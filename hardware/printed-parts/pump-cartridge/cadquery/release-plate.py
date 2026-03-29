"""
Release Plate — CadQuery STEP generation script.

Generates the release plate (Part #4) for the pump cartridge assembly.
A 55 x 55 x 5 mm PETG plate with:
  - 4 stepped bores for John Guest fitting collet engagement
  - 4 guide post through-bores
  - 2 C-shaped linkage rod hooks on left/right edges

Coordinate system:
  Origin: lower-left-front corner of plate bounding box
  X: plate width, left to right, 0..55 mm
  Y: plate thickness (depth), front (user-facing) to back (dock-facing), 0..5 mm
  Z: plate height, bottom to top, 0..55 mm
  Envelope: 55 x 5 x 55 mm -> X:[0,55] Y:[0,5] Z:[0,55]
  Hooks extend beyond plate edges: X:[-3.65, 58.65]
"""

import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq
from step_validate import Validator

# ==================================================================
# Feature Planning Table (Rubric 1)
# ==================================================================
print("""
Feature Planning Table:
=======================
| # | Feature Name                    | Operation | Shape        | Axis | Center (X,Y,Z)        | Dimensions                              |
|---|--------------------------------|-----------|--------------|------|-----------------------|-----------------------------------------|
| 1 | Plate body                     | Add       | Box          | --   | (27.5, 2.5, 27.5)    | 55 x 5 x 55 mm                         |
| 2 | Plate corner fillets           | Modify    | Fillet       | Y    | 4 edges parallel to Y | R=1.0 mm                                |
| 3 | Stepped bore B1                | Remove    | Revolved     | Y    | (17.5, *, 17.5)      | 15.5/9.8/6.5 dia, steps at Y=1,3       |
| 4 | Stepped bore B2                | Remove    | Revolved     | Y    | (37.5, *, 17.5)      | Same as B1                              |
| 5 | Stepped bore B3                | Remove    | Revolved     | Y    | (17.5, *, 37.5)      | Same as B1                              |
| 6 | Stepped bore B4                | Remove    | Revolved     | Y    | (37.5, *, 37.5)      | Same as B1                              |
| 7 | Guide bore G1                  | Remove    | Revolved     | Y    | (5.5, *, 6.0)        | 3.8 dia, through, chamfers both faces   |
| 8 | Guide bore G2                  | Remove    | Revolved     | Y    | (49.5, *, 6.0)       | Same as G1                              |
| 9 | Guide bore G3                  | Remove    | Revolved     | Y    | (5.5, *, 49.0)       | Same as G1                              |
|10 | Guide bore G4                  | Remove    | Revolved     | Y    | (49.5, *, 49.0)      | Same as G1                              |
|11 | Left linkage rod hook          | Add+Remove| C-shape      | Y    | (0, 2.5, 27.5)       | 4.3 ID, 7.3 OD, 3mm gap, Y=1..4       |
|12 | Right linkage rod hook         | Add+Remove| C-shape      | Y    | (55, 2.5, 27.5)      | Same, mirrored                          |
""")

# ==================================================================
# Dimensions (all in mm, plate local frame)
# ==================================================================

# Plate body
PLATE_W = 55.0   # X
PLATE_D = 5.0    # Y (thickness)
PLATE_H = 55.0   # Z
FILLET_R = 1.0    # Corner fillets on Y-parallel edges

# Stepped bore positions (X, Z in plate frame)
BORE_POSITIONS = [
    (17.5, 17.5),  # B1 lower-left
    (37.5, 17.5),  # B2 lower-right
    (17.5, 37.5),  # B3 upper-left
    (37.5, 37.5),  # B4 upper-right
]

# Stepped bore dimensions
BORE_DIA_1 = 15.5   # Body end clearance counterbore
BORE_DEPTH_1 = 1.0  # Y=0 to Y=1
BORE_DIA_2 = 9.8    # Collet engagement counterbore
BORE_DEPTH_2 = 2.0  # Y=1 to Y=3
BORE_DIA_3 = 6.5    # Tube clearance through-hole
BORE_CHAMFER = 0.3   # 0.3mm x 45deg chamfer

# Guide bore positions (X, Z in plate frame)
GUIDE_POSITIONS = [
    (5.5, 6.0),    # G1 lower-left
    (49.5, 6.0),   # G2 lower-right
    (5.5, 49.0),   # G3 upper-left
    (49.5, 49.0),  # G4 upper-right
]

GUIDE_DIA = 3.8
GUIDE_CHAMFER = 0.3  # Both faces

# Linkage rod hooks
HOOK_ID = 4.3        # Internal diameter (for 4mm rod)
HOOK_OD = 7.3        # Outer diameter
HOOK_WALL = 1.5      # Wall thickness
HOOK_GAP = 3.0       # Opening width
HOOK_Y_START = 1.0   # Y start (within plate thickness)
HOOK_Y_END = 4.0     # Y end
HOOK_Y_DEPTH = HOOK_Y_END - HOOK_Y_START  # 3.0 mm
HOOK_Z_CENTER = 27.5 # Plate vertical center
HOOK_EXTENSION = HOOK_OD / 2  # 3.65 mm beyond plate edge

# ==================================================================
# Build Plate Body
# ==================================================================
print("Building plate body...")
plate = cq.Workplane("XY").box(PLATE_W, PLATE_D, PLATE_H, centered=False)

# Fillet the 4 long edges parallel to Y axis (corners of the plate)
# These are the edges at (0,*,0), (55,*,0), (0,*,55), (55,*,55)
plate = (
    plate
    .edges("|Y")
    .edges(
        cq.selectors.BoxSelector(
            (-0.1, -0.1, -0.1),
            (0.1, PLATE_D + 0.1, 0.1)
        )
        + cq.selectors.BoxSelector(
            (PLATE_W - 0.1, -0.1, -0.1),
            (PLATE_W + 0.1, PLATE_D + 0.1, 0.1)
        )
        + cq.selectors.BoxSelector(
            (-0.1, -0.1, PLATE_H - 0.1),
            (0.1, PLATE_D + 0.1, PLATE_H + 0.1)
        )
        + cq.selectors.BoxSelector(
            (PLATE_W - 0.1, -0.1, PLATE_H - 0.1),
            (PLATE_W + 0.1, PLATE_D + 0.1, PLATE_H + 0.1)
        )
    )
    .fillet(FILLET_R)
)

# ==================================================================
# Stepped Bores (4x) — revolved profiles cut from plate
# ==================================================================
print("Cutting stepped bores...")

# Profile for stepped bore (in R, Y space, revolved around Y axis)
# From user face (Y=0) to dock face (Y=5)
# With chamfers at the 15.5mm entry and the 9.8mm step
R1 = BORE_DIA_1 / 2   # 7.75
R2 = BORE_DIA_2 / 2   # 4.9
R3 = BORE_DIA_3 / 2   # 3.25
C = BORE_CHAMFER       # 0.3

# Bore profile points (R, Y) — trace the bore cross-section
# Starting from axis at user face, going clockwise
bore_profile_pts = [
    (0,        0),             # axis at user face (Y=0)
    (R1 - C,   0),             # chamfer start on 15.5mm bore entry
    (R1,       C),             # chamfer end
    (R1,       BORE_DEPTH_1 - C),  # 15.5mm bore wall approaching step
    (R2 + C,   BORE_DEPTH_1 - C),  # step to 9.8mm starts (chamfer start)
    (R2,       BORE_DEPTH_1),      # chamfer end at 9.8mm bore
    (R2,       BORE_DEPTH_1 + BORE_DEPTH_2),  # 9.8mm bore wall to Y=3
    (R3,       BORE_DEPTH_1 + BORE_DEPTH_2),  # step to 6.5mm (no chamfer here)
    (R3,       PLATE_D),       # 6.5mm through to dock face (Y=5)
    (0,        PLATE_D),       # axis at dock face
]

# Create the revolved bore tool (bore axis along Y)
bore_tool = (
    cq.Workplane("XY")
    .polyline(bore_profile_pts)
    .close()
    .revolve(360, (0, 0, 0), (0, 1, 0))
)

for cx, cz in BORE_POSITIONS:
    plate = plate.cut(bore_tool.translate((cx, 0, cz)))

# ==================================================================
# Guide Post Bores (4x) — revolved profiles with chamfers on both faces
# ==================================================================
print("Cutting guide post bores...")

RG = GUIDE_DIA / 2    # 1.9
CG = GUIDE_CHAMFER     # 0.3

# Guide bore profile (R, Y) — through-hole with chamfers on both faces
guide_profile_pts = [
    (0,        0),             # axis at user face
    (RG - CG,  0),             # chamfer start at user face
    (RG,       CG),            # chamfer end
    (RG,       PLATE_D - CG),  # bore wall approaching dock face
    (RG - CG,  PLATE_D),       # chamfer start at dock face
    (0,        PLATE_D),       # axis at dock face
]

# Revolved guide bore tool (creates the chamfered hole, but note: the profile
# above creates a solid of revolution. We need the profile to trace the bore wall
# and come back along the axis. Let me fix:
guide_bore_tool = (
    cq.Workplane("XY")
    .polyline(guide_profile_pts)
    .close()
    .revolve(360, (0, 0, 0), (0, 1, 0))
)

for gx, gz in GUIDE_POSITIONS:
    plate = plate.cut(guide_bore_tool.translate((gx, 0, gz)))

# ==================================================================
# Linkage Rod Hooks (2x, C-shaped, on left and right edges)
# ==================================================================
print("Building linkage rod hooks...")

# Hook geometry:
# C-shaped hook centered at (plate_edge_x, 2.5, 27.5) in plate frame
# Hook center is at the plate edge; half protrudes beyond
# The hook is an annular shape (OD=7.3, ID=4.3) with a 3mm gap opening
# Gap faces outward (away from plate center)
# Hook spans Y=1.0 to Y=4.0 (3mm depth, centered in plate thickness)

def make_hook(edge_x, opening_direction):
    """
    Create a C-shaped hook at the given X edge position.
    opening_direction: -1 for left hook (opens toward -X), +1 for right hook (opens toward +X)
    """
    # Hook center in XZ plane is at (edge_x, HOOK_Z_CENTER)
    hx = edge_x
    hz = HOOK_Z_CENTER

    r_outer = HOOK_OD / 2     # 3.65
    r_inner = HOOK_ID / 2     # 2.15

    # The gap opening width is 3.0mm. The gap is at the side facing outward.
    # Half gap = 1.5mm. The gap spans an angle at the outer radius.
    # The gap center line is along the X axis (toward the plate edge direction).
    # Gap half-angle at outer radius: asin(gap_half / r_outer)
    gap_half = HOOK_GAP / 2   # 1.5

    # Create the hook as extruded 2D shape on XZ workplane
    # We'll build it using CadQuery's 2D operations

    # Outer cylinder - inner cylinder = annular ring
    # Then cut the gap

    # Create outer cylinder along Y axis at (hx, hz)
    outer_cyl = (
        cq.Workplane("XZ")
        .center(hx, hz)
        .circle(r_outer)
        .extrude(-HOOK_Y_DEPTH)  # XZ normal is -Y; negative extrude goes +Y
        .translate((0, HOOK_Y_START, 0))
    )

    inner_cyl = (
        cq.Workplane("XZ")
        .center(hx, hz)
        .circle(r_inner)
        .extrude(-HOOK_Y_DEPTH)
        .translate((0, HOOK_Y_START, 0))
    )

    hook_solid = outer_cyl.cut(inner_cyl)

    # Cut the gap: a box that removes material in the gap opening direction
    # Gap is 3mm wide (in Z) centered on the hook center Z, extending outward in X
    # For left hook (opening_direction = -1): gap extends from hx toward -X
    # For right hook (opening_direction = +1): gap extends from hx toward +X

    if opening_direction < 0:
        # Left hook: gap extends from hx to hx - r_outer - 1
        gap_x_start = hx - r_outer - 1
        gap_x_size = r_outer + 1
    else:
        # Right hook: gap extends from hx to hx + r_outer + 1
        gap_x_start = hx
        gap_x_size = r_outer + 1

    gap_z_start = hz - gap_half

    gap_box = (
        cq.Workplane("XY")
        .transformed(offset=(gap_x_start, HOOK_Y_START, gap_z_start))
        .box(gap_x_size, HOOK_Y_DEPTH, HOOK_GAP, centered=False)
    )

    hook_solid = hook_solid.cut(gap_box)

    return hook_solid

# Left hook at X=0, opening toward -X
left_hook = make_hook(0, -1)
plate = plate.union(left_hook)

# Right hook at X=55, opening toward +X
right_hook = make_hook(PLATE_W, +1)
plate = plate.union(right_hook)

# ==================================================================
# Export STEP file
# ==================================================================
output_path = Path(__file__).parent / "release-plate.step"
cq.exporters.export(plate, str(output_path))
print(f"\nSTEP file exported to: {output_path}")

# ==================================================================
# Validation (Rubrics 3, 4, 5)
# ==================================================================
print("\n--- Validation ---\n")
v = Validator(plate)

# --- Plate body probes ---
v.check_solid("Plate body center", 27.5, 2.5, 27.5, "solid at plate center")
v.check_solid("Plate body corner near (1,2.5,1)", 1.5, 2.5, 1.5, "solid near corner")
v.check_solid("Plate body corner near (53.5,2.5,53.5)", 53.5, 2.5, 53.5, "solid near opposite corner")

# --- Stepped bore B1 (17.5, 17.5) ---
# Step 1: 15.5mm dia, Y=0 to Y=1 (void at center)
v.check_void("B1 step1 center", 17.5, 0.5, 17.5, "void in 15.5mm counterbore at Y=0.5")
# Just inside 15.5mm radius (R=7.75), should be void
v.check_void("B1 step1 near wall", 17.5 + 7.5, 0.5, 17.5, "void near 15.5mm bore wall")
# Just outside 15.5mm radius, should be solid
v.check_solid("B1 step1 outside", 17.5 + 8.0, 0.5, 17.5, "solid outside 15.5mm bore")

# Step 2: 9.8mm dia, Y=1 to Y=3 (void at center)
v.check_void("B1 step2 center", 17.5, 2.0, 17.5, "void in 9.8mm bore at Y=2.0")
v.check_void("B1 step2 near wall", 17.5 + 4.7, 2.0, 17.5, "void near 9.8mm bore wall")
v.check_solid("B1 step2 outside", 17.5 + 5.2, 2.0, 17.5, "solid outside 9.8mm bore")
# At Y=2.0, 15.5mm radius should be solid (only 15.5mm exists at Y<1)
v.check_solid("B1 15.5mm region at Y=2", 17.5 + 7.0, 2.0, 17.5, "solid in 15.5mm region at depth Y=2")

# Step 3: 6.5mm dia, Y=0 to Y=5 (through-hole, void at center)
v.check_void("B1 through-hole center Y=4", 17.5, 4.0, 17.5, "void in 6.5mm through-hole at Y=4")
v.check_void("B1 through-hole near wall", 17.5 + 3.0, 4.0, 17.5, "void near 6.5mm bore wall")
v.check_solid("B1 through-hole outside", 17.5 + 3.5, 4.0, 17.5, "solid outside 6.5mm bore at Y=4")

# --- Stepped bore B2 (37.5, 17.5) ---
v.check_void("B2 step1 center", 37.5, 0.5, 17.5, "void in B2 counterbore")
v.check_void("B2 step2 center", 37.5, 2.0, 17.5, "void in B2 collet bore")
v.check_void("B2 through-hole", 37.5, 4.0, 17.5, "void in B2 through-hole")

# --- Stepped bore B3 (17.5, 37.5) ---
v.check_void("B3 step1 center", 17.5, 0.5, 37.5, "void in B3 counterbore")
v.check_void("B3 step2 center", 17.5, 2.0, 37.5, "void in B3 collet bore")
v.check_void("B3 through-hole", 17.5, 4.0, 37.5, "void in B3 through-hole")

# --- Stepped bore B4 (37.5, 37.5) ---
v.check_void("B4 step1 center", 37.5, 0.5, 37.5, "void in B4 counterbore")
v.check_void("B4 step2 center", 37.5, 2.0, 37.5, "void in B4 collet bore")
v.check_void("B4 through-hole", 37.5, 4.0, 37.5, "void in B4 through-hole")

# --- Guide bore G1 (5.5, 6.0) ---
v.check_void("G1 center", 5.5, 2.5, 6.0, "void at guide bore G1 center")
v.check_void("G1 near wall", 5.5 + 1.7, 2.5, 6.0, "void near G1 bore wall")
v.check_solid("G1 outside", 5.5 + 2.2, 2.5, 6.0, "solid outside G1 bore")

# --- Guide bore G2 (49.5, 6.0) ---
v.check_void("G2 center", 49.5, 2.5, 6.0, "void at guide bore G2 center")

# --- Guide bore G3 (5.5, 49.0) ---
v.check_void("G3 center", 5.5, 2.5, 49.0, "void at guide bore G3 center")

# --- Guide bore G4 (49.5, 49.0) ---
v.check_void("G4 center", 49.5, 2.5, 49.0, "void at guide bore G4 center")

# --- Left hook at X=0, Z=27.5 ---
# Hook wall should be solid (outside the inner diameter, inside outer diameter)
# Hook center is at X=0, so hook extends from X=-3.65 to X=3.65
# Top of hook wall at Z = 27.5 + 3.65 = 31.15, probing at Z=30.5 (inside OD, outside ID)
v.check_solid("Left hook wall top", 0, 2.5, 27.5 + 3.0, "solid in left hook wall (top)")
v.check_solid("Left hook wall bottom", 0, 2.5, 27.5 - 3.0, "solid in left hook wall (bottom)")
# Hook interior (inside the 4.3mm ID) should be void
v.check_void("Left hook interior", 0, 2.5, 27.5, "void inside left hook bore")
# Hook extends beyond plate to X = -3.65
v.check_solid("Left hook extension", -2.0, 2.5, 27.5 + 3.0, "solid in left hook beyond plate edge")
# Gap opening: at the opening direction (-X side), Z = 27.5 (center), should be void
v.check_void("Left hook gap", -3.0, 2.5, 27.5, "void in left hook gap opening")

# --- Right hook at X=55, Z=27.5 ---
v.check_solid("Right hook wall top", 55, 2.5, 27.5 + 3.0, "solid in right hook wall (top)")
v.check_solid("Right hook wall bottom", 55, 2.5, 27.5 - 3.0, "solid in right hook wall (bottom)")
v.check_void("Right hook interior", 55, 2.5, 27.5, "void inside right hook bore")
v.check_solid("Right hook extension", 57.0, 2.5, 27.5 + 3.0, "solid in right hook beyond plate edge")
v.check_void("Right hook gap", 58.0, 2.5, 27.5, "void in right hook gap opening")

# --- Bounding box checks ---
bb = plate.val().BoundingBox()
print(f"\nBounding box: X=[{bb.xmin:.2f}, {bb.xmax:.2f}], Y=[{bb.ymin:.2f}, {bb.ymax:.2f}], Z=[{bb.zmin:.2f}, {bb.zmax:.2f}]")

# Hooks extend 3.65mm beyond each edge
v.check_bbox("X", bb.xmin, bb.xmax, -3.65, 58.65)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, 5.0)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, 55.0)

# --- Solid integrity ---
v.check_valid()
v.check_single_body()
v.check_volume(expected_envelope=PLATE_W * PLATE_D * PLATE_H, fill_range=(0.5, 1.2))

# --- Summary ---
if not v.summary():
    sys.exit(1)
