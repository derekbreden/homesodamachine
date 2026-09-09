"""Account for the effective settings in a sliced funnel-mold project.

Pass the .provenance.json emitted by prepare_print.py alongside its unsliced
input. Bambu Studio supplies the built-in defaults and serializes the result;
this audit records that final configuration, including local overrides.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import xml.etree.ElementTree as ET
import zipfile


def equivalent(key, supplied, effective):
    if supplied == effective:
        return True
    if key == 'best_object_pos':
        return supplied.replace('x', ',') == effective
    if key == 'enable_long_retraction_when_cut':
        return supplied == [effective]
    if key in ('top_surface_density', 'bottom_surface_density', 'monotonic_travel_into_wall'):
        return float(supplied.rstrip('%')) == float(effective.rstrip('%'))
    if isinstance(supplied, list) and isinstance(effective, list):
        return len(supplied) == len(effective) and all(
            equivalent(key, a, b) for a, b in zip(supplied, effective))
    try:
        return math.isclose(float(supplied), float(effective), rel_tol=1e-9, abs_tol=1e-9)
    except (TypeError, ValueError):
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('--provenance', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    origin = json.loads(args.provenance.read_text())
    supplied = origin['supplied_settings']
    recipe = origin['recipe']
    with zipfile.ZipFile(args.project) as archive:
        names = archive.namelist()
        settings = json.loads(archive.read('Metadata/project_settings.config'))
        local = ET.fromstring(archive.read('Metadata/model_settings.config'))
        ranges = ET.fromstring(archive.read('Metadata/layer_config_ranges.xml'))
        sliced = ET.fromstring(archive.read('Metadata/slice_info.config'))
        assert not any('filament_settings_' in name or 'custom_gcode' in name for name in names)
        assert archive.testzip() is None, 'ZIP checksum failure'

    resolved = {}
    normalized = []
    for key, value in settings.items():
        if key in supplied:
            record = dict(supplied[key])
            original = record.pop('value')
            if not equivalent(key, original, value):
                assert key == 'filament_prime_volume' and original == ['30'] and value == ['45'], (key, original, value)
                record['slicer_rewrite'] = (
                    'BambuStudio CLI sets filament_prime_volume to 45 for a BBL 3MF '
                    'when no filament file is loaded separately. Prime tower is disabled '
                    'and these plates contain no material changes.')
                record['implementation'] = 'https://github.com/bambulab/BambuStudio/blob/master/src/BambuStudio.cpp'
                record['supplied_value'] = original
            elif original != value:
                normalized.append({'setting': key, 'supplied': original, 'serialized': value})
        elif key == 'wall_sequence':
            record = dict(supplied['wall_infill_order'])
            record.pop('value')
            record['slicer_legacy_name'] = 'wall_infill_order'
            assert value == 'inner wall/outer wall'
        else:
            record = {'slicer_default': origin['slicer_version']}
        resolved[key] = {'value': value, **record}

    precision = {k: ','.join(v['value']) if isinstance(v['value'], list) else v['value']
                 for k, v in recipe['precision_settings'].items()}
    objects = []
    object_data = {'name', 'extruder'}
    part_data = {'name', 'matrix', 'source_file', 'source_object_id', 'source_volume_id',
                 'source_offset_x', 'source_offset_y', 'source_offset_z'}
    for index, obj in enumerate(local.findall('object'), 1):
        md = {m.get('key'): m.get('value') for m in obj.findall('metadata') if m.get('key')}
        name = md['name'].removeprefix('Funnel mold ')
        overrides = {k: v for k, v in md.items() if k not in object_data}
        assert overrides == (precision if 'witness' in name else {}), (name, overrides)
        parts = []
        for part in obj.findall('part'):
            pm = {m.get('key'): m.get('value') for m in part.findall('metadata') if m.get('key')}
            po = {k: v for k, v in pm.items() if k not in part_data}
            assert po == (precision if part.get('subtype') == 'modifier_part' else {}), (name, po)
            parts.append({'name': pm['source_file'], 'type': part.get('subtype'), 'overrides': po})
        actual = []
        ro = ranges.find(f"object[@id='{index}']")
        if ro is not None:
            for band in ro.findall('range'):
                options = band.findall('option')
                assert len(options) == 1 and options[0].get('opt_key') == 'layer_height'
                actual.append((float(band.get('min_z')), float(band.get('max_z')), float(options[0].text)))
        expected = [(b['min_z'], b['max_z'], b['layer_height']) for b in recipe['layer_ranges_mm'][name]]
        assert actual == expected, (name, actual, expected)
        objects.append({'name': name, 'object_overrides': overrides, 'parts': parts,
                        'layer_ranges': recipe['layer_ranges_mm'][name]})

    plates = []
    for plate in local.findall('plate'):
        metadata = {m.get('key'): m.get('value') for m in plate.findall('metadata')}
        allowed = {'plater_id', 'plater_name', 'locked', 'filament_map_mode', 'filament_maps',
                   'filament_volume_maps', 'gcode_file', 'thumbnail_file', 'thumbnail_no_light_file',
                   'top_file', 'pick_file', 'bed_type'}
        assert not set(metadata)-allowed, metadata
        assert metadata['filament_maps'] == metadata['filament_volume_maps'] == '1'
        assert metadata['filament_map_mode'] == 'Manual'
        assert metadata['bed_type'] == settings['curr_bed_type'] == 'Textured PEI Plate'
        plates.append(metadata)
    assert len(objects) == 5 and len(plates) == 3
    for plate in sliced.findall('plate'):
        nozzles = [n.attrib for n in plate.findall('nozzle')]
        assert nozzles == [{'id': '0', 'extruder_id': '1', 'nozzle_diameter': '0.8', 'volume_type': 'High Flow'}]
    assert settings['post_process'] == []
    assert settings['before_layer_change_gcode'] == ''
    assert settings['enable_support'] == settings['enable_prime_tower'] == '0'
    assert settings['xy_contour_compensation'] == settings['xy_hole_compensation'] == '0'
    assert settings['seam_slope_type'] == 'none' and settings['filament_scarf_seam_type'] == ['none']
    assert settings['filament_max_volumetric_speed'] == ['16', '18']
    assert settings['filament_self_index'] == ['1', '1']
    report = {
        'project': args.project.name,
        'project_sha256': hashlib.sha256(args.project.read_bytes()).hexdigest(),
        'slicer_version': origin['slicer_version'],
        'inputs': 'Current STL files, print-recipe.json and installed Bambu system presets; no prior 3MF or user preset is read by prepare_print.py.',
        'system_preset_sha256': origin['system_preset_sha256'],
        'mesh_files_sha256': origin['mesh_files'],
        'recipe': recipe,
        'effective_setting_count': len(settings),
        'settings': resolved,
        'representation_normalizations': normalized,
        'input_keys_not_serialized': {k: v for k, v in supplied.items() if k not in settings},
        'input_keys_note': 'Bambu omits obsolete/unrecognized fields and rewrites legacy names. wall_infill_order is accounted for at wall_sequence. Only the effective settings above are the saved print configuration.',
        'objects': objects,
        'plates': plates,
        'archive_members': names,
        'extra_filament_or_per_layer_gcode_files': [],
        'physical_validation': 'The 18 mm3/s flow target, 60 mm/s finishing speed, coating result and extraction load remain subject to the actual spool, witnesses and assembled tooling. Z trim is the user-observed plate calibration.'
    }
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(f'{len(settings)} effective settings, five objects, two modifiers, three plates: all accounted for.')


if __name__ == '__main__':
    main()
