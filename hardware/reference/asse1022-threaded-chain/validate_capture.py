"""Compare the captured full-chain exterior with its six-body CAD reference."""
from pathlib import Path
import json
import os
import shutil
import sys

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'g-ganen-pump'))
from scan_tools import load_cloud
from register_scan import voxel_sample
from analyze_capture import sha


def summary(d):
    return {'samples': len(d), 'p50_p90_p95_p99_max_mm': np.quantile(d, [.5, .9, .95, .99, 1]).tolist(),
            'fraction_within_0_25_mm': float(np.mean(d <= .25)),
            'fraction_within_0_50_mm': float(np.mean(d <= .5))}


def main():
    os.environ['HSM_NO_BUILD_LOCK'] = '1'
    import asse1022_threaded_chain as model
    evidence = json.loads((HERE / 'scan-evidence.json').read_text())
    p, n, _ = load_cloud(evidence['retained_cloud']['path'], evidence['retained_cloud']['sha256'])
    p, n = voxel_sample(p, n, .30)
    meshes, components, render_parts, shapes = [], {}, [], []
    for name, shape in model.parts().items():
        shapes.append(shape)
        vertices, faces = shape.tessellate(.025, .08)
        v = np.array([x.toTuple() for x in vertices]); f = np.asarray(faces)
        triangles = v[f]
        area = np.linalg.norm(np.cross(triangles[:, 1]-triangles[:, 0], triangles[:, 2]-triangles[:, 0]), axis=1)
        mesh = trimesh.Trimesh(vertices=v, faces=f[area > 1e-12], process=False)
        meshes.append(mesh)
        components[name] = {'valid': shape.isValid(), 'solid_count': len(shape.Solids()),
                            'vertices': len(v), 'triangles': len(f)}
        color = model.COLORS[name].toTuple()
        render_parts.append({'name': name, 'vertices': v.tolist(), 'faces': f.tolist(), 'color': color[:3]})
    mesh = trimesh.util.concatenate(meshes)
    distance = np.empty(len(p))
    for start in range(0, len(p), 1000):
        stop = min(start + 1000, len(p))
        _, distance[start:stop], _ = trimesh.proximity.closest_point(mesh, p[start:stop])
    regions = {'pp010822e': p[:, 0] < -20.725,
               'gagira': (p[:, 0] >= -20.725) & (p[:, 0] < 6.1),
               'asse': (p[:, 0] >= 6.1) & (p[:, 0] < 51.5),
               'pi4512f6s': (p[:, 0] >= 51.5) & (p[:, 0] < 88.2),
               'pp061208w': (p[:, 0] >= 88.2) & (p[:, 0] < 107.8),
               'atbu444-e': p[:, 0] >= 107.8}
    bb = mesh.bounds
    report = {'units': 'mm', 'method': 'Retained native observations to CAD tessellation at 0.025 mm; unit-scale rigid registration; no CAD-distance rejection.',
              'source_sha256': sha(HERE / 'asse1022_threaded_chain.py'),
              'parameters_sha256': sha(HERE / 'reference-parameters.json'),
              'bare_asse_source_sha256': sha(HERE.parent / 'multiplex-asse1022/multiplex_asse1022.py'),
              'step_sha256': sha(HERE / 'asse1022-threaded-chain.step'),
              'scan_evidence_sha256': sha(HERE / 'scan-evidence.json'),
              'retained_cloud_sha256': evidence['retained_cloud']['sha256'],
              'observation_voxel_mm': .30, 'components': components,
              'bounds_mm': bb.tolist(), 'extent_mm': (bb[1]-bb[0]).tolist(),
              'ports': model.ports(), 'all_retained_observations': summary(distance),
              'regions': {k: summary(distance[s]) for k, s in regions.items()},
              'limits': evidence['limits'] + ['Blind mouth closures and buried joint continuations are unqualified display geometry.']}
    (HERE / 'scan-model-check.json').write_text(json.dumps(report, indent=2)+'\n')
    cache = HERE.parents[2] / '.cache/asse-chain-scan'; cache.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache / 'comparison.npz', p=p, n=n, distance=distance)
    archive = Path(evidence['native_project_archive']).parents[1]
    shutil.copy2(HERE / 'asse1022-threaded-chain.step', archive / 'asse1022-threaded-chain.step')
    model.cq.exporters.export(model.cq.Compound.makeCompound(shapes),
        str(archive / 'asse1022-threaded-chain.stl'), tolerance=.025, angularTolerance=.08)
    (cache / 'render-mesh.json').write_text(json.dumps({'parts': render_parts, 'output': str(archive/'preview.png')}))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 1, figsize=(14, 7), facecolor='#faf9f6')
    for ax, column in zip(axes, [2, 1]):
        dots = ax.scatter(p[:, 0], p[:, column], c=distance, s=.5, cmap='viridis', vmin=0, vmax=.6, rasterized=True)
        ax.set_aspect('equal'); ax.set_xlabel('X, mm'); ax.set_ylabel('XYZ'[column]+', mm'); ax.grid(alpha=.2)
    fig.subplots_adjust(left=.06, right=.9, top=.87, bottom=.12, hspace=.35)
    color = fig.colorbar(dots, cax=fig.add_axes([.93, .18, .015, .58])); color.set_label('Distance to CAD, mm (saturates at 0.6)')
    fig.suptitle('Threaded ASSE chain — captured exterior against the six-part CAD', fontsize=16)
    fig.text(.06, .025, '1,191 frames • 0.10 mm fusion • native scale • hidden underside continued from analytic profiles', fontsize=10)
    fig.savefig(HERE / 'scan-model-check.png', dpi=150, facecolor=fig.get_facecolor())
    print(json.dumps({'components': components, 'all': report['all_retained_observations'], 'regions': report['regions']}, indent=2))


if __name__ == '__main__':
    main()
