"""Task-local observation-to-export check for the two ATEU44W specimens."""
from pathlib import Path
import hashlib
import json
import shutil
import sys

import cadquery as cq
import numpy as np
import trimesh

import neofit_stem_elbow as model
HERE = Path(__file__).resolve().parent
ARCHIVE = Path.home()/'Documents/3D Scans/2026-10-29-neofit-ateu44w-stem-elbow'
sys.path.insert(0, str(HERE.parent/'g-ganen-pump'))
from scan_tools import load_cloud
from register_scan import voxel_sample


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def summary(distance):
    return {'samples': len(distance),
            'p50_p90_p95_p99_max_mm': np.quantile(distance, [.5, .9, .95, .99, 1]).tolist(),
            'fraction_within_0_25_mm': float(np.mean(distance <= .25)),
            'fraction_within_0_50_mm': float(np.mean(distance <= .5))}


def main():
    evidence = json.loads((HERE/'scan-evidence.json').read_text())
    shape = cq.importers.importStep(str(model.STEP)).val(); solids = shape.Solids()
    vertices, faces = shape.tessellate(.025, .08)
    mesh = trimesh.Trimesh(vertices=[v.toTuple() for v in vertices], faces=faces, process=False)
    reports, observations = {}, {}
    for name, item in evidence['specimens'].items():
        source = item['retained_cloud']; p, n, _ = load_cloud(source['path'], source['sha256'])
        p, n = voxel_sample(p, n, .25); distance = np.empty(len(p))
        for start in range(0, len(p), 1000):
            stop = min(start+1000, len(p)); _, distance[start:stop], _ = trimesh.proximity.closest_point(mesh, p[start:stop])
        reports[name] = {'retained_cloud_sha256': source['sha256'], 'all_observations': summary(distance),
            'regions': {region: summary(distance[mask]) for region, mask in {
                'straight_stem': p[:, 0] < -7,
                'bend_and_shoulder': (p[:, 0] >= -7) & (p[:, 1] < 5),
                'socket_fixed_body': (p[:, 0] >= -7) & (p[:, 1] >= 5) & (p[:, 1] < 19),
                **({'release_collet': p[:, 1] >= 19} if name == 'b' else {})}.items()}}
        observations[name] = (p, distance)
    stl_path = ARCHIVE/'neofit-ateu44w-stem-elbow.stl'
    pole_triangles = model.export_stl(shape, stl_path)
    stl = trimesh.load(str(stl_path), force='mesh')
    report = {'units': 'mm', 'material_id': 'HSM-000330',
              'method': 'Each physically retained specimen compared independently to the reopened exported STEP; rigid native scale, no CAD-distance rejection.',
              'model_source_sha256': sha(HERE/'neofit_stem_elbow.py'),
              'parameters_sha256': sha(HERE/'reference-parameters.json'),
              'frozen_parameter_snapshot_sha256': model.PARAMETER_SNAPSHOT_SHA256,
              'step_sha256': sha(model.STEP), 'scan_evidence_sha256': sha(HERE/'scan-evidence.json'),
              'observation_voxel_mm': .25, 'cad_tessellation_mm': .025,
              'native_assembly_valid': shape.isValid(), 'native_solid_count': len(solids),
              'each_solid_valid': [solid.isValid() for solid in solids],
              'stl_watertight': bool(stl.is_watertight), 'stl_shells': len(stl.split(only_watertight=False)),
              'stl_zero_area_triangles_removed': pole_triangles,
              'stl_triangles': len(stl.faces), 'extent_mm': mesh.extents.tolist(),
              'ports': {'socket': model.socket(), 'stem_tip': model.stem_tip(), 'stem_shoulder': model.stem_shoulder()},
              'all_observations': summary(np.concatenate([d for p, d in observations.values()])),
              'specimens': reports, 'limits': evidence['limits']}
    (HERE/'scan-model-check.json').write_text(json.dumps(report, indent=2)+'\n')
    shutil.copy2(model.STEP, ARCHIVE/'neofit-ateu44w-stem-elbow.step')
    cache = HERE.parents[2]/'.cache/ateu44w-scan'; cache.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache/'comparison.npz', **{k+'_'+c: value for k, pair in observations.items() for c, value in zip(['p', 'distance'], pair)})
    parts = []
    for name, piece in model.build():
        vertices, faces = piece.val().tessellate(.025, .08)
        parts.append({'name': name, 'vertices': [p.toTuple() for p in vertices],
                      'faces': [list(f) for f in faces], 'color': [.74, .77, .72] if name == 'body_and_stem' else [.63, .68, .64]})
    (cache/'render-mesh.json').write_text(json.dumps({'parts': parts, 'output': str(ARCHIVE/'preview.png')}))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(12, 9), facecolor='#faf9f6')
    for row, (name, (p, distance)) in zip(axes, observations.items()):
        for ax, column in zip(row, [1, 2]):
            dots = ax.scatter(p[:, 0], p[:, column], c=distance, s=.8, cmap='viridis', vmin=0, vmax=.5, rasterized=True)
            ax.set_aspect('equal'); ax.set_xlabel('X, mm'); ax.set_ylabel('XYZ'[column]+', mm'); ax.grid(alpha=.2)
            ax.set_title('Specimen '+name.upper())
    fig.subplots_adjust(left=.07, right=.88, top=.89, bottom=.12, hspace=.35, wspace=.25)
    bar = fig.colorbar(dots, cax=fig.add_axes([.92, .22, .018, .55])); bar.set_label('Distance to CAD, mm (saturates at 0.5)')
    fig.suptitle('HSM-000330 · neoFit ATEU44W — complementary specimens against one reference', fontsize=14)
    fig.text(.07, .035, '868 frames • 0.10 mm native fusion • separate rigid registrations • nominal 90° crossing and 6.35 mm male OD', fontsize=10)
    fig.savefig(HERE/'scan-model-check.png', dpi=140, facecolor=fig.get_facecolor())
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
