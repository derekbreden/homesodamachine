"""Manual native proof of branch junction bodies, rooted wells and wire mouths.

Prepare the actual fixed-body cache with aggregate_review.py --refresh-cache,
or the bounded fixture with review.py --pack-fixture --compose-only --export-wiring,
then run this script through tmp/takeover/cadq. Current native
parts, fluid spans and junction poses come from production sources. This script
is never run by a build, hook or commit gate. No wire packing or physical load
qualification is claimed.
"""
import json,sys,hashlib
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[4];sys.path[:0]=[str(ROOT/'hardware/manifold-layout'),str(ROOT/'hardware/scripts')]
import cadquery as cq
import above_core_parts as parts,above_core_wiring as junctions
TEMP=ROOT/'tmp/above-core-electrical-fixture'
from tube_review import production_specifications
specs=production_specifications()
tubes={'tube-'+n:parts.route_shape(s) for n,s in specs.items()}
components={n:r[0] for n,r in {**parts.components(),**parts.core_components()}.items()}
import enclosure_assembly as appliance
frame=appliance._funnel_frame
frame_box=SimpleNamespace(inner=frame.DEFAULT_INNER,
                          outer=(-107.5,107.5,0.,472.,0.,355.))
components['funnel-frame']=frame.build()
components.update({n:s for n,s,_c,_carry in appliance.build_drain_joint(frame_box)})
def bb(s):
 b=s.BoundingBox();return [getattr(b,n) for n in ('xmin','ymin','zmin','xmax','ymax','zmax')]
def over(a,b):return all(a[i+3]>b[i]+1e-5 and b[i+3]>a[i]+1e-5 for i in range(3))
# Include the unchanged native front manifold, complete cartridge equipment,
# display/pogo/drain hardware and retained internal front tubes from the explicit
# bounded fixture; current selected source poses replace any same-named cache.
cache_dir=TEMP/'junction-fixed'
cache_index=cache_dir/'index.json'
if not cache_index.exists():cache_dir=TEMP;cache_index=TEMP/'index.json'
cache=json.loads(cache_index.read_text())
cachefiles=cache['parts']
retained_files={}
retained=('compressor','condenser+fan','mq6-sensor','thermal-fuse','fuse-clamp','display','display-cover','pump-contact-male','pump-contact-female','funnel-frame','elbow-cradle','funnel-drain-union','funnel-drain-stub','electronics-access-panel')
for qualified_name,file in cachefiles.items():
 name=qualified_name.rsplit('/',1)[-1]
 if (name in retained or name.startswith(('pump-a-','pump-b-','tee-y-','stem-elbow-','flavor-reducer-')) or
     name.startswith('coil-v-') and name[-1] in 'cdefghij' or
     name.startswith('valve-v-') and name not in components or name in ('tube-fluid-9','tube-fluid-10','tube-fluid-11','tube-fluid-12','tube-fluid-13','tube-fluid-17','tube-fluid-19','tube-fluid-20','tube-fluid-21','tube-fluid-22','tube-fluid-23','tube-fluid-27')):
  if name not in components:
   components[name]=cq.Shape.importBrep(str(cache_dir/file));retained_files[qualified_name]=file
# Existing PSU screw approaches are an explicit installation constraint.
components.update({'driver-'+n:s for n,s in junctions.driver_columns().items()})
receiver=Path('/tmp/hsm-rear-nameplate-receiver.brep')
if receiver.exists():components['rear-nameplate-receiver']=cq.Shape.importBrep(str(receiver))
import above_core
c14=above_core.pose('c14-inlet');cx,cy,cz=c14['translation_mm'];pitch=above_core.specification()['rear_wall']['dry_openings']['c14']['mount_pitch_mm']
for side in (-1,1):
 components['c14-outside-driver-'+str(side)]=cq.Solid.makeCylinder(3.,30.,cq.Vector(cx+side*pitch/2.,cy,cz),cq.Vector(0,1,0))
 components['c14-full-insert-stock-'+str(side)]=cq.Solid.makeCylinder(5.,10.25,cq.Vector(cx+side*pitch/2.,cy-3.25-10.25,cz),cq.Vector(0,1,0))
boxes={n:bb(s) for n,s in {**tubes,**components}.items()}
record={}
original=junctions.placements
for version in ['final-staggered']:
 hits=[];partsrows={}
 for name,(body,_color,_carry) in junctions.components().items():
  if name=='ground-stack':continue
  stock,pocket=junctions._well(name);well=stock.cut(pocket)
  partsrows[name]={'body_bounds_mm':bb(body),'well_bounds_mm':bb(well),'well_valid':well.isValid()}
  for ownlabel,own in [(name,body),(name+'-well',well)]:
   for other,shape in {**tubes,**components}.items():
    if ownlabel.endswith('-well') and other.startswith('c14-full-insert-stock'):continue
    if not over(bb(own),boxes[other]):continue
    hit=own.intersect(shape);v=hit.Volume()
    if v>.01:
     row={'part':ownlabel,'obstacle':other,'volume_mm3':v,'bounds_mm':bb(hit)};hits.append(row);print(version,json.dumps(row),flush=True)
 entryhits=[]
 for name,pose in junctions.placements().items():
  if name=='ground-stack':continue
  width,depth,height,poles,rows=junctions.SIZES[pose['size']]
  for i in range(poles):
   count=poles//rows;row=i//count;slot=i%count
   point,axis=junctions.carry(name)(((-width/2+(slot+.5)*width/count,depth/2,height*(row+.5)/rows),(0.,1.,0.)))
   length=4. if name in ('wago-mana','wago-manb') else 8.
   lead=cq.Solid.makeCylinder(1.5,length,cq.Vector(*point),cq.Vector(*axis))
   for other,shape in {**tubes,**components}.items():
    if not over(bb(lead),boxes[other]):continue
    hit=lead.intersect(shape);v=hit.Volume()
    if v>.01:entryhits.append({'part':name,'port':i+1,'obstacle':other,'volume_mm3':v,'bounds_mm':bb(hit)})
 pocket_hits=[]
 for name,pose in junctions.placements().items():
  if pose['parent']!='back-top':continue
  _,pocket=junctions._well(name)
  for other,solid in components.items():
   if not other.startswith('c14-full-insert-stock') or not over(bb(pocket),bb(solid)):continue
   v=pocket.intersect(solid).Volume()
   if v>.001:pocket_hits.append([name,other,v])
 record[version]={'front_mouth_witness_mm':{'length':4.,'diameter':3.},'rear_core_mouth_witness_mm':{'length':8.,'diameter':3.},'fixed_parts':sorted(components),'tube_names':sorted(tubes),'c14_insert_stock_removed_by_pockets':pocket_hits,'parts':partsrows,'intersections':hits,'wire_entry_intersections':entryhits}
record['scope']='Nine native WAGO bodies and rooted wells, conservative wire-mouth witnesses, current selected hardware and retained fixed front hardware against selected native fluid spans; no physical or wire-packing qualification.'
record['actual_poses']=junctions.placements()
record['actual_pose_sha256']=hashlib.sha256(json.dumps(record['actual_poses'],sort_keys=True).encode()).hexdigest()
record['native_tube_sha256']=hashlib.sha256(json.dumps(specs,sort_keys=True).encode()).hexdigest()
record['source_sha256']={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in
 (Path(__file__),Path(junctions.__file__),ROOT/'hardware/manifold-layout/above-core.json',Path(parts.__file__),ROOT/'hardware/manifold-layout/above_core_routes.py',Path(appliance.__file__),Path(frame.__file__),Path(frame.funnel.__file__))}
record['frame_drain_datums']=frame.drain_seat_datums()
record['fixed_fixture_aggregate_sha256']=cache.get('aggregate_sha256')
record['fixed_fixture_index_sha256']=hashlib.sha256(cache_index.read_bytes()).hexdigest()
record['fixed_fixture_brep_sha256']={name:hashlib.sha256((cache_dir/file).read_bytes()).hexdigest() for name,file in retained_files.items()}
record['reference_sha256']={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for key,path in junctions.REFERENCES.items() if key in ('413','415','420')}
record['geometrically_clear']=not any(row.get(key) for row in record.values() if isinstance(row,dict) for key in ('intersections','wire_entry_intersections','c14_insert_stock_removed_by_pockets'))
record['front_actual_conductor_od_mm']=1.7
(Path(__file__).with_name('junction-review.json')).write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2),flush=True)
