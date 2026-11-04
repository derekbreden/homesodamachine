"""Measure the prepared PP1208E at native MINI 2 scale.

Table height and axial/radial bounds select the specimen before any model exists.
The fitting's panel seat is Y0, with +Y outboard; the nut keeps its captured pose.
"""
from pathlib import Path
import importlib.util
import json
import sys

import numpy as np
from scipy.ndimage import median_filter
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
ARCHIVE = Path.home() / 'Documents/3D Scans/2026-11-03-jg-pp1208e-bulkhead'
HELPERS = HERE.parent / 'yzmsz-water-regulator/analyze_scan.py'
spec = importlib.util.spec_from_file_location('pp1208e_scan_helpers', HELPERS)
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
sys.path.insert(0, str(HERE.parent / 'g-ganen-pump'))
from scan_tools import load_cloud, plane, stats, unit


def end_axis(p, n, height):
    radial = np.hypot(p[:, 1], p[:, 2])
    facing = (p[:, 1]*n[:, 1]+p[:, 2]*n[:, 2])/np.maximum(radial, 1e-8)
    hit = ((abs(p[:, 0]) > 13) & (abs(p[:, 0]) < 24) & (height > 16)
           & (radial < 9) & (abs(n[:, 0]) < .3) & (facing > .8))
    q, nn = p[hit][::3], n[hit][::3]
    length = np.hypot(nn[:, 1], nn[:, 2])
    x = q[:, 0]

    def residual(v):
        return (nn[:, 2]*(q[:, 1]-v[0]-v[2]*x)
                -nn[:, 1]*(q[:, 2]-v[1]-v[3]*x))/length

    fit = least_squares(residual, [0, -1, 0, 0], loss='soft_l1', f_scale=.06)
    axis = unit([1, *fit.x[2:]])
    z = unit(np.array([0, 0, 1])-axis*axis[2])
    rotation = np.array([axis, np.cross(z, axis), z])
    origin = np.array([0, *fit.x[:2]])
    return origin, rotation, {
        'samples': len(q), 'axis_point_initial_mm': origin.tolist(),
        'axis_direction_initial': axis.tolist(), 'normal_ray_residual_mm': stats(fit.fun),
        'selection': 'Initial |X| 13..24 mm; table height >16 mm; radius <9 mm; '
                     '|normal.X|<0.3; outward radial normal >0.8; every third point',
    }


def hex_fit(p, n, lo, hi):
    radial = np.hypot(p[:, 1], p[:, 2])
    facing = (p[:, 1]*n[:, 1]+p[:, 2]*n[:, 2])/np.maximum(radial, 1e-8)
    theta = np.arctan2(n[:, 2], n[:, 1])
    hit = ((p[:, 0] > lo) & (p[:, 0] < hi) & (abs(n[:, 0]) < .15)
           & (radial > 8) & (facing > .85))
    phase = np.angle(np.mean(np.exp(6j*theta[hit])))/6
    rows, patches = [], []
    for k in range(6):
        a = phase+k*np.pi/3
        selected = hit & (abs(np.angle(np.exp(1j*(theta-a)))) < np.radians(2))
        if selected.sum() < 100:
            continue
        center, normal, residual = plane(p[selected])
        normal *= np.sign(normal @ n[selected].mean(0))
        rows.append({'normal': normal.tolist(), 'offset_mm': float(normal @ center),
                     'samples': int(selected.sum()), 'plane_residual_mm': residual})
        patches.append((a, p[selected][::3, 1:3]))

    # A regular wrench envelope: equal total weight per exposed flat. Robust loss
    # prevents molded lettering on a flat from defining the wrench's base plane.
    def residual(v):
        cy, cz, apothem, turn = v
        return np.concatenate([
            ((q[:, 0]-cy)*np.cos(a+turn)+(q[:, 1]-cz)*np.sin(a+turn)-apothem)
            /np.sqrt(len(q)) for a, q in patches])

    fit = least_squares(residual, [0, 0, 10 if lo < 0 else 9.5, 0],
                        loss='soft_l1', f_scale=.003,
                        bounds=([-2, -2, 8, -.12], [2, 2, 12, .12]))
    cy, cz, apothem, turn = fit.x
    return {'axial_selection_mm': [lo, hi], 'planes': rows,
            'across_flats_mm': float(2*apothem), 'center_yz_mm': [float(cy), float(cz)],
            'vertex_clock_degrees': float(np.degrees(phase+turn)-30),
            'method': 'Six-fold normal clustering; regular hex fit with equal weight per '
                      'exposed flat and soft-L1 loss; molded marks retained in model comparison.'}


def axial_face(p, n, selection):
    lo, hi, rlo, rhi, sign = selection
    radius = np.hypot(p[:, 1], p[:, 2])
    hit = ((p[:, 0] > lo) & (p[:, 0] < hi) & (radius > rlo)
           & (radius < rhi) & (n[:, 0]*sign > .95))
    center, normal, residual = plane(p[hit])
    normal *= np.sign(normal @ n[hit].mean(0))
    return {'axis_station_mm': float((normal @ center)/normal[0]),
            'normal': normal.tolist(), 'samples': int(hit.sum()),
            'plane_residual_mm': residual, 'selection_x_radius_sign': list(selection)}


def profile(p, n, lo, hi):
    radius = np.hypot(p[:, 1], p[:, 2])
    facing = (p[:, 1]*n[:, 1]+p[:, 2]*n[:, 2])/np.maximum(radius, 1e-8)
    rows = []
    for x in np.arange(lo+.0625, hi, .125):
        hit = (abs(p[:, 0]-x) < .0625) & (facing > .1)
        if hit.sum() >= 12:
            rows.append({'x_mm': float(x), 'samples': int(hit.sum()),
                         'radius_p05_p50_p975_mm': np.quantile(radius[hit], [.05, .5, .975]).tolist()})
    outline = np.array([[row['x_mm'], row['radius_p05_p50_p975_mm'][2]] for row in rows])
    outline[:, 1] = median_filter(outline[:, 1], 3, mode='nearest')
    outline = np.vstack([[lo, outline[0, 1]], outline, [hi, outline[-1, 1]]])
    return [[round(x, 5), round(r, 5)] for x, r in common.simplify(outline, .035)], rows


def main():
    manifest = json.loads((ARCHIVE/'capture-manifest.json').read_text())
    capture = manifest['passes'][0]
    raw_path = Path(capture['native_project_archive'])/'raw_preview.ply'
    raw_sha = next(f['sha256'] for f in capture['native_files'] if f['file'] == 'raw_preview.ply')
    raw, _, raw_meta = load_cloud(raw_path, raw_sha)
    p, n, fused_meta = load_cloud(capture['cloud'], capture['sha256'])
    tc, tr, pc, pr, table_residual = common.initial_frame(raw)
    table = (p-tc) @ tr.T
    initial = (table-pc) @ pr.T
    origin, rotation, axis_evidence = end_axis(initial, n @ tr.T @ pr.T, table[:, 2])
    q = (initial-origin) @ rotation.T
    nn = n @ tr.T @ pr.T @ rotation.T
    radius = np.hypot(q[:, 1], q[:, 2])
    keep = (table[:, 2] > 17) & (q[:, 0] > -23) & (q[:, 0] < 19) & (radius < 13.5)
    q, nn = q[keep], nn[keep]
    faces = {name: axial_face(q, nn, selection) for name, selection in {
        'panel_seat': (4.3, 5.0, 8.5, 10, -1),
        'nut_front': (-1.3, -.6, 8.8, 10, 1),
        'nut_back': (-6.8, -6.1, 8.5, 10.3, -1),
        'outboard_mouth': (16.1, 16.65, 3.7, 4.5, 1),
        'inboard_mouth': (-21.65, -21.0, 3.7, 4.5, -1),
    }.items()}
    station = lambda name: faces[name]['axis_station_mm']
    seat, near, far = [station(name) for name in ('panel_seat', 'outboard_mouth', 'inboard_mouth')]
    body_hex, nut_hex = hex_fit(q, nn, 7.5, 10.3), hex_fit(q, nn, -5.5, -3)
    curves, samples = {}, {}
    for name, lo, hi in [('outboard', seat, near), ('inboard', far, -17.0),
                          ('nut', station('nut_back'), station('nut_front'))]:
        curves[name], samples[name] = profile(q, nn, lo, hi)

    permutation = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
    native = q @ permutation.T - [0, seat, 0]
    native_n = nn @ permutation.T
    out = ARCHIVE/'registered-pp1208e.ply'
    common.write_cloud(out, native, native_n)
    transform = np.eye(4)
    transform[:3, :3] = permutation @ rotation @ pr @ tr
    transform[:3, 3] = permutation @ (rotation @ (-pr @ (tr @ tc+pc)-origin)) - [0, seat, 0]
    limits = [
        'Paint thickness and absolute optical scale are not independently calibrated.',
        'Putty-hidden lower sectors continue the fitted turned and hexagonal forms.',
        'The barrel uses a smooth thread-crest envelope; grooves and hidden engagement are omitted.',
        'Collet finger slots and molded marks are omitted; the bore and mouth bevels are display geometry.',
        'Exposed release-face planes are representative coaxial datums; captured free collets may tilt.',
        'The captured nut position is separate from the installed clamp stack.',
    ]
    evidence = {'units': 'mm', 'coordinate_scale_factor': 1., 'capture': manifest,
                'registration_helpers_sha256': common.sha(HELPERS), 'raw_preview': raw_meta,
                'fused_cloud': fused_meta, 'table_plane_residual_mm': table_residual,
                'end_axis_fit': axis_evidence, 'native_to_reference': transform.tolist(),
                'selection': 'Table height >17 mm; initial axial X -23..19 mm; radius <13.5 mm. '
                             'No CAD-distance rejection.',
                'retained_cloud': {'path': str(out), 'sha256': common.sha(out), 'points': len(native)},
                'faces': faces, 'body_hex': body_hex, 'nut_hex': nut_hex,
                'profile_samples': samples,
                'manufacturer_drawing': {'file': 'source/polypropylene-bulkhead-dimensions.pdf',
                    'sha256': common.sha(HERE/'source/polypropylene-bulkhead-dimensions.pdf'),
                    'url': 'https://www.johnguest.com/sites/jg/files/2023-04/'
                           'JG%20Drinks%20Polypropylene%20Bulkhead%20Connector%20Data%20Sheet.pdf'},
                'limits': limits}
    (HERE/'scan-evidence.json').write_text(json.dumps(evidence, indent=2)+'\n')
    parameters = {
        'units': 'mm', 'material_id': 'HSM-000059', 'panel_seat_local_x_mm': seat,
        'outboard_mouth_local_x_mm': near, 'inboard_mouth_local_x_mm': far,
        'overall_mm': near-far, 'near_ring_face_y_mm': near-seat, 'far_ring_face_y_mm': far-seat,
        'body_hex': {k: body_hex[k] for k in ['across_flats_mm', 'center_yz_mm', 'vertex_clock_degrees']},
        'body_hex_start_local_x_mm': 7.0,
        'nut_hex': {k: nut_hex[k] for k in ['across_flats_mm', 'center_yz_mm', 'vertex_clock_degrees']},
        'nut_hex_stop_local_x_mm': -2.9,
        'nut_axial_range_local_mm': [station('nut_back'), station('nut_front')],
        'captured_nut_gap_mm': seat-station('nut_front'),
        'barrel_end_local_x_mm': -17.0, 'barrel_crest_diameter_mm': 16.7,
        'profiles': curves,
        'profile_method': '97.5th percentile outward-facing radius in 0.125 mm axial bins; '
                          'three-bin median; 0.035 mm radial simplification.',
        'published': {'tube_od_mm': 6.35, 'thread_bsp_inch': .375, 'panel_hole_mm': 17.,
                      'overall_with_released_collets_mm': 34.6, 'bare_panel_span_max_mm': 13.5,
                      'body_hex_af_mm': 19., 'nut_hex_af_mm': 20., 'tube_stop_depth_mm': 15.7,
                      'through_bore_mm': 5.3},
        'scan_evidence_sha256': common.sha(HERE/'scan-evidence.json'),
    }
    (HERE/'reference-parameters.json').write_text(json.dumps(parameters, indent=2)+'\n')
    print(json.dumps({'retained_points': len(native), 'overall_mm': near-far,
                      'outboard_reach_mm': near-seat, 'inboard_reach_mm': seat-far,
                      'body_hex_af_mm': body_hex['across_flats_mm'],
                      'nut_hex_af_mm': nut_hex['across_flats_mm'],
                      'captured_nut_gap_mm': seat-station('nut_front')}, indent=2))


if __name__ == '__main__':
    main()
