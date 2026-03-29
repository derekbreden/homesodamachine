"""
Sub-G: Linkage Rod Guide Slots — CUT TOOL
Two identical rectangular through-slot solids (union) for boolean subtraction
from the tray shell (Sub-A).

Left slot:  X=0..5,   Y=17..23, Z=35..40
Right slot: X=155..160, Y=17..23, Z=35..40
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq
from step_validate import Validator

# Coordinate system:
#   Origin: rear-left-bottom corner of the tray (Sub-A reference frame)
#   X: width, left to right, 0 to 160 mm
#   Y: depth, rear (dock) to front (user), 0 to 155 mm
#   Z: height, bottom to top, 0 to 72 mm
#   This cut tool envelope: X:[0,160] Y:[17,23] Z:[35,40]

# ============================================================
# Feature Planning Table
# ============================================================
print("Feature Planning Table:")
print("=" * 90)
print(f"{'#':<4}{'Feature':<22}{'Function':<28}{'Op':<8}{'Shape':<8}{'Axis':<6}{'Position':<24}{'Dimensions'}")
print("-" * 90)
print(f"{'1':<4}{'Left wall slot':<22}{'Linkage rod passthrough':<28}{'Add':<8}{'Box':<8}{'X':<6}{'X=2.5, Y=20, Z=37.5':<24}5x6x5 (XxYxZ)")
print(f"{'2':<4}{'Right wall slot':<22}{'Linkage rod passthrough':<28}{'Add':<8}{'Box':<8}{'X':<6}{'X=157.5, Y=20, Z=37.5':<24}5x6x5 (XxYxZ)")
print("=" * 90)
print()

# ============================================================
# Slot dimensions (from spec)
# ============================================================
# Left wall slot
LEFT_X_MIN = 0.0
LEFT_X_MAX = 5.0
# Right wall slot
RIGHT_X_MIN = 155.0
RIGHT_X_MAX = 160.0
# Shared Y and Z ranges
Y_MIN = 17.0
Y_MAX = 23.0
Z_MIN = 35.0
Z_MAX = 40.0

SLOT_X = LEFT_X_MAX - LEFT_X_MIN   # 5 mm (wall thickness)
SLOT_Y = Y_MAX - Y_MIN             # 6 mm (slot length)
SLOT_Z = Z_MAX - Z_MIN             # 5 mm (slot width)

# ============================================================
# Build the cut tool — union of two boxes
# ============================================================
# Left slot: origin at (0, 17, 35), size 5x6x5
left_slot = (
    cq.Workplane("XY")
    .box(SLOT_X, SLOT_Y, SLOT_Z, centered=False)
    .translate((LEFT_X_MIN, Y_MIN, Z_MIN))
)

# Right slot: origin at (155, 17, 35), size 5x6x5
right_slot = (
    cq.Workplane("XY")
    .box(SLOT_X, SLOT_Y, SLOT_Z, centered=False)
    .translate((RIGHT_X_MIN, Y_MIN, Z_MIN))
)

# Union both slots into a single solid
cut_tool = left_slot.union(right_slot)

# ============================================================
# Export STEP
# ============================================================
step_path = str(Path(__file__).with_suffix(".step"))
cq.exporters.export(cut_tool, step_path)
print(f"Exported STEP: {step_path}")
print()

# ============================================================
# Validation
# ============================================================
print("Validation:")
print("-" * 60)

v = Validator(cut_tool)

# --- Left slot probes ---
v.check_solid("Left slot center", 2.5, 20.0, 37.5, "solid at left slot center")
v.check_solid("Left slot near Y-min", 2.5, 17.5, 37.5, "solid near Y=17 end")
v.check_solid("Left slot near Y-max", 2.5, 22.5, 37.5, "solid near Y=23 end")
v.check_solid("Left slot near Z-min", 2.5, 20.0, 35.5, "solid near Z=35 edge")
v.check_solid("Left slot near Z-max", 2.5, 20.0, 39.5, "solid near Z=40 edge")
v.check_solid("Left slot near X-min", 0.5, 20.0, 37.5, "solid near X=0 face")
v.check_solid("Left slot near X-max", 4.5, 20.0, 37.5, "solid near X=5 face")

# Outside left slot boundaries
v.check_void("Outside left slot Y-", 2.5, 16.5, 37.5, "void below Y=17")
v.check_void("Outside left slot Y+", 2.5, 23.5, 37.5, "void above Y=23")
v.check_void("Outside left slot Z-", 2.5, 20.0, 34.5, "void below Z=35")
v.check_void("Outside left slot Z+", 2.5, 20.0, 40.5, "void above Z=40")
v.check_void("Outside left slot X+", 5.5, 20.0, 37.5, "void beyond X=5")

# --- Right slot probes ---
v.check_solid("Right slot center", 157.5, 20.0, 37.5, "solid at right slot center")
v.check_solid("Right slot near Y-min", 157.5, 17.5, 37.5, "solid near Y=17 end")
v.check_solid("Right slot near Y-max", 157.5, 22.5, 37.5, "solid near Y=23 end")
v.check_solid("Right slot near Z-min", 157.5, 20.0, 35.5, "solid near Z=35 edge")
v.check_solid("Right slot near Z-max", 157.5, 20.0, 39.5, "solid near Z=40 edge")
v.check_solid("Right slot near X-min", 155.5, 20.0, 37.5, "solid near X=155 face")
v.check_solid("Right slot near X-max", 159.5, 20.0, 37.5, "solid near X=160 face")

# Outside right slot boundaries
v.check_void("Outside right slot Y-", 157.5, 16.5, 37.5, "void below Y=17")
v.check_void("Outside right slot Y+", 157.5, 23.5, 37.5, "void above Y=23")
v.check_void("Outside right slot Z-", 157.5, 20.0, 34.5, "void below Z=35")
v.check_void("Outside right slot Z+", 157.5, 20.0, 40.5, "void above Z=40")
v.check_void("Outside right slot X-", 154.5, 20.0, 37.5, "void before X=155")

# Gap between slots should be void
v.check_void("Gap between slots", 80.0, 20.0, 37.5, "void at tray centerline")

# --- Bounding box ---
bb = cut_tool.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, 0.0, 160.0)
v.check_bbox("Y", bb.ymin, bb.ymax, 17.0, 23.0)
v.check_bbox("Z", bb.zmin, bb.zmax, 35.0, 40.0)

# --- Solid integrity ---
v.check_valid()
# Two disjoint boxes — expect 2 bodies after union (they don't touch)
# Actually CadQuery union of disjoint solids may produce a compound with 2 solids.
# The spec says "model as a single solid (union of both slots)" but they are disjoint.
# check_single_body may fail; let's check the count first.
num_bodies = len(cut_tool.solids().vals())
print(f"\n  Body count: {num_bodies} (disjoint slots are expected as compound)")

# Volume check: each slot is 5*6*5=150 mm^3, total=300 mm^3
# Envelope for volume ratio: use actual total volume as reference
SLOT_VOL = SLOT_X * SLOT_Y * SLOT_Z  # 150 mm^3 each
TOTAL_VOL = 2 * SLOT_VOL  # 300 mm^3
v.check_volume(expected_envelope=TOTAL_VOL, fill_range=(0.95, 1.05))

# --- Summary ---
if not v.summary():
    sys.exit(1)
