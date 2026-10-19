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

LOWER_ROOT_Y = 8.5
LOWER_ARC_R = 8.0
LOWER_TURN_DEG = 45.0
LOWER_POST_ARC = 11.4
UPPER_ARC_R = 12.2
UPPER_MOUTH_Z = 22.0
RETURN_ARC_R = 6.0
VALVE_LINK_EXPOSED = 2.0

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


def junction_ports(wall_fore_y, x, z, upper_port, return_port):
    """The asymmetric junction, aligned to the two original purchased valve ports.

    ``upper_port`` and ``return_port`` contain ``point`` and ``axis`` tuples.
    The outer lower arms are clocked slightly about Y so each straight link
    lies in its own return plane; their angle to +Y remains 45 degrees.
    """
    upper_target = tuple(upper_port["point"])
    lower_target = tuple(return_port["point"])
    angle = math.radians(LOWER_TURN_DEG)
    intercept = wall_fore_y + LOWER_ROOT_Y + LOWER_ARC_R * math.tan(angle / 2)
    phi = math.asin((lower_target[0] - x)
                    / (math.tan(angle) * (lower_target[1] - intercept)))
    lower_root = (x, wall_fore_y + LOWER_ROOT_Y, z)
    lower_arc = _fork_arc(lower_root, LOWER_ARC_R, angle,
                          (math.sin(phi), 0., -math.cos(phi)))
    lower_straight = _line(lower_arc["end_mm"], lower_arc["end_tangent"], LOWER_POST_ARC)
    lower_mouth = lower_straight["end_mm"]
    lower_axis = lower_straight["end_tangent"]
    upper_root = (x, upper_target[1] - UPPER_ARC_R, z)
    upper_arc = _fork_arc(upper_root, UPPER_ARC_R, math.pi / 2, (0., 0., 1.))
    upper_straight = _line(upper_arc["end_mm"], (0., 0., 1.),
                           UPPER_MOUTH_Z - UPPER_ARC_R)
    upper_mouth = upper_straight["end_mm"]
    return {
        "wall_fore_y": float(wall_fore_y), "pump_axis": (float(x), float(z)),
        "upper_root_local_y": upper_root[1] - wall_fore_y,
        "upper_flow_segments": (upper_arc, upper_straight),
        "lower_flow_segments": (lower_arc, lower_straight),
        "upper": {"point": upper_mouth, "axis": (0., 0., 1.),
                  "tube_stop": _add(upper_mouth, (0., 0., -SOCKET_DEPTH))},
        "lower": {"point": lower_mouth, "axis": lower_axis,
                  "tube_stop": _add(lower_mouth, _scale(lower_axis, -SOCKET_DEPTH))},
        "upper_target": dict(upper_port), "return_target": dict(return_port),
        "lower_clock_about_y_degrees": math.degrees(phi),
        "seal_land_mm": SEAL_LAND, "socket_depth_mm": SOCKET_DEPTH,
    }


def return_layout(lower_mouth, lower_axis, return_port, *, radius=RETURN_ARC_R,
                  valve_exposed=VALVE_LINK_EXPOSED):
    """One compound return and two straight LLDPE links.

    The printed body contains the first turn, horizontal passage and final
    quarter turn. Six-millimetre sockets end one millimetre before the curves.
    The incoming link is captive between opposed, rigidly supported stops;
    its cut length is set from the actual mounted span at factory assembly.
    The outgoing link is anchored by the purchased valve's own collet.
    """
    p, d, target = tuple(lower_mouth), tuple(lower_axis), tuple(return_port["point"])
    horizontal_length = math.hypot(d[0], d[1])
    horizontal = (d[0] / horizontal_length, d[1] / horizontal_length, 0.)
    beta = math.atan2(-d[2], horizontal_length)
    across = math.hypot(target[0] - p[0], target[1] - p[1])
    diagonal = (p[2] - target[2] + valve_exposed + radius * math.cos(beta)
                + MOUTH_TO_CURVE * (1 - math.sin(beta))) / math.sin(beta)
    bridge = across - (diagonal + MOUTH_TO_CURVE) * math.cos(beta) \
        - radius * (1 + math.sin(beta))
    a = _add(p, _scale(d, diagonal))
    first = _line(a, d, MOUTH_TO_CURVE)
    turn1 = _arc(first["end_mm"], horizontal, radius, -beta, beta)
    middle = _line(turn1["end_mm"], horizontal, bridge)
    turn2 = _arc(middle["end_mm"], horizontal, radius, 0., math.pi / 2)
    last = _line(turn2["end_mm"], (0., 0., 1.), MOUTH_TO_CURVE)
    b = last["end_mm"]
    stop0 = _add(p, _scale(d, -SOCKET_DEPTH))
    stop1 = _add(a, _scale(d, SOCKET_DEPTH))
    stop_span = diagonal + 2 * SOCKET_DEPTH
    segments = (first, turn1, middle, turn2, last)
    return {
        "input": {"point": a, "axis": _scale(d, -1.), "tube_stop": stop1},
        "output": {"point": b, "axis": (0., 0., 1.),
                   "tube_stop": _add(b, (0., 0., -SOCKET_DEPTH))},
        "target": dict(return_port), "flow_segments": segments,
        "diagonal_link": _line(p, d, diagonal),
        "valve_link": _line(b, (0., 0., 1.), valve_exposed),
        "opposed_stops": (stop0, stop1), "opposed_stop_axis": d,
        "nominal_stop_span_mm": stop_span,
        "nominal_link_cut_mm": stop_span - LINK_NOMINAL_AXIAL_PLAY,
        "nominal_link_tip_points": (
            _add(stop0, _scale(d, LINK_NOMINAL_AXIAL_PLAY / 2)),
            _add(stop1, _scale(d, -LINK_NOMINAL_AXIAL_PLAY / 2))),
        "maximum_total_axial_play_mm": LINK_MAX_TOTAL_AXIAL_PLAY,
        "minimum_seal_engagement_mm": LINK_MIN_SEAL_ENGAGEMENT,
        "flow_radius_mm": float(radius), "flow_bridge_mm": bridge,
        "flow_length_mm": sum(segment["length_mm"] for segment in segments),
        "total_turn_degrees": math.degrees(beta) + 90.,
        "seal_land_mm": SEAL_LAND, "socket_depth_mm": SOCKET_DEPTH,
        "mouth_to_curve_mm": MOUTH_TO_CURVE,
        "relaxed_cuff_od_mm": CUFF_OD, "occupied_cuff_od_mm": OCCUPIED_CUFF_OD,
        "flow_body_od_mm": FLOW_OD,
        "minimum_flow_centerline_z_mm": target[2] - valve_exposed - MOUTH_TO_CURVE - radius,
    }


def layouts(plate):
    """Four station-derived declarations, keyed by the serialized pump-port X."""
    out = {}
    for x, z in plate["holes"]:
        key = str(x)
        junction = junction_ports(plate["fore_y"], x, z,
                                   plate["upper_ports"][key], plate["return_ports"][key])
        lower = junction["lower"]
        returned = return_layout(lower["point"], lower["axis"], plate["return_ports"][key])
        target = plate["upper_ports"][key]["point"]
        upper_length = target[2] - junction["upper"]["point"][2]
        out[key] = {"junction": junction, "return": returned,
                    "upper_tube": _line(junction["upper"]["point"], (0., 0., 1.), upper_length)}
    return out
