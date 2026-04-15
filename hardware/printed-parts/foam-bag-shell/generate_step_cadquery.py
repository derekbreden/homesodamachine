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
# UPPER SHELL — Union (inner body + outer wall)
# ═══════════════════════════════════════════════════════
#
# The outer channel (formerly Part C, a 360-deg revolved body) is now
# built entirely by sweeps: closed-loop pocket sweeps create the outer
# channel at pocket positions, and gap arc sweeps cover the zones
# between pockets.

upper_shell = inner_body.union(outer_wall, tol=0.1)
us_solids = upper_shell.solids().vals()
print(f"\nAfter inner_body + outer_wall: {len(us_solids)} solid(s)")


# ═══════════════════════════════════════════════════════
# UPPER SHELL — Pocket channels (closed-loop sweep)
# ═══════════════════════════════════════════════════════
#
# Each pocket's channel is swept around a closed rectangular loop:
#   outer arc (CW) → radial inward → inner arc (CCW) → radial outward
#
# All four corners per pocket are mitered by transition='right'.
# The outer arc portion overlaps with Part C (360-deg channel);
# the union absorbs this harmlessly.

IC_OL_TOP = Z_CHAMFER_TOP + 5  # overlap into walls for clean union

RC_GAP_HALF = WALL / 2 + CHANNEL_CLEARANCE    # 1.0 mm
RC_RIDGE_HALF = RC_GAP_HALF + WALL             # 2.0 mm
RC_PEAK_Z = Z_SPLIT + RC_GAP_HALF              # 27.4 mm

R_PATH_INNER = (SHELL_IR + SHELL_OR) / 2       # 77.35 — inner wall center
R_PATH_OUTER = (R_INNER_OR + R_OUTER_IR) / 2   # 103.35 — outer channel gap center

for cradle_center in [0.0, 180.0]:
    a_lo = math.radians(cradle_center - HALF_CRADLE)
    a_hi = math.radians(cradle_center + HALF_CRADLE)
    a_mid = math.radians(cradle_center)

    # Closed-loop path points
    pA = (R_PATH_OUTER * math.cos(a_hi), R_PATH_OUTER * math.sin(a_hi))
    pB = (R_PATH_OUTER * math.cos(a_mid), R_PATH_OUTER * math.sin(a_mid))
    pC = (R_PATH_OUTER * math.cos(a_lo), R_PATH_OUTER * math.sin(a_lo))
    pD = (R_PATH_INNER * math.cos(a_lo), R_PATH_INNER * math.sin(a_lo))
    pE = (R_PATH_INNER * math.cos(a_mid), R_PATH_INNER * math.sin(a_mid))
    pF = (R_PATH_INNER * math.cos(a_hi), R_PATH_INNER * math.sin(a_hi))

    path_wire = (
        cq.Workplane("XY")
        .moveTo(*pA)
        .threePointArc(pB, pC)   # outer arc: hi → mid → lo
        .lineTo(*pD)              # radial inward along divider 1
        .threePointArc(pE, pF)   # inner arc: lo → mid → hi
        .lineTo(*pA)              # radial outward along divider 2 (closes loop)
        .wire().val()
    )

    # Profile plane at pA — CW tangent at angle_hi
    profile_plane = cq.Plane(
        origin=(pA[0], pA[1], 0),
        xDir=(math.cos(a_hi), math.sin(a_hi), 0),
        normal=(math.sin(a_hi), -math.cos(a_hi), 0),
    )

    # Solid body profile (no gap notch — groove cuts the gap later)
    swept_body = (
        cq.Workplane(profile_plane)
        .moveTo(-RC_RIDGE_HALF, Z_BOT)
        .lineTo(-RC_RIDGE_HALF, Z_SPLIT)
        .lineTo(-WALL / 2, Z_CHAMFER_TOP)
        .lineTo(-WALL / 2, IC_OL_TOP)
        .lineTo(WALL / 2, IC_OL_TOP)
        .lineTo(WALL / 2, Z_CHAMFER_TOP)
        .lineTo(RC_RIDGE_HALF, Z_SPLIT)
        .lineTo(RC_RIDGE_HALF, Z_BOT)
        .close()
        .sweep(path_wire, transition='right')
    )
    upper_shell = upper_shell.union(swept_body, tol=0.1)

# Gap arc sweeps: outer channel between pockets (from one divider to the next)
GAP_ARCS = [
    (HALF_CRADLE, 180.0 - HALF_CRADLE),          # +45.35° to +134.65°
    (180.0 + HALF_CRADLE, 360.0 - HALF_CRADLE),  # +225.35° to +314.65°
]

for arc_start_deg, arc_end_deg in GAP_ARCS:
    a_start = math.radians(arc_start_deg)
    a_end = math.radians(arc_end_deg)
    a_mid = math.radians((arc_start_deg + arc_end_deg) / 2)

    g_start = (R_PATH_OUTER * math.cos(a_start), R_PATH_OUTER * math.sin(a_start))
    g_mid = (R_PATH_OUTER * math.cos(a_mid), R_PATH_OUTER * math.sin(a_mid))
    g_end = (R_PATH_OUTER * math.cos(a_end), R_PATH_OUTER * math.sin(a_end))

    gap_path = (
        cq.Workplane("XY")
        .moveTo(*g_start)
        .threePointArc(g_mid, g_end)
        .wire().val()
    )

    # Profile plane: CCW tangent at start angle, xDir radially inward
    gap_profile_plane = cq.Plane(
        origin=(g_start[0], g_start[1], 0),
        xDir=(-math.cos(a_start), -math.sin(a_start), 0),
        normal=(-math.sin(a_start), math.cos(a_start), 0),
    )

    gap_body = (
        cq.Workplane(gap_profile_plane)
        .moveTo(-RC_RIDGE_HALF, Z_BOT)
        .lineTo(-RC_RIDGE_HALF, Z_SPLIT)
        .lineTo(-WALL / 2, Z_CHAMFER_TOP)
        .lineTo(-WALL / 2, IC_OL_TOP)
        .lineTo(WALL / 2, IC_OL_TOP)
        .lineTo(WALL / 2, Z_CHAMFER_TOP)
        .lineTo(RC_RIDGE_HALF, Z_SPLIT)
        .lineTo(RC_RIDGE_HALF, Z_BOT)
        .close()
        .sweep(gap_path)
    )
    upper_shell = upper_shell.union(gap_body, tol=0.1)

us_solids = upper_shell.solids().vals()
print(f"After + all channel bodies: {len(us_solids)} solid(s)")


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
        # Inner end: tiny overlap into inner wall for boolean union,
        # but NOT the full OVERLAP (1mm) that extended to SHELL_IR.
        .moveTo(SHELL_OR - OVERLAP, Z_CHAMFER_TOP)
        .lineTo(SHELL_OR - 0.1, SHELL_HEIGHT)
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
        .lineTo(SHELL_OR - OVERLAP, Z_CHAMFER_TOP)
        .close()
        .extrude(WALL / 2, both=True)
    )
    div = div.rotate((0, 0, 0), (0, 0, 1), angle)
    upper_shell = upper_shell.union(div, tol=0.1)

us_solids = upper_shell.solids().vals()
print(f"After + dividers: {len(us_solids)} solid(s)")


# ═══════════════════════════════════════════════════════
# UPPER SHELL — Groove cuts (closed-loop sweep, after dividers)
# ═══════════════════════════════════════════════════════

for cradle_center in [0.0, 180.0]:
    a_lo = math.radians(cradle_center - HALF_CRADLE)
    a_hi = math.radians(cradle_center + HALF_CRADLE)
    a_mid = math.radians(cradle_center)

    # Same closed-loop path as the body sweep
    pA = (R_PATH_OUTER * math.cos(a_hi), R_PATH_OUTER * math.sin(a_hi))
    pB = (R_PATH_OUTER * math.cos(a_mid), R_PATH_OUTER * math.sin(a_mid))
    pC = (R_PATH_OUTER * math.cos(a_lo), R_PATH_OUTER * math.sin(a_lo))
    pD = (R_PATH_INNER * math.cos(a_lo), R_PATH_INNER * math.sin(a_lo))
    pE = (R_PATH_INNER * math.cos(a_mid), R_PATH_INNER * math.sin(a_mid))
    pF = (R_PATH_INNER * math.cos(a_hi), R_PATH_INNER * math.sin(a_hi))

    path_wire = (
        cq.Workplane("XY")
        .moveTo(*pA)
        .threePointArc(pB, pC)
        .lineTo(*pD)
        .threePointArc(pE, pF)
        .lineTo(*pA)
        .wire().val()
    )

    profile_plane = cq.Plane(
        origin=(pA[0], pA[1], 0),
        xDir=(math.cos(a_hi), math.sin(a_hi), 0),
        normal=(math.sin(a_hi), -math.cos(a_hi), 0),
    )

    swept_groove = (
        cq.Workplane(profile_plane)
        .moveTo(-RC_GAP_HALF, Z_BOT - 0.1)
        .lineTo(-RC_GAP_HALF, Z_SPLIT)
        .lineTo(0, RC_PEAK_Z)
        .lineTo(RC_GAP_HALF, Z_SPLIT)
        .lineTo(RC_GAP_HALF, Z_BOT - 0.1)
        .close()
        .sweep(path_wire, transition='right')
    )
    upper_shell = upper_shell.cut(swept_groove)

# Gap arc groove cuts
for arc_start_deg, arc_end_deg in GAP_ARCS:
    a_start = math.radians(arc_start_deg)
    a_end = math.radians(arc_end_deg)
    a_mid = math.radians((arc_start_deg + arc_end_deg) / 2)

    g_start = (R_PATH_OUTER * math.cos(a_start), R_PATH_OUTER * math.sin(a_start))
    g_mid = (R_PATH_OUTER * math.cos(a_mid), R_PATH_OUTER * math.sin(a_mid))
    g_end = (R_PATH_OUTER * math.cos(a_end), R_PATH_OUTER * math.sin(a_end))

    gap_path = (
        cq.Workplane("XY")
        .moveTo(*g_start)
        .threePointArc(g_mid, g_end)
        .wire().val()
    )

    gap_groove_plane = cq.Plane(
        origin=(g_start[0], g_start[1], 0),
        xDir=(-math.cos(a_start), -math.sin(a_start), 0),
        normal=(-math.sin(a_start), math.cos(a_start), 0),
    )

    gap_groove = (
        cq.Workplane(gap_groove_plane)
        .moveTo(-RC_GAP_HALF, Z_BOT - 0.1)
        .lineTo(-RC_GAP_HALF, Z_SPLIT)
        .lineTo(0, RC_PEAK_Z)
        .lineTo(RC_GAP_HALF, Z_SPLIT)
        .lineTo(RC_GAP_HALF, Z_BOT - 0.1)
        .close()
        .sweep(gap_path)
    )
    upper_shell = upper_shell.cut(gap_groove)

us_solids = upper_shell.solids().vals()
print(f"After + swept groove cuts: {len(us_solids)} solid(s)")


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
# DIAGNOSTICS (bounding boxes only — slab intersections are slow on swept geometry)
# ═══════════════════════════════════════════════════════

for name, part in [("Bottom cup", bottom_cup), ("Upper shell", upper_shell)]:
    solids = part.solids().vals()
    print(f"\n{name}: {len(solids)} solid(s)")
    for i, s in enumerate(solids):
        bb = s.BoundingBox()
        print(f"  Solid {i}: X[{bb.xmin:.1f},{bb.xmax:.1f}] "
              f"Y[{bb.ymin:.1f},{bb.ymax:.1f}] Z[{bb.zmin:.1f},{bb.zmax:.1f}]")

print(f"\nRadii:")
print(f"  Inner wall:  {SHELL_IR:.2f} - {SHELL_OR:.2f}")
print(f"  Path inner:  {R_PATH_INNER:.2f}")
print(f"  Path outer:  {R_PATH_OUTER:.2f}")
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
