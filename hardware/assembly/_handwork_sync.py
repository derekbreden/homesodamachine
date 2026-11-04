"""Doc-sync driver for hardware/assembly/handwork.md.

Pins the carbonator rod to FR-CARB-01's finished length and tolerance, shared
with pressure-vessel.md. Reservoir rod lengths come from reservoir.py and are
shared with the reservoir's level-sensing.md.

Run: tools/cad-venv/bin/python hardware/assembly/_handwork_sync.py"""
import sys
from pathlib import Path
_here = Path(__file__).resolve().parent
_hw = next((p for p in _here.parents if p.name == 'hardware'))
sys.path.insert(0, str(_here))
sys.path.insert(0, str(next((p for p in _here.parents if p.name == 'hardware')) / 'printed-parts' / 'cold-core' / 'reservoir'))
sys.path.insert(0, str(next((p for p in _here.parents if (p / 'tools' / 'docgen').is_dir())) / 'tools'))
sys.path.insert(0, str(_hw / 'printed-parts' / 'enclosure' / 'enclosure'))
from _enclosure_datums import install as _scalar_datums
_scalar_datums()
from _pressure_vessel_sync import carbonator_rod_len, carbonator_rod_tolerance
import reservoir
from docgen import load_module
_coil_mandrel_gen = load_module('handwork_coil_mandrel_gen', _hw / 'printed-parts' / 'cold-core' / 'coil-mandrel' / 'coil_mandrel.py')
_coil_gen = load_module('handwork_coil_gen', _hw / 'cold-core-layout' / '_coil.py')

_assembly_doc_root = next(p for p in Path(__file__).resolve().parents if (p / "hardware/scripts").is_dir())
sys.path.insert(0, str(_assembly_doc_root / "hardware/assembly"))
from _rust_docs import evaluate as _evaluate, update as _update


def _inputs():
    return {
        'carbonator_rod_len': carbonator_rod_len,
        'carbonator_rod_tolerance': carbonator_rod_tolerance,
        'reservoir.reservoir_rod_len': reservoir.reservoir_rod_len,
        '_coil_gen.PITCH': _coil_gen.PITCH,
        '_coil_gen.wrap_length()': _coil_gen.wrap_length(),
        "_coil_mandrel_gen.stub_allowance['inlet']": _coil_mandrel_gen.stub_allowance['inlet'],
        "_coil_mandrel_gen.stub_allowance['outlet']": _coil_mandrel_gen.stub_allowance['outlet'],
    }


globals().update(_evaluate('handwork', _inputs())["exports"])


def main():
    _update('handwork', _inputs())


if __name__ == "__main__":
    main()
