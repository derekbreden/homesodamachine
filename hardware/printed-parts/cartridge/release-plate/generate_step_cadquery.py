"""
Release Plate v5 -- CadQuery STEP Generation Script
Pipeline step: 6g -- STEP Generation
Input: planning/parts.md
Output: release-plate-cadquery.step

Part: Single printed PETG sliding actuator that simultaneously depresses the
rear-facing collets of four PP0408W quick-connect fittings.

v5 change: Widen plate to 140.0mm and move struts to match lever/pump tray positions.
  - Plate width updated from 137.2mm to 140.0mm (matches all interior plates).
  - Strut centers moved from (10.0, 127.2) to (4.0, 136.0) in X to match
    lever strut positions and pump tray bore centers.
  - Bore positions unchanged (1x4 row at Z=34.3).
  - All other dimensions unchanged.

Coordinate system (part local frame):
  Origin: plate bottom-left corner at fitting-facing face (X=0, Y=0, Z=0)
  X: plate width, left to right, 0 -> 160.0 mm
  Y: plate depth, fitting-facing to user-facing; struts extend beyond user-facing face
       Y=0  = fitting-facing face (tube exit side, sits on build plate in print orientation)
       Y=5  = user-facing face (stepped bore entry, pull surface, struts attach here)
       Y=95 = strut tips (90 mm beyond user-facing face, toward lever)
  Z: plate height, bottom to top, 0 -> 68.6 mm
  Plate envelope:          X:[0,160.0]  Y:[0,5]     Z:[0,68.6]
  With struts:             X:[0,160.0]  Y:[0,95]    Z:[0,68.6]

CadQuery XZ workplane notes:
  XZ workplane origin: (0,0,0), normal (zDir): (0,-1,0) = -Y direction
  workplane(offset=X) shifts plane by X in the normal direction (-Y):
    offset=-5 -> plane at Y = 0 + (-5)*(-1) = +5  (USER-FACING FACE)
    offset=+5 -> plane at Y = 0 + (+5)*(-1) = -5  (outside part)
  extrude(positive) -> goes in normal direction (-Y)
  extrude(negative) -> goes opposite to normal (+Y)

  For bores running Y=5 -> Y=0 (user-facing to fitting-facing, -Y direction):
    Use offset=-Y_start (e.g., offset=-5.0 for plane at Y=5)
    Extrude positive depth (goes -Y from plane)

  For struts running Y=5 -> Y=95 (user-facing outward, +Y direction):
    Use plain XY workplane, then translate strut box to correct position.
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
# Part parameters (from parts.md v5)
# ==============================================================================

PLATE_W = 160.0  # X extent (was 140.0, +20mm to accommodate struts moved outward)
PLATE_D = 5.0    # Y extent (thickness)
PLATE_H = 68.6   # Z extent -- unchanged

# Bore zone diameters (unchanged)
Z1_D = 15.60    # Zone 1 (outer counterbore)
Z2_D = 10.07    # Zone 2 (inner lip bore)
Z3_D = 7.00     # Zone 3 (tube clearance through-hole)

Z1_R = Z1_D / 2   # 7.80
Z2_R = Z2_D / 2   # 5.035
Z3_R = Z3_D / 2   # 3.25

# Zone Y boundaries (measured from fitting-facing face, Y increases toward user)
Y_USER     = 5.0   # user-facing face (stepped bore entry, struts)
Y_Z1_FLOOR = 3.6   # Zone 1 floor / Zone 2 top
Y_Z2_FLOOR = 2.4   # Zone 2 floor / Zone 3 top (inner shoulder)
Y_FITTING  = 0.0   # fitting-facing face (tube exit, build plate)

# Bore center positions (X, Z) -- 1x4 row matching coupler tray (unchanged)
BORE_CENTERS = [
    (54.5, 34.3),   # A -- H1 (centered)
    (71.5, 34.3),   # B -- H2 (centered)
    (88.5, 34.3),   # C -- H3 (centered)
    (105.5, 34.3),  # D -- H4 (centered)
]

# Strut parameters (Features 10-13)
STRUT_W  = 6.0    # X cross-section
STRUT_H  = 6.0    # Z cross-section
STRUT_L  = 90.0   # Y length
STRUT_Y0 = 5.0    # strut base at user-facing face (Y=5)
STRUT_Y1 = 95.0   # strut tips (90 mm beyond user-facing face, toward lever)

# Strut center positions (X, Z) -- moved to match lever and pump tray bore centers
STRUTS = {
    "TL": (4.0,   51.1),   # Top-Left corner -- matches lever TL
    "TR": (156.0, 51.1),   # Top-Right corner -- matches lever TR
    "BL": (4.0,   17.5),   # Bottom-Left corner -- matches lever BL
    "BR": (156.0, 17.5),   # Bottom-Right corner -- matches lever BR
}

# Fillet radii
CORNER_R = 2.0   # Perimeter corner radii (4 vertical edges parallel to Y)
PULL_R   = 3.0   # Pull edge radius (4 fitting-face perimeter edges at Y=0)

# ==============================================================================
# Rubric 1 -- Feature Planning Table
# ==============================================================================

FEATURE_TABLE = """
RELEASE PLATE v5 -- FEATURE PLANNING TABLE (Rubric 1)
======================================================

  #   Feature Name              Op      Shape         Axis  Center / Position                Dimensions
  1   Plate body                Add     Rect prism    Y     Origin (0,0,0)                   160.0W x 5D x 68.6H mm
  2   Perimeter corner radii    Remove  Fillet R2     Y     4 vertical edges at XZ corners   R = 2.0 mm
  3   Pull edge radius          Remove  Fillet R3     X,Z   4 fitting-face perimeter edges    R = 3.0 mm
  4   Stepped bore A            Remove  3-step cyl    Y     X=53.1, Z=34.3                   Z1:D15.60 Z2:D10.07 Z3:D6.50
  5   Stepped bore B            Remove  3-step cyl    Y     X=70.1, Z=34.3                   (same)
  6   Stepped bore C            Remove  3-step cyl    Y     X=87.1, Z=34.3                   (same)
  7   Stepped bore D            Remove  3-step cyl    Y     X=104.1, Z=34.3                  (same)
  10  Strut TL (Top-Left)       Add     Rect prism    Y     X=4.0, Z=63.6                    6W x 90D x 6H mm, Y:5->95
  11  Strut TR (Top-Right)      Add     Rect prism    Y     X=156.0, Z=63.6                  6W x 90D x 6H mm, Y:5->95
  12  Strut BL (Bottom-Left)    Add     Rect prism    Y     X=4.0, Z=5.0                     6W x 90D x 6H mm, Y:5->95
  13  Strut BR (Bottom-Right)   Add     Rect prism    Y     X=156.0, Z=5.0                   6W x 90D x 6H mm, Y:5->95

Bore zone detail (identical for all 4 bores):
  Zone 1 (outer counterbore): D15.60 mm, Y: 5.0 -> 3.6 mm (depth 1.4 mm from user-facing face)
  Zone 2 (inner lip bore):    D10.07 mm, Y: 3.6 -> 1.6 mm (depth 2.0 mm)
  Zone 3 (through-hole):      D 6.50 mm, Y: 1.6 -> 0.0 mm (depth 1.6 mm, exits fitting-facing face)

Bore pattern: 1x4 row at Z=34.3, X=53.1/70.1/87.1/104.1 (17mm c-c spacing).

Strut positions match lever strut centers:
  TL (4.0, 63.6), TR (156.0, 63.6), BL (4.0, 5.0), BR (156.0, 5.0)

Coordinate system declaration (Rubric 2):
  Origin: plate bottom-left corner at fitting-facing face
  X: plate width, left to right, 0 -> 160.0 mm
  Y: plate depth, fitting-facing (Y=0) to user-facing (Y=5), struts to Y=95
  Z: plate height, bottom to top, 0 -> 68.6 mm
  Full bounding box: X:[0,160.0] Y:[0,95] Z:[0,68.6]
"""

# ==============================================================================
# Modeling
# ==============================================================================

print("=" * 70)
print("RELEASE PLATE v5 -- CadQuery STEP Generation")
print("=" * 70)
print(FEATURE_TABLE)
print("Building model...")

# ------------------------------------------------------------------------------
# Feature 1: Plate body
# box(W, D, H, centered=False) with W=140.0 (X), D=5 (Y), H=68.6 (Z)
# -> X:[0,160.0] Y:[0,5] Z:[0,68.6]
# ------------------------------------------------------------------------------
plate = cq.Workplane("XY").box(PLATE_W, PLATE_D, PLATE_H, centered=False)
print("  [+] Feature 1: Plate body (160.0 x 5 x 68.6 mm)")

# ------------------------------------------------------------------------------
# Feature 2: Perimeter corner radii -- R2 on 4 vertical edges (parallel to Y)
# These are the edges at (X=0,Z=0), (X=140.0,Z=0), (X=0,Z=68.6), (X=140.0,Z=68.6)
# running in the Y direction. Select with "|Y" edge filter.
# ------------------------------------------------------------------------------
plate = plate.edges("|Y").fillet(CORNER_R)
print("  [+] Feature 2: Corner radii R2.0 on 4 vertical (Y-parallel) edges")

# ------------------------------------------------------------------------------
# Feature 3: Pull edge radius -- R3 on 4 fitting-face perimeter edges (at Y=0)
# These are the 4 perimeter edges of the fitting-facing face (minimum Y face).
# Select with face("<Y") then edges().
# ------------------------------------------------------------------------------
plate = plate.faces("<Y").edges().fillet(PULL_R)
print("  [+] Feature 3: Pull edge radius R3.0 on fitting-face (Y=0) perimeter edges")

# ------------------------------------------------------------------------------
# Features 4-7: Stepped bores A, B, C, D
#
# Each bore runs along -Y from user-facing face (Y=5) to fitting-facing face (Y=0).
# Three cylindrical zones are cut separately.
#
# XZ workplane convention:
#   - workplane(offset=-Y_pos) places the XZ plane at Y = Y_pos
#   - positive extrude depth goes in -Y direction (from plane toward fitting face)
#   - center(cx, cz) on XZ sets X=cx, Z=cz
#
# Zone 1: D15.60 mm, from Y=5.0 -> Y=3.6 (depth 1.4 mm, opens at user-facing face)
# Zone 2: D10.07 mm, from Y=3.6 -> Y=1.6 (depth 2.0 mm)
# Zone 3: D 6.50 mm, from Y=1.6 -> Y=0.0 (depth 1.6 mm, exits fitting-facing face)
# ------------------------------------------------------------------------------

for bore_idx, (cx, cz) in enumerate(BORE_CENTERS):
    label = ["A", "B", "C", "D"][bore_idx]

    # Zone 1: plane at Y=5.0, extrude 1.4 mm toward fitting face (-Y)
    zone1 = (
        cq.Workplane("XZ")
        .workplane(offset=-Y_USER)         # offset=-5.0 -> plane at Y=5.0
        .center(cx, cz)
        .circle(Z1_R)
        .extrude(Y_USER - Y_Z1_FLOOR)      # 1.4 mm in -Y direction
    )
    plate = plate.cut(zone1)

    # Zone 2: plane at Y=3.6, extrude 2.0 mm toward fitting face (-Y)
    zone2 = (
        cq.Workplane("XZ")
        .workplane(offset=-Y_Z1_FLOOR)     # offset=-3.6 -> plane at Y=3.6
        .center(cx, cz)
        .circle(Z2_R)
        .extrude(Y_Z1_FLOOR - Y_Z2_FLOOR)  # 2.0 mm in -Y direction
    )
    plate = plate.cut(zone2)

    # Zone 3: plane at Y=1.6, extrude 1.6 mm toward fitting face (-Y)
    zone3 = (
        cq.Workplane("XZ")
        .workplane(offset=-Y_Z2_FLOOR)     # offset=-1.6 -> plane at Y=1.6
        .center(cx, cz)
        .circle(Z3_R)
        .extrude(Y_Z2_FLOOR - Y_FITTING)   # 1.6 mm in -Y direction
    )
    plate = plate.cut(zone3)

    print(f"  [-] Feature {4 + bore_idx}: Stepped bore {label} at X={cx}, Z={cz}")

# ------------------------------------------------------------------------------
# Features 10-13: Struts TL, TR, BL, BR
#
# Each strut is a 6x6 mm rectangular prism extending from Y=5 (user-facing face)
# to Y=95 (90 mm beyond user-facing face, toward lever). The strut base is flush
# with the plate user-facing face; the strut tips are plain square ends (no joinery).
#
# Placement: center at (cx, cz) in XZ, Y from STRUT_Y0 to STRUT_Y1.
# The box starts at (cx - STRUT_W/2, STRUT_Y0, cz - STRUT_H/2)
# and has dimensions (STRUT_W, STRUT_L, STRUT_H).
# ------------------------------------------------------------------------------
strut_feature_num = 10
for label, (cx, cz) in STRUTS.items():
    sx0 = cx - STRUT_W / 2    # left X edge of strut
    sz0 = cz - STRUT_H / 2    # bottom Z edge of strut
    sy0 = STRUT_Y0             # Y start = 5.0 (base at user-facing face)
    strut = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(sx0, sy0, sz0))
        .box(STRUT_W, STRUT_L, STRUT_H, centered=False)
    )
    plate = plate.union(strut)
    print(f"  [+] Feature {strut_feature_num}: Strut {label} center (X={cx}, Z={cz}), "
          f"box X:[{sx0},{cx+STRUT_W/2}] Y:[{sy0},{STRUT_Y1}] Z:[{sz0},{cz+STRUT_H/2}]")
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
v.check_solid("Plate body interior", 80.0, 2.5, 34.3,
              "solid at plate center (80.0, 2.5, 34.3)")

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

    # Path continuity: Zone1->Zone2 transition at Y=3.6
    v.check_void(f"Bore {label} Z1-Z2 transition above",
                 cx, 3.7, cz,
                 f"void just above Z1/Z2 transition at Y=3.7")
    v.check_void(f"Bore {label} Z1-Z2 transition below",
                 cx, 3.5, cz,
                 f"void just below Z1/Z2 transition at Y=3.5")

    # Path continuity: Zone2->Zone3 transition at Y=1.6
    v.check_void(f"Bore {label} Z2-Z3 transition above",
                 cx, 1.7, cz,
                 f"void just above Z2/Z3 transition at Y=1.7")
    v.check_void(f"Bore {label} Z2-Z3 transition below",
                 cx, 1.5, cz,
                 f"void just below Z2/Z3 transition at Y=1.5")

    # Check that material exists in the plate body beside the bore
    wall_z = cz + 12.0   # 12mm above bore center -- clear of Z1 outer radius (7.8mm)
    v.check_solid(f"Bore {label} wall solid",
                  cx, 2.5, wall_z,
                  f"solid in plate wall above bore {label} at Z={wall_z}, Y=2.5")

    # Check Zone1->Zone2 step annular wall at Y=2.5 (between Z2 and Z1 radii)
    step_offset = (Z1_R + Z2_R) / 2   # ~6.4 mm from center
    if cx < 70.0:
        step_x = cx + step_offset
    else:
        step_x = cx - step_offset
    v.check_solid(f"Bore {label} annular step wall",
                  step_x, 2.5, cz,
                  f"solid in annular ring between Z1 and Z2 radii at Y=2.5")

print()
print("--- Features 10-13: Struts ---")
strut_mid_y = (STRUT_Y0 + STRUT_Y1) / 2   # 50.0 mm (midpoint of strut length)
for label, (cx, cz) in STRUTS.items():
    # Probe solid at strut center (midpoint of length)
    v.check_solid(f"Strut {label} body center",
                  cx, strut_mid_y, cz,
                  f"solid at strut {label} center (X={cx}, Y={strut_mid_y}, Z={cz})")

    # Probe solid at strut base (Y just beyond user-facing face, inside strut)
    v.check_solid(f"Strut {label} base",
                  cx, STRUT_Y0 + 1.0, cz,
                  f"solid at strut {label} base (Y={STRUT_Y0 + 1.0})")

    # Probe solid near strut tip
    v.check_solid(f"Strut {label} tip",
                  cx, STRUT_Y1 - 1.0, cz,
                  f"solid near strut {label} tip (Y={STRUT_Y1 - 1.0})")

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
print(f"    X: [{bb.xmin:.3f}, {bb.xmax:.3f}]  (expected [0, 140.0])")
print(f"    Y: [{bb.ymin:.3f}, {bb.ymax:.3f}]  (expected [0, 95])")
print(f"    Z: [{bb.zmin:.3f}, {bb.zmax:.3f}]  (expected [0, 68.6])")

v.check_bbox("X", bb.xmin, bb.xmax, 0.0, PLATE_W, tol=0.5)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, STRUT_Y1, tol=0.5)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, PLATE_H, tol=0.5)

print()
print("--- Solid integrity (Rubric 4) ---")
v.check_valid()
v.check_single_body()

# Volume estimate:
# Plate body:  140.0 x 5 x 68.6 = 48020 mm3
# + 4 struts:  4 x 6 x 90 x 6   = 12960 mm3
# - 4 bores (approx):
#   Zone1: 4 x pi x 7.8^2 x 1.4 = 1070 mm3
#   Zone2: 4 x pi x 5.035^2 x 2.0 = 637 mm3
#   Zone3: 4 x pi x 3.25^2 x 1.6 = 212 mm3
#   Total bore removal: ~1919 mm3
# Estimated total: ~48020 + 12960 - 1919 = ~59061 mm3
# Full envelope: 140.0 x 95 x 68.6 = 912280 mm3
# Fill ratio: 59061 / 912280 = ~6.5%
v.check_volume(expected_envelope=PLATE_W * STRUT_Y1 * PLATE_H,
               fill_range=(0.03, 0.10))

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
