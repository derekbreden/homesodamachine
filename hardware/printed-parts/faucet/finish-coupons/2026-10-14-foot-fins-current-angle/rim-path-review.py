"""Manual review of the three user-selected rim paths; no slicing or printer control."""
from collections import defaultdict
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import sys
from zipfile import ZipFile

import numpy as np
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/bambu_print.py').exists())
sys.path.insert(0,str(ROOT/'hardware/print-tests/petgf-fins'))
spec=importlib.util.spec_from_file_location('fin_paths',ROOT/'hardware/print-tests/petgf-fins/review.py')
paths_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(paths_module)
FOLDER=HERE/'stock-vs-tree/mark2'
CASES=[('1: highlighted wall',356895),('2: preceding straight wall',372017),
       ('2: highlighted corner',372036),('3: highlighted wall',242112)]

def intervals(line,geom):
    hit=line.intersection(geom)
    chunks=list(hit.geoms) if hasattr(hit,'geoms') else [hit]
    out=[]
    for g in chunks:
        if g.geom_type=='LineString' and g.length>1e-7:
            d=[line.project(Point(p)) for p in g.coords]
            out.append([min(d),max(d)])
    return sorted(out)

def metrics(line,geom,width):
    direct=intervals(line,geom)
    overlap=intervals(line,geom.buffer(width/2))
    def longest_gap(ii):
        end=0;gaps=[]
        for a,b in ii:
            gaps.append(max(0,a-end));end=max(end,b)
        gaps.append(line.length-end)
        return max(gaps)
    return dict(centreline_over_material_mm=direct,
        bead_edge_overlap_intervals_mm=overlap,
        longest_no_centreline_bearing_mm=longest_gap(direct),
        longest_no_bead_overlap_mm=longest_gap(overlap),
        start_centre_over_material=geom.covers(Point(line.coords[0])),
        end_centre_over_material=geom.covers(Point(line.coords[-1])))

def footprint(pp):
    return unary_union([LineString([p['a'][:2],p['b'][:2]]).buffer(p['width']/2,quad_segs=8) for p in pp])

def main():
    candidate=len(sys.argv)>1
    folder=HERE/sys.argv[1]/'mark2' if candidate else FOLDER
    archive=next(folder.glob('*-print-only.gcode.3mf')) if not candidate else next(folder.glob('*-mark2.gcode.3mf'))
    with ZipFile(archive) as z:raw=z.read('Metadata/plate_1.gcode')
    if not candidate:assert hashlib.sha256(raw).hexdigest()=='6c0d4136375b68de1bb5bbe34b572585edd9682707294bcf05fdabe3c4acf63f'
    text=raw.decode();source_lines=text.splitlines()
    paths=paths_module.segments(text)
    by_line=defaultdict(list)
    for p in paths:by_line[p['line']].append(p)
    report=[];plots=[]
    cases=CASES
    if candidate:
        original=json.loads((FOLDER/'rim-path-review.json').read_text())
        cases=[]
        for r in original['cases']:
            matches=[p for p in paths if p['object']==1901 and abs(p['z']-r['nominal_layer_nozzle_z_mm'])<1e-5
                and p['feature']==r['feature'] and np.linalg.norm(p['a'][:2]-r['start_xyz_mm'][:2])<.005
                and np.linalg.norm(p['b'][:2]-r['end_xyz_mm'][:2])<.005]
            assert len(matches)==1,(r['case'],len(matches))
            cases.append((r['case'],matches[0]['line']))
    for label,number in cases:
        pieces=by_line[number]
        p=pieces[0]
        line=LineString([pieces[0]['a'][:2],pieces[-1]['b'][:2]])
        lo=np.minimum(pieces[0]['a'][:2],pieces[-1]['b'][:2])-2
        hi=np.maximum(pieces[0]['a'][:2],pieces[-1]['b'][:2])+2
        roi=box(*lo,*hi)
        own=[]
        for q in paths:
            if q['object']!=1901 or not p['z']-.73<=q['z']<=p['z']+.001:continue
            if max(q['a'][0],q['b'][0])<lo[0]-1 or min(q['a'][0],q['b'][0])>hi[0]+1:continue
            if max(q['a'][1],q['b'][1])<lo[1]-1 or min(q['a'][1],q['b'][1])>hi[1]+1:continue
            own.append(q)
        layers={}
        shapes={}
        for courses in [1,2,3]:
            z=round(p['z']-.24*courses,5)
            pp=[q for q in own if abs(q['z']-z)<1e-5]
            shapes[courses]=footprint(pp)
            layers[str(z)]=dict(metrics(line,shapes[courses],p['width']),
                bead_features=sorted({q['feature'] for q in pp}))
        earlier=[q for q in own if abs(q['z']-p['z'])<1e-5 and q['line']<number]
        prior=footprint(earlier)
        bline=LineString([(x+78,y) for x,y in line.coords])
        bshapes={}
        for courses in [1,2,3]:
            z=round(p['z']-.24*courses,5)
            pp=[]
            for q in paths:
                if q['object']!=1902 or abs(q['z']-z)>1e-5:continue
                if max(q['a'][0],q['b'][0])<lo[0]+77 or min(q['a'][0],q['b'][0])>hi[0]+79:continue
                if max(q['a'][1],q['b'][1])<lo[1]-1 or min(q['a'][1],q['b'][1])>hi[1]+1:continue
                pp.append(q)
            bshapes[str(z)]=metrics(bline,footprint(pp),p['width'])
        row=dict(case=label,gcode_line=number,command=source_lines[number-1],
            object=p['object'],nominal_layer_nozzle_z_mm=p['z'],feature=p['feature'],
            start_xyz_mm=pieces[0]['a'].tolist(),end_xyz_mm=pieces[-1]['b'].tolist(),
            xy_length_mm=line.length,speed_mm_s=p['speed'],part_fan_percent=p['fan']/2.55,
            slicer_bead_width_mm=p['width'],slicer_bead_height_mm=p['height'],
            A_previous_courses=layers,A_current_course_before_move=metrics(line,prior,p['width']),
            B_same_location_previous_courses=bshapes)
        report.append(row)
        plots.append((label,line,shapes,prior,roi,p))
        print(json.dumps(row),flush=True)
    out=dict(gcode_sha256=hashlib.sha256(raw).hexdigest(),source_archive=str(archive.relative_to(ROOT)),
        method='Measured XY footprints of actual deposited beads, using native width and chronological order. Nominal lower courses are kept separate: material two courses below is an intentional-gap bearing, not a preceding-layer weld. Current-course neighbouring strands may themselves be unsupported. Footprints do not predict sag or establish mechanical anchorage.',
        cases=report)
    (folder/'rim-path-review.json').write_text(json.dumps(out,indent=2)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    fig,axes=plt.subplots(4,1,figsize=(12,12),constrained_layout=True)
    def fill(ax,g,colour,alpha):
        if hasattr(g,'geoms'):
            for q in g.geoms:fill(ax,q,colour,alpha)
        elif g.geom_type=='Polygon':
            x,y=g.exterior.xy;ax.fill(x,y,color=colour,alpha=alpha,lw=0)
            for ring in g.interiors:
                x,y=ring.xy;ax.fill(x,y,color='white',lw=0)
    for ax,(label,line,shapes,prior,roi,p) in zip(axes,plots):
        fill(ax,shapes[3].intersection(roi),'#87cdd4',.45)
        fill(ax,shapes[2].intersection(roi),'#1799ab',.65)
        fill(ax,shapes[1].intersection(roi),'#596576',.6)
        fill(ax,prior.intersection(roi),'#e4b24d',.5)
        x,y=line.xy;ax.plot(x,y,color='#d42d38',lw=2,marker='o',markersize=3)
        ax.set(xlim=(roi.bounds[0],roi.bounds[2]),ylim=(roi.bounds[1],roi.bounds[3]),aspect='equal',
            title=f"{label}; Z{p['z']:.2f}, {line.length:.3f} mm at {p['speed']:.1f} mm/s",xlabel='Bed X (mm)',ylabel='Bed Y (mm)')
        ax.grid(alpha=.15)
    fig.legend(handles=[Patch(color='#596576',label='1 course below'),Patch(color='#1799ab',label='2 below'),
        Patch(color='#87cdd4',label='3 below'),Patch(color='#e4b24d',label='Same course, printed earlier'),
        Patch(color='#d42d38',label='Selected move')],loc='outside upper center',ncol=5)
    fig.savefig(folder/'rim-path-review.png' if candidate else HERE/'rim-path-review.png',dpi=160)

if __name__=='__main__':main()
