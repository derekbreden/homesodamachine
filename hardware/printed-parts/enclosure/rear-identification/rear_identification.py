"""Identification chips for the selected six-port rear grid.

The rear flange and nut seating planes stay fixed. Each 1.8 mm tile slides in a
continuous 2 mm rear channel, 0.2 mm inside the outer wall face, with its bore
on the corresponding fitting.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "printed-parts/enclosure/enclosure"), str(_hardware / "printed-parts/cadlib")]
import _rust_part
_rust_part.start()
from _enclosure_compiled import compiled as _compiled

_rust_enclosure_module = 'rear_identification'

def __getattr__(name):
    if name == "__all__":
        return _compiled('rear_identification', action="public-names")
    if name.startswith("__"):
        raise AttributeError(name)
    try:
        return _compiled('rear_identification', action="get", path=(name,))
    except ValueError as error:
        raise AttributeError(name) from error

from _enclosure_compiled import install as _install
_install(_sys.modules[__name__])

if __name__ == "__main__":
    _compiled('rear_identification', action="main")
