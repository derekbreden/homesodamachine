"""
Coupler Tray (Split) — CadQuery STEP Generation Script
Split coupler tray into two halves at X=68.6mm (plate midpoint).

Specification source: hardware/printed-parts/cartridge/coupler-tray/planning/parts.md

Rubric 2 — Coordinate System Declaration:
  Origin: plate bottom-left-front corner (X=0, Y=0, Z=0)
  X: plate width axis — left to right, 0..137.2mm, split at X=68.6mm
  Y: plate thickness axis — front face (Y=0) to back face of base (Y=3mm);
     bosses extend from Y=3 to Y=12.08mm
  Z: plate height axis — bottom to top, 0..68.6mm
  Bounding envelope (full): 137.2mm (X) x 12.08mm (Y) x 68.6mm (Z)
  Left half:  X:[0, 68.6]     Y:[0, 12.08]  Z:[0, 68.6]
  Right half: X:[68.6, 137.2] Y:[0, 12.08]  Z:[0, 68.6]

  Split line: X=68.6mm — between H2 (X=60.1) and H3 (X=77.1)
  Mating faces: flat, no dovetail geometry.

  Hole/boss axes are parallel to Y.
  Print orientation: Y=0 face down on build plate.
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
COUPLER TRAY (SPLIT) — Feature Planning Table (Rubric 1)
==========================================================

LEFT HALF (X: 0 to 68.6mm)
  #   Feature Name              Op      Shape         Axis  Center (X,Y,Z)          Dimensions
  L1  Base plate (left)         Add     Rect prism    —     (34.3, 1.5, 34.3)       68.6x3x68.6 mm
  L2  Boss B1                   Add     Cylinder      Y     (43.1, 7.54, 34.3)      OD 16mm, h 9.08
  L3  Boss B2                   Add     Cylinder      Y     (60.1, 7.54, 34.3)      OD 16mm, h 9.08
  L4  Bore H1                   Remove  Cylinder      Y     (43.1, 6.04, 34.3)      9.5mm dia, TH
  L5  Bore H2                   Remove  Cylinder      Y     (60.1, 6.04, 34.3)      9.5mm dia, TH
  L6  Strut bore S-TL           Remove  Rect prism    Y     (10.0, 1.5, 63.6)       6.4x3x6.4 mm, TH
  L7  Strut bore S-BL           Remove  Rect prism    Y     (10.0, 1.5, 5.0)        6.4x3x6.4 mm, TH

RIGHT HALF (X: 68.6 to 137.2mm)
  #   Feature Name              Op      Shape         Axis  Center (X,Y,Z)          Dimensions
  R1  Base plate (right)        Add     Rect prism    —     (102.9, 1.5, 34.3)      68.6x3x68.6 mm
  R2  Boss B3                   Add     Cylinder      Y     (77.1, 7.54, 34.3)      OD 16mm, h 9.08
  R3  Boss B4                   Add     Cylinder      Y     (94.1, 7.54, 34.3)      OD 16mm, h 9.08
  R4  Bore H3                   Remove  Cylinder      Y     (77.1, 6.04, 34.3)      9.5mm dia, TH
  R5  Bore H4                   Remove  Cylinder      Y     (94.1, 6.04, 34.3)      9.5mm dia, TH
  R6  Strut bore S-TR           Remove  Rect prism    Y     (127.2, 1.5, 63.6)      6.4x3x6.4 mm, TH
  R7  Strut bore S-BR           Remove  Rect prism    Y     (127.2, 1.5, 5.0)       6.4x3x6.4 mm, TH

TH = through-hole, full Y depth
Split at X=68.6mm — flat mating faces, no dovetail.
"""

print(FEATURE_TABLE)

# ---------------------------------------------------------------------------
# Dimensions (from parts.md)
# ---------------------------------------------------------------------------

# Full plate envelope
PLATE_W   = 137.2   # X — full width
PLATE_D   = 3.0     # Y — base plate thickness
PLATE_H   = 68.6    # Z — height

# Split position
SPLIT_X   = 68.6    # X coordinate of split — plate midpoint

# Boss geometry
BOSS_OD     = 16.0
BOSS_R_OUT  = BOSS_OD / 2.0    # 8.0mm
BOSS_ID     = 9.5
BOSS_R_IN   = BOSS_ID / 2.0    # 4.75mm
FULL_DEPTH  = 12.08            # base plate + boss height
BOSS_H      = FULL_DEPTH - PLATE_D   # 9.08mm

# Coupler capture bore
HOLE_DIA = 9.5
HOLE_R   = HOLE_DIA / 2.0     # 4.75mm

# Hole/boss centers (X, Z)
HOLES_LEFT = [
    ("H1/B1", 43.1, 34.3),
    ("H2/B2", 60.1, 34.3),
]
HOLES_RIGHT = [
    ("H3/B3", 77.1, 34.3),
    ("H4/B4", 94.1, 34.3),
]

# Strut bore parameters
STRUT_SIZE = 6.0
BORE_CLEARANCE = 0.4
STRUT_BORE_W = STRUT_SIZE + BORE_CLEARANCE  # 6.4mm
STRUT_BORE_H = STRUT_SIZE + BORE_CLEARANCE  # 6.4mm

STRUT_BORES_LEFT = [
    ("S-TL", 10.0, 63.6),
    ("S-BL", 10.0,  5.0),
]
STRUT_BORES_RIGHT = [
    ("S-TR", 127.2, 63.6),
    ("S-BR", 127.2,  5.0),
]

MID_Y_BASE  = PLATE_D / 2.0              # 1.5mm
MID_Y_BOSS  = PLATE_D + BOSS_H / 2.0     # 7.54mm
MID_Y_BORE  = FULL_DEPTH / 2.0           # 6.04mm

OVERCUT = 0.1


# ---------------------------------------------------------------------------
# Helper: build one half of the coupler tray
# ---------------------------------------------------------------------------

def build_half(label, x_start, x_end, holes, strut_bores):
    """Build one half of the coupler tray.

    Args:
        label: "left" or "right"
        x_start: X coordinate of the starting edge
        x_end: X coordinate of the ending edge
        holes: list of (name, x, z) for coupler holes/bosses in this half
        strut_bores: list of (name, x, z) for strut bores in this half
    """
    half_w = x_end - x_start

    print(f"Building {label} half — base plate ({half_w} x {PLATE_D} x {PLATE_H} mm)...")

    # Feature: Base plate
    plate = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(x_start, 0, 0))
        .box(half_w, PLATE_D, PLATE_H, centered=False)
    )

    # Features: Bosses (solid cylinders on back face)
    for feat_id, hx, hz in holes:
        print(f"  Adding boss {feat_id} at X={hx}, Z={hz}")
        boss = (
            cq.Workplane("XZ")
            .workplane(offset=-PLATE_D)
            .center(hx, hz)
            .circle(BOSS_R_OUT)
            .extrude(-BOSS_H)   # +Y direction: Y=3 -> Y=12.08
        )
        plate = plate.union(boss)

    # Features: Through-bores (coupler capture holes)
    for feat_id, hx, hz in holes:
        print(f"  Cutting bore {feat_id} at X={hx}, Z={hz}")
        bore = (
            cq.Workplane("XZ")
            .workplane(offset=0)
            .center(hx, hz)
            .circle(HOLE_R)
            .extrude(-(FULL_DEPTH + OVERCUT))   # +Y direction: Y=0 -> Y=12.18
        )
        plate = plate.cut(bore)

    # Features: Strut bores (rectangular through-holes in base plate)
    for bore_id, cx, cz in strut_bores:
        x0 = cx - STRUT_BORE_W / 2
        z0 = cz - STRUT_BORE_H / 2
        bore_box = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(x0, -OVERCUT / 2, z0))
            .box(STRUT_BORE_W, PLATE_D + OVERCUT, STRUT_BORE_H, centered=False)
        )
        plate = plate.cut(bore_box)
        print(f"  Cutting strut bore {bore_id} at X={cx}, Z={cz}")

    print(f"{label.capitalize()} half complete.")
    print()
    return plate


# ---------------------------------------------------------------------------
# Build both halves
# ---------------------------------------------------------------------------

left_half = build_half("left", 0.0, SPLIT_X, HOLES_LEFT, STRUT_BORES_LEFT)
right_half = build_half("right", SPLIT_X, PLATE_W, HOLES_RIGHT, STRUT_BORES_RIGHT)

# ---------------------------------------------------------------------------
# Export STEP files
# ---------------------------------------------------------------------------

OUTPUT_DIR = Path(__file__).resolve().parent
LEFT_STEP  = OUTPUT_DIR / "coupler-tray-left-cadquery.step"
RIGHT_STEP = OUTPUT_DIR / "coupler-tray-right-cadquery.step"

print(f"Exporting left half  -> {LEFT_STEP}")
cq.exporters.export(left_half, str(LEFT_STEP))
print(f"Exporting right half -> {RIGHT_STEP}")
cq.exporters.export(right_half, str(RIGHT_STEP))
print("Export complete.")
print()

# ---------------------------------------------------------------------------
# Rubric 3 — Feature-Specification Reconciliation
# ---------------------------------------------------------------------------

print("=" * 60)
print("RUBRIC 3 — Feature-Specification Reconciliation")
print("=" * 60)
print()

# --- LEFT HALF ---
print("--- LEFT HALF ---")
print()

vl = Validator(left_half)

# L1: Base plate (left)
print("Feature L1 — Base plate (left):")
vl.check_solid("L-plate center",         34.3, MID_Y_BASE, 34.3,  "solid at left plate center")
vl.check_solid("L-plate near X=0",       0.5,  MID_Y_BASE, 34.3,  "solid near left edge")
vl.check_solid("L-plate near X=68.6",    68.1, MID_Y_BASE, 34.3,  "solid near split face")
vl.check_solid("L-plate near Z=0",       34.3, MID_Y_BASE, 0.5,   "solid near bottom edge")
vl.check_solid("L-plate near Z=68.6",    34.3, MID_Y_BASE, 68.1,  "solid near top edge")
vl.check_void("L-plate void beyond X=68.6",
              69.0, MID_Y_BASE, 34.3,
              "void beyond split face — left half does not extend past X=68.6")
print()

# L2, L3: Bosses B1, B2
for feat_id, hx, hz in HOLES_LEFT:
    bid = feat_id.split("/")[1]
    print(f"Feature — Boss {bid} at X={hx}, Z={hz}:")
    vl.check_solid(f"Boss {bid} wall mid-height",
                   hx + BOSS_R_IN + (BOSS_R_OUT - BOSS_R_IN) / 2.0,
                   MID_Y_BOSS, hz,
                   f"solid in boss wall at mid-height Y={MID_Y_BOSS:.2f}")
    vl.check_solid(f"Boss {bid} wall near base",
                   hx + BOSS_R_IN + 1.0, PLATE_D + 0.5, hz,
                   f"solid in boss wall just above back face")
    vl.check_solid(f"Boss {bid} wall near tip",
                   hx + BOSS_R_IN + 1.0, FULL_DEPTH - 0.3, hz,
                   f"solid in boss wall near tip face")
    vl.check_void(f"Boss {bid} inner bore near tip",
                  hx, FULL_DEPTH - 0.5, hz,
                  f"void at boss center near tip — bore passes through")
    vl.check_void(f"Boss {bid} void beyond OD",
                  hx + BOSS_R_OUT + 1.0, MID_Y_BOSS, hz,
                  f"void outside boss OD radius")
    print()

# L4, L5: Bores H1, H2
for feat_id, hx, hz in HOLES_LEFT:
    hid = feat_id.split("/")[0]
    print(f"Feature — Bore {hid} at X={hx}, Z={hz}:")
    vl.check_void(f"Bore {hid} center mid-base",
                  hx, MID_Y_BASE, hz,
                  f"void at bore center in base plate")
    vl.check_void(f"Bore {hid} near front face",
                  hx, 0.3, hz,
                  f"void near front face Y=0.3")
    vl.check_void(f"Bore {hid} in boss mid-height",
                  hx, MID_Y_BOSS, hz,
                  f"void at boss mid-height")
    vl.check_void(f"Bore {hid} near tip face",
                  hx, FULL_DEPTH - 0.3, hz,
                  f"void near tip face")
    # Path continuity across base/boss interface
    vl.check_void(f"Bore {hid} path below Y=3",
                  hx, PLATE_D - 0.1, hz,
                  f"void just below base/boss interface")
    vl.check_void(f"Bore {hid} path above Y=3",
                  hx, PLATE_D + 0.1, hz,
                  f"void just above base/boss interface")
    vl.check_solid(f"Bore {hid} solid outside (+X)",
                   hx + HOLE_R + 0.5, MID_Y_BASE, hz,
                   f"solid outside bore radius")
    print()

# L6, L7: Strut bores
print("Features L6-L7 — Strut bores (left):")
for bore_id, cx, cz in STRUT_BORES_LEFT:
    vl.check_void(f"Strut bore {bore_id} center",
                  cx, MID_Y_BASE, cz,
                  f"void at bore center")
    vl.check_void(f"Strut bore {bore_id} front",
                  cx, 0.1, cz,
                  f"void near front face")
    vl.check_void(f"Strut bore {bore_id} back",
                  cx, 2.9, cz,
                  f"void near back face")
    inset = 0.3
    half_w = STRUT_BORE_W / 2
    half_h = STRUT_BORE_H / 2
    vl.check_void(f"Strut bore {bore_id} corner +X+Z",
                  cx + half_w - inset, MID_Y_BASE, cz + half_h - inset,
                  f"void near +X+Z corner")
    vl.check_void(f"Strut bore {bore_id} corner -X-Z",
                  cx - half_w + inset, MID_Y_BASE, cz - half_h + inset,
                  f"void near -X-Z corner")
print()

# --- RIGHT HALF ---
print("--- RIGHT HALF ---")
print()

vr = Validator(right_half)

# R1: Base plate (right)
print("Feature R1 — Base plate (right):")
vr.check_solid("R-plate center",         102.9, MID_Y_BASE, 34.3,  "solid at right plate center")
vr.check_solid("R-plate near X=68.6",    69.1,  MID_Y_BASE, 34.3,  "solid near split face")
vr.check_solid("R-plate near X=137.2",   136.7, MID_Y_BASE, 34.3,  "solid near right edge")
vr.check_solid("R-plate near Z=0",       102.9, MID_Y_BASE, 0.5,   "solid near bottom edge")
vr.check_solid("R-plate near Z=68.6",    102.9, MID_Y_BASE, 68.1,  "solid near top edge")
vr.check_void("R-plate void below X=68.6",
              68.1, MID_Y_BASE, 34.3,
              "void below split face — right half does not extend below X=68.6")
print()

# R2, R3: Bosses B3, B4
for feat_id, hx, hz in HOLES_RIGHT:
    bid = feat_id.split("/")[1]
    print(f"Feature — Boss {bid} at X={hx}, Z={hz}:")
    vr.check_solid(f"Boss {bid} wall mid-height",
                   hx + BOSS_R_IN + (BOSS_R_OUT - BOSS_R_IN) / 2.0,
                   MID_Y_BOSS, hz,
                   f"solid in boss wall at mid-height Y={MID_Y_BOSS:.2f}")
    vr.check_solid(f"Boss {bid} wall near base",
                   hx + BOSS_R_IN + 1.0, PLATE_D + 0.5, hz,
                   f"solid in boss wall just above back face")
    vr.check_solid(f"Boss {bid} wall near tip",
                   hx + BOSS_R_IN + 1.0, FULL_DEPTH - 0.3, hz,
                   f"solid in boss wall near tip face")
    vr.check_void(f"Boss {bid} inner bore near tip",
                  hx, FULL_DEPTH - 0.5, hz,
                  f"void at boss center near tip — bore passes through")
    vr.check_void(f"Boss {bid} void beyond OD",
                  hx + BOSS_R_OUT + 1.0, MID_Y_BOSS, hz,
                  f"void outside boss OD radius")
    print()

# R4, R5: Bores H3, H4
for feat_id, hx, hz in HOLES_RIGHT:
    hid = feat_id.split("/")[0]
    print(f"Feature — Bore {hid} at X={hx}, Z={hz}:")
    vr.check_void(f"Bore {hid} center mid-base",
                  hx, MID_Y_BASE, hz,
                  f"void at bore center in base plate")
    vr.check_void(f"Bore {hid} near front face",
                  hx, 0.3, hz,
                  f"void near front face Y=0.3")
    vr.check_void(f"Bore {hid} in boss mid-height",
                  hx, MID_Y_BOSS, hz,
                  f"void at boss mid-height")
    vr.check_void(f"Bore {hid} near tip face",
                  hx, FULL_DEPTH - 0.3, hz,
                  f"void near tip face")
    vr.check_void(f"Bore {hid} path below Y=3",
                  hx, PLATE_D - 0.1, hz,
                  f"void just below base/boss interface")
    vr.check_void(f"Bore {hid} path above Y=3",
                  hx, PLATE_D + 0.1, hz,
                  f"void just above base/boss interface")
    vr.check_solid(f"Bore {hid} solid outside (+X)",
                   hx + HOLE_R + 0.5, MID_Y_BASE, hz,
                   f"solid outside bore radius")
    print()

# R6, R7: Strut bores
print("Features R6-R7 — Strut bores (right):")
for bore_id, cx, cz in STRUT_BORES_RIGHT:
    vr.check_void(f"Strut bore {bore_id} center",
                  cx, MID_Y_BASE, cz,
                  f"void at bore center")
    vr.check_void(f"Strut bore {bore_id} front",
                  cx, 0.1, cz,
                  f"void near front face")
    vr.check_void(f"Strut bore {bore_id} back",
                  cx, 2.9, cz,
                  f"void near back face")
    inset = 0.3
    half_w = STRUT_BORE_W / 2
    half_h = STRUT_BORE_H / 2
    vr.check_void(f"Strut bore {bore_id} corner +X+Z",
                  cx + half_w - inset, MID_Y_BASE, cz + half_h - inset,
                  f"void near +X+Z corner")
    vr.check_void(f"Strut bore {bore_id} corner -X-Z",
                  cx - half_w + inset, MID_Y_BASE, cz - half_h + inset,
                  f"void near -X-Z corner")
print()

# ---------------------------------------------------------------------------
# Rubric 4 — Solid Validity
# ---------------------------------------------------------------------------

print("=" * 60)
print("RUBRIC 4 — Solid Validity")
print("=" * 60)
print()

print("--- LEFT HALF ---")
vl.check_valid()
vl.check_single_body()
left_envelope = SPLIT_X * FULL_DEPTH * PLATE_H
vl.check_volume(expected_envelope=left_envelope, fill_range=(0.1, 0.8))
print()

print("--- RIGHT HALF ---")
vr.check_valid()
vr.check_single_body()
right_envelope = (PLATE_W - SPLIT_X) * FULL_DEPTH * PLATE_H
vr.check_volume(expected_envelope=right_envelope, fill_range=(0.1, 0.8))
print()

# ---------------------------------------------------------------------------
# Rubric 5 — Bounding Box Reconciliation
# ---------------------------------------------------------------------------

print("=" * 60)
print("RUBRIC 5 — Bounding Box Reconciliation")
print("=" * 60)
print()

print("--- LEFT HALF ---")
bb_l = left_half.val().BoundingBox()
vl.check_bbox("X", bb_l.xmin, bb_l.xmax, 0.0,     SPLIT_X)
vl.check_bbox("Y", bb_l.ymin, bb_l.ymax, 0.0,     FULL_DEPTH)
vl.check_bbox("Z", bb_l.zmin, bb_l.zmax, 0.0,     PLATE_H)
print()

print("--- RIGHT HALF ---")
bb_r = right_half.val().BoundingBox()
vr.check_bbox("X", bb_r.xmin, bb_r.xmax, SPLIT_X, PLATE_W)
vr.check_bbox("Y", bb_r.ymin, bb_r.ymax, 0.0,     FULL_DEPTH)
vr.check_bbox("Z", bb_r.zmin, bb_r.zmax, 0.0,     PLATE_H)
print()

# ---------------------------------------------------------------------------
# Final summary — exits 1 on any FAIL
# ---------------------------------------------------------------------------

print("=" * 60)
print("FINAL SUMMARY")
print("=" * 60)
print()

left_ok = vl.summary()
right_ok = vr.summary()

if not (left_ok and right_ok):
    print()
    print("FAILURES DETECTED — fix model before exporting.")
    sys.exit(1)

print()
print(f"LEFT  STEP file written: {LEFT_STEP}")
print(f"RIGHT STEP file written: {RIGHT_STEP}")
