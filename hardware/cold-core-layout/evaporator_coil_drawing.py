"EVAP-01: production coil, complete tube outlines and tangent tail forms.\n\nThe installed coil and both tails share _coil's geometry. Views project the\nqualified kernel's fine tube meshes with hidden edges clipped in model space.\nThe local bridge relief is defined separately by a radial section and its dimensions.\nSheet two defines all circular bends and their tangent stations. Dimensions\nand tolerances define the manufactured article rather than a prototype state.\n"
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('evaporator_coil_drawing', action="public-names")
    try:
        return _member('evaporator_coil_drawing', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('evaporator_coil_drawing', action="main")
