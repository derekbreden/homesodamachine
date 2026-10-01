"""Measure native bead overlap and the roof-down part's scoped wall count."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
from shapely.geometry import LineString
from shapely.ops import unary_union
from prepare_prints import JOBS

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools').is_dir())
sys.path.insert(0, str(ROOT / 'hardware/printed-parts/enclosure/nameplate'))
from verify_mark2_print import segments


def main(part):
    job = ROOT / '.cache/prints' / JOBS[part][3]
    path = job / 'ready/plate_1.gcode'
    preparation = json.loads((job / 'preparation.json').read_text())
    back = part == 'back-top'
    cross_y = preparation['parts'][0]['plate_translation_mm'][1]
    roads, crossings = {}, {}
    sample_z = (.2, .44, 2.6, 5., 9.08, 9.8)
    for row in segments(path):
        if row['layer'] > (10 if back else .69):
            break
        if row['object'] != 1901 or row['feature'] in ('Brim', 'Support', 'Support interface', 'Custom', 'Prime tower'):
            continue
        z = row['layer']
        if z <= .68:
            roads.setdefault(z, []).append(row)
        if back and z in sample_z and row['feature'] in ('Outer wall', 'Inner wall', 'Overhang wall'):
            a, b = row['a'], row['b']
            if min(a[1], b[1]) < cross_y < max(a[1], b[1]):
                x = a[0] + (cross_y-a[1]) / (b[1]-a[1]) * (b[0]-a[0])
                if x < 60 or x > 265:
                    crossings.setdefault(z, []).append({'x_mm': round(x, 4), 'feature': row['feature'], 'width_mm': row['width']})
    zs = sorted(roads)
    assert zs == [.2, .44, .68], zs
    def surface(rows):
        return unary_union([LineString((r['a'], r['b'])).buffer(r['width']/2) for r in rows])
    transitions = []
    for az, bz in zip(zs, zs[1:]):
        lower = surface(roads[az])
        outer = [r for r in roads[bz] if r['feature'] in ('Outer wall', 'Overhang wall')
                 and (not back or max(r['a'][0], r['b'][0]) < 64 or min(r['a'][0], r['b'][0]) > 261)]
        upper = surface(outer)
        points = [LineString((r['a'], r['b'])).interpolate(i/10, normalized=True) for r in outer for i in range(11)]
        reading = {'from_z': az, 'to_z': bz, 'outer_wall_area_fraction_supported': lower.intersection(upper).area/upper.area,
                   'max_sampled_outer_centerline_unsupported_mm': max(p.distance(lower) for p in points)}
        assert reading['outer_wall_area_fraction_supported'] > .60 and reading['max_sampled_outer_centerline_unsupported_mm'] < .05, reading
        transitions.append(reading)
    counts = []
    if back:
        for z in sample_z:
            rows = crossings[z]
            west, east = sum(r['x_mm'] < 60 for r in rows), sum(r['x_mm'] > 265 for r in rows)
            expected = 6 if z < 9.4 else 2
            assert west == east == expected, (z, rows)
            counts.append({'z_mm': z, 'west_wall_count': west, 'east_wall_count': east})
    result = {'pass': True, 'gcode_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'first_layer_height_mm': .2, 'next_layer_height_mm': .24, 'transitions': transitions,
              'surface': 'Both expanding roof-side edges within 9 mm of the X bounds.' if back else 'Front-top mouth-down datum and rails; no expanding bottom round.',
              'wall_count_samples': counts, 'wall_crossing_y_mm': cross_y if back else None,
              'wall_crossings': crossings}
    (job / 'first-layer-overlap.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('pass', 'transitions', 'wall_count_samples')}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('part', choices=JOBS)
    main(parser.parse_args().part)
