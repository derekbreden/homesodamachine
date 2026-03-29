#!/usr/bin/env python3
"""
Generate the mounting partition STEP file for the pump cartridge.

Source specification: planning/partition-parts.md
Pump geometry: ../../off-the-shelf-parts/kamoer-kphm400/extracted-results/geometry-description.md

Coordinate system:
  Origin: bottom-left-front corner of the plate (Y=0 face on build plate)
  X: plate width, left to right, 0..132.0 mm
  Y: plate thickness (through-thickness), 0..5.0 mm (Y=0 = forward/pump-head face, Y=5.0 = rearward/motor face)
  Z: plate height, bottom to top, 0..63.0 mm
  Envelope (main body): 132 x 5 x 63 mm -> X:[0,132] Y:[0,5] Z:[0,63]
  Registration tabs extend to Y=7.0 (2mm protrusions past rearward face)

Print orientation: flat on build plate (XZ face down, Y=0 face on bed).
  In print coordinates: X=width, Z_print=Y_model (thickness, 5mm tall print), Y_print=Z_model.
  Motor bores and M3 holes are Y-axis through-holes in the model.
  When printed flat, these become vertical cylinders (perfect circles).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from step_validate import Validator

import cadquery as cq

# ============================================================
# Rubric 1 -- Feature Planning Table
# ============================================================
print("""
=== FEATURE PLANNING TABLE ===
| #  | Feature Name            | Mechanical Function                          | Operation | Shape    | Axis | Center (X,Y,Z)       | Dimensions                | Notes                                          |
|----|-------------------------|----------------------------------------------|-----------|----------|------|-----------------------|---------------------------|-------------------------------------------------|
|  1 | Plate body              | Structural plate, pump mount surface         | Base body | Box      | --   | (66,2.5,31.5)         | 132 x 5 x 63 mm          | centered=False from origin                     |
|  2 | Left motor bore         | Motor body pass-through clearance            | Cut       | Cylinder | Y    | (33.5, -, 31.3)      | dia 36.4 mm, thru Y      | +0.2 FDM comp, ~36.2 as-printed               |
|  3 | Right motor bore        | Motor body pass-through clearance            | Cut       | Cylinder | Y    | (98.5, -, 31.3)      | dia 36.4 mm, thru Y      | Mirror of left bore                            |
|  4 | M3 hole L1              | Vib isolation mount clearance                | Cut       | Cylinder | Y    | (9.5, -, 7.3)        | dia 3.6 mm, thru Y       | +0.2 FDM comp                                 |
|  5 | M3 hole L2              | Vib isolation mount clearance                | Cut       | Cylinder | Y    | (57.5, -, 7.3)       | dia 3.6 mm, thru Y       |                                                |
|  6 | M3 hole L3              | Vib isolation mount clearance                | Cut       | Cylinder | Y    | (9.5, -, 55.3)       | dia 3.6 mm, thru Y       |                                                |
|  7 | M3 hole L4              | Vib isolation mount clearance                | Cut       | Cylinder | Y    | (57.5, -, 55.3)      | dia 3.6 mm, thru Y       |                                                |
|  8 | M3 hole R1              | Vib isolation mount clearance                | Cut       | Cylinder | Y    | (74.5, -, 7.3)       | dia 3.6 mm, thru Y       |                                                |
|  9 | M3 hole R2              | Vib isolation mount clearance                | Cut       | Cylinder | Y    | (122.5, -, 7.3)      | dia 3.6 mm, thru Y       |                                                |
| 10 | M3 hole R3              | Vib isolation mount clearance                | Cut       | Cylinder | Y    | (74.5, -, 55.3)      | dia 3.6 mm, thru Y       |                                                |
| 11 | M3 hole R4              | Vib isolation mount clearance                | Cut       | Cylinder | Y    | (122.5, -, 55.3)     | dia 3.6 mm, thru Y       |                                                |
| 12 | Left linkage notch      | Linkage arm pass-through clearance           | Cut       | Box      | Y    | X=2..10, Z=0..5       | 8 x 5(Y) x 5(Z) mm      | 1mm/side clearance on 6mm arm                  |
| 13 | Right linkage notch     | Linkage arm pass-through clearance           | Cut       | Box      | Y    | X=122..130, Z=0..5    | 8 x 5(Y) x 5(Z) mm      | Mirror of left notch                           |
| 14 | Bottom-left reg tab     | Y-direction registration, prevents fore-aft  | Add       | Box      | Y    | X=9..11, Y=5..7, Z=0..2 | 2 x 2 x 2 mm          | Protrudes past rearward face                   |
| 15 | Bottom-right reg tab    | Y-direction registration, prevents fore-aft  | Add       | Box      | Y    | X=121..123, Y=5..7, Z=0..2 | 2 x 2 x 2 mm       | Mirror of bottom-left                          |
| 16 | Top-left reg tab        | Captured by top shell ceiling slot            | Add       | Box      | Y    | X=9..11, Y=5..7, Z=61..63 | 2 x 2 x 2 mm         | Protrudes past rearward face                   |
| 17 | Top-right reg tab       | Captured by top shell ceiling slot            | Add       | Box      | Y    | X=121..123, Y=5..7, Z=61..63 | 2 x 2 x 2 mm    | Mirror of top-left                             |
| 18 | Elephant's foot chamfer | Compensate first-layer flare on build plate  | Cut       | Chamfer  | --   | Bottom perimeter at Y=0 | 0.3 mm x 45 deg           | Y=0 face is on build plate                    |
""")

# ============================================================
# Dimensions from parts spec
# ============================================================

# Plate body
PLATE_W = 132.0   # X
PLATE_T = 5.0     # Y (thickness)
PLATE_H = 63.0    # Z

# Motor bores (Y-axis through-holes)
BORE_DIA = 36.4   # as-drawn (includes +0.2 FDM compensation)
BORE_R = BORE_DIA / 2.0
LEFT_BORE_CX = 33.5
LEFT_BORE_CZ = 31.3
RIGHT_BORE_CX = 98.5
RIGHT_BORE_CZ = 31.3

# M3 through-holes (Y-axis)
M3_DIA = 3.6      # as-drawn (includes +0.2 FDM compensation)
M3_R = M3_DIA / 2.0

M3_HOLES = [
    # (X, Z, label)
    (9.5,   7.3,  "L1"),
    (57.5,  7.3,  "L2"),
    (9.5,   55.3, "L3"),
    (57.5,  55.3, "L4"),
    (74.5,  7.3,  "R1"),
    (122.5, 7.3,  "R2"),
    (74.5,  55.3, "R3"),
    (122.5, 55.3, "R4"),
]

# Linkage arm notches (rectangular cuts from bottom corners)
LEFT_NOTCH_X0 = 2.0
LEFT_NOTCH_X1 = 10.0
RIGHT_NOTCH_X0 = 122.0
RIGHT_NOTCH_X1 = 130.0
NOTCH_Z_HEIGHT = 5.0   # Z = 0..5

# Registration tabs (Y-direction protrusions from rearward face)
TAB_W = 2.0       # X extent
TAB_DEPTH = 2.0   # Y protrusion past plate (Y=5..7)
TAB_H = 2.0       # Z extent

# Bottom tabs: Z = 0..2
# Top tabs: Z = 61..63
BL_TAB_X0 = 9.0
BR_TAB_X0 = 121.0
TL_TAB_X0 = 9.0
TR_TAB_X0 = 121.0

# Elephant's foot chamfer
EF_CHAMFER = 0.3  # mm, 45-degree chamfer on bottom perimeter (Y=0 face)

# ============================================================
# Build the model
# ============================================================

# --- Feature 1: Plate body ---
# Box from origin, centered=False: X:[0,132] Y:[0,5] Z:[0,63]
plate = cq.Workplane("XY").box(PLATE_W, PLATE_T, PLATE_H, centered=False)

# --- Features 2-3: Motor bores (Y-axis cylinders through full thickness) ---
# Use XZ workplane to sketch circles, extrude along Y.
# XZ workplane normal is -Y; positive extrude goes in -Y direction.
# We want to cut from Y=0 through Y=5. Place workplane at Y=5 and extrude
# positively (in -Y direction) by PLATE_T, or place at Y=0 and extrude negatively.
# Simpler: sketch on XZ at Y=PLATE_T, extrude positive (into -Y = toward Y=0).

for bore_cx, bore_cz, label in [(LEFT_BORE_CX, LEFT_BORE_CZ, "left"),
                                  (RIGHT_BORE_CX, RIGHT_BORE_CZ, "right")]:
    bore = (
        cq.Workplane("XZ")
        .workplane(offset=-PLATE_T)  # move workplane to Y=PLATE_T (XZ normal is -Y, so offset=-PLATE_T moves to Y=+PLATE_T)
        .center(bore_cx, bore_cz)
        .circle(BORE_R)
        .extrude(PLATE_T)  # extrude in -Y direction (toward Y=0), cutting through full thickness
    )
    plate = plate.cut(bore)

# --- Features 4-11: M3 through-holes ---
for hx, hz, label in M3_HOLES:
    hole = (
        cq.Workplane("XZ")
        .workplane(offset=-PLATE_T)
        .center(hx, hz)
        .circle(M3_R)
        .extrude(PLATE_T)
    )
    plate = plate.cut(hole)

# --- Features 12-13: Linkage arm notches ---
# Left notch: X=2..10, Y=0..5 (full thickness), Z=0..5
left_notch = (
    cq.Workplane("XY")
    .transformed(offset=(LEFT_NOTCH_X0, 0, 0))
    .box(LEFT_NOTCH_X1 - LEFT_NOTCH_X0, PLATE_T, NOTCH_Z_HEIGHT, centered=False)
)
plate = plate.cut(left_notch)

# Right notch: X=122..130, Y=0..5, Z=0..5
right_notch = (
    cq.Workplane("XY")
    .transformed(offset=(RIGHT_NOTCH_X0, 0, 0))
    .box(RIGHT_NOTCH_X1 - RIGHT_NOTCH_X0, PLATE_T, NOTCH_Z_HEIGHT, centered=False)
)
plate = plate.cut(right_notch)

# --- Features 14-17: Registration tabs (Y-direction protrusions) ---
# These are boxes added to the rearward face (Y=5..7)
tab_specs = [
    (BL_TAB_X0,  0.0,           "Bottom-left reg tab"),   # Z = 0..2
    (BR_TAB_X0,  0.0,           "Bottom-right reg tab"),  # Z = 0..2
    (TL_TAB_X0,  PLATE_H - TAB_H, "Top-left reg tab"),   # Z = 61..63
    (TR_TAB_X0,  PLATE_H - TAB_H, "Top-right reg tab"),  # Z = 61..63
]

for tx0, tz0, label in tab_specs:
    tab = (
        cq.Workplane("XY")
        .transformed(offset=(tx0, PLATE_T, tz0))
        .box(TAB_W, TAB_DEPTH, TAB_H, centered=False)
    )
    plate = plate.union(tab)

# --- Feature 18: Elephant's foot chamfer ---
# The Y=0 face sits on the build plate. 0.3mm x 45-degree chamfer on the
# perimeter edges of the Y=0 face. We use a subtractive approach: cut a
# triangular prism along each outer edge of the Y=0 face.
# The chamfer removes a right triangle (0.3mm legs) along each edge where
# Y=0 meets an outer wall.
C = EF_CHAMFER  # 0.3mm

# Build a chamfer wire frame on the Y=0 face perimeter and cut it.
# Approach: create a thin wedge along each of the 4 outer edges of the
# Y=0 face. For the bottom face (Y=0), the chamfer is at the intersection
# of Y=0 with each vertical/horizontal wall face.
#
# Edge at Z=0, Y=0 (runs along X): chamfer removes material in +Y and +Z
# Edge at Z=63, Y=0 (runs along X): chamfer removes material in +Y and -Z
# Edge at X=0, Y=0 (runs along Z): chamfer removes material in +Y and +X
# Edge at X=132, Y=0 (runs along Z): chamfer removes material in +Y and -X
#
# Use a 2D triangle profile extruded along each edge.

# Bottom edge: Z=0, Y=0, X runs 0..132
# Triangle profile in YZ plane: (0,0), (C,0), (0,C) -> cut in +Y, +Z
chamfer_bottom = (
    cq.Workplane("YZ")
    .polyline([(0, 0), (C, 0), (0, C)])
    .close()
    .extrude(PLATE_W)  # extrude in +X
)
plate = plate.cut(chamfer_bottom)

# Top edge: Z=63, Y=0, X runs 0..132
# Triangle at Z=63: need to cut in +Y and -Z
chamfer_top = (
    cq.Workplane("YZ")
    .center(0, PLATE_H)
    .polyline([(0, 0), (C, 0), (0, -C)])
    .close()
    .extrude(PLATE_W)
)
plate = plate.cut(chamfer_top)

# Left edge: X=0, Y=0, Z runs 0..63
# Triangle at X=0: cut in +Y and +X
chamfer_left = (
    cq.Workplane("XY")
    .polyline([(0, 0), (C, 0), (0, C)])
    .close()
    .extrude(PLATE_H)  # XY normal is +Z
)
plate = plate.cut(chamfer_left)

# Right edge: X=132, Y=0, Z runs 0..63
# Triangle at X=132: cut in +Y and -X (toward interior)
chamfer_right = (
    cq.Workplane("XY")
    .center(PLATE_W, 0)
    .polyline([(0, 0), (-C, 0), (0, C)])
    .close()
    .extrude(PLATE_H)
)
plate = plate.cut(chamfer_right)

# ============================================================
# Export STEP
# ============================================================
output_path = str(Path(__file__).parent / "partition.step")
cq.exporters.export(plate, output_path)
print(f"\nSTEP exported to: {output_path}")

# ============================================================
# Rubric 3 -- Feature-Specification Reconciliation
# ============================================================
print("\n=== FEATURE VALIDATION ===\n")
v = Validator(plate)

# Feature 1: Plate body -- probe interior
v.check_solid("Plate body center", 66.0, 2.5, 31.5, "solid at plate center")
v.check_solid("Plate body near left edge", 1.0, 2.5, 31.5, "solid near X=0")
v.check_solid("Plate body near right edge", 131.0, 2.5, 31.5, "solid near X=132")
v.check_solid("Plate body near bottom", 66.0, 2.5, 1.0, "solid near Z=0")
v.check_solid("Plate body near top", 66.0, 2.5, 62.0, "solid near Z=63")
# Outside plate body
v.check_void("Outside plate X-", -1.0, 2.5, 31.5, "void outside left edge")
v.check_void("Outside plate X+", 133.0, 2.5, 31.5, "void outside right edge")
v.check_void("Outside plate Y+", 66.0, 5.5, 31.5, "void above plate (no tab here)")
v.check_void("Outside plate Z+", 66.0, 2.5, 64.0, "void above plate top")

# Feature 2: Left motor bore
v.check_void("Left bore center", LEFT_BORE_CX, 2.5, LEFT_BORE_CZ, "void at left bore center")
v.check_void("Left bore near edge -X", LEFT_BORE_CX - BORE_R + 0.3, 2.5, LEFT_BORE_CZ, "void near bore -X edge")
v.check_void("Left bore near edge +X", LEFT_BORE_CX + BORE_R - 0.3, 2.5, LEFT_BORE_CZ, "void near bore +X edge")
v.check_solid("Left bore wall +X", LEFT_BORE_CX + BORE_R + 0.5, 2.5, LEFT_BORE_CZ, "solid outside bore +X")
v.check_solid("Left bore wall -X", LEFT_BORE_CX - BORE_R - 0.5, 2.5, LEFT_BORE_CZ, "solid outside bore -X")

# Feature 3: Right motor bore
v.check_void("Right bore center", RIGHT_BORE_CX, 2.5, RIGHT_BORE_CZ, "void at right bore center")
v.check_void("Right bore near edge -X", RIGHT_BORE_CX - BORE_R + 0.3, 2.5, RIGHT_BORE_CZ, "void near bore -X edge")
v.check_solid("Right bore wall +X", RIGHT_BORE_CX + BORE_R + 0.5, 2.5, RIGHT_BORE_CZ, "solid outside bore +X")

# Features 4-11: M3 holes
for hx, hz, label in M3_HOLES:
    v.check_void(f"M3 hole {label} center", hx, 2.5, hz, f"void at M3 {label} center")
    v.check_solid(f"M3 hole {label} wall", hx + M3_R + 0.5, 2.5, hz, f"solid outside M3 {label}")

# Feature 12: Left linkage notch (X=2..10, Z=0..5)
v.check_void("Left notch center", 6.0, 2.5, 2.5, "void at left notch center")
v.check_void("Left notch near X=2", 2.5, 2.5, 2.5, "void near left notch X=2")
v.check_void("Left notch near X=10", 9.5, 2.5, 2.5, "void near left notch X=10")
v.check_solid("Left notch wall above", 6.0, 2.5, 6.0, "solid above left notch Z=5")

# Feature 13: Right linkage notch (X=122..130, Z=0..5)
v.check_void("Right notch center", 126.0, 2.5, 2.5, "void at right notch center")
v.check_solid("Right notch wall above", 126.0, 2.5, 6.0, "solid above right notch Z=5")

# Feature 14: Bottom-left reg tab (X=9..11, Y=5..7, Z=0..2)
v.check_solid("BL tab center", 10.0, 6.0, 1.0, "solid at BL tab center")
v.check_void("BL tab outside Y", 10.0, 7.5, 1.0, "void past BL tab Y=7")
v.check_void("BL tab outside X-", 8.5, 6.0, 1.0, "void outside BL tab X-")

# Feature 15: Bottom-right reg tab (X=121..123, Y=5..7, Z=0..2)
v.check_solid("BR tab center", 122.0, 6.0, 1.0, "solid at BR tab center")
v.check_void("BR tab outside Y", 122.0, 7.5, 1.0, "void past BR tab Y=7")

# Feature 16: Top-left reg tab (X=9..11, Y=5..7, Z=61..63)
v.check_solid("TL tab center", 10.0, 6.0, 62.0, "solid at TL tab center")
v.check_void("TL tab outside Y", 10.0, 7.5, 62.0, "void past TL tab Y=7")

# Feature 17: Top-right reg tab (X=121..123, Y=5..7, Z=61..63)
v.check_solid("TR tab center", 122.0, 6.0, 62.0, "solid at TR tab center")
v.check_void("TR tab outside Y", 122.0, 7.5, 62.0, "void past TR tab Y=7")

# ============================================================
# Rubric 4 -- Solid Validity
# ============================================================
print("\n=== SOLID VALIDITY ===\n")
v.check_valid()
v.check_single_body()
v.check_volume(expected_envelope=PLATE_W * PLATE_T * PLATE_H, fill_range=(0.5, 1.2))

# ============================================================
# Rubric 5 -- Bounding Box Reconciliation
# ============================================================
print("\n=== BOUNDING BOX ===\n")
bb = plate.val().BoundingBox()
# X: 0..132 (plate body edges)
v.check_bbox("X", bb.xmin, bb.xmax, 0.0, 132.0)
# Y: 0..7.0 (plate 0..5, tabs extend to 7.0)
# Note: elephant's foot chamfer trims a tiny bit off Y=0 at edges, but
# the bulk of the plate still starts at Y=0. Tabs extend to Y=7.
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, 7.0)
# Z: 0..63.0 (main body; tabs are within Z range, not extending beyond)
# Chamfer may trim Z slightly at bottom edges near Y=0.
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, 63.0)

# ============================================================
# Summary
# ============================================================
if not v.summary():
    sys.exit(1)
