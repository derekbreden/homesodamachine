"""Doc-sync driver for hardware/wiring/ac-wiring-schedule.md.

Run: tools/cad-venv/bin/python hardware/wiring/_ac_wiring_schedule_sync.py"""
import sys
from pathlib import Path
_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next((p for p in _here.parents if (p / 'tools' / 'docgen').is_dir())) / 'tools'))

_assembly_doc_root = next(p for p in Path(__file__).resolve().parents if (p / "hardware/scripts").is_dir())
sys.path.insert(0, str(_assembly_doc_root / "hardware/assembly"))
from _rust_docs import evaluate as _evaluate, update as _update


def _inputs():
    return {
    }


globals().update(_evaluate('ac-wiring-schedule', _inputs())["exports"])


def main():
    _update('ac-wiring-schedule', _inputs())


if __name__ == "__main__":
    main()
