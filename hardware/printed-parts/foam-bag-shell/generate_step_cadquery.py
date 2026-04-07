"""
Foam-bag shell: two concentric shells with integrated bag cradles.

Two concentric cylinders connected by a platform floor and 4 radial divider
walls. Below the platform is a foam cavity with its own bottom floor.

Built as one solid, split at PLAT_BOTTOM into two prints. The upper shell
gets a stacking channel (double ring + 45° chamfers) that straddles the
bottom cup's outer wall for alignment.

Bottom cup:  Z=0 to PLAT_BOTTOM  (prints upside-down)
Upper shell: Z=PLAT_BOTTOM-CHANNEL_DEPTH to SHELL_HEIGHT (channel extends below)
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

# Stacking channel dimensions
CHANNEL_DEPTH = 3.0                         # how far rings extend below split
CHANNEL_CLEARANCE = 0.5                     # per side (total gap = WALL + 2*0.5 = 2mm)

# Channel ring radii
R_INNER_OR = OUTER_SHELL_IR - CHANNEL_CLEARANCE   # inner ring outer face
R_INNER_IR = R_INNER_OR - WALL                      # inner ring inner face
R_OUTER_IR = OUTER_SHELL_OR + CHANNEL_CLEARANCE    # outer ring inner face
R_OUTER_OR = R_OUTER_IR + WALL                      # outer ring outer face

# Chamfer height: 45° from widest spread back to normal wall
# Inner side: R_INNER_IR → OUTER_SHELL_IR
# Outer side: R_OUTER_OR → OUTER_SHELL_OR
CHAMFER_H = WALL + CHANNEL_CLEARANCE               # 1.5 mm

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
DIVIDER_BOTTOM = PLAT_BOTTOM + FLOOR / 2
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

# Center ceiling hole
center_hole = (
    cq.Workplane("XY")
    .transformed(offset=(0, 0, PLAT_BOTTOM - 1))
    .circle(FOAM_HOLE_DIA / 2)
    .extrude(FLOOR + 2)
)
result = result.cut(center_hole)

# 4 wall holes — small diamonds (45° sides)
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
    result = result.cut(diamond)

# ── Step 4: Split into two prints at PLAT_BOTTOM ──
cut_above = (
    cq.Workplane("XY")
    .transformed(offset=(0, 0, PLAT_BOTTOM))
    .box(OUTER_SHELL_OR * 3, OUTER_SHELL_OR * 3, SHELL_HEIGHT,
         centered=(True, True, False), combine=False)
)
cut_below = (
    cq.Workplane("XY")
    .box(OUTER_SHELL_OR * 3, OUTER_SHELL_OR * 3, PLAT_BOTTOM,
         centered=(True, True, False), combine=False)
)

bottom_cup = result.cut(cut_above)
upper_shell = result.cut(cut_below)

# ── Step 5: Stacking channel on upper shell ──
# Two concentric rings extending below PLAT_BOTTOM, with 45° chamfers
# converging back to the normal outer wall above PLAT_BOTTOM.
#
# Cross-section (R horizontal, Z vertical):
#
#     OUTER_SHELL_IR ─────── OUTER_SHELL_OR          ← normal wall above chamfer
#           /                         \               ← 45° chamfers
#     R_INNER_IR─R_INNER_OR     R_OUTER_IR─R_OUTER_OR  ← rings at PLAT_BOTTOM
#          |         2mm gap        |
#     R_INNER_IR─R_INNER_OR     R_OUTER_IR─R_OUTER_OR  ← ring bottoms
#
# Profile traced as one closed polygon with the gap cut out:

Z_BOT = PLAT_BOTTOM - CHANNEL_DEPTH
Z_SPLIT = PLAT_BOTTOM
Z_CHAMFER_TOP = PLAT_BOTTOM + CHAMFER_H
Z_OVERLAP = Z_CHAMFER_TOP + 5  # extend into existing wall for clean union

channel = (
    cq.Workplane("XZ")
    # Inner ring inside face, going up
    .moveTo(R_INNER_IR, Z_BOT)
    .lineTo(R_INNER_IR, Z_SPLIT)
    # 45° chamfer: inner face angles outward to meet normal wall
    .lineTo(OUTER_SHELL_IR, Z_CHAMFER_TOP)
    # Up into existing wall (overlap zone for union)
    .lineTo(OUTER_SHELL_IR, Z_OVERLAP)
    .lineTo(OUTER_SHELL_OR, Z_OVERLAP)
    # Back down to chamfer top on outer side
    .lineTo(OUTER_SHELL_OR, Z_CHAMFER_TOP)
    # 45° chamfer: outer face angles outward to meet outer ring
    .lineTo(R_OUTER_OR, Z_SPLIT)
    # Down outer ring outside face
    .lineTo(R_OUTER_OR, Z_BOT)
    # Across outer ring bottom
    .lineTo(R_OUTER_IR, Z_BOT)
    # Up outer ring inside face (gap side)
    .lineTo(R_OUTER_IR, Z_SPLIT)
    # Across gap top
    .lineTo(R_INNER_OR, Z_SPLIT)
    # Down inner ring outside face (gap side)
    .lineTo(R_INNER_OR, Z_BOT)
    # Close back to start
    .close()
    .revolve(360, (0, 0, 0), (0, 1, 0))
)

channel_solids = channel.solids().vals()
print(f"\nChannel: {len(channel_solids)} solid(s)")

upper_shell = upper_shell.union(channel, tol=0.05)

# ── Step 6: Dividers in the channel/chamfer zone ──
# The regular dividers (Step 2) already connect inner wall to outer wall
# from Z=DIVIDER_BOTTOM to SHELL_HEIGHT. They reach to OUTER_SHELL_OR
# (103.85), which is inside the chamfered wall material at all heights.
# The channel rings below PLAT_BOTTOM are connected to the main wall
# through the 360° chamfer — no additional dividers needed there.
# The gap between rings must stay clear for the bottom cup to nest.
#
# No stub dividers needed. Removing the problematic ones from before.

# (stub dividers removed — the regular dividers handle the connection)

# ── Diagnostics: verify cross-section ──
print("\nUpper shell XZ profile check:")
cut_plane = (
    cq.Workplane("XY")
    .box(300, 0.01, 300, centered=(True, True, True))
    .translate((0, 0, 80))
)
try:
    section = upper_shell.intersect(cut_plane)
    verts = section.vertices().vals()
    coords = sorted(set((round(v.X, 1), round(v.Z, 1)) for v in verts))
    for x, z in coords:
        if x > 0:  # just show positive X side
            print(f"  R={x:6.1f}  Z={z:5.1f}")
except Exception as e:
    print(f"  Section failed: {e}")

# ── Diagnostics ──
for name, part in [("Bottom cup", bottom_cup), ("Upper shell", upper_shell)]:
    solids = part.solids().vals()
    print(f"\n{name}: {len(solids)} solid(s)")
    for i, s in enumerate(solids):
        sbb = s.BoundingBox()
        print(f"  Solid {i}: X[{sbb.xmin:.1f},{sbb.xmax:.1f}] "
              f"Y[{sbb.ymin:.1f},{sbb.ymax:.1f}] Z[{sbb.zmin:.1f},{sbb.zmax:.1f}]")

print(f"\nZ levels:")
print(f"  Z={Z_BOT:.1f}:       channel ring bottoms")
print(f"  Z=0:           bottom floor bottom")
print(f"  Z={FLOOR:.1f}:         bottom floor top")
print(f"  Z={PLAT_BOTTOM:.1f}:        split line / channel ring tops")
print(f"  Z={Z_CHAMFER_TOP:.1f}:        chamfer tops (back to normal wall)")
print(f"  Z={PLATFORM_Z:.1f}:        platform top")
print(f"  Z={SHELL_HEIGHT:.1f}:       shell top (open)")

print(f"\nChannel radii:")
print(f"  Inner ring: IR={R_INNER_IR:.1f}  OR={R_INNER_OR:.1f}")
print(f"  Gap:        {R_INNER_OR:.1f} to {R_OUTER_IR:.1f}  ({R_OUTER_IR - R_INNER_OR:.1f}mm)")
print(f"  Outer ring: IR={R_OUTER_IR:.1f}  OR={R_OUTER_OR:.1f}")
print(f"  Normal wall: IR={OUTER_SHELL_IR:.1f}  OR={OUTER_SHELL_OR:.1f}")

# ── Export STEP files ──
out_dir = Path(__file__).resolve().parent

bottom_path = out_dir / "foam-bag-shell-bottom.step"
cq.exporters.export(bottom_cup, str(bottom_path))
print(f"\nExported: {bottom_path}")

upper_path = out_dir / "foam-bag-shell-upper.step"
cq.exporters.export(upper_shell, str(upper_path))
print(f"Exported: {upper_path}")
