# Legacy stack (pre-2026 rewrite)

The original uroarm host stack, kept for reference: PySimpleGUI apps
(`arm.py`, `servo.py`, `angle.py`), the REPL-over-serial `talker.py`
protocol, ChArUco marker + OpenVINO vision (`camera.py`, `marker.py`,
`board.py`, `infer.py`, `data/`), the S-curve experiment, Vlad's serial
test scripts (`test_scripts/`), and the Arduino firmware variant
(`Arduino_Arm/`, which speaks the old `moveServo(ch,deg)` string
protocol and is NOT compatible with the new driver).

Nothing here is used by the current driver, ROS 2 node or LeRobot
plugin. It is preserved because the vision pick-and-place calibration
workflow may still be useful, and because git history alone is a pain
to browse. Its dependencies are in `requirements-legacy.txt`.
