"""Doc-sync driver for hardware/assembly/acceptance-and-burn-in.md.

Run: tools/cad-venv/bin/python hardware/assembly/_acceptance_and_burn_in_sync.py"""
import sys
from pathlib import Path
_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next((p for p in _here.parents if (p / 'tools' / 'docgen').is_dir())) / 'tools'))
from _firmware_and_commissioning_sync import gpio_relay2 as _fc_gpio_relay2
from _firmware_and_commissioning_sync import valve_count as _fc_valve_count
from _pressure_vessel_sync import carbonation_basis_c, secondary_regulator_pressure_psi

_assembly_doc_root = next(p for p in Path(__file__).resolve().parents if (p / "hardware/scripts").is_dir())
sys.path.insert(0, str(_assembly_doc_root / "hardware/assembly"))
from _rust_docs import evaluate as _evaluate, update as _update


def _inputs():
    return {
        'secondary_regulator_pressure_psi': secondary_regulator_pressure_psi,
        'carbonation_basis_c': carbonation_basis_c,
        '_fc_gpio_relay2': _fc_gpio_relay2,
        '_fc_valve_count': _fc_valve_count,
    }


globals().update(_evaluate('acceptance-and-burn-in', _inputs())["exports"])


def main():
    _update('acceptance-and-burn-in', _inputs())


if __name__ == "__main__":
    main()
