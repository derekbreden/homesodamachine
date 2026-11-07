'Finished carbonator end cap, on one ANSI B landscape engineering sheet.\n\nThe face view and location table describe the two tapped ports and the blind\nrod register. Section A-A identifies the plate faces and NPT entry direction;\nlocal section B-B shows the actual 135-degree drill point and tip-depth datum.\nAll part dimensions come from the laser-blank/register source module. Thread\nlines are a conventional representation, not a model of the helical surfaces.\n\nendcap_circular_drawing.rs draws the sheet, when an order needs it; this module keeps the\nhelpers the other fabrication drawings import.\n'
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('endcap_circular_drawing', action="public-names")
    try:
        return _member('endcap_circular_drawing', name)
    except ValueError as error:
        raise AttributeError(name) from error
