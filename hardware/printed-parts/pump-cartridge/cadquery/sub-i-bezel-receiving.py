#!/usr/bin/env python3
"""
Sub-I: Front Bezel Receiving Features — CUT TOOL

Generates a compound solid representing all material to be removed from
the tray (Sub-A) for the front bezel receiving features. This solid is
intended for subtraction (boolean cut) from the tray body.

Features modeled:
  1. Step-lap rabbet (3 segments: left wall, right wall, floor)
     with 1 mm corner fillets at the two bottom intersections
  2. Five snap tab pockets: L1, L2, R1, R2, F1
     (T1 skipped — flagged as design gap, no material exists there)

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
| 4 | Corner Fillets (x2)   | Printability/stress relief       | Remove | Fillet R=1  | Y    | At X=1.5,Z=1.5 and X=158.5,Z=1.5       | R=1.0, L=1.5 along Y  |
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

# ==================================================================
# Build the cut tool
# ==================================================================
# Strategy: Build the rabbet as a union of 3 boxes, apply fillets to the
# inside corners, then build pockets separately. Since the pockets are
# geometrically disjoint from the rabbet (they don't touch), we combine
# everything into a single CadQuery Compound for export and subtraction.

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

# Union the three rabbet segments (they overlap at the corners, forming an
# L-shaped cross-section on each side)
rabbet = left_rabbet.union(right_rabbet).union(floor_rabbet)

# --- Feature 4: Corner Fillets ---
# The rabbet union has concave inside corners at (X=1.5, Z=1.5) and
# (X=158.5, Z=1.5), running along Y from 153.5 to 155.
# These are inside (concave) edges of the L-shaped cross-section.
# Filleting these edges rounds the inside corner of the CUT TOOL, which
# produces a rounded inside corner on the TRAY after subtraction.
#
# CadQuery .fillet() on a concave edge removes material from the solid
# (adds a curved transition that is tangent to both faces). This means
# the cut tool has LESS material at the diagonal, so the tray retains
# a rounded fillet at its inside corner.

rabbet = (
    rabbet
    .edges("|Y")
    .edges(
        cq.selectors.NearestToPointSelector(
            (RABBET_DEPTH, RABBET_Y_START + RABBET_Y_LEN / 2, RABBET_DEPTH)
        )
    )
    .fillet(FILLET_R)
)

rabbet = (
    rabbet
    .edges("|Y")
    .edges(
        cq.selectors.NearestToPointSelector(
            (TRAY_WIDTH - RABBET_DEPTH, RABBET_Y_START + RABBET_Y_LEN / 2, RABBET_DEPTH)
        )
    )
    .fillet(FILLET_R)
)

# --- Feature 5: Pocket L1 (Left Wall, Lower) ---
# X=3.5..5.0, Y=152..155, Z=19.5..24.5
pocket_l1 = (
    cq.Workplane("XY")
    .transformed(offset=(3.5, POCKET_Y_START, 19.5))
    .box(POCKET_CUT_DEPTH, POCKET_Y_DEPTH, POCKET_WIDTH, centered=False)
)

# --- Feature 6: Pocket L2 (Left Wall, Upper) ---
# X=3.5..5.0, Y=152..155, Z=47.5..52.5
pocket_l2 = (
    cq.Workplane("XY")
    .transformed(offset=(3.5, POCKET_Y_START, 47.5))
    .box(POCKET_CUT_DEPTH, POCKET_Y_DEPTH, POCKET_WIDTH, centered=False)
)

# --- Feature 7: Pocket R1 (Right Wall, Lower) ---
# X=155.0..156.5, Y=152..155, Z=19.5..24.5
pocket_r1 = (
    cq.Workplane("XY")
    .transformed(offset=(155.0, POCKET_Y_START, 19.5))
    .box(POCKET_CUT_DEPTH, POCKET_Y_DEPTH, POCKET_WIDTH, centered=False)
)

# --- Feature 8: Pocket R2 (Right Wall, Upper) ---
# X=155.0..156.5, Y=152..155, Z=47.5..52.5
pocket_r2 = (
    cq.Workplane("XY")
    .transformed(offset=(155.0, POCKET_Y_START, 47.5))
    .box(POCKET_CUT_DEPTH, POCKET_Y_DEPTH, POCKET_WIDTH, centered=False)
)

# --- Feature 9: Pocket F1 (Floor, Center) ---
# X=77.5..82.5, Y=152..155, Z=1.5..3.0
pocket_f1 = (
    cq.Workplane("XY")
    .transformed(offset=(77.5, POCKET_Y_START, 1.5))
    .box(POCKET_WIDTH, POCKET_Y_DEPTH, POCKET_CUT_DEPTH, centered=False)
)

# ==================================================================
# Combine all features into a single compound
# ==================================================================
# The rabbet and pockets are geometrically disjoint (pockets are at X=3.5..5
# and X=155..156.5, while the rabbet walls are at X=0..1.5 and X=158.5..160).
# CadQuery's .union() cannot fuse disjoint solids into one body — they remain
# separate solids in the compound. We use OCP Compound to wrap them all.

from OCP.TopoDS import TopoDS_Compound
from OCP.BRep import BRep_Builder

all_solids = []
# Rabbet (already a union of left/right/floor with fillets)
all_solids.extend([s.wrapped for s in rabbet.solids().vals()])
# Pockets
for pocket in [pocket_l1, pocket_l2, pocket_r1, pocket_r2, pocket_f1]:
    all_solids.extend([s.wrapped for s in pocket.solids().vals()])

builder = BRep_Builder()
compound = TopoDS_Compound()
builder.MakeCompound(compound)
for s in all_solids:
    builder.Add(compound, s)

# Wrap back into CadQuery for export and validation
cut_tool = cq.Workplane("XY").newObject([cq.Shape(compound)])

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

# For validation, we need point-in-solid checks. The Validator expects a
# single solid, but we have a compound. We'll build a custom validation
# approach using the compound's constituent solids.
# Actually, BRepClass3d_SolidClassifier works on compounds too if we
# iterate. Let's check each point against any solid in the compound.

from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN


class CompoundValidator:
    """Validates points against a compound of multiple solids."""

    def __init__(self, solids_list):
        self._solids = solids_list
        self._results = []

    def _is_in_any(self, x, y, z, tol=0.001):
        pt = gp_Pnt(x, y, z)
        for s in self._solids:
            c = BRepClass3d_SolidClassifier(s, pt, tol)
            if c.State() == 0:  # TopAbs_IN
                return True
        return False

    def _record(self, name, passed, detail):
        status = "PASS" if passed else "FAIL"
        self._results.append((name, status, detail))
        print(f"  [{status}] {name}: {detail}")
        return passed

    def check_solid(self, name, x, y, z, detail=None):
        result = self._is_in_any(x, y, z)
        detail = detail or f"solid at ({x:.2f}, {y:.2f}, {z:.2f})"
        return self._record(name, result, detail)

    def check_void(self, name, x, y, z, detail=None):
        result = not self._is_in_any(x, y, z)
        detail = detail or f"void at ({x:.2f}, {y:.2f}, {z:.2f})"
        return self._record(name, result, detail)

    def check_bbox(self, axis_name, actual_min, actual_max, expected_min, expected_max, tol=0.5):
        ok = abs(actual_min - expected_min) < tol and abs(actual_max - expected_max) < tol
        detail = f"[{actual_min:.2f}, {actual_max:.2f}] vs expected [{expected_min:.2f}, {expected_max:.2f}]"
        return self._record(f"Bounding box {axis_name}", ok, detail)

    @property
    def all_passed(self):
        return all(s == "PASS" for _, s, _ in self._results)

    @property
    def fail_count(self):
        return sum(1 for _, s, _ in self._results if s == "FAIL")

    def summary(self):
        print()
        print("=" * 60)
        total = len(self._results)
        if self.all_passed:
            print(f"ALL {total} CHECKS PASSED")
        else:
            print(f"{self.fail_count} of {total} CHECKS FAILED:")
            for name, status, detail in self._results:
                if status == "FAIL":
                    print(f"  - {name}: {detail}")
        print("=" * 60)
        return self.all_passed


v = CompoundValidator(all_solids)

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
# Probe above floor rabbet at X position away from F1 pocket (which is at X=77.5..82.5)
v.check_void("Floor rabbet above Z", 40.0, 154.25, 2.0, "void above floor rabbet at X=40")

# -- Corner Fillets --
# The concave fillet on the inside corner of the L-shaped cut tool ADDS material
# to fill the concave gap with a curved transition. The fillet arc center is at
# (1.5+1.0, 1.5+1.0) = (2.5, 2.5). The arc spans from (2.5, 1.5) to (1.5, 2.5).
# Points inside the fillet material (closer to corner than the arc) should be solid.
# Points outside the fillet arc (further from corner) should be void.
# At (1.6, 1.6): dist from (2.5, 2.5) = sqrt(1.62) = 1.27 > R=1.0 => solid (fillet material)
v.check_solid("Left fillet material", 1.6, 154.25, 1.6,
              "solid inside left corner fillet material")
v.check_solid("Right fillet material", 158.4, 154.25, 1.6,
              "solid inside right corner fillet material")
# A point well outside the arc should be void: (2.2, 2.2) dist from (2.5,2.5) = 0.42 < 1.0 => void
v.check_void("Left fillet outside arc", 2.2, 154.25, 2.2,
             "void outside left corner fillet arc")
v.check_void("Right fillet outside arc", 157.8, 154.25, 2.2,
             "void outside right corner fillet arc")
# Points firmly inside the rabbet arms should still be solid
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
# Compute bounding box from all solids using CadQuery's Shape wrapper
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

bbox = Bnd_Box()
for s in all_solids:
    BRepBndLib.Add_s(s, bbox)
xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()

v.check_bbox("X", xmin, xmax, 0.0, 160.0)
v.check_bbox("Y", ymin, ymax, 152.0, 155.0)
v.check_bbox("Z", zmin, zmax, 0.0, 72.0)

# -- Solid Integrity --
# For a compound cut tool, we verify each constituent solid is valid
# and count total bodies
n_solids = len(all_solids)
print(f"\n  [INFO] Compound has {n_solids} disjoint solids (rabbet + 5 pockets)")
# The rabbet is 1 body (union of 3 boxes with fillets), pockets are 5 separate bodies = 6 total
v._record("Body count", n_solids == 6, f"{n_solids} bodies (expected 6: 1 rabbet + 5 pockets)")

# Check each solid is valid
from OCP.BRepCheck import BRepCheck_Analyzer
all_valid = True
for i, s in enumerate(all_solids):
    analyzer = BRepCheck_Analyzer(s)
    if not analyzer.IsValid():
        all_valid = False
        print(f"  [FAIL] Solid {i} invalid")
v._record("All solids valid", all_valid, "all constituent solids pass OCC validity")

# Volume check: sum of all solid volumes
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp

props = GProp_GProps()
for s in all_solids:
    p = GProp_GProps()
    BRepGProp.VolumeProperties_s(s, p)
    props.Add(p)
total_vol = props.Mass()
envelope = 160.0 * 3.0 * 72.0
ratio = total_vol / envelope
ok = 0.01 < ratio < 0.5
v._record("Volume ratio", ok,
          f"{total_vol:.1f} mm3 ({ratio:.1%} of {envelope:.0f} mm3 envelope, expected 1%-50%)")

# -- Summary --
if not v.summary():
    sys.exit(1)
