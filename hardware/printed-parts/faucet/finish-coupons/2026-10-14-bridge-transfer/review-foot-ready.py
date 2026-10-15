"""Review the held Mark2 foot/shoulder pair manually; no printer control."""
from collections import Counter
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import sys
from zipfile import ZipFile

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/bambu_print.py').exists())
FOLDER = HERE / 'mark2'
sys.path[:0] = [str(ROOT / 'hardware/print-tests/petgf-fins'),
                str(ROOT / 'hardware/printed-parts/faucet'), str(ROOT / 'tools')]
loader = importlib.util.spec_from_file_location('transfer_finish', HERE / 'finish.py')
finish = importlib.util.module_from_spec(loader)
loader.loader.exec_module(finish)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    spec = json.loads((FOLDER / 'preparation.json').read_text())
    reviewed = json.loads((FOLDER / 'review.json').read_text())
    archive = next(FOLDER.glob('*-print-only.gcode.3mf'))
    with ZipFile(archive) as z:
        raw = z.read('Metadata/plate_1.gcode')
        checksum = z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        settings = json.loads(z.read('Metadata/project_settings.config'))
    with ZipFile(FOLDER / 'native.gcode.3mf') as z:
        native = z.read('Metadata/plate_1.gcode')
    if digest(raw) != reviewed['submitted_gcode_sha256']:
        raise ValueError('Submitted paths differ from the held comparison')
    if hashlib.md5(raw).hexdigest() != checksum:
        raise ValueError('Print-only checksum mismatch')
    if finish.movement_signature(native.decode()) != finish.movement_signature(raw.decode()):
        raise ValueError('Fan/feed treatment changed native coordinates or extrusion')
    paths = finish.segments(raw.decode())
    native_paths = finish.segments(native.decode())
    if len(paths) != len(native_paths):
        raise ValueError('Treatment changed deposited path count')
    rows = []
    for row in spec['specimens']:
        own = [p for p in paths if p['object'] == row['identify_id']
               and not p['feature'].startswith('Support') and p['feature'] != 'Brim']
        features = sorted({p['feature'] for p in own})
        if set(features) - finish.FOOT_MODEL:
            raise ValueError(f'Uncovered model feature: {features}')
        after = [p for p in own if p['z'] > .68001]
        if row['treatment'] and any(abs(p['fan'] - 178.5) > .001 for p in after):
            raise ValueError('B does not receive 70% fan on every model feature')
        if any(p['fan'] != 0 for p in own if p['z'] <= .68001):
            raise ValueError('Model fan is not off for the first three bed courses')
        bridges = [p for p in after if p['feature'] == 'Bridge']
        expected_speed = 15 if row['treatment'] else 25
        if any(abs(p['speed'] - expected_speed) > .001 for p in bridges):
            raise ValueError('Unexpected bridge feed')
        # 3MF transforms map centered mesh coordinates into machine coordinates.
        transform = np.asarray(row['build_transform'])
        rotation = transform[:9].reshape(3, 3).T
        translation = transform[9:]
        center = np.asarray(row['source_center_mm'])
        shoulder = []
        for p in own:
            midpoint = (p['a'] + p['b']) / 2
            cad = (midpoint - translation) @ rotation + center
            if abs(cad[0]) <= 1 and 28 <= cad[1] <= 30.2 and 12.5 <= cad[2] <= 15.5:
                shoulder.append(p)
        if not shoulder:
            raise ValueError('The localized rear shoulder is absent from the slice')
        rows.append(dict(id=row['id'], model_features=features,
            model_fan_after_three_layers_percent=sorted({round(p['fan'] / 2.55, 3) for p in after}),
            bridge_speed_after_three_layers_mm_s=sorted({p['speed'] for p in bridges}),
            rear_shoulder=dict(cad_window_mm=[[-1, 28, 12.5], [1, 30.2, 15.5]],
                sampled_segments=len(shoulder),
                nominal_print_z_mm=sorted({p['z'] for p in shoulder}),
                features=dict(Counter(p['feature'] for p in shoulder)),
                fan_percent=sorted({round(p['fan'] / 2.55, 3) for p in shoulder}),
                speed_mm_s_range=[min(p['speed'] for p in shoulder), max(p['speed'] for p in shoulder)],
                layer_height_mm=sorted({p['height'] for p in shoulder}))))
    for before, after in zip(native_paths, paths):
        if before['object'] == 1901 or before['feature'].startswith('Support') or before['feature'] == 'Brim':
            if before['fan'] != after['fan'] or before['speed'] != after['speed']:
                raise ValueError('A or support fan/feed differs from native')
    report = dict(status='Prepared and reviewed; not submitted',
        archive=str(archive.relative_to(ROOT)), archive_sha256=digest(archive.read_bytes()),
        gcode_sha256=digest(raw), embedded_md5_matches=True,
        native_xyz_arcs_and_extrusion_preserved=True,
        reference_and_support_native_fan_feed_preserved=True,
        model_feature_treatment_complete_in_this_foot_slice=True,
        geometry_sha256=spec['source_geometry']['source_sha256'],
        angle_x_degrees=-15,
        trim_commands_mm=[float(v) for v in re.findall(r'^\s*G29\.1 Z([-+.\d]+)', raw.decode(), re.M)],
        effective_settings={k: settings.get(k) for k in
            ['enable_support', 'support_type', 'support_style', 'support_top_z_distance',
             'nozzle_diameter', 'filament_nozzle_map', 'filament_colour']},
        minimum_edge_clearance_mm=reviewed['minimum_edge_clearance_mm'],
        specimens=rows,
        limits='Midpoint sampling locates commanded paths near defect 1; it does not measure bead shape, sag, seam buildup or physical release. This two-specimen crop changes layer return time. A combined recipe cannot separate flow, fan and speed effects.')
    (FOLDER / 'ready-review.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
