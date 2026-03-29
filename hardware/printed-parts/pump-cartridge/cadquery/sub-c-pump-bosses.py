"""
Sub-C: Pump Mounting Bosses — CadQuery generation script.

Generates 4 mounting bosses with pilot holes and gusset ribs,
plus 2 semicircular motor cradles, as standalone solids positioned
in the tray reference frame.

Coordinate system:
  Origin: rear-left-bottom corner of tray outer envelope
  X: 0..160 (width, left to right)
  Y: 0..155 (depth, dock/rear to user/front)
  Z: 0..72 (height, bottom to top)
  Floor inner surface: Z = 3.00
  Left wall inner face: X = 5.00
  Right wall inner face: X = 155.00
  Rear wall inner face: Y = 8.50

Feature Planning Table:
| # | Feature Name         | Function                  | Op  | Shape     | Axis | Center (X,Y,Z)         | Dimensions                       |
|---|----------------------|---------------------------|-----|-----------|------|------------------------|----------------------------------|
| 1 | Boss P1-L column     | Mount pump 1 left bracket | Add | Cylinder  | Z    | (18.48, 83.00, 18.65)  | OD=8, H=31.30 (Z=3..34.30)      |
| 2 | Boss P1-R column     | Mount pump 1 right bracket| Add | Cylinder  | Z    | (67.93, 83.00, 18.65)  | OD=8, H=31.30 (Z=3..34.30)      |
| 3 | Boss P2-L column     | Mount pump 2 left bracket | Add | Cylinder  | Z    | (92.08, 83.00, 18.65)  | OD=8, H=31.30 (Z=3..34.30)      |
| 4 | Boss P2-R column     | Mount pump 2 right bracket| Add | Cylinder  | Z    | (141.53, 83.00, 18.65) | OD=8, H=31.30 (Z=3..34.30)      |
| 5 | Boss P1-L pilot hole | Heat-set insert pocket    | Rem | Cylinder  | Z    | (18.48, 83.00, 30.80)  | D=4, depth=7 from top            |
| 6 | Boss P1-R pilot hole | Heat-set insert pocket    | Rem | Cylinder  | Z    | (67.93, 83.00, 30.80)  | D=4, depth=7 from top            |
| 7 | Boss P2-L pilot hole | Heat-set insert pocket    | Rem | Cylinder  | Z    | (92.08, 83.00, 30.80)  | D=4, depth=7 from top            |
| 8 | Boss P2-R pilot hole | Heat-set insert pocket    | Rem | Cylinder  | Z    | (141.53, 83.00, 30.80) | D=4, depth=7 from top            |
| 9 | Boss P1-L ribs (4x)  | Stiffness/print stability | Add | Tri gusset| Z    | centered on P1-L       | 2mm thick, 4mm radial, full H    |
|10 | Boss P1-R ribs (4x)  | Stiffness/print stability | Add | Tri gusset| Z    | centered on P1-R       | 2mm thick, 4mm radial, full H    |
|11 | Boss P2-L ribs (4x)  | Stiffness/print stability | Add | Tri gusset| Z    | centered on P2-L       | 2mm thick, 4mm radial, full H    |
|12 | Boss P2-R ribs (4x)  | Stiffness/print stability | Add | Tri gusset| Z    | centered on P2-R       | 2mm thick, 4mm radial, full H    |
|13 | Cradle 1 (Pump 1)    | Support motor body below  | Add | Semicircle| X    | (43.20, 116.50, 34.30) | Ri=17.75, wall=3, depth=15       |
|14 | Cradle 1 support rib | Fill below semicircle     | Add | Box       | Z    | (43.20, 116.50, ~9.78) | W=41.50, D=15, H=13.55 (Z=3..16.55)|
|15 | Cradle 2 (Pump 2)    | Support motor body below  | Add | Semicircle| X    | (116.80, 116.50, 34.30) | Ri=17.75, wall=3, depth=15      |
|16 | Cradle 2 support rib | Fill below semicircle     | Add | Box       | Z    | (116.80, 116.50, ~9.78)| W=41.50, D=15, H=13.55 (Z=3..16.55)|
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq
from step_validate import Validator

# ============================================================
# Constants from spec
# ============================================================

# Floor
FLOOR_Z = 3.00

# Boss geometry
BOSS_OD = 8.00
BOSS_R = BOSS_OD / 2  # 4.0
BOSS_TOP_Z = 34.30
BOSS_HEIGHT = BOSS_TOP_Z - FLOOR_Z  # 31.30

# Pilot hole
PILOT_D = 4.00
PILOT_R = PILOT_D / 2  # 2.0
PILOT_DEPTH = 7.00

# Ribs
RIB_THICKNESS = 2.00
RIB_RADIAL = 4.00  # extends 4mm from boss outer surface

# Boss positions (center X, Y)
BOSS_Y = 83.00
BOSSES = {
    "P1-L": (18.48, BOSS_Y),
    "P1-R": (67.93, BOSS_Y),
    "P2-L": (92.08, BOSS_Y),
    "P2-R": (141.53, BOSS_Y),
}

# Cradle geometry
CRADLE_IR = 17.75  # inner radius
CRADLE_WALL = 3.00
CRADLE_OR = CRADLE_IR + CRADLE_WALL  # 20.75
CRADLE_DEPTH = 15.00  # Y extent
CRADLE_CENTER_Z = 34.30
CRADLE_CENTER_Y = 116.50
CRADLE_Y_MIN = CRADLE_CENTER_Y - CRADLE_DEPTH / 2  # 109.00
CRADLE_Y_MAX = CRADLE_CENTER_Y + CRADLE_DEPTH / 2  # 124.00
CRADLE_ARC_BOTTOM_Z = CRADLE_CENTER_Z - CRADLE_IR  # 16.55
CRADLE_SUPPORT_H = CRADLE_ARC_BOTTOM_Z - FLOOR_Z  # 13.55

CRADLES = {
    "Cradle 1": 43.20,
    "Cradle 2": 116.80,
}

# ============================================================
# Print feature planning table
# ============================================================

print("Feature Planning Table:")
print(f"  Bosses: 4x cylinders OD={BOSS_OD}, H={BOSS_HEIGHT}, Z={FLOOR_Z}..{BOSS_TOP_Z}")
print(f"  Pilot holes: D={PILOT_D}, depth={PILOT_DEPTH} from top")
print(f"  Ribs: 4 per boss, {RIB_THICKNESS}mm thick, {RIB_RADIAL}mm radial extent")
print(f"  Cradles: 2x semicircle Ri={CRADLE_IR}, wall={CRADLE_WALL}, depth={CRADLE_DEPTH}")
print(f"  Cradle support ribs: W={CRADLE_OR*2}, H={CRADLE_SUPPORT_H}")
print()

# ============================================================
# Build geometry
# ============================================================

result = None


def add_solid(result, new_solid):
    """Union a new solid into the result."""
    if result is None:
        return new_solid
    return result.union(new_solid)


def make_boss_with_ribs(cx, cy):
    """Create a single boss column with 4 gusset ribs and pilot hole."""
    # Boss cylinder
    boss = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_Z)
        .center(cx, cy)
        .circle(BOSS_R)
        .extrude(BOSS_HEIGHT)
    )

    # Four ribs at 0/90/180/270 degrees (+X, -X, +Y, -Y)
    # Each rib: right triangle gusset, 2mm thick, 4mm radial, full height
    # Rib along +X: box from boss surface to boss surface + 4mm
    rib_specs = [
        # (x_start, y_start) relative to boss center, (width_x, width_y)
        (BOSS_R, -RIB_THICKNESS / 2, RIB_RADIAL, RIB_THICKNESS),    # +X
        (-BOSS_R - RIB_RADIAL, -RIB_THICKNESS / 2, RIB_RADIAL, RIB_THICKNESS),  # -X
        (-RIB_THICKNESS / 2, BOSS_R, RIB_THICKNESS, RIB_RADIAL),    # +Y
        (-RIB_THICKNESS / 2, -BOSS_R - RIB_RADIAL, RIB_THICKNESS, RIB_RADIAL),  # -Y
    ]

    for dx, dy, w, d in rib_specs:
        rib = (
            cq.Workplane("XY")
            .workplane(offset=FLOOR_Z)
            .center(cx + dx, cy + dy)
            .rect(w, d, centered=False)
            .extrude(BOSS_HEIGHT)
        )
        boss = boss.union(rib)

    # Pilot hole (cut from top face)
    pilot = (
        cq.Workplane("XY")
        .workplane(offset=BOSS_TOP_Z - PILOT_DEPTH)
        .center(cx, cy)
        .circle(PILOT_R)
        .extrude(PILOT_DEPTH + 0.01)  # slight overcut to ensure clean boolean
    )
    boss = boss.cut(pilot)

    return boss


def make_cradle(cx):
    """Create a semicircular motor cradle with support rib below."""
    # Support rib: rectangular block below the arc
    # Width = 2 * CRADLE_OR = 41.50
    # Positioned: X from cx - CRADLE_OR to cx + CRADLE_OR
    #             Y from CRADLE_Y_MIN to CRADLE_Y_MAX
    #             Z from FLOOR_Z to CRADLE_ARC_BOTTOM_Z
    support_w = CRADLE_OR * 2  # 41.50
    support = (
        cq.Workplane("XY")
        .workplane(offset=FLOOR_Z)
        .center(cx - CRADLE_OR, CRADLE_Y_MIN)
        .rect(support_w, CRADLE_DEPTH, centered=False)
        .extrude(CRADLE_SUPPORT_H)
    )

    # Semicircular cradle: half-pipe, 180 degrees bottom half
    # Create as difference of two cylinders (outer - inner), then cut to bottom half
    # Cylinder axis along Y, centered at (cx, CRADLE_CENTER_Y, CRADLE_CENTER_Z)
    # Outer cylinder
    outer_cyl = (
        cq.Workplane("XZ")
        .workplane(offset=-CRADLE_Y_MIN)  # XZ normal is -Y, so -offset moves in +Y
        .center(cx, CRADLE_CENTER_Z)
        .circle(CRADLE_OR)
        .extrude(-CRADLE_DEPTH)  # negative extrude goes +Y from offset
    )
    # Inner cylinder
    inner_cyl = (
        cq.Workplane("XZ")
        .workplane(offset=-CRADLE_Y_MIN)
        .center(cx, CRADLE_CENTER_Z)
        .circle(CRADLE_IR)
        .extrude(-CRADLE_DEPTH)
    )
    # Hollow tube
    tube = outer_cyl.cut(inner_cyl)

    # Cut away the top half (above center Z) to make it a semicircle (bottom half only)
    # Big cutting box: covers full X range, full Y range, Z from center to well above
    top_cut = (
        cq.Workplane("XY")
        .workplane(offset=CRADLE_CENTER_Z)
        .center(cx - CRADLE_OR - 1, CRADLE_Y_MIN - 1)
        .rect(support_w + 2, CRADLE_DEPTH + 2, centered=False)
        .extrude(CRADLE_OR + 10)
    )
    semicircle = tube.cut(top_cut)

    # Union support rib and semicircle
    cradle = support.union(semicircle)
    return cradle


# Build all bosses
for name, (cx, cy) in BOSSES.items():
    print(f"Building boss {name} at ({cx}, {cy})")
    boss = make_boss_with_ribs(cx, cy)
    result = add_solid(result, boss)

# Build all cradles
for name, cx in CRADLES.items():
    print(f"Building {name} at X={cx}")
    cradle = make_cradle(cx)
    result = add_solid(result, cradle)

print("\nGeometry built. Running validation...\n")

# ============================================================
# Validation
# ============================================================

v = Validator(result)

# --- Boss column solids ---
for name, (cx, cy) in BOSSES.items():
    mid_z = (FLOOR_Z + BOSS_TOP_Z) / 2
    # Solid at boss center (between pilot hole bottom and base)
    v.check_solid(f"{name} column center", cx, cy, FLOOR_Z + 5.0,
                  f"solid at boss {name} column body")
    # Solid at boss surface (just inside OD)
    v.check_solid(f"{name} OD -X", cx - BOSS_R + 0.3, cy, mid_z,
                  f"solid just inside boss {name} -X surface")
    # Void outside boss (beyond rib extent)
    v.check_void(f"{name} void beyond ribs +X", cx + BOSS_R + RIB_RADIAL + 1.0, cy, mid_z,
                 f"void beyond {name} +X rib tip")

# --- Pilot holes ---
for name, (cx, cy) in BOSSES.items():
    # Void at pilot hole center, near top
    v.check_void(f"{name} pilot hole center", cx, cy, BOSS_TOP_Z - 1.0,
                 f"void at {name} pilot hole center near top")
    # Void at pilot hole center, near bottom of hole
    v.check_void(f"{name} pilot hole bottom", cx, cy, BOSS_TOP_Z - PILOT_DEPTH + 0.5,
                 f"void at {name} pilot hole near bottom")
    # Solid below pilot hole
    v.check_solid(f"{name} solid below pilot", cx, cy, BOSS_TOP_Z - PILOT_DEPTH - 1.0,
                  f"solid below {name} pilot hole")

# --- Ribs ---
for name, (cx, cy) in BOSSES.items():
    mid_z = (FLOOR_Z + BOSS_TOP_Z) / 2
    # +X rib: solid at boss surface + 2mm radial (within rib extent)
    v.check_solid(f"{name} +X rib", cx + BOSS_R + 2.0, cy, mid_z,
                  f"solid in {name} +X rib")
    # -X rib
    v.check_solid(f"{name} -X rib", cx - BOSS_R - 2.0, cy, mid_z,
                  f"solid in {name} -X rib")
    # +Y rib
    v.check_solid(f"{name} +Y rib", cx, cy + BOSS_R + 2.0, mid_z,
                  f"solid in {name} +Y rib")
    # -Y rib
    v.check_solid(f"{name} -Y rib", cx, cy - BOSS_R - 2.0, mid_z,
                  f"solid in {name} -Y rib")
    # Void between ribs (diagonal, 45 degrees) — should be empty
    diag_offset = (BOSS_R + 1.5) * 0.707  # ~45 degrees, just outside boss
    v.check_void(f"{name} void diagonal", cx + diag_offset, cy + diag_offset, mid_z,
                 f"void between {name} ribs at 45 degrees")

# --- Cradle support ribs ---
for name, cx in CRADLES.items():
    mid_z = FLOOR_Z + CRADLE_SUPPORT_H / 2
    v.check_solid(f"{name} support rib center", cx, CRADLE_CENTER_Y, mid_z,
                  f"solid at {name} support rib center")
    # Solid at support rib edge
    v.check_solid(f"{name} support rib +X edge", cx + CRADLE_OR - 1.0, CRADLE_CENTER_Y, mid_z,
                  f"solid near {name} support rib +X edge")

# --- Cradle semicircles ---
for name, cx in CRADLES.items():
    # Solid in cradle wall at bottom (6 o'clock position)
    # Bottom of arc outer: Z = CRADLE_CENTER_Z - CRADLE_OR = 34.30 - 20.75 = 13.55
    # Bottom of arc inner: Z = CRADLE_CENTER_Z - CRADLE_IR = 34.30 - 17.75 = 16.55
    # Midpoint of wall at bottom: Z = (13.55 + 16.55) / 2 = 15.05
    v.check_solid(f"{name} arc wall bottom", cx, CRADLE_CENTER_Y, 15.05,
                  f"solid in {name} cradle wall at 6 o'clock")
    # Void inside cradle (inner cavity at center height)
    # At center Z, inside the inner radius
    v.check_void(f"{name} arc interior center", cx, CRADLE_CENTER_Y, CRADLE_CENTER_Z - 5.0,
                 f"void inside {name} cradle cavity")
    # Solid in cradle wall at 9 o'clock (left arm) - probe slightly below center
    # At Z = CRADLE_CENTER_Z - 1 (just below the cut plane)
    v.check_solid(f"{name} arc wall 9 o'clock", cx - CRADLE_IR - CRADLE_WALL / 2,
                  CRADLE_CENTER_Y, CRADLE_CENTER_Z - 1.0,
                  f"solid in {name} cradle wall at 9 o'clock")
    # Solid in cradle wall at 3 o'clock (right arm)
    v.check_solid(f"{name} arc wall 3 o'clock", cx + CRADLE_IR + CRADLE_WALL / 2,
                  CRADLE_CENTER_Y, CRADLE_CENTER_Z - 1.0,
                  f"solid in {name} cradle wall at 3 o'clock")
    # Void above cradle (top is open)
    v.check_void(f"{name} open top", cx, CRADLE_CENTER_Y, CRADLE_CENTER_Z + CRADLE_OR + 1.0,
                 f"void above {name} cradle (open top)")
    # Void outside cradle laterally
    v.check_void(f"{name} void outside +X", cx + CRADLE_OR + 1.0, CRADLE_CENTER_Y, CRADLE_CENTER_Z,
                 f"void outside {name} cradle +X")

# --- Bounding box ---
bb = result.val().BoundingBox()
# X: leftmost = P1-L -X rib tip = 18.48 - 4.0 - 4.0 = 10.48
# X: rightmost = P2-R +X rib tip = 141.53 + 4.0 + 4.0 = 149.53
# But cradles extend further: Cradle 2 right = 116.80 + 20.75 = 137.55
# So X min from bosses: 10.48, from cradles: 43.20 - 20.75 = 22.45 => min is 10.48
# X max from bosses: 149.53, from cradles: 137.55 => max is 149.53
EXPECTED_XMIN = 10.48
EXPECTED_XMAX = 149.53
# Y: bosses at 83.00, ribs extend +/-4mm from boss surface +/-4mm radius = 79.00 to 87.00
# Cradles at Y: 109.00 to 124.00
EXPECTED_YMIN = 75.00  # boss Y - boss_r - rib_radial = 83 - 4 - 4
EXPECTED_YMAX = 124.00  # cradle Y max
# Z: floor 3.00 to cradle arc bottom outer = 3.00 at bottom
# Top: cradle arm tips at Z = 34.30 (arms cut at center, so max Z = 34.30)
# Actually arms go to CRADLE_CENTER_Z = 34.30 (we cut above that)
# Boss top = 34.30
EXPECTED_ZMIN = 3.00
EXPECTED_ZMAX = 34.30

v.check_bbox("X", bb.xmin, bb.xmax, EXPECTED_XMIN, EXPECTED_XMAX, tol=0.6)
v.check_bbox("Y", bb.ymin, bb.ymax, EXPECTED_YMIN, EXPECTED_YMAX, tol=0.6)
v.check_bbox("Z", bb.zmin, bb.zmax, EXPECTED_ZMIN, EXPECTED_ZMAX, tol=0.6)

# --- Solid integrity ---
v.check_valid()
# Note: multiple bodies expected (bosses + cradles are separate), so skip single body check
# Instead check volume
# Rough volume estimate:
# 4 bosses: pi * 4^2 * 31.30 = ~1577 mm^3
# 16 ribs: 16 * 2 * 4 * 31.30 = ~4006 mm^3
# 4 pilot holes: -4 * pi * 2^2 * 7 = ~-352 mm^3
# 2 support ribs: 2 * 41.50 * 15 * 13.55 = ~16859 mm^3
# 2 semicircle walls: 2 * pi * (20.75^2 - 17.75^2) / 2 * 15 = 2 * pi * 115.5 / 2 * 15 = ~5443 mm^3
# Total rough: ~27533 mm^3
# Envelope: 160 * 155 * 72 = 1,785,600 (way too big, use feature-based)
envelope_est = 30000  # rough estimate
v.check_volume(expected_envelope=envelope_est, fill_range=(0.5, 1.5))

# --- Summary ---
print()
if not v.summary():
    sys.exit(1)

# ============================================================
# Export STEP
# ============================================================

step_path = str(Path(__file__).with_suffix(".step"))
cq.exporters.export(result, step_path)
print(f"\nSTEP exported to: {step_path}")
