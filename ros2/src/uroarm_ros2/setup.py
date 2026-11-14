import os
from glob import glob

from setuptools import find_packages, setup

package_name = "uroarm_ros2"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "urdf"), glob("urdf/*")),
        (os.path.join("share", package_name, "launch"), glob("launch/*")),
        (os.path.join("share", package_name, "config", "moveit"), glob("config/moveit/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Vladimir Ivanovic",
    maintainer_email="vlad@vladivanovic.com",
    description="ROS 2 driver and MoveIt 2 config for uroarm-derived arms.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "uroarm_node = uroarm_ros2.node:main",
        ],
    },
)
