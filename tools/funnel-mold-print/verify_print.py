"""Read the saved funnel-mold projects, their settings, and their embedded G-code."""

import argparse
import hashlib
import json
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
from profiles import equivalent


def audit(project, provenance_path, models):
    origin = json.loads(provenance_path.read_text())
    recipe = origin['recipe']
    names = origin.get('parts', ['cavity', 'core'])
    with zipfile.ZipFile(project) as archive:
        assert archive.testzip() is None
        settings = json.loads(archive.read('Metadata/project_settings.config'))
        local = ET.fromstring(archive.read('Metadata/model_settings.config'))
        ranges = (ET.fromstring(archive.read('Metadata/layer_config_ranges.xml'))
                  if 'Metadata/layer_config_ranges.xml' in archive.namelist() else ET.Element('objects'))
        slices = ET.fromstring(archive.read('Metadata/slice_info.config'))
        normalized = []
        value_normalizations = []
        for key, value in settings.items():
            if key in origin['supplied_settings']:
                supplied = origin['supplied_settings'][key]['value']
                if key == 'filament_prime_volume' and supplied == ['30'] and value == ['45']:
                    value_normalizations.append({'setting': key, 'supplied': supplied,
                        'saved': value, 'scope': 'Bambu Studio 02.08.02.61 saved purge volume'})
                    continue
                assert equivalent(key, supplied, value), (key, supplied, value)
                if supplied != value:
                    normalized.append(key)
        assert settings['sparse_infill_density'] == '100%'
        assert settings['enable_support'] == '1'
        assert settings['support_type'] == 'tree(auto)'
        assert settings['enable_prime_tower'] == '0'
        assert settings['brim_type'] == 'outer_only'
        assert settings['filament_max_volumetric_speed'] == ['12', '18']
        assert settings['nozzle_temperature'] == ['255', '255']
        assert settings['curr_bed_type'] == 'Textured PEI Plate'
        assert settings['post_process'] == []
        assert settings['before_layer_change_gcode'] == ''
        assert len(local.findall('object')) == len(local.findall('plate')) == len(names)
        for obj in local.findall('object'):
            keys = {m.get('key') for m in obj.findall('metadata') if m.get('key')}
            assert keys == {'name', 'extruder'}, keys
            assert len(obj.findall('part')) == 1
            assert obj.find('part').get('subtype') == 'normal_part'
        gcode_records = []
        for index, name in enumerate(names, 1):
            digest = hashlib.sha256((models/f'{name}.stl').read_bytes()).hexdigest()
            assert digest == origin['mesh_sha256'][name], 'STL changed after preparation'
            actual = ranges.find(f"object[@id='{index}']")
            bands = [(float(b.get('min_z')), float(b.get('max_z')),
                      float(b.find('option').text)) for b in ([] if actual is None else actual.findall('range'))]
            assert bands == [(a, b, .16) for a, b in recipe['layer_ranges_mm'][name]]
            plate = local.findall('plate')[index-1]
            md = {m.get('key'): m.get('value') for m in plate.findall('metadata')}
            assert md['bed_type'] == 'Textured PEI Plate'
            assert md['filament_maps'] == '1'
            assert md['filament_volume_maps'] == ('1' if recipe['nozzle_type'] == 'High Flow' else '0')
            assert md['filament_map_mode'] == 'Manual'
            gcode_name = f'Metadata/plate_{index}.gcode'
            data = archive.read(gcode_name)
            recorded_md5 = archive.read(gcode_name+'.md5').decode().strip()
            assert hashlib.md5(data).hexdigest().lower() == recorded_md5.lower()
            assert b'; FEATURE: Support' in data, 'tree supports absent from G-code'
            assert b'; FEATURE: Skirt' not in data
            gcode_records.append({'part': name, 'stl_sha256': digest,
                'gcode_sha256': hashlib.sha256(data).hexdigest(),
                'header': data.decode().split('; HEADER_BLOCK_END')[0].splitlines()[1:]})
        for plate in slices.findall('plate'):
            assert [n.attrib for n in plate.findall('nozzle')] == [
                {'id': '0', 'extruder_id': '1', 'nozzle_diameter': f"{recipe['nozzle_mm']:g}", 'volume_type': recipe['nozzle_type']}]
    return {'project': project.name, 'sha256': hashlib.sha256(project.read_bytes()).hexdigest(),
        'effective_setting_count': len(settings), 'normalized_settings': normalized,
        'value_normalizations': value_normalizations,
        'supplied_setting_origins': origin['supplied_settings'],
        'slicer_defaults': {k: v for k, v in settings.items() if k not in origin['supplied_settings']},
        'settings': settings, 'recipe': recipe, 'gcode': gcode_records}


def geometry_figures(info):
    def dims(name):
        return ' × '.join(f'{v:.1f}'.removesuffix('.0') for v in info['dimensions_mm'][name])+' mm'
    return {
        'SKIN': f"{info['shell_thickness_mm']:g} mm",
        'FLANGE': f"{info['flange_thickness_mm']:g} mm",
        'DRY_MOUTH': f"{info['dry_opening_mm']:.1f} mm",
        'BOLT_D': f"{info['clamping']['hole_diameter_mm']:g} mm",
        'LOCATOR_HEIGHT': f"{info['locators']['height_mm']:g} mm",
        'LOCATOR_CLEARANCE': f"{info['locators']['radial_clearance_mm']:.2f} mm",
        'ROD_D': f"{info['dimensions_mm']['rod'][0]:g} mm",
        'ROD_LEN': f"{info['dimensions_mm']['rod'][2]:g} mm",
        'ROD_ENGAGEMENT': f"{info['rod_support']['engagement_mm']:.1f} mm",
        'ROD_EXPOSED': f"{info['dimensions_mm']['rod'][2]-info['rod_support']['engagement_mm']:g} mm",
        'ROD_CLEARANCE': f"{info['rod_support']['guide_diametral_clearance_mm']:g} mm",
        'ROD_GUIDE_D': f"{info['rod_support']['guide_diameter_mm']:g} mm",
        'ROD_TIE_WIDTH': f"{info['rod_support']['tie_width_mm']:g} mm",
        'ROD_SEAL_DEPTH': f"{info['rod_support']['seal_depth_mm']:g} mm",
        'SPOUT_WALL': f"{info['spout']['nominal_wall_mm']:g} mm",
        'SPOUT_OD': f"{info['spout']['outside_diameter_mm']:g} mm",
        'SPOUT_LAND': f"{info['spout']['finished_length_mm']:g} mm",
        'TIP_LENGTH': f"{info['spout']['sacrificial_length_mm']:g} mm",
        'TIP_CAP': f"{info['spout']['rod_end_clearance_mm']:g} mm",
        'ROD_OFFSET': f"{info['rod_tolerance_screen']['offset_mm']:g} mm",
        'ROD_TILT': f"{info['rod_tolerance_screen']['tilt_deg']:g}°",
        'ROD_AXIAL': f"{info['rod_tolerance_screen']['short_projection_mm']:g} mm",
        'ROD_EXTRA': f"{info['rod_tolerance_screen']['extra_projection_mm']:g} mm",
        'ROD_MIN_END': f"{info['rod_tolerance_screen']['minimum_end_clearance_mm']:.2f} mm",
        'ROD_MIN_WALL': f"{info['rod_tolerance_screen']['minimum_silicone_clearance_mm']:.2f} mm",
        'FINISH': f"{info['finish_allowance_mm']:.2f} mm",
        'FILL_D': f"{info['ports']['fill_diameter_mm']:g} mm",
        'VENT_D': f"{info['ports']['vent_diameter_mm']:g} mm",
        'CAST_VOLUME': f"{info['volume_ml']['funnel']:.0f} mL",
        'CAVITY_DIMS': dims('cavity'), 'CORE_DIMS': dims('core'),
        'ENVELOPE': f"{info['enclosing_diameter_mm']:.1f} mm",
        'CHAMBER_GAP': f"{info['chamber_radial_clearance_mm']:.1f} mm",
        'LOAD_SPAN': f"{info['load_screen']['span_mm']:g} mm",
        'LOAD_PRESSURE': f"{info['load_screen']['pressure_kpa']:.2f} kPa",
        'LOAD_MODULUS': f"{info['load_screen']['assumed_modulus_mpa']:g} MPa",
        'LOAD_DEFLECTION': f"{info['load_screen']['screen_deflection_mm']:.3f} mm",
        'HEAD_PRESSURE': f"{info['load_screen']['head_pressure_kpa']:.3f} kPa"}


def write_figures(models, figures, merge=False):
    sys.path.insert(0, str(HERE.parent))
    from docgen import substitute_md
    sidecar = models/'README.figures.json'
    key = '/tools/funnel-mold-print/verify_print.py'
    held = json.loads(sidecar.read_text()).get(key, {}) if merge and sidecar.exists() else {}
    held.update(figures)
    for retired in ('SOCKET', 'SOCKET_VENT'):
        held.pop(retired, None)
    substitute_md(models/'README.md', variables=figures)
    sidecar.write_text(json.dumps({key: held}, indent=2, sort_keys=True)+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models', type=Path, required=True)
    parser.add_argument('--slices', type=Path)
    parser.add_argument('--geometry-only', action='store_true', help='Refresh CAD dimensions before slicing.')
    parser.add_argument('--project-stem', default='funnel-mold')
    parser.add_argument('--single', action='store_true', help='Audit only the default Z trim.')
    parser.add_argument('--comparison-slices', type=Path, help='Also audit a 0.4 mm default slice for comparison.')
    args = parser.parse_args()
    info = json.loads((args.models/'design.json').read_text())
    if args.geometry_only:
        write_figures(args.models, geometry_figures(info), merge=True)
        return
    if args.slices is None:
        parser.error('--slices is required unless --geometry-only is used')
    records = []
    variants = [
        ('default', 'default-input', args.project_stem+'.3mf'),
        ('z018', 'z018-input', args.project_stem+'-z018.3mf')]
    for variant, input_name, project_name in variants[:1] if args.single else variants:
        project = args.slices/variant/project_name
        record = audit(project, args.slices/f'{input_name}.provenance.json', args.models)
        result = json.loads((args.slices/variant/'result.json').read_text())
        assert result['return_code'] == 0
        assert all(not p['warning_message'] for p in result['sliced_plates'])
        record['slice_result'] = result
        if 'corner_trial' in info:
            record['specimen'] = info['corner_trial']
        records.append(record)
        (args.models/project_name).write_bytes(project.read_bytes())
    bundle = args.slices/'funnel-mold-presets.bbscfg'
    with zipfile.ZipFile(bundle) as archive:
        for record in records:
            settings = record['settings']
            for kind, identity in [('process', 'print_settings_id'), ('filament', 'filament_settings_id')]:
                name = record['recipe'][kind+'_name']
                preset = json.loads(archive.read(name+'.json'))
                for key, expected in record['recipe'][kind+'_settings'].items():
                    assert equivalent(key, preset[key], expected['value'])
                    assert equivalent(key, preset[key], settings[key])
            machine = json.loads(archive.read(settings['printer_settings_id']+'.json'))
            assert machine['machine_start_gcode'] == settings['machine_start_gcode']
    (args.models/bundle.name).write_bytes(bundle.read_bytes())
    comparison = None
    if args.comparison_slices:
        source = args.comparison_slices/'default/funnel-mold.3mf'
        comparison = audit(source, args.comparison_slices/'default-input.provenance.json', args.models)
        comparison['project'] = 'funnel-mold-04.3mf'
        comparison['slice_result'] = json.loads((args.comparison_slices/'default/result.json').read_text())
        assert comparison['recipe']['nozzle_mm'] == 0.4
        assert comparison['slice_result']['return_code'] == 0
        assert all(not p['warning_message'] for p in comparison['slice_result']['sliced_plates'])
        (args.models/comparison['project']).write_bytes(source.read_bytes())
        records.append(comparison)
    profile = 'print-profile.json' if len(records[0]['gcode']) == 2 else args.project_stem+'-profile.json'
    (args.models/profile).write_text(json.dumps(records, indent=2)+'\n')
    if len(records[0]['gcode']) == 1:
        print(records[0]['project'], records[0]['effective_setting_count'], 'settings checked')
        return
    def duration(plate):
        minutes = round(plate['total_predication']/60)
        return f'{minutes//60} h {minutes%60:02d} min'
    cavity, core = records[0]['slice_result']['sliced_plates']
    figures = geometry_figures(info)
    figures.update({'CAVITY_TIME': duration(cavity), 'CORE_TIME': duration(core),
                    'CAVITY_MASS': f"{cavity['filaments'][0]['total_used_g']:.0f} g",
                    'CORE_MASS': f"{core['filaments'][0]['total_used_g']:.0f} g"})
    recipe = records[0]['recipe']
    figures.update({'NOZZLE': f"{recipe['nozzle_mm']:g} mm", 'NOZZLE_TYPE': recipe['nozzle_type'],
                    'LAYER': recipe['process_settings']['layer_height']['value']+' mm',
                    'FLOW_CAP': ('18' if recipe['nozzle_type'] == 'High Flow' else '12')+' mm³/s'})
    mass = lambda plates: sum(p['filaments'][0]['total_used_g'] for p in plates)
    seconds = lambda plates: sum(p['total_predication'] for p in plates)
    plates = records[0]['slice_result']['sliced_plates']
    figures.update({'TOTAL_MASS': f'{mass(plates)/1000:.2f} kg',
                    'TOTAL_TIME': duration({'total_predication': seconds(plates)})})
    if comparison:
        alt = comparison['slice_result']['sliced_plates']
        figures.update({'FINE_TIME': duration({'total_predication': seconds(alt)}),
                        'FINE_MASS': f'{mass(alt)/1000:.2f} kg'})
    write_figures(args.models, figures)
    for record in records:
        print(record['project'], record['effective_setting_count'], 'settings checked')
        for plate in record['slice_result']['sliced_plates']:
            print('plate', plate['id'], round(plate['total_predication']/3600, 3), 'hours')


if __name__ == '__main__':
    main()
