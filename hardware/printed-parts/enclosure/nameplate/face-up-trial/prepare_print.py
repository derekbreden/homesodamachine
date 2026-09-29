"""Slice a face-up nameplate with all white artwork raised and black snug supports."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import trimesh
import face_up_trial as trial

HERE,ROOT,plate=trial.HERE,trial.ROOT,trial.plate
sys.path.insert(0,str(ROOT/'hardware/printed-parts/faucet'))
import refresh_print_project as writer
JOB=ROOT/'.cache/prints/2026-09-29-nameplate-all-ink-raised-mark2-v4'
STEM='nameplate-all-ink-raised-clearance-z004-mark2-v4'
BASE=HERE.parent/'nameplate-001-petgf.3mf'
PETGF=ROOT/'hardware/printed-parts/petgf.3mf'
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
    with zipfile.ZipFile(PETGF) as z:
        shared=json.loads(z.read('Metadata/project_settings.config'))
    contact_keys=('support_line_width','support_top_z_distance','support_bottom_z_distance',
                  'support_interface_top_layers','support_interface_bottom_layers',
                  'support_interface_spacing','support_bottom_interface_spacing',
                  'support_interface_pattern','support_interface_loop_pattern',
                  'support_base_pattern_spacing','support_expansion')
    settings.update({k:shared[k] for k in contact_keys})
    assert settings['support_top_z_distance']=='0.45'
    assert settings['support_interface_top_layers']=='2' and settings['support_interface_spacing']=='0.5'
    settings.update(support_filament='1',support_interface_filament='1',
                    flush_into_support='0',support_object_first_layer_gap='0.5',
                    support_type='normal(auto)',support_style='snug',support_base_pattern='rectilinear',
                    support_object_xy_distance='0.8',support_bottom_z_distance='0.45',
                    support_remove_small_overhang='0')
    members['Metadata/project_settings.config']=json.dumps(settings,indent=2).encode()
    model=ET.fromstring(members['3D/3dmodel.model'])
    body,ink=plate.split(cq.importers.importStep(str(HERE/(trial.NAME+'.step'))).val())
    shapes=(trial.print_pose(body),trial.print_pose(ink))
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
    cfg.find("plate/metadata[@key='plater_name']").set('value','Face-up nameplate; all white artwork raised; normal snug black supports')
    members['Metadata/model_settings.config']=ET.tostring(cfg,encoding='UTF-8',xml_declaration=True)
    # Align the nose, catch, plate back, face and raised artwork to layer boundaries.
    ranges=ET.Element('objects')
    obj=ET.SubElement(ranges,'object',id='1')
    for low,high,height in ((3.08,3.20,.12),(8.0,8.13,.13)):
        band=ET.SubElement(obj,'range',min_z=str(low),max_z=str(high))
        ET.SubElement(band,'option',opt_key='layer_height').text=str(height)
    members['Metadata/layer_config_ranges.xml']=ET.tostring(ranges,encoding='UTF-8',xml_declaration=True)
    writer.archive_write(target,members)
    geometry=json.loads((HERE/'geometry-check.json').read_text())
    sources=[ROOT/p for p in geometry['source_sha256']]+[BASE,PETGF,HERE/'geometry-check.json',Path(__file__)]
    report={'project':str(target.relative_to(ROOT)),'project_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
            'source_geometry_and_settings_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
            'printer':'Mark2','nozzle_mapping':{'left':'Black PET-GF, external 254','right':'White PET-GF, external 255'},
            'requested_z_trim_mm':.04,'expected_textured_plate_trim_mm':.02,
            'meshes':mesh_info,'identify_ids':{'2303':trial.NAME},
            'nominal_hook_bearing_print_z_mm':trial.retention.interface.TAB_LENGTH-trial.retention.interface.LIP_START,
            'print_planes_z_mm':geometry['print_planes_z_mm'],
            'artwork_rise_mm':trial.ARTWORK_RISE,
            'raised_artwork':geometry['raised_artwork'],
            'shared_petgf_support_contacts':{k:shared[k] for k in contact_keys},
            'support_clearance_overrides':{'support_object_xy_distance':'0.8','support_bottom_z_distance':'0.45','support_object_first_layer_gap':'0.5'},
            'precision_layer_ranges_mm':[[3.08,3.20,.12],[8.0,8.13,.13]],
            'settings':'Two-colour PET-GF. Normal auto supports, Snug style. Shared PET-GF contact settings: two top interface layers, 0.50 mm spacing, 0.45 mm top Z gap. Black support base and interface; no flushing into supports. Lateral gap 0.80 mm, bottom Z gap 0.45 mm, first-layer support gap 0.50 mm.',
            'support_policy':'Black normal snug supports carry the plate back. The angled insertion noses print from the hook tips upward. Open withdrawal lanes between the leaves and toward the short ends. Verify actual bead-edge separation along every leaf layer and both vertical contact gaps before submission.',
            'orientation':'Nameplate face +Z; hook tips on bed. Existing receiver reused.'}
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
