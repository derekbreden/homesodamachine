"""Wave 4 numbers for the split-mount station (ideas/split-mount-station.md).

Plan frame: tube axis at origin, dot at (R_in, 0), plate face z = 0.
Carrier rollers on a line through the dot at 30 deg off the radius (toward +Y,
away from the gun): P1 = dot + 34 mm, P2 = dot + 90 mm along that line
(centres 5 mm above the face). Paddle: hub pin at the centre, room foot P3 on
a motorised pad at (-70, -250), fence at P3. Section 4 shows why the line is
not the radius itself (nozzle on one side, the rotating nipples on the other). Gun proxy = scene proxy at the true opening pose [Agent].
Masses and CoM are [assumed]. Run: python3 split_mount.py
"""
import math
import numpy as np
import geom
import axis_clearance as ac

R = geom.R_IN
PSI = math.radians(30.0)
LINE = np.array([-math.cos(PSI), math.sin(PSI)])
DOT = np.array([R, 0.0])
P1, P2, P3 = DOT + 34 * LINE, DOT + 90 * LINE, np.array([-70.0, -250.0])
ROLLER_Z = 5.0


def rot_x(v, deg):
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    return np.array([v[0], c * v[1] - s * v[2], s * v[1] + c * v[2]])


print("== 1. hole-axis tilt by lifting P3 ==")
lever = abs(float((P3 - DOT)[0] * LINE[1] - (P3 - DOT)[1] * LINE[0]))
print(f"  P1 {P1.round(1)}, P2 {P2.round(1)}; P3 is {lever:.0f} mm from the P1-P2 line")
for deg in (1, 5, 10):
    print(f"  {deg:2d} deg -> P3 lift {lever*math.tan(math.radians(deg)):5.1f} mm")
print("  Tr8x2 lead screw, 200 full steps x 16 microsteps: "
      f"{2/3200*1000:.2f} um per microstep -> {math.degrees(math.atan(2/3200/lever))*3600:.2f} arcsec")

print("\n== 2. what a tilt does to the dot, by where the dot sits relative to the roller line ==")
cases = {
    "rollers ride the Y slide (dot on the line, 5 mm below roller centres)": (0.0, 0.0),
    "gun-only Y slide, plan angle 5 deg (dot 5.4 mm off the line)": (5.4, 0.0),
    "gun-only Y slide, plan angle 15 deg (dot 16.2 mm off the line)": (16.2, 0.0),
    "rollers ride Y; dot set 0.5 mm up the wall (Z trim)": (0.0, 0.5),
}
for name, (dy, dz) in cases.items():
    v = np.array([0.0, dy, dz - ROLLER_Z])   # dot relative to the roller-centre line
    for deg in (5, 10):
        d = rot_x(v, deg) - v
        print(f"  {name}: tilt {deg:2d} deg moves the dot {d[1]:+.2f} mm along the tangent, {d[2]:+.2f} mm in height")

print("\n== 3. contact loads with motors on the paddle [assumed masses] ==")
def c2(a, b):
    return float(a[0] * b[1] - a[1] * b[0])
def edge(a, b, p):
    d = b - a
    return abs(c2(d, p - a)) / np.linalg.norm(d)
tri = np.array([P1, P2, P3])
A = np.column_stack([tri, np.ones(3)])
for W, CG in ((32.0, np.array([-25.0, -140.0])), (32.0, np.array([-45.0, -160.0])), (35.0, np.array([-10.0, -120.0]))):
    w = np.linalg.solve(A.T, np.array([CG[0], CG[1], 1.0])) * W
    for hold in (0.0, 30.0):
        wh = np.linalg.solve(A.T, np.array([0.0, 0.0, 1.0])) * hold   # hold-down acts at the hub (0,0)
        loads = w + wh
        print(f"  paddle {W:.0f} N, CoM {tuple(int(v) for v in CG)}, hold-down {hold:.0f} N: "
              f"P1 {loads[0]:5.1f}  P2 {loads[1]:5.1f}  P3 {loads[2]:5.1f} N")
print("  hold-down: one K&J RC62 (N42, 19.05 x 9.52 x 3.17) is listed at 8.51 lb (38 N) pull on thick steel at contact;"
      " a 430 stainless disc and any gap reduce it [Obs + Est]")

print("\n== 4. P1 roller holder (r 7, 25 mm tall) vs the gun; rollers ride with the gun, so X/Y slides don't change this ==")
def holder_clear(w, P, rad=7.0, ztop=25.0):
    z = w[:, 2] - ac.PLATE_Z
    rr = np.hypot(w[:, 0] - P[0], w[:, 1] - P[1])
    ins = (z >= 0) & (z <= ztop)
    d1 = (rr[ins] - rad).min() if ins.any() else 1e9
    top = z > ztop
    d2 = np.sqrt(np.maximum(rr[top] - rad, 0) ** 2 + (z[top] - ztop) ** 2).min() if top.any() else 1e9
    return min(d1, d2)
for pose in ((45, 30, -15), (45, 30, 0), (45, 30, -30), (60, 30, -15), (45, 40, -15), (30, 20, -15)):
    w = ac.world(*pose)
    print(f"  pose {pose}: P1 holder {holder_clear(w, P1):5.1f} mm, P2 holder {holder_clear(w, P2):5.1f} mm from the nearest gun surface")
print(f"  for comparison, a holder on the radius at (36, 0): {holder_clear(ac.world(45, 30, -15), (36.0, 0.0)):.1f} mm at the opening pose, "
      f"{holder_clear(ac.world(45, 30, -30), (36.0, 0.0)):.1f} at vertical -30")

print("\n== 5. how far the Y and X slides can move the rollers (they ride with the gun) ==")
def ok(P):
    r = math.hypot(*P)
    return (r - 6.5 >= 28.0) and (r + 6.5 <= 57.0)   # outside the nipples' sweep (r 27.3), inside the fillet toe
ys = [y for y in np.arange(-20, 20.5, 0.5) if ok(P1 + [0, y]) and ok(P2 + [0, y])]
xs = [x for x in np.arange(-6, 6.5, 0.5) if ok(P1 + [x, 0]) and ok(P2 + [x, 0])]
print(f"  Y slide range with both rollers on clean plate: {min(ys):+.1f} .. {max(ys):+.1f} mm "
      f"= plan angle {math.degrees(math.atan(min(ys)/R)):+.1f} .. {math.degrees(math.atan(max(ys)/R)):+.1f} deg around the built-in nominal")
print(f"  X slide range: {min(xs):+.1f} .. {max(xs):+.1f} mm")
print("  dot height = %.2f*P1 %+.2f*P2" % (90 / 56, 1 - 90 / 56))
