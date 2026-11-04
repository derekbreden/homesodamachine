"""The 1 mm TPU ring between the machine display glass and its snap-retained cover.

The ring lies in the cover's local frame: X across, Y up the display plane and Z
out of the face. Its outer outline matches the glass and its inner outline the window.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "printed-parts/enclosure/enclosure"), str(_hardware / "printed-parts/cadlib")]
import _rust_part
_rust_part.start()
from _enclosure_compiled import compiled as _compiled

_rust_enclosure_module = 'display_gasket'

def __getattr__(name):
    if name == "__all__":
        return _compiled('display_gasket', action="public-names")
    if name.startswith("__"):
        raise AttributeError(name)
    try:
        return _compiled('display_gasket', action="get", path=(name,))
    except ValueError as error:
        raise AttributeError(name) from error

from _enclosure_compiled import install as _install
_install(_sys.modules[__name__])

if __name__ == "__main__":
    _compiled('display_gasket', action="main")
