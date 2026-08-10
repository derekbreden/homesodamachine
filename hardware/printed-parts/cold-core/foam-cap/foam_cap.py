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

from world_workplane import WorldWorkplane, xy_plane_z_up, yz_plane_x_up
from _cadq_export import export_step
import valve_seat as seat
from _foam_cap import (
    build_foam_cap,
    build_foam_cap_lid,
    build_foam_cap_gasket,
    lid_cut_through_depth,
    lid_total_height,
)
from _cold_core_interface import (
    build_z_axis_hole_punch,
    attachment_xy_positions,
    wall_and_floor_thickness,
    foam_cap_height,
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
    cap_anchor_cav_w,
    cap_anchor_cav_wall,
    cap_anchor_len,
    cap_anchor_wall,
    outer_shell_x_length,
    outer_shell_y_length,
)
from docgen import substitute_py_comments


# Lid z-thickness — one wall-and-floor thickness, [2 mm](LID_Z_H).
lid_z_height = wall_and_floor_thickness




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
    over = [d for d in (outer_shell_x_length / 2.0 - wall_and_floor_thickness - abs(x),
                        outer_shell_y_length / 2.0 - wall_and_floor_thickness - abs(y))
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
    rim, under the lid; a standing one carries the full cavity, the lid that closes it,
    and its standoff. Same section the whole way, standing on the floor's cavity side —
    the cap prints floor-down, and each column rises off the bed like the six screw
    bosses beside it."""
    standoff = deck_mount_standoff(name)
    if standoff == 0.0:
        return foam_cap_height
    return foam_cap_height + lid_z_height + standoff


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
    length and only its two ends carry on down to meet it, so the strap's channel is the room
    between those ends. The lid's own face is the channel's floor and the rib's underside is its
    roof — neither is drawn, and there is no cut anywhere in it to graze a face with.

    THE STRAP CLOSES ROUND THE BODY AND THE RIB'S OWN BACK TOGETHER: through the channel, out one
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
    lid_top = add_chain_anchors(
        add_cradles(cut_deck_mounts_lid(build_foam_cap_lid()), lid_total_height),
        lid_total_height)
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
        len(deck_mount_xy(name)) * math.pi * deck_lid_hole_radius(name) ** 2 * lid_z_height
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
        _conduit_section_area() * (foam_cap_height - wall_and_floor_thickness)
        - len(cap_conduits) * math.pi * cap_conduit_bore_radius ** 2 * foam_cap_height
    )
    conduit_lid_hole_volume = (len(cap_conduits) * math.pi
                               * cap_conduit_bore_radius ** 2 * lid_z_height)
    # The lid's hole opens on its outer face into the entry countersink, so each conduit takes
    # a frustum out of that plate rather than a cylinder — the bore's own radius at the inner
    # face out to `cap_conduit_entry_relief_radius` a wall above it, less the cylinder already
    # priced above. The three mouths stand clear of one another, so the cones price one each;
    # the assertion is what a pair standing closer would fail against.
    for _a, _b in itertools.combinations(cap_conduits.values(), 2):
        assert math.dist(_a, _b) >= 2.0 * cap_conduit_entry_relief_radius, (
            f"cap conduit entry reliefs at {_a} and {_b} stand {math.dist(_a, _b):.3f} mm apart "
            f"and each opens to ⌀{2.0 * cap_conduit_entry_relief_radius:.3f} — two cones that "
            f"meet are one opening, and the lens they share is priced twice below")
    conduit_lid_relief_volume = len(cap_conduits) * (
        math.pi * lid_z_height / 3.0
        * (cap_conduit_bore_radius ** 2
           + cap_conduit_bore_radius * cap_conduit_entry_relief_radius
           + cap_conduit_entry_relief_radius ** 2)
        - math.pi * cap_conduit_bore_radius ** 2 * lid_z_height)
    # The two caps differ by the deck columns and the conduits, and the two lids by the
    # openings both of those want, less the valve cradles the top one stands — nothing else is
    # cut into or built onto one end of the stack and not the other.
    #   The cradles are priced in closed form — four cylinders less four sockets per station
    # (`valve_seat.seat_volume`). The bosses are fused onto a face they only touch, so the lid
    # gains that sum and no more; a boss that plugged one of the lid's own openings, ran into its
    # neighbour, or grew a plate between the four comes up short here.
    cradle_volume = sum(seat.seat_volume(s.seat) for s in cap_cradles.values())
    # An anchor is priced the way it is laid down: one box the rib's length carrying a HALF bore
    # (the cylinder's own axis is the box's top face, so exactly half of it lies in the material),
    # and two end bands from the face up to that box. The bands stand a `cap_anchor_wall` clear of
    # the bore's own floor, so nothing here is cut twice; a rib that grew a plate across its
    # channel, or a bore that broke into the bands, comes up over.
    anchor_volume = sum(
        cap_anchor_len * 2.0 * (s.seat_r + cap_anchor_wall) * (s.seat_r + cap_anchor_wall)
        - 0.5 * math.pi * s.seat_r ** 2 * cap_anchor_len
        + 2.0 * cap_anchor_cav_wall * 2.0 * (s.seat_r + cap_anchor_wall) * cap_anchor_wall
        for s in cap_anchors.values()
    )
    cap_expect = deck_column_volume + conduit_column_volume
    lid_expect = (deck_lid_hole_volume + conduit_lid_hole_volume
                  + conduit_lid_relief_volume - cradle_volume - anchor_volume)
    cap_diff = cap_top.val().Volume() - cap_bottom.val().Volume()
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

    # What is under a head is still one wall of PETG — the same land the head
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
    head_radius = 2.75
    for name, lid, outer_z, inward, proud in (
        ("foam-cap-lid-bottom", lid_bottom, 0.0, 1.0, 0.0),
        ("foam-cap-lid-top", lid_top, lid_total_height, -1.0, max(cradle_proud, anchor_proud)),
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

    export_step(cap_top, str(_here / "foam-cap-top.step"))
    export_step(cap_bottom, str(_here / "foam-cap-bottom.step"))
    export_step(lid_top, str(_here / "foam-cap-lid-top.step"))
    export_step(lid_bottom, str(_here / "foam-cap-lid-bottom.step"))
    export_step(gasket, str(_here / "foam-cap-gasket.step"))
    print("-> foam-cap-top.step")
    print("-> foam-cap-bottom.step")
    print("-> foam-cap-lid-top.step")
    print("-> foam-cap-lid-bottom.step")
    print("-> foam-cap-gasket.step")

    variables = {
        "LID_Z_H": f"{lid_z_height:.4g} mm",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "LID_Z_H": 1,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
