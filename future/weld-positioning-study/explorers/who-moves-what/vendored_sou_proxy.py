"""VENDORED COPY (2026-09-28, wave 3) of the parts of sequence-of-use's
explorers/sequence-of-use/calc/proxy.py that this directory uses: the proxy point
cloud (their tracing of the orientation-scene gun, including the straight wire from
the dot to the wire-guide back), the axis rotation helper and the tube collision test.
Copied so this directory does not import their live file, which changed mid-wave.
Posing is NOT copied: this directory poses points with geometry.pose_dial (exact
posePoint port + main.js hole-dial offset). All credit for the point cloud and
collision test to sequence-of-use.
"""
import math
IN = 25.4
TUBE_OD = 5 * IN
WALL = 0.065 * IN
H = 6 * IN
RECESS = 0.25 * IN
R_IN = TUBE_OD / 2 - WALL
R_OUT = TUBE_OD / 2
CAP_TOP = H - RECESS
RIM = H
CL = 16.0
GB = (0.0, -118.0, 237.0)
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
