"""
3D model of the under-counter appliance for the enclosure iso drawings.

The model is a CadQuery solid with the appliance's outer box and the
external features that read on the front, back, and top faces. Internal
geometry (foam shell, pump cases, condenser, etc.) is NOT modeled here —
this is the "skin" of the enclosure plus its external-facing features,
modeled to whatever depth lets it project to a recognizable line drawing.

Coordinate convention (matches the cold-core / pump-case / faucet shell
modules in the repo):
- +X is the appliance's width axis (right).
- +Y is the appliance's depth axis (front to back). y=0 is the FRONT
  face, y=D is the BACK face.
- +Z is the appliance's height axis (up). z=0 is the bottom, z=H is the
  top.
- The box origin is at the front-bottom-left corner.

Drawing-only conventions:
- Cutouts that read as door/lid/panel outlines (top-face doors, back-face
  C14 inlet) are shallow recesses — SURFACE_CUT_DEPTH deep — so they
  show up as nested rectangles in the iso projection (the seam between
  panel and frame).
- Cutouts that are real through-holes (none currently) would cut from
  the outside surface all the way through.
- Protrusions that read as physical objects sticking out (S3 knob,
  dispense tip, push button, nameplate) are added via union as solids
  outside the box.

substitute_py_comments rewrites the [value](NAME) links in this file's
comments on every run via refresh_comments(), which the drawing scripts
call from their main().
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[3]
sys.path.insert(0, str(_REPO_ROOT / "tools"))
sys.path.insert(0, str(_REPO_ROOT / "hardware" / "printed-parts" / "flavor" / "pump-case"))
sys.path.insert(0, str(_HERE.parent))

from docgen import substitute_py_comments
from pump_case import case_outer_x, case_outer_z
from _enclosure_dimensions import APPLIANCE_W, APPLIANCE_D


# ---------------------------------------------------------------------------
# Outer enclosure
# ---------------------------------------------------------------------------

W = APPLIANCE_W
D = APPLIANCE_D
H = 280.0  # working value; not yet derived from internal stack-ups


# ---------------------------------------------------------------------------
# Top-face doors and lids
# ---------------------------------------------------------------------------

PUMP_SIDE_BY_SIDE_CLEARANCE = 15.0
PUMP_CASE_DEPTH_CLEARANCE = 10.0

# [145.5 mm](PUMP_DOOR_W) — single-case depth + clearance, along the appliance width.
pump_door_w = case_outer_z + PUMP_CASE_DEPTH_CLEARANCE

# [165.0 mm](PUMP_DOOR_D) — two cases side-by-side + clearance, along the appliance depth.
pump_door_d = 2 * case_outer_x + PUMP_SIDE_BY_SIDE_CLEARANCE

FRONT_MARGIN = 10.0
SIDE_MARGIN = 10.0
DOOR_GAP = 10.0

# [107.5 mm](HOPPER_DOOR_W) — APPLIANCE_W − 2 × SIDE_MARGIN − pump_door_w − DOOR_GAP.
hopper_door_w = W - 2 * SIDE_MARGIN - pump_door_w - DOOR_GAP

# [165.0 mm](HOPPER_DOOR_D) — matches pump door depth.
hopper_door_d = pump_door_d

pump_door_a = SIDE_MARGIN + pump_door_w / 2
pump_door_b = FRONT_MARGIN + pump_door_d / 2
hopper_door_a = W - SIDE_MARGIN - hopper_door_w / 2
hopper_door_b = FRONT_MARGIN + hopper_door_d / 2

# GFCI access band — 27 × 18 mm exposed band centered on the 42 × 67
# Legrand 1597 body, tucked into the back-right corner with the body's
# tall axis along the appliance width. Body center sits 38.5 mm from the
# right edge (5 mm yoke clearance + 67/2) and 26 mm from the back edge
# (5 + 42/2); the band is centered on the body. On the top face the
# band is 18 along a (width) × 27 along b (depth).
GFCI_W = 18.0
GFCI_H = 27.0
GFCI_A = W - 38.5
GFCI_B = D - 26.0


# ---------------------------------------------------------------------------
# Front-face features (centerline a = hopper_door_a):
#   S3 rotary display at b = 235.
#   Dispense tip at b = 200, axis tilted 40° from straight down to match
#   the mounted faucet (gn_bend1_sweep_rad + gn_bend2_sweep_rad = 140° in
#   touch-flo-shell, so the tip ends at 180° - 140° = 40° from vertical).
#   Push button at b = 170, sized to catch a glass rim raised under the
#   tip; wide enough that a finger can also press it.
# ---------------------------------------------------------------------------

S3_AT = (hopper_door_a, 235.0)
S3_D = 32.0
S3_PROTRUSION = 19.0

TIP_AT = (hopper_door_a, 200.0)
TIP_D = 20.0
TIP_LENGTH = 25.0
TIP_ANGLE_FROM_VERTICAL_DEG = 40.0
_tip_theta = math.radians(TIP_ANGLE_FROM_VERTICAL_DEG)
TIP_AXIS = (0.0, -math.sin(_tip_theta), -math.cos(_tip_theta))

BUTTON_AT = (hopper_door_a, 170.0)
BUTTON_W = 80.0
BUTTON_H = 20.0
BUTTON_PROTRUSION = 10.0


# ---------------------------------------------------------------------------
# Back-face features:
#   Umbilical: three Ø17 mm John Guest PP1208E bulkheads in a tangent
#   equilateral triangle, high on the back panel where the umbilical
#   drops down through the countertop.
#   C14 AC inlet: IEC 60320 panel-mount receptacle cutout ~28 × 20 mm.
#   Nameplate: separately-printed serialized plaque 60 × 40 mm, raised
#   from the back surface.
# ---------------------------------------------------------------------------

UMBILICAL_BULKHEAD_D = 17.0

# Equilateral triangle with side = bulkhead diameter (tangent circles).
_S = UMBILICAL_BULKHEAD_D
TRIANGLE_VERTEX_OFFSET = _S / math.sqrt(3)        # 9.81 mm
TRIANGLE_BASE_HALF_WIDTH = _S / 2                  # 8.5 mm
TRIANGLE_BASE_OFFSET = _S * math.sqrt(3) / 6       # 4.91 mm

UMBILICAL_CLUSTER_A = W / 2
UMBILICAL_CLUSTER_B = H - 50.0

C14_AT = (70.0, H - 50.0)
C14_W = 28.0
C14_H = 20.0

NAMEPLATE_AT = (200.0, 60.0)
NAMEPLATE_W = 60.0
NAMEPLATE_H = 40.0
NAMEPLATE_THICKNESS = 1.5


# ---------------------------------------------------------------------------
# Drawing-only knobs: shallow cut depths so doors / lids / inlets read as
# nested rectangles (panel seam) instead of through-holes.
# ---------------------------------------------------------------------------

SURFACE_CUT_DEPTH = 3.0


# ---------------------------------------------------------------------------
# Geometry builders
# ---------------------------------------------------------------------------

# Per-face plane definitions. Using `.faces(...)` selection on the
# appliance is unreliable here — after one front-face protrusion is
# added, `<Y` selects the protrusion's outer face instead of the
# enclosure's, so subsequent moveTo coords shift to a different plane.
# Constructing each feature on a fresh `cq.Workplane(cq.Plane(...))`
# avoids that and keeps the face-local (a, b) convention stable.

def _front_plane() -> cq.Plane:
    """Front face (y=0). a-axis = +world X, b-axis = +world Z, normal = -Y."""
    return cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, -1, 0))


def _back_plane() -> cq.Plane:
    """Back face (y=D). a-axis = -world X (mirrored as you look at the
    back face from outside), b-axis = +world Z, normal = +Y."""
    return cq.Plane(origin=(W, D, 0), xDir=(-1, 0, 0), normal=(0, 1, 0))


def _top_plane() -> cq.Plane:
    """Top face (z=H). a-axis = +world X, b-axis = +world Y, normal = +Z."""
    return cq.Plane(origin=(0, 0, H), xDir=(1, 0, 0), normal=(0, 0, 1))


def _cut_top_rectangle(solid, a, b, w, h):
    """Cut a shallow rectangle from the top face (z=H) for door/lid outlines."""
    cutter = (
        cq.Workplane(_top_plane())
        .moveTo(a, b)
        .rect(w, h)
        .extrude(-SURFACE_CUT_DEPTH)  # extrude in -normal = -Z = into the box
    )
    return solid.cut(cutter)


def _cut_back_rectangle(solid, a, b, w, h):
    """Cut a shallow rectangle from the back face (y=D)."""
    cutter = (
        cq.Workplane(_back_plane())
        .moveTo(a, b)
        .rect(w, h)
        .extrude(-SURFACE_CUT_DEPTH)
    )
    return solid.cut(cutter)


def _cut_back_circle(solid, a, b, d):
    """Cut a shallow circle from the back face for umbilical bulkhead outlines."""
    cutter = (
        cq.Workplane(_back_plane())
        .moveTo(a, b)
        .circle(d / 2)
        .extrude(-SURFACE_CUT_DEPTH)
    )
    return solid.cut(cutter)


def _add_front_knob(solid, a, b, d, protrusion):
    """Add a perpendicular cylindrical knob protruding from the front face."""
    knob = (
        cq.Workplane(_front_plane())
        .moveTo(a, b)
        .circle(d / 2)
        .extrude(protrusion)
    )
    return solid.union(knob)


def _add_front_angled_knob(solid, a, b, d, length, axis_3d):
    """Add a cylindrical knob with an arbitrary axis from the front face."""
    origin = cq.Vector(a, 0.0, b)
    direction = cq.Vector(*axis_3d)
    cyl = cq.Solid.makeCylinder(d / 2, length, pnt=origin, dir=direction)
    return solid.union(cq.Workplane().add(cyl))


def _add_front_button(solid, a, b, w, h, protrusion):
    """Add a rectangular protrusion from the front face."""
    button = (
        cq.Workplane(_front_plane())
        .moveTo(a, b)
        .rect(w, h)
        .extrude(protrusion)
    )
    return solid.union(button)


def _add_back_nameplate(solid, a, b, w, h, thickness):
    """Add a raised rectangular plaque to the back face (y=D)."""
    plate = (
        cq.Workplane(_back_plane())
        .moveTo(a, b)
        .rect(w, h)
        .extrude(thickness)
    )
    return solid.union(plate)


def build_appliance() -> cq.Workplane:
    """Build the full appliance model as a CadQuery Workplane."""
    appliance = cq.Workplane("XY").box(W, D, H, centered=False)

    # Top face: GFCI band + pump door + hopper lid
    appliance = _cut_top_rectangle(appliance, GFCI_A, GFCI_B, GFCI_W, GFCI_H)
    appliance = _cut_top_rectangle(appliance, pump_door_a, pump_door_b, pump_door_w, pump_door_d)
    appliance = _cut_top_rectangle(appliance, hopper_door_a, hopper_door_b, hopper_door_w, hopper_door_d)

    # Front face: S3 knob + dispense tip + push button
    appliance = _add_front_knob(appliance, *S3_AT, S3_D, S3_PROTRUSION)
    appliance = _add_front_angled_knob(appliance, *TIP_AT, TIP_D, TIP_LENGTH, TIP_AXIS)
    appliance = _add_front_button(appliance, *BUTTON_AT, BUTTON_W, BUTTON_H, BUTTON_PROTRUSION)

    # Back face: umbilical (3 holes) + C14 inlet + nameplate
    appliance = _cut_back_circle(
        appliance,
        UMBILICAL_CLUSTER_A,
        UMBILICAL_CLUSTER_B + TRIANGLE_VERTEX_OFFSET,
        UMBILICAL_BULKHEAD_D,
    )
    appliance = _cut_back_circle(
        appliance,
        UMBILICAL_CLUSTER_A - TRIANGLE_BASE_HALF_WIDTH,
        UMBILICAL_CLUSTER_B - TRIANGLE_BASE_OFFSET,
        UMBILICAL_BULKHEAD_D,
    )
    appliance = _cut_back_circle(
        appliance,
        UMBILICAL_CLUSTER_A + TRIANGLE_BASE_HALF_WIDTH,
        UMBILICAL_CLUSTER_B - TRIANGLE_BASE_OFFSET,
        UMBILICAL_BULKHEAD_D,
    )
    appliance = _cut_back_rectangle(appliance, *C14_AT, C14_W, C14_H)
    appliance = _add_back_nameplate(appliance, *NAMEPLATE_AT, NAMEPLATE_W, NAMEPLATE_H, NAMEPLATE_THICKNESS)

    return appliance


def refresh_comments() -> None:
    """Refresh the [value](NAME) markdown links in this file's comments."""
    substitute_py_comments(
        Path(__file__),
        variables={
            "PUMP_DOOR_W": f"{pump_door_w:.1f} mm",
            "PUMP_DOOR_D": f"{pump_door_d:.1f} mm",
            "HOPPER_DOOR_W": f"{hopper_door_w:.1f} mm",
            "HOPPER_DOOR_D": f"{hopper_door_d:.1f} mm",
        },
        expected_counts={
            "PUMP_DOOR_W": 1,
            "PUMP_DOOR_D": 1,
            "HOPPER_DOOR_W": 1,
            "HOPPER_DOOR_D": 1,
        },
    )


if __name__ == "__main__":
    refresh_comments()
    print(f"-> updated comments in {Path(__file__).name}")
