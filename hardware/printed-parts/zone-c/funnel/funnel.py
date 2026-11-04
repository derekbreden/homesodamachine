"""Removable silicone funnel with an integral roof apron.

The collar center is the origin; z=0 is the frame-bearing brim underside. The brim,
collar and normal ramp wall lead to a substantial silicone plug, a 36 mm wide
square-cornered rectangle centred on the outlet. Its flat underside bears on
the elbow cradle's two hook tops. Its walls run up into
the bowl's underside, so none of its top shows. A straight 6 mm bore grips the
1/4-inch elbow stem over its complete insertion depth. The frame's through
hole passes the stem through the rigid frame.
"""

import argparse
import sys
from pathlib import Path

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if any(
    (p / 'hardware/scripts' / helper).is_file()
    for helper in ('_rust_part.py', '_cadq_export.py')))
# _repo is this EDITION's root; tools/ is shared machinery with one copy at the
# repo root, so it gets its own anchor rather than a tools/ per edition.
_tools = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"
sys.path.insert(0, str(_repo / "hardware" / "scripts"))
sys.path.insert(0, str(_tools))


def __getattr__(name):
    if name != "elbow_cradle":
        raise AttributeError(name)
    import elbow_cradle
    globals()[name] = elbow_cradle
    return elbow_cradle


# The enclosure recorder binds this leaf to its numeric construction graph.
brim_plan = None


from _zone_data import data as _zone


def _data(**payload):
    return _zone('funnel', **payload)


globals().update(_data()['values'])
drain_local = tuple(drain_local)


def numbers():
    return _data(method='numbers')['numbers']


def _document(fill):
    from docgen import substitute_md
    substitute_md(_here.parent / 'README.md', variables=_data(fill=fill)['variables'])
    print('-> README.md')


def main(output=None):
    import _rust_part
    out = Path(output) if output is not None else _here.parent
    out.mkdir(parents=True, exist_ok=True)
    said = _rust_part.cut('funnel', 'funnel', numbers(), out)
    _document(said['bodies'][0]['fill_mm3'])
    print(f"-> funnel STEP, fine model and payload; {said['bodies'][0]['volume']:.1f} mm3")


if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    options = parser.parse_args()
    main(options.output)
