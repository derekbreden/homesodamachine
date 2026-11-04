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

import argparse
import math
import sys
from pathlib import Path


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_repo = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_repo / "tools"))
sys.path.insert(0, str(_here.parent))
sys.path.insert(0, str(_hw / 'printed-parts/cadlib'))
import fits

from docgen import substitute_md, substitute_py_comments  # noqa: E402

import _rotator_interface as interface  # noqa: E402


if __name__ == "__main__":
    import _rust_part
    _rust_part.start()


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
REGISTER_SOCKET_DEPTH = REGISTER_H + 0.2
REGISTER_ROOF_H = (REGISTER_OD + REGISTER_SLIP - SERVICE_BORE_D) / 4.0
NEST_SCREW_R = 61.0
NEST_SCREW_D = 3.5
NEST_RETAINER_ANGLES = (0.0, 120.0, 240.0)
NEST_RETAINER_ACCESS_D = M3_HEAD_D
NEST_INSERT_D = 4.0
NEST_INSERT_DEPTH = 5.2
NEST_RETAINER_SCREW_LENGTH = 10.0

# Tube nest — the [4.5](WR_PILOT_H) pilot fits above a welded plate's
# [6.35](WR_RECESS) recess.  Three radial screws bear directly on the OD;
# the pilot carries the ID; the end face lands on the annular seat between them.
NEST_OD = 150.0
NEST_BASE_H = 10.0
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
M5_SHANK_D = fits.m5_thread_pass_dia
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
MOTOR_MOUNT_HEAD_D = 9.8
MOTOR_MOUNT_HEAD_CLEARANCE = 0.4
MOTOR_MOUNT_CSK_D = MOTOR_MOUNT_HEAD_D + MOTOR_MOUNT_HEAD_CLEARANCE
MOTOR_MOUNT_CSK_DEPTH = (MOTOR_MOUNT_CSK_D - M5_SHANK_D) / 2.0
MOTOR_MOUNT_SCREW_LENGTH = 20.0

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
GROUND_SHOE_BACK_X = GROUND_SHOE_FRONT_X - GROUND_SHOE_T
GROUND_SHOE_Y = 25.0
GROUND_SHOE_SIDE_CLEARANCE = 0.4
GROUND_SHOE_Z = 50.0
GROUND_HOLDER_SHELF_H = 3.0
GROUND_SHOE_Z0 = GROUND_TOP_Z + GROUND_HOLDER_SHELF_H
GROUND_HOLDER_H = 12.0
GROUND_HOLDER_BACK_T = 3.0
# The loaded tube seats the shoe's back face on this wall.  Across the
# delivered bar's 5.75--6.5 mm thickness window that leaves 0.75--1.5 mm of
# flexure preload; thickness variation therefore cannot open the contact.
GROUND_HOLDER_BACK_FACE_X = GROUND_SHOE_BACK_X
GROUND_HOLDER_FRONT_X = -64.0
GROUND_HOLDER_SIDE_T = 3.0
GROUND_HOLDER_CLAMP_T = 7.0
GROUND_HOLDER_SHELF_X0 = GROUND_HOLDER_BACK_FACE_X - GROUND_HOLDER_BACK_T
GROUND_HOLDER_CLAMP_INNER_Y = -(GROUND_SHOE_Y / 2.0 + GROUND_SHOE_SIDE_CLEARANCE)
GROUND_HOLDER_CLAMP_OUTER_Y = GROUND_HOLDER_CLAMP_INNER_Y - GROUND_HOLDER_CLAMP_T
GROUND_HOLDER_FIXED_INNER_Y = GROUND_SHOE_Y / 2.0 + GROUND_SHOE_SIDE_CLEARANCE
GROUND_HOLDER_FIXED_OUTER_Y = GROUND_HOLDER_FIXED_INNER_Y + GROUND_HOLDER_SIDE_T
GROUND_SHOE_CLAMP_SHANK_D = 3.4
GROUND_SHOE_CLAMP_INSERT_D = 4.0
GROUND_SHOE_CLAMP_INSERT_DEPTH = 5.2
GROUND_SHOE_CLAMP_SCREW_LENGTH = 8.0
GROUND_SHOE_CLAMP_X = GROUND_SHOE_FRONT_X - GROUND_SHOE_T / 2.0
GROUND_SHOE_CLAMP_Z = GROUND_SHOE_Z0 + GROUND_HOLDER_H / 2.0
GROUND_TEARDROP_ROOF_ANGLE = 36.0
GROUND_ARM_SHANK_D = 3.4
GROUND_ARM_INSERT_D = 4.0
GROUND_ARM_INSERT_DEPTH = 5.2


def _groove_half_width(radius: float) -> float:
    """Flank line of the clearance trapezoid, continued straight past both
    the tip and the root so the opening is not pinched by the overcut."""
    t = (radius - PULLEY_ROOT_R) / PULLEY_GROOVE_DEPTH
    return GROOVE_ROOT_HALF_W + (GROOVE_TIP_HALF_W - GROOVE_ROOT_HALF_W) * t


def numbers():
    """The authored dimensions, source material colors and display rule."""
    import _rust_part
    _rust_part.start()
    import _material_base
    from _payload_rules import LINEAR_DEFLECTION_RATIO
    from _mesh_payload import ANGULAR_DEFLECTION
    values = {key: value for key, value in vars(interface).items()
              if key.isupper() and isinstance(value, (int, float, tuple))}
    values.update({key: value for key, value in globals().items()
                   if key.isupper() and isinstance(value, (int, float, tuple))})
    # Deferred project colors expose the same stored linear RGBA as OCCT.
    from _materials import linear
    values["colors"] = {name: list(linear(getattr(_material_base, name)))
                        for name in ("M_ALUMINIUM", "M_COPPER", "M_PETGF_BLACK",
                                     "M_STAINLESS", "M_TPU_BLACK")}
    values["presentation_ratio"] = LINEAR_DEFLECTION_RATIO
    values["presentation_angle"] = ANGULAR_DEFLECTION
    return values


def _document():
    pilot_clearance = (interface.TUBE_ID - PILOT_OD) / 2.0
    outer_clearance = (OUTER_BORE_D - interface.TUBE_OD) / 2.0
    ball_pitch = 2.0 * math.pi * BALL_RACE_R / BALL_COUNT
    nest_reach = (
        NEST_RETAINER_SCREW_LENGTH - (NEST_BASE_H - M3_HEAD_DEPTH)
    )
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
        "WR_MOTOR_MOUNT_HEAD": f"{MOTOR_MOUNT_HEAD_D:.1f}",
        "WR_MOTOR_MOUNT_CSK": f"{MOTOR_MOUNT_CSK_D:.1f}",
        "WR_PULLEY_HANG": f"{CARRIAGE_ARM_Z0 - MOTOR_PULLEY_Z0:.2f}",
        "WR_PILOT_OD": f"{PILOT_OD:.2f}",
        "WR_PILOT_H": f"{PILOT_H:.1f}",
        "WR_PILOT_CLEAR": f"{pilot_clearance:.2f}",
        "WR_OUTER_BORE": f"{OUTER_BORE_D:.2f}",
        "WR_OUTER_CLEAR": f"{outer_clearance:.2f}",
        "WR_RECESS": f"{interface.ENDCAP_RECESS:.2f}",
        "WR_NEST_OD": f"{NEST_OD:.0f}",
        "WR_NEST_BASE_H": f"{NEST_BASE_H:.0f}",
        "WR_NEST_RETAINER_SCREW": f"{NEST_RETAINER_SCREW_LENGTH:.0f}",
        "WR_NEST_RETAINER_REACH": f"{nest_reach:.1f}",
        "WR_REGISTER_OD": f"{REGISTER_OD:.0f}",
        "WR_REGISTER_SOCKET_DEPTH": f"{REGISTER_SOCKET_DEPTH:.1f}",
        "WR_REGISTER_CAP": f"{NEST_BASE_H - REGISTER_SOCKET_DEPTH - REGISTER_ROOF_H:.1f}",
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


def main(output=None):
    import _rust_part
    out = Path(output) if output is not None else _here.parent
    out.mkdir(parents=True, exist_ok=True)
    result = _rust_part.cut("tooling", "weld-rotator", numbers(), out)
    _document()
    print(f"-> weld rotator: {len(result['files'])} files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    main(options.output)
