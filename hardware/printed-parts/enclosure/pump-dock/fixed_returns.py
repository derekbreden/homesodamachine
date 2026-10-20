"""Shared port and flow-path datums for the permanent pump plumbing.

Coordinates are enclosure millimetres: +Y points inward and +Z points up.
The supplied pump wall and purchased valve ports locate every part. This
module contains geometry data only; the wet solids and dry fixtures consume
the same data without importing an assembly generator.
"""

import math


TUBE_OD = 6.35
TUBE_ID = 4.30
SEAL_BORE_D = 6.10
CUFF_OD = 11.72
CUFF_WALL = (CUFF_OD - SEAL_BORE_D) / 2
OCCUPIED_CUFF_OD = math.sqrt(CUFF_OD ** 2 + TUBE_OD ** 2 - SEAL_BORE_D ** 2)
FLOW_OD = CUFF_OD
SEAL_LAND = 6.0
ENTRY_LEAD = .5
SOCKET_DEPTH = SEAL_LAND + ENTRY_LEAD
FLOW_REACH = 1.0
MOUTH_TO_CURVE = SOCKET_DEPTH + FLOW_REACH

UPPER_ARC_R = 12.2
UPPER_MOUTH_Z = 22.0

# Factory links are cut against the mounted stop span. This nominal target
# does not include the complete manufacturing, thermal or loaded tolerance
# budget; the total permitted play bounds the remaining seal engagement.
LINK_NOMINAL_AXIAL_PLAY = .15
LINK_MAX_TOTAL_AXIAL_PLAY = .5
LINK_MIN_SEAL_ENGAGEMENT = SEAL_LAND - LINK_MAX_TOTAL_AXIAL_PLAY


def _add(a, b):
    return tuple(a[i] + b[i] for i in range(3))


def _scale(a, k):
    return tuple(v * k for v in a)


def _line(start, direction, length):
    return {"kind": "line", "start_mm": tuple(start),
            "end_mm": _add(start, _scale(direction, length)),
            "start_tangent": tuple(direction), "end_tangent": tuple(direction),
            "length_mm": float(length)}


def _arc(start, horizontal, radius, theta, sweep):
    """A circle in the horizontal/+Z plane; angles are measured from horizontal."""
    sign = math.copysign(1., sweep)

    def point(fraction):
        angle = theta + fraction * sweep
        return _add(start, _add(
            _scale(horizontal, sign * radius * (math.sin(angle) - math.sin(theta))),
            (0., 0., sign * radius * (math.cos(theta) - math.cos(angle)))))

    def tangent(angle):
        return _add(_scale(horizontal, math.cos(angle)), (0., 0., math.sin(angle)))

    return {"kind": "arc", "start_mm": tuple(start), "midpoint_mm": point(.5),
            "end_mm": point(1.), "radius_mm": float(radius),
            "sweep_degrees": math.degrees(sweep),
            "start_tangent": tangent(theta), "end_tangent": tangent(theta + sweep),
            "length_mm": radius * abs(sweep)}


def _fork_arc(root, radius, angle, across):
    """Turn from +Y toward an X/Z direction, without changing the inlet axis."""
    def point(fraction):
        a = angle * fraction
        return _add(root, _add((0., radius * math.sin(a), 0.),
                              _scale(across, radius * (1. - math.cos(a)))))

    return {"kind": "arc", "start_mm": tuple(root), "midpoint_mm": point(.5),
            "end_mm": point(1.), "radius_mm": float(radius),
            "sweep_degrees": math.degrees(angle), "start_tangent": (0., 1., 0.),
            "end_tangent": _add((0., math.cos(angle), 0.),
                                  _scale(across, math.sin(angle))),
            "length_mm": radius * abs(angle)}


# Scanned exterior release-face station; the scan does not establish internal stops.
ELBOW_FACE = 20.56239
ELBOW_INSERTION_NOMINAL = 15.7  # layout estimate only; factory marking sets actual cuts
VALVE_INSERTION_NOMINAL = 12.0
STUB_FACE_GAP = 1.0
TUBE_BEND_R = 14.0  # existing spool observation, _routing.STOCKS
ELBOW_ROOT_HALF = 7.15
ELBOW_BEARING_STATION = 11.5
ELBOW_WALL = 3.0


def _unit(v):
    return _scale(v, 1.0 / math.sqrt(sum(c*c for c in v)))


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def elbow_layout(wall_fore_y, x, z, return_port, bed_z):
    """A supported scanned PP0308E, captured straight stub and formed LLDPE run.

    The inner elbows lean 25 degrees to lower the run below the electrical
    terminals. Outer elbows yaw toward their valve and clear the condenser.
    The stub illustrates nominal elbow insertion. The formed run ends at the
    known release faces; its insertion allowances are stock estimates only.
    """
    target = tuple(return_port['point'])
    inner = abs(x) < 50.
    tilt = math.radians(25. if inner else 0.)
    corner = (x, wall_fore_y + (17.385 if inner else 23.585),
              bed_z + ELBOW_WALL - ELBOW_BEARING_STATION*math.cos(tilt) + .7
              if inner else bed_z - 4.65)
    up = (0., math.sin(tilt), math.cos(tilt))
    aft = (0., math.cos(tilt), -math.sin(tilt)) if inner else _unit((target[0]-x, target[1]-corner[1], 0.))
    up_face = _add(corner, _scale(up, ELBOW_FACE))
    mouth = _add(up_face, _scale(up, STUB_FACE_GAP))
    stop = _add(mouth, _scale(up, SOCKET_DEPTH))
    direction = _scale(up, -1.)
    radius = 4.0 if inner else 2.5
    turn = math.acos(direction[1])
    across = _unit((direction[0], 0., direction[2]))
    rel = _add((0., radius*math.sin(turn), 0.), _scale(across, radius*(1.-math.cos(turn))))
    tail = (stop[2] - z - rel[2]) / direction[2]
    root = (x, stop[1] - tail*direction[1] - rel[1], z)
    arc = _fork_arc(root, radius, turn, across)
    lower = (arc, _line(arc['end_mm'], direction, tail + SOCKET_DEPTH))
    out_face = _add(corner, _scale(aft, ELBOW_FACE))
    path = []
    if inner:
        first_turn = _arc(out_face, (0.,1.,0.), TUBE_BEND_R, -tilt, tilt)
        path.append(first_turn)
        level = first_turn['end_mm']
        horizontal = (0.,1.,0.)
    else:
        level, horizontal = out_face, aft
    q = (target[0]-TUBE_BEND_R*horizontal[0], target[1]-TUBE_BEND_R*horizontal[1], level[2])
    path.append(_line(level, horizontal, math.dist(level,q)))
    path.append(_arc(q, horizontal, TUBE_BEND_R, 0., math.pi/2))
    lead = target[2] - path[-1]['end_mm'][2]
    path.append(_line(path[-1]['end_mm'], (0.,0.,1.), lead))
    stub_start = _add(up_face, _scale(up, -ELBOW_INSERTION_NOMINAL))
    stub = _line(stub_start, up, ELBOW_INSERTION_NOMINAL + STUB_FACE_GAP + SOCKET_DEPTH - LINK_NOMINAL_AXIAL_PLAY)
    return {'corner':corner, 'up_axis':up, 'aft_axis':aft, 'x_axis':_cross(aft,up),
            'up_face':up_face, 'aft_face':out_face, 'tilt_degrees':math.degrees(tilt),
            'lower_flow_segments':lower, 'lower':{'point':mouth, 'axis':direction, 'tube_stop':stop},
            'target':dict(return_port), 'stub':(stub,), 'formed_tube':tuple(path),
            'stub_cut_nominal_mm':stub['length_mm'],
            'formed_cut_nominal_mm':sum(s['length_mm'] for s in path)+ELBOW_INSERTION_NOMINAL+VALVE_INSERTION_NOMINAL,
            'formed_exposed_length_mm':sum(s['length_mm'] for s in path),
            'valve_straight_exposed_mm':lead,
            'bearing_z':corner[2]+ELBOW_BEARING_STATION*math.cos(tilt)}


def junction_ports(wall_fore_y, x, z, upper_port, return_port, bed_z=None):
    """The wall inlet and upper outlet, with a lower land over its fixed elbow."""
    if bed_z is None:
        bed_z = z - 25.924
    elbow = elbow_layout(wall_fore_y,x,z,return_port,bed_z)
    upper_target = tuple(upper_port['point'])
    upper_root = (x,upper_target[1]-UPPER_ARC_R,z)
    arc = _fork_arc(upper_root,UPPER_ARC_R,math.pi/2,(0.,0.,1.))
    upper = (arc,_line(arc['end_mm'],(0.,0.,1.),UPPER_MOUTH_Z-UPPER_ARC_R))
    mouth=upper[-1]['end_mm']
    return {'wall_fore_y':float(wall_fore_y), 'pump_axis':(float(x),float(z)),
            'upper_root_local_y':upper_root[1]-wall_fore_y,
            'upper_flow_segments':upper, 'lower_flow_segments':elbow['lower_flow_segments'],
            'upper':{'point':mouth,'axis':(0.,0.,1.),'tube_stop':_add(mouth,(0.,0.,-SOCKET_DEPTH))},
            'lower':elbow['lower'], 'upper_target':dict(upper_port),'return_target':dict(return_port),
            'lower_clock_about_y_degrees':0., 'seal_land_mm':SEAL_LAND,'socket_depth_mm':SOCKET_DEPTH}


def station(wall_fore_y,x,z,upper_port,return_port,bed_z=None):
    if bed_z is None:bed_z=z-25.924
    elbow=elbow_layout(wall_fore_y,x,z,return_port,bed_z)
    junction=junction_ports(wall_fore_y,x,z,upper_port,return_port,bed_z)
    start=junction['upper']['point']
    return {'junction':junction,'elbow':elbow,
            'upper_tube':_line(start,(0.,0.,1.),upper_port['point'][2]-start[2])}


def layouts(plate):
    return {str(x):station(plate['fore_y'],x,z,plate['upper_ports'][str(x)],
                          plate['return_ports'][str(x)],plate['fixture_print_bed_z'])
            for x,z in plate['holes']}
