"""
Foam-bag shell: two concentric shells with integrated bag cradles.

Bottom cup:  Z=0 to PLAT_BOTTOM.  Prints right-side up (floor on bed).
Upper shell: Z=Z_BOT to SHELL_HEIGHT.  Prints right-side up.
             Inner wall + channel rings touch bed at Z_BOT.
             Annular floor bridges inner wall to channel inner ring at
             Z=PLAT_BOTTOM (3 mm above bed).

The upper shell is built from three revolved bodies unioned together:
  A) Inner body: inner wall (Z_BOT to SHELL_HEIGHT) + annular floor
     (SHELL_OR to R_INNER_IR, PLAT_BOTTOM to PLATFORM_Z)
  B) Outer wall: thin tube (OUTER_SHELL_IR to OUTER_SHELL_OR,
     Z_CHAMFER_TOP-overlap to SHELL_HEIGHT)
  C) Channel: double ring + 45-deg chamfers connecting A and B below
     the floor, with an overlap zone into B above Z_CHAMFER_TOP
"""

import cadquery as cq
from pathlib import Path

# ── Dimensions ──

COLD_CORE_OR = 127.0 / 2 + 6.0 + 1.0   # ~70.5 mm
INNER_FOAM_GAP = 6.35                     # 1/4"
WALL = 1.0
FLOOR = 1.0
FLOOR_FOAM_GAP = 25.4                      # 1" foam layer at the bottom

SHELL_IR = COLD_CORE_OR + INNER_FOAM_GAP  # ~76.85 mm
SHELL_OR = SHELL_IR + WALL                # ~77.85 mm

TANK_HEIGHT = 152.4
SHELL_HEIGHT = TANK_HEIGHT + 10.0 + 3 * 25.4  # 238.6 mm (+3" for foam top + bag height)

CRADLE_DEPTH = 25.0
CRADLE_ARC_DEG = 90.7                       # reduced from 105° — bag width minus 1/2" at inner wall
HALF_CRADLE = CRADLE_ARC_DEG / 2

OUTER_SHELL_IR = SHELL_OR + CRADLE_DEPTH   # ~102.85 mm
OUTER_SHELL_OR = OUTER_SHELL_IR + WALL     # ~103.85 mm

# Derived Z levels
PLAT_BOTTOM = FLOOR + FLOOR_FOAM_GAP       # ~26.4 mm
PLATFORM_Z = PLAT_BOTTOM + FLOOR           # ~27.4 mm

# Stacking channel
CHANNEL_DEPTH = 3.0                         # how far rings extend below floor
CHANNEL_CLEARANCE = 0.5                     # per side

R_INNER_OR = OUTER_SHELL_IR - CHANNEL_CLEARANCE   # inner ring outer face
R_INNER_IR = R_INNER_OR - WALL                      # inner ring inner face
R_OUTER_IR = OUTER_SHELL_OR + CHANNEL_CLEARANCE    # outer ring inner face
R_OUTER_OR = R_OUTER_IR + WALL                      # outer ring outer face

CHAMFER_H = WALL + CHANNEL_CLEARANCE               # 1.5 mm (45 deg)

# Inner channel radii (straddle the inner wall / arc wall at SHELL_IR-SHELL_OR)
IC_INNER_OR = SHELL_IR - CHANNEL_CLEARANCE          # 76.35
IC_INNER_IR = IC_INNER_OR - WALL                     # 75.35
IC_OUTER_IR = SHELL_OR + CHANNEL_CLEARANCE           # 78.35
IC_OUTER_OR = IC_OUTER_IR + WALL                     # 79.35

Z_BOT = PLAT_BOTTOM - CHANNEL_DEPTH                # 23.4 mm
Z_SPLIT = PLAT_BOTTOM                               # 26.4 mm
Z_CHAMFER_TOP = PLAT_BOTTOM + CHAMFER_H            # 27.9 mm

OVERLAP = 1.0   # boolean overlap for reliable unions

# Divider / internal wall angles (shared by both pieces)
DIVIDER_ANGLES = [
    -HALF_CRADLE,
    HALF_CRADLE,
    180.0 - HALF_CRADLE,
    180.0 + HALF_CRADLE,
]


# ═══════════════════════════════════════════════════════
# BOTTOM CUP
# ═══════════════════════════════════════════════════════
#
# Simple cup: full-radius floor at Z=0, outer wall up to PLAT_BOTTOM,
# foam floor at Z=FLOOR.  Foam cavity is the void between the two floors.
#
# XZ profile (revolved 360 deg around Z axis):
#
#   PLAT_BOTTOM ──┐              ┌──
#                 │  foam cavity │
#       FLOOR  ═══╧══════════════╧═══   (foam floor / bottom floor top)
#           0  ══════════════════════   (bottom floor bottom)
#              R=0             OUTER_SHELL_OR

bottom_cup = (
    cq.Workplane("XZ")
    .moveTo(0, 0)
    .lineTo(OUTER_SHELL_OR, 0)
    .lineTo(OUTER_SHELL_OR, PLAT_BOTTOM)
    .lineTo(OUTER_SHELL_IR, PLAT_BOTTOM)
    .lineTo(OUTER_SHELL_IR, FLOOR)
    .lineTo(0, FLOOR)
    .close()
    .revolve(360, (0, 0, 0), (0, 1, 0))
)

# ── Foam cavity holes ──
FOAM_HOLE_DIA = 8.0

# (Center hole is on the upper shell floor, not here)

# 4 diamond-shaped wall holes (self-supporting at 45 deg)
DIAMOND_SIZE = 10.0
FOAM_MID_Z = FLOOR + FLOOR_FOAM_GAP / 2

for angle_deg in [90, 270]:  # 0° and 180° removed — bags sit there
    diamond = (
        cq.Workplane("YZ")
        .transformed(offset=(0, 0, OUTER_SHELL_IR - 2))
        .moveTo(0, FOAM_MID_Z - DIAMOND_SIZE / 2)
        .lineTo(DIAMOND_SIZE / 2, FOAM_MID_Z)
        .lineTo(0, FOAM_MID_Z + DIAMOND_SIZE / 2)
        .lineTo(-DIAMOND_SIZE / 2, FOAM_MID_Z)
        .close()
        .extrude(WALL + 4)
    )
    diamond = diamond.rotate((0, 0, 0), (0, 0, 1), angle_deg)
    bottom_cup = bottom_cup.cut(diamond)

# ── Internal walls to form bag pockets ──
# Each bag zone (at 0° and 180°) gets 3 walls forming a pocket:
#   - 2 radial side walls at ±HALF_CRADLE (same angles as dividers)
#   - 1 arc wall at the inner shell radius spanning the cradle arc
# The outer wall of the bottom cup is the 4th side.

BC_WALL_BOTTOM = FLOOR / 2   # embed into foam floor
BC_WALL_RADIAL_INNER = SHELL_IR               # overlap into arc wall for clean union
BC_WALL_RADIAL_OUTER = OUTER_SHELL_IR + OVERLAP  # end at outer shell wall

# Radial side walls (4 total, at divider angles)
for angle in DIVIDER_ANGLES:
    bc_div = (
        cq.Workplane("XZ")
        .moveTo(BC_WALL_RADIAL_INNER, BC_WALL_BOTTOM)
        .lineTo(BC_WALL_RADIAL_INNER, PLAT_BOTTOM)
        .lineTo(BC_WALL_RADIAL_OUTER, PLAT_BOTTOM)
        .lineTo(BC_WALL_RADIAL_OUTER, BC_WALL_BOTTOM)
        .close()
        .extrude(WALL / 2, both=True)
    )
    bc_div = bc_div.rotate((0, 0, 0), (0, 0, 1), angle)
    bottom_cup = bottom_cup.union(bc_div, tol=0.05)

# Arc walls at the inner shell radius (one per bag zone)
for cradle_center in [0.0, 180.0]:
    bc_arc = (
        cq.Workplane("XZ")
        .moveTo(SHELL_IR, BC_WALL_BOTTOM)
        .lineTo(SHELL_IR, PLAT_BOTTOM)
        .lineTo(SHELL_OR, PLAT_BOTTOM)
        .lineTo(SHELL_OR, BC_WALL_BOTTOM)
        .close()
        .revolve(CRADLE_ARC_DEG, (0, 0, 0), (0, 1, 0))
    )
    bc_arc = bc_arc.rotate(
        (0, 0, 0), (0, 0, 1), cradle_center - HALF_CRADLE
    )
    bottom_cup = bottom_cup.union(bc_arc, tol=0.05)

bc_solids = bottom_cup.solids().vals()
print(f"Bottom cup: {len(bc_solids)} solid(s)")
for i, s in enumerate(bc_solids):
    bb = s.BoundingBox()
    print(f"  Solid {i}: X[{bb.xmin:.1f},{bb.xmax:.1f}] "
          f"Y[{bb.ymin:.1f},{bb.ymax:.1f}] Z[{bb.zmin:.1f},{bb.zmax:.1f}]")

# Horizontal cross-section (top-down view) through bottom cup foam cavity
import math
_bc_mid_z = FLOOR + FLOOR_FOAM_GAP / 2  # mid-height of foam cavity
_bc_hz_slab = (
    cq.Workplane("XY")
    .box(300, 300, 0.5, centered=(True, True, True))
    .translate((0, 0, _bc_mid_z))
)
print(f"\n── BOTTOM CUP top-down at Z={_bc_mid_z:.1f} (XY coords) ──")
try:
    _bc_hz = bottom_cup.intersect(_bc_hz_slab)
    _bc_hz_verts = _bc_hz.vertices().vals()
    _bc_hz_coords = sorted(set(
        (round(v.X, 2), round(v.Y, 2))
        for v in _bc_hz_verts
    ))
    for x, y in _bc_hz_coords:
        r = math.sqrt(x**2 + y**2)
        ang = math.degrees(math.atan2(y, x))
        print(f"  X={x:8.2f}  Y={y:8.2f}  (R={r:6.2f}, θ={ang:7.2f}°)")
except Exception as e:
    print(f"  Section failed: {e}")


# ═══════════════════════════════════════════════════════
# UPPER SHELL — Part A: Inner body
# ═══════════════════════════════════════════════════════
#
# Inner wall extends down to Z_BOT so it touches the build plate.
# Annular floor from SHELL_OR to R_INNER_IR at PLAT_BOTTOM to PLATFORM_Z.
# When printed right-side up, the inner wall and channel rings sit on the
# bed at Z_BOT; the floor bridges to the inner ring at 3 mm height.
#
# XZ profile:
#
#   SHELL_HEIGHT ─┐
#                 │ inner
#                 │ wall
#   PLATFORM_Z    └───────── R_INNER_IR
#   PLAT_BOTTOM   ┌───────── R_INNER_IR
#                 │
#       Z_BOT  ───┘
#            SHELL_IR  SHELL_OR

inner_body = (
    cq.Workplane("XZ")
    .moveTo(0, Z_BOT)
    .lineTo(R_INNER_IR, Z_BOT)
    .lineTo(R_INNER_IR, Z_BOT + FLOOR)
    .lineTo(SHELL_OR, Z_BOT + FLOOR)
    .lineTo(SHELL_OR, SHELL_HEIGHT)
    .lineTo(SHELL_IR, SHELL_HEIGHT)
    .lineTo(SHELL_IR, Z_BOT + FLOOR)
    .lineTo(0, Z_BOT + FLOOR)
    .close()
    .revolve(360, (0, 0, 0), (0, 1, 0))
)

ib_solids = inner_body.solids().vals()
print(f"\nInner body: {len(ib_solids)} solid(s)")


# ═══════════════════════════════════════════════════════
# UPPER SHELL — Part B: Outer wall
# ═══════════════════════════════════════════════════════
#
# Thin tube.  Starts at Z_CHAMFER_TOP - OVERLAP (overlaps with channel
# chamfer for a reliable boolean union).

outer_wall = (
    cq.Workplane("XZ")
    .moveTo(OUTER_SHELL_IR, Z_CHAMFER_TOP)
    .lineTo(OUTER_SHELL_IR, SHELL_HEIGHT)
    .lineTo(OUTER_SHELL_OR, SHELL_HEIGHT)
    .lineTo(OUTER_SHELL_OR, Z_CHAMFER_TOP)
    .close()
    .revolve(360, (0, 0, 0), (0, 1, 0))
)

ow_solids = outer_wall.solids().vals()
print(f"Outer wall: {len(ow_solids)} solid(s)")


# ═══════════════════════════════════════════════════════
# UPPER SHELL — Part C: Channel
# ═══════════════════════════════════════════════════════
#
# Double ring with gap, plus 45-deg chamfers converging to outer wall.
# Inner ring overlaps the floor at R_INNER_IR (shared edge).
# Overlap zone above Z_CHAMFER_TOP extends into outer wall body.
#
# XZ cross-section (not to scale):
#
#                    OW_IR ─── OW_OR
#                      │  wall  │            ← outer wall body (Part B)
#   Z_OL_TOP   ═══════╧════════╧═══════     ← overlap into outer wall
#                     /          \
#   Z_CHAMFER_TOP   /   chamfer   \          ← 45 deg converging
#                  /      45°      \
#   Z_SPLIT     ring   2mm gap   ring        ← ring tops / gap
#               ││                ││
#   Z_BOT      ││                ││          ← ring bottoms
#           R_INNER          R_OUTER
#           IR  OR           IR  OR

Z_OL_TOP = Z_CHAMFER_TOP + 5  # extend into outer wall for clean union

channel = (
    cq.Workplane("XZ")
    # Inner ring inside face, going up
    .moveTo(R_INNER_IR, Z_BOT)
    .lineTo(R_INNER_IR, Z_SPLIT)
    # 45-deg chamfer: inner face converges outward to meet outer wall
    .lineTo(OUTER_SHELL_IR, Z_CHAMFER_TOP)
    # Up into outer wall overlap zone
    .lineTo(OUTER_SHELL_IR, Z_OL_TOP)
    .lineTo(OUTER_SHELL_OR, Z_OL_TOP)
    # Back down to chamfer on outer side
    .lineTo(OUTER_SHELL_OR, Z_CHAMFER_TOP)
    # 45-deg chamfer: outer face diverges outward to meet outer ring
    .lineTo(R_OUTER_OR, Z_SPLIT)
    # Outer ring outside face, going down
    .lineTo(R_OUTER_OR, Z_BOT)
    # Across outer ring bottom
    .lineTo(R_OUTER_IR, Z_BOT)
    # Outer ring inside face (gap side), going up
    .lineTo(R_OUTER_IR, Z_SPLIT)
    # 45-deg peaked ceiling across gap (self-supporting)
    .lineTo((R_INNER_OR + R_OUTER_IR) / 2, Z_SPLIT + (R_OUTER_IR - R_INNER_OR) / 2)
    .lineTo(R_INNER_OR, Z_SPLIT)
    # Inner ring outside face (gap side), going down
    .lineTo(R_INNER_OR, Z_BOT)
    # Close across inner ring bottom
    .close()
    .revolve(360, (0, 0, 0), (0, 1, 0))
)

ch_solids = channel.solids().vals()
print(f"Channel: {len(ch_solids)} solid(s)")


# ═══════════════════════════════════════════════════════
# UPPER SHELL — Union
# ═══════════════════════════════════════════════════════

upper_shell = inner_body.union(channel, tol=0.1)
us_solids = upper_shell.solids().vals()
print(f"\nAfter inner_body + channel: {len(us_solids)} solid(s)")

upper_shell = upper_shell.union(outer_wall, tol=0.1)
us_solids = upper_shell.solids().vals()
print(f"After + outer_wall: {len(us_solids)} solid(s)")


# ═══════════════════════════════════════════════════════
# UPPER SHELL — Inner channel (arc wall lips)
# ═══════════════════════════════════════════════════════
#
# Same profile as the outer channel, but at the inner wall radii
# and only spanning the cradle arcs (0° and 180°).
# These rings on the upper shell straddle the bottom cup's arc walls.
#
# XZ cross-section (same shape as outer channel):
#
#                  SHELL_IR ─── SHELL_OR
#                     │   wall   │             ← inner wall (Part A)
#   IC_OL_TOP  ══════╧═════════╧══════        ← overlap into inner wall
#                    /            \
#   Z_CHAMFER_TOP  /    chamfer    \           ← 45 deg converging
#                 /       45°       \
#   Z_SPLIT     ring    2mm gap    ring        ← ring tops / peaked gap ceiling
#               ││                  ││
#   Z_BOT      ││                  ││          ← ring bottoms
#           IC_INNER            IC_OUTER
#           IR   OR             IR   OR

IC_OL_TOP = Z_CHAMFER_TOP + 5  # overlap into inner wall for clean union

# How far the outer ring wall extends past each divider.
# At R≈79, RC_RIDGE_HALF (2 mm) subtends ~1.4°; 3° gives overlap.
IC_ARC_EXTENSION = 3.0  # degrees past each divider end

for cradle_center in [0.0, 180.0]:
    # Channel body: rings + chamfers + peaked gap ceiling
    ic_channel = (
        cq.Workplane("XZ")
        # Inner ring inside face, going up
        .moveTo(IC_INNER_IR, Z_BOT)
        .lineTo(IC_INNER_IR, Z_SPLIT)
        # 45-deg chamfer: converges outward to inner wall
        .lineTo(SHELL_IR, Z_CHAMFER_TOP)
        # Up into inner wall overlap zone
        .lineTo(SHELL_IR, IC_OL_TOP)
        .lineTo(SHELL_OR, IC_OL_TOP)
        # Back down to chamfer on outer side
        .lineTo(SHELL_OR, Z_CHAMFER_TOP)
        # 45-deg chamfer: converges inward to outer ring
        .lineTo(IC_OUTER_OR, Z_SPLIT)
        # Outer ring outside face, going down
        .lineTo(IC_OUTER_OR, Z_BOT)
        # Across outer ring bottom
        .lineTo(IC_OUTER_IR, Z_BOT)
        # Outer ring inside face (gap side), going up
        .lineTo(IC_OUTER_IR, Z_SPLIT)
        # 45-deg peaked ceiling across gap (self-supporting)
        .lineTo((IC_INNER_OR + IC_OUTER_IR) / 2,
                Z_SPLIT + (IC_OUTER_IR - IC_INNER_OR) / 2)
        .lineTo(IC_INNER_OR, Z_SPLIT)
        # Inner ring outside face (gap side), going down
        .lineTo(IC_INNER_OR, Z_BOT)
        # Close across inner ring bottom
        .close()
        .revolve(CRADLE_ARC_DEG, (0, 0, 0), (0, 1, 0))
    )
    ic_channel = ic_channel.rotate(
        (0, 0, 0), (0, 0, 1), cradle_center - HALF_CRADLE
    )
    upper_shell = upper_shell.union(ic_channel, tol=0.1)

    # Cut the gap in the inner wall: remove material between rings
    # so the bottom cup's arc wall can slot in.
    # Profile traces the gap interior up to the peaked ceiling.
    ic_gap = (
        cq.Workplane("XZ")
        .moveTo(IC_INNER_OR, Z_BOT - 0.1)
        .lineTo(IC_INNER_OR, Z_SPLIT)
        .lineTo((IC_INNER_OR + IC_OUTER_IR) / 2,
                Z_SPLIT + (IC_OUTER_IR - IC_INNER_OR) / 2)
        .lineTo(IC_OUTER_IR, Z_SPLIT)
        .lineTo(IC_OUTER_IR, Z_BOT - 0.1)
        .close()
        .revolve(CRADLE_ARC_DEG, (0, 0, 0), (0, 1, 0))
    )
    ic_gap = ic_gap.rotate(
        (0, 0, 0), (0, 0, 1), cradle_center - HALF_CRADLE
    )
    upper_shell = upper_shell.cut(ic_gap)

    # IC_INNER ring wall extensions: continue the center-side ring
    # (IC_INNER_IR–IC_INNER_OR, R=75.35–76.35) past each divider end.
    # This is the "outer arc channel wall" from the bag-hole perspective.
    # Simple revolved rectangle — keeps boolean fast.
    for sign, div_angle in [(-1, cradle_center - HALF_CRADLE),
                            (+1, cradle_center + HALF_CRADLE)]:
        ext_start = div_angle - IC_ARC_EXTENSION if sign == -1 else div_angle - 1.0
        ext_arc = IC_ARC_EXTENSION + 1.0  # 3° extension + 1° overlap
        ic_ext = (
            cq.Workplane("XZ")
            .moveTo(IC_INNER_IR, Z_BOT)
            .lineTo(IC_INNER_IR, Z_SPLIT + OVERLAP)
            .lineTo(IC_INNER_OR, Z_SPLIT + OVERLAP)
            .lineTo(IC_INNER_OR, Z_BOT)
            .close()
            .revolve(ext_arc, (0, 0, 0), (0, 1, 0))
        )
        ic_ext = ic_ext.rotate((0, 0, 0), (0, 0, 1), ext_start)
        upper_shell = upper_shell.union(ic_ext, tol=0.05)

us_solids = upper_shell.solids().vals()
print(f"After + inner channel (arcs + corner extensions): {len(us_solids)} solid(s)")


# ═══════════════════════════════════════════════════════
# UPPER SHELL — Dividers
# ═══════════════════════════════════════════════════════

# Divider profile in the radial-Z plane:
#
#   SHELL_HEIGHT ┌──────────────────────────────────┐ SHELL_HEIGHT
#                │          divider slab             │
#   Z_CHAMFER_TOP├──┐                          ┌────┤ Z_CHAMFER_TOP
#                    │ inner        outer       │
#       Z_SPLIT      │ chamfer      chamfer    │
#                    │                         │
#  Z_BOT+FLOOR/2    └─────────────────────────┘ DIVIDER_FLOOR
#          IC_OUTER_OR                    R_INNER_IR
#   SHELL_OR-OL                              OUTER_SHELL_IR+OL
#
# Bottom follows both channel chamfer slopes:
#   - Inner: from (SHELL_OR, Z_CHAMFER_TOP) to (IC_OUTER_OR, Z_SPLIT)
#   - Drops to DIVIDER_FLOOR, flat across to R_INNER_IR
#   - Outer: from (R_INNER_IR, Z_SPLIT) to (OUTER_SHELL_IR, Z_CHAMFER_TOP)

DIVIDER_FLOOR = Z_BOT + FLOOR / 2   # embed into actual floor

for angle in DIVIDER_ANGLES:
    div = (
        cq.Workplane("XZ")
        # Inner end: start at inner wall outer surface (not past it)
        # so the divider does not protrude into the arc channel zone.
        .moveTo(SHELL_OR, Z_CHAMFER_TOP)
        .lineTo(SHELL_OR, SHELL_HEIGHT)
        # Across top to outer end
        .lineTo(OUTER_SHELL_IR + OVERLAP, SHELL_HEIGHT)
        # Outer channel ramp down
        .lineTo(OUTER_SHELL_IR + OVERLAP, Z_CHAMFER_TOP)
        .lineTo(R_INNER_IR, Z_SPLIT)
        # Drop to floor, flat across
        .lineTo(R_INNER_IR, DIVIDER_FLOOR)
        .lineTo(IC_OUTER_OR, DIVIDER_FLOOR)
        # Inner channel ramp up
        .lineTo(IC_OUTER_OR, Z_SPLIT)
        .lineTo(SHELL_OR, Z_CHAMFER_TOP)
        .close()
        .extrude(WALL / 2, both=True)
    )
    div = div.rotate((0, 0, 0), (0, 0, 1), angle)
    upper_shell = upper_shell.union(div, tol=0.05)

us_solids = upper_shell.solids().vals()
print(f"After + dividers: {len(us_solids)} solid(s)")


# ═══════════════════════════════════════════════════════
# UPPER SHELL — Radial channel (divider wall lips)
# ═══════════════════════════════════════════════════════
#
# Same cross-section profile as the arc channels, extruded along
# the divider direction.  Runs from IC_OUTER_OR to R_INNER_IR
# (between the two arc channel zones, not through them).
#
# YZ cross-section (identical shape to outer/inner channel XZ profile):
#
#                  center of divider wall
#                          │
#   Z_CHAMFER_TOP  ───────╱│╲───────     ← chamfers converge to wall
#                        ╱ │ ╲
#   Z_SPLIT        ring │gap│ ring       ← peaked ceiling in gap
#                   ││   │  │  ││
#   Z_BOT          ││   │  │  ││
#               ─RC_RIDGE_HALF─┘
#                  ─RC_GAP_HALF┘
#
# Built as a single body per divider (full profile), then gap cut.

RC_GAP_HALF = WALL / 2 + CHANNEL_CLEARANCE          # 1.0 mm
RC_RIDGE_HALF = RC_GAP_HALF + WALL                   # 2.0 mm
RC_PEAK_Z = Z_SPLIT + RC_GAP_HALF                    # 27.4

# Radial extent for BODY (ridges): stays between the arc channel zones.
# Ridges must NOT extend into arc gap zones or they fill the groove.
RC_R_INNER = IC_OUTER_OR    # 79.35 — outside inner arc ring zone
RC_R_OUTER = R_INNER_IR     # 101.35 — outside outer arc ring zone
RC_R_LEN = RC_R_OUTER - RC_R_INNER

for angle in DIVIDER_ANGLES:
    # Full channel body: YZ profile extruded along radial direction.
    # Profile mirrors the arc channel shape exactly.
    rc_body = (
        cq.Workplane("YZ")
        # Inner ridge inside face (negative Y side), going up
        .moveTo(-RC_RIDGE_HALF, Z_BOT)
        .lineTo(-RC_RIDGE_HALF, Z_SPLIT)
        # 45-deg chamfer: converges to wall center
        .lineTo(-WALL / 2, Z_CHAMFER_TOP)
        # Up into divider wall overlap zone
        .lineTo(-WALL / 2, Z_CHAMFER_TOP + 5)
        .lineTo(WALL / 2, Z_CHAMFER_TOP + 5)
        # Back down to chamfer on other side
        .lineTo(WALL / 2, Z_CHAMFER_TOP)
        # 45-deg chamfer: diverges to outer ridge
        .lineTo(RC_RIDGE_HALF, Z_SPLIT)
        # Outer ridge outside face, going down
        .lineTo(RC_RIDGE_HALF, Z_BOT)
        # Across outer ridge bottom
        .lineTo(RC_GAP_HALF, Z_BOT)
        # Outer ridge inside face (gap side), going up
        .lineTo(RC_GAP_HALF, Z_SPLIT)
        # Peaked ceiling across gap
        .lineTo(0, RC_PEAK_Z)
        .lineTo(-RC_GAP_HALF, Z_SPLIT)
        # Inner ridge outside face (gap side), going down
        .lineTo(-RC_GAP_HALF, Z_BOT)
        # Close across inner ridge bottom
        .close()
        .extrude(RC_R_LEN)
        .translate((RC_R_INNER, 0, 0))
    )
    rc_body = rc_body.rotate((0, 0, 0), (0, 0, 1), angle)
    upper_shell = upper_shell.union(rc_body, tol=0.05)

    # Corner ceiling patch for the OUTER transition zone only
    # (R=101.35-104.35).  The outer channel is 360° so its ring walls
    # already exist; only the ceiling needs patching at corners.
    # The INNER transition (R=76.35-79.35) is handled by the arc
    # channel extensions above — no radial-profile patch needed there.
    patch_ir, patch_or = RC_R_OUTER, R_OUTER_IR
    patch = (
        cq.Workplane("YZ")
        .moveTo(-RC_RIDGE_HALF, Z_SPLIT)
        .lineTo(-WALL / 2, Z_CHAMFER_TOP)
        .lineTo(-WALL / 2, Z_CHAMFER_TOP + 5)
        .lineTo(WALL / 2, Z_CHAMFER_TOP + 5)
        .lineTo(WALL / 2, Z_CHAMFER_TOP)
        .lineTo(RC_RIDGE_HALF, Z_SPLIT)
        .close()
        .extrude(patch_or - patch_ir)
        .translate((patch_ir, 0, 0))
    )
    patch = patch.rotate((0, 0, 0), (0, 0, 1), angle)
    upper_shell = upper_shell.union(patch, tol=0.05)

    # Single peaked-ceiling gap cut spanning the full radial range
    # (arc gap zone through mid-zone through arc gap zone).
    # Below Z_SPLIT: removes groove walls/floor material for connectivity.
    # Above Z_SPLIT: shapes the peaked ceiling in both mid-zone and patches.
    RC_GAP_FULL_IR = IC_INNER_OR   # 76.35
    RC_GAP_FULL_OR = R_OUTER_IR    # 104.35
    RC_GAP_FULL_LEN = RC_GAP_FULL_OR - RC_GAP_FULL_IR
    rc_gap = (
        cq.Workplane("YZ")
        .moveTo(-RC_GAP_HALF, Z_BOT - 0.1)
        .lineTo(-RC_GAP_HALF, Z_SPLIT)
        .lineTo(0, RC_PEAK_Z)
        .lineTo(RC_GAP_HALF, Z_SPLIT)
        .lineTo(RC_GAP_HALF, Z_BOT - 0.1)
        .close()
        .extrude(RC_GAP_FULL_LEN + 0.2)
        .translate((RC_GAP_FULL_IR - 0.1, 0, 0))
    )
    rc_gap = rc_gap.rotate((0, 0, 0), (0, 0, 1), angle)
    upper_shell = upper_shell.cut(rc_gap)

us_solids = upper_shell.solids().vals()
print(f"After + radial channel: {len(us_solids)} solid(s)")


# ── Center floor hole (through upper shell floor) ──
center_hole = (
    cq.Workplane("XY")
    .transformed(offset=(0, 0, Z_BOT - 1))
    .circle(FOAM_HOLE_DIA / 2)
    .extrude(FLOOR + 2)
)
upper_shell = upper_shell.cut(center_hole)

# ── Cut bag cradle openings in the floor ──
# Two arc-shaped slots through the floor at the cradle angles,
# spanning from inner wall (SHELL_OR) to floor outer edge (R_INNER_IR).
# Each cradle is centered at 0° and 180°, spanning ±HALF_CRADLE.
# Inset by ~1° on each side to preserve floor under the dividers.

# Compute angular clearance from the radial channel ridge width.
# At the smallest cut radius (IC_OUTER_OR + 0.1), the ridge extends
# RC_RIDGE_HALF from center.  Convert to angle and add 0.5° margin.
DIVIDER_ANGULAR_CLEARANCE = math.degrees(RC_RIDGE_HALF / (IC_OUTER_OR + 0.1)) + 0.5
CUT_ARC = CRADLE_ARC_DEG - 2 * DIVIDER_ANGULAR_CLEARANCE

for cradle_center in [0.0, 180.0]:
    cradle_cut = (
        cq.Workplane("XZ")
        .moveTo(IC_OUTER_OR + 0.1, Z_BOT - 0.1)
        .lineTo(IC_OUTER_OR + 0.1, Z_BOT + FLOOR + 0.1)
        .lineTo(R_INNER_IR - 0.1, Z_BOT + FLOOR + 0.1)
        .lineTo(R_INNER_IR - 0.1, Z_BOT - 0.1)
        .close()
        .revolve(CUT_ARC, (0, 0, 0), (0, 1, 0))
    )
    cradle_cut = cradle_cut.rotate(
        (0, 0, 0), (0, 0, 1), cradle_center - CUT_ARC / 2
    )
    upper_shell = upper_shell.cut(cradle_cut)

us_solids = upper_shell.solids().vals()
print(f"After cradle floor cuts: {len(us_solids)} solid(s)")


# ═══════════════════════════════════════════════════════
# DIAGNOSTICS
# ═══════════════════════════════════════════════════════

for name, part in [("Bottom cup", bottom_cup), ("Upper shell", upper_shell)]:
    solids = part.solids().vals()
    print(f"\n{name}: {len(solids)} solid(s)")
    for i, s in enumerate(solids):
        bb = s.BoundingBox()
        print(f"  Solid {i}: X[{bb.xmin:.1f},{bb.xmax:.1f}] "
              f"Y[{bb.ymin:.1f},{bb.ymax:.1f}] Z[{bb.zmin:.1f},{bb.zmax:.1f}]")

print(f"\nZ levels:")
print(f"  Z={Z_BOT:.1f}:  channel ring bottoms / upper shell bed contact")
print(f"  Z=0.0:  bottom cup floor")
print(f"  Z={FLOOR:.1f}:  foam cavity bottom")
print(f"  Z={PLAT_BOTTOM:.1f}: split line / ring tops / upper floor bottom")
print(f"  Z={PLATFORM_Z:.1f}: upper floor top")
print(f"  Z={Z_CHAMFER_TOP:.1f}: chamfer tops / outer wall starts")
print(f"  Z={SHELL_HEIGHT:.1f}: shell top (open)")

import math

# Bottom cup cross-section at Y=0 (cuts through bag zone + across internal walls)
slab_bc = (
    cq.Workplane("XY")
    .box(300, 0.02, 300, centered=(True, True, True))
    .translate((0, 0, 15))
)
print(f"\n── BOTTOM CUP cross-section at Y=0 (positive X, Z < 28) ──")
try:
    bc_sect = bottom_cup.intersect(slab_bc)
    bc_verts = bc_sect.vertices().vals()
    bc_coords = sorted(set(
        (round(v.X, 2), round(v.Z, 2))
        for v in bc_verts
    ))
    for r, z in bc_coords:
        if r > 0 and z < 28:
            print(f"  R={r:7.2f}  Z={z:5.2f}")
except Exception as e:
    print(f"  Section failed: {e}")

# Cross-section through Y=0 (between dividers — shows walls/channel only)
print("\n── XZ CROSS-SECTION at Y=0 (Z < 35) ──")
slab_y0 = (
    cq.Workplane("XY")
    .box(300, 0.02, 300, centered=(True, True, True))
    .translate((0, 0, 80))
)
try:
    section = upper_shell.intersect(slab_y0)
    verts = section.vertices().vals()
    coords = sorted(set((round(v.X, 2), round(v.Z, 2)) for v in verts))
    for x, z in coords:
        if x > 0 and z < 35:
            print(f"  R={x:7.2f}  Z={z:5.2f}")
except Exception as e:
    print(f"  Section failed: {e}")

# Cross-sections around the first divider to see floor vs cut boundary
DIV_ANGLE = DIVIDER_ANGLES[0]  # -45.35°
for label, angle in [
    (f"divider at {DIV_ANGLE:.1f}°", DIV_ANGLE),
    (f"cradle side at {DIV_ANGLE + 2:.1f}°", DIV_ANGLE + 2),
    (f"gap side at {DIV_ANGLE - 2:.1f}°", DIV_ANGLE - 2),
]:
    angle_rad = math.radians(angle)
    slab_test = (
        cq.Workplane("XY")
        .box(300, 0.02, 300, centered=(True, True, True))
        .translate((0, 0, 80))
        .rotate((0, 0, 0), (0, 0, 1), angle)
    )
    print(f"\n── CROSS-SECTION {label} (Z < 30, R=70-110) ──")
    try:
        section_test = upper_shell.intersect(slab_test)
        verts_test = section_test.vertices().vals()
        ca, sa = math.cos(angle_rad), math.sin(angle_rad)
        coords_test = sorted(set(
            (round(v.X * ca + v.Y * sa, 2), round(v.Z, 2))
            for v in verts_test
        ))
        for r, z in coords_test:
            if 70 < r < 110 and z < 30:
                print(f"  R={r:7.2f}  Z={z:5.2f}")
    except Exception as e:
        print(f"  Section failed: {e}")

DIV_ANGLE_RAD = math.radians(DIV_ANGLE)
slab_div = (
    cq.Workplane("XY")
    .box(300, 0.02, 300, centered=(True, True, True))
    .translate((0, 0, 80))
    .rotate((0, 0, 0), (0, 0, 1), DIV_ANGLE)
)
print(f"\n── FULL CROSS-SECTION through divider at {DIV_ANGLE:.1f}° (Z < 35) ──")
try:
    section2 = upper_shell.intersect(slab_div)
    verts2 = section2.vertices().vals()
    # Project onto the radial direction for this angle
    ca, sa = math.cos(DIV_ANGLE_RAD), math.sin(DIV_ANGLE_RAD)
    coords2 = sorted(set(
        (round(v.X * ca + v.Y * sa, 2), round(v.Z, 2))
        for v in verts2
    ))
    for r, z in coords2:
        if r > 0 and z < 35:
            print(f"  R={r:7.2f}  Z={z:5.2f}")
except Exception as e:
    print(f"  Section failed: {e}")

print(f"\nRadii:")
print(f"  Inner wall:  {SHELL_IR:.2f} - {SHELL_OR:.2f}")
print(f"  Floor to:    {R_INNER_IR:.2f}")
print(f"  Inner ring:  {R_INNER_IR:.2f} - {R_INNER_OR:.2f}")
print(f"  Gap:         {R_INNER_OR:.2f} - {R_OUTER_IR:.2f}  ({R_OUTER_IR - R_INNER_OR:.1f} mm)")
print(f"  Outer ring:  {R_OUTER_IR:.2f} - {R_OUTER_OR:.2f}")
print(f"  Outer wall:  {OUTER_SHELL_IR:.2f} - {OUTER_SHELL_OR:.2f}")


# ═══════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════

out_dir = Path(__file__).resolve().parent

bottom_path = out_dir / "foam-bag-shell-bottom.step"
cq.exporters.export(bottom_cup, str(bottom_path))
print(f"\nExported: {bottom_path}")

upper_path = out_dir / "foam-bag-shell-upper.step"
cq.exporters.export(upper_shell, str(upper_path))
print(f"Exported: {upper_path}")
