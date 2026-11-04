"""Doc-sync driver for hardware/assembly/refrigerant-loop.md.

Run: tools/cad-venv/bin/python hardware/assembly/_refrigerant_loop_sync.py"""
import sys
from pathlib import Path
_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next((p for p in _here.parents if p.name == 'hardware')) / 'scripts'))
sys.path.insert(0, str(next((p for p in _here.parents if (p / 'tools' / 'docgen').is_dir())) / 'tools'))
from docgen import load_module
_coil_mandrel_gen = load_module('refrigerant_loop_coil_mandrel_gen', next((p for p in _here.parents if p.name == 'hardware')) / 'printed-parts' / 'cold-core' / 'coil-mandrel' / 'coil_mandrel.py')

_assembly_doc_root = next(p for p in Path(__file__).resolve().parents if (p / "hardware/scripts").is_dir())
sys.path.insert(0, str(_assembly_doc_root / "hardware/assembly"))
from _rust_docs import evaluate as _evaluate, update as _update


def _inputs():
    return {
        "_coil_mandrel_gen.stub_protrusion['inlet']": _coil_mandrel_gen.stub_protrusion['inlet'],
        "_coil_mandrel_gen.stub_protrusion['outlet']": _coil_mandrel_gen.stub_protrusion['outlet'],
    }


globals().update(_evaluate('refrigerant-loop', _inputs())["exports"])


def main():
    _update('refrigerant-loop', _inputs())


if __name__ == "__main__":
    main()
