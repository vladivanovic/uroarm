"""Tests for the uroarm core package. Run: python3 -m unittest discover tests -v

No hardware, no pyserial, no pytest needed.
"""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from uroarm import kinematics, load_profile
from uroarm.driver import UroarmDriver


class FakeTransport:
    def __init__(self):
        self.lines = []
        self.closed = False

    def write_line(self, line):
        self.lines.append(line)

    def read_line(self):
        return "OK uroarm-fw2"

    def close(self):
        self.closed = True


class ConfigTest(unittest.TestCase):
    def test_profiles_load(self):
        for name in ("uroarm", "arm2"):
            cfg = load_profile(name)
            self.assertEqual(len(cfg.joints), 6)
            self.assertEqual(
                cfg.joint_names,
                ["shoulder_pan", "shoulder_lift", "elbow_flex",
                 "wrist_flex", "wrist_roll", "gripper"],
            )
            self.assertEqual(cfg.links_mm["L4"], 157.0)

    def test_conversion_roundtrip(self):
        cfg = load_profile("uroarm")
        j = cfg.joint("elbow_flex")
        self.assertAlmostEqual(j.servo_to_joint(j.joint_to_servo(33.0)), 33.0)


class KinematicsTest(unittest.TestCase):
    def test_fk_zero_pose(self):
        # Hand-computed from the geometry: at joint zero the planar chain
        # points straight up; TCP = (25, 0, 471), pitch = -90 deg.
        pose = kinematics.forward_kinematics([0, 0, 0, 0, 0, 0])
        self.assertAlmostEqual(pose[0], 25.0, places=5)
        self.assertAlmostEqual(pose[1], 0.0, places=5)
        self.assertAlmostEqual(pose[2], 471.0, places=5)
        self.assertAlmostEqual(pose[4], -math.pi / 2, places=5)

    def test_fk_ik_roundtrip(self):
        for joints in ([10, -20, 30, -15, 5, 0], [0, 0, -90, -90, 0, 0], [-30, 10, -40, 20, 45, 0]):
            pose = kinematics.forward_kinematics(list(joints))
            rad5 = kinematics.inverse_kinematics(pose)
            self.assertIsNotNone(rad5, f"IK failed for {joints}")
            back = kinematics.forward_kinematics(
                [kinematics.degree(r) for r in rad5] + [0]
            )
            for a, b in zip(pose[:3], back[:3]):
                self.assertAlmostEqual(a, b, places=3, msg=f"roundtrip {joints}")

    def test_ik_unreachable(self):
        self.assertIsNone(kinematics.inverse_kinematics([2000, 0, 2000, 0, 0]))


class DriverTest(unittest.TestCase):
    def setUp(self):
        self.transport = FakeTransport()
        self.driver = UroarmDriver(load_profile("uroarm"), transport=self.transport)

    def test_set_joints_packet(self):
        applied = self.driver.set_joints([0, 0, 0, 0, 0, 50])
        # default calibration [1, 90]: servo = joint + 90
        self.assertEqual(self.transport.lines[-1], "S 90.0,90.0,90.0,90.0,90.0,140.0")
        self.assertEqual(applied, [0, 0, 0, 0, 0, 50])

    def test_duration_uses_ramp_packet(self):
        self.driver.set_joints([0] * 6, duration_s=2.0)
        self.assertTrue(self.transport.lines[-1].startswith("M 2000 "))

    def test_limits_clip_and_report(self):
        applied = self.driver.set_joints([200, 0, 0, 0, 0, -5])
        self.assertEqual(applied[0], 90)    # shoulder_pan limit
        self.assertEqual(applied[5], 0)     # gripper limit
        self.assertEqual(self.driver.get_joints(), applied)

    def test_precoded_moves(self):
        self.driver.move_to_ready()
        self.assertEqual(self.driver.get_joints()[:5], [0, 0, -90, -90, 0])
        self.driver.open_hand()
        self.assertEqual(self.driver.get_joints()[5], 100)
        self.driver.close_hand()
        self.assertEqual(self.driver.get_joints()[5], 30)

    def test_move_pose_unreachable_returns_none(self):
        self.assertIsNone(self.driver.move_pose([2000, 0, 2000, 0, 0]))

    def test_ping(self):
        self.assertTrue(self.driver.ping())
        self.assertEqual(self.transport.lines[-1], "P")


if __name__ == "__main__":
    unittest.main()
