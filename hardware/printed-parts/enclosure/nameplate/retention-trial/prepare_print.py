"""Prepare a black/white broad-leaf nameplate with black supports on Mark2."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import trimesh
import nameplate_retention_trial as trial

HERE,ROOT,plate=trial.HERE,trial.ROOT,trial.plate
sys.path.insert(0,str(ROOT/'hardware/printed-parts/faucet'))
import refresh_print_project as writer
JOB=ROOT/'.cache/prints/2026-09-28-nameplate-broad-mark2-v3'
STEM='nameplate-broad-leaf-black-supports-z004-mark2-v3'
BASE=HERE.parent/'nameplate-001-petgf.3mf'
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('',NS)
Q=lambda n:'{'+NS+'}'+n


def main():
    JOB.mkdir(parents=True,exist_ok=True)
    target=JOB/(STEM+'-input.3mf')
    assert not target.exists(),'Keep sliced trials immutable.'
    with zipfile.ZipFile(BASE) as z:members={n:z.read(n) for n in z.namelist()}
    settings=json.loads(members['Metadata/project_settings.config'])
    assert settings['filament_nozzle_map']==['0','1'] and settings['filament_colour']==['#000000','#FFFFFF']
    assert settings['filament_printable']==['3','3']
    assert settings['support_top_z_distance']=='0.24' and settings['support_remove_small_overhang']=='0'
    settings.update(support_filament='1',support_interface_filament='1',
                    flush_into_support='0',support_object_first_layer_gap='0.5')
    members['Metadata/project_settings.config']=json.dumps(settings,indent=2).encode()
    model=ET.fromstring(members['3D/3dmodel.model'])
    body,ink=plate.split(cq.importers.importStep(str(HERE/(trial.NAME+'.step'))).val())
    shapes=(plate.print_pose(body),plate.print_pose(ink))
    mesh_info=[]
    for oid,shape,name in zip(('1','2'),shapes,('Black body','White artwork')):
        vertices,faces=shape.tessellate(.015,.05)
        mesh=trimesh.Trimesh(vertices=[v.toTuple() for v in vertices],faces=faces,process=True)
        assert mesh.is_watertight and mesh.is_winding_consistent
        obj=model.find(Q('resources')).find(Q('object')+f"[@id='{oid}']")
        obj.remove(obj.find(Q('mesh')))
        geometry=ET.SubElement(obj,Q('mesh'));vs=ET.SubElement(geometry,Q('vertices'));ts=ET.SubElement(geometry,Q('triangles'))
        for v in mesh.vertices:ET.SubElement(vs,Q('vertex'),**dict(zip(('x','y','z'),(f'{x:.8f}' for x in v))))
        for t in mesh.faces:ET.SubElement(ts,Q('triangle'),**dict(zip(('v1','v2','v3'),map(str,t))))
        mesh_info.append({'name':name,'id':oid,'triangles':len(mesh.faces),'bounds':mesh.bounds.tolist(),'watertight':True})
    resources=model.find(Q('resources'))
    for oid in ('4','5'):resources.remove(resources.find(Q('object')+f"[@id='{oid}']"))
    build=model.find(Q('build'))
    build.remove(build.find(Q('item')+"[@objectid='5']"))
    members['3D/3dmodel.model']=ET.tostring(model,encoding='UTF-8',xml_declaration=True)
    cfg=ET.fromstring(members['Metadata/model_settings.config'])
    cfg.remove(cfg.find("object[@id='5']"))
    plate_cfg=cfg.find('plate')
    for instance in list(plate_cfg.findall('model_instance')):
        if instance.find("metadata[@key='object_id']").get('value')=='5':plate_cfg.remove(instance)
    names={'3':trial.NAME}
    for obj in cfg.findall('object'):
        obj.find("metadata[@key='name']").set('value',names[obj.get('id')])
    cfg.find("plate/metadata[@key='plater_name']").set('value','Broad-leaf nameplate; black supports')
    members['Metadata/model_settings.config']=ET.tostring(cfg,encoding='UTF-8',xml_declaration=True)
    # Preserve the hook bearing height for the existing receiver.
    ranges=ET.Element('objects')
    for index in ('1',):
        obj=ET.SubElement(ranges,'object',id=index)
        band=ET.SubElement(obj,'range',min_z='5.0',max_z='5.17')
        ET.SubElement(band,'option',opt_key='layer_height').text='0.17'
    members['Metadata/layer_config_ranges.xml']=ET.tostring(ranges,encoding='UTF-8',xml_declaration=True)
    writer.archive_write(target,members)
    sources=[BASE,HERE/(trial.NAME+'.step'),HERE/(trial.NAME+'.stl'),HERE/(trial.RECEIVER+'.step'),HERE/(trial.RECEIVER+'.stl'),
             HERE/'nameplate_retention_trial.py',HERE/'geometry-check.json',Path(__file__)]
    report={'project':str(target.relative_to(ROOT)),'project_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
            'source_geometry_and_settings_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
            'printer':'Mark2','nozzle_mapping':{'left':'Black PET-GF, external 254','right':'White PET-GF, external 255'},
            'requested_z_trim_mm':.04,'expected_textured_plate_trim_mm':.02,
            'meshes':mesh_info,'identify_ids':{'2303':trial.NAME},
            'nominal_hook_bottom_print_z_mm':plate.THICK+trial.interface.LIP_START,
            'precision_shaft_layer_ranges_mm':[[5.,5.17,.17]],
            'settings':'Saved nameplate two-colour profile; black support base and interface, no flushing into supports, 0.5 mm support first-layer gap; other settings retained.',
            'support_policy':'Square hook bearings supported in black with exposed removal lanes; general XY gap 0.4 mm and top Z gap 0.24 mm.',
            'orientation':'Nameplate artwork down; existing receiver reused.'}
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
