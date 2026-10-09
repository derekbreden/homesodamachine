#!/usr/bin/env python3
"""borrowed-05 (guide star) meets trials-03 (the dot is clipped by the wall): what a centroid loop does at the seam.
Independent check of scene trials-20-guide-at-the-knee (same model, other random draws).

1-D model along r (mm, 0 = seam, plate at r < 0, wall at r >= 0). A top camera sees only the part of the dot lying on the plate.
The dot's footprint is a bar of width w centred at x; visible part = [x - w/2, min(x + w/2, 0)].
  centroid c(x) = mean of the visible part, fraction f(x) = visible / w.
c has slope 1 while the dot is wholly on the plate, 1/2 while it straddles the seam, 0 once it has gone.
ILLUSTRATIVE: w = d / cos(beta), d = 0.5 mm, beta = 32 deg (trials-03); centroid noise 0.025 mm (0.6 px at 24 px/mm, borrowed-05),
fraction noise 0.02, axis step 0.02 mm, drift 0.3 mm/min toward the wall, loop every 0.5 s, gain 0.6, sub-step commands dropped,
star lost -> back off 5 steps (0.1 mm) toward the plate.
Schemes:
  centroid : guide the centroid to the seam pixel (c = 0), slope from a calibration on the plate side (1.0) or a supplied value
  fraction : approach with the centroid to -0.4 w, then guide the visible fraction to 0.5 (dx = gain (f - 0.5) w)
"""
import math
import numpy as np

D, BETA, STEP, DRIFT, GAIN = 0.5, math.radians(32), 0.02, 0.3 / 60, 0.6
W = D / math.cos(BETA)

def visible(x, w=W):
    lo, hi = x - w / 2, min(x + w / 2, 0.0)
    if hi <= lo + 1e-9: return None, 0.0
    return 0.5 * (lo + hi), (hi - lo) / w

def slope_by_nudge(x0, dx=0.16, n=3):
    c0, _ = visible(x0); c1, _ = visible(x0 + n * dx)
    return None if c0 is None or c1 is None else (c1 - c0) / (n * dx)

def run(scheme, x0=-1.0, slope=1.0, seconds=60, sig_c=0.025, sig_f=0.02, seed=0):
    rng = np.random.default_rng(seed)
    steps, t, hist, lost = 0, 0.0, [], 0
    while t < seconds:
        t += 0.5
        x = x0 + steps * STEP + DRIFT * t
        c, f = visible(x)
        n = 0
        if c is None:
            n = -5; lost += 1
        else:
            cm = np.mean(c + rng.normal(0, sig_c, 3)); fm = min(1, max(0, np.mean(f + rng.normal(0, sig_f, 3))))
            if scheme == 'centroid' or fm > 0.97:
                target = 0.0 if scheme == 'centroid' else -0.4 * W
                u = GAIN * (target - cm) / (slope * STEP)
            else:
                u = GAIN * (fm - 0.5) * W / STEP
            n = int(round(u)) if abs(u) >= 0.6 else 0
        steps += n
        hist.append((t, x0 + steps * STEP + DRIFT * t, c is None))
    last = [h for h in hist if h[0] > seconds - 30]
    xs = np.array([h[1] for h in last])
    return xs.mean(), math.sqrt((xs ** 2).mean()), np.mean([h[2] for h in last])

if __name__ == '__main__':
    print('footprint width w = %.2f mm.  centroid slope vs dot position: 1 on the plate, 0.5 straddling, 0 gone.' % W)
    print('c(x) and f(x), x = dot centre past the seam (mm):')
    for x in (-1.0, -0.6, -0.3, -0.15, 0.0, 0.15, 0.3, 0.6):
        c, f = visible(x)
        print('  x %+5.2f  centroid %s  visible %3.0f %%' % (x, '%+.3f' % c if c is not None else '  gone', 100 * f))
    print('\nslope read by a nudge calibration (3 steps of 0.16 mm toward the wall) from different starting points:')
    for x0 in (-1.5, -0.8, -0.5, -0.3, -0.15, 0.0):
        s = slope_by_nudge(x0)
        print('  start %+5.2f  slope %s' % (x0, ('%.2f' % s) if s is not None else 'undefined (the star is lost while nudging)'))
    print('\na centroid target at the seam pixel needs a visible width of zero: the centre would sit at +w/2 = %.2f mm into the wall;' % (W / 2))
    print('the centre on the seam is a centroid of -w/4 = %.2f mm, or a visible fraction of 50 %%.' % (-W / 4))
    print('\nloops (start 1.0 mm short, last 30 s of 60, mean over 6 seeds): mean position, rms, fraction of time out of sight')
    for scheme, slope in (('centroid', 1.0), ('centroid', 0.53), ('fraction', 1.0)):
        r = np.array([run(scheme, slope=slope, seed=s) for s in range(6)])
        print('  %-9s slope assumed %.2f: mean %+.3f mm, rms %.3f mm, out of sight %.0f %%' % (scheme, slope, r[:, 0].mean(), r[:, 1].mean(), 100 * r[:, 2].mean()))
