"""Slice the open-underneath display receiver for the existing face-up cover."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import face_up_trial as trial

ROOT,HERE=trial.ROOT,trial.HERE
sys.path.insert(0,str(ROOT/'hardware/printed-parts/faucet'))
import refresh_print_project as writer

JOB=ROOT/'.cache/prints/2026-09-30-display-body-x050-receiver-h2c-v4'
STEM='display-body-x050-receiver-z018-h2c-v4'
PROFILE=ROOT/'hardware/printed-parts/petgf.3mf'


def main():
    staged=JOB/(STEM+'-input.3mf')
    assert not staged.exists(),'Keep reviewed native slices immutable.'
    report=writer.refresh(PROFILE,staged,parts=((trial.RECEIVER,HERE/(trial.RECEIVER+'.stl'),0.),),
                          offsets=((0.,0.),),title='Display receiver with 0.50 mm body X clearance; H2C',
                          z_trim=.18,plate_border=15.)
    with zipfile.ZipFile(staged) as z:members={n:z.read(n) for n in z.namelist()}
    settings=json.loads(members[writer.SETTINGS_MEMBER])
    settings.update(extruder_ams_count=['1#0|4#0','1#0|4#0'],
                    support_filament='1',support_interface_filament='1',flush_into_support='0')
    members[writer.SETTINGS_MEMBER]=json.dumps(settings,indent=2).encode()
    writer.archive_write(staged,members)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    geometry=json.loads((HERE/'geometry-check.json').read_text())
    sources=[ROOT/p for p in geometry['source_sha256']]+[
        HERE/'geometry-check.json',HERE/'insertion-envelope.json',Path(__file__),PROFILE]
    assert sha(HERE/(trial.NAME+'.stl'))=='bd0545aa076fed3d7adc895df205b098f11a08b6fc37c883893115aec83dd5f2'
    report.update(printer='H2C',project_sha256=sha(staged),
                  source_geometry_and_settings_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources},
                  requested_z_trim_mm=.18,expected_textured_plate_trim_mm=.16,
                  existing_cover_sha256=sha(HERE/(trial.NAME+'.stl')),
                  support_policy='Shared PET-GF tree settings in the 30 degree enclosure pose. Wing pockets open down through the frame.',
                  clearance_basis=geometry['clearance_basis'],wing_tip_air_mm=trial.TIP_AIR,
                  face_perimeter_air_mm=geometry['face_perimeter_air_mm'],
                  wing_thickness_clearance_mm=trial.BEARING_AIR,
                  pure_axis_travel_mm=geometry['pure_axis_travel_mm'],submitted=False)
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
