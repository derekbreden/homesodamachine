"""
3D model of the under-counter appliance for the enclosure iso drawings.

The model is a CadQuery solid with the appliance's outer box and the
external features that read on the front, back, and top faces. Internal
geometry (foam shell, pump cases, condenser, etc.) is NOT modeled here —
this is the "skin" of the enclosure plus its external-facing features,
modeled to whatever depth lets it project to a recognizable line drawing.

Coordinate convention — matches the repo's +Z-up convention used by the
cold-core, pump-case, and faucet shell modules:
- +X is the appliance's width axis. x=0 is the LEFT side, x=W is the RIGHT.
- +Y is the appliance's depth axis. y=0 is the FRONT face, y=D is the BACK.
- +Z is the appliance's height axis. z=0 is the BOTTOM, z=H is the TOP.
- The box origin is at the front-bottom-left corner.

Drawing-only conventions:
- Cutouts that read as door/lid/panel outlines (top-face doors, back-face
  C14 inlet) are very shallow recesses — SURFACE_CUT_DEPTH deep — so they
  show up as a single visible line at the SVG stroke width rather than as
  noticeably nested rectangles.
- Protrusions that read as physical objects sticking out (S3 knob,
  dispense tip, push button, nameplate) are added via union as solids
  outside the box.
- The dispense tip is an angled cylinder whose axis is NOT aligned with
  the front face normal; the cylinder extends BACK into the wall by
  r·tan(angle from face normal) so the cylinder's lateral surface meets
  the wall plane as a clean ellipse instead of leaving a sliver.

substitute_py_comments rewrites the [value](NAME) links in this file's
comments on every run via refresh_comments(), which the drawing scripts
call from their main().
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[4]
sys.path.insert(0, str(_REPO_ROOT / "tools"))
sys.path.insert(0, str(_REPO_ROOT / "hardware" / "printed-parts" / "cadlib"))
sys.path.insert(0, str(_REPO_ROOT / "hardware" / "printed-parts" / "flavor" / "pump-case"))
sys.path.insert(0, str(_REPO_ROOT / "hardware" / "harvested" / "co2-coupling-body"))
sys.path.insert(0, str(_REPO_ROOT / "hardware" / "harvested" / "jg-bulkhead-union"))
sys.path.insert(0, str(_HERE.parents[1]))

from docgen import substitute_py_comments
from world_workplane import WorldWorkplane, xy_plane_z_up, xz_plane_y_up
from pump_case import case_outer_x, case_outer_y
import co2_coupling_body
import jg_bulkhead_union
from _enclosure_dimensions import APPLIANCE_W, APPLIANCE_D


# ---------------------------------------------------------------------------
# Outer enclosure
# ---------------------------------------------------------------------------

W = APPLIANCE_W
H = 280.0           # height (along +Z); working value, not yet derived
D = APPLIANCE_D     # depth (along +Y)


# ---------------------------------------------------------------------------
# Top-face hopper door (a runs along +X width, b runs along +Y depth)
# ---------------------------------------------------------------------------

PUMP_SIDE_BY_SIDE_CLEARANCE = 15.0
PUMP_CASE_DEPTH_CLEARANCE = 10.0

# [98.0 mm](PUMP_DOOR_W) — single-case depth + clearance, along the appliance width.
pump_door_w = case_outer_y + PUMP_CASE_DEPTH_CLEARANCE

# [165.0 mm](PUMP_DOOR_D) — two cases side-by-side + clearance, along the appliance depth.
pump_door_d = 2 * case_outer_x + PUMP_SIDE_BY_SIDE_CLEARANCE

FRONT_MARGIN = 10.0
SIDE_MARGIN = 10.0
DOOR_GAP = 10.0

# The hopper door — the larger case footprint — centered across the
# width and anchored to the front.
# [155.0 mm](HOPPER_DOOR_W) — APPLIANCE_W − 2 × SIDE_MARGIN − pump_door_w − DOOR_GAP.
hopper_door_w = W - 2 * SIDE_MARGIN - pump_door_w - DOOR_GAP
# [165.0 mm](HOPPER_DOOR_D) — matches pump door depth.
hopper_door_d = pump_door_d
hopper_door_a = W / 2
hopper_door_b = FRONT_MARGIN + hopper_door_d / 2

# Front-panel control column X (S3 knob, dispense tip, push button), and
# the CO2 port's depth anchor on the side face.
CONTROL_COLUMN_A = W - SIDE_MARGIN - hopper_door_w / 2

# GFCI access band — 27 × [18 mm](GFCI_W) exposed band centered on the 42 × 67
# Legrand 1597 body, tucked into the back-right corner.
GFCI_W = 18.0
GFCI_H = 27.0
GFCI_A = W - 38.5
GFCI_B = D - 26.0


# ---------------------------------------------------------------------------
# Front-face features (a runs along +X width, b runs along +Z height)
# ---------------------------------------------------------------------------

S3_AT = (CONTROL_COLUMN_A, 235.0)
S3_D = 32.0
S3_PROTRUSION = 19.0

TIP_AT = (CONTROL_COLUMN_A, 200.0)
TIP_D = 20.0
TIP_LENGTH = 25.0
TIP_ANGLE_FROM_VERTICAL_DEG = 40.0
# Tip points "down" (-Z) and "forward" (-Y), at [40°](TIP_ANGLE_FROM_VERTICAL_DEG) from vertical:
#   sin([40°](TIP_ANGLE_FROM_VERTICAL_DEG)) of the unit length goes into -Y (forward),
#   cos([40°](TIP_ANGLE_FROM_VERTICAL_DEG)) into -Z (down).
_tip_theta = math.radians(TIP_ANGLE_FROM_VERTICAL_DEG)
TIP_AXIS = (0.0, -math.sin(_tip_theta), -math.cos(_tip_theta))
# r·tan(angle from face normal) — extension along the axis BACK into the
# wall so the cylinder's lateral surface meets the front face cleanly
# as a full ellipse instead of leaving a sliver gap. The axis is 50°
# from the front face normal (-Y), so tan(50°) ≈ 1.192.
_tip_angle_from_face_normal = math.radians(90 - TIP_ANGLE_FROM_VERTICAL_DEG)
TIP_BACK_EXTENSION = (TIP_D / 2) * math.tan(_tip_angle_from_face_normal)

BUTTON_AT = (CONTROL_COLUMN_A, 170.0)
BUTTON_W = 80.0
BUTTON_H = 20.0
BUTTON_PROTRUSION = 10.0


# ---------------------------------------------------------------------------
# Right-side-face features
# ---------------------------------------------------------------------------
#
# Face-local coords are (y, z) — `a` runs along +Y (depth, front to back)
# as you look at the right side from outside, `b` runs along +Z (height).

# CO2 inlet — CPC LCD10004 / LCD15004 family valved coupling body.
# The part itself is modeled at canonical origin in
# `hardware/harvested/co2-coupling-body/co2_coupling_body.py`
# (standalone STEP available in the parts viewer's Reference section).
# Wall anchor on the right side face: vertically aligned with the S3
# knob's centerline on the front face; horizontally (along depth)
# centered on the funnel-door depth. The CO2 cylinder sits in the
# side air-gap beside the appliance, so the inlet is on the side
# that faces it.
CO2_PORT_WALL_AT = (hopper_door_b, S3_AT[1])     # (face-a = world Y, face-b = world Z)


# ---------------------------------------------------------------------------
# Back-face features (a runs along -X width as seen from outside, b runs
# along +Z height)
# ---------------------------------------------------------------------------

UMBILICAL_BULKHEAD_D = 17.0

# Equilateral triangle with side = bulkhead diameter (tangent circles).
_S = UMBILICAL_BULKHEAD_D
TRIANGLE_VERTEX_OFFSET = _S / math.sqrt(3)        # [9.815 mm](TRIANGLE_VERTEX_OFFSET)
TRIANGLE_BASE_HALF_WIDTH = _S / 2                  # [8.5 mm](TRIANGLE_BASE_HALF_WIDTH)
TRIANGLE_BASE_OFFSET = _S * math.sqrt(3) / 6       # [4.907 mm](TRIANGLE_BASE_OFFSET)

UMBILICAL_CLUSTER_A = W / 2
UMBILICAL_CLUSTER_B = H - 50.0

C14_AT = (70.0, H - 50.0)
C14_W = 28.0
C14_H = 20.0

NAMEPLATE_AT = (200.0, 60.0)
NAMEPLATE_W = 60.0
NAMEPLATE_H = 40.0
NAMEPLATE_THICKNESS = 1.5

# Water inlet — 1/4" push-to-connect through-wall union (McMaster
# 51055K3), loaded in
# `hardware/harvested/jg-bulkhead-union/jg_bulkhead_union.py`. Mounted on
# the back face, tube axis on world +Y, the flange seated at the wall.
# Sits in Zone B (the back-panel terminations band above the foam
# shell), left of the umbilical cluster and aligned with its row.
# Position given in world (x, z).
WATER_PORT_WALL_AT = (65.0, 230.0)
WATER_PORT_DISC_R = 17.0


# ---------------------------------------------------------------------------
# Drawing-only knob: cut depth shallow enough that the nested-rectangle
# offset is below the SVG stroke width and reads as a single line.
# ---------------------------------------------------------------------------

SURFACE_CUT_DEPTH = 0.5


# ---------------------------------------------------------------------------
# Geometry builders
# ---------------------------------------------------------------------------
#
# Uses the repo's WorldWorkplane abstraction (hardware/printed-parts/
# cadlib/world_workplane.py) on the two shared world-coord planes:
#
#   xy_plane_z_up  — XY plane with +Z normal. Used for top-face cuts
#       (offset H puts the workplane on the top face). moveTo accepts
#       (world_x, world_y) tuples directly. extrude(-depth) goes -Z,
#       into the box.
#
#   xz_plane_y_up  — XZ plane with +Y normal. Used for front- and back-
#       face features. Offset 0 puts the workplane on the front face;
#       offset D puts it on the back face. moveTo accepts (world_x,
#       world_z) tuples; flip_z handles the Y-axis chirality inversion.
#       extrude(+) goes +Y (into the box from the front, out of the box
#       from the back); extrude(-) goes -Y (out of the box from the
#       front, into the box from the back).


def _cut_top_rectangle(solid, a, b, w, h):
    """Cut a shallow rectangle from the top face (z=H) for door/lid outlines."""
    cutter = (
        WorldWorkplane(xy_plane_z_up).workplane(offset=H)
        .moveTo((a, b))
        .rect(w, h)
        .extrude(-SURFACE_CUT_DEPTH)
    )
    return solid.cut(cutter.unwrap())


def _cut_back_rectangle(solid, a, b, w, h):
    """Cut a shallow rectangle from the back face (y=D). Face-local a runs
    along -world X (mirrored as you look at the back from outside), so
    world X = W - a; face-local b runs along +Z (height)."""
    cutter = (
        WorldWorkplane(xz_plane_y_up).workplane(offset=D)
        .moveTo((W - a, b))
        .rect(w, h)
        .extrude(-SURFACE_CUT_DEPTH)
    )
    return solid.cut(cutter.unwrap())


def _cut_back_circle(solid, a, b, d):
    """Cut a shallow circle from the back face for umbilical bulkhead outlines."""
    cutter = (
        WorldWorkplane(xz_plane_y_up).workplane(offset=D)
        .moveTo((W - a, b))
        .circle(d / 2)
        .extrude(-SURFACE_CUT_DEPTH)
    )
    return solid.cut(cutter.unwrap())


def _add_front_knob(solid, a, b, d, protrusion):
    """Add a perpendicular cylindrical knob protruding from the front face."""
    knob = (
        WorldWorkplane(xz_plane_y_up).workplane(offset=0)
        .moveTo((a, b))
        .circle(d / 2)
        .extrude(-protrusion)  # negative for outward (-Y) from the front face
    )
    return solid.union(knob.unwrap())


def _add_front_angled_knob(solid, a, b, d, length, axis_3d, back_extension):
    """Add a cylindrical knob with an arbitrary axis from the front face.

    The cylinder's start point is offset BACKWARD along its axis by
    `back_extension` so its lateral surface enters the front face wall as
    a clean ellipse before exiting at the tip; without this the cylinder
    leaves a sliver gap where its axis-perpendicular base disc doesn't
    quite reach the wall plane. Total length built = length + back_extension."""
    axis_v = cq.Vector(*axis_3d)
    face_center = cq.Vector(a, 0.0, b)
    start = face_center - axis_v * back_extension
    total_length = length + back_extension
    cyl = cq.Solid.makeCylinder(d / 2, total_length, pnt=start, dir=axis_v)
    return solid.union(cq.Workplane().add(cyl))


def _add_front_button(solid, a, b, w, h, protrusion):
    """Add a rectangular protrusion from the front face."""
    button = (
        WorldWorkplane(xz_plane_y_up).workplane(offset=0)
        .moveTo((a, b))
        .rect(w, h)
        .extrude(-protrusion)
    )
    return solid.union(button.unwrap())


def _add_back_nameplate(solid, a, b, w, h, thickness):
    """Add a raised rectangular plaque to the back face (y=D)."""
    plate = (
        WorldWorkplane(xz_plane_y_up).workplane(offset=D)
        .moveTo((W - a, b))
        .rect(w, h)
        .extrude(thickness)  # positive for outward (+Y) from the back face
    )
    return solid.union(plate.unwrap())


def _positioned_coupler() -> cq.Workplane:
    """The CPC LC-family CO2 coupling body placed at the RIGHT side face
    (x=W): coupling axis on world +X, hex back face at the wall plane —
    hex body in x ∈ [W, W + hex_length], cup beyond it, thumb latch
    rising in +Z."""
    world_y, world_z = CO2_PORT_WALL_AT
    part = co2_coupling_body.build_co2_coupling_body().val()
    part = part.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), -90)
    part = part.translate(cq.Vector(W, world_y, world_z))
    return cq.Workplane().add(part)


def build_coupler() -> cq.Workplane:
    """The coupler clipped to the part in front of the wall plane (x ≥ W)
    — hex, cup, and thumb latch. The threaded shank (x < W, embedded in
    the wall behind the marking disc) is removed so it can't occlude the
    disc in the projected silhouette."""
    world_y, world_z = CO2_PORT_WALL_AT
    front_halfspace = (
        cq.Workplane().box(1000, 1000, 1000).translate((W + 500, world_y, world_z))
    )
    return _positioned_coupler().intersect(front_halfspace)


def _add_co2_port(solid, world_y, world_z):
    return solid.union(_positioned_coupler())


def _positioned_water_fitting() -> cq.Workplane:
    """The bulkhead union placed at the BACK face (y=D): tube axis on
    world +Y, the flange's seating face at the wall plane — flange,
    collet, and tube port proud in y ≥ D. The threading and far end sit
    at y < D, embedded in the box."""
    world_x, world_z = WATER_PORT_WALL_AT
    part = jg_bulkhead_union.build_jg_bulkhead_union().val()
    part = part.translate(cq.Vector(world_x, D, world_z))
    return cq.Workplane().add(part)


def build_water_fitting() -> cq.Workplane:
    """The fitting clipped to the part in front of the wall plane (y ≥ D)
    — the proud flange, collet, and tube port. The threading and far end
    (y < D, embedded in the wall behind the marking disc) are removed so
    they can't occlude the disc in the projected silhouette."""
    world_x, world_z = WATER_PORT_WALL_AT
    front_halfspace = (
        cq.Workplane().box(1000, 1000, 1000).translate((world_x, D + 500, world_z))
    )
    return _positioned_water_fitting().intersect(front_halfspace)


def _add_water_port(solid) -> cq.Workplane:
    return solid.union(_positioned_water_fitting())


def build_appliance() -> cq.Workplane:
    """Build the full appliance model as a CadQuery Workplane."""
    appliance = cq.Workplane("XY").box(W, D, H, centered=False)

    # Top face: GFCI band + the centered hopper door
    appliance = _cut_top_rectangle(appliance, GFCI_A, GFCI_B, GFCI_W, GFCI_H)
    appliance = _cut_top_rectangle(appliance, hopper_door_a, hopper_door_b, hopper_door_w, hopper_door_d)

    # Front face: S3 knob + dispense tip + push button
    appliance = _add_front_knob(appliance, *S3_AT, S3_D, S3_PROTRUSION)
    appliance = _add_front_angled_knob(
        appliance, *TIP_AT, TIP_D, TIP_LENGTH, TIP_AXIS, TIP_BACK_EXTENSION,
    )
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
    appliance = _add_water_port(appliance)

    # Right side face: CO2 inlet (CPC LC-family coupling body)
    appliance = _add_co2_port(appliance, *CO2_PORT_WALL_AT)

    return appliance


# ---------------------------------------------------------------------------
# Printed port markings: a red disc at the CO2 port on the right side
# wall, a blue disc at the water inlet on the back wall. Each is a
# printed marking, not geometry — the renderer projects the circle to a
# filled, self-outlined SVG path and clips it by the projected
# silhouette of the fitting that occludes its center, so the visible
# remainder reads as a ring.
# ---------------------------------------------------------------------------

CO2_PORT_DISC_R = 16.5

CO2_DISC_COLOR = [255, 0, 0]        # red
WATER_DISC_COLOR = [31, 111, 235]   # blue, matching the quickstart water arrows


def red_disc_render_params() -> dict:
    """CO2 disc center / axis / radius for the Blender renderer, plus the
    port-hole `target` — the coupling-mouth center out at the proud end
    of the coupler — for aiming an arrow at the hole rather than the wall
    disc."""
    world_y, world_z = CO2_PORT_WALL_AT
    proud = co2_coupling_body.hex_length + co2_coupling_body.body_length
    return {
        "center": [W + 0.05, world_y, world_z],
        "axis": [1.0, 0.0, 0.0],
        "radius": CO2_PORT_DISC_R,
        "target": [W + proud, world_y, world_z],
    }


def blue_disc_render_params() -> dict:
    """Water disc center / axis / radius for the Blender renderer, plus
    the port-hole `target` — the tube-port center out at the proud end of
    the fitting — for aiming an arrow at the hole rather than the wall
    disc."""
    world_x, world_z = WATER_PORT_WALL_AT
    return {
        "center": [world_x, D + 0.05, world_z],
        "axis": [0.0, 1.0, 0.0],
        "radius": WATER_PORT_DISC_R,
        "target": [world_x, D + jg_bulkhead_union.PROUD_LENGTH, world_z],
    }


# Iso camera directions (camera sits along these from the scene center).
_ISO_CAM_DIR = {
    "front": (1.0, -1.0, 1.0),
    "back": (1.0, 1.0, 1.0),
}


def markings(view: str) -> list:
    """The colored port markings visible in `view`: the red CO2 disc on
    the right face, the blue water disc on the back face. A marking is
    included only when its disc faces the camera (disc axis · view
    direction > 0), so a disc on a face turned away isn't painted over
    the silhouette. Each included marking is paired with the fitting
    that occludes its center."""
    cam = _ISO_CAM_DIR[view]
    specs = [
        ("co2-disc", red_disc_render_params(), CO2_DISC_COLOR, build_coupler),
        ("water-disc", blue_disc_render_params(), WATER_DISC_COLOR, build_water_fitting),
    ]
    out = []
    for id_, disc, color, clip_fn in specs:
        ax = disc["axis"]
        if ax[0] * cam[0] + ax[1] * cam[1] + ax[2] * cam[2] > 0:
            out.append({"id": id_, "disc": disc, "color": color, "clip": clip_fn()})
    return out




def refresh_comments() -> None:
    """Refresh the [value](NAME) markdown links in this file's comments."""
    substitute_py_comments(
        Path(__file__),
        variables={
            "PUMP_DOOR_W": f"{pump_door_w:.1f} mm",
            "PUMP_DOOR_D": f"{pump_door_d:.1f} mm",
            "HOPPER_DOOR_W": f"{hopper_door_w:.1f} mm",
            "HOPPER_DOOR_D": f"{hopper_door_d:.1f} mm",
            "TIP_ANGLE_FROM_VERTICAL_DEG": f"{TIP_ANGLE_FROM_VERTICAL_DEG:.0f}°",
            "TRIANGLE_VERTEX_OFFSET": f"{TRIANGLE_VERTEX_OFFSET:.4g} mm",
            "TRIANGLE_BASE_HALF_WIDTH": f"{TRIANGLE_BASE_HALF_WIDTH:.4g} mm",
            "TRIANGLE_BASE_OFFSET": f"{TRIANGLE_BASE_OFFSET:.4g} mm",
            "GFCI_W": f"{GFCI_W:.4g} mm",
        },
        expected_counts={
            "TIP_ANGLE_FROM_VERTICAL_DEG": 3,
            "TRIANGLE_VERTEX_OFFSET": 1,
            "TRIANGLE_BASE_HALF_WIDTH": 1,
            "TRIANGLE_BASE_OFFSET": 1,
            "GFCI_W": 1,
            "PUMP_DOOR_W": 1,
            "PUMP_DOOR_D": 1,
            "HOPPER_DOOR_W": 1,
            "HOPPER_DOOR_D": 1,
        },
    )


if __name__ == "__main__":
    refresh_comments()
    print(f"-> updated comments in {Path(__file__).name}")
