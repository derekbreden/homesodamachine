"""Native clearance of both pump hoses and their adjacent reservoir fill route.

Regenerate only these three routes from source. Other routes and bodies come
from the explicitly supplied retained native capture. No production export runs.
"""
from argparse import ArgumentParser
from pathlib import Path
import ast
import hashlib
import json
import math
import sys
import time

import cadquery as cq

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'hardware/manifold-layout'))
import _lines as lines
import _routing as routing
import _clearing as clearing
import enclosure_assembly as assembly


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def owned_source():
    names={'_water_6','_water_7','_fluid_14','_fill_a_lane_y','_fill_a_cap_z','_fill_a_turn_y',
           'FILL_A_HOSE_DROP','FILL_A_HOSE_FALL_RUN','HOSE_BEND','BARB_SKEW','TUBE_BEND',
           'FILL_A_VALVE_DROP','FILL_A_VALVE_RETURN_RUN','FILL_A_BEARING_LEAD',
           'FILL_A_LANE_Z','FILL_A_GATE_LEAD','FILL_A_LANE_RUN','FILL_A_FALL_RUN','LANE_CLEAR'}
    source=Path(lines.__file__).read_text();tree=ast.parse(source)
    chosen=[]
    for node in tree.body:
        labels={node.name} if isinstance(node,(ast.FunctionDef,ast.ClassDef)) else (
            {target.id for target in node.targets if isinstance(target,ast.Name)}
            if isinstance(node,ast.Assign) else set())
        if labels & names:chosen.append(ast.dump(node,include_attributes=False))
    return hashlib.sha256('\n'.join(chosen).encode()).hexdigest()


def run(pack, neighbors, output, native_out):
    started=time.monotonic();inputs={}
    def tracked(path):
        inputs[str(path.resolve())]=sha(path);return path
    records=json.loads(tracked(pack/'frames.json').read_text())
    extra=json.loads(tracked(neighbors/'neighbors.json').read_text())
    solids={n:cq.Shape.importBrep(str(tracked(pack/r['brep']))) for n,r in records.items()}
    if sha(pack/records['foam-assembly']['brep'])!=extra['foam_brep_sha256']:
        raise ValueError('Different native foam placements in route and neighbor captures')
    frames={n:routing.frame(n,solids[n],r['ports']) for n,r in records.items() if 'ports' in r}
    for n,r in extra['placed'].items():
        p=tracked(neighbors/r['brep'])
        if sha(p)!=r['sha256']:raise ValueError('Native neighbor changed: '+n)
        solids[n]=cq.Shape.importBrep(str(p))
    route_rows=json.loads(tracked(pack/'routes.json').read_text())
    others={n:cq.Shape.importBrep(str(tracked(pack/r['brep']))) for n,r in route_rows.items()
            if n not in ('water-6','water-7','fluid-14')}
    owned_before=owned_source();lines_before=sha(lines.__file__)
    source_paths=[Path(__file__),Path(routing.__file__),Path(lines._cc.__file__),Path(lines._pump.__file__)]
    sources={str(p.relative_to(ROOT)):sha(p) for p in source_paths}
    routing.BLOCKED.clear()
    runs=[lines._water_6(frames),lines._water_7(frames),lines._fluid_14(frames,solids)]
    native={r.id:routing.tube(r) for r in runs}
    reports=[]
    for r in runs:
        tube=native[r.id];bb=tube.BoundingBox();checks=[]
        targets={**solids,**{'tube-'+n:s for n,s in {**others,**native}.items() if n!=r.id}}
        for name,shape in targets.items():
            if name=='stub-'+r.id:continue
            required=0. if name in (r.frm.split('.')[0],r.to.split('.')[0]) else 1.
            gap=clearing.box_gap(bb,shape.BoundingBox())
            if gap>=1.:
                checks.append({'neighbor':name,'bbox_clearance_lower_bound_mm':gap,'pass':True});continue
            near=[s for s in shape.Solids() if clearing.box_gap(bb,s.BoundingBox())<1.]
            if not near:
                checks.append({'neighbor':name,'all_component_bbox_clearance_lower_bound_mm':1.,'pass':True});continue
            distance=min(tube.distance(s) for s in near)
            volume=sum(tube.intersect(s).Volume() for s in near if clearing.box_gap(bb,s.BoundingBox())<1e-8)
            passed=distance>=required-1e-6 and volume<1e-5
            checks.append({'neighbor':name,'native_air_mm':distance,'native_overlap_mm3':volume,
                           'required_air_mm':required,'pass':passed})
            print(r.id,name,distance,volume,'PASS' if passed else 'FAIL',flush=True)
        exit_skew=routing.leg_skew(r.pts[0],r.pts[1],frames[r.frm.split('.')[0]].normal(r.frm.split('.')[1]))
        entry_skew=routing.leg_skew(r.pts[-2],r.pts[-1],tuple(-x for x in frames[r.to.split('.')[0]].normal(r.to.split('.')[1])))
        minimum=lines.TUBE_BEND if r.id=='fluid-14' else lines.HOSE_BEND
        reports.append({'id':r.id,'waypoints_mm':r.pts,'radii_mm':r.radii,'minimum_radius_mm':r.tightest,
                        'required_radius_mm':minimum,'exit_skew_degrees':exit_skew,'entry_skew_degrees':entry_skew,
                        'native_valid':tube.isValid(),'neighbors':checks,
                        'pass':tube.isValid() and r.tightest>=minimum-1e-6 and all(c['pass'] for c in checks)})
    # Read the complete fluid-14 bearing interval back from the actual cap frame.
    fm=frames['foam-assembly'];draw=fm.at('reservoir-a')
    local=lines._cc.cap_conduits['reservoir-a'];anchor=lines._cc.cap_anchors['fluid-14']
    axis=(draw[0]+anchor.centre[1]-local[1],draw[1]+local[0]-anchor.centre[0],lines._fill_a_cap_z(frames))
    r=next(r for r in runs if r.id=='fluid-14');half=lines._cc.cap_anchor_len/2
    bearing=None
    for i,(p,q) in enumerate(zip(r.pts,r.pts[1:])):
        if assembly._on_leg(axis,p,q):
            tangents={j:r.radii[j]*math.tan(math.radians(turn)/2) for j,turn,*_ in r.bends}
            ends=(p[1]+tangents.get(i,0),q[1]-tangents.get(i+1,0))
            bearing={'axis_mm':axis,'required_interval_y_mm':[axis[1]-half,axis[1]+half],
                     'actual_straight_interval_y_mm':ends,
                     'pass':ends[0]<=axis[1]-half and ends[1]>=axis[1]+half};break
    if bearing is None:raise ValueError('Fluid-14 misses its cap bearing')
    if owned_before!=owned_source():raise RuntimeError('Owned route source changed')
    if sources!={str(p.relative_to(ROOT)):sha(p) for p in source_paths}:raise RuntimeError('Route dependency changed')
    if any(sha(p)!=digest for p,digest in inputs.items()):raise RuntimeError('Native capture changed')
    passed=all(r['pass'] for r in reports) and bearing['pass'] and not routing.BLOCKED
    native_out.mkdir(parents=True,exist_ok=True)
    exported={}
    for name,shape in native.items():
        path=native_out/('tube-'+name+'.brep');shape.exportBrep(str(path));exported[name]={'path':str(path),'sha256':sha(path)}
    report={'scope':'Current source water-6, water-7 and fluid-14 against every supplied native body and route. Full regenerated shell and any subsequently revised other routes are separate checks.',
            'inputs_sha256':inputs,'source_sha256':sources,'owned_lines_ast_sha256':owned_before,
            'lines_file_sha256_at_start':lines_before,'lines_file_sha256_at_end':sha(lines.__file__),
            'routes':reports,'complete_fluid14_cap_bearing':bearing,'blocked':routing.BLOCKED,
            'native_outputs':exported,'all_pass':passed,'elapsed_seconds':time.monotonic()-started}
    output.write_text(json.dumps(report,indent=2)+'\n')
    print('ALL PASS',passed,flush=True)
    if not passed:raise SystemExit(1)


if __name__=='__main__':
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--pack',type=Path,required=True);parser.add_argument('--neighbors',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=HERE/'corrected-pump-routes-check.json')
    parser.add_argument('--native-out',type=Path,required=True)
    args=parser.parse_args();run(args.pack,args.neighbors,args.output,args.native_out)
