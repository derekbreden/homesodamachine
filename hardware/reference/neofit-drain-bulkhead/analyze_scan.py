"""Fit HSM-000061 from the preserved ABU44M-E bulkhead-and-nut capture."""
from pathlib import Path
import importlib.util
import json
import sys

import numpy as np
from scipy.ndimage import median_filter
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
ARCHIVE = Path.home() / 'Documents/3D Scans/2026-10-29-neofit-abu44m-bulkhead'
HELPERS = HERE.parent / 'yzmsz-water-regulator/analyze_scan.py'
spec = importlib.util.spec_from_file_location('bulkhead_scan_helpers', HELPERS)
common = importlib.util.module_from_spec(spec); spec.loader.exec_module(common)
sys.path.insert(0, str(HERE.parent / 'g-ganen-pump'))
from scan_tools import load_cloud, plane, stats, unit


def end_axis(p, n, height):
    radial = np.hypot(p[:, 1], p[:, 2]+1.5)
    facing = (p[:, 1]*n[:, 1]+(p[:, 2]+1.5)*n[:, 2])/np.maximum(radial, 1e-8)
    hit = ((abs(p[:, 0]) > 10) & (abs(p[:, 0]) < 20) & (height > 17)
           & (radial < 7) & (abs(n[:, 0]) < .5) & (facing > .6))
    q, nn = p[hit][::3], n[hit][::3]
    length = np.hypot(nn[:, 1], nn[:, 2])
    x = q[:, 0]

    def residual(v):
        return (nn[:, 2]*(q[:, 1]-v[0]-v[2]*x)-nn[:, 1]*(q[:, 2]-v[1]-v[3]*x))/length

    fit = least_squares(residual, [0, -1.5, 0, 0], loss='soft_l1', f_scale=.08)
    xaxis = unit([1, *fit.x[2:]])
    zaxis = unit(np.array([0, 0, 1])-xaxis*xaxis[2])
    rotation = np.array([xaxis, np.cross(zaxis, xaxis), zaxis])
    origin = np.array([0, *fit.x[:2]])
    return origin, rotation, {'samples': len(q), 'axis_point_initial_mm': origin.tolist(),
        'axis_direction_initial': xaxis.tolist(), 'normal_ray_residual_mm': stats(fit.fun),
        'selection': 'Initial |X| 10..20 mm; table height >17 mm; radius from (Y0,Z-1.5)<7 mm; |normal.X|<0.5; outward radial normal >0.6; every third point'}


def hex_fit(p, n, lo, hi):
    radial = np.hypot(p[:, 1], p[:, 2])
    theta = np.arctan2(n[:, 2], n[:, 1])
    selected = (p[:, 0] > lo) & (p[:, 0] < hi) & (abs(n[:, 0]) < .2) & (radial > 8)
    phase = np.angle(np.mean(np.exp(6j*theta[selected])))/6
    rows = []
    for k in range(6):
        angle = phase+k*np.pi/3
        hit = selected & (abs(np.angle(np.exp(1j*(theta-angle)))) < np.radians(3))
        if hit.sum() < 60:
            continue
        c, normal, residual = plane(p[hit]); normal *= np.sign(normal @ n[hit].mean(0))
        rows.append({'normal': normal.tolist(), 'offset_mm': float(normal @ c),
                     'samples': int(hit.sum()), 'residual_mm': residual})
    normals = np.array([row['normal'] for row in rows])
    offsets = np.array([row['offset_mm'] for row in rows])
    cy, cz, apothem = np.linalg.lstsq(np.column_stack([normals[:, 1], normals[:, 2], np.ones(len(rows))]), offsets, rcond=None)[0]
    _, _, vectors = np.linalg.svd(normals)
    axis = vectors[-1]*np.sign(vectors[-1, 0])
    return {'axial_selection_mm': [lo, hi], 'planes': rows,
            'across_flats_mm': float(2*apothem), 'center_yz_mm': [float(cy), float(cz)],
            'axis_direction': axis.tolist(), 'vertex_clock_degrees': float(np.degrees(phase)-30)}


def axial_face(p, n, spec):
    lo, hi, rlo, rhi, sign = spec
    radial = np.hypot(p[:, 1], p[:, 2])
    hit = ((p[:, 0] > lo) & (p[:, 0] < hi) & (radial > rlo)
           & (radial < rhi) & (n[:, 0]*sign > .95))
    center, normal, residual = plane(p[hit]); normal *= np.sign(normal @ n[hit].mean(0))
    station = float((normal @ center)/normal[0])
    return {'axis_station_mm': station, 'normal': normal.tolist(), 'samples': int(hit.sum()),
            'plane_residual_mm': residual, 'selection_x_radius_sign': list(spec)}


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
    return [[round(x, 5), round(radius, 5)] for x, radius in common.simplify(outline, .035)], rows


def main():
    manifest = json.loads((ARCHIVE/'capture-manifest.json').read_text()); capture = manifest['passes'][0]
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
    keep = (table[:, 2] > 17) & (q[:, 0] > -20) & (q[:, 0] < 22) & (radius < 12.5)
    q, nn = q[keep], nn[keep]
    faces = {name: axial_face(q, nn, selection) for name, selection in {
        'panel_seat': (-4.8, -3.8, 8, 9.5, 1),
        'nut_front': (.5, 1.6, 8, 9.5, -1), 'nut_back': (7.2, 8.1, 7.7, 8.7, 1),
        'outboard_mouth': (-16.6, -15.7, 3, 4.2, -1),
        'inboard_mouth': (16.6, 17.6, 2.8, 4.2, 1)}.items()}
    station = lambda name: faces[name]['axis_station_mm']
    seat = station('panel_seat')
    near = station('outboard_mouth'); far = station('inboard_mouth')
    body_hex = hex_fit(q, nn, -9.6, -7.3); nut_hex = hex_fit(q, nn, 3.6, 6.6)
    curves, samples = {}, {}
    for name, lo, hi in [('outboard', near, seat), ('inboard', 10.75, far),
                          ('nut', station('nut_front'), station('nut_back'))]:
        curves[name], samples[name] = profile(q, nn, lo, hi)
    permutation = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]])
    native = q @ permutation.T + [0, seat, 0]; native_n = nn @ permutation.T
    out = ARCHIVE/'registered-abu44m.ply'; common.write_cloud(out, native, native_n)
    transform = np.eye(4)
    transform[:3, :3] = permutation @ rotation @ pr @ tr
    transform[:3, 3] = permutation @ (rotation @ (-pr @ (tr @ tc+pc)-origin)) + [0, seat, 0]
    limits = ['Paint thickness and absolute optical scale are not independently calibrated.',
              'Putty-hidden lower sectors continue the fitted turned and hexagonal forms.',
              'The barrel uses an M15 crest envelope; thread grooves and hidden engagement are not modeled.',
              'Collet finger slots and molded markings are omitted; mouth bevels and through bore are display geometry.',
              'The captured nut pose does not define the installed panel stack or qualify thread engagement, seals or tube retention.']
    evidence = {'units': 'mm', 'coordinate_scale_factor': 1., 'capture': manifest,
                'registration_helpers_sha256': common.sha(HELPERS), 'raw_preview': raw_meta,
                'fused_cloud': fused_meta, 'table_plane_residual_mm': table_residual,
                'end_axis_fit': axis_evidence, 'native_to_reference': transform.tolist(),
                'selection': 'Table height >17 mm; initial axial X -20..22 mm; radius <12.5 mm. No CAD-distance rejection.',
                'retained_cloud': {'path': str(out), 'sha256': common.sha(out), 'points': len(native)},
                'faces': faces, 'body_hex': body_hex, 'nut_hex': nut_hex, 'profile_samples': samples,
                'manufacturer_drawing': {'file': 'source/bulkhead-union-dimensions.pdf',
                    'sha256': common.sha(HERE/'source/bulkhead-union-dimensions.pdf'),
                    'url': 'https://assets.freshwatersystems.com/image/upload/qnbgcy8djx3nj2weqz9v.pdf'},
                'limits': limits}
    (HERE/'scan-evidence.json').write_text(json.dumps(evidence, indent=2)+'\n')
    parameters = {'units': 'mm', 'material_id': 'HSM-000061', 'panel_seat_local_x_mm': seat,
                  'outboard_mouth_local_x_mm': near, 'inboard_mouth_local_x_mm': far,
                  'overall_mm': far-near, 'near_ring_face_y_mm': seat-near, 'far_ring_face_y_mm': seat-far,
                  'body_hex': {k: body_hex[k] for k in ['across_flats_mm', 'center_yz_mm', 'vertex_clock_degrees']},
                  'body_hex_stop_local_x_mm': -6.35,
                  'nut_hex': {k: nut_hex[k] for k in ['across_flats_mm', 'center_yz_mm', 'vertex_clock_degrees']},
                  'nut_hex_start_local_x_mm': 2.9,
                  'nut_axial_range_local_mm': [station('nut_front'), station('nut_back')],
                  'captured_nut_gap_mm': station('nut_front')-seat,
                  'barrel_end_local_x_mm': 10.75, 'profiles': curves,
                  'profile_method': '97.5th percentile outward-facing radius in 0.125 mm axial bins; three-bin median; 0.035 mm radial simplification.',
                  'published': {'tube_od_mm': 4., 'thread_diameter_mm': 15., 'thread_pitch_mm': 1.5,
                    'overall_mm': 32.4, 'bare_panel_span_mm': 8.1, 'nut_length_mm': 6.5,
                    'body_hex_af_mm': 17., 'nut_hex_af_mm': 18., 'tube_stop_depth_mm': 14.7},
                  'scan_evidence_sha256': common.sha(HERE/'scan-evidence.json')}
    (HERE/'reference-parameters.json').write_text(json.dumps(parameters, indent=2)+'\n')
    print(json.dumps({'retained_points': len(native), 'overall_mm': far-near,
                      'outboard_reach_mm': seat-near, 'inboard_reach_mm': far-seat,
                      'body_hex_af_mm': body_hex['across_flats_mm'], 'nut_hex_af_mm': nut_hex['across_flats_mm'],
                      'captured_nut_gap_mm': station('nut_front')-seat}, indent=2))


if __name__ == '__main__':
    main()
