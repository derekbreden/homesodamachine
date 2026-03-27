#!/usr/bin/env python3
"""
Cartridge Release Plate — CadQuery STEP Generation

Generates the release plate for the soda flavor injector pump cartridge.
The plate simultaneously releases 4 John Guest PP0408W push-to-connect collets
via cam lever actuation.

Source material:
  - hardware/cartridge-release-plate/planning/parts.md
  - hardware/planning/step-generation-standards.md
  - hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md
  - hardware/cartridge-release-plate/planning/research/release-plate.md
  - hardware/cartridge-release-plate/planning/research/collet-release.md

Coordinate system:
  Origin: plate bottom-left-front corner (front face = fitting engagement side)
  X: plate width, left to right (59mm)    -> X: [0, 59]
  Y: plate depth, front to back (6mm)     -> Y: [0, 6]
     Front face Y=0 engages fittings (outer bore entry)
     Back face Y=6 receives push rod (tube hole exit, boss)
  Z: plate height, bottom to top (47mm)   -> Z: [0, 47]
  Envelope (body only): 59 x 6 x 47 mm

Bore depth stack (from front face Y=0 inward):
  Y=0 to Y=2: outer bore (body end cradle), 15.30mm dia
  Y=2 to Y=4: inner lip (collet hugger), 9.70mm dia
  Y=4 to Y=6: structural back wall, tube clearance hole only (6.50mm dia)

Guide pin tabs protrude beyond the plate body in +/- X.
Push rod boss protrudes beyond back face in +Y.
"""

import cadquery as cq
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from step_validate import Validator

# ============================================================
# PARAMETERS — from parts.md, geometry-description.md, research
# ============================================================

# Plate body envelope
PLATE_W = 59.0   # X extent (mm)
PLATE_D = 6.0    # Y extent (mm) — depth / thickness
PLATE_H = 47.0   # Z extent (mm)

# Stepped bore diameters
# Outer bore: body end cradle, must clear 15.10mm body end OD (caliper-verified)
# Using 15.30mm = 0.10mm/side clearance. Tight for lateral constraint.
OUTER_BORE_DIA = 15.30
OUTER_BORE_DEPTH = 2.0    # Y=0 to Y=2

# Inner lip: collet hugger, must clear 9.57mm collet OD (caliper-verified)
# Using 9.70mm = 0.065mm/side clearance. Tight for lateral constraint.
INNER_LIP_DIA = 9.70
INNER_LIP_DEPTH = 2.0     # Y=2 to Y=4

# Tube clearance hole: must be between 6.30mm tube OD and 6.69mm collet ID
# Using 6.50mm = midpoint of 0.39mm design window
TUBE_HOLE_DIA = 6.50
# Tube hole goes through full depth Y=0 to Y=6

# Verify depth stack
assert abs(OUTER_BORE_DEPTH + INNER_LIP_DEPTH + (PLATE_D - OUTER_BORE_DEPTH - INNER_LIP_DEPTH) - PLATE_D) < 0.001

# Chamfers
OUTER_CHAMFER = 0.3   # 45-deg lead-in at outer bore entry (front face Y=0)
TUBE_CHAMFER = 0.1    # at tube hole entry edge

# Bore grid centers: 2x2, relative to plate bottom-left (X, Z)
# parts.md: 40mm horizontal x 28mm vertical center-to-center
BORE_CENTERS = [
    (9.5,  9.5),   # bottom-left
    (49.5, 9.5),   # bottom-right
    (9.5,  37.5),  # top-left
    (49.5, 37.5),  # top-right
]

# Guide pin slots
# parts.md: 3.3mm wide x 7.3mm long, at (X, Z) = (-5.5, 23.5) and (64.5, 23.5)
# These are X-start positions for slots that extend beyond the plate body.
# The plate has "ear" tabs at these locations to provide material around the slots.
SLOT_W = 3.3   # width in X (clears 3mm dowel pin)
SLOT_L = 7.3   # length in Z (accommodates 3mm stroke + pin dia + margin)
SLOT_CENTERS = [
    (-5.5 + SLOT_W / 2, 23.5),   # left slot center: X=-3.85, Z=23.5
    (64.5 + SLOT_W / 2, 23.5),   # right slot center: X=66.15, Z=23.5
]

# Tab dimensions around each slot (ears extending from plate body)
TAB_WALL = 2.0   # minimum wall thickness around slot
TAB_W = SLOT_W + 2 * TAB_WALL   # 7.3mm in X
TAB_H = SLOT_L + 2 * TAB_WALL   # 11.3mm in Z

# Push rod contact boss
# parts.md: centered boss on back face at (29.5, 23.5), 8mm dia x 1mm proud
BOSS_X = 29.5
BOSS_Z = 23.5
BOSS_DIA = 8.0
BOSS_HEIGHT = 1.0

# Derived radii
R_OUTER = OUTER_BORE_DIA / 2   # 7.65
R_INNER = INNER_LIP_DIA / 2    # 4.85
R_TUBE = TUBE_HOLE_DIA / 2     # 3.25

# ============================================================
# FEATURE PLANNING TABLE (Rubric 1)
# ============================================================

print("=" * 110)
print("FEATURE PLANNING TABLE (Rubric 1)")
print("=" * 110)
header = (f"{'#':<4} {'Feature Name':<28} {'Mech. Function':<30} {'Op':<7} "
          f"{'Shape':<8} {'Axis':<5} {'Center (X,Y,Z)':<22} {'Dimensions':<28} {'Notes'}")
print(header)
print("-" * 110)

table_rows = [
    ("1",  "Plate body",              "Structural base",            "Add",    "Box",     "—",
     "(29.5, 3.0, 23.5)",   "59x6x47mm",                "PETG"),
    ("2",  "Left guide pin tab",      "Material around left slot",  "Add",    "Box",     "—",
     "(-3.85, 3.0, 23.5)",  f"{TAB_W}x{PLATE_D}x{TAB_H}mm",    "Ear protruding left"),
    ("3",  "Right guide pin tab",     "Material around right slot", "Add",    "Box",     "—",
     "(66.15, 3.0, 23.5)",  f"{TAB_W}x{PLATE_D}x{TAB_H}mm",    "Ear protruding right"),
    ("4",  "Push rod boss",           "Cam push rod contact",       "Add",    "Cyl",     "Y",
     f"({BOSS_X}, 6.5, {BOSS_Z})", f"D{BOSS_DIA}xH{BOSS_HEIGHT}mm",  "Back face, +Y"),
    ("5",  "Outer bores (x4)",        "Cradle body end 15.10mm",    "Remove", "Cyl",     "Y",
     "(cx, 1.0, cz) x4",    f"D{OUTER_BORE_DIA}, {OUTER_BORE_DEPTH}mm deep", "Y=0 to Y=2"),
    ("6",  "Inner lip bores (x4)",    "Hug collet 9.57mm OD",       "Remove", "Cyl",     "Y",
     "(cx, 3.0, cz) x4",    f"D{INNER_LIP_DIA}, {INNER_LIP_DEPTH}mm deep",   "Y=2 to Y=4"),
    ("7",  "Tube clearance holes (x4)","Pass tube 6.30mm OD",       "Remove", "Cyl",     "Y",
     "(cx, 3.0, cz) x4",    f"D{TUBE_HOLE_DIA}, through",         "Full depth"),
    ("8",  "Outer bore chamfers (x4)", "Fitting engagement lead-in", "Remove", "Chamfer", "Y",
     "at bore, Y=0",         f"{OUTER_CHAMFER}mm x 45deg",         "Front face entry"),
    ("9",  "Tube hole chamfers (x4)",  "Ease tube threading",        "Remove", "Chamfer", "Y",
     "at bore, Y=4",         f"{TUBE_CHAMFER}mm x 45deg",          "At inner lip floor"),
    ("10", "Left guide pin slot",      "Linear guide on 3mm pin",    "Remove", "Stadium", "Y",
     f"({SLOT_CENTERS[0][0]:.2f}, *, 23.5)", f"{SLOT_W}Wx{SLOT_L}L, thru",   "Long axis Z"),
    ("11", "Right guide pin slot",     "Linear guide on 3mm pin",    "Remove", "Stadium", "Y",
     f"({SLOT_CENTERS[1][0]:.2f}, *, 23.5)", f"{SLOT_W}Wx{SLOT_L}L, thru",   "Long axis Z"),
]

for row in table_rows:
    print(f"{row[0]:<4} {row[1]:<28} {row[2]:<30} {row[3]:<7} {row[4]:<8} {row[5]:<5} "
          f"{row[6]:<22} {row[7]:<28} {row[8]}")

print("=" * 110)
print(f"Bore centers (X,Z): {BORE_CENTERS}")
print(f"Bore spacing: 40mm horizontal, 28mm vertical")
print()

# ============================================================
# MODEL CONSTRUCTION
# ============================================================

# --- Feature 1: Plate body ---
# Box from origin: X=[0,59], Y=[0,6], Z=[0,47]
plate = cq.Workplane("XY").box(PLATE_W, PLATE_D, PLATE_H, centered=False)

# --- Features 2 & 3: Guide pin tabs ---
# Each tab is a box centered on the slot center, extending beyond the plate body.
# Must overlap with the main plate body so union produces a single solid.
for slot_cx, slot_cz in SLOT_CENTERS:
    tab_x0 = slot_cx - TAB_W / 2
    tab_z0 = slot_cz - TAB_H / 2

    # Extend tab to overlap with plate body for solid fusion
    if slot_cx < 0:
        # Left tab: extend right edge into plate body
        tab_right = max(tab_x0 + TAB_W, 1.0)  # ensure overlap
        tab = (
            cq.Workplane("XY")
            .box(tab_right - tab_x0, PLATE_D, TAB_H, centered=False)
            .translate((tab_x0, 0, tab_z0))
        )
    else:
        # Right tab: extend left edge into plate body
        tab_left = min(tab_x0, PLATE_W - 1.0)
        tab_right = tab_x0 + TAB_W
        tab = (
            cq.Workplane("XY")
            .box(tab_right - tab_left, PLATE_D, TAB_H, centered=False)
            .translate((tab_left, 0, tab_z0))
        )
    plate = plate.union(tab)

# --- Feature 4: Push rod boss ---
# 8mm dia x 1mm cylinder on back face, centered at (29.5, 23.5)
# Back face is at Y=6, boss extends to Y=7
boss = (
    cq.Workplane("XZ")
    .center(BOSS_X, BOSS_Z)
    .circle(BOSS_DIA / 2)
    .extrude(-BOSS_HEIGHT)          # XZ normal is -Y; negative extrude goes +Y
    .translate((0, PLATE_D, 0))     # shift to back face
)
plate = plate.union(boss)

# --- Features 5-9: Stepped bores with chamfers (x4) ---
# Revolved profile technique: define the full axial cross-section as (R, Y) points
# and revolve 360 degrees around the Y axis.
#
# Y=0 is front face (fitting side), Y=6 is back face (cam side).
# Depth stack:
#   Y=0..2:  outer bore (R=7.65) with 0.3mm entry chamfer at Y=0
#   Y=2..4:  inner lip (R=4.85)
#   Y=4..6:  tube hole (R=3.25) with 0.1mm chamfer at Y=4

profile_pts = [
    (0,                 0),                                          # axis at front face
    (R_OUTER - OUTER_CHAMFER, 0),                                    # outer chamfer start
    (R_OUTER,           OUTER_CHAMFER),                              # outer chamfer end
    (R_OUTER,           OUTER_BORE_DEPTH),                           # outer bore floor (Y=2)
    (R_INNER,           OUTER_BORE_DEPTH),                           # step to inner lip
    (R_INNER,           OUTER_BORE_DEPTH + INNER_LIP_DEPTH),        # inner lip floor (Y=4)
    (R_TUBE + TUBE_CHAMFER, OUTER_BORE_DEPTH + INNER_LIP_DEPTH),    # tube chamfer start
    (R_TUBE,            OUTER_BORE_DEPTH + INNER_LIP_DEPTH + TUBE_CHAMFER),  # tube chamfer end
    (R_TUBE,            PLATE_D),                                    # tube hole to back face
    (0,                 PLATE_D),                                    # axis at back face
]

# Build the revolved bore cutter
bore_profile = cq.Workplane("XY").moveTo(*profile_pts[0])
for pt in profile_pts[1:]:
    bore_profile = bore_profile.lineTo(*pt)
bore_profile = bore_profile.close()

# Revolve around Y axis: axis point (0,0), axis direction (0,1)
bore_cutter = bore_profile.revolve(360, (0, 0), (0, 1))

# Cut each bore at its (cx, cz) position
for cx, cz in BORE_CENTERS:
    plate = plate.cut(bore_cutter.translate((cx, 0, cz)))

# --- Features 10 & 11: Guide pin slots ---
# Stadium: 3.3mm wide (X) x 7.3mm long (Z), through full depth (Y)
# slot2D(length, width, angle=90) on XZ workplane: long axis along Z
for slot_cx, slot_cz in SLOT_CENTERS:
    slot_cutter = (
        cq.Workplane("XZ")
        .center(slot_cx, slot_cz)
        .slot2D(SLOT_L, SLOT_W, angle=90)   # long axis along Z
        .extrude(-PLATE_D)                   # XZ normal is -Y; negative extrude goes +Y
    )
    plate = plate.cut(slot_cutter)

# ============================================================
# EXPORT STEP FILE
# ============================================================

output_path = Path(__file__).parent / "release-plate-cadquery.step"
cq.exporters.export(plate, str(output_path))
print(f"STEP exported to: {output_path}")
print()

# ============================================================
# VALIDATION (Rubrics 3, 4, 5)
# ============================================================

print("VALIDATION")
print("=" * 60)

v = Validator(plate)

# --- Feature 1: Plate body ---
v.check_solid("Plate body center",
              PLATE_W / 2, PLATE_D / 2, PLATE_H / 2)
v.check_solid("Plate body near origin",
              1.0, PLATE_D / 2, 1.0)
v.check_solid("Plate body far corner",
              PLATE_W - 1.0, PLATE_D / 2, PLATE_H - 1.0)

# --- Features 2 & 3: Guide pin tabs ---
# Solid in tab material, above the slot
v.check_solid("Left tab material",
              SLOT_CENTERS[0][0], PLATE_D / 2, 23.5 + SLOT_L / 2 + TAB_WALL / 2,
              "solid in left tab wall above slot")
v.check_solid("Right tab material",
              SLOT_CENTERS[1][0], PLATE_D / 2, 23.5 + SLOT_L / 2 + TAB_WALL / 2,
              "solid in right tab wall above slot")

# --- Feature 4: Push rod boss ---
v.check_solid("Boss center",
              BOSS_X, PLATE_D + BOSS_HEIGHT / 2, BOSS_Z,
              "solid at boss center")
v.check_solid("Boss near edge",
              BOSS_X + BOSS_DIA / 2 - 0.3, PLATE_D + BOSS_HEIGHT / 2, BOSS_Z,
              "solid near boss perimeter")
v.check_void("Boss outside radius",
             BOSS_X + BOSS_DIA / 2 + 0.5, PLATE_D + BOSS_HEIGHT / 2, BOSS_Z,
             "void outside boss")
v.check_void("Boss above top",
             BOSS_X, PLATE_D + BOSS_HEIGHT + 0.5, BOSS_Z,
             "void above boss top")

# --- Features 5-9: Stepped bores (x4) ---
for i, (cx, cz) in enumerate(BORE_CENTERS):
    label = f"Bore {i+1}"

    # Outer bore: void at center, Y=1.0 (within 0-2mm depth)
    v.check_void(f"{label} outer bore center",
                 cx, 1.0, cz,
                 f"void at bore center, outer bore depth")
    # Outer bore: solid just outside radius
    v.check_solid(f"{label} outer bore wall",
                  cx + R_OUTER + 0.5, 1.0, cz,
                  f"solid outside outer bore")
    # Outer bore: void just inside radius
    v.check_void(f"{label} outer bore inner edge",
                 cx + R_OUTER - 0.5, 1.0, cz,
                 f"void inside outer bore near wall")

    # Inner lip: void at center, Y=3.0 (within 2-4mm depth)
    v.check_void(f"{label} inner lip center",
                 cx, 3.0, cz,
                 f"void at bore center, inner lip depth")
    # Inner lip: solid outside inner lip radius
    v.check_solid(f"{label} inner lip wall",
                  cx + R_INNER + 0.5, 3.0, cz,
                  f"solid outside inner lip")
    # Inner lip: void inside inner lip radius
    v.check_void(f"{label} inner lip inner edge",
                 cx + R_INNER - 0.3, 3.0, cz,
                 f"void inside inner lip near wall")
    # Step verification: outer bore radius is solid at inner lip depth
    v.check_solid(f"{label} outer-to-inner step",
                  cx + R_OUTER - 0.3, 3.0, cz,
                  f"solid at outer bore radius, inner lip depth")

    # Tube hole: void at center, Y=5.0 (structural back zone)
    v.check_void(f"{label} tube hole center",
                 cx, 5.0, cz,
                 f"void at bore center, structural back depth")
    # Tube hole: solid outside tube radius
    v.check_solid(f"{label} tube hole wall",
                  cx + R_TUBE + 0.5, 5.0, cz,
                  f"solid outside tube hole")
    # Step verification: inner lip radius is solid at structural back depth
    v.check_solid(f"{label} inner-to-tube step",
                  cx + R_INNER - 0.3, 5.0, cz,
                  f"solid at inner lip radius, back depth")

    # Outer bore chamfer: at Y=0.15, the bore radius transitions from
    # R_OUTER-0.3 (at Y=0) to R_OUTER (at Y=0.3).
    # At Y=0.15, boundary is at R = R_OUTER - 0.15.
    # A point at R = R_OUTER - 0.1 should be SOLID (chamfer preserves material)
    v.check_solid(f"{label} outer chamfer",
                  cx + R_OUTER - 0.1, 0.1, cz,
                  f"solid in outer chamfer zone")

    # Tube chamfer: at Y=4.0, chamfer starts at R=R_TUBE+0.1 and
    # transitions to R=R_TUBE at Y=4.1.
    # At Y=4.05, boundary is at R = R_TUBE + 0.05.
    # A point at R = R_TUBE + 0.08 should be SOLID (chamfer preserved)
    v.check_solid(f"{label} tube chamfer",
                  cx + R_TUBE + 0.08, OUTER_BORE_DEPTH + INNER_LIP_DEPTH + 0.05, cz,
                  f"solid in tube chamfer zone")

# --- Features 10 & 11: Guide pin slots ---
for i, (sx, sz) in enumerate(SLOT_CENTERS):
    side = "Left" if i == 0 else "Right"

    # Slot center: void
    v.check_void(f"{side} slot center",
                 sx, PLATE_D / 2, sz,
                 f"void at slot center")

    # Slot Z+ end (long axis direction): void
    v.check_void(f"{side} slot Z+ end",
                 sx, PLATE_D / 2, sz + SLOT_L / 2 - 0.5,
                 f"void near top of slot")

    # Slot Z- end: void
    v.check_void(f"{side} slot Z- end",
                 sx, PLATE_D / 2, sz - SLOT_L / 2 + 0.5,
                 f"void near bottom of slot")

    # Tab wall above slot: solid
    v.check_solid(f"{side} slot tab above",
                  sx, PLATE_D / 2, sz + SLOT_L / 2 + TAB_WALL / 2,
                  f"solid in tab wall above slot")

    # Tab wall below slot: solid
    v.check_solid(f"{side} slot tab below",
                  sx, PLATE_D / 2, sz - SLOT_L / 2 - TAB_WALL / 2,
                  f"solid in tab wall below slot")

# --- Rubric 4: Solid validity ---
v.check_valid()
v.check_single_body()
v.check_volume(expected_envelope=PLATE_W * PLATE_D * PLATE_H, fill_range=(0.5, 1.5))

# --- Rubric 5: Bounding box ---
bb = plate.val().BoundingBox()

# Expected bounds:
# X: left tab extends to SLOT_CENTERS[0][0] - TAB_W/2 = -3.85 - 3.65 = -7.50
#    right tab extends to SLOT_CENTERS[1][0] + TAB_W/2 = 66.15 + 3.65 = 69.80
#    But tabs overlap with plate body, so actual extent depends on union.
#    Left tab: x0 = -3.85 - 7.3/2 = -7.50 ... wait, TAB_W = 7.3
#    tab_x0 = slot_cx - TAB_W/2 = -3.85 - 3.65 = -7.50
#    But we extended right edge to max(tab_x0 + TAB_W, 1.0) = max(-0.20, 1.0) = 1.0
#    So left tab goes from -7.50 to 1.0
# X min: -7.50, X max: right tab right edge
#    Right: tab_left = min(tab_x0, 58.0) where tab_x0 = 66.15 - 3.65 = 62.50
#    So tab_left = 58.0, tab_right = 62.50 + 7.3 = 69.80
#    Right tab goes from 58.0 to 69.80
# Actually let me recalculate:
#   Left slot center: (-3.85, 23.5)
#   TAB_W = 7.3, so tab_x0 = -3.85 - 3.65 = -7.50
#   tab_right = max(-7.50 + 7.3, 1.0) = max(-0.20, 1.0) = 1.0
#   Left tab: X from -7.50 to 1.0
#
#   Right slot center: (66.15, 23.5)
#   tab_x0 = 66.15 - 3.65 = 62.50
#   tab_left = min(62.50, 58.0) = 58.0
#   tab_right = 62.50 + 7.3 = 69.80
#   Right tab: X from 58.0 to 69.80

exp_xmin = -7.50
exp_xmax = 69.80
exp_ymin = 0.0
exp_ymax = PLATE_D + BOSS_HEIGHT   # 7.0
exp_zmin = 0.0
exp_zmax = PLATE_H                 # 47.0

v.check_bbox("X", bb.xmin, bb.xmax, exp_xmin, exp_xmax)
v.check_bbox("Y", bb.ymin, bb.ymax, exp_ymin, exp_ymax)
v.check_bbox("Z", bb.zmin, bb.zmax, exp_zmin, exp_zmax)

# ============================================================
# SUMMARY
# ============================================================
if not v.summary():
    sys.exit(1)
