"""Reed-and-cable channel system for level sensing — built into the
foam shell on the outer face of each bag-pocket far ±X wall."""

import cadquery as cq

from _cold_core_interface import (
    xz_plane_y_up,
    xy_plane_z_up,
    flip_z,
    wall_and_floor_thickness,
    foam_shell_outer_height,
    bag_pocket_width,
    bag_pocket_outermost_x,
    bag_pocket_corner_inner_radius,
    reservoir_bulkhead_port_x,
    build_a_hole_punch,
)

w = wall_and_floor_thickness

# X depth of the cable channel cavity (also the rise of the 45°
# printability slope on the cavity ceiling — 1:1 slope).
cable_x_depth = 5.0

# Reed channel position in Z, matching the reservoir's ROD_POSITION_Z
# so reeds sit opposite the float-on-rod across the bag-pocket wall.
reed_z_center = -45.0
reed_z_half_w = 4.0

# +Z extent of the horizontal cable channel.
cable_z_max = 70.5

# Outer radius of the bag-pocket +Z corner fillet (inner-radius + w).
outer_corner_r = w + bag_pocket_corner_inner_radius

# Cable channel Y: shared with the +Z cable hole so the cable runs
# straight from channel to hole with no bend. Cavity rests on the
# foam-shell floor at y=w; envelope bottom is y=0 so no unsupported
# floor mid-air. Reed channel is open through the cap so the pre-
# soldered reed column can drop in before the cap is installed.
cable_y_height = 8.0
cable_cavity_y_range = (w, w + cable_y_height)
cable_envelope_y_range = (0, cable_cavity_y_range[1] + w)
cable_y_center = sum(cable_cavity_y_range) / 2
reed_cavity_y_range = (cable_cavity_y_range[0], foam_shell_outer_height)
reed_envelope_y_range = (cable_envelope_y_range[0], foam_shell_outer_height)

# Z ranges. Reed and cable cavities share their lower Z bound (the
# reed-side end of the channel); envelopes are cavities padded by w
# on the foam-exposed sides.
reed_cavity_z_range = (reed_z_center - reed_z_half_w, reed_z_center + reed_z_half_w)
reed_envelope_z_range = (reed_cavity_z_range[0] - w, reed_cavity_z_range[1] + w)
cable_cavity_z_range = (reed_cavity_z_range[0], cable_z_max)
cable_envelope_z_range = (reed_envelope_z_range[0], cable_z_max + w)

# Apex Y of the 45° slope wedge on the cable channel ceiling: rises
# +cable_x_depth in Y from the top of the cavity/envelope.
cable_cavity_wedge_apex_y = cable_cavity_y_range[1] + cable_x_depth
cable_envelope_wedge_apex_y = cable_envelope_y_range[1] + cable_x_depth


def make_box(x_range, y_range, z_range):
    """Axis-aligned box from world-coordinate ranges in each axis."""
    x_min, x_max = min(x_range), max(x_range)
    y_min, y_max = min(y_range), max(y_range)
    z_min, z_max = min(z_range), max(z_range)
    return (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=y_min)
        .moveTo(*flip_z(((x_min + x_max) / 2, (z_min + z_max) / 2)))
        .rect(x_max - x_min, z_max - z_min)
        .extrude(y_max - y_min)
    )


def build_reed_channels(side):
    """Reed-and-cable channel system for one ±X reservoir, returned as
    a single solid (new wall material) to union with the foam shell.

    `side` = ±1 mirrors x across the y-z plane."""
    s = side
    reed_x_depth = 6.0

    bag_x = s * bag_pocket_outermost_x  # outer face of bag-pocket far ±X wall
    z_outer = bag_pocket_width / 2

    fillet_axis_x = bag_x - s * outer_corner_r
    fillet_axis_z = z_outer - w - outer_corner_r

    wedge_apex_at_wall = (bag_x, cable_envelope_wedge_apex_y)
    corner_arc_terminus = (fillet_axis_x, cable_envelope_wedge_apex_y + outer_corner_r)

    reed_envelope_x_range = (bag_x, bag_x + s * (reed_x_depth + w))
    reed_cavity_x_range = (bag_x, bag_x + s * reed_x_depth)

    reed_envelope = make_box(reed_envelope_x_range, reed_envelope_y_range, reed_envelope_z_range)
    reed_cavity = make_box(reed_cavity_x_range, reed_cavity_y_range, reed_cavity_z_range)

    cable_envelope_x_range = (bag_x, bag_x + s * (cable_x_depth + w))
    cable_cavity_x_range = (bag_x, bag_x + s * cable_x_depth)

    cable_envelope = make_box(cable_envelope_x_range, cable_envelope_y_range, cable_envelope_z_range)
    cable_cavity = make_box(cable_cavity_x_range, cable_cavity_y_range, cable_cavity_z_range)

    # 45° rise from channel-outer face to bag-pocket-wall side,
    # self-supporting in Y-up print so no bridging is needed.
    def slope_wedge(y_low, z_range):
        z_min, z_max = z_range
        base_at_wall = (bag_x, y_low)
        base_at_outer = (bag_x + s * cable_x_depth, y_low)
        apex_at_wall = (bag_x, y_low + cable_x_depth)
        return (
            cq.Workplane(xy_plane_z_up)
            .workplane(offset=z_min)
            .polyline([base_at_wall, base_at_outer, apex_at_wall])
            .close()
            .extrude(z_max - z_min)
        )
    cable_envelope = cable_envelope.union(slope_wedge(cable_envelope_y_range[1], cable_envelope_z_range))
    cable_cavity = cable_cavity.union(slope_wedge(cable_cavity_y_range[1], cable_cavity_z_range))

    # Wraps the channel-outer face around the bag-pocket +Z corner
    # fillet so the channel meets the bag-pocket wall continuously.
    # The inner-fillet cut carves out the corner radius itself.
    missing_wall_profile = [
        (bag_x, cable_envelope_y_range[0]),
        wedge_apex_at_wall,
        corner_arc_terminus,
        (fillet_axis_x, cable_envelope_y_range[0]),
    ]
    missing_wall = (
        cq.Workplane(xy_plane_z_up)
        .workplane(offset=z_outer)
        .polyline(missing_wall_profile).close()
        .extrude(-outer_corner_r)
    )
    inner_fillet_cut = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=cable_envelope_wedge_apex_y)
        .moveTo(*flip_z((fillet_axis_x, fillet_axis_z)))
        .circle(outer_corner_r)
        .extrude(outer_corner_r)
    )
    missing_wall = missing_wall.cut(inner_fillet_cut)

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
        # wall and around the +Z corner fillet, removing the trapezoidal
        # slice of wall material under it.
        z_min, z_max = cable_cavity_z_range
        slope_wall_cut = (
            cq.Workplane(xy_plane_z_up)
            .workplane(offset=z_min)
            .polyline([
                (corner_x_inner, cable_cavity_y_range[1]),
                (wall_x_outer, cable_cavity_y_range[1]),
                (wall_x_outer, cable_cavity_wedge_apex_y),
                (corner_x_inner, cable_cavity_wedge_apex_y + outer_corner_r),
            ]).close()
            .extrude(z_max - z_min)
        )
        foam_shell = foam_shell.cut(slope_wall_cut)

    return foam_shell


# ±X offset of cable hole from bulkhead hole, away from the cold-core
# centerline. The two ⌀6.5 holes are also separated by 12 mm in y
# (cable at cable_y_center, bulkhead at reservoir_bulkhead_port_y), so
# center-to-center distance is ~14 mm — plenty of PETG between them.
cable_hole_offset_from_bulkhead_hole_x = 8.0


def cut_reed_cable_holes(foam_shell):
    """Cable holes — one per reservoir side — through both the +Z
    bag-pocket wall and the +Z outer shell wall, in +Z direction.
    Sits at the same z as its side's bulkhead hole and at cable_y_center
    so the cable runs straight from channel to hole."""
    for s in (+1, -1):
        hole_origin = (
            s * (reservoir_bulkhead_port_x + cable_hole_offset_from_bulkhead_hole_x),
            cable_y_center,
            bag_pocket_width / 2 - 10,
        )
        foam_shell = foam_shell.cut(build_a_hole_punch(origin=hole_origin))
    return foam_shell
