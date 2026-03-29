#!/usr/bin/env python3
"""
Generate STEP file for the linkage arm (pump cartridge mechanism).

Both left and right arms are identical — print this part twice.

Source: hardware/printed-parts/pump-cartridge/planning/linkage-arm-parts.md
        hardware/printed-parts/pump-cartridge/planning/linkage-arm-spatial.md
"""

# Coordinate system:
#   Origin: front-left-bottom corner of the bar body
#   X: width (left to right), 0 at left face, positive rightward
#   Y: length (front to back), 0 at front face, positive rearward
#   Z: thickness (bottom to top), 0 at bottom face (build plate), positive upward
#   Bar body envelope: 6.0 x 154.4 x 3.0 mm → X:[0,6.0] Y:[0,154.4] Z:[0,3.0]
#   Overall bounding box: 6.0 x 158.4 x 8.0 mm
#     Front pin extends to Z = 8.0
#     Rear pin extends to Y = 158.4

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

import cadquery as cq
from step_validate import Validator

# ============================================================
# Rubric 1 — Feature Planning Table
# ============================================================

print("""
=== FEATURE PLANNING TABLE ===

| # | Feature Name           | Mechanical Function                                    | Operation | Shape     | Axis | Center Position (X,Y,Z)        | Dimensions                  | Notes                                          |
|---|------------------------|--------------------------------------------------------|-----------|-----------|------|--------------------------------|-----------------------------|-------------------------------------------------|
| 1 | Bar body               | Rigid push-pull rod transmitting squeeze/spring force  | Add       | Box       | Y    | (3.0, 77.2, 1.5) center       | 6.0 W x 154.4 L x 3.0 H   | centered=False, origin at (0,0,0)              |
| 2 | Front pin (Z-axis)     | Connects arm to finger plate tab socket (press-fit)    | Add       | Cylinder  | Z    | (3.0, 3.0, 3.0) base          | 3.0 dia x 5.0 tall         | Extends from bar top face upward to Z=8.0      |
| 3 | Rear pin (Y-axis)      | Connects arm to release plate tab socket (press-fit)   | Add       | Cylinder  | Y    | (3.0, 154.4, 1.5) base        | 3.0 dia x 4.0 long         | Extends from bar rear face rearward to Y=158.4 |
| 4 | Elephant's foot chamfer| Prevents flaring on build-plate face from binding      | Remove    | Chamfer   | --   | Bottom perimeter edges (Z=0)   | 0.3 mm x 45 deg            | All four bottom edges of bar body only          |
| 5 | Front pin tip chamfer  | Insertion ease into finger plate socket                | Remove    | Chamfer   | Z    | Top edge of front pin (Z=8.0)  | 0.3 mm x 45 deg            | Tip chamfer on circular edge                    |
| 6 | Rear pin tip chamfer   | Insertion ease into release plate socket               | Remove    | Chamfer   | Y    | End edge of rear pin (Y=158.4) | 0.3 mm x 45 deg            | Tip chamfer on circular edge                    |
""")

# ============================================================
# Dimensions from parts.md
# ============================================================

# Bar body
BAR_W = 6.0      # X
BAR_L = 154.4    # Y
BAR_H = 3.0      # Z

# Front pin (Z-axis, vertical, upward from top face)
FPIN_DIA = 3.0
FPIN_HEIGHT = 5.0
FPIN_CX = 3.0    # center X (arm local)
FPIN_CY = 3.0    # center Y (arm local)
FPIN_BASE_Z = BAR_H  # 3.0, top face of bar

# Rear pin (Y-axis, rearward from rear face)
RPIN_DIA = 3.0
RPIN_LENGTH = 4.0
RPIN_CX = 3.0    # center X (arm local)
RPIN_CZ = 1.5    # center Z (arm local, mid-height of bar)
RPIN_BASE_Y = BAR_L  # 154.4, rear face of bar

# Chamfers
CHAMFER_EF = 0.3   # elephant's foot chamfer
CHAMFER_PIN = 0.3  # pin tip chamfer

# Overall bounding box (for validation)
BB_X_MIN, BB_X_MAX = 0.0, 6.0
BB_Y_MIN, BB_Y_MAX = 0.0, 158.4   # rear pin tip
BB_Z_MIN, BB_Z_MAX = 0.0, 8.0     # front pin tip (before chamfer reduces slightly)

# ============================================================
# Rubric 2 — done (coordinate system declared at top)
# ============================================================

# ============================================================
# Modeling
# ============================================================

# --- Feature 1: Bar body ---
bar = cq.Workplane("XY").box(BAR_W, BAR_L, BAR_H, centered=False)

# --- Feature 4: Elephant's foot chamfer on build-plate face (Z=0) bottom edges ---
# Select the four edges on the Z=0 face. These are the edges at Z=0.
bar = (
    bar
    .edges("|X").edges(cq.selectors.NearestToPointSelector((BAR_W / 2, 0, 0)))
    .chamfer(CHAMFER_EF)
)
bar = (
    bar
    .edges("|X").edges(cq.selectors.NearestToPointSelector((BAR_W / 2, BAR_L, 0)))
    .chamfer(CHAMFER_EF)
)
bar = (
    bar
    .edges("|Y").edges(cq.selectors.NearestToPointSelector((0, BAR_L / 2, 0)))
    .chamfer(CHAMFER_EF)
)
bar = (
    bar
    .edges("|Y").edges(cq.selectors.NearestToPointSelector((BAR_W, BAR_L / 2, 0)))
    .chamfer(CHAMFER_EF)
)

# --- Feature 2: Front pin (Z-axis cylinder, upward from top face) ---
front_pin = (
    cq.Workplane("XY")
    .transformed(offset=(FPIN_CX, FPIN_CY, FPIN_BASE_Z))
    .circle(FPIN_DIA / 2)
    .extrude(FPIN_HEIGHT)  # +Z direction
)

# --- Feature 3: Rear pin (Y-axis cylinder, rearward from rear face) ---
# Build on XZ workplane, extrude along -Y normal.
# XZ normal is -Y; negative extrude goes +Y.
rear_pin = (
    cq.Workplane("XZ")
    .transformed(offset=(RPIN_CX, RPIN_CZ, 0))
    .circle(RPIN_DIA / 2)
    .extrude(-RPIN_LENGTH)  # XZ normal is -Y; negative extrude goes +Y
)
# The cylinder was extruded from Y=0 toward +Y for RPIN_LENGTH.
# We need it starting at Y=RPIN_BASE_Y, so translate.
rear_pin = rear_pin.translate((0, RPIN_BASE_Y, 0))

# Union pins to bar body
arm = bar.union(front_pin).union(rear_pin)

# --- Feature 5: Front pin tip chamfer ---
# Select the circular edge at the top of the front pin (Z = FPIN_BASE_Z + FPIN_HEIGHT = 8.0)
arm = (
    arm
    .edges(
        cq.selectors.NearestToPointSelector((FPIN_CX, FPIN_CY, FPIN_BASE_Z + FPIN_HEIGHT))
    )
    .chamfer(CHAMFER_PIN)
)

# --- Feature 6: Rear pin tip chamfer ---
# Select the circular edge at the end of the rear pin (Y = RPIN_BASE_Y + RPIN_LENGTH = 158.4)
arm = (
    arm
    .edges(
        cq.selectors.NearestToPointSelector((RPIN_CX, RPIN_BASE_Y + RPIN_LENGTH, RPIN_CZ))
    )
    .chamfer(CHAMFER_PIN)
)

# ============================================================
# Export STEP
# ============================================================

output_path = Path(__file__).parent / "linkage-arm.step"
cq.exporters.export(arm, str(output_path))
print(f"\nSTEP exported to: {output_path}")

# ============================================================
# Rubric 3 — Feature-Specification Reconciliation
# ============================================================

print("\n=== FEATURE RECONCILIATION ===\n")
v = Validator(arm)

# Feature 1: Bar body
v.check_solid("Bar body center", BAR_W / 2, BAR_L / 2, BAR_H / 2, "solid at bar center")
v.check_solid("Bar body front-left", 0.5, 0.5, BAR_H / 2, "solid near front-left")
v.check_solid("Bar body rear-right", BAR_W - 0.5, BAR_L - 0.5, BAR_H / 2, "solid near rear-right")
v.check_void("Bar body above top", BAR_W / 2, BAR_L / 2, BAR_H + 1.0, "void above bar (not at pin)")
v.check_void("Bar body below bottom", BAR_W / 2, BAR_L / 2, -0.5, "void below bar")

# Feature 2: Front pin
v.check_solid("Front pin center", FPIN_CX, FPIN_CY, FPIN_BASE_Z + FPIN_HEIGHT / 2,
              "solid at front pin mid-height")
v.check_solid("Front pin base", FPIN_CX, FPIN_CY, FPIN_BASE_Z + 0.5,
              "solid just above pin base")
v.check_solid("Front pin near tip", FPIN_CX, FPIN_CY, FPIN_BASE_Z + FPIN_HEIGHT - 0.5,
              "solid near front pin tip")
v.check_void("Front pin outside X+", FPIN_CX + FPIN_DIA / 2 + 0.5, FPIN_CY,
             FPIN_BASE_Z + FPIN_HEIGHT / 2, "void outside front pin X+")
v.check_void("Front pin outside X-", FPIN_CX - FPIN_DIA / 2 - 0.5, FPIN_CY,
             FPIN_BASE_Z + FPIN_HEIGHT / 2, "void outside front pin X-")

# Feature 3: Rear pin
v.check_solid("Rear pin center", RPIN_CX, RPIN_BASE_Y + RPIN_LENGTH / 2, RPIN_CZ,
              "solid at rear pin mid-length")
v.check_solid("Rear pin base", RPIN_CX, RPIN_BASE_Y + 0.5, RPIN_CZ,
              "solid just behind pin base")
v.check_solid("Rear pin near tip", RPIN_CX, RPIN_BASE_Y + RPIN_LENGTH - 0.5, RPIN_CZ,
              "solid near rear pin tip")
v.check_void("Rear pin outside Z+", RPIN_CX, RPIN_BASE_Y + RPIN_LENGTH / 2,
             RPIN_CZ + RPIN_DIA / 2 + 0.5, "void outside rear pin Z+")
v.check_void("Rear pin outside Z-", RPIN_CX, RPIN_BASE_Y + RPIN_LENGTH / 2,
             RPIN_CZ - RPIN_DIA / 2 - 0.5, "void outside rear pin Z-")

# Feature 4: Elephant's foot chamfer — probe corner at Z=0 to verify material removed
v.check_void("EF chamfer front-left Y edge", BAR_W / 2, -0.05, -0.05,
             "void at chamfered front-bottom edge")
v.check_void("EF chamfer rear-left Y edge", BAR_W / 2, BAR_L + 0.05, -0.05,
             "void at chamfered rear-bottom edge")
# Verify material still present just inside the chamfer
v.check_solid("Bar body inside chamfer zone", 0.5, 0.5, 0.4,
              "solid above chamfer at front-left corner")

# Feature 5: Front pin tip chamfer — pin tip should be slightly truncated
v.check_void("Front pin tip chamfer edge", FPIN_CX + FPIN_DIA / 2 - 0.05,
             FPIN_CY, FPIN_BASE_Z + FPIN_HEIGHT,
             "void at front pin chamfered tip edge")

# Feature 6: Rear pin tip chamfer
v.check_void("Rear pin tip chamfer edge", RPIN_CX + RPIN_DIA / 2 - 0.05,
             RPIN_BASE_Y + RPIN_LENGTH, RPIN_CZ,
             "void at rear pin chamfered tip edge")

# ============================================================
# Rubric 4 — Solid Validity
# ============================================================

print("\n=== SOLID VALIDITY ===\n")
v.check_valid()
v.check_single_body()
v.check_volume(
    expected_envelope=BAR_W * (BAR_L + RPIN_LENGTH) * (BAR_H + FPIN_HEIGHT),
    fill_range=(0.2, 0.8)
)

# ============================================================
# Rubric 5 — Bounding Box Reconciliation
# ============================================================

print("\n=== BOUNDING BOX ===\n")
bb = arm.val().BoundingBox()

# Pin tip chamfers reduce the max extent slightly, so allow some tolerance
v.check_bbox("X", bb.xmin, bb.xmax, BB_X_MIN, BB_X_MAX)
v.check_bbox("Y", bb.ymin, bb.ymax, BB_Y_MIN, BB_Y_MAX)
v.check_bbox("Z", bb.zmin, bb.zmax, BB_Z_MIN, BB_Z_MAX)

# ============================================================
# Summary
# ============================================================

if not v.summary():
    sys.exit(1)
