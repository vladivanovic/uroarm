# servo.py — Kevin McAleer's Servos class, adapted for firmware v2:
# - fixed: `math` was used in position() but never imported
# - added: per-channel pulse ranges (channels list of (min_us, max_us)),
#   because the two servo types on this arm have different ranges.
#   With no channels argument it behaves exactly like the original.

from pca9685 import PCA9685
import math


class Servos:
    def __init__(self, i2c, address=0x40, freq=50, min_us=600, max_us=2400,
                 degrees=180, channels=None):
        self.period = 1000000 / freq
        self.degrees = degrees
        self.freq = freq
        # channels: optional list of (min_us, max_us) per channel index
        self.ranges = channels
        self.min_duty = self._us2duty(min_us)
        self.max_duty = self._us2duty(max_us)
        self.pca9685 = PCA9685(i2c, address)
        self.pca9685.freq(freq)

    def _us2duty(self, value):
        return int(4095 * value / self.period)

    def _range_duty(self, index):
        if self.ranges is not None and index < len(self.ranges):
            lo, hi = self.ranges[index]
            return self._us2duty(lo), self._us2duty(hi)
        return self.min_duty, self.max_duty

    def position(self, index, degrees=None, radians=None, us=None, duty=None):
        min_duty, max_duty = self._range_duty(index)
        span = max_duty - min_duty
        if degrees is not None:
            duty = min_duty + span * degrees / self.degrees
        elif radians is not None:
            duty = min_duty + span * radians / math.radians(self.degrees)
        elif us is not None:
            duty = self._us2duty(us)
        elif duty is not None:
            pass
        else:
            return self.pca9685.duty(index)
        duty = min(max_duty, max(min_duty, int(duty)))
        self.pca9685.duty(index, duty)

    def release(self, index):
        self.pca9685.duty(index, 0)
