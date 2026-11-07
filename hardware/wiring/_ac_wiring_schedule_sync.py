"""The AC wiring schedule (gauges and runs), computed by the Rust `assembly-docs` program.
`hardware/wiring/_run_lengths.py` reads it."""
import sys
from pathlib import Path
_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next((p for p in _here.parents if (p / 'tools' / 'docgen').is_dir())) / 'tools'))

_assembly_doc_root = next(p for p in Path(__file__).resolve().parents if (p / "hardware/scripts").is_dir())
sys.path.insert(0, str(_assembly_doc_root / "hardware/assembly"))
from _rust_docs import evaluate as _evaluate


def _inputs():
    return {
    }


globals().update(_evaluate('ac-wiring-schedule', _inputs())["exports"])
