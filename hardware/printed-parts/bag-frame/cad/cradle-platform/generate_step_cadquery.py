"""
Cradle Platform — CadQuery STEP Generation Script
hardware/printed-parts/bag-frame/cad/cradle-platform/generate_step_cadquery.py

Generates: cradle-platform-cadquery.step

Sources:
  - hardware/printed-parts/bag-frame/planning/cradle-platform/parts.md
  - hardware/printed-parts/bag-frame/planning/cradle-platform/spatial-resolution.md
  - hardware/printed-parts/bag-frame/planning/cradle-platform/decomposition.md
  - hardware/pipeline/steps/6-step-generation.md
"""

import sys
import math
from pathlib import Path

# Validator import — tools/ is 5 levels up from this file's directory
sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "tools"))
from step_validate import Validator

import cadquery as cq

# =============================================================================
# Rubric 1 — Feature Planning Table
# =============================================================================
RUBRIC_TABLE = """
Rubric 1 — Feature Planning Table
==================================================================================================
#   Feature Name                    Mech. Function              Op      Shape       Axis
    Center (X,Y,Z)                  Dimensions                  Notes
--------------------------------------------------------------------------------------------------
1   Cradle Body (arc extrusion)     Bowl floor + lip substrate  Add     Arc+shelf   Z
    (98, 6.75, 143.5)              R=341mm arc, chord 190mm,
                                    sagitta 13.5mm, floor 2mm,
                                    lips 10mm tall, 4mm thick,
                                    287mm long

2   Side Lips (left+right)          Lateral bag retention;      (incl   Rect wall   Z
    L: (-2, 8.5, 143.5)            snap rebate host;           in 1)
    R: (198, 8.5, 143.5)           snap tab root host
                                    L: X=-4..0, Y=3.5..13.5
                                    R: X=196..200, Y=3.5..13.5

3   Structural Ribs x3              Floor stiffening            Add     Rect prism  Z
    Rib1: (50.5, 8.3, 143.5)       reduce effective span       1.6mm W, 6mm H,
    Rib2: (98,   5.0, 143.5)       to 47.5mm cells            from floor outer
    Rib3: (145.5,8.3, 143.5)

4   Cap-End Pocket                  Capture Platypus cap;       Remove  Cylinder    Z
    (98, 0, 25)                    arrest Z sliding            31.2mm ID, 50mm deep
                                                                Z=0..50mm

5   Tube Exit Hole                  Route 1/4-in OD tube        Remove  Cylinder    Y
    (98, ~5, 25)                   from pocket to enclosure    12mm dia, Y-axis,
                                                                at Z=25mm

6   Snap Tabs x4 (inboard edge)     Snap cradle to spine;       Add     Rect beam   -X
    T1-4: (-11.5, 8.5, 97/145/192/240) permanent retention    8mm Z, 2mm Y, 15mm X
                                                                hook 1.2mm in +Y

7   Interior Corner Fillet (3mm)    Prevent stress on bag seams Fillet  Concave arc —
                                    arc-to-shelf and            R=3mm at 4 Z-edges
                                    shelf-to-lip corners

8   Lip Top Edge Fillet (1.5mm)     Finished edge appearance    Fillet  Convex arc  —
                                    4 long Z-edges at Y=3.5mm  R=1.5mm

9   Snap Arm Rebate x2              Upper cap hook engagement   Remove  Rect slot   Z
    L: (-3.4, 5.5, 143.5)         groove on lip outer faces   1.2mm X x 1.2mm Y,
    R: (199.4, 5.5, 143.5)                                     Y=4.9..6.1mm, full Z

10  Cap-End Solid Terminus Z=0      Structural terminus;        (incl)  Face        —
                                    transmits Z-sliding load

11  Fold-End Lead-in Chamfer Z=287  Guide bag fold into spine   Remove  Wedge prism Z
    inner face at Z=284..287        slot during assembly        3mm x 45-deg
==================================================================================================
"""

# =============================================================================
# Rubric 2 — Coordinate System Declaration
# =============================================================================
COORD_SYS = """
Rubric 2 — Coordinate System Declaration
=========================================
# Coordinate system:
#   Origin: Left lip inner face (X=0), bowl deepest point (Y=0), cap-end face (Z=0)
#   X: Width left→right; X=-4mm (left lip outer) to X=200mm (right lip outer)
#        Snap tabs extend to X=-19mm
#   Y: Depth outward from bowl; Y=0 (bowl center inner) to Y=15.5mm (floor outer at arc edge)
#        Ribs extend to Y=11.3mm (Ribs 1,3), Y=8.0mm (Rib 2)
#   Z: Print axis; Z=0 (cap end, build plate) to Z=287mm (fold end)
#   Envelope (base body): 204mm X (-4 to 200) x 15.5mm Y x 287mm Z
#             Tabs extend X to -19mm
"""

print(RUBRIC_TABLE)
print(COORD_SYS)

# =============================================================================
# Dimensional constants (from spatial-resolution.md and parts.md)
# =============================================================================

# Arc geometry
R_ARC         = 341.0
X_ARC_CENTER  = 98.0
X_ARC_LEFT    = 3.0    # left arc tangent point X
X_ARC_RIGHT   = 193.0  # right arc tangent point X
Y_ARC_TANG    = 13.5   # Y at arc tangent points (= lip base = shelf inner face)
FLOOR_THICK   = 2.0    # floor wall thickness in Y direction
Z_TOTAL       = 287.0

# Lip geometry
Y_LIP_TOP     = 3.5    # lip top edge Y (= bag side)
Y_LIP_BASE    = 13.5   # lip base Y (= arc tangent level)
X_LIP_L_INNER = 0.0
X_LIP_L_OUTER = -4.0
X_LIP_R_INNER = 196.0
X_LIP_R_OUTER = 200.0
LIP_THICK     = 4.0    # lip thickness in X
LIP_HEIGHT    = 10.0   # = Y_LIP_BASE - Y_LIP_TOP

# Shelf geometry (connects lip base to arc tangent)
X_SHELF_L_RIGHT = X_ARC_LEFT   # = 3.0mm
X_SHELF_R_LEFT  = X_ARC_RIGHT  # = 193.0mm
Y_SHELF_LO      = Y_ARC_TANG   # = 13.5mm (inner face, same as arc tangent)
Y_SHELF_HI      = Y_ARC_TANG + FLOOR_THICK  # = 15.5mm (outer face)

# Arc profile helpers
def y_inner(x):
    """Y of bowl inner surface at given X (Y=0 at X=98, Y=13.5 at X=3 and X=193)."""
    if x <= X_ARC_LEFT or x >= X_ARC_RIGHT:
        return Y_ARC_TANG
    return R_ARC - math.sqrt(R_ARC**2 - (x - X_ARC_CENTER)**2)

def y_outer(x):
    """Y of bowl outer (convex) surface = y_inner(x) + 2.0mm."""
    return y_inner(x) + FLOOR_THICK

# Structural ribs
RIB_WIDTH   = 1.6   # X
RIB_HEIGHT  = 6.0   # Y, from floor outer surface
RIB_CENTERS = [50.5, 98.0, 145.5]

# Cap-end pocket
POCKET_R      = 15.6   # designed radius = 31.2mm / 2 (per parts.md Feature 4)
POCKET_DEPTH  = 50.0   # Z=0..50
POCKET_X      = 98.0
POCKET_Y      = 0.0

# Tube exit hole
TUBE_R = 6.0      # 12mm dia / 2
TUBE_X = 98.0
TUBE_Z = 25.0

# Snap tabs
TAB_Z_CENTERS = [97.0, 145.0, 192.0, 240.0]
TAB_W_Z       = 8.0      # tab width in Z direction
TAB_T_Y       = 2.0      # tab thickness in Y direction
TAB_LEN_X     = 15.0     # cantilever length in -X direction
TAB_Y_LO      = 7.5      # Y bottom of tab body
TAB_Y_HI      = 9.5      # Y top of tab body (= hook base — hook sits directly on tab)
TAB_Y_CTR     = 8.5      # (3.5+13.5)/2
TAB_ROOT_X    = -4.0     # inboard lip outer face
TAB_TIP_X     = -19.0    # root - length
HOOK_Y_HI     = 10.7     # top of hook (TAB_Y_HI + 1.2mm per spec)
HOOK_LEDGE    = 2.0      # hook body depth in X (from tip: X=-19 to X=-17)
TAB_CHAMFER   = 2.0      # root chamfer: 2mm x 45-deg, baked into tab profile

# Snap arm rebate
REBATE_DEPTH_X = 1.2
REBATE_H_Y     = 1.2
REBATE_Y_LO    = 4.9
REBATE_Y_HI    = 6.1

# Fillets
INNER_FILLET_R = 3.0
LIP_FILLET_R   = 1.5

# Fuse overlap — small overlap to ensure OCC fuse creates a single solid
OVL = 0.1

# Number of arc sample points
N_ARC = 64

# OCC solid count helper
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer

def count_occ_solids(shape):
    """Count OCC SOLID shapes inside a CadQuery Shape."""
    exp = TopExp_Explorer(shape.wrapped, TopAbs_SOLID)
    n = 0
    while exp.More():
        n += 1
        exp.Next()
    return n

# =============================================================================
# STEP 1: Build bowl floor arc shell (cross-section extruded along Z)
# =============================================================================
# Profile (in XY plane, no duplicate points):
# Start at (3, 13.5) [inner arc left tangent]
# → inner arc to (98, 0) to (193, 13.5)      [bowl inner surface]
# → step up: (193, 15.5)                       [right end wall of floor, 2mm]
# → outer arc reversed: (193,15.5)→(98,2)→(3,15.5) [bowl outer/convex surface]
# → close() connects (3, 15.5) → (3, 13.5)    [left end wall of floor, 2mm]
print("Building bowl floor arc shell...")

inner_arc_pts = [
    (X_ARC_LEFT + i/N_ARC * (X_ARC_RIGHT - X_ARC_LEFT),
     y_inner(X_ARC_LEFT + i/N_ARC * (X_ARC_RIGHT - X_ARC_LEFT)))
    for i in range(N_ARC + 1)
]
outer_arc_pts_rev = [
    (X_ARC_RIGHT - i/N_ARC * (X_ARC_RIGHT - X_ARC_LEFT),
     y_outer(X_ARC_RIGHT - i/N_ARC * (X_ARC_RIGHT - X_ARC_LEFT)))
    for i in range(N_ARC + 1)
]

floor_profile = (
    [inner_arc_pts[0]]
    + inner_arc_pts[1:]
    + [(X_ARC_RIGHT, y_outer(X_ARC_RIGHT))]  # right end wall top corner
    + outer_arc_pts_rev[1:-1]                 # outer arc interior (skip endpoints)
    + [(X_ARC_LEFT, y_outer(X_ARC_LEFT))]    # left end wall top corner
    # close() → back to (3, 13.5)
)

floor_shell = cq.Workplane("XY").polyline(floor_profile).close().extrude(Z_TOTAL)
s = floor_shell.val()
print(f"  Floor shell: {count_occ_solids(s)} OCC solid(s)")

# =============================================================================
# STEP 2: Fuse shelf and lip blocks
# =============================================================================
# Use slight overlap (OVL=0.1mm) to guarantee OCC fuse creates single body.

print("Fusing shelves and lips...")

# Left shelf: X=[0-OVL, 3+OVL], Y=[13.5-OVL, 15.5+OVL]
left_shelf = cq.Workplane("XY").transformed(
    offset=cq.Vector(X_LIP_L_INNER - OVL, Y_SHELF_LO - OVL, 0)
).box(3 + 2*OVL, FLOOR_THICK + 2*OVL, Z_TOTAL, centered=False).val()

# Right shelf: X=[193-OVL, 196+OVL], Y=[13.5-OVL, 15.5+OVL]
right_shelf = cq.Workplane("XY").transformed(
    offset=cq.Vector(X_ARC_RIGHT - OVL, Y_SHELF_LO - OVL, 0)
).box(3 + 2*OVL, FLOOR_THICK + 2*OVL, Z_TOTAL, centered=False).val()

# Left lip: X=[-4, 0+OVL], Y=[3.5-OVL, 13.5+OVL]  (overlap into shelf zone for fuse)
left_lip = cq.Workplane("XY").transformed(
    offset=cq.Vector(X_LIP_L_OUTER, Y_LIP_TOP - OVL, 0)
).box(LIP_THICK + OVL, LIP_HEIGHT + 2*OVL, Z_TOTAL, centered=False).val()

# Right lip: X=[196-OVL, 200], Y=[3.5-OVL, 13.5+OVL]
right_lip = cq.Workplane("XY").transformed(
    offset=cq.Vector(X_LIP_R_INNER - OVL, Y_LIP_TOP - OVL, 0)
).box(LIP_THICK + OVL, LIP_HEIGHT + 2*OVL, Z_TOTAL, centered=False).val()

s = s.fuse(left_shelf)
s = s.fuse(right_shelf)
s = s.fuse(left_lip)
s = s.fuse(right_lip)
print(f"  After lips+shelves fuse: {count_occ_solids(s)} OCC solid(s)")

# =============================================================================
# STEP 3: Add structural ribs (with small overlap into floor outer surface)
# =============================================================================
print("Adding structural ribs...")

RIB_OVL = 0.1   # overlap into floor outer surface

for i, xc in enumerate(RIB_CENTERS):
    ybase = y_outer(xc) - RIB_OVL   # slightly into the floor for solid fuse
    rib = cq.Workplane("XY").transformed(
        offset=cq.Vector(xc - RIB_WIDTH/2.0, ybase, 0)
    ).box(RIB_WIDTH, RIB_HEIGHT + RIB_OVL, Z_TOTAL, centered=False).val()
    s = s.fuse(rib)
    print(f"  Rib {i+1} at X={xc}: Y_base={y_outer(xc):.3f}, Y_tip={y_outer(xc)+RIB_HEIGHT:.3f}")

print(f"  After ribs: {count_occ_solids(s)} OCC solid(s)")

# =============================================================================
# STEP 4: Add snap tabs (4x) — combined profile (tab + chamfer + hook) per tab
# =============================================================================
# Each tab+hook+root-chamfer is built as a SINGLE 7-vertex XY cross-section profile
# extruded in Z. This guarantees a single connected solid per tab.
#
# The root chamfer is incorporated into the profile itself rather than cut
# afterward, which avoids OCC splitting the body at the tab root face (X=-4).
#
# Profile vertices (CCW in XY) — for a tab centered at Z=zc:
#   A = (-19,  7.5)  ← tab tip bottom-left
#   B = ( -6,  7.5)  ← chamfer start (X = TAB_ROOT_X - TAB_CHAMFER = -4 - 2 = -6)
#   C = (-3.9,  9.5) ← chamfer end at root (TAB_ROOT_X + OVL, TAB_Y_HI)
#   D = (-17,  9.5)  ← hook-inner junction (TAB_TIP_X + HOOK_LEDGE, TAB_Y_HI)
#   E = (-17, 10.7)  ← hook top inner corner
#   F = (-19, 10.7)  ← hook top outer corner
#   G = (-19,  9.5)  ← hook-outer junction = tab tip top
#   close → A
#
# After all tabs are fused into the body, apply the hook lead-in cut (30-deg
# chamfer on the approach face at X=TAB_TIP_X). This cut does not affect the
# body connectivity because it only touches the tip of the hook.
print("Adding snap tabs (combined tab+chamfer+hook profile)...")

# Chamfer integrated into profile: root chamfer slope from B(-6,7.5) to C(-3.9,9.5)
HOOK_H = HOOK_Y_HI - TAB_Y_HI            # 1.2mm
LEADIN_DX = HOOK_H * math.tan(math.radians(30.0))   # ~0.693mm

A_base = (TAB_TIP_X,                   TAB_Y_LO)
B_base = (TAB_ROOT_X - TAB_CHAMFER,    TAB_Y_LO)   # (-6, 7.5)
C_base = (TAB_ROOT_X + OVL,            TAB_Y_HI)   # (-3.9, 9.5) chamfer end at root
D_base = (TAB_TIP_X + HOOK_LEDGE,      TAB_Y_HI)   # (-17, 9.5)
E_base = (TAB_TIP_X + HOOK_LEDGE,      HOOK_Y_HI)  # (-17, 10.7)
F_base = (TAB_TIP_X,                   HOOK_Y_HI)  # (-19, 10.7)
G_base = (TAB_TIP_X,                   TAB_Y_HI)   # (-19, 9.5)

for zc in TAB_Z_CENTERS:
    z_lo = zc - TAB_W_Z / 2.0

    tab_shape = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, 0, z_lo))
        .polyline([A_base, B_base, C_base, D_base, E_base, F_base, G_base])
        .close()
        .extrude(TAB_W_Z)
        .val()
    )
    s = s.fuse(tab_shape)

print(f"  After snap tabs: {count_occ_solids(s)} OCC solid(s)")

# =============================================================================
# STEP 4b: Hook 30-deg lead-in cut (approach face at X=TAB_TIP_X)
# =============================================================================
# The lead-in cut only touches the outer tip of the hook and does not reach
# the tab-to-lip junction, so it cannot disconnect solids.
print("Cutting hook lead-in chamfers...")

for zc in TAB_Z_CENTERS:
    z_lo = zc - TAB_W_Z / 2.0

    leadin = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, 0, z_lo))
        .polyline([
            (TAB_TIP_X,              HOOK_Y_HI),
            (TAB_TIP_X,              TAB_Y_HI),
            (TAB_TIP_X + LEADIN_DX,  TAB_Y_HI),
        ])
        .close()
        .extrude(TAB_W_Z)
        .val()
    )
    s = s.cut(leadin)

print(f"  After lead-in cuts: {count_occ_solids(s)} OCC solid(s)")

# =============================================================================
# STEP 5: Cut cap-end pocket (cylinder, Z=0..50mm)
# =============================================================================
print("Cutting cap-end pocket...")

pocket_cyl = cq.Workplane("XY").center(POCKET_X, POCKET_Y).circle(POCKET_R).extrude(POCKET_DEPTH).val()
s = s.cut(pocket_cyl)
print(f"  After pocket cut: {count_occ_solids(s)} OCC solid(s)")

# =============================================================================
# STEP 5b: Pocket rear wall conical chamfer (30-deg, at Z=50mm)
# =============================================================================
# Resolves the 31mm bridge span at Z=50mm (exceeds 15mm bridge limit).
# Revolve a wedge about the pocket Z axis.
print("Applying pocket rear wall conical chamfer...")

CONE_AXIAL  = 2.0
CONE_RADIAL = CONE_AXIAL * math.tan(math.radians(30.0))   # 1.155mm

chamfer_pts = [
    (POCKET_R,              POCKET_DEPTH - CONE_AXIAL),  # (15.6, 48)
    (POCKET_R,              POCKET_DEPTH),               # (15.6, 50)
    (POCKET_R - CONE_RADIAL, POCKET_DEPTH),              # (14.445, 50)
]
# Revolve on XZ workplane about local Y (= global Z axis after Z-offset to pocket X)
cone_cut = (
    cq.Workplane("XZ")
    .center(POCKET_X, 0)
    .polyline(chamfer_pts)
    .close()
    .revolve(360, (0, 0, 0), (0, 1, 0))
    .val()
)
s = s.cut(cone_cut)

# =============================================================================
# STEP 6: Cut tube exit hole (12mm dia, Y-axis, at Z=25mm, X=98mm)
# =============================================================================
print("Cutting tube exit hole...")

# Cylinder on XZ workplane (normal = -Y); both=True cuts both directions
tube_cyl = (
    cq.Workplane("XZ")
    .center(TUBE_X, TUBE_Z)
    .circle(TUBE_R)
    .extrude(20.0, both=True)   # ±20mm in Y
    .val()
)
s = s.cut(tube_cyl)

# =============================================================================
# STEP 7: Cut snap arm rebates (both lip outer faces, full Z length)
# =============================================================================
print("Cutting snap arm rebates...")

# Left rebate: X=[-4, -2.8], Y=[4.9, 6.1], Z=[0, 287]
left_reb = cq.Workplane("XY").transformed(
    offset=cq.Vector(X_LIP_L_OUTER, REBATE_Y_LO, 0)
).box(REBATE_DEPTH_X, REBATE_H_Y, Z_TOTAL, centered=False).val()
s = s.cut(left_reb)

# Right rebate: X=[198.8, 200], Y=[4.9, 6.1], Z=[0, 287]
right_reb = cq.Workplane("XY").transformed(
    offset=cq.Vector(X_LIP_R_OUTER - REBATE_DEPTH_X, REBATE_Y_LO, 0)
).box(REBATE_DEPTH_X, REBATE_H_Y, Z_TOTAL, centered=False).val()
s = s.cut(right_reb)

print(f"  After rebates: {count_occ_solids(s)} OCC solid(s)")

# =============================================================================
# Wrap back in Workplane for fillet operations
# =============================================================================
body = cq.Workplane("XY").newObject([s])
print(f"\nBefore fillets: {len(body.solids().vals())} body(ies)")

# =============================================================================
# STEP 8: Interior corner fillets (3mm) at arc-to-shelf and shelf-to-lip corners
# =============================================================================
# Four Z-parallel concave edges at:
#   (3, 13.5): arc-to-shelf left
#   (0, 13.5): shelf-to-lip left
#   (193, 13.5): arc-to-shelf right
#   (196, 13.5): shelf-to-lip right
print("Applying interior corner fillets (3mm)...")

fillet_3mm = [
    (3.0,   Y_ARC_TANG, 100.0, "arc-to-shelf left"),
    (0.0,   Y_ARC_TANG, 100.0, "shelf-to-lip left"),
    (193.0, Y_ARC_TANG, 100.0, "arc-to-shelf right"),
    (196.0, Y_ARC_TANG, 100.0, "shelf-to-lip right"),
]

for (fx, fy, fz, name) in fillet_3mm:
    try:
        body = (
            body
            .edges("|Z")
            .edges(cq.selectors.NearestToPointSelector((fx, fy, fz)))
            .fillet(INNER_FILLET_R)
        )
        print(f"  OK: {name}")
    except Exception as e:
        print(f"  WARNING: fillet failed [{name}]: {e}")

# =============================================================================
# STEP 9: Lip top edge fillets (1.5mm)
# =============================================================================
# Four Z-parallel convex edges at (X, Y=3.5): both inner and outer lip top edges
print("Applying lip top edge fillets (1.5mm)...")

fillet_15mm = [
    (0.0,   Y_LIP_TOP, 100.0, "left lip inner top"),
    (-4.0,  Y_LIP_TOP, 100.0, "left lip outer top"),
    (196.0, Y_LIP_TOP, 100.0, "right lip inner top"),
    (200.0, Y_LIP_TOP, 100.0, "right lip outer top"),
]

for (fx, fy, fz, name) in fillet_15mm:
    try:
        body = (
            body
            .edges("|Z")
            .edges(cq.selectors.NearestToPointSelector((fx, fy, fz)))
            .fillet(LIP_FILLET_R)
        )
        print(f"  OK: {name}")
    except Exception as e:
        print(f"  WARNING: fillet failed [{name}]: {e}")

# =============================================================================
# STEP 10: Fold-end lead-in chamfer (3mm x 45-deg, inner face at Z=284..287)
# =============================================================================
# Cut a wedge prism from the inner bowl at the fold end.
# Profile in ZY plane (triangle): (Z=284, Y=3.5), (Z=287, Y=3.5), (Z=287, Y=0.5)
# Extrude in +X direction for full part width (204mm).
print("Applying fold-end lead-in chamfer...")

try:
    fold_cyl = (
        cq.Workplane("ZY")
        .polyline([
            (284.0, 3.5),
            (287.0, 3.5),
            (287.0, 0.5),
        ])
        .close()
        .extrude(204.0)   # ZY normal = +X
        .translate((-4.0, 0, 0))
        .val()
    )
    body_shape = body.val()
    body_shape = body_shape.cut(fold_cyl)
    body = cq.Workplane("XY").newObject([body_shape])
    print("  OK: fold-end chamfer applied")
except Exception as e:
    print(f"  WARNING: fold-end chamfer failed: {e}")

# =============================================================================
# Export STEP
# =============================================================================
output_dir  = Path(__file__).resolve().parent
output_path = output_dir / "cradle-platform-cadquery.step"

print(f"\nExporting STEP to: {output_path}")
cq.exporters.export(body, str(output_path))
print("STEP exported successfully.")

# =============================================================================
# Rubric 3 — Validation
# =============================================================================
print("\n" + "="*60)
print("Rubric 3 — Feature-Specification Reconciliation")
print("="*60)

v = Validator(body)

# ---- Feature 1 & 2: Body, floor wall, lips, shelves ----
v.check_solid("Body: floor wall center Y=1",       98.0,  1.0,  100.0, "solid: floor wall Y=0..2 at X=98")
v.check_solid("Body: left lip material",           -2.0,  8.0,  100.0, "solid: left lip X=-4..0")
v.check_solid("Body: right lip material",         198.0,  8.0,  100.0, "solid: right lip X=196..200")
v.check_solid("Body: left shelf",                   1.5, 14.5,  100.0, "solid: left shelf Y=13.5..15.5")
v.check_solid("Body: right shelf",                194.5, 14.5,  100.0, "solid: right shelf Y=13.5..15.5")
v.check_void("Bowl: void above inner surface",     98.0, -0.5,  100.0, "void: above bowl inner surface Y=0")
v.check_void("Bowl: void above at X=50",           50.0,  2.0,  100.0, "void: inside bowl at X=50 Y=2<y_inner(50)≈3.4")
v.check_void("Lips: void above top edge",          -2.0,  2.0,  100.0, "void: above lip top Y=3.5")

# ---- Feature 3: Structural ribs ----
# Rib 2 (X=98): floor outer Y=2.0, rib tip Y=8.0
v.check_solid("Rib 2: mid-height Y=5",             98.0,  5.0,  100.0, "solid: rib 2 at Y=5")
v.check_solid("Rib 2: near tip Y=7",               98.0,  7.0,  200.0, "solid: rib 2 at Y=7")
v.check_void("Rib 2: beyond tip Y=9",              98.0,  9.0,  100.0, "void: beyond rib 2 tip (Y>8.0)")
# Rib 1 (X=50.5): floor outer Y=5.323, rib tip Y=11.323
v.check_solid("Rib 1: material at Y=8",            50.5,  8.0,  100.0, "solid: rib 1 at Y=8")
v.check_void("Rib 1: beyond tip at Y=12.5",        50.5, 12.5,  100.0, "void: beyond rib 1 tip (Y>11.3)")
v.check_solid("Rib 3: material at Y=8",           145.5,  8.0,  100.0, "solid: rib 3 at Y=8")

# ---- Feature 4: Cap-end pocket ----
v.check_void("Pocket: center at Z=25",             98.0,  0.0,   25.0, "void: inside pocket Z=25")
v.check_void("Pocket: center at Z=10",             98.0,  0.0,   10.0, "void: inside pocket Z=10")
# Outside pocket: at X=114, Y=1.0, Z=25:
#   distance from pocket axis = sqrt((114-98)^2+(1-0)^2) = sqrt(257)=16.03mm > POCKET_R=15.6mm
#   AND y_inner(114)=0.376mm, floor wall Y=0.376..2.376, Y=1.0 inside floor wall → solid
v.check_solid("Pocket: wall outside at X=114,Y=1",114.0,  1.0,   25.0, "solid: outside pocket X=114")
# At Z=55 (past pocket end), Y=1 at center: floor wall → solid
v.check_solid("Pocket: rear wall at Z=55",         98.0,  1.0,   55.0, "solid: floor wall above pocket Z=55")

# ---- Feature 5: Tube exit hole ----
# At (X=98, Y=4, Z=25): inside hole (R=6mm, Y direction; at Y=4 distance from axis=0 in XZ plane → void)
v.check_void("Tube hole: void at Y=4",             98.0,  4.0,   25.0, "void: inside tube hole at Y=4")
# At (X=98, Y=1, Z=65): Z=65>pocket depth 50, dist from tube XZ=(65-25)=40mm>>R=6mm → solid floor wall
v.check_solid("Tube hole: wall at Z=65",           98.0,  1.0,   65.0, "solid: floor wall at Z=65 (outside hole+pocket)")
# Floor wall at X=50, Z=25, Y=4.5: far from hole center (dist≈48mm in X → outside R=6mm) → solid
v.check_solid("Tube hole: wall at X=50,Z=25",      50.0,  4.5,   25.0, "solid: floor wall at X=50")

# ---- Feature 6: Snap tabs ----
v.check_solid("Tab 1: body at Z=97",              -11.5,  8.5,   97.0, "solid: tab 1 body mid")
v.check_solid("Tab 2: body at Z=145",             -11.5,  8.5,  145.0, "solid: tab 2 body mid")
v.check_solid("Tab 3: body at Z=192",             -11.5,  8.5,  192.0, "solid: tab 3 body mid")
v.check_solid("Tab 4: body at Z=240",             -11.5,  8.5,  240.0, "solid: tab 4 body mid")
# Hook: Y=10.0 (inside hook zone Y=9.5..10.7) at tab tip X=-18.5
v.check_solid("Tab 1: hook at Y=10",              -18.5, 10.0,   97.0, "solid: tab 1 hook zone Y=10")
# Gap between tabs: Z=120 (between Z=101 and Z=141) — no tab here
v.check_void("Between tabs 1-2: Z=120",           -11.5,  8.5,  120.0, "void: between tab 1 and tab 2")

# ---- Feature 9: Snap arm rebates ----
# Left rebate: X=-3.4 (midpoint of X=-4..−2.8), Y=5.5, Z=143.5
v.check_void("Left rebate: groove void",           -3.4,  5.5,  143.5, "void: left rebate groove")
v.check_void("Right rebate: groove void",         199.4,  5.5,  143.5, "void: right rebate groove")
# Above rebate: Y=3.8 (between Y=3.5 lip top and Y=4.9 rebate bottom) → solid
v.check_solid("Left lip: solid above rebate",      -3.4,  3.8,  143.5, "solid: left lip above rebate Y=3.8")
# Below rebate: Y=7.0 (below rebate top at Y=6.1) → solid
v.check_solid("Left lip: solid below rebate",      -3.4,  7.0,  143.5, "solid: left lip below rebate Y=7.0")

# ---- Solid integrity ----
v.check_valid()
v.check_single_body()

# Volume check: thin-walled trough, expect 4%–30% of envelope
ENVELOPE_VOL = 204.0 * 21.5 * 287.0
v.check_volume(expected_envelope=ENVELOPE_VOL, fill_range=(0.04, 0.35))

# Bounding box
bb = body.val().BoundingBox()
print(f"\n  BoundingBox: X=[{bb.xmin:.2f}, {bb.xmax:.2f}]  Y=[{bb.ymin:.2f}, {bb.ymax:.2f}]  Z=[{bb.zmin:.2f}, {bb.zmax:.2f}]")
# X: base -4..200; tabs extend to X=-19
v.check_bbox("X", bb.xmin, bb.xmax, -19.0, 200.0, tol=2.0)
# Y: 0..~15.5 (floor outer at arc endpoints)
v.check_bbox("Y", bb.ymin, bb.ymax,   0.0,  15.5,  tol=2.0)
# Z: 0..287
v.check_bbox("Z", bb.zmin, bb.zmax,   0.0, 287.0,  tol=1.0)

passed = v.summary()
if not passed:
    print(f"\n{v.fail_count} check(s) FAILED — see above.")
    sys.exit(1)
else:
    print(f"\nAll checks passed. STEP file: {output_path}")
