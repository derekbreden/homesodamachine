#!/usr/bin/env python3
"""
Enclosure Top Panel — CadQuery STEP Generator

Generates the removable top panel (lid) for the soda flavor injector enclosure.
A flat rectangular panel with a 100mm hopper opening, raised pour lip,
tongue-and-groove underside for tub rim engagement, and steel disc pockets
for magnetic retention.

Coordinate system:
  Origin: front-left corner of panel, bottom surface
  X: width, left to right [0, 220]
  Y: depth, front to back [0, 300]
  Z: thickness, bottom (0) to top (4), lip extends to Z=7
  Envelope: 220 x 300 x 7 mm (including lip)

  Bottom face (Z=0): sits on tub rim at enclosure Z=396
  Top face (Z=4): exterior surface, flush with enclosure Z=400
  Hopper lip extends from Z=4 to Z=7 around the opening
"""

import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

import cadquery as cq
from step_validate import Validator

# ============================================================================
# RUBRIC 2 — Coordinate System Declaration
# ============================================================================
# Origin: front-left corner of panel, bottom surface
# X: width [0, 220]
# Y: depth [0, 300]
# Z: thickness [0, 4] (panel body), lip extends to [4, 7]

# ============================================================================
# DIMENSIONS
# ============================================================================

# Panel body
PANEL_W = 220.0       # X
PANEL_D = 300.0       # Y
PANEL_T = 4.0         # Z (thickness)
CORNER_R = 6.0        # Plan-view corner radius (matches tub vertical edge radii)

# Hopper opening
HOPPER_DIA = 100.0
HOPPER_R = HOPPER_DIA / 2.0  # 50.0
HOPPER_CX = 110.0     # X center (centered in 220mm width)
HOPPER_CY = 70.0      # Y center (front-biased, per spatial layout hopper zone Y=8-78)

# Raised pour lip around hopper opening
LIP_HEIGHT = 3.0      # Above top surface (Z=4 to Z=7)
LIP_WIDTH = 3.0       # Radial width of lip annulus
LIP_INNER_R = HOPPER_R            # 50.0 (flush with opening)
LIP_OUTER_R = HOPPER_R + LIP_WIDTH  # 53.0

# Tongue-and-groove (panel has groove on underside, tub has tongue on rim)
# Tub tongue: 3mm wide, 2mm tall, centered in 4mm wall
# Panel groove: 3.2mm wide (0.1mm clearance/side), 2.5mm deep (0.5mm glue res.)
GROOVE_WIDTH = 3.2
GROOVE_DEPTH = 2.5
GROOVE_INSET = 2.0    # Distance from panel edge to groove center (= wall center)
# Groove runs on 3 sides: left, right, back. Not on front (butt joint with front panel).

# Steel disc pockets (for magnetic retention — tub has neodymium magnets)
DISC_DIA = 6.2        # 0.1mm clearance on 6mm steel disc
DISC_DEPTH = 3.0      # 3mm thick disc
DISC_CX_LEFT = 2.0    # X center = wall centerline (4mm wall / 2)
DISC_CX_RIGHT = 218.0
DISC_CY = 150.0       # Y = 150, per tub specification

# ============================================================================
# RUBRIC 1 — Feature Planning Table
# ============================================================================
print("=" * 80)
print("RUBRIC 1 — Feature Planning Table")
print("=" * 80)
features = [
    ("1",  "Panel body",             "Flat lid, structural",        "Add",  "RoundedRect", "Z",
     f"({PANEL_W/2}, {PANEL_D/2}, {PANEL_T/2})",
     f"{PANEL_W}x{PANEL_D}x{PANEL_T}mm, R={CORNER_R}mm corners"),
    ("2",  "Hopper opening",         "Pour hole for flavor",        "Rem",  "Cylinder",    "Z",
     f"({HOPPER_CX}, {HOPPER_CY}, 0-{PANEL_T})",
     f"{HOPPER_DIA}mm dia through"),
    ("3",  "Raised pour lip",        "Spill containment ring",      "Add",  "Annulus",     "Z",
     f"({HOPPER_CX}, {HOPPER_CY}, {PANEL_T}-{PANEL_T+LIP_HEIGHT})",
     f"ID={LIP_INNER_R*2}, OD={LIP_OUTER_R*2}, H={LIP_HEIGHT}"),
    ("4a", "Groove left side",       "Engages tub rim tongue",      "Rem",  "Box",         "Y",
     f"X={GROOVE_INSET}, Y=0-{PANEL_D}",
     f"{GROOVE_WIDTH}x{GROOVE_DEPTH}mm channel"),
    ("4b", "Groove right side",      "Engages tub rim tongue",      "Rem",  "Box",         "Y",
     f"X={PANEL_W - GROOVE_INSET}, Y=0-{PANEL_D}",
     f"{GROOVE_WIDTH}x{GROOVE_DEPTH}mm channel"),
    ("4c", "Groove back side",       "Engages tub rim tongue",      "Rem",  "Box",         "X",
     f"Y={PANEL_D - GROOVE_INSET}, X=0-{PANEL_W}",
     f"{GROOVE_WIDTH}x{GROOVE_DEPTH}mm channel"),
    ("5a", "Steel disc pocket left", "Magnetic retention (left)",   "Rem",  "Cylinder",    "Z",
     f"({DISC_CX_LEFT}, {DISC_CY})",
     f"{DISC_DIA}mm dia x {DISC_DEPTH}mm deep"),
    ("5b", "Steel disc pocket right","Magnetic retention (right)",  "Rem",  "Cylinder",    "Z",
     f"({DISC_CX_RIGHT}, {DISC_CY})",
     f"{DISC_DIA}mm dia x {DISC_DEPTH}mm deep"),
]
for row in features:
    num, name, func, op, shape, axis, pos, dims = row
    print(f"  {num:<4} {name:<28} {func:<30} {op:<5} {shape:<12} {axis:<5} {pos}")
    print(f"       Dims: {dims}")
print()
sys.stdout.flush()

# ============================================================================
# MODELING
# ============================================================================

# --- Feature 1: Panel body (rounded rectangle) ---
print("Building panel body...")
sys.stdout.flush()

# Create a rounded rectangle in XY plane, extrude in Z
# CadQuery box is centered by default; we want origin at corner, so centered=False
# But fillets on a non-centered box: build centered, fillet, then translate.
# Actually, easier: use sketch on XY plane.
panel = (
    cq.Workplane("XY")
    .rect(PANEL_W, PANEL_D)
    .extrude(PANEL_T)
)
# Fillet the four vertical edges (6mm corner radii in plan view)
panel = panel.edges("|Z").fillet(CORNER_R)
# The box is centered at origin. Translate so origin is at front-left-bottom corner.
panel = panel.translate((PANEL_W / 2, PANEL_D / 2, 0))
print("  Panel body built with 6mm corner radii.")

# --- Feature 2: Hopper opening (through-hole) ---
print("Cutting hopper opening...")
sys.stdout.flush()
hopper_hole = (
    cq.Workplane("XY")
    .center(HOPPER_CX, HOPPER_CY)
    .circle(HOPPER_R)
    .extrude(PANEL_T + LIP_HEIGHT + 1)  # Cut through full height including lip zone
)
panel = panel.cut(hopper_hole)
print(f"  {HOPPER_DIA}mm hopper opening cut at ({HOPPER_CX}, {HOPPER_CY}).")

# --- Feature 3: Raised pour lip ---
print("Building raised pour lip...")
sys.stdout.flush()
lip = (
    cq.Workplane("XY")
    .workplane(offset=PANEL_T)  # Start at top surface
    .center(HOPPER_CX, HOPPER_CY)
    .circle(LIP_OUTER_R)
    .circle(LIP_INNER_R)
    .extrude(LIP_HEIGHT)
)
panel = panel.union(lip)
print(f"  Lip added: R={LIP_INNER_R}-{LIP_OUTER_R}mm, H={LIP_HEIGHT}mm.")

# --- Feature 4: Tongue-and-groove channels (3 sides, bottom face) ---
# Each groove is a rectangular channel cut from the bottom face (Z=0 upward).
# Groove is centered at GROOVE_INSET from the panel edge, GROOVE_WIDTH wide, GROOVE_DEPTH deep.
print("Cutting tongue-and-groove channels...")
sys.stdout.flush()

# Left groove: runs full depth of panel at X = GROOVE_INSET
groove_left = (
    cq.Workplane("XY")
    .center(GROOVE_INSET, PANEL_D / 2)
    .rect(GROOVE_WIDTH, PANEL_D)
    .extrude(GROOVE_DEPTH)
)
panel = panel.cut(groove_left)

# Right groove: at X = PANEL_W - GROOVE_INSET
groove_right = (
    cq.Workplane("XY")
    .center(PANEL_W - GROOVE_INSET, PANEL_D / 2)
    .rect(GROOVE_WIDTH, PANEL_D)
    .extrude(GROOVE_DEPTH)
)
panel = panel.cut(groove_right)

# Back groove: at Y = PANEL_D - GROOVE_INSET, runs full width
groove_back = (
    cq.Workplane("XY")
    .center(PANEL_W / 2, PANEL_D - GROOVE_INSET)
    .rect(PANEL_W, GROOVE_WIDTH)
    .extrude(GROOVE_DEPTH)
)
panel = panel.cut(groove_back)
print("  3 groove channels cut (left, right, back).")

# --- Feature 5: Steel disc pockets (2x, bottom face) ---
print("Cutting steel disc pockets...")
sys.stdout.flush()

for label, cx in [("left", DISC_CX_LEFT), ("right", DISC_CX_RIGHT)]:
    pocket = (
        cq.Workplane("XY")
        .center(cx, DISC_CY)
        .circle(DISC_DIA / 2)
        .extrude(DISC_DEPTH)
    )
    panel = panel.cut(pocket)
    print(f"  {label} pocket: {DISC_DIA}mm dia x {DISC_DEPTH}mm at ({cx}, {DISC_CY})")

# ============================================================================
# EXPORT STEP FILE
# ============================================================================
output_path = Path(__file__).parent / "top-panel.step"
cq.exporters.export(panel, str(output_path))
print(f"\nSTEP file exported to: {output_path}")

# ============================================================================
# RUBRIC 3 — Feature-Specification Reconciliation (Point-in-Solid Probes)
# ============================================================================
print("\n" + "=" * 60)
print("RUBRIC 3 — Validation Probes")
print("=" * 60)

v = Validator(panel)

# --- Panel body ---
# Solid at center of panel
v.check_solid("Panel center", PANEL_W / 2, PANEL_D / 2, PANEL_T / 2,
              "solid at panel center")
# Solid near corners (inside 6mm radii)
v.check_solid("Panel near front-left", 10, 10, PANEL_T / 2,
              "solid near front-left corner (inside radius)")
v.check_solid("Panel near back-right", 210, 290, PANEL_T / 2,
              "solid near back-right corner (inside radius)")
# Void outside panel
v.check_void("Outside -X", -1, 150, 2, "void left of panel")
v.check_void("Outside +X", 221, 150, 2, "void right of panel")
v.check_void("Outside -Y", 110, -1, 2, "void in front of panel")
v.check_void("Outside +Y", 110, 301, 2, "void behind panel")
v.check_void("Outside -Z", 110, 150, -1, "void below panel")
v.check_void("Above panel (no lip)", 50, 150, PANEL_T + 1,
             "void above panel surface (away from lip)")

# Corner radii: at the very corner (0,0) should be void due to 6mm radius
v.check_void("Corner void front-left", 0.5, 0.5, 2,
             "void at rounded corner front-left")
v.check_void("Corner void front-right", 219.5, 0.5, 2,
             "void at rounded corner front-right")
v.check_void("Corner void back-left", 0.5, 299.5, 2,
             "void at rounded corner back-left")
v.check_void("Corner void back-right", 219.5, 299.5, 2,
             "void at rounded corner back-right")

# --- Hopper opening ---
v.check_void("Hopper center", HOPPER_CX, HOPPER_CY, PANEL_T / 2,
             "void at hopper center (through-hole)")
v.check_void("Hopper edge -X", HOPPER_CX - HOPPER_R + 2, HOPPER_CY, PANEL_T / 2,
             "void just inside hopper opening edge")
v.check_solid("Outside hopper +X", HOPPER_CX + HOPPER_R + 5, HOPPER_CY, PANEL_T / 2,
              "solid outside hopper opening")
v.check_solid("Outside hopper -Y", HOPPER_CX, HOPPER_CY - HOPPER_R - 5, PANEL_T / 2,
              "solid below hopper opening")

# --- Raised pour lip ---
v.check_solid("Lip top +X", HOPPER_CX + LIP_INNER_R + LIP_WIDTH / 2, HOPPER_CY,
              PANEL_T + LIP_HEIGHT / 2,
              "solid in lip wall")
v.check_solid("Lip top -Y", HOPPER_CX, HOPPER_CY - LIP_INNER_R - LIP_WIDTH / 2,
              PANEL_T + LIP_HEIGHT / 2,
              "solid in lip wall -Y side")
v.check_void("Inside lip (opening)", HOPPER_CX, HOPPER_CY,
             PANEL_T + LIP_HEIGHT / 2,
             "void inside lip (hopper opening extends through)")
v.check_void("Outside lip", HOPPER_CX + LIP_OUTER_R + 2, HOPPER_CY,
             PANEL_T + LIP_HEIGHT / 2,
             "void outside lip ring")
v.check_solid("Lip at top", HOPPER_CX + LIP_INNER_R + LIP_WIDTH / 2, HOPPER_CY,
              PANEL_T + LIP_HEIGHT - 0.5,
              "solid near lip top")
v.check_void("Above lip", HOPPER_CX + LIP_INNER_R + LIP_WIDTH / 2, HOPPER_CY,
             PANEL_T + LIP_HEIGHT + 1,
             "void above lip")

# --- Groove channels (bottom face) ---
# Left groove: at X=GROOVE_INSET, should be void from Z=0 to Z=GROOVE_DEPTH
v.check_void("Left groove center", GROOVE_INSET, 150, GROOVE_DEPTH / 2,
             "void in left groove channel")
v.check_void("Left groove near bottom", GROOVE_INSET, 150, 0.5,
             "void near bottom of left groove")
v.check_solid("Left groove above", GROOVE_INSET, 100, GROOVE_DEPTH + 0.5,
              "solid above left groove (remaining panel thickness)")
v.check_solid("Outside left groove", GROOVE_INSET + GROOVE_WIDTH, 150, 0.5,
              "solid outside left groove width")

# Right groove
v.check_void("Right groove center", PANEL_W - GROOVE_INSET, 150, GROOVE_DEPTH / 2,
             "void in right groove channel")
v.check_solid("Right groove above", PANEL_W - GROOVE_INSET, 100, GROOVE_DEPTH + 0.5,
              "solid above right groove")

# Back groove
v.check_void("Back groove center", PANEL_W / 2, PANEL_D - GROOVE_INSET, GROOVE_DEPTH / 2,
             "void in back groove channel")
v.check_solid("Back groove above", PANEL_W / 2, PANEL_D - GROOVE_INSET, GROOVE_DEPTH + 0.5,
              "solid above back groove")

# No groove on front edge (probe at panel center X, away from side grooves)
v.check_solid("No front groove", PANEL_W / 2, 1, 0.5,
              "solid at front edge bottom center (no groove here)")

# --- Steel disc pockets ---
v.check_void("Left disc pocket center", DISC_CX_LEFT, DISC_CY, DISC_DEPTH / 2,
             "void at left disc pocket center")
v.check_void("Left disc pocket near bottom", DISC_CX_LEFT, DISC_CY, 0.5,
             "void near bottom of left disc pocket")
v.check_solid("Left disc pocket above", DISC_CX_LEFT, DISC_CY, DISC_DEPTH + 0.5,
              "solid above left disc pocket (1mm remaining)")

v.check_void("Right disc pocket center", DISC_CX_RIGHT, DISC_CY, DISC_DEPTH / 2,
             "void at right disc pocket center")
v.check_solid("Right disc pocket above", DISC_CX_RIGHT, DISC_CY, DISC_DEPTH + 0.5,
              "solid above right disc pocket")

# ============================================================================
# RUBRIC 4 — Solid Validity
# ============================================================================
print("\n" + "=" * 60)
print("RUBRIC 4 — Solid Validity")
print("=" * 60)
v.check_valid()
v.check_single_body()

# Panel envelope volume (ignoring lip, corner radii, grooves)
envelope_vol = PANEL_W * PANEL_D * (PANEL_T + LIP_HEIGHT)
v.check_volume(expected_envelope=envelope_vol, fill_range=(0.15, 0.60))

# ============================================================================
# RUBRIC 5 — Bounding Box Reconciliation
# ============================================================================
print("\n" + "=" * 60)
print("RUBRIC 5 — Bounding Box")
print("=" * 60)
bb = panel.val().BoundingBox()
print(f"Actual BB: X[{bb.xmin:.2f}, {bb.xmax:.2f}] "
      f"Y[{bb.ymin:.2f}, {bb.ymax:.2f}] "
      f"Z[{bb.zmin:.2f}, {bb.zmax:.2f}]")

v.check_bbox("X", bb.xmin, bb.xmax, 0.0, PANEL_W, tol=1.0)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, PANEL_D, tol=1.0)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, PANEL_T + LIP_HEIGHT, tol=0.5)

# ============================================================================
# SUMMARY
# ============================================================================
if not v.summary():
    sys.exit(1)

print("\nDone.")
