"""Reed-and-cable channel system for level sensing — built into the
foam shell on the outer face of each bag-pocket far ±X wall."""

import cadquery as cq

from world_workplane import WorldWorkplane, xy_plane_z_up, xz_plane_y_up
from _cold_core_interface import (
    wall_and_floor_thickness,
    foam_shell_outer_height,
    bag_pocket_width,
    bag_pocket_outermost_x,
    bag_pocket_corner_inner_radius,
    reservoir_bulkhead_port_x,
    reservoir_bulkhead_port_y,
    reservoir_bulkhead_port_z,
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

# X depth of the cable channel cavity (also the rise of the 45°
# printability slope on the cavity ceiling — 1:1 slope).
cable_x_depth = 5.0

# X depth of the reed channel cavity. No slope wedge — the reed channel
# is open through the top of the foam shell so reeds drop in from above
# through the cap.
reed_x_depth = 6.0

# Reed channel position in Y, matching the reservoir's ROD_POSITION_Y
# so reeds sit opposite the float-on-rod across the bag-pocket wall.
reed_y_center = -45.0
reed_y_half_w = 4.0

# +Y extent of the horizontal cable channel.
cable_y_max = 70.5

# Outer radius of the bag-pocket +Y corner fillet (inner-radius + w).
outer_corner_r = w + bag_pocket_corner_inner_radius

# Cable channel Z: shared with the +Y cable hole so the cable runs
# straight from channel to hole with no bend. Cavity rests on the
# foam-shell floor at z=w; envelope bottom is z=0 so no unsupported
# floor mid-air. Reed channel is open through the cap so the pre-
# soldered reed column can drop in before the cap is installed.
cable_z_height = 8.0
cable_cavity_z_range = (w, w + cable_z_height)
cable_envelope_z_range = (0, cable_cavity_z_range[1] + w)
cable_z_center = sum(cable_cavity_z_range) / 2
reed_cavity_z_range = (cable_cavity_z_range[0], foam_shell_outer_height)
reed_envelope_z_range = (cable_envelope_z_range[0], foam_shell_outer_height)

# Y ranges. Reed and cable cavities share their lower Y bound (the
# reed-side end of the channel); envelopes are cavities padded by w
# on the foam-exposed sides.
reed_cavity_y_range = (reed_y_center - reed_y_half_w, reed_y_center + reed_y_half_w)
reed_envelope_y_range = (reed_cavity_y_range[0] - w, reed_cavity_y_range[1] + w)
cable_cavity_y_range = (reed_cavity_y_range[0], cable_y_max)
cable_envelope_y_range = (reed_envelope_y_range[0], cable_y_max + w)

# Apex Z of the 45° slope wedge on the cable channel ceiling: rises
# +cable_x_depth in Z from the top of the cavity/envelope.
cable_cavity_wedge_apex_z = cable_cavity_z_range[1] + cable_x_depth
cable_envelope_wedge_apex_z = cable_envelope_z_range[1] + cable_x_depth


def build_reed_channels(side):
    """Reed-and-cable channel system for one ±X reservoir, returned as
    a single solid (new wall material) to union with the foam shell.

    `side` = ±1 mirrors x across the y-z plane."""
    s = side

    bag_x = s * bag_pocket_outermost_x  # outer face of bag-pocket far ±X wall
    y_outer = bag_pocket_width / 2

    fillet_axis_x = bag_x - s * outer_corner_r
    fillet_axis_y = y_outer - w - outer_corner_r

    wedge_apex_at_wall = (bag_x, cable_envelope_wedge_apex_z)
    corner_arc_terminus = (fillet_axis_x, cable_envelope_wedge_apex_z + outer_corner_r)

    reed_envelope_x_range = (bag_x, bag_x + s * (reed_x_depth + w))
    reed_cavity_x_range = (bag_x, bag_x + s * reed_x_depth)

    reed_envelope = make_box(reed_envelope_x_range, reed_envelope_y_range, reed_envelope_z_range)
    reed_cavity = make_box(reed_cavity_x_range, reed_cavity_y_range, reed_cavity_z_range)

    cable_envelope_x_range = (bag_x, bag_x + s * (cable_x_depth + w))
    cable_cavity_x_range = (bag_x, bag_x + s * cable_x_depth)

    cable_envelope = make_box(cable_envelope_x_range, cable_envelope_y_range, cable_envelope_z_range)
    cable_cavity = make_box(cable_cavity_x_range, cable_cavity_y_range, cable_cavity_z_range)

    # 45° rise from channel-outer face to bag-pocket-wall side,
    # self-supporting in Z-up print so no bridging is needed.
    def slope_wedge(z_low, y_range):
        y_min, y_max = y_range
        base_at_wall = (bag_x, z_low)
        base_at_outer = (bag_x + s * cable_x_depth, z_low)
        apex_at_wall = (bag_x, z_low + cable_x_depth)
        return (
            WorldWorkplane(xz_plane_y_up)
            .workplane(offset=y_min)
            .polyline([base_at_wall, base_at_outer, apex_at_wall])
            .close()
            .extrude(y_max - y_min)
            .unwrap()
        )
    cable_envelope = cable_envelope.union(slope_wedge(cable_envelope_z_range[1], cable_envelope_y_range))
    cable_cavity = cable_cavity.union(slope_wedge(cable_cavity_z_range[1], cable_cavity_y_range))

    # Wraps the channel-outer face around the bag-pocket +Y corner
    # fillet so the channel meets the bag-pocket wall continuously.
    # The inner-fillet cut carves out the corner radius itself.
    missing_wall_profile = [
        (bag_x, cable_envelope_z_range[0]),
        wedge_apex_at_wall,
        corner_arc_terminus,
        (fillet_axis_x, cable_envelope_z_range[0]),
    ]
    missing_wall = (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=y_outer)
        .polyline(missing_wall_profile).close()
        .extrude(-outer_corner_r)
        .unwrap()
    )
    inner_fillet_cut = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=cable_envelope_wedge_apex_z)
        .moveTo((fillet_axis_x, fillet_axis_y))
        .circle(outer_corner_r)
        .extrude(outer_corner_r)
    )
    missing_wall = missing_wall.cut(inner_fillet_cut.unwrap())

    # A channel = envelope (wall material) with cavity carved out. The
    # two channels' envelopes overlap at the corner where they meet,
    # so cavities must be cut from the combined envelope; cutting each
    # cavity from only its own envelope would leave the other channel's
    # wall material inside the cavity.
    total_envelope = reed_envelope.union(cable_envelope).union(missing_wall)
    total_cavity = reed_cavity.union(cable_cavity)
    channels = total_envelope.cut(total_cavity)
    return channels


def cut_reed_channel_openings(foam_shell):
    """Cut the bag-pocket far ±X wall in the reed-and-cable channel
    footprint, so each channel is open to the bag pocket interior on
    its back face. Shortens the magnet-to-reed magnetic path and
    makes the channels accessible from the bag-pocket side."""
    for s in (+1, -1):
        wall_x_outer = s * bag_pocket_outermost_x
        wall_x_inner = wall_x_outer - s * w
        corner_x_inner = wall_x_outer - s * outer_corner_r

        wall_x_range = (wall_x_inner, wall_x_outer)
        corner_x_range = (corner_x_inner, wall_x_outer)

        reed_opening = make_box(wall_x_range, reed_cavity_y_range, reed_cavity_z_range)
        cable_opening = make_box(corner_x_range, cable_cavity_y_range, cable_cavity_z_range)
        foam_shell = foam_shell.cut(reed_opening).cut(cable_opening)

        # Extends the cavity ceiling's 45° slope through the bag-pocket
        # wall and around the +Y corner fillet, removing the trapezoidal
        # slice of wall material under it.
        y_min, y_max = cable_cavity_y_range
        slope_wall_profile = [
            (corner_x_inner, cable_cavity_z_range[1]),
            (wall_x_outer, cable_cavity_z_range[1]),
            (wall_x_outer, cable_cavity_wedge_apex_z),
            (corner_x_inner, cable_cavity_wedge_apex_z + outer_corner_r),
        ]
        slope_wall_cut = (
            WorldWorkplane(xz_plane_y_up)
            .workplane(offset=y_min)
            .polyline(slope_wall_profile).close()
            .extrude(y_max - y_min)
            .unwrap()
        )
        foam_shell = foam_shell.cut(slope_wall_cut)

    return foam_shell


# ±X offset of cable hole from bulkhead hole, away from the cold-core
# centerline. Combined with the z separation below, leaves plenty of
# PETG between the two ⌀6.5 holes.
cable_hole_offset_from_bulkhead_hole_x = 8.0
cable_to_bulkhead_z_separation = abs(cable_z_center - reservoir_bulkhead_port_z)


def cut_reed_cable_holes(foam_shell):
    """Cable holes — one per reservoir side — through both the +Y
    bag-pocket wall and the +Y outer shell wall, in +Y direction.
    Sits at the same y as its side's bulkhead hole and at cable_z_center
    so the cable runs straight from channel to hole."""
    for s in (+1, -1):
        hole_origin = (
            s * (reservoir_bulkhead_port_x + cable_hole_offset_from_bulkhead_hole_x),
            reservoir_bulkhead_port_y,
            cable_z_center,
        )
        foam_shell = foam_shell.cut(build_hole_punch(origin=hole_origin, hole_punch_radius=port_hole_radius))
    return foam_shell
