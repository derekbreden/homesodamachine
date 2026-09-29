"""Compare programmed white roads with black inlay voids in the raised v4 print.

This reads emitted coordinates, not a photograph or the printer's nozzle position.
The best translation on a 0.025 mm grid cannot measure physical registration.
"""
from pathlib import Path
import hashlib
import json
import sys
import zipfile

import numpy as np
from shapely.affinity import translate
from shapely.geometry import LineString, box
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools').is_dir())
sys.path.insert(0, str(ROOT / 'hardware/printed-parts/enclosure/nameplate'))
from verify_mark2_print import segments

ARCHIVE = ROOT / '.cache/prints/2026-09-29-nameplate-all-ink-raised-mark2-v4/ready/nameplate-all-ink-raised-clearance-z004-mark2-v4.gcode.3mf'
REVIEW = ROOT / 'hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-29-nameplate-all-ink-raised-mark2-v4'


def main():
    with zipfile.ZipFile(ARCHIVE) as archive:
        gc = archive.read('Metadata/plate_1.gcode')
    path = ARCHIVE.parent / 'registration-audit.gcode'
    path.write_bytes(gc)
    roads = [r for r in segments(path) if r['object'] == 2303
             and abs(r['layer'] - 16.05) < 1e-5
             and not r['feature'].startswith('Support')]
    shapes = [unary_union([
        LineString([r['a'], r['b']]).buffer(r['width'] / 2, resolution=3)
        for r in roads if r['tool'] == tool]) for tool in (0, 1)]
    results = []
    for name, bounds in [('logo', (115,110,144,140)),
                         ('text', (144,110,187.5,140)),
                         ('qr', (188,110,215,140))]:
        region = box(*bounds)
        black, white = [s.intersection(region) for s in shapes]
        void = region.difference(black.buffer(.025).buffer(-.025))
        pieces = list(void.geoms) if hasattr(void, 'geoms') else [void]
        cavity = unary_union([v for v in pieces if v.intersection(white).area > .2])
        assert not cavity.is_empty and not white.is_empty, name
        choices = [(cavity.symmetric_difference(translate(white, dx, dy)).area,
                    round(float(dx), 6), round(float(dy), 6))
                   for dx in np.arange(-.2, .2001, .025)
                   for dy in np.arange(-.2, .2001, .025)]
        best = min(choices)
        cx, cy = cavity.centroid.coords[0]
        wx, wy = white.centroid.coords[0]
        results.append({'region': name, 'road_shape_white_area_mm2': white.area,
                        'road_void_area_mm2': cavity.area,
                        'centroid_white_minus_void_mm': [wx-cx, wy-cy],
                        'best_grid_translation_mm': list(best[1:]),
                        'symmetric_difference_area_mm2': best[0]})
    record = {'native_sha256': hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
              'gcode_sha256': hashlib.sha256(gc).hexdigest(),
              'audit_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'print_z_mm': 16.05,
              'method': 'Extrusion-road envelopes, 0.025 mm closure of black skin gaps, connected voids selected by white overlap; translation search [-0.2,0.2] on a 0.025 mm grid.',
              'scope': 'Programmed-path comparison; physical nozzle error is unmeasured.',
              'regions': results}
    (REVIEW / 'registration-path-audit.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps({r['region']: r['best_grid_translation_mm'] for r in results}))


if __name__ == '__main__':
    main()
