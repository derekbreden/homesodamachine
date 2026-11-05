"""Fake countertop: the bench stand that stands in for a counter. An inverted U as deep as
the bed with its legs 130 mm apart, the narrow cavity under the counter in Derek's kitchen;
one faucet through its 1-3/8" hole, the umbilical hanging and bending under it, one
thickness of 3 cm throughout: the thickness most US kitchen counters are, the quartz,
granite and quartzite standard, and what the faucet layout stands the faucet on.

The print stands on the show face: the slab lies on the bed and the legs rise from it, so
the show face takes the plate's texture and nothing needs support. The slab's edges on the
bed are sharp. Every other edge is rounded: the four outer corners, the legs' inner edges
and the feet, and the legs meet the slab on a rounded root. The print mesh is the faucet's
absolute-tolerance triangulation, so the rounds print as rounds.

Frame: X across the legs, Y along the front edge, +Z up from the bed; the show face is Z = 0.
In use the piece stands the other way up.

Run with tools/cad-venv/bin/python. No argument exports the print.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_repo = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
for _path in (_hw / "scripts", _hw / "printed-parts" / "cadlib", _repo / "tools"):
    sys.path.insert(0, str(_path))

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()


from _rust_data import request as _request


def _data(**payload):
    return _request('part-data', 'part-data', {'part': 'fake-countertop', **payload})


globals().update(_data()['values'])


def numbers():
    from _materials import M_PETGF_BLACK, linear
    return _data(color=list(linear(M_PETGF_BLACK)))['numbers']


def main(output=None):
    """Write the current bench fixture with the Rust generator."""
    import _rust_part
    out = Path(output) if output is not None else _here.parent
    out.mkdir(parents=True, exist_ok=True)
    said = _rust_part.cut("tooling", "fake-countertop", numbers(), out)
    from _part_output import summary
    body = said['bodies'][0]
    report = summary(body, countertop_stl=out / 'fake-countertop.stl')
    print(report['countertop_info_json'])
    print(report['countertop_line'])


if __name__ == "__main__":
    if sys.argv[1:]:
        sys.exit("usage: fake_countertop.py")
    main()
