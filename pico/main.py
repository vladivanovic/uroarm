#
# uroarm firmware v2 — MicroPython, Raspberry Pi Pico / Pico 2
#
# Replaces the v1 approach (host sent Python source into the REPL and
# move_servo() built a brand-new Servos object — re-initialising the
# PCA9685 — on every single joint move).
#
# v2: one persistent Servos object, and a framed line protocol on USB
# serial at 115200 baud. All values are SERVO degrees (0-180); the host
# driver (uroarm/driver.py) does joint<->servo conversion and limits.
#
#   S <s0>,<s1>,<s2>,<s3>,<s4>,<s5>   set all servos now
#   M <ms> <s0>,...,<s5>              ramp all servos to target over <ms>
#   R                                 release all servos (torque off)
#   P                                 ping  -> "OK uroarm-fw2"
#   Q                                 query -> "STATE <s0>,...,<s5>"
#
# Safety:
# - targets are clamped to 0-180 here as well as on the host
# - if no valid packet arrives for WATCHDOG_MS, all servos are released
#   (a crashed host or pulled cable leaves a limp arm, not a straining one)
#
# Copy pca9685.py, servo.py and this file to the Pico.
#

import sys
import select
import time
from machine import I2C, Pin

from servo import Servos

NCH = 6
WATCHDOG_MS = 10_000
LOOP_MS = 20  # 50 Hz ramp update

# Per-channel operating pulse ranges — MUST match arm.yaml pulse_us.
# Kept at the old uniform 600-2400us so existing calibration stays valid.
PULSE_US = [(600, 2400)] * NCH

i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)
servos = Servos(i2c, freq=50, channels=PULSE_US)

led = Pin("LED", Pin.OUT)


def _clamp(v):
    return max(0.0, min(180.0, v))


class Arm:
    def __init__(self):
        self.current = None      # list of 6 servo degrees, or None if released/unknown
        self.start = None
        self.target = None
        self.ramp_start = 0
        self.ramp_ms = 0
        self.last_rx = time.ticks_ms()
        self.released = True

    def set(self, targets, ramp_ms=0):
        targets = [_clamp(t) for t in targets]
        self.last_rx = time.ticks_ms()
        if ramp_ms and ramp_ms > 0 and self.current is not None:
            self.start = list(self.current)
            self.target = targets
            self.ramp_start = time.ticks_ms()
            self.ramp_ms = ramp_ms
        else:
            self.start = self.target = None
            self._apply(targets)

    def _apply(self, values):
        for ch, deg in enumerate(values):
            servos.position(ch, deg)
        self.current = list(values)
        self.released = False

    def release(self):
        for ch in range(NCH):
            servos.release(ch)
        self.current = None
        self.start = self.target = None
        self.released = True

    def update(self):
        now = time.ticks_ms()
        if self.target is not None:
            t = time.ticks_diff(now, self.ramp_start) / self.ramp_ms
            if t >= 1:
                self._apply(self.target)
                self.start = self.target = None
            else:
                # smoothstep easing — gentler ends than a linear ramp
                e = t * t * (3 - 2 * t)
                self._apply([s + e * (g - s) for s, g in zip(self.start, self.target)])
        elif not self.released and time.ticks_diff(now, self.last_rx) > WATCHDOG_MS:
            self.release()
            print("WATCHDOG release")


arm = Arm()


def _parse_targets(text):
    vals = [float(v) for v in text.split(",")]
    if len(vals) != NCH:
        raise ValueError("need %d values" % NCH)
    return vals


def handle(line):
    line = line.strip()
    if not line:
        return
    try:
        if line == "P":
            arm.last_rx = time.ticks_ms()
            print("OK uroarm-fw2")
        elif line == "R":
            arm.release()
            print("OK R")
        elif line == "Q":
            arm.last_rx = time.ticks_ms()
            if arm.current is None:
                print("STATE released")
            else:
                print("STATE " + ",".join("%.1f" % v for v in arm.current))
        elif line.startswith("S "):
            arm.set(_parse_targets(line[2:]))
            print("OK S")
        elif line.startswith("M "):
            ms_text, targets_text = line[2:].split(" ", 1)
            arm.set(_parse_targets(targets_text), ramp_ms=int(ms_text))
            print("OK M")
        else:
            print("ERR unknown command")
    except Exception as e:
        print("ERR", e)


# Backwards-compatible REPL helper, like v1: move_servo(ch, deg)
def move_servo(s, v):
    targets = list(arm.current) if arm.current is not None else [90.0] * NCH
    targets[int(s)] = _clamp(float(v))
    arm.set(targets)


def on():
    led.value(1)


def off():
    led.value(0)


def main():
    poller = select.poll()
    poller.register(sys.stdin, select.POLLIN)
    buf = ""
    print("OK uroarm-fw2 boot")
    while True:
        arm.update()
        events = poller.poll(LOOP_MS)
        if events:
            chunk = sys.stdin.read(1)
            if chunk:
                buf += chunk
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    handle(line)


main()
