"""
Coupler Tray Base Half — CadQuery STEP Generation Script
Season 1, Phase 6 — Widen coupler tray to match pump tray

Specification source: hardware/printed-parts/cartridge/coupler-tray/parts.md
Parent geometry:      hardware/printed-parts/cartridge/coupler-tray/generate_step_cadquery.py (Phase 4)

This script generates the BASE HALF of the split coupler tray.
The base half spans Z=0 to Z=34.3mm (bottom half of the assembled tray).
The mating face is at Z=34.3mm, flat.

The split cuts through the center of each coupler hole (all at Z=34.3mm),
producing semicircular channels on the mating face. The bosses are also
cut in half — each boss becomes a semicircular protrusion on the mating face.

The two bottom strut bores (S-BL at Z=5.0mm, S-BR at Z=5.0mm) are entirely
within this half. The two top strut bores (Z=63.6mm) are in the boss half.

Coordinate System Declaration:
  Origin: plate bottom-left-front corner (X=0, Y=0, Z=0)
  X: plate width axis — left to right, 0..170.0mm
  Y: plate thickness axis — front face (Y=0) to back face of base (Y=3mm);
     boss halves extend from Y=3 to Y=12.08mm
  Z: plate height axis — bottom to top, 0..34.3mm (this half only)
     Z=0: bottom face of assembled tray
     Z=34.3mm: mating face (top face of this half)
  Bounding envelope: 170.0mm (X) x 12.08mm (Y) x 34.3mm (Z)

  Approach: Build the full Phase 4 tray body and cut away the top half
  (Z=34.3 to Z=68.6) with a box. This ensures the semicircular channels and
  semicircular boss halves are exact geometric remainders of the original
  cylindrical features.

  Print orientation: front face (Y=0) down on build plate; Z is up during
  printing. Semicircular channels open toward +Z (upward) — no overhang.
"""

from pathlib import Path

import cadquery as cq

# Dimensions (from parts.md, unchanged from Phase 4)

PLATE_W     = 170.0    # X — width left to right (widened from 140.0)
PLATE_D     = 3.0      # Y — base plate thickness
PLATE_H     = 103.6    # Z — full tray height (was 68.6, +35mm)
SPLIT_Z     = 34.3     # Z — split plane (centerline of coupler holes)
BASE_H      = SPLIT_Z  # Z — height of base half (0..34.3mm)

BOSS_OD     = 16.0
BOSS_ID     = 9.5
BOSS_R_OUT  = BOSS_OD / 2.0    # 8.0mm
BOSS_R_IN   = BOSS_ID / 2.0    # 4.75mm
FULL_DEPTH  = 12.08
BOSS_H      = FULL_DEPTH - PLATE_D   # 9.08mm

HOLE_DIA    = 9.5
HOLE_R      = HOLE_DIA / 2.0   # 4.75mm

# Hole/boss centers — 1x4 row, all at Z=34.3mm (at the split plane)
HOLES = [
    ("H1/B1", 59.5, 34.3),
    ("H2/B2", 76.5, 34.3),
    ("H3/B3", 93.5, 34.3),
    ("H4/B4", 110.5, 34.3),
]

STRUT_BORE_W = 6.4
STRUT_BORE_H = 6.4

# Only bottom two strut bores are in the base half
STRUT_BORES_BASE = [
    ("S-BL",   9.0, 17.5),
    ("S-BR", 161.0, 17.5),
]

MID_Y_BASE  = PLATE_D / 2.0
MID_Y_BOSS  = PLATE_D + BOSS_H / 2.0    # 7.54mm
MID_Y_BORE  = FULL_DEPTH / 2.0           # 6.04mm
OVERCUT     = 0.1

# Build the full Phase 4 tray body first, then cut off the top half.
# This is the cleanest approach — the semicircular features are produced
# automatically by the boolean intersection with the split plane.

print("Building full Phase 4 tray body (will then cut to base half)...")
print()

# Feature 1 — Base Plate (full height Z=0..68.6)
print("Feature 1 — Base plate (170.0 x 3 x 68.6 mm, full height)...")
plate = (
    cq.Workplane("XY")
    .box(PLATE_W, PLATE_D, PLATE_H, centered=False)
)

# Features 2-5 — Bosses (full cylinders, back face, same as Phase 4)
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

# Features 6-9 — Through-bores (full depth, same as Phase 4)
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

# Features 10-11 — Bottom strut bores only (Z=5.0mm — in base half)
print(f"Features 10-11 — 2x bottom strut bores ({STRUT_BORE_W}x{STRUT_BORE_H}mm)...")
for bore_id, cx, cz in STRUT_BORES_BASE:
    x0 = cx - STRUT_BORE_W / 2
    z0 = cz - STRUT_BORE_H / 2
    bore_box = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(x0, -OVERCUT / 2, z0))
        .box(STRUT_BORE_W, PLATE_D + OVERCUT, STRUT_BORE_H, centered=False)
    )
    plate = plate.cut(bore_box)
    print(f"  [-] Strut bore {bore_id} at X={cx}, Z={cz}")
print("Bottom strut bores complete.")
print()

# Cut the top half (Z=SPLIT_Z to Z=PLATE_H+OVERCUT) to produce the base half.
# This single cut simultaneously:
#   - Removes the upper plate body
#   - Turns each full cylindrical boss into a semicircular half-boss
#   - Turns each full circular bore into a semicircular channel on the mating face

print(f"Cutting top half (Z={SPLIT_Z} to Z={PLATE_H+OVERCUT}) to produce base half...")
top_cut = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0, -OVERCUT / 2, SPLIT_Z))
    .box(PLATE_W + OVERCUT, FULL_DEPTH + OVERCUT, PLATE_H - SPLIT_Z + OVERCUT, centered=False)
)
plate = plate.cut(top_cut)
print("Base half produced.")
print()

print()

# Export STEP file

OUTPUT_STEP = Path(__file__).resolve().parent / "coupler-tray-base-half-cadquery.step"
print(f"Exporting STEP file -> {OUTPUT_STEP}")
cq.exporters.export(plate, str(OUTPUT_STEP))
print()

print("RUBRIC 3 — Feature-Specification Reconciliation")
print()
