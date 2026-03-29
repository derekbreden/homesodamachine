#!/usr/bin/env python3
"""
Sub-E Guide Post Array — CadQuery Generation Script

Generates 4 guide posts with mushroom cap stops as a standalone union solid.
Posts project from Y=0 in the -Y direction.

Coordinate system:
  Origin: rear wall exterior face at lower-left post corner reference
  X: tray width axis (post positions at X=60 and X=100)
  Y: depth axis. Y=0 is rear wall face. Posts project into -Y.
  Z: tray height axis (post positions at Z=17.5 and Z=57.5)
  Envelope: ~44.5 x 25 x 44.5 mm (bounding box around posts + caps)

Feature Planning Table:
+----+-------------------+------------------------------------+-----------+----------+------+--------------------------+----------------------------+----------------------------+
| #  | Feature Name      | Mechanical Function                | Operation | Shape    | Axis | Center Position (X,Y,Z)  | Dimensions                 | Notes                      |
+----+-------------------+------------------------------------+-----------+----------+------+--------------------------+----------------------------+----------------------------+
| 1  | Guide Post P1     | Constrains release plate Y-travel  | Add       | Cylinder | Y    | (60, -12.25, 17.5)       | 3.5 dia x 24.5 long       | Base at Y=0, tip at Y=-24.5|
| 2  | Guide Post P2     | Constrains release plate Y-travel  | Add       | Cylinder | Y    | (100, -12.25, 17.5)      | 3.5 dia x 24.5 long       | Base at Y=0, tip at Y=-24.5|
| 3  | Guide Post P3     | Constrains release plate Y-travel  | Add       | Cylinder | Y    | (60, -12.25, 57.5)       | 3.5 dia x 24.5 long       | Base at Y=0, tip at Y=-24.5|
| 4  | Guide Post P4     | Constrains release plate Y-travel  | Add       | Cylinder | Y    | (100, -12.25, 57.5)      | 3.5 dia x 24.5 long       | Base at Y=0, tip at Y=-24.5|
| 5  | Mushroom Cap C1   | Retains release plate on post P1   | Add       | Revolved | Y    | (60, -24.75, 17.5)       | 4.5 OD x 0.5 h + chamfer  | 45deg chamfer at tip       |
| 6  | Mushroom Cap C2   | Retains release plate on post P2   | Add       | Revolved | Y    | (100, -24.75, 17.5)      | 4.5 OD x 0.5 h + chamfer  | 45deg chamfer at tip       |
| 7  | Mushroom Cap C3   | Retains release plate on post P3   | Add       | Revolved | Y    | (60, -24.75, 57.5)       | 4.5 OD x 0.5 h + chamfer  | 45deg chamfer at tip       |
| 8  | Mushroom Cap C4   | Retains release plate on post P4   | Add       | Revolved | Y    | (100, -24.75, 57.5)      | 4.5 OD x 0.5 h + chamfer  | 45deg chamfer at tip       |
+----+-------------------+------------------------------------+-----------+----------+------+--------------------------+----------------------------+----------------------------+
"""

import sys
from pathlib import Path

# Add tools/ to path for step_validate
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq
from step_validate import Validator

# ==============================================================
# Dimensions from spec
# ==============================================================

POST_DIA = 3.5          # mm, guide post diameter
POST_R = POST_DIA / 2   # 1.75 mm
POST_LENGTH = 24.5       # mm, base (Y=0) to cap start (Y=-24.5)

CAP_OD = 4.5            # mm, mushroom cap outer diameter
CAP_R = CAP_OD / 2      # 2.25 mm
CAP_HEIGHT = 0.5         # mm, cap disc height
CHAMFER_HEIGHT = 0.5     # mm, 45-degree chamfer on cap tip face
CHAMFER_RADIAL = 0.5     # mm, chamfer removes this much radially (45 deg => equal to height)

TOTAL_LENGTH = POST_LENGTH + CAP_HEIGHT  # 25.0 mm (Y=0 to Y=-25)

# Post positions in XZ (tray frame)
POST_POSITIONS = [
    (60.0, 17.5),   # P1 lower-left
    (100.0, 17.5),  # P2 lower-right
    (60.0, 57.5),   # P3 upper-left
    (100.0, 57.5),  # P4 upper-right
]

# ==============================================================
# Build one post + mushroom cap as a revolved profile
# ==============================================================
# Profile cross-section in the RY plane (R = radial distance from axis, Y = axial position)
# The post axis is along Y. The post base is at Y=0, tip at Y=-25.
# We revolve around the Y axis (R=0 line).
#
# Profile points (R, Y), going clockwise from axis at base:
#   - Start at axis, base face:          (0, 0)
#   - Post OD at base:                   (POST_R, 0)
#   - Post OD at cap transition:         (POST_R, -POST_LENGTH)    = (1.75, -24.5)
#   - Cap OD at wall-facing edge:        (CAP_R, -POST_LENGTH)     = (2.25, -24.5)
#   - Cap OD at start of chamfer:        (CAP_R, -POST_LENGTH - (CAP_HEIGHT - CHAMFER_HEIGHT))
#                                         = (2.25, -24.5) since CAP_HEIGHT == CHAMFER_HEIGHT, no flat section
#   - Chamfer tip (post axis radius):    (CAP_R - CHAMFER_RADIAL, -TOTAL_LENGTH)  = (1.75, -25.0)
#   - Axis at tip:                       (0, -TOTAL_LENGTH)        = (0, -25.0)
#
# Since CAP_HEIGHT == CHAMFER_HEIGHT (both 0.5mm), the entire cap face is chamfered.
# The cap profile goes: straight wall at CAP_R from Y=-24.5 to... actually there's no flat.
# It goes: step out to CAP_R at Y=-24.5, then immediately chamfer down to POST_R at Y=-25.

cap_chamfer_start_y = -POST_LENGTH  # Y = -24.5
cap_tip_y = -TOTAL_LENGTH           # Y = -25.0

profile_pts = [
    (0,      0),                           # Axis at base
    (POST_R, 0),                           # Post OD at base
    (POST_R, -POST_LENGTH),                # Post OD at cap transition (Y=-24.5)
    (CAP_R,  -POST_LENGTH),                # Cap OD step-out (Y=-24.5)
    (POST_R, cap_tip_y),                   # Chamfer narrows back to post radius at tip (Y=-25)
    (0,      cap_tip_y),                   # Axis at tip
]

# Build one post+cap by revolving the profile around the Y axis
single_post = (
    cq.Workplane("XY")
    .polyline(profile_pts)
    .close()
    .revolve(360, (0, 0), (0, 1))  # Revolve around Y axis
)

# ==============================================================
# Place 4 posts at their XZ positions (union into one solid)
# ==============================================================

result = None
for (px, pz) in POST_POSITIONS:
    placed = single_post.translate((px, 0, pz))
    if result is None:
        result = placed
    else:
        result = result.union(placed)

# ==============================================================
# Export STEP
# ==============================================================

output_path = Path(__file__).with_suffix(".step")
cq.exporters.export(result, str(output_path))
print(f"STEP exported: {output_path}")

# ==============================================================
# Validation
# ==============================================================

print("\n--- Validation ---\n")
v = Validator(result)

# --- Feature probes: Guide Posts (check solid at midpoint of each post shaft) ---
for i, (px, pz) in enumerate(POST_POSITIONS):
    label = f"P{i+1}"
    mid_y = -POST_LENGTH / 2  # Y = -12.25 (midpoint of shaft)

    # Post center should be solid
    v.check_solid(f"{label} shaft center", px, mid_y, pz,
                  f"solid at post {label} shaft center ({px}, {mid_y:.2f}, {pz})")

    # Just outside post radius should be void (confirms diameter)
    v.check_void(f"{label} outside shaft X+", px + POST_R + 0.3, mid_y, pz,
                 f"void outside post {label} shaft radius in X+")
    v.check_void(f"{label} outside shaft Z+", px, mid_y, pz + POST_R + 0.3,
                 f"void outside post {label} shaft radius in Z+")

    # Near base (Y = -0.25, just inside post) should be solid
    v.check_solid(f"{label} near base", px, -0.25, pz,
                  f"solid near post {label} base")

    # Near tip of shaft before cap (Y = -24.25) should be solid
    v.check_solid(f"{label} near shaft tip", px, -24.25, pz,
                  f"solid near post {label} shaft tip before cap")

# --- Feature probes: Mushroom Caps ---
for i, (px, pz) in enumerate(POST_POSITIONS):
    label = f"C{i+1}"
    cap_mid_y = -POST_LENGTH - CAP_HEIGHT / 2  # Y = -24.75

    # Cap center should be solid
    v.check_solid(f"{label} cap center", px, cap_mid_y, pz,
                  f"solid at cap {label} center ({px}, {cap_mid_y:.2f}, {pz})")

    # Cap overhang region: between post radius and cap radius, at cap transition Y
    # At Y = -24.5 (cap wall-facing face), at R = CAP_R - 0.1 from axis => should be solid
    overhang_offset = (CAP_R - 0.1)  # 2.15 mm from center
    # Probe slightly inside cap body (Y=-24.55) to avoid exact boundary face at Y=-24.5
    v.check_solid(f"{label} cap overhang X+", px + overhang_offset, -POST_LENGTH - 0.05, pz,
                  f"solid in cap {label} overhang at Y=-24.55")

    # Beyond cap radius should be void at cap level
    v.check_void(f"{label} outside cap X+", px + CAP_R + 0.3, cap_mid_y, pz,
                 f"void outside cap {label} OD")

    # Past the tip (Y = -25.3) should be void
    v.check_void(f"{label} past tip", px, -25.3, pz,
                 f"void past cap {label} tip")

    # Chamfer check: at the very tip Y=-25, at post radius (1.75mm), should be on boundary
    # Slightly inside post radius at tip should be solid
    v.check_solid(f"{label} chamfer inner at tip", px, -24.9, pz,
                  f"solid at chamfer inner region of cap {label}")

# --- Bounding box checks ---
bb = result.val().BoundingBox()
# X: 60 - CAP_R to 100 + CAP_R = 57.75 to 102.25
v.check_bbox("X", bb.xmin, bb.xmax, 60 - CAP_R, 100 + CAP_R)
# Y: -25 to 0
v.check_bbox("Y", bb.ymin, bb.ymax, -TOTAL_LENGTH, 0)
# Z: 17.5 - CAP_R to 57.5 + CAP_R = 15.25 to 59.75
v.check_bbox("Z", bb.zmin, bb.zmax, 17.5 - CAP_R, 57.5 + CAP_R)

# --- Solid integrity ---
v.check_valid()
# Posts are 4 physically disjoint cylinders (connected by tray body in final assembly).
# Standalone model has 4 separate bodies as expected.
n_bodies = len(result.solids().vals())
v._record("Body count (4 disjoint posts)", n_bodies == 4, f"{n_bodies} body(ies), expected 4")

# Volume estimate: 4 posts (cylinder) + 4 caps (small volume)
# Post vol = pi * 1.75^2 * 24.5 = ~235.6 mm^3 each, x4 = ~942 mm^3
# Cap vol is small. Envelope for volume check:
# Envelope = (102.25 - 57.75) * 25 * (59.75 - 15.25) = 44.5 * 25 * 44.5 = ~49,506 mm^3
envelope = (100 + CAP_R - (60 - CAP_R)) * TOTAL_LENGTH * (57.5 + CAP_R - (17.5 - CAP_R))
v.check_volume(expected_envelope=envelope, fill_range=(0.01, 0.10))
# Posts are thin cylinders in a large envelope, so fill ratio is very low (~2%)

# --- Summary ---
print()
if not v.summary():
    sys.exit(1)
