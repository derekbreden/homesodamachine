"Shared cold-core datums and construction interfaces.\n\nRust owns the casing stock, cavity envelope, clamp stack and port-lane\ndimensions. The remaining cap mount and passage recipes expose their\nsource-frame values to the sibling parts.\n\nThe constants carry claims about each other — a screw long enough for its insert, a band wide\nenough for its bore, two columns far enough apart for foam to reach between them — and those are\nsettled here, as this file is read, with no solid yet to measure. `_stated_bounds` is the ledger\nthey record into; `enclosure_assembly.carry_stated_bounds` drains it onto the machine's card, where\nan open one is a red row a reader can see beside the geometry it describes. The siblings that\nimport this module take `bound` and `state` from here rather than reaching for the ledger\nthemselves, because this is already the path they read every other shared name off."
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('_cold_core_interface', action="public-names")
    try:
        return _member('_cold_core_interface', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('_cold_core_interface', action="main")
