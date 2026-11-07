"""Removable silicone funnel with an integral roof apron.

The collar center is the origin; z=0 is the frame-bearing brim underside. The brim,
collar and normal ramp wall lead to a substantial silicone plug, a 36 mm wide
square-cornered rectangle centred on the outlet. Its flat underside bears on
the elbow cradle's two hook tops. Its walls run up into
the bowl's underside, so none of its top shows. A straight 6 mm bore grips the
1/4-inch elbow stem over its complete insertion depth. The frame's through
hole passes the stem through the rigid frame.
"""

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
