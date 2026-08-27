"""Foam-cap stack — the three parts that close one end of the
foam shell during the pour-in-place foam cure: the cap tray, the
lid that sits atop the cap during pouring, and the TPU 90A gasket
that compresses between the cap and the outer-shell mating face.
Printed twice per build (one stack on each end of the shell)."""

import itertools
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
from _cadq_export import export_assembly
from _show_skin import write_bed_file
import _materials as _mat
from _materials import one_body
import valve_seat as seat
from _foam_cap import (
    build_foam_cap,
    build_foam_cap_lid,
    build_foam_cap_gasket,
    lid_cut_through_depth,
    lid_total_height,
    top_cap_height,
)
from _outer_shell import build_attachment_bosses
from _cold_core_interface import (
    build_z_axis_hole_punch,
    attachment_xy_positions,
    wall_and_floor_thickness,
    corner_round_radius,
    flute_depth,
    foam_cap_lid_pour_radius,
    foam_cap_lid_vent_radius,
    head_pad_height,
    screw_clearance_radius,
    screw_head_height,
    head_cbore_depth,
    deck_mounts,
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
    cap_cradle_corner_inset,
    cap_cradle_boss_radius,
    cap_cradle_socket_radius,
    cap_cradle_wall,
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
    cap_side_depth,
    cap_side_len,
    cap_side_wall,
    drain_berth_span,
    drain_berth_depth,
    cap_anchor_cav_w,
    cap_anchor_cav_wall,
    cap_anchor_len,
    cap_anchor_wall,
    outer_shell_wall,
    outer_shell_x_length,
    outer_shell_y_length,
)
from docgen import substitute_py_comments


# The lid's own footprint, as area: the shell's rectangle less what its four corner rounds take
# out of it. Every plate in this stack is cut to it, and the two lids' plates differ by nothing
# else.
footprint_area = (outer_shell_x_length * outer_shell_y_length
                  - (4.0 - math.pi) * corner_round_radius ** 2)
# The pour hole and the two vents, as one area. Neither lid carries anything else through its
# plate that the other does not, so this is the whole of what the two have in common there.
lid_open_area = (math.pi * foam_cap_lid_pour_radius ** 2
                 + 2.0 * math.pi * foam_cap_lid_vent_radius ** 2)




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
    return area - sum(_conduit_wall_overlap_area(*c) for c in centres)


def deck_boss_z_top(name):
    """A deck mount's column tops, off the cap's floor. A flush mount stops at the mouth
    rim, under the lid; a standing one carries the whole cup, the lid that closes it,
    and its standoff. Same section the whole way, standing on the floor's cavity side —
    the cap prints floor-down, and each column rises off the bed like the six screw
    bosses beside it."""
    standoff = deck_mount_standoff(name)
    if standoff == 0.0:
        return top_cap_height
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


# `_cold_core_interface` fences every cradle on a boss, and `valve_seat` builds the boss.
assert (cap_cradle_corner_inset, cap_cradle_socket_radius, cap_cradle_wall) == (
        seat.corner_inset, seat.socket_radius, seat.wall), (
    f"the cap fences its cradles on ({cap_cradle_corner_inset:g}, {cap_cradle_socket_radius:g}, "
    f"{cap_cradle_wall:g}) and `valve_seat` builds them on ({seat.corner_inset:g}, "
    f"{seat.socket_radius:g}, {seat.wall:g}) — one seat, one fence")
assert cap_cradle_boss_radius == seat.boss_radius, (
    f"the cap fences a cradle at r{cap_cradle_boss_radius:g} and `valve_seat` stands bosses at "
    f"r{seat.boss_radius:g} — the fence is drawn on the boss and there is nothing else to draw "
    f"it on")


def add_cradles(lid, face_z):
    """Every valve cradle, standing on the lid's outer face at `face_z`.

    A CRADLE IS FOUR BOSSES (`valve_seat`) and nothing between them — the valve's corner posts
    press into their sockets and its round boss lands on their tops. `main` holds the lid's gain
    against `valve_seat.seat_volume` summed over the stations, which is what says no boss has
    swallowed a hole the lid is cut with or run into its neighbour."""
    for name, station in cap_cradles.items():
        # A SEAT OF FOUR BOSSES IS SQUARE, so a quarter turn carries it onto itself and a
        # station's yaw locates its valve without turning the print.
        assert station.yaw % 90.0 == 0.0, (
            f"cradle {name} stands its valve at {station.yaw:g}° — a seat's four bosses are "
            f"square, and only a quarter turn carries them onto themselves")
        (cx, cy) = station.centre
        lid = lid.union(
            seat.build_seat(station.seat).translate((cx, cy, face_z + station.seat)))
    return lid


def add_chain_anchors(lid, face_z):
    """Every chain anchor, standing on the lid's outer face at `face_z`.

    THE CHANNEL IS A REMAINDER: the rib stands one `cap_anchor_wall` over the face down its whole
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
        (cx, cy) = station.centre
        seat_r = station.seat_r
        reach = seat_r + cap_anchor_wall
        axis_z = face_z + cap_anchor_axis_over_face(name)
        x0 = cx - cap_anchor_len / 2.0

        def block(xa, length, za, zb):
            return (
                WorldWorkplane(yz_plane_x_up)
                .workplane(offset=xa)
                .polyline([(cy - reach, za), (cy + reach, za),
                           (cy + reach, zb), (cy - reach, zb)])
                .close()
                .extrude(length)
            )

        rib = block(x0, cap_anchor_len, face_z + cap_anchor_wall, axis_z)
        for s0, s1 in ((0.0, cap_anchor_cav_wall),
                       (cap_anchor_cav_wall + cap_anchor_cav_w, cap_anchor_len)):
            rib = rib.union(block(x0 + s0, s1 - s0, face_z, face_z + cap_anchor_wall))
        bore = (
            WorldWorkplane(yz_plane_x_up)
            .workplane(offset=x0)
            .pushPoints([(cy, axis_z)])
            .circle(seat_r)
            .extrude(cap_anchor_len)
        )
        lid = lid.union(rib.cut(bore).clean().val())
    return lid


def add_side_anchors(lid, face_z):
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
        cap_side_anchor_holds(name)
        (cx, cy) = station.centre
        seat_r = station.seat_r
        axis_z = face_z + station.over_face
        roof_z = face_z + cap_side_tunnel_roof(name)  # the window's roof, one wall under the pipe
        sill_z = roof_z - cap_side_tunnel_h(name)     # and its floor, hung off that roof
        top_z = face_z + cap_side_anchor_height(name)
        y0 = cy - cap_side_len / 2.0                 # the post's ends, along the run

        def block(ya, length, za, zb):
            """One slab of the post: `length` of it along the run, spanning z."""
            return (
                WorldWorkplane(xy_plane_z_up)
                .workplane(offset=za)
                .polyline([(cx, ya), (cx - cap_side_depth, ya),
                           (cx - cap_side_depth, ya + length), (cx, ya + length)])
                .close()
                .extrude(zb - za)
            )

        post = block(y0, cap_side_len, face_z, top_z)
        # THE TIE'S WINDOW, cut front to back under the pipe and closed on every side but its two
        # mouths. One wall of the post is its roof and the post's own stock its floor, so the
        # zip tie lies against the material it pulls and the column under it is never opened.
        tunnel = (
            WorldWorkplane(xy_plane_z_up)
            .workplane(offset=sill_z)
            .polyline([(cx, cy - cap_side_cav_w / 2.0),
                       (cx - cap_side_depth, cy - cap_side_cav_w / 2.0),
                       (cx - cap_side_depth, cy + cap_side_cav_w / 2.0),
                       (cx, cy + cap_side_cav_w / 2.0)])
            .close()
            .extrude(roof_z - sill_z)
        )
        # The pipe runs ALONG the post, which is the cap's own Y — so its plane is the one whose
        # normal is Y, and the offset that walks it is the post's own end. Its axis stands
        # `axis_off` FORWARD of the post's front face, so what the cut leaves in that face is a
        # seat shallower than a half pipe and the tube beds into it from the room.
        bore = (
            WorldWorkplane(xz_plane_y_up)
            .workplane(offset=y0)
            .pushPoints([(cap_side_axis_y(name), axis_z)])
            .circle(seat_r)
            .extrude(cap_side_len)
        )
        # THE TIE'S OWN CHANNEL DOWN THE BACK, on the window's own width and over its mouth, so
        # the zip tie leaves the window and climbs the post in one line and the buckle sits in it.
        # It stops on the window's floor: below that the tie has left the post, and a channel
        # carried on down to the lid would groove the column for nothing that runs in it.
        relief = (
            WorldWorkplane(xy_plane_z_up)
            .workplane(offset=sill_z)
            .polyline([(cx - cap_side_depth + cap_side_back_relief, cy - cap_side_cav_w / 2.0),
                       (cx - cap_side_depth, cy - cap_side_cav_w / 2.0),
                       (cx - cap_side_depth, cy + cap_side_cav_w / 2.0),
                       (cx - cap_side_depth + cap_side_back_relief, cy + cap_side_cav_w / 2.0)])
            .close()
            .extrude(top_z - sill_z)
        )
        lid = lid.union(post.cut(bore).cut(tunnel).cut(relief).clean().val())
    return lid


def cut_deck_mounts_lid(lid):
    """The lid's opening at every deck-mount station — a standing column passes it, and a
    flush one meets its underside with only the screw crossing."""
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
    return lid


def main():
    # Top cap opens +Z (mouth up); the bottom cap is the same cup built
    # mouth-down (open ceiling −Z), so both stack onto the shell by Z-shift
    # alone and the bottom cap's screws land on the shell's existing bosses.
    cap_top = add_deck_mounts(build_foam_cap())
    cap_bottom = build_foam_cap(open_down=True)
    # Each lid's head pads face its own cap's mouth, so the two are built with
    # the same flag as the caps they close, not one derived from the other.
    lid_bottom = build_foam_cap_lid(open_down=True)
    # The top lid's outer face is the one surface in this stack anything stands on, so it is
    # the one that carries the valve cradles and the chain anchor — added last, after every hole
    # is cut, because both are material and the openings under them are what they stand clear of.
    lid_top = add_side_anchors(
        add_chain_anchors(
            add_cradles(cut_deck_mounts_lid(build_foam_cap_lid()), lid_total_height),
            lid_total_height),
        lid_total_height)
    # THE DRAIN'S BERTH: the fore edge set back over the funnel drain's column
    # (`_cold_core_interface.drain_berth_*`), the corner the union hangs in and `water-3`'s
    # crossing steps into. The plate alone stands there, so the cut is its own closed form.
    _by0, _by1 = drain_berth_span
    _bx = outer_shell_x_length / 2.0
    lid_top = lid_top.cut(
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=-1.0)
        .moveTo(((_bx - drain_berth_depth + _bx + 1.0) / 2.0, (_by0 + _by1) / 2.0))
        .rect(drain_berth_depth + 1.0, _by1 - _by0)
        .extrude(lid_total_height + 2.0)
        .unwrap())
    gasket = build_foam_cap_gasket()

    # Each deck column is a full-section cylinder off the floor's cavity side, less
    # the blind bore at its top. They stand clear of each other and of the six screw
    # bosses, so the pack adds without overlap and this arithmetic is exact.
    deck_column_volume = sum(
        len(deck_mount_xy(name)) * math.pi * (
            deck_mount_boss_radius ** 2 * (deck_boss_z_top(name) - wall_and_floor_thickness)
            - deck_mount_bore_radius ** 2 * deck_mount_bore_depth
        )
        for name in deck_mounts
    )
    deck_lid_hole_volume = sum(
        len(deck_mount_xy(name)) * math.pi * deck_lid_hole_radius(name) ** 2 * lid_total_height
        for name in deck_mounts
    )
    # Each conduit is a column off the floor's cavity side less a bore that carries on down
    # through the floor under it, and the lid it lands on takes the same bore through its
    # plate. The columns are priced on their SHARED section, not one section each: a pair
    # whose bores stand a `LINE_PITCH` apart carries bosses that overlap, they fuse into one
    # post, and the lens they hold in common is material counted once. The bores never merge
    # — a bore is thinner than the wall around it — so they price one each.
    #   The lens is taken pairwise, which is exact for a pair and over-subtracts for three
    # columns mutually overlapping. Nothing here is asked to trust that: the assertion below
    # is what a third conduit would fail against.
    conduit_column_volume = (
        _conduit_section_area() * (top_cap_height - wall_and_floor_thickness)
        - len(cap_conduits) * math.pi * cap_conduit_bore_radius ** 2 * top_cap_height
    )
    conduit_lid_hole_volume = (len(cap_conduits) * math.pi
                               * cap_conduit_bore_radius ** 2 * lid_total_height)
    # The bore opens on the lid's outer face into the entry countersink, which is sunk ONE WALL
    # into that face and no further — so each conduit takes a frustum out of the plate's top
    # wall on top of the cylinder already priced through the whole of it: the bore's own radius
    # a wall down, out to `cap_conduit_entry_relief_radius` at the face, less the cylinder that
    # wall already held. The three mouths stand clear of one another, so the cones price one
    # each; the assertion is what a pair standing closer would fail against.
    for _a, _b in itertools.combinations(cap_conduits.values(), 2):
        assert math.dist(_a, _b) >= 2.0 * cap_conduit_entry_relief_radius, (
            f"cap conduit entry reliefs at {_a} and {_b} stand {math.dist(_a, _b):.3f} mm apart "
            f"and each opens to ⌀{2.0 * cap_conduit_entry_relief_radius:.3f} — two cones that "
            f"meet are one opening, and the lens they share is priced twice below")
    conduit_lid_relief_volume = len(cap_conduits) * (
        math.pi * wall_and_floor_thickness / 3.0
        * (cap_conduit_bore_radius ** 2
           + cap_conduit_bore_radius * cap_conduit_entry_relief_radius
           + cap_conduit_entry_relief_radius ** 2)
        - math.pi * cap_conduit_bore_radius ** 2 * wall_and_floor_thickness)
    cradle_volume = sum(seat.seat_volume(s.seat) for s in cap_cradles.values())
    # An anchor is priced the way it is laid down: one box the rib's length carrying a HALF bore
    # (the cylinder's own axis is the box's top face, so exactly half of it lies in the material),
    # and two end bands from the face up to that box. The bands stand a `cap_anchor_wall` clear of
    # the bore's own floor, so nothing here is cut twice; a rib that grew a plate across its
    # channel, or a bore that broke into the bands, comes up over.
    #   A RIB STANDS AS HIGH AS ITS OWN ROW SAYS. One bored for a body takes the height the three
    # layers come to; one bored for a RUN is built up to a plane the run already lies on, so what
    # the block spans over the face is `cap_anchor_axis_over_face` less the channel under it.
    anchor_volume = sum(
        cap_anchor_len * 2.0 * (s.seat_r + cap_anchor_wall)
        * (cap_anchor_axis_over_face(n) - cap_anchor_wall)
        - 0.5 * math.pi * s.seat_r ** 2 * cap_anchor_len
        + 2.0 * cap_anchor_cav_wall * 2.0 * (s.seat_r + cap_anchor_wall) * cap_anchor_wall
        for n, s in cap_anchors.items()
    )
    # A SIDEWAYS anchor is priced the way it is laid down: one block the post's whole footprint,
    # standing the lid's face to its own crown, carrying a HALF bore because the pipe's axis is
    # that block's forward face; then the tie's window taken out under the pipe, and the tie's
    # channel out of the back — which runs the window's floor to the crown, so what it takes on
    # its own is only the material over the window's roof, the rest of that band being window
    # already. Neither cut reaches the bore, which stands one wall over the window and forward of
    # the channel. A post that swallowed a boss beside it, or a bore that broke out of its back,
    # comes up over.
    side_anchor_volume = sum(
        cap_side_depth * cap_side_len * cap_side_anchor_height(n)
        - _circle_beyond(s.axis_off, s.seat_r) * cap_side_len
        - cap_side_depth * cap_side_cav_w * cap_side_tunnel_h(n)
        - cap_side_back_relief * cap_side_cav_w
        * (cap_side_anchor_height(n) - cap_side_tunnel_roof(n))
        for n, s in cap_side_anchors.items()
    )
    # The drain berth's cut is the plate's own section over its span, the whole thickness of it
    # — nothing else stands in the fore edge's band.
    drain_berth_volume = (drain_berth_depth * (drain_berth_span[1] - drain_berth_span[0])
                          * lid_total_height)
    # WHAT THE TOP LID'S PLATE HOLDS THAT THE BOTTOM'S DOES NOT: one head pad of footprint,
    # less the six pads already standing in that band and less the openings both plates carry
    # through it. The pads are the one figure here not written down — a pad is the cap boss's
    # own section, a circle with its webs run out to the wall and the footprint's corner arc
    # trimming both, and that section is BUILT rather than stated. So it is measured off the
    # builder the bottom lid stands it with, and everything on either side of it is closed form.
    plate_gain = ((footprint_area - lid_open_area) * head_pad_height
                  - build_attachment_bosses(head_pad_height).val().Volume())
    # The two cups differ by the deck columns and the conduits, read over the height they BOTH
    # stand: the top cup gives its mouth band to its lid, so the bottom one is trimmed by that
    # same band before the two are subtracted, and what is left on either side is one cup. The
    # bottom cup's relief lives entirely inside the band, which is why nothing of it survives
    # into this arithmetic.
    #   The two lids differ by that band, by the openings the top one alone is cut with, and by
    # the cradles and anchors it alone stands — nothing else is cut into or built onto one end
    # of the stack and not the other.
    #   The cradles are priced in closed form — four cylinders less four sockets per station
    # (`valve_seat.seat_volume`). The bosses are fused onto a face they only touch, so the lid
    # gains that sum and no more; a boss that plugged one of the lid's own openings, ran into its
    # neighbour, or grew a plate between the four comes up short here.
    cap_expect = deck_column_volume + conduit_column_volume
    lid_expect = (deck_lid_hole_volume + conduit_lid_hole_volume
                  + conduit_lid_relief_volume - cradle_volume - anchor_volume
                  - side_anchor_volume + drain_berth_volume - plate_gain)
    cap_diff = cap_top.val().Volume() - cap_bottom.cut(
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=-1.0)
        .rect(outer_shell_x_length + 2.0, outer_shell_y_length + 2.0)
        .extrude(head_pad_height + 1.0)
        .unwrap()
    ).val().Volume()
    lid_diff = lid_bottom.val().Volume() - lid_top.val().Volume()
    assert math.isclose(cap_diff, cap_expect, rel_tol=1e-6), \
        f"cap diff {cap_diff:.6f} != expected deck columns = {cap_expect:.6f}"
    assert math.isclose(lid_diff, lid_expect, rel_tol=1e-6), \
        f"lid diff {lid_diff:.6f} != expected deck-column holes = {lid_expect:.6f}"
    assert len(cap_top.solids().vals()) == 1, "cap_top must be a single solid"
    # Every boss landed on the lid. One that missed it is a solid of its own.
    assert len(lid_top.solids().vals()) == 1, "lid_top must be a single solid"

    # And no cradle stands inside the valve it holds.
    for _name, _station in cap_cradles.items():
        _foul = seat.fouled_volume(_station.seat)
        assert _foul <= 1e-6, (
            f"cradle {_name} stands {_foul:.3f} mm^3 inside its own valve")

    # What is under a head is still one wall of PET-GF — the same land the head
    # clamps on when it sits on a flat lid, which is what makes the recess a
    # relocation of the clamp rather than a thinning of it.
    land = lid_total_height - head_cbore_depth
    assert math.isclose(land, wall_and_floor_thickness), (
        f"the land under a head is {land:g} mm, not the "
        f"{wall_and_floor_thickness:g} mm it bears on today")

    # And the heads are inside the lid. Seat an M3 SHCS head (⌀5.5 × 3, DIN 912
    # nominal) on each counterbore floor: it shares no volume with the lid, and
    # the lid is no taller than its own plate + pad + whatever stands on its
    # outer face. The bottom lid stands nothing there, so its outer face is a
    # plane; the top lid's extra height is the taller of its cradle bosses and
    # its chain anchors, whose crown is the seated body's own axis.
    cradle_proud = max((s.seat + seat.seat_top_z for s in cap_cradles.values()), default=0.0)
    anchor_proud = max((cap_anchor_axis_over_face(n) for n in cap_anchors), default=0.0)
    side_proud = max((cap_side_anchor_height(n) for n in cap_side_anchors), default=0.0)
    head_radius = 2.75
    for name, lid, outer_z, inward, proud in (
        ("foam-cap-lid-bottom", lid_bottom, 0.0, 1.0, 0.0),
        ("foam-cap-lid-top", lid_top, lid_total_height, -1.0,
         max(cradle_proud, anchor_proud, side_proud)),
    ):
        zlen = lid.val().BoundingBox().zlen
        assert math.isclose(zlen, lid_total_height + proud, abs_tol=1e-6), \
            f"{name} stands {zlen:.4f} mm tall, not {lid_total_height + proud:g}"
        for x, y in attachment_xy_positions:
            cbore_floor = outer_z + inward * head_cbore_depth
            head = build_z_axis_hole_punch(
                origin=(x, y, min(cbore_floor, cbore_floor - inward * screw_head_height)),
                hole_punch_radius=head_radius,
                hole_punch_height=screw_head_height,
            )
            fouled = lid.val().intersect(head.val()).Volume()
            assert fouled <= 1e-6, \
                f"{name}: the head at ({x:.1f}, {y:.1f}) fouls the lid by {fouled:.3f} mm^3"

    for shape, name, colour in (
            (cap_top, "foam-cap-top", _mat.C_CAP_TOP),
            (cap_bottom, "foam-cap-bottom", _mat.C_CAP_BOTTOM),
            (lid_top, "foam-cap-lid-top", _mat.C_CAP_LID_TOP),
            (lid_bottom, "foam-cap-lid-bottom", _mat.C_CAP_LID_BOTTOM),
            (gasket, "foam-cap-gasket", _mat.C_SILICONE)):
        export_assembly(one_body(shape, name, colour), str(_here / f"{name}.step"))
    print("-> foam-cap-top.step")
    print("-> foam-cap-bottom.step")
    print("-> foam-cap-lid-top.step")
    print("-> foam-cap-lid-bottom.step")
    print("-> foam-cap-gasket.step")

    # AND THE TWO CUPS' WALLS ARE FLUTED HERE, on the shell's own run — they stand on the same
    # footprint, so the stack is one silhouette and the field crosses each seam without a step.
    # THE TOP CAP INSTALLS SPUN a half turn about Z (`foam_assembly._spin`), which shifts its
    # field by half the perimeter; on an even `flute_count` that is a whole number of pitches,
    # so a field cut in the cap's own frame lands on the shell's grooves after the spin and
    # neither piece has to be told about the other (`flute-even`).
    #   THE TWO LIDS TAKE NONE OF IT, so each one's edge is a smooth band of the silhouette —
    # one `wall_and_floor_thickness` where the bottom lid closes the stack, and the whole
    # [5.2 mm](LID_Z_H) of its plate where the top lid meets the crown. Neither is tall enough
    # to carry the field: the fade runs over `flute_rise` off each of a band's own two faces, so
    # a band reaches full depth only at twice that, and cut on the core's own run these two come
    # back at 0.604 mm and 0.121 mm against the shell's [1.2 mm](FLUTE_D). `flute-reveal` is that
    # bound, read over every band of the silhouette. What a band like this reads as is a reveal,
    # which is what a seam wants.
    for shape, name in ((cap_top, "foam-cap-top"), (cap_bottom, "foam-cap-bottom")):
        write_bed_file(shape, _here / f"{name}.stl")

    variables = {
        "LID_Z_H": f"{lid_total_height:.4g} mm",
        "FLUTE_D": f"{flute_depth:.4g} mm",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
