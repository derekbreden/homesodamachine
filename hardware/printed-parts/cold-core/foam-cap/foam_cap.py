"""Foam-cap stack — the three parts that close one end of the
foam shell during the pour-in-place foam cure: the cap tray, the
lid that sits atop the cap during pouring, and the TPU 90A gasket
that compresses between the cap and the outer-shell mating face.
Printed twice per build (one stack on each end of the shell)."""

import math
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(0, str(_here.parent))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from world_workplane import WorldWorkplane, xy_plane_z_up
from _cadq_export import export_step
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
    deck_mount_lid_slip,
    deck_mount_standoff,
)
from docgen import substitute_py_comments


# Lid z-thickness — one wall-and-floor thickness, [2 mm](LID_Z_H).
lid_z_height = wall_and_floor_thickness




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


def deck_lid_hole_radius(name):
    """The lid's opening at a deck-mount station: a slip fit around a column standing
    through it, a screw clearance over one that stops beneath it."""
    if deck_mount_standoff(name) == 0.0:
        return screw_clearance_radius
    return deck_mount_boss_radius + deck_mount_lid_slip


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
    lid_top = cut_deck_mounts_lid(build_foam_cap_lid())
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
    # The two caps differ by the deck columns alone, and the two lids by the
    # clearance holes those columns pass through — nothing else is cut into one
    # end of the stack and not the other.
    cap_expect = deck_column_volume
    lid_expect = deck_lid_hole_volume
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
    # the lid is no taller than its own plate + pad. Nothing stands off the
    # outer face, so the outer face is a plane.
    head_radius = 2.75
    for name, lid, outer_z, inward in (
        ("foam-cap-lid-bottom", lid_bottom, 0.0, 1.0),
        ("foam-cap-lid-top", lid_top, lid_total_height, -1.0),
    ):
        zlen = lid.val().BoundingBox().zlen
        assert math.isclose(zlen, lid_total_height, abs_tol=1e-6), \
            f"{name} stands {zlen:.4f} mm tall, not {lid_total_height:g}"
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
