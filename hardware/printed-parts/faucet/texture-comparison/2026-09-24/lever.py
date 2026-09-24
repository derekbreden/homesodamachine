"""Time the physically accepted side-down lever at the two texture heights."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve()
while not (ROOT / 'hardware/printed-parts/petgf.3mf').is_file():
    ROOT = ROOT.parent
HERE = ROOT / '.cache/prints/2026-09-24-faucet-texture-comparison'
sys.path.insert(0, str(ROOT / 'hardware/scripts'))
from verify_round_layer_band import wall_layers

source = ROOT / 'hardware/printed-parts/faucet/lever-replica/lever-original-wide-white-z004-mark2.3mf'
SETTINGS = 'Metadata/project_settings.config'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
source_hash = sha(source)
with zipfile.ZipFile(source) as archive:
    original = {name: archive.read(name) for name in archive.namelist()}
saved = json.loads(original[SETTINGS])
results = []
for variant in ['baseline', 'all-fine']:
    job = HERE / f'lever-{variant}'
    job.mkdir(exist_ok=True)
    ready = job / 'ready'
    ready.mkdir(exist_ok=True)
    staged = job / f'lever-texture-{variant}.3mf'
    native = ready / f'lever-texture-{variant}.gcode.3mf'
    members = dict(original)
    settings = dict(saved)
    if variant == 'all-fine':
        settings.update(layer_height='0.08', initial_layer_print_height='0.08')
    members[SETTINGS] = (json.dumps(settings, indent=2) + '\n').encode()
    if not native.exists():
        with zipfile.ZipFile(staged, 'w', zipfile.ZIP_DEFLATED) as archive:
            for name, data in members.items(): archive.writestr(name, data)
        print(f'Slicing lever / {variant}', flush=True)
        with (ready / 'bambu-cli.log').open('w') as log:
            rc = subprocess.run(['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio',
                 '--slice', '0', '--arrange', '0', '--orient', '0', '--outputdir', str(ready),
                 '--export-3mf', native.name, str(staged)], cwd=ready,
                 stdout=log, stderr=subprocess.STDOUT).returncode
        assert rc == 0
    with zipfile.ZipFile(staged) as archive:
        assert all(archive.read(name) == data for name, data in original.items() if name != SETTINGS)
    with zipfile.ZipFile(native) as archive:
        output = json.loads(archive.read(SETTINGS))
        if variant == 'baseline': baseline = output
        expected = dict(baseline)
        if variant == 'all-fine': expected.update(layer_height='0.08', initial_layer_print_height='0.08')
        assert output == expected
        gcode = archive.read('Metadata/plate_1.gcode')
        assert hashlib.md5(gcode).hexdigest() == archive.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
    layers = wall_layers(native, 1901)
    assert layers
    if variant == 'all-fine': assert all(abs(h-.08) < .001 for _, h in layers)
    result = json.loads((ready / 'result.json').read_text())
    assert result['return_code'] == 0
    plate = result['sliced_plates'][0]
    record = {'part': 'Accepted lever replica', 'variant': variant,
              'source_project': str(source.relative_to(ROOT)), 'source_sha256': source_hash,
              'native_archive': str(native.relative_to(ROOT)), 'native_sha256': sha(native),
              'gcode_sha256': hashlib.sha256(gcode).hexdigest(),
              'geometry_and_placement_unchanged': True,
              'total_estimated_seconds': plate['total_predication'],
              'model_estimated_seconds': plate['main_predication'],
              'filament_grams': sum(f['total_used_g'] for f in plate['filaments']),
              'slicer_warning': plate['warning_message'], 'wall_layer_count': len(layers),
              'wall_layer_heights': sorted({round(h,4) for _,h in layers}), 'submitted': False}
    results.append(record)
    (job / 'comparison.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record), flush=True)
assert sha(source) == source_hash
(HERE / 'lever-results.json').write_text(json.dumps(results, indent=2) + '\n')
