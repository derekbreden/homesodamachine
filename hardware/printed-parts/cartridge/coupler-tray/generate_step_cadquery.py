"""
Coupler Tray — CadQuery STEP Generation Script
Pipeline step: 6g — STEP Generation
Input:  planning/parts.md, planning/spatial-resolution.md
Output: coupler-tray-cadquery.step

Part: Single printed PETG plate that captures four John Guest PP0408W union
couplers inside the pump cartridge. Each coupler seats in a stepped-bore
pocket; the barbell shoulder geometry provides axial retention in both
directions.

# Rubric 2 — Coordinate System Declaration (MANDATORY)
# -------------------------------------------------------
# Coordinate system (part local frame, from parts.md Section 1):
#   Origin: geometric center of the insertion face (large-bore opening face)
#   X: plate width, horizontal — positive right when viewed from insertion face
#      Range: −40 mm → +40 mm
#   Y: plate height, vertical — positive up
#      Range: −25 mm → +25 mm
#   Z: depth into plate from insertion face — positive toward far face
#      Range: 0 mm → +15 mm
#   Z = 0  = insertion face (large-bore openings, placed on build plate)
#   Z = +15 = far face (narrow-bore exit openings)
#   Envelope: 80W × 50H × 15D mm → X:[−40,+40] Y:[−25,+25] Z:[0,+15]
#
# Print orientation: insertion face (Z=0) DOWN on build plate.
# Bore axes run in Z direction (vertical during print).
#
# CadQuery box placement:
#   cq.Workplane("XY").box(80, 50, 15, centered=False) places X:[0,80] Y:[0,50] Z:[0,15]
#   We need X:[−40,+40] Y:[−25,+25] Z:[0,+15], so we use centered=False then translate,
#   OR we use centered=True in XY and centered=False in Z:
#     box(80, 50, 15, centered=(True, True, False)) → X:[−40,+40] Y:[−25,+25] Z:[0,+15]
#
# XY workplane convention:
#   Normal = +Z direction.
#   workplane(offset=Z_pos) places the XY plane at Z = Z_pos.
#   positive extrude depth goes in +Z direction.
#
# Bore cuts run in +Z direction from Z=0 (insertion face).
# Each stepped bore: large bore Z=0→+12.08, narrow bore Z=+12.08→+15.
"""

import sys
from pathlib import Path

import cadquery as cq

# Add tools/ to sys.path for step_validate
# Script is at: hardware/printed-parts/cartridge/coupler-tray/generate_step_cadquery.py
# parents[3] = project root (coupler-tray → cartridge → printed-parts → hardware → root)
# Wait: coupler-tray is parents[0], cartridge=parents[1], printed-parts=parents[2],
# hardware=parents[3], project root=parents[4]
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))
from step_validate import Validator

# ==============================================================================
# Part parameters (from parts.md Section 9)
# ==============================================================================

PLATE_W = 80.0    # X extent (total width)
PLATE_H = 50.0    # Y extent (total height)
PLATE_D = 15.0    # Z extent (total depth, insertion face → far face)

# Bore diameters (from parts.md Section 9, Features 2–5)
R_LARGE  = 15.5 / 2   # 7.75 mm — large bore radius (body-end clearance)
R_NARROW = 9.5  / 2   # 4.75 mm — narrow bore radius (center body fit)

# Bore depth transition (from parts.md, all four features)
DEPTH_LARGE = 12.08    # Z = 0 → +12.08 mm: large bore stage
DEPTH_NARROW_START = DEPTH_LARGE   # = 12.08
DEPTH_NARROW_END   = PLATE_D       # = 15.0 mm: narrow bore exits far face

# Elephant's foot chamfer spec (from parts.md Section 8, Step 1)
CHAMFER_SIZE = 0.3    # 0.3 mm × 45° on all four large bore rims at Z = 0

# Bore center positions (X, Y) — Z-axis bores, same (X,Y) for both stages
BORE_CENTERS = [
    (-31.0, +15.0),   # A — Pump 1 Inlet   (top-left when viewed from insertion face)
    (-31.0, -15.0),   # B — Pump 1 Outlet  (bottom-left)
    (+31.0, +15.0),   # C — Pump 2 Inlet   (top-right)
    (+31.0, -15.0),   # D — Pump 2 Outlet  (bottom-right)
]

# ==============================================================================
# Rubric 1 — Feature Planning Table (printed to stdout)
# ==============================================================================

FEATURE_TABLE = """
COUPLER TRAY — FEATURE PLANNING TABLE (Rubric 1)
=================================================

  #   Feature Name                   Op      Shape         Axis  Center (X,Y,Z)           Dimensions
  1   Plate body                     Add     Rect prism    Z     (0, 0, 7.5)               80W × 50H × 15D mm
  2   Bore A large  (−31,+15)        Remove  Cylinder      Z     (−31, +15,  6.04)         Ø15.5 mm, Z=0→+12.08 mm
  3   Bore A narrow (−31,+15)        Remove  Cylinder      Z     (−31, +15, 13.54)         Ø9.5 mm,  Z=+12.08→+15 mm
  4   Bore B large  (−31,−15)        Remove  Cylinder      Z     (−31, −15,  6.04)         Ø15.5 mm, Z=0→+12.08 mm
  5   Bore B narrow (−31,−15)        Remove  Cylinder      Z     (−31, −15, 13.54)         Ø9.5 mm,  Z=+12.08→+15 mm
  6   Bore C large  (+31,+15)        Remove  Cylinder      Z     (+31, +15,  6.04)         Ø15.5 mm, Z=0→+12.08 mm
  7   Bore C narrow (+31,+15)        Remove  Cylinder      Z     (+31, +15, 13.54)         Ø9.5 mm,  Z=+12.08→+15 mm
  8   Bore D large  (+31,−15)        Remove  Cylinder      Z     (+31, −15,  6.04)         Ø15.5 mm, Z=0→+12.08 mm
  9   Bore D narrow (+31,−15)        Remove  Cylinder      Z     (+31, −15, 13.54)         Ø9.5 mm,  Z=+12.08→+15 mm
 10   Elephant's foot chamfers ×4    Remove  Chamfer 45°   Z     Each large bore rim, Z=0  0.3 mm × 45°

Bore stage detail (identical for all 4 pockets):
  Large bore:  Ø15.5 mm (R=7.75), Z: 0 → +12.08 mm (depth 12.08 mm, from insertion face)
  Narrow bore: Ø9.5 mm  (R=4.75), Z: +12.08 → +15 mm (depth 2.92 mm, exits far face)
  Bore shoulder: annular step at Z=+12.08 mm, inner R=4.75 mm, outer R=7.75 mm
  Entry chamfer: 0.3 mm × 45° at large bore rim, Z=0 (insertion / build-plate face)

Coordinate system (Rubric 2):
  Origin: geometric center of insertion face
  X: plate width, − left → + right  (−40 mm → +40 mm)
  Y: plate height, − bottom → + top (−25 mm → +25 mm)
  Z: depth into plate, 0=insertion face, +15=far face
  Bounding box: X:[−40,+40]  Y:[−25,+25]  Z:[0,+15]
"""

# ==============================================================================
# Modeling
# ==============================================================================

print("=" * 70)
print("COUPLER TRAY — CadQuery STEP Generation")
print("=" * 70)
print(FEATURE_TABLE)
print("Building model...")

# ------------------------------------------------------------------------------
# Feature 1: Plate body
# box(80, 50, 15, centered=(True, True, False)):
#   centered=True in X and Y → X:[−40,+40], Y:[−25,+25]
#   centered=False in Z → Z:[0,+15]
# This matches the coordinate system: origin at center of insertion face,
# Z=0 = insertion face (bottom of plate during printing).
# ------------------------------------------------------------------------------
plate = cq.Workplane("XY").box(PLATE_W, PLATE_H, PLATE_D, centered=(True, True, False))
print(f"  [+] Feature 1: Plate body ({PLATE_W}W × {PLATE_H}H × {PLATE_D}D mm)")

# ------------------------------------------------------------------------------
# Features 2–9: Stepped bores A, B, C, D
#
# Each bore has two stages, both centered at (bx, by) in X,Y, running along Z:
#   Stage 1 (large bore):  Ø15.5 mm, from Z=0 to Z=+12.08 mm
#   Stage 2 (narrow bore): Ø9.5 mm,  from Z=+12.08 mm to Z=+15 mm
#
# We cut each stage separately using XY workplane cuts:
#   - Place XY workplane at Z=0, extrude +12.08 → cuts large bore
#   - Place XY workplane at Z=+12.08, extrude +2.92 → cuts narrow bore
#
# XY workplane convention:
#   workplane(offset=Z_val) → the XY plane is placed at Z = Z_val
#   extrude(depth) → extrude in +Z direction (the XY normal)
#
# The elephant's foot chamfer (Feature 10) is applied after all bores are cut.
# ------------------------------------------------------------------------------

for bore_idx, (bx, by) in enumerate(BORE_CENTERS):
    label = ["A", "B", "C", "D"][bore_idx]
    feat_large  = 2 + bore_idx * 2       # features 2, 4, 6, 8
    feat_narrow = 3 + bore_idx * 2       # features 3, 5, 7, 9

    # Stage 1 — Large bore: Z = 0 → +12.08 mm
    # XY plane at Z=0 (default offset=0), extrude +12.08 in +Z
    large_bore = (
        cq.Workplane("XY")
        .workplane(offset=0.0)            # plane at Z=0 (insertion face)
        .center(bx, by)
        .circle(R_LARGE)
        .extrude(DEPTH_LARGE)             # +Z direction, depth = 12.08 mm
    )
    plate = plate.cut(large_bore)
    print(f"  [-] Feature {feat_large}: Bore {label} large bore at X={bx}, Y={by}, Z=0→{DEPTH_LARGE}")

    # Stage 2 — Narrow bore: Z = +12.08 → +15 mm
    # XY plane at Z=+12.08, extrude +(15-12.08) = +2.92 in +Z
    narrow_depth = DEPTH_NARROW_END - DEPTH_NARROW_START   # 2.92 mm
    narrow_bore = (
        cq.Workplane("XY")
        .workplane(offset=DEPTH_NARROW_START)   # plane at Z=+12.08
        .center(bx, by)
        .circle(R_NARROW)
        .extrude(narrow_depth)                  # +Z direction, depth = 2.92 mm
    )
    plate = plate.cut(narrow_bore)
    print(f"  [-] Feature {feat_narrow}: Bore {label} narrow bore at X={bx}, Y={by}, Z={DEPTH_NARROW_START}→{DEPTH_NARROW_END}")

# ------------------------------------------------------------------------------
# Feature 10: Elephant's foot chamfers — 0.3 mm × 45° on all four large bore
# rims at Z = 0 (insertion face / build-plate face).
#
# After cutting the stepped bores, the large bore circular edges at Z=0 are
# the target edges. We select the face at Z_min (minimum Z face = insertion
# face), then select its inner circular edges (bore rims), and apply chamfer.
#
# Strategy: select the bottom face ("<Z"), then select only circular edges
# on that face using edge filter "|Z" inverted, or better: select all edges
# on that face and chamfer — but that would chamfer the outer perimeter too.
#
# Correct approach: The insertion face (Z=0) has:
#   - 4 circular bore rim edges (the openings of the large bores, Ø15.5)
#   - 4 outer perimeter edges (the plate boundary)
#
# We want ONLY the circular bore edges. Use:
#   plate.faces("<Z").wires().filter by size or use edge selection.
#
# The cleanest CadQuery approach: select the minimum-Z face, then select
# circular edges on it (bore openings are circles; plate perimeter edges
# are straight lines). We can distinguish them because bore edges are
# curved (circles) while the outer plate boundary edges are straight.
#
# CadQuery edge filter "%Circle" selects circular edges.
# ------------------------------------------------------------------------------
plate = plate.faces("<Z").edges("%Circle").chamfer(CHAMFER_SIZE)
print(f"  [-] Feature 10: Elephant's foot chamfers {CHAMFER_SIZE}mm×45° on 4 large bore rims at Z=0")

print()
print("Model construction complete.")
print()

# ==============================================================================
# Validation (Rubrics 3, 4, 5)
# ==============================================================================

print("=" * 70)
print("VALIDATION")
print("=" * 70)

v = Validator(plate)

# --- Feature 1: Plate body ---
print()
print("--- Feature 1: Plate body ---")
# Probe solid material in the plate body at several locations well away from bores
# Center of plate (between all bore clusters) at mid-depth
v.check_solid("Plate body center",      0.0, 0.0, 7.5,
              "solid at plate center (0, 0, 7.5)")
# Between the two bore columns, top region
v.check_solid("Plate body top-center",  0.0, +20.0, 7.5,
              "solid at plate top center (0, +20, 7.5)")
# Between the two bore columns, bottom region
v.check_solid("Plate body bot-center",  0.0, -20.0, 7.5,
              "solid at plate bottom center (0, -20, 7.5)")
# Left edge margin beyond bore A/B
v.check_solid("Plate body left edge",  -38.0, 0.0, 7.5,
              "solid at plate left edge X=-38, between bores")
# Right edge margin beyond bore C/D
v.check_solid("Plate body right edge", +38.0, 0.0, 7.5,
              "solid at plate right edge X=+38, between bores")

# --- Features 2–9: Stepped bores — existence, orientation, step continuity ---
bore_labels = ["A", "B", "C", "D"]
for bore_idx, (bx, by) in enumerate(BORE_CENTERS):
    label = bore_labels[bore_idx]
    print()
    print(f"--- Bore {label} at X={bx}, Y={by} ---")

    # Feature: large bore exists — probe at bore axis, mid-depth of large bore (Z~=+6)
    z_large_mid = DEPTH_LARGE / 2   # 6.04 mm
    v.check_void(f"Bore {label} large bore center",
                 bx, by, z_large_mid,
                 f"void at bore {label} axis, Z={z_large_mid:.2f} (large bore mid-depth)")

    # Feature: narrow bore exists — probe at bore axis, mid-depth of narrow bore (Z~=+13.5)
    z_narrow_mid = (DEPTH_NARROW_START + DEPTH_NARROW_END) / 2   # 13.54 mm
    v.check_void(f"Bore {label} narrow bore center",
                 bx, by, z_narrow_mid,
                 f"void at bore {label} axis, Z={z_narrow_mid:.2f} (narrow bore mid-depth)")

    # Bore orientation check: probe at a point that would be SOLID if bore ran in X or Y
    # If the bore ran along X (wrong), then point (bx, by, 6) might be solid.
    # We already checked void at (bx, by, z_large_mid) — that verifies Z orientation.
    # Extra: check that a point laterally offset but within large bore radius is void
    v.check_void(f"Bore {label} large bore lateral void",
                 bx + R_LARGE - 0.5, by, z_large_mid,
                 f"void at R={R_LARGE-0.5:.2f} inside large bore radius, Z={z_large_mid:.2f}")

    # Check annular ring between large and narrow bore at narrow-bore depth:
    # At Z=z_narrow_mid (inside narrow bore stage), R > R_NARROW should be SOLID
    # (the bore shoulder and plate material block that zone).
    # Probe at radius midway between narrow and large bore walls: (R_NARROW + R_LARGE)/2
    r_annular = (R_NARROW + R_LARGE) / 2   # (4.75 + 7.75)/2 = 6.25 mm
    # Use +X offset from bore center
    v.check_solid(f"Bore {label} shoulder material",
                  bx + r_annular, by, z_narrow_mid,
                  f"solid in annular shoulder zone at R={r_annular:.2f}, Z={z_narrow_mid:.2f}")

    # Path continuity: probe both sides of the large→narrow transition at Z=+12.08
    # Both probes should be void (the bore passes through the step)
    z_trans = DEPTH_LARGE   # 12.08 mm
    v.check_void(f"Bore {label} transition Z-0.1 (large side)",
                 bx, by, z_trans - 0.1,
                 f"void just inside large bore at Z={z_trans-0.1:.2f} (step approach)")
    v.check_void(f"Bore {label} transition Z+0.1 (narrow side)",
                 bx, by, z_trans + 0.1,
                 f"void just inside narrow bore at Z={z_trans+0.1:.2f} (step exit)")

    # Narrow bore exits far face: probe just inside narrow bore at Z=+14.9
    v.check_void(f"Bore {label} far face exit",
                 bx, by, PLATE_D - 0.1,
                 f"void at bore {label} axis, Z={PLATE_D-0.1:.1f} (near far face)")

    # Verify material exists BETWEEN bores in the plate body:
    # Only do this for bore A (check between A and C, between A and B)
    if label == "A":
        # Between bore A (X=-31) and bore C (X=+31), at bore A Y level, mid-depth
        v.check_solid("Between bores A and C (plate center strip)",
                      0.0, by, z_large_mid,
                      f"solid at X=0, Y={by}, Z={z_large_mid:.2f} (between A and C bores)")
        # Between bore A (Y=+15) and bore B (Y=-15), at bore A X position, mid-depth
        v.check_solid("Between bores A and B (plate vertical strip)",
                      bx, 0.0, z_large_mid,
                      f"solid at X={bx}, Y=0, Z={z_large_mid:.2f} (between A and B bores)")

# --- Feature 10: Elephant's foot chamfers — check void just inside chamfer region ---
print()
print("--- Feature 10: Elephant's foot chamfers at Z=0 ---")
for bore_idx, (bx, by) in enumerate(BORE_CENTERS):
    label = bore_labels[bore_idx]
    # The chamfer occupies: at Z=0, from R=(R_LARGE - 0.3) to R=R_LARGE
    #                       at Z=0.3, at R=R_LARGE (the chamfer apex)
    # Probe the chamfer interior: just inside the chamfer face.
    # At Z=0.15 (halfway through chamfer depth), chamfer radius at this Z:
    #   chamfer goes from (R_LARGE-0.3, Z=0) to (R_LARGE, Z=0.3)
    #   at Z=0.15: chamfer edge is at R = R_LARGE - 0.3 + 0.15 = R_LARGE - 0.15
    # A point at R = R_LARGE - 0.10 and Z=0.05 should be VOID (inside chamfer/bore)
    # (within bore cavity, below the chamfer hypotenuse)
    z_champ = 0.05
    r_champ = R_LARGE - 0.10    # inside the chamfer zone, near Z=0
    v.check_void(f"Bore {label} chamfer void at Z={z_champ}",
                 bx + r_champ, by, z_champ,
                 f"void at chamfer interior (R={r_champ:.2f}, Z={z_champ}) — chamfer removes material at bore rim")

    # Verify solid material just outside large bore radius at Z=0.05
    # (to confirm bore didn't cut through walls)
    r_outside = R_LARGE + 0.5    # just outside large bore, within plate wall
    # Only check if this point is within the plate boundary
    if abs(bx) + r_outside < PLATE_W/2 - 0.1 and abs(by) + r_outside < PLATE_H/2 - 0.1:
        v.check_solid(f"Bore {label} wall outside chamfer",
                      bx + r_outside, by, z_champ,
                      f"solid just outside large bore rim (R={r_outside:.2f}, Z={z_champ})")

# --- Bounding box (Rubric 5) ---
print()
print("--- Bounding box (Rubric 5) ---")
bb = plate.val().BoundingBox()
print(f"  Actual bounding box:")
print(f"    X: [{bb.xmin:.3f}, {bb.xmax:.3f}]  (expected [−40, +40])")
print(f"    Y: [{bb.ymin:.3f}, {bb.ymax:.3f}]  (expected [−25, +25])")
print(f"    Z: [{bb.zmin:.3f}, {bb.zmax:.3f}]  (expected [0, +15])")

# The chamfer at Z=0 may move zmin slightly above 0 — allow small tolerance
v.check_bbox("X", bb.xmin, bb.xmax, -PLATE_W/2, +PLATE_W/2, tol=0.5)
v.check_bbox("Y", bb.ymin, bb.ymax, -PLATE_H/2, +PLATE_H/2, tol=0.5)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, PLATE_D, tol=0.5)

# --- Solid integrity (Rubric 4) ---
print()
print("--- Solid integrity (Rubric 4) ---")
v.check_valid()
v.check_single_body()

# Volume estimate:
# Plate body: 80 × 50 × 15 = 60000 mm³
# 4 large bores: 4 × π × 7.75² × 12.08 ≈ 4 × 2278 ≈ 9112 mm³
# 4 narrow bores: 4 × π × 4.75² × 2.92 ≈ 4 × 207 ≈ 829 mm³
# 4 chamfers (approx cones, small): ~negligible
# Total removal: ~9941 mm³
# Net estimated volume: ~60000 - 9941 ≈ 50059 mm³
# Envelope: 80 × 50 × 15 = 60000 mm³
# Fill ratio: 50059 / 60000 ≈ 83.4%
v.check_volume(expected_envelope=PLATE_W * PLATE_H * PLATE_D,
               fill_range=(0.70, 0.95))

print()
passed = v.summary()

if not passed:
    print()
    print("FAIL: Validation failures detected. Exiting without writing STEP file.")
    sys.exit(1)

# ==============================================================================
# Export STEP
# ==============================================================================

output_path = Path(__file__).parent / "coupler-tray-cadquery.step"
cq.exporters.export(plate, str(output_path))
print()
print(f"SUCCESS: STEP file written to:")
print(f"  {output_path}")
print("Done.")
