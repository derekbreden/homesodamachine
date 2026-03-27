"""
Generate STEP file for the Cartridge Release Plate using CadQuery.

Part specification: planning/parts.md
JG fitting geometry: ../../off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md

Axis convention (matching engineering drawing):
  X = width (59mm)
  Y = depth (6mm) — fitting side is Y=0, back side is Y=6
  Z = height (47mm)

The plate origin is at the bottom-left corner of the fitting-side face:
  X=0 at left edge, X=59 at right edge
  Y=0 at fitting face, Y=6 at back face
  Z=0 at bottom edge, Z=47 at top edge
"""

import cadquery as cq
from pathlib import Path

# ---------------------------------------------------------------------------
# Plate envelope
# ---------------------------------------------------------------------------
PLATE_W = 59.0   # X
PLATE_D = 6.0    # Y
PLATE_H = 47.0   # Z

# ---------------------------------------------------------------------------
# Stepped bore dimensions (caliper-verified interface dimensions)
# ---------------------------------------------------------------------------
OUTER_BORE_DIA = 15.6     # body end cradle (0.50mm over 15.10mm body end OD)
OUTER_BORE_DEPTH = 2.0
INNER_LIP_DIA = 10.0      # collet hugger (0.43mm over 9.57mm collet OD)
INNER_LIP_DEPTH = 2.0
TUBE_HOLE_DIA = 6.5        # between 6.30mm tube OD and 6.69mm collet ID

# Chamfers
OUTER_BORE_CHAMFER = 0.3  # 45-degree lead-in at fitting face
TUBE_HOLE_CHAMFER = 0.1   # at tube hole entry edge

OUTER_R = OUTER_BORE_DIA / 2    # 7.8
INNER_R = INNER_LIP_DIA / 2     # 5.0
TUBE_R = TUBE_HOLE_DIA / 2      # 3.25

# ---------------------------------------------------------------------------
# Bore grid — 2x2, centers relative to plate bottom-left (X, Z)
# ---------------------------------------------------------------------------
BORE_CX = [9.5, 49.5]
BORE_CZ = [9.5, 37.5]

# ---------------------------------------------------------------------------
# Push rod contact boss
# ---------------------------------------------------------------------------
BOSS_DIA = 8.0
BOSS_HEIGHT = 1.0
BOSS_CX = 29.5
BOSS_CZ = 23.5

# ---------------------------------------------------------------------------
# Guide pin tabs
# ---------------------------------------------------------------------------
TAB_SLOT_W = 3.3
TAB_SLOT_H = 7.3
TAB_W = TAB_SLOT_W + 4.0   # 7.3mm
TAB_H = TAB_SLOT_H + 4.0   # 11.3mm
LEFT_SLOT_CX = -5.5
RIGHT_SLOT_CX = 64.5
SLOT_CZ = 23.5

# ---------------------------------------------------------------------------
# Build: additive geometry first, then subtractive
# ---------------------------------------------------------------------------

# Step 1: Main plate body
plate = (
    cq.Workplane("XY")
    .box(PLATE_W, PLATE_D, PLATE_H, centered=False)
)

# Step 2: Push rod boss — build as standalone cylinder, union with plate
# Boss is centered at (BOSS_CX, Y=6..7, BOSS_CZ), axis along Y
boss = (
    cq.Workplane("XZ")           # workplane normal to Y axis
    .center(BOSS_CX, BOSS_CZ)    # X, Z position on XZ plane
    .circle(BOSS_DIA / 2)
    .extrude(-BOSS_HEIGHT)        # extrude in +Y direction (XZ normal is -Y)
    .translate((0, PLATE_D, 0))   # move from Y=0..1 to Y=6..7
)
plate = plate.union(boss)

# Step 3: Guide pin tabs — rectangular blocks extending from plate edges
# Tabs must overlap with the plate body to fuse into a single solid.
# Left tab: extends from plate left edge (X=0) outward to X = LEFT_SLOT_CX - TAB_W/2
# Right tab: extends from plate right edge (X=59) outward to X = RIGHT_SLOT_CX + TAB_W/2
for slot_cx in [LEFT_SLOT_CX, RIGHT_SLOT_CX]:
    if slot_cx < 0:
        # Left tab: from its left edge to plate left edge (X=0) with 1mm overlap
        tab_x_left = slot_cx - TAB_W / 2
        tab_x_right = 1.0  # 1mm overlap into plate
        tab_width = tab_x_right - tab_x_left
    else:
        # Right tab: from plate right edge - 1mm overlap to its right edge
        tab_x_left = PLATE_W - 1.0  # 1mm overlap into plate
        tab_x_right = slot_cx + TAB_W / 2
        tab_width = tab_x_right - tab_x_left
    tab_z0 = SLOT_CZ - TAB_H / 2
    tab = (
        cq.Workplane("XY")
        .box(tab_width, PLATE_D, TAB_H, centered=False)
        .translate((tab_x_left, 0, tab_z0))
    )
    plate = plate.union(tab)

# Step 4: Cut the 4 stepped bores using revolved profile
# Profile is a half-section (R, Y) revolved around the Y axis.
# Y=0 is fitting face, Y=6 is back face.
C_OUT = OUTER_BORE_CHAMFER
C_TUBE = TUBE_HOLE_CHAMFER

profile_points = [
    (0, 0),
    (OUTER_R - C_OUT, 0),                                      # chamfer start
    (OUTER_R, C_OUT),                                           # chamfer end
    (OUTER_R, OUTER_BORE_DEPTH),                                # outer bore floor
    (INNER_R, OUTER_BORE_DEPTH),                                # step to inner lip
    (INNER_R, OUTER_BORE_DEPTH + INNER_LIP_DEPTH),             # inner lip floor
    (TUBE_R + C_TUBE, OUTER_BORE_DEPTH + INNER_LIP_DEPTH),     # tube chamfer start
    (TUBE_R, OUTER_BORE_DEPTH + INNER_LIP_DEPTH + C_TUBE),     # tube chamfer end
    (TUBE_R, PLATE_D),                                          # tube hole exit
    (0, PLATE_D),                                               # axis at back face
]

bore_profile = cq.Workplane("XY").moveTo(profile_points[0][0], profile_points[0][1])
for r, y in profile_points[1:]:
    bore_profile = bore_profile.lineTo(r, y)
bore_profile = bore_profile.close()

bore_cutter = bore_profile.revolve(360, (0, 0), (0, 1))

for cx in BORE_CX:
    for cz in BORE_CZ:
        plate = plate.cut(bore_cutter.translate((cx, 0, cz)))

# Step 5: Cut guide pin slots (elongated holes through tabs)
# Use a direct approach: build stadium-shaped cutter solids and subtract them.
for slot_cx in [LEFT_SLOT_CX, RIGHT_SLOT_CX]:
    # Stadium (slot) shape: two semicircles connected by straight segments.
    # The slot is vertical (Z direction), 7.3mm long x 3.3mm wide.
    # slot2D(length, width) where length is the overall length including end radii.
    # The slot end-cap radius = TAB_SLOT_W / 2 = 1.65mm
    # The straight segment length = TAB_SLOT_H - TAB_SLOT_W = 4.0mm
    slot_cutter = (
        cq.Workplane("XZ")  # work in XZ plane (front view)
        .center(slot_cx, SLOT_CZ)
        .slot2D(TAB_SLOT_H, TAB_SLOT_W, angle=90)
        .extrude(PLATE_D)  # extrude in Y direction (through full plate depth)
    )
    plate = plate.cut(slot_cutter)

# ---------------------------------------------------------------------------
# Export and validate
# ---------------------------------------------------------------------------
output_dir = Path(__file__).parent
step_path = output_dir / "release-plate-cadquery.step"

cq.exporters.export(plate, str(step_path))

# Validation
bb = plate.val().BoundingBox()
print("Bounding box:")
print(f"  X: {bb.xmin:.3f} to {bb.xmax:.3f}  (width: {bb.xmax - bb.xmin:.3f}mm)")
print(f"  Y: {bb.ymin:.3f} to {bb.ymax:.3f}  (depth: {bb.ymax - bb.ymin:.3f}mm)")
print(f"  Z: {bb.zmin:.3f} to {bb.zmax:.3f}  (height: {bb.zmax - bb.zmin:.3f}mm)")

vol = plate.val().Volume()
print(f"\nVolume: {vol:.2f} mm^3")

faces = plate.val().Faces()
print(f"Face count: {len(faces)}")

total_x = bb.xmax - bb.xmin
total_y = bb.ymax - bb.ymin
total_z = bb.zmax - bb.zmin

print(f"\nSanity checks:")
print(f"  Plate body: {PLATE_W} x {PLATE_D} x {PLATE_H} mm")
print(f"  Total X span (with tabs): {total_x:.1f}mm")
print(f"  Total Y span (plate + boss): {total_y:.1f}mm (expect 7.0)")
print(f"  Total Z span: {total_z:.1f}mm (expect {PLATE_H})")
print(f"  Bore horizontal spacing: {BORE_CX[1] - BORE_CX[0]:.1f}mm (expect 40.0)")
print(f"  Bore vertical spacing: {BORE_CZ[1] - BORE_CZ[0]:.1f}mm (expect 28.0)")
print(f"  Min wall (edge to outer bore): {BORE_CX[0] - OUTER_R:.1f}mm (expect 1.7)")

# Expected volume estimate (approximate — ignores chamfers, uses rect for stadium slots)
import math
plate_vol = PLATE_W * PLATE_D * PLATE_H
bore_vol = (math.pi * OUTER_R**2 * OUTER_BORE_DEPTH +
            math.pi * INNER_R**2 * INNER_LIP_DEPTH +
            math.pi * TUBE_R**2 * 2.0)  # remaining 2mm
total_bore_vol = 4 * bore_vol
boss_vol = math.pi * (BOSS_DIA / 2)**2 * BOSS_HEIGHT
# Tabs: actual width is from slot far edge to 1mm inside plate body
left_tab_w = 1.0 - (LEFT_SLOT_CX - TAB_W / 2)   # 10.15mm
right_tab_w = (RIGHT_SLOT_CX + TAB_W / 2) - (PLATE_W - 1.0)  # 10.15mm
# Net tab addition = tab volume minus the 1mm overlap already counted in plate
net_tab_vol = ((left_tab_w - 1.0) + (right_tab_w - 1.0)) * PLATE_D * TAB_H
slot_vol = 2 * TAB_SLOT_W * TAB_SLOT_H * PLATE_D  # rect approx (stadium is ~10% less)

expected_vol = plate_vol - total_bore_vol + boss_vol + net_tab_vol - slot_vol
print(f"\n  Approx expected volume: {expected_vol:.0f} mm^3 (actual: {vol:.0f})")
print(f"  (Difference due to chamfers and stadium vs rect slot approximation)")

print(f"\nSTEP file written to: {step_path}")
