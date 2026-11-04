"RC62 magnetic float: PETG Translucent Clear envelope and fitted ASA Aero core.\n\nFrame: guide bore on Z, finished bottom at Z=0, roof at positive Z.\nThe separate Aero insert seats from Z=47 to the roof underside at Z=57.\n\nThis module holds the float's numbers and the figures derived from them, and writes the numbers\nthe geometry takes (`numbers()`) to `magnetic-float.numbers.json`; `magnetic_float.rs`, beside\nit, cuts each piece's STEP and payload, the printed pieces' STLs, and the assembly, section and\nexploded views from them on the kernel (`hardware/scripts/_rust_part.py`).\n"
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('magnetic_float', action="public-names")
    try:
        return _member('magnetic_float', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('magnetic_float', action="main")
