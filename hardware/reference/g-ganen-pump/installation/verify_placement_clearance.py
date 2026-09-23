"""Bounded native G pump clearance against a retained placed pack and neighbors.

The cap is checked by verify_cap_contact plus the current-source mount check.
Full routed hoses and the regenerated complete shell remain separate checks.
"""
from argparse import ArgumentParser
from pathlib import Path
import hashlib
import json
import sys
import time

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT/'hardware/manifold-layout'))
import enclosure_assembly as ea
import _clearing


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bounds(shape):
    b=shape.BoundingBox()
    return [[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]]


def run(pack, neighbors, output):
    started=time.monotonic();inputs={}
    def tracked(path):
        inputs[str(path.resolve())]=sha(path)
        return path
    rows=json.loads(tracked(pack/'frames.json').read_text())
    extra=json.loads(tracked(neighbors/'neighbors.json').read_text())
    solids={n:cq.Shape.importBrep(str(tracked(pack/r['brep']))) for n,r in rows.items()}
    if sha(pack/rows['foam-assembly']['brep'])!=extra['foam_brep_sha256']:
        raise ValueError('Native neighbor and pack foam placements differ')
    for n,r in extra['placed'].items():
        path=tracked(neighbors/r['brep'])
        if sha(path)!=r['sha256']:raise ValueError('Neighbor changed: '+n)
        solids[n]=cq.Shape.importBrep(str(path))
    pump=ea._lines._pump
    tracked(Path(pump.__file__));tracked(Path(__file__))
    tracked(pump.envelope.NATIVE)
    g=solids[pump.SCENE_KEY];parts=g.Solids();pb=g.BoundingBox()
    local=pump.suction()[0];world=rows[pump.SCENE_KEY]['ports']['suction'][0]
    origin=(world[0]+local[1],world[1]-local[0],world[2]-local[2])
    rebuilt,carry=ea.seat_body(pump.build(),(((0,0,1),pump.YAW),),
                             station=(pump.bearing_datum(),origin))
    if max(abs(a-b) for r,s in zip(bounds(g),bounds(rebuilt)) for a,b in zip(r,s))>1e-5:
        raise ValueError('Native pump does not match the current reference pose')
    # These small bodies use their actual current placement functions.
    spec=json.loads(tracked(ROOT/'hardware/manifold-layout/enclosure-box.json').read_text())
    pack_spec=spec['box']['pack'];plate=dict(zip(pack_spec['fields'],pack_spec['values']))['nameplate']
    for n,s,_color in ea.build_nameplate(tuple(plate['values'][:2])):solids[n]=s
    pan,_=ea.build_pan(solids['asse1022-assembly'],g,carry,None)
    solids['asse-drip-pan']=pan
    b=pan.BoundingBox()
    solids['pan-complete-west-withdrawal-envelope']=ea._boxed(-250,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax)
    readings=[]
    for name,s in solids.items():
        if name in (pump.SCENE_KEY,'foam-assembly'):continue
        b=s.BoundingBox();gap=_clearing.box_gap(pb,b)
        if gap>=1:
            readings.append({'neighbor':name,'bbox_clearance_lower_bound_mm':gap,'pass':True});continue
        near=[p for p in parts if _clearing.box_gap(p.BoundingBox(),b)<1]
        if not near:
            readings.append({'neighbor':name,'all_component_bbox_clearance_lower_bound_mm':1.,'pass':True});continue
        distance=min(p.distance(s) for p in near)
        volume=sum(p.intersect(s).Volume() for p in near if _clearing.box_gap(p.BoundingBox(),b)<1e-8)
        readings.append({'neighbor':name,'native_air_mm':distance,'native_overlap_mm3':volume,
                         'pass':distance>=1-1e-6 and volume<1e-6})
        print(name,readings[-1],flush=True)
    if any(sha(path)!=digest for path,digest in inputs.items()):raise RuntimeError('Native input changed')
    report={'scope':'Complete retained native pack and electronics/funnel neighbors plus current nameplate and pan placement. Cap bearing, actual routed hoses, and regenerated full shell are separate checks.',
            'inputs_sha256':inputs,'origin_mm':origin,'pump_bounds_mm':bounds(g),
            'pan_bounds_mm':bounds(pan),
            'pan_body_front_y_mm':b.ymin+ea._pan.PULL_FACE_Y_OVERHANG,
            'discharge_root_aft_y_mm':pump.discharge_shape(carry).BoundingBox().ymax,
            'readings':readings,'all_pass':all(r['pass'] for r in readings),
            'elapsed_seconds':time.monotonic()-started}
    output.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS' if report['all_pass'] else 'FAIL',len(readings),'neighbors',flush=True)
    if not report['all_pass']:raise SystemExit(1)


if __name__=='__main__':
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--pack',type=Path,required=True)
    parser.add_argument('--neighbors',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=HERE/'corrected-placement-check.json')
    args=parser.parse_args();run(args.pack,args.neighbors,args.output)
