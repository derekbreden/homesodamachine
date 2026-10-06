"""Read native bead overlap at the flat bases/corbels and air at breather tips."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'hardware/scripts').is_dir())
HERE = ROOT/'.cache/funnel-gyroid-2026-10-05'
PUBLIC = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'hardware/scripts'))
import enclosure_support_audit as support


def read(raw, targets):
    x = y = e = 0.
    z = None
    width = .42
    relative_e = absolute_xy = True
    feature = ''
    model = defaultdict(list)
    outer = defaultdict(list)
    for rawline in raw.decode().splitlines():
        if rawline.startswith('; Z_HEIGHT:'):
            z = float(rawline.split(':')[1])
        elif rawline.startswith('; LINE_WIDTH:'):
            width = float(rawline.split(':')[1])
        elif rawline.startswith('; FEATURE:'):
            feature = rawline.split(':', 1)[1].strip()
        code = rawline.partition(';')[0].strip()
        if not code:
            continue
        command = code.split()[0]
        words = {k: float(v) for k, v in support._WORD.findall(code)}
        if command == 'M82': relative_e = False; continue
        if command == 'M83': relative_e = True; continue
        if command == 'G90': absolute_xy = True; continue
        if command == 'G91': absolute_xy = False; continue
        if command == 'G92':
            x, y, e = words.get('X', x), words.get('Y', y), words.get('E', e)
            continue
        if command not in ('G0', 'G1', 'G2', 'G3'):
            continue
        nx = words.get('X', x) if absolute_xy else x+words.get('X', 0)
        ny = words.get('Y', y) if absolute_xy else y+words.get('Y', 0)
        de = words.get('E', 0) if relative_e else words.get('E', e)-e
        if z in targets and de > 1e-9 and (nx, ny) != (x, y) and feature not in (
                '', 'Custom', 'Flush', 'Skirt', 'Brim', 'Wipe tower') and not feature.startswith('Support'):
            points = [(nx, ny)] if command in ('G0', 'G1') else support._arc_points(
                (x, y), (nx, ny), words, command == 'G2')
            bead = LineString([(x, y), *points]).buffer(width/2, quad_segs=8)
            model[z].append(bead)
            if feature in ('Outer wall', 'Overhang wall'):
                outer[z].append(bead)
        x, y = nx, ny
        if 'E' in words:
            e = e+words['E'] if relative_e else words['E']
    return ({z: unary_union(v) for z, v in model.items()},
            {z: unary_union(v) for z, v in outer.items()})


def main():
    project = HERE/'slice/current-funnel-mould-petg088.gcode.3mf'
    rows = []
    with zipfile.ZipFile(project) as archive:
        for index, name in enumerate(('cavity', 'core'), 1):
            raw = archive.read(f'Metadata/plate_{index}.gcode')
            layers = sorted(set(float(z) for z in re.findall(rb'; Z_HEIGHT: ([\d.]+)', raw)))
            first, second = layers[:2]
            a, b = (min(layers, key=lambda z: abs(z-target)) for target in (5.24, 5.48))
            # Independent support layers have their own Z schedule. Select a
            # model layer using the saved 0.20/0.24 mm model schedule.
            target = 2.5 if name == 'cavity' else 1.8
            drill_z = round(.20+.24*round((target-.20)/.24), 2)
            model, outer = read(raw, {first, second, a, b, drill_z})
            base_overlap = model[second].intersection(model[first].buffer(.05)).area/model[second].area
            assert base_overlap > .98, (name, base_overlap)
            if name == 'cavity':
                window = box(149.5+82, 140, 149.5+85, 180)
                tips = [(70.275, 130), (228.725, 190)]
            else:
                center = Point(151.35, 160)
                radius = 20.5425-b*.5
                window = center.buffer(radius+1).difference(center.buffer(radius-1))
                tips = [(109.5, 190), (189.5, 130)]
            new_bead = outer[b].intersection(window)
            assert new_bead.area > 1
            transition_overlap = new_bead.intersection(model[a]).area/new_bead.area
            assert transition_overlap > .65, (name, transition_overlap)
            breathers = []
            for x, y in tips:
                # Native paths leave air within the 1.5 mm drill's end window.
                probe = Point(x, y).buffer(.75, quad_segs=16)
                air_area = probe.difference(model[drill_z]).area
                assert air_area > .1, (name, x, y, air_area)
                breathers.append({'tip_bed_xy_mm': [x, y], 'nearby_layer_z_mm': drill_z,
                    'unfilled_tip_window_area_mm2': air_area})
            rows.append({'part': name, 'gcode_sha256': hashlib.sha256(raw).hexdigest(),
                'first_layer_z_mm': first, 'second_layer_z_mm': second,
                'second_layer_nominal_bead_overlap_fraction': base_overlap,
                'base_overlap_tolerance_mm': .05,
                'corbel_layers_z_mm': [a, b], 'corbel_outer_bead_overlap_fraction': transition_overlap,
                'breather_windows': breathers})
    result = {'project_sha256': hashlib.sha256(project.read_bytes()).hexdigest(),
        'method': 'Native deposited model paths buffered by half emitted line width, including arcs; support excluded.',
        'scope': 'Nominal first/second layer and steep-transition bead overlap, plus open air at specified breather depths in the native sparse slice. Extrusion adhesion and finished print leakage are physical observations.',
        'plates': rows, 'passed': True}
    (PUBLIC/'bead-review.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
