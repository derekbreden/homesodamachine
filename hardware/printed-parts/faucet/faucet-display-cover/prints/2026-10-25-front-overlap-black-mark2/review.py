"""Review the one-cover native slice and preserve all settings and commands."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import re
import shutil
import sys

from prepare import HERE, ROOT, STEM, writer
sys.path.insert(0, str(ROOT / 'hardware/printed-parts/faucet/industrial'))
from review_rim_supports import material_review
NATIVE = ROOT / '.cache/faucet-front-overlap-mark2/native'


def main():
    project = HERE / (STEM + '.3mf')
    report = json.loads(project.with_suffix('.print.json').read_text())
    if '--commands-only' in sys.argv:
        reading = json.loads(project.with_suffix('.support-audit.json').read_text())
        assert reading['project_sha256'] == writer.digest(project.read_bytes())
        assert reading['parts'][0]['inputs']['plate_gcode_sha256'] == writer.digest((NATIVE / 'plate_1.gcode').read_bytes())
    else:
        reading = writer.slice_review(project, report, NATIVE)
    archive = HERE / (STEM + '.gcode.3mf')
    shutil.copyfile(NATIVE / archive.name, archive)
    with ZipFile(project) as prepared, ZipFile(archive) as native:
        command = native.read('Metadata/plate_1.gcode')
        assert hashlib.md5(command).hexdigest() == native.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        assert command == (NATIVE / 'plate_1.gcode').read_bytes()
        settings = {'prepared_project_settings': json.loads(prepared.read(writer.SETTINGS_MEMBER)),
            'native_project_settings': json.loads(native.read(writer.SETTINGS_MEMBER)),
            'prepared_xml': {n: prepared.read(n).decode() for n in ['Metadata/model_settings.config', 'Metadata/layer_config_ranges.xml']},
            'native_xml': {n: native.read(n).decode() for n in ['Metadata/model_settings.config', 'Metadata/layer_config_ranges.xml'] if n in native.namelist()},
            'filament_presets': {n: native.read(n).decode() for n in native.namelist() if n.startswith('Metadata/filament_settings_')}}
    (HERE / 'all-settings.json').write_text(json.dumps(settings, indent=2) + '\n')
    material, _ = material_review(NATIVE / 'plate_1.gcode', report,
        localized_cooling=True, first_three_max_z=.72)
    heights = [float(x) for x in re.findall(rb'^; Z_HEIGHT: ([-+0-9.]+)', command, re.M)]
    increments = Counter(round(b-a, 5) for a,b in zip([0.] + heights, heights))
    assert set(increments) == {.24}, increments
    trims = [float(x) for x in re.findall(rb'^\s*G29\.1 Z([-+0-9.]+)', command, re.M)]
    assert trims == [0., .02], trims
    result = {'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
        'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
        'gcode_sha256': hashlib.sha256(command).hexdigest(),
        'embedded_checksum_matches': True, 'emitted_trim_values_mm': trims,
        'layer_height_mm': .24, 'first_bed_layer_height_mm': .24,
        'layer_count': len(heights), 'layer_increment_counts_mm': dict(increments),
        'material_commands': material, 'fit': reading['fit'], 'plates': reading['plates'],
        'scope': 'Exact one-cover archive, source mesh, complete settings, native commands and deposited-bead bounds. The front extension has no physical result yet.'}
    (HERE / 'native-review.json').write_text(json.dumps(result, indent=2) + '\n')
    readiness = {'status': 'native slice reviewed; authorized for Mark2 submission',
        'project_sha256': report['project_sha256'], 'archive_sha256': result['archive_sha256'],
        'launch_authorized': True, 'submitted': False, 'parts': ['sculpted-display-cover'],
        'full_settings': 'all-settings.json', 'native_review': 'native-review.json',
        'support_audit': project.with_suffix('.support-audit.json').name}
    (HERE / 'readiness.json').write_text(json.dumps(readiness, indent=2) + '\n')
    print(json.dumps({'archive': str(archive), 'layers': len(heights), 'plates': reading['plates'], 'bed_margin_mm': reading['fit']['complete_layer_bead_minimum_bed_margin_mm']}, indent=2), flush=True)


if __name__ == '__main__':
    main()
