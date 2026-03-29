"""
Upper Cap — CadQuery STEP Generation Script
hardware/printed-parts/bag-frame/cad/upper-cap/generate_step_cadquery.py

Generates: upper-cap-cadquery.step

Sources:
  - hardware/printed-parts/bag-frame/planning/upper-cap/parts.md
  - hardware/printed-parts/bag-frame/planning/upper-cap/spatial-resolution.md
  - hardware/printed-parts/bag-frame/planning/upper-cap/decomposition.md
  - hardware/pipeline/steps/6-step-generation.md
"""

import sys
from pathlib import Path

# Validator import — tools/ is 5 levels up from this file's directory
# upper-cap/ -> cad/ -> bag-frame/ -> printed-parts/ -> hardware/ -> project root
sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "tools"))
from step_validate import Validator

import cadquery as cq

# =============================================================================
# Rubric 1 — Feature Planning Table
# =============================================================================
RUBRIC_TABLE = """
Rubric 1 — Feature Planning Table
==============================================================================================================
#   Feature Name              Mech. Function                    Op      Shape      Axis
    Center (X,Y,Z)            Dimensions                         Notes
--------------------------------------------------------------------------------------------------------------
1   Cap Body (flat plate)     Structural base; bag-contact face  Add     Box        Y
    (102, 0.75, 143.5)        X:0..204, Y:0..1.5, Z:0..287
                              204mm W x 1.5mm T x 287mm L

2   Rib L1 (longitudinal)     Plate stiffening; reduces span     Add     Box        Z
    (51, 3.5, 143.5)          X:50.4..51.6, Y:1.5..6.5, Z:0..287
                              1.2mm W x 5mm H x 287mm L

3   Rib L2 (longitudinal)     Plate stiffening; reduces span     Add     Box        Z
    (102, 3.5, 143.5)         X:101.4..102.6, Y:1.5..6.5, Z:0..287
                              1.2mm W x 5mm H x 287mm L

4   Rib L3 (longitudinal)     Plate stiffening; reduces span     Add     Box        Z
    (153, 3.5, 143.5)         X:152.4..153.6, Y:1.5..6.5, Z:0..287
                              1.2mm W x 5mm H x 287mm L

5   Rib T1 (transverse)       Plate stiffening; reduces span     Add     Box        X
    (102, 3.5, 95.7)          X:0..204, Y:1.5..6.5, Z:95.1..96.3
                              204mm L x 5mm H x 1.2mm W

6   Rib T2 (transverse)       Plate stiffening; reduces span     Add     Box        X
    (102, 3.5, 191.3)         X:0..204, Y:1.5..6.5, Z:190.7..191.9
                              204mm L x 5mm H x 1.2mm W

7   Left Arm 1 body           Cantilever snap arm; hook carrier  Add     Box        X
    (-10, 1.0, 40)            X:-20..0, Y:0..2, Z:37..43
                              20mm L x 2mm T x 6mm W

8   Left Arm 1 hook body      Hook retention; 90-deg face        Add     Box        X
    (-19.4, 0.6, 40)          X:-20..-18.8, Y:0.2..1.2, Z:37..43
                              1.2mm D x 1.0mm H x 6mm W (above bridge)

9   Left Arm 1 frangible      Designed support; breaks on snap   Add     Box        X
    (-19.4, 0.1, 40)          X:-20..-18.8, Y:0..0.2, Z:37..43
                              1.2mm D x 0.2mm H x 6mm W
                              (VOID after assembly; present in model)

10  Left Arm 2 body           Same as arm 1 but Z=247 center     Add     Box        X
    (-10, 1.0, 247)           X:-20..0, Y:0..2, Z:244..250

11  Left Arm 2 hook+bridge    Same geometry, Z=247 center        Add     Box        X
    (-19.4, 0.6, 247)         X:-20..-18.8, Y:0..1.2, Z:244..250

12  Right Arm 1 body          Cantilever snap arm; hook carrier  Add     Box        X
    (214, 1.0, 40)            X:204..224, Y:0..2, Z:37..43

13  Right Arm 1 hook body     Hook retention; 90-deg face        Add     Box        X
    (223.4, 0.6, 40)          X:222.8..224, Y:0.2..1.2, Z:37..43

14  Right Arm 1 frangible     Designed support; breaks on snap   Add     Box        X
    (223.4, 0.1, 40)          X:222.8..224, Y:0..0.2, Z:37..43

15  Right Arm 2 body          Same as right arm 1 but Z=247      Add     Box        X
    (214, 1.0, 247)           X:204..224, Y:0..2, Z:244..250

16  Right Arm 2 hook+bridge   Same geometry, Z=247 center        Add     Box        X
    (223.4, 0.6, 247)         X:222.8..224, Y:0..1.2, Z:244..250

17  Arm root fillets (x4)     Stress reduction at arm junctions  Fillet  Round      —
    At X=0 and X=204mm         1mm radius on arm-body edges

18  Perimeter chamfer         Elephant's foot mitigation;        Chamfer Angled     —
    Cap body outer top edges   visual engagement cue; 45-deg
                              1.5mm x 45-deg on Y=1.5mm perimeter
                              of cap body (not arm edges)
==============================================================================================================
"""

# =============================================================================
# Rubric 2 — Coordinate System
# =============================================================================
# Origin: bag-contact face (Y=0), left body edge (X=0), cap-end face (Z=0)
# X: left-to-right across cap width (0 = left body edge, 204 = right body edge)
#    arms extend to X=-20 (left) and X=224 (right)
# Y: perpendicular to bag face, 0 = bag face (build plate), 6.5 = rib tips
# Z: along cap length, 0 = cap-end face, 287 = fold-end face
# Envelope: X:[-20, 224] (244mm total), Y:[0, 6.5], Z:[0, 287]

print(RUBRIC_TABLE)

print("Rubric 2 — Coordinate System")
print("=" * 60)
print("Origin: bag-contact face (Y=0), left body edge (X=0), cap-end face (Z=0)")
print("X: 0 = left body edge, 204 = right body edge")
print("   Arms: left X=-20..0, right X=204..224")
print("Y: 0 = bag-contact face (build plate), 6.5 = rib tips")
print("Z: 0 = cap-end face, 287 = fold-end face")
print("Envelope: X:[-20, 224] Y:[0, 6.5] Z:[0, 287]")
print()

# =============================================================================
# Feature 1 — Cap Body (flat plate)
# X:[0, 204], Y:[0, 1.5], Z:[0, 287]
# =============================================================================
print("Building Feature 1: Cap Body...")
result = cq.Workplane("XY").box(204, 1.5, 287, centered=False)
# Note: centered=False means X:[0,204], Y:[0,1.5], Z:[0,287] - correct

# =============================================================================
# Feature 2-4 — 3 Longitudinal Ribs
# Each: 1.2mm wide (X), 5mm tall (Y=1.5..6.5), 287mm long (Z=0..287)
# translate(x_min, y_base, z_base) where y_base=1.5
# =============================================================================
print("Building Features 2-4: Longitudinal Ribs...")

# Rib L1: X:[50.4, 51.6]
rib_l1 = cq.Workplane("XY").box(1.2, 5.0, 287, centered=False).translate((50.4, 1.5, 0))
result = result.union(rib_l1)

# Rib L2: X:[101.4, 102.6]
rib_l2 = cq.Workplane("XY").box(1.2, 5.0, 287, centered=False).translate((101.4, 1.5, 0))
result = result.union(rib_l2)

# Rib L3: X:[152.4, 153.6]
rib_l3 = cq.Workplane("XY").box(1.2, 5.0, 287, centered=False).translate((152.4, 1.5, 0))
result = result.union(rib_l3)

# =============================================================================
# Features 5-6 — 2 Transverse Ribs
# Each: 204mm long (X=0..204), 5mm tall (Y=1.5..6.5), 1.2mm wide (Z)
# =============================================================================
print("Building Features 5-6: Transverse Ribs...")

# Rib T1: Z:[95.1, 96.3] — center Z=95.7
rib_t1 = cq.Workplane("XY").box(204, 5.0, 1.2, centered=False).translate((0, 1.5, 95.1))
result = result.union(rib_t1)

# Rib T2: Z:[190.7, 191.9] — center Z=191.3
rib_t2 = cq.Workplane("XY").box(204, 5.0, 1.2, centered=False).translate((0, 1.5, 190.7))
result = result.union(rib_t2)

# =============================================================================
# Features 7-16 — 4 Snap Arms (body + hook including frangible bridge)
#
# Each arm:
#   - Arm body: 20mm long (X), 2mm thick (Y=0..2), 6mm wide (Z)
#   - Hook body (full including frangible): 1.2mm deep (X), 1.2mm tall (Y=0..1.2), 6mm wide (Z)
#     This includes the 0.2mm frangible bridge at Y=0..0.2
#     The hook proper is Y=0.2..1.2; the frangible bridge is Y=0..0.2
#     We model the FULL hook (Y=0..1.2) as per spec — the bridge IS present
#     (it breaks during assembly, not in the model)
#
# Left arms: root at X=0, tip at X=-20, hook protrudes in +X from tip
#   Hook at X=-20..-18.8
# Right arms: root at X=204, tip at X=224, hook protrudes in -X from tip
#   Hook at X=222.8..224
# =============================================================================
print("Building Features 7-16: Snap Arms...")

# --- Left Arm 1 (Z center = 40mm, Z:[37, 43]) ---
arm_l1_body = cq.Workplane("XY").box(20, 2.0, 6, centered=False).translate((-20, 0, 37))
result = result.union(arm_l1_body)

# Hook full (Y=0..1.2 includes frangible bridge Y=0..0.2)
hook_l1 = cq.Workplane("XY").box(1.2, 1.2, 6, centered=False).translate((-20, 0, 37))
result = result.union(hook_l1)

# --- Left Arm 2 (Z center = 247mm, Z:[244, 250]) ---
arm_l2_body = cq.Workplane("XY").box(20, 2.0, 6, centered=False).translate((-20, 0, 244))
result = result.union(arm_l2_body)

hook_l2 = cq.Workplane("XY").box(1.2, 1.2, 6, centered=False).translate((-20, 0, 244))
result = result.union(hook_l2)

# --- Right Arm 1 (Z center = 40mm, Z:[37, 43]) ---
arm_r1_body = cq.Workplane("XY").box(20, 2.0, 6, centered=False).translate((204, 0, 37))
result = result.union(arm_r1_body)

# Hook: X=[222.8, 224], protrudes in -X from tip X=224
hook_r1 = cq.Workplane("XY").box(1.2, 1.2, 6, centered=False).translate((222.8, 0, 37))
result = result.union(hook_r1)

# --- Right Arm 2 (Z center = 247mm, Z:[244, 250]) ---
arm_r2_body = cq.Workplane("XY").box(20, 2.0, 6, centered=False).translate((204, 0, 244))
result = result.union(arm_r2_body)

hook_r2 = cq.Workplane("XY").box(1.2, 1.2, 6, centered=False).translate((222.8, 0, 244))
result = result.union(hook_r2)

# =============================================================================
# Cut frangible bridge voids
# The frangible bridge is modeled as PRESENT (Y=0..0.2 of the hook zone)
# but we must NOT cut it — the spec says the 0.2mm bridge IS present in the
# printed model; it breaks during assembly.
# The validation check_void() for the frangible bridge location should be VOID
# because the void is at Y=0..0.2 BETWEEN the hook and the arm body.
#
# Wait — re-reading the spec carefully:
# "model the hook with Y_bottom = 0.2mm (i.e., a 0.2mm-thick base connecting
#  hook to arm body at Y=0 to Y=0.2mm). This creates the frangible connection."
#
# The frangible bridge IS the 0.2mm material. The validation calls check_void()
# at Y=0.1 — but the spec says the bridge IS material at Y=0..0.2.
#
# Re-reading validation requirements:
#   check_void() at left frangible bridge 1: (-19.4, 0.1, 40)
#   "should be void after the 0.2mm cut"
#
# So the task prompt says to CUT a 0.2mm void at the bridge location.
# This means: model hook from Y=0.2 to Y=1.2, then cut Y=0..0.2 from hook zone.
# Or: model full hook Y=0..1.2, then cut Y=0..0.2 void from hook zone.
#
# The void cut creates the gap between hook bottom and arm body, matching
# requirements.md "0.2mm interface gap between the support surface and the
# part surface it supports."
#
# In the physical print, the gap (void) means the hook bottom is unsupported.
# The slicer bridges this 0.2mm gap with a thin connection that breaks cleanly.
# So the VOID in the model represents the gap — the slicer/printer produces
# the bridging material. The 0.2mm void IS the frangible bridge geometry.
#
# Therefore: cut the 0.2mm void boxes from the assembled result.
# =============================================================================
print("Cutting frangible bridge voids...")

# Left Arm 1 frangible bridge void: X=[-20, -18.8], Y=[0, 0.2], Z=[37, 43]
void_l1 = cq.Workplane("XY").box(1.2, 0.2, 6, centered=False).translate((-20, 0, 37))
result = result.cut(void_l1)

# Left Arm 2 frangible bridge void: X=[-20, -18.8], Y=[0, 0.2], Z=[244, 250]
void_l2 = cq.Workplane("XY").box(1.2, 0.2, 6, centered=False).translate((-20, 0, 244))
result = result.cut(void_l2)

# Right Arm 1 frangible bridge void: X=[222.8, 224], Y=[0, 0.2], Z=[37, 43]
void_r1 = cq.Workplane("XY").box(1.2, 0.2, 6, centered=False).translate((222.8, 0, 37))
result = result.cut(void_r1)

# Right Arm 2 frangible bridge void: X=[222.8, 224], Y=[0, 0.2], Z=[244, 250]
void_r2 = cq.Workplane("XY").box(1.2, 0.2, 6, centered=False).translate((222.8, 0, 244))
result = result.cut(void_r2)

# =============================================================================
# Feature 17 — Root Fillets (1.0mm radius at arm-body junctions)
# The arm roots are where the arms meet the cap body edges:
#   Left arms: at X=0 face of arm body
#   Right arms: at X=204 face of arm body
#
# Strategy: add small gusset triangular prisms at each root corner instead,
# or use the OCC shape.fillet() directly via val().
# CadQuery BoxSelector for edge selection can be fragile; use a simpler approach:
# select all edges in the arm zone by proximity to the root X face.
# =============================================================================
print("Applying arm root fillets...")

# Use OCC direct approach: select edges near the arm roots using a lambda filter
# The arm root edges at X=0 (left) are Z-parallel edges at X=0, Y=0..2
# The arm root edges at X=204 (right) are Z-parallel edges at X=204, Y=0..2

def fillet_arm_root(shape, x_root, z_lo, z_hi, r=1.0):
    """Apply fillet to arm root edges at given X root, Z range."""
    try:
        # Use NearestToPointSelector to find edges at the root
        # Filter: edges parallel to Z within the arm zone
        result = (
            shape
            .edges("|Z")
            .edges(cq.selectors.BoxSelector(
                (x_root - 0.05, -0.05, z_lo - 0.05),
                (x_root + 0.05, 2.05, z_hi + 0.05)
            ))
            .fillet(r)
        )
        return result, True
    except Exception as e:
        return shape, False

result, ok = fillet_arm_root(result, 0.0, 37.0, 43.0)
if not ok:
    print("  Warning: Left arm 1 root fillet skipped (edge topology)")

result, ok = fillet_arm_root(result, 0.0, 244.0, 250.0)
if not ok:
    print("  Warning: Left arm 2 root fillet skipped (edge topology)")

result, ok = fillet_arm_root(result, 204.0, 37.0, 43.0)
if not ok:
    print("  Warning: Right arm 1 root fillet skipped (edge topology)")

result, ok = fillet_arm_root(result, 204.0, 244.0, 250.0)
if not ok:
    print("  Warning: Right arm 2 root fillet skipped (edge topology)")

# =============================================================================
# Feature 18 — Perimeter Chamfer (1.5mm × 45° on cap body top face perimeter)
# The chamfer is on the 4 long edges at Y=1.5mm on the cap body:
#   - Left edge: (X=0, Y=1.5mm) running Z=0..287
#   - Right edge: (X=204, Y=1.5mm) running Z=0..287
#   - Cap-end edge: (Z=0, Y=1.5mm) running X=0..204
#   - Fold-end edge: (Z=287, Y=1.5mm) running X=0..204
# NOT on the rib tops and NOT on arm edges.
#
# Strategy: apply chamfer to each perimeter edge separately, one at a time.
# =============================================================================
print("Applying perimeter chamfer...")

def chamfer_edge(shape, selector_str, bbox, c=1.5):
    """Try to chamfer edges matching selector_str within bbox."""
    try:
        r = shape.edges(selector_str).edges(cq.selectors.BoxSelector(*bbox)).chamfer(c)
        return r, True
    except Exception as e:
        return shape, str(e)

# Left long edge: Z-parallel at X≈0, Y≈1.5
result, ok = chamfer_edge(result, "|Z",
    [(-0.05, 1.45, -0.05), (0.05, 1.55, 287.05)])
if ok is not True:
    print(f"  Warning: Left perimeter chamfer skipped: {ok}")

# Right long edge: Z-parallel at X≈204, Y≈1.5
result, ok = chamfer_edge(result, "|Z",
    [(203.95, 1.45, -0.05), (204.05, 1.55, 287.05)])
if ok is not True:
    print(f"  Warning: Right perimeter chamfer skipped: {ok}")

# Cap-end short edge: X-parallel at Z≈0, Y≈1.5
result, ok = chamfer_edge(result, "|X",
    [(-0.05, 1.45, -0.05), (204.05, 1.55, 0.05)])
if ok is not True:
    print(f"  Warning: Cap-end perimeter chamfer skipped: {ok}")

# Fold-end short edge: X-parallel at Z≈287, Y≈1.5
result, ok = chamfer_edge(result, "|X",
    [(-0.05, 1.45, 286.95), (204.05, 1.55, 287.05)])
if ok is not True:
    print(f"  Warning: Fold-end perimeter chamfer skipped: {ok}")

print("Model complete. Running validation...")

# =============================================================================
# Validation
# =============================================================================
print()
print("Rubric 3 — Feature-Specification Reconciliation")
print("=" * 60)

v = Validator(result)

# Cap body
v.check_solid("Cap body center", 102, 0.75, 143.5)

# Longitudinal ribs
v.check_solid("Rib L1 center", 51, 3.5, 143.5)
v.check_solid("Rib L2 center", 102, 3.5, 143.5)
v.check_solid("Rib L3 center", 153, 3.5, 143.5)

# Transverse ribs
v.check_solid("Rib T1 center", 102, 3.5, 95.7)
v.check_solid("Rib T2 center", 102, 3.5, 191.3)

# Snap arms — bodies
v.check_solid("Left arm 1 center", -10, 1, 40)
v.check_solid("Right arm 1 center", 214, 1, 40)
v.check_solid("Left arm 2 center", -10, 1, 247)
v.check_solid("Right arm 2 center", 214, 1, 247)

# Hooks (above frangible bridge, Y=0.6 is in Y=0.2..1.2 hook zone)
v.check_solid("Left hook 1", -19.4, 0.6, 40)
v.check_solid("Right hook 1", 223.4, 0.6, 40)

# Frangible bridge voids (Y=0.1 is in Y=0..0.2 void zone)
v.check_void("Left frangible bridge 1", -19.4, 0.1, 40)
v.check_void("Right frangible bridge 1", 223.4, 0.1, 40)

# Solid validity
v.check_valid()
v.check_single_body()

# Volume check: envelope = 244 * 6.5 * 287 = 455,638 mm³
# Actual volume much less due to partial fill; expected fill ~10-25%
envelope_vol = 244 * 6.5 * 287
v.check_volume(expected_envelope=envelope_vol, fill_range=(0.03, 0.5))

# Bounding box
bb = result.val().BoundingBox()
print(f"\nBounding box: X=[{bb.xmin:.2f}, {bb.xmax:.2f}] Y=[{bb.ymin:.2f}, {bb.ymax:.2f}] Z=[{bb.zmin:.2f}, {bb.zmax:.2f}]")
v.check_bbox("X", bb.xmin, bb.xmax, -20.0, 224.0)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, 6.5)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, 287.0)

# Summary
passed = v.summary()

# =============================================================================
# Export STEP
# =============================================================================
out_path = Path(__file__).resolve().parent / "upper-cap-cadquery.step"
cq.exporters.export(result, str(out_path))
print(f"\nExported: {out_path}")

if not passed:
    sys.exit(1)
