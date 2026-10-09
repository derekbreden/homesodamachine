"""Hinged-lid retract sweep: which horizontal hinge lines let the posed proxy gun leave the recess
without touching the lip, and how far the lid must open to clear the loading column.
Fine steps (0.05 deg) near the start: coarse steps let the wire tip jump through the wall.
Assumptions: proxy geometry and opening pose from pose.js [Agent-illustrative]; wire tip starts
in the corner; lift-clear = nothing within r<95 below rim+45; full-open = nothing within r<95
below rim+320."""
import math
from proxy import *
import sys
DIAL = float(sys.argv[1]) if len(sys.argv) > 1 else 30.0   # scene hole dial; 30 = Derek's opening pose
pts_local, tags = proxy_points()
P0 = [pose(p, 45, DIAL, -15) for p in pts_local]

def angles():
    a = 0.0
    while a < 10: 
        a += 0.05; yield a
    while a < 150:
        a += 0.5; yield a

def sweep(axis_pt, u, sign):
    lift = full = None
    for d in angles():
        ang = sign * math.radians(d)
        Q = [rot_about_axis(p, axis_pt, u, ang) for p in P0]
        for q, t in zip(Q, tags):
            if collides_tube(q, margin=0.0 if d < 1 else 1.0):
                return ('COLLIDE', round(d, 2), t)
        if lift is None and all((math.hypot(q[0], q[1]) > 95 or q[2] > RIM + 45) for q in Q):
            lift = round(d, 1)
        if full is None and all((math.hypot(q[0], q[1]) > 95 or q[2] > RIM + 320) for q in Q):
            full = round(d, 1)
    return ('OK', lift, full)

if __name__ == '__main__':
    print('hole dial', DIAL)
    ok = []
    for kind, u in (('Y', (0, 1, 0)), ('X', (1, 0, 0))):
        for off in (-250, -200, -150, -100, 100, 150, 200, 250):
            for dz in (20, 60, 120, 200, 280):
                for sign in (1, -1):
                    ap = (off, 0, RIM + dz) if kind == 'Y' else (0, off, RIM + dz)
                    r = sweep(ap, u, sign)
                    if r[0] == 'OK':
                        ok.append((kind, off, dz, sign, r[1], r[2]))
    for o in ok:
        print('axis ||%s at %s=%4d, %3d above rim, sign %2d: lift-clear %s deg, full-open %s deg' % (o[0], 'x' if o[0]=='Y' else 'y', o[1], o[2], o[3], o[4], o[5]))
