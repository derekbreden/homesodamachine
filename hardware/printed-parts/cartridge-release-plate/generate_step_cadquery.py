#!/usr/bin/env python3
"""
Cartridge Release Plate — CadQuery STEP Generation

Generates the release plate for the soda flavor injector pump cartridge.
The plate simultaneously releases 4 John Guest PP0408W push-to-connect collets
via twist-release strut mechanism (PETG threaded strut press-fit + epoxied into
a socket on the plate back face).

The plate sits on the DOCK SIDE of the rear wall (outside the cartridge body).
The stepped bores face the dock, with their openings facing away from the
cartridge interior.  The strut pulls the plate toward the rear wall to push
dock-side collets inward.

Integral 6mm guide pins protrude from the back face and slide in 6.5mm printed
bushings in the rear wall, preventing rotation and ensuring parallel travel.

Source material:
  - hardware/cartridge-release-plate/planning/parts.md
  - hardware/cartridge-twist-release/planning/parts.md
  - hardware/planning/step-generation-standards.md
  - hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md
  - hardware/cartridge-release-plate/planning/research/release-plate.md
  - hardware/cartridge-release-plate/planning/research/collet-release.md

Coordinate system:
  Origin: plate bottom-left-front corner (front face = fitting engagement side)
  X: plate width, left to right (59mm)    -> X: [0, 59]
  Y: plate depth, front to back (6mm)     -> Y: [0, 6]
     Front face Y=0: stepped bore openings (dock side, facing away from cartridge)
     Back face Y=6: structural face (rear wall side), strut socket boss, guide pins
  Z: plate height, bottom to top (47mm)   -> Z: [0, 47]
  Envelope (body only): 59 x 6 x 47 mm

Bore depth stack (from front face Y=0 inward):
  Y=0 to Y=2: outer bore (body end cradle), 15.30mm dia
  Y=2 to Y=4: inner lip (collet hugger), 9.70mm dia
  Y=4 to Y=6: structural back wall, tube clearance hole only (6.50mm dia)

Integral guide pins protrude beyond back face in +Y.
Strut press-fit socket boss protrudes beyond back face in +Y.
"""

import cadquery as cq
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
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

# Strut press-fit socket boss (replaces old heat-set insert boss)
# 12mm PETG strut press-fits into 12.1mm ID socket, secured with epoxy.
# 15mm OD boss on back face at (29.5, 23.5), 10mm tall.
# Socket: 12.1mm ID x 10mm deep (0.05mm interference fit per side on 12mm strut).
BOSS_X = 29.5
BOSS_Z = 23.5
BOSS_OD = 15.0           # outer diameter of boss cylinder
BOSS_HEIGHT = 10.0        # boss protrusion from back face (socket depth)
SOCKET_ID = 12.1          # press-fit socket for 12mm OD strut (0.05mm interference/side)

# Integral guide pins (replace old guide pin slots)
# 2x 6mm diameter PETG pins, 15mm long, protruding from back face.
# Slide in 6.5mm printed bushings in rear wall (0.25mm radial clearance).
# Positioned at same X,Z as the old guide pin slot centers.
GUIDE_PIN_DIA = 6.0       # pin diameter
GUIDE_PIN_LENGTH = 15.0   # protrusion from back face
GUIDE_PIN_CENTERS = [
    (-3.85, 23.5),   # left pin center (X, Z) — same as old left slot center
    (66.15, 23.5),   # right pin center (X, Z) — same as old right slot center
]

# Pin pads: local material reinforcement around each guide pin base
# The plate body doesn't extend to the pin X positions, so we need pad material.
# Pad extends from plate body edge to beyond the pin, with wall around the pin.
PIN_PAD_WALL = 2.0        # minimum wall around pin
PIN_PAD_DIA = GUIDE_PIN_DIA + 2 * PIN_PAD_WALL  # 10mm pad diameter
PIN_PAD_H = PIN_PAD_DIA   # pad height in Z (same as diameter for circular look)

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
     "(29.5, 3.0, 23.5)",   "59x6x47mm",                "PETG, dock-side of rear wall"),
    ("2",  "Left guide pin pad",      "Material around left pin",   "Add",    "Box",     "—",
     f"({GUIDE_PIN_CENTERS[0][0]:.2f}, 3.0, 23.5)",  f"{PIN_PAD_DIA}x{PLATE_D}x{PIN_PAD_H}mm",
     "Pad protruding left, overlaps plate body"),
    ("3",  "Right guide pin pad",     "Material around right pin",  "Add",    "Box",     "—",
     f"({GUIDE_PIN_CENTERS[1][0]:.2f}, 3.0, 23.5)",  f"{PIN_PAD_DIA}x{PLATE_D}x{PIN_PAD_H}mm",
     "Pad protruding right, overlaps plate body"),
    ("4",  "Strut press-fit boss",    "Socket for PETG strut",      "Add",    "Cyl",     "Y",
     f"({BOSS_X}, *, {BOSS_Z})", f"D{BOSS_OD}xH{BOSS_HEIGHT}mm",
     "Back face, +Y, press-fit + epoxy"),
    ("5",  "Strut socket void",       "12.1mm ID press-fit bore",   "Remove", "Cyl",     "Y",
     f"({BOSS_X}, *, {BOSS_Z})", f"D{SOCKET_ID}, thru boss+wall",
     "0.05mm interference/side on 12mm strut"),
    ("6",  "Left guide pin",          "Anti-rotation linear guide", "Add",    "Cyl",     "Y",
     f"({GUIDE_PIN_CENTERS[0][0]:.2f}, *, 23.5)", f"D{GUIDE_PIN_DIA}x{GUIDE_PIN_LENGTH}mm",
     "Back face, +Y, slides in 6.5mm bushing"),
    ("7",  "Right guide pin",         "Anti-rotation linear guide", "Add",    "Cyl",     "Y",
     f"({GUIDE_PIN_CENTERS[1][0]:.2f}, *, 23.5)", f"D{GUIDE_PIN_DIA}x{GUIDE_PIN_LENGTH}mm",
     "Back face, +Y, slides in 6.5mm bushing"),
    ("8",  "Outer bores (x4)",        "Cradle body end 15.10mm",    "Remove", "Cyl",     "Y",
     "(cx, 1.0, cz) x4",    f"D{OUTER_BORE_DIA}, {OUTER_BORE_DEPTH}mm deep", "Y=0 to Y=2, dock side"),
    ("9",  "Inner lip bores (x4)",    "Hug collet 9.57mm OD",       "Remove", "Cyl",     "Y",
     "(cx, 3.0, cz) x4",    f"D{INNER_LIP_DIA}, {INNER_LIP_DEPTH}mm deep",   "Y=2 to Y=4"),
    ("10", "Tube clearance holes (x4)","Pass tube 6.30mm OD",       "Remove", "Cyl",     "Y",
     "(cx, 3.0, cz) x4",    f"D{TUBE_HOLE_DIA}, through",         "Full depth"),
    ("11", "Outer bore chamfers (x4)", "Fitting engagement lead-in", "Remove", "Chamfer", "Y",
     "at bore, Y=0",         f"{OUTER_CHAMFER}mm x 45deg",         "Front face entry (dock side)"),
    ("12", "Tube hole chamfers (x4)",  "Ease tube threading",        "Remove", "Chamfer", "Y",
     "at bore, Y=4",         f"{TUBE_CHAMFER}mm x 45deg",          "At inner lip floor"),
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

# --- Features 2 & 3: Guide pin pads ---
# Each pad is a box centered on the pin center, providing material around the pin base.
# Must overlap with the main plate body so union produces a single solid.
for pin_cx, pin_cz in GUIDE_PIN_CENTERS:
    pad_x0 = pin_cx - PIN_PAD_DIA / 2
    pad_z0 = pin_cz - PIN_PAD_H / 2

    # Extend pad to overlap with plate body for solid fusion
    if pin_cx < 0:
        # Left pad: extend right edge into plate body
        pad_right = max(pad_x0 + PIN_PAD_DIA, 1.0)  # ensure overlap
        pad = (
            cq.Workplane("XY")
            .box(pad_right - pad_x0, PLATE_D, PIN_PAD_H, centered=False)
            .translate((pad_x0, 0, pad_z0))
        )
    else:
        # Right pad: extend left edge into plate body
        pad_left = min(pad_x0, PLATE_W - 1.0)
        pad_right = pad_x0 + PIN_PAD_DIA
        pad = (
            cq.Workplane("XY")
            .box(pad_right - pad_left, PLATE_D, PIN_PAD_H, centered=False)
            .translate((pad_left, 0, pad_z0))
        )
    plate = plate.union(pad)

# --- Feature 4: Strut press-fit socket boss ---
# 15mm OD x 10mm cylinder on back face, centered at (29.5, 23.5)
# Back face is at Y=6, boss extends to Y=6+10=16
boss = (
    cq.Workplane("XZ")
    .center(BOSS_X, BOSS_Z)
    .circle(BOSS_OD / 2)
    .extrude(-BOSS_HEIGHT)          # XZ normal is -Y; negative extrude goes +Y
    .translate((0, PLATE_D, 0))     # shift to back face
)
plate = plate.union(boss)

# --- Feature 5: Strut socket void ---
# 12.1mm diameter hole through the full boss depth (10mm) plus the plate
# structural back wall (2mm from Y=4 to Y=6).
# The hole runs from Y=4 (inner edge of structural wall) through Y=16 (boss tip).
socket_void = (
    cq.Workplane("XZ")
    .center(BOSS_X, BOSS_Z)
    .circle(SOCKET_ID / 2)
    .extrude(-(BOSS_HEIGHT + (PLATE_D - OUTER_BORE_DEPTH - INNER_LIP_DEPTH)))
    # extrude 10.0 + 2.0 = 12.0mm in +Y direction
    .translate((0, OUTER_BORE_DEPTH + INNER_LIP_DEPTH, 0))  # start at Y=4
)
plate = plate.cut(socket_void)

# --- Features 6 & 7: Integral guide pins ---
# 6mm diameter x 15mm long cylinders on back face at guide pin centers.
# Back face is at Y=6, pins extend to Y=6+15=21.
for pin_cx, pin_cz in GUIDE_PIN_CENTERS:
    pin = (
        cq.Workplane("XZ")
        .center(pin_cx, pin_cz)
        .circle(GUIDE_PIN_DIA / 2)
        .extrude(-GUIDE_PIN_LENGTH)      # XZ normal is -Y; negative extrude goes +Y
        .translate((0, PLATE_D, 0))      # shift to back face
    )
    plate = plate.union(pin)

# --- Features 8-12: Stepped bores with chamfers (x4) ---
# Revolved profile technique: define the full axial cross-section as (R, Y) points
# and revolve 360 degrees around the Y axis.
#
# Y=0 is front face (dock side, bore openings), Y=6 is back face (rear wall side).
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

# --- Features 2 & 3: Guide pin pads ---
v.check_solid("Left pad material",
              GUIDE_PIN_CENTERS[0][0], PLATE_D / 2, 23.5 + PIN_PAD_H / 2 - 0.5,
              "solid in left pad wall above pin")
v.check_solid("Right pad material",
              GUIDE_PIN_CENTERS[1][0], PLATE_D / 2, 23.5 + PIN_PAD_H / 2 - 0.5,
              "solid in right pad wall above pin")

# --- Feature 4: Strut press-fit boss (annular wall, outside socket void) ---
# Boss extends from Y=6 to Y=16 (6 + 10). Socket removes center material,
# so solid checks target the annular wall between socket and boss OD.
BOSS_TIP_Y = PLATE_D + BOSS_HEIGHT  # 16.0
BOSS_CHECK_R = (SOCKET_ID / 2 + BOSS_OD / 2) / 2  # 6.775mm from center

v.check_solid("Boss annular wall mid-height",
              BOSS_X + BOSS_CHECK_R, PLATE_D + BOSS_HEIGHT / 2, BOSS_Z,
              "solid in boss wall (between socket and OD)")
v.check_solid("Boss annular wall near tip",
              BOSS_X + BOSS_CHECK_R, BOSS_TIP_Y - 0.5, BOSS_Z,
              "solid in boss wall near tip")
v.check_solid("Boss annular wall near base",
              BOSS_X + BOSS_CHECK_R, PLATE_D + 0.5, BOSS_Z,
              "solid in boss wall near base")
v.check_void("Boss outside radius",
             BOSS_X + BOSS_OD / 2 + 0.5, PLATE_D + BOSS_HEIGHT / 2, BOSS_Z,
             "void outside boss")
v.check_void("Boss above tip",
             BOSS_X, BOSS_TIP_Y + 0.5, BOSS_Z,
             "void above boss top")

# --- Feature 5: Strut socket void ---
v.check_void("Socket void in boss",
             BOSS_X, PLATE_D + BOSS_HEIGHT / 2, BOSS_Z,
             "void at socket center in boss")
v.check_void("Socket void in structural wall",
             BOSS_X, OUTER_BORE_DEPTH + INNER_LIP_DEPTH + 1.0, BOSS_Z,
             "void at socket center in structural wall (Y=5)")
v.check_void("Socket void at boss tip",
             BOSS_X, BOSS_TIP_Y - 0.3, BOSS_Z,
             "void at socket near boss tip")

# --- Features 6 & 7: Integral guide pins ---
GUIDE_PIN_TIP_Y = PLATE_D + GUIDE_PIN_LENGTH  # 21.0
for i, (pin_cx, pin_cz) in enumerate(GUIDE_PIN_CENTERS):
    side = "Left" if i == 0 else "Right"

    # Pin center at mid-length: solid
    v.check_solid(f"{side} guide pin center",
                  pin_cx, PLATE_D + GUIDE_PIN_LENGTH / 2, pin_cz,
                  f"solid at {side.lower()} pin center, mid-length")

    # Pin near tip: solid
    v.check_solid(f"{side} guide pin near tip",
                  pin_cx, GUIDE_PIN_TIP_Y - 0.5, pin_cz,
                  f"solid at {side.lower()} pin near tip")

    # Pin near base: solid
    v.check_solid(f"{side} guide pin near base",
                  pin_cx, PLATE_D + 0.5, pin_cz,
                  f"solid at {side.lower()} pin near base")

    # Outside pin radius: void
    v.check_void(f"{side} guide pin outside radius",
                 pin_cx + GUIDE_PIN_DIA / 2 + 0.5, PLATE_D + GUIDE_PIN_LENGTH / 2, pin_cz,
                 f"void outside {side.lower()} pin")

    # Above pin tip: void
    v.check_void(f"{side} guide pin above tip",
                 pin_cx, GUIDE_PIN_TIP_Y + 0.5, pin_cz,
                 f"void above {side.lower()} pin tip")

# --- Features 8-12: Stepped bores (x4) ---
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

# --- Rubric 4: Solid validity ---
v.check_valid()
v.check_single_body()
v.check_volume(expected_envelope=PLATE_W * PLATE_D * PLATE_H, fill_range=(0.5, 1.5))

# --- Rubric 5: Bounding box ---
bb = plate.val().BoundingBox()

# Expected bounds:
# X: left pad extends to pin_cx - pad_dia/2 = -3.85 - 5.0 = -8.85
#    right pad extends to pin_cx + pad_dia/2 = 66.15 + 5.0 = 71.15
# Y: 0.0 to PLATE_D + GUIDE_PIN_LENGTH = 6.0 + 15.0 = 21.0 (pins are tallest)
# Z: 0.0 to 47.0

exp_xmin = GUIDE_PIN_CENTERS[0][0] - PIN_PAD_DIA / 2   # -8.85
exp_xmax = GUIDE_PIN_CENTERS[1][0] + PIN_PAD_DIA / 2   # 71.15
exp_ymin = 0.0
exp_ymax = PLATE_D + GUIDE_PIN_LENGTH                   # 21.0
exp_zmin = 0.0
exp_zmax = PLATE_H                                       # 47.0

v.check_bbox("X", bb.xmin, bb.xmax, exp_xmin, exp_xmax)
v.check_bbox("Y", bb.ymin, bb.ymax, exp_ymin, exp_ymax)
v.check_bbox("Z", bb.zmin, bb.zmax, exp_zmin, exp_zmax)

# ============================================================
# SUMMARY
# ============================================================
if not v.summary():
    sys.exit(1)
