#!/usr/bin/env python3
"""
Generate the release plate STEP file for the pump cartridge.

Source: hardware/printed-parts/pump-cartridge/planning/release-plate-parts.md
        hardware/printed-parts/pump-cartridge/planning/release-plate-spatial.md
"""

# Coordinate system:
#   Origin: front-left-bottom corner of the main plate body
#   X: plate width, left to right (main body 0..83.4, tabs extend to -18.8 and 102.2)
#   Y: plate depth, front face to rear face (0..5.0, spring bosses to 8.0)
#   Z: plate height, bottom to top (0..34.2)
#   Envelope (with tabs and bosses): X [-18.8, 102.2]  Y [0, 8.0]  Z [0, 34.2]
#   Front face at Y=0, rear face at Y=5.0
#   Build-plate face (print orientation): rear face (Y=5.0) down

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

import cadquery as cq
from step_validate import Validator
import math

# =====================================================================
# RUBRIC 1 -- Feature Planning Table
# =====================================================================

print("""
=== RUBRIC 1: Feature Planning Table ===

| # | Feature Name             | Mechanical Function                              | Op     | Shape      | Axis | Center (X,Y,Z)                 | Dimensions                                      | Notes                              |
|---|--------------------------|--------------------------------------------------|--------|------------|------|---------------------------------|-------------------------------------------------|------------------------------------|
| 1 | Main plate body          | Structural core, transfers linkage force to collets| Add    | Box        | --   | 41.7, 2.5, 17.1                | 83.4 x 5.0 x 34.2 mm                           | centered=False from origin         |
| 2a| Left lateral tab         | Extends plate to left arm channel, holds pin socket| Add    | Box        | X    | -9.4, 2.5, 17.75               | 18.8 x 5.0 x 5.0 mm                            | X=-18.8..0, Z=15.25..20.25        |
| 2b| Right lateral tab        | Extends plate to right arm channel, holds pin socket| Add   | Box        | X    | 92.8, 2.5, 17.75               | 18.8 x 5.0 x 5.0 mm                            | X=83.4..102.2, Z=15.25..20.25     |
| 3a| Stepped bore JG1         | Cradles body end, guides on collet, pushes collet | Remove | Revolved   | Y    | (9.2, -, 8.55)                 | 15.4/9.8/6.5 dia, 3.4/0.6/1.0 deep             | Left lower bore                    |
| 3b| Stepped bore JG2         | Same as JG1                                       | Remove | Revolved   | Y    | (74.2, -, 8.55)                | Same as JG1                                     | Right lower bore                   |
| 3c| Stepped bore JG3         | Same as JG1                                       | Remove | Revolved   | Y    | (9.2, -, 25.65)                | Same as JG1                                     | Left upper bore                    |
| 3d| Stepped bore JG4         | Same as JG1                                       | Remove | Revolved   | Y    | (74.2, -, 25.65)               | Same as JG1                                     | Right upper bore                   |
| 4a| Left pin socket          | Receives 3mm linkage arm pin (press-fit)          | Remove | Cylinder   | Y    | (-9.4, 0, 17.75)               | 3.1 dia x 4.0 deep, blind                      | Opens at Y=0, ends at Y=4.0       |
| 4b| Right pin socket         | Receives 3mm linkage arm pin (press-fit)          | Remove | Cylinder   | Y    | (92.8, 0, 17.75)               | 3.1 dia x 4.0 deep, blind                      | Opens at Y=0, ends at Y=4.0       |
| 5a| Left spring boss         | Centers left compression spring on rear face      | Add    | Cylinder   | Y    | (9.2, 6.5, 17.1)               | 2.0 dia x 3.0 tall, base at Y=5.0              | Protrudes to Y=8.0                 |
| 5b| Right spring boss        | Centers right compression spring on rear face     | Add    | Cylinder   | Y    | (74.2, 6.5, 17.1)              | 2.0 dia x 3.0 tall, base at Y=5.0              | Protrudes to Y=8.0                 |
| 6 | Rear-face entry chamfers | Eases JG body-end engagement, compensates elephant foot | Remove | Chamfer | Y | At each bore center on rear face | 0.3mm x 45deg on 15.4mm bore entry at Y=5.0    | 4 chamfers total                   |
| 7 | Hugger-to-cradle chamfer | Guides collet OD into hugger bore during assembly | Remove | Chamfer    | Y    | At each bore, Y=1.6 step        | 0.3mm x 45deg on 9.8mm bore at cradle-hugger step| 4 chamfers total                  |
""")

# =====================================================================
# Dimensions from parts.md
# =====================================================================

# Main body
BODY_W = 83.4   # X
BODY_D = 5.0    # Y
BODY_H = 34.2   # Z

# Lateral tabs (now at mid-height)
TAB_LEN = 18.8   # X extent of each tab
TAB_H   = 5.0    # Z height of each tab
TAB_D   = 5.0    # Y (same as plate depth)
TAB_Z_BOT = 15.25  # Bottom of tab in plate local Z
TAB_Z_TOP = 20.25  # Top of tab in plate local Z
TAB_Z_CENTER = 17.75  # Center Z of tab

# Bore parameters (all 4 identical)
BORE_CENTERS = [
    (9.2,  8.55),   # JG1 left lower  (X, Z)
    (74.2, 8.55),   # JG2 right lower
    (9.2,  25.65),  # JG3 left upper
    (74.2, 25.65),  # JG4 right upper
]

# Stepped bore diameters and depths (from rear face Y=5.0 inward)
CRADLE_DIA   = 15.4   # Body end cradle
CRADLE_DEPTH = 3.4    # Y=5.0 to Y=1.6

HUGGER_DIA   = 9.8    # Collet hugger
HUGGER_DEPTH = 0.6    # Y=1.6 to Y=1.0

TUBE_DIA     = 6.5    # Tube clearance
TUBE_DEPTH   = 1.0    # Y=1.0 to Y=0 (through)

CHAMFER      = 0.3    # 0.3mm x 45-deg chamfers

# Pin sockets (Y-axis, opening on front face)
PIN_DIA      = 3.1
PIN_DEPTH    = 4.0    # From Y=0 to Y=4.0
# Left socket: center at (-9.4, 0, 17.75), axis +Y, depth 4.0 -> blind end at Y=4.0
# Right socket: center at (92.8, 0, 17.75), axis +Y, depth 4.0 -> blind end at Y=4.0
LEFT_SOCKET_CX  = -9.4
RIGHT_SOCKET_CX = 92.8
SOCKET_CZ       = TAB_Z_CENTER  # 17.75

# Spring bosses
BOSS_DIA     = 2.0
BOSS_HEIGHT  = 3.0    # protrudes from rear face (Y=5.0) to Y=8.0
BOSS_CENTERS = [(9.2, 17.1), (74.2, 17.1)]  # (X, Z)

# =====================================================================
# RUBRIC 2 -- Coordinate System (declared as comments at script top)
# =====================================================================

# =====================================================================
# Build the model
# =====================================================================

# --- Feature 1: Main plate body ---
plate = cq.Workplane("XY").box(BODY_W, BODY_D, BODY_H, centered=False)

# --- Feature 2a: Left lateral tab ---
# X = -18.8 to 0, Y = 0 to 5.0, Z = 15.25 to 20.25
left_tab = cq.Workplane("XY").transformed(offset=(-TAB_LEN, 0, TAB_Z_BOT)).box(
    TAB_LEN, TAB_D, TAB_H, centered=False
)
plate = plate.union(left_tab)

# --- Feature 2b: Right lateral tab ---
# X = 83.4 to 102.2, Y = 0 to 5.0, Z = 15.25 to 20.25
right_tab = cq.Workplane("XY").transformed(offset=(BODY_W, 0, TAB_Z_BOT)).box(
    TAB_LEN, TAB_D, TAB_H, centered=False
)
plate = plate.union(right_tab)

# --- Features 3a-3d: Four stepped bores (revolved profiles) ---
# The bore axis is along Y. We define the cross-section in the R-Y plane
# and revolve around the Y axis.
#
# Profile: from front face (Y=0) to rear face (Y=5.0)
# Y=0 to Y=1.0: tube clearance (R = 6.5/2 = 3.25)
# Y=1.0 to Y=1.6: collet hugger (R = 9.8/2 = 4.9)
# Y=1.6 to Y=5.0: body end cradle (R = 15.4/2 = 7.7)
#
# Plus chamfers:
# - Entry chamfer at rear face (Y=5.0): 0.3mm x 45deg on the 15.4mm bore
# - Hugger-to-cradle chamfer at Y=1.6: 0.3mm x 45deg on the 9.8mm bore
# - NO chamfer at Y=1.0 (contact face must remain flat)

R_TUBE   = TUBE_DIA / 2      # 3.25
R_HUGGER = HUGGER_DIA / 2    # 4.9
R_CRADLE = CRADLE_DIA / 2    # 7.7
C = CHAMFER                   # 0.3

# Profile points in (R, Y) starting from axis at front face, going CCW
profile_pts = [
    (0,             0),              # axis at front face (Y=0)
    (R_TUBE,        0),              # tube bore wall at front face
    (R_TUBE,        TUBE_DEPTH),     # tube bore wall at Y=1.0 (contact face - no chamfer here)
    (R_HUGGER,      TUBE_DEPTH),     # hugger bore wall at Y=1.0
    (R_HUGGER,      TUBE_DEPTH + HUGGER_DEPTH - C),  # hugger wall just before step to cradle (Y=1.6-0.3=1.3)
    (R_HUGGER + C,  TUBE_DEPTH + HUGGER_DEPTH),      # chamfer end at cradle-hugger transition (Y=1.6)
    (R_CRADLE,      TUBE_DEPTH + HUGGER_DEPTH),       # cradle bore wall at Y=1.6
    (R_CRADLE,      BODY_D - C),     # cradle bore wall just before rear face chamfer (Y=5.0-0.3=4.7)
    (R_CRADLE + C,  BODY_D),         # rear face entry chamfer end (Y=5.0)
    (0,             BODY_D),         # axis at rear face (Y=5.0)
]

# Create a single bore by revolving this profile around the Y axis
bore_profile = cq.Workplane("XY").polyline(profile_pts).close()
bore_solid = bore_profile.revolve(360, (0, 0), (0, 1))

# Cut each bore from the plate
for cx, cz in BORE_CENTERS:
    plate = plate.cut(bore_solid.translate((cx, 0, cz)))

# --- Features 4a-4b: Pin sockets (Y-axis, opening on front face) ---
# Left pin socket: cylindrical bore along +Y, center at (-9.4, 0, 17.75)
# Opens at Y=0 (front face), 4.0mm deep ending at Y=4.0
# Create cylinder along Y by using XZ workplane, then extrude.
# XZ workplane normal is -Y; negative extrude goes +Y direction.
left_socket = (
    cq.Workplane("XZ")
    .center(LEFT_SOCKET_CX, SOCKET_CZ)
    .circle(PIN_DIA / 2)
    .extrude(-PIN_DEPTH)  # XZ normal is -Y; negative extrude goes +Y
)
# The circle is on XZ at Y=0. Extrude(-4) goes from Y=0 to Y=4.0.
# No translation needed -- it's already at Y=0..4.0.
plate = plate.cut(left_socket)

# Right pin socket: cylindrical bore along +Y, center at (92.8, 0, 17.75)
# Opens at Y=0 (front face), 4.0mm deep ending at Y=4.0
right_socket = (
    cq.Workplane("XZ")
    .center(RIGHT_SOCKET_CX, SOCKET_CZ)
    .circle(PIN_DIA / 2)
    .extrude(-PIN_DEPTH)  # XZ normal is -Y; negative extrude goes +Y
)
plate = plate.cut(right_socket)

# --- Features 5a-5b: Spring bosses on rear face ---
# Bosses protrude from the rear face (Y=5.0) in the +Y direction.
for bx, bz in BOSS_CENTERS:
    boss = (
        cq.Workplane("XZ")
        .center(bx, bz)
        .circle(BOSS_DIA / 2)
        .extrude(-BOSS_HEIGHT)  # XZ normal is -Y; negative extrude goes +Y
    )
    # The circle is on XZ at Y=0. Extrude(-3) goes from Y=0 to Y=3.
    # We need the boss from Y=5.0 to Y=8.0, so translate by BODY_D.
    plate = plate.union(boss.translate((0, BODY_D, 0)))

# =====================================================================
# Export STEP
# =====================================================================

output_path = Path(__file__).parent / "release-plate.step"
cq.exporters.export(plate, str(output_path))
print(f"\nSTEP file exported to: {output_path}")

# =====================================================================
# RUBRIC 3 -- Feature-Specification Reconciliation
# =====================================================================

print("\n=== RUBRIC 3: Feature Reconciliation ===\n")

v = Validator(plate)

# --- Feature 1: Main plate body ---
v.check_solid("Body center",        41.7, 2.5, 17.1, "solid at plate body center")
v.check_solid("Body near front",    41.7, 0.1, 17.1, "solid near front face Y=0")
v.check_solid("Body near rear",     41.7, 4.9, 17.1, "solid near rear face Y=5.0")
v.check_solid("Body left edge",      0.1, 2.5, 17.1, "solid near left face X=0")
v.check_solid("Body right edge",    83.3, 2.5, 17.1, "solid near right face X=83.4")
v.check_solid("Body bottom edge",   41.7, 2.5,  0.1, "solid near bottom face Z=0")
v.check_solid("Body top edge",      41.7, 2.5, 34.1, "solid near top face Z=34.2")
# Outside the body (probe at Z=5.0, which is outside the mid-height tab range)
v.check_void("Outside body left",    -0.5, 2.5, 5.0, "void outside left face at Z=5.0 (below tabs)")
v.check_void("Outside body right",   83.9, 2.5, 5.0, "void outside right face at Z=5.0 (below tabs)")
v.check_void("Outside body front",   41.7, -0.5, 17.1, "void in front of front face")
v.check_void("Outside body top",     41.7, 2.5, 34.7, "void above top face")

# --- Feature 2a: Left lateral tab (Z=15.25 to 20.25) ---
# Probe offset from socket bore center: socket is at X=-9.4, Z=17.75 with 3.1mm dia
# Probe at Z offset from socket center to hit solid tab material
v.check_solid("Left tab center",     -9.4, 2.5, TAB_Z_BOT + 0.5, "solid at left tab center (away from socket bore)")
v.check_solid("Left tab outer end", -18.5, 2.5, TAB_Z_CENTER, "solid near left tab outer end X=-18.8")
v.check_solid("Left tab inner end",  -0.1, 2.5, TAB_Z_CENTER, "solid at left tab inner end (joins body)")
v.check_solid("Left tab Z bottom",   -9.4, 2.5, TAB_Z_BOT + 0.2, "solid near left tab bottom Z=15.25")
v.check_solid("Left tab Z top",      -9.4, 2.5, TAB_Z_TOP - 0.2, "solid near left tab top Z=20.25")
v.check_void("Left tab below",       -9.4, 2.5, TAB_Z_BOT - 0.5, "void below left tab Z=14.75")
v.check_void("Left tab above",       -9.4, 2.5, TAB_Z_TOP + 0.5, "void above left tab Z=20.75")
v.check_void("Left tab beyond",     -19.3, 2.5, TAB_Z_CENTER, "void beyond left tab outer end")

# --- Feature 2b: Right lateral tab (Z=15.25 to 20.25) ---
# Probe offset from socket bore center
v.check_solid("Right tab center",    92.8, 2.5, TAB_Z_BOT + 0.5, "solid at right tab center (away from socket bore)")
v.check_solid("Right tab outer end",102.0, 2.5, TAB_Z_CENTER, "solid near right tab outer end X=102.2")
v.check_solid("Right tab inner end", 83.5, 2.5, TAB_Z_CENTER, "solid at right tab inner end (joins body)")
v.check_solid("Right tab Z bottom",  92.8, 2.5, TAB_Z_BOT + 0.2, "solid near right tab bottom Z=15.25")
v.check_solid("Right tab Z top",     92.8, 2.5, TAB_Z_TOP - 0.2, "solid near right tab top Z=20.25")
v.check_void("Right tab above",      92.8, 2.5, TAB_Z_TOP + 0.5, "void above right tab Z=20.75")
v.check_void("Right tab beyond",    102.7, 2.5, TAB_Z_CENTER, "void beyond right tab outer end")

# Verify tabs are NOT at old Z=0..5.0 position (regression check)
v.check_void("Left tab old pos Z=2.5",  -9.4, 2.5, 2.5, "void at old left tab Z position (should be empty)")
v.check_void("Right tab old pos Z=2.5", 92.8, 2.5, 2.5, "void at old right tab Z position (should be empty)")

# --- Features 3a-3d: Stepped bores ---
bore_names = ["JG1 (left lower)", "JG2 (right lower)", "JG3 (left upper)", "JG4 (right upper)"]
for name, (cx, cz) in zip(bore_names, BORE_CENTERS):
    # Tube clearance zone: Y=0 to Y=1.0, R < 3.25 -> void
    v.check_void(f"{name} tube center Y=0.5",       cx, 0.5, cz, f"void at tube bore center Y=0.5")
    v.check_void(f"{name} tube edge Y=0.5",          cx + R_TUBE - 0.2, 0.5, cz, f"void inside tube bore radius")
    v.check_solid(f"{name} tube wall Y=0.5",         cx + R_TUBE + 0.3, 0.5, cz, f"solid outside tube bore at Y=0.5")

    # Collet hugger zone: Y=1.0 to Y=1.6, R < 4.9 -> void
    v.check_void(f"{name} hugger center Y=1.3",      cx, 1.3, cz, f"void at hugger bore center Y=1.3")
    v.check_void(f"{name} hugger edge Y=1.3",        cx + R_HUGGER - 0.2, 1.3, cz, f"void inside hugger radius at Y=1.3")
    v.check_solid(f"{name} hugger wall Y=1.3",       cx + R_HUGGER + 0.5, 1.3, cz, f"solid outside hugger at Y=1.3")

    # Body end cradle zone: Y=1.6 to Y=5.0, R < 7.7 -> void
    v.check_void(f"{name} cradle center Y=3.0",      cx, 3.0, cz, f"void at cradle bore center Y=3.0")
    v.check_void(f"{name} cradle edge Y=3.0",        cx + R_CRADLE - 0.2, 3.0, cz, f"void inside cradle radius at Y=3.0")

    # Contact face: the annular step at Y=1.0 between R_TUBE and R_HUGGER -> solid
    annular_r = (R_TUBE + R_HUGGER) / 2  # ~4.075
    v.check_solid(f"{name} contact face annulus Y=0.95", cx + annular_r, 0.95, cz, f"solid in annular contact zone")

    # Verify bore axes are along Y by probing at different Y depths on-axis
    v.check_void(f"{name} on-axis Y=0.1",  cx, 0.1, cz, f"void on bore axis near front face")
    v.check_void(f"{name} on-axis Y=4.5",  cx, 4.5, cz, f"void on bore axis near rear face")

# --- Features 4a-4b: Pin sockets (Y-axis) ---
# Left pin socket: bore from Y=0 to Y=4.0, center X=-9.4, Z=17.75, dia=3.1
v.check_void("Left pin socket center",     LEFT_SOCKET_CX, 2.0, SOCKET_CZ, "void at left socket center Y=2.0")
v.check_void("Left pin socket near open",  LEFT_SOCKET_CX, 0.2, SOCKET_CZ, "void near left socket opening Y=0.2")
v.check_void("Left pin socket near blind", LEFT_SOCKET_CX, 3.8, SOCKET_CZ, "void near left socket blind end Y=3.8")
v.check_solid("Left pin socket wall Z+",   LEFT_SOCKET_CX, 2.0, SOCKET_CZ + PIN_DIA/2 + 0.3, "solid above left socket radius")
v.check_solid("Left pin socket wall Z-",   LEFT_SOCKET_CX, 2.0, SOCKET_CZ - PIN_DIA/2 - 0.3, "solid below left socket radius")
v.check_solid("Left pin socket blind end", LEFT_SOCKET_CX, 4.3, SOCKET_CZ, "solid beyond blind end of left socket Y=4.3")

# Right pin socket: bore from Y=0 to Y=4.0, center X=92.8, Z=17.75, dia=3.1
v.check_void("Right pin socket center",     RIGHT_SOCKET_CX, 2.0, SOCKET_CZ, "void at right socket center Y=2.0")
v.check_void("Right pin socket near open",  RIGHT_SOCKET_CX, 0.2, SOCKET_CZ, "void near right socket opening Y=0.2")
v.check_void("Right pin socket near blind", RIGHT_SOCKET_CX, 3.8, SOCKET_CZ, "void near right socket blind end Y=3.8")
v.check_solid("Right pin socket wall Z+",   RIGHT_SOCKET_CX, 2.0, SOCKET_CZ + PIN_DIA/2 + 0.3, "solid above right socket radius")
v.check_solid("Right pin socket wall Z-",   RIGHT_SOCKET_CX, 2.0, SOCKET_CZ - PIN_DIA/2 - 0.3, "solid below right socket radius")
v.check_solid("Right pin socket blind end", RIGHT_SOCKET_CX, 4.3, SOCKET_CZ, "solid beyond blind end of right socket Y=4.3")

# Verify no tab material at old Z=0..5 position in tab X range (regression check)
# Old tabs were at Z=0..5.0 along X=-18.8..0 and X=83.4..102.2.
# New tabs are at Z=15.25..20.25. At Z=2.5 and tab X, there should be void.
v.check_void("No old left tab Z=2.5",  -9.4, 2.5, 2.5, "void at old left tab Z position (tabs moved to mid-height)")
v.check_void("No old right tab Z=2.5", 92.8, 2.5, 2.5, "void at old right tab Z position (tabs moved to mid-height)")

# --- Features 5a-5b: Spring bosses ---
# Left boss: center (9.2, Y, 17.1), Y=5.0 to 8.0, dia=2.0
v.check_solid("Left spring boss mid",       9.2, 6.5, 17.1, "solid at left boss mid-height Y=6.5")
v.check_solid("Left spring boss near base", 9.2, 5.1, 17.1, "solid near left boss base Y=5.1")
v.check_solid("Left spring boss near tip",  9.2, 7.9, 17.1, "solid near left boss tip Y=7.9")
v.check_void("Left spring boss beyond tip", 9.2, 8.3, 17.1, "void beyond left boss tip Y=8.3")
v.check_void("Left spring boss wall",       9.2 + BOSS_DIA/2 + 0.3, 6.5, 17.1, "void outside left boss radius")

# Right boss: center (74.2, Y, 17.1), Y=5.0 to 8.0, dia=2.0
v.check_solid("Right spring boss mid",      74.2, 6.5, 17.1, "solid at right boss mid-height Y=6.5")
v.check_solid("Right spring boss near base",74.2, 5.1, 17.1, "solid near right boss base Y=5.1")
v.check_solid("Right spring boss near tip", 74.2, 7.9, 17.1, "solid near right boss tip Y=7.9")
v.check_void("Right spring boss beyond tip",74.2, 8.3, 17.1, "void beyond right boss tip Y=8.3")
v.check_void("Right spring boss wall",      74.2 + BOSS_DIA/2 + 0.3, 6.5, 17.1, "void outside right boss radius")

# --- Feature 6 & 7: Chamfers ---
# Rear face entry chamfer: at Y=5.0, the bore opens at R_CRADLE + C = 8.0
for name, (cx, cz) in zip(bore_names, BORE_CENTERS):
    v.check_void(f"{name} rear chamfer zone", cx + R_CRADLE + 0.1, 4.85, cz,
                 f"void in rear-face entry chamfer at R>{R_CRADLE}")

# Hugger-to-cradle chamfer: at Y=1.6, transition from R_HUGGER to R_CRADLE
for name, (cx, cz) in zip(bore_names, BORE_CENTERS):
    v.check_void(f"{name} hugger-cradle chamfer zone", cx + R_HUGGER + 0.1, 1.45, cz,
                 f"void in hugger-to-cradle chamfer zone")

# =====================================================================
# RUBRIC 4 -- Solid Validity
# =====================================================================

print("\n=== RUBRIC 4: Solid Validity ===\n")

v.check_valid()
v.check_single_body()

# Expected envelope for volume check: overall bounding box
# X: 121.0, Y: 8.0 (including bosses), Z: 34.2
ENVELOPE_VOL = 121.0 * 8.0 * 34.2
v.check_volume(expected_envelope=ENVELOPE_VOL, fill_range=(0.15, 0.60))

# =====================================================================
# RUBRIC 5 -- Bounding Box Reconciliation
# =====================================================================

print("\n=== RUBRIC 5: Bounding Box ===\n")

bb = plate.val().BoundingBox()

# Expected: X [-18.8, 102.2], Y [0, 8.0], Z [0, 34.2]
# Tabs are now at Z=15.25..20.25, within the main body height, so no Z extension
v.check_bbox("X", bb.xmin, bb.xmax, -18.8, 102.2)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, 8.0)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, 34.2)

# =====================================================================
# Summary
# =====================================================================

if not v.summary():
    sys.exit(1)

print(f"\nDone. STEP file: {output_path}")
