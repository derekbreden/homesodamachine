"""Foam cap stack: cap (top/bottom [16 mm](FOAM_CAP_INTERIOR_HEIGHT) foam pour tray, printed
twice), lid (sits atop a cap during foam pour), and gasket (TPU 90A
perimeter ring between cap mating edge and outer-shell mating face)."""

from world_workplane import WorldWorkplane, xy_plane_z_up
from _cold_core_interface import (
    wall_and_floor_thickness,
    outer_shell_x_length,
    outer_shell_y_length,
    corner_round_radius,
    cap_conduits,
    cap_conduit_bore_radius,
    cap_conduit_boss_radius,
    foam_cap_height,
    foam_cap_lid_pour_radius,
    foam_cap_lid_vent_radius,
    foam_cap_lid_hole_inset,
    attachment_xy_positions,
    screw_clearance_radius,
    head_cbore_radius,
    head_cbore_depth,
    head_pad_height,
    head_pad_slip,
    gasket_thickness,
    gasket_strip_width,
)
from _outer_shell import build_attachment_bosses

# The lid is one wall of plate plus a head pad at each of the six stations.
lid_total_height = wall_and_floor_thickness + head_pad_height
lid_cut_through_depth = lid_total_height + wall_and_floor_thickness


def attachment_clearances_extrude(height):
    """Screw-clearance cylinders at every attachment position, extruded +Z by height."""
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .pushPoints(attachment_xy_positions)
        .circle(screw_clearance_radius)
        .extrude(height)
    )


def build_conduit_columns(height):
    """Every cap conduit's column, extruded +Z by height from z=0."""
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .pushPoints(list(cap_conduits.values()))
        .circle(cap_conduit_boss_radius)
        .extrude(height)
    )


def build_conduit_bores(height, radius=cap_conduit_bore_radius):
    """Every cap conduit's bore, extruded +Z by height from z=0."""
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .pushPoints(list(cap_conduits.values()))
        .circle(radius)
        .extrude(height)
    )


def _relief_z0(open_down):
    """Z the mouth-end boss relief starts at, in the cap's own frame — always
    the material side of the open face, which is +Z from a mouth-down cup's
    mouth at 0 and −Z from a mouth-up cup's at foam_cap_height."""
    return 0.0 if open_down else foam_cap_height - head_pad_height


def build_foam_cap(open_down=False):
    """The foam-pour cup. Default opens +Z (floor on the bottom, mouth up) —
    the top cap. open_down=True shells the other face so the cup opens −Z
    (floor on top, mouth down): the bottom cap, seated floor-up against the
    shell's bottom face with its open mouth + lid as the most-negative-Z
    layer. Same footprint and same six-screw clearance pattern either way, so
    the mouth-down bottom cap lands its screws on the shell's existing bosses.

    The six boss columns run the cup's full height but stop head_pad_height
    short of the mouth: that relief is where the lid's head pads go, and the
    slip it carries is what lets them in.

    A CONDUIT column runs the full height to the mouth rim, where the lid's plate lands on
    it, and carries a ⌀[6.5 mm](FCAP_BORE_D) bore through itself and the floor under it. Only
    the mouth-up top cap has them: `cap_conduits` are the lines that leave by the top, and
    the service bay is on the top cap's outer face."""
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
    # The mouth-end relief: the lid's pad section, one slip larger all round.
    relief = build_attachment_bosses(head_pad_height, oversize=head_pad_slip).translate(
        (0, 0, _relief_z0(open_down))
    )
    # Screw clearance passes the full cap height, floor through to mating edge.
    clearances = attachment_clearances_extrude(foam_cap_height)
    cap = cap.union(bosses)
    if not open_down:
        cap = cap.union(build_conduit_columns(foam_cap_height))
    cap = cap.cut(relief).cut(clearances)
    if not open_down:
        cap = cap.cut(build_conduit_bores(foam_cap_height))
    return cap.unwrap()


def build_foam_cap_lid(open_down=False):
    """The pour lid for the cap built with the same `open_down` — the plate
    that closes its mouth, with a head pad standing off the mouth-facing side
    at each of the six stations. Authored outer-face-out either way: the
    default (top cap, mouth up) carries its pads on −Z under the plate, and
    open_down=True (bottom cap, mouth down) carries them on +Z above it. Each
    pad is counterbored from the outer face, so the head lands
    head_seat_recess under a face that is otherwise a plane."""
    plate_z0 = 0.0 if open_down else head_pad_height
    pad_z0 = wall_and_floor_thickness if open_down else 0.0
    cbore_z0 = 0.0 if open_down else lid_total_height - head_cbore_depth

    lid = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=plate_z0)
        .rect(outer_shell_x_length, outer_shell_y_length)
        .extrude(wall_and_floor_thickness)
        .edges("|Z")
        .fillet(corner_round_radius)
    )
    # The pads are the cap boss's own section — what its columns gave up.
    lid = lid.union(build_attachment_bosses(head_pad_height).translate((0, 0, pad_z0)))
    head_cbores = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=cbore_z0)
        .pushPoints(attachment_xy_positions)
        .circle(head_cbore_radius)
        .extrude(head_cbore_depth)
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
    lid = (
        lid.cut(pour_hole)
        .cut(vent_hole_plus_y)
        .cut(vent_hole_minus_y)
        .cut(head_cbores)
        .cut(clearances)
    )
    # The conduit's bore continues through the plate the column's top lands on. The
    # mouth-down bottom lid closes the stack's other end and takes none.
    if not open_down:
        lid = lid.cut(build_conduit_bores(lid_cut_through_depth))
    return lid.unwrap()


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
