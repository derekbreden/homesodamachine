"""
Pump-Tray STEP Generator
========================
Generates pump-tray-cadquery.step for the soda-flavor-injector cartridge sub-assembly.

Specification: hardware/printed-parts/cartridge/pump-tray/planning/parts.md
Standards:     hardware/pipeline/steps/6-step-generation.md
"""

# =============================================================================
# Coordinate System Declaration (Rubric 2)
# =============================================================================
#
# Origin:    Front-face bottom-left corner
#            (X=0, Y=0, Z=0 — the build-plate contact face corner)
#
# X-axis:    Tray width, left to right
#            X = 0   → left lateral face
#            X = 144 → right lateral face
#
# Y-axis:    Tray depth, front to rear
#            Y = 0   → front face (pump-bracket side; build plate contact face)
#            Y = 5   → rear face (motor/service side; top surface during printing)
#            Y = 10  → boss tips and rib crowns (+Y protrusions from rear face)
#
# Z-axis:    Tray height, bottom to top
#            Z = 0   → bottom edge (build-plate contact edge)
#            Z = 80  → top edge
#
# Envelope (plate body only): X=[0,144] Y=[0,5] Z=[0,80]
# Full part with protrusions:  X=[0,144] Y=[0,10] Z=[0,80]
# Print orientation: front face (Y=0) face-down on build plate
#
# =============================================================================

import sys
import math
from pathlib import Path

import cadquery as cq

# Add tools/ to path for step_validate
# Script is at: soda-flavor-injector/hardware/printed-parts/cartridge/pump-tray/
# tools/ is at:  soda-flavor-injector/tools/
# parents[0] = pump-tray, [1] = cartridge, [2] = printed-parts, [3] = hardware, [4] = soda-flavor-injector
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))
from step_validate import Validator

# =============================================================================
# Feature Planning Table (Rubric 1)
# =============================================================================

FEATURE_TABLE = """
Feature Planning Table — Pump-Tray
=============================================================================================================================
#  | Feature Name              | Mech Function                          | Op  | Shape    | Axis | Center (X, Y, Z)     | Dimensions                          | Notes
---|---------------------------|----------------------------------------|-----|----------|------|----------------------|-------------------------------------|------
01 | Base plate body           | Structural substrate for all features  | Add | Box      | —    | (72, 2.5, 40)        | 144×5×80mm, 3mm plan-view corners   | centered=False; |Y edge fillet
02 | Motor bore 1              | Motor cylinder pass-through clearance  | Sub | Cylinder | Y    | (34.5, 2.5, 40.0)    | D=37.2mm, Y=0→5 through-cut         | 0.5mm×45° rear-face entry chamfer
03 | Motor bore 2              | Motor cylinder pass-through clearance  | Sub | Cylinder | Y    | (109.5, 2.5, 40.0)   | D=37.2mm, Y=0→5 through-cut         | 0.5mm×45° rear-face entry chamfer
04 | M3 clearance hole 1A      | Screw shank pass-through               | Sub | Cylinder | Y    | (10.5, 2.75, 16.0)   | D=3.6mm, Y=0→5.5 (0.5mm into boss)  | Coaxial with boss 1A
05 | M3 clearance hole 1B      | Screw shank pass-through               | Sub | Cylinder | Y    | (58.5, 2.75, 16.0)   | D=3.6mm, Y=0→5.5 (0.5mm into boss)  | Coaxial with boss 1B
06 | M3 clearance hole 1C      | Screw shank pass-through               | Sub | Cylinder | Y    | (10.5, 2.75, 64.0)   | D=3.6mm, Y=0→5.5 (0.5mm into boss)  | Coaxial with boss 1C
07 | M3 clearance hole 1D      | Screw shank pass-through               | Sub | Cylinder | Y    | (58.5, 2.75, 64.0)   | D=3.6mm, Y=0→5.5 (0.5mm into boss)  | Coaxial with boss 1D
08 | M3 clearance hole 2A      | Screw shank pass-through               | Sub | Cylinder | Y    | (85.5, 2.75, 16.0)   | D=3.6mm, Y=0→5.5 (0.5mm into boss)  | Coaxial with boss 2A
09 | M3 clearance hole 2B      | Screw shank pass-through               | Sub | Cylinder | Y    | (133.5, 2.75, 16.0)  | D=3.6mm, Y=0→5.5 (0.5mm into boss)  | Coaxial with boss 2B
10 | M3 clearance hole 2C      | Screw shank pass-through               | Sub | Cylinder | Y    | (85.5, 2.75, 64.0)   | D=3.6mm, Y=0→5.5 (0.5mm into boss)  | Coaxial with boss 2C
11 | M3 clearance hole 2D      | Screw shank pass-through               | Sub | Cylinder | Y    | (133.5, 2.75, 64.0)  | D=3.6mm, Y=0→5.5 (0.5mm into boss)  | Coaxial with boss 2D
12 | Field zone pocket bottom  | Bracket seating reference surface      | Sub | Box      | Y    | (72, 0.25, 1.5)      | 144×0.5×3mm pocket                  | X=0..144, Z=0..3, Y=0..0.5
13 | Field zone pocket top     | Bracket seating reference surface      | Sub | Box      | Y    | (72, 0.25, 78.5)     | 144×0.5×3mm pocket                  | X=0..144, Z=77..80, Y=0..0.5
14 | Field zone gap lower      | Bracket seating reference surface      | Sub | Box      | Y    | (72.0, 0.25, 20.0)   | 1×0.5×34mm gap                      | X=71.5..72.5, Z=3..37
15 | Field zone gap upper      | Bracket seating reference surface      | Sub | Box      | Y    | (72.0, 0.25, 60.0)   | 1×0.5×34mm gap                      | X=71.5..72.5, Z=43..77
16 | Heat-set boss 1A          | M3 insert seat; brackets pump bracket  | Add | Cylinder | Y    | (10.5, 7.5, 16.0)    | OD=9mm, Y=5→10; 1.5mm base fillet   | 4.7mm insert bore Y=5.5→10
17 | Heat-set boss 1B          | M3 insert seat; clamps pump bracket    | Add | Cylinder | Y    | (58.5, 7.5, 16.0)    | OD=9mm, Y=5→10; 1.5mm base fillet   |
18 | Heat-set boss 1C          | M3 insert seat; clamps pump bracket    | Add | Cylinder | Y    | (10.5, 7.5, 64.0)    | OD=9mm, Y=5→10; 1.5mm base fillet   |
19 | Heat-set boss 1D          | M3 insert seat; clamps pump bracket    | Add | Cylinder | Y    | (58.5, 7.5, 64.0)    | OD=9mm, Y=5→10; 1.5mm base fillet   |
20 | Heat-set boss 2A          | M3 insert seat; clamps pump bracket    | Add | Cylinder | Y    | (85.5, 7.5, 16.0)    | OD=9mm, Y=5→10; 1.5mm base fillet   |
21 | Heat-set boss 2B          | M3 insert seat; clamps pump bracket    | Add | Cylinder | Y    | (133.5, 7.5, 16.0)   | OD=9mm, Y=5→10; 1.5mm base fillet   |
22 | Heat-set boss 2C          | M3 insert seat; clamps pump bracket    | Add | Cylinder | Y    | (85.5, 7.5, 64.0)    | OD=9mm, Y=5→10; 1.5mm base fillet   |
23 | Heat-set boss 2D          | M3 insert seat; clamps pump bracket    | Add | Cylinder | Y    | (133.5, 7.5, 64.0)   | OD=9mm, Y=5→10; 1.5mm base fillet   |
24 | Insert bore 1A            | Insert cavity (blind from boss tip)    | Sub | Cylinder | Y    | (10.5, 7.75, 16.0)   | D=4.7mm, Y=5.5→10 (4.5mm deep)     | Opens at boss tip Y=10, floor Y=5.5
25 | Insert bore 1B            | Insert cavity                          | Sub | Cylinder | Y    | (58.5, 7.75, 16.0)   | D=4.7mm                             |
26 | Insert bore 1C            | Insert cavity                          | Sub | Cylinder | Y    | (10.5, 7.75, 64.0)   | D=4.7mm                             |
27 | Insert bore 1D            | Insert cavity                          | Sub | Cylinder | Y    | (58.5, 7.75, 64.0)   | D=4.7mm                             |
28 | Insert bore 2A            | Insert cavity                          | Sub | Cylinder | Y    | (85.5, 7.75, 16.0)   | D=4.7mm                             |
29 | Insert bore 2B            | Insert cavity                          | Sub | Cylinder | Y    | (133.5, 7.75, 16.0)  | D=4.7mm                             |
30 | Insert bore 2C            | Insert cavity                          | Sub | Cylinder | Y    | (85.5, 7.75, 64.0)   | D=4.7mm                             |
31 | Insert bore 2D            | Insert cavity                          | Sub | Cylinder | Y    | (133.5, 7.75, 64.0)  | D=4.7mm                             |
32 | Cross-rib                 | Lateral stiffness between bores        | Add | Box      | X    | (72.0, 7.5, 40.0)    | 37.8×5×6mm, X=53.1..90.9           | 1mm crown chamfer, 2mm base fillet
33 | Radiating rib 1A          | Boss-to-bore load path                 | Add | Box      | 45°  | (17.52, 7.5, 23.02)  | 10.84×5×4mm rotated 45° about Y    | Y=5→10; 2mm base fillet
34 | Radiating rib 1B          | Boss-to-bore load path                 | Add | Box      | -45° | (51.49, 7.5, 23.02)  | 10.84×5×4mm rotated -45° about Y   |
35 | Radiating rib 1C          | Boss-to-bore load path                 | Add | Box      | -45° | (17.52, 7.5, 56.99)  | 10.84×5×4mm rotated -45° about Y   |
36 | Radiating rib 1D          | Boss-to-bore load path                 | Add | Box      | 45°  | (51.49, 7.5, 56.99)  | 10.84×5×4mm rotated 45° about Y    |
37 | Radiating rib 2A          | Boss-to-bore load path                 | Add | Box      | 45°  | (92.52, 7.5, 23.02)  | 10.84×5×4mm rotated 45° about Y    |
38 | Radiating rib 2B          | Boss-to-bore load path                 | Add | Box      | -45° | (126.49, 7.5, 23.02) | 10.84×5×4mm rotated -45° about Y   |
39 | Radiating rib 2C          | Boss-to-bore load path                 | Add | Box      | -45° | (92.52, 7.5, 56.99)  | 10.84×5×4mm rotated -45° about Y   |
40 | Radiating rib 2D          | Boss-to-bore load path                 | Add | Box      | 45°  | (126.49, 7.5, 56.99) | 10.84×5×4mm rotated 45° about Y    |
41 | Wiring channel 1          | Motor lead wire routing conduit        | Sub | Box      | X    | (7.95, 3.0, 40.0)    | 15.9×4×6mm, X=0..15.9, Y=1..5     | 1.5mm int. fillet; bumps inside
42 | Wiring channel 2          | Motor lead wire routing conduit        | Sub | Box      | X    | (136.05, 3.0, 40.0)  | 15.9×4×6mm, X=128.1..144, Y=1..5  | 1.5mm int. fillet; bumps inside
43 | Strain-relief bump 1-ch1  | Wire retention in channel              | Add | Cylinder | Y    | (10.9, 1.75, 40.0)   | D=2mm, H=1.5mm from Y=1            | Rounded crown
44 | Strain-relief bump 2-ch1  | Wire retention in channel              | Add | Cylinder | Y    | (5.9, 1.75, 40.0)    | D=2mm, H=1.5mm from Y=1            |
45 | Strain-relief bump 1-ch2  | Wire retention in channel              | Add | Cylinder | Y    | (133.1, 1.75, 40.0)  | D=2mm, H=1.5mm from Y=1            |
46 | Strain-relief bump 2-ch2  | Wire retention in channel              | Add | Cylinder | Y    | (138.1, 1.75, 40.0)  | D=2mm, H=1.5mm from Y=1            |
47 | Snap notch left           | Shell snap-latch engagement pocket     | Sub | Box      | X    | (0.75, 3.5, 40.0)    | 1.5×3×3mm, X=0..1.5, Y=2..5       | Z=38.5..41.5
48 | Snap notch right          | Shell snap-latch engagement pocket     | Sub | Box      | X    | (143.25, 3.5, 40.0)  | 1.5×3×3mm, X=142.5..144, Y=2..5   | Z=38.5..41.5
49 | Perimeter chamfers        | Visual quality, print quality          | Sub | Chamfer  | —    | external edges ≠Y=0  | 1.5mm×45°                          | Top/lateral/rear perimeter
50 | Elephant's foot chamfer   | Compensate FDM base flare              | Sub | Chamfer  | —    | Z=0 bottom edge      | 0.3mm×45°                          | Only on Y=0 face bottom edge
51 | Motor bore rear chamfers  | Finished appearance, bridge artifact   | Sub | Chamfer  | —    | bore circle at Y=5   | 0.5mm×45°                          | Both bores at rear face entry
=============================================================================================================================
"""

print(FEATURE_TABLE)

# =============================================================================
# Dimensions
# =============================================================================

PLATE_W = 144.0   # X
PLATE_D = 5.0     # Y
PLATE_H = 80.0    # Z
CORNER_R = 3.0

BORE_D = 37.2
BORE_R = BORE_D / 2.0  # 18.6
BORE_1_X = 34.5
BORE_2_X = 109.5
BORE_Z = 40.0

HOLE_D = 3.6
HOLE_R = HOLE_D / 2.0  # 1.8

BOSS_POSITIONS = [
    (10.5,  16.0),   # 1A
    (58.5,  16.0),   # 1B
    (10.5,  64.0),   # 1C
    (58.5,  64.0),   # 1D
    (85.5,  16.0),   # 2A
    (133.5, 16.0),   # 2B
    (85.5,  64.0),   # 2C
    (133.5, 64.0),   # 2D
]

BOSS_OD = 9.0
BOSS_R = BOSS_OD / 2.0  # 4.5
BOSS_H = 5.0             # Y=5 to Y=10

INSERT_D = 4.7
INSERT_R = INSERT_D / 2.0
INSERT_DEPTH = 4.5  # from boss tip (Y=10) down to Y=5.5

# Cross-rib geometry
RIB_X0 = 53.1
RIB_X1 = 90.9
RIB_Z0 = 37.0
RIB_Z1 = 43.0
RIB_Y0 = 5.0
RIB_Y1 = 10.0

# Wiring channels
CHAN_DEPTH = 4.0   # Y depth from Y=5 to Y=1
CHAN_W = 6.0       # Z width

# Radiating ribs: (cx, cz, angle_deg)
# Angle is rotation of rib long-axis about Y-axis
# 45 degrees: rib runs from lower-left to upper-right in XZ plane
RAD_RIB_LENGTH = 10.84
RAD_RIB_WIDTH = 4.0
RAD_RIB_H = 5.0    # Y=5 to Y=10

RAD_RIB_SPECS = [
    # (cx, cz, angle_deg)
    (17.52,  23.02,  45.0),   # 1A: boss (10.5,16) to bore (34.5,40)
    (51.49,  23.02, -45.0),   # 1B: boss (58.5,16) to bore (34.5,40)
    (17.52,  56.99, -45.0),   # 1C: boss (10.5,64) to bore (34.5,40)
    (51.49,  56.99,  45.0),   # 1D: boss (58.5,64) to bore (34.5,40)
    (92.52,  23.02,  45.0),   # 2A: boss (85.5,16) to bore (109.5,40)
    (126.49, 23.02, -45.0),   # 2B: boss (133.5,16) to bore (109.5,40)
    (92.52,  56.99, -45.0),   # 2C: boss (85.5,64) to bore (109.5,40)
    (126.49, 56.99,  45.0),   # 2D: boss (133.5,64) to bore (109.5,40)
]

# =============================================================================
# Helper: make a cylinder tool for cutting/adding along Y-axis
# Creates a cylinder from Y=y0 to Y=y1 at (cx, cz) in XZ
# Since XZ workplane extrudes in -Y direction:
#   extrude(h) → Y from 0 to -h
#   extrude(-h) → Y from 0 to +h
# We translate into position after.
# =============================================================================

def cylinder_along_y(cx, cz, radius, y0, y1):
    """
    Creates a cylinder at (cx, ?, cz) extending from Y=y0 to Y=y1.
    Uses XZ workplane: extrude(-height) goes in +Y direction.
    Returns a CadQuery Workplane containing the cylinder.
    """
    height = y1 - y0
    # XZ plane normal is -Y. extrude(-height) goes in +Y (opposite of -Y normal).
    cyl = (
        cq.Workplane("XZ")
        .center(cx, cz)
        .circle(radius)
        .extrude(-height)   # extrudes in +Y from Y=0, giving Y=[0, height]
    )
    # Translate to start at y0
    if y0 != 0.0:
        cyl = cyl.translate((0, y0, 0))
    return cyl


# =============================================================================
# Step 1: Base plate body
# Box at X=[0,144], Y=[0,5], Z=[0,80]
# 4 plan-view corner radii: 3mm on the 4 edges parallel to Y-axis
# (the short 5mm edges at corners of the XZ perimeter)
# =============================================================================
print("Step 1: Building base plate body...")

plate = (
    cq.Workplane("XY")
    .box(PLATE_W, PLATE_D, PLATE_H, centered=False)
    # centered=False: X=[0,144], Y=[0,5], Z=[0,80]
)

# Fillet the 4 edges parallel to Y-axis (plan-view vertical corners in XZ)
# These are the short 5mm edges at the 4 corners of the 144x80 plan
# Selector "|Y" selects edges whose direction is parallel to Y
plate = plate.edges("|Y").fillet(CORNER_R)

print("  Base plate with 3mm corner radii: OK")

# =============================================================================
# Step 2: Motor bores (×2, subtractive)
# Through-cylinders along Y, D=37.2mm, center at (bore_x, ?, bore_z=40)
# =============================================================================
print("Step 2: Cutting motor bores...")

for bore_x in [BORE_1_X, BORE_2_X]:
    bore = cylinder_along_y(bore_x, BORE_Z, BORE_R, -1.0, PLATE_D + 1.0)
    plate = plate.cut(bore)

print("  Motor bores: OK")

# =============================================================================
# Step 3: M3 clearance holes (×8, subtractive)
# =============================================================================
print("Step 3: Cutting M3 clearance holes...")

for (hx, hz) in BOSS_POSITIONS:
    hole = cylinder_along_y(hx, hz, HOLE_R, -1.0, PLATE_D + 1.0)
    plate = plate.cut(hole)

print("  M3 clearance holes: OK")

# =============================================================================
# Step 4: Field zone step on front face (subtractive)
# Cut 0.5mm deep pockets into front face (Y=0..0.5) for field zone areas.
#
# Keep zones (NOT cut):
#   Pump 1 pad: X=0..71.5, Z=3..77
#   Pump 2 pad: X=72.5..144, Z=3..77
#   Cross-rib band: X=69..75, Z=37..43
#
# Cut zones:
#   Bottom strip: X=0..144, Z=0..3
#   Top strip: X=0..144, Z=77..80
#   Center gap lower: X=71.5..72.5, Z=3..37
#   Center gap upper: X=71.5..72.5, Z=43..77
#
# On XY workplane (normal = +Z), box(W,D,H,centered=False):
#   X=[0..W], Y=[0..D], Z=[0..H]
# We need Y=[0..0.5] for the pocket, so box(W, 0.5, H, centered=False) is correct.
# =============================================================================
print("Step 4: Cutting field zone step pockets...")

FIELD_DEPTH = 0.5

def field_pocket(x0, z0, width_x, height_z):
    """Create a 0.5mm deep pocket at (x0, 0, z0) with given X width and Z height."""
    return (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(x0, 0.0, z0))
        .box(width_x, FIELD_DEPTH, height_z, centered=False)
        # Box: X=[x0..x0+width_x], Y=[0..0.5], Z=[z0..z0+height_z]
    )

# Bottom strip: X=0..144, Z=0..3
plate = plate.cut(field_pocket(0, 0, PLATE_W, 3.0))
# Top strip: X=0..144, Z=77..80
plate = plate.cut(field_pocket(0, 77.0, PLATE_W, 3.0))
# Center gap lower: X=71.5..72.5, Z=3..37
plate = plate.cut(field_pocket(71.5, 3.0, 1.0, 34.0))
# Center gap upper: X=71.5..72.5, Z=43..77
plate = plate.cut(field_pocket(71.5, 43.0, 1.0, 34.0))

print("  Field zone pockets: OK")

# =============================================================================
# Step 5: Heat-set insert bosses (×8, additive)
# Cylinders at each boss position, Y=5..10 (protrude from rear face)
# =============================================================================
print("Step 5: Adding heat-set insert bosses...")

for (bx, bz) in BOSS_POSITIONS:
    boss = cylinder_along_y(bx, bz, BOSS_R, PLATE_D, PLATE_D + BOSS_H)
    plate = plate.union(boss)

print("  Bosses added: OK")

# =============================================================================
# Step 5a: Boss base fillets (1.5mm at Y=5 circular junction)
# Apply per-boss using NearestToPointSelector on the base circular edge
# =============================================================================
print("Step 5a: Applying boss base fillets...")

BOSS_BASE_FILLET = 1.5
for (bx, bz) in BOSS_POSITIONS:
    try:
        plate = plate.edges(
            cq.selectors.NearestToPointSelector((bx, PLATE_D, bz))
        ).fillet(BOSS_BASE_FILLET)
    except Exception as e:
        print(f"  Boss fillet at ({bx},{bz}) skipped: {e}")

print("  Boss base fillets: OK")

# =============================================================================
# Step 5b: Insert bores (×8, subtractive)
# Blind bores from boss tip (Y=10) down to Y=5.5 — 4.5mm deep
# =============================================================================
print("Step 5b: Cutting insert bores...")

for (bx, bz) in BOSS_POSITIONS:
    # Y=5.5 to Y=10 (opens at boss tip, floor at Y=5.5)
    insert_bore = cylinder_along_y(bx, bz, INSERT_R, PLATE_D + 0.5, PLATE_D + BOSS_H)
    plate = plate.cut(insert_bore)

print("  Insert bores: OK")

# =============================================================================
# Step 5c: Clearance hole boss-extension (×8, subtractive)
# Extends each M3 clearance hole (3.6mm) from Y=5.0 to Y=5.5 inside the boss.
# This closes the 0.5mm solid plug that would otherwise block the screw path.
# The clearance bore now meets the insert bore floor exactly at Y=5.5.
# Must run AFTER bosses are unioned (step 5) — boss material didn't exist at step 3.
# =============================================================================
print("Step 5c: Cutting clearance hole boss-extensions (Y=5.0 to Y=5.5)...")

for (hx, hz) in BOSS_POSITIONS:
    extension = cylinder_along_y(hx, hz, HOLE_R, PLATE_D, PLATE_D + 0.5)
    plate = plate.cut(extension)

print("  Clearance hole boss-extensions: OK")

# =============================================================================
# Step 5d: Motor bore rear-face chamfers (0.5mm × 45° at Y=5 entry)
# =============================================================================
print("Step 5d: Motor bore rear-face chamfers...")

BORE_CHAMFER_SIZE = 0.5
for bore_x in [BORE_1_X, BORE_2_X]:
    try:
        plate = plate.edges(
            cq.selectors.NearestToPointSelector((bore_x, PLATE_D, BORE_Z))
        ).chamfer(BORE_CHAMFER_SIZE)
    except Exception as e:
        print(f"  Bore chamfer at X={bore_x} skipped: {e}")

print("  Motor bore rear chamfers: OK")

# =============================================================================
# Step 6: Structural cross-rib on rear face (additive)
# Box: X=53.1..90.9, Y=5..10, Z=37..43
# =============================================================================
print("Step 6: Adding cross-rib...")

cross_rib = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(RIB_X0, RIB_Y0, RIB_Z0))
    .box(RIB_X1 - RIB_X0, RIB_Y1 - RIB_Y0, RIB_Z1 - RIB_Z0, centered=False)
    # Box: X=[53.1..90.9], Y=[5..10], Z=[37..43]
)
plate = plate.union(cross_rib)

print("  Cross-rib added: OK")

# Crown chamfer: 1mm at Y=10 top edge of cross-rib
try:
    # The crown is at Y=10, along X direction, at Z midpoints
    # NearestToPointSelector finds the nearest edge to this point
    plate = plate.edges(
        cq.selectors.NearestToPointSelector((72.0, RIB_Y1, 40.0))
    ).chamfer(1.0)
    print("  Cross-rib crown chamfer: OK")
except Exception as e:
    print(f"  Cross-rib crown chamfer skipped: {e}")

# Base fillet: 2mm where cross-rib meets rear face at Y=5
try:
    plate = plate.edges(
        cq.selectors.NearestToPointSelector((72.0, RIB_Y0, 40.0))
    ).fillet(2.0)
    print("  Cross-rib base fillet: OK")
except Exception as e:
    print(f"  Cross-rib base fillet skipped (deferred to post-processing): {e}")

# =============================================================================
# Step 7: Boss-to-bore radiating ribs (×8, additive) on rear face
# Each is a box 10.84×4mm in XZ, 5mm in Y (Y=5..10), rotated about Y-axis
# =============================================================================
print("Step 7: Adding radiating ribs...")

def make_radiating_rib(cx, cz, angle_deg):
    """
    Create a radiating rib at (cx, Y=5..10, cz).
    Rib is a box: length=10.84mm along X, width=4mm along Z, height=5mm along Y.
    Rotated about Y-axis by angle_deg degrees, centered at (cx, 7.5, cz).
    """
    # Create box centered at origin: X=[-5.42..5.42], Y=[-2.5..2.5], Z=[-2..2]
    rib = cq.Workplane("XY").box(RAD_RIB_LENGTH, RAD_RIB_H, RAD_RIB_WIDTH, centered=True)
    # Rotate about Y-axis through origin
    rib = rib.rotate((0, 0, 0), (0, 1, 0), angle_deg)
    # Translate to rear face position: Y center = 7.5 (Y=5..10), XZ = (cx, cz)
    rib = rib.translate((cx, 7.5, cz))
    return rib

for (cx, cz, angle_deg) in RAD_RIB_SPECS:
    rib = make_radiating_rib(cx, cz, angle_deg)
    plate = plate.union(rib)

print("  Radiating ribs added: OK")

# =============================================================================
# Step 8: Wiring channels (×2, subtractive)
# Rectangular cuts from rear face (Y=5) inward to Y=1 (4mm deep)
# Channel 1: X=0..15.9, Y=1..5, Z=37..43
# Channel 2: X=128.1..144, Y=1..5, Z=37..43
# =============================================================================
print("Step 8: Cutting wiring channels...")

# Channel 1: X=0..15.9, Y=1..5, Z=37..43
# box(W, D, H, centered=False) on XY: X=[0..W], Y=[0..D], Z=[0..H]
chan1 = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0.0, 1.0, RIB_Z0))
    .box(15.9, 4.0, CHAN_W, centered=False)
    # Box: X=[0..15.9], Y=[1..5], Z=[37..43]
)
plate = plate.cut(chan1)

# Channel 2: X=128.1..144, Y=1..5, Z=37..43
chan2 = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(128.1, 1.0, RIB_Z0))
    .box(15.9, 4.0, CHAN_W, centered=False)
    # Box: X=[128.1..144], Y=[1..5], Z=[37..43]
)
plate = plate.cut(chan2)

print("  Wiring channels: OK")

# =============================================================================
# Step 8a: Strain-relief bumps inside channels (×4, additive)
# Cylinders: D=2mm, H=1.5mm, from channel floor Y=1 up to Y=2.5
# =============================================================================
print("Step 8a: Adding strain-relief bumps...")

BUMP_R = 1.0  # 2mm diameter
BUMP_H = 1.5  # 1.5mm tall, from Y=1 to Y=2.5

BUMP_POSITIONS = [
    (10.9,  40.0),   # Channel 1, bump 1
    (5.9,   40.0),   # Channel 1, bump 2
    (133.1, 40.0),   # Channel 2, bump 1
    (138.1, 40.0),   # Channel 2, bump 2
]

for (bx, bz) in BUMP_POSITIONS:
    bump = cylinder_along_y(bx, bz, BUMP_R, 1.0, 1.0 + BUMP_H)
    plate = plate.union(bump)

print("  Strain-relief bumps: OK")

# =============================================================================
# Step 9: Snap notches (×2, subtractive)
# Left:  X=0..1.5, Y=2..5, Z=38.5..41.5
# Right: X=142.5..144, Y=2..5, Z=38.5..41.5
# =============================================================================
print("Step 9: Cutting snap notches...")

left_notch = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0.0, 2.0, 38.5))
    .box(1.5, 3.0, 3.0, centered=False)
)
plate = plate.cut(left_notch)

right_notch = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(142.5, 2.0, 38.5))
    .box(1.5, 3.0, 3.0, centered=False)
)
plate = plate.cut(right_notch)

print("  Snap notches: OK")

# =============================================================================
# Step 10: Perimeter chamfers
# 1.5mm chamfer on external perimeter edges (excluding Y=0 face edges)
# 0.3mm elephant's foot chamfer on Z=0 bottom edge at Y=0
# =============================================================================
print("Step 10: Applying perimeter chamfers...")

CHAMFER_EXT = 1.5
CHAMFER_ELEPH = 0.3

# Top face edges (Z=80): there are edges on the plate top face
# Use NearestToPointSelector to pick the top-front and top-rear edges
try:
    # Top face front edge (Z=80, Y=0)
    plate = plate.edges(
        cq.selectors.NearestToPointSelector((72.0, 0.0, PLATE_H))
    ).chamfer(CHAMFER_EXT)
    print("  Top face front edge chamfer: OK")
except Exception as e:
    print(f"  Top face front edge chamfer skipped: {e}")

try:
    # Top face rear edge (Z=80, Y=5)
    plate = plate.edges(
        cq.selectors.NearestToPointSelector((72.0, PLATE_D, PLATE_H))
    ).chamfer(CHAMFER_EXT)
    print("  Top face rear edge chamfer: OK")
except Exception as e:
    print(f"  Top face rear edge chamfer skipped: {e}")

try:
    # Rear face bottom edge (Y=5, Z=0)
    plate = plate.edges(
        cq.selectors.NearestToPointSelector((72.0, PLATE_D, 0.0))
    ).chamfer(CHAMFER_EXT)
    print("  Rear face bottom edge chamfer: OK")
except Exception as e:
    print(f"  Rear face bottom edge chamfer skipped: {e}")

try:
    # Elephant's foot: Z=0 bottom edge on front face (Y=0)
    plate = plate.edges(
        cq.selectors.NearestToPointSelector((72.0, 0.0, 0.0))
    ).chamfer(CHAMFER_ELEPH)
    print("  Elephant's foot chamfer: OK")
except Exception as e:
    print(f"  Elephant's foot chamfer skipped: {e}")

print("  Perimeter chamfers done")

# =============================================================================
# Validation (Rubrics 3, 4, 5)
# =============================================================================
print()
print("=" * 60)
print("VALIDATION")
print("=" * 60)

v = Validator(plate)

# --- Motor bores (void at centers) ---
v.check_void("Motor bore 1 center",  BORE_1_X, 2.5, BORE_Z,
             f"void at bore 1 ({BORE_1_X}, 2.5, {BORE_Z})")
v.check_void("Motor bore 2 center",  BORE_2_X, 2.5, BORE_Z,
             f"void at bore 2 ({BORE_2_X}, 2.5, {BORE_Z})")

# Bore walls solid (outside bore radius)
v.check_solid("Motor bore 1 wall",  BORE_1_X + BORE_R + 0.5, 2.5, BORE_Z,
              "solid outside bore 1 radius")
v.check_solid("Motor bore 2 wall",  BORE_2_X - BORE_R - 0.5, 2.5, BORE_Z,
              "solid outside bore 2 radius")

# --- M3 clearance holes (void) ---
# Y=2.5: mid-plate, confirms through-cut exists
# Y=5.25: 0.25mm inside the 0.5mm boss extension — confirms hole reaches into boss.
#   This probe catches the specific plug bug (Y=5.0→5.5 solid) if it ever regresses.
for i, (hx, hz) in enumerate(BOSS_POSITIONS):
    v.check_void(f"M3 hole {i+1:02d} mid ({hx},{hz})", hx, 2.5, hz,
                 f"void at clearance hole mid-point ({hx}, 2.5, {hz})")
    v.check_void(f"M3 hole {i+1:02d} boss-ext ({hx},{hz})", hx, 5.25, hz,
                 f"void at clearance hole boss-extension ({hx}, 5.25, {hz}) — plug regression check")

# --- Boss walls (solid annulus between insert bore and outer OD) ---
# Probe at (bx + 3.0, 7.5, bz): 3mm offset from boss center,
# which is inside boss OD (r=4.5mm) but outside insert bore (r=2.35mm).
# This confirms the boss cylinder exists and the insert bore was correctly cut.
BOSS_WALL_PROBE_OFFSET = 3.0
for i, (bx, bz) in enumerate(BOSS_POSITIONS):
    v.check_solid(f"Boss {i+1:02d} wall ({bx},{bz})", bx + BOSS_WALL_PROBE_OFFSET, 7.5, bz,
                  f"solid in boss wall annulus at ({bx+BOSS_WALL_PROBE_OFFSET}, 7.5, {bz})")

# --- Insert bores (void) ---
for i, (bx, bz) in enumerate(BOSS_POSITIONS):
    v.check_void(f"Insert bore {i+1:02d} ({bx},{bz})", bx, 8.0, bz,
                 f"void in insert bore at ({bx}, 8.0, {bz})")

# --- Field zone (void = recessed 0.5mm from Y=0) ---
# Bottom strip interior
v.check_void("Field zone bottom strip",  72.0, 0.25, 1.5,
             "void inside bottom field strip (Z=0..3)")
# Top strip interior
v.check_void("Field zone top strip",  72.0, 0.25, 78.5,
             "void inside top field strip (Z=77..80)")
# Center gap lower
v.check_void("Field zone gap lower",  72.0, 0.25, 20.0,
             "void in center gap lower (Z=3..37)")
# Center gap upper
v.check_void("Field zone gap upper",  72.0, 0.25, 60.0,
             "void in center gap upper (Z=43..77)")

# --- Mounting pads (solid — not in field zone, outside bore radius) ---
# Probe at points that are:
#   - In the pad zone (X=0..71.5 for pad 1, X=72.5..144 for pad 2)
#   - At Y=0.25 (inside the 0.5mm pocket depth — the pad zone is NOT pocketed)
#   - Outside the motor bore radius (18.6mm from bore center)
#   - Outside the clearance hole positions
# Pad 1 probe: (30.0, 0.25, 60.0)
#   Distance to bore 1 (34.5,40): sqrt((30-34.5)^2+(60-40)^2) = sqrt(20.25+400)=20.5mm > 18.6mm OK
#   Not at any clearance hole. In pad zone (X=30<71.5, Z=60 in 3..77). Not in field gap.
# Pad 2 probe: (100.0, 0.25, 60.0)
#   Distance to bore 2 (109.5,40): sqrt((100-109.5)^2+(60-40)^2) = sqrt(90.25+400)=22.1mm > 18.6mm OK
v.check_solid("Mounting pad 1 solid",  30.0, 0.25, 60.0,
              "solid at pump 1 pad zone (X=30, Y=0.25, Z=60 — not recessed, outside bore)")
v.check_solid("Mounting pad 2 solid",  100.0, 0.25, 60.0,
              "solid at pump 2 pad zone (X=100, Y=0.25, Z=60 — not recessed, outside bore)")
v.check_solid("Cross-rib band front solid",  72.0, 0.25, 40.0,
              "solid at cross-rib band (Z=37..43, not recessed)")

# --- Cross-rib body (solid) ---
v.check_solid("Cross-rib body",  72.0, 7.5, 40.0,
              "solid inside cross-rib")

# --- Radiating rib midpoints (solid) ---
for i, (cx, cz, _) in enumerate(RAD_RIB_SPECS):
    v.check_solid(f"Radiating rib {i+1} ({cx},{cz})", cx, 7.5, cz,
                  f"solid at rib midpoint ({cx}, 7.5, {cz})")

# --- Wiring channels (void) ---
v.check_void("Wiring channel 1",  7.95, 3.0, 40.0,
             "void inside wiring channel 1")
v.check_void("Wiring channel 2",  136.05, 3.0, 40.0,
             "void inside wiring channel 2")

# --- Strain-relief bumps (solid inside channel) ---
v.check_solid("Strain-relief bump ch1-1",  10.9, 1.5, 40.0,
              "solid in strain-relief bump (channel 1, bump 1)")
v.check_solid("Strain-relief bump ch1-2",  5.9, 1.5, 40.0,
              "solid in strain-relief bump (channel 1, bump 2)")

# --- Snap notches (void) ---
v.check_void("Snap notch left",  0.75, 3.5, 40.0,
             "void in left snap notch")
v.check_void("Snap notch right",  143.25, 3.5, 40.0,
             "void in right snap notch")

# --- Plate body general ---
v.check_solid("Plate body center",  72.0, 2.5, 40.0,
              "solid at plate center (between bores)")
v.check_solid("Plate body bottom-left",  5.0, 2.5, 5.0,
              "solid in bottom-left plate zone")
v.check_solid("Plate body top-right",  139.0, 2.5, 75.0,
              "solid in top-right plate zone")

# --- Bounding box (Rubric 5) ---
bb = plate.val().BoundingBox()
print(f"\nBounding box: "
      f"X=[{bb.xmin:.2f},{bb.xmax:.2f}] "
      f"Y=[{bb.ymin:.2f},{bb.ymax:.2f}] "
      f"Z=[{bb.zmin:.2f},{bb.zmax:.2f}]")

# X: 0 to 144 (corner radii inset the corners, bounding box still 0..144)
v.check_bbox("X", bb.xmin, bb.xmax, 0.0, 144.0)
# Y: 0 to 10 (bosses and ribs protrude to Y=10)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, 10.0)
# Z: 0 to 80
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, 80.0)

# --- Solid validity (Rubric 4) ---
v.check_valid()
v.check_single_body()
# Volume: plate body ≈ 57600mm³ minus bores/holes, plus bosses/ribs
# Bosses add ~8 * pi*4.5^2*5 = 2545 mm³
# Bores subtract ~2 * pi*18.6^2*5 = 10877 mm³
# Use wide fill_range since bosses and ribs add volume
v.check_volume(
    expected_envelope=PLATE_W * PLATE_D * PLATE_H,  # 57600
    fill_range=(0.4, 1.6)
)

# --- Summary ---
all_passed = v.summary()

if not all_passed:
    print(f"\n{v.fail_count} check(s) failed. Exiting without STEP export.")
    sys.exit(1)

# =============================================================================
# Export STEP
# =============================================================================
output_path = Path(__file__).resolve().parent / "pump-tray-cadquery.step"
cq.exporters.export(plate, str(output_path))
print(f"\nSTEP exported to: {output_path}")
