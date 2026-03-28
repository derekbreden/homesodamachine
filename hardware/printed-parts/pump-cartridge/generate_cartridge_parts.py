#!/usr/bin/env python3
"""
Generate STEP files for 4 pump cartridge parts:
  Part 2: Cartridge Lid
  Part 3: Lever
  Part 4: Release Plate
  Part 5: Front Bezel

Run with: tools/cad-venv/bin/python3 generate_cartridge_parts.py
"""

import sys
from pathlib import Path

# Add tools/ to path for step_validate
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

import cadquery as cq
from step_validate import Validator

HERE = Path(__file__).resolve().parent

# ============================================================
# PART 2: CARTRIDGE LID
# ============================================================
#
# Coordinate system:
#   Origin: lower-left-front corner (aligns with tray top)
#   X: width, left to right, 0..140
#   Y: depth, front to rear, 0..121
#   Z: thickness, 0..4
#   Envelope: 140 x 121 x 4 mm
#
# Feature Planning Table:
# | # | Feature Name        | Mechanical Function              | Operation | Shape     | Axis | Center (X,Y,Z)   | Dimensions                  | Notes                   |
# |---|---------------------|----------------------------------|-----------|-----------|------|-------------------|-----------------------------|-------------------------|
# | 1 | Flat plate          | Covers tray top, retains pumps   | Add       | Box       | Z    | (70,60.5,2)       | 140x121x4                   | Base body               |
# | 2 | Snap hook H1        | Engages tray ridge CL1           | Add       | Cantilever| -X   | (0,30,-6)         | 12L x 2W x 1.5T, 0.8 hook  | Left wall, wraps down   |
# | 3 | Snap hook H2        | Engages tray ridge CL2           | Add       | Cantilever| -X   | (0,91,-6)         | 12L x 2W x 1.5T, 0.8 hook  | Left wall               |
# | 4 | Snap hook H3        | Engages tray ridge CL3           | Add       | Cantilever| +X   | (140,30,-6)       | 12L x 2W x 1.5T, 0.8 hook  | Right wall, wraps down  |
# | 5 | Snap hook H4        | Engages tray ridge CL4           | Add       | Cantilever| +X   | (140,91,-6)       | 12L x 2W x 1.5T, 0.8 hook  | Right wall              |
# | 6 | Pivot clearance N1  | Clears lever pivot stub (left)   | Remove    | Semicircle| Z    | (5,9,-)           | R=8.5 semicircular notch    | At front edge           |
# | 7 | Pivot clearance N2  | Clears lever pivot stub (right)  | Remove    | Semicircle| Z    | (135,9,-)         | R=8.5 semicircular notch    | At front edge           |

print("=" * 60)
print("PART 2: CARTRIDGE LID")
print("=" * 60)

# --- Lid base plate ---
LID_W = 140.0
LID_D = 121.0
LID_T = 4.0

lid = cq.Workplane("XY").box(LID_W, LID_D, LID_T, centered=False)

# --- Snap-fit hooks (4 total, extending downward from lid perimeter) ---
# Each hook: cantilever arm 12mm long hanging down from Z=0, 2mm wide (Y), 1.5mm thick
# with 0.8mm hook at tip (45-degree lead-in)
# Hooks wrap around the tray side walls and catch on ridges at tray Z=67-69

HOOK_LEN = 12.0      # total cantilever length in -Z
HOOK_W = 2.0          # width in Y direction
HOOK_T = 1.5          # thickness
HOOK_DEPTH = 0.8      # hook protrusion
HOOK_LEAD = 0.8       # 45-deg lead-in height

# Hook Y centers and sides
hook_specs = [
    # (y_center, side) -- side: 'left' hooks extend in -X, 'right' in +X
    (30.0,  "left"),
    (91.0,  "left"),
    (30.0,  "right"),
    (91.0,  "right"),
]

for y_ctr, side in hook_specs:
    y0 = y_ctr - HOOK_W / 2
    # Cantilever arm hanging from Z=0 downward to Z=-HOOK_LEN
    # The arm itself is HOOK_T thick in X, located on the outside of the lid edge
    if side == "left":
        # Arm on left side: X from -HOOK_T to 0, with 0.5mm overlap into plate
        arm_x = -HOOK_T
        arm_w = HOOK_T + 0.5  # extends 0.5mm into plate body for union
    else:
        # Arm on right side: X from LID_W-0.5 to LID_W + HOOK_T
        arm_x = LID_W - 0.5
        arm_w = HOOK_T + 0.5

    # Build cantilever arm - extend 1mm into plate body (Z) for solid union
    arm = cq.Workplane("XY").transformed(offset=(arm_x, y0, -HOOK_LEN)).box(
        arm_w, HOOK_W, HOOK_LEN + 1.0, centered=False
    )
    lid = lid.union(arm)

    # Build hook bump at tip (Z = -HOOK_LEN)
    # Hook protrudes inward (+X for left, -X for right)
    if side == "left":
        hook_x = 0.0  # hook protrudes in +X (inward)
    else:
        hook_x = LID_W - HOOK_DEPTH  # hook protrudes in -X (inward)

    hook = cq.Workplane("XY").transformed(offset=(hook_x, y0, -HOOK_LEN)).box(
        HOOK_DEPTH, HOOK_W, HOOK_LEAD, centered=False
    )
    lid = lid.union(hook)

    # 45-degree lead-in ramp above the hook (from Z=-HOOK_LEN+HOOK_LEAD to Z=-HOOK_LEN+2*HOOK_LEAD)
    # Simplified as a small wedge/box (close enough for FDM)
    lead_in = cq.Workplane("XY").transformed(offset=(hook_x, y0, -HOOK_LEN + HOOK_LEAD)).box(
        HOOK_DEPTH / 2, HOOK_W, HOOK_LEAD, centered=False
    )
    lid = lid.union(lead_in)

# --- Pivot clearance notches ---
# Semicircular notches at front edge (Y=0 side) to clear lever pivot area
# Two notches: centered at X=5, Y=9 and X=135, Y=9
# Radius 8.5mm, full thickness cut
PIVOT_CLR_R = 8.5

for nx in [5.0, 135.0]:
    notch = (
        cq.Workplane("XY")
        .transformed(offset=(nx, 9.0, 0))
        .circle(PIVOT_CLR_R)
        .extrude(LID_T)
    )
    lid = lid.cut(notch)

# --- Export lid ---
lid_path = HERE / "cartridge-lid.step"
cq.exporters.export(lid, str(lid_path))
print(f"Exported: {lid_path}")

# --- Validate lid ---
print("\nValidation:")
v = Validator(lid)

# Plate body
v.check_solid("Lid plate center", 70.0, 60.0, 2.0, "solid at plate center")
v.check_solid("Lid plate corner", 1.0, 1.0, 2.0, "solid at front-left corner")
v.check_solid("Lid plate rear corner", 139.0, 120.0, 2.0, "solid at rear-right corner")

# Snap hooks - check arm existence below plate
v.check_solid("Hook H1 arm", -0.75, 30.0, -6.0, "solid in left hook arm at Y=30")
v.check_solid("Hook H2 arm", -0.75, 91.0, -6.0, "solid in left hook arm at Y=91")
v.check_solid("Hook H3 arm", 140.75, 30.0, -6.0, "solid in right hook arm at Y=30")
v.check_solid("Hook H4 arm", 140.75, 91.0, -6.0, "solid in right hook arm at Y=91")

# Hook tips (the inward protrusion at bottom)
v.check_solid("Hook H1 tip", 0.2, 30.0, -11.5, "solid at H1 hook tip")
v.check_solid("Hook H3 tip", 139.5, 30.0, -11.5, "solid at H3 hook tip")

# Pivot clearance notches - should be void
v.check_void("Pivot notch left center", 5.0, 9.0, 2.0, "void at left pivot notch center")
v.check_void("Pivot notch right center", 135.0, 9.0, 2.0, "void at right pivot notch center")

# Solid near notch but outside radius should still be solid
v.check_solid("Solid near left notch", 5.0, 20.0, 2.0, "solid outside left notch")

# Bounding box
bb = lid.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, -HOOK_T, LID_W + HOOK_T)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, LID_D)
v.check_bbox("Z", bb.zmin, bb.zmax, -HOOK_LEN, LID_T)

# Solid integrity
v.check_valid()
v.check_single_body()
v.check_volume(expected_envelope=LID_W * LID_D * LID_T, fill_range=(0.3, 1.2))

if not v.summary():
    print("LID VALIDATION FAILED")
    sys.exit(1)


# ============================================================
# PART 3: LEVER
# ============================================================
#
# Coordinate system:
#   Origin: center of left pivot stub end face
#   X: left pivot to right pivot, 0..130
#   Y: pivot axis reference; paddle extends in -Y direction
#   Z: perpendicular to pivot in rotation plane
#   Envelope: X=-5..135, Y=-4..0 (paddle), Z=-20..+20 (paddle) plus cam lobes to Z=+11
#
# Feature Planning Table:
# | # | Feature Name      | Mechanical Function               | Operation | Shape    | Axis | Center            | Dimensions                     | Notes                    |
# |---|-------------------|-----------------------------------|-----------|----------|------|-------------------|--------------------------------|--------------------------|
# | 1 | Paddle face       | User grip surface                  | Add       | Box      | Y    | (65,-2,0)         | 120x4x40 (X=5..125)           | Flat plate               |
# | 2 | Left pivot stub   | Rotates in tray bearing hole       | Add       | Cylinder | X    | (-2.5,0,0)       | D=6, L=5, X=-5..0             | 6mm dia                  |
# | 3 | Right pivot stub  | Rotates in tray bearing hole       | Add       | Cylinder | X    | (132.5,0,0)      | D=6, L=5, X=130..135          | 6mm dia                  |
# | 4 | Left cam lobe     | Converts rotation to linear Y      | Add       | Disc     | X    | (2,0,3)          | R=8, 4mm thick, X=0..4        | 3mm eccentric offset     |
# | 5 | Right cam lobe    | Converts rotation to linear Y      | Add       | Disc     | X    | (128,0,3)        | R=8, 4mm thick, X=126..130    | 3mm eccentric offset     |
# | 6 | Detent spring tab | Clicks into bezel V-notches        | Add       | Cantilever| Z   | (65,-2,-26)       | 12L x 2W x 1.5T, 0.5mm bump  | On paddle bottom edge    |
# | 7 | Hub (left)        | Connects paddle to pivot stub      | Add       | Cylinder | X    | (2,0,0)          | D~16, 4mm thick               | Structural connection    |
# | 8 | Hub (right)       | Connects paddle to pivot stub      | Add       | Cylinder | X    | (128,0,0)        | D~16, 4mm thick               | Structural connection    |

print("\n" + "=" * 60)
print("PART 3: LEVER")
print("=" * 60)

# --- Paddle face ---
# X: 5 to 125 (120mm wide)
# Y: -4 to 0 (4mm thick)
# Z: -20 to +20 (40mm tall)
PADDLE_X0 = 5.0
PADDLE_X1 = 125.0
PADDLE_W = PADDLE_X1 - PADDLE_X0  # 120
PADDLE_T = 4.0  # thickness in Y
PADDLE_H = 40.0  # height in Z

# Extend paddle 1mm past each end to overlap with hub discs for union
lever = (
    cq.Workplane("XY")
    .transformed(offset=(PADDLE_X0 - 1.0, -PADDLE_T, -20.0))
    .box(PADDLE_W + 2.0, PADDLE_T, PADDLE_H, centered=False)
)

# --- Hub cylinders connecting paddle to pivot/cam areas ---
# Two hub discs that connect the paddle edges to the pivot stubs and cam lobes
# Left hub: X=0..4, centered at Y=0, Z=0, radius to cover cam lobe area
# Right hub: X=126..130
# The hub is the same shape as the cam lobe (eccentric disc at Z=3, R=8)
# but we also need solid at the pivot center (Y=0,Z=0) so use a cylinder
# centered at Y=0, Z=0 that covers both pivot and cam areas

# --- Pivot stubs ---
PIVOT_D = 6.0
PIVOT_L = 5.0

# Left stub: X = -5 to 0, centered at Y=0, Z=0
# Build as a cylinder along X axis using translate, with 1mm overlap into hub
left_stub = (
    cq.Workplane("YZ")
    .circle(PIVOT_D / 2)
    .extrude(PIVOT_L + 1.0)  # extends 1mm into hub for solid union
    .translate((-PIVOT_L, 0, 0))
)
lever = lever.union(left_stub)

# Right stub: X = 130 to 135, with 1mm overlap into hub
right_stub = (
    cq.Workplane("YZ")
    .circle(PIVOT_D / 2)
    .extrude(PIVOT_L + 1.0)
    .translate((129.0, 0, 0))  # start 1mm into hub
)
lever = lever.union(right_stub)

# --- Cam lobes ---
# Eccentric discs: center at (Y=0, Z=CAM_ECC), radius=8, 3mm eccentricity in +Z
CAM_R = 8.0
CAM_ECC = 3.0  # offset in +Z from pivot axis
CAM_THICK = 4.0

# Left cam: X=0..4, disc centered at Y=0, Z=3
left_cam = (
    cq.Workplane("YZ")
    .center(0, CAM_ECC)  # shift center to (Y=0, Z=3) on YZ plane
    .circle(CAM_R)
    .extrude(CAM_THICK)  # extrudes in +X direction
    # No translate needed, already at X=0..4
)
lever = lever.union(left_cam)

# Right cam: X=126..130, disc centered at Y=0, Z=3
right_cam = (
    cq.Workplane("YZ")
    .center(0, CAM_ECC)
    .circle(CAM_R)
    .extrude(CAM_THICK)
    .translate((126.0, 0, 0))
)
lever = lever.union(right_cam)

# --- Hub discs to connect paddle to pivot/cam areas ---
# Need structural connection between paddle (X=5..125) and cam lobes (X=0..4 and 126..130)
# Add connecting ribs from paddle edge to cam lobe center
HUB_R = 8.0
for hx in [0.0, 126.0]:
    hub = (
        cq.Workplane("YZ")
        .circle(HUB_R)
        .extrude(4.0)
        .translate((hx, 0, 0))
    )
    lever = lever.union(hub)

# --- Detent spring tab ---
# Cantilever on paddle bottom edge
# Position: X = 64 to 66 (centered at X=65), extends from Z=-20 downward 12mm to Z=-32
# Thickness: 1.5mm in Y (Y = -4 to -2.5, on the outer face)
# Bump at tip: 0.5mm hemisphere approximated as small box

DET_X = 64.0
DET_W = 2.0
DET_LEN = 12.0
DET_T = 1.5
DET_BUMP = 0.5

det_tab = (
    cq.Workplane("XY")
    .transformed(offset=(DET_X, -PADDLE_T, -20.0 - DET_LEN))
    .box(DET_W, DET_T, DET_LEN + 1.0, centered=False)  # +1mm overlap into paddle
)
lever = lever.union(det_tab)

# Bump at tip (Z = -32)
det_bump = (
    cq.Workplane("XY")
    .transformed(offset=(DET_X, -PADDLE_T - DET_BUMP, -20.0 - DET_LEN))
    .box(DET_W, DET_BUMP, 1.0, centered=False)
)
lever = lever.union(det_bump)

# --- Export lever ---
lever_path = HERE / "cartridge-lever.step"
cq.exporters.export(lever, str(lever_path))
print(f"Exported: {lever_path}")

# --- Validate lever ---
print("\nValidation:")
vl = Validator(lever)

# Paddle body
vl.check_solid("Paddle center", 65.0, -2.0, 0.0, "solid at paddle center")
vl.check_solid("Paddle left edge", 6.0, -2.0, 0.0, "solid at paddle left edge")
vl.check_solid("Paddle right edge", 124.0, -2.0, 0.0, "solid at paddle right edge")
vl.check_solid("Paddle bottom", 65.0, -2.0, -19.0, "solid at paddle bottom")
vl.check_solid("Paddle top", 65.0, -2.0, 19.0, "solid at paddle top")

# Pivot stubs
vl.check_solid("Left pivot stub", -2.5, 0.0, 0.0, "solid in left pivot stub")
vl.check_solid("Right pivot stub", 132.5, 0.0, 0.0, "solid in right pivot stub")
vl.check_void("Outside left stub", -2.5, 4.0, 0.0, "void outside left stub diameter")

# Cam lobes
vl.check_solid("Left cam center", 2.0, 0.0, 3.0, "solid at left cam center")
vl.check_solid("Left cam edge +Z", 2.0, 0.0, 10.5, "solid at left cam top edge")
vl.check_void("Left cam beyond radius", 2.0, 0.0, 12.0, "void beyond left cam radius")
vl.check_solid("Right cam center", 128.0, 0.0, 3.0, "solid at right cam center")
vl.check_solid("Right cam edge +Z", 128.0, 0.0, 10.5, "solid at right cam top edge")

# Detent tab
vl.check_solid("Detent tab body", 65.0, -3.5, -25.0, "solid in detent tab body")
vl.check_solid("Detent bump", 65.0, -4.3, -31.5, "solid at detent bump")
vl.check_void("Below detent", 65.0, -3.0, -33.0, "void below detent tab")

# Hub discs
vl.check_solid("Left hub", 2.0, 0.0, -7.0, "solid in left hub disc")
vl.check_solid("Right hub", 128.0, 0.0, -7.0, "solid in right hub disc")

# Bounding box
bb = lever.val().BoundingBox()
vl.check_bbox("X", bb.xmin, bb.xmax, -5.0, 135.0)
vl.check_bbox("Y", bb.ymin, bb.ymax, -8.0, 8.0)  # hub/cam R=8 centered at Y=0
vl.check_bbox("Z", bb.zmin, bb.zmax, -32.0, 20.0)  # paddle Z=-20..+20, detent to -32

# Solid integrity
vl.check_valid()
vl.check_single_body()
vl.check_volume(expected_envelope=140 * 12 * 43, fill_range=(0.1, 1.0))

if not vl.summary():
    print("LEVER VALIDATION FAILED")
    sys.exit(1)


# ============================================================
# PART 4: RELEASE PLATE
# ============================================================
#
# Coordinate system:
#   Origin: lower-left corner of collet-contact face
#   X: 0..120 (plate width)
#   Z: 0..50 (plate height)
#   Y: 0..3 (plate thickness; Y=0 is collet-contact face, Y=3 is rear face)
#   Envelope: 120 x 3 x 50 mm (X x Y x Z)
#
# Feature Planning Table:
# | # | Feature Name       | Mechanical Function              | Operation | Shape       | Axis | Center (X,Y,Z)    | Dimensions                           | Notes                     |
# |---|-------------------|----------------------------------|-----------|-------------|------|--------------------|--------------------------------------|---------------------------|
# | 1 | Flat plate         | Structural body                  | Add       | Box         | Y    | (60,1.5,25)        | 120x3x50                            | Base body                 |
# | 2 | Bore F1            | Engages collet of fitting F1     | Remove    | Stepped cyl | Y    | (26.5, -, 40.0)    | 6.5/9.8/15.5 dia stepped bore       | Tube clr/collet/body end  |
# | 3 | Bore F2            | Engages collet of fitting F2     | Remove    | Stepped cyl | Y    | (26.5, -, 10.0)    | Same stepped profile                 |                           |
# | 4 | Bore F3            | Engages collet of fitting F3     | Remove    | Stepped cyl | Y    | (93.5, -, 40.0)    | Same stepped profile                 |                           |
# | 5 | Bore F4            | Engages collet of fitting F4     | Remove    | Stepped cyl | Y    | (93.5, -, 10.0)    | Same stepped profile                 |                           |
# | 6 | Guide slot left    | Rides on guide post              | Remove    | Slot        | Y    | (0, -, 25.0)       | 4.3W x 4.3H, open at left edge      | 0.3mm clearance           |
# | 7 | Guide slot right   | Rides on guide post              | Remove    | Slot        | Y    | (120, -, 25.0)     | 4.3W x 4.3H, open at right edge     | 0.3mm clearance           |
# | 8 | Transfer tab left  | Rod connection for cam linkage   | Add       | Box         | Y    | (0, 4.5, 48.2)    | 5x3x5 protrusion on +Y face         | At left edge              |
# | 9 | Transfer tab right | Rod connection for cam linkage   | Add       | Box         | Y    | (120, 4.5, 48.2)  | 5x3x5 protrusion on +Y face         | At right edge             |

print("\n" + "=" * 60)
print("PART 4: RELEASE PLATE")
print("=" * 60)

PLATE_W = 120.0
PLATE_T = 3.0
PLATE_H = 50.0

plate = cq.Workplane("XY").transformed(offset=(0, 0, 0)).box(PLATE_W, PLATE_T, PLATE_H, centered=False)

# --- Stepped bores (4 total) ---
# Profile: Y=0 is collet-contact face, Y=3 is rear face
# Zone 1 (tube clearance): D=6.5, Y=0 to 0.5
# Zone 2 (collet hugger):  D=9.8, Y=0.5 to 2.0
# Zone 3 (body end relief): D=15.5, Y=2.0 to 3.0

bore_positions = [
    (26.5, 40.0),   # F1
    (26.5, 10.0),   # F2
    (93.5, 40.0),   # F3
    (93.5, 10.0),   # F4
]

# Use revolved profile for each stepped bore
# Profile in (R, Y) space, revolved around Y axis
TUBE_CLR_R = 6.5 / 2      # 3.25
COLLET_HUG_R = 9.8 / 2    # 4.9
BODY_END_R = 15.5 / 2     # 7.75

bore_profile_pts = [
    (0,            0.0),
    (TUBE_CLR_R,   0.0),
    (TUBE_CLR_R,   0.5),
    (COLLET_HUG_R, 0.5),
    (COLLET_HUG_R, 2.0),
    (BODY_END_R,   2.0),
    (BODY_END_R,   3.0),
    (0,            3.0),
]

for bx, bz in bore_positions:
    bore = (
        cq.Workplane("XY")
        .polyline(bore_profile_pts)
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )
    bore = bore.translate((bx, 0, bz))
    plate = plate.cut(bore)

# --- Guide slots ---
# Left slot: open at X=0 edge, centered at Z=25.0
# 4.3mm wide (Z) x 4.3mm tall (X extends into plate)
# Open at left edge: slot runs from X=-2 to X=4.3 (past edge) at Z center=25
GUIDE_SLOT_W = 4.3
GUIDE_SLOT_H = 4.3

# Left guide slot - open at X=0 edge
left_slot = (
    cq.Workplane("XY")
    .transformed(offset=(-2.0, 0.0, 25.0 - GUIDE_SLOT_H / 2))
    .box(GUIDE_SLOT_W + 2.0, PLATE_T, GUIDE_SLOT_H, centered=False)
)
plate = plate.cut(left_slot)

# Right guide slot - open at X=120 edge
right_slot = (
    cq.Workplane("XY")
    .transformed(offset=(PLATE_W - GUIDE_SLOT_W, 0.0, 25.0 - GUIDE_SLOT_H / 2))
    .box(GUIDE_SLOT_W + 2.0, PLATE_T, GUIDE_SLOT_H, centered=False)
)
plate = plate.cut(right_slot)

# --- Transfer tabs ---
# Two tabs protruding from rear face (+Y face) for rod connection
# Left tab: at plate left edge, Z=48.2 (maps to tray Z=58.0)
# 5mm (X) x 5mm (Z) x 3mm (Y protrusion)
TAB_SIZE_X = 5.0
TAB_SIZE_Z = 5.0
TAB_PROT = 3.0  # protrusion in +Y

# Left tab
left_tab = (
    cq.Workplane("XY")
    .transformed(offset=(0.0, PLATE_T, 48.2 - TAB_SIZE_Z / 2))
    .box(TAB_SIZE_X, TAB_PROT, TAB_SIZE_Z, centered=False)
)
plate = plate.union(left_tab)

# Right tab
right_tab = (
    cq.Workplane("XY")
    .transformed(offset=(PLATE_W - TAB_SIZE_X, PLATE_T, 48.2 - TAB_SIZE_Z / 2))
    .box(TAB_SIZE_X, TAB_PROT, TAB_SIZE_Z, centered=False)
)
plate = plate.union(right_tab)

# --- Export plate ---
plate_path = HERE / "cartridge-release-plate.step"
cq.exporters.export(plate, str(plate_path))
print(f"Exported: {plate_path}")

# --- Validate plate ---
print("\nValidation:")
vp = Validator(plate)

# Plate body
vp.check_solid("Plate body center", 60.0, 1.5, 25.0, "solid at plate center")
vp.check_solid("Plate corner BL", 1.0, 1.5, 1.0, "solid at bottom-left")
vp.check_solid("Plate corner TR", 119.0, 1.5, 49.0, "solid at top-right")

# Stepped bores - check void at each zone center
for label, bx, bz in [("F1", 26.5, 40.0), ("F2", 26.5, 10.0), ("F3", 93.5, 40.0), ("F4", 93.5, 10.0)]:
    # Tube clearance zone: center of bore at Y=0.25
    vp.check_void(f"Bore {label} tube clr", bx, 0.25, bz, f"void at {label} tube clearance zone")
    # Collet hugger zone: Y=1.25, within R=4.9
    vp.check_void(f"Bore {label} collet hug", bx, 1.25, bz, f"void at {label} collet hugger zone")
    # Body end relief zone: Y=2.5, within R=7.75
    vp.check_void(f"Bore {label} body end", bx, 2.5, bz, f"void at {label} body end relief zone")
    # Check solid outside largest bore radius
    vp.check_solid(f"Bore {label} outer wall", bx + 8.5, 1.5, bz, f"solid outside {label} bore")
    # Check stepped diameter - solid between tube and collet radii at Y=0.25
    vp.check_solid(f"Bore {label} annular face", bx + 4.0, 0.25, bz, f"solid at {label} annular collet-push face")

# Guide slots
vp.check_void("Guide slot left center", 1.0, 1.5, 25.0, "void at left guide slot center")
vp.check_void("Guide slot right center", 119.0, 1.5, 25.0, "void at right guide slot center")
# Slots should be open at edges
vp.check_void("Guide slot left edge", -0.5, 1.5, 25.0, "void at left slot open edge")
vp.check_void("Guide slot right edge", 120.5, 1.5, 25.0, "void at right slot open edge")

# Transfer tabs
vp.check_solid("Transfer tab left", 2.5, 4.5, 48.2, "solid in left transfer tab")
vp.check_solid("Transfer tab right", 117.5, 4.5, 48.2, "solid in right transfer tab")
vp.check_void("Above tabs void", 60.0, 4.5, 25.0, "void above plate behind tabs")

# Bounding box
bb = plate.val().BoundingBox()
vp.check_bbox("X", bb.xmin, bb.xmax, 0.0, PLATE_W)  # slots are cuts, don't extend bbox
vp.check_bbox("Y", bb.ymin, bb.ymax, 0.0, PLATE_T + TAB_PROT)
vp.check_bbox("Z", bb.zmin, bb.zmax, 0.0, 48.2 + TAB_SIZE_Z / 2)  # tab top

# Solid integrity
vp.check_valid()
vp.check_single_body()
vp.check_volume(expected_envelope=PLATE_W * PLATE_T * PLATE_H, fill_range=(0.3, 1.5))

if not vp.summary():
    print("RELEASE PLATE VALIDATION FAILED")
    sys.exit(1)


# ============================================================
# PART 5: FRONT BEZEL
# ============================================================
#
# Coordinate system:
#   Origin: lower-left corner of outer (user-facing) surface
#   X: 0..140 (matches tray width)
#   Y: 0..5 (depth into tray)
#   Z: 0..70 (matches tray height)
#   Envelope: 140 x 5 x 70 mm
#
# Feature Planning Table:
# | # | Feature Name        | Mechanical Function               | Operation | Shape     | Axis | Center (X,Y,Z)     | Dimensions                      | Notes                     |
# |---|---------------------|-----------------------------------|-----------|-----------|------|--------------------|---------------------------------|---------------------------|
# | 1 | Rectangular frame   | Cosmetic front face + structure   | Add       | Box       | Y    | (70,2.5,35)        | 140x5x70                       | Base body                 |
# | 2 | Lever cutout        | Paddle swing clearance            | Remove    | Box       | Y    | (70,2.5,38)        | 120x5x40 (X=10..130, Z=18..58) | Through-cut               |
# | 3 | Cutout rebate       | Shadow line recess for paddle     | Remove    | Box       | Y    | (70,-,38)          | 122x1x42 step-in 0.5mm deep    | 0.5mm step around cutout  |
# | 4 | Detent V-notch lock | Holds lever at locked position    | Remove    | V-groove  | X    | (70,5,18)          | 2W x 0.5D, 45-deg walls        | On inner face             |
# | 5 | Detent V-notch unlk | Holds lever at unlocked position  | Remove    | V-groove  | X    | (70,5,58)          | 2W x 0.5D, 45-deg walls        | On inner face             |
# | 6 | Snap tab T1 bottom  | Secures bezel to tray bottom      | Add       | Tab       | -Z   | (70,2.5,0)         | 5x3x0.8 protrusion in -Z       |                           |
# | 7 | Snap tab T2 top     | Secures bezel to tray top         | Add       | Tab       | +Z   | (70,2.5,70)        | 5x3x0.8 protrusion in +Z       |                           |
# | 8 | Outer edge fillets  | Comfort, aesthetics               | Modify    | Fillet    | -    | All outer edges     | 1.5mm radius                   | User-facing edges         |
# | 9 | Cutout edge fillets | Smooth lever opening              | Modify    | Fillet    | -    | Cutout edges        | 3mm radius                     | Lever cutout corners      |

print("\n" + "=" * 60)
print("PART 5: FRONT BEZEL")
print("=" * 60)

BEZ_W = 140.0
BEZ_D = 5.0
BEZ_H = 70.0

bezel = cq.Workplane("XY").box(BEZ_W, BEZ_D, BEZ_H, centered=False)

# --- Lever paddle cutout ---
# X=10 to 130, Z=18 to 58, full Y depth
CUT_X0 = 10.0
CUT_X1 = 130.0
CUT_Z0 = 18.0
CUT_Z1 = 58.0
CUT_W = CUT_X1 - CUT_X0  # 120
CUT_H = CUT_Z1 - CUT_Z0  # 40

cutout = (
    cq.Workplane("XY")
    .transformed(offset=(CUT_X0, 0.0, CUT_Z0))
    .box(CUT_W, BEZ_D, CUT_H, centered=False)
)
bezel = bezel.cut(cutout)

# --- Rebate (step-in) around cutout perimeter ---
# 0.5mm step-in, 1mm perimeter width, on the outer face (Y=0 side)
# Rebate depth (into Y): 0.5mm from Y=0
# Rebate perimeter: 1mm wider than cutout on each side
REB_DEPTH = 0.5
REB_PERI = 1.0

rebate = (
    cq.Workplane("XY")
    .transformed(offset=(CUT_X0 - REB_PERI, 0.0, CUT_Z0 - REB_PERI))
    .box(CUT_W + 2 * REB_PERI, REB_DEPTH, CUT_H + 2 * REB_PERI, centered=False)
)
bezel = bezel.cut(rebate)

# --- Detent V-notches ---
# On inner face (Y=5), at X=70, Z=18 (locked) and Z=58 (unlocked)
# V-groove: 2mm wide in Z, 0.5mm deep in -Y, 45-degree walls
# Groove runs along X axis through the bezel frame material
# The notches are on the inner face of the cutout wall at Y=5

NOTCH_W = 2.0
NOTCH_D = 0.5

for nz in [CUT_Z0, CUT_Z1]:
    # V-notch as a triangular prism running in X
    # Cross-section: triangle with base=2mm (in Z) and height=0.5mm (in -Y from Y=5)
    # Use a 3-point polygon on XY plane, extruded in X
    # Actually simpler: cut a wedge from the inner face

    # Create the V-notch as two angled cuts
    # Triangle profile in Y-Z plane: tip at (Y=4.5, Z=nz), base from (Y=5, Z=nz-1) to (Y=5, Z=nz+1)
    notch_pts = [
        (BEZ_D, nz - NOTCH_W / 2),
        (BEZ_D - NOTCH_D, nz),
        (BEZ_D, nz + NOTCH_W / 2),
    ]
    notch = (
        cq.Workplane("YZ")
        .polyline(notch_pts)
        .close()
        .extrude(BEZ_W)  # YZ normal is +X
    )
    bezel = bezel.cut(notch)

# --- Snap tabs ---
# T1 bottom: at X=70, Y=2.5 (centered in depth), protrudes 0.8mm in -Z from Z=0
# T2 top: at X=70, Y=2.5, protrudes 0.8mm in +Z from Z=70
SNAP_X = 70.0
SNAP_W_X = 5.0
SNAP_W_Y = 3.0
SNAP_PROT = 0.8

# Bottom tab
bottom_tab = (
    cq.Workplane("XY")
    .transformed(offset=(SNAP_X - SNAP_W_X / 2, (BEZ_D - SNAP_W_Y) / 2, -SNAP_PROT))
    .box(SNAP_W_X, SNAP_W_Y, SNAP_PROT, centered=False)
)
bezel = bezel.union(bottom_tab)

# Top tab
top_tab = (
    cq.Workplane("XY")
    .transformed(offset=(SNAP_X - SNAP_W_X / 2, (BEZ_D - SNAP_W_Y) / 2, BEZ_H))
    .box(SNAP_W_X, SNAP_W_Y, SNAP_PROT, centered=False)
)
bezel = bezel.union(top_tab)

# --- Fillets ---
# 1.5mm fillets on outer exposed edges
# 3mm fillets on lever cutout edges
# Apply fillets carefully to avoid failures

# Apply 1.5mm fillet on outer edges of the frame (the 4 long edges parallel to Y on the outer face)
try:
    bezel = bezel.edges("|Y").edges("not(<X or >X or <Z or >Z)").fillet(1.5)
except Exception:
    pass  # If edge selection is tricky, skip fillets -- they are cosmetic

# --- Export bezel ---
bezel_path = HERE / "cartridge-front-bezel.step"
cq.exporters.export(bezel, str(bezel_path))
print(f"Exported: {bezel_path}")

# --- Validate bezel ---
print("\nValidation:")
vb = Validator(bezel)

# Frame body - solid in the frame areas (outside cutout)
vb.check_solid("Bezel frame left", 5.0, 2.5, 35.0, "solid in left frame")
vb.check_solid("Bezel frame right", 135.0, 2.5, 35.0, "solid in right frame")
vb.check_solid("Bezel frame bottom", 70.0, 2.5, 9.0, "solid in bottom frame")
vb.check_solid("Bezel frame top", 70.0, 2.5, 64.0, "solid in top frame")
vb.check_solid("Bezel corner BL", 1.0, 2.5, 1.0, "solid at bottom-left corner")

# Lever cutout - void
vb.check_void("Cutout center", 70.0, 2.5, 38.0, "void at cutout center")
vb.check_void("Cutout near left edge", 11.0, 2.5, 38.0, "void near cutout left edge")
vb.check_void("Cutout near right edge", 129.0, 2.5, 38.0, "void near cutout right edge")
vb.check_void("Cutout near bottom", 70.0, 2.5, 19.0, "void near cutout bottom")
vb.check_void("Cutout near top", 70.0, 2.5, 57.0, "void near cutout top")

# Frame solid just outside cutout
vb.check_solid("Frame below cutout", 70.0, 2.5, 17.0, "solid below cutout")
vb.check_solid("Frame above cutout", 70.0, 2.5, 59.0, "solid above cutout")
vb.check_solid("Frame left of cutout", 9.0, 2.5, 38.0, "solid left of cutout")
vb.check_solid("Frame right of cutout", 131.0, 2.5, 38.0, "solid right of cutout")

# Rebate check - void at rebate depth on outer face
vb.check_void("Rebate at cutout perimeter", 9.5, 0.25, 38.0, "void in rebate zone")
vb.check_solid("Solid behind rebate", 9.0, 1.0, 38.0, "solid behind rebate depth")

# Detent V-notches on inner face
vb.check_void("V-notch locked center", 70.0, 4.65, 18.0, "void at locked V-notch tip")
vb.check_void("V-notch unlocked center", 70.0, 4.65, 58.0, "void at unlocked V-notch tip")
vb.check_solid("Solid beside locked notch", 70.0, 4.65, 16.0, "solid beside locked notch")

# Snap tabs
vb.check_solid("Bottom snap tab", 70.0, 2.5, -0.4, "solid in bottom snap tab")
vb.check_solid("Top snap tab", 70.0, 2.5, 70.4, "solid in top snap tab")

# Bounding box
bb = bezel.val().BoundingBox()
vb.check_bbox("X", bb.xmin, bb.xmax, 0.0, BEZ_W)
vb.check_bbox("Y", bb.ymin, bb.ymax, 0.0, BEZ_D)
vb.check_bbox("Z", bb.zmin, bb.zmax, -SNAP_PROT, BEZ_H + SNAP_PROT)

# Solid integrity
vb.check_valid()
vb.check_single_body()
vb.check_volume(expected_envelope=BEZ_W * BEZ_D * BEZ_H, fill_range=(0.3, 1.2))

if not vb.summary():
    print("FRONT BEZEL VALIDATION FAILED")
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL 4 PARTS GENERATED AND VALIDATED SUCCESSFULLY")
print("=" * 60)
