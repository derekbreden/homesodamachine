"""Verify the support-free repeat against the successful carrier's native slice."""
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

BASE = ROOT / '.cache/prints/2026-09-24-tee-carrier-plate-mark2-v10'
JOB = ROOT / '.cache/prints/2026-09-24-tee-carrier-plate-mark2-v11'
old = next((BASE / 'ready').glob('*.gcode.3mf'))
new = next((JOB / 'ready').glob('*.gcode.3mf'))
staged = next(JOB.glob('*-input.3mf'))
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(old) == 'e1632e613f46a5546c6454eb17716ebf9770af67473733dc71e76482f45a2cdd'
with zipfile.ZipFile(old) as a, zipfile.ZipFile(new) as b:
    assert b.testzip() is None
    old_s = json.loads(a.read('Metadata/project_settings.config'))
    new_s = json.loads(b.read('Metadata/project_settings.config'))
    differences = {k: {'reference': old_s.get(k), 'value': new_s.get(k)}
                   for k in set(old_s) | set(new_s) if old_s.get(k) != new_s.get(k)}
    assert differences == {'enable_support': {'reference': '1', 'value': '0'}}, differences
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
proof = {
    'reference_archive': str(old.relative_to(ROOT)), 'reference_archive_sha256': sha(old),
    'native_archive': str(new.relative_to(ROOT)), 'native_archive_sha256': sha(new),
    'gcode_sha256': hashlib.sha256(gc).hexdigest(),
    'setting_differences': differences, 'emitted_wall_layers_identical': True,
    'model_layer_runs': runs, 'rounds': rounds, 'support_feature_paths': 0,
    'support_bodies': 0, 'plate_object_count': 1, 'layer_count': len(layers),
    'emitted_z_trim_commands_mm': trims, 'slicer': 'BambuStudio 02.08.02.61',
    'slicer_return_code': 0, 'slicer_warning_message': '', 'pass': True
}
(JOB / 'verification.json').write_text(json.dumps(proof, indent=2) + '\n')
(JOB / 'support-audit.json').write_text(json.dumps(support, indent=2, sort_keys=True) + '\n')
print(json.dumps(proof, indent=2))
