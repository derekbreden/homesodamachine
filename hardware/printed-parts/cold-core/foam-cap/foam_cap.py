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
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
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
    pocket_centerward_arc_outer_radius,
    support_ring_radial_width,
    wall_and_floor_thickness,
    foam_cap_height,
    foam_cap_attachment_xy_positions_bottom,
)
from docgen import substitute_py_comments


# Lid z-thickness — one wall-and-floor thickness, [2 mm](LID_Z_H).
lid_z_height = wall_and_floor_thickness


# CO2 elbow vertical leg sits in the foam zone between the centerward
# wall band and the support-ring wall band, midway between their midlines.
# [72.5 mm](CW_WALL_OUTER_R) centerward-wall outer cylinder radius.
centerward_wall_outer_r = pocket_centerward_arc_outer_radius
# [70.5 mm](CW_WALL_INNER_R) centerward-wall inner face.
centerward_wall_inner_r = centerward_wall_outer_r - wall_and_floor_thickness
support_ring_outer_r = centerward_wall_inner_r
# [61.5 mm](SUPPORT_RING_INNER_R) support-ring inner radius.
support_ring_inner_r = support_ring_outer_r - support_ring_radial_width
centerward_wall_mid_y = -(centerward_wall_outer_r + centerward_wall_inner_r) / 2
support_ring_mid_y = -(support_ring_outer_r + support_ring_inner_r) / 2
# [-68.75 mm](COTWO_INLET_Y) CO2 inlet Y — midway between the two wall midlines.
co2_inlet_y = (centerward_wall_mid_y + support_ring_mid_y) / 2


# [6.5 mm](COTWO_TUBE_D) tube clearance for the 1/4" OD LLDPE CO2 line —
# distinct from the foam shell's ⌀16 elbow-body bore below the cap; only
# the tube itself traverses the cap and lid.
co2_tube_clearance_radius = 3.25
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


def main():
    # Top cap opens +Z (mouth up) on the top diagonal; bottom cap is authored
    # mouth-down (open ceiling −Z) on the mirrored bottom diagonal. Both stack
    # onto the shell by Z-translation alone.
    cap_top = add_co2_boss(cut_co2_inlet(build_foam_cap()))
    cap_bottom = build_foam_cap(
        open_down=True, positions=foam_cap_attachment_xy_positions_bottom
    )
    lid_top = cut_co2_inlet_lid(build_foam_cap_lid())
    lid_bottom = build_foam_cap_lid(positions=foam_cap_attachment_xy_positions_bottom)
    gasket = build_foam_cap_gasket()

    cap_floor_hole_volume = math.pi * co2_tube_clearance_radius ** 2 * wall_and_floor_thickness
    cap_boss_annular_volume = (
        math.pi
        * (co2_boss_outer_radius ** 2 - co2_tube_clearance_radius ** 2)
        * (co2_boss_z_top - co2_boss_z_bottom)
    )
    lid_hole_volume = math.pi * co2_tube_clearance_radius ** 2 * lid_z_height
    cap_diff = cap_top.val().Volume() - cap_bottom.val().Volume()
    lid_diff = lid_bottom.val().Volume() - lid_top.val().Volume()
    assert math.isclose(cap_diff, cap_boss_annular_volume - cap_floor_hole_volume, rel_tol=1e-6), \
        f"cap diff {cap_diff:.6f} != expected boss − hole = {cap_boss_annular_volume - cap_floor_hole_volume:.6f}"
    assert math.isclose(lid_diff, lid_hole_volume, rel_tol=1e-6), \
        f"lid diff {lid_diff:.6f} != expected lid hole = {lid_hole_volume:.6f}"
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
        "CW_WALL_OUTER_R": f"{centerward_wall_outer_r:.4g} mm",
        "CW_WALL_INNER_R": f"{centerward_wall_inner_r:.4g} mm",
        "SUPPORT_RING_INNER_R": f"{support_ring_inner_r:.4g} mm",
        "COTWO_INLET_Y": f"{co2_inlet_y:.4g} mm",
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
            "CW_WALL_OUTER_R": 1,
            "CW_WALL_INNER_R": 1,
            "SUPPORT_RING_INNER_R": 1,
            "COTWO_INLET_Y": 1,
            "COTWO_TUBE_D": 1,
            "COTWO_BOSS_OUTER_R": 1,
            "COTWO_BOSS_Z_BOTTOM": 1,
            "COTWO_BOSS_Z_TOP": 1,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
