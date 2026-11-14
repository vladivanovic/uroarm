"""Arm configuration: loads one profile from arm.yaml.

Replaces the old data/arm.json (servo-angle scale/offset, prev-servo)
and the link lengths that were hard-coded in kinematics.py.
Convert an existing arm.json with tools/import_arm_json.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "arm.yaml"


@dataclass
class JointConfig:
    name: str
    channel: int
    servo: str
    scale: float
    offset_deg: float
    limit_deg: tuple[float, float]
    pulse_us: tuple[int, int]

    def joint_to_servo(self, joint_deg: float) -> float:
        """joint-space degrees -> servo degrees (old angle_to_servo)."""
        return self.scale * joint_deg + self.offset_deg

    def servo_to_joint(self, servo_deg: float) -> float:
        """servo degrees -> joint-space degrees (old servo_to_angle)."""
        return (servo_deg - self.offset_deg) / self.scale

    def clip_joint(self, joint_deg: float) -> float:
        lo, hi = self.limit_deg
        return max(lo, min(hi, joint_deg))


@dataclass
class ArmConfig:
    name: str
    port: str | None
    baudrate: int
    links_mm: dict[str, float]
    joints: list[JointConfig] = field(default_factory=list)

    @property
    def joint_names(self) -> list[str]:
        return [j.name for j in self.joints]

    def joint(self, name: str) -> JointConfig:
        for j in self.joints:
            if j.name == name:
                return j
        raise KeyError(f"no joint named {name!r} in profile {self.name!r}")

    def by_channel(self) -> list[JointConfig]:
        return sorted(self.joints, key=lambda j: j.channel)


def load_profile(profile: str = "uroarm", path: str | Path | None = None) -> ArmConfig:
    try:
        import yaml
    except ImportError as e:
        raise ImportError("PyYAML is required: pip install pyyaml") from e

    cfg_path = Path(path) if path else DEFAULT_CONFIG_PATH
    with open(cfg_path) as f:
        raw = yaml.safe_load(f)

    arms = raw.get("arms", {})
    if profile not in arms:
        raise KeyError(f"profile {profile!r} not in {cfg_path} (have: {sorted(arms)})")
    p = arms[profile]

    joints = [
        JointConfig(
            name=j["name"],
            channel=int(j["channel"]),
            servo=str(j.get("servo", "")),
            scale=float(j["scale"]),
            offset_deg=float(j["offset_deg"]),
            limit_deg=(float(j["limit_deg"][0]), float(j["limit_deg"][1])),
            pulse_us=(int(j["pulse_us"][0]), int(j["pulse_us"][1])),
        )
        for j in p["joints"]
    ]
    return ArmConfig(
        name=profile,
        port=p.get("port"),
        baudrate=int(p.get("baudrate", 115200)),
        links_mm={k: float(v) for k, v in p["links_mm"].items()},
        joints=joints,
    )
