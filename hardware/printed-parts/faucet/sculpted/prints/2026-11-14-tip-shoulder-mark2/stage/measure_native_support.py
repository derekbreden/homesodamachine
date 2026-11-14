"""Audit actual donor support and first mapped shoulder roads in the mating plane."""
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import re

import numpy as np
from shapely import LineString, Point, Polygon, line_merge, union_all
from shapely.strtree import STRtree

from shoulder_geo import placed, shoulder, solid, section

WORD=re.compile(r'([XYZEF])(-?\d*\.?\d+)')
TOL = .025
SUPPORT_BADGES = ('Support','Support interface','Support transition')


@dataclass(frozen=True)
class Road:
    start: np.ndarray
    end: np.ndarray
    height: float
    width: float
    feature: str
    virtual_z: float
    band_z: float
    sequence: int
    e: float

    @property
    def trace(self):
        return LineString((self.start[:2],self.end[:2]))


def read_tape(tape,frame):
    pos=(0.0,0.0,0.0)
    height,width=.24,.42
    virtual,band=0.,0.
    feature='Custom'
    sequence=0
    in_tip=False
    with tape.open() as stream:
        for line in stream:
            if line.startswith('; HSM_TIP_VIRTUAL_Z:'):
                virtual=float(line.split(':',1)[1])
            elif line.startswith('; HSM_PHASE:'):
                in_tip=line.split(':',1)[1].strip().startswith('tip ')
            elif line.startswith('; HSM_TIP_BAND_Z:'):
                band=float(line.split(':',1)[1])
            elif line.startswith('; HSM_TIP_COURSE:'):
                sequence=int(line.split(':',1)[1])
                in_tip=True
            elif line.startswith('; HSM_ENTRY_XYZ:'):
                pos=tuple(map(float,line.split(':',1)[1].split()))
            elif line.startswith('; FEATURE:'):
                feature=line.split(':',1)[1].strip()
            elif line.startswith('; LINE_WIDTH:'):
                width=float(line.split(':',1)[1])
            elif line.startswith('; LAYER_HEIGHT:'):
                height=float(line.split(':',1)[1])
            elif line.startswith('G1 '):
                values={key:float(value) for key,value in WORD.findall(line)}
                end=tuple(values.get(key,old) for key,old in zip('XYZ',pos))
                if in_tip and values.get('E',0)>0 and (0.01 < virtual < 30.) and end!=pos:
                    a,b=frame.relative([pos,end])
                    yield Road(a,b,height,width,feature,virtual,band,sequence,values['E'])
                pos=end


def road_foot(road,raw_width=False,tol=0.):
    length=math.dist(road.start,road.end)
    if length<=1e-6:
        return Polygon()
    radius=road.width/2
    if not raw_width and road.e>0 and road.height>0:
        h=road.height
        equivalent=road.e*math.pi*.875**2/(length*h)+h*(1-math.pi/4)
        radius=min(radius,equivalent/2)
    return road.trace.buffer(radius+tol,quad_segs=4)


def lines_of(r):
    return [r] if r.geom_type=='LineString' else list(getattr(r,'geoms',[]))


def release_witnesses(interface, outer, plug, radius=.7):
    """Check nominal nipper corridors where the annulus and seam lie completely outside the plug."""
    center=np.asarray(outer.centroid.coords[0]);r=(outer.bounds[2]-outer.bounds[0])/2
    result=[]
    for side in (-1,1):
        angle=math.pi if side<0 else 0.0
        along=np.array([math.cos(angle),math.sin(angle)])
        a=center+along*(r-1.25); b=center+along*(r+2.0)
        path=LineString((a,b))
        corridor=path.buffer(radius,cap_style='flat')
        occupied=path.intersection(interface)
        minimum_usable_shift=Point(b).distance(interface)
        result.append({'angular_seam_deg':math.degrees(angle),
                       'uv_centerline_start_and_end_mm':[a.tolist(),b.tolist()],
                       'nipper_tip_path_half_width_mm':radius,
                       'centerline_in_top_roof_mm':occupied.length,
                       'nipper_plane_corridor_over_model_plug_mm2':corridor.intersection(plug).area,
                       'nipper_plane_corridor_over_roof_mm2':corridor.intersection(interface).area,
                       'outside_approach_to_roof_mm':minimum_usable_shift})
    return result


def stats(targets,prior,roof,center,origin):
    conventional=union_all([road_foot(m) for m in prior]).buffer(TOL)
    interface=union_all([road_foot(m) for m in roof]).buffer(TOL)
    stock=conventional.union(interface)
    target_groups=defaultdict(list)
    upstream=prior+roof
    actual=[road_foot(r, tol=TOL) for r in upstream]
    reader=STRtree(actual)
    for move in targets:
        target_groups[move.feature].append(move)
    out={}
    for label,rows in target_groups.items():
        line=union_all([r.trace for r in rows]).intersection(center)
        if line.is_empty:
            continue
        footprint=union_all([road_foot(r,raw_width=True) for r in rows]).intersection(center)
        gap=line_merge(line.difference(stock))
        ready_trace_length=0.0
        missing_order=[]
        for r in rows:
            t=r.trace.intersection(center)
            if t.is_empty:
                continue
            existing=union_all([actual[k] for k in reader.query(t,predicate='intersects') if upstream[k].sequence<r.sequence])
            ready_trace_length+=t.intersection(existing).length
            supported=t.intersection(stock)
            if not supported.is_empty:
                missing_order.append(supported.difference(existing))
        unsupported=[]
        for l in sorted(lines_of(gap),key=lambda p:-p.length)[:8]:
            if l.length<.05:
                continue
            approx=l.interpolate(.5, normalized=True)
            x,y=approx.coords[0]
            unsupported.append({'length_mm':l.length,'center_uv_mm':[x,y],
                                'center_ring_azimuth_deg': (math.degrees(math.atan2(y-origin[1],x-origin[0]))+360)%360})
        out[label]={'road_centerline_on_yellow_mm':line.length,'underlying_part_centerline_landing_fraction':line.intersection(conventional).length/line.length,
                    'interface_centerline_landing_fraction':line.intersection(interface).length/line.length,
                    'interface_bead_area_fraction':footprint.intersection(interface).area/footprint.area,
                    'joint_support_or_part_centerline_fraction':line.intersection(stock).length/line.length,
                    'centerline_on_actual_already_printed_support_fraction':ready_trace_length/sum(r.trace.intersection(center).length for r in rows),
                    'landings_scheduled_after_deposit_length_mm':union_all(missing_order).length,
                    'longest_free_centerline_mm':max((r.length for r in lines_of(gap)),default=0.0),
                    'unbacked_continuous_roads':unsupported}
    return out


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mesh',type=Path);parser.add_argument('project',type=Path)
    parser.add_argument('tape',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('--support-audit',type=Path,
                        help='Optional bed-root and interface reading from the actual native donor')
    args=parser.parse_args()
    mesh,world,frame=placed(args.mesh,args.project)
    lip,outer,plug_outline,raw=shoulder(mesh)
    true_vol=solid(frame.relative(world),mesh.faces)
    incoming=[]; roof=[]; support=[]; targets=[]; near_positive=[]; prior=[]
    for road in read_tape(args.tape,frame):
        z=road.virtual_z
        if road.feature in SUPPORT_BADGES:
            support.append(road)
            if abs(z-22.04)<1e-4 and road.feature=='Support interface':
                roof.append(road)
            if min(road.start[2],road.end[2]) < .1 and road.feature=='Support interface':
                incoming.append(road)
            if 22.04<z<22.95 and road.feature=='Support interface':
                near_positive.append(road)
        elif abs(z-22.28)<1e-4:
            prior.append(road)
        elif abs(z-22.52)<1e-4:
            targets.append(road)
    roof_on_lip=[m for m in roof if m.trace.intersects(lip)]
    stock=union_all([road_foot(m) for m in roof_on_lip]).buffer(TOL)
    full_interface=union_all([road_foot(m) for m in roof]).buffer(TOL)
    near=[m for m in targets if m.trace.intersects(lip)]
    part_below=section(true_vol,-.24)
    material_at_plane=section(true_vol,.12)
    deepest=union_all([road_foot(m) for m in support if max(m.start[2],m.end[2])<=.1 and
                       min(m.start[2],m.end[2])>=-1.0]).buffer(TOL)
    high_interface={}
    for u in sorted({r.virtual_z for r in near_positive}):
        high=[r for r in near_positive if r.virtual_z==u]
        stock_at_h=union_all([road_foot(r) for r in high])
        d=[k for r in high for k in (r.start[2],r.end[2])]
        high_interface[u]={'normal_top_range_mm':[min(d),max(d)],
                           'footprint_area_mm2':stock_at_h.area,
                           'support_crosses_yellow_plane_xy_mm2':stock_at_h.intersection(lip).area,
                           'support_crosses_true_solid_at_same_normal_mm2':stock_at_h.intersection(section(true_vol,float(np.mean(d)))).area,
                           'bearings_mm': stock_at_h.bounds}
    normal_gap=-max(max(m.start[2],m.end[2]) for m in roof_on_lip)
    out={'purpose':__doc__,'tape_sha256':hashlib.sha256(args.tape.read_bytes()).hexdigest(),
         'mesh_sha256':hashlib.sha256(args.mesh.read_bytes()).hexdigest(),
         'mating_lip_mm2':lip.area,'mating_lip_coverage_mm2':lip.intersection(stock).area,
         'mating_lip_coverage_fraction':lip.intersection(stock).area/lip.area,
         'native_roof_course_on_lip_road_count':len(roof_on_lip),'native_roof_course_total_road_count':len(roof),
         'roof_area_hits_plug_mm2':part_below.intersection(stock).area,
         'bore_area_hits_roof_mm2':sum(Polygon(h).intersection(stock).area for p in [material_at_plane] if p.geom_type=='Polygon' for h in p.interiors),
         'top_roof_normal_range_mm':[min(min(r.start[2],r.end[2]) for r in roof_on_lip),max(max(r.start[2],r.end[2]) for r in roof_on_lip)],
         'first_model_nozzle_normal_range_mm':[min(min(r.start[2],r.end[2]) for r in near),max(max(r.start[2],r.end[2]) for r in near)],
         'first_model_feature_paths':stats(near,prior,roof_on_lip,lip,((outer.bounds[0]+outer.bounds[2])/2,(outer.bounds[1]+outer.bounds[3])/2)),
         'trace_contains_support_course_xy_outside_tip_shadow': len([m for m in roof if not m.trace.intersects(outer)]),
         'support_near_joint_plug_overlap_mm2':deepest.intersection(part_below).area,
         'closest_top_interface_to_model_shoulder_normal_mm':normal_gap,
         'roof_footprint_connected_components':len(getattr(full_interface,'geoms',[full_interface])),
         'full_roof_planar_distance_from_plug_mm':full_interface.distance(part_below),
         'angular_seam_tool_access':release_witnesses(full_interface,outer,part_below),
         'higher_interface_courses':high_interface}
    if args.support_audit:
        audit=args.support_audit.read_bytes()
        source=json.loads(audit)
        interfaces=[island for island in source['interfaces'] if 21.0 < island['first_z_mm'] < 23.0]
        root_ids={i['tree'] for i in interfaces}
        roots=[{k:t[k] for k in ('id','root','base_z_mm')}
               for t in source['trees'] if t['id'] in root_ids]
        if not interfaces or not roots:
            raise ValueError('The native audit does not connect a support to the shoulder')
        out['native_shoulder_root']={'source_audit_sha256':hashlib.sha256(audit).hexdigest(),
                                    'roots':roots,'interfaces':interfaces}
    out['expected_removal']={
      'shell_passage':'The modeled roof clears the plug and bore. The full native tree is continuous below the two labeled roof sectors.',
      'shoulder_tool_approach':'Approach both X extrema from the outer side of the open rim. If the ribbon remains connected as sliced, sever the exposed roof work at both radial cuts and pull the two pieces out laterally.',
      'unverified':'Physical pull-off and nipper-jaw access depend on the finished print and actual tool envelope.'}
    args.output.write_text(json.dumps(out,indent=2)+'\n')


if __name__=='__main__':main()
