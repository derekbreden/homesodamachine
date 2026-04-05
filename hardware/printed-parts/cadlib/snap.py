"""Tongue-and-groove snap-fit: modify walls in place.

Functions to add tongue or groove snap features to existing CadQuery walls.
The wall is never removed and replaced — it is shaped via union and cut.

Orientation parameters (height_dir, swap_axes) allow these functions to work
on any workplane orientation.
"""

import cadquery as cq

# ── Snap geometry constants ──

WALL_THICKNESS = 3.0
TONGUE_GROWTH = 2.0
FLEXING_WIDTH = 2.0
ENGAGEMENT = 2.0
CHANNEL_FLOOR = 6.0
OUTER_RAMP_START = 4.0
INITIAL_RIB = 5.0
DEFLECTION = 0.3

CHANNEL_WIDTH = WALL_THICKNESS + TONGUE_GROWTH             # 5.0
INTERLOCK = CHANNEL_WIDTH / 2 + DEFLECTION                 # 2.8
RAMP = INTERLOCK - FLEXING_WIDTH                           # 0.8

TONGUE_INTERLOCK_DEPTH = CHANNEL_WIDTH - INTERLOCK         # 2.2
TONGUE_FLEX_DEPTH = CHANNEL_WIDTH - FLEXING_WIDTH          # 3.0
GROOVE_RIB_DEPTH = INTERLOCK                               # 2.8
GROOVE_GROOVE_DEPTH = FLEXING_WIDTH                        # 2.0

TONGUE_TIP_H = CHANNEL_FLOOR + 3 * RAMP + 2 * ENGAGEMENT  # 12.4
GROOVE_TIP_H = INITIAL_RIB + 3 * RAMP + 2 * ENGAGEMENT    # 11.4

OVERCUT = 0.1


def _pt(face, height, swap):
    """Return (face, height) or (height, face) depending on axis order."""
    return (height, face) if swap else (face, height)


def apply_tongue(solid, inner_face, sign, plane, extrude_start, zone_width,
                 wall_base, height_dir=1, swap_axes=False):
    """Grow the outer face outward, then cut the engagement channel.

    height_dir: +1 if height increases in the workplane's second axis,
                -1 if it decreases (e.g. pump case where Y goes negative).
    swap_axes:  True when the workplane's first axis is the height axis
                (e.g. YZ plane with Y=height, Z=face).
    """
    outer = inner_face + sign * WALL_THICKNESS
    hd = height_dir
    sw = swap_axes
    r = RAMP
    e = ENGAGEMENT
    f = CHANNEL_FLOOR

    # 1. Growth ramp on outer face — trapezoid from ramp start to tongue tip
    #    Inner edge overlaps 0.01mm into existing wall to avoid coincident faces
    oi = outer - sign * 0.01
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

    # 2. Channel cut from inner face — zigzag engagement pattern
    ic = inner_face - sign * OVERCUT
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

    The initial rib stays at full wall thickness. Only the cantilever rib
    and groove channels are cut.
    """
    outer = inner_face + sign * WALL_THICKNESS
    hd = height_dir
    sw = swap_axes
    r = RAMP
    e = ENGAGEMENT
    oc = outer + sign * OVERCUT
    rb = inner_face + sign * GROOVE_RIB_DEPTH
    gr = inner_face + sign * GROOVE_GROOVE_DEPTH
    wall_top = wall_base + hd * wall_height
    ic = inner_face - sign * OVERCUT

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

    # 2. Cut groove channels + cantilever rib from outer face
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
