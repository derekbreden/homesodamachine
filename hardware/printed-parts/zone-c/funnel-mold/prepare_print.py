"""Prepare the three-plate Bambu project from the generated STL files.

Run with the project's CadQuery Python. --profile-source supplies the retained
H2C/PETG machine and filament configuration; --output is an unsliced 3MF. Slice
that project in Bambu Studio before using it. Machine G-code is copied verbatim.
"""
from pathlib import Path
import argparse
import copy
import json
import uuid
import zipfile
import xml.etree.ElementTree as ET
import trimesh

HERE = Path(__file__).resolve().parent
PROJECT = 'funnel-mold-guided-vacuum-petg-08-016.3mf'
CORE = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
PROD = 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
ET.register_namespace('', CORE)
ET.register_namespace('p', PROD)
ET.register_namespace('BambuStudio', 'http://schemas.bambulab.com/package/2021')
qn = lambda tag: f'{{{CORE}}}{tag}'
uid = lambda: str(uuid.uuid4())
PRECISION = {'outer_wall_speed': '30,30,30,30',
             'inner_wall_speed': '80,80,80,80',
             'outer_wall_acceleration': '1000,1000,1000,1000',
             'inner_wall_acceleration': '3000,3000,3000,3000'}


def metadata(node, key, value):
    existing = node.find(f"metadata[@key='{key}']")
    if existing is None:
        existing = ET.SubElement(node, 'metadata', key=key)
    existing.set('value', str(value))


def mesh_object(resources, part_id, mesh, center):
    obj = ET.SubElement(resources, qn('object'), id=str(part_id), type='model')
    geometry = ET.SubElement(obj, qn('mesh'))
    verts = ET.SubElement(geometry, qn('vertices'))
    faces = ET.SubElement(geometry, qn('triangles'))
    for xyz in mesh.vertices-center:
        ET.SubElement(verts, qn('vertex'), **dict(zip(('x','y','z'), (f'{v:.9f}' for v in xyz))))
    for tri in mesh.faces:
        ET.SubElement(faces, qn('triangle'), **dict(zip(('v1','v2','v3'), map(str, tri))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile-source', type=Path, default=HERE/PROJECT)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with zipfile.ZipFile(args.profile_source) as archive:
        data = {name: archive.read(name) for name in archive.namelist()}
    settings = json.loads(data['Metadata/project_settings.config'])
    settings.update({'print_settings_id': 'Funnel mold guided vacuum PETG 0.8 - 0.16mm',
        'outer_wall_speed': ['100']*4, 'inner_wall_speed': ['100']*4,
        'outer_wall_acceleration': ['6000']*4, 'inner_wall_acceleration': ['6000']*4,
        'default_acceleration': ['8000']*4,
        'sparse_infill_density': '100%', 'sparse_infill_pattern': 'zig-zag',
        'bridge_speed': ['20']*4, 'internal_bridge_speed': ['30']*4,
        'overhang_2_4_speed': ['30']*4, 'max_travel_detour_distance': '30',
        'brim_width': '6', 'brim_type': 'outer_only',
        'top_shell_layers': '20', 'top_shell_thickness': '3.2',
        'bottom_shell_layers': '20', 'bottom_shell_thickness': '3.2'})
    data['Metadata/project_settings.config'] = json.dumps(settings, indent=2).encode()
    model = ET.fromstring(data['3D/3dmodel.model'])
    for node in model.findall(qn('metadata')):
        if node.get('name') == 'Title':
            node.text = 'Funnel mold - guided screw extraction / vented ribs / 0.20 mm finish'
    resources = model.find(qn('resources')); resources.clear()
    build = model.find(qn('build')); build.clear(); build.set(f'{{{PROD}}}UUID', uid())
    previous = ET.fromstring(data['Metadata/model_settings.config'])
    config = ET.Element('config'); rels = ET.Element(f'{{{REL}}}Relationships')
    assembly = ET.Element('assemble')
    instances = {1: [], 2: [], 3: []}
    # Bambu plate pitch: 396 mm across columns, 384 mm down rows.
    layout = [('finish-witness', 1, (105, 135), False),
              ('cavity', 2, (545.5, 160), False),
              ('core', 3, (149.5, -224), True),
              ('hardware-witness', 1, (200, 145), False),
              ('guide-witness', 1, (140, 190), False)]
    object_paths = []
    for i, (name, plate, xy, flip) in enumerate(layout, 1):
        mesh = trimesh.load(HERE/f'funnel-mold-{name}.stl', force='mesh', process=True)
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1, name
        center = mesh.bounds.mean(axis=0); height = mesh.extents[2]
        oid, pid = str(2*i), str(2*i-1)
        path = f'/3D/Objects/object_{i}.model'; object_paths.append(path.lstrip('/'))
        sub = ET.Element(qn('model'), unit='millimeter'); subr = ET.SubElement(sub, qn('resources'))
        mesh_object(subr, pid, mesh, center)
        obj = ET.SubElement(resources, qn('object'), id=oid, type='model', **{f'{{{PROD}}}UUID': uid()})
        components = ET.SubElement(obj, qn('components'))
        def component(part_id):
            ET.SubElement(components, qn('component'), objectid=str(part_id),
                transform='1 0 0 0 1 0 0 0 1 0 0 0',
                **{f'{{{PROD}}}path': path, f'{{{PROD}}}UUID': uid()})
        component(pid)
        orient = '1 0 0 0 -1 0 0 0 -1' if flip else '1 0 0 0 1 0 0 0 1'
        transform = f'{orient} {xy[0]} {xy[1]} {height/2:.9f}'
        ET.SubElement(build, qn('item'), objectid=oid, transform=transform,
                      printable='1', **{f'{{{PROD}}}UUID': uid()})
        ET.SubElement(rels, f'{{{REL}}}Relationship', Target=path, Id=f'rel-{i}',
                      Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
        obj = ET.SubElement(config, 'object', id=oid)
        metadata(obj, 'name', f'Funnel mold {name}'); metadata(obj, 'extruder', 1)
        face_count = ET.SubElement(obj, 'metadata', face_count=str(len(mesh.faces)))
        if 'witness' in name:
            for key, value in PRECISION.items(): metadata(obj, key, value)
        part = ET.SubElement(obj, 'part', id=pid, subtype='normal_part', uuid=uid())
        for key, value in {'name': f'funnel-mold-{name}',
                'matrix': '1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1',
                'source_file': f'funnel-mold-{name}.stl', 'source_object_id': 0,
                'source_volume_id': 0, 'source_offset_x': center[0],
                'source_offset_y': center[1], 'source_offset_z': center[2]}.items():
            metadata(part, key, value)
        ET.SubElement(part, 'mesh_stat', face_count=str(len(mesh.faces)), edges_fixed='0',
            degenerate_facets='0', facets_removed='0', facets_reversed='0', backwards_edges='0')
        if name in ('cavity', 'core'):
            zone = trimesh.load(HERE/f'funnel-mold-{name}-surface-zone.stl', force='mesh', process=True)
            zone.update_faces(zone.nondegenerate_faces()); zone.remove_unreferenced_vertices()
            assert zone.is_watertight and zone.is_winding_consistent, name
            zid = str(100+i); mesh_object(subr, zid, zone, center); component(zid)
            zp = copy.deepcopy(part); zp.set('id', zid); zp.set('subtype', 'modifier_part'); zp.set('uuid', uid())
            metadata(zp, 'name', 'Forming faces, registration and hardware fits - 30 mm/s')
            metadata(zp, 'source_file', f'funnel-mold-{name}-surface-zone.stl')
            for key, value in PRECISION.items(): metadata(zp, key, value)
            zp.find('mesh_stat').set('face_count', str(len(zone.faces))); obj.append(zp)
            face_count.set('face_count', str(len(mesh.faces)+len(zone.faces)))
        data[path.lstrip('/')] = ET.tostring(sub, xml_declaration=True, encoding='UTF-8')
        instances[plate].append((oid, 1700+i))
        ET.SubElement(assembly, 'assemble_item', object_id=oid, instance_id='0',
                      transform=f'{orient} 0 0 {height/2}', offset='0 0 0')
        ET.SubElement(assembly, 'assemble_item', object_id=oid, volume_id='0',
                      transform='1 0 0 0 1 0 0 0 1 0 0 0')
        print(name, 'plate', plate, 'mm', mesh.extents.round(3).tolist(),
              'mL', round(mesh.volume/1000, 2), 'faces', len(mesh.faces), flush=True)
    for i, name in enumerate(('Finish and hardware witnesses - print first',
                             'Cavity - vented ribs and bearing pads',
                             'Core - guided screw extraction'), 1):
        plate = copy.deepcopy(previous.find('plate'))
        for instance in plate.findall('model_instance'): plate.remove(instance)
        metadata(plate, 'plater_id', i); metadata(plate, 'plater_name', name)
        for entry in plate.findall('metadata'):
            if entry.get('key') in ('gcode_file', 'thumbnail_file', 'thumbnail_no_light_file', 'top_file', 'pick_file'):
                entry.set('value', entry.get('value').replace('_1.', f'_{i}.'))
        for oid, identify in instances[i]:
            instance = ET.SubElement(plate, 'model_instance')
            metadata(instance, 'object_id', oid); metadata(instance, 'instance_id', 0)
            metadata(instance, 'identify_id', identify)
        config.append(plate)
    config.append(assembly)
    data['3D/3dmodel.model'] = ET.tostring(model, xml_declaration=True, encoding='UTF-8')
    data['3D/_rels/3dmodel.model.rels'] = ET.tostring(rels, xml_declaration=True, encoding='UTF-8').replace(b'ns0:', b'').replace(b'xmlns:ns0=', b'xmlns=')
    data['Metadata/model_settings.config'] = ET.tostring(config, xml_declaration=True, encoding='UTF-8')
    keep = ['Metadata/project_settings.config', 'Metadata/model_settings.config',
            '3D/3dmodel.model', '3D/_rels/3dmodel.model.rels', '[Content_Types].xml', '_rels/.rels', *object_paths]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name in keep: archive.writestr(name, data[name])


if __name__ == '__main__':
    main()
