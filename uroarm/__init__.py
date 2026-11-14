"""uroarm — shared driver core for Vlad's uroarm-derived arms.

One core, two adapters:
- ROS 2 node:      ros2/src/uroarm_ros2/
- LeRobot plugin:  lerobot_robot_uroarm/

The hardware has NO position feedback (hobby servos on a PCA9685 are
write-only), so every "current position" in this package is the last
COMMANDED position (echo state). That is documented wherever it matters.
"""

from .config import ArmConfig, JointConfig, load_profile
from .driver import UroarmDriver

__all__ = ["ArmConfig", "JointConfig", "load_profile", "UroarmDriver"]
