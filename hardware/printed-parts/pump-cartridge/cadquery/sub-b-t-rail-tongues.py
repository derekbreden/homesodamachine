"""
Sub-B T-Rail Tongues — CadQuery Generation Script

Two T-profile rail tongues as standalone solids for boolean union
with the tray box shell (Sub-A). Left tongue on X=0 face at Z=54,
right tongue on X=160 face at Z=18. Each is a constant T cross-section
extruded 155mm along Y, with 1mm fillets at cap-to-wall junctions.

Coordinate system:
  Origin: rear-left-bottom corner of the tray outer envelope
  X: width, 0 (left wall outer face) .. 160 (right wall outer face)
  Y: depth, 0 (dock-facing rear face) .. 155 (user-facing front edge)
  Z: height, 0 (bottom of floor) .. 72 (top of side walls)
  Tongue envelope: X: -4..164, Y: 0..155, Z: per tongue

Feature Planning Table:
| # | Feature Name       | Function                          | Op  | Shape       | Axis | Center (X,Y,Z)     | Dimensions                    | Notes                          |
|---|--------------------|-----------------------------------|-----|-------------|------|---------------------|-------------------------------|--------------------------------|
| 1 | Left T-tongue      | Guide rail + X/Z constraint       | Add | T-extrusion | Y    | (-2, 77.5, 54)      | 4x6mm T-profile, 155mm long   | Protrudes -X from X=0 wall     |
| 2 | Right T-tongue     | Guide rail + X/Z constraint       | Add | T-extrusion | Y    | (162, 77.5, 18)     | 4x6mm T-profile, 155mm long   | Protrudes +X from X=160 wall   |
| 3 | Left cap-wall fillet| Stress relief + printability      | Mod | Fillet      | Y    | (0, -, 51/57)       | R=1.0mm                       | At re-entrant cap-wall corners |
| 4 | Right cap-wall fillet| Stress relief + printability     | Mod | Fillet      | Y    | (160, -, 15/21)     | R=1.0mm                       | At re-entrant cap-wall corners |
"""

import sys
from pathlib import Path

# Add tools/ to path for step_validate
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq
from step_validate import Validator

# =====================================================================
# Parameters from spec
# =====================================================================

# T-profile cross-section
CAP_WIDTH_Z = 6.0       # Cap extent in Z
STEM_HEIGHT_Z = 3.0     # Stem extent in Z
TOTAL_PROTRUSION_X = 4.0 # How far tongue sticks out from wall
CAP_THICKNESS_X = 2.0   # Cap portion thickness in X
STEM_DEPTH_X = 2.0      # Stem depth in X (wall to cap)
FLANGE_OVERHANG = 1.5   # (CAP_WIDTH_Z - STEM_HEIGHT_Z) / 2

# Extrusion
EXTRUDE_Y = 155.0       # Full tray depth

# Left tongue: protrudes -X from X=0, centered at Z=54
LEFT_WALL_X = 0.0
LEFT_CENTER_Z = 54.0

# Right tongue: protrudes +X from X=160, centered at Z=18
RIGHT_WALL_X = 160.0
RIGHT_CENTER_Z = 18.0

# Fillet
FILLET_R = 1.0

# =====================================================================
# Helper: build a single T-tongue as a standalone solid
# =====================================================================

def make_tongue(wall_x, center_z, direction):
    """
    Build a T-profile tongue extruded along Y.

    Args:
        wall_x: X coordinate of the wall face
        center_z: Z center of the tongue
        direction: +1 for +X protrusion, -1 for -X protrusion
    """
    # Compute Z bounds
    cap_z_min = center_z - CAP_WIDTH_Z / 2      # bottom of cap
    cap_z_max = center_z + CAP_WIDTH_Z / 2      # top of cap
    stem_z_min = center_z - STEM_HEIGHT_Z / 2   # bottom of stem
    stem_z_max = center_z + STEM_HEIGHT_Z / 2   # top of stem

    # Compute X bounds
    # direction=-1: tongue goes from wall_x to wall_x - 4
    # direction=+1: tongue goes from wall_x to wall_x + 4
    stem_x_tip = wall_x + direction * STEM_DEPTH_X
    cap_x_tip = wall_x + direction * TOTAL_PROTRUSION_X

    # Build T-profile as XZ polygon points (spec points A-H)
    # Going counterclockwise for the left tongue, adapted per direction
    if direction == -1:
        # Left tongue: A(0,52.5) B(-2,52.5) C(-2,51) D(-4,51)
        #              E(-4,57) F(-2,57) G(-2,55.5) H(0,55.5)
        pts = [
            (wall_x,     stem_z_min),   # A: stem root, bottom
            (stem_x_tip, stem_z_min),   # B: stem tip, bottom
            (stem_x_tip, cap_z_min),    # C: cap inner, bottom
            (cap_x_tip,  cap_z_min),    # D: cap tip, bottom
            (cap_x_tip,  cap_z_max),    # E: cap tip, top
            (stem_x_tip, cap_z_max),    # F: cap inner, top
            (stem_x_tip, stem_z_max),   # G: stem tip, top
            (wall_x,     stem_z_max),   # H: stem root, top
        ]
    else:
        # Right tongue: A(160,16.5) B(162,16.5) C(162,15) D(164,15)
        #               E(164,21) F(162,21) G(162,19.5) H(160,19.5)
        pts = [
            (wall_x,     stem_z_min),   # A
            (stem_x_tip, stem_z_min),   # B
            (stem_x_tip, cap_z_min),    # C
            (cap_x_tip,  cap_z_min),    # D
            (cap_x_tip,  cap_z_max),    # E
            (stem_x_tip, cap_z_max),    # F
            (stem_x_tip, stem_z_max),   # G
            (wall_x,     stem_z_max),   # H
        ]

    # Create the T-profile on XZ plane and extrude along Y
    # CadQuery XZ workplane: sketch X maps to world X, sketch Y maps to world Z
    # Normal is -Y, so positive extrude goes in -Y direction
    # We want Y=0..155, so we place the workplane at Y=155 and extrude 155mm
    # (positive extrude on XZ at Y=155 goes toward -Y, ending at Y=0)
    tongue = (
        cq.Workplane("XZ")
        .workplane(offset=-EXTRUDE_Y)  # Move workplane to Y=155 (offset is along -Y normal)
        .moveTo(pts[0][0], pts[0][1])
    )
    for p in pts[1:]:
        tongue = tongue.lineTo(p[0], p[1])
    tongue = tongue.close().extrude(EXTRUDE_Y)
    # Extrude from Y=155 in -Y direction (workplane normal) => Y=155..0
    # Actually: XZ workplane normal is -Y. offset=-155 moves it to Y=155.
    # extrude(155) goes along -Y normal * 155 => from Y=155 toward Y=0. Good.

    return tongue


# =====================================================================
# Build tongues
# =====================================================================

print("Building left T-tongue...")
left_tongue = make_tongue(LEFT_WALL_X, LEFT_CENTER_Z, direction=-1)

print("Building right T-tongue...")
right_tongue = make_tongue(RIGHT_WALL_X, RIGHT_CENTER_Z, direction=+1)

# =====================================================================
# Apply fillets at cap-to-wall junctions
# =====================================================================

# For the left tongue, the re-entrant corners where the cap flanges meet
# the wall plane (X=0) are the edges at:
#   - Bottom: where cap face at Z=51 meets wall at X=0 (edge along Y at Z=51, X=0)
#     Actually the re-entrant corners are at D-E face meeting the wall.
#     The spec says: "at the two re-entrant corners where the cap flanges
#     meet the wall plane" — these are at (X=0, Z=51) and (X=0, Z=57)
#     for the left tongue.
#
# But since these are standalone tongues (not attached to wall yet),
# the "wall face" edges are at X=0 for the left tongue. The re-entrant
# corners in the T-profile are between the stem and cap flanges:
# Points C-B junction (bottom) and F-G junction (top).
# These are the inner corners of the T at X=-2.
#
# Per spec section 5.6: "1.0 mm fillet at the edges where the cap meets
# the wall face at X=0" — specifically at points between cap outer corners
# and the wall. Looking at the profile, the re-entrant edges that run
# along Y are at:
#   Left: (X=0, Z=51..52.5 region) and (X=0, Z=55.5..57 region)
#   But actually, there's no edge at X=0, Z=51 — the profile goes
#   H(0,55.5)->A(0,52.5) which is the wall-face closing edge.
#
# Re-reading spec: "at the two re-entrant corners where the cap flanges
# meet the wall plane" — in the standalone tongue, these would be the
# internal corners of the T shape. The T has re-entrant (concave) corners
# at B(X=-2, Z=52.5) and G(X=-2, Z=55.5) for the left tongue.
# These are the inside corners where stem meets cap.
#
# Since we're building standalone tongues, let's fillet those inner T corners.

print("Applying fillets to left tongue...")
# Select the 4 re-entrant edges of the T-profile (2 inner corners, each running along Y)
# For left tongue: inner corners at (-2, Y, 52.5) and (-2, Y, 55.5)
left_tongue = (
    left_tongue
    .edges("|Y")
    .edges(
        cq.selectors.BoxSelector(
            (-2.1, -0.1, 52.4), (-1.9, 155.1, 52.6)
        )
    )
    .fillet(FILLET_R)
)

left_tongue = (
    left_tongue
    .edges("|Y")
    .edges(
        cq.selectors.BoxSelector(
            (-2.1, -0.1, 55.4), (-1.9, 155.1, 55.6)
        )
    )
    .fillet(FILLET_R)
)

print("Applying fillets to right tongue...")
# Right tongue inner corners at (162, Y, 16.5) and (162, Y, 19.5)
right_tongue = (
    right_tongue
    .edges("|Y")
    .edges(
        cq.selectors.BoxSelector(
            (161.9, -0.1, 16.4), (162.1, 155.1, 16.6)
        )
    )
    .fillet(FILLET_R)
)

right_tongue = (
    right_tongue
    .edges("|Y")
    .edges(
        cq.selectors.BoxSelector(
            (161.9, -0.1, 19.4), (162.1, 155.1, 19.6)
        )
    )
    .fillet(FILLET_R)
)

# =====================================================================
# Combine into a single compound for export
# =====================================================================

print("Combining tongues...")
result = left_tongue.union(right_tongue)

# =====================================================================
# Export STEP
# =====================================================================

output_path = str(Path(__file__).parent / "sub-b-t-rail-tongues.step")
print(f"Exporting STEP to {output_path}...")
cq.exporters.export(result, output_path)
print("STEP exported.")

# =====================================================================
# Validation
# =====================================================================

print("\n--- VALIDATION ---\n")

v = Validator(result)

# --- Feature 1: Left T-tongue ---
# Solid at stem center: (-1, 77.5, 54)
v.check_solid("Left tongue stem center", -1.0, 77.5, 54.0, "solid at left stem center")
# Solid at cap center: (-3, 77.5, 54)
v.check_solid("Left tongue cap center", -3.0, 77.5, 54.0, "solid at left cap center")
# Solid at cap top: (-3, 77.5, 56.5)
v.check_solid("Left tongue cap top", -3.0, 77.5, 56.5, "solid at left cap top region")
# Solid at cap bottom: (-3, 77.5, 51.5)
v.check_solid("Left tongue cap bottom", -3.0, 77.5, 51.5, "solid at left cap bottom region")
# Void above cap: (-3, 77.5, 57.5)
v.check_void("Left tongue above cap", -3.0, 77.5, 57.5, "void above left cap")
# Void below cap: (-3, 77.5, 50.5)
v.check_void("Left tongue below cap", -3.0, 77.5, 50.5, "void below left cap")
# Void beyond tip: (-4.5, 77.5, 54)
v.check_void("Left tongue beyond tip", -4.5, 77.5, 54.0, "void beyond left tongue tip")
# Void in flange gap (above stem, below cap top): stem top is 55.5, cap inner at -2
# At (-1, 77.5, 56) — this is in the flange overhang region but inside the stem X range
# Should be void because stem only goes to Z=55.5, and cap starts at X=-2
v.check_void("Left flange gap top", -0.5, 77.5, 56.5, "void in top flange gap (stem side)")
v.check_void("Left flange gap bottom", -0.5, 77.5, 51.5, "void in bottom flange gap (stem side)")
# Solid at Y start: (-3, 0.5, 54)
v.check_solid("Left tongue Y start", -3.0, 0.5, 54.0, "solid at left tongue Y=0 end")
# Solid at Y end: (-3, 154.5, 54)
v.check_solid("Left tongue Y end", -3.0, 154.5, 54.0, "solid at left tongue Y=155 end")
# Void beyond Y: (-3, -0.5, 54)
v.check_void("Left tongue before Y=0", -3.0, -0.5, 54.0, "void before Y=0")
v.check_void("Left tongue after Y=155", -3.0, 155.5, 54.0, "void after Y=155")

# --- Feature 2: Right T-tongue ---
v.check_solid("Right tongue stem center", 161.0, 77.5, 18.0, "solid at right stem center")
v.check_solid("Right tongue cap center", 163.0, 77.5, 18.0, "solid at right cap center")
v.check_solid("Right tongue cap top", 163.0, 77.5, 20.5, "solid at right cap top region")
v.check_solid("Right tongue cap bottom", 163.0, 77.5, 15.5, "solid at right cap bottom region")
v.check_void("Right tongue above cap", 163.0, 77.5, 21.5, "void above right cap")
v.check_void("Right tongue below cap", 163.0, 77.5, 14.5, "void below right cap")
v.check_void("Right tongue beyond tip", 164.5, 77.5, 18.0, "void beyond right tongue tip")
v.check_void("Right flange gap top", 160.5, 77.5, 20.5, "void in top flange gap (stem side)")
v.check_void("Right flange gap bottom", 160.5, 77.5, 15.5, "void in bottom flange gap (stem side)")
v.check_solid("Right tongue Y start", 163.0, 0.5, 18.0, "solid at right tongue Y=0 end")
v.check_solid("Right tongue Y end", 163.0, 154.5, 18.0, "solid at right tongue Y=155 end")

# --- Feature 3 & 4: Fillets ---
# After filleting the inner T corners, the sharp corner at (-2, Y, 52.5) is
# replaced by a smooth curve. Check that the corner point is now void (material removed by fillet).
# The fillet R=1mm removes material at the concave corner. A point at the exact corner
# diagonal offset of ~0.3mm should still be solid (within fillet curve), but the very
# corner itself at the intersection of the two faces should be rounded.
# At (-2, 77.5, 52.5): this is right at the inner corner. With a 1mm fillet,
# this point might still be solid depending on exact geometry. Let's check a point
# that would only be solid if the fillet exists — the fillet adds material in the
# concave region. Actually, fillets on concave (re-entrant) corners ADD material.
# So check that material exists slightly inside the concave corner.
# Concave fillets at the inner T corners add material to fill the notch.
# R=1mm fillet at corner (-2, Y, 52.5) adds material in a 1mm radius arc.
# A point very close to the corner should now be solid. Test at ~0.3mm
# diagonal offset into the concave region.
# Corner at (-2, Y, 52.5): the concave region is toward (-1.7, Y, 52.2)
# At the exact corner the two edges meet. The fillet inscribes an arc of R=1
# into the right angle. At 45-degree diagonal, the fillet surface is at
# R*(1 - 1/sqrt(2)) ≈ 0.293mm from corner. So a point 0.2mm diagonally
# into the notch should be solid (inside the fillet curve).
v.check_solid("Left fillet region bottom", -1.8, 77.5, 52.3, "solid in filleted concave corner (bottom)")
v.check_solid("Left fillet region top", -1.8, 77.5, 55.7, "solid in filleted concave corner (top)")
v.check_solid("Right fillet region bottom", 161.8, 77.5, 16.3, "solid in filleted concave corner (bottom)")
v.check_solid("Right fillet region top", 161.8, 77.5, 19.7, "solid in filleted concave corner (top)")

# --- Keying verification ---
# Left at Z=54, right at Z=18, offset = 36mm
v.check_solid("Keying: left at Z=54", -3.0, 77.5, 54.0, "left tongue present at Z=54")
v.check_void("Keying: no left at Z=18", -3.0, 77.5, 18.0, "no tongue at Z=18 on left side")
v.check_solid("Keying: right at Z=18", 163.0, 77.5, 18.0, "right tongue present at Z=18")
v.check_void("Keying: no right at Z=54", 163.0, 77.5, 54.0, "no tongue at Z=54 on right side")

# --- Bounding box ---
bb = result.val().BoundingBox()
print(f"\nBounding box: X=[{bb.xmin:.2f}, {bb.xmax:.2f}] Y=[{bb.ymin:.2f}, {bb.ymax:.2f}] Z=[{bb.zmin:.2f}, {bb.zmax:.2f}]")
v.check_bbox("X", bb.xmin, bb.xmax, -4.0, 164.0)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, 155.0)
# Z: left cap 51..57, right cap 15..21 => Z range 15..57
v.check_bbox("Z", bb.zmin, bb.zmax, 15.0, 57.0)

# --- Solid integrity ---
v.check_valid()
# Two disjoint tongues — they will become a single body only after union
# with the tray shell (Sub-A). As standalone solids they are 2 bodies.
n_bodies = len(result.solids().vals())
ok = n_bodies == 2
v._record("Body count", ok, f"{n_bodies} bodies (expected 2 disjoint tongues)")
# Volume estimate: each tongue is approximately 18mm^2 cross-section * 155mm = 2790mm^3 x2 = 5580
# T cross-section area = stem (3*2=6) + cap (6*2=12) = 18 mm^2
# With fillets adding a tiny bit, volume ~ 5600
expected_envelope = 168.0 * 155.0 * 57.0  # bounding box volume
v.check_volume(expected_envelope=expected_envelope, fill_range=(0.001, 0.02))

# --- Summary ---
if not v.summary():
    sys.exit(1)

print("\nDone. STEP file ready for composition with Sub-A box shell.")
