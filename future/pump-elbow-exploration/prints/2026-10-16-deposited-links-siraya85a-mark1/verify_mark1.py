"""Manual review of the emitted elbow trial, including every free strand chord."""
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import zipfile

import numpy as np
from shapely.geometry import LineString
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/bambu_printer.py').is_file())
sys.path[:0] = [str(HERE.parent.parent),str(ROOT/'tools')]
from departure_lap import movements, MEMBER
from travel_survey import arc_xy
from wall_travel import model_layer_outlines
from bambu_print import archive_details


def main():
    source = next(HERE.glob('*-native.gcode.3mf'))
    output = source.with_name(source.name.replace('-native.gcode.3mf','.gcode.3mf'))
    with zipfile.ZipFile(source) as z:
        a = {n:z.read(n) for n in z.namelist()}
    with zipfile.ZipFile(output) as z:
        b = {n:z.read(n) for n in z.namelist()}
    assert set(a)==set(b)
    changed = sorted(n for n in a if a[n]!=b[n])
    assert changed==[MEMBER,MEMBER+'.md5']
    original = list(movements(a[MEMBER].decode().splitlines(keepends=True)))
    emitted_lines = b[MEMBER].decode().splitlines(keepends=True)
    emitted = list(movements(emitted_lines))
    native = {m['index']+1:m for m in original if m['layer']>0 and m['words'].get('E',-1)>0
              and math.dist(m['start'][:2],m['end'][:2])>1e-8}
    tag,tag_at = None,{}
    for i,line in enumerate(emitted_lines):
        if line.startswith('; DEPOSITION_SOURCE:'):
            kind,number = line.split(':',1)[1].split()
            tag = kind,int(number)
        tag_at[i] = tag
    received,geometries,extra = Counter(),defaultdict(list),Counter()
    all_deposited,body = [],[]
    first = next(m['index'] for m in emitted if tag_at[m['index']] is not None)
    last = max(m['index'] for m in emitted if m['words'].get('E',-1)>0
               and m['layer']>0 and tag_at[m['index']] is not None
               and math.dist(m['start'][:2],m['end'][:2])>1e-8)
    max_width_error,max_feed_error = 0.,0.
    capped_sources = set()
    max_flow = 0.
    for m in emitted:
        if not first<=m['index']<=last:
            continue
        body.append(m)
        if m['words'].get('E',0)<=0:
            continue
        assert m['command']=='G1' and m['relative_e'] and m['absolute']
        assert abs(m['start'][2]-m['layer_z'])<1e-6 and abs(m['end'][2]-m['layer_z'])<1e-6
        line = LineString([m['start'][:2],m['end'][:2]])
        assert line.length>0
        kind,number = tag_at[m['index']]
        assert kind in ('native','deposited_return','deposited_anchor')
        if kind in ('native','deposited_return'):
            parent = native[number]
            assert parent['layer']==m['layer'] and parent['feature']==m['feature']
            max_width_error = max(max_width_error,abs(parent['width']-m['width']))
            max_feed_error = max(max_feed_error,abs(parent['feed']-m['feed']))
            assert abs(parent['width']-m['width'])<=.00000051
            expected_feed = min(parent['feed'],2.2*line.length/(m['words']['E']*math.pi*(1.75/2)**2)*60)
            assert abs(expected_feed-m['feed'])<=.015
            if abs(parent['feed']-m['feed'])>.00051:
                capped_sources.add(number)
        if kind=='native':
            received[number] += m['words']['E']
            geometries[number].append(line)
        else:
            extra[(kind,m['feature'])] += m['words']['E']
        max_flow = max(max_flow,m['words']['E']*math.pi*(1.75/2)**2/(line.length/(m['feed']/60)))
        all_deposited.append(m)
    assert set(received)==set(native)
    max_e_error,max_geometry_error = 0.,0.
    for number,parent in native.items():
        max_e_error = max(max_e_error,abs(received[number]-parent['words']['E']))
        assert abs(received[number]-parent['words']['E'])<.000001
        w = parent['words']
        points = [parent['start'][:2]]
        points += arc_xy(parent['start'],parent['end'],w.get('I',0),w.get('J',0),
                         parent['command']=='G2',chord=.01) if parent['command'] in ('G2','G3') else [parent['end'][:2]]
        error = unary_union(geometries[number]).hausdorff_distance(LineString(points))
        max_geometry_error = max(max_geometry_error,error)
        assert error<.005,(number,error)
    # Independent replay of ALL free motions, combining consecutive free moves
    # until extrusion starts again. Test the straight attachment-to-attachment
    # chord as well as the commanded route; no small-hole cutoff is used.
    stock,_ = model_layer_outlines(source,original)
    ex = [i for i,m in enumerate(body) if m['words'].get('E',0)>0]
    maximum_chord,maximum_route,maximum_bend = 0.,0.,0.
    travels,layer_changes = 0,0
    for ia,ib in zip(ex,ex[1:]):
        departure,arrival = body[ia],body[ib]
        between = body[ia+1:ib]
        assert not any(m['words'].get('E',0)<0 for m in between)
        points = [departure['end'][:2]]
        for m in between:
            assert m['command']=='G1'
            if math.dist(points[-1],m['end'][:2])>1e-8:
                points.append(m['end'][:2])
        if len(points)==1:
            continue
        assert math.dist(points[-1],arrival['start'][:2])<1e-6
        allowed = stock[(arrival['layer'],0)].buffer(.000001)
        chord = LineString([points[0],points[-1]])
        route = LineString(points)
        off_chord,off_route = chord.difference(allowed).length,route.difference(allowed).length
        excess = route.length-chord.length
        maximum_chord,maximum_route,maximum_bend = max(maximum_chord,off_chord),max(maximum_route,off_route),max(maximum_bend,excess)
        assert off_chord<1e-5 and off_route<1e-5 and excess<1e-5
        travels += 1
        layer_changes += departure['layer']!=arrival['layer']
    # A tiny native fragment alone need not be a reliable physical attachment.
    # Ignore extrusion runs shorter than 1 mm and recheck the free span between
    # the remaining deposited runs as a deliberately conservative case.
    deposition_runs,run = [],[]
    for m in body:
        if m['words'].get('E',0)>0:
            run.append(m)
        elif run:
            deposition_runs.append(run)
            run = []
    if run:
        deposition_runs.append(run)
    substantial = [r for r in deposition_runs if sum(math.dist(m['start'][:2],m['end'][:2]) for m in r)>=1.]
    conservative_span_maximum = 0.
    for a,b0 in zip(substantial,substantial[1:]):
        aa,bb = a[-1],b0[0]
        points = [aa['end'][:2],bb['start'][:2]]
        if math.dist(*points)<=1e-8:
            continue
        off = LineString(points).difference(stock[(bb['layer'],0)].buffer(.000001)).length
        conservative_span_maximum = max(conservative_span_maximum,off)
        assert off<1e-5
    assert all(max(m['start'][2],m['end'][2])<=m['layer_z']+.000001 for m in body)
    assert max_flow<=2.2+.001
    trims = [float(v) for v in re.findall(r'^G29\.1 Z([-+.\d]+)',b[MEMBER].decode(),re.M)]
    assert trims==[0.]
    assert not re.search(rb'^\s*M9711\b',b[MEMBER],re.M)
    lo,hi = np.array([np.inf,np.inf]),np.array([-np.inf,-np.inf])
    for m in all_deposited:
        radius = m['width']/2+.025
        pts = np.asarray([m['start'][:2],m['end'][:2]])
        lo,hi = np.minimum(lo,pts.min(axis=0)-radius),np.maximum(hi,pts.max(axis=0)+radius)
    inset = min(*(lo-np.array([25,0])),*(np.array([330,320])-hi))
    assert inset>80
    review = dict(archive=archive_details(output),modified_zip_members=changed,
                  native_deposition_commands_preserved=len(native),all_native_source_commands_accounted_once=True,
                  maximum_per_source_e_difference_mm=max_e_error,
                  maximum_native_path_hausdorff_difference_mm=max_geometry_error,
                  maximum_native_feed_difference_mm_min=max_feed_error,maximum_line_width_difference_mm=max_width_error,
                  source_commands_slowed_for_2_2_mm3_s_cap=len(capped_sources),
                  added_e_mm_by_kind_and_feature={str(k):v for k,v in extra.items()},
                  extra_deposition_scope='Returns duplicate native inner-wall paths; no new bore-crossing deposition.',
                  nonextruding_transfers_assessed=travels,straight_layer_change_transfers=layer_changes,
                  maximum_free_attachment_chord_outside_model_mm=maximum_chord,
                  maximum_nonextruding_route_outside_model_mm=maximum_route,
                  maximum_nonextruding_route_excess_over_chord_mm=maximum_bend,
                  conservative_attachment_minimum_deposited_length_mm=1.,
                  maximum_chord_outside_model_ignoring_shorter_deposition_runs_mm=conservative_span_maximum,
                  in_part_retractions=0,in_part_z_hops=0,maximum_deposition_flow_mm3_s=max_flow,
                  photo_trip_commands=0,local_z_trim_mm=0,
                  conservative_full_bead_bounds_xy_mm=[lo.tolist(),hi.tolist()],conservative_bed_inset_mm=inset,
                  scope='Every in-part free attachment chord and XY travel stays inside the arriving native model section, retaining every hole. Native paths are reordered and may reverse. Arc chords are at most 0.10 mm; path deviation is measured above. Startup and shutdown are retained and outside this in-part assessment. Adhesion, ooze capture, fin removal and fit require the physical result.')
    (HERE/'emitted-command-review.json').write_text(json.dumps(review,indent=2)+'\n')
    print(json.dumps(review,indent=2),flush=True)


if __name__=='__main__':
    main()
