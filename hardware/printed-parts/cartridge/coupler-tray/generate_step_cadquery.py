"""
Coupler Tray — CadQuery STEP Generation Script
Season 1, Phase 1, Item 3

Specification source: hardware/printed-parts/cartridge/coupler-tray/planning/parts.md
JG union geometry:    hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md

Rubric 2 — Coordinate System Declaration:
  Origin: plate bottom-left-front corner (X=0, Y=0, Z=0)
  X: plate width axis — left to right, 0..137.2mm
  Y: plate thickness axis — front face (Y=0) to back face (Y=12.08mm)
  Z: plate height axis — bottom to top, 0..68.6mm
  Envelope: 137.2mm (X) × 12.08mm (Y) × 68.6mm (Z)

  The 4 hole axes are parallel to Y.
  Print orientation: Y=0 face down on build plate; holes become vertical cylinders.
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
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  COUPLER TRAY — Feature Planning Table (Rubric 1)                                                                               ║
╠═══╦══════════════════════╦══════════════════════════════════════════╦═══════════╦══════╦═════════════════╦══════════════════════╗
║ # ║ Feature Name         ║ Mechanical Function                      ║ Operation ║ Axis ║ Center (X,Y,Z)  ║ Dimensions           ║
╠═══╬══════════════════════╬══════════════════════════════════════════╬═══════════╬══════╬═════════════════╬══════════════════════╣
║ 1 ║ Plate body           ║ Structural substrate; body-end shoulders ║ Add       ║  —   ║ (68.6,6.04,34.3)║ 137.2×12.08×68.6 mm  ║
║   ║                      ║ of JG union bear against both faces      ║           ║      ║                 ║                      ║
╠═══╬══════════════════════╬══════════════════════════════════════════╬═══════════╬══════╬═════════════════╬══════════════════════╣
║ 2 ║ Hole H1 (bot-left)   ║ Press-fit capture of JG union central    ║ Remove    ║  Y   ║ (60.1,6.04,25.8)║ 9.5mm dia, TH        ║
║ 3 ║ Hole H2 (bot-right)  ║ body (9.31mm OD); shoulders on 15.10mm  ║ Remove    ║  Y   ║ (77.1,6.04,25.8)║ 9.5mm dia, TH        ║
║ 4 ║ Hole H3 (top-left)   ║ body ends provide axial retention        ║ Remove    ║  Y   ║ (60.1,6.04,42.8)║ 9.5mm dia, TH        ║
║ 5 ║ Hole H4 (top-right)  ║ against both plate faces                 ║ Remove    ║  Y   ║ (77.1,6.04,42.8)║ 9.5mm dia, TH        ║
╚═══╩══════════════════════╩══════════════════════════════════════════╩═══════════╩══════╩═════════════════╩══════════════════════╝
TH = through-hole, full Y depth (0→12.08mm)
Grid: 2×2, centered at (X=68.6, Z=34.3), 17mm c-c in both X and Z.
"""

print(FEATURE_TABLE)

# ---------------------------------------------------------------------------
# Dimensions (from parts.md)
# ---------------------------------------------------------------------------

# Plate envelope
PLATE_W = 137.2   # X — width left to right
PLATE_D = 12.08   # Y — thickness front to back
PLATE_H = 68.6    # Z — height bottom to top

# Coupler capture hole
HOLE_DIA = 9.5    # mm — per build sequence; press-fit on 9.31mm JG union center body
HOLE_R   = HOLE_DIA / 2.0

# Hole centers (X, Z) — 2×2 grid centered at (68.6, 34.3), 17mm c-c
HOLES = [
    ("H1", 60.1, 25.8),   # bottom-left
    ("H2", 77.1, 25.8),   # bottom-right
    ("H3", 60.1, 42.8),   # top-left
    ("H4", 77.1, 42.8),   # top-right
]

MID_Y = PLATE_D / 2.0     # 6.04mm — used for mid-depth probes

# ---------------------------------------------------------------------------
# Feature 1 — Plate Body
# centered=False places box with corner at origin, extending +X, +Y, +Z.
# Result: X:[0,137.2], Y:[0,12.08], Z:[0,68.6]
# ---------------------------------------------------------------------------

print("Building Feature 1 — Plate body (137.2 × 12.08 × 68.6 mm)...")

plate = (
    cq.Workplane("XY")
    .box(PLATE_W, PLATE_D, PLATE_H, centered=False)
)

# ---------------------------------------------------------------------------
# Features 2–5 — Coupler Capture Holes (4×, 9.5mm dia, through Y)
#
# XZ workplane normal is -Y. workplane(offset=0) positions the sketch at Y=0.
# extrude(-(PLATE_D + overcut)) goes in +Y direction, cutting from front face
# (Y=0) through to beyond the back face (Y=12.08mm).
# ---------------------------------------------------------------------------

print("Building Features 2–5 — 4× coupler capture holes (9.5mm dia, through Y)...")

OVERCUT = 0.1   # mm past back face to ensure clean boolean exit

for hole_id, hx, hz in HOLES:
    print(f"  Cutting hole {hole_id} at X={hx}, Z={hz}")
    cyl = (
        cq.Workplane("XZ")
        .workplane(offset=0)              # sketch plane at Y=0 (front face)
        .center(hx, hz)                   # hole center in XZ
        .circle(HOLE_R)
        .extrude(-(PLATE_D + OVERCUT))    # +Y direction: Y=0 → Y=12.18mm
    )
    plate = plate.cut(cyl)

print("Model construction complete.")
print()

# ---------------------------------------------------------------------------
# Export STEP file
# ---------------------------------------------------------------------------

OUTPUT_STEP = Path(__file__).resolve().parent / "coupler-tray-cadquery.step"
print(f"Exporting STEP file → {OUTPUT_STEP}")
cq.exporters.export(plate, str(OUTPUT_STEP))
print("Export complete.")
print()

# ---------------------------------------------------------------------------
# Rubric 3 — Feature-Specification Reconciliation
# Probe every feature row from the Feature Planning Table.
# ---------------------------------------------------------------------------

print("=" * 60)
print("RUBRIC 3 — Feature-Specification Reconciliation")
print("=" * 60)
print()

v = Validator(plate)

# --- Feature 1: Plate body ---
print("Feature 1 — Plate body:")
v.check_solid("Plate body center",      68.6,         MID_Y, 34.3,  "solid at plate geometric center")
v.check_solid("Plate near front face",  68.6,         0.5,   34.3,  "solid near Y=0 front face")
v.check_solid("Plate near back face",   68.6,         11.5,  34.3,  "solid near Y=12.08 back face")
v.check_solid("Plate near left edge",   0.5,          MID_Y, 34.3,  "solid near X=0 left edge")
v.check_solid("Plate near right edge",  136.7,        MID_Y, 34.3,  "solid near X=137.2 right edge")
v.check_solid("Plate near bottom edge", 68.6,         MID_Y, 0.5,   "solid near Z=0 bottom edge")
v.check_solid("Plate near top edge",    68.6,         MID_Y, 68.1,  "solid near Z=68.6 top edge")
print()

# --- Features 2–5: Coupler capture holes ---
# Each hole: void at center mid-depth, void near both faces (through-hole confirmation),
# solid just outside hole radius (+X direction), orientation check (+Z axis probe).
for hole_id, hx, hz in HOLES:
    print(f"Feature — Hole {hole_id} at X={hx}, Z={hz}:")

    # Void at center, mid-depth
    v.check_void(f"Hole {hole_id} center (mid-depth)",
                 hx, MID_Y, hz,
                 f"void at ({hx}, {MID_Y:.2f}, {hz}) — hole center mid-depth")

    # Void near front face — confirms hole enters Y=0 face
    v.check_void(f"Hole {hole_id} near front face",
                 hx, 0.5, hz,
                 f"void at ({hx}, 0.5, {hz}) — hole enters front face")

    # Void near back face — confirms through-hole exits Y=12.08 face
    v.check_void(f"Hole {hole_id} near back face",
                 hx, 11.5, hz,
                 f"void at ({hx}, 11.5, {hz}) — hole exits back face")

    # Solid just outside hole radius in +X — 6.5mm > HOLE_R (4.75mm)
    v.check_solid(f"Hole {hole_id} solid outside (+X)",
                  hx + 6.5, MID_Y, hz,
                  f"solid at ({hx + 6.5:.1f}, {MID_Y:.2f}, {hz}) — outside r={HOLE_R}mm in +X")

    # Solid just outside hole radius in +Z — orientation check
    v.check_solid(f"Hole {hole_id} solid outside (+Z)",
                  hx, MID_Y, hz + 6.5,
                  f"solid at ({hx}, {MID_Y:.2f}, {hz + 6.5:.1f}) — outside r={HOLE_R}mm in +Z")

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

# Volume estimate:
#   Plate envelope: 137.2 × 12.08 × 68.6 = 113,822 mm³
#   4 holes: π × (4.75)² × 12.08 ≈ 857.8 mm³ each × 4 = 3,431 mm³
#   Expected volume ≈ 110,391 mm³ → ratio ≈ 0.970 of envelope
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
