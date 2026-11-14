"""LeRobot plugin: uroarm_follower.

Importing this package registers the `uroarm_follower` robot type with
LeRobot (its plugin loader auto-imports installed `lerobot_robot_*`
packages).
"""

from .config_uroarm import UroarmConfig
from .uroarm_robot import UroarmFollower

__all__ = ["UroarmConfig", "UroarmFollower"]
