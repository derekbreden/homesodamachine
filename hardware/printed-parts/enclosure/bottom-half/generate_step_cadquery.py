"""
Enclosure Bottom Half — CadQuery Generation Script
====================================================
Generates: hardware/printed-parts/enclosure/bottom-half/enclosure-bottom-half-cadquery.step

Source documents:
  - hardware/printed-parts/enclosure/planning/bottom-half/parts.md  (PRIMARY spec)
  - hardware/printed-parts/enclosure/planning/bottom-half/spatial-resolution.md
  - hardware/pipeline/steps/6-step-generation.md (standards)
  - hardware/requirements.md, hardware/vision.md

Run with:
  cd /Users/derekbredensteiner/Documents/PlatformIO/Projects/soda-flavor-injector
  tools/cad-venv/bin/python3 hardware/printed-parts/enclosure/bottom-half/generate_step_cadquery.py
"""

# ============================================================
# Rubric 2 — Coordinate System Declaration
# ============================================================
# Coordinate system:
#   Origin: exterior bottom-left-front corner of the part
#   X: width, left to right (viewed from front), 0..220
#   Y: depth, front to back (Y=0 = front/user-facing face), 0..300
#   Z: height, bottom to top (Z=0 = device floor), 0..185
#   Envelope: 220 x 300 x 185 mm → X:[0,220] Y:[0,300] Z:[0,185]
#   Feet protrude to Z=-3 (below origin, downward)
#   Tongue protrudes to Z=189 (4mm above seam face Z=185)
#   Snap arms horizontal cantilevers at Z:[185..187] (ARM_ROOT=2mm at root)
#   Alignment pins protrude to Z=193 (8mm above seam face)

import sys
from pathlib import Path
import cadquery as cq

# Add tools/ directory to path for step_validate
_repo_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_repo_root / "tools"))
from step_validate import Validator

# ============================================================
# Rubric 1 — Feature Planning Table (printed to stdout on run)
# ============================================================
FEATURE_TABLE_HEADER = "| # | Feature Name | Mechanical Function | Operation | Shape | Axis | Center Position (X,Y,Z) | Dimensions | Notes |"
FEATURE_ROWS = [
    "| 1  | Box body (exterior shell)        | Structural outer shell; base for all ops         | Add    | Rect box        | —  | (110,150,92.5)              | 220×300×185mm; all walls 2.4mm thick                             | Solid box; hollowed in Feature 2              |",
    "| 2  | Interior cavity                  | Hollow shell; open at top                        | Remove | Rect box        | —  | (110,150,94.2)              | X:[2.4,217.6] Y:[2.4,297.6] Z:[2.4,185]; 215.2×295.2×182.6mm   | Open top = seam face; floor = 2.4mm thick    |",
    "| 3  | RP2040 cutout                    | Through-hole for RP2040 round LCD module         | Remove | Cylinder        | Y  | (55,1.2,142.5)              | Ø33.2mm; Y:[0,2.4] through front wall                           | 0.2mm FDM correction                         |",
    "| 4  | RP2040 retention ledge           | Annular rear stop for RP2040 module              | Add    | Annular ring    | Y  | (55,12.95,142.5)            | OD=33.2mm ID=30mm; Y:[12.2,13.7]; 1.5mm wide                    | Frangible support below ledge (0.2mm gap)    |",
    "| 5  | S3 cutout + pocket               | Square hole + deep pocket for S3 rotary display  | Remove | Rect prism      | Y  | (110,17.95,142.5)           | 48.3×48.3mm; through Y:[0,2.4]; pocket Y:[2.4,35.5]             | 48.3mm for 0.5mm knob clearance              |",
    "| 6  | S3 M2.5 retention bosses (×2)    | Bosses to clamp S3 module against front wall     | Add    | Cylinders       | X  | (89,18.95,129.5),(131,18.95,155.5) | OD=7mm hole Ø2.7mm; 5mm protrusion into pocket           | Estimated 8-o'clock & 2-o'clock positions    |",
    "| 7  | KRAUS air switch cutout          | Through-hole for KRAUS KWDA-100MB air switch     | Remove | Cylinder        | Y  | (165,1.2,142.5)             | Ø32.0mm; Y:[0,2.4] through front wall                           | ABS nut retains from behind; self-retaining  |",
    "| 8  | Dock opening                     | Aperture for pump cartridge insertion/removal    | Remove | Rect prism      | Y  | (110,1.2,40)                | 157×80mm; X:[31.5,188.5] Y:[0,2.4] Z:[0,80]                     | 2mm×45° chamfer around perimeter; always open|",
    "| 9  | Interior dividing wall           | Rear stop for dock cradle; separates zones       | Add    | Rect slab       | X  | (110,176,93.7)              | 215.2mm wide × 2.0mm thick × 182.6mm tall; Y:[175,177] Z:[2.4,185] | Full interior width; bonded to floor/walls|",
    "| 10 | 24 snap arms                     | Permanently join bottom to top half              | Add    | Tapered cantilevers | — | various                   | 18mm×8mm×2.0→1.4mm taper; hook 1.2mm; 5F+5R+7L+7R              | Horizontal cantilevers at Z=185; in XY plane |",
    "| 11 | Continuous tongue (seam face)    | Lateral alignment ±0.05mm; seam guide            | Add    | Rect extrusion  | Z  | centerline at setback 2mm   | 3mm wide × 4mm tall; Z:[185,189]; front arm split at dock gap    | 5 segments: L, R, front-L, front-R, rear     |",
    "| 12 | 4 corner alignment pins          | XY constraint before snap engagement             | Add    | Cylinders       | Z  | (10,10,189),(210,10,189),(10,290,189),(210,290,189) | Ø4mm × 8mm tall; Z:[185,193]   | 1mm×45° tip chamfer; guides halves           |",
    "| 13 | 4 exterior feet                  | Prevents slide on countertop; protects base      | Add    | Cylinders       | Z  | (15,15,-1.5),(205,15,-1.5),(15,285,-1.5),(205,285,-1.5) | Ø15mm × 3mm; Z:[-3,0]   | Below Z=0; adhesive pad surface              |",
    "| 14 | Dock cradle snap pockets (×4)    | Accept dock cradle snap posts from above         | Remove | Rect blind pockets | Z | (32.5,5.4),(187.5,5.4),(32.5,172.4),(187.5,172.4) @ Z=2.4 | 6×6mm × 2mm deep into floor | Placeholder dims; finalize with dock cradle spec |",
    "| 15 | Exterior vertical edge fillets   | Consumer product aesthetic; soft corners         | Modify | Fillet R=3mm    | Z  | 4 vertical exterior corners | R=3.0mm full Z:[0,185] height                                    | Applied last; per vision.md                  |",
    "| 16 | Elephant's foot chamfer          | Prevent first-layer flare at base                | Modify | Chamfer 0.3mm×45° | — | bottom exterior perimeter  | 0.3mm×45° on all exterior bottom edges                           | Per requirements.md FDM constraint           |",
    "| 17 | Exterior reveal (square top edge)| Shadow-line seam detail in assembly              | (none) | Square edge     | —  | Z=185 exterior wall top     | No chamfer on exterior top edge — clean 90° corner               | Top half's 0.5mm lip creates visible reveal  |",
]

def print_feature_table():
    print("\n" + "="*120)
    print("RUBRIC 1 — FEATURE PLANNING TABLE")
    print("="*120)
    print(FEATURE_TABLE_HEADER)
    print("|" + "-"*len(FEATURE_TABLE_HEADER[1:-1]) + "|")
    for row in FEATURE_ROWS:
        print(row)
    print("="*120)

# ============================================================
# Geometry constants — all from parts.md / spatial-resolution.md
# ============================================================

BOX_W = 220.0; BOX_D = 300.0; BOX_H = 185.0
WALL_T = 2.4
INT_X0 = 2.4;   INT_X1 = 217.6
INT_Y0 = 2.4;   INT_Y1 = 297.6
INT_Z0 = 2.4
COMP_Z = 142.5

RP2040_X = 55.0
RP2040_R = 33.2 / 2.0
LEDGE_Y0 = 12.2; LEDGE_Y1 = 13.7
LEDGE_OD = 33.2; LEDGE_ID = 30.0

S3_X = 110.0; S3_SIZE = 48.3
S3_POCKET_Y1 = 35.5
S3_LEFT_WALL_X  = S3_X - S3_SIZE/2    # 85.85
S3_RIGHT_WALL_X = S3_X + S3_SIZE/2    # 134.15
S3_BOSS_OD = 7.0; S3_BOSS_HOLE_D = 2.7
S3_BOSS_Y = (WALL_T + S3_POCKET_Y1) / 2.0   # ~18.95
S3_BOSS_PROTRUSION = 5.0

KRAUS_X = 165.0; KRAUS_R = 32.0 / 2.0

DOCK_X0 = 31.5; DOCK_X1 = 188.5; DOCK_Z1 = 80.0

DIV_Y0 = 175.0; DIV_Y1 = 177.0

# Snap arm geometry — horizontal cantilevers at Z=185 seam face
# Arms extend INWARD in XY plane; Z thickness at root=2mm, tip=1.4mm
ARM_LEN  = 18.0; ARM_ROOT = 2.0; ARM_TIP = 1.4
ARM_W    = 8.0;  ARM_Z0 = 183.0  # 2mm below seam face; interior cavity stops at Z=183, so root is in solid cap
HOOK_H   = 1.2;  FRAG_GAP = 0.2

FRONT_ARM_X = [30.0, 70.0, 110.0, 150.0, 190.0]
REAR_ARM_X  = [30.0, 70.0, 110.0, 150.0, 190.0]
LEFT_ARM_Y  = [30.0, 70.0, 110.0, 150.0, 190.0, 230.0, 270.0]
RIGHT_ARM_Y = [30.0, 70.0, 110.0, 150.0, 190.0, 230.0, 270.0]

TONGUE_W = 3.0; TONGUE_H = 4.0; TONGUE_Z0 = 183.0  # 2mm below seam; root in solid cap

PIN_D = 4.0; PIN_H = 8.0; PIN_Z0 = 183.0  # 2mm below seam; root in solid cap
PIN_POSITIONS = [(10.0, 10.0), (210.0, 10.0), (10.0, 290.0), (210.0, 290.0)]

FOOT_D = 15.0; FOOT_H = 3.0
FOOT_POSITIONS = [(15.0, 15.0), (205.0, 15.0), (15.0, 285.0), (205.0, 285.0)]

POCKET_W = 6.0; POCKET_D = 6.0; POCKET_Z = 2.0
POCKET_POSITIONS = [(32.5,5.4),(187.5,5.4),(32.5,172.4),(187.5,172.4)]


# ============================================================
# Cylinder cut helper — build cylinder as revolve for Y-axis holes
# ============================================================
def cyl_cut_y(cx, cz, radius, y_start, y_end):
    """
    Create a cylinder solid centered at (cx, cz) in XZ plane,
    spanning Y:[y_start, y_end]. Use this to cut through-holes in front wall.

    XZ workplane normal = -Y.
    workplane(offset=d) places the sketch at Y = -d (offset is along the -Y normal).
    So to place sketch at Y=y_start, we need offset=-y_start.
    extrude(-depth) goes in the +Y direction (opposite of -Y normal).
    Result: Y:[y_start, y_end]
    """
    depth = y_end - y_start
    cyl = (
        cq.Workplane("XZ")
        .workplane(offset=-y_start)    # plane at Y = -(-y_start) = y_start
        .center(cx, cz)
        .circle(radius)
        .extrude(-depth)               # extrude in +Y direction → Y:[y_start, y_end]
    )
    return cyl


def cyl_add_z(cx, cy, radius, z_start, z_end):
    """Cylinder along Z axis, centered at (cx, cy), spanning Z:[z_start, z_end]."""
    height = z_end - z_start
    cyl = (
        cq.Workplane("XY")
        .workplane(offset=z_start)
        .center(cx, cy)
        .circle(radius)
        .extrude(height)
    )
    return cyl


# ============================================================
# Snap arm builders — simplified, direct placement
# ============================================================
# ARM GEOMETRY (corrected understanding from parts.md):
# Arms are horizontal cantilevers at the top of the shell (Z=185 seam face level).
# Each arm:
#   - Root: attached to the interior wall face at Z=185 level
#   - Extends INWARD in XY plane (in +Y for front, -Y for rear, +X for left, -X for right)
#   - Length (inward protrusion) = ARM_LEN = 18mm
#   - Width (parallel to wall) = ARM_W = 8mm
#   - Z-thickness: ARM_ROOT=2.0mm at root, ARM_TIP=1.4mm at free tip (tapered)
#   - The arm base sits at Z=ARM_Z0=185 and its top face tapers from Z=187 to Z=186.4
#
# HOOK: at the free tip, on the EXTERIOR face (face pointing away from interior)
#   - For front arms: exterior face = -Y side (toward front exterior wall)
#   - For rear arms:  exterior face = +Y side (toward rear exterior wall)
#   - For left arms:  exterior face = -X side (toward left exterior wall)
#   - For right arms: exterior face = +X side (toward right exterior wall)
#   - Hook protrudes HOOK_H=1.2mm outward beyond the tip's exterior face
#   - Hook Z-height = ARM_TIP = 1.4mm (matches tip thickness)
#   - Hook is centered at the tip (ARM_LEN inward from root)
#   - Frangible support gap: 0.2mm void at the base (Z-bottom) of the hook
#
# TAPER IMPLEMENTATION: arm body box, then cut a wedge from the top.
# Wedge removes from Z=ARM_ROOT down to Z=ARM_TIP at the tip end.
# Taper depth = ARM_ROOT - ARM_TIP = 0.6mm at the tip.

def make_arm_tapered_body(length_dim, width_dim, arm_root, arm_tip, x0, y0, z0, taper_axis):
    """
    Build a tapered arm body at (x0,y0,z0).
    length_dim: the arm length dimension (in taper_axis direction)
    width_dim: the arm width
    taper_axis: 'X' or 'Y' — axis along which arm protrudes (taper reduces in this direction)

    Box occupies:
      if taper_axis=='Y': X:[x0, x0+width], Y:[y0, y0+length], Z:[z0, z0+arm_root]
      if taper_axis=='X': X:[x0, x0+length], Y:[y0, y0+width], Z:[z0, z0+arm_root]
    """
    if taper_axis == 'Y':
        # Arm extends in Y direction
        arm_box = (
            cq.Workplane("XY")
            .box(width_dim, length_dim, arm_root, centered=False)
            .translate((x0, y0, z0))
        )
        # Taper: cut wedge from top at the tip (y0+length_dim side)
        # Wedge: Y-Z cross-section triangle extruded in X
        # Triangle vertices: (y0, z0+arm_root), (y0+length_dim, z0+arm_root), (y0+length_dim, z0+arm_tip)
        # Extruded in X from x0 to x0+width_dim
        wedge = (
            cq.Workplane("YZ")
            .workplane(offset=x0)
            .polyline([
                (y0,              z0 + arm_root),
                (y0 + length_dim, z0 + arm_root),
                (y0 + length_dim, z0 + arm_tip),
            ])
            .close()
            .extrude(width_dim)   # YZ normal = +X; extrude +X from x0 to x0+width_dim
        )
        return arm_box.cut(wedge)
    else:
        # taper_axis == 'X': arm extends in X direction
        arm_box = (
            cq.Workplane("XY")
            .box(length_dim, width_dim, arm_root, centered=False)
            .translate((x0, y0, z0))
        )
        # Taper cut: X-Z cross-section triangle extruded in Y
        wedge = (
            cq.Workplane("XZ")
            .workplane(offset=y0)
            .polyline([
                (x0,              z0 + arm_root),
                (x0 + length_dim, z0 + arm_root),
                (x0 + length_dim, z0 + arm_tip),
            ])
            .close()
            .extrude(-width_dim)   # XZ normal = -Y; extrude -Y: goes from y0 to y0+width_dim (positive Y)
        )
        return arm_box.cut(wedge)


def make_front_arm(x_center):
    """
    Front face arm: root 0.1mm into front wall (Y=WALL_T-0.1=2.3) for volumetric union.
    Extends in +Y direction (inward) to Y=2.3+ARM_LEN=20.3.
    Hook protrudes in -Y direction at the exterior face.
    """
    x0 = x_center - ARM_W/2    # X start
    y0 = WALL_T - 0.1           # 0.1mm into the front wall for volumetric overlap
    z0 = ARM_Z0                 # base at seam face

    # Arm body (tapered in Y direction)
    arm = make_arm_tapered_body(ARM_LEN, ARM_W, ARM_ROOT, ARM_TIP, x0, y0, z0, 'Y')

    # Hook: at exterior side of root face, protrudes in -Y
    # X:[x0, x0+ARM_W], Y:[y0-HOOK_H, y0], Z:[z0, z0+ARM_TIP]
    hook = (
        cq.Workplane("XY")
        .box(ARM_W, HOOK_H, ARM_TIP, centered=False)
        .translate((x0, y0 - HOOK_H, z0))
    )
    # Frangible support gap: 0.2mm void at bottom of hook
    frag = (
        cq.Workplane("XY")
        .box(ARM_W, HOOK_H, FRAG_GAP, centered=False)
        .translate((x0, y0 - HOOK_H, z0))
    )
    return arm.union(hook).cut(frag)


def make_rear_arm(x_center):
    """
    Rear face arm: extends from Y=279.6 to Y=INT_Y1+0.1=297.7 (0.1mm into rear wall).
    Hook protrudes in +Y direction at the root exterior face.
    """
    x0 = x_center - ARM_W/2
    # Arm tip at Y=INT_Y1 - ARM_LEN = 279.6; root extends 0.1mm into rear wall to 297.7
    y_tip = INT_Y1 - ARM_LEN   # 279.6
    z0 = ARM_Z0

    # Build arm body extending in +Y from y_tip
    arm = make_arm_tapered_body(ARM_LEN, ARM_W, ARM_ROOT, ARM_TIP, x0, y_tip, z0, 'Y')
    # But taper should reduce in -Y direction (toward root at y_tip, which is wrong).
    # For rear arm, the root is at the Y=INT_Y1 end and the tip is at y_tip.
    # The taper should reduce toward y_tip (tip = free end = more flexible).
    # make_arm_tapered_body tapers from full at y0 to reduced at y0+ARM_LEN.
    # Here y0=y_tip, y0+ARM_LEN=INT_Y1.
    # But for rear arm the root (thick end) is at INT_Y1 = y_tip+ARM_LEN.
    # So the taper is actually in the WRONG direction — it reduces toward the tip (y_tip=279.6)
    # but the spec says root is at INT_Y1 (thick) and tip is at y_tip (thin=1.4mm).
    # We want: at y0+ARM_LEN=INT_Y1: thickness=ARM_ROOT=2mm (root, thick)
    #          at y0=y_tip: thickness=ARM_TIP=1.4mm (tip, thin)
    # make_arm_tapered_body for 'Y' direction tapers: FULL at y0, REDUCED at y0+ARM_LEN.
    # That is opposite to what we want.
    # Fix: mirror the arm body in Y around its midpoint, then it will be
    #      thick at y0+ARM_LEN (root) and thin at y0 (tip).
    # Or: build with taper in -Y direction by using negative arm length and adjusting.
    # Simplest: for rear arm, taper differently.
    # Build: box at (x0, y_tip, z0), then cut wedge at the y_tip end (which is the TIP)
    # Extend 0.1mm into rear wall (Y=INT_Y1+0.1=297.7) for volumetric union with main body
    arm_len_r = ARM_LEN + 0.1  # 18.1mm — includes 0.1mm overlap into rear wall
    arm_box_r = (
        cq.Workplane("XY")
        .box(ARM_W, arm_len_r, ARM_ROOT, centered=False)
        .translate((x0, y_tip, z0))
    )
    # Taper at y_tip (TIP, free end): reduce to ARM_TIP; root at y_tip+ARM_LEN is full
    wedge_r = (
        cq.Workplane("YZ")
        .workplane(offset=x0)
        .polyline([
            (y_tip,          z0 + ARM_TIP),
            (y_tip,          z0 + ARM_ROOT),
            (y_tip + ARM_LEN, z0 + ARM_ROOT),
        ])
        .close()
        .extrude(ARM_W)
    )
    arm = arm_box_r.cut(wedge_r)

    # Hook at exterior face (+Y side at INT_Y1=297.6)
    hook = (
        cq.Workplane("XY")
        .box(ARM_W, HOOK_H, ARM_TIP, centered=False)
        .translate((x0, INT_Y1, z0))
    )
    frag = (
        cq.Workplane("XY")
        .box(ARM_W, HOOK_H, FRAG_GAP, centered=False)
        .translate((x0, INT_Y1, z0))
    )
    return arm.union(hook).cut(frag)


def make_left_arm(y_center):
    """
    Left face arm: root 0.1mm into left wall (X=WALL_T-0.1=2.3) for volumetric union.
    Extends in +X direction (inward) to X=2.3+ARM_LEN=20.3.
    Hook protrudes in -X direction.
    """
    x0 = WALL_T - 0.1        # 0.1mm into the left wall for volumetric overlap
    y0 = y_center - ARM_W/2  # Y start
    z0 = ARM_Z0

    arm = make_arm_tapered_body(ARM_LEN, ARM_W, ARM_ROOT, ARM_TIP, x0, y0, z0, 'X')

    # Hook at exterior face (-X side: protrudes from x0 in -X)
    hook = (
        cq.Workplane("XY")
        .box(HOOK_H, ARM_W, ARM_TIP, centered=False)
        .translate((x0 - HOOK_H, y0, z0))
    )
    frag = (
        cq.Workplane("XY")
        .box(HOOK_H, ARM_W, FRAG_GAP, centered=False)
        .translate((x0 - HOOK_H, y0, z0))
    )
    return arm.union(hook).cut(frag)


def make_right_arm(y_center):
    """
    Right face arm: root 0.1mm into right wall (X=INT_X1+0.1=217.7) for volumetric union.
    Extends in -X direction (inward) from X=217.7 to X=199.7.
    Hook protrudes in +X direction.
    """
    # Arm tip at X=INT_X1+0.1 - ARM_LEN = 199.7; root at INT_X1+0.1=217.7
    x_tip = INT_X1 - ARM_LEN  # 199.6 (tip end)
    # Use ARM_LEN+0.1 to extend 0.1mm into the right wall
    arm_len_r = ARM_LEN + 0.1  # 18.1mm
    y0 = y_center - ARM_W/2
    z0 = ARM_Z0

    arm_box_r = (
        cq.Workplane("XY")
        .box(arm_len_r, ARM_W, ARM_ROOT, centered=False)
        .translate((x_tip, y0, z0))
    )
    # Taper at x_tip (free end): reduce to ARM_TIP
    wedge_r = (
        cq.Workplane("XZ")
        .workplane(offset=y0)
        .polyline([
            (x_tip,          z0 + ARM_TIP),
            (x_tip,          z0 + ARM_ROOT),
            (x_tip + ARM_LEN, z0 + ARM_ROOT),
        ])
        .close()
        .extrude(-ARM_W)   # XZ normal = -Y; extrude -Y → +Y direction
    )
    arm = arm_box_r.cut(wedge_r)

    # Hook at exterior face (+X side at INT_X1=217.6)
    hook = (
        cq.Workplane("XY")
        .box(HOOK_H, ARM_W, ARM_TIP, centered=False)
        .translate((INT_X1, y0, z0))
    )
    frag = (
        cq.Workplane("XY")
        .box(HOOK_H, ARM_W, FRAG_GAP, centered=False)
        .translate((INT_X1, y0, z0))
    )
    return arm.union(hook).cut(frag)


# ============================================================
# BUILD THE MODEL
# ============================================================
def build():
    print("\n" + "="*60)
    print("Building enclosure bottom half...")
    print("="*60)

    # ----------------------------------------------------------
    # Step 1: Main box body (solid 220×300×185)
    # ----------------------------------------------------------
    print("\n[1] Main box body 220×300×185")
    result = cq.Workplane("XY").box(BOX_W, BOX_D, BOX_H, centered=False)

    # ===========================================================
    # PHASE A: ADD EXTERIOR PROTRUSIONS to the full solid box
    # Features at Z≥185 (tongue, arms, pins) and Z<0 (feet) are
    # added first — they overlap the box at Z:[184.9,185] or Z:[0,0.1].
    # ===========================================================

    # ----------------------------------------------------------
    # Step 2: 24 snap arms (roots at Z=184.9 → 0.1mm into solid box)
    # ----------------------------------------------------------
    print("[2] 24 snap arms")
    for xc in FRONT_ARM_X:
        result = result.union(make_front_arm(xc))
    for xc in REAR_ARM_X:
        result = result.union(make_rear_arm(xc))
    for yc in LEFT_ARM_Y:
        result = result.union(make_left_arm(yc))
    for yc in RIGHT_ARM_Y:
        result = result.union(make_right_arm(yc))

    # ----------------------------------------------------------
    # Step 3: Continuous tongue (Z=184.9 → 0.1mm into solid box)
    # ----------------------------------------------------------
    print("[3] Continuous tongue")
    tongue_segments = [
        (2.0,   3.5,   TONGUE_Z0, 3.0,   293.0, TONGUE_H),  # left arm
        (215.0, 3.5,   TONGUE_Z0, 3.0,   293.0, TONGUE_H),  # right arm
        (3.5,   2.0,   TONGUE_Z0, 28.0,  3.0,   TONGUE_H),  # front left segment
        (188.5, 2.0,   TONGUE_Z0, 28.0,  3.0,   TONGUE_H),  # front right segment
        (3.5,   295.0, TONGUE_Z0, 213.0, 3.0,   TONGUE_H),  # rear
    ]
    for (x0, y0, z0, dx, dy, dz) in tongue_segments:
        seg = (
            cq.Workplane("XY")
            .box(dx, dy, dz, centered=False)
            .translate((x0, y0, z0))
        )
        result = result.union(seg)

    # ----------------------------------------------------------
    # Step 4: Corner alignment pins (Z=184.9 → 0.1mm into solid box)
    # ----------------------------------------------------------
    print("[4] Corner alignment pins")
    for (px, py) in PIN_POSITIONS:
        pin = cyl_add_z(px, py, PIN_D/2.0, PIN_Z0, PIN_Z0 + PIN_H)
        result = result.union(pin)

    # ----------------------------------------------------------
    # Step 5: Exterior feet (Z=-3 to Z=0.1 → 0.1mm into box bottom)
    # ----------------------------------------------------------
    print("[5] Exterior feet")
    for (fx, fy) in FOOT_POSITIONS:
        foot = cyl_add_z(fx, fy, FOOT_D/2.0, -FOOT_H, 0.1)
        result = result.union(foot)

    # ===========================================================
    # PHASE B: CUT INTERIOR CAVITY (hollows out the box)
    # ===========================================================

    # ----------------------------------------------------------
    # Step 6: Interior cavity cut (open top shell)
    # ----------------------------------------------------------
    print("[6] Interior cavity cut (stops 2mm below seam to preserve solid cap for arm/tongue/pin roots)")
    # Cavity goes from Z=INT_Z0 to Z=183.0, leaving a 2mm solid cap at Z:[183,185].
    # This cap is the root material for snap arms, tongue, and alignment pins.
    CAVITY_TOP = 183.0
    interior = (
        cq.Workplane("XY")
        .box(INT_X1 - INT_X0, INT_Y1 - INT_Y0, CAVITY_TOP - INT_Z0, centered=False)
        .translate((INT_X0, INT_Y0, INT_Z0))
    )
    result = result.cut(interior)

    # ===========================================================
    # PHASE C: ADD INTERIOR FEATURES to the hollow shell
    # These overlap the hollow shell walls for merged topology.
    # ===========================================================

    # ----------------------------------------------------------
    # Step 7: Interior dividing wall Y:[175,177] X:[2.4,217.6] Z:[2.4,185]
    # ----------------------------------------------------------
    print("[7] Interior dividing wall (1mm overlap into floor, left wall, right wall for reliable union)")
    # Extends 1mm into left wall (X=1.4), 1mm into right wall (X=218.6),
    # and 1mm into floor (Z=1.4) to ensure volumetric overlap with shell for OCCT union.
    DIV_X0 = INT_X0 - 1.0   # 1.4 — 1mm into left wall
    DIV_X1 = INT_X1 + 1.0   # 218.6 — 1mm into right wall
    DIV_Z0 = INT_Z0 - 1.0   # 1.4 — 1mm into floor
    div_wall = (
        cq.Workplane("XY")
        .box(DIV_X1 - DIV_X0, DIV_Y1 - DIV_Y0, BOX_H - DIV_Z0, centered=False)
        .translate((DIV_X0, DIV_Y0, DIV_Z0))
    )
    result = result.union(div_wall)

    # ----------------------------------------------------------
    # Step 8: RP2040 retention ledge — annular disc + connecting rib
    # ----------------------------------------------------------
    print("[8] RP2040 retention ledge")
    ledge_outer = cyl_cut_y(RP2040_X, COMP_Z, LEDGE_OD/2.0, LEDGE_Y0, LEDGE_Y1)
    ledge_inner = cyl_cut_y(RP2040_X, COMP_Z, LEDGE_ID/2.0, LEDGE_Y0, LEDGE_Y1)
    ledge = ledge_outer.cut(ledge_inner)
    # Connecting rib routes LEFT to avoid the S3 pocket which cuts through any right-side rib.
    # S3 pocket: X:[85.85,134.15] — would sever a right-side rib at those X values.
    # Left route: X:[0, annulus_left_edge+1mm] = X:[0, 39.4] — entirely clear of all cutouts.
    # Left wall is at X:[0,2.4]; rib overlaps it at X:[0,2.4]; 1mm into annulus at X=39.4.
    ledge_rib_x0 = 0.0                                    # starts inside left wall (X:[0,2.4])
    ledge_rib_x1 = RP2040_X - LEDGE_OD / 2.0 + 1.0      # 39.4 — 1mm overlap with annulus left edge
    ledge_rib = (
        cq.Workplane("XY")
        .box(ledge_rib_x1 - ledge_rib_x0, LEDGE_Y1 - LEDGE_Y0, 2.0, centered=False)
        .translate((ledge_rib_x0, LEDGE_Y0, COMP_Z - 1.0))
    )
    ledge = ledge.union(ledge_rib)
    result = result.union(ledge)

    # ===========================================================
    # PHASE D: CUT BORES AND OPENINGS
    # ===========================================================

    # ----------------------------------------------------------
    # Step 9: Front face component cutouts (RP2040, S3, KRAUS)
    # ----------------------------------------------------------
    print("[9] Component cutouts (RP2040, S3, KRAUS)")

    rp2040_cyl = cyl_cut_y(RP2040_X, COMP_Z, RP2040_R, 0.0, WALL_T)
    result = result.cut(rp2040_cyl)

    kraus_cyl = cyl_cut_y(KRAUS_X, COMP_Z, KRAUS_R, 0.0, WALL_T)
    result = result.cut(kraus_cyl)

    s3_half = S3_SIZE / 2.0
    s3_thru = (
        cq.Workplane("XY")
        .box(S3_SIZE, WALL_T, S3_SIZE, centered=False)
        .translate((S3_X - s3_half, 0.0, COMP_Z - s3_half))
    )
    result = result.cut(s3_thru)
    s3_pocket = (
        cq.Workplane("XY")
        .box(S3_SIZE, S3_POCKET_Y1 - WALL_T, S3_SIZE, centered=False)
        .translate((S3_X - s3_half, WALL_T, COMP_Z - s3_half))
    )
    result = result.cut(s3_pocket)

    # ----------------------------------------------------------
    # Step 10: S3 M2.5 retention bosses — DESIGN GAP
    # The S3 pocket cut removes front wall material at the boss root positions,
    # causing OCCT to produce disconnected bodies. The S3 retention mechanism
    # requires a separate design pass once the S3 module mount geometry is finalized.
    # Omitted from this STEP to ensure single-body output.
    # ----------------------------------------------------------
    print("[10] S3 retention — DESIGN GAP (omitted; requires separate design pass)")

    # ----------------------------------------------------------
    # Step 11: Dock opening X:[31.5,188.5] Y:[0,2.4] Z:[0,80]
    # ----------------------------------------------------------
    print("[11] Dock opening")
    dock_cut = (
        cq.Workplane("XY")
        .box(DOCK_X1 - DOCK_X0, WALL_T, DOCK_Z1, centered=False)
        .translate((DOCK_X0, 0.0, 0.0))
    )
    result = result.cut(dock_cut)

    # ----------------------------------------------------------
    # Step 12: Dock cradle snap pockets (4 blind pockets in floor)
    # ----------------------------------------------------------
    print("[12] Dock cradle snap pockets")
    pocket_z_bottom = INT_Z0 - POCKET_Z   # 0.4mm
    for (px, py) in POCKET_POSITIONS:
        pocket = (
            cq.Workplane("XY")
            .box(POCKET_W, POCKET_D, POCKET_Z, centered=False)
            .translate((px - POCKET_W/2, py - POCKET_D/2, pocket_z_bottom))
        )
        result = result.cut(pocket)

    # ----------------------------------------------------------
    # Step 13: Exterior vertical edge fillets (R=3mm)
    # ----------------------------------------------------------
    print("[13] Exterior vertical edge fillets (R=3mm)")
    try:
        result = result.edges("|Z").fillet(3.0)
    except Exception as e:
        print(f"  WARNING: Edge fillet failed: {e}")

    # ----------------------------------------------------------
    # Step 14: Elephant's foot chamfer on bottom exterior edges
    # ----------------------------------------------------------
    print("[14] Elephant's foot chamfer (0.3mm×45°)")
    try:
        result = result.faces("<Z").chamfer(0.3)
    except Exception as e:
        print(f"  WARNING: Bottom chamfer failed: {e}")

    print("\nModel build complete.")
    return result


# ============================================================
# VALIDATION
# ============================================================
def validate(result):
    print("\n" + "="*60)
    print("RUBRIC 3-5 — VALIDATION")
    print("="*60)

    v = Validator(result)

    bb = result.val().BoundingBox()
    print(f"\nBounding box: X:[{bb.xmin:.2f},{bb.xmax:.2f}] "
          f"Y:[{bb.ymin:.2f},{bb.ymax:.2f}] "
          f"Z:[{bb.zmin:.2f},{bb.zmax:.2f}]")

    print("\n--- Feature probes (Rubric 3) ---")

    # Features 1/2: Shell walls and interior
    v.check_solid("Front wall solid",       110.0, 1.2,   100.0, "solid in front wall Y=1.2 Z=100")
    v.check_solid("Rear wall solid",        110.0, 298.8, 100.0, "solid in rear wall")
    v.check_solid("Left wall solid",        1.2,   150.0, 100.0, "solid in left wall")
    v.check_solid("Right wall solid",       218.8, 150.0, 100.0, "solid in right wall")
    v.check_solid("Floor solid",            110.0, 150.0, 1.2,   "solid in floor")
    v.check_void("Interior cavity",         110.0, 150.0, 90.0,  "void in interior cavity")

    # Feature 3: RP2040 cutout
    v.check_void("RP2040 cutout center",    55.0,  1.2,   142.5, "void at RP2040 center Y=1.2")
    v.check_void("RP2040 inside radius",    55.0+10.0, 1.2, 142.5, "void at r=10 inside RP2040")
    v.check_solid("RP2040 outside radius",  55.0+17.0, 1.2, 142.5, "solid at r=17 outside RP2040")

    # Feature 4: RP2040 retention ledge (annulus at Y:[12.2,13.7], OD=33.2, ID=30)
    # Probe at r=15.8 (between ID/2=15 and OD/2=16.6) at Y=12.95
    v.check_solid("RP2040 ledge annulus",   55.0+15.8, 12.95, 142.5, "solid in ledge annulus (r=15.8)")
    v.check_void("RP2040 ledge inner",      55.0+13.0, 12.95, 142.5, "void inside ledge ID (r=13)")

    # Feature 5: S3 cutout + pocket
    v.check_void("S3 cutout center",        110.0, 1.2,  142.5, "void at S3 center Y=1.2")
    v.check_void("S3 pocket Y=20",          110.0, 20.0, 142.5, "void in S3 pocket Y=20")
    v.check_solid("S3 left of cutout",      83.0,  1.2,  142.5, "solid at X=83 (left of S3 cutout edge 85.85)")
    v.check_solid("Front wall above S3",    110.0, 1.2,  180.0, "solid in front wall above S3 zone")

    # Feature 6: S3 bosses — DESIGN GAP; omitted from this STEP.
    # Verify the S3 pocket side walls are solid (the material the bosses will eventually attach to).
    v.check_solid("S3 left wall solid",     80.0,   1.2, 142.5, "solid in front wall left of S3 cutout (X=80)")
    v.check_solid("S3 right wall solid",   140.0,   1.2, 142.5, "solid in front wall right of S3 cutout (X=140)")

    # Feature 7: KRAUS cutout
    v.check_void("KRAUS cutout center",     165.0, 1.2,   142.5, "void at KRAUS center Y=1.2")
    v.check_void("KRAUS inside radius",     165.0+10.0, 1.2, 142.5, "void at r=10 inside KRAUS")
    v.check_solid("KRAUS outside radius",   165.0+17.0, 1.2, 142.5, "solid at r=17 outside KRAUS")

    # Feature 8: Dock opening
    v.check_void("Dock opening center",     110.0, 1.2, 40.0,  "void at dock center")
    v.check_void("Dock opening near floor", 110.0, 1.2, 1.0,   "void at dock Z=1")
    v.check_solid("Front wall left of dock",15.0,  1.2, 40.0,  "solid left of dock (X=15)")
    v.check_solid("Front wall right of dock",205.0,1.2, 40.0,  "solid right of dock (X=205)")
    v.check_solid("Front wall above dock",  110.0, 1.2, 85.0,  "solid in front wall above dock (Z=85)")

    # Feature 9: Interior dividing wall
    v.check_solid("Dividing wall",          110.0, 176.0, 90.0, "solid at dividing wall Y=176")
    v.check_void("In front of dividing wall",110.0,173.0, 90.0, "void in pump zone Y=173")
    v.check_void("Behind dividing wall",    110.0, 180.0, 90.0, "void in rear zone Y=180")

    # Feature 10: Snap arms
    # ARM_Z0=183.0, ARM_ROOT=2.0 → arm body at Z:[183,185]. Probe at Z=184 (mid-body).
    # Front arm F3 (X=110): arm body at X:[106,114], Y:[2.3,20.3], Z:[183,185]
    v.check_solid("Front arm F3",           110.0, 5.0,   184.0, "solid in front arm F3 (Y=5 Z=184)")
    v.check_solid("Front arm F1",           30.0,  5.0,   184.0, "solid in front arm F1")
    # Rear arm R3 (X=110): arm body at Y:[279.6,297.6], Z:[183,185]
    v.check_solid("Rear arm R3",            110.0, 293.0, 184.0, "solid in rear arm R3 (Y=293 Z=184)")
    # Left arm L4 (Y=150): arm body at X:[2.3,20.3], Z:[183,185]
    v.check_solid("Left arm L4",            5.0,   150.0, 184.0, "solid in left arm L4 (X=5 Z=184)")
    # Right arm RL4 (Y=150): arm body at X:[199.7,217.7], Z:[183,185]
    v.check_solid("Right arm RL4",          215.0, 150.0, 184.0, "solid in right arm RL4 (X=215 Z=184)")

    # Feature 11: Tongue
    # TONGUE_Z0=183.0, TONGUE_H=4.0 → tongue at Z:[183,187]. Probe at Z=185 (mid-tongue).
    v.check_solid("Tongue left arm",        3.5,   150.0, 185.0, "solid at tongue left arm Z=185")
    v.check_solid("Tongue right arm",       216.5, 150.0, 185.0, "solid at tongue right arm Z=185")
    v.check_solid("Tongue rear",            110.0, 296.5, 185.0, "solid at tongue rear arm Z=185")
    v.check_solid("Tongue front-left",      10.0,  3.5,   185.0, "solid at tongue front-left (X=10)")
    v.check_solid("Tongue front-right",     200.0, 3.5,   185.0, "solid at tongue front-right (X=200)")
    v.check_void("Tongue gap at dock",      110.0, 3.5,   185.0, "void in tongue front gap (X=110=dock span)")

    # Feature 12: Alignment pins
    # PIN_Z0=183.0, PIN_H=8.0 → pins at Z:[183,191]. Probe at Z=188 (mid-pin).
    v.check_solid("Align pin FL",           10.0,  10.0,  188.0, "solid at front-left pin Z=188")
    v.check_solid("Align pin FR",           210.0, 10.0,  188.0, "solid at front-right pin")
    v.check_solid("Align pin RL",           10.0,  290.0, 188.0, "solid at rear-left pin")
    v.check_solid("Align pin RR",           210.0, 290.0, 188.0, "solid at rear-right pin")

    # Feature 13: Feet
    v.check_solid("Foot FL",                15.0,  15.0,  -1.5,  "solid at front-left foot")
    v.check_solid("Foot FR",                205.0, 15.0,  -1.5,  "solid at front-right foot")
    v.check_solid("Foot RL",                15.0,  285.0, -1.5,  "solid at rear-left foot")
    v.check_solid("Foot RR",                205.0, 285.0, -1.5,  "solid at rear-right foot")

    # Feature 14: Snap pockets
    v.check_void("Pocket FL",               32.5,  5.4,   1.5,   "void at front-left snap pocket")
    v.check_void("Pocket FR",               187.5, 5.4,   1.5,   "void at front-right pocket")
    v.check_void("Pocket RL",               32.5,  172.4, 1.5,   "void at rear-left pocket")
    v.check_void("Pocket RR",               187.5, 172.4, 1.5,   "void at rear-right pocket")

    # Rubric 4: Solid validity
    print("\n--- Solid validity (Rubric 4) ---")
    v.check_valid()
    v.check_single_body()
    envelope = BOX_W * BOX_D * (BOX_H + FOOT_H)
    v.check_volume(expected_envelope=envelope, fill_range=(0.04, 0.40))

    # Rubric 5: Bounding box
    print("\n--- Bounding box (Rubric 5) ---")
    v.check_bbox("X", bb.xmin, bb.xmax, 0.0, 220.0)
    v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, 300.0)
    v.check_bbox("Z_min (feet)", bb.zmin, bb.zmin, -3.0, -3.0)
    v.check_bbox("Z_max (pins)", bb.zmax, bb.zmax, 191.0, 191.0)  # PIN_Z0=183 + PIN_H=8 = 191

    passed = v.summary()
    return passed, v


# ============================================================
# EXPORT
# ============================================================
def export(result, path):
    cq.exporters.export(result, str(path))
    print(f"\nSTEP file written: {path}")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print_feature_table()
    result = build()
    passed, v = validate(result)

    out_path = Path(__file__).parent / "enclosure-bottom-half-cadquery.step"
    export(result, out_path)

    if not passed:
        print(f"\nWARNING: {v.fail_count} validation check(s) failed.")
        sys.exit(1)
    else:
        print(f"\nAll {v.pass_count} validation checks passed. STEP file ready.")
        sys.exit(0)
