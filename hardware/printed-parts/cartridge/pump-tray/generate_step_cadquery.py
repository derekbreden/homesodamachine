"""
Pump Tray — CadQuery STEP Generation Script
Season 1, Phase 1, Item 2

Specification source: hardware/printed-parts/cartridge/pump-tray/planning/parts.md
Coordinate source:    hardware/printed-parts/cartridge/pump-tray/planning/spatial-resolution.md
Pump geometry source: hardware/off-the-shelf-parts/kamoer-kphm400/extracted-results/geometry-description.md

Rubric 1 — Feature Planning Table:
printed to stdout at runtime (see FEATURE_TABLE below)

Rubric 2 — Coordinate System Declaration:
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

# ---------------------------------------------------------------------------
# Rubric 1 — Feature Planning Table (printed to stdout)
# ---------------------------------------------------------------------------

FEATURE_TABLE = """
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  PUMP TRAY — Feature Planning Table (Rubric 1)                                                              ║
╠═══╦══════════════════════════╦════════════════════════════════════════╦═══════════╦══════════╦═══════════════╣
║ # ║ Feature Name             ║ Mechanical Function                    ║ Operation ║ Axis     ║ Dims          ║
╠═══╬══════════════════════════╬════════════════════════════════════════╬═══════════╬══════════╬═══════════════╣
║ 1 ║ Plate body               ║ Structural substrate for both pumps    ║ Add       ║ —        ║ 137.2×3.0×68.6║
║ 2 ║ Motor bore 1 (Pump 1)    ║ Motor cylinder passes through; enables motor-side screw access  ║ Remove    ║ Y        ║ 37mm dia, TH  ║
║ 3 ║ Motor bore 2 (Pump 2)    ║ Motor cylinder passes through; enables motor-side screw access  ║ Remove    ║ Y        ║ 37mm dia, TH  ║
║ 4 ║ Hole 1-A (P1 top-left)   ║ M3 clearance, pump 1 top-left screw   ║ Remove    ║ Y        ║ 3.3mm dia, TH ║
║ 5 ║ Hole 1-B (P1 top-right)  ║ M3 clearance, pump 1 top-right screw  ║ Remove    ║ Y        ║ 3.3mm dia, TH ║
║ 6 ║ Hole 1-C (P1 bot-right)  ║ M3 clearance, pump 1 bot-right screw  ║ Remove    ║ Y        ║ 3.3mm dia, TH ║
║ 7 ║ Hole 1-D (P1 bot-left)   ║ M3 clearance, pump 1 bot-left screw   ║ Remove    ║ Y        ║ 3.3mm dia, TH ║
║ 8 ║ Hole 2-A (P2 top-left)   ║ M3 clearance, pump 2 top-left screw   ║ Remove    ║ Y        ║ 3.3mm dia, TH ║
║ 9 ║ Hole 2-B (P2 top-right)  ║ M3 clearance, pump 2 top-right screw  ║ Remove    ║ Y        ║ 3.3mm dia, TH ║
║10 ║ Hole 2-C (P2 bot-right)  ║ M3 clearance, pump 2 bot-right screw  ║ Remove    ║ Y        ║ 3.3mm dia, TH ║
║11 ║ Hole 2-D (P2 bot-left)   ║ M3 clearance, pump 2 bot-left screw   ║ Remove    ║ Y        ║ 3.3mm dia, TH ║
╚═══╩══════════════════════════╩════════════════════════════════════════╩═══════════╩══════════╩═══════════════╝
TH = through-hole, full Y depth (0→3.0mm)
"""

print(FEATURE_TABLE)

# ---------------------------------------------------------------------------
# Dimensions (from parts.md / spatial-resolution.md)
# ---------------------------------------------------------------------------

# Plate envelope
PLATE_W = 137.2   # X — width left to right
PLATE_D = 3.0     # Y — thickness front to back
PLATE_H = 68.6    # Z — height bottom to top

# Clearance hole diameter
HOLE_DIA = 3.3    # mm — M3 nominal 3.0 + 0.2mm loose clearance (requirements.md)
HOLE_R = HOLE_DIA / 2.0

# Motor bore diameter
MOTOR_BORE_DIA = 37.0   # mm — per vision.md (~37mm for 35.73mm motor cylinder)
MOTOR_BORE_R = MOTOR_BORE_DIA / 2.0

# Motor bore centers (XZ positions) — from spatial-resolution.md Section 3.3
MOTOR_BORES = [
    ("bore-1", 34.3,  34.3),   # Pump 1 motor axis
    ("bore-2", 102.9, 34.3),   # Pump 2 motor axis
]

# Hole XZ positions — (X, Z) in part-local frame
# Pump 1 center: X=34.3, Z=34.3 — holes at ±25mm in X and Z
# Pump 2 center: X=102.9, Z=34.3 — holes at ±25mm in X and Z
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

# ---------------------------------------------------------------------------
# Feature 1 — Plate Body
# Build the rectangular solid.
# Origin at bottom-left-front corner: X:[0,137.2], Y:[0,3.0], Z:[0,68.6]
# centered=False places box with corner at origin, extending +X, +Y, +Z.
# ---------------------------------------------------------------------------

print("Building Feature 1 — Plate body (137.2 × 3.0 × 68.6 mm)...")

plate = (
    cq.Workplane("XY")
    .box(PLATE_W, PLATE_D, PLATE_H, centered=False)
    # centered=False: box occupies X:[0,137.2], Y:[0,3.0], Z:[0,68.6]
)

# ---------------------------------------------------------------------------
# Features 2–3 — Motor Bores (2×, 37mm dia, through Y=0 to Y=3.0mm)
#
# Same approach as the M3 holes: XZ workplane, sketch at Y=0, extrude in +Y
# using a negative extrude value (-(PLATE_D + overcut)).
# ---------------------------------------------------------------------------

print("Building Features 2-3 — 2× Motor bores (37mm dia, through Y)...")

for bore_id, bx, bz in MOTOR_BORES:
    print(f"  Cutting motor bore {bore_id} at X={bx}, Z={bz}")
    overcut = 0.1
    bore_cyl = (
        cq.Workplane("XZ")
        .workplane(offset=0)        # sketch plane at Y=0 (front face)
        .center(bx, bz)             # bore center in XZ
        .circle(MOTOR_BORE_R)
        .extrude(-(PLATE_D + overcut))
        # negative extrude on XZ workplane goes in +Y direction
        # cuts from Y=0 through to Y=3.1mm, clearing the Y=3.0 back face
    )
    plate = plate.cut(bore_cyl)

# ---------------------------------------------------------------------------
# Features 4–11 — M3 Clearance Holes (8×, through Y=0 to Y=3.0mm)
#
# Approach: use the XZ workplane (normal = -Y direction).
# Sketch at the midplane of the plate (or anywhere along Y — it doesn't
# matter for a through-hole since both bore and extrude reach beyond the faces).
# Use a cylinder cut from Y=0 front face through to Y=3.0mm back face.
#
# We'll use cq.Workplane("XZ") to sketch circles at each hole center,
# then extrude through the full plate depth.
# On the XZ workplane, normal is -Y; extrude(depth) goes in -Y direction.
# We position at Y=PLATE_D (back face) and extrude forward (into +Y going -Y).
# Alternatively: cut with a cylinder aligned along Y at each (X,Z) position.
# ---------------------------------------------------------------------------

print("Building Features 4–11 — 8× M3 clearance holes (3.3mm dia, through Y)...")

for hole_id, hx, hz in HOLES:
    print(f"  Cutting hole {hole_id} at X={hx}, Z={hz}")
    # Build a cylinder aligned with the Y axis (through-hole).
    #
    # XZ workplane normal is -Y. workplane(offset=0) positions the sketch plane
    # at Y=0 (the front face of the plate).
    # extrude(d) goes in the -Y direction (outward, away from plate front).
    # extrude(-d) goes in the +Y direction (through the plate toward back face).
    #
    # Strategy: sketch at Y=0 (front face), extrude in -Y direction with
    # both=True and depth = PLATE_D/2 + overcut.
    # Actually simpler: sketch at Y=0, extrude(-PLATE_D - overcut) goes +Y,
    # cutting from front face through to beyond the back face.
    overcut = 0.1
    cyl = (
        cq.Workplane("XZ")
        .workplane(offset=0)        # sketch plane at Y=0 (front face)
        .center(hx, hz)             # hole center in XZ
        .circle(HOLE_R)
        .extrude(-(PLATE_D + overcut))
        # negative extrude on XZ workplane goes in +Y direction
        # cuts from Y=0 through to Y=3.1mm, clearing the Y=3.0 back face
    )
    plate = plate.cut(cyl)

print("Model construction complete.")
print()

# ---------------------------------------------------------------------------
# Export STEP file
# ---------------------------------------------------------------------------

OUTPUT_STEP = Path(__file__).resolve().parent / "pump-tray-cadquery.step"
print(f"Exporting STEP file → {OUTPUT_STEP}")
cq.exporters.export(plate, str(OUTPUT_STEP))
print("Export complete.")
print()

# ---------------------------------------------------------------------------
# Rubric 3 — Feature-Specification Reconciliation
# Probe every feature against the built solid.
# ---------------------------------------------------------------------------

print("=" * 60)
print("RUBRIC 3 — Feature-Specification Reconciliation")
print("=" * 60)
print()

v = Validator(plate)

# --- Feature 1: Plate body interior ---
# Probe at geometric center of plate — must be solid (material present)
print("Feature 1 — Plate body:")
v.check_solid("Plate body center", 68.6, 1.5, 34.3,
              "solid at plate geometric center (68.6, 1.5, 34.3)")

# Probe near each face — verify plate extends to its boundaries
v.check_solid("Plate near front face", 68.6, 0.1, 34.3,
              "solid near Y=0 front face")
v.check_solid("Plate near back face", 68.6, 2.9, 34.3,
              "solid near Y=3.0 back face")
v.check_solid("Plate near left edge", 0.5, 1.5, 34.3,
              "solid near X=0 left edge")
v.check_solid("Plate near right edge", 136.7, 1.5, 34.3,
              "solid near X=137.2 right edge")
v.check_solid("Plate near bottom edge", 68.6, 1.5, 0.5,
              "solid near Z=0 bottom edge")
v.check_solid("Plate near top edge", 68.6, 1.5, 68.1,
              "solid near Z=68.6 top edge")
print()

# --- Features 2–3: Motor bores ---
# For each bore: probe void at center, near front face, near back face,
# and solid just outside bore radius in +X and +Z directions.
for bore_id, bx, bz in MOTOR_BORES:
    print(f"Feature — Motor bore {bore_id} at X={bx}, Z={bz}:")
    v.check_void(f"Motor bore {bore_id} center (mid-depth)", bx, 1.5, bz, f"void at ({bx}, 1.5, {bz}) — bore center mid-depth")
    v.check_void(f"Motor bore {bore_id} near front face (Y=0.1)", bx, 0.1, bz, f"void at ({bx}, 0.1, {bz}) — bore enters front face")
    v.check_void(f"Motor bore {bore_id} near back face (Y=2.9)", bx, 2.9, bz, f"void at ({bx}, 2.9, {bz}) — bore exits back face")
    # Solid outside bore radius
    v.check_solid(f"Motor bore {bore_id} solid outside (+X)", bx + MOTOR_BORE_R + 2.0, 1.5, bz, f"solid at ({bx + MOTOR_BORE_R + 2.0:.1f}, 1.5, {bz}) — outside bore radius")
    v.check_solid(f"Motor bore {bore_id} solid outside (+Z)", bx, 1.5, bz + MOTOR_BORE_R + 2.0, f"solid at ({bx}, 1.5, {bz + MOTOR_BORE_R + 2.0:.1f}) — outside bore radius in Z")
    print()

# --- Features 4–11: Each clearance hole ---
# For each hole: probe void at center (X, Y=1.5, Z), then solid just outside
# Also probe void at both faces (Y=0.1 and Y=2.9) to confirm through-hole
for hole_id, hx, hz in HOLES:
    print(f"Feature — Hole {hole_id} at X={hx}, Z={hz}:")

    # Void at hole center at mid-depth
    v.check_void(f"Hole {hole_id} center (mid-depth)",
                 hx, 1.5, hz,
                 f"void at ({hx}, 1.5, {hz}) — hole center mid-depth")

    # Void near front face (Y=0.1) — confirms through-hole entry
    v.check_void(f"Hole {hole_id} near front face (Y=0.1)",
                 hx, 0.1, hz,
                 f"void at ({hx}, 0.1, {hz}) — hole enters front face")

    # Void near back face (Y=2.9) — confirms through-hole exit
    v.check_void(f"Hole {hole_id} near back face (Y=2.9)",
                 hx, 2.9, hz,
                 f"void at ({hx}, 2.9, {hz}) — hole exits back face")

    # Solid just outside hole radius in +X direction (2.5mm offset from center)
    # 2.5mm > HOLE_R (1.65mm), so this point is outside the hole → solid
    offset = 2.5
    v.check_solid(f"Hole {hole_id} solid just outside (+X)",
                  hx + offset, 1.5, hz,
                  f"solid at ({hx + offset:.1f}, 1.5, {hz}) — {offset}mm from center, outside r={HOLE_R}mm")

    print()

# ---------------------------------------------------------------------------
# Rubric 4 — Solid Validity
# ---------------------------------------------------------------------------

print("=" * 60)
print("RUBRIC 4 — Solid Validity")
print("=" * 60)
print()

v.check_valid()
v.check_single_body()

# Volume: plate envelope = 137.2 × 3.0 × 68.6 = 28237.44 mm³
# 8 screw holes remove: π × (1.65)² × 3.0 = 25.76 mm³ each × 8 = 206.08 mm³
# 2 motor bores remove: π × (18.5)² × 3.0 = 3236.11 mm³ each × 2 = 6472.22 mm³
# Expected volume ≈ 28237.44 - 206.08 - 6472.22 ≈ 21559 mm³
# Ratio ≈ 21559 / 28237 ≈ 0.764 — within (0.5, 1.2)
envelope_vol = PLATE_W * PLATE_D * PLATE_H
v.check_volume(expected_envelope=envelope_vol, fill_range=(0.5, 1.2))
print()

# ---------------------------------------------------------------------------
# Rubric 5 — Bounding Box Reconciliation
# ---------------------------------------------------------------------------

print("=" * 60)
print("RUBRIC 5 — Bounding Box Reconciliation")
print("=" * 60)
print()

bb = plate.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, 0.0, PLATE_W)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, PLATE_D)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, PLATE_H)
print()

# ---------------------------------------------------------------------------
# Final summary — exits 1 on any FAIL
# ---------------------------------------------------------------------------

if not v.summary():
    print()
    print("FAILURES DETECTED — fix model before exporting.")
    sys.exit(1)

print()
print(f"STEP file written: {OUTPUT_STEP}")
