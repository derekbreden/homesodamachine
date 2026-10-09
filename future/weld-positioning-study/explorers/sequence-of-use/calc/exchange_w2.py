"""Pose: scene hole DIAL 30 (Derek's opening pose) since the wave-3 convention fix;
the wave-2 file quotes the dial-65 run. Wave-2 calcs for the exchange with who-moves-what. Proxy gun (pose.js opening pose).

1. Still gun: can the tube leave sideways with the wire tip in the corner? Which direction?
   How much drop, or how much wire pullback, clears it?
2. Stand-hung plate head: clearance between the proxy gun and a hanger head inside the
   tube top (pads at r=40 at 180/+-60 deg, frame within r<=45 away from the station,
   arm leaving toward -X at rim+40).
3. Carrier rings (D2): gun CG offset from the grip axis -> roll torque when roll is free.
4. Balancer-hung gun pulled to a park position: pendulum restoring force.
5. Drawer lateral play -> yaw (their 1.08 mm/deg).
"""
import math
from proxy import *

pts, tags = proxy_points()
P0 = [pose(p) for p in pts]

print('== 1. tube leaving a still gun, wire tip in the corner (proxy standoff 16 mm)')
def depart(dirdeg, drop, pull=0.0, travel=200):
    # pull: wire retracted along its own line by `pull` mm (tip moves toward guide)
    wt, wb = pose((0, 0, -CL)), pose((0, -24.7, 87.1))
    u = [(wb[i] - wt[i]) / math.dist(wb, wt) for i in range(3)]
    Q = []
    for q, t in zip(P0, tags):
        if t == 'wire':
            # shift wire points along the wire direction if they lie in the retracted zone
            q = tuple(q[i] + pull * u[i] for i in range(3))
        Q.append((q, t))
    ph = math.radians(dirdeg)
    s = 0.0
    while s <= travel:
        cx, cy = s * math.cos(ph), s * math.sin(ph)
        dz = min(drop, drop * s / 5.0) if drop else 0.0   # drop happens in the first 5 mm of motion
        for q, t in Q:
            qq = (q[0] - cx, q[1] - cy, q[2] + dz)
            if collides_tube(qq, margin=0.0 if s < 0.6 else 0.8):
                return f'COLLIDE at {s:.1f} mm ({t})'
        s += 0.5
    return 'clear'
for d in (0, 180, 90, -90):
    for drop in (0, 5, 10, 20):
        print(f'   tube moves toward {d:4d} deg (0=+X station side), drop {drop:2d}: {depart(d, drop)}')
wt, wb = pose((0, 0, -CL)), pose((0, -24.7, 87.1))
elev = math.degrees(math.asin((wb[2] - wt[2]) / math.dist(wb, wt)))
print(f'   wire elevation {elev:.1f} deg; pullback to lift tip 6.35+1 mm above rim: {(RECESS+1)/math.sin(math.radians(elev)):.1f} mm')
for pull in (4, 8, 10, 14):
    print(f'   no drop, wire pulled back {pull:2d} mm, tube toward +X: {depart(0, 0, pull)}; toward -X: {depart(180, 0, pull)}')

print('\n== 2. stand-hung plate head vs proxy gun')
def seg_pts(a, b, n=40):
    return [tuple(a[i] + (b[i] - a[i]) * k / n for i in range(3)) for k in range(n + 1)]
head = []
for ang in (180, 60, -60):
    x, y = 40 * math.cos(math.radians(ang)), 40 * math.sin(math.radians(ang))
    head += seg_pts((x, y, CAP_TOP), (x, y, RIM + 40))          # pad legs
    head += seg_pts((0, 0, RIM + 40), (x, y, RIM + 40))          # spokes at rim+40
head += seg_pts((0, 0, CAP_TOP + 12), (0, 0, RIM + 40))         # spindle, fork 12 mm above plate
head += seg_pts((0, 0, RIM + 40), (-200, 0, RIM + 40))          # arm to the stand, -X side
for hz in (40, 25):
    H2 = [(p[0], p[1], p[2] - (40 - hz) if p[2] > RIM else p[2]) for p in head]
    dmin, who = 1e9, None
    for q, t in zip(P0, tags):
        for h in H2:
            d = math.dist(q, h)
            if d < dmin:
                dmin, who = d, (t, [round(v, 1) for v in q], [round(v, 1) for v in h])
    print(f'   frame at rim+{hz}: closest gun point {dmin:.1f} mm (gun part {who[0]} at {who[1]}, head at {who[2]}) [centre-line distances; subtract member radii]')

print('\n== 3. gun CG vs grip axis (proxy CG at housing centre)')
dot, gb, cg = pose((0, 0, -CL)), pose(GB), pose((0, 0, 185.5))
a = [(gb[i] - dot[i]) / math.dist(gb, dot) for i in range(3)]
v = [cg[i] - dot[i] for i in range(3)]
along = sum(v[i] * a[i] for i in range(3))
perp = [v[i] - along * a[i] for i in range(3)]
off = math.sqrt(sum(t * t for t in perp))
g_perp = math.sqrt(1 - a[2] ** 2)   # fraction of gravity perpendicular to the axis
print(f'   CG is {off:.1f} mm off the grip axis; axis elevation {math.degrees(math.asin(a[2])):.1f} deg')
for m in (0.8, 1.0, 1.4):
    print(f'   mass {m} kg (gun+shell): max roll torque {m*9.81*off/1000*g_perp:.2f} N*m if roll is free on the rings')

print('\n== 4. balancer-hung gun pulled sideways to park (pendulum)')
for W in (10, 15, 20):
    for L in (0.8, 1.2):
        for x in (150, 300):
            print(f'   weight {W} N, line {L} m, {x} mm aside: restoring force {W*x/1000/L:4.1f} N')

print('\n== 5. drawer lateral play -> yaw (their 1.08 mm/deg)')
for play in (0.2, 0.5, 1.0):
    print(f'   {play} mm along the tangent -> {play/1.0795:.2f} deg of yaw')
