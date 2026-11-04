'One-piece ASA Aero bench float with an RC62 at its axial midplane.\n\nFrame: open guide bore on Z, flat print bottom at Z=0. The enclosed annular\npocket is filled with the magnet during a native layer pause.\n'
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('all_aero_float', action="public-names")
    try:
        return _member('all_aero_float', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('all_aero_float', action="main")
