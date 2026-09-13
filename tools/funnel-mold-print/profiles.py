"""Bambu system preset resolution and 3MF serialization for the funnel mold."""

import hashlib
import json
import math
import zipfile
import xml.etree.ElementTree as ET

CORE = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
PROD = 'http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
ET.register_namespace('', CORE)
ET.register_namespace('p', PROD)
ET.register_namespace('BambuStudio', 'http://schemas.bambulab.com/package/2021')
qn = lambda tag: f'{{{CORE}}}{tag}'
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


def printer_names(recipe):
    return [recipe['system_presets']['machine']] + [
        f"Bambu Lab H2C {recipe['nozzle_mm']:g} {recipe['nozzle_type']} +{v:.2f} Z trim"
        for v in recipe['z_trim']['available_mm']]


def preset_bundle(root, recipe, version, destination):
    """Save all three selectors' presets with their stock parents and recipe edits."""
    stock, _, _ = system_preset(root, 'machine', recipe['system_presets']['machine'], {})
    profiles = []
    for offset in recipe['z_trim']['available_mm']:
        name = f"Bambu Lab H2C {recipe['nozzle_mm']:g} {recipe['nozzle_type']} +{offset:.2f} Z trim"
        profiles.append({'from': 'User', 'inherits': recipe['system_presets']['machine'],
            'name': name, 'printer_settings_id': name, 'version': version,
            'machine_start_gcode': trimmed_start_gcode(stock['machine_start_gcode'], offset),
            'default_nozzle_volume_type': [recipe['nozzle_type'], 'Standard']})
    for kind, identity in (('process', 'print_settings_id'), ('filament', 'filament_settings_id')):
        name = recipe[f'{kind}_name']
        assert not any(c in name for c in '/\\'), 'Preset names must also be valid filenames.'
        profile = {'from': 'User', 'inherits': recipe['system_presets'][kind],
                   'name': name, 'version': version,
                   identity: [name] if kind == 'filament' else name,
                   **{key: choice['value'] for key, choice in recipe[f'{kind}_settings'].items()}}
        if kind == 'process':
            profile['compatible_printers'] = printer_names(recipe)
        else:
            _, _, ids = system_preset(root, kind, recipe['system_presets'][kind], {})
            profile['filament_id'] = ids['filament_id']
        profiles.append(profile)
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
        for profile in profiles:
            archive.writestr(profile['name']+'.json', json.dumps(profile, indent=2)+'\n')


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
        'printer_settings_id': f"Bambu Lab H2C {recipe['nozzle_mm']:g} {recipe['nozzle_type']} +{trim:.2f} Z trim",
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
        'filament_volume_map': ['1' if recipe['nozzle_type'] == 'High Flow' else '0'],
        'nozzle_volume_type': [recipe['nozzle_type'], 'Standard'],
        'default_nozzle_volume_type': [recipe['nozzle_type'], 'Standard'],
        'extruder_nozzle_stats': [recipe['nozzle_type']+'#1', 'Standard#1'],
        'extruder_nozzle_stats_new': [recipe['nozzle_type']+'#1', 'Standard#1'],
        'curr_bed_type': 'Textured PEI Plate',
        'print_compatible_printers': printer_names(recipe),
    }
    for key, value in assignment.items():
        values[key] = value
        sources[key] = {'generator': 'fresh_settings',
            'reason': 'One PETG filament on the left selected nozzle, textured PEI; named source presets.'}
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
