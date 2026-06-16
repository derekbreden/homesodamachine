"""Foam cap stack: cap (top/bottom [16 mm](FOAM_CAP_INTERIOR_HEIGHT) foam pour tray, printed
twice), lid (sits atop a cap during foam pour), and gasket (TPU 90A
perimeter ring between cap mating edge and outer-shell mating face)."""

from world_workplane import WorldWorkplane, xy_plane_z_up
from _cold_core_interface import (
    wall_and_floor_thickness,
    outer_shell_x_length,
    outer_shell_y_length,
    corner_round_radius,
    foam_cap_height,
    foam_cap_lid_pour_radius,
    foam_cap_lid_vent_radius,
    foam_cap_lid_hole_inset,
    foam_cap_attachment_xy_positions,
    screw_clearance_radius,
    gasket_thickness,
    gasket_strip_width,
)
from _outer_shell import build_attachment_bosses

lid_cut_through_depth = wall_and_floor_thickness * 3


def attachment_clearances_extrude(height):
    """Screw-clearance cylinders at every attachment position, extruded +Z by height."""
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .pushPoints(foam_cap_attachment_xy_positions)
        .circle(screw_clearance_radius)
        .extrude(height)
    )


def build_foam_cap(open_down=False):
    """The foam-pour cup. Default opens +Z (floor on the bottom, mouth up) —
    the top cap. open_down=True shells the other face so the cup opens −Z
    (floor on top, mouth down): the bottom cap, seated floor-up against the
    shell's bottom face with its open mouth + lid as the most-negative-Z
    layer. Same footprint and same six-screw clearance pattern either way, so
    the mouth-down bottom cap lands its screws on the shell's existing bosses."""
    cap = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .rect(outer_shell_x_length, outer_shell_y_length)
        .extrude(foam_cap_height)
        .edges("|Z")
        .fillet(corner_round_radius)
        .faces("<Z" if open_down else ">Z")
        .shell(-wall_and_floor_thickness)
    )
    # Same ⌀ boss + teardrop webs as the outer shell.
    bosses = build_attachment_bosses(foam_cap_height)
    # Screw clearance passes the full cap height, floor through to mating edge.
    clearances = attachment_clearances_extrude(foam_cap_height)
    return cap.union(bosses).cut(clearances).unwrap()


def build_foam_cap_lid():
    lid = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .rect(outer_shell_x_length, outer_shell_y_length)
        .extrude(wall_and_floor_thickness)
        .edges("|Z")
        .fillet(corner_round_radius)
    )

    # Pour hole on the +X half at y=0; vent holes mirrored across y at the −X corners.
    inset_x = outer_shell_x_length / 2 - foam_cap_lid_hole_inset
    inset_y = outer_shell_y_length / 2 - foam_cap_lid_hole_inset
    pour_xy = (inset_x, 0)
    vent_plus_y_xy = (-inset_x, inset_y)
    vent_minus_y_xy = (-inset_x, -inset_y)

    def cut_hole(anchor_xy, radius):
        return (
            WorldWorkplane(xy_plane_z_up)
            .workplane(offset=0)
            .moveTo(anchor_xy)
            .circle(radius)
            .extrude(lid_cut_through_depth)
        )

    pour_hole = cut_hole(pour_xy, foam_cap_lid_pour_radius)
    vent_hole_plus_y = cut_hole(vent_plus_y_xy, foam_cap_lid_vent_radius)
    vent_hole_minus_y = cut_hole(vent_minus_y_xy, foam_cap_lid_vent_radius)
    clearances = attachment_clearances_extrude(lid_cut_through_depth)
    return lid.cut(pour_hole).cut(vent_hole_plus_y).cut(vent_hole_minus_y).cut(clearances).unwrap()


def build_foam_cap_gasket():
    """TPU 90A gasket between foam_cap mating edge and outer_shell mating
    face. Rounded-corner perimeter ring matching the shell's rounded outer
    wall, ring width uniform through the corner, + a boss-shaped pad
    (same boss + teardrop-web shape as the shell/cap) at each of the 6 screw
    positions. Printed twice."""
    outer = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .rect(outer_shell_x_length, outer_shell_y_length)
        .extrude(gasket_thickness)
        .edges("|Z")
        .fillet(corner_round_radius)
    )
    inner = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .rect(
            outer_shell_x_length - 2 * gasket_strip_width,
            outer_shell_y_length - 2 * gasket_strip_width,
        )
        .extrude(gasket_thickness)
        .edges("|Z")
        .fillet(corner_round_radius - gasket_strip_width)
    )
    gasket = outer.cut(inner)
    pads = build_attachment_bosses(gasket_thickness)
    holes = attachment_clearances_extrude(gasket_thickness)
    return gasket.union(pads).cut(holes).unwrap()
