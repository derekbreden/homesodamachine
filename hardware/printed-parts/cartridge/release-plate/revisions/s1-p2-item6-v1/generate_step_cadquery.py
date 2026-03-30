"""
Release Plate v2 — CadQuery STEP Generation Script
Pipeline step: 6g — STEP Generation
Input: planning/parts.md, planning/spatial-resolution.md
Output: release-plate-cadquery.step

Part: Single printed PETG sliding actuator that simultaneously depresses the
rear-facing collets of four PP0408W quick-connect fittings.

v2 change: 4 struts (TL, TR, BL, BR) replacing 2.  Struts extend from the
plate front face (Y=0) in the −Y direction.  Positions derived from the bore
column X-values (9.0 and 71.0) at Z=60.0 (above top bores) and Z=5.0 (below
bottom bores), each clearing the nearest bore outer circle by 1.7 mm.

Coordinate system (part local frame):
  Origin: plate bottom-left-front corner (X=0, Y=0, Z=0)
  X: plate width, left to right, 0 → 80.0 mm
  Y: plate depth, front (user-facing, build-plate face) to rear (fitting-facing)
       Y=0  = front face (pull surface, sits on build plate in print orientation)
       Y=5  = rear face (bore-entry face, faces PP0408W fittings)
       Y=-90 = strut tips (90 mm beyond front face, toward user/lever)
       Y=35  = guide pin tips (30 mm beyond rear face)
  Z: plate height, bottom to top, 0 → 65.0 mm
  Plate envelope:          X:[0,80]   Y:[0,5]     Z:[0,65]
  With guide pins:         X:[0,80]   Y:[0,35]    Z:[0,65]
  With struts:             X:[0,80]   Y:[-90,0]   Z:[0,65]
  Full bounding box:       X:[0,80]   Y:[-90,35]  Z:[0,65]

CadQuery XZ workplane notes (verified by test):
  XZ workplane origin: (0,0,0), normal (zDir): (0,-1,0) = -Y direction
  workplane(offset=X) shifts plane by X in the normal direction (-Y):
    offset=-5 → plane at Y = 0 + (-5)*(-1) = +5  (REAR FACE)
    offset=+5 → plane at Y = 0 + (+5)*(-1) = -5  (outside part — WRONG)
  extrude(positive) → goes in normal direction (-Y)
  extrude(negative) → goes opposite to normal (+Y)

  For bores running Y=5 → Y=0 (rear to front, -Y direction):
    Use offset=-Y_start (e.g., offset=-5.0 for plane at Y=5)
    Extrude positive depth (goes -Y from plane)

  For pins running Y=5 → Y=35 (rear outward, +Y direction):
    Use offset=-5.0 (plane at Y=5)
    Extrude negative length (goes +Y from plane)

  For struts running Y=0 → Y=-90 (front outward, -Y direction):
    Use plain XY workplane at Y=0 (default), then translate strut box
    to its correct position using transformed(offset=...).
"""

import sys
from pathlib import Path

import cadquery as cq

# Add tools/ to sys.path for step_validate
# Script is at: hardware/printed-parts/cartridge/release-plate/generate_step_cadquery.py
# parents[4] = project root
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))
from step_validate import Validator

# ==============================================================================
# Part parameters (from parts.md and spatial-resolution.md)
# ==============================================================================

PLATE_W = 80.0   # X extent
PLATE_D = 5.0    # Y extent (thickness)
PLATE_H = 65.0   # Z extent

# Bore zone diameters
Z1_D = 15.60    # Zone 1 (outer counterbore)
Z2_D = 10.07    # Zone 2 (inner lip bore)
Z3_D = 6.50     # Zone 3 (tube clearance through-hole)

Z1_R = Z1_D / 2   # 7.80
Z2_R = Z2_D / 2   # 5.035
Z3_R = Z3_D / 2   # 3.25

# Zone Y boundaries (measured from front face, Y increases toward rear)
Y_REAR     = 5.0   # rear face
Y_Z1_FLOOR = 3.6   # Zone 1 floor / Zone 2 top
Y_Z2_FLOOR = 1.6   # Zone 2 floor / Zone 3 top
Y_FRONT    = 0.0   # front face

# Bore center positions (X, Z) — all four bores identical geometry
BORE_CENTERS = [
    (9.0,  47.5),   # A — Pump 1 Inlet (top-left)
    (9.0,  17.5),   # B — Pump 1 Outlet (bottom-left)
    (71.0, 47.5),   # C — Pump 2 Inlet (top-right)
    (71.0, 17.5),   # D — Pump 2 Outlet (bottom-right)
]

# Guide pin parameters
PIN_D   = 5.0
PIN_R   = PIN_D / 2    # 2.5
PIN_Y0  = 5.0          # pin base at rear face
PIN_Y1  = 35.0         # pin tip (30 mm projection from rear face)
PIN_LEN = PIN_Y1 - PIN_Y0  # 30.0 mm

PIN1_X, PIN1_Z = 5.0,  60.0   # Guide pin 1 (top-left)
PIN2_X, PIN2_Z = 75.0,  5.0   # Guide pin 2 (bottom-right)

# Strut parameters (Features 10-13)
STRUT_W  = 6.0    # X cross-section
STRUT_H  = 6.0    # Z cross-section
STRUT_L  = 90.0   # Y length
STRUT_Y0 = 0.0    # strut base at front face (Y=0)
STRUT_Y1 = -90.0  # strut tips (90 mm beyond front face, toward user)

# Strut center positions (X, Z) — derived from bore pattern
# X values match bore columns; Z values clear bore outer circles by 1.7 mm
# Clearance check: strut half-height 3.0 mm + bore outer radius 7.8 mm = 10.8 mm
#   Bore A center Z=47.5: strut center Z=60.0 → gap = 60.0-47.5-10.8 = 1.7 mm ✓
#   Bore B center Z=17.5: strut center Z= 5.0 → gap = 17.5-5.0-10.8  = 1.7 mm ✓
STRUTS = {
    "TL": (9.0,  60.0),   # Top-Left:     above bore A
    "TR": (71.0, 60.0),   # Top-Right:    above bore C
    "BL": (9.0,   5.0),   # Bottom-Left:  below bore B
    "BR": (71.0,  5.0),   # Bottom-Right: below bore D
}

# Fillet radii
CORNER_R = 2.0   # Perimeter corner radii (4 vertical edges parallel to Y)
PULL_R   = 3.0   # Pull edge radius (4 front-face perimeter edges)

# ==============================================================================
# Rubric 1 — Feature Planning Table
# ==============================================================================

FEATURE_TABLE = """
RELEASE PLATE v2 — FEATURE PLANNING TABLE (Rubric 1)
======================================================

  #   Feature Name              Op      Shape         Axis  Center / Position                Dimensions
  1   Plate body                Add     Rect prism    Y     Origin (0,0,0)                   80W × 5D × 65H mm
  2   Perimeter corner radii    Remove  Fillet R2     Y     4 vertical edges at XZ corners   R = 2.0 mm
  3   Pull edge radius          Remove  Fillet R3     X,Z   4 front-face perimeter edges      R = 3.0 mm
  4   Stepped bore A            Remove  3-step cyl    Y     X=9.0, Z=47.5                    Z1:Ø15.60 Z2:Ø10.07 Z3:Ø6.50
  5   Stepped bore B            Remove  3-step cyl    Y     X=9.0, Z=17.5                    (same)
  6   Stepped bore C            Remove  3-step cyl    Y     X=71.0, Z=47.5                   (same)
  7   Stepped bore D            Remove  3-step cyl    Y     X=71.0, Z=17.5                   (same)
  8   Guide pin 1               Add     Cylinder      Y     X=5.0, Z=60.0                    Ø5.0 mm, Y:5→35 (30 mm)
  9   Guide pin 2               Add     Cylinder      Y     X=75.0, Z=5.0                    Ø5.0 mm, Y:5→35 (30 mm)
  10  Strut TL (Top-Left)       Add     Rect prism    Y     X=9.0, Z=60.0                    6W × 90D × 6H mm, Y:0→-90
  11  Strut TR (Top-Right)      Add     Rect prism    Y     X=71.0, Z=60.0                   6W × 90D × 6H mm, Y:0→-90
  12  Strut BL (Bottom-Left)    Add     Rect prism    Y     X=9.0, Z=5.0                     6W × 90D × 6H mm, Y:0→-90
  13  Strut BR (Bottom-Right)   Add     Rect prism    Y     X=71.0, Z=5.0                    6W × 90D × 6H mm, Y:0→-90

Bore zone detail (identical for all 4 bores):
  Zone 1 (outer counterbore): Ø15.60 mm, Y: 5.0 → 3.6 mm (depth 1.4 mm from rear face)
  Zone 2 (inner lip bore):    Ø10.07 mm, Y: 3.6 → 1.6 mm (depth 2.0 mm)
  Zone 3 (through-hole):      Ø 6.50 mm, Y: 1.6 → 0.0 mm (depth 1.6 mm, exits front face)

Strut clearances (all struts):
  Struts TL/TR: nearest bore outer edge at Z=47.5+7.8=55.3; strut near edge at Z=57.0 → gap 1.7 mm ✓
  Struts BL/BR: nearest bore outer edge at Z=17.5-7.8= 9.7; strut near edge at Z= 8.0 → gap 1.7 mm ✓

Coordinate system declaration (Rubric 2):
  Origin: plate bottom-left-front corner
  X: plate width, left to right, 0 → 80.0 mm
  Y: plate depth, front (Y=0) to rear (Y=5), pins to Y=35, struts to Y=-90
  Z: plate height, bottom to top, 0 → 65.0 mm
  Full bounding box: X:[0,80] Y:[-90,35] Z:[0,65]

XZ workplane convention (verified):
  Normal = -Y direction.
  offset = -Y_position (offset=-5.0 puts plane at Y=5.0)
  positive extrude = -Y direction (from plane toward front)
  negative extrude = +Y direction (from plane toward rear)
"""

# ==============================================================================
# Modeling
# ==============================================================================

print("=" * 70)
print("RELEASE PLATE v2 — CadQuery STEP Generation")
print("=" * 70)
print(FEATURE_TABLE)
print("Building model...")

# ------------------------------------------------------------------------------
# Feature 1: Plate body
# box(W, D, H, centered=False) with W=80 (X), D=5 (Y), H=65 (Z)
# → X:[0,80] Y:[0,5] Z:[0,65]
# ------------------------------------------------------------------------------
plate = cq.Workplane("XY").box(PLATE_W, PLATE_D, PLATE_H, centered=False)
print("  [+] Feature 1: Plate body (80 × 5 × 65 mm)")

# ------------------------------------------------------------------------------
# Feature 2: Perimeter corner radii — R2 on 4 vertical edges (parallel to Y)
# These are the edges at (X=0,Z=0), (X=80,Z=0), (X=0,Z=65), (X=80,Z=65)
# running in the Y direction. Select with "|Y" edge filter.
# ------------------------------------------------------------------------------
plate = plate.edges("|Y").fillet(CORNER_R)
print("  [+] Feature 2: Corner radii R2.0 on 4 vertical (Y-parallel) edges")

# ------------------------------------------------------------------------------
# Feature 3: Pull edge radius — R3 on 4 front-face perimeter edges (at Y=0)
# These are the 4 perimeter edges of the front face (minimum Y face).
# Select with face("<Y") then edges().
# ------------------------------------------------------------------------------
plate = plate.faces("<Y").edges().fillet(PULL_R)
print("  [+] Feature 3: Pull edge radius R3.0 on front-face (Y=0) perimeter edges")

# ------------------------------------------------------------------------------
# Features 4-7: Stepped bores A, B, C, D
#
# Each bore runs along -Y from rear face (Y=5) to front face (Y=0).
# Three cylindrical zones are cut separately (equivalent to revolved profile).
#
# XZ workplane convention:
#   - workplane(offset=-Y_pos) places the XZ plane at Y = Y_pos
#   - positive extrude depth goes in -Y direction (from plane toward front face)
#   - center(cx, cz) on XZ sets X=cx, Z=cz
#
# Zone 1: Ø15.60 mm, from Y=5.0 → Y=3.6 (depth 1.4 mm, opens at rear face)
# Zone 2: Ø10.07 mm, from Y=3.6 → Y=1.6 (depth 2.0 mm)
# Zone 3: Ø 6.50 mm, from Y=1.6 → Y=0.0 (depth 1.6 mm, exits front face)
# ------------------------------------------------------------------------------

for bore_idx, (cx, cz) in enumerate(BORE_CENTERS):
    label = ["A", "B", "C", "D"][bore_idx]

    # Zone 1: plane at Y=5.0, extrude 1.4 mm toward front (−Y)
    zone1 = (
        cq.Workplane("XZ")
        .workplane(offset=-Y_REAR)         # offset=-5.0 → plane at Y=5.0
        .center(cx, cz)
        .circle(Z1_R)
        .extrude(Y_REAR - Y_Z1_FLOOR)      # 1.4 mm in -Y direction
    )
    plate = plate.cut(zone1)

    # Zone 2: plane at Y=3.6, extrude 2.0 mm toward front (−Y)
    zone2 = (
        cq.Workplane("XZ")
        .workplane(offset=-Y_Z1_FLOOR)     # offset=-3.6 → plane at Y=3.6
        .center(cx, cz)
        .circle(Z2_R)
        .extrude(Y_Z1_FLOOR - Y_Z2_FLOOR)  # 2.0 mm in -Y direction
    )
    plate = plate.cut(zone2)

    # Zone 3: plane at Y=1.6, extrude 1.6 mm toward front (−Y)
    zone3 = (
        cq.Workplane("XZ")
        .workplane(offset=-Y_Z2_FLOOR)     # offset=-1.6 → plane at Y=1.6
        .center(cx, cz)
        .circle(Z3_R)
        .extrude(Y_Z2_FLOOR - Y_FRONT)     # 1.6 mm in -Y direction
    )
    plate = plate.cut(zone3)

    print(f"  [-] Feature {4 + bore_idx}: Stepped bore {label} at X={cx}, Z={cz}")

# ------------------------------------------------------------------------------
# Feature 8: Guide Pin 1
# Ø5 mm cylinder, center at (X=5.0, Z=60.0), extends from Y=5.0 to Y=35.0
# (30 mm outward from rear face in +Y direction).
#
# XZ workplane at Y=5.0 (offset=-5.0), extrude negative → +Y direction
# negative extrude on XZ (normal=-Y) goes opposite to normal = +Y
# ------------------------------------------------------------------------------
pin1 = (
    cq.Workplane("XZ")
    .workplane(offset=-PIN_Y0)         # offset=-5.0 → plane at Y=5.0 (rear face)
    .center(PIN1_X, PIN1_Z)            # X=5.0, Z=60.0
    .circle(PIN_R)
    .extrude(-PIN_LEN)                 # negative extrude → +Y direction → Y: 5→35
)
plate = plate.union(pin1)
print(f"  [+] Feature 8: Guide Pin 1 at X={PIN1_X}, Z={PIN1_Z}, Y:{PIN_Y0}→{PIN_Y1}")

# Feature 9: Guide Pin 2
pin2 = (
    cq.Workplane("XZ")
    .workplane(offset=-PIN_Y0)         # plane at Y=5.0
    .center(PIN2_X, PIN2_Z)            # X=75.0, Z=5.0
    .circle(PIN_R)
    .extrude(-PIN_LEN)                 # +Y direction → Y: 5→35
)
plate = plate.union(pin2)
print(f"  [+] Feature 9: Guide Pin 2 at X={PIN2_X}, Z={PIN2_Z}, Y:{PIN_Y0}→{PIN_Y1}")

# ------------------------------------------------------------------------------
# Features 10-13: Struts TL, TR, BL, BR
#
# Each strut is a 6×6 mm rectangular prism extending from Y=0 (front face)
# to Y=-90 (toward user/lever). The strut base is flush with the plate front
# face; the strut tips are plain square ends (no joinery).
#
# Placement: center at (cx, cz) in XZ, Y from STRUT_Y1 to STRUT_Y0 (i.e.
# from -90 to 0). The box starts at (cx - STRUT_W/2, STRUT_Y1, cz - STRUT_H/2)
# and has dimensions (STRUT_W, STRUT_L, STRUT_H).
#
# Using XY workplane with transformed(offset=...) to position each strut:
#   transformed(offset=Vector(x0, y0, z0)) moves the workplane origin to (x0,y0,z0)
#   box(W, D, H, centered=False) then places the box at X:[0,W] Y:[0,D] Z:[0,H]
#   relative to the new origin.
#
# For a strut with center (cx, cz), Y from STRUT_Y1 (-90) to STRUT_Y0 (0):
#   origin = (cx - STRUT_W/2, STRUT_Y1, cz - STRUT_H/2)
#   box(STRUT_W, STRUT_L, STRUT_H, centered=False)
#   → X:[cx-3, cx+3]  Y:[-90, 0]  Z:[cz-3, cz+3]
# ------------------------------------------------------------------------------
strut_feature_num = 10
for label, (cx, cz) in STRUTS.items():
    sx0 = cx - STRUT_W / 2    # left X edge of strut
    sz0 = cz - STRUT_H / 2    # bottom Z edge of strut
    sy0 = STRUT_Y1             # Y start = -90.0 (tip end)
    strut = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(sx0, sy0, sz0))
        .box(STRUT_W, STRUT_L, STRUT_H, centered=False)
    )
    plate = plate.union(strut)
    print(f"  [+] Feature {strut_feature_num}: Strut {label} center (X={cx}, Z={cz}), "
          f"box X:[{sx0},{cx+STRUT_W/2}] Y:[{sy0},{STRUT_Y0}] Z:[{sz0},{cz+STRUT_H/2}]")
    strut_feature_num += 1

print()
print("Model construction complete.")
print()

# ==============================================================================
# Validation (Rubric 3, 4, 5)
# ==============================================================================

print("=" * 70)
print("VALIDATION")
print("=" * 70)

v = Validator(plate)

print()
print("--- Feature 1: Plate body ---")
v.check_solid("Plate body interior", 40.0, 2.5, 32.5,
              "solid at plate center (40, 2.5, 32.5)")

print()
print("--- Features 4-7: Stepped bores ---")
bore_labels = ["A", "B", "C", "D"]
for bore_idx, (cx, cz) in enumerate(BORE_CENTERS):
    label = bore_labels[bore_idx]

    # Zone 1: probe at Y=4.5 (inside Zone 1, between Y=5 and Y=3.6)
    v.check_void(f"Bore {label} Zone1 void",
                 cx, 4.5, cz,
                 f"void at bore {label} center, Y=4.5 (Zone1 outer bore)")

    # Zone 2: probe at Y=2.5 (inside Zone 2, between Y=3.6 and Y=1.6)
    v.check_void(f"Bore {label} Zone2 void",
                 cx, 2.5, cz,
                 f"void at bore {label} center, Y=2.5 (Zone2 inner lip)")

    # Zone 3: probe at Y=0.8 (inside Zone 3, between Y=1.6 and Y=0)
    v.check_void(f"Bore {label} Zone3 void",
                 cx, 0.8, cz,
                 f"void at bore {label} center, Y=0.8 (Zone3 through-hole)")

    # Check that material exists in the annular wall between Z1 and Z2 at Zone2 depth
    if cx < 40:
        wall_x = cx + 9.0
    else:
        wall_x = cx - 9.0
    v.check_solid(f"Bore {label} wall solid",
                  wall_x, 2.5, cz,
                  f"solid in plate wall beside bore {label} at X={wall_x}, Y=2.5")

    # Check Zone1→Zone2 step annular wall at Y=2.5
    step_offset = (Z1_R + Z2_R) / 2   # ~6.4 mm from center
    if cx < 40:
        step_x = cx + step_offset
    else:
        step_x = cx - step_offset
    v.check_solid(f"Bore {label} annular step wall",
                  step_x, 2.5, cz,
                  f"solid in annular ring between Z1 and Z2 radii at Y=2.5")

print()
print("--- Features 8-9: Guide pins ---")
pin1_mid_y = (PIN_Y0 + PIN_Y1) / 2   # 20.0 mm
v.check_solid("Guide Pin 1 body",
              PIN1_X, pin1_mid_y, PIN1_Z,
              f"solid inside pin 1 body at ({PIN1_X}, {pin1_mid_y}, {PIN1_Z})")
v.check_solid("Guide Pin 2 body",
              PIN2_X, pin1_mid_y, PIN2_Z,
              f"solid inside pin 2 body at ({PIN2_X}, {pin1_mid_y}, {PIN2_Z})")

v.check_solid("Guide Pin 1 mid-extension",
              PIN1_X, 10.0, PIN1_Z,
              f"solid in pin 1 extension at Y=10 (beyond plate)")
v.check_solid("Guide Pin 2 mid-extension",
              PIN2_X, 10.0, PIN2_Z,
              f"solid in pin 2 extension at Y=10 (beyond plate)")

v.check_void("Void beside Pin 1",
             PIN1_X + PIN_R + 1.0, 10.0, PIN1_Z,
             f"void outside pin 1 radius at Y=10")

print()
print("--- Features 10-13: Struts ---")
strut_mid_y = (STRUT_Y0 + STRUT_Y1) / 2   # -45.0 mm (midpoint of strut length)
for label, (cx, cz) in STRUTS.items():
    # Probe solid at strut center (midpoint of length)
    v.check_solid(f"Strut {label} body center",
                  cx, strut_mid_y, cz,
                  f"solid at strut {label} center (X={cx}, Y={strut_mid_y}, Z={cz})")

    # Probe solid at strut base (Y just inside front face, inside strut)
    v.check_solid(f"Strut {label} base",
                  cx, -1.0, cz,
                  f"solid at strut {label} base (Y=-1.0, just beyond front face)")

    # Probe solid near strut tip
    v.check_solid(f"Strut {label} tip",
                  cx, STRUT_Y1 + 1.0, cz,
                  f"solid near strut {label} tip (Y={STRUT_Y1 + 1.0})")

    # Probe void just outside strut X extent (in X direction)
    void_x = cx + STRUT_W / 2 + 1.0   # 1 mm outside right edge of strut
    v.check_void(f"Strut {label} void beside X+",
                 void_x, strut_mid_y, cz,
                 f"void outside strut {label} X+ edge at X={void_x}")

    # Probe void just outside strut Z extent (in Z direction)
    void_z = cz + STRUT_H / 2 + 1.0   # 1 mm outside top edge of strut
    v.check_void(f"Strut {label} void beside Z+",
                 cx, strut_mid_y, void_z,
                 f"void outside strut {label} Z+ edge at Z={void_z}")

print()
print("--- Bounding box (Rubric 5) ---")
bb = plate.val().BoundingBox()
print(f"  Actual bounding box:")
print(f"    X: [{bb.xmin:.3f}, {bb.xmax:.3f}]  (expected [0, 80])")
print(f"    Y: [{bb.ymin:.3f}, {bb.ymax:.3f}]  (expected [-90, 35])")
print(f"    Z: [{bb.zmin:.3f}, {bb.zmax:.3f}]  (expected [0, 65])")

v.check_bbox("X", bb.xmin, bb.xmax, 0.0, 80.0, tol=0.5)
v.check_bbox("Y", bb.ymin, bb.ymax, -90.0, 35.0, tol=0.5)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, 65.0, tol=0.5)

print()
print("--- Solid integrity (Rubric 4) ---")
v.check_valid()
v.check_single_body()

# Volume estimate:
# Plate body:  80 × 5 × 65 = 26000 mm³
# + 2 pins:    2 × π × 2.5² × 30 ≈ 1178 mm³
# + 4 struts:  4 × 6 × 90 × 6   = 12960 mm³
# - 4 bores (approx):
#   Zone1: 4 × π × 7.8² × 1.4 ≈ 1070 mm³
#   Zone2: 4 × π × 5.035² × 2.0 ≈ 637 mm³
#   Zone3: 4 × π × 3.25² × 1.6 ≈ 212 mm³
#   Total bore removal: ≈ 1919 mm³
# Estimated total: ≈ 26000 + 1178 + 12960 - 1919 ≈ 38219 mm³
# Full envelope: 80 × 125 × 65 = 650000 mm³  (Y span = 35 - (-90) = 125)
# Fill ratio: 38219 / 650000 ≈ 5.9%
v.check_volume(expected_envelope=PLATE_W * (PIN_Y1 - STRUT_Y1) * PLATE_H,
               fill_range=(0.04, 0.12))

print()
passed = v.summary()

if not passed:
    print()
    print("FAIL: Validation failures detected. Exiting without writing STEP file.")
    sys.exit(1)

# ==============================================================================
# Export STEP
# ==============================================================================

output_path = Path(__file__).parent / "release-plate-cadquery.step"
cq.exporters.export(plate, str(output_path))
print()
print(f"SUCCESS: STEP file written to:")
print(f"  {output_path}")
print("Done.")
