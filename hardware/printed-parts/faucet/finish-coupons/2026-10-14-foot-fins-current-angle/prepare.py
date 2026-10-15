"""Manual current-angle foot experiment; does not contact either printer."""
from pathlib import Path
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import cadquery as cq
import numpy as np
import trimesh

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/bambu_print.py').exists())
FAUCET=HERE.parents[1]
sys.path[:0]=[str(FAUCET),str(FAUCET/'industrial')]
import refresh_print_project as writer
import prepare_print_project as industrial

ENGINE_COMMIT='511d81fc9124075cef142bfb2766bd5e8bfa777d'
WORK=ROOT/'.cache/printer-control/faucet-foot-fins-20261014'
SOURCE=FAUCET/'industrial/faucet-industrial-petgf.3mf'
STEM='2026-10-14-faucet-foot-fins-current15-petgf-left04-z004-mark2'

def save(path,data): path.write_text(json.dumps(data,indent=2)+'\n')

def geometry():
    source=FAUCET/'industrial/industrial-shell-base'
    approval=json.loads((FAUCET/'industrial/prints/2026-10-13-complete-rear-seam-base-tip-mark2/physical-result.json').read_text())
    sha=writer.digest(source.with_suffix('.stl').read_bytes())
    assert sha==approval['source_geometry_hashes'][str(source.with_suffix('.stl').relative_to(ROOT))]
    m=trimesh.load(source.with_suffix('.stl'),force='mesh')
    r=trimesh.transformations.rotation_matrix(math.radians(-15),[1,0,0])
    lift=-float(trimesh.transform_points(m.vertices,r)[:,2].min())
    shape=cq.importers.importStep(str(source.with_suffix('.step'))).val()
    shape=shape.rotate((0,0,0),(1,0,0),-15).translate((0,0,lift))
    shape=shape.intersect(cq.Solid.makeBox(400,500,16.761,cq.Vector(-200,-200,-.001)),tol=1e-6)
    assert shape.isValid() and len(shape.Solids())==1
    shape=shape.translate((0,0,-lift)).rotate((0,0,0),(1,0,0),15)
    out=HERE/'foot-section.stl'
    cq.exporters.export(shape,str(out),tolerance=.012,angularTolerance=.07)
    save(HERE/'geometry.json',dict(rotation_x_degrees=-15,lift_mm=lift,crop_print_z_mm=16.76,
        source_stl_sha256=sha,source_step_sha256=writer.digest(source.with_suffix('.step').read_bytes()),
        tessellation_tolerance_mm=.012))
    return out

def engines(part):
    upstream=ROOT/'.cache/support-fins-faucet'
    actual=subprocess.check_output(['git','-C',str(upstream),'rev-parse','HEAD'],text=True).strip()
    assert actual==ENGINE_COMMIT
    local=ROOT/'.cache/support-fins-faucet-15deg'
    # A separate local copy records the only experimental source change.
    if local.exists(): shutil.rmtree(local)
    shutil.copytree(upstream,local,ignore=shutil.ignore_patterns('.git'))
    target=local/'web/prop/tines.js'
    before=target.read_text()
    old='if (hm < 0.34) continue;'
    new='if (hm < 0.25) continue;'
    assert before.count(old)==1
    target.write_text(before.replace(old,new))
    for engine,folder in [(upstream,WORK/'stock'),(local,WORK/'gate025')]:
        subprocess.run(['node',str(HERE/'build-fins.mjs'),str(engine),str(part),str(folder)],check=True)
    records=json.loads((WORK/'gate025/engine.json').read_text())
    assert records[0]['tines']==len(records[0]['retained_tines'])==26
    assert records[1]['tines']==0
    save(HERE/'engine.json',dict(repository='https://github.com/gittrahan/support-fins',commit=ENGINE_COMMIT,
        local_change=dict(file='web/prop/tines.js',original=old,experimental=new,
            reason='The stock inward-normal cutoff excludes the retained 15 degree underside; reach and inside-part tests remain intact.'),
        stock=[{k:r[k] for k in ('name','tines','fin_count','seating')} for r in json.loads((WORK/'stock/engine.json').read_text())],
        candidates=records))
    return records

def component(members,model,config,relationships,row,mesh,pid,name,subtype='normal_part'):
    member=f'3D/Objects/{name}.model'
    sub=ET.Element(writer.qn('model'),unit='millimeter')
    resources=ET.SubElement(sub,writer.qn('resources'))
    obj=ET.SubElement(resources,writer.qn('object'),id=str(pid),type='model')
    geo=ET.SubElement(obj,writer.qn('mesh'))
    vs=ET.SubElement(geo,writer.qn('vertices'))
    ts=ET.SubElement(geo,writer.qn('triangles'))
    for v in mesh.vertices-np.array(row['source_center_mm']):
        ET.SubElement(vs,writer.qn('vertex'),**dict(zip('xyz',(f'{x:.9f}' for x in v))))
    for f in mesh.faces:
        ET.SubElement(ts,writer.qn('triangle'),**dict(zip(('v1','v2','v3'),map(str,f))),paint_supports='8')
    members[member]=writer.xml(sub)
    owner=model.find(f"{writer.qn('resources')}/{writer.qn('object')}[@id='{row['object_id']}']")
    ET.SubElement(owner.find(writer.qn('components')),writer.qn('component'),objectid=str(pid),
        transform='1 0 0 0 1 0 0 0 1 0 0 0',**{f'{{{writer.PROD}}}path':'/'+member,
        f'{{{writer.PROD}}}UUID':writer.identifier(name+'/component')})
    cfg=config.find(f"object[@id='{row['object_id']}']")
    part=ET.SubElement(cfg,'part',id=str(pid),subtype=subtype,uuid=writer.identifier(name+'/part'))
    for k,v in dict(name=name,matrix='1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1',extruder='1',wall_loops='2').items():
        writer.metadata(part,k,v)
    ET.SubElement(relationships,f'{{{writer.REL}}}Relationship',Target='/'+member,Id=name,
        Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')

def main():
    stock=len(sys.argv)==1 or sys.argv[1]=='stock'
    if not stock and sys.argv[1]!='grip': raise ValueError('Choose stock or grip')
    folder=HERE/'stock-vs-tree/mark2' if stock else HERE/'mark2'
    if (folder/'launch.json').exists(): raise ValueError('Preserve the submitted experiment')
    WORK.mkdir(parents=True,exist_ok=True)
    part=geometry()
    if stock:
        upstream=ROOT/'.cache/support-fins-faucet'
        assert subprocess.check_output(['git','-C',str(upstream),'rev-parse','HEAD'],text=True).strip()==ENGINE_COMMIT
        subprocess.run(['node',str(HERE/'build-fins.mjs'),str(upstream),str(part),str(WORK/'stock')],check=True)
        records=json.loads((WORK/'stock/engine.json').read_text())
        save(HERE/'stock-engine.json',dict(repository='https://github.com/gittrahan/support-fins',
            commit=ENGINE_COMMIT,local_changes=False,candidates=records))
    else:
        records=engines(part)
    folder.mkdir(parents=True,exist_ok=True)
    stem=STEM.replace('fins-current15','stock-fins-vs-tree-current15') if stock else STEM
    project=folder/f'{stem}.3mf'
    definitions=(('A stock fin walls',part,-15),('B production auto supports',part,-15)) if stock else (('A 26 tines',part,-15),('B plain walls',part,-15))
    report=writer.refresh(SOURCE,project,parts=definitions,
        offsets=((-39,0),(39,0)),title='Current-angle faucet foot: stock fins versus Tree(auto)' if stock else 'Current-angle faucet foot: A tines, B plain walls',z_trim=.04,plate_border=80)
    with ZipFile(project) as z,ZipFile(SOURCE) as source:
        members={n:z.read(n) for n in z.namelist()}
        parent=ET.fromstring(source.read('Metadata/model_settings.config'))
        base=next(o for o in parent.findall('object') if o.find("metadata[@key='name']").get('value')=='industrial-shell-base')
    settings=json.loads(members[writer.SETTINGS_MEMBER])
    settings['filament_colour']=['#161616']
    members[writer.SETTINGS_MEMBER]=(json.dumps(settings,indent=2)+'\n').encode()
    config=ET.fromstring(members['Metadata/model_settings.config'])
    model=ET.fromstring(members['3D/3dmodel.model'])
    rel=ET.fromstring(members['3D/_rels/3dmodel.model.rels'])
    helper_spec=importlib.util.spec_from_file_location('foot_helpers',HERE.parent/'coarse-start-v1/prepare.py')
    helper=importlib.util.module_from_spec(helper_spec);helper_spec.loader.exec_module(helper)
    paint=[]
    specimens=[]
    for i,row in enumerate(report['parts']):
        cfg=config.find(f"object[@id='{row['object_id']}']")
        for m in base.findall('metadata'):
            if m.get('key') and m.get('key') not in ('name','extruder'):
                writer.metadata(cfg,m.get('key'),m.get('value'))
        # Both conditions keep native production extrusion/cooling/feed.
        writer.metadata(cfg,'bridge_flow','1')
        region=trimesh.creation.box(extents=[61,61,14.02]);region.apply_translation([0,0,7])
        helper.add_foot_modifier(members,model,config,rel,row,region,i)
        # Only the retained annular bottom plane is served by the custom fins.
        mesh=trimesh.load(part,force='mesh',process=True)
        mask=(mesh.face_normals[:,2]<-.999)&(np.abs(mesh.triangles_center[:,2])<.015)
        child=ET.fromstring(members[row['member']])
        tris=child.find(f".//{writer.qn('triangles')}")
        assert len(tris)==len(mask)
        for tri,block in zip(tris,mask):
            if block and (not stock or i==0): tri.set('paint_supports','8')
        members[row['member']]=writer.xml(child)
        rec=records[1] if stock else records[i]
        if not stock or i==0:
            support=trimesh.load(WORK/('stock' if stock else 'gate025')/f"{rec['name']}-seated.stl",force='mesh',process=True)
            support.apply_translation(-np.array([rec['offset'][k] for k in 'xyz']))
            support.apply_transform(trimesh.transformations.rotation_matrix(math.radians(15),[1,0,0]))
            component(members,model,config,rel,row,support,2000+i,f'custom-foot-fins-{i}')
        present=not stock or i==0
        specimens.append(dict(id='AB'[i],identify_id=row['identify_id'],tines=rec['tines'] if present else 0,
            walls=rec['fin_count'] if present else 0,blocked_model_faces=int(mask.sum()) if present else 0,
            blocked_model_area_mm2=float(mesh.area_faces[mask].sum()) if present else 0,
            supports_component_id=2000+i if present else None,bridge_flow=1))
    members['Metadata/model_settings.config']=writer.xml(config)
    members['3D/3dmodel.model']=writer.xml(model)
    members['3D/_rels/3dmodel.model.rels']=writer.xml(rel).replace(b'ns0:',b'').replace(b'xmlns:ns0=',b'xmlns=')
    for row in report['parts']:
        paint.append(industrial.enforce_rear_seam(members,report,dict(part=row['name'],half_width_mm=.25)))
    writer.archive_write(project,members)
    report.update(project=str(project.relative_to(ROOT)),project_sha256=writer.digest(project.read_bytes()),
        specimens=specimens,rear_seam_paint=paint,crop_print_z_mm=16.76,
        support_scope='A: eight stock fin walls under the bottom annulus, with support-block paint on that plane and added fin surfaces only; Tree(auto)/Default elsewhere. B: production Tree(auto)/Default everywhere.' if stock else 'Eight custom walls under the bottom annulus only. Native tree-auto/default remains elsewhere. All custom support faces are blocked from recursive slicer supports.',
        support_reason='Full-circumference rim defect 3; stock fin walls versus the production automatic supports at the retained angle. PET-GF v8 G1 selects a .24 gap candidate; faucet removal is unqualified.' if stock else 'Full-circumference rim defect 3; matched fin walls with/without horizontal grip. PET-GF v8 G1 selects a .24 gap candidate; removal on this faucet is unqualified.',
        upper_finish='Production pose and geometry retained; crop ends before the original fine bands. Full upper finish remains accepted production evidence.',
        material_treatment='Native production bridge flow, fan and speeds in both conditions; no G-code edits.')
    save(folder/'preparation.json',report)
    save(project.with_suffix('.print.json'),report)
    native=WORK/('stock-vs-tree-native' if stock else 'native');native.mkdir(exist_ok=True)
    command=['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--slice','0','--arrange','0','--orient','0',
        '--outputdir',str(native),'--export-3mf','native.gcode.3mf',str(project)]
    save(folder/'slice-command.json',dict(argv=command))
    with (native/'slice.log').open('w') as log:
        subprocess.run(command,cwd=native,stdout=log,stderr=subprocess.STDOUT,check=True,
            env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1'))
    result=json.loads((native/'result.json').read_text())
    assert result.get('return_code')==0,result
    (folder/f'{stem}.gcode.3mf').write_bytes((native/'native.gcode.3mf').read_bytes())
    save(folder/'slice-result.json',result)
    print(json.dumps(result['sliced_plates']))

if __name__=='__main__': main()
