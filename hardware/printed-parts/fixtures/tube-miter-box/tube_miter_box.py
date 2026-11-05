"""Tube miter box: the bench block that holds 1/4" and 3/8" OD LLDPE tube round and guides a
razor blade square across it.

Two open troughs run along Y, one per tube size: a half-round floor at the tube's radius plus
a running fit, under vertical walls the same width apart, open at the top face so a tube lies
in from above at any point along its length. One slot crosses both troughs in the XZ plane. A
0.009" single-edge razor blade drops into it from the top face; the slot's walls to either side
of each trough hold the blade in one plane while the trough holds the tube round under it, and
the spine landing on the top face ends the stroke with the edge below the trough floor. A
0.025" utility blade fits the same slot and ends on the slot floor.

The slot stands nearer one end face. The short side carries the offcut; the long side aligns
the tube that is kept.

Frame: X along the blade, Y along the tube, +Z up. The bottom face is Z = 0 and is the print
bed. Every face is vertical, upward or a valley; the print needs no support.

Run with tools/cad-venv/bin/python. No argument exports the print.
"""

from __future__ import annotations

import argparse
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

from fits import running  # noqa: E402


from _rust_data import request as _request


def _data(**payload):
    return _request('part-data', 'part-data', {'part': 'tube-miter-box', 'running': running, **payload})


globals().update(_data()['values'])
TROUGHS = {name: tuple(row) for name, row in TROUGHS.items()}


def trough_r(tube_od):
    return _data(method='trough_r', tube_od=tube_od)


def numbers():
    from _material_base import M_PETGF_BLACK
    from _materials import linear
    return _data(color=list(linear(M_PETGF_BLACK)))['numbers']


def main(output=None):
    import _rust_part
    out = Path(output) if output is not None else _here.parent
    out.mkdir(parents=True, exist_ok=True)
    said = _rust_part.cut("tooling", "tube-miter-box", numbers(), out)
    from _part_output import summary
    print(f"-> tube-miter-box STEP, STL and fine model; {summary(said['bodies'][0], volume_spec='.2f')['volume']} cm3")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    main(options.output)
