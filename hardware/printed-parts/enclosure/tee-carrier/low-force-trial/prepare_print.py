"""Prepare and natively slice the low-force carrier on Mark2."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'tools').is_dir())
NAME = 'tee-carrier-low-force'
ARCHIVED_GENERATOR = HERE / 'low_force_trial.py'
GENERATOR_REVISION = 'f90aba23c585bf2e73430e3157dff74474041aa3'
sys.path.insert(0,str(ROOT/'hardware/printed-parts/faucet'))
import refresh_print_project as writer
BASE=ROOT/'.cache/prints/2026-09-24-tee-carrier-plate-mark2-v15/tee-carrier-plate-black-z004-mark2-v15-six-wall-band-original-order-input.3mf'
PETGF=ROOT/'hardware/printed-parts/petgf.3mf'
JOB=ROOT/'.cache/prints/2026-09-30-tee-low-force050-mark2-v16'
STEM='tee-carrier-low-force050-filled-bottom-024-black-z004-mark2-v16'
PRINTER='Mark2'
Z_TRIM=.04


def source_bytes(path):
    """Read live inputs, or the exact Git source of the retired generator."""
    if path == ARCHIVED_GENERATOR and not path.is_file():
        return subprocess.check_output(
            ['git', 'show', f'{GENERATOR_REVISION}:{path.relative_to(ROOT)}'], cwd=ROOT)
    return path.read_bytes()


def main():
    JOB.mkdir(parents=True,exist_ok=True)
    target=JOB/(STEM+'-input.3mf')
    assert not target.exists(),'Keep sliced trials immutable.'
    source=HERE/(NAME+'.stl')
    report=writer.refresh(BASE,target,parts=((NAME,source,-90.),),offsets=((0.,0.),),
                          title=f'Tee carrier low-force roof clearance; {PRINTER}',z_trim=Z_TRIM,plate_border=15.)
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
    geometry=json.loads((HERE/'geometry-check.json').read_text())
    report.update(project_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                  source_geometry_and_settings_sha256={str(p.relative_to(ROOT)):hashlib.sha256(source_bytes(p)).hexdigest() for p in sources},
                  archived_generator_revision=(None if ARCHIVED_GENERATOR.is_file() else GENERATOR_REVISION),
                  printer=PRINTER,requested_z_trim_mm=Z_TRIM,expected_textured_plate_trim_mm=.02,
                  roof_relief_mm=geometry['roof_relief_mm'],
                  roof_clearance_mm=geometry['roof_clearance_mm'],
                  floor_clearance_mm=geometry['floor_clearance_mm'],
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
