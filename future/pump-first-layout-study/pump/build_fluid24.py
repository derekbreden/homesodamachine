"""Reservoir-B fill route around the reversed VK and its high return loop."""
from pathlib import Path
import sys, json, hashlib, math, argparse
import cadquery as cq

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
sys.path.insert(0, str(HERE))
import generate as G
sys.path.insert(0,str(STUDY))
from evidence_binding import content_sha256,manifest_content_sha256
from structure import proof_sources


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    sources=proof_sources.snapshot(__file__,G.__file__,G.baseline.__file__,
                                  ROOT/'hardware/manifold-layout/_lines.py')
    receipts=[]
    def publish(shape,path):
        if not args.check:
            shape.exportBrep(str(path));return
        received=cq.Shape.importBrep(str(path))
        missing=abs(shape.cut(received,tol=.0001).Volume(tol=1e-9))
        excess=abs(received.cut(shape,tol=.0001).Volume(tol=1e-9))
        volume=abs(received.Volume(tol=1e-9)-shape.Volume(tol=1e-9))
        area=abs(received.Area()-shape.Area())
        bounds_error=max(abs(a-b)for a,b in zip(G.bounds(shape),G.bounds(received)))
        passed=received.isValid() and len(received.Solids())==len(shape.Solids()) and max(missing,excess,volume,area)<.001 and bounds_error<1e-6
        receipts.append({'brep':str(path.relative_to(ROOT)),'missing_mm3':missing,'excess_mm3':excess,
                         'volume_error_mm3':volume,'area_error_mm2':area,'bounds_error_mm':bounds_error,'pass':passed})
        if not passed:raise ValueError('Received fixed R14 route differs from recipe '+str(path))
    native = G.baseline.read(['valve-v-i', 'cold-core/foam-cap-lid-top',
                              'tube-fluid-26', 'tube-fluid-24', 'tube-fluid-27'])
    models = dict(native)
    records = {}
    manifests = {}
    manifest_content={}
    for folder in ['pump', 'funnel', 'routing', 'structure', 'mounts']:
        path = STUDY / folder / 'candidate.json'
        raw=path.read_bytes()
        manifests[str(path.relative_to(ROOT))] = hashlib.sha256(raw).hexdigest()
        m = json.loads(raw)
        manifest_content[str(path.relative_to(ROOT))]=content_sha256(m)
        for name, rec in m['parts'].items():
            if name == 'tube-fluid-24':
                continue
            records[name] = rec
            models[name] = cq.Shape.importBrep(str(ROOT / rec['brep']))
    R = G.R
    R.frame('valve-v-i', native['valve-v-i'], {
        'outlet': ((-82.1, 105.29, 282.175), (0, 0, 1), 6.35)})
    R.frame('cold-core/foam-cap-lid-top', models['cold-core/foam-cap-lid-top'], {
        'reservoir-b-fill': ((-43.5, 233.3, 253.4), (0, 0, 1), 6.35)})
    pts = [
        (-82.1, 105.29 + 13.4 * math.tan(math.radians(2.9)), 295.575),
        (-82.1, 127, 295.575),
        (-94.8, 157, 295.575),
        (-94.8, 205.3, 295.575),
        (-94.8, 205.3, 267.4),
        (-43.5, 205.3, 267.4),
        (-43.5, 233.3, 267.4),
    ]
    note = ('Reservoir B fill keeps the fixed V-I upward attachment and its R14 crown, '
            'takes the west perimeter outside VK, descends before its raised plinth, then '
            'returns from the fore at Z267.4 through a true cap-normal R14 quarter into the fixed B-fill mouth. '
            'Every rounded corner retains R14.')
    R.BLOCKED.clear()
    run = R.bent('fluid-24', 'valve-v-i.outlet', *pts,
                 'cold-core/foam-cap-lid-top.reservoir-b-fill',
                 kind='fluid', bend=14, skew=(3, 38), note=note)
    shape = R.tube(run)
    path = ROOT / '.cache/pump-first-layout/pump/tube-fluid-24.brep'
    publish(shape,path)
    start = cq.Vector(*run.pts[0])
    axis = (cq.Vector(*run.pts[1]) - start).normalized()
    cutter = cq.Solid.sweep(cq.Wire.makeCircle(4.175, start, axis), [],
                           R.centreline(run), makeSolid=True, isFrenet=True)
    cutter_path = ROOT / '.cache/pump-first-layout/pump/tube-fluid-24-clearance-cutter.brep'
    publish(cutter,cutter_path)
    checks = [{'check': 'stock R14 at every actual bend',
               'pass': run.tightest >= 14 - 1e-6 and not R.BLOCKED,
               'minimum_radius_mm': run.tightest, 'blocked': dict(R.BLOCKED)}]
    rows = []
    inputs = {}
    box = G.bounds(shape)
    for name, other in models.items():
        if name in ['valve-v-i', 'cold-core/foam-cap-lid-top', 'tube-fluid-24']:
            continue
        b = G.bounds(other)
        if not all(box[i] <= b[i + 3] + 1.5 and b[i] <= box[i + 3] + 1.5 for i in range(3)):
            continue
        if name == 'enclosure-back-top':
            other = other.cut(cutter)
        gap = shape.distance(other)
        common = G.overlap(shape, other) if gap < 1e-6 else 0.
        passed = gap >= 1 - 1e-6 and common < .01
        rows.append({'other': name, 'gap_mm': gap, 'common_mm3': common, 'pass': passed})
        if name in records:
            inputs[name] = {'brep': records[name]['brep'], 'sha256': sha(ROOT / records[name]['brep'])}
        checks.append({'check': 'complete native route clears ' + name +
                       (' with declared matching flank relief' if name == 'enclosure-back-top' else ''),
                       'pass': passed, 'gap_mm': gap, 'common_mm3': common})
    # The source and first R14 crown are identical through the forward pack.
    # The tiny imported-source rounding difference is retained in the result.
    clip = cq.Solid.makeBox(240, 123, 80, cq.Vector(-120, 0, 240))
    original_fore = native['tube-fluid-24'].intersect(clip)
    new_fore = shape.intersect(clip)
    fore_change = abs(original_fore.cut(new_fore).Volume()) + abs(new_fore.cut(original_fore).Volume())
    checks.append({'check': 'native forward attachment and crown retained through Y123',
                   'pass': fore_change < .001, 'symmetric_difference_mm3': fore_change})
    rec = {'brep': str(path.relative_to(ROOT)), 'sha256': sha(path), 'role': 'water',
           'bounds_mm': G.bounds(shape), 'detail': note}
    result = {
        'parts': {'tube-fluid-24': rec}, 'replacement_names': ['tube-fluid-24'],
        'routes': {'fluid-24': {
            'from': run.frm, 'to': run.to, 'kind': run.kind,
            'points_mm': run.pts, 'diameter_mm': run.diam,
            'radii_mm': run.radii, 'tightest_mm': run.tightest,
            'developed_length_mm': run.length, 'note': note}},
        'checks': checks, 'pass': all(c['pass'] for c in checks),
        'clearance_cutters': {'tube-fluid-24': {
            'brep': str(cutter_path.relative_to(ROOT)), 'sha256': sha(cutter_path),
            'bounds_mm': G.bounds(cutter), 'radial_air_mm': 1,
            'nominal_flank_stock_remaining_mm': 107.5 + G.bounds(cutter)[0],
            'scope': 'Reorganized west flank above the cold-core lid only; preserve fixed conduit mouths.'}},
        'native_clearances': rows, 'native_inputs': inputs,
        'source_sha256': {'baseline': G.baseline.prepare()['sha256'],
                          'hardware/manifold-layout/_lines.py': sha(ROOT / 'hardware/manifold-layout/_lines.py'),
                          str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))},
        'manifest_sha256': manifests,
        'manifest_content_sha256':manifest_content,
        'source_inputs':sources,
        'source_drift':proof_sources.changed(sources)+[
            name for name,record in inputs.items() if sha(ROOT/record['brep'])!=record['sha256']],
        'manifest_drift':[p for p,h in manifest_content.items() if manifest_content_sha256(ROOT/p)!=h],
        'received_native_checks':receipts,
        'qualification_limits': ['Exact nominal stock radius and complete swept occupancy are checked. Tube memory, appliance vibration, installation tolerances and attachment strength require physical qualification.'],
    }
    result['pass']=result['pass'] and all(r['pass']for r in receipts) and not result['source_drift'] and not result['manifest_drift']
    (HERE / 'fluid24-candidate.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'pass': result['pass'], 'checks': len(checks),
                      'length_mm': run.length, 'failed': [c for c in checks if not c['pass']]}), flush=True)


if __name__ == '__main__':
    main()
