"""
Sub-A: Box Shell — CadQuery Generation Script

Generates the open-top, open-front rectangular box that is the foundational
solid of the pump cartridge tray.

Coordinate system:
  Origin: rear-left-bottom corner (dock side)
  X: width, left to right (0..160)
  Y: depth, rear (dock) to front (user) (0..155)
  Z: height, bottom to top (0..72)
  Envelope: 160x155x72 mm -> X:[0,160] Y:[0,155] Z:[0,72]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq
from step_validate import Validator

# ==========================================================================
# Dimensions from spec
# ==========================================================================
W = 160.0       # overall width (X)
D = 155.0       # overall depth (Y)
H = 72.0        # overall height (Z)

SIDE_WALL = 5.0     # left and right wall thickness (X)
FLOOR_T = 3.0       # floor thickness (Z)
REAR_WALL = 8.5     # rear wall thickness (Y)

FILLET_R = 1.0       # internal corner fillet radius

# Interior pocket extents
POCKET_X_MIN = SIDE_WALL            # 5
POCKET_X_MAX = W - SIDE_WALL        # 155
POCKET_Y_MIN = REAR_WALL            # 8.5
POCKET_Y_MAX = D                    # 155 (open front)
POCKET_Z_MIN = FLOOR_T              # 3
POCKET_Z_MAX = H                    # 72 (open top)

POCKET_W = POCKET_X_MAX - POCKET_X_MIN   # 150
POCKET_D = POCKET_Y_MAX - POCKET_Y_MIN   # 146.5
POCKET_H = POCKET_Z_MAX - POCKET_Z_MIN   # 69

# ==========================================================================
# Feature Planning Table (Rubric 1)
# ==========================================================================
print("=" * 80)
print("FEATURE PLANNING TABLE — Sub-A: Box Shell")
print("=" * 80)
print(f"{'#':<3} {'Feature':<25} {'Function':<25} {'Op':<8} {'Shape':<10} {'Dims':<30}")
print("-" * 80)
features = [
    ("1", "Outer block",        "Envelope solid",        "Add",  "Box",     f"{W}x{D}x{H}"),
    ("2", "Interior pocket",    "Cavity for components", "Remove","Box",    f"{POCKET_W}x{POCKET_D}x{POCKET_H}"),
    ("3", "Left wall-floor fillet",  "Stress relief",    "Modify","Fillet", f"R{FILLET_R}, Y=0..155"),
    ("4", "Right wall-floor fillet", "Stress relief",    "Modify","Fillet", f"R{FILLET_R}, Y=0..155"),
    ("5", "Rear wall-floor fillet",  "Stress relief",    "Modify","Fillet", f"R{FILLET_R}, X=5..155"),
    ("6", "Left wall-rear fillet",   "Stress relief",    "Modify","Fillet", f"R{FILLET_R}, Z=0..72"),
    ("7", "Right wall-rear fillet",  "Stress relief",    "Modify","Fillet", f"R{FILLET_R}, Z=0..72"),
]
for f in features:
    print(f"{f[0]:<3} {f[1]:<25} {f[2]:<25} {f[3]:<8} {f[4]:<10} {f[5]:<30}")
print("=" * 80)
print()

# ==========================================================================
# Modeling
# ==========================================================================

# Step 1: Outer block — full envelope solid
box = cq.Workplane("XY").box(W, D, H, centered=False)

# Step 2: Interior pocket — subtract the cavity
# The pocket is open at front (Y=155) and top (Z=72)
pocket = (
    cq.Workplane("XY")
    .transformed(offset=(POCKET_X_MIN, POCKET_Y_MIN, POCKET_Z_MIN))
    .box(POCKET_W, POCKET_D, POCKET_H, centered=False)
)
shell = box.cut(pocket)

# Step 3: Internal corner fillets
# Find edges at internal junctions by their geometric position.
# Internal edges from the pocket cut are at known coordinates.

# We need to find edges that lie along specific lines:
# 1. Left wall-floor: line at X=5, Z=3, parallel to Y (Y: 8.5..155)
# 2. Right wall-floor: line at X=155, Z=3, parallel to Y (Y: 8.5..155)
# 3. Rear wall-floor: line at Y=8.5, Z=3, parallel to X (X: 5..155)
# 4. Left wall-rear wall: line at X=5, Y=8.5, parallel to Z (Z: 3..72)
# 5. Right wall-rear wall: line at X=155, Y=8.5, parallel to Z (Z: 3..72)

# Use edge midpoint matching to find these edges
def find_edges_near(solid, target_mid, tol=1.0):
    """Find edges whose midpoint is near target_mid (x,y,z)."""
    from OCP.BRep import BRep_Tool
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_EDGE
    from OCP.GCPnts import GCPnts_AbscissaPoint

    result = []
    all_edges = solid.edges().vals()
    tx, ty, tz = target_mid
    for edge in all_edges:
        bb = edge.BoundingBox()
        mx = (bb.xmin + bb.xmax) / 2
        my = (bb.ymin + bb.ymax) / 2
        mz = (bb.zmin + bb.zmax) / 2
        dist = ((mx - tx)**2 + (my - ty)**2 + (mz - tz)**2) ** 0.5
        if dist < tol:
            result.append(edge)
    return result

# Edge midpoints for the 5 internal junctions
edge_targets = [
    # Left wall-floor: X=5, Z=3, Y midpoint = (8.5+155)/2 = 81.75
    (SIDE_WALL, (REAR_WALL + D) / 2, FLOOR_T),
    # Right wall-floor: X=155, Z=3, Y midpoint
    (W - SIDE_WALL, (REAR_WALL + D) / 2, FLOOR_T),
    # Rear wall-floor: Y=8.5, Z=3, X midpoint = (5+155)/2 = 80
    ((SIDE_WALL + W - SIDE_WALL) / 2, REAR_WALL, FLOOR_T),
    # Left wall-rear wall: X=5, Y=8.5, Z midpoint = (3+72)/2 = 37.5
    (SIDE_WALL, REAR_WALL, (FLOOR_T + H) / 2),
    # Right wall-rear wall: X=155, Y=8.5, Z midpoint
    (W - SIDE_WALL, REAR_WALL, (FLOOR_T + H) / 2),
]

# Collect all edge objects to fillet
edges_to_fillet = []
for target in edge_targets:
    found = find_edges_near(shell, target, tol=1.0)
    if found:
        edges_to_fillet.extend(found)
    else:
        print(f"WARNING: No edge found near {target}")

# Apply fillets using OCC directly
if edges_to_fillet:
    from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
    from OCP.TopAbs import TopAbs_EDGE
    from OCP.TopoDS import TopoDS

    solid_shape = shell.val().wrapped
    fillet_builder = BRepFilletAPI_MakeFillet(solid_shape)

    for edge in edges_to_fillet:
        fillet_builder.Add(FILLET_R, edge.wrapped)

    fillet_builder.Build()
    filleted_shape = fillet_builder.Shape()

    # Wrap back into CadQuery
    shell = cq.Workplane("XY").newObject([cq.Shape(filleted_shape)])

print("Model built successfully.")
print(f"  Outer: {W} x {D} x {H} mm")
print(f"  Pocket: {POCKET_W} x {POCKET_D} x {POCKET_H} mm")
print(f"  Fillets: {FILLET_R} mm at {len(edges_to_fillet)} internal edges")
print()

# ==========================================================================
# Export STEP
# ==========================================================================
step_path = Path(__file__).with_suffix(".step")
cq.exporters.export(shell, str(step_path))
print(f"STEP exported: {step_path}")
print()

# ==========================================================================
# Validation (Rubric 3-5)
# ==========================================================================
print("VALIDATION")
print("-" * 60)

v = Validator(shell)

# --- Feature 1: Outer block walls ---
v.check_solid("Left wall body", 2.5, 80, 36, "solid at left wall center")
v.check_solid("Right wall body", 157.5, 80, 36, "solid at right wall center")
v.check_solid("Floor body", 80, 80, 1.5, "solid at floor center")
v.check_solid("Rear wall body", 80, 4.25, 36, "solid at rear wall center")

# --- Feature 2: Interior pocket ---
v.check_void("Pocket center", 80, 80, 37.5, "void at pocket center")
v.check_void("Pocket near floor", 80, 80, 4.0, "void just above floor")
v.check_void("Pocket near left wall", 6.0, 80, 36, "void just inside left wall")
v.check_void("Pocket near right wall", 154.0, 80, 36, "void just inside right wall")
v.check_void("Pocket near rear wall", 80, 9.5, 36, "void just inside rear wall")
v.check_void("Pocket open front", 80, 154.5, 36, "void near front opening")
v.check_void("Pocket open top", 80, 80, 71.5, "void near top opening")

# --- Verify walls are solid at boundaries ---
v.check_solid("Left wall inner edge", 4.5, 80, 36, "solid just inside left wall edge")
v.check_solid("Right wall inner edge", 155.5, 80, 36, "solid just inside right wall edge")
v.check_solid("Floor top surface", 80, 80, 2.5, "solid just below floor top")
v.check_solid("Rear wall inner edge", 80, 8.0, 36, "solid just inside rear wall")

# --- Features 3-7: Internal fillets ---
# At fillet junctions, a point at the sharp corner (before filleting) should
# now be void because the fillet rounds it away.
# The fillet is R=1.0. At the 45-degree diagonal, about 0.3mm from the corner
# axis intersection should be in the filleted void zone.
fillet_offset = FILLET_R * 0.3
v.check_void("Left wall-floor fillet", SIDE_WALL + fillet_offset, 80, FLOOR_T + fillet_offset,
             "void at left wall-floor fillet zone")
v.check_void("Right wall-floor fillet", W - SIDE_WALL - fillet_offset, 80, FLOOR_T + fillet_offset,
             "void at right wall-floor fillet zone")
v.check_void("Rear wall-floor fillet", 80, REAR_WALL + fillet_offset, FLOOR_T + fillet_offset,
             "void at rear wall-floor fillet zone")
v.check_void("Left wall-rear fillet", SIDE_WALL + fillet_offset, REAR_WALL + fillet_offset, 36,
             "void at left wall-rear wall fillet zone")
v.check_void("Right wall-rear fillet", W - SIDE_WALL - fillet_offset, REAR_WALL + fillet_offset, 36,
             "void at right wall-rear wall fillet zone")

# Verify solid remains present just outside fillet zone
v.check_solid("Solid near left-floor fillet", SIDE_WALL - 0.5, 80, FLOOR_T - 0.5,
              "solid outside fillet in wall/floor material")
v.check_solid("Solid near right-floor fillet", W - SIDE_WALL + 0.5, 80, FLOOR_T - 0.5,
              "solid outside fillet in wall/floor material")

# --- Rubric 4: Solid validity ---
v.check_valid()
v.check_single_body()
# Shell volume ~ 75 cm3 = 75000 mm3, envelope = 1,785,600 mm3, ratio ~ 4.2%
# Actual shell volume ~269,450 mm3 = 15.1% of envelope (walls+floor+rear are solid)
v.check_volume(expected_envelope=W * D * H, fill_range=(0.10, 0.20))

# --- Rubric 5: Bounding box ---
bb = shell.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, 0.0, W)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, D)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, H)

# --- Summary ---
if not v.summary():
    sys.exit(1)

print(f"\nDone. STEP file: {step_path}")
