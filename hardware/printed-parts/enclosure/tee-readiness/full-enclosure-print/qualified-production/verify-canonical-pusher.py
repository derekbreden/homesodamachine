#!/usr/bin/env python3
"""Bounded native export equality and actual 2 mm pusher routes; no generation.

The full assembly gate owns carrier/tee/valve/guide motions. This probe closes its
0.6 mm tool-witness limitation using the canonical 2 mm printed tool against the
complete exported wall, seated tees, moving cups and the already seated left half.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, dataclasses, hashlib, importlib.util, json, os, shutil, sys, time

ROOT=Path('/Users/derekbredensteiner/Developer/homesodamachine')
WORK=Path('/tmp/scanner-review/integration-correction')
CARRIER=ROOT/'hardware/printed-parts/enclosure/tee-carrier'
PUSHER=ROOT/'hardware/printed-parts/fixtures/carrier-spring-pusher'
ENC=ROOT/'hardware/printed-parts/enclosure/enclosure'
TOL=1e-5

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def label(p):
 p=Path(p).resolve();return str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output-dir',type=Path,required=True)
a=p.parse_args();out=a.output_dir.resolve()
if out.exists():raise SystemExit('Use a new output directory; proofs and native inputs are immutable')
out.mkdir(parents=True)
spec=importlib.util.spec_from_file_location('existing_wall_reader',ROOT/'hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/verify_current_front_top.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
snapshot=v.source_snapshot()
script_start_sha=sha(__file__)
os.environ['HSM_NO_BUILD_LOCK']='1'
sys.path[:0]=[str(ROOT/'hardware/manifold-layout'),str(CARRIER),str(PUSHER)]
import cadquery as cq
import enclosure_assembly as ea
import _box_spec
import _carrier_motion as motion
import carrier_spring_pusher as pusher
from _simple_carrier import box as block
enc,carrier,ml=ea._enc,ea._carrier,ea.ml
paths=[ROOT/'hardware/manifold-layout/enclosure-box.json',ENC/'enclosure-front-top.step',
       *[CARRIER/f'enclosure-tee-carrier-{side}{ext}' for side in ('left','right') for ext in ('.step','.stl')],
       PUSHER/'carrier-spring-pusher.step',PUSHER/'carrier-spring-pusher.stl',PUSHER/'geometry-check.json']
inputs={label(path):sha(path) for path in paths}
for path in paths:
 if path.suffix=='.step' or path.name=='enclosure-box.json':shutil.copyfile(path,out/path.name)
started=time.monotonic()
report={'status':'running','created_at_utc':datetime.now(timezone.utc).isoformat(),
 'scope':__doc__,'input_sha256':inputs,'source_sha256':v.source_hashes(),
 'checks':[],'sweeps':[],'failures':[],'source_drift':[],
 'claims':{'canonical_carriers_equal_motion_gate':False,'canonical_2mm_pusher_motion_clear':False},
 'print_released':False,'physical_trial_is_preprint_gate':False,
 'limitations':['Does not repeat full carrier/guide/valve/whole appliance gates.',
 'Full tee-carrier-motion gate must pass on the same current Box and sources.',
 'Native collision and source equality only; force, physical handling and support removal remain trial/slice readings.']}
def save():write(out/'focused-native-check.json',report)
def check(name,value,maxval=TOL):
 value=float(value);passed=value<=maxval
 report['checks'].append({'check':name,'value':value,'maximum':maxval,'pass':passed})
 if not passed:report['failures'].append(name)
def equal(name,x,y):
 check(name+' extra native stock',x.cut(y).Volume());check(name+' missing native stock',y.cut(x).Volume())
def native(path):
 s=cq.importers.importStep(str(path)).val()
 if not s.isValid() or len(s.Solids())!=1:raise ValueError(str(path)+' is not one valid native solid')
 return s
def sweep(name,s,start,end,obstacle):
 t=time.monotonic();r={'check':name,**motion.swept_overlap(s,start,end,obstacle)}
 r['elapsed_seconds']=time.monotonic()-t;report['sweeps'].append(r)
 check(name,max(r['initial_overlap_mm3'],r['max_prism_overlap_mm3']))
 print(name,report['checks'][-1]['value'],'mm3',flush=True);save()
def ycyl(x,z,d,y0,y1):return cq.Solid.makeCylinder(d/2,y1-y0,cq.Vector(x,y0,z),cq.Vector(0,1,0))
try:
 box,_bounds=_box_spec.read(enc.Box,enc.Bound,(enc.Pack,enc.PortField,enc.Nameplate),path=paths[0])
 interface=box.pack.tee_carrier;cs=carrier.DEFAULT_SPEC
 mismatch=v.datum_differences(carrier.interface(cs),interface)
 check('Canonical default interface matches complete current serialized Box interface',len(mismatch),0)
 report['interface_mismatches']=mismatch;report['box_interface']=interface
 report['canonical_spec']=dataclasses.asdict(cs)
 wall=native(out/'enclosure-front-top.step')
 halves={side:native(out/f'enclosure-tee-carrier-{name}.step') for side,name in ((-1,'left'),(1,'right'))}
 tool=native(out/'carrier-spring-pusher.step')
 parts=carrier.assembly_parts(cs)
 for side,name in ((-1,'left'),(1,'right')):equal('canonical '+name+' / current source',halves[side],parts[name])
 equal('canonical pusher / current source',tool,pusher.build())
 check('Canonical pusher has 2 mm native thickness',abs(tool.BoundingBox().zlen-2.0),1e-7)
 check('Carrier and canonical pusher preload length agree',abs(cs.spring_load_length-pusher.HELD_SPRING_LENGTH),1e-8)
 # Actual Box interface encodes every declared geometry/placement field; the
 # producer's tee_carrier_interface guard rejects a different live gate spec.
 report['carrier_gate_equality_basis']='Canonical half native/source equality plus exact complete source-interface comparison with serialized Box. The final gate must use that same Box and pass its placement guard.'
 report['claims']['canonical_carriers_equal_motion_gate']=not report['failures']
 lift=cs.tee_axis_z-ml.branch_port(sorted(ml.CARRIER_TEES)[0])[0][1]
 tees=[(ml.body_name(name),ea.pose_manifold(ml.carrier_tee(name,cs.release_offset_y)).translate((0,ea.PACK_Y,lift))) for name in sorted(ml.CARRIER_TEES)]
 obstacles=wall.fuse(*(s for _,s in tees)).clean()
 aft=cs.aft_limit_offset_y;spring_d=interface['spring_clearance_d']+2*cs.slide_air
 def installed(side):
  s=next(s for s in interface['spring_stations'] if s['x']*side>0)
  tip=s['bore_floor_y']-pusher.HELD_SPRING_LENGTH
  posed=tool.rotate((0,0,0),(0,0,1),180) if side<0 else tool
  return posed.rotate((0,0,0),(1,0,0),-90).translate((s['x'],tip-pusher.THICKNESS,s['z']))
 for side in (-1,1):
  station=next(s for s in interface['spring_stations'] if s['x']*side>0)
  posed=installed(side);equal(f'{side:+} canonical installed tool/source',posed,pusher.installed(interface,side))
  tip=station['bore_floor_y']-cs.spring_load_length
  held=ycyl(station['x'],station['z'],spring_d,tip,station['bore_floor_y'])
  check(f'{side:+} held spring / canonical moving cup',held.intersect(halves[side]).Volume())
  check(f'{side:+} 2 mm pusher / canonical moving cup',posed.intersect(halves[side]).Volume())
  held=held.fuse(posed)
  poses=[pose for _name,pose in carrier.insertion_poses(cs,side)]
  blockers=obstacles if side<0 else obstacles.fuse(halves[-1].translate((0,aft,0)))
  for i,(start,end) in enumerate(zip(poses,poses[1:]),1):
   sweep(f'half {side:+} canonical 2 mm tool/held spring insertion {i}',held,start,end,blockers)
  withdraw=cs.spring_x-max(cs.tee_xs)
  path=[(0,aft,0),(-side*withdraw,aft,0),(-side*withdraw,aft,cs.entry_lift_z)]
  blockers=blockers.fuse(halves[side].translate((0,aft,0)))
  for i,(start,end) in enumerate(zip(path,path[1:]),1):
   sweep(f'half {side:+} canonical 2 mm pusher removal {i}',posed,start,end,blockers)
  b=posed.translate(path[1]).BoundingBox()
  region=block((b.xmin,b.xmax),(b.ymin,b.ymax),(b.zmin,b.zmax+cs.entry_lift_z))
  check(f'half {side:+} complete pusher lift envelope',region.intersect(blockers).Volume())
 left=interface['spring_stations'][0]
 released=ycyl(left['x'],left['z'],spring_d,left['seat_floor_y'],left['bore_floor_y']+aft)
 right_with_tool=halves[1].fuse(installed(1))
 poses=[pose for _name,pose in carrier.insertion_poses(cs,1)]
 for i,(start,end) in enumerate(zip(poses,poses[1:]),1):
  sweep(f'right half/tool reuse past released left spring {i}',right_with_tool,start,end,released)
 report['canonical_pusher']={'thickness_mm':pusher.THICKNESS,'quantity':1,'held_length_mm':pusher.HELD_SPRING_LENGTH}
 source_after=v.source_hashes()
 report['source_drift']=[name for name,digest in source_after.items() if snapshot.get(name)!=digest]
 report['source_sha256']={**source_after,label(__file__):sha(__file__)}
 if sha(__file__)!=script_start_sha:report['source_drift'].append(label(__file__))
 if report['source_drift']:report['failures'].append('Loaded source changed during focused check')
 for name,digest in inputs.items():
  if sha(ROOT/name)!=digest:report['failures'].append('Input changed during check: '+name)
 report['claims']['canonical_2mm_pusher_motion_clear']=not report['failures']
 report['status']='pass' if not report['failures'] else 'fail'
except Exception as e:
 import traceback
 report['failures'].append(repr(e));report['traceback']=traceback.format_exc();report['status']='fail'
finally:
 report['elapsed_seconds']=time.monotonic()-started;save()
 print(json.dumps({'status':report['status'],'checks':len(report['checks']),'sweeps':len(report['sweeps']),'failures':report['failures'],'report':str(out/'focused-native-check.json')},indent=2),flush=True)
raise SystemExit(0 if report['status']=='pass' else 1)
