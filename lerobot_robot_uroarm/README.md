# lerobot-robot-uroarm

LeRobot plugin for the uroarm-derived arms. LeRobot auto-discovers
installed packages named `lerobot_robot_*`, so after installing this
package the robot type `uroarm_follower` works with the stock CLIs:

```bash
pip install -e .            # from this directory; also install the repo's uroarm driver package
lerobot-teleoperate --robot.type=uroarm_follower --robot.port=/dev/ttyACM0 --robot.id=uroarm1 \
    --teleop.type=keyboard
lerobot-record --robot.type=uroarm_follower --robot.port=/dev/ttyACM0 --robot.id=uroarm1 ...
```

**Positions are in joint DEGREES** (like SO followers with
`use_degrees=True`), keyed `<joint>.pos` using the SO-101 joint names
from `arm.yaml`.

**Honest limitation:** observations are the last COMMANDED positions.
The PCA9685 + hobby servos have no position feedback, so datasets
record commanded state; a policy cannot see sag, slip or a stalled
joint. See the repo plan doc (Step 5, AS5600 encoders) for the fix.
