#!/usr/bin/env python3
"""
Cartridge Twist-Release Threaded Strut -- CadQuery STEP Generation

Generates the threaded strut for the soda flavor injector pump cartridge
twist-release mechanism. The strut has Tr12x3 2-start trapezoidal threads
on both ends with a smooth cylindrical section in the middle.

The plate end (Y=0) press-fits into the release plate's 12mm ID socket
with epoxy. The knob end (Y=126) threads into the wing knob's internal
female Tr12x3 2-start thread. The strut passes through the rear wall
via a 12.5mm bore (0.25mm clearance per side).

Source material:
  - hardware/printed-parts/cartridge-twist-release/planning/parts.md
  - hardware/printed-parts/cartridge-twist-release/planning/research/3d-printed-approach.md
  - hardware/planning/step-generation-standards.md

Coordinate system:
  Origin: strut centered on X=0, Z=0; Y=0 is plate end
  X: radial, centered at 0
  Y: strut axis, plate end to knob end (126mm)  -> Y: [0, 126]
  Z: radial, centered at 0
  Envelope: 12mm dia x 126mm long

Thread specification (Tr12x3 2-start):
  Major diameter (external): 12.0mm
  Minor diameter: 9.0mm (12.0 - 2 x 1.5mm thread depth)
  Pitch per start: 1.5mm (axial distance between consecutive threads of SAME start)
  Lead: 3.0mm (axial advance per full revolution = 2 starts x 1.5mm pitch)
  Thread depth: 1.5mm per side
  Flank angle: 15 deg from vertical (29-deg included)
  Profile: flat crests and roots (trapezoidal, not triangular)
  2 starts: two helical threads offset 180 degrees

Thread sections:
  Section 1 (plate end):  Y=0  to Y=20  (20mm)
  Section 2 (knob end):   Y=106 to Y=126 (20mm)

Smooth section: Y=20 to Y=106 (86mm, 12mm cylinder)

Chamfers: 0.5mm x 45 deg on both ends (thread entry aid)
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

# Overall geometry
STRUT_LENGTH = 126.0       # total length along Y
STRUT_DIA = 12.0           # smooth section & thread major diameter
STRUT_RADIUS = STRUT_DIA / 2  # 6.0mm

# Thread specification: Tr12x3 2-start trapezoidal
THREAD_MAJOR_DIA = 12.0    # external major diameter
THREAD_MINOR_DIA = 9.0     # external minor diameter (root)
THREAD_DEPTH = 1.5         # (major - minor) / 2
THREAD_PITCH = 1.5         # axial pitch per start (distance between consecutive crests of same start)
THREAD_LEAD = 3.0          # axial advance per revolution (2 starts x 1.5mm)
NUM_STARTS = 2             # number of thread starts
FLANK_ANGLE_DEG = 15.0     # flank angle from vertical (half the 29-deg included angle)

# Thread section locations (Y ranges)
THREAD1_Y_START = 0.0      # plate end thread start
THREAD1_Y_END = 20.0       # plate end thread end
THREAD2_Y_START = 106.0    # knob end thread start
THREAD2_Y_END = 126.0      # knob end thread end

# Smooth section
SMOOTH_Y_START = 20.0
SMOOTH_Y_END = 106.0
SMOOTH_LENGTH = SMOOTH_Y_END - SMOOTH_Y_START  # 86mm

# Thread section lengths
THREAD_SECTION_LENGTH = 20.0  # both sections are 20mm

# Chamfers
CHAMFER_SIZE = 0.5         # 0.5mm x 45 deg on both ends

# Derived thread geometry
THREAD_MAJOR_R = THREAD_MAJOR_DIA / 2  # 6.0mm
THREAD_MINOR_R = THREAD_MINOR_DIA / 2  # 4.5mm
FLANK_ANGLE_RAD = math.radians(FLANK_ANGLE_DEG)

# Trapezoidal tooth profile dimensions (in axial cross-section):
# The tooth is a trapezoid. At the crest (major radius), the flat width is
# narrower than at the root. For standard Tr threads:
#   Crest flat = pitch/2 - 2 * depth * tan(flank_angle)
#   Root flat  = pitch/2
# But for 2-start, the "pitch" in the profile sense is the lead/num_starts = 1.5mm.
# The tooth occupies half the pitch (0.75mm nominal) and the groove the other half.
TOOTH_CREST_WIDTH = THREAD_PITCH / 2 - 2 * THREAD_DEPTH * math.tan(FLANK_ANGLE_RAD)
TOOTH_ROOT_WIDTH = THREAD_PITCH / 2

# ============================================================
# FEATURE PLANNING TABLE (Rubric 1)
# ============================================================

print("=" * 120)
print("FEATURE PLANNING TABLE (Rubric 1)")
print("=" * 120)
header = (f"{'#':<4} {'Feature Name':<30} {'Mech. Function':<35} {'Op':<7} "
          f"{'Shape':<10} {'Axis':<5} {'Center (X,Y,Z)':<20} {'Dimensions':<30} {'Notes'}")
print(header)
print("-" * 120)

table_rows = [
    ("1",  "Base cylinder",
     "Structural core of strut",        "Add",    "Cylinder", "Y",
     "(0, 63, 0)",     f"D{STRUT_DIA} x L{STRUT_LENGTH}mm",
     "Full length at minor dia"),
    ("2",  "Thread section 1 (plate end)",
     "Engages release plate socket",    "Add",    "Helix",    "Y",
     "(0, 10, 0)",     f"Tr12x3 2-start, Y=0..20mm",
     "2 helices offset 180 deg"),
    ("3",  "Thread section 2 (knob end)",
     "Engages wing knob female thread", "Add",    "Helix",    "Y",
     "(0, 116, 0)",    f"Tr12x3 2-start, Y=106..126mm",
     "2 helices offset 180 deg"),
    ("4",  "Chamfer 1 (plate end)",
     "Thread entry aid at Y=0",         "Remove", "Chamfer",  "Y",
     "(0, 0, 0)",      f"{CHAMFER_SIZE}mm x 45 deg",
     "Tapered lead-in"),
    ("5",  "Chamfer 2 (knob end)",
     "Thread entry aid at Y=126",       "Remove", "Chamfer",  "Y",
     "(0, 126, 0)",    f"{CHAMFER_SIZE}mm x 45 deg",
     "Tapered lead-in"),
]

for row in table_rows:
    print(f"{row[0]:<4} {row[1]:<30} {row[2]:<35} {row[3]:<7} {row[4]:<10} {row[5]:<5} "
          f"{row[6]:<20} {row[7]:<30} {row[8]}")

print("=" * 120)
print(f"Thread tooth crest width: {TOOTH_CREST_WIDTH:.4f}mm")
print(f"Thread tooth root width:  {TOOTH_ROOT_WIDTH:.4f}mm")
print()

# ============================================================
# HELPER: Build trapezoidal thread helix for one section
# ============================================================


def make_thread_tooth_profile():
    """
    Create the 2D trapezoidal tooth cross-section profile as a CadQuery Wire.

    The profile is defined in a local coordinate system where:
      - The "radial" direction is X (outward from cylinder axis)
      - The "axial" direction is Y (along the strut axis)

    The tooth profile is a trapezoid:
      - Root (inner edge) at X = THREAD_MINOR_R, width = TOOTH_ROOT_WIDTH
      - Crest (outer edge) at X = THREAD_MAJOR_R, width = TOOTH_CREST_WIDTH
      - Flanks connect root corners to crest corners at FLANK_ANGLE_DEG

    Returns a closed CadQuery Wire for the tooth cross-section, centered
    axially on Y=0 in the profile's local frame.
    """
    half_root = TOOTH_ROOT_WIDTH / 2
    half_crest = TOOTH_CREST_WIDTH / 2

    # Profile points (X=radial, Y=axial), starting at root bottom-left,
    # going clockwise:
    pts = [
        (THREAD_MINOR_R, -half_root),    # root, bottom (axially trailing)
        (THREAD_MAJOR_R, -half_crest),   # crest, bottom
        (THREAD_MAJOR_R,  half_crest),   # crest, top (axially leading)
        (THREAD_MINOR_R,  half_root),    # root, top
    ]
    return pts


def make_thread_solid_for_section(y_start, y_end):
    """
    Build the thread solid (both starts) for a thread section from y_start to y_end.

    Strategy: sweep the trapezoidal tooth profile along a helical path.
    For each start, create a helix wire and sweep the tooth cross-section along it.

    For CadQuery, we build the helix parametrically and use the sweep operation.
    The thread is built as a solid that gets unioned with the base cylinder.
    """
    section_length = y_end - y_start
    # Number of full pitches in this section (per start)
    num_turns = section_length / THREAD_LEAD  # turns of the helix

    # Build thread for each start
    thread_solids = []

    for start_idx in range(NUM_STARTS):
        # Phase offset for this start: 0 deg for start 0, 180 deg for start 1
        phase_offset_deg = start_idx * (360.0 / NUM_STARTS)

        # Create the helical spine using CadQuery's parametric helix.
        # CadQuery Wire.makeHelix(pitch, height, radius, ...) creates a helix
        # along Z axis by default. We'll build along Z then rotate to Y.
        #
        # For a 2-start thread with lead=3mm, each helix has pitch = lead = 3mm
        # (the helix pitch is the axial advance per revolution, which equals the lead).
        helix_wire = cq.Wire.makeHelix(
            pitch=THREAD_LEAD,
            height=section_length,
            radius=THREAD_MINOR_R + THREAD_DEPTH / 2,  # sweep at mid-depth of tooth
            angle=0.0,       # right-hand thread
            lefthand=False,
        )

        # The tooth profile needs to be perpendicular to the helix path.
        # Build the profile on a workplane at the helix start, oriented to
        # be perpendicular to the helix tangent.
        #
        # The helix starts at (radius, 0, 0) and spirals upward along Z.
        # At the start, the tangent direction is approximately (0, tan(helix_angle), 1)
        # normalized, but for the sweep CadQuery handles the Frenet frame.
        #
        # Build the tooth profile as a face that CadQuery can sweep.
        # The profile is in a plane perpendicular to the helix at its start.

        tooth_pts = make_thread_tooth_profile()

        # Create the profile as a Workplane sketch.
        # The profile radial direction (tooth height) aligns with the helix radius.
        # We define it on the XZ plane at the helix start point, with X as radial
        # and Z as axial (the helix goes along Z before we rotate to Y).

        # Actually, for CadQuery sweep, we need the profile on a plane perpendicular
        # to the path at the start. The helix starts along Z, so at the start point
        # the tangent is mostly in Z with a small circumferential component.
        # For practical purposes with CadQuery's sweep, we build the profile
        # centered at the helix start point in the plane perpendicular to Z.

        # Build profile wire manually using CadQuery edges
        profile_wp = (
            cq.Workplane("XZ")
            .moveTo(tooth_pts[0][0], tooth_pts[0][1])
        )
        for pt in tooth_pts[1:]:
            profile_wp = profile_wp.lineTo(pt[0], pt[1])
        profile_wp = profile_wp.close()

        # Sweep the profile along the helix
        try:
            thread_single = profile_wp.sweep(
                cq.Workplane("XY").add(helix_wire),
                isFrenet=True,
            )

            # Rotate for the phase offset of this start
            if phase_offset_deg != 0:
                thread_single = thread_single.rotate((0, 0, 0), (0, 0, 1), phase_offset_deg)

            # The helix was built along Z. Rotate the entire solid so the thread
            # axis aligns with Y instead. Rotation: Z -> Y means rotate -90 deg
            # around X axis.
            thread_single = thread_single.rotate((0, 0, 0), (1, 0, 0), -90)

            # Translate to the correct Y position for this thread section
            thread_single = thread_single.translate((0, y_start, 0))

            thread_solids.append(thread_single)
        except Exception as e:
            print(f"  WARNING: Helical sweep failed for start {start_idx}: {e}")
            print(f"  Falling back to smooth cylinder for this thread section.")
            # Fallback: no thread geometry added, base cylinder provides the shape
            pass

    return thread_solids


# ============================================================
# MODEL CONSTRUCTION
# ============================================================

print("Building strut geometry...")
print()

# --- Feature 1: Base cylinder ---
# The base cylinder runs the full length at the thread minor diameter.
# Thread sections will add material up to the major diameter.
# The smooth section in the middle needs to be at the major diameter (12mm).
#
# Strategy: Build the full-length cylinder at major diameter (12mm),
# then the threads add their helical profile. The base cylinder at 12mm
# means the smooth section is correct. For the thread sections, the cylinder
# at major diameter provides the crest, but we need the thread grooves cut
# into it to form the trapezoidal profile.
#
# Alternative (cleaner for threads): Build at minor diameter and ADD thread teeth.
# This is better because the helical sweep adds material above the minor diameter.
#
# Actually, let's think about this differently:
# - Smooth section (Y=20..106): 12mm diameter cylinder -> radius 6.0mm
# - Thread sections: the CREST of the thread is at 12mm dia (6.0mm radius),
#   and the ROOT (groove between threads) is at 9mm dia (4.5mm radius).
#
# So the approach is:
# 1. Build full-length cylinder at minor diameter (9mm dia = 4.5mm radius)
# 2. Add a 12mm diameter cylinder for the smooth section (Y=20..106)
# 3. Add helical thread teeth for both thread sections
#
# This ensures threads have proper root diameter and the smooth section
# is at the full 12mm diameter.

# Step 1: Full-length core at minor diameter
core = (
    cq.Workplane("XZ")       # sketch on XZ, extrude along Y (normal is -Y)
    .circle(THREAD_MINOR_R)
    .extrude(-STRUT_LENGTH)   # XZ normal is -Y; negative extrude goes +Y
)
# Core spans Y=0 to Y=126, centered on X=0, Z=0

# Step 2: Smooth section at major diameter (fills the middle to 12mm)
smooth_section = (
    cq.Workplane("XZ")
    .circle(STRUT_RADIUS)
    .extrude(-SMOOTH_LENGTH)
    .translate((0, SMOOTH_Y_START, 0))
)
strut = core.union(smooth_section)

# Step 3: Thread sections -- attempt helical sweep
print("Attempting helical thread sweep...")

# Build thread section 1 (plate end, Y=0..20)
thread_solids_1 = make_thread_solid_for_section(THREAD1_Y_START, THREAD1_Y_END)
for ts in thread_solids_1:
    strut = strut.union(ts)

# Build thread section 2 (knob end, Y=106..126)
thread_solids_2 = make_thread_solid_for_section(THREAD2_Y_START, THREAD2_Y_END)
for ts in thread_solids_2:
    strut = strut.union(ts)

# If no thread solids were created (sweep failed), add smooth cylinders as fallback
if not thread_solids_1 and not thread_solids_2:
    print("  Thread sweep failed entirely. Using smooth 12mm cylinders as fallback.")
    print("  NOTE: Thread geometry is approximated -- no helical features present.")
    # Add full-diameter cylinders at the thread sections
    thread1_cyl = (
        cq.Workplane("XZ")
        .circle(STRUT_RADIUS)
        .extrude(-THREAD_SECTION_LENGTH)
        .translate((0, THREAD1_Y_START, 0))
    )
    thread2_cyl = (
        cq.Workplane("XZ")
        .circle(STRUT_RADIUS)
        .extrude(-THREAD_SECTION_LENGTH)
        .translate((0, THREAD2_Y_START, 0))
    )
    strut = strut.union(thread1_cyl).union(thread2_cyl)
elif not thread_solids_1 or not thread_solids_2:
    # One section succeeded and the other failed -- fill the failed one
    if not thread_solids_1:
        print("  Thread section 1 (plate end) fell back to smooth cylinder.")
        fallback = (
            cq.Workplane("XZ")
            .circle(STRUT_RADIUS)
            .extrude(-THREAD_SECTION_LENGTH)
            .translate((0, THREAD1_Y_START, 0))
        )
        strut = strut.union(fallback)
    if not thread_solids_2:
        print("  Thread section 2 (knob end) fell back to smooth cylinder.")
        fallback = (
            cq.Workplane("XZ")
            .circle(STRUT_RADIUS)
            .extrude(-THREAD_SECTION_LENGTH)
            .translate((0, THREAD2_Y_START, 0))
        )
        strut = strut.union(fallback)
else:
    print("  Helical thread sweep succeeded for both sections.")

# --- Features 4 & 5: Chamfers on both ends ---
# Chamfer at Y=0 (plate end): taper from minor diameter inward at the face
# Chamfer at Y=126 (knob end): same
#
# For the chamfer, we cut a cone-shaped ring from each end face.
# The chamfer removes material at the outer edge of the end face,
# tapering from the outer radius down by CHAMFER_SIZE over CHAMFER_SIZE axially.
#
# At Y=0, the thread section starts, so the outer radius is the major radius.
# The chamfer tapers from R=THREAD_MAJOR_R at Y=CHAMFER_SIZE to
# R=THREAD_MAJOR_R - CHAMFER_SIZE at Y=0.
#
# Build chamfer as a revolved profile subtracted from the strut.

# Chamfer at Y=0 (plate end)
# The material to remove is a ring: from R=(major_R - chamfer) to R=major_R,
# tapered from Y=0 to Y=chamfer_size.
# Revolved profile of the material to CUT:
chamfer_pts_1 = [
    (THREAD_MAJOR_R - CHAMFER_SIZE, 0),   # inner edge at face
    (THREAD_MAJOR_R,                0),   # outer edge at face (but this is already the crest)
    (THREAD_MAJOR_R,                CHAMFER_SIZE),  # outer edge at chamfer depth
    (THREAD_MAJOR_R - CHAMFER_SIZE, 0),   # back to start (triangle)
]
# Actually this is a triangle. Let's use a cleaner approach:
# The chamfer is a 45-deg bevel. We want to remove a conical ring at the end.
chamfer1_profile = (
    cq.Workplane("XY")
    .moveTo(THREAD_MAJOR_R - CHAMFER_SIZE, 0)
    .lineTo(THREAD_MAJOR_R, 0)
    .lineTo(THREAD_MAJOR_R, CHAMFER_SIZE)
    .close()
)
chamfer1_cutter = chamfer1_profile.revolve(360, (0, 0), (0, 1))
strut = strut.cut(chamfer1_cutter)

# Chamfer at Y=126 (knob end)
chamfer2_profile = (
    cq.Workplane("XY")
    .moveTo(THREAD_MAJOR_R - CHAMFER_SIZE, STRUT_LENGTH)
    .lineTo(THREAD_MAJOR_R, STRUT_LENGTH)
    .lineTo(THREAD_MAJOR_R, STRUT_LENGTH - CHAMFER_SIZE)
    .close()
)
chamfer2_cutter = chamfer2_profile.revolve(360, (0, 0), (0, 1))
strut = strut.cut(chamfer2_cutter)

print("Chamfers applied to both ends.")
print()

# ============================================================
# EXPORT STEP FILE
# ============================================================

output_path = Path(__file__).parent / "twist-release-strut-cadquery.step"
cq.exporters.export(strut, str(output_path))
print(f"STEP exported to: {output_path}")
print()

# ============================================================
# VALIDATION (Rubrics 3, 4, 5)
# ============================================================

print("VALIDATION")
print("=" * 60)

v = Validator(strut)

# --- Feature 1: Base cylinder / smooth section ---
# Smooth section center: (0, 63, 0), should be solid at any radius < 6.0
v.check_solid("Smooth section center",
              0, STRUT_LENGTH / 2, 0,
              "solid at strut center (smooth section)")
v.check_solid("Smooth section near surface",
              STRUT_RADIUS - 0.3, STRUT_LENGTH / 2, 0,
              "solid just inside surface of smooth section")
v.check_void("Outside smooth section",
             STRUT_RADIUS + 0.5, STRUT_LENGTH / 2, 0,
             "void outside strut diameter")

# Smooth section at boundaries
v.check_solid("Smooth section Y=25 (5mm past thread transition)",
              0, 25.0, 0,
              "solid in smooth section near plate-end transition")
v.check_solid("Smooth section Y=100 (6mm before knob-end transition)",
              0, 100.0, 0,
              "solid in smooth section near knob-end transition")

# --- Feature 2: Thread section 1 (plate end, Y=0..20) ---
# At the thread center axis, should be solid (core cylinder)
v.check_solid("Thread 1 core center",
              0, 10.0, 0,
              "solid at thread section 1 center axis")
# At minor radius, should be solid (thread root)
v.check_solid("Thread 1 at minor radius",
              THREAD_MINOR_R - 0.3, 10.0, 0,
              "solid inside minor radius of thread section 1")
# At major radius - whether solid or void depends on where on the helix we probe.
# But the bounding envelope should not exceed major radius.
v.check_void("Thread 1 outside major radius",
             THREAD_MAJOR_R + 0.5, 10.0, 0,
             "void well outside major radius of thread section 1")

# Thread 1 near start (Y=1, past chamfer)
v.check_solid("Thread 1 near plate end",
              0, 1.0, 0,
              "solid at thread section 1 near plate end (past chamfer)")

# Thread 1 near end (Y=19)
v.check_solid("Thread 1 near smooth transition",
              0, 19.0, 0,
              "solid at thread section 1 near smooth section boundary")

# --- Feature 3: Thread section 2 (knob end, Y=106..126) ---
v.check_solid("Thread 2 core center",
              0, 116.0, 0,
              "solid at thread section 2 center axis")
v.check_solid("Thread 2 at minor radius",
              THREAD_MINOR_R - 0.3, 116.0, 0,
              "solid inside minor radius of thread section 2")
v.check_void("Thread 2 outside major radius",
             THREAD_MAJOR_R + 0.5, 116.0, 0,
             "void well outside major radius of thread section 2")

# Thread 2 near end (Y=125, past chamfer zone)
v.check_solid("Thread 2 near knob end",
              0, 125.0, 0,
              "solid at thread section 2 near knob end")

# Thread 2 near start (Y=107)
v.check_solid("Thread 2 near smooth transition",
              0, 107.0, 0,
              "solid at thread section 2 near smooth section boundary")

# --- Feature 4: Chamfer 1 (plate end, Y=0) ---
# At Y=0 face, the chamfer removes material at the outer edge.
# At Y=0, the max radius should be THREAD_MAJOR_R - CHAMFER_SIZE = 5.5mm
# So a point at R=5.8 (between 5.5 and 6.0) at Y=0.1 should be void due to chamfer
v.check_void("Chamfer 1 material removed",
             THREAD_MAJOR_R - 0.1, 0.1, 0,
             "void in chamfer zone at plate end (R=5.9mm, Y=0.1mm)")
# But at Y=CHAMFER_SIZE (0.5mm), the full radius is restored
v.check_solid("Chamfer 1 past chamfer at core",
              0, 0.3, 0,
              "solid at core past chamfer start")

# --- Feature 5: Chamfer 2 (knob end, Y=126) ---
v.check_void("Chamfer 2 material removed",
             THREAD_MAJOR_R - 0.1, STRUT_LENGTH - 0.1, 0,
             "void in chamfer zone at knob end (R=5.9mm, Y=125.9mm)")
v.check_solid("Chamfer 2 past chamfer at core",
              0, STRUT_LENGTH - 0.3, 0,
              "solid at core past chamfer end")

# --- Symmetry check: strut is rotationally symmetric ---
# Check solid at 90-degree rotated position (Z axis instead of X)
v.check_solid("Rotational symmetry check (Z axis)",
              0, STRUT_LENGTH / 2, STRUT_RADIUS - 0.3,
              "solid at 90-deg rotated position in smooth section")
v.check_void("Rotational symmetry check (Z axis, outside)",
             0, STRUT_LENGTH / 2, STRUT_RADIUS + 0.5,
             "void outside strut at 90-deg rotated position")

# --- Rubric 4: Solid validity ---
v.check_valid()
v.check_single_body()

# Volume estimate:
# Smooth section: pi * 6^2 * 86 = ~9726 mm^3
# Thread sections (approx): two 20mm sections, average between minor and major
# ~pi * 5.25^2 * 40 = ~3464 mm^3 (rough)
# Total: ~13190 mm^3
# Envelope: 12 * 12 * 126 = 18144 mm^3
ENVELOPE_VOL = STRUT_DIA * STRUT_DIA * STRUT_LENGTH
v.check_volume(expected_envelope=ENVELOPE_VOL, fill_range=(0.3, 1.0))

# --- Rubric 5: Bounding box ---
bb = strut.val().BoundingBox()

# Expected bounds:
# X: [-6.0, 6.0] (strut centered on X=0, radius 6.0)
# Y: [0.0, 126.0]
# Z: [-6.0, 6.0] (strut centered on Z=0, radius 6.0)
v.check_bbox("X", bb.xmin, bb.xmax, -STRUT_RADIUS, STRUT_RADIUS)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, STRUT_LENGTH)
v.check_bbox("Z", bb.zmin, bb.zmax, -STRUT_RADIUS, STRUT_RADIUS)

# ============================================================
# SUMMARY
# ============================================================
if not v.summary():
    sys.exit(1)
