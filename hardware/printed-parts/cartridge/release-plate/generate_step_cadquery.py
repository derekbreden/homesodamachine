"""
Release Plate v3 — CadQuery STEP Generation Script
Pipeline step: 6g — STEP Generation
Input: planning/parts.md
Output: release-plate-cadquery.step

Part: Single printed PETG sliding actuator that simultaneously depresses the
rear-facing collets of four PP0408W quick-connect fittings.

v3 change: Redesign to 1×4 bore layout matching coupler tray v3.
  - Plate footprint updated to 137.2 × 68.6 mm (matches coupler tray v3 footprint).
  - 4 stepped bores repositioned to 1×4 row: X=43.1, 60.1, 77.1, 94.1 at Z=34.3.
  - 4 struts repositioned to plate corners (clear of all bores).
  - 2 guide pins repositioned diagonally to match new plate geometry.

v4 change: Struts moved from front face to rear face; guide pins removed.
  - Struts now extend from Y=5.0 (rear face) to Y=95.0 (90 mm beyond rear face).
  - Guide pins (Features 8-9) removed entirely — not a feature of this plate.

Coordinate system (part local frame):
  Origin: plate bottom-left-front corner (X=0, Y=0, Z=0)
  X: plate width, left to right, 0 → 137.2 mm
  Y: plate depth, front (user-facing, build-plate face) to rear (fitting-facing)
       Y=0  = front face (pull surface, sits on build plate in print orientation)
       Y=5  = rear face (bore-entry face, faces PP0408W fittings)
       Y=95 = strut tips (90 mm beyond rear face, toward lever)
  Z: plate height, bottom to top, 0 → 68.6 mm
  Plate envelope:          X:[0,137.2]  Y:[0,5]     Z:[0,68.6]
  With struts:             X:[0,137.2]  Y:[0,95]    Z:[0,68.6]
  Full bounding box:       X:[0,137.2]  Y:[0,95]    Z:[0,68.6]

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

  For struts running Y=5 → Y=95 (rear outward, +Y direction):
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
# Part parameters (from parts.md)
# ==============================================================================

PLATE_W = 137.2  # X extent — matches coupler tray v3 width
PLATE_D = 5.0    # Y extent (thickness)
PLATE_H = 68.6   # Z extent — matches coupler tray v3 height

# Bore zone diameters (unchanged from v2)
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

# Bore center positions (X, Z) — 1×4 row matching coupler tray v3
# H1: X=43.1, Z=34.3
# H2: X=60.1, Z=34.3
# H3: X=77.1, Z=34.3
# H4: X=94.1, Z=34.3
BORE_CENTERS = [
    (43.1, 34.3),   # A — H1
    (60.1, 34.3),   # B — H2
    (77.1, 34.3),   # C — H3
    (94.1, 34.3),   # D — H4
]

# Strut parameters (Features 10-13)
STRUT_W  = 6.0    # X cross-section
STRUT_H  = 6.0    # Z cross-section
STRUT_L  = 90.0   # Y length
STRUT_Y0 = 5.0    # strut base at rear face (Y=5)
STRUT_Y1 = 95.0   # strut tips (90 mm beyond rear face, toward lever)

# Strut center positions (X, Z) — corner placement, clear of all bore outer circles
# Bore outer radius = 7.8 mm. Nearest bore to corner struts:
#   TL (10.0, 63.6) to bore A (43.1, 34.3): ~40mm center-to-center → 32.2mm gap ✓
#   TR (127.2, 63.6) to bore D (94.1, 34.3): ~40mm center-to-center → 32.2mm gap ✓
#   BL (10.0, 5.0) to bore A (43.1, 34.3): ~40mm center-to-center → 32.2mm gap ✓
#   BR (127.2, 5.0) to bore D (94.1, 34.3): ~40mm center-to-center → 32.2mm gap ✓
STRUTS = {
    "TL": (10.0,  63.6),   # Top-Left corner
    "TR": (127.2, 63.6),   # Top-Right corner
    "BL": (10.0,   5.0),   # Bottom-Left corner
    "BR": (127.2,  5.0),   # Bottom-Right corner
}

# Fillet radii
CORNER_R = 2.0   # Perimeter corner radii (4 vertical edges parallel to Y)
PULL_R   = 3.0   # Pull edge radius (4 front-face perimeter edges)

# ==============================================================================
# Rubric 1 — Feature Planning Table
# ==============================================================================

FEATURE_TABLE = """
RELEASE PLATE v3 — FEATURE PLANNING TABLE (Rubric 1)
======================================================

  #   Feature Name              Op      Shape         Axis  Center / Position                Dimensions
  1   Plate body                Add     Rect prism    Y     Origin (0,0,0)                   137.2W × 5D × 68.6H mm
  2   Perimeter corner radii    Remove  Fillet R2     Y     4 vertical edges at XZ corners   R = 2.0 mm
  3   Pull edge radius          Remove  Fillet R3     X,Z   4 front-face perimeter edges      R = 3.0 mm
  4   Stepped bore A            Remove  3-step cyl    Y     X=43.1, Z=34.3                   Z1:Ø15.60 Z2:Ø10.07 Z3:Ø6.50
  5   Stepped bore B            Remove  3-step cyl    Y     X=60.1, Z=34.3                   (same)
  6   Stepped bore C            Remove  3-step cyl    Y     X=77.1, Z=34.3                   (same)
  7   Stepped bore D            Remove  3-step cyl    Y     X=94.1, Z=34.3                   (same)
  10  Strut TL (Top-Left)       Add     Rect prism    Y     X=10.0, Z=63.6                   6W × 90D × 6H mm, Y:5→95
  11  Strut TR (Top-Right)      Add     Rect prism    Y     X=127.2, Z=63.6                  6W × 90D × 6H mm, Y:5→95
  12  Strut BL (Bottom-Left)    Add     Rect prism    Y     X=10.0, Z=5.0                    6W × 90D × 6H mm, Y:5→95
  13  Strut BR (Bottom-Right)   Add     Rect prism    Y     X=127.2, Z=5.0                   6W × 90D × 6H mm, Y:5→95

Bore zone detail (identical for all 4 bores):
  Zone 1 (outer counterbore): Ø15.60 mm, Y: 5.0 → 3.6 mm (depth 1.4 mm from rear face)
  Zone 2 (inner lip bore):    Ø10.07 mm, Y: 3.6 → 1.6 mm (depth 2.0 mm)
  Zone 3 (through-hole):      Ø 6.50 mm, Y: 1.6 → 0.0 mm (depth 1.6 mm, exits front face)

Bore pattern: 1×4 row at Z=34.3, X=43.1/60.1/77.1/94.1 (17mm c-c spacing).
Bore row centered at X=68.6 (plate midpoint), Z=34.3 (plate midpoint).

Strut clearances (all struts, worst-case nearest bore):
  TL (10.0, 63.6): nearest bore A (43.1, 34.3) → 40.0mm c-c → 32.2mm edge-to-edge ✓
  TR (127.2, 63.6): nearest bore D (94.1, 34.3) → 40.0mm c-c → 32.2mm edge-to-edge ✓
  BL (10.0, 5.0): nearest bore A (43.1, 34.3) → 40.0mm c-c → 32.2mm edge-to-edge ✓
  BR (127.2, 5.0): nearest bore D (94.1, 34.3) → 40.0mm c-c → 32.2mm edge-to-edge ✓

Coordinate system declaration (Rubric 2):
  Origin: plate bottom-left-front corner
  X: plate width, left to right, 0 → 137.2 mm
  Y: plate depth, front (Y=0) to rear (Y=5), struts to Y=95
  Z: plate height, bottom to top, 0 → 68.6 mm
  Full bounding box: X:[0,137.2] Y:[0,95] Z:[0,68.6]

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
print("RELEASE PLATE v3 — CadQuery STEP Generation")
print("=" * 70)
print(FEATURE_TABLE)
print("Building model...")

# ------------------------------------------------------------------------------
# Feature 1: Plate body
# box(W, D, H, centered=False) with W=137.2 (X), D=5 (Y), H=68.6 (Z)
# → X:[0,137.2] Y:[0,5] Z:[0,68.6]
# ------------------------------------------------------------------------------
plate = cq.Workplane("XY").box(PLATE_W, PLATE_D, PLATE_H, centered=False)
print("  [+] Feature 1: Plate body (137.2 × 5 × 68.6 mm)")

# ------------------------------------------------------------------------------
# Feature 2: Perimeter corner radii — R2 on 4 vertical edges (parallel to Y)
# These are the edges at (X=0,Z=0), (X=137.2,Z=0), (X=0,Z=68.6), (X=137.2,Z=68.6)
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
# Three cylindrical zones are cut separately.
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
# Features 10-13: Struts TL, TR, BL, BR
#
# Each strut is a 6×6 mm rectangular prism extending from Y=5 (rear face)
# to Y=95 (90 mm beyond rear face, toward lever). The strut base is flush with
# the plate rear face; the strut tips are plain square ends (no joinery).
#
# Placement: center at (cx, cz) in XZ, Y from STRUT_Y0 to STRUT_Y1 (i.e.
# from 5 to 95). The box starts at (cx - STRUT_W/2, STRUT_Y0, cz - STRUT_H/2)
# and has dimensions (STRUT_W, STRUT_L, STRUT_H).
#
# Using XY workplane with transformed(offset=...) to position each strut:
#   transformed(offset=Vector(x0, y0, z0)) moves the workplane origin to (x0,y0,z0)
#   box(W, D, H, centered=False) then places the box at X:[0,W] Y:[0,D] Z:[0,H]
#   relative to the new origin.
#
# For a strut with center (cx, cz), Y from STRUT_Y0 (5) to STRUT_Y1 (95):
#   origin = (cx - STRUT_W/2, STRUT_Y0, cz - STRUT_H/2)
#   box(STRUT_W, STRUT_L, STRUT_H, centered=False)
#   → X:[cx-3, cx+3]  Y:[5, 95]  Z:[cz-3, cz+3]
# ------------------------------------------------------------------------------
strut_feature_num = 10
for label, (cx, cz) in STRUTS.items():
    sx0 = cx - STRUT_W / 2    # left X edge of strut
    sz0 = cz - STRUT_H / 2    # bottom Z edge of strut
    sy0 = STRUT_Y0             # Y start = 5.0 (base at rear face)
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
v.check_solid("Plate body interior", 68.6, 2.5, 34.3,
              "solid at plate center (68.6, 2.5, 34.3)")

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

    # Check that material exists in the plate body beside the bore (at Zone2 depth).
    # All bores are at Z=34.3; probe in Z direction (above or below) to stay clear
    # of neighboring bore Z1 outer circles.  Probing at Z=34.3+12.0=46.3 (above) is
    # clear of all bore outer edges (all bores at same Z, no Z-direction neighbors).
    wall_z = cz + 12.0   # 12mm above bore center — clear of Z1 outer radius (7.8mm)
    v.check_solid(f"Bore {label} wall solid",
                  cx, 2.5, wall_z,
                  f"solid in plate wall above bore {label} at Z={wall_z}, Y=2.5")

    # Check Zone1→Zone2 step annular wall at Y=2.5 (between Z2 and Z1 radii)
    step_offset = (Z1_R + Z2_R) / 2   # ~6.4 mm from center
    if cx < 68.6:
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

    # Probe solid at strut base (Y just beyond rear face, inside strut)
    v.check_solid(f"Strut {label} base",
                  cx, STRUT_Y0 + 1.0, cz,
                  f"solid at strut {label} base (Y={STRUT_Y0 + 1.0}, just beyond rear face)")

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
print(f"    X: [{bb.xmin:.3f}, {bb.xmax:.3f}]  (expected [0, 137.2])")
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
# Plate body:  137.2 × 5 × 68.6 = 47051 mm³
# + 4 struts:  4 × 6 × 90 × 6   = 12960 mm³
# - 4 bores (approx):
#   Zone1: 4 × π × 7.8² × 1.4 ≈ 1070 mm³
#   Zone2: 4 × π × 5.035² × 2.0 ≈ 637 mm³
#   Zone3: 4 × π × 3.25² × 1.6 ≈ 212 mm³
#   Total bore removal: ≈ 1919 mm³
# Estimated total: ≈ 47051 + 12960 - 1919 ≈ 58092 mm³
# Full envelope: 137.2 × 95 × 68.6 = 893888 mm³  (Y span = 0 → 95)
# Fill ratio: 58092 / 893888 ≈ 6.5%
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
