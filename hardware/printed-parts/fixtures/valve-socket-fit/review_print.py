"""Read socket openings and floor stock from the retained native extrusion paths."""
from collections import defaultdict
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import numpy as np
from shapely.geometry import LineString
from shapely.ops import unary_union

from prepare_print import HERE, ROOT, JOB, JOB_NAME, sha, single_object_segments


def intervals(shape):
    if shape.is_empty:
        return []
    pieces = [shape] if shape.geom_type == 'LineString' else list(shape.geoms)
    return sorted((p.bounds[0], p.bounds[2]) for p in pieces if p.geom_type == 'LineString')


def main():
    readiness = json.loads((HERE / 'print-readiness.json').read_text())
    geometry = json.loads((HERE / 'geometry-check.json').read_text())
    report = json.loads((JOB / (JOB_NAME + '-input.print.json')).read_text())
    part, = report['parts']
    gcode = JOB / 'ready/plate_1.gcode'
    assert sha(gcode) == readiness['gcode_sha256']
    layers = defaultdict(list)
    for segment in single_object_segments(gcode, part['identify_id']):
        if segment['feature'] in ('', 'Custom', 'Brim'):
            continue
        local = (np.array([segment['a'], segment['b']])
                 - np.array(part['plate_translation_mm']) + np.array(part['source_center_mm']))
        layers[segment['layer']].append((segment, local))
    errors, sections, rectangles, center_readings = [], [], [], []
    dimensions = geometry['dimensions']
    centers_z = [dimensions['station_z_mm'] + s * dimensions['post_pitch_z_mm'] / 2 for s in (-1, 1)]
    centers_x = [s * dimensions['post_pitch_x_mm'] / 2 for s in (-1, 1)]
    for z, items in sorted(layers.items()):
        supports = [s for s, _ in items if s['feature'].startswith('Support')]
        if supports:
            errors.append(f'Support enters the socket panel at Z{z:g}.')
        roads = unary_union([LineString(local[:, :2]).buffer(s['width'] / 2)
                             for s, local in items if not s['feature'].startswith('Support')])
        spans = intervals(roads.intersection(LineString(((-25, 2), (25, 2)))))
        layer_height = 0.2 if z < 0.3 else 0.24
        for lo, hi in spans:
            rectangles.append([(lo, z-layer_height), (hi, z-layer_height), (hi, z), (lo, z)])
        for center_z in centers_z:
            if abs(z - center_z) > 0.12:
                continue
            for center_x in centers_x:
                left = max((hi for lo, hi in spans if hi < center_x), default=None)
                right = min((lo for lo, hi in spans if lo > center_x), default=None)
                assert left is not None and right is not None
                opening = right - left
                center_readings.append({'center_x_mm': center_x, 'center_z_mm': center_z,
                    'layer_top_z_mm': z, 'axial_probe_y_mm': 2.0,
                    'opening_x_mm': [left, right], 'opening_width_mm': opening})
                if not 7.0 <= opening <= 7.4:
                    errors.append(f'Unexpected socket width {opening:g} at X{center_x:g}, Z{z:g}.')
        sections.append({'layer_top_z_mm': z, 'occupied_x_at_y_2_mm': spans})
    assert len(center_readings) == 4
    support = json.loads((ROOT / readiness['support_audit']).read_text())
    assert support['parts'][0]['summary']['support_bodies'] == 0
    fig, ax = plt.subplots(figsize=(6.2, 6.1))
    ax.add_collection(PolyCollection(rectangles, facecolors='#303a44', edgecolors='none'))
    for x in centers_x:
        for z in centers_z:
            ax.add_patch(plt.Circle((x, z), 3.45, fill=False, color='#df702a', linewidth=1))
    ax.set(xlim=(-23, 23), ylim=(-1, 46), xlabel='X (mm)', ylabel='Z (mm)',
           title='Native socket toolpaths at Y = 2 mm\nOrange: nominal Ø6.9 valve posts')
    ax.set_aspect('equal')
    fig.tight_layout()
    for extension in ('svg', 'png'):
        fig.savefig(HERE / ('toolpath-review.' + extension), dpi=160)
    result = {'status': 'pass' if not errors else 'fail', 'errors': errors,
        'gcode_sha256': readiness['gcode_sha256'], 'socket_center_readings': center_readings,
        'support_bodies': 0, 'sections': sections,
        'scope': 'Commanded extrusion envelopes and support paths; physical socket retention is unmeasured.'}
    (HERE / 'toolpath-review.json').write_text(json.dumps(result, indent=2) + '\n')
    readiness.update({'status': 'ready_for_socket_fit_trial' if not errors else 'toolpath_review_failed',
        'toolpath_review': str((HERE / 'toolpath-review.json').relative_to(ROOT)),
        'toolpath_review_sha256': sha(HERE / 'toolpath-review.json')})
    for path in (HERE / 'print-readiness.json', JOB / 'readiness.json'):
        path.write_text(json.dumps(readiness, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'errors', 'socket_center_readings', 'support_bodies')}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
