'The purchased hardware inside the cold core, as solids.\n\nEvery body here is a PARAMETRIC STAND-IN built to its catalog envelope. What each one owes the\narrangement is where its mouths are and how much room it takes; what it does not owe is a\nthread form or a casting radius. Each is built from the two or three figures the layout reads\noff it — the mating dimension, the reach, the envelope — and each of those figures carries its\nsource in its own comment.\n\nWHAT A FITTING IS FOR, in this file: the mouth. Each builder hands back the point and axis a\nline lands on, and the assembly routes to that. A fitting that moves carries its line with it.\n'
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('_fittings', action="public-names")
    try:
        return _member('_fittings', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('_fittings', action="main")
