"""East-wall bearings for the back-top-carried meter's fixed collars.

The purchased body and tube ports keep their selected world poses. Each
six-millimetre bearing meets the wall through a flat three-millimetre beam.
The vertical tie opening retains three millimetres of stock on both sides.
Strap sections are nominal clearance allowances, not retention qualification.
"""

import importlib
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
HW = HERE.parents[2]
sys.path[:0] = [str(HW / 'manifold-layout'), str(HW / 'scripts'),
                str(HW / 'reference/digiten-flow-sensor'),
                str(HW / 'printed-parts/cadlib')]
import above_core as layout


def meter_support_datums():
    import fits
    meter = importlib.import_module('digiten_flow_sensor')
    first, last, r0, r1 = meter.mounting_profile(1)[-1]
    axial = (first + last) / 2.
    radius, wall = max(r0, r1) + fits.slip, 3.
    result = []
    for side in (-1, 1):
        station = side * axial - (.5 if side == 1 else 0.)
        x, y, z = layout.point(layout.pose('digiten-flow'), (station, 0., 0.))
        seat_bottom = z - radius - wall
        bottom = seat_bottom - (.5 if side == 1 else 0.)
        tie_y = y + (.7 if side == -1 else -1.7)
        beam_y = tie_y if side == -1 else y - .4
        beam_width = 9.
        if side == -1:
            # A broad flat dogleg passes fore of the fixed gas-drop column.
            wall_y = 358.
            beam_boxes = (
                ((x+3., beam_y-beam_width/2., bottom),
                 (73., beam_y+beam_width/2., bottom+wall)),
                ((64., wall_y-beam_width/2., bottom),
                 (73., beam_y+beam_width/2., bottom+wall)),
                ((64., wall_y-beam_width/2., bottom),
                 (98.51, wall_y+beam_width/2., bottom+wall)),
            )
        else:
            wall_y = beam_y
            # The full quarter seat overlaps this broad beam east of the
            # unchanged reservoir-draw tube beneath its western edge.
            beam_boxes = (((x+3., beam_y-beam_width/2., bottom),
                           (98.51, beam_y+beam_width/2., bottom+wall)),)
        result.append({
            'parent': 'enclosure-back-top',
            'centre_world_mm': (x, y, z),
            'width_mm': 6., 'seat_radius_mm': radius, 'wall_mm': wall,
            'native_bearing_band_mm': (station - 3., station + 3.),
            'seat_bottom_world_z_mm': seat_bottom,
            'beam_width_mm': beam_width, 'beam_thickness_mm': wall,
            'beam_bottom_world_z_mm': bottom,
            'beam_boxes_world_mm': beam_boxes,
            'wall_lane_world_y_mm': wall_y,
            'wall_root_x_mm': 98.51,
            'tie_plane_world_y_mm': tie_y,
            'tie_slot_min_world_mm': (x + 16., beam_y - 1.5, bottom - .1),
            'tie_slot_max_world_mm': (x + 18., beam_y + 1.5, bottom + wall + .1),
        })
    return tuple(result)


def meter_supports():
    """One connected world-frame solid per fixed collar, open west and above."""
    import cadquery as cq
    result = []
    for data in meter_support_datums():
        x, y, z = data['centre_world_mm']
        radius, wall = data['seat_radius_mm'], data['wall_mm']
        half = data['width_mm'] / 2.
        low = data['seat_bottom_world_z_mm']
        outer = cq.Solid.makeCylinder(radius + wall, 2. * half,
                                      cq.Vector(x, y - half, z), cq.Vector(0, 1, 0))
        quarter = outer.intersect(cq.Solid.makeBox(
            radius + wall, 2. * half, radius + wall,
            cq.Vector(x, y - half, low)))
        beams = [cq.Solid.makeBox(*(b[i]-a[i] for i in range(3)), cq.Vector(*a))
                 for a, b in data['beam_boxes_world_mm']]
        bore = cq.Solid.makeCylinder(radius, 2. * half + .2,
                                     cq.Vector(x, y - half - .1, z), cq.Vector(0, 1, 0))
        a, b = data['tie_slot_min_world_mm'], data['tie_slot_max_world_mm']
        slot = cq.Solid.makeBox(*(b[i] - a[i] for i in range(3)), cq.Vector(*a))
        result.append(quarter.fuse(*beams).cut(bore, slot).clean())
    return tuple(result)


def meter_tie_routes():
    """Nominal straps through the wall beams and around fixed collars.

    The 2.5 by 0.8 mm sections clear the printed stock. Purchased tie/head
    dimensions, corner bending, threading and holding force are unqualified.
    """
    result = {}
    for number, data in enumerate(meter_support_datums()):
        x, _bearing_y, z = data['centre_world_mm']
        y = data['tie_plane_world_y_mm']
        radius = data['seat_radius_mm'] + .6
        bottom = data['beam_bottom_world_z_mm'] - .6
        slot_y = sum(point[1] for point in (
            data['tie_slot_min_world_mm'], data['tie_slot_max_world_mm'])) / 2.
        west = (x - 4., y, bottom)
        under = (x + 17., slot_y, bottom)
        upper_slot = (x + 17., slot_y, z + 1.)
        upper = (x + 17., y, z + 1.)
        phi = math.atan2(upper[2] - z, upper[0] - x)
        east_angle = math.degrees(phi + math.acos(radius / math.hypot(
            upper[0] - x, upper[2] - z)))
        phi = math.atan2(west[2] - z, west[0] - x)
        west_angle = math.degrees(phi - math.acos(radius / math.hypot(
            west[0] - x, west[2] - z))) % 360.

        def point(angle):
            radians = math.radians(angle)
            return (x + radius * math.cos(radians), y, z + radius * math.sin(radians))

        def line(a, b, wide_axis=(0., 1., 0.)):
            return {'kind': 'line', 'points_mm': [a, b], 'wide_axis': wide_axis}

        east, far = point(east_angle), point(west_angle)
        if abs(slot_y-y) > 1.e-9:
            # The aft collar plane stays fore of the reservoir tube. Offset
            # below and above the beam, leaving its complete slot surround.
            below_collar = (x + 5., y, bottom)
            below_slot = (x + 5., slot_y, bottom)
            segments = [line(west, below_collar),
                        line(below_collar, below_slot, (1., 0., 0.)),
                        line(below_slot, under), line(under, upper_slot),
                        line(upper_slot, upper, (1., 0., 0.))]
        else:
            segments = [line(west, under), line(under, upper)]
        segments += [line(upper, east),
                    {'kind': 'arc', 'points_mm': [east, point((east_angle + west_angle) / 2.), far],
                     'radius_mm': radius, 'sweep_degrees': west_angle - east_angle,
                     'wide_axis': (0., 1., 0.)}, line(far, west)]
        length = sum(math.dist(*row['points_mm']) if row['kind'] == 'line'
                     else radius * math.radians(row['sweep_degrees']) for row in segments)
        result['meter-' + ('fore' if number == 0 else 'aft')] = {
            'parent': 'enclosure-back-top', 'segments': segments, 'length_mm': length,
            'stock': '6-inch narrow nylon tie', 'stock_length_mm': 152.4,
            'width_mm': 2.5, 'thickness_mm': .8,
            'collar_plane_world_y_mm': y,
            'strip_basis': 'Nominal layout section; purchased strap/head dimensions unmeasured',
        }
    return result
