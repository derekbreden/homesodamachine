"""Where the gun sits in space for scene poses, so structure can be arranged around it.

Port of web/public/js/weld-position/pose.js (posePoint) plus the proxy housing
from main.js. Frame: tube axis = Z, tube centre at X=Y=0, Z=0 at the tube's
lower end (pose.js); the dot is at (R_in, 0, CAP_TOP). Outputs are expressed
relative to the dot and relative to the rim, and as heights above a bench
when the rotator stands on its current feet (dot 232.05 mm above bench).

The gun proxy (housing sections, 60 deg pitch, 16 mm clearance) is the
scene's illustrative proxy [Agent], not a scan. Treat outputs as +/- 10-20 mm.
"""
import math
import itertools
import numpy as np

IN = 25.4
TUBE_OD = 5 * IN
WALL = 0.065 * IN
R_IN = TUBE_OD / 2 - WALL
TUBE_H = 6 * IN
CAP_TOP = TUBE_H - 0.25 * IN
RIM = TUBE_H
JOINT = np.array([R_IN, 0.0, CAP_TOP])
PITCH = math.radians(60)
CLEAR = 16.0
GRIP_BASE = np.array([0.0, -118.0, 237.0])
_axlen = math.hypot(GRIP_BASE[1], GRIP_BASE[2] + CLEAR)
LOCAL_ROLL_AXIS = np.array([0.0, GRIP_BASE[1] / _axlen, (GRIP_BASE[2] + CLEAR) / _axlen])
HOLE_OFFSET = 35.0  # scene dial = hole parameter + 35
DOT_ABOVE_BENCH = 238.4 - 6.35  # current rotator feet


def pose_point(p, roll=0.0, hole_param=0.0, vertical=0.0):
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
    h = math.radians(hole_param)
    ch, sh = math.cos(h), math.sin(h)
    hy = ry * ch + rz * sh
    hz = -ry * sh + rz * ch
    v = math.radians(vertical)
    cv, sv = math.cos(v), math.sin(v)
    return JOINT + np.array([rx * cv - hy * sv, rx * sv + hy * cv, hz])


def box_corners(center, size, axis_from=None, axis_to=None):
    """Corners of the proxy boxes in local gun coordinates."""
    cx, cy, cz = center
    sx, sy, sz = size
    return [np.array([cx + dx * sx / 2, cy + dy * sy / 2, cz + dz * sz / 2])
            for dx, dy, dz in itertools.product((-1, 1), repeat=3)]


def grip_corners():
    a = np.array([0, -25, 172.0]); b = np.array([0, -111, 232.0])
    d = (b - a) / np.linalg.norm(b - a)
    n = np.cross(d, [1, 0, 0]); n /= np.linalg.norm(n)
    half_len = (np.linalg.norm(b - a) + 16) / 2
    mid = (a + b) / 2
    pts = []
    for sl, sw, sn in itertools.product((-1, 1), repeat=3):
        pts.append(mid + sl * half_len * d + sw * 15 * np.array([1, 0, 0]) + sn * 14 * n)
    return pts


FEATURES = {
    "nozzle tip": [np.array([0, 0, 0.0])],
    "nozzle Ø17 top (z=54)": [np.array([dx, dy, 54.0]) for dx, dy in ((8.5, 0), (-8.5, 0), (0, 8.5), (0, -8.5))],
    "lens section (z=100-118, r12)": [np.array([dx, dy, z]) for z in (100.0, 118.0) for dx, dy in ((12, 0), (-12, 0), (0, 12), (0, -12))],
    "housing": box_corners((0, 0, 185.5), (34, 34, 135)),
    "grip": grip_corners(),
    "grip base": [GRIP_BASE],
}


def describe(roll, dial, vertical):
    hp = dial - HOLE_OFFSET
    out = {}
    for name, pts in FEATURES.items():
        w = np.array([pose_point(p, roll, hp, vertical) for p in pts])
        out[name] = w
    return out


def rel(w):
    """Relative to the dot: dx (radial, + outward at dot side), dy (tangent), dz (up)."""
    return w - JOINT


def main():
    poses = [
        ("scene opening", 45, 30, -15),
        ("unrolled ref", 0, 35, 0),
        ("roll 0, dial 30, vert 0", 0, 30, 0),
        ("roll 60, dial 30, vert -15", 60, 30, -15),
        ("roll 45, dial 10, vert -15", 45, 10, -15),
        ("roll 45, dial 55, vert -15", 45, 55, -15),
        ("roll 45, dial 30, vert +15", 45, 30, 15),
        ("roll 45, dial 30, vert -40", 45, 30, -40),
    ]
    for label, roll, dial, vert in poses:
        d = describe(roll, dial, vert)
        print(f"\n== {label}: grip {roll}, hole dial {dial}, vertical {vert}")
        allpts = np.vstack(list(d.values()))
        r = rel(allpts)
        print(f"  gun envelope rel. dot: x {r[:,0].min():7.1f}..{r[:,0].max():6.1f}  "
              f"y {r[:,1].min():7.1f}..{r[:,1].max():6.1f}  z {r[:,2].min():6.1f}..{r[:,2].max():6.1f}")
        for name in ("nozzle tip", "housing", "grip", "grip base"):
            rr = rel(d[name])
            if len(rr) == 1:
                p = rr[0]
                print(f"  {name:12s} at x {p[0]:7.1f} y {p[1]:7.1f} z {p[2]:6.1f} (above rim {p[2]-6.35:6.1f}; above bench {p[2]+DOT_ABOVE_BENCH:6.1f})")
            else:
                print(f"  {name:12s} x {rr[:,0].min():7.1f}..{rr[:,0].max():6.1f} y {rr[:,1].min():7.1f}..{rr[:,1].max():6.1f} z {rr[:,2].min():6.1f}..{rr[:,2].max():6.1f}")
        gb = rel(d["grip base"])[0]
        L = np.linalg.norm(gb)
        elev = math.degrees(math.asin(gb[2] / L))
        plan = math.degrees(math.atan2(gb[1], gb[0]))
        print(f"  dot->grip base: {L:.1f} mm, elevation {elev:.1f} deg, plan heading {plan:.1f} deg from +X (tangent -Y = -90)")
        # lowest point of the gun that is outside the tube bore in plan (clash with rim/lip?)
        lowest_outside = None
        for name, w in d.items():
            for p in w:
                rad = math.hypot(p[0], p[1])
                if rad > R_IN - 1:
                    zz = p[2] - RIM
                    if lowest_outside is None or zz < lowest_outside[0]:
                        lowest_outside = (zz, name, rad)
        if lowest_outside:
            print(f"  lowest proxy point outside bore radius: {lowest_outside[0]:6.1f} mm vs rim ({lowest_outside[1]}, r={lowest_outside[2]:.0f})")

    # Tangent-slide equivalence: shifting the gun along Y by dy at fixed heading
    print("\n== Y shift at fixed heading  ==  vertical-axis rotation about the dot")
    for dy in (0.5, 1, 2, 5, 10, 16.2, 30):
        phi = math.degrees(math.atan2(dy, R_IN))
        dx = math.hypot(R_IN, dy) - R_IN
        print(f"  dy {dy:5.1f} mm -> heading vs local tangent {phi:5.2f} deg, radial correction {dx:5.2f} mm")


if __name__ == "__main__":
    main()
