"""Compare actual first-layer support paths in two Bambu G-code archives."""

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union


def first_layer(project):
    with zipfile.ZipFile(project) as archive:
        assert archive.testzip() is None
        raw = archive.read('Metadata/plate_1.gcode')
        gcode = raw.decode()
        assert hashlib.md5(raw).hexdigest() == archive.read(
            'Metadata/plate_1.gcode.md5').decode().strip().lower()
        plate = ET.fromstring(archive.read('Metadata/slice_info.config')).find('plate')
        assert [n.attrib for n in plate.findall('nozzle')] == [
            {'id': '0', 'extruder_id': '1', 'nozzle_diameter': '0.8', 'volume_type': 'High Flow'}]
        settings = dict(re.findall(r'^; (\w+) = (.*)$',
            gcode.split('; CONFIG_BLOCK_END')[0], re.M))
    layer = gcode.split('; CHANGE_LAYER\n')[1]
    startup = gcode.split('; CONFIG_BLOCK_END')[1].split('; CHANGE_LAYER')[0]
    commands = [line.partition(';')[0].strip() for line in startup.splitlines()]
    assert 'G29.1 Z0.16' in commands
    # Only progress estimates and the footprint's bed-leveling rectangle may differ.
    startup_commands = [line for line in commands if line and not (
        line.startswith('M73 ') or re.match(r'G29 A[12] O ', line))]
    z = float(re.search(r'^; Z_HEIGHT: ([\d.]+)', layer, re.M)[1])
    assert z == 0.4
    x = y = None
    width = 0.82
    feature = None
    segments, polygons = [], []
    for line in layer.splitlines():
        if line.startswith('; FEATURE: '):
            feature = line.removeprefix('; FEATURE: ')
        elif line.startswith('; LINE_WIDTH: '):
            width = float(line.removeprefix('; LINE_WIDTH: '))
        code = line.partition(';')[0].split()
        if not code or code[0] not in ('G0', 'G1', 'G2', 'G3'):
            continue
        args = {m[0]: float(m[1:]) for m in code[1:]
                if re.fullmatch(r'[XYE][-+]?\d*\.?\d+', m)}
        nx, ny = args.get('X', x), args.get('Y', y)
        if (feature == 'Support' and args.get('E', 0) > 0
                and None not in (x, y, nx, ny) and (x, y) != (nx, ny)):
            assert code[0] == 'G1', 'Extruding arcs need a curved-path reader'
            segment = [(x, y), (nx, ny)]
            segments.append(segment)
            polygons.append(LineString(segment).buffer(width / 2, quad_segs=4))
        x, y = nx, ny
    assert segments, 'No first-layer support extrusion'
    footprint = unary_union(polygons)
    bed = Polygon([tuple(map(float, p.split('x')))
                   for p in settings['printable_area'].split(',')])
    assert bed.covers(footprint), 'Support footprint extends beyond the bed'
    return {
        'project': project.name,
        'project_sha256': hashlib.sha256(project.read_bytes()).hexdigest(),
        'gcode_sha256': hashlib.sha256(raw).hexdigest(),
        'initial_layer_expansion_mm': float(settings['raft_first_layer_expansion']),
        'support_extrusion_area_mm2': round(footprint.area, 1),
        'support_bounds_mm': [round(v, 2) for v in footprint.bounds],
        'within_printable_area': True,
        'first_layer_mm': z,
    }, settings, segments, startup_commands


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous', type=Path, required=True)
    parser.add_argument('--retry', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--image', type=Path, required=True)
    args = parser.parse_args()
    before, old_settings, old_paths, old_startup = first_layer(args.previous)
    after, new_settings, new_paths, new_startup = first_layer(args.retry)
    assert old_startup == new_startup, 'Startup commands changed'
    changes = {k: {'previous': old_settings.get(k), 'retry': new_settings.get(k)}
               for k in old_settings.keys() | new_settings.keys()
               if old_settings.get(k) != new_settings.get(k)}
    normalizations = {}
    for key, values in list(changes.items()):
        old, new = values['previous'], values['retry']
        # Studio adds the unused right High Flow variant to the G-code header.
        # The slice's sole nozzle is asserted above; the existing entries must match.
        a, b = re.split('[,;]', old), re.split('[,;]', new)
        expanded = len(b) > len(a) > 1 and b[:len(a)] == a
        stock_prime = key == 'filament_prime_volume' and (old, new) == ('45', '30')
        metadata = key == 'different_settings_to_system' and new.replace(
            ';raft_first_layer_expansion', '') == old
        unused_nozzle = key == 'extruder_nozzle_stats' and (old, new) == (
            '"High Flow#1";Standard#0', '"High Flow#1";"Standard#0|High Flow#0"')
        if expanded or stock_prime or metadata or unused_nozzle:
            normalizations[key] = changes.pop(key)
    assert set(changes) == {'raft_first_layer_expansion', 'print_settings_id'}, changes
    assert before['initial_layer_expansion_mm'] == -1
    assert after['initial_layer_expansion_mm'] == 8
    assert after['support_extrusion_area_mm2'] > before['support_extrusion_area_mm2']
    ratio = after['support_extrusion_area_mm2'] / before['support_extrusion_area_mm2']
    report = {'previous': before, 'retry': after,
              'gcode_setting_changes': changes,
              'studio_header_normalizations': normalizations,
              'startup_commands_match_except_progress_and_leveling_rectangle': True,
              'effective_g29_1_mm': 0.16,
              'support_extrusion_area_ratio': round(ratio, 3),
              'method': 'Union of first-layer support G1 extrusion segments buffered by half their emitted line width; excludes model brim and startup purge.'}
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    fig, axes = plt.subplots(1, 2, figsize=(10, 5), constrained_layout=True)
    for ax, paths, reading, title in zip(axes, (old_paths, new_paths),
            (before, after), ('Previous: Auto', 'Retry: 8 mm expansion')):
        ax.add_collection(LineCollection(paths, colors='#157b91', linewidths=0.5))
        ax.set(xlim=(25, 275), ylim=(35, 285), aspect='equal',
               title=f"{title}\n{reading['support_extrusion_area_mm2']:,.0f} mm² support contact",
               xlabel='X (mm)', ylabel='Y (mm)')
    fig.savefig(args.image, dpi=180)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
