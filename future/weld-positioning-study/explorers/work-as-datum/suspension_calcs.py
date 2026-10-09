"""Wave-3 numbers for the work-hung suspension (Derek's tip loop hung from the endcap).

Scene opening pose (grip 45, hole dial 30, vertical -15), dial offset applied.
Frame: origin on the tube axis at the plate's outer face, dot at (61.85, 0, 0).
[Agent] scene proxy, [Est] this explorer's estimate, [Unknown] not measured.
Run:  python3 suspension_calcs.py
"""
import math
import numpy as np
from pose_geometry import pose_point, GRIP_BASE

POSE = (45, 30, -15)
P = lambda p: np.array(pose_point(p, *POSE))
dot = P((0, 0, -16))

print("=== where the loops sit ===")
for zl in (10, 20, 30, 40):
    q = P((0, 0, zl))
    print(f"  nose collar at barrel z={zl:>2}: ({q[0]:5.1f},{q[1]:6.1f},{q[2]:5.1f})  "
          f"{np.linalg.norm(q-dot):4.0f} mm from the dot; r {math.hypot(q[0],q[1]):4.1f} from the tube axis; "
          f"{q[2]-6.35:4.1f} above the rim")
gb = P(GRIP_BASE)
axis = (gb - dot) / np.linalg.norm(gb - dot)
base = gb + 40 * axis           # base loop 40 mm beyond the grip butt [carry-and-locate]
print(f"  grip base ({gb[0]:.1f},{gb[1]:.1f},{gb[2]:.1f}); base loop ~({base[0]:.1f},{base[1]:.1f},{base[2]:.1f})")

print("\n=== how much a base-loop motion reaches the dot (nose loop = ball joint on the work) ===")
for zl in (10, 30):
    nose = P((0, 0, zl))
    a = np.linalg.norm(nose - dot)
    b = np.linalg.norm(base - nose)
    k = a / b
    print(f"  nose at {a:.0f} mm from the dot, base {b:.0f} mm from the nose: dot moves {k:.3f} x base motion")
    for kb, name in ((0.1, "Derek's bungee pair (~0.1 N/mm) [carry-and-locate est]"),
                     (13.0, "2 mm polyester line 500 mm (~13 N/mm)"),
                     (100.0, "1/16 in stainless rope 500 mm (~100 N/mm)")):
        print(f"    base held by {name}: 1 N at the base -> dot {k/kb:.3f} mm")
    for d in (0.15, 1.0, 3.2):
        print(f"    work moves {d} mm under a fixed base -> dot misses the moved corner by {k*d:.2f} mm, "
              f"gun turns {math.degrees(d/b):.2f} deg")

print("\n=== weight shares (two vertical supports: nose V and base loop) ===")
# Gun + shell mass and CoM [Unknown]; two guesses: housing centre, and 30 mm
# toward the grip. 1.2 kg gun + 0.4 kg shell [Est].
W = 1.6 * 9.81
for zl in (30,):
    nose = P((0, 0, zl))
    for label, cg_local in (("CoM at housing centre", (0, 0, 185)), ("CoM toward the grip", (0, -30, 200))):
        cg = P(cg_local)
        # project onto the nose->base line in plan
        d = (base - nose)[:2]
        t = np.dot((cg - nose)[:2], d) / np.dot(d, d)
        off = abs(np.cross(np.append(d, 0), np.append((cg - nose)[:2], 0))[2]) / np.linalg.norm(d)
        print(f"  {label}: nose carries {(1-t)*100:.0f} % ({(1-t)*W:.1f} N), base {t*100:.0f} %; "
              f"CoM {off:.0f} mm off the nose-base line -> roll moment {W*off/1000:.2f} N*m for the third ring")

print("\n=== the nose V-seat ===")
nose = P((0, 0, 30))
bar = (P((0, 0, 31)) - nose)
bar /= np.linalg.norm(bar)
g = np.array([0, 0, -1.0])
g_in_plane = g - np.dot(g, bar) * bar
print(f"  barrel direction {bar.round(3)}; gravity's share in the ring plane {np.linalg.norm(g_in_plane):.2f}, "
      f"along the barrel {abs(np.dot(g, bar)):.2f} (taken by the groove)")
for Wn in (7.0, 10.0):
    seat = Wn * np.linalg.norm(g_in_plane)
    for half in (45,):
        print(f"  nose share {Wn} N: seats {seat:.1f} N in the V; sideways capacity before climbing a 90 deg V "
              f"~{seat*math.tan(math.radians(half)):.1f} N; axial load on the groove {Wn*abs(np.dot(g, bar)):.1f} N")

print("\n=== what the nose load does to the plate-borne hub ===")
for Wn in (7.0, 10.0):
    mx = Wn * abs(nose[1]) / 1000   # about the dot's radius (X line)
    my = Wn * abs(nose[0]) / 1000   # about Y
    print(f"  {Wn} N at the nose ({nose[0]:.0f},{nose[1]:.0f}): {my:.2f} N*m about Y (plate rollers + clamp), "
          f"{mx:.2f} N*m about the dot's radius (room wire or foot)")
print("  compare: loose tube lifts at 0.9-2.5 N*m; the paddle's pin-and-roller clamp at ~20 N x 38 mm = 0.76 N*m per side")

print("\n=== stuck wire ===")
for F in (3.0, 5.0):
    print(f"  {F} N tangential at the dot: torque about the tube axis {F*61.85/1000:.2f} N*m on the hub's azimuth restraint")
