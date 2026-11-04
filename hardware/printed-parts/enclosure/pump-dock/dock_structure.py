"""Front-top's tee wall, the pump tees that stand in it and the stem elbows of their returns.

Each pump port feeds a purchased PP0208E tee (`fixed_returns`). Its branch stands in the TEE
WALL: front-top's bay bulkhead, one flat slab the bay's whole width and height
(`enclosure._bulkhead`). Each tee has one collar-clear bore through the wall from its bore
face; ahead of the bore a smaller hole through the wall's fore band passes the pump tube and
leaves room for the branch collet to stand extended and grip it. The bore holds the tee in X
and Z. Its fixed branch barrel stops it fore on the bore face, clear of the collet, and its
lower return, anchored in the rear valve, stops it aft.

Each lower return carries a NeoFit stem elbow in the tee's lower collet and another in the rear
valve's bottom collet, their stems cut to stand where `fixed_returns.elbow_return` puts them.

Every wall cut is a horizontal bore in a piece printed on Z, so each is teardropped.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "printed-parts/enclosure/enclosure"), str(_hardware / "printed-parts/cadlib")]
import _rust_part
_rust_part.start()
from _enclosure_compiled import compiled as _compiled

_rust_enclosure_module = 'dock_structure'

def __getattr__(name):
    if name == "__all__":
        return _compiled('dock_structure', action="public-names")
    if name.startswith("__"):
        raise AttributeError(name)
    try:
        return _compiled('dock_structure', action="get", path=(name,))
    except ValueError as error:
        raise AttributeError(name) from error

from _enclosure_compiled import install as _install
_install(_sys.modules[__name__])

if __name__ == "__main__":
    _compiled('dock_structure', action="main")
