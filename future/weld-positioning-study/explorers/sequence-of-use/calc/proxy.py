"""Gun proxy from web/public/js/weld-position/pose.js + main.js, posed in the tube frame.

Tube frame (as pose.js): +Z up, tube bottom rim at z=0, weld dot at (61.8, 0, 146.05).
Bench is at z = 146.05 - 232 = -85.95 on the current rotator feet.
Hole angles are scene DIAL values (opening pose: roll 45, dial 30, vertical -15).
The proxy's housing sections, 60 deg pitch and 16 mm clearance are illustrative [Agent];
only 253 x 143 x 34 overall is manual data.
"""
import math
IN = 25.4
TUBE_OD = 5 * IN
WALL = 0.065 * IN
H = 6 * IN
RECESS = 0.25 * IN
R_IN = TUBE_OD / 2 - WALL          # 61.82
R_OUT = TUBE_OD / 2                # 63.5
CAP_TOP = H - RECESS               # 146.05
RIM = H                            # 152.4
BENCH_Z = CAP_TOP - 232.0          # -85.95
J = (R_IN, 0.0, CAP_TOP)
PITCH = math.radians(60)
CL = 16.0
GB = (0.0, -118.0, 237.0)
_al = math.hypot(GB[1], GB[2] + CL)
LRA = (0.0, GB[1] / _al, (GB[2] + CL) / _al)


HOLE_AXIS_OFFSET = 35.0   # main.js: posePoint(p, grip, holeDial - 35, vertical)


def pose(p, roll=45, hole=30, vert=-15):
    """Pose a gun-local point. `hole` is the scene's HOLE DIAL (Derek's opening pose: 30).
    posePoint itself receives dial - 35 (main.js). Wave 1 passed the dial straight in,
    which is dial 65; call pose(p, 45, 65, -15) to reproduce those labelled results."""
    hole = hole - HOLE_AXIS_OFFSET
    x, y, z = p
    s, c = math.sin(PITCH), math.cos(PITCH)
    along = z + CL
    py = -c * along + s * y
    pz = s * along + c * y
    r = math.radians(roll)
    ay = -c * LRA[2] + s * LRA[1]
    az = s * LRA[2] + c * LRA[1]
    d = ay * py + az * pz
    cr, sr = math.cos(r), math.sin(r)
    rx = x * cr + (ay * pz - az * py) * sr
    ry = py * cr + az * x * sr + ay * d * (1 - cr)
    rz = pz * cr - ay * x * sr + az * d * (1 - cr)
    h = math.radians(hole)
    ch, sh = math.cos(h), math.sin(h)
    hy = ry * ch + rz * sh
    hz = -ry * sh + rz * ch
    v = math.radians(vert)
    cv, sv = math.cos(v), math.sin(v)
    return (J[0] + rx * cv - hy * sv, J[1] + rx * sv + hy * cv, J[2] + hz)


def proxy_points(step=4.0):
    """Surface-ish point cloud of the proxy in its local frame (+Z nozzle->back, -Y grip side)."""
    pts = []
    tags = []
    # wire from tip to guide back (straight guide), tip at (0,0,-16)
    wt = (0.0, 0.0, -CL)
    wb = (0.0, -24.7, 87.1)
    n = 30
    for i in range(n + 1):
        t = i / n
        pts.append(tuple(wt[k] + t * (wb[k] - wt[k]) for k in range(3)))
        tags.append('wire')
    # nozzle + graduated tube: radius 2.2 at tip growing to ~8, then 12 at lens ring
    for z in [0, 5, 10, 15, 23, 40, 60, 80, 100, 110, 118]:
        rad = 2.2 if z == 0 else (5 if z <= 23 else (8 if z < 100 else 12))
        for a in range(0, 360, 30):
            pts.append((rad * math.cos(math.radians(a)), rad * math.sin(math.radians(a)), float(z)))
            tags.append('barrel')
    # housing box 34 x 34 x 135 centred z=185.5
    for x in (-17, 17):
        for y in (-17, 17):
            for z in range(118, 254, 15):
                pts.append((float(x), float(y), float(z)))
                tags.append('housing')
    # grip: from (0,-25,172) to (0,-111,232), 30 wide (x) x 28 thick
    g0 = (0, -25, 172); g1 = (0, -111, 232)
    for i in range(0, 11):
        t = i / 10
        c = [g0[k] + t * (g1[k] - g0[k]) for k in range(3)]
        for dx in (-15, 15):
            for dz in (-14, 14):
                pts.append((c[0] + dx, c[1], c[2] + dz))
                tags.append('grip')
    pts.append(GB); tags.append('gripbase')
    return pts, tags


def rot_about_axis(p, a, u, ang):
    """Rotate point p about axis through a with unit direction u by ang (rad)."""
    v = [p[i] - a[i] for i in range(3)]
    c, s = math.cos(ang), math.sin(ang)
    dot = sum(v[i] * u[i] for i in range(3))
    cross = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    return tuple(a[i] + v[i] * c + cross[i] * s + u[i] * dot * (1 - c) for i in range(3))


def collides_tube(q, margin=0.5):
    """True if q is inside tube wall/plate material or below rim outside the bore."""
    x, y, z = q
    r = math.hypot(x, y)
    if z < RIM + margin and z > -1:
        if r > R_IN - margin and r < R_OUT + margin:
            return True           # in the wall (incl. lip)
        if r <= R_IN and z < CAP_TOP - 0.2:
            return True           # inside the plate
    return False
