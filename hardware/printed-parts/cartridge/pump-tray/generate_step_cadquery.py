"""
Pump Tray v3 — CadQuery STEP Generation Script
Build sequence line: Widen pump tray — make the pump tray wider so that the
strut bores can be moved outward and no longer overlap the pump mounting holes.

Specification source: hardware/printed-parts/cartridge/pump-tray/planning/parts.md

v3 change: Plate widened from 137.2mm to 140.0mm. Pump pattern re-centered.
Strut bores moved outward to X=4.0/136.0 (from 10.0/127.2), fully clearing
the M3 mounting holes with 1.85mm edge-to-edge gap.

Coordinate system (part local frame):
  Origin: plate bottom-left-front corner (X=0, Y=0, Z=0)
  X: plate width axis — left to right, 0..140.0mm
  Y: plate thickness axis — front face (Y=0, pump bracket side) to back face (Y=3.0mm, motor side)
  Z: plate height axis — bottom to top, 0..68.6mm
  Envelope: 140.0mm (X) × 3.0mm (Y) × 68.6mm (Z)
"""

import sys
from pathlib import Path

# Add tools/ to sys.path for step_validate import
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq
from step_validate import Validator

# ==============================================================================
# Part parameters (from parts.md v3)
# ==============================================================================

# Plate envelope
PLATE_W = 170.0   # X — width left to right (was 140.0 in v3)
PLATE_D = 3.0     # Y — thickness front to back
PLATE_H = 103.6   # Z — height bottom to top (was 68.6, +35mm)

# Diamond (45°-rotated square) cutout for pump base
DIAMOND_SIDE = 42.5  # side length of the square before rotation

# Pump base cutout centers (XZ positions)
# Pump center-to-center: 68.6mm. Plate center: 70.0mm.
# Pump 1: 70.0 - 34.3 = 35.7. Pump 2: 70.0 + 34.3 = 104.3.
PUMP_CUTOUTS = [
    ("cutout-1", 50.7,  34.3),   # Pump 1 (was 35.7, +15mm for wider plate)
    ("cutout-2", 119.3, 34.3),   # Pump 2 (was 104.3, +15mm for wider plate)
]

# M3 clearance hole diameter
HOLE_DIA = 3.3
HOLE_R = HOLE_DIA / 2.0

# M3 hole XZ positions — 50mm square pattern around each motor bore, re-centered
HOLES = [
    ("1-A", 25.7,  59.3),   # Pump 1, top-left (was 10.7, +15mm)
    ("1-B", 75.7,  59.3),   # Pump 1, top-right (was 60.7, +15mm)
    ("1-C", 75.7,   9.3),   # Pump 1, bottom-right (was 60.7, +15mm)
    ("1-D", 25.7,   9.3),   # Pump 1, bottom-left (was 10.7, +15mm)
    ("2-A", 94.3,  59.3),   # Pump 2, top-left (was 79.3, +15mm)
    ("2-B", 144.3, 59.3),   # Pump 2, top-right (was 129.3, +15mm)
    ("2-C", 144.3,  9.3),   # Pump 2, bottom-right (was 129.3, +15mm)
    ("2-D", 94.3,   9.3),   # Pump 2, bottom-left (was 79.3, +15mm)
]

# Strut bore parameters
# Strut cross-section on release plate: 6.0 x 6.0 mm
# Bore clearance: 0.2mm per side × 2 sides = 0.4mm total
# Bore size: 6.0 + 0.4 = 6.4 mm per axis
STRUT_SIZE = 6.0
BORE_CLEARANCE = 0.4
STRUT_BORE_W = STRUT_SIZE + BORE_CLEARANCE  # 6.4 mm (X)
STRUT_BORE_H = STRUT_SIZE + BORE_CLEARANCE  # 6.4 mm (Z)

# Strut bore center positions (X, Z) — moved outward to clear M3 holes
STRUT_BORES = [
    ("S-TL",   9.0, 63.6),   # Top-Left (was 4.0, +15mm shift, -10mm outward)
    ("S-TR", 161.0, 63.6),   # Top-Right (was 136.0, +15mm shift, +10mm outward)
    ("S-BL",   9.0,  5.0),   # Bottom-Left (was 4.0, +15mm shift, -10mm outward)
    ("S-BR", 161.0,  5.0),   # Bottom-Right (was 136.0, +15mm shift, +10mm outward)
]

# ==============================================================================
# Rubric 1 — Feature Planning Table
# ==============================================================================

FEATURE_TABLE = """
PUMP TRAY v3 — FEATURE PLANNING TABLE (Rubric 1)
===================================================

  #   Feature Name              Op      Shape         Axis  Center / Position                Dimensions
  1   Plate body                Add     Rect prism    —     Origin (0,0,0)                   140.0W × 3.0D × 68.6H mm
  2   Motor bore 1              Remove  Cylinder      Y     X=35.7, Z=34.3                   37mm dia, TH
  3   Motor bore 2              Remove  Cylinder      Y     X=104.3, Z=34.3                  37mm dia, TH
  4   Hole 1-A (P1 top-left)    Remove  Cylinder      Y     X=10.7, Z=59.3                   3.3mm dia, TH
  5   Hole 1-B (P1 top-right)   Remove  Cylinder      Y     X=60.7, Z=59.3                   3.3mm dia, TH
  6   Hole 1-C (P1 bot-right)   Remove  Cylinder      Y     X=60.7, Z=9.3                    3.3mm dia, TH
  7   Hole 1-D (P1 bot-left)    Remove  Cylinder      Y     X=10.7, Z=9.3                    3.3mm dia, TH
  8   Hole 2-A (P2 top-left)    Remove  Cylinder      Y     X=79.3, Z=59.3                   3.3mm dia, TH
  9   Hole 2-B (P2 top-right)   Remove  Cylinder      Y     X=129.3, Z=59.3                  3.3mm dia, TH
  10  Hole 2-C (P2 bot-right)   Remove  Cylinder      Y     X=129.3, Z=9.3                   3.3mm dia, TH
  11  Hole 2-D (P2 bot-left)    Remove  Cylinder      Y     X=79.3, Z=9.3                    3.3mm dia, TH
  12  Strut bore S-TL           Remove  Rect prism    Y     X=4.0, Z=63.6                    6.4W × 3.0D × 6.4H mm, TH
  13  Strut bore S-TR           Remove  Rect prism    Y     X=136.0, Z=63.6                  6.4W × 3.0D × 6.4H mm, TH
  14  Strut bore S-BL           Remove  Rect prism    Y     X=4.0, Z=5.0                     6.4W × 3.0D × 6.4H mm, TH
  15  Strut bore S-BR           Remove  Rect prism    Y     X=136.0, Z=5.0                   6.4W × 3.0D × 6.4H mm, TH

TH = through-hole, full Y depth (Y=0 to Y=3.0mm)

Coordinate system (Rubric 2):
  Origin: plate bottom-left-front corner (X=0, Y=0, Z=0)
  X: plate width, left to right, 0 → 140.0 mm
  Y: plate thickness, front (Y=0) to back (Y=3.0)
  Z: plate height, bottom to top, 0 → 68.6 mm
  Bounding box: X:[0, 140.0] Y:[0, 3.0] Z:[0, 68.6]
"""

print("=" * 70)
print("PUMP TRAY v3 — CadQuery STEP Generation")
print("=" * 70)
print(FEATURE_TABLE)
print("Building model...")

# ==============================================================================
# Modeling
# ==============================================================================

# ------------------------------------------------------------------------------
# Feature 1: Plate body
# box(W, D, H, centered=False) → X:[0,140.0] Y:[0,3.0] Z:[0,68.6]
# ------------------------------------------------------------------------------
plate = cq.Workplane("XY").box(PLATE_W, PLATE_D, PLATE_H, centered=False)
print("  [+] Feature 1: Plate body (140.0 × 3.0 × 68.6 mm)")

# ------------------------------------------------------------------------------
# Features 2-3: Octagon cutouts (42.5mm square rotated 45°, corners trimmed)
# Start with diamond (42.5mm square @ 45°), trim corners so corner-to-corner
# span shrinks from 60.1mm to 52.5mm. Result: octagon with 4 long + 4 short edges.
# ------------------------------------------------------------------------------
import math
DIAMOND_HALF_DIAG = DIAMOND_SIDE * math.sqrt(2) / 2  # original corner-to-corner half = 30.05
TRIMMED_HALF_DIAG = 52.5 / 2                          # trimmed corner-to-corner half = 26.25

for cutout_id, cx, cz in PUMP_CUTOUTS:
    overcut = 0.1
    h = DIAMOND_HALF_DIAG   # 30.05 — where original corners were
    t = TRIMMED_HALF_DIAG   # 26.25 — where we clip
    # Each original corner (e.g. top at (0, h)) is replaced by two points
    # on the original diamond edges, at the Z (or X) level where we clip.
    # The trim distance from the corner along each axis: h - t = 3.8mm
    d = h - t
    # Octagon vertices going clockwise from top-right of top corner:
    pts = [
        ( d,  t),   # top corner, right side
        ( t,  d),   # right corner, top side
        ( t, -d),   # right corner, bottom side
        ( d, -t),   # bottom corner, right side
        (-d, -t),   # bottom corner, left side
        (-t, -d),   # left corner, bottom side
        (-t,  d),   # left corner, top side
        (-d,  t),   # top corner, left side
    ]
    octagon = (
        cq.Workplane("XZ")
        .workplane(offset=0)
        .center(cx, cz)
        .polyline(pts).close()
        .extrude(-(PLATE_D + overcut))
    )
    plate = plate.cut(octagon)
    print(f"  [-] Feature: Octagon {cutout_id} at X={cx}, Z={cz} "
          f"(42.5mm square @ 45°, corners trimmed to {2*t:.1f}mm span)")

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
v.check_solid("Plate body center", 85.0, 1.5, 34.3,
              "solid at plate geometric center")
v.check_solid("Plate near front face", 85.0, 0.1, 34.3,
              "solid near Y=0 front face")
v.check_solid("Plate near back face", 85.0, 2.9, 34.3,
              "solid near Y=3.0 back face")
print()

# --- Features 2-3: Octagon cutouts ---
print("--- Features 2-3: Octagon cutouts ---")
for cutout_id, cx, cz in PUMP_CUTOUTS:
    v.check_void(f"Octagon {cutout_id} center", cx, 1.5, cz,
                 f"void at octagon center ({cx}, 1.5, {cz})")
    v.check_void(f"Octagon {cutout_id} front", cx, 0.1, cz,
                 f"void near front face")
    v.check_void(f"Octagon {cutout_id} back", cx, 2.9, cz,
                 f"void near back face")
    # Check void inside the trimmed span
    t = TRIMMED_HALF_DIAG
    v.check_void(f"Octagon {cutout_id} near top", cx, 1.5, cz + t - 2.0,
                 f"void near top of octagon")
    v.check_void(f"Octagon {cutout_id} near right", cx + t - 2.0, 1.5, cz,
                 f"void near right of octagon")
    # Check solid OUTSIDE the trimmed span (where corners were clipped)
    v.check_solid(f"Octagon {cutout_id} beyond top", cx, 1.5, cz + t + 1.0,
                  f"solid beyond trimmed top corner")
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

    # Void at bore corners (checks rectangular extent)
    inset = 0.3
    v.check_void(f"Strut bore {bore_id} corner +X+Z",
                 cx + half_w - inset, 1.5, cz + half_h - inset,
                 f"void near +X+Z corner of bore")
    v.check_void(f"Strut bore {bore_id} corner -X-Z",
                 cx - half_w + inset, 1.5, cz - half_h + inset,
                 f"void near -X-Z corner of bore")

    # Solid outside bore in X direction (1mm beyond bore edge)
    outside_x = cx + half_w + 1.0
    if outside_x < PLATE_W:
        v.check_solid(f"Strut bore {bore_id} wall +X",
                      outside_x, 1.5, cz,
                      f"solid outside bore +X edge at X={outside_x:.1f}")

    outside_x_neg = cx - half_w - 1.0
    if outside_x_neg > 0:
        v.check_solid(f"Strut bore {bore_id} wall -X",
                      outside_x_neg, 1.5, cz,
                      f"solid outside bore -X edge at X={outside_x_neg:.1f}")

print()

# --- Verify strut bores do NOT overlap M3 holes (the v3 fix) ---
print("--- Strut bore / M3 hole separation check ---")
# Between each corner strut bore and its nearest M3 hole, probe the gap.
# The gap region should be solid, confirming the two voids are separated.
gap_checks = [
    ("S-TL vs 1-A", 18.5, 1.5, 61.0),   # Between strut right edge (12.2) and hole left edge (24.05)
    ("S-TR vs 2-B", 152.5, 1.5, 61.0),   # Between strut left edge (157.8) and hole right edge (145.95)
    ("S-BL vs 1-D", 18.5, 1.5, 7.3),     # Between strut right edge (12.2) and hole left edge (24.05)
    ("S-BR vs 2-C", 152.5, 1.5, 7.3),    # Between strut left edge (157.8) and hole right edge (145.95)
]
for name, gx, gy, gz in gap_checks:
    v.check_solid(f"Gap {name}", gx, gy, gz,
                  f"solid in gap between strut bore and M3 hole — confirms no overlap")
print()

# --- Bounding box (Rubric 5) ---
print("--- Bounding box (Rubric 5) ---")
bb = plate.val().BoundingBox()
print(f"  Actual bounding box:")
print(f"    X: [{bb.xmin:.3f}, {bb.xmax:.3f}]  (expected [0, 140.0])")
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
# Plate body: 140.0 × 3.0 × 68.6 = 28812 mm³
# - 2 motor bores: 2 × π × 18.5² × 3.0 = 6472 mm³
# - 8 M3 holes: 8 × π × 1.65² × 3.0 = 205 mm³
# - 4 strut bores: 4 × 6.4 × 6.4 × 3.0 = 491 mm³
# Estimated: 28812 - 6472 - 205 - 491 ≈ 21644 mm³
# Fill ratio: 21644 / 28812 ≈ 0.751
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
