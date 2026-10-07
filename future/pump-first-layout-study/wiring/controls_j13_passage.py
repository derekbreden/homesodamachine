"""Native fixed-cartridge lead through its retained ridge clip and frame chase."""
from pathlib import Path
import hashlib,json,sys
import cadquery as cq
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
sys.path[:0]=[str(HERE),str(STUDY)]
from controls_looms import definition,native_hits,loaded_digest,protected_nameplate_models
from controls_harness import passed_body_models,lower_lead_models
from native_harness import sweep,bounds
import audit

def main():
 _,network,sections,fanouts=definition()
 n=next(n for n in network if n['name']=='loom-J13-retained-cartridge-loom');p=n['to_dock']
 x,y,z=p['point'];points=[[x,y,z],[x,112.,z],[x,112.,301.],[62.,112.,301.],[62.,98.5,301.],[90.,98.5,301.],[90.,120.,301.]]
 shape,record=sweep(points,4.3,4.7)
 tool_points=[*points[:-1],[90.,126.,301.]]
 tool,_=sweep(tool_points,6.3,4.7)
 fm=json.loads((STUDY/'funnel/candidate.json').read_text());frame=cq.Shape.importBrep(str(ROOT/fm['parts']['funnel-frame']['brep']))
 silicone=cq.Shape.importBrep(str(ROOT/fm['parts']['funnel']['brep']))
 revised=frame.cut(tool,tol=.0001);removed=frame.intersect(tool,tol=.0001)
 models,_,_,_,_=audit.collect();models.update(passed_body_models()[0]);models.update(lower_lead_models()[0]);models.update(protected_nameplate_models())
 for name,s in list(models.items()):
  if name.startswith(('control-','power-','wire-')) or name in ['rear-roof-hatch','funnel-frame']:models.pop(name);continue
  if name.startswith(('enclosure-front-top','enclosure-back-top')):models[name]=s.intersect(cq.Solid.makeBox(240,241.685,130,cq.Vector(-120,84.015,240)))
 models.update({name:s for name,(s,_) in sections.items()});models.update({'control-'+name:s for name,(s,_,_) in fanouts.items()})
 hits=native_hits(shape,models,[p['owner']]);models['funnel-frame']=revised
 band=cq.Solid.makeBox(240,400,5.25,cq.Vector(-120,0,304.15));lost=abs(frame.intersect(band,tol=.0001).cut(revised,tol=.0001).Volume(tol=1e-9))
 checks=[{'test':'complete native lead and retained forward interfaces','native_interferences':hits,'pass':not hits},
  {'test':'frame running air','air_mm':revised.distance(shape),'pass':revised.distance(shape)>=.9999},
  {'test':'retained source5.25mm floor band','floor_band_z_mm':[304.15,309.4],'missing_mm3':lost,'pass':lost<.001},
  {'test':'native joined relieved frame','valid':revised.isValid(),'solids':len(revised.Solids()),'pass':revised.isValid() and len(revised.Solids())==1},
  {'test':'forming stock','removed_to_silicone_mm':removed.distance(silicone),'forming_expansion_reserve_mm':.6,'remaining_lower_bound_mm':removed.distance(silicone)-.6,'pass':removed.distance(silicone)-.6>=3},
  {'test':'cutter below protected rail/root band','cutter_max_z_mm':tool.BoundingBox().zmax,'protected_min_z_mm':306.9,'pass':tool.BoundingBox().zmax<306.9}]
 out=ROOT/'.cache/pump-first-layout/wiring/controls-looms';out.mkdir(parents=True,exist_ok=True)
 files={}
 for name,s in [('j13-ridge-passage',shape),('j13-frame-clearance',tool)]:
  path=out/(name+'.brep');s.exportBrep(str(path));files[name]={'brep':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bounds':bounds(s)}
 report={'part':files['j13-ridge-passage'],'clearance_cutter':files['j13-frame-clearance'],'port_point':p['point'],'lead_paths':[points],'diameter_mm':4.3,'bend_radius_mm':4.7,'removed_frame_stock_mm3':removed.Volume(tol=1e-9),
  'checks':checks,'pass':all(r['pass'] for r in checks),'input_geometry_sha256':{name:loaded_digest(s) for name,s in models.items() if s.Solids()},
  'source_sha256':{str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
  'scope':'The fixed cartridge lead uses its retained bulkhead bore and ridge clip. Only the changed removable frame admits this1mm-air underside chase; front-shell stock is retained. The complete source5.25mm floor band, production rails and their roots remain. This does not qualify material strength, wire dressing or donor lead reach.'}
 (HERE/'frame-j13-relief.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':main()
