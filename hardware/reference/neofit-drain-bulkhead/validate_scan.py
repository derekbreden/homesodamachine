"""Task-local comparison of the delivered ABU44M-E STEP with its capture."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import sys

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ARCHIVE = Path.home() / 'Documents/3D Scans/2026-10-29-neofit-abu44m-bulkhead'
os.environ['HSM_NO_BUILD_LOCK'] = '1'
import neofit_drain_bulkhead as model
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
    source = evidence['retained_cloud']
    p, n, _ = load_cloud(source['path'], source['sha256'])
    p, n = voxel_sample(p, n, .25)
    shape = cq.importers.importStep(str(model.STEP)).val()
    solids = shape.Solids()
    vertices, faces = shape.tessellate(.025, .08)
    mesh = trimesh.Trimesh(vertices=[v.toTuple() for v in vertices], faces=faces, process=False)
    distance = np.empty(len(p))
    for start in range(0, len(p), 1000):
        stop = min(start+1000, len(p))
        _, distance[start:stop], _ = trimesh.proximity.closest_point(mesh, p[start:stop])
    stl_path = ARCHIVE/'neofit-abu44m-bulkhead.stl'
    cq.exporters.export(shape, str(stl_path), tolerance=.025, angularTolerance=.08)
    stl = trimesh.load(str(stl_path), force='mesh')
    pset = model.PARAMETERS
    seat = pset['panel_seat_local_x_mm']
    front, back = [seat-x for x in pset['nut_axial_range_local_mm']]
    report = {'units': 'mm', 'material_id': 'HSM-000061',
              'method': 'All physically retained native observations to reopened STEP at 0.025 mm tessellation; no scale fit or CAD-distance rejection.',
              'model_source_sha256': sha(HERE/'neofit_drain_bulkhead.py'),
              'parameters_sha256': sha(HERE/'reference-parameters.json'),
              'frozen_parameter_snapshot_sha256': model.PARAMETER_SNAPSHOT_SHA256,
              'step_sha256': sha(model.STEP), 'scan_evidence_sha256': sha(HERE/'scan-evidence.json'),
              'retained_cloud_sha256': source['sha256'], 'observation_voxel_mm': .25,
              'native_assembly_valid': shape.isValid(), 'native_solid_count': len(solids),
              'each_solid_valid': [solid.isValid() for solid in solids],
              'stl_watertight': bool(stl.is_watertight), 'stl_triangles': len(stl.faces),
              'bounds_mm': mesh.bounds.tolist(), 'extent_mm': mesh.extents.tolist(),
              'ports': {'outboard': model.port(1), 'inboard': model.port(-1)},
              'panel_seat_y_mm': 0., 'captured_nut_front_y_mm': front,
              'all_retained_observations': summary(distance),
              'regions': {name: summary(distance[hit]) for name, hit in {
                  'outboard_head_and_fixed_flange': p[:, 1] >= 0,
                  'exposed_thread_barrel': (p[:, 1] < 0) & (p[:, 1] > front),
                  'nut_zone': (p[:, 1] <= front) & (p[:, 1] >= back),
                  'inboard_thread_and_head': p[:, 1] < back}.items()},
              'limits': evidence['limits']}
    (HERE/'scan-model-check.json').write_text(json.dumps(report, indent=2)+'\n')
    shutil.copy2(model.STEP, ARCHIVE/'neofit-abu44m-bulkhead.step')
    cache = HERE.parents[2]/'.cache/abu44m-scan'; cache.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache/'comparison.npz', p=p, distance=distance)
    parts = []
    for name, solid in model.parts().items():
        vertices, faces = solid.tessellate(.025, .08)
        v = np.array([p.toTuple() for p in vertices])
        display = np.column_stack([-v[:, 1], v[:, 0], v[:, 2]])
        parts.append({'name': name, 'vertices': display.tolist(), 'faces': [list(f) for f in faces],
                      'color': [.12, .13, .14] if name == 'fitting' else [.15, .16, .17]})
    (cache/'render-mesh.json').write_text(json.dumps({'parts': parts, 'output': str(ARCHIVE/'preview.png')}))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), facecolor='#faf9f6')
    for ax, column in zip(axes, [2, 0]):
        dots = ax.scatter(p[:, 1], p[:, column], c=distance, s=.8, cmap='viridis', vmin=0, vmax=.6, rasterized=True)
        ax.set_aspect('equal'); ax.set_xlabel('Y outboard, mm'); ax.set_ylabel('XYZ'[column]+', mm'); ax.grid(alpha=.2)
        ax.axvline(0, color='#777777', lw=.7, ls='--')
    fig.subplots_adjust(left=.08, right=.88, top=.88, bottom=.12, hspace=.35)
    bar = fig.colorbar(dots, cax=fig.add_axes([.92, .18, .018, .58])); bar.set_label('Distance to CAD, mm (saturates at 0.6)')
    fig.suptitle('HSM-000061 · neoFit ABU44M-E — captured fitting and nut against CAD', fontsize=15)
    fig.text(.08, .025, '954 frames • 0.10 mm native fusion • Y0 = fixed-flange panel seat • thread crest envelope', fontsize=10)
    fig.savefig(HERE/'scan-model-check.png', dpi=140, facecolor=fig.get_facecolor())
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
