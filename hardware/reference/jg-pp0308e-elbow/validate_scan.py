"""Measure distances from every retained observation to the exported exterior CAD."""
from pathlib import Path
import json, hashlib
import numpy as np
import trimesh
import cadquery as cq
HERE=Path(__file__).resolve().parent
from scan_tools import observations, material_mask

def voxel_sample(p,n,spacing):
 _,indices=np.unique(np.floor(p/spacing).astype(np.int64),axis=0,return_index=True)
 return p[indices],n[indices]

def summary(d):
 return {'samples':len(d),'p50_p90_p95_p99_max_mm':np.quantile(d,[.5,.9,.95,.99,1]).tolist(),'fraction_over_0_25mm':float(np.mean(d>.25))}

def main():
 p,n,h=observations()
 # Fixed geometric exclusion of fixture and table, independent of CAD error.
 keep=material_mask(p,h)
 p,n=voxel_sample(p[keep],n[keep],.25)
 shape=cq.importers.importStep(str(HERE/'jg-pp0308e-elbow.step')).val()
 solids=shape.Solids()
 assert len(solids)==3 and all(s.isValid() for s in solids)
 verts,faces=shape.tessellate(.025,.1)
 mesh=trimesh.Trimesh(vertices=[v.toTuple() for v in verts],faces=faces,process=False)
 dist=np.empty(len(p))
 for start in range(0,len(p),1000):
  _,dist[start:start+1000],_=trimesh.proximity.closest_point(mesh,p[start:start+1000])
 regions={'bend':(p[:,1]<6.7)&(p[:,2]<6.7),'y_fixed_body':(p[:,1]>7)&(p[:,1]<18.8),'z_fixed_body':(p[:,2]>7)&(p[:,2]<18.8),'y_release_face':(p[:,1]>20.3)&(n[:,1]>.9),'y_collet':p[:,1]>18.9,'z_collet_symmetry_completion':p[:,2]>18.9}
 for leg,a in [('y',1),('z',2)]:
  r=np.linalg.norm(np.delete(p,a,1),axis=1)
  regions[leg+'_root_band']=(p[:,a]>8.3)&(p[:,a]<10.8)&(r>6.3)
  regions[leg+'_collar_band']=(p[:,a]>13.6)&(p[:,a]<15.8)&(r>7.5)
 report={'units':'mm','coordinate_scale_factor':1.0,'method':'Closest distance to CAD triangles, all retained observations, no distance-based exclusion. Regions may overlap.','observation_voxel_mm':.25,'cad_tessellation_mm':.025,'solid_valid':True,'solids':3,'all_retained_observations':summary(dist),'features':{k:summary(dist[v]) for k,v in regions.items() if v.sum()},'step_sha256':hashlib.sha256((HERE/'jg-pp0308e-elbow.step').read_bytes()).hexdigest()}
 (HERE/'scan-model-check.json').write_text(json.dumps(report,indent=2)+'\n')
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axs=plt.subplots(1,2,figsize=(12,5))
 for ax,(a,b) in zip(axs,[(1,2),(0,1)]):
  pts=ax.scatter(p[:,a],p[:,b],c=dist,s=1,cmap='turbo',vmin=0,vmax=.5);ax.set(xlabel='XYZ'[a]+' (mm)',ylabel='XYZ'[b]+' (mm)',aspect='equal')
 fig.colorbar(pts,ax=axs,label='Distance to CAD (mm), saturates at 0.5',fraction=.025);fig.suptitle('Elbow: observed surface compared with editable exterior CAD')
 fig.savefig(HERE/'scan-model-check.png',dpi=160,bbox_inches='tight')
 print(json.dumps(report,indent=2))

if __name__=='__main__':main()
