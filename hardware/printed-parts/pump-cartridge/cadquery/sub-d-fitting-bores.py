"""
Sub-D Fitting Bore Array — CadQuery Generation Script

Produces TWO STEP files:
  1. sub-d-fitting-bores-union.step  — bore plate bosses (material to ADD to tray)
  2. sub-d-fitting-bores-cut.step    — bore cuts + rear wall clearances (material to REMOVE)

The composition agent unions the bosses into the tray, then subtracts the bore cuts.

Coordinate system (tray frame):
  Origin: rear-left-bottom corner of tray outer envelope
  X: width, left to right (0..160)
  Y: depth, dock face to user side (0..155)
  Z: height, bottom to top (0..72)
  Bosses envelope: X:[60,100] Y:[8.5,42.2] Z:[16,56]
  Bore cuts envelope: X:[62.25,97.75] Y:[0,42.2] Z:[18.25,53.75]
"""

import math
import sys
from pathlib import Path

# Add tools/ to path for step_validate
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq
from step_validate import Validator

# ============================================================
# Feature Planning Table (Rubric 1)
# ============================================================
print("""
Feature Planning Table — Sub-D Fitting Bore Array
===================================================================
# | Feature Name              | Function                        | Op     | Shape    | Axis | Center (X,Y,Z)    | Dimensions                              | Notes
--|---------------------------|---------------------------------|--------|----------|------|--------------------|-----------------------------------------|------
1 | Bore plate boss 1         | Houses fitting 1 press-fit      | Add    | Cylinder | Y    | (70, 25.35, 26)    | OD=20, Y:8.5..42.2 (L=33.7)            | Merges with adjacent
2 | Bore plate boss 2         | Houses fitting 2 press-fit      | Add    | Cylinder | Y    | (90, 25.35, 26)    | OD=20, Y:8.5..42.2 (L=33.7)            | Merges with adjacent
3 | Bore plate boss 3         | Houses fitting 3 press-fit      | Add    | Cylinder | Y    | (70, 25.35, 46)    | OD=20, Y:8.5..42.2 (L=33.7)            | Merges with adjacent
4 | Bore plate boss 4         | Houses fitting 4 press-fit      | Add    | Cylinder | Y    | (90, 25.35, 46)    | OD=20, Y:8.5..42.2 (L=33.7)            | Merges with adjacent
5 | Dock-side counterbore 1   | Recess fitting dock shoulder    | Remove | Cylinder | Y    | (70, 27.0, 26)     | D=15.5, Y:26..28 (depth=2)             | Part of stepped bore
6 | Press-fit bore 1          | Grip fitting center body        | Remove | Cylinder | Y    | (70, 34.1, 26)     | D=9.5, Y:28..40.2 (depth=12.2)         | 0.19mm interference
7 | User-side counterbore 1   | Recess fitting user shoulder    | Remove | Cylinder | Y    | (70, 41.2, 26)     | D=15.5, Y:40.2..42.2 (depth=2)         | Part of stepped bore
8 | Dock-side counterbore 2   | Recess fitting dock shoulder    | Remove | Cylinder | Y    | (90, 27.0, 26)     | D=15.5, Y:26..28 (depth=2)             |
9 | Press-fit bore 2          | Grip fitting center body        | Remove | Cylinder | Y    | (90, 34.1, 26)     | D=9.5, Y:28..40.2 (depth=12.2)         |
10| User-side counterbore 2   | Recess fitting user shoulder    | Remove | Cylinder | Y    | (90, 41.2, 26)     | D=15.5, Y:40.2..42.2 (depth=2)         |
11| Dock-side counterbore 3   | Recess fitting dock shoulder    | Remove | Cylinder | Y    | (70, 27.0, 46)     | D=15.5, Y:26..28 (depth=2)             |
12| Press-fit bore 3          | Grip fitting center body        | Remove | Cylinder | Y    | (70, 34.1, 46)     | D=9.5, Y:28..40.2 (depth=12.2)         |
13| User-side counterbore 3   | Recess fitting user shoulder    | Remove | Cylinder | Y    | (70, 41.2, 46)     | D=15.5, Y:40.2..42.2 (depth=2)         |
14| Dock-side counterbore 4   | Recess fitting dock shoulder    | Remove | Cylinder | Y    | (90, 27.0, 46)     | D=15.5, Y:26..28 (depth=2)             |
15| Press-fit bore 4          | Grip fitting center body        | Remove | Cylinder | Y    | (90, 34.1, 46)     | D=9.5, Y:28..40.2 (depth=12.2)         |
16| User-side counterbore 4   | Recess fitting user shoulder    | Remove | Cylinder | Y    | (90, 41.2, 46)     | D=15.5, Y:40.2..42.2 (depth=2)         |
17| Rear wall tube bore 1     | Clearance for dock tube         | Remove | Cylinder | Y    | (70, 5.25, 26)     | D=8, Y:2..8.5 (depth=6.5)              | 0.825mm radial clear
18| Entry funnel 1            | Guide tube into bore            | Remove | Cone     | Y    | (70, 1.0, 26)      | D1=12@Y=0, D2=8@Y=2 (depth=2, 45deg)  |
19| Rear wall tube bore 2     | Clearance for dock tube         | Remove | Cylinder | Y    | (90, 5.25, 26)     | D=8, Y:2..8.5 (depth=6.5)              |
20| Entry funnel 2            | Guide tube into bore            | Remove | Cone     | Y    | (90, 1.0, 26)      | D1=12@Y=0, D2=8@Y=2 (depth=2, 45deg)  |
21| Rear wall tube bore 3     | Clearance for dock tube         | Remove | Cylinder | Y    | (70, 5.25, 46)     | D=8, Y:2..8.5 (depth=6.5)              |
22| Entry funnel 3            | Guide tube into bore            | Remove | Cone     | Y    | (70, 1.0, 46)      | D1=12@Y=0, D2=8@Y=2 (depth=2, 45deg)  |
23| Rear wall tube bore 4     | Clearance for dock tube         | Remove | Cylinder | Y    | (90, 5.25, 46)     | D=8, Y:2..8.5 (depth=6.5)              |
24| Entry funnel 4            | Guide tube into bore            | Remove | Cone     | Y    | (90, 1.0, 46)      | D1=12@Y=0, D2=8@Y=2 (depth=2, 45deg)  |
===================================================================
""")

# ============================================================
# Parameters (all from spec)
# ============================================================

# Bore center positions (X, Z)
BORE_CENTERS = [
    (70.0, 26.0),   # Bore 1: lower-left (pump 1 inlet)
    (90.0, 26.0),   # Bore 2: lower-right (pump 1 outlet)
    (70.0, 46.0),   # Bore 3: upper-left (pump 2 inlet)
    (90.0, 46.0),   # Bore 4: upper-right (pump 2 outlet)
]

# Boss dimensions
BOSS_OD = 20.0          # mm, outer diameter
BOSS_R = BOSS_OD / 2    # 10.0 mm radius
BOSS_Y_START = 8.5      # mm, rear wall interior face
BOSS_Y_END = 42.2       # mm, user-side counterbore outer face
BOSS_LENGTH = BOSS_Y_END - BOSS_Y_START  # 33.7 mm

# Stepped bore dimensions (along Y axis)
CB_DOCK_DIA = 15.5      # mm, dock-side counterbore diameter
CB_DOCK_Y_START = 26.0  # mm
CB_DOCK_Y_END = 28.0    # mm
CB_DOCK_DEPTH = 2.0     # mm

PF_BORE_DIA = 9.5       # mm, press-fit bore diameter
PF_BORE_Y_START = 28.0  # mm
PF_BORE_Y_END = 40.2    # mm
PF_BORE_DEPTH = 12.2    # mm

CB_USER_DIA = 15.5      # mm, user-side counterbore diameter
CB_USER_Y_START = 40.2  # mm
CB_USER_Y_END = 42.2    # mm
CB_USER_DEPTH = 2.0     # mm

# Rear wall tube bore
TUBE_BORE_DIA = 8.0     # mm
TUBE_BORE_Y_START = 2.0 # mm (after funnel)
TUBE_BORE_Y_END = 8.5   # mm (rear wall interior)
TUBE_BORE_DEPTH = 6.5   # mm

# Entry funnel
FUNNEL_LARGE_DIA = 12.0 # mm at Y=0
FUNNEL_SMALL_DIA = 8.0  # mm at Y=2
FUNNEL_Y_START = 0.0    # mm (dock face)
FUNNEL_Y_END = 2.0      # mm
FUNNEL_DEPTH = 2.0      # mm

# ============================================================
# Model: Bore Plate Bosses (union solid)
# ============================================================
# 4 cylinders along Y axis, centered at bore positions in XZ plane.
# CadQuery cylinder: workplane normal = cylinder axis.
# We work on XZ plane at Y=BOSS_Y_START, extrude along -Y normal
# which goes +Y (XZ normal is -Y, negative extrude = +Y direction).
# Actually: XZ workplane normal is -Y. extrude(positive) goes -Y.
# We want bosses from Y=8.5 to Y=42.2 (toward +Y).
# So: place workplane at offset, extrude negatively = goes +Y? No.
#
# Simpler approach: build cylinders on XY plane and translate.
# A cylinder on XY plane with height h extends from Z=0 to Z=h.
# We need cylinders along Y axis. So we'll build them using
# the XZ workplane approach, or just construct them with transformed
# workplanes.
#
# Best approach: use workplane("XZ") at a Y offset, draw circle, extrude.
# XZ normal = -Y. extrude(L) goes in -Y direction.
# We want material from Y=8.5 to Y=42.2.
# Place workplane at Y=42.2 (user side), extrude 33.7mm in -Y direction.

print("Building bore plate bosses...")

# Build 4 cylinders and union them. At 20mm center-to-center with 20mm OD,
# adjacent bosses touch tangentially (0mm overlap). CAD boolean union fails
# to fuse tangent-touching bodies, so we use a tiny radius increase (0.01mm)
# to create a guaranteed 0.02mm overlap at tangent points. This is sub-
# printer-resolution and has no mechanical effect.
BOSS_R_CAD = BOSS_R + 0.01  # 10.01 mm for CAD fusion

boss_list = []
for i, (cx, cz) in enumerate(BORE_CENTERS):
    # Create cylinder: circle on XZ plane at Y=42.2, extrude 33.7mm along -Y
    boss = (
        cq.Workplane("XZ")
        .workplane(offset=-BOSS_Y_END)  # XZ normal is -Y, offset=-42.2 puts plane at Y=42.2
        .center(cx, cz)
        .circle(BOSS_R_CAD)
        .extrude(BOSS_LENGTH)  # extrude along -Y normal = toward -Y, i.e., Y=42.2 to Y=8.5
    )
    boss_list.append(boss)

# Union all bosses
bosses = boss_list[0]
for b in boss_list[1:]:
    bosses = bosses.union(b)

print(f"  Bosses built: 4 cylinders (R={BOSS_R_CAD}mm for CAD fusion), Y=[{BOSS_Y_START}, {BOSS_Y_END}]")

# ============================================================
# Model: Bore Cuts (cut solid)
# ============================================================
# For each bore position: stepped bore through boss + rear wall clearance + funnel
# All features are along Y axis.
# Use revolved profiles for the stepped bores and rear wall bores.

print("Building bore cuts...")

cuts = None
for i, (cx, cz) in enumerate(BORE_CENTERS):
    # --- Stepped bore through boss (Y=26.0 to Y=42.2) ---
    # Profile in (R, Y_local) where Y_local=0 is at Y=26.0 (dock-side counterbore start)
    # Revolve around the Y axis (which is the bore axis).
    # The bore total Y range: 26.0 to 42.2 = 16.2mm
    #
    # Y_local mapping:
    #   0.0  = Y=26.0 (dock-side counterbore start)
    #   2.0  = Y=28.0 (dock-side counterbore end / press-fit start)
    #  14.2  = Y=40.2 (press-fit end / user-side counterbore start)
    #  16.2  = Y=42.2 (user-side counterbore end)

    bore_profile = [
        (0,              0),      # axis at dock-side counterbore start
        (CB_DOCK_DIA/2,  0),      # dock counterbore radius = 7.75
        (CB_DOCK_DIA/2,  CB_DOCK_DEPTH),  # dock counterbore end at 2.0
        (PF_BORE_DIA/2,  CB_DOCK_DEPTH),  # step to press-fit radius = 4.75
        (PF_BORE_DIA/2,  CB_DOCK_DEPTH + PF_BORE_DEPTH),  # press-fit end at 14.2
        (CB_USER_DIA/2,  CB_DOCK_DEPTH + PF_BORE_DEPTH),  # step to user counterbore = 7.75
        (CB_USER_DIA/2,  CB_DOCK_DEPTH + PF_BORE_DEPTH + CB_USER_DEPTH),  # user CB end at 16.2
        (0,              CB_DOCK_DEPTH + PF_BORE_DEPTH + CB_USER_DEPTH),  # axis at user end
    ]

    # Build the revolved solid on XY plane (revolve about Y axis)
    # Profile is in (R, Y) = (x, y) on XY plane, revolve around (0,0)-(0,1) = Y axis
    stepped_bore = (
        cq.Workplane("XY")
        .polyline(bore_profile)
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )
    # Translate to bore position: cx in X, CB_DOCK_Y_START in Y, cz in Z
    stepped_bore = stepped_bore.translate((cx, CB_DOCK_Y_START, cz))

    # --- Rear wall tube bore (Y=2.0 to Y=8.5) ---
    tube_bore = (
        cq.Workplane("XZ")
        .workplane(offset=-TUBE_BORE_Y_END)  # plane at Y=8.5
        .center(cx, cz)
        .circle(TUBE_BORE_DIA / 2)
        .extrude(TUBE_BORE_DEPTH)  # extrude -Y direction: Y=8.5 to Y=2.0
    )

    # --- Entry funnel (Y=0 to Y=2.0) ---
    # Conical from 12mm dia at Y=0 to 8mm dia at Y=2.0
    # Profile points (R, Y_local) where Y_local=0 is Y=0:
    funnel_profile = [
        (0,                    0),                # axis at dock face
        (FUNNEL_LARGE_DIA/2,   0),                # funnel mouth radius = 6.0
        (FUNNEL_SMALL_DIA/2,   FUNNEL_DEPTH),     # funnel throat radius = 4.0
        (0,                    FUNNEL_DEPTH),      # axis at funnel end
    ]

    funnel = (
        cq.Workplane("XY")
        .polyline(funnel_profile)
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )
    # Translate: Y_local=0 maps to Y=0 (dock face)
    funnel = funnel.translate((cx, FUNNEL_Y_START, cz))

    # --- Connecting cylinder (Y=8.5 to Y=26.0) ---
    # Bridges the gap between rear wall bore exit and dock-side counterbore entry.
    # Uses press-fit bore diameter. This region is interior air space in the tray,
    # so the connecting cylinder has no mechanical effect — it just ensures a
    # single connected body for the composition agent.
    CONNECT_Y_START = TUBE_BORE_Y_END   # 8.5
    CONNECT_Y_END = CB_DOCK_Y_START     # 26.0
    CONNECT_DEPTH = CONNECT_Y_END - CONNECT_Y_START  # 17.5
    connector = (
        cq.Workplane("XZ")
        .workplane(offset=-CONNECT_Y_END)  # plane at Y=26.0
        .center(cx, cz)
        .circle(PF_BORE_DIA / 2)  # 4.75mm radius
        .extrude(CONNECT_DEPTH)  # extrude -Y direction: Y=26.0 to Y=8.5
    )

    # Union all cut features for this bore
    bore_cut = stepped_bore.union(tube_bore).union(funnel).union(connector)

    if cuts is None:
        cuts = bore_cut
    else:
        cuts = cuts.union(bore_cut)

print(f"  Bore cuts built: 4x (stepped bore + tube bore + funnel)")

# ============================================================
# Export STEP files
# ============================================================
script_dir = Path(__file__).resolve().parent
union_path = script_dir / "sub-d-fitting-bores-union.step"
cut_path = script_dir / "sub-d-fitting-bores-cut.step"

cq.exporters.export(bosses, str(union_path))
print(f"\nExported bosses (union): {union_path}")

cq.exporters.export(cuts, str(cut_path))
print(f"Exported bore cuts (cut): {cut_path}")

# ============================================================
# Validation: Bosses (union solid)
# ============================================================
print("\n--- Validating BOSSES (union solid) ---")
vb = Validator(bosses)

# Check boss material at center of each boss
for i, (cx, cz) in enumerate(BORE_CENTERS):
    mid_y = (BOSS_Y_START + BOSS_Y_END) / 2  # 25.35
    # Solid at boss center (but note bores aren't cut from bosses — bosses are pure cylinders)
    vb.check_solid(f"Boss {i+1} center", cx, mid_y, cz,
                   f"solid at boss {i+1} center ({cx}, {mid_y:.1f}, {cz})")
    # Solid at boss edge (just inside OD)
    vb.check_solid(f"Boss {i+1} edge -X", cx - BOSS_R + 0.5, mid_y, cz,
                   f"solid just inside boss {i+1} -X edge")
    # Void outside boss OD — probe diagonally outward from grid center (80,36)
    # to avoid hitting adjacent bosses. Direction: away from (80,36).
    dx = cx - 80.0  # -10 or +10
    dz = cz - 36.0  # -10 or +10
    dist = math.sqrt(dx*dx + dz*dz)  # 14.14
    # Probe at boss_center + (BOSS_R + 2.0) in the outward diagonal direction
    probe_dist = BOSS_R + 2.0  # 12.0 — well outside the 10.01 radius
    px = cx + dx / dist * probe_dist
    pz = cz + dz / dist * probe_dist
    vb.check_void(f"Boss {i+1} outside diagonal", px, mid_y, pz,
                  f"void outside boss {i+1} diagonal edge ({px:.1f}, {mid_y:.1f}, {pz:.1f})")

# Check boss Y extent
for i, (cx, cz) in enumerate(BORE_CENTERS):
    vb.check_solid(f"Boss {i+1} near base", cx, BOSS_Y_START + 1.5, cz,
                   f"solid near boss {i+1} base (Y={BOSS_Y_START + 1.5})")
    vb.check_solid(f"Boss {i+1} near tip", cx, BOSS_Y_END - 0.5, cz,
                   f"solid near boss {i+1} tip (Y={BOSS_Y_END - 0.5})")
    vb.check_void(f"Boss {i+1} below base", cx, BOSS_Y_START - 1.0, cz,
                  f"void below boss {i+1} base (Y={BOSS_Y_START - 1.0})")
    vb.check_void(f"Boss {i+1} above tip", cx, BOSS_Y_END + 1.0, cz,
                  f"void above boss {i+1} tip (Y={BOSS_Y_END + 1.0})")

# Check boss merge (between adjacent bosses — should be solid at midpoint)
# Between boss 1 (70,26) and boss 2 (90,26): midpoint X=80, Z=26
vb.check_solid("Boss merge 1-2", 80.0, 25.35, 26.0,
               "solid at midpoint between boss 1 and 2 (merged)")
# Between boss 3 (70,46) and boss 4 (90,46): midpoint X=80, Z=46
vb.check_solid("Boss merge 3-4", 80.0, 25.35, 46.0,
               "solid at midpoint between boss 3 and 4 (merged)")
# Between boss 1 (70,26) and boss 3 (70,46): midpoint X=70, Z=36
vb.check_solid("Boss merge 1-3", 70.0, 25.35, 36.0,
               "solid at midpoint between boss 1 and 3 (merged)")
# Between boss 2 (90,26) and boss 4 (90,46): midpoint X=90, Z=36
vb.check_solid("Boss merge 2-4", 90.0, 25.35, 36.0,
               "solid at midpoint between boss 2 and 4 (merged)")
# Center of all 4 (80, 36) — check this is void (outside all 4 circles by sqrt(200)-10 ≈ 4.14mm)
# Wait: distance from (80,36) to (70,26) = sqrt(100+100) = 14.14 > 10. So center is void.
vb.check_void("Center gap (80,36)", 80.0, 25.35, 36.0,
              "void at center of 4-boss grid (outside all radii)")

# Bounding box
bb_b = bosses.val().BoundingBox()
vb.check_bbox("X", bb_b.xmin, bb_b.xmax, 60.0, 100.0)
vb.check_bbox("Y", bb_b.ymin, bb_b.ymax, BOSS_Y_START, BOSS_Y_END)
vb.check_bbox("Z", bb_b.zmin, bb_b.zmax, 16.0, 56.0)

# Solid validity
vb.check_valid()
vb.check_single_body()
# Volume: 4 overlapping cylinders. Each = pi*10^2*33.7 = 10586 mm³. Total < 4*10586 due to overlap.
# But adjacent pairs overlap significantly. Rough estimate: ~35000 mm³
# Envelope box = 40 * 33.7 * 40 = 53920
vb.check_volume(expected_envelope=40 * BOSS_LENGTH * 40, fill_range=(0.5, 1.0))

if not vb.summary():
    print("\nBOSSES VALIDATION FAILED")
    sys.exit(1)

# ============================================================
# Validation: Bore Cuts (cut solid)
# ============================================================
print("\n--- Validating BORE CUTS (cut solid) ---")
vc = Validator(cuts)

for i, (cx, cz) in enumerate(BORE_CENTERS):
    # --- Stepped bore checks ---
    # Dock-side counterbore center (Y=27.0, mid of 26..28)
    vc.check_solid(f"Bore {i+1} dock CB center", cx, 27.0, cz,
                   f"solid at dock counterbore center (part of cut tool)")
    # Verify counterbore radius: solid at r=7.5 (inside 7.75), void at r=8.0 (outside 7.75)
    vc.check_solid(f"Bore {i+1} dock CB edge inside", cx + CB_DOCK_DIA/2 - 0.5, 27.0, cz,
                   f"solid just inside dock CB edge")
    vc.check_void(f"Bore {i+1} dock CB edge outside", cx + CB_DOCK_DIA/2 + 0.5, 27.0, cz,
                  f"void just outside dock CB edge")

    # Press-fit bore center (Y=34.1, mid of 28..40.2)
    vc.check_solid(f"Bore {i+1} PF center", cx, 34.1, cz,
                   f"solid at press-fit bore center")
    # Verify press-fit radius: solid at r=4.5 (inside 4.75), void at r=5.0 (outside 4.75)
    vc.check_solid(f"Bore {i+1} PF edge inside", cx + PF_BORE_DIA/2 - 0.5, 34.1, cz,
                   f"solid just inside PF bore edge")
    vc.check_void(f"Bore {i+1} PF edge outside", cx + PF_BORE_DIA/2 + 0.5, 34.1, cz,
                  f"void just outside PF bore edge")

    # User-side counterbore center (Y=41.2, mid of 40.2..42.2)
    vc.check_solid(f"Bore {i+1} user CB center", cx, 41.2, cz,
                   f"solid at user counterbore center")

    # --- Rear wall tube bore checks ---
    # Center of tube bore (Y=5.25, mid of 2..8.5)
    vc.check_solid(f"Bore {i+1} tube bore center", cx, 5.25, cz,
                   f"solid at tube bore center")
    # Verify tube bore radius: solid at r=3.5 (inside 4.0), void at r=4.5 (outside 4.0)
    vc.check_solid(f"Bore {i+1} tube bore edge inside", cx + TUBE_BORE_DIA/2 - 0.5, 5.25, cz,
                   f"solid just inside tube bore edge")
    vc.check_void(f"Bore {i+1} tube bore edge outside", cx + TUBE_BORE_DIA/2 + 0.5, 5.25, cz,
                  f"void just outside tube bore edge")

    # --- Entry funnel checks ---
    # Funnel at Y=0 (mouth): solid at r=5.5 (inside 6.0), void at r=6.5 (outside 6.0)
    vc.check_solid(f"Bore {i+1} funnel mouth inside", cx + FUNNEL_LARGE_DIA/2 - 0.5, 0.3, cz,
                   f"solid just inside funnel mouth")
    vc.check_void(f"Bore {i+1} funnel mouth outside", cx + FUNNEL_LARGE_DIA/2 + 0.5, 0.3, cz,
                  f"void just outside funnel mouth")
    # Funnel at Y=1.0 (mid): should be solid at center
    vc.check_solid(f"Bore {i+1} funnel mid center", cx, 1.0, cz,
                   f"solid at funnel midpoint center")

    # --- Continuity: bore axis should be solid all the way from Y=0.5 to Y=41.2 ---
    vc.check_solid(f"Bore {i+1} axis at Y=0.5", cx, 0.5, cz,
                   f"solid on bore axis at funnel (Y=0.5)")
    vc.check_solid(f"Bore {i+1} axis at Y=5.0", cx, 5.0, cz,
                   f"solid on bore axis at tube bore (Y=5.0)")
    vc.check_solid(f"Bore {i+1} axis at Y=27.0", cx, 27.0, cz,
                   f"solid on bore axis at dock CB (Y=27.0)")
    vc.check_solid(f"Bore {i+1} axis at Y=34.0", cx, 34.0, cz,
                   f"solid on bore axis at PF bore (Y=34.0)")
    vc.check_solid(f"Bore {i+1} axis at Y=41.0", cx, 41.0, cz,
                   f"solid on bore axis at user CB (Y=41.0)")

# Bounding box for cuts
bb_c = cuts.val().BoundingBox()
# Widest cut feature is the counterbore at 15.5mm dia = 7.75mm radius
vc.check_bbox("X", bb_c.xmin, bb_c.xmax, 70.0 - CB_DOCK_DIA/2, 90.0 + CB_DOCK_DIA/2)
vc.check_bbox("Y", bb_c.ymin, bb_c.ymax, 0.0, 42.2)
vc.check_bbox("Z", bb_c.zmin, bb_c.zmax, 26.0 - CB_DOCK_DIA/2, 46.0 + CB_DOCK_DIA/2)

# Solid validity
vc.check_valid()
# Note: bore cuts are 4 independent bore positions with 4.5mm gaps between them.
# Multiple bodies is correct geometry for a cut tool — each bore is a separate
# through-bore at a distinct (X,Z) position. Check for exactly 4 bodies.
n_cut_bodies = len(cuts.solids().vals())
vc._record("Cut body count", n_cut_bodies == 4,
           f"{n_cut_bodies} bodies (expected 4, one per bore position)")
# Volume estimate: 4 stepped bores + 4 tube bores + 4 funnels
# Stepped bore approx: pi*(7.75^2*2 + 4.75^2*12.2 + 7.75^2*2) = pi*(120.1 + 275.1 + 120.1) = 1618 mm³ each
# Tube bore: pi*4^2*6.5 = 326.7 mm³ each
# Funnel: approx cone frustum pi*2/3*(6^2+6*4+4^2) = pi*2/3*76 ≈ 159 mm³ each
# Total per bore ≈ 2104, x4 = 8416
# Envelope: (90+6)-(70-6) x 42.2 x (46+6)-(26-6) = 32 x 42.2 x 32 = 43213
vc.check_volume(expected_envelope=32 * 42.2 * 32, fill_range=(0.05, 0.5))

if not vc.summary():
    print("\nBORE CUTS VALIDATION FAILED")
    sys.exit(1)

print("\nAll validations passed. STEP files exported successfully.")
