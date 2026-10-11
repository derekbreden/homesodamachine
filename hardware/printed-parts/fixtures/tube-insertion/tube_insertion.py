"""Horizontal tube-insertion T handle and guided bench press.

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

BASE_X0, BASE_X1 = -12.0, 196.0
BASE_Y0, BASE_Y1 = -36.0, 198.0
BASE_H = 8.0
TUBE_Z = 30.0
TUBE_Y = DONOR_PORT_Y
DONOR_AXIS_Z = TUBE_Z
SHANK_SLOT_D = DONOR_SHANK_OD + 0.8
DONOR_NEST_R = DONOR_BODY_OD / 2 + 0.35
THRUST_WALL_X0, THRUST_WALL_X1 = -12.0, 0.0
THRUST_WALL_Y_HALF = 19.0
THRUST_WALL_Z1 = TUBE_Z + 19.0
NEST_LENGTH = 12.0
CLOCKING_PAD_X0, CLOCKING_PAD_X1 = 20.0, 26.0
CLOCKING_PAD_HALF_WIDTH = 8.0
CLOCKING_PAD_Z1 = TUBE_Z - _donor["rect_short"] / 2

JAW_LENGTH = 38.5
LINER_LENGTH = 28.0
LINER_X0 = 2.0
LINER_START_X = LINER_X0
LINER_WIDTH = 20.0
LINER_H = 8.0
GRIP_BORE_D = 9.25
JAW_HALF_H = 11.0
JAW_CORE_WIDTH = 32.0
JAW_HANDLE_WIDTH = 77.0
JAW_HANDLE_START_X = 13.5
JAW_BACK_H = JAW_HALF_H - LINER_H
JAW_LINER_AXIAL_CLEARANCE = 0.3
JAW_LINER_SIDE_CLEARANCE = 0.25
JAW_TUBE_CLEARANCE_D = 10.8
CLAMP_FINAL_X = 58.0
CLAMP_BACK_X = CLAMP_FINAL_X + JAW_LENGTH
CLAMP_BOLT_X = 26.0
CLAMP_BOLT_Y = 26.0
M5_CLEARANCE_D = 5.5
M5_HEAD_D = 9.0
M5_HEAD_H = 5.0
M5_CS_HEAD_D = 10.2
M5_CS_HEAD_H = (M5_CS_HEAD_D - M5_CLEARANCE_D) / 2
M5_NUT_WIDTH = 8.3
M5_NUT_H = 4.2

RAM_FINAL_X = CLAMP_BACK_X
RAM_LENGTH = 26.0
RAM_FOOT_LENGTH = 52.0
RAM_BACK_X = RAM_FINAL_X + RAM_LENGTH
RAM_HALF_WIDTH = 32.0
RAM_FOOT_H = 6.0
RAM_BOTTOM_Z = BASE_H
RAM_GROOVE_HALF = 7.0
RAM_FORK_HALF_WIDTH = 32.0
RAM_TOP_Z = TUBE_Z + 6.0
RAM_SHELF_LENGTH = JAW_LENGTH
RAM_SHELF_HALF_WIDTH = JAW_CORE_WIDTH / 2
RAM_SHELF_H = TUBE_Z - JAW_HALF_H - RAM_BOTTOM_Z
RAIL_LATERAL_GAP = 0.2
RAIL_WIDTH = 8.0
RAIL_HEIGHT = 10.0
RAIL_X0 = RAM_FINAL_X - 2.0
RAIL_X1 = RAM_FINAL_X + RAM_FOOT_LENGTH + 24.0
STOP_X0 = RAM_FINAL_X - 4.0
STOP_X1 = RAM_FINAL_X
STOP_Z1 = BASE_H + 5.0
STOP_INNER_HALF_WIDTH = RAM_SHELF_HALF_WIDTH + 1.5
PRESS_TRAVEL = 20.0
REAR_STOP_X0 = RAM_FINAL_X + RAM_FOOT_LENGTH + PRESS_TRAVEL
REAR_STOP_X1 = REAR_STOP_X0 + 4.0
PRESS_SHORT_ARM = 30.0
PRESS_HAND_ARM = 120.0
PRESS_LEVER_WIDTH = 24.0
PRESS_LEVER_H = 8.0
PRESS_CAM_R = PRESS_LEVER_WIDTH / 2
PRESS_STEM_JOIN_Y = -22.0
PRESS_STEM_JOIN_HALF_WIDTH = 4.0
PRESS_LEVER_Z0 = TUBE_Z - PRESS_LEVER_H / 2
PRESS_PIVOT_X = RAM_BACK_X + PRESS_CAM_R
PRESS_CAM_FINAL_Y = TUBE_Y + 20.0
PRESS_PIVOT_Y = PRESS_CAM_FINAL_Y + PRESS_SHORT_ARM
PRESS_PIVOT_Z = TUBE_Z
PRESS_PIVOT_PLATFORM = 32.0
PRESS_PIVOT_HOLE_D = 5.6
PIVOT_COUNTERBORE_D = 9.2
PIVOT_COUNTERBORE_H = 5.4
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
    """A: bed-flat base, annular thrust wall, open donor saddle and ram guides."""
    base = block(BASE_X0, BASE_X1, BASE_Y0, BASE_Y1, 0, BASE_H)
    thrust = block(THRUST_WALL_X0, THRUST_WALL_X1,
                   -THRUST_WALL_Y_HALF, THRUST_WALL_Y_HALF,
                   BASE_H, THRUST_WALL_Z1)
    shank_slot = cylinder_x(THRUST_WALL_X0 - 1, THRUST_WALL_X1 + 1, 0,
                           DONOR_AXIS_Z, SHANK_SLOT_D / 2)
    shank_open = block(THRUST_WALL_X0 - 1, THRUST_WALL_X1 + 1,
                       -SHANK_SLOT_D / 2, SHANK_SLOT_D / 2,
                       DONOR_AXIS_Z, THRUST_WALL_Z1 + 1)
    thrust = thrust.cut(shank_slot.union(shank_open))
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
        y_inner = TUBE_Y + side * (RAM_HALF_WIDTH + RAIL_LATERAL_GAP)
        ya, yb = sorted((y_inner, y_inner + side * RAIL_WIDTH))
        base = base.union(block(RAIL_X0, RAIL_X1, ya, yb, BASE_H, BASE_H + RAIL_HEIGHT))
    for side in (-1, 1):
        ya, yb = sorted((TUBE_Y + side * STOP_INNER_HALF_WIDTH,
                         TUBE_Y + side * RAM_HALF_WIDTH))
        base = base.union(block(STOP_X0, STOP_X1, ya, yb, BASE_H, STOP_Z1))
        base = base.union(block(REAR_STOP_X0, REAR_STOP_X1, ya, yb, BASE_H, STOP_Z1))
    pedestal = block(PRESS_PIVOT_X - PRESS_PIVOT_PLATFORM / 2,
                     PRESS_PIVOT_X + PRESS_PIVOT_PLATFORM / 2,
                     PRESS_PIVOT_Y - PRESS_PIVOT_PLATFORM / 2,
                     PRESS_PIVOT_Y + PRESS_PIVOT_PLATFORM / 2,
                     BASE_H, PRESS_LEVER_Z0 - 0.3)
    base = base.union(pedestal)
    base = base.cut(vertical_hole(PRESS_PIVOT_X, PRESS_PIVOT_Y, -1,
                                  PRESS_LEVER_Z0 + 1, PRESS_PIVOT_HOLE_D))
    base = base.cut(vertical_hole(PRESS_PIVOT_X, PRESS_PIVOT_Y, -0.1,
                                  PIVOT_COUNTERBORE_H, PIVOT_COUNTERBORE_D))
    # Optional existing clamps/bolts may use these two open mounting holes.
    for x, y in ((12.0, 112.0), (170.0, 170.0)):
        base = base.cut(vertical_hole(x, y, -1, BASE_H + 1, 6.0))
    return base


def build_ram():
    """B: one-piece ram; open top and both ends pass the entire free tube."""
    foot = block(0, RAM_FOOT_LENGTH, -RAM_HALF_WIDTH, RAM_HALF_WIDTH, 0, RAM_FOOT_H)
    fork_h = RAM_TOP_Z - RAM_BOTTOM_Z
    for side in (-1, 1):
        y0, y1 = sorted((side * RAM_GROOVE_HALF, side * RAM_FORK_HALF_WIDTH))
        foot = foot.union(block(0, RAM_LENGTH, y0, y1, RAM_FOOT_H, fork_h))
    # The complete lower jaw rests at the tube's nominal height; the broad
    # central shelf is open above and leaves both protruding jaw bolt heads clear.
    foot = foot.union(block(-RAM_SHELF_LENGTH, 0,
                            -RAM_SHELF_HALF_WIDTH, RAM_SHELF_HALF_WIDTH,
                            0, RAM_SHELF_H))
    return foot


def build_press_lever():
    """C: a 4:1 seesaw press lever, printed flat in its bending plane."""
    bar = block(-PRESS_LEVER_WIDTH / 2, PRESS_LEVER_WIDTH / 2,
                0, PRESS_HAND_ARM, 0, PRESS_LEVER_H)
    # The short stem narrows into the circular nose to clear the guided ram
    # at the start of its sweep. The cam disk itself backs the stem's tip.
    stem = (cq.Workplane("XY")
            .polyline([(-PRESS_LEVER_WIDTH / 2, 0), (PRESS_LEVER_WIDTH / 2, 0),
                       (PRESS_STEM_JOIN_HALF_WIDTH, PRESS_STEM_JOIN_Y),
                       (-PRESS_STEM_JOIN_HALF_WIDTH, PRESS_STEM_JOIN_Y)])
            .close().extrude(PRESS_LEVER_H))
    bar = bar.union(stem)
    for y in (-PRESS_SHORT_ARM, PRESS_HAND_ARM):
        end = cq.Workplane("XY", origin=(0, y, 0)).circle(PRESS_LEVER_WIDTH / 2).extrude(PRESS_LEVER_H)
        bar = bar.union(end)
    return bar.cut(vertical_hole(0, 0, -1, PRESS_LEVER_H + 1, PRESS_PIVOT_HOLE_D))


def build_lower_jaw():
    """D: lower T-handle jaw. Hard mating faces limit squeeze to GRIP_BORE_D."""
    jaw = block(0, JAW_LENGTH, -JAW_CORE_WIDTH / 2, JAW_CORE_WIDTH / 2,
                -JAW_HALF_H, 0)
    jaw = jaw.union(block(JAW_HANDLE_START_X, JAW_LENGTH,
                          -JAW_HANDLE_WIDTH / 2, JAW_HANDLE_WIDTH / 2,
                          -JAW_HALF_H, 0))
    liner_x0 = LINER_X0 - JAW_LINER_AXIAL_CLEARANCE / 2
    liner_x1 = LINER_X0 + LINER_LENGTH + JAW_LINER_AXIAL_CLEARANCE / 2
    liner_pocket = block(liner_x0, liner_x1,
                         -LINER_WIDTH / 2 - JAW_LINER_SIDE_CLEARANCE,
                         LINER_WIDTH / 2 + JAW_LINER_SIDE_CLEARANCE,
                         -LINER_H, 1)
    jaw = jaw.cut(liner_pocket)
    jaw = jaw.cut(cylinder_x(-1, JAW_LENGTH + 1, 0, 0, JAW_TUBE_CLEARANCE_D / 2))
    for y in (-CLAMP_BOLT_Y, CLAMP_BOLT_Y):
        jaw = jaw.cut(vertical_hole(CLAMP_BOLT_X, y, -JAW_HALF_H - 1, 1, M5_CLEARANCE_D))
    return jaw


def build_upper_jaw():
    """E: upper jaw, with flat outside nut/washer faces and upward open print pocket."""
    return build_lower_jaw().mirror("XY")


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
        "ram": build_ram(),
        "press-lever": build_press_lever(),
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


def press_angle(stroke):
    """Angle above final position for 0..20mm travel; slide stays translational."""
    return math.degrees(math.asin(stroke / PRESS_SHORT_ARM))


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


def square_nut_shape(x, y, z0):
    return block(x - 4, x + 4, y - 4, y + 4, z0, z0 + 4).cut(vertical_hole(x, y, z0 - 1, z0 + 5, 5.0))


def washer_shape(x, y, z0):
    return vertical_hole(x, y, z0, z0 + 1.5, 25.0).cut(vertical_hole(x, y, z0 - 1, z0 + 3, 5.5))


def build_assembly(stroke=0.0, include_workpiece=True, include_hardware=True, depth=DONOR_PORT_DEPTH_MIN):
    """Placed named components; stroke20 starts at the lip, stroke0 is stop contact.

    Accepted faucet lever local geometry has no measured assembled transform.
    Its occupied side is deliberately clear; do not fabricate its installed pose.
    """
    if not 0 <= stroke <= PRESS_TRAVEL:
        raise ValueError(f"stroke must be between 0 and {PRESS_TRAVEL} mm")
    parts = build_parts()
    assy = cq.Assembly(name="tube-insertion-press")
    assy.add(parts["base"], name="base", color=COLOR_RIGID)
    ram = parts["ram"].translate((RAM_FINAL_X + stroke, TUBE_Y, RAM_BOTTOM_Z))
    assy.add(ram, name="ram", color=COLOR_RIGID)
    lever = parts["press-lever"].rotate((0, 0, 0), (0, 0, 1), press_angle(stroke)).translate(
        (PRESS_PIVOT_X, PRESS_PIVOT_Y, PRESS_LEVER_Z0))
    assy.add(lever, name="press-lever", color=COLOR_RIGID)
    jaw_place = (CLAMP_FINAL_X + stroke, TUBE_Y, TUBE_Z)
    assy.add(parts["lower-jaw"].translate(jaw_place), name="lower-jaw", color=COLOR_RIGID)
    assy.add(parts["upper-jaw"].translate(jaw_place), name="upper-jaw", color=COLOR_RIGID)
    liner_x = CLAMP_FINAL_X + stroke + LINER_X0
    lower = parts["liner"].translate((liner_x, TUBE_Y, TUBE_Z - LINER_H))
    upper = parts["liner"].mirror("XY").translate((liner_x, TUBE_Y, TUBE_Z + LINER_H))
    assy.add(lower, name="lower-liner", color=COLOR_TPU)
    assy.add(upper, name="upper-liner", color=COLOR_TPU)
    if include_workpiece:
        assy.add(donor_shape(), name="touch-flo-donor", color=COLOR_DONOR)
        assy.add(tube_shape(depth, stroke), name="lldpe-tube", color=COLOR_TUBE)
        assy.add(sleeve_on_tube_shape(depth, stroke), name="tpu-sealing-thimble", color=COLOR_SLEEVE)
    if include_hardware:
        pivot_head_z = PIVOT_COUNTERBORE_H
        assy.add(bolt_shape(PRESS_PIVOT_X, PRESS_PIVOT_Y, pivot_head_z), name="pivot-m5x50", color=COLOR_STEEL)
        pivot_washer_z = PRESS_LEVER_Z0 + PRESS_LEVER_H + 0.2
        assy.add(washer_shape(PRESS_PIVOT_X, PRESS_PIVOT_Y, pivot_washer_z), name="pivot-washer", color=COLOR_STEEL)
        for i in range(2):
            assy.add(square_nut_shape(PRESS_PIVOT_X, PRESS_PIVOT_Y, pivot_washer_z + 1.5 + i * 4),
                     name=f"pivot-nut-{i + 1}", color=COLOR_STEEL)
        for side, label in ((-1, "front"), (1, "rear")):
            bx, by = CLAMP_FINAL_X + stroke + CLAMP_BOLT_X, TUBE_Y + side * CLAMP_BOLT_Y
            hz = TUBE_Z - JAW_HALF_H
            assy.add(bolt_shape(bx, by, hz), name=f"clamp-{label}-m5x50", color=COLOR_STEEL)
            wz = TUBE_Z + JAW_HALF_H
            assy.add(washer_shape(bx, by, wz), name=f"clamp-{label}-washer", color=COLOR_STEEL)
            assy.add(square_nut_shape(bx, by, wz + 1.5), name=f"clamp-{label}-nut", color=COLOR_STEEL)
    return assy


def _bbox(shape):
    bb = shape.val().BoundingBox()
    return {"min_mm": [bb.xmin, bb.ymin, bb.zmin], "max_mm": [bb.xmax, bb.ymax, bb.zmax],
            "size_mm": [bb.xlen, bb.ylen, bb.zlen]}


def part_manifest(parts=None):
    parts = parts or build_parts(print_frame=True)
    letters = {"base": "A", "ram": "B", "press-lever": "C", "lower-jaw": "D",
               "upper-jaw": "E", "liner": "F", "cap-support-puck": "G"}
    return {"schema": 1, "frame": "X insertion axis from donor toward free tube; Z up from bed",
            "parts": [{"name": name, "letter": letters[name], "quantity": 2 if name == "liner" else 1,
                       "material": "TPU 85A" if name == "liner" else "PET-GF15",
                       "filename": f"tube-insertion-{name}-print.stl",
                       "step": f"tube-insertion-{name}.step",
                       "print_rotation_x_degrees": 0, "print_stl_is_pretransformed": True,
                       "bbox": _bbox(shape),
                       "support_strategy": ("Flat bed face and open features up; short underside pivot-head pocket permits accessible automatic support"
                                            if name == "base" else
                                            "Solid end face on bed; tube axis vertical; repeated XY semicircle; automatic brim retained"
                                            if name == "liner" else
                                            "Flat bed face and open features up; no CAD ceilings or undercuts")}
                      for name, shape in parts.items()],
            "hardware": [
                {"name": "M5 x 50 socket-head screw", "quantity": 3, "role": "two jaw bolts and press-lever pivot", "owned": True},
                {"name": "M5 x 0.8 square nut, 8 x 4 mm", "quantity": 4, "role": "two jaw closure nuts and two jammed pivot nuts", "owned": True},
                {"name": "M5 fender washer, OD 25 mm", "quantity": 3, "role": "two jaw load spreaders and pivot thrust washer", "owned": True},
            ]}


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
