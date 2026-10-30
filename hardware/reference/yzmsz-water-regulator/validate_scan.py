"""Compare the delivered YZMSZ STEP with all physically retained observations."""
from pathlib import Path
import json
import shutil
import sys

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
from analyze_scan import sha, ARCHIVE
sys.path.insert(0, str(HERE.parent / 'g-ganen-pump'))
from scan_tools import load_cloud
from register_scan import voxel_sample


def summary(d):
    return {'samples': len(d), 'p50_p90_p95_p99_max_mm': np.quantile(d, [.5, .9, .95, .99, 1]).tolist(),
            'fraction_within_0_25_mm': float(np.mean(d <= .25)),
            'fraction_within_0_50_mm': float(np.mean(d <= .5))}


def main():
    evidence = json.loads((HERE / 'scan-evidence.json').read_text())
    source = evidence['retained_cloud']
    p, n, _ = load_cloud(source['path'], source['sha256'])
    p, n = voxel_sample(p, n, .30)
    step = HERE / 'geometry/yzmsz-water-regulator.step'
    shape = cq.importers.importStep(str(step)).val()
    vertices, faces = shape.tessellate(.025, .08)
    v = np.array([x.toTuple() for x in vertices]); f = np.array(faces)
    mesh = trimesh.Trimesh(vertices=v, faces=f, process=False)
    distance = np.empty(len(p))
    for start in range(0, len(p), 1000):
        stop = min(start+1000, len(p))
        _, distance[start:stop], _ = trimesh.proximity.closest_point(mesh, p[start:stop])
    report = {'units': 'mm', 'method': 'All physically retained native observations to reopened STEP tessellated at 0.025 mm; no scale fit or CAD-distance rejection.',
              'model_source_sha256': sha(HERE / 'build.py'),
              'parameters_sha256': sha(HERE / 'reference-parameters.json'),
              'step_sha256': sha(step), 'scan_evidence_sha256': sha(HERE / 'scan-evidence.json'),
              'retained_cloud_sha256': source['sha256'], 'observation_voxel_mm': .30,
              'native_solid_valid': shape.isValid(), 'native_solid_count': len(shape.Solids()),
              'bounds_mm': mesh.bounds.tolist(), 'extent_mm': mesh.extents.tolist(),
              'all_retained_observations': summary(distance),
              'regions': {k: summary(distance[mask]) for k, mask in {
                  'inlet_collet_and_collar': p[:, 0] < 9.6,
                  'windowed_cap': (p[:, 0] >= 9.6) & (p[:, 0] < 27.7),
                  'long_housing': (p[:, 0] >= 27.7) & (p[:, 0] < 48.8),
                  'outlet_neck_and_collet': p[:, 0] >= 48.8}.items()},
              'limits': evidence['limits']}
    cq.exporters.export(shape, str(ARCHIVE / 'yzmsz-water-regulator.stl'), tolerance=.025, angularTolerance=.08)
    stl = trimesh.load(str(ARCHIVE / 'yzmsz-water-regulator.stl'), force='mesh')
    report['stl_watertight'] = bool(stl.is_watertight)
    report['stl_triangles'] = len(stl.faces)
    (HERE / 'scan-model-check.json').write_text(json.dumps(report, indent=2)+'\n')
    shutil.copy2(step, ARCHIVE / step.name)
    cache = HERE.parents[2] / '.cache/yzmsz-scan'; cache.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache / 'comparison.npz', p=p, distance=distance, v=v, f=f)
    (cache / 'render-mesh.json').write_text(json.dumps({'parts': [{'name': 'YZMSZ', 'vertices': v.tolist(),
        'faces': f.tolist(), 'color': [.65, .78, .70]}], 'output': str(ARCHIVE / 'preview.png')}))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), facecolor='#faf9f6')
    for ax, column in zip(axes, [2, 1]):
        dots = ax.scatter(p[:, 0], p[:, column], c=distance, s=.7, cmap='viridis', vmin=0, vmax=.6, rasterized=True)
        ax.set_aspect('equal'); ax.set_xlabel('X, mm'); ax.set_ylabel('XYZ'[column]+', mm'); ax.grid(alpha=.2)
    fig.subplots_adjust(left=.08, right=.88, top=.86, bottom=.12, hspace=.35)
    bar = fig.colorbar(dots, cax=fig.add_axes([.92, .18, .018, .58])); bar.set_label('Distance to CAD, mm (saturates at 0.6)')
    fig.suptitle('YZMSZ water regulator — scan against fitted exterior', fontsize=16)
    fig.text(.08, .025, '872 frames • 0.10 mm native fusion • putty-hidden lower sectors continued analytically', fontsize=10)
    fig.savefig(HERE / 'scan-model-check.png', dpi=140, facecolor=fig.get_facecolor())
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
