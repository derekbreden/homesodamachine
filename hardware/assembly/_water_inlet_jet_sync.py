"""Update water-inlet jet trial figures from the nominal CAD dimensions.

Run: tools/cad-venv/bin/python hardware/assembly/_water_inlet_jet_sync.py"""
import sys
from pathlib import Path
_here = Path(__file__).resolve().parent
_repo = next((p for p in _here.parents if (p / 'tools' / 'docgen').is_dir()))
_hw = next((p for p in _here.parents if p.name == 'hardware'))
sys.path.insert(0, str(_repo / 'tools'))
sys.path.insert(0, str(_hw / 'cold-core-layout'))
from _water_inlet_jet import JET_CAP_D, JET_CAP_T, JET_PASSAGE_D

_assembly_doc_root = next(p for p in Path(__file__).resolve().parents if (p / "hardware/scripts").is_dir())
sys.path.insert(0, str(_assembly_doc_root / "hardware/assembly"))
from _rust_docs import evaluate as _evaluate, update as _update


def _inputs():
    return {
        'JET_PASSAGE_D': JET_PASSAGE_D,
        'JET_CAP_D': JET_CAP_D,
        'JET_CAP_T': JET_CAP_T,
    }


globals().update(_evaluate('water-inlet-jet', _inputs())["exports"])


def main():
    _update('water-inlet-jet', _inputs())


if __name__ == "__main__":
    main()
