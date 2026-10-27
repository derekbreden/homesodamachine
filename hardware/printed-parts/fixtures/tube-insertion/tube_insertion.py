"""Horizontal tube-insertion T handle and twin steel screw-clamp fixture.

Fixture frame: X is the insertion axis, positive from the donor toward the
free tube. Y is lateral. Z is up from the printed base. The workpiece moves
in -X. The donor's original front, with its attached unpressed faucet lever,
is the open -Y side. No fixture member touches that lever or its plunger.

The source is a manual generator; importing its builders writes no files and
does not import the repository's global CAD build lock. Call main() explicitly
to export the printable solids, STEP files, payloads and design measurements.
"""

from __future__ import annotations

import ast
import hashlib
import json
import math
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
REPO = next(p for p in HERE.parents if (p / "tools" / "docgen").is_dir())
HARDWARE = REPO / "hardware"
sys.path.insert(0, str(HARDWARE / 'printed-parts/cadlib'))
import fits
DONOR_SOURCE = HARDWARE / "reference/touch-flo-faucet/westbrass-reference/westbrass_reference.py"
DONOR_STEP = DONOR_SOURCE.parent / "westbrass-reference.step"
SLEEVE_SOURCE = HARDWARE / "printed-parts/faucet/tpu-o-ring/tpu_o_ring.py"


def _numeric_constants(path):
    """Read numeric geometry without importing other generators or their locks."""
    values = {}

    def number(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name):
            return values[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -number(node.operand)
        if isinstance(node, ast.BinOp):
            a, b = number(node.left), number(node.right)
            if isinstance(node.op, ast.Add):
                return a + b
            if isinstance(node.op, ast.Sub):
                return a - b
            if isinstance(node.op, ast.Mult):
                return a * b
            if isinstance(node.op, ast.Div):
                return a / b
        raise ValueError("not a numeric geometry constant")

    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign):
            try:
                value = number(node.value)
            except (ValueError, KeyError, TypeError):
                continue
            for target in node.targets:
                if isinstance(target, ast.Name):
                    values[target.id] = float(value)
    return values


_donor = _numeric_constants(DONOR_SOURCE)
_sleeve = _numeric_constants(SLEEVE_SOURCE)
DONOR_BODY_OD = _donor["body_od"]
DONOR_SHANK_OD = _donor["shank_od"]
DONOR_SHANK_LENGTH = _donor["shank_length"]
DONOR_PORT_Y = _donor["port_center_x"]
DONOR_PORT_X = _donor["plateau_z"]
DONOR_ARCH_X = _donor["arc_peak_z"]
DONOR_PORT_DEPTH_MIN = _donor["port_bore_depth"]
TUBE_OD = _sleeve["lldpe_od"]
TUBE_ID = _sleeve["lldpe_id"]
SLEEVE_OD = _sleeve["outer_diameter"]
SLEEVE_ID = _sleeve["inner_diameter"]
SLEEVE_CAP_H = _sleeve["cap_thickness"]
SLEEVE_CAP_HOLE = _sleeve["cap_hole_diameter"]
SLEEVE_LENGTH = _sleeve["cap_thickness"] + _sleeve["cylinder_length"]

BASE_X0, BASE_X1 = -28.0, 244.5
BASE_Y0, BASE_Y1 = -100.0, 134.0
BASE_H = 8.0
TUBE_Z = 30.0
TUBE_Y = DONOR_PORT_Y
DONOR_AXIS_Z = TUBE_Z
SHANK_SLOT_D = DONOR_SHANK_OD + 0.8
DONOR_NEST_R = DONOR_BODY_OD / 2 + 0.35
THRUST_WALL_X0, THRUST_WALL_X1 = -26.0, 0.0
THRUST_WALL_Y_HALF = 60.0
THRUST_WALL_Z1 = 54.0
NEST_LENGTH = 12.0
CLOCKING_PAD_X0, CLOCKING_PAD_X1 = 20.0, 26.0
CLOCKING_PAD_HALF_WIDTH = 8.0
CLOCKING_PAD_Z1 = TUBE_Z - _donor["rect_short"] / 2

JAW_LENGTH = 44.0
LINER_LENGTH = 28.0
LINER_X0 = (JAW_LENGTH - LINER_LENGTH) / 2
LINER_START_X = LINER_X0
LINER_WIDTH = 20.0
LINER_POCKET_H = 8.0
LINER_BACK_ADDITION = 1.0
LINER_H = LINER_POCKET_H + LINER_BACK_ADDITION
GRIP_BORE_D = 7.75
JAW_HALF_H = 15.0
JAW_CORE_WIDTH = 32.0
JAW_HANDLE_WIDTH = 100.0
JAW_HANDLE_START_X = 4.0
JAW_HANDLE_END_X = JAW_LENGTH - JAW_HANDLE_START_X
JAW_BACK_H = JAW_HALF_H - LINER_POCKET_H
JAW_LINER_AXIAL_CLEARANCE = 0.3
JAW_LINER_SIDE_CLEARANCE = 0.25
JAW_TUBE_CLEARANCE_D = 10.8
CLAMP_FINAL_X = 58.0
CLAMP_BACK_X = CLAMP_FINAL_X + JAW_HANDLE_END_X
CLAMP_BOLT_X = LINER_X0 + LINER_LENGTH / 2
CLAMP_BOLT_Y = 26.0
M5_CLEARANCE_D = fits.m5_thread_pass_dia
M5_HEAD_D = 9.0
M5_HEAD_H = 5.0
M5_CS_HEAD_D = 10.2
M5_CS_HEAD_H = (M5_CS_HEAD_D - M5_CLEARANCE_D) / 2
M5_CS_OWNED_HEAD_D = 9.8
M5_CS_HEAD_RECESS = (M5_CS_HEAD_D - M5_CS_OWNED_HEAD_D) / 2
M5_NUT_WIDTH = 8.3
M5_NUT_H = 4.2
COUPLING_BOLT_X = 31.0
COUPLING_BOLT_Y = 40.0
COUPLING_TOE_R = 10.0
COUPLING_NUT_ROOF_H = 3.2
COUPLING_NUT_Z0 = -COUPLING_NUT_ROOF_H - M5_NUT_H
COUPLING_KEY_X0, COUPLING_KEY_X1 = 26.0, 34.0
COUPLING_KEY_Y = 12.0
COUPLING_KEY_W = 6.0
COUPLING_KEY_H = 3.0
COUPLING_KEY_CLEARANCE = 0.1

CARRIER_FINAL_X = 96.5
CARRIER_SHELF_LENGTH = 38.5
CARRIER_HEAD_RELIEF_X = 26.0
CARRIER_LENGTH = 124.0
CARRIER_HALF_WIDTH = JAW_HANDLE_WIDTH / 2
CARRIER_FOOT_H = 6.0
CARRIER_BOTTOM_Z = BASE_H
CARRIER_JAW_LOCAL_X = CLAMP_FINAL_X - CARRIER_FINAL_X
CARRIER_SHELF_H = TUBE_Z - JAW_HALF_H - CARRIER_BOTTOM_Z
RAIL_LATERAL_GAP = 0.1
RAIL_WIDTH = 8.0
RAIL_HEIGHT = CARRIER_FOOT_H
RAIL_X0 = CARRIER_FINAL_X - 2.0
RAIL_X1 = CARRIER_FINAL_X + CARRIER_LENGTH + 22.0
STOP_X0 = CARRIER_FINAL_X - 4.0
STOP_X1 = CARRIER_FINAL_X
STOP_Z1 = BASE_H + CARRIER_FOOT_H
STOP_INNER_HALF_WIDTH = 16.5
STOP_OUTER_HALF_WIDTH = 21.0
PRESS_TRAVEL = 20.0
REAR_STOP_X0 = CARRIER_FINAL_X + CARRIER_LENGTH + PRESS_TRAVEL
REAR_STOP_X1 = REAR_STOP_X0 + 4.0
SCREW_OFFSET_Y = 32.0
FACTORY_CLAMP_CAPACITY = 152.4
FACTORY_CLAMP_THROAT = 63.5
# These are ordinary setup envelopes, not manufacturer measured pad/profile CAD.
FACTORY_PAD_ENVELOPE_D = 30.0
FACTORY_PAD_SCHEMATIC_H = 4.0
FACTORY_HANDLE_ENVELOPE_D = 30.0
FACTORY_CLAMP_URL = "https://www.amazon.com/dp/B000FA0BL8"
FACTORY_CLAMP_MODEL = "BESSEY GSCC2.506"
PUCK_SIZE = 54.0
PUCK_H = 8.0
PUCK_CAP_RECESS_D = 11.2
PUCK_CAP_RECESS_H = 1.8
PUCK_HOLE_D = 6.8

COLOR_RIGID = cq.Color(0.16, 0.18, 0.19)
COLOR_TPU = cq.Color(0.11, 0.12, 0.13)
COLOR_DONOR = cq.Color(0.58, 0.61, 0.64)
COLOR_TUBE = cq.Color(0.84, 0.90, 0.91, 0.7)
COLOR_SLEEVE = cq.Color(0.04, 0.05, 0.06)
COLOR_STEEL = cq.Color(0.67, 0.69, 0.71)


def block(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY", origin=((x0 + x1) / 2, (y0 + y1) / 2, z0))
            .rect(x1 - x0, y1 - y0).extrude(z1 - z0))


def cylinder_x(x0, x1, y, z, radius):
    plane = cq.Plane(origin=(x0, y, z), xDir=(0, 1, 0), normal=(1, 0, 0))
    return cq.Workplane(plane).circle(radius).extrude(x1 - x0)


def vertical_hole(x, y, z0, z1, diameter):
    return cq.Workplane("XY", origin=(x, y, z0)).circle(diameter / 2).extrude(z1 - z0)


def countersink_from_below(shape, x, y, z0, shank_d=M5_CLEARANCE_D):
    cone = cq.Solid.makeCone(M5_CS_HEAD_D / 2, shank_d / 2, M5_CS_HEAD_H,
                             cq.Vector(x, y, z0), cq.Vector(0, 0, 1))
    return shape.cut(cq.Workplane("XY").add(cone))


def build_base():
    """A: bed-flat base with short steel-backed reaction block and low guides."""
    base = block(BASE_X0, BASE_X1, BASE_Y0, BASE_Y1, 0, BASE_H)
    thrust = block(THRUST_WALL_X0, THRUST_WALL_X1,
                   -THRUST_WALL_Y_HALF, THRUST_WALL_Y_HALF,
                   0, THRUST_WALL_Z1)
    shank_slot = cylinder_x(THRUST_WALL_X0 - 1, THRUST_WALL_X1 + 1, 0,
                           DONOR_AXIS_Z, SHANK_SLOT_D / 2)
    shank_open = block(THRUST_WALL_X0 - 1, THRUST_WALL_X1 + 1,
                       -SHANK_SLOT_D / 2, SHANK_SLOT_D / 2,
                       DONOR_AXIS_Z, THRUST_WALL_Z1 + 1)
    thrust = thrust.cut(shank_slot.union(shank_open))
    # Factory fixed jaws back this broad block at the same height as the load.
    # The base carries location, yaw-guide reactions and bench hold-down loads.
    # A bottom-open semicircular support only locates the robust cylindrical
    # metal base; the flat annular rear face carries the axial insertion load.
    nest = block(0, NEST_LENGTH, -19, 19, BASE_H, DONOR_AXIS_Z)
    nest = nest.cut(cylinder_x(-1, NEST_LENGTH + 1, 0, DONOR_AXIS_Z, DONOR_NEST_R))
    # The oversize saddle supplies lateral loading clearance; this tangent
    # floor locates the cylindrical metal base at the tube's exact height.
    nest = nest.union(block(0, NEST_LENGTH, -8, 8, BASE_H,
                            DONOR_AXIS_Z - DONOR_BODY_OD / 2))
    base = base.union(thrust).union(nest)
    base = base.union(block(CLOCKING_PAD_X0, CLOCKING_PAD_X1,
                            -CLOCKING_PAD_HALF_WIDTH, CLOCKING_PAD_HALF_WIDTH,
                            BASE_H, CLOCKING_PAD_Z1))
    for side in (-1, 1):
        y_inner = TUBE_Y + side * (CARRIER_HALF_WIDTH + RAIL_LATERAL_GAP)
        ya, yb = sorted((y_inner, y_inner + side * RAIL_WIDTH))
        base = base.union(block(RAIL_X0, RAIL_X1, ya, yb, BASE_H, BASE_H + RAIL_HEIGHT))
    for side in (-1, 1):
        ya, yb = sorted((TUBE_Y + side * STOP_INNER_HALF_WIDTH,
                         TUBE_Y + side * STOP_OUTER_HALF_WIDTH))
        base = base.union(block(STOP_X0, STOP_X1, ya, yb, BASE_H, STOP_Z1))
        base = base.union(block(REAR_STOP_X0, REAR_STOP_X1, ya, yb, BASE_H, STOP_Z1))
    # Small station marks are outside the full circular bearing envelopes.
    for side in (-1, 1):
        y = TUBE_Y + side * (SCREW_OFFSET_Y + FACTORY_PAD_ENVELOPE_D / 2 + 1.5)
        base = base.cut(block(THRUST_WALL_X0 - 0.1, THRUST_WALL_X0 + 0.3,
                              y - 0.4, y + 0.4, TUBE_Z - 3, TUBE_Z + 3))
    # Optional existing clamps/bolts may use these two open mounting holes.
    for x, y in ((12.0, 112.0), (170.0, 112.0)):
        base = base.cut(vertical_hole(x, y, -1, BASE_H + 1, 6.0))
    return base


def build_carrier():
    """B: long low guide carrier, with a full jaw shelf and two locating keys."""
    carrier = block(0, CARRIER_LENGTH, -CARRIER_HALF_WIDTH, CARRIER_HALF_WIDTH,
                    0, CARRIER_FOOT_H)
    carrier = carrier.union(block(CARRIER_JAW_LOCAL_X, CARRIER_JAW_LOCAL_X + CARRIER_SHELF_LENGTH,
                                   -JAW_CORE_WIDTH / 2, JAW_CORE_WIDTH / 2,
                                   0, CARRIER_SHELF_H))
    for side in (-1, 1):
        y = side * COUPLING_BOLT_Y
        # Round-ended toes provide broad countersunk screw seats beside the
        # narrow full-length shelf. Actual attached-lever clearance is checked
        # in ordinary unloaded setup, without inventing an assembled pose.
        x = CARRIER_JAW_LOCAL_X + COUPLING_BOLT_X
        toe = cq.Workplane("XY", origin=(x, y, 0)).circle(COUPLING_TOE_R).extrude(CARRIER_SHELF_H)
        toe = toe.union(block(x, 0, y - COUPLING_TOE_R, y + COUPLING_TOE_R, 0, CARRIER_SHELF_H))
        carrier = carrier.union(toe)
        carrier = carrier.cut(vertical_hole(x, y, -1, CARRIER_SHELF_H + COUPLING_KEY_H + 1,
                                            M5_CLEARANCE_D))
        carrier = countersink_from_below(carrier, x, y, 0)
        key_y = side * COUPLING_KEY_Y
        carrier = carrier.union(block(CARRIER_JAW_LOCAL_X + COUPLING_KEY_X0,
                                      CARRIER_JAW_LOCAL_X + COUPLING_KEY_X1,
                                      key_y - COUPLING_KEY_W / 2, key_y + COUPLING_KEY_W / 2,
                                      CARRIER_SHELF_H, CARRIER_SHELF_H + COUPLING_KEY_H))
    # Jaw-closure bolt heads remain installed when fitting the carrier.
    for y in (-CLAMP_BOLT_Y, CLAMP_BOLT_Y):
        carrier = carrier.cut(vertical_hole(CARRIER_JAW_LOCAL_X + CARRIER_HEAD_RELIEF_X, y,
                                            -1, CARRIER_SHELF_H + 1, M5_HEAD_D + 1.4))
    return carrier


def build_lower_jaw(with_coupling=True):
    """D: centred plus-handle jaw with proud TPU and carrier coupling."""
    jaw = block(0, JAW_LENGTH, -JAW_CORE_WIDTH / 2, JAW_CORE_WIDTH / 2,
                -JAW_HALF_H, 0)
    jaw = jaw.union(block(JAW_HANDLE_START_X, JAW_HANDLE_END_X,
                          -JAW_HANDLE_WIDTH / 2, JAW_HANDLE_WIDTH / 2,
                          -JAW_HALF_H, 0))
    liner_x0 = LINER_X0 - JAW_LINER_AXIAL_CLEARANCE / 2
    liner_x1 = LINER_X0 + LINER_LENGTH + JAW_LINER_AXIAL_CLEARANCE / 2
    liner_pocket = block(liner_x0, liner_x1,
                         -LINER_WIDTH / 2 - JAW_LINER_SIDE_CLEARANCE,
                         LINER_WIDTH / 2 + JAW_LINER_SIDE_CLEARANCE,
                         -LINER_POCKET_H, 1)
    jaw = jaw.cut(liner_pocket)
    jaw = jaw.cut(cylinder_x(-1, JAW_LENGTH + 1, 0, 0, JAW_TUBE_CLEARANCE_D / 2))
    for y in (-CLAMP_BOLT_Y, CLAMP_BOLT_Y):
        jaw = jaw.cut(vertical_hole(CLAMP_BOLT_X, y, -JAW_HALF_H - 1, 1, M5_CLEARANCE_D))
    # Metal coupling removes a free yaw joint between collar and guide carrier.
    if with_coupling:
        for side in (-1, 1):
            y = side * COUPLING_BOLT_Y
            key_y = side * COUPLING_KEY_Y
            jaw = jaw.cut(block(COUPLING_KEY_X0 - COUPLING_KEY_CLEARANCE,
                                 COUPLING_KEY_X1 + COUPLING_KEY_CLEARANCE,
                                 key_y - COUPLING_KEY_W / 2 - COUPLING_KEY_CLEARANCE,
                                 key_y + COUPLING_KEY_W / 2 + COUPLING_KEY_CLEARANCE,
                                 -JAW_HALF_H - 1, -JAW_HALF_H + COUPLING_KEY_H + COUPLING_KEY_CLEARANCE))
            jaw = jaw.cut(vertical_hole(COUPLING_BOLT_X, y, -JAW_HALF_H - 1,
                                        1, M5_CLEARANCE_D))
            ya, yb = sorted((y - side * M5_NUT_WIDTH / 2, side * (JAW_HANDLE_WIDTH / 2 + 1)))
            jaw = jaw.cut(block(COUPLING_BOLT_X - M5_NUT_WIDTH / 2,
                                 COUPLING_BOLT_X + M5_NUT_WIDTH / 2,
                                 ya, yb, COUPLING_NUT_Z0, COUPLING_NUT_Z0 + M5_NUT_H))
    return jaw


def build_upper_jaw():
    """E: upper jaw, with flat outside nut/washer faces and upward open print pocket."""
    return build_lower_jaw(with_coupling=False).mirror("XY")


def build_liner():
    """F: two identical thick 85A pads, printed to their final half-round shape."""
    liner = block(0, LINER_LENGTH, -LINER_WIDTH / 2, LINER_WIDTH / 2, 0, LINER_H)
    return liner.cut(cylinder_x(-1, LINER_LENGTH + 1, 0, LINER_H, GRIP_BORE_D / 2))


def build_cap_support_puck():
    """G: a shallow sleeve-cap seat that leaves its wall accessible to fingers."""
    puck = block(-PUCK_SIZE / 2, PUCK_SIZE / 2, -PUCK_SIZE / 2, PUCK_SIZE / 2, 0, PUCK_H)
    puck = puck.cut(vertical_hole(0, 0, -1, PUCK_H + 1, PUCK_HOLE_D))
    return puck.cut(vertical_hole(0, 0, PUCK_H - PUCK_CAP_RECESS_H,
                                  PUCK_H + 1, PUCK_CAP_RECESS_D))


def build_parts(print_frame=False):
    """Named printable parts; print_frame=True puts each specified bed face at Z=0."""
    parts = {
        "base": build_base(),
        "carrier": build_carrier(),
        "lower-jaw": build_lower_jaw(),
        "upper-jaw": build_upper_jaw(),
        "liner": build_liner(),
        "cap-support-puck": build_cap_support_puck(),
    }
    if print_frame:
        parts["lower-jaw"] = parts["lower-jaw"].translate((0, 0, JAW_HALF_H))
        parts["upper-jaw"] = parts["upper-jaw"].rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, JAW_HALF_H))
        # Tube axis vertical preserves the circular grip as an XY perimeter.
        # The footprint is a solid end face, not the thin wall of a sleeve.
        parts["liner"] = parts["liner"].rotate((0, 0, 0), (0, 1, 0), -90).translate((LINER_H, 0, 0))
    return parts


def donor_shape():
    """The exact existing donor reference, transformed to the fixture frame."""
    # Rotation about Y maps world Z -> fixture X, world X -> fixture -Z.
    return cq.importers.importStep(str(DONOR_STEP)).rotate((0, 0, 0), (0, 1, 0), 90).translate((0, 0, DONOR_AXIS_Z))


def sleeve_on_tube_shape(depth=DONOR_PORT_DEPTH_MIN, stroke=0.0):
    """Nominal expanded sleeved workpiece; drawn fit is not a deformation solution."""
    x0 = DONOR_PORT_X - depth + stroke
    # Match the accepted wall's material area when displaying it on the tube.
    expanded_od = math.sqrt(TUBE_OD ** 2 + SLEEVE_OD ** 2 - SLEEVE_ID ** 2)
    sleeve = cylinder_x(x0, x0 + SLEEVE_LENGTH, TUBE_Y, TUBE_Z, expanded_od / 2)
    cap_bore = cylinder_x(x0 - 1, x0 + SLEEVE_CAP_H, TUBE_Y, TUBE_Z, SLEEVE_CAP_HOLE / 2)
    tube_bore = cylinder_x(x0 + SLEEVE_CAP_H, x0 + SLEEVE_LENGTH + 1, TUBE_Y, TUBE_Z, TUBE_OD / 2)
    return sleeve.cut(cap_bore).cut(tube_bore)


def tube_shape(depth=DONOR_PORT_DEPTH_MIN, stroke=0.0, length=330.0):
    x0 = DONOR_PORT_X - depth + SLEEVE_CAP_H + stroke
    return cylinder_x(x0, x0 + length, TUBE_Y, TUBE_Z, TUBE_OD / 2).cut(
        cylinder_x(x0 - 1, x0 + length + 1, TUBE_Y, TUBE_Z, TUBE_ID / 2))


def bolt_shape(x, y, head_z, length=50.0):
    """Nominal M5 SHCS, head below head_z and threads above it (threads omitted)."""
    head = vertical_hole(x, y, head_z - M5_HEAD_H, head_z, 8.5)
    return head.union(vertical_hole(x, y, head_z, head_z + length, 5.0))


def countersunk_bolt_shape(x, y, top_z, length=20.0):
    """Owned DIN7991 M5 screw; top_z is its flat underside/print-bed face."""
    head_h = (9.8 - 5.0) / 2
    head = cq.Solid.makeCone(9.8 / 2, 5.0 / 2, head_h,
                             cq.Vector(x, y, top_z), cq.Vector(0, 0, 1))
    return cq.Workplane("XY").add(head).union(vertical_hole(x, y, top_z + head_h,
                                                           top_z + length, 5.0))


def square_nut_shape(x, y, z0):
    return block(x - 4, x + 4, y - 4, y + 4, z0, z0 + 4).cut(vertical_hole(x, y, z0 - 1, z0 + 5, 5.0))


def washer_shape(x, y, z0):
    return vertical_hole(x, y, z0, z0 + 1.5, 25.0).cut(vertical_hole(x, y, z0 - 1, z0 + 3, 5.5))


def clamp_stations(stroke=0.0):
    """Factory-pad contact centres; these are fixture stations, not tool CAD."""
    return [{"name": label, "side": side,
             "fixed_center_mm": [THRUST_WALL_X0, TUBE_Y + side * SCREW_OFFSET_Y, TUBE_Z],
             "moving_center_mm": [CLAMP_BACK_X + stroke, TUBE_Y + side * SCREW_OFFSET_Y, TUBE_Z]}
            for side, label in ((-1, "C1"), (1, "C2"))]


def build_clamp_reference(side, stroke=0.0):
    """Schematic GSCC2.506 steel loop with wood handle; no manufacturer fit CAD.

    Capacity and throat are manufacturer dimensions. Pad, rail, jaw, spindle
    and handle solids are illustrations/envelopes, not measured reference parts.
    No printed part captures their proprietary outlines.
    """
    if side not in (-1, 1):
        raise ValueError("clamp side must be -1 or +1")
    y = TUBE_Y + side * SCREW_OFFSET_Y
    rail_y = y + side * FACTORY_CLAMP_THROAT
    x_fixed = THRUST_WALL_X0
    x_moving = CLAMP_BACK_X + stroke
    assy = cq.Assembly(name="C1" if side < 0 else "C2")
    pad_r = FACTORY_PAD_ENVELOPE_D / 2
    assy.add(cylinder_x(x_fixed - FACTORY_PAD_SCHEMATIC_H, x_fixed, y, TUBE_Z, pad_r),
             name="fixed-pad-envelope", color=COLOR_STEEL)
    assy.add(cylinder_x(x_moving, x_moving + FACTORY_PAD_SCHEMATIC_H, y, TUBE_Z, pad_r),
             name="moving-pad-envelope", color=COLOR_STEEL)
    ya, yb = sorted((y, rail_y))
    assy.add(block(x_fixed - 16, x_fixed - 4, ya - 4, yb + 4, TUBE_Z - 6, TUBE_Z + 6),
             name="fixed-jaw-schematic", color=COLOR_STEEL)
    assy.add(block(x_moving + 32, x_moving + 44, ya - 4, yb + 4, TUBE_Z - 6, TUBE_Z + 6),
             name="sliding-jaw-schematic", color=COLOR_STEEL)
    assy.add(block(x_fixed - 16, 212, rail_y - 4, rail_y + 4, TUBE_Z - 6, TUBE_Z + 6),
             name="rail-schematic", color=COLOR_STEEL)
    assy.add(cylinder_x(x_moving + 4, x_moving + 47, y, TUBE_Z, 4),
             name="spindle-schematic", color=COLOR_STEEL)
    assy.add(cylinder_x(x_moving + 47, x_moving + 98, y, TUBE_Z,
                         FACTORY_HANDLE_ENVELOPE_D / 2), name="wood-handle-envelope",
             color=cq.Color(0.61, 0.39, 0.18))
    return assy


def build_assembly(stroke=0.0, include_workpiece=True, include_hardware=True,
                   depth=DONOR_PORT_DEPTH_MIN, include_clamps=True):
    """Placed named components; stroke20 starts at the lip, stroke0 is stop contact.

    Accepted faucet lever local geometry has no measured assembled transform.
    Its occupied side is deliberately clear; do not fabricate its installed pose.
    """
    if not 0 <= stroke <= PRESS_TRAVEL:
        raise ValueError(f"stroke must be between 0 and {PRESS_TRAVEL} mm")
    parts = build_parts()
    assy = cq.Assembly(name="tube-insertion-press")
    assy.add(parts["base"], name="base", color=COLOR_RIGID)
    carrier = parts["carrier"].translate((CARRIER_FINAL_X + stroke, TUBE_Y, CARRIER_BOTTOM_Z))
    assy.add(carrier, name="carrier", color=COLOR_RIGID)
    jaw_place = (CLAMP_FINAL_X + stroke, TUBE_Y, TUBE_Z)
    assy.add(parts["lower-jaw"].translate(jaw_place), name="lower-jaw", color=COLOR_RIGID)
    assy.add(parts["upper-jaw"].translate(jaw_place), name="upper-jaw", color=COLOR_RIGID)
    liner_x = CLAMP_FINAL_X + stroke + LINER_X0
    lower = parts["liner"].translate((liner_x, TUBE_Y, TUBE_Z - LINER_POCKET_H))
    upper = parts["liner"].mirror("XY").translate((liner_x, TUBE_Y, TUBE_Z + LINER_POCKET_H))
    assy.add(lower, name="lower-liner", color=COLOR_TPU)
    assy.add(upper, name="upper-liner", color=COLOR_TPU)
    if include_workpiece:
        assy.add(donor_shape(), name="touch-flo-donor", color=COLOR_DONOR)
        assy.add(tube_shape(depth, stroke), name="lldpe-tube", color=COLOR_TUBE)
        assy.add(sleeve_on_tube_shape(depth, stroke), name="tpu-sealing-thimble", color=COLOR_SLEEVE)
    if include_hardware:
        for side, label in ((-1, "front"), (1, "rear")):
            bx, by = CLAMP_FINAL_X + stroke + CLAMP_BOLT_X, TUBE_Y + side * CLAMP_BOLT_Y
            hz = TUBE_Z - JAW_HALF_H
            assy.add(bolt_shape(bx, by, hz), name=f"clamp-{label}-m5x50", color=COLOR_STEEL)
            wz = TUBE_Z + JAW_HALF_H
            assy.add(washer_shape(bx, by, wz), name=f"clamp-{label}-washer", color=COLOR_STEEL)
            assy.add(square_nut_shape(bx, by, wz + 1.5), name=f"clamp-{label}-nut", color=COLOR_STEEL)
            cx, cy = CLAMP_FINAL_X + stroke + COUPLING_BOLT_X, TUBE_Y + side * COUPLING_BOLT_Y
            assy.add(countersunk_bolt_shape(cx, cy, CARRIER_BOTTOM_Z + M5_CS_HEAD_RECESS),
                     name=f"carrier-{label}-m5x20", color=COLOR_STEEL)
            assy.add(square_nut_shape(cx, cy, TUBE_Z + COUPLING_NUT_Z0),
                     name=f"carrier-{label}-nut", color=COLOR_STEEL)
    if include_clamps:
        for side, label in ((-1, "C1"), (1, "C2")):
            assy.add(build_clamp_reference(side, stroke), name=label)
    return assy


def _bbox(shape):
    bb = shape.val().BoundingBox()
    return {"min_mm": [bb.xmin, bb.ymin, bb.zmin], "max_mm": [bb.xmax, bb.ymax, bb.zmax],
            "size_mm": [bb.xlen, bb.ylen, bb.zlen]}


def part_manifest(parts=None):
    parts = parts or build_parts(print_frame=True)
    letters = {"base": "A", "carrier": "B", "lower-jaw": "D",
               "upper-jaw": "E", "liner": "F", "cap-support-puck": "G"}
    return {"schema": 1, "frame": "X insertion axis from donor toward free tube; Z up from bed",
            "parts": [{"name": name, "letter": letters[name], "quantity": 2 if name == "liner" else 1,
                       "material": "TPU 85A" if name == "liner" else "PET-GF15",
                       "filename": f"tube-insertion-{name}-print.stl",
                       "step": f"tube-insertion-{name}.step",
                       "print_rotation_x_degrees": 0, "print_stl_is_pretransformed": True,
                       "bbox": _bbox(shape),
                       "support_strategy": (
                                            "Solid end face on bed; tube axis vertical; repeated XY semicircle; automatic brim retained"
                                            if name == "liner" else
                                            "Flat bed face; native automatic Tree review for functional side-loading nut pockets"
                                            if name == "lower-jaw" else
                                            "Flat bed face with open functional holes and pockets; retain native automatic Tree decisions")}
                      for name, shape in parts.items()],
            "hardware": [
                {"name": "BESSEY GSCC2.506 6-inch screw clamp", "letter": "C", "quantity": 2,
                 "role": "C1 and C2 complete metal screw and reaction loops", "owned": False,
                 "prime_url": FACTORY_CLAMP_URL, "reference_model_scope": "Schematic only; ordinary setup checks actual contact feet and full 20 mm screw travel"},
                {"name": "M5 x 50 socket-head screw", "quantity": 2, "role": "two jaw closure bolts", "owned": True},
                {"name": "M5 x 20 DIN7991 countersunk screw", "quantity": 2, "role": "two lower-jaw to carrier coupling bolts", "owned": True},
                {"name": "M5 x 0.8 square nut, 8 x 4 mm", "quantity": 4, "role": "two jaw closure nuts and two carrier coupling nuts", "owned": True},
                {"name": "M5 fender washer, OD 25 mm", "quantity": 2, "role": "two jaw closure load spreaders", "owned": True},
                {"name": "Owned 4-inch steel C-clamp", "quantity": 2, "role": "hold base stationary at bench edge for two-hand operation", "owned": True},
            ],
            "factory_clamp_setup": {"stations": clamp_stations(PRESS_TRAVEL),
                                    "pad_envelope_diameter_mm": FACTORY_PAD_ENVELOPE_D,
                                    "initial_opening_mm": CLAMP_BACK_X + PRESS_TRAVEL - THRUST_WALL_X0,
                                    "final_opening_mm": CLAMP_BACK_X - THRUST_WALL_X0,
                                    "rated_capacity_mm": FACTORY_CLAMP_CAPACITY,
                                    "scope": "Opening dimension and adaptable flat bearing stations; schematic tool solids are not measured manufacturer CAD"}}


def main():
    # Export helpers import the global build lock only in this explicit manual run.
    sys.path.insert(0, str(HARDWARE / "scripts"))
    from _cadq_export import export_assembly
    printed = build_parts(print_frame=True)
    manifest = part_manifest(printed)
    for name, shape in printed.items():
        out = HERE / f"tube-insertion-{name}"
        assy = cq.Assembly(name=out.name).add(shape, name=name, color=COLOR_TPU if name == "liner" else COLOR_RIGID)
        export_assembly(assy, str(out.with_suffix(".step")))
        cq.exporters.export(shape, str(HERE / f"tube-insertion-{name}-print.stl"), tolerance=0.025, angularTolerance=0.08)
    export_assembly(build_assembly(), str(HERE / "tube-insertion-assembly.step"))
    manifest["source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    manifest["reference_source_sha256"] = {
        str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (DONOR_SOURCE, SLEEVE_SOURCE)}
    (HERE / "parts.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
