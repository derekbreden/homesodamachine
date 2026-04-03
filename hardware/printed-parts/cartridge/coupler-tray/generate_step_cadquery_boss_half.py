"""
Coupler Tray Boss Half — CadQuery STEP Generation Script
Season 1, Phase 6 — Widen coupler tray to match pump tray

Specification source: hardware/printed-parts/cartridge/coupler-tray/parts.md
Parent geometry:      hardware/printed-parts/cartridge/coupler-tray/generate_step_cadquery.py (Phase 4)

This script generates the BOSS HALF of the split coupler tray.
The boss half spans Z=34.3mm to Z=68.6mm (top half of the assembled tray).
The mating face is at Z=34.3mm (assembly frame), flat.

The split cuts through the center of each coupler hole (all at Z=34.3mm),
producing semicircular channels on the mating face. The bosses are also
cut in half — each boss becomes a semicircular protrusion on the mating face.

The two top strut bores (S-TL at Z=63.6mm, S-TR at Z=63.6mm) are entirely
within this half. The two bottom strut bores (Z=5.0mm) are in the base half.

Coordinate System Declaration:
  All coordinates are given in the assembly frame (same as Phase 4):
  Origin: plate bottom-left-front corner (X=0, Y=0, Z=0)
  X: plate width axis — left to right, 0..170.0mm
  Y: plate thickness axis — front face (Y=0) to back face of base (Y=3mm);
     boss halves extend from Y=3 to Y=12.08mm
  Z: plate height axis — bottom to top, assembly Z=34.3..103.6mm for this half
  Bounding envelope of this part: 170.0mm (X) x 12.08mm (Y) x 69.3mm (Z)
    (Z=34.3mm to Z=103.6mm in assembly frame, so part height = 69.3mm)

  Approach: Build the full Phase 4 tray body and cut away the bottom half
  (Z=0 to Z=34.3) with a box. This ensures the semicircular channels and
  semicircular boss halves are exact geometric remainders of the original
  cylindrical features.

  The resulting solid occupies assembly-frame Z=34.3..68.6mm. CadQuery will
  place it with actual Z coordinates in that range. The STEP file is exported
  in this frame — assembly-frame coordinates are preserved.

  Print orientation: mating face (assembly Z=34.3mm) down on build plate.
  The semicircular channels open downward toward the build plate — no overhang.
  Bosses protrude in +Y (upward from back face during print).
"""

from pathlib import Path

import cadquery as cq

# Dimensions (from parts.md, unchanged from Phase 4)

PLATE_W     = 170.0    # widened from 140.0
PLATE_D     = 3.0
PLATE_H     = 103.6    # was 68.6, +35mm
SPLIT_Z     = 34.3
BOSS_H_HALF = PLATE_H - SPLIT_Z   # 34.3mm — height of boss half

BOSS_OD     = 16.0
BOSS_ID     = 9.5
BOSS_R_OUT  = BOSS_OD / 2.0
BOSS_R_IN   = BOSS_ID / 2.0
FULL_DEPTH  = 12.08
BOSS_H      = FULL_DEPTH - PLATE_D   # 9.08mm

HOLE_DIA    = 9.5
HOLE_R      = HOLE_DIA / 2.0

HOLES = [
    ("H1/B1", 59.5, 34.3),
    ("H2/B2", 76.5, 34.3),
    ("H3/B3", 93.5, 34.3),
    ("H4/B4", 110.5, 34.3),
]

STRUT_BORE_W = 6.4
STRUT_BORE_H = 6.4

# Only top two strut bores are in the boss half
STRUT_BORES_BOSS = [
    ("S-TL",   9.0, 51.1),
    ("S-TR", 161.0, 51.1),
]

MID_Y_BASE  = PLATE_D / 2.0
MID_Y_BOSS  = PLATE_D + BOSS_H / 2.0    # 7.54mm
MID_Y_BORE  = FULL_DEPTH / 2.0
OVERCUT     = 0.1

# Z midpoint of boss half in assembly frame
MID_Z_BOSS_HALF = (SPLIT_Z + PLATE_H) / 2.0   # 51.45mm

# Build the full Phase 4 tray body, then cut off the bottom half.

print("Building full Phase 4 tray body (will then cut to boss half)...")
print()

# Feature 1 — Base Plate (full height)
print("Feature 1 — Base plate (170.0 x 3 x 68.6 mm, full height)...")
plate = (
    cq.Workplane("XY")
    .box(PLATE_W, PLATE_D, PLATE_H, centered=False)
)

# Features 2-5 — Bosses (full cylinders)
print(f"Features 2-5 — 4x bosses (OD={BOSS_OD}mm, h={BOSS_H}mm, Y=3->12.08mm)...")
for feat_id, hx, hz in HOLES:
    print(f"  Adding boss {feat_id} at X={hx}, Z={hz}")
    boss = (
        cq.Workplane("XZ")
        .workplane(offset=-PLATE_D)
        .center(hx, hz)
        .circle(BOSS_R_OUT)
        .extrude(-BOSS_H)
    )
    plate = plate.union(boss)
print("Bosses complete.")
print()

# Features 6-9 — Through-bores
print(f"Features 6-9 — 4x through-bores ({HOLE_DIA}mm dia, Y=0->{FULL_DEPTH}mm)...")
for feat_id, hx, hz in HOLES:
    print(f"  Cutting bore {feat_id} at X={hx}, Z={hz}")
    bore = (
        cq.Workplane("XZ")
        .workplane(offset=0)
        .center(hx, hz)
        .circle(HOLE_R)
        .extrude(-(FULL_DEPTH + OVERCUT))
    )
    plate = plate.cut(bore)
print("Coupler bores complete.")
print()

# Features 10-11 — Top strut bores only (Z=63.6mm — in boss half)
print(f"Features 10-11 — 2x top strut bores ({STRUT_BORE_W}x{STRUT_BORE_H}mm)...")
for bore_id, cx, cz in STRUT_BORES_BOSS:
    x0 = cx - STRUT_BORE_W / 2
    z0 = cz - STRUT_BORE_H / 2
    bore_box = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(x0, -OVERCUT / 2, z0))
        .box(STRUT_BORE_W, PLATE_D + OVERCUT, STRUT_BORE_H, centered=False)
    )
    plate = plate.cut(bore_box)
    print(f"  [-] Strut bore {bore_id} at X={cx}, Z={cz}")
print("Top strut bores complete.")
print()

# Cut the bottom half (Z=0 to Z=SPLIT_Z) to produce the boss half.
# The cut box starts below Z=0 and goes up to Z=SPLIT_Z.

print(f"Cutting bottom half (Z={-OVERCUT} to Z={SPLIT_Z}) to produce boss half...")
bottom_cut = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(-OVERCUT / 2, -OVERCUT / 2, -OVERCUT))
    .box(PLATE_W + OVERCUT, FULL_DEPTH + OVERCUT, SPLIT_Z + OVERCUT, centered=False)
)
plate = plate.cut(bottom_cut)
print("Boss half produced.")
print()

print()

# Export STEP file

OUTPUT_STEP = Path(__file__).resolve().parent / "coupler-tray-boss-half-cadquery.step"
print(f"Exporting STEP file -> {OUTPUT_STEP}")
cq.exporters.export(plate, str(OUTPUT_STEP))
print()

print("RUBRIC 3 — Feature-Specification Reconciliation")
print()
