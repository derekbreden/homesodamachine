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
    """Read the existing drain question in Rust over explicit immutable models."""
    import _machine_checks
    result = _machine_checks.drain(model, envelope=envelope, names=names,
        route_specs=route_specs, physical_reading=physical_reading, aliases=aliases,
        wiring_model=wiring_model, obstacles=obstacles,
        expected_envelope_bounds=expected_envelope_bounds)
    if output is not None:
        Path(output).write_text(json.dumps(result, indent=2) + '\n')
    print('ASSE drain clearance', result['passed'], flush=True)
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
