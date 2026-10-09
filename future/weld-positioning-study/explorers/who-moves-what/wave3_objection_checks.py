"""Wave 3: sequence-of-use's objections to my ideas were computed at hole dial 65.
Re-check the pose-dependent ones at the true opening pose (dials 45 / 30 / -15) and
at dial 65, with this study's posePoint port and the vendored proxy point cloud.
1. Wire retraction (along the wire's own line) needed to lift the tip above the rim.
2. Plate head from P (their x2 idea): pad stems at r = 40 mm vs the gun, for their
   pad angles (180, +60, -60) and an alternative (150, 30, 250).
3. D2 rings: gravity torque about the grip axis (CoM proxy at local z = 185.5).
"""
import math
import numpy as np
from geometry import pose_dial, world, CAPSULES, R_IN, RIM, CAP_TOP, FEATURES
import vendored_sou_proxy as V

PTS, TAGS = V.proxy_points()

def posed(dial, grip=45, yaw=-15):
    return [np.array(pose_dial(p, grip, dial, yaw)) for p in PTS]

print("== 1. wire line and retraction to clear the rim (+1 mm)")
for dial in (30, 65):
    pts = posed(dial)
    tip = pts[0]; back = pts[30]
    u = (back - tip) / np.linalg.norm(back - tip)
    elev = math.degrees(math.asin(u[2]))
    need = (RIM + 1 - tip[2]) / u[2]
    print(f"   dial {dial}: wire elevation {elev:.1f} deg; retract {need:.1f} mm along the wire to lift the tip 1 mm above the rim")

print("\n== 2. plate head pad stems (r = 40 mm, from rim+40 down to the plate) vs gun capsules")
def seg_dist(p, a, b):
    ab = b - a; t = np.clip(np.dot(p - a, ab) / np.dot(ab, ab), 0, 1)
    return np.linalg.norm(p - (a + t * ab))
def stem_clear(dial, ang_deg, stem_r=5.0):
    ang = math.radians(ang_deg)
    top = np.array([40 * math.cos(ang), 40 * math.sin(ang), RIM + 40])
    bot = np.array([40 * math.cos(ang), 40 * math.sin(ang), CAP_TOP + 2])
    best = 1e9
    for name, (a, b, rad) in CAPSULES.items():
        for t in np.linspace(0, 1, 40):
            q = world((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])), (45, dial, -15))
            best = min(best, seg_dist(q, top, bot) - rad - stem_r)
    # spider arm from the axis to the stem top
    arm_best = 1e9
    for name, (a, b, rad) in CAPSULES.items():
        for t in np.linspace(0, 1, 40):
            q = world((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])), (45, dial, -15))
            arm_best = min(arm_best, seg_dist(q, np.array([0, 0, RIM + 40.0]), top) - rad - stem_r)
    return best, arm_best
for dial in (30, 65):
    for layout in ((180, 60, -60), (150, 30, 250), (180, 90, 20)):
        res = [stem_clear(dial, a) for a in layout]
        print(f"   dial {dial} pads {layout}: stem clearances {[round(r[0],1) for r in res]} mm, spider-arm {[round(r[1],1) for r in res]} mm")

print("\n== 3. D2: gravity torque about the grip axis, CoM proxy local (0, 0, 185.5)")
for dial in (30, 65):
    pose = (45, dial, -15)
    dot = world(FEATURES['dot'], pose); gb = world(FEATURES['grip_base_QBH'], pose)
    g = (gb - dot) / np.linalg.norm(gb - dot)
    com = world((0.0, 185.5), pose)
    r = com - dot
    off = np.linalg.norm(r - np.dot(r, g) * g)
    for m in (0.8, 1.4):
        Wv = np.array([0, 0, -9.81 * m])
        tq = np.dot(np.cross(r / 1000, Wv), g)
        print(f"   dial {dial}, {m} kg: CoM {off:.0f} mm off the grip axis (axis elevation {math.degrees(math.asin(g[2])):.0f} deg); gravity torque about the axis {tq:+.2f} N*m")
