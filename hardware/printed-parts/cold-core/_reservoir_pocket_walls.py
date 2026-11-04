'Two reservoir pockets, one on each ±X side, as four-walled\nenclosures whose centerward wall is curved to clear the carbonator+coil\nenvelope. The −X pocket mirrors the +X pocket across YZ.'
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('_reservoir_pocket_walls', action="public-names")
    try:
        return _member('_reservoir_pocket_walls', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('_reservoir_pocket_walls', action="main")
