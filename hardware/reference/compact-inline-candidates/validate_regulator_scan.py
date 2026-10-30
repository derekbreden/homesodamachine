"""One-task surface comparison of the delivered PISCO STEP to its capture."""
from pathlib import Path
import hashlib
import json
import shutil
import sys

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ARCHIVE = Path.home() / 'Documents/3D Scans/2026-10-29-pisco-rvfup-regulator'
sys.path.insert(0, str(HERE.parent / 'g-ganen-pump'))
from scan_tools import load_cloud
from register_scan import voxel_sample


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def summary(d):
    return {'samples': len(d), 'p50_p90_p95_p99_max_mm': np.quantile(d, [.5, .9, .95, .99, 1]).tolist(),
            'fraction_within_0_25_mm': float(np.mean(d <= .25)),
            'fraction_within_0_50_mm': float(np.mean(d <= .5))}


def main():
    evidence = json.loads((HERE / 'regulator-scan-evidence.json').read_text())
    source = evidence['retained_cloud']
    p, n, _ = load_cloud(source['path'], source['sha256'])
    p, n = voxel_sample(p, n, .30)
    step = HERE / 'geometry/candidate-regulator.step'
    shape = cq.importers.importStep(str(step)).val()
    vertices, faces = shape.tessellate(.025, .08)
    v = np.array([x.toTuple() for x in vertices]); f = np.array(faces)
    mesh = trimesh.Trimesh(vertices=v, faces=f, process=False)
    distance = np.empty(len(p))
    for start in range(0, len(p), 1000):
        stop = min(start+1000, len(p))
        _, distance[start:stop], _ = trimesh.proximity.closest_point(mesh, p[start:stop])
    solids = shape.Solids()
    united = solids[0].fuse(*solids[1:]).clean()
    stl_path = ARCHIVE / 'pisco-rvfup-regulator.stl'
    cq.exporters.export(united, str(stl_path), tolerance=.025, angularTolerance=.08)
    stl = trimesh.load(str(stl_path), force='mesh')
    report = {'units': 'mm', 'method': 'All physically retained native observations to reopened four-body STEP tessellated at 0.025 mm; no scale fit or CAD-distance rejection.',
              'model_source_sha256': sha(HERE / 'build.py'),
              'parameters_sha256': sha(HERE / 'regulator-scan-parameters.json'),
              'step_sha256': sha(step), 'scan_evidence_sha256': sha(HERE / 'regulator-scan-evidence.json'),
              'retained_cloud_sha256': source['sha256'], 'observation_voxel_mm': .30,
              'native_assembly_valid': shape.isValid(), 'native_solid_count': len(solids),
              'each_solid_valid': [solid.isValid() for solid in solids],
              'stl_union_valid': united.isValid(), 'stl_union_solids': len(united.Solids()),
              'stl_watertight': bool(stl.is_watertight), 'stl_triangles': len(stl.faces),
              'bounds_mm': mesh.bounds.tolist(), 'extent_mm': mesh.extents.tolist(),
              'all_retained_observations': summary(distance),
              'regions': {key: summary(distance[mask]) for key, mask in {
                  'inlet_collet_and_long_neck': p[:, 2] < 16.,
                  'main_housing_and_rings': (p[:, 2] >= 16.) & (p[:, 2] < 43.),
                  'outlet_fitting_and_collet': p[:, 2] >= 43.}.items()},
              'limits': evidence['limits']}
    (HERE / 'regulator-scan-model-check.json').write_text(json.dumps(report, indent=2)+'\n')
    shutil.copy2(step, ARCHIVE / 'pisco-rvfup-regulator.step')
    cache = HERE.parents[2] / '.cache/pisco-scan'; cache.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache / 'comparison.npz', p=p, distance=distance, v=v, f=f)
    parts = []
    for name in ('body', 'outlet_fitting', 'inlet_collet', 'outlet_collet'):
        data = np.load(HERE / f'geometry/candidate-regulator-{name}.npz')
        color = [.2, .22, .24] if name == 'body' else [.66, .68, .7] if name == 'outlet_fitting' else [.78, .8, .81]
        # Put the long axis along display X and keep the native UP direction
        # as display Z, for a directly comparable preview beside the YZMSZ.
        display = data['v'][:, [2, 0, 1]]
        parts.append({'name': name, 'vertices': display.tolist(), 'faces': data['f'].tolist(), 'color': color})
    (cache / 'render-mesh.json').write_text(json.dumps({'parts': parts, 'output': str(ARCHIVE / 'preview.png')}))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), facecolor='#faf9f6')
    for ax, column in zip(axes, [1, 0]):
        dots = ax.scatter(p[:, 2], p[:, column], c=distance, s=.7, cmap='viridis', vmin=0, vmax=.6, rasterized=True)
        ax.set_aspect('equal'); ax.set_xlabel('Z along flow, mm'); ax.set_ylabel('XY'[column]+', mm'); ax.grid(alpha=.2)
    fig.subplots_adjust(left=.08, right=.88, top=.86, bottom=.12, hspace=.35)
    bar = fig.colorbar(dots, cax=fig.add_axes([.92, .18, .018, .58])); bar.set_label('Distance to CAD, mm (saturates at 0.6)')
    fig.suptitle('PISCO RVFUP regulator — scan against fitted exterior', fontsize=16)
    fig.text(.08, .025, '1,819 frames • 0.10 mm native fusion • putty-hidden lower sectors continued analytically', fontsize=10)
    fig.savefig(HERE / 'regulator-scan-model-check.png', dpi=140, facecolor=fig.get_facecolor())
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
