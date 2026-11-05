"""Fit the prepared ACVUS44 from its preserved native MINI 2 capture."""
from pathlib import Path
import importlib.util
import json
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ARCHIVE = Path.home()/'Documents/3D Scans/2026-11-03-neofit-acvus44-stem-check'
HELPERS = HERE.parent/'jg-bulkhead-union/analyze_scan.py'
spec = importlib.util.spec_from_file_location('stem_scan_helpers', HELPERS)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
common = helpers.common
sys.path.insert(0, str(HERE.parent/'g-ganen-pump'))
from scan_tools import load_cloud, cylinder, unit


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
    initial_n = n @ tr.T @ pr.T
    selected = ((initial[:, 0] > 14) & (initial[:, 0] < 27)
                & (abs(initial_n[:, 0]) < .3) & (table[:, 2] > 14)
                & (np.hypot(initial[:, 1], initial[:, 2]+2) < 5))
    fitted = cylinder(initial[selected][::2], [1, 0, -.1], 3.175)
    origin = np.array(fitted['axis_point'])
    axis = np.array(fitted['axis_direction'])
    z = unit(np.array([0, 0, 1])-axis*axis[2])
    rotation = np.array([axis, np.cross(z, axis), z])
    q = (initial-origin) @ rotation.T
    nn = initial_n @ rotation.T
    radius = np.hypot(q[:, 1], q[:, 2])
    keep = ((table[:, 2] > 14) & (q[:, 0] > -44) & (q[:, 0] < 10) & (radius < 10)
            & (((initial[:, 0] < -12) | (initial[:, 0] > 12)) | (table[:, 2] > 19.5)))
    q, nn = q[keep], nn[keep]
    faces = {name: helpers.axial_face(q, nn, selection) for name, selection in {
        'stem_tip': (8.2, 8.7, 2, 2.7, 1),
        'stem_shoulder': (-10, -9.5, 4, 6.3, 1),
        'socket_mouth': (-42.9, -42.1, 3.6, 5.8, -1),
    }.items()}
    tip, shoulder, mouth = [faces[k]['axis_station_mm']
                            for k in ('stem_tip', 'stem_shoulder', 'socket_mouth')]
    profile, samples = helpers.profile(q, nn, mouth, tip)
    profile = [[round(tip-x, 5), r] for x, r in reversed(profile)]
    profile[0][0] = 0.
    profile[-1][0] = tip-mouth
    # The receiving length uses the specified tube size. Preserve the observed
    # tip chamfer and groove while removing the percentile envelope's optical
    # excess over the nominal mating cylinder; the source cloud stays at unit scale.
    mating_length = 17.
    radius_at_end = float(np.interp(mating_length, *zip(*profile)))
    profile = [[x, min(r, 6.35/2) if x <= mating_length else r] for x, r in profile]
    profile.append([mating_length, min(radius_at_end, 6.35/2)])
    profile.sort()
    permutation = np.diag([-1., -1., 1.])
    native = q @ permutation.T + [tip, 0, 0]
    native_n = nn @ permutation.T
    out = ARCHIVE/'registered-acvus44.ply'
    common.write_cloud(out, native, native_n)
    transform = np.eye(4)
    transform[:3, :3] = permutation @ rotation @ pr @ tr
    transform[:3, 3] = permutation @ (rotation @ (-pr @ (tr @ tc+pc)-origin)) + [tip, 0, 0]
    evidence = {
        'units': 'mm', 'coordinate_scale_factor': 1., 'capture': manifest,
        'registration_helpers_sha256': common.sha(HELPERS), 'raw_preview': raw_meta,
        'fused_cloud': fused_meta, 'table_plane_residual_mm': table_residual,
        'stem_cylinder': {**fitted, 'selection': 'Initial X 14..27 mm; '
            '|normal.X|<0.3; table height >14 mm; radius from (Y0,Z-2)<5 mm; every second point'},
        'native_to_reference': transform.tolist(),
        'selection': 'Table height >14 mm; local axial X -44..10 mm; radius <10 mm. '
                     'Central initial X -12..12 mm additionally requires table height >19.5 mm '
                     'to exclude putty. No CAD-distance rejection.',
        'retained_cloud': {'path': str(out), 'sha256': common.sha(out), 'points': len(native)},
        'faces': faces, 'profile_samples': samples,
        'limits': ['Absolute optical scale is not independently calibrated.',
                   'Putty-hidden lower sectors continue the fitted turned forms.',
                   'The release face is a representative axial datum for the captured free collet.',
                   'Collet slots, molded markings, hidden seals and check internals are omitted.',
                   'The scan measures exterior geometry, not insertion stops, flow direction or pressure performance.'],
    }
    (HERE/'scan-evidence.json').write_text(json.dumps(evidence, indent=2)+'\n')
    parameters = {
        'units': 'mm', 'material_id': 'HSM-0383', 'length_mm': tip-mouth,
        'stem_shoulder_x_mm': tip-shoulder, 'stem_cylinder_diameter_mm': 2*fitted['radius_mm'],
        'nominal_stem_diameter_mm': 6.35, 'socket_display_diameter_mm': 6.5,
        'nominal_mating_stem_length_mm': mating_length,
        'socket_insertion_estimate_mm': 16.891, 'through_bore_display_mm': 4.3,
        'profile_x_radius_mm': profile,
        'profile_method': '97.5th percentile outward-facing radius in 0.125 mm axial bins; '
                          'three-bin median; 0.035 mm radial simplification. The mating '
                          'stem through X17 uses nominal 6.35 mm OD, retaining its observed '
                          'tip chamfer and groove. No cloud rescaling.',
        'scan_evidence_sha256': common.sha(HERE/'scan-evidence.json'),
    }
    (HERE/'reference-parameters.json').write_text(json.dumps(parameters, indent=2)+'\n')
    print(json.dumps({k: v for k, v in parameters.items() if k != 'profile_x_radius_mm'}, indent=2))


if __name__ == '__main__':
    main()
