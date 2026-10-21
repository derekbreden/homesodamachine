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
LOWER_TURN_DEG = 50.0
LOWER_POST_ARC = 11.4

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
TUBE_BEND_R = 28.0


def _unit(v):
    return _scale(v, 1.0 / math.sqrt(sum(c*c for c in v)))


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def elbow_layout(wall_fore_y, x, z, return_port, bed_z=None, *, lower=None):
    """An upright scanned PP0308E immediately below the rear valve.

    The forward leg faces the junction. One shallow R28 tube bend turns the
    diagonal outlet toward that leg; a short straight tube joins elbow and
    valve. Displayed tubing ends at the known mouths, not imagined stops.
    """
    target = tuple(return_port['point'])
    if lower is None:
        lower = junction_ports(wall_fore_y, x, z,
            {'point': (x, wall_fore_y + 22.775, z + UPPER_MOUTH_Z),
             'axis': (0., 0., -1.)}, return_port)['lower']
    mouth = tuple(lower['point'])
    corner = (target[0], target[1], target[2] - STUB_FACE_GAP - ELBOW_FACE)
    up = (0., 0., 1.)
    aft = _unit((mouth[0] - corner[0], mouth[1] - corner[1], 0.))
    up_face = _add(corner, _scale(up, ELBOW_FACE))
    out_face = _add(corner, _scale(aft, ELBOW_FACE))
    horizontal = _scale(aft, -1.)
    direction = tuple(lower['axis'])
    beta = math.atan2(-direction[2], math.hypot(*direction[:2]))
    lead = (mouth[2] - corner[2] - TUBE_BEND_R * (1. - math.cos(beta))) / math.sin(beta)
    path = [_line(mouth, direction, lead)]
    path.append(_arc(path[-1]['end_mm'], horizontal, TUBE_BEND_R, -beta, beta))
    tail = sum((out_face[i] - path[-1]['end_mm'][i]) * horizontal[i] for i in range(3))
    path.append(_line(path[-1]['end_mm'], horizontal, tail))
    stub = _line(up_face, up, STUB_FACE_GAP)
    return {'corner':corner, 'up_axis':up, 'aft_axis':aft, 'x_axis':_cross(aft,up),
            'up_face':up_face, 'aft_face':out_face, 'tilt_degrees':0.,
            'target':dict(return_port), 'stub':(stub,), 'formed_tube':tuple(path),
            'stub_cut_nominal_mm':STUB_FACE_GAP+ELBOW_INSERTION_NOMINAL+VALVE_INSERTION_NOMINAL,
            'formed_cut_nominal_mm':sum(s['length_mm'] for s in path)+ELBOW_INSERTION_NOMINAL+SOCKET_DEPTH-LINK_NOMINAL_AXIAL_PLAY,
            'formed_exposed_length_mm':sum(s['length_mm'] for s in path),
            'tube_turn_degrees':math.degrees(beta), 'tube_bend_radius_mm':TUBE_BEND_R,
            'junction_straight_exposed_mm':lead,
            'elbow_straight_exposed_mm':tail,
            'valve_straight_exposed_mm':STUB_FACE_GAP}


def junction_ports(wall_fore_y, x, z, upper_port, return_port, bed_z=None):
    """Upward valve link and a diagonal outlet aimed at the rear elbow."""
    upper_target = tuple(upper_port['point'])
    upper_root = (x,upper_target[1]-UPPER_ARC_R,z)
    arc = _fork_arc(upper_root,UPPER_ARC_R,math.pi/2,(0.,0.,1.))
    upper = (arc,_line(arc['end_mm'],(0.,0.,1.),UPPER_MOUTH_Z-UPPER_ARC_R))
    mouth=upper[-1]['end_mm']
    target = tuple(return_port['point'])
    angle = math.radians(LOWER_TURN_DEG)
    intercept = upper_root[1] + LOWER_ARC_R * math.tan(angle / 2)
    phi = math.asin((target[0] - x) / (math.tan(angle) * (target[1] - intercept)))
    lower_arc = _fork_arc(upper_root, LOWER_ARC_R,
                          angle, (math.sin(phi), 0., -math.cos(phi)))
    lower_axis = lower_arc['end_tangent']
    lower = (lower_arc, _line(lower_arc['end_mm'], lower_axis, LOWER_POST_ARC))
    lower_mouth = lower[-1]['end_mm']
    upper_stop = _add(mouth,(0.,0.,-SOCKET_DEPTH))
    lower_stop = _add(lower_mouth,_scale(lower_axis,-SOCKET_DEPTH))
    setback = TUBE_ID/2 + FLOW_REACH
    gallery_upper = _add(upper_stop,(0.,0.,-setback))
    gallery_lower = _add(lower_stop,_scale(lower_axis,-setback))
    inlet_y = gallery_lower[1] + (gallery_upper[1]-gallery_lower[1]) * (
        (z-gallery_lower[2])/(gallery_upper[2]-gallery_lower[2]))
    return {'wall_fore_y':float(wall_fore_y), 'pump_axis':(float(x),float(z)),
            'upper_root_local_y':upper_root[1]-wall_fore_y,
            'gallery':{'upper':gallery_upper,'lower':gallery_lower,'inlet':(x,inlet_y,z)},
            'upper':{'point':mouth,'axis':(0.,0.,1.),'tube_stop':upper_stop},
            'lower':{'point':lower_mouth,'axis':lower_axis,
                     'tube_stop':lower_stop},
            'upper_target':dict(upper_port),'return_target':dict(return_port),
            'lower_clock_about_y_degrees':math.degrees(phi),
            'seal_land_mm':SEAL_LAND,'socket_depth_mm':SOCKET_DEPTH}


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
