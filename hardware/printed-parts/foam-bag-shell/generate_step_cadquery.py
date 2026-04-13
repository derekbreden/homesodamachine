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

Z_BOT = PLAT_BOTTOM - CHANNEL_DEPTH                # 23.4 mm
Z_SPLIT = PLAT_BOTTOM                               # 26.4 mm
Z_CHAMFER_TOP = PLAT_BOTTOM + CHAMFER_H            # 27.9 mm

OVERLAP = 1.0   # boolean overlap for reliable unions


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

for angle_deg in [0, 90, 180, 270]:
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

bc_solids = bottom_cup.solids().vals()
print(f"Bottom cup: {len(bc_solids)} solid(s)")
for i, s in enumerate(bc_solids):
    bb = s.BoundingBox()
    print(f"  Solid {i}: X[{bb.xmin:.1f},{bb.xmax:.1f}] "
          f"Y[{bb.ymin:.1f},{bb.ymax:.1f}] Z[{bb.zmin:.1f},{bb.zmax:.1f}]")


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
# UPPER SHELL — Dividers
# ═══════════════════════════════════════════════════════

DIVIDER_ANGLES = [
    -HALF_CRADLE,
    HALF_CRADLE,
    180.0 - HALF_CRADLE,
    180.0 + HALF_CRADLE,
]

# Divider profile in the radial-Z plane (hexagon):
#
#   SHELL_HEIGHT ┌──────────────────────────┐ SHELL_HEIGHT
#                │                          │
#                │       divider slab       │
#                │                          │
#  Z_BOT+FLOOR/2├──────────┐               │
#                           │  ramp up 45°  │
#             SHELL_OR-OL   R_INNER_IR      │ Z_CHAMFER_TOP
#                                           │
#                              OUTER_SHELL_IR+OL
#
# Bottom is flat from inner wall to R_INNER_IR (sitting on the floor),
# then ramps up at ~45° to Z_CHAMFER_TOP at OUTER_SHELL_IR (following
# the chamfer slope so nothing protrudes into the groove).

DIVIDER_FLOOR = Z_BOT + FLOOR / 2   # embed into actual floor

# Divider profile (hexagon):
#   Top:    flat from SHELL_OR to OUTER_SHELL_IR at SHELL_HEIGHT
#   Bottom: flat from SHELL_OR to R_INNER_IR at DIVIDER_FLOOR (on the floor),
#           then ramp following the chamfer from (R_INNER_IR, Z_SPLIT)
#           to (OUTER_SHELL_IR, Z_CHAMFER_TOP) — exactly 45°

for angle in DIVIDER_ANGLES:
    div = (
        cq.Workplane("XZ")
        .moveTo(SHELL_OR - OVERLAP, DIVIDER_FLOOR)
        .lineTo(SHELL_OR - OVERLAP, SHELL_HEIGHT)
        .lineTo(OUTER_SHELL_IR + OVERLAP, SHELL_HEIGHT)
        .lineTo(OUTER_SHELL_IR + OVERLAP, Z_CHAMFER_TOP)
        .lineTo(R_INNER_IR, Z_SPLIT)
        .lineTo(R_INNER_IR, DIVIDER_FLOOR)
        .close()
        .extrude(WALL / 2, both=True)
    )
    div = div.rotate((0, 0, 0), (0, 0, 1), angle)
    upper_shell = upper_shell.union(div, tol=0.05)

us_solids = upper_shell.solids().vals()
print(f"After + dividers: {len(us_solids)} solid(s)")

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

for cradle_center in [0.0, 180.0]:
    # Annular wedge: revolve a rectangle through the cradle arc
    cradle_cut = (
        cq.Workplane("XZ")
        .moveTo(SHELL_OR + 0.1, Z_BOT - 0.1)
        .lineTo(SHELL_OR + 0.1, Z_BOT + FLOOR + 0.1)
        .lineTo(R_INNER_IR - 0.1, Z_BOT + FLOOR + 0.1)
        .lineTo(R_INNER_IR - 0.1, Z_BOT - 0.1)
        .close()
        .revolve(CRADLE_ARC_DEG, (0, 0, 0), (0, 1, 0))
    )
    cradle_cut = cradle_cut.rotate(
        (0, 0, 0), (0, 0, 1), cradle_center - HALF_CRADLE
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

# Cross-section through first divider angle to see divider profile
DIV_ANGLE_RAD = math.radians(DIVIDER_ANGLES[0])
slab_div = (
    cq.Workplane("XY")
    .box(300, 0.02, 300, centered=(True, True, True))
    .translate((0, 0, 80))
    .rotate((0, 0, 0), (0, 0, 1), DIVIDER_ANGLES[0])
)
print(f"\n── CROSS-SECTION through divider at {DIVIDER_ANGLES[0]:.1f}° (Z < 35) ──")
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
