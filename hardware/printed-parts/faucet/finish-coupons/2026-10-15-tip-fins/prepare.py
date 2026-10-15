"""Prepare one tip fin candidate manually; no printer commands or control repeat."""
from pathlib import Path
import importlib.util
import json
import math
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'tools/bambu_print.py').exists())
FAUCET = HERE.parents[1]
sys.path[:0] = [str(FAUCET), str(FAUCET/'industrial'), str(FAUCET/'faucet-shell')]
import refresh_print_project as writer
import prepare_print_project as industrial
import faucet_shell as shell

loader = importlib.util.spec_from_file_location('fin_component', HERE.parent/'2026-10-14-foot-fins-current-angle/prepare.py')
component = importlib.util.module_from_spec(loader)
loader.loader.exec_module(component)
WORK = ROOT/'.cache/printer-control/faucet-tip-fins-20261015'
ENGINE = ROOT/'.cache/support-fins-faucet'
PIN = '511d81fc9124075cef142bfb2766bd5e8bfa777d'
FOLDER = HERE/'mark2'
STEM = '2026-10-15-faucet-tip-eight-fins-current105-bridge125-fan70-z004-mark2'
SOURCE = FAUCET/'industrial/faucet-industrial-petgf.3mf'
PART = HERE.parent/'2026-10-14-bridge-transfer/tip-section.stl'


def save(p, data):
    p.write_text(json.dumps(data, indent=2)+'\n')


def main():
    if (FOLDER/'launch.json').exists():
        raise ValueError('Preserve the submitted experiment')
    FOLDER.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    assert subprocess.check_output(['git','-C',str(ENGINE),'rev-parse','HEAD'],text=True).strip()==PIN
    assert not subprocess.check_output(['git','-C',str(ENGINE),'status','--porcelain'],text=True).strip()
    origin = json.loads((HERE.parent/'2026-10-14-bridge-transfer/mark1/preparation.json').read_text())
    assert writer.digest(PART.read_bytes())==origin['parts'][0]['stl_sha256']
    assert writer.digest((ROOT/origin['source_geometry']['source']).read_bytes())==origin['source_geometry']['source_sha256']
    mesh = trimesh.load(PART, force='mesh', process=True)
    point = np.array([0, shell.split_junction_y, shell.split_junction_z])
    normal = np.array(shell.split_normal)
    mask = (np.max(abs((mesh.triangles-point)@normal),axis=1)<.02)&(mesh.face_normals@(-normal)>.999)
    scope = dict(point=point.tolist(), normal=normal.tolist(), angle=-105,
                 face_tolerance_mm=.02, area_mm2=float(mesh.area_faces[mask].sum()))
    save(HERE/'contact-scope.json',scope)
    subprocess.run(['node',str(HERE/'build-fins.mjs'),str(ENGINE),str(PART),
                    str(HERE/'contact-scope.json'),str(WORK/'engine')],check=True)
    layout = json.loads((WORK/'engine/full100.json').read_text())
    assert layout['fin_count']==8 and layout['tines']==0
    save(FOLDER/'layout-engine.json',dict(engine_commit=PIN,engine_local_changes=False,**layout))
    project = FOLDER/f'{STEM}.3mf'
    report = writer.refresh(SOURCE,project,
        parts=(('Tip joint with eight plain fin walls',PART,-105),), offsets=((0,0),),
        title='Faucet tip joint: eight plain fin walls, bridge recipe',z_trim=.04,plate_border=80)
    with ZipFile(project) as z, ZipFile(SOURCE) as source:
        members={n:z.read(n) for n in z.namelist()}
        parent=ET.fromstring(source.read('Metadata/model_settings.config'))
        tip=next(o for o in parent.findall('object') if o.find("metadata[@key='name']").get('value')=='faucet-shell-tip')
    settings=json.loads(members[writer.SETTINGS_MEMBER])
    changes={}
    for key in ['fan_min_speed','fan_max_speed','overhang_fan_speed']:
        old=settings[key]; settings[key]=['70']*len(old)
        changes[key]=dict(source=old,candidate=settings[key])
    for key in ['bridge_speed','filament_bridge_speed']:
        old=settings[key]; settings[key]=['15']*len(old)
        changes[key]=dict(source=old,candidate=settings[key])
    for prefix in ['', 'filament_']:
        for kind in ['1_4','2_4','3_4','4_4','totally']:
            key=f'{prefix}overhang_{kind}_speed';old=settings[key]
            settings[key]=[str(min(float(v),15)) if float(v)>0 else '15' for v in old]
            changes[key]=dict(source=old,candidate=settings[key])
    settings['bridge_flow']='1.25'
    settings['filament_colour']=['#161616']
    members[writer.SETTINGS_MEMBER]=(json.dumps(settings,indent=2)+'\n').encode()
    config=ET.fromstring(members['Metadata/model_settings.config'])
    model=ET.fromstring(members['3D/3dmodel.model'])
    rel=ET.fromstring(members['3D/_rels/3dmodel.model.rels'])
    row=report['parts'][0]
    cfg=config.find(f"object[@id='{row['object_id']}']")
    for m in tip.findall('metadata'):
        if m.get('key') and m.get('key') not in ('name','extruder'):
            writer.metadata(cfg,m.get('key'),m.get('value'))
    writer.metadata(cfg,'bridge_flow','1.25')
    child=ET.fromstring(members[row['member']])
    triangles=child.find('.//'+writer.qn('triangles'))
    assert len(triangles)==len(mask)
    for tri,block in zip(triangles,mask):
        if block:tri.set('paint_supports','8')
    members[row['member']]=writer.xml(child)
    support=trimesh.load(WORK/'engine/full100-seated.stl',force='mesh',process=True)
    support.apply_translation(-np.array([layout['offset'][k] for k in 'xyz']))
    support.apply_transform(trimesh.transformations.rotation_matrix(math.radians(105),[1,0,0]))
    component.component(members,model,config,rel,row,support,2000,'tip-joint-fin-walls')
    members['Metadata/model_settings.config']=writer.xml(config)
    members['3D/3dmodel.model']=writer.xml(model)
    members['3D/_rels/3dmodel.model.rels']=writer.xml(rel).replace(b'ns0:',b'').replace(b'xmlns:ns0=',b'xmlns=')
    paint=industrial.enforce_rear_seam(members,report,dict(part=row['name'],half_width_mm=0,surface='curved_outer_arc'))
    writer.archive_write(project,members)
    report.update(project=str(project.relative_to(ROOT)),project_sha256=writer.digest(project.read_bytes()),
        settings_sha256=writer.digest(members[writer.SETTINGS_MEMBER]),settings_preserved_byte_for_byte=False,
        printer='Mark2',source_geometry=origin['source_geometry'],recipe_changes=changes,
        rear_seam_paint=paint,fin_count=8,tines=0,requested_vertical_fin_gap_mm=.24,
        blocked_contact_faces=int(mask.sum()),blocked_contact_area_mm2=float(mesh.area_faces[mask].sum()),
        support_scope='Eight plain Full-mode engine walls selected for the downward joint ledge. The full tip topology controls first-hit wall tops, including the plug where it lies below that ledge. Only the joint plane and added fin surfaces receive support-block paint; Tree(auto)/Default remains elsewhere.',
        support_reason='Defect 2 continues around the tip mating lip. The narrow 35-degree joint ledge receives no walls from Auto; Full mode supplies eight walls, including a near-midpoint low-lip contact. Direct base evidence supports plain-wall release; tip contact and release remain a physical transfer question.',
        material_treatment='Native bridge_flow1.25,70% fan after3off bedlayers including floating vertical shell/supports,Bridge15mm/s,overhang limits at most15 with existing10 limit retained. No post-slice G-code edits.',
        candidate_status='Prepared; no printer job accepted.',
        specimen_count=1,repeat_control=False,
        authorization_quotes=["I'd rather you start iterating on the faucet tip, which also needs fins.",
          'As far as the next print on mark2','which is open and ready for your next print',
          "And I don't want you to keep wasting my time printing the same control over and over again. Please just print what you think will work best, no repeat control."])
    save(FOLDER/'preparation.json',report)
    save(project.with_suffix('.print.json'),report)
    native=WORK/'native';native.mkdir(exist_ok=True)
    cmd=['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--slice','0','--arrange','0','--orient','0',
         '--outputdir',str(native),'--export-3mf','native.gcode.3mf',str(project)]
    save(FOLDER/'slice-command.json',dict(argv=cmd))
    with (native/'slice.log').open('w') as log:
        subprocess.run(cmd,cwd=native,stdout=log,stderr=subprocess.STDOUT,check=True,
                       env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1'))
    result=json.loads((native/'result.json').read_text())
    assert result.get('return_code')==0,result
    (FOLDER/f'{STEM}.gcode.3mf').write_bytes((native/'native.gcode.3mf').read_bytes())
    save(FOLDER/'slice-result.json',result)
    print(json.dumps(result['sliced_plates']),flush=True)


if __name__=='__main__':main()
