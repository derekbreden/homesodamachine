"""Transfer the reviewed comparison to Mark1's saved start code and spool colour."""
from pathlib import Path
import importlib.util
import json
import os
import subprocess
from zipfile import ZipFile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('foot_prepare',HERE/'prepare.py')
prep=importlib.util.module_from_spec(spec);spec.loader.exec_module(prep)
ROOT=prep.ROOT;writer=prep.writer
FOLDER=HERE/'full-annulus/mark1'
STEM='2026-10-14-faucet-foot-full-annulus-fins-vs-tree-current15-bridge125-fan70-z018-mark1'

def save(path,data):path.write_text(json.dumps(data,indent=2)+'\n')

def main():
    if (FOLDER/'launch.json').exists():raise ValueError('Preserve submitted experiments')
    FOLDER.mkdir(parents=True,exist_ok=True)
    parent=HERE/'full-annulus/mark2'
    report=json.loads((parent/'preparation.json').read_text());source=ROOT/report['project']
    accepted=HERE.parent/'2026-10-14-bridge-transfer/mark1'
    profile=next(accepted.glob('*-mark1.3mf'))
    with ZipFile(source) as z:members={n:z.read(n) for n in z.namelist()}
    with ZipFile(profile) as z:mark1=json.loads(z.read(writer.SETTINGS_MEMBER))
    settings=json.loads(members[writer.SETTINGS_MEMBER]);changes={}
    for key in ['machine_start_gcode','printer_settings_id','filament_colour']:
        before=settings[key];settings[key]=mark1[key]
        changes[key]=dict(source_sha256=writer.digest(json.dumps(before).encode()),
            transferred_sha256=writer.digest(json.dumps(settings[key]).encode()))
    assert settings['filament_colour']==['#000000']
    assert '+0.18 Z trim' in settings['printer_settings_id']
    members[writer.SETTINGS_MEMBER]=(json.dumps(settings,indent=2)+'\n').encode()
    project=FOLDER/f'{STEM}.3mf';writer.archive_write(project,members)
    report.update(project=str(project.relative_to(ROOT)),project_sha256=writer.digest(project.read_bytes()),
        parent_project=str(source.relative_to(ROOT)),parent_project_sha256=writer.digest(source.read_bytes()),
        printer=settings['printer_settings_id'],printer_display_name='Mark1',connection_key='H2C',
        requested_z_trim_mm=.18,candidate_status='Prepared for the user-cleared Mark1 bed; launch.json records acceptance.',
        printer_profile_transfer=dict(source=str(profile.relative_to(ROOT)),
            source_sha256=writer.digest(profile.read_bytes()),settings=changes),
        authorization_quote='Mark1 bed is clear')
    save(FOLDER/'preparation.json',report);save(project.with_suffix('.print.json'),report)
    (FOLDER/'layout-engine.json').write_bytes((parent/'layout-engine.json').read_bytes())
    work=prep.WORK/'full-annulus-mark1/native';work.mkdir(parents=True,exist_ok=True)
    cmd=['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--slice','0','--arrange','0','--orient','0',
        '--outputdir',str(work),'--export-3mf','native.gcode.3mf',str(project)]
    save(FOLDER/'slice-command.json',dict(argv=cmd))
    with (work/'slice.log').open('w') as log:
        subprocess.run(cmd,cwd=work,stdout=log,stderr=subprocess.STDOUT,check=True,
            env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1'))
    result=json.loads((work/'result.json').read_text());assert result.get('return_code')==0,result
    (FOLDER/f'{STEM}.gcode.3mf').write_bytes((work/'native.gcode.3mf').read_bytes())
    save(FOLDER/'slice-result.json',result);print(json.dumps(result['sliced_plates']),flush=True)

if __name__=='__main__':main()
