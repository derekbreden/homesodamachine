"B-fill tube passage and independent R14 bend holder, in appliance XYZ.\n\nThe R14 bend and 6.8 mm bore use the accepted holder's tube envelope.\nThe cap passage is circular, with 0.5 mm insertion lead-ins and a supported\nroof allowance toward print-up. The inlet extends to the front cap face;\nthe outlet turns directly into the reservoir seat.\n"
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('_reservoir_b_fill', action="public-names")
    try:
        return _member('_reservoir_b_fill', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('_reservoir_b_fill', action="main")
