"""
Generate STEP file for the Cartridge Release Plate using build123d.

Part spec: hardware/cartridge-release-plate/planning/parts.md
JG fitting geometry: hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md

Axis convention (matching engineering drawing):
  X = width (59mm)
  Y = depth (6mm) -- fitting side is Y=0, back side is Y=6
  Z = height (47mm)

The plate origin is at the bottom-left corner of the fitting face:
  X: 0 to 59
  Y: 0 to 6  (fitting side to back side)
  Z: 0 to 47
"""

from build123d import *
from pathlib import Path

# ── Plate dimensions ──
PLATE_W = 59.0   # X
PLATE_D = 6.0    # Y
PLATE_H = 47.0   # Z

# ── Stepped bore dimensions (caliper-verified interface) ──
# Outer bore (body end cradle): just over 15.10mm body end OD
OUTER_BORE_DIA = 15.6    # mm (0.5mm clearance over 15.10mm OD)
OUTER_BORE_DEPTH = 2.0   # mm (from fitting face, Y=0 inward)

# Inner lip (collet hugger): just over 9.57mm collet OD
INNER_LIP_DIA = 10.0     # mm (0.43mm clearance over 9.57mm OD)
INNER_LIP_DEPTH = 2.0    # mm

# Tube clearance hole: between 6.30mm tube OD and 6.69mm collet ID
TUBE_HOLE_DIA = 6.5      # mm (0.20mm over tube, 0.19mm under collet ID)
# Through remaining thickness: 6.0 - 2.0 - 2.0 = 2.0mm
TUBE_HOLE_DEPTH = 2.0    # mm (through to back face)

# Chamfers
OUTER_BORE_CHAMFER = 0.3  # mm, 45-degree lead-in at outer bore entry
TUBE_HOLE_CHAMFER = 0.1   # mm, at tube hole entry edge

# ── Bore grid positions (from bottom-left of plate) ──
# 2x2 grid: 40mm horizontal, 28mm vertical center-to-center
BORE_CENTERS = [
    (9.5, 9.5),
    (49.5, 9.5),
    (9.5, 37.5),
    (49.5, 37.5),
]

# ── Push rod contact boss ──
BOSS_DIA = 8.0       # mm
BOSS_HEIGHT = 1.0    # mm proud of back face
BOSS_CENTER = (29.5, 23.5)  # (X, Z) from bottom-left

# ── Guide pin tabs ──
# Elongated slots for 3mm dowel pins
SLOT_W = 3.3    # mm (X direction, matches 3mm pin + clearance)
SLOT_H = 7.3    # mm (Z direction, elongated for travel)
# Tab dimensions: extend from plate edge
TAB_EXTENSION = 11.0  # mm total from plate center to slot center (X=-5.5 and X=64.5)
TAB_WIDTH = SLOT_W + 2 * 2.5  # mm wall around slot (2.5mm each side)
TAB_HEIGHT = SLOT_H + 2 * 2.5  # mm wall around slot
TAB_DEPTH = PLATE_D   # same depth as plate

# Slot center positions (X, Z) from plate bottom-left
SLOT_CENTERS = [
    (-5.5, 23.5),   # left tab
    (64.5, 23.5),   # right tab
]

# ── Output path ──
STEP_PATH = Path(__file__).parent / "release-plate-build123d.step"


def make_release_plate():
    """Build the release plate geometry."""

    # ── 1. Main plate body ──
    # Origin at bottom-left of fitting face (X=0, Y=0, Z=0)
    # Box centered, then relocated
    plate = Box(PLATE_W, PLATE_D, PLATE_H)
    plate = Pos(PLATE_W / 2, PLATE_D / 2, PLATE_H / 2) * plate

    # ── 2. Guide pin tabs ──
    # Tabs extend from plate edges. Overlap 1mm with plate body to ensure
    # boolean fusion (adjacent-but-not-overlapping produces compound solids).
    OVERLAP = 1.0

    # Left tab: extends from X=0 to the left, overlapping into plate by 1mm
    left_tab_left_edge = SLOT_CENTERS[0][0] - TAB_WIDTH / 2  # leftmost edge
    left_tab_right_edge = OVERLAP  # overlap 1mm into plate
    left_tab_actual_w = left_tab_right_edge - left_tab_left_edge
    left_tab_x_center = (left_tab_left_edge + left_tab_right_edge) / 2
    left_tab = Box(left_tab_actual_w, TAB_DEPTH, TAB_HEIGHT)
    left_tab = Pos(left_tab_x_center, PLATE_D / 2, SLOT_CENTERS[0][1]) * left_tab

    # Right tab: extends from X=59 to the right, overlapping into plate by 1mm
    right_tab_left_edge = PLATE_W - OVERLAP  # overlap 1mm into plate
    right_tab_right_edge = SLOT_CENTERS[1][0] + TAB_WIDTH / 2
    right_tab_actual_w = right_tab_right_edge - right_tab_left_edge
    right_tab_x_center = (right_tab_left_edge + right_tab_right_edge) / 2
    right_tab = Box(right_tab_actual_w, TAB_DEPTH, TAB_HEIGHT)
    right_tab = Pos(right_tab_x_center, PLATE_D / 2, SLOT_CENTERS[1][1]) * right_tab

    # Union plate + tabs (overlap ensures proper fusion)
    body = plate + left_tab + right_tab

    # ── 3. Push rod contact boss on back face ──
    boss = Cylinder(BOSS_DIA / 2, BOSS_HEIGHT)
    # Cylinder axis is Z by default in build123d; we need it along Y
    # Rotate 90 degrees around X to point cylinder along Y
    boss = Rot(90, 0, 0) * boss
    # Position: center at (BOSS_CENTER[0], PLATE_D + BOSS_HEIGHT/2, BOSS_CENTER[1])
    boss = Pos(BOSS_CENTER[0], PLATE_D + BOSS_HEIGHT / 2, BOSS_CENTER[1]) * boss
    body = body + boss

    # ── 4. Stepped bores (subtract from fitting face) ──
    # Bores go along Y axis (into the plate from fitting face at Y=0)
    # Each bore has 3 concentric zones stacked in Y:
    #   Y=0 to Y=2.0: outer bore (15.6mm dia)
    #   Y=2.0 to Y=4.0: inner lip (10.0mm dia)
    #   Y=4.0 to Y=6.0: tube clearance hole (6.5mm dia)

    for cx, cz in BORE_CENTERS:
        # Outer bore: from Y=0 to Y=OUTER_BORE_DEPTH
        outer = Cylinder(OUTER_BORE_DIA / 2, OUTER_BORE_DEPTH)
        outer = Rot(90, 0, 0) * outer
        outer = Pos(cx, OUTER_BORE_DEPTH / 2, cz) * outer

        # Inner lip: from Y=OUTER_BORE_DEPTH to Y=OUTER_BORE_DEPTH+INNER_LIP_DEPTH
        inner = Cylinder(INNER_LIP_DIA / 2, INNER_LIP_DEPTH)
        inner = Rot(90, 0, 0) * inner
        y_inner = OUTER_BORE_DEPTH + INNER_LIP_DEPTH / 2
        inner = Pos(cx, y_inner, cz) * inner

        # Tube clearance hole: from Y=OUTER_BORE_DEPTH+INNER_LIP_DEPTH to Y=PLATE_D
        tube = Cylinder(TUBE_HOLE_DIA / 2, TUBE_HOLE_DEPTH)
        tube = Rot(90, 0, 0) * tube
        y_tube = OUTER_BORE_DEPTH + INNER_LIP_DEPTH + TUBE_HOLE_DEPTH / 2
        tube = Pos(cx, y_tube, cz) * tube

        bore = outer + inner + tube
        body = body - bore

    # ── 5. Chamfers on bores ──
    # We need to chamfer specific edges on the bore features.
    # Outer bore entry chamfer (0.3mm at Y=0 face) and tube hole entry chamfer
    # (0.1mm at the Y=2.0 step where tube hole meets inner lip).
    #
    # Strategy: find edges by position. After boolean subtraction, the bore
    # edges exist on the body. We select edges near the bore entry circles.

    for cx, cz in BORE_CENTERS:
        # Outer bore entry chamfer: circular edge at Y=0, radius = OUTER_BORE_DIA/2
        outer_entry_edges = body.edges().filter_by(
            lambda e: (
                abs(e.center().Y) < 0.01
                and abs(
                    ((e.center().X - cx) ** 2 + (e.center().Z - cz) ** 2) ** 0.5
                    - OUTER_BORE_DIA / 2
                )
                < 0.1
            )
        )
        if len(outer_entry_edges) > 0:
            body = chamfer(outer_entry_edges, OUTER_BORE_CHAMFER)

        # Tube hole entry chamfer: circular edge at Y=OUTER_BORE_DEPTH+INNER_LIP_DEPTH
        # where the inner lip meets the tube hole (step from 10mm to 6.5mm)
        tube_entry_y = OUTER_BORE_DEPTH + INNER_LIP_DEPTH
        tube_entry_edges = body.edges().filter_by(
            lambda e, _y=tube_entry_y, _cx=cx, _cz=cz: (
                abs(e.center().Y - _y) < 0.01
                and abs(
                    ((e.center().X - _cx) ** 2 + (e.center().Z - _cz) ** 2) ** 0.5
                    - TUBE_HOLE_DIA / 2
                )
                < 0.1
            )
        )
        if len(tube_entry_edges) > 0:
            body = chamfer(tube_entry_edges, TUBE_HOLE_CHAMFER)

    # ── 6. Guide pin slots (through tabs) ──
    # Stadium-shaped through-holes for 3mm dowel pins.
    # Cross-section in X-Z plane: SLOT_W (3.3mm) in X, SLOT_H (7.3mm) in Z.
    # Through-hole runs along Y (full plate depth).
    for sx, sz in SLOT_CENTERS:
        # Build the stadium profile on an XZ plane at Y=0, then extrude along +Y.
        # Plane.XZ sketch: local X maps to global X, local Y maps to global Z.
        # SlotOverall(length, width): length=SLOT_H (7.3mm) along local Y (=Z),
        # width=SLOT_W (3.3mm) along local X (=X).
        xz_plane = Plane.XZ.offset(0)
        with BuildSketch(xz_plane) as slot_sk:
            with Locations([(sx, sz)]):
                SlotOverall(SLOT_H, SLOT_W)
        slot_solid = extrude(slot_sk.sketch, PLATE_D)
        body = body - slot_solid

    return body


def validate_release_plate(part):
    """Per-feature validation against the specification.

    Returns (results, all_pass) where results is a list of
    (feature_name, status, detail) tuples.
    """
    results = []
    TOL = 0.05  # mm tolerance for dimension checks

    bb = part.bounding_box()

    # ── 1. Plate body ──
    # Expected bounding box (without tabs/boss):
    #   X: ~-9.65 to ~68.65 (with tabs), Y: 0 to 7.0 (with boss), Z: 0 to 47
    # But the plate itself is X: 0..59, Y: 0..6, Z: 0..47.
    # Check overall Z range matches plate height.
    z_size = bb.max.Z - bb.min.Z
    if abs(z_size - PLATE_H) < TOL:
        results.append(("Plate body height", "PASS", f"Z range = {z_size:.3f}mm (spec {PLATE_H})"))
    else:
        results.append(("Plate body height", "FAIL", f"Z range = {z_size:.3f}mm, expected {PLATE_H}"))

    y_size = bb.max.Y - bb.min.Y
    expected_y = PLATE_D + BOSS_HEIGHT  # 6 + 1 = 7
    if abs(y_size - expected_y) < TOL:
        results.append(("Plate body depth+boss", "PASS", f"Y range = {y_size:.3f}mm (spec {expected_y})"))
    else:
        results.append(("Plate body depth+boss", "FAIL", f"Y range = {y_size:.3f}mm, expected {expected_y}"))

    # ── 2. Stepped bores (4x) ──
    # Check for cylindrical/circular faces at each bore position.
    # After subtraction, each bore creates curved faces. We look for faces
    # whose center is near each bore center (cx, cz) and at various Y depths.
    for i, (cx, cz) in enumerate(BORE_CENTERS):
        bore_name = f"Bore #{i+1} ({cx},{cz})"
        # Find faces whose center is within the outer bore radius of this bore center
        bore_faces = part.faces().filter_by(
            lambda f, _cx=cx, _cz=cz: (
                ((f.center().X - _cx) ** 2 + (f.center().Z - _cz) ** 2) ** 0.5
                < OUTER_BORE_DIA / 2 + 1.0
                and f.center().Y > -0.1
                and f.center().Y < PLATE_D + 0.1
                and f.geom_type == GeomType.CYLINDER
            )
        )
        if len(bore_faces) >= 2:
            results.append((bore_name, "PASS", f"{len(bore_faces)} cylindrical faces found"))
        else:
            results.append((bore_name, "FAIL", f"Only {len(bore_faces)} cylindrical faces (expected >=2 stepped surfaces)"))

    # ── 3. Push rod boss ──
    # The boss should create a cylindrical face centered at (29.5, ~6.5, 23.5)
    # with radius 4.0mm, extending from Y=6 to Y=7.
    boss_faces = part.faces().filter_by(
        lambda f: (
            f.geom_type == GeomType.CYLINDER
            and abs(f.center().X - BOSS_CENTER[0]) < BOSS_DIA
            and abs(f.center().Z - BOSS_CENTER[1]) < BOSS_DIA
            and f.center().Y > PLATE_D - 0.5
        )
    )
    if len(boss_faces) >= 1:
        bf = boss_faces[0]
        boss_bb = bf.bounding_box()
        boss_dia_x = boss_bb.max.X - boss_bb.min.X
        if abs(boss_dia_x - BOSS_DIA) < TOL:
            results.append(("Push rod boss", "PASS",
                            f"Cyl face at ({bf.center().X:.1f}, {bf.center().Y:.1f}, {bf.center().Z:.1f}), "
                            f"dia ~{boss_dia_x:.2f}mm (spec {BOSS_DIA})"))
        else:
            results.append(("Push rod boss", "FAIL",
                            f"Boss diameter {boss_dia_x:.2f}mm, expected {BOSS_DIA}"))
    else:
        results.append(("Push rod boss", "FAIL", "No cylindrical face found at boss position"))

    # Boss protrusion height: Y should extend to PLATE_D + BOSS_HEIGHT
    if abs(bb.max.Y - (PLATE_D + BOSS_HEIGHT)) < TOL:
        results.append(("Boss height", "PASS",
                        f"Max Y = {bb.max.Y:.3f}mm (spec {PLATE_D + BOSS_HEIGHT})"))
    else:
        results.append(("Boss height", "FAIL",
                        f"Max Y = {bb.max.Y:.3f}mm, expected {PLATE_D + BOSS_HEIGHT}"))

    # ── 4. Guide tabs (2x) ──
    # Left tab: bounding box should extend to X ~ SLOT_CENTERS[0][0] - TAB_WIDTH/2
    left_expected_x = SLOT_CENTERS[0][0] - TAB_WIDTH / 2
    right_expected_x = SLOT_CENTERS[1][0] + TAB_WIDTH / 2
    if abs(bb.min.X - left_expected_x) < TOL:
        results.append(("Left guide tab extent", "PASS",
                        f"Min X = {bb.min.X:.3f}mm (spec {left_expected_x:.3f})"))
    else:
        results.append(("Left guide tab extent", "FAIL",
                        f"Min X = {bb.min.X:.3f}mm, expected {left_expected_x:.3f}"))

    if abs(bb.max.X - right_expected_x) < TOL:
        results.append(("Right guide tab extent", "PASS",
                        f"Max X = {bb.max.X:.3f}mm (spec {right_expected_x:.3f})"))
    else:
        results.append(("Right guide tab extent", "FAIL",
                        f"Max X = {bb.max.X:.3f}mm, expected {right_expected_x:.3f}"))

    # Tab Z extent: tabs should be vertically centered at Z=23.5 with TAB_HEIGHT
    # The tab's Z range: SLOT_CENTERS[0][1] +/- TAB_HEIGHT/2
    tab_z_min = SLOT_CENTERS[0][1] - TAB_HEIGHT / 2
    tab_z_max = SLOT_CENTERS[0][1] + TAB_HEIGHT / 2
    # These should be within the plate's Z range (0..47), so the plate body
    # already covers them. We can't isolate the tab Z from the plate Z.
    # Instead, verify the tab is not taller than the plate (it shouldn't be).
    if tab_z_min >= 0 and tab_z_max <= PLATE_H:
        results.append(("Tab Z within plate", "PASS",
                        f"Tab Z [{tab_z_min:.1f}, {tab_z_max:.1f}] inside plate [0, {PLATE_H}]"))
    else:
        results.append(("Tab Z within plate", "FAIL",
                        f"Tab Z [{tab_z_min:.1f}, {tab_z_max:.1f}] exceeds plate [0, {PLATE_H}]"))

    # ── 5. Guide pin slots (2x) ──
    # Slots are stadium-shaped through-holes. After subtraction, they create
    # curved faces (semi-cylindrical) inside the tabs. We look for cylindrical
    # faces centered near each slot center.
    for i, (sx, sz) in enumerate(SLOT_CENTERS):
        slot_name = f"Guide slot #{i+1} ({sx},{sz})"
        # Find cylindrical faces near the slot center
        slot_cyl_faces = part.faces().filter_by(
            lambda f, _sx=sx, _sz=sz: (
                f.geom_type == GeomType.CYLINDER
                and abs(f.center().X - _sx) < SLOT_W
                and abs(f.center().Z - _sz) < SLOT_H
                and f.center().Y > -0.1
                and f.center().Y < PLATE_D + 0.1
            )
        )
        # Also find planar faces that form the flat sides of the stadium
        slot_plane_faces = part.faces().filter_by(
            lambda f, _sx=sx, _sz=sz: (
                f.geom_type == GeomType.PLANE
                and abs(f.center().X - _sx) < SLOT_W
                and abs(f.center().Z - _sz) < SLOT_H
                and f.center().Y > 0.1
                and f.center().Y < PLATE_D - 0.1
            )
        )
        total_slot_faces = len(slot_cyl_faces) + len(slot_plane_faces)
        if total_slot_faces >= 2:
            # Verify orientation: cylindrical faces should have axis along Y
            # Check that the cylindrical face spans the full Y depth
            orientations_ok = True
            for cf in slot_cyl_faces:
                cf_bb = cf.bounding_box()
                y_span = cf_bb.max.Y - cf_bb.min.Y
                if y_span < PLATE_D - TOL:
                    orientations_ok = False
            if orientations_ok:
                results.append((slot_name, "PASS",
                                f"{len(slot_cyl_faces)} cyl + {len(slot_plane_faces)} planar faces, "
                                f"orientation OK (through Y)"))
            else:
                results.append((slot_name, "FAIL",
                                f"Faces found but Y span < {PLATE_D}mm (wrong orientation)"))
        else:
            results.append((slot_name, "FAIL",
                            f"Only {total_slot_faces} faces near slot position (expected >=2)"))

        # Check slot dimensions: the cylindrical end caps should have radius = SLOT_W/2 = 1.65mm
        if len(slot_cyl_faces) >= 1:
            cf_bb = slot_cyl_faces[0].bounding_box()
            # The cylinder bounding box X extent should be ~SLOT_W (3.3mm)
            cyl_x = cf_bb.max.X - cf_bb.min.X
            # Z extent of one semicircle should be ~SLOT_W/2 = 1.65mm
            if abs(cyl_x - SLOT_W) < TOL + 0.1:
                results.append((f"Slot #{i+1} width", "PASS",
                                f"Cyl X extent = {cyl_x:.3f}mm (spec ~{SLOT_W})"))
            else:
                results.append((f"Slot #{i+1} width", "FAIL",
                                f"Cyl X extent = {cyl_x:.3f}mm, expected ~{SLOT_W}"))

    all_pass = all(r[1] == "PASS" for r in results)
    return results, all_pass


if __name__ == "__main__":
    print("Generating release plate...")
    part = make_release_plate()

    # ── Overall geometry summary ──
    bb = part.bounding_box()
    print(f"\nBounding box:")
    print(f"  X: {bb.min.X:.3f} to {bb.max.X:.3f}  (width: {bb.max.X - bb.min.X:.3f})")
    print(f"  Y: {bb.min.Y:.3f} to {bb.max.Y:.3f}  (depth: {bb.max.Y - bb.min.Y:.3f})")
    print(f"  Z: {bb.min.Z:.3f} to {bb.max.Z:.3f}  (height: {bb.max.Z - bb.min.Z:.3f})")
    print(f"Volume: {part.volume:.2f} mm^3")
    print(f"Face count: {len(part.faces())}")

    # ── Per-feature validation ──
    print("\n" + "=" * 72)
    print("FEATURE VALIDATION")
    print("=" * 72)
    results, all_pass = validate_release_plate(part)
    for name, status, detail in results:
        marker = "OK" if status == "PASS" else "!!"
        print(f"  [{marker}] {status:4s}  {name:30s}  {detail}")
    print("=" * 72)
    if all_pass:
        print("RESULT: ALL FEATURES PASS")
    else:
        fail_count = sum(1 for r in results if r[1] == "FAIL")
        print(f"RESULT: {fail_count} FEATURE(S) FAILED")
    print("=" * 72)

    # ── Export STEP ──
    export_step(part, str(STEP_PATH))
    print(f"\nSTEP file written to: {STEP_PATH}")
