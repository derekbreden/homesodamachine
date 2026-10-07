"""Diagonal WR1110 barrel seat, full tie loop and explicit locking-head reserve.

The scanned circular band defines the seat independently of its wrench clock.
The 9.5mm rib retains two3mm end webs around a3.5mm tie passage, and roots into
the west wall plus the existing junction carrier. The tie remains the load path.
"""
from pathlib import Path
import argparse,hashlib,json,math,sys
import cadquery as cq
import numpy as np

HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
OUT=ROOT/'.cache/pump-first-layout/mounts/wr'
sys.path[:0]=[str(STUDY/'wiring'),str(STUDY)]
from controls_looms import native_hits,loaded_digest
from native_harness import bounds,broad
import audit

def box(x0,x1,y0,y1,z0,z1):return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--head-bottom',type=float,default=-18.1);args=parser.parse_args()
 routing=json.loads((STUDY/'routing/candidate.json').read_text());mounts=json.loads((HERE/'candidate.json').read_text())
 body_path=ROOT/routing['parts']['wr1110']['brep'];body=cq.Shape.importBrep(str(body_path))
 barrel=next(f for f in body.Faces() if f.geomType()=='CYLINDER' and abs(f._geomAdaptor().Cylinder().Radius()-9.435)<1e-5)
 center=np.asarray(barrel.Center().toTuple());inlet=routing['ports']['wr1110']['inlet'];flow=-np.asarray(inlet.get('normal',inlet.get('axis')),float)
 # Port metadata uses `normal` in some producer versions and `axis` in others.
 flow/=np.linalg.norm(flow);nw=np.asarray([-flow[1],flow[0],0.]);r=9.435+.15;reach=r+3.;length=9.5
 def profile(points,s0,s1):
  origin=center+flow*s0;plane=cq.Plane(origin=cq.Vector(*origin),xDir=cq.Vector(*nw),normal=cq.Vector(*flow))
  return cq.Workplane(plane).polyline(points).close().extrude(s1-s0).val()
 seat=profile([(0,-reach),(reach,-reach),(reach,reach),(0,reach)],-length/2,length/2)
 for lo,hi in [(-4.75,-1.75),(1.75,4.75)]:
  seat=seat.fuse(profile([(reach,-reach),(35,-reach),(35,reach),(reach,reach)],lo,hi),tol=.0001)
 seat=seat.fuse(profile([(reach+4.25,-reach),(35,-reach),(35,reach),(reach+4.25,reach)],-1.75,1.75),tol=.0001)
 seat=seat.intersect(box(-99.5,107.5,295,430,295,340))
 bore=cq.Solid.makeCylinder(r,length,cq.Vector(*(center-flow*length/2)),cq.Vector(*flow));seat=seat.cut(bore,tol=.0001).clean()
 # Exact tangent circle/rectangle hull. No polygonal approximation changes the
 # scanned circular bearing or the tie's explicit1mm section.
 q=math.sqrt(1-(r/reach)**2);b=-r*q;z=r*r/reach
 plane=cq.Plane(origin=cq.Vector(*(center-flow*1.25)),xDir=cq.Vector(*nw),normal=cq.Vector(*flow))
 outline=(cq.Workplane(plane).moveTo(0,reach).lineTo(reach,reach).lineTo(reach,-reach).lineTo(0,-reach)
          .lineTo(b,-z).threePointArc((-r,0),(b,z)).close().wire())
 outer=outline.offset2D(1.15).extrude(2.5).val()
 outline=(cq.Workplane(plane).moveTo(0,reach).lineTo(reach,reach).lineTo(reach,-reach).lineTo(0,-reach)
          .lineTo(b,-z).threePointArc((-r,0),(b,z)).close().wire())
 inner=outline.offset2D(.15).extrude(2.5).val();band=outer.cut(inner,tol=.0001)
 head=profile([(12.4,args.head_bottom),(20.4,args.head_bottom),(20.4,args.head_bottom+5),(12.4,args.head_bottom+5)],-4,4)
 tie=band.fuse(head,tol=.0001).clean()
 # The existing deck cannot fill the narrow tie's upper flank. Open the
 # carrier only over the3.5mm tie band, leaving both complete3mm end webs.
 roof=json.loads((HERE/'roof-candidate.json').read_text())
 slot_top=max(reach+2,335.75+roof.get('high_junction_lift_mm',0.)-center[2]+.01)
 slot=profile([(-reach-2,-reach-2),(reach+4.25,-reach-2),(reach+4.25,slot_top),(-reach-2,slot_top)],-1.75,1.75)
 platform_path=ROOT/mounts['parts']['west-junction-platform']['brep'];platform=cq.Shape.importBrep(str(platform_path));revised=platform.cut(slot,tol=.0001).clean()
 models,records,_,_,_=audit.collect();shell=models['enclosure-back-top']
 for n in list(models):
  if n.startswith(('wr-regulator-','wire-','control-')) or n in ['west-junction-platform']:models.pop(n)
  elif n.startswith(('enclosure-back-top','enclosure-front-top')):models.pop(n)
 for name,working in mounts['working_envelopes'].items():
  if 'levers' in working:models[name+'-lever-working-space']=cq.Shape.importBrep(str(ROOT/working['levers']['brep']))
 # An anchor can join the deck but cannot consume any purchased body or lead.
 checks=[]
 for name,shape in [('wr-regulator-seat',seat),('wr-regulator-retention-tie',tie),('west-junction-platform',revised)]:
  hits=native_hits(shape,models,['wr1110'] if name=='wr-regulator-seat' else[])
  row={'part':name,'valid':shape.isValid(),'solids':len(shape.Solids()),'native_interferences':hits,'pass':shape.isValid() and len(shape.Solids())==1 and not hits};checks.append(row)
  print(json.dumps(row),flush=True)
 common=abs(seat.intersect(tie,tol=.0001).Volume(tol=1e-9));checks.append({'test':'tie clears full seat','common_mm3':common,'pass':common<.001})
 common=abs(revised.intersect(tie,tol=.0001).Volume(tol=1e-9));checks.append({'test':'tie clears revised carrier','common_mm3':common,'pass':common<.001})
 joined=revised.fuse(seat,tol=.0001).clean();checks.append({'test':'single joined carrier and seat','valid':joined.isValid(),'solids':len(joined.Solids()),'pass':joined.isValid() and len(joined.Solids())==1})
 checks.append({'test':'seat reaches west wall','gap_mm':seat.distance(shell),'common_mm3':abs(seat.intersect(shell,tol=.0001).Volume(tol=1e-9)),'pass':seat.distance(shell)<1e-6})
 checks.append({'test':'scanned barrel0.15mm radial slip','gap_mm':seat.distance(body),'pass':abs(seat.distance(body)-.15)<.0001})
 OUT.mkdir(parents=True,exist_ok=True)
 def emit(name,s,detail,role='structure'):
  path=OUT/(name+'.brep');s.exportBrep(str(path));v,t=s.tessellate(.12,.08);mesh=path.with_suffix('.json');mesh.write_text(json.dumps({'vertices':[[q.x,q.y,q.z] for q in v],'triangles':[list(q) for q in t]},separators=(',',':'))+'\n')
  return {'brep':str(path.relative_to(ROOT)),'mesh':str(mesh.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bounds':bounds(s),'role':role,'detail':detail}
 # Only non-bearing carrier stock is recut after fusion. Cutting the complete
 # local prism would erase the central3mm bearing web beneath the tie.
 passage=slot.cut(seat,tol=.0001).clean()
 checks.append({'test':'tie passage preserves complete bearing rib','common_mm3':abs(passage.intersect(seat,tol=.0001).Volume(tol=1e-9)),'pass':abs(passage.intersect(seat,tol=.0001).Volume(tol=1e-9))<.001})
 finished=joined.cut(passage,tol=.0001).clean();checks.append({'test':'joined carrier remains one solid after passage recut','valid':finished.isValid(),'solids':len(finished.Solids()),'pass':finished.isValid() and len(finished.Solids())==1})
 outline=(cq.Workplane(plane).moveTo(0,reach).lineTo(reach,reach).lineTo(reach,-reach).lineTo(0,-reach)
          .lineTo(b,-z).threePointArc((-r,0),(b,z)).close().wire())
 loop_length=outline.offset2D(.65).val().Length();checks.append({'test':'6in tie closes complete occupied loop','loop_length_mm':loop_length,'documented6in_closure_capacity_mm':110,'pass':loop_length<=110})
 result={'parts':{'wr-regulator-seat':emit('wr-regulator-seat',seat,'West-wall/roof-carrier rooted9.5mm seat on the actual scanned18.87mm barrel;0.15 radial slip,3mm radial/end webs,3.5mm central tie passage.'),
  'wr-regulator-retention-tie':emit('wr-regulator-retention-tie',tie,'Complete nominal6in narrow tie2.5×1mm,0.15mm stock air, full tangent loop around the barrel and bearing rib; conservative8×8×5mm locking-head reserve below the west flank. Purchased head shape remains unmeasured.','hardware'),
  'west-junction-platform':emit('west-junction-platform',revised,'One rooted3mm carrier with the WR tie-band passage open; two full3mm bearing end webs remain beside the3.5mm channel.')},
  'shell_fuse_part_names':['wr-regulator-seat'],
  'factory_carried_part_names':['wr1110','co2-adapter-regulator-in','co2-adapter-regulator-out','wr-regulator-retention-tie'],
  'clearance_cutters':{'wr-regulator-tie-channel':{**emit('wr-regulator-tie-channel',passage,'Recut non-bearing carrier stock after host fusion so it cannot fill the real tie passage; complete seat/rib remains protected.'),'print_owner':'enclosure-back-top'}},
  'intended_contacts':[['wr-regulator-seat','west-junction-platform']], 'checks':checks,'pass':all(r['pass'] for r in checks),
  'barrel':{'center_mm':center.tolist(),'axis':flow.tolist(),'radius_mm':9.435,'native_band_length_mm':35.4,'seat_width_mm':9.5,'radial_slip_mm':.15,'tie_section_mm':[2.5,1.],'tie_head_reserve_mm':[8,8,5],'closed_loop_length_mm':loop_length},
  'input_geometry_sha256':{n:loaded_digest(s) for n,s in models.items()},'source_sha256':{str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
  'qualification_limits':['Scanned WR1110 barrel geometry locates the seat; the received WR1105 geometry and made-up adapters retain their existing fit qualification scope.',
  'Nylon tie load capacity, head make-up, vibration and lifetime remain physical properties. The locking head is an explicit conservative working reserve, not measured purchased geometry.',
  'The complete joined carrier/seat and final shell require fresh manufacturing slices after integration.']}
 (HERE/'wr-candidate.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'pass':result['pass'],'checks':checks},indent=2),flush=True)
if __name__=='__main__':main()
