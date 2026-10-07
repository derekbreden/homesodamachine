"""Verify removable parts, cleaning lift and retained front-shell insertion."""
from pathlib import Path
import hashlib,json,sys
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware/scripts/_cadq_export.py').exists())
HERE=Path(__file__).parent
sys.path[:0]=[str(HERE.parent),str(ROOT/'hardware/scripts'),str(ROOT/'hardware/printed-parts/zone-c/funnel-cover'),
             str(ROOT/'hardware/printed-parts/zone-c/funnel')]
import cadquery as cq
import baseline
from study_configuration import configuration,save_record
from frame_stock import selected_frame
extra,preview,manifest=configuration()
parts={n:cq.Shape.importBrep(str(ROOT/v['brep'])) for n,v in manifest['parts'].items()}
parts['funnel-frame'],frame_record=selected_frame(manifest)
frame,silicone,lid=(parts[n] for n in ('funnel-frame','funnel','funnel-cover'))
reads=[]
def common(a,b): return abs(a.intersect(b,tol=.0001).Volume(tol=1e-9))
for z in (0,.25,.5,1,2,4,6,8,16,32,50,75):
 overlap=common(frame,silicone.translate((0,0,z)))
 reads.append(dict(test='silicone vertical cleaning lift against frame',lift_mm=z,overlap_mm3=overlap,pass_result=overlap<.0001))
 print('silicone lift',z,overlap,flush=True)
# Four pads intentionally compress the silicone. Their contact is an intended
# elastic fit; all other lid surfaces must clear it through the same straight lift.
import funnel as f
f.collar_d+=extra;f.neck_dy=-extra/2
# Rebind the cover's cached import-time mouth sizes to this candidate's dimensions.
import funnel_cover as cover
cover.MOUTH_W=f.collar_w-12;cover.MOUTH_D=f.collar_d-12
mask=cover.pads().translate((0,manifest['collar_centre_world_mm'][1],355))
for z in (0,.5,2,4,6,8,12):
 moving=lid.translate((0,0,z));moving_mask=mask.translate((0,0,z))
 contact=moving.intersect(silicone,tol=.0001)
 total=abs(contact.Volume(tol=1e-9))
 outside=abs(contact.cut(moving_mask,tol=.0001).Volume(tol=1e-9)) if total>.00000001 else 0.0
 reads.append(dict(test='lid vertical lift permits only four silicone friction pads',lift_mm=z,
  intentional_pad_contact_mm3=total,outside_pad_contact_mm3=outside,pass_result=outside<.0001))
 print('lid lift',z,outside,flush=True)
front=baseline.read(names=['enclosure-front-top'])['enclosure-front-top']
for y in (0,1,2,5,10,20,40,70):
 overlap=common(front,frame.translate((0,y,0)))
 reads.append(dict(test='frame insertion/removal through retained front-top rails; bay hardware excluded',
   travel_aft_mm=y,overlap_mm3=overlap,pass_result=overlap<.01))
 print('frame/front insertion',y,overlap,flush=True)
result=dict(aft_extension_mm=extra,checks=reads,pass_result=all(r['pass_result'] for r in reads),
 source_sha256={v['brep']:hashlib.sha256((ROOT/v['brep']).read_bytes()).hexdigest() for v in [*manifest['parts'].values(),frame_record]},
 retained_front_shell=baseline.prepare()['parts']['enclosure-front-top'],
 scope='Native Boolean sampled poses. Customer cleaning is vertical silicone removal after lid removal; the 5.015 mm retained drain-tube engagement is unchanged. Frame sliding is factory assembly with the front-top off and captured by closing both upper shells. Other installed bay hardware and revised back-top insertion/closing are checked by the full study integration.')
save_record('motion-check',extra,preview,result)
assert result['pass_result'],[r for r in reads if not r['pass_result']]
