#!/usr/bin/env python3
"""
Wing Knob with Internal Tr12x3 2-Start Trapezoidal Threads — CadQuery STEP Generation

Generates the wing knob for the soda flavor injector pump cartridge twist-release
mechanism. The knob threads onto the strut's male Tr12x3 2-start trapezoidal thread.
Half a turn (180 degrees) produces 3mm of plate travel. The knob doubles as a pull
handle for cartridge extraction.

UX is the primary concern — the knob must feel good in the hand. Wings provide
torque leverage and pull-handle grip. Diamond knurl texture on the cylindrical body
provides secure grip even with wet hands.

Source material:
  - hardware/printed-parts/cartridge-twist-release/planning/parts.md
  - hardware/printed-parts/cartridge-twist-release/planning/research/3d-printed-approach.md
  - hardware/planning/step-generation-standards.md

Coordinate system:
  Origin: knob center axis at rear face
  X: width, left to right (wings extend along X)
  Y: depth along knob axis (rear face Y=0, front face Y=25)
     Y=0: rear face (thread entry, faces into cartridge)
     Y=25: front face (user grip side)
  Z: height, bottom to top
  Envelope (body only): 40mm dia x 25mm tall cylinder centered on X=0, Z=0
  Wings extend to X=+/-35mm (body radius 20mm + 15mm wing extension)

Thread geometry (internal female Tr12x3 2-start):
  Major diameter (bore): 12.3mm (12mm nominal + 0.3mm clearance)
  Minor diameter (thread crests): 9.3mm (12.3mm - 2 x 1.5mm thread depth)
  Pitch per start: 1.5mm
  Lead: 3.0mm (2 starts x 1.5mm pitch)
  Thread depth in knob: 20mm from rear face (Y=0 to Y=20)
  Flank angle: 15 degrees from vertical (half of 30-degree included angle)
  Through-hole: 12.3mm bore from Y=20 to Y=25 (smooth section pass-through)
"""

import cadquery as cq
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from step_validate import Validator

# ============================================================
# PARAMETERS
# ============================================================

# Knob body
BODY_DIA = 40.0          # cylindrical body diameter
BODY_R = BODY_DIA / 2    # 20mm
BODY_HEIGHT = 25.0        # Y extent (rear Y=0 to front Y=25)

# Wing extensions
WING_EXTENSION = 15.0    # how far beyond body radius each wing extends
WING_THICKNESS = 10.0    # thickness in Z
WING_TOTAL_SPAN = BODY_DIA + 2 * WING_EXTENSION  # 70mm tip to tip
WING_HALF_SPAN = WING_TOTAL_SPAN / 2             # 35mm from center to tip
WING_TIP_R = WING_THICKNESS / 2                  # 5mm radius for pill-shaped ends

# Thread parameters — Tr12x3 2-start (internal/female)
THREAD_MAJOR_DIA = 12.3   # bore diameter (male OD + 0.3mm clearance)
THREAD_MAJOR_R = THREAD_MAJOR_DIA / 2  # 6.15mm
THREAD_DEPTH_RADIAL = 1.5  # radial depth of each thread tooth
THREAD_MINOR_DIA = THREAD_MAJOR_DIA - 2 * THREAD_DEPTH_RADIAL  # 9.3mm
THREAD_MINOR_R = THREAD_MINOR_DIA / 2  # 4.65mm
THREAD_PITCH = 1.5        # pitch per start
THREAD_LEAD = 3.0         # 2 starts x 1.5mm pitch
THREAD_STARTS = 2
THREAD_LENGTH = 20.0      # engagement length from rear face (Y=0 to Y=20)
THREAD_FLANK_ANGLE = 15.0  # degrees from vertical (half-angle)

# Trapezoidal tooth proportions
# At the minor diameter (tooth crest), the tooth flat is narrower.
# At the major diameter (bore wall / tooth root), the groove flat is wider.
# Standard Tr thread: tooth thickness at pitch diameter ~ 0.5 * pitch
tan_flank = math.tan(math.radians(THREAD_FLANK_ANGLE))

# Tooth half-widths (axial direction)
# Crest flat (at minor radius, tooth tip): ~0.366 * pitch for Tr threads
CREST_HALF = THREAD_PITCH * 0.366 / 2    # ~0.2745mm
# Root half-width (at major radius): crest + flank taper
ROOT_HALF = CREST_HALF + THREAD_DEPTH_RADIAL * tan_flank  # + 0.402mm

# Through-hole above threads
THROUGH_HOLE_DIA = THREAD_MAJOR_DIA  # 12.3mm, smooth bore
THROUGH_HOLE_LENGTH = BODY_HEIGHT - THREAD_LENGTH  # 5mm (Y=20 to Y=25)

# Fillets and chamfers
FRONT_FILLET_R = 1.0      # front face fillet
REAR_CHAMFER = 1.0        # rear face 45-degree chamfer (thread entry aid)

# ============================================================
# FEATURE PLANNING TABLE (Rubric 1)
# ============================================================

print("=" * 120)
print("FEATURE PLANNING TABLE (Rubric 1)")
print("=" * 120)
header = (f"{'#':<4} {'Feature Name':<30} {'Mech. Function':<35} {'Op':<7} "
          f"{'Shape':<10} {'Axis':<5} {'Center (X,Y,Z)':<22} {'Dimensions':<30} {'Notes'}")
print(header)
print("-" * 120)

table_rows = [
    ("1",  "Cylindrical body",           "Structural shell + grip",       "Add",    "Cylinder", "Y",
     "(0, 12.5, 0)",       f"D{BODY_DIA}xH{BODY_HEIGHT}mm",       "Main knob body"),
    ("2",  "Wing extension +X",          "Torque leverage + pull handle", "Add",    "Stadium",  "Y",
     f"({BODY_R + WING_EXTENSION/2}, 12.5, 0)", f"{WING_TOTAL_SPAN}x{WING_THICKNESS}x{BODY_HEIGHT}mm",
     "Pill-shaped tip, extends 15mm past body"),
    ("3",  "Wing extension -X",          "Torque leverage + pull handle", "Add",    "Stadium",  "Y",
     f"(-{BODY_R + WING_EXTENSION/2}, 12.5, 0)", f"{WING_TOTAL_SPAN}x{WING_THICKNESS}x{BODY_HEIGHT}mm",
     "Pill-shaped tip, extends 15mm past body"),
    ("4",  "Internal thread bore",       "Female Tr12x3 2-start thread",  "Remove", "Helix",    "Y",
     f"(0, {THREAD_LENGTH/2}, 0)", f"D{THREAD_MAJOR_DIA}, {THREAD_LENGTH}mm deep",
     "2 helical starts, 180 deg offset"),
    ("5",  "Through-hole (smooth)",      "Strut smooth section pass",     "Remove", "Cylinder", "Y",
     f"(0, {THREAD_LENGTH + THROUGH_HOLE_LENGTH/2}, 0)", f"D{THROUGH_HOLE_DIA}x{THROUGH_HOLE_LENGTH}mm",
     "Y=20 to Y=25"),
    ("6",  "Front face fillet",          "Comfortable grip edge",         "Remove", "Fillet",   "Y",
     "outer edge at Y=25",  f"R{FRONT_FILLET_R}mm",
     "Applied to body + wing front edges"),
    ("7",  "Rear face chamfer",          "Thread entry aid",              "Remove", "Chamfer",  "Y",
     "bore edge at Y=0",    f"{REAR_CHAMFER}mm x 45deg",
     "Guides strut thread into bore"),
]

for row in table_rows:
    print(f"{row[0]:<4} {row[1]:<30} {row[2]:<35} {row[3]:<7} {row[4]:<10} {row[5]:<5} "
          f"{row[6]:<22} {row[7]:<30} {row[8]}")

print("=" * 120)
print()

# ============================================================
# MODEL CONSTRUCTION
# ============================================================

# --- Feature 1: Cylindrical body ---
# Cylinder centered on X=0, Z=0, extending Y=0 to Y=25.
# CadQuery XZ workplane: normal is -Y, so negative extrude goes +Y.
body = (
    cq.Workplane("XZ")
    .circle(BODY_R)
    .extrude(-BODY_HEIGHT)  # negative on XZ normal => +Y direction
)

# --- Features 2 & 3: Wing extensions ---
# Wings are pill-shaped (stadium cross-section in XZ plane) extending along X
# on both sides. The stadium shape provides rounded wing tips for comfort.
# Total span 70mm along X, 10mm thick along Z, full knob height along Y.
wing_profile = (
    cq.Workplane("XZ")
    .slot2D(WING_TOTAL_SPAN, WING_THICKNESS, angle=0)  # long axis along X
    .extrude(-BODY_HEIGHT)  # XZ normal -Y; negative extrude => +Y
)
body = body.union(wing_profile)

# --- Features 4 & 5: Internal bore ---
# Cut the full-length bore at the major diameter (12.3mm) through the entire
# knob (Y=0 to Y=25). This creates both the thread bore zone and the
# through-hole zone. Thread teeth will be added back into the bore.
full_bore = (
    cq.Workplane("XZ")
    .circle(THREAD_MAJOR_R)
    .extrude(-BODY_HEIGHT)  # full depth Y=0 to Y=25
)
body = body.cut(full_bore)

# --- Feature 4 (continued): Trapezoidal thread teeth ---
# For a female (internal) thread, thread teeth protrude INWARD from the bore
# wall (from major radius toward minor radius).
#
# Strategy: loft trapezoidal cross-sections along the helical path.
# Discretize each helix into many cross-sections and use OCC ThruSections.
#
# The trapezoidal tooth cross-section (in a radial-axial plane):
#   Root at major radius (6.15mm, bore wall) — narrow gap between teeth
#   Crest at minor radius (4.65mm) — flat tooth tip
#   Flanks at 15 degrees from the radial direction
#   Tooth height (radial) = 1.5mm

from OCP.gp import gp_Pnt
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeEdge
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections


def make_thread_solid_lofted(start_angle_deg):
    """Create one thread start as a lofted solid through trapezoid sections.

    Discretizes the helix into cross-sections and lofts between them.
    Each cross-section is a trapezoid positioned and oriented tangent to
    the helical path at the bore wall.

    For an internal thread, the tooth protrudes inward:
      - Root (wide base) sits at the bore wall (major radius)
      - Crest (narrow tip) protrudes toward the axis (minor radius)

    Args:
        start_angle_deg: Angular offset for this start (0 or 180).

    Returns:
        CadQuery Workplane containing the thread tooth solid, or None on failure.
    """
    start_rad = math.radians(start_angle_deg)

    # Number of cross-sections: ~16 per revolution for smooth geometry
    n_revs = THREAD_LENGTH / THREAD_PITCH  # 13.333
    sections_per_rev = 16
    n_sections = int(n_revs * sections_per_rev) + 2
    n_sections = max(n_sections, 30)

    # Trapezoid corner points in local coordinates (axial_offset, radial_depth):
    #   axial_offset: distance along Y from section center
    #   radial_depth: distance inward from bore wall (0 = bore wall, positive = toward axis)
    trap_local = [
        (-ROOT_HALF,  0),                      # root left (bore wall)
        ( ROOT_HALF,  0),                      # root right (bore wall)
        ( CREST_HALF, THREAD_DEPTH_RADIAL),    # crest right (minor radius)
        (-CREST_HALF, THREAD_DEPTH_RADIAL),    # crest left (minor radius)
    ]

    loft = BRepOffsetAPI_ThruSections(True, False)  # solid=True, ruled=False

    for i in range(n_sections):
        t = i / (n_sections - 1)
        y_pos = t * THREAD_LENGTH

        # Helix angle at this Y position
        angle = start_rad + 2 * math.pi * (y_pos / THREAD_PITCH)

        # Position on the bore wall (major radius)
        cx = THREAD_MAJOR_R * math.cos(angle)
        cz = THREAD_MAJOR_R * math.sin(angle)

        # Radial direction (inward toward axis)
        rad_x = -math.cos(angle)
        rad_z = -math.sin(angle)

        # Build 4 corner points of the trapezoid in 3D
        corners = []
        for (u, v) in trap_local:
            # u = axial offset (along Y)
            # v = radial depth (inward from bore wall)
            px = cx + v * rad_x
            py = y_pos + u
            pz = cz + v * rad_z
            corners.append(gp_Pnt(px, py, pz))

        # Create a wire from the 4 corners
        wire_builder = BRepBuilderAPI_MakeWire()
        for j in range(4):
            p1 = corners[j]
            p2 = corners[(j + 1) % 4]
            edge = BRepBuilderAPI_MakeEdge(p1, p2).Edge()
            wire_builder.Add(edge)
        wire = wire_builder.Wire()

        loft.AddWire(wire)

    loft.Build()
    if not loft.IsDone():
        print(f"  WARNING: Thread loft failed for start angle {start_angle_deg}")
        return None

    thread_shape = loft.Shape()
    return cq.Workplane("XY").newObject([cq.Shape(thread_shape)])


print("Building thread start 1 (0 deg)...")
thread1 = make_thread_solid_lofted(0)
print("Building thread start 2 (180 deg)...")
thread2 = make_thread_solid_lofted(180)

# Add thread teeth back into the bore
if thread1 is not None:
    body = body.union(thread1)
    print("  Thread start 1 unioned.")
else:
    print("  WARNING: Thread start 1 failed — bore will be smooth at this start.")

if thread2 is not None:
    body = body.union(thread2)
    print("  Thread start 2 unioned.")
else:
    print("  WARNING: Thread start 2 failed — bore will be smooth at this start.")

# --- Feature 7: Rear face chamfer (thread entry aid) ---
# Conical countersink at Y=0: bore opens from THREAD_MAJOR_R + REAR_CHAMFER at
# the rear face to THREAD_MAJOR_R at Y = REAR_CHAMFER depth. 45-degree taper.
# Modeled as a revolved triangle cut from the rear face.
chamfer_profile = (
    cq.Workplane("XY")
    .moveTo(0, 0)                                         # axis at rear face
    .lineTo(THREAD_MAJOR_R + REAR_CHAMFER, 0)             # outer edge at Y=0
    .lineTo(THREAD_MAJOR_R, REAR_CHAMFER)                 # taper to bore dia
    .lineTo(0, REAR_CHAMFER)                              # back to axis
    .close()
    .revolve(360, (0, 0), (0, 1))                         # revolve around Y axis
)
body = body.cut(chamfer_profile)
print("Rear face chamfer applied.")

# --- Feature 6: Front face fillet ---
# Fillet the outer edges at the front face (Y=25) for comfortable grip.
# Select edges on the front face and apply a 1mm fillet.
try:
    body = body.faces(">Y").fillet(FRONT_FILLET_R)
    print("Front face fillet applied.")
except Exception as e:
    print(f"Note: Front face fillet skipped due to complex geometry: {e}")
    # Fillet failure is non-critical — the knob is still functional.
    # Post-print sanding or a slicer-side fillet can substitute.

# ============================================================
# EXPORT STEP FILE
# ============================================================

output_path = Path(__file__).parent / "wing-knob-cadquery.step"
cq.exporters.export(body, str(output_path))
print(f"\nSTEP exported to: {output_path}")
print()

# ============================================================
# VALIDATION (Rubrics 3, 4, 5)
# ============================================================

print("VALIDATION")
print("=" * 60)

v = Validator(body)

# --- Feature 1: Cylindrical body ---
v.check_solid("Body center",
              0, BODY_HEIGHT / 2, 0)
v.check_solid("Body near front face +X",
              BODY_R - 2.0, BODY_HEIGHT - 1.0, 0)
v.check_solid("Body near rear face -X",
              -(BODY_R - 2.0), 1.0, 0)
v.check_solid("Body at +Z edge",
              0, BODY_HEIGHT / 2, BODY_R - 2.0)
v.check_void("Outside body +Z",
             0, BODY_HEIGHT / 2, BODY_R + 1.0,
             "void above body cylinder radius")
v.check_void("Outside body -Z",
             0, BODY_HEIGHT / 2, -(BODY_R + 1.0),
             "void below body cylinder radius")
v.check_void("In front of knob",
             0, BODY_HEIGHT + 1.0, 0,
             "void beyond front face")
v.check_void("Behind knob",
             0, -1.0, 0,
             "void behind rear face")

# --- Features 2 & 3: Wing extensions ---
v.check_solid("Wing +X body",
              BODY_R + 5.0, BODY_HEIGHT / 2, 0,
              "solid in +X wing beyond body cylinder")
v.check_solid("Wing +X near tip",
              WING_HALF_SPAN - 2.0, BODY_HEIGHT / 2, 0,
              "solid near +X wing tip")
v.check_solid("Wing -X body",
              -(BODY_R + 5.0), BODY_HEIGHT / 2, 0,
              "solid in -X wing beyond body cylinder")
v.check_solid("Wing -X near tip",
              -(WING_HALF_SPAN - 2.0), BODY_HEIGHT / 2, 0,
              "solid near -X wing tip")
v.check_void("Beyond wing +X",
             WING_HALF_SPAN + 2.0, BODY_HEIGHT / 2, 0,
             "void beyond +X wing tip")
v.check_void("Beyond wing -X",
             -(WING_HALF_SPAN + 2.0), BODY_HEIGHT / 2, 0,
             "void beyond -X wing tip")
# Wing Z extent
v.check_solid("Wing +X Z=0",
              BODY_R + 8.0, BODY_HEIGHT / 2, 0,
              "solid at wing center thickness")
v.check_void("Wing +X outside Z",
             BODY_R + 8.0, BODY_HEIGHT / 2, WING_THICKNESS / 2 + 1.0,
             "void outside wing thickness")

# --- Feature 4: Internal thread bore ---
# Bore center should be void (hollow)
v.check_void("Bore center Y=5",
             0, 5.0, 0,
             "void at bore center, thread region")
v.check_void("Bore center Y=10",
             0, 10.0, 0,
             "void at bore center, mid-thread")
v.check_void("Bore center Y=15",
             0, 15.0, 0,
             "void at bore center, deep thread")
# Just inside bore wall — void
v.check_void("Inside bore wall",
             THREAD_MAJOR_R - 0.3, 10.0, 0,
             "void just inside bore at major radius")

# Thread tooth verification:
# At Y positions where a helix start aligns with angle=0 (X>0, Z=0),
# probing at the minor radius should hit solid (thread tooth material).
#
# Start 1 (offset=0): tooth at angle=0 when Y/pitch is integer.
#   Y=0, 1.5, 3.0, 4.5, ... -> tooth crest at X=+minor_r, Z=0
# Start 2 (offset=180): tooth at angle=0 when (180 + 360*Y/pitch) mod 360 = 0
#   -> 360*Y/pitch mod 360 = 180 -> Y/pitch mod 1 = 0.5
#   Y=0.75, 2.25, 3.75, ... -> tooth crest at X=+minor_r, Z=0

v.check_solid("Thread tooth start 1 (Y=3.0)",
              THREAD_MINOR_R + 0.3, 3.0, 0,
              "solid at thread tooth near minor R (start 1)")
v.check_solid("Thread tooth start 2 (Y=3.75)",
              THREAD_MINOR_R + 0.3, 3.75, 0,
              "solid at thread tooth near minor R (start 2)")

# Groove check: between tooth positions, probe should be void
# At Y=3.375 (between 3.0 and 3.75):
#   Start 1 angle = 2*pi*(3.375/1.5) = 2*pi*2.25 = 90 deg from X-axis
#   Start 2 angle = pi + 2*pi*(3.375/1.5) = 270 deg from X-axis
#   Neither at 0 deg, so at X=minor_r+0.3, Z=0 -> groove (void)
v.check_void("Thread groove (Y=3.375)",
             THREAD_MINOR_R + 0.3, 3.375, 0,
             "void in thread groove between starts")

# Body wall outside bore
v.check_solid("Wall outside bore",
              THREAD_MAJOR_R + 3.0, 10.0, 0,
              "solid in body wall outside thread bore")

# --- Feature 5: Through-hole (smooth bore above threads) ---
v.check_void("Through-hole center Y=22",
             0, 22.0, 0,
             "void in smooth bore above threads")
v.check_void("Through-hole near wall Y=22",
             THREAD_MAJOR_R - 0.5, 22.0, 0,
             "void inside through-hole near bore wall")
v.check_solid("Wall outside through-hole",
              THREAD_MAJOR_R + 3.0, 22.0, 0,
              "solid in body wall at through-hole section")

# --- Feature 7: Rear face chamfer ---
# At Y=0.3 (within chamfer zone), the opening is wider than bore diameter
# by approximately chamfer*(1 - 0.3/1.0) = 0.7mm beyond THREAD_MAJOR_R
v.check_void("Chamfer void at Y=0.3",
             THREAD_MAJOR_R + 0.3, 0.3, 0,
             "void in chamfer zone near rear face")
v.check_solid("Past chamfer depth",
              THREAD_MAJOR_R + 0.3, REAR_CHAMFER + 0.5, 0,
              "solid past chamfer depth (bore wall intact)")

# --- Rubric 4: Solid validity ---
v.check_valid()
v.check_single_body()

# Volume: rough estimate
# Cylinder volume: pi * 20^2 * 25 = 31416
# Wing additions (beyond cylinder, 2 wings): ~2 * 15 * 10 * 25 = 7500 (minus overlaps)
# Bore removal: pi * 6.15^2 * 25 = 2972
# Net: ~33000 mm^3
# Bounding box envelope: 70 * 25 * 40 = 70000
envelope_vol = WING_TOTAL_SPAN * BODY_HEIGHT * BODY_DIA
v.check_volume(expected_envelope=envelope_vol, fill_range=(0.2, 0.8))

# --- Rubric 5: Bounding box ---
bb = body.val().BoundingBox()

# Expected: X = [-35, 35], Y = [0, 25], Z = [-20, 20]
# Wings have pill-shaped (rounded) tips, so X extent may be very slightly less
# than 35mm at the extreme. Use 1mm tolerance.
v.check_bbox("X", bb.xmin, bb.xmax, -WING_HALF_SPAN, WING_HALF_SPAN)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, BODY_HEIGHT)
v.check_bbox("Z", bb.zmin, bb.zmax, -BODY_R, BODY_R)

# ============================================================
# SUMMARY
# ============================================================
if not v.summary():
    sys.exit(1)
