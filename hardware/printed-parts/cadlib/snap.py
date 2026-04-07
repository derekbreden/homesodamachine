"""Snap-fit: ramp_out_first / ramp_in_first profiles applied to existing walls.

Each side produces a zigzag profile of bumps (wall extends toward center) and
notches (wall recedes from center), connected by ramps (angled transitions).
"Inner side" faces channel center, "outer side" faces the enclosure exterior.

The two sides interleave:
  ramp_out_first — first ramp goes outward from base (bump at bottom)
  ramp_in_first  — first ramp goes inward from base (notch at bottom)

Deflection tuning:
  RAMP_OUT_DEFLECTION — how far ramp_out_first bumps extend past channel center.
  RAMP_IN_DEFLECTION  — how far ramp_in_first bumps extend past channel center.
  Total interference at engagement = sum of both.
"""

import cadquery as cq

# ── Deflection tuning (change these two values) ──

RAMP_OUT_DEFLECTION = 0.5
RAMP_IN_DEFLECTION = 0.5

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


def _pt(face, height, swap):
    """Return (face, height) or (height, face) depending on axis order."""
    return (height, face) if swap else (face, height)


def apply_ramp_out_first(solid, inner_face, sign, plane, extrude_start,
                         zone_width, wall_base, wall_height,
                         height_dir=1, swap_axes=False):
    """Apply ramp_out_first snap profile to a wall.

    Profile from base up: bump, ramp out, notch, ramp in, bump, ramp out.
    The outer face grows outward to provide material for the channel.
    The channel is cut from the inner side of the wall.

    height_dir: +1 if height increases in the workplane's second axis,
                -1 if it decreases.
    swap_axes:  True when the workplane's first axis is the height axis.
    """
    outer = inner_face + sign * WALL_THICKNESS
    hd = height_dir
    sw = swap_axes

    bump_reach = CHANNEL_WIDTH / 2 + RAMP_OUT_DEFLECTION
    r = bump_reach - NOTCH_WALL_WIDTH                          # ramp height
    e = BUMP_HEIGHT
    f = RAMP_OUT_START
    snap_features_total_height = f + 3 * r + 2 * e
    snap_features_wall_consumption_height = min(snap_features_total_height, wall_height)
    snap_features_beyond_the_wall_height = snap_features_total_height - snap_features_wall_consumption_height
    tip_h = snap_features_total_height
    wall_top = wall_base + hd * wall_height

    # Face-normal positions for bump and notch surfaces (offset from inner_face)
    bump_offset = CHANNEL_WIDTH - bump_reach
    notch_offset = CHANNEL_WIDTH - NOTCH_WALL_WIDTH
    bump_face = inner_face + sign * bump_offset
    notch_face = inner_face + sign * (notch_offset + OVERCUT)

    # Overcut boundaries
    ic = inner_face - sign * OVERCUT       # just past inner face
    oi = outer - sign * OVERCUT            # just inside outer face

    # 1. Growth ramp on outer face — trapezoid from ramp start to tip
    growth = [
        _pt(oi,                          wall_base + hd * OUTER_GROWTH_START, sw),
        _pt(outer + sign * OUTER_GROWTH, wall_base + hd * f, sw),
        _pt(outer + sign * OUTER_GROWTH, wall_base + hd * tip_h, sw),
        _pt(oi,                          wall_base + hd * tip_h, sw),
    ]
    solid = solid.union(
        cq.Workplane(plane).workplane(offset=extrude_start)
        .polyline(growth).close().extrude(zone_width)
    )

    # 2. Extend wall upward to tip height
    extension = [
        _pt(ic, wall_top, sw),
        _pt(ic, wall_base + hd * tip_h, sw),
        _pt(oi, wall_base + hd * tip_h, sw),
        _pt(oi, wall_top, sw),
    ]
    solid = solid.union(
        cq.Workplane(plane).workplane(offset=extrude_start)
        .polyline(extension).close().extrude(zone_width)
    )

    # 3. Channel cut from inner face — zigzag of bumps and notches
    channel = [
        _pt(ic,         wall_base + hd * f, sw),
        _pt(bump_face,  wall_base + hd * f, sw),
        _pt(notch_face, wall_base + hd * (f + r), sw),
        _pt(notch_face, wall_base + hd * (f + r + e), sw),
        _pt(bump_face,  wall_base + hd * (f + 2 * r + e), sw),
        _pt(bump_face,  wall_base + hd * (f + 2 * r + 2 * e), sw),
        _pt(notch_face, wall_base + hd * tip_h, sw),
        _pt(ic,         wall_base + hd * tip_h, sw),
    ]
    solid = solid.cut(
        cq.Workplane(plane).workplane(offset=extrude_start - OVERCUT)
        .polyline(channel).close().extrude(zone_width + 2 * OVERCUT)
    )

    return solid


def apply_ramp_in_first(solid, inner_face, sign, plane, extrude_start,
                        zone_width, wall_base, wall_height,
                        height_dir=1, swap_axes=False):
    """Apply ramp_in_first snap profile to a wall.

    Profile from base up: notch, ramp in, bump, ramp out, notch, ramp in.
    Bumps are on the outer side; notches are cut from the outer face.
    If bumps extend past the wall thickness, growth is added on the outer face.
    """
    outer = inner_face + sign * WALL_THICKNESS
    hd = height_dir
    sw = swap_axes

    bump_reach = CHANNEL_WIDTH / 2 + RAMP_IN_DEFLECTION
    r = bump_reach - NOTCH_WALL_WIDTH                          # ramp height
    e = BUMP_HEIGHT
    s = RAMP_IN_START
    snap_features_total_height = s + 3 * r + 2 * e
    snap_features_wall_consumption_height = min(snap_features_total_height, wall_height)
    snap_features_beyond_the_wall_height = snap_features_total_height - snap_features_wall_consumption_height
    tip_h = snap_features_total_height
    wall_top = wall_base + hd * wall_height

    # Face-normal positions for bump and notch surfaces (offset from inner_face)
    bump_face = inner_face + sign * bump_reach
    notch_face = inner_face + sign * NOTCH_WALL_WIDTH

    # Overcut boundaries
    ic = inner_face - sign * OVERCUT

    # If bumps extend past wall, add growth on outer face
    outer_growth = max(0.0, bump_reach - WALL_THICKNESS)
    if outer_growth > 0:
        oi = outer - sign * OVERCUT
        growth = [
            _pt(oi,                            wall_base + hd * s, sw),
            _pt(outer + sign * outer_growth,   wall_base + hd * s, sw),
            _pt(outer + sign * outer_growth,   wall_base + hd * tip_h, sw),
            _pt(oi,                            wall_base + hd * tip_h, sw),
        ]
        solid = solid.union(
            cq.Workplane(plane).workplane(offset=extrude_start)
            .polyline(growth).close().extrude(zone_width)
        )

    # 1. Extend wall to tip height with bump/notch profile
    extension = [
        _pt(ic,         wall_top, sw),
        _pt(ic,         wall_base + hd * tip_h, sw),
        _pt(notch_face, wall_base + hd * tip_h, sw),
        _pt(bump_face,  wall_base + hd * (s + 2 * r + 2 * e), sw),
        _pt(bump_face,  wall_top, sw),
    ]
    solid = solid.union(
        cq.Workplane(plane).workplane(offset=extrude_start)
        .polyline(extension).close().extrude(zone_width)
    )

    # 2. Cut notches from outer face — zigzag of bumps and notches
    oc = outer + sign * (outer_growth + OVERCUT)
    notch_cut = [
        _pt(oc,         wall_base + hd * s, sw),
        _pt(notch_face, wall_base + hd * (s + r), sw),
        _pt(notch_face, wall_base + hd * (s + r + e), sw),
        _pt(bump_face,  wall_base + hd * (s + 2 * r + e), sw),
        _pt(bump_face,  wall_base + hd * (s + 2 * r + 2 * e), sw),
        _pt(notch_face, wall_base + hd * tip_h, sw),
        _pt(oc,         wall_base + hd * tip_h, sw),
    ]
    solid = solid.cut(
        cq.Workplane(plane).workplane(offset=extrude_start - OVERCUT)
        .polyline(notch_cut).close().extrude(zone_width + 2 * OVERCUT)
    )

    return solid
