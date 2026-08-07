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
    reed_x_depth,
    level_rod_y,
    front_port_z,
    make_box,
    cut_pour_band_pass_through,
)

w = wall_and_floor_thickness

# Reed switches per reservoir, level-sensing fuel gauge — see
# `reservoir/level-sensing.md`.
reeds_per_reservoir = 4

# Reed channel cavity is open through the top of the foam shell; reeds
# drop in from above before the lid goes on. Cavity depth (reed_x_depth) is
# shared via the interface — the outer_shell X width is sized to butt it.

# The reservoir's own ROD_POSITION_Y: reeds sit opposite the float-on-rod
# across the bag-pocket wall, so this is not a second station that has to be
# kept level with that one — it IS that one (`_cold_core_interface.level_rod_y`).
reed_y_center = level_rod_y
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

# Which reservoir's cable takes which front-field station. +X is A, −X is B.
_CABLE_STATION = {+1: "reed-cable-a", -1: "reed-cable-b"}


def cut_reed_cable_holes(foam_shell):
    """Cable holes, one per reservoir side: −Y through the −Y bag-pocket wall onto
    the port lane, and out the front field at that side's station. The reed cable
    runs through the open bag-pocket bottom to the pocket bore, leaving at
    bulkhead_elbow_exit_z (level with the elbow's lateral port and the flavor-line
    hole) at the same y as its side's bulkhead hole, then climbs the lane west to
    its station — the two stations one bore pitch apart, above both flavor lines'."""
    for s in (+1, -1):
        foam_shell = cut_pour_band_pass_through(
            foam_shell,
            pocket_hole_x=s * (reservoir_bulkhead_port_x + cable_hole_offset_from_bulkhead_hole_x),
            y=reservoir_bulkhead_port_y,
            z=bulkhead_elbow_exit_z,
            exit_z=front_port_z(_CABLE_STATION[s]),
            hole_punch_radius=port_hole_radius,
        )
    return foam_shell
