"""Measure commanded support and travel motion in Bambu's sliced 3MFs."""

import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile


def motion(gcode):
    body = gcode[gcode.index('; CHANGE_LAYER'):].split('; MACHINE_END_GCODE_START')[0]
    assert 'M82' not in body, 'Reader expects relative extrusion'
    feature = ''
    x = y = feed = acceleration = 0.0
    layer = 0
    wiping = False
    readings = defaultdict(lambda: {'moves': 0, 'max_speed_mm_s': 0.,
                                    'max_acceleration_mm_s2': 0.})
    bounds = [math.inf, math.inf, -math.inf, -math.inf]
    for raw in body.splitlines():
        if raw.startswith('; layer num/total_layer_count:'):
            layer = int(raw.split(':')[1].split('/')[0])
        elif raw.startswith('; FEATURE:'):
            feature = raw.split(':', 1)[1].strip()
        elif raw == '; WIPE_START':
            wiping = True
        elif raw == '; WIPE_END':
            wiping = False
        tokens = raw.partition(';')[0].split()
        if not tokens:
            continue
        values = {t[0]: float(t[1:]) for t in tokens[1:]
                  if re.fullmatch(r'[XYEFSPTIJ][-+]?\d*\.?\d+', t)}
        if tokens[0] == 'M204':
            assert 'P' not in values and 'T' not in values, 'Separate acceleration modes'
            acceleration = values.get('S', acceleration)
        if tokens[0] not in ('G0', 'G1', 'G2', 'G3'):
            continue
        nx, ny = values.get('X', x), values.get('Y', y)
        feed = values.get('F', feed)
        moving = math.hypot(nx-x, ny-y) > 1e-6 or any(k in values for k in ('I', 'J'))
        if moving and values.get('E', 0) > 0:
            bounds = [min(bounds[0], x, nx), min(bounds[1], y, ny),
                      max(bounds[2], x, nx), max(bounds[3], y, ny)]
        if layer > 1 and moving and not wiping:
            kind = feature if values.get('E', 0) > 0 else 'Travel'
            if kind in ('Support', 'Support interface', 'Travel'):
                record = readings[kind]
                record['moves'] += 1
                record['max_speed_mm_s'] = max(record['max_speed_mm_s'], feed/60)
                record['max_acceleration_mm_s2'] = max(
                    record['max_acceleration_mm_s2'], acceleration)
        x, y = nx, ny
    return {'after_first_layer': dict(readings), 'total_layers': layer,
            'extruding_centerline_bounds_mm': bounds}


def inspect(project):
    with zipfile.ZipFile(project) as archive:
        assert archive.testzip() is None
        settings = json.loads(archive.read('Metadata/project_settings.config'))
        slices = ET.fromstring(archive.read('Metadata/slice_info.config'))
        plates = []
        for plate in slices.findall('plate'):
            meta = {m.get('key'): m.get('value') for m in plate.findall('metadata')}
            name = f"Metadata/plate_{meta['index']}.gcode"
            raw = archive.read(name)
            assert hashlib.md5(raw).hexdigest() == archive.read(name+'.md5').decode().strip().lower()
            gcode = raw.decode()
            assert '\nG29.1 Z0.16\n' in gcode.replace('    ', '')
            assert [n.attrib for n in plate.findall('nozzle')] == [
                {'id': '0', 'extruder_id': '1', 'nozzle_diameter': '0.8', 'volume_type': 'High Flow'}]
            assert meta['outside'] == 'false'
            plates.append({'gcode': name, 'gcode_sha256': hashlib.sha256(raw).hexdigest(),
                           'estimated_seconds': int(meta['prediction']),
                           'estimated_filament_g': float(meta['weight']), **motion(gcode)})
    return settings, {'project': project.name,
                      'project_sha256': hashlib.sha256(project.read_bytes()).hexdigest(),
                      'plates': plates}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous', type=Path, required=True)
    parser.add_argument('--retry', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    old, previous = inspect(args.previous)
    new, retry = inspect(args.retry)
    changed = {k: {'previous': old.get(k), 'retry': new.get(k)}
               for k in sorted(old.keys() | new.keys()) if old.get(k) != new.get(k)}
    expected = {'support_speed', 'support_interface_speed', 'travel_speed',
                'default_acceleration', 'travel_acceleration', 'tree_support_wall_count',
                'tree_support_branch_diameter', 'avoid_crossing_wall_includes_support',
                'print_settings_id', 'print_compatible_printers', 'different_settings_to_system'}
    assert set(changed) <= expected, changed
    assert new['printer_settings_id'] in new['print_compatible_printers']
    for plate in retry['plates']:
        readings = plate['after_first_layer']
        for kind, cap in [('Support', 40), ('Support interface', 30), ('Travel', 150)]:
            assert readings[kind]['moves'] > 0
            assert readings[kind]['max_speed_mm_s'] <= cap + 0.02, (kind, readings[kind])
            assert readings[kind]['max_acceleration_mm_s2'] <= 1500, (kind, readings[kind])
    report = {'previous': previous, 'retry': retry, 'settings_changes': changed,
              'machine_start_gcode_matches': old['machine_start_gcode'] == new['machine_start_gcode'],
              'effective_g29_1_mm': 0.16,
              'scope': 'Commanded motion after the first layer, including spiral travel lifts; excludes wiping, startup and shutdown. This is not a physical stability test.'}
    assert report['machine_start_gcode_matches']
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
