"""Foam-cap tray and pour lid at each end of the cold-core shell.
Rigid seats retain their printed-face clearances; exterior foil tape
seals the dry casing seams."""

import itertools
import cadquery as cq
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

from world_workplane import (WorldWorkplane, xy_plane_z_up, xz_plane_y_up,
                             yz_plane_x_up)
import fits
from _cadq_export import export_assembly
from _show_skin import write_bed_file, piece_mesh
import _materials as _mat
from _materials import one_body
import valve_seat as seat
import _foam_cap as _foam_cap_module
import _above_core_mounts as _above_mounts
import _reservoir_a_anchors as _a_anchors
import above_core_wiring
from _foam_cap import (
    build_foam_cap,
    build_foam_cap_lid,
    head_access_pockets,
    head_pad_growth,
    lid_cut_through_depth,
    lid_total_height,
    top_cap_height,
)
from _outer_shell import build_attachment_bosses, rebate_casing_seals
from _cold_core_interface import cap_conduit_links, cap_conduit_link_width
from _cold_core_interface import (
    build_z_axis_hole_punch,
    attachment_xy_positions,
    cap_shell_clearance,
    cap_lid_clearance,
    casing_seal_rebate,
    wall_and_floor_thickness,
    corner_round_radius,
    flute_depth,
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


# The lid's own footprint, as area: the shell's rectangle less what its four corner rounds take
# out of it. Every plate in this stack is cut to it, and the two lids' plates differ by nothing
# else.
footprint_area = ((outer_shell_x_length - 2 * casing_seal_rebate)
                  * (outer_shell_y_length - 2 * casing_seal_rebate)
                  - (4.0 - math.pi) * (corner_round_radius - casing_seal_rebate) ** 2)
# The pour hole and the two vents, as one area. Neither lid carries anything else through its
# plate that the other does not, so this is the whole of what the two have in common there.
lid_open_area = (math.pi * foam_cap_lid_pour_radius ** 2
                 + 2.0 * math.pi * foam_cap_lid_vent_radius ** 2)




def _ring(section):
    """A section's own points with the first repeated, so the closing edge is DRAWN.

    `close()` infers it instead, from the last edge's end read back off OCCT — a few 1e-16 off
    the point that was passed in — and a tangential boolean downstream resolves that vertex one
    way in one process and the other way in the next. Naming the point is what makes the same
    source write the same bytes."""
    pts = list(section)
    return pts if pts[0] == pts[-1] else pts + [pts[0]]


def _circle_beyond(d, r):
    """The area of a circle of radius `r` lying beyond a chord its centre stands `d` from —
    signed, so a centre on the far side of that line (`d` < 0) reports most of the circle."""
    if d >= r:
        return 0.0
    if d <= -r:
        return math.pi * r ** 2
    return r * r * math.acos(d / r) - d * math.sqrt(max(r * r - d * d, 0.0))


def _conduit_wall_overlap_area(x, y):
    """The part of one column's section that is ALREADY the cup's perimeter wall.

    A column merged into that wall (`_cold_core_interface.cap_conduit_wall_neck`) adds only
    what stands INBOARD of the cavity face — the rest of its circle is wall the cup already
    carried, and counting it twice is what makes the stack's volume disagree with its parts.
    A column may merge into one face and no more: two at once is a corner, where the cup's
    own fillet is, and the section there is not this figure."""
    over = [d for d in (outer_shell_x_length / 2.0 - outer_shell_wall - abs(x),
                        outer_shell_y_length / 2.0 - outer_shell_wall - abs(y))
            if d < cap_conduit_boss_radius]
    assert len(over) <= 1, (
        f"cap conduit at ({x:g}, {y:g}) merges into two walls at once — that is the cup's "
        f"filleted corner, and a circle-and-chord does not describe the section there")
    return _circle_beyond(over[0], cap_conduit_boss_radius) if over else 0.0


def _conduit_section_area():
    """The conduit columns' section as ONE figure — the union of their circles, less the
    part of any of them the perimeter wall already holds.

    Where two columns overlap they are a single post, so the lens they share is area the
    pack holds once. `build_conduit_columns` unions them for the same reason."""
    r = cap_conduit_boss_radius
    centres = list(cap_conduits.values())
    area = len(centres) * math.pi * r ** 2
    for i, a in enumerate(centres):
        for b in centres[i + 1:]:
            d = math.dist(a, b)
            if d < 2.0 * r:
                area -= (2.0 * r ** 2 * math.acos(d / (2.0 * r))
                         - (d / 2.0) * math.sqrt(4.0 * r ** 2 - d ** 2))
    # The named links join separated columns inside the cup. Each rectangle's
    # exposed area is its length times width, less the two circular end strips.
    # Their added sections do not overlap each other or the perimeter wall.
    half = cap_conduit_link_width / 2.0
    end_strip = half * math.sqrt(r * r - half * half) + r * r * math.asin(half / r)
    for first, second in cap_conduit_links:
        area += math.dist(cap_conduits[first], cap_conduits[second]) * cap_conduit_link_width - 2 * end_strip
    return area - sum(_conduit_wall_overlap_area(*c) for c in centres)


def deck_boss_z_top(name):
    """A deck mount's column tops, off the cap's floor. A flush mount stops at the mouth
    rim, under the lid; a standing one carries the whole cup, the lid that closes it,
    and its standoff. Same section the whole way, standing on the floor's cavity side —
    the cap prints floor-down, and each column rises off the bed like the screw
    bosses beside it."""
    standoff = deck_mount_standoff(name)
    if standoff == 0.0:
        return top_cap_height - cap_lid_clearance
    return top_cap_height + lid_total_height + standoff


def add_deck_mounts(cap):
    """The electronics' boss columns, standing on the top cap's floor. Each carries a
    blind bore at its top for a heat-set insert; foam pours around the shanks, so the
    column is the module's only root."""
    for name in deck_mounts:
        z_top = deck_boss_z_top(name)
        for x, y in deck_mount_xy(name):
            column = (
                WorldWorkplane(xy_plane_z_up)
                .workplane(offset=wall_and_floor_thickness)
                .moveTo((x, y))
                .circle(deck_mount_boss_radius)
                .extrude(z_top - wall_and_floor_thickness)
                .unwrap()
            )
            cap = cap.union(column).cut(
                build_z_axis_hole_punch(
                    origin=(x, y, z_top - deck_mount_bore_depth),
                    hole_punch_radius=deck_mount_bore_radius,
                    hole_punch_height=deck_mount_bore_depth,
                )
            )
    return cap


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


def capped_lid_rib_volume(name):
    """What a capped row adds to the lid, in closed form: the post from the face to the axis
    plane less its half bore and its two lip-ride chamfers, less each window's share of the
    post, less what each window and slot take out of the plate under it."""
    a = _anchor_cap
    b_face = cap_anchor_axis_over_face(name)
    post = a.RIB_LEN * (2.0 * a.RIB_R * b_face - a.RIB_CHAMFER ** 2
                        - 0.5 * math.pi * cap_anchors[name].seat_r ** 2)
    in_post = 2.0 * a.WINDOW_DEPTH * (b_face - a.WINDOW_B0) * a.WINDOW_LEN
    in_plate = (2.0 * (a.WINDOW_DEPTH + a.SLOT_W) * (a.SLOT_TOP - b_face) * a.WINDOW_LEN
                if b_face < a.SLOT_TOP - a.HEADROOM / 2.0 else 0.0)
    return post - in_post - in_plate


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


def cradle_anchor_intersections(face_z):
    """Actual shared material between valve seats and the lid's tube anchors."""
    rows = []
    for valve in cap_cradles:
        plinth = cradle_shape(valve, face_z).val()
        for anchor in cap_anchors:
            rib = add_chain_anchors(cq.Workplane('XY'), face_z, (anchor,)).val()
            shared = plinth.intersect(rib)
            volume = shared.Volume()
            if volume <= 0.001:
                continue
            b = shared.BoundingBox()
            rows.append({'valve': valve, 'anchor': anchor, 'volume_mm3': volume,
                         'bounds_cap_mm': [[b.xmin, b.ymin, b.zmin],
                                           [b.xmax, b.ymax, b.zmax]]})
        for anchor in cap_side_anchors:
            rib = add_side_anchors(cq.Workplane('XY'), face_z, (anchor,)).val()
            shared = plinth.intersect(rib)
            volume = shared.Volume()
            if volume <= 0.001:
                continue
            b = shared.BoundingBox()
            rows.append({'valve': valve, 'anchor': anchor, 'volume_mm3': volume,
                         'bounds_cap_mm': [[b.xmin, b.ymin, b.zmin],
                                           [b.xmax, b.ymax, b.zmax]]})
    return rows


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


def cut_deck_mounts_lid(lid):
    """The lid's opening at every deck-mount station — a standing column passes it, and a
    flush one meets its underside with only the screw crossing.

    A column hole that leaves less than the pour gap beside a clamp screw's head pocket
    opens into that screw's stations instead: a slot of the clearance hole's width
    through the plate and one of the pocket's width above its floor, so no web or cusp
    is left between the two."""
    head_floor = lid_total_height - head_cbore_depth
    for name in deck_mounts:
        radius = deck_lid_hole_radius(name)
        for x, y in deck_mount_xy(name):
            lid = lid.cut(
                build_z_axis_hole_punch(
                    origin=(x, y, 0),
                    hole_punch_radius=radius,
                    hole_punch_height=lid_cut_through_depth,
                )
            )
            for station in attachment_xy_positions:
                if math.dist((x, y), station) - radius - head_cbore_radius >= deck_mount_cap_gap:
                    continue
                lid = (lid.cut(_joining_slot(station, (x, y), 2.0 * screw_clearance_radius,
                                             -1.0, lid_cut_through_depth))
                       .cut(_joining_slot(station, (x, y), 2.0 * head_cbore_radius,
                                          head_floor, lid_cut_through_depth)))
    return lid


def rebated_outline(z0, z1):
    """The lid's foil-land outline, `z0` to `z1`: the bare footprint less the casing seal
    rebate all round."""
    return (WorldWorkplane(xy_plane_z_up).workplane(offset=z0)
            .rect(outer_shell_x_length - 2 * casing_seal_rebate,
                  outer_shell_y_length - 2 * casing_seal_rebate)
            .extrude(z1 - z0).edges("|Z")
            .fillet(corner_round_radius - casing_seal_rebate)).unwrap().val()


def build_top_lid():
    """Equipment passages, integral V-B wall and upward-access wiring wells."""
    lid = add_side_anchors(
        add_chain_anchors(
            add_cradles(cut_deck_mounts_lid(build_foam_cap_lid()), lid_total_height),
            lid_total_height, names=tuple(n for n in cap_anchors if n != 'discharge-chain')),
        lid_total_height)
    for name in ('valve-v-b',):
        lid = lid.union(_above_mounts.valve_support(name,lid_total_height))
    lid = lid.union(_above_mounts.check_support())
    for support in _above_mounts.union_supports().values():
        lid = lid.union(support)
    for passage in _above_mounts.union_support_cuts().values():
        lid = lid.cut(passage)
    electrical = above_core_wiring.cap_features()
    # The wiring wells keep to the lid's rebated outline, so the foil land runs past them.
    lid = lid.union(_above_mounts.world_shape_in_cap(electrical['add'])
                    .intersect(rebated_outline(-1.0, lid_total_height + 30.0)))
    lid = lid.cut(_above_mounts.world_shape_in_cap(electrical['cut']))
    for support in _a_anchors.supports().values():
        lid = lid.union(_above_mounts.world_shape_in_cap(support))
    for passage in _a_anchors.cuts().values():
        lid = lid.cut(_above_mounts.world_shape_in_cap(passage))
    return lid.clean()


def main():
    # Top cap opens +Z (mouth up); the bottom cap is the same cup built
    # mouth-down (open ceiling −Z), so both stack onto the shell by Z-shift
    # alone and the bottom cap's screws land on the shell's existing bosses.
    plain_cap_top = build_foam_cap()
    cap_top = add_deck_mounts(plain_cap_top)
    cap_bottom = build_foam_cap(open_down=True)
    # Each lid's head pads face its own cap's mouth, so the two are built with
    # the same flag as the caps they close, not one derived from the other.
    lid_bottom = build_foam_cap_lid(open_down=True)
    lid_top = build_top_lid()

    assert len(cap_top.solids().vals()) == 1, "cap_top must be a single solid"
    # Every plinth and anchor joins the lid.
    assert len(lid_top.solids().vals()) == 1, "lid_top must be a single solid"
    # The lid is no taller than its own plate + pad + whatever stands on its
    # outer face. The bottom lid's outer face is a plane; the top lid's extra
    # height includes its V-B wall and check bridge.
    cradle_proud = max((s.seat + seat.seat_top_z for s in cap_cradles.values()), default=0.0)
    anchor_proud = max((cap_anchor_axis_over_face(n) for n in cap_anchors), default=0.0)
    side_proud = max((cap_side_anchor_height(n) for n in cap_side_anchors), default=0.0)
    for name, lid, proud in (
        ("foam-cap-lid-bottom", lid_bottom, 0.0),
        ("foam-cap-lid-top", lid_top, max(cradle_proud, anchor_proud, side_proud,
                    *(_above_mounts.valve_support(n,lid_total_height).BoundingBox().zmax
                      - lid_total_height for n in ('valve-v-b',)))),
    ):
        zlen = lid.val().BoundingBox().zlen
        assert math.isclose(zlen, lid_total_height + proud, abs_tol=1e-6), \
            f"{name} stands {zlen:.4f} mm tall, not {lid_total_height + proud:g}"

    for shape, name, colour in (
            (cap_top, "foam-cap-top", _mat.C_CAP_TOP),
            (cap_bottom, "foam-cap-bottom", _mat.C_CAP_BOTTOM),
            (lid_top, "foam-cap-lid-top", _mat.C_CAP_LID_TOP),
            (lid_bottom, "foam-cap-lid-bottom", _mat.C_CAP_LID_BOTTOM)):
        export_assembly(one_body(shape, name, colour), str(_here / f"{name}.step"))
    print("-> foam-cap-top.step")
    print("-> foam-cap-bottom.step")
    print("-> foam-cap-lid-top.step")
    print("-> foam-cap-lid-bottom.step")

    # The cups have smooth recessed foil-seal lands. The common bed writer
    # retains their exact mesh and the shell's source frame; the lands stand
    # beyond the show-field proximity and receive no cosmetic flute cuts.
    for shape, name in ((cap_top, "foam-cap-top"), (cap_bottom, "foam-cap-bottom")):
        write_bed_file(shape, _here / f"{name}.stl")
    for shape, name in ((lid_top, "foam-cap-lid-top"), (lid_bottom, "foam-cap-lid-bottom")):
        piece_mesh(shape).export(str(_here / f"{name}.stl"))

    variables = {
        "LID_Z_H": f"{lid_total_height:.4g} mm",
        "FLUTE_D": f"{flute_depth:.4g} mm",
        "FCAP_BORE_D": f"{2.0 * cap_conduit_bore_radius:.4g} mm",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
    )
    # `_foam_cap` is where the two cups and the two lids are actually built, and it states the
    # conduit bore in its own docstrings. It exports no `__main__`, so this is the run that
    # hands it its figures.
    substitute_py_comments(
        Path(_foam_cap_module.__file__),
        variables=variables,
    )
    print("-> _foam_cap.py")
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
