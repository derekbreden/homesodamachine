"""Geometry around the X1 Pro and the recessed corner, for the who-moves-what notebook.

Replicates web/public/js/weld-position/pose.js exactly (pose frame, 60 deg proxy
pitch, 16 mm proxy clearance) and adds a capsule model of the gun traced from the
manual's section 3.4 drawing (0.195 mm/px on the 253 mm dimension line).
Every gun dimension here other than 253 x 143 x 34 is a drawing-scaled estimate.

World frame: +Z up, tube axis on Z, dot on +X at the inside corner.
Heights above the bench add 86.0 mm (joint 232.05 mm above bench, repo).

Pose tuples in this study are the SCENE'S DIALS (grip, hole dial, vertical).
main.js passes the hole dial to posePoint as dial - 35 (HOLE_AXIS_OFFSET), so
Derek's opening pose 45 / 30 / -15 is posePoint(p, 45, -5, -15). Wave-1 numbers
first published here passed 30 straight in, i.e. hole dial 65; those remain valid
for dial 65 and are printed below, labelled.

Run: tools/cad-venv/bin/python <this file>
"""
import numpy as np

IN = 25.4
TUBE_OD = 5 * IN
WALL = 0.065 * IN
R_IN = TUBE_OD / 2 - WALL          # 61.849
R_OUT = TUBE_OD / 2                # 63.5
CAP_TOP = 6 * IN - 0.25 * IN       # 146.05 in scene frame
RIM = 6 * IN                       # 152.4
JOINT = np.array([R_IN, 0.0, CAP_TOP])
BENCH = CAP_TOP - 232.05           # scene z of the bench top
PITCH = np.radians(60)
CLEAR = 16.0
GRIP_BASE = np.array([0, -118.0, 237.0])
_ax = np.hypot(GRIP_BASE[1], GRIP_BASE[2] + CLEAR)
LOCAL_ROLL_AXIS = np.array([0, GRIP_BASE[1] / _ax, (GRIP_BASE[2] + CLEAR) / _ax])


HOLE_DIAL_OFFSET = 35.0  # main.js HOLE_AXIS_OFFSET


def pose_point(p, roll=0.0, hole=0.0, vert=0.0):
    """Exact port of posePoint() in pose.js (hole = posePoint argument, not the dial)."""
    x, y, z = p
    s, c = np.sin(PITCH), np.cos(PITCH)
    along = z + CLEAR
    py = -c * along + s * y
    pz = s * along + c * y
    r = np.radians(roll)
    ay = -c * LOCAL_ROLL_AXIS[2] + s * LOCAL_ROLL_AXIS[1]
    az = s * LOCAL_ROLL_AXIS[2] + c * LOCAL_ROLL_AXIS[1]
    dot = ay * py + az * pz
    cr, sr = np.cos(r), np.sin(r)
    rx = x * cr + (ay * pz - az * py) * sr
    ry = py * cr + az * x * sr + ay * dot * (1 - cr)
    rz = pz * cr - ay * x * sr + az * dot * (1 - cr)
    h = np.radians(hole)
    ch, sh = np.cos(h), np.sin(h)
    hy = ry * ch + rz * sh
    hz = -ry * sh + rz * ch
    v = np.radians(vert)
    cv, sv = np.cos(v), np.sin(v)
    return np.array([JOINT[0] + rx * cv - hy * sv, JOINT[1] + rx * sv + hy * cv, JOINT[2] + hz])


# Gun capsules in the pose.js local frame: (y, z) centreline ends and radius.
# Local z runs from the nozzle tip (0) back along the barrel; -y is the grip side.
# Drawing-scaled estimates; the body is really a 34 x ~34 mm box.
CAPSULES = {
    "nozzle":      ((0, 0), (0, 23), 5.5),
    "grad_tube":   ((0, 23), (0, 55), 8.3),
    "thin_tube":   ((0, 55), (0, 96), 6.4),
    "coupling":    ((0, 96), (0, 115), 11.5),
    "body":        ((0, 115), (0, 247), 17.0),
    "grip":        ((-17, 193), (-114, 238), 19.0),
}
FEATURES = {
    "dot": (0, -16),
    "nozzle_tip": (0, 0),
    "body_front": (0, 125),
    "body_back": (0, 247),
    "wire_bracket": (-27, 120),
    "light_switch": (-56, 172),
    "grip_base_QBH": (-118, 237),
}
FIBER_DIR_LOCAL = np.array([0, -0.866, 0.5])  # grip rakes 30 deg; QBH exits along it


def pose_dial(p, grip, hole_dial, vert):
    """Scene dials -> posePoint, as main.js does."""
    return pose_point(p, grip, hole_dial - HOLE_DIAL_OFFSET, vert)


def world(yz, pose):
    """pose = scene dials (grip, hole dial, vertical)."""
    return pose_dial((0.0, yz[0], yz[1]), *pose)


def dist_to_tube(p):
    """Distance from point p to the tube wall + end plate solid (axisymmetric)."""
    rho = np.hypot(p[0], p[1])
    z = p[2]
    # wall: rho in [R_IN, R_OUT], z <= RIM
    dr = max(R_IN - rho, 0, rho - R_OUT)
    dz = max(z - RIM, 0)
    d_wall = np.hypot(dr, dz)
    # plate: rho <= R_IN, z <= CAP_TOP
    dr2 = max(rho - R_IN, 0)
    dz2 = max(z - CAP_TOP, 0)
    d_plate = np.hypot(dr2, dz2)
    return min(d_wall, d_plate)


def clearance(pose, skip=("nozzle",)):
    worst = (1e9, None)
    for name, (a, b, rad) in CAPSULES.items():
        if name in skip:
            continue
        for t in np.linspace(0, 1, 25):
            yz = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
            d = dist_to_tube(world(yz, pose)) - rad
            if d < worst[0]:
                worst = (d, name)
    return worst


def fmt(p):
    return f"({p[0]:7.1f}, {p[1]:7.1f}, {p[2]:6.1f})  bench+{p[2]-BENCH:6.1f}  rho {np.hypot(p[0], p[1]):6.1f}  above-rim {p[2]-RIM:6.1f}"


if __name__ == "__main__":
    OPEN = (45, 30, -15)          # Derek's opening pose, dials
    OLD = (45, 65, -15)           # what wave 1 first computed (posePoint hole 30)
    for label, pose in (("opening pose, dials 45 / 30 / -15 (posePoint hole -5)", OPEN),
                        ("dial 65 (wave-1 first numbers; posePoint hole 30)", OLD)):
        print(f"\n== {label}")
        for k, v in FEATURES.items():
            print(f"  {k:14s} {fmt(world(v, pose))}")
        c, where = clearance(pose)
        print(f"  min gun-to-tube clearance (nozzle excluded): {c:6.1f} mm at {where}")
        nz = min(dist_to_tube(world((0, t), pose)) - 5.5 for t in np.linspace(0, 23, 10))
        print(f"  nozzle clearance: {nz:6.1f} mm")

    # Axes in world at the opening pose
    dot = world(FEATURES["dot"], OPEN)
    gb = world(FEATURES["grip_base_QBH"], OPEN)
    g = (gb - dot) / np.linalg.norm(gb - dot)
    print("\n== axes at the opening pose")
    print(f"  grip axis dir {np.round(g, 3)}  elevation {np.degrees(np.arcsin(g[2])):.1f} deg  length dot->QBH {np.linalg.norm(gb-dot):.1f}")
    v = np.radians(OPEN[2])
    hdir = np.array([np.cos(v), np.sin(v), 0])
    print(f"  hole axis dir {np.round(hdir, 3)}")
    # fiber exit direction in world
    f_tip = world((FEATURES['grip_base_QBH'][0] + 100 * FIBER_DIR_LOCAL[1], FEATURES['grip_base_QBH'][1] + 100 * FIBER_DIR_LOCAL[2]), OPEN)
    fdir = (f_tip - gb) / 100
    print(f"  fiber exit dir {np.round(fdir, 3)}  angle to grip axis {np.degrees(np.arccos(np.dot(fdir, g))):.1f} deg")

    print("\n== candidate pin points on the grip axis (distance s from the dot)")
    for s in (60, 100, 140, 180, 279.0, 330):
        p = dot + s * g
        # nearest gun surface
        best = 1e9
        for name, (a, b, rad) in CAPSULES.items():
            for t in np.linspace(0, 1, 60):
                yz = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
                best = min(best, np.linalg.norm(world(yz, OPEN) - p) - rad)
        print(f"  s={s:5.0f}: {fmt(p)}  to gun surface {best:6.1f}")

    print("\n== feasible orientations: min clearance (mm) of gun body to tube, nozzle excluded")
    print("   rows hole DIAL deg, cols grip-axis roll deg, yaw -15")
    rolls = list(range(0, 91, 15))
    print("hole\\roll " + "".join(f"{r:7d}" for r in rolls))
    for h in range(0, 71, 10):
        print(f"{h:9d} " + "".join(f"{clearance((r, h, -15))[0]:7.1f}" for r in rolls))
    print("   yaw sweep at roll 45, hole dial 30")
    for yv in (-45, -30, -15, 0, 15, 30, 45):
        c, w = clearance((45, 30, yv))
        print(f"   yaw {yv:4d}: {c:6.1f} ({w})")

    print("\n== yaw by sliding along the tangent (tube symmetry)")
    print("   Y slide mm -> relative yaw deg, radial correction mm")
    for Y in (1, 2, 5, 10, 16.6, 25, 33.5):
        th = np.degrees(np.arctan2(Y, R_IN))
        dx = np.hypot(R_IN, Y) - R_IN
        print(f"   {Y:5.1f} -> {th:6.2f} deg, move inward {dx:5.2f} mm")

    print("\n== dot error from a physical axis that misses the dot by e, turned by a")
    for e in (0.1, 0.5, 1.0, 2.0):
        print("   e=%.1f mm: " % e + ", ".join(f"{a} deg->{2*e*np.sin(np.radians(a)/2):.3f} mm" for a in (1, 5, 15, 30)))

    print("\n== a follower offset by phi from the dot sees eccentricity/ovality at a different angle")
    for phi in (10, 20, 30, 45):
        ph = np.radians(phi)
        print(f"   phi {phi:2d} deg (arc {R_IN*ph:5.1f} mm): worst error = {2*np.sin(ph/2):.2f} x eccentricity, {2*np.sin(ph):.2f} x ovality amplitude")

    print("\n== tilting the existing rotator: tip margin")
    # 2.01 kg vessel; assume turntable+nest 0.8 kg, CG of vessel 76 mm above race plane + ~40 mm
    for tilt in (5, 10, 20, 30, 45):
        t = np.radians(tilt)
        m = 2.01 + 0.8
        zcg = 0.116  # m above the race plane, estimate
        rr = 0.0825
        # turntable lifts on one side when the CG line leaves the race circle
        ok = zcg * np.tan(t) < rr
        print(f"   tilt {tilt:2d} deg: CG shift at race plane {1000*zcg*np.tan(t):5.1f} mm vs race radius 82.5 mm -> {'stays seated by gravity' if ok else 'lifts onto the spool catch'}")
