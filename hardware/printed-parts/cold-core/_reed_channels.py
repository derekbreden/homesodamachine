"""Reed-and-cable channel system for level sensing — built into the
foam shell on the outer face of each bag-pocket far ±X wall."""

import cadquery as cq

from _cold_core_interface import (
    xz_plane_y_up,
    xy_plane_z_up,
    wall_and_floor_thickness,
    foam_shell_outer_height,
    bag_pocket_width,
    bag_pocket_outermost_x,
    bag_pocket_corner_inner_radius,
    reservoir_bulkhead_port_x,
    build_a_hole_punch,
)

W = wall_and_floor_thickness

# X depth of the cable channel cavity, also the rise of the 45°
# printability slope on the cavity ceiling.
cable_channel_x_depth = 5.0

# Reed channel position in Z, matching the reservoir's ROD_POSITION_Z
# so reeds sit opposite the float-on-rod across the bag-pocket wall.
reed_z_center = -45.0
reed_z_half_w = 4.0

# +Z extent of the horizontal cable channel — reaches the +Z
# bag-pocket inner face.
cable_z_max = 70.5

# Outer radius of the bag-pocket +Z corner fillet.
outer_corner_R = W + bag_pocket_corner_inner_radius

# Cable runs along Y in [W, W+8]; +Z cable hole shares this Y so the
# cable goes straight from channel to hole with no bend. Envelope's
# bottom hits the foam-shell floor (y=0) — no unsupported floor mid-air.
cable_y_range          = (W, W + 8.0)
cable_envelope_y_range = (0, W + 8.0 + W)

# Apex Y of the 45° slope wedge on the cable channel ceiling: rises
# +cable_channel_x_depth in Y from the top of the cavity/envelope.
cable_cavity_wedge_apex_y   = cable_y_range[1]          + cable_channel_x_depth
cable_envelope_wedge_apex_y = cable_envelope_y_range[1] + cable_channel_x_depth

reed_cavity_z_range    = (reed_z_center - reed_z_half_w,     reed_z_center + reed_z_half_w)
reed_envelope_z_range  = (reed_z_center - reed_z_half_w - W, reed_z_center + reed_z_half_w + W)
cable_cavity_z_range   = (reed_z_center - reed_z_half_w,     cable_z_max)
cable_envelope_z_range = (reed_z_center - reed_z_half_w - W, cable_z_max + W)


def make_box(x_range, y_range, z_range):
    """Axis-aligned box from world-coordinate ranges in each axis."""
    x_min, x_max = min(x_range), max(x_range)
    y_min, y_max = min(y_range), max(y_range)
    z_min, z_max = min(z_range), max(z_range)
    return (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=y_min)
        .moveTo((x_min + x_max) / 2, -(z_min + z_max) / 2)
        .rect(x_max - x_min, z_max - z_min)
        .extrude(y_max - y_min)
    )


def build_reed_channels(side):
    """Reed-and-cable channel system for one ±X reservoir, returned as
    a single solid (new wall material) to union with the foam shell.

    Vertical reed segment is open at the top so the pre-soldered reed
    column can be dropped in before the foam cap is installed.

    `side` = ±1 mirrors x across the y-z plane."""
    s = side
    reed_x_depth = 6.0

    bag_x = s * bag_pocket_outermost_x  # outer face of bag-pocket far ±X wall
    z_outer = bag_pocket_width / 2

    fillet_axis_x = bag_x - s * outer_corner_R
    fillet_axis_z = z_outer - W - outer_corner_R

    wedge_apex_at_wall  = (bag_x,         cable_envelope_wedge_apex_y)
    corner_arc_terminus = (fillet_axis_x, cable_envelope_wedge_apex_y + outer_corner_R)

    vert_x_range_envelope = (bag_x, bag_x + s * (reed_x_depth + W))
    vert_x_range_cavity   = (bag_x, bag_x + s *  reed_x_depth)
    vert_y_range_envelope = (cable_envelope_y_range[0], foam_shell_outer_height)
    vert_y_range_cavity   = (cable_y_range[0],          foam_shell_outer_height)

    vert_envelope = make_box(vert_x_range_envelope, vert_y_range_envelope, reed_envelope_z_range)
    vert_cavity   = make_box(vert_x_range_cavity,   vert_y_range_cavity,   reed_cavity_z_range)

    horiz_x_range_envelope = (bag_x, bag_x + s * (cable_channel_x_depth + W))
    horiz_x_range_cavity   = (bag_x, bag_x + s *  cable_channel_x_depth)

    horiz_envelope = make_box(horiz_x_range_envelope, cable_envelope_y_range, cable_envelope_z_range)
    horiz_cavity   = make_box(horiz_x_range_cavity,   cable_y_range,          cable_cavity_z_range)

    # 45° rise from channel-outer face to bag-pocket-wall side,
    # self-supporting in Y-up print so no bridging is needed.
    def slope_wedge(y_low, z_range):
        z_min, z_max = z_range
        return (
            cq.Workplane(xy_plane_z_up)
            .workplane(offset=z_min)
            .moveTo(bag_x, y_low)
            .lineTo(bag_x + s * cable_channel_x_depth, y_low)
            .lineTo(bag_x, y_low + cable_channel_x_depth)
            .close()
            .extrude(z_max - z_min)
        )
    horiz_envelope = horiz_envelope.union(slope_wedge(cable_envelope_y_range[1], cable_envelope_z_range))
    horiz_cavity   = horiz_cavity.union(  slope_wedge(cable_y_range[1],          cable_cavity_z_range))

    # Wraps the channel-outer face around the bag-pocket +Z corner
    # fillet so the channel meets the bag-pocket wall continuously.
    # Cylinder cut carves out the inner-corner radius itself.
    missing_wall_profile = [
        (bag_x,         cable_envelope_y_range[0]),
        wedge_apex_at_wall,
        corner_arc_terminus,
        (fillet_axis_x, cable_envelope_y_range[0]),
    ]
    missing_wall = (
        cq.Workplane(xy_plane_z_up)
        .workplane(offset=z_outer)
        .polyline(missing_wall_profile).close()
        .extrude(-outer_corner_R)
    )
    cylinder_cut_for_missing_wall = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=cable_envelope_wedge_apex_y)
        .moveTo(fillet_axis_x, -fillet_axis_z)
        .circle(outer_corner_R)
        .extrude(outer_corner_R)
    )
    missing_wall = missing_wall.cut(cylinder_cut_for_missing_wall)

    return (
        vert_envelope.union(horiz_envelope).union(missing_wall)
        .cut(vert_cavity).cut(horiz_cavity)
    )


def cut_reed_channel_openings(foam_shell):
    """Cut the bag-pocket far ±X wall in the reed-and-cable channel
    footprint, so each channel is open to the bag pocket interior on
    its back face. Shortens the magnet-to-reed magnetic path and
    makes the channels accessible from the bag-pocket side."""
    for s in (+1, -1):
        wall_x_outer   = s * bag_pocket_outermost_x
        wall_x_inner   = wall_x_outer - s * W
        corner_x_inner = wall_x_outer - s * outer_corner_R

        wall_x_range   = (wall_x_inner,   wall_x_outer)
        corner_x_range = (corner_x_inner, wall_x_outer)

        vert_opening = make_box(
            wall_x_range, (cable_y_range[0], foam_shell_outer_height), reed_cavity_z_range,
        )
        horiz_opening = make_box(corner_x_range, cable_y_range, cable_cavity_z_range)
        foam_shell = foam_shell.cut(vert_opening).cut(horiz_opening)

        # Extends the cavity ceiling's 45° slope through the bag-pocket
        # wall and around the +Z corner fillet, removing the trapezoidal
        # slice of wall material under it.
        z_min, z_max = cable_cavity_z_range
        slope_wall_cut = (
            cq.Workplane(xy_plane_z_up)
            .workplane(offset=z_min)
            .polyline([
                (corner_x_inner, cable_y_range[1]),
                (wall_x_outer,   cable_y_range[1]),
                (wall_x_outer,   cable_cavity_wedge_apex_y),
                (corner_x_inner, cable_cavity_wedge_apex_y + outer_corner_R),
            ]).close()
            .extrude(z_max - z_min)
        )
        foam_shell = foam_shell.cut(slope_wall_cut)

    return foam_shell


# ±X offset of cable hole from bulkhead hole, away from the cold-core
# centerline. The two ⌀6.5 holes are also separated by 12 mm in y
# (cable at cable_y_range center, bulkhead at reservoir_bulkhead_port_y),
# so center-to-center distance is ~14 mm — plenty of PETG between them.
cable_hole_offset_from_bulkhead_hole_x = 8.0


def cut_reed_cable_holes(foam_shell):
    """Cable holes — one per reservoir side — through both the +Z
    bag-pocket wall and the +Z outer shell wall, in +Z direction.
    Sits at the same z as its side's bulkhead hole and at the cable
    channel's y so the cable runs straight from channel to hole with
    no bend."""
    cable_y_center = sum(cable_y_range) / 2
    for s in (+1, -1):
        hole_origin = (
            s * (reservoir_bulkhead_port_x + cable_hole_offset_from_bulkhead_hole_x),
            cable_y_center,
            bag_pocket_width / 2 - 10,
        )
        foam_shell = foam_shell.cut(build_a_hole_punch(origin=hole_origin))
    return foam_shell
