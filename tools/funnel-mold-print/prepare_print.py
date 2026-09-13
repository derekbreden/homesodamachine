"""Prepare funnel-mold plates from current meshes and installed Bambu presets."""

import argparse
import hashlib
import json
import plistlib
import sys
import uuid
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

import trimesh

HERE = Path(__file__).resolve().parent
from profiles import (CORE, PROD, REL, fresh_settings, mesh_object, metadata,
                           preset_bundle, qn)


def choice(value, reason):
    return {'value': value, 'reason': reason}


def recipe(info, nozzle=0.4):
    fine = nozzle == 0.4
    size = f'{nozzle:g}'
    layer = '0.16' if fine else '0.24'
    process = '0.16mm Standard @BBL H2C' if fine else '0.40mm Standard @BBL H2C 0.8 nozzle'
    filament = 'Bambu PETG Translucent @BBL H2C'+('' if fine else ' 0.8 nozzle')
    return {
        'nozzle_mm': nozzle, 'nozzle_type': 'Standard' if fine else 'High Flow',
        'system_presets': {
            'machine': f'Bambu Lab H2C {size} nozzle',
            'process': process, 'filament': filament},
        'process_name': f'Funnel mold shell - {size} nozzle - tree supports',
        'filament_name': f'Funnel mold PETG Translucent - {size} nozzle - 255C',
        'z_trim': {'default_mm': 0.04, 'available_mm': [0.04, 0.18],
            'reason': 'User-established plate corrections; translucent uses +0.04 mm.'},
        'process_settings': {
            'enable_arc_fitting': choice('0', 'Connected H2C firmware uses curve planning.'),
            'layer_height': choice(layer, 'Fine layers on the forming slopes.'),
            'initial_layer_print_height': choice('0.2' if fine else '0.32', 'Stock nozzle first-layer height.'),
            'wall_generator': choice('arachne', 'Variable-width paths around sockets and shell transitions.'),
            'wall_loops': choice('4' if fine else '3', 'Continuous forming and dry-back perimeters.'),
            'sparse_infill_density': choice('100%', 'Solid modeled shells and flanges.'),
            'sparse_infill_pattern': choice('zig-zag', 'Alternating solid fill.'),
            'top_shell_layers': choice('5', 'Closed skin faces.'),
            'bottom_shell_layers': choice('5', 'Closed skin faces.'),
            'top_shell_thickness': choice('0.8', 'Solid top face.'),
            'bottom_shell_thickness': choice('0.8', 'Solid bottom face.'),
            'top_one_wall_type': choice('not apply', 'Full perimeter count at forming edges.'),
            'outer_wall_speed': choice(['40']*4, 'Nominal outer-wall speed; stock overhang overrides also apply.'),
            'outer_wall_acceleration': choice(['2000']*4, 'Controlled forming-wall acceleration.'),
            'top_surface_speed': choice(['60']*4, 'Flat forming faces capped at 60 mm/s.'),
            'seam_position': choice('back', 'Aligned seams for local finishing.'),
            'seam_placement_away_from_overhangs': choice('1', 'Account for adjacent overhangs.'),
            'reduce_crossing_wall': choice('1', 'Detour around forming faces when possible.'),
            'seam_gap': choice('0%', 'Closed seam paths.'),
            'brim_type': choice('outer_only', 'Removable adhesion brim around feet, flange and support roots.'),
            'brim_width': choice('6', 'Broad temporary bed grip.'),
            'brim_object_gap': choice('0.15', 'Breakaway brim gap.'),
            'skirt_loops': choice('0', 'Stock machine sequence primes the nozzle.'),
            'enable_support': choice('1', 'Automatic breakaway tree supports on the open dry backs.'),
            'support_type': choice('tree(auto)', 'The project uses automatic tree supports.'),
            'support_style': choice('default', 'Stock tree branching.'),
            'support_threshold_angle': choice('35', 'Project tree-support threshold.'),
            'support_on_build_plate_only': choice('0', 'Supports may root on accessible dry faces.'),
            'support_top_z_distance': choice('0.3', 'Project breakaway interface gap.'),
            'support_bottom_z_distance': choice('0.3', 'Project breakaway interface gap.'),
            'support_object_xy_distance': choice('0.4', 'Project lateral removal clearance.'),
            'support_interface_top_layers': choice('2', 'Two removable interface layers.'),
            'support_interface_bottom_layers': choice('2', 'Two removable interface layers.'),
            'support_interface_spacing': choice('0.5', 'Project sparse interface spacing.'),
            'support_filament': choice('0', 'Same PETG as model.'),
            'support_interface_filament': choice('0', 'Same PETG as model.'),
            'enable_prime_tower': choice('0', 'One filament per plate.')},
        'filament_settings': {
            'filament_prime_volume': choice(['45'], 'Bambu Studio saved purge volume.'),
            'nozzle_temperature': choice(['255', '255'], 'PETG Translucent specimen and existing process temperature.'),
            'nozzle_temperature_initial_layer': choice(['255', '255'], 'Same melt temperature on the first layer.'),
            'filament_max_volumetric_speed': choice(['12', '18'], '12 mm3/s standard nozzle, 18 mm3/s high flow.'),
            'filament_cost': choice(['11.20'], 'Ledger cost per kilogram.')},
        'layer_ranges_mm': {'cavity': [], 'core': []}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--z-trim', type=float, choices=(0.04, 0.18), default=0.04)
    parser.add_argument('--label')
    parser.add_argument('--nozzle', type=float, choices=(0.4, 0.8), default=0.4)
    parser.add_argument('--only', choices=('cavity', 'core'))
    args = parser.parse_args()
    info = json.loads((args.models/'design.json').read_text())
    settings_recipe = recipe(info, args.nozzle)
    presets = Path('/Applications/BambuStudio.app/Contents/Resources/profiles/BBL')
    settings, provenance = fresh_settings(presets, settings_recipe, args.z_trim)
    version = plistlib.loads((presets.parents[2]/'Info.plist').read_bytes())['CFBundleShortVersionString']
    data = {'Metadata/project_settings.config': json.dumps(settings, indent=2).encode()}
    model = ET.Element(qn('model'), unit='millimeter', requiredextensions='p',
        **{'xmlns:BambuStudio': 'http://schemas.bambulab.com/package/2021'})
    ET.SubElement(model, qn('metadata'), name='Application').text = f'BambuStudio-{version}'
    ET.SubElement(model, qn('metadata'), name='BambuStudio:3mfVersion').text = '1'
    ET.SubElement(model, qn('metadata'), name='Title').text = args.label or 'Funnel mold'
    resources = ET.SubElement(model, qn('resources'))
    build = ET.SubElement(model, qn('build'), **{f'{{{PROD}}}UUID': str(uuid.uuid4())})
    config = ET.Element('config')
    ranges = ET.Element('objects')
    rels = ET.Element(f'{{{REL}}}Relationships')
    assembled = ET.Element('assemble')
    provenance['mesh_sha256'] = {}
    names = (args.only,) if args.only else ('cavity', 'core')
    provenance['parts'] = list(names)
    for index, name in enumerate(names, 1):
        mesh_path = args.models/f'{name}.stl'
        mesh = trimesh.load(mesh_path, force='mesh', process=True)
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1
        center, height = mesh.bounds.mean(axis=0), mesh.extents[2]
        part_id, object_id = str(index*2-1), str(index*2)
        path = f'/3D/Objects/object_{index}.model'
        sub = ET.Element(qn('model'), unit='millimeter')
        subresources = ET.SubElement(sub, qn('resources'))
        mesh_object(subresources, part_id, mesh, center)
        data[path.lstrip('/')] = ET.tostring(sub, xml_declaration=True, encoding='UTF-8')
        obj = ET.SubElement(resources, qn('object'), id=object_id, type='model',
                            **{f'{{{PROD}}}UUID': str(uuid.uuid4())})
        components = ET.SubElement(obj, qn('components'))
        ET.SubElement(components, qn('component'), objectid=part_id,
            transform='1 0 0 0 1 0 0 0 1 0 0 0',
            **{f'{{{PROD}}}path': path, f'{{{PROD}}}UUID': str(uuid.uuid4())})
        rotation = '1 0 0 0 -1 0 0 0 -1' if name == 'core' else '1 0 0 0 1 0 0 0 1'
        transform = f'{rotation} {149.5+(index-1)*396} 160 {height/2:.9f}'
        ET.SubElement(build, qn('item'), objectid=object_id, transform=transform,
            printable='1', **{f'{{{PROD}}}UUID': str(uuid.uuid4())})
        ET.SubElement(rels, f'{{{REL}}}Relationship', Target=path, Id=f'rel-{index}',
            Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
        obj = ET.SubElement(config, 'object', id=object_id)
        metadata(obj, 'name', f"{args.label or 'Funnel mold'} {name}")
        metadata(obj, 'extruder', '1')
        ET.SubElement(obj, 'metadata', face_count=str(len(mesh.faces)))
        part = ET.SubElement(obj, 'part', id=part_id, subtype='normal_part', uuid=str(uuid.uuid4()))
        for key, value in {'name': name, 'matrix': '1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1',
                'source_file': mesh_path.name, 'source_object_id': 0, 'source_volume_id': 0,
                'source_offset_x': center[0], 'source_offset_y': center[1],
                'source_offset_z': center[2]}.items():
            metadata(part, key, value)
        ET.SubElement(part, 'mesh_stat', face_count=str(len(mesh.faces)), edges_fixed='0',
            degenerate_facets='0', facets_removed='0', facets_reversed='0', backwards_edges='0')
        plate = ET.SubElement(config, 'plate')
        for key, value in {'plater_id': index, 'plater_name': f"{args.label or 'Funnel mold'} {name}", 'locked': 'false',
                'filament_map_mode': 'Manual', 'filament_maps': '1',
                'filament_volume_maps': '1' if settings_recipe['nozzle_type'] == 'High Flow' else '0',
                'bed_type': 'Textured PEI Plate'}.items():
            metadata(plate, key, value)
        instance = ET.SubElement(plate, 'model_instance')
        for key, value in {'object_id': object_id, 'instance_id': 0, 'identify_id': 1800+index}.items():
            metadata(instance, key, value)
        layer_object = ET.SubElement(ranges, 'object', id=str(index))
        for bottom, top in settings_recipe['layer_ranges_mm'][name]:
            band = ET.SubElement(layer_object, 'range', min_z=str(bottom), max_z=str(top))
            ET.SubElement(band, 'option', opt_key='layer_height').text = '0.16'
        ET.SubElement(assembled, 'assemble_item', object_id=object_id, instance_id='0',
            transform=f'{rotation} 0 0 {height/2}', offset='0 0 0')
        ET.SubElement(assembled, 'assemble_item', object_id=object_id, volume_id='0',
            transform='1 0 0 0 1 0 0 0 1 0 0 0')
        provenance['mesh_sha256'][name] = hashlib.sha256(mesh_path.read_bytes()).hexdigest()
    config.append(assembled)
    for path, element in [('3D/3dmodel.model', model),
            ('Metadata/model_settings.config', config), ('Metadata/layer_config_ranges.xml', ranges)]:
        data[path] = ET.tostring(element, xml_declaration=True, encoding='UTF-8')
    package_rels = ET.Element(f'{{{REL}}}Relationships')
    ET.SubElement(package_rels, f'{{{REL}}}Relationship', Target='/3D/3dmodel.model', Id='rel-1',
        Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
    for path, element in [('3D/_rels/3dmodel.model.rels', rels), ('_rels/.rels', package_rels)]:
        data[path] = ET.tostring(element, xml_declaration=True, encoding='UTF-8').replace(
            b'ns0:', b'').replace(b'xmlns:ns0=', b'xmlns=')
    data['[Content_Types].xml'] = b'''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
<Default Extension="png" ContentType="image/png"/>
<Default Extension="gcode" ContentType="text/x.gcode"/>
</Types>'''
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, payload in data.items():
            archive.writestr(name, payload)
    provenance['recipe'] = settings_recipe
    provenance['slicer_version'] = version
    args.output.with_suffix('.provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    preset_bundle(presets, settings_recipe, version, args.output.parent/'funnel-mold-presets.bbscfg')
    print(args.output)


if __name__ == '__main__':
    main()
