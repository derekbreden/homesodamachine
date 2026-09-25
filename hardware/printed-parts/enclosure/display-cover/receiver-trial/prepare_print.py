"""Stage and natively slice the receiver coupon in front-top's print orientation."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware').parent
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'hardware/printed-parts/faucet'))
import refresh_print_project as writer

JOB = ROOT/'.cache/prints/2026-09-25-display-receiver-trial-mark2-v1-final'
STEM = 'display-receiver-trial-black-z004-mark2-v1'
PROFILE = ROOT/'hardware/printed-parts/petgf.3mf'
SOURCE = HERE/'display-receiver-trial-v1.stl'
STAGED = JOB/(STEM+'-input.3mf')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not STAGED.exists()
    assert sha(PROFILE) == '3864deceaa295d0fffded05e445b77ee926e2706d8765fdc8bbf81a23fe98697'
    report = writer.refresh(PROFILE, STAGED, parts=(('display-receiver-trial-v1', SOURCE, 0.),),
                            offsets=((0., 0.),), title='Machine display receiver trial; Mark2',
                            z_trim=.04, plate_border=15.)
    with zipfile.ZipFile(STAGED) as z:
        members = {n: z.read(n) for n in z.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    overrides = {'extruder_ams_count': ['1#0|4#0', '1#0|4#0'],
                 'support_remove_small_overhang': '0', 'support_top_z_distance': '0.24'}
    settings.update(overrides)
    assert settings['layer_height'] == '0.24' and settings['initial_layer_print_height'] == '0.2'
    assert settings['wall_loops'] == '2' and settings['wall_sequence'] == 'inner wall/outer wall'
    assert settings['is_infill_first'] == '0' and settings['infill_wall_overlap'] == '15%'
    assert settings['filament_nozzle_map'] == ['0'] and settings['filament_colour'] == ['#000000']
    members[writer.SETTINGS_MEMBER] = (json.dumps(settings, indent=2)+'\n').encode()
    writer.archive_write(STAGED, members)
    sources = [SOURCE, SOURCE.with_suffix('.step'), HERE/'display_receiver_trial.py',
               HERE/'geometry-check.json', Path(__file__).resolve(), PROFILE]
    report.update({'project_sha256': sha(STAGED),
                   'source_geometry_and_settings_sha256': {str(p.relative_to(ROOT)): sha(p) for p in sources},
                   'settings_sha256': hashlib.sha256(members[writer.SETTINGS_MEMBER]).hexdigest(),
                   'intentional_process_and_mapping_overrides': overrides,
                   'printer': 'Mark2', 'requested_z_trim_mm': .04,
                   'orientation': 'Source upright: display plane 30 degrees above bed, same as front-top.',
                   'support_policy': 'Supports carry the functional pocket seats and catches; all contacts release through the open underside.',
                   'layer_policy': '0.24 mm with 0.20 mm first layer. Square outer coupon frame; no cosmetic rounded show edges.'})
    (JOB/'preparation.json').write_text(json.dumps(report, indent=2)+'\n')
    ready = JOB/'ready'
    ready.mkdir(exist_ok=True)
    command = ['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio', '--slice', '0',
               '--arrange', '0', '--orient', '0', '--outputdir', str(ready), '--export-3mf',
               STEM+'.gcode.3mf', str(STAGED)]
    (JOB/'slice-command.json').write_text(json.dumps(command, indent=2)+'\n')
    with (ready/'bambu-cli.log').open('w') as log:
        rc = subprocess.run(command, cwd=ready, stdout=log, stderr=subprocess.STDOUT).returncode
    print('SLICE_EXIT', rc, flush=True)
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
