"Finished reservoir guide rod; common part for channels A and B.\n\nNominal dimensions are imported from the reservoir's seats. The limits below\nare chosen finished-part requirements, not measured stock/print capability.\n"
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('reservoir_float_rod_drawing', action="public-names")
    try:
        return _member('reservoir_float_rod_drawing', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('reservoir_float_rod_drawing', action="main")
