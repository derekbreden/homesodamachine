"""Native Mark2 pair: flat raised-artwork plate and a standard-clearance receiver."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import trimesh
import horizontal_wing_trial as trial
from prepare_receiver import support_settings

HERE,ROOT,plate=trial.HERE,trial.ROOT,trial.plate
sys.path.insert(0,str(ROOT/'hardware/printed-parts/faucet'))
import refresh_print_project as writer

JOB=ROOT/'.cache/prints/2026-09-29-nameplate-flat-standard-mark2-v5'
STEM='nameplate-flat-standard-pair-z004-mark2-v5'
BASE=HERE.parent/'nameplate-001-petgf.3mf'
PETGF=ROOT/'hardware/printed-parts/petgf.3mf'
MEASUREMENT=ROOT/'hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-29-registration-mark2-v3/physical-result.json'
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('',NS)
Q=lambda n:'{'+NS+'}'+n
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main(uncorrected=False):
    job=JOB/'uncorrected' if uncorrected else JOB
    stem=STEM+('-uncorrected' if uncorrected else '')
    job.mkdir(parents=True,exist_ok=True)
    target=job/(stem+'-input.3mf')
    assert not target.exists(),'Keep reviewed slices immutable.'
    with zipfile.ZipFile(BASE) as z:members={n:z.read(n) for n in z.namelist()}
    settings=json.loads(members['Metadata/project_settings.config'])
    with zipfile.ZipFile(PETGF) as z:shared=json.loads(z.read('Metadata/project_settings.config'))
    settings.update(support_settings(shared))
    settings.update(support_filament='1',support_interface_filament='1',flush_into_support='0',
                    layer_height=shared['layer_height'],initial_layer_print_height='0.2',
                    brim_type=shared['brim_type'],brim_width=shared['brim_width'])
    measurement=json.loads(MEASUREMENT.read_text());assert measurement['printer']=='Mark2'
    correction={'X':0.,'Y':0.} if uncorrected else measurement['white_correction_mm']
    settings['extruder_offset']=['0x0',f"{-correction['X']:g}x{-correction['Y']:g}"]
    assert settings['filament_nozzle_map']==['0','1']
    members['Metadata/project_settings.config']=json.dumps(settings,indent=2).encode()
    body,ink=plate.split(cq.importers.importStep(str(HERE/(trial.NAME+'.step'))).val())
    receiver=cq.importers.importStep(str(HERE/(trial.RECEIVER+'.step'))).val()
    rb=receiver.BoundingBox()
    posed_receiver=receiver.rotate((0,0,0),(1,0,0),180).translate((0,(rb.ymin+rb.ymax)/2,rb.zmax))
    shapes=(trial.print_pose(body),trial.print_pose(ink),posed_receiver)
    model=ET.fromstring(members['3D/3dmodel.model']);meshes=[]
    for oid,shape,name in zip(('1','2','4'),shapes,('Black nameplate','White artwork','Black receiver')):
        vertices,faces=shape.tessellate(.015,.05)
        mesh=trimesh.Trimesh(vertices=[v.toTuple() for v in vertices],faces=faces,process=True)
        assert mesh.is_watertight and mesh.is_winding_consistent
        obj=model.find(Q('resources')).find(Q('object')+f"[@id='{oid}']")
        obj.remove(obj.find(Q('mesh')))
        geometry=ET.SubElement(obj,Q('mesh'));vs=ET.SubElement(geometry,Q('vertices'));ts=ET.SubElement(geometry,Q('triangles'))
        for v in mesh.vertices:ET.SubElement(vs,Q('vertex'),**dict(zip(('x','y','z'),(f'{x:.8f}' for x in v))))
        for face in mesh.faces:ET.SubElement(ts,Q('triangle'),**dict(zip(('v1','v2','v3'),map(str,face))))
        meshes.append({'id':oid,'name':name,'triangles':len(mesh.faces),'bounds':mesh.bounds.tolist()})
    members['3D/3dmodel.model']=ET.tostring(model,encoding='UTF-8',xml_declaration=True)
    cfg=ET.fromstring(members['Metadata/model_settings.config'])
    plate_cfg=cfg.find("object[@id='3']");receiver_cfg=cfg.find("object[@id='5']")
    for k,v in {'name':trial.NAME,'enable_support':'0','brim_type':'no_brim','brim_width':'0'}.items():writer.metadata(plate_cfg,k,v)
    writer.metadata(receiver_cfg,'name',trial.RECEIVER)
    writer.metadata(cfg.find('plate'),'plater_name','Flat nameplate and standard-clearance receiver')
    members['Metadata/model_settings.config']=writer.xml(cfg)
    ranges=ET.Element('objects')
    # The prime tower requires matching model-layer schedules for both objects.
    for object_id in ('1','2'):
        obj=ET.SubElement(ranges,'object',id=object_id)
        band=ET.SubElement(obj,'range',min_z='.2',max_z='.48')
        ET.SubElement(band,'option',opt_key='layer_height').text='.28'
    members['Metadata/layer_config_ranges.xml']=writer.xml(ranges)
    writer.archive_write(target,members)
    geometry=json.loads((HERE/'geometry-check.json').read_text())
    sources=[ROOT/p for p in geometry['source_sha256']]+[BASE,PETGF,MEASUREMENT,Path(__file__),HERE/'geometry-check.json',HERE/'insertion-envelope.json']
    record={'printer':'Mark2','project_sha256':sha(target),'project':str(target.relative_to(ROOT)),
            'source_geometry_and_settings_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sources},
            'identify_ids':{'2303':trial.NAME,'2305':trial.RECEIVER},'meshes':meshes,
            'white_correction_mm':correction,'native_extruder_offset':settings['extruder_offset'],
            'nozzle_mapping':{'left':'black PET-GF, external 254','right':'white PET-GF, external 255'},
            'requested_z_trim_mm':.04,'expected_textured_plate_trim_mm':.02,
            'print_planes_z_mm':geometry['print_planes_z_mm'],
            'raised_perimeter':False,'artwork_rise_mm':trial.ARTWORK_RISE,
            'nameplate_supports':False,'receiver_support_settings':support_settings(settings),
            'receiver_build_direction':'CAD -Z up, matching enclosure back-top',
            'receiver_transform':{'translation':[165,205+(rb.ymin+rb.ymax)/2,rb.zmax],'rotation_X_degrees':180},
            'nameplate_translation':[165,125,0],'clearance_policy':geometry['clearance_policy'],
            'seated_pure_axis_travel_mm':geometry['seated_pure_axis_travel_mm'],'submitted':False}
    (job/'preparation.json').write_text(json.dumps(record,indent=2)+'\n')
    ready=job/'ready';ready.mkdir()
    command=['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--slice','0','--arrange','0','--orient','0',
             '--outputdir',str(ready),'--export-3mf',stem+'.gcode.3mf',str(target)]
    (job/'slice-command.json').write_text(json.dumps(command,indent=2)+'\n')
    with (ready/'bambu-cli.log').open('w') as log:
        rc=subprocess.run(command,cwd=ready,stdout=log,stderr=subprocess.STDOUT).returncode
    print(json.dumps({'slice_exit':rc,'archive':str(ready/(stem+'.gcode.3mf'))}),flush=True)
    return rc


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--uncorrected',action='store_true')
    raise SystemExit(main(parser.parse_args().uncorrected))
