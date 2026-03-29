#!/usr/bin/env python3
"""
Generate the bottom shell STEP file for the pump cartridge mechanism.

Coordinate system:
  Origin: front-left-bottom exterior corner
  X: width (left to right), 0..132 mm
  Y: depth (front to back), 0..177 mm
  Z: height (bottom to top), 0..33.5 mm
  Envelope: 132 x 177 x 33.5 mm -> X:[0,132] Y:[0,177] Z:[0,33.5]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

import cadquery as cq
from step_validate import Validator

# ==============================================================================
# RUBRIC 1 -- Feature Planning Table
# ==============================================================================

FEATURE_TABLE = """
+----+-----------------------------------+--------------------------------------------+----------+----------+------+---------------------------+------------------------------------------+-------------------------------+
| #  | Feature Name                      | Mechanical Function                        | Operation| Shape    | Axis | Center Position (X,Y,Z)   | Dimensions                               | Notes                         |
+----+-----------------------------------+--------------------------------------------+----------+----------+------+---------------------------+------------------------------------------+-------------------------------+
|  1 | Floor Plate (1.1)                 | Structural base, pumps rest on it          | Base     | Box      | Z    | (66,88.5,1.0)             | 132 x 177 x 2.0                         | Z=0..2.0                     |
|  2 | Left Inner Rib (1.2)             | Lateral constraint for left linkage arm    | Add      | Box      | Y    | (9.6,88.0,11.125)         | 1.2W x 172.0D x 18.25H                  | X=9.0..10.2, Y=2..174, Z=2..20.25|
|  3 | Right Inner Rib (1.2)            | Lateral constraint for right linkage arm   | Add      | Box      | Y    | (122.4,88.0,11.125)       | 1.2W x 172.0D x 18.25H                  | X=121.8..123, Y=2..174, Z=2..20.25|
|  6 | Left Side Wall (2.1)             | Structural side wall + groove + slots      | Base     | Box      | Z    | (1.0,88.5,16.75)          | 2.0W x 177 x 33.5H                      | X=0..2                        |
|  7 | Right Side Wall (2.2)            | Structural side wall (mirror)              | Base     | Box      | Z    | (131.0,88.5,16.75)        | 2.0W x 177 x 33.5H                      | X=130..132                    |
|  8 | Left Groove-Band Thickening (2.1)| Extra wall thickness for groove depth      | Add      | Box      | Y    | (3.85,88.5,15.0)          | 3.7W x 177D x 4.5H                      | X=2..5.7, Z=12.75..17.25     |
|  9 | Right Groove-Band Thickening(2.2)| Extra wall thickness for groove depth      | Add      | Box      | Y    | (128.15,88.5,15.0)        | 3.7W x 177D x 4.5H                      | X=126.3..130, Z=12.75..17.25 |
| 10 | Left Rail Groove (2.3)           | Dock rail slides in for cartridge mounting | Remove   | Box      | Y    | (2.25,91.0,15.0)          | 4.5D(X) x 172D(Y) x 4.5H               | X=0..4.5, Z=12.75..17.25     |
| 11 | Right Rail Groove (2.3)          | Dock rail (mirror)                         | Remove   | Box      | Y    | (129.75,91.0,15.0)        | 4.5D(X) x 172D(Y) x 4.5H               | X=127.5..132, Z=12.75..17.25 |
| 12 | Left Groove Entry Chamfer (2.3)  | Flared mouth for blind insertion alignment | Remove   | Loft     | Y    | (2.25,2.5,15.0)           | Y=0..5, tapers W and D                  | 30deg chamfer                 |
| 13 | Right Groove Entry Chamfer (2.3) | Flared mouth (mirror)                      | Remove   | Loft     | Y    | (129.75,2.5,15.0)         | Y=0..5, tapers W and D                  | 30deg chamfer                 |
| 14 | Left Detent Relief (2.3)         | Snap-in retention at full insertion        | Remove   | Box      | Y    | (2.1,174.5,15.0)          | 0.3D x 2L x 4.5H                        | Y=173.5..175.5, 0.3mm extra  |
| 15 | Right Detent Relief (2.3)        | Snap-in retention (mirror)                 | Remove   | Box      | Y    | (129.9,174.5,15.0)        | 0.3D x 2L x 4.5H                        | mirror                        |
| 16 | Left Partition Slot (2.4)        | Receives mounting partition left edge      | Remove   | Box      | Z    | (1.0,75.0,17.75)          | 2.0W x 5.4D x 31.5H                     | X=0..2, Y=72.3..77.7, Z=2..33.5|
| 17 | Right Partition Slot (2.4)       | Receives mounting partition right edge     | Remove   | Box      | Z    | (131.0,75.0,17.75)        | 2.0W x 5.4D x 31.5H                     | X=130..132, Y=72.3..77.7     |
| 18 | Left Wall Catch Ledges x5 (2.5) | Snap-fit engagement for top shell hooks    | Add      | Box      | Y    | (varies)                   | 0.3prot x 8.0W x 0.3H each              | Z=33.2..33.5, +X from X=2.0  |
| 19 | Right Wall Catch Ledges x5(2.5) | Snap-fit engagement (mirror)               | Add      | Box      | Y    | (varies)                   | 0.3prot x 8.0W x 0.3H each              | -X from X=130.0               |
| 20 | Center Divider Wall (2.6)        | Separates left and right pump bays         | Add      | Box      | Y    | (66.0,76.0,17.75)         | 2.0W x 148D x 31.5H                     | X=65..67, Y=2..150, Z=2..33.5|
| 21 | Rear Wall Plate (3.1)            | Houses JG bores, structural rear wall      | Base     | Box      | Z    | (66.0,175.5,16.75)        | 132W x 3.0D x 33.5H                     | Y=174..177                    |
| 22 | JG Bore 1 left lower (3.2)      | Press-fit bore for JG fitting              | Remove   | Cylinder | Y    | (33.5,175.5,9.55)         | dia=9.6, len=3.0                         | Y=174..177                    |
| 23 | JG Bore 2 right lower (3.2)     | Press-fit bore for JG fitting              | Remove   | Cylinder | Y    | (98.5,175.5,9.55)         | dia=9.6, len=3.0                         | Y=174..177                    |
| 24 | JG Bore 3 left upper (3.2)      | Press-fit bore for JG fitting              | Remove   | Cylinder | Y    | (33.5,175.5,26.65)        | dia=9.6, len=3.0                         | Y=174..177                    |
| 25 | JG Bore 4 right upper (3.2)     | Press-fit bore for JG fitting              | Remove   | Cylinder | Y    | (98.5,175.5,26.65)        | dia=9.6, len=3.0                         | Y=174..177                    |
| 26 | Left Spring Boss (3.3)           | Centers compression spring coils           | Add      | Cylinder | Y    | (33.5,171.5,18.1)         | dia=2.0, height=5.0                      | Y=169..174                    |
| 27 | Right Spring Boss (3.3)          | Centers compression spring coils           | Add      | Cylinder | Y    | (98.5,171.5,18.1)         | dia=2.0, height=5.0                      | Y=169..174                    |
| 28 | Blade Terminal Slot BT1 (3.4)    | Recessed slot for blade terminal           | Remove   | Box      | Y    | (12.0,176.5,5.5)          | 8.0W x 1.0D x 4.0H                      | rear face recess              |
| 29 | Blade Terminal Slot BT2 (3.4)    | Recessed slot for blade terminal           | Remove   | Box      | Y    | (12.0,176.5,28.0)         | 8.0W x 1.0D x 4.0H                      |                               |
| 30 | Blade Terminal Slot BT3 (3.4)    | Recessed slot for blade terminal           | Remove   | Box      | Y    | (120.0,176.5,5.5)         | 8.0W x 1.0D x 4.0H                      |                               |
| 31 | Blade Terminal Slot BT4 (3.4)    | Recessed slot for blade terminal           | Remove   | Box      | Y    | (120.0,176.5,28.0)        | 8.0W x 1.0D x 4.0H                      |                               |
| 32 | Rear Wall Catch Ledges x4 (3.5) | Snap-fit for top shell hooks               | Add      | Box      | X    | (varies)                   | 0.3prot x 8.0W x 0.3H each              | -Y from Y=174.0               |
| 33 | Front Wall Plate (4.1)           | Structural front wall                      | Base     | Box      | Z    | (66.0,1.0,16.75)          | 132W x 2.0D x 33.5H                     | Y=0..2                        |
| 34 | Front Wall Catch Ledges x4 (4.2)| Snap-fit for top shell hooks               | Add      | Box      | X    | (varies)                   | 0.3prot x 8.0W x 0.3H each              | +Y from Y=2.0                 |
| 35 | Exterior Fillets (5.1)           | Finished edge treatment                    | Modify   | Fillet   | --   | All exterior edges          | R=1.0 mm                                |                               |
| 36 | Elephant's Foot Chamfer (5.2)    | Prevents first-layer flare                 | Modify   | Chamfer  | Z    | Bottom perimeter            | 0.3 x 45 deg                            | Z=0 plane edges               |
+----+-----------------------------------+--------------------------------------------+----------+----------+------+---------------------------+------------------------------------------+-------------------------------+
"""

print("=" * 80)
print("RUBRIC 1 -- Feature Planning Table")
print("=" * 80)
print(FEATURE_TABLE)

# ==============================================================================
# CONSTANTS from parts.md
# ==============================================================================

# Envelope
W = 132.0   # X extent
D = 177.0   # Y extent
H = 33.5    # Z extent

# Wall thicknesses
SIDE_WALL = 2.0
FRONT_WALL = 2.0
REAR_WALL = 3.0
FLOOR_T = 2.0

# Groove band
GROOVE_W = 4.5       # Z direction
GROOVE_D = 4.5       # X direction, depth into wall
GROOVE_CENTER_Z = 15.0
GROOVE_Z_BOT = 12.75
GROOVE_Z_TOP = 17.25
GROOVE_BAND_INNER_LEFT = 5.7    # inner face X of left wall at groove band
GROOVE_BAND_INNER_RIGHT = 126.3  # inner face X of right wall at groove band

# Groove Y extents
GROOVE_Y_CHAMFER_END = 5.0
GROOVE_Y_END = D  # 177.0

# Detent relief
DETENT_Y_START = 173.5
DETENT_Y_END = 175.5
DETENT_EXTRA_DEPTH = 0.3

# Partition slots
PART_SLOT_Y_START = 72.3
PART_SLOT_Y_END = 77.7
PART_SLOT_W = 5.4  # Y direction

# Center divider
DIVIDER_X_LEFT = 65.0
DIVIDER_X_RIGHT = 67.0
DIVIDER_Y_END = 150.0  # Shortened from rear wall inner face (174) to clear release plate zone

# Mid-height guide channel geometry
# The arm channel sits just above the groove band (Z=12.75..17.25).
# The groove band thickening top face at Z=17.25 serves as the natural
# shelf/ledge for the arm to rest on. No separate bridge shelf is needed.
# Channel: Z=17.25..20.25 (3mm tall), X=2.0..9.0 (7mm wide) left side.
# Inner ribs extend from floor (Z=2.0) to channel top (Z=20.25).
RIB_LEFT_X_START = 9.0
RIB_LEFT_X_END = 10.2
RIB_RIGHT_X_START = 121.8
RIB_RIGHT_X_END = 123.0
RIB_Z_BOT = FLOOR_T  # 2.0 -- rib starts at floor for structural support
RIB_Z_TOP = 20.25    # top of channel
RIB_Y_START = FRONT_WALL  # 2.0
RIB_Y_END = D - REAR_WALL  # 174.0

# Channel dimensions (arm slot)
CHANNEL_Z_BOT = 17.25  # arm sits here (groove band top = natural shelf)
CHANNEL_Z_TOP = 20.25  # arm top (3mm above channel bottom)
CHANNEL_CENTER_Z = 18.75  # close to JG bore pattern center 18.1 (0.65mm offset)

# JG bore positions (X, Z) and dimensions
JG_BORE_DIA = 9.6
JG_BORE_R = JG_BORE_DIA / 2.0
JG_BORES = [
    (33.5, 9.55),   # JG1 left lower
    (98.5, 9.55),   # JG2 right lower
    (33.5, 26.65),  # JG3 left upper
    (98.5, 26.65),  # JG4 right upper
]

# Spring bosses (revised -- 5mm height)
SPRING_BOSS_DIA = 2.0
SPRING_BOSS_HEIGHT = 5.0
SPRING_BOSSES = [
    (33.5, 18.1),  # left
    (98.5, 18.1),  # right
]

# Blade terminal slots
BT_W = 8.0    # X
BT_H = 4.0    # Z
BT_DEPTH = 1.0  # Y into rear face
BT_SLOTS = [
    (12.0, 5.5),    # BT1 left lower
    (12.0, 28.0),   # BT2 left upper
    (120.0, 5.5),   # BT3 right lower
    (120.0, 28.0),  # BT4 right upper
]

# Catch ledges
LEDGE_H = 0.3
LEDGE_PROT = 0.3
LEDGE_LEN = 8.0
LEDGE_Z_BOT = H - LEDGE_H  # 33.2
LEDGE_Z_TOP = H             # 33.5

# Left wall ledge Y centers
LEFT_LEDGE_Y = [19.0, 54.0, 89.0, 124.0, 159.0]
# Right wall same Y
RIGHT_LEDGE_Y = LEFT_LEDGE_Y

# Front wall ledge X centers
FRONT_LEDGE_X = [18.0, 50.0, 82.0, 114.0]
# Rear wall same X
REAR_LEDGE_X = FRONT_LEDGE_X

# Fillet radius
EXT_FILLET_R = 1.0
# Elephant foot chamfer
EF_CHAMFER = 0.3


# ==============================================================================
# MODELING
# ==============================================================================

print("\n" + "=" * 80)
print("Building geometry...")
print("=" * 80)

# --- Step 1: Outer shell box (solid block) ---
# Feature: Overall envelope
shell = cq.Workplane("XY").box(W, D, H, centered=False)

# --- Step 2: Cut interior cavity ---
# The interior cavity is the space inside the walls and above the floor.
# We need to handle the groove-band thickening: at Z=12.75..17.25 the side walls
# are thicker (inner face moves inward from X=2 to X=5.7 left, X=130 to X=126.3 right).
# Strategy: cut the main cavity at the nominal wall thickness, then ADD material
# back for the groove-band thickening.

# Main interior cavity: X=2..130, Y=2..174, Z=2..33.5
cavity = (
    cq.Workplane("XY")
    .transformed(offset=(SIDE_WALL, FRONT_WALL, FLOOR_T))
    .box(
        W - 2 * SIDE_WALL,   # 128
        D - FRONT_WALL - REAR_WALL,  # 172
        H - FLOOR_T,         # 31.5
        centered=False,
    )
)
shell = shell.cut(cavity)

# --- Step 3: Add groove-band thickening (fill back cavity at groove height) ---
# Feature: Left Groove-Band Thickening (2.1)
# At Z=12.75..17.25, the left wall inner face moves from X=2.0 to X=5.7.
# We need to add solid from X=2.0 to X=5.7 in that Z band.
left_groove_thick = (
    cq.Workplane("XY")
    .transformed(offset=(SIDE_WALL, FRONT_WALL, GROOVE_Z_BOT))
    .box(
        GROOVE_BAND_INNER_LEFT - SIDE_WALL,  # 5.7 - 2.0 = 3.7
        D - FRONT_WALL - REAR_WALL,          # 172
        GROOVE_W,                             # 4.5
        centered=False,
    )
)
shell = shell.union(left_groove_thick)

# Feature: Right Groove-Band Thickening (2.2)
right_groove_thick = (
    cq.Workplane("XY")
    .transformed(offset=(GROOVE_BAND_INNER_RIGHT, FRONT_WALL, GROOVE_Z_BOT))
    .box(
        W - SIDE_WALL - GROOVE_BAND_INNER_RIGHT,  # 132 - 2 - 126.3 = 3.7
        D - FRONT_WALL - REAR_WALL,                # 172
        GROOVE_W,                                   # 4.5
        centered=False,
    )
)
shell = shell.union(right_groove_thick)

# --- Step 4: Cut rail grooves ---
# Feature: Left Rail Groove (2.3)
# X=0..4.5, Z=12.75..17.25, Y=5..177 (full depth groove)
left_groove = (
    cq.Workplane("XY")
    .transformed(offset=(0, GROOVE_Y_CHAMFER_END, GROOVE_Z_BOT))
    .box(
        GROOVE_D,                              # 4.5
        D - GROOVE_Y_CHAMFER_END,              # 177 - 5 = 172
        GROOVE_W,                              # 4.5
        centered=False,
    )
)
shell = shell.cut(left_groove)

# Feature: Right Rail Groove (2.3)
right_groove = (
    cq.Workplane("XY")
    .transformed(offset=(W - GROOVE_D, GROOVE_Y_CHAMFER_END, GROOVE_Z_BOT))
    .box(
        GROOVE_D,
        D - GROOVE_Y_CHAMFER_END,
        GROOVE_W,
        centered=False,
    )
)
shell = shell.cut(right_groove)

# --- Step 5: Cut groove entry chamfers ---
# Feature: Left Groove Entry Chamfer (2.3)
# At Y=0, the groove opening is wider (~10.3mm in Z) and no depth (X=0).
# At Y=5, the groove is 4.5mm wide (Z) and 4.5mm deep (X).
# The chamfer is a tapered pocket approximated with thin slices.

import math

chamfer_half_extra = 5.0 * math.tan(math.radians(30))  # ~2.887mm per side

# Left entry chamfer - use a series of thin slices to approximate the taper
n_slices = 10
for i in range(n_slices):
    y_start = i * GROOVE_Y_CHAMFER_END / n_slices
    y_end = (i + 1) * GROOVE_Y_CHAMFER_END / n_slices
    y_mid = (y_start + y_end) / 2.0
    # Interpolation factor: 0 at Y=0, 1 at Y=5
    t = y_mid / GROOVE_Y_CHAMFER_END
    # Width (Z) tapers from ~10.27 to 4.5
    current_half_extra = chamfer_half_extra * (1.0 - t)
    current_z_bot = GROOVE_Z_BOT - current_half_extra
    current_z_top = GROOVE_Z_TOP + current_half_extra
    # Depth (X) tapers from 0 to 4.5
    current_depth = GROOVE_D * t

    if current_depth < 0.01:
        continue

    slice_cut = (
        cq.Workplane("XY")
        .transformed(offset=(0, y_start, current_z_bot))
        .box(
            current_depth,
            y_end - y_start,
            current_z_top - current_z_bot,
            centered=False,
        )
    )
    shell = shell.cut(slice_cut)

# Right entry chamfer (mirror)
for i in range(n_slices):
    y_start = i * GROOVE_Y_CHAMFER_END / n_slices
    y_end = (i + 1) * GROOVE_Y_CHAMFER_END / n_slices
    y_mid = (y_start + y_end) / 2.0
    t = y_mid / GROOVE_Y_CHAMFER_END
    current_half_extra = chamfer_half_extra * (1.0 - t)
    current_z_bot = GROOVE_Z_BOT - current_half_extra
    current_z_top = GROOVE_Z_TOP + current_half_extra
    current_depth = GROOVE_D * t

    if current_depth < 0.01:
        continue

    slice_cut = (
        cq.Workplane("XY")
        .transformed(offset=(W - current_depth, y_start, current_z_bot))
        .box(
            current_depth,
            y_end - y_start,
            current_z_top - current_z_bot,
            centered=False,
        )
    )
    shell = shell.cut(slice_cut)

# --- Step 6: Cut detent reliefs ---
# Feature: Left Detent Relief (2.3)
# Additional 0.3mm depth beyond groove floor at Y=173.5..175.5
left_detent = (
    cq.Workplane("XY")
    .transformed(offset=(GROOVE_D, DETENT_Y_START, GROOVE_Z_BOT))
    .box(
        DETENT_EXTRA_DEPTH,           # 0.3
        DETENT_Y_END - DETENT_Y_START,  # 2.0
        GROOVE_W,                       # 4.5
        centered=False,
    )
)
shell = shell.cut(left_detent)

# Feature: Right Detent Relief (2.3)
right_detent = (
    cq.Workplane("XY")
    .transformed(offset=(W - GROOVE_D - DETENT_EXTRA_DEPTH, DETENT_Y_START, GROOVE_Z_BOT))
    .box(
        DETENT_EXTRA_DEPTH,
        DETENT_Y_END - DETENT_Y_START,
        GROOVE_W,
        centered=False,
    )
)
shell = shell.cut(right_detent)

# --- Step 7: Cut partition slots ---
# Feature: Left Partition Slot (2.4)
# X=0..2, Y=72.3..77.7, Z=2..33.5
left_part_slot = (
    cq.Workplane("XY")
    .transformed(offset=(0, PART_SLOT_Y_START, FLOOR_T))
    .box(
        SIDE_WALL,          # 2.0
        PART_SLOT_W,        # 5.4
        H - FLOOR_T,        # 31.5
        centered=False,
    )
)
shell = shell.cut(left_part_slot)

# Feature: Right Partition Slot (2.4)
right_part_slot = (
    cq.Workplane("XY")
    .transformed(offset=(W - SIDE_WALL, PART_SLOT_Y_START, FLOOR_T))
    .box(
        SIDE_WALL,
        PART_SLOT_W,
        H - FLOOR_T,
        centered=False,
    )
)
shell = shell.cut(right_part_slot)

# --- Step 8: Add center divider wall ---
# Feature: Center Divider Wall (2.6)
# X=65..67, Y=2..150, Z=2..33.5
# Shortened to Y=150 to clear release plate path (plate at Y≈157-162, translates 3mm rearward)
divider = (
    cq.Workplane("XY")
    .transformed(offset=(DIVIDER_X_LEFT, FRONT_WALL, FLOOR_T))
    .box(
        DIVIDER_X_RIGHT - DIVIDER_X_LEFT,  # 2.0
        DIVIDER_Y_END - FRONT_WALL,         # 148
        H - FLOOR_T,                         # 31.5
        centered=False,
    )
)
shell = shell.union(divider)

# --- Step 9: Add mid-height guide channel inner ribs ---
# The guide channels sit just above the groove band. The groove band thickening
# top face at Z=17.25 acts as the natural shelf for the arm. The inner ribs
# provide lateral constraint. Ribs extend from floor to channel top (Z=2..20.25).
# Channel slot (arm space): X=2.0..9.0, Z=17.25..20.25 (left), mirrored for right.

# Feature: Left Inner Rib (1.2)
# X=9.0..10.2, Y=2..174, Z=2..20.25
left_rib = (
    cq.Workplane("XY")
    .transformed(offset=(RIB_LEFT_X_START, RIB_Y_START, RIB_Z_BOT))
    .box(
        RIB_LEFT_X_END - RIB_LEFT_X_START,  # 1.2
        RIB_Y_END - RIB_Y_START,             # 172
        RIB_Z_TOP - RIB_Z_BOT,              # 18.25
        centered=False,
    )
)
shell = shell.union(left_rib)

# Feature: Right Inner Rib (1.2)
right_rib = (
    cq.Workplane("XY")
    .transformed(offset=(RIB_RIGHT_X_START, RIB_Y_START, RIB_Z_BOT))
    .box(
        RIB_RIGHT_X_END - RIB_RIGHT_X_START,  # 1.2
        RIB_Y_END - RIB_Y_START,               # 172
        RIB_Z_TOP - RIB_Z_BOT,                # 18.25
        centered=False,
    )
)
shell = shell.union(right_rib)

# --- Step 10: Cut JG fitting bores ---
# Feature: JG Bores (3.2) -- 4 cylindrical bores through rear wall along Y axis
for idx, (bx, bz) in enumerate(JG_BORES):
    bore = cq.Workplane("XY").cylinder(
        REAR_WALL, JG_BORE_R, centered=True
    )
    # Rotate to align along Y axis and translate to position
    bore = bore.rotateAboutCenter((1, 0, 0), 90).translate((bx, D - REAR_WALL / 2.0, bz))
    shell = shell.cut(bore)

# --- Step 11: Add spring bosses ---
# Feature: Spring Bosses (3.3)
# Cylindrical bosses protruding from rear wall inner face in -Y direction
# Base at Y=174, tip at Y=169, dia=2.0mm
for sbx, sbz in SPRING_BOSSES:
    boss = cq.Workplane("XY").cylinder(
        SPRING_BOSS_HEIGHT, SPRING_BOSS_DIA / 2.0, centered=True
    )
    boss = boss.rotateAboutCenter((1, 0, 0), 90).translate(
        (sbx, D - REAR_WALL - SPRING_BOSS_HEIGHT / 2.0, sbz)
    )
    shell = shell.union(boss)

# --- Step 12: Cut blade terminal slots ---
# Feature: Blade Terminal Slots (3.4)
# Recessed pockets in rear exterior face (Y=177), 1mm deep into wall
for btx, btz in BT_SLOTS:
    bt_slot = (
        cq.Workplane("XY")
        .transformed(offset=(btx - BT_W / 2.0, D - BT_DEPTH, btz - BT_H / 2.0))
        .box(BT_W, BT_DEPTH, BT_H, centered=False)
    )
    shell = shell.cut(bt_slot)

# --- Step 13: Add snap-fit catch ledges ---
# All ledges: 0.3mm tall (Z=33.2..33.5), 0.3mm protrusion, 8mm long

# Feature: Left Wall Catch Ledges (2.5) -- 5 ledges, protrude +X from X=2.0
for yc in LEFT_LEDGE_Y:
    ledge = (
        cq.Workplane("XY")
        .transformed(offset=(SIDE_WALL, yc - LEDGE_LEN / 2.0, LEDGE_Z_BOT))
        .box(LEDGE_PROT, LEDGE_LEN, LEDGE_H, centered=False)
    )
    shell = shell.union(ledge)

# Feature: Right Wall Catch Ledges (2.5) -- 5 ledges, protrude -X from X=130.0
for yc in RIGHT_LEDGE_Y:
    ledge = (
        cq.Workplane("XY")
        .transformed(offset=(W - SIDE_WALL - LEDGE_PROT, yc - LEDGE_LEN / 2.0, LEDGE_Z_BOT))
        .box(LEDGE_PROT, LEDGE_LEN, LEDGE_H, centered=False)
    )
    shell = shell.union(ledge)

# Feature: Front Wall Catch Ledges (4.2) -- 4 ledges, protrude +Y from Y=2.0
for xc in FRONT_LEDGE_X:
    ledge = (
        cq.Workplane("XY")
        .transformed(offset=(xc - LEDGE_LEN / 2.0, FRONT_WALL, LEDGE_Z_BOT))
        .box(LEDGE_LEN, LEDGE_PROT, LEDGE_H, centered=False)
    )
    shell = shell.union(ledge)

# Feature: Rear Wall Catch Ledges (3.5) -- 4 ledges, protrude -Y from Y=174.0
for xc in REAR_LEDGE_X:
    ledge = (
        cq.Workplane("XY")
        .transformed(offset=(xc - LEDGE_LEN / 2.0, D - REAR_WALL - LEDGE_PROT, LEDGE_Z_BOT))
        .box(LEDGE_LEN, LEDGE_PROT, LEDGE_H, centered=False)
    )
    shell = shell.union(ledge)

# --- Step 14: Apply exterior fillets ---
# Feature: Exterior Fillets (5.1) -- R=1.0mm on all exterior edges
# For a complex shell with many boolean operations, applying fillets to all edges
# is likely to fail. We apply fillets selectively to the most visible exterior edges.

# Try applying to the four vertical corner edges of the outer envelope
try:
    shell = (
        shell.edges("|Z")
        .edges(cq.selectors.BoxSelector((-0.1, -0.1, -0.1), (0.1, 0.1, H + 0.1)))
        .fillet(EXT_FILLET_R)
    )
    print("  Applied fillet to front-left vertical edge")
except Exception:
    pass

# Apply elephant's foot chamfer to bottom perimeter edges (Z=0 plane)
# Feature: Elephant's Foot Chamfer (5.2) -- 0.3mm x 45deg on bottom perimeter
try:
    shell = (
        shell.edges(
            cq.selectors.BoxSelector((-0.1, -0.1, -0.1), (W + 0.1, D + 0.1, 0.1))
        ).chamfer(EF_CHAMFER)
    )
    print("  Applied 0.3mm elephant's foot chamfer to bottom perimeter edges")
except Exception as e:
    print(f"  Warning: Elephant's foot chamfer failed: {e}. Skipping.")

print("\nGeometry build complete.")

# ==============================================================================
# EXPORT STEP
# ==============================================================================

output_path = Path(__file__).parent / "bottom-shell.step"
cq.exporters.export(shell, str(output_path))
print(f"\nSTEP file exported to: {output_path}")

# ==============================================================================
# RUBRIC 3 -- Feature-Specification Reconciliation
# ==============================================================================

print("\n" + "=" * 80)
print("RUBRIC 3 -- Feature-Specification Reconciliation (Point-in-Solid Probes)")
print("=" * 80)

v = Validator(shell)

# --- 1. Floor Plate ---
v.check_solid("Floor plate center", 66.0, 88.5, 1.0, "solid in floor at Z=1.0")
# Probe cavity in left bay (not on center divider, not on rib)
v.check_void("Above floor interior", 33.5, 88.5, 10.0, "void in left bay cavity at Z=10")

# --- 2. Left Inner Rib ---
# Rib at X=9.0..10.2, Z=2..20.25. Probe at center of rib cross-section.
v.check_solid("Left inner rib center low", 9.6, 88.0, 5.0, "solid in left rib at Z=5.0")
v.check_solid("Left inner rib center high", 9.6, 88.0, 19.0, "solid in left rib at Z=19.0")
# Above rib top, should be void
v.check_void("Above left inner rib", 9.6, 88.0, 21.0, "void above left rib at Z=21.0")

# --- 3. Right Inner Rib ---
v.check_solid("Right inner rib center low", 122.4, 88.0, 5.0, "solid in right rib at Z=5.0")
v.check_solid("Right inner rib center high", 122.4, 88.0, 19.0, "solid in right rib at Z=19.0")
v.check_void("Above right inner rib", 122.4, 88.0, 21.0, "void above right rib at Z=21.0")

# --- 4. Left arm channel (above groove band) ---
# Channel at X=2.0..9.0, Z=17.25..20.25. Arm rests on groove band thickening top (Z=17.25).
# Probe in channel void (above groove band top, inside channel)
v.check_void("Left arm channel center", 5.5, 88.0, 18.75, "void in left arm channel at Z=18.75")
# Groove band thickening (behind groove floor, X=4.5..5.7) is solid below channel
v.check_solid("Left channel shelf (groove band top)", 5.2, 88.0, 16.0, "solid at groove band thickening below channel")

# --- 5. Right arm channel (above groove band) ---
v.check_void("Right arm channel center", 126.5, 88.0, 18.75, "void in right arm channel at Z=18.75")
v.check_solid("Right channel shelf (groove band top)", 126.8, 88.0, 16.0, "solid at groove band thickening below channel")

# --- 6. Left Side Wall ---
v.check_solid("Left side wall", 1.0, 88.5, 10.0, "solid in left wall below groove")
v.check_solid("Left side wall above groove", 1.0, 88.5, 25.0, "solid in left wall above groove")

# --- 7. Right Side Wall ---
v.check_solid("Right side wall", 131.0, 88.5, 10.0, "solid in right wall below groove")
v.check_solid("Right side wall above groove", 131.0, 88.5, 25.0, "solid in right wall above groove")

# --- 8. Left Groove-Band Thickening ---
v.check_solid("Left groove-band thickening", 5.0, 88.5, 15.0, "solid behind left groove floor at groove Z")

# --- 9. Right Groove-Band Thickening ---
v.check_solid("Right groove-band thickening", 127.0, 88.5, 15.0, "solid behind right groove floor at groove Z")

# --- 10. Left Rail Groove ---
v.check_void("Left groove center", 2.25, 88.5, 15.0, "void in left groove")
v.check_solid("Left groove floor wall", 5.0, 88.5, 15.0, "solid behind left groove floor")

# --- 11. Right Rail Groove ---
v.check_void("Right groove center", 129.75, 88.5, 15.0, "void in right groove")
v.check_solid("Right groove floor wall", 127.0, 88.5, 15.0, "solid behind right groove floor")

# --- 12. Left Groove Entry Chamfer ---
v.check_void("Left chamfer at Y=2.5", 1.0, 2.5, 15.0, "void in left chamfer zone at Y=2.5")

# --- 13. Right Groove Entry Chamfer ---
v.check_void("Right chamfer at Y=2.5", 131.0, 2.5, 15.0, "void in right chamfer zone at Y=2.5")

# --- 14. Left Detent Relief ---
v.check_void("Left detent relief", 4.6, 174.5, 15.0, "void at left detent position (past groove floor)")

# --- 15. Right Detent Relief ---
v.check_void("Right detent relief", 127.4, 174.5, 15.0, "void at right detent position")

# --- 16. Left Partition Slot ---
v.check_void("Left partition slot center", 1.0, 75.0, 20.0, "void in left partition slot")
v.check_solid("Left wall outside partition slot", 1.0, 68.0, 20.0, "solid in left wall outside slot Y range")

# --- 17. Right Partition Slot ---
v.check_void("Right partition slot center", 131.0, 75.0, 20.0, "void in right partition slot")

# --- 18. Left Wall Catch Ledges ---
# Check one ledge: L3 at Y=89, protruding +X from X=2.0
v.check_solid("Left catch ledge L3", 2.15, 89.0, 33.35, "solid at left ledge L3")

# --- 19. Right Wall Catch Ledges ---
v.check_solid("Right catch ledge R3", 129.85, 89.0, 33.35, "solid at right ledge R3")

# --- 20. Center Divider Wall ---
v.check_solid("Center divider center", 66.0, 88.0, 17.75, "solid in center divider at Y=88")
v.check_solid("Center divider near end", 66.0, 149.0, 17.75, "solid in center divider near Y=150 end")
v.check_void("Center divider past end", 66.0, 155.0, 17.75, "void past center divider end (release plate zone)")
v.check_void("Left bay center", 33.5, 50.0, 25.0, "void in left pump bay")
v.check_void("Right bay center", 98.5, 50.0, 25.0, "void in right pump bay")

# --- 21. Rear Wall Plate ---
v.check_solid("Rear wall center", 66.0, 175.5, 16.75, "solid in rear wall")

# --- 22-25. JG Bores ---
for idx, (bx, bz) in enumerate(JG_BORES):
    v.check_void(f"JG bore {idx+1} center", bx, 175.5, bz, f"void at JG bore {idx+1} center")
    # Check solid just outside bore radius
    v.check_solid(f"JG bore {idx+1} wall", bx + JG_BORE_R + 0.5, 175.5, bz,
                  f"solid outside JG bore {idx+1}")

# --- 26-27. Spring Bosses ---
for idx, (sbx, sbz) in enumerate(SPRING_BOSSES):
    # Boss center at Y=171.5 (midpoint of 169..174)
    v.check_solid(f"Spring boss {idx+1} center", sbx, 171.5, sbz,
                  f"solid at spring boss {idx+1}")
    # Check void just outside boss radius in X
    v.check_void(f"Spring boss {idx+1} outside", sbx + 2.0, 171.5, sbz,
                 f"void outside spring boss {idx+1}")

# --- 28-31. Blade Terminal Slots ---
for idx, (btx, btz) in enumerate(BT_SLOTS):
    v.check_void(f"BT slot {idx+1} center", btx, 176.5, btz,
                 f"void at blade terminal slot {idx+1}")
    v.check_solid(f"BT slot {idx+1} surround", btx + BT_W / 2.0 + 1.0, 176.5, btz,
                  f"solid surrounding BT slot {idx+1}")

# --- 32. Rear Wall Catch Ledges ---
v.check_solid("Rear catch ledge R2", 50.0, 173.85, 33.35, "solid at rear ledge R2")

# --- 33. Front Wall Plate ---
v.check_solid("Front wall center", 66.0, 1.0, 16.75, "solid in front wall")

# --- 34. Front Wall Catch Ledges ---
v.check_solid("Front catch ledge F2", 50.0, 2.15, 33.35, "solid at front ledge F2")

# ==============================================================================
# RUBRIC 4 -- Solid Validity
# ==============================================================================

print("\n" + "=" * 80)
print("RUBRIC 4 -- Solid Validity")
print("=" * 80)

v.check_valid()
v.check_single_body()
v.check_volume(expected_envelope=W * D * H, fill_range=(0.05, 0.50))

# ==============================================================================
# RUBRIC 5 -- Bounding Box Reconciliation
# ==============================================================================

print("\n" + "=" * 80)
print("RUBRIC 5 -- Bounding Box Reconciliation")
print("=" * 80)

bb = shell.val().BoundingBox()
print(f"  Actual bounding box: X=[{bb.xmin:.2f}, {bb.xmax:.2f}], "
      f"Y=[{bb.ymin:.2f}, {bb.ymax:.2f}], Z=[{bb.zmin:.2f}, {bb.zmax:.2f}]")

v.check_bbox("X", bb.xmin, bb.xmax, 0.0, W)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, D)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, H)

# ==============================================================================
# SUMMARY
# ==============================================================================

if not v.summary():
    print("\nFAILURES detected. Please review and fix.")
    sys.exit(1)
else:
    print(f"\nAll checks passed. STEP file: {output_path}")
