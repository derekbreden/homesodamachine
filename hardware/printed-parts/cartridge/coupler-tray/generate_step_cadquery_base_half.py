"""
Coupler Tray Base Half — CadQuery STEP Generation Script
Season 1, Phase 5 — Split coupler tray into two halves

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

Rubric 2 — Coordinate System Declaration:
  Origin: plate bottom-left-front corner (X=0, Y=0, Z=0)
  X: plate width axis — left to right, 0..137.2mm
  Y: plate thickness axis — front face (Y=0) to back face of base (Y=3mm);
     boss halves extend from Y=3 to Y=12.08mm
  Z: plate height axis — bottom to top, 0..34.3mm (this half only)
     Z=0: bottom face of assembled tray
     Z=34.3mm: mating face (top face of this half)
  Bounding envelope: 137.2mm (X) x 12.08mm (Y) x 34.3mm (Z)

  Approach: Build the full Phase 4 tray body and cut away the top half
  (Z=34.3 to Z=68.6) with a box. This ensures the semicircular channels and
  semicircular boss halves are exact geometric remainders of the original
  cylindrical features.

  Print orientation: front face (Y=0) down on build plate; Z is up during
  printing. Semicircular channels open toward +Z (upward) — no overhang.
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
COUPLER TRAY BASE HALF — Feature Planning Table (Rubric 1)
===========================================================

Assembly frame coordinates (Z=0..34.3mm is this half):

  #   Feature Name              Op      Shape         Axis  Center (X,Y,Z)              Dimensions
  1   Base plate body           Add     Rect prism    —     (68.6, 1.5, 17.15)          137.2 x 3 x 34.3 mm
  2   Boss half B1              Add     Half-cyl      Y     (43.1, 7.54, 34.3)          OD 16mm, h 9.08mm, lower half (Z<=34.3)
  3   Boss half B2              Add     Half-cyl      Y     (60.1, 7.54, 34.3)          OD 16mm, h 9.08mm, lower half (Z<=34.3)
  4   Boss half B3              Add     Half-cyl      Y     (77.1, 7.54, 34.3)          OD 16mm, h 9.08mm, lower half (Z<=34.3)
  5   Boss half B4              Add     Half-cyl      Y     (94.1, 7.54, 34.3)          OD 16mm, h 9.08mm, lower half (Z<=34.3)
  6   Semicircular channel C1   Remove  Half-cyl bore Y     (43.1, 6.04, 34.3)          9.5mm dia, lower half bore, TH
  7   Semicircular channel C2   Remove  Half-cyl bore Y     (60.1, 6.04, 34.3)          9.5mm dia, lower half bore, TH
  8   Semicircular channel C3   Remove  Half-cyl bore Y     (77.1, 6.04, 34.3)          9.5mm dia, lower half bore, TH
  9   Semicircular channel C4   Remove  Half-cyl bore Y     (94.1, 6.04, 34.3)          9.5mm dia, lower half bore, TH
  10  Strut bore S-BL           Remove  Rect prism    Y     (10.0, 1.5, 5.0)            6.4 x 3 x 6.4 mm, TH
  11  Strut bore S-BR           Remove  Rect prism    Y     (127.2, 1.5, 5.0)           6.4 x 3 x 6.4 mm, TH

  Implementation: build full Phase 4 tray (Z 0..68.6), then cut top half
  (Z=34.3..68.6+overcut) with a large box to produce the base half.
  Semicircular channels and boss halves are produced automatically by
  the boolean cut — no separate feature operations needed.

TH = through-hole, full Y depth
Boss half Y center = (3 + 12.08) / 2 = 7.54mm
Bore Y center = 12.08 / 2 = 6.04mm
Strut bore Y center = 3.0 / 2 = 1.5mm
"""

print(FEATURE_TABLE)

# ---------------------------------------------------------------------------
# Dimensions (from parts.md, unchanged from Phase 4)
# ---------------------------------------------------------------------------

PLATE_W     = 137.2    # X — width left to right
PLATE_D     = 3.0      # Y — base plate thickness
PLATE_H     = 68.6     # Z — full tray height
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
    ("H1/B1", 43.1, 34.3),
    ("H2/B2", 60.1, 34.3),
    ("H3/B3", 77.1, 34.3),
    ("H4/B4", 94.1, 34.3),
]

STRUT_BORE_W = 6.4
STRUT_BORE_H = 6.4

# Only bottom two strut bores are in the base half
STRUT_BORES_BASE = [
    ("S-BL", 10.0,   5.0),
    ("S-BR", 127.2,  5.0),
]

MID_Y_BASE  = PLATE_D / 2.0
MID_Y_BOSS  = PLATE_D + BOSS_H / 2.0    # 7.54mm
MID_Y_BORE  = FULL_DEPTH / 2.0           # 6.04mm
OVERCUT     = 0.1

# ---------------------------------------------------------------------------
# Build the full Phase 4 tray body first, then cut off the top half.
# This is the cleanest approach — the semicircular features are produced
# automatically by the boolean intersection with the split plane.
# ---------------------------------------------------------------------------

print("Building full Phase 4 tray body (will then cut to base half)...")
print()

# Feature 1 — Base Plate (full height Z=0..68.6)
print("Feature 1 — Base plate (137.2 x 3 x 68.6 mm, full height)...")
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

# ---------------------------------------------------------------------------
# Cut the top half (Z=SPLIT_Z to Z=PLATE_H+OVERCUT) to produce the base half.
# This single cut simultaneously:
#   - Removes the upper plate body
#   - Turns each full cylindrical boss into a semicircular half-boss
#   - Turns each full circular bore into a semicircular channel on the mating face
# ---------------------------------------------------------------------------

print(f"Cutting top half (Z={SPLIT_Z} to Z={PLATE_H+OVERCUT}) to produce base half...")
top_cut = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0, -OVERCUT / 2, SPLIT_Z))
    .box(PLATE_W + OVERCUT, FULL_DEPTH + OVERCUT, PLATE_H - SPLIT_Z + OVERCUT, centered=False)
)
plate = plate.cut(top_cut)
print("Base half produced.")
print()

print("Model construction complete.")
print()

# ---------------------------------------------------------------------------
# Export STEP file
# ---------------------------------------------------------------------------

OUTPUT_STEP = Path(__file__).resolve().parent / "coupler-tray-base-half-cadquery.step"
print(f"Exporting STEP file -> {OUTPUT_STEP}")
cq.exporters.export(plate, str(OUTPUT_STEP))
print("Export complete.")
print()

# ---------------------------------------------------------------------------
# Rubric 3 — Feature-Specification Reconciliation
# ---------------------------------------------------------------------------

print("=" * 60)
print("RUBRIC 3 — Feature-Specification Reconciliation")
print("=" * 60)
print()

v = Validator(plate)

# --- Feature 1: Base plate body ---
print("Feature 1 — Base plate body (Z=0..34.3mm):")
v.check_solid("Base plate center",          68.6, MID_Y_BASE, 17.15,  "solid at base plate XZ center")
v.check_solid("Base plate near Y=0",        68.6, 0.3,        17.15,  "solid near front face Y=0")
v.check_solid("Base plate near Y=3",        68.6, 2.7,        17.15,  "solid near back face Y=3")
v.check_solid("Base plate left edge",        0.5, MID_Y_BASE, 17.15,  "solid near X=0")
v.check_solid("Base plate right edge",     136.7, MID_Y_BASE, 17.15,  "solid near X=137.2")
v.check_solid("Base plate bottom edge",     68.6, MID_Y_BASE,  0.5,   "solid near Z=0 bottom")
v.check_solid("Base plate near mating face",68.6, MID_Y_BASE, 34.0,   "solid near Z=34.3 mating face")
# Verify top half is gone — no material above Z=34.3 in body region (away from bosses/holes)
v.check_void("No material above split Z (away from bosses)",
             5.0, MID_Y_BASE, 35.0,
             "void at Z=35mm away from hole centers — top half removed")
# Verify no boss material above split
v.check_void("No boss material above split",
             43.1 + BOSS_R_IN + 1.0, MID_Y_BOSS, 35.0,
             "void at Z=35mm in boss wall region — boss cut at split plane")
print()

# --- Features 2-5: Semicircular boss halves ---
for feat_id, hx, hz in HOLES:
    bid = feat_id.split("/")[1]
    print(f"Feature — Semicircular boss half {bid} at X={hx}, Z={hz} (mating face):")

    # Solid in boss wall below split (at mating face, just below Z=34.3)
    # Sample on the +X side of the boss at Z just below the split
    v.check_solid(f"Boss half {bid} wall below split (+X)",
                  hx + BOSS_R_IN + (BOSS_R_OUT - BOSS_R_IN) / 2.0,
                  MID_Y_BOSS, hz - 0.5,
                  f"solid in boss half wall just below split Z={hz-0.5:.1f}")

    # Solid in boss wall away from split plane (well inside the half)
    v.check_solid(f"Boss half {bid} wall mid-height",
                  hx + BOSS_R_IN + (BOSS_R_OUT - BOSS_R_IN) / 2.0,
                  MID_Y_BOSS, hz - 2.0,
                  f"solid in boss wall at Z={hz-2.0:.1f}")

    # Void at boss center below split (inner bore present)
    v.check_void(f"Boss half {bid} inner bore below split",
                 hx, FULL_DEPTH - 0.5, hz - 0.5,
                 f"void at boss center near tip face, Z below split")

    # Void at mating face: boss does NOT extend above split (no boss above Z=34.3)
    v.check_void(f"Boss half {bid} no material above split",
                 hx + BOSS_R_IN + (BOSS_R_OUT - BOSS_R_IN) / 2.0,
                 MID_Y_BOSS, hz + 0.5,
                 f"void above split Z={hz+0.5:.1f} — boss half cut at split plane")

    print()

# --- Features 6-9: Semicircular channels on mating face ---
for feat_id, hx, hz in HOLES:
    hid = feat_id.split("/")[0]
    print(f"Feature — Semicircular channel {hid} at X={hx}, mating face Z={hz}:")

    # Void at bore center just below split (channel is open)
    v.check_void(f"Channel {hid} center below split",
                 hx, MID_Y_BASE, hz - 0.3,
                 f"void at channel center Z={hz-0.3:.1f} — semicircle opens toward mating face")

    # Void near front face at channel location
    v.check_void(f"Channel {hid} near front face",
                 hx, 0.3, hz - 0.3,
                 f"void near Y=0 at channel location")

    # Void in boss inner bore near tip face
    v.check_void(f"Channel {hid} in boss near tip",
                 hx, FULL_DEPTH - 0.3, hz - 0.3,
                 f"void in boss inner bore near tip face")

    # Path continuity: base plate bore meets boss bore at Y=3
    v.check_void(f"Channel {hid} path continuity below Y=3",
                 hx, PLATE_D - 0.1, hz - 0.3,
                 f"void just below Y=3 interface")
    v.check_void(f"Channel {hid} path continuity above Y=3",
                 hx, PLATE_D + 0.1, hz - 0.3,
                 f"void just above Y=3 interface")

    # Solid just outside bore radius in +X (in base plate) — confirms bore radius
    v.check_solid(f"Channel {hid} solid outside (+X) in base",
                  hx + HOLE_R + 0.5, MID_Y_BASE, hz - 0.3,
                  f"solid outside bore radius at Z just below split")

    # Mating face: channel is open (void) at split plane
    v.check_void(f"Channel {hid} open at mating face",
                 hx, MID_Y_BASE, hz - 0.05,
                 f"void very close to mating face — channel is open at Z={hz:.1f}")

    # Solid just above the split plane in the base plate region (away from hole)
    # This confirms the top half was removed
    # Check away from hole centers in X
    check_x = hx + HOLE_R + 2.0
    if check_x < PLATE_W - 1.0:
        v.check_void(f"Channel {hid} no plate above split",
                     check_x, MID_Y_BASE, hz + 0.3,
                     f"void above split plane — top half removed")
    print()

# --- Features 10-11: Bottom strut bores ---
print("Features 10-11 — Bottom strut bores (S-BL, S-BR):")
for bore_id, cx, cz in STRUT_BORES_BASE:
    half_w = STRUT_BORE_W / 2  # 3.2
    half_h = STRUT_BORE_H / 2  # 3.2

    v.check_void(f"Strut bore {bore_id} center",
                 cx, MID_Y_BASE, cz,
                 f"void at bore center ({cx}, {MID_Y_BASE}, {cz})")
    v.check_void(f"Strut bore {bore_id} front",
                 cx, 0.1, cz,
                 f"void near front face Y=0.1")
    v.check_void(f"Strut bore {bore_id} back",
                 cx, 2.9, cz,
                 f"void near back face Y=2.9")
    inset = 0.3
    v.check_void(f"Strut bore {bore_id} corner +X+Z",
                 cx + half_w - inset, MID_Y_BASE, cz + half_h - inset,
                 f"void near +X+Z corner")
    v.check_void(f"Strut bore {bore_id} corner -X-Z",
                 cx - half_w + inset, MID_Y_BASE, cz - half_h + inset,
                 f"void near -X-Z corner")
    outside_x = cx + half_w + 1.0
    if outside_x < PLATE_W:
        v.check_solid(f"Strut bore {bore_id} wall +X",
                      outside_x, MID_Y_BASE, cz,
                      f"solid outside bore +X edge")
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

# Volume estimate (base half):
#   Base plate lower half: 137.2 x 3 x 34.3 = 14,118 mm^3
#   4 boss halves (solid, half-cyl): pi x 8^2 x 9.08 / 2 x 4 = 3,641 mm^3
#   4 semicircular channels (half-bores, full depth): pi x 4.75^2 x 12.08 / 2 x 4 = 1,716 mm^3
#   2 bottom strut bores: 2 x 6.4 x 6.4 x 3.0 = 246 mm^3
#   Expected ~ 14,118 + 3,641 - 1,716 - 246 = 15,797 mm^3
#   Bounding box: 137.2 x 12.08 x 34.3 = 56,911 mm^3
#   Fill ratio ~ 15,797 / 56,911 ~ 0.278 — within (0.1, 0.8)
envelope_vol = PLATE_W * FULL_DEPTH * BASE_H
v.check_volume(expected_envelope=envelope_vol, fill_range=(0.1, 0.8))
print()

# ---------------------------------------------------------------------------
# Rubric 5 — Bounding Box Reconciliation
# ---------------------------------------------------------------------------

print("=" * 60)
print("RUBRIC 5 — Bounding Box Reconciliation")
print("=" * 60)
print()

bb = plate.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, 0.0,       PLATE_W)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0,       FULL_DEPTH)   # boss halves extend to Y=12.08
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0,       SPLIT_Z)      # base half: Z=0..34.3
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
