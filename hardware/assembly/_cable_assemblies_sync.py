"""Doc-sync driver for hardware/assembly/cable-assemblies.md.

Every conductor count in the schedule is a board connector's pin count, so the
board is the source: `<Jst name="Jn" ... count={N}>` for the XH wafers, and the
KF301 screw terminal's pinLabels for J10.
Preparation blanks use the AC wiring schedule's conservative lengths, taking
the longest populated leg for each ribbon pair.

Run: tools/cad-venv/bin/python hardware/assembly/_cable_assemblies_sync.py"""
import sys
from pathlib import Path
_here = Path(__file__).resolve().parent
_repo = next((p for p in _here.parents if (p / 'tools' / 'docgen').is_dir()))
_hw = next((p for p in _here.parents if p.name == 'hardware'))
sys.path.insert(0, str(_repo / 'tools'))
BOARD = _hw / 'pcb' / 'pcba' / 'pcba.tsx'

_assembly_doc_root = next(p for p in Path(__file__).resolve().parents if (p / "hardware/scripts").is_dir())
sys.path.insert(0, str(_assembly_doc_root / "hardware/assembly"))
from _rust_docs import evaluate as _evaluate, update as _update


def _inputs():
    return {
    }


def connector_pins():
    return _evaluate("cable-assemblies")["exports"]["connector_pins"]


def main():
    _update('cable-assemblies', _inputs())


if __name__ == "__main__":
    main()
