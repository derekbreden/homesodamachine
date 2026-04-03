"""
Back Panel — CadQuery STEP Generation Script

Specification source: hardware/printed-parts/cartridge/back-panel/planning/parts.md

Flat panel 140.0mm (X) x 3.0mm (Y) x 79.0mm (Z) with 4 tube-stub through-holes.
Slides into the back-panel rail channels on the left and right walls.

Coordinate system (assembly frame):
  Origin: cartridge interior bottom-left-front corner (X=0, Y=0, Z=0)
  X: left-to-right across interior width, 0..140.0mm
  Y: front-to-back, 0..133.0mm; panel occupies Y=127.8..130.8mm
  Z: bottom-to-top, 0..79.0mm
  Envelope: 140.0mm (X) x 3.0mm (Y) x 79.0mm (Z)
            at X=0..140, Y=127.8..130.8, Z=0..79

Print orientation: front face (Y=127.8mm) down on build plate. Flat panel with
vertical through-holes — no overhangs, no supports required.
"""

import sys
from pathlib import Path

# Script is at: hardware/printed-parts/cartridge/back-panel/generate_step_cadquery.py
# parents[4] = project root
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq

# Dimensions (from parts.md)

# Panel body
PANEL_W = 170.0    # X — width (was 140.0)
PANEL_D = 3.0      # Y — thickness (channel portion)
PANEL_H = 103.6    # Z — height (was 79.0, matches interior plates)

# Extension dimensions
EDGE_W = 3.0       # X — width of left/right edges that sit in wall channels
EXT_DEPTH = 2.0    # Y — how far the middle extends beyond the channel edges

# Installed position in assembly frame
# Back panel rail channel: Y=127.6..131.0mm (3.4mm wide)
# Panel thickness 3.0mm: clearance = (3.4 - 3.0) / 2 = 0.2mm each side
PANEL_Y0 = 127.8   # front face Y position (127.6 + 0.2)
PANEL_Y1 = 130.8   # back face Y position  (127.8 + 3.0)

# Hole geometry — pass 9.57mm John Guest collet OD with 0.2mm loose-fit tolerance
HOLE_DIA = 7.00
HOLE_R   = HOLE_DIA / 2.0

# Coupler XZ centers (from coupler-tray boss half script, assembly frame)
# All 4 couplers at Z=34.3mm (the coupler tray split plane / coupler centers)
HOLES = [
    ("H1", 59.5, 34.3),
    ("H2", 76.5, 34.3),
    ("H3", 93.5, 34.3),
    ("H4", 110.5, 34.3),
]

MID_Y   = (PANEL_Y0 + PANEL_Y1) / 2.0   # 129.3mm — Y center of panel
OVERCUT = 0.1                             # small extension to ensure clean boolean cuts

# Build model

print("Building back panel model...")
print()

# Feature 1 — Panel body
# XY workplane box: X:[0,W] Y:[0,D] Z:[0,H] with centered=False
# Translated to panel Y position: Y=PANEL_Y0..PANEL_Y1, Z=0..PANEL_H, X=0..PANEL_W
print(f"Feature 1 — Panel body ({PANEL_W} x {PANEL_D} x {PANEL_H} mm, X x Y x Z)...")
print(f"  Placed at X=0..{PANEL_W}, Y={PANEL_Y0}..{PANEL_Y1}, Z=0..{PANEL_H}")

panel = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0.0, PANEL_Y0, 0.0))
    .box(PANEL_W, PANEL_D, PANEL_H, centered=False)
)
print("Panel body complete.")
print()

# Feature 1b — Middle extension: 2mm outward (+Y) beyond the main slab,
# excluding the 3mm left and right edges that sit in the wall channels.
# X: EDGE_W to PANEL_W - EDGE_W (3..167), full Z height, Y: PANEL_Y1..PANEL_Y1+EXT_DEPTH
print(f"Feature 1b — Middle extension (2mm outward, X={EDGE_W}..{PANEL_W - EDGE_W})...")
extension = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(EDGE_W, PANEL_Y1, 0.0))
    .box(PANEL_W - 2 * EDGE_W, EXT_DEPTH, PANEL_H, centered=False)
)
panel = panel.union(extension)
print(f"  Placed at X={EDGE_W}..{PANEL_W - EDGE_W}, Y={PANEL_Y1}..{PANEL_Y1 + EXT_DEPTH}, Z=0..{PANEL_H}")
print()

# Features 2-5 — Tube stub holes H1..H4
# Cylindrical through-holes, axis along Y, centered at (hx, MID_Y, hz)
# Drilled using XZ workplane centered at (hx, hz), extrude through full Y+overcut
print(f"Features 2-5 — 4x tube stub holes (dia={HOLE_DIA}mm, through Y={PANEL_Y0}..{PANEL_Y1})...")
# XZ workplane normal is -Y. workplane(offset=-N) places the workplane at Y=N.
# extrude(D) goes in the -Y direction, so the cylinder spans Y=(N - D) to Y=N.
# We need Y span = PANEL_Y0-OVERCUT to PANEL_Y1+OVERCUT.
# Set workplane at Y=PANEL_Y1+OVERCUT, extrude D=PANEL_D+2*OVERCUT → spans Y=PANEL_Y0-OVERCUT..PANEL_Y1+OVERCUT.
for i, (hid, hx, hz) in enumerate(HOLES, start=2):
    print(f"  Feature {i} — Hole {hid}: X={hx}, Z={hz}")
    FULL_D = PANEL_D + EXT_DEPTH                     # 5.0mm total through both slab and extension
    hole = (
        cq.Workplane("XZ")
        .workplane(offset=-(PANEL_Y1 + EXT_DEPTH + OVERCUT))  # workplane at Y = PANEL_Y1 + EXT_DEPTH + OVERCUT
        .center(hx, hz)
        .circle(HOLE_R)
        .extrude(FULL_D + 2 * OVERCUT)              # extrude in -Y; spans full panel thickness
    )
    panel = panel.cut(hole)
    print(f"    [-] Hole {hid} cut at (X={hx}, Z={hz}), dia={HOLE_DIA}mm")
print("Tube stub holes complete.")
print()

print()

# Export STEP file

OUTPUT_STEP = Path(__file__).resolve().parent / "back-panel-cadquery.step"
print(f"Exporting STEP file -> {OUTPUT_STEP}")
cq.exporters.export(panel, str(OUTPUT_STEP))
print()

print("RUBRIC 3 — Feature-Specification Reconciliation")
print()
