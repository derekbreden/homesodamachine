"""
Foam-bag shell: two concentric shells with integrated bag cradles.

Two concentric cylinders connected by a platform floor and 4 radial divider
walls. Below the platform is a foam cavity with its own bottom floor.

Bottom-up stack:
  Z=0 to FLOOR:                Bottom floor (solid disc)
  Z=FLOOR to FLOOR+FOAM_GAP:   Foam cavity (contained by outer wall)
  Z=PLAT_BOTTOM to PLATFORM_Z: Platform floor (solid disc, things rest here)
  Z=PLATFORM_Z to SHELL_HEIGHT: Main structure (inner wall, gap, outer wall)

Build strategy: single profile revolved 360° with a foam void traced into it.
Divider walls added as flat slabs with overlap. No vent holes.
"""

import math
import cadquery as cq
from pathlib import Path

# ── Dimensions ──

COLD_CORE_OR = 127.0 / 2 + 6.0 + 1.0   # ~70.5 mm
INNER_FOAM_GAP = 6.35                     # 1/4"
WALL = 1.0
FLOOR = 1.0
FLOOR_FOAM_GAP = 12.7                      # 1/2" foam layer at the bottom

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
PLAT_BOTTOM = FLOOR + FLOOR_FOAM_GAP       # ~7.35 mm
PLATFORM_Z = PLAT_BOTTOM + FLOOR           # ~8.35 mm

# ── Step 1: Profile revolved 360° ──
# Cross-section (X=radial, Y=height in XZ workplane):
#
#       Inner wall              Outer wall
#       IR====OR                OIR====OOR
#       |      |                |          |
#       |      |   bag space    |          |
#       |      |                |          |
# 0=====IR    OR================OIR        |   ← PLATFORM_Z
# |            platform disc          |    |
# 0===================================OIR  |   ← PLAT_BOTTOM
#                                      |   |
#              foam cavity             |   |
#                                      |   |
# 0===================================OIR  |   ← FLOOR
# |           bottom floor disc             |
# 0=========================================OOR ← Z=0

shells = (
    cq.Workplane("XZ")
    # A: center, top of platform
    .moveTo(0, PLATFORM_Z)
    # B: out to inner wall inside face
    .lineTo(SHELL_IR, PLATFORM_Z)
    # C: up inner wall
    .lineTo(SHELL_IR, SHELL_HEIGHT)
    # D: across inner wall top
    .lineTo(SHELL_OR, SHELL_HEIGHT)
    # E: down inner wall outside
    .lineTo(SHELL_OR, PLATFORM_Z)
    # F: across platform top in gap
    .lineTo(OUTER_SHELL_IR, PLATFORM_Z)
    # G: up outer wall inside
    .lineTo(OUTER_SHELL_IR, SHELL_HEIGHT)
    # H: across outer wall top
    .lineTo(OUTER_SHELL_OR, SHELL_HEIGHT)
    # I: down outer wall outside all the way to Z=0
    .lineTo(OUTER_SHELL_OR, 0)
    # J: across bottom floor bottom to center
    .lineTo(0, 0)
    # K: up to bottom floor top at center
    .lineTo(0, FLOOR)
    # L: across bottom floor top to outer wall
    .lineTo(OUTER_SHELL_IR, FLOOR)
    # M: up foam zone inner wall to platform bottom
    .lineTo(OUTER_SHELL_IR, PLAT_BOTTOM)
    # N: across platform bottom to center
    .lineTo(0, PLAT_BOTTOM)
    # close: back up to A (0, PLATFORM_Z)
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
DIVIDER_BOTTOM = PLATFORM_Z / 2           # overlap into platform
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
FOAM_HOLE_DIA = 8.0  # bigger for easier foam injection

# Center ceiling hole — vertical through the platform floor at center.
# Offset 1mm from axis to avoid revolve-axis degeneracy at X=0,Y=0.
center_hole = (
    cq.Workplane("XY")
    .transformed(offset=(0, 0, PLAT_BOTTOM - 1))
    .circle(FOAM_HOLE_DIA / 2)
    .extrude(FLOOR + 2)
)
result = result.cut(center_hole)

# 4 wall holes — right triangles (45° rule for printability).
# 90° angle at top, two 45° base angles. Triangle lies in the wall plane
# with the base horizontal and the apex pointing up.
# Punched radially through the outer wall.
TRIANGLE_BASE = 10.0   # base width
TRIANGLE_HEIGHT = TRIANGLE_BASE / 2  # right isoceles: height = base/2
FOAM_MID_Z = FLOOR + FLOOR_FOAM_GAP / 2

for angle_deg in [0, 90, 180, 270]:
    # Build triangle in YZ plane: local X = global Y (tangential),
    # local Y = global Z (vertical), extrude along normal = global +X (radial).
    base_z = FOAM_MID_Z - TRIANGLE_HEIGHT / 3
    tri = (
        cq.Workplane("YZ")
        .transformed(offset=(0, 0, OUTER_SHELL_IR - 2))  # shift along +X to wall
        .moveTo(-TRIANGLE_BASE / 2, base_z)
        .lineTo(TRIANGLE_BASE / 2, base_z)
        .lineTo(0, base_z + TRIANGLE_HEIGHT)
        .close()
        .extrude(WALL + 4)
    )
    tri = tri.rotate((0, 0, 0), (0, 0, 1), angle_deg)
    result = result.cut(tri)

# ── Diagnostics ──
solids = result.solids().vals()
print(f"Final solid count: {len(solids)}")
for i, s in enumerate(solids):
    sbb = s.BoundingBox()
    print(f"  Solid {i}: X[{sbb.xmin:.1f},{sbb.xmax:.1f}] "
          f"Y[{sbb.ymin:.1f},{sbb.ymax:.1f}] Z[{sbb.zmin:.1f},{sbb.zmax:.1f}]")

print(f"\nZ levels:")
print(f"  Z=0:          bottom floor bottom")
print(f"  Z={FLOOR:.1f}:        bottom floor top")
print(f"  Z={PLAT_BOTTOM:.1f}:        platform bottom (foam cavity top)")
print(f"  Z={PLATFORM_Z:.1f}:        platform top (components rest here)")
print(f"  Z={SHELL_HEIGHT:.1f}:      shell top (open)")

print(f"\nDimensions:")
print(f"  Inner shell: IR={SHELL_IR:.1f}  OR={SHELL_OR:.1f}")
print(f"  Outer shell: IR={OUTER_SHELL_IR:.1f}  OR={OUTER_SHELL_OR:.1f}")
print(f"  Wall: {WALL:.1f}  Floor: {FLOOR:.1f}  Foam gap: {FLOOR_FOAM_GAP:.1f}")

# ── Export STEP ──
out_dir = Path(__file__).resolve().parent
step_path = out_dir / "foam-bag-shell.step"
cq.exporters.export(result, str(step_path))
print(f"\nExported: {step_path}")
