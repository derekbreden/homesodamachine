"""One-task comparison of the fitted ASSE solid with retained native observations."""
from pathlib import Path
import hashlib
import json
import os
import sys

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'g-ganen-pump'))
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
    os.environ['HSM_NO_BUILD_LOCK'] = '1'
    import multiplex_asse1022 as model
    evidence = json.loads((HERE / 'scan-evidence.json').read_text())
    p, n, _ = load_cloud(evidence['retained_cloud']['path'], evidence['retained_cloud']['sha256'])
    p, n = voxel_sample(p, n, .30)
    shape = model.build()
    vertices, faces = shape.tessellate(.025, .08)
    mesh = trimesh.Trimesh(vertices=[v.toTuple() for v in vertices], faces=faces, process=False)
    distances = np.empty(len(p))
    for start in range(0, len(p), 1200):
        stop = min(start + 1200, len(p))
        _, distances[start:stop], _ = trimesh.proximity.closest_point(mesh, p[start:stop])
    vent = ((np.hypot(p[:, 0] - model.VENT_X, p[:, 1] - model.VENT_Y) < 7)
            & (p[:, 2] < 13.1))
    regions = {
        'inlet_thread_envelope_and_mouth': p[:, 0] < 12.7,
        'inlet_collar': (p[:, 0] >= 12.7) & (p[:, 0] < 17.8),
        'main_wrench': (p[:, 0] >= 17.8) & (p[:, 0] < 31.9) & ~vent,
        'body_waist': (p[:, 0] >= 31.9) & (p[:, 0] < 36.1),
        'outlet_cap': (p[:, 0] >= 36.1) & (p[:, 0] < 49.2),
        'outlet_thread_and_flare_mouth': p[:, 0] >= 49.2,
        'vent': vent,
    }
    bb = shape.BoundingBox()
    report = {
        'units': 'mm', 'method': 'Unit-scale observations to analytic CAD tessellated at 0.025 mm; no distance rejection.',
        'model_source_sha256': sha(HERE / 'multiplex_asse1022.py'),
        'step_sha256': sha(HERE / 'multiplex-asse1022.step'),
        'scan_evidence_sha256': sha(HERE / 'scan-evidence.json'),
        'retained_cloud_sha256': evidence['retained_cloud']['sha256'],
        'observation_voxel_mm': .30, 'solid_valid': shape.isValid(), 'solids': len(shape.Solids()),
        'bounds_mm': {'min': [bb.xmin, bb.ymin, bb.zmin], 'max': [bb.xmax, bb.ymax, bb.zmax]},
        'interfaces': {k: getattr(model, k)() for k in ('inlet', 'outlet', 'vent')},
        'all_retained_observations': summary(distances),
        'features': {k: summary(distances[s]) for k, s in regions.items()},
        'limits': evidence['limits'],
    }
    (HERE / 'scan-model-check.json').write_text(json.dumps(report, indent=2) + '\n')
    cache = HERE.parents[2] / '.cache/asse-scan'
    cache.mkdir(parents=True, exist_ok=True)
    np.savez(cache / 'comparison.npz', p=p, n=n, distance=distances)

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig = plt.figure(figsize=(14, 9), facecolor='#faf9f6')
    ax = fig.add_subplot(2, 2, 1, projection='3d')
    triangle = mesh.vertices[mesh.faces]
    normals = np.cross(triangle[:, 1] - triangle[:, 0], triangle[:, 2] - triangle[:, 0])
    normals /= np.maximum(np.linalg.norm(normals, axis=1)[:, None], 1e-8)
    light = np.array([-.4, -.6, .8]); light /= np.linalg.norm(light)
    shade = .45 + .5 * np.maximum(0, normals @ light)
    color = np.array([.73, .57, .27])[None, :] * shade[:, None]
    ax.add_collection3d(Poly3DCollection(triangle, facecolors=color, edgecolors='none'))
    ax.set_xlim(0, 65.05); ax.set_ylim(-20, 20); ax.set_zlim(0, 43)
    ax.set_box_aspect((65, 40, 43)); ax.view_init(elev=24, azim=-54)
    ax.set_axis_off(); ax.set_title('Fitted exterior • STEP / STL', fontsize=13)
    dots = None
    for position, (i, j), title in [(2, (0, 2), 'Side'), (3, (0, 1), 'Top'), (4, (1, 2), 'End')]:
        ax = fig.add_subplot(2, 2, position)
        dots = ax.scatter(p[:, i], p[:, j], c=distances, s=.6, cmap='viridis', vmin=0, vmax=.6, rasterized=True)
        ax.set_aspect('equal'); ax.set_xlabel('XYZ'[i] + ', mm'); ax.set_ylabel('XYZ'[j] + ', mm')
        ax.set_title(title + ' • observed surface'); ax.grid(alpha=.18)
    fig.subplots_adjust(left=.06, right=.9, top=.88, bottom=.09, wspace=.27, hspace=.3)
    bar = fig.colorbar(dots, cax=fig.add_axes([.93, .18, .015, .58]))
    bar.set_label('Distance to CAD, mm (saturates at 0.6)')
    fig.suptitle('Multiplex ASSE 1022 — captured sample and fitted exterior', fontsize=17, y=.96)
    fig.text(.06, .025, '686 frames • 0.10 mm fusion • native scale • threads use crest envelopes • underside continued from fitted profiles', fontsize=10)
    fig.savefig(HERE / 'scan-model-check.png', dpi=150, facecolor=fig.get_facecolor())
    print(json.dumps({'valid': report['solid_valid'], 'solids': report['solids'],
                      'all': report['all_retained_observations'], 'features': report['features']}, indent=2))


if __name__ == '__main__':
    main()
