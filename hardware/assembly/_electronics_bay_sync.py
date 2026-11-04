"""Figure-sync entry point and checked relay GPIO names for electronics-bay.md.

The current mounting and wiring procedure uses its linked native geometry and
wire schedule directly. It contains no generated numeric figure markers."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = next((p for p in HERE.parents if (p / 'tools' / 'docgen').is_dir()))
sys.path.insert(0, str(ROOT / 'tools'))

_assembly_doc_root = next(p for p in Path(__file__).resolve().parents if (p / "hardware/scripts").is_dir())
sys.path.insert(0, str(_assembly_doc_root / "hardware/assembly"))
from _rust_docs import evaluate as _evaluate, update as _update


def _inputs():
    return {
    }


globals().update(_evaluate('electronics-bay', _inputs())["exports"])


def main():
    _update('electronics-bay', _inputs())


if __name__ == "__main__":
    main()
