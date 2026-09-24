"""Verify the six-wall carrier experiment against the stopped steady-cooling reference."""
from pathlib import Path
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve()
while not (ROOT / 'hardware/printed-parts/petgf.3mf').is_file():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / 'hardware/scripts'))
from verify_round_layer_band import wall_layers, check_span
from enclosure_support_audit import audit

BASE = ROOT / '.cache/prints/2026-09-24-tee-carrier-plate-mark2-v13'
JOB = ROOT / '.cache/prints/2026-09-24-tee-carrier-plate-mark2-v14'
old = next((BASE / 'ready').glob('*.gcode.3mf'))
new = next((JOB / 'ready').glob('*.gcode.3mf'))
staged = next(JOB.glob('*-input.3mf'))
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(old) == '9ccb143d9926611baf3bd0bc89d0fbb3c6235f1dc21fd354a603f6f3a2162ac4'
with zipfile.ZipFile(old) as a, zipfile.ZipFile(new) as b:
    assert b.testzip() is None
    old_s = json.loads(a.read('Metadata/project_settings.config'))
    new_s = json.loads(b.read('Metadata/project_settings.config'))
    differences = {k: {'reference': old_s.get(k), 'value': new_s.get(k)}
                   for k in set(old_s) | set(new_s) if old_s.get(k) != new_s.get(k)}
    assert differences == json.loads((JOB / 'preparation.json').read_text())['setting_differences'], differences
    range_tree = ET.fromstring(b.read('Metadata/layer_config_ranges.xml'))
    native_ranges = [{'min_z': float(r.get('min_z')), 'max_z': float(r.get('max_z')),
                      'settings': {o.get('opt_key'): o.text for o in r.findall('option')}}
                     for r in range_tree.findall('./object/range')]
    assert len(native_ranges) == 2, native_ranges
    lower = native_ranges[0]
    assert lower['min_z'] == 0 and lower['max_z'] == 6.1, lower
    assert lower['settings'] == {'layer_height': '0.08', 'wall_loops': '6'}, lower
    assert native_ranges[1]['settings'] == {'layer_height': '0.08'}, native_ranges[1]
    assert new_s['outer_wall_speed'] == ['200'] * 5
    assert new_s['inner_wall_speed'] == ['300'] * 5
    gc = b.read('Metadata/plate_1.gcode')
    assert hashlib.md5(gc).hexdigest() == b.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
    text = gc.decode()
    (JOB / 'ready/plate_1.gcode').write_bytes(gc)
    (JOB / 'preview.png').write_bytes(b.read('Metadata/plate_1.png'))
    features = sorted(set(re.findall(r'^; FEATURE: (.*)', text, re.M)))
    assert not any('support' in feature.lower() for feature in features), features
    trims = [float(v) for v in re.findall(r'^\s*G29\.1 Z([-+\d.]+)', text, re.M)]
    assert trims == [0.0, 0.02], trims
    layers = [float(v) for v in re.findall(r'^; Z_HEIGHT: ([\d.]+)', text, re.M)]
    assert len(layers) == 189 and all(b > a for a, b in zip(layers, layers[1:]))
    plate = ET.fromstring(b.read('Metadata/slice_info.config')).find('plate')
    objects = plate.findall('object')
    assert len(objects) == 1 and objects[0].attrib == {
        'identify_id': '1901', 'name': 'enclosure-tee-carrier-plate', 'skipped': 'false'}
    assert {m.attrib['key']: m.attrib['value'] for m in plate.findall('metadata')}['support_used'] == 'false'
    assert set(re.findall(r'^; OBJECT_ID: (\d+)', text, re.M)) == {'1901'}

wall = wall_layers(new, 1901)
assert wall == wall_layers(old, 1901), 'Every emitted model wall layer must match the reference'
runs = []
for z, h in sorted({(round(z, 4), round(h, 4)) for z, h in wall}):
    if not runs or runs[-1]['height'] != h:
        runs.append({'height': h, 'bottom': round(z-h, 4), 'last_z': z, 'count': 1})
    else:
        runs[-1].update(last_z=z, count=runs[-1]['count'] + 1)
assert [r['height'] for r in runs] == [.08, .24, .08]
assert [r['count'] for r in runs] == [76, 37, 76]
rounds = [check_span(wall, 'aft-R6', 0, 6, .08, .001),
          check_span(wall, 'fore-R6', 15.054, 21.054, .08, .001)]
assert all(r['pass'] for r in rounds)
support = audit(JOB / 'ready/plate_1.gcode', 'enclosure-tee-carrier-plate',
                profile=staged, include_unlabelled_support=True)
assert support['summary']['support_bodies'] == 0
result = json.loads((JOB / 'ready/result.json').read_text())
assert result['return_code'] == 0
assert len(result['sliced_plates']) == 1
assert result['sliced_plates'][0]['warning_message'] == ''
assert 'Support' not in result['sliced_plates'][0]['feature_type_times']
body = text[text.index('; CHANGE_LAYER'):text.rindex('; FEATURE: Custom')]
fan_commands = []
layer = 0
part_fan = None
aux_fan = None
layer_fans = {}
for line in body.splitlines():
    if line.startswith('; CHANGE_LAYER'):
        layer += 1
    command = line.split(';', 1)[0].strip()
    if command.startswith('M106 '):
        words = dict(re.findall(r'([PS])([-+\d.]+)', command))
        fan, value = int(float(words.get('P', 1))), float(words.get('S', 255))
        fan_commands.append({'layer': layer, 'fan': fan, 'value': value})
        if fan == 1:
            part_fan = value
        elif fan == 2:
            aux_fan = value
    elif re.match(r'G[0123]\s', command) and re.search(r'\b[XY][-+\d.]', command):
        amount = re.search(r'\bE([-+\d.]+)', command)
        if amount and float(amount.group(1)) > 0:
            assert part_fan is not None and aux_fan == 0, (layer, part_fan, aux_fan)
            percentage = round(part_fan / 255 * 100, 3)
            layer_fans.setdefault(layer, set()).add(percentage)
            expected = 0 if layer <= 3 else 55
            assert abs(percentage - expected) < .02, (layer, percentage, expected)
assert set(layer_fans) == set(range(1, 190))
fan_runs = []
for layer, values in layer_fans.items():
    assert len(values) == 1
    percent = next(iter(values))
    if not fan_runs or fan_runs[-1]['part_fan_percent'] != percent:
        fan_runs.append({'first_layer': layer, 'last_layer': layer, 'part_fan_percent': percent})
    else:
        fan_runs[-1]['last_layer'] = layer
assert fan_runs == [{'first_layer': 1, 'last_layer': 3, 'part_fan_percent': 0.0},
                    {'first_layer': 4, 'last_layer': 189, 'part_fan_percent': 55.0}]
assert new_s['wall_loops'] == '2'
assert new_s['infill_wall_overlap'] == '15%'
assert new_s['is_infill_first'] == '1'
assert new_s['wall_sequence'] == 'inner wall/outer wall'
assert new_s['sparse_infill_density'] == '15%'
assert new_s['sparse_infill_pattern'] == 'grid'
assert new_s['nozzle_temperature'][0] == '280'
assert new_s['nozzle_temperature_initial_layer'][0] == '265'
assert new_s['chamber_temperatures'] == ['0']
assert new_s['textured_plate_temp'] == ['80']
assert re.findall(r'^M104 S([\d.]+)', body, re.M) == ['280']
proof = {
    'reference_archive': str(old.relative_to(ROOT)), 'reference_archive_sha256': sha(old),
    'native_archive': str(new.relative_to(ROOT)), 'native_archive_sha256': sha(new),
    'gcode_sha256': hashlib.sha256(gc).hexdigest(),
    'setting_differences': differences, 'emitted_wall_layers_identical': True,
    'native_layer_ranges': native_ranges, 'global_wall_loops': 2, 'infill_wall_overlap': '15%',
    'part_and_aux_fan_commands_during_model': fan_commands,
    'part_fan_runs_during_model_extrusion': fan_runs, 'aux_fan_off_during_model_extrusion': True,
    'first_layer_nozzle_c': 265, 'remaining_model_nozzle_c': 280,
    'bed_c': 80, 'chamber_setting_c': 0,
    'model_layer_runs': runs, 'rounds': rounds, 'support_feature_paths': 0,
    'support_bodies': 0, 'plate_object_count': 1, 'layer_count': len(layers),
    'emitted_z_trim_commands_mm': trims, 'slicer': 'BambuStudio 02.08.02.61',
    'slicer_return_code': 0, 'slicer_warning_message': '', 'pass': True
}
(JOB / 'verification.json').write_text(json.dumps(proof, indent=2) + '\n')
(JOB / 'support-audit.json').write_text(json.dumps(support, indent=2, sort_keys=True) + '\n')
print(json.dumps(proof, indent=2))
