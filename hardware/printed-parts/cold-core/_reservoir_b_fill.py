"""B-fill tube passage and independent R14 bend holder, in appliance XYZ.

The R14 bend and 6.8 mm bore use the accepted holder's tube envelope.
The cap passage is circular, with 0.5 mm insertion lead-ins and a supported
roof allowance toward print-up. The inlet extends to the front cap face;
the outlet turns directly into the reservoir seat.
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
    fore_y = front + 23.0
    return {
        'entry_world_mm': entry,
        'outward_axis_world': (0.0, -1.0, 0.0),
        'route_points_world_mm': (entry, (x, y, entry[2]), tip),
        'bend_radius_mm': BEND_RADIUS,
        'channel_diameter_mm': CHANNEL_DIAMETER,
        'channel_section': 'round',
        'wall_mm': WALL,
        'outlet_leg_mm': 0.0,
        'mouth_lead_in_mm': MOUTH,
        'cup_mouth_relief_mm': MOUTH,
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
        'stock_min_world_mm': (x - 16.5, front, floor),
        'stock_max_world_mm': (x + 16.5, y + 15.0, face),

    }


def _body_section():
    import cadquery as cq
    outer = CHANNEL_RADIUS + WALL
    lo, hi = BEND_RADIUS - outer, BEND_RADIUS + outer
    z = CHANNEL_CENTRE + DOME_LIFT
    return (cq.Workplane('XZ').moveTo(lo, 0.0).lineTo(hi, 0.0).lineTo(hi, z)
            .threePointArc((BEND_RADIUS, z + outer), (lo, z)).close())


def _channel_section():
    import cadquery as cq
    return cq.Workplane('XZ').moveTo(BEND_RADIUS, CHANNEL_CENTRE).circle(CHANNEL_RADIUS)


def _mouth():
    import cadquery as cq
    def at(y, radius):
        plane = cq.Plane(origin=(0.0, y, 0.0), xDir=(1.0, 0.0, 0.0),
                         normal=(0.0, -1.0, 0.0))
        return (cq.Workplane(plane).moveTo(BEND_RADIUS, CHANNEL_CENTRE)
                .circle(radius).wires().val())
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


@lru_cache(maxsize=1)
def channel_air():
    """Continuous round tube envelope, including its mouth relief and print allowance."""
    data=passage()
    x,y,tangent_z=data['bend_end_world_mm']
    turn_y=y-BEND_RADIUS
    _body,channel=holder_sections(turn_y-data['entry_world_mm'][1],0.)
    channel=channel.rotate((0,0,0),(0,1,0),-90.).translate((x+CHANNEL_CENTRE,turn_y,tangent_z))
    return channel.fuse(channel.translate((0.,0.,data['supported_roof_allowance_mm']))).clean()


@lru_cache(maxsize=1)
def guide_native():
    """The accepted 2 mm R14 holder, printed flat on its D back."""
    import importlib.util
    from pathlib import Path
    root=next(p for p in Path(__file__).resolve().parents if (p/'future').is_dir())
    spec=importlib.util.spec_from_file_location('_b_fill_r14',root/'future/tube-bend-holder-exploration/tube_bend_holder.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.holder(WALL,0.).val()


def guide_world():
    """Installed bend holder, clear of the reservoir cap at its vertical outlet."""
    x,y,z=passage()['bend_end_world_mm']
    return guide_native().rotate((0,0,0),(0,1,0),-90.).translate(
        (x+CHANNEL_CENTRE,y-BEND_RADIUS,z))


def features(cup_height):
    return {'cut':channel_air(),'channel_air':channel_air(),'holder_outer':guide_world()}
