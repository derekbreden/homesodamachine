"""Derive non-sheet stock cuts from the governing fabrication registry."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/printed-parts/fixtures/gun-positioner'
src=OUT/'gun_positioner.py'
spec=importlib.util.spec_from_file_location('gun_positioner_profiles',src)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.init_parts()
KERF=3.0
tubes=[]
for name,d in m.PARTS.items():
    if d['kind']!='metal' or d.get('template_type')!='tube':continue
    od,_,length=d['blank_mm']
    bore=math.sqrt(max(0,od*od-4*d['model'].val().Volume()/(math.pi*length)))
    tubes.append(dict(part=name,quantity=d['quantity'],outer_diameter_mm=od,
                      finished_ID_mm=round(bore,3),finished_length_mm=length,notes=d['notes']))
stocks={}
for od,stock_length,stock_id in [(8,400,6),(10,250,8),(20,300,12)]:
    selected=[d for d in tubes if d['outer_diameter_mm']==od]
    cuts=[dict(part=d['part'],instance=i+1,length_mm=d['finished_length_mm']) for d in selected for i in range(d['quantity'])]
    bins=[]
    for c in sorted(cuts,key=lambda c:-c['length_mm']):
        cost=c['length_mm']+KERF
        options=[(stock_length-b['used_mm']-cost,i) for i,b in enumerate(bins) if b['used_mm']+cost<=stock_length]
        if options:_,i=min(options)
        else:i=len(bins);bins.append(dict(used_mm=0,cuts=[]))
        bins[i]['cuts'].append(c);bins[i]['used_mm']+=cost
    for i,b in enumerate(bins):b.update(stick=i+1,offcut_mm=stock_length-b['used_mm'])
    stocks[str(od)]=dict(stock_OD_mm=od,stock_ID_mm=stock_id,stock_length_mm=stock_length,
                         kerf_mm=KERF,pieces=len(cuts),finished_length_mm=sum(c['length_mm'] for c in cuts),
                         sticks_needed=len(bins),two_packs_to_buy=math.ceil(len(bins)/2),
                         sticks_supplied=2*math.ceil(len(bins)/2),layouts=bins)
record=dict(source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),tube_parts=tubes,tube_stock=stocks,
            angle_slices=[dict(profile_mm=[25.4,25.4,3.175],cut_length_mm=25.4,quantity=149),
                          dict(profile_mm=[50.8,50.8,6.35],cut_length_mm=40,quantity=7,
                               fits_spare_304p8mm_stick_with_3mm_kerf=True,used_length_mm=301),
                          dict(profile_mm=[50.8,50.8,6.35],cut_length_mm=70,quantity=1,
                               separate_stock_required=True,purpose='proof-gauge-quill-cap')],
            square_bar_cuts=[dict(size_mm=[38.1,38.1,25],quantity=7),dict(size_mm=[25.4,25.4,7.35],quantity=28),dict(size_mm=[25.4,25.4,15],quantity=4)],
            shaft_stock=dict(diameter_mm=12,material='304 stainless',sticks_mm=[356,356],kerf_mm=3,
                             layouts=[[175,165],[130,85]],no_transverse_holes=True,
                             end_threads='M5x0.8 at all eight ends',usable_thread_mm=10,pilot_mm=[4.2,16]),
            screw_stock=dict(quantity=8,stock_length_mm=400,finished_main_lengths_mm=[400,400,400,300,300,300],test_spare_length_mm=200),
            ground_rods=dict(diameter_mm=8,length_mm=100,quantity=4,cutting='uncut purchased hardened stock'),
            scope='Nominal finished cuts. Grade delivered bores, faces and spring rates before finishing precision spacer lengths. Kerf is charged for every separated piece, including its final cut; listed offcuts are trim reserve.')
(OUT/'stock-profiles.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:{n:v[n] for n in ('pieces','finished_length_mm','sticks_needed','sticks_supplied')} for k,v in stocks.items()},indent=2))
