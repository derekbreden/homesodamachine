"""Place the complete accepted nameplate mating geometry on the west flank."""
from pathlib import Path
import sys,json,hashlib,cadquery as cq
ROOT=Path(__file__).resolve().parents[3];S=ROOT/'future/pump-first-layout-study';H=S/'routing';C=ROOT/'.cache/pump-first-layout/routing';sys.path.insert(0,str(S));import baseline
m=json.load(open(H/'candidate.json'));shells=json.load(open(S/'funnel/shells.json'));base=baseline.read(['nameplate','nameplate-ink']);rec=cq.Shape.importBrep(str(ROOT/shells['interfaces']['retained-nameplate-stock']['brep']))
b=rec.BoundingBox();oldblank=cq.Solid.makeBox(b.xlen,b.ylen,b.zlen,cq.Vector(b.xmin,b.ymin,b.zmin));oldcuts=oldblank.cut(rec)
delta=(363.8,339.175,47.0715)
def moved(q):return q.rotate((0,0,0),(0,0,1),90).translate(delta)
def bounds(q):b=q.BoundingBox();return[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def record(n,q,role,detail):
 p=C/(n+'.brep');q.exportBrep(str(p));return{'brep':str(p.relative_to(ROOT)),'role':role,'detail':detail,'bounds':bounds(q),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
plate=moved(base['nameplate']);glyph=moved(base['nameplate-ink']).translate((.48,0,0));engraved=plate.cut(glyph)
assert engraved.isValid() and len(engraved.Solids())==1
for n,q in [('nameplate',engraved),('nameplate-ink',glyph)]:
 m['parts'][n]=record(n,q,'electronics','Exact accepted flat-wing nameplate, installed on west wall; bodyY322.67..432/Z304..342, faceX-107.5; original fit dimensions unchanged.')
 if n not in m['replacement_names']:m['replacement_names'].append(n)
root=m.setdefault('interface_moves',{})
root['nameplate']={'rotation_world_z_deg':90,'translation_after_rotation':list(delta),'print_owner':'enclosure-back-top','original_receiver':shells['interfaces']['retained-nameplate-stock'],'original_receiver_removal':record('nameplate-original-removal',oldblank,'context','Exact source receiver bounding region, used to restore original rear skin.'),'original_voids':record('nameplate-original-voids',oldcuts,'context','Original fitted nameplate openings.'),'new_receiver':record('nameplate-west-receiver',moved(rec),'structure','Complete accepted 6.96 mm deep receiver, including wing slots and release opening.'),'new_cutter':record('nameplate-west-cutter',moved(oldcuts),'context','Exact transformed receiver openings; subtract after fusing receiver to west wall.'),'minimum_backing_stock_mm':3.04,'local_outer_x_mm':-107.5,'face_axis':[-1,0,0],'inner_backing_face_x_mm':-97.49,'raised_ink_beyond_nominal_face_mm':0,'marking_finish':'Exact glyph engraved into plate with flush paint/fill, preserving full accepted rear mating and wing slots','engraving_depth_mm':1.2,'remaining_face_thickness_mm':2.16,'body_bounds':bounds(moved(base['nameplate'])),'receiver_bounds':bounds(moved(rec)),'scope':'Rigid transformation preserves the accepted mating dimensions; full side-wall printing, insertion and lifetime remain separate qualifications.'}
backing=cq.Solid.makeBox(10.01,115.33,46,cq.Vector(-107.5,319.67,300))
root['nameplate']['new_backing']=record('nameplate-west-backing',backing,'structure','Full3.05mm backing behind the complete6.96mm fitted receiver, rooted into nominal west shell; exact cutter recut after fuse.')
pump_packet=json.loads((S/'pump/candidate.json').read_text())
pump_record=pump_packet['parts']['g-ganen-pump']
pump_body=cq.Shape.importBrep(str(ROOT/pump_record['brep']))
root['nameplate']['native_backing_check']={
 'pump_brep':pump_record['brep'],
 'pump_sha256':hashlib.sha256((ROOT/pump_record['brep']).read_bytes()).hexdigest(),
 'air_mm':backing.distance(pump_body),
 'common_mm3':abs(backing.intersect(pump_body,tol=.0001).Volume(tol=1e-9)),
 'scope':'Full backing exterior against the complete installed scanned pump; receiver mating dimensions and physical qualification remain separate.'}
assert root['nameplate']['native_backing_check']['common_mm3']<.001
assert root['nameplate']['native_backing_check']['air_mm']>=1.-1e-5
root['nameplate']['native_backing_status']='The full backing clears the installed scanned pump and joins the west junction platform as common enclosure stock. The exact backing-to-pump native result is recorded separately.'
(H/'candidate.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(root,indent=2),flush=True)
