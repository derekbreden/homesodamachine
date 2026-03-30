"""
Pump Tray v2 — CadQuery STEP Generation Script
Build sequence line: Add strut bores to pump tray — 4 holes sized to the
strut cross-section, positioned so the struts pass through cleanly.

Specification source: hardware/printed-parts/cartridge/pump-tray/planning/parts.md
Strut positions source: hardware/printed-parts/cartridge/release-plate/generate_step_cadquery.py

v2 change: Added 4 rectangular strut bores (6.4 x 6.4 mm) at positions
matching the release plate strut centers: TL(10.0, 63.6), TR(127.2, 63.6),
BL(10.0, 5.0), BR(127.2, 5.0).

Coordinate system (part local frame):
  Origin: plate bottom-left-front corner (X=0, Y=0, Z=0)
  X: plate width axis — left to right, 0..137.2mm
  Y: plate thickness axis — front face (Y=0, pump bracket side) to back face (Y=3.0mm, motor side)
  Z: plate height axis — bottom to top, 0..68.6mm
  Envelope: 137.2mm (X) × 3.0mm (Y) × 68.6mm (Z)
"""

import sys
from pathlib import Path

# Add tools/ to sys.path for step_validate import
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq
from step_validate import Validator

# ==============================================================================
# Part parameters (from parts.md)
# ==============================================================================

# Plate envelope
PLATE_W = 137.2   # X — width left to right
PLATE_D = 3.0     # Y — thickness front to back
PLATE_H = 68.6    # Z — height bottom to top

# Motor bore diameter
MOTOR_BORE_DIA = 37.0
MOTOR_BORE_R = MOTOR_BORE_DIA / 2.0

# Motor bore centers (XZ positions)
MOTOR_BORES = [
    ("bore-1", 34.3,  34.3),   # Pump 1 motor axis
    ("bore-2", 102.9, 34.3),   # Pump 2 motor axis
]

# M3 clearance hole diameter
HOLE_DIA = 3.3
HOLE_R = HOLE_DIA / 2.0

# M3 hole XZ positions
HOLES = [
    ("1-A", 9.3,   59.3),   # Pump 1, top-left
    ("1-B", 59.3,  59.3),   # Pump 1, top-right
    ("1-C", 59.3,  9.3),    # Pump 1, bottom-right
    ("1-D", 9.3,   9.3),    # Pump 1, bottom-left
    ("2-A", 77.9,  59.3),   # Pump 2, top-left
    ("2-B", 127.9, 59.3),   # Pump 2, top-right
    ("2-C", 127.9, 9.3),    # Pump 2, bottom-right
    ("2-D", 77.9,  9.3),    # Pump 2, bottom-left
]

# Strut bore parameters (NEW in v2)
# Strut cross-section on release plate: 6.0 x 6.0 mm
# Bore clearance: 0.2mm per side (requirements.md sliding fit)
# Bore size: 6.0 + 0.4 = 6.4 mm per axis
STRUT_SIZE = 6.0       # release plate strut cross-section
BORE_CLEARANCE = 0.4   # 0.2mm per side × 2 sides
STRUT_BORE_W = STRUT_SIZE + BORE_CLEARANCE  # 6.4 mm (X)
STRUT_BORE_H = STRUT_SIZE + BORE_CLEARANCE  # 6.4 mm (Z)

# Strut bore center positions (X, Z) — match release plate strut centers
STRUT_BORES = [
    ("S-TL", 10.0,  63.6),   # Top-Left
    ("S-TR", 127.2, 63.6),   # Top-Right
    ("S-BL", 10.0,   5.0),   # Bottom-Left
    ("S-BR", 127.2,  5.0),   # Bottom-Right
]

# ==============================================================================
# Rubric 1 — Feature Planning Table
# ==============================================================================

FEATURE_TABLE = """
PUMP TRAY v2 — FEATURE PLANNING TABLE (Rubric 1)
===================================================

  #   Feature Name              Op      Shape         Axis  Center / Position                Dimensions
  1   Plate body                Add     Rect prism    —     Origin (0,0,0)                   137.2W × 3.0D × 68.6H mm
  2   Motor bore 1              Remove  Cylinder      Y     X=34.3, Z=34.3                   37mm dia, TH
  3   Motor bore 2              Remove  Cylinder      Y     X=102.9, Z=34.3                  37mm dia, TH
  4   Hole 1-A (P1 top-left)    Remove  Cylinder      Y     X=9.3, Z=59.3                    3.3mm dia, TH
  5   Hole 1-B (P1 top-right)   Remove  Cylinder      Y     X=59.3, Z=59.3                   3.3mm dia, TH
  6   Hole 1-C (P1 bot-right)   Remove  Cylinder      Y     X=59.3, Z=9.3                    3.3mm dia, TH
  7   Hole 1-D (P1 bot-left)    Remove  Cylinder      Y     X=9.3, Z=9.3                     3.3mm dia, TH
  8   Hole 2-A (P2 top-left)    Remove  Cylinder      Y     X=77.9, Z=59.3                   3.3mm dia, TH
  9   Hole 2-B (P2 top-right)   Remove  Cylinder      Y     X=127.9, Z=59.3                  3.3mm dia, TH
  10  Hole 2-C (P2 bot-right)   Remove  Cylinder      Y     X=127.9, Z=9.3                   3.3mm dia, TH
  11  Hole 2-D (P2 bot-left)    Remove  Cylinder      Y     X=77.9, Z=9.3                    3.3mm dia, TH
  12  Strut bore S-TL           Remove  Rect prism    Y     X=10.0, Z=63.6                   6.4W × 3.0D × 6.4H mm, TH
  13  Strut bore S-TR           Remove  Rect prism    Y     X=127.2, Z=63.6                  6.4W × 3.0D × 6.4H mm, TH
  14  Strut bore S-BL           Remove  Rect prism    Y     X=10.0, Z=5.0                    6.4W × 3.0D × 6.4H mm, TH
  15  Strut bore S-BR           Remove  Rect prism    Y     X=127.2, Z=5.0                   6.4W × 3.0D × 6.4H mm, TH

TH = through-hole, full Y depth (Y=0 to Y=3.0mm)

Coordinate system (Rubric 2):
  Origin: plate bottom-left-front corner (X=0, Y=0, Z=0)
  X: plate width, left to right, 0 → 137.2 mm
  Y: plate thickness, front (Y=0) to back (Y=3.0)
  Z: plate height, bottom to top, 0 → 68.6 mm
  Bounding box: X:[0, 137.2] Y:[0, 3.0] Z:[0, 68.6]
"""

print("=" * 70)
print("PUMP TRAY v2 — CadQuery STEP Generation")
print("=" * 70)
print(FEATURE_TABLE)
print("Building model...")

# ==============================================================================
# Modeling
# ==============================================================================

# ------------------------------------------------------------------------------
# Feature 1: Plate body
# box(W, D, H, centered=False) → X:[0,137.2] Y:[0,3.0] Z:[0,68.6]
# ------------------------------------------------------------------------------
plate = cq.Workplane("XY").box(PLATE_W, PLATE_D, PLATE_H, centered=False)
print("  [+] Feature 1: Plate body (137.2 × 3.0 × 68.6 mm)")

# ------------------------------------------------------------------------------
# Features 2-3: Motor bores (37mm dia, through Y)
# XZ workplane: normal = -Y. offset=0 → plane at Y=0.
# Negative extrude goes +Y direction (through plate toward back face).
# ------------------------------------------------------------------------------
for bore_id, bx, bz in MOTOR_BORES:
    overcut = 0.1
    bore_cyl = (
        cq.Workplane("XZ")
        .workplane(offset=0)        # plane at Y=0 (front face)
        .center(bx, bz)
        .circle(MOTOR_BORE_R)
        .extrude(-(PLATE_D + overcut))
        # negative extrude on XZ → +Y direction, cuts Y=0 to Y=3.1
    )
    plate = plate.cut(bore_cyl)
    print(f"  [-] Feature: Motor bore {bore_id} at X={bx}, Z={bz}")

# ------------------------------------------------------------------------------
# Features 4-11: M3 clearance holes (3.3mm dia, through Y)
# Same approach as motor bores.
# ------------------------------------------------------------------------------
for hole_id, hx, hz in HOLES:
    overcut = 0.1
    cyl = (
        cq.Workplane("XZ")
        .workplane(offset=0)        # plane at Y=0 (front face)
        .center(hx, hz)
        .circle(HOLE_R)
        .extrude(-(PLATE_D + overcut))
        # negative extrude on XZ → +Y direction
    )
    plate = plate.cut(cyl)
    print(f"  [-] Feature: Hole {hole_id} at X={hx}, Z={hz}")

# ------------------------------------------------------------------------------
# Features 12-15: Strut bores (6.4 x 6.4 mm rectangular, through Y)
#
# Each bore is a rectangular through-hole centered at (cx, cz) in the XZ plane,
# running from Y=0 to Y=3.0mm.
#
# Approach: create a box at the bore position and cut it from the plate.
# Box corner at (cx - STRUT_BORE_W/2, 0, cz - STRUT_BORE_H/2),
# dimensions (STRUT_BORE_W, PLATE_D + overcut, STRUT_BORE_H).
# Using overcut to ensure clean through-cut.
# ------------------------------------------------------------------------------
for bore_id, cx, cz in STRUT_BORES:
    overcut = 0.1
    x0 = cx - STRUT_BORE_W / 2   # left X edge of bore
    z0 = cz - STRUT_BORE_H / 2   # bottom Z edge of bore
    bore_box = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(x0, -overcut / 2, z0))
        .box(STRUT_BORE_W, PLATE_D + overcut, STRUT_BORE_H, centered=False)
    )
    plate = plate.cut(bore_box)
    print(f"  [-] Feature: Strut bore {bore_id} at X={cx}, Z={cz} "
          f"(rect {STRUT_BORE_W}×{STRUT_BORE_H} mm)")

print()
print("Model construction complete.")
print()

# ==============================================================================
# Export STEP file
# ==============================================================================

OUTPUT_STEP = Path(__file__).resolve().parent / "pump-tray-cadquery.step"
print(f"Exporting STEP file → {OUTPUT_STEP}")
cq.exporters.export(plate, str(OUTPUT_STEP))
print("Export complete.")
print()

# ==============================================================================
# Validation (Rubrics 3, 4, 5)
# ==============================================================================

print("=" * 70)
print("VALIDATION")
print("=" * 70)
print()

v = Validator(plate)

# --- Feature 1: Plate body ---
print("--- Feature 1: Plate body ---")
v.check_solid("Plate body center", 68.6, 1.5, 34.3,
              "solid at plate geometric center")
v.check_solid("Plate near front face", 68.6, 0.1, 34.3,
              "solid near Y=0 front face")
v.check_solid("Plate near back face", 68.6, 2.9, 34.3,
              "solid near Y=3.0 back face")
print()

# --- Features 2-3: Motor bores ---
print("--- Features 2-3: Motor bores ---")
for bore_id, bx, bz in MOTOR_BORES:
    v.check_void(f"Motor bore {bore_id} center", bx, 1.5, bz,
                 f"void at bore center ({bx}, 1.5, {bz})")
    v.check_void(f"Motor bore {bore_id} front", bx, 0.1, bz,
                 f"void near front face")
    v.check_void(f"Motor bore {bore_id} back", bx, 2.9, bz,
                 f"void near back face")
    v.check_solid(f"Motor bore {bore_id} wall +X", bx + MOTOR_BORE_R + 2.0, 1.5, bz,
                  f"solid outside bore radius in +X")
print()

# --- Features 4-11: M3 holes ---
print("--- Features 4-11: M3 clearance holes ---")
for hole_id, hx, hz in HOLES:
    v.check_void(f"Hole {hole_id} center", hx, 1.5, hz,
                 f"void at hole center ({hx}, 1.5, {hz})")
    v.check_void(f"Hole {hole_id} front", hx, 0.1, hz,
                 f"void near front face")
    v.check_void(f"Hole {hole_id} back", hx, 2.9, hz,
                 f"void near back face")
print()

# --- Features 12-15: Strut bores ---
print("--- Features 12-15: Strut bores ---")
for bore_id, cx, cz in STRUT_BORES:
    half_w = STRUT_BORE_W / 2  # 3.2
    half_h = STRUT_BORE_H / 2  # 3.2

    # Void at bore center, mid-depth
    v.check_void(f"Strut bore {bore_id} center",
                 cx, 1.5, cz,
                 f"void at bore center ({cx}, 1.5, {cz})")

    # Void near front face
    v.check_void(f"Strut bore {bore_id} front",
                 cx, 0.1, cz,
                 f"void near front face Y=0.1")

    # Void near back face
    v.check_void(f"Strut bore {bore_id} back",
                 cx, 2.9, cz,
                 f"void near back face Y=2.9")

    # Void at bore corners (checks rectangular extent, not just center)
    # Probe 0.3mm inside each bore corner to confirm rectangular shape
    inset = 0.3
    v.check_void(f"Strut bore {bore_id} corner +X+Z",
                 cx + half_w - inset, 1.5, cz + half_h - inset,
                 f"void near +X+Z corner of bore")
    v.check_void(f"Strut bore {bore_id} corner -X-Z",
                 cx - half_w + inset, 1.5, cz - half_h + inset,
                 f"void near -X-Z corner of bore")

    # Solid outside bore in X direction (1mm beyond bore edge)
    # Only check if not near plate edge (bore edge + 1mm < plate width)
    outside_x = cx + half_w + 1.0
    if outside_x < PLATE_W:
        v.check_solid(f"Strut bore {bore_id} wall +X",
                      outside_x, 1.5, cz,
                      f"solid outside bore +X edge at X={outside_x:.1f}")

    # Solid outside bore in -X direction
    outside_x_neg = cx - half_w - 1.0
    if outside_x_neg > 0:
        v.check_solid(f"Strut bore {bore_id} wall -X",
                      outside_x_neg, 1.5, cz,
                      f"solid outside bore -X edge at X={outside_x_neg:.1f}")

print()

# --- Bounding box (Rubric 5) ---
print("--- Bounding box (Rubric 5) ---")
bb = plate.val().BoundingBox()
print(f"  Actual bounding box:")
print(f"    X: [{bb.xmin:.3f}, {bb.xmax:.3f}]  (expected [0, 137.2])")
print(f"    Y: [{bb.ymin:.3f}, {bb.ymax:.3f}]  (expected [0, 3.0])")
print(f"    Z: [{bb.zmin:.3f}, {bb.zmax:.3f}]  (expected [0, 68.6])")

v.check_bbox("X", bb.xmin, bb.xmax, 0.0, PLATE_W)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, PLATE_D)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, PLATE_H)
print()

# --- Solid integrity (Rubric 4) ---
print("--- Solid integrity (Rubric 4) ---")
v.check_valid()
v.check_single_body()

# Volume estimate:
# Plate body: 137.2 × 3.0 × 68.6 = 28237 mm³
# - 2 motor bores: 2 × π × 18.5² × 3.0 = 6472 mm³
# - 8 M3 holes: 8 × π × 1.65² × 3.0 = 205 mm³
# - 4 strut bores: 4 × 6.4 × 6.4 × 3.0 = 491 mm³
# Estimated: 28237 - 6472 - 205 - 491 ≈ 21069 mm³
# Fill ratio: 21069 / 28237 ≈ 0.746
envelope_vol = PLATE_W * PLATE_D * PLATE_H
v.check_volume(expected_envelope=envelope_vol, fill_range=(0.5, 1.2))
print()

# --- Summary ---
passed = v.summary()

if not passed:
    print()
    print("FAIL: Validation failures detected. Exiting without STEP file.")
    sys.exit(1)

print()
print(f"SUCCESS: STEP file written to:")
print(f"  {OUTPUT_STEP}")
print("Done.")
