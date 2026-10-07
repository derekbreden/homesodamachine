"""Native underside fitting pockets, preserving the complete slide/bearing band."""
from pathlib import Path
import argparse,hashlib,json
import cadquery as cq
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bounds(s):
 b=s.BoundingBox();return[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--hold-manifest',action='store_true');parser.add_argument('--aft',type=float);parser.add_argument('--closure-travel-mm',type=float,default=102.2);args=parser.parse_args()
 selected=json.loads((HERE/'candidate.json').read_text())
 extra=args.aft if args.aft is not None else selected['aft_extension_mm']
 OUT=ROOT/'.cache/pump-first-layout/funnel'/f'aft-{extra:g}'/'underframe-reliefs'
 OUT.mkdir(parents=True,exist_ok=True)
 source=ROOT/'.cache/pump-first-layout/funnel'/f'aft-{extra:g}'/'funnel-frame.brep'
 frame=cq.Shape.importBrep(str(source));silicone_path=source.with_name('funnel.brep');silicone=cq.Shape.importBrep(str(silicone_path))
 pump_path=HERE.parent/'pump/candidate.json';pump=json.loads(pump_path.read_text());vk_path=ROOT/pump['parts']['vk-solenoid']['brep'];vk=cq.Shape.importBrep(str(vk_path));b=vk.BoundingBox()
 assert b.zmax+1<306.9,'Valve clearance reaches the production slide/bearing band'
 vk_cutter=cq.Solid.makeBox(b.xlen+2,b.ylen+2+args.closure_travel_mm,b.zlen+2,cq.Vector(b.xmin-1,b.ymin-1,b.zmin-1))
 cradle_path=ROOT/pump['parts']['vk-cradle']['brep'];cradle=cq.Shape.importBrep(str(cradle_path));cb=cradle.BoundingBox()
 cradle_cutter=cq.Solid.makeBox(cb.xlen+2,cb.ylen+2+args.closure_travel_mm,cb.zlen+2,cq.Vector(cb.xmin-1,cb.ymin-1,cb.zmin-1))
 # The upright side cradle reaches above the valve casting. Its pocket remains
 # inboard of the production rails and their complete 3 mm root section.
 cutter=vk_cutter.fuse(cradle_cutter,tol=.0001)
 routing=json.loads((HERE.parent/'routing/candidate.json').read_text())
 tee_path=ROOT/routing['parts']['water-split']['brep'];tee=cq.Shape.importBrep(str(tee_path))
 fluid_a_report_path=HERE.parent/'routing/frame-fluid-a-relief.json'
 fluid_a_inputs=[];fluid_a=None;fluid_a_cutter=None
 if fluid_a_report_path.exists():
  fluid_a_report=json.loads(fluid_a_report_path.read_text())
  occupied_name=fluid_a_report['occupied_part']
  # The complete native tool is already below the rail band. Cropping its
  # thin crown at a chosenY plane can leave a nearby tube section without the
  # specified1mm air, and is unnecessary for this frame-only subtraction.
  fluid_a_cutter_path=ROOT/routing['clearance_cutters'][occupied_name]['brep']
  fluid_a_cutter=cq.Shape.importBrep(str(fluid_a_cutter_path))
  assert fluid_a_cutter.BoundingBox().zmax<306.9,'Gate-A relief reaches the protected rail band'
  fluid_a_path=ROOT/routing['parts'][occupied_name]['brep']
  fluid_a=cq.Shape.importBrep(str(fluid_a_path))
  cutter=cutter.fuse(fluid_a_cutter,tol=.0001)
  fluid_a_inputs=[fluid_a_report_path,fluid_a_cutter_path,fluid_a_path]
 j13_inputs=[];j13=None;j13_cutter=None
 j13_report_path=HERE.parent/'wiring/frame-j13-relief.json'
 if j13_report_path.exists():
  j13_report=json.loads(j13_report_path.read_text())
  assert j13_report['pass'],'Retained cartridge passage has not passed its native interfaces'
  j13_path=ROOT/j13_report['part']['brep'];j13_cutter_path=ROOT/j13_report['clearance_cutter']['brep']
  j13=cq.Shape.importBrep(str(j13_path));j13_cutter=cq.Shape.importBrep(str(j13_cutter_path))
  assert j13_cutter.BoundingBox().zmax<306.9,'Cartridge lead relief reaches protected rail stock'
  cutter=cutter.fuse(j13_cutter,tol=.0001)
  j13_inputs=[j13_report_path,j13_path,j13_cutter_path]
 revised=frame.cut(cutter,tol=.0001);removed=frame.intersect(cutter,tol=.0001)
 railband=cq.Compound.makeCompound([cq.Solid.makeBox(14.75,400,49,cq.Vector(-110,0,306.9)),cq.Solid.makeBox(14.75,400,49,cq.Vector(95.25,0,306.9))])
 missing=abs(frame.intersect(railband,tol=.0001).cut(revised,tol=.0001).Volume(tol=1e-9))
 bearing=cq.Solid.makeBox(220,400,20,cq.Vector(-110,0,346));bearing_missing=abs(frame.intersect(bearing,tol=.0001).cut(revised,tol=.0001).Volume(tol=1e-9))
 checks=[{'test':'native relieved frame','valid':revised.isValid(),'solids':len(revised.Solids()),'pass':revised.isValid() and len(revised.Solids())==1},
 {'test':'complete production rails and their three-millimetre roots','removed_mm3':missing,'protected_abs_x_min_mm':95.25,'lowest_rail_z_mm':306.9,'highest_valve_cutter_z_mm':vk_cutter.BoundingBox().zmax,'highest_cradle_cutter_z_mm':cradle_cutter.BoundingBox().zmax,'pass':missing<.001},
 {'test':'complete three-millimetre brim bearing and upper surround','removed_mm3':bearing_missing,'lowest_protected_z_mm':346,'pass':bearing_missing<.001},
 {'test':'exact raisedVK exterior air','gap_mm':revised.distance(vk),'common_mm3':abs(revised.intersect(vk,tol=.0001).Volume(tol=1e-9)),'pass':revised.distance(vk)>=.9999},
 {'test':'exact raisedVK cradle exterior air','gap_mm':revised.distance(cradle),'common_mm3':abs(revised.intersect(cradle,tol=.0001).Volume(tol=1e-9)),'pass':revised.distance(cradle)>=.9999},
 {'test':'exact raised tee exterior air','gap_mm':revised.distance(tee),'common_mm3':abs(revised.intersect(tee,tol=.0001).Volume(tol=1e-9)),'pass':revised.distance(tee)>=.9999},
 {'test':'subset of original motion-checked frame','added_mm3':abs(revised.cut(frame,tol=.0001).Volume(tol=1e-9)),'pass':abs(revised.cut(frame,tol=.0001).Volume(tol=1e-9))<.001},
 {'test':'forming stock retained before silicone','native_removed_to_silicone_mm':removed.distance(silicone),'forming_expansion_upper_bound_mm':.6,'remaining_stock_lower_bound_mm':removed.distance(silicone)-.6,'pass':removed.distance(silicone)-.6>=3}]
 if fluid_a is not None:
  gap=revised.distance(fluid_a);common=abs(revised.intersect(fluid_a,tol=.0001).Volume(tol=1e-9))
  checks.append({'test':'Gate-A exact R14 elbow retains one-millimetre frame air',
   'gap_mm':gap,'common_mm3':common,'cutter_bounds_mm':bounds(fluid_a_cutter),'pass':gap>=.9999 and common<.001})
 if j13 is not None:
  gap=revised.distance(j13);common=abs(revised.intersect(j13,tol=.0001).Volume(tol=1e-9))
  checks.append({'test':'retained cartridge bore and ridge-clip lead has one-millimetre frame air',
   'gap_mm':gap,'common_mm3':common,'cutter_bounds_mm':bounds(j13_cutter),'pass':gap>=.9999 and common<.001})
  floor_band=cq.Solid.makeBox(240,400,5.25,cq.Vector(-120,0,304.15))
  without_j13=frame.cut(vk_cutter.fuse(cradle_cutter,tol=.0001).fuse(fluid_a_cutter,tol=.0001),tol=.0001) if fluid_a_cutter is not None else frame.cut(vk_cutter.fuse(cradle_cutter,tol=.0001),tol=.0001)
  lost=abs(without_j13.intersect(floor_band,tol=.0001).cut(revised,tol=.0001).Volume(tol=1e-9))
  checks.append({'test':'cartridge chase retains the complete source5.25mm frame-floor band',
   'floor_band_z_mm':[304.15,309.4],'additional_missing_mm3':lost,'pass':lost<.001})
 for travel in [0,.5,1,2,5,10,20,40,70,90,args.closure_travel_mm]:
  if travel>args.closure_travel_mm:continue
  moving=revised.translate((0,-travel,0))
  for name,part in [('VK casting',vk),('VK cradle',cradle)]:
   volume=abs(moving.intersect(part,tol=.0001).Volume(tol=1e-9));gap=moving.distance(part)
   checks.append({'test':'front-top/frame factory closure versus '+name,'frame_fore_of_home_mm':travel,'common_mm3':volume,'gap_mm':gap,'pass':volume<.001 and gap>=.9999})
 report={'aft_extension_mm':extra,'closure_travel_mm':args.closure_travel_mm,'checks':checks,'pass':all(c['pass'] for c in checks),'removed_stock_mm3':removed.Volume(tol=1e-9),'removed_bounds_mm':bounds(removed),
 'inputs_sha256':{str(p.relative_to(ROOT)):digest(p) for p in [source,silicone_path,pump_path,vk_path,cradle_path,tee_path,*fluid_a_inputs,*j13_inputs]},
 'source_sha256':{str(Path(__file__).relative_to(ROOT)):digest(Path(__file__))},
 'scope':'One-millimetre fitting air and complete production rail/bearing geometry. Subset preserves previous interference motion checks; no printed strength, lifetime or physical fitting qualification is inferred.'}
 assert report['pass'],checks
 p=OUT/'funnel-frame.brep';revised.exportBrep(str(p));step=p.with_suffix('.step');cq.exporters.export(revised,str(step));v,t=revised.tessellate(.12,.08);mesh=p.with_suffix('.json');mesh.write_text(json.dumps({'vertices':[[q.x,q.y,q.z] for q in v],'triangles':[list(q) for q in t]},separators=(',',':'))+'\n')
 (HERE/f'underframe-reliefs-aft-{extra:g}.json').write_text(json.dumps(report,indent=2)+'\n')
 if not args.hold_manifest:
  m=json.loads((HERE/'candidate.json').read_text());m['parts']['funnel-frame']={'brep':str(p.relative_to(ROOT)),'step':str(step.relative_to(ROOT)),'mesh':str(mesh.relative_to(ROOT)),
   'sha256':{str(q.relative_to(ROOT)):digest(q) for q in [p,step,mesh]},'valid':revised.isValid(),'solids':len(revised.Solids()),'bounds_world_mm':bounds(revised),'volume_mm3':revised.Volume(),'role':'structure',
   'detail':f'One PET-GF frame solid with full production slide rails and their3mm roots, complete3mm brim bearing and original drain/cradle socket;1mm-air underside corridors admit the raised VK casting and cradle throughout the{args.closure_travel_mm:g}mm closing slide, the fixed Gate-A R14 elbow and the retained cartridge bore/ridge-clip lead. The lead chase retains the complete5.25mm source floor band. Final tee clears the unmodified underside.'}
  m['underframe_reliefs']=report;m['source_sha256'].update(report['source_sha256']);(HERE/'candidate.json').write_text(json.dumps(m,indent=2)+'\n')
  (HERE/'underframe-reliefs.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':main()
