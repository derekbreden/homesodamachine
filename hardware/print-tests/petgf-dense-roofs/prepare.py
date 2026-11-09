"""prepare.py packages the authored ceiling meshes with native per-object interface settings."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import uuid
import xml.etree.ElementTree as ET
import zipfile

import trimesh

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CORE = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
PROD = 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
TITLE = '2026-11-09-dense-roofs-left04-z018-mark1'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cli-output', type=Path, required=True)
    args = parser.parse_args()
    recipe = json.loads((HERE/'parts/geometry.json').read_text())
    profile = ROOT/recipe['profile']
    template = HERE.parent/'petgf-interface-patterns/interface-patterns.3mf'
    with zipfile.ZipFile(profile) as archive:
        settings = json.loads(archive.read('Metadata/project_settings.config'))
        members = {n: archive.read(n) for n in archive.namelist()
                   if re.fullmatch(r'Metadata/filament_settings_\d+\.config', n)}
    with zipfile.ZipFile(template) as archive:
        model = ET.fromstring(archive.read('3D/3dmodel.model'))
        config = ET.fromstring(archive.read('Metadata/model_settings.config'))
        rels = ET.fromstring(archive.read('3D/_rels/3dmodel.model.rels'))
        members['[Content_Types].xml'] = archive.read('[Content_Types].xml')
        members['_rels/.rels'] = archive.read('_rels/.rels')
    start = settings['machine_start_gcode']
    marker = re.search(r';===== (?:for Textured PEI Plate|plate compensation plus user-calibrated)', start)
    if marker is None:
        raise ValueError('No recognized plate compensation block')
    end = start.index('\nG150.1', marker.start())
    trim = recipe['z_trim_mm']
    block = (';===== plate compensation plus user-calibrated Z trim =====\n'
             '{if curr_bed_type=="Textured PEI Plate"}\n'
             '    {if nozzle_diameter_at_nozzle_id[initial_nozzle_id] == 0.2}\n'
             f'        G29.1 Z{{{trim:.2f} - 0.01}}\n'
             '    {else}\n'
             f'        G29.1 Z{{{trim:.2f} - 0.02}}\n'
             '    {endif}\n{else}\n'
             '    {if nozzle_diameter_at_nozzle_id[initial_nozzle_id] == 0.2}\n'
             f'        G29.1 Z{{{trim:.2f} + 0.01}}\n'
             '    {else}\n'
             f'        G29.1 Z{{{trim:.2f}}}\n'
             '    {endif}\n{endif}')
    identity = f'Bambu Lab H2C {recipe["nozzle_diameter_mm"]} Standard +{trim:.2f} Z trim'
    compatible = list(dict.fromkeys(settings.get('print_compatible_printers',[])+[identity]))
    settings.update(machine_start_gcode=start[:marker.start()]+block+start[end:],
                    printer_settings_id=identity, print_compatible_printers=compatible,
                    enable_support='1', brim_type='no_brim', skirt_loops='0',
                    filament_colour=['#000000'], filament_map=['1'], filament_map_mode='Manual')
    resources = model.find(f'{{{CORE}}}resources')
    build = model.find(f'{{{CORE}}}build')
    plate = config.find('plate')
    count = len(recipe['specimens'])
    for parent, children in [(resources,list(resources)),(build,list(build)),
                             (plate,plate.findall('model_instance')),
                             (config,config.findall('object')),(rels,list(rels))]:
        for child in children[count:]:
            parent.remove(child)
    for element in model.iter():
        key = f'{{{PROD}}}UUID'
        if key in element.attrib:
            element.set(key,str(uuid.uuid5(uuid.NAMESPACE_URL,TITLE+'/'+element.get(key))))
    for metadata in model.findall(f'{{{CORE}}}metadata'):
        if metadata.get('name') == 'Title':
            metadata.text = TITLE
    for metadata in plate.findall('metadata'):
        if metadata.get('key') == 'plater_name':
            metadata.set('value', TITLE)
    for index, specimen in enumerate(recipe['specimens']):
        name = 'roof-'+specimen['id']
        path = HERE/'parts'/(name+'.stl')
        mesh = trimesh.load_mesh(path,process=True)
        if not mesh.is_watertight or len(mesh.split()) != 1:
            raise ValueError(f'{name}: one watertight coupon required')
        center = (mesh.bounds[0]+mesh.bounds[1])/2
        vertices = mesh.vertices-center
        part_id = index*2+1
        mesh_model = ET.Element('model',{'xmlns':CORE,'unit':'millimeter'})
        mesh_resources = ET.SubElement(mesh_model,'resources')
        obj = ET.SubElement(mesh_resources,'object',{'id':str(part_id),'type':'model'})
        packed_mesh = ET.SubElement(obj,'mesh')
        vs = ET.SubElement(packed_mesh,'vertices')
        for x,y,z in vertices:
            ET.SubElement(vs,'vertex',{'x':f'{x:.9f}','y':f'{y:.9f}','z':f'{z:.9f}'})
        ts = ET.SubElement(packed_mesh,'triangles')
        for a,b,c in mesh.faces:
            ET.SubElement(ts,'triangle',{'v1':str(a),'v2':str(b),'v3':str(c)})
        members[f'3D/Objects/object_{index+1}.model'] = ET.tostring(mesh_model,encoding='utf-8',xml_declaration=True)
        build[index].set('transform','1 0 0 0 1 0 0 0 1 '+' '.join(str(v) for v in specimen['position_mm']))
        obj = config.findall('object')[index]
        for child in list(obj):
            if child.tag == 'metadata':
                obj.remove(child)
        values = {'name':f'{specimen["id"]} interface spacing {specimen["interface_spacing_mm"]}',
                  'extruder':'1','support_top_z_distance':str(recipe['requested_top_z_distance_mm']),
                  'support_interface_top_layers':str(recipe['interface_layers']),
                  'support_interface_pattern':recipe['interface_pattern'],
                  'support_interface_spacing':str(specimen['interface_spacing_mm'])}
        for key,value in values.items():
            ET.SubElement(obj,'metadata',{'key':key,'value':value})
        ET.SubElement(obj,'metadata',{'face_count':str(len(mesh.faces))})
        for md in obj.find('part').findall('metadata'):
            key = md.get('key')
            if key in ('name','source_file'):
                md.set('value',path.name)
            elif key.startswith('source_offset_'):
                md.set('value',str(center['xyz'.index(key[-1])]))
        specimen.update(stl_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                        bounds_mm=mesh.bounds.tolist(),watertight=True)
    ET.register_namespace('',CORE)
    ET.register_namespace('p',PROD)
    members['3D/3dmodel.model'] = ET.tostring(model,encoding='utf-8',xml_declaration=True)
    members['Metadata/model_settings.config'] = ET.tostring(config,encoding='utf-8',xml_declaration=True)
    ET.register_namespace('',REL)
    members['3D/_rels/3dmodel.model.rels'] = ET.tostring(rels,encoding='utf-8',xml_declaration=True)
    project = HERE/(TITLE+'.3mf')
    for path,cli in [(project,False),(args.cli_output,True)]:
        local = dict(settings)
        if cli:
            local['post_process'] = []
        path.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as archive:
            for member,data in members.items():
                archive.writestr(member,data)
            archive.writestr('Metadata/project_settings.config',json.dumps(local,indent=2)+'\n')
    recipe.update(project=project.name,project_sha256=hashlib.sha256(project.read_bytes()).hexdigest(),
                  source_profile_sha256=hashlib.sha256(profile.read_bytes()).hexdigest(),
                  mesh_template=str(template.relative_to(ROOT)),
                  source_code_sha256=hashlib.sha256((HERE/'coupons.rs').read_bytes()).hexdigest())
    (HERE/'recipe.json').write_text(json.dumps(recipe,indent=2)+'\n')
    print(project)


if __name__ == '__main__':
    main()
