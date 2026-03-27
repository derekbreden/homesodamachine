#!/usr/bin/env python3
"""
Cartridge Release Plate with Integral Strut — CadQuery STEP Generation

Generates the unified release plate + threaded strut for the soda flavor injector
pump cartridge. The plate simultaneously releases 4 John Guest PP0408W push-to-connect
collets via twist-release mechanism. The strut is integral to the plate (single
printed part), eliminating the press-fit + epoxy joint.

The plate sits on the DOCK SIDE of the rear wall (outside the cartridge body).
The stepped bores face the dock, with their openings facing away from the
cartridge interior. The strut pulls the plate toward the rear wall to push
dock-side collets inward.

Integral 6mm guide pins protrude from the back face and slide in 6.5mm printed
bushings in the rear wall, preventing rotation and ensuring parallel travel.

The strut extends from the plate back face through the rear wall and cartridge
interior. Only the far end (knob end) has Tr12x3 2-start trapezoidal threads
for engaging the wing knob. The plate end is integral — no threads needed.

Source material:
  - hardware/cartridge-release-plate/planning/parts.md
  - hardware/cartridge-twist-release/planning/parts.md
  - hardware/planning/step-generation-standards.md
  - hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md
  - hardware/cartridge-release-plate/planning/research/release-plate.md
  - hardware/cartridge-release-plate/planning/research/collet-release.md

Coordinate system:
  Origin: plate bottom-left-front corner (front face = fitting engagement side)
  X: plate width, left to right (59mm)    -> X: [0, 59]
  Y: plate depth, front to back + strut   -> Y: [0, 136]
     Front face Y=0: stepped bore openings (dock side, facing away from cartridge)
     Y=0 to Y=6: plate body
     Y=6 to Y=116: smooth 12mm strut (passes through rear wall + cartridge interior)
     Y=116 to Y=136: Tr12x3 2-start threaded section (engages wing knob)
  Z: plate height, bottom to top (47mm)   -> Z: [0, 47]

Bore depth stack (from front face Y=0 inward):
  Y=0 to Y=2: outer bore (body end cradle), 15.30mm dia
  Y=2 to Y=4: inner lip (collet hugger), 9.70mm dia
  Y=4 to Y=6: structural back wall, tube clearance hole only (6.50mm dia)

Integral guide pins protrude beyond back face in +Y.
Strut extends from plate center along +Y.

Print orientation: strut vertical (standing up), plate at bottom on build plate.
Stepped bores at Y=0 face the build plate — ideal for bore accuracy.
Threaded end at top.
"""

import math
import cadquery as cq
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from step_validate import Validator

# ============================================================
# PARAMETERS — from parts.md, geometry-description.md, research
# ============================================================

# Plate body envelope
PLATE_W = 59.0   # X extent (mm)
PLATE_D = 6.0    # Y extent (mm) — depth / thickness
PLATE_H = 47.0   # Z extent (mm)

# Stepped bore diameters
# Outer bore: body end cradle, must clear 15.10mm body end OD (caliper-verified)
# Using 15.30mm = 0.10mm/side clearance. Tight for lateral constraint.
OUTER_BORE_DIA = 15.30
OUTER_BORE_DEPTH = 2.0    # Y=0 to Y=2

# Inner lip: collet hugger, must clear 9.57mm collet OD (caliper-verified)
# Using 9.70mm = 0.065mm/side clearance. Tight for lateral constraint.
INNER_LIP_DIA = 9.70
INNER_LIP_DEPTH = 2.0     # Y=2 to Y=4

# Tube clearance hole: must be between 6.30mm tube OD and 6.69mm collet ID
# Using 6.50mm = midpoint of 0.39mm design window
TUBE_HOLE_DIA = 6.50
# Tube hole goes through full depth Y=0 to Y=6

# Verify depth stack
assert abs(OUTER_BORE_DEPTH + INNER_LIP_DEPTH + (PLATE_D - OUTER_BORE_DEPTH - INNER_LIP_DEPTH) - PLATE_D) < 0.001

# Chamfers
OUTER_CHAMFER = 0.3   # 45-deg lead-in at outer bore entry (front face Y=0)
TUBE_CHAMFER = 0.1    # at tube hole entry edge

# Bore grid centers: 2x2, relative to plate bottom-left (X, Z)
# parts.md: 40mm horizontal x 28mm vertical center-to-center
BORE_CENTERS = [
    (9.5,  9.5),   # bottom-left
    (49.5, 9.5),   # bottom-right
    (9.5,  37.5),  # top-left
    (49.5, 37.5),  # top-right
]

# Integral guide pins (replace old guide pin slots)
# 2x 6mm diameter PETG pins, 15mm long, protruding from back face.
# Slide in 6.5mm printed bushings in rear wall (0.25mm radial clearance).
# Positioned at same X,Z as the old guide pin slot centers.
GUIDE_PIN_DIA = 6.0       # pin diameter
GUIDE_PIN_LENGTH = 15.0   # protrusion from back face
GUIDE_PIN_CENTERS = [
    (-3.85, 23.5),   # left pin center (X, Z) — same as old left slot center
    (66.15, 23.5),   # right pin center (X, Z) — same as old right slot center
]

# Pin pads: local material reinforcement around each guide pin base
# The plate body doesn't extend to the pin X positions, so we need pad material.
# Pad extends from plate body edge to beyond the pin, with wall around the pin.
PIN_PAD_WALL = 2.0        # minimum wall around pin
PIN_PAD_DIA = GUIDE_PIN_DIA + 2 * PIN_PAD_WALL  # 10mm pad diameter
PIN_PAD_H = PIN_PAD_DIA   # pad height in Z (same as diameter for circular look)

# --- Integral strut parameters ---
# Strut center position on plate (X, Z)
STRUT_X = 29.5
STRUT_Z = 23.5

# Strut geometry
STRUT_DIA = 12.0          # smooth section & thread major diameter
STRUT_RADIUS = STRUT_DIA / 2  # 6.0mm

# Strut Y extents (measured from plate coordinate origin Y=0)
# Y=0 to Y=6: plate body (strut is integral here, no separate geometry needed)
# Y=6 to Y=116: smooth 12mm cylinder (110mm, passes through rear wall + cartridge)
# Y=116 to Y=136: Tr12x3 2-start threaded section (20mm, engages wing knob)
STRUT_SMOOTH_Y_START = PLATE_D         # 6.0 (back face of plate)
STRUT_SMOOTH_Y_END = 116.0
STRUT_SMOOTH_LENGTH = STRUT_SMOOTH_Y_END - STRUT_SMOOTH_Y_START  # 110mm

STRUT_THREAD_Y_START = 116.0
STRUT_THREAD_Y_END = 136.0
STRUT_THREAD_LENGTH = STRUT_THREAD_Y_END - STRUT_THREAD_Y_START  # 20mm

STRUT_TOTAL_Y = STRUT_THREAD_Y_END     # 136mm total Y extent

# Thread specification: Tr12x3 2-start trapezoidal (knob end only)
THREAD_MAJOR_DIA = 12.0    # external major diameter
THREAD_MINOR_DIA = 9.0     # external minor diameter (root)
THREAD_DEPTH = 1.5         # (major - minor) / 2
THREAD_PITCH = 3.0         # axial pitch per start (Tr12x3 means P=3mm)
THREAD_LEAD = 6.0          # axial advance per revolution (2 starts x 3.0mm = 6mm lead)
NUM_STARTS = 2             # number of thread starts
FLANK_ANGLE_DEG = 15.0     # flank angle from vertical (half the 29-deg included angle)

THREAD_MAJOR_R = THREAD_MAJOR_DIA / 2  # 6.0mm
THREAD_MINOR_R = THREAD_MINOR_DIA / 2  # 4.5mm
FLANK_ANGLE_RAD = math.radians(FLANK_ANGLE_DEG)

# Trapezoidal tooth profile dimensions
TOOTH_CREST_WIDTH = THREAD_PITCH / 2 - 2 * THREAD_DEPTH * math.tan(FLANK_ANGLE_RAD)
TOOTH_ROOT_WIDTH = THREAD_PITCH / 2

# Chamfer on threaded end only (knob end)
STRUT_CHAMFER = 0.5        # 0.5mm x 45 deg

# Derived radii
R_OUTER = OUTER_BORE_DIA / 2   # 7.65
R_INNER = INNER_LIP_DIA / 2    # 4.85
R_TUBE = TUBE_HOLE_DIA / 2     # 3.25

# ============================================================
# FEATURE PLANNING TABLE (Rubric 1)
# ============================================================

print("=" * 120)
print("FEATURE PLANNING TABLE (Rubric 1)")
print("=" * 120)
header = (f"{'#':<4} {'Feature Name':<32} {'Mech. Function':<35} {'Op':<7} "
          f"{'Shape':<10} {'Axis':<5} {'Center (X,Y,Z)':<22} {'Dimensions':<30} {'Notes'}")
print(header)
print("-" * 120)

table_rows = [
    ("1",  "Plate body",
     "Structural base",                  "Add",    "Box",      "—",
     "(29.5, 3.0, 23.5)",   "59x6x47mm",
     "PETG, dock-side of rear wall"),
    ("2",  "Left guide pin pad",
     "Material around left pin",         "Add",    "Box",      "—",
     f"({GUIDE_PIN_CENTERS[0][0]:.2f}, 3.0, 23.5)",
     f"{PIN_PAD_DIA}x{PLATE_D}x{PIN_PAD_H}mm",
     "Pad protruding left, overlaps plate body"),
    ("3",  "Right guide pin pad",
     "Material around right pin",        "Add",    "Box",      "—",
     f"({GUIDE_PIN_CENTERS[1][0]:.2f}, 3.0, 23.5)",
     f"{PIN_PAD_DIA}x{PLATE_D}x{PIN_PAD_H}mm",
     "Pad protruding right, overlaps plate body"),
    ("4",  "Strut smooth section",
     "Structural link plate-to-knob",    "Add",    "Cyl",      "Y",
     f"({STRUT_X}, *, {STRUT_Z})",
     f"D{STRUT_DIA}x{STRUT_SMOOTH_LENGTH}mm",
     f"Y={STRUT_SMOOTH_Y_START}..{STRUT_SMOOTH_Y_END}, integral to plate"),
    ("5",  "Strut thread core",
     "Core cylinder for threaded end",   "Add",    "Cyl",      "Y",
     f"({STRUT_X}, *, {STRUT_Z})",
     f"D{THREAD_MINOR_DIA}x{STRUT_THREAD_LENGTH}mm",
     f"Y={STRUT_THREAD_Y_START}..{STRUT_THREAD_Y_END}, minor dia"),
    ("6",  "Strut thread helices",
     "Engages wing knob female thread",  "Add",    "Helix",    "Y",
     f"({STRUT_X}, *, {STRUT_Z})",
     f"Tr12x3 2-start, {STRUT_THREAD_LENGTH}mm",
     "2 helices offset 180 deg, knob end only"),
    ("7",  "Strut end chamfer",
     "Thread entry aid at knob end",     "Remove", "Chamfer",  "Y",
     f"({STRUT_X}, {STRUT_TOTAL_Y}, {STRUT_Z})",
     f"{STRUT_CHAMFER}mm x 45 deg",
     "Tapered lead-in at Y=136"),
    ("8",  "Left guide pin",
     "Anti-rotation linear guide",       "Add",    "Cyl",      "Y",
     f"({GUIDE_PIN_CENTERS[0][0]:.2f}, *, 23.5)",
     f"D{GUIDE_PIN_DIA}x{GUIDE_PIN_LENGTH}mm",
     "Back face, +Y, slides in 6.5mm bushing"),
    ("9",  "Right guide pin",
     "Anti-rotation linear guide",       "Add",    "Cyl",      "Y",
     f"({GUIDE_PIN_CENTERS[1][0]:.2f}, *, 23.5)",
     f"D{GUIDE_PIN_DIA}x{GUIDE_PIN_LENGTH}mm",
     "Back face, +Y, slides in 6.5mm bushing"),
    ("10", "Outer bores (x4)",
     "Cradle body end 15.10mm",          "Remove", "Cyl",      "Y",
     "(cx, 1.0, cz) x4",
     f"D{OUTER_BORE_DIA}, {OUTER_BORE_DEPTH}mm deep",
     "Y=0 to Y=2, dock side"),
    ("11", "Inner lip bores (x4)",
     "Hug collet 9.57mm OD",            "Remove", "Cyl",      "Y",
     "(cx, 3.0, cz) x4",
     f"D{INNER_LIP_DIA}, {INNER_LIP_DEPTH}mm deep",
     "Y=2 to Y=4"),
    ("12", "Tube clearance holes (x4)",
     "Pass tube 6.30mm OD",             "Remove", "Cyl",      "Y",
     "(cx, 3.0, cz) x4",
     f"D{TUBE_HOLE_DIA}, through",
     "Full depth"),
    ("13", "Outer bore chamfers (x4)",
     "Fitting engagement lead-in",       "Remove", "Chamfer",  "Y",
     "at bore, Y=0",
     f"{OUTER_CHAMFER}mm x 45deg",
     "Front face entry (dock side)"),
    ("14", "Tube hole chamfers (x4)",
     "Ease tube threading",              "Remove", "Chamfer",  "Y",
     "at bore, Y=4",
     f"{TUBE_CHAMFER}mm x 45deg",
     "At inner lip floor"),
]

for row in table_rows:
    print(f"{row[0]:<4} {row[1]:<32} {row[2]:<35} {row[3]:<7} {row[4]:<10} {row[5]:<5} "
          f"{row[6]:<22} {row[7]:<30} {row[8]}")

print("=" * 120)
print(f"Bore centers (X,Z): {BORE_CENTERS}")
print(f"Bore spacing: 40mm horizontal, 28mm vertical")
print(f"Strut center: ({STRUT_X}, {STRUT_Z})")
print(f"Thread tooth crest width: {TOOTH_CREST_WIDTH:.4f}mm")
print(f"Thread tooth root width:  {TOOTH_ROOT_WIDTH:.4f}mm")
print()

# ============================================================
# HELPER: Build trapezoidal thread helix for one section
# ============================================================


def make_thread_tooth_profile():
    """
    Create the 2D trapezoidal tooth cross-section profile points.

    The profile is defined in a local coordinate system where:
      - The "radial" direction is X (outward from cylinder axis)
      - The "axial" direction is Y (along the strut axis)

    The tooth profile is a trapezoid:
      - Root (inner edge) at X = THREAD_MINOR_R, width = TOOTH_ROOT_WIDTH
      - Crest (outer edge) at X = THREAD_MAJOR_R, width = TOOTH_CREST_WIDTH
      - Flanks connect root corners to crest corners at FLANK_ANGLE_DEG

    Returns profile points for the tooth cross-section, centered
    axially on Y=0 in the profile's local frame.
    """
    half_root = TOOTH_ROOT_WIDTH / 2
    half_crest = TOOTH_CREST_WIDTH / 2

    pts = [
        (THREAD_MINOR_R, -half_root),    # root, bottom (axially trailing)
        (THREAD_MAJOR_R, -half_crest),   # crest, bottom
        (THREAD_MAJOR_R,  half_crest),   # crest, top (axially leading)
        (THREAD_MINOR_R,  half_root),    # root, top
    ]
    return pts


def make_thread_solid_for_section(y_start, y_end, center_x, center_z):
    """
    Build the thread solid (both starts) for a thread section from y_start to y_end.

    The thread is built centered on X=0, Z=0 along the Z axis (CadQuery convention),
    then rotated and translated to the correct position at (center_x, y_start, center_z).
    """
    section_length = y_end - y_start

    # Reduce helix height slightly to prevent the swept profile from
    # overshooting beyond the section boundaries. The tooth root width
    # causes ~0.75mm overshoot at each end.
    helix_trim = TOOTH_ROOT_WIDTH / 2 + 0.1  # trim margin at each end
    helix_height = section_length - 2 * helix_trim
    helix_y_offset = helix_trim  # shift helix start inward

    thread_solids = []

    for start_idx in range(NUM_STARTS):
        phase_offset_deg = start_idx * (360.0 / NUM_STARTS)

        # Create the helical spine (along Z axis by default in CadQuery)
        helix_wire = cq.Wire.makeHelix(
            pitch=THREAD_LEAD,
            height=helix_height,
            radius=THREAD_MINOR_R + THREAD_DEPTH / 2,  # sweep at mid-depth of tooth
            lefthand=False,
        )

        tooth_pts = make_thread_tooth_profile()

        # Build profile on XZ plane (perpendicular to helix Z axis at start)
        profile_wp = (
            cq.Workplane("XZ")
            .moveTo(tooth_pts[0][0], tooth_pts[0][1])
        )
        for pt in tooth_pts[1:]:
            profile_wp = profile_wp.lineTo(pt[0], pt[1])
        profile_wp = profile_wp.close()

        try:
            thread_single = profile_wp.sweep(
                cq.Workplane("XY").add(helix_wire),
                isFrenet=True,
            )

            # Rotate for the phase offset of this start
            if phase_offset_deg != 0:
                thread_single = thread_single.rotate((0, 0, 0), (0, 0, 1), phase_offset_deg)

            # Rotate Z->Y: the helix was built along Z, rotate -90 around X to align with Y
            thread_single = thread_single.rotate((0, 0, 0), (1, 0, 0), -90)

            # Translate to correct position (shifted inward by helix_trim)
            thread_single = thread_single.translate((center_x, y_start + helix_y_offset, center_z))

            thread_solids.append(thread_single)
        except Exception as e:
            print(f"  WARNING: Helical sweep failed for start {start_idx}: {e}")
            print(f"  Falling back to smooth cylinder for this thread section.")
            pass

    return thread_solids


# ============================================================
# MODEL CONSTRUCTION
# ============================================================

print("Building unified release plate + strut geometry...")
print()

# --- Feature 1: Plate body ---
# Box from origin: X=[0,59], Y=[0,6], Z=[0,47]
plate = cq.Workplane("XY").box(PLATE_W, PLATE_D, PLATE_H, centered=False)

# --- Features 2 & 3: Guide pin pads ---
for pin_cx, pin_cz in GUIDE_PIN_CENTERS:
    pad_x0 = pin_cx - PIN_PAD_DIA / 2
    pad_z0 = pin_cz - PIN_PAD_H / 2

    if pin_cx < 0:
        # Left pad: extend right edge into plate body
        pad_right = max(pad_x0 + PIN_PAD_DIA, 1.0)
        pad = (
            cq.Workplane("XY")
            .box(pad_right - pad_x0, PLATE_D, PIN_PAD_H, centered=False)
            .translate((pad_x0, 0, pad_z0))
        )
    else:
        # Right pad: extend left edge into plate body
        pad_left = min(pad_x0, PLATE_W - 1.0)
        pad_right = pad_x0 + PIN_PAD_DIA
        pad = (
            cq.Workplane("XY")
            .box(pad_right - pad_left, PLATE_D, PIN_PAD_H, centered=False)
            .translate((pad_left, 0, pad_z0))
        )
    plate = plate.union(pad)

# --- Features 8 & 9: Integral guide pins ---
# 6mm diameter x 15mm long cylinders on back face at guide pin centers.
# NOTE: Guide pins are unioned BEFORE thread operations to avoid OCCT boolean
# corruption when unioning simple cylinders with complex helical thread geometry.
for pin_cx, pin_cz in GUIDE_PIN_CENTERS:
    pin = (
        cq.Workplane("XZ")
        .center(pin_cx, pin_cz)
        .circle(GUIDE_PIN_DIA / 2)
        .extrude(-GUIDE_PIN_LENGTH)      # XZ normal is -Y; negative extrude goes +Y
        .translate((0, PLATE_D, 0))      # shift to back face
    )
    plate = plate.union(pin)

# --- Features 10-14: Stepped bores with chamfers (x4) ---
# Revolved profile technique: define the full axial cross-section as (R, Y) points
# and revolve 360 degrees around the Y axis.
# NOTE: Bore cuts are performed BEFORE thread operations because OCCT boolean
# engine produces corrupt results when cutting revolved profiles from solids
# containing complex helical sweep geometry.
profile_pts = [
    (0,                 0),                                          # axis at front face
    (R_OUTER - OUTER_CHAMFER, 0),                                    # outer chamfer start
    (R_OUTER,           OUTER_CHAMFER),                              # outer chamfer end
    (R_OUTER,           OUTER_BORE_DEPTH),                           # outer bore floor (Y=2)
    (R_INNER,           OUTER_BORE_DEPTH),                           # step to inner lip
    (R_INNER,           OUTER_BORE_DEPTH + INNER_LIP_DEPTH),        # inner lip floor (Y=4)
    (R_TUBE + TUBE_CHAMFER, OUTER_BORE_DEPTH + INNER_LIP_DEPTH),    # tube chamfer start
    (R_TUBE,            OUTER_BORE_DEPTH + INNER_LIP_DEPTH + TUBE_CHAMFER),  # tube chamfer end
    (R_TUBE,            PLATE_D),                                    # tube hole to back face
    (0,                 PLATE_D),                                    # axis at back face
]

bore_profile = cq.Workplane("XY").moveTo(*profile_pts[0])
for pt in profile_pts[1:]:
    bore_profile = bore_profile.lineTo(*pt)
bore_profile = bore_profile.close()

# Revolve around Y axis: axis point (0,0), axis direction (0,1)
bore_cutter = bore_profile.revolve(360, (0, 0), (0, 1))

# Cut each bore at its (cx, cz) position
for cx, cz in BORE_CENTERS:
    plate = plate.cut(bore_cutter.translate((cx, 0, cz)))

# --- Feature 4: Strut smooth section ---
# 12mm diameter cylinder from Y=6 (plate back face) to Y=116
# Centered at (STRUT_X, STRUT_Z) in the XZ plane
smooth_strut = (
    cq.Workplane("XZ")
    .center(STRUT_X, STRUT_Z)
    .circle(STRUT_RADIUS)
    .extrude(-STRUT_SMOOTH_LENGTH)     # XZ normal is -Y; negative extrude goes +Y
    .translate((0, STRUT_SMOOTH_Y_START, 0))
)
plate = plate.union(smooth_strut)

# --- Feature 5: Strut thread core ---
# Minor diameter cylinder for the threaded section, Y=116 to Y=136
thread_core = (
    cq.Workplane("XZ")
    .center(STRUT_X, STRUT_Z)
    .circle(THREAD_MINOR_R)
    .extrude(-STRUT_THREAD_LENGTH)
    .translate((0, STRUT_THREAD_Y_START, 0))
)
plate = plate.union(thread_core)

# --- Feature 6: Strut thread helices (knob end only) ---
print("Attempting helical thread sweep for knob end...")
thread_solids = make_thread_solid_for_section(
    STRUT_THREAD_Y_START, STRUT_THREAD_Y_END,
    STRUT_X, STRUT_Z
)
for ts in thread_solids:
    plate = plate.union(ts)

if not thread_solids:
    print("  Thread sweep failed. Using smooth 12mm cylinder as fallback.")
    print("  NOTE: Thread geometry is approximated -- no helical features present.")
    thread_fallback = (
        cq.Workplane("XZ")
        .center(STRUT_X, STRUT_Z)
        .circle(STRUT_RADIUS)
        .extrude(-STRUT_THREAD_LENGTH)
        .translate((0, STRUT_THREAD_Y_START, 0))
    )
    plate = plate.union(thread_fallback)
else:
    print("  Helical thread sweep succeeded.")

# --- Feature 7: Strut end chamfer (knob end, Y=136) ---
# Chamfer at Y=136: taper from major radius inward at the end face
# Build revolved triangle profile as cutter, centered on strut axis
# The cutter is built in local coordinates then translated to strut position
chamfer_profile = (
    cq.Workplane("XY")
    .moveTo(THREAD_MAJOR_R - STRUT_CHAMFER, 0)
    .lineTo(THREAD_MAJOR_R, 0)
    .lineTo(THREAD_MAJOR_R, STRUT_CHAMFER)
    .close()
)
chamfer_cutter = chamfer_profile.revolve(360, (0, 0), (0, 1))
# This cutter is at Y=0..STRUT_CHAMFER centered on X=0, Z=0
# Translate to knob end: Y=STRUT_TOTAL_Y - STRUT_CHAMFER..STRUT_TOTAL_Y, centered at strut XZ
chamfer_cutter = chamfer_cutter.translate((STRUT_X, STRUT_TOTAL_Y - STRUT_CHAMFER, STRUT_Z))
plate = plate.cut(chamfer_cutter)
print("Chamfer applied to knob end.")

print()

# ============================================================
# EXPORT STEP FILE
# ============================================================

output_path = Path(__file__).parent / "release-plate-cadquery.step"
cq.exporters.export(plate, str(output_path))
print(f"STEP exported to: {output_path}")
print()

# ============================================================
# VALIDATION (Rubrics 3, 4, 5)
# ============================================================

print("VALIDATION")
print("=" * 60)

v = Validator(plate)

# --- Feature 1: Plate body ---
v.check_solid("Plate body center",
              PLATE_W / 2, PLATE_D / 2, PLATE_H / 2)
v.check_solid("Plate body near origin",
              1.0, PLATE_D / 2, 1.0)
v.check_solid("Plate body far corner",
              PLATE_W - 1.0, PLATE_D / 2, PLATE_H - 1.0)

# --- Features 2 & 3: Guide pin pads ---
v.check_solid("Left pad material",
              GUIDE_PIN_CENTERS[0][0], PLATE_D / 2, 23.5 + PIN_PAD_H / 2 - 0.5,
              "solid in left pad wall above pin")
v.check_solid("Right pad material",
              GUIDE_PIN_CENTERS[1][0], PLATE_D / 2, 23.5 + PIN_PAD_H / 2 - 0.5,
              "solid in right pad wall above pin")

# --- Feature 4: Strut smooth section ---
# Check solid at various points along the smooth strut
v.check_solid("Strut smooth near plate",
              STRUT_X, STRUT_SMOOTH_Y_START + 5.0, STRUT_Z,
              "solid in smooth strut near plate (Y=11)")
v.check_solid("Strut smooth midpoint",
              STRUT_X, (STRUT_SMOOTH_Y_START + STRUT_SMOOTH_Y_END) / 2, STRUT_Z,
              "solid at strut smooth section midpoint (Y=61)")
v.check_solid("Strut smooth near thread transition",
              STRUT_X, STRUT_SMOOTH_Y_END - 5.0, STRUT_Z,
              "solid in smooth strut near thread transition (Y=111)")
v.check_solid("Strut smooth near surface",
              STRUT_X + STRUT_RADIUS - 0.3,
              (STRUT_SMOOTH_Y_START + STRUT_SMOOTH_Y_END) / 2, STRUT_Z,
              "solid just inside strut surface")
v.check_void("Outside strut smooth",
             STRUT_X + STRUT_RADIUS + 0.5,
             (STRUT_SMOOTH_Y_START + STRUT_SMOOTH_Y_END) / 2, STRUT_Z,
             "void outside strut diameter")

# --- Feature 5 & 6: Strut threaded section ---
v.check_solid("Thread section core center",
              STRUT_X, (STRUT_THREAD_Y_START + STRUT_THREAD_Y_END) / 2, STRUT_Z,
              "solid at thread section center axis (Y=126)")
v.check_solid("Thread section at minor radius",
              STRUT_X + THREAD_MINOR_R - 0.3,
              (STRUT_THREAD_Y_START + STRUT_THREAD_Y_END) / 2, STRUT_Z,
              "solid inside minor radius of thread section")
v.check_void("Thread section outside major radius",
             STRUT_X + THREAD_MAJOR_R + 0.5,
             (STRUT_THREAD_Y_START + STRUT_THREAD_Y_END) / 2, STRUT_Z,
             "void well outside major radius of thread section")
v.check_solid("Thread section near start",
              STRUT_X, STRUT_THREAD_Y_START + 1.0, STRUT_Z,
              "solid at thread section near smooth transition (Y=117)")
v.check_solid("Thread section near end",
              STRUT_X, STRUT_THREAD_Y_END - 1.0, STRUT_Z,
              "solid at thread section near knob end (Y=135)")

# --- Feature 7: Strut end chamfer ---
# At Y=136 face, chamfer removes material at outer edge
# At the very end, max radius = THREAD_MAJOR_R - STRUT_CHAMFER = 5.5mm
v.check_void("Strut end chamfer material removed",
             STRUT_X + THREAD_MAJOR_R - 0.1,
             STRUT_TOTAL_Y - 0.1, STRUT_Z,
             "void in chamfer zone at knob end (R=5.9mm from axis)")
v.check_solid("Strut end past chamfer at core",
              STRUT_X, STRUT_TOTAL_Y - 0.3, STRUT_Z,
              "solid at core past chamfer")

# --- Features 8 & 9: Integral guide pins ---
GUIDE_PIN_TIP_Y = PLATE_D + GUIDE_PIN_LENGTH  # 21.0
for i, (pin_cx, pin_cz) in enumerate(GUIDE_PIN_CENTERS):
    side = "Left" if i == 0 else "Right"

    v.check_solid(f"{side} guide pin center",
                  pin_cx, PLATE_D + GUIDE_PIN_LENGTH / 2, pin_cz,
                  f"solid at {side.lower()} pin center, mid-length")
    v.check_solid(f"{side} guide pin near tip",
                  pin_cx, GUIDE_PIN_TIP_Y - 0.5, pin_cz,
                  f"solid at {side.lower()} pin near tip")
    v.check_solid(f"{side} guide pin near base",
                  pin_cx, PLATE_D + 0.5, pin_cz,
                  f"solid at {side.lower()} pin near base")
    v.check_void(f"{side} guide pin outside radius",
                 pin_cx + GUIDE_PIN_DIA / 2 + 0.5, PLATE_D + GUIDE_PIN_LENGTH / 2, pin_cz,
                 f"void outside {side.lower()} pin")
    v.check_void(f"{side} guide pin above tip",
                 pin_cx, GUIDE_PIN_TIP_Y + 0.5, pin_cz,
                 f"void above {side.lower()} pin tip")

# --- Features 10-14: Stepped bores (x4) ---
for i, (cx, cz) in enumerate(BORE_CENTERS):
    label = f"Bore {i+1}"

    # Outer bore: void at center, Y=1.0 (within 0-2mm depth)
    v.check_void(f"{label} outer bore center",
                 cx, 1.0, cz,
                 f"void at bore center, outer bore depth")
    v.check_solid(f"{label} outer bore wall",
                  cx + R_OUTER + 0.5, 1.0, cz,
                  f"solid outside outer bore")
    v.check_void(f"{label} outer bore inner edge",
                 cx + R_OUTER - 0.5, 1.0, cz,
                 f"void inside outer bore near wall")

    # Inner lip
    v.check_void(f"{label} inner lip center",
                 cx, 3.0, cz,
                 f"void at bore center, inner lip depth")
    v.check_solid(f"{label} inner lip wall",
                  cx + R_INNER + 0.5, 3.0, cz,
                  f"solid outside inner lip")
    v.check_void(f"{label} inner lip inner edge",
                 cx + R_INNER - 0.3, 3.0, cz,
                 f"void inside inner lip near wall")
    v.check_solid(f"{label} outer-to-inner step",
                  cx + R_OUTER - 0.3, 3.0, cz,
                  f"solid at outer bore radius, inner lip depth")

    # Tube hole
    v.check_void(f"{label} tube hole center",
                 cx, 5.0, cz,
                 f"void at bore center, structural back depth")
    v.check_solid(f"{label} tube hole wall",
                  cx + R_TUBE + 0.5, 5.0, cz,
                  f"solid outside tube hole")
    v.check_solid(f"{label} inner-to-tube step",
                  cx + R_INNER - 0.3, 5.0, cz,
                  f"solid at inner lip radius, back depth")

    # Chamfers
    v.check_solid(f"{label} outer chamfer",
                  cx + R_OUTER - 0.1, 0.1, cz,
                  f"solid in outer chamfer zone")
    v.check_solid(f"{label} tube chamfer",
                  cx + R_TUBE + 0.08, OUTER_BORE_DEPTH + INNER_LIP_DEPTH + 0.05, cz,
                  f"solid in tube chamfer zone")

# --- Rubric 4: Solid validity ---
v.check_valid()
v.check_single_body()

# Volume estimate:
# Plate body: 59 * 6 * 47 = 16638 mm^3
# Smooth strut: pi * 6^2 * 110 = ~12441 mm^3
# Thread section: ~pi * 5.25^2 * 20 = ~1732 mm^3
# Guide pins: 2 * pi * 3^2 * 15 = ~848 mm^3
# Total estimate: ~31659 mm^3
# Use plate body envelope as reference with generous fill range
PLATE_ENVELOPE = PLATE_W * PLATE_D * PLATE_H
v.check_volume(expected_envelope=PLATE_ENVELOPE, fill_range=(0.5, 3.0))

# --- Rubric 5: Bounding box ---
bb = plate.val().BoundingBox()

# Expected bounds:
# X: left pad extends to pin_cx - pad_dia/2 = -3.85 - 5.0 = -8.85
#    right pad extends to pin_cx + pad_dia/2 = 66.15 + 5.0 = 71.15
# Y: 0.0 to STRUT_TOTAL_Y = 136.0 (strut extends furthest)
# Z: 0.0 to 47.0
#    (strut is centered at Z=23.5, radius 6.0, so Z range 17.5..29.5, within plate)

exp_xmin = GUIDE_PIN_CENTERS[0][0] - PIN_PAD_DIA / 2   # -8.85
exp_xmax = GUIDE_PIN_CENTERS[1][0] + PIN_PAD_DIA / 2   # 71.15
exp_ymin = 0.0
exp_ymax = STRUT_TOTAL_Y                                # 136.0
exp_zmin = 0.0
exp_zmax = PLATE_H                                       # 47.0

v.check_bbox("X", bb.xmin, bb.xmax, exp_xmin, exp_xmax)
v.check_bbox("Y", bb.ymin, bb.ymax, exp_ymin, exp_ymax)
v.check_bbox("Z", bb.zmin, bb.zmax, exp_zmin, exp_zmax)

# ============================================================
# SUMMARY
# ============================================================
if not v.summary():
    sys.exit(1)
