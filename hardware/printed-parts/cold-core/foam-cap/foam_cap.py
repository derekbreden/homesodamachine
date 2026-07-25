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
)
from _cold_core_interface import (
    build_z_axis_hole_punch,
    co2_inlet_y,
    co2_inlet_tube_radius,
    wall_and_floor_thickness,
    foam_cap_height,
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


# [6.5 mm](COTWO_TUBE_D) tube clearance for the 1/4" OD LLDPE CO2 line —
# distinct from the foam shell's ⌀18 elbow-body bore below the cap; only
# the tube itself traverses the cap and lid. Inlet position: co2_inlet_y
# (interface), between the centerward-wall and support-ring midlines.
co2_tube_clearance_radius = co2_inlet_tube_radius
# [5.25 mm](COTWO_BOSS_OUTER_R) boss outer radius.
co2_boss_outer_radius = co2_tube_clearance_radius + wall_and_floor_thickness
# Boss spans the full interior cavity height, from the floor's
# cavity-side face (Z = [2 mm](COTWO_BOSS_Z_BOTTOM)) to the cavity opening
# at Z = [18 mm](COTWO_BOSS_Z_TOP).
co2_boss_z_bottom = wall_and_floor_thickness
co2_boss_z_top = foam_cap_height


def cut_co2_inlet(cap):
    """Z-axis tube-clearance cut through the top cap floor."""
    return cap.cut(
        build_z_axis_hole_punch(
            origin=(0, co2_inlet_y, 0),
            hole_punch_radius=co2_tube_clearance_radius,
            hole_punch_height=foam_cap_height,
        )
    )


def cut_co2_inlet_lid(lid):
    """Z-axis tube-clearance cut through the lid, aligned with the top-cap hole."""
    return lid.cut(
        build_z_axis_hole_punch(
            origin=(0, co2_inlet_y, 0),
            hole_punch_radius=co2_tube_clearance_radius,
            hole_punch_height=lid_z_height,
        )
    )


def add_co2_boss(cap):
    """Annular boss around the CO2 through-hole on the cap floor's cavity
    side, spanning the full cavity height to seal the bore from the foam pour."""
    boss = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=co2_boss_z_bottom)
        .moveTo((0, co2_inlet_y))
        .circle(co2_boss_outer_radius)
        .circle(co2_tube_clearance_radius)
        .extrude(co2_boss_z_top - co2_boss_z_bottom)
        .unwrap()
    )
    return cap.union(boss)


# The deck-mount columns' top plane, off the cap's floor: the full cavity, the
# lid that closes it, and the standoff the module sits on. Same section the whole
# way, standing on the floor's cavity side — the cap prints floor-down, so each
# column rises off the bed at constant section like the six screw bosses beside it.
deck_boss_z_top = foam_cap_height + lid_z_height + deck_mount_standoff


def add_deck_mounts(cap):
    """The electronics' boss columns, standing on the top cap's floor and rising
    through the lid. Each carries a blind bore at its top for a heat-set insert;
    foam pours around the shanks, so the column is the module's only root."""
    for name in deck_mounts:
        for x, y in deck_mount_xy(name):
            column = (
                WorldWorkplane(xy_plane_z_up)
                .workplane(offset=wall_and_floor_thickness)
                .moveTo((x, y))
                .circle(deck_mount_boss_radius)
                .extrude(deck_boss_z_top - wall_and_floor_thickness)
                .unwrap()
            )
            cap = cap.union(column).cut(
                build_z_axis_hole_punch(
                    origin=(x, y, deck_boss_z_top - deck_mount_bore_depth),
                    hole_punch_radius=deck_mount_bore_radius,
                    hole_punch_height=deck_mount_bore_depth,
                )
            )
    return cap


def cut_deck_mounts_lid(lid):
    """Clearance through the lid at every deck-mount station — the columns pass it,
    they do not carry it. Same relationship the six cap screws already have."""
    for name in deck_mounts:
        for x, y in deck_mount_xy(name):
            lid = lid.cut(
                build_z_axis_hole_punch(
                    origin=(x, y, 0),
                    hole_punch_radius=deck_mount_boss_radius + deck_mount_lid_slip,
                    hole_punch_height=lid_z_height,
                )
            )
    return lid


def main():
    # Top cap opens +Z (mouth up); the bottom cap is the same cup built
    # mouth-down (open ceiling −Z), so both stack onto the shell by Z-shift
    # alone and the bottom cap's screws land on the shell's existing bosses.
    cap_top = add_deck_mounts(add_co2_boss(cut_co2_inlet(build_foam_cap())))
    cap_bottom = build_foam_cap(open_down=True)
    lid_bottom = build_foam_cap_lid()
    lid_top = cut_deck_mounts_lid(cut_co2_inlet_lid(lid_bottom))
    gasket = build_foam_cap_gasket()

    n_deck = sum(len(deck_mount_xy(name)) for name in deck_mounts)
    cap_floor_hole_volume = math.pi * co2_tube_clearance_radius ** 2 * wall_and_floor_thickness
    cap_boss_annular_volume = (
        math.pi
        * (co2_boss_outer_radius ** 2 - co2_tube_clearance_radius ** 2)
        * (co2_boss_z_top - co2_boss_z_bottom)
    )
    # Each deck column is a full-section cylinder off the floor's cavity side, less
    # the blind bore at its top. They stand clear of each other and of the six screw
    # bosses, so the pack adds without overlap and this arithmetic is exact.
    deck_column_volume = n_deck * math.pi * (
        deck_mount_boss_radius ** 2 * (deck_boss_z_top - wall_and_floor_thickness)
        - deck_mount_bore_radius ** 2 * deck_mount_bore_depth
    )
    deck_lid_hole_volume = (
        n_deck * math.pi * (deck_mount_boss_radius + deck_mount_lid_slip) ** 2 * lid_z_height
    )
    lid_hole_volume = math.pi * co2_tube_clearance_radius ** 2 * lid_z_height
    cap_expect = cap_boss_annular_volume - cap_floor_hole_volume + deck_column_volume
    lid_expect = lid_hole_volume + deck_lid_hole_volume
    cap_diff = cap_top.val().Volume() - cap_bottom.val().Volume()
    lid_diff = lid_bottom.val().Volume() - lid_top.val().Volume()
    assert math.isclose(cap_diff, cap_expect, rel_tol=1e-6), \
        f"cap diff {cap_diff:.6f} != expected boss − hole + deck columns = {cap_expect:.6f}"
    assert math.isclose(lid_diff, lid_expect, rel_tol=1e-6), \
        f"lid diff {lid_diff:.6f} != expected lid holes = {lid_expect:.6f}"
    assert len(cap_top.solids().vals()) == 1, "cap_top must be a single solid"

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
        "COTWO_TUBE_D": f"{co2_tube_clearance_radius * 2:.4g} mm",
        "COTWO_BOSS_OUTER_R": f"{co2_boss_outer_radius:.4g} mm",
        "COTWO_BOSS_Z_BOTTOM": f"{co2_boss_z_bottom:.4g} mm",
        "COTWO_BOSS_Z_TOP": f"{co2_boss_z_top:.4g} mm",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "LID_Z_H": 1,
            "COTWO_TUBE_D": 1,
            "COTWO_BOSS_OUTER_R": 1,
            "COTWO_BOSS_Z_BOTTOM": 1,
            "COTWO_BOSS_Z_TOP": 1,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
