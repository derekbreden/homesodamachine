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

# Add tools/ to sys.path for step_validate import
# Script is at: hardware/printed-parts/cartridge/bottom-panel/generate_step_cadquery.py
# parents[4] = project root
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq
from step_validate import Validator

# ==============================================================================
# Part parameters (from planning/parts.md)
# ==============================================================================

PANEL_W = 170.0   # X — panel width (left to right, was 140.0)
PANEL_D = 188.0   # Y — panel depth (back to front, full wall length)
PANEL_T = 3.0     # Z — panel thickness (fits 3.4mm channel, 0.2mm clearance each side)

# Channel edge dimensions
EDGE_W = 3.0      # X — width of left/right edges that sit in wall channels
EXT_DEPTH = 2.0   # Z — how far the middle extends below the channel edges

# ==============================================================================
# Rubric 1 — Feature Planning Table (MANDATORY, before coding)
# ==============================================================================

FEATURE_TABLE = """
BOTTOM PANEL — FEATURE PLANNING TABLE (Rubric 1)
=================================================

Part envelope: 140.0mm (X) x 123.0mm (Y) x 3.0mm (Z)

Coordinate system (Rubric 2):
  Origin: panel front-bottom-left corner (X=0, Y=0, Z=0)
  X: panel width, left (X=0) to right (X=140.0mm)
  Y: panel depth, front (Y=0) to back (Y=123.0mm)
  Z: panel thickness, bottom (Z=0) to top (Z=3.0mm)

  #   Feature Name   Op    Shape  Axis  Center Position (X,Y,Z)        Dimensions              Notes
  1   Panel body     Add   Box    —     (70.0, 61.5, 1.5)              140.0 x 123.0 x 3.0mm   Flat panel, no features

  Total: 1 feature (flat panel body)
"""

print(FEATURE_TABLE)

# ==============================================================================
# Modeling
# ==============================================================================

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

# ==============================================================================
# Validation (Rubrics 3, 4, 5)
# ==============================================================================

v = Validator(panel)

# Rubric 3 — Feature-Specification Reconciliation
# Feature 1: Panel body — probe interior and all faces

# Interior solid probe — main slab
v.check_solid("Panel body interior center",    85.0, 94.0, 1.5,   "solid at panel center")

# Near each face of main slab
v.check_solid("Panel body X+ face interior",  169.9, 94.0, 1.5,  "solid near X+ face")
v.check_solid("Panel body X- face interior",    0.1, 94.0, 1.5,  "solid near X- face")
v.check_solid("Panel body Y+ face interior",   85.0, 187.9, 1.5, "solid near Y+ face")
v.check_solid("Panel body Y- face interior",   85.0,  0.1,  1.5, "solid near Y- face")
v.check_solid("Panel body Z+ face interior",   85.0, 94.0, 2.9,  "solid near Z+ face")

# Middle extension probes
v.check_solid("Extension center",              85.0, 94.0, -1.0,  "solid in middle extension")
v.check_solid("Extension near bottom",         85.0, 94.0, -1.9,  "solid near extension bottom face")

# Left edge: no extension below Z=0
v.check_void("Left edge no extension",          1.5, 94.0, -1.0,  "void below left channel edge")
# Right edge: no extension below Z=0
v.check_void("Right edge no extension",       168.5, 94.0, -1.0,  "void below right channel edge")

# Rubric 5 — Bounding Box Reconciliation
bb = panel.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, 0.0, PANEL_W)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, PANEL_D)
v.check_bbox("Z", bb.zmin, bb.zmax, -EXT_DEPTH, PANEL_T)

# Rubric 4 — Solid Validity
v.check_valid()
v.check_single_body()
total_vol = (PANEL_W * PANEL_D * PANEL_T) + ((PANEL_W - 2 * EDGE_W) * PANEL_D * EXT_DEPTH)
v.check_volume(expected_envelope=PANEL_W * PANEL_D * (PANEL_T + EXT_DEPTH), fill_range=(0.90, 1.05))

# Summary — exits 1 on any failure
if not v.summary():
    sys.exit(1)

# ==============================================================================
# Export STEP
# ==============================================================================

out_path = Path(__file__).resolve().parent / "bottom-panel-cadquery.step"
panel.val().exportStep(str(out_path))
print(f"\nSTEP exported: {out_path}")
