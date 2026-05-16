"""Outer rectangular cup (floor + four perimeter walls) with the
6 corner/mid-side bosses and their heat-set insert pockets."""

import cadquery as cq

from _cold_core_interface import (
    xz_plane_y_up,
    xz_plane_y_up_local,
    wall_and_floor_thickness,
    tank_copper_shell_height,
    outer_shell_x_length,
    outer_shell_z_length,
    foam_cap_attachment_xz_positions,
    screw_boss_size,
    insert_pocket_radius,
    insert_pocket_depth,
)


def build_outer_shell():
    shell = (
        cq.Workplane(xz_plane_y_up)
        .rect(outer_shell_x_length, outer_shell_z_length)
        .extrude(tank_copper_shell_height)
        .faces(">Y")
        .shell(-wall_and_floor_thickness)
    )
    boss_points = xz_plane_y_up_local(foam_cap_attachment_xz_positions)
    bosses = (
        cq.Workplane(xz_plane_y_up)
        .pushPoints(boss_points)
        .rect(screw_boss_size, screw_boss_size)
        .extrude(tank_copper_shell_height)
    )
    # Heat-set insert pockets — drilled DOWN from the top (top-cap
    # screw threads down) and UP from the bottom (bottom-cap screw
    # threads up).
    top_pockets = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=tank_copper_shell_height - insert_pocket_depth)
        .pushPoints(boss_points)
        .circle(insert_pocket_radius)
        .extrude(insert_pocket_depth)
    )
    bottom_pockets = (
        cq.Workplane(xz_plane_y_up)
        .pushPoints(boss_points)
        .circle(insert_pocket_radius)
        .extrude(insert_pocket_depth)
    )
    return shell.union(bosses).cut(top_pockets).cut(bottom_pockets)
