#!/usr/bin/env python3
"""Python twin of scene borrowed-05-guide-star (a SIMULATION; every parameter illustrative).

Model: two stepper axes A (radial) and B (vertical) with backlash dead zones, a camera rolled by phi relative to the
axes, centroid noise, slow drift, optional tube runout (period 48.6 s = 2*pi*61.85 mm / 8 mm/s [derived]; amplitudes
0.125 / 0.15 mm = half of the rig-doc TIR limits 0.25 / 0.30 mm [repo]). Guide tick every 0.5 s.

Prints RMS error over the last 20 s of a 60 s run for a naive guide (assumes camera aligned with axes) and for a guide
that first calibrated by nudging, over a sweep of camera roll.
"""
import math
import numpy as np

def run(phi_deg, calibrate, runout, gain=0.6, kA=0.02, kB=0.03, blA=4, blB=6, s=24.0, sigma=0.6, drift=0.3, comp=True, seed=1, T=60.0, tick=0.5):
    rng = np.random.default_rng(seed)
    phi = math.radians(phi_deg); c, sn = math.cos(phi), math.sin(phi)
    axes = {'A': [0.0, 0.0, 0], 'B': [0.0, 0.0, 0]}   # cmd, pos, last direction
    lim = {'A': round(6 / kA), 'B': round(6 / kB)}; bl = {'A': blA, 'B': blB}; k = {'A': kA, 'B': kB}
    init = np.array([0.35, -0.25]); t = 0.0

    def move(ax, n):
        a = axes[ax]; a[0] += n
        if abs(a[0]) > lim[ax]: a[0] = math.copysign(lim[ax], a[0])
        d = a[0] - a[1]
        if d > bl[ax] / 2: a[1] = a[0] - bl[ax] / 2
        elif d < -bl[ax] / 2: a[1] = a[0] + bl[ax] / 2

    def true_pos(t):
        w = 2 * math.pi / 48.6
        r = np.array([0.125 * math.sin(w * t), 0.15 * math.sin(w * t + 1.05)]) if runout else np.zeros(2)
        d = drift / 60 * t
        return init + np.array([axes['A'][1] * kA + 0.8 * d, axes['B'][1] * kB + 0.6 * d]) + r

    def px(p): return np.array([s * (c * p[0] - sn * p[1]), -s * (sn * p[0] + c * p[1])])
    def meas(n, t): return np.mean([px(true_pos(t)) + rng.normal(0, sigma, 2) for _ in range(n)], axis=0)

    N = 24.0 * 0.02                                    # naive px per step (0.48)
    M = np.array([[N, 0], [0, -N]])                    # columns: axis A, axis B
    blhat = {'A': 0.0, 'B': 0.0}
    if calibrate:
        for ax, col in (('A', 0), ('B', 1)):
            for _ in range(2): move(ax, 8); t += 0.32
            p0 = meas(6, t)
            for _ in range(3): move(ax, 8); t += 0.32
            p3 = meas(6, t)
            v = (p3 - p0) / 24.0
            for _ in range(5): move(ax, -8); t += 0.32
            q5 = meas(6, t)
            eff = np.linalg.norm(q5 - p3) / max(np.linalg.norm(v), 1e-9)
            M[:, col] = v; blhat[ax] = max(0.0, 40 - eff)
    hist = []; next_tick = t; end = t + T
    while t < end:
        if t >= next_tick:
            e = -meas(3, t)                             # target pixel minus dot pixel, target at (0,0) in these units
            e = -(meas(3, t) - px(np.zeros(2)))
            dA, dB = np.linalg.solve(M, e) * gain
            for ax, dd in (('A', dA), ('B', dB)):
                n = int(round(dd))
                if abs(dd) < 0.6: n = 0
                if n == 0: continue
                d = 1 if n > 0 else -1
                if comp and calibrate and axes[ax][2] != 0 and d != axes[ax][2]: n += d * int(round(blhat[ax]))
                axes[ax][2] = d; move(ax, n)
            next_tick += tick
        hist.append((t, true_pos(t)))
        t += 0.1
    last = np.array([h[1] for h in hist if h[0] > end - 20])
    return np.sqrt((last ** 2).mean(axis=0))

if __name__ == '__main__':
    print('RMS error (mm) over the last 20 s of a 60 s guide run: radial / vertical. Runout on, drift 0.3 mm/min, sigma 0.6 px.')
    print('phi   naive guide          calibrated guide')
    for phi in (0, 27, 45, 65, 75, 85):
        a = run(phi, False, True); b = run(phi, True, True)
        print('%3d   %7.3f / %-7.3f     %6.3f / %-6.3f' % (phi, a[0], a[1], b[0], b[1]))
    print()
    print('Without runout, calibrated guide, backlash compensation on vs off (phi 65):')
    print('  on : %.3f / %.3f' % tuple(run(65, True, False, comp=True)))
    print('  off: %.3f / %.3f' % tuple(run(65, True, False, comp=False)))
    print('Guide gain sweep, naive guide, phi 65, no runout:')
    for g in (0.2, 0.4, 0.6, 0.8, 1.0):
        print('  gain %.1f: %.3f / %.3f' % ((g,) + tuple(run(65, False, False, gain=g))))
