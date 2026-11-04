"""Station datums for the four pump tees, the tee wall's fore band and the fittings and tubes
that join them.

Coordinates are enclosure millimetres: +Y points inward and +Z points up. Each pump port
feeds one purchased PP0208E tee, its branch toward the pump and its run upright. The fore
valve stands over the run on one short straight tube. The lower return reaches the rear valve's
bottom port: a trimmed NeoFit stem elbow in the tee's lower collet, one tube, and a
second stem elbow in the valve.

THE FORE BAND'S AFT FACE IS THE BORE FACE. Each tee's branch bore opens on it, and the tee
stands with its fixed branch barrel just aft of it. The branch collet stands extended in its
recess ahead of that face and grips the pump tube like any push-fit; the tube is pushed home
once, at the factory, to the tee's stop.

This module holds geometry data only; the dock's solids and the manifold read the same
figures.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "printed-parts/enclosure/enclosure"), str(_hardware / "printed-parts/cadlib")]
import _rust_part
_rust_part.start()
from _enclosure_compiled import compiled as _compiled

_rust_enclosure_module = 'fixed_returns'

def __getattr__(name):
    if name == "__all__":
        return _compiled('fixed_returns', action="public-names")
    if name.startswith("__"):
        raise AttributeError(name)
    try:
        return _compiled('fixed_returns', action="get", path=(name,))
    except ValueError as error:
        raise AttributeError(name) from error

from _enclosure_compiled import install as _install
_install(_sys.modules[__name__])

if __name__ == "__main__":
    _compiled('fixed_returns', action="main")
