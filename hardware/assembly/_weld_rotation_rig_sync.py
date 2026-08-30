"""Update derived figures in hardware/assembly/weld-rotation-rig.md.

The weld path, printed pulley, purchased pulley and controller all reduce to
one circular interface. This script reads the same CadQuery-free interface as
the printable fixture and derives every speed, pulse count and lap time in the
assembly procedure from it.

Run: tools/cad-venv/bin/python hardware/assembly/_weld_rotation_rig_sync.py
"""

import math
import sys
from pathlib import Path


_here = Path(__file__).resolve().parent
_repo = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
_hw = next(p for p in _here.parents if p.name == "hardware")
_rotator = _hw / "printed-parts" / "fixtures" / "weld-rotator"
sys.path.insert(0, str(_repo / "tools"))
sys.path.insert(0, str(_hw / "cut-parts" / "carbonation" / "endcaps-circular"))
sys.path.insert(0, str(_here))
sys.path.insert(0, str(_rotator))

import _rotator_interface as interface  # noqa: E402
from _pressure_vessel_sync import carbonator_rod_len  # noqa: E402
from docgen import substitute_md  # noqa: E402
from endcap_circular_dxf import disc_diameter, disc_thickness, tube_id  # noqa: E402


MM_PER_IN = 25.4
TUBE_LENGTH = 6.0 * MM_PER_IN
ROD_DIAMETER = 0.125 * MM_PER_IN
DENSITY_316L = 7.98e-3  # g/mm³

WIRE_DIAMETER = 0.030 * MM_PER_IN
WIRE_FEED = 12.0
SPEEDS = (5, 6, 8, 10, 12, 15)


def fillet_leg(travel_mm_s: float) -> float:
    wire_area = math.pi * WIRE_DIAMETER ** 2 / 4.0
    return math.sqrt(2.0 * wire_area * WIRE_FEED / travel_mm_s)


def cylinder_mass(diameter: float, length: float) -> float:
    return math.pi * diameter ** 2 / 4.0 * length * DENSITY_316L


def rotating_masses() -> tuple[float, float]:
    tube = (
        math.pi / 4.0 * (interface.TUBE_OD ** 2 - interface.TUBE_ID ** 2)
        * TUBE_LENGTH * DENSITY_316L
    )
    plate = cylinder_mass(disc_diameter * MM_PER_IN,
                          disc_thickness * MM_PER_IN)
    rod = cylinder_mass(ROD_DIAMETER, carbonator_rod_len)
    return tube + plate, tube + 2.0 * plate + rod


def main():
    canonical_id = tube_id * MM_PER_IN
    if abs(canonical_id - interface.TUBE_ID) > 1e-6:
        raise ValueError(
            f"rotator tube ID {interface.TUBE_ID} disagrees with end-cap "
            f"geometry {canonical_id}"
        )

    mass_first, mass_second = rotating_masses()
    wire_area = math.pi * WIRE_DIAMETER ** 2 / 4.0
    overlap_length = (
        interface.bead_circumference() * interface.OVERLAP_DEGREES / 360.0
    )
    nominal_lap_s = (
        interface.bead_circumference()
        * (360.0 + interface.OVERLAP_DEGREES) / 360.0
        / interface.TRAVEL_NOMINAL
    )

    variables = {
        "BEAD_D": f"{interface.TUBE_ID:.2f} mm",
        "BEAD_C": f"{interface.bead_circumference():.2f} mm",
        "RECESS": f"{interface.ENDCAP_RECESS:.2f} mm",
        "SERVICE_BORE": f"{interface.SERVICE_BORE_DIAMETER:.0f} mm",
        "BASE_CLEARANCE": f"{interface.BASE_CLEARANCE:.0f} mm",
        "MASS_FIRST": f"{mass_first / 1000.0:.2f} kg",
        "MASS_SECOND": f"{mass_second / 1000.0:.2f} kg",
        "SPEED_MIN": f"{interface.TRAVEL_MIN:.0f} mm/s",
        "SPEED_NOM": f"{interface.TRAVEL_NOMINAL:.0f} mm/s",
        "SPEED_MAX": f"{interface.TRAVEL_MAX:.0f} mm/s",
        "RPM_WINDOW": (
            f"{interface.table_rpm(interface.TRAVEL_MIN):.3f}–"
            f"{interface.table_rpm(interface.TRAVEL_MAX):.3f} rpm"
        ),
        "RPM_NOM": f"{interface.table_rpm(interface.TRAVEL_NOMINAL):.3f} rpm",
        "MOTOR_RPM_NOM": f"{interface.motor_rpm(interface.TRAVEL_NOMINAL):.3f} rpm",
        "PULSE_HZ_NOM": f"{interface.pulse_hz(interface.TRAVEL_NOMINAL):.1f} Hz",
        "RATIO": f"{interface.drive_ratio():.1f}:1",
        "BELT_CENTER": f"{interface.belt_center_distance():.1f} mm",
        "SMALL_WRAP": f"{interface.small_pulley_wrap_degrees():.1f}°",
        "SMALL_WRAP_TEETH": (
            f"{interface.small_pulley_wrap_degrees() / 360.0 * interface.MOTOR_PULLEY_TEETH:.1f}"
        ),
        "TABLE_PULSES": f"{interface.table_pulses_per_rev():,}",
        "LAP_PULSES": (
            f"{interface.pulses_for_degrees(360.0 + interface.OVERLAP_DEGREES):,}"
        ),
        "INDEX_PULSES": f"{interface.pulses_for_degrees(45.0):,}",
        "TABLE_STEP_DEG": f"{360.0 / interface.table_pulses_per_rev():.3f}°",
        "TABLE_STEP_MM": (
            f"{interface.bead_circumference() / interface.table_pulses_per_rev():.3f} mm"
        ),
        "OVERLAP_DEG": f"{interface.OVERLAP_DEGREES:.0f}°",
        "OVERLAP_MM": f"{overlap_length:.1f} mm",
        "LAP_NOM": f"{nominal_lap_s:.1f} s",
        "WIRE_FEED": f"{WIRE_FEED:.0f} mm/s",
        "WIRE_AREA": f"{wire_area:.3f} mm²",
        "FILLET_NOM": f"{fillet_leg(interface.TRAVEL_NOMINAL):.2f} mm",
    }
    for speed in SPEEDS:
        variables[f"RPM_{speed}"] = f"{interface.table_rpm(speed):.3f}"
        variables[f"REV_{speed}"] = f"{interface.bead_circumference() / speed:.1f}"
        variables[f"LAP_{speed}"] = (
            f"{interface.bead_circumference() * (360.0 + interface.OVERLAP_DEGREES) / 360.0 / speed:.1f}"
        )
        variables[f"PULSE_{speed}"] = f"{interface.pulse_hz(speed):.1f}"
        variables[f"LEG_{speed}"] = f"{fillet_leg(speed):.2f}"

    substitute_md(_here / "weld-rotation-rig.md", variables)
    print(
        f"bead {interface.bead_circumference():.2f} mm; "
        f"nominal {interface.table_rpm(interface.TRAVEL_NOMINAL):.3f} rpm, "
        f"{interface.pulse_hz(interface.TRAVEL_NOMINAL):.1f} Hz, "
        f"{nominal_lap_s:.1f} s / "
        f"{interface.pulses_for_degrees(380):,} pulses"
    )


if __name__ == "__main__":
    main()
