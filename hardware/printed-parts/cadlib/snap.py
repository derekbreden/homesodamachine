"""Snap-fit: ramp_out_first / ramp_in_first profiles applied to existing walls.

Each side produces a zigzag profile of bumps (wall extends toward center) and
notches (wall recedes from center), connected by ramps (angled transitions).
"Inner side" faces channel center, "outer side" faces the enclosure exterior.

The two sides interleave:
  ramp_out_first — first ramp goes outward from base (bump at bottom)
  ramp_in_first  — first ramp goes inward from base (notch at bottom)

The caller describes the wall as two scalars on the snap's "up" axis:
  wall_top_at  — coord of the wall top (where "within the wall" ends)
  wall_height  — span the snap consumes, measured backward from wall_top
The snap geometry determines how much it extends beyond the wall top, based
on deflection.

Deflection tuning:
  deflection_distance — total interference at engagement, split evenly
  between both sides.  Each side's bumps extend past channel center by
  deflection_distance / 2.
"""

import cadquery as cq

wall_thickness = 3.0
# Outward growth added to the ramp_out_first outer face so the cut channel
# has room without piercing the original wall.
ramp_out_outer_growth = 2.0
notch_wall_width = 2.0
bump_height = 2.0

# Inner-face to (grown) outer-face span the snap features inhabit on the
# ramp_out_first side.
channel_width = wall_thickness + ramp_out_outer_growth

overcut = 0.1


class Frame:
    """Coordinate frame for a snap-fit feature.

    extrusion_plane — cadquery plane name ('XY', 'YZ', 'XZ'). The snap
        cross-section lives in this plane; extrusion runs along the
        plane's normal.
    outward_sign — +1 or -1, sign of the outward direction along the
        wall-thickness axis (the axis in extrusion_plane that ISN'T
        up_axis).
    up_axis — 'X', 'Y', or 'Z'. The snap's growth direction; must be
        one of the two axes named in extrusion_plane.
    up_sign — +1 or -1, which way along up_axis counts as "up" in world
        coords. The snap grows from the wall toward +up.
    """

    def __init__(self, *, extrusion_plane, outward_sign, up_axis, up_sign=1):
        self.extrusion_plane = extrusion_plane
        self.outward_sign = outward_sign
        self.up_axis = up_axis
        self.up_sign = up_sign
        # In the cadquery plane name (e.g. "YZ"), the first letter is
        # the local U-axis. If that matches up_axis, points are (up, outward).
        self.up_first = extrusion_plane[0] == up_axis


def _polyline_in_zone(frame, zone_range, points, overshoot=0.0):
    """Extrude a closed polyline across the zone, optionally overshooting."""
    z_lo, z_hi = min(zone_range), max(zone_range)
    return (
        cq.Workplane(frame.extrusion_plane)
        .workplane(offset=z_lo - overshoot)
        .polyline(points).close()
        .extrude((z_hi - z_lo) + 2 * overshoot)
    )


def apply_ramp_out_first(
        solid,
        *,
        frame,
        inner_wall_at,
        wall_top_at,
        wall_height,
        zone_range,
        deflection_distance=1.0,
):
    """Apply ramp_out_first snap profile to a wall.

    Profile from base up: bump, ramp out, notch, ramp in, bump, ramp out.
    The outer face grows outward to provide material for the channel.
    The channel is cut from the inner side of the wall.
    """
    sign = frame.outward_sign
    up_sign = frame.up_sign
    base = wall_top_at - up_sign * wall_height
    outer_wall = inner_wall_at + sign * wall_thickness

    bump_reach = channel_width / 2 + deflection_distance / 2
    ramp_height = bump_reach - notch_wall_width

    zigzag_start = wall_height - ramp_height - bump_height
    ramp_top_1 = zigzag_start + ramp_height
    notch_top = ramp_top_1 + bump_height
    ramp_top_2 = notch_top + ramp_height
    bump_top = ramp_top_2 + bump_height
    tip_height = bump_top + ramp_height
    growth_ramp_start = zigzag_start - ramp_out_outer_growth

    bump_face = inner_wall_at + sign * (channel_width - bump_reach)
    notch_face = inner_wall_at + sign * (channel_width - notch_wall_width + overcut)
    grown_outer = outer_wall + sign * ramp_out_outer_growth
    inner_overcut = inner_wall_at - sign * overcut
    outer_overcut = outer_wall - sign * overcut

    def pt(face, height):
        h = base + up_sign * height
        return (h, face) if frame.up_first else (face, h)

    # 1. Growth ramp on outer face — 45° trapezoid from growth start to tip
    growth = [
        pt(outer_overcut, growth_ramp_start),
        pt(grown_outer, zigzag_start),
        pt(grown_outer, tip_height),
        pt(outer_overcut, tip_height),
    ]
    solid = solid.union(_polyline_in_zone(frame, zone_range, growth))

    # 2. Extend wall beyond wall top to tip height
    extension = [
        pt(inner_overcut, wall_height),
        pt(inner_overcut, tip_height),
        pt(outer_overcut, tip_height),
        pt(outer_overcut, wall_height),
    ]
    solid = solid.union(_polyline_in_zone(frame, zone_range, extension))

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
    solid = solid.cut(_polyline_in_zone(frame, zone_range, channel, overshoot=overcut))

    return solid


def apply_ramp_in_first(
        solid,
        *,
        frame,
        inner_wall_at,
        wall_top_at,
        wall_height,
        zone_range,
        deflection_distance=1.0,
):
    """Apply ramp_in_first snap profile to a wall.

    Profile from base up: notch, ramp in, bump, ramp out, notch, ramp in.
    Bumps are on the outer side; notches are cut from the outer face.
    If bumps extend past the wall thickness, growth is added on the outer face.
    """
    sign = frame.outward_sign
    up_sign = frame.up_sign
    base = wall_top_at - up_sign * wall_height
    outer_wall = inner_wall_at + sign * wall_thickness

    bump_reach = channel_width / 2 + deflection_distance / 2
    ramp_height = bump_reach - notch_wall_width
    outer_growth = max(0.0, bump_reach - wall_thickness)

    zigzag_start = wall_height - 2 * ramp_height - bump_height
    ramp_top_1 = zigzag_start + ramp_height
    notch_top = ramp_top_1 + bump_height
    ramp_top_2 = notch_top + ramp_height
    bump_top = ramp_top_2 + bump_height
    tip_height = bump_top + ramp_height
    growth_ramp_start = notch_top + (wall_thickness - notch_wall_width) - outer_growth

    bump_face = inner_wall_at + sign * bump_reach
    notch_face = inner_wall_at + sign * notch_wall_width
    grown_outer = outer_wall + sign * outer_growth
    inner_overcut = inner_wall_at - sign * overcut
    outer_overcut = outer_wall - sign * overcut
    outer_overcut_past_growth = outer_wall + sign * (outer_growth + overcut)

    def pt(face, height):
        h = base + up_sign * height
        return (h, face) if frame.up_first else (face, h)

    # If bumps extend past wall, add growth ramp on outer face (2:1 trapezoid)
    if outer_growth > 0:
        growth = [
            pt(outer_overcut, growth_ramp_start),
            pt(grown_outer, ramp_top_2),
            pt(grown_outer, tip_height),
            pt(outer_overcut, tip_height),
        ]
        solid = solid.union(_polyline_in_zone(frame, zone_range, growth))

    # 1. Extend wall beyond wall top to tip height
    extension = [
        pt(inner_overcut, wall_height),
        pt(inner_overcut, tip_height),
        pt(notch_face, tip_height),
        pt(bump_face, bump_top),
        pt(bump_face, wall_height),
    ]
    solid = solid.union(_polyline_in_zone(frame, zone_range, extension))

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
    solid = solid.cut(_polyline_in_zone(frame, zone_range, notch_cut, overshoot=overcut))

    return solid
