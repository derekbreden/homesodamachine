#!/usr/bin/env python3
"""
Enclosure Tub (Structural Monocoque) — CadQuery STEP Generator

The structural core of the enclosure: a five-sided open-top box with 4mm walls.
Front wall is partial (Z=0-130 only). Cartridge slot opening on front wall.
Snap receptacle slots in side walls for front panel. Tongue on rim for top panel.
Magnet pockets in rim. Groove in front wall top face for front panel tongue.

This models the tub as a single pre-joined piece (not split at Z=200).
The Z=200 manufacturing split is handled separately.

Coordinate system:
  Origin: exterior front-bottom-left corner
  X: width [0, 220]
  Y: depth [0, 300]
  Z: height [0, 398] (rim at 396, tongue to 398)
"""

import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

import cadquery as cq
from step_validate import Validator

# ============================================================================
# DIMENSIONS
# ============================================================================

# Overall exterior
EXT_W = 220.0       # X
EXT_D = 300.0       # Y
EXT_H = 396.0       # Z (rim height; top panel adds 4mm to Z=400)
WALL_T = 4.0        # Wall and floor thickness
CORNER_R = 6.0      # Vertical edge radii

# Interior
INT_W = EXT_W - 2 * WALL_T       # 212
INT_D = EXT_D - 2 * WALL_T       # 292
INT_H = EXT_H - WALL_T           # 392 (floor is 4mm)

# Front wall (partial)
FRONT_WALL_H = 130.0             # Z=0 to Z=130 only

# Cartridge slot opening
SLOT_W = 148.0                    # Width of opening
SLOT_H = 84.0                    # Height of opening
SLOT_X_MIN = (EXT_W - SLOT_W) / 2  # 36.0
SLOT_X_MAX = SLOT_X_MIN + SLOT_W   # 184.0

# Front panel tongue groove (top face of front wall at Z=130)
FP_GROOVE_W = 2.2       # Width (Y direction, centered in wall)
FP_GROOVE_D = 3.0        # Depth (into top face, downward from Z=130)

# Snap receptacle slots (4 total: 2 per side wall)
# Located near front face for front panel engagement
SNAP_Y_MIN = 10.0       # Y start (near front face)
SNAP_Y_MAX = 22.0       # Y end (12mm wide)
SNAP_DEPTH = 3.0        # Into wall from interior face
SNAP_HEIGHT = 8.0       # Z extent
SNAP_Z_CENTERS = [200.0, 340.0]  # Z positions (enclosure coords)

# Top panel interface: tongue on rim (3 sides: left, right, back)
TONGUE_W = 3.0           # Width (across wall thickness, centered)
TONGUE_H = 2.0           # Height (protrudes above Z=396)

# Magnet pockets in rim top face
MAG_DIA = 6.2            # Pocket diameter
MAG_DEPTH = 3.2          # Pocket depth (from rim top face, downward)
MAG_Y = 150.0            # Y position

# ============================================================================
# RUBRIC 1 — Feature Planning Table
# ============================================================================
print("=" * 80)
print("RUBRIC 1 — Feature Planning Table")
print("=" * 80)
features = [
    ("1",  "Outer shell",            "Exterior box",                 "Add", "RoundBox",  "XYZ",
     f"0-{EXT_W}, 0-{EXT_D}, 0-{EXT_H}", f"R={CORNER_R}mm corners"),
    ("2",  "Interior cavity",        "Hollow out shell",             "Rem", "RoundBox",  "XYZ",
     f"{WALL_T}-{EXT_W-WALL_T}, {WALL_T}-{EXT_D-WALL_T}, {WALL_T}-{EXT_H}",
     f"{INT_W}x{INT_D}x{INT_H}mm"),
    ("3",  "Remove upper front wall","Open front above Z=130",      "Rem", "Box",       "Z",
     f"X=0-{EXT_W}, Y=0-{WALL_T}, Z={FRONT_WALL_H}-{EXT_H}", ""),
    ("4",  "Cartridge slot",         "Opening in front wall",       "Rem", "Box",       "Y",
     f"X={SLOT_X_MIN}-{SLOT_X_MAX}, Z=0-{SLOT_H}", f"{SLOT_W}x{SLOT_H}mm"),
    ("5",  "Front panel groove",     "Tongue groove at Z=130",      "Rem", "Box",       "X",
     f"Y centered, Z={FRONT_WALL_H-FP_GROOVE_D}-{FRONT_WALL_H}", f"{FP_GROOVE_W}x{FP_GROOVE_D}mm"),
    ("6",  "Snap receptacles x4",    "Front panel hook pockets",    "Rem", "Box",       "X",
     f"Side walls, Z={SNAP_Z_CENTERS}", f"12x{SNAP_DEPTH}x{SNAP_HEIGHT}mm"),
    ("7",  "Rim tongue (3 sides)",   "Top panel alignment",         "Add", "Channel",   "perimeter",
     f"Z={EXT_H}-{EXT_H+TONGUE_H}", f"{TONGUE_W}x{TONGUE_H}mm"),
    ("8",  "Magnet pockets x2",      "Top panel retention",         "Rem", "Cylinder",  "Z",
     f"Y={MAG_Y}, rim top face", f"{MAG_DIA}mm dia x {MAG_DEPTH}mm deep"),
]
for row in features:
    num, name, func, op, shape, axis, pos, dims = row
    print(f"  {num:<4} {name:<28} {func:<30} {op:<5} {shape:<10} {axis:<10} {pos}")
    if dims:
        print(f"       Dims: {dims}")
print()
sys.stdout.flush()

# ============================================================================
# MODELING
# ============================================================================

# --- Feature 1: Outer shell ---
print("Building outer shell...")
sys.stdout.flush()
outer = (
    cq.Workplane("XY")
    .rect(EXT_W, EXT_D)
    .extrude(EXT_H)
)
outer = outer.edges("|Z").fillet(CORNER_R)
outer = outer.translate((EXT_W / 2, EXT_D / 2, 0))
print(f"  Outer: {EXT_W}x{EXT_D}x{EXT_H}mm")

# --- Feature 2: Interior cavity ---
print("Cutting interior cavity...")
sys.stdout.flush()
inner_corner_r = max(CORNER_R - WALL_T, 0.5)  # 2.0mm interior corners
inner = (
    cq.Workplane("XY")
    .rect(INT_W, INT_D)
    .extrude(INT_H)
)
inner = inner.edges("|Z").fillet(inner_corner_r)
inner = inner.translate((EXT_W / 2, EXT_D / 2, WALL_T))
tub = outer.cut(inner)
print(f"  Interior: {INT_W}x{INT_D}x{INT_H}mm, corner R={inner_corner_r}mm")

# --- Feature 3: Remove upper front wall (above Z=130) ---
# The front wall (Y=0 to Y=WALL_T) exists only from Z=0 to Z=130.
# Remove the section from Z=130 to Z=396.
print("Removing upper front wall...")
sys.stdout.flush()
upper_front_cut = (
    cq.Workplane("XY")
    .workplane(offset=FRONT_WALL_H)
    .center(EXT_W / 2, WALL_T / 2)
    .rect(EXT_W - 2 * CORNER_R, WALL_T + 1)  # Slightly wider to ensure clean cut
    .extrude(EXT_H - FRONT_WALL_H + 1)
)
tub = tub.cut(upper_front_cut)
print(f"  Front wall removed above Z={FRONT_WALL_H}")

# --- Feature 4: Cartridge slot opening ---
# Through the front wall (Y=0 to Y=WALL_T) from Z=0 to Z=SLOT_H
print("Cutting cartridge slot opening...")
sys.stdout.flush()
slot = (
    cq.Workplane("XZ")
    .center((SLOT_X_MIN + SLOT_X_MAX) / 2, SLOT_H / 2)
    .rect(SLOT_W, SLOT_H)
    .extrude(-WALL_T - 1)  # Through front wall
)
tub = tub.cut(slot)
print(f"  Slot: {SLOT_W}x{SLOT_H}mm at X={SLOT_X_MIN}-{SLOT_X_MAX}")

# --- Feature 5: Front panel tongue groove ---
# A groove in the top face of the front wall at Z=130
# Centered in Y within the 4mm wall, FP_GROOVE_W wide, FP_GROOVE_D deep
print("Cutting front panel tongue groove...")
sys.stdout.flush()
groove_y_center = WALL_T / 2  # 2.0 (centered in wall)
fp_groove = (
    cq.Workplane("XY")
    .workplane(offset=FRONT_WALL_H - FP_GROOVE_D)
    .center(EXT_W / 2, groove_y_center)
    .rect(EXT_W - 2 * CORNER_R, FP_GROOVE_W)
    .extrude(FP_GROOVE_D + 1)
)
tub = tub.cut(fp_groove)
print(f"  Groove: {FP_GROOVE_W}mm wide x {FP_GROOVE_D}mm deep at Z={FRONT_WALL_H}")

# --- Feature 6: Snap receptacle slots (4x) ---
# In interior faces of side walls, near front
# Left wall interior face at X=WALL_T, right wall at X=EXT_W-WALL_T
print("Cutting snap receptacle slots...")
sys.stdout.flush()

for z_center in SNAP_Z_CENTERS:
    for side, x_start in [("left", 0), ("right", EXT_W - WALL_T)]:
        # Cut from interior face into wall
        # Left: cut from X=WALL_T inward toward X=0 (SNAP_DEPTH into wall)
        # Right: cut from X=EXT_W-WALL_T inward toward X=EXT_W
        if side == "left":
            slot_x = WALL_T - SNAP_DEPTH / 2  # Center of cut in X: 2.5
            # Actually, the slot goes from X=1 (leaving 1mm exterior) to X=4 (interior face)
            slot_x = WALL_T - SNAP_DEPTH + SNAP_DEPTH / 2  # 1 + 1.5 = 2.5
        else:
            slot_x = EXT_W - WALL_T + SNAP_DEPTH / 2  # 216 + 1.5 = 217.5

        snap_slot = (
            cq.Workplane("XY")
            .workplane(offset=z_center - SNAP_HEIGHT / 2)
            .center(slot_x, (SNAP_Y_MIN + SNAP_Y_MAX) / 2)
            .rect(SNAP_DEPTH, SNAP_Y_MAX - SNAP_Y_MIN)
            .extrude(SNAP_HEIGHT)
        )
        tub = tub.cut(snap_slot)
        print(f"  {side} receptacle at Z={z_center}: {SNAP_DEPTH}mm deep")

# --- Feature 7: Rim tongue (3 sides) ---
# Protrudes upward from rim top face (Z=396) by TONGUE_H (2mm)
# Runs along left, right, and back wall rims
# Width: TONGUE_W (3mm), centered in 4mm wall
print("Building rim tongue...")
sys.stdout.flush()

tongue_offset = (WALL_T - TONGUE_W) / 2  # 0.5mm from each wall face

# Left tongue: X = tongue_offset to tongue_offset + TONGUE_W, Y = 0 to EXT_D
left_tongue = (
    cq.Workplane("XY")
    .workplane(offset=EXT_H)
    .center(tongue_offset + TONGUE_W / 2, EXT_D / 2)
    .rect(TONGUE_W, EXT_D)
    .extrude(TONGUE_H)
)
tub = tub.union(left_tongue)

# Right tongue: X = EXT_W - tongue_offset - TONGUE_W to EXT_W - tongue_offset
right_tongue = (
    cq.Workplane("XY")
    .workplane(offset=EXT_H)
    .center(EXT_W - tongue_offset - TONGUE_W / 2, EXT_D / 2)
    .rect(TONGUE_W, EXT_D)
    .extrude(TONGUE_H)
)
tub = tub.union(right_tongue)

# Back tongue: Y = EXT_D - tongue_offset - TONGUE_W to EXT_D - tongue_offset
# Runs between left and right tongues
back_tongue = (
    cq.Workplane("XY")
    .workplane(offset=EXT_H)
    .center(EXT_W / 2, EXT_D - tongue_offset - TONGUE_W / 2)
    .rect(EXT_W - 2 * WALL_T, TONGUE_W)  # Between side walls
    .extrude(TONGUE_H)
)
tub = tub.union(back_tongue)
print(f"  Tongue: {TONGUE_W}mm wide x {TONGUE_H}mm tall on 3 sides")

# --- Feature 8: Magnet pockets in rim (2x) ---
# Blind holes in rim top face at Z=396, going downward
print("Cutting magnet pockets...")
sys.stdout.flush()

for side, mx in [("left", WALL_T / 2), ("right", EXT_W - WALL_T / 2)]:
    pocket = (
        cq.Workplane("XY")
        .workplane(offset=EXT_H - MAG_DEPTH)
        .center(mx, MAG_Y)
        .circle(MAG_DIA / 2)
        .extrude(MAG_DEPTH + TONGUE_H + 1)  # Through tongue too
    )
    tub = tub.cut(pocket)
    print(f"  {side} magnet pocket: {MAG_DIA}mm at ({mx}, {MAG_Y})")

# ============================================================================
# EXPORT
# ============================================================================
output_path = Path(__file__).parent / "tub.step"
cq.exporters.export(tub, str(output_path))
print(f"\nSTEP file exported to: {output_path}")

# ============================================================================
# RUBRIC 3 — Validation Probes
# ============================================================================
print("\n" + "=" * 60)
print("RUBRIC 3 — Validation Probes")
print("=" * 60)

v = Validator(tub)

# --- Walls ---
# Left wall solid
v.check_solid("Left wall mid", WALL_T / 2, EXT_D / 2, EXT_H / 2,
              "solid in left wall")
# Right wall solid
v.check_solid("Right wall mid", EXT_W - WALL_T / 2, EXT_D / 2, EXT_H / 2,
              "solid in right wall")
# Back wall solid
v.check_solid("Back wall mid", EXT_W / 2, EXT_D - WALL_T / 2, EXT_H / 2,
              "solid in back wall")
# Floor solid
v.check_solid("Floor center", EXT_W / 2, EXT_D / 2, WALL_T / 2,
              "solid at floor center")

# --- Interior cavity ---
v.check_void("Interior center", EXT_W / 2, EXT_D / 2, EXT_H / 2,
             "void at interior center")
v.check_void("Interior near floor", EXT_W / 2, EXT_D / 2, WALL_T + 5,
             "void just above floor")

# --- Exterior boundary ---
v.check_void("Outside -X", -1, EXT_D / 2, EXT_H / 2, "void outside left wall")
v.check_void("Outside +X", EXT_W + 1, EXT_D / 2, EXT_H / 2, "void outside right wall")
v.check_void("Outside +Y", EXT_W / 2, EXT_D + 1, EXT_H / 2, "void outside back wall")
v.check_void("Below floor", EXT_W / 2, EXT_D / 2, -1, "void below floor")

# --- Front wall (partial, Z=0-130) ---
v.check_solid("Front wall above slot", EXT_W / 2, WALL_T / 2, SLOT_H + 20,
              "solid in front wall above slot at Z=104")
v.check_solid("Front wall side column", 18, WALL_T / 2, 42,
              "solid in front wall left column (beside slot)")

# Front wall above Z=130: should be void (removed)
v.check_void("No front wall Z=200", EXT_W / 2, WALL_T / 2, 200,
             "void where upper front wall was removed")
v.check_void("No front wall Z=350", EXT_W / 2, WALL_T / 2, 350,
             "void where upper front wall was removed (high)")

# --- Cartridge slot opening ---
v.check_void("Slot center", EXT_W / 2, WALL_T / 2, SLOT_H / 2,
             "void at cartridge slot center")
v.check_void("Slot edge left", SLOT_X_MIN + 5, WALL_T / 2, 20,
             "void inside slot near left edge")
# Solid beside slot
v.check_solid("Beside slot left", SLOT_X_MIN - 10, WALL_T / 2, 20,
              "solid in front wall beside slot (left)")
v.check_solid("Beside slot right", SLOT_X_MAX + 10, WALL_T / 2, 20,
              "solid in front wall beside slot (right)")
# Solid above slot
v.check_solid("Above slot", EXT_W / 2, WALL_T / 2, SLOT_H + 20,
              "solid in front wall above slot")

# --- Front panel tongue groove ---
v.check_void("FP groove center", EXT_W / 2, WALL_T / 2, FRONT_WALL_H - FP_GROOVE_D / 2,
             "void in front panel groove at Z=128.5")
v.check_solid("FP groove below", EXT_W / 2, WALL_T / 2, FRONT_WALL_H - FP_GROOVE_D - 2,
              "solid below groove")

# --- Snap receptacle slots ---
snap_y_center = (SNAP_Y_MIN + SNAP_Y_MAX) / 2  # 16.0
# Left wall, Z=200
v.check_void("Left snap Z=200", WALL_T - SNAP_DEPTH / 2, snap_y_center, SNAP_Z_CENTERS[0],
             "void in left snap receptacle at Z=200")
# Right wall, Z=340
v.check_void("Right snap Z=340", EXT_W - WALL_T + SNAP_DEPTH / 2,
             snap_y_center, SNAP_Z_CENTERS[1],
             "void in right snap receptacle at Z=340")
# Solid outside receptacle (exterior wall remaining)
v.check_solid("Left snap exterior", 0.3, snap_y_center, SNAP_Z_CENTERS[0],
              "solid outside left snap (exterior wall)")

# --- Rim tongue ---
tongue_z_mid = EXT_H + TONGUE_H / 2  # 397
# Left tongue solid (avoid magnet pocket at Y=150)
v.check_solid("Left tongue", tongue_offset + TONGUE_W / 2, 100, tongue_z_mid,
              "solid in left rim tongue")
# Right tongue solid (avoid magnet pocket at Y=150)
v.check_solid("Right tongue", EXT_W - tongue_offset - TONGUE_W / 2, 100, tongue_z_mid,
              "solid in right rim tongue")
# Back tongue solid
v.check_solid("Back tongue", EXT_W / 2, EXT_D - tongue_offset - TONGUE_W / 2, tongue_z_mid,
              "solid in back rim tongue")
# No tongue on front (above open area)
v.check_void("No front tongue", EXT_W / 2, WALL_T / 2, tongue_z_mid,
             "void where front tongue would be (no front wall)")
# Void above tongue
v.check_void("Above tongue", WALL_T / 2, EXT_D / 2, EXT_H + TONGUE_H + 1,
             "void above tongue")
# Void inside rim (between tongues)
v.check_void("Inside rim", EXT_W / 2, EXT_D / 2, tongue_z_mid,
             "void inside rim (interior)")

# --- Magnet pockets ---
v.check_void("Left magnet pocket", WALL_T / 2, MAG_Y, EXT_H - MAG_DEPTH / 2,
             "void in left magnet pocket")
v.check_void("Right magnet pocket", EXT_W - WALL_T / 2, MAG_Y, EXT_H - MAG_DEPTH / 2,
             "void in right magnet pocket")
# Solid beside magnet pocket (wall material)
v.check_solid("Beside left magnet", WALL_T / 2, MAG_Y + MAG_DIA, EXT_H - 1,
              "solid in rim beside magnet pocket")

# ============================================================================
# RUBRIC 4
# ============================================================================
print("\n" + "=" * 60)
print("RUBRIC 4 — Solid Validity")
print("=" * 60)
v.check_valid()
v.check_single_body()

outer_vol = EXT_W * EXT_D * EXT_H
v.check_volume(expected_envelope=outer_vol, fill_range=(0.03, 0.20))

# ============================================================================
# RUBRIC 5
# ============================================================================
print("\n" + "=" * 60)
print("RUBRIC 5 — Bounding Box")
print("=" * 60)
bb = tub.val().BoundingBox()
print(f"Actual BB: X[{bb.xmin:.2f}, {bb.xmax:.2f}] "
      f"Y[{bb.ymin:.2f}, {bb.ymax:.2f}] "
      f"Z[{bb.zmin:.2f}, {bb.zmax:.2f}]")

v.check_bbox("X", bb.xmin, bb.xmax, 0, EXT_W, tol=1.0)
v.check_bbox("Y", bb.ymin, bb.ymax, 0, EXT_D, tol=1.0)
v.check_bbox("Z", bb.zmin, bb.zmax, 0, EXT_H + TONGUE_H, tol=1.0)

# ============================================================================
# SUMMARY
# ============================================================================
if not v.summary():
    sys.exit(1)

print("\nDone.")
