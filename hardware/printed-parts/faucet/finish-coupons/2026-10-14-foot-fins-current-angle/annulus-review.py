"""Manual whole-annulus path survey; reports measurements, never controls a printer."""
from collections import defaultdict
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import re
import sys
from zipfile import ZipFile

import numpy as np
import shapely
from shapely.geometry import LineString

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('rim_review',HERE/'rim-path-review.py')
rim=importlib.util.module_from_spec(spec);spec.loader.exec_module(rim)

def main():
    folder=HERE/sys.argv[1]/'mark2' if len(sys.argv)>1 else HERE/'stock-vs-tree/mark2'
    prep=json.loads((folder/'preparation.json').read_text())
    archive=next(folder.glob('*-mark2.gcode.3mf'))
    with ZipFile(archive) as z:raw=z.read('Metadata/plate_1.gcode')
    text=raw.decode();paths=rim.paths_module.segments(text)
    lines=text.splitlines()
    breaks=np.zeros(len(lines)+1,dtype=np.int32)
    for i,l in enumerate(lines,1):
        if re.match(r'G[0123]\b',l) and (re.search(r'\bE-',l) or (re.search(r'\b[XY]',l) and not re.search(r'\bE',l))):breaks[i]=1
    breaks=np.cumsum(breaks)
    rows=[]
    for part in prep['parts']:
        oid=part['identify_id'];own=[p for p in paths if p['object']==oid]
        transform=np.array(part['build_transform']);rot=transform[:9].reshape(3,3).T;tr=transform[9:]
        centre=np.array(part['source_center_mm'])
        lower=defaultdict(list);traces=[];trace=[];last=None
        def finish():
            if trace and {p['feature'] for p in trace}&{'Bridge','Overhang wall','Floating vertical shell'}:
                traces.append(trace.copy())
            trace.clear()
        for p in own:
            mid=(p['a']+p['b'])/2
            cad=(mid-tr)@rot+centre;r=math.hypot(cad[0],cad[1])
            if -1.2<=cad[2]<=1.05 and 15.8<=r<=30.6:
                lower[round(p['z'],5)].append(p)
            qualified=.05<=cad[2]<=.60 and 16.1<=r<=30 and p['z']>.68001 and not p['feature'].startswith(('Support','Brim'))
            continuous=last is not None and p['z']==last['z'] and np.linalg.norm(p['a']-last['b'])<.02 and breaks[p['line']-1]==breaks[last['line']]
            if not qualified or not continuous:finish()
            if qualified:trace.append(p)
            last=p
        finish()
        geom={}
        for z,pp in lower.items():
            xy=np.array([[p['a'][:2],p['b'][:2]] for p in pp])
            widths=np.array([p['width']/2 for p in pp])
            geom[z]=shapely.union_all(shapely.buffer(shapely.linestrings(xy),widths,quad_segs=8))
        current={}
        for z in {p['z'] for p in own}:
            pp=[p for p in own if p['z']==z]
            xy=np.array([[p['a'][:2],p['b'][:2]] for p in pp])
            shapes=shapely.buffer(shapely.linestrings(xy),np.array([p['width']/2 for p in pp]),quad_segs=8)
            current[z]=(shapely.STRtree(shapes),np.array([p['line'] for p in pp]))
        surveyed=[]
        for trace in traces:
            xyz=[trace[0]['a']]+[p['b'] for p in trace]
            line=LineString([p[:2] for p in xyz]);length=line.length
            if length<.1:continue
            z=trace[0]['z'];n=max(1,math.ceil(length/.05));step=length/n
            points=shapely.line_interpolate_point(line,np.linspace(0,length,n+1))
            covered=np.zeros(n+1,dtype=bool);gaps={}
            for courses in [1,2,3]:
                foot=geom.get(round(z-.24*courses,5),shapely.GeometryCollection())
                covered|=shapely.covered_by(points,foot)
                longest=run=0
                for hit in covered:
                    run=0 if hit else run+1;longest=max(longest,run)
                gaps[str(courses)]=min(length,longest*step)
            width=min(p['width'] for p in trace)
            below=shapely.union_all([geom.get(round(z-.24*k,5),shapely.GeometryCollection()) for k in [1,2,3]])
            overlap=shapely.dwithin(points,below,width/2)
            tree,order=current[z]
            hits=tree.query(points,predicate='dwithin',distance=width/2)
            earlier=hits[0,order[hits[1]]<trace[0]['line']]
            with_earlier=overlap.copy();with_earlier[earlier]=True
            def air_run(covered):
                longest=run=0
                for hit in covered:
                    run=0 if hit else run+1;longest=max(longest,run)
                return min(length,longest*step)
            surveyed.append(dict(first_gcode_line=trace[0]['line'],last_gcode_line=trace[-1]['line'],
                nozzle_z_mm=z,path_length_mm=length,features=sorted({p['feature'] for p in trace}),
                longest_no_centreline_bearing_within_courses_mm=gaps,
                longest_no_bead_overlap_within_three_courses_mm=air_run(overlap),
                longest_no_bead_overlap_below_or_earlier_same_course_mm=air_run(with_earlier),
                start_xyz_mm=xyz[0].tolist(),end_xyz_mm=xyz[-1].tolist()))
        surveyed.sort(key=lambda r:r['longest_no_centreline_bearing_within_courses_mm']['3'],reverse=True)
        fan=defaultdict(set);speed=defaultdict(set);early=set()
        for p in own:
            if p['z']>.68001:
                fan[p['feature']].add(round(p['fan']/2.55,4));speed[p['feature']].add(round(p['speed'],4))
            else:early.add(round(p['fan']/2.55,4))
        rows.append(dict(object=oid,name=part['name'],surveyed_continuous_traces=len(surveyed),
            maximum_no_bearing_within_three_courses_mm=surveyed[0]['longest_no_centreline_bearing_within_courses_mm']['3'] if surveyed else None,
            traces_exceeding_12mm=sum(r['longest_no_centreline_bearing_within_courses_mm']['3']>12 for r in surveyed),
            maximum_no_bead_overlap_below_or_earlier_same_course_mm=max(r['longest_no_bead_overlap_below_or_earlier_same_course_mm'] for r in surveyed),
            first_three_layer_fan_percent=sorted(early),
            after_three_layer_fan_percent_by_feature={k:sorted(v) for k,v in fan.items()},
            after_three_layer_speed_range_mm_s_by_feature={k:[min(v),max(v)] for k,v in speed.items()},
            traces=surveyed))
        print(json.dumps({k:v for k,v in rows[-1].items() if k!='traces'}),flush=True)
    out=dict(gcode_sha256=hashlib.sha256(raw).hexdigest(),sample_pitch_max_mm=.05,
        scope='Continuous native model-extrusion paths with nozzle-centre CAD Z0.05..0.60 and radius16.1..30mm, after the three bed layers. Traces must include Bridge, Overhang wall or Floating vertical shell. Lower footprints include native model and support beads at CAD Z-1.2..1.05 and radius15.8..30.6mm.',
        interpretation='Centreline bearing and bead-edge overlap are sampled against actual lower-course footprints. Earlier same-course overlap uses only beads deposited before the trace starts; those neighbours may themselves be unsupported. Three courses allow up to0.72mm nominal nozzle-height separation. These measurements are not weld or bridge-end qualification, sag prediction or physical finish acceptance. Contiguous extrusion is retained across feature changes. Twelve millimetres is a comparison reference from the bridge coupon, not a qualification gate.',
        specimens=rows)
    (folder/'annulus-review.json').write_text(json.dumps(out,indent=2)+'\n')

if __name__=='__main__':main()
