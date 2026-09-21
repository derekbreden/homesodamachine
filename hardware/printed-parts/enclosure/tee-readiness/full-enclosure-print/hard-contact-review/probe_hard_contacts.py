from pathlib import Path
import os,sys,json,hashlib,time,faulthandler
from types import SimpleNamespace
os.environ['HSM_NO_BUILD_LOCK']='1'
faulthandler.enable();faulthandler.dump_traceback_later(90,repeat=True)
root=Path('/Users/derekbredensteiner/Developer/homesodamachine')
sys.path[:0]=[str(root/'hardware/manifold-layout'),str(root/'hardware/scripts')]
import cadquery as cq
import enclosure_assembly as ea
import _box_spec,_overlap,_clearing,_boxes,_scorecard
enc=ea._enc
directory=root/'hardware/printed-parts/enclosure/enclosure'
out=Path('/tmp/scanner-review/current-hard-contacts');out.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={}
def load(p):
 inputs[str(p)]=sha(p)
 return cq.importers.importStep(str(p)).val() if p.suffix=='.step' else cq.Shape.importBrep(str(p))
wall=load(directory/'enclosure-back-top.step')
c14,carry=ea.build_c14()
inputs[str(ea.C14_STEP)]=sha(ea.C14_STEP)
report={'inputs':inputs,'checks':[],'source_sha256':{str(Path(m.__file__)):sha(Path(m.__file__)) for m in (ea,enc,enc._c14,ea._cci)}}
def bbox(s):
 if not s.Solids():return None
 b=s.BoundingBox();return {n:getattr(b,n) for n in ('xmin','ymin','zmin','xmax','ymax','zmax')}
def check(name,a,b):
 if _clearing.box_gap(_boxes.loose(a),_boxes.loose(b))>0:
  row={'name':name,'overlap_mm3':0,'method':'disjoint native bounding boxes'}
 else:
  mesh,v=_overlap.common(a,b)
  row={'name':name,'overlap_mm3':v,'overlap_bounds':mesh.bounding_box() if v>1e-6 else None}
  if v>1e-4:
   native=a.intersect(b);row['native_overlap_mm3']=native.Volume();row['native_bounds']=bbox(native)
   native.exportBrep(str(out/(name.replace(' ','-')+'.brep')))
 report['checks'].append(row);(out/'check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(row),flush=True)
check('C14 current back-top',c14,wall)
cx,cz=ea.C14_STATION
report['c14']={'station':ea.C14_STATION,'pocket_floor_y':ea.c14_seat_y(),
 'ear_plane_y':carry(((0,0,0),(0,1,0)))[0][1],
 'rim_face_y':carry(((0,enc._c14.RIM_PROUD,0),(0,1,0)))[0][1],
 'screw_axes_error_x_mm':abs(enc.c14_screw_pitch-enc._c14.SCREW_PITCH)/2,
 'screw_radial_room_mm':(enc._c14.SCREW_D-3)/2,
 'bore':ea.c14_cutout(),'housing_bounds':bbox(c14)}
for dy in (-10,-5,-2,-1,-.5):check('C14 insertion Y'+str(dy),c14.translate((0,dy,0)),wall)

cache=Path('/tmp/scanner-review/integration-correction/route-pack')
record=json.loads((cache/'frames.json').read_text())
inputs[str(cache/'frames.json')]=sha(cache/'frames.json')
cap=load(directory/'enclosure-pump-cap.step');cartridge=load(directory/'enclosure-pump-cartridge.step')
for n in [f'pump-{p}-{s}' for p in 'ab' for s in ('head','boss','motor')]:
 s=load(cache/record[n]['brep'])
 check(n+' cartridge',s,cartridge);check(n+' cap',s,cap)

base,_=ea.build_foam(0)
front=enc.rear_plane_y-enc.rear_seam_clear-ea.box(base).ylen
foam,foamcarry=ea.build_foam(front)
inputs[str(ea.FOAM_STEP)]=sha(ea.FOAM_STEP)
import g_ganen_installation as pump
old=load(cache/record['g-ganen-pump']['brep'])
local=pump.suction()[0];world=record['g-ganen-pump']['ports']['suction'][0]
origin=(world[0]+local[1],world[1]-local[0],world[2]-local[2])
actual,pcarry=ea.seat_body(pump.build(),(((0,0,1),pump.YAW),),station=(pump.bearing_datum(),origin))
report['g_pump']={'origin':origin,'source_expected_y':ea.box(foam).ymax-pump.rigid_shape().BoundingBox().xmax-pump.REAR_CLEARANCE,'source_expected_z':ea.cap_face(foam),
 'classification':_scorecard.pump_cap_contact(SimpleNamespace(carries={pump.SCENE_KEY:pcarry}),{'g-ganen-pump':actual,'foam-assembly':foam})}
print('G pump',json.dumps(report['g_pump']),flush=True)
for name in ('enclosure-back-top','enclosure-back-bottom','enclosure-front-top','enclosure-front-bottom'):
 s=wall if name=='enclosure-back-top' else load(directory/(name+'.step'))
 check('G-pump '+name,actual,s)
report['stable_inputs']=all(sha(Path(p))==s for p,s in inputs.items())
report['stable_sources']=all(sha(Path(p))==s for p,s in report['source_sha256'].items())
(out/'check.json').write_text(json.dumps(report,indent=2)+'\n')
print('complete',report['stable_inputs'],report['stable_sources'],flush=True)
