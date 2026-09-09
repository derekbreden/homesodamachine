"""Prepare the three-plate Bambu project from the generated STL files.

Run with the project's CadQuery Python. The only inputs are the generated STL
files, print-recipe.json and Bambu Studio's installed system presets. --output
is an unsliced 3MF. Slice it in the matching Bambu Studio version before use.
Every supplied setting has a source in the accompanying provenance JSON.
"""
from pathlib import Path
import argparse
import copy
import json
import hashlib
import plistlib
import uuid
import zipfile
import xml.etree.ElementTree as ET
import trimesh

HERE = Path(__file__).resolve().parent
PROJECT = 'funnel-mold-petg-hf08-variable-016-040.3mf'
CORE = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
PROD = 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
ET.register_namespace('', CORE)
ET.register_namespace('p', PROD)
ET.register_namespace('BambuStudio', 'http://schemas.bambulab.com/package/2021')
qn = lambda tag: f'{{{CORE}}}{tag}'
uid = lambda: str(uuid.uuid4())
PRESET_METADATA = {'type', 'name', 'inherits', 'include', 'from', 'setting_id',
                   'instantiation', 'description', 'alias', 'filament_id',
                   'version', 'rename', 'compatible_printers'}


def system_preset(root, kind, name, files):
    """Resolve parent, included template, then leaf; record the last writer.

    These selected includes supply dual-extruder arrays. They have no parents;
    their explicit values are the template overrides, followed by leaf values.
    No user profile or previous 3MF is consulted.
    """
    path = root / kind / (name + '.json')
    raw = path.read_bytes(); data = json.loads(raw)
    source = f'{kind}/{path.name}'
    files[source] = hashlib.sha256(raw).hexdigest()
    values, sources, ids = {}, {}, {}
    if data.get('inherits'):
        values, sources, ids = system_preset(root, kind, data['inherits'], files)
    for include in data.get('include', []):
        extra, origins, _ = system_preset(root, kind, include, files)
        values.update(extra); sources.update(origins)
    for key, value in data.items():
        if key not in PRESET_METADATA:
            values[key] = value; sources[key] = {'preset': source}
    for key in ('filament_id', 'setting_id'):
        if key in data: ids[key] = data[key]
    return values, sources, ids


def trimmed_start_gcode(stock, trim):
    """Add the user's measured plate adjustment to the stock plate correction."""
    start = stock.index(';===== for Textured PEI Plate')
    end = stock.index('\nG150.1', start)
    block = f'''\
;===== plate compensation plus user-calibrated +{trim:.2f} mm Z trim =====
{{if curr_bed_type=="Textured PEI Plate"}}
    {{if nozzle_diameter_at_nozzle_id[initial_nozzle_id] == 0.2}}
        G29.1 Z{{{trim:.2f} - 0.01}}
    {{else}}
        G29.1 Z{{{trim:.2f} - 0.02}}
    {{endif}}
{{else}}
    {{if nozzle_diameter_at_nozzle_id[initial_nozzle_id] == 0.2}}
        G29.1 Z{{{trim:.2f} + 0.01}}
    {{else}}
        G29.1 Z{{{trim:.2f}}}
    {{endif}}
{{endif}}'''
    return stock[:start] + block + stock[end:]


def fresh_settings(root, recipe, trim):
    values, sources, files = {}, {}, {}
    filament_id = None
    for kind, name in recipe['system_presets'].items():
        resolved, origins, ids = system_preset(root, kind, name, files)
        values.update(resolved); sources.update(origins)
        if kind == 'filament': filament_id = ids['filament_id']
    for group in ('process_settings', 'filament_settings'):
        for key, choice in recipe[group].items():
            assert choice['reason'], key
            values[key] = choice['value']
            sources[key] = {'recipe': group, 'reason': choice['reason']}
    assignment = {
        'printer_settings_id': f'Bambu Lab H2C 0.8 High Flow +{trim:.2f} Z trim',
        'print_settings_id': recipe['process_name'],
        'filament_settings_id': [recipe['filament_name']],
        'inherits_group': [recipe['system_presets']['process'],
                           recipe['system_presets']['filament'],
                           recipe['system_presets']['machine']],
        'different_settings_to_system': [
            ';'.join(recipe['process_settings']),
            ';'.join(recipe['filament_settings']), 'machine_start_gcode;default_nozzle_volume_type;nozzle_volume_type'],
        'filament_ids': [filament_id], 'filament_colour': ['#DDEBF0'],
        'filament_map_mode': 'Manual', 'filament_map': ['1'],
        'filament_map_2': ['1'], 'filament_nozzle_map': ['0'],
        'filament_self_index': ['1', '1'],
        'filament_volume_map': ['1'],
        'nozzle_volume_type': ['High Flow', 'Standard'],
        'default_nozzle_volume_type': ['High Flow', 'Standard'],
        'extruder_nozzle_stats': ['High Flow#1', 'Standard#1'],
        'extruder_nozzle_stats_new': ['High Flow#1', 'Standard#1'],
        'curr_bed_type': 'Textured PEI Plate',
        'print_compatible_printers': [recipe['system_presets']['machine']] + [
            f'Bambu Lab H2C 0.8 High Flow +{v:.2f} Z trim' for v in recipe['z_trim']['available_mm']],
    }
    for key, value in assignment.items():
        values[key] = value
        sources[key] = {'generator': 'fresh_settings',
            'reason': 'One PETG filament on the left 0.8 mm High Flow nozzle, textured PEI; named source presets.'}
    values['machine_start_gcode'] = trimmed_start_gcode(values['machine_start_gcode'], trim)
    sources['machine_start_gcode'] = {
        'preset': sources['machine_start_gcode']['preset'],
        'generator': 'trimmed_start_gcode', 'z_trim_mm': trim,
        'reason': recipe['z_trim']['reason']}
    return values, {'system_preset_sha256': files, 'supplied_settings': {
        key: {'value': value, **sources[key]} for key, value in values.items()}}


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
    parser.add_argument('--presets', type=Path, default=Path(
        '/Applications/BambuStudio.app/Contents/Resources/profiles/BBL'))
    parser.add_argument('--recipe', type=Path, default=HERE/'print-recipe.json')
    parser.add_argument('--z-trim', type=float, choices=(0.04, 0.18))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    recipe = json.loads(args.recipe.read_text())
    trim = args.z_trim if args.z_trim is not None else recipe['z_trim']['default_mm']
    settings, provenance = fresh_settings(args.presets, recipe, trim)
    version = plistlib.loads((args.presets.parents[2]/'Info.plist').read_bytes())['CFBundleShortVersionString']
    provenance['slicer_version'] = version
    precision = {k: ','.join(v['value']) if isinstance(v['value'], list) else v['value']
                 for k, v in recipe['precision_settings'].items()}
    data = {'Metadata/project_settings.config': json.dumps(settings, indent=2).encode()}
    model = ET.Element(qn('model'), unit='millimeter', requiredextensions='p',
                       **{'xmlns:BambuStudio': 'http://schemas.bambulab.com/package/2021'})
    ET.SubElement(model, qn('metadata'), name='Application').text = f'BambuStudio-{version}'
    ET.SubElement(model, qn('metadata'), name='BambuStudio:3mfVersion').text = '1'
    ET.SubElement(model, qn('metadata'), name='Title').text = 'Funnel mold - guided screw extraction / vented ribs / 0.20 mm finish'
    resources = ET.SubElement(model, qn('resources'))
    build = ET.SubElement(model, qn('build'), **{f'{{{PROD}}}UUID': uid()})
    config = ET.Element('config'); rels = ET.Element(f'{{{REL}}}Relationships')
    assembly = ET.Element('assemble')
    instances = {1: [], 2: [], 3: []}
    layer_ranges = ET.Element('objects')
    provenance['recipe'] = recipe
    provenance['mesh_files'] = {}
    # Bambu plate pitch: 396 mm across columns, 384 mm down rows.
    layout = [('finish-witness', 1, (105, 135), False),
              ('cavity', 2, (545.5, 160), False),
              ('core', 3, (149.5, -224), True),
              ('hardware-witness', 1, (200, 145), False),
              ('guide-witness', 1, (140, 190), False)]
    object_paths = []
    for i, (name, plate, xy, flip) in enumerate(layout, 1):
        mesh = trimesh.load(HERE/f'funnel-mold-{name}.stl', force='mesh', process=True)
        provenance['mesh_files'][f'funnel-mold-{name}.stl'] = hashlib.sha256(
            (HERE/f'funnel-mold-{name}.stl').read_bytes()).hexdigest()
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
            for key, value in precision.items(): metadata(obj, key, value)
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
            provenance['mesh_files'][f'funnel-mold-{name}-surface-zone.stl'] = hashlib.sha256(
                (HERE/f'funnel-mold-{name}-surface-zone.stl').read_bytes()).hexdigest()
            zone.update_faces(zone.nondegenerate_faces()); zone.remove_unreferenced_vertices()
            assert zone.is_watertight and zone.is_winding_consistent, name
            zid = str(100+i); mesh_object(subr, zid, zone, center); component(zid)
            zp = copy.deepcopy(part); zp.set('id', zid); zp.set('subtype', 'modifier_part'); zp.set('uuid', uid())
            metadata(zp, 'name', 'Forming faces, registration and hardware fits - 60 mm/s')
            metadata(zp, 'source_file', f'funnel-mold-{name}-surface-zone.stl')
            for key, value in precision.items(): metadata(zp, key, value)
            zp.find('mesh_stat').set('face_count', str(len(zone.faces))); obj.append(zp)
            face_count.set('face_count', str(len(mesh.faces)+len(zone.faces)))
        data[path.lstrip('/')] = ET.tostring(sub, xml_declaration=True, encoding='UTF-8')
        # Bambu's layer-range object IDs are 1-based object order, not 3MF IDs.
        bands = recipe['layer_ranges_mm'][name]
        if bands:
            ro = ET.SubElement(layer_ranges, 'object', id=str(i))
            for band in bands:
                rr = ET.SubElement(ro, 'range', min_z=str(band['min_z']), max_z=str(band['max_z']))
                ET.SubElement(rr, 'option', opt_key='layer_height').text = str(band['layer_height'])
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
        plate = ET.Element('plate')
        metadata(plate, 'plater_id', i); metadata(plate, 'plater_name', name)
        metadata(plate, 'locked', 'false')
        metadata(plate, 'filament_map_mode', 'Manual')
        metadata(plate, 'filament_maps', '1')
        metadata(plate, 'filament_volume_maps', '1')
        for oid, identify in instances[i]:
            instance = ET.SubElement(plate, 'model_instance')
            metadata(instance, 'object_id', oid); metadata(instance, 'instance_id', 0)
            metadata(instance, 'identify_id', identify)
        config.append(plate)
    config.append(assembly)
    data['3D/3dmodel.model'] = ET.tostring(model, xml_declaration=True, encoding='UTF-8')
    data['3D/_rels/3dmodel.model.rels'] = ET.tostring(rels, xml_declaration=True, encoding='UTF-8').replace(b'ns0:', b'').replace(b'xmlns:ns0=', b'xmlns=')
    data['Metadata/model_settings.config'] = ET.tostring(config, xml_declaration=True, encoding='UTF-8')
    data['Metadata/layer_config_ranges.xml'] = ET.tostring(layer_ranges, xml_declaration=True, encoding='UTF-8')
    data['[Content_Types].xml'] = b'''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
<Default Extension="png" ContentType="image/png"/>
<Default Extension="gcode" ContentType="text/x.gcode"/>
</Types>'''
    package_rels = ET.Element(f'{{{REL}}}Relationships')
    ET.SubElement(package_rels, f'{{{REL}}}Relationship', Target='/3D/3dmodel.model',
                  Id='rel-1', Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
    data['_rels/.rels'] = ET.tostring(package_rels, xml_declaration=True, encoding='UTF-8').replace(b'ns0:', b'').replace(b'xmlns:ns0=', b'xmlns=')
    keep = ['Metadata/project_settings.config', 'Metadata/model_settings.config',
            'Metadata/layer_config_ranges.xml',
            '3D/3dmodel.model', '3D/_rels/3dmodel.model.rels', '[Content_Types].xml', '_rels/.rels', *object_paths]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name in keep: archive.writestr(name, data[name])
    provenance['input_3mf_sha256'] = hashlib.sha256(args.output.read_bytes()).hexdigest()
    args.output.with_suffix('.provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    # Bambu configuration bundles provide both plate calibrations in the
    # printer selector; the 3MF embeds the selected one, +0.04 mm by default.
    bundle = args.output.parent/'funnel-mold-hf08-z-trim-presets.bbscfg'
    stock, _, _ = system_preset(args.presets, 'machine', recipe['system_presets']['machine'], {})
    with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED) as archive:
        for offset in recipe['z_trim']['available_mm']:
            name = f'Bambu Lab H2C 0.8 High Flow +{offset:.2f} Z trim'
            profile = {'from': 'User', 'inherits': recipe['system_presets']['machine'],
                'name': name, 'printer_settings_id': name, 'version': version,
                'machine_start_gcode': trimmed_start_gcode(stock['machine_start_gcode'], offset),
                'nozzle_volume_type': ['High Flow', 'Standard'],
                'default_nozzle_volume_type': ['High Flow', 'Standard']}
            archive.writestr(name+'.json', json.dumps(profile, indent=2))


if __name__ == '__main__':
    main()
