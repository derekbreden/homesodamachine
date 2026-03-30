"""
Coupler Tray v2 — CadQuery STEP Generation Script
Season 1, Phase 1, Item 4

Specification source: hardware/printed-parts/cartridge/coupler-tray/planning/parts.md
JG union geometry:    hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md

Rubric 2 — Coordinate System Declaration:
  Origin: plate bottom-left-front corner (X=0, Y=0, Z=0)
  X: plate width axis — left to right, 0..137.2mm
  Y: plate thickness axis — front face (Y=0) to back face of base (Y=3mm);
     bosses extend from Y=3 to Y=12.08mm
  Z: plate height axis — bottom to top, 0..68.6mm
  Bounding envelope: 137.2mm (X) × 12.08mm (Y) × 68.6mm (Z)

  Hole/boss axes are parallel to Y.
  Print orientation: Y=0 face down on build plate; holes and bosses become vertical cylinders.
"""

import sys
from pathlib import Path

# Add tools/ to sys.path for step_validate import
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq
from step_validate import Validator

# ---------------------------------------------------------------------------
# Rubric 1 — Feature Planning Table (printed to stdout)
# ---------------------------------------------------------------------------

FEATURE_TABLE = """
╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  COUPLER TRAY v2 — Feature Planning Table (Rubric 1)                                                                                   ║
╠═══╦══════════════════════╦══════════════════════════════════════════╦═══════════╦═════════╦══════╦══════════════════╦══════════════════╗
║ # ║ Feature Name         ║ Mechanical Function                      ║ Operation ║ Shape   ║ Axis ║ Center (X,Y,Z)   ║ Dimensions       ║
╠═══╬══════════════════════╬══════════════════════════════════════════╬═══════════╬═════════╬══════╬══════════════════╬══════════════════╣
║ 1 ║ Base plate           ║ Structural substrate; fits same rails    ║ Add       ║ Box     ║  —   ║ (68.6,1.5,34.3)  ║ 137.2×3×68.6 mm  ║
║   ║                      ║ as pump tray (3mm thick)                 ║           ║         ║      ║                  ║                  ║
╠═══╬══════════════════════╬══════════════════════════════════════════╬═══════════╬═════════╬══════╬══════════════════╬══════════════════╣
║ 2 ║ Boss B1 (bot-left)   ║ Provides 12.08mm capture depth;         ║ Add       ║ Cyl     ║  Y   ║ (60.1,7.54,25.8) ║ OD 16mm, h 9.08  ║
║ 3 ║ Boss B2 (bot-right)  ║ boss tip face (Y=12.08) is shoulder-    ║ Add       ║ Cyl     ║  Y   ║ (77.1,7.54,25.8) ║ OD 16mm, h 9.08  ║
║ 4 ║ Boss B3 (top-left)   ║ bearing surface for JG union body-end   ║ Add       ║ Cyl     ║  Y   ║ (60.1,7.54,42.8) ║ OD 16mm, h 9.08  ║
║ 5 ║ Boss B4 (top-right)  ║ shoulder (15.10mm OD → 9.31mm)          ║ Add       ║ Cyl     ║  Y   ║ (77.1,7.54,42.8) ║ OD 16mm, h 9.08  ║
╠═══╬══════════════════════╬══════════════════════════════════════════╬═══════════╬═════════╬══════╬══════════════════╬══════════════════╣
║ 6 ║ Bore H1 (bot-left)   ║ Continuous 9.5mm bore Y=0→12.08mm;      ║ Remove    ║ Cyl     ║  Y   ║ (60.1,6.04,25.8) ║ 9.5mm dia, TH    ║
║ 7 ║ Bore H2 (bot-right)  ║ captures JG union center body (9.31mm); ║ Remove    ║ Cyl     ║  Y   ║ (77.1,6.04,25.8) ║ 9.5mm dia, TH    ║
║ 8 ║ Bore H3 (top-left)   ║ front shoulder bears on Y=0 face;       ║ Remove    ║ Cyl     ║  Y   ║ (60.1,6.04,42.8) ║ 9.5mm dia, TH    ║
║ 9 ║ Bore H4 (top-right)  ║ back shoulder bears on boss tip Y=12.08 ║ Remove    ║ Cyl     ║  Y   ║ (77.1,6.04,42.8) ║ 9.5mm dia, TH    ║
╚═══╩══════════════════════╩══════════════════════════════════════════╩═══════════╩═════════╩══════╩══════════════════╩══════════════════╝
TH = through-bore, full depth Y=0→12.08mm (base plate + boss inner bore continuous)
Boss Y center = (3 + 12.08) / 2 = 7.54mm
Hole positions: 2×2 grid centered at (X=68.6, Z=34.3), 17mm c-c in both X and Z.
"""

print(FEATURE_TABLE)

# ---------------------------------------------------------------------------
# Dimensions (from parts.md)
# ---------------------------------------------------------------------------

# Plate envelope
PLATE_W   = 137.2   # X — width left to right
PLATE_D   = 3.0     # Y — base plate thickness (front to back of base)
PLATE_H   = 68.6    # Z — height bottom to top

# Boss geometry
BOSS_OD     = 16.0   # mm — outer diameter of boss cylinder
BOSS_ID     = 9.5    # mm — inner bore diameter (same as coupler capture hole)
BOSS_R_OUT  = BOSS_OD / 2.0    # 8.0mm
BOSS_R_IN   = BOSS_ID / 2.0    # 4.75mm
FULL_DEPTH  = 12.08  # mm — total bore depth (base plate + boss height)
BOSS_H      = FULL_DEPTH - PLATE_D   # 9.08mm — boss protrusion from back face

# Coupler capture bore
HOLE_DIA = 9.5     # mm
HOLE_R   = HOLE_DIA / 2.0   # 4.75mm

# Hole/boss centers (X, Z) — 2×2 grid centered at (68.6, 34.3), 17mm c-c
HOLES = [
    ("H1/B1", 60.1, 25.8),   # bottom-left
    ("H2/B2", 77.1, 25.8),   # bottom-right
    ("H3/B3", 60.1, 42.8),   # top-left
    ("H4/B4", 77.1, 42.8),   # top-right
]

MID_Y_BASE  = PLATE_D / 2.0                  # 1.5mm — mid-depth of base plate
MID_Y_BOSS  = PLATE_D + BOSS_H / 2.0         # 7.54mm — mid-height of boss
MID_Y_BORE  = FULL_DEPTH / 2.0               # 6.04mm — mid-depth of full bore

OVERCUT = 0.1   # mm past exit face to ensure clean boolean exit

# ---------------------------------------------------------------------------
# Feature 1 — Base Plate
# centered=False places box with corner at origin, extending +X, +Y, +Z.
# Result: X:[0,137.2], Y:[0,3], Z:[0,68.6]
# ---------------------------------------------------------------------------

print("Building Feature 1 — Base plate (137.2 × 3 × 68.6 mm)...")

plate = (
    cq.Workplane("XY")
    .box(PLATE_W, PLATE_D, PLATE_H, centered=False)
)

# ---------------------------------------------------------------------------
# Features 2–5 — Bosses (4× solid cylinders on back face, Y=3→12.08)
#
# XZ workplane normal is -Y. workplane(offset=-(PLATE_D)) positions the sketch
# at Y=PLATE_D (back face). extrude(-(BOSS_H)) goes in +Y direction, adding
# the boss protruding from Y=3mm to Y=12.08mm.
# ---------------------------------------------------------------------------

print(f"Building Features 2–5 — 4× bosses (OD={BOSS_OD}mm, h={BOSS_H}mm, Y=3→12.08mm)...")

for feat_id, hx, hz in HOLES:
    print(f"  Adding boss {feat_id} at X={hx}, Z={hz}")
    boss = (
        cq.Workplane("XZ")
        .workplane(offset=-PLATE_D)          # sketch plane at Y=PLATE_D (back face)
        .center(hx, hz)                      # boss center in XZ
        .circle(BOSS_R_OUT)
        .extrude(-(BOSS_H + OVERCUT))        # +Y direction: Y=3 → Y=12.18mm (overcut trimmed below)
    )
    # Intersect with a bounding solid capped at Y=FULL_DEPTH to avoid the overcut
    # Instead use exact BOSS_H without overcut — bosses are additive, no boolean issue
    boss = (
        cq.Workplane("XZ")
        .workplane(offset=-PLATE_D)
        .center(hx, hz)
        .circle(BOSS_R_OUT)
        .extrude(-BOSS_H)                    # +Y direction: Y=3mm → Y=12.08mm exactly
    )
    plate = plate.union(boss)

print("Bosses complete.")
print()

# ---------------------------------------------------------------------------
# Features 6–9 — Through-bores (4×, 9.5mm dia, Y=0→12.08mm continuous)
#
# Single cut from Y=0 through the base plate and the full boss height.
# XZ workplane normal is -Y. workplane(offset=0) positions sketch at Y=0.
# extrude(-(FULL_DEPTH + OVERCUT)) goes in +Y direction: Y=0 → Y=12.18mm,
# cutting through base plate and boss inner bore in one operation.
# ---------------------------------------------------------------------------

print(f"Building Features 6–9 — 4× through-bores ({HOLE_DIA}mm dia, Y=0→{FULL_DEPTH}mm)...")

for feat_id, hx, hz in HOLES:
    print(f"  Cutting bore {feat_id} at X={hx}, Z={hz}")
    bore = (
        cq.Workplane("XZ")
        .workplane(offset=0)                         # sketch plane at Y=0 (front face)
        .center(hx, hz)                              # bore center in XZ
        .circle(HOLE_R)
        .extrude(-(FULL_DEPTH + OVERCUT))            # +Y direction: Y=0 → Y=12.18mm
    )
    plate = plate.cut(bore)

print("Model construction complete.")
print()

# ---------------------------------------------------------------------------
# Export STEP file
# ---------------------------------------------------------------------------

OUTPUT_STEP = Path(__file__).resolve().parent / "coupler-tray-cadquery.step"
print(f"Exporting STEP file → {OUTPUT_STEP}")
cq.exporters.export(plate, str(OUTPUT_STEP))
print("Export complete.")
print()

# ---------------------------------------------------------------------------
# Rubric 3 — Feature-Specification Reconciliation
# Probe every feature row from the Feature Planning Table.
# ---------------------------------------------------------------------------

print("=" * 60)
print("RUBRIC 3 — Feature-Specification Reconciliation")
print("=" * 60)
print()

v = Validator(plate)

# --- Feature 1: Base plate ---
print("Feature 1 — Base plate:")
v.check_solid("Base plate center",       68.6,  MID_Y_BASE,  34.3,  "solid at base plate geometric center")
v.check_solid("Base plate near Y=0",     68.6,  0.3,         34.3,  "solid near front face Y=0")
v.check_solid("Base plate near Y=3",     68.6,  2.7,         34.3,  "solid near back face Y=3")
v.check_solid("Base plate left edge",    0.5,   MID_Y_BASE,  34.3,  "solid near X=0 left edge")
v.check_solid("Base plate right edge",   136.7, MID_Y_BASE,  34.3,  "solid near X=137.2 right edge")
v.check_solid("Base plate bottom edge",  68.6,  MID_Y_BASE,  0.5,   "solid near Z=0 bottom edge")
v.check_solid("Base plate top edge",     68.6,  MID_Y_BASE,  68.1,  "solid near Z=68.6 top edge")
# Verify base plate does NOT extend above Y=3 in a region with no boss (away from hole positions)
v.check_void("No material above base plate (away from bosses)",
             5.0, PLATE_D + 1.0, 5.0,
             "void at Y=4mm near corner — base plate only 3mm, no boss at X=5, Z=5")
print()

# --- Features 2–5: Bosses ---
for feat_id, hx, hz in HOLES:
    bid = feat_id.split("/")[1]
    print(f"Feature — Boss {bid} at X={hx}, Z={hz}:")

    # Solid inside boss wall mid-height
    v.check_solid(f"Boss {bid} wall mid-height",
                  hx + BOSS_R_IN + (BOSS_R_OUT - BOSS_R_IN) / 2.0,
                  MID_Y_BOSS, hz,
                  f"solid in boss wall at mid-height Y={MID_Y_BOSS:.2f}")

    # Solid in boss wall near base of boss (just above back face)
    v.check_solid(f"Boss {bid} wall near base",
                  hx + BOSS_R_IN + 1.0, PLATE_D + 0.5, hz,
                  f"solid in boss wall just above back face Y={PLATE_D + 0.5}")

    # Solid in boss wall near tip face
    v.check_solid(f"Boss {bid} wall near tip",
                  hx + BOSS_R_IN + 1.0, FULL_DEPTH - 0.3, hz,
                  f"solid in boss wall near tip face Y={FULL_DEPTH - 0.3:.2f}")

    # Void at boss center near tip face (inner bore, not solid boss)
    v.check_void(f"Boss {bid} inner bore near tip",
                 hx, FULL_DEPTH - 0.5, hz,
                 f"void at boss center near tip — bore passes through boss")

    # Verify boss does NOT exist far outside OD radius (8mm) at mid-boss height
    v.check_void(f"Boss {bid} void beyond OD (+X)",
                 hx + BOSS_R_OUT + 1.0, MID_Y_BOSS, hz,
                 f"void outside boss OD radius in +X at Y={MID_Y_BOSS:.2f}")

    print()

# --- Features 6–9: Through-bores ---
for feat_id, hx, hz in HOLES:
    hid = feat_id.split("/")[0]
    print(f"Feature — Bore {hid} at X={hx}, Z={hz}:")

    # Void at bore center in base plate (mid-depth)
    v.check_void(f"Bore {hid} center mid-base",
                 hx, MID_Y_BASE, hz,
                 f"void at ({hx}, {MID_Y_BASE:.1f}, {hz}) — bore in base plate")

    # Void near front face — bore enters Y=0
    v.check_void(f"Bore {hid} near front face",
                 hx, 0.3, hz,
                 f"void at ({hx}, 0.3, {hz}) — bore enters front face")

    # Void in boss inner bore mid-height
    v.check_void(f"Bore {hid} in boss mid-height",
                 hx, MID_Y_BOSS, hz,
                 f"void at ({hx}, {MID_Y_BOSS:.2f}, {hz}) — inner bore at boss mid-height")

    # Void near tip face — bore exits boss at Y=12.08
    v.check_void(f"Bore {hid} near tip face",
                 hx, FULL_DEPTH - 0.3, hz,
                 f"void at ({hx}, {FULL_DEPTH - 0.3:.2f}, {hz}) — bore exits boss tip face")

    # Path continuity: void just below and just above base/boss interface (Y=3mm)
    v.check_void(f"Bore {hid} path continuity below Y=3",
                 hx, PLATE_D - 0.1, hz,
                 f"void just below base/boss interface Y={PLATE_D - 0.1:.1f} — bore through base plate reaches interface")
    v.check_void(f"Bore {hid} path continuity above Y=3",
                 hx, PLATE_D + 0.1, hz,
                 f"void just above base/boss interface Y={PLATE_D + 0.1:.1f} — boss inner bore starts at interface")

    # Solid just outside bore radius in +X direction (in base plate) — confirms bore diameter
    v.check_solid(f"Bore {hid} solid outside (+X) in base",
                  hx + HOLE_R + 0.5, MID_Y_BASE, hz,
                  f"solid at ({hx + HOLE_R + 0.5:.2f}, {MID_Y_BASE:.1f}, {hz}) — outside bore radius")

    # Solid just outside bore radius in +X direction (in boss wall) — confirms boss bore dia
    v.check_solid(f"Bore {hid} solid outside (+X) in boss",
                  hx + HOLE_R + 0.5, MID_Y_BOSS, hz,
                  f"solid at ({hx + HOLE_R + 0.5:.2f}, {MID_Y_BOSS:.2f}, {hz}) — boss wall outside bore")

    print()

# ---------------------------------------------------------------------------
# Rubric 4 — Solid Validity
# ---------------------------------------------------------------------------

print("=" * 60)
print("RUBRIC 4 — Solid Validity")
print("=" * 60)
print()

v.check_valid()
v.check_single_body()

# Volume estimate:
#   Base plate: 137.2 × 3 × 68.6 = 28,235 mm³
#   4 bosses (solid): π × 8² × 9.08 × 4 = 7,282 mm³
#   4 bores (full depth): π × 4.75² × 12.08 × 4 = 3,431 mm³
#   Expected ≈ 28,235 + 7,282 − 3,431 = 32,086 mm³
#   Bounding box envelope: 137.2 × 12.08 × 68.6 = 113,822 mm³
#   Fill ratio ≈ 32,086 / 113,822 ≈ 0.282 — well within (0.1, 0.8) range
envelope_vol = PLATE_W * FULL_DEPTH * PLATE_H
v.check_volume(expected_envelope=envelope_vol, fill_range=(0.1, 0.8))
print()

# ---------------------------------------------------------------------------
# Rubric 5 — Bounding Box Reconciliation
# ---------------------------------------------------------------------------

print("=" * 60)
print("RUBRIC 5 — Bounding Box Reconciliation")
print("=" * 60)
print()

bb = plate.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, 0.0,      PLATE_W)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0,      FULL_DEPTH)  # bosses extend to 12.08
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0,      PLATE_H)
print()

# ---------------------------------------------------------------------------
# Final summary — exits 1 on any FAIL
# ---------------------------------------------------------------------------

if not v.summary():
    print()
    print("FAILURES DETECTED — fix model before exporting.")
    sys.exit(1)

print()
print(f"STEP file written: {OUTPUT_STEP}")
