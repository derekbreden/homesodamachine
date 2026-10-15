"""Prepare the unsent annulus-scoped Full-mode comparison; no printer control."""
from pathlib import Path
import importlib.util
import json
import math
import os
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import numpy as np
import trimesh
import cadquery as cq

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('foot_prepare',HERE/'prepare.py')
prep=importlib.util.module_from_spec(spec);spec.loader.exec_module(prep)
writer=prep.writer
ROOT=prep.ROOT
FOLDER=HERE/'full-annulus/mark2'
WORK=prep.WORK/'full-annulus'
STEM='2026-10-14-faucet-foot-full-annulus-fins-vs-tree-current15-bridge125-fan70-mark2'

def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')

def main():
    if (FOLDER/'launch.json').exists():raise ValueError('Preserve submitted experiments')
    FOLDER.mkdir(parents=True,exist_ok=True);WORK.mkdir(parents=True,exist_ok=True)
    parent=HERE/'stock-vs-tree/mark2'
    report=json.loads((parent/'preparation.json').read_text())
    source=ROOT/report['project']
    with ZipFile(source) as z:members={n:z.read(n) for n in z.namelist()}
    row=report['parts'][0]
    config=ET.fromstring(members['Metadata/model_settings.config'])
    model=ET.fromstring(members['3D/3dmodel.model'])
    rel=ET.fromstring(members['3D/_rels/3dmodel.model.rels'])
    settings=json.loads(members[writer.SETTINGS_MEMBER])
    changes={}
    for key in ['fan_min_speed','fan_max_speed','overhang_fan_speed']:
        old=settings[key];settings[key]=['70']*len(old)
        changes[key]=dict(source=old,candidate=settings[key])
    for key in ['bridge_speed','filament_bridge_speed']:
        old=settings[key];settings[key]=['15']*len(old)
        changes[key]=dict(source=old,candidate=settings[key])
    for prefix in ['', 'filament_']:
        for kind in ['1_4','2_4','3_4','4_4','totally']:
            key=f'{prefix}overhang_{kind}_speed';old=settings[key]
            settings[key]=[str(min(float(v),15)) if float(v)>0 else '15' for v in old]
            changes[key]=dict(source=old,candidate=settings[key])
    old=settings['bridge_flow'];settings['bridge_flow']='1.25'
    changes['bridge_flow']=dict(source=old,candidate='1.25')
    members[writer.SETTINGS_MEMBER]=(json.dumps(settings,indent=2)+'\n').encode()
    for obj in config.findall('object'):
        for value in obj.findall("metadata[@key='bridge_flow']"):value.set('value','1.25')
    engine=ROOT/'.cache/support-fins-faucet'
    assert subprocess.check_output(['git','-C',str(engine),'rev-parse','HEAD'],text=True).strip()==prep.ENGINE_COMMIT
    layout_dir=WORK/'engine'
    subprocess.run(['node',str(HERE/'build-fins.mjs'),str(engine),str(HERE/'foot-section.stl'),
        str(layout_dir),'1','true','full','annulus'],check=True)
    layout=json.loads((layout_dir/'engine.json').read_text())[1]
    assert layout['tines']==0
    mesh=trimesh.load(layout_dir/'B-plain-seated.stl',force='mesh',process=True)
    mesh.apply_translation(-np.array([layout['offset'][k] for k in 'xyz']))
    mesh.apply_transform(trimesh.transformations.rotation_matrix(math.radians(15),[1,0,0]))
    member='3D/Objects/custom-foot-fins-0.model'
    support_doc=ET.fromstring(members[member])
    vertices=support_doc.find('.//'+writer.qn('vertices'));vertices.clear()
    faces=support_doc.find('.//'+writer.qn('triangles'));faces.clear()
    for v in mesh.vertices-np.array(row['source_center_mm']):
        ET.SubElement(vertices,writer.qn('vertex'),**dict(zip('xyz',(f'{x:.9f}' for x in v))))
    for f in mesh.faces:
        ET.SubElement(faces,writer.qn('triangle'),**dict(zip(('v1','v2','v3'),map(str,f))),paint_supports='8')
    members[member]=writer.xml(support_doc)
    save(FOLDER/'layout-engine.json',dict(engine_commit=prep.ENGINE_COMMIT,engine_local_changes=False,**layout))
    transform=np.array(row['build_transform']);rot=transform[:9].reshape(3,3).T;tr=transform[9:]
    origin=tr-rot@np.array(row['source_center_mm'])
    rear=[]
    for i,x in enumerate([-6,0,6],1):
        a=origin+rot@np.array([x,23,0]);b=origin+rot@np.array([x,27.4,0])
        # The tool's 0.6 mm minimum squat-wall height omits the lowest rear band.
        # These simple, local walls follow that same underside at a vertical
        # 0.24 mm gap, with no broad bed pad and no added grip contacts.
        solid=(cq.Workplane('YZ').workplane(offset=a[0]-.5)
            .polyline([(a[1],0),(b[1],0),(b[1],b[2]-.24),(a[1],a[2]-.24)])
            .close().extrude(1).val())
        assert solid.isValid() and solid.Volume()>0
        output=WORK/f'rear-low-wall-{x}.stl';cq.exporters.export(solid,str(output))
        local=trimesh.load(output,force='mesh',process=True)
        local.vertices=(local.vertices-tr)@rot+np.array(row['source_center_mm'])
        pid=2100+i
        prep.component(members,model,config,rel,row,local,pid,f'rear-low-wall-{x}')
        rear.append(dict(component_id=pid,cad_x_mm=x,cad_y_interval_mm=[23,27.4],
            wall_width_mm=1,requested_vertical_gap_mm=.24,
            native_world_contact_endpoints_mm=[a.tolist(),b.tolist()],
            top_height_interval_mm=[float(b[2]-.24),float(a[2]-.24)],
            builder='Local CadQuery straight wall, not upstream Full-mode output.'))
    name='A Full annulus fins plus low rear walls'
    cfg=config.find(f"object[@id='{row['object_id']}']")
    cfg.find("metadata[@key='name']").set('value',name)
    for plate in config.findall('plate'):
        value=plate.find("metadata[@key='plater_name']")
        if value is not None:value.set('value','Full-mode annulus fins versus Tree(auto), bridge recipe')
    members['Metadata/model_settings.config']=writer.xml(config)
    members['3D/3dmodel.model']=writer.xml(model)
    members['3D/_rels/3dmodel.model.rels']=writer.xml(rel).replace(b'ns0:',b'').replace(b'xmlns:ns0=',b'xmlns=')
    project=FOLDER/f'{STEM}.3mf';writer.archive_write(project,members)
    report.update(project=str(project.relative_to(ROOT)),project_sha256=writer.digest(project.read_bytes()),
        parent_project=str(source.relative_to(ROOT)),parent_project_sha256=writer.digest(source.read_bytes()),
        candidate_status='Prepared only; not sent to a printer.',recipe_changes=changes,
        rear_low_walls=rear,
        material_treatment='Both specimens: native bridge_flow1.25;70% part fan after3bedlayers, including floating vertical shells and supports; bridges15mm/s; overhang limits capped15mm/s while preserving the existing10mm/s fully unsupported-wall limit. No G-code edits.',
        support_scope=f'A uses{layout["fin_count"]} unmodified-engine walls in Full mode, coverage1.0/downhill:true, plus three local low rear walls. Caller selects only the CAD Z0 downward annulus for engine placement; the complete part remains available for collision and seating checks. Tree(auto)/Default elsewhere. B retains production Tree(auto)/Default everywhere.',
        support_reason='Whole-annulus native-path review and the user-priority lever-facing midpoint require closer deposition bearings than the stock eight-wall layout supplies. Full-mode fill serves short annulus regions. Three simple low rear walls address the native Z0.92/1.40 first-skin gaps below the tool minimum wall height. The accepted -15 degree pose remains.')
    report['parts'][0]['name']=name;report['specimens'][0]['walls']=layout['fin_count']+len(rear)
    for obj in report['specimens']:obj['bridge_flow']=1.25
    save(FOLDER/'preparation.json',report);save(project.with_suffix('.print.json'),report)
    native=WORK/'native';native.mkdir(exist_ok=True)
    cmd=['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--slice','0','--arrange','0','--orient','0',
        '--outputdir',str(native),'--export-3mf','native.gcode.3mf',str(project)]
    save(FOLDER/'slice-command.json',dict(argv=cmd))
    with (native/'slice.log').open('w') as log:
        subprocess.run(cmd,cwd=native,stdout=log,stderr=subprocess.STDOUT,check=True,
            env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1'))
    sliced=json.loads((native/'result.json').read_text());assert sliced.get('return_code')==0,sliced
    (FOLDER/f'{STEM}.gcode.3mf').write_bytes((native/'native.gcode.3mf').read_bytes())
    save(FOLDER/'slice-result.json',sliced);print(json.dumps(sliced['sliced_plates']),flush=True)

if __name__=='__main__':main()
