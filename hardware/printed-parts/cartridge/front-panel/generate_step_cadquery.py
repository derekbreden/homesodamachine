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

# Add tools/ to sys.path for step_validate
# Script is at: hardware/printed-parts/cartridge/front-panel/generate_step_cadquery.py
# parents[4] = project root
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))
from step_validate import Validator

import cadquery as cq

# ============================================================
# Rubric 1 — Feature Planning Table (MANDATORY, before coding)
# ============================================================

print()
print("=" * 90)
print("RUBRIC 1 — Feature Planning Table")
print("=" * 90)
print()

FEATURE_TABLE = [
    ("1", "Panel Body",
     "Rigid flat plate closing front face of cartridge; slides in wall front-panel rail channels",
     "Add", "Box", "Y", "(70.0, 1.5, 39.5)",
     "140.0W x 3.0D x 79.0H mm; X:[0,140] Y:[0,3] Z:[0,79]",
     "Base body; front face Y=0 flush with wall front edges"),

    ("2", "Finger Access Hole",
     "Through-hole allowing user fingers to reach lever pull surface (lever front face at Y=0)",
     "Remove", "Box", "Y", "(70.0, 1.5, 27.0)",
     "100.0W x 3.0D x 30.0H mm; X:[20,120] Y:[0,3] Z:[12,42]",
     "Center X=70 (on lever center), Z center=27 < 39.5 (lower half); Phase 8 will refine"),
]

col_w = [3, 24, 20, 8, 7, 5, 20, 38]
header = (f"{'#':<{col_w[0]}} {'Feature Name':<{col_w[1]}} {'Operation':<{col_w[3]}} "
          f"{'Shape':<{col_w[4]}} {'Axis':<{col_w[5]}} {'Center (X,Y,Z)':<{col_w[6]}} "
          f"{'Dimensions':<{col_w[7]}} Notes")
print(header)
print("-" * 140)
for row in FEATURE_TABLE:
    num, name, func, op, shape, axis, center, dims, notes = row
    print(f"{num:<{col_w[0]}} {name:<{col_w[1]}} {op:<{col_w[3]}} "
          f"{shape:<{col_w[4]}} {axis:<{col_w[5]}} {center:<{col_w[6]}} "
          f"{dims:<{col_w[7]}} {notes}")

print()

# ============================================================
# Rubric 2 — Coordinate System Declaration (MANDATORY, before coding)
# ============================================================

print("=" * 90)
print("RUBRIC 2 — Coordinate System Declaration")
print("=" * 90)
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

# ============================================================
# Geometry constants (from planning/parts.md)
# ============================================================

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

# ============================================================
# Feature 1 — Panel Body
# ============================================================
print("Building Feature 1: Panel Body ...")
panel = cq.Workplane("XY").box(PANEL_W, PANEL_D, PANEL_H, centered=False)

# ============================================================
# Feature 1b — Middle extension (2mm outward in -Y)
# ============================================================
print("Building Feature 1b: Middle extension ...")
extension = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(EDGE_W, -EXT_DEPTH, 0.0))
    .box(PANEL_W - 2 * EDGE_W, EXT_DEPTH, PANEL_H, centered=False)
)
panel = panel.union(extension)

# ============================================================
# Feature 2 — Finger Access Hole (through-hole along Y)
# ============================================================
print("Building Feature 2: Finger Access Hole ...")
# Cut through full thickness including extension
hole = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(HOLE_X0, -EXT_DEPTH, HOLE_Z0))
    .box(HOLE_W, PANEL_D + EXT_DEPTH, HOLE_H, centered=False)
)
panel = panel.cut(hole)

# ============================================================
# Export STEP file
# ============================================================
OUT_DIR = Path(__file__).parent
STEP_PATH = OUT_DIR / "front-panel-cadquery.step"
print(f"\nExporting STEP to: {STEP_PATH}")
cq.exporters.export(panel, str(STEP_PATH))
print("Export complete.")

# ============================================================
# Rubric 3 — Feature-Specification Reconciliation
# ============================================================

print()
print("=" * 90)
print("RUBRIC 3 — Feature-Specification Reconciliation")
print("=" * 90)
print()

v = Validator(panel)

# --- Feature 1: Panel Body ---
print("Feature 1: Panel Body")
# Center of panel
v.check_solid("Panel interior center",       85.0,  1.5, 60.0, "solid at panel center above hole")
# Near edges (solid portions outside hole)
v.check_solid("Panel left edge",              1.0,  1.5, 60.0, "solid near left edge")
v.check_solid("Panel right edge",           169.0,  1.5, 60.0, "solid near right edge")
v.check_solid("Panel front face interior",   85.0,  0.2, 60.0, "solid near front face above hole")
v.check_solid("Panel rear face interior",    85.0,  2.8, 60.0, "solid near rear face above hole")
v.check_solid("Panel top interior",          85.0,  1.5, 103.0, "solid near top edge")
v.check_solid("Panel bottom interior",       85.0,  1.5,  1.0, "solid near bottom edge")
# Extension probes
v.check_solid("Extension center",            85.0, -1.0, 60.0, "solid in middle extension")
v.check_void("Left edge no extension",        1.5, -1.0, 60.0, "void in front of left channel edge")
v.check_void("Right edge no extension",     168.5, -1.0, 60.0, "void in front of right channel edge")
# Void outside envelope
v.check_void("Void in front of panel",       85.0, -EXT_DEPTH - 0.5, 60.0, "void forward of front face extension")
v.check_void("Void behind panel",            85.0,  3.5, 60.0, "void behind back face")
v.check_void("Void above panel",             85.0,  1.5, 104.6, "void above top edge")
v.check_void("Void below panel",             85.0,  1.5, -1.0, "void below bottom edge")
v.check_void("Void left of panel",          -0.5,   1.5, 60.0, "void left of panel")
v.check_void("Void right of panel",         170.5,  1.5, 60.0, "void right of panel")

print()

# --- Feature 2: Finger Access Hole ---
print("Feature 2: Finger Access Hole")

# Hole spans X:[20,120], Y:[0,3], Z:[12,42]
HOLE_X_CENTER = HOLE_X0 + HOLE_W / 2   # 70.0
HOLE_Z_CENTER = HOLE_Z0 + HOLE_H / 2   # 27.0
HOLE_X1 = HOLE_X0 + HOLE_W             # 120.0
HOLE_Z1 = HOLE_Z0 + HOLE_H             # 42.0

# Center of hole — void
v.check_void("Hole center",             HOLE_X_CENTER, 1.5, HOLE_Z_CENTER,
             "void at hole center (X=70, Y=1.5, Z=27)")
# Front and rear faces of hole — void (through-hole)
v.check_void("Hole front face",         HOLE_X_CENTER, 0.1, HOLE_Z_CENTER,
             "void near front face through hole")
v.check_void("Hole rear face",          HOLE_X_CENTER, 2.9, HOLE_Z_CENTER,
             "void near rear face through hole")
# X extents of hole — void
v.check_void("Hole X+ side interior",   HOLE_X1 - 1.0, 1.5, HOLE_Z_CENTER,
             "void inside hole near X+ edge (X=119)")
v.check_void("Hole X- side interior",   HOLE_X0 + 1.0, 1.5, HOLE_Z_CENTER,
             "void inside hole near X- edge (X=21)")
# Z extents of hole — void
v.check_void("Hole Z+ side interior",   HOLE_X_CENTER, 1.5, HOLE_Z1 - 1.0,
             "void inside hole near Z+ edge (Z=41)")
v.check_void("Hole Z- side interior",   HOLE_X_CENTER, 1.5, HOLE_Z0 + 1.0,
             "void inside hole near Z- edge (Z=13)")

# Walls around hole — solid
# Left wall of hole (panel solid at X=15, Z=27)
v.check_solid("Panel solid left of hole",  30.0, 1.5, HOLE_Z_CENTER,
              "solid in panel left of finger hole (X=30)")
# Right wall of hole (panel solid at X=140, Z=27)
v.check_solid("Panel solid right of hole", 140.0, 1.5, HOLE_Z_CENTER,
              "solid in panel right of finger hole (X=140)")
# Below hole (panel solid at X=70, Z=6)
v.check_solid("Panel solid below hole",    HOLE_X_CENTER, 1.5, 6.0,
              "solid in panel below finger hole (Z=6)")
# Above hole (panel solid at X=70, Z=55)
v.check_solid("Panel solid above hole",    HOLE_X_CENTER, 1.5, 55.0,
              "solid in panel above finger hole (Z=55)")

# Hole boundary confirmation — just outside hole should be solid
v.check_solid("Panel solid just above hole top",  HOLE_X_CENTER, 1.5, HOLE_Z1 + 1.0,
              "solid just above hole top (Z=43)")
v.check_solid("Panel solid just below hole btm",  HOLE_X_CENTER, 1.5, HOLE_Z0 - 1.0,
              "solid just below hole bottom (Z=11)")
v.check_solid("Panel solid just left of hole",    HOLE_X0 - 1.0, 1.5, HOLE_Z_CENTER,
              "solid just left of hole left edge (X=19)")
v.check_solid("Panel solid just right of hole",   HOLE_X1 + 1.0, 1.5, HOLE_Z_CENTER,
              "solid just right of hole right edge (X=121)")

print()

# ============================================================
# Rubric 4 — Solid Validity
# ============================================================
print("=" * 90)
print("RUBRIC 4 — Solid Validity")
print("=" * 90)
print()

v.check_valid()
v.check_single_body()

# Volume estimate:
# Panel full: 140 x 3 x 79 = 33180 mm^3
# Hole: 100 x 3 x 30 = 9000 mm^3
# Net: 33180 - 9000 = 24180 mm^3
# Envelope: 140 x 3 x 79 = 33180 mm^3
# Fill ratio: 24180 / 33180 = 0.729
envelope_vol = PANEL_W * (PANEL_D + EXT_DEPTH) * PANEL_H
v.check_volume(expected_envelope=envelope_vol, fill_range=(0.50, 0.85))

print()

# ============================================================
# Rubric 5 — Bounding Box Reconciliation
# ============================================================
print("=" * 90)
print("RUBRIC 5 — Bounding Box Reconciliation")
print("=" * 90)
print()
print(f"Expected envelope: {PANEL_W}mm (X) x {PANEL_D}mm (Y) x {PANEL_H}mm (Z)")
print()

bb = panel.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, 0.0, PANEL_W)
v.check_bbox("Y", bb.ymin, bb.ymax, -EXT_DEPTH, PANEL_D)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, PANEL_H)

print()

# ============================================================
# Summary
# ============================================================
ok = v.summary()
if not ok:
    sys.exit(1)
else:
    print(f"\nSTEP file written to: {STEP_PATH}")
    sys.exit(0)
