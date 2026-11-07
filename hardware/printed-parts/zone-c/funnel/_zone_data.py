"""Transport to the funnel, cradle and frame datums in part-data, for the hand-run tools that read
them through `funnel.py`, `elbow_cradle.py` and `funnel_frame.py`."""
from pathlib import Path
import sys

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'hardware/scripts/_rust_part.py').is_file())
for path in (ROOT / 'hardware/scripts', ROOT / 'hardware/printed-parts/cadlib'):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import fits
import _rust_part
from _rust_data import request


def note_read(path):
    try:
        _rust_part._READ_TARGETS.add(Path(path).resolve().relative_to(_rust_part.ROOT.resolve()).as_posix())
    except ValueError:
        pass


def data(part, *, method='state', **payload):
    if part == 'elbow-cradle' or (part == 'funnel-frame' and method in ('numbers', 'document')):
        note_read(ROOT / 'hardware/reference/neofit-stem-elbow/reference-parameters.json')
        if method in ('block', 'stations', 'numbers', 'hook_corner_clearance', 'document'):
            note_read(ROOT / 'hardware/manifold-layout/above-core.json')
        if part == 'elbow-cradle' and method == 'numbers':
            note_read(ROOT / 'hardware/reference/neofit-stem-elbow/neofit-stem-elbow.fine.step.mesh')
    values = {'part': part, 'method': method, 'root': str(ROOT),
              'slip': fits.slip, 'running': fits.running,
              'supported_surface': fits.supported_surface}
    return request('part-data', 'part-data', {**values, **payload})
