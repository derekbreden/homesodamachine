"""Read every native back-top support road against its exact protected show faces."""
from pathlib import Path
import argparse,hashlib,json,math,time,zipfile
import cadquery as cq
import numpy as np
from OCP.BRepAdaptor import BRepAdaptor_Surface
from review_roads import layers
import sys
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/docgen').is_dir())
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('job',nargs='?',type=Path,default=ROOT/'.cache/prints/2026-10-07-drain/back-top-mark2')
parser.add_argument('--archive',type=Path)
parser.add_argument('--preparation',type=Path)
args=parser.parse_args();JOB=args.job.resolve();ARCHIVE=args.archive or JOB/'ready/back-top-black-z004-mark2.gcode.3mf';PREP=args.preparation or JOB/'back-top-black-z004-mark2.preparation.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();write=lambda p,d:Path(p).write_text(json.dumps(d,indent=2)+'\n')
start=time.time();prep=json.loads(PREP.read_text());part=prep['parts'][0];STL=ROOT/part['source'];assert sha(STL)==part['stl_sha256'];rot=np.array(part['build_transform'][:9]).reshape(3,3);trans=np.array(part['build_transform'][9:12]);center=np.array(part['source_center_mm']);new=cq.importers.importStep(str(STL.with_suffix('.step'))).val();newfaces=new.Faces();protected=[];same=[]
def bbox(face):
 b=face.BoundingBox();return np.array([b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax])
for i,face in enumerate(newfaces):
 b=face.BoundingBox();n=face.normalAt();c=face.Center();kind=face.geomType();name=None
 if kind=='PLANE' and abs(c.x+107.5)<1e-5 and n.x<-.999:name='west exterior standing wall'
 elif kind=='PLANE' and abs(c.x-107.5)<1e-5 and n.x>.999:name='east exterior standing wall'
 elif kind=='PLANE' and abs(c.y-471.3)<1e-5 and n.y>.999:name='flat rear C14/port field; separate functional contact reading'
 elif kind=='PLANE' and abs(b.zmin-355.)<1e-5 and n.z>.999:name='complete exterior roof bed face'
 elif kind=='PLANE' and b.zmin>351.68 and n.z>.4 and n.x*c.x>90:name='exterior additive roof-side chamfer'
 elif kind=='CYLINDER' and b.zmin>348.99 and n.x*c.x>90 and n.z>.2:name='retained outer R6 roof-side runout'
 elif kind=='CYLINDER' and b.ymin>459.29 and n.x*c.x>50 and n.y>.5:name='exterior rear standing R12 corner'
 if name:
  protected.append((i,face));same.append({'native_face':i,'functional_surface':name,'type':kind,'bounds_cad_mm':bbox(face).tolist(),'native_area_mm2':face.Area()})
assert len(protected)==10,same
aux_faces={r['native_face'] for r in same if r['functional_surface'].startswith('flat rear C14')}
assert len(aux_faces)==1
for r in same:r['scope']='functional rear-port field, outside protected roof transitions' if r['native_face'] in aux_faces else 'protected exterior roof/chamfer/runout/corner/sidewall'
protected_faces=[r for r in same if r['native_face'] not in aux_faces]
assert len(protected_faces)==9
faceboxes=np.array([bbox(f) for i,f in protected]);models=[]
for i,f in protected:
 ad=BRepAdaptor_Surface(f.wrapped);kind=f.geomType();g={'kind':kind}
 if kind=='PLANE':
  plane=ad.Plane();p=plane.Location();d=plane.Axis().Direction();g.update(point=np.array([p.X(),p.Y(),p.Z()]),normal=np.array([d.X(),d.Y(),d.Z()]))
 elif kind=='CYLINDER':
  cy=ad.Cylinder();p=cy.Axis().Location();d=cy.Axis().Direction();g.update(point=np.array([p.X(),p.Y(),p.Z()]),axis=np.array([d.X(),d.Y(),d.Z()]),radius=cy.Radius())
 models.append(g)
count=bboxpairs=analyticpairs=exactpairs=0;contacts=[];minclear=np.inf;maxz=maxw=maxh=0.;details=[]
with zipfile.ZipFile(ARCHIVE) as a:
 gcode_sha=hashlib.sha256(a.read('Metadata/plate_1.gcode')).hexdigest()
 with a.open('Metadata/plate_1.gcode') as data:
  for z,h,roads,commands in layers(data):
   for r in roads:
    if r[7] not in ('Support','Support transition','Support interface'):continue
    assert r[8] in ('G0','G1') and r[4]>0 and r[10]>0,r
    count+=1;maxz=max(maxz,z);maxw=max(maxw,r[4]);maxh=max(maxh,r[10]);w,road_h=r[4],r[10];radius=math.hypot(w,road_h)/2+.00001
    aa=(np.array([r[0],r[1],z-road_h/2])-trans) @ rot.T+center;bb=(np.array([r[2],r[3],z-road_h/2])-trans) @ rot.T+center
    lo,hi=np.minimum(aa,bb),np.maximum(aa,bb);delta=np.maximum(0,np.maximum(faceboxes[:,:3]-hi,lo-faceboxes[:,3:]));lower=np.linalg.norm(delta,axis=1);candidates=np.flatnonzero(lower<=radius)
    bboxpairs+=len(candidates);edge=None
    for j in candidates:
     i,face=protected[j];g=models[j];bound=0.;method='exact native edge-to-face'
     if g['kind']=='PLANE':
      da=np.dot(aa-g['point'],g['normal']);db=np.dot(bb-g['point'],g['normal']);bound=0. if da*db<=0 else min(abs(da),abs(db));method='exact infinite-plane lower bound'
     elif g['kind']=='CYLINDER':
      qa=aa-g['point'];v=bb-aa;pa=qa-np.dot(qa,g['axis'])*g['axis'];pv=v-np.dot(v,g['axis'])*g['axis'];vv=np.dot(pv,pv);t=float(np.clip(-np.dot(pa,pv)/vv,0,1)) if vv>1e-18 else 0.;mn=np.linalg.norm(pa+t*pv);mx=max(np.linalg.norm(pa),np.linalg.norm(pa+pv));rr=g['radius'];bound=0. if mn<=rr<=mx else min(abs(mn-rr),abs(mx-rr));method='exact infinite-cylinder radial-range lower bound'
     if bound>radius:
      analyticpairs+=1;clear=bound-radius
     else:
      if edge is None:edge=cq.Edge.makeLine(cq.Vector(*aa),cq.Vector(*bb))
      bound=face.distance(edge);clear=bound-radius;method='exact native edge-to-face';exactpairs+=1
     minclear=min(minclear,clear)
     detail={'native_face':i,'protected_show_transition':i not in aux_faces,'gcode_line':r[-1],'z_print_mm':z,'feature':r[7],'road_midheight_cad_mm':[aa.tolist(),bb.tolist()],'width_mm':w,'height_mm':road_h,'conservative_radius_mm':radius,'native_centreline_distance_lower_bound_mm':bound,'bead_envelope_clearance_lower_bound_mm':clear,'method':method};details.append(detail)
     if clear<=0:contacts.append(detail)
   if count and count%100000<2000:print(f'{count} support roads; {bboxpairs} bbox candidates; {exactpairs} exact face queries; {len(contacts)} potential contacts',flush=True)
protected_contacts=[r for r in contacts if r['protected_show_transition']]
aux_contacts=[r for r in contacts if not r['protected_show_transition']]
protected_candidates=[r for r in details if r['protected_show_transition']]
aux_candidates=[r for r in details if not r['protected_show_transition']]
protected_min=min((r['bead_envelope_clearance_lower_bound_mm'] for r in protected_candidates),default=None)
aux_record={'source_step_sha256':sha(STL.with_suffix('.step')),'source_stl_sha256':sha(STL),'gcode_sha256':gcode_sha,'native_faces':[r for r in same if r['native_face'] in aux_faces],'potential_actual_bead_contacts':aux_contacts,'candidate_readings':aux_candidates,'method':'All actual fresh support roads receive the same conservative own-width/height capsule test against the full flat rear port plane. The functional C14 port reading is retained separately from the nine protected roof/chamfer/runout/corner/sidewall faces. A conservative capsule witness is a potential support contact, not a claim of physical scarring.','functional_region':'Retained C14 station X66.9 pocket and bore hood crown on the exterior rear port field. The flange pocket floor, receptacle locating faces and insertion opening keep their required stock. Support contacts are released through the exposed rear side before installing the inlet or other hardware.','physical_support_removal_verified':False,'physical_finish_tested':False}
write(JOB/'rear-port-support-contacts.json',aux_record)
record={'pass':not protected_contacts,'source_step_sha256':sha(STL.with_suffix('.step')),'source_stl_sha256':sha(STL),'gcode_sha256':gcode_sha,'protected_show_face_count':len(protected_faces),'protected_show_faces':protected_faces,'auxiliary_functional_face_count':len(aux_faces),'auxiliary_functional_contact_record':'rear-port-support-contacts.json','auxiliary_functional_contact_record_sha256':sha(JOB/'rear-port-support-contacts.json'),'auxiliary_functional_potential_contacts':len(aux_contacts),'support_roads_checked':count,'support_road_max_print_z_mm':maxz,'support_road_max_width_mm':maxw,'support_road_max_height_mm':maxh,'native_bbox_candidate_pairs':bboxpairs,'analytic_surface_lower_bound_exclusions':analyticpairs,'exact_native_edge_to_face_pairs':exactpairs,'minimum_candidate_bead_clearance_lower_bound_mm':protected_min,'potential_bead_contacts':protected_contacts,'candidate_readings':details,'method':'Every emitted support road uses its own width/height capsule. Native face bounding boxes exclude distant capsules. Exact infinite-plane/cylinder distance lower bounds may exclude a finite face only when the lower bound exceeds the bead radius; remaining candidates receive exact native edge-to-face queries. Nine current exact native exterior roof/chamfer/R6-runout/R12-corner/sidewall faces are identified by their full boundary and outward orientation. The full flat rear port plane receives a separate retained contact reading; it is not claimed support-free. Every road comes from this fresh archive.','scope':'Nominal native geometric bead-envelope clearance. Functional support contacts remain permitted where accessible. Physical surface finish and removal effort remain separate.'}
write(JOB/'show-support-clearance.json',record)
summary={k:v for k,v in record.items() if k not in ['protected_show_faces','candidate_readings']};summary.update(detail_file='show-support-clearance.json',detailed_road_readings_sha256=sha(JOB/'show-support-clearance.json'),elapsed_seconds=time.time()-start);write(JOB/'show-support-clearance-summary.json',summary)
print(json.dumps({k:summary[k] for k in ['pass','support_roads_checked','native_bbox_candidate_pairs','analytic_surface_lower_bound_exclusions','exact_native_edge_to_face_pairs','minimum_candidate_bead_clearance_lower_bound_mm','auxiliary_functional_potential_contacts','elapsed_seconds']},indent=2),flush=True)
assert record['pass'],protected_contacts[:10]
