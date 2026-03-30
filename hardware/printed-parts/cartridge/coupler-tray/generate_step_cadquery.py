"""
Coupler Tray v3 — Widened Top and Bottom Plates
CadQuery STEP Generation Script

Specification source: hardware/printed-parts/cartridge/coupler-tray/planning/parts.md
JG union geometry:    hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md

The coupler tray is split along Y (thickness) into two identical plates.
Each plate is 6.08mm thick with 9.5mm through-bores at coupler positions
and 6.4x6.4mm rectangular strut bores at corner positions. When the two
plates are stacked face-to-face, the combined bore length (12.16mm) matches
the coupler center body length, and the wider shoulders (15.10mm OD) on
each end provide axial retention against the 9.5mm bore.

Both plates are geometrically identical.

v3 changes: Plate widened from 137.2mm to 140.0mm to match pump tray v3.
Coupler bores re-centered (+1.4mm X shift). Strut bores repositioned to
match pump tray v3 strut positions.

Rubric 2 — Coordinate System Declaration:
  Origin: plate bottom-left corner of outer face (X=0, Y=0, Z=0)
  X: plate width axis — left to right, 0..140.0mm
  Y: plate thickness axis — outer face (Y=0) to mating face (Y=6.08mm)
  Z: plate height axis — bottom to top, 0..68.6mm
  Bounding envelope: 140.0mm (X) x 6.08mm (Y) x 68.6mm (Z)

  Hole/bore axes are parallel to Y.
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
COUPLER TRAY v3 — WIDENED SPLIT PLATE — Feature Planning Table (Rubric 1)
==========================================================================
Each half (top plate and bottom plate) is identical.

  #   Feature Name              Op      Shape         Axis  Center (X,Y,Z)          Dimensions
  1   Base plate body           Add     Rect prism    —     (70.0, 3.04, 34.3)      140.0 x 6.08 x 68.6 mm
  2   Coupler bore H1           Remove  Cylinder      Y     (44.5, 3.04, 34.3)      9.5mm dia, through Y
  3   Coupler bore H2           Remove  Cylinder      Y     (61.5, 3.04, 34.3)      9.5mm dia, through Y
  4   Coupler bore H3           Remove  Cylinder      Y     (78.5, 3.04, 34.3)      9.5mm dia, through Y
  5   Coupler bore H4           Remove  Cylinder      Y     (95.5, 3.04, 34.3)      9.5mm dia, through Y
  6   Strut bore S-TL           Remove  Rect prism    Y     (4.0, 3.04, 63.6)       6.4 x 6.08 x 6.4 mm, TH
  7   Strut bore S-TR           Remove  Rect prism    Y     (136.0, 3.04, 63.6)     6.4 x 6.08 x 6.4 mm, TH
  8   Strut bore S-BL           Remove  Rect prism    Y     (4.0, 3.04, 5.0)        6.4 x 6.08 x 6.4 mm, TH
  9   Strut bore S-BR           Remove  Rect prism    Y     (136.0, 3.04, 5.0)      6.4 x 6.08 x 6.4 mm, TH

TH = through-hole, full Y depth (0 to 6.08mm)
"""

print(FEATURE_TABLE)

# ---------------------------------------------------------------------------
# Dimensions (from parts.md and JG union geometry)
# ---------------------------------------------------------------------------

# Plate envelope
PLATE_W = 140.0    # X — width left to right (widened from 137.2)
PLATE_D = 6.08     # Y — half-plate thickness (half of 12.16mm center body length)
PLATE_H = 68.6     # Z — height bottom to top

# Coupler bore
HOLE_DIA = 9.5     # mm — clears 9.31mm center body OD
HOLE_R = HOLE_DIA / 2.0  # 4.75mm

# Hole centers (X, Z) — 1x4 row along X, all at Z=34.3mm, 17mm c-c
# Re-centered for 140.0mm width: old center 68.6 -> new center 70.0, shift +1.4mm
HOLES = [
    ("H1", 44.5, 34.3),
    ("H2", 61.5, 34.3),
    ("H3", 78.5, 34.3),
    ("H4", 95.5, 34.3),
]

# Strut bore parameters — positions match pump tray v3
STRUT_BORE_W = 6.4   # mm (X) — 6.0mm strut + 0.4mm clearance
STRUT_BORE_H = 6.4   # mm (Z) — 6.0mm strut + 0.4mm clearance

STRUT_BORES = [
    ("S-TL", 4.0,   63.6),
    ("S-TR", 136.0, 63.6),
    ("S-BL", 4.0,    5.0),
    ("S-BR", 136.0,  5.0),
]

MID_Y = PLATE_D / 2.0  # 3.04mm — mid-depth of plate

OVERCUT = 0.1  # mm past exit face to ensure clean boolean exit


def build_half_plate(name):
    """Build one half of the split coupler tray. Both halves are identical."""

    print(f"=== Building {name} ===")
    print()

    # --- Feature 1: Base plate body ---
    print(f"Building Feature 1 — Base plate body ({PLATE_W} x {PLATE_D} x {PLATE_H} mm)...")
    plate = (
        cq.Workplane("XY")
        .box(PLATE_W, PLATE_D, PLATE_H, centered=False)
    )

    # --- Features 2-5: Coupler through-bores ---
    print(f"Building Features 2-5 — 4x coupler through-bores ({HOLE_DIA}mm dia, Y=0->{PLATE_D}mm)...")

    for hole_id, hx, hz in HOLES:
        print(f"  Cutting bore {hole_id} at X={hx}, Z={hz}")
        bore = (
            cq.Workplane("XZ")
            .workplane(offset=0)                          # sketch plane at Y=0 (outer face)
            .center(hx, hz)
            .circle(HOLE_R)
            .extrude(-(PLATE_D + OVERCUT))                # +Y direction: Y=0 -> Y=6.18mm
        )
        plate = plate.cut(bore)

    print("Coupler bores complete.")
    print()

    # --- Features 6-9: Strut bores ---
    print(f"Building Features 6-9 — 4x strut bores ({STRUT_BORE_W}x{STRUT_BORE_H}mm, Y=0->{PLATE_D}mm)...")

    for bore_id, cx, cz in STRUT_BORES:
        x0 = cx - STRUT_BORE_W / 2
        z0 = cz - STRUT_BORE_H / 2
        bore_box = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(x0, -OVERCUT / 2, z0))
            .box(STRUT_BORE_W, PLATE_D + OVERCUT, STRUT_BORE_H, centered=False)
        )
        plate = plate.cut(bore_box)
        print(f"  [-] Strut bore {bore_id} at X={cx}, Z={cz} "
              f"(rect {STRUT_BORE_W}x{STRUT_BORE_H} mm)")

    print(f"{name} construction complete.")
    print()

    return plate


def validate_half(plate, name):
    """Run Rubric 3-5 validation on one half plate."""

    print("=" * 60)
    print(f"VALIDATION — {name}")
    print("=" * 60)
    print()

    # --- Rubric 3: Feature-Specification Reconciliation ---
    print("RUBRIC 3 — Feature-Specification Reconciliation")
    print("-" * 50)
    print()

    v = Validator(plate)

    # Feature 1: Base plate body
    print("Feature 1 — Base plate body:")
    v.check_solid("Plate center",         70.0, MID_Y, 34.3,  "solid at plate geometric center")
    v.check_solid("Plate near Y=0",       70.0, 0.3,   34.3,  "solid near outer face Y=0")
    v.check_solid("Plate near Y=max",     70.0, PLATE_D - 0.3, 34.3, "solid near mating face")
    v.check_solid("Plate left edge",      0.5,  MID_Y, 34.3,  "solid near X=0 left edge")
    v.check_solid("Plate right edge",     139.5, MID_Y, 34.3, "solid near X=140.0 right edge")
    v.check_solid("Plate bottom edge",    70.0, MID_Y, 0.5,   "solid near Z=0 bottom edge")
    v.check_solid("Plate top edge",       70.0, MID_Y, 68.1,  "solid near Z=68.6 top edge")
    # Verify plate does NOT extend above Y=6.08
    v.check_void("No material above plate",
                 70.0, PLATE_D + 0.5, 34.3,
                 "void above mating face — plate is only 6.08mm thick")
    print()

    # Features 2-5: Coupler through-bores
    for hole_id, hx, hz in HOLES:
        print(f"Feature — Bore {hole_id} at X={hx}, Z={hz}:")

        # Void at bore center at mid-depth
        v.check_void(f"Bore {hole_id} center mid-depth",
                     hx, MID_Y, hz,
                     f"void at ({hx}, {MID_Y}, {hz}) — bore center")

        # Void near outer face
        v.check_void(f"Bore {hole_id} near outer face",
                     hx, 0.3, hz,
                     f"void at ({hx}, 0.3, {hz}) — bore enters outer face")

        # Void near mating face
        v.check_void(f"Bore {hole_id} near mating face",
                     hx, PLATE_D - 0.3, hz,
                     f"void at ({hx}, {PLATE_D - 0.3:.2f}, {hz}) — bore exits mating face")

        # Solid just outside bore radius in +X direction
        v.check_solid(f"Bore {hole_id} solid outside (+X)",
                      hx + HOLE_R + 0.5, MID_Y, hz,
                      f"solid at ({hx + HOLE_R + 0.5:.2f}, {MID_Y}, {hz}) — outside bore radius")

        print()

    # Features 6-9: Strut bores
    print("Features 6-9 — Strut bores:")
    for bore_id, cx, cz in STRUT_BORES:
        half_w = STRUT_BORE_W / 2  # 3.2
        half_h = STRUT_BORE_H / 2  # 3.2

        # Void at bore center, mid-depth
        v.check_void(f"Strut bore {bore_id} center",
                     cx, MID_Y, cz,
                     f"void at bore center ({cx}, {MID_Y}, {cz})")

        # Void near outer face
        v.check_void(f"Strut bore {bore_id} outer",
                     cx, 0.1, cz,
                     f"void near outer face Y=0.1")

        # Void near mating face
        v.check_void(f"Strut bore {bore_id} mating",
                     cx, PLATE_D - 0.1, cz,
                     f"void near mating face Y={PLATE_D - 0.1:.2f}")

        # Void at bore corners
        inset = 0.3
        v.check_void(f"Strut bore {bore_id} corner +X+Z",
                     cx + half_w - inset, MID_Y, cz + half_h - inset,
                     f"void near +X+Z corner of bore")
        v.check_void(f"Strut bore {bore_id} corner -X-Z",
                     cx - half_w + inset, MID_Y, cz - half_h + inset,
                     f"void near -X-Z corner of bore")

        # Solid outside bore in X direction
        outside_x = cx + half_w + 1.0
        if outside_x < PLATE_W:
            v.check_solid(f"Strut bore {bore_id} wall +X",
                          outside_x, MID_Y, cz,
                          f"solid outside bore +X edge at X={outside_x:.1f}")

        outside_x_neg = cx - half_w - 1.0
        if outside_x_neg > 0:
            v.check_solid(f"Strut bore {bore_id} wall -X",
                          outside_x_neg, MID_Y, cz,
                          f"solid outside bore -X edge at X={outside_x_neg:.1f}")

    print()

    # --- Rubric 4: Solid Validity ---
    print("RUBRIC 4 — Solid Validity")
    print("-" * 50)
    print()

    v.check_valid()
    v.check_single_body()

    # Volume estimate:
    #   Base plate: 140.0 x 6.08 x 68.6 = 58,357 mm^3
    #   4 coupler bores: pi x 4.75^2 x 6.08 x 4 = 1,724 mm^3
    #   4 strut bores: 4 x 6.4 x 6.4 x 6.08 = 997 mm^3
    #   Expected ~ 58,357 - 1,724 - 997 = 55,636 mm^3
    #   Envelope: 140.0 x 6.08 x 68.6 = 58,357 mm^3
    #   Fill ratio ~ 55,636 / 58,357 ~ 0.953
    envelope_vol = PLATE_W * PLATE_D * PLATE_H
    v.check_volume(expected_envelope=envelope_vol, fill_range=(0.8, 1.0))
    print()

    # --- Rubric 5: Bounding Box Reconciliation ---
    print("RUBRIC 5 — Bounding Box Reconciliation")
    print("-" * 50)
    print()

    bb = plate.val().BoundingBox()
    v.check_bbox("X", bb.xmin, bb.xmax, 0.0, PLATE_W)
    v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, PLATE_D)
    v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, PLATE_H)
    print()

    return v


# ---------------------------------------------------------------------------
# Build and validate both halves
# ---------------------------------------------------------------------------

top_plate = build_half_plate("Top Plate")
bottom_plate = build_half_plate("Bottom Plate")

v_top = validate_half(top_plate, "TOP PLATE")
v_bottom = validate_half(bottom_plate, "BOTTOM PLATE")

# ---------------------------------------------------------------------------
# Export STEP files
# ---------------------------------------------------------------------------

OUTPUT_DIR = Path(__file__).resolve().parent

TOP_STEP = OUTPUT_DIR / "coupler-tray-top-cadquery.step"
BOTTOM_STEP = OUTPUT_DIR / "coupler-tray-bottom-cadquery.step"

print(f"Exporting top plate STEP -> {TOP_STEP}")
cq.exporters.export(top_plate, str(TOP_STEP))
print(f"Exporting bottom plate STEP -> {BOTTOM_STEP}")
cq.exporters.export(bottom_plate, str(BOTTOM_STEP))
print("Export complete.")
print()

# ---------------------------------------------------------------------------
# Final summary — exits 1 on any FAIL
# ---------------------------------------------------------------------------

top_ok = v_top.summary()
bottom_ok = v_bottom.summary()

if not (top_ok and bottom_ok):
    print()
    print("FAILURES DETECTED — fix model before exporting.")
    sys.exit(1)

print()
print(f"Top plate STEP:    {TOP_STEP}")
print(f"Bottom plate STEP: {BOTTOM_STEP}")
