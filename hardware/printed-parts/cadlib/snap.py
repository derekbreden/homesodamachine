"""Tongue-and-groove snap-fit: modify walls in place.

Functions to add tongue or groove snap features to existing CadQuery walls.
The wall is never removed and replaced — it is shaped via union and cut.

Deflection tuning:
  TONGUE_DEFLECTION — how far the tongue bumps extend past channel center.
  GROOVE_DEFLECTION — how far the groove ribs extend past channel center.
  Total interference at engagement ramps = sum of both.

  PLA:  0.3 / 0.3  (0.6 total)
  PETG: 0.45 / 0.95  (1.4 total)
"""

import cadquery as cq

# ── Deflection tuning (change these two values) ──

TONGUE_DEFLECTION = 0.5
GROOVE_DEFLECTION = 0.5

# ── Snap geometry constants ──

WALL_THICKNESS = 3.0
TONGUE_GROWTH = 2.0
FLEXING_WIDTH = 2.0
ENGAGEMENT = 2.0
CHANNEL_FLOOR = 6.0
OUTER_RAMP_START = 4.0
INITIAL_RIB = 5.0

CHANNEL_WIDTH = WALL_THICKNESS + TONGUE_GROWTH             # 5.0

# ── Tongue side ──

TONGUE_INTERLOCK = CHANNEL_WIDTH / 2 + TONGUE_DEFLECTION
TONGUE_RAMP = TONGUE_INTERLOCK - FLEXING_WIDTH
TONGUE_INTERLOCK_DEPTH = CHANNEL_WIDTH - TONGUE_INTERLOCK
TONGUE_FLEX_DEPTH = CHANNEL_WIDTH - FLEXING_WIDTH           # 3.0
TONGUE_TIP_H = CHANNEL_FLOOR + 3 * TONGUE_RAMP + 2 * ENGAGEMENT

# ── Groove side ──

GROOVE_INTERLOCK = CHANNEL_WIDTH / 2 + GROOVE_DEFLECTION
GROOVE_RAMP = GROOVE_INTERLOCK - FLEXING_WIDTH
GROOVE_RIB_DEPTH = GROOVE_INTERLOCK
GROOVE_GROOVE_DEPTH = FLEXING_WIDTH                         # 2.0
GROOVE_TIP_H = INITIAL_RIB + 3 * GROOVE_RAMP + 2 * ENGAGEMENT

# If groove ribs extend past wall, groove piece needs outward growth
GROOVE_GROWTH = max(0.0, GROOVE_RIB_DEPTH - WALL_THICKNESS)

OVERCUT = 0.1


def _pt(face, height, swap):
    """Return (face, height) or (height, face) depending on axis order."""
    return (height, face) if swap else (face, height)


def apply_tongue(solid, inner_face, sign, plane, extrude_start, zone_width,
                 wall_base, wall_height, height_dir=1, swap_axes=False):
    """Grow the outer face outward, extend wall upward, then cut the channel.

    The tongue extends above the wall top, so the wall must be extended
    upward to provide material for the channel cut's engagement zigzag.

    height_dir: +1 if height increases in the workplane's second axis,
                -1 if it decreases (e.g. pump case where Y goes negative).
    swap_axes:  True when the workplane's first axis is the height axis
                (e.g. YZ plane with Y=height, Z=face).
    """
    outer = inner_face + sign * WALL_THICKNESS
    hd = height_dir
    sw = swap_axes
    r = TONGUE_RAMP
    e = ENGAGEMENT
    f = CHANNEL_FLOOR
    wall_top = wall_base + hd * wall_height

    # 1. Growth ramp on outer face — trapezoid from ramp start to tongue tip
    #    Inner edge overlaps OVERCUT into existing wall to avoid coincident faces.
    oi = outer - sign * OVERCUT
    growth = [
        _pt(oi,                         wall_base + hd * OUTER_RAMP_START, sw),
        _pt(outer + sign * TONGUE_GROWTH, wall_base + hd * f, sw),
        _pt(outer + sign * TONGUE_GROWTH, wall_base + hd * TONGUE_TIP_H, sw),
        _pt(oi,                         wall_base + hd * TONGUE_TIP_H, sw),
    ]
    solid = solid.union(
        cq.Workplane(plane)
        .workplane(offset=extrude_start)
        .polyline(growth).close()
        .extrude(zone_width)
    )

    # 2. Extend wall upward past wall top to tongue tip — provides material
    #    for the channel cut's engagement bumps above the wall.
    ic = inner_face - sign * OVERCUT
    extension = [
        _pt(ic, wall_top, sw),
        _pt(ic, wall_base + hd * TONGUE_TIP_H, sw),
        _pt(oi, wall_base + hd * TONGUE_TIP_H, sw),
        _pt(oi, wall_top, sw),
    ]
    solid = solid.union(
        cq.Workplane(plane)
        .workplane(offset=extrude_start)
        .polyline(extension).close()
        .extrude(zone_width)
    )

    # 3. Channel cut from inner face — zigzag engagement pattern
    il = inner_face + sign * TONGUE_INTERLOCK_DEPTH
    fl = inner_face + sign * (TONGUE_FLEX_DEPTH + OVERCUT)

    channel = [
        _pt(ic, wall_base + hd * f, sw),
        _pt(il, wall_base + hd * f, sw),
        _pt(fl, wall_base + hd * (f + r), sw),
        _pt(fl, wall_base + hd * (f + r + e), sw),
        _pt(il, wall_base + hd * (f + 2 * r + e), sw),
        _pt(il, wall_base + hd * (f + 2 * r + 2 * e), sw),
        _pt(fl, wall_base + hd * TONGUE_TIP_H, sw),
        _pt(ic, wall_base + hd * TONGUE_TIP_H, sw),
    ]
    solid = solid.cut(
        cq.Workplane(plane)
        .workplane(offset=extrude_start - OVERCUT)
        .polyline(channel).close()
        .extrude(zone_width + 2 * OVERCUT)
    )

    return solid


def apply_groove(solid, inner_face, sign, plane, extrude_start, zone_width,
                 wall_base, wall_height, height_dir=1, swap_axes=False):
    """Cut groove channels from the outer face, add rib extension.

    If GROOVE_DEFLECTION pushes the ribs past the wall thickness, growth
    material is added on the outer face first (like the tongue's growth).
    """
    outer = inner_face + sign * WALL_THICKNESS
    hd = height_dir
    sw = swap_axes
    r = GROOVE_RAMP
    e = ENGAGEMENT
    rb = inner_face + sign * GROOVE_RIB_DEPTH
    gr = inner_face + sign * GROOVE_GROOVE_DEPTH
    wall_top = wall_base + hd * wall_height
    ic = inner_face - sign * OVERCUT

    # 0. If groove ribs extend past wall, add growth on outer face
    if GROOVE_GROWTH > 0:
        oi = outer - sign * OVERCUT
        growth = [
            _pt(oi,                            wall_base + hd * INITIAL_RIB, sw),
            _pt(outer + sign * GROOVE_GROWTH,  wall_base + hd * INITIAL_RIB, sw),
            _pt(outer + sign * GROOVE_GROWTH,  wall_base + hd * GROOVE_TIP_H, sw),
            _pt(oi,                            wall_base + hd * GROOVE_TIP_H, sw),
        ]
        solid = solid.union(
            cq.Workplane(plane)
            .workplane(offset=extrude_start)
            .polyline(growth).close()
            .extrude(zone_width)
        )

    # 1. Rib extension past wall top
    extension = [
        _pt(ic, wall_top, sw),
        _pt(ic, wall_base + hd * GROOVE_TIP_H, sw),
        _pt(gr, wall_base + hd * GROOVE_TIP_H, sw),
        _pt(rb, wall_base + hd * (INITIAL_RIB + 2 * r + 2 * e), sw),
        _pt(rb, wall_top, sw),
    ]
    solid = solid.union(
        cq.Workplane(plane)
        .workplane(offset=extrude_start)
        .polyline(extension).close()
        .extrude(zone_width)
    )

    # 2. Cut groove channels from outer face (past any growth)
    oc = outer + sign * (GROOVE_GROWTH + OVERCUT)
    groove = [
        _pt(oc, wall_base + hd * INITIAL_RIB, sw),
        _pt(gr, wall_base + hd * (INITIAL_RIB + r), sw),
        _pt(gr, wall_base + hd * (INITIAL_RIB + r + e), sw),
        _pt(rb, wall_base + hd * (INITIAL_RIB + 2 * r + e), sw),
        _pt(rb, wall_base + hd * (INITIAL_RIB + 2 * r + 2 * e), sw),
        _pt(gr, wall_base + hd * GROOVE_TIP_H, sw),
        _pt(oc, wall_base + hd * GROOVE_TIP_H, sw),
    ]
    solid = solid.cut(
        cq.Workplane(plane)
        .workplane(offset=extrude_start - OVERCUT)
        .polyline(groove).close()
        .extrude(zone_width + 2 * OVERCUT)
    )

    return solid
