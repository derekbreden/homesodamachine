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
    outer = coordinate_inner_wall + orientation_outward_sign * wall_thickness
    hd = orientation_height_sign
    hf = _height_is_first_axis(orientation_plane, orientation_height_axis)
    sign = orientation_outward_sign
    base = coordinate_lowest_possible_snap_base_in_wall
    zone_width = abs(coordinate_zone_end - coordinate_zone_start)

    available_wall_height = (coordinate_top_of_wall - base) * hd

    bump_reach = channel_width / 2 + deflection_distance / 2
    r = bump_reach - notch_wall_width
    e = bump_height
    f = available_wall_height - r - e
    tip_h = f + 3 * r + 2 * e
    growth_ramp_start = f - outer_growth_default

    bump_face = coordinate_inner_wall + sign * (channel_width - bump_reach)
    notch_face = coordinate_inner_wall + sign * (channel_width - notch_wall_width + overcut)
    ic = coordinate_inner_wall - sign * overcut
    oi = outer - sign * overcut

    # 1. Growth ramp on outer face — trapezoid from growth start to tip
    growth = [
        _pt(oi, base + hd * growth_ramp_start, hf),
        _pt(outer + sign * outer_growth_default, base + hd * f, hf),
        _pt(outer + sign * outer_growth_default, base + hd * tip_h, hf),
        _pt(oi, base + hd * tip_h, hf),
    ]
    solid = solid.union(
        cq.Workplane(orientation_plane).workplane(offset=coordinate_zone_start)
        .polyline(growth).close().extrude(zone_width)
    )

    # 2. Extend wall beyond wall top to tip height
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
        _pt(ic, base + hd * f, hf),
        _pt(bump_face, base + hd * f, hf),
        _pt(notch_face, base + hd * (f + r), hf),
        _pt(notch_face, base + hd * (f + r + e), hf),
        _pt(bump_face, base + hd * (f + 2 * r + e), hf),
        _pt(bump_face, base + hd * (f + 2 * r + 2 * e), hf),
        _pt(notch_face, base + hd * tip_h, hf),
        _pt(ic, base + hd * tip_h, hf),
    ]
    solid = solid.cut(
        cq.Workplane(orientation_plane).workplane(offset=coordinate_zone_start - overcut)
        .polyline(channel).close().extrude(zone_width + 2 * overcut)
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
    outer = coordinate_inner_wall + orientation_outward_sign * wall_thickness
    hd = orientation_height_sign
    hf = _height_is_first_axis(orientation_plane, orientation_height_axis)
    sign = orientation_outward_sign
    base = coordinate_lowest_possible_snap_base_in_wall
    zone_width = abs(coordinate_zone_end - coordinate_zone_start)

    available_wall_height = (coordinate_top_of_wall - base) * hd

    bump_reach = channel_width / 2 + deflection_distance / 2
    r = bump_reach - notch_wall_width
    e = bump_height
    outer_growth = max(0.0, bump_reach - wall_thickness)
    s = available_wall_height - 2 * r - e
    growth_ramp_start = s + r + e + (wall_thickness - notch_wall_width) - outer_growth
    tip_h = s + 3 * r + 2 * e

    bump_face = coordinate_inner_wall + sign * bump_reach
    notch_face = coordinate_inner_wall + sign * notch_wall_width
    ic = coordinate_inner_wall - sign * overcut

    # If bumps extend past wall, add growth ramp on outer face (45° trapezoid)
    if outer_growth > 0:
        oi = outer - sign * overcut
        growth = [
            _pt(oi, base + hd * growth_ramp_start, hf),
            _pt(outer + sign * outer_growth, base + hd * (s + 2 * r + e), hf),
            _pt(outer + sign * outer_growth, base + hd * tip_h, hf),
            _pt(oi, base + hd * tip_h, hf),
        ]
        solid = solid.union(
            cq.Workplane(orientation_plane).workplane(offset=coordinate_zone_start)
            .polyline(growth).close().extrude(zone_width)
        )

    # 1. Extend wall beyond wall top to tip height
    extension = [
        _pt(ic, coordinate_top_of_wall, hf),
        _pt(ic, base + hd * tip_h, hf),
        _pt(notch_face, base + hd * tip_h, hf),
        _pt(bump_face, base + hd * (s + 2 * r + 2 * e), hf),
        _pt(bump_face, coordinate_top_of_wall, hf),
    ]
    solid = solid.union(
        cq.Workplane(orientation_plane).workplane(offset=coordinate_zone_start)
        .polyline(extension).close().extrude(zone_width)
    )

    # 2. Cut notches from outer face — zigzag of bumps and notches
    oc = outer + sign * (outer_growth + overcut)
    notch_cut = [
        _pt(oc, base + hd * s, hf),
        _pt(notch_face, base + hd * (s + r), hf),
        _pt(notch_face, base + hd * (s + r + e), hf),
        _pt(bump_face, base + hd * (s + 2 * r + e), hf),
        _pt(bump_face, base + hd * (s + 2 * r + 2 * e), hf),
        _pt(notch_face, base + hd * tip_h, hf),
        _pt(oc, base + hd * tip_h, hf),
    ]
    solid = solid.cut(
        cq.Workplane(orientation_plane).workplane(offset=coordinate_zone_start - overcut)
        .polyline(notch_cut).close().extrude(zone_width + 2 * overcut)
    )

    return solid
