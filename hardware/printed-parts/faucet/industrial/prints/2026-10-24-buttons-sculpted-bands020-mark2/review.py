"""Manual review of this exact requested print and its emitted commands."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import re
import shutil
import sys

HERE = Path(__file__).resolve().parent
INDUSTRIAL = HERE.parents[1]
ROOT = next(p for p in HERE.parents if (p / 'tools/bambu_print.py').is_file())
NATIVE = ROOT / '.cache/faucet-buttons-bands020-mark2/native'
STEM = '2026-10-24-industrial-sculpted-buttons-bands020v2-black-left04-z004-mark2'
sys.path.insert(0, str(INDUSTRIAL))
import prepare_print_project as industrial
from review_rim_supports import material_review
writer = industrial.writer


def main():
    project = HERE / (STEM + '.3mf')
    report = json.loads(project.with_suffix('.print.json').read_text())
    if '--commands-only' in sys.argv:
        reading = json.loads(project.with_suffix('.support-audit.json').read_text())
        assert reading['project_sha256'] == writer.digest(project.read_bytes())
    else:
        reading = writer.slice_review(project, report, NATIVE)
        industrial.write_readiness(project, report, reading, NATIVE)
    archive = HERE / (STEM + '.gcode.3mf')
    shutil.copyfile(NATIVE / archive.name, archive)
    with ZipFile(project) as prepared, ZipFile(archive) as native:
        psettings = json.loads(prepared.read(writer.SETTINGS_MEMBER))
        nsettings = json.loads(native.read(writer.SETTINGS_MEMBER))
        command = native.read('Metadata/plate_1.gcode')
        expected = native.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        assert hashlib.md5(command).hexdigest() == expected
        assert command == (NATIVE / 'plate_1.gcode').read_bytes()
        settings = {'prepared_project_settings': psettings, 'native_project_settings': nsettings,
                    'prepared_xml': {n: prepared.read(n).decode() for n in
                                     ('Metadata/model_settings.config', 'Metadata/layer_config_ranges.xml')},
                    'native_xml': {n: native.read(n).decode() for n in
                                   ('Metadata/model_settings.config', 'Metadata/layer_config_ranges.xml')},
                    'filament_presets': {n: native.read(n).decode() for n in native.namelist()
                                         if n.startswith('Metadata/filament_settings_')}}
    (HERE / 'all-settings.json').write_text(json.dumps(settings, indent=2) + '\n')
    material, _ = material_review(NATIVE / 'plate_1.gcode', report,
                                  localized_cooling=True, first_three_max_z=.72)
    heights = defaultdict(set)
    z, obj, feature = 0., None, ''
    names = {int(p['identify_id']): p['name'] for p in report['parts']}
    for raw in command.decode().splitlines():
        if raw.startswith('; Z_HEIGHT:'):
            z = float(raw.split(':', 1)[1])
        elif raw.startswith('; FEATURE:'):
            feature = raw.split(':', 1)[1].strip()
        elif raw.startswith('; start printing object, unique label id:'):
            obj = int(raw.rsplit(':', 1)[1])
        elif raw.startswith('; OBJECT_ID:'):
            obj = int(raw.rsplit(':', 1)[1])
        elif raw.startswith('; stop printing object'):
            obj = None
        elif obj in names and 'Support' not in feature and re.match(r'G[123] ', raw):
            e = re.search(r' E([-+]?(?:\d+(?:\.\d*)?|\.\d+))', raw)
            if e and float(e[1]) > 0:
                heights[names[obj]].add(z)
    layers = {}
    for name, values in heights.items():
        values = sorted(values)
        layers[name] = {'first_z_mm': values[0], 'last_z_mm': values[-1],
                        'model_z_count': len(values),
                        'z_increment_counts_mm': dict(Counter(round(b - a, 5) for a, b in zip([0.] + values, values))),
                        'first_band_z_mm': [v for v in values if 16.7 <= v <= 29.3],
                        'second_band_z_mm': [v for v in values if 54.9 <= v <= 68.4]}
    trims = [float(x) for x in re.findall(rb'^\s*G29\.1 Z([-+0-9.]+)', command, re.M)]
    assert trims == [0., .02], trims
    result = {'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
              'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
              'gcode_sha256': hashlib.sha256(command).hexdigest(),
              'embedded_checksum_matches': True, 'emitted_trim_values_mm': trims,
              'first_bed_layer_height_mm': .24, 'normal_layer_height_mm': .24,
              'base_layer_bands': report['base_layer_bands'],
              'part_layer_planes': layers, 'material_commands': material,
              'fit': reading['fit'], 'plates': reading['plates'],
              'scope': 'Exact native archive, sources, commands and deposited-bead bounds; physical fit awaits the requested print.'}
    (HERE / 'native-review.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'archive': str(archive), 'layers': {n:{k:v for k,v in r.items() if not k.endswith('band_z_mm')} for n,r in layers.items()},
                      'fit': reading['fit'], 'plates': reading['plates']}, indent=2), flush=True)


if __name__ == '__main__':
    main()
