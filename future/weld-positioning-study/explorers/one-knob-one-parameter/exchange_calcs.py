"""Wave-2 calculations for one-knob-one-parameter--on--borrowed-ecosystems.md.

1. The scene's hole dial vs the rotation pose.js receives (dial - 35).
   borrowed-ecosystems/geometry.py passes 30 straight in as the rotation,
   i.e. scene dial 65.  Compare the numbers their notes rest on at both.
2. A1 rider at the scene's real opening pose (dial 30): where the gun passes
   over the rim relative to the rider stations; CG position for the hook.
3. A1-G: a work-angle arc about the tangent line through the dot, carried on
   the rider.  How much a rotation about that line disturbs the wire, compared
   with Derek's grip roll; arc clearance to the gun proxy.
4. C: the vertical-axis angle as a G2/G3 arc about the tube axis (exact)
   versus a straight tangent move (Y only).
5. Software pivot: residual dot motion when the stage axis location is
   mis-calibrated by d.

Frames and proxy as geometry.py (scene frame, dot at (61.85, 0, 146.05)).
Run: python3 exchange_calcs.py
"""
import math
import numpy as np
from geometry import pose_point, proxy_points, JOINT, GRIP_BASE, R_IN, R_OUT, TUBE_H, BENCH_Z

BE_CG_LOCAL = [0, -20, 190]          # borrowed-ecosystems' CG proxy [their assumption]
G0 = 9.81


def unit(v):
    return v / np.linalg.norm(v)


def section1():
    print("== 1. Opening pose at scene dial 30 (what the scene shows) vs dial 65 (hole=30 passed as rotation)")
    for dial in (30, 65):
        tip = pose_point([0, 0, 0], 45, dial, -15)
        back = pose_point([0, 0, 253], 45, dial, -15)
        gb = pose_point(GRIP_BASE, 45, dial, -15)
        cg = pose_point(BE_CG_LOCAL, 45, dial, -15)
        bdir = unit(back - tip)
        # umbilical loop, borrowed-ecosystems' method: exit along local (0,-0.443,0.897), R = 350
        p1 = pose_point(np.array(GRIP_BASE) + np.array([0, -0.443, 0.897]) * 100, 45, dial, -15)
        d = unit(p1 - gb)
        elev = math.asin(d[2])
        apex = gb[2] - BENCH_Z + 350 * (1 - math.cos(elev))
        # gravity torques about the three axes for 1 and 2 kg
        r = (cg - JOINT) / 1000
        ga = unit(gb - JOINT)
        v = math.radians(-15)
        axes = {"grip": ga, "hole": np.array([math.cos(v), math.sin(v), 0]), "vertical": np.array([0, 0, 1.0])}
        tq = {k: [float(np.dot(np.cross(r, [0, 0, -m * G0]), a)) for m in (1, 2)] for k, a in axes.items()}
        print(f"  dial {dial}: barrel elevation {math.degrees(math.asin(bdir[2])):.0f} deg; nozzle tip {tip[2]-146.05:+.1f} above dot "
              f"({tip[2]-TUBE_H:+.1f} vs rim); grip base {gb[2]-146.05:.0f} above dot, plan ({gb[0]:.0f},{gb[1]:.0f})")
        print(f"           CG proxy plan ({cg[0]:.0f},{cg[1]:.0f}) {cg[2]-146.05:.0f} above dot; umbilical exit elev {math.degrees(elev):.0f} deg, "
              f"apex {apex:.0f} mm above bench")
        print("           gravity torque N*m (1 kg / 2 kg): " + ", ".join(f"{k} {a:+.2f}/{b:+.2f}" for k, (a, b) in tq.items()))


def gun_samples(roll, dial, vert):
    return np.vstack([np.array([pose_point(p, roll, dial, vert) for p in v]) for v in proxy_points().values()])


def section2():
    print("\n== 2. A1 rider stations vs the gun at the real opening pose (45, dial 30, -15)")
    pts = gun_samples(45, 30, -15)
    th = np.degrees(np.arctan2(pts[:, 1], pts[:, 0]))
    r = np.hypot(pts[:, 0], pts[:, 1])
    for a0, a1 in ((-20, -40), (-40, -70), (-70, -100), (-100, -130)):
        m = (th <= a0) & (th >= a1) & (r > 40) & (r < 90)
        if m.any():
            print(f"  gun over the rim band r 40-90, theta {a0}..{a1}: lowest point {pts[m,2].min()-TUBE_H:+.0f} mm vs rim")
        else:
            print(f"  gun over the rim band r 40-90, theta {a0}..{a1}: none")
    for name, ang in (("station 1", -30), ("station 2", -60)):
        p = np.array([R_OUT * math.cos(math.radians(ang)) - 1, R_OUT * math.sin(math.radians(ang)), TUBE_H])
        dmin = np.min(np.linalg.norm(pts - p, axis=1))
        print(f"  {name} at theta {ang}: nearest gun proxy point {dmin:.0f} mm away")


def section3():
    print("\n== 3. A1-G: work-angle arc about the tangent line through the dot")
    # wire guide end and wire direction from pose.js (local frame); wire tip at the dot
    guide_back_local = np.array([0, -24.7, 87.1])
    for label, fn in (("rotate about the tangent line (A1-G knob)", "tangent"), ("Derek's grip roll", "grip")):
        moves = []
        for dth in (5, 10):
            base = pose_point(guide_back_local, 45, 30, -15)
            if fn == "grip":
                moved = pose_point(guide_back_local, 45 + dth, 30, -15)
            else:
                # rotation about the local seam tangent (Y) through the dot
                a = math.radians(dth)
                v = base - JOINT
                R = np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
                moved = JOINT + R @ v
            w0, w1 = unit(base - JOINT), unit(moved - JOINT)
            moves.append((dth, np.linalg.norm(moved - base), math.degrees(math.acos(np.clip(np.dot(w0, w1), -1, 1)))))
        print(f"  {label}: " + "; ".join(f"{d} deg -> wire guide end moves {m:.1f} mm, wire direction turns {t:.1f} deg" for d, m, t in moves))
    wdir = unit(pose_point(guide_back_local, 45, 30, -15) - JOINT)
    print(f"  wire approach at the opening pose: {math.degrees(math.asin(wdir[2])):.0f} deg elevation, "
          f"{math.degrees(math.acos(abs(wdir[1]) / math.hypot(wdir[0], wdir[1]))):.0f} deg off the tangent in plan")
    # arc clearance: quarter arc in plane y = y0, centred on the tangent line, radius R
    pts = gun_samples(45, 30, -15)
    for y0 in (-35, -45):
        for R in (60, 80):
            arc = np.array([[R_IN + R * math.cos(a), y0, 146.05 + R * math.sin(a)] for a in np.radians(np.arange(0, 61, 5))])
            dmin = min(np.min(np.linalg.norm(pts - q, axis=1)) for q in arc)
            wall = min(math.hypot(q[0], q[1]) - R_OUT for q in arc if q[2] < TUBE_H + 2) if any(q[2] < TUBE_H + 2 for q in arc) else float('nan')
            print(f"  arc plane y={y0}, R={R}, 0-60 deg: nearest gun proxy point {dmin:.0f} mm; clearance to OD below rim {wall:.0f} mm")


def section4():
    print("\n== 4. Vertical-axis angle by moving the dot: G2 arc about the tube axis vs a straight tangent move")
    for phi in (5, 10, 15, 30):
        s = R_IN * math.sin(math.radians(phi))          # straight tangent move giving the same approach change
        off = R_IN - math.hypot(R_IN, s)                 # how far the dot leaves the corner (negative = inside the wall)
        print(f"  {phi:2d} deg: arc about the tube axis keeps the dot on the corner exactly; "
              f"a straight tangent move of {s:.1f} mm leaves it {abs(off):.2f} mm off the corner (needs X {R_IN*(1-math.cos(math.radians(phi))):.2f} mm)")


def section5():
    print("\n== 5. Software pivot: stage axis location wrong by d -> dot moves d * dtheta per step")
    for d in (0.2, 0.5, 1.0, 2.0):
        print(f"  d = {d} mm: 2 deg step {d*math.radians(2):.3f} mm, 10 deg step {d*math.radians(10):.3f} mm")


if __name__ == "__main__":
    section1(); section2(); section3(); section4(); section5()
