"""Replay the inverse-sliced tip in physical Z bands with bounded nozzle paths."""
from __future__ import annotations

import argparse
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from dataclasses import replace
import json
import math
from pathlib import Path

import numpy as np

import map_base as source
from tip_warp import BED_THROUGH, END_HOLD, NORMAL_AGAIN, START_HOLD, TipWarp

TIP_ID = 1902
RETRACT = .8
Z_PRINT_MM_MIN = 450.
Z_TRAVEL_MM_MIN = 900.
TRAVEL_XY_MM_MIN = 5400.
LIFT = .85
FILAMENT_AREA = math.pi*.875**2
MIN_PATH = .00001
SUBDIVIDE_ROAD_MM = 1.
UPHILL_WALLS = source.WALLS
SHOULDER_FINE_BANDS = (8.,44.)


def mix(a,b,t):
    return tuple(v*(1-t)+w*t for v,w in zip(a,b))


def physical_phase(warp,u):
    if u <= BED_THROUGH:
        return 'tip anchor'
    if u < START_HOLD:
        return 'tip shoulder entry'
    if u <= END_HOLD+1e-4:
        return 'tip yellow shoulder'
    if u < NORMAL_AGAIN-1e-4:
        return 'tip shoulder fade'
    return 'tip native nose'


def tip_source(report):
    obj=next(row for row in report["parts"] if row["name"]=="faucet-shell-tip")
    placed=np.asarray(obj['build_transform']).reshape(4,3)
    rotation=placed[:3].T
    translation=placed[3]-rotation@np.asarray(obj['source_center_mm'])
    return rotation,translation


def layout(receipt,report):
    warp=TipWarp(tuple(receipt["authored_plane_pick_world_xyz_mm"]),
                 receipt["full_angle_degrees"],receipt["virtual_shoulder_z_mm"])
    rotation,donor=tip_source(report)
    if not np.allclose(rotation,receipt["physical_rotation"],rtol=0,atol=1e-6):
        raise ValueError('Warped donor rotation contradicts model pre-warp receipt')
    displacement=tuple(np.asarray(receipt["physical_cad_to_plate_translation"])-donor)
    return warp,displacement


def physical_linear(move,displacement,warp):
    raw=list(source.points(move)) if move.arc else [move.end]
    prev=move.start
    points=[prev]
    for point in raw:
        dist=math.dist(prev,point)
        if dist<=MIN_PATH:
            continue
        stable_zone = max(prev[2],point[2])+displacement[2] <= BED_THROUGH or min(prev[2],point[2])+displacement[2] >= NORMAL_AGAIN
        n=1 if stable_zone else max(1,math.ceil(dist/SUBDIVIDE_ROAD_MM))
        points.extend(mix(prev,point,j/n) for j in range(1,n+1))
        prev=point
    if len(points)<2:
        return []
    p=np.asarray(points)
    lengths=np.linalg.norm(np.diff(p,axis=0),axis=1)
    curve=p+displacement
    curve[:,2]=warp.forward(curve[:,1],curve[:,2])
    m=(p[1:]+p[:-1])*.5+displacement
    if np.all(np.abs(curve[:,2]-p[:,2]-displacement[2])<1e-8):
        thickening=np.ones_like(lengths)
    elif move.bead_height:
        height=float(move.bead_height)
        thickening=(warp.forward(m[:,1],m[:,2])-warp.forward(m[:,1],m[:,2]-height))/height
    else:
        thickening=warp.derivative(m[:,1],m[:,2])
    volumes=move.e*lengths/sum(lengths)*thickening
    return [replace(move,start=tuple(a),end=tuple(b),e=float(e),arc=None)
            for a,b,e in zip(curve,curve[1:],volumes)]


def band_boundaries(step,fine=None):
    if not step:
        return []
    ordinary=[i*step for i in range(1,math.ceil(321/step)+1)]
    if fine is None:
        return ordinary
    lower,upper=SHOULDER_FINE_BANDS
    rib=[lower+i*fine for i in range(math.ceil((upper-lower)/fine)) if lower+i*fine<upper-1e-6]
    return sorted(set([*rib,upper,*[h for h in ordinary if h<lower-1e-6 or h>upper+1e-6]]))


def cut_at_bands(move,boundaries):
    low=min(move.start[2],move.end[2])
    high=max(move.start[2],move.end[2])
    delta=move.end[2]-move.start[2]
    if high-low<MIN_PATH:
        yield round(boundaries[bisect_left(boundaries,high-1e-6)],5),move
        return
    cuts=boundaries[bisect_right(boundaries,low+1e-6):bisect_left(boundaries,high-1e-6)]
    t=sorted((edge-move.start[2])/delta for edge in cuts)
    for a,b in zip([0.,*t],[*t,1.]):
        level=boundaries[bisect_left(boundaries,move.start[2]+delta*(a+b)*.5-1e-6)]
        yield round(level,5),replace(move,start=mix(move.start,move.end,a),
                                      end=mix(move.start,move.end,b),e=move.e*(b-a))


def upward_runs(run):
    """Cut orientation changes without shortening or flattening individual roads."""
    previous_sign=0
    sample=[]
    for p in run:
        dz=p.end[2]-p.start[2]
        sign=0 if abs(dz)<.002 else 1 if dz>0 else -1
        if sign and previous_sign and sign!=previous_sign:
            if previous_sign<0:
                yield [replace(m,start=m.end,end=m.start) for m in reversed(sample)]
            else:
                yield sample
            sample=[]
        sample.append(p)
        previous_sign=sign or previous_sign
    if sample:
        if previous_sign<0:
            yield [replace(m,start=m.end,end=m.start) for m in reversed(sample)]
        else:
            yield sample


def split_runs(moves,displacement,warp,boundaries,u,uphill):
    grouped=defaultdict(list)
    for native_path in source.runs_of(moves):
        runs=defaultdict(list)
        for move in native_path:
            for projected in physical_linear(move,displacement,warp):
                # The cardinal edge support/foot remains independently printable.
                # A route tagged Bridge is never flipped, though geometric band
                # cuts can interrupt its tension and are independently audited.
                bands=cut_at_bands(projected,boundaries) if boundaries and BED_THROUGH < u < NORMAL_AGAIN-1e-4 else [(None,projected)]
                for band,p in bands:
                    if source.output_point(p.start)==source.output_point(p.end):
                        continue
                    neighbors=runs[band]
                    if not neighbors or math.dist(neighbors[-1][-1].end,p.start)>.002:
                        neighbors.append([])
                    neighbors[-1].append(p)
        for band,paths in runs.items():
            for path in paths:
                if uphill and u > BED_THROUGH and u < NORMAL_AGAIN-1e-4 and path[0].feature in UPHILL_WALLS:
                    grouped[band].extend(upward_runs(path))
                elif any(m.e and round(m.e,5)>0 for m in path):
                    grouped[band].append(path)
    return grouped


def order_local_height(runs):
    """Print each portion of one virtual course before its uphill neighbours."""
    stock=[]
    bridges=[]
    for run in runs:
        if 'Bridge' in run[0].feature:
            bridges.append(run)
        else:
            stock.extend(upward_runs(run))
    order=lambda run: (round(run[0].start[2],6),max(p.end[2] for p in run))
    # A bridge needs both ends in place. Keep the source anchor-first policy,
    # while moving independent wall, fill and support runs to the low side first.
    return sorted(stock,key=order)+bridges


def write_course(out,index,height,band,runs,warp,stats):
    phase=physical_phase(warp,height)
    start=runs[0][0].start
    end=runs[-1][-1].end
    xyz=lambda p: ' '.join(f'{v:.3f}' for v in p)
    out.write(f'; HSM_TIP_PHASE: {phase}\n; HSM_TIP_COURSE: {index}\n')
    if band is not None:
        out.write(f'; HSM_TIP_BAND_Z: {band:.5f}\n')
    out.write(f'; HSM_TIP_VIRTUAL_Z: {height:.5f}\n')
    out.write(f'; HSM_ENTRY_XYZ: {xyz(start)}\n; HSM_ENTRY_RETRACT_MM: {RETRACT}\n')
    out.write(f'; HSM_EXIT_XYZ: {xyz(end)}\n; HSM_EXIT_RETRACT_MM: {RETRACT}\n')
    out.write(f'; OBJECT_ID: {TIP_ID}\nG90\nM83\nG1 E{RETRACT:g} F1800\n')
    prev=start
    active={}

    def set_mode(key,val):
        if active.get(key)==val:
            return
        active[key]=val
        out.write(f'{key}{" S" if not key.startswith(";") else ": "}{val}\n')

    def linear(point,feed,extrusion=None):
        nonlocal prev
        if source.output_point(prev)==source.output_point(point):
            return
        rate=source.output_feed(prev,point,feed,Z_PRINT_MM_MIN if extrusion is not None else Z_TRAVEL_MM_MIN)
        x,y,z=point
        material='' if extrusion is None else f' E{extrusion:.5f}'
        out.write(f'G1 X{x:.3f} Y{y:.3f} Z{z:.3f}{material} F{rate}\n')
        prev=point

    for run in runs:
        start=run[0].start
        if math.dist(prev,start)>.001:
            out.write(f'G1 E-{RETRACT:g} F1800\n')
            hike=max(prev[2],start[2],band if band is not None else -math.inf)+LIFT
            linear((*prev[:2],hike),Z_TRAVEL_MM_MIN)
            linear((*start[:2],hike),TRAVEL_XY_MM_MIN)
            linear(start,Z_TRAVEL_MM_MIN)
            out.write(f'G1 E{RETRACT:g} F1800\n')
        for move in run:
            set_mode('; FEATURE',move.feature)
            set_mode('; LINE_WIDTH',move.width or '.42')
            set_mode('; LAYER_HEIGHT',move.bead_height or '.24')
            set_mode('M106',move.fan)
            set_mode('M204',move.acceleration)
            linear(move.end,move.feed,move.e)
            stats[phase]['deposition_roads']+=1
            stats[phase]['filament_mm']+=move.e
            stats[phase]['vertical_roads']+=int(abs(move.end[2]-move.start[2])>.002)
            stats[phase]['downward_bridge_roads']+=int('Bridge' in move.feature and move.end[2]<move.start[2]-.002)
    out.write(f'G1 E-{RETRACT:g} F1800\n')
    out.write('; HSM_TIP_END_COURSE\n')
    stats[phase]['courses']+=1


def write_native_course(out,index,height,moves,warp,displacement,stats):
    """Keep upper input route, acceleration, cooling, retractions, arc geometry and E."""
    phase=physical_phase(warp,height)
    shift=lambda p: tuple(a+b for a,b in zip(p,displacement))
    xyz=lambda p: ' '.join(f'{v:.5f}' for v in p)
    start=shift(moves[0].start)
    end=shift(moves[-1].end)
    out.write(f'; HSM_TIP_PHASE: {phase}\n; HSM_TIP_COURSE: {index}\n')
    out.write(f'; HSM_TIP_VIRTUAL_Z: {height:.5f}\n')
    out.write(f'; HSM_ENTRY_XYZ: {xyz(start)}\n; HSM_ENTRY_RETRACT_MM: {RETRACT}\n')
    out.write(f'; HSM_EXIT_XYZ: {xyz(end)}\n; HSM_EXIT_RETRACT_MM: {RETRACT}\n')
    out.write(f'; OBJECT_ID: {TIP_ID}\nG90\nM83\nG1 E{RETRACT:g} F1800\n')
    mode={}
    for move in moves:
        active_modes = {'M106':move.fan,'M204':move.acceleration}
        if move.deposition:
            active_modes.update({'; FEATURE':move.feature,'; LINE_WIDTH':move.width or '.42',
                                 '; LAYER_HEIGHT':move.bead_height or '.24'})
        for key,v in active_modes.items():
            if v!=mode.get(key):
                out.write(f'{key}{": " if key.startswith(";") else " S"}{v}\n')
                mode[key]=v
        spatial = math.dist(move.start,move.end)>MIN_PATH or move.arc is not None
        if not spatial and move.e is None:
            continue
        cw,i,j=move.arc or (None,None,None)
        cmd='G1' if cw is None else 'G2' if cw else 'G3'
        target = shift(move.end)
        args=' '.join(f'{axis}{v:.5f}' for axis,v in zip('XYZ',target)) if spatial else ''
        arc='' if not move.arc else f' I{i:.5f} J{j:.5f}'
        e='' if move.e is None else f' E{move.e:.5f}'
        out.write(f'{cmd} {args}{arc}{e} F{move.feed:g}\n')
        if move.deposition:
            stats[phase]['deposition_roads']+=1
            stats[phase]['filament_mm']+=move.e
            stats[phase]['vertical_roads']+=int(abs(move.end[2]-move.start[2])>.002)
    out.write(f'G1 E-{RETRACT:g} F1800\n; HSM_TIP_END_COURSE\n')
    stats[phase]['courses']+=1


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('gcode',type=Path)
    p.add_argument('donor',type=Path)
    p.add_argument('warp',type=Path)
    p.add_argument('output',type=Path)
    p.add_argument('--band-step',type=float,default=2.)
    p.add_argument('--shoulder-band-step',type=float,
                   help='Optional finer band step around the shoulder crest and graded lands')
    p.add_argument('--upper-up-to',type=float,default=320.)
    p.add_argument('--uphill-walls',action='store_true')
    p.add_argument('--uphill-all',action='store_true')
    p.add_argument('--native-nose',action='store_true')
    a=p.parse_args()
    warp,displacement=layout(json.loads(a.warp.read_text()),json.loads(a.donor.read_text()))
    boundaries=band_boundaries(a.band_step,a.shoulder_band_step)
    stats=defaultdict(Counter)
    schedule=[]
    for layer,moves in source.groups(a.gcode):
        u=float(layer)+displacement[2]
        if u > a.upper_up_to:
            break
        if a.native_nose and u>=NORMAL_AGAIN-1e-4:
            body=source.active(moves)
            if any(m.e and round(m.e,5)>0 and m.deposition for m in body):
                schedule.append(((2,u,u),u,None,body))
            continue
        for band,runs in split_runs(moves,displacement,warp,boundaries,u,a.uphill_walls).items():
            much=any(m.e and round(m.e,5)>0 for run in runs for m in run)
            phase=physical_phase(warp,u)
            if much:
                state=0 if phase=='tip anchor' else 2 if band is None else 1
                if state==1 and a.uphill_all:
                    runs=order_local_height(runs)
                if not runs:
                    continue
                schedule.append(((state,u if band is None else band,u),u,band,runs))
    schedule.sort(key=lambda x:x[0])
    with a.output.open('w') as tape:
        tape.write('G90\nM83\n')
        for index,(_,u,band,runs) in enumerate(schedule,1):
            if a.native_nose and u>=NORMAL_AGAIN-1e-4:
                write_native_course(tape,index,u,runs,warp,displacement,stats)
            else:
                write_course(tape,index,u,band,runs,warp,stats)
    a.output.with_suffix('.json').write_text(json.dumps({
        'purpose':__doc__,'gcode_source_sha256':source.file_hash(a.gcode),
        'warp_report_sha256':source.file_hash(a.warp),
        'tip_tape_sha256':source.file_hash(a.output),
        'shoulder_placement_mm':warp.shoulder_xyz,'native_nose_from_physical_z_mm':NORMAL_AGAIN,
        'native_donor_translation_to_plate_mm':displacement,
        'world_band_spacing_mm':a.band_step,'finer_band_spacing_mm':a.shoulder_band_step,
        'finer_physical_band_range_mm':SHOULDER_FINE_BANDS if a.shoulder_band_step else None,
        'physical_order':"world band, then virtual source height" if boundaries else "whole virtual course in source height order",
        'uphill_wall_runs':a.uphill_walls,'uphill_all':a.uphill_all,'retained_native_nose_travel':a.native_nose,
        'phase_stats':stats,
    },indent=2)+'\n')


if __name__=='__main__':
    main()
