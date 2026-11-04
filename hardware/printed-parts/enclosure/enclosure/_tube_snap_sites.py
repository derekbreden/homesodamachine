"""Selected integral tube snaps on back-top's roof and east wall.

The listed world-space line endpoints and parameters are explicit routing
datums; this registry does not infer clearance or follow an unrelated route
edit. Back-top builds in machine -Z. Each flavor station shares one filled
root bridge while its two seats remain individual routing records.

Quarter-inch tube retains the selected C2 section: diameter 6.35, wing 2.40.
The 4 mm tube uses diameter 4.10 and a 1.52 mm functional spring section scaled
from C2's proportions. That smaller section is a modeled fit estimate.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "printed-parts/enclosure/enclosure"), str(_hardware / "printed-parts/cadlib")]
import _rust_part
_rust_part.start()
from _enclosure_compiled import compiled as _compiled

_rust_enclosure_module = '_tube_snap_sites'

def __getattr__(name):
    if name == "__all__":
        return _compiled('_tube_snap_sites', action="public-names")
    if name.startswith("__"):
        raise AttributeError(name)
    try:
        return _compiled('_tube_snap_sites', action="get", path=(name,))
    except ValueError as error:
        raise AttributeError(name) from error

from _enclosure_compiled import install as _install
_install(_sys.modules[__name__])

if __name__ == "__main__":
    _compiled('_tube_snap_sites', action="main")
