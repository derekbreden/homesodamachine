"Candidate inlet-jet dimensions, shared by the nominal model and fabrication procedure.\n\nThese are fabrication targets for the purchased 316 rod. They do not establish the\nelbow's measured bore, available weld land, installed projection or qualified joint.\n"
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('_water_inlet_jet', action="public-names")
    try:
        return _member('_water_inlet_jet', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('_water_inlet_jet', action="main")
