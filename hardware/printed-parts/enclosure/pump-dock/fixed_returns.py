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
FLOW_REACH = 1.25
MOUTH_TO_CURVE = SOCKET_DEPTH + FLOW_REACH

UPPER_ARC_R = 12.2
UPPER_MOUTH_Z = 22.0
LOWER_ARC_R = 6.0
LOWER_MOUTH_DROP = LOWER_ARC_R + MOUTH_TO_CURVE

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


def _unit(v):
    return _scale(v, 1.0 / math.sqrt(sum(c*c for c in v)))


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def elbow_layout(wall_fore_y, x, z, return_port, bed_z=None, *, lower=None):
    """An upright scanned PP0308E immediately below the rear valve.

    The forward leg faces the junction. One R14 tube bend turns the junction's
    downward outlet toward that leg; a short straight tube joins elbow and
    valve. Displayed tubing ends at the known mouths, not imagined stops.
    """
    target = tuple(return_port['point'])
    if lower is None:
        lower = {'point': (x, wall_fore_y + 22.775 + LOWER_ARC_R,
                           z - LOWER_MOUTH_DROP), 'axis': (0., 0., -1.)}
    mouth = tuple(lower['point'])
    corner = (target[0], target[1], target[2] - STUB_FACE_GAP - ELBOW_FACE)
    up = (0., 0., 1.)
    aft = _unit((mouth[0] - corner[0], mouth[1] - corner[1], 0.))
    up_face = _add(corner, _scale(up, ELBOW_FACE))
    out_face = _add(corner, _scale(aft, ELBOW_FACE))
    horizontal = _scale(aft, -1.)
    lead = mouth[2] - corner[2] - TUBE_BEND_R
    path = [_line(mouth, (0., 0., -1.), lead)]
    path.append(_arc(path[-1]['end_mm'], horizontal, TUBE_BEND_R, -math.pi/2, math.pi/2))
    path.append(_line(path[-1]['end_mm'], horizontal, math.dist(path[-1]['end_mm'], out_face)))
    stub = _line(up_face, up, STUB_FACE_GAP)
    return {'corner':corner, 'up_axis':up, 'aft_axis':aft, 'x_axis':_cross(aft,up),
            'up_face':up_face, 'aft_face':out_face, 'tilt_degrees':0.,
            'target':dict(return_port), 'stub':(stub,), 'formed_tube':tuple(path),
            'stub_cut_nominal_mm':STUB_FACE_GAP+ELBOW_INSERTION_NOMINAL+VALVE_INSERTION_NOMINAL,
            'formed_cut_nominal_mm':sum(s['length_mm'] for s in path)+ELBOW_INSERTION_NOMINAL+SOCKET_DEPTH-LINK_NOMINAL_AXIAL_PLAY,
            'formed_exposed_length_mm':sum(s['length_mm'] for s in path),
            'junction_straight_exposed_mm':lead,
            'valve_straight_exposed_mm':STUB_FACE_GAP}


def junction_ports(wall_fore_y, x, z, upper_port, return_port, bed_z=None):
    """One common junction: upward valve link and downward tube outlet."""
    upper_target = tuple(upper_port['point'])
    upper_root = (x,upper_target[1]-UPPER_ARC_R,z)
    arc = _fork_arc(upper_root,UPPER_ARC_R,math.pi/2,(0.,0.,1.))
    upper = (arc,_line(arc['end_mm'],(0.,0.,1.),UPPER_MOUTH_Z-UPPER_ARC_R))
    mouth=upper[-1]['end_mm']
    lower_arc = _fork_arc((x, upper_target[1], z), LOWER_ARC_R, math.pi/2, (0.,0.,-1.))
    lower = (lower_arc, _line(lower_arc['end_mm'], (0.,0.,-1.), MOUTH_TO_CURVE))
    lower_mouth = lower[-1]['end_mm']
    return {'wall_fore_y':float(wall_fore_y), 'pump_axis':(float(x),float(z)),
            'upper_root_local_y':upper_root[1]-wall_fore_y,
            'upper_flow_segments':upper, 'lower_flow_segments':lower,
            'upper':{'point':mouth,'axis':(0.,0.,1.),'tube_stop':_add(mouth,(0.,0.,-SOCKET_DEPTH))},
            'lower':{'point':lower_mouth,'axis':(0.,0.,-1.),'tube_stop':_add(lower_mouth,(0.,0.,SOCKET_DEPTH))},
            'upper_target':dict(upper_port),'return_target':dict(return_port),
            'lower_clock_about_y_degrees':0., 'seal_land_mm':SEAL_LAND,'socket_depth_mm':SOCKET_DEPTH}


def station(wall_fore_y,x,z,upper_port,return_port,bed_z=None):
    if bed_z is None:bed_z=z-25.924
    junction=junction_ports(wall_fore_y,x,z,upper_port,return_port,bed_z)
    elbow=elbow_layout(wall_fore_y,x,z,return_port,bed_z,lower=junction['lower'])
    start=junction['upper']['point']
    return {'junction':junction,'elbow':elbow,
            'upper_tube':_line(start,(0.,0.,1.),upper_port['point'][2]-start[2])}


def layouts(plate):
    return {str(x):station(plate['fore_y'],x,z,plate['upper_ports'][str(x)],
                          plate['return_ports'][str(x)],plate['fixture_print_bed_z'])
            for x,z in plate['holes']}
