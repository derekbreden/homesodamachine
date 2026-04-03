"""
Bottom Panel — CadQuery STEP Generation Script

Specification source: hardware/printed-parts/cartridge/bottom-panel/planning/parts.md

The bottom panel is a flat panel with no features. It spans the interior floor
of the pump cartridge, captured in the bottom panel channels of the left and
right walls (Z=2.0..5.4mm in wall coordinates, 3.4mm channel width).

Coordinate system:
  Origin: panel front-bottom-left corner (X=0, Y=0, Z=0)
  X: panel width axis — left to right, X=0..140.0mm
  Y: panel depth axis — front to back, Y=0..123.0mm
  Z: panel thickness axis — bottom to top, Z=0..3.0mm
  Envelope: 140.0mm (X) x 123.0mm (Y) x 3.0mm (Z)
"""

import sys
from pathlib import Path

# Script is at: hardware/printed-parts/cartridge/bottom-panel/generate_step_cadquery.py
# parents[4] = project root
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq

# Part parameters (from planning/parts.md)

PANEL_W = 170.0   # X — panel width (left to right, was 140.0)
PANEL_D = 188.0   # Y — panel depth (back to front, full wall length)
PANEL_T = 3.0     # Z — panel thickness (fits 3.4mm channel, 0.2mm clearance each side)

# Channel edge dimensions
EDGE_W = 3.0      # X — width of left/right edges that sit in wall channels
EXT_DEPTH = 2.0   # Z — how far the middle extends below the channel edges

# Modeling

# Feature 1: Panel body — flat slab (top face flush, sits in channels)
panel = cq.Workplane("XY").box(PANEL_W, PANEL_D, PANEL_T, centered=False)
# X:[0,170] Y:[0,188] Z:[0,3]

# Feature 2: Middle extension — 2mm downward below the main slab,
# excluding the 3mm left and right edges that sit in the wall channels.
# X: EDGE_W to PANEL_W - EDGE_W (3..167), Y: full depth, Z: -2..0
extension = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(EDGE_W, 0, -EXT_DEPTH))
    .box(PANEL_W - 2 * EDGE_W, PANEL_D, EXT_DEPTH, centered=False)
)
panel = panel.union(extension)
print("  [+] Feature 2: Middle extension (2mm down, X=3..167)")

# Export STEP file
OUTPUT_STEP = Path(__file__).resolve().parent / "bottom-panel-cadquery.step"
print(f"Exporting STEP file → {OUTPUT_STEP}")
cq.exporters.export(panel, str(OUTPUT_STEP))
