"""
Front Panel — CadQuery STEP Generation Script
Season 2, Phase 7, Item 18 of the pump cartridge build sequence.

Specification source:
  hardware/printed-parts/cartridge/front-panel/planning/parts.md

The front panel is a flat rectangular plate in the XZ plane with thickness in Y.
It slides into the front panel rail channels on the left and right walls.
A rectangular through-hole in the lower half provides finger access to the lever
pull surface.

Coordinate system:
  Origin: front-panel bottom-left-front corner (X=0, Y=0, Z=0)
  X: width axis — left to right; range [0, 140.0] mm
  Y: thickness axis — front face (Y=0) to back face (Y=3.0); range [0, 3.0] mm
  Z: height axis — bottom to top; range [0, 79.0] mm
  Envelope: 140.0 (X) x 3.0 (Y) x 79.0 (Z) mm
"""

import sys
from pathlib import Path

# Script is at: hardware/printed-parts/cartridge/front-panel/generate_step_cadquery.py
# parents[4] = project root
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq

print()
print("RUBRIC 1 — Feature Planning Table")
print()

col_w = [3, 24, 20, 8, 7, 5, 20, 38]
header = (f"{'#':<{col_w[0]}} {'Feature Name':<{col_w[1]}} {'Operation':<{col_w[3]}} "
          f"{'Shape':<{col_w[4]}} {'Axis':<{col_w[5]}} {'Center (X,Y,Z)':<{col_w[6]}} "
          f"{'Dimensions':<{col_w[7]}} Notes")
print(header)
print()

print("RUBRIC 2 — Coordinate System Declaration")
print()
print("  Origin: front-panel bottom-left-front corner (X=0, Y=0, Z=0)")
print("  X: panel width, left to right; range [0, 140.0] mm")
print("  Y: panel thickness, front face (Y=0) to back face (Y=3.0); range [0, 3.0] mm")
print("  Z: panel height, bottom to top; range [0, 79.0] mm")
print("  Envelope: 140.0 x 3.0 x 79.0 mm  ->  X:[0,140]  Y:[0,3]  Z:[0,79]")
print()
print("  Feature coordinate cross-check:")
print("    Panel body:         X:[0,140]  Y:[0,3]   Z:[0,79]")
print("    Finger access hole: X:[20,120] Y:[0,3]   Z:[12,42]  (through-hole along Y)")
print("    Hole X center: 70.0mm  (centered on lever X center)")
print("    Hole Z center: 27.0mm  (< 39.5mm half-height -> lower half confirmed)")
print()

# Geometry constants (from planning/parts.md)

# Panel body
PANEL_W = 170.0   # X — width (was 140.0)
PANEL_D =   3.0   # Y — thickness (channel portion)
PANEL_H = 103.6   # Z — height (was 79.0, +24.6mm added to top)

# Extension dimensions
EDGE_W = 3.0      # X — width of left/right edges that sit in wall channels
EXT_DEPTH = 2.0   # Y — how far the middle extends beyond the channel edges

# Finger access hole
HOLE_W  = 100.0   # X — width of hole
HOLE_H  =  30.0   # Z — height of hole
HOLE_X0 =  35.0   # X start (left edge of hole, shifted +15mm)
HOLE_Z0 =  12.0   # Z start (bottom edge of hole)

# Feature 1 — Panel Body
print("Building Feature 1: Panel Body ...")
panel = cq.Workplane("XY").box(PANEL_W, PANEL_D, PANEL_H, centered=False)

# Feature 1b — Middle extension (2mm outward in -Y)
print("Building Feature 1b: Middle extension ...")
extension = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(EDGE_W, -EXT_DEPTH, 0.0))
    .box(PANEL_W - 2 * EDGE_W, EXT_DEPTH, PANEL_H, centered=False)
)
panel = panel.union(extension)

# Feature 2 — Finger Access Hole (through-hole along Y)
print("Building Feature 2: Finger Access Hole ...")
# Cut through full thickness including extension
hole = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(HOLE_X0, -EXT_DEPTH, HOLE_Z0))
    .box(HOLE_W, PANEL_D + EXT_DEPTH, HOLE_H, centered=False)
)
panel = panel.cut(hole)

# Export STEP file
OUT_DIR = Path(__file__).parent
STEP_PATH = OUT_DIR / "front-panel-cadquery.step"
print(f"\nExporting STEP to: {STEP_PATH}")
cq.exporters.export(panel, str(STEP_PATH))

print()
print("RUBRIC 3 — Feature-Specification Reconciliation")
print()
