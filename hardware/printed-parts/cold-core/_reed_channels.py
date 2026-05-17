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

# Horizontal cable channel cavity sits on the foam-shell floor
# (bottom y = wall_and_floor_thickness) — no unsupported envelope
# floor mid-air. The +Z cable hole shares cable_y_center, so the
# cable runs straight from channel to hole with no y-bend.
cable_y_half_h = 4.0
cable_y_center = wall_and_floor_thickness + cable_y_half_h

# X depth of the cable channel cavity, also the rise of the 45°
# printability slope on the cavity ceiling (slope runs over this same
# x distance, then continues wall_and_floor_thickness further through
# the bag-pocket wall).
cable_channel_x_depth = 5.0

# Vertical reed channel position in Z, matching the reservoir's
# ROD_POSITION_Z so reeds sit opposite the float-on-rod across
# the bag-pocket wall.
reed_z_center = -45.0
reed_z_half_w = 4.0

# +Z extent of the horizontal cable channel — reaches the +Z
# bag-pocket inner face.
cable_z_max = 70.5

# Outer radius of the bag-pocket +Z corner fillet.
outer_corner_R = wall_and_floor_thickness + bag_pocket_corner_inner_radius


def make_box(x_a, x_b, y_min, y_max, z_a, z_b):
    """Axis-aligned box from world-coordinate min/max ranges in each axis."""
    x_min, x_max = min(x_a, x_b), max(x_a, x_b)
    z_min, z_max = min(z_a, z_b), max(z_a, z_b)
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

    Two segments, both with back face on the bag-pocket far ±X wall,
    extruding outward into the outer-foam zone:

    - Vertical reed channel at z = reed_z_center, open at the top so
      the pre-soldered reed column can be dropped in before the foam
      cap is installed.
    - Horizontal cable channel running in +Z from the vertical channel
      to the +Z bag-pocket inner face. Cavity sits on the foam-shell
      floor; ceiling slopes 45° for printability (no bridging). Cable
      exits at z = cable_z_max through wall openings cut by
      `cut_reed_channel_openings`, then out the +Z cable hole at the
      same y = cable_y_center so no y-bend is required.

    `side` = ±1 mirrors x across the y-z plane."""
    s = side
    W = wall_and_floor_thickness
    reed_x_depth = 6.0

    bag_x = s * bag_pocket_outermost_x  # outer face of bag-pocket far ±X wall
    z_outer = bag_pocket_width / 2

    # Axis along Y through the center of the bag-pocket +Z corner fillet.
    fillet_axis_x = bag_x - s * outer_corner_R
    fillet_axis_z = z_outer - W - outer_corner_R

    env_y_low = cable_y_center - cable_y_half_h - W
    cav_y_low = cable_y_center - cable_y_half_h
    env_wedge_y_low = cable_y_center + cable_y_half_h + W
    cav_wedge_y_low = cable_y_center + cable_y_half_h
    env_wedge_y_high = env_wedge_y_low + cable_channel_x_depth

    vert_envelope = make_box(
        bag_x, bag_x + s * (reed_x_depth + W),
        env_y_low, foam_shell_outer_height,
        reed_z_center - reed_z_half_w - W, reed_z_center + reed_z_half_w + W,
    )
    vert_cavity = make_box(
        bag_x, bag_x + s * reed_x_depth,
        cav_y_low, foam_shell_outer_height,
        reed_z_center - reed_z_half_w, reed_z_center + reed_z_half_w,
    )

    # Horizontal cable channel envelope + cavity. The (+X, +Z) corner
    # is square; missing_wall (below) extends the channel-outer face
    # material around the bag-pocket inner corner fillet.
    horiz_envelope = make_box(
        bag_x, bag_x + s * (cable_channel_x_depth + W),
        env_y_low, env_wedge_y_low,
        reed_z_center - reed_z_half_w - W, cable_z_max + W,
    )
    horiz_cavity = make_box(
        bag_x, bag_x + s * cable_channel_x_depth,
        cav_y_low, cav_wedge_y_low,
        reed_z_center - reed_z_half_w, cable_z_max,
    )

    # Sloped ceiling on the horizontal cable channel — 45° rise from
    # channel-outer face to bag-pocket-wall side, self-supporting in
    # Y-up print so no bridging / support material is needed.
    def slope_wedge(y_low, z_min, z_max):
        return (
            cq.Workplane(xy_plane_z_up)
            .workplane(offset=z_min)
            .moveTo(bag_x, y_low)
            .lineTo(bag_x + s * cable_channel_x_depth, y_low)
            .lineTo(bag_x, y_low + cable_channel_x_depth)
            .close()
            .extrude(z_max - z_min)
        )
    horiz_envelope = horiz_envelope.union(slope_wedge(
        env_wedge_y_low,
        reed_z_center - reed_z_half_w - W, cable_z_max + W,
    ))
    horiz_cavity = horiz_cavity.union(slope_wedge(
        cav_wedge_y_low,
        reed_z_center - reed_z_half_w, cable_z_max,
    ))

    # Wraps the channel-outer face around the bag-pocket +Z corner
    # fillet so the channel meets the bag-pocket wall continuously
    # (no foam-pour gap behind the corner). The cylinder cut carves
    # out the inner-corner radius itself.
    missing_wall = (
        cq.Workplane(xy_plane_z_up)
        .workplane(offset=z_outer)
        .moveTo(bag_x, env_y_low)
        .lineTo(bag_x, env_wedge_y_high)
        .lineTo(fillet_axis_x, env_wedge_y_high + outer_corner_R)
        .lineTo(fillet_axis_x, env_y_low)
        .close()
        .extrude(-outer_corner_R)
    )
    cylinder_cut_for_missing_wall = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=env_wedge_y_high)
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
    its back face. Two payoffs:

    - Shortens the magnet-to-reed magnetic path (removes the 2 mm
      bag-pocket wall PETG between the magnet inside the reservoir
      and the reed sensors in the foam-zone channel).
    - Makes the channels accessible / inspectable from the bag-pocket
      side.

    Foam-pour safety is unaffected: the cut is on the bag-pocket-inner
    side; foam lives only in the foam zone outboard of the channel."""
    W = wall_and_floor_thickness

    for s in (+1, -1):
        wall_x_outer   = s * bag_pocket_outermost_x
        wall_x_inner   = wall_x_outer - s * W
        corner_x_inner = wall_x_outer - s * outer_corner_R

        # Vertical opening: through the wall in the reed channel's
        # footprint (full height).
        vert_opening = make_box(
            wall_x_inner, wall_x_outer,
            cable_y_center - cable_y_half_h, foam_shell_outer_height,
            reed_z_center - reed_z_half_w, reed_z_center + reed_z_half_w,
        )
        foam_shell = foam_shell.cut(vert_opening)

        # Horizontal opening: through the wall (and the corner-arc band
        # material) in the cable channel's y footprint, reaching to
        # z = ±cable_z_max.
        horiz_opening = make_box(
            corner_x_inner, wall_x_outer,
            cable_y_center - cable_y_half_h, cable_y_center + cable_y_half_h,
            reed_z_center - reed_z_half_w, cable_z_max,
        )
        foam_shell = foam_shell.cut(horiz_opening)

        # Slope wall cut: extends the cavity ceiling's 45° slope
        # through the bag-pocket wall and around the +Z corner fillet,
        # removing the trapezoidal slice of wall material under it.
        slope_y_low       = cable_y_center + cable_y_half_h
        slope_y_at_wall   = slope_y_low + cable_channel_x_depth
        slope_y_at_corner = slope_y_at_wall + outer_corner_R
        slope_z_min       = reed_z_center - reed_z_half_w
        slope_wall_cut = (
            cq.Workplane(xy_plane_z_up)
            .workplane(offset=slope_z_min)
            .moveTo(corner_x_inner, slope_y_low)
            .lineTo(wall_x_outer, slope_y_low)
            .lineTo(wall_x_outer, slope_y_at_wall)
            .lineTo(corner_x_inner, slope_y_at_corner)
            .close()
            .extrude(cable_z_max - slope_z_min)
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
    Sits at the same z as its side's bulkhead hole, X-offset by
    cable_hole_offset_from_bulkhead_hole_x away from the bulkhead
    hole, and at y = cable_y_center so the cable runs straight from
    channel to hole with no bend.

    Cable's path: reed column → vertical channel → horizontal channel
    → bag-pocket-wall opening (cut by cut_reed_channel_openings) →
    bag-pocket interior, traversing in −X through the body's dry-side
    empty space → cable hole, in +Z → out the front face."""
    for s in (+1, -1):
        hole_origin = (
            s * (reservoir_bulkhead_port_x + cable_hole_offset_from_bulkhead_hole_x),
            cable_y_center,
            bag_pocket_width / 2 - 10,
        )
        foam_shell = foam_shell.cut(build_a_hole_punch(origin=hole_origin))
    return foam_shell
