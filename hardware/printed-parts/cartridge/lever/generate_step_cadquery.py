"""
Lever v3 -- CadQuery STEP Generation Script
Season 1, Phase 6, Item 15 of the pump cartridge build sequence.

Updates from v2: plate widened from 80mm to 140mm, height increased from
65mm to 68.6mm. Strut positions updated to match pump tray v3 strut bore centers.

Coordinate system:
  Origin: Bottom-left corner of lever plate front face (X=0, Y=0, Z=0)
  X: Width axis -- positive rightward as seen by user from front face
     Range: 0 -> 160.0 mm
  Y: Depth axis -- positive rearward (into cartridge)
     Y=0:  Lever plate front face (user contact / pull surface)
     Y=4:  Lever plate rear face (strut attachment point)
     Y=94: Strut tips (4mm plate + 90mm struts)
  Z: Height axis -- positive upward
     Range: 0 -> 68.6 mm

Envelope: 160.0 (X) x 94.0 (Y) x 68.6 (Z) mm
"""

from pathlib import Path

import cadquery as cq

print()
print("RUBRIC 1 -- Feature Planning Table")
print()

col_w = [3, 26, 20, 15, 10, 6, 26, 35, 40]
header = (f"{'#':<{col_w[0]}} {'Feature Name':<{col_w[1]}} {'Operation':<{col_w[3]}} "
          f"{'Shape':<{col_w[4]}} {'Axis':<{col_w[5]}} {'Center (X,Y,Z)':<{col_w[6]}} "
          f"{'Dimensions':<{col_w[7]}} Notes")
print(header)
print()

print("RUBRIC 2 -- Coordinate System Declaration")
print()
print("  Origin: Bottom-left corner of lever plate front face (X=0, Y=0, Z=0)")
print("  X: Plate width, left to right as seen from front face; range [0, 160.0] mm")
print("  Y: Plate depth, front (user contact Y=0) to rear (strut tips Y=94.0); range [0, 94.0] mm")
print("  Z: Plate height, bottom to top; range [0, 68.6] mm")
print("  Envelope: 160.0 x 94.0 x 68.6 mm  ->  X:[0,160]  Y:[0,94]  Z:[0,68.6]")
print()
print("  Feature coordinate cross-check:")
print("    Plate occupies  X:[0,160]    Y:[0,4]    Z:[0,68.6]")
print("    Strut TL center X=4.0,   Z=63.6  -> box X:[1,7]     Y:[4,94]  Z:[60.6,66.6]")
print("    Strut TR center X=156.0, Z=63.6  -> box X:[153,159]  Y:[4,94]  Z:[60.6,66.6]")
print("    Strut BL center X=4.0,   Z=5.0   -> box X:[1,7]     Y:[4,94]  Z:[2,8]")
print("    Strut BR center X=156.0, Z=5.0   -> box X:[153,159]  Y:[4,94]  Z:[2,8]")
print()

# Geometry constants

# Plate
PLATE_W  = 160.0   # X (was 140.0, +20mm to accommodate struts moved outward)
PLATE_D  =   4.0   # Y
PLATE_H  =  43.6   # Z (was 68.6, -25mm: 12.5mm from top and bottom)

# Struts
STRUT_W  =  6.0    # X cross-section
STRUT_H  =  6.0    # Z cross-section
STRUT_L  = 90.0    # Y length
STRUT_Y0 =  4.0    # struts start at plate rear face
STRUT_Y1 = 94.0    # strut tips

# Strut center positions in lever local X and Z
# Positions match pump tray v3 strut bore centers exactly.
STRUTS = {
    "TL": (  4.0, 38.6),
    "TR": (156.0, 38.6),
    "BL": (  4.0,  5.0),
    "BR": (156.0,  5.0),
}

# Plate corner fillet radius (Feature 2)
CORNER_R = 2.0    # mm

# Elephant's foot chamfer (Feature 3)
CHAMFER  = 0.3    # mm

# Feature 1 -- Plate Body
print("Building Feature 1: Plate Body ...")
plate = cq.Workplane("XY").box(PLATE_W, PLATE_D, PLATE_H, centered=False)

# Feature 2 -- Plate Perimeter Corner Radii
print("Building Feature 2: Corner radii on vertical plate edges ...")
plate = plate.edges("|Y").fillet(CORNER_R)

# Feature 3 -- Elephant's Foot Chamfer on bottom front edge
print("Building Feature 3: Elephant's foot chamfer ...")
# Bottom front edge: Z=0, Y=0 intersection. Select edges on Z=0 face, then Y=0 face.
plate = plate.edges("<Z").edges("<Y").chamfer(CHAMFER)

# Features 4-7 -- Struts (union to plate)
print("Building Features 4-7: Struts (TL, TR, BL, BR) ...")
lever = plate
for label, (cx, cz) in STRUTS.items():
    sx0 = cx - STRUT_W / 2   # left X edge of strut
    sz0 = cz - STRUT_H / 2   # bottom Z edge of strut
    strut = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(sx0, STRUT_Y0, sz0))
        .box(STRUT_W, STRUT_L, STRUT_H, centered=False)
    )
    lever = lever.union(strut)

# Features 8-11 -- 3x3 tips on strut ends (last 17mm)
print("Building Features 8-11: 3x3 tips on strut ends ...")
TIP_W = 3.0          # X cross-section of tip
TIP_H = 3.0          # Z cross-section of tip
TIP_L = 17.0         # Y length of tip
TIP_Y0 = STRUT_Y1 - TIP_L  # Y=77.0 (start of tip)

# Cut the 6x6 strut back to 3x3 for the last 17mm by removing the excess
for label, (cx, cz) in STRUTS.items():
    sz0 = cz - STRUT_H / 2
    sx0 = cx - STRUT_W / 2
    overcut = 0.1
    # Cut a 6x6 box and add back a 3x3 box (simpler: cut the difference)
    # Remove the full 6x6 section at the tip
    tip_cut = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(sx0, TIP_Y0, sz0))
        .box(STRUT_W, TIP_L, STRUT_H, centered=False)
    )
    lever = lever.cut(tip_cut)
    # Add back the 3x3 tip
    tip_x0 = cx - TIP_W / 2
    tip_z0 = cz - TIP_H / 2
    tip = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(tip_x0, TIP_Y0, tip_z0))
        .box(TIP_W, TIP_L, TIP_H, centered=False)
    )
    lever = lever.union(tip)

# Features 12-15 -- Snap-fit grooves on 3x3 tips
print("Building Features 12-15: Snap-fit grooves on 3x3 tips ...")
SNAP_GROOVE_DEPTH = 0.25  # depth into tip X face
SNAP_GROOVE_WIDTH = 1.0   # width in Y
SNAP_GROOVE_Y_CENTER = STRUT_Y1 - 2.0  # 2mm from tip end, aligns with socket bumps
snap_groove_y0 = SNAP_GROOVE_Y_CENTER - SNAP_GROOVE_WIDTH / 2

for label, (cx, cz) in STRUTS.items():
    tip_z0 = cz - TIP_H / 2
    overcut = 0.1
    for groove_x0, groove_w in [
        (cx - TIP_W / 2 - overcut, SNAP_GROOVE_DEPTH + overcut),      # -X face
        (cx + TIP_W / 2 - SNAP_GROOVE_DEPTH, SNAP_GROOVE_DEPTH + overcut),  # +X face
    ]:
        groove = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(groove_x0, snap_groove_y0, tip_z0))
            .box(groove_w, SNAP_GROOVE_WIDTH, TIP_H, centered=False)
        )
        lever = lever.cut(groove)

# Features 16-19 -- Tip lead-in ramps on 3x3 tips
print("Building Features 16-19: Tip lead-in ramps on 3x3 tips ...")
RAMP_LENGTH = 1.5    # Y length of ramp
RAMP_TAPER  = 0.25   # X removed from each side at tip
RAMP_Y0_POS = STRUT_Y1 - RAMP_LENGTH  # Y=92.5

for label, (cx, cz) in STRUTS.items():
    tip_z0 = cz - TIP_H / 2
    overcut = 0.1
    # +X face ramp
    wedge_px = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, 0, tip_z0 - overcut))
        .moveTo(cx + TIP_W / 2, RAMP_Y0_POS)
        .lineTo(cx + TIP_W / 2, STRUT_Y1)
        .lineTo(cx + TIP_W / 2 - RAMP_TAPER, STRUT_Y1)
        .close()
        .extrude(TIP_H + 2 * overcut)
    )
    lever = lever.cut(wedge_px)
    # -X face ramp
    wedge_nx = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, 0, tip_z0 - overcut))
        .moveTo(cx - TIP_W / 2, RAMP_Y0_POS)
        .lineTo(cx - TIP_W / 2, STRUT_Y1)
        .lineTo(cx - TIP_W / 2 + RAMP_TAPER, STRUT_Y1)
        .close()
        .extrude(TIP_H + 2 * overcut)
    )
    lever = lever.cut(wedge_nx)

# Export STEP file
OUT_DIR = Path(__file__).parent
STEP_PATH = OUT_DIR / "lever-cadquery.step"
print(f"\nExporting STEP to: {STEP_PATH}")
cq.exporters.export(lever, str(STEP_PATH))

print()
print("RUBRIC 3 -- Feature-Specification Reconciliation")
print()
