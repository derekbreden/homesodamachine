"""Manual native bead review and print-only packaging for the foot experiment."""
from collections import defaultdict
from pathlib import Path
import hashlib
import json
import math
import re
import sys
from zipfile import ZipFile

import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/bambu_print.py').exists())
sys.path[:0]=[str(ROOT/'hardware/print-tests/petgf-fins'),str(ROOT/'tools')]
# Avoid importing this file as the shared module with the same name.
import importlib.util
spec=importlib.util.spec_from_file_location('fin_paths',ROOT/'hardware/print-tests/petgf-fins/review.py')
shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared)
from bambu_print_archive import package

def save(p,d): p.write_text(json.dumps(d,indent=2)+'\n')

def review_stock():
    folder=HERE/'stock-vs-tree/mark2'
    if (folder/'launch.json').exists(): raise ValueError('Preserve submitted artifacts')
    prep=json.loads((folder/'preparation.json').read_text())
    engine=json.loads((HERE/'stock-engine.json').read_text())
    assert engine['local_changes'] is False
    assert all(r['tines']==0 and r['fin_count']==8 for r in engine['candidates'])
    source=ROOT/str(Path(prep['project']).with_suffix('.gcode.3mf'))
    with ZipFile(source) as z:
        raw=z.read('Metadata/plate_1.gcode')
        assert hashlib.md5(raw).hexdigest()==z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
    text=raw.decode();paths=shared.segments(text)
    lo=np.full(2,np.inf);hi=-lo
    for p in paths:
        xy=np.array([p['a'][:2],p['b'][:2]])
        lo=np.minimum(lo,xy.min(0)-p['width']/2-.02)
        hi=np.maximum(hi,xy.max(0)+p['width']/2+.02)
    usable=np.array(prep['shared_printable_area_mm'])
    inset=float(min(*(lo-usable[0]),*(usable[1]-hi)))
    assert inset>=80,inset
    trims=[float(v) for v in re.findall(r'^\s*G29\.1 Z([-+.\d]+)',text,re.M)]
    assert trims==[0,.02],trims
    assert not re.search(r'^\s*G39(?:\s|$)',text,re.M)
    rows=[]
    for r in prep['specimens']:
        own=[p for p in paths if p['object']==r['identify_id']]
        features=defaultdict(int)
        for p in own: features[p['feature']]+=1
        rows.append(dict(**r,features_sampled_segments=dict(features),
            model_and_support_z_range_mm=[min(p['z'] for p in own),max(p['z'] for p in own)]))
    assert rows[0]['walls']==8 and rows[1]['walls']==0
    assert rows[0]['blocked_model_faces']==965 and rows[1]['blocked_model_faces']==0
    assert rows[1]['features_sampled_segments'].get('Support interface',0)>0
    report=dict(gcode_sha256=hashlib.sha256(raw).hexdigest(),gcode_edits=False,
        full_bead_bounds_mm=[lo.tolist(),hi.tolist()],minimum_bed_edge_clearance_mm=inset,
        emitted_trim_mm=trims,native_layer_count=len({p['z'] for p in paths}),specimens=rows,
        support_gap='Stock fins request .24 mm; B retains production auto support gap .45. Native beads do not establish physical release or a uniform empty course everywhere.',
        physical_result='Pending: full-circumference rim, mounting-plate fit and support removal remain unqualified.')
    save(folder/'review.json',report)
    output=source.with_name(source.stem.replace('.gcode','')+'-print-only.gcode.3mf')
    save(folder/'packaging.json',package(source,output))
    print(json.dumps(report),flush=True)

def main():
    if len(sys.argv)>1 and sys.argv[1]=='stock': return review_stock()
    folder=HERE/'mark2'
    if (folder/'launch.json').exists(): raise ValueError('Preserve submitted artifacts')
    prep=json.loads((folder/'preparation.json').read_text())
    engine=json.loads((HERE/'engine.json').read_text())['candidates'][0]
    source=ROOT/str(Path(prep['project']).with_suffix('.gcode.3mf'))
    with ZipFile(source) as z:
        raw=z.read('Metadata/plate_1.gcode')
        assert hashlib.md5(raw).hexdigest()==z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
    text=raw.decode();lines=text.splitlines()
    paths=shared.segments(text)
    grouped=defaultdict(list)
    previous=None;run=0
    for p in paths:
        split=previous is None or p['object']!=previous['object'] or p['z']!=previous['z'] or np.linalg.norm(p['a']-previous['b'])>.02
        if not split and p['line']>previous['line']+1:
            between=lines[previous['line']:p['line']-1]
            split=any(re.match(r'G[01]\b',l) and (re.search(r'\bE-',l) or (re.search(r'\b[XY]',l) and not re.search(r'\bE',l))) for l in between)
        if split: run+=1
        p['run']=run
        grouped[p['object'],round(p['z'],5)].append(p)
        previous=p
    usable=np.array(prep['shared_printable_area_mm'])
    lo=np.full(2,np.inf);hi=-lo
    for p in paths:
        xy=np.array([p['a'][:2],p['b'][:2]])
        lo=np.minimum(lo,xy.min(0)-p['width']/2-.02)
        hi=np.maximum(hi,xy.max(0)+p['width']/2+.02)
    inset=float(min(*(lo-usable[0]),*(usable[1]-hi)))
    assert inset>=80,inset
    trims=[float(v) for v in re.findall(r'^\s*G29\.1 Z([-+.\d]+)',text,re.M)]
    assert trims==[0,.02],trims
    assert not re.search(r'^\s*G39(?:\s|$)',text,re.M)
    observed_heights=sorted({round(p['height'],3) for p in paths})
    rows=[];plot_data=[]
    a=math.radians(-15);c=math.cos(a);s=math.sin(a)
    rot=np.array([[1,0,0],[0,c,-s],[0,s,c]])
    centers=[]
    for r in prep['parts']:
        centers.append(np.array(r['plate_translation_mm'])-rot@np.array(r['source_center_mm'])-
            np.array([engine['offset'][k] for k in 'xyz']))
    zs=sorted({round(p['z'],5) for p in paths})
    for i,t in enumerate(engine['retained_tines'],1):
        layer=next(z for z in zs if t['bottom']<z-.12<t['top'])
        sample=layer-.12
        f=(sample-t['bottom'])/.24
        end=np.array(t['ends']['bot'])*(1-f)+np.array(t['ends']['top'])*f
        along=np.array([t['biteX'],t['biteY']]);across=np.array([-along[1],along[0]])
        seed=np.array([t['x'],t['y']])+centers[0][:2]
        poly=Polygon([seed-.3*along-.25*across,seed+end[0]*along-.25*across,
            seed+end[1]*along+.25*across,seed-.3*along+.25*across])
        root=seed-.20*along
        # Stay inside the nominal tine's tip by 0.05 mm.
        tip=seed+(float(end.mean())-.05)*along
        nearby=defaultdict(list)
        for p in grouped[1901,layer]:
            line=LineString([p['a'][:2],p['b'][:2]])
            if line.distance(Point(seed))<1.8:
                nearby[p['run']].append(p)
        scored=[]
        for rid,pp in nearby.items():
            foot=unary_union([LineString([p['a'][:2],p['b'][:2]]).buffer(p['width']/2,quad_segs=8) for p in pp])
            scored.append((foot.intersection(poly).area/poly.area,
                foot.covers(Point(root)) and foot.covers(Point(tip)),rid,pp,foot))
        best=max(scored,key=lambda q:q[0])
        bseed=np.array([t['x'],t['y']])+centers[1][:2]
        b_hits=[]
        for z in zs:
            if abs(z-layer)>.72: continue
            if any(LineString([p['a'][:2],p['b'][:2]]).distance(Point(bseed))<p['width']/2 for p in grouped[1902,z]):
                b_hits.append(z)
        rows.append(dict(contact=i,nominal_bottom_z_mm=t['bottom'],nominal_top_z_mm=t['top'],
            slicer_midplane_z_mm=sample,one_geometric_slice_layer=True,emitted_nozzle_z_mm=layer,
            same_continuous_bead_covers_root_and_tip=bool(best[1]),
            tine_section_fraction_covered_by_best_run=round(best[0],4),
            native_run_id=best[2],native_gcode_lines=sorted({p['line'] for p in best[3]}),
            B_stock_wall_point_nearby_occupied_nozzle_z_mm=b_hits,
            B_point_empty_on_tine_layer=layer not in b_hits))
        plot_data.append((t,seed,poly,best,layer))
    summary=dict(gcode_sha256=hashlib.sha256(raw).hexdigest(),gcode_edits=False,
        native_layer_count=len(zs),all_feature_bead_heights_mm=observed_heights,emitted_trim_mm=trims,
        full_bead_bounds_mm=[lo.tolist(),hi.tolist()],minimum_bed_edge_clearance_mm=inset,
        designed_contacts=len(rows),single_layer_geometry_contacts=len(rows),
        continuous_root_to_tip_contacts=sum(r['same_continuous_bead_covers_root_and_tip'] for r in rows),
        stock_point_empty_on_tine_layer=sum(r['B_point_empty_on_tine_layer'] for r in rows),
        physical_contact_strength_and_removal='Unmeasured; native continuity is not physical grip or release evidence.',contacts=rows)
    save(folder/'review.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='contacts'}),flush=True)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,3,figsize=(12,8),constrained_layout=True)
    for ax,data in zip(axes.flat,[plot_data[k] for k in [0,4,8,13,18,25]]):
        t,seed,poly,best,layer=data
        for p in grouped[1901,layer]:
            line=LineString([p['a'][:2],p['b'][:2]])
            if line.distance(Point(seed))<2:
                ax.plot([p['a'][0]-seed[0],p['b'][0]-seed[0]],[p['a'][1]-seed[1],p['b'][1]-seed[1]],color='#2464a0',lw=2)
        xx,yy=poly.exterior.xy
        ax.plot(np.array(xx)-seed[0],np.array(yy)-seed[1],color='#e18422',lw=1.5)
        ax.set(xlim=(-1,1),ylim=(-1,1.5),aspect='equal',title=f"Contact {plot_data.index(data)+1}, nozzle Z{layer:.2f} mm",xlabel='Across wall (mm)',ylabel='Along wall (mm)')
        ax.grid(alpha=.2)
    fig.suptitle('Actual native courses: blue bead centres; orange one-layer tine section')
    fig.savefig(HERE/'native-contacts.png',dpi=150)
    plt.close(fig)
    output=source.with_name(source.stem.replace('.gcode','')+'-print-only.gcode.3mf')
    if output.exists(): output.unlink()
    save(folder/'packaging.json',package(source,output))

if __name__=='__main__': main()
