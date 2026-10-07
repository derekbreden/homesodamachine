"""Native endpoint lead feasibility before the complete grouped search."""
from pathlib import Path
import argparse,json,sys
import cadquery as cq
import numpy as np

HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
sys.path[:0]=[str(HERE),str(STUDY)]
from controls_looms import definition,protected_nameplate_models,native_hits,loaded_digest
from controls_harness import passed_body_models,lower_lead_models,strict_fluid_air_models
from native_harness import sweep,bounds,broad
import audit,baseline

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--include-power',action='store_true');args=parser.parse_args()
 data,network,sections,fanouts=definition();models,records,_,_,_=audit.collect()
 for name,r in baseline.prepare()['parts'].items():
  if name in records or not broad(r['bounds'],[-107.5,84,241,107.5,465.3,355]):continue
  models[name]=cq.Shape.importBrep(str(baseline.CACHE/r['file']))
 models.update(protected_nameplate_models())
 body_models,body_records=passed_body_models();models.update(body_models);records.update(body_records)
 lower_models,lower_records=lower_lead_models();models.update(lower_models);records.update(lower_records)
 models.update(strict_fluid_air_models(models,records)[0])
 mounts=json.loads((STUDY/'mounts/candidate.json').read_text())
 for name,r in mounts['working_envelopes'].items():
  if 'levers' in r:models[name+'-lever-working-space']=cq.Shape.importBrep(str(ROOT/r['levers']['brep']))
 blocked={}
 for name,s in models.items():
  if name.startswith(('control-','wire-','power-')) or name=='rear-roof-hatch':continue
  if name.startswith(('enclosure-back-top','enclosure-front-top')):s=s.intersect(cq.Solid.makeBox(240,241.685,130,cq.Vector(-120,84.015,240)))
  if s.Solids():blocked[name]=s
 blocked.update({n:s for n,(s,r) in sections.items()});blocked.update({'control-'+n:s for n,(s,_,_) in fanouts.items()})
 if args.include_power:
  power=json.loads((HERE/'power-candidate.json').read_text())
  blocked.update({n:cq.Shape.importBrep(str(ROOT/r['brep'])) for n,r in power['parts'].items()})
 blocked.update(lower_models)
 rows=[]
 for n in network:
  for end in ['from_dock','to_dock']:
   p=n[end];options=[];print('DOCK',n['name'],end,flush=True)
   for points in p['lead_paths']:
    shape,record=sweep(points,n['diameter_mm'],n['bend_radius_mm']);b=bounds(shape)
    limits={'width':b[0]>=-103.5-1e-5 and b[3]<=103.5+1e-5,'roof':b[5]<=351.00001,'floor':b[2]>=241.5-1e-5}
    hits=native_hits(shape,blocked,[p['owner']]) if all(limits.values()) else[]
    options.append({'points_mm':points,'native_interferences':hits,'limits':limits,'pass':all(limits.values()) and not hits})
    if options[-1]['pass']:break
   row={'route':n['name'],'endpoint':end,'port':p,'options':options,'pass':any(q['pass'] for q in options)};rows.append(row)
   if not row['pass']:print(json.dumps(row),flush=True)
 report={'checks':rows,'pass':all(r['pass'] for r in rows),'include_power':args.include_power,'input_geometry_sha256':{n:loaded_digest(s) for n,s in blocked.items()},
  'scope':'Exact full native endpoint lead candidates including working levers, protected forward stock and counted static controls. Aft shell and rear hatch stock are admitted wiring recesses; final swept clearance cutters must preserve the established 3 mm outer stock. This is endpoint feasibility only; other future leads and complete grouped route closure remain separate.'}
 (HERE/'loom-dock-probe.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'ends':len(rows),'pass':report['pass'],'failures':[(r['route'],r['endpoint']) for r in rows if not r['pass']]}),flush=True)

if __name__=='__main__':main()
