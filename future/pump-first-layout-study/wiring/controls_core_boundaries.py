"""Locate unmeasured core-service upper approaches in native free bay space.

The lower donor lead paths and actual core exits remain unlocated. This producer
reserves only their upper-bay approaches; it creates no lid hole or lower route.
"""
from pathlib import Path
import hashlib,json,sys
import numpy as np
import cadquery as cq
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
sys.path[:0]=[str(HERE),str(STUDY)]
from controls_looms import definition,native_hits,loaded_digest,protected_nameplate_models
from controls_harness import passed_body_models,lower_lead_models,strict_fluid_air_models
from native_harness import sweep,bounds
import audit

def main():
 data,network,sections,fanouts=definition();models,records,_,_,_=audit.collect()
 models.update(passed_body_models()[0]);models.update(lower_lead_models()[0]);models.update(protected_nameplate_models())
 physical_fluid18=models['tube-fluid-18']
 models.update(strict_fluid_air_models(models,records)[0])
 for name,shape in list(models.items()):
  if name.startswith(('control-','power-','wire-')) or name=='rear-roof-hatch':models.pop(name);continue
  if name.startswith(('enclosure-back-top','enclosure-front-top')):
   models[name]=shape.intersect(cq.Solid.makeBox(240,241.685,130,cq.Vector(-120,84.015,240)))
 roof=json.loads((STUDY/'mounts/candidate.json').read_text())
 for name,fields in roof['working_envelopes'].items():
  if 'levers' in fields:models[name+'-lever-working-space']=cq.Shape.importBrep(str(ROOT/fields['levers']['brep']))
 models.update({n:s for n,(s,_) in sections.items()});models.update({'control-'+n:s for n,(s,_,_) in fanouts.items()})
 specs=[('loom-J7-retained-cold-core-service-leads',-94.7,408.55,['carb-CHI','carb-CLO']),
        ('loom-J4-retained-cold-core-service-leads',-88.,396.,['probe-3V3','probe-IO26']),
        ('loom-wago-reeds-b-retained-cold-core-service-leads',-80.7,408.55,['carb-CHI-GND','carb-CLO-GND']),
        ('loom-J11-retained-mq6-loom',-92.5,374.,['J11-GND-fixed','J11-V5-fixed','J11-DOUT-fixed','J11-AOUT-fixed'])]
 checks=[];prepared={};port_positions={};shapes={}
 for route,x,y,keys in specs:
  n=next(n for n in network if n['name']==route);p=n['to_dock'];point=[x,y,261.8];R=n['bend_radius_mm'];D=n['diameter_mm']
  top=325. if route=='loom-J11-retained-mq6-loom' else 329.
  points=[point,[x,y,top],[x,382.,top]]
  if route=='loom-J11-retained-mq6-loom':points=[point,[x,y,267.2]]
  s,record=sweep(points,D,R);shape_start=cq.Solid.makeCylinder(D/2,8.4,cq.Vector(x,y,253.4),cq.Vector(0,0,1))
  complete=cq.Compound.makeCompound([shape_start,s]);hits=native_hits(complete,models,[p['owner']]);b=bounds(complete)
  row={'route':route,'point':point,'points_mm':points,'bounds':b,'native_interferences':hits,'pass':not hits and b[0]>=-103.5 and b[5]<=351}
  if route=='loom-J11-retained-mq6-loom':
   target=fanouts[route+'-target'][0]
   row['target_fluid18_air_mm']=target.distance(physical_fluid18)
   row['pass']=row['pass'] and row['target_fluid18_air_mm']>=1.-1e-6
  checks.append(row);shapes[route]=complete
  if row['pass']:
   prepared[p['label']]={'port_point':point,'diameter_mm':D,'bend_radius_mm':R,'lead_paths':[points]}
   if len(keys)==4:
    for i,key in enumerate(keys):port_positions[key]=[x+(-.9 if i%2==0 else .9),y+(-.9 if i<2 else .9),253.4]
   else:
    for key,offset in zip(keys,[-.9,.9]):port_positions[key]=[x+offset,y,253.4]
 pairs=[]
 for i,(name,s) in enumerate(shapes.items()):
  for other,t in list(shapes.items())[i+1:]:
   common=abs(s.intersect(t,tol=.0001).Volume(tol=1e-9));pairs.append({'routes':[name,other],'common_mm3':common,'pass':common<.001})
 out={'port_positions':port_positions,'prepared_leads':prepared,'checks':checks,'pair_checks':pairs,'pass':len(prepared)==4 and all(r['pass'] for r in pairs),
 'scope':'Unlocated carbonator/probe leads reserve these upper-bay approaches only. Actual donor lengths, lower continuations, core exits and any passage through the cold core remain unlocated; no new cold-core hole is specified.',
 'input_geometry_sha256':{n:loaded_digest(s) for n,s in models.items() if s.Solids()},'source_sha256':{str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}
 (HERE/'controls-core-boundaries.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':checks,'pairs':pairs},indent=2),flush=True)
if __name__=='__main__':main()
