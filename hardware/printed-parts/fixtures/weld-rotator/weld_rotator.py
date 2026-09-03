"""PET-GF cap-weld tube rotator.

World frame:
  Z is the rotary axis and points up through the 5 inch tube.
  X points from the tube axis toward the NEMA 23 motor.
  Y completes the right-handed frame.
  Z=0 is the stationary base's bottom face.

The base, four feet, motor tower, sliding motor carriage, two clamp pads,
turntable, upper race ring, spool, tube nest, ball cage, ground tower and
ground arm are printable.  The turntable runs on the
project's stock 10 mm PP balls.  The 90-tooth HTD-5M pulley is part of the
turntable and is driven by the purchased 20-tooth pulley and 550 mm belt.

The purchased pulley's motor-side flange is gauged 0.25 mm below the motor's
1.6 mm face pilot.  That puts the 16 mm belt land in the printed pulley's
tooth zone and leaves the pulley's outer face 0.85 mm beyond the nominal
21 mm shaft end.  Only a 2 mm pilot skin sits between the face and the belt;
every other stationary member stays outside the belt's swept path.
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
from _material_base import (  # noqa: E402
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
# 10 mm polypropylene; the cage spaces 36 of them without carrying load.  The
# lower groove is in the base's top face; the upper groove is in a separate
# race ring, so both running surfaces are printed as top faces.
BALL_D = 10.0
BALL_CLEARANCE = 0.15
BALL_RACE_R = 82.5
BALL_COUNT = 36
BALL_CENTER_Z = BASE_Z + 3.0
RACE_CUT_R = BALL_D / 2.0 + BALL_CLEARANCE
CAGE_H = 2.0
CAGE_INNER_R = BALL_RACE_R - 7.5
CAGE_OUTER_R = BALL_RACE_R + 7.5
CAGE_POCKET_D = BALL_D + 0.55

# Upper race ring: printed groove-up, then screwed groove-down to the flat
# underside of the platter.  Its groove face sits 5 mm above the base's.
RACE_RING_Z0 = BASE_Z + 5.0
RACE_RING_H = 6.0
RACE_RING_Z1 = RACE_RING_Z0 + RACE_RING_H
RACE_RING_INNER_R = 68.0
RACE_RING_OUTER_R = 92.0
RACE_RING_SCREW_R = 72.5
RACE_RING_SCREW_ANGLES = (30.0, 150.0, 270.0)
RACE_RING_SCREW_LENGTH = 8.0
RACE_RING_INSERT_DEPTH = 6.0
CAGE_Z = (BASE_Z + RACE_RING_Z0) / 2.0 - CAGE_H / 2.0

# The moving disk's flat underside is its bed face: the race ring bolts to it
# and the spool hangs from it.  Its wide pitch radius is the angular datum.
PLATTER_R = 94.0
PLATTER_Z0 = RACE_RING_Z1
PLATTER_Z1 = 32.0
SERVICE_BORE_D = interface.SERVICE_BORE_DIAMETER
M3_HEAD_D = 6.2
M3_HEAD_DEPTH = 3.2
M3_SHANK_D = 3.5
M3_INSERT_D = 4.0
M3_INSERT_LENGTH = 4.0

# Spool: the hub and the lift-catch flange in one part, inserted from below
# through the base and screwed up into the platter.  The flange rim keeps a
# 1 mm running gap to the base shoulder so it catches lift without carrying
# running load.
SPOOL_HUB_OD = 112.0
SPOOL_CLEARANCE_D = 114.0
SPOOL_FLANGE_OD = 124.0
SPOOL_POCKET_D = 126.0
SPOOL_POCKET_H = 6.0
SPOOL_FLANGE_Z0 = 1.0
SPOOL_FLANGE_H = 4.0
SPOOL_HUB_Z0 = SPOOL_FLANGE_Z0 + SPOOL_FLANGE_H
SPOOL_GAP = SPOOL_POCKET_H - SPOOL_HUB_Z0
SPOOL_SCREW_R = 51.0
SPOOL_SCREW_ANGLES = (60.0, 180.0, 300.0)
SPOOL_SCREW_LENGTH = 25.0
SPOOL_INSERT_DEPTH = 6.8

# Printed 90T pulley.  Exact 5 mm pitch; the groove is a printable clearance
# trapezoid — [3.6](WR_PULLEY_OPENING) mm at the tip circle — that accepts
# the belt tooth's 3.05 mm root and absorbs accumulated pitch error over the
# 45 engaged teeth.  The first belt-fit coupon is the acceptance gate before
# the complete turntable is printed.
TABLE_PITCH_R = interface.pitch_diameter(interface.TABLE_PULLEY_TEETH) / 2.0
MOTOR_PITCH_R = interface.pitch_diameter(interface.MOTOR_PULLEY_TEETH) / 2.0
PITCH_LINE_OFFSET = interface.BELT_PITCH_LINE_OFFSET
PULLEY_TIP_R = TABLE_PITCH_R - PITCH_LINE_OFFSET
PULLEY_GROOVE_DEPTH = 2.15
PULLEY_ROOT_R = PULLEY_TIP_R - PULLEY_GROOVE_DEPTH
PULLEY_INNER_R = 64.5
PULLEY_Z0 = PLATTER_Z1
PULLEY_TOOTH_Z0 = PULLEY_Z0 + 1.0
PULLEY_TOOTH_H = 17.0
PULLEY_Z1 = PULLEY_TOOTH_Z0 + PULLEY_TOOTH_H + 1.0
PULLEY_FLANGE_R = PULLEY_TIP_R + 3.0
PULLEY_FLANGE_H = 1.0
GROOVE_TIP_HALF_W = 1.80
GROOVE_ROOT_HALF_W = 1.30
GROOVE_OVERCUT = 1.0
GROOVE_UNDERCUT = 0.15
COUPON_TEETH = 12

# The central pedestal places the replaceable precision nest above the belt.
PEDESTAL_R = PULLEY_INNER_R + 1.5
NEST_SEAT_Z = 52.0
REGISTER_OD = 112.0
REGISTER_H = 3.0
REGISTER_SLIP = 0.25
NEST_SCREW_R = 61.0
NEST_SCREW_D = 3.5
NEST_RETAINER_ANGLES = (0.0, 120.0, 240.0)
NEST_RETAINER_ACCESS_D = M3_HEAD_D
NEST_INSERT_D = 4.0
NEST_INSERT_DEPTH = 5.2

# Tube nest — the [4.5](WR_PILOT_H) pilot fits above a welded plate's
# [6.35](WR_RECESS) recess.  Three radial screws bear directly on the OD;
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
TUBE_ADJUSTER_ANGLES = (60.0, 180.0, 300.0)
TUBE_ADJUSTER_INSERT_D = 4.0
TUBE_ADJUSTER_INSERT_DEPTH = 5.2
M3_ADJUSTER_SHANK_D = 3.4
TUBE_ADJUSTER_Z = NEST_BASE_H + PILOT_H - M3_ADJUSTER_SHANK_D / 2.0

# The purchased belt fixes the exact nominal centre.  Slots only move the motor
# outward: belt installation occurs at the nominal end and tension is added by
# sliding away from the turntable.
MOTOR_CENTER_NOMINAL = interface.belt_center_distance()
MOTOR_CENTER_MIN = MOTOR_CENTER_NOMINAL - 1.0
MOTOR_CENTER_MAX = MOTOR_CENTER_NOMINAL + 7.0
MOTOR_SLOT_R = 1.8

# Belt plane.  The motor hangs face-down.  The purchased pulley's 16 mm land
# is centred in the printed pulley's tooth zone; its motor-side flange keeps a
# measured running gap to the motor's projecting face pilot.  The resulting
# 0.85 mm nominal overhang beyond the shaft end is intentional.
MOTOR_PULLEY_PILOT_GAP = 0.25
MOTOR_PULLEY_Z0 = (
    PULLEY_TOOTH_Z0 + PULLEY_TOOTH_H / 2.0
    - interface.MOTOR_PULLEY_LENGTH / 2.0
)
MOTOR_PULLEY_Z1 = MOTOR_PULLEY_Z0 + interface.MOTOR_PULLEY_LENGTH
MOTOR_FACE_Z = (
    MOTOR_PULLEY_Z1
    + interface.MOTOR_PILOT_LENGTH
    + MOTOR_PULLEY_PILOT_GAP
)
MOTOR_LAND_Z0 = MOTOR_PULLEY_Z0 + interface.MOTOR_PULLEY_FLANGE_LENGTH
MOTOR_LAND_Z1 = MOTOR_PULLEY_Z1 - interface.MOTOR_PULLEY_FLANGE_LENGTH
BELT_Z0 = MOTOR_LAND_Z0
BELT_Z1 = MOTOR_LAND_Z1
MOTOR_SHAFT_TIP_Z = MOTOR_FACE_Z - interface.MOTOR_SHAFT_LENGTH
MOTOR_PULLEY_SHAFT_OVERHANG = MOTOR_SHAFT_TIP_Z - MOTOR_PULLEY_Z0
MOTOR_PULLEY_CORE_D = 2.0 * (MOTOR_PITCH_R - PITCH_LINE_OFFSET)
MOTOR_PULLEY_FLANGE_D = interface.MOTOR_PULLEY_FLANGE_DIAMETER

# Motor tower: two rails outside the belt's swept path, tied by a rear wall
# behind the pulley's wrap, on the base's four M5 stations.  The rail feet
# are wide enough to seat the M5 heads; above the belt's height the rails
# narrow away from the spans.  The carriage seats on the rail tops.
TOWER_X0 = 110.0
TOWER_X1 = 178.0
TOWER_Y_HALF = 45.0
TOWER_FOOT_Y0 = 30.0
TOWER_RAIL_Y0 = 33.0
TOWER_Z0 = BASE_Z
TOWER_FOOT_Z1 = BASE_Z + 8.0
TOWER_Z1 = MOTOR_FACE_Z - 8.0
TOWER_REAR_X0 = 151.0
TOWER_MOUNT_POINTS = (
    (116.0, -36.0),
    (116.0, 36.0),
    (164.0, -36.0),
    (164.0, 36.0),
)
TOWER_RAIL_INSERT_X = (130.0, 150.0)
TOWER_RAIL_INSERT_Y = 41.0
TOWER_RAIL_INSERT_DEPTH = 6.0
M5_SHANK_D = 5.5
M5_HEAD_D = 9.0
M5_HEAD_DEPTH = 4.5
M5_INSERT_D = 7.0
M5_INSERT_DEPTH = 9.7

# Motor carriage: a 2 mm pilot skin under the whole face, arms that follow
# the belt's swept path with clearance, four slotted screws into the rail
# tops, and two side walls whose pads clamp the 57.3 mm frame.  The face
# pilot in the skin takes the belt tension; the pads only hold the motor down
# and square.
CARRIAGE_X0 = 94.0
CARRIAGE_X1 = 165.0
CARRIAGE_Y_HALF = TOWER_Y_HALF
CARRIAGE_ARM_Z0 = TOWER_Z1
CARRIAGE_SKIN_H = 2.0
CARRIAGE_SKIN_Z0 = MOTOR_FACE_Z - CARRIAGE_SKIN_H
CARRIAGE_PILOT_D = 38.6
CARRIAGE_BELT_MARGIN = 2.0
CARRIAGE_WALL_Y0 = 32.0
CARRIAGE_WALL_Y1 = 37.5
CARRIAGE_WALL_X_HALF = interface.MOTOR_FRAME / 2.0 + 0.35
CARRIAGE_WALL_H = 16.0
CARRIAGE_SCREW_LENGTH = 10.0

# The motor bolts to the carriage through its two rear flange holes.  The
# front pair of the 47.14 mm square falls inside the belt's swept path and
# stays open.  Heads recess flush into the arms' underside, so the motor and
# carriage are joined on the bench and go onto the tower as one piece.
MOTOR_MOUNT_X = MOTOR_CENTER_NOMINAL + interface.MOTOR_MOUNT_SQUARE / 2.0
MOTOR_MOUNT_Y = interface.MOTOR_MOUNT_SQUARE / 2.0
MOTOR_MOUNT_CSK_D = 9.4
MOTOR_MOUNT_CSK_DEPTH = (MOTOR_MOUNT_CSK_D - M5_SHANK_D) / 2.0
MOTOR_MOUNT_SCREW_LENGTH = 12.0

MOTOR_CLAMP_PAD_X = 48.0
MOTOR_CLAMP_PAD_Y = 3.0
MOTOR_CLAMP_PAD_Z = 12.0
MOTOR_CLAMP_SCREW_X = 18.0
MOTOR_CLAMP_SCREW_Z = MOTOR_FACE_Z + 8.0
MOTOR_CLAMP_INSERT_DEPTH = 5.2
MOTOR_CLAMP_SOCKET_D = 2.85
MOTOR_CLAMP_SOCKET_DEPTH = 2.2
MOTOR_CLAMP_SCREW_LENGTH = 8.0

# A stationary copper shoe gives the laser welder's continuity interlock a
# path that does not travel through the polymer bearing or wind a work cable
# around the vessel.  Its PET-GF arm is a replaceable in-plane leaf spring;
# the shoe is one 25 mm crosscut from the acquired nominal 6 x 50 mm
# (1/4 x 2 inch) C110 flat bar, stood with the stock width vertical.  The
# factory face bears on the tube and the cut edge is only a seated side.
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
GROUND_BEAM_CENTER_X = -104.5
GROUND_BEAM_T = 5.0
GROUND_BEAM_X0 = GROUND_BEAM_CENTER_X - GROUND_BEAM_T / 2.0
GROUND_BEAM_X1 = GROUND_BEAM_CENTER_X + GROUND_BEAM_T / 2.0
GROUND_BEAM_Y0 = -40.0
GROUND_BEAM_Y1 = 5.0
GROUND_NOSE_Y = 10.0
GROUND_SPRING_FILLET_R = 2.0
GROUND_SHOE_FRONT_X = -62.5
GROUND_SHOE_T = 6.0
GROUND_SHOE_MIN_T = 5.75
GROUND_SHOE_MAX_T = 6.5
GROUND_SHOE_BACK_X = GROUND_SHOE_FRONT_X - GROUND_SHOE_T
GROUND_SHOE_Y = 25.0
GROUND_SHOE_SIDE_CLEARANCE = 0.4
GROUND_SHOE_Z = 50.0
GROUND_SHOE_Z0 = GROUND_TOP_Z - 1.0
GROUND_HOLDER_H = 12.0
GROUND_HOLDER_BACK_T = 3.0
# The loaded tube seats the shoe's back face on this wall.  Across the
# delivered bar's 5.75--6.5 mm thickness window that leaves 0.75--1.5 mm of
# flexure preload; thickness variation therefore cannot open the contact.
GROUND_HOLDER_BACK_FACE_X = GROUND_SHOE_BACK_X
GROUND_HOLDER_FRONT_X = -64.0
GROUND_HOLDER_SIDE_T = 3.0
GROUND_HOLDER_CLAMP_T = 7.0
GROUND_HOLDER_SHELF_H = 3.0
GROUND_HOLDER_CLAMP_INNER_Y = -(GROUND_SHOE_Y / 2.0 + GROUND_SHOE_SIDE_CLEARANCE)
GROUND_HOLDER_CLAMP_OUTER_Y = GROUND_HOLDER_CLAMP_INNER_Y - GROUND_HOLDER_CLAMP_T
GROUND_HOLDER_FIXED_INNER_Y = GROUND_SHOE_Y / 2.0 + GROUND_SHOE_SIDE_CLEARANCE
GROUND_HOLDER_FIXED_OUTER_Y = GROUND_HOLDER_FIXED_INNER_Y + GROUND_HOLDER_SIDE_T
GROUND_SHOE_CLAMP_SHANK_D = 3.4
GROUND_SHOE_CLAMP_INSERT_D = 4.0
GROUND_SHOE_CLAMP_INSERT_DEPTH = 5.2
GROUND_SHOE_CLAMP_SCREW_LENGTH = 8.0
GROUND_SHOE_CLAMP_X = GROUND_SHOE_FRONT_X - GROUND_SHOE_T / 2.0
GROUND_SHOE_CLAMP_Z = GROUND_TOP_Z + GROUND_ARM_H / 2.0
GROUND_TEARDROP_ROOF_ANGLE = 36.0
GROUND_ARM_SHANK_D = 3.4
GROUND_ARM_INSERT_D = 4.0
GROUND_ARM_INSERT_DEPTH = 5.2


def _ring(section):
    """A section's own points with the first repeated, so the closing edge is DRAWN.

    `close()` infers it instead, from the last edge's end read back off OCCT — a few 1e-16 off
    the point that was passed in — and a tangential boolean downstream resolves that vertex one
    way in one process and the other way in the next. Naming the point is what makes the same
    source write the same bytes."""
    pts = list(section)
    return pts if pts[0] == pts[-1] else pts + [pts[0]]


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


def _teardrop_y(radius: float, x: float, z: float, y0: float, y1: float):
    """Support-free Y-axis bore in a part printed on the XY plane.

    The entire nominal circle remains below a pair of tangent roof planes, so
    a round screw or heat-set insert still has its specified fit without an
    unsupported circular crown.
    """
    a = math.radians(GROUND_TEARDROP_ROOF_ANGLE)
    half = radius * math.sin(a)
    tangent = z + radius * math.cos(a)
    apex = z + radius / math.cos(a)
    round_bore = cq.Solid.makeCylinder(
        radius,
        y1 - y0,
        cq.Vector(x, y0, z),
        cq.Vector(0.0, 1.0, 0.0),
    )
    roof = (
        cq.Workplane("XZ")
        .polyline(_ring([
            (x - half, tangent),
            (x + half, tangent),
            (x, apex),
        ]))
        .wire()
        .extrude(-(y1 - y0))
        .val()
        .translate((0.0, y0, 0.0))
    )
    return cq.Workplane(obj=round_bore.fuse(roof))


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
        .polyline(_ring([
            (0.0, 0.0),
            (reach * math.cos(-a), reach * math.sin(-a)),
            (reach * math.cos(a), reach * math.sin(a)),
        ]))
        .wire()
        .extrude(height)
    )
    return _annulus(outer_r, inner_r, height, z0).intersect(wedge)


def _annular_sector(cx: float, cy: float, outer_r: float, inner_r: float,
                    a0: float, a1: float, z0: float, height: float):
    """Annulus about (cx, cy) kept between angles a0 and a1, counter-clockwise."""
    ring = (
        cq.Workplane("XY", origin=(cx, cy, z0))
        .circle(outer_r)
        .circle(inner_r)
        .extrude(height)
    )
    span = (a1 - a0) % 360.0
    if span < 1e-9:
        return ring
    reach = outer_r + 5.0
    points = [(cx, cy)]
    steps = 48
    for i in range(steps + 1):
        a = math.radians(a0 + span * i / steps)
        points.append((cx + reach * math.cos(a), cy + reach * math.sin(a)))
    wedge = (
        cq.Workplane("XY", origin=(0.0, 0.0, z0))
        .polyline(_ring(points))
        .wire()
        .extrude(height)
    )
    return ring.intersect(wedge)


def _belt_solid(center: float, z0: float, z1: float, margin: float = 0.0):
    """The closed belt around both pulleys for a motor at `center`: two wraps
    and two straight spans, from tooth tips to back, grown by `margin`."""
    inner = interface.belt_inner_offset() + margin
    outer = interface.belt_outer_offset() + margin
    a = interface.span_tangent_angle(center)
    a_deg = math.degrees(a)
    big_t = (TABLE_PITCH_R * math.cos(a), TABLE_PITCH_R * math.sin(a))
    small_t = (center + MOTOR_PITCH_R * math.cos(a), MOTOR_PITCH_R * math.sin(a))
    h = z1 - z0
    belt = _annular_sector(0.0, 0.0, TABLE_PITCH_R + outer, TABLE_PITCH_R - inner,
                           a_deg, 360.0 - a_deg, z0, h)
    belt = belt.union(
        _annular_sector(center, 0.0, MOTOR_PITCH_R + outer, MOTOR_PITCH_R - inner,
                        -a_deg, a_deg, z0, h)
    )
    for sign in (1.0, -1.0):
        p = (big_t[0], sign * big_t[1])
        q = (small_t[0], sign * small_t[1])
        dx, dy = q[0] - p[0], q[1] - p[1]
        length = math.hypot(dx, dy)
        ux, uy = dx / length, dy / length
        nx, ny = -uy * sign, ux * sign
        polygon = [
            (p[0] + nx * outer, p[1] + ny * outer),
            (q[0] + nx * outer, q[1] + ny * outer),
            (q[0] - nx * inner, q[1] - ny * inner),
            (p[0] - nx * inner, p[1] - ny * inner),
        ]
        belt = belt.union(
            cq.Workplane("XY", origin=(0.0, 0.0, z0)).polyline(_ring(polygon)).wire().extrude(h)
        )
    return belt


def _belt_in_carriage_frame(center: float, z0: float, z1: float, margin: float = 0.0):
    """The belt for a motor at `center`, moved so its pulley sits at the
    carriage's nominal shaft position."""
    return _belt_solid(center, z0, z1, margin).translate(
        (MOTOR_CENTER_NOMINAL - center, 0.0, 0.0)
    )


def _counterbored_m3(x: float, y: float, z_head: float, through: float, from_below: bool):
    """M3 shank plus head recess.  `z_head` is the head's seating face; the
    shank runs `through` millimetres away from the head."""
    if from_below:
        shank = (
            cq.Workplane("XY", origin=(x, y, z_head))
            .circle(M3_SHANK_D / 2.0).extrude(through)
        )
        head = (
            cq.Workplane("XY", origin=(x, y, z_head - M3_HEAD_DEPTH))
            .circle(M3_HEAD_D / 2.0).extrude(M3_HEAD_DEPTH + 0.01)
        )
    else:
        shank = (
            cq.Workplane("XY", origin=(x, y, z_head - through))
            .circle(M3_SHANK_D / 2.0).extrude(through)
        )
        head = (
            cq.Workplane("XY", origin=(x, y, z_head - 0.01))
            .circle(M3_HEAD_D / 2.0).extrude(M3_HEAD_DEPTH + 0.01)
        )
    return shank.union(head)


def _polar(radius: float, angle: float):
    theta = math.radians(angle)
    return radius * math.cos(theta), radius * math.sin(theta)


def build_base():
    base = (
        cq.Workplane("XY")
        .box(BASE_X, BASE_Y, BASE_Z, centered=(True, True, False))
        .translate((BASE_CENTER_X, 0.0, 0.0))
        .edges("|Z")
        .fillet(BASE_CORNER_R)
    )

    base = base.cut(
        cq.Workplane("XY").circle(SPOOL_CLEARANCE_D / 2.0).extrude(BASE_Z)
    )
    base = base.cut(
        cq.Workplane("XY")
        .circle(SPOOL_POCKET_D / 2.0)
        .extrude(SPOOL_POCKET_H)
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


def _groove_half_width(radius: float) -> float:
    """Flank line of the clearance trapezoid, continued straight past both
    the tip and the root so the opening is not pinched by the overcut."""
    t = (radius - PULLEY_ROOT_R) / PULLEY_GROOVE_DEPTH
    return GROOVE_ROOT_HALF_W + (GROOVE_TIP_HALF_W - GROOVE_ROOT_HALF_W) * t


def _pulley_grooves():
    r_out = PULLEY_TIP_R + GROOVE_OVERCUT
    r_in = PULLEY_ROOT_R - GROOVE_UNDERCUT
    groove = (
        cq.Workplane("XY", origin=(0.0, 0.0, PULLEY_TOOTH_Z0))
        .polyline(_ring([
            (r_out, -_groove_half_width(r_out)),
            (r_in, -_groove_half_width(r_in)),
            (r_in, _groove_half_width(r_in)),
            (r_out, _groove_half_width(r_out)),
        ]))
        .wire()
        .extrude(PULLEY_TOOTH_H)
    )
    solids = []
    for tooth in range(interface.TABLE_PULLEY_TEETH):
        solids.append(
            groove.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0),
                          tooth * 360.0 / interface.TABLE_PULLEY_TEETH).val()
        )
    return cq.Workplane(obj=cq.Compound.makeCompound(solids))


def _toothed_ring():
    pulley = _annulus(PULLEY_TIP_R, PULLEY_INNER_R, PULLEY_Z1 - PULLEY_Z0, PULLEY_Z0)
    pulley = pulley.cut(_pulley_grooves())
    lower_flange = _annulus(PULLEY_FLANGE_R, PULLEY_INNER_R, PULLEY_FLANGE_H, PULLEY_Z0)
    upper_flange = _annulus(PULLEY_FLANGE_R, PULLEY_INNER_R,
                            PULLEY_FLANGE_H, PULLEY_Z1 - PULLEY_FLANGE_H)
    return pulley.union(lower_flange).union(upper_flange)


def build_turntable():
    platter = _annulus(PLATTER_R, SERVICE_BORE_D / 2.0,
                       PLATTER_Z1 - PLATTER_Z0, PLATTER_Z0)
    pedestal = _annulus(PEDESTAL_R, SERVICE_BORE_D / 2.0,
                        NEST_SEAT_Z - PLATTER_Z1, PLATTER_Z1)
    turntable = platter.union(pedestal).union(_toothed_ring())

    register = _annulus(REGISTER_OD / 2.0, SERVICE_BORE_D / 2.0,
                        REGISTER_H, NEST_SEAT_Z)
    turntable = turntable.union(register)

    for angle in NEST_RETAINER_ANGLES:
        x, y = _polar(NEST_SCREW_R, angle)
        pocket = (
            cq.Workplane("XY", origin=(x, y, NEST_SEAT_Z - NEST_INSERT_DEPTH))
            .circle(NEST_INSERT_D / 2.0)
            .extrude(NEST_INSERT_DEPTH + 0.01)
        )
        turntable = turntable.cut(pocket)

    for angle in SPOOL_SCREW_ANGLES:
        x, y = _polar(SPOOL_SCREW_R, angle)
        pocket = (
            cq.Workplane("XY", origin=(x, y, PLATTER_Z0 - 0.01))
            .circle(M3_INSERT_D / 2.0)
            .extrude(SPOOL_INSERT_DEPTH + 0.01)
        )
        turntable = turntable.cut(pocket)

    for angle in RACE_RING_SCREW_ANGLES:
        x, y = _polar(RACE_RING_SCREW_R, angle)
        pocket = (
            cq.Workplane("XY", origin=(x, y, PLATTER_Z0 - 0.01))
            .circle(M3_INSERT_D / 2.0)
            .extrude(RACE_RING_INSERT_DEPTH + 0.01)
        )
        turntable = turntable.cut(pocket)
    return turntable


def build_race_ring():
    ring = _annulus(RACE_RING_OUTER_R, RACE_RING_INNER_R, RACE_RING_H, RACE_RING_Z0)
    race = cq.Workplane(
        obj=cq.Solid.makeTorus(
            BALL_RACE_R,
            RACE_CUT_R,
            cq.Vector(0.0, 0.0, BALL_CENTER_Z),
            cq.Vector(0.0, 0.0, 1.0),
        )
    )
    ring = ring.cut(race)
    for angle in RACE_RING_SCREW_ANGLES:
        x, y = _polar(RACE_RING_SCREW_R, angle)
        ring = ring.cut(
            _counterbored_m3(x, y, RACE_RING_Z0 + M3_HEAD_DEPTH,
                             RACE_RING_H - M3_HEAD_DEPTH + 0.02, from_below=True)
        )
    return ring


def build_spool():
    flange = _annulus(SPOOL_FLANGE_OD / 2.0, SERVICE_BORE_D / 2.0,
                      SPOOL_FLANGE_H, SPOOL_FLANGE_Z0)
    hub = _annulus(SPOOL_HUB_OD / 2.0, SERVICE_BORE_D / 2.0,
                   PLATTER_Z0 - SPOOL_HUB_Z0, SPOOL_HUB_Z0)
    spool = flange.union(hub)
    for angle in SPOOL_SCREW_ANGLES:
        x, y = _polar(SPOOL_SCREW_R, angle)
        spool = spool.cut(
            _counterbored_m3(x, y, SPOOL_FLANGE_Z0 + M3_HEAD_DEPTH,
                             PLATTER_Z0 - SPOOL_FLANGE_Z0 - M3_HEAD_DEPTH + 0.02,
                             from_below=True)
        )
    return spool


def build_pulley_coupon():
    pulley = _toothed_ring()
    half_angle = COUPON_TEETH * 360.0 / interface.TABLE_PULLEY_TEETH / 2.0
    coupon = pulley.intersect(
        _sector(PULLEY_FLANGE_R + 1.0, PULLEY_INNER_R - 1.0,
                half_angle, PULLEY_Z1 - PULLEY_Z0, PULLEY_Z0)
    )
    return coupon.translate((0.0, 0.0, -PULLEY_Z0))


def build_cage():
    cage = _annulus(CAGE_OUTER_R, CAGE_INNER_R, CAGE_H, CAGE_Z)
    points = [
        _polar(BALL_RACE_R, 360.0 * i / BALL_COUNT) for i in range(BALL_COUNT)
    ]
    pockets = (
        cq.Workplane("XY", origin=(0.0, 0.0, CAGE_Z))
        .pushPoints(points)
        .circle(CAGE_POCKET_D / 2.0)
        .extrude(CAGE_H)
    )
    return cage.cut(pockets)


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

    for angle in TUBE_ADJUSTER_ANGLES:
        insert = _radial_cylinder(
            angle,
            OUTER_COLLAR_OD / 2.0 + 0.1,
            TUBE_ADJUSTER_Z,
            TUBE_ADJUSTER_INSERT_D,
            TUBE_ADJUSTER_INSERT_DEPTH + 0.2,
        )
        shank_start_r = OUTER_COLLAR_OD / 2.0 - TUBE_ADJUSTER_INSERT_DEPTH
        through = _radial_cylinder(
            angle,
            shank_start_r,
            TUBE_ADJUSTER_Z,
            M3_ADJUSTER_SHANK_D,
            shank_start_r - OUTER_BORE_D / 2.0 + 0.2,
        )
        nest = nest.cut(insert.union(through))

    for angle in NEST_RETAINER_ANGLES:
        x, y = _polar(NEST_SCREW_R, angle)
        shank = (
            cq.Workplane("XY", origin=(x, y, 0.0))
            .circle(NEST_SCREW_D / 2.0)
            .extrude(NEST_BASE_H)
        )
        # The retainer lies under the ID pilot.  Its head recess therefore
        # continues through every feature above the base as a top-entry well.
        head_access = (
            cq.Workplane("XY", origin=(x, y, NEST_BASE_H - M3_HEAD_DEPTH))
            .circle(NEST_RETAINER_ACCESS_D / 2.0)
            .extrude(M3_HEAD_DEPTH + NEST_OUTER_H + 0.01)
        )
        nest = nest.cut(shank.union(head_access))
    return nest


def build_motor_tower():
    tower = None
    for sign in (-1.0, 1.0):
        foot = (
            cq.Workplane("XY", origin=((TOWER_X0 + TOWER_X1) / 2.0,
                                        sign * (TOWER_FOOT_Y0 + TOWER_Y_HALF) / 2.0,
                                        TOWER_Z0))
            .box(TOWER_X1 - TOWER_X0, TOWER_Y_HALF - TOWER_FOOT_Y0,
                 TOWER_FOOT_Z1 - TOWER_Z0, centered=(True, True, False))
        )
        rail = (
            cq.Workplane("XY", origin=((TOWER_X0 + TOWER_X1) / 2.0,
                                        sign * (TOWER_RAIL_Y0 + TOWER_Y_HALF) / 2.0,
                                        TOWER_FOOT_Z1))
            .box(TOWER_X1 - TOWER_X0, TOWER_Y_HALF - TOWER_RAIL_Y0,
                 TOWER_Z1 - TOWER_FOOT_Z1, centered=(True, True, False))
        )
        piece = foot.union(rail)
        tower = piece if tower is None else tower.union(piece)

    rear = (
        cq.Workplane("XY", origin=((TOWER_REAR_X0 + TOWER_X1) / 2.0, 0.0, TOWER_Z0))
        .box(TOWER_X1 - TOWER_REAR_X0, 2.0 * TOWER_Y_HALF,
             TOWER_Z1 - TOWER_Z0, centered=(True, True, False))
    )
    tower = tower.union(rear)

    head_seat_z = TOWER_FOOT_Z1 - M5_HEAD_DEPTH
    for x, y in TOWER_MOUNT_POINTS:
        shank = (
            cq.Workplane("XY", origin=(x, y, TOWER_Z0 - 0.01))
            .circle(M5_SHANK_D / 2.0)
            .extrude(head_seat_z - TOWER_Z0 + 0.02)
        )
        access = (
            cq.Workplane("XY", origin=(x, y, head_seat_z))
            .circle(M5_HEAD_D / 2.0)
            .extrude(TOWER_Z1 - head_seat_z + 0.01)
        )
        tower = tower.cut(shank.union(access))

    for x in TOWER_RAIL_INSERT_X:
        for sign in (-1.0, 1.0):
            pocket = (
                cq.Workplane("XY", origin=(x, sign * TOWER_RAIL_INSERT_Y,
                                            TOWER_Z1 - TOWER_RAIL_INSERT_DEPTH))
                .circle(M3_INSERT_D / 2.0)
                .extrude(TOWER_RAIL_INSERT_DEPTH + 0.01)
            )
            tower = tower.cut(pocket)
    return tower


def _carriage_swept_belt(margin: float):
    """Everything the belt occupies, in the carriage's frame, across the
    whole tension range."""
    swept = None
    for center in (MOTOR_CENTER_MIN, MOTOR_CENTER_NOMINAL, MOTOR_CENTER_MAX):
        belt = _belt_in_carriage_frame(center, BELT_Z0 - 1.0, BELT_Z1 + 1.0, margin)
        swept = belt if swept is None else swept.union(belt)
    return swept


def _motor_mount_screws(offset: float = 0.0):
    """The two rear flange screws as installed, for a carriage displaced
    `offset` along X.  They run from the countersink's top face up into the
    motor's tapped holes."""
    screws = None
    for sign in (-1.0, 1.0):
        screw = cq.Workplane(
            obj=cq.Solid.makeCylinder(
                M5_SHANK_D / 2.0,
                MOTOR_MOUNT_SCREW_LENGTH,
                cq.Vector(MOTOR_MOUNT_X + offset, sign * MOTOR_MOUNT_Y,
                          CARRIAGE_ARM_Z0),
                cq.Vector(0.0, 0.0, 1.0),
            )
        )
        screws = screw if screws is None else screws.union(screw)
    return screws


def build_motor_carriage():
    center = MOTOR_CENTER_NOMINAL
    x_mid = (CARRIAGE_X0 + CARRIAGE_X1) / 2.0
    arms = (
        cq.Workplane("XY", origin=(x_mid, 0.0, CARRIAGE_ARM_Z0))
        .box(CARRIAGE_X1 - CARRIAGE_X0, 2.0 * CARRIAGE_Y_HALF,
             CARRIAGE_SKIN_Z0 - CARRIAGE_ARM_Z0, centered=(True, True, False))
    )
    arms = arms.cut(_carriage_swept_belt(CARRIAGE_BELT_MARGIN))
    arms = arms.cut(
        cq.Workplane("XY", origin=(center, 0.0, CARRIAGE_ARM_Z0 - 0.01))
        .circle(CARRIAGE_PILOT_D / 2.0)
        .extrude(CARRIAGE_SKIN_Z0 - CARRIAGE_ARM_Z0 + 0.02)
    )
    skin = (
        cq.Workplane("XY", origin=(x_mid, 0.0, CARRIAGE_SKIN_Z0))
        .box(CARRIAGE_X1 - CARRIAGE_X0, 2.0 * CARRIAGE_Y_HALF,
             CARRIAGE_SKIN_H, centered=(True, True, False))
    )
    skin = skin.cut(
        cq.Workplane("XY", origin=(center, 0.0, CARRIAGE_SKIN_Z0 - 0.01))
        .circle(CARRIAGE_PILOT_D / 2.0)
        .extrude(CARRIAGE_SKIN_H + 0.02)
    )
    carriage = arms.union(skin)

    for sign in (-1.0, 1.0):
        wall = (
            cq.Workplane("XY", origin=(center,
                                        sign * (CARRIAGE_WALL_Y0 + CARRIAGE_WALL_Y1) / 2.0,
                                        MOTOR_FACE_Z))
            .box(2.0 * CARRIAGE_WALL_X_HALF, CARRIAGE_WALL_Y1 - CARRIAGE_WALL_Y0,
                 CARRIAGE_WALL_H, centered=(True, True, False))
        )
        carriage = carriage.union(wall)
        direction = cq.Vector(0.0, -sign, 0.0)
        y_outer = sign * CARRIAGE_WALL_Y1
        for x_offset in (-MOTOR_CLAMP_SCREW_X, MOTOR_CLAMP_SCREW_X):
            origin = cq.Vector(center + x_offset, y_outer + sign * 0.01, MOTOR_CLAMP_SCREW_Z)
            shank = cq.Workplane(
                obj=cq.Solid.makeCylinder(
                    M3_ADJUSTER_SHANK_D / 2.0,
                    CARRIAGE_WALL_Y1 - CARRIAGE_WALL_Y0 + 0.02,
                    origin,
                    direction,
                )
            )
            insert = cq.Workplane(
                obj=cq.Solid.makeCylinder(
                    M3_INSERT_D / 2.0,
                    MOTOR_CLAMP_INSERT_DEPTH + 0.01,
                    origin,
                    direction,
                )
            )
            carriage = carriage.cut(shank.union(insert))

    for sign in (-1.0, 1.0):
        y = sign * MOTOR_MOUNT_Y
        shank = (
            cq.Workplane("XY", origin=(MOTOR_MOUNT_X, y, CARRIAGE_ARM_Z0 - 0.01))
            .circle(M5_SHANK_D / 2.0)
            .extrude(MOTOR_FACE_Z - CARRIAGE_ARM_Z0 + 0.02)
        )
        head = cq.Workplane(
            obj=cq.Solid.makeCone(
                MOTOR_MOUNT_CSK_D / 2.0,
                M5_SHANK_D / 2.0,
                MOTOR_MOUNT_CSK_DEPTH,
                cq.Vector(MOTOR_MOUNT_X, y, CARRIAGE_ARM_Z0),
                cq.Vector(0.0, 0.0, 1.0),
            )
        )
        carriage = carriage.cut(shank.union(head))

    for x in TOWER_RAIL_INSERT_X:
        for sign in (-1.0, 1.0):
            y = sign * TOWER_RAIL_INSERT_Y
            x0 = x - (MOTOR_CENTER_MAX - MOTOR_CENTER_NOMINAL)
            x1 = x + (MOTOR_CENTER_NOMINAL - MOTOR_CENTER_MIN)
            carriage = carriage.cut(
                _vertical_slot(x0, x1, y, 2.0 * MOTOR_SLOT_R,
                               CARRIAGE_ARM_Z0 - 0.01,
                               MOTOR_FACE_Z - CARRIAGE_ARM_Z0 + 0.02)
            )
            carriage = carriage.cut(
                _vertical_slot(x0, x1, y, M3_HEAD_D,
                               MOTOR_FACE_Z - M3_HEAD_DEPTH,
                               M3_HEAD_DEPTH + 0.01)
            )
    return carriage


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
        cq.Workplane(
            "XY",
            origin=((GROUND_BEAM_X0 + GROUND_HOLDER_BACK_FACE_X) / 2.0,
                    0.0,
                    GROUND_TOP_Z),
        )
        .box(GROUND_HOLDER_BACK_FACE_X - GROUND_BEAM_X0,
             GROUND_NOSE_Y,
             GROUND_ARM_H,
             centered=(True, True, False))
    )
    back = (
        cq.Workplane(
            "XY",
            origin=(GROUND_HOLDER_BACK_FACE_X - GROUND_HOLDER_BACK_T / 2.0,
                    (GROUND_HOLDER_CLAMP_OUTER_Y
                     + GROUND_HOLDER_FIXED_OUTER_Y) / 2.0,
                    GROUND_SHOE_Z0),
        )
        .box(GROUND_HOLDER_BACK_T,
             GROUND_HOLDER_FIXED_OUTER_Y - GROUND_HOLDER_CLAMP_OUTER_Y,
             GROUND_HOLDER_H,
             centered=(True, True, False))
    )
    clamp_jaw = (
        cq.Workplane(
            "XY",
            origin=((GROUND_HOLDER_BACK_FACE_X + GROUND_HOLDER_FRONT_X) / 2.0,
                    (GROUND_HOLDER_CLAMP_OUTER_Y
                     + GROUND_HOLDER_CLAMP_INNER_Y) / 2.0,
                    GROUND_SHOE_Z0),
        )
        .box(GROUND_HOLDER_FRONT_X - GROUND_HOLDER_BACK_FACE_X,
             GROUND_HOLDER_CLAMP_T,
             GROUND_HOLDER_H,
             centered=(True, True, False))
    )
    fixed_jaw = (
        cq.Workplane(
            "XY",
            origin=((GROUND_HOLDER_BACK_FACE_X + GROUND_HOLDER_FRONT_X) / 2.0,
                    (GROUND_HOLDER_FIXED_INNER_Y
                     + GROUND_HOLDER_FIXED_OUTER_Y) / 2.0,
                    GROUND_SHOE_Z0),
        )
        .box(GROUND_HOLDER_FRONT_X - GROUND_HOLDER_BACK_FACE_X,
             GROUND_HOLDER_SIDE_T,
             GROUND_HOLDER_H,
             centered=(True, True, False))
    )
    shelf = (
        cq.Workplane(
            "XY",
            origin=((GROUND_HOLDER_BACK_FACE_X + GROUND_HOLDER_FRONT_X) / 2.0,
                    0.0,
                    GROUND_SHOE_Z0 - GROUND_HOLDER_SHELF_H),
        )
        .box(GROUND_HOLDER_FRONT_X - GROUND_HOLDER_BACK_FACE_X,
             GROUND_HOLDER_FIXED_INNER_Y - GROUND_HOLDER_CLAMP_INNER_Y,
             GROUND_HOLDER_SHELF_H,
             centered=(True, True, False))
    )
    spring = pad.union(beam).union(nose)
    spring_fillet_points = (
        (GROUND_BEAM_X0, GROUND_PAD_Y1),
        (GROUND_BEAM_X1, GROUND_PAD_Y1),
        (GROUND_BEAM_X0, GROUND_NOSE_Y / 2.0),
        (GROUND_BEAM_X1, -GROUND_NOSE_Y / 2.0),
    )
    spring_fillet_edges = [
        edge
        for edge in spring.edges("|Z").vals()
        if any(
            math.hypot(edge.Center().x - x, edge.Center().y - y) < 1e-6
            for x, y in spring_fillet_points
        )
    ]
    if len(spring_fillet_edges) != len(spring_fillet_points):
        raise ValueError("ground spring corner selection changed")
    spring = cq.Workplane(
        obj=spring.val().fillet(GROUND_SPRING_FILLET_R, spring_fillet_edges)
    )
    arm = spring.union(back).union(clamp_jaw).union(fixed_jaw).union(shelf)

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

    clamp_shank = _teardrop_y(
        GROUND_SHOE_CLAMP_SHANK_D / 2.0,
        GROUND_SHOE_CLAMP_X,
        GROUND_SHOE_CLAMP_Z,
        GROUND_HOLDER_CLAMP_OUTER_Y - 0.1,
        GROUND_HOLDER_CLAMP_INNER_Y + 0.1,
    )
    clamp_insert = _teardrop_y(
        GROUND_SHOE_CLAMP_INSERT_D / 2.0,
        GROUND_SHOE_CLAMP_X,
        GROUND_SHOE_CLAMP_Z,
        GROUND_HOLDER_CLAMP_OUTER_Y - 0.1,
        GROUND_HOLDER_CLAMP_OUTER_Y + GROUND_SHOE_CLAMP_INSERT_DEPTH,
    )
    return arm.cut(clamp_shank.union(clamp_insert))


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


def build_motor_proxy(center: float = MOTOR_CENTER_NOMINAL):
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


def build_motor_pulley_proxy(center: float = MOTOR_CENTER_NOMINAL):
    flange_h = interface.MOTOR_PULLEY_FLANGE_LENGTH
    core = (
        cq.Workplane("XY", origin=(center, 0.0, MOTOR_LAND_Z0))
        .circle(MOTOR_PULLEY_CORE_D / 2.0)
        .circle(interface.MOTOR_SHAFT_DIAMETER / 2.0)
        .extrude(MOTOR_LAND_Z1 - MOTOR_LAND_Z0)
    )
    pulley = core
    for z in (MOTOR_PULLEY_Z0, MOTOR_PULLEY_Z1 - flange_h):
        pulley = pulley.union(
            cq.Workplane("XY", origin=(center, 0.0, z))
            .circle(MOTOR_PULLEY_FLANGE_D / 2.0)
            .circle(interface.MOTOR_SHAFT_DIAMETER / 2.0)
            .extrude(flange_h)
        )
    return pulley


def build_belt_proxy(center: float = MOTOR_CENTER_NOMINAL):
    z0 = (BELT_Z0 + BELT_Z1) / 2.0 - interface.BELT_WIDTH / 2.0
    return _belt_solid(center, z0, z0 + interface.BELT_WIDTH)


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
        x, y = _polar(BALL_RACE_R, 360.0 * i / BALL_COUNT)
        balls.append(
            cq.Workplane("XY")
            .sphere(BALL_D / 2.0)
            .translate((x, y, BALL_CENTER_Z))
            .val()
        )
    return cq.Workplane(obj=cq.Compound.makeCompound(balls))


def _valid(name: str, part):
    value = part.val()
    if not value.isValid():
        raise ValueError(f"{name} is not a valid solid")
    if value.Volume() <= 0.0:
        raise ValueError(f"{name} has no volume")


def _overlap(a, b) -> float:
    return a.intersect(b).val().Volume()


def selftest():
    parts = {
        "base": build_base(),
        "base-foot": build_base_foot(),
        "turntable": build_turntable(),
        "race-ring": build_race_ring(),
        "spool": build_spool(),
        "pulley-coupon": build_pulley_coupon(),
        "ball-cage": build_cage(),
        "tube-nest": build_nest(),
        "motor-tower": build_motor_tower(),
        "motor-carriage": build_motor_carriage(),
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
    if SPOOL_POCKET_D / 2.0 + 10.0 >= BALL_RACE_R - RACE_CUT_R:
        raise ValueError("spool pocket leaves too little base web inside the race")

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

    # Race: both grooves are top faces when printed; the cage floats between.
    ball_pitch = 2.0 * math.pi * BALL_RACE_R / BALL_COUNT
    if ball_pitch < CAGE_POCKET_D + 2.0:
        raise ValueError("ball cage leaves less than 2 mm between pockets")
    if CAGE_Z < BASE_Z + 1.0 or CAGE_Z + CAGE_H > RACE_RING_Z0 - 1.0:
        raise ValueError("ball cage does not clear both race faces by 1 mm")
    groove_crest = BALL_CENTER_Z + RACE_CUT_R
    if RACE_RING_Z1 - groove_crest < 2.5:
        raise ValueError("race ring floor above the groove crest is under 2.5 mm")
    groove_edge_r = BALL_RACE_R - math.sqrt(
        RACE_CUT_R ** 2 - (RACE_RING_Z0 - BALL_CENTER_Z) ** 2
    )
    head_outer_r = RACE_RING_SCREW_R + M3_HEAD_D / 2.0
    head_inner_r = RACE_RING_SCREW_R - M3_HEAD_D / 2.0
    if groove_edge_r - head_outer_r < 1.0 or head_inner_r - RACE_RING_INNER_R < 1.0:
        raise ValueError("race ring screw heads crowd the groove or the inner edge")
    ring_seat_z = RACE_RING_Z0 + M3_HEAD_DEPTH
    ring_tip_z = ring_seat_z + RACE_RING_SCREW_LENGTH
    ring_reach = ring_tip_z - PLATTER_Z0
    if ring_reach < M3_INSERT_LENGTH or ring_reach > RACE_RING_INSERT_DEPTH - 0.5:
        raise ValueError("M3 x 8 race ring screws do not land in their platter inserts")
    if PLATTER_Z0 + RACE_RING_INSERT_DEPTH > PLATTER_Z1 - 2.0:
        raise ValueError("race ring insert pockets leave under 2 mm of platter above them")
    if RACE_RING_OUTER_R > PLATTER_R:
        raise ValueError("race ring projects beyond the platter")

    # Spool: inserted through the base, catches lift with a 1 mm running gap.
    if SPOOL_FLANGE_Z0 < 0.0:
        raise ValueError("spool flange projects below the base")
    if abs(SPOOL_GAP - 1.0) > 1e-6:
        raise ValueError("spool flange does not preserve its running gap")
    if SPOOL_HUB_OD >= SPOOL_CLEARANCE_D or SPOOL_FLANGE_OD >= SPOOL_POCKET_D:
        raise ValueError("spool binds in the base")
    spool_seat_z = SPOOL_FLANGE_Z0 + M3_HEAD_DEPTH
    spool_reach = spool_seat_z + SPOOL_SCREW_LENGTH - PLATTER_Z0
    if spool_reach < M3_INSERT_LENGTH or spool_reach > SPOOL_INSERT_DEPTH - 0.5:
        raise ValueError("M3 x 25 spool screws do not land in their platter inserts")
    if PLATTER_Z0 + SPOOL_INSERT_DEPTH > PLATTER_Z1 - 2.0:
        raise ValueError("spool insert pockets leave under 2 mm of platter above them")

    # Nest datum.
    pilot_radial_clearance = (interface.TUBE_ID - PILOT_OD) / 2.0
    outer_radial_clearance = (OUTER_BORE_D - interface.TUBE_OD) / 2.0
    if pilot_radial_clearance <= 0.0 or outer_radial_clearance <= 0.0:
        raise ValueError("tube nest nominal clearances are not positive")
    if PILOT_H >= interface.ENDCAP_RECESS:
        raise ValueError("ID pilot reaches a welded end-cap plate")
    collar_wall = (OUTER_COLLAR_OD - OUTER_BORE_D) / 2.0
    if TUBE_ADJUSTER_INSERT_DEPTH >= collar_wall:
        raise ValueError("tube-adjuster insert removes the collar's inner screw guide")
    if (
        TUBE_ADJUSTER_Z - M3_ADJUSTER_SHANK_D / 2.0 < NEST_BASE_H
        or TUBE_ADJUSTER_Z + M3_ADJUSTER_SHANK_D / 2.0
        > NEST_BASE_H + PILOT_H
    ):
        raise ValueError("tube adjuster does not bear over the nest's ID pilot")
    for angle in NEST_RETAINER_ANGLES:
        x, y = _polar(NEST_SCREW_R, angle)
        insertion_path = (
            cq.Workplane(
                "XY", origin=(x, y, NEST_BASE_H - M3_HEAD_DEPTH + 0.02)
            )
            .circle((NEST_RETAINER_ACCESS_D - 0.10) / 2.0)
            .extrude(M3_HEAD_DEPTH + NEST_OUTER_H + 10.0)
        )
        if _overlap(parts["tube-nest"], insertion_path) > 1e-4:
            raise ValueError("tube nest blocks a retainer screw insertion path")
    for angle in TUBE_ADJUSTER_ANGLES:
        adjuster_path = _radial_cylinder(
            angle,
            OUTER_COLLAR_OD / 2.0 + 0.02,
            TUBE_ADJUSTER_Z,
            M3_ADJUSTER_SHANK_D - 0.10,
            OUTER_COLLAR_OD / 2.0 - interface.TUBE_OD / 2.0 + 1.0,
        )
        if _overlap(parts["tube-nest"], adjuster_path) > 1e-4:
            raise ValueError("tube nest blocks a direct tube-adjuster screw path")

    # Printed pulley: a clearance groove for a 3.05 mm belt tooth root and
    # a printable land between grooves.
    opening = 2.0 * _groove_half_width(PULLEY_TIP_R)
    land = 2.0 * math.pi * PULLEY_TIP_R / interface.TABLE_PULLEY_TEETH - opening
    if opening < 3.5:
        raise ValueError(f"pulley groove opening is only {opening:.2f} mm")
    if land < 1.2:
        raise ValueError(f"pulley land between grooves is only {land:.2f} mm")
    if PULLEY_FLANGE_R < TABLE_PITCH_R + interface.belt_outer_offset() + 0.5:
        raise ValueError("pulley flanges do not stand above the belt back")

    # Belt plane: the belt sits on the purchased pulley's land, inside the
    # printed pulley's tooth zone, and under the carriage skin.
    if PULLEY_TOOTH_Z0 > BELT_Z0 or PULLEY_TOOTH_Z0 + PULLEY_TOOTH_H < BELT_Z1:
        raise ValueError("printed pulley tooth zone does not span the belt")
    if CARRIAGE_SKIN_Z0 - BELT_Z1 < 0.9:
        raise ValueError("carriage skin does not clear the belt's upper edge")
    if CARRIAGE_SKIN_H < interface.MOTOR_PILOT_LENGTH:
        raise ValueError("carriage skin is thinner than the motor's face pilot")
    pilot_front_z = MOTOR_FACE_Z - interface.MOTOR_PILOT_LENGTH
    pilot_gap = pilot_front_z - MOTOR_PULLEY_Z1
    if abs(pilot_gap - MOTOR_PULLEY_PILOT_GAP) > 1e-6 or pilot_gap < 0.2:
        raise ValueError("purchased pulley lacks its running gap to the motor face pilot")
    shaft_engagement = MOTOR_PULLEY_Z1 - max(MOTOR_PULLEY_Z0, MOTOR_SHAFT_TIP_Z)
    if shaft_engagement < interface.MOTOR_PULLEY_LENGTH - 2.0:
        raise ValueError("purchased pulley has less than 18 mm of shaft engagement")
    dcut_top = MOTOR_SHAFT_TIP_Z + interface.MOTOR_SHAFT_DCUT_LENGTH
    set_screw_z = (MOTOR_LAND_Z0 + MOTOR_LAND_Z1) / 2.0
    if not MOTOR_SHAFT_TIP_Z <= set_screw_z <= dcut_top:
        raise ValueError("purchased pulley set-screw plane misses the shaft D-cut")

    # Motor carriage and tower.
    cradle_pilot_radial = (
        CARRIAGE_PILOT_D - interface.MOTOR_PILOT_DIAMETER
    ) / 2.0
    if not 0.15 <= cradle_pilot_radial <= 0.40:
        raise ValueError("carriage skin does not positively locate the face pilot")
    if (CARRIAGE_PILOT_D - MOTOR_PULLEY_FLANGE_D) / 2.0 < 1.0:
        raise ValueError("purchased pulley flanges cannot pass the carriage pilot hole")
    clamp_travel = (
        2.0 * CARRIAGE_WALL_Y0
        - interface.MOTOR_FRAME
        - 2.0 * MOTOR_CLAMP_PAD_Y
    ) / 2.0
    screw_projection = MOTOR_CLAMP_SCREW_LENGTH - MOTOR_CLAMP_INSERT_DEPTH
    if clamp_travel < 0.2 or screw_projection < clamp_travel + 0.5:
        raise ValueError("motor side pads cannot take up the frame clearance")
    # Motor mount: the two rear flange holes carry the motor, the countersink
    # is flush in the arms' underside so nothing protrudes toward the tower,
    # and the screw stops short of the tapped hole's bottom.
    if MOTOR_MOUNT_CSK_DEPTH > CARRIAGE_SKIN_Z0 - CARRIAGE_ARM_Z0:
        raise ValueError("motor mount countersink breaks through the carriage arms")
    mount_reach = MOTOR_MOUNT_SCREW_LENGTH - (MOTOR_FACE_Z - CARRIAGE_ARM_Z0)
    if not 3.0 <= mount_reach <= interface.MOTOR_MOUNT_TAPPED_DEPTH:
        raise ValueError(
            f"motor mount screws reach {mount_reach:.1f} mm into a "
            f"{interface.MOTOR_MOUNT_TAPPED_DEPTH:.1f} mm tapped hole"
        )
    if MOTOR_MOUNT_Y + MOTOR_MOUNT_CSK_D / 2.0 > interface.MOTOR_FRAME / 2.0:
        raise ValueError("motor mount countersinks fall outside the motor's flange")
    if (MOTOR_MOUNT_X + MOTOR_MOUNT_CSK_D / 2.0 > CARRIAGE_X1
            or MOTOR_MOUNT_Y + MOTOR_MOUNT_CSK_D / 2.0 > CARRIAGE_Y_HALF):
        raise ValueError("motor mount countersinks fall off the carriage")

    carriage_grip = MOTOR_FACE_Z - CARRIAGE_ARM_Z0 - M3_HEAD_DEPTH
    carriage_reach = CARRIAGE_SCREW_LENGTH - carriage_grip
    if not 3.0 <= carriage_reach <= TOWER_RAIL_INSERT_DEPTH - 0.5:
        raise ValueError("carriage screws have invalid rail insert engagement")
    if TOWER_RAIL_INSERT_Y + M3_INSERT_D / 2.0 > TOWER_Y_HALF - 1.5:
        raise ValueError("rail inserts break the tower's outer face")
    if TOWER_RAIL_INSERT_Y - M3_HEAD_D / 2.0 < CARRIAGE_WALL_Y1:
        raise ValueError("carriage screw heads land on the clamp walls")
    for x in TOWER_RAIL_INSERT_X:
        for mx, my in TOWER_MOUNT_POINTS:
            if abs(mx - x) < (M5_HEAD_D + M3_INSERT_D) / 2.0 + 1.0 and \
                    abs(abs(my) - TOWER_RAIL_INSERT_Y) < (M5_HEAD_D + M3_INSERT_D) / 2.0 + 1.0:
                raise ValueError("a rail insert meets an M5 access hole")
    if MOTOR_CENTER_MIN - CARRIAGE_WALL_X_HALF - PLATTER_R < 0.5:
        raise ValueError("motor overhangs the platter")
    carriage_to_nest = (
        CARRIAGE_X0 - (MOTOR_CENTER_NOMINAL - MOTOR_CENTER_MIN) - NEST_OD / 2.0
    )
    if carriage_to_nest < 5.0:
        raise ValueError("motor carriage approaches the tube nest too closely")
    if TOWER_X0 <= PLATTER_R:
        raise ValueError("motor tower stands over the platter")
    if CARRIAGE_X1 + (MOTOR_CENTER_MAX - MOTOR_CENTER_NOMINAL) > TOWER_X1 + 5.0:
        raise ValueError("carriage overhangs the tower at full tension")
    wrap_back_x = MOTOR_CENTER_MAX + MOTOR_PITCH_R + interface.belt_outer_offset()
    if TOWER_REAR_X0 - wrap_back_x < 1.5:
        raise ValueError("tower rear wall crowds the belt wrap at full tension")

    if _overlap(parts["motor-carriage"], parts["turntable"]) > 1e-4:
        raise ValueError("motor carriage intersects the turntable")
    if _overlap(parts["motor-tower"], parts["turntable"]) > 1e-4:
        raise ValueError("motor tower intersects the turntable")
    if _overlap(parts["motor-tower"], parts["base"]) > 1e-4:
        raise ValueError("motor tower intersects the base")

    carriage_offsets = {
        MOTOR_CENTER_MIN: MOTOR_CENTER_MIN - MOTOR_CENTER_NOMINAL,
        MOTOR_CENTER_NOMINAL: 0.0,
        MOTOR_CENTER_MAX: MOTOR_CENTER_MAX - MOTOR_CENTER_NOMINAL,
    }
    for center, offset in carriage_offsets.items():
        motor_proxy = build_motor_proxy(center)
        pulley_proxy = build_motor_pulley_proxy(center)
        carriage = parts["motor-carriage"].translate((offset, 0.0, 0.0))
        belt = _belt_solid(center, BELT_Z0, BELT_Z1)
        belt_margin = _belt_solid(center, BELT_Z0, BELT_Z1, 1.5)
        if _overlap(motor_proxy, pulley_proxy) > 1e-4:
            raise ValueError("purchased pulley intersects the motor face pilot")
        for fixed_name, fixed_part in (
            ("motor carriage", carriage),
            ("motor tower", parts["motor-tower"]),
        ):
            if _overlap(fixed_part, motor_proxy) > 1e-4:
                raise ValueError(f"{fixed_name} intersects the purchased motor")
            if _overlap(fixed_part, pulley_proxy) > 1e-4:
                raise ValueError(f"{fixed_name} intersects the purchased 20T pulley")
            if _overlap(fixed_part, belt) > 1e-4:
                raise ValueError(f"{fixed_name} intersects the belt at centre {center:.1f}")
            if _overlap(fixed_part, belt_margin) > 1e-4:
                raise ValueError(
                    f"{fixed_name} is within 1.5 mm of the belt at centre {center:.1f}"
                )
        mount_screws = _motor_mount_screws(offset)
        if _overlap(mount_screws, belt) > 1e-4:
            raise ValueError(
                f"motor mount screws intersect the belt at centre {center:.1f}"
            )
        if _overlap(mount_screws, motor_proxy) < 1.0:
            raise ValueError("motor mount screws do not enter the motor's flange")
        for name in ("base", "ground-tower", "ground-arm", "ground-shoe", "spool",
                     "race-ring", "ball-cage"):
            if _overlap(parts[name], belt) > 1e-4:
                raise ValueError(f"{name} intersects the belt at centre {center:.1f}")
        nest = parts["tube-nest"].translate((0.0, 0.0, NEST_SEAT_Z))
        if _overlap(nest, belt) > 1e-4 or _overlap(nest, motor_proxy) > 1e-4:
            raise ValueError("tube nest meets the belt or motor")
        if _overlap(carriage, parts["motor-tower"]) > 1e-4:
            raise ValueError("motor carriage intersects the motor tower")
        if _overlap(pulley_proxy, parts["turntable"]) > 1e-4:
            raise ValueError("purchased 20T pulley intersects the turntable")

    ground_preload_min = (
        GROUND_HOLDER_BACK_FACE_X
        + GROUND_SHOE_MIN_T
        + interface.TUBE_OD / 2.0
    )
    ground_preload_max = (
        GROUND_HOLDER_BACK_FACE_X
        + GROUND_SHOE_MAX_T
        + interface.TUBE_OD / 2.0
    )
    if ground_preload_min < 0.5 or ground_preload_max > 2.0:
        raise ValueError(
            "ground shoe stock tolerance gives "
            f"{ground_preload_min:.2f}--{ground_preload_max:.2f} mm preload"
        )
    ground_preload = (
        GROUND_HOLDER_BACK_FACE_X
        + GROUND_SHOE_T
        + interface.TUBE_OD / 2.0
    )
    flexure_free_length = -GROUND_NOSE_Y / 2.0 - GROUND_PAD_Y1
    flexure_surface_strain = (
        1.5 * GROUND_BEAM_T * ground_preload / flexure_free_length**2
    )
    if flexure_surface_strain > 0.01:
        raise ValueError("ground flexure exceeds 1% nominal outer-fibre strain")
    if _overlap(parts["ground-arm"], parts["ground-shoe"]) > 1e-4:
        raise ValueError("ground arm consumes the copper-shoe fit clearance")
    tube_proxy = build_tube_proxy()
    if _overlap(parts["ground-arm"], tube_proxy) > 1e-4:
        raise ValueError("ground arm reaches the tube before its copper shoe")
    if _overlap(parts["ground-shoe"], tube_proxy) <= 1e-4:
        raise ValueError("ground shoe has no nominal preload into the tube")
    clamp_tip_reach = GROUND_SHOE_CLAMP_SCREW_LENGTH - GROUND_HOLDER_CLAMP_T
    if clamp_tip_reach < 2.0 * GROUND_SHOE_SIDE_CLEARANCE:
        raise ValueError("ground-shoe clamp screw cannot take up the side clearance")
    if GROUND_SHOE_CLAMP_INSERT_DEPTH > GROUND_HOLDER_CLAMP_T - 1.0:
        raise ValueError("ground-shoe clamp insert lacks a closed end")
    clamp_tip_edge = GROUND_SHOE_CLAMP_SHANK_D / 2.0 + 1.0
    if not (
        GROUND_HOLDER_BACK_FACE_X + clamp_tip_edge
        < GROUND_SHOE_CLAMP_X
        < GROUND_HOLDER_BACK_FACE_X + GROUND_SHOE_MIN_T - clamp_tip_edge
    ):
        raise ValueError("ground-shoe clamp screw misses the stock edge")
    clamp_screw = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            1.5,
            GROUND_SHOE_CLAMP_SCREW_LENGTH,
            cq.Vector(
                GROUND_SHOE_CLAMP_X,
                GROUND_HOLDER_CLAMP_OUTER_Y,
                GROUND_SHOE_CLAMP_Z,
            ),
            cq.Vector(0.0, 1.0, 0.0),
        )
    )
    if _overlap(parts["ground-arm"], clamp_screw) > 1e-4:
        raise ValueError("ground arm blocks its shoe-clamp screw")
    if _overlap(parts["ground-shoe"], clamp_screw) <= 1e-4:
        raise ValueError("ground-shoe clamp screw cannot reach the copper edge")
    insertion_sweep = (
        cq.Workplane(
            "XY",
            origin=(
                (GROUND_SHOE_BACK_X + GROUND_SHOE_FRONT_X) / 2.0,
                0.0,
                GROUND_SHOE_Z0,
            ),
        )
        .box(
            GROUND_SHOE_FRONT_X - GROUND_SHOE_BACK_X,
            GROUND_SHOE_Y,
            GROUND_SHOE_Z + 20.0,
            centered=(True, True, False),
        )
    )
    if _overlap(parts["ground-arm"], insertion_sweep) > 1e-4:
        raise ValueError("ground arm blocks the copper shoe's top-down insertion path")
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
    assembly.add(parts["motor-carriage"], name="motor-carriage", color=M_PETGF_BLACK)
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
    assembly.add(parts["race-ring"], name="upper-race-ring", color=M_PETGF_BLACK)
    assembly.add(parts["ball-cage"], name="ball-cage", color=M_PETGF_BLACK)
    assembly.add(parts["spool"], name="spool", color=M_PETGF_BLACK)
    assembly.add(
        parts["tube-nest"],
        name="tube-nest",
        color=M_PETGF_BLACK,
        loc=cq.Location(cq.Vector(0.0, 0.0, NEST_SEAT_Z)),
    )
    assembly.add(build_balls_proxy(), name="10mm-pp-balls", color=M_TPU_BLACK)
    assembly.add(build_motor_proxy(), name="23hs30-2804s", color=M_STAINLESS)
    assembly.add(build_motor_pulley_proxy(), name="20t-htd5m-pulley", color=M_ALUMINIUM)
    assembly.add(build_belt_proxy(), name="550-5m-15-belt", color=M_TPU_BLACK)
    assembly.add(build_tube_proxy(), name="5in-316l-tube", color=M_STAINLESS)
    return assembly


def main():
    parts = selftest()
    outputs = {
        "base": "weld-rotator-base.step",
        "base-foot": "weld-rotator-base-foot.step",
        "turntable": "weld-rotator-turntable-90t.step",
        "race-ring": "weld-rotator-race-ring.step",
        "spool": "weld-rotator-spool.step",
        "pulley-coupon": "weld-rotator-pulley-coupon.step",
        "ball-cage": "weld-rotator-ball-cage.step",
        "tube-nest": "weld-rotator-tube-nest.step",
        "motor-tower": "weld-rotator-motor-tower.step",
        "motor-carriage": "weld-rotator-motor-carriage.step",
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
    mount_reach = MOTOR_MOUNT_SCREW_LENGTH - (MOTOR_FACE_Z - CARRIAGE_ARM_Z0)
    variables = {
        "WR_BASE_X": f"{BASE_X:.0f}",
        "WR_BASE_Y": f"{BASE_Y:.0f}",
        "WR_BASE_Z": f"{BASE_Z:.0f}",
        "WR_BASE_CLEARANCE": f"{BASE_FOOT_H:.0f}",
        "WR_SERVICE_BORE": f"{SERVICE_BORE_D:.0f}",
        "WR_SPOOL_POCKET": f"{SPOOL_POCKET_D:.0f}",
        "WR_BALLS": f"{BALL_COUNT}",
        "WR_BALL_D": f"{BALL_D:.0f}",
        "WR_BALL_RACE": f"{2.0 * BALL_RACE_R:.0f}",
        "WR_BALL_PITCH": f"{ball_pitch:.1f}",
        "WR_RACE_RING_H": f"{RACE_RING_H:.0f}",
        "WR_TABLE_TEETH": f"{interface.TABLE_PULLEY_TEETH}",
        "WR_MOTOR_TEETH": f"{interface.MOTOR_PULLEY_TEETH}",
        "WR_RATIO": f"{interface.drive_ratio():.1f}:1",
        "WR_CENTER": f"{interface.belt_center_distance():.1f}",
        "WR_WRAP": f"{interface.small_pulley_wrap_degrees():.1f}°",
        "WR_PULLEY_OPENING": f"{2.0 * _groove_half_width(PULLEY_TIP_R):.1f}",
        "WR_BELT_Z0": f"{BELT_Z0:.1f}",
        "WR_BELT_Z1": f"{BELT_Z1:.1f}",
        "WR_MOTOR_FACE_Z": f"{MOTOR_FACE_Z:.2f}",
        "WR_PULLEY_PILOT_GAP": f"{MOTOR_PULLEY_PILOT_GAP:.2f}",
        "WR_PULLEY_OVERHANG": f"{MOTOR_PULLEY_SHAFT_OVERHANG:.2f}",
        "WR_LAND_SKIN_CLEAR": f"{CARRIAGE_SKIN_Z0 - BELT_Z1:.2f}",
        "WR_SKIN_H": f"{CARRIAGE_SKIN_H:.0f}",
        "WR_MOTOR_MOUNT_SCREW": f"{MOTOR_MOUNT_SCREW_LENGTH:.0f}",
        "WR_MOTOR_MOUNT_REACH": f"{mount_reach:.1f}",
        "WR_MOTOR_MOUNT_TAPPED": f"{interface.MOTOR_MOUNT_TAPPED_DEPTH:.1f}",
        "WR_MOTOR_MOUNT_MARGIN": f"{interface.MOTOR_MOUNT_TAPPED_DEPTH - mount_reach:.1f}",
        "WR_PULLEY_HANG": f"{CARRIAGE_ARM_Z0 - MOTOR_PULLEY_Z0:.2f}",
        "WR_PILOT_OD": f"{PILOT_OD:.2f}",
        "WR_PILOT_H": f"{PILOT_H:.1f}",
        "WR_PILOT_CLEAR": f"{pilot_clearance:.2f}",
        "WR_OUTER_BORE": f"{OUTER_BORE_D:.2f}",
        "WR_OUTER_CLEAR": f"{outer_clearance:.2f}",
        "WR_RECESS": f"{interface.ENDCAP_RECESS:.2f}",
        "WR_NEST_OD": f"{NEST_OD:.0f}",
        "WR_NEST_RETAINER_ACCESS": f"{NEST_RETAINER_ACCESS_D:.1f}",
        "WR_GROUND_BEAM_T": f"{GROUND_BEAM_T:.1f}",
        "WR_GROUND_SHOE_EXPOSED": f"{GROUND_SHOE_Z - GROUND_HOLDER_H:.0f}",
        "WR_GROUND_SHOE_T": f"{GROUND_SHOE_T:.0f}",
        "WR_GROUND_SHOE_W": f"{GROUND_SHOE_Y:.0f}",
        "WR_GROUND_SHOE_Z": f"{GROUND_SHOE_Z:.0f}",
        "WR_GROUND_ARM_TOP": f"{GROUND_SHOE_Z0 + GROUND_HOLDER_H:.0f}",
        "WR_TUBE_ADJUSTER_BORE": f"{M3_ADJUSTER_SHANK_D:.1f}",
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
            f"{name:14s} {bb.xlen:7.2f} × {bb.ylen:7.2f} × {bb.zlen:7.2f} mm  "
            f"{part.val().Volume() / 1000.0:8.1f} cm³"
        )


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        selftest()
        print("weld rotator selftest: pass")
    else:
        main()
