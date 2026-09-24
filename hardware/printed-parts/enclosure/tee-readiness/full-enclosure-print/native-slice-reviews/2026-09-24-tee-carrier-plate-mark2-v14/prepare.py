"""Slice the carrier with six walls in its lower rounded band."""
from pathlib import Path
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
import zipfile

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'hardware/printed-parts/petgf.3mf').is_file())
BASE = ROOT / '.cache/prints/2026-09-24-tee-carrier-plate-mark2-v13'
JOB = ROOT / '.cache/prints/2026-09-24-tee-carrier-plate-mark2-v14'
STEM = 'tee-carrier-plate-black-z004-mark2-v14-six-wall-band-original-speeds'
source = BASE / 'tee-carrier-plate-black-z004-mark2-v13-steady-cooling-input.3mf'
target = JOB / (STEM + '-input.3mf')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(source) == '465b8609aed31dc10e74dd41d9c57796aec8ffac6b681a410832dd2a33c3905b'
assert not target.exists(), 'Keep prepared jobs immutable'
config = json.loads((BASE / 'job-config.json').read_text())
part = config['parts'][0]
assert sha(ROOT / part['stl']) == 'f781331deb3397d7b55b4d09e4fcaf68a05b9af8eb1d2f212530d18f34edca1c'
with zipfile.ZipFile(source) as archive:
    members = {name: archive.read(name) for name in archive.namelist()}
settings_member = 'Metadata/project_settings.config'
ranges_member = 'Metadata/layer_config_ranges.xml'
previous = json.loads(members[settings_member])
settings = dict(previous)
assert settings['enable_support'] == '0'
assert settings['wall_loops'] == '2'
assert settings['infill_wall_overlap'] == '15%'
assert settings['wall_sequence'] == 'inner wall/outer wall'
assert settings['fan_min_speed'] == settings['fan_max_speed'] == ['55']
assert settings['enable_overhang_bridge_fan'] == ['0']
assert settings['additional_cooling_fan_speed'] == ['0']
assert settings['nozzle_temperature'][0] == '280'
overrides = {'is_infill_first': '1'}
band_overrides = {
    'wall_loops': '6',
}
settings.update(overrides)
members[settings_member] = (json.dumps(settings, indent=2) + '\n').encode()
ranges = ET.fromstring(members[ranges_member])
bands = ranges.findall('./object/range')
assert len(bands) == 2
lower = bands[0]
assert float(lower.get('min_z')) == 0 and float(lower.get('max_z')) == 6.1
assert [(float(b.get('min_z')), float(b.get('max_z')),
         b.find("option[@opt_key='layer_height']").text) for b in bands] == [
             (0.0, 6.1, '0.08'), (14.9, 21.054, '0.08')]
for key, value in band_overrides.items():
    ET.SubElement(lower, 'option', opt_key=key).text = value
members[ranges_member] = ET.tostring(ranges, encoding='utf-8', xml_declaration=True)
with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
    for name, payload in members.items():
        archive.writestr(name, payload)
with zipfile.ZipFile(source) as a, zipfile.ZipFile(target) as b:
    changed = [name for name in a.namelist() if a.read(name) != b.read(name)]
    assert set(changed) == {settings_member, ranges_member} and b.testzip() is None
differences = {key: {'reference': previous[key], 'value': value}
               for key, value in overrides.items()}
config.update(archive_stem=STEM,
              title='Tee carrier only; six walls at Z 0–6.1 mm; infill first; 15% overlap; no supports; Mark2')
config['settings_overrides'].update(overrides)
config['layer_ranges_mm']['enclosure-tee-carrier-plate'][0]['settings_overrides'] = band_overrides
(JOB / 'job-config.json').write_text(json.dumps(config, indent=2) + '\n')
preparation = {
    'reference_input': str(source.relative_to(ROOT)), 'reference_input_sha256': sha(source),
    'staged_input': str(target.relative_to(ROOT)), 'staged_input_sha256': sha(target),
    'changed_archive_members': changed, 'setting_differences': differences,
    'lower_band_mm': [0, 6.1], 'lower_band_overrides': band_overrides,
    'source_stl_sha256': sha(ROOT / part['stl']), 'source_step_sha256': sha(ROOT / part['step']),
    'identical_member_sha256': {name: hashlib.sha256(payload).hexdigest()
                               for name, payload in members.items()
                               if name not in {settings_member, ranges_member}},
    'geometry_placement_and_layer_heights_identical': True,
    'base_wall_loops': 2, 'infill_wall_overlap': '15%',
    'retained_infill': '15% grid',
    'retained_cooling': 'Part fan 0% on layers 1–3, 55% on layers 4–189; auxiliary fan off.',
    'wall_sequence': 'Print infill first enabled globally; inner walls precede outer walls. Native first-layer wall-first behavior remains.',
    'speed_and_acceleration_settings': 'All inherited process and filament speed and acceleration settings are unchanged, including overhang speeds. The lower range overrides wall count only.',
    'nozzle_temperature_c': 280, 'first_layer_nozzle_temperature_c': 265,
    'bed_temperature_c': 80, 'chamber_temperature_setting_c': 0,
    'printer': 'Mark2', 'requested_z_trim_mm': .04,
    'hypothesis': 'Six walls in the lower rounded band may retain the expanding edge between infill contacts. Printing infill first supplies those contacts before the surrounding walls. This combined wall-strategy trial does not isolate individual contributions.',
    'independent_variable': 'Six walls at Z 0–6.1 mm; infill first throughout the print. Speeds and overlap are unchanged.',
    'user_authority': 'Derek requests the wall trial, confirms the bed is clear, approves six walls and sequence, specifies the height-range scope, explicitly retains 15% overlap and requests no speed reductions.',
    'physical_reference': 'hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-24-tee-carrier-plate-mark2-v13/physical-result.json',
    'user_observation': 'Failures occur between infill contacts; the contact locations appear to hold the outside edge out.',
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
                  'setting_differences': differences, 'band_overrides': band_overrides}, indent=2))
raise SystemExit(result.returncode)
