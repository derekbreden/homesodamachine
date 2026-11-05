"""Relay GPIO names for the electronics bay, computed by the Rust `assembly-docs` program.
`hardware/scripts/check_pinmap.py` checks them against the pin map."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = next((p for p in HERE.parents if (p / 'tools' / 'docgen').is_dir()))
sys.path.insert(0, str(ROOT / 'tools'))

_assembly_doc_root = next(p for p in Path(__file__).resolve().parents if (p / "hardware/scripts").is_dir())
sys.path.insert(0, str(_assembly_doc_root / "hardware/assembly"))
from _rust_docs import evaluate as _evaluate


def _inputs():
    return {
    }


globals().update(_evaluate('electronics-bay', _inputs())["exports"])
