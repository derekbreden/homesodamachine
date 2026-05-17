"""Foam cap stack: cap (top/bottom 16 mm foam pour tray, printed
twice), lid (sits atop a cap during foam pour), and gasket (TPU 90A
perimeter ring between cap mating edge and outer-shell mating face)."""

from _cold_core_interface import (
    xz_plane_y_up,
    WorldWorkplane,
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

# Cut-through depth for lid features — any value ≥ the lid's Y extent
# fully traverses it; 3× gives margin without depending on the exact
# lid thickness.
lid_cut_through_depth = wall_and_floor_thickness * 3


def boss_pads_extrude(height):
    """Square pads at every attachment position, extruded +Y by height.
    Used both as cap/gasket boss footprints and as the boss-shaped
    gasket compression pads."""
    return (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=0)
        .pushPoints(foam_cap_attachment_xz_positions)
        .rect(screw_boss_size, screw_boss_size)
        .extrude(height)
    )


def boss_clearances_extrude(height):
    """Screw-clearance cylinders at every attachment position, extruded
    +Y by height. Used as the cut tool through cap, lid, and gasket."""
    return (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=0)
        .pushPoints(foam_cap_attachment_xz_positions)
        .circle(screw_clearance_radius)
        .extrude(height)
    )


def build_foam_cap():
    cap = (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=0)
        .rect(outer_shell_x_length, outer_shell_z_length)
        .extrude(foam_cap_height)
        .faces(">Y")
        .shell(-wall_and_floor_thickness)
    )
    bosses = boss_pads_extrude(foam_cap_height)
    # Screw clearances run the full boss height: the screws pass from
    # the cap floor (top in service) all the way to the mating edge.
    clearances = boss_clearances_extrude(foam_cap_height)
    return cap.union(bosses).cut(clearances).unwrap()


def build_foam_cap_lid():
    lid = (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=0)
        .rect(outer_shell_x_length, outer_shell_z_length)
        .extrude(wall_and_floor_thickness)
    )

    # 2D anchor points on the lid plane. Pour hole on the +X half at
    # z=0; vent holes mirrored across z at the −X corners.
    inset_x = outer_shell_x_length / 2 - foam_cap_lid_hole_inset
    inset_z = outer_shell_z_length / 2 - foam_cap_lid_hole_inset
    pour_xz = (inset_x, 0)
    vent_plus_z_xz = (-inset_x, inset_z)
    vent_minus_z_xz = (-inset_x, -inset_z)

    def cut_hole(anchor_xz, radius):
        return (
            WorldWorkplane(xz_plane_y_up)
            .workplane(offset=0)
            .moveTo(anchor_xz)
            .circle(radius)
            .extrude(lid_cut_through_depth)
        )

    pour_hole = cut_hole(pour_xz, foam_cap_lid_pour_radius)
    vent_hole_plus_z = cut_hole(vent_plus_z_xz, foam_cap_lid_vent_radius)
    vent_hole_minus_z = cut_hole(vent_minus_z_xz, foam_cap_lid_vent_radius)
    clearances = boss_clearances_extrude(lid_cut_through_depth)
    return lid.cut(pour_hole).cut(vent_hole_plus_z).cut(vent_hole_minus_z).cut(clearances).unwrap()


def build_foam_cap_gasket():
    """TPU 90A gasket between foam_cap mating edge and outer_shell
    mating face. Perimeter ring + 8×8 mm pads at the 6 screw positions
    so the corner-boss screws compress the full boss footprint
    uniformly (a uniform ring would leave them asymmetrically supported
    and seal poorly at the corners). Printed twice."""
    outer = (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=0)
        .rect(outer_shell_x_length, outer_shell_z_length)
        .extrude(gasket_thickness)
    )
    inner = (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=0)
        .rect(
            outer_shell_x_length - 2 * gasket_strip_width,
            outer_shell_z_length - 2 * gasket_strip_width,
        )
        .extrude(gasket_thickness)
    )
    gasket = outer.cut(inner)
    pads = boss_pads_extrude(gasket_thickness)
    holes = boss_clearances_extrude(gasket_thickness)
    return gasket.union(pads).cut(holes).unwrap()
