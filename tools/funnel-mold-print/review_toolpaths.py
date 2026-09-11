"""Read commanded outer-wall speeds, cooling and seam positions from sliced molds.

The report describes the emitted G-code. It does not establish adhesion,
temperature at the deposited filament, or successful physical printing.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import zipfile


def outer_blocks(data):
    blocks = []
    block = None
    x = y = feed = fan = z = height = 0.0
    layer = 0
    feature = ''
    for raw in data.splitlines():
        if raw.startswith('; layer num/total_layer_count:'):
            layer = int(raw.split(':')[-1].split('/')[0])
        elif raw.startswith('; Z_HEIGHT:'):
            z = float(raw.split(':')[-1])
        elif raw.startswith('; LAYER_HEIGHT:'):
            height = float(raw.split(':')[-1])
        elif raw.startswith('; FEATURE:'):
            feature = raw.split(':', 1)[1].strip()
            block = None
            if feature in ('Outer wall', 'Overhang wall') and layer:
                block = {'layer': layer, 'z_mm': z, 'height_mm': height,
                         'start_xy_mm': [x, y], 'segments': []}
                blocks.append(block)
        line = raw.split(';')[0]
        if line.startswith('M106'):
            p = re.search(r'\bP(\d+)', line)
            s = re.search(r'\bS([\d.]+)', line)
            if s and (not p or p[1] == '1'):
                fan = float(s[1])*100/255
        if re.match(r'G[01] ', line):
            values = {key: float(value) for key, value in
                      re.findall(r'\b([XYEF])(-?[\d.]+)', line)}
            old_x, old_y = x, y
            x, y = values.get('X', x), values.get('Y', y)
            feed = values.get('F', feed)
            length = math.hypot(x-old_x, y-old_y)
            if block is not None and values.get('E', 0) > 0 and length > 1e-5:
                block['segments'].append([old_x, old_y, x, y, feed/60, fan, length])
    return [b for b in blocks if b['segments']]


def summarize(block):
    segments = block['segments']
    xs = [s[i] for s in segments for i in (0, 2)]
    ys = [s[i] for s in segments for i in (1, 3)]
    return {key: value for key, value in block.items() if key != 'segments'} | {
        'xy_bounds_mm': [min(xs), min(ys), max(xs), max(ys)],
        'commanded_speed_mm_s': sorted({round(s[4], 3) for s in segments}),
        'commanded_fan_percent': sorted({round(s[5], 1) for s in segments}),
        'length_mm': sum(s[6] for s in segments),
        'seam_distance_from_rearmost_y_mm': max(ys)-block['start_xy_mm'][1]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {'project': args.project.name,
              'project_sha256': hashlib.sha256(args.project.read_bytes()).hexdigest(),
              'scope': 'Commanded paths; physical extrusion quality remains a print observation.',
              'plates': []}
    with zipfile.ZipFile(args.project) as archive:
        settings = json.loads(archive.read('Metadata/project_settings.config'))
        cap = max(map(float, settings['outer_wall_speed']))
        for name in sorted(archive.namelist()):
            if not re.fullmatch(r'Metadata/plate_\d+\.gcode', name):
                continue
            data = archive.read(name)
            blocks = outer_blocks(data.decode())
            regular = [b for b in blocks if b['layer'] > 3]
            speed = max(s[4] for b in regular for s in b['segments'])
            assert speed <= cap+0.02, (name, speed, cap)
            fan_min = min(s[5] for b in regular for s in b['segments'])
            if settings['overhang_fan_threshold'] == ['0%']:
                target = float(settings['overhang_fan_speed'][0])
                assert fan_min >= target-0.1, (name, fan_min, target)
            exterior = {}
            for block in regular:
                summary = summarize(block)
                # The exterior loop is the longest closed outer perimeter at this layer.
                old = exterior.get(block['layer'])
                if old is None or summary['length_mm'] > old['length_mm']:
                    exterior[block['layer']] = summary
            report['plates'].append({'gcode': name,
                'gcode_sha256': hashlib.sha256(data).hexdigest(),
                'outer_wall_speed_limit_mm_s': cap,
                'maximum_commanded_outer_wall_speed_after_layer_3_mm_s': speed,
                'minimum_commanded_outer_wall_fan_after_layer_3_percent': fan_min,
                'exterior_perimeters': list(exterior.values())})
            print(name, len(exterior), 'layers;', speed, 'mm/s maximum outer wall')
    args.output.write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
