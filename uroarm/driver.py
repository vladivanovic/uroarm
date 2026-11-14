"""uroarm driver core — the one place that talks to the arm.

Protocol (firmware v2, pico/main.py), newline-terminated ASCII at the
profile baudrate (default 115200):

    S <s0>,<s1>,<s2>,<s3>,<s4>,<s5>     set all servos now (servo degrees)
    M <ms> <s0>,...,<s5>                ramp to target over <ms> on the Pico
    R                                   release all servos (torque off)
    P                                   ping -> "OK uroarm-fw2"
    Q                                   query -> "STATE <s0>,...,<s5>"

This replaces the old talker.py approach of sending Python source into
the Pico REPL with a 1-second sleep per joint (~6 s per pose). One
packet now moves all six servos, and the Pico does the ramping.

Position feedback: there is none. Hobby servos on a PCA9685 are
write-only, so get_joints() returns the last COMMANDED joint state
(echo). Callers (LeRobot get_observation, ROS 2 /joint_states) inherit
that limitation — see the plan doc.
"""

from __future__ import annotations

import math
import time

from . import kinematics
from .config import ArmConfig

GRIPPER_OPEN_DEG = 100.0    # from arm.py open_hand()
GRIPPER_CLOSED_DEG = 30.0   # from arm.py close_hand()
READY_JOINT_DEG = [0.0, 0.0, -90.0, -90.0, 0.0]  # arm.py move_to_ready(), arm joints only
PICK_Z, PLACE_Z, LIFT_Z = 15.0, 25.0, 50.0       # arm.py constants


class SerialTransport:
    """pyserial transport. Imported lazily so the driver (and its tests)
    work on machines without pyserial or hardware attached."""

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        import serial  # pyserial

        self._ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)  # Pico enumerates / resets on connect, as before
        self._ser.reset_input_buffer()

    def write_line(self, line: str) -> None:
        self._ser.write((line + "\n").encode("utf-8"))

    def read_line(self) -> str | None:
        raw = self._ser.readline()
        if not raw:
            return None
        return raw.decode("utf-8", errors="replace").strip()

    def close(self) -> None:
        self._ser.close()


class UroarmDriver:
    def __init__(self, config: ArmConfig, transport=None):
        self.config = config
        self.transport = transport
        # Echo state, in JOINT degrees. Starts at joint zero (the old
        # prev-servo default of 90 servo degrees everywhere).
        self._commanded_joint_deg: list[float] = [0.0] * len(config.joints)

    # -- connection -----------------------------------------------------

    @property
    def is_connected(self) -> bool:
        return self.transport is not None

    def connect(self, port: str | None = None) -> None:
        port = port or self.config.port
        if not port:
            raise ValueError(
                f"no serial port: set port in arm.yaml profile {self.config.name!r} or pass one"
            )
        self.transport = SerialTransport(port, self.config.baudrate)

    def disconnect(self) -> None:
        if self.transport is not None:
            self.transport.close()
            self.transport = None

    def ping(self) -> bool:
        self._send("P")
        reply = self.transport.read_line() if self.transport else None
        return bool(reply and reply.startswith("OK"))

    # -- conversions ------------------------------------------------------

    def joint_to_servo_all(self, joint_deg) -> list[float]:
        out = []
        for jcfg, deg in zip(self.config.by_channel(), joint_deg):
            servo = jcfg.joint_to_servo(jcfg.clip_joint(deg))
            out.append(max(0.0, min(180.0, servo)))
        return out

    def servo_to_joint_all(self, servo_deg) -> list[float]:
        return [
            jcfg.servo_to_joint(s)
            for jcfg, s in zip(self.config.by_channel(), servo_deg)
        ]

    # -- motion -----------------------------------------------------------

    def _send(self, line: str) -> None:
        if self.transport is None:
            raise RuntimeError("driver is not connected")
        self.transport.write_line(line)

    def set_joints(self, joint_deg, duration_s: float = 0.0) -> list[float]:
        """Command all joints (joint-space degrees).

        Returns the joint values actually applied, after limit clipping —
        the LeRobot send_action contract expects exactly this.
        """
        if len(joint_deg) != len(self.config.joints):
            raise ValueError(f"expected {len(self.config.joints)} joint values, got {len(joint_deg)}")
        applied = [
            jcfg.clip_joint(float(d))
            for jcfg, d in zip(self.config.by_channel(), joint_deg)
        ]
        servo = self.joint_to_servo_all(applied)
        payload = ",".join(f"{s:.1f}" for s in servo)
        if duration_s and duration_s > 0:
            self._send(f"M {int(duration_s * 1000)} {payload}")
        else:
            self._send(f"S {payload}")
        self._commanded_joint_deg = applied
        return list(applied)

    def set_joint(self, name_or_channel, joint_deg: float, duration_s: float = 0.0) -> list[float]:
        target = list(self._commanded_joint_deg)
        if isinstance(name_or_channel, str):
            idx = self.config.joint_names.index(name_or_channel)
            # joint_names is in config order; channels are sorted the same
            # way in arm.yaml, but resolve via channel to be safe:
            ch = self.config.joint(name_or_channel).channel
            idx = [j.channel for j in self.config.by_channel()].index(ch)
        else:
            idx = int(name_or_channel)
        target[idx] = joint_deg
        return self.set_joints(target, duration_s=duration_s)

    def get_joints(self) -> list[float]:
        """Last COMMANDED joint degrees (echo — there is no feedback)."""
        return list(self._commanded_joint_deg)

    def get_joints_rad(self) -> list[float]:
        return [math.radians(d) for d in self._commanded_joint_deg]

    def release(self) -> None:
        self._send("R")

    def pose(self):
        """Current (commanded) TCP pose via forward kinematics."""
        return kinematics.forward_kinematics(self._commanded_joint_deg, self.config.links_mm)

    # -- precoded movements, ported from arm.py ---------------------------

    def move_to_ready(self, duration_s: float = 2.0) -> list[float]:
        target = list(self._commanded_joint_deg)
        target[:5] = READY_JOINT_DEG
        return self.set_joints(target, duration_s=duration_s)

    def open_hand(self, duration_s: float = 1.0) -> list[float]:
        return self.set_joint("gripper", GRIPPER_OPEN_DEG, duration_s=duration_s)

    def close_hand(self, duration_s: float = 1.0) -> list[float]:
        return self.set_joint("gripper", GRIPPER_CLOSED_DEG, duration_s=duration_s)

    def move_pose(self, pose, duration_s: float = 2.0) -> list[float] | None:
        """Move TCP to [x, y, z, roll, pitch] via IK. None if unreachable."""
        rad5 = kinematics.inverse_kinematics(pose, self.config.links_mm)
        if rad5 is None:
            return None
        target = list(self._commanded_joint_deg)
        target[:5] = [kinematics.degree(r) for r in rad5]
        return self.set_joints(target, duration_s=duration_s)

    def pose_from_xyz(self, x: float, y: float, z: float):
        """arm.py get_pose_from_xyz, unchanged heuristic."""
        x_min, x_max = 100.0, 300.0
        pitch_min, pitch_max = 90.0, 60.0
        if not (x_min <= x <= x_max):
            raise ValueError(f"x out of range: {x_min}..{x_max}, got {x}")
        r = (x - x_min) / (x_max - x_min)
        pitch = r * pitch_max + (1 - r) * pitch_min
        yaw = -math.atan2(y, x)
        return [x, y, z, yaw, kinematics.radian(pitch)]

    def move_xyz(self, x: float, y: float, z: float, duration_s: float = 2.0):
        return self.move_pose(self.pose_from_xyz(x, y, z), duration_s=duration_s)

    def grab(self, arm_x: float, arm_y: float, arm_z: float, sleep_s: float = 1.0):
        """The arm.py grab() pick-and-place sequence, minus the vision:
        the caller supplies the work position (was: camera + hand-eye
        calibration). Sleeps are real here — the old generator/yield
        dance existed only to keep the GUI event loop alive.
        """
        self.move_to_ready(duration_s=1.0)
        self.open_hand(duration_s=1.0)
        self.move_xyz(arm_x, arm_y, LIFT_Z, duration_s=1.0)
        z = arm_z - (PLACE_Z - PICK_Z)
        self.move_xyz(arm_x, arm_y, z, duration_s=1.0)
        time.sleep(sleep_s)
        self.close_hand(duration_s=1.0)
        time.sleep(sleep_s)
        self.move_xyz(arm_x, arm_y, LIFT_Z, duration_s=1.0)
        # place poses from arm.py (pose1/pose2)
        self.move_pose([90, -90, LIFT_Z, math.pi / 4, math.pi / 2], duration_s=1.0)
        self.move_pose([90, -90, PLACE_Z, math.pi / 4, math.pi / 2], duration_s=1.0)
        self.open_hand(duration_s=1.0)
        self.move_pose([90, -90, LIFT_Z, math.pi / 4, math.pi / 2], duration_s=1.0)
        self.move_to_ready(duration_s=1.0)
