"""Doc-sync driver for hardware/assembly/firmware-and-commissioning.md.

Run: tools/cad-venv/bin/python hardware/assembly/_firmware_and_commissioning_sync.py"""
import sys
from pathlib import Path
_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next((p for p in _here.parents if (p / 'tools' / 'docgen').is_dir())) / 'tools'))
_hw = next((p for p in _here.parents if p.name == 'hardware'))
sys.path.insert(0, str(_hw / 'manifold-layout'))
sys.path.insert(0, str(_hw / 'printed-parts' / 'cadlib'))
sys.path.insert(0, str(_hw / 'printed-parts' / 'cold-core' / 'reservoir'))
sys.path.insert(0, str(_hw / 'wiring'))
sys.path.insert(0, str(_hw / 'printed-parts' / 'enclosure' / 'enclosure'))
from _enclosure_datums import install as _scalar_datums
_scalar_datums()
import manifold_layout as _ml
from reservoir import reservoir_count
import _ac_wiring_schedule_sync as _ac
_cold_policy = next((p for p in _here.parents if (p / 'firmware').is_dir())) / 'firmware' / 'lib' / 'machine_policy' / 'cold_policy.h'

_assembly_doc_root = next(p for p in Path(__file__).resolve().parents if (p / "hardware/scripts").is_dir())
sys.path.insert(0, str(_assembly_doc_root / "hardware/assembly"))
from _rust_docs import evaluate as _evaluate, update as _update


def _inputs():
    return {
        'manifold_stations': list(_ml.P),
        'reservoir_count': reservoir_count,
        '_ac.max_simultaneous_valves': _ac.max_simultaneous_valves,
        '_ac.board_peak_a': _ac.board_peak_a,
        '_ac.diaphragm_peak_a': _ac.diaphragm_peak_a,
        '_ac.psu_max_dc_a': _ac.psu_max_dc_a,
        '_ac.coincident_peak_a': _ac.coincident_peak_a,
    }


globals().update(_evaluate('firmware-and-commissioning', _inputs())["exports"])


def _constexpr(name):
    return _evaluate("firmware-and-commissioning", {"name": name}, operation="constexpr")["exports"]["value"]


def main():
    _update('firmware-and-commissioning', _inputs())


if __name__ == "__main__":
    main()
