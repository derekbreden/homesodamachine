"""Integral fore Reservoir A C2 pair, in appliance millimetres.

The broad filled base joins both seats to the lid. Its equator is the root
of the two independent C2 spring pairs; the air above that plane stays open.
"""
import math
from pathlib import Path
import sys

CENTRE = (57.25, 209.75, 258.5)
PITCH = 13.5
TUBE_OD = 6.35
BORE = 6.35
WING = 2.4
TIP_DEGREES = 125.42102606277044
SPAN = 8.
LID_FACE = 253.4
FLOOR = 3.


def specification():
    radius = BORE/2
    outer = radius+WING
    x, y, z = CENTRE
    centres = [[x+side*PITCH/2, y, z] for side in (-1., 1.)]
    low = [centres[0][0]-outer, y-SPAN/2, LID_FACE-FLOOR]
    high = [centres[-1][0]+outer, y+SPAN/2, z]
    nose = WING/2
    middle = radius+nose
    # Disk-to-round-nose contact bound for a nominal bare tube. This is a
    # kinematic span allowance, not a spring-force or strain calculation.
    spread = TUBE_OD/2+nose-middle*math.sin(math.radians(TIP_DEGREES))
    return dict(
        closure='direct-snap', centre_world_mm=list(CENTRE),
        tube_centers_world_mm=centres, tube_axis_world=[0., 1., 0.],
        tube_axis_worlds=[[0., 1., 0.]]*2,
        tube_od_mm=TUBE_OD, bore_diameter_mm=BORE, seat_radius_mm=radius,
        tube_pitch_mm=PITCH, station_length_mm=SPAN, spring_thickness_mm=WING,
        tip_degrees=TIP_DEGREES, lid_face_z_mm=LID_FACE,
        base_floor_world_z_mm=LID_FACE-FLOOR, base_top_world_z_mm=z,
        base_bounds_mm=[low, high],
        body_bounds_mm=[low, [high[0], high[1], z-middle*math.cos(math.radians(TIP_DEGREES))+nose]],
        floor_stock_mm=FLOOR,
        outer_radius_mm=outer, outer_width_mm=PITCH+2*outer,
        central_land_mm=PITCH-BORE, static_outer_gap_mm=PITCH-2*outer,
        nominal_nose_spread_per_jaw_mm=spread,
        clearance_spread_per_jaw_mm=1.,
        opposing_jaw_envelope_gap_mm=PITCH-2*outer-2.,
        insertion_direction_world=[0., 0., -1.],
        print_up_world=[0., 0., 1.],
        print_basis='Lid flat underside on bed; C2 mouths grow upward, matching the floor-rooted trial orientation.',
        spring_basis='Accepted C2 bore6.35, wing2.4 and tip125.421 degrees; no load or lifetime claim.',
    )


def clips():
    """Two native C2 seats before their lower halves share the full base."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'cadlib'))
    from route_snap import tube_clip
    return tuple(tube_clip(point, (0., 1., 0.), (0., 0., 1.),
                           CENTRE[2]-LID_FACE, tube_od=TUBE_OD,
                           bore_diameter=BORE, wing=WING, span=SPAN,
                           tip_degrees=TIP_DEGREES, print_up=(0., 0., 1.))
                 for point in specification()['tube_centers_world_mm'])


def base():
    """One full-span solid with two cut seats and unbridged working jaws."""
    import cadquery as cq
    s = specification()
    lo, hi = s['base_bounds_mm']
    stock = cq.Solid.makeBox(*(b-a for a, b in zip(lo, hi)), cq.Vector(*lo))
    first, second = clips()
    body = stock.fuse(first, second)
    for x, y, z in s['tube_centers_world_mm']:
        bore = cq.Solid.makeCylinder(BORE/2, SPAN+.2,
            cq.Vector(x, y-SPAN/2-.1, z), cq.Vector(0., 1., 0.))
        body = body.cut(bore)
    return body.clean()
