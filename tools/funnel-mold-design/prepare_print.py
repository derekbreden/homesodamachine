"""Prepare two solid-mold plates from current meshes and installed Bambu presets."""

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
sys.path.insert(0, str(HERE.parent/'funnel-mold-print'))
from prepare_print import (CORE, PROD, REL, fresh_settings, mesh_object, metadata,
                           preset_bundle, qn)


def choice(value, reason):
    return {'value': value, 'reason': reason}


def recipe(info):
    return {
        'system_presets': {
            'machine': 'Bambu Lab H2C 0.8 nozzle',
            'process': '0.40mm Standard @BBL H2C 0.8 nozzle',
            'filament': 'Bambu PETG Translucent @BBL H2C 0.8 nozzle'},
        'process_name': 'Funnel mold solid - 0.16 mm faces - 0.40 mm backing',
        'filament_name': 'Funnel mold PETG Translucent - HF 255C 18mm3s',
        'z_trim': {'default_mm': 0.04, 'available_mm': [0.04, 0.18],
            'reason': 'The user has established both build-plate corrections across materials and nozzles; translucent uses +0.04 mm.'},
        'process_settings': {
            'enable_arc_fitting': choice('0', 'Connected H2C firmware uses curve planning.'),
            'wall_generator': choice('arachne', 'Variable-width perimeter paths at the rod socket and coating step.'),
            'wall_loops': choice('4', 'Four perimeter paths around continuous solid backing.'),
            'sparse_infill_density': choice('100%', 'All modeled stock is solid; no designed enclosed infill volume.'),
            'sparse_infill_pattern': choice('zig-zag', 'Alternating solid infill paths.'),
            'top_shell_layers': choice('8', 'Solid surface layer classification.'),
            'bottom_shell_layers': choice('8', 'Solid surface layer classification.'),
            'top_shell_thickness': choice('3.2', 'Solid surface classification through fine layer bands.'),
            'bottom_shell_thickness': choice('3.2', 'Solid surface classification through fine layer bands.'),
            'top_one_wall_type': choice('not apply', 'Full perimeter count at forming edges.'),
            'outer_wall_speed': choice(['60']*4, 'Finishing and registration surfaces print at 60 mm/s or below the flow cap.'),
            'outer_wall_acceleration': choice(['2000']*4, 'Acceleration of the forming and locating perimeters.'),
            'top_surface_speed': choice(['60']*4, 'Flat forming surfaces print at 60 mm/s or below the flow cap.'),
            'seam_gap': choice('0%', 'Closed seam paths on the forming faces.'),
            'brim_type': choice('no_brim', 'The user specifies permanent bed-contact geometry.'),
            'brim_width': choice('0', 'No slicer brim.'),
            'skirt_loops': choice('0', 'The stock machine sequence primes the nozzle.'),
            'enable_support': choice('0', 'The solid backing carries the forming faces; the external taper is at least 45 degrees.'),
            'enable_prime_tower': choice('0', 'One filament and nozzle per plate.')},
        'filament_settings': {
            'filament_prime_volume': choice(['45'], 'Saved filament preset prime volume.'),
            'nozzle_temperature': choice(['255', '255'], 'Current translucent PETG high-flow temperature.'),
            'nozzle_temperature_initial_layer': choice(['255', '255'], 'Current translucent PETG high-flow temperature.'),
            'filament_max_volumetric_speed': choice(['16', '18'], 'Standard preset 16 mm3/s; user high-flow target 18 mm3/s.'),
            'filament_cost': choice(['11.20'], 'Ledger cost per kilogram.')},
        'layer_ranges_mm': {
            'cavity': [(7, 9), (19, 21), (31, 53),
                       (info['parting_z_mm']-7, info['parting_z_mm']+0.1)],
            'core': [(8, 16.2), (21, 23), (30, info['dimensions_mm']['core'][2]+0.1)]}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--z-trim', type=float, choices=(0.04, 0.18), default=0.04)
    parser.add_argument('--label')
    args = parser.parse_args()
    info = json.loads((args.models/'design.json').read_text())
    settings_recipe = recipe(info)
    presets = Path('/Applications/BambuStudio.app/Contents/Resources/profiles/BBL')
    settings, provenance = fresh_settings(presets, settings_recipe, args.z_trim)
    version = plistlib.loads((presets.parents[2]/'Info.plist').read_bytes())['CFBundleShortVersionString']
    data = {'Metadata/project_settings.config': json.dumps(settings, indent=2).encode()}
    model = ET.Element(qn('model'), unit='millimeter', requiredextensions='p',
        **{'xmlns:BambuStudio': 'http://schemas.bambulab.com/package/2021'})
    ET.SubElement(model, qn('metadata'), name='Application').text = f'BambuStudio-{version}'
    ET.SubElement(model, qn('metadata'), name='BambuStudio:3mfVersion').text = '1'
    ET.SubElement(model, qn('metadata'), name='Title').text = args.label or 'Funnel mold - solid cavity and core'
    resources = ET.SubElement(model, qn('resources'))
    build = ET.SubElement(model, qn('build'), **{f'{{{PROD}}}UUID': str(uuid.uuid4())})
    config = ET.Element('config')
    ranges = ET.Element('objects')
    rels = ET.Element(f'{{{REL}}}Relationships')
    assembled = ET.Element('assemble')
    provenance['mesh_sha256'] = {}
    for index, name in enumerate(('cavity', 'core'), 1):
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
        metadata(obj, 'name', f"{args.label or 'Solid funnel mold'} {name}")
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
        for key, value in {'plater_id': index, 'plater_name': f"{args.label or 'Solid'} {name}", 'locked': 'false',
                'filament_map_mode': 'Manual', 'filament_maps': '1', 'filament_volume_maps': '1',
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
    preset_bundle(presets, settings_recipe, version, args.output.parent/'solid-mold-presets.bbscfg')
    print(args.output)


if __name__ == '__main__':
    main()
