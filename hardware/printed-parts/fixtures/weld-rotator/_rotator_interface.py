"""Shared physical interface for the cap-weld tube rotator.

This module is deliberately CadQuery-free. The printable geometry and weld
recipe synchronizer read these same dimensions; the controller's matching
constants are held by its native policy tests.
"""

import math


MM_PER_IN = 25.4

TUBE_OD = 5.0 * MM_PER_IN
TUBE_WALL = 0.065 * MM_PER_IN
TUBE_ID = TUBE_OD - 2.0 * TUBE_WALL
TUBE_LENGTH = 6.0 * MM_PER_IN
ENDCAP_RECESS = 0.25 * MM_PER_IN
ENDCAP_PORT_OFFSET = 0.75 * MM_PER_IN
ENDCAP_SERVICE_ENVELOPE = 1.0 * MM_PER_IN

# Both lower end-cap ports have to remain reachable while the already-welded
# end supports the second closure.  The feet hold this unobstructed passage
# above the bench.
SERVICE_BORE_DIAMETER = 90.0
BASE_CLEARANCE = 24.0

BELT_PITCH = 5.0
BELT_PITCH_LENGTH = 550.0
BELT_WIDTH = 15.0
MOTOR_PULLEY_TEETH = 20
TABLE_PULLEY_TEETH = 90

MOTOR_FULL_STEPS = 200
DRIVER_MICROSTEPS = 16
MOTOR_PULSES_PER_REV = MOTOR_FULL_STEPS * DRIVER_MICROSTEPS

TRAVEL_MIN = 5.0
TRAVEL_NOMINAL = 8.0
TRAVEL_MAX = 15.0
OVERLAP_DEGREES = 20.0

MOTOR_FRAME = 57.3
MOTOR_BODY_LENGTH = 76.5
MOTOR_SHAFT_DIAMETER = 6.35
MOTOR_SHAFT_LENGTH = 21.0
MOTOR_PILOT_DIAMETER = 38.1
MOTOR_PILOT_LENGTH = 1.6
MOTOR_MOUNT_SQUARE = 47.14
MOTOR_MOUNT_HOLE_DIAMETER = 5.2


def pitch_diameter(teeth: int) -> float:
    return teeth * BELT_PITCH / math.pi


def belt_center_distance() -> float:
    """Larger positive solution of the standard open-belt length equation."""
    large = pitch_diameter(TABLE_PULLEY_TEETH)
    small = pitch_diameter(MOTOR_PULLEY_TEETH)
    b = math.pi * (large + small) / 2.0 - BELT_PITCH_LENGTH
    c = (large - small) ** 2 / 4.0
    return (-b + math.sqrt(b * b - 8.0 * c)) / 4.0


def small_pulley_wrap_degrees() -> float:
    large = pitch_diameter(TABLE_PULLEY_TEETH)
    small = pitch_diameter(MOTOR_PULLEY_TEETH)
    center = belt_center_distance()
    return math.degrees(math.pi - 2.0 * math.asin((large - small) / (2.0 * center)))


def bead_circumference() -> float:
    return math.pi * TUBE_ID


def table_rpm(travel_mm_s: float) -> float:
    return travel_mm_s * 60.0 / bead_circumference()


def drive_ratio() -> float:
    return TABLE_PULLEY_TEETH / MOTOR_PULLEY_TEETH


def motor_rpm(travel_mm_s: float) -> float:
    return table_rpm(travel_mm_s) * drive_ratio()


def pulse_hz(travel_mm_s: float) -> float:
    return motor_rpm(travel_mm_s) * MOTOR_PULSES_PER_REV / 60.0


def table_pulses_per_rev() -> int:
    return int(MOTOR_PULSES_PER_REV * drive_ratio())


def pulses_for_degrees(degrees: float) -> int:
    return round(table_pulses_per_rev() * degrees / 360.0)
