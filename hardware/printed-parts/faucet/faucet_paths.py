"""Consumer faucet tube layout, in millimetres.

The arc station is measured on the water centreline after the internal
70-degree joint datum. X is lateral; N is outward from the water tube.
All transitions have zero first and second offset derivatives at their ends.
This module deliberately has no CAD imports so qualification can read it.
"""

import math

WATER_Y = 8.875
WATER_OD = 9.525
FLAVOR_OD = 6.35
DRAIN_OD = 4.0
DRAIN_ID = 2.5
LOWER_FLAVOR_X = 5.45
LOWER_BUNDLE_X = 2.275
LOWER_Y = 18.925
LOWER_DRAIN_Y = 18.525
LOWER_RIBBON_Y = 21.4875
LOWER_START_Z = 40.0
LOWER_END_Z = 67.5
LOWER_FLAVOR_FLARE = 0.10
OUTLET_Y = -133.99672200476698
OUTLET_Z = 180.38874339162197
TOTAL_ANGLE = math.radians(140.0)
TIP_LENGTH = 25.0
WATER_RADIUS = (WATER_Y - OUTLET_Y - TIP_LENGTH * math.sin(TOTAL_ANGLE)) / (1 - math.cos(TOTAL_ANGLE))
ARC_START_Z = OUTLET_Z - WATER_RADIUS * math.sin(TOTAL_ANGLE) - TIP_LENGTH * math.cos(TOTAL_ANGLE)
JOINT_ANGLE = math.radians(70.0)
SHELL_CENTER_N = 4.027512922
SHELL_RADIUS = 13.5
CAVITY_RADIUS = 11.5
TIGHT_DRAIN_N = (WATER_OD + DRAIN_OD) / 2
_rf = (WATER_OD + FLAVOR_OD) / 2
_rd = (DRAIN_OD + FLAVOR_OD) / 2
TIGHT_FLAVOR_N = (_rf**2 - _rd**2 + TIGHT_DRAIN_N**2) / (2*TIGHT_DRAIN_N)
TIGHT_FLAVOR_X = math.sqrt(_rf**2 - TIGHT_FLAVOR_N**2)
FACE_FLAVOR_X = FLAVOR_OD / 2
FACE_FLAVOR_N = math.sqrt(_rf**2 - FACE_FLAVOR_X**2)
SEAL_WEB = 0.8
SEAL_DRAIN_N = TIGHT_DRAIN_N + SEAL_WEB
_seal_rf = _rf + SEAL_WEB
_seal_rd = _rd + SEAL_WEB
SEAL_FLAVOR_N = (_seal_rf**2 - _seal_rd**2 + SEAL_DRAIN_N**2) / (2*SEAL_DRAIN_N)
SEAL_FLAVOR_X = math.sqrt(_seal_rf**2 - SEAL_FLAVOR_N**2)
TIGHT_RIBBON_N = 9.75
SEAL_RIBBON_N = 11.0125
FACE_RIBBON_N = 11.55
SPREAD_END_S = 14.0
UPSTREAM_GLAND_S = 30.0
DOWNSTREAM_GLAND_S = 59.3
GLAND_LENGTH = 7.3
GLAND_BODY_MID_Z = 4.1
GLAND_MID_SHIFT_S = GLAND_BODY_MID_Z*WATER_RADIUS/(WATER_RADIUS+SHELL_CENTER_N)
_floor_radius = WATER_RADIUS+SHELL_CENTER_N-CAVITY_RADIUS
WET_START_S = UPSTREAM_GLAND_S+GLAND_MID_SHIFT_S+WATER_RADIUS*math.asin((GLAND_LENGTH-GLAND_BODY_MID_Z)/_floor_radius)
WET_END_S = DOWNSTREAM_GLAND_S+GLAND_MID_SHIFT_S+WATER_RADIUS*math.asin(-GLAND_BODY_MID_Z/_floor_radius)
# The plain drain mouth and warning hole keep their absolute position on
# the bend. They are independent of the assembly joint and require no seals.
DRAIN_END_ANGLE = math.radians(80.68709001137978)
DRAIN_CUT_S = (DRAIN_END_ANGLE - JOINT_ANGLE) * WATER_RADIUS
CONVERGE_START_S = DRAIN_CUT_S + 3.0
CONVERGE_LENGTH = 24.0
RIBBON_CONVERGE_LENGTH = 8.0
PORT_START_S = WET_START_S
PORT_LENGTH_S = 22.0
PORT_WIDTH = 12.0
PORT_CORNER_R = 2.0
DRIP_POCKET_ENTRY_S = 30.0
DRIP_POCKET_EXIT_S = 59.3
DRIP_GUIDE_WALL_THICKNESS = 2.0
DRIP_HOLE_DIAMETER = 4.0
DRIP_FLOOR_ENTRY_S = (DRIP_POCKET_ENTRY_S
    + WATER_RADIUS*math.asin(DRIP_GUIDE_WALL_THICKNESS/_floor_radius))
DRIP_HOLE_ANGLE = math.radians(75.72139663878282)
DRIP_HOLE_S = (DRIP_HOLE_ANGLE - JOINT_ANGLE) * WATER_RADIUS
DRIP_END_CLEARANCE_MM = 3.0


def ease(t):
    t = max(0.0, min(1.0, t))
    return t*t*t*(10 + t*(-15 + 6*t))


def lower_positions(z):
    u = ease((z - LOWER_START_Z)/(LOWER_END_Z-LOWER_START_Z))
    # Symmetric local separation preserves the tangent pack at both ends.
    flare = LOWER_FLAVOR_FLARE*4*u*(1-u)
    return (LOWER_FLAVOR_X + (TIGHT_FLAVOR_X-LOWER_FLAVOR_X)*u + flare,
            LOWER_Y-WATER_Y + (TIGHT_FLAVOR_N-(LOWER_Y-WATER_Y))*u,
            LOWER_DRAIN_Y-WATER_Y + (TIGHT_DRAIN_N-(LOWER_DRAIN_Y-WATER_Y))*u)


def lower_bundle_x(z):
    """Shared lateral return from the purchased mounting channel to the neck."""
    return LOWER_BUNDLE_X*(1-ease((z-LOWER_START_Z)/(LOWER_END_Z-LOWER_START_Z)))


def lower_ribbon_y(z):
    u = ease((z-LOWER_START_Z)/(LOWER_END_Z-LOWER_START_Z))
    return LOWER_RIBBON_Y+(WATER_Y+TIGHT_RIBBON_N-LOWER_RIBBON_Y)*u


def lower_point(z, kind, sign=1):
    x, f, d = lower_positions(z)
    y = WATER_Y+(f if kind == "flavor" else d) if kind != "ribbon" else lower_ribbon_y(z)
    return (lower_bundle_x(z)+(sign*x if kind == "flavor" else 0.0), y, z)


def positions(s):
    """F lateral/normal, D normal, cable normal and maximum cable width."""
    # Four tubes share the upstream opening. Beyond the drain's open end,
    # the two flavors return smoothly to the proven tangent dispense pair.
    u = ease((s-CONVERGE_START_S)/CONVERGE_LENGTH)
    a0 = math.atan2(TIGHT_FLAVOR_X, TIGHT_FLAVOR_N)
    a1 = math.atan2(FACE_FLAVOR_X, FACE_FLAVOR_N)
    angle = a0 + (a1-a0)*u
    cable_u = ease((s-CONVERGE_START_S)/RIBBON_CONVERGE_LENGTH)
    return (_rf*math.sin(angle), _rf*math.cos(angle), TIGHT_DRAIN_N,
            TIGHT_RIBBON_N+(FACE_RIBBON_N-TIGHT_RIBBON_N)*cable_u, 4.1)


def arc_point(angle, x=0.0, n=0.0):
    return (x, WATER_Y-WATER_RADIUS+(WATER_RADIUS+n)*math.cos(angle),
            ARC_START_Z+(WATER_RADIUS+n)*math.sin(angle))


def station_point(s, x=0.0, n=0.0):
    return arc_point(JOINT_ANGLE+s/WATER_RADIUS, x, n)


def station_plane(s, *, center_n=0.0):
    """CAD-free origin, lateral vector and forward tangent at a station."""
    a = JOINT_ANGLE+s/WATER_RADIUS
    return station_point(s, n=center_n), (1.0, 0.0, 0.0), (0.0, -math.sin(a), math.cos(a))


def tube_arc_point(s, kind, sign=1):
    x, f, d, ribbon, _ = positions(s)
    return station_point(s, sign*x if kind == "flavor" else 0.0,
                         f if kind == "flavor" else d if kind == "drain" else ribbon)


def port_half_width(s):
    q = s-PORT_START_S
    if q < 0 or q > PORT_LENGTH_S:
        return 0.0
    r = PORT_CORNER_R
    d = min(q, PORT_LENGTH_S-q)
    return PORT_WIDTH/2 if d >= r else PORT_WIDTH/2-r+math.sqrt(max(0, r*r-(d-r)**2))


def path_wire(kind, bottom_z=-6.2, sign=1, *, end_s=None):
    """Circular/spline CAD path with analytic straight and constant arc runs."""
    import cadquery as cq
    edges = []

    def line(a, b):
        if math.dist(a, b) > 1e-7:
            edges.append(cq.Edge.makeLine(cq.Vector(*a), cq.Vector(*b)))

    def spline(fn, a, b):
        count = max(16, math.ceil((b-a)/0.4))
        edges.append(cq.Edge.makeSpline([cq.Vector(*fn(a+(b-a)*i/count)) for i in range(count+1)], tol=1e-7))

    def lower(z):
        return lower_point(z, kind, sign)

    def constant_arc(a, b, x, n):
        if b-a > 1e-9:
            edges.append(cq.Edge.makeThreePointArc(cq.Vector(*arc_point(a,x,n)),
                cq.Vector(*arc_point((a+b)/2,x,n)), cq.Vector(*arc_point(b,x,n))))

    start = lower(LOWER_START_Z)
    line((start[0], start[1], bottom_z), start)
    spline(lower, LOWER_START_Z, LOWER_END_Z)
    _, ty, _ = lower(LOWER_END_Z)
    nx = sign*TIGHT_FLAVOR_X if kind == "flavor" else 0.0
    nn = TIGHT_FLAVOR_N if kind == "flavor" else TIGHT_DRAIN_N if kind == "drain" else TIGHT_RIBBON_N
    line(lower(LOWER_END_Z), (nx, ty, ARC_START_Z))
    constant_arc(0, JOINT_ANGLE, nx, nn)
    end_s = DRAIN_CUT_S if kind == "drain" and end_s is None else end_s
    if end_s is not None:
        if end_s <= CONVERGE_START_S:
            constant_arc(JOINT_ANGLE, JOINT_ANGLE+end_s/WATER_RADIUS, nx, nn)
        else:
            constant_arc(JOINT_ANGLE, JOINT_ANGLE+CONVERGE_START_S/WATER_RADIUS, nx, nn)
            spline(lambda s: tube_arc_point(s,kind,sign), CONVERGE_START_S, end_s)
    else:
        constant_arc(JOINT_ANGLE, JOINT_ANGLE+CONVERGE_START_S/WATER_RADIUS, nx, nn)
        spline(lambda s: tube_arc_point(s,kind,sign), CONVERGE_START_S, CONVERGE_START_S+CONVERGE_LENGTH)
        p = positions(CONVERGE_START_S+CONVERGE_LENGTH)
        nx, nn = (sign*p[0],p[1]) if kind == "flavor" else (0.0,p[3])
        constant_arc(JOINT_ANGLE+(CONVERGE_START_S+CONVERGE_LENGTH)/WATER_RADIUS, TOTAL_ANGLE, nx, nn)
        start = arc_point(TOTAL_ANGLE,nx,nn)
        line(start, (start[0],start[1]-TIP_LENGTH*math.sin(TOTAL_ANGLE),start[2]+TIP_LENGTH*math.cos(TOTAL_ANGLE)))
    return cq.Wire.assembleEdges(edges)
