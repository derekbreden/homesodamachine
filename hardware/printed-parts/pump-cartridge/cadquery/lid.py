"""
Lid — CadQuery Generation Script

A flat 160 x 155 x 4 mm PETG panel that snaps onto the tray top edges.
Features: 8 slot-released snap tabs, 3 stiffening ribs, 1 bezel pocket (T1),
top-face chamfers, and a directional arrow emboss.

Coordinate system:
  Origin: rear-left-bottom corner of lid
  X: width, 0..160 mm (left to right)
  Y: depth, 0..155 mm (rear to front)
  Z: thickness, 0..4 mm (bottom to top). Z=0 = bottom face (contacts tray).
  Envelope: 160 x 155 x 4 mm main body; tabs extend to Z=-4.5; ribs to Z=-3

Feature Planning Table:
| #  | Feature Name          | Function                    | Op     | Shape   | Axis | Center (X,Y,Z)           | Dimensions                          | Notes                          |
|----|-----------------------|-----------------------------|--------|---------|------|--------------------------|-------------------------------------|--------------------------------|
| 1  | Panel body            | Structural flat panel       | Add    | Box     | --   | (80, 77.5, 2)            | 160x155x4                           | Base solid                     |
| 2  | LT1 relief slot       | Creates cantilever flex     | Remove | Box     | Z    | (5.5, 20, 1.75)          | 1x6x3.5 (X,Y,Z)                    | X=5..6, Y=17..23, Z=0..3.5    |
| 3  | LT1 beam              | Cantilever flexure          | Add    | Box     | Z    | (6.5, 20, -1.25)         | 1x6x2.5 (X,Y,Z)                    | X=6..7, Y=17..23, Z=-2.5..0   |
| 4  | LT1 hook              | Retention behind ridge      | Add    | Box     | Z    | (6.5, 20, -3.5)          | 1x6x2 (X,Y,Z)                      | X=6..7, Y=17..23, Z=-4.5..-2.5|
| 5  | LT2 relief slot       | Creates cantilever flex     | Remove | Box     | Z    | (5.5, 60, 1.75)          | 1x6x3.5                            | Same pattern as LT1            |
| 6  | LT2 beam              | Cantilever flexure          | Add    | Box     | Z    | (6.5, 60, -1.25)         | 1x6x2.5                            |                                |
| 7  | LT2 hook              | Retention behind ridge      | Add    | Box     | Z    | (6.5, 60, -3.5)          | 1x6x2                              |                                |
| 8  | LT3 relief slot       | Creates cantilever flex     | Remove | Box     | Z    | (5.5, 100, 1.75)         | 1x6x3.5                            |                                |
| 9  | LT3 beam              | Cantilever flexure          | Add    | Box     | Z    | (6.5, 100, -1.25)        | 1x6x2.5                            |                                |
| 10 | LT3 hook              | Retention behind ridge      | Add    | Box     | Z    | (6.5, 100, -3.5)         | 1x6x2                              |                                |
| 11 | LT4 relief slot       | Creates cantilever flex     | Remove | Box     | Z    | (5.5, 140, 1.75)         | 1x6x3.5                            |                                |
| 12 | LT4 beam              | Cantilever flexure          | Add    | Box     | Z    | (6.5, 140, -1.25)        | 1x6x2.5                            |                                |
| 13 | LT4 hook              | Retention behind ridge      | Add    | Box     | Z    | (6.5, 140, -3.5)         | 1x6x2                              |                                |
| 14 | RT1 relief slot       | Creates cantilever flex     | Remove | Box     | Z    | (154.5, 20, 1.75)        | 1x6x3.5                            | X=154..155, Y=17..23, Z=0..3.5|
| 15 | RT1 beam              | Cantilever flexure          | Add    | Box     | Z    | (153.5, 20, -1.25)       | 1x6x2.5                            | X=153..154, Y=17..23, Z=-2.5..0|
| 16 | RT1 hook              | Retention behind ridge      | Add    | Box     | Z    | (153.5, 20, -3.5)        | 1x6x2                              | X=153..154, Y=17..23, Z=-4.5..-2.5|
| 17-24 | RT2-RT4 slot/beam/hook | Same pattern as RT1       |        |         |      | Y=60,100,140             |                                     |                                |
| 25 | Bezel pocket T1       | Receives bezel top tab      | Remove | Box     | Z    | (80, 153.5, 1.25)        | 5x3x2.5 (X,Y,Z)                    | X=77.5..82.5, Y=152..155, Z=0..2.5|
| 26 | Rib 1                 | Stiffens panel              | Add    | Box     | X    | (80, 40, -1.5)           | 150x2x3 (X,Y,Z)                    | X=5..155, Y=39..41, Z=-3..0   |
| 27 | Rib 2                 | Stiffens panel              | Add    | Box     | X    | (80, 80, -1.5)           | 150x2x3                            | X=5..155, Y=79..81, Z=-3..0   |
| 28 | Rib 3                 | Stiffens panel              | Add    | Box     | X    | (80, 120, -1.5)          | 150x2x3                            | X=5..155, Y=119..121, Z=-3..0 |
| 29 | Top edge chamfers     | Removes sharp edges         | Remove | Chamfer | --   | Perimeter at Z=4         | 0.5 mm chamfer                      | All 4 top-face perimeter edges |
| 30 | Orientation arrow     | Indicates front direction   | Remove | Emboss  | Z    | (80, 147.5, 3.85)        | ~10x5, 0.3mm deep                   | Arrow pointing +Y on top face  |
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq
from step_validate import Validator

# ── Parameters ──────────────────────────────────────────────────────

# Panel body
W = 160.0       # X extent
D = 155.0       # Y extent
T = 4.0         # Z extent (thickness)

# Snap tab parameters
TAB_Y_CENTERS = [20.0, 60.0, 100.0, 140.0]
TAB_Y_WIDTH = 6.0           # Y extent of each tab
BEAM_THICKNESS = 1.0        # X thickness of cantilever beam
BEAM_LENGTH_BELOW = 2.5     # Z extent below lid (Z=0 to Z=-2.5)
HOOK_HEIGHT = 2.0           # Z extent of hook (Z=-2.5 to Z=-4.5)
HOOK_WIDTH = 1.0            # X width of hook (same as beam)
RELIEF_SLOT_WIDTH = 1.0     # X width of relief slot
RELIEF_SLOT_DEPTH = 3.5     # Z depth of relief slot into lid body (Z=0 to Z=3.5)

# Left tab X positions
L_WALL_X = 5.0              # Left wall interior face
L_SLOT_X0 = 5.0             # Relief slot X start
L_SLOT_X1 = 6.0             # Relief slot X end
L_BEAM_X0 = 6.0             # Beam/hook X start
L_BEAM_X1 = 7.0             # Beam/hook X end

# Right tab X positions (mirrored)
R_WALL_X = 155.0            # Right wall interior face
R_SLOT_X0 = 154.0           # Relief slot X start
R_SLOT_X1 = 155.0           # Relief slot X end
R_BEAM_X0 = 153.0           # Beam/hook X start
R_BEAM_X1 = 154.0           # Beam/hook X end

# Bezel pocket T1
POCKET_X0 = 77.5
POCKET_X1 = 82.5
POCKET_Y0 = 152.0
POCKET_Y1 = 155.0
POCKET_Z_HEIGHT = 2.5       # Z=0 to Z=2.5

# Stiffening ribs
RIB_Y_CENTERS = [40.0, 80.0, 120.0]
RIB_THICKNESS = 2.0         # Y thickness
RIB_HEIGHT = 3.0            # Z extent below lid (Z=0 to Z=-3)
RIB_X0 = 5.0
RIB_X1 = 155.0

# Edge treatment
CHAMFER = 0.5               # Top edge chamfer

# Arrow emboss
ARROW_DEPTH = 0.3           # Depth of engraving from Z=4 face

# ── Build Model ─────────────────────────────────────────────────────

# 1. Panel body: 160 x 155 x 4
lid = cq.Workplane("XY").box(W, D, T, centered=False)

# 2. Add snap tab beams and hooks (8 tabs total)
# Each tab: beam from Z=-2.5 to Z=0, hook from Z=-4.5 to Z=-2.5
# The beam also extends through the lid body from Z=0 to Z=3.5 (inside the lid,
# adjacent to the relief slot). This portion is already part of the panel body,
# so we only need to add the below-lid portions.

for y_c in TAB_Y_CENTERS:
    y0 = y_c - TAB_Y_WIDTH / 2.0  # Tab Y start
    y1 = y_c + TAB_Y_WIDTH / 2.0  # Tab Y end

    # Left tabs: beam at X=6..7, hook at X=6..7
    # Beam: Z=-2.5 to 0
    left_beam = (
        cq.Workplane("XY")
        .transformed(offset=(L_BEAM_X0, y0, -BEAM_LENGTH_BELOW))
        .box(BEAM_THICKNESS, TAB_Y_WIDTH, BEAM_LENGTH_BELOW, centered=False)
    )
    lid = lid.union(left_beam)

    # Hook: Z=-4.5 to -2.5
    left_hook = (
        cq.Workplane("XY")
        .transformed(offset=(L_BEAM_X0, y0, -(BEAM_LENGTH_BELOW + HOOK_HEIGHT)))
        .box(HOOK_WIDTH, TAB_Y_WIDTH, HOOK_HEIGHT, centered=False)
    )
    lid = lid.union(left_hook)

    # Right tabs: beam at X=153..154, hook at X=153..154
    right_beam = (
        cq.Workplane("XY")
        .transformed(offset=(R_BEAM_X0, y0, -BEAM_LENGTH_BELOW))
        .box(BEAM_THICKNESS, TAB_Y_WIDTH, BEAM_LENGTH_BELOW, centered=False)
    )
    lid = lid.union(right_beam)

    right_hook = (
        cq.Workplane("XY")
        .transformed(offset=(R_BEAM_X0, y0, -(BEAM_LENGTH_BELOW + HOOK_HEIGHT)))
        .box(HOOK_WIDTH, TAB_Y_WIDTH, HOOK_HEIGHT, centered=False)
    )
    lid = lid.union(right_hook)

# 3. Cut relief slots (8 slots, one per tab)
# Each slot: cut into lid body from Z=0 upward to Z=3.5
for y_c in TAB_Y_CENTERS:
    y0 = y_c - TAB_Y_WIDTH / 2.0
    y1 = y_c + TAB_Y_WIDTH / 2.0

    # Left relief slot: X=5..6, Y=tab extent, Z=0..3.5
    left_slot = (
        cq.Workplane("XY")
        .transformed(offset=(L_SLOT_X0, y0, 0))
        .box(RELIEF_SLOT_WIDTH, TAB_Y_WIDTH, RELIEF_SLOT_DEPTH, centered=False)
    )
    lid = lid.cut(left_slot)

    # Right relief slot: X=154..155, Y=tab extent, Z=0..3.5
    right_slot = (
        cq.Workplane("XY")
        .transformed(offset=(R_SLOT_X0, y0, 0))
        .box(RELIEF_SLOT_WIDTH, TAB_Y_WIDTH, RELIEF_SLOT_DEPTH, centered=False)
    )
    lid = lid.cut(right_slot)

# 4. Cut bezel pocket T1
# X=77.5..82.5, Y=152..155, Z=0..2.5 (cut from bottom face upward)
pocket = (
    cq.Workplane("XY")
    .transformed(offset=(POCKET_X0, POCKET_Y0, 0))
    .box(POCKET_X1 - POCKET_X0, POCKET_Y1 - POCKET_Y0, POCKET_Z_HEIGHT, centered=False)
)
lid = lid.cut(pocket)

# 5. Add stiffening ribs (3 ribs on underside)
# Each rib: X=5..155, 2mm thick (Y), 3mm tall (Z), hanging below lid
for y_c in RIB_Y_CENTERS:
    y0 = y_c - RIB_THICKNESS / 2.0
    rib = (
        cq.Workplane("XY")
        .transformed(offset=(RIB_X0, y0, -RIB_HEIGHT))
        .box(RIB_X1 - RIB_X0, RIB_THICKNESS, RIB_HEIGHT, centered=False)
    )
    lid = lid.union(rib)

# 6. Top edge chamfers (0.5 mm on all 4 perimeter edges at Z=4)
# Select edges on the top face (Z=4) that are on the perimeter
lid = (
    lid
    .edges("|X").edges(">Z")
    .chamfer(CHAMFER)
)
lid = (
    lid
    .edges("|Y").edges(">Z")
    .chamfer(CHAMFER)
)

# 7. Orientation arrow emboss on top face
# Arrow pointing toward +Y (front), centered at X=80, Y~147.5
# Simple arrow shape: triangle head + rectangular shaft
# Shaft: X=79..81, Y=143..148, 0.3mm deep from Z=4
# Head: triangle at Y=148..152, X=77..83, pointing +Y
arrow_shaft = (
    cq.Workplane("XY")
    .transformed(offset=(79.0, 143.0, T - ARROW_DEPTH))
    .box(2.0, 5.0, ARROW_DEPTH, centered=False)
)
lid = lid.cut(arrow_shaft)

# Arrow head as a triangular prism
# Triangle vertices (XY at Z=T-0.3): (77, 148), (83, 148), (80, 152)
arrow_head = (
    cq.Workplane("XY")
    .transformed(offset=(0, 0, T - ARROW_DEPTH))
    .moveTo(77, 148)
    .lineTo(83, 148)
    .lineTo(80, 152)
    .close()
    .extrude(ARROW_DEPTH)
)
lid = lid.cut(arrow_head)

# ── Export STEP ──────────────────────────────────────────────────────

step_path = str(Path(__file__).parent / "lid.step")
cq.exporters.export(lid, step_path)
print(f"Exported: {step_path}")

# ── Validation ──────────────────────────────────────────────────────

print("\n=== Validation ===\n")

v = Validator(lid)

# --- Panel body ---
v.check_solid("Panel body center", 80.0, 77.5, 2.0, "solid at panel center")
v.check_solid("Panel body corner", 1.0, 1.0, 2.0, "solid at rear-left corner")
v.check_solid("Panel body front-right", 159.0, 154.0, 2.0, "solid at front-right corner")

# --- Relief slots (should be void inside lid body) ---
for i, y_c in enumerate(TAB_Y_CENTERS):
    tag = f"L{i+1}"
    # Left relief slot center: X=5.5, Y=y_c, Z=1.75 (midpoint of 0..3.5)
    v.check_void(f"Left relief slot {tag} center", 5.5, y_c, 1.75,
                 f"void at left relief slot {tag}")
    # Right relief slot center: X=154.5, Y=y_c, Z=1.75
    v.check_void(f"Right relief slot {tag} center", 154.5, y_c, 1.75,
                 f"void at right relief slot {tag}")

# --- Tab beams (should be solid below lid) ---
for i, y_c in enumerate(TAB_Y_CENTERS):
    tag = f"T{i+1}"
    # Left beam center: X=6.5, Y=y_c, Z=-1.25
    v.check_solid(f"Left beam {tag} center", 6.5, y_c, -1.25,
                  f"solid at left beam {tag}")
    # Right beam center: X=153.5, Y=y_c, Z=-1.25
    v.check_solid(f"Right beam {tag} center", 153.5, y_c, -1.25,
                  f"solid at right beam {tag}")

# --- Tab hooks (should be solid) ---
for i, y_c in enumerate(TAB_Y_CENTERS):
    tag = f"T{i+1}"
    # Left hook center: X=6.5, Y=y_c, Z=-3.5
    v.check_solid(f"Left hook {tag} center", 6.5, y_c, -3.5,
                  f"solid at left hook {tag}")
    # Right hook center: X=153.5, Y=y_c, Z=-3.5
    v.check_solid(f"Right hook {tag} center", 153.5, y_c, -3.5,
                  f"solid at right hook {tag}")

# --- Void below hooks (no material below Z=-4.5) ---
v.check_void("Below left hook", 6.5, 20.0, -4.8, "void below hooks")
v.check_void("Below right hook", 153.5, 20.0, -4.8, "void below hooks")

# --- Bezel pocket T1 (should be void) ---
v.check_void("Bezel pocket T1 center", 80.0, 153.5, 1.25,
             "void at bezel pocket center")
# Solid above pocket (remaining lid thickness Z=2.5..4)
v.check_solid("Lid above bezel pocket", 80.0, 153.5, 3.5,
              "solid above bezel pocket (lid material)")

# --- Stiffening ribs (should be solid) ---
for i, y_c in enumerate(RIB_Y_CENTERS):
    v.check_solid(f"Rib {i+1} center", 80.0, y_c, -1.5,
                  f"solid at rib {i+1} center")
    # Solid near ends of rib
    v.check_solid(f"Rib {i+1} left end", 6.0, y_c, -1.5,
                  f"solid at rib {i+1} left end")
    v.check_solid(f"Rib {i+1} right end", 154.0, y_c, -1.5,
                  f"solid at rib {i+1} right end")

# --- Void between ribs (no material hanging below lid in non-rib/non-tab zones) ---
v.check_void("Void between rib 1 and rib 2", 80.0, 60.0, -1.5,
             "void between ribs at Y=60 (tab beams are at X=6.5/153.5 not X=80)")

# --- Arrow emboss (should be void at top face) ---
v.check_void("Arrow shaft center", 80.0, 145.5, 3.85,
             "void at arrow shaft (0.3mm deep from top)")
v.check_void("Arrow head center", 80.0, 149.0, 3.85,
             "void at arrow head (0.3mm deep from top)")
# Solid just below the emboss
v.check_solid("Solid below arrow", 80.0, 145.5, 3.5,
              "solid below arrow emboss depth")

# --- Chamfer checks ---
# After 0.5mm chamfer, the very corner at (0,0,4) should be void
v.check_void("Top chamfer corner RL", 0.1, 0.1, 3.95,
             "void at chamfered top corner (rear-left)")

# --- Bounding box ---
bb = lid.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, 0.0, 160.0)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, 155.0)
v.check_bbox("Z", bb.zmin, bb.zmax, -4.5, 4.0)

# --- Solid integrity ---
v.check_valid()
v.check_single_body()
v.check_volume(
    expected_envelope=W * D * T,
    fill_range=(0.30, 1.05)  # Panel minus cuts plus ribs and tabs
)

# --- Summary ---
if not v.summary():
    sys.exit(1)
