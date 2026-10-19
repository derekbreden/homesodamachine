"""Archived four-straight-receiver preparation; no printer action.

Uses the retained Siraya single-elbow process and material recipe. Receiver
geometry uses the archive's straight-receiver source name and +Y-to-+Z pose.
This script does not prepare the current asymmetric junctions, fixed returns
or twenty-part dock; those wet parts use individual manufacturing poses and
one object per plate.
"""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import uuid
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import trimesh

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/bambu_printer.py').is_file())
SOURCE=ROOT/'hardware/printed-parts/enclosure/enclosure/enclosure-pump-receiver.stl'
SOURCE_REFERENCE=HERE/'input-snapshots/receiver-source-current-geometry.py.txt'
RECIPE_DIR=ROOT/'future/pump-elbow-exploration/prints/2026-10-14-compact-single-siraya85a-overhang10-engineering-z000-mark1'
RECIPE=next(p for p in RECIPE_DIR.glob('*.3mf') if not p.name.endswith('.gcode.3mf'))
SLICER=Path('/Applications/BambuStudio.app/Contents/MacOS/BambuStudio')
STEM='2026-10-18-four-pump-receivers-siraya85a-right06-z000-mark1'
SETTINGS='Metadata/project_settings.config'
CORE='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
PROD='http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
REL='http://schemas.openxmlformats.org/package/2006/relationships'
ET.register_namespace('',CORE)
ET.register_namespace('p',PROD)
I='1 0 0 0 1 0 0 0 1 0 0 0'
POSES=((159.5,142.),(195.5,142.),(159.5,178.),(195.5,178.))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def q(name):
    return f'{{{CORE}}}{name}'


def uid(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL,'homesodamachine/pump-receiver-preparation/'+name))


def xml(node):
    return ET.tostring(node,encoding='UTF-8',xml_declaration=True)


def metadata(parent,key,value):
    ET.SubElement(parent,'metadata',key=key,value=str(value))


def mesh_object(resources,id_,mesh,name):
    obj=ET.SubElement(resources,q('object'),id=str(id_),type='model',
                      **{f'{{{PROD}}}UUID':uid(name)})
    body=ET.SubElement(obj,q('mesh'))
    vertices=ET.SubElement(body,q('vertices'));triangles=ET.SubElement(body,q('triangles'))
    for vertex in mesh.vertices:
        ET.SubElement(vertices,q('vertex'),**dict(zip('xyz',(f'{v:.9f}' for v in vertex))))
    for face in mesh.faces:
        ET.SubElement(triangles,q('triangle'),**dict(zip(('v1','v2','v3'),map(str,face))))


def main():
    HERE.mkdir(parents=True,exist_ok=True)
    SOURCE_REFERENCE.parent.mkdir(exist_ok=True)
    SOURCE_REFERENCE.write_bytes((ROOT/'hardware/printed-parts/enclosure/pump-dock/pump_receiver.py').read_bytes())
    with zipfile.ZipFile(RECIPE) as z:
        recipe=json.loads(z.read(SETTINGS))
        original=json.loads(z.read(SETTINGS))
        members={name:z.read(name) for name in ('[Content_Types].xml','_rels/.rels')}
    recipe.update(print_settings_id='Four permanent pump receivers Siraya85A right06 Mark1',
                  enable_support='1',support_type='tree(auto)',support_style='default',
                  support_filament='1',support_interface_filament='1',flush_into_support='0',
                  seam_position='nearest',reduce_crossing_wall='1',time_lapse_gcode='',
                  top_one_wall_type='not apply')
    members[SETTINGS]=(json.dumps(recipe,indent=2)+'\n').encode()

    mesh=trimesh.load(SOURCE,force='mesh',process=True)
    rotation=np.array(((1,0,0),(0,0,-1),(0,1,0)),dtype=float)
    mesh.vertices=mesh.vertices@rotation.T
    mesh.vertices[np.abs(mesh.vertices)<1e-9]=0.
    blocker=trimesh.creation.cylinder(radius=4.65,height=15.2,sections=96)
    blocker.apply_translation((0,0,7.5))
    geometry=ET.Element(q('model'),unit='millimeter')
    resources=ET.SubElement(geometry,q('resources'))
    mesh_object(resources,1,mesh,'receiver-mesh')
    mesh_object(resources,2,blocker,'wet-bore-blocker-mesh')
    member='3D/Objects/permanent_pump_receiver.model'
    members[member]=xml(geometry)

    model=ET.Element(q('model'),unit='millimeter',requiredextensions='p')
    ET.SubElement(model,q('metadata'),name='Application').text='BambuStudio-02.08.02.61'
    ET.SubElement(model,q('metadata'),name='BambuStudio:3mfVersion').text='1'
    ET.SubElement(model,q('metadata'),name='Title').text='Four permanent pump receivers; offline review'
    resources=ET.SubElement(model,q('resources'))
    build=ET.SubElement(model,q('build'),**{f'{{{PROD}}}UUID':uid('build')})
    config=ET.Element('config')
    plate=ET.SubElement(config,'plate')
    for key,value in dict(plater_id=1,plater_name='Four permanent TPU receivers - offline review',
                          locked='false',filament_map_mode='Auto For Flush',filament_maps='2',
                          filament_volume_maps='0',bed_type=recipe['curr_bed_type']).items():
        metadata(plate,key,value)
    assemble=ET.SubElement(config,'assemble')
    parts=[]
    for idx,(cx,cy) in enumerate(POSES,1):
        object_id=10+idx
        owner=ET.SubElement(resources,q('object'),id=str(object_id),type='model',
                            **{f'{{{PROD}}}UUID':uid(f'owner-{idx}')})
        components=ET.SubElement(owner,q('components'))
        cfg=ET.SubElement(config,'object',id=str(object_id))
        metadata(cfg,'name',f'Permanent pump receiver {idx}')
        metadata(cfg,'extruder',1)
        for part_id,subtype,name,part_mesh in ((1,'normal_part','permanent-pump-receiver',mesh),
                          (2,'support_blocker','wet-bore-support-exclusion',blocker)):
            ET.SubElement(components,q('component'),objectid=str(part_id),transform=I,
                          **{f'{{{PROD}}}path':'/'+member,
                             f'{{{PROD}}}UUID':uid(f'component-{idx}-{part_id}')})
            part=ET.SubElement(cfg,'part',id=str(part_id),subtype=subtype,
                               uuid=uid(f'part-{idx}-{part_id}'))
            for key,value in dict(name=name,matrix='1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1',
                                  extruder=1,source_file=SOURCE.name if part_id==1 else name,
                                  source_object_id=0,source_volume_id=0,
                                  source_offset_x=0,source_offset_y=0,source_offset_z=0).items():
                metadata(part,key,value)
            ET.SubElement(part,'mesh_stat',face_count=str(len(part_mesh.faces)),edges_fixed='0',
                          degenerate_facets='0',facets_removed='0',facets_reversed='0',backwards_edges='0')
        transform=f'1 0 0 0 1 0 0 0 1 {cx} {cy} 0'
        ET.SubElement(build,q('item'),objectid=str(object_id),transform=transform,printable='1',
                      **{f'{{{PROD}}}UUID':uid(f'item-{idx}')})
        instance=ET.SubElement(plate,'model_instance')
        for key,value in dict(object_id=object_id,instance_id=0,identify_id=2300+idx).items():
            metadata(instance,key,value)
        ET.SubElement(assemble,'assemble_item',object_id=str(object_id),instance_id='0',
                      transform=transform,offset='0 0 0')
        parts.append(dict(name=f'permanent-pump-receiver-{idx}',object_id=object_id,
                          identify_id=2300+idx,source=str(SOURCE.relative_to(ROOT)),
                          source_sha256=sha(SOURCE.read_bytes()),source_center_mm=[0,0,0],
                          plate_translation_mm=[cx,cy,0],build_transform=[1,0,0,0,1,0,0,0,1,cx,cy,0],
                          source_rotation_rows=rotation.tolist(),member=member))
    members['3D/3dmodel.model']=xml(model)
    members['Metadata/model_settings.config']=xml(config)
    rels=ET.Element(f'{{{REL}}}Relationships')
    ET.SubElement(rels,f'{{{REL}}}Relationship',Target='/'+member,Id='rel-1',
                  Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
    members['3D/_rels/3dmodel.model.rels']=xml(rels).replace(b'ns0:',b'').replace(b'xmlns:ns0=',b'xmlns=')
    project=HERE/(STEM+'.3mf')
    with zipfile.ZipFile(project,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(members.items()):
            z.writestr(name,data)
    changes={k:dict(source=original.get(k),prepared=recipe.get(k))
             for k in recipe if original.get(k)!=recipe.get(k)}
    record=dict(status='Offline print preparation; no printer contacted or started',
                prepared_at=datetime.now(timezone.utc).isoformat(),parts=parts,
                source_recipe=str(RECIPE.relative_to(ROOT)),source_recipe_sha256=sha(RECIPE.read_bytes()),
                source_geometry_sha256=sha(SOURCE.read_bytes()),project=project.name,
                geometry_definition_snapshot=str(SOURCE_REFERENCE.relative_to(HERE)),
                geometry_definition_sha256=sha(SOURCE_REFERENCE.read_bytes()),
                project_sha256=sha(project.read_bytes()),settings_changes=changes,
                rotation='Source +Y bore rotated +90 degrees about X to print +Z; front lip at Z0',
                normal_volume_count=4,bore_support_blocker_count=4,
                bore_support_exclusion=dict(radius_mm=4.65,z_mm=[-.1,15.1],
                    reason='Keep all supports outside the fluid passage and both sealing lands; exterior Tree(auto)/Default decisions remain active'),
                print_mesh_bounds_mm=mesh.bounds.tolist(),per_part_cad_volume_mm3=float(mesh.volume),
                material='Siraya Tech Flex TPU85A Clear; SKU ST3008',
                inherited_physical_scope='Accepted single-elbow exterior quality; internal stringing reported. No receiver acceptance.')
    (HERE/'preparation.json').write_text(json.dumps(record,indent=2)+'\n')
    cache=ROOT/'.cache/pump-dock-engineering/receiver-slice'
    cache.mkdir(parents=True,exist_ok=True)
    run=Path(tempfile.mkdtemp(prefix='native-',dir=cache))
    archive=HERE/(STEM+'.gcode.3mf')
    command=[str(SLICER),'--slice','0','--arrange','0','--orient','0',
             '--export-3mf',archive.name,'--outputdir',str(run),str(project)]
    (HERE/'slice-command.json').write_text(json.dumps(command,indent=2)+'\n')
    print('NATIVE_RUN',run,flush=True)
    with (run/'slice.log').open('w') as log:
        result=subprocess.run(command,cwd=run,stdout=log,stderr=subprocess.STDOUT,
                              env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1'))
    record['slicer_exit_code']=result.returncode
    if (run/'result.json').exists():
        native_result=json.loads((run/'result.json').read_text())
        (HERE/'slice-result.json').write_text(json.dumps(native_result,indent=2)+'\n')
    if not (run/archive.name).exists():
        record['status']='Native slicer produced no archive'
        record['slice_log_tail']=(run/'slice.log').read_text(errors='replace')[-5000:]
        (HERE/'native-readback.json').write_text(json.dumps(record,indent=2)+'\n')
        raise SystemExit(result.returncode or 1)
    archive.write_bytes((run/archive.name).read_bytes())
    with zipfile.ZipFile(archive) as z:
        gcode=z.read('Metadata/plate_1.gcode')
        emitted=json.loads(z.read(SETTINGS))
        record.update(archive=archive.name,archive_sha256=sha(archive.read_bytes()),
                      gcode_sha256=sha(gcode),gcode_md5_matches=
                        hashlib.md5(gcode).hexdigest()==z.read('Metadata/plate_1.gcode.md5').decode().strip().lower(),
                      emitted_recipe_matches_prepared=emitted==recipe,
                      cache_run=str(run.relative_to(ROOT)))
    (run/'plate_1.gcode').write_bytes(gcode)
    row,=native_result['sliced_plates']
    record.update(estimated_seconds=row['total_predication'],
                  estimated_filament_g=sum(f['total_used_g'] for f in row['filaments']),
                  slicer_warning=row['warning_message'])
    (HERE/'native-readback.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ('status','archive','estimated_seconds',
                    'estimated_filament_g','slicer_warning','gcode_md5_matches','cache_run')},indent=2),flush=True)


if __name__=='__main__':
    main()
