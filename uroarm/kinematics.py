"""Forward / inverse kinematics — ported from the original kinematics.py.

Differences from the original, and only these:
- Pure: no imports from servo.py / util.py (which dragged in PySimpleGUI,
  a live serial connection and the arm.json calibration).
- Works in JOINT space. The original took servo degrees and converted
  each one with servo_to_angle() first; here the caller passes joint
  degrees directly (the driver does the scale/offset conversion).
- Link lengths are parameters (from arm.yaml) instead of globals.

The math is unchanged. Pose is [x, y, z, roll, pitch] in mm / radians;
the arm is 5-DoF for pose (base, shoulder, elbow, wrist pitch, wrist
roll) plus a gripper that kinematics ignores, exactly as before.
"""

from __future__ import annotations

import math

import numpy as np

DEFAULT_LINKS_MM = {"L0": 111.0, "L1": 105.0, "L2": 98.0, "L3": 25.0, "L4": 157.0}


def radian(d):
    return d * math.pi / 180.0


def degree(t):
    return t * 180.0 / math.pi


def normalize_radian(rad):
    while np.pi < rad:
        rad -= 2 * np.pi
    while rad < -np.pi:
        rad += 2 * np.pi
    return rad


class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"(x:{self.x:.1f} y:{self.y:.1f})"

    def len(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def unit(self):
        l = self.len()
        assert l != 0
        return Vec2(self.x / l, self.y / l)

    def rot(self, t):
        cs = math.cos(t)
        sn = math.sin(t)
        return Vec2(self.x * cs - self.y * sn, self.x * sn + self.y * cs)

    def arctan2p(self):
        rad = np.arctan2(self.y, self.x)
        return rad if 0 <= rad else 2 * np.pi + rad

    def __rmul__(self, other):
        return Vec2(other * self.x, other * self.y)

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)


def forward_kinematics(joint_deg, links_mm=None):
    """joint_deg: 6 joint-space degrees (gripper ignored). Returns pose array."""
    links = links_mm or DEFAULT_LINKS_MM
    L0, L1, L2, L3, L4 = (links[k] for k in ("L0", "L1", "L2", "L3", "L4"))

    rads = [radian(d) for d in joint_deg]
    j0, j1, j2, j3, j4, j5 = rads

    p1 = Vec2(0, L0)
    p2 = p1 + (Vec2(L1, 0).rot(0.5 * np.pi + j1))
    p3 = p2 + L2 * (p2 - p1).unit().rot(j2)
    p4 = p3 + L3 * (p3 - p2).unit().rot(j3 + 0.5 * np.pi)
    tcp = p4 + L4 * (p3 - p2).unit().rot(j3)

    et = (p4 - tcp).unit()
    theta = normalize_radian(np.pi - np.arctan2(et.y, et.x))

    r = abs(tcp.x)
    x = r * math.cos(j0)
    y = r * math.sin(j0)
    z = tcp.y

    return np.array([x, y, z, j4, theta], dtype=np.float64)


def inverse_kinematics(pose, links_mm=None):
    """pose: [x, y, z, roll, pitch]. Returns 5 joint radians, or None if unreachable."""
    links = links_mm or DEFAULT_LINKS_MM
    L0, L1, L2, L3, L4 = (links[k] for k in ("L0", "L1", "L2", "L3", "L4"))

    x, y, z, phi, theta = pose

    r = Vec2(x, y).len()
    if x < 0:
        r *= -1

    p1 = Vec2(0, L0)
    tcp = Vec2(r, z)

    theta2 = np.pi - theta
    p4 = tcp + L4 * Vec2(math.cos(theta2), math.sin(theta2))

    et = (p4 - tcp).unit()
    e4 = et.rot(radian(90))
    p3 = p4 + L3 * e4

    l = (p3 - p1).len()

    cos_alpha = (L2 * L2 + l * l - L1 * L1) / (2 * L2 * l)
    if 1 < abs(cos_alpha):
        if 0.05 < abs(cos_alpha) - 1:
            return None
        cos_alpha = np.sign(cos_alpha)

    alpha = math.acos(cos_alpha)

    e31 = (p1 - p3).unit()
    e32 = e31.rot(-alpha)
    p2 = p3 + L2 * e32

    ts = [0] * 5
    ts[0] = np.arctan2(y, x)
    ts[1] = (p2 - p1).arctan2p() - 0.5 * np.pi
    ts[2] = (p3 - p2).arctan2p() - (p2 - p1).arctan2p()
    ts[3] = (tcp - p4).arctan2p() - (p3 - p2).arctan2p()
    ts[4] = phi

    return [normalize_radian(rad) for rad in ts]
