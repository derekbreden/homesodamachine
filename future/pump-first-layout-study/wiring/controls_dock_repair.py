"""Exact departure diagnosis and curved escape options for counted looms."""
from pathlib import Path
import argparse,json,sys
import numpy as np
import cadquery as cq

HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
sys.path[:0]=[str(HERE),str(STUDY)]
from controls_looms import definition,native_hits,protected_nameplate_models,loaded_digest
from controls_harness import passed_body_models,lower_lead_models,strict_fluid_air_models,required_power_departures
from native_harness import sweep,bounds
import audit

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--targets',action='store_true');args=parser.parse_args()
 data,network,sections,fanouts=definition();models,records,_,_,_=audit.collect()
 body,br=passed_body_models();models.update(body);records.update(br)
 lower,lr=lower_lead_models();models.update(lower);records.update(lr)
 models.update(protected_nameplate_models())
 models.update(strict_fluid_air_models(models,records)[0])
 for name,shape in list(models.items()):
  if name.startswith(('control-','power-','wire-')) or name=='rear-roof-hatch':models.pop(name);continue
  if name.startswith(('enclosure-back-top','enclosure-front-top')):
   models[name]=shape.intersect(cq.Solid.makeBox(240,241.685,130,cq.Vector(-120,84.015,240)))
 roof=json.loads((STUDY/'mounts/candidate.json').read_text())
 for name,working in roof['working_envelopes'].items():
  if 'levers' in working:models[name+'-lever-working-space']=cq.Shape.importBrep(str(ROOT/working['levers']['brep']))
 models.update({n:s for n,(s,_) in sections.items()})
 models.update({'control-'+n:s for n,(s,_,_) in fanouts.items()})
 power=json.loads((HERE/'power-candidate.json').read_text())
 models.update({n:cq.Shape.importBrep(str(ROOT/r['brep'])) for n,r in power.get('parts',{}).items()})
 models.update(required_power_departures()[0])
 current=json.loads((HERE/'controls-candidate.json').read_text())
 wire_models={n:cq.Shape.importBrep(str(ROOT/r['brep'])) for n,r in current.get('parts',{}).items() if n.startswith('control-loom-') and 'from_dock' in current.get('control_routes',{}).get(n,{})}
 rows=[];accepted={}
 names=['loom-J1-coil-v-b','loom-J6-reed-A','loom-J6-wago-reeds-a','loom-J9-retained-display-loom','loom-J13-retained-cartridge-loom','loom-J11-retained-mq6-loom']
 for route in [n for n in network if n['name'] in names]:
  endpoint='to_dock' if args.targets else 'from_dock'
  p=route[endpoint];x,y,z=p['point'];R=route['bend_radius_mm'];normal_axis=np.asarray(p['axis']);candidates=list(p['lead_paths'])
  for normal in ([] if p.get('required_path') else [.5,1.,2.,3.]):
   corner=np.asarray(p['point'])+normal_axis*(R+normal)
   for height in [340.3,344.5,326.4,321.,305.5,291.,280.]:
    if normal_axis[2]!=0:continue
    if abs(height-z)<2*R:continue
    q=corner.copy();q[2]=height
    candidates.append([p['point'],corner.tolist(),q.tolist()])
    for endy in [330.,425.]:
     if abs(endy-y)<2*R:continue
     end=q.copy();end[1]=endy
     candidates.append([p['point'],corner.tolist(),q.tolist(),end.tolist()])
   # A fore/aft escape before an upward turn keeps the contact axis exact.
   for endy in [350.,400.,435.]:
    if normal_axis[1]!=0:continue
    q=corner.copy();q[1]=endy
    if abs(endy-y)<2*R:continue
    candidates.append([p['point'],corner.tolist(),q.tolist()])
   for endx in [55.5,61.5,65.]:
    if normal_axis[0]!=0 or abs(endx-x)<2*R:continue
    q=corner.copy();q[0]=endx
    candidates.append([p['point'],corner.tolist(),q.tolist()])
  # Extend existing authored departures far enough to reach an open lane.
  for lead in p['lead_paths']:
   if len(lead)<3:continue
   end=np.asarray(lead[-1],float);axis=int(np.argmax(abs(end-np.asarray(lead[-2],float))))
   sign=np.sign(end[axis]-lead[-2][axis])
   for distance in [12.,25.,45.]:
    q=end.copy();q[axis]+=sign*distance
    candidates.append(lead[:-1]+[q.tolist()])
   for normal in [.5,1.,2.]:
    corner=end.copy();corner[axis]+=sign*(R+normal)
    for turn_axis in range(3):
     if turn_axis==axis:continue
     for offset in [-25.,-12.,12.,25.]:
      q=corner.copy();q[turn_axis]+=offset
      candidates.append(lead+[corner.tolist(),q.tolist()])
  blocked={**models,**wire_models};good=[]
  for points in candidates:
   try:shape,record=sweep(points,route['diameter_mm'],R)
   except ValueError as e:rows.append({'route':route['name'],'points_mm':points,'pass':False,'reason':str(e)});continue
   hits=native_hits(shape,blocked,[p['owner'],'control-'+route['name']]);b=bounds(shape)
   stock=b[0]>=-103.5 and b[3]<=103.5 and b[2]>=241.5 and b[5]<=351
   row={'route':route['name'],'port':p['label'],'points_mm':points,'native_interferences':hits,'bounds':b,'pass':not hits and stock}
   rows.append(row)
   if row['pass']:good.append(points)
  if good:
   good.sort(key=lambda points:-len(points))
   accepted[p['label']]={'port_point':p['point'],'diameter_mm':route['diameter_mm'],'bend_radius_mm':R,'lead_paths':good}
   if p.get('required_path'):accepted[p['label']]['required_path']=True
  print(json.dumps({'route':route['name'],'good':len(good),'default':rows[-len(candidates):][:len(p['lead_paths'])]}),flush=True)
 report={'prepared_leads':accepted,'checks':rows,'pass':len(accepted)==len(names),
  'input_geometry_sha256':{n:loaded_digest(s) for n,s in {**models,**wire_models}.items() if s.Solids()},
  'scope':'Exact counted normal-axis departures and optional curved docking escapes, with current full physical hardware, 1 mm fluid-air tools, fixed static controls and published partial power/other control paths occupied. Complete loom search remains required.'}
 filename='controls-target-repair.json' if args.targets else 'controls-dock-repair.json'
 (HERE/filename).write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'pass':report['pass'],'good':{k:len(v['lead_paths']) for k,v in accepted.items()}}),flush=True)
if __name__=='__main__':main()
