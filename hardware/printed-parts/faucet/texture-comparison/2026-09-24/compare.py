"""Offline native-slicer timing comparison of the faucet's proposed texture regions."""
from pathlib import Path
import hashlib
import json
import math
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve()
while not (ROOT / 'hardware/printed-parts/petgf.3mf').is_file():
    ROOT = ROOT.parent
HERE = ROOT / '.cache/prints/2026-09-24-faucet-texture-comparison'
sys.path.insert(0, str(ROOT / 'hardware/scripts'))
from verify_round_layer_band import wall_layers

import numpy as np
import trimesh

FAUCET = ROOT / 'hardware/printed-parts/faucet'
SETTINGS = 'Metadata/project_settings.config'
STYLES = {
    'sculpted': FAUCET / 'faucet-petgf.3mf',
}
VARIANTS = ('baseline', 'fine-cover', 'fine-upper', 'all-fine')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
results = []


def runs(layers):
    result = []
    for z, height in sorted({(round(z, 4), round(h, 4)) for z, h in layers}):
        if not result or result[-1]['height_mm'] != height:
            result.append({'height_mm': height, 'bottom_z_mm': round(z-height, 4),
                           'last_z_mm': z, 'layer_count': 1})
        else:
            result[-1].update(last_z_mm=z, layer_count=result[-1]['layer_count'] + 1)
    return result


for style, source in STYLES.items():
    source_hash = sha(source)
    report = json.loads(source.with_suffix('.print.json').read_text())
    assert report['project_sha256'] == source_hash
    parts = report['parts']
    for part in parts:
        assert sha(ROOT / part['source']) == part['stl_sha256']
    with zipfile.ZipFile(source) as archive:
        original = {name: archive.read(name) for name in archive.namelist()}
    saved = json.loads(original[SETTINGS])
    assert saved['layer_height'] == '0.24' and saved['initial_layer_print_height'] == '0.2'
    assert 'Metadata/layer_config_ranges.xml' not in original
    # The curved gooseneck begins at CAD Z 153.4 mm. Take the lowest print-Z
    # of its mesh, including the tilted inner/outer skins, then round down.
    base = parts[0]
    mesh = trimesh.load(ROOT / base['source'], process=False)
    transform = np.asarray(base['build_transform']).reshape(4, 3)
    xyz = (mesh.vertices - np.asarray(base['source_center_mm'])) @ transform[:3] + transform[3]
    low = float(xyz[mesh.vertices[:, 2] >= 153.4, 2].min())
    upper_start = math.floor((low - .24) / .24) * .24
    for variant in VARIANTS:
        job = HERE / f'{style}-{variant}'
        job.mkdir(exist_ok=True)
        ready = job / 'ready'
        ready.mkdir(exist_ok=True)
        name = f'faucet-texture-{style}-{variant}'
        staged = job / f'{name}.3mf'
        native = ready / f'{name}.gcode.3mf'
        members = dict(original)
        settings = dict(saved)
        ranges = {}
        if variant != 'baseline':
            settings['initial_layer_print_height'] = '0.08'
        if variant == 'all-fine':
            settings['layer_height'] = '0.08'
        if variant in {'fine-cover', 'fine-upper'}:
            ranges[3] = [(0.0, 100.0, .08)]
        if variant == 'fine-upper':
            ranges[1] = [(upper_start, 300.0, .08)]
            ranges[2] = [(0.0, 300.0, .08)]
        if ranges:
            objects = ET.Element('objects')
            for object_id, bands in sorted(ranges.items()):
                element = ET.SubElement(objects, 'object', id=str(object_id))
                for low, high, height in bands:
                    band = ET.SubElement(element, 'range', min_z=f'{low:.4f}', max_z=f'{high:.4f}')
                    ET.SubElement(band, 'option', opt_key='layer_height').text = str(height)
            members['Metadata/layer_config_ranges.xml'] = ET.tostring(objects, encoding='UTF-8', xml_declaration=True)
        members[SETTINGS] = (json.dumps(settings, indent=2) + '\n').encode()
        if not native.exists():
            with zipfile.ZipFile(staged, 'w', zipfile.ZIP_DEFLATED) as archive:
                for member, data in members.items():
                    archive.writestr(member, data)
            print(f'Slicing {style} / {variant}', flush=True)
            with (ready / 'bambu-cli.log').open('w') as log:
                rc = subprocess.run(['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio',
                     '--slice', '0', '--arrange', '0', '--orient', '0', '--outputdir', str(ready),
                     '--export-3mf', native.name, str(staged)], cwd=ready,
                     stdout=log, stderr=subprocess.STDOUT).returncode
            assert rc == 0, (style, variant, rc)
        result = json.loads((ready / 'result.json').read_text())
        assert result['return_code'] == 0
        plate = result['sliced_plates'][0]
        assert len(plate['objects']) == 4
        with zipfile.ZipFile(staged) as archive:
            assert all(archive.read(key) == data for key, data in original.items() if key != SETTINGS)
        with zipfile.ZipFile(native) as archive:
            output_settings = json.loads(archive.read(SETTINGS))
            if variant == 'baseline':
                normalized_baseline = output_settings
            expected_output = dict(normalized_baseline)
            expected_output.update({key: value for key, value in settings.items() if saved.get(key) != value})
            assert output_settings == expected_output, {
                key: (expected_output.get(key), output_settings.get(key))
                for key in set(expected_output) | set(output_settings)
                if expected_output.get(key) != output_settings.get(key)}
            gcode = archive.read('Metadata/plate_1.gcode')
            assert hashlib.md5(gcode).hexdigest() == archive.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
            (job / 'preview.png').write_bytes(archive.read('Metadata/plate_1.png'))
        emitted = {}
        for index, part in enumerate(parts, 1):
            wall = wall_layers(native, part['identify_id'])
            assert wall
            emitted[part['name']] = runs(wall)
            regular = [(z, h) for z, h in wall if z > .21]
            if variant == 'all-fine' or (variant == 'fine-cover' and index == 3) or (variant == 'fine-upper' and index in (2, 3)):
                assert all(abs(h - .08) < .001 for _, h in regular), (variant, index, emitted)
            elif variant == 'fine-upper' and index == 1:
                assert all(abs(h - .08) < .001 for z, h in regular if z > upper_start + .24)
                assert all(abs(h - .24) < .001 for z, h in regular if z < upper_start - .24)
            else:
                assert all(abs(h - .24) < .001 for _, h in regular), (variant, index, emitted)
        record = {
            'style': style, 'variant': variant,
            'source_project': str(source.relative_to(ROOT)), 'source_sha256': source_hash,
            'staged_input': str(staged.relative_to(ROOT)), 'staged_sha256': sha(staged),
            'native_archive': str(native.relative_to(ROOT)), 'native_sha256': sha(native),
            'gcode_sha256': hashlib.sha256(gcode).hexdigest(),
            'settings_changes': {key: {'reference': saved.get(key), 'value': value}
                                 for key, value in settings.items() if saved.get(key) != value},
            'common_native_normalization': {key: {'project': saved.get(key), 'native': value}
                                            for key, value in normalized_baseline.items()
                                            if saved.get(key) != value},
            'fine_ranges_print_z_mm': ranges, 'fine_upper_base_start_mm': upper_start,
            'geometry_and_placement_unchanged': True,
            'total_estimated_seconds': plate['total_predication'],
            'model_estimated_seconds': plate['main_predication'],
            'filament_grams': sum(f['total_used_g'] for f in plate['filaments']),
            'slicer_warning': plate['warning_message'], 'wall_layer_runs': emitted,
            'object_count': 4, 'submitted': False
        }
        (job / 'comparison.json').write_text(json.dumps(record, indent=2) + '\n')
        results.append(record)
        (HERE / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
        print(json.dumps({'style': style, 'variant': variant,
                          'minutes': round(record['total_estimated_seconds'] / 60, 1),
                          'grams': round(record['filament_grams'], 2),
                          'fine_upper_base_start_mm': upper_start,
                          'warning': plate['warning_message']}), flush=True)
    assert sha(source) == source_hash
