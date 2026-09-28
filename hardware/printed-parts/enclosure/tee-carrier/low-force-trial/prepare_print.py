"""Prepare and natively slice the low-force carrier on H2C."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile
import low_force_trial as trial

ROOT,HERE = trial.ROOT,trial.HERE
sys.path.insert(0,str(ROOT/'hardware/printed-parts/faucet'))
import refresh_print_project as writer
BASE=ROOT/'.cache/prints/2026-09-24-tee-carrier-plate-mark2-v15/tee-carrier-plate-black-z004-mark2-v15-six-wall-band-original-order-input.3mf'
JOB=ROOT/'.cache/prints/2026-09-28-tee-low-force-h2c-v1'
STEM='tee-carrier-low-force-black-z018-h2c-v1'


def main():
    JOB.mkdir(parents=True,exist_ok=True)
    target=JOB/(STEM+'-input.3mf')
    assert not target.exists(),'Keep sliced trials immutable.'
    source=HERE/(trial.NAME+'.stl')
    report=writer.refresh(BASE,target,parts=((trial.NAME,source,-90.),),offsets=((0.,0.),),
                          title='Tee carrier low-force roof clearance; H2C',z_trim=.18,plate_border=15.)
    with zipfile.ZipFile(BASE) as z:
        ranges=z.read('Metadata/layer_config_ranges.xml')
    with zipfile.ZipFile(target) as z:members={n:z.read(n) for n in z.namelist()}
    members['Metadata/layer_config_ranges.xml']=ranges
    writer.archive_write(target,members)
    sources=[source,source.with_suffix('.step'),HERE/'low_force_trial.py',HERE/'geometry-check.json',Path(__file__),BASE]
    report.update(project_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                  source_geometry_and_settings_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                  printer='H2C',requested_z_trim_mm=.18,expected_textured_plate_trim_mm=.16,
                  roof_relief_mm=.75,roof_clearance_mm=1.25,floor_clearance_mm=.25,
                  support_policy='No supports. Complete visible R6 rounds use 0.08 mm; six walls in print Z 0–6.1 mm only.',
                  speeds_and_order='Saved speeds, inner/outer then infill, 15% overlap.')
    (JOB/'preparation.json').write_text(json.dumps(report,indent=2)+'\n')
    ready=JOB/'ready';ready.mkdir()
    command=['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--slice','0','--arrange','0','--orient','0',
             '--outputdir',str(ready),'--export-3mf',STEM+'.gcode.3mf',str(target)]
    (JOB/'slice-command.json').write_text(json.dumps(command,indent=2)+'\n')
    with (ready/'bambu-cli.log').open('w') as log:
        rc=subprocess.run(command,cwd=ready,stdout=log,stderr=subprocess.STDOUT).returncode
    print('SLICE_EXIT',rc,flush=True)
    return rc


if __name__=='__main__':raise SystemExit(main())
