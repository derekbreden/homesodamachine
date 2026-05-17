"""Foam cap stack: cap (top/bottom 16 mm foam pour tray, printed
twice), lid (sits atop a cap during foam pour), and gasket (TPU 90A
perimeter ring between cap mating edge and outer-shell mating face)."""

import cadquery as cq

from _cold_core_interface import (
    xz_plane_y_up,
    flip_z,
    wall_and_floor_thickness,
    outer_shell_x_length,
    outer_shell_z_length,
    foam_cap_height,
    foam_cap_lid_pour_radius,
    foam_cap_lid_vent_radius,
    foam_cap_lid_hole_inset,
    foam_cap_attachment_xz_positions,
    screw_clearance_radius,
    screw_boss_size,
    gasket_thickness,
    gasket_strip_width,
)


def build_foam_cap():
    cap = (
        cq.Workplane(xz_plane_y_up)
        .rect(outer_shell_x_length, outer_shell_z_length)
        .extrude(foam_cap_height)
        .faces(">Y")
        .shell(-wall_and_floor_thickness)
    )
    boss_points = [flip_z(p) for p in foam_cap_attachment_xz_positions]
    bosses = (
        cq.Workplane(xz_plane_y_up)
        .pushPoints(boss_points)
        .rect(screw_boss_size, screw_boss_size)
        .extrude(foam_cap_height)
    )
    # Screw clearance holes through the full boss height — the screws
    # pass from the cap floor (top in service) all the way to the cap's
    # mating edge (bottom in service).
    clearances = (
        cq.Workplane(xz_plane_y_up)
        .pushPoints(boss_points)
        .circle(screw_clearance_radius)
        .extrude(foam_cap_height)
    )
    cap = cap.union(bosses).cut(clearances)
    # Consolidate the multi-cut Compound into a single Solid for clean
    # STEP export.
    return cap.union(cap)


def build_foam_cap_lid():
    lid = (
        cq.Workplane(xz_plane_y_up)
        .rect(outer_shell_x_length, outer_shell_z_length)
        .extrude(wall_and_floor_thickness)
    )

    pour_x = outer_shell_x_length / 2 - foam_cap_lid_hole_inset
    vent_x = -(outer_shell_x_length / 2 - foam_cap_lid_hole_inset)
    vent_z = outer_shell_z_length / 2 - foam_cap_lid_hole_inset

    pour_hole = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(pour_x, 0, 0))
        .circle(foam_cap_lid_pour_radius)
        .extrude(wall_and_floor_thickness * 3)
    )
    vent_hole_a = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(vent_x, 0, vent_z))
        .circle(foam_cap_lid_vent_radius)
        .extrude(wall_and_floor_thickness * 3)
    )
    vent_hole_b = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(vent_x, 0, -vent_z))
        .circle(foam_cap_lid_vent_radius)
        .extrude(wall_and_floor_thickness * 3)
    )

    lid = lid.cut(pour_hole).cut(vent_hole_a).cut(vent_hole_b)

    boss_points = [flip_z(p) for p in foam_cap_attachment_xz_positions]
    clearances = (
        cq.Workplane(xz_plane_y_up)
        .pushPoints(boss_points)
        .circle(screw_clearance_radius)
        .extrude(wall_and_floor_thickness * 3)
    )
    return lid.cut(clearances)


def build_foam_cap_gasket():
    """TPU 90A gasket between foam_cap mating edge and outer_shell
    mating face. Perimeter ring + 8×8 mm pads at the 6 screw positions
    so the corner-boss screws compress the full boss footprint
    uniformly (a uniform ring would leave them asymmetrically supported
    and seal poorly at the corners). Printed twice."""
    outer = (
        cq.Workplane(xz_plane_y_up)
        .rect(outer_shell_x_length, outer_shell_z_length)
        .extrude(gasket_thickness)
    )
    inner = (
        cq.Workplane(xz_plane_y_up)
        .rect(
            outer_shell_x_length - 2 * gasket_strip_width,
            outer_shell_z_length - 2 * gasket_strip_width,
        )
        .extrude(gasket_thickness)
    )
    gasket = outer.cut(inner)

    boss_points = [flip_z(p) for p in foam_cap_attachment_xz_positions]
    pads = (
        cq.Workplane(xz_plane_y_up)
        .pushPoints(boss_points)
        .rect(screw_boss_size, screw_boss_size)
        .extrude(gasket_thickness)
    )
    holes = (
        cq.Workplane(xz_plane_y_up)
        .pushPoints(boss_points)
        .circle(screw_clearance_radius)
        .extrude(gasket_thickness)
    )
    return gasket.union(pads).cut(holes)
