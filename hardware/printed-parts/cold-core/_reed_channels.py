"""Reed-and-cable channel system for level sensing — built into the
foam shell on the outer face of each bag-pocket far ±X wall."""

import math
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
# STRUT_POSITION_Z so reeds sit opposite the float-on-strut across
# the bag-pocket wall.
reed_z_center = -45.0
reed_z_half_w = 4.0

# +Z extent of the horizontal cable channel — reaches the +Z
# bag-pocket inner face.
cable_z_max = 70.5

# X depth of the vertical reed channel cavity.
reed_x_depth = 6.0


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
      floor; ceiling slopes 45° over the straight section for
      printability (no bridging). Cable exits at z = cable_z_max
      through wall openings cut by `cut_reed_channel_openings`, then
      out the +Z cable hole at the same y = cable_y_center so no
      y-bend is required.

    `side` = ±1 mirrors x across the y-z plane."""
    s = side
    W = wall_and_floor_thickness

    bag_x = s * bag_pocket_outermost_x  # outer face of bag-pocket far ±X wall

    # Vertical reed channel envelope + cavity
    vert_envelope = make_box(
        bag_x, bag_x + s * (reed_x_depth + W),
        cable_y_center - cable_y_half_h - W, foam_shell_outer_height,
        reed_z_center - reed_z_half_w - W, reed_z_center + reed_z_half_w + W,
    )
    vert_cavity = make_box(
        bag_x, bag_x + s * reed_x_depth,
        cable_y_center - cable_y_half_h, foam_shell_outer_height,
        reed_z_center - reed_z_half_w, reed_z_center + reed_z_half_w,
    )

    # Horizontal cable channel envelope + cavity. The (+X, +Z) corner
    # of each is rounded with R = bag_pocket_corner_inner_radius so
    # the cable bends from going +Z (along the channel) to going -X
    # (out into the bag-pocket interior) along an arc parallel to the
    # bag-pocket inner corner arc the channel joins.
    #
    # Built as polylines rather than `make_box(...).fillet()` because
    # R > cable_channel_x_depth: the cavity's +Z face is too narrow
    # for a tangent fillet, so the arc is tangent only to the channel-
    # outer face and meets the channel-inner face partway up the -X
    # side. (The envelope's +Z face IS wide enough; its arc is tangent
    # to both faces.)
    R = bag_pocket_corner_inner_radius

    horiz_envelope = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=cable_y_center - cable_y_half_h - W)
        .moveTo(bag_x, -(reed_z_center - reed_z_half_w - W))
        .lineTo(bag_x + s * (cable_channel_x_depth + W), -(reed_z_center - reed_z_half_w - W))
        .lineTo(bag_x + s * (cable_channel_x_depth + W), -(cable_z_max + W - R))
        .radiusArc(
            (bag_x + s * (cable_channel_x_depth + W - R), -(cable_z_max + W)),
            s * R,
        )
        .lineTo(bag_x, -(cable_z_max + W))
        .close()
        .extrude(2 * (cable_y_half_h + W))
    )

    cavity_arc_z_at_inner_x = (cable_z_max - R) + math.sqrt(R**2 - (R - cable_channel_x_depth)**2)
    horiz_cavity = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=cable_y_center - cable_y_half_h)
        .moveTo(bag_x, -(reed_z_center - reed_z_half_w))
        .lineTo(bag_x + s * cable_channel_x_depth, -(reed_z_center - reed_z_half_w))
        .lineTo(bag_x + s * cable_channel_x_depth, -(cable_z_max - R))
        .radiusArc(
            (bag_x, -cavity_arc_z_at_inner_x),
            s * R,
        )
        .close()
        .extrude(2 * cable_y_half_h)
    )

    # Sloped ceiling on the horizontal cable channel (straight section
    # only, z ≤ cable_z_max − R). Triangular wedge added to both
    # envelope and cavity, rising 1:1 (45°) over cable_channel_x_depth
    # from the channel-outer face to the bag-pocket-wall side. Self-
    # supporting in Y-up print; no internal support material needed.
    # The +Z corner area keeps its current flat ceiling (TODO: address
    # the resulting step at z = cable_z_max − R in a later iteration).
    slope_z_min_env = reed_z_center - reed_z_half_w - W
    slope_z_min_cav = reed_z_center - reed_z_half_w
    slope_z_max     = cable_z_max - R
    env_wedge_y_low  = cable_y_center + cable_y_half_h + W
    env_wedge_y_high = env_wedge_y_low + cable_channel_x_depth
    cav_wedge_y_low  = cable_y_center + cable_y_half_h
    cav_wedge_y_high = cav_wedge_y_low + cable_channel_x_depth
    env_wedge = (
        cq.Workplane(xy_plane_z_up)
        .workplane(offset=slope_z_min_env)
        .moveTo(bag_x, env_wedge_y_low)
        .lineTo(bag_x + s * cable_channel_x_depth, env_wedge_y_low)
        .lineTo(bag_x, env_wedge_y_high)
        .close()
        .extrude(slope_z_max - slope_z_min_env)
    )
    cav_wedge = (
        cq.Workplane(xy_plane_z_up)
        .workplane(offset=slope_z_min_cav)
        .moveTo(bag_x, cav_wedge_y_low)
        .lineTo(bag_x + s * cable_channel_x_depth, cav_wedge_y_low)
        .lineTo(bag_x, cav_wedge_y_high)
        .close()
        .extrude(slope_z_max - slope_z_min_cav)
    )
    horiz_envelope = horiz_envelope.union(env_wedge)
    horiz_cavity = horiz_cavity.union(cav_wedge)

    # Corner wedge — extends the channel envelope around the bag-pocket
    # wall's +Z outer corner arc so the channel-outer face meets the
    # wall continuously (no foam-pour gap behind the corner). Cut back
    # in the cable's y range by cut_reed_channel_openings.
    R_outer_corner = bag_pocket_corner_inner_radius + W
    corner_arc_endpoint_x = s * (
        bag_pocket_outermost_x - W - bag_pocket_corner_inner_radius
    )
    z_outer = bag_pocket_width / 2
    z_corner_start = z_outer - W - bag_pocket_corner_inner_radius
    y_min_env = cable_y_center - cable_y_half_h - W
    y_max_env = cable_y_center + cable_y_half_h + W
    corner_wedge = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=y_min_env)
        .moveTo(bag_x, -z_corner_start)
        .radiusArc((corner_arc_endpoint_x, -z_outer), s * R_outer_corner)
        .lineTo(bag_x, -z_outer)
        .close()
        .extrude(y_max_env - y_min_env)
    )

    return (
        vert_envelope.union(horiz_envelope).union(corner_wedge)
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
        # Bag-pocket far ±X wall: 2 mm-thick band at x ∈ [outer−W, outer]
        # in the straight section, curving inward along the +Z corner
        # arc up to its terminus at x = ±(outer − W − R).
        wall_x_outer   = s * bag_pocket_outermost_x
        wall_x_inner   = s * (bag_pocket_outermost_x - W)
        corner_x_inner = s * (bag_pocket_outermost_x - W - bag_pocket_corner_inner_radius)

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
        # through the bag-pocket wall — removes the trapezoidal slice
        # of wall material under the slope's continuation. Straight
        # section only (z ≤ cable_z_max − R).
        slope_y_low      = cable_y_center + cable_y_half_h
        slope_y_at_outer = slope_y_low + cable_channel_x_depth
        slope_y_at_inner = slope_y_at_outer + W
        slope_z_min      = reed_z_center - reed_z_half_w
        slope_z_max      = cable_z_max - bag_pocket_corner_inner_radius
        slope_wall_cut = (
            cq.Workplane(xy_plane_z_up)
            .workplane(offset=slope_z_min)
            .moveTo(wall_x_inner, slope_y_low)
            .lineTo(wall_x_outer, slope_y_low)
            .lineTo(wall_x_outer, slope_y_at_outer)
            .lineTo(wall_x_inner, slope_y_at_inner)
            .close()
            .extrude(slope_z_max - slope_z_min)
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
