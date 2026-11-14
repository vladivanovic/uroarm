from dataclasses import dataclass, field

from lerobot.cameras import CameraConfig
from lerobot.robots import RobotConfig


@RobotConfig.register_subclass("uroarm_follower")
@dataclass
class UroarmConfig(RobotConfig):
    # Serial port of the Pico ("" = take from the arm.yaml profile)
    port: str = ""

    # Which profile in arm.yaml to use: "uroarm" or "arm2"
    arm_profile: str = "uroarm"

    # Path to arm.yaml (None = the one in the uroarm repo)
    arm_config_path: str | None = None

    # Release servos (torque off) when disconnecting
    disable_torque_on_disconnect: bool = True

    # Safety cap on how far a single action may move a joint, in degrees.
    # Scalar (same for all) or per-joint dict. None = only arm.yaml limits apply.
    max_relative_target: float | dict[str, float] | None = None

    cameras: dict[str, CameraConfig] = field(default_factory=dict)
