"""Kerf-aware shared flat-sheet and 4040 stock nest, including camera plates."""
import importlib.util
import json
import math
import random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/printed-parts/fixtures/gun-positioner'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.init_parts();return m
mechanics=module('gun_positioner',OUT/'gun_positioner.py')
optics=module('positioner_optics',ROOT/'tools/gun-positioner-optics/mounts.py')
KERF=3.0;EDGE=1.0
TYPES={
 '12x18':dict(width_mm=304.8,height_mm=457.2,pack_quantity=2,pack_price_usd=81.99,asin='B0GZTCFFPF'),
 '12x16':dict(width_mm=304.8,height_mm=406.4,pack_quantity=1,pack_price_usd=30.99,asin='B0CG5FXWT5'),
 '12x12':dict(width_mm=304.8,height_mm=304.8,pack_quantity=2,pack_price_usd=36.59,asin='B09WDQTKZ7'),
}
items=[]
for registry,prefix in ((mechanics.PARTS,''),(optics.PARTS,'optics-')):
 for name,d in registry.items():
  if d['kind']!='metal' or not d.get('blank_mm') or d['blank_mm'][2]!=6.35 or d.get('stock_profile'):continue
  if prefix=='' and d.get('template_type')!='plate':continue
  for i in range(d['quantity']):
   x,y,t=d['blank_mm'];items.append(dict(part=prefix+name,instance=i+1,x=x,y=y,t=t))
def new_sheet(kind):
 d=TYPES[kind];return dict(stock_type=kind,free=[(EDGE,EDGE,d['width_mm']-2*EDGE+KERF,d['height_mm']-2*EDGE+KERF)],cuts=[])
def place_options(sheet,item):
 for fi,(fx,fy,fw,fh) in enumerate(sheet['free']):
  for rotated in (False,True):
   x,y=(item['y'],item['x']) if rotated else (item['x'],item['y'])
   if x+KERF<=fw+1e-8 and y+KERF<=fh+1e-8:
    for split in ('vertical','horizontal'):
     rem1=(fw-x-KERF)*fh if split=='vertical' else fw*(fh-y-KERF)
     rem2=(x+KERF)*(fh-y-KERF) if split=='vertical' else (fw-x-KERF)*(y+KERF)
     # Avoid slender lost strips; keep one useful large remainder.
     score=fw*fh-x*y+.15*min(max(rem1,0),max(rem2,0))
     yield(score,fi,rotated,x,y,split)
def insert(sheet,item,option):
 _,fi,rotated,x,y,split=option;fx,fy,fw,fh=sheet['free'].pop(fi)
 if split=='vertical':
  if fw-x-KERF>0:sheet['free'].append((fx+x+KERF,fy,fw-x-KERF,fh))
  if fh-y-KERF>0:sheet['free'].append((fx,fy+y+KERF,x+KERF,fh-y-KERF))
 else:
  if fh-y-KERF>0:sheet['free'].append((fx,fy+y+KERF,fw,fh-y-KERF))
  if fw-x-KERF>0:sheet['free'].append((fx+x+KERF,fy,fw-x-KERF,y+KERF))
 sheet['cuts'].append({**item,'stock_x_mm':fx,'stock_y_mm':fy,'cut_width_mm':x,'cut_height_mm':y,'rotated90':rotated,'guillotine_first':split})
def purchase_cost(sheets):
 counts={k:sum(s['stock_type']==k for s in sheets) for k in TYPES}
 return sum(math.ceil(counts[k]/d['pack_quantity'])*d['pack_price_usd'] for k,d in TYPES.items())
def layout(order):
 # Three 450 mm beds require the long stock; its fourth sheet is available
 # from the two purchased packs and is fully included before other sheets.
 sheets=[new_sheet('12x18') for _ in range(4)]
 for item in order:
  candidates=[(o[0],si,o) for si,s in enumerate(sheets) for o in place_options(s,item)]
  if candidates:
   _,si,o=min(candidates);insert(sheets[si],item,o);continue
  choices=[]
  for kind in ('12x12','12x16'):
   s=new_sheet(kind);opts=list(place_options(s,item))
   if opts:
    incremental=TYPES[kind]['pack_price_usd']/TYPES[kind]['pack_quantity']
    choices.append((incremental,TYPES[kind]['width_mm']*TYPES[kind]['height_mm'],kind,min(opts)))
  if not choices:raise RuntimeError(f'Blank cannot fit available Prime stock: {item}')
  _,_,kind,o=min(choices);s=new_sheet(kind);insert(s,item,o);sheets.append(s)
 return sheets
large=[i for i in items if max(i['x'],i['y'])>406.4-2*EDGE]
rest=[i for i in items if i not in large]
rng=random.Random(5124)
orders=[]
reserved=[i for i in rest if i['part']=='rotator-platform']
camera=[i for i in rest if i['part']=='optics-camera-fixed-plate']
remaining=[i for i in rest if i not in reserved and i not in camera]
for key in (lambda i:i['x']*i['y'],lambda i:max(i['x'],i['y']),lambda i:min(i['x'],i['y'])):
 orders.append(large+reserved+camera+sorted(remaining,key=key,reverse=True))
for key in (lambda i:i['x']*i['y'],lambda i:max(i['x'],i['y']),lambda i:min(i['x'],i['y'])):
 orders.append(sorted(large,key=key,reverse=True)+sorted(rest,key=key,reverse=True))
for _ in range(160):
 orders.append(large+sorted(rest,key=lambda i:-(i['x']*i['y'])*(0.7+0.6*rng.random())))
result=min((layout(o) for o in orders),key=lambda s:(purchase_cost(s),len(s)))
counts={k:sum(s['stock_type']==k for s in result) for k in TYPES}
# Ordered first-fit backtracking gives exact stick contents and separate cuts.
extrusion=[('station-long',750,2),('station-cross',460,6),('z-mast',600,2),('z-head',225,1),('z-head-cross',180,1),('fiber-post',900,1),('fiber-arm',750,1),('camera-riser',300,4),('installed-Z-test-column',500,1)]
pieces=[dict(part=n,instance=i+1,length_mm=l) for n,l,q in extrusion for i in range(q)]
pieces.sort(key=lambda p:-p['length_mm'])
bins=[[] for _ in range(8)];used=[0.0]*8
def solve(i):
 if i==len(pieces):return True
 p=pieces[i];seen=set()
 for b in range(8):
  if used[b] in seen:continue
  seen.add(used[b]);extra=p['length_mm']+(KERF if bins[b] else 0)
  if used[b]+extra<=1220:
   bins[b].append(p);used[b]+=extra
   if solve(i+1):return True
   used[b]-=extra;bins[b].pop()
 return False
if not solve(0):raise RuntimeError('4040 stock does not fit eight 1220 mm sticks')
record=dict(kerf_mm=KERF,edge_allowance_mm=EDGE,
 flat_sheet_purchases={k:{**TYPES[k],'sheets_used':counts[k],'packs_to_buy':math.ceil(counts[k]/TYPES[k]['pack_quantity']),'sheets_supplied':math.ceil(counts[k]/TYPES[k]['pack_quantity'])*TYPES[k]['pack_quantity']} for k in TYPES},
 flat_sheet_total_usd=round(purchase_cost(result),2),total_part_blank_area_mm2=sum(i['x']*i['y'] for i in items),
 slices=[dict(sheet=i+1,stock_type=s['stock_type'],stock_mm=[TYPES[s['stock_type']]['width_mm'],TYPES[s['stock_type']]['height_mm'],6.35],cuts=s['cuts']) for i,s in enumerate(result)],
 extrusion_4040=dict(stock_length_mm=1220,sticks=8,packs_of_four=2,asin='B0BZRL4VTJ',finished_length_mm=sum(p['length_mm'] for p in pieces),layouts=[dict(stick=i+1,cuts=b,used_including_kerf_mm=used[i],offcut_mm=1220-used[i]) for i,b in enumerate(bins)]),
 notes=['Shared purchase nest includes both camera flat plates and all mechanism flat blanks. Tube spacers, square bars and formed angles are separate stock profiles, never flat-sheet substitutes.','Three millimetre saw kerf is allowed between independent blanks and extrusion cuts. Sheet edge allowance is one millimetre. Factory extrusion ends are accepted only after square-end inspection; listed offcuts are the available trim reserve.','Use the purchased nonferrous jigsaw blade for wide sheet. The bench band saw cannot accept 199-300 mm sheet width. Measure and deburr blanks; nominal size tolerance +/-0.5 mm and registered hole centers +/-0.25 mm, with catalog patterns transfer-drilled.'])
(OUT/'templates').mkdir(exist_ok=True)
for old in (OUT/'templates').glob('stock-sheet-*.svg'):old.unlink()
for old in (OUT/'templates').glob('stock-sheet-*.dxf'):old.unlink()
for s in record['slices']:
 W,H,_=s['stock_mm'];svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">','<rect width="100%" height="100%" fill="white"/>']
 for c in s['cuts']:
  x,y,w,h=[c[k] for k in ('stock_x_mm','stock_y_mm','cut_width_mm','cut_height_mm')]
  svg.extend([f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#e0e5e8" stroke="black" stroke-width=".25"/>',f'<text x="{x+1}" y="{y+4}" font-family="sans-serif" font-size="2.5">{c["part"]} #{c["instance"]}</text>',f'<text x="{x+1}" y="{y+8}" font-family="sans-serif" font-size="2.5">{w} x {h} mm</text>'])
 svg.append('</svg>');(OUT/'templates'/f'stock-sheet-{s["sheet"]:02}.svg').write_text('\n'.join(svg))
# Millimetre DXFs preserve the same kerf-aware stock blank layout.
import ezdxf
for sl in record['slices']:
    doc=ezdxf.new('R2010');doc.units=4;ms=doc.modelspace();W,H,_=sl['stock_mm']
    ms.add_lwpolyline([(0,0),(W,0),(W,H),(0,H)],close=True)
    for c in sl['cuts']:
        x,y,w,h=[c[k] for k in('stock_x_mm','stock_y_mm','cut_width_mm','cut_height_mm')]
        ms.add_lwpolyline([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],close=True)
        ms.add_text(f"{c['part']} #{c['instance']}",dxfattribs={'height':2.5,'insert':(x+1,y+4)})
    doc.saveas(OUT/'templates'/f"stock-sheet-{sl['sheet']:02}.dxf")
(OUT/'stock-nest.json').write_text(json.dumps(record,indent=2)+'\n')
(OUT/'metal-blanks.json').write_text(json.dumps(items,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k!='slices'},indent=2))
