"""Move the entire accepted keystone mating packet to its compact bay station."""
from pathlib import Path
import json,sys,hashlib,cadquery as cq
ROOT=Path(__file__).resolve().parents[3];S=ROOT/'future/pump-first-layout-study';H=S/'routing';C=ROOT/'.cache/pump-first-layout/routing'
sys.path.insert(0,str(S));import baseline
m=json.load(open(H/'candidate.json'));s=json.load(open(S/'funnel/shells.json'))['interfaces'];delta=(-25.865,0,-.0472904687784)
def rec(n,q,detail):
 p=C/(n+'.brep');q.exportBrep(str(p));b=q.BoundingBox()
 return {'brep':str(p.relative_to(ROOT)),'role':'electronics','detail':detail,'bounds':[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax],'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
body=baseline.read(['keystone-jack'])['keystone-jack'].translate(delta)
m['parts']['keystone-jack']=rec('keystone-jack',body,'Complete accepted keystone at translated compact rear station; receiver geometry and catches move with the scanned body.')
if 'keystone-jack' not in m['replacement_names']:m['replacement_names'].append('keystone-jack')
move={'translation':list(delta),'print_owner':'enclosure-back-top','accepted_fit_preserved':True}
for k,out in [('retained-keystone-stock','new_receiver'),('original-keystone-cutter','new_cutter'),('original-keystone-feature','new_feature'),('original-keystone-catches','new_catches')]:
 q=cq.Shape.importBrep(str(ROOT/s[k]['brep']));move[out]=rec('keystone-'+out,q.translate(delta),'Exact accepted native mating geometry translated with the jack.')
move['original_receiver']=s['retained-keystone-stock'];move['original_cutter']=s['original-keystone-cutter']
m.setdefault('interface_moves',{})['keystone']=move
(H/'candidate.json').write_text(json.dumps(m,indent=2)+'\n')
print(json.dumps(move,indent=2))
