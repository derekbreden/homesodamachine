"""Canonical controller pin inventory and occupied1.7mm loom candidates.

The board's native purchased wafer geometry is retained. Its exact canonical
pin map feeds the same11.65mm conservative contact-to-free-wire allowance as
the accepted wiring review. Any unlocated device contact remains a named
interface reservation; the artifact never calls that geometry measured.
"""
from pathlib import Path
import argparse,hashlib,json,math,sys
import cadquery as cq
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
OUT=ROOT/'.cache/pump-first-layout/wiring/controls'
sys.path[:0]=[str(HERE),str(STUDY)]
from native_harness import bounds,sweep
from controls_harness import ControlsGuide


def port(owner,point,axis,label,basis='Nominal terminal-face reservation'):
 return {'owner':owner,'point':list(point),'axis':list(axis),'label':label,'basis':basis}

def inventory():
 canonical=json.loads((HERE/'canonical-pins.json').read_text());pins={};ports={};jobs=[];boundaries={};contracts=[]
 structure=json.loads((STUDY/'structure/candidate.json').read_text())
 board=cq.Shape.importBrep(str(ROOT/structure['parts']['pcba']['brep']))
 board_bounds=bounds(board)
 board_delta_x=board_bounds[0]+20.0
 board_delta_y=board_bounds[1]-326.8
 board_delta_z=board_bounds[5]-351.0
 def add(key,p):ports[key]=p;return key
 def job(name,a,b,topology,loom=None,cut=None):jobs.append({'name':name,'from':a,'to':b,'topology':topology,'loom':loom,'baseline_bench_cut_mm':cut})
 for name,c in canonical['connectors'].items():
  pins[name]={}
  for label,(dx,dy) in c['pins']:
   x=c['y']+dy+16.3+board_delta_x;y=c['x']+dx+400.61606375+board_delta_y
   key=add(name+':'+label,port('pcba',(x,y,335.75+board_delta_z),(0,0,-1),name+' '+label,'Canonical physical PCB pinXY; nominal free wire plane11.65mm below the current native PCBtop'))
   pins[name][label]=key
  contracts.append({'connector':name,'count':c['count'],'canonical_labels':[label for label,_ in c['pins']],
    'pin_contact_allowance_mm':11.65,'status':'Expansion wafer retained with no installed loom' if name=='J8' else 'Populated loom',
    'mating_housing_and_crimp_scope':'Purchased wafer is native; full XH mating housing and crimp insertion remain inherited fit reservations.'})
 # J10 belongs to the power module, but its exact nominal face is explicit here.
 for label,x in [('GND',-7.4),('V12',-2.4)]:
  add('J10:'+label,port('pcba',(x+board_delta_x,412.76606415+board_delta_y,337.5000002+board_delta_z),(0,0,-1),'J10 '+label,'Nominal reference clamp mouth; power module owns the two16AWG conductors'))
 # Fixed cartridge/manifold loom boundaries: native accepted bare corridor.
 # Source valveA/B andVK are the changed interfaces and are routed fully.
 electrical=json.loads((STUDY/'pump/electrical-ends.json').read_text())
 # The reference blades lack polarity markings. Pin identity is localX sign;
 # logical feed and return below must be confirmed against the actual diode.
 native_names={'VA':'valve-v-a','VB':'valve-v-b','VK':'vk-solenoid'}
 blade_points={name:[electrical[n]['-1']['point_mm'],electrical[n]['1']['point_mm']] for name,n in native_names.items()}
 blade_axes={name:[0 if abs(v)<1e-8 else v for v in electrical[n]['-1']['outward_axis']] for name,n in native_names.items()}
 blade_owners={'VA':'coil-v-a','VB':'coil-v-b','VK':'vk-solenoid'}
 for name,points in blade_points.items():
  for i,p in enumerate(points):add(name+(':+candidate' if i==0 else ':return-candidate'),port(blade_owners[name],p,blade_axes[name],name+' blade localX'+('−' if i==0 else '+'),'Exact native front-face centre; reference does not establish electrical polarity'))
 job('J1-OUT1-VA',pins['J1']['OUT1'],'VA:return-candidate','J1OUT1 to native sourceA blade','J1',550)
 job('J1-OUT2-VB',pins['J1']['OUT2'],'VB:return-candidate','J1OUT2 to native sourceB blade','J1',550)
 job('J2-OUT3-VK',pins['J2']['OUT3'],'VK:return-candidate','J2OUT3 to nativeVK blade','J2',150)
 lanes={'J1':[(94.625,250.4),(94.625,248.7),(94.625,247),(94.625,245.3),(94.625,243.6),(96.325,243.6),(96.325,245.3)],
        'J2':[(92.925,250.4),(92.925,248.7),(92.925,247),(92.925,245.3)]}
 for connector,labels in [('J1',['COM','OUT3','OUT4','OUT5','OUT6','OUT7','OUT8']),('J2',['COM','FAN','OUT1','OUT2'])]:
  for i,label in enumerate(labels):
   x,z=lanes[connector][i];key=add(connector+'-'+label+'-fixed',port('retained-manifold-loom',(x,183,z),(0,1,0),connector+' '+label+' fixed bare-loom boundary','Accepted unsleeved side corridor X92.075..97.175,Z242.75..251.25; forward loom retained'))
   boundaries[key]={'scope':'Fixed foreground harness beyond upper-bay study','source':'hardware/wiring/manifold-junction-clearance-check.json'}
   job(connector+'-'+label,pins[connector][label],key,'Controller to retained protected manifold loom',connector,300 if label=='COM' else (650 if label=='FAN' else 550))
 # Faucet IDC nominal mouths on the exact moved keystone's inboard face.
 key_shape=cq.Shape.importBrep(str(ROOT/structure['parts']['keystone-jack']['brep']))
 key_bounds=bounds(key_shape)
 key_centre_x=(key_bounds[0]+key_bounds[3])/2
 key_contact_z=key_bounds[2]+5.405
 for i,label in enumerate(['IO33','IO35','V5','GND']):
  key=add('keystone-'+label,port('keystone-jack',(key_centre_x-4.5+3*i,key_bounds[1],key_contact_z),(0,-1,0),'IDC '+label,'Current native inboard face; four IDC clamp centres and lower-face offset5.405mm are nominal reservations'))
  job('J3-'+label,pins['J3'][label],key,'Faucet TTL/5V/GND to retained inboard keystone','J3')
 # Horizontal relay working face is native, pole pitch5mm remains reference.
 mount=json.loads((STUDY/'mounts/candidate.json').read_text())
 for ri,label in [(1,'IO19'),(2,'IO2')]:
  face=mount['endpoints'][f'relay-{ri}']['logic']['point'];x,y,z=face
  for signal,offset in [('GND',-5),('V5',0),(label,5)]:
   key=add(f'R{ri}-{signal}',port(f'relay-{ri}',(x,y+offset,z),(0,0,1),f'Relay{ri} '+signal,'Exact native top-face centre;5mm clamp pitch is representative'))
   job(f'J5-{signal}-R{ri}',pins['J5'][signal],key,'Relay opto-control and5V rail; AC/DC divider retained','J5')
 # Complete the three changed source-valve positive branches at the retained
 # manifold commons; other foreground coil branches remain at their fixed station.
 for name,owner,point in [('VA','wago-mana',(86.2,165.05,274.04)),('VB','wago-mana',(86.2,165.05,280)),('VK','wago-manb',(85.9,169,258))]:
  key=add('common-'+name,port(owner,point,(-1,0,0),'COM branch '+name,'Nominal source groove face on retained common; metal clamp centre remains unmeasured'))
  job('COM-'+name,key,name+':+candidate','Retained manifold common to changed native source-valve blade',None,350 if name!='VK' else 300)
 # Each eight-conductor reservoir service lead occupies its accepted6.8mm bore.
 # Ring centres atR2.35 give0.2mm nominal radial bore air and0.099mm conductor air.
 for reservoir,y,connector,labels in [('A',458.3,'J6',['RA1','RA2','RA3','RA4']),('B',189.3,'J7',['RB1','RB2','RB3','RB4'])]:
  for i,label in enumerate(labels):
   a=i*math.pi/4;key=add('reed-'+reservoir+'-'+label,port('cold-core/foam-cap-lid-top',(-31+2.35*math.cos(a),y+2.35*math.sin(a),253.4),(0,0,1),label+' retained column boundary','Actual accepted6.8mm bore; individual ring positions are nominal harness packing'))
   boundaries[key]={'scope':'Retained pre-soldered reed column below cap','bore_axis_mm':[-31,y,253.4],'bore_diameter_mm':6.8}
   job(connector+'-'+label,pins[connector][label],key,'Controller reed input to retained cold-core column',connector)
 junction=json.loads((STUDY/'mounts/junction-port-approaches.json').read_text())['junctions']
 def wg(name,index):
  p=next(row for row in junction[name] if row['port_index']==index);key=name+':'+str(index)
  if key not in ports:add(key,port(name,p['mouth'],p['outward_axis'],key,'Exact rotated source groove pitch; nominal metal clamp reservation'))
  return key
 for connector,name in [('J6','wago-reeds-a'),('J7','wago-reeds-b'),('J4','wago-sensors')]:
  job(connector+'-GND',pins[connector]['GND'],wg(name,1),'Shared rail to device-end ground fanout',connector)
 for reservoir,name,y in [('A','wago-reeds-a',458.3),('B','wago-reeds-b',189.3)]:
  for i in range(4):
   a=(i+4)*math.pi/4;key=add('reed-'+reservoir+'-GND'+str(i+1),port('cold-core/foam-cap-lid-top',(-31+2.35*math.cos(a),y+2.35*math.sin(a),253.4),(0,0,1),'Reservoir'+reservoir+' ground'+str(i+1),'Nominal ring packing in accepted bore; existing pre-soldered column remains below boundary'))
   job('fanout-'+reservoir+'-GND'+str(i+1),wg(name,i+2),key,'Device-end ground fanout to retained reed column')
 # Boundaries without located purchased contact geometry remain explicit.
 # No new cold-core hole or donor connector is created by these reservations.
 for label,p in [('CHI',(-95.6,408.55,253.4)),('CLO',(-93.8,408.55,253.4))]:
  key=add('carb-'+label,port('retained-cold-core-service-leads',p,(0,0,1),label+' retained service lead','Carbonator lead exit is unlocated in native source; service-bay boundary reservation only'))
  boundaries[key]={'scope':'Carbonator reed service lead exit is not physically located'};job('J7-'+label,pins['J7'][label],key,'Carbonator reed service-bay lead boundary','J7')
 for label,p in [('3V3',(-88.9,396.,253.4)),('IO26',(-87.1,396.,253.4))]:
  key=add('probe-'+label,port('retained-cold-core-service-leads',p,(0,0,1),label+' probe lead boundary','Probe cable exit is unlocated in native source; service-bay reservation only'))
  boundaries[key]={'scope':'Probe lead exit below retained core is not physically located'};job('J4-'+label,pins['J4'][label],key,'Temperature lead boundary','J4')
 for name,index,label,point in [('wago-reeds-b',6,'carb-CHI-GND',(-81.6,408.55,253.4)),('wago-reeds-b',7,'carb-CLO-GND',(-79.8,408.55,253.4)),('wago-sensors',2,'probe-GND',(0,395,253.4))]:
  key=add(label,port('retained-cold-core-service-leads',point,(0,0,1),label,'Unlocated retained core service lead; upper approach reservation only'))
  job('fanout-'+label,wg(name,index),key,'Device-end ground to retained core service lead boundary')
 # The measured DIGITEN source locates its pigtail root and outward axis.
 # Current flow-axis roll maps sourceX->worldY,sourceY->worldX,sourceZ->-worldZ;
 # the flexible conductor order/length remains an explicit dressing reservation.
 routing=json.loads((STUDY/'routing/candidate.json').read_text())
 meter_in=routing['ports']['digiten-flow']['inlet']['pos'];meter_out=routing['ports']['digiten-flow']['outlet']['pos']
 meter_root=(meter_in[0]+14.8,(meter_in[1]+meter_out[1])/2,meter_in[2]-26.5)
 for i,label in enumerate(['V5','IO25']):
  key=add('meter-'+label,port('digiten-flow',(meter_root[0]-1.7+i*1.7,meter_root[1],meter_root[2]),(0,0,-1),'Flow meter '+label,'Measured pigtail root and outward axis;1.7mm conductor order within6x3mm root is nominal'))
  job('J4-'+label,pins['J4'][label],key,'Flow meter signal/V5 nominal lead reservation','J4')
 # Dry LM393 board must stay above the tray; its exact board is not in CAD.
 for i,label in enumerate(['IO27','IO23']):
  key=add('moisture-'+label,port('moisture-comparator-reserve',(-69+2.5*i,303,275.0),(0,1,0),'Dry moisture comparator '+label,'Dry comparator is not a purchased native model; nominal service lead boundary above the drip pan, west of the suction chain'))
  job('J4-'+label,pins['J4'][label],key,'Dry moisture comparator signal/switched supply','J4')
 for name,index,label,point,axis,owner in [('wago-sensors',3,'meter-GND',(meter_root[0]+1.7,meter_root[1],meter_root[2]),(0,0,-1),'digiten-flow'),('wago-sensors',4,'moisture-GND',(-64,303,275.0),(0,1,0),'moisture-comparator-reserve')]:
  key=add(label,port(owner,point,axis,label,'Nominal lead interface; actual device contact remains unlocated'))
  job('fanout-'+label,wg(name,index),key,'Device-end sensor ground fanout')
 # Locate the unchanged front interfaces on their real admitted native bores.
 # The lower refrigeration harness is outside this study's upper bay.
 from retained_foreground import passages
 native_passages=passages()
 for connector,labels,kind,owner in [
  ('J9',['V12','GND','A','B'],'display','retained-display-loom'),
  ('J13',['AM2','AM1','BM2','BM1'],'cartridge','retained-cartridge-loom')]:
  p=native_passages[kind];x,y,z=p['point']
  for i,label in enumerate(labels):
   key=add(connector+'-'+label+'-fixed',port(owner,(x+(i-1.5)*1.7,y,z),p['axis'],label+' admitted native cable-passage boundary','Actual retained native bore; individual ribbon order and downstream terminal dressing are nominal'))
   boundaries[key]={'scope':p['scope'],'native_passage':p};job(connector+'-'+label,pins[connector][label],key,'Controller to unchanged native '+connector+' cable passage',connector,350 if connector=='J13' else 400)
 for i,label in enumerate(['GND','V5','DOUT','AOUT']):
  point=(-92.5+(-.9 if i%2==0 else .9),374.+(-.9 if i<2 else .9),253.4)
  key=add('J11-'+label+'-fixed',port('retained-mq6-loom',point,(0,0,1),label+' retained lower-cabinet loom upper approach','Nominal upper-bay approach only; the actual MQ6 module remains at its retained refrigeration-floor station'))
  boundaries[key]={'scope':'MQ6 header, actual lower exit and lower refrigeration harness remain outside the upper-bay rearrangement. This upper approach does not locate a header, claim a lower continuation or specify a new cold-core bore.'}
  job('J11-'+label,pins['J11'][label],key,'Controller to retained lower-cabinet MQ6 loom','J11',600)
 return {'ports':ports,'jobs':jobs,'boundaries':boundaries,'connectors':contracts,'pins':pins,'source_sha256':canonical['source_sha256'],
  'board_translation_mm':[board_delta_x,board_delta_y,board_delta_z],'board_translation_z_mm':board_delta_z}


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--only');parser.add_argument('--inventory-only',action='store_true');args=parser.parse_args()
 OUT.mkdir(parents=True,exist_ok=True);data=inventory();(HERE/'controls-interfaces.json').write_text(json.dumps(data,indent=2)+'\n')
 if args.inventory_only:print('controls interface inventory',len(data['jobs']),'routes',flush=True);return
 jobs=[j for j in data['jobs'] if not args.only or j['name'].startswith(args.only)]
 ports=data['ports'];used={j[e] for j in jobs for e in ['from','to']};guide=ControlsGuide([ports[k] for k in sorted(used)])
 result={**data,'parts':{},'control_routes':{},'replacement_names':[],'intended_contacts':[],'clearance_cutters':{},'failures':[],
 'basis':{'wire_diameter_mm':1.7,'nominal_awg':22,'geometric_radius_mm':3.4,'board_contact_to_free_plane_mm':11.65},
 'qualification_limits':['Exact canonical pin map and native purchased wafer geometry. XH mating housing/crimp insertion and11.65mm free-wire allowance are inherited reservations, not new physical acceptance.',
 'Nominal1.7mm wire exteriors are source stock dimensions; R3.4 bends and terminal approaches are geometric candidates, not qualified strain relief.',
 'Blade localX identities are exact; actual valve electrical polarity requires the diode markings and is not encoded in the calipered reference.',
 'Carbonator/probe service leads, meter pigtail, dry moisture comparator and fixed foreground donor contacts retain their explicitly named unlocated interfaces. No new cold-core hole is invented.',
 'Bare ribbons need the inherited manufacturing web-peel/clip/sleeve checks; native geometry does not qualify terminal retention, insulation, cooling, vibration or lifetime.']}
 for job in jobs:
  name='control-'+job['name'];a=ports[job['from']];b=ports[job['to']]
  try:shape,record=guide.route(a,b,name)
  except ValueError as e:
   result['failures'].append({'route':name,'reason':str(e)});print('CONTROL FAILURE',name,str(e),flush=True);continue
  p=OUT/(name+'.brep');shape.exportBrep(str(p));result['parts'][name]={'brep':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bounds':bounds(shape),'role':'wiring','color_role':'control','detail':job['topology']+';1.7mm occupied conductor and exact R3.4 arcs.'}
  record.update(job);record['contact_span_allowance_mm']=11.65 if job['from'].startswith('J') else 0
  if job.get('baseline_bench_cut_mm'):record['existing_bench_cut_reserve_mm']=job['baseline_bench_cut_mm']-record['length_mm']-record['contact_span_allowance_mm']
  result['control_routes'][job['name']]=record
  for end in [a,b]:
   if end['owner'] in guide.models:result['intended_contacts'].append([name,end['owner']])
  c,_=sweep(record['points_mm'],3.7);f=OUT/(name+'-clearance.brep');c.exportBrep(str(f));result['clearance_cutters'][name]={'brep':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
  result['pass']=not result['failures'];(HERE/'controls-candidate.json').write_text(json.dumps(result,indent=2)+'\n');guide.refresh()
 result['pass']=not result['failures'] and len(result['control_routes'])==len(jobs);result['source_sha256'][str(Path(__file__).relative_to(ROOT))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();(HERE/'controls-candidate.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'routes':len(result['control_routes']),'pass':result['pass'],'failures':result['failures']},indent=2),flush=True)
if __name__=='__main__':main()
