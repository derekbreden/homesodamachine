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


import _rotator_interface as interface  # noqa: E402


if __name__ == "__main__":
    import _rust_part
    _rust_part.start()


# Stationary footprint — one H2C-bed print, with the tube axis left of centre
# so the motor and its tower remain on the same base.

def _reference_inputs(method='state'):
    values = {'fits': {'m5_thread_pass_dia': fits.m5_thread_pass_dia}}
    if method == 'numbers':
        from _materials import linear
        import _material_base
        from _payload_rules import LINEAR_DEFLECTION_RATIO
        from _mesh_payload import ANGULAR_DEFLECTION
        values.update(colors={name: list(linear(getattr(_material_base, name))) for name in (
            'M_ALUMINIUM', 'M_COPPER', 'M_PETGF_BLACK', 'M_STAINLESS', 'M_TPU_BLACK')},
            presentation_ratio=LINEAR_DEFLECTION_RATIO, presentation_angle=ANGULAR_DEFLECTION)
    return values

import pathlib as _reference_pathlib
_reference_hardware = next(p for p in _reference_pathlib.Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('weld_rotator', inputs=_reference_inputs())
globals().update({name: _reference_values[name] for name in ('BASE_X', 'BASE_Y', 'BASE_Z', 'BASE_CENTER_X', 'BASE_CORNER_R', 'BASE_X_MIN', 'BASE_X_MAX', 'BASE_Y_MIN', 'BASE_Y_MAX', 'BENCH_HOLE_D', 'BENCH_HOLE_MARGIN', 'BASE_FOOT_X', 'BASE_FOOT_Y', 'BASE_FOOT_H', 'BASE_FOOT_CENTERS', 'BASE_FOOT_SCREW_X', 'BASE_FOOT_INSERT_D', 'BASE_FOOT_INSERT_DEPTH', 'BASE_FOOT_SCREW_LENGTH', 'BALL_D', 'BALL_CLEARANCE', 'BALL_RACE_R', 'BALL_COUNT', 'BALL_CENTER_Z', 'RACE_CUT_R', 'CAGE_H', 'CAGE_INNER_R', 'CAGE_OUTER_R', 'CAGE_POCKET_D', 'RACE_RING_Z0', 'RACE_RING_H', 'RACE_RING_Z1', 'RACE_RING_INNER_R', 'RACE_RING_OUTER_R', 'RACE_RING_SCREW_R', 'RACE_RING_SCREW_ANGLES', 'RACE_RING_SCREW_LENGTH', 'RACE_RING_INSERT_DEPTH', 'CAGE_Z', 'PLATTER_R', 'PLATTER_Z0', 'PLATTER_Z1', 'SERVICE_BORE_D', 'M3_HEAD_D', 'M3_HEAD_DEPTH', 'M3_SHANK_D', 'M3_INSERT_D', 'SPOOL_HUB_OD', 'SPOOL_CLEARANCE_D', 'SPOOL_FLANGE_OD', 'SPOOL_POCKET_D', 'SPOOL_POCKET_H', 'SPOOL_FLANGE_Z0', 'SPOOL_FLANGE_H', 'SPOOL_HUB_Z0', 'SPOOL_GAP', 'SPOOL_SCREW_R', 'SPOOL_SCREW_ANGLES', 'SPOOL_SCREW_LENGTH', 'SPOOL_INSERT_DEPTH', 'TABLE_PITCH_R', 'MOTOR_PITCH_R', 'PITCH_LINE_OFFSET', 'PULLEY_TIP_R', 'PULLEY_GROOVE_DEPTH', 'PULLEY_ROOT_R', 'PULLEY_INNER_R', 'PULLEY_Z0', 'PULLEY_TOOTH_Z0', 'PULLEY_TOOTH_H', 'PULLEY_Z1', 'PULLEY_FLANGE_R', 'PULLEY_FLANGE_H', 'GROOVE_TIP_HALF_W', 'GROOVE_ROOT_HALF_W', 'GROOVE_OVERCUT', 'GROOVE_UNDERCUT', 'COUPON_TEETH', 'PEDESTAL_R', 'NEST_SEAT_Z', 'REGISTER_OD', 'REGISTER_H', 'REGISTER_SLIP', 'REGISTER_SOCKET_DEPTH', 'REGISTER_ROOF_H', 'NEST_SCREW_R', 'NEST_SCREW_D', 'NEST_RETAINER_ANGLES', 'NEST_RETAINER_ACCESS_D', 'NEST_INSERT_D', 'NEST_INSERT_DEPTH', 'NEST_RETAINER_SCREW_LENGTH', 'NEST_OD', 'NEST_BASE_H', 'NEST_OUTER_H', 'NEST_CENTER_BORE_D', 'PILOT_OD', 'PILOT_ID', 'PILOT_H', 'OUTER_BORE_D', 'OUTER_COLLAR_OD', 'TUBE_ADJUSTER_ANGLES', 'TUBE_ADJUSTER_INSERT_D', 'TUBE_ADJUSTER_INSERT_DEPTH', 'M3_ADJUSTER_SHANK_D', 'TUBE_ADJUSTER_Z', 'MOTOR_CENTER_NOMINAL', 'MOTOR_CENTER_MIN', 'MOTOR_CENTER_MAX', 'MOTOR_SLOT_R', 'MOTOR_PULLEY_PILOT_GAP', 'MOTOR_PULLEY_Z0', 'MOTOR_PULLEY_Z1', 'MOTOR_FACE_Z', 'MOTOR_LAND_Z0', 'MOTOR_LAND_Z1', 'BELT_Z0', 'BELT_Z1', 'MOTOR_SHAFT_TIP_Z', 'MOTOR_PULLEY_SHAFT_OVERHANG', 'MOTOR_PULLEY_CORE_D', 'MOTOR_PULLEY_FLANGE_D', 'TOWER_X0', 'TOWER_X1', 'TOWER_Y_HALF', 'TOWER_FOOT_Y0', 'TOWER_RAIL_Y0', 'TOWER_Z0', 'TOWER_FOOT_Z1', 'TOWER_Z1', 'TOWER_REAR_X0', 'TOWER_MOUNT_POINTS', 'TOWER_RAIL_INSERT_X', 'TOWER_RAIL_INSERT_Y', 'TOWER_RAIL_INSERT_DEPTH', 'M5_SHANK_D', 'M5_HEAD_D', 'M5_HEAD_DEPTH', 'M5_INSERT_D', 'M5_INSERT_DEPTH', 'CARRIAGE_X0', 'CARRIAGE_X1', 'CARRIAGE_Y_HALF', 'CARRIAGE_ARM_Z0', 'CARRIAGE_SKIN_H', 'CARRIAGE_SKIN_Z0', 'CARRIAGE_PILOT_D', 'CARRIAGE_BELT_MARGIN', 'CARRIAGE_WALL_Y0', 'CARRIAGE_WALL_Y1', 'CARRIAGE_WALL_X_HALF', 'CARRIAGE_WALL_H', 'CARRIAGE_SCREW_LENGTH', 'MOTOR_MOUNT_X', 'MOTOR_MOUNT_Y', 'MOTOR_MOUNT_HEAD_D', 'MOTOR_MOUNT_HEAD_CLEARANCE', 'MOTOR_MOUNT_CSK_D', 'MOTOR_MOUNT_CSK_DEPTH', 'MOTOR_MOUNT_SCREW_LENGTH', 'MOTOR_CLAMP_PAD_X', 'MOTOR_CLAMP_PAD_Y', 'MOTOR_CLAMP_PAD_Z', 'MOTOR_CLAMP_SCREW_X', 'MOTOR_CLAMP_SCREW_Z', 'MOTOR_CLAMP_INSERT_DEPTH', 'MOTOR_CLAMP_SOCKET_D', 'MOTOR_CLAMP_SOCKET_DEPTH', 'MOTOR_CLAMP_SCREW_LENGTH', 'GROUND_BASE_POINTS', 'GROUND_FOOT_X0', 'GROUND_FOOT_X1', 'GROUND_FOOT_Y0', 'GROUND_FOOT_Y1', 'GROUND_FOOT_Z0', 'GROUND_FOOT_Z1', 'GROUND_POST_X0', 'GROUND_POST_X1', 'GROUND_POST_Y0', 'GROUND_POST_Y1', 'GROUND_TOP_Z', 'GROUND_ARM_H', 'GROUND_ARM_POINTS', 'GROUND_PAD_X0', 'GROUND_PAD_X1', 'GROUND_PAD_Y0', 'GROUND_PAD_Y1', 'GROUND_BEAM_CENTER_X', 'GROUND_BEAM_T', 'GROUND_BEAM_X0', 'GROUND_BEAM_X1', 'GROUND_BEAM_Y0', 'GROUND_BEAM_Y1', 'GROUND_NOSE_Y', 'GROUND_SPRING_FILLET_R', 'GROUND_SHOE_FRONT_X', 'GROUND_SHOE_T', 'GROUND_SHOE_MIN_T', 'GROUND_SHOE_BACK_X', 'GROUND_SHOE_Y', 'GROUND_SHOE_SIDE_CLEARANCE', 'GROUND_SHOE_Z', 'GROUND_HOLDER_SHELF_H', 'GROUND_SHOE_Z0', 'GROUND_HOLDER_H', 'GROUND_HOLDER_BACK_T', 'GROUND_HOLDER_BACK_FACE_X', 'GROUND_HOLDER_FRONT_X', 'GROUND_HOLDER_SIDE_T', 'GROUND_HOLDER_CLAMP_T', 'GROUND_HOLDER_SHELF_X0', 'GROUND_HOLDER_CLAMP_INNER_Y', 'GROUND_HOLDER_CLAMP_OUTER_Y', 'GROUND_HOLDER_FIXED_INNER_Y', 'GROUND_HOLDER_FIXED_OUTER_Y', 'GROUND_SHOE_CLAMP_SHANK_D', 'GROUND_SHOE_CLAMP_INSERT_D', 'GROUND_SHOE_CLAMP_INSERT_DEPTH', 'GROUND_SHOE_CLAMP_SCREW_LENGTH', 'GROUND_SHOE_CLAMP_X', 'GROUND_SHOE_CLAMP_Z', 'GROUND_TEARDROP_ROOF_ANGLE', 'GROUND_ARM_SHANK_D', 'GROUND_ARM_INSERT_D', 'GROUND_ARM_INSERT_DEPTH')})


# One large-diameter race carries thrust and radial load.  The balls are stock
# 10 mm polypropylene; the cage spaces 36 of them without carrying load.  The
# lower groove is in the base's top face; the upper groove is in a separate
# race ring, so both running surfaces are printed as top faces.

# Upper race ring: printed groove-up, then screwed groove-down to the flat
# underside of the platter.  Its groove face sits 5 mm above the base's.

# The moving disk's flat underside is its bed face: the race ring bolts to it
# and the spool hangs from it.  Its wide pitch radius is the angular datum.

# Spool: the hub and the lift-catch flange in one part, inserted from below
# through the base and screwed up into the platter.  The flange rim keeps a
# 1 mm running gap to the base shoulder so it catches lift without carrying
# running load.

# Printed 90T pulley.  Exact 5 mm pitch; the groove is a printable clearance
# trapezoid — mm at the tip circle — that accepts
# the belt tooth's 3.05 mm root and absorbs accumulated pitch error over the
# 45 engaged teeth.  The first belt-fit coupon is the acceptance gate before
# the complete turntable is printed.

# The central pedestal places the replaceable precision nest above the belt.

# Tube nest — the pilot fits above a welded plate's
# recess.  Three radial screws bear directly on the OD;
# the pilot carries the ID; the end face lands on the annular seat between them.

# The purchased belt fixes the exact nominal centre.  Slots only move the motor
# outward: belt installation occurs at the nominal end and tension is added by
# sliding away from the turntable.

# Belt plane.  The motor hangs face-down.  The purchased pulley's 16 mm land
# is centred in the printed pulley's tooth zone; its motor-side flange keeps a
# measured running gap to the motor's projecting face pilot.  The resulting
# 0.85 mm nominal overhang beyond the shaft end is intentional.

# Motor tower: two rails outside the belt's swept path, tied by a rear wall
# behind the pulley's wrap, on the base's four M5 stations.  The rail feet
# are wide enough to seat the M5 heads; above the belt's height the rails
# narrow away from the spans.  The carriage seats on the rail tops.

# Motor carriage: a 2 mm pilot skin under the whole face, arms that follow
# the belt's swept path with clearance, four slotted screws into the rail
# tops, and two side walls whose pads clamp the 57.3 mm frame.  The face
# pilot in the skin takes the belt tension; the pads only hold the motor down
# and square.

# The motor bolts to the carriage through its two rear flange holes.  The
# front pair of the 47.14 mm square falls inside the belt's swept path and
# stays open.  Heads recess flush into the arms' underside, so the motor and
# carriage are joined on the bench and go onto the tower as one piece.


# A stationary copper shoe gives the laser welder's continuity interlock a
# path that does not travel through the polymer bearing or wind a work cable
# around the vessel.  Its PET-GF arm is a replaceable in-plane leaf spring;
# the shoe is one 25 mm crosscut from the acquired nominal 6 x 50 mm
# (1/4 x 2 inch) C110 flat bar, stood with the stock width vertical.  The
# factory face bears on the tube and the cut edge is only a seated side.
# The loaded tube seats the shoe's back face on this wall.  Across the
# delivered bar's 5.75--6.5 mm thickness window that leaves 0.75--1.5 mm of
# flexure preload; thickness variation therefore cannot open the contact.


def _groove_half_width(radius: float):
    'Flank line of the clearance trapezoid, continued straight past both\n    the tip and the root so the opening is not pinched by the overcut.'
    return _reference_data('weld_rotator', '_groove_half_width', (radius,), {}, inputs=_reference_inputs())


def numbers():
    'The authored dimensions, source material colors and display rule.'
    return _reference_data('weld_rotator', 'numbers', (), {}, inputs=_reference_inputs('numbers'))


def main(output=None):
    import _rust_part
    out = Path(output) if output is not None else _here.parent
    out.mkdir(parents=True, exist_ok=True)
    result = _rust_part.cut("tooling", "weld-rotator", numbers(), out)
    print(f"-> weld rotator: {len(result['files'])} files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    main(options.output)
