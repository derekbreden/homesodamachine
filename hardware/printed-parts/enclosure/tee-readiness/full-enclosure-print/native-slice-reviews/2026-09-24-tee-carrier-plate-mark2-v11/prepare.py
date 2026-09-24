"""Repeat the accepted carrier plate with automatic support generation disabled."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

ROOT = Path(__file__).resolve()
while not (ROOT / 'hardware/printed-parts/petgf.3mf').is_file():
    ROOT = ROOT.parent
BASE = ROOT / '.cache/prints/2026-09-24-tee-carrier-plate-mark2-v10'
JOB = ROOT / '.cache/prints/2026-09-24-tee-carrier-plate-mark2-v11'
STEM = 'tee-carrier-plate-black-z004-mark2-v11-no-supports'
source = BASE / 'tee-carrier-plate-black-z004-mark2-v10-input.3mf'
target = JOB / (STEM + '-input.3mf')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(source) == '91a5b12ad968b108c9a8911b5952ff5a826bb50d93db63f1a034bd60ee3fb822'
assert not target.exists(), 'Keep each prepared job immutable'
with zipfile.ZipFile(source) as archive:
    members = {name: archive.read(name) for name in archive.namelist()}
settings_name = 'Metadata/project_settings.config'
previous = json.loads(members[settings_name])
settings = dict(previous)
assert settings['enable_support'] == '1'
settings['enable_support'] = '0'
members[settings_name] = (json.dumps(settings, indent=2) + '\n').encode()
with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for name, payload in members.items():
        archive.writestr(name, payload)
with zipfile.ZipFile(source) as old, zipfile.ZipFile(target) as new:
    changed = [name for name in old.namelist() if old.read(name) != new.read(name)]
    assert changed == [settings_name], changed
    assert new.testzip() is None
differences = {key: {'reference': previous.get(key), 'value': settings.get(key)}
               for key in set(previous) | set(settings) if previous.get(key) != settings.get(key)}
assert differences == {'enable_support': {'reference': '1', 'value': '0'}}
config = json.loads((BASE / 'job-config.json').read_text())
config['archive_stem'] = STEM
config['title'] = 'Tee carrier only; no supports; 0.24 mm base, 0.08 mm exposed rounds; Mark2'
config['settings_overrides']['enable_support'] = '0'
(JOB / 'job-config.json').write_text(json.dumps(config, indent=2) + '\n')
preparation = {
    'reference_input': str(source.relative_to(ROOT)),
    'reference_input_sha256': sha(source),
    'staged_input': str(target.relative_to(ROOT)),
    'staged_input_sha256': sha(target),
    'changed_archive_members': changed,
    'setting_differences': differences,
    'identical_member_sha256': {name: hashlib.sha256(payload).hexdigest()
                               for name, payload in members.items() if name != settings_name},
    'geometry_and_placement_identical': True,
    'layer_ranges_identical': True,
    'printer': 'Mark2',
    'requested_z_trim_mm': 0.04,
    'user_authority': 'Repeat the successful tee carrier with all the same settings and no supports; plate clear.'
}
(JOB / 'preparation.json').write_text(json.dumps(preparation, indent=2) + '\n')
ready = JOB / 'ready'
ready.mkdir(exist_ok=True)
with (ready / 'bambu-cli.log').open('w') as log:
    result = subprocess.run([
        '/Applications/BambuStudio.app/Contents/MacOS/BambuStudio', '--slice', '0',
        '--arrange', '0', '--orient', '0', '--outputdir', str(ready),
        '--export-3mf', STEM + '.gcode.3mf', str(target)
    ], cwd=ready, stdout=log, stderr=subprocess.STDOUT)
print(json.dumps({'slice_exit': result.returncode, 'input_sha256': sha(target),
                  'setting_differences': differences}, indent=2))
raise SystemExit(result.returncode)
