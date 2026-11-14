"""Display the uroarm URDF in RViz with joint sliders — NO hardware needed.

This is the bring-up path while the PCA9685 is borrowed by another
project: the model, TF tree and joint names can all be verified first.

    ros2 launch uroarm_ros2 display.launch.py
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory("uroarm_ros2")
    urdf_path = os.path.join(pkg, "urdf", "uroarm.urdf")
    with open(urdf_path) as f:
        robot_description = f.read()

    return LaunchDescription([
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[{"robot_description": robot_description}],
        ),
        Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
        ),
        Node(package="rviz2", executable="rviz2", name="rviz2"),
    ])
