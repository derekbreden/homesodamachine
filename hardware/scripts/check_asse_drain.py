"""Read the dedicated ASSE drain against the actual installed appliance bodies.

Read the explicitly bound physical fine model and the exact casing model in its
installed frame. The normal caller excludes wiring; the standalone installed
reader includes it under the existing tube exclusions. Connections share material
by design. This is nominal geometry evidence, not vent-flow qualification.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "hardware/manifold-layout/drain-clearance-check.json"
NAMES = ("asse-drain-adapter", "tube-drain-vent", "tube-fluid-18", "tube-fluid-28")
CONNECTED = {frozenset(pair) for pair in (
    ("asse-drain-adapter", "asse1022-assembly"),
    ("asse-drain-adapter", "tube-drain-vent"),
    ("tube-drain-vent", "bulkhead-drain"),
    ("tube-fluid-18", "valve-v-g"), ("tube-fluid-18", "flavor-reducer-v-g"), ("tube-fluid-18", "bulkhead-flavor-a"),
    ("tube-fluid-28", "valve-v-j"), ("tube-fluid-28", "flavor-reducer-v-j"), ("tube-fluid-28", "bulkhead-flavor-b"))}


def sha(path):
    with Path(path).open('rb')as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def centerline_radii(segments):
    """Actual circular radii and every polynomial Bezier curvature extremum."""
    import math
    import numpy as np
    from numpy.polynomial import Polynomial as P

    values = []
    for segment in segments:
        if segment['kind'] == 'line':
            continue
        if segment['kind'] == 'arc':
            a, b, c = np.asarray(segment['points_mm'], dtype=float)
            values.append(math.dist(a, b)*math.dist(b, c)*math.dist(c, a)
                          / (2*np.linalg.norm(np.cross(b-a, c-a))))
            continue
        q = np.asarray(segment['control_points_mm'], dtype=float)
        if q.ndim != 2 or q.shape[1] != 3 or len(q) < 2:
            raise ValueError('A Bezier centerline needs at least two 3D control points')
        degree = len(q)-1
        basis = [math.comb(degree,i)*P([0.,1.])**i*P([1.,-1.])**(degree-i)
                 for i in range(degree+1)]
        v = [sum(b*q[i,k] for i,b in enumerate(basis)).deriv() for k in range(3)]
        a = [p.deriv() for p in v]
        cross = [v[1]*a[2]-v[2]*a[1], v[2]*a[0]-v[0]*a[2],
                 v[0]*a[1]-v[1]*a[0]]
        speed2 = sum(p*p for p in v)
        cross2 = sum(p*p for p in cross)
        stationary = cross2.deriv()*speed2-3*cross2*speed2.deriv()
        candidates = [0., 1., *[float(t.real) for t in stationary.roots()
                                if abs(t.imag) < 1.e-8 and 0. <= t.real <= 1.]]
        radii = [0. if speed2(t) <= 1.e-16 else
                 math.sqrt(max(0., speed2(t))**3/cross2(t))
                 for t in candidates if cross2(t) > 1.e-16 or speed2(t) <= 1.e-16]
        if radii:
            values.append(min(radii))
    return sorted(set(round(r, 7) for r in values))



def _path(path):
    path=Path(path)
    return (ROOT/path).resolve()if not path.is_absolute()else path.resolve()


def _binding(path):
    path=_path(path)
    return {'path':str(path.relative_to(ROOT))if path.is_relative_to(ROOT)else str(path),
            'sha256':sha(path)}


def _names(path):
    import numpy as np
    with np.load(path,allow_pickle=False)as archive:
        return json.loads(bytes(archive['names']))


def _base(name):
    import re
    return re.sub(r'/\d+$','',name)


def _overlap(a,b):
    return not any(a[i+3]+1<b[i]or b[i+3]+1<a[i]for i in range(3))


def _rows(model,component_names=(),reading=None):
    import _assembly_model
    model=_path(model);binding=_binding(model)
    if reading is None:
        rows=_assembly_model.measure([_assembly_model.instance(model)],(),
                                    component_names=component_names)['bodies']
    else:
        if _path(reading['path'])!=model or reading['sha256']!=binding['sha256']:
            raise ValueError('Physical fine summaries belong to another model')
        rows=reading['bodies']
    if [row['name']for row in rows]!=_names(model):
        raise ValueError('Fine summary entry names differ from the bound model')
    return rows,binding


def _torus_records(path,entries):
    import numpy as np
    with np.load(path,allow_pickle=False)as archive:
        records=json.loads(bytes(archive['records']))
    return [{'entry_index':index,'qualified_name':name,'face_index':face,'record':record}
            for index,name in entries for face,record in enumerate(records[index])
            if isinstance(record,dict)and record.get('kind')=='TORUS']


def write(model, output=OUTPUT, *, envelope, names=NAMES, route_specs=None,
          physical_reading=None, aliases=None, wiring_model=None, obstacles=None,
          expected_envelope_bounds=None):
    """The existing drain question on explicit f64 models, through Rust queries.

    `aliases` maps a physical model's qualified component names to the exact
    logical names the caller measures. The casing remains its existing source
    model with an explicit installed frame; it is never a box approximation.
    """
    import math
    import numpy as np
    import _assembly_model

    model=_path(model);names=tuple(names);aliases=dict(aliases or {})
    if not names:raise ValueError('A drain reading needs a checked member')
    source_names=_names(model)
    unknown=set(aliases)-{_base(name)for name in source_names}
    if unknown:raise ValueError('Unknown qualified physical aliases: '+', '.join(sorted(unknown)))
    component_names=[name for name in source_names if aliases.get(_base(name),_base(name))in names]
    rows,physical_binding=_rows(model,component_names,physical_reading)
    paths={'physical':model};model_bindings={'physical':physical_binding}
    summaries={'physical':rows}
    if wiring_model is not None:
        wire_path=_path(wiring_model);wire_names=_names(wire_path)
        wire_rows,wire_binding=_rows(wire_path,[name for name in wire_names if _base(name)in names])
        paths['wiring']=wire_path;model_bindings['wiring']=wire_binding;summaries['wiring']=wire_rows
    envelope=dict(envelope);envelope_path=_path(envelope['path'])
    envelope_binding=_binding(envelope_path)
    if envelope.get('sha256')!=envelope_binding['sha256']:
        raise ValueError('The exact casing model differs from its declared binding')
    transform=np.asarray(envelope['transform'],dtype=float)
    if(transform.shape!=(3,4)or not np.isfinite(transform).all()or
       not np.allclose(transform[:,:3]@transform[:,:3].T,np.eye(3),atol=1e-10,rtol=0.)or
       abs(np.linalg.det(transform[:,:3])-1.)>1e-10):
        raise ValueError('The casing needs its explicit rigid source-to-world frame')
    envelope_instance=_assembly_model.instance(envelope_path,name='foam-assembly',transform=transform)
    envelope_rows=_assembly_model.measure([envelope_instance],(),
                                         component_names=['foam-assembly'])['bodies']
    envelope_names=_names(envelope_path)
    if len(envelope_rows)!=len(envelope_names):raise ValueError('Casing entry coverage differs')
    paths['envelope']=envelope_path
    model_bindings['envelope']={**envelope_binding,'transform':transform.tolist(),
                                'qualified_names':envelope_names}
    summaries['envelope']=envelope_rows
    groups={}
    for role,found in summaries.items():
        for index,row in enumerate(found):
            name=('foam-assembly'if role=='envelope'else
                  aliases.get(_base(row['name']),_base(row['name']))if role=='physical'else _base(row['name']))
            groups.setdefault(name,[]).append((role,index,row))
    missing=set(names)-set(groups)
    if missing:raise ValueError('Missing checked fine members: '+', '.join(sorted(missing)))
    bounds={name:[min(row['min'][i]for _role,_index,row in entries)for i in range(3)]+
                 [max(row['max'][i]for _role,_index,row in entries)for i in range(3)]
            for name,entries in groups.items()}
    if expected_envelope_bounds is not None and(len(expected_envelope_bounds)!=6 or any(
            abs(a-b)>1e-5 for a,b in zip(bounds['foam-assembly'],expected_envelope_bounds))):
        raise ValueError('The exact casing model/frame differs from the saved placement')
    selected=set(groups)if obstacles is None else set(obstacles)
    unknown=selected-set(groups)
    if unknown:raise ValueError('Unknown logical obstacles: '+', '.join(sorted(unknown)))
    candidates=[];checks={}
    for name in names:
        entries=groups[name]
        if any('components'not in row for _role,_index,row in entries):
            raise ValueError('Fine summaries lack the requested solid components: '+name)
        solids=sum(len(row['components'])for _role,_index,row in entries)
        valid=all(row['volume']>0 and row['triangles']>0 and
                  all(math.isfinite(value)for value in(*row['min'],*row['max'],row['volume']))
                  for _role,_index,row in entries)
        checks[name]={'valid':valid,'solids':solids,
                      'minimum_unconnected_gap_mm':1. if name=='tube-drain-vent'else 0.,'neighbors':[]}
        for other in groups:
            if other not in selected or other==name or frozenset((name,other))in CONNECTED:continue
            leaf=other.rsplit('/',1)[-1]
            wire_body=(leaf.startswith(('wire-','wiring-','terminal-'))and
                       not leaf.startswith(('wiring-junction-','terminal-J')))
            if name.startswith('tube-')and wire_body:continue
            if _overlap(bounds[name],bounds[other]):candidates.append((name,other))
    used={role:sorted({index for pair in candidates for name in pair
                      for r,index,_row in groups[name]if r==role})for role in paths}
    instances=[];slots={};offset=0
    for role,path in paths.items():
        if not used[role]:continue
        options={'indices':used[role]}
        if role=='envelope':options.update(name='foam-assembly',transform=transform)
        instances.append(_assembly_model.instance(path,**options))
        for index in used[role]:slots[role,index]=offset;offset+=1
    queries=[];owners=[]
    for name,other in candidates:
        # Existing pump occupied envelopes stay separate; the current mesh path
        # also distributes an ordinary compound intersection over its entries.
        for ra,ia,_row in groups[name]:
            for rb,ib,_row in groups[other]:
                pair={'a':slots[ra,ia],'b':slots[rb,ib]}
                queries.extend([{'kind':'gap',**pair},{'kind':'common',**pair}])
                owners.append((name,other))
    readings=_assembly_model.measure(instances,queries)['queries']if queries else []
    if len(readings)!=len(queries):raise ValueError('Drain fine query coverage differs')
    values={pair:{'gaps':[],'volumes':[]}for pair in candidates};errors=[]
    for owner,gap,common in zip(owners,readings[::2],readings[1::2]):
        if gap.get('kind')!='gap'or common.get('kind')!='common':raise ValueError('Drain query order differs')
        if 'error'in gap or 'error'in common:
            errors.append({'member':owner[0],'obstacle':owner[1],'error':gap.get('error')or common['error']});continue
        values[owner]['gaps'].append(gap['value']);values[owner]['volumes'].append(common['common']['raw']['volume_mm3'])
    for(name,other),value in values.items():
        if not value['gaps']:continue
        gap=min(value['gaps']);overlap=sum(value['volumes'])
        checks[name]['neighbors'].append({'name':other,'gap_mm':round(gap,7),'overlap_mm3':round(overlap,7)})
        print(name,other,f'gap {gap:.4f}; overlap {overlap:.6f}',flush=True)
    for name,row in checks.items():
        row['passed']=(row['valid']and row['solids']==1 and
            not any(error['member']==name for error in errors)and
            all(neighbor['overlap_mm3']<=1e-5 and
                neighbor['gap_mm']>=row['minimum_unconnected_gap_mm']-1e-6 for neighbor in row['neighbors']))
    radii={};surface_readings={}
    for name in set(names)&{'tube-drain-vent','tube-fluid-18','tube-fluid-28'}:
        spec=(route_specs or {}).get('drain-vent')if name=='tube-drain-vent'else None
        if spec:
            values=centerline_radii(spec['segments'])
        else:
            found=[]
            for role,path in paths.items():
                selected_entries=[(index,(envelope_names[index]if role=='envelope'else row['name']))
                                  for r,index,row in groups[name]if r==role]
                if selected_entries:found.extend(_torus_records(path,selected_entries))
            surface_readings[name]=found
            values=sorted({round(row['record']['R'],7)for row in found})
        radii[name]={'centerline_radii_mm':values}
        if name=='tube-drain-vent':
            radii[name].update(method=('Producer centerline; circular arcs and cubic curvature extrema'
                if spec else 'Authoritative fine toroidal face records'),
                passed=(bool(values)or bool(spec and spec['segments']))and(not values or min(values)>=25-1e-6))
        else:radii[name].update(stock_minimum_mm=25.,passed=bool(values)and min(values)>=25-1e-6)
    sources=[Path(__file__),ROOT/'hardware/manifold-layout/_drain.py',
             ROOT/'hardware/manifold-layout/enclosure_assembly.py',ROOT/'hardware/manifold-layout/_lines.py',
             ROOT/'hardware/manifold-layout/rear_plumbing.py',ROOT/'hardware/manifold-layout/above-core.json',
             ROOT/'hardware/reference/neofit-drain-bulkhead/neofit_drain_bulkhead.py',
             ROOT/'hardware/reference/asse1022-assembly/asse1022_assembly.py',
             ROOT/'hardware/printed-parts/asse-drain-adapter/asse_drain_adapter.py',
             ROOT/'hardware/scripts/_assembly_model.py',ROOT/'hardware/manifold-layout/enclosure_assembly.rs']
    population={name:[{'model':role,'entry_index':index,
        'qualified_name':envelope_names[index]if role=='envelope'else row['name']}
        for role,index,row in entries]for name,entries in groups.items()}
    for role,path in paths.items():
        if sha(path)!=model_bindings[role]['sha256']:raise ValueError('Fine drain inputs changed during queries')
    result={'scope':'Nominal authoritative fine model clearance of the direct TPU ASSE sleeve and dedicated drain against the complete installed assembly population, including cold-core bodies and retained flavor returns. Connected interfaces are excluded. Tubes exclude flexible conductors and jackets as obstacles; connector housings remain. The white 4 mm return requires at least 1 mm to every other unconnected body. Pump occupied envelopes are read per component. The sleeve expanded shape is an occupancy approximation. Hardware tolerances, zip-tie heads, actual bending, seals and vent performance are unmeasured.',
        'conservative_cold_core_envelope_included':True,'installed_body_count':len(groups),
        'checked_members':list(names),'checks':checks,'bend_radii':radii,
        'source_sha256':{str(path.relative_to(ROOT)):sha(path)for path in sources},
        'fine_inputs':{**model_bindings,'population':population,'aliases':aliases,
                       'bend_surface_records':surface_readings,
                       'route_specs_sha256':hashlib.sha256(json.dumps(route_specs or {},sort_keys=True).encode()).hexdigest()},
        'fine_query_count':len(queries),'candidate_pairs':[list(pair)for pair in candidates],
        'selected_obstacles':sorted(selected)if obstacles is not None else None,
        'errors':errors,'passed':not errors and all(row['passed']for row in checks.values())and
                                   all(row['passed']for row in radii.values())}
    if obstacles is not None:result['scope']='Selected named obstacles only. '+result['scope']
    if output is not None:Path(output).write_text(json.dumps(result,indent=2)+'\n')
    print('ASSE drain clearance',result['passed'],flush=True)
    return result


def main(argv=None):
    """Read the installed fine models and their exact saved casing placement."""
    import argparse
    import numpy as np
    import _realized
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aggregate',type=Path,default=ROOT/'hardware/manifold-layout/enclosure-assembly.step')
    parser.add_argument('--facts',type=Path,default=ROOT/'hardware/manifold-layout/enclosure-assembly.facts.json')
    parser.add_argument('--scorecard',type=Path,default=ROOT/'hardware/manifold-layout/enclosure-assembly.scorecard.json')
    parser.add_argument('--scene',type=Path,default=ROOT/'hardware/manifold-layout/enclosure-assembly.scene.npz')
    parser.add_argument('--manifest',type=Path,default=ROOT/'hardware/wiring/enclosure-wiring.json')
    parser.add_argument('--envelope-frame',type=Path,help='Explicit casing path/SHA/transform JSON when the scene has no fine drain binding')
    parser.add_argument('--only',nargs='+')
    parser.add_argument('--neighbors',nargs='+')
    parser.add_argument('--output',type=Path,default=OUTPUT)
    args=parser.parse_args(argv)
    saved=json.loads(args.facts.read_text())
    if(saved.get('card')!=_realized.code_digest(args.scorecard)or
       saved.get('step')!=_realized.code_digest(args.aggregate)):
        raise ValueError('The saved assembly, scorecard and placement facts disagree')
    model=Path(str(args.aggregate)+'.npz')
    if not any(name.startswith('cold-core/')for name in _names(model)):
        raise ValueError('The exported fine assembly contains no cold-core bodies')
    if args.envelope_frame:envelope=json.loads(args.envelope_frame.read_text())
    else:
        with np.load(args.scene,allow_pickle=False)as archive:document=json.loads(bytes(archive['document']))
        inputs=(document.get('drain')or {}).get('fine_inputs',{})
        if inputs.get('physical',{}).get('sha256')!=sha(model):
            raise ValueError('The scene lacks this physical model casing binding; supply --envelope-frame')
        envelope=inputs['envelope']
    manifest=json.loads(args.manifest.read_text())
    wiring=Path(str(args.manifest.with_suffix('.step'))+'.npz')
    if(manifest.get('physical_fine_model_sha256')!=sha(model)or
       manifest.get('wiring_fine_model_sha256')!=sha(wiring)):
        raise ValueError('The installed wiring fine manifest belongs to another model')
    expected=saved['bodies']['foam-assembly']
    result=write(model,args.output,envelope=envelope,wiring_model=wiring,
        names=args.only or NAMES,obstacles=args.neighbors,
        route_specs={row['id']:row for row in saved['native_runs']},expected_envelope_bounds=expected)
    result['serialized_input_sha256']={str(path):sha(path)for path in
        (args.aggregate,model,wiring,args.facts,args.scorecard,args.manifest,_path(envelope['path']))}
    result['placement_fact_bounds_mm']=expected
    result['placement_fact_bounds_sha256']=hashlib.sha256(json.dumps(expected,separators=(',',':')).encode()).hexdigest()
    result['foam_envelope_matches_saved_placement']=True
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    return 0 if result['passed']else 1


if __name__=='__main__':
    sys.exit(main())
