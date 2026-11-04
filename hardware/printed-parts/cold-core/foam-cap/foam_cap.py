"""Top equipment lid, open-topped bottom cap and internal B-fill bend holder.
Rigid seats retain their printed-face clearances; exterior foil tape seals the
cold core's dry casing seams.
"""

import argparse
import math
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_printed = next(p for p in _here.parents if p.name == "printed-parts")
sys.path.insert(0, str(_printed / "cadlib"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(0, str(_here.parent))
# How this machine holds a Beduan on a printed face — the cap prints it rather than restating it.
sys.path.insert(0, str(_printed / "valve-seat"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

if __name__ == '__main__':
    import _rust_part
    _rust_part.start()

import fits
import _materials as _mat
import valve_seat as seat
import _above_core_mounts as _above_mounts
import _reservoir_a_anchors as _a_anchors
import above_core_wiring
import _reservoir_ports as reservoir_ports
import _reservoir_b_fill
from _foam_cap import head_pad_growth, lid_cut_through_depth, lid_total_height, top_cap_height
from _cold_core_interface import cap_conduit_links, cap_conduit_link_width
from _cold_core_interface import attachment_xy_positions, cap_shell_clearance, cap_lid_clearance, wall_and_floor_thickness, corner_round_radius, foam_cap_lid_pour_radius, foam_cap_lid_pour_xy, foam_cap_lid_vent_radius, foam_cap_lid_vent_xy, head_pad_height, screw_clearance_radius, head_cbore_radius, head_cbore_depth, deck_mounts, deck_mount_cap_gap, deck_mount_xy, deck_mount_boss_radius, deck_mount_bore_radius, deck_mount_bore_depth, deck_mount_standoff, deck_lid_hole_radius, cap_conduits, cap_conduit_bore_radius, cap_conduit_boss_radius, cap_conduit_entry_relief_radius, cap_cradles, cap_cradle_boss_radius, cap_cradle_socket_radius, cap_cradle_wall, cap_cradle_room_gap, cap_cradle_half_x, cap_cradle_half_y, cap_anchors, cap_anchor_axis_over_face, cap_side_anchors, cap_side_anchor_height, cap_side_anchor_holds, cap_side_axis_y, cap_side_tunnel_h, cap_side_tunnel_roof, cap_side_back_relief, cap_side_cav_w, cap_side_flank, cap_side_len, cap_side_wall, cap_anchor_cav_w, cap_anchor_cav_wall, cap_anchor_len, cap_anchor_wall, cap_anchor_channel_height, outer_shell_wall, outer_shell_x_length, outer_shell_y_length
from docgen import substitute_py_comments


def deck_boss_z_top(name):
    """PCB bearing plane above the uniformly thick lid."""
    return lid_total_height + deck_mount_standoff(name)


def numbers():
    """Current lid mounts, cap stock and routing datums, without native solids."""
    import itertools
    import _cold_core_interface as core
    import _reservoir_a_c2 as a_snap
    import above_core_routes
    import rear_snaps
    from _materials import linear
    root = next(p for p in _here.parents if (p / 'hardware').is_dir())
    sys.path.insert(0, str(root))
    from hardware.wiring.installed.retainers import manifold_bank_site, rear_level_hook_site

    layout = _above_mounts.above_core
    pose = layout.cap_lid_pose()
    world_origin = layout.world_to_cap((0., 0., 0.))
    world_axes = [tuple(b-a for a, b in zip(world_origin, layout.world_to_cap(axis)))
                  for axis in ((1., 0., 0.), (0., 1., 0.), (0., 0., 1.))]
    pump = _above_mounts.pump_cradle_datums()
    b_fill = _reservoir_b_fill.passage()
    r = _reservoir_b_fill.CHANNEL_RADIUS
    centre = _reservoir_b_fill.CHANNEL_CENTRE
    outer = r + _reservoir_b_fill.WALL
    height = centre + _reservoir_b_fill.DOME_LIFT + outer
    x, y, z = b_fill['bend_end_world_mm']
    bend = _reservoir_b_fill.BEND_RADIUS
    guide_world_bounds = ((x+centre-height, x+centre),
                          (y-bend, y+outer), (z+bend-outer, z+bend+outer))
    corners = [layout.world_to_cap(p) for p in itertools.product(*guide_world_bounds)]
    guide_bounds = [[min(p[i] for p in corners) for i in range(3)],
                    [max(p[i] for p in corners) for i in range(3)]]
    spec = layout.specification()
    va = spec['fore_routes']['va_feed_snap']
    clips = [dict(centre=va['centre_world_mm'], along=va['along_world'],
                  radius=6.35/2., wing=2.4, span=8.,
                  tip_degrees=125.42102606277044)]
    clips += [dict(centre=p, along=u, radius=4.1/2., wing=1.52, span=8.,
                   tip_degrees=125.42102606277044)
              for p, u in (((26.5,266.,296.),(1.,0.,0.)),
                           ((35.,414.,264.),(0.,1.,0.)))]
    a_spec = a_snap.specification()
    clips += [dict(centre=p, along=a_spec['tube_axis_world'],
                   radius=a_spec['seat_radius_mm'], wing=a_spec['spring_thickness_mm'],
                   span=a_spec['station_length_mm'], tip_degrees=a_spec['tip_degrees'])
              for p in a_spec['tube_centers_world_mm']]
    wells = []
    for name, placement in above_core_wiring.placements().items():
        if placement['parent'] != 'cold-core':
            continue
        wells.append(dict(name=name, pose=placement,
                          size=above_core_wiring.SIZES[placement['size']]))
    return {
        'width': core.outer_shell_x_length, 'depth': core.outer_shell_y_length,
        'corner': core.corner_round_radius, 'wall': core.outer_shell_wall,
        'floor': core.wall_and_floor_thickness, 'lid_height': lid_total_height,
        'bottom_height': core.bottom_cap_height, 'head_radius': core.head_cbore_radius,
        'head_depth': core.head_cbore_depth, 'screw_radius': core.screw_clearance_radius,
        'boss_radius': core.screw_boss_size/2., 'head_pad_growth': head_pad_growth,
        'supported_surface': fits.supported_surface, 'running': fits.running, 'slip': fits.slip,
        'bottom_stations': [{'xy':xy, 'wall':wall} for xy,wall in core.attachment_stations],
        'top_stations': [{'xy':xy, 'wall':wall} for xy,wall in core.lid_attachment_stations],
        'bottom_holes': [{'xy':xy,'radius':core.bottom_pour_radius}
                         for xy in core.bottom_pour_positions] +
                        [{'xy':xy,'radius':core.foam_cap_lid_vent_radius}
                         for xy in core.foam_cap_lid_vent_xy(top=False)],
        'air_holes': [{'xy':[-v for v in xy], 'radius':reservoir_ports.air_passage_diameter/2.}
                      for xy in reservoir_ports.air_position.values()],
        'conduits': {name:xy for name,xy in core.cap_conduits.items()
                     if name not in ('reservoir-b-fill','water-in','carb-water-out')},
        'reliefs': {name:xy for name,xy in core.cap_conduits.items()
                    if name not in ('reservoir-b-fill','water-in','sensor-cable',*core.cap_conduit_bore_radii)},
        'conduit_radius': core.cap_conduit_bore_radius,
        'conduit_radii': core.cap_conduit_bore_radii,
        'relief_radius': core.cap_conduit_entry_relief_radius,
        'deck_columns': [{'xy':xy, 'top':deck_boss_z_top(name)}
                         for name in core.deck_mounts for xy in core.deck_mount_xy(name)],
        'deck_radius': core.deck_mount_boss_radius,
        'deck_bore_radius': core.deck_mount_bore_radius,
        'deck_bore_depth': core.deck_mount_bore_depth,
        'straight_guides': [{'point':spec['cap_guides_world_mm'][name],
                            'floor':pose['translation_mm'][2]-top_cap_height}
                            for name in ('water-in','carb-water-out')],
        'world_to_cap_origin': world_origin, 'world_to_cap_axes': world_axes,
        'cap_face_world_z': spec['cap_face_z_mm'],
        'pump': pump,
        'snap': {name:getattr(rear_snaps,name) for name in ('WING','REACH','LEDGE','HOOK','CATCH')},
        'valve_wall': _above_mounts.valve_support_datums('valve-v-b',lid_total_height),
        'valve_pose': layout.pose('valve-v-b'),
        'valve': {key:getattr(seat,key) for key in ('corner_inset_x','corner_inset_y',
                   'socket_radius','socket_floor_z','seat_top_z','seat_half_y','port_air')},
        'valve_port_radius': seat.valve.port_radius,
        'valve_port_z': seat.valve.port_center_z,
        'union_supports': _above_mounts.union_support_datums(),
        'wells': wells, 'well_wall': above_core_wiring.WALL, 'well_fit': above_core_wiring.FIT,
        'a_seats': _a_anchors.datums(), 'a_seat_spec': _a_anchors.specification(),
        'a_snap': a_spec,
        'a_routes': {name:row['segments'] for name,row in
                     above_core_routes.reservoir_a_route_specs().items()},
        'tube_clips': clips, 'flavor_wall': _above_mounts.valve_support_datums('valve-v-b'),
        'cable_bank': manifold_bank_site(), 'cable_hook': rear_level_hook_site(),
        'b_fill': {'bend':bend, 'radius':r, 'centre':centre, 'outer':outer,
                   'dome_lift':_reservoir_b_fill.DOME_LIFT,
                   'inlet':y-bend-b_fill['entry_world_mm'][1],
                   'mouth':_reservoir_b_fill.MOUTH,
                   'mouth_start':-.3, 'mouth_end':_reservoir_b_fill.MOUTH+.05,
                   'end_world':[x,y,z], 'guide_bounds_cap':guide_bounds},
        'colors': {'foam-cap-lid-top':linear(_mat.C_CAP_LID_TOP),
                   'foam-cap-bottom':linear(_mat.C_CAP_BOTTOM),
                   'reservoir-b-fill-guide':linear(_mat.C_CAP_TOP),
                   'pump-snap-cap':linear(_mat.M_PETGF_BLACK)},
    }


def main(output=_here):
    import _rust_part
    import flute_payload
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    _rust_part.cut('cold-core', 'foam-cap', numbers(), output)
    for name in ('foam-cap-lid-top','foam-cap-bottom','reservoir-b-fill-guide','pump-snap-cap'):
        flute_payload.cut(output/f'{name}.step',output/f'{name}.stl',
                          preserve_print_triangles=name == 'pump-snap-cap')
    for name in ('foam-cap-top','foam-cap-lid-bottom','pump-snap-cap-rear'):
        for suffix in ('.step','.step.mesh','.stl'):
            (output/f'{name}{suffix}').unlink(missing_ok=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=_here)
    args = parser.parse_args()
    main(args.output)
