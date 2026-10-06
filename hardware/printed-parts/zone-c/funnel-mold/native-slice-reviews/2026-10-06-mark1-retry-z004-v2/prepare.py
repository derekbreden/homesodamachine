"""Prepare the authorized +0.04 mm Mark1 retry; preserve geometry and other settings."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'tools').is_dir())
PUBLIC = Path(__file__).resolve().parent
SOURCE_DIR = PUBLIC.parent / '2026-10-06-mark1-retry-v1'
SOURCE = SOURCE_DIR / 'funnel-mold-mark1-retry.3mf'
DESTINATION = PUBLIC / 'funnel-mold-mark1-retry-z004.3mf'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE) == '76cfd1ae322feaab87c0a59eb13629437f229594ca5eb90aed11f3a453367807'
assert not DESTINATION.exists()
with zipfile.ZipFile(SOURCE) as z:
    payloads = {n: z.read(n) for n in z.namelist()}
settings = json.loads(payloads['Metadata/project_settings.config'])
original = dict(settings)
assert settings['machine_start_gcode'].count('0.18') == 5
settings['machine_start_gcode'] = settings['machine_start_gcode'].replace('0.18', '0.04')
settings['printer_settings_id'] = 'Bambu Lab H2C 0.4 Standard +0.04 Z trim'
assert settings['enable_wrapping_detection'] == '0'
payloads['Metadata/project_settings.config'] = (json.dumps(settings, indent=2) + '\n').encode()
with zipfile.ZipFile(DESTINATION, 'x', zipfile.ZIP_DEFLATED) as z:
    for n, data in payloads.items(): z.writestr(n, data)
with zipfile.ZipFile(SOURCE) as a, zipfile.ZipFile(DESTINATION) as b:
    assert b.testzip() is None
    changed = [n for n in a.namelist() if a.read(n) != b.read(n)]
    assert changed == ['Metadata/project_settings.config']
    mesh = {n: hashlib.sha256(b.read(n)).hexdigest() for n in b.namelist() if n.startswith('3D/Objects/')}
record = json.loads((SOURCE_DIR / 'preparation-review.json').read_text())
record['scope'] = 'Authorized lower-trim cavity retry. No Send attempted; native review required before the one authorized Send.'
record['selected_recipe']['printer_settings_id'] = settings['printer_settings_id']
record['preparation'] = {
    'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
    'prepared_project': str(DESTINATION.relative_to(ROOT)), 'prepared_project_sha256': sha(DESTINATION),
    'setting_changes': {k: {'source': original[k], 'prepared': settings[k]} for k in settings if original[k] != settings[k]},
    'changed_container_entries': changed, 'embedded_geometry_byte_identical': True,
    'embedded_geometry_sha256': mesh, 'placements_unchanged': True, 'all_other_payloads_identical': True,
    'requested_z_trim_mm': 0.04, 'expected_emitted_z_trim_mm': 0.02,
}
(PUBLIC / 'preparation-review.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'project':str(DESTINATION.relative_to(ROOT)), 'sha256':sha(DESTINATION),'requested_trim_mm':0.04,'expected_emitted_trim_mm':0.02,'geometry_and_placement':'unchanged','probing':'Off'},indent=2))
