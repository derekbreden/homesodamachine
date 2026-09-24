"""Slice the carrier-only steady-cooling experiment without changing its geometry or temperatures."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'hardware/printed-parts/petgf.3mf').is_file())
BASE = ROOT / '.cache/prints/2026-09-24-tee-carrier-plate-mark2-v11'
JOB = ROOT / '.cache/prints/2026-09-24-tee-carrier-plate-mark2-v13'
STEM = 'tee-carrier-plate-black-z004-mark2-v13-steady-cooling'
source = BASE / 'tee-carrier-plate-black-z004-mark2-v11-no-supports-input.3mf'
target = JOB / (STEM + '-input.3mf')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(source) == '9e1270590f23c6201786808f86c2228fba7ffba429a6254e209cd3a25c290322'
assert not target.exists(), 'Keep prepared jobs immutable'
config = json.loads((BASE / 'job-config.json').read_text())
part = config['parts'][0]
assert sha(ROOT / part['stl']) == 'f781331deb3397d7b55b4d09e4fcaf68a05b9af8eb1d2f212530d18f34edca1c'
with zipfile.ZipFile(source) as archive:
    members = {name: archive.read(name) for name in archive.namelist()}
settings_member = 'Metadata/project_settings.config'
previous = json.loads(members[settings_member])
settings = dict(previous)
assert settings['enable_support'] == '0'
assert settings['fan_min_speed'] == settings['overhang_fan_speed'] == ['0']
assert settings['additional_cooling_fan_speed'] == ['0']
assert settings['nozzle_temperature'][0] == '280'
overrides = {'fan_min_speed': ['55'], 'fan_max_speed': ['55'], 'enable_overhang_bridge_fan': ['0']}
settings.update(overrides)
members[settings_member] = (json.dumps(settings, indent=2) + '\n').encode()
with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
    for name, payload in members.items():
        archive.writestr(name, payload)
with zipfile.ZipFile(source) as a, zipfile.ZipFile(target) as b:
    changed = [name for name in a.namelist() if a.read(name) != b.read(name)]
    assert changed == [settings_member] and b.testzip() is None
differences = {key: {'reference': previous[key], 'value': value}
               for key, value in overrides.items()}
config.update(archive_stem=STEM, title='Tee carrier only; no supports; steady 55% part cooling after layer 3; Mark2')
config['settings_overrides'].update(overrides)
(JOB / 'job-config.json').write_text(json.dumps(config, indent=2) + '\n')
preparation = {
    'reference_input': str(source.relative_to(ROOT)), 'reference_input_sha256': sha(source),
    'staged_input': str(target.relative_to(ROOT)), 'staged_input_sha256': sha(target),
    'changed_archive_members': changed, 'setting_differences': differences,
    'source_stl_sha256': sha(ROOT / part['stl']), 'source_step_sha256': sha(ROOT / part['step']),
    'identical_member_sha256': {name: hashlib.sha256(payload).hexdigest()
                               for name, payload in members.items() if name != settings_member},
    'geometry_placement_and_layer_ranges_identical': True,
    'nozzle_temperature_c': 280, 'first_layer_nozzle_temperature_c': 265,
    'bed_temperature_c': 80, 'chamber_temperature_setting_c': 0,
    'printer': 'Mark2', 'requested_z_trim_mm': .04,
    'hypothesis': 'Steady 55% cooling may preserve the deposited edge and its overlap with the next perimeter. This tests local shape retention; the thermal cause remains unconfirmed.',
    'independent_variable': 'Steady 55% part cooling after the unchanged first three fan-off layers; disable the zero-fan overhang override.',
    'user_authority': 'Mark2 bed is clear for whatever you would like to try.',
    'physical_reference': 'hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-24-tee-carrier-plate-mark2-v12/physical-result.json',
    'reference_cooling_reading': 'hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-24-tee-carrier-plate-mark2-v12/v11-cooling-reading.json',
}
(JOB / 'preparation.json').write_text(json.dumps(preparation, indent=2) + '\n')
ready = JOB / 'ready'
ready.mkdir(exist_ok=True)
with (ready / 'bambu-cli.log').open('w') as log:
    result = subprocess.run([
        '/Applications/BambuStudio.app/Contents/MacOS/BambuStudio', '--slice', '0',
        '--arrange', '0', '--orient', '0', '--outputdir', str(ready),
        '--export-3mf', STEM + '.gcode.3mf', str(target)],
        cwd=ready, stdout=log, stderr=subprocess.STDOUT)
print(json.dumps({'slice_exit': result.returncode, 'input_sha256': sha(target),
                  'setting_differences': differences}, indent=2))
raise SystemExit(result.returncode)
