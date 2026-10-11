from pathlib import Path
import hashlib,json,sys,zipfile
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path.cwd();F=ROOT/'hardware/printed-parts/faucet';W=ROOT/'.cache/printer-control/faucet-current-review-20261011'
W.mkdir(parents=True,exist_ok=True)
OUT=F/'industrial/prints/2026-10-11-centered-mounting-review-mark2'
sys.path[:0]=[str(F)]
from prepare_display_print import extrusion_segments
from review_vent_prints import filled_section,draw_polygon
physical=json.loads((F/'industrial/physical-acceptance.json').read_text())
accepted_report=json.loads((ROOT/physical['prepared_project']).parent.joinpath('preparation.json').read_text())
current_report=json.loads((F/'industrial/faucet-industrial-petgf.print.json').read_text())
for archive_path,digest,gcode_digest,target in [(ROOT/physical['native_archive'],physical['native_archive_sha256'],physical['gcode_sha256'],W/'accepted.gcode'),(ROOT/json.loads((OUT/'native-check.json').read_text())['native']['archive'],json.loads((OUT/'native-check.json').read_text())['native']['archive_sha256'],json.loads((OUT/'native-check.json').read_text())['native']['gcode_sha256'],W/'current-tip-review.gcode')]:
 assert hashlib.sha256(archive_path.read_bytes()).hexdigest()==digest
 with zipfile.ZipFile(archive_path) as arc:payload=arc.read('Metadata/plate_1.gcode')
 assert hashlib.sha256(payload).hexdigest()==gcode_digest
 target.write_bytes(payload)
points={}; readings=[]
for label, report, path in [('accepted',accepted_report,W/'accepted.gcode'),('current',current_report,W/'current-tip-review.gcode')]:
 row=report['parts'][1];rotation=np.array(row['build_transform'][:9]).reshape(3,3).T
 samples=[]
 for road in extrusion_segments(path):
  if road['object']==row['identify_id'] and road['feature'].startswith('Support'):
   midpoint=(np.array(road['a'])+road['b'])/2
   samples.append((midpoint-row['plate_translation_mm'])@rotation+row['source_center_mm'])
 p=np.array(samples).reshape(-1,3);points[label]=p
 readings.append(dict(label=label,segment_midpoints=len(p),cad_bounds_mm=[p.min(axis=0).tolist(),p.max(axis=0).tolist()]))
 print(label,len(p),flush=True)
np.savez_compressed(W/'tip-support-points.npz',**points)
mesh=trimesh.load(ROOT/current_report['parts'][1]['source'],force='mesh',process=True)
levels=[187.0,195.0,205.0,213.0,220.0,230.0]
fig,axes=plt.subplots(2,3,figsize=(15,9),constrained_layout=True)
sections=[]
for axis,z in zip(axes.flat,levels):
 stock=filled_section(mesh,z)
 draw_polygon(axis,stock,facecolor='#dce0e5',edgecolor='#343b43',linewidth=.65)
 record=dict(source_z_mm=z,midpoint_half_band_mm=.5)
 for label,color,marker in [('accepted','#d86b44','o'),('current','#278c99','+')]:
  near=points[label][np.abs(points[label][:,2]-z)<=.5]
  axis.scatter(near[:,0],near[:,1],s=4,color=color,marker=marker,alpha=.65,label=label)
  record[label+'_midpoints']=len(near)
 axis.set_title('CAD Z%.1f mm'%z);axis.set_aspect('equal');axis.set_xlabel('X / mm');axis.set_ylabel('Y / mm')
 sections.append(record)
axes[0,0].legend()
fig.suptitle('Tip support locations: accepted (orange) and current (blue) on current stock (grey); ±0.5 mm Z band')
image=OUT/'native-tip-support-comparison.png';fig.savefig(image,dpi=170);plt.close(fig)
result=dict(accepted_archive=physical['native_archive'],accepted_archive_sha256=physical['native_archive_sha256'],accepted_gcode_sha256=physical['gcode_sha256'],current_project_sha256=current_report['project_sha256'],current_gcode_sha256=hashlib.sha256((W/'current-tip-review.gcode').read_bytes()).hexdigest(),current_tip_sha256=current_report['parts'][1]['stl_sha256'],samples=readings,sections=sections,image=str(image.relative_to(ROOT)),method='Every labelled native Support path midpoint transformed to CAD; current source STL sections; midpoint overlays use ±0.5 mm bands, not exact bead intersections.',scope='Location and cleanup-access review; unlabelled interfaces and physical removal force are not inferred.')
(OUT/'tip-support-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
