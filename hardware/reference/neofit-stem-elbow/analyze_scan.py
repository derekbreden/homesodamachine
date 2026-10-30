"""Measure two prepared ATEU44W specimens at native scale in one capture.

Opposing mounting ends supply complementary visible surfaces. Each specimen
has its own rigid registration; neither its size nor its observation weights
are changed to make it agree with the other specimen or the delivered CAD.
"""
from pathlib import Path
import importlib.util
import json
import sys

import numpy as np
from scipy.ndimage import median_filter
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

HERE = Path(__file__).resolve().parent
ARCHIVE = Path.home()/'Documents/3D Scans/2026-10-29-neofit-ateu44w-stem-elbow'
HELPERS = HERE.parent/'yzmsz-water-regulator/analyze_scan.py'
spec = importlib.util.spec_from_file_location('ateu_scan_helpers', HELPERS)
common = importlib.util.module_from_spec(spec); spec.loader.exec_module(common)
sys.path.insert(0, str(HERE.parent/'g-ganen-pump'))
from scan_tools import load_cloud, plane, stats

# Inspected coarse poses in the marker-table frame, before the surface fit.
SEEDS = {
    'a': {'origin': [-4.8295260083, 14.6867264369, 20.6388786872],
          'rotation': [[.7158069457, -.1242015957, -.6871640125],
                       [-.4067588372, -.8740316175, -.2657366742],
                       [-.5675981544, .4697261918, -.6761579992]]},
    'b': {'origin': [20.1613952332, -3.7631515830, 28.6407221920],
          'rotation': [[.7264803319, .0902013915, .6812415403],
                       [-.1204003264, -.9593055039, .2554147834],
                       [.6765575280, -.2675755204, -.6860563039]]},
}


def register(p, n, name):
    seed = SEEDS[name]; o = np.array(seed['origin']); r = np.array(seed['rotation'])
    # Polar decomposition removes only rounding of the inspected pose matrix.
    u, _, vt = np.linalg.svd(r); r = u@vt
    q = (p-o)@r.T; nn = n@r.T
    rs, rb = np.hypot(q[:, 1], q[:, 2]), np.hypot(q[:, 0], q[:, 2])
    fs = np.sum(q[:, 1:]*nn[:, 1:], axis=1)/np.maximum(rs, 1e-8)
    fb = (q[:, 0]*nn[:, 0]+q[:, 2]*nn[:, 2])/np.maximum(rb, 1e-8)
    sm = ((q[:, 0] > -23) & (q[:, 0] < -9) & (rs > 2.7) & (rs < 3.7)
          & (fs > .8) & (abs(nn[:, 0]) < .2) & (p[:, 2] > 14))
    bm = ((q[:, 1] > 8.7) & (q[:, 1] < 13.7) & (rb > 7.3) & (rb < 8.5)
          & (fb > .8) & (abs(nn[:, 1]) < .2) & (p[:, 2] > 14))
    s, b = q[sm][::3], q[bm][::3]

    def unpack(v):
        return v[:3], Rotation.from_rotvec(v[3:6]).as_matrix()

    def residual(v):
        d, rr = unpack(v); ss = (s-d)@rr.T; bb = (b-d)@rr.T
        return np.r_[np.hypot(ss[:, 1], ss[:, 2])-v[6],
                     np.hypot(bb[:, 0], bb[:, 2])-v[7]-v[8]*(bb[:, 1]-11)]

    fit = least_squares(residual, [0, 0, 0, 0, 0, 0, 3.18, 7.8, 0],
                        loss='soft_l1', f_scale=.05, max_nfev=100)
    d, rr = unpack(fit.x); o = o+r.T@d; r = rr@r
    q, nn = (p-o)@r.T, n@r.T
    keep = ((q[:, 0] > (-28.5 if name == 'a' else -21.5))
            & (q[:, 0] < (6 if name == 'a' else 8.8))
            & (q[:, 1] > -6.5) & (q[:, 1] < (15 if name == 'a' else 23))
            & (abs(q[:, 2]) < 9) & (p[:, 2] > 15))
    record = {'coarse_pose': seed, 'table_frame_origin_mm': o.tolist(),
              'table_frame_rotation': r.tolist(), 'coordinate_scale_factor': 1.,
              'constraint': 'Orthogonal intersecting stem and socket axes; straight stem cylinder and drafted main socket collar fitted jointly.',
              'fit_selection': 'Coarse stem X -23..-9, radius 2.7..3.7, outward normal >0.8, |normal.X|<0.2; socket Y 8.7..13.7, radius 7.3..8.5, outward normal >0.8, |normal.Y|<0.2; table height >14; every third observation.',
              'fit_samples_stem': len(s), 'fit_samples_socket': len(b),
              'observed_stem_radius_mm': float(fit.x[6]),
              'observed_socket_radius_at_y11_mm': float(fit.x[7]),
              'socket_draft_per_mm': float(fit.x[8]), 'untrimmed_fit_residual_mm': stats(fit.fun),
              'retained_selection': {'x_mm': [-28.5 if name == 'a' else -21.5, 6 if name == 'a' else 8.8],
                                     'y_mm': [-6.5, 15 if name == 'a' else 23],
                                     'abs_z_max_mm': 9, 'minimum_table_height_mm': 15},
              'retained_points': int(keep.sum())}
    return q[keep], nn[keep], o, r, record


def face(p, n, axis, lo, hi, rlo, rhi, sign):
    other = [i for i in range(3) if i != axis]
    rad = np.linalg.norm(p[:, other], axis=1)
    hit = ((p[:, axis] > lo) & (p[:, axis] < hi) & (rad > rlo)
           & (rad < rhi) & (n[:, axis]*sign > .95))
    c, normal, residual = plane(p[hit]); normal *= np.sign(normal@n[hit].mean(0))
    return {'station_mm': float((normal@c)/normal[axis]), 'normal': normal.tolist(),
            'samples': int(hit.sum()), 'plane_residual_mm': residual,
            'selection_axis_interval_radius_sign': [axis, lo, hi, rlo, rhi, sign]}


def profile(p, n, axis, lo, hi, root=False, stem=False, ellipse=None):
    other = [i for i in range(3) if i != axis]
    radial = np.linalg.norm(p[:, other], axis=1)
    facing = np.sum(p[:, other]*n[:, other], axis=1)/np.maximum(radial, 1e-8)
    valid = facing > .2
    if ellipse is not None:
        x = p[:, 0]-ellipse['center_xz_mm'][0]
        z = p[:, 2]-ellipse['center_xz_mm'][1]
        c, s = np.cos(ellipse['angle_radians']), np.sin(ellipse['angle_radians'])
        radial = np.hypot(x*c+z*s, (-x*s+z*c)/ellipse['minor_major_ratio'])
    if root:
        valid &= (p[:, 1] > 5.4) | (p[:, 0] > .5)
    if stem:
        valid &= (p[:, 1] < 3) & (radial < 5.8)
    rows = []
    for station in np.arange(lo+.05, hi, .1):
        hit = valid & (abs(p[:, axis]-station) < .05)
        if hit.sum() < 12:
            continue
        rows.append({'station_mm': float(station), 'samples': int(hit.sum()),
                     'radius_p05_p50_p95_mm': np.quantile(radial[hit], [.05, .5, .95]).tolist()})
    outline = np.array([[row['station_mm'], row['radius_p05_p50_p95_mm'][2]] for row in rows])
    outline[:, 1] = median_filter(outline[:, 1], 3, mode='nearest')
    outline = np.vstack([[lo, outline[0, 1]], outline, [hi, outline[-1, 1]]])
    return [[round(x, 5), round(rad, 5)] for x, rad in common.simplify(outline, .035)], rows


def collet_ellipse(p, n):
    radius = np.hypot(p[:, 0], p[:, 2])
    facing = (p[:, 0]*n[:, 0]+p[:, 2]*n[:, 2])/np.maximum(radius, 1e-8)
    hit = ((p[:, 1] > 19.35) & (p[:, 1] < 20.2) & (radius > 4.4)
           & (facing > .5) & (abs(n[:, 1]) < .6))
    q = p[hit]

    def residual(v):
        x, z = q[:, 0]-v[0], q[:, 2]-v[1]
        c, s = np.cos(v[4]), np.sin(v[4])
        return (np.hypot((x*c+z*s)/v[2], (-x*s+z*c)/v[3])-1)*5.5

    fit = least_squares(residual, [0, 0, 5.9, 5.2, 0], loss='soft_l1', f_scale=.04)
    return {'center_xz_mm': fit.x[:2].tolist(), 'major_radius_mm': float(fit.x[2]),
            'minor_radius_mm': float(fit.x[3]), 'angle_radians': float(fit.x[4]),
            'minor_major_ratio': float(fit.x[3]/fit.x[2]), 'samples': len(q),
            'residual_mm': stats(fit.fun),
            'selection': 'B Y19.35..20.2, radial distance >4.4, outward normal >0.5, |normal.Y|<0.6'}


def main():
    capture = json.loads((ARCHIVE/'capture-manifest.json').read_text()); scan = capture['passes'][0]
    raw_path = Path(scan['native_project_archive'])/'raw_preview.ply'
    raw_hash = next(f['sha256'] for f in scan['native_files'] if f['file'] == 'raw_preview.ply')
    raw, _, raw_meta = load_cloud(raw_path, raw_hash)
    source, normal, fused_meta = load_cloud(scan['cloud'], scan['sha256'])
    tc, tr, table_residual = common.table_frame(raw)
    raw_table = (raw-tc)@tr.T
    pc = raw_table[raw_table[:, 2] > 7].mean(0); pc[2] = 0
    p = (source-tc)@tr.T-pc; n = normal@tr.T
    clouds, registrations = {}, {}
    for name in ['a', 'b']:
        q, nn, o, r, record = register(p, n, name)
        transform = np.eye(4); transform[:3, :3] = r@tr
        transform[:3, 3] = r@(-tr@tc-pc-o)
        record['native_to_reference'] = transform.tolist()
        out = ARCHIVE/f'registered-specimen-{name}.ply'; common.write_cloud(out, q, nn)
        record['retained_cloud'] = {'path': str(out), 'sha256': common.sha(out), 'points': len(q)}
        registrations[name] = record; clouds[name] = (q, nn)
    a, an = clouds['a']; b, bn = clouds['b']
    faces = {
        'stem_tip_a': face(a, an, 0, -27.5, -26.7, 2.35, 2.85, -1),
        'stem_shoulder_a': face(a, an, 0, -7, -5.5, 3.7, 4.5, -1),
        'socket_release_face_b': face(b, bn, 1, 20.8, 21.5, 3.7, 4.7, 1),
    }
    mouth = faces['socket_release_face_b']['station_mm']; tip = faces['stem_tip_a']['station_mm']
    shoulder = faces['stem_shoulder_a']['station_mm']
    body, body_rows = profile(b, bn, 1, 0, 19.0, root=True)
    oval = collet_ellipse(b, bn)
    collet, collet_rows = profile(b, bn, 1, 19.08, mouth, ellipse=oval)
    stem, stem_rows = profile(a, an, 0, tip, -5.8, stem=True)
    # Straight mating diameter remains the supplier's nominal 1/4 inch. Only
    # the shoulder profile and the observed tip datum come from this curve.
    stem = [[tip, 3.0], [tip+.22, 3.175], [shoulder-.14, 3.175],
            [shoulder-.02, 4.75], *[[x, rad] for x, rad in stem if x > shoulder], [-5.5, 5.08], [0., 5.08]]
    stem = sorted({round(x, 5): round(rad, 5) for x, rad in stem}.items())
    # The exposed outside bend is the spherical quarter between the two legs.
    hub = ((b[:, 0] > .5) & (b[:, 1] < -.5) & (b[:, 1] > -5.3)
           & (np.linalg.norm(b, axis=1) < 6.0))
    hub_radius = float(np.median(np.linalg.norm(b[hub], axis=1)))
    limits = ['Paint thickness, absolute optical scale and specimen-to-specimen variation are not independently calibrated.',
              'The nominal 90-degree crossing and straight 6.35 mm male diameter are modeling constraints; source clouds are not rescaled.',
              'Specimen A supplies the free stem tip and shoulder, specimen B the socket release face and exposed nose; the two registrations remain separate.',
              'Putty-hidden sectors are completed by rotational and bend symmetry. Fine collet finger slots, lettering and mold seams are omitted.',
              'The 4.3 mm flow bore, hidden transitions and collet underside are display geometry; 16.891 mm insertion is the published family value, not measured seal or grip geometry.']
    evidence = {'units': 'mm', 'material_id': 'HSM-000330', 'coordinate_scale_factor': 1.,
                'capture': capture, 'raw_preview': raw_meta, 'fused_cloud': fused_meta,
                'registration_helpers_sha256': common.sha(HELPERS),
                'table_plane_residual_mm': table_residual, 'specimens': registrations,
                'faces': faces, 'profile_method': '95th percentile outward-facing radial observations in 0.10 mm axial bins; three-bin median; 0.035 mm radial simplification.',
                'profile_feature_selection': 'Socket root below Y5.4 uses X>0.5 to exclude the crossing stem. Stem profile uses Y<3 and radial distance below 5.8 to exclude the crossing socket. These feature masks do not remove comparison observations.',
                'profile_samples': {'fixed_body_b': body_rows, 'release_collet_b': collet_rows, 'stem_a': stem_rows},
                'collet_ellipse': oval,
                'bend': {'radius_mm': hub_radius, 'samples': int(hub.sum()),
                         'sphere_residual_mm': stats(np.linalg.norm(b[hub], axis=1)-hub_radius)},
                'source_drawing': {'file': 'source/stem-elbow-dimensions.pdf', 'sha256': common.sha(HERE/'source/stem-elbow-dimensions.pdf')},
                'retained_observation_policy': 'Physical table-height and per-specimen bounds are fixed before CAD comparison; no observations are rejected by distance to the model.',
                'limits': limits}
    (HERE/'scan-evidence.json').write_text(json.dumps(evidence, indent=2)+'\n')
    params = {'units': 'mm', 'material_id': 'HSM-000330', 'tube_od_mm': 6.35, 'stem_od_mm': 6.35,
              'stem_tip_x_mm': tip, 'stem_shoulder_x_mm': shoulder, 'socket_mouth_y_mm': mouth,
              'stem_length_mm': shoulder-tip, 'flow_bore_display_mm': 4.3,
              'published_socket_insertion_mm': 16.891, 'fixed_nose_y_mm': 19.,
              'collet_start_y_mm': 19.08, 'bend_radius_mm': hub_radius,
              'collet_ellipse': {k: oval[k] for k in ['center_xz_mm', 'angle_radians', 'minor_major_ratio']},
              'profiles': {'fixed_body_y': body, 'release_collet_y': collet, 'stem_x': stem},
              'scan_evidence_sha256': common.sha(HERE/'scan-evidence.json')}
    (HERE/'reference-parameters.json').write_text(json.dumps(params, indent=2)+'\n')
    print(json.dumps({'retained_points': {k:v['retained_points'] for k,v in registrations.items()},
                      'faces': faces, 'bend_radius_mm': hub_radius, 'stem_length_mm': shoulder-tip,
                      'body_profile': body, 'collet_profile': collet, 'stem_profile': stem}, indent=2))


if __name__ == '__main__':
    main()
