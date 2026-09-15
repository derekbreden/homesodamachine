#!/usr/bin/env python3
"""Read Bambu G-code and measure support/ceiling deposition inside coupon ROIs.

--regions is a JSON list (or {"regions": [...]}) of rectangular interiors:
  {"id":"A1", "x_min":25,"x_max":65,"y_min":25,"y_max":65,
   "ceiling_z":48.2,"model_layer_height":0.24,"expected_top_gap":0.30}

Use a central ROI inside every wall/ceiling edge. Gap is NOT merely the
difference of consecutive nozzle Z coordinates: subtract the deposited model
layer height, too. This does not measure real-world strand sag or fusion.
"""
import argparse
import collections
import contextlib
import io
import json
import math
import re
import sys
import zipfile

TOKEN = re.compile(r"([A-Z])\s*([-+]?(?:\d*\.\d+|\d+\.?\d*))", re.I)
EPS = 1e-7


def clipped_length(a, b, box):
    """Liang-Barsky: portion of line inside an axis-aligned rectangle."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    lo, hi = 0.0, 1.0
    for p, q in ((-dx, a[0] - box['x_min']),
                 (dx, box['x_max'] - a[0]),
                 (-dy, a[1] - box['y_min']),
                 (dy, box['y_max'] - a[1])):
        if abs(p) < EPS:
            if q < 0:
                return 0.0
        else:
            t = q / p
            if p < 0:
                lo = max(lo, t)
            else:
                hi = min(hi, t)
            if lo > hi:
                return 0.0
    return math.hypot(dx, dy) * max(0.0, hi - lo)


def paths(start, end, command, args):
    """Approximate G17 I/J arcs to <=0.5mm chords; normal moves stay exact."""
    if command not in ('G2', 'G3') or not ('I' in args or 'J' in args):
        yield start[:2], end[:2]
        return
    cx, cy = start[0] + args.get('I', 0), start[1] + args.get('J', 0)
    radius = math.hypot(start[0] - cx, start[1] - cy)
    a0 = math.atan2(start[1] - cy, start[0] - cx)
    a1 = math.atan2(end[1] - cy, end[0] - cx)
    da = (a1 - a0) % (2 * math.pi)
    if command == 'G2':
        da = -((a0 - a1) % (2 * math.pi))
    if abs(da) < EPS:
        da = 2 * math.pi * (-1 if command == 'G2' else 1)
    n = max(1, math.ceil(abs(da) * radius / 0.5))
    previous = start[:2]
    for i in range(1, n + 1):
        angle = a0 + da * i / n
        following = end[:2] if i == n else (cx + radius * math.cos(angle), cy + radius * math.sin(angle))
        yield previous, following
        previous = following


@contextlib.contextmanager
def source(path):
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            candidates = [x for x in z.namelist() if x.endswith('.gcode')]
            if len(candidates) != 1:
                raise ValueError(f'Expected one G-code member, got {candidates}')
            with z.open(candidates[0]) as raw:
                yield io.TextIOWrapper(raw, encoding='utf8', errors='replace')
    else:
        with open(path, encoding='utf8', errors='replace') as f:
            yield f


def audit(stream, regions):
    position = [0.0, 0.0, 0.0]
    absolute = True
    e_absolute = False
    last_e = 0.0
    feature = ''
    layer_height = None
    started = False
    lowest = min(r['ceiling_z'] - 3.5 for r in regions)
    highest = max(r['ceiling_z'] + r['model_layer_height'] * 2 + .05 for r in regions)
    records = [{"interface": collections.defaultdict(float),
                "ceiling": collections.defaultdict(float),
                "base": collections.defaultdict(float),
                "height_comments": collections.defaultdict(set),
                "features": collections.defaultdict(set)} for _ in regions]
    for line_number, line in enumerate(stream, 1):
        text = line.strip()
        if text == '; CHANGE_LAYER':
            started = True
        elif text.startswith('; FEATURE:'):
            feature = text.split(':', 1)[1].strip()
        elif text.startswith('; LAYER_HEIGHT:'):
            layer_height = float(text.split(':', 1)[1])
        code = text.split(';', 1)[0].strip()
        if not code:
            continue
        command = code.split(None, 1)[0].upper()
        args = {k.upper(): float(v) for k, v in TOKEN.findall(code[len(command):])}
        if command == 'G90':
            absolute = True
        elif command == 'G91':
            absolute = False
        elif command == 'M82':
            e_absolute = True
        elif command == 'M83':
            e_absolute = False
        elif command == 'G92':
            for i, axis in enumerate('XYZ'):
                if axis in args:
                    position[i] = args[axis]
            if 'E' in args:
                last_e = args['E']
        elif command in ('G0', 'G1', 'G2', 'G3'):
            start = tuple(position)
            for i, axis in enumerate('XYZ'):
                if axis in args:
                    position[i] = args[axis] if absolute else position[i] + args[axis]
            e_delta = 0
            if 'E' in args:
                e_delta = args['E'] - last_e if e_absolute else args['E']
                last_e = args['E'] if e_absolute else last_e + args['E']
            if not started or e_delta <= EPS:
                continue
            end = tuple(position)
            if not ('X' in args or 'Y' in args or command in ('G2', 'G3')):
                continue
            z = round(end[2], 5)
            if not lowest <= z <= highest:
                continue
            for r, rec in zip(regions, records):
                if z < r['ceiling_z'] - 3.5 or z > r['ceiling_z'] + r['model_layer_height'] * 2 + .05:
                    continue
                amount = sum(clipped_length(a, b, r) for a, b in paths(start, end, command, args))
                if amount < .02:
                    continue
                if feature.lower() == 'support interface':
                    key = 'interface'
                elif feature.lower().startswith('support'):
                    key = 'base'
                elif z >= r['ceiling_z'] - .01 and feature.lower() not in ('skirt', 'brim', 'prime tower', 'wipe tower', 'custom'):
                    key = 'ceiling'
                else:
                    continue
                rec[key][z] += amount
                rec['height_comments'][z].add(layer_height)
                rec['features'][z].add(feature)

    results = []
    for r, rec in zip(regions, records):
        result = dict(r)
        # Reject edge flecks as decisive measurements; require at least 2mm path.
        interface_zs = [z for z, length in rec['interface'].items() if length >= 2]
        ceiling_zs = [z for z, length in rec['ceiling'].items() if length >= 2]
        top = max(interface_zs, default=None)
        first = min(ceiling_zs, default=None)
        result.update(final_interface_z=top, first_ceiling_tool_z=first,
                      observed_interface_layers=len(interface_zs))
        if top is not None and first is not None:
            gap = round(first - r['model_layer_height'] - top, 5)
            result['planned_deposition_gap_mm'] = gap
            result['cad_ceiling_gap_mm'] = round(r['ceiling_z'] - top, 5)
            result['ceiling_tool_z_minus_interface_z'] = round(first - top, 5)
            if 'expected_top_gap' in r:
                result['gap_matches_requested_within_0_015mm'] = abs(gap - r['expected_top_gap']) <= .015
                result['gap_quantization_mm'] = round(gap - r['expected_top_gap'], 5)
            result['positive_planned_deposition_gap'] = gap > 0
        else:
            result['error'] = 'No substantial support interface or ceiling extrusion inside ROI'
        if 'expected_interface_layers' in r:
            result['interface_layer_count_matches'] = len(interface_zs) == r['expected_interface_layers']
        for key in ('interface', 'base', 'ceiling'):
            result[key + '_paths_by_z'] = [
                {'z': z, 'length_mm': round(length, 3),
                 'layer_height_comments': sorted(h for h in rec['height_comments'][z] if h is not None),
                 'features': sorted(rec['features'][z])}
                for z, length in sorted(rec[key].items())]
        results.append(result)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gcode', required=True)
    parser.add_argument('--regions', required=True)
    args = parser.parse_args()
    with open(args.regions) as f:
        regions = json.load(f)
    if isinstance(regions, dict):
        regions = regions['regions']
    with source(args.gcode) as stream:
        results = audit(stream, regions)
    groups = collections.defaultdict(set)
    for r in results:
        if 'expected_top_gap' in r and 'planned_deposition_gap_mm' in r:
            groups[r['expected_top_gap']].add(r['planned_deposition_gap_mm'])
    group_summary = [{'requested_gap_mm': nominal, 'actual_gaps_mm': sorted(actual)}
                     for nominal, actual in sorted(groups.items())]
    consistent = all(len(actual) == 1 for actual in groups.values())
    distinct = len({gap for actual in groups.values() for gap in actual}) == len(groups)
    valid = consistent and distinct and all(
        'error' not in r and r.get('positive_planned_deposition_gap', False)
        and r.get('interface_layer_count_matches', True) for r in results)
    print(json.dumps({'gcode': args.gcode, 'valid_gap_and_layer_experiment': valid,
                      'requested_gap_groups_are_consistent': consistent,
                      'requested_gap_groups_remain_distinct': distinct,
                      'gap_groups': group_summary, 'regions': results}, indent=2))
    return 0 if valid else 1


if __name__ == '__main__':
    sys.exit(main())
