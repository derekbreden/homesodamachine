"""Read support deposition above Derek's two front-top seam-land picks.

The support's full road width and actual emitted height are included. A location
reading is not physical cleanup qualification. No archive is modified.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

import numpy as np
import trimesh
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'tools').is_dir())
sys.path.insert(0, str(ROOT / 'hardware/scripts'))
from enclosure_support_audit import _WORD

PICKS = ((105.690, 34.793, 165.194), (82.129, 7.118, 165.194))


def segments(path, maximum_z):
    x = y = e = 0.
    z = height = None
    width = .62
    feature = ''
    obj = None
    absolute = relative_e = True
    for number, raw in enumerate(path.open(), 1):
        text = raw.strip()
        if text.startswith('; Z_HEIGHT:'):
            z = float(text.split(':', 1)[1]); obj = None; feature = ''
            if z > maximum_z:
                break
        elif text.startswith('; LAYER_HEIGHT:'):
            height = float(text.split(':', 1)[1])
        elif text.startswith('; LINE_WIDTH:'):
            width = float(text.split(':', 1)[1])
        elif text.startswith('; FEATURE:'):
            feature = text.split(':', 1)[1].strip()
        elif text.startswith('; stop printing object'):
            obj = None
        match = re.match(r'; (?:start printing object, unique label id:|OBJECT_ID:)\s*(-?\d+)', text)
        if match:
            obj = int(match[1])
        code = text.split(';', 1)[0].strip()
        if not code:
            continue
        command = code.split()[0]
        words = {key: float(value) for key, value in _WORD.findall(code)}
        if command in ('G90', 'G91'):
            absolute = command == 'G90'
        elif command in ('M82', 'M83'):
            relative_e = command == 'M83'
        elif command == 'G92':
            x, y, e = words.get('X', x), words.get('Y', y), words.get('E', e)
        elif command in ('G0', 'G1', 'G2', 'G3'):
            nx = words.get('X', x) if absolute else x + words.get('X', 0.)
            ny = words.get('Y', y) if absolute else y + words.get('Y', 0.)
            de = words.get('E', 0.) if relative_e else words.get('E', e) - e
            if de > 1e-9 and (nx != x or ny != y) and obj == 1901 and z is not None:
                assert command in ('G0', 'G1'), 'Arc fitting must remain disabled.'
                yield dict(line=number, z=z, bottom_z=z-height, height=height,
                           width=width, feature=feature, a=(x, y), b=(nx, ny))
            x, y = nx, ny
            if 'E' in words:
                e = e + words['E'] if relative_e else words['E']


def check(gcode, stl, translation, radius=7.):
    mesh = trimesh.load_mesh(stl, process=False)
    planar = (mesh.face_normals[:, 2] > .999) & (np.max(np.abs(mesh.triangles[:, :, 2]-165.195), axis=1) < .002)
    assert planar.any()
    stock = unary_union([Polygon(triangle[:, :2]+translation[:2]) for triangle in mesh.triangles[planar]])
    windows = [stock.intersection(Point(np.array(point[:2])+translation[:2]).buffer(radius)) for point in PICKS]
    assert all(not window.is_empty for window in windows)
    plane_z = 165.195 + translation[2]
    findings = [dict(pick_cad_xyz_mm=list(point), native_surface_z_mm=165.195,
                     window_radius_mm=radius, first_overlying_support=None,
                     last_model_top_surface_z_mm=None) for point in PICKS]
    for road in segments(gcode, plane_z+3.):
        if road['z'] < plane_z-.3:
            continue
        footprint = LineString((road['a'], road['b'])).buffer(road['width']/2.)
        for window, finding in zip(windows, findings):
            overlap = footprint.intersection(window).area
            if overlap <= 1e-5:
                continue
            if road['feature'].startswith('Support') and road['bottom_z'] >= plane_z-.05:
                item = dict(road, overlap_native_land_mm2=overlap,
                            gap_above_native_surface_mm=road['bottom_z']-plane_z)
                previous = finding['first_overlying_support']
                if previous is None or item['bottom_z'] < previous['bottom_z']:
                    finding['first_overlying_support'] = item
            elif road['feature'] == 'Top surface' and abs(road['z']-plane_z) < .3:
                previous = finding['last_model_top_surface_z_mm']
                finding['last_model_top_surface_z_mm'] = max(previous or 0., road['z'])
    for finding in findings:
        support = finding['first_overlying_support']
        top = finding['last_model_top_surface_z_mm']
        finding['support_gap_above_emitted_top_mm'] = None if support is None or top is None else support['bottom_z']-top
        finding['support_absent_over_window'] = support is None
    deposited_model = [[] for _ in findings]
    touching_support = [[] for _ in findings]
    for road in segments(gcode, plane_z+3.):
        if road['z'] < plane_z-.3:
            continue
        footprint = LineString((road['a'], road['b'])).buffer(road['width']/2.)
        for index, (window, finding) in enumerate(zip(windows, findings)):
            top = finding['last_model_top_surface_z_mm']
            if top is None:
                continue
            if not road['feature'].startswith('Support') and abs(road['z']-top) < 1e-6:
                deposited_model[index].append(footprint.intersection(window))
            elif road['feature'].startswith('Support') and top-.01 <= road['bottom_z'] <= top+1e-6 \
                    and road['z'] > top:
                touching_support[index].append(footprint.intersection(window))
    for finding, model, support in zip(findings, deposited_model, touching_support):
        stock, feet = unary_union(model), unary_union(support)
        finding['touching_support_emitted_model_overlap_mm2'] = feet.intersection(stock).area
        finding['emitted_xy_gap_at_top_mm'] = None if feet.is_empty else feet.distance(stock)
        finding['touching_support_absent_over_window'] = feet.is_empty
    return dict(schema=1, gcode_sha256=hashlib.sha256(gcode.read_bytes()).hexdigest(),
                source_stl_sha256=hashlib.sha256(stl.read_bytes()).hexdigest(),
                machine_to_bed_translation_mm=translation, picks=findings,
                method='Actual support slab bottom (emitted Z minus emitted road height) and full road-width footprints against native +Z seam land and all actual model beads at its emitted top within each picked window.',
                scope='Emitted separation or absence at the reported locations only; no physical support-removal or surface-finish qualification.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('gcode', type=Path)
    parser.add_argument('stl', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--translation', type=float, nargs=3, required=True)
    args = parser.parse_args()
    record = check(args.gcode, args.stl, args.translation)
    args.output.write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(record['picks'], indent=2))
