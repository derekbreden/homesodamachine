"""Continuous B-fill tube guide and the local cup/lid clamp, in appliance XYZ.

The R14, D6.8 teardrop, 2 mm section and 0.5 mm mouths use the accepted
holder geometry in future/tube-bend-holder-exploration. The inlet extends to
the front cap face; the outlet turns directly into the reservoir seat.
"""
from functools import lru_cache
import importlib
import math

BEND_RADIUS = 14.0
CHANNEL_DIAMETER = 6.8
WALL = 2.0
MOUTH = 0.5
CHANNEL_RADIUS = CHANNEL_DIAMETER / 2.0
CHANNEL_CENTRE = WALL + CHANNEL_RADIUS
DOME_LIFT = (math.sqrt(2.0) - 1.0) * CHANNEL_RADIUS


def passage():
    """Data-only interface for the continuous tube and both printed pieces."""
    core = importlib.import_module('_cold_core_interface')
    layout = importlib.import_module('above_core')
    pose = layout.cap_lid_pose()
    cup_height = core.foam_cap_height - core.head_pad_height
    floor = pose['translation_mm'][2] - cup_height + core.cap_shell_clearance
    x, y = layout.point(pose, (*core.reservoir_fill_conduit_xy(-1), 0.0))[:2]
    front = layout.point(pose, (core.outer_shell_x_length / 2.0, 0.0, 0.0))[1]
    import fits
    tangent_z = floor
    entry = (x, front, tangent_z + BEND_RADIUS)
    tip = (x, y, floor - 5.4)
    face = layout.specification()['cap_face_z_mm']
    lift_y = y - BEND_RADIUS * (1.0 - math.sin(math.pi / 4.0))
    fore_y = lift_y - 2.0
    clamp_stations = []
    for name, axis in (('aft', (x, y + 9.0)),
                       ('fore-west', (x - 10.5, fore_y)),
                       ('fore-east', (x + 10.5, fore_y))):
        clamp_stations.append({
            'name': name, 'axis_world_xy_mm': axis,
            'screw_length_mm': 10.0, 'insert': 'RX-M3x5.7',
            'insert_length_mm': 5.7,
            'insert_face_world_z_mm': pose['translation_mm'][2] - core.cap_lid_clearance,
            'head_seat_world_z_mm': face - 3.15})
    return {
        'entry_world_mm': entry,
        'outward_axis_world': (0.0, -1.0, 0.0),
        'route_points_world_mm': (entry, (x, y, entry[2]), tip),
        'bend_radius_mm': BEND_RADIUS,
        'channel_diameter_mm': CHANNEL_DIAMETER,
        'wall_mm': WALL,
        'outlet_leg_mm': 0.0,
        'mouth_lead_in_mm': MOUTH,
        'supported_roof_allowance_mm': fits.supported_surface,
        'print_up_world': (0.0, 0.0, 1.0),
        'bend_end_world_mm': (x, y, tangent_z),
        'outlet_world_mm': (x, y, floor),
        'tip_world_mm': tip,
        'cup_floor_world_z_mm': floor,
        'cup_top_world_z_mm': pose['translation_mm'][2] - core.cap_lid_clearance,
        'lid_bottom_world_z_mm': pose['translation_mm'][2],
        'lid_face_world_z_mm': face,
        'roof_top_world_z_mm': face,
        'throat_roof_stock_mm': face - (entry[2] + CHANNEL_RADIUS + fits.supported_surface),
        'entry_leadin_roof_stock_mm': face - (entry[2] + CHANNEL_RADIUS + MOUTH + fits.supported_surface),
        'stock_min_world_mm': (x - 8.0, front, floor),
        'stock_max_world_mm': (x + 7.0, y + 15.0, face),
        'clamp_stations': clamp_stations,
        'clamp_crossbar_centre_world_xy_mm': (x, fore_y),
        'clamp_crossbar_length_mm': 33.0,
        'clamp_crossbar_width_mm': 12.0,
        # Mid-arc reference for the requested three-point clamp, not a force prediction.
        'lift_reference_world_mm': (x, lift_y, floor + BEND_RADIUS * math.cos(math.pi / 4.0)),
        'clamp_insert': 'RX-M3x5.7',
        'clamp_screw_length_mm': 10.0,
        'clamp_pilot_diameter_mm': 4.0,
        'clamp_pilot_depth_mm': 9.0,
        'clamp_through_diameter_mm': 3.3,
        'clamp_head_recess_diameter_mm': 5.8,
        'clamp_head_recess_depth_mm': 3.15,
    }


def _teardrop(wp, x, z, radius):
    k = radius / math.sqrt(2.0)
    return (wp.moveTo(x + k, z + k).lineTo(x, z + math.sqrt(2.0) * radius)
            .lineTo(x - k, z + k)
            .threePointArc((x, z - radius), (x + k, z + k)).close())


def _body_section():
    import cadquery as cq
    outer = CHANNEL_RADIUS + WALL
    lo, hi = BEND_RADIUS - outer, BEND_RADIUS + outer
    z = CHANNEL_CENTRE + DOME_LIFT
    return (cq.Workplane('XZ').moveTo(lo, 0.0).lineTo(hi, 0.0).lineTo(hi, z)
            .threePointArc((BEND_RADIUS, z + outer), (lo, z)).close())


def _channel_section():
    import cadquery as cq
    return _teardrop(cq.Workplane('XZ'), BEND_RADIUS, CHANNEL_CENTRE, CHANNEL_RADIUS)


def _mouth():
    import cadquery as cq
    def at(y, radius):
        plane = cq.Plane(origin=(0.0, y, 0.0), xDir=(1.0, 0.0, 0.0),
                         normal=(0.0, -1.0, 0.0))
        return _teardrop(cq.Workplane(plane), BEND_RADIUS,
                         CHANNEL_CENTRE, radius).wires().val()
    return cq.Solid.makeLoft([
        at(-0.3, CHANNEL_RADIUS + MOUTH + 0.3),
        at(MOUTH + 0.05, CHANNEL_RADIUS - 0.05)], ruled=True)


def holder_sections(inlet_leg, outlet_leg=0.0):
    """Accepted outer body and complete channel, with an extended inlet leg."""
    import cadquery as cq
    axis = ((0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    mirror = cq.Vector(math.sqrt(0.5), -math.sqrt(0.5), 0.0)
    origin = cq.Vector()
    body = _body_section().revolve(90.0, *axis).union(_body_section().extrude(inlet_leg))
    channel = (_channel_section().revolve(90.0, *axis)
               .union(_channel_section().extrude(inlet_leg)))
    if outlet_leg > 0.0:
        body = body.union(_body_section().extrude(outlet_leg).mirror(mirror, origin))
        channel = channel.union(_channel_section().extrude(outlet_leg).mirror(mirror, origin))
    start = _mouth().translate((0.0, -inlet_leg, 0.0))
    end = _mouth().translate((0.0, -outlet_leg, 0.0)).mirror(mirror, origin)
    return body.val(), channel.val().fuse(start, end).clean()


@lru_cache(maxsize=2)
def features(cup_height):
    """Full-height cup stock, compensated channel roof and three blind clamps."""
    import cadquery as cq
    data = passage()
    x, y, tangent_z = data['bend_end_world_mm']
    front = data['entry_world_mm'][1]
    turn_y = y - BEND_RADIUS
    body, channel = holder_sections(turn_y - front, data['outlet_leg_mm'])
    def place(shape):
        return shape.rotate((0, 0, 0), (0, 1, 0), -90.0).translate(
            (x + CHANNEL_CENTRE, turn_y, tangent_z))
    body, channel = place(body), place(channel)
    up = data['supported_roof_allowance_mm']
    # The supported underside occupies this space after printing. Retreat
    # only the crown toward print-up; the nominal lower envelope stays fixed.
    channel = channel.fuse(channel.translate((0.0, 0.0, up))).clean()
    body = body.fuse(body.translate((0.0, 0.0, up))).clean()
    def box(lo, hi):
        return cq.Solid.makeBox(*(b - a for a, b in zip(lo, hi)), cq.Vector(*lo))
    low, high = data['stock_min_world_mm'], data['stock_max_world_mm']
    bx, by = data['clamp_crossbar_centre_world_xy_mm']
    crossbar = (cq.Workplane('XY').workplane(offset=low[2]).center(bx, by)
                .slot2D(data['clamp_crossbar_length_mm'], data['clamp_crossbar_width_mm'])
                .extrude(high[2] - low[2]).val())
    stock = box(low, high).fuse(body, crossbar).clean()
    cup_top = data['cup_top_world_z_mm']
    lid_bottom = data['lid_bottom_world_z_mm']
    face = data['lid_face_world_z_mm']
    roof_top = data['roof_top_world_z_mm']
    pilots, shafts, heads = [], [], []
    for station in data['clamp_stations']:
        sx, sy = station['axis_world_xy_mm']
        def cylinder(radius, z0, z1):
            return cq.Solid.makeCylinder(radius, z1 - z0, cq.Vector(sx, sy, z0))
        pilots.append(cylinder(data['clamp_pilot_diameter_mm'] / 2.0,
                                cup_top - data['clamp_pilot_depth_mm'], cup_top + 0.1))
        shafts.append(cylinder(data['clamp_through_diameter_mm'] / 2.0, cup_top, face + 0.1))
        heads.append(cylinder(data['clamp_head_recess_diameter_mm'] / 2.0,
                               face - data['clamp_head_recess_depth_mm'], face + 0.1))
    bb = stock.BoundingBox()
    cup = stock.intersect(box((bb.xmin - 1.0, front - 1.0, low[2] - 0.1),
                              (bb.xmax + 1.0, bb.ymax + 1.0, cup_top)))
    lid = stock.intersect(box((bb.xmin - 1.0, front - 1.0, lid_bottom),
                              (bb.xmax + 1.0, bb.ymax + 1.0, roof_top + 0.1)))
    return {'cup_add': cup, 'lid_add': lid,
            'cut': channel.fuse(*pilots, *shafts, *heads).clean(),
            'channel_air': channel, 'clamp_pilots': pilots,
            'clamp_head_air': heads, 'holder_outer': body,
            'roof_top_z_mm': roof_top}
