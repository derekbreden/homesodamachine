#!/usr/bin/env python3
"""
Generate the finger plate STEP file for the pump cartridge.

Source: hardware/printed-parts/pump-cartridge/planning/finger-plate-parts.md
        hardware/printed-parts/pump-cartridge/planning/finger-plate-spatial.md
"""

# Coordinate system:
#   Origin: front-left-bottom corner of the visible plate body
#   X: plate width, left to right (visible body 0..120.0, tabs extend to -3.5 and 123.5)
#   Y: depth, front face (user-facing) to rear face (0..4.0 visible body, tabs to 5.0)
#   Z: height, bottom of visible body to top (0..24.5 visible body, tabs down to -8.25)
#   Envelope: X [-3.5, 123.5]  Y [0, 5.0]  Z [-8.25, 24.5]
#   Front face at Y=0 (user-facing, build-plate face)
#   Rear face at Y=4.0 (visible body), Y=5.0 (tabs)
#   Build-plate face (print orientation): front face (Y=0) down

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

| # | Feature Name             | Mechanical Function                                     | Op     | Shape    | Axis | Center (X,Y,Z)        | Dimensions                          | Notes                                  |
|---|--------------------------|--------------------------------------------------------|--------|----------|------|------------------------|--------------------------------------|----------------------------------------|
| 1 | Visible plate body       | User-contact surface, distributes finger force 120mm   | Add    | Box      | --   | (60.0, 2.0, 12.25)    | 120.0 x 4.0 x 24.5 mm               | centered=False from origin             |
| 2 | Left downward tab        | Structural bridge to left linkage arm pin              | Add    | Box      | Z    | (-0.5, 2.5, -4.125)   | 6.0 x 5.0 x 8.25 mm                 | X=-3.5..2.5, Y=0..5.0, Z=-8.25..0     |
| 3 | Right downward tab       | Structural bridge to right linkage arm pin             | Add    | Box      | Z    | (120.5, 2.5, -4.125)  | 6.0 x 5.0 x 8.25 mm                 | X=117.5..123.5, Y=0..5.0, Z=-8.25..0  |
| 4 | Tab-to-body fillets      | Stress relief at junction Z=0, rear face transition    | Add    | Fillet   | X    | Z=0, Y=4.0..5.0       | 1.0 mm radius                        | Both tabs, rear face junction           |
| 5 | Left pin socket          | Accepts 3.0mm linkage arm pin (press-fit + CA glue)    | Remove | Cylinder | Z    | (-0.5, 2.5, -8.25)    | 3.1 mm dia x 5.0 mm deep blind      | Opens at Z=-8.25, ends at Z=-3.25      |
| 6 | Right pin socket         | Accepts 3.0mm linkage arm pin (press-fit + CA glue)    | Remove | Cylinder | Z    | (120.5, 2.5, -8.25)   | 3.1 mm dia x 5.0 mm deep blind      | Opens at Z=-8.25, ends at Z=-3.25      |
| 7 | Elephant's foot chamfer  | Prevents flaring on build-plate face from affecting fit | Remove | Chamfer  | Y    | Perimeter of Y=0 face  | 0.3 mm x 45 deg                     | Visible body perimeter only             |
""")

# =====================================================================
# Dimensions from parts.md
# =====================================================================

# Visible plate body
BODY_W = 120.0    # X
BODY_D = 4.0      # Y
BODY_H = 24.5     # Z

# Downward tabs
TAB_W = 6.0       # X extent of each tab
TAB_D = 5.0       # Y extent (1.0mm thicker than body rear face)
TAB_L = 8.25      # Z length (extends downward from Z=0 to Z=-8.25)

# Tab X positions (plate local)
LEFT_TAB_X_MIN  = -3.5
LEFT_TAB_X_MAX  =  2.5
RIGHT_TAB_X_MIN = 117.5
RIGHT_TAB_X_MAX = 123.5

# Pin sockets
PIN_DIA   = 3.1   # 3.0mm pin + 0.1mm press-fit clearance
PIN_DEPTH = 5.0   # from Z=-8.25 upward to Z=-3.25

# Pin socket centers (plate local, at socket opening face)
LEFT_PIN_CX  = -0.5    # X center of left tab
LEFT_PIN_CY  =  2.5    # Y center of left tab
RIGHT_PIN_CX = 120.5   # X center of right tab
RIGHT_PIN_CY =  2.5    # Y center of right tab
PIN_OPEN_Z   = -8.25   # Z of socket opening (bottom of tab)

# Fillets at tab-to-body junction
FILLET_R = 1.0

# Elephant's foot chamfer
EF_CHAMFER = 0.3

# =====================================================================
# Modeling
# =====================================================================

# --- Feature 1: Visible plate body ---
# Box from (0, 0, 0) to (120.0, 4.0, 24.5)
plate = cq.Workplane("XY").box(BODY_W, BODY_D, BODY_H, centered=False)

# --- Feature 2: Left downward tab ---
# Box from (-3.5, 0, -8.25) to (2.5, 5.0, 0)
left_tab = (
    cq.Workplane("XY")
    .transformed(offset=(LEFT_TAB_X_MIN, 0, -TAB_L))
    .box(TAB_W, TAB_D, TAB_L, centered=False)
)
plate = plate.union(left_tab)

# --- Feature 3: Right downward tab ---
# Box from (117.5, 0, -8.25) to (123.5, 5.0, 0)
right_tab = (
    cq.Workplane("XY")
    .transformed(offset=(RIGHT_TAB_X_MIN, 0, -TAB_L))
    .box(TAB_W, TAB_D, TAB_L, centered=False)
)
plate = plate.union(right_tab)

# --- Feature 4: Tab-to-body fillets ---
# The junction at Z=0 between the tabs (Y=0..5.0) and the visible body (Y=0..4.0)
# creates concave edges where the tab rear face step (Y=4.0..5.0) meets the body
# bottom face (Z=0). The spec calls for 1.0mm fillet at this junction on the rear
# face. The concave edges are at Z=0, Y=4.0, running along X within each tab width,
# plus the short vertical edge at Y=4.0..5.0, Z=0 at the inner tab face.
#
# Approach: use OCC fillet builder directly to select concave edges at the junction.
# Filter edges by midpoint proximity to the junction coordinates.

from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.BRep import BRep_Tool
from OCP.TopAbs import TopAbs_REVERSED

def get_edge_midpoint(edge):
    """Get the midpoint of an edge."""
    curve_data = BRep_Tool.Curve_s(edge)
    curve, first, last = curve_data
    mid_param = (first + last) / 2.0
    pt = curve.Value(mid_param)
    return (pt.X(), pt.Y(), pt.Z())

def fillet_junction(solid, tab_x_min, tab_x_max):
    """Apply 1.0mm fillet to the concave edges at one tab-to-body junction."""
    occ_solid = solid.val().wrapped

    fillet_builder = BRepFilletAPI_MakeFillet(occ_solid)
    edge_count = 0

    explorer = TopExp_Explorer(occ_solid, TopAbs_EDGE)
    while explorer.More():
        edge = explorer.Current()
        try:
            mx, my, mz = get_edge_midpoint(edge)
        except Exception:
            explorer.Next()
            continue

        # Target: edges at the junction zone Z~0, Y~4.0..5.0, within tab X range
        # The concave edges are:
        #   1. Horizontal edge along X at Y=4.0, Z=0 (the step edge)
        #   2. Vertical edge along Z at Y=4.0..5.0, Z~0 at the inner tab X face
        #      (at X=2.5 for left tab, X=117.5 for right tab)
        in_tab_x = tab_x_min - 0.1 < mx < tab_x_max + 0.1
        at_junction_z = -0.5 < mz < 0.5
        at_junction_y = 3.5 < my < 5.1

        if in_tab_x and at_junction_z and at_junction_y:
            from OCP.TopoDS import topods
            fillet_builder.Add(FILLET_R, topods.Edge_s(edge))
            edge_count += 1

        explorer.Next()

    if edge_count > 0:
        fillet_builder.Build()
        from cadquery.occ_impl.shapes import Solid
        result_solid = Solid(fillet_builder.Shape())
        return cq.Workplane("XY").newObject([result_solid])
    return solid

plate = fillet_junction(plate, LEFT_TAB_X_MIN, LEFT_TAB_X_MAX)
plate = fillet_junction(plate, RIGHT_TAB_X_MIN, RIGHT_TAB_X_MAX)

# --- Feature 5: Left pin socket ---
# 3.1mm diameter x 5.0mm deep blind bore, Z-axis
# Center at (-0.5, 2.5), opens at Z=-8.25, blind end at Z=-3.25
left_socket = (
    cq.Workplane("XY")
    .transformed(offset=(LEFT_PIN_CX, LEFT_PIN_CY, PIN_OPEN_Z))
    .circle(PIN_DIA / 2)
    .extrude(PIN_DEPTH)  # extrudes in +Z direction (from -8.25 to -3.25)
)
plate = plate.cut(left_socket)

# --- Feature 6: Right pin socket ---
# Center at (120.5, 2.5), opens at Z=-8.25, blind end at Z=-3.25
right_socket = (
    cq.Workplane("XY")
    .transformed(offset=(RIGHT_PIN_CX, RIGHT_PIN_CY, PIN_OPEN_Z))
    .circle(PIN_DIA / 2)
    .extrude(PIN_DEPTH)  # extrudes in +Z direction
)
plate = plate.cut(right_socket)

# --- Feature 7: Elephant's foot chamfer ---
# 0.3mm x 45 deg chamfer on all perimeter edges of the front face (Y=0)
# of the visible plate body only.
# The front face edges are at Y=0. Select edges on the Y=0 face of the
# visible body (not the tabs, which are at the top of the print).
# Edges at Y=0: top edge (Z=24.5), bottom edge (Z=0), left edge (X=0), right edge (X=120.0)
# The tabs also have edges at Y=0 but the spec says visible body perimeter only.

# Select all edges that lie on the Y=0 plane and are within the visible body Z range (0..24.5)
# and X range (0..120.0).
plate = (
    plate
    .edges(
        cq.selectors.BoxSelector(
            (-0.1, -0.1, -0.1),
            (BODY_W + 0.1, 0.1, BODY_H + 0.1)
        )
    )
    .chamfer(EF_CHAMFER)
)

# =====================================================================
# Export STEP
# =====================================================================

step_path = str(Path(__file__).parent / "finger-plate.step")
cq.exporters.export(plate, step_path)
print(f"\nSTEP exported to: {step_path}")

# =====================================================================
# RUBRIC 3 -- Feature-Specification Reconciliation
# =====================================================================

print("\n=== RUBRIC 3: Feature-Specification Reconciliation ===\n")

v = Validator(plate)

# Feature 1: Visible plate body
# Probe interior of body at several locations
v.check_solid("Body center",        60.0, 2.0, 12.25, "solid at body center")
v.check_solid("Body front-left",     1.0, 0.5, 1.0,   "solid near front-left corner")
v.check_solid("Body front-right",  119.0, 0.5, 23.0,  "solid near front-right-top")
v.check_solid("Body rear mid",      60.0, 3.5, 12.0,  "solid near rear face mid")
# Outside body in Y
v.check_void("Above body Y",        60.0, 4.5, 12.0,  "void above body rear face (Y=4.0) at mid-height")
# Outside body in Z (above)
v.check_void("Above body Z",        60.0, 2.0, 25.0,  "void above body top (Z=24.5)")

# Feature 2: Left downward tab
v.check_solid("Left tab center",    -0.5, 0.5, -4.125, "solid at left tab center (offset from socket in Y)")
v.check_solid("Left tab top",       -0.5, 2.5,  -1.0,  "solid near top of left tab")
v.check_solid("Left tab bottom",    -0.5, 0.5,  -7.5,  "solid near bottom of left tab (offset from socket)")
v.check_solid("Left tab rear",      -0.5, 4.5,  -4.0,  "solid at left tab rear (Y=4.5, within 5.0)")
# Outside left tab in X
v.check_void("Left of left tab",    -4.0, 2.5,  -4.0,  "void left of left tab (X=-4.0)")
# Outside left tab in Z
v.check_void("Below left tab",      -0.5, 2.5,  -9.0,  "void below left tab (Z=-9.0)")

# Feature 3: Right downward tab
v.check_solid("Right tab center",  120.5, 0.5, -4.125, "solid at right tab center (offset from socket in Y)")
v.check_solid("Right tab top",     120.5, 2.5,  -1.0,  "solid near top of right tab")
v.check_solid("Right tab bottom",  120.5, 0.5,  -7.5,  "solid near bottom of right tab (offset from socket)")
v.check_solid("Right tab rear",    120.5, 4.5,  -4.0,  "solid at right tab rear (Y=4.5)")
# Outside right tab in X
v.check_void("Right of right tab", 124.0, 2.5,  -4.0,  "void right of right tab (X=124.0)")
# Outside right tab in Z
v.check_void("Below right tab",    120.5, 2.5,  -9.0,  "void below right tab (Z=-9.0)")

# Feature 4: Tab-to-body fillets (probe the fillet region)
# The fillet rounds the concave edge at Z=0, Y=4.0. After filleting,
# a point slightly inside the concave corner should be solid (fillet material).
# Before filleting, the point at Y=4.3, Z=-0.3 (inside the 1mm step) would be void.
# With a 1mm fillet, it should now be solid.
v.check_solid("Left fillet region",   0.0, 4.3, -0.3,  "solid in left fillet region (was concave corner)")
v.check_solid("Right fillet region", 120.0, 4.3, -0.3, "solid in right fillet region (was concave corner)")

# Feature 5: Left pin socket
# Void at socket center, solid at socket wall
v.check_void("Left socket center",      LEFT_PIN_CX, LEFT_PIN_CY, -6.0,
             "void at left pin socket mid-depth")
v.check_void("Left socket opening",     LEFT_PIN_CX, LEFT_PIN_CY, -8.1,
             "void near left socket opening (Z=-8.1)")
v.check_solid("Left socket blind end",  LEFT_PIN_CX, LEFT_PIN_CY, -2.5,
              "solid above left socket blind end (Z=-2.5)")
# Solid outside socket radius
v.check_solid("Left socket wall +X",    LEFT_PIN_CX + 2.0, LEFT_PIN_CY, -6.0,
              "solid outside left socket in +X")

# Feature 6: Right pin socket
v.check_void("Right socket center",     RIGHT_PIN_CX, RIGHT_PIN_CY, -6.0,
             "void at right pin socket mid-depth")
v.check_void("Right socket opening",    RIGHT_PIN_CX, RIGHT_PIN_CY, -8.1,
             "void near right socket opening (Z=-8.1)")
v.check_solid("Right socket blind end", RIGHT_PIN_CX, RIGHT_PIN_CY, -2.5,
              "solid above right socket blind end (Z=-2.5)")
v.check_solid("Right socket wall +X",   RIGHT_PIN_CX + 2.0, RIGHT_PIN_CY, -6.0,
              "solid outside right socket in +X")

# Feature 7: Elephant's foot chamfer
# The chamfer removes material at Y=0 corners. Probe just inside the
# chamfer zone: at (0.1, 0.1, 0.1) should be void or near-surface
# due to 0.3mm chamfer. A point at (0.5, 0.5, 0.5) should be solid.
v.check_solid("Inside chamfer zone", 0.5, 0.5, 0.5, "solid just inside chamfer region")
# The very corner at (0, 0, 0) is clipped by the chamfer -- should be void
v.check_void("Chamfer corner origin", -0.05, -0.05, 12.0,
             "void at chamfered front-left edge")
# Top-front edge chamfer check
v.check_void("Chamfer top-front corner", 60.0, -0.05, 24.55,
             "void at chamfered front-top edge")

# =====================================================================
# RUBRIC 4 -- Solid Validity
# =====================================================================

print("\n=== RUBRIC 4: Solid Validity ===\n")

v.check_valid()
v.check_single_body()

# Envelope volume: 127.0 x 5.0 x 32.75 = 20796.25 mm^3
# Actual volume:
# Body: 120.0 * 4.0 * 24.5 = 11760
# Tabs: 2 * 6.0 * 5.0 * 8.25 = 495
# Total additive ~12255, minus sockets, plus fillets ~ 12200
# Fill range relative to envelope: ~12200/20796 ~ 0.59
v.check_volume(expected_envelope=127.0 * 5.0 * 32.75, fill_range=(0.3, 0.8))

# =====================================================================
# RUBRIC 5 -- Bounding Box
# =====================================================================

print("\n=== RUBRIC 5: Bounding Box ===\n")

bb = plate.val().BoundingBox()
print(f"  Actual BB: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
      f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
      f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")

v.check_bbox("X", bb.xmin, bb.xmax, -3.5, 123.5)
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, 5.0)
v.check_bbox("Z", bb.zmin, bb.zmax, -8.25, 24.5)

# =====================================================================
# Summary
# =====================================================================

if not v.summary():
    sys.exit(1)
