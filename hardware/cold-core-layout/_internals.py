"What stands inside the carbonator and inside each pocket: the inlet jet, the\nlevel-sensing columns and the two 1-wire probes.\n\nEvery station here is read off the part that owns it. The reservoir rod is at `reservoir.py`'s\nown `rod_position_x` / `rod_position_y`; the reed column stands in the channel\n`_reed_channels` carves; the carbonator's two reeds sit at the heights `reed_bridge` cuts its\npockets at; the inlet jet is at the top water elbow's male tip.\n\nTHE ONE SET OF STATIONS THIS FILE STRIKES ITSELF is where each reservoir's four reeds sit\nalong its column. `level-sensing.md` states the float's useful travel and the pitch that\nspans it — the soldering is what fixes them on the real column — so `reservoir_reed_z` lays\nfour at that pitch across that travel, and `report` prints what it laid.\n"
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('_internals', action="public-names")
    try:
        return _member('_internals', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('_internals', action="main")
