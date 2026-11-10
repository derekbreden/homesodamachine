"""prepare.py builds the enclosure support specimens and their offline comparison plate."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import uuid
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = ROOT/'.cache/runs/enclosure-support-coupons-2026-11-09'
CORE = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
PROD = 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
TITLE = '2026-11-09-enclosure-support-scenarios-left04-z018-mark1'
EXAMPLE = 'enclosure-support-scenarios'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def heavy(args, **kwargs):
    subprocess.run([str(ROOT/'tools/run'),'--',*map(str,args)],cwd=ROOT,check=True,**kwargs)


def geometry():
    spec = json.loads((HERE/'samples.json').read_text())
    out = RUN/'geometry'
    inputs = out/'inputs'
    inputs.mkdir(parents=True,exist_ok=True)
    for family in spec['families']:
        source = ROOT/family['source']
        mesh = trimesh.load_mesh(source,process=True)
        np.savez(inputs/(family['id']+'.npz'),
                 names=np.frombuffer(json.dumps([family['id']]).encode(),dtype=np.uint8),
                 colors=np.frombuffer(b'[null]',dtype=np.uint8),
                 records=np.frombuffer(json.dumps([[{'kind':'MESH','src':family['source'],'op':'read-stl'}]]).encode(),dtype=np.uint8),
                 V0=np.asarray(mesh.vertices,dtype=np.float64),T0=np.asarray(mesh.faces,dtype=np.uint32),
                 F0=np.zeros(len(mesh.faces),dtype=np.uint32))
        family['source_sha256'] = digest(source)
    (inputs/'spec.json').write_text(json.dumps(spec,indent=2)+'\n')
    link = ROOT/'tools/hsm/sandbox/examples'/(EXAMPLE+'.rs')
    if not link.exists():
        link.symlink_to(HERE/'samples.rs')
    try:
        heavy(['cargo','run','--release','--locked','-j2','--manifest-path','tools/hsm/Cargo.toml',
               '-p','hsm-sandbox','--example',EXAMPLE,'--',out])
    finally:
        if link.is_symlink() and link.resolve()==HERE/'samples.rs':
            link.unlink()
    parts = HERE/'parts'
    parts.mkdir(exist_ok=True)
    for path in out.glob('*.stl'):
        shutil.copyfile(path,parts/path.name)
    shutil.copyfile(out/'geometry.json',parts/'geometry.json')


def package():
    record = json.loads((HERE/'parts/geometry.json').read_text())
    spec = record['spec']
    profile = ROOT/spec['profile']
    with zipfile.ZipFile(profile) as archive:
        settings = json.loads(archive.read('Metadata/project_settings.config'))
        members = {name:archive.read(name) for name in archive.namelist()
                   if name in ['[Content_Types].xml','_rels/.rels'] or name.startswith('Metadata/filament_settings_')}
    model = ET.Element(f'{{{CORE}}}model',{'unit':'millimeter','requiredextensions':'p'})
    def uid(name):
        return str(uuid.uuid5(uuid.NAMESPACE_URL,TITLE+'/'+name))
    for name,value in [('Application','BambuStudio-02.08.02.61'),('BambuStudio:3mfVersion','1'),('Title',TITLE)]:
        ET.SubElement(model,f'{{{CORE}}}metadata',{'name':name}).text=value
    resources = ET.SubElement(model,f'{{{CORE}}}resources')
    build = ET.SubElement(model,f'{{{CORE}}}build',{f'{{{PROD}}}UUID':uid('build')})
    config = ET.Element('config')
    plate = ET.SubElement(config,'plate')
    def md(parent,key,value):
        ET.SubElement(parent,'metadata',{'key':key,'value':str(value)})
    for key,value in [('plater_id','1'),('plater_name',TITLE),('locked','false'),
                      ('filament_map_mode','Manual'),('filament_maps','1'),('filament_volume_maps','0'),
                      ('bed_type',settings['curr_bed_type'])]:
        md(plate,key,value)
    rels = ET.Element(f'{{{REL}}}Relationships')
    for index,part in enumerate(record['specimens']):
        family = next(f for f in spec['families'] if f['id']==part['family'])
        name = part['id']
        source = HERE/'parts'/(name+'.stl')
        mesh = trimesh.load_mesh(source,process=True)
        if not mesh.is_watertight or len(mesh.split())!=part.get('solids',1):
            raise ValueError(f'{name} must retain its declared closed print bodies')
        center = mesh.bounds.mean(axis=0)
        vertex = mesh.vertices-center
        part_id,object_id = index*2+1,index*2+2
        member = f'3D/Objects/object_{index+1}.model'
        packed = ET.Element(f'{{{CORE}}}model',{'unit':'millimeter'})
        packed_resources = ET.SubElement(packed,f'{{{CORE}}}resources')
        obj = ET.SubElement(packed_resources,f'{{{CORE}}}object',{'id':str(part_id),'type':'model',f'{{{PROD}}}UUID':uid(name+'/part')})
        packed_mesh = ET.SubElement(obj,f'{{{CORE}}}mesh')
        vs = ET.SubElement(packed_mesh,f'{{{CORE}}}vertices')
        for x,y,z in vertex:
            ET.SubElement(vs,f'{{{CORE}}}vertex',{'x':f'{x:.9f}','y':f'{y:.9f}','z':f'{z:.9f}'})
        ts = ET.SubElement(packed_mesh,f'{{{CORE}}}triangles')
        for a,b,c in mesh.faces:
            ET.SubElement(ts,f'{{{CORE}}}triangle',{'v1':str(a),'v2':str(b),'v3':str(c)})
        ET.register_namespace('',CORE)
        ET.register_namespace('p',PROD)
        members[member] = ET.tostring(packed,encoding='utf-8',xml_declaration=True)
        obj = ET.SubElement(resources,f'{{{CORE}}}object',{'id':str(object_id),'type':'model',f'{{{PROD}}}UUID':uid(name)})
        components = ET.SubElement(obj,f'{{{CORE}}}components')
        ET.SubElement(components,f'{{{CORE}}}component',{'objectid':str(part_id),'transform':'1 0 0 0 1 0 0 0 1 0 0 0',f'{{{PROD}}}path':'/'+member,f'{{{PROD}}}UUID':uid(name+'/component')})
        column = list(spec['interface_spacing_mm']).index(part['condition'])
        translation = [family.get('column_x_mm',spec['column_x_mm'])[column],family['row_y_mm'],float(center[2])]
        ET.SubElement(build,f'{{{CORE}}}item',{'objectid':str(object_id),'printable':'1','transform':'1 0 0 0 1 0 0 0 1 '+' '.join(map(str,translation))})
        obj = ET.SubElement(config,'object',{'id':str(object_id)})
        options = dict(family['settings'],name=name+' '+family['name'],extruder='1',
                       support_type='tree(auto)',support_interface_top_layers='2',support_top_z_distance='0.45',
                       support_interface_spacing=str(spec['interface_spacing_mm'][part['condition']]))
        options.update(spec.get('common_object_settings',{}))
        for key,value in options.items():
            md(obj,key,value)
        ET.SubElement(obj,'metadata',{'face_count':str(len(mesh.faces))})
        model_part = ET.SubElement(obj,'part',{'id':str(part_id),'subtype':'normal_part'})
        for key,value in [('name',source.name),('matrix','1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1'),
                          ('source_file',source.name),('source_object_id','0'),('source_volume_id','0'),
                          *[(f'source_offset_{k}',center[i]) for i,k in enumerate('xyz')]]:
            md(model_part,key,value)
        instance = ET.SubElement(plate,'model_instance')
        for key,value in [('object_id',object_id),('instance_id','0'),('identify_id',1901+index)]:
            md(instance,key,value)
        ET.SubElement(rels,f'{{{REL}}}Relationship',{'Target':'/'+member,'Id':f'rel-{index+1}',
                      'Type':'http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel'})
        part.update(stl_sha256=digest(source),position_mm=translation,identify_id=1901+index,
                    native_object_settings=options)
    ET.register_namespace('',CORE)
    members['3D/3dmodel.model'] = ET.tostring(model,encoding='utf-8',xml_declaration=True)
    members['Metadata/model_settings.config'] = ET.tostring(config,encoding='utf-8',xml_declaration=True)
    ET.register_namespace('',REL)
    members['3D/_rels/3dmodel.model.rels'] = ET.tostring(rels,encoding='utf-8',xml_declaration=True)
    project = HERE/(TITLE+'.3mf')
    cli = RUN/'input'/project.name
    cli.parent.mkdir(parents=True,exist_ok=True)
    for path,offline in [(project,False),(cli,True)]:
        local = dict(settings)
        if offline:
            local['post_process'] = []
        with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as archive:
            for member,data in members.items():
                archive.writestr(member,data)
            archive.writestr('Metadata/project_settings.config',json.dumps(local,indent=2)+'\n')
    record.update(project=project.name,project_sha256=digest(project),profile_sha256=digest(profile),
                  source_definition_sha256=digest(HERE/'samples.json'),crop_source_sha256=digest(HERE/'samples.rs'),
                  status='Prepared offline; no printer submission')
    (HERE/'preparation.json').write_text(json.dumps(record,indent=2)+'\n')
    print(project,flush=True)
    return project,cli


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry',action='store_true')
    parser.add_argument('--slice',action='store_true')
    args = parser.parse_args()
    if args.geometry:
        geometry()
    project,cli = package()
    if args.slice:
        sliced = RUN/'slice'
        sliced.mkdir(exist_ok=True)
        with (RUN/'bambu-cli.log').open('w') as log:
            heavy(['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--slice','0','--arrange','0','--orient','0',
                   '--outputdir',sliced,'--export-3mf',TITLE+'.gcode.3mf',cli],stdout=log,stderr=log)
        heavy([ROOT/'tools/hsm/target/release/petgf-cooling','--directory',sliced,'--project',project])
        ready = HERE/'ready'
        ready.mkdir(exist_ok=True)
        shutil.copyfile(sliced/(TITLE+'.gcode.3mf'),ready/(TITLE+'.gcode.3mf'))
        shutil.copyfile(sliced/'result.json',ready/'slice-result.json')


if __name__=='__main__':
    main()
