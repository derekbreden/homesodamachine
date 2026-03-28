#!/usr/bin/env python3
"""
Enclosure Front Panel — CadQuery STEP Generator

Removable cosmetic panel covering the upper front face (enclosure Z=130 to Z=400).
Carries two display dock recesses, cable exit holes, four cantilever snap hooks,
and a bottom tongue for alignment with the tub's partial front wall groove.

Coordinate system:
  Origin: front-left-bottom corner of panel exterior face
  X: width, left to right [0, 220]
  Y: depth, front face (0) to interior face (4)
  Z: height, bottom (0 = enclosure Z=130) to top (270 = enclosure Z=400)
  Tongue extends below to Z=-3. Snap hooks extend beyond Y=4.
  Envelope: 220 x ~16 x 273 mm (including snap hooks and tongue)
"""

import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

import cadquery as cq
from step_validate import Validator

# ============================================================================
# RUBRIC 2 — Coordinate System Declaration
# ============================================================================
# Origin: front-left-bottom corner of panel exterior
# X: width [0, 220]
# Y: depth [0, 4] (panel body), snap hooks extend to ~16
# Z: height [0, 270] (bottom = enclosure Z=130), tongue extends to Z=-3

# ============================================================================
# DIMENSIONS
# ============================================================================

# Panel body
PANEL_W = 220.0       # X
PANEL_D = 4.0         # Y (wall thickness, matches tub)
PANEL_H = 270.0       # Z (Z=130 to Z=400 in enclosure coords)
CORNER_R = 6.0        # Vertical edge corner radius (plan view)

# Display dock recesses (from spatial layout)
# Recess 1: center at enclosure X=57, Z=275 → local X=57, Z=275-130=145
# Recess 2: center at enclosure X=163, Z=275 → local X=163, Z=145
DOCK_DIA = 50.0
DOCK_R = DOCK_DIA / 2.0   # 25.0
DOCK_DEPTH = 3.0           # From front face inward (leaves 1mm backing)
DOCK_CENTERS = [
    (57.0, 145.0),     # Left dock (X, Z in local coords)
    (163.0, 145.0),    # Right dock
]

# Cable exit holes (through remaining 1mm behind dock recess)
CABLE_HOLE_DIA = 8.0

# Bottom tongue (engages groove in tub front wall at Z=130)
TONGUE_HEIGHT = 3.0    # Extends below panel body (Z=-3 to Z=0)
TONGUE_DEPTH = 2.0     # Y dimension (centered in wall thickness)
TONGUE_WIDTH = PANEL_W  # Full panel width

# Snap hooks (4 cantilever tabs, 2 per side)
# Engage 12mm-wide x 3mm-deep x 8mm-tall receptacle slots in tub side walls
# Hook positions in local Z: enclosure Z=200→local 70, Z=340→local 210
HOOK_Z_POSITIONS = [70.0, 210.0]
HOOK_WIDTH_Z = 10.0     # Narrower than 12mm slot (clearance)
HOOK_LENGTH_Y = 12.0    # Extends from interior face into interior
HOOK_THICKNESS_X = 2.0  # Cantilever arm thickness
HOOK_TIP_HEIGHT = 1.5   # Hook tip protrusion (catches slot edge)
HOOK_TIP_DEPTH = 2.0    # Hook tip depth in Y
# Hook X positions: on panel side edges
# Left hooks at X=2 (wall interior face at X=4, hook extends from panel interior)
# Right hooks at X=218

# ============================================================================
# RUBRIC 1 — Feature Planning Table
# ============================================================================
print("=" * 80)
print("RUBRIC 1 — Feature Planning Table")
print("=" * 80)
features = [
    ("1",  "Panel body",              "Cosmetic front face",          "Add", "Box",      "Z",
     f"({PANEL_W/2}, {PANEL_D/2}, {PANEL_H/2})",
     f"{PANEL_W}x{PANEL_D}x{PANEL_H}mm, R={CORNER_R}mm corners"),
    ("2a", "Dock recess left",        "Display puck seat",            "Rem", "Cylinder", "Y",
     f"({DOCK_CENTERS[0][0]}, 0-{DOCK_DEPTH}, {DOCK_CENTERS[0][1]})",
     f"{DOCK_DIA}mm dia x {DOCK_DEPTH}mm deep"),
    ("2b", "Dock recess right",       "Display puck seat",            "Rem", "Cylinder", "Y",
     f"({DOCK_CENTERS[1][0]}, 0-{DOCK_DEPTH}, {DOCK_CENTERS[1][1]})",
     f"{DOCK_DIA}mm dia x {DOCK_DEPTH}mm deep"),
    ("3a", "Cable hole left",         "Cat6 cable pass-through",      "Rem", "Cylinder", "Y",
     f"({DOCK_CENTERS[0][0]}, 0-{PANEL_D}, {DOCK_CENTERS[0][1]})",
     f"{CABLE_HOLE_DIA}mm dia through"),
    ("3b", "Cable hole right",        "Cat6 cable pass-through",      "Rem", "Cylinder", "Y",
     f"({DOCK_CENTERS[1][0]}, 0-{PANEL_D}, {DOCK_CENTERS[1][1]})",
     f"{CABLE_HOLE_DIA}mm dia through"),
    ("4",  "Bottom tongue",           "Aligns in tub front wall groove","Add","Box",     "Z",
     f"(0-{PANEL_W}, Y centered, Z=-3..0)",
     f"{TONGUE_WIDTH}x{TONGUE_DEPTH}x{TONGUE_HEIGHT}mm"),
    ("5",  "Snap hooks x4",           "Engages tub wall receptacles", "Add", "L-tab",    "Y",
     "Side edges, Z=70 and Z=210",
     f"{HOOK_WIDTH_Z}x{HOOK_LENGTH_Y}x{HOOK_THICKNESS_X}mm + {HOOK_TIP_HEIGHT}mm tip"),
]
for row in features:
    num, name, func, op, shape, axis, pos, dims = row
    print(f"  {num:<4} {name:<28} {func:<30} {op:<5} {shape:<10} {axis:<5} {pos}")
    print(f"       Dims: {dims}")
print()
sys.stdout.flush()

# ============================================================================
# MODELING
# ============================================================================

# --- Feature 1: Panel body ---
print("Building panel body...")
sys.stdout.flush()

# Build in XZ plane (front face), extrude in Y (depth)
# Use centered box, fillet vertical edges, then translate
panel = (
    cq.Workplane("XZ")
    .rect(PANEL_W, PANEL_H)
    .extrude(-PANEL_D)  # Extrude in +Y (away from viewer)
)
# Fillet the 4 vertical edges (parallel to Y axis) with 6mm radius
panel = panel.edges("|Y").fillet(CORNER_R)
# Translate so origin is at front-left-bottom corner
panel = panel.translate((PANEL_W / 2, 0, PANEL_H / 2))

print(f"  Panel: {PANEL_W}x{PANEL_D}x{PANEL_H}mm with {CORNER_R}mm corner radii.")

# --- Feature 2: Display dock recesses ---
print("Cutting display dock recesses...")
sys.stdout.flush()

for i, (dx, dz) in enumerate(DOCK_CENTERS):
    recess = (
        cq.Workplane("XZ")
        .center(dx, dz)
        .circle(DOCK_R)
        .extrude(-DOCK_DEPTH)  # Into panel from front face (Y=0 toward +Y)
    )
    panel = panel.cut(recess)
    print(f"  Dock {i+1}: {DOCK_DIA}mm dia x {DOCK_DEPTH}mm at ({dx}, {dz})")

# --- Feature 3: Cable exit holes ---
print("Cutting cable exit holes...")
sys.stdout.flush()

for i, (dx, dz) in enumerate(DOCK_CENTERS):
    hole = (
        cq.Workplane("XZ")
        .center(dx, dz)
        .circle(CABLE_HOLE_DIA / 2)
        .extrude(-PANEL_D - 1)  # Through full panel thickness
    )
    panel = panel.cut(hole)
    print(f"  Cable hole {i+1}: {CABLE_HOLE_DIA}mm dia at ({dx}, {dz})")

# --- Feature 4: Bottom tongue ---
# Extends below the panel body from Z=0 to Z=-3
# Centered in Y (wall thickness): Y = (PANEL_D - TONGUE_DEPTH)/2 to Y = (PANEL_D + TONGUE_DEPTH)/2
# = Y = 1.0 to Y = 3.0
print("Building bottom tongue...")
sys.stdout.flush()

tongue_y_center = PANEL_D / 2  # 2.0
tongue = (
    cq.Workplane("XZ")
    .center(PANEL_W / 2, -TONGUE_HEIGHT / 2)  # Center at (110, -1.5)
    .rect(PANEL_W - 2 * CORNER_R, TONGUE_HEIGHT)  # Slightly narrower than panel to clear corner radii
    .extrude(-TONGUE_DEPTH)  # in +Y
)
# Position tongue centered in Y within wall thickness
tongue = tongue.translate((0, (PANEL_D - TONGUE_DEPTH) / 2, 0))
panel = panel.union(tongue)
print(f"  Tongue: {TONGUE_WIDTH-2*CORNER_R:.0f}W x {TONGUE_DEPTH}D x {TONGUE_HEIGHT}H at Z=-3..0")

# --- Feature 5: Snap hooks (4x) ---
# Each hook: L-shaped tab extending from the panel interior face.
# The arm runs along +Y (into the enclosure interior), with a hook tip
# that protrudes in -X (left hooks) or +X (right hooks) to catch the receptacle edge.
print("Building snap hooks...")
sys.stdout.flush()

# Left hooks: at X = HOOK_THICKNESS_X/2 (near X=0 edge), extending in +Y
# Right hooks: at X = PANEL_W - HOOK_THICKNESS_X/2 (near X=220 edge)
hook_sides = [
    ("left",  HOOK_THICKNESS_X / 2,             -1),  # X center, tip direction (-X = outward)
    ("right", PANEL_W - HOOK_THICKNESS_X / 2,    1),  # X center, tip direction (+X = outward)
]

for side_name, hook_x, tip_dir in hook_sides:
    for hook_z in HOOK_Z_POSITIONS:
        # Cantilever arm: thin slab extending from Y=PANEL_D to Y=PANEL_D+HOOK_LENGTH_Y
        arm = (
            cq.Workplane("XZ")
            .center(hook_x, hook_z)
            .rect(HOOK_THICKNESS_X, HOOK_WIDTH_Z)
            .extrude(-HOOK_LENGTH_Y)  # in +Y direction
        )
        arm = arm.translate((0, PANEL_D, 0))

        # Hook tip: small protrusion at the end of the arm
        # Extends in X direction (outward from panel center) to catch receptacle edge
        tip_x = hook_x + tip_dir * (HOOK_THICKNESS_X / 2 + HOOK_TIP_HEIGHT / 2)
        tip = (
            cq.Workplane("XZ")
            .center(tip_x, hook_z)
            .rect(HOOK_TIP_HEIGHT, HOOK_WIDTH_Z)
            .extrude(-HOOK_TIP_DEPTH)  # Short depth at arm end
        )
        tip = tip.translate((0, PANEL_D + HOOK_LENGTH_Y - HOOK_TIP_DEPTH, 0))

        panel = panel.union(arm)
        panel = panel.union(tip)
        print(f"  {side_name} hook at Z={hook_z}: arm {HOOK_THICKNESS_X}x{HOOK_LENGTH_Y}mm + tip")

# ============================================================================
# EXPORT STEP FILE
# ============================================================================
output_path = Path(__file__).parent / "front-panel.step"
cq.exporters.export(panel, str(output_path))
print(f"\nSTEP file exported to: {output_path}")

# ============================================================================
# RUBRIC 3 — Validation Probes
# ============================================================================
print("\n" + "=" * 60)
print("RUBRIC 3 — Validation Probes")
print("=" * 60)

v = Validator(panel)

# --- Panel body ---
v.check_solid("Panel center", PANEL_W / 2, PANEL_D / 2, PANEL_H / 2,
              "solid at panel center")
v.check_solid("Panel near bottom-left", 10, 2, 5,
              "solid near bottom-left (inside corner radius)")
v.check_solid("Panel near top-right", 210, 2, 265,
              "solid near top-right (inside corner radius)")
v.check_void("Outside -X", -1, 2, PANEL_H / 2, "void left of panel")
v.check_void("Outside +X", 221, 2, PANEL_H / 2, "void right of panel")
v.check_void("Outside -Y", 110, -1, PANEL_H / 2, "void in front of panel")
v.check_void("Outside +Y (no hook)", 110, PANEL_D + 1, PANEL_H / 2,
             "void behind panel at center (no hook here)")
v.check_void("Above panel", 110, 2, PANEL_H + 1, "void above panel")
v.check_void("Below tongue", 110, 2, -TONGUE_HEIGHT - 1, "void below tongue")

# Corner radii: at very corner should be void
v.check_void("Corner void BL", 0.5, 2, 0.5, "void at bottom-left corner (radius)")
v.check_void("Corner void TR", 219.5, 2, 269.5, "void at top-right corner (radius)")

# --- Display dock recesses ---
for i, (dx, dz) in enumerate(DOCK_CENTERS):
    tag = f"Dock{i+1}"
    # Center of recess should be void (cable hole goes through)
    v.check_void(f"{tag} center", dx, DOCK_DEPTH / 2, dz,
                 f"void at dock center (cable hole)")
    # Edge of recess (inside dock, outside cable hole)
    v.check_void(f"{tag} recess edge", dx + DOCK_R - 2, DOCK_DEPTH / 2, dz,
                 f"void inside recess near edge")
    # Floor of recess (between DOCK_DEPTH and PANEL_D, outside cable hole)
    # At dock edge, Y=DOCK_DEPTH+0.3 should be solid (remaining 0.7mm backing)
    v.check_solid(f"{tag} backing", dx + DOCK_R - 2, DOCK_DEPTH + 0.3, dz,
                  f"solid in recess backing (1mm)")
    # Outside recess should be solid
    v.check_solid(f"{tag} outside", dx + DOCK_R + 3, 1.0, dz,
                  f"solid outside dock recess")

# --- Cable exit holes ---
for i, (dx, dz) in enumerate(DOCK_CENTERS):
    tag = f"Cable{i+1}"
    v.check_void(f"{tag} through", dx, PANEL_D - 0.5, dz,
                 f"void at cable hole near interior face")
    v.check_solid(f"{tag} outside", dx + CABLE_HOLE_DIA / 2 + 2, PANEL_D - 0.5, dz,
                  f"solid outside cable hole")

# --- Bottom tongue ---
v.check_solid("Tongue center", PANEL_W / 2, tongue_y_center, -TONGUE_HEIGHT / 2,
              "solid at tongue center")
v.check_solid("Tongue near left", CORNER_R + 5, tongue_y_center, -1,
              "solid in tongue near left end")
v.check_solid("Tongue near right", PANEL_W - CORNER_R - 5, tongue_y_center, -1,
              "solid in tongue near right end")
# Tongue does not extend in front of panel or behind panel
v.check_void("Tongue front void", PANEL_W / 2, -0.5, -1,
             "void in front of tongue")
v.check_void("Tongue rear void", PANEL_W / 2, PANEL_D + 0.5, -1,
             "void behind tongue")

# --- Snap hooks ---
# Left hook at Z=70
v.check_solid("Left hook arm Z=70", HOOK_THICKNESS_X / 2, PANEL_D + HOOK_LENGTH_Y / 2, 70,
              "solid in left hook arm")
v.check_solid("Left hook tip Z=70",
              HOOK_THICKNESS_X / 2 - HOOK_TIP_HEIGHT / 2 - 0.2,
              PANEL_D + HOOK_LENGTH_Y - HOOK_TIP_DEPTH / 2,
              70, "solid at left hook tip")
# Right hook at Z=210
v.check_solid("Right hook arm Z=210",
              PANEL_W - HOOK_THICKNESS_X / 2,
              PANEL_D + HOOK_LENGTH_Y / 2, 210,
              "solid in right hook arm")
# Void between hooks
v.check_void("No hook at center", PANEL_W / 2, PANEL_D + 5, 70,
             "void behind panel center (no hook)")

# ============================================================================
# RUBRIC 4 — Solid Validity
# ============================================================================
print("\n" + "=" * 60)
print("RUBRIC 4 — Solid Validity")
print("=" * 60)
v.check_valid()
v.check_single_body()

# Envelope: panel body + hooks + tongue
panel_vol = PANEL_W * PANEL_D * PANEL_H
hook_vol = 4 * HOOK_THICKNESS_X * HOOK_LENGTH_Y * HOOK_WIDTH_Z
tongue_vol = (PANEL_W - 2 * CORNER_R) * TONGUE_DEPTH * TONGUE_HEIGHT
total_envelope = panel_vol + hook_vol + tongue_vol
v.check_volume(expected_envelope=total_envelope, fill_range=(0.5, 1.2))

# ============================================================================
# RUBRIC 5 — Bounding Box
# ============================================================================
print("\n" + "=" * 60)
print("RUBRIC 5 — Bounding Box")
print("=" * 60)
bb = panel.val().BoundingBox()
print(f"Actual BB: X[{bb.xmin:.2f}, {bb.xmax:.2f}] "
      f"Y[{bb.ymin:.2f}, {bb.ymax:.2f}] "
      f"Z[{bb.zmin:.2f}, {bb.zmax:.2f}]")

# X: hooks extend slightly beyond panel edges (tip protrusion)
expected_x_min = -HOOK_TIP_HEIGHT  # Left hook tip extends in -X
expected_x_max = PANEL_W + HOOK_TIP_HEIGHT  # Right hook tip extends in +X
v.check_bbox("X", bb.xmin, bb.xmax, expected_x_min, expected_x_max, tol=1.0)
v.check_bbox("Y", bb.ymin, bb.ymax, 0, PANEL_D + HOOK_LENGTH_Y, tol=1.0)
v.check_bbox("Z", bb.zmin, bb.zmax, -TONGUE_HEIGHT, PANEL_H, tol=1.0)

# ============================================================================
# SUMMARY
# ============================================================================
if not v.summary():
    sys.exit(1)

print("\nDone.")
