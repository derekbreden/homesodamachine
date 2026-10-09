"""Small calculations behind the borrowed-ecosystems arrangements.

Every mass, stiffness and friction value here is an assumption or an estimate
(labelled); the geometry comes from geometry.py (the orientation scene proxy).
Run: python3 calcs.py
"""
import numpy as np
import geometry as G

g0 = 9.81
POSE = (45, 30, -15)          # scene opening pose [Derek]; hole is the DIAL value (geometry.pose_point subtracts 35)
CG_LOCAL = G.CG_LOCAL         # gun CG proxy [assumption: in the housing, pulled toward the grip]


def axes(pose):
    roll, hole, vert = pose
    dot = G.JOINT
    gb = G.pose_point(G.GRIP_BASE, *pose)
    grip = (gb - dot) / np.linalg.norm(gb - dot)
    v = np.radians(vert)
    hole_ax = np.array([np.cos(v), np.sin(v), 0.0])   # radial line through dot, turned by the vertical axis
    vert_ax = np.array([0, 0, 1.0])
    return dot, {"grip": grip, "hole": hole_ax, "vertical": vert_ax}


def gravity_torques(pose, m):
    dot, ax = axes(pose)
    cg = G.pose_point(CG_LOCAL, *pose)
    r = (cg - dot) / 1000.0
    F = np.array([0, 0, -m * g0])
    tau = np.cross(r, F)
    return {k: float(np.dot(tau, a)) for k, a in ax.items()}, cg - dot


print("== 1. Gravity torque about each dot axis (gun+shell mass m) ==")
for pose in [(45, 30, -15), (35, 20, -15), (55, 40, -15), (45, 30, 0), (45, 45, -15)]:
    for m in (1.0, 2.0):
        t, off = gravity_torques(pose, m)
        print(f"pose {pose} m={m} kg: CG offset from dot {off.round(0)} mm; torque N*m " +
              ", ".join(f"{k} {v:+.2f}" for k, v in t.items()))

print("\n== 2. Following error of a rim/OD rider vs contact angle ==")
# Once-per-rev runout r(theta) = A cos(theta - phi). A rigid rider:
#  - symmetric pair at +/-a : estimate = mean -> error A|cos phi|(1-cos a)
#  - two contacts ahead at -a1, -a2, linear extrapolation to 0
for A, what in ((0.125, "radial, 0.25 TIR limit"), (0.15, "face, 0.30 TIR limit")):
    worst_sym = {a: A * (1 - np.cos(np.radians(a))) for a in (15, 30, 45, 60)}
    print(f"{what}: symmetric pair worst error " + ", ".join(f"+/-{a} deg {e:.3f} mm" for a, e in worst_sym.items()))
    for a1, a2 in ((20, 40), (30, 60), (45, 90)):
        errs = []
        for phi in np.radians(np.arange(0, 360, 1)):
            h = lambda th: A * np.cos(np.radians(th) - phi)
            est = h(-a1) + (h(-a1) - h(-a2)) * (a1 / (a2 - a1))
            errs.append(abs(est - h(0)))
        print(f"   ahead-only contacts at -{a1},-{a2} deg, linear extrapolation: worst {max(errs):.3f} mm")
    for a in (30, 60, 90):
        print(f"   single contact {a} deg away, no extrapolation: worst {2*A*np.sin(np.radians(a)/2):.3f} mm")

print("\n== 3. Arm-to-rider coupling (A1) ==")
# Gas-spring monitor arm: near-zero vertical rate, friction band (assumed +/-4 N at the head).
for k in (0.3, 0.5, 1.0, 2.0):
    runout = 0.15
    print(f"hanger spring k={k} N/mm: force change over +/-{runout} mm follow = {k*runout:.2f} N; "
          f"arm stick/slip band +/-4 N moves the hanger top at most {4/k:.1f} mm before the rider sees >4 N")
# balancer pendulum
for L, m in ((0.4, 2.0), (0.8, 2.0)):
    print(f"balancer cable {L} m, {m} kg hung: lateral pendulum stiffness {m*g0/L/1000:.3f} N/mm")

print("\n== 4. Rider preload budget (A1) ==")
# rolling resistance of steel ball-bearing wheels, coefficient ~0.002-0.005 [estimate]
for N in (5, 10, 20):
    print(f"preload {N} N on 3 wheels: rolling drag {N*0.005:.3f} N (mu_r 0.005); "
          f"table torque {N*0.005*0.0635:.5f} N*m at the rim radius")
# stuck wire: 0.030 in ER316L wire, yield ~ 400-600 MPa (cold drawn higher)
d = 0.030 * 25.4
A_w = np.pi * d**2 / 4
print(f"0.030 in wire area {A_w:.3f} mm^2 -> tensile load at 500 MPa {A_w*500:.0f} N, at 1000 MPa {A_w*1000:.0f} N")
print("   -> a stuck wire can pull ~0.2-0.5 kN before it breaks; the rider's tangential tether must yield far below that")

print("\n== 5. Belt-gantry stiffness (C) ==")
EA = 24000.0   # N, GT2-6 fibreglass estimate from ~600 N break at ~2.5% strain [estimate]
for L1, L2 in ((0.1, 0.5), (0.3, 0.3)):
    kb = EA / (L1 * 1000) + EA / (L2 * 1000)
    km = 22.0 / (0.0064**2) / 1000   # N/mm: NEMA17 ~22 N*m/rad near hold, 20T GT2 pulley r=6.4 mm [estimate]
    k = 1 / (1 / kb + 1 / km)
    print(f"carriage between belt spans {L1} m / {L2} m: belt {kb:.0f} N/mm, motor {km:.0f} N/mm, series {k:.0f} N/mm "
          f"-> 2 N wire/umbilical change moves the carriage {2/k*1000:.0f} um")
print("   POM V-wheel preload, printed hanger and X-beam torsion add compliance not modelled here")

print("\n== 6. Umbilical loop from the scene proxy (R = 350 mm while emitting) ==")
p0 = G.pose_point(G.GRIP_BASE, *POSE)
rake = G.pose_point(G.GRIP_BASE + G.GRIP_RAKE * 100, *POSE) - p0
rake /= np.linalg.norm(rake)
gax = (p0 - G.JOINT) / np.linalg.norm(p0 - G.JOINT)
print(f"grip base (cable exit) at bench z {p0[2]+G.BENCH_OFFSET:.0f} mm; grip axis elevation {np.degrees(np.arcsin(gax[2])):.1f} deg, "
      f"plan az {np.degrees(np.arctan2(gax[1], gax[0])):.0f} deg")
print(f"scene grip rake vs grip axis: {np.degrees(np.arccos(np.clip(np.dot(gax, rake), -1, 1))):.1f} deg "
      "(the scene bends the cable from the rake onto the grip axis within 70 mm)")
d_ = gax
elev = np.arcsin(d_[2])
R = 350
start = p0 + 70 * gax
print(f"from 70 mm out along the grip axis (bench z {start[2]+G.BENCH_OFFSET:.0f}): loop apex {R*(1-np.cos(elev)):.0f} mm higher "
      f"(bench z {start[2]+G.BENCH_OFFSET+R*(1-np.cos(elev)):.0f}); horizontal run to vertical {R*np.sin(elev)+R:.0f} mm")

print("\n== 7. Hole-axis rotator loads (B), rotator face 30 mm outboard of the tube OD ==")
for m in (1.0, 2.0):
    cg = G.pose_point(CG_LOCAL, *POSE)
    face_x = G.R_OUT + 30
    lever = (face_x - cg[0]) / 1000
    arm_m = 0.6   # kg of printed/aluminium hole-arm, CG ~40 mm inboard of the face [assumption]
    M = m * g0 * lever + arm_m * g0 * 0.04
    t, _ = gravity_torques(POSE, m)
    print(f"gun+shell {m} kg: bending moment on rotator bearing ~{M:.2f} N*m (lever {lever*1000:.0f} mm), "
          f"torque about its own axis {t['hole']:+.2f} N*m (plus arm imbalance)")
