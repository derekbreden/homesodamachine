"""Manual native contact review of cached installed wiring and final tube spans.

Run through tmp/takeover/cadq after the native routes are settled. Conservative
analytic segment bounds prune disjoint pairs; remaining pairs use native CAD
Booleans. No wiring composition, appliance build or shell generation runs.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT),str(ROOT/'hardware/manifold-layout')]
import cadquery as cq
import above_core_parts
from hardware.wiring.installed.model import STOCK

HERE=Path(__file__).resolve().parent
CACHE=ROOT/'tmp/above-core-electrical-fixture/wiring'


def production_specifications():
    """Selected native tube spans, without composing the appliance or shells."""
    import above_core as layout
    import above_core_routes as onward
    import manifold_layout as manifold
    foam=above_core_parts._module('tube_review_foam',
                                 'printed-parts/cold-core/foam-assembly/foam_assembly.py')
    rows={**above_core_parts.components(),**above_core_parts.core_components()}
    carries={name:row[2] for name,row in rows.items()}
    def manifold_carry(station):
        point,axis=station
        return manifold.enclosure_point(point),manifold.enclosure_axis(axis)
    for letter in 'efghij':carries['valve-v-'+letter]=manifold_carry
    cap=layout.cap_lid_pose()
    def resolve(name,port):
        if name=='foam-assembly':
            xyz,axis=foam.cap_conduit_mouth(port)
            local=(-xyz[0],-xyz[1],xyz[2]-foam.foam_shell_outer_height-foam.top_cap_height)
            return (layout.point(cap,local),
                    layout.vector(cap['rotation'],(-axis[0],-axis[1],axis[2])),6.35)
        return onward._station(carries,name,port)
    specs={**above_core_parts.route_specs(),**onward.route_specifications(resolve)}
    if onward.unresolved:raise RuntimeError(onward.unresolved)
    return specs


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


def native_bounds(solid):
    box=solid.BoundingBox()
    return [getattr(box,k) for k in ('xmin','ymin','zmin','xmax','ymax','zmax')]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--specs',type=Path,help='Optional saved native specs; defaults to current production APIs')
    parser.add_argument('--only',nargs='+')
    parser.add_argument('--bodies',nargs='+',help='Optional cached wire/termination names for a focused follow-up')
    parser.add_argument('--output',type=Path,default=HERE/'tube-review.json')
    args=parser.parse_args()
    if args.specs:
        raw=args.specs.read_bytes();specs=json.loads(raw)
        source=str(args.specs.relative_to(ROOT)) if args.specs.is_relative_to(ROOT) else str(args.specs)
    else:
        specs=production_specifications()
        raw=json.dumps(specs,sort_keys=True,separators=(',',':')).encode()
        source='above_core_parts.route_specs + above_core_routes.route_specifications'
    if args.only:specs={name:spec for name,spec in specs.items() if name in args.only}
    cache_index=CACHE/'index.json'
    fixture=json.loads(cache_index.read_text())
    files=fixture['parts']
    if args.bodies:files={name:file for name,file in files.items() if name in args.bodies}
    wiring=json.loads((HERE/'native-review.json').read_text())
    routes={'wire-'+r['id']:r for r in wiring['routes']}
    shapes={name:cq.Shape.importBrep(str(CACHE/file)) for name,file in files.items()}
    boxes={}
    for name,solid in shapes.items():
        if name in routes:
            row=routes[name]
            boxes[name]=[box for segment in row['segments']
                         for box in segment_bounds(segment,STOCK[row['stock']]['od_mm']/2.)]
        else:boxes[name]=[native_bounds(solid)]
    record={'scope':'Cached insulated conductors and native connector/termination/jacket bodies '
                    'against selected native fluid tube spans; no physical qualification.',
            'conductor_count':len(routes),'wiring_body_count':len(shapes),'tube_count':len(specs),
            'cached_conductor_count':sum(name in routes for name in shapes),
            'fixture_aggregate_sha256':fixture.get('aggregate_sha256'),
            'fixture_index_sha256':hashlib.sha256(cache_index.read_bytes()).hexdigest(),
            'missing_wire_breps':sorted((set(args.bodies) if args.bodies else set(routes))-set(shapes)),
            'tube_spec_sha256':hashlib.sha256(raw).hexdigest(),
            'tube_spec_source':source,'review_complete':False,
            'native_boolean_count':0,'tubes':{},'intersections':[],'errors':[],
            'wire_brep_sha256':{name:hashlib.sha256((CACHE/file).read_bytes()).hexdigest()
                                for name,file in files.items()}}
    def save():args.output.write_text(json.dumps(record,indent=2)+'\n')
    save()
    for name,spec in specs.items():
        tube_boxes=[box for segment in spec['segments']
                    for box in segment_bounds(segment,spec['od_mm']/2.)]
        candidates=[body for body in shapes
                    if any(overlaps(a,b) for a in boxes[body] for b in tube_boxes)]
        entry={'candidate_bodies':candidates,'native_boolean_count':0}
        record['tubes'][name]=entry
        if candidates:
            tube=above_core_parts.route_shape(spec)
            for body in candidates:
                try:
                    intersection=shapes[body].intersect(tube)
                    volume=intersection.Volume()
                    entry['native_boolean_count']+=1;record['native_boolean_count']+=1
                    if volume>.01:
                        row={'wire_body':body,'tube':name,'volume_mm3':volume,
                             'bounds_mm':native_bounds(intersection)}
                        record['intersections'].append(row)
                        print(json.dumps(row),flush=True)
                except Exception as error:
                    row={'wire_body':body,'tube':name,'error':str(error)}
                    record['errors'].append(row);print(json.dumps(row),flush=True)
        save()
        print(f'{name}: {len(candidates)} native candidate pairs checked',flush=True)
    record['review_complete']=True
    record['geometrically_clear']=(not record['intersections'] and not record['errors'] and
                                   not record['missing_wire_breps'])
    record['source_sha256']={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest()
                            for path in (Path(__file__),Path(above_core_parts.__file__),
                                         ROOT/'hardware/manifold-layout/above_core_routes.py',
                                         ROOT/'hardware/manifold-layout/above-core.json')}
    save()
    print(json.dumps({k:record[k] for k in ('conductor_count','wiring_body_count','tube_count',
                                          'native_boolean_count','geometrically_clear')},indent=2),flush=True)


if __name__=='__main__':main()
