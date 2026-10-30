"""Measure the sprayed PISCO RVFUP regulator exterior at native scan scale."""
from pathlib import Path
import importlib.util
import json
import sys

import numpy as np
from scipy.ndimage import median_filter

HERE = Path(__file__).resolve().parent
ARCHIVE = Path.home() / 'Documents/3D Scans/2026-10-29-pisco-rvfup-regulator'
HELPERS = HERE.parent / 'yzmsz-water-regulator/analyze_scan.py'
spec = importlib.util.spec_from_file_location('regulator_scan_helpers', HELPERS)
common = importlib.util.module_from_spec(spec); spec.loader.exec_module(common)
sys.path.insert(0, str(HERE.parent / 'g-ganen-pump'))
from scan_tools import cylinder, load_cloud, stats, unit


def main():
    manifest = json.loads((ARCHIVE / 'capture-manifest.json').read_text())
    capture = manifest['passes'][0]
    raw_path = Path(capture['native_project_archive']) / 'raw_preview.ply'
    raw_sha = next(f['sha256'] for f in capture['native_files'] if f['file'] == 'raw_preview.ply')
    raw, _, raw_meta = load_cloud(raw_path, raw_sha)
    p, n, meta = load_cloud(capture['cloud'], capture['sha256'])
    tc, tr, pc, pr, table_residual = common.initial_frame(raw)
    table = (p - tc) @ tr.T
    # The inspected long-neck inlet lies at the positive end of the initial
    # table PCA axis. Reverse X/Y to follow flow while retaining a proper frame.
    flip = np.diag([-1., -1., 1.])
    initial = (table - pc) @ pr.T @ flip
    normals = n @ tr.T @ pr.T @ flip
    hit = ((initial[:, 0] > -5) & (initial[:, 0] < 6) & (table[:, 2] > 21)
           & (abs(normals[:, 0]) < .2) & (abs(initial[:, 1]) < 11))
    fitted = cylinder(initial[hit][::3], [1, 0, 0], 10.)
    c = np.array(fitted['axis_point']); x = unit(fitted['axis_direction'])
    x *= np.sign(x[0])
    z = unit(np.array([0, 0, 1]) - x*x[2])
    r = np.array([x, np.cross(z, x), z])
    q = (initial - c) @ r.T; nn = normals @ r.T
    radius = np.hypot(q[:, 1], q[:, 2])
    keep = ((table[:, 2] > 21) & (q[:, 0] > -36) & (q[:, 0] < 33) & (radius < 12.5))
    mouths = {}
    for name, lo, hi, sign in [('inlet', -35, -31, -1), ('outlet', 26, 32, 1)]:
        hit = (keep & (q[:, 0] > lo) & (q[:, 0] < hi) & (radius > 4.5)
               & (radius < 5.5) & (nn[:, 0]*sign > .95))
        bins = np.arange(lo, hi+.04, .04)
        counts, edges = np.histogram(q[hit, 0], bins=bins)
        i = int(np.argmax(counts)); peak = float((edges[i]+edges[i+1])/2)
        patch = hit & (abs(q[:, 0]-peak) < .12)
        station = float(np.median(q[patch, 0]))
        mouths[name] = {'initial_x_mm': station, 'samples': int(patch.sum()),
                        'selection': f'Initial X {lo}..{hi} mm; radius 4.5..5.5 mm; outward axial normal >0.95; dominant 0.04 mm-bin face within 0.12 mm',
                        'axial_residual_mm': stats(q[patch, 0]-station)}
    inlet = mouths['inlet']['initial_x_mm']
    length = mouths['outlet']['initial_x_mm']-inlet
    q[:, 0] -= inlet
    # Native library frame: flow +Z. X is the table's transverse direction,
    # Y is its upward direction projected perpendicular to the fitted axis.
    permutation = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]])
    native = q @ permutation.T; native_normals = nn @ permutation.T
    out = ARCHIVE / 'registered-pisco.ply'
    common.write_cloud(out, native[keep], native_normals[keep])
    facing = (q[:, 1]*nn[:, 1] + q[:, 2]*nn[:, 2])/np.maximum(radius, 1e-8)
    profile = []
    for station in np.arange(.075, length, .15):
        hit = keep & (abs(q[:, 0]-station) < .075) & (facing > .1)
        if hit.sum() >= 12:
            profile.append({'z_mm': float(station), 'samples': int(hit.sum()),
                            'radius_p05_p50_p95_mm': np.quantile(radius[hit], [.05, .5, .95]).tolist()})
    outline = np.array([[row['z_mm'], row['radius_p05_p50_p95_mm'][2]] for row in profile])
    outline[:, 1] = median_filter(outline[:, 1], 3, mode='nearest')
    outline = np.vstack([[0, outline[0, 1]], outline, [length, outline[-1, 1]]])
    transform = np.eye(4)
    transform[:3, :3] = permutation @ r @ flip @ pr @ tr
    transform[:3, 3] = permutation @ (r @ (-flip @ pr @ (tr @ tc + pc)-c) - [inlet, 0, 0])
    evidence = {'units': 'mm', 'coordinate_scale_factor': 1., 'capture': manifest,
                'registration_helpers_sha256': common.sha(HELPERS), 'raw_preview': raw_meta, 'fused_cloud': meta,
                'native_to_reference': transform.tolist(), 'table_plane_residual_mm': table_residual,
                'axis_selection': 'Initial flow-axis X -5..6 mm; height >21 mm; |normal.X|<0.2; |Y|<11 mm; every third selected observation',
                'housing_cylinder_fit': fitted, 'mouth_fits': mouths,
                'selection': 'Table height >21 mm; initial flow-axis X -36..33 mm; radius <12.5 mm. No CAD-distance rejection.',
                'retained_cloud': {'path': str(out), 'sha256': common.sha(out), 'points': int(keep.sum())},
                'axial_profiles': profile,
                'limits': ['Paint thickness and absolute optical scale are not independently calibrated.',
                           'Putty-hidden lower sectors continue the fitted rotational exterior.',
                           'The visible housing is modeled as round; embossed markings, molding seams and collet finger slots are omitted.',
                           'Material boundaries and hidden joint continuation are display interpretations.',
                           'The 17 mm socket depth follows the OEM catalog; the scan does not qualify insertion stops, seals or pressure performance.']}
    (HERE / 'regulator-scan-evidence.json').write_text(json.dumps(evidence, indent=2)+'\n')
    parameters = {'units': 'mm', 'length_mm': length,
                  'profile_z_radius_mm': [[round(z, 4), round(radius, 4)] for z, radius in common.simplify(outline)],
                  'profile_method': '95th percentile outward-facing radius in 0.15 mm axial bins; three-bin median; 0.04 mm radial simplification.',
                  'component_ranges_mm': {'inlet_collet': [0, 2.2], 'body': [2.2, 42.2],
                                           'outlet_fitting': [42.2, length-2.1], 'outlet_collet': [length-2.1, length]},
                  'material_boundary_scope': 'Display split at OEM axial landmark 42.2 mm and visible end rings; not hidden joint anatomy.',
                  'tube_od_mm': 6.35, 'oem_insertion_mm': 17.,
                  'scan_evidence_sha256': common.sha(HERE / 'regulator-scan-evidence.json')}
    (HERE / 'regulator-scan-parameters.json').write_text(json.dumps(parameters, indent=2)+'\n')
    cache = HERE.parents[2] / '.cache/pisco-scan'; cache.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache / 'registered.npz', p=native[keep], n=native_normals[keep], height=table[keep, 2])
    print(json.dumps({'retained_points': int(keep.sum()), 'length_mm': length,
                      'maximum_profile_diameter_mm': float(outline[:, 1].max()*2), 'mouths': mouths,
                      'housing_fit': fitted}, indent=2))


if __name__ == '__main__':
    main()
