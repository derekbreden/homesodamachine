"""The display cover's two skirts and the slots and catches the housing holds them with.

Coordinates follow the machine display: X across, Y up the screen, Z out of the face.

EACH SKIRT IS THE NAMEPLATE'S SNAP TAB RUN BROAD. Its thickness, reach, square lip, land and
bearing slip are `_nameplate_interface`'s, and it runs `LENGTH` along the display instead of
the tab's width. The housing's side of it is the nameplate receiver's too: a slot with a flex
lane to one side, and under the catch nothing at all. The catch is the ceiling of the storey
cavity beside the display (`enclosure.display_storey_cavities`), one a side from the flex lane
out to the side wall, open into the pump bay.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "printed-parts/enclosure/enclosure"), str(_hardware / "printed-parts/cadlib")]
import _rust_part
_rust_part.start()
from _enclosure_compiled import compiled as _compiled

_rust_enclosure_module = '_display_retention'

def __getattr__(name):
    if name == "__all__":
        return _compiled('_display_retention', action="public-names")
    if name.startswith("__"):
        raise AttributeError(name)
    try:
        return _compiled('_display_retention', action="get", path=(name,))
    except ValueError as error:
        raise AttributeError(name) from error

from _enclosure_compiled import install as _install
_install(_sys.modules[__name__])

if __name__ == "__main__":
    _compiled('_display_retention', action="main")
