"""Prepare the H2C magnetic-float project from its meshes and installed presets."""

import argparse
import hashlib
import json
import plistlib
import sys
import uuid
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/funnel-mold-print/profiles.py').is_file())
sys.path.insert(0, str(ROOT / 'tools/funnel-mold-print'))
from profiles import CORE, PROD, REL, qn, metadata, mesh_object, system_preset

PRESETS = Path('/Applications/BambuStudio.app/Contents/Resources/profiles/BBL')
LAYER = 0.2
MACHINE = 'Bambu Lab H2C 0.4 nozzle'
PROCESS = '0.20mm Standard @BBL H2C'
FILAMENTS = ('Bambu PETG Translucent @BBL H2C 0.4 nozzle',
             'Bambu PLA Aero @BBL H2C 0.4 nozzle')
NAMES = ('Float PETG Translucent 250C', 'Float PLA Aero 250C 0.38 flow')
PAUSE_MESSAGE = 'Seat one RC62 magnet. Press the Aero insert flush with the rim. Use the snugger spare if loose. Resume with the insert staying seated.'


def uid(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'homesodamachine/magnetic-float/' + name))


def set_value(settings, key, value):
    previous = settings.get(key)
    settings[key] = [str(value)] * len(previous) if isinstance(previous, list) else str(value)


def recipe(destination):
    files = {}
    version = plistlib.loads((PRESETS.parents[2] / 'Info.plist').read_bytes())['CFBundleShortVersionString']
    machine, _, _ = system_preset(PRESETS, 'machine', MACHINE, files)
    process, _, _ = system_preset(PRESETS, 'process', PROCESS, files)
    process_changes = {
        'layer_height': LAYER, 'initial_layer_print_height': LAYER,
        'wall_generator': 'arachne', 'wall_loops': 3,
        'sparse_infill_density': '100%', 'sparse_infill_pattern': 'zig-zag',
        'top_shell_layers': 5, 'bottom_shell_layers': 5,
        'top_shell_thickness': 1, 'bottom_shell_thickness': 1,
        'outer_wall_speed': 40, 'inner_wall_speed': 60,
        'internal_solid_infill_speed': 80, 'top_surface_speed': 30,
        'initial_layer_speed': 20, 'initial_layer_infill_speed': 30,
        'bridge_speed': 20, 'bridge_flow': 1, 'internal_bridge_flow': 1,
        'enable_support': 0, 'enable_prime_tower': 1,
        'prime_tower_width': 35, 'seam_gap': '0%', 'seam_position': 'back',
        'brim_type': 'outer_only', 'brim_width': 4, 'brim_object_gap': 0.15,
        'skirt_loops': 0, 'enable_arc_fitting': 0, 'print_sequence': 'by layer',
        'flush_into_infill': 0, 'flush_into_objects': 0, 'flush_into_support': 0,
        'detect_thin_wall': 0, 'reduce_crossing_wall': 1,
    }
    for key, value in process_changes.items():
        set_value(process, key, value)
    machine.update({'printer_settings_id': MACHINE, 'name': MACHINE,
                    'nozzle_volume_type': ['Standard', 'Standard'],
                    'default_nozzle_volume_type': ['Standard', 'Standard']})
    process.update({'print_settings_id': 'Magnetic float 1mm PETG 50mm',
                    'name': 'Magnetic float 1mm PETG 50mm',
                    'compatible_printers': [MACHINE]})
    filaments = []
    for index, name in enumerate(FILAMENTS):
        values, _, ids = system_preset(PRESETS, 'filament', name, files)
        changes = {'nozzle_temperature': 250, 'nozzle_temperature_initial_layer': 250,
                   'textured_plate_temp': 65, 'textured_plate_temp_initial_layer': 65,
                   'filament_max_volumetric_speed': 6, 'additional_cooling_fan_speed': 0}
        if index == 1:
            changes['filament_flow_ratio'] = 0.38
        else:
            changes.update({'overhang_fan_speed': 40, 'overhang_fan_threshold': '25%'})
        for key, value in changes.items():
            set_value(values, key, value)
        values.update({'name': NAMES[index], 'filament_settings_id': [NAMES[index]],
                       'filament_id': ids['filament_id'], 'compatible_printers': [MACHINE],
                       'filament_colour': ['#45A9CA' if index == 0 else '#EBC777']})
        filaments.append(values)
    settings = {**machine, **process}
    for key in set(filaments[0]) | set(filaments[1]):
        if key in ('name', 'compatible_printers', 'filament_id'):
            continue
        values = [f.get(key) for f in filaments]
        if all(isinstance(v, list) for v in values):
            settings[key] = [v[0] for v in values]
        elif values[0] is not None:
            settings[key] = values[0]
    settings.update({
        'filament_settings_id': list(NAMES), 'filament_ids': ['GFG01', 'GFA11'],
        'inherits_group': [PROCESS, *FILAMENTS, MACHINE],
        'different_settings_to_system': [';'.join(process_changes), '', '', ''],
        'filament_map_mode': 'Manual', 'filament_map': ['1', '2'],
        'filament_map_2': ['1', '2'], 'filament_nozzle_map': ['0', '1'],
        'filament_volume_map': ['0', '0'], 'filament_self_index': ['1', '2'],
        'nozzle_volume_type': ['Standard', 'Standard'],
        'extruder_nozzle_stats': ['Standard#1', 'Standard#1'],
        'extruder_nozzle_stats_new': ['Standard#1', 'Standard#1'],
        'curr_bed_type': 'Textured PEI Plate',
        'wipe_tower_x': ['220', '220'], 'wipe_tower_y': ['200', '200'],
        'print_compatible_printers': [MACHINE],
    })
    for name, values in [('machine', machine), ('process', process),
                         ('petg', filaments[0]), ('aero', filaments[1])]:
        values.update({'type': name if name in ('machine', 'process') else 'filament',
                       'from': 'User', 'version': version, 'instantiation': 'true'})
        (destination / f'{name}.json').write_text(json.dumps(values, indent=2) + '\n')
    return settings, filaments, {'system_presets_sha256': files,
        'process_changes': process_changes, 'aero_source':
        'https://bambulab-eu.myshopify.com/nl-nl/products/pla-aero',
        'aero_reference': {'temperature_c': 250, 'flow_ratio': 0.38,
            'manufacturer_specimen_minimum_density_g_cc': 0.45,
            'specimen_nozzle_mm': 0.4, 'specimen_speed_mm_s': 80},
        'prepared_materials': NAMES, 'bed_c': 65, 'nozzle_mm': 0.4,
        'mapping': {'left': 'PETG Translucent Clear', 'right': 'PLA Aero'}}


def project(destination):
    destination.mkdir(parents=True, exist_ok=True)
    settings, filaments, provenance = recipe(destination)
    info = json.loads((HERE / 'design.json').read_text())
    version = plistlib.loads((PRESETS.parents[2] / 'Info.plist').read_bytes())['CFBundleShortVersionString']
    model = ET.Element(qn('model'), unit='millimeter', requiredextensions='p',
                       **{'xmlns:BambuStudio': 'http://schemas.bambulab.com/package/2021'})
    ET.SubElement(model, qn('metadata'), name='Application').text = f'BambuStudio-{version}'
    ET.SubElement(model, qn('metadata'), name='BambuStudio:3mfVersion').text = '1'
    ET.SubElement(model, qn('metadata'), name='Title').text = 'RC62 magnetic float 28 x 50 - 1mm PETG'
    resources = ET.SubElement(model, qn('resources'))
    build = ET.SubElement(model, qn('build'), **{f'{{{PROD}}}UUID': uid('build')})
    config = ET.Element('config')
    rels = ET.Element(f'{{{REL}}}Relationships')
    package_rels = ET.Element(f'{{{REL}}}Relationships')
    ET.SubElement(package_rels, f'{{{REL}}}Relationship', Target='/3D/3dmodel.model', Id='rel-1',
                  Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
    data = {'Metadata/project_settings.config': json.dumps(settings, indent=2).encode()}
    for i, filament in enumerate(filaments, 1):
        data[f'Metadata/filament_settings_{i}.config'] = json.dumps(filament, indent=2).encode()
    plates = []
    for number, title in ((1, '1 - Aero inserts'), (2, '2 - Float - insert magnet at pause')):
        plate = ET.SubElement(config, 'plate')
        for key, value in {'plater_id': number, 'plater_name': title, 'locked': 'false',
                           'bed_type': 'Textured PEI Plate', 'filament_map_mode': 'Manual',
                           'filament_maps': '1 2', 'filament_volume_maps': '0 0'}.items():
            metadata(plate, key, value)
        plates.append(plate)
    objects = [
        ('Insert', ['insert-aero'], 0, 115, 145),
        ('Spare insert - snugger fit', ['insert-aero'], 0, 155, 145),
        ('Float body', ['body-petg', 'body-aero'], 1, 150, 145),
    ]
    provenance['meshes_sha256'] = {}
    for index, (label, names, plate_index, x, y) in enumerate(objects, 1):
        meshes = {name: trimesh.load(HERE / f'{name}.stl', force='mesh', process=True) for name in names}
        h = max(mesh.bounds[1, 2] for mesh in meshes.values())
        parent_id = index * 10
        path = f'/3D/Objects/object_{index}.model'
        sub = ET.Element(qn('model'), unit='millimeter')
        subresources = ET.SubElement(sub, qn('resources'))
        parent = ET.SubElement(resources, qn('object'), id=str(parent_id), type='model',
                               **{f'{{{PROD}}}UUID': uid(label)})
        components = ET.SubElement(parent, qn('components'))
        record = ET.SubElement(config, 'object', id=str(parent_id))
        metadata(record, 'name', label)
        metadata(record, 'extruder', 2 if plate_index == 0 else 1)
        if plate_index == 0:
            allowance = info['insert_print_fit_allowances_radial_mm'][index - 1]
            metadata(record, 'xy_contour_compensation', allowance)
            metadata(record, 'xy_hole_compensation', -allowance)
        center = np.array([0, 0, h / 2])
        for ordinal, name in enumerate(names, 1):
            part_id = parent_id + ordinal
            mesh_path = HERE / f'{name}.stl'
            mesh = meshes[name]
            mesh_object(subresources, part_id, mesh, center)
            ET.SubElement(components, qn('component'), objectid=str(part_id),
                transform='1 0 0 0 1 0 0 0 1 0 0 0',
                **{f'{{{PROD}}}path': path, f'{{{PROD}}}UUID': uid(name)})
            part = ET.SubElement(record, 'part', id=str(part_id), subtype='normal_part')
            for key, value in {'name': name, 'extruder': 2 if name.endswith('aero') else 1,
                'matrix': '1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1', 'source_file': mesh_path.name,
                'source_object_id': 0, 'source_volume_id': ordinal - 1,
                'source_offset_x': 0, 'source_offset_y': 0, 'source_offset_z': h / 2}.items():
                metadata(part, key, value)
            ET.SubElement(part, 'mesh_stat', face_count=str(len(mesh.faces)), edges_fixed='0',
                degenerate_facets='0', facets_removed='0', facets_reversed='0', backwards_edges='0')
            provenance['meshes_sha256'][name] = hashlib.sha256(mesh_path.read_bytes()).hexdigest()
        data[path.lstrip('/')] = ET.tostring(sub, xml_declaration=True, encoding='UTF-8')
        ET.SubElement(build, qn('item'), objectid=str(parent_id), printable='1',
                      transform=f'1 0 0 0 1 0 0 0 1 {x + plate_index * 396} {y} {h / 2}')
        instance = ET.SubElement(plates[plate_index], 'model_instance')
        for key, value in {'object_id': parent_id, 'instance_id': 0, 'identify_id': 4600 + index}.items():
            metadata(instance, key, value)
        ET.SubElement(rels, f'{{{REL}}}Relationship', Target=path, Id=f'rel-{index}',
                      Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
    pauses = ET.Element('custom_gcodes_per_layer')
    plate = ET.SubElement(pauses, 'plate')
    ET.SubElement(plate, 'plate_info', id='2')
    pause_z = info['dimensions_mm']['roof_bottom'] + LAYER
    ET.SubElement(plate, 'layer', top_z=str(pause_z), type='1', extruder='1',
                  color='', extra=PAUSE_MESSAGE, gcode='M400 U1')
    ET.SubElement(plate, 'mode', value='MultiExtruder')
    for path, xml in [('3D/3dmodel.model', model), ('Metadata/model_settings.config', config),
                     ('Metadata/custom_gcode_per_layer.xml', pauses),
                     ('3D/_rels/3dmodel.model.rels', rels), ('_rels/.rels', package_rels)]:
        payload = ET.tostring(xml, xml_declaration=True, encoding='UTF-8')
        if path.endswith('.rels'):
            payload = payload.replace(b'ns0:', b'').replace(b'xmlns:ns0=', b'xmlns=')
        data[path] = payload
    data['[Content_Types].xml'] = b'''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
<Default Extension="png" ContentType="image/png"/>
<Default Extension="gcode" ContentType="text/x.gcode"/></Types>'''
    output = destination / 'magnetic-float-input.3mf'
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, payload in data.items():
            entry = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, payload)
    provenance.update({'slicer_version': version, 'pause_before_z_mm': pause_z,
                       'geometry_sha256': hashlib.sha256((HERE / 'design.json').read_bytes()).hexdigest()})
    (destination / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    print(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '.cache/magnetic-float-print')
    project(parser.parse_args().output)
