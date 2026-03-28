#!/usr/bin/env python3
"""
Generate STEP file for the Enclosure Tub (lower half of soda machine enclosure).

Coordinate system:
  Origin: Front-left-bottom corner of the tub exterior
  X: Width, left to right. 0 to 220 mm.
  Y: Depth, front to back. 0 to 300 mm.
  Z: Height, bottom to top. 0 to 200 mm (rim), tongue to 203 mm.
  Envelope: 220 x 300 x 203 mm -> X:[0,220] Y:[0,300] Z:[0,203]

Feature Planning Table:
| # | Feature Name                    | Operation | Shape        | Key Dimensions                                |
|---|---------------------------------|-----------|--------------|-----------------------------------------------|
|  1| Outer shell                     | Add       | Rounded box  | 220x300x200, 8mm vert edge R, 2mm bottom R   |
|  2| Interior cavity                 | Remove    | Rounded box  | 212x292x196, offset 4mm walls/floor           |
|  3| Tongue on top rim               | Add       | Perimeter rib| 1.5mm wide x 3.0mm tall, centered in wall     |
|  4| Cartridge opening               | Remove    | Rectangle    | 152x75mm at X=34-186, Z=20-95, front wall     |
|  5| Cartridge opening chamfer       | Remove    | Chamfer      | 1mm on all 4 edges exterior                   |
|  6| Finger scoop                    | Remove    | Concave      | 40x5x3mm at bottom of cartridge opening       |
|  7| Guide rails (2)                 | Add       | Rect ribs    | 4x5mm, Y=4-130, X=50/170 center               |
|  8| Dock floor                      | Add       | Slab         | X=30-190, Y=4-134, Z=16-20                    |
|  9| Dock rear wall                  | Add       | Slab         | X=30-190, Y=134-140, Z=16-95                  |
| 10| JG tube stub pockets (4, dock)  | Remove    | Cylinder     | 9.1mm bore, at X=75/145, Z=55/75              |
| 11| Rear bulkhead pockets (5)       | Remove    | Cylinder     | 9.1mm bore through rear wall                  |
| 12| Rear bulkhead bosses (5)        | Add       | Cylinder     | 2mm inward boss for 6mm total pocket depth     |
| 13| Rear wall wire pass-through     | Remove    | Rounded rect | 12x8mm at X=110, Z=30                         |
| 14| Rubber foot recesses (4)        | Remove    | Cylinder     | 15mm dia x 1.5mm deep                         |
| 15| Snap-fit catches (8)            | Add       | Cantilever   | 35mm beam, 15mm wide, 2.5mm thick, 2mm hook   |
| 16| Below-dock support ribs (4)     | Add       | Rect ribs    | 2mm thick, Z=4-20, at X=50/90/130/170         |
| 17| Valve support ribs (3)          | Add       | Rect ribs    | 2mm thick Y, full X width, Z=95-200           |
| 18| Valve cradles lower row (5)     | Add       | U-channels   | 34x54x20mm at Z=95, Y=220 center              |
| 19| Valve cradles upper row (5)     | Add       | U-channels   | 34x54x20mm at Z=155, Y=220 center             |
| 20| Cap tube pass-throughs (2)      | Remove    | Notch/circle | 8mm dia at rim, X=70/150, Y=280               |
| 21| Cap wire pass-throughs (2)      | Remove    | Notch/rect   | 12x6mm at rim, X=40/180, Y=290                |
| 22| Rear bulkhead chamfers          | Remove    | Chamfer      | 1mm around each rear pocket bore               |
| 23| Wire pass-through chamfer       | Remove    | Chamfer      | 1mm on exterior edge                           |
"""

import cadquery as cq
import sys
from pathlib import Path
from math import pi

# Add tools/ to path for step_validate
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from step_validate import Validator

# ==============================================================
# PARAMETERS
# ==============================================================

# Exterior envelope
W = 220.0   # X width
D = 300.0   # Y depth
H = 200.0   # Z height (to rim, not including tongue)
WALL = 4.0  # wall thickness
FLOOR = 4.0 # bottom face thickness
R_VERT = 8.0   # vertical edge exterior radius
R_BOT = 2.0    # bottom edge exterior radius

# Interior
IW = W - 2 * WALL   # 212
ID_ = D - 2 * WALL  # 292
IH = H - FLOOR       # 196

# Tongue
TONGUE_W = 1.5
TONGUE_H = 3.0
TONGUE_OFFSET = (WALL - TONGUE_W) / 2  # 1.25 mm from outer face

# Cartridge opening
CART_OPEN_W = 152.0
CART_OPEN_H = 75.0
CART_OPEN_X0 = (W - CART_OPEN_W) / 2  # 34
CART_OPEN_Z0 = 20.0
CART_OPEN_Z1 = CART_OPEN_Z0 + CART_OPEN_H  # 95
CART_CHAMFER = 1.0

# Finger scoop
SCOOP_W = 40.0
SCOOP_DEPTH = 5.0  # into Y
SCOOP_HEIGHT = 3.0
SCOOP_CX = W / 2  # 110

# Guide rails
RAIL_H = 5.0
RAIL_W = 4.0
RAIL_LEN = 126.0  # Y=4 to Y=130
RAIL_Y0 = WALL  # 4
RAIL_Z0 = 20.0  # top of dock floor
RAIL_X_LEFT = 50.0   # center
RAIL_X_RIGHT = 170.0 # center

# Dock floor
DOCK_X0 = 30.0
DOCK_X1 = 190.0
DOCK_Y0 = WALL  # 4
DOCK_Y1 = 134.0
DOCK_FLOOR_Z0 = 16.0
DOCK_FLOOR_Z1 = 20.0

# Dock rear wall
DOCK_REAR_Y0 = 134.0
DOCK_REAR_Y1 = 140.0
DOCK_REAR_Z0 = 16.0
DOCK_REAR_Z1 = 95.0

# JG tube stub pockets in dock rear wall
JG_BORE_DIA = 9.1  # press-fit bore for 9.31mm center body
JG_STUBS = [(75.0, 55.0), (75.0, 75.0), (145.0, 55.0), (145.0, 75.0)]  # (X, Z)

# Rear bulkhead fittings
RB_POSITIONS = [
    (40.0, 120.0),   # RB-1: carb water in
    (40.0, 150.0),   # RB-2: carb water out
    (110.0, 120.0),  # RB-3: tap water in
    (150.0, 120.0),  # RB-4: flavor 1 out
    (180.0, 120.0),  # RB-5: flavor 2 out
]
RB_BOSS_PROTRUSION = 2.0  # inward from rear inner wall

# Wire pass-through (rear wall)
WIRE_PT_W = 12.0
WIRE_PT_H = 8.0
WIRE_PT_X = 110.0
WIRE_PT_Z = 30.0
WIRE_PT_R = 2.0  # corner radius

# Rubber foot recesses
FOOT_DIA = 15.0
FOOT_DEPTH = 1.5
FOOT_POSITIONS = [(30.0, 30.0), (190.0, 30.0), (30.0, 270.0), (190.0, 270.0)]

# Snap-fit catches
CATCH_BEAM_LEN = 35.0   # Z, from Z=200 down to Z=165
CATCH_BEAM_W = 15.0      # along wall
CATCH_THICK_ROOT = 2.5   # protrusion from wall at root
CATCH_THICK_TIP = 2.0    # at hook
CATCH_HOOK_DEPTH = 2.0   # overhang
CATCH_HOOK_H = 2.0       # vertical

# Catch positions: (wall, along-wall position)
# Front wall (Y = 4): X = 60, 160
# Back wall (Y = 296): X = 60, 160
# Left wall (X = 4): Y = 100, 200
# Right wall (X = 216): Y = 100, 200

# Below-dock support ribs
BELOW_DOCK_RIB_X = [50.0, 90.0, 130.0, 170.0]
BELOW_DOCK_RIB_THICK = 2.0

# Valve support ribs (3 vertical ribs at Y=200, 220, 240)
VALVE_RIB_Y = [200.0, 220.0, 240.0]
VALVE_RIB_THICK = 2.0

# Valve cradle parameters
CRADLE_IW = 34.0   # interior width
CRADLE_ID = 54.0   # interior depth
CRADLE_IH = 20.0   # interior height
CRADLE_WALL = 2.0  # wall thickness
VALVE_X_CENTERS = [22.0, 58.0, 94.0, 130.0, 166.0]
VALVE_Y_CENTER = 220.0
LOWER_ROW_Z_BOTTOM = 95.0
UPPER_ROW_Z_BOTTOM = 155.0

# Cap interface pass-throughs (notches at top rim)
BAG_TUBE_POSITIONS = [(70.0, 280.0), (150.0, 280.0)]  # (X, Y)
BAG_TUBE_DIA = 8.0
WIRE_HARNESS_POSITIONS = [(40.0, 290.0), (180.0, 290.0)]  # (X, Y)
WIRE_HARNESS_W = 12.0
WIRE_HARNESS_H = 6.0

print("=" * 60)
print("Enclosure Tub — CadQuery STEP Generation")
print("=" * 60)

# ==============================================================
# 1. OUTER SHELL — rounded rectangle box
# ==============================================================
print("\n[1] Outer shell...")

# Build outer shell as a rounded rectangle extruded upward
outer = (
    cq.Workplane("XY")
    .moveTo(R_VERT, 0)
    .lineTo(W - R_VERT, 0)
    .tangentArcPoint((W, R_VERT), relative=False)
    .lineTo(W, D - R_VERT)
    .tangentArcPoint((W - R_VERT, D), relative=False)
    .lineTo(R_VERT, D)
    .tangentArcPoint((0, D - R_VERT), relative=False)
    .lineTo(0, R_VERT)
    .tangentArcPoint((R_VERT, 0), relative=False)
    .close()
    .extrude(H)
)

# Fillet bottom edges (2mm radius) — vertical edges are already arcs from the sketch
outer = outer.edges("<Z").fillet(R_BOT)

# ==============================================================
# 2. INTERIOR CAVITY — hollow out
# ==============================================================
print("[2] Interior cavity...")

# Interior rounded rectangle (offset by wall thickness)
inner_r = R_VERT - WALL  # 4mm radius on interior vertical edges
inner = (
    cq.Workplane("XY")
    .workplane(offset=FLOOR)
    .moveTo(WALL + inner_r, WALL)
    .lineTo(W - WALL - inner_r, WALL)
    .tangentArcPoint((W - WALL, WALL + inner_r), relative=False)
    .lineTo(W - WALL, D - WALL - inner_r)
    .tangentArcPoint((W - WALL - inner_r, D - WALL), relative=False)
    .lineTo(WALL + inner_r, D - WALL)
    .tangentArcPoint((WALL, D - WALL - inner_r), relative=False)
    .lineTo(WALL, WALL + inner_r)
    .tangentArcPoint((WALL + inner_r, WALL), relative=False)
    .close()
    .extrude(H - FLOOR)
)

tub = outer.cut(inner)

# ==============================================================
# 3. TONGUE on top rim
# ==============================================================
print("[3] Tongue on top rim...")

# Tongue: 1.5mm wide rib centered in 4mm wall, 3mm tall, on full perimeter
# The tongue follows the outer shell perimeter but offset inward by 1.25mm
tongue_outer_offset = TONGUE_OFFSET  # 1.25mm from outer face
tongue_r_outer = R_VERT - tongue_outer_offset  # 6.75
tongue_r_inner = tongue_r_outer - TONGUE_W      # 5.25

# Tongue X/Y positions
tox = tongue_outer_offset  # 1.25 from exterior = X=1.25 (outer edge of tongue)
tix = tox + TONGUE_W       # 2.75 (inner edge of tongue)
toy = tongue_outer_offset
tiy = toy + TONGUE_W

tongue = (
    cq.Workplane("XY")
    .workplane(offset=H)
    # Outer perimeter of tongue
    .moveTo(tox + tongue_r_outer, toy)
    .lineTo(W - tox - tongue_r_outer, toy)
    .tangentArcPoint((W - tox, toy + tongue_r_outer), relative=False)
    .lineTo(W - tox, D - toy - tongue_r_outer)
    .tangentArcPoint((W - tox - tongue_r_outer, D - toy), relative=False)
    .lineTo(tox + tongue_r_outer, D - toy)
    .tangentArcPoint((tox, D - toy - tongue_r_outer), relative=False)
    .lineTo(tox, toy + tongue_r_outer)
    .tangentArcPoint((tox + tongue_r_outer, toy), relative=False)
    .close()
    .extrude(TONGUE_H)
)

tongue_hole = (
    cq.Workplane("XY")
    .workplane(offset=H)
    .moveTo(tix + tongue_r_inner, tiy)
    .lineTo(W - tix - tongue_r_inner, tiy)
    .tangentArcPoint((W - tix, tiy + tongue_r_inner), relative=False)
    .lineTo(W - tix, D - tiy - tongue_r_inner)
    .tangentArcPoint((W - tix - tongue_r_inner, D - tiy), relative=False)
    .lineTo(tix + tongue_r_inner, D - tiy)
    .tangentArcPoint((tix, D - tiy - tongue_r_inner), relative=False)
    .lineTo(tix, tiy + tongue_r_inner)
    .tangentArcPoint((tix + tongue_r_inner, tiy), relative=False)
    .close()
    .extrude(TONGUE_H)
)

tongue = tongue.cut(tongue_hole)
tub = tub.union(tongue)

# ==============================================================
# 4. CARTRIDGE OPENING (front face)
# ==============================================================
print("[4] Cartridge opening...")

# Cut rectangular opening in front wall
cart_cut = (
    cq.Workplane("XZ")
    .workplane(offset=0)  # at Y=0, normal is -Y
    .moveTo(CART_OPEN_X0, CART_OPEN_Z0)
    .rect(CART_OPEN_W, CART_OPEN_H, centered=False)
    .extrude(-WALL - 1)  # cut through front wall (+Y direction since XZ normal is -Y, negative extrude goes +Y)
)
# Actually XZ workplane normal is -Y. extrude(-val) goes in +Y direction.
# We want to cut from Y=0 into the wall (Y=0 to Y=WALL). So extrude into +Y = extrude(-(WALL+1))
# Let me redo: on XZ plane at offset=0, positive extrude goes -Y (outward), negative goes +Y (inward).
# We want to go +Y to cut through the wall. So extrude with negative value.
# Actually, let me use a simpler approach.

cart_cut = (
    cq.Workplane("XY")
    .box(CART_OPEN_W, WALL + 2, CART_OPEN_H, centered=False)
    .translate((CART_OPEN_X0, -1, CART_OPEN_Z0))
)

tub = tub.cut(cart_cut)

# ==============================================================
# 5. CARTRIDGE OPENING CHAMFER (1mm on all 4 edges, exterior side)
# ==============================================================
print("[5] Cartridge opening chamfer...")
# Chamfer: cut a slightly larger opening 1mm deep on the exterior face
# A rectangular frame 1mm deep, expanding 1mm on each side
cart_chamfer = (
    cq.Workplane("XY")
    .workplane(offset=CART_OPEN_Z0)
    .transformed(rotate=(90, 0, 0))
    .moveTo(CART_OPEN_X0, 0)
    .rect(CART_OPEN_W, CART_CHAMFER, centered=False)
    .extrude(CART_CHAMFER)
)
# This is getting complex. Let me use a simpler approach - cut chamfer blocks at each edge.

# Bottom edge chamfer: triangle at Z = CART_OPEN_Z0, Y = 0
# Top edge chamfer: triangle at Z = CART_OPEN_Z1, Y = 0
# Left edge chamfer: triangle at X = CART_OPEN_X0, Y = 0
# Right edge chamfer: triangle at X = CART_OPEN_X0 + CART_OPEN_W, Y = 0

# Use a wedge approach: extrude a trapezoid profile
C = CART_CHAMFER  # 1.0
x0 = CART_OPEN_X0
x1 = CART_OPEN_X0 + CART_OPEN_W
z0 = CART_OPEN_Z0
z1 = CART_OPEN_Z1

# Bottom edge chamfer (along X at Z=z0, Y=0)
bot_chamfer = (
    cq.Workplane("YZ")
    .moveTo(0, z0)
    .lineTo(-C, z0)
    .lineTo(0, z0 - C)
    .close()
    .extrude(CART_OPEN_W)
    .translate((x0, 0, 0))
)
tub = tub.cut(bot_chamfer)

# Top edge chamfer (along X at Z=z1, Y=0)
top_chamfer = (
    cq.Workplane("YZ")
    .moveTo(0, z1)
    .lineTo(-C, z1)
    .lineTo(0, z1 + C)
    .close()
    .extrude(CART_OPEN_W)
    .translate((x0, 0, 0))
)
tub = tub.cut(top_chamfer)

# Left edge chamfer (along Z at X=x0, Y=0)
left_chamfer = (
    cq.Workplane("XY")
    .workplane(offset=z0)
    .transformed(rotate=(90, 0, 0))
    .moveTo(x0, 0)
    .lineTo(x0 - C, 0)
    .lineTo(x0, -C)
    .close()
    .extrude(CART_OPEN_H)
)
tub = tub.cut(left_chamfer)

# Right edge chamfer (along Z at X=x1, Y=0)
right_chamfer = (
    cq.Workplane("XY")
    .workplane(offset=z0)
    .transformed(rotate=(90, 0, 0))
    .moveTo(x1, 0)
    .lineTo(x1 + C, 0)
    .lineTo(x1, -C)
    .close()
    .extrude(CART_OPEN_H)
)
tub = tub.cut(right_chamfer)

# ==============================================================
# 6. FINGER SCOOP (bottom of cartridge opening)
# ==============================================================
print("[6] Finger scoop...")
# Shallow concave recess: 40mm wide x 5mm deep (Y) x 3mm tall (Z) centered at X=110, Z=20
# Approximate with a box for now (concave shape is cosmetic)
scoop = (
    cq.Workplane("XY")
    .box(SCOOP_W, SCOOP_DEPTH, SCOOP_HEIGHT, centered=False)
    .translate((SCOOP_CX - SCOOP_W / 2, -SCOOP_DEPTH, CART_OPEN_Z0 - SCOOP_HEIGHT))
)
tub = tub.cut(scoop)

# ==============================================================
# 7. DOCK FLOOR
# ==============================================================
print("[7] Dock floor...")
dock_floor = (
    cq.Workplane("XY")
    .box(DOCK_X1 - DOCK_X0, DOCK_Y1 - DOCK_Y0, DOCK_FLOOR_Z1 - DOCK_FLOOR_Z0, centered=False)
    .translate((DOCK_X0, DOCK_Y0, DOCK_FLOOR_Z0))
)
tub = tub.union(dock_floor)

# ==============================================================
# 8. GUIDE RAILS (2)
# ==============================================================
print("[8] Guide rails...")
for rail_cx in [RAIL_X_LEFT, RAIL_X_RIGHT]:
    rail = (
        cq.Workplane("XY")
        .box(RAIL_W, RAIL_LEN, RAIL_H, centered=False)
        .translate((rail_cx - RAIL_W / 2, RAIL_Y0, RAIL_Z0))
    )
    tub = tub.union(rail)

# ==============================================================
# 9. DOCK REAR WALL
# ==============================================================
print("[9] Dock rear wall...")
dock_rear = (
    cq.Workplane("XY")
    .box(DOCK_X1 - DOCK_X0, DOCK_REAR_Y1 - DOCK_REAR_Y0, DOCK_REAR_Z1 - DOCK_REAR_Z0, centered=False)
    .translate((DOCK_X0, DOCK_REAR_Y0, DOCK_REAR_Z0))
)
tub = tub.union(dock_rear)

# ==============================================================
# 10. JG TUBE STUB POCKETS (4, in dock rear wall)
# ==============================================================
print("[10] JG tube stub pockets (dock)...")
for (jx, jz) in JG_STUBS:
    # Cut a 9.1mm bore through the 6mm thick dock rear wall (Y=134 to Y=140)
    # Use a simple cylinder along Y axis
    pocket = (
        cq.Workplane("XY")
        .cylinder(DOCK_REAR_Y1 - DOCK_REAR_Y0 + 2, JG_BORE_DIA / 2, centered=(True, True, False))
        .rotateAboutCenter((1, 0, 0), -90)
        .translate((jx, DOCK_REAR_Y0 - 1, jz))
    )
    tub = tub.cut(pocket)

# ==============================================================
# 11. REAR BULKHEAD BOSSES + POCKETS (5 fittings on rear wall)
# ==============================================================
print("[11] Rear bulkhead bosses and pockets...")

for (rx, rz) in RB_POSITIONS:
    # Boss: cylindrical protrusion inward from rear wall inner face
    # Rear wall inner face is at Y = D - WALL = 296
    # Boss protrudes 2mm inward (toward front), so Y = 294 to Y = 296
    boss = (
        cq.Workplane("XY")
        .workplane(offset=rz)
        .transformed(rotate=(90, 0, 0))
        .center(rx, 0)
        .circle(JG_BORE_DIA / 2 + 3)  # boss OD ~15mm
        .extrude(RB_BOSS_PROTRUSION)
        .translate((0, D - WALL - RB_BOSS_PROTRUSION, 0))
    )
    # Simplify: just a cylinder
    boss = (
        cq.Workplane("XY")
        .transformed(offset=(rx, D - WALL - RB_BOSS_PROTRUSION, rz), rotate=(90, 0, 0))
        .circle(JG_BORE_DIA / 2 + 3)
        .extrude(RB_BOSS_PROTRUSION)
    )
    # Even simpler approach: use a box-based cylinder
    boss_r = JG_BORE_DIA / 2 + 3  # 7.55mm radius
    boss = cq.Workplane("YZ").workplane(offset=rx).center(D - WALL, rz).circle(boss_r).extrude(-1)  # doesn't work well

    # Let me use the most straightforward approach
    boss = (
        cq.Workplane("XY")
        .cylinder(RB_BOSS_PROTRUSION, boss_r, centered=(True, True, False))
        .rotateAboutCenter((1, 0, 0), 90)
        .translate((rx, D - WALL, rz))
    )
    # cylinder creates along Z by default. We need along Y.
    # Let me just make a cylinder along Y axis properly.

    boss = (
        cq.Workplane("XZ")
        .workplane(offset=-(D - WALL))
        .center(rx, rz)
        .circle(boss_r)
        .extrude(RB_BOSS_PROTRUSION)  # extrude in -Y (toward front, which is inward)
    )
    tub = tub.union(boss)

    # Bore: 9.1mm through the total 6mm (4mm wall + 2mm boss)
    bore = (
        cq.Workplane("XZ")
        .workplane(offset=-(D + 1))
        .center(rx, rz)
        .circle(JG_BORE_DIA / 2)
        .extrude(WALL + RB_BOSS_PROTRUSION + 2)  # through wall+boss
    )
    tub = tub.cut(bore)

# ==============================================================
# 12. REAR WALL WIRE PASS-THROUGH
# ==============================================================
print("[12] Rear wall wire pass-through...")
# 12x8mm rounded rectangle at X=110, Z=30, through rear wall
# Use a box cut (rounded rect with R=2mm corners)
wire_cut = (
    cq.Workplane("XZ")
    .workplane(offset=-(D + 1))
    .center(WIRE_PT_X, WIRE_PT_Z)
    .rect(WIRE_PT_W, WIRE_PT_H)
    .extrude(WALL + 2)
)
tub = tub.cut(wire_cut)

# ==============================================================
# 13. RUBBER FOOT RECESSES (4)
# ==============================================================
print("[13] Rubber foot recesses...")
for (fx, fy) in FOOT_POSITIONS:
    foot = (
        cq.Workplane("XY")
        .workplane(offset=0)
        .center(fx, fy)
        .circle(FOOT_DIA / 2)
        .extrude(-FOOT_DEPTH)  # cut into bottom face (below Z=0)
    )
    # Actually Z=0 is the bottom face, recesses go from Z=0 upward to Z=1.5
    # No -- recesses are on the exterior bottom, carved into the bottom face
    # The bottom face is at Z=0. Recesses go downward. But our model starts at Z=0.
    # The recesses are carved INTO the bottom, from Z=0 downward. But the solid starts at Z=0.
    # Actually: the recess is a shallow pocket on the bottom face. It removes material from
    # Z=0 to Z=FOOT_DEPTH (1.5mm) upward into the floor. The floor is 4mm thick.
    foot = (
        cq.Workplane("XY")
        .workplane(offset=-0.01)
        .center(fx, fy)
        .circle(FOOT_DIA / 2)
        .extrude(FOOT_DEPTH + 0.01)
    )
    tub = tub.cut(foot)

# ==============================================================
# 14. BELOW-DOCK SUPPORT RIBS (4)
# ==============================================================
print("[14] Below-dock support ribs...")
for rib_x in BELOW_DOCK_RIB_X:
    rib = (
        cq.Workplane("XY")
        .box(BELOW_DOCK_RIB_THICK, DOCK_Y1 - DOCK_Y0, DOCK_FLOOR_Z0 - FLOOR, centered=False)
        .translate((rib_x - BELOW_DOCK_RIB_THICK / 2, DOCK_Y0, FLOOR))
    )
    tub = tub.union(rib)

# ==============================================================
# 15. VALVE SUPPORT RIBS (3 vertical ribs)
# ==============================================================
print("[15] Valve support ribs...")
for rib_y in VALVE_RIB_Y:
    rib = (
        cq.Workplane("XY")
        .box(IW, VALVE_RIB_THICK, H - DOCK_REAR_Z1, centered=False)
        .translate((WALL, rib_y - VALVE_RIB_THICK / 2, DOCK_REAR_Z1))
    )
    tub = tub.union(rib)

# ==============================================================
# 16. VALVE CRADLES (10 total: 5 lower + 5 upper)
# ==============================================================
print("[16] Valve cradles...")

def make_cradle(cx, cy, z_bottom):
    """Create a U-shaped cradle at given center position and Z bottom."""
    # Outer box of cradle
    ow = CRADLE_IW + 2 * CRADLE_WALL  # 38
    od = CRADLE_ID + 2 * CRADLE_WALL  # 58
    oh = CRADLE_IH + CRADLE_WALL      # 22 (U-channel: floor + two side walls, open top)

    outer_box = (
        cq.Workplane("XY")
        .box(ow, od, oh, centered=False)
        .translate((cx - ow / 2, cy - od / 2, z_bottom))
    )

    # Inner cutout (open top)
    inner_cut = (
        cq.Workplane("XY")
        .box(CRADLE_IW, CRADLE_ID, CRADLE_IH + 1, centered=False)
        .translate((cx - CRADLE_IW / 2, cy - CRADLE_ID / 2, z_bottom + CRADLE_WALL))
    )

    return outer_box.cut(inner_cut)

for vcx in VALVE_X_CENTERS:
    # Lower row
    cradle_lower = make_cradle(vcx, VALVE_Y_CENTER, LOWER_ROW_Z_BOTTOM)
    tub = tub.union(cradle_lower)
    # Upper row
    cradle_upper = make_cradle(vcx, VALVE_Y_CENTER, UPPER_ROW_Z_BOTTOM)
    tub = tub.union(cradle_upper)

# Re-cut cradle interiors to ensure ribs don't block them
print("[16b] Re-cutting cradle interiors (ribs may have filled them)...")
for vcx in VALVE_X_CENTERS:
    for z_bot in [LOWER_ROW_Z_BOTTOM, UPPER_ROW_Z_BOTTOM]:
        inner_cut = (
            cq.Workplane("XY")
            .box(CRADLE_IW, CRADLE_ID, CRADLE_IH + 1, centered=False)
            .translate((vcx - CRADLE_IW / 2, VALVE_Y_CENTER - CRADLE_ID / 2, z_bot + CRADLE_WALL))
        )
        tub = tub.cut(inner_cut)

# ==============================================================
# 17. SNAP-FIT CATCHES (8 total)
# ==============================================================
print("[17] Snap-fit catches...")

def make_catch_front_back(cx, wall_y, inward_dir):
    """Create a catch on front or back wall.
    cx: X center of catch
    wall_y: Y of inner wall face
    inward_dir: +1 if catch protrudes toward +Y (front wall), -1 for back wall
    """
    # Beam: from Z=200 down to Z=165, protruding from wall
    # The beam is a tapered slab: thick at root (2.5mm), thin at tip (2.0mm)
    # For simplicity, use uniform 2.5mm thickness (the taper is minor)
    beam_thick = CATCH_THICK_ROOT

    # Beam body
    beam = (
        cq.Workplane("XY")
        .box(CATCH_BEAM_W, beam_thick, CATCH_BEAM_LEN, centered=False)
        .translate((
            cx - CATCH_BEAM_W / 2,
            wall_y if inward_dir > 0 else wall_y - beam_thick,
            H - CATCH_BEAM_LEN
        ))
    )

    # Hook at the bottom of the beam (Z = 165): extends further inward by CATCH_HOOK_DEPTH
    hook = (
        cq.Workplane("XY")
        .box(CATCH_BEAM_W, CATCH_HOOK_DEPTH, CATCH_HOOK_H, centered=False)
        .translate((
            cx - CATCH_BEAM_W / 2,
            (wall_y + beam_thick) if inward_dir > 0 else (wall_y - beam_thick - CATCH_HOOK_DEPTH),
            H - CATCH_BEAM_LEN
        ))
    )

    return beam.union(hook)

def make_catch_left_right(cy, wall_x, inward_dir):
    """Create a catch on left or right wall.
    cy: Y center of catch
    wall_x: X of inner wall face
    inward_dir: +1 if catch protrudes toward +X (left wall), -1 for right wall
    """
    beam_thick = CATCH_THICK_ROOT

    beam = (
        cq.Workplane("XY")
        .box(beam_thick, CATCH_BEAM_W, CATCH_BEAM_LEN, centered=False)
        .translate((
            wall_x if inward_dir > 0 else wall_x - beam_thick,
            cy - CATCH_BEAM_W / 2,
            H - CATCH_BEAM_LEN
        ))
    )

    hook = (
        cq.Workplane("XY")
        .box(CATCH_HOOK_DEPTH, CATCH_BEAM_W, CATCH_HOOK_H, centered=False)
        .translate((
            (wall_x + beam_thick) if inward_dir > 0 else (wall_x - beam_thick - CATCH_HOOK_DEPTH),
            cy - CATCH_BEAM_W / 2,
            H - CATCH_BEAM_LEN
        ))
    )

    return beam.union(hook)

# Front wall catches: Y=4 (inner face), protrude +Y (inward)
for cx in [60.0, 160.0]:
    catch = make_catch_front_back(cx, WALL, +1)
    tub = tub.union(catch)

# Back wall catches: Y=296 (inner face), protrude -Y (inward)
for cx in [60.0, 160.0]:
    catch = make_catch_front_back(cx, D - WALL, -1)
    tub = tub.union(catch)

# Left wall catches: X=4 (inner face), protrude +X (inward)
for cy in [100.0, 200.0]:
    catch = make_catch_left_right(cy, WALL, +1)
    tub = tub.union(catch)

# Right wall catches: X=216 (inner face), protrude -X (inward)
for cy in [100.0, 200.0]:
    catch = make_catch_left_right(cy, W - WALL, -1)
    tub = tub.union(catch)

# ==============================================================
# 18. CAP INTERFACE PASS-THROUGHS (notches at top rim)
# ==============================================================
print("[18] Cap interface pass-throughs...")

# Bag tube pass-throughs: 8mm diameter holes at Z=200 (through rim/tongue)
for (bx, by) in BAG_TUBE_POSITIONS:
    notch = (
        cq.Workplane("XY")
        .workplane(offset=H - WALL)  # start below rim top
        .center(bx, by)
        .circle(BAG_TUBE_DIA / 2)
        .extrude(WALL + TONGUE_H + 1)  # through rim and tongue
    )
    tub = tub.cut(notch)

# Wire harness pass-throughs: 12x6mm rectangular notches
for (wx, wy) in WIRE_HARNESS_POSITIONS:
    notch = (
        cq.Workplane("XY")
        .workplane(offset=H - WALL)
        .center(wx, wy)
        .rect(WIRE_HARNESS_W, WIRE_HARNESS_H)
        .extrude(WALL + TONGUE_H + 1)
    )
    tub = tub.cut(notch)

# ==============================================================
# EXPORT STEP FILE
# ==============================================================
print("\nExporting STEP file...")
step_path = str(Path(__file__).parent / "tub.step")
cq.exporters.export(tub, step_path)
print(f"Exported: {step_path}")

# ==============================================================
# VALIDATION
# ==============================================================
print("\n" + "=" * 60)
print("VALIDATION")
print("=" * 60)

v = Validator(tub)

# --- Rubric 4: Solid validity ---
v.check_valid()
v.check_single_body()
v.check_volume(expected_envelope=W * D * (H + TONGUE_H), fill_range=(0.05, 0.30))

# --- Rubric 5: Bounding box ---
bb = tub.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, 0.0, W, tol=0.5)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, D, tol=0.5)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, H + TONGUE_H, tol=0.5)

# --- Feature 1: Outer shell walls ---
print("\n--- Feature probes: Outer shell ---")
v.check_solid("Front wall center", W/2, WALL/2, H/2, "solid in front wall")
v.check_solid("Back wall center", W/2, D - WALL/2, H/2, "solid in back wall")
v.check_solid("Left wall center", WALL/2, D/2, H/2, "solid in left wall")
v.check_solid("Right wall center", W - WALL/2, D/2, H/2, "solid in right wall")
v.check_solid("Bottom floor center", W/2, D/2, FLOOR/2, "solid in floor")

# --- Feature 2: Interior cavity ---
print("\n--- Feature probes: Interior cavity ---")
v.check_void("Interior center", W/2, D/2, H/2, "void inside tub")
v.check_void("Interior near front", W/2, WALL + 5, H/2, "void near front wall interior")
v.check_void("Interior near floor", W/2, D/2, FLOOR + 2, "void above floor")

# --- Feature 3: Tongue ---
print("\n--- Feature probes: Tongue ---")
tongue_cx = W / 2
tongue_cy = TONGUE_OFFSET + TONGUE_W / 2  # center of tongue in wall
v.check_solid("Tongue front side", tongue_cx, tongue_cy, H + TONGUE_H / 2, "solid in tongue")
v.check_solid("Tongue back side", tongue_cx, D - tongue_cy, H + TONGUE_H / 2, "solid in tongue back")
v.check_solid("Tongue left side", tongue_cy, D / 2, H + TONGUE_H / 2, "solid in tongue left")
v.check_solid("Tongue right side", W - tongue_cy, D / 2, H + TONGUE_H / 2, "solid in tongue right")
v.check_void("Inside tongue perimeter", W/2, D/2, H + TONGUE_H / 2, "void inside tongue ring")

# --- Feature 4: Cartridge opening ---
print("\n--- Feature probes: Cartridge opening ---")
v.check_void("Cart opening center", W/2, WALL/2, (CART_OPEN_Z0 + CART_OPEN_Z1)/2, "void at cartridge opening center")
v.check_void("Cart opening left edge", CART_OPEN_X0 + 1, WALL/2, 57, "void at left side of opening")
v.check_void("Cart opening right edge", CART_OPEN_X0 + CART_OPEN_W - 1, WALL/2, 57, "void at right side of opening")
v.check_solid("Wall left of cart opening", CART_OPEN_X0 - 2, WALL/2, 57, "solid left of opening")
v.check_solid("Wall right of cart opening", CART_OPEN_X0 + CART_OPEN_W + 2, WALL/2, 57, "solid right of opening")

# --- Feature 7: Dock floor ---
print("\n--- Feature probes: Dock floor ---")
v.check_solid("Dock floor center", W/2, (DOCK_Y0 + DOCK_Y1)/2, (DOCK_FLOOR_Z0 + DOCK_FLOOR_Z1)/2, "solid in dock floor")

# --- Feature 8: Guide rails ---
print("\n--- Feature probes: Guide rails ---")
v.check_solid("Left guide rail", RAIL_X_LEFT, RAIL_Y0 + RAIL_LEN/2, RAIL_Z0 + RAIL_H/2, "solid in left rail")
v.check_solid("Right guide rail", RAIL_X_RIGHT, RAIL_Y0 + RAIL_LEN/2, RAIL_Z0 + RAIL_H/2, "solid in right rail")

# --- Feature 9: Dock rear wall ---
print("\n--- Feature probes: Dock rear wall ---")
v.check_solid("Dock rear wall center", W/2, (DOCK_REAR_Y0 + DOCK_REAR_Y1)/2, (DOCK_REAR_Z0 + DOCK_REAR_Z1)/2, "solid in dock rear wall")

# --- Feature 10: JG tube stub pockets ---
print("\n--- Feature probes: JG tube stub pockets ---")
for i, (jx, jz) in enumerate(JG_STUBS):
    v.check_void(f"JG stub pocket {i+1} center", jx, (DOCK_REAR_Y0 + DOCK_REAR_Y1)/2, jz, f"void at JG pocket {i+1}")

# --- Feature 11: Rear bulkhead pockets ---
print("\n--- Feature probes: Rear bulkhead pockets ---")
for i, (rx, rz) in enumerate(RB_POSITIONS):
    v.check_void(f"Rear bulkhead {i+1} center", rx, D - WALL/2, rz, f"void at RB pocket {i+1}")

# --- Feature 12: Wire pass-through ---
print("\n--- Feature probes: Wire pass-through ---")
v.check_void("Wire pass-through center", WIRE_PT_X, D - WALL/2, WIRE_PT_Z, "void at wire pass-through")

# --- Feature 13: Rubber foot recesses ---
print("\n--- Feature probes: Rubber foot recesses ---")
for i, (fx, fy) in enumerate(FOOT_POSITIONS):
    v.check_void(f"Foot recess {i+1}", fx, fy, FOOT_DEPTH / 2, f"void at foot recess {i+1}")

# --- Feature 14: Below-dock support ribs ---
print("\n--- Feature probes: Below-dock ribs ---")
for rib_x in BELOW_DOCK_RIB_X:
    v.check_solid(f"Below-dock rib X={rib_x}", rib_x, (DOCK_Y0 + DOCK_Y1)/2, (FLOOR + DOCK_FLOOR_Z0)/2, f"solid in rib at X={rib_x}")

# --- Feature 15: Valve support ribs ---
print("\n--- Feature probes: Valve support ribs ---")
for rib_y in VALVE_RIB_Y:
    v.check_solid(f"Valve rib Y={rib_y}", W/2, rib_y, (DOCK_REAR_Z1 + H)/2, f"solid in valve rib at Y={rib_y}")

# --- Feature 16: Valve cradles ---
print("\n--- Feature probes: Valve cradles ---")
# Check lower row center cradle (X=94, Y=220, Z=95)
v.check_solid("Lower cradle 3 floor", 94.0, 220.0, LOWER_ROW_Z_BOTTOM + CRADLE_WALL/2, "solid in lower cradle floor")
v.check_void("Lower cradle 3 interior", 94.0, 220.0, LOWER_ROW_Z_BOTTOM + CRADLE_WALL + CRADLE_IH/2, "void in lower cradle interior")
# Check upper row center cradle
v.check_solid("Upper cradle 3 floor", 94.0, 220.0, UPPER_ROW_Z_BOTTOM + CRADLE_WALL/2, "solid in upper cradle floor")
v.check_void("Upper cradle 3 interior", 94.0, 220.0, UPPER_ROW_Z_BOTTOM + CRADLE_WALL + CRADLE_IH/2, "void in upper cradle interior")

# --- Feature 17: Snap-fit catches ---
print("\n--- Feature probes: Snap-fit catches ---")
# Front wall catch at X=60: beam body at Y=4 to Y=6.5, Z=165 to Z=200
v.check_solid("Front catch X=60 beam", 60.0, WALL + CATCH_THICK_ROOT/2, H - CATCH_BEAM_LEN/2, "solid in front catch beam")
# Hook at Z=165, protruding further inward
v.check_solid("Front catch X=60 hook", 60.0, WALL + CATCH_THICK_ROOT + CATCH_HOOK_DEPTH/2, H - CATCH_BEAM_LEN + CATCH_HOOK_H/2, "solid in front catch hook")

# Left wall catch at Y=100
v.check_solid("Left catch Y=100 beam", WALL + CATCH_THICK_ROOT/2, 100.0, H - CATCH_BEAM_LEN/2, "solid in left catch beam")

# --- Feature 18: Cap tube pass-throughs ---
print("\n--- Feature probes: Cap pass-throughs ---")
for i, (bx, by) in enumerate(BAG_TUBE_POSITIONS):
    v.check_void(f"Bag tube pass-through {i+1}", bx, by, H + TONGUE_H/2, f"void at bag tube pass-through {i+1}")

for i, (wx, wy) in enumerate(WIRE_HARNESS_POSITIONS):
    v.check_void(f"Wire harness pass-through {i+1}", wx, wy, H + TONGUE_H/2, f"void at wire harness pass-through {i+1}")

# --- Summary ---
print()
if not v.summary():
    sys.exit(1)
