"""
Coupler Tray Split — CadQuery STEP Generation Script
Season 1, Phase 5 — Split coupler tray into two halves

Produces two STEP files:
  coupler-tray-bottom-cadquery.step  — base half (flat front, no bosses)
  coupler-tray-top-cadquery.step     — boss half  (back, retains original bosses)

Specification source:
  hardware/printed-parts/cartridge/coupler-tray/planning/parts.md

JG union geometry:
  hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md

The split is perpendicular to Y (the coupler axis). Every coupler passes through both halves.
Each half provides half the total bore depth needed to capture the coupler center body
(9.31mm OD, 12.16mm long). Plain flat mating faces — no dovetail geometry.

----------------------------------------------------------------------------
Rubric 2 — Coordinate System Declaration
----------------------------------------------------------------------------

SHARED coordinate origin: bottom-left corner of base half outer (front) face.

  X: width axis — left to right, 0..137.2mm
  Y: thickness axis:
       Base half spans  Y=0     (outer front face) to Y=6.04mm  (mating face)
       Boss half spans  Y=6.04  (mating face, = local Y=0)      to Y=18.12mm (boss tip)
       NOTE: each half is modeled with its own local Y=0.
             Base half local Y=0 = outer face   (placed at Y=0   in shared coords)
             Boss half local Y=0 = mating face  (placed at Y=6.04 in shared coords)
  Z: height axis — bottom to top, 0..68.6mm

  Both halves share identical XZ extents: X:[0,137.2] Z:[0,68.6]

  Print orientation:
    Base half — outer face (local XZ, Y=0) down on build plate; Z is print-up.
    Boss half — mating face (local XZ, Y=0) down on build plate; Z is print-up.
    All bores and bosses print as vertical cylinders in both orientations.
"""

import sys
from pathlib import Path

# Add tools/ to sys.path for step_validate import
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq
from step_validate import Validator

# ============================================================================
# Shared Dimensions (from planning/parts.md and original coupler tray parts.md)
# ============================================================================

PLATE_W    = 137.2   # X — width, left to right
PLATE_H    = 68.6    # Z — height, bottom to top

# Coupler bore geometry
HOLE_DIA   = 9.5     # mm — bore diameter (light press-fit on 9.31mm center body)
HOLE_R     = HOLE_DIA / 2.0   # 4.75mm

# Boss geometry (boss half only)
BOSS_OD    = 16.0    # mm — outer diameter of boss cylinder
BOSS_R_OUT = BOSS_OD / 2.0    # 8.0mm
BOSS_R_IN  = HOLE_R            # 4.75mm (inner bore = same as coupler bore)
BOSS_BASE_D = 3.0   # mm — boss half base plate thickness (Y)
BOSS_H      = 9.08  # mm — boss protrusion beyond base plate back face
BOSS_FULL_D = BOSS_BASE_D + BOSS_H  # 12.08mm — boss half total Y (mating face to boss tip)

# Split geometry
# Base half thickness = half the total coupler center body capture depth
# 12.08mm (total capture depth) / 2 = 6.04mm per half
BASE_HALF_D = 6.04  # mm — base half Y thickness (= mating face position in base half coords)

# Coupler bore centers — 1×4 row along X, all at Z=34.3mm, 17mm c-c
# Identical to original coupler tray layout
HOLES = [
    ("H1", 43.1, 34.3),
    ("H2", 60.1, 34.3),
    ("H3", 77.1, 34.3),
    ("H4", 94.1, 34.3),
]

# Strut bore geometry — 6.4×6.4mm rectangular through-bores
# Identical positions to original coupler tray strut bores
STRUT_BORE_W = 6.4  # X dimension
STRUT_BORE_H = 6.4  # Z dimension
STRUT_BORES = [
    ("S-TL", 10.0,  63.6),
    ("S-TR", 127.2, 63.6),
    ("S-BL", 10.0,   5.0),
    ("S-BR", 127.2,  5.0),
]

OVERCUT = 0.1   # mm past exit face for clean boolean cut

# ============================================================================
# Rubric 1 — Feature Planning Table (both parts)
# ============================================================================

FEATURE_TABLE = f"""
COUPLER TRAY SPLIT — Feature Planning Table (Rubric 1)
=======================================================

BASE HALF (coupler-tray-bottom-cadquery.step)
  #   Feature             Op      Shape        Axis  Center(X,Y,Z)           Dimensions
  1   Base plate          Add     Rect prism   —     (68.6, 3.02, 34.3)      137.2×6.04×68.6 mm
  2   Bore BH1            Remove  Cylinder     Y     (43.1, 3.02, 34.3)      9.5mm dia, through
  3   Bore BH2            Remove  Cylinder     Y     (60.1, 3.02, 34.3)      9.5mm dia, through
  4   Bore BH3            Remove  Cylinder     Y     (77.1, 3.02, 34.3)      9.5mm dia, through
  5   Bore BH4            Remove  Cylinder     Y     (94.1, 3.02, 34.3)      9.5mm dia, through
  6   Strut bore S-TL     Remove  Rect prism   Y     (10.0,  3.02, 63.6)     6.4×6.04×6.4 mm, through
  7   Strut bore S-TR     Remove  Rect prism   Y     (127.2, 3.02, 63.6)     6.4×6.04×6.4 mm, through
  8   Strut bore S-BL     Remove  Rect prism   Y     (10.0,  3.02, 5.0)      6.4×6.04×6.4 mm, through
  9   Strut bore S-BR     Remove  Rect prism   Y     (127.2, 3.02, 5.0)      6.4×6.04×6.4 mm, through

  Local Y=0 = outer face (on build plate).
  Local Y={BASE_HALF_D} = mating face (flat, no features).

BOSS HALF (coupler-tray-top-cadquery.step)
  #   Feature             Op      Shape        Axis  Center(X,Y,Z)           Dimensions
  1   Base plate          Add     Rect prism   —     (68.6, 1.5, 34.3)       137.2×3×68.6 mm
  2   Boss TB1            Add     Cylinder     Y     (43.1, 7.54, 34.3)      OD 16mm, h 9.08mm
  3   Boss TB2            Add     Cylinder     Y     (60.1, 7.54, 34.3)      OD 16mm, h 9.08mm
  4   Boss TB3            Add     Cylinder     Y     (77.1, 7.54, 34.3)      OD 16mm, h 9.08mm
  5   Boss TB4            Add     Cylinder     Y     (94.1, 7.54, 34.3)      OD 16mm, h 9.08mm
  6   Bore TH1            Remove  Cylinder     Y     (43.1, 6.04, 34.3)      9.5mm dia, through (Y=0..12.08)
  7   Bore TH2            Remove  Cylinder     Y     (60.1, 6.04, 34.3)      9.5mm dia, through (Y=0..12.08)
  8   Bore TH3            Remove  Cylinder     Y     (77.1, 6.04, 34.3)      9.5mm dia, through (Y=0..12.08)
  9   Bore TH4            Remove  Cylinder     Y     (94.1, 6.04, 34.3)      9.5mm dia, through (Y=0..12.08)
  10  Strut bore TS-TL    Remove  Rect prism   Y     (10.0,  1.5, 63.6)      6.4×3×6.4 mm, through base plate
  11  Strut bore TS-TR    Remove  Rect prism   Y     (127.2, 1.5, 63.6)      6.4×3×6.4 mm, through base plate
  12  Strut bore TS-BL    Remove  Rect prism   Y     (10.0,  1.5, 5.0)       6.4×3×6.4 mm, through base plate
  13  Strut bore TS-BR    Remove  Rect prism   Y     (127.2, 1.5, 5.0)       6.4×3×6.4 mm, through base plate

  Local Y=0 = mating face (flat, on build plate).
  Local Y={BOSS_BASE_D} = back face of base plate / base of bosses.
  Local Y={BOSS_FULL_D} = boss tip face (coupler shoulder bearing surface).

  Boss Y center = ({BOSS_BASE_D} + {BOSS_FULL_D}) / 2 = {(BOSS_BASE_D + BOSS_FULL_D) / 2:.2f}mm
  Bore Y center  = {BOSS_FULL_D} / 2 = {BOSS_FULL_D / 2:.2f}mm
  Strut Y center = {BOSS_BASE_D} / 2 = {BOSS_BASE_D / 2:.2f}mm

Notes:
  - Strut bores in boss half only penetrate the 3mm base plate (Y=0..3mm).
    Beyond Y=3mm the boss material is only at boss XZ positions; strut bore
    corners are at X=10.0/127.2 and Z=5.0/63.6 — far from bosses at Z=34.3.
  - Boss half bounding envelope: 137.2 × 12.08 × 68.6 mm
  - Base half bounding envelope: 137.2 × 6.04 × 68.6 mm
"""

print(FEATURE_TABLE)

# ============================================================================
# ============================================================================
#  PART 1 — BASE HALF
# ============================================================================
# ============================================================================

print("=" * 60)
print("BUILDING BASE HALF (coupler-tray-bottom-cadquery.step)")
print("=" * 60)
print()

MID_Y_BASE_HALF = BASE_HALF_D / 2.0   # 3.02mm — mid-depth of base half

# ---------------------------------------------------------------------------
# Feature 1 — Base plate body
# Box with corner at origin: X:[0,137.2] Y:[0,6.04] Z:[0,68.6]
# ---------------------------------------------------------------------------

print(f"Feature 1 — Base plate body ({PLATE_W}×{BASE_HALF_D}×{PLATE_H} mm)...")
base_half = (
    cq.Workplane("XY")
    .box(PLATE_W, BASE_HALF_D, PLATE_H, centered=False)
)

# ---------------------------------------------------------------------------
# Features 2–5 — Coupler through-bores (4×, 9.5mm dia)
#
# XZ workplane normal is -Y. workplane(offset=0) places sketch at Y=0.
# extrude(-(BASE_HALF_D + OVERCUT)) goes +Y: cuts Y=0 to Y=6.14mm (full through).
# ---------------------------------------------------------------------------

print(f"Features 2-5 — 4× coupler bores ({HOLE_DIA}mm dia, Y=0..{BASE_HALF_D}mm)...")
for bore_id, hx, hz in HOLES:
    print(f"  [-] Bore {bore_id} at X={hx}, Z={hz}")
    bore = (
        cq.Workplane("XZ")
        .workplane(offset=0)            # sketch plane at Y=0 (outer front face)
        .center(hx, hz)
        .circle(HOLE_R)
        .extrude(-(BASE_HALF_D + OVERCUT))  # +Y direction (XZ normal is -Y)
    )
    base_half = base_half.cut(bore)

print("Coupler bores complete.")
print()

# ---------------------------------------------------------------------------
# Features 6–9 — Strut bores (4×, 6.4×6.4mm rectangular, through Y)
#
# Each bore: box with corner at (cx - half_w, -overcut/2, cz - half_h),
# dimensions (STRUT_BORE_W, BASE_HALF_D + OVERCUT, STRUT_BORE_H).
# ---------------------------------------------------------------------------

print(f"Features 6-9 — 4× strut bores ({STRUT_BORE_W}×{STRUT_BORE_H}mm, Y=0..{BASE_HALF_D}mm)...")
for bore_id, cx, cz in STRUT_BORES:
    x0 = cx - STRUT_BORE_W / 2
    z0 = cz - STRUT_BORE_H / 2
    bore_box = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(x0, -OVERCUT / 2, z0))
        .box(STRUT_BORE_W, BASE_HALF_D + OVERCUT, STRUT_BORE_H, centered=False)
    )
    base_half = base_half.cut(bore_box)
    print(f"  [-] Strut bore {bore_id} at X={cx}, Z={cz} "
          f"(rect {STRUT_BORE_W}×{STRUT_BORE_H} mm)")

print("Base half construction complete.")
print()

# ---------------------------------------------------------------------------
# Export base half STEP
# ---------------------------------------------------------------------------

OUTPUT_BASE = Path(__file__).resolve().parent / "coupler-tray-bottom-cadquery.step"
print(f"Exporting base half STEP -> {OUTPUT_BASE}")
cq.exporters.export(base_half, str(OUTPUT_BASE))
print("Base half export complete.")
print()

# ---------------------------------------------------------------------------
# Rubric 3 — Base half Feature-Specification Reconciliation
# ---------------------------------------------------------------------------

print("=" * 60)
print("RUBRIC 3 — BASE HALF Feature-Specification Reconciliation")
print("=" * 60)
print()

vb = Validator(base_half)

# Feature 1 — Base plate body
print("Feature 1 — Base plate body:")
vb.check_solid("Plate center",       68.6, MID_Y_BASE_HALF, 34.3, "solid at geometric center")
vb.check_solid("Plate near Y=0",     68.6, 0.2,             34.3, "solid near outer face")
vb.check_solid("Plate near Y=mating",68.6, BASE_HALF_D-0.2, 34.3, "solid near mating face")
vb.check_solid("Plate left edge",    0.5,  MID_Y_BASE_HALF,  34.3, "solid near X=0")
vb.check_solid("Plate right edge",   136.7,MID_Y_BASE_HALF,  34.3, "solid near X=137.2")
vb.check_solid("Plate bottom edge",  68.6, MID_Y_BASE_HALF,  0.5,  "solid near Z=0")
vb.check_solid("Plate top edge",     68.6, MID_Y_BASE_HALF,  68.1, "solid near Z=68.6")
# Verify mating face is at correct Y (void just beyond mating face)
vb.check_void("No material beyond mating face",
              68.6, BASE_HALF_D + 0.5, 34.3,
              f"void at Y={BASE_HALF_D + 0.5}mm — plate ends at mating face")
print()

# Features 2–5 — Coupler through-bores
for bore_id, hx, hz in HOLES:
    print(f"Feature — Coupler bore {bore_id} at X={hx}, Z={hz}:")
    # Void at bore center, mid-depth
    vb.check_void(f"Bore {bore_id} center",
                  hx, MID_Y_BASE_HALF, hz,
                  f"void at bore center ({hx}, {MID_Y_BASE_HALF:.2f}, {hz})")
    # Void near outer face (Y=0 side)
    vb.check_void(f"Bore {bore_id} near outer face",
                  hx, 0.2, hz,
                  "void near outer face Y=0.2")
    # Void near mating face
    vb.check_void(f"Bore {bore_id} near mating face",
                  hx, BASE_HALF_D - 0.2, hz,
                  f"void near mating face Y={BASE_HALF_D - 0.2:.2f}")
    # Solid just outside bore radius (+X)
    vb.check_solid(f"Bore {bore_id} wall +X",
                   hx + HOLE_R + 0.5, MID_Y_BASE_HALF, hz,
                   f"solid outside bore radius at X={hx + HOLE_R + 0.5:.2f}")
    print()

# Features 6–9 — Strut bores
print("Features 6-9 — Strut bores (base half):")
for bore_id, cx, cz in STRUT_BORES:
    half_w = STRUT_BORE_W / 2   # 3.2
    half_h = STRUT_BORE_H / 2   # 3.2
    inset = 0.3
    # Void at bore center
    vb.check_void(f"Strut bore {bore_id} center",
                  cx, MID_Y_BASE_HALF, cz,
                  f"void at bore center ({cx}, {MID_Y_BASE_HALF:.2f}, {cz})")
    # Void near outer face
    vb.check_void(f"Strut bore {bore_id} outer face",
                  cx, 0.1, cz,
                  "void near outer face Y=0.1")
    # Void near mating face
    vb.check_void(f"Strut bore {bore_id} mating face",
                  cx, BASE_HALF_D - 0.1, cz,
                  f"void near mating face Y={BASE_HALF_D - 0.1:.2f}")
    # Void at bore corners (checks rectangular extent)
    vb.check_void(f"Strut bore {bore_id} corner +X+Z",
                  cx + half_w - inset, MID_Y_BASE_HALF, cz + half_h - inset,
                  "void near +X+Z corner")
    vb.check_void(f"Strut bore {bore_id} corner -X-Z",
                  cx - half_w + inset, MID_Y_BASE_HALF, cz - half_h + inset,
                  "void near -X-Z corner")
    # Solid outside bore in +X direction (if room)
    outside_x = cx + half_w + 1.0
    if outside_x < PLATE_W:
        vb.check_solid(f"Strut bore {bore_id} wall +X",
                       outside_x, MID_Y_BASE_HALF, cz,
                       f"solid outside bore +X at X={outside_x:.1f}")
    outside_x_neg = cx - half_w - 1.0
    if outside_x_neg > 0:
        vb.check_solid(f"Strut bore {bore_id} wall -X",
                       outside_x_neg, MID_Y_BASE_HALF, cz,
                       f"solid outside bore -X at X={outside_x_neg:.1f}")
print()

# Rubric 4 — Solid validity
print("=" * 60)
print("RUBRIC 4 — BASE HALF Solid Validity")
print("=" * 60)
print()
vb.check_valid()
vb.check_single_body()
# Volume estimate:
#   Base plate:    137.2 × 6.04 × 68.6  = 56,820 mm³
#   4 coupler bores: π × 4.75² × 6.04 × 4 = 1,710 mm³
#   4 strut bores:   6.4 × 6.4 × 6.04 × 4 = 990 mm³
#   Expected ≈ 56,820 − 1,710 − 990 = 54,120 mm³
#   Envelope: 137.2 × 6.04 × 68.6 = 56,820 mm³
#   Fill ratio ≈ 54,120 / 56,820 ≈ 0.95
envelope_vol_base = PLATE_W * BASE_HALF_D * PLATE_H
vb.check_volume(expected_envelope=envelope_vol_base, fill_range=(0.85, 1.0))
print()

# Rubric 5 — Bounding box
print("=" * 60)
print("RUBRIC 5 — BASE HALF Bounding Box Reconciliation")
print("=" * 60)
print()
bb_base = base_half.val().BoundingBox()
vb.check_bbox("X", bb_base.xmin, bb_base.xmax, 0.0,         PLATE_W)
vb.check_bbox("Y", bb_base.ymin, bb_base.ymax, 0.0,         BASE_HALF_D)
vb.check_bbox("Z", bb_base.zmin, bb_base.zmax, 0.0,         PLATE_H)
print()

if not vb.summary():
    print()
    print("BASE HALF FAILURES — fix before continuing.")
    sys.exit(1)

print()
print(f"Base half STEP written: {OUTPUT_BASE}")
print()

# ============================================================================
# ============================================================================
#  PART 2 — BOSS HALF
# ============================================================================
# ============================================================================

print("=" * 60)
print("BUILDING BOSS HALF (coupler-tray-top-cadquery.step)")
print("=" * 60)
print()

MID_Y_BOSS_PLATE = BOSS_BASE_D / 2.0        # 1.5mm — mid-depth of base plate
MID_Y_BOSS_BODY  = BOSS_BASE_D + BOSS_H / 2.0   # 7.54mm — mid-height of boss
MID_Y_BORE       = BOSS_FULL_D / 2.0         # 6.04mm — mid of full boss-half bore

# ---------------------------------------------------------------------------
# Feature 1 — Base plate body
# Box with corner at origin: X:[0,137.2] Y:[0,3.0] Z:[0,68.6]
# Y=0 is the mating face (flat, placed face-down on build plate).
# ---------------------------------------------------------------------------

print(f"Feature 1 — Boss half base plate ({PLATE_W}×{BOSS_BASE_D}×{PLATE_H} mm)...")
boss_half = (
    cq.Workplane("XY")
    .box(PLATE_W, BOSS_BASE_D, PLATE_H, centered=False)
)

# ---------------------------------------------------------------------------
# Features 2–5 — Bosses (4× solid cylinders, from back face to boss tip)
#
# XZ workplane normal is -Y. workplane(offset=-BOSS_BASE_D) places sketch at
# Y=BOSS_BASE_D (back face of base plate). extrude(-BOSS_H) goes +Y,
# adding the boss from Y=3mm to Y=12.08mm.
# ---------------------------------------------------------------------------

print(f"Features 2-5 — 4× bosses (OD={BOSS_OD}mm, h={BOSS_H}mm, Y={BOSS_BASE_D}..{BOSS_FULL_D}mm)...")
for feat_id, hx, hz in HOLES:
    print(f"  [+] Boss at X={hx}, Z={hz}")
    boss = (
        cq.Workplane("XZ")
        .workplane(offset=-BOSS_BASE_D)     # sketch plane at Y=BOSS_BASE_D (back face)
        .center(hx, hz)
        .circle(BOSS_R_OUT)
        .extrude(-BOSS_H)                   # +Y direction: Y=3mm -> Y=12.08mm
    )
    boss_half = boss_half.union(boss)

print("Bosses complete.")
print()

# ---------------------------------------------------------------------------
# Features 6–9 — Through-bores (4×, 9.5mm dia, Y=0..12.08mm continuous)
#
# Single cut from Y=0 (mating face) through the full boss depth to boss tip.
# XZ workplane normal is -Y. workplane(offset=0) places sketch at Y=0.
# extrude(-(BOSS_FULL_D + OVERCUT)) goes +Y: Y=0 to Y=12.18mm.
# ---------------------------------------------------------------------------

print(f"Features 6-9 — 4× through-bores ({HOLE_DIA}mm dia, Y=0..{BOSS_FULL_D}mm)...")
for bore_id, hx, hz in HOLES:
    print(f"  [-] Bore {bore_id} at X={hx}, Z={hz}")
    bore = (
        cq.Workplane("XZ")
        .workplane(offset=0)                # sketch plane at Y=0 (mating face)
        .center(hx, hz)
        .circle(HOLE_R)
        .extrude(-(BOSS_FULL_D + OVERCUT))  # +Y direction: Y=0 -> Y=12.18mm
    )
    boss_half = boss_half.cut(bore)

print("Boss half coupler bores complete.")
print()

# ---------------------------------------------------------------------------
# Features 10–13 — Strut bores (4×, 6.4×6.4mm, through base plate only Y=0..3mm)
#
# Strut bores are at plate corners (X=10.0/127.2, Z=5.0/63.6), well away from
# boss positions (Z=34.3mm). No boss material exists in the strut bore region —
# bores only need to cut through the 3mm base plate.
# ---------------------------------------------------------------------------

print(f"Features 10-13 — 4× strut bores ({STRUT_BORE_W}×{STRUT_BORE_H}mm, Y=0..{BOSS_BASE_D}mm)...")
for bore_id, cx, cz in STRUT_BORES:
    x0 = cx - STRUT_BORE_W / 2
    z0 = cz - STRUT_BORE_H / 2
    bore_box = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(x0, -OVERCUT / 2, z0))
        .box(STRUT_BORE_W, BOSS_BASE_D + OVERCUT, STRUT_BORE_H, centered=False)
    )
    boss_half = boss_half.cut(bore_box)
    print(f"  [-] Strut bore {bore_id} at X={cx}, Z={cz} "
          f"(rect {STRUT_BORE_W}×{STRUT_BORE_H} mm, base plate only)")

print("Boss half construction complete.")
print()

# ---------------------------------------------------------------------------
# Export boss half STEP
# ---------------------------------------------------------------------------

OUTPUT_BOSS = Path(__file__).resolve().parent / "coupler-tray-top-cadquery.step"
print(f"Exporting boss half STEP -> {OUTPUT_BOSS}")
cq.exporters.export(boss_half, str(OUTPUT_BOSS))
print("Boss half export complete.")
print()

# ---------------------------------------------------------------------------
# Rubric 3 — Boss half Feature-Specification Reconciliation
# ---------------------------------------------------------------------------

print("=" * 60)
print("RUBRIC 3 — BOSS HALF Feature-Specification Reconciliation")
print("=" * 60)
print()

vt = Validator(boss_half)

# Feature 1 — Base plate body
print("Feature 1 — Boss half base plate:")
vt.check_solid("Plate center",          68.6, MID_Y_BOSS_PLATE, 34.3, "solid at base plate center")
vt.check_solid("Plate near Y=0 (mating face)", 68.6, 0.2,       34.3, "solid near mating face Y=0")
vt.check_solid("Plate near Y=3 (back face)", 68.6, BOSS_BASE_D - 0.2, 34.3, "solid near back face Y=3")
vt.check_solid("Plate left edge",       0.5,  MID_Y_BOSS_PLATE, 34.3, "solid near X=0")
vt.check_solid("Plate right edge",      136.7,MID_Y_BOSS_PLATE, 34.3, "solid near X=137.2")
vt.check_solid("Plate bottom edge",     68.6, MID_Y_BOSS_PLATE, 0.5,  "solid near Z=0")
vt.check_solid("Plate top edge",        68.6, MID_Y_BOSS_PLATE, 68.1, "solid near Z=68.6")
# Verify no plate material beyond Y=3 in non-boss region
vt.check_void("No plate beyond Y=3 (non-boss region)",
              5.0, BOSS_BASE_D + 1.0, 5.0,
              f"void at Y={BOSS_BASE_D + 1.0}mm near corner — base plate only 3mm, no boss here")
print()

# Features 2–5 — Bosses
for feat_id, hx, hz in HOLES:
    bid = feat_id
    print(f"Feature — Boss {bid} at X={hx}, Z={hz}:")
    # Solid in boss wall mid-height
    vt.check_solid(f"Boss {bid} wall mid-height",
                   hx + BOSS_R_IN + (BOSS_R_OUT - BOSS_R_IN) / 2.0,
                   MID_Y_BOSS_BODY, hz,
                   f"solid in boss wall at Y={MID_Y_BOSS_BODY:.2f} (mid-boss height)")
    # Solid in boss wall near base (just above plate back face)
    vt.check_solid(f"Boss {bid} wall near base",
                   hx + BOSS_R_IN + 1.0, BOSS_BASE_D + 0.5, hz,
                   f"solid in boss wall just above Y={BOSS_BASE_D}")
    # Solid in boss wall near tip face
    vt.check_solid(f"Boss {bid} wall near tip",
                   hx + BOSS_R_IN + 1.0, BOSS_FULL_D - 0.3, hz,
                   f"solid in boss wall near tip face Y={BOSS_FULL_D - 0.3:.2f}")
    # Void at boss inner bore (center) mid-boss height — bore runs through boss
    vt.check_void(f"Boss {bid} inner bore mid-height",
                  hx, MID_Y_BOSS_BODY, hz,
                  f"void at boss center (bore) at Y={MID_Y_BOSS_BODY:.2f}")
    # Void outside boss OD (+X) at mid-boss height — confirms boss boundary
    vt.check_void(f"Boss {bid} void beyond OD +X",
                  hx + BOSS_R_OUT + 1.0, MID_Y_BOSS_BODY, hz,
                  f"void outside boss OD in +X at Y={MID_Y_BOSS_BODY:.2f}")
    print()

# Features 6–9 — Coupler through-bores
for bore_id, hx, hz in HOLES:
    print(f"Feature — Coupler bore {bore_id} at X={hx}, Z={hz}:")
    # Void at center, mid-bore
    vt.check_void(f"Bore {bore_id} center mid-bore",
                  hx, MID_Y_BORE, hz,
                  f"void at ({hx}, {MID_Y_BORE:.2f}, {hz}) — bore mid-depth")
    # Void near mating face (Y=0)
    vt.check_void(f"Bore {bore_id} near mating face",
                  hx, 0.2, hz,
                  "void near mating face Y=0.2")
    # Void near boss tip face
    vt.check_void(f"Bore {bore_id} near boss tip face",
                  hx, BOSS_FULL_D - 0.3, hz,
                  f"void near boss tip face Y={BOSS_FULL_D - 0.3:.2f}")
    # Path continuity: void just below and just above base plate / boss interface
    vt.check_void(f"Bore {bore_id} path below Y=3",
                  hx, BOSS_BASE_D - 0.1, hz,
                  f"void just below Y={BOSS_BASE_D} — bore reaches base/boss interface")
    vt.check_void(f"Bore {bore_id} path above Y=3",
                  hx, BOSS_BASE_D + 0.1, hz,
                  f"void just above Y={BOSS_BASE_D} — bore continues into boss")
    # Solid just outside bore radius (+X) in base plate zone
    vt.check_solid(f"Bore {bore_id} wall +X in base plate",
                   hx + HOLE_R + 0.5, MID_Y_BOSS_PLATE, hz,
                   f"solid outside bore at ({hx + HOLE_R + 0.5:.2f}, {MID_Y_BOSS_PLATE:.2f}, {hz})")
    # Solid just outside bore radius (+X) in boss wall zone
    vt.check_solid(f"Bore {bore_id} wall +X in boss",
                   hx + HOLE_R + 0.5, MID_Y_BOSS_BODY, hz,
                   f"solid in boss wall outside bore at Y={MID_Y_BOSS_BODY:.2f}")
    print()

# Features 10–13 — Strut bores
print("Features 10-13 — Strut bores (boss half):")
for bore_id, cx, cz in STRUT_BORES:
    half_w = STRUT_BORE_W / 2   # 3.2
    half_h = STRUT_BORE_H / 2   # 3.2
    inset = 0.3
    # Void at bore center, in base plate
    vt.check_void(f"Strut bore {bore_id} center",
                  cx, MID_Y_BOSS_PLATE, cz,
                  f"void at bore center ({cx}, {MID_Y_BOSS_PLATE}, {cz}) — in base plate")
    # Void near mating face
    vt.check_void(f"Strut bore {bore_id} mating face",
                  cx, 0.1, cz,
                  "void near mating face Y=0.1")
    # Void near plate back face
    vt.check_void(f"Strut bore {bore_id} plate back face",
                  cx, BOSS_BASE_D - 0.1, cz,
                  f"void near plate back face Y={BOSS_BASE_D - 0.1:.1f}")
    # Void at bore corners
    vt.check_void(f"Strut bore {bore_id} corner +X+Z",
                  cx + half_w - inset, MID_Y_BOSS_PLATE, cz + half_h - inset,
                  "void near +X+Z corner of bore")
    vt.check_void(f"Strut bore {bore_id} corner -X-Z",
                  cx - half_w + inset, MID_Y_BOSS_PLATE, cz - half_h + inset,
                  "void near -X-Z corner of bore")
    # Solid outside bore in +X direction (if room)
    outside_x = cx + half_w + 1.0
    if outside_x < PLATE_W:
        vt.check_solid(f"Strut bore {bore_id} wall +X",
                       outside_x, MID_Y_BOSS_PLATE, cz,
                       f"solid outside bore +X at X={outside_x:.1f}")
    outside_x_neg = cx - half_w - 1.0
    if outside_x_neg > 0:
        vt.check_solid(f"Strut bore {bore_id} wall -X",
                       outside_x_neg, MID_Y_BOSS_PLATE, cz,
                       f"solid outside bore -X at X={outside_x_neg:.1f}")
    # Confirm no boss material at strut bore XZ position above base plate
    vt.check_void(f"Strut bore {bore_id} no boss beyond plate",
                  cx, BOSS_BASE_D + 1.0, cz,
                  f"void at Y={BOSS_BASE_D + 1.0}mm at strut position — no boss material here")
print()

# Rubric 4 — Solid validity
print("=" * 60)
print("RUBRIC 4 — BOSS HALF Solid Validity")
print("=" * 60)
print()
vt.check_valid()
vt.check_single_body()
# Volume estimate:
#   Base plate:           137.2 × 3 × 68.6  = 28,235 mm³
#   4 bosses (solid):     π × 8² × 9.08 × 4 = 7,282 mm³
#   4 coupler bores (full depth): π × 4.75² × 12.08 × 4 = 3,431 mm³
#   4 strut bores:        6.4 × 6.4 × 3.0 × 4 = 491 mm³
#   Expected ≈ 28,235 + 7,282 − 3,431 − 491 = 31,595 mm³
#   Envelope: 137.2 × 12.08 × 68.6 = 113,822 mm³
#   Fill ratio ≈ 31,595 / 113,822 ≈ 0.278
envelope_vol_boss = PLATE_W * BOSS_FULL_D * PLATE_H
vt.check_volume(expected_envelope=envelope_vol_boss, fill_range=(0.1, 0.8))
print()

# Rubric 5 — Bounding box
print("=" * 60)
print("RUBRIC 5 — BOSS HALF Bounding Box Reconciliation")
print("=" * 60)
print()
bb_boss = boss_half.val().BoundingBox()
vt.check_bbox("X", bb_boss.xmin, bb_boss.xmax, 0.0,        PLATE_W)
vt.check_bbox("Y", bb_boss.ymin, bb_boss.ymax, 0.0,        BOSS_FULL_D)  # bosses extend to 12.08
vt.check_bbox("Z", bb_boss.zmin, bb_boss.zmax, 0.0,        PLATE_H)
print()

if not vt.summary():
    print()
    print("BOSS HALF FAILURES — fix before continuing.")
    sys.exit(1)

print()
print(f"Boss half STEP written: {OUTPUT_BOSS}")
print()
print("=" * 60)
print("ALL DONE")
print(f"  Base half: {OUTPUT_BASE}")
print(f"  Boss half: {OUTPUT_BOSS}")
print("=" * 60)
