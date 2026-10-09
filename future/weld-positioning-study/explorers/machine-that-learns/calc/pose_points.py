"""Where the gun's key points sit in the tube frame for a few scene poses.

Port of web/public/js/weld-position/pose.js (posePoint) with main.js's
35-degree hole-axis dial offset. Frame: mm, +Z up, tube axis vertical,
dot at the inside corner on +X, tangent along +/-Y. Bench is 232 mm below
the dot on the current rotator feet (shared-context).

The gun proxy (253 x 143 x 34, 60 deg pitch, 16 mm clearance, grip geometry)
is the scene's illustrative proxy, not a measurement.
"""
import math

IN = 25.4
TUBE_OD = 5 * IN
WALL = 0.065 * IN
TUBE_H = 6 * IN
RECESS = 0.25 * IN
R_IN = TUBE_OD / 2 - WALL
CAP_TOP = TUBE_H - RECESS
JOINT = (R_IN, 0.0, CAP_TOP)
PITCH = math.radians(60)
CLEAR = 16.0
GRIP_BASE = (0.0, -118.0, 237.0)
L = math.hypot(GRIP_BASE[1], GRIP_BASE[2] + CLEAR)
LOCAL_AXIS = (0.0, GRIP_BASE[1] / L, (GRIP_BASE[2] + CLEAR) / L)
HOLE_OFFSET = 35
BENCH_BELOW_DOT = 232.0


def pose_point(p, roll=0.0, hole_dial=0.0, vertical=0.0):
    hole = hole_dial - HOLE_OFFSET
    x, y, z = p
    s, c = math.sin(PITCH), math.cos(PITCH)
    along = z + CLEAR
    py = -c * along + s * y
    pz = s * along + c * y
    r = math.radians(roll)
    ay = -c * LOCAL_AXIS[2] + s * LOCAL_AXIS[1]
    az = s * LOCAL_AXIS[2] + c * LOCAL_AXIS[1]
    d = ay * py + az * pz
    cr, sr = math.cos(r), math.sin(r)
    rx = x * cr + (ay * pz - az * py) * sr
    ry = py * cr + az * x * sr + ay * d * (1 - cr)
    rz = pz * cr - ay * x * sr + az * d * (1 - cr)
    h = math.radians(hole)
    ch, sh = math.cos(h), math.sin(h)
    hy = ry * ch + rz * sh
    hz = -ry * sh + rz * ch
    v = math.radians(vertical)
    cv, sv = math.cos(v), math.sin(v)
    return (JOINT[0] + rx * cv - hy * sv, JOINT[1] + rx * sv + hy * cv, JOINT[2] + hz)


def rel(p):
    return tuple(round(a - b, 1) for a, b in zip(p, JOINT))


def unit(v):
    n = math.sqrt(sum(a * a for a in v))
    return tuple(a / n for a in v)


POINTS = {
    "nozzle tip": (0, 0, 0),
    "nozzle back / graduated tube": (0, 0, 54),
    "body front (lens drawer)": (0, 0, 118),
    "body back top": (0, 17, 253),
    "grip front top": (0, -25, 172),
    "grip base (cable exit)": GRIP_BASE,
    "wire guide back": (0, -24.7, 87.1),
}

if __name__ == "__main__":
    for name, (roll, hole, vert) in {
        "opening pose (45, 30, -15)": (45, 30, -15),
        "unrolled (0, 35, 0)": (0, 35, 0),
        "roll 30": (30, 30, -15),
        "roll 60": (60, 30, -15),
        "hole 50": (45, 50, -15),
    }.items():
        print(f"\n== {name}   [dx, dy, dz] from dot, mm; r = plan radius from tube axis")
        for pname, p in POINTS.items():
            q = pose_point(p, roll, hole, vert)
            r = math.hypot(q[0], q[1])
            print(f"  {pname:32s} {str(rel(q)):28s} r={r:6.1f}  above bench={q[2]-JOINT[2]+BENCH_BELOW_DOT:6.1f}")
        beam_back = unit(tuple(a - b for a, b in zip(pose_point((0, 0, 0), roll, hole, vert), JOINT)))
        el = math.degrees(math.asin(beam_back[2]))
        plan = math.degrees(math.atan2(beam_back[1], beam_back[0]))
        # work angle: beam direction projected into the XZ plane (perpendicular to the joint tangent)
        work = math.degrees(math.atan2(beam_back[2], -beam_back[0]))
        travel = math.degrees(math.asin(beam_back[1]))
        gb = pose_point(GRIP_BASE, roll, hole, vert)
        axis = unit(tuple(a - b for a, b in zip(gb, JOINT)))
        print(f"  beam (dot->nozzle) unit {tuple(round(a,3) for a in beam_back)}; elevation {el:.1f} deg; plan az {plan:.1f} deg")
        print(f"  work angle from cap face (in XZ) {work:.1f} deg (90 = straight down); travel lean along Y {travel:.1f} deg")
        print(f"  grip-axis unit {tuple(round(a,3) for a in axis)}; elevation {math.degrees(math.asin(axis[2])):.1f} deg; dot->grip {math.dist(gb, JOINT):.1f} mm")
