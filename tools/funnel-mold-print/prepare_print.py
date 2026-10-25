"""Prepare funnel-mold plates from current meshes and installed Bambu presets."""

import argparse
import hashlib
import json
import plistlib
import subprocess
import sys
import uuid
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

import trimesh

HERE = Path(__file__).resolve().parent
STUDIO = '/Applications/BambuStudio.app/Contents/MacOS/BambuStudio'
from profiles import (CORE, PROD, REL, equivalent, fresh_settings, mesh_object, metadata,
                           preset_bundle, qn)


def choice(value, reason):
    return {'value': value, 'reason': reason}


def recipe(info, nozzle=0.4):
    if nozzle == 0.4:
        return mold_recipe()
    return gentle_recipe()


def mold_recipe():
    """The README's recipe: stock 0.24 mm H2C process and PETG Translucent on the right 0.4 mm
    Standard hotend, with the October 6 Mark1 cavity retry's changes (task 1315124888, whose
    cavity completed; print-log.md)."""
    log = 'zone-c/funnel-mold/print-log.md'
    retry = 'the October 6 Mark1 cavity retry (native-slice-reviews/2026-10-06-mark1-retry-z004-v2)'
    return {
        'nozzle_mm': 0.4, 'nozzle_type': 'Standard', 'side': 'right',
        'system_presets': {
            'machine': 'Bambu Lab H2C 0.4 nozzle',
            'process': '0.24mm Standard @BBL H2C',
            'filament': 'Bambu PETG Translucent @BBL H2C 0.4 nozzle'},
        'process_name': 'Funnel mold - six walls - 15% gyroid - PETG088',
        'filament_name': 'Funnel mold PETG Translucent - 0.4 Standard - flow 0.88',
        'z_trim': {'default_mm': 0.04, 'available_mm': [0.04, 0.18],
            'reason': f"Derek's +0.04 mm for {retry}; the October 7 core used the same ({log})."},
        'process_settings': {
            'wall_loops': choice('6', 'Six walls: continuous forming and dry-back perimeters (README).'),
            'top_shell_layers': choice('6', 'Six top layers (README).'),
            'bottom_shell_layers': choice('6', 'Six bottom layers; dry-side breathers are drilled after printing (README).'),
            'sparse_infill_density': choice('15%', f'15% gyroid; the September 16 15% cavity worked well ({log}).'),
            'sparse_infill_pattern': choice('gyroid', 'Three-dimensional infill without crossings within a layer (README).'),
            'skeleton_infill_density': choice('100%', f'As {retry}.'),
            'skin_infill_density': choice('100%', f'As {retry}.'),
            'initial_layer_speed': choice(['20']*5, '20 mm/s first-layer walls (README).'),
            'initial_layer_infill_speed': choice(['30']*5, '30 mm/s first-layer solid infill (README).'),
            'brim_type': choice('outer_only', 'Outer brim (README).'),
            'brim_width': choice('8', '8 mm outer brim (README).'),
            'brim_object_gap': choice('0.1', f'0.10 mm brim gap, as {retry}.'),
            'enable_support': choice('1', "Removable support under the eight bolt pockets' flat washer-bearing ceilings (README)."),
            'support_type': choice('normal(auto)', 'Snug normal supports for the bolt pockets (README): tall tree '
                f'supports detached or were knocked over on September 14, and Snug columns stood on September 16 and on October 6 ({log}).'),
            'support_style': choice('snug', 'Snug normal supports for the bolt pockets (README).'),
            'support_object_xy_distance': choice('0.48', f'0.48 mm XY gap, as {retry}.'),
            'support_object_first_layer_gap': choice('0.48', f'As {retry}.'),
            'enable_prime_tower': choice('0', 'One filament per plate.')},
        'filament_settings': {
            'filament_flow_ratio': choice(['0.88', '0.97', '0.97'],
                f'0.88 flow on the Standard nozzle; the September 18 cavity at 0.88 reduced the overflow defect ({log}).'),
            'filament_max_volumetric_speed': choice(['5.61702', '6', '6'],
                f'5.61702 mm3/s on the Standard nozzle with the 0.88 flow ({log}, September 18).'),
            'filament_cost': choice(['11.20'], 'Ledger cost per kilogram.')},
        'layer_ranges_mm': {'cavity': [], 'core': []}}


def gentle_recipe():
    """The September 14 left 0.8 mm High Flow trial recipe (print-log.md, 0.40 mm support trial)."""
    return {
        'nozzle_mm': 0.8, 'nozzle_type': 'High Flow', 'side': 'left',
        'system_presets': {
            'machine': 'Bambu Lab H2C 0.8 nozzle',
            'process': '0.40mm Standard @BBL H2C 0.8 nozzle',
            'filament': 'Bambu PETG Translucent @BBL H2C 0.8 nozzle'},
        'process_name': 'Funnel mold shell - 0.8 nozzle - 0.40 mm gentle supports',
        'filament_name': 'Funnel mold PETG Translucent - 0.8 nozzle - Bambu defaults',
        'z_trim': {'default_mm': 0.18, 'available_mm': [0.04, 0.18],
            'reason': 'User-established PET-GF plate corrections; transfer to PETG is not established.'},
        'process_settings': {
            'enable_arc_fitting': choice('0', 'Connected H2C firmware uses curve planning.'),
            'layer_height': choice('0.4', 'Stock 0.8 mm nozzle layer height; finish the forming slopes before casting.'),
            'initial_layer_print_height': choice('0.4', 'Stock nozzle first-layer height.'),
            'wall_generator': choice('arachne', 'Variable-width paths around sockets and shell transitions.'),
            'wall_loops': choice('6', 'Continuous forming and dry-back perimeters.'),
            'sparse_infill_density': choice('15%', 'Sparse interior with continuous forming skins.'),
            'sparse_infill_pattern': choice('gyroid', 'Three-dimensional infill without crossings within a layer.'),
            'top_shell_layers': choice('6', 'Closed forming skins.'),
            'bottom_shell_layers': choice('6', 'Closed bed skins; dry-side breathers are drilled after printing.'),
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
            'brim_type': choice('outer_only', 'Removable adhesion brim around the model feet and flange.'),
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
            'enable_prime_tower': choice('0', 'One filament per plate.'),
            'raft_first_layer_expansion': choice('8', 'Broad connected support feet on the build plate.'),
            'support_speed': choice(['40']*4, 'Tall tree extrusion capped at 40 mm/s.'),
            'support_interface_speed': choice(['30']*4, 'Support interfaces capped at 30 mm/s.'),
            'travel_speed': choice(['150']*4, 'Travel moves capped at 150 mm/s.'),
            'default_acceleration': choice(['1500']*4, 'Normal printing, including tree walls, at 1500 mm/s2.'),
            'travel_acceleration': choice(['1500']*4, 'Travel acceleration at 1500 mm/s2.'),
            'avoid_crossing_wall_includes_support': choice('1', 'Support walls participate in travel detours.'),
            'tree_support_wall_count': choice('2', 'Two perimeter loops around tree branches.'),
            'tree_support_branch_diameter': choice('4', 'Tree nodes start at 4 mm diameter.')},
        'filament_settings': {
            'filament_cost': choice(['11.20'], 'Ledger cost per kilogram.')},
        'layer_ranges_mm': {'cavity': [], 'core': []}}


def bed_centre(settings, side):
    """Centre of the selected hotend's printable area, the plate's model centre."""
    area = settings['extruder_printable_area'][{'left': 0, 'right': 1}[side]]
    points = [[float(v) for v in point.split('x')] for point in area.split(',')]
    xs, ys = zip(*points)
    return (min(xs)+max(xs))/2, (min(ys)+max(ys))/2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--z-trim', type=float, choices=(0.04, 0.18),
                        help="Requested Z trim; default is the recipe's (+0.04 for the 0.4 mm recipe).")
    parser.add_argument('--label')
    parser.add_argument('--nozzle', type=float, choices=(0.4, 0.8), default=0.4)
    parser.add_argument('--only', choices=('cavity', 'core'))
    parser.add_argument('--settings-from', type=Path,
                        help='Preserve the complete settings payload from this saved 3MF.')
    parser.add_argument('--slice', action='store_true',
                        help='Slice the project with the installed Bambu Studio command line into native/ beside it.')
    args = parser.parse_args()
    info = json.loads((args.models/'design.json').read_text())
    settings_recipe = recipe(info, args.nozzle)
    presets = Path('/Applications/BambuStudio.app/Contents/Resources/profiles/BBL')
    if args.z_trim is None:
        args.z_trim = settings_recipe['z_trim']['default_mm']
    settings, provenance = fresh_settings(presets, settings_recipe, args.z_trim)
    settings_payload = json.dumps(settings, indent=2).encode()
    if args.settings_from:
        source_sha256 = hashlib.sha256(args.settings_from.read_bytes()).hexdigest()
        with zipfile.ZipFile(args.settings_from) as archive:
            assert archive.testzip() is None
            settings_payload = archive.read('Metadata/project_settings.config')
        preserved = json.loads(settings_payload)
        for group in ('process_settings', 'filament_settings'):
            for key, expected in settings_recipe[group].items():
                assert equivalent(key, expected['value'], preserved[key]), (key, preserved[key])
        for key in ('printer_settings_id', 'print_settings_id', 'filament_settings_id',
                    'machine_start_gcode', 'curr_bed_type', 'nozzle_diameter',
                    'nozzle_volume_type', 'filament_volume_map'):
            assert equivalent(key, settings[key], preserved[key]), (key, preserved[key])
        settings = preserved
        source = {'project': args.settings_from.name, 'project_sha256': source_sha256}
        provenance['settings_source'] = {
            **source, 'settings_sha256': hashlib.sha256(settings_payload).hexdigest()}
        provenance['supplied_settings'] = {
            key: {'value': value, **source} for key, value in settings.items()}
    version = plistlib.loads((presets.parents[2]/'Info.plist').read_bytes())['CFBundleShortVersionString']
    centre_x, centre_y = bed_centre(settings, settings_recipe['side'])
    side_map = {'left': '1', 'right': '2'}[settings_recipe['side']]
    assert settings['filament_map'] == [side_map], (settings['filament_map'], side_map)
    data = {'Metadata/project_settings.config': settings_payload}
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
        transform = f'{rotation} {centre_x+(index-1)*396:g} {centre_y:g} {height/2:.9f}'
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
                'filament_map_mode': 'Manual', 'filament_maps': side_map,
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
    if args.slice:
        slice_project(args.output.resolve())


def slice_project(project):
    """Native slice of every plate; prints each plate's estimate. Nothing is sent to a printer."""
    native = project.parent/'native'
    native.mkdir(exist_ok=True)
    archive = native/project.name.replace('.3mf', '.gcode.3mf')
    with (native/'slice.log').open('w') as log:
        code = subprocess.run([STUDIO, '--slice', '0', '--arrange', '0', '--orient', '0',
                               '--outputdir', str(native), '--export-3mf', archive.name, str(project)],
                              cwd=native, stdout=log, stderr=subprocess.STDOUT).returncode
    result = json.loads((native/'result.json').read_text()) if (native/'result.json').is_file() else {}
    if code or result.get('return_code') != 0:
        raise SystemExit(f"slice failed ({code}): {result.get('error_string')}; see {native/'slice.log'}")
    for plate in result['sliced_plates']:
        grams = sum(f['total_used_g'] for f in plate['filaments'])
        print(f"plate {plate['id']}: {plate['total_predication']/3600:.1f} h, {grams:.0f} g")
    print(archive)


if __name__ == '__main__':
    main()
