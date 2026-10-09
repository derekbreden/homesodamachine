"""Hole angles are scene dials (opening pose dial 30). Idea B: gun fixed, tube+rotator come in on a drawer and rise on end ramps.
Checks the proxy gun against the moving tube for approach direction phi (0 = tube arrives
moving -X, i.e. from the weld-station side), a drop of DROP mm held until the ramp, and a
linear ramp over the last RAMP mm. Relative motion: gun point p vs tube shifted by (c, drop).
"""
import math
from proxy import *
pts_local, tags = proxy_points()
P0 = [pose(p) for p in pts_local]

def check(phi_deg, drop, ramp, travel=250, step=0.5):
    phi = math.radians(phi_deg)
    worst = None
    s = travel
    while s >= 0:
        cx, cy = s * math.cos(phi), s * math.sin(phi)
        dz = drop if s > ramp else drop * s / ramp   # tube lowered by dz
        for q, t in zip(P0, tags):
            qq = (q[0] - cx, q[1] - cy, q[2] + dz)      # gun point in the moving tube's frame
            if collides_tube(qq, margin=0.0 if s < 1 else 0.8):
                return ('COLLIDE', round(s, 1), t, [round(v, 1) for v in qq])
        s -= step
    return ('OK',)

if __name__ == '__main__':
  for phi in (0, 20, 40, 60):
    for drop in (10, 15, 20, 25, 35):
        for ramp in (30, 60, 100):
            r = check(phi, drop, ramp)
            print(f'phi={phi:3d} drop={drop:3d} ramp={ramp:3d}:', r)
