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

wall_thickness = 3.0
# Outward growth added to the ramp_out_first outer face so the cut channel
# has room without piercing the original wall.
outer_growth_default = 2.0
notch_wall_width = 2.0
bump_height = 2.0

# Inner-face to (grown) outer-face span the snap features inhabit on the
# ramp_out_first side.
channel_width = wall_thickness + outer_growth_default

overcut = 0.1


def _polyline_in_zone(orientation_plane, zone_start, zone_width, points, overshoot=0.0):
    """Extrude a closed polyline across [zone_start - overshoot, zone_start + zone_width + overshoot]."""
    return (
        cq.Workplane(orientation_plane).workplane(offset=zone_start - overshoot)
        .polyline(points).close()
        .extrude(zone_width + 2 * overshoot)
    )


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
    sign = orientation_outward_sign
    height_dir = orientation_height_sign
    height_first = orientation_plane[0] == orientation_height_axis
    base = coordinate_lowest_possible_snap_base_in_wall
    outer_wall = coordinate_inner_wall + sign * wall_thickness
    zone_width = abs(coordinate_zone_end - coordinate_zone_start)

    available_wall_height = (coordinate_top_of_wall - base) * height_dir

    bump_reach = channel_width / 2 + deflection_distance / 2
    ramp_height = bump_reach - notch_wall_width

    zigzag_start = available_wall_height - ramp_height - bump_height
    ramp_top_1 = zigzag_start + ramp_height
    notch_top = ramp_top_1 + bump_height
    ramp_top_2 = notch_top + ramp_height
    bump_top = ramp_top_2 + bump_height
    tip_height = bump_top + ramp_height
    growth_ramp_start = zigzag_start - outer_growth_default

    bump_face = coordinate_inner_wall + sign * (channel_width - bump_reach)
    notch_face = coordinate_inner_wall + sign * (channel_width - notch_wall_width + overcut)
    grown_outer = outer_wall + sign * outer_growth_default
    inner_overcut = coordinate_inner_wall - sign * overcut
    outer_overcut = outer_wall - sign * overcut

    def pt(face, height):
        h = base + height_dir * height
        return (h, face) if height_first else (face, h)

    # 1. Growth ramp on outer face — trapezoid from growth start to tip
    growth = [
        pt(outer_overcut, growth_ramp_start),
        pt(grown_outer, zigzag_start),
        pt(grown_outer, tip_height),
        pt(outer_overcut, tip_height),
    ]
    solid = solid.union(_polyline_in_zone(orientation_plane, coordinate_zone_start, zone_width, growth))

    # 2. Extend wall beyond wall top to tip height
    extension = [
        pt(inner_overcut, available_wall_height),
        pt(inner_overcut, tip_height),
        pt(outer_overcut, tip_height),
        pt(outer_overcut, available_wall_height),
    ]
    solid = solid.union(_polyline_in_zone(orientation_plane, coordinate_zone_start, zone_width, extension))

    # 3. Channel cut from inner face — zigzag of bumps and notches
    channel = [
        pt(inner_overcut, zigzag_start),
        pt(bump_face, zigzag_start),
        pt(notch_face, ramp_top_1),
        pt(notch_face, notch_top),
        pt(bump_face, ramp_top_2),
        pt(bump_face, bump_top),
        pt(notch_face, tip_height),
        pt(inner_overcut, tip_height),
    ]
    solid = solid.cut(_polyline_in_zone(orientation_plane, coordinate_zone_start, zone_width, channel, overshoot=overcut))

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
    sign = orientation_outward_sign
    height_dir = orientation_height_sign
    height_first = orientation_plane[0] == orientation_height_axis
    base = coordinate_lowest_possible_snap_base_in_wall
    outer_wall = coordinate_inner_wall + sign * wall_thickness
    zone_width = abs(coordinate_zone_end - coordinate_zone_start)

    available_wall_height = (coordinate_top_of_wall - base) * height_dir

    bump_reach = channel_width / 2 + deflection_distance / 2
    ramp_height = bump_reach - notch_wall_width
    outer_growth = max(0.0, bump_reach - wall_thickness)

    zigzag_start = available_wall_height - 2 * ramp_height - bump_height
    ramp_top_1 = zigzag_start + ramp_height
    notch_top = ramp_top_1 + bump_height
    ramp_top_2 = notch_top + ramp_height
    bump_top = ramp_top_2 + bump_height
    tip_height = bump_top + ramp_height
    growth_ramp_start = notch_top + (wall_thickness - notch_wall_width) - outer_growth

    bump_face = coordinate_inner_wall + sign * bump_reach
    notch_face = coordinate_inner_wall + sign * notch_wall_width
    grown_outer = outer_wall + sign * outer_growth
    inner_overcut = coordinate_inner_wall - sign * overcut
    outer_overcut = outer_wall - sign * overcut
    outer_overcut_past_growth = outer_wall + sign * (outer_growth + overcut)

    def pt(face, height):
        h = base + height_dir * height
        return (h, face) if height_first else (face, h)

    # If bumps extend past wall, add growth ramp on outer face (45° trapezoid)
    if outer_growth > 0:
        growth = [
            pt(outer_overcut, growth_ramp_start),
            pt(grown_outer, ramp_top_2),
            pt(grown_outer, tip_height),
            pt(outer_overcut, tip_height),
        ]
        solid = solid.union(_polyline_in_zone(orientation_plane, coordinate_zone_start, zone_width, growth))

    # 1. Extend wall beyond wall top to tip height
    extension = [
        pt(inner_overcut, available_wall_height),
        pt(inner_overcut, tip_height),
        pt(notch_face, tip_height),
        pt(bump_face, bump_top),
        pt(bump_face, available_wall_height),
    ]
    solid = solid.union(_polyline_in_zone(orientation_plane, coordinate_zone_start, zone_width, extension))

    # 2. Cut notches from outer face — zigzag of bumps and notches
    notch_cut = [
        pt(outer_overcut_past_growth, zigzag_start),
        pt(notch_face, ramp_top_1),
        pt(notch_face, notch_top),
        pt(bump_face, ramp_top_2),
        pt(bump_face, bump_top),
        pt(notch_face, tip_height),
        pt(outer_overcut_past_growth, tip_height),
    ]
    solid = solid.cut(_polyline_in_zone(orientation_plane, coordinate_zone_start, zone_width, notch_cut, overshoot=overcut))

    return solid
