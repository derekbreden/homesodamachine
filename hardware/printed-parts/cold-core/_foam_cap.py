"""Foam cap stack: cap (top/bottom 16 mm foam pour tray, printed
twice), lid (sits atop a cap during foam pour), and gasket (TPU 90A
perimeter ring between cap mating edge and outer-shell mating face)."""

from world_workplane import WorldWorkplane, xy_plane_z_up
from _cold_core_interface import (
    wall_and_floor_thickness,
    outer_shell_x_length,
    outer_shell_y_length,
    foam_cap_height,
    foam_cap_lid_pour_radius,
    foam_cap_lid_vent_radius,
    foam_cap_lid_hole_inset,
    foam_cap_attachment_xy_positions,
    screw_clearance_radius,
    screw_boss_size,
    gasket_thickness,
    gasket_strip_width,
)

# Cut-through depth for lid features — any value ≥ wall_and_floor_thickness
# fully traverses the lid. 3× gives margin without making the depth
# look semantically meaningful.
lid_cut_through_depth = wall_and_floor_thickness * 3


def attachment_pads_extrude(height):
    """Square pads at every attachment position, extruded +Z by height.
    Used as cap-boss footprints and as boss-shaped gasket compression
    pads."""
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .pushPoints(foam_cap_attachment_xy_positions)
        .rect(screw_boss_size, screw_boss_size)
        .extrude(height)
    )


def attachment_clearances_extrude(height):
    """Screw-clearance cylinders at every attachment position, extruded
    +Z by height. Used as the cut tool through cap, lid, and gasket."""
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .pushPoints(foam_cap_attachment_xy_positions)
        .circle(screw_clearance_radius)
        .extrude(height)
    )


def build_foam_cap():
    cap = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .rect(outer_shell_x_length, outer_shell_y_length)
        .extrude(foam_cap_height)
        .faces(">Z")
        .shell(-wall_and_floor_thickness)
    )
    bosses = attachment_pads_extrude(foam_cap_height)
    # Clearances run the full boss height so the screw passes from the
    # cap floor (top in service) through to the mating edge.
    clearances = attachment_clearances_extrude(foam_cap_height)
    return cap.union(bosses).cut(clearances).unwrap()


def build_foam_cap_lid():
    lid = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .rect(outer_shell_x_length, outer_shell_y_length)
        .extrude(wall_and_floor_thickness)
    )

    # 2D anchor points on the lid plane. Pour hole on the +X half at
    # y=0; vent holes mirrored across y at the −X corners.
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
    """TPU 90A gasket between foam_cap mating edge and outer_shell
    mating face. Perimeter ring + 8×8 mm pads at the 6 screw positions
    so the corner-boss screws compress the full boss footprint
    uniformly (a uniform ring would leave them asymmetrically supported
    and seal poorly at the corners). Printed twice."""
    outer = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .rect(outer_shell_x_length, outer_shell_y_length)
        .extrude(gasket_thickness)
    )
    inner = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .rect(
            outer_shell_x_length - 2 * gasket_strip_width,
            outer_shell_y_length - 2 * gasket_strip_width,
        )
        .extrude(gasket_thickness)
    )
    gasket = outer.cut(inner)
    pads = attachment_pads_extrude(gasket_thickness)
    holes = attachment_clearances_extrude(gasket_thickness)
    return gasket.union(pads).cut(holes).unwrap()
