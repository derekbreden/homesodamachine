"""Case-derived locating profiles for the integral pump inverse and lower retainer.

The lower retainer has flat lands around the rigid eight-millimetre molded skirt.
Front-top's integral upper inverse locates the rear boss and clears the motor can.
The production geometry consumes these profiles in enclosure._fixed_pump_mount.

The accepted earlier cradle/cap assembly held both physical pumps firmly without observed
vertical play; hardware/reference/kamoer-kphm400/physical-fit.json binds that identified
article. It does not qualify the integral upper/lower skirt capture. This module's collar
builder is a source solid, not a separate printed part. The physical reference is
hardware/reference/kamoer-kphm400/scan-review.md; case-derived geometry alone does not
independently establish physical contact.

Run:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/pump-tray/pump_tray.py selftest
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "printed-parts/enclosure/enclosure"), str(_hardware / "printed-parts/cadlib")]
import _rust_part
_rust_part.start()
from _enclosure_compiled import compiled as _compiled

_rust_enclosure_module = 'pump_tray'

def __getattr__(name):
    if name == "__all__":
        return _compiled('pump_tray', action="public-names")
    if name.startswith("__"):
        raise AttributeError(name)
    try:
        return _compiled('pump_tray', action="get", path=(name,))
    except ValueError as error:
        raise AttributeError(name) from error

from _enclosure_compiled import install as _install
_install(_sys.modules[__name__])

if __name__ == "__main__":
    _compiled('pump_tray', action="main")
