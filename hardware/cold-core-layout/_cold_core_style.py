"The cold core's exact viewer colours, without building its geometry.\n\nThe cold-core producer and the scene composer meet at a mesh payload.  RGB is carried by that\npayload because it is part of the STEP/viewer surface; alpha is a material fact that STEP does\nnot carry.  Both sides therefore read the same constants here.  Importing this module creates\ncolours and nothing else: no STEP is opened and no CadQuery solid is made.\n"
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('_cold_core_style', action="public-names")
    try:
        return _member('_cold_core_style', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('_cold_core_style', action="main")
