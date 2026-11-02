"""Manual current-fine wiring/tube contact question; never a routing gate.

The normal producer's hash-bound route specs select its actual named fine tube
bodies. No native BREP cache, tube reconstruction or appliance generation runs.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT),str(ROOT/'hardware/scripts'),str(ROOT/'hardware/manifold-layout')]
from hardware.wiring.installed._fine_contacts import (
    CurrentFine,current_fine,fine_arguments,fine_overlap,production_tube_specs)
from hardware.wiring.installed.model import STOCK
HERE=Path(__file__).resolve().parent


def production_specifications(*,manifest=None,aggregate=None,source_root=None,facts=None):
    """Exact specs from the normal producer's bound facts, without native builders."""
    context=CurrentFine(manifest or ROOT/'hardware/wiring/enclosure-wiring.json',
                        aggregate or ROOT/'hardware/manifold-layout/enclosure-assembly.step',
                        source_root=source_root or ROOT,facts=facts)
    return production_tube_specs(context)


def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def mul(a,s):return tuple(x*s for x in a)
def add(a,b):return tuple(x+y for x,y in zip(a,b))


def point_bounds(points,radius):
    return ([min(p[i] for p in points)-radius for i in range(3)]+
            [max(p[i] for p in points)+radius for i in range(3)])


def arc_bounds(points,radius,curve_radius):
    a,mid,b=points
    u,v=sub(mid,a),sub(b,a)
    normal=cross(u,v);n2=dot(normal,normal)
    if n2<1e-18:
        # Degenerate serialized arcs retain a conservative whole-circle reach.
        return point_bounds(points,radius+2.*curve_radius)
    centre=add(a,mul(add(mul(cross(v,normal),dot(u,u)),
                         mul(cross(normal,u),dot(v,v))),1./(2.*n2)))
    r=math.dist(a,centre)
    axis=mul(normal,1./math.sqrt(n2))
    first=mul(sub(a,centre),1./r);second=cross(axis,first)
    last=sub(b,centre)
    angle=math.atan2(dot(last,second),dot(last,first))%(2.*math.pi)
    middle=sub(mid,centre)
    middle_angle=math.atan2(dot(middle,second),dot(middle,first))%(2.*math.pi)
    if middle_angle>angle+1e-7:angle=2.*math.pi
    values=[a,b,mid]
    for i in range(3):
        maximum=math.atan2(second[i],first[i])%(2.*math.pi)
        for theta in (maximum,(maximum+math.pi)%(2.*math.pi)):
            if theta<=angle+1e-7:
                values.append(add(centre,mul(add(mul(first,math.cos(theta)),
                                                mul(second,math.sin(theta))),r)))
    return point_bounds(values,radius)


def bezier_hulls(control,depth=5):
    if not depth:
        yield control
        return
    rows=[control]
    while len(rows[-1])>1:
        rows.append([mul(add(a,b),.5) for a,b in zip(rows[-1],rows[-1][1:])])
    yield from bezier_hulls([row[0] for row in rows],depth-1)
    yield from bezier_hulls([row[-1] for row in reversed(rows)],depth-1)


def segment_bounds(segment,radius):
    radius+=.001
    kind=segment['kind']
    if kind=='spline':
        from hardware.wiring.installed.model import sampled_segments
        points=sampled_segments([segment],.25)
        margin=segment['maximum_sample_step_mm']/2
        return [point_bounds([a,b],radius+margin)for a,b in zip(points,points[1:])]
    if 'start_mm' in segment:
        points=[segment['start_mm'],segment['end_mm']]
        if kind=='arc':points.insert(1,segment['midpoint_mm'])
    else:points=segment.get('points_mm')
    if kind=='bezier':
        return [point_bounds(hull,radius) for hull in bezier_hulls(segment['control_points_mm'])]
    if kind=='arc':return [arc_bounds(points,radius,segment['radius_mm'])]
    return [point_bounds(points,radius)]


def overlaps(a,b):
    return all(a[i+3]>b[i] and b[i+3]>a[i] for i in range(3))



def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    fine_arguments(parser,ROOT)
    parser.add_argument('--specs',type=Path,help='Optional saved specs; each must match this captured production handoff')
    parser.add_argument('--only',nargs='+')
    parser.add_argument('--bodies',nargs='+',help='Explicit wire/termination names for a bounded follow-up')
    parser.add_argument('--output',type=Path,default=HERE/'tube-review.json')
    args=parser.parse_args(argv)
    context=current_fine(args);production=production_tube_specs(context)
    specs=production
    if args.specs:
        raw=args.specs.read_bytes();specs=json.loads(raw)
        if any(name not in production or spec!=production[name]for name,spec in specs.items()):
            raise ValueError('Saved tube specs differ from the explicit current fine handoff')
        source=str(args.specs)
    else:
        raw=json.dumps(specs,sort_keys=True,separators=(',',':')).encode()
        source=str(context.facts_path)+'#/tube_export/routing/native_route_specs'
    if args.only:
        unknown=set(args.only)-set(specs)
        if unknown:raise ValueError('Unknown current tube specs: '+', '.join(sorted(unknown)))
        specs={name:specs[name]for name in args.only}
    names=list(context.names('wiring'))
    if args.bodies:names=[context.resolve(name,'wiring')[1]for name in args.bodies]
    routes={'wire-'+row['id']:row for row in context.manifest['routes']}
    record={'scope':'Actual current fine conductors, connectors, terminations and jackets against the selected actual fine fluid tube spans. This separately requested contact question does not make wire/tube contacts a routing obstruction or qualify physical assembly.',
        'conductor_count':len(routes),'wiring_body_count':len(names),'tube_count':len(specs),
        'cached_conductor_count':sum(name in routes for name in names),
        'fixture_aggregate_sha256':context.digest(context.aggregate),
        'tube_spec_sha256':hashlib.sha256(raw).hexdigest(),'tube_spec_source':source,
        'review_complete':False,'native_boolean_count':0,'fine_boolean_count':0,
        'missing_wire_breps':[],'tubes':{},'intersections':[],'errors':[]}
    pairs=[];owners=[]
    for name,spec in specs.items():
        tube=context.resolve('tube-'+name)
        candidates=[]
        for body in names:
            ref=context.resolve(body,'wiring')
            if fine_overlap(context.bounds(ref),context.bounds(tube),tol=0.):
                candidates.append(body);pairs.append((ref,tube));owners.append((body,name))
        record['tubes'][name]={'qualified_fine_body':tube[1],'candidate_bodies':candidates,
                               'native_boolean_count':0,'fine_boolean_count':0}
    for(body,name),reading in zip(owners,context.commons(pairs)):
        count=reading['entry_common_count'];record['fine_boolean_count']+=count
        record['tubes'][name]['fine_boolean_count']+=count
        hit=reading['raw']
        if hit['volume_mm3']>.01:
            record['intersections'].append({'wire_body':body,'tube':name,'volume_mm3':hit['volume_mm3'],
                                           'bounds_mm':hit['min']+hit['max']})
    record['fine_binding']=context.finish();record['review_complete']=True
    record['geometrically_clear']=not record['intersections']and not record['errors']
    record['source_sha256']={str(Path(__file__).relative_to(ROOT)):context.digest(Path(__file__))}
    args.output.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({key:record[key]for key in('conductor_count','wiring_body_count','tube_count',
                                              'fine_boolean_count','geometrically_clear')}),flush=True)
    return record


if __name__=='__main__':main()
