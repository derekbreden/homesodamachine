"""Native-proved curved departures from closely bounded loom dressing faces."""
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
 data,network,sections,fanouts=definition()
 for n in network:
  if 'retained-manifold' not in n['name']:continue
  p=n['to_dock'];p['point'][1]=460.2
  if 'J1' in n['name']:p['point'][0]=100.3
  p['lead_paths']=[[p['point'],(np.asarray(p['point'])+np.asarray(p['axis'])*length).tolist()] for length in [5.4,6.8,8.4,12.6,16.8]]
 models,records,_,_,_=audit.collect()
 bm,br=passed_body_models();models.update(bm)
 lm,lr=lower_lead_models();models.update(lm)
 models.update(protected_nameplate_models())
 models.update(strict_fluid_air_models(models,records)[0])
 for name,shape in list(models.items()):
  if name.startswith(('control-','power-','wire-')) or name=='rear-roof-hatch':models.pop(name);continue
  if name.startswith(('enclosure-back-top','enclosure-front-top')):
   models[name]=shape.intersect(cq.Solid.makeBox(240,241.685,130,cq.Vector(-120,84.015,240)))
 roof=json.loads((STUDY/'mounts/candidate.json').read_text())
 for name,fields in roof['working_envelopes'].items():
  if 'levers' in fields:models[name+'-lever-working-space']=cq.Shape.importBrep(str(ROOT/fields['levers']['brep']))
 models.update({n:s for n,(s,_) in sections.items()})
 models.update({'control-'+n:s for n,(s,_,_) in fanouts.items()})
 future_shapes={}
 for n in network:
  for end in ['from_dock','to_dock']:
   q=n[end];lead=q.get('lead_paths',[[q['point'],(np.asarray(q['point'])+np.asarray(q['axis'])*8.4).tolist()]])[0]
   future_shapes[q['label']]=sweep(lead,q['diameter_mm'],q['bend_radius_mm'])[0]
 checks=[];accepted={}
 for n in network:
  if 'retained-manifold' not in n['name'] and n['name'] not in ['loom-J1-coil-v-a','loom-J1-coil-v-b','loom-wago-sensors-digiten-flow','loom-J13-retained-cartridge-loom','loom-J11-retained-mq6-loom']:continue
  for which in ['from_dock','to_dock']:
   if n['name']=='loom-J1-coil-v-b' and which!='to_dock':continue
   if n['name']=='loom-J1-coil-v-a' and which!='from_dock':continue
   if n['name']=='loom-J11-retained-mq6-loom' and which!='from_dock':continue
   p=n[which];x,y,z=p['point'];R=n['bend_radius_mm'];candidates=[]
   if n['name']=='loom-J1-coil-v-a':
    for normal in [1.,2.]:
     for top in [340.3,342.]:
      for endy in [430.,438.,440.]:candidates.append([[x,y,z],[x,y+R+normal,z],[x,y+R+normal,top],[x,endy,top]])
   elif n['name']=='loom-J1-coil-v-b':
    for normal in [.5,1.,2.]:
     for endz in [255.5,256.5]:candidates.append([[x,y,z],[x,y+R+normal,z],[x,y+R+normal,endz]])
   elif n['name']=='loom-wago-sensors-digiten-flow':
    if which=='from_dock':
     for normal in [1.,2.,3.]:
      for endx in [-34.45,-30.,-24.]:
       for endy in [400.,406.]:candidates.append([[x,y,z],[x,y,z-R-normal],[endx,y,z-R-normal],[endx,endy,z-R-normal]])
    else:
     for normal in [1.,2.,3.]:
      for down in [293.9,292.5,290.]:
       for endx in [94.,95.]:
        candidates.append([[x,y,z],[x,y-R-normal,z],[x,y-R-normal,down],[endx,y-R-normal,down]])
     for normal in [1.,2.,3.]:
      for endx in [87.8,84.,79.5]:candidates.append([[x,y,z],[x,y-R-normal,z],[endx,y-R-normal,z]])
   elif n['name']=='loom-J13-retained-cartridge-loom':
    if which=='from_dock':
     for normal in [.5,1.,2.]:
      for top in [341.3,342.]:
       for endy in [374.,372.]:candidates.append([[x,y,z],[x+R+normal,y,z],[x+R+normal,y,top],[x+R+normal,endy,top]])
    else:
     passage=json.loads((HERE/'frame-j13-relief.json').read_text())
     assert passage['pass'],'Retained ridge-clip passage must pass before route preparation'
     assert passage['port_point']==p['point']
     candidates=passage['lead_paths']
   elif n['name']=='loom-J11-retained-mq6-loom':
    if which=='from_dock':
     for normal in [1.,2.,3.]:
      for endz in [321.5,322.,322.6]:candidates.append([[x,y,z],[x+R+normal,y,z],[x+R+normal,y,endz]])
    else:
     for plane in [280.,282.,286.5,291.,294.]:
      for aft in [300.,307.,312.,340.5]:
       candidates.append([[x,y,z],[x,y+9.4,z],[x,y+9.4,plane],[x,aft,plane],[-45.,aft,plane]])
     for plane in [286.5,291.,294.]:candidates.append([[x,y,z],[x,y+9.4,z],[x,y+9.4,plane]])
   elif which=='to_dock':
    if 'J2' in n['name']:
     for normal in [0.,.5,1.]:
      for fore in [440.,437.5]:candidates.append([[x,y,z],[x,y-R-normal,z],[x,y-R-normal,310.],[x,fore,310.]])
    for normal in [0.,.5,1.,2.]:
     for endz in [310.,326.4,338.]:
      candidates.append([[x,y,z],[x,y-R-normal,z],[x,y-R-normal,endz]])
    for normal in [1.,2.,3.]:
     for xend in [83.3,79.5,75.]:
      candidates.append([[x,y,z],[x,y-R-normal,z],[xend,y-R-normal,z]])
   else:
    if 'J1' in n['name']:
     for length in [5.4,6.8,8.4]:candidates.append([[x,y,z],[x,y+length,z]])
     for normal in [.2,.5,1.,2.]:
      for endx in [55.5,62.,67.]:
       candidates.append([[x,y,z],[x,y+R+normal,z],[endx,y+R+normal,z]])
       candidates.append([[x,y,z],[x,y+R+normal,z],[endx,y+R+normal,z],[endx,430.,z]])
    for normal in [.5,1.,2.]:
     for cornerz in [340.3,341.2,342.]:
      for endy in ([438.,440.,442.] if 'J2' in n['name'] else [430.,434.]):
       candidates.append([[x,y,z],[x,y+R+normal,z],[x,y+R+normal,cornerz],[x,endy,cornerz]])
   future={'reserved-lead-'+label:shape for label,shape in future_shapes.items() if label!=p['label']}
   good=[]
   for points in candidates:
    try:s,record=sweep(points,n['diameter_mm'],R)
    except ValueError as e:checks.append({'port':p['label'],'points_mm':points,'pass':False,'reason':str(e)});continue
    hits=native_hits(s,{**models,**future},[p['owner'],'control-'+n['name']]);b=bounds(s)
    stock=b[0]>=-103.5 and b[3]<=103.5 and b[5]<=351
    row={'port':p['label'],'points_mm':points,'native_interferences':hits,'bounds':b,'stock_scope_pass':stock,'pass':not hits and stock}
    checks.append(row)
    if row['pass']:good.append(points)
   if good:
    accepted[p['label']]={'port_point':p['point'],'diameter_mm':n['diameter_mm'],'bend_radius_mm':R,'lead_paths':good}
    if n['name']=='loom-J13-retained-cartridge-loom' and which=='to_dock':accepted[p['label']]['required_path']=True
 out={'prepared_leads':accepted,'checks':checks,'pass':len(accepted)==11,'scope':'Exact native curved departure options from counted dressing faces. Full completed looms require their own current hardware/wire/endpoint checks.',
 'input_geometry_sha256':{n:loaded_digest(s) for n,s in models.items() if s.Solids()},'source_sha256':{str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}
 (HERE/'controls-prepared-leads.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'pass':out['pass'],'accepted':{n:len(r['lead_paths']) for n,r in accepted.items()},'failed':[{k:q[k] for k in ['port','points_mm','native_interferences'] if k in q} for q in checks if not q['pass']]},indent=2),flush=True)
if __name__=='__main__':main()
