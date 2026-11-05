'Verify the shared float datums against emitted vessel CAD.\n\nUpright geometry is checked over the whole translation range with bore play.\nPhysical sliding, expansion, immersion and directional reed switching are not\naccepted by this check. Run after the float/reservoir/end-cap generators.\n'
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('integration', action="public-names")
    try:
        return _member('integration', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('integration', action="main")
