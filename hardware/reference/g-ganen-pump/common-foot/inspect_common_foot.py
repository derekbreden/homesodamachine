"""Inspect retained native observations in one rigid local frame per rubber foot."""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
REF = HERE.parent
ROOT = REF.parents[2]
CACHE = ROOT / '.cache/g-ganen-common-foot'
sys.path.insert(0, str(REF))
from scan_tools import load_cloud, transform_points, unit


def run():
    data = json.loads((REF/'reference-parameters.json').read_text())
    measured = json.loads((REF/'registered-measurements.json').read_text())
    CACHE.mkdir(parents=True, exist_ok=True)
    records = []
    for source in measured['passes']:
        identity = source['id']
        p, n, checked = load_cloud(source['source']['path'], source['source']['sha256'])
        transform = np.array(source['native_to_reference'])
        p = transform_points(p, transform)
        n = n @ transform[:3, :3].T
        for foot in data['mounting_feet']:
            side = -1 if 'yminus' in foot['id'] else 1
            observed = next(v for v in foot['pose_observations'] if v['pass'] == identity)
            frame = observed['local_slot_sections']
            if 'reference_to_local_rotation' not in frame:
                frame = foot['pose_observations'][0]['local_slot_sections']
            origin = np.array(frame['local_origin_reference_mm'])
            z = np.array(frame['reference_to_local_rotation'])[2]
            y = unit(np.array([0, side, 0])-z*z[1]*side)
            x = np.cross(y, z)
            rotation = np.array([x, y, z])
            assert np.linalg.det(rotation) > .999999
            # Retain the original measured foot pose; do not combine extrema
            # from differently bent feet into a new convex solid.
            nominal_center_x = observed['translation_basis'].get('center_x_mm')
            if nominal_center_x is None:
                nominal_center_x = origin[0]
            region = ((abs(p[:, 0]-nominal_center_x) < 12)
                      & (p[:, 1]*side > 22) & (p[:, 1]*side < 49.5)
                      & (p[:, 2] > -2.5) & (p[:, 2] < 24))
            indices = np.flatnonzero(region)
            cloud = (p[region]-origin) @ rotation.T
            normal = n[region] @ rotation.T
            cache = CACHE/f'{identity}-{foot["id"]}.npz'
            np.savez_compressed(cache, points=cloud, normals=normal,
                                native_indices=indices, origin=origin, rotation=rotation)
            records.append({'pass': identity, 'foot': foot['id'], 'source': checked,
                            'points': len(cloud), 'origin_reference_mm': origin.tolist(),
                            'reference_to_local_rotation': rotation.tolist(),
                            'cache': str(cache),
                            'scope': 'Unit scale; rigid per-foot frame. Local +Y is outward; +Z is above the observed bearing plane. Pump/rail points near the inner edge remain visible for classification.'})
    fig, axes = plt.subplots(4, 3, figsize=(15, 16), constrained_layout=True)
    for row, foot in enumerate(data['mounting_feet']):
        for record in [v for v in records if v['foot'] == foot['id']]:
            cloud = np.load(record['cache'])
            p = cloud['points'][::5]
            color = {'pass-01-feet-up': '#264b96', 'pass-02-on-back': '#b25f17', 'pass-03-feet-down': '#329d76'}[record['pass']]
            for ax, (a,b) in zip(axes[row], [(0,1),(1,2),(0,2)]):
                ax.scatter(p[:,a],p[:,b],s=.16,alpha=.55,color=color,rasterized=True,label=record['pass'])
        for col, ax in enumerate(axes[row]):
            ax.set_aspect('equal');ax.grid(alpha=.2)
            ax.set_title(foot['id'] + ' · ' + ['axial / outward','outward / height','axial / height'][col])
        axes[row,0].set_xlim(-12,12);axes[row,0].set_ylim(-17,12)
        axes[row,1].set_xlim(-17,12);axes[row,1].set_ylim(-3,25)
        axes[row,2].set_xlim(-12,12);axes[row,2].set_ylim(-3,25)
    axes[0,0].legend(markerscale=8,fontsize=7)
    fig.suptitle('G Ganen purchased rubber feet · retained unit-scale scan observations\nRigid local frames; no smoothing, scaling or convex-hull filling',fontsize=16)
    fig.savefig(HERE/'registered-foot-views.png',dpi=150)
    (HERE/'inspection-inputs.json').write_text(json.dumps({'status':'native_scan_inspection','records':records,'input_sha256':{str(REF/name):hashlib.sha256((REF/name).read_bytes()).hexdigest() for name in ['reference-parameters.json','registered-measurements.json']}},indent=2)+'\n')
    print(HERE/'registered-foot-views.png')

if __name__ == '__main__': run()
