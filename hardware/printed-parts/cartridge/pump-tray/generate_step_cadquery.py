"""
Pump-Tray — CadQuery STEP Generation Script
Pipeline step: 6 — STEP Generation
Input: planning/parts.md, planning/spatial-resolution.md
Output: pump-tray-cadquery.step

Part: Single printed PETG structural plate carrying two Kamoer KPHM-400
peristaltic pumps inside the pump cartridge.

Coordinate system (part local frame):
  Origin: front-face bottom-left corner (X=0, Y=0, Z=0)
  X: tray width, left to right, 0 → 144 mm
  Y: tray thickness, front-face (build plate) to rear-face (motor zone), 0 → 5 mm
     Y < 0: ribs/cross-rib protrude toward pump (front-face side)
     Y > 5: bosses protrude toward motor zone (rear-face side)
  Z: tray height, bottom to top, 0 → 80 mm

  CadQuery workplane notes:
    Workplane "XY": normal = +Z. box(L,W,H) → L along X, W along Y, H along Z.
    Workplane "XZ": normal = -Y. box(L,W,H) → L along X, W along Z, H along -Y.
      extrude(+d) on XZ workplane → goes in -Y direction.
      extrude(-d) on XZ workplane → goes in +Y direction.
      workplane(offset=k) shifts plane by k in normal (-Y) direction:
        offset=0  → plane at Y=0
        offset=-5 → plane at Y=5  (shifted 5mm in -Y normal, so at +5 world Y)
        offset=5  → plane at Y=-5 (shifted 5mm in +Y direction from Y=0)

  KEY WORKPLANE TRICK:
    To place a cylinder at world Y = Ypos, use offset=-(Ypos):
      .workplane("XZ").workplane(offset=-Ypos) → plane sits at world Y = Ypos
    Then extrude(+depth) cuts/builds in -Y direction (lower Y values).
    Then extrude(-depth) cuts/builds in +Y direction (higher Y values).
"""

import sys
import math
from pathlib import Path

import cadquery as cq

# Add tools/ to sys.path for step_validate
# Script at: hardware/printed-parts/cartridge/pump-tray/generate_step_cadquery.py
# parents[4] = project root
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))
from step_validate import Validator

# ==============================================================================
# Part parameters
# ==============================================================================

PLATE_W = 144.0
PLATE_D = 5.0
PLATE_H = 80.0
CORNER_R = 3.0

BORE_D = 37.2
BORE_R = BORE_D / 2
BORE1_X, BORE1_Z = 34.5, 40.0
BORE2_X, BORE2_Z = 109.5, 40.0
BORE_CHAMFER = 0.5

CLEAR_D = 3.6
CLEAR_R = CLEAR_D / 2
CLEAR_Y_END = 5.5

BOSS_OD = 9.0
BOSS_R  = BOSS_OD / 2
BOSS_Y0 = 5.0
BOSS_Y1 = 10.0
BOSS_H  = BOSS_Y1 - BOSS_Y0
BOSS_FILLET = 1.5

INSERT_D = 4.7
INSERT_R = INSERT_D / 2
INSERT_DEPTH = 4.5   # Y=10 → Y=5.5

BOSS_POSITIONS = [
    (10.5,  16.0),
    (58.5,  16.0),
    (10.5,  64.0),
    (58.5,  64.0),
    (85.5,  16.0),
    (133.5, 16.0),
    (85.5,  64.0),
    (133.5, 64.0),
]

FIELD_STEP = 0.5

CROSSRIB_Z0, CROSSRIB_Z1 = 37.0, 43.0
CROSSRIB_H = CROSSRIB_Z1 - CROSSRIB_Z0
CROSSRIB_Y_PROTRUDE = 5.0
CROSSRIB_CHAMFER = 1.0
CROSSRIB_FILLET = 2.0

RIB_WIDTH = 4.0
RIB_Y_PROTRUDE = 5.0
RIB_FILLET = 2.0
RIB_CHAMFER = 1.0

CHAN_Z0, CHAN_Z1 = 37.0, 43.0
CHAN_W = CHAN_Z1 - CHAN_Z0
CHAN_DEPTH = 4.0
CHAN1_X0, CHAN1_X1 = 0.0, 15.9
CHAN2_X0, CHAN2_X1 = 128.1, 144.0
CHAN_FLOOR_Y = PLATE_D - CHAN_DEPTH   # Y=1
CHAN_FILLET_R = 1.5

BUMP_HEIGHT = 1.5
BUMP_R = 1.0
BUMP_POSITIONS = [
    (10.9, 40.0),
    (5.9,  40.0),
    (133.1, 40.0),
    (138.1, 40.0),
]

NOTCH_DEPTH = 1.5
NOTCH_W = 3.0
NOTCH_Z0, NOTCH_Z1 = 38.5, 41.5
NOTCH_Y0, NOTCH_Y1 = 2.0, 5.0

CHAMFER_PERIMETER = 1.5
CHAMFER_ELEPHANT = 0.3

# ==============================================================================
# Feature planning and coordinate tables (Rubric 1 + 2)
# ==============================================================================
print("""
PUMP-TRAY FEATURE PLANNING TABLE (Rubric 1)
============================================
F1  Plate body         144×5×80mm, 3mm plan corners  Add Box
F2  Motor bores (2×)   D=37.2mm through Y=0→5        Remove Cyl  0.5mm chamfer at Y=5
F3  M3 clearance (8×)  D=3.6mm, Y=0→5.5              Remove Cyl
F4  Bosses (8×)        OD=9mm, Y=5→10, 1.5mm fillet  Add Cyl
F4  Insert bores (8×)  D=4.7mm, Y=5.5→10             Remove Cyl
F5  Field zone step    0.5mm recess front face        Remove Box
F6  Radiating ribs (8) 10.84mm×4mm, Y=0→-5           Add Box
F7  Cross-rib (1)      144mm×6mm×5mm, Y=0→-5         Add Box
F8  Wiring chans (2)   6mm×4mm deep, rear face        Remove Box
F9  SR bumps (4)       1.5mm tall×2mm, chan floor     Add Cyl
F10 Snap notches (2)   1.5×3mm, rear lateral          Remove Box
F11 Chamfers           perimeter 1.5mm, EF 0.3mm      Remove
F12 Fillets            plan corners 3mm, boss 1.5mm   Modify

COORDINATE SYSTEM (Rubric 2)
==============================
Origin: front-face bottom-left corner (X=0, Y=0, Z=0)
X: [0, 144]  width left→right
Y: [-5, 10]  ribs→front face→rear face→boss tips
Z: [0, 80]   height bottom→top
""")

# ==============================================================================
# Helper: cylinder cut along Y-axis
# A cylinder whose axis runs along world Y, centered at (cx, cz) in XZ,
# from Y=y_start to Y=y_end (y_end > y_start means going in +Y direction).
# We place the cut workplane at max Y, extrude in -Y direction.
# ==============================================================================
def make_y_cylinder(cx, cz, radius, y_start, y_end):
    """Return a CQ solid: cylinder at (cx, *, cz) from Y=y_start to Y=y_end."""
    depth = y_end - y_start
    # Place workplane at y_end, extrude depth in -Y direction
    cyl = (
        cq.Workplane("XZ")
        .workplane(offset=-y_end)       # plane at world Y = y_end
        .center(cx, cz)
        .circle(radius)
        .extrude(depth)                 # +depth → -Y direction → from Y=y_end to Y=y_start
    )
    return cyl

# ==============================================================================
# STEP 1 — Base plate with plan-view corner radii
# box(PLATE_W, PLATE_D, PLATE_H) on XY workplane with centered=False:
#   X:[0,144], Y:[0,5], Z:[0,80]
# Corner radii on edges parallel to Y ("|Y" selector)
# ==============================================================================
print("Step 1: Building base plate with corner radii...")
plate = (
    cq.Workplane("XY")
    .box(PLATE_W, PLATE_D, PLATE_H, centered=False)
)
plate = plate.edges("|Y").fillet(CORNER_R)
print(f"  Base plate: {PLATE_W}×{PLATE_D}×{PLATE_H}mm, {CORNER_R}mm corner fillets on |Y edges")

# ==============================================================================
# STEP 2 — Motor bores (D=37.2, Y=0→5, through-cut along Y-axis)
# ==============================================================================
print("Step 2: Cutting motor bores...")
for (bx, bz) in [(BORE1_X, BORE1_Z), (BORE2_X, BORE2_Z)]:
    cyl = make_y_cylinder(bx, bz, BORE_R, 0.0, PLATE_D)
    plate = plate.cut(cyl)
print(f"  Motor bores D={BORE_D}mm at ({BORE1_X},{BORE1_Z}) and ({BORE2_X},{BORE2_Z})")

# ==============================================================================
# STEP 3 — M3 clearance holes through plate (D=3.6mm, Y=0→5.5)
# Cut now from Y=0 through plate (Y=5). The extra 0.5mm (Y=5→5.5) will be
# cut again after bosses are added (step 5d). Cutting 5.5mm now means we
# cut 0.5mm below Y=0 which is harmless (no material there yet).
# ==============================================================================
print("Step 3: Cutting M3 clearance holes through plate...")
for (hx, hz) in BOSS_POSITIONS:
    # Cut from Y=0 to Y=5.5 (5.5mm depth starting at Y=0, going +Y)
    # Place at Y=5.5, extrude 5.5mm in -Y → Y=5.5 to Y=0
    cyl = make_y_cylinder(hx, hz, CLEAR_R, 0.0, 5.5)
    plate = plate.cut(cyl)
print(f"  {len(BOSS_POSITIONS)} clearance holes D={CLEAR_D}mm (Y=0→5.5 intended; boss floor re-cut later)")

# ==============================================================================
# STEP 4 — Field zone step (0.5mm recess on front face outside mounting pad zones)
# Field zone = everything on front face (Y=0) outside:
#   Pad 1: X=0→71.5, Z=3→77
#   Pad 2: X=72.5→144, Z=3→77
#   Cross-rib band: X=69→75, Z=37→43 (covers the gap between pads)
# Field zone regions to cut (0.5mm deep into plate, from Y=0→+0.5):
#   A: X=0→144, Z=0→3    (bottom strip)
#   B: X=0→144, Z=77→80  (top strip)
#   C: X=71.5→72.5, Z=3→37   (gap below cross-rib band)
#   D: X=71.5→72.5, Z=43→77  (gap above cross-rib band)
# ==============================================================================
print("Step 4: Cutting field zone step...")
field_cuts = [
    (0.0,   144.0,  0.0,  3.0),
    (0.0,   144.0, 77.0, 80.0),
    (71.5,   72.5,  3.0, 37.0),
    (71.5,   72.5, 43.0, 77.0),
]
for (x0, x1, z0, z1) in field_cuts:
    lx = x1 - x0
    lz = z1 - z0
    if lx <= 0 or lz <= 0:
        continue
    # Box: X:[x0,x1], Y:[0,0.5], Z:[z0,z1]
    # XY workplane box(lx, FIELD_STEP, lz) at origin → translate to position
    pocket = (
        cq.Workplane("XY")
        .box(lx, FIELD_STEP, lz, centered=False)
        .translate((x0, 0.0, z0))
    )
    plate = plate.cut(pocket)
print("  Field zone step cut (0.5mm recess, 4 regions)")

# ==============================================================================
# STEP 5a — Add boss cylinders (OD=9mm, Y=5→10)
# ==============================================================================
print("Step 5a: Adding boss cylinders...")
for (hx, hz) in BOSS_POSITIONS:
    boss = make_y_cylinder(hx, hz, BOSS_R, BOSS_Y0, BOSS_Y1)
    plate = plate.union(boss)
print(f"  {len(BOSS_POSITIONS)} bosses OD={BOSS_OD}mm, Y={BOSS_Y0}→{BOSS_Y1}")

# ==============================================================================
# STEP 5b — Boss base fillets (1.5mm at boss OD meets Y=5 rear face)
# Select circular edges at Y=5 (boss base circles).
# CadQuery string selector: we use a LambdaSelector approach.
# ==============================================================================
print("Step 5b: Boss base fillets...")
try:
    # Select edges that are circles (non-linear, closed) at Y≈5
    # near boss centers. Use LambdaSelector from cadquery.selectors.
    from cadquery import selectors as sel

    class BossBaseEdgeSelector(sel.Selector):
        def filter(self, object_list):
            result = []
            for e in object_list:
                start = e.startPoint()
                end   = e.endPoint()
                y_s = start.y; y_e = end.y
                y_mid = (y_s + y_e) / 2.0
                # Must be near Y=5 (boss base)
                if abs(y_mid - BOSS_Y0) > 0.3:
                    continue
                # Must be near a boss center XZ
                x_mid = (start.x + end.x) / 2.0
                z_mid = (start.z + end.z) / 2.0
                for (bx, bz) in BOSS_POSITIONS:
                    if math.sqrt((x_mid-bx)**2 + (z_mid-bz)**2) < BOSS_R + 1.0:
                        result.append(e)
                        break
            return result

    plate = plate.edges(BossBaseEdgeSelector()).fillet(BOSS_FILLET)
    print(f"  Boss base fillets {BOSS_FILLET}mm applied")
except Exception as ex:
    print(f"  WARNING: Boss base fillet failed ({ex}), continuing")

# ==============================================================================
# STEP 5c — Cut insert bores (D=4.7mm, Y=5.5→10, opens at boss tip Y=10)
# ==============================================================================
print("Step 5c: Cutting insert bores...")
for (hx, hz) in BOSS_POSITIONS:
    cyl = make_y_cylinder(hx, hz, INSERT_R, 5.5, BOSS_Y1)
    plate = plate.cut(cyl)
print(f"  Insert bores D={INSERT_D}mm, Y=5.5→{BOSS_Y1}")

# ==============================================================================
# STEP 5d — Re-cut clearance holes through boss floor (Y=5.0→5.5)
# After boss union, material exists at Y=5→5.5 (boss floor).
# Cut 3.6mm clearance hole through that 0.5mm layer.
# ==============================================================================
print("Step 5d: Re-cutting clearance holes through boss floor (Y=5.0→5.5)...")
for (hx, hz) in BOSS_POSITIONS:
    cyl = make_y_cylinder(hx, hz, CLEAR_R, PLATE_D, CLEAR_Y_END)
    plate = plate.cut(cyl)
print("  Boss floor clearance hole extension cut")

# ==============================================================================
# STEP 6 — Cross-rib (X=0→144, Z=37→43, Y=0→-5)
# Box on XZ workplane: protrudes in -Y from front face
# ==============================================================================
print("Step 6: Adding cross-rib...")
# XY workplane: box(PLATE_W, CROSSRIB_Y_PROTRUDE, CROSSRIB_H, centered=False)
# But this would go in Y direction. We need it to go in -Y from Y=0.
# Build the box using translate: the rib is a box
#   X:[0,144], Y:[-5,0], Z:[37,43]
# Use XY workplane, box(144, 5, 6), translate to (0, -5, 37)
# XY workplane box(L, W, H): L=X, W=Y, H=Z
crossrib = (
    cq.Workplane("XY")
    .box(PLATE_W, CROSSRIB_Y_PROTRUDE, CROSSRIB_H, centered=False)
    .translate((0.0, -CROSSRIB_Y_PROTRUDE, CROSSRIB_Z0))
)
# Result: X:[0,144], Y:[-5,0], Z:[37,43] ✓
plate = plate.union(crossrib)

# Crown chamfer at Y=-5 (crown face)
try:
    from cadquery import selectors as sel

    class YMinFaceEdges(sel.Selector):
        def __init__(self, y_val, tol=0.3):
            self.y_val = y_val
            self.tol = tol
        def filter(self, object_list):
            result = []
            for e in object_list:
                y_mid = (e.startPoint().y + e.endPoint().y) / 2.0
                if abs(y_mid - self.y_val) < self.tol:
                    result.append(e)
            return result

    plate = plate.edges(YMinFaceEdges(-CROSSRIB_Y_PROTRUDE)).chamfer(CROSSRIB_CHAMFER)
    print(f"  Cross-rib crown chamfer {CROSSRIB_CHAMFER}mm at Y=-5")
except Exception as ex:
    print(f"  WARNING: Cross-rib crown chamfer failed ({ex}), continuing")

# Rib base fillet at Y=0
try:
    class CrossribBaseEdges(sel.Selector):
        """Edges at Y=0 within the cross-rib Z range."""
        def filter(self, object_list):
            result = []
            for e in object_list:
                y_mid = (e.startPoint().y + e.endPoint().y) / 2.0
                if abs(y_mid) > 0.2:
                    continue
                z_mid = (e.startPoint().z + e.endPoint().z) / 2.0
                if CROSSRIB_Z0 - 0.5 < z_mid < CROSSRIB_Z1 + 0.5:
                    result.append(e)
            return result

    plate = plate.edges(CrossribBaseEdges()).fillet(CROSSRIB_FILLET)
    print(f"  Cross-rib base fillet {CROSSRIB_FILLET}mm at Y=0")
except Exception as ex:
    print(f"  WARNING: Cross-rib base fillet failed ({ex}), continuing")

print("  Cross-rib added")

# ==============================================================================
# STEP 7 — Radiating ribs (8×)
# Each rib: 4mm wide × 5mm tall (-Y protrusion) × ~10.84mm long
# Oriented along boss→bore vector in XZ plane.
# Build as box translated and rotated to correct position.
# ==============================================================================
print("Step 7: Adding radiating ribs...")

def boss_to_bore(hx):
    """Return bore center for a given boss X."""
    return (BORE1_X, BORE1_Z) if hx < 72.0 else (BORE2_X, BORE2_Z)

for i, (hx, hz) in enumerate(BOSS_POSITIONS):
    bx, bz = boss_to_bore(hx)
    dx = bx - hx;  dz = bz - hz
    dist = math.sqrt(dx*dx + dz*dz)
    ux, uz = dx/dist, dz/dist

    # Rib endpoints in XZ plane
    r_start_x = hx + ux * BOSS_R
    r_start_z = hz + uz * BOSS_R
    r_end_x   = bx - ux * BORE_R
    r_end_z   = bz - uz * BORE_R
    rib_cx    = (r_start_x + r_end_x) / 2
    rib_cz    = (r_start_z + r_end_z) / 2
    rib_len   = math.sqrt((r_end_x-r_start_x)**2 + (r_end_z-r_start_z)**2)

    # Angle of long axis relative to X axis (in XZ plane)
    # atan2(z, x) gives angle of vector in XZ plane
    angle_deg = math.degrees(math.atan2(uz, ux))

    # Build rib: box of size (rib_len × RIB_WIDTH × RIB_Y_PROTRUDE) in XZ workplane
    # In XZ workplane: box(L_x, L_z, L_y) → L_x along X, L_z along Z, L_y along -Y
    # Center it at (rib_cx, rib_cz) after rotation
    # Use: create centered box at origin, then transform
    # XZ workplane box(rib_len, RIB_WIDTH, RIB_Y_PROTRUDE, centered=True):
    #   centered box: X:[-rib_len/2, rib_len/2], Z:[-RIB_WIDTH/2, RIB_WIDTH/2], Y:[0, -5]
    # Rotate around Y-axis by angle_deg, then translate to (rib_cx, 0, rib_cz)
    rib = (
        cq.Workplane("XZ")
        .workplane(offset=0.0)   # at Y=0 (front face)
        .transformed(rotate=cq.Vector(0, angle_deg, 0))
        .center(rib_cx, rib_cz)
        .rect(rib_len, RIB_WIDTH)
        .extrude(RIB_Y_PROTRUDE)   # → -Y direction ✓
    )
    plate = plate.union(rib)

# Crown chamfers on rib crowns (at Y = -RIB_Y_PROTRUDE = -5)
try:
    plate = plate.edges(YMinFaceEdges(-RIB_Y_PROTRUDE, tol=0.4)).chamfer(RIB_CHAMFER)
    print(f"  Rib crown chamfers {RIB_CHAMFER}mm at Y=-5")
except Exception as ex:
    print(f"  WARNING: Rib crown chamfer failed ({ex}), continuing")

# Rib base fillets at Y=0
try:
    class RibBaseEdges(sel.Selector):
        """Edges at Y=0 NOT within cross-rib Z range."""
        def filter(self, object_list):
            result = []
            for e in object_list:
                y_mid = (e.startPoint().y + e.endPoint().y) / 2.0
                if abs(y_mid) > 0.3:
                    continue
                z_mid = (e.startPoint().z + e.endPoint().z) / 2.0
                # Exclude cross-rib zone already filletted
                if CROSSRIB_Z0 - 0.5 < z_mid < CROSSRIB_Z1 + 0.5:
                    continue
                result.append(e)
            return result

    plate = plate.edges(RibBaseEdges()).fillet(RIB_FILLET)
    print(f"  Rib base fillets {RIB_FILLET}mm at Y=0")
except Exception as ex:
    print(f"  WARNING: Rib base fillet failed ({ex}), continuing")

print(f"  {len(BOSS_POSITIONS)} radiating ribs added")

# ==============================================================================
# STEP 8 — Wiring channels and strain-relief bumps
# ==============================================================================
print("Step 8: Cutting wiring channels...")
# Channel 1: X:[0,15.9], Y:[1,5], Z:[37,43]
# Channel 2: X:[128.1,144], Y:[1,5], Z:[37,43]
# Cut as box: lx × CHAN_DEPTH × CHAN_W, translated to position
for (cx0, cx1) in [(CHAN1_X0, CHAN1_X1), (CHAN2_X0, CHAN2_X1)]:
    lx = cx1 - cx0
    chan = (
        cq.Workplane("XY")
        .box(lx, CHAN_DEPTH, CHAN_W, centered=False)
        .translate((cx0, CHAN_FLOOR_Y, CHAN_Z0))
    )
    # box(lx, CHAN_DEPTH, CHAN_W): X:[0,lx], Y:[0,4], Z:[0,6]
    # translate: X:[cx0,cx1], Y:[1,5], Z:[37,43] ✓
    plate = plate.cut(chan)

# Channel interior corner fillets
try:
    class ChannelFloorEdges(sel.Selector):
        """Edges at the channel floor Y=1, within channel Z range."""
        def filter(self, object_list):
            result = []
            for e in object_list:
                y_mid = (e.startPoint().y + e.endPoint().y) / 2.0
                if abs(y_mid - CHAN_FLOOR_Y) > 0.2:
                    continue
                z_mid = (e.startPoint().z + e.endPoint().z) / 2.0
                if CHAN_Z0 - 0.2 < z_mid < CHAN_Z1 + 0.2:
                    result.append(e)
            return result

    plate = plate.edges(ChannelFloorEdges()).fillet(CHAN_FILLET_R)
    print(f"  Channel interior corner fillets {CHAN_FILLET_R}mm")
except Exception as ex:
    print(f"  WARNING: Channel corner fillet failed ({ex}), continuing")

print("  Wiring channels cut")

# Strain-relief bumps
print("Step 8b: Adding strain-relief bumps...")
for (bx, bz) in BUMP_POSITIONS:
    # Bump: cylinder R=1mm, from Y=1 down to Y=-0.5 (protrudes -Y from channel floor)
    bump = make_y_cylinder(bx, bz, BUMP_R, -0.5, CHAN_FLOOR_Y)
    # make_y_cylinder places at (bx, *, bz), Y=−0.5 → Y=1 ✓
    plate = plate.union(bump)
print(f"  {len(BUMP_POSITIONS)} strain-relief bumps added")

# ==============================================================================
# STEP 9 — Snap notches (2×)
# Left: X:[0,1.5], Y:[2,5], Z:[38.5,41.5]
# Right: X:[142.5,144], Y:[2,5], Z:[38.5,41.5]
# ==============================================================================
print("Step 9: Cutting snap notches...")
notch_y_depth = NOTCH_Y1 - NOTCH_Y0    # 3mm
for (x0) in [0.0, PLATE_W - NOTCH_DEPTH]:
    notch = (
        cq.Workplane("XY")
        .box(NOTCH_DEPTH, notch_y_depth, NOTCH_W, centered=False)
        .translate((x0, NOTCH_Y0, NOTCH_Z0))
    )
    # box: X:[x0, x0+1.5], Y:[2,5], Z:[38.5,41.5] ✓
    plate = plate.cut(notch)
print("  Snap notches cut")

# ==============================================================================
# STEP 10 — Perimeter chamfers
# ==============================================================================
print("Step 10: Applying perimeter chamfers...")

# 10a — Rear bore entry chamfer (0.5mm at bore rim at Y=5)
try:
    class BoreRimEdges(sel.Selector):
        """Circular edges at Y=5 (rear face) near bore centers."""
        def filter(self, object_list):
            result = []
            for e in object_list:
                y_mid = (e.startPoint().y + e.endPoint().y) / 2.0
                if abs(y_mid - PLATE_D) > 0.3:
                    continue
                x_mid = (e.startPoint().x + e.endPoint().x) / 2.0
                z_mid = (e.startPoint().z + e.endPoint().z) / 2.0
                for (bx, bz) in [(BORE1_X, BORE1_Z), (BORE2_X, BORE2_Z)]:
                    d = math.sqrt((x_mid-bx)**2 + (z_mid-bz)**2)
                    if d < BORE_R + 1.0:
                        result.append(e)
                        break
            return result

    plate = plate.edges(BoreRimEdges()).chamfer(BORE_CHAMFER)
    print(f"  Bore rim chamfers {BORE_CHAMFER}mm at Y=5")
except Exception as ex:
    print(f"  WARNING: Bore rim chamfer failed ({ex}), continuing")

# 10b — Elephant's foot chamfer (0.3mm at Z=0, Y=0 edge)
try:
    class ElephantFootEdge(sel.Selector):
        """The build-plate bottom-front edge: Z≈0, Y≈0."""
        def filter(self, object_list):
            result = []
            for e in object_list:
                y_mid = (e.startPoint().y + e.endPoint().y) / 2.0
                z_mid = (e.startPoint().z + e.endPoint().z) / 2.0
                if abs(y_mid) < 0.3 and abs(z_mid) < 0.3:
                    result.append(e)
            return result

    plate = plate.edges(ElephantFootEdge()).chamfer(CHAMFER_ELEPHANT)
    print(f"  Elephant's foot chamfer {CHAMFER_ELEPHANT}mm at Z=0,Y=0")
except Exception as ex:
    print(f"  WARNING: Elephant's foot chamfer failed ({ex}), continuing")

# 10c — Perimeter chamfers (1.5mm)
# Target edges (all on perimeter of the plate body):
#   Top edges at Z=80 (at Y=0 and Y=5 faces)
#   Bottom rear edge at Z=0, Y=5
#   Left lateral edges at X=0 (at Y=0 and Y=5 faces, full Z)
#   Right lateral edges at X=144 (at Y=0 and Y=5 faces, full Z)
try:
    class PerimeterChamferEdges(sel.Selector):
        def filter(self, object_list):
            result = []
            for e in object_list:
                x_s, y_s, z_s = e.startPoint().x, e.startPoint().y, e.startPoint().z
                x_e, y_e, z_e = e.endPoint().x,   e.endPoint().y,   e.endPoint().z
                x_mid = (x_s+x_e)/2; y_mid = (y_s+y_e)/2; z_mid = (z_s+z_e)/2

                # Top edges at Z=PLATE_H on front or rear face
                if abs(z_mid - PLATE_H) < 0.3:
                    if abs(y_mid) < 0.3 or abs(y_mid - PLATE_D) < 0.3:
                        result.append(e); continue

                # Bottom rear edge: Z≈0, Y≈PLATE_D
                if abs(z_mid) < 0.3 and abs(y_mid - PLATE_D) < 0.3:
                    result.append(e); continue

                # Left lateral edges at X=0
                if abs(x_mid) < 0.3:
                    if abs(y_mid) < 0.3 or abs(y_mid - PLATE_D) < 0.3:
                        result.append(e); continue

                # Right lateral edges at X=PLATE_W
                if abs(x_mid - PLATE_W) < 0.3:
                    if abs(y_mid) < 0.3 or abs(y_mid - PLATE_D) < 0.3:
                        result.append(e); continue

            return result

    plate = plate.edges(PerimeterChamferEdges()).chamfer(CHAMFER_PERIMETER)
    print(f"  Perimeter chamfers {CHAMFER_PERIMETER}mm applied")
except Exception as ex:
    print(f"  WARNING: Perimeter chamfer failed ({ex}), continuing")

print("\nModel geometry complete.")

# ==============================================================================
# RUBRIC 3 — Feature-Specification Reconciliation
# ==============================================================================
print("\n" + "="*60)
print("RUBRIC 3 — FEATURE-SPECIFICATION RECONCILIATION")
print("="*60)

v = Validator(plate)

# F1 — Plate body
print("\n[F1] Plate body")
v.check_solid("F1 center",      72.0,  2.5, 40.0, "solid at plate center")
v.check_solid("F1 left",         5.0,  2.5, 40.0, "solid at left side")
v.check_solid("F1 right",      139.0,  2.5, 40.0, "solid at right side")
v.check_solid("F1 bottom",      72.0,  2.5,  5.0, "solid near bottom edge")
v.check_solid("F1 top",         72.0,  2.5, 75.0, "solid near top edge")
# Corner fillets: corners should be void
v.check_void("F1 corner BL",    0.5,   2.5,  0.5, "void inside BL corner (fillet arc)")
v.check_void("F1 corner BR",  143.5,   2.5,  0.5, "void inside BR corner")
v.check_void("F1 corner TL",    0.5,   2.5, 79.5, "void inside TL corner")
v.check_void("F1 corner TR",  143.5,   2.5, 79.5, "void inside TR corner")

# F2 — Motor bores
print("\n[F2] Motor bores")
v.check_void("F2 bore1 Y=1",   BORE1_X,  1.0, BORE1_Z, "void bore1 center near front")
v.check_void("F2 bore1 Y=4",   BORE1_X,  4.0, BORE1_Z, "void bore1 center near rear")
v.check_void("F2 bore2 Y=2.5", BORE2_X,  2.5, BORE2_Z, "void bore2 center mid-depth")
v.check_solid("F2 bore1 wall+", BORE1_X + BORE_R + 1.0, 2.5, BORE1_Z, "solid outside bore1 (+X)")
v.check_solid("F2 bore1 wall-", BORE1_X - BORE_R - 1.0, 2.5, BORE1_Z, "solid outside bore1 (-X)")
v.check_solid("F2 bore2 wall+", BORE2_X + BORE_R + 1.0, 2.5, BORE2_Z, "solid outside bore2 (+X)")

# F3 — M3 clearance holes
print("\n[F3] M3 clearance holes")
for n, (hx, hz) in enumerate(BOSS_POSITIONS):
    v.check_void(f"F3 hole{n+1} mid",   hx, 2.5, hz, f"void hole {n+1} mid-plate")
    v.check_void(f"F3 hole{n+1} front", hx, 0.5, hz, f"void hole {n+1} near Y=0")

# F3/F4 — PATH CONTINUITY PROBES (MANDATORY Rubric 3, point 5)
# 2 probes per fastener × 8 fasteners = 16 mandatory probes
print("\n[F3/F4] Path continuity at Y=5.5 transition (MANDATORY 16 probes)")
for n, (hx, hz) in enumerate(BOSS_POSITIONS):
    v.check_void(f"Path {n+1} transition below", hx, 5.4, hz,
                 "void just below Y=5.5 — clearance hole reaches transition")
    v.check_void(f"Path {n+1} transition above", hx, 5.6, hz,
                 "void just above Y=5.5 — insert bore reaches transition")

# F4 — Boss cylinders and insert bores
print("\n[F4] Bosses and insert bores")
for n, (hx, hz) in enumerate(BOSS_POSITIONS):
    mid_wall_r = (BOSS_R + INSERT_R) / 2     # ~3.425 (between boss OD and insert bore)
    v.check_solid(f"F4 boss{n+1} wall",   hx + mid_wall_r, 7.5, hz, f"solid in boss wall")
    v.check_void(f"F4 insert{n+1} Y7.5",  hx, 7.5, hz,   f"void in insert bore mid-height")
    v.check_void(f"F4 insert{n+1} Y9.5",  hx, 9.5, hz,   f"void in insert bore near tip")
# Boss floor (annular ring at Y=5.5) should have boss wall material
v.check_solid("F4 boss floor annular", BOSS_POSITIONS[0][0] + INSERT_R + 0.2, 5.3, BOSS_POSITIONS[0][1],
              "solid in annular ring at boss floor (between clearance hole and insert bore)")

# F5 — Field zone step
print("\n[F5] Field zone step")
v.check_void("F5 bottom strip",  72.0,  0.25,  1.5, "void at field zone Y=0→0.5 (bottom strip)")
v.check_void("F5 top strip",     72.0,  0.25, 78.5, "void at field zone Y=0→0.5 (top strip)")
v.check_void("F5 center gap",    72.0,  0.25, 50.0, "void at center gap field zone")
v.check_solid("F5 pad1 near Y0", 35.0,  0.1,  40.0, "solid at mounting pad 1 surface (Y≈0)")
v.check_solid("F5 pad2 near Y0",110.0,  0.1,  40.0, "solid at mounting pad 2 surface (Y≈0)")
v.check_solid("F5 field depth",  72.0,  0.75,  1.5, "solid below field zone floor (Y=0.75)")

# F6 — Radiating ribs
print("\n[F6] Radiating ribs")
for n, (hx, hz) in enumerate(BOSS_POSITIONS):
    bx, bz = boss_to_bore(hx)
    dx = bx - hx; dz = bz - hz; dist = math.sqrt(dx*dx + dz*dz)
    ux, uz = dx/dist, dz/dist
    r_start_x = hx + ux * BOSS_R;  r_start_z = hz + uz * BOSS_R
    r_end_x   = bx - ux * BORE_R;  r_end_z   = bz - uz * BORE_R
    rib_cx = (r_start_x + r_end_x) / 2
    rib_cz = (r_start_z + r_end_z) / 2
    v.check_solid(f"F6 rib{n+1} mid", rib_cx, -2.5, rib_cz, f"solid rib {n+1} midpoint Y=-2.5")

# F7 — Cross-rib
print("\n[F7] Cross-rib")
v.check_solid("F7 rib left",    10.0, -2.5, 40.0, "solid cross-rib left zone")
v.check_solid("F7 rib center",  72.0, -2.5, 40.0, "solid cross-rib center")
v.check_solid("F7 rib right",  134.0, -2.5, 40.0, "solid cross-rib right zone")
v.check_void("F7 above rib",    72.0, -2.5, 44.0, "void above cross-rib (Z=44)")
v.check_void("F7 below rib",    72.0, -2.5, 36.0, "void below cross-rib (Z=36)")
v.check_void("F7 beyond tip",   72.0, -5.5, 40.0, "void beyond cross-rib tip (Y=-5.5)")

# F8 — Wiring channels
print("\n[F8] Wiring channels")
v.check_void("F8 chan1 mid",     8.0,  3.0, 40.0, "void channel 1 mid (X=8, Y=3, Z=40)")
v.check_void("F8 chan1 Y4.5",    8.0,  4.5, 40.0, "void channel 1 near rear face (Y=4.5)")
v.check_solid("F8 chan1 floor",  8.0,  0.5, 40.0, "solid below channel 1 floor (Y=0.5)")
v.check_void("F8 chan2 mid",   136.0,  3.0, 40.0, "void channel 2 mid")
v.check_solid("F8 chan2 floor",136.0,  0.5, 40.0, "solid below channel 2 floor")
v.check_solid("F8 chan1 wall Z+", 8.0, 3.0, 44.0, "solid outside channel 1 Z range (Z=44)")
v.check_solid("F8 chan2 wall Z-",136.0,3.0, 36.0, "solid outside channel 2 Z range (Z=36)")

# F9 — Strain-relief bumps
print("\n[F9] Strain-relief bumps")
for n, (bx, bz) in enumerate(BUMP_POSITIONS):
    v.check_solid(f"F9 bump{n+1}",  bx, -0.2, bz, f"solid at bump {n+1} near crown (Y=-0.2)")

# F10 — Snap notches
print("\n[F10] Snap notches")
v.check_void("F10 notch L",    0.75,  3.5, 40.0, "void inside left snap notch")
v.check_void("F10 notch R",  143.25,  3.5, 40.0, "void inside right snap notch")
v.check_solid("F10 notch L out Z", 0.75, 3.5, 43.0, "solid outside left notch (Z=43)")
v.check_solid("F10 notch R out Z",143.25,3.5, 37.0, "solid outside right notch (Z=37)")
v.check_solid("F10 notch L out Y", 0.75, 1.5, 40.0, "solid below left notch Y range (Y=1.5)")

# Rubric 4 — Solid validity
print("\n[Rubric 4] Solid validity")
v.check_valid()
v.check_single_body()
v.check_volume(expected_envelope=PLATE_W * PLATE_D * PLATE_H,
               fill_range=(0.5, 2.5))  # includes boss + rib protrusions

# Rubric 5 — Bounding box
print("\n[Rubric 5] Bounding box")
bb = plate.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, 0.0, PLATE_W, tol=0.6)
v.check_bbox("Y", bb.ymin, bb.ymax, -CROSSRIB_Y_PROTRUDE, BOSS_Y1, tol=1.0)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, PLATE_H, tol=0.6)

# Summary
print()
passed = v.summary()
if not passed:
    print("\nFAILURES DETECTED — not exporting")
    sys.exit(1)

# ==============================================================================
# Export STEP
# ==============================================================================
output_path = Path(__file__).resolve().parent / "pump-tray-cadquery.step"
cq.exporters.export(plate, str(output_path))
print(f"\nSTEP exported: {output_path}")
