"""Prepare and slice separate ASA Aero cores and PETG envelopes for the H2C."""

import argparse
import hashlib
import json
import plistlib
import shutil
import subprocess
import sys
import uuid
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
import trimesh

import magnetic_float as m

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/funnel-mold-print/profiles.py').is_file())
sys.path.append(str(ROOT / 'tools/funnel-mold-print'))
from profiles import PROD, REL, qn, metadata, mesh_object, system_preset

PRESETS = Path('/Applications/BambuStudio.app/Contents/Resources/profiles/BBL')
STUDIO = PRESETS.parents[2] / 'MacOS/BambuStudio'
PAUSE_MESSAGE = ('Seat the cooled ASA Aero core on the floor. Seat one RC62 in its pocket. '
                 'Press the ASA Aero insert flush with the PETG rim. Clear loose strings '
                 'and resume with both Aero pieces fully seated.')
JOBS = {
    'aero': {'filename': 'magnetic-float-aero.3mf', 'nozzle': 0.4, 'side': 2,
             'filament': 'Bambu ASA-Aero @BBL H2C 0.4 nozzle',
             'bed': 'Engineering Plate', 'parts': ['body-aero', 'insert-aero']},
    'petg': {'filename': 'magnetic-float.3mf', 'nozzle': 0.6, 'side': 1,
             'filament': 'Bambu PETG Basic @BBL H2C',
             'bed': 'Textured PEI Plate', 'parts': ['body-petg']},
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def uid(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'homesodamachine/magnetic-float/' + name))


def set_value(settings, key, value):
    previous = settings.get(key)
    settings[key] = [str(value)] * len(previous) if isinstance(previous, list) else str(value)


def recipe(key):
    job = JOBS[key]
    aero = key == 'aero'
    nozzle = job['nozzle']
    layer = 0.2 if aero else m.petg_layer
    machine_name = f'Bambu Lab H2C {nozzle:g} nozzle'
    process_name = ('0.20mm Standard @BBL H2C' if nozzle == 0.4
                    else '0.18mm Balanced Quality @BBL H2C 0.6 nozzle')
    files = {}
    machine, _, _ = system_preset(PRESETS, 'machine', machine_name, files)
    process, _, _ = system_preset(PRESETS, 'process', process_name, files)
    filament, _, ids = system_preset(PRESETS, 'filament', job['filament'], files)
    changes = {
        'layer_height': layer, 'initial_layer_print_height': layer if aero else m.petg_first_layer,
        'wall_generator': 'arachne', 'wall_loops': 3 if aero else 6,
        'sparse_infill_density': '100%', 'sparse_infill_pattern': 'zig-zag',
        'top_shell_layers': 5 if aero else round(m.roof / layer),
        'bottom_shell_layers': 5 if aero else 1 + round((m.floor - m.petg_first_layer) / layer),
        'top_shell_thickness': 1 if aero else m.roof, 'bottom_shell_thickness': 1 if aero else m.floor,
        'enable_support': 0, 'enable_prime_tower': 0,
        'seam_gap': '0%', 'seam_position': 'back',
        'brim_type': 'outer_only', 'brim_width': 3 if aero else 4,
        'brim_object_gap': 0.2 if aero else 0.15,
        'skirt_loops': 0, 'enable_arc_fitting': 0,
        'print_sequence': 'by layer', 'reduce_crossing_wall': 1,
        'flush_into_infill': 0, 'flush_into_objects': 0, 'flush_into_support': 0,
    }
    if aero:
        changes.update({name: 0.48 for name in (
            'line_width', 'initial_layer_line_width', 'outer_wall_line_width',
            'inner_wall_line_width', 'top_surface_line_width', 'sparse_infill_line_width',
            'internal_solid_infill_line_width')})
        changes.update({name: 80 for name in (
            'outer_wall_speed', 'inner_wall_speed', 'sparse_infill_speed',
            'internal_solid_infill_speed', 'top_surface_speed', 'gap_infill_speed')})
        changes.update({'default_acceleration': 5000, 'outer_wall_acceleration': 3000,
                        'slice_closing_radius': 0.02, 'bridge_flow': 0.7})
    else:
        water = json.loads((HERE / 'petg-water-recipe.json').read_text())
        changes.update(water['process'])
        changes.update({'outer_wall_speed': 40, 'inner_wall_speed': 60,
                        'internal_solid_infill_speed': 60, 'sparse_infill_speed': 60,
                        'top_surface_speed': 30, 'bridge_speed': 20, 'internal_bridge_speed': '100%',
                        'bridge_flow': 1, 'internal_bridge_flow': 1,
                        'seam_gap': '0%', 'seam_slope_conditional': 0})
    for name, value in changes.items():
        set_value(process, name, value)
    machine_changes = {'nozzle_volume_type': ['Standard', 'Standard'],
                       'default_nozzle_volume_type': ['Standard', 'Standard'],
                       'nozzle_diameter': ['0.6', '0.4'],
                       'max_layer_height': ['0.42', '0.28'],
                       'min_layer_height': ['0.12', '0.08']}
    machine.update(machine_changes)
    filament_changes = {} if aero else {**water['filament'], 'overhang_fan_speed': ['20']}
    filament.update(filament_changes)
    settings = {**machine, **process}
    for name, value in filament.items():
        settings[name] = [value[0]] if isinstance(value, list) else value
    settings.update({
        'printer_settings_id': machine_name, 'name': f'Magnetic float {key}',
        'print_settings_id': f'Magnetic float {key}',
        'filament_settings_id': [job['filament']], 'filament_ids': [ids['filament_id']],
        'filament_colour': ['#F5F1DD' if aero else '#000000'],
        'inherits_group': [process_name, job['filament'], machine_name],
        'different_settings_to_system': [';'.join(changes), ';'.join(filament_changes), ';'.join(machine_changes)],
        'filament_map_mode': 'Manual', 'filament_map': [str(job['side'])],
        'filament_map_2': [str(job['side'])], 'filament_nozzle_map': [str(job['side'] - 1)],
        'filament_self_index': ['1'], 'filament_volume_map': ['0'],
        'nozzle_volume_type': ['Standard', 'Standard'],
        'extruder_nozzle_stats': ['Standard#1', 'Standard#1'],
        'extruder_nozzle_stats_new': ['Standard#1', 'Standard#1'],
        'curr_bed_type': job['bed'], 'print_compatible_printers': [machine_name],
    })
    version = plistlib.loads((PRESETS.parents[2] / 'Info.plist').read_bytes())['CFBundleShortVersionString']
    return settings, filament, {
        'slicer_version': version, 'system_presets_sha256': files,
        'process_changes': changes, 'machine_changes': machine_changes,
        'filament_changes': filament_changes, 'filament_preset': job['filament'],
        'petg_recipe_sha256': None if aero else sha(HERE / 'petg-water-recipe.json'),
        'filament_id': ids['filament_id'], 'active_nozzle_mm': nozzle,
        'active_side': 'left' if job['side'] == 1 else 'right',
        'bed': job['bed'], 'layer_height_mm': layer,
        'first_layer_height_mm': layer if aero else m.petg_first_layer,
        'pause_before_z_mm': None if aero else m.roof_bottom + layer,
        'geometry_sha256': sha(HERE / 'design.json'),
    }


def project(destination, key):
    job = JOBS[key]
    aero = key == 'aero'
    destination.mkdir(parents=True, exist_ok=True)
    settings, filament, provenance = recipe(key)
    model = ET.Element(qn('model'), unit='millimeter', requiredextensions='p',
                       **{'xmlns:BambuStudio': 'http://schemas.bambulab.com/package/2021'})
    ET.SubElement(model, qn('metadata'), name='Application').text = 'BambuStudio-' + provenance['slicer_version']
    ET.SubElement(model, qn('metadata'), name='BambuStudio:3mfVersion').text = '1'
    ET.SubElement(model, qn('metadata'), name='Title').text = f'RC62 magnetic float - {key}'
    resources = ET.SubElement(model, qn('resources'))
    build = ET.SubElement(model, qn('build'), **{f'{{{PROD}}}UUID': uid(key + '/build')})
    config = ET.Element('config')
    rels = ET.Element(f'{{{REL}}}Relationships')
    package_rels = ET.Element(f'{{{REL}}}Relationships')
    ET.SubElement(package_rels, f'{{{REL}}}Relationship', Target='/3D/3dmodel.model', Id='rel-1',
                  Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
    data = {'Metadata/project_settings.config': json.dumps(settings, indent=2).encode(),
            'Metadata/filament_settings_1.config': json.dumps({**filament,
                'name': job['filament'], 'filament_id': provenance['filament_id']}, indent=2).encode()}
    provenance['meshes_sha256'] = {}
    provenance['objects'] = []
    for number, name in enumerate(job['parts'], 1):
        label = {'body-aero': 'ASA Aero core', 'insert-aero': 'ASA Aero insert',
                 'body-petg': 'PETG envelope - insert core and magnet at pause'}[name]
        plate = ET.SubElement(config, 'plate')
        for attr, value in {'plater_id': number, 'plater_name': label,
                           'locked': 'false', 'bed_type': job['bed'], 'filament_map_mode': 'Manual',
                           'filament_maps': str(job['side']), 'filament_volume_maps': '0'}.items():
            metadata(plate, attr, value)
        path = f'/3D/Objects/object_{number}.model'
        mesh_path = HERE / f'{name}.stl'
        mesh = trimesh.load(mesh_path, force='mesh', process=True)
        mesh.apply_translation((0, 0, -mesh.bounds[0, 2]))
        height = float(mesh.bounds[1, 2])
        parent_id, part_id = number * 10, number * 10 + 1
        sub = ET.Element(qn('model'), unit='millimeter')
        subresources = ET.SubElement(sub, qn('resources'))
        mesh_object(subresources, part_id, mesh, np.array([0, 0, height / 2]))
        parent = ET.SubElement(resources, qn('object'), id=str(parent_id), type='model',
                               **{f'{{{PROD}}}UUID': uid(key + '/' + name)})
        components = ET.SubElement(parent, qn('components'))
        ET.SubElement(components, qn('component'), objectid=str(part_id),
                      transform='1 0 0 0 1 0 0 0 1 0 0 0',
                      **{f'{{{PROD}}}path': path, f'{{{PROD}}}UUID': uid(name)})
        record = ET.SubElement(config, 'object', id=str(parent_id))
        metadata(record, 'name', label)
        metadata(record, 'extruder', 1)
        allowance = None
        if aero:
            allowance = m.core_fit_allowance if name == 'body-aero' else m.insert_fit_allowance
            metadata(record, 'xy_contour_compensation', allowance)
            metadata(record, 'xy_hole_compensation', -allowance)
        part = ET.SubElement(record, 'part', id=str(part_id), subtype='normal_part')
        for attr, value in {'name': name, 'extruder': 1,
                           'matrix': '1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1',
                           'source_file': mesh_path.name, 'source_object_id': 0,
                           'source_volume_id': 0, 'source_offset_x': 0,
                           'source_offset_y': 0, 'source_offset_z': height / 2}.items():
            metadata(part, attr, value)
        ET.SubElement(part, 'mesh_stat', face_count=str(len(mesh.faces)), edges_fixed='0',
                      degenerate_facets='0', facets_removed='0', facets_reversed='0', backwards_edges='0')
        ET.SubElement(build, qn('item'), objectid=str(parent_id), printable='1',
                      transform=f'1 0 0 0 1 0 0 0 1 {150 + (number - 1) * 396} 145 {height / 2}')
        instance = ET.SubElement(plate, 'model_instance')
        for attr, value in {'object_id': parent_id, 'instance_id': 0,
                           'identify_id': 4600 + number}.items():
            metadata(instance, attr, value)
        ET.SubElement(rels, f'{{{REL}}}Relationship', Target=path, Id=f'rel-{number}',
                      Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
        data[path.lstrip('/')] = ET.tostring(sub, xml_declaration=True, encoding='UTF-8')
        provenance['meshes_sha256'][name] = sha(mesh_path)
        provenance['objects'].append({'part': name, 'plate': number, 'print_height_mm': height,
                                      'fit_allowance_radial_mm': allowance})
    pauses = ET.Element('custom_gcodes_per_layer')
    if not aero:
        plate = ET.SubElement(pauses, 'plate')
        ET.SubElement(plate, 'plate_info', id='1')
        ET.SubElement(plate, 'layer', top_z=str(provenance['pause_before_z_mm']), type='1', extruder='1',
                      color='', extra=PAUSE_MESSAGE, gcode='M400 U1')
        ET.SubElement(plate, 'mode', value='SingleExtruder')
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
    output = destination / f'{key}-input.3mf'
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, payload in data.items():
            entry = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, payload)
    (destination / f'{key}-provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    return output


def slice_projects(destination):
    for key, job in JOBS.items():
        output = destination / key
        output.mkdir(parents=True, exist_ok=True)
        with (destination / f'{key}-slice.log').open('w') as log:
            subprocess.run([str(STUDIO), '--arrange', '0', '--orient', '0', '--slice', '0',
                            '--export-3mf', job['filename'], '--outputdir', str(output),
                            str(destination / f'{key}-input.3mf')],
                           cwd=output, stdout=log, stderr=subprocess.STDOUT, check=True)
        print(f'Sliced {job["filename"]}', flush=True)
    import verify
    report, profile = verify.verify_directory(destination)
    for key, job in JOBS.items():
        shutil.copy2(destination / key / job['filename'], HERE / job['filename'])
    (HERE / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    (HERE / 'print-profile.json').write_text(json.dumps(profile, indent=2) + '\n')
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '.cache/magnetic-float-print')
    parser.add_argument('--slice', action='store_true', help='Slice, verify and save both print projects.')
    args = parser.parse_args()
    destination = args.output.resolve()
    for key in JOBS:
        print(project(destination, key), flush=True)
    if args.slice:
        slice_projects(destination)
