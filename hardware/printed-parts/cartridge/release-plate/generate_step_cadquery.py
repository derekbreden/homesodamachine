"""
Release Plate v5 -- CadQuery STEP Generation Script
Pipeline step: 6g -- STEP Generation
Input: planning/parts.md
Output: release-plate-cadquery.step

Part: Single printed PETG sliding actuator that simultaneously depresses the
rear-facing collets of four PP0408W quick-connect fittings.

v5 change: Widen plate to 140.0mm and move struts to match lever/pump tray positions.
  - Plate width updated from 137.2mm to 140.0mm (matches all interior plates).
  - Strut centers moved from (10.0, 127.2) to (4.0, 136.0) in X to match
    lever strut positions and pump tray bore centers.
  - Bore positions unchanged (1x4 row at Z=34.3).
  - All other dimensions unchanged.

Coordinate system (part local frame):
  Origin: plate bottom-left corner at fitting-facing face (X=0, Y=0, Z=0)
  X: plate width, left to right, 0 -> 160.0 mm
  Y: plate depth, fitting-facing to user-facing; struts extend beyond user-facing face
       Y=0  = fitting-facing face (tube exit side, sits on build plate in print orientation)
       Y=5  = user-facing face (stepped bore entry, pull surface, struts attach here)
       Y=95 = strut tips (90 mm beyond user-facing face, toward lever)
  Z: plate height, bottom to top, 0 -> 68.6 mm
  Plate envelope:          X:[0,160.0]  Y:[0,5]     Z:[0,68.6]
  With struts:             X:[0,160.0]  Y:[0,95]    Z:[0,68.6]

CadQuery XZ workplane notes:
  XZ workplane origin: (0,0,0), normal (zDir): (0,-1,0) = -Y direction
  workplane(offset=X) shifts plane by X in the normal direction (-Y):
    offset=-5 -> plane at Y = 0 + (-5)*(-1) = +5  (USER-FACING FACE)
    offset=+5 -> plane at Y = 0 + (+5)*(-1) = -5  (outside part)
  extrude(positive) -> goes in normal direction (-Y)
  extrude(negative) -> goes opposite to normal (+Y)

  For bores running Y=5 -> Y=0 (user-facing to fitting-facing, -Y direction):
    Use offset=-Y_start (e.g., offset=-5.0 for plane at Y=5)
    Extrude positive depth (goes -Y from plane)

  For struts running Y=5 -> Y=95 (user-facing outward, +Y direction):
    Use plain XY workplane, then translate strut box to correct position.
"""

import sys
from pathlib import Path

import cadquery as cq

# Script is at: hardware/printed-parts/cartridge/release-plate/generate_step_cadquery.py
# parents[4] = project root
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

# Part parameters (from parts.md v5)

PLATE_W = 160.0  # X extent (was 140.0, +20mm to accommodate struts moved outward)
PLATE_D = 5.0    # Y extent (thickness)
PLATE_H = 43.6   # Z extent (was 68.6, -25mm: 12.5mm from top and bottom)

# Bore zone diameters (unchanged)
Z1_D = 15.60    # Zone 1 (outer counterbore)
Z2_D = 10.07    # Zone 2 (inner lip bore)
Z3_D = 7.00     # Zone 3 (tube clearance through-hole)

Z1_R = Z1_D / 2   # 7.80
Z2_R = Z2_D / 2   # 5.035
Z3_R = Z3_D / 2   # 3.25

# Zone Y boundaries (measured from fitting-facing face, Y increases toward user)
Y_USER     = 5.0   # user-facing face (stepped bore entry, struts)
Y_Z1_FLOOR = 3.6   # Zone 1 floor / Zone 2 top
Y_Z2_FLOOR = 2.4   # Zone 2 floor / Zone 3 top (inner shoulder)
Y_FITTING  = 0.0   # fitting-facing face (tube exit, build plate)

# Bore center positions (X, Z) -- 1x4 row matching coupler tray (unchanged)
BORE_CENTERS = [
    (54.5, 21.8),   # A -- H1 (centered, Z shifted -12.5mm)
    (71.5, 21.8),   # B -- H2 (centered, Z shifted -12.5mm)
    (88.5, 21.8),   # C -- H3 (centered, Z shifted -12.5mm)
    (105.5, 21.8),  # D -- H4 (centered, Z shifted -12.5mm)
]

# Strut parameters (Features 10-13)
STRUT_W  = 6.0    # X cross-section
STRUT_H  = 6.0    # Z cross-section
STRUT_L  = 75.0   # Y length
STRUT_Y0 = 5.0    # strut base at user-facing face (Y=5)
STRUT_Y1 = 80.0   # strut tips (75 mm beyond user-facing face, toward lever)

# Strut center positions (X, Z) -- moved to match lever and pump tray bore centers
STRUTS = {
    "TL": (7.0,   35.6),   # Top-Left corner -- matches lever TL
    "TR": (153.0, 35.6),   # Top-Right corner -- matches lever TR
    "BL": (7.0,    8.0),   # Bottom-Left corner -- matches lever BL
    "BR": (153.0,  8.0),   # Bottom-Right corner -- matches lever BR
}

# Fillet radii
CORNER_R = 2.0   # Perimeter corner radii (4 vertical edges parallel to Y)
PULL_R   = 3.0   # Pull edge radius (4 fitting-face perimeter edges at Y=0)

# Modeling

print("RELEASE PLATE v5 -- CadQuery STEP Generation")

# Feature 1: Plate body
# box(W, D, H, centered=False) with W=140.0 (X), D=5 (Y), H=68.6 (Z)
# -> X:[0,160.0] Y:[0,5] Z:[0,68.6]
plate = cq.Workplane("XY").box(PLATE_W, PLATE_D, PLATE_H, centered=False)
print("  [+] Feature 1: Plate body (160.0 x 5 x 68.6 mm)")

# Feature 2: Perimeter corner radii -- R2 on 4 vertical edges (parallel to Y)
# These are the edges at (X=0,Z=0), (X=140.0,Z=0), (X=0,Z=68.6), (X=140.0,Z=68.6)
# running in the Y direction. Select with "|Y" edge filter.
plate = plate.edges("|Y").fillet(CORNER_R)
print("  [+] Feature 2: Corner radii R2.0 on 4 vertical (Y-parallel) edges")

# Feature 3: Pull edge radius -- R3 on 4 fitting-face perimeter edges (at Y=0)
# These are the 4 perimeter edges of the fitting-facing face (minimum Y face).
# Select with face("<Y") then edges().
plate = plate.faces("<Y").edges().fillet(PULL_R)
print("  [+] Feature 3: Pull edge radius R3.0 on fitting-face (Y=0) perimeter edges")

# Features 4-7: Stepped bores A, B, C, D
#
# Each bore runs along -Y from user-facing face (Y=5) to fitting-facing face (Y=0).
# Three cylindrical zones are cut separately.
#
# XZ workplane convention:
#   - workplane(offset=-Y_pos) places the XZ plane at Y = Y_pos
#   - positive extrude depth goes in -Y direction (from plane toward fitting face)
#   - center(cx, cz) on XZ sets X=cx, Z=cz
#
# Zone 1: D15.60 mm, from Y=5.0 -> Y=3.6 (depth 1.4 mm, opens at user-facing face)
# Zone 2: D10.07 mm, from Y=3.6 -> Y=1.6 (depth 2.0 mm)
# Zone 3: D 6.50 mm, from Y=1.6 -> Y=0.0 (depth 1.6 mm, exits fitting-facing face)

for bore_idx, (cx, cz) in enumerate(BORE_CENTERS):
    label = ["A", "B", "C", "D"][bore_idx]

    # Zone 1: plane at Y=5.0, extrude 1.4 mm toward fitting face (-Y)
    zone1 = (
        cq.Workplane("XZ")
        .workplane(offset=-Y_USER)         # offset=-5.0 -> plane at Y=5.0
        .center(cx, cz)
        .circle(Z1_R)
        .extrude(Y_USER - Y_Z1_FLOOR)      # 1.4 mm in -Y direction
    )
    plate = plate.cut(zone1)

    # Zone 2: plane at Y=3.6, extrude 2.0 mm toward fitting face (-Y)
    zone2 = (
        cq.Workplane("XZ")
        .workplane(offset=-Y_Z1_FLOOR)     # offset=-3.6 -> plane at Y=3.6
        .center(cx, cz)
        .circle(Z2_R)
        .extrude(Y_Z1_FLOOR - Y_Z2_FLOOR)  # 2.0 mm in -Y direction
    )
    plate = plate.cut(zone2)

    # Zone 3: plane at Y=1.6, extrude 1.6 mm toward fitting face (-Y)
    zone3 = (
        cq.Workplane("XZ")
        .workplane(offset=-Y_Z2_FLOOR)     # offset=-1.6 -> plane at Y=1.6
        .center(cx, cz)
        .circle(Z3_R)
        .extrude(Y_Z2_FLOOR - Y_FITTING)   # 1.6 mm in -Y direction
    )
    plate = plate.cut(zone3)

    print(f"  [-] Feature {4 + bore_idx}: Stepped bore {label} at X={cx}, Z={cz}")

# Features 10-13: Struts TL, TR, BL, BR
#
# Each strut is a 6x6 mm rectangular prism extending from Y=5 (user-facing face)
# to Y=95 (90 mm beyond user-facing face, toward lever). The strut base is flush
# with the plate user-facing face; the strut tips are plain square ends (no joinery).
#
# Placement: center at (cx, cz) in XZ, Y from STRUT_Y0 to STRUT_Y1.
# The box starts at (cx - STRUT_W/2, STRUT_Y0, cz - STRUT_H/2)
# and has dimensions (STRUT_W, STRUT_L, STRUT_H).
SOCKET_W = 3.0       # X cross-section of socket hole
SOCKET_H = 3.0       # Z cross-section of socket hole
STRUT_SOCKET_L = 17.0  # Y length of socket hole
STRUT_SOCKET_Y0 = STRUT_Y1 - STRUT_SOCKET_L  # Y=63.0 (start of socket)

SNAP_BUMP_PROTRUSION = 0.25  # protrudes into socket in X
SNAP_BUMP_WIDTH = 1.0        # width in Y

strut_feature_num = 10
for label, (cx, cz) in STRUTS.items():
    sx0 = cx - STRUT_W / 2    # left X edge of strut
    sz0 = cz - STRUT_H / 2    # bottom Z edge of strut
    sy0 = STRUT_Y0             # Y start = 5.0 (base at user-facing face)
    # Main 6x6 strut body (full length, no expansion)
    strut = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(sx0, sy0, sz0))
        .box(STRUT_W, STRUT_L, STRUT_H, centered=False)
    )
    plate = plate.union(strut)
    # 3x3 socket hole in tip (last 17mm, open at tip end)
    socket_x0 = cx - SOCKET_W / 2
    socket_z0 = cz - SOCKET_H / 2
    socket = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(socket_x0, STRUT_SOCKET_Y0, socket_z0))
        .box(SOCKET_W, STRUT_SOCKET_L, SOCKET_H, centered=False)
    )
    plate = plate.cut(socket)
    # Snap-fit bumps on opposing X walls of socket, 2mm from closed end
    snap_bump_y0 = STRUT_SOCKET_Y0 + 2.0 - SNAP_BUMP_WIDTH / 2  # centered 2mm from closed end
    for bump_x0 in [cx - SOCKET_W / 2,                                # -X wall, protrudes inward (+X)
                     cx + SOCKET_W / 2 - SNAP_BUMP_PROTRUSION]:       # +X wall, protrudes inward (-X)
        bump = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(bump_x0, snap_bump_y0, socket_z0))
            .box(SNAP_BUMP_PROTRUSION, SNAP_BUMP_WIDTH, SOCKET_H, centered=False)
        )
        plate = plate.union(bump)
    print(f"  [+] Feature {strut_feature_num}: Strut {label} center (X={cx}, Z={cz}), "
          f"6x6 Y:[{sy0},{STRUT_Y1}], 3x3 socket Y:[{STRUT_SOCKET_Y0},{STRUT_Y1}]")
    strut_feature_num += 1

print()
print()

# Export STEP

output_path = Path(__file__).parent / "release-plate-cadquery.step"
cq.exporters.export(plate, str(output_path))
print()
print(f"SUCCESS: STEP file written to:")
print(f"  {output_path}")
print("Done.")
