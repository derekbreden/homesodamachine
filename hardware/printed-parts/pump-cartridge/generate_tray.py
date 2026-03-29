#!/usr/bin/env python3
"""
Cartridge Tray -- CadQuery STEP Generation Script

Coordinate system:
  Origin: front-left-bottom corner of tray outer envelope
  X: width, left to right (0..160, rails extend to -7 and 167)
  Y: depth, front to dock (0=front/user, 155=rear/dock)
  Z: height, bottom to top (0..72)
  Envelope: 174x155x72 mm (with T-rails)

Build order: Sub-A, B, C, E, H, F (unions), then D, G, I, J (cuts)
"""

import sys, math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
import cadquery as cq
from step_validate import Validator

STEP_PATH = str(Path(__file__).parent / "cartridge-tray.step")

OLAP = 0.5  # overlap for boolean reliability

# === DIMENSIONS ===
TRAY_W, TRAY_D, TRAY_H = 160.0, 155.0, 72.0
WALL = 5.0; FLOOR_T = 3.0
BP_Y0, BP_Y1 = 120.0, 128.5
RS_Y0, RS_Y1 = 153.0, 155.0

TNG_X, TNG_Z, CAP_X, CAP_Z = 4.0, 3.0, 3.0, 6.0
L_RAIL_Z, R_RAIL_Z = 54.0, 18.0

P1X, P2X, PCZ, BRKT_Y = 42.0, 118.0, 37.0, 82.0
BOSS_R, BOSS_TOP = 5.0, 37.0
PILOT_R, PILOT_DEPTH = 2.0, 5.7
BOSS_XS = [17.3, 66.7, 93.3, 142.7]

CR_IR, CR_OR = 18.0, 21.0
CR_Y0, CR_Y1 = 45.0, 55.0

GP_R, GP_LEN = 1.75, 18.0
GP_ROOT = BP_Y1
GP_POS = [(58.0,17.0),(102.0,17.0),(58.0,57.0),(102.0,57.0)]
SB_R, SB_LEN = 2.5, 10.8
SB_POS = [(80.0,20.0),(80.0,54.0),(65.0,37.0),(95.0,37.0)]

RDG_H, RDG_WZ, RDG_LY = 1.0, 2.0, 10.0
RDG_Z = 70.0
RDG_YS = [20.0, 50.0, 80.0, 110.0]

CH_W, CH_WALL, CH_WH = 10.0, 2.0, 5.0
CH_Y0, CH_Y1 = 82.0, 110.0
CH_XS = [70.0, 70.0, 90.0, 90.0]
CLIP_T, CLIP_O, CLIP_L = 1.0, 3.0, 3.0
CLIP_YS = [87.0, 97.0, 107.0]

FB_R = 4.75
FG = [(70.0,27.0),(90.0,27.0),(70.0,47.0),(90.0,47.0)]
CB_R, CB_DEPTH = 7.75, 2.0
RC_R = 8.0
FN_R, FN_DEPTH = 10.0, 1.0

SL_L, SL_W = 12.0, 5.0
SL_CY, SL_CZ = 114.0, 37.0

SLP = 1.5

TERMS = [(30.0,25.0,35.0,8.0,8.0),(130.0,30.0,42.0,8.0,8.0),(80.0,60.0,64.0,6.0,6.0)]


def cyl_y(cx, cy_start, cy_end, cz, radius):
    """Create cylinder along Y axis from cy_start to cy_end at (cx, cz)."""
    length = abs(cy_end - cy_start)
    y_min = min(cy_start, cy_end)
    # Build on XZ plane (normal = -Y), extrude in -Y = length
    c = cq.Workplane("XZ").circle(radius).extrude(length)
    # This goes from Y=0 to Y=-length. Translate so Y_min maps correctly.
    return c.translate((cx, y_min + length, cz))


def slot_y(cx, cy, cz, slot_len, slot_wid, x_depth, x_start):
    """Stadium slot along Y through wall in X direction."""
    # Build on YZ plane at origin, extrude in +X
    s = cq.Workplane("YZ").slot2D(slot_len, slot_wid, angle=0).extrude(x_depth)
    # slot2D on YZ: sketch X=Y, sketch Y=Z. Centered at origin.
    # Extrude goes +X from X=0 to X=x_depth
    return s.translate((x_start, cy, cz))


print("="*60)
print("Cartridge Tray -- STEP Generation")
print("="*60)

# ===== SUB-A: BOX SHELL =====
print("\nSub-A: Box Shell...")
tray = cq.Workplane("XY").box(TRAY_W, TRAY_D, TRAY_H, centered=False)

# Main cavity
tray = tray.cut(cq.Workplane("XY").transformed(offset=(WALL, 0, FLOOR_T))
    .box(TRAY_W-2*WALL, BP_Y0, TRAY_H-FLOOR_T, centered=False))

# Release plate pocket
tray = tray.cut(cq.Workplane("XY").transformed(offset=(WALL, BP_Y1, FLOOR_T))
    .box(TRAY_W-2*WALL, RS_Y0-BP_Y1, TRAY_H-FLOOR_T, centered=False))

# Cross-ribs (overlap into bore plate and rear skin)
for rx, rw, rz0, rzh in [(28.0,2.0,FLOOR_T,TRAY_H-FLOOR_T),
                           (130.0,2.0,FLOOR_T,TRAY_H-FLOOR_T),
                           (78.0,4.0,FLOOR_T,12.0)]:
    tray = tray.union(cq.Workplane("XY").transformed(offset=(rx,BP_Y1-OLAP,rz0))
        .box(rw, RS_Y0-BP_Y1+2*OLAP, rzh, centered=False))
print("  done.")

# ===== SUB-B: T-RAIL TONGUES =====
print("Sub-B: T-Rails...")
# Left tongue & cap (overlap into wall)
tray = tray.union(cq.Workplane("XY").transformed(offset=(-TNG_X, 0, L_RAIL_Z-TNG_Z/2))
    .box(TNG_X+OLAP, TRAY_D, TNG_Z, centered=False))
tray = tray.union(cq.Workplane("XY").transformed(offset=(-(TNG_X+CAP_X), 0, L_RAIL_Z-CAP_Z/2))
    .box(CAP_X+OLAP, TRAY_D, CAP_Z, centered=False))
# Right tongue & cap
tray = tray.union(cq.Workplane("XY").transformed(offset=(TRAY_W-OLAP, 0, R_RAIL_Z-TNG_Z/2))
    .box(TNG_X+OLAP, TRAY_D, TNG_Z, centered=False))
tray = tray.union(cq.Workplane("XY").transformed(offset=(TRAY_W+TNG_X-OLAP, 0, R_RAIL_Z-CAP_Z/2))
    .box(CAP_X+OLAP, TRAY_D, CAP_Z, centered=False))
print("  done.")

# ===== SUB-C: PUMP MOUNTING BOSSES =====
print("Sub-C: Pump Bosses & Cradles...")
for bx in BOSS_XS:
    # Cylinder from Z=0 to BOSS_TOP at (bx, BRKT_Y)
    tray = tray.union(cq.Workplane("XY").transformed(offset=(bx, BRKT_Y, 0))
        .circle(BOSS_R).extrude(BOSS_TOP))
    # Buttress ribs (overlap into boss and floor)
    for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
        rx0 = bx + (BOSS_R-OLAP if dx>0 else (-BOSS_R-5.0+OLAP if dx<0 else -1.0))
        ry0 = BRKT_Y + (BOSS_R-OLAP if dy>0 else (-BOSS_R-5.0+OLAP if dy<0 else -1.0))
        rw = 5.0+OLAP if dx!=0 else 2.0
        rd = 2.0 if dy==0 else 5.0+OLAP
        tray = tray.union(cq.Workplane("XY").transformed(offset=(rx0,ry0,0))
            .box(rw, rd, 20.0, centered=False))

# Motor cradles
for pcx in [P1X, P2X]:
    # Pedestal box
    tray = tray.union(cq.Workplane("XY").transformed(offset=(pcx-CR_OR, CR_Y0, 0))
        .box(CR_OR*2, CR_Y1-CR_Y0, PCZ, centered=False))
    # Cut inner bore: cylinder along Y
    tray = tray.cut(cyl_y(pcx, CR_Y0-0.5, CR_Y1+0.5, PCZ, CR_IR))
    # Cut top half
    tray = tray.cut(cq.Workplane("XY").transformed(offset=(pcx-CR_OR-1, CR_Y0-0.5, PCZ))
        .box(CR_OR*2+2, CR_Y1-CR_Y0+1, TRAY_H-PCZ+1, centered=False))
print("  done.")

# ===== SUB-E: GUIDE POSTS & STOP BOSSES =====
print("Sub-E: Guide Posts...")
# Posts from bore plate dock face (Y=128.5) to Y=146.5, with OLAP into bore plate
for gpx, gpz in GP_POS:
    tray = tray.union(cyl_y(gpx, GP_ROOT-OLAP, GP_ROOT+GP_LEN, gpz, GP_R))
for sbx, sbz in SB_POS:
    tray = tray.union(cyl_y(sbx, GP_ROOT-OLAP, GP_ROOT+SB_LEN, sbz, SB_R))
print("  done.")

# ===== SUB-H: LID SNAP DETENT RIDGES =====
print("Sub-H: Lid Detent Ridges...")
# Triangle cross-section in XZ, extruded along Y
# Build at origin in XZ, extrude length in -Y (which we handle by building on XY and translating)
for ry in RDG_YS:
    # Left wall: peak at X = WALL+RDG_H = 6, base from Z=69 to Z=71 at X=WALL-OLAP=4.5
    # Build 2D profile in XZ at origin, extrude along Y
    lr = (cq.Workplane("XY")
        .transformed(offset=(WALL-OLAP, ry-RDG_LY/2, RDG_Z-RDG_WZ/2))
        .box(RDG_H+OLAP, RDG_LY, RDG_WZ, centered=False))
    tray = tray.union(lr)
    # Right wall
    rr = (cq.Workplane("XY")
        .transformed(offset=(TRAY_W-WALL-RDG_H, ry-RDG_LY/2, RDG_Z-RDG_WZ/2))
        .box(RDG_H+OLAP, RDG_LY, RDG_WZ, centered=False))
    tray = tray.union(rr)
print("  done.")

# ===== SUB-F: TUBE ROUTING CHANNELS =====
print("Sub-F: Tube Channels...")
for fx in CH_XS:
    lx = fx - CH_W/2 - CH_WALL
    tray = tray.union(cq.Workplane("XY").transformed(offset=(lx, CH_Y0, FLOOR_T-OLAP))
        .box(CH_WALL, CH_Y1-CH_Y0, CH_WH+OLAP, centered=False))
    rx = fx + CH_W/2
    tray = tray.union(cq.Workplane("XY").transformed(offset=(rx, CH_Y0, FLOOR_T-OLAP))
        .box(CH_WALL, CH_Y1-CH_Y0, CH_WH+OLAP, centered=False))
    for cy in CLIP_YS:
        tray = tray.union(cq.Workplane("XY").transformed(offset=(fx-CH_W/2, cy-CLIP_L/2, FLOOR_T+CH_WH-OLAP))
            .box(CLIP_O, CLIP_L, CLIP_T+OLAP, centered=False))
        tray = tray.union(cq.Workplane("XY").transformed(offset=(fx+CH_W/2-CLIP_O, cy-CLIP_L/2, FLOOR_T+CH_WH-OLAP))
            .box(CLIP_O, CLIP_L, CLIP_T+OLAP, centered=False))
print("  done.")

# ===== CUTS BEGIN =====
print("\n--- All unions done. Starting cuts. ---\n")

# ===== SUB-D: FITTING BORES =====
print("Sub-D: Fitting Bores...")
for fx, fz in FG:
    # Main bore through bore plate (Y=119.9..128.6)
    tray = tray.cut(cyl_y(fx, BP_Y0-0.1, BP_Y1+0.1, fz, FB_R))
    # User counterbore: 2mm from Y=120 into bore plate
    tray = tray.cut(cyl_y(fx, BP_Y0-0.1, BP_Y0+CB_DEPTH, fz, CB_R))
    # Dock counterbore: 2mm from Y=128.5 into bore plate
    tray = tray.cut(cyl_y(fx, BP_Y1-CB_DEPTH, BP_Y1+0.1, fz, CB_R))
    # Rear skin clearance
    tray = tray.cut(cyl_y(fx, RS_Y0-0.1, RS_Y1+0.1, fz, RC_R))
    # Entry funnel (simplified as cylindrical cut 1mm into rear skin)
    tray = tray.cut(cyl_y(fx, RS_Y1-FN_DEPTH, RS_Y1+0.1, fz, FN_R))
print("  done.")

# ===== SUB-G: LINKAGE SLOTS =====
print("Sub-G: Linkage Slots...")
# Left wall slot: X=0..5, center Y=114, Z=37
tray = tray.cut(slot_y(0, SL_CY, SL_CZ, SL_L, SL_W, WALL+0.2, -0.1))
# Right wall slot: X=155..160
tray = tray.cut(slot_y(0, SL_CY, SL_CZ, SL_L, SL_W, WALL+0.2, TRAY_W-WALL-0.1))
print("  done.")

# ===== SUB-I: BEZEL FEATURES =====
print("Sub-I: Bezel Features...")
for x,y,z,w,d,h in [(0,0,0,SLP,SLP,TRAY_H),
                      (TRAY_W-SLP,0,0,SLP,SLP,TRAY_H),
                      (0,0,0,TRAY_W,SLP,SLP),
                      (0,0,TRAY_H-SLP,WALL,SLP,SLP),
                      (TRAY_W-WALL,0,TRAY_H-SLP,WALL,SLP,SLP)]:
    tray = tray.cut(cq.Workplane("XY").transformed(offset=(x,y,z)).box(w,d,h,centered=False))
for x,y,z,w,d,h in [(0,0,15,SLP,3,5),(0,0,52,SLP,3,5),
                      (TRAY_W-SLP,0,15,SLP,3,5),(TRAY_W-SLP,0,52,SLP,3,5),
                      (75,0,0,10,3,SLP)]:
    tray = tray.cut(cq.Workplane("XY").transformed(offset=(x,y,z)).box(w,d,h,centered=False))
print("  done.")

# ===== SUB-J: ELECTRICAL CONTACTS =====
print("Sub-J: Electrical Contacts...")
for cx, z1, z2, sw, sh in TERMS:
    for tz in [z1, z2]:
        tray = tray.cut(cq.Workplane("XY").transformed(offset=(cx-sw/2,RS_Y1-2,tz-sh/2))
            .box(sw,2,sh,centered=False))
        tray = tray.cut(cq.Workplane("XY").transformed(offset=(cx-2,RS_Y1-2,tz-2))
            .box(4,2,4,centered=False))
        tray = tray.cut(cyl_y(cx, RS_Y0-0.1, RS_Y1+0.1, tz, 1.5))
print("  done.")

# ===== PILOT HOLES =====
print("Cutting pilot holes...")
for bx in BOSS_XS:
    tray = tray.cut(cq.Workplane("XY").transformed(offset=(bx,BRKT_Y,BOSS_TOP-PILOT_DEPTH))
        .circle(PILOT_R).extrude(PILOT_DEPTH+0.1))
print("  done.")

# ===== EXPORT =====
print("\nExporting STEP...")
cq.exporters.export(tray, STEP_PATH)
print(f"  -> {STEP_PATH}")

# ===== VALIDATION =====
print("\n" + "="*60)
print("VALIDATION")
print("="*60 + "\n")

v = Validator(tray)
bb = tray.val().BoundingBox()
print(f"BB: X=[{bb.xmin:.2f},{bb.xmax:.2f}] Y=[{bb.ymin:.2f},{bb.ymax:.2f}] Z=[{bb.zmin:.2f},{bb.zmax:.2f}]")

v.check_bbox("X", bb.xmin, bb.xmax, -7.0, 167.0)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, 155.0)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, 72.0)
v.check_valid()
v.check_single_body()
v.check_volume(expected_envelope=174*155*72, fill_range=(0.05, 0.30))

# Sub-A
print("\n--- Sub-A ---")
v.check_solid("Left wall", 2.5, 77.5, 36.0)
v.check_solid("Right wall", 157.5, 77.5, 36.0)
v.check_solid("Floor", 80.0, 60.0, 1.5)
v.check_solid("Bore plate", 80.0, 124.0, 36.0)
v.check_solid("Rear skin", 40.0, 154.0, 36.0)
v.check_void("Main cavity", 80.0, 60.0, 36.0)
v.check_void("RP pocket", 50.0, 140.0, 36.0)
v.check_solid("Rib 1", 29.0, 140.0, 36.0)
v.check_solid("Rib 2", 131.0, 140.0, 36.0)
v.check_solid("Rib 3", 80.0, 140.0, 9.0)

# Sub-B
print("\n--- Sub-B ---")
v.check_solid("L tongue", -2.0, 77.5, 54.0)
v.check_solid("L cap", -5.5, 77.5, 54.0)
v.check_solid("R tongue", 162.0, 77.5, 18.0)
v.check_solid("R cap", 165.5, 77.5, 18.0)
v.check_void("L@Z=18", -5.5, 77.5, 18.0)
v.check_void("R@Z=54", 165.5, 77.5, 54.0)

# Sub-C
print("\n--- Sub-C ---")
for i, bx in enumerate(BOSS_XS):
    v.check_solid(f"B{i+1} body", bx, BRKT_Y, 20.0)
    v.check_void(f"B{i+1} pilot", bx, BRKT_Y, 35.0)
v.check_solid("Cradle P1 ped", P1X, 50.0, 10.0)
v.check_void("Cradle P1 bore", P1X, 50.0, 30.0)
v.check_solid("Cradle P2 ped", P2X, 50.0, 10.0)

# Sub-E
print("\n--- Sub-E ---")
for i, (gx, gz) in enumerate(GP_POS):
    v.check_solid(f"GP{i+1}", gx, GP_ROOT+GP_LEN/2, gz)
for i, (sx, sz) in enumerate(SB_POS):
    v.check_solid(f"SB{i+1}", sx, GP_ROOT+SB_LEN/2, sz)
v.check_solid("SB1 near tip", 80.0, 139.0, 20.0)
v.check_void("SB1 past tip", 80.0, 140.0, 20.0)

# Sub-H
print("\n--- Sub-H ---")
v.check_solid("L ridge H1", 5.5, 20.0, 70.0)
v.check_solid("R ridge H5", 154.5, 20.0, 70.0)

# Sub-F
print("\n--- Sub-F ---")
v.check_solid("CH1 Lwall", 64.0, 95.0, 5.5)
v.check_solid("CH1 Rwall", 76.0, 95.0, 5.5)
v.check_solid("CH1 clip", 67.0, 87.0, 8.3)

# Sub-D
print("\n--- Sub-D ---")
for fx, fz in FG:
    v.check_void(f"Bore({fx},{fz})", fx, 124.0, fz)
    v.check_solid(f"BoreWall({fx},{fz})", fx+FB_R+1, 124.0, fz)
    v.check_void(f"CBu({fx},{fz})", fx+7.0, 120.5, fz)
    v.check_void(f"CBd({fx},{fz})", fx+7.0, 128.0, fz)
    v.check_void(f"RearClr({fx},{fz})", fx, 154.0, fz)

# Sub-G
print("\n--- Sub-G ---")
v.check_void("L slot ctr", 2.5, 114.0, 37.0)
v.check_void("L slot Y+", 2.5, 119.5, 37.0)
v.check_void("L slot Y-", 2.5, 108.5, 37.0)
v.check_solid("L slot Z+", 2.5, 114.0, 40.0)
v.check_solid("L slot Z-", 2.5, 114.0, 34.0)
v.check_void("R slot ctr", 157.5, 114.0, 37.0)

# Sub-I
print("\n--- Sub-I ---")
v.check_void("L rabbet", 0.5, 0.5, 36.0)
v.check_void("R rabbet", 159.5, 0.5, 36.0)
v.check_void("Floor rabbet", 80.0, 0.5, 0.5)
v.check_solid("L wall past", 2.5, 2.0, 36.0)
v.check_void("IP1", 0.5, 1.5, 17.0)
v.check_void("IP5", 80.0, 1.5, 0.5)

# Sub-J
print("\n--- Sub-J ---")
v.check_void("P1 term", 30.0, 154.5, 25.0)
v.check_void("P1 wire", 30.0, 154.0, 25.0)

if not v.summary():
    sys.exit(1)
print(f"\nSTEP: {STEP_PATH}")
