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

import cadquery as cq
from world_workplane import (WorldWorkplane, xy_plane_z_up, xz_plane_y_up,
                             yz_plane_x_up)
import fits
from _cadq_export import export_assembly
from _show_skin import write_bed_file
import _materials as _mat
from _materials import one_body
import valve_seat as seat
import _foam_cap as _foam_cap_module
import _above_core_mounts as _above_mounts
import _reservoir_a_anchors as _a_anchors
import above_core_wiring
import _reservoir_ports as reservoir_ports
import _reservoir_b_fill
from _foam_cap import (
    build_bottom_cap,
    build_foam_cap_lid,
    head_access_pockets,
    head_pad_growth,
    lid_cut_through_depth,
    lid_total_height,
    top_cap_height,
)
from _outer_shell import build_attachment_bosses
from _cold_core_interface import cap_conduit_links, cap_conduit_link_width
from _cold_core_interface import (
    build_z_axis_hole_punch,
    attachment_xy_positions,
    cap_shell_clearance,
    cap_lid_clearance,
    wall_and_floor_thickness,
    corner_round_radius,
    foam_cap_lid_pour_radius,
    foam_cap_lid_pour_xy,
    foam_cap_lid_vent_radius,
    foam_cap_lid_vent_xy,
    head_pad_height,
    screw_clearance_radius,
    head_cbore_radius,
    head_cbore_depth,
    deck_mounts,
    deck_mount_cap_gap,
    deck_mount_xy,
    deck_mount_boss_radius,
    deck_mount_bore_radius,
    deck_mount_bore_depth,
    deck_mount_standoff,
    deck_lid_hole_radius,
    cap_conduits,
    cap_conduit_bore_radius,
    cap_conduit_boss_radius,
    cap_conduit_entry_relief_radius,
    cap_cradles,
    cap_cradle_boss_radius,
    cap_cradle_socket_radius,
    cap_cradle_wall,
    cap_cradle_room_gap,
    cap_cradle_half_x,
    cap_cradle_half_y,
    cap_anchors,
    cap_anchor_axis_over_face,
    cap_side_anchors,
    cap_side_anchor_height,
    cap_side_anchor_holds,
    cap_side_axis_y,
    cap_side_tunnel_h,
    cap_side_tunnel_roof,
    cap_side_back_relief,
    cap_side_cav_w,
    cap_side_flank,
    cap_side_len,
    cap_side_wall,
    cap_anchor_cav_w,
    cap_anchor_cav_wall,
    cap_anchor_len,
    cap_anchor_wall,
    cap_anchor_channel_height,
    outer_shell_wall,
    outer_shell_x_length,
    outer_shell_y_length,
)
import _anchor_cap_interface as _anchor_cap
from docgen import substitute_py_comments


def _ring(section):
    """A section's own points with the first repeated, so the closing edge is DRAWN.

    `close()` infers it instead, from the last edge's end read back off OCCT — a few 1e-16 off
    the point that was passed in — and a tangential boolean downstream resolves that vertex one
    way in one process and the other way in the next. Naming the point is what makes the same
    source write the same bytes."""
    pts = list(section)
    return pts if pts[0] == pts[-1] else pts + [pts[0]]


def deck_boss_z_top(name):
    """PCB bearing plane above the uniformly thick lid."""
    return lid_total_height + deck_mount_standoff(name)


def add_deck_mounts(lid):
    """Four lid-rooted PCB columns with blind full-length M3 insert pilots."""
    for name in deck_mounts:
        top = deck_boss_z_top(name)
        for x,y in deck_mount_xy(name):
            column = cq.Solid.makeCylinder(deck_mount_boss_radius,top-lid_total_height+.1,
                cq.Vector(x,y,lid_total_height-.1))
            bore = cq.Solid.makeCylinder(deck_mount_bore_radius,deck_mount_bore_depth+.1,
                cq.Vector(x,y,top-deck_mount_bore_depth))
            lid = lid.union(column).cut(bore)
    return lid


def cradle_shape(name, face_z):
    """One socketed valve plinth, with the lid conduits open along its edge."""
    station = cap_cradles[name]
    cx, cy = station.centre
    plinth = (seat.build_seat(max(station.seat, -seat.socket_floor_z))
              .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), station.yaw + 90.0)
              .translate((cx, cy, face_z + station.seat)))
    if station.seat < -seat.socket_floor_z:
        # The plate carries the recessed socket floors. This part is only the
        # material above its outer face; add_cradles cuts the complete sockets.
        depth = -seat.socket_floor_z - station.seat
        below = (cq.Workplane("XY").workplane(offset=face_z-depth-1.0)
                 .center(cx, cy).rect(2.0*cap_cradle_half_y+2.0,
                                     2.0*cap_cradle_half_x+2.0)
                 .extrude(depth+1.0))
        plinth = plinth.cut(below)
    for x, y in cap_conduits.values():
        passage = (WorldWorkplane(xy_plane_z_up).workplane(offset=face_z)
                   .center(x, y)
                   .circle(cap_conduit_entry_relief_radius + cap_cradle_room_gap)
                   .extrude(station.seat + seat.seat_top_z + 1.0).unwrap())
        plinth = plinth.cut(passage)
    return plinth


def add_cradles(lid, face_z):
    """Three plinths joined to the lid, with port channels on each valve's axis."""
    for name, station in cap_cradles.items():
        lid = lid.union(cradle_shape(name, face_z))
        if station.seat < -seat.socket_floor_z:
            floor = face_z + station.seat + seat.socket_floor_z
            assert floor >= cap_cradle_wall - 1e-9, (
                f"cradle {name} leaves only {floor:g} mm under its sockets")
            sockets = (seat.build_sockets()
                       .rotate((0,0,0), (0,0,1), station.yaw+90.0)
                       .translate((*station.centre, face_z+station.seat)))
            lid = lid.cut(sockets)
    return lid


def capped_lid_rib(lid, name, face_z):
    """A capped row's rib on the lid at `face_z`: the anchor cap's own post
    (`_anchor_cap_interface.rib`), struck in the row's frame — along its own axis, rooted on the
    lid — fused on, then its two catch windows and, where the lid stands inside the cap's wings,
    the wings' two slots cut (`wing_room`). Each window runs from its bearing face to where its
    flank ends: the slot's floor where the lid gives the wings room, the lid's face otherwise."""
    row = cap_anchors[name]
    (cx, cy) = row.centre
    b_face = cap_anchor_axis_over_face(name)
    frame = _anchor_cap.Frame((cx, cy, face_z + b_face),
                              (1.0, 0.0, 0.0) if row.along == "x" else (0.0, 1.0, 0.0),
                              (0.0, 0.0, -1.0))
    lid = lid.union(_anchor_cap.rib(frame, b_face, row.seat_r).clean())
    for cutter in (_anchor_cap.windows(frame, _anchor_cap.window_top(b_face))
                   + _anchor_cap.wing_room(frame, b_face)):
        lid = lid.cut(cutter)
    return lid


def add_chain_anchors(lid, face_z, names=None):
    """Every chain anchor, standing on the lid's outer face at `face_z`.

    A ROW THE ANCHOR CAP CLOSES is the cap's own rib (`capped_lid_rib`) and takes none of what
    follows.

    THE CHANNEL IS A REMAINDER: the rib stands `cap_anchor_channel_height` over the face down its whole
    length and only its two ends carry on down to meet it, so the zip tie's channel is the room
    between those ends. The lid's own face is the channel's floor and the rib's underside is its
    roof — neither is drawn, and there is no cut anywhere in it to graze a face with.

    THE ZIP TIE CLOSES ROUND THE BODY AND THE RIB'S OWN BACK TOGETHER: through the channel, out one
    flank, over the far side of the body and back in the other. What it pulls is the body down
    into the bore, and the bore is what says where the body is.

    The lower box runs the rib's whole length so the seat's own lip is ONE edge, and the rib is
    UNIFIED before it joins the lid — a fuse imprints the seam of every solid that went into it,
    so a rib fused straight onto the plate carries its lip in as many pieces as it was laid down
    in, and its bore in as many again."""
    for name, station in cap_anchors.items():
        if names is not None and name not in names:
            continue
        if station.closure == "cap":
            lid = capped_lid_rib(lid, name, face_z)
            continue
        (cx, cy) = station.centre
        seat_r = station.seat_r
        reach = seat_r + cap_anchor_wall
        axis_z = face_z + cap_anchor_axis_over_face(name)
        x0 = cx - cap_anchor_len / 2.0

        def block(xa, length, za, zb):
            return (
                WorldWorkplane(yz_plane_x_up)
                .workplane(offset=xa)
                .polyline(_ring([(cy - reach, za), (cy + reach, za),
                                 (cy + reach, zb), (cy - reach, zb)]))
                .wire()
                .extrude(length)
            )

        rib = block(x0, cap_anchor_len, face_z + cap_anchor_channel_height, axis_z)
        for s0, s1 in ((0.0, cap_anchor_cav_wall),
                       (cap_anchor_cav_wall + cap_anchor_cav_w, cap_anchor_len)):
            rib = rib.union(block(x0 + s0, s1 - s0, face_z, face_z + cap_anchor_channel_height))
        bore = (
            WorldWorkplane(yz_plane_x_up)
            .workplane(offset=x0)
            .pushPoints([(cy, axis_z)])
            .circle(seat_r)
            .extrude(cap_anchor_len)
        )
        lid = lid.union(rib.cut(bore).clean().val())

    return lid


def add_side_anchors(lid, face_z, names=None):
    """Every SIDEWAYS anchor, standing on the lid's outer face at `face_z`.

    A post ACROSS the run rather than along it: its forward face is the run's own axis plane, a
    half pipe is cut into that face, and the tube is pushed in horizontally.

    ONE BLOCK AND THREE CUTS. The pipe is cut as a full cylinder and the block stops at the axis
    plane, so what is left is a half pipe whose lip is one edge and not two. The tie's tunnel is
    a WINDOW cut through under it, hung off its own roof (`cap_side_tunnel_h`) with the post's
    stock standing under it, so what prints below the pipe is one block and not two blades. The
    tie's channel down the back face is the third, and it runs the window's floor to the crown —
    which is the whole of what the zip tie climbs.

    The post is unified before it joins the lid, for the reason the up-opening ribs are: a fuse
    imprints the seam of every solid that went into it."""
    for name, station in cap_side_anchors.items():
        if names is not None and name not in names:
            continue
        cap_side_anchor_holds(name)
        (cx, cy) = station.centre
        seat_r = station.seat_r
        depth = station.depth
        axis_z = face_z + station.over_face
        roof_z = face_z + cap_side_tunnel_roof(name)  # the window's roof, one wall under the pipe
        sill_z = roof_z - cap_side_tunnel_h(name) - fits.supported_surface
        top_z = face_z + cap_side_anchor_height(name)
        y0 = cy - cap_side_len / 2.0                 # the post's ends, along the run

        def block(ya, length, za, zb):
            """One slab of the post: `length` of it along the run, spanning z."""
            return (
                WorldWorkplane(xy_plane_z_up)
                .workplane(offset=za)
                .polyline(_ring([(cx, ya), (cx - depth, ya),
                                 (cx - depth, ya + length), (cx, ya + length)]))
                .wire()
                .extrude(zb - za)
            )

        post = block(y0, cap_side_len, face_z, top_z)
        # THE TIE'S WINDOW, cut front to back under the pipe and closed on every side but its two
        # mouths. One wall of the post is its roof and the post's own stock its floor, so the
        # zip tie lies against the material it pulls and the column under it is never opened.
        tunnel = (
            WorldWorkplane(xy_plane_z_up)
            .workplane(offset=sill_z)
            .polyline(_ring([(cx, cy - cap_side_cav_w / 2.0),
                             (cx - depth, cy - cap_side_cav_w / 2.0),
                             (cx - depth, cy + cap_side_cav_w / 2.0),
                             (cx, cy + cap_side_cav_w / 2.0)]))
            .wire()
            .extrude(roof_z - sill_z)
        )
        # The pipe runs ALONG the post, which is the cap's own Y — so its plane is the one whose
        # normal is Y, and the offset that walks it is the post's own end. Its axis stands
        # `axis_off` FORWARD of the post's front face, so what the cut leaves in that face is a
        # seat shallower than a half pipe and the tube beds into it from the room.
        bore = (
            WorldWorkplane(xz_plane_y_up)
            .workplane(offset=y0)
            .center(cap_side_axis_y(name), axis_z + fits.supported_surface / 2.0)
            .slot2D(2.0 * seat_r + fits.supported_surface, 2.0 * seat_r, angle=90)
            .extrude(cap_side_len)
        )
        # THE TIE'S OWN CHANNEL DOWN THE BACK, on the window's own width and over its mouth, so
        # the zip tie leaves the window and climbs the post in one line and the buckle sits in it.
        # It stops on the window's floor: below that the tie has left the post, and a channel
        # carried on down to the lid would groove the column for nothing that runs in it.
        relief = (
            WorldWorkplane(xy_plane_z_up)
            .workplane(offset=sill_z)
            .polyline(_ring([
                (cx - depth + cap_side_back_relief, cy - cap_side_cav_w / 2.0),
                (cx - depth, cy - cap_side_cav_w / 2.0),
                (cx - depth, cy + cap_side_cav_w / 2.0),
                (cx - depth + cap_side_back_relief, cy + cap_side_cav_w / 2.0)]))
            .wire()
            .extrude(top_z - sill_z)
        )
        lid = lid.union(post.cut(bore).cut(tunnel).cut(relief).clean().val())
        # Low anchors use the lid as the tunnel floor; the cutter reaches its
        # surface only after the post joins it. Tall anchors keep their plinth.
        lid = lid.cut(tunnel.val())
    return lid


def _joining_slot(a, b, width, z0, z1):
    """A straight slot of `width` between two hole centres, `z0` to `z1`."""
    (ax, ay), (bx, by) = a, b
    return (cq.Workplane("XY")
            .box(math.dist(a, b), width, z1 - z0, centered=(True, True, False))
            .rotate((0, 0, 0), (0, 0, 1), math.degrees(math.atan2(by - ay, bx - ax)))
            .translate(((ax + bx) / 2, (ay + by) / 2, z0)))



def casing_outline(z0, z1):
    """The plain lid footprint, between two heights."""
    return (WorldWorkplane(xy_plane_z_up).workplane(offset=z0)
            .rect(outer_shell_x_length, outer_shell_y_length)
            .extrude(z1 - z0).edges("|Z")
            .fillet(corner_round_radius)).unwrap().val()


def build_top_lid():
    """Equipment passages, integral V-B wall and board-facing wiring wells."""
    lid = add_side_anchors(
        add_chain_anchors(
            add_cradles(add_deck_mounts(build_foam_cap_lid()), lid_total_height),
            lid_total_height, names=tuple(n for n in cap_anchors if n != 'discharge-chain')),
        lid_total_height)
    lid = lid.union(_above_mounts.world_shape_in_cap(_above_mounts.pump_cradle()))
    for name in ('valve-v-b',):
        lid = lid.union(_above_mounts.valve_support(name,lid_total_height))
    for support in _above_mounts.union_supports().values():
        lid = lid.union(support)
    for passage in _above_mounts.union_support_cuts().values():
        lid = lid.cut(passage)
    electrical = above_core_wiring.cap_features()
    # Wiring wells keep to the plain casing footprint.
    electrical_stock = _above_mounts.world_shape_in_cap(electrical['add'])
    lid = lid.union(electrical_stock.intersect(
        casing_outline(-1.0, electrical_stock.BoundingBox().zmax+1.0)))
    lid = lid.cut(_above_mounts.world_shape_in_cap(electrical['cut']))
    for support in _a_anchors.supports().values():
        lid = lid.union(_above_mounts.world_shape_in_cap(support))
    for passage in _a_anchors.cuts().values():
        lid = lid.cut(_above_mounts.world_shape_in_cap(passage))
    lid = lid.union(_above_mounts.world_shape_in_cap(_above_mounts.va_feed_snap()))
    for support in _above_mounts.flavor_snaps().values():
        lid = lid.union(_above_mounts.world_shape_in_cap(support))
    lid = lid.union(_above_mounts.world_shape_in_cap(_above_mounts.manifold_cable_bank()))
    lid = lid.union(_above_mounts.world_shape_in_cap(_above_mounts.rear_level_cable_hook()))
    # Cut the pump's straight clearance room through all joined lid stock.
    lid = lid.cut(_above_mounts.world_shape_in_cap(_above_mounts.pump_lid_clearance()))
    # The straight air passages continue through all joined equipment stock.
    return cut_reservoir_air_bores(lid, -.1, lid.val().BoundingBox().zmax + .1).clean()


def cut_reservoir_air_bores(shape, z0, z1):
    """Straight air-tube passages in this cap's pre-install half-turn frame."""
    for shell_xy in reservoir_ports.air_position.values():
        xy = tuple(-v for v in shell_xy)
        shape = shape.cut(reservoir_ports.cylinder(
            xy, z0, z1, reservoir_ports.air_passage_diameter))
    return shape



def native_main(output=_here):
    import flute_payload
    lid_top = build_top_lid()
    cap_bottom = build_bottom_cap()
    for shape,name,colour in (
        (lid_top,'foam-cap-lid-top',_mat.C_CAP_LID_TOP),
        (cap_bottom,'foam-cap-bottom',_mat.C_CAP_BOTTOM),
        (_reservoir_b_fill.guide_native(),'reservoir-b-fill-guide',_mat.C_CAP_TOP),
        (_above_mounts.pump_snap_printable(),'pump-snap-cap',_mat.M_PETGF_BLACK)):
        export_assembly(one_body(shape,name,colour),str(output/f'{name}.step'))
        write_bed_file(shape,output/f'{name}.stl')
        flute_payload.cut(output/f'{name}.step',output/f'{name}.stl',
                          preserve_print_triangles=name.startswith('pump-snap-cap'))
        print(f'-> {name}.step / .stl')
    for name in ('foam-cap-top','foam-cap-lid-bottom','pump-snap-cap-rear'):
        for suffix in ('.step','.step.mesh','.stl'):
            (output/f'{name}{suffix}').unlink(missing_ok=True)


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
    parser.add_argument('--native', action='store_true', help='Run the retained native builders')
    parser.add_argument('--output', type=Path, default=_here)
    args = parser.parse_args()
    (native_main if args.native else main)(args.output)
