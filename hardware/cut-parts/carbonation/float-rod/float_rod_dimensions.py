"""Finished carbonator guide rod and its assembly fit requirements, in inches.

These are design requirements for the finished part. The register depth and
point tolerances used in the fit calculation follow END-CAP-01's general
linear/angular tolerances. The cap-to-cap span is controlled by CV-WLD-01.
The calculation is available for on-demand drawing review, not a build gate.
"""

import math

finished_length = 5.110
length_tolerance = 0.005
diameter_tolerance = 0.002
inside_face_span = 5.000
inside_face_span_tolerance = 0.010
edge_break_maximum = 0.003
end_squareness_degrees = 0.5
register_depth_tolerance = 0.005
register_point_degrees = 135.0
register_point_tolerance_degrees = 0.5


def fit_envelope(*, rod_diameter, register_depth):
    """Conservative independent-extreme axial stack, including rod-end form.

The nominal flat rod seats on the drill cone, above its deepest tip. Edge
break can let it enter farther; end slope is bounded by the full diametral
height error at each end. Bore diameter must separately clear the rod OD.
"""
    def seat(depth, diameter, point, edge=0):
        return depth - (diameter / 2 - edge) / math.tan(math.radians(point / 2))

    end_error = (rod_diameter + diameter_tolerance) * math.tan(
        math.radians(end_squareness_degrees))
    nominal = seat(register_depth, rod_diameter, register_point_degrees)
    low = seat(register_depth - register_depth_tolerance,
               rod_diameter + diameter_tolerance,
               register_point_degrees - register_point_tolerance_degrees) - end_error
    high = seat(register_depth + register_depth_tolerance,
                rod_diameter - diameter_tolerance,
                register_point_degrees + register_point_tolerance_degrees,
                edge_break_maximum) + end_error
    return {
        "nominal_engagement": finished_length - inside_face_span - nominal,
        "nominal_clearance": inside_face_span + 2 * nominal - finished_length,
        "minimum_engagement": (finished_length - length_tolerance
                               - inside_face_span - inside_face_span_tolerance - high),
        "minimum_clearance": (inside_face_span - inside_face_span_tolerance
                              + 2 * low - finished_length - length_tolerance),
        "seat_minimum": low,
        "seat_maximum": high,
    }
