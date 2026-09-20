"""Read the coupon's actual native paths, including the keeper beam and support lanes."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
from shapely.geometry import LineString
from shapely.ops import unary_union

from prepare_print import HERE, ROOT, JOB, JOB_NAME
sys.path.insert(0, str(ROOT / 'hardware/printed-parts/faucet'))
from prepare_display_print import extrusion_segments


def main():
    report = json.loads((JOB / (JOB_NAME + '-input.print.json')).read_text())
    readiness = json.loads((HERE / 'print-readiness.json').read_text())
    gcode = JOB / 'ready/plate_1.gcode'
    assert hashlib.sha256(gcode.read_bytes()).hexdigest() == readiness['gcode_sha256']
    rows = {row['identify_id']: row for row in report['parts']}
    paths = defaultdict(list)
    for segment in extrusion_segments(gcode):
        if segment['object'] not in rows:
            continue
        row = rows[segment['object']]
        rotation = np.array(row['build_transform'][:9]).reshape(3, 3).T
        placed = np.array([segment['a'], segment['b']])
        local = ((placed - np.array(row['plate_translation_mm'])) @ rotation
                 + np.array(row['source_center_mm']))
        paths[row['name']].append({**segment, 'local': local.tolist()})
    layer_number, nozzle_c, bed_c = 0, None, None
    layer_temperatures = {}
    for raw in gcode.read_text().splitlines():
        line = raw.strip()
        if line == '; CHANGE_LAYER':
            layer_number += 1
        code = line.split(';', 1)[0].strip()
        if not code:
            continue
        command = code.split()[0]
        fields = {key: float(value) for key, value in re.findall(r'([XYZESD])([-+0-9.]+)', code)}
        if command in ('M104', 'M109') and 'S' in fields:
            nozzle_c = fields['S']
        if command in ('M140', 'M190'):
            bed_c = fields.get('S', fields.get('D', bed_c))
        if (layer_number and command in ('G0', 'G1') and fields.get('E', 0.0) > 0
                and ('X' in fields or 'Y' in fields)):
            layer_temperatures.setdefault(layer_number, (nozzle_c, bed_c))
    keeper = paths['joint-coupon-keeper']
    by_layer = defaultdict(list)
    for segment in keeper:
        if not segment['feature'].startswith('Support') and segment['feature'] not in ('Brim', 'Custom'):
            by_layer[segment['layer']].append(segment)
    readings, errors = [], []
    if layer_temperatures.get(1) != (265.0, 80.0):
        errors.append('first model layer does not command the profile temperatures 265/80 C')
    if any(temps != (280.0, 80.0) for layer, temps in layer_temperatures.items() if layer > 1):
        errors.append('subsequent model layer does not command the profile temperatures 280/80 C')
    if len(layer_temperatures) != readiness['layers']:
        errors.append('model temperature readings do not cover every layer')
    log = (JOB / 'ready/bambu-cli.log').read_text()
    parser_messages = [line.split('[error]', 1)[1].strip() for line in log.splitlines() if '[error]' in line]
    expected_diagnostics = {'Invalid T command (T1001).', 'Invalid T command (T65535).',
                            'Invalid T command (T65279).'}
    if set(parser_messages) - expected_diagnostics:
        errors.append('native slicer emitted a new diagnostic')
    for layer, segments in sorted(by_layer.items()):
        if layer > 1.17:
            continue
        roads = unary_union([LineString(np.array(row['local'])[:, :2]).buffer(row['width'] / 2.0)
                             for row in segments])
        for y in (19.0, 22.0, 25.0, 28.0):
            intersection = roads.intersection(LineString(((-1.0, y), (4.6, y))))
            pieces = [intersection] if intersection.geom_type == 'LineString' else list(intersection.geoms)
            spans = sorted((part.bounds[0], part.bounds[2]) for part in pieces if not part.is_empty)
            beam = next(((lo, hi) for lo, hi in spans if lo <= 0.85 <= hi), None)
            spine = next(((lo, hi) for lo, hi in spans if lo <= 2.7 <= hi), None)
            if beam is None or spine is None:
                errors.append(f'keeper beam or spine absent at layer {layer:g}, Y{y:g}')
                continue
            width, gap = beam[1] - beam[0], spine[0] - beam[1]
            readings.append({'layer_z_mm': layer, 'probe_y_mm': y,
                             'beam_road_bounds_x_mm': list(beam),
                             'beam_road_width_mm': width, 'open_gap_to_spine_mm': gap})
            if width < 0.65 or gap < 0.40:
                errors.append(f'keeper beam width/gap is {width:.3f}/{gap:.3f} at {layer:g}, Y{y:g}')
    if len({row['layer_z_mm'] for row in readings}) < 5:
        errors.append('keeper beam does not persist through all five expected model layers')
    support = json.loads((JOB / (JOB_NAME + '-input.support-audit.json')).read_text())
    lanes = {
        'joint-coupon-left': {
            'contacts': 'Undersides of the two headed keys.',
            'reason': 'Square head faces transfer joint load; the neck is a complete rigid section.',
            'removal_lane': 'Open rear face of the loose left coupon, directly away from the lap in +Y.',
        },
        'joint-coupon-right': {
            'contacts': 'Crowns of the two key receiving pockets.',
            'reason': 'Flat pocket boundaries retain the keyed section and its supported clearance.',
            'removal_lane': 'The emitted tree has fore and aft legs. Separate them at the accessible bed/root branches; '
                            'the fore leg leaves in -Y and the opened rear pockets expose the aft leg for +Y removal. '
                            'No keeper or mating half is installed during cleanup.',
        },
        'joint-coupon-keeper': {
            'contacts': 'Small catch shoulder if support is emitted; beam and blocks start on the rear face.',
            'reason': 'Square catch shoulder positively retains the keeper.',
            'removal_lane': 'Loose keeper has an exposed catch and beam gap; no hardware or mating part covers them.',
        },
    }
    for row in support['parts']:
        lanes[row['piece']]['summary'] = row['summary']
        lanes[row['piece']]['trees'] = row['trees']
        lanes[row['piece']]['interfaces'] = row['interfaces']

    fig, axes = plt.subplots(1, 3, figsize=(14, 6), constrained_layout=True)
    for ax, name in zip(axes[:2], ('joint-coupon-left', 'joint-coupon-right')):
        model, supports = [], []
        for row in paths[name]:
            points = np.array(row['local'])[:, [1, 2]]
            (supports if row['feature'].startswith('Support') else model).append(points)
        ax.add_collection(LineCollection(model, colors='#526272', linewidths=0.35, alpha=0.35,
                                         rasterized=True))
        ax.add_collection(LineCollection(supports, colors='#D97706', linewidths=0.8,
                                         rasterized=True))
        ax.autoscale()
        ax.set_aspect('equal')
        ax.set_title(name.replace('joint-coupon-', '').title() + ': actual support paths')
        ax.set_xlabel('Print Y (mm) · rear access →')
        ax.set_ylabel('Print Z (mm)')
        ax.grid(alpha=0.2)
    ax = axes[2]
    selected = min(by_layer, key=lambda value: abs(value - 0.68))
    for row in by_layer[selected]:
        points = np.array(row['local'])[:, :2]
        ax.plot(points[:, 0], points[:, 1], color='#087E8B', linewidth=max(row['width'] * 2.0, 0.4))
    ax.set_xlim(-0.4, 4.0)
    ax.set_ylim(14.0, 30.5)
    ax.set_aspect('equal')
    ax.set_title(f'Keeper beam: actual layer Z={selected:g}')
    ax.set_xlabel('Print X (mm)')
    ax.set_ylabel('Print Y (mm)')
    ax.grid(alpha=0.2)
    fig.suptitle('Native coupon toolpaths · orange is removable support; teal is the thin keeper beam', fontsize=13)
    fig.savefig(HERE / 'toolpath-review.svg', dpi=160)
    fig.savefig(JOB / 'toolpath-review.png', dpi=160)
    plt.close(fig)
    result = {
        'status': 'pass' if not errors else 'fail', 'errors': errors,
        'gcode_sha256': readiness['gcode_sha256'],
        'method': 'Actual extrusion segments buffered by half commanded line width in each layer. '
                  'No extrusion sag, shrinkage, adhesion or material strength is simulated.',
        'keeper_beam': readings,
        'actual_model_nozzle_bed_c': {'first_layer': layer_temperatures.get(1),
                                     'subsequent_layers': [280.0, 80.0],
                                     'model_layers_read': len(layer_temperatures)},
        'native_stock_template_parser_diagnostics': parser_messages,
        'diagnostic_scope': 'These three unrecognized H2C template T commands also occur in retained successful '
                            'jobs. Native slicing reports Success with no geometry warning; no command was removed.',
        'minimum_keeper_beam_road_width_mm': min((row['beam_road_width_mm'] for row in readings), default=None),
        'minimum_keeper_open_gap_mm': min((row['open_gap_to_spine_mm'] for row in readings), default=None),
        'support_lanes': lanes,
        'physical_removal_and_fit': 'Not yet observed; remove supports and examine actual bearing finish before assembly.',
    }
    output = HERE / 'toolpath-review.json'
    output.write_text(json.dumps(result, indent=2) + '\n')
    if errors:
        readiness['status'] = 'coupon_toolpath_review_failed'
    elif not readiness.get('submitted'):
        readiness['status'] = 'ready_for_coupon_print'
    readiness['toolpath_review'] = str(output.relative_to(ROOT))
    readiness['toolpath_review_sha256'] = hashlib.sha256(output.read_bytes()).hexdigest()
    readiness['geometry_not_strength_qualification'] = True
    (HERE / 'print-readiness.json').write_text(json.dumps(readiness, indent=2) + '\n')
    (JOB / 'readiness.json').write_text(json.dumps(readiness, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ('status', 'errors',
                     'minimum_keeper_beam_road_width_mm', 'minimum_keeper_open_gap_mm')}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
