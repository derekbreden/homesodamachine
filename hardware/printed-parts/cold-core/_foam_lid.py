"""Foam lid — the thin PETG cover that closes the body's open +Z top after the
body-pour foam has cured. A flat plate on the outer-shell footprint: six M3
SHCS pass through it into the shell's top-face heat-set inserts, and the CO2
tube passes through at x=0. No foam, no gasket."""

from world_workplane import WorldWorkplane, xy_plane_z_up
from _cold_core_interface import (
    wall_and_floor_thickness,
    outer_shell_x_length,
    outer_shell_y_length,
    corner_round_radius,
    foam_lid_thickness,
    attachment_xy_positions,
    screw_clearance_radius,
    co2_inlet_y,
    co2_inlet_tube_radius,
    build_z_axis_hole_punch,
)


def build_foam_lid():
    """The thin cover: a rounded-corner plate matching the outer-shell footprint,
    with a screw-clearance hole at each of the six attachment positions and the
    CO2 tube pass-through at (x=0, co2_inlet_y)."""
    lid = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .rect(outer_shell_x_length, outer_shell_y_length)
        .extrude(foam_lid_thickness)
        .edges("|Z")
        .fillet(corner_round_radius)
    )
    cut_depth = foam_lid_thickness + 2 * wall_and_floor_thickness
    clearances = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .pushPoints(attachment_xy_positions)
        .circle(screw_clearance_radius)
        .extrude(cut_depth)
    )
    co2 = build_z_axis_hole_punch(
        origin=(0, co2_inlet_y, 0),
        hole_punch_radius=co2_inlet_tube_radius,
        hole_punch_height=cut_depth,
    )
    return lid.cut(clearances).cut(co2).unwrap()
