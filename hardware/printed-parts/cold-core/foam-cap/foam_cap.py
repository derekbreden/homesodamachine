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
# The valve-manifold family's own cradle cell — the cap prints it rather than restating it.
sys.path.insert(0, str(_printed / "valve-manifold" / "single-tray"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from world_workplane import WorldWorkplane, xy_plane_z_up
from _cadq_export import export_step
import single_tray as cell
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
    cap_cradle_corner_radius,
    cap_cradle_reach,
    cap_cradle_socket_radius,
    cap_cradle_wall,
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


# The cap prints the valve-manifold family's cell, so the reach `_cold_core_interface` fences
# every cradle by has to be that cell's own. Held here, where both are in the room together:
# the interface cannot import the tray family without dragging it into every consumer of the
# cap's numbers, and a reach that drifted off the cell would fence a pad that is not the pad.
assert (cap_cradle_corner_inset, cap_cradle_socket_radius, cap_cradle_wall) == (
        cell.corner_pos, cell.socket_radius, cell.wall), (
    f"the cap fences its cradles on ({cap_cradle_corner_inset:g}, {cap_cradle_socket_radius:g}, "
    f"{cap_cradle_wall:g}) and `single_tray` cuts them on ({cell.corner_pos:g}, "
    f"{cell.socket_radius:g}, {cell.wall:g}) — one cell, one reach")
assert cell.saddle_half_y + 1.0 >= cap_cradle_reach, (
    f"the cell's saddle runs {cell.saddle_half_y + 1.0:g} mm off centre and the pad reaches "
    f"{cap_cradle_reach:g} — a trough that stops inside the pad leaves the valve's port on a rib")


def build_cradle(station):
    """One valve cradle, in the CAP's own frame.

    The pad is the least plate that carries the cell's four sockets — `cap_cradle_reach` each
    way, filleted on `cap_cradle_corner_radius`, which puts an arc centre on every socket — and
    it stands from the lid's outer face up to the cell's own top, where the valve's round boss
    lands. `single_tray.cut_cell` then cuts the port saddle and the four blind sockets into it,
    unchanged, so the cradle holds a Beduan exactly the way the tray family's plate does.

    Built at the cell's own origin (the valve's mounting plane on z = 0), then turned by the
    station's yaw and dropped onto the face."""
    pad = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=-station.seat)
        .rect(2 * cap_cradle_reach, 2 * cap_cradle_reach)
        .extrude(station.seat + cell.tray_top_z)
        .edges("|Z")
        .fillet(cap_cradle_corner_radius)
        .unwrap()
    )
    return cell.cut_cell(pad)


def add_cradles(lid, face_z):
    """Every valve cradle, standing on the lid's outer face at `face_z`.

    Returns `(lid, cradles)` — the lid with the pads fused on, and the pads as their own solid.
    `main` holds the lid's gain against that solid's volume, which is what says no pad has
    swallowed a hole the lid is cut with or run into another pad."""
    cradles = None
    for name, station in cap_cradles.items():
        pad = build_cradle(station)
        (cx, cy) = station.centre
        pad = (pad.rotate((0, 0, 0), (0, 0, 1), station.yaw)
                  .translate((cx, cy, face_z + station.seat)))
        cradles = pad if cradles is None else cradles.union(pad)
    return (lid if cradles is None else lid.union(cradles)), cradles


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
    # the one that carries the valve cradles — added last, after every hole is cut, because a
    # pad is material and the openings under it are what it has to stand clear of.
    lid_top, cradles = add_cradles(cut_deck_mounts_lid(build_foam_cap_lid()), lid_total_height)
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
    #   The cradles are priced as the solid they were built as. That is not arithmetic about
    # itself: the pads are fused onto a face they only touch, so the lid gains their whole
    # volume and no more — unless a pad has plugged one of the lid's own openings or run into
    # its neighbour, and then the gain comes up short and this fails.
    cradle_volume = 0.0 if cradles is None else cradles.val().Volume()
    cap_expect = deck_column_volume + conduit_column_volume
    lid_expect = (deck_lid_hole_volume + conduit_lid_hole_volume
                  + conduit_lid_relief_volume - cradle_volume)
    cap_diff = cap_top.val().Volume() - cap_bottom.val().Volume()
    lid_diff = lid_bottom.val().Volume() - lid_top.val().Volume()
    assert math.isclose(cap_diff, cap_expect, rel_tol=1e-6), \
        f"cap diff {cap_diff:.6f} != expected deck columns = {cap_expect:.6f}"
    assert math.isclose(lid_diff, lid_expect, rel_tol=1e-6), \
        f"lid diff {lid_diff:.6f} != expected deck-column holes = {lid_expect:.6f}"
    assert len(cap_top.solids().vals()) == 1, "cap_top must be a single solid"

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
    # plane; the top lid's cradle pads are the whole of its extra height.
    cradle_proud = max((s.seat + cell.tray_top_z for s in cap_cradles.values()), default=0.0)
    head_radius = 2.75
    for name, lid, outer_z, inward, proud in (
        ("foam-cap-lid-bottom", lid_bottom, 0.0, 1.0, 0.0),
        ("foam-cap-lid-top", lid_top, lid_total_height, -1.0, cradle_proud),
    ):
        zlen = lid.val().BoundingBox().zlen
        assert math.isclose(zlen, lid_total_height + proud, abs_tol=1e-6), \
            f"{name} stands {zlen:.4f} mm tall, not {lid_total_height + proud:g}"
        for x, y in attachment_xy_positions:
            seat = outer_z + inward * head_cbore_depth
            head = build_z_axis_hole_punch(
                origin=(x, y, min(seat, seat - inward * screw_head_height)),
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
