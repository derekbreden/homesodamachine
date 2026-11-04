'Outer rectangular cup (floor + four perimeter walls) with a cylindrical boss at\nevery `attachment_stations` station and their heat-set insert pockets. Exterior\ncorners rounded; each corner boss seated in the corner with its ⌀ tangent to the\nexterior wall arc, two short webs filling to the flanking flat walls — the\ncylinder + corner-fill teardrop idiom of the reservoir pocket-corner supports.'
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('_outer_shell', action="public-names")
    try:
        return _member('_outer_shell', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('_outer_shell', action="main")
