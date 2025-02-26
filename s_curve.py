"""S-curve acceleration/deceleration
"""

import math
import numpy as np
import matplotlib.pyplot as plt
import itertools
from util import get_move_time

pi = math.pi

class SCurve:
    def __init__(self, S_all):
        move_time = get_move_time()

        t1 = move_time / 2.0
        self.t1 = t1
        self.S1 = S_all / 2.0
        self.vmax = S_all / t1
        w = 2 * pi / t1
        self.w = w
        self.A = self.vmax * w * w / (2 * pi)
        s1 = (2 * self.A * pi * pi) / (w * w * w)
        diff = abs(self.S1 - s1)
        if 0.00000000000001 < diff:
            print('s-curve diff:%.15f' % diff)

    def jerk(self, t):
        if t < self.t1:
            c = self.A
        else:
            t -= self.t1
            c = -self.A

        return c* math.sin(self.w * t)

    def acc(self, t):
        if t < self.t1:
            c = self.A
        else:
            t -= self.t1
            c = -self.A

        c_w = c / self.w

        return c_w * (1 - math.cos(self.w * t))

    def vel(self, t):
        global v0

        if t < self.t1:
            c = self.A
            v0 = 0
        else:
            t -= self.t1
            c = -self.A
            v0 = self.vmax

        c_w = c / self.w

        return v0 + c_w * (t - math.sin(self.w * t) / self.w)

    def dist(self, t):
        if t < self.t1:
            c = self.A
            s = 0
        else:
            t -= self.t1
            c = -self.A
            s = self.S1 + self.vmax * t

        c_w = c / self.w

        return s + c_w * (0.5 * t * t + (math.cos(self.w * t) - 1) / (self.w * self.w) )

if __name__ == '__main__':

    cnt = 500
    fig = plt.figure()

    for idx in range(2):
        S_all = 3 if idx == 0 else -3

        sc = SCurve(S_all)
        ts = np.linspace(0, 2 * sc.t1, cnt)

        dt = 2 * sc.t1 / cnt

        # jerk
        ax = fig.add_subplot(4, 2, 1 + idx)
        ax.plot(ts, [sc.jerk(t) for t in ts], color='blue')
        ax.set_title('jerk', fontname="Meiryo")

        # acceleration
        ax = fig.add_subplot(4, 2, 3 + idx)
        ax.plot(ts, [sc.acc(t) for t in ts], color='blue')
        ax.plot(ts, list(itertools.accumulate([sc.jerk(t) * dt for t in ts])), color='red')
        ax.set_title('acceleration', fontname="Meiryo")

        # velocity
        ax = fig.add_subplot(4, 2, 5 + idx)
        ax.plot(ts, [sc.vel(t) for t in ts], color='blue')
        ax.plot(ts, list(itertools.accumulate([sc.acc(t) * dt for t in ts])), color='red')
        ax.set_title('velocity', fontname="Meiryo")

        # distance
        ax = fig.add_subplot(4, 2, 7 + idx)
        # ax.set_ylim(0, 1.1 * 2 * sc.S1)
        ax.plot(ts, [sc.dist(t) for t in ts], color='blue')
        ax.plot(ts, list(itertools.accumulate([sc.vel(t) * dt for t in ts])), color='red')
        ax.set_title('distance', fontname="Meiryo")

    fig.tight_layout()

    plt.show()