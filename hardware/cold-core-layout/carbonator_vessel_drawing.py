'Carbonator closure assembly: source-defined sections and an exterior end view.\n\nFabrication state of HSM-0004, before permanent fittings. Registers show their\nactual drill points; the rod has its fixed finished length and the cap spacing\nis controlled to its specified interface tolerance. Weld profiles are\ndiagrammatic because a qualified weld size is not established by the procedure.\n'
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('carbonator_vessel_drawing', action="public-names")
    try:
        return _member('carbonator_vessel_drawing', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('carbonator_vessel_drawing', action="main")
