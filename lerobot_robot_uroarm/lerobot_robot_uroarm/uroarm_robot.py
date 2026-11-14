"""LeRobot Robot implementation for uroarm-derived arms.

Written against the LeRobot v0.6.x Robot API (verified against v0.6.2,
the version in Vlad's LeRobot-Splunk fork) and mirroring the SO follower
implementation's structure.

The arm is driven through the shared `uroarm` driver package — the same
core the ROS 2 node uses. Calibration comes from arm.yaml: the
scale/offset pair per joint IS this arm's motor calibration (it was
data/arm.json's "servo-angle" in the old stack), so calibrate() simply
exports it into LeRobot's calibration format. There is no interactive
calibration procedure: with no position feedback there is nothing to
measure, which is also why get_observation() returns COMMANDED state.
"""

import logging
import time
from functools import cached_property

from lerobot.cameras import make_cameras_from_configs
from lerobot.lerobot_types import RobotAction, RobotObservation
from lerobot.motors import MotorCalibration
from lerobot.robots import Robot
from lerobot.utils.decorators import check_if_already_connected, check_if_not_connected

from uroarm import load_profile
from uroarm.driver import UroarmDriver

from .config_uroarm import UroarmConfig

logger = logging.getLogger(__name__)


class UroarmFollower(Robot):
    config_class = UroarmConfig
    name = "uroarm_follower"

    def __init__(self, config: UroarmConfig):
        super().__init__(config)
        self.config = config
        self.arm_config = load_profile(config.arm_profile, config.arm_config_path)
        self.driver = UroarmDriver(self.arm_config)
        self.cameras = make_cameras_from_configs(config.cameras)

    @property
    def _motors_ft(self) -> dict[str, type]:
        return {f"{name}.pos": float for name in self.arm_config.joint_names}

    @property
    def _cameras_ft(self) -> dict[str, tuple]:
        return {
            cam: (self.config.cameras[cam].height, self.config.cameras[cam].width, 3)
            for cam in self.cameras
        }

    @cached_property
    def observation_features(self) -> dict:
        return {**self._motors_ft, **self._cameras_ft}

    @cached_property
    def action_features(self) -> dict:
        return self._motors_ft

    @property
    def is_connected(self) -> bool:
        return self.driver.is_connected and all(
            cam.is_connected for cam in self.cameras.values()
        )

    @check_if_already_connected
    def connect(self, calibrate: bool = True) -> None:
        self.driver.connect(self.config.port or None)
        if not self.is_calibrated and calibrate:
            self.calibrate()
        for cam in self.cameras.values():
            cam.connect()
        self.configure()
        logger.info(f"{self} connected.")

    @property
    def is_calibrated(self) -> bool:
        # Calibration lives in arm.yaml and is loaded with the profile;
        # it is always present. A LeRobot calibration file, if one was
        # saved by calibrate(), is a copy of the same numbers.
        return True

    def calibrate(self) -> None:
        """Export the arm.yaml calibration into LeRobot's format.

        range_min/max are the joint limits in degrees; homing_offset is
        the joint's offset_deg (servo degrees at joint zero). These are
        informational in LeRobot's schema — the driver keeps using
        arm.yaml as the source of truth.
        """
        self.calibration = {
            j.name: MotorCalibration(
                id=j.channel,
                drive_mode=0,
                homing_offset=int(round(j.offset_deg)),
                range_min=int(round(j.limit_deg[0])),
                range_max=int(round(j.limit_deg[1])),
            )
            for j in self.arm_config.joints
        }
        self._save_calibration()
        logger.info(f"Calibration (from arm.yaml) saved to {self.calibration_fpath}")

    def configure(self) -> None:
        # Nothing to write to the motors: PCA9685 servos have no
        # registers, gains or operating modes. Kept for API parity.
        pass

    @check_if_not_connected
    def get_observation(self) -> RobotObservation:
        start = time.perf_counter()
        # COMMANDED positions (echo) — the hardware cannot report actuals.
        obs = {
            f"{name}.pos": float(val)
            for name, val in zip(self.arm_config.joint_names, self.driver.get_joints())
        }
        logger.debug(f"{self} read state: {(time.perf_counter() - start) * 1e3:.1f}ms")

        for cam_key, cam in self.cameras.items():
            if getattr(cam, "use_rgb", True):
                obs[cam_key] = cam.read_latest()
            if getattr(cam, "use_depth", False):
                obs[f"{cam_key}_depth"] = cam.read_latest_depth()
        return obs

    @check_if_not_connected
    def send_action(self, action: RobotAction) -> RobotAction:
        goal = {
            key.removesuffix(".pos"): float(val)
            for key, val in action.items()
            if key.endswith(".pos")
        }

        # Optional safety cap relative to current (commanded) position.
        if self.config.max_relative_target is not None:
            present = dict(zip(self.arm_config.joint_names, self.driver.get_joints()))
            for name, g in goal.items():
                cap = (
                    self.config.max_relative_target[name]
                    if isinstance(self.config.max_relative_target, dict)
                    else self.config.max_relative_target
                )
                if cap is not None:
                    goal[name] = max(present[name] - cap, min(present[name] + cap, g))

        target = list(self.driver.get_joints())
        for name, g in goal.items():
            target[self.arm_config.joint_names.index(name)] = g
        applied = self.driver.set_joints(target)

        return {
            f"{name}.pos": float(val)
            for name, val in zip(self.arm_config.joint_names, applied)
            if name in goal
        }

    @check_if_not_connected
    def disconnect(self) -> None:
        if self.config.disable_torque_on_disconnect:
            self.driver.release()
        self.driver.disconnect()
        for cam in self.cameras.values():
            cam.disconnect()
        logger.info(f"{self} disconnected.")
