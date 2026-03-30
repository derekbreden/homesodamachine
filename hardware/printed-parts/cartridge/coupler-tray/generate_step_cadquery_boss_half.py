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

Rubric 2 — Coordinate System Declaration:
  All coordinates are given in the assembly frame (same as Phase 4):
  Origin: plate bottom-left-front corner (X=0, Y=0, Z=0)
  X: plate width axis — left to right, 0..140.0mm
  Y: plate thickness axis — front face (Y=0) to back face of base (Y=3mm);
     boss halves extend from Y=3 to Y=12.08mm
  Z: plate height axis — bottom to top, assembly Z=34.3..68.6mm for this half
  Bounding envelope of this part: 140.0mm (X) x 12.08mm (Y) x 34.3mm (Z)
    (Z=34.3mm to Z=68.6mm in assembly frame, so part height = 34.3mm)

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
COUPLER TRAY BOSS HALF — Feature Planning Table (Rubric 1)
==========================================================

Assembly frame coordinates (Z=34.3..68.6mm is this half):

  #   Feature Name              Op      Shape         Axis  Center (X,Y,Z)              Dimensions
  1   Base plate body           Add     Rect prism    —     (70.0, 1.5, 51.45)          140.0 x 3 x 34.3 mm
  2   Boss half B1              Add     Half-cyl      Y     (43.1, 7.54, 34.3)          OD 16mm, h 9.08mm, upper half (Z>=34.3)
  3   Boss half B2              Add     Half-cyl      Y     (60.1, 7.54, 34.3)          OD 16mm, h 9.08mm, upper half (Z>=34.3)
  4   Boss half B3              Add     Half-cyl      Y     (77.1, 7.54, 34.3)          OD 16mm, h 9.08mm, upper half (Z>=34.3)
  5   Boss half B4              Add     Half-cyl      Y     (94.1, 7.54, 34.3)          OD 16mm, h 9.08mm, upper half (Z>=34.3)
  6   Semicircular channel C1   Remove  Half-cyl bore Y     (43.1, 6.04, 34.3)          9.5mm dia, upper half bore, TH
  7   Semicircular channel C2   Remove  Half-cyl bore Y     (60.1, 6.04, 34.3)          9.5mm dia, upper half bore, TH
  8   Semicircular channel C3   Remove  Half-cyl bore Y     (77.1, 6.04, 34.3)          9.5mm dia, upper half bore, TH
  9   Semicircular channel C4   Remove  Half-cyl bore Y     (94.1, 6.04, 34.3)          9.5mm dia, upper half bore, TH
  10  Strut bore S-TL           Remove  Rect prism    Y     (4.0, 1.5, 63.6)            6.4 x 3 x 6.4 mm, TH
  11  Strut bore S-TR           Remove  Rect prism    Y     (136.0, 1.5, 63.6)          6.4 x 3 x 6.4 mm, TH

  Implementation: build full Phase 4 tray (Z 0..68.6), then cut bottom half
  (Z=0..34.3+overcut downward) with a large box to produce the boss half.
  Semicircular channels and boss halves are produced automatically.

TH = through-hole, full Y depth
Boss half Y center = (3 + 12.08) / 2 = 7.54mm
Bore Y center = 12.08 / 2 = 6.04mm
Strut bore Y center = 3.0 / 2 = 1.5mm
"""

print(FEATURE_TABLE)

# ---------------------------------------------------------------------------
# Dimensions (from parts.md, unchanged from Phase 4)
# ---------------------------------------------------------------------------

PLATE_W     = 140.0
PLATE_D     = 3.0
PLATE_H     = 68.6
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
    ("H1/B1", 43.1, 34.3),
    ("H2/B2", 60.1, 34.3),
    ("H3/B3", 77.1, 34.3),
    ("H4/B4", 94.1, 34.3),
]

STRUT_BORE_W = 6.4
STRUT_BORE_H = 6.4

# Only top two strut bores are in the boss half
STRUT_BORES_BOSS = [
    ("S-TL",   4.0, 63.6),
    ("S-TR", 136.0, 63.6),
]

MID_Y_BASE  = PLATE_D / 2.0
MID_Y_BOSS  = PLATE_D + BOSS_H / 2.0    # 7.54mm
MID_Y_BORE  = FULL_DEPTH / 2.0
OVERCUT     = 0.1

# Z midpoint of boss half in assembly frame
MID_Z_BOSS_HALF = (SPLIT_Z + PLATE_H) / 2.0   # 51.45mm

# ---------------------------------------------------------------------------
# Build the full Phase 4 tray body, then cut off the bottom half.
# ---------------------------------------------------------------------------

print("Building full Phase 4 tray body (will then cut to boss half)...")
print()

# Feature 1 — Base Plate (full height)
print("Feature 1 — Base plate (140.0 x 3 x 68.6 mm, full height)...")
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

# ---------------------------------------------------------------------------
# Cut the bottom half (Z=0 to Z=SPLIT_Z) to produce the boss half.
# The cut box starts below Z=0 and goes up to Z=SPLIT_Z.
# ---------------------------------------------------------------------------

print(f"Cutting bottom half (Z={-OVERCUT} to Z={SPLIT_Z}) to produce boss half...")
bottom_cut = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(-OVERCUT / 2, -OVERCUT / 2, -OVERCUT))
    .box(PLATE_W + OVERCUT, FULL_DEPTH + OVERCUT, SPLIT_Z + OVERCUT, centered=False)
)
plate = plate.cut(bottom_cut)
print("Boss half produced.")
print()

print("Model construction complete.")
print()

# ---------------------------------------------------------------------------
# Export STEP file
# ---------------------------------------------------------------------------

OUTPUT_STEP = Path(__file__).resolve().parent / "coupler-tray-boss-half-cadquery.step"
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

# --- Feature 1: Base plate body (boss half) ---
print("Feature 1 — Base plate body (Z=34.3..68.6mm):")
v.check_solid("Base plate center boss half",   70.0, MID_Y_BASE, MID_Z_BOSS_HALF,  "solid at base plate center of boss half")
v.check_solid("Base plate near Y=0",           70.0, 0.3,        MID_Z_BOSS_HALF,  "solid near front face Y=0")
v.check_solid("Base plate near Y=3",           70.0, 2.7,        MID_Z_BOSS_HALF,  "solid near back face Y=3")
v.check_solid("Base plate left edge",           0.5, MID_Y_BASE, MID_Z_BOSS_HALF,  "solid near X=0")
v.check_solid("Base plate right edge",        139.5, MID_Y_BASE, MID_Z_BOSS_HALF,  "solid near X=140.0")
v.check_solid("Base plate top edge",           68.6, MID_Y_BASE, 68.1,             "solid near Z=68.6 top")
v.check_solid("Base plate near mating face",   68.6, MID_Y_BASE, 34.6,             "solid just above mating face Z=34.3")
# Verify bottom half is gone — no material below Z=34.3 in body region (away from bosses/holes)
v.check_void("No material below split Z (away from bosses)",
             5.0, MID_Y_BASE, 33.0,
             "void at Z=33mm away from hole centers — bottom half removed")
# Verify no boss material below split
v.check_void("No boss material below split",
             43.1 + BOSS_R_IN + 1.0, MID_Y_BOSS, 33.0,
             "void at Z=33mm in boss wall region — boss cut at split plane")
print()

# --- Features 2-5: Semicircular boss halves ---
for feat_id, hx, hz in HOLES:
    bid = feat_id.split("/")[1]
    print(f"Feature — Semicircular boss half {bid} at X={hx}, Z={hz} (mating face):")

    # Solid in boss wall above split (just above Z=34.3)
    v.check_solid(f"Boss half {bid} wall above split (+X)",
                  hx + BOSS_R_IN + (BOSS_R_OUT - BOSS_R_IN) / 2.0,
                  MID_Y_BOSS, hz + 0.5,
                  f"solid in boss half wall just above split Z={hz+0.5:.1f}")

    # Solid in boss wall well above split
    v.check_solid(f"Boss half {bid} wall mid-height",
                  hx + BOSS_R_IN + (BOSS_R_OUT - BOSS_R_IN) / 2.0,
                  MID_Y_BOSS, hz + 2.0,
                  f"solid in boss wall at Z={hz+2.0:.1f}")

    # Void at boss center above split (inner bore present)
    v.check_void(f"Boss half {bid} inner bore above split",
                 hx, FULL_DEPTH - 0.5, hz + 0.5,
                 f"void at boss center near tip face, Z above split")

    # Void at mating face: boss does NOT extend below split (no boss below Z=34.3)
    v.check_void(f"Boss half {bid} no material below split",
                 hx + BOSS_R_IN + (BOSS_R_OUT - BOSS_R_IN) / 2.0,
                 MID_Y_BOSS, hz - 0.5,
                 f"void below split Z={hz-0.5:.1f} — boss half starts at split plane")

    print()

# --- Features 6-9: Semicircular channels on mating face ---
for feat_id, hx, hz in HOLES:
    hid = feat_id.split("/")[0]
    print(f"Feature — Semicircular channel {hid} at X={hx}, mating face Z={hz}:")

    # Void at bore center just above split (channel is open)
    v.check_void(f"Channel {hid} center above split",
                 hx, MID_Y_BASE, hz + 0.3,
                 f"void at channel center Z={hz+0.3:.1f} — semicircle opens toward mating face")

    # Void near front face at channel location
    v.check_void(f"Channel {hid} near front face",
                 hx, 0.3, hz + 0.3,
                 f"void near Y=0 at channel location")

    # Void in boss inner bore near tip face
    v.check_void(f"Channel {hid} in boss near tip",
                 hx, FULL_DEPTH - 0.3, hz + 0.3,
                 f"void in boss inner bore near tip face")

    # Path continuity: base plate bore meets boss bore at Y=3
    v.check_void(f"Channel {hid} path continuity below Y=3",
                 hx, PLATE_D - 0.1, hz + 0.3,
                 f"void just below Y=3 interface")
    v.check_void(f"Channel {hid} path continuity above Y=3",
                 hx, PLATE_D + 0.1, hz + 0.3,
                 f"void just above Y=3 interface")

    # Solid just outside bore radius in +X (in base plate)
    v.check_solid(f"Channel {hid} solid outside (+X) in base",
                  hx + HOLE_R + 0.5, MID_Y_BASE, hz + 0.3,
                  f"solid outside bore radius at Z just above split")

    # Mating face: channel is open (void) at split plane
    v.check_void(f"Channel {hid} open at mating face",
                 hx, MID_Y_BASE, hz + 0.05,
                 f"void very close to mating face — channel is open at Z={hz:.1f}")

    # No plate below split (away from hole center in X)
    check_x = hx + HOLE_R + 2.0
    if check_x < PLATE_W - 1.0:
        v.check_void(f"Channel {hid} no plate below split",
                     check_x, MID_Y_BASE, hz - 0.3,
                     f"void below split plane — bottom half removed")
    print()

# --- Features 10-11: Top strut bores ---
print("Features 10-11 — Top strut bores (S-TL, S-TR):")
for bore_id, cx, cz in STRUT_BORES_BOSS:
    half_w = STRUT_BORE_W / 2
    half_h = STRUT_BORE_H / 2

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

# Volume estimate (boss half, same as base half by symmetry):
#   Base plate upper half: 140.0 x 3 x 34.3 = 14,406 mm^3
#   4 boss halves (solid, half-cyl): pi x 8^2 x 9.08 / 2 x 4 = 3,641 mm^3
#   4 semicircular channels (half-bores): pi x 4.75^2 x 12.08 / 2 x 4 = 1,716 mm^3
#   2 top strut bores: 2 x 6.4 x 6.4 x 3.0 = 246 mm^3
#   Expected ~ 14,406 + 3,641 - 1,716 - 246 = 16,085 mm^3
#   Bounding box: 140.0 x 12.08 x 34.3 = 58,069 mm^3
#   Fill ratio ~ 16,085 / 58,069 ~ 0.277 — within (0.1, 0.8)
envelope_vol = PLATE_W * FULL_DEPTH * BOSS_H_HALF
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
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0,       FULL_DEPTH)    # boss halves extend to Y=12.08
v.check_bbox("Z", bb.zmin, bb.zmax, SPLIT_Z,   PLATE_H)       # boss half: Z=34.3..68.6
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
