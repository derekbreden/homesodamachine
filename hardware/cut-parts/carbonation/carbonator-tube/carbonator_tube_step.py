'\nCarbonator tube — the 3D solid of the cut stock, for the welding fixture and for quotes.\n\nThe pressure vessel\'s barrel: 5" OD × 0.065" wall 316 stainless, cut square to\nlength. This is purchased tube (OnlineMetals #12498) cut to size and deburred,\nnot a fabricated part — there is no cut file and no drawing, because a saw and a\nlength are the whole of it. The solid exists so the tube is a model the viewer\ncan open on its own, the same as the end caps that close it.\n\nEvery dimension is read off `_carbonator_stock`, which the assembly also reads.\nNothing here is a second copy of a number.\n\nThe tube stands on the origin, ends square, as it lies on the saw — not at the\nz it occupies inside the shell. Its assembly placement is the cold core\'s to\nstate.\n\nUnits: millimetres.\n'
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('carbonator_tube_step', action="public-names")
    try:
        return _member('carbonator_tube_step', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('carbonator_tube_step', action="main")
