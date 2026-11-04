"""Keep ASSE drain assembly dimensions tied to the production geometry."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for path in (ROOT / 'tools', ROOT / 'hardware/manifold-layout', ROOT / 'hardware/reference/neofit-drain-bulkhead', ROOT / 'hardware/printed-parts/enclosure/enclosure'):
    sys.path.insert(0, str(path))
from _enclosure_datums import install as _scalar_datums
_scalar_datums()
import _drain
import neofit_drain_bulkhead as bulkhead

_assembly_doc_root = next(p for p in Path(__file__).resolve().parents if (p / "hardware/scripts").is_dir())
sys.path.insert(0, str(_assembly_doc_root / "hardware/assembly"))
from _rust_docs import update as _update


def _inputs():
    return {
        '_drain.OD': _drain.OD,
        '_drain.ID': _drain.ID,
        '_drain.MIN_R': _drain.MIN_R,
        'bulkhead.THREAD_D': bulkhead.THREAD_D,
        'bulkhead.THREAD_PITCH': bulkhead.THREAD_PITCH,
        'bulkhead.PANEL_THREAD': bulkhead.PANEL_THREAD,
    }


def main():
    _update('asse-drain', _inputs())


if __name__ == "__main__":
    main()
