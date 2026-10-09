"""VENDORED COPY (2026-09-28, wave 4) of one-knob-one-parameter's explorers/one-knob-one-parameter/geometry.py, unmodified except the import name.
All credit to one-knob-one-parameter; copied so this directory does not import their live files."""
"""Pose geometry for the one-knob-one-parameter explorer.

Re-implements web/public/js/weld-position/pose.js (the scene's rotation math)
so arrangements can be laid out around the scene's gun proxy.  Scene frame:
millimetres, +Z up, tube axis on Z, tube bottom at z=0, the dot at the inside
corner on the +X radius.  Bench height: the rotator rim is 238.4 mm above the
bench and 152.4 mm in scene z, so bench z = -86.0.

The gun proxy (housing sections, 60 deg pitch, 16 mm clearance, grip) is the
scene's ILLUSTRATIVE proxy [Agent], not a scan.  Every number printed here
inherits that.

Run:  python3 geometry.py
"""
import math
import numpy as np

IN = 25.4
TUBE_OD = 5 * IN
WALL = 0.065 * IN
TUBE_H = 6 * IN
CAP_RECESS = 0.25 * IN
R_IN = TUBE_OD / 2 - WALL           # 61.849
R_OUT = TUBE_OD / 2                 # 63.5
CAP_TOP = TUBE_H - CAP_RECESS       # 146.05
JOINT = np.array([R_IN, 0.0, CAP_TOP])
BENCH_Z = TUBE_H - 238.4            # -86.0

PITCH = math.radians(60)
CLEAR = 16.0
GRIP_BASE = np.array([0.0, -118.0, 237.0])
_len = math.hypot(GRIP_BASE[1], GRIP_BASE[2] + CLEAR)
LOCAL_ROLL_AXIS = np.array([0.0, GRIP_BASE[1] / _len, (GRIP_BASE[2] + CLEAR) / _len])
HOLE_AXIS_OFFSET = 35.0             # dial reads 35 at zero hole rotation


def pose_point(p, roll=0.0, hole_dial=HOLE_AXIS_OFFSET, vertical=0.0):
    """Port of posePoint(); hole_dial is the scene's displayed dial value."""
    x, y, z = p
    s, c = math.sin(PITCH), math.cos(PITCH)
    along = z + CLEAR
    py = -c * along + s * y
    pz = s * along + c * y
    r = math.radians(roll)
    ay = -c * LOCAL_ROLL_AXIS[2] + s * LOCAL_ROLL_AXIS[1]
    az = s * LOCAL_ROLL_AXIS[2] + c * LOCAL_ROLL_AXIS[1]
    dot = ay * py + az * pz
    cr, sr = math.cos(r), math.sin(r)
    rx = x * cr + (ay * pz - az * py) * sr
    ry = py * cr + az * x * sr + ay * dot * (1 - cr)
    rz = pz * cr - ay * x * sr + az * dot * (1 - cr)
    h = math.radians(hole_dial - HOLE_AXIS_OFFSET)
    ch, sh = math.cos(h), math.sin(h)
    hy = ry * ch + rz * sh
    hz = -ry * sh + rz * ch
    v = math.radians(vertical)
    cv, sv = math.cos(v), math.sin(v)
    return JOINT + np.array([rx * cv - hy * sv, rx * sv + hy * cv, hz])


# Proxy sample points in the gun's local frame (from main.js): nozzle cone,
# graduated tube, barrel, lens collar, housing box, grip box.
def proxy_points():
    pts = {}
    for name, z0, z1, r in [("nozzle", 0, 23, 5.0), ("tube", 23, 54, 8.5),
                            ("barrel", 54, 100, 5.5), ("collar", 100, 118, 12.0)]:
        ring = []
        for zz in np.linspace(z0, z1, 6):
            for a in np.linspace(0, 2 * math.pi, 16, endpoint=False):
                ring.append([r * math.cos(a), r * math.sin(a), zz])
        pts[name] = np.array(ring)
    box = []
    for xx in (-17, 17):
        for yy in (-17, 17):
            for zz in np.linspace(118, 253, 8):
                box.append([xx, yy, zz])
    pts["housing"] = np.array(box)
    g0, g1 = np.array([0, -25, 172.0]), np.array([0, -111, 232.0])
    grip = []
    for t in np.linspace(0, 1, 8):
        c = g0 + t * (g1 - g0)
        for dx in (-15, 15):
            for dz in (-14, 14):
                grip.append(c + [dx, 0, dz])
    pts["grip"] = np.array(grip)
    return pts


def world(points, roll, hole, vert):
    return np.array([pose_point(p, roll, hole, vert) for p in points])


def unit(v):
    return v / np.linalg.norm(v)


def describe(roll, hole, vert, label):
    tip = pose_point([0, 0, 0], roll, hole, vert)
    back = pose_point([0, 0, 253], roll, hole, vert)
    grip = pose_point(GRIP_BASE, roll, hole, vert)
    beam = unit(JOINT - tip)                 # travels from nozzle to dot
    # Working angles, measured at the dot in the local seam frame:
    # n_cap = +Z (cap face normal), n_wall = -X (bore normal, facing inward),
    # seam tangent = +/-Y.
    to_gun = -beam
    elev_from_cap = math.degrees(math.asin(to_gun[2]))
    inc_cap = math.degrees(math.acos(to_gun[2]))          # from cap normal
    inc_wall = math.degrees(math.acos(-to_gun[0]))        # from wall normal (-X)
    # work angle: projection of to_gun into the XZ cross-section plane,
    # measured up from the cap face toward the wall (90 = straight down)
    work = math.degrees(math.atan2(to_gun[2], -to_gun[0]))
    travel = math.degrees(math.asin(to_gun[1]))           # + means gun leans to +Y
    ga = unit(grip - JOINT)
    grip_elev = math.degrees(math.asin(ga[2]))
    grip_plan = math.degrees(math.atan2(ga[1], ga[0]))
    print(f"--- {label}: roll {roll}, hole dial {hole}, vertical {vert}")
    print(f"  nozzle tip       {np.round(tip, 1)}  (bench height {tip[2]-BENCH_Z:.0f})")
    print(f"  gun back (253)   {np.round(back, 1)}  (bench height {back[2]-BENCH_Z:.0f})")
    print(f"  grip base        {np.round(grip, 1)}  (bench height {grip[2]-BENCH_Z:.0f}); dist from dot {np.linalg.norm(grip-JOINT):.1f}")
    print(f"  grip axis: elevation {grip_elev:.1f} deg, plan bearing {grip_plan:.1f} deg (from +X)")
    print(f"  beam elevation above cap {elev_from_cap:.1f}; from cap normal {inc_cap:.1f}; from wall normal {inc_wall:.1f}")
    print(f"  work angle (XZ, from cap toward wall) {work:.1f}; travel angle (toward +Y) {travel:.1f}")
    pts = proxy_points()
    allw = np.vstack([world(v, roll, hole, vert) for v in pts.values()])
    lo, hi = allw.min(axis=0), allw.max(axis=0)
    print(f"  gun envelope x[{lo[0]:.0f},{hi[0]:.0f}] y[{lo[1]:.0f},{hi[1]:.0f}] z[{lo[2]:.0f},{hi[2]:.0f}]  top above bench {hi[2]-BENCH_Z:.0f}")
    # clearance of nozzle/tube samples to the tube wall region above the cap
    near = np.vstack([world(pts[k], roll, hole, vert) for k in ("nozzle", "tube", "barrel")])
    r = np.hypot(near[:, 0], near[:, 1])
    below_rim = near[:, 2] < TUBE_H + 0.5
    inside = r < R_IN
    worst = None
    if below_rim.any():
        gap = R_IN - r[below_rim]
        worst = gap.min()
    print(f"  min radial gap of nozzle/barrel samples below rim to bore: {worst if worst is None else round(worst,1)} mm")
    return dict(tip=tip, grip=grip, beam=beam, back=back, envelope=(lo, hi))


if __name__ == "__main__":
    print(f"R_IN {R_IN:.3f}  CAP_TOP {CAP_TOP:.2f}  joint above bench {CAP_TOP-BENCH_Z:.1f}")
    describe(0, 35, 0, "reference (unrolled)")
    describe(45, 30, -15, "opening pose / Derek's hand pose")
    for r in (30, 45, 60):
        describe(r, 30, -15, f"roll sweep {r}")
    for h in (20, 30, 45):
        describe(45, h, -15, f"hole sweep {h}")
    for v in (-30, -15, 0):
        describe(45, 30, v, f"vertical sweep {v}")

    # Lever arms: dot displacement for small errors at supports
    print("\nLever arms (dot moves = distance * angle):")
    for d in (100, 200, 279, 300, 400):
        print(f"  {d} mm: 0.1 deg -> {d*math.radians(0.1):.3f} mm ; 0.05 mm there -> {math.degrees(0.05/d):.4f} deg")


# ---------------------------------------------------------------------------
# Weld-language angles vs the scene's knobs.
# work   : beam direction projected into the XZ cross-section, measured up from
#          the cap face toward the wall (90 = straight down onto the cap).
# travel : beam lean along the seam (asin of the gun-ward beam's Y component).
# wobble : angle between the wobble line and the seam tangent, ASSUMING the
#          wobble sweeps along the gun's local X (the scene's illustrative
#          2 mm sweep does).  90 = sweeping straight across the corner.
def weld_angles(roll, hole, vert):
    tip = pose_point([0, 0, 0], roll, hole, vert)
    to_gun = unit(tip - JOINT)
    work = math.degrees(math.atan2(to_gun[2], -to_gun[0]))
    travel = math.degrees(math.asin(to_gun[1]))
    wob = unit(pose_point([1, 0, -CLEAR], roll, hole, vert) - pose_point([0, 0, -CLEAR], roll, hole, vert))
    # remove the beam-direction component, then angle to the seam tangent (Y)
    wob_perp = unit(wob - np.dot(wob, to_gun) * to_gun)
    wobble = math.degrees(math.acos(min(1.0, abs(wob_perp[1]))))
    return np.array([work, travel, wobble])


def jacobian(roll=45, hole=30, vert=-15, h=0.5):
    base = np.array([roll, hole, vert], dtype=float)
    J = np.zeros((3, 3))
    for i in range(3):
        d = np.zeros(3); d[i] = h
        J[:, i] = (weld_angles(*(base + d)) - weld_angles(*(base - d))) / (2 * h)
    return J


def report_jacobian():
    J = jacobian()
    print("\nAt the opening pose (roll 45, hole 30, vertical -15):")
    print("  weld angles:", np.round(weld_angles(45, 30, -15), 2), "(work, travel, wobble-crossing)")
    print("  d(work, travel, wobble)/d(roll, hole, vertical), deg per deg:")
    for name, row in zip(("work", "travel", "wobble"), J):
        print(f"    {name:7s}", np.round(row, 3))
    Jinv = np.linalg.inv(J)
    print("  knob turns (roll, hole, vertical) for +1 deg of one weld angle, others held:")
    for name, col in zip(("work", "travel", "wobble"), Jinv.T):
        print(f"    +1 {name:7s} ->", np.round(col, 3))


if __name__ == "__main__":
    report_jacobian()
