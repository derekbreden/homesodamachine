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

# Number of reed switches per reservoir (level-sensing fuel gauge —
# see `reservoir/level-sensing.md`). The channel cavity is one
# continuous Z slot regardless of count, so this number doesn't drive
# the channel geometry built below — it lives here as the single
# source of truth for the design count that bom and reservoir both
# need.
reeds_per_reservoir = 4

# X depth of the reed channel cavity. No slope wedge — the reed channel
# is open through the top of the foam shell so reeds drop in from above
# through the cap.
reed_x_depth = 6.0

# Reed channel position in Y, matching the reservoir's ROD_POSITION_Y
# so reeds sit opposite the float-on-rod across the bag-pocket wall.
reed_y_center = -45.0
reed_y_half_w = 4.0

# Reed channel Z: cavity rests on the foam-shell floor at z=w; envelope
# bottom is z=0 so no unsupported floor mid-air. Open through the cap to
# the full outer height so the pre-soldered reed column drops in before
# the cap is installed.
reed_cavity_z_range = (w, foam_shell_outer_height)
reed_envelope_z_range = (0, foam_shell_outer_height)

# Y ranges. The envelope is the cavity padded by w on the foam-exposed
# sides.
reed_cavity_y_range = (reed_y_center - reed_y_half_w, reed_y_center + reed_y_half_w)
reed_envelope_y_range = (reed_cavity_y_range[0] - w, reed_cavity_y_range[1] + w)


def build_reed_channels(side):
    """Reed channel for one ±X reservoir, returned as a single solid
    (new wall material) to union with the foam shell. A Z-slot envelope
    on the outer face of the bag-pocket far ±X wall with the reed cavity
    carved out.

    `side` = ±1 mirrors x across the y-z plane."""
    s = side
    bag_x = s * bag_pocket_outermost_x  # outer face of bag-pocket far ±X wall

    reed_envelope_x_range = (bag_x, bag_x + s * (reed_x_depth + w))
    reed_cavity_x_range = (bag_x, bag_x + s * reed_x_depth)

    reed_envelope = make_box(reed_envelope_x_range, reed_envelope_y_range, reed_envelope_z_range)
    reed_cavity = make_box(reed_cavity_x_range, reed_cavity_y_range, reed_cavity_z_range)
    return reed_envelope.cut(reed_cavity)


def cut_reed_channel_openings(foam_shell):
    """Cut the bag-pocket far ±X wall in the reed channel footprint, so
    the channel is open to the bag pocket interior on its back face.
    Shortens the magnet-to-reed magnetic path and makes the channel
    accessible from the bag-pocket side."""
    for s in (+1, -1):
        wall_x_outer = s * bag_pocket_outermost_x
        wall_x_inner = wall_x_outer - s * w
        reed_opening = make_box((wall_x_inner, wall_x_outer), reed_cavity_y_range, reed_cavity_z_range)
        foam_shell = foam_shell.cut(reed_opening)
    return foam_shell


# ±X offset of cable hole from bulkhead hole, away from the cold-core
# centerline — nudged inboard so the hole sits clear of both the inboard
# flavor-line hole and the +X+Y corner support, keeping PETG around all
# three.
cable_hole_offset_from_bulkhead_hole_x = 4.0


def cut_reed_cable_holes(foam_shell):
    """Cable holes — one per reservoir side — through both the -Y
    bag-pocket wall and the -Y outer shell wall, in -Y direction. The
    reed cable runs through the open bag-pocket bottom to here. Pinned to
    bulkhead_elbow_exit_z (level with the elbow's lateral port and the
    flavor-line hole), at the same y as its side's bulkhead hole."""
    for s in (+1, -1):
        hole_origin = (
            s * (reservoir_bulkhead_port_x + cable_hole_offset_from_bulkhead_hole_x),
            reservoir_bulkhead_port_y,
            bulkhead_elbow_exit_z,
        )
        # Negative height: extrude -Y to bore out through the front (-Y) wall.
        foam_shell = foam_shell.cut(
            build_hole_punch(origin=hole_origin, hole_punch_radius=port_hole_radius, hole_punch_height=-40)
        )
    return foam_shell
