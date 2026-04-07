"""
Foam-bag shell: two concentric shells with integrated bag cradles.

Two concentric cylinders connected by a platform floor and 4 radial divider
walls. Below the platform is a foam cavity with its own bottom floor.

Bottom-up stack:
  Z=0 to FLOOR:                Bottom floor (solid disc)
  Z=FLOOR to FLOOR+FOAM_GAP:   Foam cavity (contained by outer wall)
  Z=PLAT_BOTTOM to PLATFORM_Z: Platform floor (solid disc, things rest here)
  Z=PLATFORM_Z to SHELL_HEIGHT: Main structure (inner wall, gap, outer wall)

Built as one solid, then split at PLATFORM_Z into two prints:
  - Bottom cup:  Z=0 to PLATFORM_Z (prints upside-down, no overhangs)
  - Upper shell: Z=PLATFORM_Z to SHELL_HEIGHT (open top and bottom, no overhangs)
"""

import math
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
SHELL_HEIGHT = TANK_HEIGHT + 10.0          # 162.4 mm

CRADLE_DEPTH = 25.0
CRADLE_ARC_DEG = 105.0

OUTER_SHELL_IR = SHELL_OR + CRADLE_DEPTH   # ~102.85 mm
OUTER_SHELL_OR = OUTER_SHELL_IR + WALL     # ~103.85 mm

HALF_CRADLE = CRADLE_ARC_DEG / 2

# Derived Z levels
PLAT_BOTTOM = FLOOR + FLOOR_FOAM_GAP       # ~26.4 mm
PLATFORM_Z = PLAT_BOTTOM + FLOOR           # ~27.4 mm

# ── Step 1: Profile revolved 360° ──
shells = (
    cq.Workplane("XZ")
    .moveTo(0, PLATFORM_Z)
    .lineTo(SHELL_IR, PLATFORM_Z)
    .lineTo(SHELL_IR, SHELL_HEIGHT)
    .lineTo(SHELL_OR, SHELL_HEIGHT)
    .lineTo(SHELL_OR, PLATFORM_Z)
    .lineTo(OUTER_SHELL_IR, PLATFORM_Z)
    .lineTo(OUTER_SHELL_IR, SHELL_HEIGHT)
    .lineTo(OUTER_SHELL_OR, SHELL_HEIGHT)
    .lineTo(OUTER_SHELL_OR, 0)
    .lineTo(0, 0)
    .lineTo(0, FLOOR)
    .lineTo(OUTER_SHELL_IR, FLOOR)
    .lineTo(OUTER_SHELL_IR, PLAT_BOTTOM)
    .lineTo(0, PLAT_BOTTOM)
    .close()
    .revolve(360, (0, 0, 0), (0, 1, 0))
)

solids = shells.solids().vals()
print(f"After revolve: {len(solids)} solid(s)")

# ── Step 2: Divider walls (flat slabs, constant thickness) ──
DIVIDER_ANGLES = [
    -HALF_CRADLE,
    HALF_CRADLE,
    180.0 - HALF_CRADLE,
    180.0 + HALF_CRADLE,
]

OVERLAP = 1.0
DIVIDER_BOTTOM = PLAT_BOTTOM + FLOOR / 2   # overlap into platform floor
DIVIDER_HEIGHT = SHELL_HEIGHT - DIVIDER_BOTTOM
DIVIDER_RADIAL_SPAN = (OUTER_SHELL_IR + OVERLAP) - (SHELL_OR - OVERLAP)

result = shells
for angle in DIVIDER_ANGLES:
    div = (
        cq.Workplane("XY")
        .transformed(offset=(
            (SHELL_OR - OVERLAP + OUTER_SHELL_IR + OVERLAP) / 2,
            0,
            DIVIDER_BOTTOM + DIVIDER_HEIGHT / 2,
        ))
        .box(DIVIDER_RADIAL_SPAN, WALL, DIVIDER_HEIGHT, centered=True, combine=False)
    )
    div = div.rotate((0, 0, 0), (0, 0, 1), angle)
    result = result.union(div, tol=0.05)

# ── Step 3: Foam cavity holes ──
FOAM_HOLE_DIA = 8.0

# Center ceiling hole — vertical through the platform floor at center
center_hole = (
    cq.Workplane("XY")
    .transformed(offset=(0, 0, PLAT_BOTTOM - 1))
    .circle(FOAM_HOLE_DIA / 2)
    .extrude(FLOOR + 2)
)
result = result.cut(center_hole)

# 4 wall holes — small diamonds (45° sides) through the outer wall
DIAMOND_SIZE = 10.0  # height and width (45° on all sides)
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
    result = result.cut(diamond)

# ── Step 4: Split into two prints at PLATFORM_Z ──
# Cutting box above PLATFORM_Z (keeps bottom cup)
cut_above = (
    cq.Workplane("XY")
    .transformed(offset=(0, 0, PLAT_BOTTOM))
    .box(OUTER_SHELL_OR * 3, OUTER_SHELL_OR * 3, SHELL_HEIGHT, centered=(True, True, False), combine=False)
)

# Cutting box below PLAT_BOTTOM (keeps upper shell — includes platform floor)
cut_below = (
    cq.Workplane("XY")
    .box(OUTER_SHELL_OR * 3, OUTER_SHELL_OR * 3, PLAT_BOTTOM, centered=(True, True, False), combine=False)
)

bottom_cup = result.cut(cut_above)
upper_shell = result.cut(cut_below)

# ── Diagnostics ──
for name, part in [("Bottom cup", bottom_cup), ("Upper shell", upper_shell)]:
    solids = part.solids().vals()
    print(f"\n{name}: {len(solids)} solid(s)")
    for i, s in enumerate(solids):
        sbb = s.BoundingBox()
        print(f"  Solid {i}: X[{sbb.xmin:.1f},{sbb.xmax:.1f}] "
              f"Y[{sbb.ymin:.1f},{sbb.ymax:.1f}] Z[{sbb.zmin:.1f},{sbb.zmax:.1f}]")

print(f"\nZ levels:")
print(f"  Z=0:          bottom floor bottom")
print(f"  Z={FLOOR:.1f}:        bottom floor top")
print(f"  Z={PLAT_BOTTOM:.1f}:       platform bottom (foam cavity top)")
print(f"  Z={PLATFORM_Z:.1f}:       platform top — SPLIT LINE")
print(f"  Z={SHELL_HEIGHT:.1f}:      shell top (open)")

# ── Export STEP files ──
out_dir = Path(__file__).resolve().parent

bottom_path = out_dir / "foam-bag-shell-bottom.step"
cq.exporters.export(bottom_cup, str(bottom_path))
print(f"\nExported: {bottom_path}")

upper_path = out_dir / "foam-bag-shell-upper.step"
cq.exporters.export(upper_shell, str(upper_path))
print(f"Exported: {upper_path}")
