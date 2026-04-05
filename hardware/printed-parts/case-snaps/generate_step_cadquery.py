"""Snap-fit test case: tongue-and-groove by modifying walls in place.

The snap features are geometric modifications to existing walls:
  Tongue: grow the outer face outward (ramp), then cut the engagement channel
  Groove: cut the engagement pattern from the outer face, add rib extension

The wall is never removed and replaced. It is shaped.
"""

from pathlib import Path

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

# How far the tongue/groove interlock faces sit from the inner face
TONGUE_INTERLOCK_DEPTH = CHANNEL_WIDTH - INTERLOCK         # 2.2
TONGUE_FLEX_DEPTH = CHANNEL_WIDTH - FLEXING_WIDTH          # 3.0
GROOVE_RIB_DEPTH = INTERLOCK                               # 2.8
GROOVE_GROOVE_DEPTH = FLEXING_WIDTH                        # 2.0

TONGUE_TIP_H = CHANNEL_FLOOR + 3 * RAMP + 2 * ENGAGEMENT  # 12.4
GROOVE_TIP_H = INITIAL_RIB + 3 * RAMP + 2 * ENGAGEMENT    # 11.4

OVERCUT = 0.1


# ── Wall modification functions ──

def apply_tongue(solid, inner_face, sign, plane, extrude_start, zone_width,
                 wall_base):
    """Grow the outer face outward, then cut the engagement channel."""
    outer = inner_face + sign * WALL_THICKNESS
    r = RAMP
    e = ENGAGEMENT
    f = CHANNEL_FLOOR

    # 1. Growth ramp on outer face — trapezoid from ramp start to tongue tip
    growth = [
        (outer,                      wall_base + OUTER_RAMP_START),
        (outer + sign * TONGUE_GROWTH, wall_base + f),
        (outer + sign * TONGUE_GROWTH, wall_base + TONGUE_TIP_H),
        (outer,                      wall_base + TONGUE_TIP_H),
    ]
    solid = solid.union(
        cq.Workplane(plane)
        .workplane(offset=extrude_start)
        .polyline(growth).close()
        .extrude(zone_width)
    )

    # 2. Channel cut from inner face — zigzag engagement pattern
    ic = inner_face - sign * OVERCUT                   # slightly past inner face
    il = inner_face + sign * TONGUE_INTERLOCK_DEPTH    # 2.2 from inner
    fl = inner_face + sign * TONGUE_FLEX_DEPTH         # 3.0 from inner

    channel = [
        (ic, wall_base + f),
        (il, wall_base + f),
        (fl, wall_base + f + r),
        (fl, wall_base + f + r + e),
        (il, wall_base + f + 2 * r + e),
        (il, wall_base + f + 2 * r + 2 * e),
        (fl, wall_base + TONGUE_TIP_H),
        (ic, wall_base + TONGUE_TIP_H),
    ]
    solid = solid.cut(
        cq.Workplane(plane)
        .workplane(offset=extrude_start - OVERCUT)
        .polyline(channel).close()
        .extrude(zone_width + 2 * OVERCUT)
    )

    return solid


def apply_groove(solid, inner_face, sign, plane, extrude_start, zone_width,
                 wall_base, wall_height):
    """Cut the engagement pattern from the outer face, add rib extension."""
    outer = inner_face + sign * WALL_THICKNESS
    r = RAMP
    e = ENGAGEMENT
    oc = outer + sign * OVERCUT                       # slightly past outer face
    rb = inner_face + sign * GROOVE_RIB_DEPTH         # rib face (2.8 from inner)
    gr = inner_face + sign * GROOVE_GROOVE_DEPTH      # groove face (2.0 from inner)

    # 1. Cut groove pattern from outer face — thins and shapes the wall
    groove = [
        (oc, wall_base - OVERCUT),
        (rb, wall_base - OVERCUT),
        (rb, wall_base + INITIAL_RIB),
        (gr, wall_base + INITIAL_RIB + r),
        (gr, wall_base + INITIAL_RIB + r + e),
        (rb, wall_base + INITIAL_RIB + 2 * r + e),
        (rb, wall_base + INITIAL_RIB + 2 * r + 2 * e),
        (gr, wall_base + GROOVE_TIP_H),
        (oc, wall_base + GROOVE_TIP_H),
    ]
    solid = solid.cut(
        cq.Workplane(plane)
        .workplane(offset=extrude_start - OVERCUT)
        .polyline(groove).close()
        .extrude(zone_width + 2 * OVERCUT)
    )

    # 2. Rib extension past mating surface — the part that protrudes
    wall_top = wall_base + wall_height
    ic = inner_face - sign * OVERCUT                  # overlap into cavity for clean union

    extension = [
        (ic, wall_top),
        (ic, wall_base + GROOVE_TIP_H),
        (gr, wall_base + GROOVE_TIP_H),
        (rb, wall_base + INITIAL_RIB + 2 * r + 2 * e),
        (rb, wall_top),
    ]
    solid = solid.union(
        cq.Workplane(plane)
        .workplane(offset=extrude_start)
        .polyline(extension).close()
        .extrude(zone_width)
    )

    return solid


# ── Test case: simple box shell ──

if __name__ == "__main__":
    FOOTPRINT = 40.0
    CORNER_RADIUS = 6.0
    BASE_PLATE = 3.0
    WALL_HEIGHT = 9.0
    ZONE_WIDTH = 20.0

    HALF = FOOTPRINT / 2
    INNER = HALF - WALL_THICKNESS

    def make_box_shell():
        inner_dim = FOOTPRINT - 2 * WALL_THICKNESS
        inner_r = max(CORNER_RADIUS - WALL_THICKNESS, 0.01)
        outer = (
            cq.Workplane("XY").sketch()
            .rect(FOOTPRINT, FOOTPRINT).vertices().fillet(CORNER_RADIUS)
            .finalize().extrude(BASE_PLATE + WALL_HEIGHT)
        )
        cavity = (
            cq.Workplane("XY").workplane(offset=BASE_PLATE).sketch()
            .rect(inner_dim, inner_dim).vertices().fillet(inner_r)
            .finalize().extrude(WALL_HEIGHT + OVERCUT)
        )
        return outer.cut(cavity)

    WALLS = {
        "+y": (INNER, +1, "YZ"),
        "-y": (-INNER, -1, "YZ"),
        "+x": (INNER, +1, "XZ"),
        "-x": (-INNER, -1, "XZ"),
    }

    bottom = make_box_shell()
    top = make_box_shell()

    for wall_id, (face, sign, plane) in WALLS.items():
        bottom = apply_tongue(
            bottom, face, sign, plane,
            extrude_start=-ZONE_WIDTH / 2,
            zone_width=ZONE_WIDTH,
            wall_base=BASE_PLATE,
        )
        top = apply_groove(
            top, face, sign, plane,
            extrude_start=-ZONE_WIDTH / 2,
            zone_width=ZONE_WIDTH,
            wall_base=BASE_PLATE,
            wall_height=WALL_HEIGHT,
        )

    OUTPUT_DIR = Path(__file__).resolve().parent
    cq.exporters.export(bottom, str(OUTPUT_DIR / "case-snaps-bottom.step"))
    cq.exporters.export(top, str(OUTPUT_DIR / "case-snaps-top.step"))
    print("Exported → case-snaps-bottom.step + case-snaps-top.step")
