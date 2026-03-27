#!/usr/bin/env python3
"""
Cartridge Release Plate — CadQuery STEP Generation

Generated from scratch per:
  - hardware/cartridge-release-plate/planning/parts.md
  - hardware/planning/step-generation-standards.md
  - hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md

Coordinate system:
  Origin: plate bottom-left-front corner (front face = fitting engagement side)
  X: plate width, left to right (59mm)  -> X: [0, 59]
  Y: plate depth, front to back (6mm)   -> Y: [0, 6]
      Front face Y=0 engages fittings (outer bore entry)
      Back face Y=6 receives push rod (tube hole exit, boss)
  Z: plate height, bottom to top (47mm) -> Z: [0, 47]
  Envelope (body only): 59 x 6 x 47 mm

Bore depth stack (from front face Y=0 inward):
  Y=0 to Y=2: outer bore (body end cradle), 15.30mm dia (clears 15.10mm body end OD)
  Y=2 to Y=4: inner lip (collet hugger), 9.70mm dia (clears 9.57mm collet OD)
  Y=4 to Y=6: structural back wall, tube clearance hole only (6.50mm dia)

Guide pin tabs protrude beyond the plate body in +/- X.
Push rod boss protrudes beyond back face in +Y.
"""

import cadquery as cq
import sys
from pathlib import Path

# ============================================================
# PARAMETERS — all from parts.md and geometry-description.md
# ============================================================

# Plate body
PLATE_W = 59.0   # X
PLATE_D = 6.0    # Y
PLATE_H = 47.0   # Z

# Stepped bore diameters
OUTER_BORE_DIA = 15.30    # body end cradle: 0.20mm over 15.10mm body end OD
OUTER_BORE_DEPTH = 2.0    # Y=0 to Y=2
INNER_LIP_DIA = 9.70      # collet hugger: 0.13mm over 9.57mm collet OD
INNER_LIP_DEPTH = 2.0     # Y=2 to Y=4
TUBE_HOLE_DIA = 6.50      # between 6.30mm tube OD and 6.69mm collet ID (midpoint)
# Tube hole goes through full depth Y=0 to Y=6

# Chamfers
OUTER_CHAMFER = 0.3   # 45-deg lead-in at outer bore entry (front face Y=0)
TUBE_CHAMFER = 0.1    # at tube hole entry edge (back face Y=6)

# Bore grid centers: 2x2, relative to plate bottom-left (X, Z)
BORE_CENTERS_XZ = [
    (9.5,  9.5),   # bottom-left
    (49.5, 9.5),   # bottom-right
    (9.5,  37.5),  # top-left
    (49.5, 37.5),  # top-right
]

# Guide pin slots
SLOT_W = 3.3   # width in X (clears 3mm dowel pin)
SLOT_L = 7.3   # length in Z (vertical alignment tolerance)
# Slot centers relative to plate bottom-left (X, Z):
SLOT_CENTERS_XZ = [
    (-5.5,  23.5),  # left (beyond plate body)
    (64.5,  23.5),  # right (beyond plate body)
]

# Guide pin tab dimensions
TAB_WALL_MIN = 2.0   # minimum wall around slot
TAB_W = SLOT_W + 2 * TAB_WALL_MIN   # 7.3mm in X
TAB_H = SLOT_L + 2 * TAB_WALL_MIN   # 11.3mm in Z

# Push rod contact boss
BOSS_X = 29.5    # plate center width
BOSS_Z = 23.5    # plate center height
BOSS_DIA = 8.0
BOSS_PROUD = 1.0  # mm proud of back face

# Derived radii
R_OUTER = OUTER_BORE_DIA / 2     # 7.65
R_INNER = INNER_LIP_DIA / 2      # 4.85
R_TUBE  = TUBE_HOLE_DIA / 2      # 3.25

# ============================================================
# FEATURE PLANNING TABLE (Rubric 1 — printed at runtime)
# ============================================================

FEATURE_TABLE = """\
============================================================
FEATURE PLANNING TABLE (Rubric 1)
============================================================
| #  | Feature Name               | Mechanical Function                 | Op     | Shape   | Axis | Center (X,Y,Z)      | Dimensions                | Notes                        |
|----|----------------------------|-------------------------------------|--------|---------|------|----------------------|---------------------------|------------------------------|
| 1  | Plate body                 | Structural base; carries all bores  | Add    | Box     | -    | (29.5, 3.0, 23.5)   | 59 x 6 x 47              | PETG, origin at BL-front     |
| 2  | Left guide pin tab         | Material surrounding left slot      | Add    | Box     | -    | (-5.5, 3.0, 23.5)   | 7.3 x 6.0 x 11.3         | Ear left of plate body       |
| 3  | Right guide pin tab        | Material surrounding right slot     | Add    | Box     | -    | (64.5, 3.0, 23.5)   | 7.3 x 6.0 x 11.3         | Ear right of plate body      |
| 4  | Push rod boss              | Cam lever push rod contact point    | Add    | Cyl     | Y    | (29.5, 6.5, 23.5)   | dia 8.0 x 1.0 proud      | On back face, extends +Y     |
| 5  | Tube clearance holes (x4)  | Tube passes through plate           | Remove | Cyl     | Y    | (cx, *, cz) x4      | dia 6.50, thru 6mm       | Through full depth           |
| 6  | Inner lip bores (x4)       | Lateral constraint on collet        | Remove | Cyl     | Y    | (cx, 3.0, cz) x4    | dia 9.70 x 2.0 deep      | Y=2 to Y=4                  |
| 7  | Outer bores (x4)           | Captures body end of fitting        | Remove | Cyl     | Y    | (cx, 1.0, cz) x4    | dia 15.30 x 2.0 deep     | Y=0 to Y=2 (front face)     |
| 8  | Outer bore chamfers (x4)   | Lead-in for fitting body end        | Remove | Chamfer | Y    | At each bore, Y=0    | 0.3mm x 45 deg           | Front face entry             |
| 9  | Tube hole chamfers (x4)    | Ease tube insertion at back face    | Remove | Chamfer | Y    | At each bore, Y~4    | 0.1mm x 45 deg           | At tube-to-inner-lip step    |
| 10 | Left guide pin slot        | Plate slides on dowel pin           | Remove | Stadium | Y    | (-5.5, *, 23.5)     | 3.3W x 7.3L thru         | Through tab, long axis in Z  |
| 11 | Right guide pin slot       | Plate slides on dowel pin           | Remove | Stadium | Y    | (64.5, *, 23.5)     | 3.3W x 7.3L thru         | Through tab, long axis in Z  |
============================================================
Bore centers (X, Z): (9.5,9.5), (49.5,9.5), (9.5,37.5), (49.5,37.5)
Bore spacing: 40mm horizontal, 28mm vertical
============================================================
"""

print(FEATURE_TABLE)

# ============================================================
# MODEL CONSTRUCTION
# ============================================================

# --- Feature 1: Plate body ---
# CQ box on XY workplane with centered=False: X=[0,W], Y=[0,D], Z=[0,H]
plate = cq.Workplane("XY").box(PLATE_W, PLATE_D, PLATE_H, centered=False)

# --- Features 2 & 3: Guide pin tabs ---
# Each tab is a rectangular block centered on the slot location.
# Tab must overlap with plate body so the union produces a single solid.
for slot_cx, slot_cz in SLOT_CENTERS_XZ:
    tab_x0 = slot_cx - TAB_W / 2
    tab_z0 = slot_cz - TAB_H / 2
    tab = (
        cq.Workplane("XY")
        .box(TAB_W, PLATE_D, TAB_H, centered=False)
        .translate((tab_x0, 0, tab_z0))
    )
    # Extend tab to overlap with plate body for solid fusion
    if slot_cx < 0:
        # Left tab: extend right edge to X=1 for overlap
        overlap = (
            cq.Workplane("XY")
            .box(abs(tab_x0 + TAB_W), PLATE_D, TAB_H, centered=False)
            .translate((tab_x0 + TAB_W, 0, tab_z0))
        )
        # Actually, simpler: make one box from tab_x0 to max(tab_x0+TAB_W, 1.0)
        tab_right_edge = max(tab_x0 + TAB_W, 1.0)
        tab = (
            cq.Workplane("XY")
            .box(tab_right_edge - tab_x0, PLATE_D, TAB_H, centered=False)
            .translate((tab_x0, 0, tab_z0))
        )
    else:
        # Right tab: extend left edge to X=58 for overlap
        tab_left_edge = min(tab_x0, PLATE_W - 1.0)
        tab_right_edge = tab_x0 + TAB_W
        tab = (
            cq.Workplane("XY")
            .box(tab_right_edge - tab_left_edge, PLATE_D, TAB_H, centered=False)
            .translate((tab_left_edge, 0, tab_z0))
        )
    plate = plate.union(tab)

# --- Feature 4: Push rod boss ---
# 8mm dia x 1mm cylinder on back face, centered at (29.5, 23.5)
# Back face is at Y=6, boss extends from Y=6 to Y=7
# Build on XZ plane, extrude along Y
boss = (
    cq.Workplane("XZ")
    .center(BOSS_X, BOSS_Z)
    .circle(BOSS_DIA / 2)
    .extrude(-BOSS_PROUD)           # XZ normal is -Y, so -extrude goes in +Y
    .translate((0, PLATE_D, 0))     # shift from Y=0..1 to Y=6..7
)
plate = plate.union(boss)

# --- Features 5, 6, 7, 8, 9: Stepped bores with chamfers (x4) ---
# Use a revolved half-section profile to create each bore cutter.
# Profile is drawn in (R, Y) space and revolved around Y axis.
# Y=0 is front face, Y=6 is back face.
#
# Depth stack:
#   Y=0..2: outer bore (R_OUTER=7.65) with 0.3mm chamfer at Y=0
#   Y=2..4: inner lip (R_INNER=4.85)
#   Y=4..6: tube hole (R_TUBE=3.25) with 0.1mm chamfer at Y=4
#
# Revolved profile points (R, Y), starting from axis at front face,
# going outward then back to axis at back face:
C_O = OUTER_CHAMFER  # 0.3
C_T = TUBE_CHAMFER   # 0.1

profile_pts = [
    (0,                0),                                      # axis at front face
    (R_OUTER - C_O,   0),                                      # chamfer start on front face
    (R_OUTER,          C_O),                                    # chamfer end (bore wall)
    (R_OUTER,          OUTER_BORE_DEPTH),                       # outer bore floor (Y=2)
    (R_INNER,          OUTER_BORE_DEPTH),                       # step down to inner lip
    (R_INNER,          OUTER_BORE_DEPTH + INNER_LIP_DEPTH),    # inner lip floor (Y=4)
    (R_TUBE + C_T,     OUTER_BORE_DEPTH + INNER_LIP_DEPTH),    # tube chamfer start
    (R_TUBE,           OUTER_BORE_DEPTH + INNER_LIP_DEPTH + C_T),  # tube chamfer end
    (R_TUBE,           PLATE_D),                                # tube hole to back face
    (0,                PLATE_D),                                # axis at back face
]

# Build the bore cutter profile on XY plane
bore_profile = cq.Workplane("XY").moveTo(*profile_pts[0])
for pt in profile_pts[1:]:
    bore_profile = bore_profile.lineTo(*pt)
bore_profile = bore_profile.close()

# Revolve around Y axis (line from origin along Y direction)
bore_cutter = bore_profile.revolve(360, (0, 0), (0, 1))

# Cut each bore at its (cx, cz) position
for cx, cz in BORE_CENTERS_XZ:
    plate = plate.cut(bore_cutter.translate((cx, 0, cz)))

# --- Features 10 & 11: Guide pin slots ---
# Stadium shape: 3.3mm wide (X) x 7.3mm long (Z), through full depth (Y)
# On XZ workplane, slot2D(length, width, angle=90) orients the long axis along Z.
for slot_cx, slot_cz in SLOT_CENTERS_XZ:
    slot_cutter = (
        cq.Workplane("XZ")
        .center(slot_cx, slot_cz)
        .slot2D(SLOT_L, SLOT_W, angle=90)
        .extrude(-PLATE_D)   # XZ normal is -Y; -extrude goes in +Y direction
    )
    plate = plate.cut(slot_cutter)

# ============================================================
# EXPORT STEP FILE
# ============================================================

output_path = Path(__file__).parent / "release-plate-cadquery.step"
cq.exporters.export(plate, str(output_path))
print(f"STEP exported to: {output_path}")

# ============================================================
# RUBRIC 4: Solid Validity
# ============================================================

print("\n" + "=" * 60)
print("RUBRIC 4: Solid Validity")
print("=" * 60)

solid = plate.val()
is_valid = solid.isValid()
num_bodies = len(plate.solids().vals())
volume = solid.Volume()
envelope_vol = PLATE_W * PLATE_D * PLATE_H
vol_pct = volume / envelope_vol * 100

print(f"  Valid solid: {is_valid}")
print(f"  Number of bodies: {num_bodies}")
print(f"  Volume: {volume:.1f} mm^3")
print(f"  Envelope volume: {envelope_vol:.1f} mm^3")
print(f"  Fill ratio: {vol_pct:.1f}% (expect 60-90% — tabs/boss add, bores remove)")

rubric4_pass = is_valid and num_bodies == 1 and volume > 0

# ============================================================
# RUBRIC 5: Bounding Box Reconciliation
# ============================================================

print("\n" + "=" * 60)
print("RUBRIC 5: Bounding Box Reconciliation")
print("=" * 60)

bb = solid.BoundingBox()
print(f"  Actual:   X=[{bb.xmin:.2f}, {bb.xmax:.2f}]  Y=[{bb.ymin:.2f}, {bb.ymax:.2f}]  Z=[{bb.zmin:.2f}, {bb.zmax:.2f}]")

# Expected bounds accounting for tabs, boss, and chamfers
exp_xmin = SLOT_CENTERS_XZ[0][0] - TAB_W / 2   # -5.5 - 3.65 = -9.15
exp_xmax = SLOT_CENTERS_XZ[1][0] + TAB_W / 2   # 64.5 + 3.65 = 68.15
exp_ymin = 0.0
exp_ymax = PLATE_D + BOSS_PROUD                 # 7.0
exp_zmin = 0.0
exp_zmax = PLATE_H                               # 47.0

print(f"  Expected: X=[{exp_xmin:.2f}, {exp_xmax:.2f}]  Y=[{exp_ymin:.2f}, {exp_ymax:.2f}]  Z=[{exp_zmin:.2f}, {exp_zmax:.2f}]")

rubric5_pass = True
for name, a_min, a_max, e_min, e_max in [
    ("X", bb.xmin, bb.xmax, exp_xmin, exp_xmax),
    ("Y", bb.ymin, bb.ymax, exp_ymin, exp_ymax),
    ("Z", bb.zmin, bb.zmax, exp_zmin, exp_zmax),
]:
    ok = abs(a_min - e_min) < 0.5 and abs(a_max - e_max) < 0.5
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}: [{a_min:.2f}, {a_max:.2f}] vs [{e_min:.2f}, {e_max:.2f}]")
    if not ok:
        rubric5_pass = False

# ============================================================
# RUBRIC 3: Feature-Specification Reconciliation
# ============================================================

print("\n" + "=" * 60)
print("RUBRIC 3: Feature-Specification Reconciliation")
print("=" * 60)

from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt

def is_void(x, y, z, tol=0.001):
    """Return True if the point is outside the solid (void)."""
    classifier = BRepClass3d_SolidClassifier(solid.wrapped, gp_Pnt(x, y, z), tol)
    return classifier.State() != 0  # 0=IN, 1=ON, 2=OUT

def is_solid_at(x, y, z, tol=0.001):
    """Return True if the point is inside the solid."""
    return not is_void(x, y, z, tol)

results = []

def check(name, passed, detail):
    status = "PASS" if passed else "FAIL"
    results.append((name, status, detail))
    print(f"  [{status}] {name}: {detail}")

# --- Feature 1: Plate body ---
# Check solid at plate interior points
check("Plate body",
      is_solid_at(PLATE_W / 2, PLATE_D / 2, 2.0) and  # near bottom
      is_solid_at(PLATE_W / 2, PLATE_D / 2, 45.0),     # near top
      f"solid at center bottom and top interior points")

# --- Features 2 & 3: Guide pin tabs ---
left_tab_cx = SLOT_CENTERS_XZ[0][0]
right_tab_cx = SLOT_CENTERS_XZ[1][0]

# Check solid in tab material (outside slot, inside tab boundary)
check("Left guide pin tab",
      is_solid_at(left_tab_cx, PLATE_D / 2, 23.5 + SLOT_L / 2 + 1.0),
      f"solid above slot in left tab at X={left_tab_cx}")

check("Right guide pin tab",
      is_solid_at(right_tab_cx, PLATE_D / 2, 23.5 + SLOT_L / 2 + 1.0),
      f"solid above slot in right tab at X={right_tab_cx}")

# --- Feature 4: Push rod boss ---
check("Push rod boss",
      is_solid_at(BOSS_X, PLATE_D + BOSS_PROUD / 2, BOSS_Z) and
      bb.ymax > PLATE_D + BOSS_PROUD - 0.1,
      f"solid at boss center Y={PLATE_D + BOSS_PROUD/2:.1f}, ymax={bb.ymax:.2f}")

# --- Features 5, 6, 7: Stepped bores (4x) ---
for i, (cx, cz) in enumerate(BORE_CENTERS_XZ):
    label = f"Bore {i+1} ({cx},{cz})"

    # Feature 7: Outer bore (Y=0 to Y=2) — void at outer bore radius
    check(f"{label} outer bore void",
          is_void(cx + R_OUTER - 0.5, 1.0, cz),
          f"void at R={R_OUTER-0.5:.1f}, Y=1.0")

    # Outer bore wall — solid just outside outer bore
    check(f"{label} outer bore wall",
          is_solid_at(cx + R_OUTER + 0.5, 1.0, cz),
          f"solid at R={R_OUTER+0.5:.1f}, Y=1.0")

    # Feature 6: Inner lip (Y=2 to Y=4) — void at inner lip radius
    check(f"{label} inner lip void",
          is_void(cx + R_INNER - 0.3, 3.0, cz),
          f"void at R={R_INNER-0.3:.1f}, Y=3.0")

    # Wall between inner lip and plate edge at Y=3
    r_mid = (R_INNER + R_OUTER) / 2
    check(f"{label} lip-to-outer wall",
          is_solid_at(cx + r_mid, 3.0, cz),
          f"solid at R={r_mid:.1f}, Y=3.0")

    # Feature 5: Tube clearance hole — void at bore center, full depth
    check(f"{label} tube hole (center Y=5)",
          is_void(cx, 5.0, cz),
          f"void at bore center, Y=5.0")

    # Structural back wall around tube hole (Y=4 to Y=6)
    r_tube_wall = (R_TUBE + R_INNER) / 2
    check(f"{label} back wall solid",
          is_solid_at(cx + r_tube_wall, 5.0, cz),
          f"solid at R={r_tube_wall:.1f}, Y=5.0")

# --- Feature 8: Outer bore chamfers ---
# The chamfer narrows the bore opening at the front face (lead-in bevel).
# Profile: (R_OUTER-C_O, 0) to (R_OUTER, C_O) — i.e., bore radius at Y=0
# is R_OUTER-0.3 = 7.35, expanding to R_OUTER = 7.65 at Y=0.3.
# Test: at Y=0.15 (mid-chamfer), the boundary is at R ~= 7.50.
# A point at R=7.55 should be SOLID (the chamfer preserves material there
# that a straight bore wall would have removed).
for i, (cx, cz) in enumerate(BORE_CENTERS_XZ):
    # Point in the chamfer-preserved material zone
    test_r = R_OUTER - 0.1   # R=7.55 — inside bore wall but outside chamfer line at Y=0.1
    test_y = 0.1             # within the chamfer transition zone
    check(f"Bore {i+1} outer chamfer",
          is_solid_at(cx + test_r, test_y, cz),
          f"solid at R={test_r:.2f}, Y={test_y} (chamfer preserves material here)")

# --- Feature 9: Tube hole chamfers ---
# The chamfer transitions from the inner lip bore (R=4.85) to tube hole (R=3.25).
# Profile: (R_TUBE+C_T, 4.0) = (3.35, 4.0) to (R_TUBE, 4.1) = (3.25, 4.1).
# Without the chamfer, the step would be a sharp corner at (3.25, 4.0).
# The chamfer preserves material between R=3.25 and R=3.35 around Y=4.0.
# Test: verify the inner lip bore (R=4.85) is void at Y=3.5, but the tube
# hole region (R=3.30) is SOLID at Y=4.05 thanks to the chamfer bevel.
# The chamfer boundary at Y=4.05 is R = 3.35 - 0.1*(0.05/0.1) = 3.30.
# Check that at R=3.32 (just inside chamfer line), Y=4.03, material exists.
for i, (cx, cz) in enumerate(BORE_CENTERS_XZ):
    # A point well inside the chamfer-preserved zone: R=3.34 at Y=4.01
    # At Y=4.01, chamfer boundary = 3.35 - 0.1*(0.01/0.1) = 3.34
    # Use R=3.34 at Y=4.005 — boundary there is 3.345, so R=3.34 < 3.345 means void
    # Actually, let's just verify the chamfer exists by checking that at the inner lip
    # floor (Y=4.0), a point at R between R_TUBE and R_TUBE+C_T is void
    # (the chamfer starts at R=3.35 at Y=4.0 and is void below that)
    # and that at Y=4.08, R=3.26 is solid (just outside tube hole, chamfer preserved)
    test_r = R_TUBE + 0.02  # R=3.27
    test_y = OUTER_BORE_DEPTH + INNER_LIP_DEPTH + TUBE_CHAMFER * 0.7  # Y = 4.07
    # At Y=4.07, chamfer boundary = 3.35 - 0.1*(0.07/0.1) = 3.28
    # R=3.27 < 3.28, so this is inside the bore (void). Need R > 3.28.
    # Use R=3.30 at Y=4.07: boundary is 3.28, so R=3.30 > 3.28 = SOLID
    test_r2 = R_TUBE + 0.05  # R=3.30
    test_y2 = OUTER_BORE_DEPTH + INNER_LIP_DEPTH + TUBE_CHAMFER * 0.7  # Y=4.07
    check(f"Bore {i+1} tube chamfer",
          is_solid_at(cx + test_r2, test_y2, cz),
          f"solid at R={test_r2:.2f}, Y={test_y2:.2f} (chamfer-preserved zone)")

# --- Features 10 & 11: Guide pin slots ---
for i, (sx, sz) in enumerate(SLOT_CENTERS_XZ):
    label = f"Guide slot {i+1} ({sx},{sz})"

    # Slot center should be void (through-hole)
    check(f"{label} center void",
          is_void(sx, PLATE_D / 2, sz),
          f"void at slot center Y={PLATE_D/2}")

    # Ends of slot should be void (stadium extends +/- SLOT_L/2 in Z)
    check(f"{label} top end void",
          is_void(sx, PLATE_D / 2, sz + SLOT_L / 2 - 0.3),
          f"void near top end of slot Z={sz + SLOT_L/2 - 0.3:.1f}")

    # Material around slot (tab wall)
    check(f"{label} tab material",
          is_solid_at(sx, PLATE_D / 2, sz + SLOT_L / 2 + TAB_WALL_MIN / 2),
          f"solid in tab wall above slot")

# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

all_features_pass = all(s == "PASS" for _, s, _ in results)
print(f"  Rubric 3 (Feature Validation): {'ALL PASS' if all_features_pass else 'SOME FAILED'}")
print(f"  Rubric 4 (Solid Validity):     {'PASS' if rubric4_pass else 'FAIL'}")
print(f"  Rubric 5 (Bounding Box):       {'PASS' if rubric5_pass else 'FAIL'}")

if all_features_pass and rubric4_pass and rubric5_pass:
    print("\n  *** ALL VALIDATIONS PASSED ***")
    print(f"  STEP file: {output_path}")
else:
    print("\n  *** VALIDATION FAILED — review errors above ***")
    sys.exit(1)
