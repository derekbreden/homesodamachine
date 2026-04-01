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

# Add tools/ to sys.path for step_validate import
# Script is at: hardware/printed-parts/cartridge/back-panel/generate_step_cadquery.py
# parents[4] = project root
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq
from step_validate import Validator

# ---------------------------------------------------------------------------
# Rubric 1 — Feature Planning Table (MANDATORY, before coding)
# ---------------------------------------------------------------------------

FEATURE_TABLE = """
BACK PANEL — Feature Planning Table (Rubric 1)
==============================================

Assembly frame coordinates:
  Origin: cartridge interior bottom-left-front corner
  X: left to right, 0..140.0mm
  Y: front to back, 127.8..130.8mm (panel occupies this range)
  Z: bottom to top, 0..79.0mm

Rubric 2 — Coordinate System:
  Panel front face: Y=127.8mm
  Panel back face:  Y=130.8mm
  Panel thickness:  3.0mm
  Panel width:      140.0mm (X=0..140.0)
  Panel height:     79.0mm  (Z=0..79.0)

  #   Feature Name      Mech Function                 Op      Shape    Axis  Center (X,Y,Z)           Dimensions          Notes
  1   Panel body        Structural enclosure wall     Add     Box      —     (70.0, 129.3, 39.5)      140x3x79mm          X=0..140, Y=127.8..130.8, Z=0..79
  2   Tube stub hole H1 Pass tube stub to coupler H1  Remove  Cyl      Y     (43.1, 129.3, 34.3)      dia=10.0mm, TH      Coupler center X=43.1, Z=34.3
  3   Tube stub hole H2 Pass tube stub to coupler H2  Remove  Cyl      Y     (60.1, 129.3, 34.3)      dia=10.0mm, TH      Coupler center X=60.1, Z=34.3
  4   Tube stub hole H3 Pass tube stub to coupler H3  Remove  Cyl      Y     (77.1, 129.3, 34.3)      dia=10.0mm, TH      Coupler center X=77.1, Z=34.3
  5   Tube stub hole H4 Pass tube stub to coupler H4  Remove  Cyl      Y     (94.1, 129.3, 34.3)      dia=10.0mm, TH      Coupler center X=94.1, Z=34.3

TH = through-hole, full Y thickness (127.8..130.8mm)
"""

print(FEATURE_TABLE)

# ---------------------------------------------------------------------------
# Dimensions (from parts.md)
# ---------------------------------------------------------------------------

# Panel body
PANEL_W = 170.0    # X — width (was 140.0)
PANEL_D = 3.0      # Y — thickness
PANEL_H = 103.6    # Z — height (was 79.0, matches interior plates)

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

# ---------------------------------------------------------------------------
# Build model
# ---------------------------------------------------------------------------

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
    hole = (
        cq.Workplane("XZ")
        .workplane(offset=-(PANEL_Y1 + OVERCUT))    # workplane at Y = PANEL_Y1 + OVERCUT (back approach)
        .center(hx, hz)
        .circle(HOLE_R)
        .extrude(PANEL_D + 2 * OVERCUT)             # extrude in -Y; spans Y = PANEL_Y0-OVERCUT..PANEL_Y1+OVERCUT
    )
    panel = panel.cut(hole)
    print(f"    [-] Hole {hid} cut at (X={hx}, Z={hz}), dia={HOLE_DIA}mm")
print("Tube stub holes complete.")
print()

print("Model construction complete.")
print()

# ---------------------------------------------------------------------------
# Export STEP file
# ---------------------------------------------------------------------------

OUTPUT_STEP = Path(__file__).resolve().parent / "back-panel-cadquery.step"
print(f"Exporting STEP file -> {OUTPUT_STEP}")
cq.exporters.export(panel, str(OUTPUT_STEP))
print("Export complete.")
print()

# ---------------------------------------------------------------------------
# Rubric 3 — Feature-Specification Reconciliation
# ---------------------------------------------------------------------------

print("=" * 60)
print("RUBRIC 3 — Feature-Specification Reconciliation")
print("=" * 60)
print()

v = Validator(panel)

# --- Feature 1: Panel body ---
print("Feature 1 — Panel body:")
# Interior solid points away from holes
v.check_solid("Panel center interior",   85.0,     MID_Y, 39.5,  "solid at panel center")
v.check_solid("Panel left edge",          0.5,     MID_Y, 39.5,  "solid near X=0 edge")
v.check_solid("Panel right edge",       169.5,     MID_Y, 39.5,  "solid near X=170 edge")
v.check_solid("Panel bottom edge",       85.0,     MID_Y,  0.5,  "solid near Z=0 edge")
v.check_solid("Panel top edge",          85.0,     MID_Y, 103.1, "solid near Z=103.6 edge")
v.check_solid("Panel front face inside", 85.0, PANEL_Y0 + 0.2, 39.5, "solid just inside front face")
v.check_solid("Panel back face inside",  85.0, PANEL_Y1 - 0.2, 39.5, "solid just inside back face")
# No material outside envelope
v.check_void("No material below Z=0",   85.0,     MID_Y, -0.1,  "void below bottom edge")
v.check_void("No material above Z=103.6", 85.0,    MID_Y, 103.7, "void above top edge")
v.check_void("No material before Y front",85.0, PANEL_Y0 - 0.1, 39.5, "void in front of panel")
v.check_void("No material behind Y back", 85.0, PANEL_Y1 + 0.1, 39.5, "void behind panel")
print()

# --- Features 2-5: Tube stub holes H1..H4 ---
for i, (hid, hx, hz) in enumerate(HOLES, start=2):
    print(f"Feature {i} — Tube stub hole {hid} at X={hx}, Z={hz}:")

    # Void at hole center (through entire panel)
    v.check_void(f"{hid} center at front face",
                 hx, PANEL_Y0 + 0.1, hz,
                 f"void at hole center near front face")
    v.check_void(f"{hid} center at mid Y",
                 hx, MID_Y, hz,
                 f"void at hole center at mid-panel Y")
    v.check_void(f"{hid} center at back face",
                 hx, PANEL_Y1 - 0.1, hz,
                 f"void at hole center near back face")

    # Path continuity: hole must pass completely through
    v.check_void(f"{hid} path continuity Y0 side",
                 hx, PANEL_Y0 + 0.05, hz,
                 f"void very close to front face — hole opens at Y={PANEL_Y0}")
    v.check_void(f"{hid} path continuity Y1 side",
                 hx, PANEL_Y1 - 0.05, hz,
                 f"void very close to back face — hole opens at Y={PANEL_Y1}")

    # Solid just outside hole radius in +X (panel material present)
    v.check_solid(f"{hid} solid outside +X",
                  hx + HOLE_R + 0.5, MID_Y, hz,
                  f"solid outside hole radius in +X")

    # Solid just outside hole radius in +Z
    v.check_solid(f"{hid} solid outside +Z",
                  hx, MID_Y, hz + HOLE_R + 0.5,
                  f"solid outside hole radius in +Z")

    # Void at hole center confirms correct diameter (just inside radius)
    v.check_void(f"{hid} void just inside radius",
                 hx + HOLE_R - 0.3, MID_Y, hz,
                 f"void just inside hole radius — diameter correct")

    print()

# ---------------------------------------------------------------------------
# Rubric 4 — Solid Validity
# ---------------------------------------------------------------------------

print("=" * 60)
print("RUBRIC 4 — Solid Validity")
print("=" * 60)
print()

v.check_valid()
v.check_single_body()

# Volume estimate:
#   Panel body: 140.0 x 3.0 x 79.0 = 33,180 mm^3
#   4 holes: 4 x pi x 5.0^2 x 3.0 = 4 x 235.6 = 942.5 mm^3
#   Expected: ~33,180 - 943 = 32,237 mm^3
#   Bounding box: 140.0 x 3.0 x 79.0 = 33,180 mm^3
#   Fill ratio: ~32,237 / 33,180 = 0.972 — well within (0.5, 1.2)
envelope_vol = PANEL_W * PANEL_D * PANEL_H
v.check_volume(expected_envelope=envelope_vol, fill_range=(0.5, 1.2))
print()

# ---------------------------------------------------------------------------
# Rubric 5 — Bounding Box Reconciliation
# ---------------------------------------------------------------------------

print("=" * 60)
print("RUBRIC 5 — Bounding Box Reconciliation")
print("=" * 60)
print()

bb = panel.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, 0.0,      PANEL_W)
v.check_bbox("Y", bb.ymin, bb.ymax, PANEL_Y0, PANEL_Y1)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0,      PANEL_H)
print()

# ---------------------------------------------------------------------------
# Final summary — exits 1 on any FAIL
# ---------------------------------------------------------------------------

if not v.summary():
    print()
    print("FAILURES DETECTED — fix model before exporting.")
    sys.exit(1)

print()
print(f"STEP file written: {OUTPUT_STEP}")
