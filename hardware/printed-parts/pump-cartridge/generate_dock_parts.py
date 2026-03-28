#!/usr/bin/env python3
"""
Dock Parts — CadQuery STEP generation script.

Generates three STEP files for the permanent dock assembly:
  1. Dock Cradle — U-shaped channel with rails, tube holes, bosses, contacts
  2. Dock Floor Plate — flat plate with snap tabs
  3. Dock Face Frame — rectangular bezel with entry chamfers

Source: planning/parts-dock.md, planning/spatial-resolution.md

Dock Cradle coordinate system:
  Origin: rear-wall outboard face, lower-left corner (Y=0 is rear wall)
  X: width, left to right, 0..160
  Y: depth, rear wall (Y=0) toward front opening (Y=130)
  Z: height, bottom to top, 0..80
  Note: Y=0 is rear wall per feature positions in parts-dock.md.
        Rear wall spans Y=0..7. Front opening at Y=130.

Dock Floor Plate coordinate system:
  Origin: lower-left-front corner
  X: 0..150, Y: 0..120, Z: 0..3 (thickness)

Dock Face Frame coordinate system:
  Origin: lower-left corner of outer (user-facing) surface
  X: 0..170, Y: 0..5 (depth), Z: 0..90
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

import cadquery as cq
from step_validate import Validator

OUTPUT_DIR = Path(__file__).resolve().parent

# ============================================================================
# PART 1: DOCK CRADLE
# ============================================================================

print("""
==============================================================================
FEATURE PLANNING TABLE — Dock Cradle
==============================================================================
| #  | Feature Name              | Mech Function              | Op     | Shape    | Axis | Center/Position              | Dimensions                       |
|----|---------------------------|----------------------------|--------|----------|------|------------------------------|----------------------------------|
|  1 | Left side wall            | Structural enclosure       | Add    | Box      | —    | X:0-7.7 Y:0-130 Z:0-80      | 7.7x130x80                       |
|  2 | Right side wall           | Structural enclosure       | Add    | Box      | —    | X:152.3-160 Y:0-130 Z:0-80  | 7.7x130x80                       |
|  3 | Rear wall                 | Structural + interfaces    | Add    | Box      | —    | X:0-160 Y:0-7 Z:0-80        | 160x7x80                         |
|  4 | Floor ledge (left)        | Supports floor plate       | Add    | Box      | —    | X:7.7-10.4 Y:0-130 Z:0-5    | 2.7x130x5                        |
|  5 | Floor ledge (right)       | Supports floor plate       | Add    | Box      | —    | X:149.6-152.3 Y:0-130 Z:0-5 | 2.7x130x5                        |
|  6 | Left rail groove          | Guides cartridge rail rib  | Remove | Box      | Y    | X:7.7-10.3 Z:32.7-53.3 Y:7-130 | 2.6x123x20.6                 |
|  7 | Right rail groove         | Guides cartridge rail rib  | Remove | Box      | Y    | X:149.7-152.3 Z:32.7-53.3 Y:7-130 | 2.6x123x20.6              |
|  8 | Left groove entry chamfer | Eases cartridge entry      | Remove | Tapered  | Y    | Y:125-130, left groove       | 2.6->5.6mm W, 20.6->26.6mm H    |
|  9 | Right groove entry chamfer| Eases cartridge entry      | Remove | Tapered  | Y    | Y:125-130, right groove      | mirror of left                   |
| 10 | Tube hole H1              | Tube stub pass-through     | Remove | Cylinder | Y    | (46.5, -, 57.8) Y:0-7       | dia 6.6                         |
| 11 | Tube hole H2              | Tube stub pass-through     | Remove | Cylinder | Y    | (46.5, -, 27.8) Y:0-7       | dia 6.6                         |
| 12 | Tube hole H3              | Tube stub pass-through     | Remove | Cylinder | Y    | (113.5, -, 57.8) Y:0-7      | dia 6.6                         |
| 13 | Tube hole H4              | Tube stub pass-through     | Remove | Cylinder | Y    | (113.5, -, 27.8) Y:0-7      | dia 6.6                         |
| 14 | Registration boss A       | Cartridge alignment        | Add    | Cone     | Y    | (31.5, 7-32, 17.8)          | 10mm base->7mm tip, L=25        |
| 15 | Registration boss B       | Cartridge alignment        | Add    | Cone     | Y    | (128.5, 7-32, 67.8)         | 10mm base->7mm tip, L=25        |
| 16 | Blade pocket P1           | Houses blade contact       | Remove | Box      | Y    | (68.0, 2-7, 42.8)           | 12x5x6 (WxDxH)                  |
| 17 | Blade pocket P2           | Houses blade contact       | Remove | Box      | Y    | (80.0, 2-7, 42.8)           | 12x5x6                          |
| 18 | Blade pocket P3           | Houses blade contact       | Remove | Box      | Y    | (92.0, 2-7, 42.8)           | 12x5x6                          |
| 19 | Blade pocket P4           | Houses blade contact       | Remove | Box      | Y    | (104.0, 2-7, 42.8)          | 12x5x6                          |
| 20 | Wire hole W1              | Wire routing               | Remove | Cylinder | Y    | (68.0, 0-2, 42.8)           | dia 3                            |
| 21 | Wire hole W2              | Wire routing               | Remove | Cylinder | Y    | (80.0, 0-2, 42.8)           | dia 3                            |
| 22 | Wire hole W3              | Wire routing               | Remove | Cylinder | Y    | (92.0, 0-2, 42.8)           | dia 3                            |
| 23 | Wire hole W4              | Wire routing               | Remove | Cylinder | Y    | (104.0, 0-2, 42.8)          | dia 3                            |
| 24 | Mounting lug L1           | Enclosure attachment       | Add    | Box      | X    | left wall, Y=40, Z=40       | 10x10x3, protrudes -X           |
| 25 | Mounting lug L2           | Enclosure attachment       | Add    | Box      | X    | left wall, Y=100, Z=40      | 10x10x3, protrudes -X           |
| 26 | Mounting lug L3           | Enclosure attachment       | Add    | Box      | X    | right wall, Y=40, Z=40      | 10x10x3, protrudes +X           |
| 27 | Mounting lug L4           | Enclosure attachment       | Add    | Box      | X    | right wall, Y=100, Z=40     | 10x10x3, protrudes +X           |
| 28 | Snap tab pocket S1        | Floor plate retention      | Remove | Box      | Z    | (80.0, 37.0, 5.0)           | 5.2x5.2x1.2                     |
| 29 | Snap tab pocket S2        | Floor plate retention      | Remove | Box      | Z    | (80.0, 97.0, 5.0)           | 5.2x5.2x1.2                     |
==============================================================================
""")

# --- Dimensions ---
CRADLE_W = 160.0
CRADLE_D = 130.0
CRADLE_H = 80.0
SIDE_WALL_T = 7.7
REAR_WALL_T = 7.0
FLOOR_LEDGE_H = 5.0
LEDGE_STEPIN = 2.7

GROOVE_W = 2.6
GROOVE_H = 20.6
GROOVE_Z_BOT = 32.7
GROOVE_Z_TOP = 53.3
GROOVE_Y_START = REAR_WALL_T  # 7.0
GROOVE_Y_END = CRADLE_D       # 130.0

TUBE_HOLE_D = 6.6
TUBE_POSITIONS = [(46.5, 57.8), (46.5, 27.8), (113.5, 57.8), (113.5, 27.8)]

BOSS_BASE_D = 10.0
BOSS_TIP_D = 7.0
BOSS_LENGTH = 25.0
BOSS_Y_BASE = REAR_WALL_T  # 7.0
BOSS_Y_TIP = BOSS_Y_BASE + BOSS_LENGTH  # 32.0
BOSS_POSITIONS = [(31.5, 17.8), (128.5, 67.8)]

POCKET_W = 12.0
POCKET_H = 6.0
POCKET_DEPTH = 5.0
POCKET_Y_START = 2.0
CONTACT_POSITIONS = [68.0, 80.0, 92.0, 104.0]
CONTACT_Z = 42.8

WIRE_HOLE_D = 3.0

LUG_Y_SIZE = 10.0
LUG_Z_SIZE = 10.0
LUG_X_PROTRUSION = 3.0

SNAP_POCKET_W = 5.2
SNAP_POCKET_D = 5.2
SNAP_POCKET_DEPTH = 1.2
SNAP_POCKET_POSITIONS = [(80.0, 37.0), (80.0, 97.0)]

# --- Build Dock Cradle ---
print("Building Dock Cradle...")

# Left side wall: X:0-7.7, Y:0-130, Z:0-80
left_wall = cq.Workplane("XY").box(SIDE_WALL_T, CRADLE_D, CRADLE_H, centered=False)

# Right side wall: X:152.3-160
right_wall = (
    cq.Workplane("XY")
    .box(SIDE_WALL_T, CRADLE_D, CRADLE_H, centered=False)
    .translate((CRADLE_W - SIDE_WALL_T, 0, 0))
)

# Rear wall: X:0-160, Y:0-7, Z:0-80
rear_wall = cq.Workplane("XY").box(CRADLE_W, REAR_WALL_T, CRADLE_H, centered=False)

# Floor ledge strips
left_ledge = (
    cq.Workplane("XY")
    .box(LEDGE_STEPIN, CRADLE_D, FLOOR_LEDGE_H, centered=False)
    .translate((SIDE_WALL_T, 0, 0))
)
right_ledge = (
    cq.Workplane("XY")
    .box(LEDGE_STEPIN, CRADLE_D, FLOOR_LEDGE_H, centered=False)
    .translate((CRADLE_W - SIDE_WALL_T - LEDGE_STEPIN, 0, 0))
)

cradle = left_wall.union(right_wall).union(rear_wall).union(left_ledge).union(right_ledge)

# --- Rail Grooves ---
# Left groove: X:7.7-10.3, Z:32.7-53.3, Y:7-130
left_groove = (
    cq.Workplane("XY")
    .box(GROOVE_W, GROOVE_Y_END - GROOVE_Y_START, GROOVE_H, centered=False)
    .translate((SIDE_WALL_T, GROOVE_Y_START, GROOVE_Z_BOT))
)
cradle = cradle.cut(left_groove)

# Right groove: X:149.7-152.3
right_groove = (
    cq.Workplane("XY")
    .box(GROOVE_W, GROOVE_Y_END - GROOVE_Y_START, GROOVE_H, centered=False)
    .translate((CRADLE_W - SIDE_WALL_T - GROOVE_W, GROOVE_Y_START, GROOVE_Z_BOT))
)
cradle = cradle.cut(right_groove)

# --- Entry Chamfers on Grooves (Y=125 to Y=130) ---
# Width expands from 2.6mm at Y=125 to 5.6mm at Y=130 (1.5mm per side)
# Height expands from 20.6mm at Y=125 to 26.6mm at Y=130 (3mm top/bottom)
# Use a box cut that's larger than needed, since the groove is already cut
# and we just need to widen the entry. Use a simple trapezoidal approach.
# Approximate with a box for the expanded region at Y=125-130.

CHAMFER_LEN = 5.0  # Y=125 to Y=130
CHAMFER_W_EXPAND = 1.5  # per side
CHAMFER_H_EXPAND = 3.0  # top and bottom

# Left groove center: X=7.7+1.3=9.0, Z=32.7+10.3=43.0
L_GR_CX = SIDE_WALL_T + GROOVE_W / 2  # 9.0
GR_CZ = GROOVE_Z_BOT + GROOVE_H / 2   # 43.0

# Build loft: small rect at Y=125, large rect at Y=130
# Use CadQuery loft on a workplane parallel to XZ at the right Y
left_chamfer = (
    cq.Workplane("XY")
    .transformed(offset=(L_GR_CX, 125.0, GR_CZ))
    .rect(GROOVE_W, GROOVE_H)  # XY workplane: rect in X and Y dims... wrong
)
# Actually CadQuery workplane("XY") at the origin has X=X, Y=Y, Z is extrude.
# For a loft along Y we need sketches on XZ planes at different Y positions.

# Let's use a different approach: build with Solid.makeLoft or use workplane transforms
# The XZ workplane has normal -Y. We want to loft from Y=125 to Y=130.
# On XZ workplane, the first sketch is at Y=0 (worldspace).
# We need to position it at Y=125.

# Simpler approach: cut a box for the full expanded envelope, since the wall is
# only 7.7mm thick and the groove is already in it. The chamfer just needs to
# remove more material at the front.
# At Y=130: groove expands to 5.6mm wide (X) and 26.6mm tall (Z)
# At Y=125: groove is 2.6mm wide and 20.6mm tall (already cut)
# The expansion is 1.5mm per side in X and 3mm per side in Z over 5mm of Y

# Use a wedge-like cut. Since the groove is already cut from Y=7 to Y=130,
# we just need to expand it at the front. Cut a tapered solid.

# For left groove chamfer:
# Build a loft between two rectangular wire profiles
import OCP.BRepBuilderAPI as BRepBuilderAPI
import OCP.BRepOffsetAPI as BRepOffsetAPI
from OCP.gp import gp_Pnt

def make_rect_wire(cx, cy, cz, w, h, normal='Y'):
    """Make a rectangular wire centered at (cx, cy, cz) in the XZ plane at Y=cy."""
    hw, hh = w / 2, h / 2
    if normal == 'Y':
        pts = [
            gp_Pnt(cx - hw, cy, cz - hh),
            gp_Pnt(cx + hw, cy, cz - hh),
            gp_Pnt(cx + hw, cy, cz + hh),
            gp_Pnt(cx - hw, cy, cz + hh),
        ]
    wire_builder = BRepBuilderAPI.BRepBuilderAPI_MakeWire()
    for i in range(4):
        edge = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(pts[i], pts[(i + 1) % 4]).Edge()
        wire_builder.Add(edge)
    return wire_builder.Wire()

def make_loft_cut(cx, z_center, y_start, y_end, w_start, h_start, w_end, h_end):
    """Make a lofted solid between two rectangular profiles along Y axis."""
    wire1 = make_rect_wire(cx, y_start, z_center, w_start, h_start)
    wire2 = make_rect_wire(cx, y_end, z_center, w_end, h_end)
    loft = BRepOffsetAPI.BRepOffsetAPI_ThruSections(True)  # True = solid
    loft.AddWire(wire1)
    loft.AddWire(wire2)
    loft.Build()
    return cq.Shape(loft.Shape())

# Left groove entry chamfer
left_chamfer_shape = make_loft_cut(
    cx=L_GR_CX, z_center=GR_CZ,
    y_start=125.0, y_end=130.0,
    w_start=GROOVE_W, h_start=GROOVE_H,
    w_end=GROOVE_W + 2 * CHAMFER_W_EXPAND, h_end=GROOVE_H + 2 * CHAMFER_H_EXPAND
)
cradle = cradle.cut(cq.Workplane("XY").newObject([left_chamfer_shape]))

# Right groove entry chamfer
R_GR_CX = CRADLE_W - SIDE_WALL_T - GROOVE_W / 2  # 151.0
right_chamfer_shape = make_loft_cut(
    cx=R_GR_CX, z_center=GR_CZ,
    y_start=125.0, y_end=130.0,
    w_start=GROOVE_W, h_start=GROOVE_H,
    w_end=GROOVE_W + 2 * CHAMFER_W_EXPAND, h_end=GROOVE_H + 2 * CHAMFER_H_EXPAND
)
cradle = cradle.cut(cq.Workplane("XY").newObject([right_chamfer_shape]))

# --- Tube Stub Through-Holes ---
for tx, tz in TUBE_POSITIONS:
    hole = (
        cq.Workplane("XZ")
        .center(tx, tz)
        .circle(TUBE_HOLE_D / 2)
        .extrude(-REAR_WALL_T)  # XZ normal is -Y; -extrude goes +Y direction (Y:0 to 7)
    )
    cradle = cradle.cut(hole)

# --- Registration Bosses ---
for bx, bz in BOSS_POSITIONS:
    cone = cq.Solid.makeCone(
        BOSS_BASE_D / 2, BOSS_TIP_D / 2, BOSS_LENGTH,
        pnt=cq.Vector(bx, BOSS_Y_BASE, bz),
        dir=cq.Vector(0, 1, 0)
    )
    cradle = cradle.union(cq.Workplane("XY").newObject([cone]))

# --- Blade Contact Pockets ---
for cx in CONTACT_POSITIONS:
    pocket = (
        cq.Workplane("XY")
        .box(POCKET_W, POCKET_DEPTH, POCKET_H, centered=False)
        .translate((cx - POCKET_W / 2, POCKET_Y_START, CONTACT_Z - POCKET_H / 2))
    )
    cradle = cradle.cut(pocket)

# --- Wire Routing Holes ---
for cx in CONTACT_POSITIONS:
    wire_hole = (
        cq.Workplane("XZ")
        .center(cx, CONTACT_Z)
        .circle(WIRE_HOLE_D / 2)
        .extrude(-POCKET_Y_START)  # XZ normal -Y; -extrude goes +Y (Y:0 to 2)
    )
    cradle = cradle.cut(wire_hole)

# --- Mounting Lugs ---
# Each lug is a rectangular tab with a 4mm through-hole along X
LUG_CONFIGS = [
    # (x_start, y_center, z_center) - x_start is where lug starts
    (-LUG_X_PROTRUSION, 40.0, 40.0),     # L1: left, X=-3 to 0
    (-LUG_X_PROTRUSION, 100.0, 40.0),    # L2: left
    (CRADLE_W, 40.0, 40.0),              # L3: right, X=160 to 163
    (CRADLE_W, 100.0, 40.0),             # L4: right
]

for x_start, yc, zc in LUG_CONFIGS:
    lug = (
        cq.Workplane("XY")
        .box(LUG_X_PROTRUSION, LUG_Y_SIZE, LUG_Z_SIZE, centered=False)
        .translate((x_start, yc - LUG_Y_SIZE / 2, zc - LUG_Z_SIZE / 2))
    )
    cradle = cradle.union(lug)

    # Through-hole: 4mm diameter along X through the lug
    # Create cylinder at lug center, along X axis
    hole_cyl = cq.Solid.makeCylinder(
        2.0,  # radius
        LUG_X_PROTRUSION + 0.2,  # length (slightly longer to ensure through-cut)
        pnt=cq.Vector(x_start - 0.1, yc, zc),
        dir=cq.Vector(1, 0, 0)
    )
    cradle = cradle.cut(cq.Workplane("XY").newObject([hole_cyl]))

# --- Snap Tab Pockets ---
for sx, sy in SNAP_POCKET_POSITIONS:
    pocket = (
        cq.Workplane("XY")
        .box(SNAP_POCKET_W, SNAP_POCKET_D, SNAP_POCKET_DEPTH, centered=False)
        .translate((sx - SNAP_POCKET_W / 2, sy - SNAP_POCKET_D / 2,
                    FLOOR_LEDGE_H - SNAP_POCKET_DEPTH))
    )
    cradle = cradle.cut(pocket)

# Export cradle
cradle_path = str(OUTPUT_DIR / "dock-cradle.step")
cq.exporters.export(cradle, cradle_path)
print(f"Exported: {cradle_path}")

# ============================================================================
# PART 2: DOCK FLOOR PLATE
# ============================================================================

print("""
==============================================================================
FEATURE PLANNING TABLE — Dock Floor Plate
==============================================================================
| #  | Feature Name       | Mech Function           | Op     | Shape  | Axis | Center/Position        | Dimensions          |
|----|--------------------|-------------------------|--------|--------|------|------------------------|---------------------|
|  1 | Flat plate body    | Sliding surface         | Add    | Box    | —    | X:0-150 Y:0-120 Z:0-3 | 150x120x3           |
|  2 | Snap tab S1        | Retention in cradle     | Add    | Box    | Z    | (75,30) Z:-1 to 0      | 5x5x1               |
|  3 | Snap tab S2        | Retention in cradle     | Add    | Box    | Z    | (75,90) Z:-1 to 0      | 5x5x1               |
|  4 | Edge chamfers      | Eases cartridge sliding | Remove | Chamfer| —    | All top edges           | 0.5mm x 45deg       |
==============================================================================
""")

PLATE_W = 150.0
PLATE_D = 120.0
PLATE_H = 3.0
SNAP_TAB_SIZE = 5.0
SNAP_TAB_H = 1.0

print("Building Dock Floor Plate...")

floor_plate = cq.Workplane("XY").box(PLATE_W, PLATE_D, PLATE_H, centered=False)

# Chamfer top edges (0.5mm x 45deg) - top face perimeter edges
floor_plate = floor_plate.edges(">Z").chamfer(0.5)

# Snap tabs on bottom face (Z=0), protruding downward
for tx, ty in [(75.0, 30.0), (75.0, 90.0)]:
    tab = (
        cq.Workplane("XY")
        .box(SNAP_TAB_SIZE, SNAP_TAB_SIZE, SNAP_TAB_H, centered=False)
        .translate((tx - SNAP_TAB_SIZE / 2, ty - SNAP_TAB_SIZE / 2, -SNAP_TAB_H))
    )
    floor_plate = floor_plate.union(tab)

plate_path = str(OUTPUT_DIR / "dock-floor-plate.step")
cq.exporters.export(floor_plate, plate_path)
print(f"Exported: {plate_path}")

# ============================================================================
# PART 3: DOCK FACE FRAME
# ============================================================================

print("""
==============================================================================
FEATURE PLANNING TABLE — Dock Face Frame
==============================================================================
| #  | Feature Name       | Mech Function           | Op     | Shape    | Axis | Center/Position        | Dimensions              |
|----|--------------------|-------------------------|--------|----------|------|------------------------|-------------------------|
|  1 | Frame body         | Structural bezel        | Add    | Box      | —    | X:0-170 Y:0-5 Z:0-90  | 170x5x90                |
|  2 | Inner opening      | Cartridge pass-through  | Remove | Loft     | Y    | center X:85 Z:45       | 142x72 at Y=5, 147.8x77.8 at Y=0 |
|  3 | Outer edge fillets | Cosmetic finish         | Modify | Fillet   | —    | Outer Y-parallel edges  | 1.5mm radius            |
==============================================================================
""")

FRAME_W = 170.0
FRAME_D = 5.0
FRAME_H = 90.0
OPENING_W = 142.0
OPENING_H = 72.0
OPENING_X_START = 14.0
OPENING_Z_START = 9.0
CHAMFER_EXPAND = 2.9  # 5 * tan(30deg) = 2.887

print("Building Dock Face Frame...")

# Full rectangular block
face_frame = cq.Workplane("XY").box(FRAME_W, FRAME_D, FRAME_H, centered=False)

# Inner opening with entry chamfer as a loft:
# At Y=0 (outer face): 147.8 x 77.8 (larger)
# At Y=5 (inner face): 142 x 72 (smaller)
opening_cx = FRAME_W / 2  # 85.0
opening_cz = FRAME_H / 2  # 45.0
outer_w = OPENING_W + 2 * CHAMFER_EXPAND  # 147.8
outer_h = OPENING_H + 2 * CHAMFER_EXPAND  # 77.8

# Build loft using OCP directly
chamfer_opening = make_loft_cut(
    cx=opening_cx, z_center=opening_cz,
    y_start=0.0, y_end=FRAME_D,
    w_start=outer_w, h_start=outer_h,
    w_end=OPENING_W, h_end=OPENING_H
)
face_frame = face_frame.cut(cq.Workplane("XY").newObject([chamfer_opening]))

# Outer edge fillets (1.5mm on edges parallel to Y = the depth edges on outer perimeter)
try:
    face_frame = face_frame.edges("|Y").fillet(1.5)
except Exception as e:
    print(f"  Warning: Could not apply Y-parallel fillets: {e}")
    # Try a smaller fillet
    try:
        face_frame = face_frame.edges("|Y").fillet(1.0)
    except Exception as e2:
        print(f"  Warning: Could not apply fillets at all: {e2}")

frame_path = str(OUTPUT_DIR / "dock-face-frame.step")
cq.exporters.export(face_frame, frame_path)
print(f"Exported: {frame_path}")


# ============================================================================
# VALIDATION — Dock Cradle
# ============================================================================

print("\n" + "=" * 60)
print("VALIDATION — Dock Cradle")
print("=" * 60)

v1 = Validator(cradle)

# --- Walls ---
v1.check_solid("Left wall mid", 3.0, 65.0, 60.0, "solid in left side wall")
v1.check_solid("Right wall mid", 157.0, 65.0, 60.0, "solid in right side wall")
# Rear wall: probe a point not on any hole/pocket (X=20, Z=70 is clear)
v1.check_solid("Rear wall solid", 20.0, 3.5, 70.0, "solid in rear wall (clear area)")
v1.check_void("Interior void", 80.0, 65.0, 40.0, "void in dock interior")

# --- Floor ledge ---
v1.check_solid("Left floor ledge", 9.0, 65.0, 2.5, "solid in left ledge")
v1.check_solid("Right floor ledge", 151.0, 65.0, 2.5, "solid in right ledge")
v1.check_void("Above ledge interior", 80.0, 65.0, 3.0, "void above ledge in interior")

# --- Rail grooves ---
v1.check_void("Left groove center", 9.0, 70.0, 43.0, "void in left rail groove")
v1.check_void("Right groove center", 151.0, 70.0, 43.0, "void in right rail groove")
# Groove closed at rear (Y=7) — wall is solid there below groove
v1.check_solid("Left groove rear stop", 9.0, 6.5, 43.0, "solid at rear wall blocking groove")
# Above groove (Z=53.3 + 1 = 54.3): should be solid in left wall
v1.check_solid("Left wall above groove", 3.0, 70.0, 54.3, "solid in left wall above groove")
# Below groove (Z=32.7 - 1 = 31.7): solid in left wall
v1.check_solid("Left wall below groove", 3.0, 70.0, 31.7, "solid in left wall below groove")

# Entry chamfer: at Y=128, groove should be wider than 2.6mm
# Left groove chamfer: at Y=128, 60% through chamfer, expansion ~ 0.9mm per side
# Groove at Y=128: X from ~7.7-0.9=6.8 to ~10.3+0.9=11.2. But X=6.8 is inside the wall (0-7.7).
# The chamfer cuts INTO the wall, so at X=7.2 (inside wall material), Y=128, Z=43: should be void
v1.check_void("Left groove chamfer expanded", 7.2, 129.0, 43.0,
              "void at expanded chamfer zone of left groove near front")
# At Y=120 (before chamfer region), X=7.2 should be solid (wall)
v1.check_solid("Left wall pre-chamfer", 7.2, 120.0, 43.0,
               "solid in left wall before chamfer zone")

# --- Tube holes ---
for i, (tx, tz) in enumerate(TUBE_POSITIONS):
    v1.check_void(f"Tube hole H{i+1} center", tx, 3.5, tz,
                  f"void at tube hole H{i+1} center")
    v1.check_solid(f"Tube hole H{i+1} wall", tx + TUBE_HOLE_D / 2 + 1.5, 3.5, tz,
                   f"solid outside tube hole H{i+1}")

# --- Registration bosses ---
for i, (bx, bz) in enumerate(BOSS_POSITIONS):
    label = "A" if i == 0 else "B"
    mid_y = (BOSS_Y_BASE + BOSS_Y_TIP) / 2  # 19.5
    v1.check_solid(f"Reg boss {label} center", bx, mid_y, bz,
                   f"solid at boss {label} center")
    v1.check_void(f"Reg boss {label} outside tip", bx + BOSS_TIP_D / 2 + 1.0,
                  BOSS_Y_TIP, bz, f"void outside boss {label} tip")

# --- Blade contact pockets ---
for i, cx in enumerate(CONTACT_POSITIONS):
    v1.check_void(f"Blade pocket P{i+1} center", cx, 4.5, CONTACT_Z,
                  f"void at blade pocket P{i+1} center")
    v1.check_solid(f"Blade pocket P{i+1} wall", cx, 4.5,
                   CONTACT_Z + POCKET_H / 2 + 1.0,
                   f"solid above blade pocket P{i+1}")

# --- Wire routing holes ---
for i, cx in enumerate(CONTACT_POSITIONS):
    v1.check_void(f"Wire hole W{i+1} center", cx, 1.0, CONTACT_Z,
                  f"void at wire hole W{i+1}")

# --- Mounting lugs ---
# L1: X=-3 to 0, Y=35-45, Z=35-45. Center at (-1.5, 40, 40). Hole at center.
# Check solid offset from hole center, and void at hole center.
v1.check_solid("Lug L1 body", -1.5, 43.0, 43.0, "solid in lug L1 body")
v1.check_void("Lug L1 hole", -1.5, 40.0, 40.0, "void at lug L1 hole center")
v1.check_solid("Lug L2 body", -1.5, 103.0, 43.0, "solid in lug L2 body")
v1.check_void("Lug L2 hole", -1.5, 100.0, 40.0, "void at lug L2 hole center")
v1.check_solid("Lug L3 body", 161.5, 43.0, 43.0, "solid in lug L3 body")
v1.check_void("Lug L3 hole", 161.5, 40.0, 40.0, "void at lug L3 hole center")
v1.check_solid("Lug L4 body", 161.5, 103.0, 43.0, "solid in lug L4 body")
v1.check_void("Lug L4 hole", 161.5, 100.0, 40.0, "void at lug L4 hole center")

# --- Snap tab pockets ---
for i, (sx, sy) in enumerate(SNAP_POCKET_POSITIONS):
    v1.check_void(f"Snap pocket S{i+1}", sx, sy,
                  FLOOR_LEDGE_H - SNAP_POCKET_DEPTH / 2,
                  f"void at snap pocket S{i+1}")

# --- Bounding box ---
bb1 = cradle.val().BoundingBox()
v1.check_bbox("X", bb1.xmin, bb1.xmax, -3.0, 163.0)
v1.check_bbox("Y", bb1.ymin, bb1.ymax, 0.0, 130.0)
v1.check_bbox("Z", bb1.zmin, bb1.zmax, 0.0, 80.0)

# --- Solid integrity ---
v1.check_valid()
v1.check_single_body()
v1.check_volume(expected_envelope=CRADLE_W * CRADLE_D * CRADLE_H, fill_range=(0.05, 0.5))

if not v1.summary():
    print("\nDock Cradle has failures.")

# ============================================================================
# VALIDATION — Dock Floor Plate
# ============================================================================

print("\n" + "=" * 60)
print("VALIDATION — Dock Floor Plate")
print("=" * 60)

v2 = Validator(floor_plate)

v2.check_solid("Plate body center", 75.0, 60.0, 1.5, "solid at plate center")
v2.check_solid("Plate body corner", 1.0, 1.0, 1.5, "solid near corner")
v2.check_solid("Snap tab S1", 75.0, 30.0, -0.5, "solid at snap tab S1")
v2.check_solid("Snap tab S2", 75.0, 90.0, -0.5, "solid at snap tab S2")
v2.check_void("Below snap tab S1", 75.0, 30.0, -1.5, "void below snap tab S1")
v2.check_void("Top edge chamfer corner", 0.0, 0.0, 3.0, "void at chamfered top corner")

bb2 = floor_plate.val().BoundingBox()
v2.check_bbox("X", bb2.xmin, bb2.xmax, 0.0, 150.0)
v2.check_bbox("Y", bb2.ymin, bb2.ymax, 0.0, 120.0)
v2.check_bbox("Z", bb2.zmin, bb2.zmax, -1.0, 3.0)

v2.check_valid()
v2.check_single_body()
v2.check_volume(expected_envelope=PLATE_W * PLATE_D * PLATE_H, fill_range=(0.8, 1.2))

if not v2.summary():
    print("\nDock Floor Plate has failures.")

# ============================================================================
# VALIDATION — Dock Face Frame
# ============================================================================

print("\n" + "=" * 60)
print("VALIDATION — Dock Face Frame")
print("=" * 60)

v3 = Validator(face_frame)

# Frame body solid checks (in frame material, not in opening)
v3.check_solid("Frame left rail", 5.0, 2.5, 45.0, "solid in left frame rail")
v3.check_solid("Frame right rail", 165.0, 2.5, 45.0, "solid in right frame rail")
v3.check_solid("Frame top rail", 85.0, 2.5, 87.0, "solid in top frame rail")
v3.check_solid("Frame bottom rail", 85.0, 2.5, 3.0, "solid in bottom frame rail")

# Inner opening void
v3.check_void("Opening center", 85.0, 2.5, 45.0, "void at frame opening center")
v3.check_void("Opening at inner face", 85.0, 4.5, 45.0, "void at inner face (Y=4.5)")

# Entry chamfer: at Y=0 (outer), opening is ~147.8mm wide centered at X=85
# At Y=0.5, X=12 should be void (within chamfered opening: 85-147.8/2=85-73.9=11.1)
v3.check_void("Chamfer outer face X", 12.0, 0.5, 45.0,
              "void in chamfer zone near outer face")
# At Y=4.5, X=12 should be solid (outside 142mm inner opening: 85-71=14, so X=12 is outside)
v3.check_solid("Inner face frame edge", 12.0, 4.5, 45.0,
               "solid at inner face outside 142mm opening")

# Chamfer Z direction: at Y=0.5, Z=7.0 should be void (45-77.8/2=45-38.9=6.1)
v3.check_void("Chamfer outer face Z", 85.0, 0.5, 7.0,
              "void in chamfer zone Z direction near outer face")
# At Y=4.5, Z=7.0 should be solid (outside 72mm inner: 45-36=9.0, so Z=7 is outside)
v3.check_solid("Inner face frame Z edge", 85.0, 4.5, 7.0,
               "solid at inner face outside 72mm opening Z")

bb3 = face_frame.val().BoundingBox()
v3.check_bbox("X", bb3.xmin, bb3.xmax, 0.0, 170.0)
v3.check_bbox("Y", bb3.ymin, bb3.ymax, 0.0, 5.0)
v3.check_bbox("Z", bb3.zmin, bb3.zmax, 0.0, 90.0)

v3.check_valid()
v3.check_single_body()
v3.check_volume(expected_envelope=FRAME_W * FRAME_D * FRAME_H, fill_range=(0.2, 0.9))

if not v3.summary():
    print("\nDock Face Frame has failures.")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 60)
all_pass = v1.all_passed and v2.all_passed and v3.all_passed
if all_pass:
    print("ALL PARTS: ALL CHECKS PASSED")
else:
    total_fails = v1.fail_count + v2.fail_count + v3.fail_count
    print(f"TOTAL FAILURES: {total_fails}")
print("=" * 60)

if not all_pass:
    sys.exit(1)
