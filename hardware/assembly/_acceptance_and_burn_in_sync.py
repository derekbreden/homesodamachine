"""Acceptance targets (the glass, the ratio, the dispense temperature), computed by the Rust
`assembly-docs` program. `tools/model/model.py` reads them."""
import sys
from pathlib import Path
_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next((p for p in _here.parents if (p / 'tools' / 'docgen').is_dir())) / 'tools'))
from _firmware_and_commissioning_sync import gpio_relay2 as _fc_gpio_relay2
from _firmware_and_commissioning_sync import valve_count as _fc_valve_count
from _pressure_vessel_sync import carbonation_basis_c, secondary_regulator_pressure_psi

_assembly_doc_root = next(p for p in Path(__file__).resolve().parents if (p / "hardware/scripts").is_dir())
sys.path.insert(0, str(_assembly_doc_root / "hardware/assembly"))
from _rust_docs import evaluate as _evaluate


def _inputs():
    return {
        'secondary_regulator_pressure_psi': secondary_regulator_pressure_psi,
        'carbonation_basis_c': carbonation_basis_c,
        '_fc_gpio_relay2': _fc_gpio_relay2,
        '_fc_valve_count': _fc_valve_count,
    }


globals().update(_evaluate('acceptance-and-burn-in', _inputs())["exports"])
