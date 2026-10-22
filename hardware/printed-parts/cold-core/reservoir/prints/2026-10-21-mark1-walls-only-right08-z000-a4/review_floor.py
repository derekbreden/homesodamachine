from pathlib import Path
import sys,json,hashlib,re
import numpy as np
from shapely.geometry import LineString,Polygon
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=next(p for p in Path(__file__).resolve().parents if (p/'tools/gcode/toolpaths.py').exists());sys.path.insert(0,str(root/'tools/gcode'))
from toolpaths import read_runs
folder=root/'.cache/reservoir-walls-only-right08/slice';out=root/'hardware/printed-parts/cold-core/reservoir/prints/2026-10-21-mark1-walls-only-right08-z000-a4'
t=(folder/'plate_1.gcode').read_text();sections=t.split('; CHANGE_LAYER');short='; CHANGE_LAYER'.join(sections[:14]);lines=short.splitlines();width=.8;widths={}
for n,line in enumerate(lines,1):
 if line.startswith('; LINE_WIDTH:'):width=float(line.split(':')[1])
 widths[n]=width
allruns=read_runs(short,object_id=2401,features=('Outer wall','Inner wall','Overhang wall'))
outer=read_runs(short,object_id=2401,features=('Outer wall',))
report={'gcode_sha256':hashlib.sha256(t.encode()).hexdigest(),'body_object_label':2401,'method':'Union of nominal wall-bead XY footprints using emitted per-move widths and arcs sampled at 0.25 mm chords. Target is the enclosing native outer-wall loop buffered by its half-width. All twelve floor layers inspected.','scope':'Commanded XY footprint, not measured deposited shape or a guarantee of fusion/water hold. Scarf Z/flow ramps are not a physical bead model.','floor_layers':[]}
fig,axes=plt.subplots(1,2,figsize=(7,6),layout='constrained')
for layer in range(12):
 runs=[r for r in allruns if r['layer']==layer]
 border=max((Polygon(r['pts'][:,:2]) for r in outer if r['layer']==layer),key=lambda p:p.area).buffer(.4)
 roads=[]
 for r in runs:
  for i,line in enumerate(r['lines']):
   if np.linalg.norm(r['pts'][i+1,:2]-r['pts'][i,:2])>1e-7:roads.append(LineString(r['pts'][i:i+2,:2]).buffer(widths[int(line)]/2,quad_segs=8))
 covered=unary_union(roads);missing=border.difference(covered)
 # Report the interior separately from outer-edge differences caused by tessellation and a seam.
 interior=missing.intersection(border.buffer(-.8))
 report['floor_layers'].append({'layer':layer+1,'z_mm':runs[0]['z'],'wall_runs':len(runs),'nominal_enclosed_area_mm2':round(border.area,4),'uncovered_area_mm2':round(missing.area,6),'uncovered_interior_area_mm2':round(interior.area,6)})
 if layer in [0,11]:
  ax=axes[0 if layer==0 else 1]
  for r in runs:ax.plot(r['pts'][:,0],r['pts'][:,1],color='#1b5b9b',lw=.5)
  for geo in getattr(interior,'geoms',[interior]):
   if geo.geom_type=='Polygon' and not geo.is_empty:ax.fill(*geo.exterior.xy,color='#c3352b')
  ax.set_aspect('equal');ax.set_title(f"Floor layer {layer+1}, Z {runs[0]['z']:.2f} mm");ax.set_xlabel('Plate X (mm)');ax.set_ylabel('Plate Y (mm)')
fig.savefig(out/'floor-wall-paths.png',dpi=160)
(out/'floor-wall-coverage.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
