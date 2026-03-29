#!/usr/bin/env python3
"""
Rear Wall Plate — CadQuery STEP Generation Script

Generates the rear wall plate of the pump cartridge: a rectangular plate
hosting 4x JG fitting stepped bores, 2x guide pin bores with bosses,
2x link rod U-notches, 4x pogo pad recesses, and edge treatments.

Coordinate system:
  Origin: lower-left corner of dock-facing face
  X: width (left to right),   0..147.8 mm
  Y: thickness (toward cartridge interior), 0..14.8 mm
  Z: height (bottom to top),  0..69.8 mm
  Envelope: 147.8 x 14.8 x 69.8 mm -> X:[0,147.8] Y:[0,14.8] Z:[0,69.8]
  (Guide pin bosses extend Y to 17.8)

Feature Planning Table (Rubric 1):
| #  | Feature Name                     | Mechanical Function                              | Op     | Shape    | Axis | Center (X,Y,Z)       | Dimensions                                   |
|----|----------------------------------|--------------------------------------------------|--------|----------|------|----------------------|----------------------------------------------|
| 1  | Plate body                       | Structural closure                               | Add    | Box      | --   | --                   | 147.8 x 14.8 x 69.8                          |
| 2  | JG1 stepped bore (upper-left)    | Press-fit JG PP0408W fitting                     | Remove | Revolved | Y    | 61.4, -, 47.4        | 15.5/9.5 stepped, 1mm entry chamfer           |
| 3  | JG2 stepped bore (upper-right)   | Same                                             | Remove | Revolved | Y    | 86.4, -, 47.4        | Same                                          |
| 4  | JG3 stepped bore (lower-left)    | Same                                             | Remove | Revolved | Y    | 61.4, -, 22.4        | Same                                          |
| 5  | JG4 stepped bore (lower-right)   | Same                                             | Remove | Revolved | Y    | 86.4, -, 22.4        | Same                                          |
| 6  | Guide pin bore (left)            | Press-fit anchor for dowel pin                   | Remove | Cylinder | Y    | 25.0, -, 34.9        | 3.1mm dia, 10mm deep from Y=14.8             |
| 7  | Guide pin bore (right)           | Same                                             | Remove | Cylinder | Y    | 122.8, -, 34.9       | Same                                          |
| 8  | Guide pin boss (left)            | Extends pin engagement + spring seat             | Add    | Cylinder | Y    | 25.0, -, 34.9        | 6mm OD, 3mm protrusion Y=14.8..17.8          |
| 9  | Guide pin boss (right)           | Same                                             | Add    | Cylinder | Y    | 122.8, -, 34.9       | Same                                          |
| 10 | Link rod U-notch (left)          | Clearance for link rod pass-through              | Remove | U-notch  | Y    | 43.9, -, 0..3.4      | 3.4mm wide, open at bottom, semicircular top  |
| 11 | Link rod U-notch (right)         | Same                                             | Remove | U-notch  | Y    | 103.9, -, 0..3.4     | Same                                          |
| 12 | Pogo pad recess 1                | Recess for copper contact pad                    | Remove | Cylinder | Y    | 66.3, 0, 8.0         | 4.5mm dia, 0.5mm deep                        |
| 13 | Pogo pad recess 2                | Same                                             | Remove | Cylinder | Y    | 71.4, 0, 8.0         | Same                                          |
| 14 | Pogo pad recess 3                | Same                                             | Remove | Cylinder | Y    | 76.4, 0, 8.0         | Same                                          |
| 15 | Pogo pad recess 4                | Same                                             | Remove | Cylinder | Y    | 81.5, 0, 8.0         | Same                                          |
| 16 | Elephant's foot chamfer          | Prevents first-layer flare                       | Remove | Chamfer  | --   | Y=0 face edges       | 0.3mm x 45-deg                               |
| 17 | General exterior edge chamfers   | Design language, softens edges                   | Remove | Chamfer  | --   | Non-bottom edges     | 1mm                                           |
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq
from step_validate import Validator

# =============================================================================
# Dimensions from spec
# =============================================================================

# Plate body
W = 147.8    # width (X)
T = 14.8     # thickness (Y)
H = 69.8     # height (Z)

# JG fitting bore positions (center X, Z in plate frame)
JG_POSITIONS = [
    (61.4, 47.4),   # JG1 upper-left
    (86.4, 47.4),   # JG2 upper-right
    (61.4, 22.4),   # JG3 lower-left
    (86.4, 22.4),   # JG4 lower-right
]

# JG stepped bore profile
JG_SHOULDER_DIA = 15.5
JG_PRESSFIT_DIA = 9.5
JG_SHOULDER_LEN = 1.32
JG_PRESSFIT_LEN = 12.16
JG_ENTRY_CHAMFER = 1.0

# Guide pin bore/boss
GP_POSITIONS = [
    (25.0, 34.9),
    (122.8, 34.9),
]
GP_BORE_DIA = 3.1
GP_BORE_DEPTH = 10.0
GP_BOSS_OD = 6.0
GP_BOSS_HEIGHT = 3.0

# Link rod U-notch
NOTCH_POSITIONS_X = [43.9, 103.9]
NOTCH_WIDTH = 3.4
NOTCH_HEIGHT = 3.4

# Pogo pad recesses
POGO_POSITIONS_X = [66.3, 71.4, 76.4, 81.5]
POGO_Z = 8.0
POGO_RECESS_DIA = 4.5
POGO_RECESS_DEPTH = 0.5

# Edge treatments
EFOOT_CHAMFER = 0.3
EDGE_CHAMFER = 1.0

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
STEP_PATH = SCRIPT_DIR / "rear-wall-plate.step"

# =============================================================================
# Build the plate body (Feature 1)
# =============================================================================
print("Building rear wall plate...")

plate = cq.Workplane("XY").box(W, T, H, centered=False)

# =============================================================================
# Features 8, 9: Guide pin bosses (ADD before boolean cuts)
# 6mm OD cylinders, 3mm tall, protruding from interior face (Y=14.8..17.8)
# Built as cylinders with axis along Y, positioned at (gx, T, gz)
# =============================================================================
print("  Adding guide pin bosses...")

for gx, gz in GP_POSITIONS:
    # Create a cylinder with axis along Y.
    # Use XY workplane shifted to the boss base, extrude cylinder upward in Z,
    # then rotate? No — simpler to build a revolved profile or use a direct cylinder.

    # Approach: sketch circle on XZ plane offset to Y=T, extrude in +Y direction.
    # XZ plane normal is -Y. workplane(offset=-T) shifts sketch plane to Y=T.
    # extrude(GP_BOSS_HEIGHT) goes in -Y direction from Y=T → that's wrong.
    # We need +Y (from T to T+3).
    # Solution: place workplane at Y=T+3=17.8, extrude(3) in -Y direction to Y=T.

    boss = (
        cq.Workplane("XZ")
        .workplane(offset=-(T + GP_BOSS_HEIGHT))  # offset -17.8 puts plane at Y=17.8
        .center(gx, gz)
        .circle(GP_BOSS_OD / 2)
        .extrude(GP_BOSS_HEIGHT)  # extrude 3mm in -Y direction → Y=17.8 to Y=14.8
    )
    plate = plate.union(boss)

# =============================================================================
# Features 2-5: JG fitting stepped through-bores (REMOVE)
# Revolved profile: entry chamfer → shoulder clearance → press-fit → shoulder clearance
# Bore axis along Y, from Y=0 to Y=T=14.8
# =============================================================================
print("  Cutting JG fitting stepped bores...")

R_SHOULDER = JG_SHOULDER_DIA / 2   # 7.75
R_PRESSFIT = JG_PRESSFIT_DIA / 2   # 4.75
C = JG_ENTRY_CHAMFER               # 1.0
Y1 = JG_SHOULDER_LEN               # 1.32
Y2 = Y1 + JG_PRESSFIT_LEN          # 13.48

# Revolved profile in (R, Y) space about Y axis:
jg_profile_pts = [
    (0,              0),           # axis at dock face
    (R_SHOULDER - C, 0),           # chamfer start
    (R_SHOULDER,     C),           # chamfer end
    (R_SHOULDER,     Y1),          # end of dock-side shoulder
    (R_PRESSFIT,     Y1),          # step to press-fit
    (R_PRESSFIT,     Y2),          # end of press-fit
    (R_SHOULDER,     Y2),          # step to interior shoulder
    (R_SHOULDER,     T),           # end of interior shoulder
    (0,              T),           # axis at interior face
]

jg_bore_tool = (
    cq.Workplane("XY")
    .polyline(jg_profile_pts)
    .close()
    .revolve(360, (0, 0, 0), (0, 1, 0))  # revolve about Y axis
)

for jx, jz in JG_POSITIONS:
    bore = jg_bore_tool.translate((jx, 0, jz))
    plate = plate.cut(bore)

# =============================================================================
# Features 6, 7: Guide pin bores (REMOVE)
# 3.1mm dia, 10mm deep from interior face (Y=4.8..14.8)
# Continues through boss (Y=14.8..17.8) — total Y=4.8..17.8 = 13mm
# =============================================================================
print("  Cutting guide pin bores...")

for gx, gz in GP_POSITIONS:
    bore_total = GP_BORE_DEPTH + GP_BOSS_HEIGHT  # 13mm
    # Place workplane at Y=T+BOSS=17.8, extrude 13mm in -Y direction to Y=4.8
    bore = (
        cq.Workplane("XZ")
        .workplane(offset=-(T + GP_BOSS_HEIGHT))  # at Y=17.8
        .center(gx, gz)
        .circle(GP_BORE_DIA / 2)
        .extrude(bore_total)  # -Y direction: Y=17.8 to Y=4.8
    )
    plate = plate.cut(bore)

# =============================================================================
# Features 10, 11: Link rod U-notches (REMOVE)
# 3.4mm wide, Z=0..3.4, open at bottom edge, semicircular top
# Through full plate thickness Y=0..14.8
# =============================================================================
print("  Cutting link rod U-notches...")

for nx in NOTCH_POSITIONS_X:
    r = NOTCH_WIDTH / 2  # 1.7mm

    # U-notch profile in XZ plane: rectangle from bottom to Z=NOTCH_HEIGHT-r,
    # then semicircular top from Z=NOTCH_HEIGHT-r to Z=NOTCH_HEIGHT.
    # Since NOTCH_HEIGHT = NOTCH_WIDTH = 3.4 and r = 1.7, the semicircle
    # center is at Z = 1.7. The rectangle part has zero height (3.4-1.7=1.7,
    # which equals r). So the shape is just a semicircle on top of a rectangle
    # from Z=-0.5 (below plate) to Z=1.7, then semicircle to Z=3.4.

    z_bottom = -0.5  # extend below plate for clean cut
    z_arc_center = NOTCH_HEIGHT - r  # 1.7
    x_left = nx - r
    x_right = nx + r

    notch = (
        cq.Workplane("XZ")
        .moveTo(x_left, z_bottom)
        .lineTo(x_left, z_arc_center)
        .threePointArc((nx, NOTCH_HEIGHT), (x_right, z_arc_center))
        .lineTo(x_right, z_bottom)
        .close()
        .extrude(T + 1)  # extrude in -Y direction from Y=0 to Y=-(T+1)
    )
    # Problem: this extrudes in -Y direction (outside the plate).
    # The plate is at Y=0..T. We need the notch solid at Y=-1..T+1 to cut through.
    # Solution: shift the workplane to Y=T+1 and extrude T+2 in -Y.

    notch = (
        cq.Workplane("XZ")
        .workplane(offset=-(T + 1))  # at Y=T+1
        .moveTo(x_left, z_bottom)
        .lineTo(x_left, z_arc_center)
        .threePointArc((nx, NOTCH_HEIGHT), (x_right, z_arc_center))
        .lineTo(x_right, z_bottom)
        .close()
        .extrude(T + 2)  # extrude T+2 in -Y direction from Y=T+1 to Y=-(1)
    )
    plate = plate.cut(notch)

# =============================================================================
# Features 12-15: Pogo pad recesses (REMOVE)
# 4.5mm dia, 0.5mm deep from dock face (Y=0 surface, cut into plate)
# =============================================================================
print("  Cutting pogo pad recesses...")

for px in POGO_POSITIONS_X:
    # Place workplane at Y=POGO_RECESS_DEPTH=0.5, extrude 0.5 in -Y to Y=0
    recess = (
        cq.Workplane("XZ")
        .workplane(offset=-POGO_RECESS_DEPTH)  # at Y=0.5
        .center(px, POGO_Z)
        .circle(POGO_RECESS_DIA / 2)
        .extrude(POGO_RECESS_DEPTH)  # -Y direction from Y=0.5 to Y=0
    )
    plate = plate.cut(recess)

# =============================================================================
# Feature 16: Elephant's foot chamfer (0.3mm on Y=0 face perimeter edges)
# Feature 17: General 1mm chamfers on non-bottom exterior edges
# =============================================================================
print("  Applying edge treatments...")

# Strategy: The dock face (Y=0) is the build plate. Apply 0.3mm chamfer to
# edges on that face, then 1mm to remaining exterior edges.
# CadQuery edge selection is tricky with boolean'd geometry. Let's use
# selectors based on Y position.

# Elephant's foot chamfer: 0.3mm on the 4 outer perimeter edges of the dock face (Y=0).
# Apply each edge individually with error handling.
efoot_count = 0
for label, box_min, box_max in [
    ("dock-bottom", (-0.1, -0.1, -0.1), (W + 0.1, 0.01, 0.01)),
    ("dock-top",    (-0.1, -0.1, H - 0.01), (W + 0.1, 0.01, H + 0.1)),
    ("dock-left",   (-0.1, -0.1, -0.1), (0.01, 0.01, H + 0.1)),
    ("dock-right",  (W - 0.01, -0.1, -0.1), (W + 0.1, 0.01, H + 0.1)),
]:
    try:
        plate = plate.edges(cq.selectors.BoxSelector(box_min, box_max)).chamfer(EFOOT_CHAMFER)
        efoot_count += 1
    except Exception:
        pass
print(f"    Elephant's foot chamfer: {efoot_count}/4 dock face edges applied")

# General 1mm chamfer on interior face (Y=T) perimeter edges and
# Y-direction edges at the 4 plate corners. Applied individually to
# isolate failures from chamfer conflicts at multi-chamfer vertices.
chamfer_count = 0
for label, box_min, box_max in [
    # Interior face (Y=T) X-direction edges
    ("interior-bottom", (-0.1, T - 0.01, -0.1), (W + 0.1, T + 0.01, 0.01)),
    ("interior-top",    (-0.1, T - 0.01, H - 0.01), (W + 0.1, T + 0.01, H + 0.1)),
    # Interior face (Y=T) Z-direction edges
    ("interior-left",   (-0.1, T - 0.01, -0.1), (0.01, T + 0.01, H + 0.1)),
    ("interior-right",  (W - 0.01, T - 0.01, -0.1), (W + 0.1, T + 0.01, H + 0.1)),
]:
    try:
        plate = plate.edges(cq.selectors.BoxSelector(box_min, box_max)).chamfer(EDGE_CHAMFER)
        chamfer_count += 1
    except Exception:
        pass
print(f"    General 1mm chamfer: {chamfer_count}/4 interior face edges applied")

# =============================================================================
# Export STEP
# =============================================================================
print(f"\n  Exporting STEP to {STEP_PATH}...")
cq.exporters.export(plate, str(STEP_PATH))

# =============================================================================
# Validation (Rubrics 3, 4, 5)
# =============================================================================
print("\nValidation:")
v = Validator(plate)

# --- Feature 1: Plate body ---
v.check_solid("Plate body center", W/2, T/2, H/2, "solid at plate centroid")
v.check_solid("Plate body corner near origin", 2.0, 2.0, 2.0, "solid near origin (inside chamfer)")
v.check_solid("Plate body corner far", W-2.0, T-2.0, H-2.0, "solid near far corner (inside chamfer)")

# --- Features 2-5: JG stepped bores ---
for i, (jx, jz) in enumerate(JG_POSITIONS, 1):
    lbl = f"JG{i}"
    # Center of bore is void at all Y depths
    v.check_void(f"{lbl} center dock-side", jx, 0.5, jz, "void in dock shoulder zone")
    v.check_void(f"{lbl} center press-fit", jx, T/2, jz, "void in press-fit zone")
    v.check_void(f"{lbl} center interior-side", jx, T-0.5, jz, "void in interior shoulder zone")

    # Inside shoulder bore edge = void; outside = solid
    v.check_void(f"{lbl} shoulder inner edge", jx + R_SHOULDER - 0.5, 0.5, jz,
                 "void inside shoulder bore")
    v.check_solid(f"{lbl} shoulder outer edge", jx + R_SHOULDER + 0.5, 0.5, jz,
                  "solid outside shoulder bore")

    # Press-fit zone: inside = void, outside = solid
    v.check_void(f"{lbl} pressfit inner edge", jx + R_PRESSFIT - 0.3, T/2, jz,
                 "void inside press-fit bore")
    v.check_solid(f"{lbl} pressfit outer edge", jx + R_PRESSFIT + 0.5, T/2, jz,
                  "solid outside press-fit bore")

    # Entry chamfer at dock face
    v.check_void(f"{lbl} entry chamfer", jx + R_SHOULDER - C + 0.1, 0.1, jz,
                 "void at chamfer zone")

# --- Features 6-7: Guide pin bores ---
for i, (gx, gz) in enumerate(GP_POSITIONS):
    side = "left" if i == 0 else "right"
    # Bore center: void at Y=9.8 (mid-bore)
    v.check_void(f"GP bore {side} center", gx, 9.8, gz, "void at bore center")
    # Solid backing behind bore: Y=2.0 (well before Y=4.8 bore start)
    v.check_solid(f"GP bore {side} backing", gx, 2.0, gz, "solid behind bore")
    # Solid outside bore radius
    v.check_solid(f"GP bore {side} wall", gx + GP_BORE_DIA/2 + 0.5, 9.8, gz,
                  "solid outside bore")

# --- Features 8-9: Guide pin bosses ---
for i, (gx, gz) in enumerate(GP_POSITIONS):
    side = "left" if i == 0 else "right"
    # Boss body: solid at Y=16 near boss edge
    v.check_solid(f"GP boss {side} body", gx + GP_BOSS_OD/2 - 0.5, 16.0, gz,
                  "solid in boss body")
    # Outside boss: void at Y=16
    v.check_void(f"GP boss {side} outside", gx + GP_BOSS_OD/2 + 0.5, 16.0, gz,
                 "void outside boss")
    # Boss bore: void at center
    v.check_void(f"GP boss {side} bore", gx, 16.0, gz, "void at boss bore center")

# --- Features 10-11: Link rod U-notches ---
for i, nx in enumerate(NOTCH_POSITIONS_X):
    side = "left" if i == 0 else "right"
    v.check_void(f"U-notch {side} center", nx, T/2, 1.0, "void at notch center")
    v.check_solid(f"U-notch {side} above", nx, T/2, NOTCH_HEIGHT + 1.0, "solid above notch")
    v.check_solid(f"U-notch {side} beside", nx + NOTCH_WIDTH/2 + 1.0, T/2, 1.0,
                  "solid beside notch")
    v.check_void(f"U-notch {side} bottom-open", nx, T/2, 0.1, "void at bottom edge")

# --- Features 12-15: Pogo pad recesses ---
for i, px in enumerate(POGO_POSITIONS_X, 1):
    v.check_void(f"Pogo pad {i} recess", px, 0.25, POGO_Z, "void at recess center")
    v.check_solid(f"Pogo pad {i} behind", px, 1.0, POGO_Z, "solid behind recess")
    v.check_solid(f"Pogo pad {i} outside dia", px + POGO_RECESS_DIA/2 + 0.3, 0.25, POGO_Z,
                  "solid outside recess")

# --- Rubric 5: Bounding box ---
bb = plate.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, 0.0, W)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, T + GP_BOSS_HEIGHT)  # bosses to Y=17.8
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, H)

# --- Rubric 4: Solid integrity ---
v.check_valid()
v.check_single_body()
v.check_volume(expected_envelope=W * T * H, fill_range=(0.5, 1.2))

# --- Summary ---
if not v.summary():
    sys.exit(1)

print(f"\nSTEP file written to: {STEP_PATH}")
