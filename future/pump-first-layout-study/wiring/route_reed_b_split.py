"""Counted four-plus-four reed-B routes after the accepted35mm bore exit."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
import cadquery as cq
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
sys.path[:0]=[str(HERE),str(STUDY)]
from controls_looms import port,hull,circle_points
from controls_harness import ControlsGuide
import native_harness as nh
original_sweep=nh.sweep;nh.RADIUS=4.7
nh.sweep=lambda points,diameter,radius=4.7,with_centerline=False:original_sweep(points,diameter,4.7,with_centerline)
ports=[];pairs=[]
for label,x,y,endx,gx in [('signals',-33.25,205,-17,-21.75),('ground',-28.75,200,-12.5,-26.25)]:
 a=port('control-reed-B-bare-fork',(x,189.3,287.5),(0,0,1),'Reed-B '+label+' source')
 a['lead_paths']=[[a['point'],[x,189.3,296.2],[x,y,296.2],[endx,y,296.2]]]
 b=port('control-service-fork-B',(gx,404,327.45),(0,1,0),'Reed-B '+label+' aft dock')
 b['lead_paths']=[[b['point'],[gx,409.4,327.45]],[b['point'],[gx,412.4,327.45]]]
 for p in [a,b]:p['diameter_mm']=4.3
 ports.extend([a,b]);pairs.append((label,a,b))
g=ControlsGuide(ports,diameter=4.3)
sourcefork=hull(circle_points((-31,189.3,283),(0,0,1),6.4)+circle_points((-33.25,189.3,287.5),(0,0,1),4.3)+circle_points((-28.75,189.3,287.5),(0,0,1),4.3))
aftfork=hull(circle_points((-26.25,404,327.45),(0,1,0),4.3)+circle_points((-21.75,404,327.45),(0,1,0),4.3)+circle_points((-29,399.7,326.4),(0,-1,0),4.3)+circle_points((-19,399.7,326.4),(0,-1,0),4.3))
reserves=json.loads((HERE/'control-reserves.json').read_text());chunks=[]
fanouts=json.loads((HERE/'control-fanouts-check.json').read_text())
reserves['parts'].update({'control-'+n:r for n,r in fanouts['parts'].items()})
for name,r in reserves['parts'].items():
 if name=='control-service-fork-B':continue
 s=cq.Shape.importBrep(str(ROOT/r['brep']));g.obstacles[name]=s;chunks.append(nh.occupied_points(name,s,r['brep']))
for name,s in [('control-reed-B-bare-fork',sourcefork),('control-service-fork-B',aftfork)]:
 g.obstacles[name]=s;chunks.append(nh.occupied_points(name,s,None))
g.voxels=np.vstack([g.voxels,*chunks]);g.refresh();pieces=[];records=[];failures=[]
for label,a,b in pairs:
 try:
  g.refresh();s,r=g.route(a,b,'control-service-reeds-B-'+label);pieces.append(s);records.append(r)
 except ValueError as e:failures.append({'route':label,'reason':str(e)});print(str(e),flush=True)
if len(pieces)==2:
 common=abs(pieces[0].intersect(pieces[1],tol=.0001).Volume(tol=1e-9))
 if common>.001:failures.append({'reason':'Counted4-wire branches overlap','common_mm3':common})
if not failures:
 stem=cq.Solid.makeCylinder(3.2,35,cq.Vector(-31,189.3,248),cq.Vector(0,0,1))
 pieces.extend([stem,sourcefork]);shape=cq.Compound.makeCompound(pieces)
 out=ROOT/'.cache/pump-first-layout/wiring/controls-looms';out.mkdir(parents=True,exist_ok=True)
 path=out/'control-service-reeds-B-split-proved.brep';shape.exportBrep(str(path));fpath=out/'control-service-fork-B-split.brep';aftfork.exportBrep(str(fpath))
 report={'pass':True,'brep':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
  'aft_fork':{'brep':str(fpath.relative_to(ROOT)),'sha256':hashlib.sha256(fpath.read_bytes()).hexdigest()},
  'branches':records,'conductor_count':8,'actual_bore_mm':6.8,'normal_exit_from_lid_base_mm':35,
  'branch_diameter_mm':4.3,'branch_radius_mm':4.7,'minimum_nominal_branch_wire_centre_radius_mm':4.7-1.8/2**.5,
  'scope':'Counted eight-wire actual-bore trunk; bare four-plus-four fork follows the complete35mm normal exit, then two exactR4.7 outer routes. Individual fork dressing and terminal retention remain unqualified.'}
else:report={'pass':False,'failures':failures}
(HERE/'reed-b-split-route.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
