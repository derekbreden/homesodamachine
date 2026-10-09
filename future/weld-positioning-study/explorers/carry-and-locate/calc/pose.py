"""Gun pose in the orientation scene's frame, ported from web/public/js/weld-position/pose.js.

Frame: +Z up, tube axis vertical through the origin, weld station on the +X side,
the dot at the inside corner on the +X radius, tangent along +/-Y.
Scene z=0 is the bottom of a 152.4 mm tube. BENCH_Z converts to height above the
bench on the current rotator feet (rim 238.4 mm above bench, repo).

Angles are the scene's dial readings (the hole dial is offset 35 deg from pose.js,
as main.js applies it). The gun is the scene's schematic proxy (253 x 143 x 34 mm from the manual's
drawing; section lengths, 60 deg pitch and 16 mm clearance are illustrative).
"""
import numpy as np

IN = 25.4
TUBE_OD = 5 * IN
WALL = 0.065 * IN
TUBE_H = 6 * IN
RECESS = 0.25 * IN
R_IN = TUBE_OD / 2 - WALL          # 61.849
CAP_TOP = TUBE_H - RECESS          # 146.05
RIM = TUBE_H                       # 152.4
JOINT = np.array([R_IN, 0.0, CAP_TOP])
BENCH_Z = 238.4 - TUBE_H           # scene z -> height above bench

PITCH = np.radians(60)
CLEARANCE = 16.0
GRIP_BASE = np.array([0.0, -118.0, 237.0])
_axis_len = np.hypot(GRIP_BASE[1], GRIP_BASE[2] + CLEARANCE)
LOCAL_ROLL_AXIS = np.array([0.0, GRIP_BASE[1] / _axis_len, (GRIP_BASE[2] + CLEARANCE) / _axis_len])

# Proxy landmarks in the gun's local frame (local +Z nozzle->back, -Y grip side).
LOCAL = {
    "dot": np.array([0.0, 0.0, -CLEARANCE]),
    "nozzle_tip": np.array([0.0, 0.0, 0.0]),
    "nozzle_back": np.array([0.0, 0.0, 23.0]),
    "grad_tube_back": np.array([0.0, 0.0, 54.0]),
    "barrel_back": np.array([0.0, 0.0, 100.0]),
    "lens_back": np.array([0.0, 0.0, 118.0]),
    "housing_front": np.array([0.0, 0.0, 118.0]),
    "housing_center": np.array([0.0, 0.0, 185.5]),
    "housing_back": np.array([0.0, 0.0, 253.0]),
    "housing_top_back": np.array([0.0, 17.0, 253.0]),
    "housing_top_front": np.array([0.0, 17.0, 118.0]),
    "grip_start": np.array([0.0, -25.0, 172.0]),
    "grip_end": np.array([0.0, -111.0, 232.0]),
    "grip_base": GRIP_BASE.copy(),
    "wire_brace": np.array([0.0, -12.0, 110.0]),
}


HOLE_DIAL_OFFSET = 35.0  # main.js: the hole dial reads 35 deg at pose.js holeRoll 0


def pose_point(p, roll=0.0, hole=0.0, vert=0.0):
    """roll, hole and vert are the scene's DIAL readings; hole is converted to pose.js holeRoll."""
    hole = hole - HOLE_DIAL_OFFSET
    x, y, z = p
    s, c = np.sin(PITCH), np.cos(PITCH)
    along = z + CLEARANCE
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


def pose_all(roll=45.0, hole=30.0, vert=-15.0):
    return {k: pose_point(v, roll, hole, vert) for k, v in LOCAL.items()}


def rot_matrix(roll=45.0, hole=30.0, vert=-15.0):
    """World rotation of local axes (columns = local x, y, z in world)."""
    o = pose_point(np.zeros(3), roll, hole, vert)
    cols = [pose_point(e, roll, hole, vert) - o for e in np.eye(3)]
    return np.column_stack(cols)


if __name__ == "__main__":
    np.set_printoptions(precision=1, suppress=True)
    for name, (r, h, v) in {"opening pose (45,30,-15)": (45, 30, -15),
                            "zero pose (0,0,0)": (0, 0, 0)}.items():
        P = pose_all(r, h, v)
        print(f"\n== {name}; scene coords, z also as height above bench ==")
        for k, p in P.items():
            rad = np.hypot(p[0], p[1])
            print(f"{k:18s} x={p[0]:7.1f} y={p[1]:7.1f} z={p[2]:7.1f}  bench_z={p[2]+BENCH_Z:6.1f}  r={rad:6.1f}")
        R = rot_matrix(r, h, v)
        barrel = R[:, 2]
        print("barrel dir (nozzle->back):", barrel, " elevation deg:",
              np.degrees(np.arcsin(barrel[2])).round(1),
              " plan az deg:", np.degrees(np.arctan2(barrel[1], barrel[0])).round(1))
        ga = P["grip_base"] - P["dot"]
        print("grip axis dir:", ga / np.linalg.norm(ga), "len", np.linalg.norm(ga).round(1),
              " elevation deg:", np.degrees(np.arcsin(ga[2] / np.linalg.norm(ga))).round(1))
        # where the barrel axis crosses the rim plane, and its radius there
        t = (RIM - P["dot"][2]) / barrel[2]
        cross = P["dot"] + t * barrel
        print("barrel axis crosses rim plane at", cross, "radius", np.hypot(cross[0], cross[1]).round(1),
              "(bore radius", round(R_IN, 1), ")")
        # the housing's lowest corner vs rim
