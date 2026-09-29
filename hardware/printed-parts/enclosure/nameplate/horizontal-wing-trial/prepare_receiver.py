"""Slice the matching receiver in its installed enclosure wall orientation."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools').is_dir())
sys.path.insert(0,str(ROOT/'hardware/printed-parts/faucet'))
import refresh_print_project as writer

JOB=ROOT/'.cache/prints/2026-09-29-nameplate-flat-wing-receiver-h2c-v1'
STEM='nameplate-flat-wing-receiver-z018-h2c-v1'
NAME='nameplate-horizontal-wings-receiver'
PROFILE=ROOT/'hardware/printed-parts/petgf.3mf'

def main():
    staged=JOB/(STEM+'-input.3mf')
    assert not staged.exists(),'Keep reviewed jobs immutable.'
    source=HERE/(NAME+'.stl')
    report=writer.refresh(PROFILE,staged,parts=((NAME,source,180.),),
                          offsets=((0.,0.),),title='Horizontal-wing nameplate receiver; H2C',
                          z_trim=.18,plate_border=15.)
    with zipfile.ZipFile(staged) as z:members={n:z.read(n) for n in z.namelist()}
    settings=json.loads(members[writer.SETTINGS_MEMBER])
    overrides={'extruder_ams_count':['1#0|4#0','1#0|4#0'],
               'enable_support':'1','support_type':'normal(auto)','support_style':'snug',
               'support_remove_small_overhang':'0','support_object_xy_distance':'0.8',
               'support_top_z_distance':'0.45','support_bottom_z_distance':'0.45',
               'support_object_first_layer_gap':'0.5','support_filament':'1',
               'support_interface_filament':'1','flush_into_support':'0'}
    settings.update(overrides)
    assert settings['layer_height']=='0.24' and settings['initial_layer_print_height']=='0.2'
    assert settings['filament_nozzle_map']==['0'] and settings['filament_colour']==['#000000']
    members[writer.SETTINGS_MEMBER]=json.dumps(settings,indent=2).encode()
    writer.archive_write(staged,members)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    sources=[source,source.with_suffix('.step'),HERE/'geometry-check.json',HERE/'wing_interface.py',Path(__file__),PROFILE]
    report.update(project_sha256=sha(staged),printer='H2C',
                  source_geometry_and_settings_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources},
                  intentional_overrides=overrides,requested_z_trim_mm=.18,expected_textured_plate_trim_mm=.16,
                  orientation='CAD -Z up, matching front-top wall orientation; slots open to the face.',
                  support_policy='Black normal Snug supports, 0.8 mm nominal XY and 0.45 mm Z gaps. Verify emitted slot access.',
                  qualification='Insertion flex, retention and removal remain physical tests.')
    (JOB/'preparation.json').write_text(json.dumps(report,indent=2)+'\n')
    ready=JOB/'ready';ready.mkdir()
    command=['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--slice','0','--arrange','0','--orient','0',
             '--outputdir',str(ready),'--export-3mf',STEM+'.gcode.3mf',str(staged)]
    (JOB/'slice-command.json').write_text(json.dumps(command,indent=2)+'\n')
    with (ready/'bambu-cli.log').open('w') as log:
        rc=subprocess.run(command,cwd=ready,stdout=log,stderr=subprocess.STDOUT).returncode
    print('SLICE_EXIT',rc,flush=True)
    return rc

if __name__=='__main__':raise SystemExit(main())
