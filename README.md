# uroarm — LeRobot + ROS 2 robot arm controller

Vlad's fork of [teatime77/uroarm](https://github.com/teatime77/uroarm)
(original tutorial, Japanese: https://uroa.jp/arm/), rebuilt around a
shared driver core with **LeRobot** and **ROS 2** adapters.

Two physical arms use this codebase — the original uroarm and a second
custom build from the same design with different motors. They differ
only in their profile in [`arm.yaml`](arm.yaml).

## Why the rewrite

The original design is classic old-school robotics: hand-derived IK, a
GUI, marker-based vision, and precoded motion sequences, glued together
by sending Python source code into the Pico's REPL with a 1-second
sleep per joint (~6 s per pose). That can't serve a LeRobot control
loop or a ROS 2 trajectory controller, both of which stream joint
targets at 10–50 Hz.

What survived, because it was the good stuff: the analytic FK/IK
(link lengths 111/105/98/25/157 mm), the per-joint scale/offset
calibration, and the precoded movements (ready pose, hand open/close,
the `grab()` pick-and-place sequence) — all ported into the driver core.

## Layout

| Path | What |
|---|---|
| `arm.yaml` | **Single source of truth**: per-arm profiles — joint names (SO-101 convention), channels, servo models, scale/offset calibration, joint limits, pulse ranges, link lengths |
| `uroarm/` | Driver core: `config.py` (profile loader), `kinematics.py` (pure FK/IK, no GUI/serial deps), `driver.py` (framed serial protocol + precoded moves) |
| `pico/` | Firmware v2 (MicroPython): persistent PCA9685 driver, one packet moves all 6 servos, on-Pico ramping with smoothstep easing, watchdog servo release |
| `ros2/src/uroarm_ros2/` | ROS 2 package: URDF, driver node (`/joint_states` + `FollowJointTrajectory` action server), launch files, MoveIt 2 config |
| `lerobot_robot_uroarm/` | LeRobot plugin: registers robot type `uroarm_follower` (v0.6.x API) |
| `tools/import_arm_json.py` | Converts an old `data/arm.json` calibration into an `arm.yaml` profile |
| `tests/` | Unit tests (stdlib only): `python3 -m unittest discover tests -v` |
| `legacy/` | The old GUI/vision/REPL stack, Arduino variant and test scripts — reference only |

## Protocol (firmware v2)

Newline-terminated ASCII at 115200 baud, values in servo degrees:

```
S <s0>,...,<s5>     set all servos now
M <ms> <s0>,...,<s5>  ramp to target over <ms> (on the Pico)
R                   release all servos
P                   ping -> "OK uroarm-fw2"
Q                   query commanded state
```

## Quick start

```bash
pip install -r requirements.txt        # pyyaml, pyserial, numpy
python3 -m unittest discover tests -v  # no hardware needed

# Flash the Pico: copy pico/pca9685.py, pico/servo.py, pico/main.py onto it
# Set your port in arm.yaml (or pass it), then:
python3 -c "
from uroarm import load_profile
from uroarm.driver import UroarmDriver
d = UroarmDriver(load_profile('uroarm')); d.connect('/dev/ttyACM0')
d.move_to_ready(); d.open_hand(); d.close_hand()
"
```

ROS 2 (Jazzy, on the Orin/Pi):

```bash
ros2 launch uroarm_ros2 display.launch.py   # URDF + RViz, no hardware needed
ros2 launch uroarm_ros2 driver.launch.py port:=/dev/ttyACM0
```

LeRobot:

```bash
pip install -e lerobot_robot_uroarm
lerobot-teleoperate --robot.type=uroarm_follower --robot.port=/dev/ttyACM0 \
    --robot.id=uroarm1 --teleop.type=keyboard
```

## The one big limitation

**There is no position feedback.** Hobby servos on a PCA9685 are
write-only, so every "current position" in this stack — LeRobot
observations, ROS 2 `/joint_states`, trajectory feedback — is the last
*commanded* position (echo). Policies and planners cannot see sag,
slip or a stalled joint. The planned fix is per-joint AS5600 magnetic
encoders on a TCA9548A mux, read by the same Pico; with encoders on
*one* arm it also becomes a 1:1 leader for the other (identical
geometry = no retargeting), which is the proper way to record LeRobot
demonstrations for these arms.

## Bring-up checklist (not yet done on hardware)

- [ ] Flash firmware v2, verify `P` → `OK uroarm-fw2`
- [ ] Import your real calibration: `tools/import_arm_json.py <old arm.json>`
- [ ] Verify URDF joint axis signs against the physical arm before
      trusting MoveIt Cartesian moves (URDF zeros are from FK geometry)
- [ ] Build the ROS 2 package (`colcon build`) on the Orin and run the
      display launch, then the driver launch
- [ ] First LeRobot record run with the keyboard teleoperator
