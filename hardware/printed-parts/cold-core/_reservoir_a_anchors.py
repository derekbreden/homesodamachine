"Reservoir A's fore snap receiver and aft tied seats, in appliance millimetres.\n\nThe fore integral C2 pair shares `_reservoir_a_c2`. The aft open seats\nshare one filled stepped-height saddle within the casing footprint. Its tie witnesses\ndescribe routing, not purchased dimensions or physical acceptance.\n"
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('_reservoir_a_anchors', action="public-names")
    try:
        return _member('_reservoir_a_anchors', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('_reservoir_a_anchors', action="main")
