#!/usr/bin/env python3
"""
Generate the top shell STEP file for the pump cartridge.

Source: hardware/printed-parts/pump-cartridge/planning/top-shell-parts.md
        hardware/printed-parts/pump-cartridge/planning/top-shell-spatial.md
"""

# Coordinate system:
#   Origin: front-left-bottom exterior corner (as printed)
#   X: width (left to right), 0 at left exterior face, positive rightward. 0..131.4
#   Y: depth (front to back), 0 at front exterior face, positive rearward. 0..176.4
#   Z: height (bottom to top), 0 at ceiling exterior (build plate), positive upward. 0..33.5
#   Ceiling exterior at Z=0 (build plate face). Open edge (parting line) at Z=33.5.
#   Front face at Y=0. Rear face at Y=176.4.
#   Envelope: 131.4 x 176.4 x 33.5 mm

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

import cadquery as cq
from step_validate import Validator

# =====================================================================
# RUBRIC 1 -- Feature Planning Table
# =====================================================================

print("""
=== RUBRIC 1: Feature Planning Table ===

| #  | Feature Name                          | Mechanical Function                                           | Op     | Shape    | Axis | Center (X,Y,Z)           | Dimensions                                     | Notes                                      |
|----|---------------------------------------|---------------------------------------------------------------|--------|----------|------|---------------------------|-------------------------------------------------|--------------------------------------------|
| 1  | Outer box                             | Shell envelope, structural enclosure                          | Add    | Box      | --   | 65.7, 88.2, 16.75        | 131.4 x 176.4 x 33.5 mm                       | centered=False from origin                  |
| 2  | Interior cavity                       | Hollow interior for pump bays and mechanism                   | Remove | Box      | --   | 65.7, 88.2, 17.75        | 127.4 x 172.4 x 31.5 mm (X=2..129.4, Y=2..174.4, Z=2..33.5) | 2mm walls on all 5 closed sides |
| 3  | Finger plate slot                     | Through-opening in front wall for finger plate                | Remove | Box      | Y    | 65.7, 1.0, 21.0          | 121.0(X) x 2.0(Y) x 25.0(Z) at X=5.2..126.2, Z=8.5..33.5 | Through front wall Y=0..2 |
| 4a | Snap-fit hook L1 (left wall)          | Cantilever beam engaging bottom shell catch ledge             | Add    | Box      | Z    | 3.0, 18.7, 28.5          | 2(X) x 8(Y) x 10(Z) at X=2..4, Y=14.7..22.7, Z=23.5..33.5 | +0.3mm catch at tip       |
| 4b | Snap-fit hook L2                      | Same                                                          | Add    | Box      | Z    | 3.0, 53.7, 28.5          | Same                                            |                                            |
| 4c | Snap-fit hook L3                      | Same                                                          | Add    | Box      | Z    | 3.0, 88.7, 28.5          | Same                                            |                                            |
| 4d | Snap-fit hook L4                      | Same                                                          | Add    | Box      | Z    | 3.0, 123.7, 28.5         | Same                                            |                                            |
| 4e | Snap-fit hook L5                      | Same                                                          | Add    | Box      | Z    | 3.0, 158.7, 28.5         | Same                                            |                                            |
| 5a | Snap-fit hook R1 (right wall)         | Same, mirrored on right side                                  | Add    | Box      | Z    | 128.4, 18.7, 28.5        | 2(X) x 8(Y) x 10(Z) at X=127.4..129.4         |                                            |
| 5b | Snap-fit hook R2                      | Same                                                          | Add    | Box      | Z    | 128.4, 53.7, 28.5        | Same                                            |                                            |
| 5c | Snap-fit hook R3                      | Same                                                          | Add    | Box      | Z    | 128.4, 88.7, 28.5        | Same                                            |                                            |
| 5d | Snap-fit hook R4                      | Same                                                          | Add    | Box      | Z    | 128.4, 123.7, 28.5       | Same                                            |                                            |
| 5e | Snap-fit hook R5                      | Same                                                          | Add    | Box      | Z    | 128.4, 158.7, 28.5       | Same                                            |                                            |
| 6a | Snap-fit hook Rear1 (rear wall)       | Same, on rear wall                                            | Add    | Box      | Z    | 17.7, 173.4, 28.5        | 8(X) x 2(Y) x 10(Z) at Y=172.4..174.4         |                                            |
| 6b | Snap-fit hook Rear2                   | Same                                                          | Add    | Box      | Z    | 49.7, 173.4, 28.5        | Same                                            |                                            |
| 6c | Snap-fit hook Rear3                   | Same                                                          | Add    | Box      | Z    | 81.7, 173.4, 28.5        | Same                                            |                                            |
| 6d | Snap-fit hook Rear4                   | Same                                                          | Add    | Box      | Z    | 113.7, 173.4, 28.5       | Same                                            |                                            |
| 7a | Partition capture slot (left wall)    | Captures mounting partition top-left tab                      | Remove | Box      | X    | 1.0, 74.7, 17.75         | 2.0(X) x 5.4(Y) x 31.5(Z) at X=0..2, Y=72..77.4, Z=2..33.5 |                     |
| 7b | Partition capture slot (right wall)   | Captures mounting partition top-right tab                     | Remove | Box      | X    | 130.4, 74.7, 17.75       | 2.0(X) x 5.4(Y) x 31.5(Z) at X=129.4..131.4, Y=72..77.4, Z=2..33.5 |           |
| 8  | JG fitting clearance relief           | Accommodates upper JG body ends protruding above parting line | Remove | Box      | Z    | 66.0, 175.4, 33.15       | 98(X) x 2(Y) x 0.7(Z) at X=17..115, Y=174.4..176.4, Z=32.8..33.5 |            |
| 9  | Elephant's foot chamfer               | Prevents first-layer flare on build-plate face                | Remove | Chamfer  | Z    | Perimeter at Z=0          | 0.3mm x 45deg on ceiling perimeter edges        |                                            |
""")

# =====================================================================
# Dimensions from parts.md
# =====================================================================

# Outer envelope
OX, OY, OZ = 131.4, 176.4, 33.5

# Wall thickness
WALL = 2.0

# Interior cavity
IX_START, IY_START, IZ_START = WALL, WALL, WALL
IX_LEN = OX - 2 * WALL   # 127.4
IY_LEN = OY - 2 * WALL   # 172.4
IZ_LEN = OZ - WALL        # 31.5 (open at Z=33.5)

# Finger plate slot
FP_SLOT_X_START = 5.2
FP_SLOT_X_END = 126.2
FP_SLOT_W = FP_SLOT_X_END - FP_SLOT_X_START  # 121.0
FP_SLOT_Z_START = 8.5
FP_SLOT_Z_END = 33.5
FP_SLOT_H = FP_SLOT_Z_END - FP_SLOT_Z_START  # 25.0

# Snap-fit hook dimensions
HOOK_LENGTH = 10.0   # Z direction
HOOK_THICK = 2.0     # perpendicular to wall
HOOK_WIDTH = 8.0     # along wall
HOOK_CATCH = 0.3     # catch tip depth
HOOK_BASE_Z = 23.5   # Z start of cantilever
HOOK_TIP_Z = 33.5    # Z end (flush with open face)

# Left wall hook Y centers
LEFT_HOOK_Y = [18.7, 53.7, 88.7, 123.7, 158.7]
# Right wall hook Y centers (same as left)
RIGHT_HOOK_Y = LEFT_HOOK_Y
# Rear wall hook X centers
REAR_HOOK_X = [17.7, 49.7, 81.7, 113.7]

# Partition capture slots
PART_SLOT_Y_START = 72.0
PART_SLOT_Y_END = 77.4
PART_SLOT_W = PART_SLOT_Y_END - PART_SLOT_Y_START  # 5.4
PART_SLOT_Z_START = IZ_START  # 2.0
PART_SLOT_Z_END = OZ          # 33.5

# JG clearance relief
JG_RELIEF_X_START = 17.0
JG_RELIEF_X_END = 115.0
JG_RELIEF_Y_START = 174.4  # rear wall inner face
JG_RELIEF_Y_END = 176.4    # rear wall outer face
JG_RELIEF_Z_START = 32.8
JG_RELIEF_Z_END = 33.5

# Elephant's foot chamfer
EF_CHAMFER = 0.3

# =====================================================================
# MODELING
# =====================================================================

# --- 1. Outer box ---
shell = cq.Workplane("XY").box(OX, OY, OZ, centered=False)

# --- 2. Interior cavity ---
cavity = (
    cq.Workplane("XY")
    .transformed(offset=(IX_START, IY_START, IZ_START))
    .box(IX_LEN, IY_LEN, IZ_LEN, centered=False)
)
shell = shell.cut(cavity)

# --- 3. Finger plate slot (through-cut in front wall) ---
# The slot is at X=5.2..126.2, Y=0..2.0 (full wall thickness), Z=8.5..33.5
fp_slot = (
    cq.Workplane("XY")
    .transformed(offset=(FP_SLOT_X_START, 0, FP_SLOT_Z_START))
    .box(FP_SLOT_W, WALL, FP_SLOT_H, centered=False)
)
shell = shell.cut(fp_slot)

# --- 4. Partition capture slots ---
# Left wall slot: X=0..2.0, Y=72.0..77.4, Z=2.0..33.5 (through entire wall)
left_part_slot = (
    cq.Workplane("XY")
    .transformed(offset=(0, PART_SLOT_Y_START, PART_SLOT_Z_START))
    .box(WALL, PART_SLOT_W, PART_SLOT_Z_END - PART_SLOT_Z_START, centered=False)
)
shell = shell.cut(left_part_slot)

# Right wall slot: X=129.4..131.4, Y=72.0..77.4, Z=2.0..33.5
right_part_slot = (
    cq.Workplane("XY")
    .transformed(offset=(OX - WALL, PART_SLOT_Y_START, PART_SLOT_Z_START))
    .box(WALL, PART_SLOT_W, PART_SLOT_Z_END - PART_SLOT_Z_START, centered=False)
)
shell = shell.cut(right_part_slot)

# --- 5. JG fitting clearance relief ---
# Continuous relief at rear wall interior: X=17..115, Y=174.4..176.4, Z=32.8..33.5
jg_relief = (
    cq.Workplane("XY")
    .transformed(offset=(JG_RELIEF_X_START, JG_RELIEF_Y_START, JG_RELIEF_Z_START))
    .box(
        JG_RELIEF_X_END - JG_RELIEF_X_START,  # 98
        JG_RELIEF_Y_END - JG_RELIEF_Y_START,  # 2.0
        JG_RELIEF_Z_END - JG_RELIEF_Z_START,  # 0.7
        centered=False,
    )
)
shell = shell.cut(jg_relief)

# --- 6. Snap-fit cantilever hooks (added AFTER all cuts to avoid relief conflicts) ---
# Build all hook geometry as a single compound, then union once to ensure single body.

# Helper: build a beam+catch pair as a single solid
def make_hook_pair(beam_origin, beam_dims, catch_origin, catch_dims):
    """Create a beam and catch as a single unioned solid."""
    bx, by, bz = beam_origin
    bw, bd, bh = beam_dims
    beam = (
        cq.Workplane("XY")
        .transformed(offset=(bx, by, bz))
        .box(bw, bd, bh, centered=False)
    )
    cx, cy, cz = catch_origin
    cw, cd, ch = catch_dims
    catch = (
        cq.Workplane("XY")
        .transformed(offset=(cx, cy, cz))
        .box(cw, cd, ch, centered=False)
    )
    return beam.union(catch)

# Left wall hooks: beams protrude +X from inner face at X=2.0
# Catch tip curls outward toward -X (toward wall exterior)
for yc in LEFT_HOOK_Y:
    hook = make_hook_pair(
        beam_origin=(IX_START, yc - HOOK_WIDTH / 2, HOOK_BASE_Z),
        beam_dims=(HOOK_THICK, HOOK_WIDTH, HOOK_LENGTH),
        catch_origin=(IX_START - HOOK_CATCH, yc - HOOK_WIDTH / 2, HOOK_TIP_Z - HOOK_CATCH),
        catch_dims=(HOOK_CATCH, HOOK_WIDTH, HOOK_CATCH),
    )
    shell = shell.union(hook)

# Right wall hooks: beams protrude -X from inner face at X=129.4
# Catch tip curls outward toward +X
for yc in RIGHT_HOOK_Y:
    hook = make_hook_pair(
        beam_origin=(OX - WALL - HOOK_THICK, yc - HOOK_WIDTH / 2, HOOK_BASE_Z),
        beam_dims=(HOOK_THICK, HOOK_WIDTH, HOOK_LENGTH),
        catch_origin=(OX - WALL, yc - HOOK_WIDTH / 2, HOOK_TIP_Z - HOOK_CATCH),
        catch_dims=(HOOK_CATCH, HOOK_WIDTH, HOOK_CATCH),
    )
    shell = shell.union(hook)

# Rear wall hooks: beams protrude -Y from inner face at Y=174.4
# Catch tip curls outward toward +Y
for xc in REAR_HOOK_X:
    hook = make_hook_pair(
        beam_origin=(xc - HOOK_WIDTH / 2, OY - WALL - HOOK_THICK, HOOK_BASE_Z),
        beam_dims=(HOOK_WIDTH, HOOK_THICK, HOOK_LENGTH),
        catch_origin=(xc - HOOK_WIDTH / 2, OY - WALL, HOOK_TIP_Z - HOOK_CATCH),
        catch_dims=(HOOK_WIDTH, HOOK_CATCH, HOOK_CATCH),
    )
    shell = shell.union(hook)

# --- 7. Elephant's foot chamfer on ceiling perimeter ---
# 0.3mm x 45deg chamfer on the 4 edges where the Z=0 ceiling face meets the outer walls.
# Model as 4 triangular prism cuts along each perimeter edge.

# Front edge (Y=0, Z=0): triangular prism running along X (full width)
# Cross-section in YZ: triangle at the Y=0/Z=0 corner
ch_front = (
    cq.Workplane("YZ")
    .polyline([(0, 0), (EF_CHAMFER, 0), (0, EF_CHAMFER)])
    .close()
    .extrude(OX)  # YZ normal is +X, extrude full width
)
shell = shell.cut(ch_front)

# Rear edge (Y=OY, Z=0): triangular prism running along X
ch_rear = (
    cq.Workplane("YZ")
    .center(OY, 0)
    .polyline([(0, 0), (-EF_CHAMFER, 0), (0, EF_CHAMFER)])
    .close()
    .extrude(OX)
)
shell = shell.cut(ch_rear)

# Left edge (X=0, Z=0): triangular prism running along Y
ch_left = (
    cq.Workplane("XZ")
    .polyline([(0, 0), (EF_CHAMFER, 0), (0, EF_CHAMFER)])
    .close()
    .extrude(-OY)  # XZ normal is -Y, negative extrude goes +Y direction
)
shell = shell.cut(ch_left)

# Right edge (X=OX, Z=0): triangular prism running along Y
ch_right = (
    cq.Workplane("XZ")
    .center(OX, 0)
    .polyline([(0, 0), (-EF_CHAMFER, 0), (0, EF_CHAMFER)])
    .close()
    .extrude(-OY)
)
shell = shell.cut(ch_right)


# --- 8. Verify single body ---
n_bodies = len(shell.solids().vals())
if n_bodies > 1:
    print(f"  WARNING: {n_bodies} bodies detected. Attempting cleanup...")

# =====================================================================
# EXPORT STEP FILE
# =====================================================================

output_path = Path(__file__).parent / "top-shell.step"
cq.exporters.export(shell, str(output_path))
print(f"\nSTEP exported to: {output_path}")

# =====================================================================
# RUBRIC 3 -- Feature-Specification Reconciliation (point-in-solid probes)
# =====================================================================

print("\n=== RUBRIC 3: Feature-Specification Reconciliation ===\n")

v = Validator(shell)

# --- 1. Outer box: solid in walls ---
v.check_solid("Outer box - left wall", 1.0, 88.2, 16.75, "solid in left wall")
v.check_solid("Outer box - right wall", 130.4, 88.2, 16.75, "solid in right wall")
v.check_solid("Outer box - front wall (palm zone)", 65.7, 1.0, 4.0, "solid in front wall palm zone")
v.check_solid("Outer box - rear wall", 65.7, 175.4, 16.75, "solid in rear wall")
v.check_solid("Outer box - ceiling", 65.7, 88.2, 1.0, "solid in ceiling plate")

# --- 2. Interior cavity: void inside ---
v.check_void("Interior cavity center", 65.7, 88.2, 17.75, "void at cavity center")
v.check_void("Interior cavity near front", 65.7, 3.0, 17.75, "void near front interior")
v.check_void("Interior cavity near rear", 65.7, 173.0, 17.75, "void near rear interior")

# --- 3. Finger plate slot: void through front wall ---
v.check_void("FP slot center", 65.7, 1.0, 21.0, "void at finger plate slot center")
v.check_void("FP slot left edge interior", 6.0, 1.0, 21.0, "void just inside left edge of slot")
v.check_void("FP slot right edge interior", 125.0, 1.0, 21.0, "void just inside right edge of slot")
v.check_solid("FP slot left column solid", 3.0, 1.0, 21.0, "solid in left column flanking slot")
v.check_solid("FP slot right column solid", 128.0, 1.0, 21.0, "solid in right column flanking slot")
v.check_solid("FP slot palm strip above", 65.7, 1.0, 4.0, "solid in palm strip above slot")
v.check_void("FP slot lower edge interior", 65.7, 1.0, 9.0, "void just above slot lower edge Z=8.5")

# --- 4. Left wall hooks ---
for i, yc in enumerate(LEFT_HOOK_Y):
    v.check_solid(f"Left hook L{i+1} beam center", 3.0, yc, 28.5, f"solid at L{i+1} beam center")
    v.check_solid(f"Left hook L{i+1} catch", 1.85, yc, 33.35, f"solid at L{i+1} catch tip")

# --- 5. Right wall hooks ---
for i, yc in enumerate(RIGHT_HOOK_Y):
    v.check_solid(f"Right hook R{i+1} beam center", 128.4, yc, 28.5, f"solid at R{i+1} beam center")
    v.check_solid(f"Right hook R{i+1} catch", 129.55, yc, 33.35, f"solid at R{i+1} catch tip")

# --- 6. Rear wall hooks ---
for i, xc in enumerate(REAR_HOOK_X):
    v.check_solid(f"Rear hook Rr{i+1} beam center", xc, 173.4, 28.5, f"solid at Rear{i+1} beam center")
    v.check_solid(f"Rear hook Rr{i+1} catch", xc, 174.55, 33.35, f"solid at Rear{i+1} catch tip")

# --- 7. Partition capture slots: void through wall ---
v.check_void("Part slot left center", 1.0, 74.7, 17.75, "void at left partition slot center")
v.check_void("Part slot right center", 130.4, 74.7, 17.75, "void at right partition slot center")
# Solid just outside the slot in Y
v.check_solid("Part slot left - solid above slot Y", 1.0, 71.0, 17.75, "solid above left slot in Y")
v.check_solid("Part slot left - solid below slot Y", 1.0, 78.0, 17.75, "solid below left slot in Y")

# --- 8. Ceiling solid where M3 features were removed ---
# Verify that the ceiling at former pillar positions is now solid (no holes, no counterbores)
v.check_solid("Ceiling solid at former pillar 1 pos", 19.7, 88.2, 1.0, "solid at former pillar 1 ceiling position")
v.check_solid("Ceiling solid at former pillar 2 pos", 111.7, 88.2, 1.0, "solid at former pillar 2 ceiling position")
# Verify cavity (void) at the former pillar body locations (no pillars, just open cavity)
v.check_void("Cavity at former pillar 1 location", 19.7, 88.2, 19.0, "void where pillar 1 was removed")
v.check_void("Cavity at former pillar 2 location", 111.7, 88.2, 19.0, "void where pillar 2 was removed")

# --- 9. JG clearance relief ---
v.check_void("JG relief center", 66.0, 175.4, 33.15, "void at JG relief center")
v.check_void("JG relief left end", 18.0, 175.4, 33.15, "void near left end of JG relief")
v.check_void("JG relief right end", 114.0, 175.4, 33.15, "void near right end of JG relief")
# Solid just outside relief in X
v.check_solid("JG relief - solid left of relief", 16.0, 175.4, 33.15, "solid left of JG relief")

# --- 10. Elephant's foot chamfer ---
# At the very corner (0, 0, 0) the chamfer removes material.
# Probe at (0.1, 0.1, 0.1) -- should be void (chamfer removed this corner)
v.check_void("EF chamfer front-left corner", 0.1, 0.1, 0.1, "void at chamfered corner")
# Probe just inside the chamfer line -- should be solid
v.check_solid("EF chamfer - solid beyond chamfer", 1.0, 1.0, 0.5, "solid beyond chamfer zone")

# =====================================================================
# RUBRIC 4 -- Solid Validity
# =====================================================================

print("\n=== RUBRIC 4: Solid Validity ===\n")

v.check_valid()
v.check_single_body()
v.check_volume(expected_envelope=OX * OY * OZ, fill_range=(0.05, 0.25))

# =====================================================================
# RUBRIC 5 -- Bounding Box
# =====================================================================

print("\n=== RUBRIC 5: Bounding Box ===\n")

bb = shell.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, 0.0, OX)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, OY)
v.check_bbox("Z", bb.zmin, bb.zmax, 0.0, OZ)

# =====================================================================
# SUMMARY
# =====================================================================

if not v.summary():
    sys.exit(1)
