"""Launch the uroarm driver node + robot_state_publisher.

Usage:
    ros2 launch uroarm_ros2 driver.launch.py port:=/dev/ttyACM0
    ros2 launch uroarm_ros2 driver.launch.py arm_profile:=arm2 port:=/dev/ttyACM1
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory("uroarm_ros2")
    urdf_path = os.path.join(pkg, "urdf", "uroarm.urdf")
    with open(urdf_path) as f:
        robot_description = f.read()

    return LaunchDescription([
        DeclareLaunchArgument("arm_profile", default_value="uroarm"),
        DeclareLaunchArgument("port", default_value=""),
        DeclareLaunchArgument("config_path", default_value=""),
        Node(
            package="uroarm_ros2",
            executable="uroarm_node",
            name="uroarm_driver_node",
            output="screen",
            parameters=[{
                "arm_profile": LaunchConfiguration("arm_profile"),
                "port": LaunchConfiguration("port"),
                "config_path": LaunchConfiguration("config_path"),
            }],
        ),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            parameters=[{"robot_description": robot_description}],
        ),
    ])
