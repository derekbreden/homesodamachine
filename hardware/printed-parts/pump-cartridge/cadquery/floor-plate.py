"""
Floor Plate — CadQuery STEP generation script.

Generates a flat PETG panel (148 x 60 x 4 mm) with two M3 counterbore
through-holes and bottom-edge chamfers. The simplest part in the cartridge.

Source: hardware/printed-parts/pump-cartridge/planning/specs/floor-plate.md
Spatial: hardware/printed-parts/pump-cartridge/planning/spatial/floor-plate-spatial.md
"""

import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))
from step_validate import Validator

# ======================================================================
# Coordinate system (Rubric 2):
#   Origin: rear-left corner of plate, top face
#   X: width, 0..148 mm (left to right)
#   Y: depth, 0..60 mm (rear to front)
#   Z: thickness, 0 at top face, -4 at bottom face (negative downward)
#   Envelope: 148 x 60 x 4 mm -> X:[0,148] Y:[0,60] Z:[-4,0]
# ======================================================================

# --- Dimensions ---
PLATE_W = 148.0   # X extent
PLATE_D = 60.0    # Y extent
PLATE_T = 4.0     # Z thickness (positive value; plate spans Z=-4..0)

# M3 counterbore through-holes (2x)
HOLE1_X = 21.50
HOLE2_X = 126.50
HOLE_Y = 30.00    # Y centerline

THRU_DIA = 3.40       # M3 clearance hole diameter
CB_DIA = 5.70         # Counterbore diameter (M3 SHCS head + 0.2 mm)
CB_DEPTH = 3.20       # Counterbore depth from bottom face

# Chamfer
CHAMFER = 0.30         # 0.30 mm x 45-deg elephant's foot on bottom edges

# --- Feature Planning Table (Rubric 1) ---
print("=" * 70)
print("Feature Planning Table — Floor Plate")
print("=" * 70)
print(f"{'#':<3} {'Feature':<30} {'Op':<8} {'Shape':<12} {'Axis':<5} "
      f"{'Center (X,Y,Z)':<22} {'Dimensions'}")
print("-" * 70)
features = [
    ("1", "Plate body", "Add", "Box", "Z",
     f"(74.0, 30.0, -2.0)", f"{PLATE_W}x{PLATE_D}x{PLATE_T}"),
    ("2a", "Through-hole 1", "Remove", "Cylinder", "Z",
     f"({HOLE1_X}, {HOLE_Y}, -2.0)", f"dia {THRU_DIA}, full depth"),
    ("2b", "Through-hole 2", "Remove", "Cylinder", "Z",
     f"({HOLE2_X}, {HOLE_Y}, -2.0)", f"dia {THRU_DIA}, full depth"),
    ("3a", "Counterbore 1", "Remove", "Cylinder", "Z",
     f"({HOLE1_X}, {HOLE_Y}, -2.4)", f"dia {CB_DIA}, depth {CB_DEPTH}"),
    ("3b", "Counterbore 2", "Remove", "Cylinder", "Z",
     f"({HOLE2_X}, {HOLE_Y}, -2.4)", f"dia {CB_DIA}, depth {CB_DEPTH}"),
    ("4", "Bottom-edge chamfers", "Remove", "Chamfer", "Z",
     "perimeter at Z=-4", f"{CHAMFER} x 45 deg"),
]
for f in features:
    print(f"{f[0]:<3} {f[1]:<30} {f[2]:<8} {f[3]:<12} {f[4]:<5} "
          f"{f[5]:<22} {f[6]}")
print("=" * 70)
print()

# ======================================================================
# Modeling
# ======================================================================

# 1. Plate body: box from (0,0,-4) to (148,60,0)
#    CadQuery box with centered=False places at origin corner.
#    We build at Z=0..PLATE_T then translate down by -PLATE_T.
plate = (
    cq.Workplane("XY")
    .box(PLATE_W, PLATE_D, PLATE_T, centered=False)
    .translate((0, 0, -PLATE_T))
)

# 2. M3 through-holes (2x) — full-depth cylindrical cuts, Z=0 to Z=-4
for hx in [HOLE1_X, HOLE2_X]:
    hole = (
        cq.Workplane("XY")
        .center(hx, HOLE_Y)
        .circle(THRU_DIA / 2.0)
        .extrude(-PLATE_T)  # XY workplane normal is +Z; negative extrude goes -Z
    )
    plate = plate.cut(hole)

# 3. Counterbores (2x) — from bottom face Z=-4, depth 3.20 upward to Z=-0.80
for hx in [HOLE1_X, HOLE2_X]:
    cb = (
        cq.Workplane("XY")
        .workplane(offset=-PLATE_T)  # move workplane to Z=-4
        .center(hx, HOLE_Y)
        .circle(CB_DIA / 2.0)
        .extrude(CB_DEPTH)  # extrude upward (+Z) from Z=-4 to Z=-0.80
    )
    plate = plate.cut(cb)

# 4. Bottom-edge chamfers (0.30 mm x 45-deg on bottom perimeter)
#    Select only the four bottom perimeter edges at Z=-4.
#    These are the edges on the bottom face that form the rectangle perimeter.
plate = (
    plate
    .edges("|Z")                    # vertical edges (corners of the box)
    .edges(cq.selectors.NearestToPointSelector((0, 0, -PLATE_T)))  # near bottom
    # That approach is tricky; let's use a direct approach instead.
)

# Re-do: start fresh for chamfer approach.
# Build plate body
plate = (
    cq.Workplane("XY")
    .box(PLATE_W, PLATE_D, PLATE_T, centered=False)
    .translate((0, 0, -PLATE_T))
)

# Through-holes
for hx in [HOLE1_X, HOLE2_X]:
    hole = (
        cq.Workplane("XY")
        .center(hx, HOLE_Y)
        .circle(THRU_DIA / 2.0)
        .extrude(-PLATE_T)
    )
    plate = plate.cut(hole)

# Counterbores
for hx in [HOLE1_X, HOLE2_X]:
    cb = (
        cq.Workplane("XY")
        .workplane(offset=-PLATE_T)
        .center(hx, HOLE_Y)
        .circle(CB_DIA / 2.0)
        .extrude(CB_DEPTH)
    )
    plate = plate.cut(cb)

# Bottom-edge chamfers: select edges on the bottom face (Z=-4) that form the
# rectangular perimeter. These are the 4 edges where vertical side walls meet
# the bottom face.
plate = (
    plate
    .edges(
        cq.selectors.BoxSelector(
            (-0.1, -0.1, -PLATE_T - 0.1),
            (PLATE_W + 0.1, PLATE_D + 0.1, -PLATE_T + 0.1)
        )
    )
    .chamfer(CHAMFER)
)

# ======================================================================
# Export STEP
# ======================================================================
step_path = Path(__file__).with_suffix(".step")
cq.exporters.export(plate, str(step_path))
print(f"Exported STEP: {step_path}")
print()

# ======================================================================
# Validation (Rubric 3-5)
# ======================================================================
print("=" * 60)
print("VALIDATION")
print("=" * 60)

v = Validator(plate)

# --- Rubric 4: Solid validity ---
v.check_valid()
v.check_single_body()

# --- Rubric 5: Bounding box ---
bb = plate.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, 0.0, PLATE_W)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, PLATE_D)
v.check_bbox("Z", bb.zmin, bb.zmax, -PLATE_T, 0.0)

# --- Rubric 4: Volume ---
# Envelope = 148 * 60 * 4 = 35520 mm^3
# Subtract: 2x through-holes + 2x counterbores + chamfer material
# Through-holes: 2 * pi*(1.7)^2 * 4 = ~72.6
# Counterbores (net above through-hole): 2 * (pi*(2.85)^2 - pi*(1.7)^2) * 3.2 = ~103.2
# Chamfer: small, ~53 mm^3
# Expected ~ 35520 - 72.6 - 103.2 - 53 ~ 35291
v.check_volume(expected_envelope=PLATE_W * PLATE_D * PLATE_T, fill_range=(0.90, 1.0))

# --- Rubric 3: Feature probes ---
print()
print("Feature probes:")

# 1. Plate body — solid at interior points
v.check_solid("Plate body center", 74.0, 30.0, -2.0,
              "solid at plate center")
v.check_solid("Plate body near top face", 74.0, 30.0, -0.1,
              "solid just below top face")
v.check_solid("Plate body near bottom face", 74.0, 30.0, -3.9,
              "solid just above bottom face")
v.check_solid("Plate body corner RL", 1.0, 1.0, -2.0,
              "solid near rear-left corner")
v.check_solid("Plate body corner FR", 147.0, 59.0, -2.0,
              "solid near front-right corner")

# 2. Through-holes — void full depth at hole centers
for name, hx in [("Hole 1", HOLE1_X), ("Hole 2", HOLE2_X)]:
    v.check_void(f"{name} center top", hx, HOLE_Y, -0.1,
                 f"void at {name} center near top face")
    v.check_void(f"{name} center mid", hx, HOLE_Y, -2.0,
                 f"void at {name} center at mid-depth")
    v.check_void(f"{name} center bottom", hx, HOLE_Y, -3.9,
                 f"void at {name} center near bottom face")
    # Solid just outside through-hole radius (1.7 mm) but inside counterbore (2.85 mm)
    # At Z=-0.4 (above counterbore ceiling at Z=-0.80), this ring should be solid
    v.check_solid(f"{name} thin ring above CB", hx + 2.0, HOLE_Y, -0.4,
                  f"solid in thin ring above counterbore at {name}")

# 3. Counterbores — void in counterbore region (Z=-4 to Z=-0.80)
for name, hx in [("CB 1", HOLE1_X), ("CB 2", HOLE2_X)]:
    # Point inside counterbore but outside through-hole
    # CB radius = 2.85, through-hole radius = 1.7
    # Probe at radius 2.2 (between 1.7 and 2.85)
    probe_r = 2.2
    v.check_void(f"{name} annular void bottom", hx + probe_r, HOLE_Y, -3.5,
                 f"void in counterbore annulus at {name}, near bottom")
    v.check_void(f"{name} annular void mid", hx + probe_r, HOLE_Y, -2.0,
                 f"void in counterbore annulus at {name}, mid-depth")
    v.check_void(f"{name} annular void top", hx + probe_r, HOLE_Y, -1.0,
                 f"void in counterbore annulus at {name}, near CB ceiling")
    # Solid just above counterbore ceiling (Z=-0.80) in the annular region
    v.check_solid(f"{name} solid above CB ceiling", hx + probe_r, HOLE_Y, -0.4,
                  f"solid above counterbore at {name}")

# 4. Outside solid boundary — void
v.check_void("Above top face", 74.0, 30.0, 0.5,
             "void above plate")
v.check_void("Below bottom face", 74.0, 30.0, -4.5,
             "void below plate")
v.check_void("Left of plate", -0.5, 30.0, -2.0,
             "void left of plate")
v.check_void("Right of plate", 148.5, 30.0, -2.0,
             "void right of plate")

# --- Summary ---
if not v.summary():
    sys.exit(1)
