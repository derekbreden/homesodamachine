#!/usr/bin/env python3
"""Compare the fluid-2 clearance guard without regenerating the assembly."""
import argparse
import ast
import copy
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace as NS

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())
SOURCE='hardware/manifold-layout/_lines.py'
OLD_REVISION='7aa2c76e98f59db6c35b661c77eb0e5b852eaeef'
OLD_SHA='1674cdc2971073826d7c25a6a759cd0d3a22b51f7cee059a99db9bea9f45307c'
NEW_SHA='25ebc25e36b3aa68e46c38f03061be3654b19c31e77d9fd76e6832008ee93cee'


def sha(data):return hashlib.sha256(data).hexdigest()
def tree(node):return ast.dump(node,include_attributes=False)
def same(a,b):return tree(a)==tree(b)
def function(module):return next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='_fluid_2')
def compiled(node,namespace):
    code=ast.fix_missing_locations(ast.Module(body=[copy.deepcopy(node)],type_ignores=[]))
    env=dict(namespace);exec(compile(code,SOURCE,'exec'),env)
    return env['_fluid_2']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pack-cache',type=Path,default=Path('/tmp/scanner-review/full-enclosure-current/route-pack'))
    parser.add_argument('--output',type=Path,default=HERE/'fluid-2-guard-equivalence.json')
    args=parser.parse_args()
    old=subprocess.check_output(['git','show',OLD_REVISION+':'+SOURCE],cwd=ROOT)
    new=(ROOT/SOURCE).read_bytes()
    assert sha(old)==OLD_SHA and sha(new)==NEW_SHA,'The named source pair changed'
    old_module,new_module=ast.parse(old),ast.parse(new)
    old_fn,new_fn=function(old_module),function(new_module)
    signature=copy.deepcopy(new_fn);signature.body=copy.deepcopy(old_fn.body)
    assert same(old_fn,signature),'The function signature or annotations changed'
    untouched=copy.deepcopy(new_module)
    untouched.body[untouched.body.index(function(untouched))]=copy.deepcopy(old_fn)
    assert same(old_module,untouched),'A second source region changed'
    old_i=next(i for i,n in enumerate(old_fn.body) if isinstance(n,ast.Assign) and tree(n.targets[0])=="Name(id='pump_gap', ctx=Store())")
    new_i=next(i for i,n in enumerate(new_fn.body) if isinstance(n,ast.Assign) and tree(n.targets[0])=="Name(id='tube', ctx=Store())")
    assert same(ast.Module(body=old_fn.body[:old_i],type_ignores=[]),ast.Module(body=new_fn.body[:new_i],type_ignores=[]))
    assert len(old_fn.body[old_i:])==3 and len(new_fn.body[new_i:])==3
    old_assign,old_guard,old_return=old_fn.body[old_i:]
    new_tube,new_guard,new_return=new_fn.body[new_i:]
    assert same(old_return,new_return) and isinstance(old_return.value,ast.Name) and old_return.value.id=='run'
    assert same(old_assign.value.func.value,new_tube.value)
    assert len(new_guard.body)==2 and not new_guard.orelse
    assert same(old_guard,new_guard.body[1]),'The exact near-case guard changed'
    rewritten=copy.deepcopy(new_guard.body[0]);rewritten.value.func.value=copy.deepcopy(new_tube.value)
    assert same(old_assign,rewritten),'The exact near-case distance changed'
    expected=ast.parse('pump_fore - tube.BoundingBox().ymax < _card.CLEARANCE_FLOOR - 1e-6',mode='eval').body
    assert same(new_guard.test,expected),'The bounding-plane condition changed'

    os.environ['HSM_NO_BUILD_LOCK']='1'
    sys.path[:0]=[str(ROOT/'hardware/manifold-layout'),str(ROOT/'hardware/scripts')]
    import cadquery as cq
    import _lines as lines
    import _routing as routing
    cache=args.pack_cache.resolve()
    frame_path=cache/'frames.json';pump_path=cache/'g-ganen-pump.brep'
    proof_path=HERE.parent/'routing-clearance/fluid18-current-pack.json'
    proof=json.loads(proof_path.read_text())
    inputs={str(p):sha(p.read_bytes()) for p in (frame_path,pump_path,proof_path)}
    assert proof['source_sha256'][SOURCE]==OLD_SHA
    for path in (frame_path,pump_path):
        assert inputs[str(path)]==proof['input_sha256'][str(path)],'Retained route input changed'
    records=json.loads(frame_path.read_text())
    needed=('flow-regulator','valve-v-a','valve-v-b','bulkhead-flavor-a')
    frames={name:routing.Frame(name,records[name]['ports'],NS(**records[name]['bbox'])) for name in needed}
    routing._frames.update(frames)
    pump=cq.Shape.importBrep(str(pump_path))
    assert pump.isValid()
    prefix=copy.deepcopy(old_fn);prefix.body=prefix.body[:old_i]+[old_return]
    before=compiled(prefix,vars(lines))(frames,{'g-ganen-pump':pump})
    # Only this one tube is constructed. The slow compound-distance call is absent.
    after=lines._fluid_2(frames,{'g-ganen-pump':pump})
    assert asdict(before)==asdict(after),'Returned geometry data changed'
    tube=routing.tube(after)
    assert tube.isValid() and len(tube.Solids())==1
    bb=tube.BoundingBox();pb=pump.BoundingBox()
    bound=pb.ymin-bb.ymax;floor=lines._card.CLEARANCE_FLOOR
    assert bound>=floor-1e-6,'This retained geometry does not take the proved fast path'

    cases=[]
    # Exact distances in these controlled valid-bound cases are >= their box bounds.
    samples=[('separated',2.,2.5,14.),('at floor',floor,floor,14.),
             ('within existing tolerance',floor-.5e-6,floor-.5e-6,14.),
             ('near but clear',.1,1.4,14.),('near and below floor',.1,.5,14.),
             ('overlapping boxes but clear',-4.,1.4,14.),
             ('overlapping boxes and collision',-4.,0.,14.),
             ('just below tolerance',floor-2e-6,floor-2e-6,14.),
             ('stock bend rejected',2.,2.5,13.9)]
    for name,box_gap,exact_gap,radius in samples:
        outcomes=[]
        for fn in (old_fn,new_fn):
            calls={'bent':0,'tube':0,'exact_distance':0,'bounding_box':0}
            run=NS(radii={1:radius},bend=14.)
            class Probe:
                def BoundingBox(self):
                    calls['bounding_box']+=1;return NS(ymax=-box_gap)
                def distance(self,_pump):
                    calls['exact_distance']+=1;return exact_gap
            class Routing:
                @staticmethod
                def bent(*a,**kw):
                    calls['bent']+=1;calls['constructor_args']=a;calls['constructor_keywords']=kw;return run
                @staticmethod
                def tube(got):
                    assert got is run;calls['tube']+=1;return Probe()
            env={**vars(lines),'R':Routing}
            try:
                result=compiled(fn,env)(frames,{'g-ganen-pump':NS(BoundingBox=lambda:NS(ymin=0.))})
                outcome='returned_identical_run' if result is run else 'wrong_return'
            except ValueError as exc:outcome=str(exc)
            outcomes.append({'outcome':outcome,'calls':calls})
        assert outcomes[0]['outcome']==outcomes[1]['outcome'],name
        assert outcomes[0]['calls'].get('constructor_args')==outcomes[1]['calls'].get('constructor_args')
        assert outcomes[0]['calls'].get('constructor_keywords')==outcomes[1]['calls'].get('constructor_keywords')
        for result in outcomes:
            result['calls'].pop('constructor_args',None);result['calls'].pop('constructor_keywords',None)
        cases.append({'case':name,'box_gap_mm':box_gap,'exact_gap_mm':exact_gap,'minimum_bend_mm':radius,
                      'old':outcomes[0],'new':outcomes[1],'same_outcome':True})
    assert all(c['new']['calls']['exact_distance']==1 for c in cases if c['box_gap_mm']<floor-1e-6 and c['minimum_bend_mm']>=14.)
    loaded={}
    for module in tuple(sys.modules.values()):
        raw=getattr(module,'__file__',None)
        if raw:
            p=Path(raw).resolve()
            if p.suffix=='.py' and p.is_relative_to(ROOT) and '/site-packages/' not in str(p):
                loaded[str(p.relative_to(ROOT))]=sha(p.read_bytes())
    assert sha((ROOT/SOURCE).read_bytes())==NEW_SHA
    assert all(sha(Path(p).read_bytes())==digest for p,digest in inputs.items())
    record={'status':'geometry_and_near_guard_equivalent','created_at_utc':datetime.now(timezone.utc).isoformat(),
        'old_revision':OLD_REVISION,'source_path':SOURCE,'old_sha256':OLD_SHA,'new_sha256':NEW_SHA,
        'reproducer_sha256':sha(Path(__file__).read_bytes()),'command':sys.argv,
        'ast':{'all_other_module_nodes_identical':True,'function_signature_and_geometry_prefix_identical':True,
               'geometry_prefix_sha256':sha(tree(ast.Module(body=old_fn.body[:old_i],type_ignores=[])).encode()),
               'tube_constructor_expression_identical':True,'tube_constructor_calls_per_valid_radius':1,
               'return_statement_identical':True,'near_distance_expression_identical':True,
               'near_guard_condition_and_error_identical':True,'bbox_condition':ast.unparse(new_guard.test)},
        'bound_proof':'For every pump point p and tube point t, p.y - t.y >= pump_bbox.ymin - tube_bbox.ymax. If that separation is at least the existing floor minus 1e-6, Euclidean separation is at least the same bound; otherwise the unchanged exact-distance guard executes.',
        'behavior_cases':cases,'input_sha256':inputs,'loaded_source_sha256':dict(sorted(loaded.items())),
        'retained_native_geometry':{'tube_brep_available':False,'tube_scope':'One fluid-2 tube reconstructed from the retained current port frames; no full CAD assembly or other route is built.',
            'old_geometry_prefix_and_new_returned_run_equal':True,'run':asdict(after),
            'pump_bbox_ymin_mm':pb.ymin,'tube_bbox_ymax_mm':bb.ymax,'proved_minimum_air_mm':bound,
            'clearance_floor_mm':floor,'tolerance_mm':1e-6,'fast_path_taken':True,
            'tube_valid':True,'tube_solids':1,'tube_volume_mm3':tube.Volume(),
            'exact_compound_distance_recomputed':False},
        'scope':'Only the named _lines.py source transition. Current geometry/slice receipt is not modified; unchanged geometry may retain its existing native/artifact evidence across this guard-only transition.',
        'full_assembly_regenerated':False,'print_released':False}
    args.output.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'status':record['status'],'old':OLD_SHA,'new':NEW_SHA,'behavior_cases':len(cases),
                      'minimum_proved_air_mm':bound,'output':str(args.output)},indent=2),flush=True)


if __name__=='__main__':main()
