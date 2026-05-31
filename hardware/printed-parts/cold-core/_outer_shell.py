"""Outer rectangular cup (floor + four perimeter walls) with the
6 cylindrical corner/mid-side bosses and their heat-set insert pockets.
Each boss is a ⌀screw_boss_size cylinder inscribed in the former square
footprint — tangent to both wall faces at each corner — so the corner
boss can be wrapped by a rounded wall."""

from world_workplane import WorldWorkplane, xy_plane_z_up
from _cold_core_interface import (
    wall_and_floor_thickness,
    foam_shell_outer_height,
    outer_shell_x_length,
    outer_shell_y_length,
    foam_cap_attachment_xy_positions,
    screw_boss_size,
    insert_pocket_radius,
    insert_pocket_depth,
)


def build_outer_shell():
    shell = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .rect(outer_shell_x_length, outer_shell_y_length)
        .extrude(foam_shell_outer_height)
        .faces(">Z")
        .shell(-wall_and_floor_thickness)
    )
    bosses = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .pushPoints(foam_cap_attachment_xy_positions)
        .circle(screw_boss_size / 2)
        .extrude(foam_shell_outer_height)
    )

    # Heat-set insert pockets on both faces — each cap's M3 SHCS threads
    # into an insert pressed from its own face, so every boss carries a
    # pocket at z=0 and another at z=foam_shell_outer_height.
    def insert_pockets_at(z_floor):
        return (
            WorldWorkplane(xy_plane_z_up)
            .workplane(offset=z_floor)
            .pushPoints(foam_cap_attachment_xy_positions)
            .circle(insert_pocket_radius)
            .extrude(insert_pocket_depth)
        )
    bottom_pockets = insert_pockets_at(0)
    top_pockets = insert_pockets_at(foam_shell_outer_height - insert_pocket_depth)
    return shell.union(bosses).cut(bottom_pockets).cut(top_pockets).unwrap()
