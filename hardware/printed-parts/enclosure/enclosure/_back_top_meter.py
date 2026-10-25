"""East-wall bearings for the back-top-carried meter's fixed collars.

The purchased body and tube ports keep their selected world poses. Each
six-millimetre bearing meets the wall through a plain dogleg with at least
three millimetres of stock, starting on the seat's own west plane.
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
        tie_y = y + (.7 if side == -1 else -.5)
        beam_y = tie_y if side == -1 else y - .4
        beam_width = 9.
        beam_plan = None
        if side == -1:
            # A broad flat dogleg passes fore of the fixed gas-drop column.
            # Its six-millimetre neck shares the collar's two end planes;
            # one plain flare reaches full slot stock before X63.
            wall_y = 358.
            beam_plan = ((x, y-3.), (59., y-3.),
                         (63., beam_y-beam_width/2.),
                         (73., beam_y-beam_width/2.),
                         (73., beam_y+beam_width/2.),
                         (63., beam_y+beam_width/2.),
                         (59., y+3.), (x, y+3.))
            beam_boxes = (
                ((64., wall_y-beam_width/2., bottom),
                 (73., beam_y+beam_width/2., bottom+wall)),
                ((64., wall_y-beam_width/2., bottom),
                 (98.51, wall_y+beam_width/2., bottom+wall)),
            )
            # The wall lane rises off the wall on a 45-degree corbel: back-top prints
            # ceiling-down, and nothing stands over this lane below the gas union.
            lane_corbel = ((64., 98.51), (wall_y-beam_width/2., wall_y+beam_width/2.))
        else:
            # A flat dogleg reaches the wall aft of the fixed regulator.
            # The local pad carries the short tie beside the fixed collar.
            wall_y = 436.
            lane_corbel = None
            beam_boxes = (
                ((x, y-3., bottom), (x+3., y+3., bottom+wall)),
                ((x+3., y-3., bottom), (60., 437.5, bottom+wall)),
                ((59., tie_y-4.5, bottom), (67., tie_y+4.5, bottom+wall)),
                ((57.5, wall_y-wall/2., bottom-wall),
                 (98.51, wall_y+wall/2., bottom+wall)),
            )
        result.append({
            'parent': 'enclosure-back-top',
            'centre_world_mm': (x, y, z),
            'width_mm': 6., 'seat_radius_mm': radius, 'wall_mm': wall,
            'native_bearing_band_mm': (station - 3., station + 3.),
            'seat_bottom_world_z_mm': seat_bottom,
            'beam_width_mm': beam_width, 'beam_thickness_mm': wall,
            'beam_bottom_world_z_mm': bottom,
            'beam_plan_world_xy_mm': beam_plan,
            'beam_boxes_world_mm': beam_boxes,
            'lane_corbel_world_xy_mm': lane_corbel,
            'wall_lane_world_y_mm': wall_y,
            'wall_landing_width_mm': beam_width if side == -1 else wall,
            'wall_landing_height_mm': wall if side == -1 else 2.*wall,
            'wall_landing_bottom_world_z_mm': bottom if side == -1 else bottom-wall,
            'wall_root_x_mm': 98.51,
            'tie_plane_world_y_mm': tie_y,
            'tie_slot_min_world_mm': ((x + 16., beam_y - 1.5, bottom - .1)
                                      if side == -1 else (62., tie_y-1.5, bottom-.1)),
            'tie_slot_max_world_mm': ((x + 18., beam_y + 1.5, bottom + wall + .1)
                                      if side == -1 else (64., tie_y+1.5, bottom+wall+.1)),
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
        if data['lane_corbel_world_xy_mm']:
            (x0, x1), (y0, y1) = data['lane_corbel_world_xy_mm']
            top = data['beam_bottom_world_z_mm'] + wall
            beams.append(cq.Workplane('XZ')
                         .polyline(((x0, top), (x1, top), (x1, top + x1 - x0))).close()
                         .extrude(-(y1 - y0)).val().translate((0., y0, 0.)))
        if data['beam_plan_world_xy_mm']:
            beams.append(cq.Workplane('XY').polyline(data['beam_plan_world_xy_mm'])
                         .close().extrude(wall).val().translate(
                             (0., 0., data['beam_bottom_world_z_mm'])))
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
        slot_x = sum(point[0] for point in (
            data['tie_slot_min_world_mm'], data['tie_slot_max_world_mm'])) / 2.
        under = (slot_x, slot_y, bottom)
        upper = (slot_x, y, z + 1.)
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
