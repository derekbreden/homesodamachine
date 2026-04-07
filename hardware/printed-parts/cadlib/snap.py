"""Snap-fit: ramp_out_first / ramp_in_first profiles applied to existing walls.

Each side produces a zigzag profile of bumps (wall extends toward center) and
notches (wall recedes from center), connected by ramps (angled transitions).
"Inner side" faces channel center, "outer side" faces the enclosure exterior.

The two sides interleave:
  ramp_out_first — first ramp goes outward from base (bump at bottom)
  ramp_in_first  — first ramp goes inward from base (notch at bottom)

The caller provides two coordinates defining the available wall:
  coordinate_lowest_possible_snap_base_in_wall — bottom of available space
  coordinate_top_of_wall — where "within the wall" ends
The snap geometry determines how much wall it consumes and how far it
extends beyond the wall, based on deflection.

Deflection tuning:
  deflection_distance — total interference at engagement, split evenly
  between both sides.  Each side's bumps extend past channel center by
  deflection_distance / 2.
"""

import cadquery as cq

# ── Snap geometry constants ──

WALL_THICKNESS = 3.0
OUTER_GROWTH = 2.0          # outward growth on ramp_out_first outer face
NOTCH_WALL_WIDTH = 2.0      # wall width at notch positions
BUMP_HEIGHT = 2.0           # vertical height of each bump / notch section
RAMP_OUT_START = 6.0        # height where ramp_out_first features begin
RAMP_IN_START = 5.0         # height where ramp_in_first features begin
OUTER_GROWTH_START = 4.0    # height where outer growth ramp begins

CHANNEL_WIDTH = WALL_THICKNESS + OUTER_GROWTH  # 5.0

OVERCUT = 0.1


def _height_is_first_axis(orientation_plane, orientation_height_axis):
    """True when the height axis is the first coordinate of the workplane."""
    return orientation_plane[0] == orientation_height_axis


def _pt(face, height, height_first):
    """Return (face, height) or (height, face) depending on axis order."""
    return (height, face) if height_first else (face, height)


def apply_ramp_out_first(
        solid,
        coordinate_inner_wall,
        coordinate_zone_start,
        coordinate_zone_end,
        coordinate_lowest_possible_snap_base_in_wall,
        coordinate_top_of_wall,
        orientation_outward_sign,
        orientation_plane,
        orientation_height_sign=1,
        orientation_height_axis="Z",
        deflection_distance=1.0,
):
    """Apply ramp_out_first snap profile to a wall.

    Profile from base up: bump, ramp out, notch, ramp in, bump, ramp out.
    The outer face grows outward to provide material for the channel.
    The channel is cut from the inner side of the wall.
    """
    outer = coordinate_inner_wall + orientation_outward_sign * WALL_THICKNESS
    hd = orientation_height_sign
    hf = _height_is_first_axis(orientation_plane, orientation_height_axis)
    sign = orientation_outward_sign
    base = coordinate_lowest_possible_snap_base_in_wall
    zone_width = abs(coordinate_zone_end - coordinate_zone_start)

    available_wall_height = (coordinate_top_of_wall - base) * hd

    bump_reach = CHANNEL_WIDTH / 2 + deflection_distance / 2
    r = bump_reach - NOTCH_WALL_WIDTH                          # ramp height
    e = BUMP_HEIGHT
    f = RAMP_OUT_START
    tip_h = f + 3 * r + 2 * e

    snap_base_in_wall = base + hd * OUTER_GROWTH_START
    snap_features_total_height = tip_h - OUTER_GROWTH_START
    snap_features_beyond_the_wall_height = max(0.0, tip_h - available_wall_height)
    snap_features_wall_consumption_height = snap_features_total_height - snap_features_beyond_the_wall_height

    # Face-normal positions for bump and notch surfaces (offset from coordinate_inner_wall)
    bump_offset = CHANNEL_WIDTH - bump_reach
    notch_offset = CHANNEL_WIDTH - NOTCH_WALL_WIDTH
    bump_face = coordinate_inner_wall + sign * bump_offset
    notch_face = coordinate_inner_wall + sign * (notch_offset + OVERCUT)

    # Overcut boundaries
    ic = coordinate_inner_wall - sign * OVERCUT       # just past inner face
    oi = outer - sign * OVERCUT                       # just inside outer face

    # 1. Growth ramp on outer face — trapezoid from ramp start to tip
    growth = [
        _pt(oi,                          base + hd * OUTER_GROWTH_START, hf),
        _pt(outer + sign * OUTER_GROWTH, base + hd * f, hf),
        _pt(outer + sign * OUTER_GROWTH, base + hd * tip_h, hf),
        _pt(oi,                          base + hd * tip_h, hf),
    ]
    solid = solid.union(
        cq.Workplane(orientation_plane).workplane(offset=coordinate_zone_start)
        .polyline(growth).close().extrude(zone_width)
    )

    # 2. Extend wall upward to tip height
    extension = [
        _pt(ic, coordinate_top_of_wall, hf),
        _pt(ic, base + hd * tip_h, hf),
        _pt(oi, base + hd * tip_h, hf),
        _pt(oi, coordinate_top_of_wall, hf),
    ]
    solid = solid.union(
        cq.Workplane(orientation_plane).workplane(offset=coordinate_zone_start)
        .polyline(extension).close().extrude(zone_width)
    )

    # 3. Channel cut from inner face — zigzag of bumps and notches
    channel = [
        _pt(ic,         base + hd * f, hf),
        _pt(bump_face,  base + hd * f, hf),
        _pt(notch_face, base + hd * (f + r), hf),
        _pt(notch_face, base + hd * (f + r + e), hf),
        _pt(bump_face,  base + hd * (f + 2 * r + e), hf),
        _pt(bump_face,  base + hd * (f + 2 * r + 2 * e), hf),
        _pt(notch_face, base + hd * tip_h, hf),
        _pt(ic,         base + hd * tip_h, hf),
    ]
    solid = solid.cut(
        cq.Workplane(orientation_plane).workplane(offset=coordinate_zone_start - OVERCUT)
        .polyline(channel).close().extrude(zone_width + 2 * OVERCUT)
    )

    return solid


def apply_ramp_in_first(
        solid,
        coordinate_inner_wall,
        coordinate_zone_start,
        coordinate_zone_end,
        coordinate_lowest_possible_snap_base_in_wall,
        coordinate_top_of_wall,
        orientation_outward_sign,
        orientation_plane,
        orientation_height_sign=1,
        orientation_height_axis="Z",
        deflection_distance=1.0,
):
    """Apply ramp_in_first snap profile to a wall.

    Profile from base up: notch, ramp in, bump, ramp out, notch, ramp in.
    Bumps are on the outer side; notches are cut from the outer face.
    If bumps extend past the wall thickness, growth is added on the outer face.
    """
    outer = coordinate_inner_wall + orientation_outward_sign * WALL_THICKNESS
    hd = orientation_height_sign
    hf = _height_is_first_axis(orientation_plane, orientation_height_axis)
    sign = orientation_outward_sign
    base = coordinate_lowest_possible_snap_base_in_wall
    zone_width = abs(coordinate_zone_end - coordinate_zone_start)

    available_wall_height = (coordinate_top_of_wall - base) * hd

    bump_reach = CHANNEL_WIDTH / 2 + deflection_distance / 2
    r = bump_reach - NOTCH_WALL_WIDTH                          # ramp height
    e = BUMP_HEIGHT
    s = RAMP_IN_START
    tip_h = s + 3 * r + 2 * e

    snap_base_in_wall = base + hd * RAMP_IN_START
    snap_features_total_height = tip_h - RAMP_IN_START
    snap_features_beyond_the_wall_height = max(0.0, tip_h - available_wall_height)
    snap_features_wall_consumption_height = snap_features_total_height - snap_features_beyond_the_wall_height

    # Face-normal positions for bump and notch surfaces (offset from coordinate_inner_wall)
    bump_face = coordinate_inner_wall + sign * bump_reach
    notch_face = coordinate_inner_wall + sign * NOTCH_WALL_WIDTH

    # Overcut boundaries
    ic = coordinate_inner_wall - sign * OVERCUT

    # If bumps extend past wall, add growth on outer face
    outer_growth = max(0.0, bump_reach - WALL_THICKNESS)
    if outer_growth > 0:
        oi = outer - sign * OVERCUT
        growth = [
            _pt(oi,                            base + hd * s, hf),
            _pt(outer + sign * outer_growth,   base + hd * s, hf),
            _pt(outer + sign * outer_growth,   base + hd * tip_h, hf),
            _pt(oi,                            base + hd * tip_h, hf),
        ]
        solid = solid.union(
            cq.Workplane(orientation_plane).workplane(offset=coordinate_zone_start)
            .polyline(growth).close().extrude(zone_width)
        )

    # 1. Extend wall to tip height with bump/notch profile
    extension = [
        _pt(ic,         coordinate_top_of_wall, hf),
        _pt(ic,         base + hd * tip_h, hf),
        _pt(notch_face, base + hd * tip_h, hf),
        _pt(bump_face,  base + hd * (s + 2 * r + 2 * e), hf),
        _pt(bump_face,  coordinate_top_of_wall, hf),
    ]
    solid = solid.union(
        cq.Workplane(orientation_plane).workplane(offset=coordinate_zone_start)
        .polyline(extension).close().extrude(zone_width)
    )

    # 2. Cut notches from outer face — zigzag of bumps and notches
    oc = outer + sign * (outer_growth + OVERCUT)
    notch_cut = [
        _pt(oc,         base + hd * s, hf),
        _pt(notch_face, base + hd * (s + r), hf),
        _pt(notch_face, base + hd * (s + r + e), hf),
        _pt(bump_face,  base + hd * (s + 2 * r + e), hf),
        _pt(bump_face,  base + hd * (s + 2 * r + 2 * e), hf),
        _pt(notch_face, base + hd * tip_h, hf),
        _pt(oc,         base + hd * tip_h, hf),
    ]
    solid = solid.cut(
        cq.Workplane(orientation_plane).workplane(offset=coordinate_zone_start - OVERCUT)
        .polyline(notch_cut).close().extrude(zone_width + 2 * OVERCUT)
    )

    return solid
