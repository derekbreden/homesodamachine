#!/usr/bin/env python3
"""
Enclosure Cap — CadQuery STEP Generation Script

Generates the upper half (cap) of the home soda machine enclosure.

Coordinate system:
  Origin: Front-left-bottom corner of enclosure exterior (shared with tub)
  X: Width, left to right. 0 to 220 mm (at bottom rim Z=200)
  Y: Depth, front to back. 0 to 300 mm (at bottom rim Z=200)
  Z: Height, bottom to top. Cap spans Z=196.8 (groove bottom) to Z=402 (lip top)
  Envelope at bottom rim: 220 x 300 x 200 mm

  Draft: 3-degree inward taper. Cap is widest at bottom rim (Z=200),
         narrowest at top (Z=400).

  Reveal: Cap exterior at Z=200 is inset 0.8 mm per side from tub.
          Cap exterior at Z=200: X=[0.8, 219.2], Y=[0.8, 299.2].

  Bottom rim construction: The rim has two legs (outer and inner) that
  extend 3.2 mm below Z=200 to form the groove walls. The 1.7 mm wide
  groove between the legs receives the tub's tongue.

Feature Planning Table (Rubric 1):
| #  | Feature Name                    | Mechanical Function                | Op     | Shape              | Axis | Center (X,Y,Z)            | Dimensions                            |
|----|--------------------------------|------------------------------------|---------|--------------------|------|----------------------------|---------------------------------------|
| 1  | Outer shell                    | Enclosure exterior with draft      | Add     | Drafted box        | Z    | 110,150,300                | 220x300 base, 3deg draft, R8 vert     |
| 2  | Inner cavity                   | Hollow interior                    | Remove  | Drafted box        | Z    | 110,150,300                | 4mm wall offset from exterior          |
| 3  | Bottom rim groove              | Mates with tub tongue              | Add+Cut | Two legs + gap     | Z    | Perimeter at Z=196.8-200   | 1.7W x 3.2D, full perimeter           |
| 4  | Reveal step                    | Shadow line at seam                | Built-in| N/A                | -    | -                          | 0.8mm inset per side at Z=200          |
| 5  | Snap-fit ledges (8x)          | Permanent catch engagement         | Add     | Rectangular shelf  | var  | See spec per wall          | 15x2x2mm, Z_bottom=205                |
| 6  | Air switch aperture            | Front face through-hole            | Remove  | Cylinder           | Y    | 50,wall,225                | dia 33 ext, dia 39 pocket              |
| 7  | RP2040 aperture                | Front face through-hole            | Remove  | Cylinder           | Y    | 110,wall,245               | dia 26 ext, dia 34 pocket              |
| 8  | S3 display aperture            | Front face through-hole            | Remove  | Cylinder           | Y    | 170,wall,245               | dia 43 ext, dia 46 pocket              |
| 9  | Funnel opening                 | Pour access on top face            | Remove  | Rounded rectangle  | Z    | 99.5,55,398                | 79x70mm, R5 corners                   |
| 10 | Funnel drip lip                | Contains drips                     | Add     | Rectangular ring   | Z    | 99.5,55,401                | 3mm wide, 2mm tall above Z=400        |
| 11 | Electronics shelf              | Holds PCBs at rear-top             | Add     | Flat plate+ribs    | Z    | 109.5,256,378.5            | 203x72x3mm                            |
| 12 | Shelf support ribs (3x)       | Supports shelf                     | Add     | Vertical plates    | Y    | X=50,110,170               | 3x72x20mm each                        |
| 13 | Wire channel (shelf front)     | Routes wiring harness              | Remove  | Rectangular channel| X    | shelf front edge           | 10W x 8D along shelf front             |
| 14 | Bag outlet tube pass-throughs  | Tube exits at bottom rim           | Remove  | Cylinder           | Z    | X=70,150; Y=280; Z=200     | dia 8mm each                          |
| 15 | Wire pass-throughs (2x)       | Wire exits at bottom rim           | Remove  | Rectangular slot   | Z    | X=40,180; Y=290; Z=200     | 12x6mm each                           |
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

import cadquery as cq
from step_validate import Validator

# ===================================================================
# Constants
# ===================================================================

W_BOT = 220.0
D_BOT = 300.0
H_CAP = 200.0
Z_SEAM = 200.0
Z_TOP = 400.0

DRAFT_DEG = 3.0
DRAFT_RAD = math.radians(DRAFT_DEG)
DRAFT_OFFSET = H_CAP * math.tan(DRAFT_RAD)

W_TOP = W_BOT - 2 * DRAFT_OFFSET
D_TOP = D_BOT - 2 * DRAFT_OFFSET

WALL = 4.0
REVEAL = 0.8
R_VERT = 8.0
R_TOP = 5.0

GROOVE_W = 1.7
GROOVE_D = 3.2
Z_GROOVE_BOT = Z_SEAM - GROOVE_D  # 196.8

LEDGE_W = 15.0
LEDGE_D = 2.0
LEDGE_H = 2.0
LEDGE_Z_BOT = 205.0

AIR_X, AIR_Z = 50.0, 225.0
AIR_DIA_EXT = 33.0
AIR_DIA_PKT = 39.0
AIR_PKT_DEPTH = 2.0

RP_X, RP_Z = 110.0, 245.0
RP_DIA_EXT = 26.0
RP_DIA_PKT = 34.0
RP_PKT_DEPTH = 2.5

S3_X, S3_Z = 170.0, 245.0
S3_DIA_EXT = 43.0
S3_DIA_PKT = 46.0
S3_PKT_DEPTH = 3.0

FUNNEL_X0, FUNNEL_X1 = 60.0, 139.0
FUNNEL_Y0, FUNNEL_Y1 = 20.0, 90.0
FUNNEL_W = FUNNEL_X1 - FUNNEL_X0
FUNNEL_D = FUNNEL_Y1 - FUNNEL_Y0
FUNNEL_CX = (FUNNEL_X0 + FUNNEL_X1) / 2.0
FUNNEL_CY = (FUNNEL_Y0 + FUNNEL_Y1) / 2.0
FUNNEL_R = 5.0
LIP_H = 2.0
LIP_W = 3.0

SHELF_Z = 380.0
SHELF_THICK = 3.0
SHELF_X0 = 8.0
SHELF_X1 = 211.0
SHELF_Y0 = 220.0
SHELF_Y1 = 292.0
SHELF_W = SHELF_X1 - SHELF_X0
SHELF_DEPTH = SHELF_Y1 - SHELF_Y0

RIB_THICK = 3.0
RIB_HEIGHT = 20.0
RIB_X_POSITIONS = [50.0, 110.0, 170.0]

WIRE_CH_W = 10.0
WIRE_CH_D = 8.0

TUBE_PT_DIA = 8.0
TUBE_PT_Y = 280.0
TUBE_PT_X = [70.0, 150.0]

WIRE_PT_W = 12.0
WIRE_PT_H = 6.0
WIRE_PT_Y = 290.0
WIRE_PT_X = [40.0, 180.0]


# ===================================================================
# Helpers
# ===================================================================

def outer_rect_at_z(z):
    """Outer wall position at height z, with reveal + draft."""
    dz = z - Z_SEAM
    inset = REVEAL + max(dz, 0) * math.tan(DRAFT_RAD)
    # Below Z_SEAM, no additional draft — straight extrusion for groove legs
    return inset, inset, W_BOT - inset, D_BOT - inset


def inner_rect_at_z(z):
    """Inner wall position at height z."""
    ox0, oy0, ox1, oy1 = outer_rect_at_z(z)
    return ox0 + WALL, oy0 + WALL, ox1 - WALL, oy1 - WALL


def rounded_rect_wire(x0, y0, x1, y1, r, z):
    """Create a rounded rectangle CadQuery Wire at height z."""
    w = x1 - x0
    d = y1 - y0
    r = min(r, w / 2 - 0.01, d / 2 - 0.01)
    if r < 0.1:
        r = 0.1
    wp = (
        cq.Workplane("XY", origin=(0, 0, z))
        .moveTo(x0 + r, y0)
        .lineTo(x1 - r, y0)
        .tangentArcPoint((x1, y0 + r), relative=False)
        .lineTo(x1, y1 - r)
        .tangentArcPoint((x1 - r, y1), relative=False)
        .lineTo(x0 + r, y1)
        .tangentArcPoint((x0, y1 - r), relative=False)
        .lineTo(x0, y0 + r)
        .tangentArcPoint((x0 + r, y0), relative=False)
        .close()
    )
    return wp.val()


def front_wall_outer_y(z):
    """Y of front wall outer surface at height z."""
    return REVEAL + max(z - Z_SEAM, 0) * math.tan(DRAFT_RAD)


def front_wall_inner_y(z):
    return front_wall_outer_y(z) + WALL


def rounded_rect_sketch(x0, y0, x1, y1, r, z):
    """Create a rounded rectangle CadQuery Workplane sketch at height z."""
    w = x1 - x0
    d = y1 - y0
    r = min(r, w / 2 - 0.01, d / 2 - 0.01)
    if r < 0.1:
        r = 0.1
    return (
        cq.Workplane("XY", origin=(0, 0, z))
        .moveTo(x0 + r, y0)
        .lineTo(x1 - r, y0)
        .tangentArcPoint((x1, y0 + r), relative=False)
        .lineTo(x1, y1 - r)
        .tangentArcPoint((x1 - r, y1), relative=False)
        .lineTo(x0 + r, y1)
        .tangentArcPoint((x0, y1 - r), relative=False)
        .lineTo(x0, y0 + r)
        .tangentArcPoint((x0 + r, y0), relative=False)
        .close()
    )


# ===================================================================
# Build
# ===================================================================

print("=" * 60)
print("Enclosure Cap — CadQuery STEP Generation")
print("=" * 60)
print()

# --- 1. Outer shell ---
# Loft from bottom rim (Z=200) to top (Z=400), then add rim legs for groove.
print("Building outer shell...")

bx0, by0, bx1, by1 = outer_rect_at_z(Z_SEAM)  # 0.8, 0.8, 219.2, 299.2
tx0, ty0, tx1, ty1 = outer_rect_at_z(Z_TOP)

bot_wire = rounded_rect_wire(bx0, by0, bx1, by1, R_VERT, Z_SEAM)
top_wire = rounded_rect_wire(tx0, ty0, tx1, ty1, R_VERT, Z_TOP)

outer_solid = (
    cq.Workplane("XY")
    .add(bot_wire).toPending()
    .workplane(offset=H_CAP)
    .add(top_wire).toPending()
    .loft(combine=True)
)

# Try top-face-to-side fillet (R_TOP=5)
try:
    outer_solid = outer_solid.edges(">Z").fillet(R_TOP)
except Exception as e:
    print(f"  Note: Top edge fillet: {e}")

# --- 2. Inner cavity ---
print("Building inner cavity...")
Z_TOP_INNER = Z_TOP - WALL  # 396

ibx0, iby0, ibx1, iby1 = inner_rect_at_z(Z_SEAM)
itx0, ity0, itx1, ity1 = inner_rect_at_z(Z_TOP_INNER)

inner_bot_wire = rounded_rect_wire(ibx0, iby0, ibx1, iby1, max(R_VERT - WALL, 1), Z_SEAM - 0.1)
inner_top_wire = rounded_rect_wire(itx0, ity0, itx1, ity1, max(R_VERT - WALL, 1), Z_TOP_INNER)

inner_cavity = (
    cq.Workplane("XY")
    .add(inner_bot_wire).toPending()
    .workplane(offset=(Z_TOP_INNER - Z_SEAM + 0.1))
    .add(inner_top_wire).toPending()
    .loft(combine=True)
)

cap = outer_solid.cut(inner_cavity)

# --- 3. Bottom rim groove ---
# The groove is formed by adding two "legs" (outer and inner) below Z=200
# and leaving a 1.7mm gap between them.
# Outer leg: from outer wall face inward by (WALL - GROOVE_W)/2 = 1.15 mm
# Inner leg: from inner wall face outward by 1.15 mm
# Both legs extend from Z=200 downward by GROOVE_D = 3.2 mm (to Z=196.8)
print("Adding bottom rim legs (groove)...")

# At Z=200, outer is at inset=0.8, inner is at inset=4.8
# Outer leg: from 0.8 to 0.8+1.15 = 1.95 (inset from encl edge)
# Inner leg: from 4.8-1.15=3.65 to 4.8 (inset from encl edge)
# Gap (groove): from 1.95 to 3.65 (1.7mm wide)

GROOVE_OUTER_EDGE = REVEAL  # 0.8 from enclosure edge
GROOVE_INNER_WALL_POS = REVEAL + (WALL - GROOVE_W) / 2.0  # 0.8 + 1.15 = 1.95
GROOVE_OUTER_WALL_POS = REVEAL + (WALL + GROOVE_W) / 2.0  # 0.8 + 2.85 = 3.65
GROOVE_INNER_EDGE = REVEAL + WALL  # 4.8 from enclosure edge

# Outer leg: rounded rect from GROOVE_OUTER_EDGE to GROOVE_INNER_WALL_POS
outer_leg_outer = rounded_rect_sketch(
    GROOVE_OUTER_EDGE, GROOVE_OUTER_EDGE,
    W_BOT - GROOVE_OUTER_EDGE, D_BOT - GROOVE_OUTER_EDGE,
    R_VERT, Z_GROOVE_BOT
).extrude(GROOVE_D)

outer_leg_inner = rounded_rect_sketch(
    GROOVE_INNER_WALL_POS, GROOVE_INNER_WALL_POS,
    W_BOT - GROOVE_INNER_WALL_POS, D_BOT - GROOVE_INNER_WALL_POS,
    max(R_VERT - (GROOVE_INNER_WALL_POS - GROOVE_OUTER_EDGE), 1), Z_GROOVE_BOT
).extrude(GROOVE_D)

outer_leg = outer_leg_outer.cut(outer_leg_inner)
cap = cap.union(outer_leg)

# Inner leg: rounded rect from GROOVE_OUTER_WALL_POS to GROOVE_INNER_EDGE
inner_leg_outer = rounded_rect_sketch(
    GROOVE_OUTER_WALL_POS, GROOVE_OUTER_WALL_POS,
    W_BOT - GROOVE_OUTER_WALL_POS, D_BOT - GROOVE_OUTER_WALL_POS,
    max(R_VERT - (GROOVE_OUTER_WALL_POS - GROOVE_OUTER_EDGE), 1), Z_GROOVE_BOT
).extrude(GROOVE_D)

inner_leg_inner = rounded_rect_sketch(
    GROOVE_INNER_EDGE, GROOVE_INNER_EDGE,
    W_BOT - GROOVE_INNER_EDGE, D_BOT - GROOVE_INNER_EDGE,
    max(R_VERT - WALL, 1), Z_GROOVE_BOT
).extrude(GROOVE_D)

inner_leg = inner_leg_outer.cut(inner_leg_inner)
cap = cap.union(inner_leg)

# --- 5. Snap-fit ledges ---
print("Adding snap-fit ledges...")

ix0_l, iy0_l, ix1_l, iy1_l = inner_rect_at_z(LEDGE_Z_BOT)

ledge_positions = [
    (60.0, iy0_l, "front"), (160.0, iy0_l, "front"),
    (60.0, iy1_l, "back"), (160.0, iy1_l, "back"),
    (ix0_l, 100.0, "left"), (ix0_l, 200.0, "left"),
    (ix1_l, 100.0, "right"), (ix1_l, 200.0, "right"),
]

for cx, cy, wall in ledge_positions:
    if wall == "front":
        ledge = cq.Workplane("XY", origin=(cx - LEDGE_W/2, cy, LEDGE_Z_BOT)).box(LEDGE_W, LEDGE_D, LEDGE_H, centered=False)
    elif wall == "back":
        ledge = cq.Workplane("XY", origin=(cx - LEDGE_W/2, cy - LEDGE_D, LEDGE_Z_BOT)).box(LEDGE_W, LEDGE_D, LEDGE_H, centered=False)
    elif wall == "left":
        ledge = cq.Workplane("XY", origin=(cx, cy - LEDGE_W/2, LEDGE_Z_BOT)).box(LEDGE_D, LEDGE_W, LEDGE_H, centered=False)
    elif wall == "right":
        ledge = cq.Workplane("XY", origin=(cx - LEDGE_D, cy - LEDGE_W/2, LEDGE_Z_BOT)).box(LEDGE_D, LEDGE_W, LEDGE_H, centered=False)
    cap = cap.union(ledge)

# --- 6, 7, 8. Front face apertures ---
print("Cutting front face apertures...")

def cut_front_aperture(body, cx, cz, dia_ext, dia_pkt, pkt_depth):
    """Cut a stepped circular aperture through the front wall."""
    y_outer = front_wall_outer_y(cz)
    y_inner = front_wall_inner_y(cz)

    # Through-hole at exterior diameter: cylinder along Y through entire wall
    # Place cylinder at (cx, y_outer-1, cz), extend in Y to y_inner+1
    hole_len = (y_inner - y_outer) + 2  # wall thickness + margin
    through = (
        cq.Workplane("XZ", origin=(0, y_outer - 0.5, 0))
        .center(cx, cz)
        .circle(dia_ext / 2)
        .extrude(-(hole_len))  # XZ normal is -Y, negative extrude = +Y
    )
    body = body.cut(through)

    # Stepped pocket from interior side (larger diameter, partial depth)
    if pkt_depth > 0 and dia_pkt > dia_ext:
        pocket = (
            cq.Workplane("XZ", origin=(0, y_inner + 0.5, 0))
            .center(cx, cz)
            .circle(dia_pkt / 2)
            .extrude(pkt_depth + 0.5)  # XZ normal is -Y, positive extrude = -Y (toward exterior)
        )
        body = body.cut(pocket)

    return body

cap = cut_front_aperture(cap, AIR_X, AIR_Z, AIR_DIA_EXT, AIR_DIA_PKT, AIR_PKT_DEPTH)
cap = cut_front_aperture(cap, RP_X, RP_Z, RP_DIA_EXT, RP_DIA_PKT, RP_PKT_DEPTH)
cap = cut_front_aperture(cap, S3_X, S3_Z, S3_DIA_EXT, S3_DIA_PKT, S3_PKT_DEPTH)

# --- 9. Funnel opening ---
print("Cutting funnel opening...")

funnel_cut = rounded_rect_sketch(
    FUNNEL_X0, FUNNEL_Y0, FUNNEL_X1, FUNNEL_Y1, FUNNEL_R, Z_TOP - WALL - 0.5
).extrude(WALL + 1.0)
cap = cap.cut(funnel_cut)

# --- 10. Funnel drip lip ---
print("Adding funnel drip lip...")

# Extend lip slightly into the top face (Z=399.5) to ensure Boolean union merges properly
LIP_START_Z = Z_TOP - 0.5

lip_outer = rounded_rect_sketch(
    FUNNEL_X0, FUNNEL_Y0, FUNNEL_X1, FUNNEL_Y1, FUNNEL_R, LIP_START_Z
).extrude(LIP_H + 0.5)

lip_ix0 = FUNNEL_X0 + LIP_W
lip_ix1 = FUNNEL_X1 - LIP_W
lip_iy0 = FUNNEL_Y0 + LIP_W
lip_iy1 = FUNNEL_Y1 - LIP_W
lip_ir = max(FUNNEL_R - LIP_W, 0.5)

lip_inner = rounded_rect_sketch(
    lip_ix0, lip_iy0, lip_ix1, lip_iy1, lip_ir, LIP_START_Z
).extrude(LIP_H + 0.5)

lip_ring = lip_outer.cut(lip_inner)
cap = cap.union(lip_ring)

# --- 11. Electronics shelf ---
print("Adding electronics shelf...")

shelf = cq.Workplane("XY", origin=(SHELF_X0, SHELF_Y0, SHELF_Z - SHELF_THICK)).box(
    SHELF_W, SHELF_DEPTH, SHELF_THICK, centered=False
)
cap = cap.union(shelf)

# --- 12. Shelf support ribs ---
print("Adding shelf support ribs...")

for rx in RIB_X_POSITIONS:
    rib = cq.Workplane("XY", origin=(rx - RIB_THICK/2, SHELF_Y0, SHELF_Z - SHELF_THICK - RIB_HEIGHT)).box(
        RIB_THICK, SHELF_DEPTH, RIB_HEIGHT, centered=False
    )
    cap = cap.union(rib)

# --- 13. Wire channel ---
print("Cutting wire channel...")

wire_ch = cq.Workplane("XY", origin=(SHELF_X0, SHELF_Y0, SHELF_Z - WIRE_CH_D)).box(
    SHELF_W, WIRE_CH_W, WIRE_CH_D, centered=False
)
cap = cap.cut(wire_ch)

# --- 14. Tube pass-throughs ---
print("Cutting tube pass-throughs...")

for tx in TUBE_PT_X:
    tube_hole = cq.Workplane("XY", origin=(tx, TUBE_PT_Y, Z_GROOVE_BOT - 1)).circle(TUBE_PT_DIA / 2).extrude(GROOVE_D + 10)
    cap = cap.cut(tube_hole)

# --- 15. Wire pass-throughs ---
print("Cutting wire pass-throughs...")

for wx in WIRE_PT_X:
    wire_slot = cq.Workplane("XY", origin=(wx - WIRE_PT_W/2, WIRE_PT_Y - WIRE_PT_H/2, Z_GROOVE_BOT - 1)).box(
        WIRE_PT_W, WIRE_PT_H, GROOVE_D + 10, centered=False
    )
    cap = cap.cut(wire_slot)

# ===================================================================
# Export STEP
# ===================================================================

output_path = Path(__file__).parent / "cap.step"
cq.exporters.export(cap, str(output_path))
print(f"\nSTEP exported to: {output_path}")

# ===================================================================
# Validation
# ===================================================================

print("\n" + "=" * 60)
print("VALIDATION")
print("=" * 60 + "\n")

v = Validator(cap)

# --- Feature 1: Outer shell ---
z_mid = 300.0
y_fw_outer = front_wall_outer_y(z_mid)
y_fw_inner = front_wall_inner_y(z_mid)
v.check_solid("Outer shell - front wall mid", 110, (y_fw_outer + y_fw_inner) / 2, z_mid,
              "solid in front wall at mid-height")
v.check_solid("Outer shell - top face", 110, 150, Z_TOP - WALL / 2,
              "solid in top face center")
# At Z=300, outer wall X = 0.8 + (300-200)*tan(3deg) = ~6.04
# Wall extends from ~6.04 to ~10.04. Probe at ~8.0 (mid-wall).
ox0_300, _, _, _ = outer_rect_at_z(z_mid)
v.check_solid("Outer shell - side wall mid", ox0_300 + WALL / 2, 150, z_mid,
              "solid in left side wall at Z=300")

# --- Feature 2: Inner cavity ---
v.check_void("Inner cavity center", 110, 150, 300, "void at center of interior")
v.check_void("Inner cavity near top", 110, 150, Z_TOP_INNER - 2, "void just below interior top")

# --- Feature 3: Bottom rim groove ---
# The groove is the gap between outer and inner legs, at Z=198 (mid-groove)
# Groove center inset: (0.8 + 1.15 + 0.85) = 2.8 from enclosure edge => Y=2.8 on front wall
groove_y_center = REVEAL + WALL / 2  # 2.8
z_groove_mid = Z_SEAM - GROOVE_D / 2  # 198.4
v.check_void("Groove - front wall center", 110, groove_y_center, z_groove_mid,
             "void in groove gap at front wall")
# Outer leg solid (between outer face and groove)
v.check_solid("Groove - outer leg front", 110, REVEAL + (GROOVE_INNER_WALL_POS - REVEAL) / 2, z_groove_mid,
              "solid in outer leg of groove")
# Inner leg solid (between groove and inner face)
v.check_solid("Groove - inner leg front", 110, (GROOVE_OUTER_WALL_POS + GROOVE_INNER_EDGE) / 2, z_groove_mid,
              "solid in inner leg of groove")

# --- Feature 4: Reveal ---
v.check_void("Reveal - void outside cap", 0.3, 150, Z_SEAM + 1, "void outside cap at X=0.3")
v.check_solid("Reveal - solid inside cap wall", 2.5, 150, Z_SEAM + 1, "solid in wall at X=2.5")

# --- Feature 5: Snap-fit ledges ---
ix0_205, iy0_205, ix1_205, iy1_205 = inner_rect_at_z(LEDGE_Z_BOT)
v.check_solid("Snap ledge - front left", 60, iy0_205 + LEDGE_D / 2, LEDGE_Z_BOT + LEDGE_H / 2)
v.check_solid("Snap ledge - back right", 160, iy1_205 - LEDGE_D / 2, LEDGE_Z_BOT + LEDGE_H / 2)
v.check_solid("Snap ledge - left wall", ix0_205 + LEDGE_D / 2, 100, LEDGE_Z_BOT + LEDGE_H / 2)
v.check_solid("Snap ledge - right wall", ix1_205 - LEDGE_D / 2, 200, LEDGE_Z_BOT + LEDGE_H / 2)

# --- Feature 6: Air switch aperture ---
y_air_mid = front_wall_outer_y(AIR_Z) + WALL / 2
v.check_void("Air switch - center", AIR_X, y_air_mid, AIR_Z, "void at air switch center")
# Pocket dia is 39mm (r=19.5), so top of pocket = 225+19.5=244.5. Probe above that.
v.check_solid("Air switch - wall above", AIR_X, y_air_mid, AIR_Z + AIR_DIA_PKT / 2 + 2, "solid above air switch")

# --- Feature 7: RP2040 aperture ---
y_rp_mid = front_wall_outer_y(RP_Z) + WALL / 2
v.check_void("RP2040 - center", RP_X, y_rp_mid, RP_Z, "void at RP2040 center")
# Pocket dia is 34mm (r=17), so top of pocket = 245+17=262. Probe above that.
v.check_solid("RP2040 - wall above", RP_X, y_rp_mid, RP_Z + RP_DIA_PKT / 2 + 2, "solid above RP2040")

# --- Feature 8: S3 display aperture ---
y_s3_mid = front_wall_outer_y(S3_Z) + WALL / 2
v.check_void("S3 display - center", S3_X, y_s3_mid, S3_Z, "void at S3 center")
v.check_solid("S3 display - wall below", S3_X, y_s3_mid, S3_Z - S3_DIA_EXT / 2 - 3, "solid below S3")

# --- Feature 9: Funnel opening ---
v.check_void("Funnel opening - center", FUNNEL_CX, FUNNEL_CY, Z_TOP - WALL / 2, "void at funnel center")
v.check_solid("Funnel opening - outside", FUNNEL_X1 + 5, FUNNEL_CY, Z_TOP - WALL / 2, "solid outside funnel")

# --- Feature 10: Funnel drip lip ---
v.check_solid("Drip lip - ring", FUNNEL_X0 + LIP_W / 2, FUNNEL_CY, Z_TOP + LIP_H / 2,
              "solid in drip lip")
v.check_void("Drip lip - interior", FUNNEL_CX, FUNNEL_CY, Z_TOP + LIP_H / 2,
             "void inside lip ring")

# --- Feature 11: Electronics shelf ---
v.check_solid("Shelf center", 110, 256, SHELF_Z - SHELF_THICK / 2)

# --- Feature 12: Shelf ribs ---
v.check_solid("Shelf rib X=110", 110, 256, SHELF_Z - SHELF_THICK - RIB_HEIGHT / 2)

# --- Feature 13: Wire channel ---
v.check_void("Wire channel", 110, SHELF_Y0 + WIRE_CH_W / 2, SHELF_Z - WIRE_CH_D / 2)

# --- Feature 14: Tube pass-throughs ---
v.check_void("Tube pass-through X=70", 70, TUBE_PT_Y, Z_SEAM + 1)
v.check_void("Tube pass-through X=150", 150, TUBE_PT_Y, Z_SEAM + 1)

# --- Feature 15: Wire pass-throughs ---
v.check_void("Wire pass-through X=40", 40, WIRE_PT_Y, Z_SEAM + 1)
v.check_void("Wire pass-through X=180", 180, WIRE_PT_Y, Z_SEAM + 1)

# --- Rubric 4: Solid validity ---
v.check_valid()
v.check_single_body()
v.check_volume(expected_envelope=W_BOT * D_BOT * H_CAP, fill_range=(0.02, 0.25))

# --- Rubric 5: Bounding box ---
bb = cap.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, bx0, bx1)
v.check_bbox("Y", bb.ymin, bb.ymax, by0, by1)
v.check_bbox("Z", bb.zmin, bb.zmax, Z_GROOVE_BOT, Z_TOP + LIP_H)

# --- Summary ---
if not v.summary():
    sys.exit(1)
