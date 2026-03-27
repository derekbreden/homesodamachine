#!/usr/bin/env python3
"""
Wing Knob — CadQuery STEP Generation

PETG wing knob with internal female Tr12x3 2-start trapezoidal threads.
Mates with strut male threads. Wing extensions provide grip for twisting
and double as a pull handle for cartridge extraction.

Source material:
  - hardware/printed-parts/cartridge-twist-release/planning/parts.md
  - hardware/printed-parts/cartridge-twist-release/planning/research/3d-printed-approach.md
  - hardware/printed-parts/cartridge-twist-release/planning/research/decision.md
  - hardware/planning/step-generation-standards.md

Coordinate system:
  Origin: geometric center of the cylindrical body
  X: wing span direction (left wing -X, right wing +X)
  Y: bore/depth axis (rear face Y=-12.5, front face Y=+12.5)
     Rear face = strut entry side (bore entry, chamfered)
     Front face = user-facing grip side (filleted)
  Z: vertical
  Envelope: 70mm (X) x 25mm (Y) x 40mm (Z, body diameter)
  Body cylinder: R=20mm in XZ, 25mm along Y
  Wings: pill-shaped, 25mm tall (Z), extending to X=+/-35mm

Feature Planning Table (Rubric 1):
| # | Feature               | Function                        | Op     | Shape    | Axis | Center       | Dimensions                    |
|---|-----------------------|---------------------------------|--------|----------|------|--------------|-------------------------------|
| 1 | Cylindrical body      | Main body, houses bore          | Add    | Cylinder | Y    | (0,0,0)      | D=40, L=25                    |
| 2 | Left wing             | Grip + pull handle              | Add    | Stadium  | Y    | (-20,0,0)    | 30Lx25W(Z), 25D(Y)           |
| 3 | Right wing            | Grip + pull handle              | Add    | Stadium  | Y    | (+20,0,0)    | 30Lx25W(Z), 25D(Y)           |
| 4 | Female threaded bore  | Mates with strut Tr12x3 thread  | Remove | Helical  | Y    | (0,*,0)      | Minor D=12.6, 20mm engage    |
| 5 | Smooth clearance bore | Shaft passage above threads     | Remove | Cylinder | Y    | (0,front,0)  | D=12.6, L=4mm                |
| 6 | Entry chamfer         | Guides strut into bore          | Remove | Chamfer  | Y    | (0,rear,0)   | 1.0mm x 45deg                |
| 7 | Front face fillet     | Comfortable grip edge           | Modify | Fillet   | -    | front edges  | R=1.0mm                      |
"""

import math
import cadquery as cq
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from step_validate import Validator

# ============================================================
# PARAMETERS
# ============================================================

BODY_DIA = 40.0
BODY_R = BODY_DIA / 2        # 20mm
BODY_DEPTH = 25.0             # along Y axis

WING_TOTAL_SPAN = 70.0        # tip-to-tip in X
WING_EXTENSION = (WING_TOTAL_SPAN - BODY_DIA) / 2  # 15mm beyond body each side
WING_HEIGHT = 25.0             # Z extent of each wing (spec: same as body depth)

# Thread: Tr12x3 2-start
THREAD_NOMINAL_DIA = 12.0
THREAD_PITCH = 3.0             # per start
THREAD_STARTS = 2
THREAD_LEAD = THREAD_PITCH * THREAD_STARTS  # 6mm/rev
THREAD_CLEARANCE = 0.3         # radial
THREAD_DEPTH = 1.5             # groove depth

BORE_MINOR_DIA = THREAD_NOMINAL_DIA + 2 * THREAD_CLEARANCE  # 12.6mm
BORE_MINOR_R = BORE_MINOR_DIA / 2   # 6.3mm
BORE_MAJOR_R = BORE_MINOR_R + THREAD_DEPTH  # 7.8mm

THREAD_HALF_FLANK = 15.0       # degrees (30 deg total included)
THREAD_ENGAGEMENT = 20.0       # mm

ENTRY_CHAMFER = 1.0            # mm, 45 deg
FRONT_FILLET_R = 1.0           # mm

# Derived
REAR_Y = -BODY_DEPTH / 2      # -12.5
FRONT_Y = BODY_DEPTH / 2      # +12.5
SMOOTH_BORE_LEN = BODY_DEPTH - ENTRY_CHAMFER - THREAD_ENGAGEMENT  # 4mm
THREAD_Y_START = REAR_Y + ENTRY_CHAMFER  # -11.5
THREAD_Y_END = THREAD_Y_START + THREAD_ENGAGEMENT  # +8.5

# Thread groove profile widths
GROOVE_WIDTH_AT_BORE = THREAD_PITCH / 2  # 1.5mm
GROOVE_WIDTH_AT_DEPTH = GROOVE_WIDTH_AT_BORE - 2 * THREAD_DEPTH * math.tan(math.radians(THREAD_HALF_FLANK))
# = 1.5 - 0.804 = 0.696mm

# Wing pill dimensions for slot2D
# Each wing pill: 30mm long (X), 25mm wide (Z), centered at X=+/-20
WING_PILL_LENGTH = 30.0
WING_PILL_WIDTH = WING_HEIGHT  # 25mm
WING_PILL_CX = BODY_R         # 20mm

# ============================================================
# PRINT FEATURE TABLE
# ============================================================

print("=" * 70)
print("FEATURE PLANNING TABLE — Wing Knob")
print("=" * 70)
print(f"  1. Cylindrical body:   D={BODY_DIA}mm, depth={BODY_DEPTH}mm, centered at origin")
print(f"  2. Left wing:          extends to X=-{WING_TOTAL_SPAN/2:.0f}mm, pill shape {WING_PILL_LENGTH}x{WING_PILL_WIDTH}mm")
print(f"  3. Right wing:         extends to X=+{WING_TOTAL_SPAN/2:.0f}mm, pill shape")
print(f"  4. Threaded bore:      Tr12x3 2-start female, minor D={BORE_MINOR_DIA}mm, {THREAD_ENGAGEMENT}mm engage")
print(f"  5. Smooth bore:        D={BORE_MINOR_DIA}mm, {SMOOTH_BORE_LEN}mm from front face")
print(f"  6. Entry chamfer:      {ENTRY_CHAMFER}mm x 45deg at rear bore entry")
print(f"  7. Front face fillet:  R={FRONT_FILLET_R}mm")
print(f"  Body Z range:          [{-BODY_R}, {BODY_R}] (40mm dia)")
print(f"  Wing Z range:          [{-WING_HEIGHT/2}, {WING_HEIGHT/2}] (25mm tall)")
print(f"  Bore Y layout:         chamfer [{REAR_Y},{THREAD_Y_START}] thread [{THREAD_Y_START},{THREAD_Y_END}] smooth [{THREAD_Y_END},{FRONT_Y}]")
print("=" * 70)
print()

# ============================================================
# MODELING
# ============================================================

# --- Feature 1: Cylindrical body ---
# XZ workplane normal = -Y. offset=-FRONT_Y moves plane to Y=+12.5 (front face).
# extrude(BODY_DEPTH) goes -Y: from +12.5 to -12.5.
body = (
    cq.Workplane("XZ")
    .workplane(offset=-FRONT_Y)
    .circle(BODY_R)
    .extrude(BODY_DEPTH)
)

# --- Features 2 & 3: Wing extensions (pill-shaped) ---
# Each wing is a slot2D(30, 25) in XZ plane, extruded 25mm along Y.
# slot2D long axis along X (angle=0), width 25mm along Z.
# Centered at X=+/-20: spans X=5 to X=35 (right) or X=-35 to X=-5 (left).
# Z: -12.5 to +12.5 (wing height 25mm).
left_wing = (
    cq.Workplane("XZ")
    .workplane(offset=-FRONT_Y)
    .center(-WING_PILL_CX, 0)
    .slot2D(WING_PILL_LENGTH, WING_PILL_WIDTH, angle=0)
    .extrude(BODY_DEPTH)
)

right_wing = (
    cq.Workplane("XZ")
    .workplane(offset=-FRONT_Y)
    .center(WING_PILL_CX, 0)
    .slot2D(WING_PILL_LENGTH, WING_PILL_WIDTH, angle=0)
    .extrude(BODY_DEPTH)
)

knob = body.union(left_wing).union(right_wing)

# --- Features 4 & 5: Full bore (smooth + thread engagement zone) ---
# Cut a smooth bore through the entire body at minor diameter.
# Thread grooves will be cut additionally in the threaded zone.
smooth_bore = (
    cq.Workplane("XZ")
    .workplane(offset=-FRONT_Y)
    .circle(BORE_MINOR_R)
    .extrude(BODY_DEPTH)
)
knob = knob.cut(smooth_bore)

# --- Feature 6: Entry chamfer ---
# Revolved triangle at rear face: widens bore from BORE_MINOR_R to BORE_MINOR_R+1mm
chamfer_r_inner = BORE_MINOR_R
chamfer_r_outer = BORE_MINOR_R + ENTRY_CHAMFER

chamfer_profile_pts = [
    (chamfer_r_inner, REAR_Y),
    (chamfer_r_outer, REAR_Y),
    (chamfer_r_inner, REAR_Y + ENTRY_CHAMFER),
]

chamfer_solid = (
    cq.Workplane("XY")
    .polyline(chamfer_profile_pts)
    .close()
    .revolve(360, (0, 0, 0), (0, 1, 0))
)
knob = knob.cut(chamfer_solid)

# --- Feature 4: Thread grooves ---
# Circular ring groove approximation: for each start, revolve trapezoidal
# profile at correct pitch intervals. Not truly helical, but captures the
# correct geometry for printing validation.

hw_bore = GROOVE_WIDTH_AT_BORE / 2    # 0.75mm
hw_depth = GROOVE_WIDTH_AT_DEPTH / 2  # 0.348mm

print("Building thread grooves (ring approximation)...")
for start in range(THREAD_STARTS):
    start_offset = start * (THREAD_PITCH / THREAD_STARTS)  # 0 or 1.5mm
    y_pos = THREAD_Y_START + start_offset

    n_grooves = 0
    while y_pos <= THREAD_Y_END:
        # Trapezoidal groove profile revolved around Y axis
        # Profile in XY plane: X = radius, Y = axial position
        prof = [
            (BORE_MINOR_R, y_pos - hw_bore),
            (BORE_MAJOR_R, y_pos - hw_depth),
            (BORE_MAJOR_R, y_pos + hw_depth),
            (BORE_MINOR_R, y_pos + hw_bore),
        ]

        ring = (
            cq.Workplane("XY")
            .polyline(prof)
            .close()
            .revolve(360, (0, 0, 0), (0, 1, 0))
        )
        knob = knob.cut(ring)
        n_grooves += 1
        y_pos += THREAD_PITCH

    print(f"  Start {start + 1}: {n_grooves} groove rings")

print("  Thread grooves complete.")

# --- Feature 7: Front face fillet ---
try:
    knob = knob.edges(
        cq.selectors.NearestToPointSelector((0, FRONT_Y, 0))
    ).fillet(FRONT_FILLET_R)
    print("Front face fillet applied.")
except Exception as e:
    print(f"  WARNING: Fillet failed: {e}")
    print("  Skipping front face fillet — non-critical comfort feature.")

# ============================================================
# EXPORT STEP
# ============================================================

output_path = Path(__file__).parent / "wing-knob-cadquery.step"
cq.exporters.export(knob, str(output_path))
print(f"\nSTEP file written: {output_path}")

# ============================================================
# VALIDATION (Rubrics 3-5)
# ============================================================

print("\n" + "=" * 60)
print("VALIDATION")
print("=" * 60)

v = Validator(knob)

# --- Feature 1: Cylindrical body ---
# Origin is inside bore, so it's void. Probe body wall at R=15 from axis.
v.check_solid("Body wall +X", 15, 0, 0, "solid in body wall")
v.check_solid("Body wall -X", -15, 0, 0, "solid in body wall")
v.check_solid("Body wall +Z", 0, 0, 15, "solid in body wall above bore")
v.check_solid("Body wall -Z", 0, 0, -15, "solid in body wall below bore")
v.check_solid("Body near +Z edge", 0, 0, BODY_R - 1, "solid near body +Z surface")
v.check_solid("Body near -Z edge", 0, 0, -(BODY_R - 1), "solid near body -Z surface")
v.check_void("Outside body +Z", 0, 0, BODY_R + 2, "void above body")
v.check_void("Outside body -Z", 0, 0, -(BODY_R + 2), "void below body")
# Body should exist at Y extents
v.check_solid("Body rear face inside", 15, REAR_Y + 0.5, 0, "solid just inside rear face")
v.check_solid("Body front face inside", 15, FRONT_Y - 0.5, 0, "solid just inside front face")
v.check_void("Beyond rear face", 15, REAR_Y - 1, 0, "void beyond rear face")
v.check_void("Beyond front face", 15, FRONT_Y + 1, 0, "void beyond front face")

# --- Features 2 & 3: Wing extensions ---
# Wings: pill shape, X from +/-5 to +/-35, Z from -12.5 to +12.5
# Wing tips at X=+/-35 are semicircular with R=12.5 centered at X=+/-22.5
# So at X=-33 (inside tip semicircle), Z=0 should be solid
v.check_solid("Left wing tip", -33, 0, 0, "solid near left wing tip")
v.check_solid("Left wing mid", -(BODY_R + WING_EXTENSION/2), 0, 0, "solid at left wing middle")
v.check_void("Left wing beyond", -(WING_TOTAL_SPAN/2 + 2), 0, 0, "void beyond left wing")

v.check_solid("Right wing tip", 33, 0, 0, "solid near right wing tip")
v.check_solid("Right wing mid", (BODY_R + WING_EXTENSION/2), 0, 0, "solid at right wing middle")
v.check_void("Right wing beyond", (WING_TOTAL_SPAN/2 + 2), 0, 0, "void beyond right wing")

# Wings are 25mm tall (Z: -12.5 to +12.5), so at Z=+/-10 within wing should be solid
# At X=-27.5 (wing mid), Z=10 is within the 25mm wing height
v.check_solid("Left wing +Z inner", -27.5, 0, 10, "solid at wing upper region")
v.check_solid("Left wing -Z inner", -27.5, 0, -10, "solid at wing lower region")
# At Z=+/-13 (just outside 25mm wing height, inside body dia but outside wing)
# At X=-27.5 (outside body cylinder R=20), Z=13 is outside wing height -> void
v.check_void("Left wing above", -27.5, 0, 13.5, "void above wing at wing X position")
v.check_void("Left wing below", -27.5, 0, -13.5, "void below wing at wing X position")

# --- Feature 4: Threaded bore ---
v.check_void("Bore center origin", 0, 0, 0, "void at bore center (origin)")
v.check_void("Bore center rear", 0, REAR_Y + 2, 0, "void at bore center near rear")
v.check_void("Bore center front", 0, FRONT_Y - 2, 0, "void at bore center near front")
v.check_void("Bore at R=5", 5, 0, 0, "void inside bore at R=5")
v.check_void("Bore at minor-0.5", BORE_MINOR_R - 0.5, 0, 0, "void inside bore near wall")
# Beyond thread groove depth, body wall should be solid
v.check_solid("Wall beyond grooves", BORE_MAJOR_R + 1, 0, 0, "solid beyond thread groove depth")

# Thread groove existence: at a groove center Y position, probe at mid-groove radius
# First groove of start 1 is at Y = THREAD_Y_START = -11.5
groove_y = THREAD_Y_START
groove_mid_r = (BORE_MINOR_R + BORE_MAJOR_R) / 2  # 7.05mm
v.check_void("Thread groove center", groove_mid_r, groove_y, 0,
             "void at mid-radius of first thread groove")
# Between grooves (at tooth center), same radius should be solid
# Tooth center of start 1 is at Y = THREAD_Y_START + THREAD_PITCH/2 = -10.0
# But start 2 groove is at Y = THREAD_Y_START + 1.5 = -10.0 ... so -10.0 is also a groove
# Tooth center between start 1 grooves: Y = THREAD_Y_START + THREAD_PITCH/4 = -10.75
tooth_y = THREAD_Y_START + THREAD_PITCH * 0.25  # -10.75, between grooves
v.check_solid("Thread tooth", groove_mid_r, tooth_y, 0,
              "solid at thread tooth between grooves")

# --- Feature 5: Smooth clearance bore ---
smooth_y = FRONT_Y - 2  # Y = 10.5
v.check_void("Smooth bore center", 0, smooth_y, 0, "void at smooth bore center")
v.check_void("Smooth bore inner", BORE_MINOR_R - 1, smooth_y, 0, "void inside smooth bore")
# In smooth zone, no thread grooves — solid just outside minor radius
v.check_solid("Smooth bore wall", BORE_MINOR_R + 0.5, smooth_y, 0,
              "solid outside smooth bore (no grooves)")

# --- Feature 6: Entry chamfer ---
# At rear face + 0.3mm depth, bore is widened by chamfer
# Chamfer is 45deg so at 0.3mm depth, radius = BORE_MINOR_R + 0.7mm
v.check_void("Chamfer void", BORE_MINOR_R + 0.3, REAR_Y + 0.3, 0,
             "void in chamfer zone")
# Past chamfer (Y > THREAD_Y_START), at R = BORE_MINOR_R + 0.5:
# This is inside the thread groove zone so it depends on groove position.
# Probe at a tooth position past the chamfer
past_chamfer_y = THREAD_Y_START + THREAD_PITCH * 0.25  # at a tooth
v.check_solid("Past chamfer at tooth", BORE_MINOR_R + 0.3, past_chamfer_y, 0,
              "solid past chamfer at thread tooth position")

# --- Rubric 4: Solid validity ---
v.check_valid()
v.check_single_body()

# Expected envelope: 70mm (X) x 25mm (Y) x 40mm (Z)
ENVELOPE_X = WING_TOTAL_SPAN  # 70
ENVELOPE_Y = BODY_DEPTH       # 25
ENVELOPE_Z = BODY_DIA         # 40 (cylinder diameter)
v.check_volume(expected_envelope=ENVELOPE_X * ENVELOPE_Y * ENVELOPE_Z, fill_range=(0.15, 0.8))

# --- Rubric 5: Bounding box ---
bb = knob.val().BoundingBox()
print(f"\nActual bounding box: X[{bb.xmin:.2f}, {bb.xmax:.2f}] Y[{bb.ymin:.2f}, {bb.ymax:.2f}] Z[{bb.zmin:.2f}, {bb.zmax:.2f}]")

v.check_bbox("X", bb.xmin, bb.xmax, -WING_TOTAL_SPAN/2, WING_TOTAL_SPAN/2, tol=1.0)
v.check_bbox("Y", bb.ymin, bb.ymax, REAR_Y, FRONT_Y, tol=1.0)
v.check_bbox("Z", bb.zmin, bb.zmax, -BODY_R, BODY_R, tol=1.0)

# --- Summary ---
if not v.summary():
    sys.exit(1)
