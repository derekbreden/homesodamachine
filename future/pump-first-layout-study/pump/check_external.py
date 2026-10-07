"""Hash-bound external contacts of the final pump, source and B-fill module."""
from pathlib import Path
import hashlib, itertools, json, sys, time
import cadquery as cq

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
sys.path.insert(0, str(STUDY))
import audit
from evidence_binding import content_sha256,manifest_content_sha256
from structure import proof_sources


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    sources=proof_sources.snapshot(__file__)
    start = time.time()
    models, records, _, mates, inputs = audit.collect()
    extra = ['routing/co2-candidate.json', 'mounts/check-tee-candidate.json',
             'mounts/needle-candidate.json', 'mounts/wr-candidate.json',
             'wiring/control-reserves.json', 'wiring/control-fanouts-check.json']
    for rel in extra:
        path = STUDY/rel
        if not path.exists():
            continue
        m = json.loads(path.read_text())
        inputs[str(path.relative_to(ROOT))] = sha(path)
        inputs.content_sha256[str(path.relative_to(ROOT))]=content_sha256(m)
        for n, r in m.get('parts', {}).items():
            records[n] = r
            models[n] = cq.Shape.importBrep(str(ROOT/r['brep']))
        for pair in m.get('intended_contacts', []):
            mates[frozenset(pair)] = 'declared mounting or mating interface'
    own = set(json.loads((HERE/'candidate.json').read_text())['parts'])
    own.update(json.loads((HERE/'fluid24-candidate.json').read_text())['parts'])
    # Only external contacts belong to this audit. The producer's local checks
    # qualify its exact foot stacks, seated barbs and internal stock.
    boxes = {n: audit.bbox(s) for n, s in models.items()}
    pairs = [(a, b) for a, b in itertools.combinations(models, 2)
             if ((a in own) != (b in own)) and audit.broad(boxes[a], boxes[b], 1)]
    native = {n: {'brep': records[n]['brep'], 'sha256': sha(ROOT/records[n]['brep']),
                  'valid': s.isValid(), 'solids': len(s.Solids())}
              for n, s in models.items()}
    rows, errors = [], []
    for i, (a, b) in enumerate(pairs):
        gap = models[a].distance(models[b])
        if gap >= 1-1e-6:
            continue
        why = audit.intended(a, b, records, mates)
        try:
            common = audit.common(models[a], models[b], why == 'declared joined print root') if gap < 1e-6 else 0.
        except RuntimeError as error:
            errors.append({'a': a, 'b': b, 'error': str(error)})
            continue
        r = {'a': a, 'b': b, 'gap_mm': gap, 'common_mm3': common, 'intended': why}
        rows.append(r)
        if common > .01 and why is None:
            print('INTERFERENCE', json.dumps(r), flush=True)
        if i % 100 == 0:
            print('external progress', i, len(pairs), flush=True)
    blockers = [r for r in rows if r['common_mm3'] > .01 and r['intended'] is None]
    invalid = [n for n, r in native.items() if not r['valid']]
    drift = [n for n, r in native.items() if sha(ROOT/r['brep']) != r['sha256']]+proof_sources.changed(sources)
    report = {'pass': not blockers and not errors and not invalid and not drift,
              'targets': sorted(own), 'native_pairs': len(pairs), 'close_pairs': rows,
              'blockers': blockers, 'operation_errors': errors, 'invalid_parts': invalid,
              'native_inputs': native, 'manifest_sha256': inputs,
              'manifest_content_sha256':inputs.content_sha256,'source_drift': drift,
              'source_inputs':sources,
              'elapsed_seconds': time.time()-start,
              'scope': 'Exact final seated external occupancy of the pump, source valves, source connections, mounts, water5/6/7 and B-fill tube. Native source controls are obstacles. Factory motions, tolerance, loads and flexible compliance have separate scope.'}
    report['manifest_drift']=[n for n,h in inputs.content_sha256.items()if manifest_content_sha256(ROOT/n)!=h]
    report['pass']=report['pass']and not report['manifest_drift']
    (HERE/'external-native-check.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'pass': report['pass'], 'blockers': len(blockers), 'drift': len(drift)}), flush=True)


if __name__ == '__main__':
    main()
