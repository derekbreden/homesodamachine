"""Natively slice the broad-leaf cover on Mark2 or its matching receiver on H2C."""

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import retention_trial as trial

ROOT, HERE = trial.ROOT, trial.HERE
sys.path.insert(0, str(ROOT/'hardware/printed-parts/faucet'))
import refresh_print_project as writer

JOBS = {
    'Mark2': (trial.COVER_NAME, .04, 180., 'display-cover-retention-black-z004-mark2-v12'),
    'H2C': (trial.RECEIVER_NAME, .18, 0., 'display-receiver-retention-black-z018-h2c-v2'),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('printer', choices=JOBS)
    args = parser.parse_args()
    name, trim, rotation, stem = JOBS[args.printer]
    job = ROOT/('.cache/prints/2026-09-28-display-retention-'+args.printer.lower())
    job.mkdir(parents=True, exist_ok=True)
    source = HERE/(name+'.stl')
    profile = ROOT/'hardware/printed-parts/petgf.3mf'
    staged = job/(stem+'-input.3mf')
    assert not staged.exists()
    assert sha(profile) == '3864deceaa295d0fffded05e445b77ee926e2706d8765fdc8bbf81a23fe98697'
    report = writer.refresh(profile, staged, parts=((name, source, rotation),),
                            offsets=((0., 0.),), title=f'Machine display retention trial; {args.printer}',
                            z_trim=trim, plate_border=15.)
    with zipfile.ZipFile(staged) as z:
        members = {n:z.read(n) for n in z.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    overrides = {'extruder_ams_count':['1#0|4#0','1#0|4#0'],
                 'support_remove_small_overhang':'0','support_top_z_distance':'0.24'}
    settings.update(overrides)
    assert settings['layer_height']=='0.24' and settings['initial_layer_print_height']=='0.2'
    assert settings['wall_loops']=='2' and settings['wall_sequence']=='inner wall/outer wall'
    assert settings['is_infill_first']=='0' and settings['infill_wall_overlap']=='15%'
    assert settings['filament_nozzle_map']==['0'] and settings['filament_colour']==['#000000']
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2)+'\n').encode()
    writer.archive_write(staged, members)
    sources = [source, source.with_suffix('.step'), HERE/'retention_trial.py',
               HERE/'geometry-check.json', Path(__file__).resolve(), profile]
    report.update({'project_sha256':sha(staged),
                   'source_geometry_and_settings_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sources},
                   'settings_sha256':hashlib.sha256(members[writer.SETTINGS_MEMBER]).hexdigest(),
                   'intentional_process_and_mapping_overrides':overrides,
                   'printer':args.printer,'requested_z_trim_mm':trim,
                   'expected_textured_plate_trim_mm':round(trim-.02,2),
                   'orientation':'Visible face on plate, leaves up.' if rotation else 'Display plane at 30 degrees, matching front-top.',
                   'support_policy':'Functional square bearing faces supported with open removal lanes.',
                   'layer_policy':'0.24 mm with 0.20 mm first layer; cosmetic bezel rounds are in XY.'})
    (job/'preparation.json').write_text(json.dumps(report, indent=2)+'\n')
    ready = job/'ready'
    ready.mkdir(exist_ok=True)
    command = ['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--slice','0',
               '--arrange','0','--orient','0','--outputdir',str(ready),
               '--export-3mf',stem+'.gcode.3mf',str(staged)]
    (job/'slice-command.json').write_text(json.dumps(command, indent=2)+'\n')
    with (ready/'bambu-cli.log').open('w') as log:
        rc = subprocess.run(command,cwd=ready,stdout=log,stderr=subprocess.STDOUT).returncode
    print('SLICE_EXIT',rc,args.printer,flush=True)
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
