"""Slice the face-up bezel and its angled tree-supported receiver together on H2C."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

import face_up_trial as trial

ROOT, HERE = trial.ROOT, trial.HERE
sys.path.insert(0, str(ROOT/'hardware/printed-parts/faucet'))
import refresh_print_project as writer

JOB = ROOT/'.cache/prints/2026-09-29-display-flat-wings-h2c-v1'
STEM = 'display-face-up-cover-receiver-z018-h2c-v1'


def main():
    JOB.mkdir(parents=True, exist_ok=True)
    staged = JOB/(STEM+'-input.3mf')
    assert not staged.exists(), 'Keep trial archives immutable.'
    profile = ROOT/'hardware/printed-parts/petgf.3mf'
    report = writer.refresh(profile, staged,
        parts=((trial.NAME, HERE/(trial.NAME+'.stl'), 0.), (trial.RECEIVER, HERE/(trial.RECEIVER+'.stl'), 0.)),
        offsets=((0., 70.), (0., -55.)), title='Face-up display cover and matching receiver; H2C',
        z_trim=.18, plate_border=15.)
    with zipfile.ZipFile(staged) as z:
        members = {n:z.read(n) for n in z.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    settings.update(extruder_ams_count=['1#0|4#0', '1#0|4#0'],
                    support_filament='1', support_interface_filament='1', flush_into_support='0')
    members[writer.SETTINGS_MEMBER] = json.dumps(settings, indent=2).encode()
    cfg = ET.fromstring(members['Metadata/model_settings.config'])
    objects = cfg.findall('object')
    assert len(objects) == 2
    for key, value in {'enable_support':'0', 'brim_type':'no_brim', 'brim_width':'0'}.items():
        writer.metadata(objects[0], key, value)
    members['Metadata/model_settings.config'] = writer.xml(cfg)
    ranges = ET.Element('objects')
    obj = ET.SubElement(ranges, 'object', id='1')
    band = ET.SubElement(obj, 'range', min_z='0.2', max_z='0.48')
    ET.SubElement(band, 'option', opt_key='layer_height').text = '0.28'
    members['Metadata/layer_config_ranges.xml'] = writer.xml(ranges)
    writer.archive_write(staged, members)
    geometry = json.loads((HERE/'geometry-check.json').read_text())
    sources = [ROOT/p for p in geometry['source_sha256']] + [HERE/'geometry-check.json', Path(__file__), profile]
    report.update(project_sha256=hashlib.sha256(staged.read_bytes()).hexdigest(), printer='H2C',
        source_geometry_and_settings_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        requested_z_trim_mm=.18, expected_textured_plate_trim_mm=.16,
        identify_ids={'1901':trial.NAME, '1902':trial.RECEIVER},
        support_policy='Cover: no supports, back and wings on the bed. Receiver: saved PET-GF tree supports, 30 degree enclosure display plane.',
        support_clearance_mm={'XY':.4, 'top_Z':.45, 'bottom_Z':.3, 'first_layer_XY':.2},
        cover_layer_policy='0.20 first, 0.28 second to align wings, then 0.24. No show rounds in build Z.',
        physical_qualification='Fit trial only: insertion flex, full engagement, relaxed flatness and shake retention pending.',
        submitted=False)
    (JOB/'preparation.json').write_text(json.dumps(report, indent=2)+'\n')
    ready = JOB/'ready'
    ready.mkdir()
    command = ['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio', '--slice', '0', '--arrange', '0', '--orient', '0',
               '--outputdir', str(ready), '--export-3mf', STEM+'.gcode.3mf', str(staged)]
    (JOB/'slice-command.json').write_text(json.dumps(command, indent=2)+'\n')
    with (ready/'bambu-cli.log').open('w') as log:
        rc = subprocess.run(command, cwd=ready, stdout=log, stderr=subprocess.STDOUT).returncode
    print('SLICE_EXIT', rc)
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
