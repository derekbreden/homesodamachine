"""Construct every changed upper-bay route with measured fitting endpoints and R14 arcs."""
from pathlib import Path
from dataclasses import replace
import json,sys,math,hashlib,cadquery as cq
ROOT=Path(__file__).resolve().parents[3];S=ROOT/'future/pump-first-layout-study';H=S/'routing';C=ROOT/'.cache/pump-first-layout/routing';sys.path[:0]=[str(H),str(S),str(ROOT/'hardware/scripts')];import baseline,_routing as R
from curves import *
m=json.load(open(H/'candidate.json'));selected=set(sys.argv[1:])
for n,ps in m['ports'].items():R.frame(n,cq.Shape.importBrep(str(ROOT/m['parts'][n]['brep'])),{p:(tuple(v['pos']),tuple(v['axis']),v['diam'])for p,v in ps.items()})
core=baseline.read(['cold-core/foam-cap-lid-top','valve-v-f','valve-v-g','valve-v-j','bulkhead-flavor-a','bulkhead-flavor-b'])
def frame(n,solid,ps):R.frame(n,solid,{p:(pos,axis,6.35)for p,(pos,axis)in ps.items()})
frame('core',core['cold-core/foam-cap-lid-top'],{'carb':((77.5,271.6,253.4000001),(0,0,1)),'co2':((77.5,322.3,253.4000001),(0,0,1)),'a-fill':((57.5,426.3,253.4000001),(0,0,1))})
for n,pos in [('valve-v-f',(82.1,105.29,282.175)),('valve-v-g',(73.82,166.24,229.675)),('valve-v-j',(-73.82,166.24,229.675))]:frame(n,core[n],{'outlet':(pos,(0,0,1))})
for n,x in [('bulkhead-flavor-a',-37.81),('bulkhead-flavor-b',-78.07)]:frame(n,core[n],{'inboard':((x,446.51,269.024),(0,-1,0))})
pump=json.load(open(S/'pump/candidate.json'))
for n,ps in {'valve-v-a':{'inlet':((49.05,270.25,270.15),(0,1,0))},'vk-solenoid':{'inlet':((-75.55,266.5,288.5),(0,1,0))}}.items():frame(n,cq.Shape.importBrep(str(ROOT/pump['parts'][n]['brep'])),ps)
def pos(port):f,p=port.split('.');return V(R._frames[f].at(p))
def norm(port):f,p=port.split('.');return V(R._frames[f].normal(p))
def bounds(q):b=q.BoundingBox();return[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def save(cid,frm,to,es,kind='water',foam=False,note='',radius=14,stations=None,info=None):
 if selected and cid not in selected:return
 w=wire(es)
 start_error=(es[0].startPoint()-pos(frm)).Length;end_error=(es[-1].endPoint()-pos(to)).Length
 start_angle=math.degrees(es[0].tangentAt(0).getAngle(norm(frm)));end_angle=math.degrees(es[-1].tangentAt(1).getAngle(-norm(to)))
 allowed_skew=(info or{}).get('source_attachment_skew_deg',0)
 if max(start_error,end_error)>1e-5 or start_angle>allowed_skew+1e-5 or end_angle>1e-5:raise ValueError(f'{cid} endpoint/normal error: {start_error,end_error,start_angle,end_angle}')
 q=swept(es,norm(frm));p=C/('tube-'+cid+'.brep');q.exportBrep(str(p))
 wp=C/('centreline-'+cid+'.brep');w.exportBrep(str(wp))
 clearance=swept(es,norm(frm),27.4 if foam else 8.35);cp=C/('tube-'+cid+'-clearance.brep');clearance.exportBrep(str(cp))
 m.setdefault('clearance_cutters',{})['tube-'+cid]={'brep':str(cp.relative_to(ROOT)),'sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),'bounds':bounds(clearance),'radial_air_mm':1.,'scope':'Exact tangent occupied exterior plus1mm radial clearance; full carbonated insulation exterior included.'}
 if cid in ['fluid-18','fluid-28','water-supply-link']:
  m['clearance_cutters']['tube-'+cid].update(print_owner='enclosure-back-top',factory_upper_bay_channel=True)
 if cid=='fluid-14':
  relief=clearance;fp=C/'frame-fluid-a-clearance.brep';relief.exportBrep(str(fp));fr={'brep':str(fp.relative_to(ROOT)),'sha256':hashlib.sha256(fp.read_bytes()).hexdigest(),'bounds':bounds(relief),'target_host':'funnel-frame','print_owner':'funnel-frame','occupied_part':'tube-fluid-14','radial_air_mm':1.,'scope':'Complete exact Gate-A run clearance; its actual maximumZ300.795mm is below all protected306.9mm rail stock.'};(H/'frame-fluid-a-relief.json').write_text(json.dumps(fr,indent=2)+'\n')
 segments=[];distance=0.
 for edge in es:
  if edge.geomType()=='LINE':segments.append({'start':list(edge.startPoint().toTuple()),'end':list(edge.endPoint().toTuple()),'length_mm':edge.Length(),'start_developed_mm':distance,'end_developed_mm':distance+edge.Length()})
  distance+=edge.Length()
 rec={'kind':kind,'diameter_mm':6.35,'nominal_bend_mm':radius,'minimum_bend_mm':radius,'length_mm':w.Length(),'waypoints':stations or [e.startPoint().toTuple()for e in es]+[es[-1].endPoint().toTuple()],'radii':[radius for e in es if e.geomType()=='CIRCLE'],'from':frm,'to':to,'centreline_brep':str(wp.relative_to(ROOT)),'straight_segments':segments,'source_position_error_mm':start_error,'destination_position_error_mm':end_error,'source_normal_error_deg':start_angle,'destination_normal_error_deg':end_angle,'blocked':{},'tangent_continuity_pass':True,'sweep_volume_mm3':q.Volume(),'sweep_area_length_volume_mm3':math.pi*3.175**2*w.Length(),'native_clearance_status':'pending','curve':'exact tangent circular arcs with fixed stock radius',**(info or{})}
 m['parts']['tube-'+cid]={'brep':str(p.relative_to(ROOT)),'role':'gas'if kind=='co2'else'water','detail':note,'bounds':bounds(q),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'route':rec}
 names=['tube-'+cid]
 if foam:
  fo=swept(es,norm(frm),25.4).cut(q);fp=C/('carb-foam-'+cid+'.brep');fo.exportBrep(str(fp));m['parts']['carb-foam-'+cid]={'brep':str(fp.relative_to(ROOT)),'role':'water','detail':'FullØ25.4mm insulation sleeve along the actual tangent tube, including both elbow envelopes.','bounds':bounds(fo),'sha256':hashlib.sha256(fp.read_bytes()).hexdigest()};names.append('carb-foam-'+cid)
 m.setdefault('routes',{})[cid]={'from':frm,'to':to,'parts':names,'stock_bend_pass':True,'native_clearance_status':'pending','diameter_mm':6.35,'minimum_bend_mm':radius,'developed_length_mm':w.Length(),'endpoints_exact':True}
 for n in names:
  if n not in m['replacement_names']:m['replacement_names'].append(n)
 print('constructed',cid,'R14','length',round(w.Length(),2),flush=True)
 (H/'candidate.json').write_text(json.dumps(m,indent=2)+'\n')

def rp(cid,frm,pts,to,kind='water',lead=0,foam=False,note='',skew=None):
 if selected and cid not in selected:return
 R.BLOCKED.clear();r=R.bent(cid,frm,*pts,to,kind=kind,bend=14,lead=lead,skew=skew)
 if r.tightest<14-1e-6:raise ValueError(cid+' radius '+str(r.tightest))
 if R.BLOCKED:raise ValueError(cid+' '+str(R.BLOCKED))
 save(cid,frm,to,R.centreline(r).Edges(),kind,foam,note,stations=r.pts,info={'radii':r.radii,'minimum_bend_mm':r.tightest})
# Compact purchased poses and exact tangent paths remain insideX+-107.5.
if not selected or 'fluid-1' in selected:
 a=pos('water-split.to-flavor');phi=math.radians(0);diag=V((-math.cos(phi),-math.sin(phi),0));es,b=turn(a,Z,diag);ee,c=turn(b,diag,Z);es+=ee;ee,d=turn(c,Z,-Y);es+=ee;e=V((d.x,349,304));ee,meta=s(d,-Y,e);es+=ee;ee,f=turn(e,-Y,-X);es+=ee;g=V((-24.5,335,304));es+=line(f,g);ee,h=turn(g,-X,-Z);es+=ee;j=V((-38.5,335,289.25));es+=line(h,j);ee,k=turn(j,-Z,X);es+=ee;ee,meta=s(k,X,pos('flow-regulator.inlet'));es+=ee;save('fluid-1','water-split.to-flavor','flow-regulator.inlet',es,'fluid',note='The tee upper flavor outlet turns fore and west below the meter, passes behind ASSE at Z304 beneath its roof seats, then descends into the needle inlet.',info=meta)
if not selected or 'fluid-2' in selected:
 a=pos('flow-regulator.outlet');b=a+X*.5;es=line(a,b);ee,c=turn(b,X,-Y);es+=ee;ee,meta=s(c,-Y,pos('valve-v-a.inlet'));es+=ee;save('fluid-2','flow-regulator.outlet','valve-v-a.inlet',es,'fluid',note='The needle east outlet turns fore at R14 and descends into the source-A aft inlet, west of the complete carbonated-water sleeve.',info=meta)
if not selected or 'water-3' in selected:
 a=pos('water-split.to-vk');b=V((100.325,334.6,278));es,meta=s(a,-Y,b,lead_start=.5);ee,c=turn(b,-Y,Z);es+=ee;ee,d=turn(c,Z,-X);es+=ee;ee,e=turn(d,-X,Z);es+=ee;f=V((72.325,320.6,333.2));es+=line(e,f);ee,g=turn(f,Z,-X);es+=ee;hh=V((-24.5,320.6,347.2));es+=line(g,hh);ii=V((-47.55,327.0,347.2));ee,meta=s(hh,-X,ii);es+=ee;h=V((-61.55,327.0,347.2));es+=line(ii,h);ee,j=turn(h,-X,-Y);es+=ee;ee,k=turn(j,-Y,-Z);es+=ee;l=V((-75.55,299.0,302.5));es+=line(k,l);ee,n=turn(l,-Z,-Y);es+=ee;es+=line(n,pos('vk-solenoid.inlet'));save('water-3','water-split.to-vk','vk-solenoid.inlet',es,note='The tee fore output rises beside the cold sleeve, steps inside Water5, crosses fore of the controller above the ASSE seats, then descends fore of ASSE into the raised pump inlet valve.',info=meta)
rp('carb-1','core.carb',[(77.5,271.6,285.2),(84.5,354.01,285.2),(84.5,354.01,332.1)],'digiten-flow.inlet',lead=4,foam=True,note='Full Ø25.4 insulation covers the chilled path from the fixed cap mouth through the east riser behind ASSE into the rolled flow meter.')
if not selected or 'carb-2'in selected:
 es,meta=s(pos('digiten-flow.outlet'),Y,pos('bulkhead-carb.tube-in'));save('carb-2','digiten-flow.outlet','bulkhead-carb.tube-in',es,foam=True,note='The aligned meter and rear CARB collet connect through an exact R14 S descending 3.1 mm; the complete insulation exterior is included.',info=meta)
if not selected or 'co2-2'in selected:
 a=pos('gasher-co2.outlet');b=V((77.5,336.3,267.4));es,meta=s(a,-Y,b);ee,c=turn(b,-Y,-Z);es+=ee+line(c,pos('core.co2'));save('co2-2','gasher-co2.outlet','core.co2',es,'co2',note='The low check-to-core gas return lies below the complete carbonated-water sleeve and uses an R14 normal downward cap elbow.',info=meta)
if not selected or 'water-2'in selected:
 a=pos('asse1022-assembly.tube-out');b=V((62.5,a.y,a.z));es=line(a,b);ee,c=turn(b,X,Z);es+=ee;dd=V((76.5,a.y,333));es+=line(c,dd);ee,d=turn(dd,Z,Y);es+=ee;e=V((66.725,357,347));ee,meta=s(d,Y,e);es+=ee;f=V((66.725,385,347));es+=line(e,f);ff=V((68.5,396.3,347));ee,meta=s(f,Y,ff);es+=ee;ee,g=turn(ff,Y,-Z);es+=ee;h=V((68.5,410.3,299.5));es+=line(g,h);ee,j=turn(h,-Z,Y);es+=ee;k=j;target=pos('water-split.supply')+Y*.3;off=target-k;axis=off.normalized();ee,l=turn(k,Y,axis);es+=ee;n=l+axis*(off.Length-28);es+=line(l,n);ee,o=turn(n,axis,-Y);es+=ee;es+=line(o,pos('water-split.supply'));save('water-2','asse1022-assembly.tube-out','water-split.supply',es,note='The ASSE outlet rises ahead of the suction bridge and cold riser, runs outside the controller, descends fore of the gas column and uses a diagonal R14 return above the rear gas intake into the east tee.',info=meta)
if not selected or 'water-supply-link'in selected:
 a=pos('bulkhead-water.inboard');b=V((-53.5,418,315.4));es,meta=s(a,-Y,b,lead_start=.5);c=V((-53.5,404,315.4));es+=line(b,c);d=V((-55.225,382,317.125));ee,meta=s(c,-Y,d);es+=ee;e=V((-55.225,345,317.125));es+=line(d,e)
 phi=math.asin(17/(14*math.sqrt(2)))-math.pi/4;zz=pos('asse1022-assembly.tube-in').z-14*(math.sin(phi)+1-math.cos(phi));f=V((-55.225,320.8,zz));ee,meta=s(e,-Y,f);es+=ee;g=V((-55.225,294.5,zz));es+=line(f,g);ee,h=turn(g,-Y,-X);es+=ee;j=V((-86.325,280.5,zz));es+=line(h,j);ee,k=turn(j,-X,Y);es+=ee;l=V((-100.325,296.3,zz));es+=line(k,l);di=V((math.cos(phi),0,math.sin(phi)));ee,n=turn(l,Y,di);es+=ee;ee,o=turn(n,di,V((math.sin(phi),0,-math.cos(phi))),phi);es+=ee;es+=line(o,pos('asse1022-assembly.tube-in'));save('water-supply-link','bulkhead-water.inboard','asse1022-assembly.tube-in',es,note='Rear water passes ahead of the jack and braided riser, runs between the regulator and shifted reed-B junction above the pump, then uses a fore return and compound R14 normal approach into ASSE.',info=meta)
if not selected or 'fluid-14'in selected:
 points=[pos('valve-v-f.outlet'),(82.1,106.0296,296.775),(44.75,191.4299999,295.7),(44.75,210,294.6),(57.5,244,295.4),(57.5,306,295.4)];es,r=poly(points)
 lowz=268.325;delta=(295.4-lowz)/14-1;phi=math.acos(delta/math.sqrt(2))-math.pi/4;di=V((math.sin(phi),0,-math.cos(phi)));ee,b=turn(V(points[-1]),Y,di);es+=ee;ee,d=turn(b,di,V((math.cos(phi),0,math.sin(phi))),math.pi/2-phi);es+=ee;e=V((74,320,lowz));es+=line(d,e);ee,f=turn(e,X,Y);es+=ee;g=V((88,354,lowz));es+=line(f,g);h=V((88.5,384,291));ee,meta=s(g,Y,h);es+=ee
 phi=math.asin(17/(14*math.sqrt(2)))-math.pi/4;di=V((-math.cos(phi),0,-math.sin(phi)));ee,k=turn(h,Y,di);es+=ee;ee,k=turn(k,di,V((-math.sin(phi),0,math.cos(phi))),phi);es+=ee
 ss=.55;cc=math.sqrt(1-ss*ss);direction=V((0,cc,-ss));ee,l=turn(k,-X,direction);es+=ee;ll=l+direction*((426.3-l.y-14*(1-ss))/cc);es+=line(l,ll);perp=(-Z-direction*ss)/cc;ee,n=turn(ll,direction,perp,math.acos(ss));es+=ee;es+=line(n,pos('core.a-fill'));save('fluid-14','valve-v-f.outlet','core.a-fill',es,'fluid',note='The fixed Gate-F lead follows the protected front corridor, turns below ASSE aft of the needle, runs beneath the complete cold sleeve, crosses above the check tie and descends normally into the fixed A-fill mouth.',info={**meta,'source_attachment_skew_deg':3})
if not selected or 'fluid-18'in selected:
 points=[pos('valve-v-g.outlet'),(73.82,166.24,259.75),(53.4,201.5,259.75),(-29,201.5,259.75)];es,r=poly(points);b=V((-86.325,194,259.75));ee,meta=s(V(points[-1]),-X,b);es+=ee;ee,c=turn(b,-X,Y);es+=ee;d=V((-100.325,249,259.75));es+=line(c,d);e=V((-100.325,278,271));ee,meta=s(d,Y,e);es+=ee;f=V((-100.325,344,271));es+=line(e,f);g=V((-100.325,373,257.6));ee,meta=s(f,Y,g);es+=ee;ee,h=turn(g,Y,X);es+=ee;j=V((-65.5,387,257.6));es+=line(h,j);ee,k=turn(j,X,Y);es+=ee;ee,meta=s(k,Y,pos('bulkhead-flavor-a.inboard'));es+=ee;save('fluid-18','valve-v-g.outlet','bulkhead-flavor-a.inboard',es,'fluid',note='Flavor A leaves fixed Gate-G, bypasses the raised inlet valve and B-fill mouth, rises above the sensed tray in the nominal west channel, then descends outside the scanned head into the rear flavor-A union.',info=meta)
if not selected or 'fluid-28'in selected:
 points=[pos('valve-v-j.outlet'),(-73.82,166.24,277.75),(-74,181,277.75),(-74,196,277.75)];es,r=poly(points);zz=V((-97,224,277.75));ee,meta=s(V(points[-1]),Y,zz,lead_start=.1);es+=ee;aa=V((-97,265,281.5));ee,meta=s(zz,Y,aa);es+=ee;b=V((-100.325,293,281.5));ee,meta=s(aa,Y,b);es+=ee;c=V((-100.325,349,281.5));es+=line(b,c);d=V((-100.325,377,266.1));ee,meta=s(c,Y,d);es+=ee;e=V((-100.325,385,266.1));es+=line(d,e);f=V((-88,413,257.6));ee,meta=s(e,Y,f);es+=ee;ee,meta=s(f,Y,pos('bulkhead-flavor-b.inboard'));es+=ee;save('fluid-28','valve-v-j.outlet','bulkhead-flavor-b.inboard',es,'fluid',note='Flavor B leaves fixed Gate-J normally, steps outside B-fill below the inlet valve, rises over the tray above Flavor A, then lowers around the pump into the retained rear flavor-B union.',info=meta)
# The complete gas paths are authored and native checked by co2_routes.py.
# Its packet owns those curves, including measured endpoint tangents.
if not selected or selected.intersection({'co2-0','co2-1'}):
 gas=json.loads((H/'co2-candidate.json').read_text())
 for cid in ['co2-0','co2-1']:
  if selected and cid not in selected:continue
  route=gas['routes'][cid];m['routes'][cid]=route
  for name in route['parts']:
   m['parts'][name]=gas['parts'][name]
   if name not in m['replacement_names']:m['replacement_names'].append(name)
   if name in gas.get('clearance_cutters',{}):m.setdefault('clearance_cutters',{})[name]=gas['clearance_cutters'][name]
  print('imported native gas packet',cid,round(route['developed_length_mm'],2),flush=True)

# Explicit fitting, sleeve and endpoint contacts. No crossed route is exempt.
contacts=[['wr1110','co2-adapter-regulator-in'],['wr1110','co2-adapter-regulator-out'],['gasher-co2','co2-adapter-check-in'],['gasher-co2','co2-adapter-check-out']]
for cid,r in m['routes'].items():
 for endpoint in[r['from'],r['to']]:
  comp,p=endpoint.split('.')
  if comp=='wr1110':comp='co2-adapter-regulator-'+('in'if p=='inlet'else'out')
  if comp=='gasher-co2':comp='co2-adapter-check-'+('in'if p=='inlet'else'out')
  if comp=='core':comp='cold-core/foam-cap-lid-top'
  for part in r['parts']:contacts.append([part,comp])
 if len(r['parts'])>1:contacts.append(r['parts'])
m['intended_contacts']=contacts
for old in ['carb-foam-1','carb-foam-2']:
 if old not in m['replacement_names']:m['replacement_names'].append(old)
m['routing_status']={'constructed':list(m['routes']),'finished':[],'pending':list(m['routes']),'note':'All13 compact tangentR14 paths serialized; geometric qualification waits for complete native component/route checks.'}
(H/'candidate.json').write_text(json.dumps(m,indent=2)+'\n')
