"""Reproduce the bounded 9.5 mm fixed-inner-manifold correction.

Reads frozen placed references and current production construction functions. Writes
only the requested evidence report and temporary probe solids. This is not a full
appliance rebuild or a release verdict for regenerated shell parts. Intended valve,
tee and tube mating contacts are excluded explicitly; the current fluid14 proof is
linked separately. The full simultaneous route and shell checks remain necessary.
"""
from pathlib import Path
import os,sys,json,hashlib,time,faulthandler
os.environ['HSM_NO_BUILD_LOCK']='1'
faulthandler.enable();faulthandler.dump_traceback_later(90,repeat=True)
HERE=Path(__file__).resolve().parent
root=next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())
import argparse,tempfile,zipfile
from datetime import datetime,timezone
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--baseline',type=Path,default=HERE/'inner-limb-drop-baseline.zip')
parser.add_argument('--fit-baseline',type=Path,default=HERE/'fit-correction-baseline.zip')
parser.add_argument('--output',type=Path,default=HERE/'inner-limb-drop-check.json')
args=parser.parse_args()
evidence_tmp=tempfile.TemporaryDirectory(prefix='hsm-inner-drop-')
evidence_root=Path(evidence_tmp.name)
input_sha={}
for archive_path in (args.baseline,args.fit_baseline):
 input_sha[str(archive_path.relative_to(root))]=hashlib.sha256(archive_path.read_bytes()).hexdigest()
 with zipfile.ZipFile(archive_path) as archive:
  manifest=json.loads(archive.read('manifest.json'))
  for name,row in manifest['files'].items():
   path=Path(name)
   if path.is_absolute() or '..' in path.parts:raise ValueError('Unsafe archive path')
   data=archive.read(name)
   if hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError('Input digest mismatch: '+name)
   dest=evidence_root/path if archive_path==args.baseline else evidence_root/'fixtures'/path
   dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
phases={}

sys.path[:0]=[str(root/'hardware/manifold-layout'),str(root/'hardware/scripts')]
import cadquery as cq
import enclosure_assembly as ea
import _clearing as C, _boxes
ml=ea.ml
if abs(ml.INNER_LIMB_DROP-9.5)>1e-9:raise ValueError('This evidence expects the checked 9.5 mm source')
modules=(ea,ea._enc,ea._enc._interface,ml,ea._cci)
source_start={str(Path(m.__file__).relative_to(root)):hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest() for m in modules}
cache=evidence_root/'route-pack'
out=evidence_root/'scratch';out.mkdir()
records=json.loads((cache/'frames.json').read_text())
old={n:cq.Shape.importBrep(str(cache/v['brep'])) for n,v in records.items()}
extra=cache.parent/'route-neighbors'; er=json.loads((extra/'neighbors.json').read_text())['placed']
old.update({n:cq.Shape.importBrep(str(extra/v['brep'])) for n,v in er.items()})
live_drop=ml.INNER_LIMB_DROP
lift=records['valve-v-a']['ports']['inlet'][0][2]-ml.port('V-A','front')[1]-(live_drop-8.0)
delta=1.5
change=['valve-v-'+x for x in 'abcd']+['coil-v-'+x for x in 'abcd']+['tee-y-a','tee-y-b','turn-fluid-3','turn-fluid-5','step-fluid-3','step-fluid-5']
new=dict(old)
for n in change:new[n]=old[n].translate((0,0,-delta))
ml.INNER_LIMB_DROP=9.5
for n in ('V-A','V-B','V-C','V-D','Y-A','Y-B'):
    v=ml.SHIFT[n];ml.SHIFT[n]=(v[0],v[1]-(9.5-live_drop),v[2])
for cid in (9,19):
    name='tube-fluid-'+str(cid)
    new[name]=ea.pose_manifold(ml.uturn(ml.SPINE[cid],ml.CARRIER_CONNECTED)).translate((0,ea.PACK_Y,lift))
    change.append(name)
for n in ('stub-fluid-2','stub-fluid-4'):new[n]=old[n].translate((0,0,-delta))

skip={
 'valve-v-a':{'coil-v-a','step-fluid-3','stub-fluid-2','foam-assembly'},
 'valve-v-b':{'coil-v-b','step-fluid-5','stub-fluid-4','foam-assembly'},
 'coil-v-a':{'valve-v-a'},'coil-v-b':{'valve-v-b'},
 'valve-v-c':{'coil-v-c','tee-y-a','tube-fluid-9'},
 'valve-v-d':{'coil-v-d','tee-y-b','tube-fluid-19'},
 'coil-v-c':{'valve-v-c'},'coil-v-d':{'valve-v-d'},
 'tee-y-a':{'valve-v-c','turn-fluid-3','tee-y-b'},
 'tee-y-b':{'valve-v-d','turn-fluid-5','tee-y-a'},
 'turn-fluid-3':{'tee-y-a','step-fluid-3'},'turn-fluid-5':{'tee-y-b','step-fluid-5'},
 'step-fluid-3':{'turn-fluid-3','valve-v-a'},'step-fluid-5':{'turn-fluid-5','valve-v-b'},
 'tube-fluid-9':{'valve-v-c','tee-y-c'},'tube-fluid-19':{'valve-v-d','tee-y-f'},
}
report={'status':'running','drop_delta_mm':delta,'lift':lift,'affected':change,'near_pairs':[],'source_files':{},'checks':[]}
for m in (ea,ea._enc,ea._enc._interface,ml,ea._cci):
 p=Path(m.__file__);report['source_files'][str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
def save(): (out/'probe.json').write_text(json.dumps(report,indent=2)+'\n')
for i,n in enumerate(change):
 a=new[n];bb=_boxes.loose(a)
 a.exportBrep(str(out/(n+'.brep')))
 for q,b in new.items():
  if q==n or q in skip.get(n,set()) or n in skip.get(q,set()) or q.startswith('stub-'):continue
  if q in change and change.index(q)<i:continue
  if C.box_gap(bb,_boxes.loose(b))>=2:continue
  g=C.gap(a,b,2.)
  if g<2:
   prior=C.gap(old[n],old[q],2.)
   row={'a':n,'b':q,'old_mesh_gap_mm':prior,'new_mesh_gap_mm':g}
   if g<1.05:
    row['native_overlap_mm3']=a.intersect(b).Volume()
   report['near_pairs'].append(row);save();print(row,flush=True)
 print('finished',n,flush=True)
for c in 'ab':
 s=new['coil-v-'+c];f=new['funnel']
 report['checks'].append({'name':'coil '+c+' funnel exact air','value':s.distance(f)})
# Current carrier and cartridge native geometry remain read-only input witnesses.
partdir=evidence_root/'fixtures'
carrier_dir=evidence_root/'fixtures'
fixtures={}
for side in ('left','right'):
 fixtures['carrier-'+side]=cq.importers.importStep(str(carrier_dir/('enclosure-tee-carrier-'+side+'.step'))).val()
for name in ('enclosure-front-bottom','enclosure-pump-cartridge','enclosure-pump-cap'):
 fixtures[name]=cq.importers.importStep(str(partdir/(name+'.step'))).val()
for n in change:
 for q,b in fixtures.items():
  if C.box_gap(_boxes.loose(new[n]),_boxes.loose(b))>=1:continue
  g=C.gap(new[n],b,1.)
  if g<1:
   row={'a':n,'fixture':q,'gap':g,'overlap':new[n].intersect(b).Volume()}
   report.setdefault('fixture_near',[]).append(row);save();print('fixture',row,flush=True)
report['ports']={n:{e:ea.manifold_carry(lift)((ml.port(n,end),ml.port_axis(n,end)))[0] for e,end in [('front','front'),('back','back')]} for n in ('V-A','V-B','V-C','V-D')}
report['new_trays']=ea.valve_tray_stations({n:s for n,s in new.items() if n.startswith(('valve-','coil-'))})
report['carrier_datums']={'inner_coil_top':max(new['coil-v-'+c].BoundingBox().zmax for c in 'cd'),'current_flange_z0':ea._carrier.DEFAULT_SPEC.flange_z0,'current_backing_z0':ea._carrier.DEFAULT_SPEC.side_web_z0}
report['status']='bounded_probe_complete';save()
print(json.dumps({k:v for k,v in report.items() if k not in ('source_files','near_pairs')},indent=2),flush=True)

phases['bodies_and_static_neighbors']=report
from dataclasses import asdict,replace
from collections import namedtuple
import zipfile,tempfile
import _box_spec
sys.path.insert(0,str(root/'hardware/printed-parts/cold-core/foam-cap'))
import foam_cap as fc
from _carrier_motion import swept_overlap
vs=fc.seat; enc=ea._enc; tc=ea._carrier
report={'status':'running','checks':[],'reading':{}}
def add(name,value,minimum=None,maximum=None):
 passed=(minimum is None or value>=minimum-1e-6) and (maximum is None or value<=maximum+1e-5)
 row={'name':name,'value':value,'minimum':minimum,'maximum':maximum,'pass':passed}
 report['checks'].append(row);save();print(json.dumps(row),flush=True)
def save():(out/'dependent-probe.json').write_text(json.dumps(report,indent=2)+'\n')
face=ea.cap_face(new['foam-assembly'])
for name in ('valve-v-a','valve-v-b'):
 oldstation=fc.cap_cradles[name]._replace(seat=12.725+ea._cci.manifold_rise-8.0)
 station=oldstation._replace(seat=oldstation.seat-delta)
 fc.cap_cradles[name]=station
 plinth=fc.cradle_shape(name,0).val()
 native=vs.valve.build_beduan_solenoid().rotate((0,0,0),(0,0,1),station.yaw+90).translate((*station.centre,station.seat)).val()
 add(name+' new native cradle interference',plinth.intersect(native).Volume(),maximum=1e-6)
 add(name+' retained socket floor stock mm',station.seat+vs.socket_floor_z,minimum=3)
 add(name+' mounting plane vs source cradle seat mm',abs(new[name].BoundingBox().zmin-face-station.seat),maximum=1e-6)
 cw=plinth.rotate((0,0,0),(0,0,1),-90).translate((0,229.710+station.centre[0],face))
 add(name+' world valve/plinth exact interference',cw.intersect(new[name]).Volume(),maximum=1e-6)
 oldseat=vs.build_seat(oldstation.seat).val();newseat=vs.build_seat(station.seat).val()
 critical=cq.Solid.makeBox(100,100,30,cq.Vector(-50,-50,vs.socket_floor_z))
 def inside_volume(s,region):return s.intersect(region).Volume() if s.Solids() else 0.0
 add(name+' socket/bearing region native extra',inside_volume(newseat.cut(oldseat),critical),maximum=1e-6)
 add(name+' socket/bearing region native missing',inside_volume(oldseat.cut(newseat),critical),maximum=1e-6)
 openings=[('pour',fc.foam_cap_lid_pour_xy(),fc.foam_cap_lid_pour_radius)]
 openings += [('vent',xy,fc.foam_cap_lid_vent_radius) for xy in fc.foam_cap_lid_vent_xy()]
 openings += [('deck '+key,xy,fc.deck_lid_hole_radius(key)) for key in fc.deck_mounts for xy in fc.deck_mount_xy(key)]
 openings += [('conduit '+key,xy,fc.cap_conduit_entry_relief_radius) for key,xy in fc.cap_conduits.items()]
 openings += [('clamp screw',xy,fc.head_cbore_radius) for xy in fc.attachment_xy_positions]
 for label,xy,r in openings:
  passage=cq.Solid.makeCylinder(r,station.seat+vs.seat_top_z+1,cq.Vector(*xy,0))
  add(name+' preserves '+label+' opening',plinth.intersect(passage).Volume(),maximum=1e-6)
 room=ea._cci.cap_cradle_room(name)
 report['reading'][name+' cap station']={'station':station,'minimum_plan_air':room,'world_floor':face}
 add(name+' cap room',room[0],minimum=1)

tmp=tempfile.TemporaryDirectory();base=Path(tmp.name)
with zipfile.ZipFile(args.fit_baseline) as archive:
 (base/'enclosure-box.json').write_bytes(archive.read('enclosure-box.json'))
fields=json.loads((base/'enclosure-box.json').read_text())['box']['pack']['fields']
oldpack=namedtuple('Pack',fields)
b,_=_box_spec.read(enc.Box,enc.Bound,(oldpack,enc.PortField,enc.Nameplate),path=base/'enclosure-box.json')
b=b._replace(pack=enc.Pack(**b.pack._asdict()))
halves=[cq.importers.importStep(str(evidence_root/'fixtures'/('enclosure-tee-carrier-'+s+'.step'))).val() for s in ('left','right')]
carrier=cq.Compound.makeCompound(halves)
for c in 'cd':
 coil=new['coil-v-'+c];valve=new['valve-v-'+c]
 dz=b.pack.collet_plate['z0']-max(coil.BoundingBox().zmax,valve.BoundingBox().zmax)-tc.DEFAULT_SPEC.slide_air
 for name,s in [('coil',coil),('valve',valve)]:
  starts=[(0,b.pack.tee_carrier['aft_valve_entry_y'],dz),(0,b.pack.tee_carrier['aft_valve_entry_y'],0),(0,0,0)]
  for a,z in zip(starts,starts[1:]):
   r=swept_overlap(s,a,z,carrier)
   report['reading'][name+' '+c+' entry '+str(a)]=r
   add(name+' '+c+' exact entry overlap',max(r['initial_overlap_mm3'],r['max_prism_overlap_mm3']),maximum=1e-5)

squeeze=[(n,s.translate((0,-ml.CARRIER_CONNECTED,0)) if n in {ml.body_name(q) for q in ml.CARRIER_TEES} else s,None) for n,s in new.items() if n in records]
pumptrays=ea.pump_tray_stations(new)
plate=ea.collet_plate_spec(ea.manifold_carry(lift),pumptrays)
spec=ea.tee_carrier_spec(ea.manifold_carry(lift),squeeze,plate)
report['reading']['derived_carrier_mismatches']=tc.placement_mismatches(spec)
preserved=replace(spec,flange_z0=max(spec.flange_z0,tc.DEFAULT_SPEC.flange_z0),side_web_z0=max(spec.side_web_z0,tc.DEFAULT_SPEC.side_web_z0))
report['reading']['candidate_preserved_carrier_mismatches']=tc.placement_mismatches(preserved)
add('current printed carrier all placement dimensions preserved using design floors',len(tc.placement_mismatches(preserved)),maximum=0)
report['reading']['pump_trays']=pumptrays
report['reading']['plate']=plate
report['reading']['new_trays']=ea.valve_tray_stations(new)
report['reading']['inner_spines']={}
for state,offset in ml.CARRIER_STATES.items():
 for cid in (9,19):
  x=ml.SPINE[cid];t=ea.pose_manifold(ml.uturn(x,offset)).translate((0,ea.PACK_Y,lift))
  bb=t.BoundingBox()
  vals={'R':ml.spine_radius(offset,x),'cut_length':ml.spine_tube_length(x),'bounds':{k:getattr(bb,k) for k in ('xmin','ymin','zmin','xmax','ymax','zmax')}}
  report['reading']['inner_spines'][str(cid)+' '+state]=vals
  add(str(cid)+' '+state+' bend radius',vals['R'],minimum=ml.MIN_BEND)
report['reading']['new_carrier_interface']=ea.tee_carrier_interface(spec,plate,squeeze)
inner=list(b.inner);outer=list(b.outer)
inner[3]=enc.rear_plane_y;outer[3]=enc.rear_plane_y+enc.wall
candidate=b._replace(inner=tuple(inner),outer=tuple(outer),pack=b.pack._replace(
 valve_trays=ea.valve_tray_stations(new),pump_trays=pumptrays,
 collet_plate=plate,tee_carrier=report['reading']['new_carrier_interface']))
cache={}
partdir=evidence_root/'fixtures'
for name,fn in [('pump-cartridge',enc.build_pump_cartridge),('pump-cap',enc.build_pump_cap)]:
 current=fn(candidate,cache).val()
 frozen=cq.importers.importStep(str(partdir/('enclosure-'+name+'.step'))).val()
 add(name+' candidate native extra',current.cut(frozen).Volume(),maximum=1e-5)
 add(name+' frozen native extra',frozen.cut(current).Volume(),maximum=1e-5)
report['source_sha256']={str(Path(m.__file__).relative_to(root)):hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest() for m in (ea,enc,enc._interface,ml,ea._cci)}
report['status']='bounded_dependent_pass' if all(q['pass'] for q in report['checks']) else 'failed'
save();print(report['status'],flush=True)

phases['cradles_carrier_pump']=report
from types import SimpleNamespace
import _lines as L, _routing as R
inner=(*ea._enc.interior_x(),ea._enc.front_plane_y,ea._enc.rear_plane_y,0.,ea._enc.appliance_height-ea._enc.floor_t-ea._enc.ceiling_skin)
outer=(-ea._enc.appliance_width/2,ea._enc.appliance_width/2,ea._enc.front_plane_y-ea._enc.front_wall,ea._enc.rear_plane_y+ea._enc.wall,-ea._enc.floor_t,ea._enc.appliance_height-ea._enc.floor_t)
funnel,carry=ea.build_funnel(SimpleNamespace(inner=inner,outer=outer))
new['funnel']=funnel
carries={'funnel':carry}
for name,shape,color,c in ea.build_drain_joint(carry):
 new[name]=shape
 if c:carries[name]=c
F={}
for n,v in records.items():
 if 'ports' not in v:continue
 ports={}
 for p,(pos,axis,dia) in v['ports'].items():
  pos=list(pos)
  if n in ('valve-v-a','valve-v-b','valve-v-c','valve-v-d'):pos[2]-=delta
  ports[p]=(pos,axis,dia)
 F[n]=R.frame(n,new[n],ports)
F.update(L.frames(new,carries))
r=L._fluid_4(F,new);t=R.tube(r)
t.exportBrep(str(out/'fluid-4.brep'))
report={'source_sha256':{str(Path(m.__file__).relative_to(root)):hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest() for m in (ea,ml,L,ea._enc._interface)},
 'scope':'Production funnel/drain placement and fluid4 constructor; fixed moved manifold bodies and retained corrected-rear neighbors. Root final simultaneous routing/body precheck remains required.',
 'run':{'pts':r.pts,'radii':r.radii,'tightest':r.tightest,'blocked':R.BLOCKED.get(r.id),'frm':r.frm,'to':r.to},'neighbors':[]}
for n,s in new.items():
 if n in ('funnel-drain-union','valve-v-b') or n.startswith('stub-'):continue
 if C.box_gap(_boxes.loose(t),_boxes.loose(s))>=2:continue
 g=C.gap(t,s,2.)
 if g<2:
  row={'neighbor':n,'mesh_gap_mm':g,'native_overlap_mm3':t.intersect(s).Volume()}
  if len(s.Solids())<3:row['native_gap_mm']=t.distance(s)
  report['neighbors'].append(row);print(row,flush=True)
p=evidence_root/'fixtures/candidate-lower-cradle-lid.brep'
lid=cq.Shape.importBrep(str(p))
report['candidate_lid']={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'gap_mm':C.gap(t,lid,2),'overlap_mm3':t.intersect(lid).Volume()}
report['pass']=r.tightest>=14-1e-6 and not R.BLOCKED.get(r.id) and all(q['mesh_gap_mm']>=1-1e-6 for q in report['neighbors']) and report['candidate_lid']['gap_mm']>=1-1e-6
(out/'fluid4.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)

phases['fluid4']=report
fluid14=HERE.parents[3]/'reference/g-ganen-pump/installation/inner-valve-route-check.json'
# Resolve from the repository root so the reference path is independent of this folder.
fluid14=root/'hardware/reference/g-ganen-pump/installation/inner-valve-route-check.json'
source_end={str(Path(m.__file__).relative_to(root)):hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest() for m in modules}
body=phases['bodies_and_static_neighbors']
passed=(all(r['new_mesh_gap_mm']>=1-1e-6 for r in body['near_pairs'])
        and not body.get('fixture_near')
        and all(r['value']>=1-1e-6 for r in body['checks'])
        and phases['cradles_carrier_pump']['status']=='bounded_dependent_pass'
        and phases['fluid4']['pass'] and source_start==source_end)
result={'status':'bounded_inner_limb_correction_pass' if passed else 'failed',
 'created_at_utc':datetime.now(timezone.utc).isoformat(),
 'scope':'Current source at inner_limb_drop9.5 against frozen rear-corrected native placements at8.0. Native cradle/entry/pump equality and production fluid4 checks; no full regenerated shell or whole-appliance acceptance claim.',
 'input_sha256':input_sha,'source_sha256':source_end,'sources_stable':source_start==source_end,
 'reproducer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'paired_fluid14_proof':{'path':str(fluid14.relative_to(root)),'sha256':hashlib.sha256(fluid14.read_bytes()).hexdigest()},
 'phases':phases}
args.output.write_text(json.dumps(result,indent=2)+'\n')
print(result['status'],str(args.output),flush=True)
if not passed:raise SystemExit('Bounded inner-limb proof failed')
