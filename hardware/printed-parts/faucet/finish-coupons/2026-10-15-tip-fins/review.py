"""Manual review of the single candidate's native paths, placement and joint skin."""
from collections import defaultdict
from pathlib import Path
import hashlib
import json
import math
import re
import sys
from zipfile import ZipFile

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union
import trimesh

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/bambu_print.py').exists())
FOLDER=HERE/'mark2'
sys.path[:0]=[str(ROOT/'hardware/print-tests/petgf-fins'),str(ROOT/'tools')]
from review import segments
from bambu_print_archive import package


def longest(mask, pitch):
    run=best=0
    for value in mask:
        run=run+1 if value else 0
        best=max(best,run)
    return max(0,(best-1)*pitch)


def main():
    spec=json.loads((FOLDER/'preparation.json').read_text())
    row=spec['parts'][0]
    archive=ROOT/str(spec['project']).replace('.3mf','.gcode.3mf')
    with ZipFile(archive) as z:
        raw=z.read('Metadata/plate_1.gcode')
        checksum=z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        settings=json.loads(z.read('Metadata/project_settings.config'))
    assert hashlib.md5(raw).hexdigest()==checksum
    text=raw.decode()
    paths=segments(text)
    assert paths
    assert [float(v) for v in re.findall(r'^\s*G29\.1 Z([-+.\d]+)',text,re.M)]==[0,.02]
    assert settings['support_type']=='tree(auto)' and settings['support_style']=='default'
    assert settings['bridge_flow']=='1.25'
    assert all(p['fan']==0 for p in paths if p['z']<=.68001)
    assert all(abs(p['fan']-178.5)<.001 for p in paths if p['z']>.68001)
    assert all(abs(p['speed']-15)<.001 for p in paths if p['feature']=='Bridge' and p['z']>.68001)
    assert all(p['speed']<=15.001 for p in paths if p['feature']=='Overhang wall')
    low=np.full(2,np.inf);high=-low
    for p in paths:
        xy=np.array([p['a'][:2],p['b'][:2]])
        low=np.minimum(low,xy.min(axis=0)-p['width']/2)
        high=np.maximum(high,xy.max(axis=0)+p['width']/2)
    inset=float(min(*low,325-high[0],320-high[1]))
    assert inset>=80,inset
    scope=json.loads((HERE/'contact-scope.json').read_text())
    normal=np.array(scope['normal']);point=np.array(scope['point'])
    t=np.array(row['build_transform']);rotation=t[:9].reshape(3,3).T;translation=t[9:]
    center=np.array(row['source_center_mm'])
    world_normal=rotation@normal
    world_point=(point-center)@rotation.T+translation
    source=trimesh.load(ROOT/row['source'],force='mesh')
    selected=(np.max(abs((source.triangles-point)@normal),axis=1)<.02)&(source.face_normals@(-normal)>.999)
    projected=(source.triangles[selected]-center)@rotation.T+translation
    footprint=unary_union([Polygon(tri[:,:2]) for tri in projected]).buffer(.30)
    # Follow continuous deposition through feature changes, then sample only the
    # first 0.7 mm of part above the joint plane. Fins lie below that plane.
    traces=[];active=None
    for p in paths:
        middle=(p['a']+p['b'])/2
        distance=float((middle-world_point)@world_normal)
        keep=(p['object']==row['identify_id'] and not p['feature'].startswith('Support')
              and p['feature']!='Brim' and .02<=distance<=.70
              and footprint.covers(shapely.Point(*middle[:2])))
        if not keep:
            active=None
            continue
        if active is None or active['z']!=p['z'] or np.linalg.norm(active['points'][-1]-p['a'][:2])>.005:
            active=dict(z=p['z'],line=p['line'],end_line=p['line'],points=[p['a'][:2]],width=p['width'],features=set())
            traces.append(active)
        active['points'].append(p['b'][:2]);active['features'].add(p['feature']);active['end_line']=p['line']
    layers=defaultdict(list)
    for p in paths:layers[round(p['z'],5)].append(p)
    unions={}
    def at(z):
        if z not in unions:
            unions[z]=unary_union([LineString([p['a'][:2],p['b'][:2]]).buffer(p['width']/2,quad_segs=4)
                                   for p in layers[z]])
        return unions[z]
    results=[]
    for trace in traces:
        line=LineString(trace['points'])
        if line.length<.10:continue
        count=max(2,math.ceil(line.length/.05)+1);pitch=line.length/(count-1)
        samples=shapely.line_interpolate_point(line,np.linspace(0,line.length,count))
        lower=[]
        for courses in (1,2,3):
            z=round(trace['z']-.24*courses,5)
            lower.append(at(z))
        bearing=unary_union(lower)
        overlap=shapely.intersects(bearing.buffer(trace['width']/2),samples)
        earlier=unary_union([LineString([p['a'][:2],p['b'][:2]]).buffer(p['width']/2,quad_segs=4)
                for p in layers[round(trace['z'],5)] if p['line']<trace['line']])
        neighbour=shapely.intersects(earlier.buffer(trace['width']/2),samples)
        low_start=float((line.interpolate(.5,normalized=True).x-translation[0]))
        results.append(dict(nominal_print_z_mm=trace['z'],first_gcode_line=trace['line'],last_gcode_line=trace['end_line'],
            length_mm=line.length,width_mm=trace['width'],features=sorted(trace['features']),
            start_xy_mm=list(line.coords[0]),end_xy_mm=list(line.coords[-1]),
            no_lower_overlap_run_mm=longest(~overlap,pitch),
            no_lower_or_earlier_neighbour_overlap_run_mm=longest(~(overlap|neighbour),pitch)))
    assert results,'No first-skin paths located'
    worst=max(results,key=lambda p:p['no_lower_or_earlier_neighbour_overlap_run_mm'])
    front=[p for p in results if p['nominal_print_z_mm']<17 and min(abs(p['start_xy_mm'][0]-translation[0]),abs(p['end_xy_mm'][0]-translation[0]))<4]
    report=dict(archive=str(archive.relative_to(ROOT)),archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
        gcode_sha256=hashlib.sha256(raw).hexdigest(),embedded_md5_matches=True,
        specimen_count=1,repeat_control=False,fin_count=8,angle_x_degrees=-105,
        layer_count=len({p['z'] for p in paths}),height_range_mm=[min(p['z'] for p in paths),max(p['z'] for p in paths)],
        fan_first_three_layers_percent=[0],fan_after_first_three_layers_percent=[70],
        model_features=sorted({p['feature'] for p in paths if not p['feature'].startswith('Support')}),
        bridge_speed_mm_s=sorted({p['speed'] for p in paths if p['feature']=='Bridge' and p['z']>.68001}),
        overhang_wall_speed_mm_s=sorted({p['speed'] for p in paths if p['feature']=='Overhang wall'}),
        full_bead_envelope_mm=[low.tolist(),high.tolist()],minimum_edge_clearance_mm=inset,
        support_segments=sum(p['feature'].startswith('Support') for p in paths),
        joint_skin=dict(cad_plane_point=point.tolist(),cad_plane_normal=normal.tolist(),
            selected_face_area_mm2=float(source.area_faces[selected].sum()),trace_count=len(results),
            maximum_no_lower_overlap_run_mm=max(p['no_lower_overlap_run_mm'] for p in results),
            maximum_no_lower_or_earlier_neighbour_overlap_run_mm=worst['no_lower_or_earlier_neighbour_overlap_run_mm'],
            worst_trace=worst,low_midpoint_traces=front,traces=results),
        limits='0.05 mm maximum sample pitch on the commanded first-skin paths. Lower actual bead footprints within three courses and earlier same-course neighbours are geometric bearings, not predicted strand support or fusion; neighbours may also sag. This audit does not establish finish or fin removal.')
    (FOLDER/'review.json').write_text(json.dumps(report,indent=2)+'\n')
    print_only=archive.with_name(archive.name.removesuffix('.gcode.3mf')+'-print-only.gcode.3mf')
    if print_only.exists():raise ValueError('Preserve the packaged review; use a new candidate for revisions')
    packaging=package(archive,print_only)
    (FOLDER/'packaging.json').write_text(json.dumps(packaging,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='joint_skin'},indent=2))
    print(json.dumps({'joint_trace_count':len(results),'worst':worst,'low_midpoint_traces':front},indent=2))


if __name__=='__main__':main()
