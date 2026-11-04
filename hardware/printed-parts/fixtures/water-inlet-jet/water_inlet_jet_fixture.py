"""Standalone drilling jaws for the candidate water-inlet jet cap stock.

The base lies on the drill table, Z=0. A rod stands on its 8 mm floor. Two
horizontal C-clamps close the loose jaw against the fixed jaw; two more hold
the base flanges to the owned wood backer and drill table. The grooves are
vertical and open at the top. There is no printed drill bushing.

The nominal stock diameter comes from the candidate jet dimensions. Physical
stock fit, printed grip, clamp clearance and spindle alignment are untested.
This bench fixture is not part of the machine assembly or its BOM.

Run with tools/cad-venv/bin/python. No argument exports both print parts.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_repo = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
for _path in (_hw / "scripts", _hw / "cold-core-layout", _repo / "tools"):
    sys.path.insert(0, str(_path))

from _water_inlet_jet import JET_CAP_D, JET_PASSAGE_D  # noqa: E402
from docgen import substitute_md  # noqa: E402


if __name__ == "__main__":
    import _rust_part
    _rust_part.start()


from _rust_data import request as _request


def _data(**payload):
    return _request('part-data', 'part-data', {'part': 'water-inlet-jet-fixture',
        'cap_diameter': JET_CAP_D, 'passage_diameter': JET_PASSAGE_D, **payload})


globals().update(_data()['values'])


def numbers():
    from _material_base import M_PETGF_BLACK
    from _materials import linear
    return _data(color=list(linear(M_PETGF_BLACK)))['numbers']


def _document():
    substitute_md(_here.parent / 'README.md', variables=_data()['variables'])


def main(output=None):
    import _rust_part
    out = Path(output) if output is not None else _here.parent
    out.mkdir(parents=True, exist_ok=True)
    result = _rust_part.cut("tooling", "water-inlet-jet-fixture", numbers(), out)
    _document()
    print(f"-> water inlet jet fixture: {len(result['files'])} files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    main(options.output)
