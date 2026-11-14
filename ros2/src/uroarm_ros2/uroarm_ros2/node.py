"""uroarm ROS 2 driver node.

Publishes /joint_states from the driver and serves a FollowJointTrajectory
action server. This is deliberately NOT a ros2_control C++ hardware
plugin: for write-only hobby servos a Python bridge node provides the
same standard interfaces (this is the pattern the OmArm Zero project
used for near-identical hardware).

IMPORTANT: /joint_states and trajectory feedback report COMMANDED
positions (echo). The servos have no position feedback, so ROS cannot
detect sag, slip or a blocked joint. Trajectory "success" means
"commanded", not "reached".

Requires the repo's `uroarm` Python package importable (pip install -e
the repo root, or set PYTHONPATH) and pyserial.

Parameters:
    arm_profile (string, default "uroarm")  profile name in arm.yaml
    config_path (string, default "")        path to arm.yaml ("" = repo default)
    port        (string, default "")        serial port override
    state_rate_hz (double, default 20.0)    /joint_states publish rate
"""

from __future__ import annotations

import math
import time

import rclpy
from control_msgs.action import FollowJointTrajectory
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory

from uroarm import load_profile
from uroarm.driver import UroarmDriver


class UroarmNode(Node):
    def __init__(self):
        super().__init__("uroarm_driver_node")
        self.declare_parameter("arm_profile", "uroarm")
        self.declare_parameter("config_path", "")
        self.declare_parameter("port", "")
        self.declare_parameter("state_rate_hz", 20.0)

        profile = self.get_parameter("arm_profile").value
        config_path = self.get_parameter("config_path").value or None
        port = self.get_parameter("port").value or None

        self.config = load_profile(profile, config_path)
        self.driver = UroarmDriver(self.config)
        self.driver.connect(port)
        if not self.driver.ping():
            self.get_logger().warning(
                "no ping reply from firmware — check port/baud and that firmware v2 is flashed"
            )
        self.joint_names = self.config.joint_names
        self.get_logger().info(
            f"uroarm profile {profile!r} connected on {port or self.config.port}; "
            "joint state is COMMANDED echo (no position feedback)"
        )

        self._pub = self.create_publisher(JointState, "joint_states", 10)
        rate = float(self.get_parameter("state_rate_hz").value)
        self._timer = self.create_timer(1.0 / rate, self._publish_state)

        self._action = ActionServer(
            self,
            FollowJointTrajectory,
            "uroarm_controller/follow_joint_trajectory",
            execute_callback=self._execute,
            goal_callback=lambda goal: GoalResponse.ACCEPT,
            cancel_callback=lambda goal: CancelResponse.ACCEPT,
        )

    def _publish_state(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = self.driver.get_joints_rad()
        self._pub.publish(msg)

    def _execute(self, goal_handle):
        traj: JointTrajectory = goal_handle.request.trajectory
        result = FollowJointTrajectory.Result()

        # Map trajectory joint order onto driver joint order.
        try:
            order = [self.joint_names.index(n) for n in traj.joint_names]
        except ValueError as e:
            result.error_code = FollowJointTrajectory.Result.INVALID_JOINTS
            result.error_string = str(e)
            goal_handle.abort()
            return result

        start = time.monotonic()
        current = self.driver.get_joints_rad()
        for point in traj.points:
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                result.error_code = FollowJointTrajectory.Result.SUCCESSFUL
                return result
            target_rad = list(current)
            for src_idx, dst_idx in enumerate(order):
                target_rad[dst_idx] = point.positions[src_idx]
            t_goal = start + point.time_from_start.sec + point.time_from_start.nanosec * 1e-9
            remaining = t_goal - time.monotonic()
            target_deg = [math.degrees(r) for r in target_rad]
            # Firmware ramps over the remaining segment time.
            self.driver.set_joints(target_deg, duration_s=max(remaining, 0.0))
            if remaining > 0:
                time.sleep(remaining)
            current = target_rad

            feedback = FollowJointTrajectory.Feedback()
            feedback.joint_names = self.joint_names
            feedback.desired.positions = list(point.positions)
            feedback.actual.positions = self.driver.get_joints_rad()
            goal_handle.publish_feedback(feedback)

        goal_handle.succeed()
        result.error_code = FollowJointTrajectory.Result.SUCCESSFUL
        return result

    def destroy_node(self):
        try:
            self.driver.disconnect()
        finally:
            super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = UroarmNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
