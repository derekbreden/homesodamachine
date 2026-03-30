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

PANEL_W = 140.0   # X — panel width (left to right, interior X span)
PANEL_D = 123.0   # Y — panel depth (front to back, interior Y span)
PANEL_T = 3.0     # Z — panel thickness (fits 3.4mm channel, 0.2mm clearance each side)

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

# Feature 1: Panel body — flat box, no features
panel = cq.Workplane("XY").box(PANEL_W, PANEL_D, PANEL_T, centered=False)
# Envelope: X:[0,140.0] Y:[0,123.0] Z:[0,3.0]

# ==============================================================================
# Validation (Rubrics 3, 4, 5)
# ==============================================================================

v = Validator(panel)

# Rubric 3 — Feature-Specification Reconciliation
# Feature 1: Panel body — probe interior and all faces

# Interior solid probe
v.check_solid("Panel body interior center",    70.0, 61.5, 1.5,   "solid at panel center")

# Near each face — still solid (0.1mm in from each face)
v.check_solid("Panel body X+ face interior",  139.9, 61.5, 1.5,  "solid near X+ face")
v.check_solid("Panel body X- face interior",    0.1, 61.5, 1.5,  "solid near X- face")
v.check_solid("Panel body Y+ face interior",   70.0, 122.9, 1.5, "solid near Y+ face")
v.check_solid("Panel body Y- face interior",   70.0,  0.1,  1.5, "solid near Y- face")
v.check_solid("Panel body Z+ face interior",   70.0, 61.5, 2.9,  "solid near Z+ face")
v.check_solid("Panel body Z- face interior",   70.0, 61.5, 0.1,  "solid near Z- face")

# Rubric 5 — Bounding Box Reconciliation
bb = panel.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, 0.0, PANEL_W)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, PANEL_D)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, PANEL_T)

# Rubric 4 — Solid Validity
v.check_valid()
v.check_single_body()
v.check_volume(expected_envelope=PANEL_W * PANEL_D * PANEL_T, fill_range=(0.95, 1.05))

# Summary — exits 1 on any failure
if not v.summary():
    sys.exit(1)

# ==============================================================================
# Export STEP
# ==============================================================================

out_path = Path(__file__).resolve().parent / "bottom-panel-cadquery.step"
panel.val().exportStep(str(out_path))
print(f"\nSTEP exported: {out_path}")
