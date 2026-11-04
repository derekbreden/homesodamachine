"""Update derived figures in hardware/assembly/weld-rotation-rig.md.

The weld path, printed pulley, purchased pulley and controller all reduce to
one circular interface. This script reads the same CadQuery-free interface as
the printable fixture and derives every speed and pulse count in the assembly
procedure from it.

Run: tools/cad-venv/bin/python hardware/assembly/_weld_rotation_rig_sync.py"""
import sys
from pathlib import Path
_here = Path(__file__).resolve().parent
_repo = next((p for p in _here.parents if (p / 'tools' / 'docgen').is_dir()))
_hw = next((p for p in _here.parents if p.name == 'hardware'))
_rotator = _hw / 'printed-parts' / 'fixtures' / 'weld-rotator'
sys.path.insert(0, str(_repo / 'tools'))
sys.path.insert(0, str(_hw / 'cut-parts' / 'carbonation' / 'endcaps-circular'))
sys.path.insert(0, str(_here))
sys.path.insert(0, str(_rotator))
import _rotator_interface as interface
from _pressure_vessel_sync import carbonator_rod_len
from endcap_circular_dxf import disc_diameter, disc_thickness, tube_id

_assembly_doc_root = next(p for p in Path(__file__).resolve().parents if (p / "hardware/scripts").is_dir())
sys.path.insert(0, str(_assembly_doc_root / "hardware/assembly"))
from _rust_docs import evaluate as _evaluate, update as _update


def _inputs():
    return {
        'interface.TUBE_OD': interface.TUBE_OD,
        'interface.TUBE_ID': interface.TUBE_ID,
        'disc_diameter': disc_diameter,
        'disc_thickness': disc_thickness,
        'carbonator_rod_len': carbonator_rod_len,
        'tube_id': tube_id,
        'interface.bead_circumference()': interface.bead_circumference(),
        'interface.OVERLAP_DEGREES': interface.OVERLAP_DEGREES,
        'interface.ENDCAP_RECESS': interface.ENDCAP_RECESS,
        'interface.SERVICE_BORE_DIAMETER': interface.SERVICE_BORE_DIAMETER,
        'interface.BASE_CLEARANCE': interface.BASE_CLEARANCE,
        'interface.TRAVEL_MIN': interface.TRAVEL_MIN,
        'interface.TRAVEL_NOMINAL': interface.TRAVEL_NOMINAL,
        'interface.TRAVEL_MAX': interface.TRAVEL_MAX,
        'interface.table_rpm(interface.TRAVEL_MIN)': interface.table_rpm(interface.TRAVEL_MIN),
        'interface.table_rpm(interface.TRAVEL_MAX)': interface.table_rpm(interface.TRAVEL_MAX),
        'interface.table_rpm(interface.TRAVEL_NOMINAL)': interface.table_rpm(interface.TRAVEL_NOMINAL),
        'interface.motor_rpm(interface.TRAVEL_NOMINAL)': interface.motor_rpm(interface.TRAVEL_NOMINAL),
        'interface.pulse_hz(interface.TRAVEL_NOMINAL)': interface.pulse_hz(interface.TRAVEL_NOMINAL),
        'interface.drive_ratio()': interface.drive_ratio(),
        'interface.belt_center_distance()': interface.belt_center_distance(),
        'interface.small_pulley_wrap_degrees()': interface.small_pulley_wrap_degrees(),
        'interface.MOTOR_PULLEY_TEETH': interface.MOTOR_PULLEY_TEETH,
        'interface.table_pulses_per_rev()': interface.table_pulses_per_rev(),
        'interface.pulses_for_degrees(45.0)': interface.pulses_for_degrees(45.0),
        'pulse_hz_per_speed': {speed: interface.pulse_hz(speed) for speed in SPEEDS},
        'table_rpm_per_speed': {speed: interface.table_rpm(speed) for speed in SPEEDS},
    }


globals().update(_evaluate('weld-rotation-rig', operation='settings')["exports"])
globals().update(_evaluate('weld-rotation-rig', _inputs())["exports"])


def fillet_leg(travel_mm_s):
    return _evaluate("weld-rotation-rig", {"travel_mm_s": travel_mm_s}, operation="fillet_leg")["exports"]["value"]


def cylinder_mass(diameter, length):
    return _evaluate("weld-rotation-rig", {"diameter": diameter, "length": length}, operation="cylinder_mass")["exports"]["value"]


def rotating_masses():
    return tuple(_evaluate("weld-rotation-rig", _inputs())["exports"]["rotating_masses"])


def main():
    _update('weld-rotation-rig', _inputs())


if __name__ == "__main__":
    main()
