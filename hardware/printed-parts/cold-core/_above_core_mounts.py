'Cold-core equipment mounts carried by the production above-core datums.\n\nCoordinates returned here belong to the top cap and lid before their installed\nhalf turn. Component mounting holes come from their native references; the\nappliance placement belongs to ``manifold-layout/above_core.py``.\n'
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('_above_core_mounts', action="public-names")
    try:
        return _member('_above_core_mounts', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('_above_core_mounts', action="main")
