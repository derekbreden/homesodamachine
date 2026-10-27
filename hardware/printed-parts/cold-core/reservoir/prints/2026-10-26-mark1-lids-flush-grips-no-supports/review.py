"""Read the actual native lid slice: six open ports, no supports, correct recipe."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/cad-venv').is_dir())
CACHE = ROOT / '.cache/reservoir-lids-clear-ports-20261026'
sys.path.insert(0, str(HERE.parents[1]))
from review_slice import arc_geometry, WORDS


def main():
    path = CACHE / 'open-ports-native.gcode.3mf'
    with zipfile.ZipFile(path) as archive:
        gcode = archive.read('Metadata/plate_1.gcode')
        assert hashlib.md5(gcode).hexdigest() == archive.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        exported = json.loads(archive.read('Metadata/project_settings.config'))
        info = ET.fromstring(archive.read('Metadata/slice_info.config')).find('plate')
        config = ET.fromstring(archive.read('Metadata/model_settings.config'))
    text = gcode.decode()
    objects = [o.attrib for o in info.findall('object')]
    assert [o['name'] for o in objects] == ['reservoir-cap-left', 'reservoir-cap-right']
    meta = {m.get('key'): m.get('value') for m in info.findall('metadata')}
    plate = {m.get('key'): m.get('value') for m in config.find('plate').findall('metadata')}
    assert plate['bed_type'] == 'Engineering Plate' and meta['support_used'] == 'false'
    assert meta['filament_maps'] == '1' and meta['outside'] == 'false'
    for key, value in {'enable_support': '0', 'curr_bed_type': 'Engineering Plate',
                       'filament_flow_ratio': '1.05', 'nozzle_temperature': '260',
                       'nozzle_temperature_initial_layer': '255', 'infill_wall_overlap': '50%',
                       'wall_loops': '5', 'layer_height': '0.24', 'ironing_type': 'no ironing'}.items():
        assert f'; {key} = {value}\n' in text, key
    trims = re.findall(r'^\s*(G29\.1 Z[^\r\n]*)', text, re.M)
    assert trims == ['G29.1 Z0 ; clear z-trim value first', 'G29.1 Z0']
    assert re.search(r'^M972 S36 P0 C0 X1$', text, re.M)
    assert re.search(r'^T0 H-1', text, re.M)
    supports = re.findall(r'^; FEATURE: Support[^\r\n]*', text, re.M)
    assert not supports
    centres = {}
    for letter, offset, tx in [('left', -90.76909446716309, 119), ('right', 90.76909446716309, 206)]:
        points = {'air': (-102, -32.5), 'fill': (-90.5, 43.5), 'draw': (-94.3, 9.5)} if letter == 'left' else {
            'air': (120, -26), 'fill': (102.5, -57.5), 'draw': (84.2, -45)}
        for name, (px, py) in points.items():
            centres[letter + '-' + name] = np.array([px - offset + tx, 160 - py])
    hits = Counter()
    low, high = np.full(2, np.inf), np.full(2, -np.inf)
    x = y = e = 0.
    height = None
    feature = ''
    width = .8
    relative_e = True
    absolute = True
    count = 0
    for raw in text.splitlines():
        if raw.startswith('; Z_HEIGHT:'): height = float(raw.split(':')[1])
        if raw.startswith('; FEATURE:'): feature = raw.split(':', 1)[1].strip()
        if raw.startswith('; LINE_WIDTH:'): width = float(raw.split(':')[1])
        code = raw.split(';', 1)[0].strip()
        if not code: continue
        command = code.split()[0]
        words = {k: float(v) for k, v in WORDS.findall(code)}
        if command in ('G90', 'G91'): absolute = command == 'G90'
        if command in ('M82', 'M83'): relative_e = command == 'M83'
        if command == 'G92': x, y, e = words.get('X', x), words.get('Y', y), words.get('E', e)
        if command not in ('G0', 'G1', 'G2', 'G3'): continue
        nx = words.get('X', x) if absolute else x + words.get('X', 0)
        ny = words.get('Y', y) if absolute else y + words.get('Y', 0)
        ne = words.get('E', 0 if relative_e else e)
        extrusion = ne if relative_e else ne - e
        start, end = np.array([x, y]), np.array([nx, ny])
        if height is not None and extrusion > 0 and np.linalg.norm(end - start) > .001 and feature and feature != 'Custom':
            points = extrema = np.array([start, end])
            if command in ('G2', 'G3'):
                length, extrema = arc_geometry(start, end, words, command == 'G2')
                center = start + [words.get('I', 0), words.get('J', 0)]
                radius = np.linalg.norm(start - center)
                first = math.atan2(*(start - center)[::-1])
                angles = np.linspace(first, first + (-1 if command == 'G2' else 1) * length / radius,
                                     max(3, int(length / .1)))
                points = center + radius * np.stack([np.cos(angles), np.sin(angles)], axis=1)
            low = np.minimum(low, extrema.min(axis=0) - width / 2)
            high = np.maximum(high, extrema.max(axis=0) + width / 2)
            count += 1
            for name, centre in centres.items():
                vec = points[1:] - points[:-1]
                t = np.clip(((centre - points[:-1]) * vec).sum(axis=1) / np.maximum((vec * vec).sum(axis=1), 1e-12), 0, 1)
                distance = np.linalg.norm(points[:-1] + t[:, None] * vec - centre, axis=1).min()
                if distance - width / 2 < (2.35 if name.endswith('air') else 3.5): hits[name] += 1
        x, y, e = nx, ny, e + ne if relative_e else ne
    assert not hits, hits
    minimum = float(min(*low, *(np.array([325, 320]) - high)))
    assert count > 0 and minimum >= 80
    saved = json.loads((HERE / 'settings.json').read_text())
    diff = {k: {'saved': v, 'exported': exported.get(k)} for k, v in saved.items() if exported.get(k) != v}
    assert set(diff) <= {'curr_bed_type', 'extruder_ams_count', 'filament_map_mode', 'filament_settings_id', 'print_settings_id', 'printer_settings_id'}
    report = {'native_archive': str(path.relative_to(ROOT)), 'native_archive_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'gcode_sha256': hashlib.sha256(gcode).hexdigest(), 'embedded_md5_verified': True,
              'parts': objects, 'layer_count': len(re.findall(r'^; CHANGE_LAYER$', text, re.M)),
              'estimate_seconds': int(meta['prediction']), 'estimate_weight_g': float(meta['weight']),
              'support_features': 0, 'port_core_deposited_bead_intersections': {n: hits[n] for n in centres},
              'port_centres_bed_xy_mm': {n: v.tolist() for n, v in centres.items()},
              'port_probe_radii_mm': {'air': 2.35, 'liquid': 3.5},
              'arc_sampling_chord_length_max_mm': .1, 'minimum_full_bead_bed_inset_mm': minimum,
              'model_full_bead_bounds_xy_mm': [low.tolist(), high.tolist()], 'deposited_moves': count,
              'z_trim_commands': trims, 'plate': 'Engineering Plate', 'hotend': 'left 0.8 mm Standard',
              'global_export_metadata_differences': diff,
              'metadata_scope': 'Selected plate and emitted G-code are Engineering; actual left-nozzle selection and zero Z trim are checked. Other saved process values match.',
              'scope': 'Native slice verifies six open port cores through the complete print height and zero generated supports. Physical finish and TPU fit remain unassessed.'}
    (HERE / 'native-review.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['layer_count', 'estimate_seconds', 'estimate_weight_g', 'support_features', 'port_core_deposited_bead_intersections', 'minimum_full_bead_bed_inset_mm']}, indent=2))


if __name__ == '__main__': main()
