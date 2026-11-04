"""Shared physical interface for the cap-weld tube rotator.

This module is deliberately CadQuery-free. The printable geometry and weld
recipe synchronizer read these same dimensions; the controller's matching
constants are held by its native policy tests.
"""

import math



import pathlib as _reference_pathlib
_reference_hardware = next(p for p in _reference_pathlib.Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('_rotator_interface')
globals().update({name: _reference_values[name] for name in ('MM_PER_IN', 'TUBE_OD', 'TUBE_WALL', 'TUBE_ID', 'TUBE_LENGTH', 'ENDCAP_RECESS', 'SERVICE_BORE_DIAMETER', 'BASE_CLEARANCE', 'BELT_PITCH', 'BELT_PITCH_LENGTH', 'BELT_WIDTH', 'BELT_PITCH_LINE_OFFSET', 'BELT_TOOTH_HEIGHT', 'BELT_THICKNESS', 'MOTOR_PULLEY_TEETH', 'TABLE_PULLEY_TEETH', 'MOTOR_PULLEY_LENGTH', 'MOTOR_PULLEY_FLANGE_DIAMETER', 'MOTOR_PULLEY_FLANGE_LENGTH', 'MOTOR_PULLEY_LAND_LENGTH', 'MOTOR_FULL_STEPS', 'DRIVER_MICROSTEPS', 'MOTOR_PULSES_PER_REV', 'TRAVEL_MIN', 'TRAVEL_NOMINAL', 'TRAVEL_MAX', 'OVERLAP_DEGREES', 'MOTOR_FRAME', 'MOTOR_BODY_LENGTH', 'MOTOR_SHAFT_DIAMETER', 'MOTOR_SHAFT_LENGTH', 'MOTOR_SHAFT_DCUT_LENGTH', 'MOTOR_PILOT_DIAMETER', 'MOTOR_PILOT_LENGTH', 'MOTOR_MOUNT_SQUARE', 'MOTOR_MOUNT_HOLE_DIAMETER')})



# Both lower end-cap ports have to remain reachable while the already-welded
# end supports the second closure.  The feet hold this unobstructed passage
# above the bench.

# HTD 5M: the pitch line sits 0.5715 mm outside the pulley tip circle, the
# belt tooth stands 2.06 mm below it and the back 1.18 mm above it.

# Purchased uxcell 5M 20T pulley for 15 mm belt, 6.35 mm bore: two 2 mm
# flanges of Ø35 around a 16 mm land, 20 mm overall, no boss, two radial set
# screws in the toothed body.



# STEPPERONLINE 23HS30-2804S: 57 mm frame, 76.5 mm body, Ø6.35 × 21 mm
# shaft with a 15 mm D-cut, Ø38.1 × 1.6 mm face pilot, four Ø5.2 flange
# holes on a 47.14 mm square.


def pitch_diameter(teeth: int):
    return _reference_data('_rotator_interface', 'pitch_diameter', (teeth,), {})


def belt_inner_offset():
    'Belt tooth tips, measured inward from the pitch line.'
    return _reference_data('_rotator_interface', 'belt_inner_offset', (), {})


def belt_outer_offset():
    'Belt back, measured outward from the pitch line.'
    return _reference_data('_rotator_interface', 'belt_outer_offset', (), {})


def belt_center_distance():
    'Larger positive solution of the standard open-belt length equation.'
    return _reference_data('_rotator_interface', 'belt_center_distance', (), {})


def span_tangent_angle(center: float):
    "Angle, in radians from the centre line, of the radius to each span's\n    tangent point.  The same angle serves both pulleys of an open drive."
    return _reference_data('_rotator_interface', 'span_tangent_angle', (center,), {})


def small_pulley_wrap_degrees():
    return _reference_data('_rotator_interface', 'small_pulley_wrap_degrees', (), {})


def bead_circumference():
    return _reference_data('_rotator_interface', 'bead_circumference', (), {})


def table_rpm(travel_mm_s: float):
    return _reference_data('_rotator_interface', 'table_rpm', (travel_mm_s,), {})


def drive_ratio():
    return _reference_data('_rotator_interface', 'drive_ratio', (), {})


def motor_rpm(travel_mm_s: float):
    return _reference_data('_rotator_interface', 'motor_rpm', (travel_mm_s,), {})


def pulse_hz(travel_mm_s: float):
    return _reference_data('_rotator_interface', 'pulse_hz', (travel_mm_s,), {})


def table_pulses_per_rev():
    return _reference_data('_rotator_interface', 'table_pulses_per_rev', (), {})


def pulses_for_degrees(degrees: float):
    return _reference_data('_rotator_interface', 'pulses_for_degrees', (degrees,), {})
