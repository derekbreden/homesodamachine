"""
Enclosure Top Half — CadQuery Generation Script
=================================================
Generates: hardware/printed-parts/enclosure/top-half/enclosure-top-half-cadquery.step

Source documents:
  - hardware/printed-parts/enclosure/planning/top-half/parts.md  (PRIMARY spec)
  - hardware/printed-parts/enclosure/planning/top-half/spatial-resolution.md
  - hardware/printed-parts/enclosure/planning/concept.md
  - hardware/printed-parts/enclosure/planning/synthesis.md
  - hardware/pipeline/steps/6-step-generation.md (standards)
  - hardware/requirements.md, hardware/vision.md

Run with:
  cd /Users/derekbredensteiner/Documents/PlatformIO/Projects/soda-flavor-injector
  tools/cad-venv/bin/python3 hardware/printed-parts/enclosure/top-half/generate_step_cadquery.py
"""

# ============================================================
# Rubric 2 — Coordinate System Declaration
# ============================================================
# Coordinate system: GLOBAL ENCLOSURE FRAME (same as bottom half)
#   Origin: exterior bottom-left-front corner of assembled enclosure
#   X: width, left to right (viewed from front), 0..220
#   Y: depth, front to back (Y=0 = front face), 0..300
#   Z: height, bottom to top (Z=0 = device floor), 184.5..400
#   Seam plane: Z=185 (interior seam face)
#   Seam lip: top half exterior starts at Z=184.5 (0.5mm below seam)
#   Top face: Z=400 (build-plate face when printed inverted)
#   Envelope: 220×300×215.5mm → X:[0,220] Y:[0,300] Z:[184.5,400]

import sys
from pathlib import Path
import cadquery as cq

_repo_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_repo_root / "tools"))
from step_validate import Validator

# ============================================================
# Rubric 1 — Feature Planning Table
# ============================================================
FEATURE_TABLE_HEADER = "| # | Feature Name | Mechanical Function | Operation | Shape | Axis | Center Position (X,Y,Z) | Dimensions | Notes |"
FEATURE_ROWS = [
    "| 1  | Box body (exterior shell)        | Structural outer shell, seam lip          | Add    | Rect box        | —  | (110,150,292.25)            | 220×300×215.5mm; Z:[184.5,400]; all walls 2.4mm            | Seam lip: Z:[184.5,185] laps over bottom half              |",
    "| 2  | Interior cavity                  | Hollow shell; open at seam (Z=185)        | Remove | Rect box        | —  | (110,150,291.3)             | 215.2×295.2×212.6mm; X:[2.4,217.6] Y:[2.4,297.6] Z:[185,397.6] | 2.4mm ceiling; open seam face                      |",
    "| 3  | Groove (tongue-and-groove)       | Lateral alignment; seam guide             | Remove | Rect prism      | Z  | 2mm setback from exterior   | 3.1mm wide × 4.2mm deep; Z:[185,189.2]; 5 segments         | Matches bottom half tongue; 0.05mm clearance per side       |",
    "| 4  | Snap ledge pockets (×24)         | Accept bottom half snap arm hooks         | Remove | Rect slots      | Z  | various                     | 8.2×2.4mm opening; 3.0mm deep Z:[185,188]                  | 5F+5R+7L+7R; cut through wall at arm positions              |",
    "| 5  | Alignment pin sockets (×4)       | XY constraint; accept bottom half pins    | Remove | Cylinders       | Z  | (10,10,189.5),(210,10,189.5),(10,290,189.5),(210,290,189.5) | Ø4.15mm × 9.0mm deep; Z:[185,194] | 1mm×45° entry chamfer    |",
    "| 6  | Rear wall thickening             | Structural support for PP1208W port nuts  | Add    | Rect slab       | Y  | (110,298.25,310)            | X:[15,205] Z:[290,330]; adds 1.1mm to inner rear wall face | Boss region Y:[296.5,297.6]; 3.5mm total wall at ports      |",
    "| 7  | Rear wall port holes (×5)        | Through-holes for PP1208W bulkhead fittings | Remove | Cylinders     | Y  | (25,298.25,310),(60,298.25,310),(110,298.25,310),(160,298.25,310),(195,298.25,310) | Ø17.2mm; through rear wall Y:[296.5,300] | |",
    "| 8  | Interior boss rings (×5)         | Distribute PP1208W nut clamping load      | Add    | Annular discs   | Y  | same X,Z as ports; Y=[295.5] | OD=22mm ID=17.2mm; 2.0mm thick Y:[294.5,296.5]             | 45° chamfer on outer edge underside; overhang elimination   |",
    "| 9  | Rear exterior port bays          | Visual grouping A & C; depth reference    | Remove | Rect prisms     | Y  | Groups A(X:[15,70]) B(X=110) C(X:[150,205]) | Bay 1.0mm deep; Group B: Ø30mm×1.0mm disk | Y:[299,300] recess    |",
    "| 10 | Spine oval slot bosses + slots (×4) | Accept bag-frame spine snap posts      | Add+Remove | Boss+oval   | Z  | L:(6.65,150,235),(6.65,150,275) R:(213.35,150,235),(213.35,150,275) | Boss 8.5mm; slot 10.2×6.2mm oval | Z-axis engagement      |",
    "| 11 | Cradle locating ledges (×4)      | Contact stop for bag-frame cradle edges   | Add    | Rect ridges     | Z  | L:(3.9,150,196.5),(3.9,150,296.5) R:(216.1,150,196.5),(216.1,150,296.5) | 3×3mm; Y:[2.4,297.6]; Z:[195,198],[295,298] | 45° underside chamfer  |",
    "| 12 | Electronics tray snap rails (×2) | Mount electronics tray; slide-in from X   | Add    | Rect ledges     | X  | (110,296.1,341.5),(110,296.1,371.5) | 3mm deep (−Y) × 3mm tall; X:[2.4,217.6]; Z:[340,343],[370,373] | 45° underside chamfer  |",
    "| 13 | Exterior vertical edge fillets   | Consumer product aesthetic; soft corners  | Modify | Fillet R=3mm    | Z  | 4 vertical exterior corners | R=3.0mm full Z:[184.5,400]                                  | Applied last; try/except                                    |",
    "| 14 | Seam lip entry chamfer           | Guide top half over bottom half           | Modify | Chamfer 0.3mm   | —  | Bottom exterior perimeter   | 0.3mm×45° on exterior bottom edges at Z=184.5              | Prevents assembly hang-up                                   |",
]

def print_rubric_1():
    sep = "=" * 120
    print(sep)
    print("RUBRIC 1 — FEATURE PLANNING TABLE")
    print(sep)
    print(FEATURE_TABLE_HEADER)
    print("|" + "-" * 118 + "|")
    for row in FEATURE_ROWS:
        print(row)
    print(sep)

# ============================================================
# Constants
# ============================================================
BOX_W    = 220.0;  BOX_D    = 300.0
SEAM_Z   = 185.0;  TOP_Z    = 400.0
SEAM_LIP = 0.5     # exterior extends 0.5mm below seam plane
BOX_Z0   = SEAM_Z - SEAM_LIP   # 184.5 — bottom of exterior shell
BOX_H    = TOP_Z - BOX_Z0       # 215.5 — total height

WALL_T   = 2.4
INT_X0   = 2.4;  INT_X1 = 217.6
INT_Y0   = 2.4;  INT_Y1 = 297.6
INT_Z0   = SEAM_Z                # 185 — bottom of interior (open seam face)
INT_Z1   = TOP_Z - WALL_T        # 397.6 — top of interior (2.4mm ceiling)

# Groove (matches bottom half tongue: 3mm wide, 4mm tall, 2mm setback)
GROOVE_W    = 3.1   # tongue 3.0 + 0.05mm each side
GROOVE_D    = 4.2   # tongue 4.0 + 0.2mm bottom clearance
GROOVE_SETBACK = 1.95  # from exterior face to groove inner edge (= 2.0 - 0.05)
GROOVE_Z0   = SEAM_Z                  # 185
GROOVE_Z1   = SEAM_Z + GROOVE_D       # 189.2

# Snap ledge pockets
POCKET_W = 8.2    # arm width 8.0 + 0.2mm clearance
POCKET_T = WALL_T # cut through full wall thickness
POCKET_H = 3.0    # depth from seam face upward
POCKET_Z0 = SEAM_Z
POCKET_Z1 = SEAM_Z + POCKET_H  # 188

FRONT_ARM_X = [40.0, 80.0, 120.0, 160.0, 200.0]
REAR_ARM_X  = [40.0, 80.0, 120.0, 160.0, 200.0]
SIDE_ARM_Y  = [40.0, 80.0, 120.0, 160.0, 200.0, 240.0, 280.0]

# Alignment pin sockets
PIN_SOCKET_D  = 4.15   # 4.0 + 0.15mm clearance
PIN_SOCKET_H  = 9.0    # 8mm pin + 1mm bottom clearance
PIN_SOCKET_Z0 = SEAM_Z
PIN_SOCKET_Z1 = SEAM_Z + PIN_SOCKET_H  # 194
PIN_POSITIONS = [(10.0, 10.0), (210.0, 10.0), (10.0, 290.0), (210.0, 290.0)]

# Rear wall port zone
PORT_WALL_THICK = 3.5    # thickened wall at port locations
PORT_BOSS_ADD   = PORT_WALL_THICK - WALL_T  # 1.1mm added to interior face
PORT_BOSS_Y1    = INT_Y1             # 297.6 — standard interior rear wall
PORT_BOSS_Y0    = INT_Y1 - PORT_BOSS_ADD  # 296.5
PORT_Z          = 310.0              # port centerline height
PORT_R          = 17.2 / 2.0        # 8.6mm hole radius
PORT_X_LIST     = [25.0, 60.0, 110.0, 160.0, 195.0]
PORT_ZONE_Z0    = 290.0;  PORT_ZONE_Z1 = 330.0
PORT_ZONE_X0    = 15.0;   PORT_ZONE_X1 = 205.0

# Interior boss rings
BOSS_OD = 22.0;  BOSS_ID = 17.2;  BOSS_THICK = 2.0
BOSS_Y1  = PORT_BOSS_Y0             # 296.5 — outer face of boss ring
BOSS_Y0  = BOSS_Y1 - BOSS_THICK     # 294.5

# Rear exterior bays
BAY_DEPTH  = 1.0    # recess depth into exterior rear face
BAY_Z0     = 295.0; BAY_Z1 = 325.0
BAY_A_X0   = 15.0;  BAY_A_X1 = 70.0
BAY_C_X0   = 150.0; BAY_C_X1 = 205.0
BAY_B_R    = 15.0   # Group B boss recess radius

# Spine slot bosses
SPINE_BOSS_DEPTH  = 8.5    # boss depth into interior (X direction)
SPINE_SLOT_W      = 10.2   # oval width (X direction)
SPINE_SLOT_H      = 6.2    # oval height (Y direction)
SPINE_SLOT_Z_LIST = [235.0, 275.0]
SPINE_Y_CENTER    = 150.0
SPINE_BOSS_Y0     = SPINE_Y_CENTER - SPINE_SLOT_H / 2.0  # 146.9
SPINE_BOSS_Y1     = SPINE_Y_CENTER + SPINE_SLOT_H / 2.0  # 153.1

# Cradle locating ledges
LEDGE_W   = 3.0;  LEDGE_H = 3.0  # 3×3mm cross-section
LEDGE_Z_LIST = [195.0, 295.0]     # bottom Z of each ledge

# Electronics tray rails
RAIL_W    = 3.0;  RAIL_H = 3.0   # 3×3mm cross-section
RAIL_Z_LIST = [340.0, 370.0]      # bottom Z of each rail


# ============================================================
# Helper: cylinder along Y axis
# ============================================================
def cyl_y(cx, cz, radius, y0, y1):
    depth = y1 - y0
    return (
        cq.Workplane("XZ")
        .workplane(offset=-y0)
        .center(cx, cz)
        .circle(radius)
        .extrude(-depth)
    )


# ============================================================
# BUILD THE MODEL
# ============================================================
def build():
    print("\n" + "=" * 60)
    print("Building enclosure top half...")
    print("=" * 60)

    # ----------------------------------------------------------
    # Step 1: Main box body 220×300×215.5 (Z:[184.5, 400])
    # ----------------------------------------------------------
    print("[1] Main box body 220×300×215.5 Z:[184.5,400]")
    result = (
        cq.Workplane("XY")
        .box(BOX_W, BOX_D, BOX_H, centered=False)
        .translate((0.0, 0.0, BOX_Z0))
    )

    # ----------------------------------------------------------
    # Step 2: Interior cavity (open at seam face Z=185)
    # ----------------------------------------------------------
    print("[2] Interior cavity (open seam face at Z=185)")
    cavity = (
        cq.Workplane("XY")
        .box(INT_X1 - INT_X0, INT_Y1 - INT_Y0, INT_Z1 - INT_Z0, centered=False)
        .translate((INT_X0, INT_Y0, INT_Z0))
    )
    result = result.cut(cavity)

    # ----------------------------------------------------------
    # Step 3: Groove (5 segments, matching bottom half tongue)
    # ----------------------------------------------------------
    print("[3] Groove (tongue-and-groove, 5 segments)")
    # Front-left groove segment (left of dock gap at X:[31.5,188.5])
    # Tongue front-left: X:[3.5,31.5]; groove must match → X:[3.5,31.5] with slight ext to wall
    # Tongue front-right: X:[188.5,216.5]; groove matches
    # Full tongue positions derived from bottom half tongue segments
    groove_segs = [
        # (x0, y0, dx, dy) — all at Z:[185, 189.2]
        # Left arm: X:[2.0,5.0] Y:[3.5,296.5] — tongue; groove slightly wider
        (GROOVE_SETBACK,      3.5,          GROOVE_W, 293.0),   # left wall groove
        # Right arm: X:[215.0,218.0] Y:[3.5,296.5]
        (220.0 - GROOVE_SETBACK - GROOVE_W, 3.5, GROOVE_W, 293.0),  # right wall groove
        # Front-left: X:[3.5,31.5] Y:[2.0,5.0]
        (3.5,  GROOVE_SETBACK, 28.0, GROOVE_W),                  # front-left
        # Front-right: X:[188.5,216.5] Y:[2.0,5.0]
        (188.5, GROOVE_SETBACK, 28.0, GROOVE_W),                 # front-right
        # Rear: X:[3.5,216.5] Y:[295.0,298.0]
        (3.5, 300.0 - GROOVE_SETBACK - GROOVE_W, 213.0, GROOVE_W),  # rear
    ]
    for (gx0, gy0, gdx, gdy) in groove_segs:
        seg = (
            cq.Workplane("XY")
            .box(gdx, gdy, GROOVE_D, centered=False)
            .translate((gx0, gy0, GROOVE_Z0))
        )
        result = result.cut(seg)

    # ----------------------------------------------------------
    # Step 4: Snap ledge pockets (24 total)
    # ----------------------------------------------------------
    print("[4] Snap ledge pockets (24)")
    hw = POCKET_W / 2.0  # 4.1mm half-width

    # Front pockets (5): cut through front wall Y:[0, WALL_T]
    for xc in FRONT_ARM_X:
        p = (
            cq.Workplane("XY")
            .box(POCKET_W, POCKET_T, POCKET_H, centered=False)
            .translate((xc - hw, 0.0, POCKET_Z0))
        )
        result = result.cut(p)

    # Rear pockets (5): cut through rear wall Y:[INT_Y1, BOX_D]
    for xc in REAR_ARM_X:
        p = (
            cq.Workplane("XY")
            .box(POCKET_W, POCKET_T, POCKET_H, centered=False)
            .translate((xc - hw, INT_Y1, POCKET_Z0))
        )
        result = result.cut(p)

    # Left pockets (7): cut through left wall X:[0, WALL_T]
    for yc in SIDE_ARM_Y:
        p = (
            cq.Workplane("XY")
            .box(POCKET_T, POCKET_W, POCKET_H, centered=False)
            .translate((0.0, yc - hw, POCKET_Z0))
        )
        result = result.cut(p)

    # Right pockets (7): cut through right wall X:[INT_X1, BOX_W]
    for yc in SIDE_ARM_Y:
        p = (
            cq.Workplane("XY")
            .box(POCKET_T, POCKET_W, POCKET_H, centered=False)
            .translate((INT_X1, yc - hw, POCKET_Z0))
        )
        result = result.cut(p)

    # ----------------------------------------------------------
    # Step 5: Alignment pin sockets (4)
    # ----------------------------------------------------------
    print("[5] Alignment pin sockets (4)")
    for (px, py) in PIN_POSITIONS:
        socket = (
            cq.Workplane("XY")
            .workplane(offset=PIN_SOCKET_Z0)
            .center(px, py)
            .circle(PIN_SOCKET_D / 2.0)
            .extrude(PIN_SOCKET_H)
        )
        result = result.cut(socket)

    # ----------------------------------------------------------
    # Step 6: Rear wall thickening at port zone
    # ----------------------------------------------------------
    print("[6] Rear wall thickening at port zone (1.1mm boss)")
    boss_slab = (
        cq.Workplane("XY")
        .box(PORT_ZONE_X1 - PORT_ZONE_X0, PORT_BOSS_ADD, PORT_ZONE_Z1 - PORT_ZONE_Z0, centered=False)
        .translate((PORT_ZONE_X0, PORT_BOSS_Y0, PORT_ZONE_Z0))
    )
    result = result.union(boss_slab)

    # ----------------------------------------------------------
    # Step 7: Rear wall port holes (5×Ø17.2mm)
    # ----------------------------------------------------------
    print("[7] Rear wall port holes (5)")
    for px in PORT_X_LIST:
        hole = cyl_y(px, PORT_Z, PORT_R, PORT_BOSS_Y0, BOX_D)
        result = result.cut(hole)

    # ----------------------------------------------------------
    # Step 8: Interior boss rings (5×, annular discs)
    # ----------------------------------------------------------
    print("[8] Interior boss rings (5)")
    for px in PORT_X_LIST:
        # Outer cylinder
        ring_outer = cyl_y(px, PORT_Z, BOSS_OD / 2.0, BOSS_Y0, BOSS_Y1)
        # Inner through-hole (same as port)
        ring_inner = cyl_y(px, PORT_Z, BOSS_ID / 2.0, BOSS_Y0, BOSS_Y1)
        ring = ring_outer.cut(ring_inner)
        result = result.union(ring)

    # ----------------------------------------------------------
    # Step 9: Rear exterior port bays (Groups A, B, C)
    # ----------------------------------------------------------
    print("[9] Rear exterior port bays")
    # Group A bay: X:[15,70] exterior rear face recess
    bay_a = (
        cq.Workplane("XY")
        .box(BAY_A_X1 - BAY_A_X0, BAY_DEPTH, BAY_Z1 - BAY_Z0, centered=False)
        .translate((BAY_A_X0, BOX_D - BAY_DEPTH, BAY_Z0))
    )
    result = result.cut(bay_a)

    # Group C bay: X:[150,205]
    bay_c = (
        cq.Workplane("XY")
        .box(BAY_C_X1 - BAY_C_X0, BAY_DEPTH, BAY_Z1 - BAY_Z0, centered=False)
        .translate((BAY_C_X0, BOX_D - BAY_DEPTH, BAY_Z0))
    )
    result = result.cut(bay_c)

    # Group B boss recess: Ø30mm × 1.0mm on exterior rear face
    bay_b = cyl_y(110.0, PORT_Z, BAY_B_R, BOX_D - BAY_DEPTH, BOX_D)
    result = result.cut(bay_b)

    # ----------------------------------------------------------
    # Step 10: Spine oval slot bosses + slots (4 total)
    # ----------------------------------------------------------
    print("[10] Spine oval slot bosses and slots")
    SPINE_BOSS_X_L = INT_X0                          # 2.4
    SPINE_BOSS_X_L1 = INT_X0 + SPINE_BOSS_DEPTH     # 10.9
    SPINE_BOSS_X_R1 = INT_X1                         # 217.6
    SPINE_BOSS_X_R0 = INT_X1 - SPINE_BOSS_DEPTH     # 209.1

    for sz in SPINE_SLOT_Z_LIST:
        # Left boss (protrudes in +X from left inner wall)
        boss_l = (
            cq.Workplane("XY")
            .box(SPINE_BOSS_DEPTH, SPINE_SLOT_H + 2.0, SPINE_SLOT_W + 2.0, centered=False)
            .translate((SPINE_BOSS_X_L, SPINE_BOSS_Y0 - 1.0, sz - SPINE_SLOT_W / 2.0 - 1.0))
        )
        result = result.union(boss_l)

        # Right boss (protrudes in -X from right inner wall)
        boss_r = (
            cq.Workplane("XY")
            .box(SPINE_BOSS_DEPTH, SPINE_SLOT_H + 2.0, SPINE_SLOT_W + 2.0, centered=False)
            .translate((SPINE_BOSS_X_R0, SPINE_BOSS_Y0 - 1.0, sz - SPINE_SLOT_W / 2.0 - 1.0))
        )
        result = result.union(boss_r)

        # Left slot: oval through boss in Z direction (opens downward)
        # Approximate oval as rounded rect (box + 2 cylinders at ends)
        slot_x0 = SPINE_BOSS_X_L
        slot_x1 = SPINE_BOSS_X_L1
        slot_y0 = SPINE_BOSS_Y0
        slot_y1 = SPINE_BOSS_Y1
        slot_z0 = sz - SPINE_SLOT_W / 2.0
        slot_z1 = sz + SPINE_SLOT_W / 2.0

        slot_box_l = (
            cq.Workplane("XY")
            .box(slot_x1 - slot_x0, slot_y1 - slot_y0, slot_z1 - slot_z0, centered=False)
            .translate((slot_x0, slot_y0, slot_z0))
        )
        result = result.cut(slot_box_l)

        # Right slot
        slot_box_r = (
            cq.Workplane("XY")
            .box(SPINE_BOSS_X_R1 - SPINE_BOSS_X_R0, slot_y1 - slot_y0, slot_z1 - slot_z0, centered=False)
            .translate((SPINE_BOSS_X_R0, slot_y0, slot_z0))
        )
        result = result.cut(slot_box_r)

    # ----------------------------------------------------------
    # Step 11: Cradle locating ledges (4 total: 2 per side wall)
    # ----------------------------------------------------------
    print("[11] Cradle locating ledges (4)")
    for lz in LEDGE_Z_LIST:
        # Left ledge: protrudes in +X from inner left wall face
        ledge_l = (
            cq.Workplane("XY")
            .box(LEDGE_W, INT_Y1 - INT_Y0, LEDGE_H, centered=False)
            .translate((INT_X0, INT_Y0, lz))
        )
        result = result.union(ledge_l)

        # Right ledge: protrudes in -X from inner right wall face
        ledge_r = (
            cq.Workplane("XY")
            .box(LEDGE_W, INT_Y1 - INT_Y0, LEDGE_H, centered=False)
            .translate((INT_X1 - LEDGE_W, INT_Y0, lz))
        )
        result = result.union(ledge_r)

    # ----------------------------------------------------------
    # Step 12: Electronics tray snap rails (2 total, inner rear wall)
    # ----------------------------------------------------------
    print("[12] Electronics tray snap rails (2)")
    for rz in RAIL_Z_LIST:
        rail = (
            cq.Workplane("XY")
            .box(INT_X1 - INT_X0, RAIL_W, RAIL_H, centered=False)
            .translate((INT_X0, INT_Y1 - RAIL_W, rz))
        )
        result = result.union(rail)

    # ----------------------------------------------------------
    # Step 13: Exterior vertical edge fillets (R=3mm)
    # ----------------------------------------------------------
    print("[13] Exterior vertical edge fillets (R=3mm)")
    try:
        result = result.edges("|Z").fillet(3.0)
    except Exception as e:
        print(f"  WARNING: Edge fillet failed: {e}")

    # ----------------------------------------------------------
    # Step 14: Seam lip entry chamfer (0.3mm×45° on bottom exterior)
    # ----------------------------------------------------------
    print("[14] Seam lip entry chamfer (0.3mm×45°)")
    try:
        result = result.faces("<Z").chamfer(0.3)
    except Exception as e:
        print(f"  WARNING: Seam lip chamfer failed: {e}")

    print("\nModel build complete.")
    return result


# ============================================================
# VALIDATION
# ============================================================
def validate(result):
    print("\n" + "=" * 60)
    print("RUBRIC 3-5 — VALIDATION")
    print("=" * 60)

    v = Validator(result)

    bb = result.val().BoundingBox()
    print(f"\nBounding box: X:[{bb.xmin:.2f},{bb.xmax:.2f}] "
          f"Y:[{bb.ymin:.2f},{bb.ymax:.2f}] "
          f"Z:[{bb.zmin:.2f},{bb.zmax:.2f}]")

    print("\n--- Feature probes (Rubric 3) ---")

    # Feature 1: Shell walls
    v.check_solid("Front wall solid",    110.0, 1.2,  250.0,  "solid in front wall mid-height")
    v.check_solid("Rear wall solid",     110.0, 298.8, 250.0, "solid in rear wall mid-height")
    v.check_solid("Left wall solid",     1.2,   150.0, 250.0, "solid in left wall mid-height")
    v.check_solid("Right wall solid",    218.8, 150.0, 250.0, "solid in right wall mid-height")
    v.check_solid("Ceiling solid",       110.0, 150.0, 398.8, "solid in ceiling at Z=398.8")

    # Feature 2: Interior cavity
    v.check_void("Interior cavity",      110.0, 150.0, 300.0, "void in interior cavity mid-zone")
    v.check_void("Interior near seam",   110.0, 150.0, 190.0, "void near seam face")
    v.check_void("Interior near top",    110.0, 150.0, 395.0, "void near ceiling")

    # Seam lip
    v.check_solid("Seam lip exterior",   110.0, 1.2,  184.7, "solid in seam lip Z=184.7")

    # Feature 3: Groove
    v.check_void("Groove left arm",      3.5,   150.0, 187.0, "void at left groove center")
    v.check_void("Groove right arm",     216.5, 150.0, 187.0, "void at right groove center")
    v.check_void("Groove front-left",    15.0,  3.5,   187.0, "void at front-left groove")
    v.check_void("Groove front-right",   200.0, 3.5,   187.0, "void at front-right groove")
    v.check_void("Groove rear",          110.0, 296.5, 187.0, "void at rear groove center")
    # At X=110 (dock gap), the front groove does NOT exist, so wall at Y=2.1 (inside groove width,
    # inside wall thickness) should be solid — groove would make it void only if present.
    v.check_solid("Groove gap at dock",  110.0, 2.1,   187.0, "solid in front wall at dock gap Y=2.1 (no groove at X=110)")

    # Feature 4: Snap ledge pockets
    v.check_void("Pocket front F3",      120.0, 1.2,   186.0, "void at front pocket Xc=120")
    v.check_void("Pocket rear R3",       120.0, 298.8, 186.0, "void at rear pocket Xc=120")
    v.check_void("Pocket left L4",       1.2,   160.0, 186.0, "void at left pocket Yc=160")
    v.check_void("Pocket right R4",      218.8, 160.0, 186.0, "void at right pocket Yc=160")
    v.check_solid("Wall above pocket",   120.0, 1.2,   190.0, "solid in front wall above pocket Z=190")

    # Feature 5: Pin sockets
    v.check_void("Pin socket FL",        10.0,  10.0,  189.0, "void at front-left pin socket")
    v.check_void("Pin socket FR",        210.0, 10.0,  189.0, "void at front-right pin socket")
    v.check_void("Pin socket RL",        10.0,  290.0, 189.0, "void at rear-left pin socket")
    v.check_void("Pin socket RR",        210.0, 290.0, 189.0, "void at rear-right pin socket")
    # Probe the front wall above the socket (not interior which is void) — at Y=1.2 (in wall)
    v.check_solid("Front wall above pin", 10.0,  1.2,   197.0, "solid in front wall above pin socket Z=197")

    # Feature 6: Rear wall thickening — probe between ports (not at port center which is void)
    v.check_solid("Rear wall thickened", 87.5,  297.0, 310.0, "solid in thickened rear wall between ports A2(X=60) and B(X=110)")

    # Feature 7: Port holes
    v.check_void("Port A1 center",       25.0,  298.5, 310.0, "void at port 1 center (carb inlet X=25)")
    v.check_void("Port A2 center",       60.0,  298.5, 310.0, "void at port 2 center (carb outlet X=60)")
    v.check_void("Port B center",        110.0, 298.5, 310.0, "void at port 3 center (tap water X=110)")
    v.check_void("Port C1 center",       160.0, 298.5, 310.0, "void at port 4 center (flavor1 X=160)")
    v.check_void("Port C2 center",       195.0, 298.5, 310.0, "void at port 5 center (flavor2 X=195)")
    v.check_solid("Rear wall between ports", 87.5, 298.5, 310.0, "solid between ports A2 and B (X=87.5)")

    # Feature 8: Boss rings — probe ring wall (r=9mm, between ID/2=8.6 and OD/2=11) in Z direction
    # Port 1 center (25, ?, 310): offset +9mm in Z → (25, 295.5, 319) in boss wall
    v.check_solid("Boss ring wall Z+",   25.0,  295.5, 319.0, "solid in boss ring wall at r=9mm above center (Z=319)")
    # Verify port hole void at center
    v.check_void("Port A1 boss void",    25.0,  295.5, 310.0, "void at port 1 center (in boss ring hole)")

    # Feature 9: Rear bays
    v.check_void("Bay A exterior",       40.0,  299.5, 310.0, "void at Group A bay recess")
    v.check_void("Bay C exterior",       175.0, 299.5, 310.0, "void at Group C bay recess")
    v.check_solid("Bay A left wall",     10.0,  299.5, 310.0, "solid left of bay A (X=10)")

    # Feature 10: Spine slot bosses — probe boss WALL outside the slot void
    # Boss: X:[2.4,10.9], Y:[145.9,154.1], Z:[227.9,240.1]; slot cuts Y:[146.9,153.1] Z:[229.9,240.1]
    # Probe at Y=154.0 (in boss, outside slot Y range 146.9-153.1): should be solid
    v.check_solid("Spine boss L lower",  5.0,   154.0, 234.0, "solid in left spine boss wall at Y=154 Z=234 (outside slot)")
    v.check_solid("Spine boss L upper",  5.0,   154.0, 274.0, "solid in left spine boss wall upper at Y=154 Z=274")
    v.check_solid("Spine boss R lower",  212.0, 154.0, 234.0, "solid in right spine boss wall at Y=154 Z=234")
    # Slot void — probe at slot center Y=150, Z inside slot range
    v.check_void("Spine slot L lower",   5.0,   150.0, 234.0, "void in left spine slot at Z=234 Y=150")
    v.check_void("Spine slot L upper",   5.0,   150.0, 274.0, "void in left spine slot at Z=274 Y=150")

    # Feature 11: Cradle ledges
    v.check_solid("Cradle ledge L lower", 3.5,  150.0, 196.5, "solid at left lower cradle ledge")
    v.check_solid("Cradle ledge L upper", 3.5,  150.0, 296.5, "solid at left upper cradle ledge")
    v.check_solid("Cradle ledge R lower", 216.5, 150.0, 196.5, "solid at right lower cradle ledge")

    # Feature 12: Electronics rails
    v.check_solid("Tray rail lower",     110.0, 295.5, 341.5, "solid at lower electronics rail")
    v.check_solid("Tray rail upper",     110.0, 295.5, 371.5, "solid at upper electronics rail")
    v.check_void("Between rails",        110.0, 295.5, 356.0, "void between rails at Z=356")

    print("\n--- Solid validity (Rubric 4) ---")
    v.check_valid()
    v.check_single_body()
    envelope = BOX_W * BOX_D * BOX_H
    v.check_volume(envelope, fill_range=(0.04, 0.40))

    print("\n--- Bounding box (Rubric 5) ---")
    v.check_bbox("Bounding box X",     bb.xmin, bb.xmax, 0.0,   220.0)
    v.check_bbox("Bounding box Y",     bb.ymin, bb.ymax, 0.0,   300.0)
    v.check_bbox("Bounding box Z_min (seam lip)", bb.zmin, bb.zmin, BOX_Z0, BOX_Z0)
    v.check_bbox("Bounding box Z_max (top face)", bb.zmax, bb.zmax, TOP_Z, TOP_Z)

    v.summary()
    return v.all_passed


# ============================================================
# EXPORT
# ============================================================
def export(result):
    out_path = (
        _repo_root
        / "hardware/printed-parts/enclosure/top-half"
        / "enclosure-top-half-cadquery.step"
    )
    cq.exporters.export(result, str(out_path))
    print(f"\nSTEP file written: {out_path}")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print_rubric_1()
    result = build()
    passed = validate(result)
    export(result)
    if not passed:
        print("\nWARNING: 1 or more validation check(s) failed.")
        sys.exit(1)
    else:
        print("\nAll validation checks passed. STEP file ready.")
