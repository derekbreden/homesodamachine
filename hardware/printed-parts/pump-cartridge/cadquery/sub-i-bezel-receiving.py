#!/usr/bin/env python3
"""
Sub-I: Front Bezel Receiving Features — CUT TOOL

Generates a single solid representing all material to be removed from
the tray (Sub-A) for the front bezel receiving features. This solid is
intended for subtraction (boolean cut) from the tray body.

Features modeled:
  1. Step-lap rabbet (3 segments: left wall, right wall, floor)
     with fillet relief notches at the two bottom-front corners
  2. Five snap tab pockets: L1, L2, R1, R2, F1
     (T1 skipped — flagged as design gap, no material exists there)

All features are connected via thin bridges (0.01 mm) to ensure a
single solid body for robust boolean operations.

Coordinate system:
  Origin: rear-left-bottom corner of tray (dock side)
  X: width, 0..160 mm (left to right when facing front)
  Y: depth, 0..155 mm (0 = rear/dock, 155 = front/user)
  Z: height, 0..72 mm (0 = floor bottom, 72 = top of side walls)
  Envelope of cut tool: X:[0, 160] Y:[152, 155] Z:[0, 72]
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq
from step_validate import Validator

# ==================================================================
# Feature Planning Table
# ==================================================================
print("""
Feature Planning Table — Sub-I: Front Bezel Receiving Features (CUT TOOL)
=========================================================================
| # | Feature Name          | Function                        | Op     | Shape       | Axis | Cut Volume (X, Y, Z ranges)             | Dims (mm)              |
|---|-----------------------|---------------------------------|--------|-------------|------|-----------------------------------------|------------------------|
| 1 | Left Wall Rabbet      | Bezel seats against X=1.5 ledge | Remove | Box         | Z    | X=0..1.5, Y=153.5..155, Z=0..72        | 1.5 x 1.5 x 72        |
| 2 | Right Wall Rabbet     | Bezel seats against X=158.5     | Remove | Box         | Z    | X=158.5..160, Y=153.5..155, Z=0..72    | 1.5 x 1.5 x 72        |
| 3 | Floor Rabbet          | Bezel seats against Z=1.5       | Remove | Box         | X    | X=0..160, Y=153.5..155, Z=0..1.5       | 160 x 1.5 x 1.5       |
| 4 | Fillet Reliefs (x2)   | Printability/stress relief       | Remove | Notch       | Y    | At X=1.5,Z=1.5 and X=158.5,Z=1.5       | R=1.0, L=1.5 along Y  |
| 5 | Pocket L1             | Snap tab detent (left lower)    | Remove | Box         | X    | X=3.5..5, Y=152..155, Z=19.5..24.5     | 1.5 x 3.0 x 5.0       |
| 6 | Pocket L2             | Snap tab detent (left upper)    | Remove | Box         | X    | X=3.5..5, Y=152..155, Z=47.5..52.5     | 1.5 x 3.0 x 5.0       |
| 7 | Pocket R1             | Snap tab detent (right lower)   | Remove | Box         | X    | X=155..156.5, Y=152..155, Z=19.5..24.5 | 1.5 x 3.0 x 5.0       |
| 8 | Pocket R2             | Snap tab detent (right upper)   | Remove | Box         | X    | X=155..156.5, Y=152..155, Z=47.5..52.5 | 1.5 x 3.0 x 5.0       |
| 9 | Pocket F1             | Snap tab detent (floor center)  | Remove | Box         | Z    | X=77.5..82.5, Y=152..155, Z=1.5..3.0   | 5.0 x 3.0 x 1.5       |
|   | (T1 SKIPPED)          | Design gap — no material exists  | —      | —           | —    | —                                       | —                      |
""")

# ==================================================================
# Parameters
# ==================================================================

# Rabbet dimensions
RABBET_DEPTH = 1.5       # mm, cut depth into wall/floor
RABBET_Y_START = 153.5   # mm
RABBET_Y_END = 155.0     # mm
RABBET_Y_LEN = RABBET_Y_END - RABBET_Y_START  # 1.5 mm

TRAY_WIDTH = 160.0       # mm
TRAY_HEIGHT = 72.0       # mm

# Corner fillet radius
FILLET_R = 1.0           # mm

# Pocket common dimensions
POCKET_WIDTH = 5.0       # mm (along host edge)
POCKET_Y_DEPTH = 3.0     # mm (Y = 152..155)
POCKET_CUT_DEPTH = 1.5   # mm (into wall/floor)
POCKET_Y_START = 152.0
POCKET_Y_END = 155.0

# Bridge thickness for connecting disjoint features into a single body
BRIDGE = 0.01            # mm (negligible for physical part)

# ==================================================================
# Build the cut tool as a single solid
# ==================================================================
# Strategy:
# 1. Build the L-shaped rabbet (union of 3 boxes)
# 2. Subtract fillet relief cylinders at the two bottom-front corners
#    (this removes material from the cut tool at the diagonal, leaving
#    a rounded fillet on the tray after the boolean cut)
# 3. Build pockets and connect them to the rabbet with thin bridges
#    so everything forms a single solid body.

# --- Feature 1: Left Wall Rabbet ---
# X=0..1.5, Y=153.5..155, Z=0..72
left_rabbet = (
    cq.Workplane("XY")
    .transformed(offset=(0, RABBET_Y_START, 0))
    .box(RABBET_DEPTH, RABBET_Y_LEN, TRAY_HEIGHT, centered=False)
)

# --- Feature 2: Right Wall Rabbet ---
# X=158.5..160, Y=153.5..155, Z=0..72
right_rabbet = (
    cq.Workplane("XY")
    .transformed(offset=(TRAY_WIDTH - RABBET_DEPTH, RABBET_Y_START, 0))
    .box(RABBET_DEPTH, RABBET_Y_LEN, TRAY_HEIGHT, centered=False)
)

# --- Feature 3: Floor Rabbet ---
# X=0..160, Y=153.5..155, Z=0..1.5
floor_rabbet = (
    cq.Workplane("XY")
    .transformed(offset=(0, RABBET_Y_START, 0))
    .box(TRAY_WIDTH, RABBET_Y_LEN, RABBET_DEPTH, centered=False)
)

# Union the three rabbet segments
rabbet = left_rabbet.union(right_rabbet).union(floor_rabbet)

# --- Feature 4: Fillet Relief Notches ---
# We need to REMOVE material from the cut tool at the inside corners
# (X=1.5, Z=1.5) and (X=158.5, Z=1.5), running along Y.
# This is done by subtracting a QUARTER-cylinder at each corner.
# Only the quarter facing into the concave region (X>=1.5, Z>=1.5 for
# left; X<=158.5, Z>=1.5 for right) is subtracted.
# When this cut tool (with the notch) is subtracted from the tray,
# the tray retains a rounded fillet at its inside corner.

# Left fillet relief: quarter-cylinder at (X=1.5, Z=1.5) along Y
# The L-shape overlap region is X=0..1.5, Z=0..1.5. The fillet removes
# the material inside the circle R=1 centered at (1.5, 1.5) within
# this overlap quadrant. Clip box: X=0..1.5, Z=0..1.5.
left_fillet_cyl = (
    cq.Workplane("XZ")
    .transformed(offset=(RABBET_DEPTH, RABBET_DEPTH, -(RABBET_Y_START + RABBET_Y_LEN / 2)))
    .cylinder(RABBET_Y_LEN, FILLET_R, centered=True)
)
left_clip = (
    cq.Workplane("XY")
    .transformed(offset=(0, RABBET_Y_START, 0))
    .box(RABBET_DEPTH, RABBET_Y_LEN, RABBET_DEPTH, centered=False)
)
left_quarter = left_fillet_cyl.intersect(left_clip)

# Right fillet relief: quarter-cylinder at (X=158.5, Z=1.5) along Y
# Overlap region is X=158.5..160, Z=0..1.5. Clip box: same region.
right_fillet_cyl = (
    cq.Workplane("XZ")
    .transformed(offset=(TRAY_WIDTH - RABBET_DEPTH, RABBET_DEPTH, -(RABBET_Y_START + RABBET_Y_LEN / 2)))
    .cylinder(RABBET_Y_LEN, FILLET_R, centered=True)
)
right_clip = (
    cq.Workplane("XY")
    .transformed(offset=(TRAY_WIDTH - RABBET_DEPTH, RABBET_Y_START, 0))
    .box(RABBET_DEPTH, RABBET_Y_LEN, RABBET_DEPTH, centered=False)
)
right_quarter = right_fillet_cyl.intersect(right_clip)

# Subtract the quarter-cylinder fillet reliefs from the rabbet
rabbet = rabbet.cut(left_quarter).cut(right_quarter)

# --- Pockets with bridges ---
# Each pocket needs a thin bridge connecting it to the rabbet so
# the final result is a single solid body.

# --- Feature 5: Pocket L1 (Left Wall, Lower) ---
# X=3.5..5.0, Y=152..155, Z=19.5..24.5
pocket_l1 = (
    cq.Workplane("XY")
    .transformed(offset=(3.5, POCKET_Y_START, 19.5))
    .box(POCKET_CUT_DEPTH, POCKET_Y_DEPTH, POCKET_WIDTH, centered=False)
)
# Bridge from left rabbet (X=0..1.5) to pocket (X=3.5..5) in shared Y zone
bridge_l1 = (
    cq.Workplane("XY")
    .transformed(offset=(RABBET_DEPTH, RABBET_Y_START, 19.5))
    .box(3.5 - RABBET_DEPTH, RABBET_Y_LEN, BRIDGE, centered=False)
)

# --- Feature 6: Pocket L2 (Left Wall, Upper) ---
# X=3.5..5.0, Y=152..155, Z=47.5..52.5
pocket_l2 = (
    cq.Workplane("XY")
    .transformed(offset=(3.5, POCKET_Y_START, 47.5))
    .box(POCKET_CUT_DEPTH, POCKET_Y_DEPTH, POCKET_WIDTH, centered=False)
)
bridge_l2 = (
    cq.Workplane("XY")
    .transformed(offset=(RABBET_DEPTH, RABBET_Y_START, 47.5))
    .box(3.5 - RABBET_DEPTH, RABBET_Y_LEN, BRIDGE, centered=False)
)

# --- Feature 7: Pocket R1 (Right Wall, Lower) ---
# X=155.0..156.5, Y=152..155, Z=19.5..24.5
pocket_r1 = (
    cq.Workplane("XY")
    .transformed(offset=(155.0, POCKET_Y_START, 19.5))
    .box(POCKET_CUT_DEPTH, POCKET_Y_DEPTH, POCKET_WIDTH, centered=False)
)
# Bridge from pocket end (X=156.5) to right rabbet (X=158.5..160) in shared Y zone
bridge_r1 = (
    cq.Workplane("XY")
    .transformed(offset=(156.5, RABBET_Y_START, 19.5))
    .box(TRAY_WIDTH - RABBET_DEPTH - 156.5, RABBET_Y_LEN, BRIDGE, centered=False)
)

# --- Feature 8: Pocket R2 (Right Wall, Upper) ---
# X=155.0..156.5, Y=152..155, Z=47.5..52.5
pocket_r2 = (
    cq.Workplane("XY")
    .transformed(offset=(155.0, POCKET_Y_START, 47.5))
    .box(POCKET_CUT_DEPTH, POCKET_Y_DEPTH, POCKET_WIDTH, centered=False)
)
bridge_r2 = (
    cq.Workplane("XY")
    .transformed(offset=(156.5, RABBET_Y_START, 47.5))
    .box(TRAY_WIDTH - RABBET_DEPTH - 156.5, RABBET_Y_LEN, BRIDGE, centered=False)
)

# --- Feature 9: Pocket F1 (Floor, Center) ---
# X=77.5..82.5, Y=152..155, Z=1.5..3.0
# This pocket sits directly above the floor rabbet (Z=0..1.5).
# The floor rabbet and F1 share the face at Z=1.5 in Y=153.5..155.
pocket_f1 = (
    cq.Workplane("XY")
    .transformed(offset=(77.5, POCKET_Y_START, RABBET_DEPTH))
    .box(POCKET_WIDTH, POCKET_Y_DEPTH, POCKET_CUT_DEPTH, centered=False)
)
# Bridge overlapping both: spans Z=1.5-BRIDGE..1.5+BRIDGE to bridge the face
bridge_f1 = (
    cq.Workplane("XY")
    .transformed(offset=(77.5, RABBET_Y_START, RABBET_DEPTH - BRIDGE))
    .box(POCKET_WIDTH, RABBET_Y_LEN, 2 * BRIDGE, centered=False)
)

# --- Union everything into a single solid ---
cut_tool = rabbet

# Add each pocket + its bridge
for pocket, bridge in [
    (pocket_l1, bridge_l1),
    (pocket_l2, bridge_l2),
    (pocket_r1, bridge_r1),
    (pocket_r2, bridge_r2),
    (pocket_f1, bridge_f1),
]:
    cut_tool = cut_tool.union(bridge).union(pocket)

# ==================================================================
# Export STEP
# ==================================================================
step_path = str(Path(__file__).with_suffix(".step"))
cq.exporters.export(cut_tool, step_path)
print(f"\nExported STEP: {step_path}")

# ==================================================================
# Validation
# ==================================================================
print("\n--- Validation ---\n")

v = Validator(cut_tool)

# -- Left Wall Rabbet --
v.check_solid("Left rabbet center", 0.75, 154.25, 36.0, "solid inside left rabbet cut")
v.check_solid("Left rabbet near X=0", 0.1, 154.25, 36.0, "solid at outer edge of left rabbet")
v.check_void("Left rabbet outside X", 2.0, 154.25, 36.0, "void outside left rabbet in X")
v.check_void("Left rabbet behind Y", 0.75, 153.0, 36.0, "void behind left rabbet in Y")

# -- Right Wall Rabbet --
v.check_solid("Right rabbet center", 159.25, 154.25, 36.0, "solid inside right rabbet cut")
v.check_solid("Right rabbet near X=160", 159.9, 154.25, 36.0, "solid at outer edge of right rabbet")
v.check_void("Right rabbet outside X", 158.0, 154.25, 36.0, "void outside right rabbet in X")

# -- Floor Rabbet --
v.check_solid("Floor rabbet center", 80.0, 154.25, 0.75, "solid inside floor rabbet cut")
v.check_solid("Floor rabbet at X=80", 80.0, 154.25, 0.1, "solid near Z=0 in floor rabbet")
v.check_void("Floor rabbet above Z", 40.0, 154.25, 2.0, "void above floor rabbet at X=40")

# -- Corner Fillets --
v.check_void("Left fillet relief", 1.0, 154.25, 1.0,
             "void at left corner fillet relief")
v.check_void("Right fillet relief", 159.0, 154.25, 1.0,
             "void at right corner fillet relief")
v.check_solid("Left rabbet below fillet", 0.75, 154.25, 0.5, "solid in floor rabbet below left fillet")
v.check_solid("Left rabbet above fillet", 0.75, 154.25, 2.0, "solid in left wall rabbet above fillet")

# -- Pocket L1 --
v.check_solid("Pocket L1 center", 4.25, 153.5, 22.0, "solid inside L1 pocket")
v.check_solid("Pocket L1 Y=152.5", 4.25, 152.5, 22.0, "solid at rear of L1 pocket")
v.check_void("Pocket L1 outside X", 5.5, 153.5, 22.0, "void outside L1 in X")
v.check_void("Pocket L1 outside Z+", 4.25, 153.5, 25.0, "void above L1 in Z")
v.check_void("Pocket L1 behind Y", 4.25, 151.5, 22.0, "void behind L1 in Y")

# -- Pocket L2 --
v.check_solid("Pocket L2 center", 4.25, 153.5, 50.0, "solid inside L2 pocket")
v.check_void("Pocket L2 outside X", 5.5, 153.5, 50.0, "void outside L2 in X")
v.check_void("Pocket L2 outside Z-", 4.25, 153.5, 47.0, "void below L2 in Z")

# -- Pocket R1 --
v.check_solid("Pocket R1 center", 155.75, 153.5, 22.0, "solid inside R1 pocket")
v.check_void("Pocket R1 outside X", 154.5, 153.5, 22.0, "void outside R1 in X")
v.check_void("Pocket R1 outside Z+", 155.75, 153.5, 25.0, "void above R1 in Z")

# -- Pocket R2 --
v.check_solid("Pocket R2 center", 155.75, 153.5, 50.0, "solid inside R2 pocket")
v.check_void("Pocket R2 outside X", 154.5, 153.5, 50.0, "void outside R2 in X")

# -- Pocket F1 --
v.check_solid("Pocket F1 center", 80.0, 153.5, 2.25, "solid inside F1 pocket")
v.check_void("Pocket F1 outside Z+", 80.0, 153.5, 3.5, "void above F1 in Z")
v.check_void("Pocket F1 outside X-", 77.0, 153.5, 2.25, "void left of F1 in X")
v.check_void("Pocket F1 outside X+", 83.0, 153.5, 2.25, "void right of F1 in X")

# -- Bounding Box --
bb = cut_tool.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, 0.0, 160.0)
v.check_bbox("Y", bb.ymin, bb.ymax, 152.0, 155.0)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, 72.0)

# -- Solid Integrity --
v.check_valid()
v.check_single_body()

# Volume check
envelope = 160.0 * 3.0 * 72.0
v.check_volume(expected_envelope=envelope, fill_range=(0.01, 0.5))

# -- Summary --
if not v.summary():
    sys.exit(1)
