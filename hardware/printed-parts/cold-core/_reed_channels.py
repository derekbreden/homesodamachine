"""Reed-and-cable channel system for level sensing — built into the
foam shell on the outer face of each bag-pocket far ±X wall."""

from _cold_core_interface import (
    wall_and_floor_thickness,
    foam_shell_outer_height,
    bag_pocket_outermost_x,
    reservoir_bulkhead_port_x,
    reservoir_bulkhead_port_y,
    bulkhead_elbow_exit_z,
    port_hole_radius,
    make_box,
    build_hole_punch,
)

w = wall_and_floor_thickness

# Reed switches per reservoir, level-sensing fuel gauge — see
# `reservoir/level-sensing.md`.
reeds_per_reservoir = 4

# Reed channel cavity is open through the top of the foam shell; reeds
# drop in from above through the cap.
reed_x_depth = 6.0

# Matches the reservoir's ROD_POSITION_Y: reeds sit opposite the
# float-on-rod across the bag-pocket wall.
reed_y_center = -45.0
reed_y_half_w = 4.0

# Cavity rests on the foam-shell floor at z=w; envelope bottom at z=0.
# Open through the cap to full outer height: the pre-soldered reed
# column drops in before the cap is installed.
reed_cavity_z_range = (w, foam_shell_outer_height)
reed_envelope_z_range = (0, foam_shell_outer_height)

reed_cavity_y_range = (reed_y_center - reed_y_half_w, reed_y_center + reed_y_half_w)
reed_envelope_y_range = (reed_cavity_y_range[0] - w, reed_cavity_y_range[1] + w)


def build_reed_channels(side):
    """Reed channel for one ±X reservoir: a Z-slot envelope on the outer
    face of the bag-pocket far ±X wall with the reed cavity carved out,
    new wall material to union with the foam shell.

    `side` = ±1 mirrors x across the y-z plane."""
    s = side
    bag_x = s * bag_pocket_outermost_x  # outer face of bag-pocket far ±X wall

    reed_envelope_x_range = (bag_x, bag_x + s * (reed_x_depth + w))
    reed_cavity_x_range = (bag_x, bag_x + s * reed_x_depth)

    reed_envelope = make_box(reed_envelope_x_range, reed_envelope_y_range, reed_envelope_z_range)
    reed_cavity = make_box(reed_cavity_x_range, reed_cavity_y_range, reed_cavity_z_range)
    return reed_envelope.cut(reed_cavity)


def cut_reed_channel_openings(foam_shell):
    """Cut the bag-pocket far ±X wall in the reed channel footprint: the
    channel opens to the bag-pocket interior on its back face, shortening
    the magnet-to-reed magnetic path across the wall."""
    for s in (+1, -1):
        wall_x_outer = s * bag_pocket_outermost_x
        wall_x_inner = wall_x_outer - s * w
        reed_opening = make_box((wall_x_inner, wall_x_outer), reed_cavity_y_range, reed_cavity_z_range)
        foam_shell = foam_shell.cut(reed_opening)
    return foam_shell


# Cable hole sits inboard of the bulkhead hole, clear of both the
# inboard flavor-line hole and the +X+Y corner support, with PETG around
# all three.
cable_hole_offset_from_bulkhead_hole_x = 4.0


def cut_reed_cable_holes(foam_shell):
    """Cable holes, one per reservoir side, in +Y through both the +Y
    bag-pocket wall and the +Y outer shell wall; the reed cable runs
    through the open bag-pocket bottom to here. At bulkhead_elbow_exit_z
    (level with the elbow's lateral port and the flavor-line hole), at
    the same y as its side's bulkhead hole."""
    for s in (+1, -1):
        hole_origin = (
            s * (reservoir_bulkhead_port_x + cable_hole_offset_from_bulkhead_hole_x),
            reservoir_bulkhead_port_y,
            bulkhead_elbow_exit_z,
        )
        foam_shell = foam_shell.cut(build_hole_punch(origin=hole_origin, hole_punch_radius=port_hole_radius))
    return foam_shell
