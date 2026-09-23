"""Compare retained WR1110 observations to the analytic CAD surface, without trimming errors."""
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


def summary(d):
    return {'samples': len(d), 'p50_p90_p95_p99_max_mm': np.quantile(d, [.5,.9,.95,.99,1]).tolist(),
            'fraction_over_0_25mm': float(np.mean(d > .25)),
            'fraction_over_0_5mm': float(np.mean(d > .5))}


def main():
    os.environ['HSM_NO_BUILD_LOCK'] = '1'
    import wr1110_regulator as model
    evidence = json.loads((HERE / 'scan-measurements.json').read_text())
    p,n,_ = load_cloud(evidence['merged_cloud']['path'], evidence['merged_cloud']['sha256'])
    p,n = voxel_sample(p,n,.25)
    model.stations_hold()
    shape = model.import_step(str(model.STEP)).val()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise ValueError('The regulator must be one valid solid')
    vertices, faces = shape.tessellate(.025, .1)
    mesh = trimesh.Trimesh(vertices=[v.toTuple() for v in vertices], faces=faces, process=False)
    distances = np.empty(len(p)); nearest = np.empty_like(p)
    for start in range(0,len(p),1500):
        end=min(start+1500,len(p))
        nearest[start:end],distances[start:end],_ = trimesh.proximity.closest_point(mesh,p[start:end])
    r=np.hypot(p[:,0],p[:,2]); y=p[:,1]
    regions={
        'barrel': (y>15)&(y<49.5),
        'inlet_wrench_and_rounds': (y<14.65)&(r>8),
        'inlet_face': (y<.5)&(r>7.2)&(r<9)&(n[:,1]<-.9),
        'inlet_visible_mouth': (y<6)&(r<7.2),
        'outlet_wrench_and_rounds': (y>50.05)&(y<54.47)&(r>8),
        'outlet_shoulder': (y>54)&(y<54.8)&(r>7.2)&(r<9)&(n[:,1]>.9),
        'stub_and_thread_envelope': (y>54.47)&(r>4.5),
        'outlet_visible_mouth': (y>61)&(r<4.5),
    }
    report={
        'units':'mm', 'method':'Unit-scale registered observations to tessellated analytical CAD; no distance-based exclusion.',
        'model_source_sha256':sha(HERE/'wr1110_regulator.py'),
        'exported_step_sha256':sha(model.STEP),
        'observations_sha256':evidence['merged_cloud']['sha256'],
        'observation_voxel_mm':.25, 'cad_tessellation_mm':.025,
        'all_retained_observations':summary(distances),
        'features':{name:summary(distances[mask]) for name,mask in regions.items()},
        'solid_valid':True, 'solids':1,
        'limits':['Agreement describes the coated scan, not independent absolute accuracy.',
                  'Thread grooves use a smooth crest envelope; end rounds use short conical sections.',
                  'Mouth closures and internal pressure-control surfaces are unobserved and are not qualified.']}
    (HERE/'scan-model-check.json').write_text(json.dumps(report,indent=2)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(2,1,figsize=(12,6))
    for ax,coord,label in zip(axs,[2,0],['Z','X']):
        order=np.argsort(p[:,0] if coord==2 else p[:,2])
        dots=ax.scatter(y[order],p[order,coord],c=distances[order],s=1,cmap='turbo',vmin=0,vmax=.5)
        ax.set_aspect('equal');ax.set_xlabel('Y, mm');ax.set_ylabel(label+', mm')
    fig.colorbar(dots,ax=axs,label='Distance to model, mm (saturates at 0.5)',fraction=.018)
    fig.suptitle('WR1110: both retained scan surfaces against analytical CAD')
    fig.savefig(HERE/'scan-model-check.png',dpi=150,bbox_inches='tight')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
