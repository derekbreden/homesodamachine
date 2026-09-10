"""Read the saved solid-mold projects, their settings, and their embedded G-code."""

import argparse
import hashlib
import json
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'funnel-mold-print'))
from audit_profile import equivalent


def audit(project, provenance_path, models):
    origin = json.loads(provenance_path.read_text())
    recipe = origin['recipe']
    with zipfile.ZipFile(project) as archive:
        assert archive.testzip() is None
        settings = json.loads(archive.read('Metadata/project_settings.config'))
        local = ET.fromstring(archive.read('Metadata/model_settings.config'))
        ranges = ET.fromstring(archive.read('Metadata/layer_config_ranges.xml'))
        slices = ET.fromstring(archive.read('Metadata/slice_info.config'))
        normalized = []
        for key, value in settings.items():
            if key in origin['supplied_settings']:
                supplied = origin['supplied_settings'][key]['value']
                assert equivalent(key, supplied, value), (key, supplied, value)
                if supplied != value:
                    normalized.append(key)
        assert settings['sparse_infill_density'] == '100%'
        assert settings['enable_support'] == settings['enable_prime_tower'] == '0'
        assert settings['brim_type'] == 'no_brim'
        assert settings['filament_max_volumetric_speed'] == ['16', '18']
        assert settings['nozzle_temperature'] == ['255', '255']
        assert settings['curr_bed_type'] == 'Textured PEI Plate'
        assert settings['post_process'] == []
        assert settings['before_layer_change_gcode'] == ''
        assert len(local.findall('object')) == len(local.findall('plate')) == 2
        for obj in local.findall('object'):
            keys = {m.get('key') for m in obj.findall('metadata') if m.get('key')}
            assert keys == {'name', 'extruder'}, keys
            assert len(obj.findall('part')) == 1
            assert obj.find('part').get('subtype') == 'normal_part'
        gcode_records = []
        for index, name in enumerate(('cavity', 'core'), 1):
            digest = hashlib.sha256((models/f'{name}.stl').read_bytes()).hexdigest()
            assert digest == origin['mesh_sha256'][name], 'STL changed after preparation'
            actual = ranges.find(f"object[@id='{index}']")
            bands = [(float(b.get('min_z')), float(b.get('max_z')),
                      float(b.find('option').text)) for b in actual.findall('range')]
            assert bands == [(a, b, .16) for a, b in recipe['layer_ranges_mm'][name]]
            plate = local.findall('plate')[index-1]
            md = {m.get('key'): m.get('value') for m in plate.findall('metadata')}
            assert md['bed_type'] == 'Textured PEI Plate'
            assert md['filament_maps'] == md['filament_volume_maps'] == '1'
            assert md['filament_map_mode'] == 'Manual'
            gcode_name = f'Metadata/plate_{index}.gcode'
            data = archive.read(gcode_name)
            recorded_md5 = archive.read(gcode_name+'.md5').decode().strip()
            assert hashlib.md5(data).hexdigest().lower() == recorded_md5.lower()
            for feature in (b'; FEATURE: Support', b'; FEATURE: Brim', b'; FEATURE: Skirt'):
                assert feature not in data
            gcode_records.append({'part': name, 'stl_sha256': digest,
                'gcode_sha256': hashlib.sha256(data).hexdigest(),
                'header': data.decode().split('; HEADER_BLOCK_END')[0].splitlines()[1:]})
        for plate in slices.findall('plate'):
            assert [n.attrib for n in plate.findall('nozzle')] == [
                {'id': '0', 'extruder_id': '1', 'nozzle_diameter': '0.8', 'volume_type': 'High Flow'}]
    return {'project': project.name, 'sha256': hashlib.sha256(project.read_bytes()).hexdigest(),
        'effective_setting_count': len(settings), 'normalized_settings': normalized,
        'supplied_setting_origins': origin['supplied_settings'],
        'slicer_defaults': {k: v for k, v in settings.items() if k not in origin['supplied_settings']},
        'settings': settings, 'recipe': recipe, 'gcode': gcode_records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models', type=Path, required=True)
    parser.add_argument('--slices', type=Path, required=True)
    parser.add_argument('--project-stem', default='solid-mold')
    args = parser.parse_args()
    records = []
    for variant, input_name, project_name in [
        ('default', 'default-input', args.project_stem+'.3mf'),
        ('z018', 'z018-input', args.project_stem+'-z018.3mf')]:
        project = args.slices/variant/project_name
        record = audit(project, args.slices/f'{input_name}.provenance.json', args.models)
        result = json.loads((args.slices/variant/'result.json').read_text())
        assert result['return_code'] == 0
        assert all(not p['warning_message'] for p in result['sliced_plates'])
        record['slice_result'] = result
        records.append(record)
        (args.models/project_name).write_bytes(project.read_bytes())
    bundle = args.slices/'solid-mold-presets.bbscfg'
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
    (args.models/'print-profile.json').write_text(json.dumps(records, indent=2)+'\n')
    sys.path.insert(0, str(HERE.parent))
    from docgen import substitute_md
    info = json.loads((args.models/'design.json').read_text())
    def dims(name):
        return ' × '.join(f'{v:.1f}'.removesuffix('.0') for v in info['dimensions_mm'][name])+' mm'
    def duration(plate):
        minutes = round(plate['total_predication']/60)
        return f'{minutes//60} h {minutes%60:02d} min'
    cavity, core = records[0]['slice_result']['sliced_plates']
    figures = {
        'REGISTER': f"{info['register_depth_mm']:g} mm",
        'ROD_D': f"{info['dimensions_mm']['rod'][0]:g} mm",
        'ROD_LEN': f"{info['dimensions_mm']['rod'][2]:g} mm",
        'SOCKET': f"{info['rod_socket_depth_mm']:.1f} mm",
        'FINISH': f"{info['finish_allowance_mm']:.2f} mm",
        'CAST_VOLUME': f"{info['volume_ml']['funnel']:.0f} mL",
        'CAVITY_DIMS': dims('cavity'), 'CORE_DIMS': dims('core'),
        'CAVITY_TIME': duration(cavity), 'CORE_TIME': duration(core),
        'CAVITY_MASS': f"{cavity['filaments'][0]['total_used_g']:.0f} g",
        'CORE_MASS': f"{core['filaments'][0]['total_used_g']:.0f} g",
        'ENVELOPE': f"{info['enclosing_diameter_mm']:.1f} mm",
        'CHAMBER_GAP': f"{info['chamber_radial_clearance_mm']:.1f} mm"}
    substitute_md(args.models/'README.md', variables=figures)
    # docgen records sidecars automatically only for callers under hardware.
    (args.models/'README.figures.json').write_text(json.dumps({
        '/tools/funnel-mold-design/verify_print.py': figures}, indent=2, sort_keys=True)+'\n')
    for record in records:
        print(record['project'], record['effective_setting_count'], 'settings checked')
        for plate in record['slice_result']['sliced_plates']:
            print('plate', plate['id'], round(plate['total_predication']/3600, 3), 'hours')


if __name__ == '__main__':
    main()
