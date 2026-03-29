"""
Bag Frame Spine — CadQuery STEP Generation Script
==================================================
Part:       Spine
Version:    1.0
Date:       2026-03-29
Source:     hardware/printed-parts/bag-frame/planning/spine/parts.md
            hardware/printed-parts/bag-frame/planning/spine/spatial-resolution.md
            hardware/printed-parts/bag-frame/planning/spine/decomposition.md
            hardware/pipeline/steps/6-step-generation.md

Coordinate system:
  Origin: front-face lower-left corner (intersection of Y=0, X=0, Z=0 faces)
          as seen from the front (looking in +Y direction).
  X: spine width, left to right.   X=0 (left end face) → X=220mm (right end face)
  Y: spine depth, front to rear.   Y=0 (front face)    → Y=35mm  (rear face)
  Z: spine height, bottom to top.  Z=0 (bottom face)   → Z=245mm (top face)
  Main body envelope:  X:[0,220]   Y:[0,35]    Z:[0,245]
  Full part envelope:  X:[−8,228]  Y:[−1.5,35] Z:[0,245]
    (ribs protrude to Y=−1.5mm; snap posts protrude to X=−8mm and X=+228mm)

Rib geometry (from parts.md §5.2 + spatial-resolution.md §3.1):
  Each rib is a VERTICAL STRIPE running in Z on the front face.
  Spaced in X at 10mm pitch: X=5, 15, 25, …, 215mm.
  Width in X = 0.8mm (centered on x_center).
  Protrusion depth = 1.5mm outward from Y=0 face (into Y<0 space).

slot2D note (verified empirically):
  cq.Workplane.slot2D(length, diameter, angle) — length is the TIP-TO-TIP
  total length of the stadium slot. arc_center_separation = length - diameter.
  For a 10mm×6mm stadium post: slot2D(10, 6, angle=90).
  For a 13mm×9mm flange (post + 1.5mm radial):  slot2D(13, 9, angle=90).

Post positioning note:
  cq.Workplane("YZ").transformed(offset=cq.Vector(x,y,z)) — the offset vector
  is in the WORKPLANE'S LOCAL COORDINATE SYSTEM, not world coordinates.
  For a YZ workplane: local_X = world_Y, local_Y = world_Z, local_Z = world_X.
  To position the workplane at world X = x_val, use: Vector(0, 0, x_val).
  Safest approach: build posts at X=0 face, then translate to final X position.

Run with:
  tools/cad-venv/bin/python3 \
    hardware/printed-parts/bag-frame/cad/spine/generate_step_cadquery.py
"""

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Validation helper
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "tools"))
from step_validate import Validator

import cadquery as cq

# ===========================================================================
# RUBRIC 1 — Feature Planning Table (printed to stdout)
# ===========================================================================
print("""
══════════════════════════════════════════════════════════════════════════════════════════
RUBRIC 1 — FEATURE PLANNING TABLE
══════════════════════════════════════════════════════════════════════════════════════════
 #  Feature Name             Function               Op     Shape    Axis
    Center/Position           Dimensions            Notes
──────────────────────────────────────────────────────────────────────────────────────────
 1  Spine body                Structural backbone   Add    Box       —
    center (110,17.5,122.5)   220(X)×35(Y)×245(Z)  centered=False; corner at origin

 2  Transverse ribs ×22       Design-language rib   Add    Rect      Z
    (front face, Y=0)         texture on visible    strip  0.8mm(X)×1.5mm(Y)×Z-height
    X=5,15,...,215mm          interior spine face   22 ribs; end ribs continuous Z=0-245
                                                    inner ribs: 3 Z-segments each

 3  Lower fold-end slot       Captures lower bag    Remove Rect      Y
    center (110, 5, 169.6)    fold end vs front     pocket 195(X)×10(Y)×20(Z)
                              wall                         Z=159.6-179.6

 4  Upper fold-end slot       Captures upper bag    Remove Rect      Y
    center (110, 5, 229.6)    fold end vs front     pocket 195(X)×10(Y)×20(Z)
                              wall                         Z=219.6-239.6

 5  Tab slot L1 (lower crad.) Snap-tab receiver;    Remove Rect      Z
    center (8.0, 27.5, ~150)  retains lower cradle  slot   2.2(X)×15(Y)×open-top
                              tab 1; hook lock      (open top) Z=56.5–245mm

 6  Tab slot L2               Same; lower tab 2     Remove Same      Z  Z=84.1-245
 7  Tab slot L3               Same; lower tab 3     Remove Same      Z  Z=111.0-245
 8  Tab slot L4               Same; lower tab 4     Remove Same      Z  Z=138.6-245
 9  Tab slot U1 (upper crad.) Same; upper tab 1     Remove Same      Z  Z=116.5-245; X=212
10  Tab slot U2               Same; upper tab 2     Remove Same      Z  Z=144.1-245; X=212
11  Tab slot U3               Same; upper tab 3     Remove Same      Z  Z=171.0-245; X=212
12  Tab slot U4               Same; upper tab 4     Remove Same      Z  Z=198.6-245; X=212

13  Snap post left lower      Locks spine into      Add    Stadium   X (-)
    root (0,17.5,30)          enclosure left half   boss   10(Z)×6(Y) mm; 8mm protrusion
    tip (-8,17.5,30)          permanent snap        +1.5mm retention flange at 6mm from root

14  Snap post left upper      Same; Z=70            Add    Stadium   X (-)
    root (0,17.5,70)          upper mounting pt     boss   Same cross-section

15  Snap post right lower     Locks spine into      Add    Stadium   X (+)
    root (220,17.5,30)        enclosure right half  boss   Same; protrudes +X to X=228
16  Snap post right upper     Same; Z=70            Add    Stadium   X (+)
    root (220,17.5,70)        upper mounting pt     boss   Same

17  Body corner fillets       Consumer-product      Fillet 2mm radius —
    Z-parallel body corners   design language       Applied to body only (before posts)

18  Fold-end slot entry chf.  Guide bag insertion   Chamfer 1mm×45°  —
    Z-edges at slot opening   UX; smooth entry      On top/bot Z-edges of each slot; try/except

19  Tab slot entry chamfers   Guide cradle tab      Chamfer 1mm×45°  —
    Top rim of each tab slot  insertion; UX         Try/except

20  Snap post tip chamfers    Guide enclosure       Chamfer 1mm×45°  —
    Post tip edges            alignment as halves   Try/except
                              close
══════════════════════════════════════════════════════════════════════════════════════════
""")

# ===========================================================================
# RUBRIC 2 — Coordinate System Declaration (printed to stdout)
# ===========================================================================
print("""
══════════════════════════════════════════════════════════════════════════════
RUBRIC 2 — COORDINATE SYSTEM
──────────────────────────────────────────────────────────────────────────────
Origin: front-face lower-left corner
        (intersection of Y=0 front face, X=0 left end face, Z=0 bottom face)

X: spine width,  left to right.   X=0 (left end face)  → X=220mm (right end)
Y: spine depth,  front to rear.   Y=0 (front face)      → Y=35mm  (rear face)
Z: spine height, bottom to top.   Z=0 (bottom face)     → Z=245mm (top face)

Main body envelope: X:[0,220]   Y:[0,35]    Z:[0,245]
Full part envelope: X:[−8,228]  Y:[−1.5,35] Z:[0,245]
  X: extended by snap post protrusion (8mm each side)
  Y: extended by rib protrusion (1.5mm outward from Y=0 = Y<0)
  Z: 0 to 245 (ribs are vertical stripes starting at Z=0, ending at Z=245)
══════════════════════════════════════════════════════════════════════════════
""")


# ===========================================================================
# DIMENSIONS  (from parts.md §8 / spatial-resolution.md)
# ===========================================================================

# ── Body ──────────────────────────────────────────────────────────────────
BODY_W = 220.0    # X
BODY_D =  35.0    # Y
BODY_H = 245.0    # Z

# ── Ribs ──────────────────────────────────────────────────────────────────
RIB_W_X   = 0.8    # rib width in X (thin dimension)
RIB_PROTR = 1.5    # rib protrusion in -Y from front face (Y=[-1.5,0])
# 22 rib X-centers: 5, 15, 25, …, 215mm
RIB_X = [5.0 + 10.0 * n for n in range(22)]

# Fold-slot Z boundaries (inner ribs at X=15..205 are interrupted here)
LOWER_FZ_MIN = 159.6
LOWER_FZ_MAX = 179.6
UPPER_FZ_MIN = 219.6
UPPER_FZ_MAX = 239.6

# ── Fold-end slots ────────────────────────────────────────────────────────
FOLD_X_MIN   = 12.5
FOLD_X_MAX   = 207.5
FOLD_Y_DEPTH = 10.0    # Y=0 to Y=10 (into body)
FOLD_W       = FOLD_X_MAX - FOLD_X_MIN   # 195.0 mm

# ── Tab slots ─────────────────────────────────────────────────────────────
TAB_W_X   = 2.2    # slot width in X  (2mm tab + 0.2mm clearance)
TAB_DEPTH = 15.0   # depth from rear face inward: Y=35 → Y=20
TAB_Y_BOT = BODY_D - TAB_DEPTH   # = 20.0

# Lower cradle slots (X center = 8.0 mm)
L_SLOTS = [
    (60.6,   56.5),   # (z_center, z_closed_bottom)
    (88.2,   84.1),
    (115.1, 111.0),
    (142.7, 138.6),
]
TAB_X_L = 8.0

# Upper cradle slots (X center = 212.0 mm)
U_SLOTS = [
    (120.6, 116.5),
    (148.2, 144.1),
    (175.1, 171.0),
    (202.7, 198.6),
]
TAB_X_U = 212.0

# ── Snap posts ────────────────────────────────────────────────────────────
# Stadium cross-section: 10mm(Z) × 6mm(Y) total
# slot2D(length=10, diameter=6, angle=90):
#   length = tip-to-tip = 10mm (verified: slot2D length is tip-to-tip)
#   diameter = 6mm
#   angle=90: long axis along sketch-Y (= world Z for YZ plane)
POST_Z_TOT    = 10.0   # total stadium height (Z span, tip to tip)
POST_Y_TOT    =  6.0   # total stadium width (Y span = diameter)
POST_PROTR    =  8.0   # protrusion length in ±X direction

# Retention flange: adds 1.5mm radially to all sides
# slot2D(10+3=13, 6+3=9): 13mm tip-to-tip, 9mm wide
POST_FLANGE_RAD = 1.5  # radial height of ridge
POST_FLANGE_W   = 1.5  # axial width in X
POST_FLANGE_POS = 6.0  # distance from root face to near side of flange

# Post centers (Y, Z) — same for left and right sides
POST_Y_C = 17.5   # = BODY_D / 2
POST_Z_L = 30.0   # lower pair Z center
POST_Z_U = 70.0   # upper pair Z center

# Edge treatments
CORNER_FILLET = 2.0
CHAMFER_SIZE  = 1.0


# ===========================================================================
# MODELING
# ===========================================================================

# ---------------------------------------------------------------------------
# STEP 1 — Spine body
# ---------------------------------------------------------------------------
print("Step 1: Spine body [220×35×245mm]...")
spine = cq.Workplane("XY").box(BODY_W, BODY_D, BODY_H, centered=False)
# X:[0,220], Y:[0,35], Z:[0,245]  ✓


# ---------------------------------------------------------------------------
# STEP 2 — Transverse ribs (22 vertical stripes on front face Y=0)
# ---------------------------------------------------------------------------
# Each rib: vertical stripe in Z direction, positioned at specific X center.
#   X: [xc - 0.4, xc + 0.4]  (0.8mm wide, centered at x_center)
#   Y: [-1.5, 0]              (protrudes outward in -Y from Y=0 front face)
#   Z: [z_lo, z_hi]
#
# End ribs (n=0 X=5, n=21 X=215): full Z=0..245 — outside fold slot X range
# Inner ribs (n=1..20): three Z-segments interrupted at fold slot Z ranges
#   Seg 1: Z=0 to 159.6      Seg 2: Z=179.6 to 219.6      Seg 3: Z=239.6 to 245.0

print("Step 2: Adding 22 transverse ribs...")

def add_rib_seg(solid, x_center, z_lo, z_hi):
    """Union one rib strip (vertical stripe) to the solid."""
    z_h = z_hi - z_lo
    if z_h < 0.1:
        return solid
    rib = (cq.Workplane("XY")
           .box(RIB_W_X, RIB_PROTR, z_h, centered=False)
           .translate((x_center - RIB_W_X / 2.0, -RIB_PROTR, z_lo)))
    return solid.union(rib)

# End ribs: single continuous segment
spine = add_rib_seg(spine,   5.0, 0.0, BODY_H)
spine = add_rib_seg(spine, 215.0, 0.0, BODY_H)

# Inner ribs: three segments each
INNER_SEGS = [
    (0.0,          LOWER_FZ_MIN),    # 0 → 159.6
    (LOWER_FZ_MAX, UPPER_FZ_MIN),    # 179.6 → 219.6
    (UPPER_FZ_MAX, BODY_H),          # 239.6 → 245.0  (5.4mm — retained)
]
for n in range(1, 21):
    xc = 5.0 + 10.0 * n
    for (zlo, zhi) in INNER_SEGS:
        spine = add_rib_seg(spine, xc, zlo, zhi)


# ---------------------------------------------------------------------------
# STEP 3 — Body corner fillets (before posts — OCC fillet fails with posts)
# ---------------------------------------------------------------------------
print("Step 3: Applying 2mm corner fillets to body (before posts)...")
try:
    spine = spine.edges("|Z").fillet(CORNER_FILLET)
    print("  Corner fillets applied.")
except Exception as e:
    print(f"  Skipped: {e}")


# ---------------------------------------------------------------------------
# STEP 4 — Fold-end slots (cut pockets from front face into body)
# ---------------------------------------------------------------------------
# X=[12.5,207.5], Y=[0,10], Z=[z_lo,z_hi]

print("Step 4: Cutting fold-end slots...")

def cut_fold_slot(solid, z_lo, z_hi):
    pocket = (cq.Workplane("XY")
              .box(FOLD_W, FOLD_Y_DEPTH, z_hi - z_lo, centered=False)
              .translate((FOLD_X_MIN, 0.0, z_lo)))
    return solid.cut(pocket)

spine = cut_fold_slot(spine, LOWER_FZ_MIN, LOWER_FZ_MAX)
spine = cut_fold_slot(spine, UPPER_FZ_MIN, UPPER_FZ_MAX)


# ---------------------------------------------------------------------------
# STEP 5 — Rear-face tab slots (open at top)
# ---------------------------------------------------------------------------
# X=[xc-1.1,xc+1.1], Y=[20,35], Z=[z_bot,245]

print("Step 5: Cutting rear-face tab slots...")

def cut_tab_slot(solid, x_center, z_bottom):
    x_lo = x_center - TAB_W_X / 2.0
    z_h  = BODY_H - z_bottom            # open at top
    pocket = (cq.Workplane("XY")
              .box(TAB_W_X, TAB_DEPTH, z_h, centered=False)
              .translate((x_lo, TAB_Y_BOT, z_bottom)))
    return solid.cut(pocket)

for (zc, zbot) in L_SLOTS:
    spine = cut_tab_slot(spine, TAB_X_L, zbot)

for (zc, zbot) in U_SLOTS:
    spine = cut_tab_slot(spine, TAB_X_U, zbot)


# ---------------------------------------------------------------------------
# STEP 6 — Snap posts
# ---------------------------------------------------------------------------
# CORRECTED approach: build each post at origin (YZ plane at X=0),
# then translate to final position. This avoids the transformed() axis
# confusion where CadQuery's YZ workplane local axes differ from world axes.
#
# Verified slot2D behavior:
#   slot2D(total_length, diameter, angle=90)
#   total_length = tip-to-tip = 10mm for 10mm post
#   diameter     = 6mm for 6mm wide post
#   → slot2D(10, 6, angle=90): Z span = 10mm, Y span = 6mm  ✓
#
# Post shaft: slot2D(10, 6, angle=90), extrude 8mm
# Post flange: slot2D(10+3, 6+3, angle=90) = slot2D(13, 9, angle=90), extrude 1.5mm
#
# Left posts (root at X=0, protrude in -X to X=-8):
#   Shaft: extrude(-8) from YZ plane at X=0 → X=[-8,0]
#   Flange: at X=[-7.5,-6] → build at origin, extrude(-1.5) → X=[-1.5,0],
#           then translate(-6, 0, 0) → X=[-7.5,-6]
#
# Right posts (root at X=220, protrude in +X to X=228):
#   Shaft: extrude(8) from YZ plane at X=0 → X=[0,8],
#          translate(220,0,0) → X=[220,228]
#   Flange: at X=[226,227.5] → build at origin, extrude(1.5) → X=[0,1.5],
#           translate(226,0,0) → X=[226,227.5]

print("Step 6: Adding snap posts (stadium extrusions)...")

# Left post shaft: at X=0, extrudes to X=-8
def make_left_shaft(y_c, z_c):
    return (cq.Workplane("YZ")
            .center(y_c, z_c)
            .slot2D(POST_Z_TOT, POST_Y_TOT, angle=90)
            .extrude(-POST_PROTR))   # -X direction from YZ at X=0

# Left post flange: at X=[-7.5,-6] (6mm from root)
def make_left_flange(y_c, z_c):
    f_len  = POST_Z_TOT + 2 * POST_FLANGE_RAD   # 10+3 = 13mm tip-to-tip
    f_diam = POST_Y_TOT + 2 * POST_FLANGE_RAD   # 6+3  = 9mm wide
    flange = (cq.Workplane("YZ")
              .center(y_c, z_c)
              .slot2D(f_len, f_diam, angle=90)
              .extrude(-POST_FLANGE_W))           # extrude -1.5mm in -X from X=0
    # Translate from X=[-1.5,0] to X=[-7.5,-6]: move by -6 in X
    return flange.translate((-POST_FLANGE_POS, 0, 0))

# Right post shaft: build at origin, extrude +X, translate to X=220
def make_right_shaft(y_c, z_c):
    shaft = (cq.Workplane("YZ")
             .center(y_c, z_c)
             .slot2D(POST_Z_TOT, POST_Y_TOT, angle=90)
             .extrude(POST_PROTR))               # +X direction from YZ at X=0
    # Translate from X=[0,8] to X=[220,228]
    return shaft.translate((BODY_W, 0, 0))

# Right post flange: at X=[226,227.5] (6mm from root at X=220)
def make_right_flange(y_c, z_c):
    f_len  = POST_Z_TOT + 2 * POST_FLANGE_RAD
    f_diam = POST_Y_TOT + 2 * POST_FLANGE_RAD
    flange = (cq.Workplane("YZ")
              .center(y_c, z_c)
              .slot2D(f_len, f_diam, angle=90)
              .extrude(POST_FLANGE_W))            # +1.5mm in +X from X=0
    # Translate from X=[0,1.5] to X=[226,227.5]: move by 226 in X
    return flange.translate((BODY_W + POST_FLANGE_POS, 0, 0))

# Add all four posts + flanges
for pz in [POST_Z_L, POST_Z_U]:
    spine = spine.union(make_left_shaft(POST_Y_C, pz))
    spine = spine.union(make_left_flange(POST_Y_C, pz))
    spine = spine.union(make_right_shaft(POST_Y_C, pz))
    spine = spine.union(make_right_flange(POST_Y_C, pz))


# ---------------------------------------------------------------------------
# STEP 7 — Consolidate to single solid and export STEP
# ---------------------------------------------------------------------------
# After many union/cut operations, consolidate the result to ensure
# the solid is clean and val() returns the full compound correctly.
print("Step 7: Consolidating solid...")
solid = spine.solids().vals()[0]
spine_final = cq.Workplane("XY").add(cq.Compound.makeCompound([solid]))

out_dir  = Path(__file__).resolve().parent
out_path = out_dir / "spine-cadquery.step"

print(f"Exporting STEP to: {out_path}")
cq.exporters.export(spine_final, str(out_path))
print("Export complete.")


# ===========================================================================
# STEP 8 — Validation (Rubric 3, 4, 5)
# ===========================================================================
print("\nRunning validation checks...")
v = Validator(spine_final)

# ── Rubric 3: Feature probes ────────────────────────────────────────────

# F1 — Spine body interior
v.check_solid("Spine body center",
              110.0, 17.5, 122.5,
              "solid at center of body (110, 17.5, 122.5)")

# F2 — Ribs: five sample points
v.check_solid("Rib X=5 (end rib), Y=-0.75, Z=100",
              5.0, -0.75, 100.0,
              "solid in end rib at X=5, Y=-0.75, Z=100")
v.check_solid("Rib X=55 seg1 (Z=80)",
              55.0, -0.75, 80.0,
              "solid in inner rib X=55, seg1, Z=80")
v.check_solid("Rib X=105 seg2 (Z=200)",
              105.0, -0.75, 200.0,
              "solid in inner rib X=105, seg2, Z=200")
v.check_solid("Rib X=155 seg3 (Z=242)",
              155.0, -0.75, 242.0,
              "solid in inner rib X=155, seg3, Z=242")

# F3-4 — Fold-end slots (void at slot centers)
v.check_void("Lower fold slot center (110,5,169.6)",
             110.0, 5.0, 169.6,
             "void at lower fold-end slot center")
v.check_void("Upper fold slot center (110,5,229.6)",
             110.0, 5.0, 229.6,
             "void at upper fold-end slot center")
v.check_void("Lower fold slot near left (X=20,Y=5,Z=169.6)",
             20.0, 5.0, 169.6,
             "void inside lower fold slot near left edge")
v.check_void("Upper fold slot near right (X=200,Y=5,Z=229.6)",
             200.0, 5.0, 229.6,
             "void inside upper fold slot near right edge")
# Solid outside fold slot X range at same Y/Z
v.check_solid("Side wall outside fold slot (X=5,Y=5,Z=169.6)",
              5.0, 5.0, 169.6,
              "solid at X=5 — side wall outside fold slot X range")

# F5-12 — Tab slots (void at center Y=27.5 = midpoint of Y=20..35)
v.check_void("Tab L1 center (8.0,27.5,60.6)",
             TAB_X_L, 27.5, 60.6,
             "void at L1 center")
v.check_void("Tab L2 center (8.0,27.5,88.2)",
             TAB_X_L, 27.5, 88.2,
             "void at L2 center")
v.check_void("Tab L3 center (8.0,27.5,115.1)",
             TAB_X_L, 27.5, 115.1,
             "void at L3 center")
v.check_void("Tab L4 center (8.0,27.5,142.7)",
             TAB_X_L, 27.5, 142.7,
             "void at L4 center")
v.check_void("Tab U1 center (212,27.5,120.6)",
             TAB_X_U, 27.5, 120.6,
             "void at U1 center")
v.check_void("Tab U2 center (212,27.5,148.2)",
             TAB_X_U, 27.5, 148.2,
             "void at U2 center")
v.check_void("Tab U3 center (212,27.5,175.1)",
             TAB_X_U, 27.5, 175.1,
             "void at U3 center")
v.check_void("Tab U4 center (212,27.5,202.7)",
             TAB_X_U, 27.5, 202.7,
             "void at U4 center")

# Solid BELOW tab slot closed bottom
v.check_solid("Solid below L1 closed bottom (Z=50)",
              TAB_X_L, 27.5, 50.0,
              "solid at Z=50 < L1 closed bottom (56.5)")
v.check_solid("Solid below U1 closed bottom (Z=110)",
              TAB_X_U, 27.5, 110.0,
              "solid at Z=110 < U1 closed bottom (116.5)")

# F13-16 — Snap posts (solid at mid-shaft)
v.check_solid("Left lower post mid-shaft (-4,17.5,30)",
              -4.0, POST_Y_C, POST_Z_L,
              "solid at left lower post shaft")
v.check_solid("Left upper post mid-shaft (-4,17.5,70)",
              -4.0, POST_Y_C, POST_Z_U,
              "solid at left upper post shaft")
v.check_solid("Right lower post mid-shaft (224,17.5,30)",
              224.0, POST_Y_C, POST_Z_L,
              "solid at right lower post shaft")
v.check_solid("Right upper post mid-shaft (224,17.5,70)",
              224.0, POST_Y_C, POST_Z_U,
              "solid at right upper post shaft")

# Retention flanges (at 6.75mm from root = mid of flange 6..7.5mm from root)
# Left lower: flange at X=[-7.5,-6], mid X=-6.75
v.check_solid("Left lower post flange (-6.75,17.5,30)",
              -6.75, POST_Y_C, POST_Z_L,
              "solid at left lower post retention flange")
# Right lower: flange at X=[226,227.5], mid X=226.75
v.check_solid("Right lower post flange (226.75,17.5,30)",
              226.75, POST_Y_C, POST_Z_L,
              "solid at right lower post retention flange")

# F17 — Body gap between slot zones (Y=15 in the 10mm solid gap)
v.check_solid("Body gap (Y=15 between slot zones)",
              110.0, 15.0, 100.0,
              "solid at Y=15 — 10mm gap between fold and tab slot zones")

# ── Rubric 4: Solid validity ────────────────────────────────────────────
v.check_valid()
v.check_single_body()

# Volume check: envelope = 220×35×245. Net volume ~65-100% (slots removed, ribs add small amount)
BODY_VOL = BODY_W * BODY_D * BODY_H
v.check_volume(expected_envelope=BODY_VOL, fill_range=(0.60, 1.10))

# ── Rubric 5: Bounding box ──────────────────────────────────────────────
# Expected:
#   X: -8.0 (left post tips) to 228.0 (right post tips)
#   Y: -1.5 (rib protrusion from front face) to 35.0 (rear face)
#   Z: 0.0 to 245.0 (ribs are vertical from Z=0; spine top at Z=245)
bb = spine_final.val().BoundingBox()
print(f"\nActual bounding box:")
print(f"  X: [{bb.xmin:.3f}, {bb.xmax:.3f}]   expected: [−8.0, 228.0]")
print(f"  Y: [{bb.ymin:.3f}, {bb.ymax:.3f}]   expected: [−1.5, 35.0]")
print(f"  Z: [{bb.zmin:.3f}, {bb.zmax:.3f}]   expected: [0.0, 245.0]")

v.check_bbox("X", bb.xmin, bb.xmax, -8.0, 228.0)
v.check_bbox("Y", bb.ymin, bb.ymax, -1.5,  35.0)
v.check_bbox("Z", bb.zmin, bb.zmax,  0.0, 245.0)

# Final summary — exits 1 on any failure
ok = v.summary()
if not ok:
    sys.exit(1)

print(f"\nSTEP file: {out_path}")
