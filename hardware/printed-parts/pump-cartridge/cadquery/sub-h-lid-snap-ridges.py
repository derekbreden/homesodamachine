"""
Sub-H: Lid Snap Detent Ridges — CadQuery Generation Script

Generates 8 triangular-profile ridges on the interior faces of tray side walls.
4 ridges per side, symmetric about X=80 mm centerline.

Coordinate system:
  Origin: rear-left-bottom corner of tray
  X: width, 0..160 mm (left to right)
  Y: depth, 0..155 mm (rear to front)
  Z: height, 0..72 mm (bottom to top)
  Sub-H envelope: X=[5,6] and [154,155], Y per ridge 6mm, Z=[69.5,71.5]

Feature Planning Table:
| # | Feature Name         | Function              | Op  | Shape       | Axis | Center (X,Y,Z)      | Dimensions              | Notes                    |
|---|----------------------|-----------------------|-----|-------------|------|----------------------|-------------------------|--------------------------|
| 1 | Left ridge L1        | Lid snap retention    | Add | Tri prism   | Y    | (5.5, 20, 70.5)     | 1x2x6 (prot x ht x len)| Protrudes +X from X=5    |
| 2 | Left ridge L2        | Lid snap retention    | Add | Tri prism   | Y    | (5.5, 60, 70.5)     | 1x2x6                   | Protrudes +X from X=5    |
| 3 | Left ridge L3        | Lid snap retention    | Add | Tri prism   | Y    | (5.5, 100, 70.5)    | 1x2x6                   | Protrudes +X from X=5    |
| 4 | Left ridge L4        | Lid snap retention    | Add | Tri prism   | Y    | (5.5, 140, 70.5)    | 1x2x6                   | Protrudes +X from X=5    |
| 5 | Right ridge R1       | Lid snap retention    | Add | Tri prism   | Y    | (154.5, 20, 70.5)   | 1x2x6                   | Protrudes -X from X=155  |
| 6 | Right ridge R2       | Lid snap retention    | Add | Tri prism   | Y    | (154.5, 60, 70.5)   | 1x2x6                   | Protrudes -X from X=155  |
| 7 | Right ridge R3       | Lid snap retention    | Add | Tri prism   | Y    | (154.5, 100, 70.5)  | 1x2x6                   | Protrudes -X from X=155  |
| 8 | Right ridge R4       | Lid snap retention    | Add | Tri prism   | Y    | (154.5, 140, 70.5)  | 1x2x6                   | Protrudes -X from X=155  |
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq
from step_validate import Validator

# ── Parameters ──────────────────────────────────────────────────────

WALL_X_LEFT = 5.0       # Left wall interior face X
WALL_X_RIGHT = 155.0    # Right wall interior face X
PROTRUSION = 1.0        # Ridge protrusion from wall face (mm)
RIDGE_HEIGHT = 2.0      # Z extent: 69.5 to 71.5
RIDGE_LENGTH = 6.0      # Y extent per ridge
Z_BOTTOM = 69.5         # Bottom of ridge
Z_PEAK = 70.5           # Peak of triangular profile
Z_TOP = 71.5            # Top of ridge (start of ramp)

Y_CENTERS = [20.0, 60.0, 100.0, 140.0]  # Y center positions

# ── Build ridges ────────────────────────────────────────────────────

result = None

for y_center in Y_CENTERS:
    y_start = y_center - RIDGE_LENGTH / 2.0  # 3mm before center

    # Left ridge profile (XZ plane): vertices A, B, D, C
    # A(5.0, 71.5), B(6.0, 70.5), D(6.0, 69.5), C(5.0, 69.5)
    # Extrude along Y for RIDGE_LENGTH
    left_profile = (
        cq.Workplane("XZ")
        .moveTo(WALL_X_LEFT, Z_TOP)          # A
        .lineTo(WALL_X_LEFT + PROTRUSION, Z_PEAK)  # B
        .lineTo(WALL_X_LEFT + PROTRUSION, Z_BOTTOM)  # D
        .lineTo(WALL_X_LEFT, Z_BOTTOM)       # C
        .close()
        .extrude(-RIDGE_LENGTH)  # XZ normal is -Y; negative extrude goes +Y
    )
    # The extrude starts at Y=0 and goes to Y=RIDGE_LENGTH in +Y direction.
    # We need to translate to the correct Y position.
    left_ridge = left_profile.translate((0, y_start, 0))

    # Right ridge profile (mirrored): vertices A, B, D, C
    # A(155.0, 71.5), B(154.0, 70.5), D(154.0, 69.5), C(155.0, 69.5)
    right_profile = (
        cq.Workplane("XZ")
        .moveTo(WALL_X_RIGHT, Z_TOP)          # A
        .lineTo(WALL_X_RIGHT - PROTRUSION, Z_PEAK)  # B
        .lineTo(WALL_X_RIGHT - PROTRUSION, Z_BOTTOM)  # D
        .lineTo(WALL_X_RIGHT, Z_BOTTOM)       # C
        .close()
        .extrude(-RIDGE_LENGTH)  # goes +Y
    )
    right_ridge = right_profile.translate((0, y_start, 0))

    if result is None:
        result = left_ridge.union(right_ridge)
    else:
        result = result.union(left_ridge).union(right_ridge)

# ── Export STEP ─────────────────────────────────────────────────────

out_path = str(Path(__file__).with_suffix(".step"))
cq.exporters.export(result, out_path)
print(f"Exported STEP: {out_path}")

# ── Validation ──────────────────────────────────────────────────────

print("\n--- Validation ---")
v = Validator(result)

# Check each ridge: solid at center, solid at peak, void outside
for i, y_c in enumerate(Y_CENTERS):
    label_l = f"L{i+1}"
    label_r = f"R{i+1}"

    # Left ridges: protrude +X from X=5
    # Solid at ridge center
    v.check_solid(f"{label_l} center", 5.5, y_c, 70.5, f"solid at left ridge {label_l} center")
    # Solid at ramp mid-point (X=5.3, Z=71.2 — on the ramp slope)
    v.check_solid(f"{label_l} ramp solid", 5.2, y_c, 71.2, f"solid on {label_l} ramp face")
    # Solid at catch face (X=5.8, Z=69.8)
    v.check_solid(f"{label_l} catch face", 5.8, y_c, 69.8, f"solid at {label_l} catch face")
    # Void just outside protrusion (X=6.2)
    v.check_void(f"{label_l} outside protrusion", 6.2, y_c, 70.5, f"void outside {label_l} protrusion")
    # Void above ramp top (X=5.8, Z=71.8)
    v.check_void(f"{label_l} above ramp", 5.8, y_c, 71.8, f"void above {label_l} ramp")
    # Void below catch face (X=5.8, Z=69.2)
    v.check_void(f"{label_l} below catch", 5.8, y_c, 69.2, f"void below {label_l} catch face")
    # Check Y extent: solid at Y start+0.5, void at Y start-0.5
    y_start = y_c - 3.0
    y_end = y_c + 3.0
    v.check_solid(f"{label_l} Y start", 5.5, y_start + 0.5, 70.0, f"solid near {label_l} Y start")
    v.check_void(f"{label_l} Y before", 5.5, y_start - 0.5, 70.0, f"void before {label_l} Y start")
    v.check_solid(f"{label_l} Y end", 5.5, y_end - 0.5, 70.0, f"solid near {label_l} Y end")
    v.check_void(f"{label_l} Y after", 5.5, y_end + 0.5, 70.0, f"void after {label_l} Y end")

    # Right ridges: protrude -X from X=155
    v.check_solid(f"{label_r} center", 154.5, y_c, 70.5, f"solid at right ridge {label_r} center")
    v.check_solid(f"{label_r} ramp solid", 154.8, y_c, 71.2, f"solid on {label_r} ramp face")
    v.check_solid(f"{label_r} catch face", 154.2, y_c, 69.8, f"solid at {label_r} catch face")
    v.check_void(f"{label_r} outside protrusion", 153.8, y_c, 70.5, f"void outside {label_r} protrusion")
    v.check_void(f"{label_r} above ramp", 154.2, y_c, 71.8, f"void above {label_r} ramp")
    v.check_void(f"{label_r} below catch", 154.2, y_c, 69.2, f"void below {label_r} catch face")
    v.check_solid(f"{label_r} Y start", 154.5, y_start + 0.5, 70.0, f"solid near {label_r} Y start")
    v.check_void(f"{label_r} Y before", 154.5, y_start - 0.5, 70.0, f"void before {label_r} Y start")
    v.check_solid(f"{label_r} Y end", 154.5, y_end - 0.5, 70.0, f"solid near {label_r} Y end")
    v.check_void(f"{label_r} Y after", 154.5, y_end + 0.5, 70.0, f"void after {label_r} Y end")

# Bounding box checks
bb = result.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, 5.0, 155.0)
v.check_bbox("Y", bb.ymin, bb.ymax, 17.0, 143.0)
v.check_bbox("Z", bb.zmin, bb.zmax, 69.5, 71.5)

# Solid integrity
v.check_valid()
# 8 disjoint ridges cannot form a single body — they become one solid
# only when unioned with the tray shell (Sub-A). Verify exactly 8 bodies.
n_bodies = len(result.solids().vals())
v._record("Body count (8 ridges)", n_bodies == 8, f"{n_bodies} body(ies), expected 8")

# Volume: each ridge is a trapezoid cross-section extruded 6mm
# Cross-section area = triangle(1x1)/2 + rectangle(1x1) = 0.5 + 1.0 = 1.5 mm^2
# Per ridge volume = 1.5 * 6 = 9 mm^3
# 8 ridges = 72 mm^3
# Envelope for volume check: 150 * 126 * 2 = 37800 (very sparse)
# Use a tight fill range
v.check_volume(expected_envelope=72.0, fill_range=(0.8, 1.2))

# Summary
if not v.summary():
    sys.exit(1)
