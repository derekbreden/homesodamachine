"""PET-GF cap-weld tube rotator.

World frame:
  Z is the rotary axis and points up through the 5 inch tube.
  X points from the tube axis toward the NEMA 23 motor.
  Y completes the right-handed frame.
  Z=0 is the stationary base's bottom face.

The base, motor tower, turntable, tube nest, three jaw caps, ball cage, and
retainer are printable.  The turntable runs on the project's stock 10 mm PP
balls.  The 90-tooth HTD-5M pulley is part of the turntable and is driven by the
purchased 20-tooth pulley and 550 mm belt.
"""

import math
import sys
from pathlib import Path

import cadquery as cq


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_repo = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_repo / "tools"))
sys.path.insert(0, str(_here.parent))

from _cadq_export import export_assembly  # noqa: E402
from _materials import (  # noqa: E402
    M_ALUMINIUM,
    M_COPPER,
    M_PETGF_BLACK,
    M_STAINLESS,
    M_TPU_BLACK,
    one_body,
)
from docgen import substitute_md, substitute_py_comments  # noqa: E402

import _rotator_interface as interface  # noqa: E402


# Stationary footprint — one H2C-bed print, with the tube axis left of centre
# so the motor and its tower remain on the same base.
BASE_X = 300.0
BASE_Y = 250.0
BASE_Z = 12.0
BASE_CENTER_X = 30.0
BASE_CORNER_R = 12.0
BASE_X_MIN = BASE_CENTER_X - BASE_X / 2.0
BASE_X_MAX = BASE_CENTER_X + BASE_X / 2.0
BASE_Y_MIN = -BASE_Y / 2.0
BASE_Y_MAX = BASE_Y / 2.0
BENCH_HOLE_D = 10.0
BENCH_HOLE_MARGIN = 18.0
BASE_FOOT_X = 44.0
BASE_FOOT_Y = 32.0
BASE_FOOT_H = interface.BASE_CLEARANCE
BASE_FOOT_CENTERS = (
    (-75.0, -100.0),
    (-75.0, 100.0),
    (135.0, -100.0),
    (135.0, 100.0),
)
BASE_FOOT_SCREW_X = 10.0
BASE_FOOT_INSERT_D = 4.0
BASE_FOOT_INSERT_DEPTH = 5.2
BASE_FOOT_SCREW_LENGTH = 25.0

# One large-diameter race carries thrust and radial load.  The balls are stock
# 10 mm polypropylene; the cage spaces 36 of them without carrying load.
BALL_D = 10.0
BALL_CLEARANCE = 0.15
BALL_RACE_R = 82.5
BALL_COUNT = 36
BALL_CENTER_Z = BASE_Z + 3.0
RACE_CUT_R = BALL_D / 2.0 + BALL_CLEARANCE
CAGE_Z = BALL_CENTER_Z - 1.0
CAGE_H = 2.0
CAGE_INNER_R = BALL_RACE_R - 7.5
CAGE_OUTER_R = BALL_RACE_R + 7.5
CAGE_POCKET_D = BALL_D + 0.55

# The moving disk sits 6 mm above the base top: each race receives 2 mm of the
# 10 mm ball.  Its wide pitch radius is the angular datum, not the centre hub.
PLATTER_R = 94.0
PLATTER_Z0 = BASE_Z + 6.0
PLATTER_Z1 = PLATTER_Z0 + 6.0
SERVICE_BORE_D = interface.SERVICE_BORE_DIAMETER
HUB_OD = 112.0
HUB_CLEARANCE_D = 114.0
HUB_Z0 = 6.0
RETAINER_OD = 124.0
RETAINER_H = 4.0
RETAINER_GAP = 1.0
RETAINER_POCKET_D = 126.0
RETAINER_POCKET_H = 6.0
RETAINER_SCREW_R = 51.0
RETAINER_BOSS_R = 4.5
RETAINER_BOSS_H = RETAINER_GAP
RETAINER_INSERT_DEPTH = 6.5
M3_HEAD_D = 6.2
M3_HEAD_DEPTH = 3.2

# Printed 90T pulley.  The groove is a low-speed printable HTD approximation:
# exact 5 mm pitch, 2.1 mm radial depth, rounded-belt clearance supplied by the
# belt itself.  The first belt-fit coupon is the acceptance gate before the
# complete turntable is printed.
TABLE_PITCH_R = interface.pitch_diameter(interface.TABLE_PULLEY_TEETH) / 2.0
PITCH_LINE_OFFSET = 0.57
PULLEY_TIP_R = TABLE_PITCH_R - PITCH_LINE_OFFSET
PULLEY_GROOVE_DEPTH = 2.10
PULLEY_ROOT_R = PULLEY_TIP_R - PULLEY_GROOVE_DEPTH
PULLEY_INNER_R = 64.5
PULLEY_Z0 = 32.0
PULLEY_TOOTH_Z0 = PULLEY_Z0 + 1.0
PULLEY_TOOTH_H = 17.0
PULLEY_Z1 = PULLEY_TOOTH_Z0 + PULLEY_TOOTH_H + 1.0
PULLEY_FLANGE_R = PULLEY_TIP_R + 2.0
PULLEY_FLANGE_H = 1.0
GROOVE_OUTER_HALF_W = 1.70
GROOVE_ROOT_HALF_W = 1.25
COUPON_TEETH = 12

# The central pedestal places the replaceable precision nest above the belt.
PEDESTAL_R = PULLEY_INNER_R + 1.5
NEST_SEAT_Z = 52.0
REGISTER_OD = 112.0
REGISTER_H = 3.0
REGISTER_SLIP = 0.25
NEST_SCREW_R = 61.0
NEST_SCREW_D = 3.5
NEST_INSERT_D = 4.0
NEST_INSERT_DEPTH = 5.2

# Tube nest — the [4.5](WR_PILOT_H) pilot fits above a welded plate's
# [6.35](WR_RECESS) recess.  The three screw-driven jaw caps carry the OD;
# the pilot carries the ID; the end face lands on the annular seat between them.
NEST_OD = 150.0
NEST_BASE_H = 8.0
NEST_OUTER_H = 10.0
NEST_CENTER_BORE_D = SERVICE_BORE_D
PILOT_OD = 123.30
PILOT_ID = 100.0
PILOT_H = 4.5
OUTER_BORE_D = 127.80
OUTER_COLLAR_OD = NEST_OD
JAW_GUIDE_INNER_R = 63.45
JAW_GUIDE_OUTER_R = 67.50
JAW_HALF_ANGLE = 7.0
JAW_H = 7.0
JAW_SOCKET_D = 2.85
JAW_SOCKET_DEPTH = 2.5
JAW_GUIDE_SLIP = 0.20
JAW_Z0 = NEST_BASE_H + 1.5
JAW_SCREW_Z = JAW_Z0 + JAW_H / 2.0
JAW_INSERT_D = 4.0
JAW_INSERT_DEPTH = 5.2
JAW_SHANK_D = 3.4

# The purchased belt fixes the exact nominal centre.  Slots only move the motor
# outward: belt installation occurs at the nominal end and tension is added by
# sliding away from the turntable.
MOTOR_CENTER_NOMINAL = interface.belt_center_distance()
MOTOR_CENTER_MIN = MOTOR_CENTER_NOMINAL - 1.0
MOTOR_CENTER_MAX = MOTOR_CENTER_NOMINAL + 7.0
MOTOR_SLOT_R = 1.8
MOTOR_FACE_Z = 54.0
MOTOR_PULLEY_Z0 = MOTOR_FACE_Z - interface.MOTOR_SHAFT_LENGTH + 1.0
MOTOR_PULLEY_Z1 = MOTOR_PULLEY_Z0 + 18.0
MOTOR_PULLEY_CORE_D = interface.pitch_diameter(interface.MOTOR_PULLEY_TEETH) - 1.1
MOTOR_PULLEY_FLANGE_D = MOTOR_PULLEY_CORE_D + 7.0

# The motor drawing specifies four plain Ø5.2 mm flange holes, not threads.
# A separate sliding cradle therefore locates the Ø38.1 pilot and clamps the
# 57.3 mm frame.  Four underside M3 screws move the complete cradle in the
# tower slots; four side screws and two load-spreading pads retain the motor.
MOTOR_CRADLE_X = 66.0
MOTOR_CRADLE_Y = 75.0
MOTOR_CRADLE_BASE_H = 8.0
MOTOR_CRADLE_Z0 = MOTOR_FACE_Z - MOTOR_CRADLE_BASE_H
MOTOR_CRADLE_INNER_X = 58.0
MOTOR_CRADLE_INNER_Y = 64.0
MOTOR_CRADLE_WALL_H = 16.0
MOTOR_CRADLE_PILOT_D = 38.6
MOTOR_CRADLE_BOLT_SQUARE = interface.MOTOR_MOUNT_SQUARE
MOTOR_CRADLE_INSERT_DEPTH = 5.5
MOTOR_CLAMP_PAD_X = 48.0
MOTOR_CLAMP_PAD_Y = 3.0
MOTOR_CLAMP_PAD_Z = 12.0
MOTOR_CLAMP_SCREW_X = 18.0
MOTOR_CLAMP_SCREW_Z = MOTOR_FACE_Z + 8.0
MOTOR_CLAMP_INSERT_DEPTH = 5.2
MOTOR_CLAMP_SOCKET_D = 2.85
MOTOR_CLAMP_SOCKET_DEPTH = 2.2
MOTOR_CLAMP_SCREW_LENGTH = 8.0
MOTOR_CRADLE_SCREW_LENGTH = 10.0

# Motor tower: registered foot, back wall, top shelf, and two side gussets.
TOWER_X0 = 100.0
TOWER_X1 = 178.0
TOWER_Y_HALF = 43.0
TOWER_FOOT_Z0 = BASE_Z
TOWER_FOOT_Z1 = BASE_Z + 8.0
TOWER_BACK_X0 = 166.0
TOWER_SHELF_X0 = 89.0
TOWER_SHELF_Z0 = MOTOR_CRADLE_Z0 - 8.0
TOWER_SHELF_Z1 = MOTOR_CRADLE_Z0
TOWER_SHELF_Y_HALF = 39.0
TOWER_MOUNT_POINTS = (
    (116.0, -36.0),
    (116.0, 36.0),
    (164.0, -36.0),
    (164.0, 36.0),
)

# A stationary copper shoe gives the laser welder's continuity interlock a
# path that does not travel through the polymer bearing or wind a work cable
# around the vessel.  Its PET-GF arm is a replaceable in-plane leaf spring;
# the shoe is cut from the acquired 1/4 inch C110 bar.
GROUND_BASE_POINTS = (
    (-99.5, -60.0),
    (-99.5, -40.0),
)
GROUND_FOOT_X0 = -118.0
GROUND_FOOT_X1 = -96.0
GROUND_FOOT_Y0 = -68.0
GROUND_FOOT_Y1 = -32.0
GROUND_FOOT_Z0 = BASE_Z
GROUND_FOOT_Z1 = BASE_Z + 8.0
GROUND_POST_X0 = -117.0
GROUND_POST_X1 = -103.0
GROUND_POST_Y0 = -66.0
GROUND_POST_Y1 = -34.0
GROUND_TOP_Z = 76.0
GROUND_ARM_H = 10.0
GROUND_ARM_POINTS = (
    (-109.0, -59.0),
    (-109.0, -41.0),
)
GROUND_PAD_X0 = -117.0
GROUND_PAD_X1 = -99.0
GROUND_PAD_Y0 = -65.0
GROUND_PAD_Y1 = -35.0
GROUND_BEAM_X0 = -105.7
GROUND_BEAM_X1 = -103.3
GROUND_BEAM_Y0 = -40.0
GROUND_BEAM_Y1 = 5.0
GROUND_SHOE_BACK_X = -68.85
GROUND_SHOE_FRONT_X = GROUND_SHOE_BACK_X + 6.35
GROUND_SHOE_Y = 20.0
GROUND_SHOE_Z = 30.0
GROUND_SHOE_Z0 = GROUND_TOP_Z - 1.0
GROUND_HOLDER_H = 12.0
GROUND_SHOE_SCREW_D = 3.4
GROUND_SHOE_SCREW_X = -66.0
GROUND_SHOE_SCREW_Z = GROUND_TOP_Z + GROUND_ARM_H / 2.0
GROUND_ARM_SHANK_D = 3.4
GROUND_ARM_INSERT_D = 4.0
GROUND_ARM_INSERT_DEPTH = 5.2
M5_SHANK_D = 5.5
M5_HEAD_D = 9.0
M5_HEAD_DEPTH = 4.5
M5_INSERT_D = 7.0
M5_INSERT_DEPTH = 9.7


def _annulus(outer_r: float, inner_r: float, height: float, z0: float = 0.0):
    return (
        cq.Workplane("XY", origin=(0.0, 0.0, z0))
        .circle(outer_r)
        .circle(inner_r)
        .extrude(height)
    )


def _radial_cylinder(angle: float,
                     radius: float,
                     z: float,
                     diameter: float,
                     depth: float,
                     inward: bool = True):
    theta = math.radians(angle)
    direction = -1.0 if inward else 1.0
    return cq.Workplane(
        obj=cq.Solid.makeCylinder(
            diameter / 2.0,
            depth,
            cq.Vector(radius * math.cos(theta), radius * math.sin(theta), z),
            cq.Vector(direction * math.cos(theta), direction * math.sin(theta), 0.0),
        )
    )


def _vertical_slot(x0: float, x1: float, y: float, diameter: float, z0: float, h: float):
    r = diameter / 2.0
    body = cq.Workplane("XY", origin=(0.0, 0.0, z0)).box(x1 - x0, diameter, h,
                                                                   centered=(True, True, False))
    body = body.translate(((x0 + x1) / 2.0, y, 0.0))
    for x in (x0, x1):
        body = body.union(
            cq.Workplane("XY", origin=(x, y, z0)).circle(r).extrude(h)
        )
    return body


def _sector(outer_r: float, inner_r: float, half_angle: float, height: float, z0: float):
    reach = outer_r + 5.0
    a = math.radians(half_angle)
    wedge = (
        cq.Workplane("XY", origin=(0.0, 0.0, z0))
        .polyline([
            (0.0, 0.0),
            (reach * math.cos(-a), reach * math.sin(-a)),
            (reach * math.cos(a), reach * math.sin(a)),
        ])
        .close()
        .extrude(height)
    )
    return _annulus(outer_r, inner_r, height, z0).intersect(wedge)


def build_base():
    base = (
        cq.Workplane("XY")
        .box(BASE_X, BASE_Y, BASE_Z, centered=(True, True, False))
        .translate((BASE_CENTER_X, 0.0, 0.0))
        .edges("|Z")
        .fillet(BASE_CORNER_R)
    )

    base = base.cut(
        cq.Workplane("XY").circle(HUB_CLEARANCE_D / 2.0).extrude(BASE_Z)
    )
    base = base.cut(
        cq.Workplane("XY")
        .circle(RETAINER_POCKET_D / 2.0)
        .extrude(RETAINER_POCKET_H)
    )
    race = cq.Workplane(
        obj=cq.Solid.makeTorus(
            BALL_RACE_R,
            RACE_CUT_R,
            cq.Vector(0.0, 0.0, BALL_CENTER_Z),
            cq.Vector(0.0, 0.0, 1.0),
        )
    )
    base = base.cut(race)

    bench_points = (
        (BASE_X_MIN + BENCH_HOLE_MARGIN, BASE_Y_MIN + BENCH_HOLE_MARGIN),
        (BASE_X_MIN + BENCH_HOLE_MARGIN, BASE_Y_MAX - BENCH_HOLE_MARGIN),
        (BASE_X_MAX - BENCH_HOLE_MARGIN, BASE_Y_MIN + BENCH_HOLE_MARGIN),
        (BASE_X_MAX - BENCH_HOLE_MARGIN, BASE_Y_MAX - BENCH_HOLE_MARGIN),
    )
    bench_cuts = (
        cq.Workplane("XY")
        .pushPoints(bench_points)
        .circle(BENCH_HOLE_D / 2.0)
        .extrude(BASE_Z)
    )
    base = base.cut(bench_cuts)

    for foot_x, foot_y in BASE_FOOT_CENTERS:
        for dx in (-BASE_FOOT_SCREW_X, BASE_FOOT_SCREW_X):
            x = foot_x + dx
            shank = (
                cq.Workplane("XY", origin=(x, foot_y, 0.0))
                .circle(NEST_SCREW_D / 2.0)
                .extrude(BASE_Z)
            )
            head = (
                cq.Workplane(
                    "XY", origin=(x, foot_y, BASE_Z - M3_HEAD_DEPTH)
                )
                .circle(M3_HEAD_D / 2.0)
                .extrude(M3_HEAD_DEPTH + 0.01)
            )
            base = base.cut(shank.union(head))

    for x, y in TOWER_MOUNT_POINTS + GROUND_BASE_POINTS:
        pocket = (
            cq.Workplane("XY", origin=(x, y, BASE_Z - M5_INSERT_DEPTH))
            .circle(M5_INSERT_D / 2.0)
            .extrude(M5_INSERT_DEPTH + 0.01)
        )
        base = base.cut(pocket)
    return base


def build_base_foot():
    foot = (
        cq.Workplane("XY")
        .box(BASE_FOOT_X, BASE_FOOT_Y, BASE_FOOT_H,
             centered=(True, True, False))
        .edges("|Z")
        .fillet(4.0)
    )
    for x in (-BASE_FOOT_SCREW_X, BASE_FOOT_SCREW_X):
        through = (
            cq.Workplane("XY", origin=(x, 0.0, 0.0))
            .circle(NEST_SCREW_D / 2.0)
            .extrude(BASE_FOOT_H)
        )
        insert = (
            cq.Workplane(
                "XY",
                origin=(x, 0.0, BASE_FOOT_H - BASE_FOOT_INSERT_DEPTH),
            )
            .circle(BASE_FOOT_INSERT_D / 2.0)
            .extrude(BASE_FOOT_INSERT_DEPTH + 0.01)
        )
        foot = foot.cut(through.union(insert))
    return foot


def _pulley_grooves():
    groove = (
        cq.Workplane("XY", origin=(0.0, 0.0, PULLEY_TOOTH_Z0))
        .polyline([
            (PULLEY_TIP_R + 0.8, -GROOVE_OUTER_HALF_W),
            (PULLEY_ROOT_R - 0.15, -GROOVE_ROOT_HALF_W),
            (PULLEY_ROOT_R - 0.15, GROOVE_ROOT_HALF_W),
            (PULLEY_TIP_R + 0.8, GROOVE_OUTER_HALF_W),
        ])
        .close()
        .extrude(PULLEY_TOOTH_H)
    )
    solids = []
    for tooth in range(interface.TABLE_PULLEY_TEETH):
        solids.append(
            groove.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0),
                          tooth * 360.0 / interface.TABLE_PULLEY_TEETH).val()
        )
    return cq.Workplane(obj=cq.Compound.makeCompound(solids))


def build_turntable():
    platter = (
        cq.Workplane("XY", origin=(0.0, 0.0, PLATTER_Z0))
        .circle(PLATTER_R)
        .extrude(PLATTER_Z1 - PLATTER_Z0)
    )
    hub = _annulus(HUB_OD / 2.0, SERVICE_BORE_D / 2.0,
                   PLATTER_Z1 - HUB_Z0, HUB_Z0)
    turntable = platter.union(hub)

    race = cq.Workplane(
        obj=cq.Solid.makeTorus(
            BALL_RACE_R,
            RACE_CUT_R,
            cq.Vector(0.0, 0.0, BALL_CENTER_Z),
            cq.Vector(0.0, 0.0, 1.0),
        )
    )
    turntable = turntable.cut(race)

    pedestal = _annulus(PEDESTAL_R, SERVICE_BORE_D / 2.0,
                        NEST_SEAT_Z - PLATTER_Z1, PLATTER_Z1)
    pulley = _annulus(PULLEY_TIP_R, PULLEY_INNER_R,
                      PULLEY_Z1 - PULLEY_Z0, PULLEY_Z0)
    pulley = pulley.cut(_pulley_grooves())
    lower_flange = _annulus(PULLEY_FLANGE_R, PULLEY_INNER_R,
                            PULLEY_FLANGE_H, PULLEY_Z0)
    upper_flange = _annulus(PULLEY_FLANGE_R, PULLEY_INNER_R,
                            PULLEY_FLANGE_H, PULLEY_Z1 - PULLEY_FLANGE_H)
    turntable = turntable.union(pedestal).union(pulley).union(lower_flange).union(upper_flange)

    register = _annulus(REGISTER_OD / 2.0, SERVICE_BORE_D / 2.0,
                        REGISTER_H, NEST_SEAT_Z)
    turntable = turntable.union(register)

    for angle in (0.0, 120.0, 240.0):
        theta = math.radians(angle)
        x = NEST_SCREW_R * math.cos(theta)
        y = NEST_SCREW_R * math.sin(theta)
        pocket = (
            cq.Workplane("XY", origin=(x, y, NEST_SEAT_Z - NEST_INSERT_DEPTH))
            .circle(NEST_INSERT_D / 2.0)
            .extrude(NEST_INSERT_DEPTH + 0.01)
        )
        turntable = turntable.cut(pocket)

    for angle in (60.0, 180.0, 300.0):
        theta = math.radians(angle)
        x = RETAINER_SCREW_R * math.cos(theta)
        y = RETAINER_SCREW_R * math.sin(theta)
        retainer_pocket = (
            cq.Workplane("XY", origin=(x, y, HUB_Z0))
            .circle(NEST_INSERT_D / 2.0)
            .extrude(RETAINER_INSERT_DEPTH)
        )
        turntable = turntable.cut(retainer_pocket)
    return turntable


def build_pulley_coupon():
    pulley = _annulus(PULLEY_TIP_R, PULLEY_INNER_R,
                      PULLEY_Z1 - PULLEY_Z0, PULLEY_Z0)
    pulley = pulley.cut(_pulley_grooves())
    pulley = pulley.union(
        _annulus(PULLEY_FLANGE_R, PULLEY_INNER_R,
                 PULLEY_FLANGE_H, PULLEY_Z0)
    )
    pulley = pulley.union(
        _annulus(PULLEY_FLANGE_R, PULLEY_INNER_R,
                 PULLEY_FLANGE_H, PULLEY_Z1 - PULLEY_FLANGE_H)
    )
    half_angle = COUPON_TEETH * 360.0 / interface.TABLE_PULLEY_TEETH / 2.0
    coupon = pulley.intersect(
        _sector(PULLEY_FLANGE_R + 1.0, PULLEY_INNER_R - 1.0,
                half_angle, PULLEY_Z1 - PULLEY_Z0, PULLEY_Z0)
    )
    return coupon.translate((0.0, 0.0, -PULLEY_Z0))


def build_cage():
    cage = _annulus(CAGE_OUTER_R, CAGE_INNER_R, CAGE_H, CAGE_Z)
    points = [
        (
            BALL_RACE_R * math.cos(2.0 * math.pi * i / BALL_COUNT),
            BALL_RACE_R * math.sin(2.0 * math.pi * i / BALL_COUNT),
        )
        for i in range(BALL_COUNT)
    ]
    pockets = (
        cq.Workplane("XY", origin=(0.0, 0.0, CAGE_Z))
        .pushPoints(points)
        .circle(CAGE_POCKET_D / 2.0)
        .extrude(CAGE_H)
    )
    return cage.cut(pockets)


def build_retainer():
    retainer = _annulus(RETAINER_OD / 2.0, SERVICE_BORE_D / 2.0, RETAINER_H)
    for angle in (60.0, 180.0, 300.0):
        theta = math.radians(angle)
        x = RETAINER_SCREW_R * math.cos(theta)
        y = RETAINER_SCREW_R * math.sin(theta)
        boss = (
            cq.Workplane("XY", origin=(x, y, RETAINER_H))
            .circle(RETAINER_BOSS_R)
            .extrude(RETAINER_BOSS_H)
        )
        retainer = retainer.union(boss)
        hole = (
            cq.Workplane("XY", origin=(x, y, 0.0))
            .circle(NEST_SCREW_D / 2.0)
            .extrude(RETAINER_H + RETAINER_BOSS_H)
        )
        head = (
            cq.Workplane("XY", origin=(x, y, 0.0))
            .circle(M3_HEAD_D / 2.0)
            .extrude(M3_HEAD_DEPTH)
        )
        retainer = retainer.cut(hole.union(head))
    return retainer


def build_nest():
    base = _annulus(NEST_OD / 2.0, NEST_CENTER_BORE_D / 2.0, NEST_BASE_H)
    register_socket = _annulus(
        (REGISTER_OD + REGISTER_SLIP) / 2.0,
        NEST_CENTER_BORE_D / 2.0,
        REGISTER_H + 0.2,
    )
    base = base.cut(register_socket)

    pilot = _annulus(PILOT_OD / 2.0, PILOT_ID / 2.0, PILOT_H, NEST_BASE_H)
    outer = _annulus(
        OUTER_COLLAR_OD / 2.0,
        OUTER_BORE_D / 2.0,
        NEST_OUTER_H,
        NEST_BASE_H,
    )
    nest = base.union(pilot).union(outer)

    guide = _sector(
        JAW_GUIDE_OUTER_R + JAW_GUIDE_SLIP,
        JAW_GUIDE_INNER_R - JAW_GUIDE_SLIP,
        JAW_HALF_ANGLE + 0.4,
        JAW_H + 0.4,
        JAW_Z0 - 0.2,
    )
    for angle in (0.0, 120.0, 240.0):
        nest = nest.cut(
            guide.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), angle)
        )
        nest = nest.cut(
            _radial_cylinder(
                angle,
                OUTER_COLLAR_OD / 2.0 + 0.1,
                JAW_SCREW_Z,
                JAW_INSERT_D,
                JAW_INSERT_DEPTH + 0.2,
            )
        )
        nest = nest.cut(
            _radial_cylinder(
                angle,
                OUTER_COLLAR_OD / 2.0 - JAW_INSERT_DEPTH,
                JAW_SCREW_Z,
                JAW_SHANK_D,
                OUTER_COLLAR_OD / 2.0 - JAW_INSERT_DEPTH - JAW_GUIDE_OUTER_R + 0.4,
            )
        )

    for angle in (0.0, 120.0, 240.0):
        theta = math.radians(angle)
        x = NEST_SCREW_R * math.cos(theta)
        y = NEST_SCREW_R * math.sin(theta)
        shank = (
            cq.Workplane("XY", origin=(x, y, 0.0))
            .circle(NEST_SCREW_D / 2.0)
            .extrude(NEST_BASE_H)
        )
        counterbore = (
            cq.Workplane("XY", origin=(x, y, NEST_BASE_H - M3_HEAD_DEPTH))
            .circle(M3_HEAD_D / 2.0)
            .extrude(M3_HEAD_DEPTH)
        )
        nest = nest.cut(shank.union(counterbore))
    return nest


def build_jaw():
    jaw = _sector(
        JAW_GUIDE_OUTER_R,
        JAW_GUIDE_INNER_R,
        JAW_HALF_ANGLE,
        JAW_H,
        0.0,
    )
    socket = _radial_cylinder(
        0.0,
        JAW_GUIDE_OUTER_R + 0.01,
        JAW_H / 2.0,
        JAW_SOCKET_D,
        JAW_SOCKET_DEPTH,
    )
    return jaw.cut(socket)


def _gusset(y0: float, direction: float):
    profile = (
        cq.Workplane("XZ", origin=(0.0, y0, 0.0))
        .polyline([
            (TOWER_SHELF_X0 + 10.0, TOWER_SHELF_Z0),
            (TOWER_X1, TOWER_FOOT_Z1),
            (TOWER_X1, TOWER_SHELF_Z0),
        ])
        .close()
        .extrude(direction * 6.0)
    )
    return profile


def build_motor_tower():
    foot = (
        cq.Workplane("XY", origin=((TOWER_X0 + TOWER_X1) / 2.0, 0.0, TOWER_FOOT_Z0))
        .box(TOWER_X1 - TOWER_X0, 2.0 * TOWER_Y_HALF,
             TOWER_FOOT_Z1 - TOWER_FOOT_Z0, centered=(True, True, False))
    )
    back = (
        cq.Workplane("XY", origin=((TOWER_BACK_X0 + TOWER_X1) / 2.0, 0.0, TOWER_FOOT_Z1))
        .box(TOWER_X1 - TOWER_BACK_X0, 2.0 * TOWER_Y_HALF,
             TOWER_SHELF_Z1 - TOWER_FOOT_Z1, centered=(True, True, False))
    )
    shelf = (
        cq.Workplane("XY", origin=((TOWER_SHELF_X0 + TOWER_X1) / 2.0, 0.0, TOWER_SHELF_Z0))
        .box(TOWER_X1 - TOWER_SHELF_X0, 2.0 * TOWER_SHELF_Y_HALF,
             TOWER_SHELF_Z1 - TOWER_SHELF_Z0, centered=(True, True, False))
    )
    tower = foot.union(back).union(shelf)
    tower = tower.union(_gusset(-TOWER_SHELF_Y_HALF, +1.0))
    tower = tower.union(_gusset(TOWER_SHELF_Y_HALF, -1.0))

    shaft_slot = _vertical_slot(
        MOTOR_CENTER_MIN,
        MOTOR_CENTER_MAX,
        0.0,
        MOTOR_PULLEY_FLANGE_D + 2.0,
        TOWER_SHELF_Z0,
        TOWER_SHELF_Z1 - TOWER_SHELF_Z0,
    )
    tower = tower.cut(shaft_slot)

    mount_offset = MOTOR_CRADLE_BOLT_SQUARE / 2.0
    for y in (-mount_offset, mount_offset):
        for x_sign in (-1.0, 1.0):
            x0 = MOTOR_CENTER_MIN + x_sign * mount_offset
            x1 = MOTOR_CENTER_MAX + x_sign * mount_offset
            tower = tower.cut(
                _vertical_slot(
                    min(x0, x1), max(x0, x1), y,
                    2.0 * MOTOR_SLOT_R,
                    TOWER_SHELF_Z0,
                    TOWER_SHELF_Z1 - TOWER_SHELF_Z0,
                )
            )
            tower = tower.cut(
                _vertical_slot(
                    min(x0, x1), max(x0, x1), y,
                    M3_HEAD_D,
                    TOWER_SHELF_Z0,
                    M3_HEAD_DEPTH,
                )
            )

    for x, y in TOWER_MOUNT_POINTS:
        shank = (
            cq.Workplane("XY", origin=(x, y, TOWER_FOOT_Z0))
            .circle(M5_SHANK_D / 2.0)
            .extrude(TOWER_FOOT_Z1 - TOWER_FOOT_Z0)
        )
        head = (
            cq.Workplane("XY", origin=(x, y, TOWER_FOOT_Z1 - M5_HEAD_DEPTH))
            .circle(M5_HEAD_D / 2.0)
            .extrude(M5_HEAD_DEPTH)
        )
        tower = tower.cut(shank.union(head))
    return tower


def build_motor_cradle():
    center = MOTOR_CENTER_NOMINAL
    base = (
        cq.Workplane("XY", origin=(center, 0.0, MOTOR_CRADLE_Z0))
        .box(MOTOR_CRADLE_X, MOTOR_CRADLE_Y, MOTOR_CRADLE_BASE_H,
             centered=(True, True, False))
    )
    pilot_clearance = (
        cq.Workplane("XY", origin=(center, 0.0, MOTOR_CRADLE_Z0))
        .circle(MOTOR_CRADLE_PILOT_D / 2.0)
        .extrude(MOTOR_CRADLE_BASE_H + 0.01)
    )
    cradle = base.cut(pilot_clearance)

    wall_outer = (
        cq.Workplane("XY", origin=(center, 0.0, MOTOR_FACE_Z))
        .box(MOTOR_CRADLE_X, MOTOR_CRADLE_Y, MOTOR_CRADLE_WALL_H,
             centered=(True, True, False))
    )
    wall_inner = (
        cq.Workplane("XY", origin=(center, 0.0, MOTOR_FACE_Z))
        .box(MOTOR_CRADLE_INNER_X, MOTOR_CRADLE_INNER_Y,
             MOTOR_CRADLE_WALL_H + 0.01, centered=(True, True, False))
    )
    cradle = cradle.union(wall_outer.cut(wall_inner))

    mount_offset = MOTOR_CRADLE_BOLT_SQUARE / 2.0
    for x_sign in (-1.0, 1.0):
        for y_sign in (-1.0, 1.0):
            pocket = (
                cq.Workplane(
                    "XY",
                    origin=(center + x_sign * mount_offset,
                            y_sign * mount_offset,
                            MOTOR_CRADLE_Z0),
                )
                .circle(NEST_INSERT_D / 2.0)
                .extrude(MOTOR_CRADLE_INSERT_DEPTH)
            )
            cradle = cradle.cut(pocket)

    side_wall = (MOTOR_CRADLE_Y - MOTOR_CRADLE_INNER_Y) / 2.0
    for y_sign in (-1.0, 1.0):
        direction = cq.Vector(0.0, -y_sign, 0.0)
        y_outer = y_sign * MOTOR_CRADLE_Y / 2.0
        for x_offset in (-MOTOR_CLAMP_SCREW_X, MOTOR_CLAMP_SCREW_X):
            origin = cq.Vector(center + x_offset, y_outer, MOTOR_CLAMP_SCREW_Z)
            shank = cq.Workplane(
                obj=cq.Solid.makeCylinder(
                    JAW_SHANK_D / 2.0,
                    side_wall + 0.01,
                    origin,
                    direction,
                )
            )
            insert = cq.Workplane(
                obj=cq.Solid.makeCylinder(
                    NEST_INSERT_D / 2.0,
                    MOTOR_CLAMP_INSERT_DEPTH,
                    origin,
                    direction,
                )
            )
            cradle = cradle.cut(shank.union(insert))
    return cradle


def build_motor_clamp_pad():
    pad = (
        cq.Workplane("XY")
        .box(MOTOR_CLAMP_PAD_X, MOTOR_CLAMP_PAD_Y, MOTOR_CLAMP_PAD_Z,
             centered=(True, True, False))
    )
    for x in (-MOTOR_CLAMP_SCREW_X, MOTOR_CLAMP_SCREW_X):
        socket = cq.Workplane(
            obj=cq.Solid.makeCylinder(
                MOTOR_CLAMP_SOCKET_D / 2.0,
                MOTOR_CLAMP_SOCKET_DEPTH,
                cq.Vector(x, -MOTOR_CLAMP_PAD_Y / 2.0, MOTOR_CLAMP_PAD_Z / 2.0),
                cq.Vector(0.0, 1.0, 0.0),
            )
        )
        pad = pad.cut(socket)
    return pad


def build_ground_tower():
    foot = (
        cq.Workplane("XY", origin=((GROUND_FOOT_X0 + GROUND_FOOT_X1) / 2.0,
                                    (GROUND_FOOT_Y0 + GROUND_FOOT_Y1) / 2.0,
                                    GROUND_FOOT_Z0))
        .box(GROUND_FOOT_X1 - GROUND_FOOT_X0,
             GROUND_FOOT_Y1 - GROUND_FOOT_Y0,
             GROUND_FOOT_Z1 - GROUND_FOOT_Z0,
             centered=(True, True, False))
    )
    post = (
        cq.Workplane("XY", origin=((GROUND_POST_X0 + GROUND_POST_X1) / 2.0,
                                    (GROUND_POST_Y0 + GROUND_POST_Y1) / 2.0,
                                    GROUND_FOOT_Z1))
        .box(GROUND_POST_X1 - GROUND_POST_X0,
             GROUND_POST_Y1 - GROUND_POST_Y0,
             GROUND_TOP_Z - GROUND_FOOT_Z1,
             centered=(True, True, False))
    )
    tower = foot.union(post)

    for x, y in GROUND_BASE_POINTS:
        shank = (
            cq.Workplane("XY", origin=(x, y, GROUND_FOOT_Z0))
            .circle(M5_SHANK_D / 2.0)
            .extrude(GROUND_FOOT_Z1 - GROUND_FOOT_Z0)
        )
        head = (
            cq.Workplane("XY", origin=(x, y, GROUND_FOOT_Z1 - M5_HEAD_DEPTH))
            .circle(M5_HEAD_D / 2.0)
            .extrude(M5_HEAD_DEPTH)
        )
        tower = tower.cut(shank.union(head))

    for x, y in GROUND_ARM_POINTS:
        pocket = (
            cq.Workplane("XY", origin=(x, y, GROUND_TOP_Z - GROUND_ARM_INSERT_DEPTH))
            .circle(GROUND_ARM_INSERT_D / 2.0)
            .extrude(GROUND_ARM_INSERT_DEPTH + 0.01)
        )
        tower = tower.cut(pocket)
    return tower


def build_ground_arm():
    pad = (
        cq.Workplane("XY", origin=((GROUND_PAD_X0 + GROUND_PAD_X1) / 2.0,
                                    (GROUND_PAD_Y0 + GROUND_PAD_Y1) / 2.0,
                                    GROUND_TOP_Z))
        .box(GROUND_PAD_X1 - GROUND_PAD_X0,
             GROUND_PAD_Y1 - GROUND_PAD_Y0,
             GROUND_ARM_H,
             centered=(True, True, False))
    )
    beam = (
        cq.Workplane("XY", origin=((GROUND_BEAM_X0 + GROUND_BEAM_X1) / 2.0,
                                    (GROUND_BEAM_Y0 + GROUND_BEAM_Y1) / 2.0,
                                    GROUND_TOP_Z))
        .box(GROUND_BEAM_X1 - GROUND_BEAM_X0,
             GROUND_BEAM_Y1 - GROUND_BEAM_Y0,
             GROUND_ARM_H,
             centered=(True, True, False))
    )
    nose = (
        cq.Workplane("XY", origin=((GROUND_BEAM_X0 + GROUND_SHOE_BACK_X) / 2.0,
                                    0.0,
                                    GROUND_TOP_Z))
        .box(GROUND_SHOE_BACK_X - GROUND_BEAM_X0,
             10.0,
             GROUND_ARM_H,
             centered=(True, True, False))
    )
    back = (
        cq.Workplane("XY", origin=(-70.4, 0.0, GROUND_SHOE_Z0))
        .box(3.1, GROUND_SHOE_Y + 6.0, GROUND_HOLDER_H,
             centered=(True, True, False))
    )
    side_lugs = (
        cq.Workplane("XY", origin=((GROUND_SHOE_BACK_X - 64.0) / 2.0,
                                    -(GROUND_SHOE_Y / 2.0 + 1.5),
                                    GROUND_SHOE_Z0))
        .box(-64.0 - GROUND_SHOE_BACK_X, 3.0, GROUND_HOLDER_H,
             centered=(True, True, False))
    ).union(
        cq.Workplane("XY", origin=((GROUND_SHOE_BACK_X - 64.0) / 2.0,
                                    GROUND_SHOE_Y / 2.0 + 1.5,
                                    GROUND_SHOE_Z0))
        .box(-64.0 - GROUND_SHOE_BACK_X, 3.0, GROUND_HOLDER_H,
             centered=(True, True, False))
    )
    arm = pad.union(beam).union(nose).union(back).union(side_lugs)

    for x, y in GROUND_ARM_POINTS:
        hole = (
            cq.Workplane("XY", origin=(x, y, GROUND_TOP_Z))
            .circle(GROUND_ARM_SHANK_D / 2.0)
            .extrude(GROUND_ARM_H)
        )
        head = (
            cq.Workplane(
                "XY",
                origin=(x, y, GROUND_TOP_Z + GROUND_ARM_H - M3_HEAD_DEPTH),
            )
            .circle(M3_HEAD_D / 2.0)
            .extrude(M3_HEAD_DEPTH)
        )
        arm = arm.cut(hole.union(head))

    shoe_screw = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            GROUND_SHOE_SCREW_D / 2.0,
            7.0,
            cq.Vector(GROUND_SHOE_SCREW_X,
                      -GROUND_SHOE_Y / 2.0 - 3.0,
                      GROUND_SHOE_SCREW_Z),
            cq.Vector(0.0, 1.0, 0.0),
        )
    )
    return arm.cut(shoe_screw)


def build_ground_shoe_proxy():
    return (
        cq.Workplane("XY", origin=((GROUND_SHOE_BACK_X + GROUND_SHOE_FRONT_X) / 2.0,
                                    0.0,
                                    GROUND_SHOE_Z0))
        .box(GROUND_SHOE_FRONT_X - GROUND_SHOE_BACK_X,
             GROUND_SHOE_Y,
             GROUND_SHOE_Z,
             centered=(True, True, False))
    )


def build_motor_proxy():
    center = MOTOR_CENTER_NOMINAL
    body = (
        cq.Workplane("XY", origin=(center, 0.0, MOTOR_FACE_Z))
        .box(interface.MOTOR_FRAME, interface.MOTOR_FRAME,
             interface.MOTOR_BODY_LENGTH, centered=(True, True, False))
    )
    pilot = (
        cq.Workplane(
            "XY",
            origin=(center, 0.0, MOTOR_FACE_Z - interface.MOTOR_PILOT_LENGTH),
        )
        .circle(interface.MOTOR_PILOT_DIAMETER / 2.0)
        .extrude(interface.MOTOR_PILOT_LENGTH)
    )
    shaft = (
        cq.Workplane("XY", origin=(center, 0.0, MOTOR_FACE_Z - interface.MOTOR_SHAFT_LENGTH))
        .circle(interface.MOTOR_SHAFT_DIAMETER / 2.0)
        .extrude(interface.MOTOR_SHAFT_LENGTH)
    )
    return body.union(pilot).union(shaft)


def build_motor_pulley_proxy():
    center = MOTOR_CENTER_NOMINAL
    core = (
        cq.Workplane("XY", origin=(center, 0.0, MOTOR_PULLEY_Z0 + 1.0))
        .circle(MOTOR_PULLEY_CORE_D / 2.0)
        .circle(interface.MOTOR_SHAFT_DIAMETER / 2.0)
        .extrude(MOTOR_PULLEY_Z1 - MOTOR_PULLEY_Z0 - 2.0)
    )
    flanges = []
    for z in (MOTOR_PULLEY_Z0, MOTOR_PULLEY_Z1 - 1.0):
        flanges.append(
            cq.Workplane("XY", origin=(center, 0.0, z))
            .circle(MOTOR_PULLEY_FLANGE_D / 2.0)
            .circle(interface.MOTOR_SHAFT_DIAMETER / 2.0)
            .extrude(1.0)
        )
    return core.union(flanges[0]).union(flanges[1])


def build_tube_proxy():
    return (
        cq.Workplane("XY", origin=(0.0, 0.0, NEST_SEAT_Z + NEST_BASE_H))
        .circle(interface.TUBE_OD / 2.0)
        .circle(interface.TUBE_ID / 2.0)
        .extrude(interface.TUBE_LENGTH)
    )


def build_balls_proxy():
    balls = []
    for i in range(BALL_COUNT):
        a = 2.0 * math.pi * i / BALL_COUNT
        balls.append(
            cq.Workplane("XY")
            .sphere(BALL_D / 2.0)
            .translate((BALL_RACE_R * math.cos(a),
                        BALL_RACE_R * math.sin(a),
                        BALL_CENTER_Z))
            .val()
        )
    return cq.Workplane(obj=cq.Compound.makeCompound(balls))


def _valid(name: str, part):
    value = part.val()
    if not value.isValid():
        raise ValueError(f"{name} is not a valid solid")
    if value.Volume() <= 0.0:
        raise ValueError(f"{name} has no volume")


def selftest():
    parts = {
        "base": build_base(),
        "base-foot": build_base_foot(),
        "turntable": build_turntable(),
        "pulley-coupon": build_pulley_coupon(),
        "ball-cage": build_cage(),
        "retainer": build_retainer(),
        "tube-nest": build_nest(),
        "jaw-cap": build_jaw(),
        "motor-tower": build_motor_tower(),
        "motor-cradle": build_motor_cradle(),
        "motor-clamp-pad": build_motor_clamp_pad(),
        "ground-tower": build_ground_tower(),
        "ground-arm": build_ground_arm(),
        "ground-shoe": build_ground_shoe_proxy(),
    }
    for name, part in parts.items():
        _valid(name, part)

    base_bb = parts["base"].val().BoundingBox()
    if base_bb.xlen > 325.0 or base_bb.ylen > 320.0:
        raise ValueError("base exceeds the H2C left-nozzle build envelope")

    service_radius_needed = (
        interface.ENDCAP_PORT_OFFSET
        + interface.ENDCAP_SERVICE_ENVELOPE / 2.0
    )
    service_margin = SERVICE_BORE_D / 2.0 - service_radius_needed
    if service_margin < 10.0:
        raise ValueError(
            f"end-cap port service margin is only {service_margin:.2f} mm"
        )
    if SERVICE_BORE_D >= PILOT_ID:
        raise ValueError("service passage removes the tube nest's pilot support")
    if RETAINER_POCKET_D / 2.0 + 10.0 >= BALL_RACE_R - RACE_CUT_R:
        raise ValueError("retainer pocket leaves too little base web inside the race")

    foot_thread_reach = (
        BASE_FOOT_SCREW_LENGTH - (BASE_Z - M3_HEAD_DEPTH)
    )
    if foot_thread_reach < BASE_FOOT_INSERT_DEPTH:
        raise ValueError("M3 x 25 foot screws do not fully engage their inserts")
    if foot_thread_reach >= BASE_FOOT_H:
        raise ValueError("M3 x 25 foot screws project below the feet")
    for foot_x, foot_y in BASE_FOOT_CENTERS:
        if not (
            BASE_X_MIN <= foot_x - BASE_FOOT_X / 2.0
            and foot_x + BASE_FOOT_X / 2.0 <= BASE_X_MAX
            and BASE_Y_MIN <= foot_y - BASE_FOOT_Y / 2.0
            and foot_y + BASE_FOOT_Y / 2.0 <= BASE_Y_MAX
        ):
            raise ValueError("a base foot falls outside the stationary base")

    motor_clearance = (
        MOTOR_CENTER_MIN - interface.MOTOR_FRAME / 2.0 - PLATTER_R
    )
    if motor_clearance < 0.5:
        raise ValueError(f"motor-to-platter clearance is only {motor_clearance:.2f} mm")

    ball_pitch = 2.0 * math.pi * BALL_RACE_R / BALL_COUNT
    if ball_pitch < CAGE_POCKET_D + 2.0:
        raise ValueError("ball cage leaves less than 2 mm between pockets")

    pilot_radial_clearance = (interface.TUBE_ID - PILOT_OD) / 2.0
    outer_radial_clearance = (OUTER_BORE_D - interface.TUBE_OD) / 2.0
    if pilot_radial_clearance <= 0.0 or outer_radial_clearance <= 0.0:
        raise ValueError("tube nest nominal clearances are not positive")
    if PILOT_H >= interface.ENDCAP_RECESS:
        raise ValueError("ID pilot reaches a welded end-cap plate")

    retainer_z = HUB_Z0 - RETAINER_GAP - RETAINER_H
    retainer_running_gap = RETAINER_POCKET_H - (retainer_z + RETAINER_H)
    if retainer_z < 0.0:
        raise ValueError("underside retainer projects below the base")
    if abs(retainer_running_gap - RETAINER_GAP) > 1e-6:
        raise ValueError("underside retainer does not preserve its running gap")
    if abs(retainer_z + RETAINER_H + RETAINER_BOSS_H - HUB_Z0) > 1e-6:
        raise ValueError("retainer standoff bosses do not meet the hub")
    retainer_grip = RETAINER_H + RETAINER_BOSS_H - M3_HEAD_DEPTH
    retainer_thread_reach = 8.0 - retainer_grip
    if RETAINER_INSERT_DEPTH < retainer_thread_reach + 0.2:
        raise ValueError("M3 x 8 retainer screws bottom in the hub insert pilots")

    cradle_pilot_radial = (
        MOTOR_CRADLE_PILOT_D - interface.MOTOR_PILOT_DIAMETER
    ) / 2.0
    if not 0.15 <= cradle_pilot_radial <= 0.40:
        raise ValueError("motor cradle does not positively locate the face pilot")
    if MOTOR_CRADLE_INNER_X < interface.MOTOR_FRAME + 0.5:
        raise ValueError("motor cradle X pocket lacks frame clearance")
    clamp_travel = (
        MOTOR_CRADLE_INNER_Y
        - interface.MOTOR_FRAME
        - 2.0 * MOTOR_CLAMP_PAD_Y
    ) / 2.0
    screw_projection = MOTOR_CLAMP_SCREW_LENGTH - MOTOR_CLAMP_INSERT_DEPTH
    if clamp_travel < 0.2 or screw_projection < clamp_travel + 0.5:
        raise ValueError("motor side pads cannot take up the frame clearance")
    shelf_grip = (
        TOWER_SHELF_Z1 - TOWER_SHELF_Z0 - M3_HEAD_DEPTH
    )
    cradle_thread_reach = MOTOR_CRADLE_SCREW_LENGTH - shelf_grip
    if not 3.0 <= cradle_thread_reach <= MOTOR_CRADLE_INSERT_DEPTH:
        raise ValueError("motor cradle screws have invalid insert engagement")

    cradle_to_nest = (
        MOTOR_CENTER_MIN - MOTOR_CRADLE_X / 2.0 - NEST_OD / 2.0
    )
    if cradle_to_nest < 5.0:
        raise ValueError("motor cradle approaches the tube nest too closely")
    if parts["motor-cradle"].intersect(parts["turntable"]).val().Volume() > 1e-4:
        raise ValueError("motor cradle intersects the turntable")
    motor_proxy = build_motor_proxy()
    pulley_proxy = build_motor_pulley_proxy()
    for fixed_name, fixed_part in (
        ("motor cradle", parts["motor-cradle"]),
        ("motor tower", parts["motor-tower"]),
    ):
        if fixed_part.intersect(motor_proxy).val().Volume() > 1e-4:
            raise ValueError(f"{fixed_name} intersects the purchased motor")
        if fixed_part.intersect(pulley_proxy).val().Volume() > 1e-4:
            raise ValueError(f"{fixed_name} intersects the purchased 20T pulley")

    ground_preload = GROUND_SHOE_FRONT_X + interface.TUBE_OD / 2.0
    if not 0.5 <= ground_preload <= 2.0:
        raise ValueError(f"ground shoe preload is {ground_preload:.2f} mm")
    if GROUND_FOOT_X0 < BASE_X_MIN or GROUND_FOOT_Y0 < BASE_Y_MIN:
        raise ValueError("ground tower falls outside the stationary base")

    if not (MOTOR_CENTER_MIN <= interface.belt_center_distance() <= MOTOR_CENTER_MAX):
        raise ValueError("purchased belt centre does not fall inside the motor slots")
    if interface.small_pulley_wrap_degrees() < 120.0:
        raise ValueError("small pulley wrap is below seven 5M teeth")
    return parts


def _assembly(parts):
    assembly = cq.Assembly(name="weld-rotator")
    for index, (x, y) in enumerate(BASE_FOOT_CENTERS):
        assembly.add(
            parts["base-foot"],
            name=f"base-foot-{index + 1}",
            color=M_PETGF_BLACK,
            loc=cq.Location(cq.Vector(x, y, -BASE_FOOT_H)),
        )
    assembly.add(parts["base"], name="stationary-base", color=M_PETGF_BLACK)
    assembly.add(parts["motor-tower"], name="motor-tower", color=M_PETGF_BLACK)
    assembly.add(parts["motor-cradle"], name="motor-cradle", color=M_PETGF_BLACK)
    pad_y = interface.MOTOR_FRAME / 2.0 + MOTOR_CLAMP_PAD_Y / 2.0
    assembly.add(
        parts["motor-clamp-pad"],
        name="motor-clamp-pad-negative-y",
        color=M_PETGF_BLACK,
        loc=cq.Location(cq.Vector(MOTOR_CENTER_NOMINAL, -pad_y, MOTOR_FACE_Z + 2.0)),
    )
    assembly.add(
        parts["motor-clamp-pad"],
        name="motor-clamp-pad-positive-y",
        color=M_PETGF_BLACK,
        loc=cq.Location(cq.Vector(MOTOR_CENTER_NOMINAL, pad_y, MOTOR_FACE_Z + 2.0),
                        cq.Vector(0.0, 0.0, 1.0), 180.0),
    )
    assembly.add(parts["ground-tower"], name="ground-tower", color=M_PETGF_BLACK)
    assembly.add(parts["ground-arm"], name="ground-flexure-arm", color=M_PETGF_BLACK)
    assembly.add(parts["ground-shoe"], name="c110-ground-shoe", color=M_COPPER)
    assembly.add(parts["turntable"], name="turntable-90t", color=M_PETGF_BLACK)
    assembly.add(parts["ball-cage"], name="ball-cage", color=M_PETGF_BLACK)
    assembly.add(
        parts["retainer"],
        name="turntable-retainer",
        color=M_PETGF_BLACK,
        loc=cq.Location(cq.Vector(0.0, 0.0, HUB_Z0 - RETAINER_GAP - RETAINER_H)),
    )
    assembly.add(
        parts["tube-nest"],
        name="tube-nest",
        color=M_PETGF_BLACK,
        loc=cq.Location(cq.Vector(0.0, 0.0, NEST_SEAT_Z)),
    )
    for index, angle in enumerate((0.0, 120.0, 240.0)):
        assembly.add(
            parts["jaw-cap"],
            name=f"jaw-cap-{index + 1}",
            color=M_PETGF_BLACK,
            loc=cq.Location(cq.Vector(0.0, 0.0, NEST_SEAT_Z + JAW_Z0),
                            cq.Vector(0.0, 0.0, 1.0), angle),
        )
    assembly.add(build_balls_proxy(), name="10mm-pp-balls", color=M_TPU_BLACK)
    assembly.add(build_motor_proxy(), name="23hs30-2804s", color=M_STAINLESS)
    assembly.add(build_motor_pulley_proxy(), name="20t-htd5m-pulley", color=M_ALUMINIUM)
    assembly.add(build_tube_proxy(), name="5in-316l-tube", color=M_STAINLESS)
    return assembly


def main():
    parts = selftest()
    outputs = {
        "base": "weld-rotator-base.step",
        "base-foot": "weld-rotator-base-foot.step",
        "turntable": "weld-rotator-turntable-90t.step",
        "pulley-coupon": "weld-rotator-pulley-coupon.step",
        "ball-cage": "weld-rotator-ball-cage.step",
        "retainer": "weld-rotator-retainer.step",
        "tube-nest": "weld-rotator-tube-nest.step",
        "jaw-cap": "weld-rotator-jaw-cap.step",
        "motor-tower": "weld-rotator-motor-tower.step",
        "motor-cradle": "weld-rotator-motor-cradle.step",
        "motor-clamp-pad": "weld-rotator-motor-clamp-pad.step",
        "ground-tower": "weld-rotator-ground-tower.step",
        "ground-arm": "weld-rotator-ground-arm.step",
    }
    for name, filename in outputs.items():
        export_assembly(
            one_body(parts[name], name, M_PETGF_BLACK),
            str(_here.parent / filename),
        )
        print(f"-> {filename}")

    export_assembly(
        one_body(parts["ground-shoe"], "c110-ground-shoe", M_COPPER),
        str(_here.parent / "weld-rotator-ground-shoe.step"),
    )
    print("-> weld-rotator-ground-shoe.step")

    export_assembly(_assembly(parts), str(_here.parent / "weld-rotator-assembly.step"))
    print("-> weld-rotator-assembly.step")

    pilot_clearance = (interface.TUBE_ID - PILOT_OD) / 2.0
    outer_clearance = (OUTER_BORE_D - interface.TUBE_OD) / 2.0
    ball_pitch = 2.0 * math.pi * BALL_RACE_R / BALL_COUNT
    variables = {
        "WR_BASE_X": f"{BASE_X:.0f}",
        "WR_BASE_Y": f"{BASE_Y:.0f}",
        "WR_BASE_Z": f"{BASE_Z:.0f}",
        "WR_BASE_CLEARANCE": f"{BASE_FOOT_H:.0f}",
        "WR_SERVICE_BORE": f"{SERVICE_BORE_D:.0f}",
        "WR_RETAINER_POCKET": f"{RETAINER_POCKET_D:.0f}",
        "WR_BALLS": f"{BALL_COUNT}",
        "WR_BALL_D": f"{BALL_D:.0f}",
        "WR_BALL_RACE": f"{2.0 * BALL_RACE_R:.0f}",
        "WR_BALL_PITCH": f"{ball_pitch:.1f}",
        "WR_TABLE_TEETH": f"{interface.TABLE_PULLEY_TEETH}",
        "WR_MOTOR_TEETH": f"{interface.MOTOR_PULLEY_TEETH}",
        "WR_RATIO": f"{interface.drive_ratio():.1f}:1",
        "WR_CENTER": f"{interface.belt_center_distance():.1f}",
        "WR_WRAP": f"{interface.small_pulley_wrap_degrees():.1f}°",
        "WR_PILOT_OD": f"{PILOT_OD:.2f}",
        "WR_PILOT_H": f"{PILOT_H:.1f}",
        "WR_PILOT_CLEAR": f"{pilot_clearance:.2f}",
        "WR_OUTER_BORE": f"{OUTER_BORE_D:.2f}",
        "WR_OUTER_CLEAR": f"{outer_clearance:.2f}",
        "WR_RECESS": f"{interface.ENDCAP_RECESS:.2f}",
        "WR_NEST_OD": f"{NEST_OD:.0f}",
        "WR_TUBE_TOP": f"{NEST_SEAT_Z + NEST_BASE_H + interface.TUBE_LENGTH:.1f}",
        "WR_TUBE_TOP_BENCH": (
            f"{BASE_FOOT_H + NEST_SEAT_Z + NEST_BASE_H + interface.TUBE_LENGTH:.1f}"
        ),
    }
    substitute_py_comments(_here, variables=variables)
    substitute_md(_here.parent / "README.md", variables=variables)
    print("-> README.md")

    for name, part in parts.items():
        bb = part.val().BoundingBox()
        print(
            f"{name:12s} {bb.xlen:7.2f} × {bb.ylen:7.2f} × {bb.zlen:7.2f} mm  "
            f"{part.val().Volume() / 1000.0:8.1f} cm³"
        )


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        selftest()
        print("weld rotator selftest: pass")
    else:
        main()
