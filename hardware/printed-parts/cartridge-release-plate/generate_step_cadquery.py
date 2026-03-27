#!/usr/bin/env python3
"""
Cartridge Release Plate with Integral Strut and Guide Pins — CadQuery STEP Generator

Generates a STEP file for the release plate per parts.md specification.
This is a single printed PETG piece: plate body + threaded strut + 2 guide pins.

Coordinate system:
  Origin: bottom-left corner of dock-facing face (the face with stepped bores)
  X: plate width, left to right [0, 59]
  Y: plate depth, dock-facing face to rear face [0, 6], then strut/pins extend in +Y
  Z: plate height, bottom to top [0, 47]
  Envelope (plate body): 59 x 6 x 47 mm -> X:[0,59] Y:[0,6] Z:[0,47]

  Dock-facing face (Y=0): 4x stepped bores face this direction
  Rear face (Y=6): strut and guide pins extend from here in +Y direction
  Strut extends ~130mm in +Y from rear face (through rear wall, interior, to front wall)
  Guide pins extend 15mm in +Y from rear face (into rear wall bushings)
"""

import sys
import math
from pathlib import Path

# Add tools/ to path for step_validate
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

import cadquery as cq
from step_validate import Validator

# ============================================================================
# RUBRIC 2 — Coordinate System Declaration
# ============================================================================
# Origin: bottom-left corner of dock-facing face
# X: plate width, left to right, [0, 59]
# Y: plate depth/thickness, dock-facing face (Y=0) to rear face (Y=6),
#    then strut/pins extend in +Y beyond Y=6
# Z: plate height, bottom to top, [0, 47]
# Envelope (plate body only): 59 x 6 x 47 mm

# ============================================================================
# DIMENSIONS FROM PARTS.MD
# ============================================================================

# Plate body
PLATE_W = 59.0   # X dimension
PLATE_D = 6.0    # Y dimension (thickness)
PLATE_H = 47.0   # Z dimension

# Bore grid - 2x2, centers relative to plate bottom-left corner (X, Z)
BORE_CENTERS_XZ = [
    (9.5, 9.5),    # Bore 1: bottom-left
    (49.5, 9.5),   # Bore 2: bottom-right
    (9.5, 37.5),   # Bore 3: top-left
    (49.5, 37.5),  # Bore 4: top-right
]

# Stepped bore dimensions (from parts.md, caliper-verified)
TUBE_HOLE_DIA = 6.50       # Through full plate thickness
INNER_LIP_DIA = 9.70       # Collet hugger
OUTER_BORE_DIA = 15.30     # Body end cradle

# Axial depth stack (from dock-facing face Y=0 inward):
#   Y=0 to Y=2: outer bore (15.30mm dia)
#   Y=2 to Y=4: inner lip (9.70mm dia)
#   Y=4 to Y=6: structural back with tube hole only (6.50mm dia)
# Tube hole runs through full 6mm thickness.
OUTER_BORE_DEPTH = 2.0     # Y=0 to Y=2
INNER_LIP_DEPTH = 2.0      # Y=2 to Y=4

# Chamfers
TUBE_HOLE_CHAMFER = 0.1     # At tube hole entry on rear face (Y=6)
OUTER_BORE_CHAMFER = 0.3    # 45-degree lead-in at outer bore entry (Y=0 face)

# Strut
STRUT_DIA = 12.0            # OD
STRUT_CENTER_X = 29.5       # Center of plate (59/2)
STRUT_CENTER_Z = 23.5       # Center of plate (47/2)
STRUT_LENGTH = 130.0        # From plate rear face (Y=6) in +Y direction
STRUT_Y_START = PLATE_D     # Y=6 (plate rear face)
STRUT_Y_END = PLATE_D + STRUT_LENGTH  # Y=136

# Thread parameters (Tr12x3 2-start trapezoidal)
THREAD_MAJOR_DIA = 12.0     # Same as strut OD
THREAD_MINOR_DIA = 9.0      # 12.0 - 2*1.5
THREAD_DEPTH = 1.5          # (12-9)/2
THREAD_PITCH = 3.0          # Per start
THREAD_LEAD = 6.0           # 2-start: 2 * 3.0mm
THREAD_FLANK_ANGLE = 29.0   # Degrees (trapezoidal)
THREAD_LENGTH = 20.0        # Threaded section at front end of strut
THREAD_Y_START = STRUT_Y_END - THREAD_LENGTH  # Y=116
THREAD_Y_END = STRUT_Y_END                     # Y=136

# Guide pins
PIN_DIA = 6.0
PIN_LENGTH = 15.0
PIN_CENTERS_XZ = [
    (12.0, 23.5),   # Left pin
    (47.0, 23.5),   # Right pin
]
PIN_Y_START = PLATE_D       # Y=6 (plate rear face)
PIN_Y_END = PLATE_D + PIN_LENGTH  # Y=21

# ============================================================================
# RUBRIC 1 — Feature Planning Table
# ============================================================================
print("=" * 80)
print("RUBRIC 1 — Feature Planning Table")
print("=" * 80)
features = [
    ("1",  "Plate body",             "Main structural plate",          "Add",  "Box",      "Y",
     f"(29.5, 3.0, 23.5)",   f"{PLATE_W}x{PLATE_D}x{PLATE_H}mm"),
    ("2a", "Tube clearance hole x4", "Tube passes through",            "Rem",  "Cylinder", "Y",
     "bore centers, Y=0..6",  f"{TUBE_HOLE_DIA}mm dia, 6mm thru"),
    ("2b", "Inner lip x4",           "Lateral constraint on collet",   "Rem",  "Cylinder", "Y",
     "bore centers, Y=2..4",  f"{INNER_LIP_DIA}mm dia, 2mm deep"),
    ("2c", "Outer bore x4",          "Aligns plate on JG body end",   "Rem",  "Cylinder", "Y",
     "bore centers, Y=0..2",  f"{OUTER_BORE_DIA}mm dia, 2mm deep"),
    ("2d", "Tube hole chamfer x4",   "Prevents tube snagging",         "Rem",  "Chamfer",  "Y",
     "bore centers, Y=6",    f"{TUBE_HOLE_CHAMFER}mm at rear face"),
    ("2e", "Outer bore chamfer x4",  "Guides plate over body end",     "Rem",  "Chamfer",  "Y",
     "bore centers, Y=0",    f"{OUTER_BORE_CHAMFER}mm x 45deg"),
    ("3",  "Integral strut",         "Transmits knob twist to travel", "Add",  "Cylinder", "Y",
     f"({STRUT_CENTER_X}, Y=6..136, {STRUT_CENTER_Z})",
     f"{STRUT_DIA}mm dia, {STRUT_LENGTH}mm"),
    ("4",  "Front thread (Tr12x3)",  "Engages wing knob",              "Rem",  "Helix",    "Y",
     "strut Y=116..136",     f"major {THREAD_MAJOR_DIA}, minor {THREAD_MINOR_DIA}"),
    ("5a", "Guide pin left",         "Anti-rotation + guide",          "Add",  "Cylinder", "Y",
     f"({PIN_CENTERS_XZ[0][0]}, Y=6..21, {PIN_CENTERS_XZ[0][1]})",
     f"{PIN_DIA}mm dia, {PIN_LENGTH}mm"),
    ("5b", "Guide pin right",        "Anti-rotation + guide",          "Add",  "Cylinder", "Y",
     f"({PIN_CENTERS_XZ[1][0]}, Y=6..21, {PIN_CENTERS_XZ[1][1]})",
     f"{PIN_DIA}mm dia, {PIN_LENGTH}mm"),
]
for row in features:
    num, name, func, op, shape, axis, pos, dims = row
    print(f"  {num:<4} {name:<28} {func:<30} {op:<5} {shape:<10} {axis:<5} {pos}")
    print(f"       Dims: {dims}")
print()
sys.stdout.flush()

# ============================================================================
# MODELING
# ============================================================================

# --- Feature 1: Plate body ---
print("Building plate body...")
sys.stdout.flush()
plate = cq.Workplane("XY").box(PLATE_W, PLATE_D, PLATE_H, centered=False)

# --- Feature 2: Stepped bores (4x) ---
# Each bore is a revolved profile cut from the plate.
# Profile in (R, Y_axial) coordinates, revolved around Y axis, then translated to bore center.
print("Cutting stepped bores...")
sys.stdout.flush()

R_outer = OUTER_BORE_DIA / 2.0      # 7.65
R_inner = INNER_LIP_DIA / 2.0       # 4.85
R_tube = TUBE_HOLE_DIA / 2.0        # 3.25
C_outer = OUTER_BORE_CHAMFER         # 0.3
C_tube = TUBE_HOLE_CHAMFER           # 0.1

for i, (cx, cz) in enumerate(BORE_CENTERS_XZ):
    # Revolved profile in (X, Y) = (R, axial_Y) plane.
    # Y=0 is dock-facing face, Y=6 is rear face.
    # Revolve around the Y axis (0,0,0)-(0,1,0).
    # Trace the void cross-section clockwise from axis at dock face:
    profile_pts = [
        (0,                     0),                    # Axis at dock face
        (R_outer - C_outer,     0),                    # Before outer bore chamfer
        (R_outer,               C_outer),              # After outer bore chamfer (0.3mm 45deg)
        (R_outer,               OUTER_BORE_DEPTH),     # Outer bore wall at Y=2
        (R_inner,               OUTER_BORE_DEPTH),     # Step to inner lip at Y=2
        (R_inner,               OUTER_BORE_DEPTH + INNER_LIP_DEPTH),  # Inner lip wall at Y=4
        (R_tube,                OUTER_BORE_DEPTH + INNER_LIP_DEPTH),  # Step to tube hole at Y=4
        (R_tube,                PLATE_D - C_tube),     # Tube hole near rear face
        (R_tube - C_tube,       PLATE_D),              # Tube chamfer at rear face entry
        (0,                     PLATE_D),              # Axis at rear face
    ]

    bore_profile = cq.Workplane("XY").polyline(profile_pts).close()
    bore_solid = bore_profile.revolve(360, (0, 0, 0), (0, 1, 0))
    plate = plate.cut(bore_solid.translate((cx, 0, cz)))

print("  4 stepped bores cut.")

# --- Feature 3: Integral strut (smooth cylinder) ---
# 12mm OD cylinder from plate rear face (Y=6) to Y=136, centered at (29.5, 23.5) in XZ.
# Use XZ workplane. Normal is -Y. extrude(positive) goes -Y, extrude(negative) goes +Y.
# Position workplane at Y=PLATE_D (Y=6) by using offset from Y=0.
# offset parameter on XZ workplane: offset along the normal (-Y), so offset=-6 puts us at Y=6.
print("Building strut...")
sys.stdout.flush()
strut = (
    cq.Workplane("XZ")
    .workplane(offset=-PLATE_D)  # -(-Y)*6 => Y=6
    .center(STRUT_CENTER_X, STRUT_CENTER_Z)
    .circle(STRUT_DIA / 2.0)
    .extrude(-STRUT_LENGTH)  # -(- Y direction) = +Y direction, length 130
)
plate = plate.union(strut)
print("  Strut added.")

# --- Feature 4: Front-end thread (Tr12x3 2-start trapezoidal) ---
# Ring-groove approximation: cut annular trapezoidal grooves at each pitch interval.
# For 2-start, there are two sets of grooves offset by LEAD/2 = 3.0mm.
print("Building thread grooves...")
sys.stdout.flush()

half_flank_rad = math.radians(THREAD_FLANK_ANGLE / 2.0)  # 14.5 degrees
tan_half = math.tan(half_flank_rad)

# Groove dimensions:
# At major radius: groove half-width = (pitch/2 - depth*tan(half_flank)) / 2
# At minor radius: groove half-width = (pitch/2 + depth*tan(half_flank)) / 2
groove_top_hw = (THREAD_PITCH / 2.0 - THREAD_DEPTH * tan_half) / 2.0  # ~0.556mm
groove_bot_hw = (THREAD_PITCH / 2.0 + THREAD_DEPTH * tan_half) / 2.0  # ~0.944mm

R_major = THREAD_MAJOR_DIA / 2.0  # 6.0
R_minor = THREAD_MINOR_DIA / 2.0  # 4.5

groove_count = 0

for start_idx in range(2):  # 2-start thread
    # Start offset: second start is offset by LEAD/2 = 3.0mm
    start_offset = start_idx * (THREAD_LEAD / 2.0)  # 0 or 3.0

    y = THREAD_Y_START + start_offset
    while y < THREAD_Y_END:
        groove_center_y = y + THREAD_PITCH / 4.0  # Center of groove

        # Check that the groove center is within the threaded section.
        # Groove root may extend slightly past boundaries (clipped by strut geometry).
        if groove_center_y < THREAD_Y_START:
            y += THREAD_PITCH
            continue
        if groove_center_y > THREAD_Y_END:
            break

        # Trapezoidal groove profile in (R, Y_axial) plane, revolved around Y axis
        groove_pts = [
            (R_major, groove_center_y - groove_top_hw),  # Top-left (entry)
            (R_minor, groove_center_y - groove_bot_hw),  # Bottom-left (root)
            (R_minor, groove_center_y + groove_bot_hw),  # Bottom-right (root)
            (R_major, groove_center_y + groove_top_hw),  # Top-right (exit)
        ]

        groove_profile = cq.Workplane("XY").polyline(groove_pts).close()
        groove_solid = groove_profile.revolve(360, (0, 0, 0), (0, 1, 0))
        groove_solid = groove_solid.translate((STRUT_CENTER_X, 0, STRUT_CENTER_Z))
        plate = plate.cut(groove_solid)
        groove_count += 1

        y += THREAD_PITCH

print(f"  {groove_count} thread grooves cut.")
sys.stdout.flush()

# --- Feature 5: Guide pins (2x) ---
print("Building guide pins...")
for j, (px, pz) in enumerate(PIN_CENTERS_XZ):
    pin = (
        cq.Workplane("XZ")
        .workplane(offset=-PLATE_D)  # Y=6
        .center(px, pz)
        .circle(PIN_DIA / 2.0)
        .extrude(-PIN_LENGTH)  # +Y direction
    )
    plate = plate.union(pin)
print("  2 guide pins added.")

# ============================================================================
# EXPORT STEP FILE
# ============================================================================
output_path = Path(__file__).parent / "release-plate-cadquery.step"
cq.exporters.export(plate, str(output_path))
print(f"\nSTEP file exported to: {output_path}")

# ============================================================================
# RUBRIC 3 — Feature-Specification Reconciliation (Point-in-Solid Probes)
# ============================================================================
print("\n" + "=" * 60)
print("RUBRIC 3 — Validation Probes")
print("=" * 60)

v = Validator(plate)

# --- Plate body ---
v.check_solid("Plate body center", PLATE_W / 2, PLATE_D / 2, PLATE_H / 2,
              "solid at plate center")
v.check_solid("Plate corner near origin", 0.5, 0.5, 0.5,
              "solid near (0,0,0)")
v.check_solid("Plate corner far", 58.5, 5.5, 46.5,
              "solid near (59,6,47)")
v.check_void("Outside plate -X", -0.5, 3.0, 23.5, "void left of plate")
v.check_void("Outside plate +X", 59.5, 3.0, 23.5, "void right of plate")
v.check_void("Outside plate -Z", 29.5, 3.0, -0.5, "void below plate")
v.check_void("Outside plate +Z", 29.5, 3.0, 47.5, "void above plate")

# --- Stepped bores (4x) ---
for i, (cx, cz) in enumerate(BORE_CENTERS_XZ):
    tag = f"Bore{i+1}"

    # Tube hole: void through full plate thickness
    v.check_void(f"{tag} tube center Y=1", cx, 1.0, cz, "tube hole near dock face")
    v.check_void(f"{tag} tube center Y=3", cx, 3.0, cz, "tube hole mid-plate")
    v.check_void(f"{tag} tube center Y=5", cx, 5.0, cz, "tube hole near rear face")

    # Tube hole boundary check
    v.check_void(f"{tag} tube edge-in Y=3",
                 cx + R_tube - 0.2, 3.0, cz, "void just inside tube hole radius")
    # Between inner lip radius (4.85) and outer bore radius at Y=3 (outer bore ended):
    # At Y=3, only the inner lip (R<4.85) is void. Just outside inner lip should be solid.
    v.check_solid(f"{tag} wall outside inner lip Y=3",
                  cx + R_inner + 0.5, 3.0, cz, "solid outside inner lip at Y=3")

    # Outer bore: void at Y=1, solid outside
    v.check_void(f"{tag} outer bore Y=1",
                 cx + R_outer - 0.5, 1.0, cz, "void inside outer bore")
    v.check_solid(f"{tag} outside outer bore Y=1",
                  cx + R_outer + 0.5, 1.0, cz, "solid outside outer bore")

    # Inner lip: void at Y=3, solid outside
    v.check_void(f"{tag} inner lip Y=3",
                 cx + R_inner - 0.5, 3.0, cz, "void inside inner lip")
    v.check_solid(f"{tag} outside inner lip Y=3",
                  cx + R_inner + 0.5, 3.0, cz, "solid outside inner lip")

    # Outer bore does NOT extend to Y=3
    v.check_solid(f"{tag} outer bore gone Y=3",
                  cx + R_outer - 0.5, 3.0, cz, "solid where outer bore ended")

    # Structural back: only tube hole at Y=5
    v.check_void(f"{tag} tube at Y=5", cx, 5.0, cz, "tube hole in structural back")
    v.check_solid(f"{tag} struct back Y=5",
                  cx + R_tube + 0.5, 5.0, cz, "solid in structural back")

# --- Strut ---
v.check_solid("Strut center Y=60", STRUT_CENTER_X, 60.0, STRUT_CENTER_Z,
              "solid at strut mid-length")
v.check_solid("Strut edge Y=60",
              STRUT_CENTER_X + STRUT_DIA / 2 - 0.3, 60.0, STRUT_CENTER_Z,
              "solid near strut OD")
v.check_void("Outside strut Y=60",
             STRUT_CENTER_X + STRUT_DIA / 2 + 0.5, 60.0, STRUT_CENTER_Z,
             "void outside strut")
v.check_solid("Strut at Y=10", STRUT_CENTER_X, 10.0, STRUT_CENTER_Z,
              "solid at strut near plate")
v.check_solid("Strut at Y=135", STRUT_CENTER_X, 135.0, STRUT_CENTER_Z,
              "solid near strut tip")
v.check_void("Past strut Y=137", STRUT_CENTER_X, 137.0, STRUT_CENTER_Z,
             "void past strut end")

# --- Thread grooves ---
# First groove center: THREAD_Y_START + PITCH/4 = 116 + 0.75 = 116.75
first_groove_y = THREAD_Y_START + THREAD_PITCH / 4.0
mid_thread_r = (R_major + R_minor) / 2.0  # 5.25

# Probe at the first groove center: R=5.0 from axis (between minor 4.5 and major 6.0)
v.check_void("Thread groove void",
             STRUT_CENTER_X + R_minor + 0.5, first_groove_y, STRUT_CENTER_Z,
             f"void at thread groove (R=5.0 from axis, Y={first_groove_y:.2f})")

# Tooth: between grooves, should be solid at near-major radius
# First tooth center at approximately THREAD_Y_START + 3*PITCH/4 = 116 + 2.25 = 118.25
first_tooth_y = THREAD_Y_START + 3 * THREAD_PITCH / 4.0
v.check_solid("Thread tooth solid",
              STRUT_CENTER_X + R_major - 0.3, first_tooth_y, STRUT_CENTER_Z,
              "solid at thread tooth")

# Smooth section has no grooves
v.check_solid("No groove at Y=60",
              STRUT_CENTER_X + R_major - 0.3, 60.0, STRUT_CENTER_Z,
              "solid at smooth strut surface")

# --- Guide pins ---
for j, (px, pz) in enumerate(PIN_CENTERS_XZ):
    tag = f"Pin{j+1}"
    mid_y = PIN_Y_START + PIN_LENGTH / 2  # Y=13.5

    v.check_solid(f"{tag} center", px, mid_y, pz, "solid at pin center")
    v.check_solid(f"{tag} edge", px + PIN_DIA / 2 - 0.3, mid_y, pz,
                  "solid near pin OD")
    v.check_void(f"{tag} outside", px + PIN_DIA / 2 + 0.5, mid_y, pz,
                 "void outside pin")
    v.check_solid(f"{tag} base Y=7", px, 7.0, pz, "solid at pin base")
    v.check_solid(f"{tag} tip Y=20", px, 20.0, pz, "solid near pin tip")
    v.check_void(f"{tag} past tip Y=22", px, 22.0, pz, "void past pin end")

# ============================================================================
# RUBRIC 4 — Solid Validity
# ============================================================================
print("\n" + "=" * 60)
print("RUBRIC 4 — Solid Validity")
print("=" * 60)
v.check_valid()
v.check_single_body()
# Envelope volume for ratio: use plate body as reference, allow >1.0 for strut/pins
v.check_volume(expected_envelope=PLATE_W * PLATE_D * PLATE_H, fill_range=(0.5, 3.0))

# ============================================================================
# RUBRIC 5 — Bounding Box Reconciliation
# ============================================================================
print("\n" + "=" * 60)
print("RUBRIC 5 — Bounding Box")
print("=" * 60)
bb = plate.val().BoundingBox()
print(f"Actual BB: X[{bb.xmin:.2f}, {bb.xmax:.2f}] "
      f"Y[{bb.ymin:.2f}, {bb.ymax:.2f}] "
      f"Z[{bb.zmin:.2f}, {bb.zmax:.2f}]")

v.check_bbox("X", bb.xmin, bb.xmax, 0.0, PLATE_W)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, STRUT_Y_END)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, PLATE_H)

# ============================================================================
# SUMMARY
# ============================================================================
if not v.summary():
    sys.exit(1)

print("\nDone.")
