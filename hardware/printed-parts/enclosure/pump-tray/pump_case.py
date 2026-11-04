"""Pump case — two-piece enclosure for a peristaltic pump.

Base: base plate with octagon-to-footprint ramp, octagon pump bore,
      and a cylindrical tower below.
Cap:  asymmetric flared skirt (wide on +Y, narrow on -Y) with a lower
      extension that tapers to uniform width.

The two parts mate at a stepped split surface and lock together with
snap-fit ramps on four interior walls.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "printed-parts/enclosure/enclosure"), str(_hardware / "printed-parts/cadlib")]
import _rust_part
_rust_part.start()
from _enclosure_compiled import compiled as _compiled

_rust_enclosure_module = 'pump_case'

def __getattr__(name):
    if name == "__all__":
        return _compiled('pump_case', action="public-names")
    if name.startswith("__"):
        raise AttributeError(name)
    try:
        return _compiled('pump_case', action="get", path=(name,))
    except ValueError as error:
        raise AttributeError(name) from error

from _enclosure_compiled import install as _install
_install(_sys.modules[__name__])

if __name__ == "__main__":
    _compiled('pump_case', action="main")
