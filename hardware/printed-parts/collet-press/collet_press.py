"""Collet press — one-piece hand tool for releasing a 1/4-inch John Guest
push-to-connect collet.

Print orientation is the modelling orientation: the handle lies flat on Z=0
and the forked head rises from it at 45 degrees.  The head is one unstepped
slab.  Its U-slot passes the tube while the surrounding face bears on the
release sleeve.

Run:
    tools/cad-venv/bin/python \
        hardware/printed-parts/collet-press/collet_press.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


_here = Path(__file__).resolve().parent
_hardware = next(p for p in _here.parents if p.name == "hardware")
_repo = _hardware.parent
sys.path.insert(0, str(_hardware / "scripts"))
sys.path.insert(0, str(_repo / "tools"))
sys.path.insert(0, str(_hardware / "reference" / "jg-pp0408w"))

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

import jg_pp0408w as jg  # noqa: E402


from _rust_data import request as _request


def _data(**payload):
    return _request('part-data', 'part-data', {'part': 'collet-press',
        'port_diameter': jg.PORT_D, 'collet_diameter': jg.COLLET_D,
        'collet_bore': jg.COLLET_BORE, 'collet_wall': jg.COLLET_WALL,
        'collet_travel': jg.COLLET_TRAVEL, **payload})


globals().update(_data()['values'])


def _head_underside_x(z):
    return _data(method='head_underside_x', z=z)


def numbers():
    from _materials import M_PETGF_BLACK, linear
    return _data(color=list(linear(M_PETGF_BLACK)))['numbers']


def main(output=None):
    import _rust_part
    out = Path(output) if output is not None else _here
    out.mkdir(parents=True, exist_ok=True)
    said = _rust_part.cut("tooling", "collet-press", numbers(), out)
    body = said["bodies"][0]
    from _part_output import summary
    report = summary(body, volume_spec='.2f')
    print(f"-> collet-press STEP, STL, fine model and payload; {report['volume']} cm3")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    main(options.output)
