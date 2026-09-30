"""Prepare and natively slice the low-force carrier on H2C."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
import low_force_trial as trial

ROOT,HERE = trial.ROOT,trial.HERE
sys.path.insert(0,str(ROOT/'hardware/printed-parts/faucet'))
import refresh_print_project as writer
BASE=ROOT/'.cache/prints/2026-09-24-tee-carrier-plate-mark2-v15/tee-carrier-plate-black-z004-mark2-v15-six-wall-band-original-order-input.3mf'
PETGF=ROOT/'hardware/printed-parts/petgf.3mf'
JOB=ROOT/'.cache/prints/2026-09-29-tee-low-force050-h2c-v7'
STEM='tee-carrier-low-force050-filled-bottom-024-black-z018-h2c-v7'


def main():
    JOB.mkdir(parents=True,exist_ok=True)
    target=JOB/(STEM+'-input.3mf')
    assert not target.exists(),'Keep sliced trials immutable.'
    source=HERE/(trial.NAME+'.stl')
    report=writer.refresh(BASE,target,parts=((trial.NAME,source,-90.),),offsets=((0.,0.),),
                          title='Tee carrier low-force roof clearance; H2C',z_trim=.18,plate_border=15.)
    with zipfile.ZipFile(BASE) as z:
        ranges=ET.fromstring(z.read('Metadata/layer_config_ranges.xml'))
    lower=ranges.find('./object/range')
    # Native Bambu range parsing requires an explicit layer height even when
    # the range's only intended override is its wall count.
    lower.find("option[@opt_key='layer_height']").text='0.24'
    # The preceding coarse layer must finish before the fore R6 starts at 15.054.
    ranges.findall('./object/range')[1].set('min_z','14.8000')
    with zipfile.ZipFile(PETGF) as z:
        normal_height=json.loads(z.read('Metadata/project_settings.config'))['layer_height']
    assert normal_height=='0.24'
    with zipfile.ZipFile(target) as z:members={n:z.read(n) for n in z.namelist()}
    members['Metadata/layer_config_ranges.xml']=ET.tostring(ranges,encoding='utf-8',xml_declaration=True)
    settings=json.loads(members['Metadata/project_settings.config'])
    settings.update(layer_height=normal_height,initial_layer_print_height='0.2',brim_type='no_brim',
                    brim_width='0',brim_object_gap='0',elefant_foot_compensation='0')
    members['Metadata/project_settings.config']=json.dumps(settings,indent=2).encode()
    writer.archive_write(target,members)
    sources=[source,source.with_suffix('.step'),HERE/'low_force_trial.py',HERE/'geometry-check.json',Path(__file__),BASE,PETGF]
    _, carrier = trial.specifications()
    report.update(project_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                  source_geometry_and_settings_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                  printer='H2C',requested_z_trim_mm=.18,expected_textured_plate_trim_mm=.16,
                  roof_relief_mm=trial.ROOF_RELIEF,
                  roof_clearance_mm=carrier.roof_z-carrier.column_z[1],
                  floor_clearance_mm=carrier.column_z[0]-carrier.floor_z,
                  initial_layer_height_mm=.20,
                  support_policy='No supports or brim. Bed layer 0.20 mm; filled bottom chamfer/taper and body use normal PET-GF 0.24 mm layers; top R6 uses 0.08 mm. Six walls in print Z 0–6.1 mm only.',
                  bottom_geometry=json.loads((HERE/'geometry-check.json').read_text())['bottom_chamfer'],
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
