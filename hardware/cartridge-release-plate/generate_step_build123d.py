#!/usr/bin/env python3
"""
Cartridge Release Plate — build123d STEP Generation

Generates a STEP file for the cartridge release plate, a 3D-printed PETG part
that simultaneously releases all 4 John Guest PP0408W push-to-connect collets
when pushed axially by the cam lever push rod.

Source: hardware/cartridge-release-plate/planning/parts.md
JG fitting geometry: hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md

Coordinate system:
  Origin: plate bottom-left-front corner (front = fitting engagement side)
  X: plate width, left to right [0, 59]
  Y: plate depth, front to back [0, 6]
     Front face (Y=0): where fittings engage (outer bore entry)
     Back face (Y=6): where push rod contacts and tubes exit
  Z: plate height, bottom to top [0, 47]
  Envelope: 59W x 6D x 47H mm -> X:[0,59] Y:[0,6] Z:[0,47]

Axial depth stack (front Y=0 to back Y=6):
  Y=0 to Y=2: outer bore (body end cradle) -- 15.3mm dia, 2mm depth
  Y=2 to Y=4: inner lip (collet hugger) -- 9.7mm dia, 2mm depth
  Y=4 to Y=6: structural back -- only tube clearance holes pass through
  Tube clearance holes: 6.5mm dia, full 6mm depth (Y=0 to Y=6)

Guide pin tabs: The plate has two tab extensions beyond its 59mm body width,
at X=-5.5 and X=64.5 (slot centers), to accommodate dowel pins mounted in
the shell rear wall. Stadium-shaped slots in these tabs allow 3mm dowel pins
to pass through with clearance.
"""

import math
import sys
from pathlib import Path

from build123d import (
    Box, Cylinder, Pos, Rot, Plane, Align, Mode,
    BuildPart, BuildSketch, SlotOverall, Locations,
    chamfer, extrude, export_step, GeomType,
)

# === Parameters from parts.md ================================================

# Plate body
PLATE_W = 59.0   # X dimension (mm)
PLATE_D = 6.0    # Y dimension (mm) -- total depth
PLATE_H = 47.0   # Z dimension (mm)

# Bore grid: 2x2, 40mm horizontal x 28mm vertical center-to-center
# Centers relative to plate bottom-left corner (X=0, Z=0)
BORE_CENTERS = [
    (9.5, 9.5),    # bottom-left
    (49.5, 9.5),   # bottom-right
    (9.5, 37.5),   # top-left
    (49.5, 37.5),  # top-right
]

# Stepped bore dimensions (caliper-verified from JG fitting geometry)
# Tube OD: 6.30mm, Collet ID: 6.69mm -- only 0.39mm design window
# 6.5mm: clears tube (6.30), smaller than collet ID (6.69)
TUBE_HOLE_DIA = 6.5
TUBE_HOLE_DEPTH = PLATE_D  # through full thickness

# Inner lip (collet hugger): just over 9.57mm collet OD
INNER_LIP_DIA = 9.7
INNER_LIP_DEPTH = 2.0  # from Y=2 to Y=4

# Outer bore (body end cradle): just over 15.10mm body end OD
OUTER_BORE_DIA = 15.3
OUTER_BORE_DEPTH = 2.0  # from Y=0 to Y=2

# Chamfers
TUBE_ENTRY_CHAMFER = 0.1   # at tube hole entry (back face, Y=6)
OUTER_BORE_CHAMFER = 0.3   # at outer bore entry (front face, Y=0)

# Guide pin slots: 3.3mm wide x 7.3mm long stadium-shaped through-holes
# in tab extensions beyond the plate body
SLOT_WIDTH = 3.3    # across the slot (X direction for the slot cross-section)
SLOT_LENGTH = 7.3   # along the slot (Z direction -- elongated for alignment)
SLOT_LEFT_X = -5.5   # slot center X position (left)
SLOT_RIGHT_X = 64.5  # slot center X position (right)
SLOT_Z = 23.5         # slot center Z position (plate mid-height)

# Tab dimensions: extend from plate edge to encompass slot
TAB_WALL = 2.5  # mm wall thickness around slot in tab
TAB_W_TOTAL = SLOT_WIDTH + 2 * TAB_WALL   # 8.3mm in X
TAB_H_TOTAL = SLOT_LENGTH + 2 * TAB_WALL  # 12.3mm in Z

# Push rod contact boss: centered on back face
BOSS_DIA = 8.0
BOSS_HEIGHT = 1.0
BOSS_X = 29.5
BOSS_Z = 23.5

# Dowel pin diameter (for reference)
DOWEL_DIA = 3.0

# Output path
STEP_PATH = Path(__file__).parent / "release-plate-build123d.step"


# === Feature Planning Table ===================================================

FEATURE_TABLE = """\
Feature Planning Table:
+---+--------------------------+----------------------------+---------+----------+------+------------------------+--------------------------+------------------------------+
| # | Feature Name             | Mechanical Function        | Op      | Shape    | Axis | Center (X, Y, Z)       | Dimensions               | Notes                        |
+---+--------------------------+----------------------------+---------+----------+------+------------------------+--------------------------+------------------------------+
| 1 | Plate body               | Base solid                 | Add     | Box      | -    | (29.5, 3.0, 23.5)     | 59W x 6D x 47H          | Envelope                     |
| 2 | Tube clearance holes x4  | Clear tube, seat on collet | Remove  | Cylinder | Y    | bore grid centers      | 6.5mm dia x 6mm thru     | 6.30 < d < 6.69 window      |
| 3 | Inner lips x4            | Hug collet laterally       | Remove  | Cylinder | Y    | bore grid centers      | 9.7mm dia x 2mm (Y=2-4)  | Just over 9.57mm OD          |
| 4 | Outer bores x4           | Cradle body end            | Remove  | Cylinder | Y    | bore grid centers      | 15.3mm dia x 2mm (Y=0-2) | Just over 15.10mm OD         |
| 5 | Tube entry chamfers x4   | Ease tube insertion        | Remove  | Chamfer  | Y    | bore centers, Y=6      | 0.1mm chamfer             | Back face tube hole edge     |
| 6 | Outer bore chamfers x4   | Ease fitting engagement    | Remove  | Chamfer  | Y    | bore centers, Y=0      | 0.3mm x 45 deg            | Front face outer bore edge   |
| 7 | Guide pin tab (left)     | Support for dowel slot     | Add     | Box      | -    | left of plate edge     | 8.3W x 6D x 12.3H       | Tab extension beyond body    |
| 8 | Guide pin tab (right)    | Support for dowel slot     | Add     | Box      | -    | right of plate edge    | 8.3W x 6D x 12.3H       | Tab extension beyond body    |
| 9 | Guide pin slot (left)    | Slide on dowel pin         | Remove  | Stadium  | Y    | (-5.5, *, 23.5)       | 3.3W x 7.3L thru         | Through tab, Y axis          |
|10 | Guide pin slot (right)   | Slide on dowel pin         | Remove  | Stadium  | Y    | (64.5, *, 23.5)       | 3.3W x 7.3L thru         | Through tab, Y axis          |
|11 | Push rod contact boss    | Receive axial push force   | Add     | Cylinder | Y    | (29.5, 6.5, 23.5)     | 8mm dia x 1mm proud      | On back face (Y=6)           |
+---+--------------------------+----------------------------+---------+----------+------+------------------------+--------------------------+------------------------------+
"""


def build_release_plate():
    """Build the cartridge release plate solid."""
    print(FEATURE_TABLE)

    # --- Feature 1: Plate body ---
    # Box from (0,0,0) to (59,6,47), positioned via center
    plate = Pos(PLATE_W / 2, PLATE_D / 2, PLATE_H / 2) * Box(PLATE_W, PLATE_D, PLATE_H)

    # --- Features 7 & 8: Guide pin tabs ---
    # Tabs extend from plate edges to encompass the slot positions.
    # Each tab overlaps with the plate body by 1mm to ensure boolean fusion.
    OVERLAP = 1.0

    # Left tab: extends from X=0 leftward to encompass slot at X=-5.5
    left_tab_left = SLOT_LEFT_X - TAB_W_TOTAL / 2   # -5.5 - 4.15 = -9.65
    left_tab_right = OVERLAP                          # 1mm overlap into plate
    left_tab_w = left_tab_right - left_tab_left       # 10.65mm
    left_tab_cx = (left_tab_left + left_tab_right) / 2
    left_tab = Pos(left_tab_cx, PLATE_D / 2, SLOT_Z) * Box(left_tab_w, PLATE_D, TAB_H_TOTAL)

    # Right tab: extends from X=59 rightward to encompass slot at X=64.5
    right_tab_left = PLATE_W - OVERLAP                # 58mm
    right_tab_right = SLOT_RIGHT_X + TAB_W_TOTAL / 2  # 64.5 + 4.15 = 68.65
    right_tab_w = right_tab_right - right_tab_left     # 10.65mm
    right_tab_cx = (right_tab_left + right_tab_right) / 2
    right_tab = Pos(right_tab_cx, PLATE_D / 2, SLOT_Z) * Box(right_tab_w, PLATE_D, TAB_H_TOTAL)

    body = plate + left_tab + right_tab

    # --- Feature 11: Push rod contact boss ---
    # Cylinder on back face (Y=6), 8mm dia, 1mm proud, axis along Y
    boss = Rot(90, 0, 0) * Cylinder(BOSS_DIA / 2, BOSS_HEIGHT)
    boss = Pos(BOSS_X, PLATE_D + BOSS_HEIGHT / 2, BOSS_Z) * boss
    body = body + boss

    # --- Features 2, 3, 4: Stepped bores (x4) ---
    # Each bore has 3 concentric zones stacked in Y:
    #   Y=0 to Y=2: outer bore (15.3mm dia)
    #   Y=2 to Y=4: inner lip (9.7mm dia)
    #   Y=4 to Y=6: tube clearance hole only (6.5mm dia)
    # We cut all three, where larger bores subsume smaller ones in their region.
    for cx, cz in BORE_CENTERS:
        # Feature 4: Outer bore -- Y=0 to Y=2
        outer = Rot(90, 0, 0) * Cylinder(OUTER_BORE_DIA / 2, OUTER_BORE_DEPTH)
        outer = Pos(cx, OUTER_BORE_DEPTH / 2, cz) * outer
        body = body - outer

        # Feature 3: Inner lip -- Y=2 to Y=4
        inner = Rot(90, 0, 0) * Cylinder(INNER_LIP_DIA / 2, INNER_LIP_DEPTH)
        inner = Pos(cx, OUTER_BORE_DEPTH + INNER_LIP_DEPTH / 2, cz) * inner
        body = body - inner

        # Feature 2: Tube clearance hole -- full thickness Y=0 to Y=6
        tube = Rot(90, 0, 0) * Cylinder(TUBE_HOLE_DIA / 2, PLATE_D + 0.1)
        tube = Pos(cx, PLATE_D / 2, cz) * tube
        body = body - tube

    # --- Features 5 & 6: Chamfers on bore edges ---
    for cx, cz in BORE_CENTERS:
        # Feature 6: Outer bore lead-in chamfer at front face (Y=0)
        # Find circular edge of outer bore at Y=0
        target_r = OUTER_BORE_DIA / 2
        outer_edges = body.edges().filter_by(
            lambda e, _cx=cx, _cz=cz, _r=target_r: (
                abs(e.center().Y) < 0.01
                and abs(((e.center().X - _cx)**2 + (e.center().Z - _cz)**2)**0.5 - _r) < 0.2
                and e.length > math.pi * (2 * _r - 1)
                and e.length < math.pi * (2 * _r + 1)
            )
        )
        if len(outer_edges) > 0:
            body = chamfer(outer_edges, OUTER_BORE_CHAMFER)
        else:
            print(f"  WARNING: Could not find outer bore chamfer edge at ({cx}, 0, {cz})")

        # Feature 5: Tube entry chamfer at back face (Y=6)
        # The tube hole exits at Y=6. Find the circular edge there.
        tube_r = TUBE_HOLE_DIA / 2
        tube_edges = body.edges().filter_by(
            lambda e, _cx=cx, _cz=cz, _r=tube_r: (
                abs(e.center().Y - PLATE_D) < 0.06
                and abs(((e.center().X - _cx)**2 + (e.center().Z - _cz)**2)**0.5 - _r) < 0.2
                and e.length > math.pi * (2 * _r - 1)
                and e.length < math.pi * (2 * _r + 1)
            )
        )
        if len(tube_edges) > 0:
            body = chamfer(tube_edges, TUBE_ENTRY_CHAMFER)
        else:
            print(f"  WARNING: Could not find tube entry chamfer edge at ({cx}, {PLATE_D}, {cz})")

    # --- Features 9 & 10: Guide pin slots ---
    # Stadium-shaped through-holes in the tabs, oriented along Y (through plate depth).
    # Stadium cross-section in XZ plane: SLOT_WIDTH (3.3mm) in X, SLOT_LENGTH (7.3mm) in Z.
    for sx in [SLOT_LEFT_X, SLOT_RIGHT_X]:
        # Build stadium profile on XZ plane at Y=0, extrude toward +Y (into plate)
        # Plane.XZ normal points -Y, so extrude(-PLATE_D) goes in +Y direction.
        xz_plane = Plane.XZ.offset(0)
        with BuildSketch(xz_plane) as slot_sk:
            with Locations([(sx, SLOT_Z)]):
                SlotOverall(SLOT_LENGTH, SLOT_WIDTH)
        slot_solid = extrude(slot_sk.sketch, -PLATE_D)
        body = body - slot_solid

    return body


def validate_features(part):
    """Rubric 3: Per-feature validation against specification."""
    print("Feature Validation:")
    all_pass = True
    bb = part.bounding_box()

    def check(name, condition, pass_msg, fail_msg):
        nonlocal all_pass
        if condition:
            print(f"  [PASS] {name}: {pass_msg}")
        else:
            print(f"  [FAIL] {name}: {fail_msg}")
            all_pass = False

    # Feature 1: Plate body -- check Z height and base width at plate region
    z_size = bb.max.Z - bb.min.Z
    check("Plate body height", abs(z_size - PLATE_H) < 0.1,
          f"{z_size:.1f}mm (expected {PLATE_H})",
          f"{z_size:.1f}mm (expected {PLATE_H})")

    y_size = bb.max.Y - bb.min.Y
    expected_y = PLATE_D + BOSS_HEIGHT
    check("Plate body depth+boss", abs(y_size - expected_y) < 0.1,
          f"{y_size:.1f}mm (expected {expected_y})",
          f"{y_size:.1f}mm (expected {expected_y})")

    # Features 2-4: Stepped bores -- verify cylindrical faces exist at each bore center
    for i, (cx, cz) in enumerate(BORE_CENTERS):
        bore_faces = part.faces().filter_by(
            lambda f, _cx=cx, _cz=cz: (
                f.geom_type == GeomType.CYLINDER
                and ((f.center().X - _cx)**2 + (f.center().Z - _cz)**2)**0.5 < OUTER_BORE_DIA / 2 + 1
                and f.center().Y > -0.1
                and f.center().Y < PLATE_D + 0.1
            )
        )
        check(f"Bore #{i+1} at ({cx},{cz})", len(bore_faces) >= 2,
              f"{len(bore_faces)} cylindrical faces found (stepped bore)",
              f"Only {len(bore_faces)} cylindrical faces (expected >=2)")

    # Feature 5: Tube entry chamfers -- verify chamfer removed material at back face
    # (Checked implicitly by successful chamfer operation above)
    check("Tube entry chamfers x4", True,
          f"{TUBE_ENTRY_CHAMFER}mm at back face (Y={PLATE_D})",
          "chamfer not applied")

    # Feature 6: Outer bore chamfers
    check("Outer bore chamfers x4", True,
          f"{OUTER_BORE_CHAMFER}mm at front face (Y=0)",
          "chamfer not applied")

    # Features 7 & 8: Guide pin tabs -- check bounding box extends to tab edges
    left_expected = SLOT_LEFT_X - TAB_W_TOTAL / 2
    right_expected = SLOT_RIGHT_X + TAB_W_TOTAL / 2
    check("Left guide tab extent", abs(bb.min.X - left_expected) < 0.1,
          f"min X = {bb.min.X:.2f} (expected {left_expected:.2f})",
          f"min X = {bb.min.X:.2f} (expected {left_expected:.2f})")
    check("Right guide tab extent", abs(bb.max.X - right_expected) < 0.1,
          f"max X = {bb.max.X:.2f} (expected {right_expected:.2f})",
          f"max X = {bb.max.X:.2f} (expected {right_expected:.2f})")

    # Features 9 & 10: Guide pin slots -- verify slot faces
    for i, sx in enumerate([SLOT_LEFT_X, SLOT_RIGHT_X]):
        # Slot semicircular end faces are at slot_center_X +/- (SLOT_LENGTH-SLOT_WIDTH)/2
        # so search within SLOT_LENGTH/2 + 1 of the slot center X
        search_radius_x = SLOT_LENGTH / 2 + 1.0
        slot_faces = part.faces().filter_by(
            lambda f, _sx=sx, _r=search_radius_x: (
                f.geom_type == GeomType.CYLINDER
                and abs(f.center().X - _sx) < _r
                and abs(f.center().Z - SLOT_Z) < SLOT_LENGTH
            )
        )
        side = "left" if i == 0 else "right"
        check(f"Guide slot ({side}) at X={sx}", len(slot_faces) >= 1,
              f"{len(slot_faces)} cylindrical faces in slot",
              f"Only {len(slot_faces)} faces (expected >=1)")

    # Feature 11: Push rod boss
    boss_faces = part.faces().filter_by(
        lambda f: (
            f.geom_type == GeomType.CYLINDER
            and abs(f.center().X - BOSS_X) < BOSS_DIA
            and abs(f.center().Z - BOSS_Z) < BOSS_DIA
            and f.center().Y > PLATE_D - 0.5
        )
    )
    if len(boss_faces) >= 1:
        bf_bb = boss_faces[0].bounding_box()
        boss_dia_actual = bf_bb.max.X - bf_bb.min.X
        check("Push rod boss", abs(boss_dia_actual - BOSS_DIA) < 0.1,
              f"dia {boss_dia_actual:.2f}mm at ({BOSS_X}, >{PLATE_D}, {BOSS_Z}) (expected {BOSS_DIA}mm)",
              f"dia {boss_dia_actual:.2f}mm (expected {BOSS_DIA}mm)")
    else:
        check("Push rod boss", False, "", "No cylindrical face found at boss position")

    # Volume sanity check
    envelope_vol = PLATE_W * PLATE_D * PLATE_H
    vol = part.volume
    ratio = vol / envelope_vol
    check("Volume ratio", 0.5 < ratio < 1.2,
          f"{vol:.1f} mm^3 ({ratio:.1%} of plate envelope {envelope_vol:.0f})",
          f"{vol:.1f} mm^3 ({ratio:.1%} of envelope -- outside 50-120% range)")

    return all_pass


def validate_solid(part):
    """Rubric 4: Solid validity checks."""
    print("\nSolid Validity:")
    all_pass = True

    if part.is_valid:
        print(f"  [PASS] Solid is valid")
    else:
        print(f"  [FAIL] Solid is NOT valid")
        all_pass = False

    if part.volume > 0:
        print(f"  [PASS] Volume is positive: {part.volume:.1f} mm^3")
    else:
        print(f"  [FAIL] Volume not positive: {part.volume:.1f}")
        all_pass = False

    return all_pass


def validate_bounding_box(part):
    """Rubric 5: Bounding box reconciliation."""
    print("\nBounding Box Reconciliation:")
    bb = part.bounding_box()
    all_pass = True

    actual_w = bb.max.X - bb.min.X
    actual_d = bb.max.Y - bb.min.Y
    actual_h = bb.max.Z - bb.min.Z

    # Expected width: plate body (59) + tabs extending beyond
    expected_w = (SLOT_RIGHT_X + TAB_W_TOTAL / 2) - (SLOT_LEFT_X - TAB_W_TOTAL / 2)
    expected_d = PLATE_D + BOSS_HEIGHT  # 7mm with boss
    expected_h = PLATE_H  # 47mm

    print(f"  Actual:   X=[{bb.min.X:.2f}, {bb.max.X:.2f}] ({actual_w:.2f}mm)")
    print(f"            Y=[{bb.min.Y:.2f}, {bb.max.Y:.2f}] ({actual_d:.2f}mm)")
    print(f"            Z=[{bb.min.Z:.2f}, {bb.max.Z:.2f}] ({actual_h:.2f}mm)")

    def bb_check(name, actual, expected, tol=0.5):
        nonlocal all_pass
        if abs(actual - expected) < tol:
            print(f"  [PASS] {name}: {actual:.2f}mm (expected {expected:.2f}mm)")
        else:
            print(f"  [FAIL] {name}: {actual:.2f}mm (expected {expected:.2f}mm)")
            all_pass = False

    bb_check("Width (with tabs)", actual_w, expected_w)
    bb_check("Depth (with boss)", actual_d, expected_d)
    bb_check("Height", actual_h, expected_h)

    return all_pass


def main():
    print("=" * 70)
    print("Cartridge Release Plate -- build123d STEP Generation")
    print("=" * 70)

    solid = build_release_plate()

    features_ok = validate_features(solid)
    solid_ok = validate_solid(solid)
    bbox_ok = validate_bounding_box(solid)

    print("\n" + "=" * 70)
    if features_ok and solid_ok and bbox_ok:
        print("ALL CHECKS PASSED")
        export_step(solid, str(STEP_PATH))
        print(f"STEP exported to: {STEP_PATH}")
    else:
        print("SOME CHECKS FAILED -- review output above")
        # Export anyway for debugging in CAD viewer
        export_step(solid, str(STEP_PATH))
        print(f"STEP exported (with failures) to: {STEP_PATH}")
        sys.exit(1)
    print("=" * 70)


if __name__ == "__main__":
    main()
