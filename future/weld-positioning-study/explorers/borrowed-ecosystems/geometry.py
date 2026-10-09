"""Gun pose geometry for the borrowed-ecosystems arrangements.

Replicates web/public/js/weld-position/pose.js (the orientation scene) so the
arrangements can be placed around the same proxy. Tube frame: +Z up, tube axis
at x=y=0, tube bottom at z=0, dot at the inside corner on +X. Bench height is
added for the current rotator feet (rim 238.4 mm above the bench).

Everything about the gun beyond the manual's 253 x 143 x 34 mm envelope is the
scene's illustrative proxy (pitch 60 deg, 16 mm nozzle clearance, grip base at
local (0,-118,237)); nothing here is a measurement of the real gun.

Hole angles are the scene's DIAL values: main.js subtracts HOLE_AXIS_OFFSET
(35 deg) before calling posePoint, so the opening pose "hole 30" is a pose.js
rotation of -5 deg. (Wave 1 of this notebook passed 30 straight into the pose
math, i.e. dial 65; corrected in wave 2.)
"""
import numpy as np

IN = 25.4
TUBE_OD = 5 * IN
WALL = 0.065 * IN
TUBE_H = 6 * IN
RECESS = 0.25 * IN
R_IN = TUBE_OD / 2 - WALL          # 61.849
R_OUT = TUBE_OD / 2                # 63.5
CAP_TOP = TUBE_H - RECESS          # dot height in tube frame
JOINT = np.array([R_IN, 0.0, CAP_TOP])
RIM_ABOVE_BENCH = 238.4            # [Repo]
BENCH_OFFSET = RIM_ABOVE_BENCH - TUBE_H   # tube-frame z=0 is this far above the bench

PITCH = np.radians(60)
CLEAR = 16.0
GRIP_BASE = np.array([0, -118.0, 237.0])
_ax = np.array([0, GRIP_BASE[1], GRIP_BASE[2] + CLEAR])
LOCAL_ROLL_AXIS = _ax / np.linalg.norm(_ax)


HOLE_AXIS_OFFSET = 35.0   # main.js


def pose_point(p, roll=0.0, hole=HOLE_AXIS_OFFSET, vert=0.0):
    """roll, hole (scene DIAL value), vertical in degrees -> tube-frame point."""
    hole = hole - HOLE_AXIS_OFFSET
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


# Proxy landmarks in the gun's local frame (nozzle tip at origin, barrel +z,
# grip toward -y), taken from the scene's main.js proxy: barrel sections to
# z=118, housing box 34 x 34 x 135 centred at z=185.5, grip box from
# (y,z)=(-25,172) to (-111,232). The trigger point is an estimate.
LANDMARKS = {
    "nozzle tip": [0, 0, 0],
    "graduated tube end": [0, 0, 54],
    "lens drawer": [0, 0, 110],
    "body front (barrel meets body)": [0, 0, 118],
    "body back / top of barrel line": [0, 0, 253],
    "body top rear": [0, 17, 253],
    "wire brace mount": [0, -12, 110],
    "trigger (10), est.": [0, -45, 180],
    "grip base / QBH exit (9)": list(GRIP_BASE),
}
# Scene grip rake: the cable leaves the butt along this direction, then the
# scene bends it onto the grip axis within 70 mm.
GRIP_RAKE = np.array([0, -86.0, 60.0]) / np.hypot(86.0, 60.0)


CG_LOCAL = [0, -15, 185]


def barrel_dir(roll, hole, vert):
    a = pose_point([0, 0, 0], roll, hole, vert)
    b = pose_point([0, 0, 100], roll, hole, vert)
    d = b - a
    return d / np.linalg.norm(d)


def report(roll, hole, vert):
    print(f"\n=== pose grip {roll}, hole {hole}, vertical {vert} ===")
    print(f"dot (tube frame) {JOINT.round(2)}; above bench {JOINT[2] + BENCH_OFFSET:.1f}")
    pts = {}
    for k, v in LANDMARKS.items():
        p = pose_point(v, roll, hole, vert)
        pts[k] = p
        r = np.hypot(p[0], p[1])
        print(f"{k:34s} xyz {p.round(1)}  r_from_axis {r:6.1f}  z_above_dot {p[2]-JOINT[2]:6.1f}  bench_z {p[2]+BENCH_OFFSET:6.1f}")
    d = barrel_dir(roll, hole, vert)
    elev = np.degrees(np.arcsin(d[2]))
    az = np.degrees(np.arctan2(d[1], d[0]))
    print(f"barrel direction (nozzle->body) {d.round(3)}  elevation {elev:.1f} deg  plan azimuth {az:.1f} deg")
    # beam direction is -d from nozzle to dot
    # rim clearance along the barrel: sample local z from 0 to 135 at the barrel
    # axis and report the radial margin to the bore where the point is below the rim.
    worst = None
    for zl in np.linspace(0, 135, 136):
        p = pose_point([0, 0, zl], roll, hole, vert)
        if p[2] <= TUBE_H + 0.0:
            margin = R_IN - np.hypot(p[0], p[1])
            if worst is None or margin < worst[0]:
                worst = (margin, zl, p[2] - JOINT[2])
    if worst:
        print(f"barrel axis below rim: min radial margin to bore {worst[0]:.1f} mm at local z {worst[1]:.0f} (z above dot {worst[2]:.1f})")
    # CG proxy: assume the gun CG sits in the housing, pulled a little toward
    # the grip, local (0,-15,185) -- an estimate, not a measurement.
    cg = pose_point(CG_LOCAL, roll, hole, vert)
    print(f"CG proxy (local {CG_LOCAL}) xyz {cg.round(1)}; offset from dot {(cg-JOINT).round(1)}")
    return pts


if __name__ == "__main__":
    for pose in [(0, 35, 0), (45, 35, 0), (45, 30, 0), (45, 30, -15)]:
        report(*pose)
