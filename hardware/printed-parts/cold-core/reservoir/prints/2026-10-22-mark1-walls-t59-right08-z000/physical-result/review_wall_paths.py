from pathlib import Path
import sys,json,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=next(p for p in Path(__file__).resolve().parents if (p/'tools/gcode/toolpaths.py').exists())
sys.path.insert(0,str(root/'tools/gcode'))
from toolpaths import read_runs
cache=Path(__file__).resolve().parent
files={'angle10':root/'.cache/reservoir-walls-only-right08/slice/plate_1.gcode','angle59':root/'.cache/reservoir-walls-t59-right08/slice/plate_1.gcode'}
report={'scope':'Native XY paths and extrusion starts/ends; photo-to-toolpath position registration and physical causality are unverified.','sources':{},'layers':[]};fig,axes=plt.subplots(1,2,figsize=(11,7),layout='constrained')
all_data={}
for label,p in files.items():
 text=p.read_text();parts=text.split('; CHANGE_LAYER');report['sources'][label]={'gcode_sha256':hashlib.sha256(text.encode()).hexdigest()}
 keep=[119,399,699];data={}
 for n in keep:
  segment=parts[0]+'; CHANGE_LAYER'+parts[n+1]
  rs=read_runs(segment,object_id=2401,features=('Inner wall','Outer wall','Overhang wall'))
  out=[]
  for r in rs:
   pts=r['pts'];out.append({'start':pts[0].tolist(),'end':pts[-1].tolist(),'length_mm':float(np.linalg.norm(np.diff(pts[:,:2],axis=0),axis=1).sum()),'closed_distance_mm':float(np.linalg.norm(pts[0,:2]-pts[-1,:2])),'z_min_max_mm':[float(pts[:,2].min()),float(pts[:,2].max())],'xy_bounds_mm':[pts[:,:2].min(axis=0).tolist(),pts[:,:2].max(axis=0).tolist()]})
  data[n]={'z':rs[0]['z'],'runs':out,'raw':rs}
 all_data[label]=data
 ax=axes[0 if label=='angle10' else 1]
 for r in data[119]['raw']:
  pxy=r['pts'][:,:2];ax.plot(*pxy.T,lw=.8);ax.scatter(*pxy[0],s=13,marker='o',c='red');ax.scatter(*pxy[-1],s=13,marker='x',c='black')
 ax.set_aspect('equal');ax.set_title(label+' — layer 120');ax.set_xlabel('Plate X mm');ax.set_ylabel('Plate Y mm')
for n in [119,399,699]:
 row={'layer':n+1,'z_mm':all_data['angle59'][n]['z']}
 for label in files:row[label]={'run_count':len(all_data[label][n]['runs']),'runs':all_data[label][n]['runs']}
 report['layers'].append(row)
fig.savefig(cache/'wall-paths.png',dpi=150)
(cache/'wall-paths.json').write_text(json.dumps(report,indent=2)+'\n')
for row in report['layers']:
 print(json.dumps({'layer':row['layer'],'z_mm':row['z_mm'],**{k:row[k] for k in files}}))
