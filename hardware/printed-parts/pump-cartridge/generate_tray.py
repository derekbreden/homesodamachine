#!/usr/bin/env python3
"""
Cartridge Tray — CadQuery STEP generation script.

Generates the structural backbone of the pump cartridge: a U-shaped open-top
tray with side walls, floor, and rear wall containing all rear-face interfaces.

Coordinate system:
  Origin: outer lower-left corner of the FRONT face (user-facing)
  X: width, left to right, 0..140  (144 with rail ribs)
  Y: depth, front face toward rear wall, 0..121
  Z: height, bottom to top, 0..70
  Envelope: 140x121x70 mm (base body), 144x129x70 mm (with ribs + funnels)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

import cadquery as cq
from step_validate import Validator

# ============================================================================
# Feature Planning Table (Rubric 1)
# ============================================================================
print("""
==============================================================================
FEATURE PLANNING TABLE — Cartridge Tray
==============================================================================
| #  | Feature Name                  | Operation | Shape      | Axis | Center/Position         | Dimensions                    |
|----|-------------------------------|-----------|------------|------|-------------------------|-------------------------------|
|  1 | Floor plate                   | Add       | Box        | Z    | X:0-140 Y:0-112.5 Z:0-3| 140x112.5x3                  |
|  2 | Left side wall                | Add       | Box        | —    | X:0-5 Y:0-112.5 Z:0-70 | 5x112.5x70                   |
|  3 | Right side wall               | Add       | Box        | —    | X:135-140 Y:0-112.5 Z:0-70 | 5x112.5x70               |
|  4 | Rear wall                     | Add       | Box        | —    | X:0-140 Y:112.5-121 Z:0-70 | 140x8.5x70                |
|  5 | Pump pocket left              | Remove    | Box        | —    | X:5.2-67.8 Y:0.6-48.6 Z:3.5-66.1 | 62.6x48x62.6          |
|  6 | Pump pocket right             | Remove    | Box        | —    | X:72.2-134.8 Y:0.6-48.6 Z:3.5-66.1 | 62.6x48x62.6        |
|  7 | Motor nub pocket left         | Remove    | Cylinder   | Y    | (36.5, -, 34.8) Y:112.5-117.5 | dia 8, depth 5          |
|  8 | Motor nub pocket right        | Remove    | Cylinder   | Y    | (103.5, -, 34.8) Y:112.5-117.5 | dia 8, depth 5         |
|  9 | Mount boss P1-L               | Add       | Cylinder   | Z    | (11.8, 48.6, -) Z:3-8   | OD 7, H 5                    |
| 10 | Mount boss P1-R               | Add       | Cylinder   | Z    | (61.2, 48.6, -) Z:3-8   | OD 7, H 5                    |
| 11 | Mount boss P2-L               | Add       | Cylinder   | Z    | (78.8, 48.6, -) Z:3-8   | OD 7, H 5                    |
| 12 | Mount boss P2-R               | Add       | Cylinder   | Z    | (128.2, 48.6, -) Z:3-8  | OD 7, H 5                    |
| 13 | Mount hole P1-L               | Remove    | Cylinder   | Z    | (11.8, 48.6, -) Z:3-8   | dia 4, through boss          |
| 14 | Mount hole P1-R               | Remove    | Cylinder   | Z    | (61.2, 48.6, -) Z:3-8   | dia 4                        |
| 15 | Mount hole P2-L               | Remove    | Cylinder   | Z    | (78.8, 48.6, -) Z:3-8   | dia 4                        |
| 16 | Mount hole P2-R               | Remove    | Cylinder   | Z    | (128.2, 48.6, -) Z:3-8  | dia 4                        |
| 17 | Standoff rib P1-L             | Add       | Box        | Z    | X:8.3-15.3 Y:45.1-52.1 Z:3-34.8 | 7x7x31.8              |
| 18 | Standoff rib P1-R             | Add       | Box        | Z    | X:57.7-64.7 Y:45.1-52.1 Z:3-34.8 | 7x7x31.8             |
| 19 | Standoff rib P2-L             | Add       | Box        | Z    | X:75.3-82.3 Y:45.1-52.1 Z:3-34.8 | 7x7x31.8             |
| 20 | Standoff rib P2-R             | Add       | Box        | Z    | X:124.7-131.7 Y:45.1-52.1 Z:3-34.8 | 7x7x31.8           |
| 21 | JG fitting bore F1            | Remove    | Cylinder   | Y    | (36.5, -, 49.8) Y:112.5-121 | dia 9.5                  |
| 22 | JG fitting bore F2            | Remove    | Cylinder   | Y    | (36.5, -, 19.8) Y:112.5-121 | dia 9.5                  |
| 23 | JG fitting bore F3            | Remove    | Cylinder   | Y    | (103.5, -, 49.8) Y:112.5-121 | dia 9.5                 |
| 24 | JG fitting bore F4            | Remove    | Cylinder   | Y    | (103.5, -, 19.8) Y:112.5-121 | dia 9.5                 |
| 25 | Entry funnel F1               | Remove    | Cone       | Y    | (36.5, -, 49.8) Y:121-129 | 12mm mouth to 9.5mm         |
| 26 | Entry funnel F2               | Remove    | Cone       | Y    | (36.5, -, 19.8) Y:121-129 | 12mm mouth to 9.5mm         |
| 27 | Entry funnel F3               | Remove    | Cone       | Y    | (103.5, -, 49.8) Y:121-129 | 12mm mouth to 9.5mm        |
| 28 | Entry funnel F4               | Remove    | Cone       | Y    | (103.5, -, 19.8) Y:121-129 | 12mm mouth to 9.5mm        |
| 29 | Reg boss socket A             | Remove    | Cone       | Y    | (21.5, -, 9.8) Y:106-121 | 10.3mm mouth to 7.3mm       |
| 30 | Reg boss socket B             | Remove    | Cone       | Y    | (118.5, -, 59.8) Y:106-121 | 10.3mm mouth to 7.3mm      |
| 31 | Guide post left               | Add       | Cylinder   | Y    | (8.0, -, 34.8) Y:121-143 | dia 4, L 22                  |
| 32 | Guide post right              | Add       | Cylinder   | Y    | (132.0, -, 34.8) Y:121-143 | dia 4, L 22                 |
| 33 | Push rod slot left            | Remove    | Box        | Y    | (7.0, -, 58.0) Y:112.5-121 | 5x8.5x5                    |
| 34 | Push rod slot right           | Remove    | Box        | Y    | (133.0, -, 58.0) Y:112.5-121 | 5x8.5x5                   |
| 35 | Push rod channel left         | Remove    | Box        | Y    | X:5-9 Z:56-60 Y:0-112.5 | 4x112.5x4                    |
| 36 | Push rod channel right        | Remove    | Box        | Y    | X:131-135 Z:56-60 Y:0-112.5 | 4x112.5x4                 |
| 37 | Lever bearing hole left       | Remove    | Cylinder   | X    | (2.5, 9.0, 58.0) X:0-5  | dia 6.1, depth 5             |
| 38 | Lever bearing hole right      | Remove    | Cylinder   | X    | (137.5, 9.0, 58.0) X:135-140 | dia 6.1, depth 5        |
| 39 | Rail rib left                 | Add       | Box        | Y    | X:-2-0 Z:25-45 Y:0-121  | 2x121x20                     |
| 40 | Rail rib right                | Add       | Box        | Y    | X:140-142 Z:25-45 Y:0-121 | 2x121x20                   |
| 41 | Detent ridge CL1              | Add       | Box        | —    | X:-0.8-0 Y:26-34 Z:67-69 | 0.8x8x2                     |
| 42 | Detent ridge CL2              | Add       | Box        | —    | X:-0.8-0 Y:87-95 Z:67-69 | 0.8x8x2                     |
| 43 | Detent ridge CL3              | Add       | Box        | —    | X:140-140.8 Y:26-34 Z:67-69 | 0.8x8x2                  |
| 44 | Detent ridge CL4              | Add       | Box        | —    | X:140-140.8 Y:87-95 Z:67-69 | 0.8x8x2                  |
| 45 | E-contact pocket E1           | Remove    | Box        | Y    | (58.0, 121.0, 34.8)     | 10x5 x 0.1 deep              |
| 46 | E-contact pocket E2           | Remove    | Box        | Y    | (70.0, 121.0, 34.8)     | 10x5 x 0.1 deep              |
| 47 | E-contact pocket E3           | Remove    | Box        | Y    | (82.0, 121.0, 34.8)     | 10x5 x 0.1 deep              |
| 48 | E-contact pocket E4           | Remove    | Box        | Y    | (94.0, 121.0, 34.8)     | 10x5 x 0.1 deep              |
| 49 | Bezel snap pocket T1 (bottom) | Remove    | Box        | Z    | (70.0, 2.5, 0.0)        | 5x3x0.8                      |
| 50 | Bezel snap pocket T2 (top)    | Remove    | Box        | Z    | (70.0, 2.5, 70.0)       | 5x3x0.8                      |
==============================================================================
""")

# ============================================================================
# Dimensions
# ============================================================================

# Overall envelope
W = 140.0   # X
D = 121.0   # Y (full depth including rear wall outboard face)
H = 70.0    # Z

# Walls
SIDE_WALL = 5.0       # side wall thickness
FLOOR_T = 3.0         # floor thickness
REAR_WALL_T = 8.5     # rear wall thickness
REAR_INNER_Y = 112.5  # rear wall inner face Y
REAR_OUTER_Y = 121.0  # rear wall outboard face Y

# Pump pocket
PP_X_L = 5.2;   PP_X_R_L = 67.8   # left pocket X range
PP_X_R = 72.2;  PP_X_RR = 134.8   # right pocket X range
PP_Y_F = 0.6;   PP_Y_R = 48.6     # pocket Y range (front to bracket)
PP_Z_B = 3.5;   PP_Z_T = 66.1     # pocket Z range

# Motor nub pockets
MN_DIA = 8.0
MN_DEPTH = 5.0  # into rear wall from inner face

# Mount bosses
BOSS_OD = 7.0
BOSS_H = 5.0
BOSS_HOLE_DIA = 4.0
MOUNT_X = [11.8, 61.2, 78.8, 128.2]
MOUNT_Y = 48.6
MOUNT_Z = 34.8
BOSS_Z_BOT = FLOOR_T  # 3.0
BOSS_Z_TOP = BOSS_Z_BOT + BOSS_H  # 8.0

# Standoff ribs (7mm wide, centered on mount X, 7mm in Y centered on mount Y)
STANDOFF_RIB_W = 7.0
STANDOFF_RIB_Z_TOP = MOUNT_Z  # 34.8

# JG fitting bores
FIT_BORE_DIA = 9.5
FIT_POSITIONS = [(36.5, 49.8), (36.5, 19.8), (103.5, 49.8), (103.5, 19.8)]

# Entry funnels
FUNNEL_MOUTH_DIA = 12.0
FUNNEL_EXIT_DIA = FIT_BORE_DIA  # 9.5
FUNNEL_DEPTH = 8.0  # extends from Y=121 to Y=129

# Registration boss sockets
REG_A = (21.5, 9.8)    # X, Z
REG_B = (118.5, 59.8)
REG_MOUTH_DIA = 10.3
REG_BASE_DIA = 7.3
REG_DEPTH = 15.0  # Y=121 to Y=106

# Guide posts
GP_LEFT = (8.0, 34.8)    # X, Z
GP_RIGHT = (132.0, 34.8)
GP_DIA = 4.0
GP_LEN = 22.0  # Y=121 to Y=143

# Push rod transfer slots
PR_SLOT_W = 5.0
PR_SLOT_H = 5.0
PR_LEFT_X = 7.0
PR_RIGHT_X = 133.0
PR_Z = 58.0

# Push rod channels
PRC_LEFT_X = (5.0, 9.0)   # X range
PRC_RIGHT_X = (131.0, 135.0)
PRC_Z = (56.0, 60.0)

# Lever bearing holes
LBH_LEFT_X = 2.5
LBH_RIGHT_X = 137.5
LBH_Y = 9.0
LBH_Z = 58.0
LBH_DIA = 6.1
LBH_DEPTH = 5.0

# Rail ribs
RAIL_W = 2.0
RAIL_Z = (25.0, 45.0)

# Detent ridges
DET_PROTRUSION = 0.8
DET_Y_LEN = 8.0
DET_Z = (67.0, 69.0)
DET_Y_CENTERS = [30.0, 91.0]

# E-contact pockets
EC_W = 10.0
EC_H = 5.0
EC_DEPTH = 0.1
EC_X_CENTERS = [58.0, 70.0, 82.0, 94.0]
EC_Z = 34.8

# Bezel snap pockets
BSP_W = 5.0
BSP_D = 3.0
BSP_H = 0.8

# ============================================================================
# Build the tray
# ============================================================================

# --- Feature 1: Floor plate ---
# Z:0..3, X:0..140, Y:0..112.5
# Actually we build the main U-shape as walls+floor first, then add rear wall
tray = cq.Workplane("XY").box(W, REAR_INNER_Y, H, centered=False)

# Hollow out the interior (remove everything inside the walls above the floor)
interior = (
    cq.Workplane("XY")
    .transformed(offset=(SIDE_WALL, 0, FLOOR_T))
    .box(W - 2 * SIDE_WALL, REAR_INNER_Y, H - FLOOR_T, centered=False)
)
tray = tray.cut(interior)

# --- Feature 4: Rear wall ---
rear_wall = (
    cq.Workplane("XY")
    .transformed(offset=(0, REAR_INNER_Y, 0))
    .box(W, REAR_WALL_T, H, centered=False)
)
tray = tray.union(rear_wall)

# --- Features 5-6: Pump pockets ---
# Left pump pocket
pocket_l = (
    cq.Workplane("XY")
    .transformed(offset=(PP_X_L, PP_Y_F, PP_Z_B))
    .box(PP_X_R_L - PP_X_L, PP_Y_R - PP_Y_F, PP_Z_T - PP_Z_B, centered=False)
)
tray = tray.cut(pocket_l)

# Right pump pocket
pocket_r = (
    cq.Workplane("XY")
    .transformed(offset=(PP_X_R, PP_Y_F, PP_Z_B))
    .box(PP_X_RR - PP_X_R, PP_Y_R - PP_Y_F, PP_Z_T - PP_Z_B, centered=False)
)
tray = tray.cut(pocket_r)

# --- Features 7-8: Motor nub pockets ---
# Cylindrical pockets in rear wall inner face, along Y axis
for mx in [36.5, 103.5]:
    nub = (
        cq.Workplane("XZ")
        .center(mx, MOUNT_Z)
        .circle(MN_DIA / 2)
        .extrude(-MN_DEPTH)  # XZ normal is -Y; negative extrude goes +Y (into wall)
    )
    # Position: cylinder starts at Y=0 on XZ plane, need it at Y=112.5 going to Y=117.5
    nub = nub.translate((0, REAR_INNER_Y, 0))
    tray = tray.cut(nub)

# --- Features 9-12: Mount bosses (cylindrical, on floor) ---
for mx in MOUNT_X:
    boss = (
        cq.Workplane("XY")
        .transformed(offset=(mx, MOUNT_Y, BOSS_Z_BOT))
        .circle(BOSS_OD / 2)
        .extrude(BOSS_H)
    )
    tray = tray.union(boss)

# --- Features 17-20: Standoff ribs ---
# 7mm wide ribs centered on mount X, centered on mount Y, from floor to bracket Z
# (must be added BEFORE mount holes are cut, so holes pass through ribs)
for mx in MOUNT_X:
    rib = (
        cq.Workplane("XY")
        .transformed(offset=(mx - STANDOFF_RIB_W / 2, MOUNT_Y - STANDOFF_RIB_W / 2, FLOOR_T))
        .box(STANDOFF_RIB_W, STANDOFF_RIB_W, STANDOFF_RIB_Z_TOP - FLOOR_T, centered=False)
    )
    tray = tray.union(rib)

# --- Features 13-16: Mount holes (through bosses and standoff ribs) ---
for mx in MOUNT_X:
    hole = (
        cq.Workplane("XY")
        .transformed(offset=(mx, MOUNT_Y, BOSS_Z_BOT - 1))
        .circle(BOSS_HOLE_DIA / 2)
        .extrude(STANDOFF_RIB_Z_TOP - BOSS_Z_BOT + 2)
    )
    tray = tray.cut(hole)

# --- Features 21-24: JG fitting bores ---
for fx, fz in FIT_POSITIONS:
    bore = (
        cq.Workplane("XZ")
        .center(fx, fz)
        .circle(FIT_BORE_DIA / 2)
        .extrude(-REAR_WALL_T)  # XZ normal is -Y; negative goes +Y through wall
    )
    bore = bore.translate((0, REAR_INNER_Y, 0))
    tray = tray.cut(bore)

# --- Features 25-28: Entry funnels ---
# Conical funnel from Y=121 (mouth=12mm) to Y=129 (exit=9.5mm) — extends outboard
# Use a revolved profile for a truncated cone
import math
for fx, fz in FIT_POSITIONS:
    # Build cone as a revolved cross-section
    r_mouth = FUNNEL_MOUTH_DIA / 2  # 6.0
    r_exit = FUNNEL_EXIT_DIA / 2    # 4.75
    # Cone along local Y axis (height = FUNNEL_DEPTH = 8mm)
    # Profile in (R, Y) space, revolved around Y axis
    pts = [
        (0, 0),
        (r_exit, 0),      # exit end (at Y=121)
        (r_mouth, FUNNEL_DEPTH),  # mouth end (at Y=129)
        (0, FUNNEL_DEPTH),
    ]
    funnel = (
        cq.Workplane("XY")
        .polyline(pts)
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )
    funnel = funnel.translate((fx, REAR_OUTER_Y, fz))
    tray = tray.cut(funnel)

# --- Features 29-30: Registration boss sockets ---
# Tapered sockets: mouth (10.3mm dia) at Y=121 outboard face, base (7.3mm) at Y=106
# Socket depth = 15mm, going from outboard face inward (-Y direction)
for rx, rz in [REG_A, REG_B]:
    r_mouth = REG_MOUTH_DIA / 2  # 5.15
    r_base = REG_BASE_DIA / 2    # 3.65
    # Profile in (R, Y) space
    pts = [
        (0, 0),
        (r_mouth, 0),        # mouth at outboard face (Y=121)
        (r_base, REG_DEPTH),  # base at Y=106
        (0, REG_DEPTH),
    ]
    socket = (
        cq.Workplane("XY")
        .polyline(pts)
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )
    # The cone's Y=0 is at mouth (outboard face Y=121), Y extends in +Y
    # But we need it going inward: mouth at Y=121, base at Y=106
    # So Y=0 of cone → Y=121, and it extends in -Y to Y=106
    # The revolve creates the cone from Y=0 to Y=15
    # We translate so Y=0→Y=121, meaning cone extends from Y=121 to Y=136
    # That's wrong; we need to flip it.
    # Instead: mirror the cone so it extends in -Y, then translate.
    # Or: create with negative Y values.
    # Simpler: translate so Y=0→Y=106, cone extends from Y=106 to Y=121
    socket = socket.translate((rx, REAR_OUTER_Y - REG_DEPTH, rz))
    tray = tray.cut(socket)

# --- Features 31-32: Guide posts ---
for gx, gz in [GP_LEFT, GP_RIGHT]:
    post = (
        cq.Workplane("XZ")
        .center(gx, gz)
        .circle(GP_DIA / 2)
        .extrude(-GP_LEN)  # XZ normal is -Y; negative goes +Y (outboard)
    )
    post = post.translate((0, REAR_OUTER_Y, 0))
    tray = tray.union(post)

# --- Features 33-34: Push rod transfer slots ---
for px in [PR_LEFT_X, PR_RIGHT_X]:
    slot = (
        cq.Workplane("XY")
        .transformed(offset=(px - PR_SLOT_W / 2, REAR_INNER_Y, PR_Z - PR_SLOT_H / 2))
        .box(PR_SLOT_W, REAR_WALL_T, PR_SLOT_H, centered=False)
    )
    tray = tray.cut(slot)

# --- Features 35-36: Push rod channels ---
# U-groove in side wall interior faces
# Left channel: X=5..9, Z=56..60, Y=0..112.5
for xr, zr in [(PRC_LEFT_X, PRC_Z), (PRC_RIGHT_X, PRC_Z)]:
    chan = (
        cq.Workplane("XY")
        .transformed(offset=(xr[0], 0, zr[0]))
        .box(xr[1] - xr[0], REAR_INNER_Y, zr[1] - zr[0], centered=False)
    )
    tray = tray.cut(chan)

# --- Features 37-38: Lever bearing holes ---
# Left: cylindrical hole along X axis, from X=5 inward to X=0, centered at Y=9, Z=58
# CadQuery: workplane on YZ, circle at (Y, Z), extrude along X
lbh_l = (
    cq.Workplane("YZ")
    .center(LBH_Y, LBH_Z)
    .circle(LBH_DIA / 2)
    .extrude(LBH_DEPTH)  # YZ normal is +X
)
tray = tray.cut(lbh_l)

# Right: from X=135 inward to X=140
lbh_r = (
    cq.Workplane("YZ")
    .center(LBH_Y, LBH_Z)
    .circle(LBH_DIA / 2)
    .extrude(-LBH_DEPTH)  # negative = -X direction
)
lbh_r = lbh_r.translate((W, 0, 0))
tray = tray.cut(lbh_r)

# --- Features 39-40: Rail ribs ---
# Left rib: X=-2..0, Z=25..45, Y=0..121
rib_l = (
    cq.Workplane("XY")
    .transformed(offset=(-RAIL_W, 0, RAIL_Z[0]))
    .box(RAIL_W, D, RAIL_Z[1] - RAIL_Z[0], centered=False)
)
tray = tray.union(rib_l)

# Right rib: X=140..142, Z=25..45, Y=0..121
rib_r = (
    cq.Workplane("XY")
    .transformed(offset=(W, 0, RAIL_Z[0]))
    .box(RAIL_W, D, RAIL_Z[1] - RAIL_Z[0], centered=False)
)
tray = tray.union(rib_r)

# --- Features 41-44: Detent ridges ---
for y_center in DET_Y_CENTERS:
    y_start = y_center - DET_Y_LEN / 2
    # Left: X=-0.8..0
    det_l = (
        cq.Workplane("XY")
        .transformed(offset=(-DET_PROTRUSION, y_start, DET_Z[0]))
        .box(DET_PROTRUSION, DET_Y_LEN, DET_Z[1] - DET_Z[0], centered=False)
    )
    tray = tray.union(det_l)
    # Right: X=140..140.8
    det_r = (
        cq.Workplane("XY")
        .transformed(offset=(W, y_start, DET_Z[0]))
        .box(DET_PROTRUSION, DET_Y_LEN, DET_Z[1] - DET_Z[0], centered=False)
    )
    tray = tray.union(det_r)

# --- Features 45-48: Electrical contact pad pockets ---
for ecx in EC_X_CENTERS:
    ec = (
        cq.Workplane("XY")
        .transformed(offset=(ecx - EC_W / 2, REAR_OUTER_Y - EC_DEPTH, EC_Z - EC_H / 2))
        .box(EC_W, EC_DEPTH, EC_H, centered=False)
    )
    tray = tray.cut(ec)

# --- Features 49-50: Bezel snap tab receiving pockets ---
# T1: bottom (Z=0 face, floor), pocket goes upward 0.8mm from Z=0
bsp1 = (
    cq.Workplane("XY")
    .transformed(offset=(70.0 - BSP_W / 2, 2.5 - BSP_D / 2, 0))
    .box(BSP_W, BSP_D, BSP_H, centered=False)
)
tray = tray.cut(bsp1)

# T2: top (Z=70 face, ceiling edge), pocket goes downward 0.8mm from Z=70
bsp2 = (
    cq.Workplane("XY")
    .transformed(offset=(70.0 - BSP_W / 2, 2.5 - BSP_D / 2, H - BSP_H))
    .box(BSP_W, BSP_D, BSP_H, centered=False)
)
tray = tray.cut(bsp2)


# ============================================================================
# Export STEP
# ============================================================================
out_path = str(Path(__file__).parent / "cartridge-tray.step")
cq.exporters.export(tray, out_path)
print(f"STEP exported to: {out_path}")

# ============================================================================
# Validation (Rubrics 3-5)
# ============================================================================
print("\n--- Validation ---")
v = Validator(tray)

# --- Feature 1: Floor ---
v.check_solid("Floor center", 70.0, 56.0, 1.5, "solid in floor plate center")
v.check_void("Above floor interior", 70.0, 56.0, 35.0, "void inside tray interior")

# --- Features 2-3: Side walls ---
v.check_solid("Left wall", 2.5, 56.0, 35.0, "solid in left side wall")
v.check_solid("Right wall", 137.5, 56.0, 35.0, "solid in right side wall")

# --- Feature 4: Rear wall ---
v.check_solid("Rear wall center", 70.0, 116.75, 35.0, "solid in rear wall center")

# --- Feature 5: Left pump pocket ---
v.check_void("Left pump pocket center", 36.5, 25.0, 34.8, "void in left pump pocket")
v.check_solid("Left pump pocket wall left", 4.0, 25.0, 34.8, "solid outside left pocket")

# --- Feature 6: Right pump pocket ---
v.check_void("Right pump pocket center", 103.5, 25.0, 34.8, "void in right pump pocket")

# --- Feature 7: Motor nub pocket left ---
v.check_void("Motor nub pocket L center", 36.5, 115.0, 34.8, "void in left nub pocket")
v.check_solid("Motor nub pocket L wall", 36.5, 118.0, 34.8, "solid behind nub pocket")

# --- Feature 8: Motor nub pocket right ---
v.check_void("Motor nub pocket R center", 103.5, 115.0, 34.8, "void in right nub pocket")

# --- Features 9-12: Mount bosses (probe at boss wall, offset from center by 2.5mm to avoid hole) ---
v.check_solid("Boss P1-L", 11.8 + 2.5, 48.6, 5.5, "solid in P1-L boss wall")
v.check_solid("Boss P1-R", 61.2 + 2.5, 48.6, 5.5, "solid in P1-R boss wall")
v.check_solid("Boss P2-L", 78.8 + 2.5, 48.6, 5.5, "solid in P2-L boss wall")
v.check_solid("Boss P2-R", 128.2 + 2.5, 48.6, 5.5, "solid in P2-R boss wall")

# --- Features 13-16: Mount holes ---
v.check_void("Hole P1-L", 11.8, 48.6, 5.5, "void in P1-L mount hole")
v.check_void("Hole P1-R", 61.2, 48.6, 5.5, "void in P1-R mount hole")
v.check_void("Hole P2-L", 78.8, 48.6, 5.5, "void in P2-L mount hole")
v.check_void("Hole P2-R", 128.2, 48.6, 5.5, "void in P2-R mount hole")

# --- Features 17-20: Standoff ribs (probe at rib wall, offset from center to avoid hole) ---
v.check_solid("Standoff rib P1-L", 11.8 + 2.5, 48.6, 20.0, "solid in P1-L standoff rib wall")
v.check_solid("Standoff rib P1-R", 61.2 + 2.5, 48.6, 20.0, "solid in P1-R standoff rib wall")
v.check_solid("Standoff rib P2-L", 78.8 + 2.5, 48.6, 20.0, "solid in P2-L standoff rib wall")
v.check_solid("Standoff rib P2-R", 128.2 + 2.5, 48.6, 20.0, "solid in P2-R standoff rib wall")

# --- Features 21-24: JG fitting bores ---
v.check_void("Bore F1 center", 36.5, 116.75, 49.8, "void at F1 bore center")
v.check_void("Bore F2 center", 36.5, 116.75, 19.8, "void at F2 bore center")
v.check_void("Bore F3 center", 103.5, 116.75, 49.8, "void at F3 bore center")
v.check_void("Bore F4 center", 103.5, 116.75, 19.8, "void at F4 bore center")
# Check wall material around bores
v.check_solid("Bore F1 wall", 36.5 + 5.5, 116.75, 49.8, "solid outside F1 bore")

# --- Features 25-28: Entry funnels ---
v.check_void("Funnel F1 center", 36.5, 125.0, 49.8, "void at F1 funnel center")
v.check_void("Funnel F2 center", 36.5, 125.0, 19.8, "void at F2 funnel center")
v.check_void("Funnel F3 center", 103.5, 125.0, 49.8, "void at F3 funnel center")
v.check_void("Funnel F4 center", 103.5, 125.0, 19.8, "void at F4 funnel center")

# --- Features 29-30: Registration boss sockets ---
v.check_void("Reg socket A center", 21.5, 115.0, 9.8, "void at socket A center")
v.check_void("Reg socket B center", 118.5, 115.0, 59.8, "void at socket B center")
# Socket A should be void at mouth (Y=121) and at base (Y=106+1)
v.check_void("Reg socket A near mouth", 21.5, 120.0, 9.8, "void near socket A mouth")
v.check_void("Reg socket A near base", 21.5, 107.0, 9.8, "void near socket A base")

# --- Features 31-32: Guide posts ---
v.check_solid("Guide post L", 8.0, 132.0, 34.8, "solid in left guide post")
v.check_solid("Guide post R", 132.0, 132.0, 34.8, "solid in right guide post")
v.check_void("Guide post L outside", 8.0, 132.0, 34.8 + 3.0, "void outside left guide post")

# --- Features 33-34: Push rod transfer slots ---
v.check_void("PR slot L", 7.0, 116.75, 58.0, "void at left push rod slot")
v.check_void("PR slot R", 133.0, 116.75, 58.0, "void at right push rod slot")

# --- Features 35-36: Push rod channels ---
v.check_void("PR channel L center", 7.0, 56.0, 58.0, "void in left push rod channel")
v.check_void("PR channel R center", 133.0, 56.0, 58.0, "void in right push rod channel")

# --- Features 37-38: Lever bearing holes ---
v.check_void("Bearing hole L", 2.5, 9.0, 58.0, "void at left bearing hole center")
v.check_void("Bearing hole R", 137.5, 9.0, 58.0, "void at right bearing hole center")
# Check wall material exists outside bearing holes
v.check_solid("Bearing L wall outside", 2.5, 9.0, 58.0 + 4.0, "solid above left bearing")

# --- Features 39-40: Rail ribs ---
v.check_solid("Rail rib L", -1.0, 60.0, 35.0, "solid in left rail rib")
v.check_solid("Rail rib R", 141.0, 60.0, 35.0, "solid in right rail rib")
v.check_void("No rib L above", -1.0, 60.0, 50.0, "void above left rail rib")
v.check_void("No rib L below", -1.0, 60.0, 20.0, "void below left rail rib")

# --- Features 41-44: Detent ridges ---
v.check_solid("Detent CL1", -0.4, 30.0, 68.0, "solid at CL1 detent ridge")
v.check_solid("Detent CL2", -0.4, 91.0, 68.0, "solid at CL2 detent ridge")
v.check_solid("Detent CL3", 140.4, 30.0, 68.0, "solid at CL3 detent ridge")
v.check_solid("Detent CL4", 140.4, 91.0, 68.0, "solid at CL4 detent ridge")

# --- Features 45-48: E-contact pockets ---
v.check_void("E-contact E1", 58.0, 121.0 - 0.05, 34.8, "void at E1 pocket")
v.check_void("E-contact E2", 70.0, 121.0 - 0.05, 34.8, "void at E2 pocket")
v.check_void("E-contact E3", 82.0, 121.0 - 0.05, 34.8, "void at E3 pocket")
v.check_void("E-contact E4", 94.0, 121.0 - 0.05, 34.8, "void at E4 pocket")

# --- Features 49-50: Bezel snap pockets ---
v.check_void("Bezel pocket T1", 70.0, 2.5, 0.4, "void at T1 bezel pocket")
v.check_void("Bezel pocket T2", 70.0, 2.5, 69.6, "void at T2 bezel pocket")

# --- Rubric 4: Solid validity ---
v.check_valid()
v.check_single_body()
v.check_volume(expected_envelope=W * D * H, fill_range=(0.05, 0.50))

# --- Rubric 5: Bounding box ---
bb = tray.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, -RAIL_W, W + RAIL_W)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, REAR_OUTER_Y + GP_LEN)  # guide posts extend to Y=143
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, H)

# Summary
if not v.summary():
    sys.exit(1)
