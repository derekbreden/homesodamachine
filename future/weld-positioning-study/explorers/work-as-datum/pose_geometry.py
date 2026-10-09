"""Where the gun sits relative to the tube, lip and endcap at a given pose.

Replicates web/public/js/weld-position/pose.js (posePoint) so the explorer's
arrangements can be checked against the scene's gun proxy. The proxy's 60 deg
pitch, 16 mm nozzle clearance and grip-base location are illustrative [Agent];
the tube, lip and cap numbers are [Repo].

The hole argument is the scene's dial reading; main.js subtracts 35 before
calling posePoint (wave-1 versions of this file omitted that offset and put the
gun 35 deg too steep; corrected in wave 2).

Frame: +Z up, tube axis = Z, the dot at the inside corner on the +X radius.
Origin here is the tube axis at the endcap's outer face (z = 0 at the corner),
so the rim is at z = +6.35.

Run:  python3 pose_geometry.py
"""
import math

IN = 25.4
R_OUT = 5 * IN / 2              # 63.50 tube OD radius
R_IN = R_OUT - 0.065 * IN       # 61.849 bore radius = corner radius
RECESS = 0.25 * IN              # lip height above the cap face
PORT_OFF = 0.75 * IN            # port centres at +-19.05 on one diameter
PORT_D = 0.438 * IN

PITCH = math.radians(60)
CLEARANCE = 16.0
GRIP_BASE = (0.0, -118.0, 237.0)   # proxy cable exit, gun-local frame
WIRE_TIP = (0.0, 0.0, -CLEARANCE)  # the dot, gun-local frame
NOZZLE_TIP = (0.0, 0.0, 0.0)
BARREL_BACK = (0.0, 0.0, 150.0)    # rough: back of the barrel/front of body
BODY_BACK = (0.0, 0.0, 237.0)      # rough: back of the body (253 overall incl. nozzle)
WIRE_GUIDE_BACK = (0.0, -24.7, 87.1)

_axis_len = math.hypot(GRIP_BASE[1], GRIP_BASE[2] + CLEARANCE)
LOCAL_ROLL_AXIS = (0.0, GRIP_BASE[1] / _axis_len, (GRIP_BASE[2] + CLEARANCE) / _axis_len)


HOLE_DIAL_OFFSET = 35.0  # main.js: holeRotation = holeDegrees (dial) - 35


def pose_point(p, roll=0.0, hole=0.0, vert=0.0):
    """roll, hole, vert are the scene's DIAL readings (hole dial 30 = opening pose)."""
    hole = hole - HOLE_DIAL_OFFSET
    x, y, z = p
    s, c = math.sin(PITCH), math.cos(PITCH)
    along = z + CLEARANCE
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
    h = math.radians(hole)
    ch, sh = math.cos(h), math.sin(h)
    hy = ry * ch + rz * sh
    hz = -ry * sh + rz * ch
    v = math.radians(vert)
    cv, sv = math.cos(v), math.sin(v)
    # relative to the dot at (R_IN, 0, 0)
    return (R_IN + rx * cv - hy * sv, rx * sv + hy * cv, hz)


def describe(name, p):
    x, y, z = p
    rad = math.hypot(x, y)
    return f"{name:14s} x={x:8.1f} y={y:8.1f} z={z:7.1f}  r_from_axis={rad:6.1f}  above_rim={z-RECESS:7.1f}"


def beam_dir(roll, hole, vert):
    a = pose_point(NOZZLE_TIP, roll, hole, vert)
    b = pose_point(WIRE_TIP, roll, hole, vert)
    d = [b[i] - a[i] for i in range(3)]
    n = math.sqrt(sum(v * v for v in d))
    return [v / n for v in d]


def report(roll, hole, vert):
    print(f"\n== pose grip={roll} hole={hole} vertical={vert}")
    for name, p in [("dot", WIRE_TIP), ("nozzle tip", NOZZLE_TIP),
                    ("barrel@80", (0, 0, 80.0)), ("barrel back", BARREL_BACK),
                    ("body back", BODY_BACK), ("grip base", GRIP_BASE),
                    ("wire guide bk", WIRE_GUIDE_BACK)]:
        print(describe(name, pose_point(p, roll, hole, vert)))
    d = beam_dir(roll, hole, vert)
    elev = math.degrees(math.asin(-d[2]))
    # angle of the beam from the tube axis, and its radial/tangential lean
    print(f"beam dir (nozzle->dot) = ({d[0]:.3f},{d[1]:.3f},{d[2]:.3f}); "
          f"elevation below horizontal {elev:.1f} deg; "
          f"radial component {d[0]:+.3f} (+ = toward wall)")
    # where does the nozzle-to-dot line cross the rim plane?
    a = pose_point(NOZZLE_TIP, roll, hole, vert)
    t = (RECESS - 0) / (-d[2])  # distance back from the dot along the beam to reach rim height
    q = [R_IN - d[0] * t, 0 - d[1] * t, RECESS]
    print(f"beam crosses rim plane at r={math.hypot(q[0], q[1]):.1f} (bore {R_IN:.2f}); "
          f"{t:.1f} mm back from the dot")
    return d


if __name__ == "__main__":
    print(f"bore radius {R_IN:.3f}, OD radius {R_OUT:.3f}, lip {RECESS:.2f}")
    for pose in [(0, 35, 0), (45, 30, -15), (45, 10, -15), (45, 55, -15), (60, 30, -15), (45, 30, 15)]:
        report(*pose)

    # How far is the dot from the plate centre, and from the port edges?
    print("\nport edge nearest the corner (on the port diameter):",
          f"{PORT_OFF + PORT_D / 2:.2f} mm from centre; corner at {R_IN:.2f}; gap {R_IN - PORT_OFF - PORT_D / 2:.2f}")

    # Tangent line leaving the dot: how far into the wall, and where does it clear the OD?
    for d in (2, 5, 10, 14.4, 20, 30):
        excess = math.hypot(R_IN, d) - R_IN
        print(f"tangent line {d:5.1f} mm from the dot lies {excess:5.2f} mm outside the bore")
