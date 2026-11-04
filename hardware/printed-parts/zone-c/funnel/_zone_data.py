"""Compatibility transport for the Rust funnel and casting-tool scalar graph."""
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
    if part == 'funnel-mold' and method in ('design', 'report'):
        note_read(ROOT / 'hardware/printed-parts/zone-c/funnel/funnel.step')
    values = {'part': part, 'method': method, 'root': str(ROOT),
              'slip': fits.slip, 'running': fits.running,
              'supported_surface': fits.supported_surface}
    if part == 'funnel-frame' and method in ('fasteners', 'body_half', 'numbers', 'document'):
        import _enclosure_interface as enc
        values['enclosure'] = {name: getattr(enc, name) for name in (
            'heatset_long_len', 'wall', 'heatset_dia', 'slide_slip',
            'y_stack_high_depth', 'screw_clear_dia', 'head_cbore_dia', 'funnel_collar_air')}
    if method == 'numbers':
        from _materials import M_PETGF_BLACK, M_PETG_BLACK, M_SILICONE_BLACK, linear
        from _payload_rules import LINEAR_DEFLECTION_RATIO
        values.update(silicone_color=list(linear(M_SILICONE_BLACK)),
                      viewer_deflection_ratio=LINEAR_DEFLECTION_RATIO)
        if part in ('elbow-cradle', 'funnel-frame'):
            values['color'] = list(linear(M_PETGF_BLACK))
        elif part == 'funnel-cover':
            values['color'] = list(linear(M_PETG_BLACK))
        elif part == 'funnel-mold':
            for name, color in {'cavity': '#3D9998', 'core': '#D8A751',
                                'funnel': '#555C68', 'rod': '#AAB9C8'}.items():
                values[name + '_color'] = list(linear(color))
    return request('part-data', 'part-data', {**values, **payload})
