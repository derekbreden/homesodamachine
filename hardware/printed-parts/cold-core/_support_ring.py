"Annular ring sitting at the bottom of the foam-shell's central\nzone, holding the carbonator up by its outer rim. The ring's outer face sits\non the carbonator+coil envelope — inboard of the reservoir pockets' centerward\nwall, which stands off from it by the cylinder's foam blanket."
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('_support_ring', action="public-names")
    try:
        return _member('_support_ring', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('_support_ring', action="main")
