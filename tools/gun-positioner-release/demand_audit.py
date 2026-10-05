"""Check shared purchase coverage against the released assembly schedules.

Unknown consumed classes fail closed. This checks quantities and stock bins;
it does not establish the fit or capacity of received hardware.
"""
from pathlib import Path
from collections import Counter
import hashlib,json,datetime
root=Path(__file__).resolve().parents[2]
mech=root/'hardware/printed-parts/fixtures/gun-positioner'
source=root/'hardware/gun-positioner/sourcing/prime-verified.json'
cam=root/'hardware/printed-parts/fixtures/gun-positioner-observation/manifest.json'
files=[mech/'fasteners.json',mech/'hardware-counts.json',mech/'joint-allocations.json',mech/'gun_positioner.py',mech/'stock-nest.json',mech/'requirements.json',mech/'stock-profiles.json',cam,source,root/'hardware/gun-positioner/controller-purchase-requirements.json',root/'hardware/gun-positioner/mounting/manifest.json']
rows=json.loads((mech/'fasteners.json').read_text());h=json.loads((mech/'hardware-counts.json').read_text());c=json.loads(cam.read_text());stock={r['id']:r for r in json.loads(source.read_text())['rows']}
profiles=json.loads((mech/'stock-profiles.json').read_text())
counts={'bolts':Counter(),'nuts':Counter(),'flat_washers':Counter()}
unknown=[]
known_tapped={'force gauge M4 tapped socket','motor M3 tapped thread','purchased M5 tapped block','shaft M5 tapped thread','shaft M5 tapped end','M5 tapped shaft end'}
reused=[]
for r in rows:
 q=r['quantity'];n=r['nut_or_thread'];b=r['fastener']
 if n.startswith('reuse') or r.get('reuse_from'):
  reused.append({'joint':r['joint'],'quantity':q,'fastener':b,'reuse_from':r.get('reuse_from',n)})
  continue
 counts['bolts'][b]+=q;counts['flat_washers'][b.split('x')[0]]+=q*r['flat_washers_per_fastener']
 direct={x:x for x in ['M3 locking nut','M4 locking nut','M5 locking nut','M6 locking nut','M8 locking nut']}
 direct.update({'slot8 M8 T-nut':'M8 slot8 T-nut','slot8 M6 T-nut':'M6 slot8 T-nut','steel M6x1 coupling nut':'M6x1 coupling nut'})
 nut_known=n in direct or n in known_tapped
 if n in direct:counts['nuts'][direct[n]]+=q
 for prefix,factor in [('two M3 nuts',2),('two M5 nuts',2),('two M6 nuts',2),('three M6 nuts',3)]:
  if n.startswith(prefix):counts['nuts'][prefix.split()[1]+' nut']+=q*factor;nut_known=True
 if not nut_known:unknown.append({'source':'mechanical schedule','class':'nut_or_thread','name':n,'row':r})
schedule_diff={cat:{key:[computed[key],h[cat].get(key,0)] for key in set(computed)|set(h[cat]) if computed[key]!=h[cat].get(key,0)} for cat,computed in counts.items()}
b=counts['bolts'].copy();n=counts['nuts'].copy();w=counts['flat_washers'].copy()
cm={'M3x20 socket bolt':('bolts','M3x20'),'M5x16 socket bolt':('bolts','M5x16'),'M5x25 socket bolt':('bolts','M5x25'),'M5x40 socket bolt':('bolts','M5x40'),'M5x70 socket bolt':('bolts','M5x70'),'M8x100 threaded stud':('bolts','M8x100'),'M8x16 socket bolt':('bolts','M8x16'),'M8x75 through bolt':('bolts','M8x75'),'M3 hex nut':('nuts','M3 nut'),'M5 nylock nut':('nuts','M5 locking nut'),'M8 nut':('nuts','M8 nut'),'M8 slot8 T-nut':('nuts','M8 slot8 T-nut'),'M3 washer':('flat_washers','M3'),'M5 washer':('flat_washers','M5'),'M8 washer':('flat_washers','M8')}
combined={'bolts':b,'nuts':n,'flat_washers':w}
camera_special=Counter()
known_camera_special={'40mm steel spacer, ID6 OD12','40-series metal corner bracket','1/4-20x1/2inch tripod screw','1/4inch washer'}
for r in c['fasteners']:
 if r['part'] in cm:
  cat,name=cm[r['part']];combined[cat][name]+=r['quantity']
 elif r['part'] in known_camera_special:
  camera_special[r['part']]+=r['quantity']
 else:unknown.append({'source':'camera fasteners','class':'unmapped consumption','name':r['part'],'row':r})
for name,q in {'M3x25':36,'M4x50 grade12.9':4,'M6x16':4}.items():b[name]+=q
for name,q in {'M3 locking nut':36,'M4 locking nut':4,'M6 slot8 T-nut':4}.items():n[name]+=q
for name,q in {'M3':72,'M4':8,'M6':4}.items():w[name]+=q
m3large=sum(r['quantity'] for r in h['large_M3_washer_requirements'].values() if isinstance(r,dict));m4large=sum(data['quantity'] for name,data in h.items() if name.startswith('large_M4_') and isinstance(data,dict))
entries=[]
def cover(name,required,ids,provided=0,note=''):
 for id in ids:
  if id not in stock:unknown.append({'source':'stock mapping','class':'missing purchase row','name':id,'demand':name})
 cap=provided+sum(stock[i]['pack']*stock[i]['packs'] for i in ids if i in stock)
 entries.append({'demand':name,'quantity':required,'stock_ids':ids,'ordered_capacity':cap-provided,'included_or_owned_capacity':provided,'total_capacity':cap,'shortage':max(0,required-cap),'note':note})
def stock_id_for_asin(asin):
 matches=[id for id,row in stock.items() if row.get('asin')==asin]
 if len(matches)!=1:
  unknown.append({'source':'stock mapping','class':'missing or ambiguous verified ASIN','name':asin,'matches':matches})
  return '__unresolved_ASIN_'+asin
 return matches[0]
bolt_ids={'M3x20':'m3x20','M3x25':'m3x25','M3x30':'m3x30','M3x40':'m3x40','M3x100':'m3x100','M3x12':'m3x12','M3x14':'m3x14','M3x50':'retention-guide-m3x50','M4x25 finish-to-depth':'m4x25','M4x30':'m4x30','M4x35':'m4x35','M4x50 grade12.9':'m4x50-12.9','M5x12':'m5x12','M5x16':'m5x16','M5x20':'m5x20','M5x25':'m5x25','M5x25 countersunk':'crash-cup-screw','M5x35':'m5x35','M5x40':'m5x40','M5x45':'m5x45','M5x70':'m5x70','M5x80':'m5x80','M5x90':'m5x90','M6x16':'m6x16','M6x25':'m6x25','M6x30':'m6x30','M6x40 grade8.8':'m6x40-12.9','M6x40 grade12.9':'m6x40-12.9','M8x50 partly threaded grade8.8':'m8x50-half-thread','M8x75':'m8x75','M8x90 partly threaded grade8.8':'link-guide-bolt','M8x100':'m8x100-stud'}
for name,q in b.items():
 if name in bolt_ids:cover(name,q,[bolt_ids[name]],note='The four normal backing screws are shared between the normal gauge backings; the proof backing has a separate four-screw set finished for its deeper grip. Included screws may replace only the measured compatible normal set.' if name.startswith('M4x25') else '')
 elif name not in {'M6x80','M6x80 finished72.5','M8x16'}:unknown.append({'source':'combined demand','class':'bolt','name':name,'quantity':q})
cover('M6x80 stock,12finished72.5 plus1uncut',b['M6x80']+b['M6x80 finished72.5'],['retention-post'])
kits=stock['corner-bracket']['pack']*stock['corner-bracket']['packs']
cover('M8x16 bolts',b['M8x16'],[],provided=2*kits,note='Included in corner-bracket kits.')
nut_ids={'M3 locking nut':'m3-locknut','M4 locking nut':'m4-nylock','M5 locking nut':'m5-locknut','M6 locking nut':'m6-locknut','M8 locking nut':'m8-locknut','M3 nut':'m3-nut','M5 nut':'m5-nut','M6 nut':'retention-m6-nut','M8 nut':'m8-nut','M6 slot8 T-nut':'tnut-m6-slot8','M6x1 coupling nut':stock_id_for_asin('B0DHGXW6G9')}
for name,q in n.items():
 if name in nut_ids:cover(name,q,[nut_ids[name]])
 elif name!='M8 slot8 T-nut':unknown.append({'source':'combined demand','class':'nut','name':name,'quantity':q})
cover('M8 slot8 T-nut',n['M8 slot8 T-nut'],['m8-tnut-slot8'] if 'm8-tnut-slot8' in stock else [],provided=2*kits,note='Included corner-bracket kit T-nuts are allocated once to the full mechanical, proof fixture and camera demand; separate pack not required when the received contents match the purchase row.')
cover('ordinary M3 washers',w['M3']-m3large,['m3-washer'],provided=64,note='64 camera washers are the explicitly allocated owned stock; large washers counted separately.')
cover('large M3 washers',m3large,['m3-washer-large'])
cover('ordinary M4 washers',w['M4']-m4large,['m4-washer'])
cover('large M4 washers',m4large,['m4-washer-large'])
cover('M5 washers',w['M5'],['m5-washer']);cover('M6 washers',w['M6'],['m6-washer']);cover('M8 washers',w['M8'],['m8-washer'],provided=2*kits,note='Includes80 mechanical kit washers and8 camera kit washers; spare pack capacity is sufficient either way.')
for name,q in w.items():
 if name not in {'M3','M4','M5','M6','M8'}:unknown.append({'source':'combined demand','class':'washer','name':name,'quantity':q})
other_washer_ids={'M10_ID10.5_OD20_x2mm':'m10-washer','M8_ID8.5_OD32_x1.5mm':'link-fender-washer','M12_ID13_OD37_x3mm':'friction-washer-m12x37','M6_ID6_OD25_x2mm_carbon_steel':'crash-striker','M6_ID6_OD20_x2mm_304_shaft_end':stock_id_for_asin('B0DYK1PVYB')}
for name,q in h.get('other_washers',{}).items():
 if name in other_washer_ids:cover(name,q,[other_washer_ids[name]])
 else:unknown.append({'source':'other_washers','class':'washer','name':name,'quantity':q})
tube_ids={'8':'tube-8x6','10':'tube-10x8','20':'tube-20x12'}
for size,data in profiles.get('tube_stock',{}).items():
 if size not in tube_ids:
  unknown.append({'source':'stock profiles','class':'tube','name':size,'data':data})
  continue
 sticks=data.get('sticks_needed',data.get('sticks_used'))
 if sticks is None:
  unknown.append({'source':'stock profiles','class':'missing tube stick demand','name':size,'data':data})
  continue
 cover('tube OD'+size+' stock sticks',sticks,[tube_ids[size]],note='Finished cuts and saw kerf are included in the source stock-profile bin allocation; received stock and final facing remain physical fitting checks.')
 for layout in data.get('layouts',data.get('bins',[])):
  if layout['used_mm']>data['stock_length_mm']+1e-6:unknown.append({'source':'stock profiles','class':'invalid tube bin','name':size,'layout':layout})
cover('4040 metal corner brackets',h['corner_brackets_4040']+camera_special['40-series metal corner bracket'],['corner-bracket'])
cover('1inch angle finished25.4mm slices',h['metal_angle_slices'],['angle-1x1x0.125'],note='Each304.8mmstick gives10 finished25.4mmslices with3mmkerf; ordered16sticks yield160 slices.')
entries[-1]['ordered_capacity']=stock['angle-1x1x0.125']['pack']*stock['angle-1x1x0.125']['packs']*10;entries[-1]['total_capacity']=entries[-1]['ordered_capacity'];entries[-1]['shortage']=max(0,h['metal_angle_slices']-entries[-1]['total_capacity'])
for name,q,id in [('camera40mmmetalspacers',camera_special['40mm steel spacer, ID6 OD12'],'spacer-40'),('cameraquarter20screws',camera_special['1/4-20x1/2inch tripod screw'],'5a-screws'),('cameraquarterwashers',camera_special['1/4inch washer'],'5b-washers'),('drivers',6,'drivers'),('eightpinfemalesockets',12,'driver_carriers__female_headers'),('GX16-4 connector pairs',7,'motor_connectors'),('GX12-2 connector pairs',8,'switch_connectors'),('microswitches',28,'limit_switches'),('driverfan',1,'driver-fan'),('driverfanguards',2,'driver-fan-guard'),('UART1k8pullups',2,'uart-pullup-1k8'),('UART330series',2,'uart-series-330'),('500mAfuses',3,'fuse_distribution__fuses_500mA'),('1Afuses',6,'fuse_distribution__fuses_1A'),('5Afuses',1,'fuse_distribution__fuses_5A'),('100uFcapacitors',6,'capacitors'),('470uFcapacitor',1,'capacitors__470uF')]:cover(name,q,[id])
for name,q,id in [('M5 spiral-flute tap',1,'tap-m5'),('M3-M8 tap wrench',1,'tap-wrench'),('25in-lb clockwise cam-over driver',1,'torque-screwdriver'),('metric H3 bit set',1,'hex-bits-metric')]:cover(name,q,[id])
shared_stock={}
for entry in entries:
 if len(entry['stock_ids'])==1:
  shared_stock.setdefault(entry['stock_ids'][0],[]).append(entry)
shared_usage=[]
for id,group in shared_stock.items():
 if len(group)<2:continue
 demand=sum(max(0,e['quantity']-e['included_or_owned_capacity']) for e in group)
 capacities={e['ordered_capacity'] for e in group}
 if len(capacities)!=1:
  unknown.append({'source':'shared stock','class':'incompatible unit allocation','name':id,'entries':group})
 capacity=min(capacities)
 shared_usage.append({'stock_id':id,'classes':[e['demand'] for e in group],'combined_quantity':demand,'capacity':capacity,'shortage':max(0,demand-capacity)})
result={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'audit_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Independent final mechanical joint demand plus both camera stages and quantified controller mounts. Numeric coverage only; received fit/material and physical tests unqualified. Unknown consumed bolt, nut, washer and camera classes fail the audit.','source_sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'mechanical_joint_rows':len(rows),'schedule_vs_hardware_counts':schedule_diff,'combined_consumption':{k:dict(v) for k,v in combined.items()},'unknown_consumption_classes':unknown,'reused_allocations_excluded_from_new_demand':reused,'shared_stock_allocations':shared_usage,'separate_large_washer_subsets':{'M3':m3large,'M4':m4large},'coverage':entries,'shortages':[e for e in entries if e['shortage']]+[e for e in shared_usage if e['shortage']],'text_quantity_mismatches':[] if stock['driver-fan-guard']['need']==2 else ['driver-fan-guard consumption differs from physical assembly2; six-pack capacity covers both.'],'stock_notes':['M8 slot8 T-nuts come from the included corner-bracket kits; no separate pack is required when their measured contents match the purchase row.']}
result['audit_script']='tools/gun-positioner-release/demand_audit.py'
out=root/'hardware/gun-positioner/sourcing/final-demand-audit.json';out.write_text(json.dumps(result,indent=2)+'\n')
print(out);print('joint-count diffs',schedule_diff,'classes',len(entries),'shortages',result['shortages']);print('combined bolts',dict(b));print('combined nuts',dict(n));print('combined washers',dict(w))
if unknown or result['shortages'] or any(schedule_diff.values()) or result['text_quantity_mismatches']:
 print('AUDIT FAILED',unknown)
 raise SystemExit(1)
