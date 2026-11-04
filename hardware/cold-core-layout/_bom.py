'Every cold-core row of the bill, against the body that realizes it.\n\n`ledger/bom.md` is what the machine costs; this assembly is where those parts stand. `PARTS`\nholds the two together — one entry per billed part the cold core carries, naming the text that\nfinds its row and the bodies `cold_core_assembly` places for it.\n\nTHE TABLE IS HELD TO THE BILL FROM BOTH ENDS. An entry whose `bills` text is not in `bom.md`\nis a part that has left the bill, and a body placed under a name no entry claims is a body\nnobody is buying. `check` reports each, so the table cannot drift from either side.\n\nA part with no body is the reading this file exists for. Wire and fasteners are in the bill and\ncarry no solid here, so they stand in that list permanently and by name.\n'
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('_bom', action="public-names")
    try:
        return _member('_bom', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('_bom', action="main")
