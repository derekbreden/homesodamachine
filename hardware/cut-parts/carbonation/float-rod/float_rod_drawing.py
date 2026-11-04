'Finished carbonator guide rod: fixed cut length, tolerances and end finish.\n\nThe controlled cap spacing and conical-register tolerance basis are stated on\nthe sheet. All rod dimensions and fit assumptions come from float_rod_dimensions.\n'
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('float_rod_drawing', action="public-names")
    try:
        return _member('float_rod_drawing', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('float_rod_drawing', action="main")
