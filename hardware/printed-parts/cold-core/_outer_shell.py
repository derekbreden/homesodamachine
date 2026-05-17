"""Outer rectangular cup (floor + four perimeter walls) with the
6 corner/mid-side bosses and their heat-set insert pockets."""

from _cold_core_interface import (
    xz_plane_y_up,
    WorldWorkplane,
    wall_and_floor_thickness,
    foam_shell_outer_height,
    outer_shell_x_length,
    outer_shell_z_length,
    foam_cap_attachment_xz_positions,
    screw_boss_size,
    insert_pocket_radius,
    insert_pocket_depth,
)


def build_outer_shell():
    shell = (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=0)
        .rect(outer_shell_x_length, outer_shell_z_length)
        .extrude(foam_shell_outer_height)
        .faces(">Y")
        .shell(-wall_and_floor_thickness)
    )
    bosses = (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=0)
        .pushPoints(foam_cap_attachment_xz_positions)
        .rect(screw_boss_size, screw_boss_size)
        .extrude(foam_shell_outer_height)
    )
    # Heat-set insert pockets — drilled DOWN from the top (top-cap
    # screw threads down) and UP from the bottom (bottom-cap screw
    # threads up).
    top_pockets = (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=foam_shell_outer_height - insert_pocket_depth)
        .pushPoints(foam_cap_attachment_xz_positions)
        .circle(insert_pocket_radius)
        .extrude(insert_pocket_depth)
    )
    bottom_pockets = (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=0)
        .pushPoints(foam_cap_attachment_xz_positions)
        .circle(insert_pocket_radius)
        .extrude(insert_pocket_depth)
    )
    return shell.union(bosses).cut(top_pockets).cut(bottom_pockets).unwrap()
