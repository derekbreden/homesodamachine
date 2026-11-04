"""Black DATA trim, white raised lettering, continuous nameplate wings."""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "printed-parts/enclosure/enclosure"), str(_hardware / "printed-parts/cadlib")]
import _rust_part
_rust_part.start()
from _enclosure_compiled import compiled as _compiled

_rust_enclosure_module = 'data_ring'

def __getattr__(name):
    if name == "__all__":
        return _compiled('data_ring', action="public-names")
    if name.startswith("__"):
        raise AttributeError(name)
    try:
        return _compiled('data_ring', action="get", path=(name,))
    except ValueError as error:
        raise AttributeError(name) from error

from _enclosure_compiled import install as _install
_install(_sys.modules[__name__])

if __name__ == "__main__":
    _compiled('data_ring', action="main")
