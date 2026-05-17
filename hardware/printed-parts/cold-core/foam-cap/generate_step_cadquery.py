"""Foam-cap stack — the three parts that close one end of the
foam shell during the pour-in-place foam cure: the cap tray, the
lid that sits atop the cap during pouring, and the TPU 90A gasket
that compresses between the cap and the outer-shell mating face.
Printed twice per build (one stack on each end of the shell)."""

import math
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(0, str(_here.parent))

from _cadq_export import export_step
from _foam_cap import (
    build_foam_cap,
    build_foam_cap_lid,
    build_foam_cap_gasket,
)
from _cold_core_interface import (
    build_a_y_axis_hole_punch,
    pocket_centerward_arc_outer_radius,
    wall_and_floor_thickness,
    foam_cap_height,
    xz_plane_y_up,
    WorldWorkplane,
)


lid_y_height = wall_and_floor_thickness


# CO2 elbow vertical leg sits in the foam zone between the centerward
# wall band and the support-ring wall band — midway between their
# midlines so it's clear of both walls and surrounded by foam.
support_ring_radial_width = 9.0
centerward_wall_outer_r = pocket_centerward_arc_outer_radius
centerward_wall_inner_r = centerward_wall_outer_r - wall_and_floor_thickness
support_ring_outer_r = centerward_wall_inner_r
support_ring_inner_r = support_ring_outer_r - support_ring_radial_width
centerward_wall_mid_z = -(centerward_wall_outer_r + centerward_wall_inner_r) / 2
support_ring_mid_z = -(support_ring_outer_r + support_ring_inner_r) / 2
co2_inlet_z = (centerward_wall_mid_z + support_ring_mid_z) / 2


# ⌀6.5 tube clearance for the 1/4" OD LLDPE CO2 line — distinct from
# the foam shell's ⌀16 elbow-body bore below the cap; only the tube
# itself traverses the cap and lid.
co2_tube_clearance_radius = 3.25
co2_boss_outer_radius = co2_tube_clearance_radius + wall_and_floor_thickness
# Boss spans the full interior cavity height, from the floor's
# cavity-side face to the cavity opening.
co2_boss_y_bottom = wall_and_floor_thickness
co2_boss_y_top = foam_cap_height


def cut_co2_inlet(cap):
    """Y-axis tube-clearance cut through the top cap floor."""
    return cap.cut(
        build_a_y_axis_hole_punch(
            origin=(0, 0, co2_inlet_z),
            hole_punch_radius=co2_tube_clearance_radius,
            hole_punch_height=foam_cap_height,
        )
    )


def cut_co2_inlet_lid(lid):
    """Y-axis tube-clearance cut through the lid, continuing the CO2
    path from outside through to the top cap."""
    return lid.cut(
        build_a_y_axis_hole_punch(
            origin=(0, 0, co2_inlet_z),
            hole_punch_radius=co2_tube_clearance_radius,
            hole_punch_height=lid_y_height,
        )
    )


def add_co2_boss(cap):
    """Union an annular boss around the CO2 through-hole on the cap
    floor's cavity side: a 2 mm-wall hollow tube spanning the full
    interior cavity height, sealing the through-hole off from the
    foam pour while keeping the bore clear."""
    # Two concentric circles on the same workplane extrude as an
    # annulus via CadQuery's even-odd fill rule.
    boss = (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=co2_boss_y_bottom)
        .moveTo((0, co2_inlet_z))
        .circle(co2_boss_outer_radius)
        .circle(co2_tube_clearance_radius)
        .extrude(co2_boss_y_top - co2_boss_y_bottom)
        .unwrap()
    )
    return cap.union(boss)


def main():
    cap_bottom = build_foam_cap()
    cap_top = add_co2_boss(cut_co2_inlet(cap_bottom))
    lid_bottom = build_foam_cap_lid()
    lid_top = cut_co2_inlet_lid(lid_bottom)
    gasket = build_foam_cap_gasket()

    cap_floor_hole_volume = math.pi * co2_tube_clearance_radius ** 2 * wall_and_floor_thickness
    cap_boss_annular_volume = (
        math.pi
        * (co2_boss_outer_radius ** 2 - co2_tube_clearance_radius ** 2)
        * (co2_boss_y_top - co2_boss_y_bottom)
    )
    lid_hole_volume = math.pi * co2_tube_clearance_radius ** 2 * lid_y_height
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


if __name__ == "__main__":
    main()
