"""Wave 2 checks on sequence-of-use's lid carrier (idea A), run with THEIR proxy point
cloud and collision test (vendored copy: vendored_sou_proxy.py, from
explorers/sequence-of-use/calc/proxy.py, 2026-09-28).

1. Does the chosen hinge (axis || Y at x = 200, rim + 60) stay collision-free across a
   range of recipe poses, with yaw realized two ways:
     (a) the gun turned about the vertical through the dot (pose vert = yaw), or
     (b) the gun kept at room yaw 0 and slid along the tangent (tube symmetry),
         so the dot lands on the seam point at angle theta = -yaw.
2. Latch force for a seat triangle kept entirely behind the station (no front vee
   over the tube), versus their spanning triangle.
3. How tube-length variation shows up at the hinge escape if Z is taken by the work
   (rim returned to nominal) versus by a Z slide on the lid.

Pose convention: all poses here are the scene's DIALS (grip, hole dial, vertical).
main.js passes hole dial - 35 to posePoint. To stay independent of how their
proxy.pose() is defined (it changed to take dials during wave 2), their local point
cloud is posed with this study's own exact port, geometry.pose_dial(). Only their
point cloud, rotation helper and collision test are used. Derek's opening pose is
dials 45 / 30 / -15.
(A first run of this file passed the hole value straight through, i.e. dial 65,
matching their proxy's default; those results are kept, labelled, in the exchange
file.)

Run: tools/cad-venv/bin/python wave2_lid_checks.py
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
import vendored_sou_proxy as P  # noqa: E402  (copy of their point cloud + collision test)
from geometry import pose_dial  # noqa: E402  (exact port of posePoint + main.js dial offset)

PTS, TAGS = P.proxy_points()
HINGE = (200.0, 0.0, P.RIM + 60.0)
U = (0.0, 1.0, 0.0)


DIAL_OFFSET = 35.0


def _pose(p, roll, hole_dial, yaw):
    return tuple(float(v) for v in pose_dial(p, roll, hole_dial, yaw))


def posed_points(roll, hole_dial, yaw, mode, dz=0.0):
    if mode == "rotate":
        pts = [_pose(p, roll, hole_dial, yaw) for p in PTS]
    else:  # slide: room yaw 0, translate so dot sits at seam angle theta = -yaw
        th = math.radians(-yaw)
        tx = P.R_IN * math.cos(th) - P.R_IN
        ty = P.R_IN * math.sin(th)
        pts = [tuple(a + b for a, b in zip(_pose(p, roll, hole_dial, 0), (tx, ty, 0.0))) for p in PTS]
    if dz:
        pts = [(x, y, z + dz) for x, y, z in pts]
    return pts


def angles():
    a = 0.0
    while a < 10:
        a += 0.05
        yield a
    while a < 150:
        a += 0.5
        yield a


def sweep(pts, sign=1, tube_dz=0.0, hinge=None, u=None):
    """Rotate the posed points about the hinge; tube shifted by tube_dz (rim moves)."""
    lift = full = None
    hinge = HINGE if hinge is None else hinge
    u = U if u is None else u
    for d in angles():
        ang = sign * math.radians(d)
        Q = [P.rot_about_axis(p, hinge, u, ang) for p in pts]
        for q, t in zip(Q, TAGS):
            qq = (q[0], q[1], q[2] - tube_dz)
            if P.collides_tube(qq, margin=0.0 if d < 1 else 1.0):
                return ("COLLIDE", round(d, 2), t)
        rim = P.RIM + tube_dz
        if lift is None and all((math.hypot(q[0], q[1]) > 95 or q[2] > rim + 45) for q in Q):
            lift = round(d, 1)
        if full is None and all((math.hypot(q[0], q[1]) > 95 or q[2] > rim + 320) for q in Q):
            full = round(d, 1)
    return ("OK", lift, full)


if __name__ == "__main__":
    print("== 0. Their 80-candidate hinge sweep (lid_swing2.py logic) at the TRUE opening pose, dials 45/30/-15")
    pts0 = posed_points(45, 30, -15, "rotate")
    ok = []
    for kind, u in (("Y", (0, 1, 0)), ("X", (1, 0, 0))):
        for off in (-250, -200, -150, -100, 100, 150, 200, 250):
            for dz in (20, 60, 120, 200, 280):
                for sgn in (1, -1):
                    ap = (off, 0, P.RIM + dz) if kind == "Y" else (0, off, P.RIM + dz)
                    r = sweep(pts0, sgn, hinge=ap, u=u)
                    if r[0] == "OK":
                        ok.append((kind, off, dz, sgn, r[1], r[2]))
    for o in ok:
        print(f"   OK: axis || {o[0]} at {'x' if o[0]=='Y' else 'y'}={o[1]:4d}, {o[2]:3d} above rim, sign {o[3]:+d}: lift-clear {o[4]}, full-open {o[5]}")
    print(f"   {len(ok)} of 160 candidates collision-free")

    print("\n== 1. Hinge x=200, rim+60, || Y, lifting sign; recipe range (dials); two yaw realizations")
    print("   (lift = column clear to rim+45, full = column clear to rim+320, degrees of lid)")
    sign = None
    for s in (1, -1):
        if sweep(posed_points(45, 30, -15, "rotate"), s)[0] == "OK":
            sign = s
    print(f"   lifting sign reproducing their result: {sign}")
    sign = sign or 1
    rows = []
    for mode in ("rotate", "slide"):
        for roll in (30, 45, 60):
            for hole in (15, 30, 45):  # hole dials
                for yaw in (-30, -15, 0, 15):
                    r = sweep(posed_points(roll, hole, yaw, mode), sign)
                    rows.append((mode, roll, hole, yaw, r))
    for mode in ("rotate", "slide"):
        bad = [r for r in rows if r[0] == mode and r[4][0] != "OK"]
        ok = [r for r in rows if r[0] == mode and r[4][0] == "OK"]
        print(f"   yaw by {mode}: {len(ok)} OK, {len(bad)} collide")
        for r in bad:
            print(f"      COLLIDE roll {r[1]} hole {r[2]} yaw {r[3]}: at {r[4][1]} deg, {r[4][2]}")
        if ok:
            lifts = [r[4][1] for r in ok if r[4][1] is not None]
            fulls = [r[4][2] for r in ok if r[4][2] is not None]
            print(f"      lift-clear {min(lifts)}-{max(lifts)} deg; full-open {min(fulls) if fulls else None}-{max(fulls) if fulls else None} deg")

    print("\n== 3. Tube length +/-3.2 mm (OnlineMetals cut tolerance, digest)")
    for dz in (-3.2, 0.0, 3.2):
        # (i) Z taken by a lid Z slide: gun moved with the rim, tube moved with the rim
        r1 = sweep(posed_points(45, 30, -15, "rotate", dz=dz), sign, tube_dz=dz)
        # (ii) Z taken by the work: rim returned to nominal, gun unchanged
        r2 = sweep(posed_points(45, 30, -15, "rotate"), sign, tube_dz=0.0)
        # (iii) nobody takes Z: the gun stays, the corner moves (tube_dz = dz, gun not moved)
        r3 = sweep(posed_points(45, 30, -15, "rotate"), sign, tube_dz=dz)
        print(f"   dz {dz:+.1f}: lid-Z slide {r1}; work-Z {r2}; untaken {r3}")

    print("\n== 2. Seat triangle kept behind the station (+X side only)")
    # lid + gun + shell weight ~2.2 kg (their assumption) at the gun CG proxy
    W = 2.2 * 9.81
    cg = _pose((0, 0, 185.5), 45, 30, -15)  # their CG proxy point at the true opening pose
    print(f"   CG (their proxy) at x={cg[0]:.1f}, y={cg[1]:.1f}; weight {W:.1f} N")
    # Posts must stand on the subplate outside the 300 x 250 rotator base (the base rises
    # with the per-tube Z), so the front pair sits at x = 170, y = +/-110 and the rear
    # ball on a tail behind the hinge. Latch at the rear ball.
    for fx, rx in ((170, 300), (170, 280), (180, 320)):
        # three balls A(fx,+110) B(fx,-110) C(rx,0); latch F down at C; weight W down at CG.
        # R_C = F - W*(fx - cg_x)/(rx - fx) >= 0 sets the minimum latch; check A, B stay loaded.
        k = (fx - cg[0]) / (rx - fx)
        F = W * k
        RA_plus_RB = W + F
        RA_minus_RB = W * cg[1] / 110.0
        RA, RB = (RA_plus_RB + RA_minus_RB) / 2, (RA_plus_RB - RA_minus_RB) / 2
        print(f"   front pair x={fx}, rear ball x={rx}: latch at rear ball >= {F:.1f} N (+ {5*177/(rx-fx):.1f} N for a 5 N tug 177 mm up); at that latch R_A={RA:.1f} N, R_B={RB:.1f} N")
