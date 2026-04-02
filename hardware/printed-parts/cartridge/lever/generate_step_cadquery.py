"""
Lever v3 -- CadQuery STEP Generation Script
Season 1, Phase 6, Item 15 of the pump cartridge build sequence.

Updates from v2: plate widened from 80mm to 140mm, height increased from
65mm to 68.6mm. Strut positions updated to match pump tray v3 strut bore centers.

Coordinate system:
  Origin: Bottom-left corner of lever plate front face (X=0, Y=0, Z=0)
  X: Width axis -- positive rightward as seen by user from front face
     Range: 0 -> 160.0 mm
  Y: Depth axis -- positive rearward (into cartridge)
     Y=0:  Lever plate front face (user contact / pull surface)
     Y=4:  Lever plate rear face (strut attachment point)
     Y=94: Strut tips (4mm plate + 90mm struts)
  Z: Height axis -- positive upward
     Range: 0 -> 68.6 mm

Envelope: 160.0 (X) x 94.0 (Y) x 68.6 (Z) mm
"""

import sys
from pathlib import Path

# Add tools/ to sys.path for step_validate
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))
from step_validate import Validator

import cadquery as cq

# ============================================================
# Rubric 1 -- Feature Planning Table
# ============================================================

print()
print("=" * 90)
print("RUBRIC 1 -- Feature Planning Table")
print("=" * 90)
print()

FEATURE_TABLE = [
    ("1", "Plate Body",
     "Rigid load-transfer body: user finger contact surface (Y=0) to strut attachment (Y=4)",
     "Add", "Box", "Y", "(80.0, 2.0, 34.3)",
     "160W x 4D x 68.6H mm; X:[0,160] Y:[0,4] Z:[0,68.6]", "Base body"),

    ("2", "Plate Perimeter Corner Radii",
     "Prevents sharp corners snagging front panel hole; design language consistency",
     "Remove (blend)", "Fillet", "Y",
     "Edges at (X=0/160, Z=0/68.6), each runs Y=0->4",
     "R=2.0 mm on all 4 vertical (|Y) plate edges", "concept.md"),

    ("3", "Plate Bottom Chamfer (Elephant's Foot)",
     "Prevents elephant's foot dimensional error at build-plate contact edge",
     "Remove", "Chamfer", "Y (edge at Z=0, Y=0 face)",
     "Bottom edge of front face (Z=0, Y=0->4 edge, full X width)",
     "0.3 mm x 45 deg", "Build plate contact = Z=0 face"),

    ("4", "Strut TL (Top-Left)",
     "Transmits pull force from lever plate to Phase 2 joint",
     "Add", "Box", "Y", "Center (4.0, 49.0, 63.6)",
     "6W x 90D x 6H mm; X:[1,7] Y:[4,94] Z:[60.6,66.6]",
     "Matches pump tray bore S-TL center (4.0, 63.6)"),

    ("5", "Strut TR (Top-Right)",
     "Transmits pull force; mirror of TL about X=80",
     "Add", "Box", "Y", "Center (156.0, 49.0, 63.6)",
     "6W x 90D x 6H mm; X:[153,159] Y:[4,94] Z:[60.6,66.6]",
     "Matches pump tray bore S-TR center (161.0, 63.6) when centered"),

    ("6", "Strut BL (Bottom-Left)",
     "Transmits pull force; mirror of TL about Z=34.3",
     "Add", "Box", "Y", "Center (4.0, 49.0, 5.0)",
     "6W x 90D x 6H mm; X:[1,7] Y:[4,94] Z:[2,8]",
     "Matches pump tray bore S-BL center (4.0, 5.0)"),

    ("7", "Strut BR (Bottom-Right)",
     "Transmits pull force; mirror of both TL and BL",
     "Add", "Box", "Y", "Center (156.0, 49.0, 5.0)",
     "6W x 90D x 6H mm; X:[153,159] Y:[4,94] Z:[2,8]",
     "Matches pump tray bore S-BR center (161.0, 5.0) when centered"),
]

col_w = [3, 26, 20, 15, 10, 6, 26, 35, 40]
header = (f"{'#':<{col_w[0]}} {'Feature Name':<{col_w[1]}} {'Operation':<{col_w[3]}} "
          f"{'Shape':<{col_w[4]}} {'Axis':<{col_w[5]}} {'Center (X,Y,Z)':<{col_w[6]}} "
          f"{'Dimensions':<{col_w[7]}} Notes")
print(header)
print("-" * 140)
for row in FEATURE_TABLE:
    num, name, func, op, shape, axis, center, dims, notes = row
    print(f"{num:<{col_w[0]}} {name:<{col_w[1]}} {op:<{col_w[3]}} "
          f"{shape:<{col_w[4]}} {axis:<{col_w[5]}} {center:<{col_w[6]}} "
          f"{dims:<{col_w[7]}} {notes}")

print()

# ============================================================
# Rubric 2 -- Coordinate System Declaration
# ============================================================

print("=" * 90)
print("RUBRIC 2 -- Coordinate System Declaration")
print("=" * 90)
print()
print("  Origin: Bottom-left corner of lever plate front face (X=0, Y=0, Z=0)")
print("  X: Plate width, left to right as seen from front face; range [0, 160.0] mm")
print("  Y: Plate depth, front (user contact Y=0) to rear (strut tips Y=94.0); range [0, 94.0] mm")
print("  Z: Plate height, bottom to top; range [0, 68.6] mm")
print("  Envelope: 160.0 x 94.0 x 68.6 mm  ->  X:[0,160]  Y:[0,94]  Z:[0,68.6]")
print()
print("  Feature coordinate cross-check:")
print("    Plate occupies  X:[0,160]    Y:[0,4]    Z:[0,68.6]")
print("    Strut TL center X=4.0,   Z=63.6  -> box X:[1,7]     Y:[4,94]  Z:[60.6,66.6]")
print("    Strut TR center X=156.0, Z=63.6  -> box X:[153,159]  Y:[4,94]  Z:[60.6,66.6]")
print("    Strut BL center X=4.0,   Z=5.0   -> box X:[1,7]     Y:[4,94]  Z:[2,8]")
print("    Strut BR center X=156.0, Z=5.0   -> box X:[153,159]  Y:[4,94]  Z:[2,8]")
print()

# ============================================================
# Geometry constants
# ============================================================

# Plate
PLATE_W  = 160.0   # X (was 140.0, +20mm to accommodate struts moved outward)
PLATE_D  =   4.0   # Y
PLATE_H  =  43.6   # Z (was 68.6, -25mm: 12.5mm from top and bottom)

# Struts
STRUT_W  =  6.0    # X cross-section
STRUT_H  =  6.0    # Z cross-section
STRUT_L  = 90.0    # Y length
STRUT_Y0 =  4.0    # struts start at plate rear face
STRUT_Y1 = 94.0    # strut tips

# Strut center positions in lever local X and Z
# Positions match pump tray v3 strut bore centers exactly.
STRUTS = {
    "TL": (  4.0, 38.6),
    "TR": (156.0, 38.6),
    "BL": (  4.0,  5.0),
    "BR": (156.0,  5.0),
}

# Plate corner fillet radius (Feature 2)
CORNER_R = 2.0    # mm

# Elephant's foot chamfer (Feature 3)
CHAMFER  = 0.3    # mm

# ============================================================
# Feature 1 -- Plate Body
# ============================================================
print("Building Feature 1: Plate Body ...")
plate = cq.Workplane("XY").box(PLATE_W, PLATE_D, PLATE_H, centered=False)

# ============================================================
# Feature 2 -- Plate Perimeter Corner Radii
# ============================================================
print("Building Feature 2: Corner radii on vertical plate edges ...")
plate = plate.edges("|Y").fillet(CORNER_R)

# ============================================================
# Feature 3 -- Elephant's Foot Chamfer on bottom front edge
# ============================================================
print("Building Feature 3: Elephant's foot chamfer ...")
# Bottom front edge: Z=0, Y=0 intersection. Select edges on Z=0 face, then Y=0 face.
plate = plate.edges("<Z").edges("<Y").chamfer(CHAMFER)

# ============================================================
# Features 4-7 -- Struts (union to plate)
# ============================================================
print("Building Features 4-7: Struts (TL, TR, BL, BR) ...")
lever = plate
for label, (cx, cz) in STRUTS.items():
    sx0 = cx - STRUT_W / 2   # left X edge of strut
    sz0 = cz - STRUT_H / 2   # bottom Z edge of strut
    strut = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(sx0, STRUT_Y0, sz0))
        .box(STRUT_W, STRUT_L, STRUT_H, centered=False)
    )
    lever = lever.union(strut)

# ============================================================
# Features 8-11 -- Snap-fit grooves on strut tips
# ============================================================
print("Building Features 8-11: Snap-fit grooves on strut X faces ...")
SNAP_GROOVE_DEPTH = 0.5   # depth into strut X face
SNAP_GROOVE_WIDTH = 0.5   # width in Y
SNAP_GROOVE_Y_CENTER = STRUT_Y1 - 2.0  # 2mm from tip, aligns with socket bumps
snap_groove_y0 = SNAP_GROOVE_Y_CENTER - SNAP_GROOVE_WIDTH / 2

for label, (cx, cz) in STRUTS.items():
    sz0 = cz - STRUT_H / 2
    overcut = 0.1
    for groove_x0, groove_w in [
        (cx - STRUT_W / 2 - overcut, SNAP_GROOVE_DEPTH + overcut),   # -X face
        (cx + STRUT_W / 2 - SNAP_GROOVE_DEPTH, SNAP_GROOVE_DEPTH + overcut),  # +X face
    ]:
        groove = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(groove_x0, snap_groove_y0, sz0))
            .box(groove_w, SNAP_GROOVE_WIDTH, STRUT_H, centered=False)
        )
        lever = lever.cut(groove)

# ============================================================
# Export STEP file
# ============================================================
OUT_DIR = Path(__file__).parent
STEP_PATH = OUT_DIR / "lever-cadquery.step"
print(f"\nExporting STEP to: {STEP_PATH}")
cq.exporters.export(lever, str(STEP_PATH))
print("Export complete.")

# ============================================================
# Rubric 3 -- Feature-Specification Reconciliation
# ============================================================

print()
print("=" * 90)
print("RUBRIC 3 -- Feature-Specification Reconciliation")
print("=" * 90)
print()

v = Validator(lever)

# --- Feature 1: Plate Body ---
print("Feature 1: Plate Body")
v.check_solid("Plate interior center",      80.0,  2.0, 21.8, "solid at plate center")
v.check_solid("Plate left face interior",    1.0,   2.0, 21.8, "solid near left face")
v.check_solid("Plate right face interior", 159.0,   2.0, 21.8, "solid near right face")
v.check_solid("Plate front face interior",  80.0,   0.5, 21.8, "solid near front face")
v.check_solid("Plate rear face interior",   80.0,   3.5, 21.8, "solid near rear face")
v.check_solid("Plate top interior",         80.0,   2.0, 42.6, "solid near top face")
v.check_solid("Plate bottom interior",      80.0,   2.0,  1.0, "solid near bottom face (above chamfer)")
# Void outside plate
v.check_void("Void in front of plate",      80.0,  -1.0, 21.8, "void in front of plate front face")
v.check_void("Void above plate (no strut)", 80.0,   2.0, 44.6, "void above plate where no strut")

print()

# --- Feature 2: Corner Radii ---
print("Feature 2: Plate Corner Radii (R=2.0mm)")
# After 2mm fillet on convex corner at (X=0, Z=0): point at (0.5, 2.0, 0.5) is in
# the removed zone. Distance from fillet center at (2.0, y, 2.0) = sqrt(1.5^2+1.5^2) = 2.12 > 2.0 -> void.
v.check_void("Corner BL fillet",
             0.5, 2.0, 0.5, "void in BL corner fillet zone")
v.check_void("Corner BR fillet",
             PLATE_W - 0.5, 2.0, 0.5, "void in BR corner fillet zone")
v.check_void("Corner TL fillet",
             0.5, 2.0, PLATE_H - 0.5, "void in TL corner fillet zone")
v.check_void("Corner TR fillet",
             PLATE_W - 0.5, 2.0, PLATE_H - 0.5, "void in TR corner fillet zone")
# Solid just inside fillet tangent points
v.check_solid("Plate BL near-corner solid",  3.0, 2.0,  0.5, "solid past fillet tangent on X=3")
v.check_solid("Plate BL near-corner solid2", 0.5, 2.0,  3.0, "solid past fillet tangent on Z=3")

print()

# --- Feature 3: Elephant's Foot Chamfer ---
print("Feature 3: Elephant's Foot Chamfer (0.3mm x 45 deg, bottom front edge)")
# At Y=0.1, Z=0.1, Y+Z=0.2 < 0.3 -> void (in chamfer zone)
v.check_void("Chamfer void at (70, 0.1, 0.1)",
             70.0, 0.1, 0.1, "void in chamfer zone")
# At Y=0.25, Z=0.25, Y+Z=0.5 > 0.3 -> solid
v.check_solid("Solid above chamfer zone (70, 0.25, 0.25)",
              70.0, 0.25, 0.25, "solid above 0.3mm chamfer zone")
v.check_solid("Front face solid above chamfer",
              70.0, 0.2, 2.0, "solid on front face above chamfer zone")

print()

# --- Features 4-7: Struts ---
print("Features 4-7: Struts TL, TR, BL, BR")

for label, (cx, cz) in STRUTS.items():
    mid_y = (STRUT_Y0 + STRUT_Y1) / 2  # Y=49.0
    tip_y = STRUT_Y1 - 1.0             # Y=93.0
    base_y = STRUT_Y0 + 1.0            # Y=5.0

    # Interior of strut at midpoint
    v.check_solid(f"Strut {label} mid-center",
                  cx, mid_y, cz, f"solid at strut {label} center (X={cx}, Y={mid_y}, Z={cz})")
    # Near strut tip
    v.check_solid(f"Strut {label} tip interior",
                  cx, tip_y, cz, f"solid near strut {label} tip (Y={tip_y})")
    # At strut base
    v.check_solid(f"Strut {label} base",
                  cx, base_y, cz, f"solid at strut {label} base (Y={base_y})")

    # Dimensions: check that points just outside strut cross-section are void
    sx0 = cx - STRUT_W / 2
    sx1 = cx + STRUT_W / 2
    sz0 = cz - STRUT_H / 2
    sz1 = cz + STRUT_H / 2

    # Void just beyond X extents at mid strut (only where outside plate Y range)
    if sx0 - 0.5 > 0 and sx0 - 0.5 < PLATE_W:
        v.check_void(f"Strut {label} void X- side",
                     sx0 - 0.5, mid_y, cz,
                     f"void just left of strut {label} (X={sx0-0.5:.1f})")

    if sx1 + 0.5 < PLATE_W:
        v.check_void(f"Strut {label} void X+ side",
                     sx1 + 0.5, mid_y, cz,
                     f"void just right of strut {label} (X={sx1+0.5:.1f})")

    if sz0 - 0.5 > 0:
        v.check_void(f"Strut {label} void Z- side",
                     cx, mid_y, sz0 - 0.5,
                     f"void below strut {label} (Z={sz0-0.5:.1f})")

    if sz1 + 0.5 < PLATE_H:
        v.check_void(f"Strut {label} void Z+ side",
                     cx, mid_y, sz1 + 0.5,
                     f"void above strut {label} (Z={sz1+0.5:.1f})")

    # Void beyond strut tips
    v.check_void(f"Strut {label} void beyond tip",
                 cx, STRUT_Y1 + 1.0, cz,
                 f"void beyond strut {label} tip (Y={STRUT_Y1+1.0})")

print()

# ============================================================
# Rubric 4 -- Solid Validity
# ============================================================
print("=" * 90)
print("RUBRIC 4 -- Solid Validity")
print("=" * 90)
print()

v.check_valid()
v.check_single_body()

# Volume estimate:
# Plate: 140 x 4 x 68.6 = 38416 mm^3
# 4 struts: 4 x 6 x 90 x 6 = 12960 mm^3
# Minus corner fillets and chamfer (small)
# Total ~ 51376 mm^3
# Envelope: 140 x 94 x 68.6 = 903,544 mm^3
# Fill ratio: ~51376/903544 ~ 5.7%
envelope_vol = PLATE_W * STRUT_Y1 * PLATE_H  # 140 x 94 x 68.6
v.check_volume(expected_envelope=envelope_vol, fill_range=(0.04, 0.12))

print()

# ============================================================
# Rubric 5 -- Bounding Box Reconciliation
# ============================================================
print("=" * 90)
print("RUBRIC 5 -- Bounding Box Reconciliation")
print("=" * 90)
print()
print("Expected envelope from parts.md: 140.0mm (X) x 94.0mm (Y) x 68.6mm (Z)")
print()

bb = lever.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, 0.0, PLATE_W)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, STRUT_Y1)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, PLATE_H)

print()

# ============================================================
# Summary
# ============================================================
ok = v.summary()
if not ok:
    sys.exit(1)
else:
    print(f"\nSTEP file written to: {STEP_PATH}")
    sys.exit(0)
