#!/usr/bin/env python3
"""Which straight axes through the laser dot can have a shaft or bearing on them?

Behind scene borrowed-04-free-directions and the pivot-in-free-air observations.
Geometry: WK.DIM in kit/weldkit.js ([repo] tube 5.000 in OD, 0.065 in wall, 6 in long,
plate 4.860 in dia x 0.250 in, recess 0.250 in below the rim). Everything is axisymmetric,
so a point's clearance is a 2D rectangle distance in (r, z).

Solids used (mm):
  wall   r in [61.85, 63.50], z in [0, 152.4]            [derived from repo dims]
  plate  r in [0, 61.72],     z in [139.70, 146.05]      [derived]
The dot is at r = 61.85, z = 146.05, at the wall/plate corner. Directions are (azimuth in plan from
+X = outward radial, elevation above horizontal).

A one-sided (cantilever) axis with shaft radius rho, starting t0 mm from the dot and running L mm,
is 'free' if the shaft stays at least rho from the solids the whole way. A two-sided axis (a shaft
through the dot with bearings on both sides) needs both rays free.
"""
import math, sys

R_IN, R_OUT, H = 61.85, 63.50, 152.4
PLATE_R, PLATE_Z0, PLATE_Z1 = 61.722, 139.70, 146.05
DOT = (R_IN, 0.0, PLATE_Z1)

def rect_dist(r, z, r0, r1, z0, z1):
    dr = max(r0 - r, 0.0, r - r1)
    dz = max(z0 - z, 0.0, z - z1)
    return math.hypot(dr, dz)

def clearance(p):
    r = math.hypot(p[0], p[1])
    z = p[2]
    return min(rect_dist(r, z, R_IN, R_OUT, 0.0, H),
               rect_dist(r, z, 0.0, PLATE_R, PLATE_Z0, PLATE_Z1))

def ray_free(a, rho, t0, L, step=0.5):
    n = int((L - t0) / step) + 1
    worst = 1e9
    for i in range(n + 1):
        t = t0 + i * step
        p = (DOT[0] + a[0] * t, DOT[1] + a[1] * t, DOT[2] + a[2] * t)
        c = clearance(p)
        worst = min(worst, c)
        if c < rho:
            return False, worst
    return True, worst

def unit(v):
    m = math.sqrt(sum(x * x for x in v))
    return tuple(x / m for x in v)

def dirs(az, el):
    a, e = math.radians(az), math.radians(el)
    return (math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e))

NAMED = {
    'straight up (vertical axis)':          (0, 0, 1),
    'straight down':                        (0, 0, -1),
    'toward tube axis, level with plate':   (-1, 0, 0),
    'outward, level with plate':            (1, 0, 0),
    'along the tangent (crease line)':      (0, 1, 0),
    'up and inward 45 deg':                 unit((-1, 0, 1)),
    'up and outward 45 deg':                unit((1, 0, 1)),
    'inward 30 deg above plate':            unit((-math.cos(math.radians(30)), 0, math.sin(math.radians(30)))),
}

def sphere_fraction(rho, t0, L, both=False):
    free = tot = 0
    for el in range(-85, 90, 5):
        w = math.cos(math.radians(el))
        for az in range(0, 360, 5):
            a = dirs(az, el)
            ok, _ = ray_free(a, rho, t0, L, 1.0)
            if both:
                ok2, _ = ray_free(tuple(-x for x in a), rho, t0, L, 1.0)
                ok = ok and ok2
            free += w * (1 if ok else 0)
            tot += w
    return free / tot

if __name__ == '__main__':
    print('Named axes: free one-sided (starts 12 mm from the dot, runs 150 mm) for shaft radius rho')
    print('%-40s' % 'direction', *['rho=%-4g' % r for r in (0, 2, 5, 10, 20)])
    for name, a in NAMED.items():
        row = []
        for rho in (0, 2, 5, 10, 20):
            ok, worst = ray_free(unit(a), rho, 12, 150)
            row.append('free ' if ok else 'BLOCK')
        print('%-40s' % name, *['%-8s' % x for x in row])
    print()
    print('Fraction of the sphere of directions that is free (one-sided), t0=12, L=150:')
    for rho in (0, 2, 5, 10, 20, 30):
        print('  rho=%-3g  one-sided %.3f   two-sided (both rays) %.3f' % (rho, sphere_fraction(rho, 12, 150), sphere_fraction(rho, 12, 150, True)))
    print()
    print('Vertical axis: how high must a ring bearing sit above the dot to clear the rim, ring bore radius b?')
    print('  the rim is 6.35 mm above the dot; the ring (thin) sits at height h; its bore of radius b is centred on the axis.')
    print('  A ring at h > 6.35 + margin clears the rim wherever b is, because the wall stops at the rim; b only has to clear the gun.')
    print()
    print('Cantilever shaft along the vertical axis: clearance to the wall is 0 for the first 6.35 mm (axis lies on the wall face),')
    print('so the shaft radius there must be 0; a ring bearing has no shaft on the axis, so no such limit.')
    # inward horizontal axis: lies on the plate top, clearance 0
    print()
    print('Inward horizontal axis (hole axis when yaw = 0): its clearance along the ray, from the dot:')
    for t in (5, 12, 20, 40):
        p = (DOT[0] - t, 0, DOT[2])
        print('  t=%2d mm: clearance to plate/wall %.2f mm (the axis lies on the plate face)' % (t, clearance(p)))
