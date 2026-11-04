"""Low lift-off cover located in the silicone funnel's existing mouth.

Local Z=0 is the underside of the plate on the silicone brim. The whole top
is a flat bed face in the separate print export. The continuous shallow skirt
locates the cover sideways; the plate rests on the silicone brim under gravity.

The Rust kernel cuts both file sets from `numbers()`.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/scripts/_rust_part.py').is_file())
sys.path[:0] = [str(ROOT / 'hardware/scripts'), str(ROOT / 'tools'),
                str(HERE.parent / 'funnel')]
if __name__ == '__main__':
    import _rust_part
    _rust_part.start()

import funnel
from _materials import M_PETG_BLACK, linear
from docgen import substitute_md

from _zone_data import data as _zone


def _data(**payload):
    return _zone('funnel-cover', **payload)


globals().update(_data()['values'])


def _skirt_dimensions():
    return tuple(_data()['skirt'])


def numbers():
    return _data(method='numbers')['numbers']


def main():
    import _rust_part
    said = _rust_part.cut('funnel', 'funnel-cover', numbers(), HERE)
    substitute_md(HERE / 'README.md', variables=_data()['variables'])
    print(f'-> cover STEP, print STEP, STL and payload; {said["bodies"][0]["volume"]:.1f} mm3')


if __name__ == '__main__':
    main()
