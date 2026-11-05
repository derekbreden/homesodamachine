"""The namespace check: one module's names, in order, and what each holds, from a candidate
enclosure-data binary against the generated (baseline) binary.

usage: names.py <module>[,<module>...] <binary> [--against <binary>]
Runs the probe in a clone of the enclosure step's staged inputs. Prints the differences and
exits 1 when there are any. Values are compared by type and, for data, by value (repr).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RUN = Path(__file__).resolve().parent
REPO = Path('/Users/derekbredensteiner/Developer/homesodamachine')
PY = REPO / 'tools/cad-venv/bin/python'
ap = argparse.ArgumentParser()
ap.add_argument('modules')
ap.add_argument('binary')
ap.add_argument('--against', default=str(RUN / 'bin/enclosure-data.baseline'))
ap.add_argument('--save', help='write both probes here (generated.json, typed.json)')
args = ap.parse_args()


def probe(binary, tag):
    pins = json.load(open(RUN / 'pins-baseline.json'))
    pins['workers'] = {'enclosure-data': os.path.abspath(binary)}
    work = RUN / 'work' / f'names.{tag}.{os.getpid()}'
    shutil.rmtree(work, ignore_errors=True)
    subprocess.run(['cp', '-cR', str(RUN / 'stage/enclosure'), str(work)], check=True)
    spec = work / '.pins.json'
    spec.write_text(json.dumps(pins))
    out = work / '.names.json'
    env = {**os.environ, 'HSM_REPO_ROOT': str(work), 'HSM_INPUT_DIGEST': 'probe',
           'HSM_WORKSPACE': str(REPO), 'HSM_PIN_SPEC': str(spec), 'HSM_NO_REALIZED_CACHE': '1'}
    r = subprocess.run([str(PY), str(RUN / 'harness/run_step.py'),
                        str(RUN / 'harness/probe_names.py'), args.modules, str(out)],
                       cwd=work, env=env, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-3000:], file=sys.stderr)
        sys.exit(2)
    data = json.load(open(out))
    shutil.rmtree(work, ignore_errors=True)
    return data


def canonical(module):
    """The probe with each `$ref` id renumbered in order of first appearance, so two runs compare by
    which values share an object rather than by the ids the worker happened to assign."""
    ids = {}

    def walk(v):
        if isinstance(v, dict):
            if set(v) == {'$ref'}:
                return {'$ref': ids.setdefault(v['$ref'], len(ids))}
            return {k: walk(x) for k, x in v.items()}
        if isinstance(v, list):
            return [walk(x) for x in v]
        return v
    if 'values' in module:
        module = {**module, 'values': {n: walk(module['values'][n]) for n in module['names']}}
    return module


base = probe(args.against, 'base')
cand = probe(args.binary, 'cand')
if args.save:
    os.makedirs(args.save, exist_ok=True)
    json.dump(base, open(os.path.join(args.save, 'generated.json'), 'w'), indent=1)
    json.dump(cand, open(os.path.join(args.save, 'typed.json'), 'w'), indent=1)
total = 0
for m in args.modules.split(','):
    bad = 0
    b, c = canonical(base.get(m, {})), canonical(cand.get(m, {}))
    if 'error' in b or 'error' in c:
        print(m, 'error', b.get('error'), c.get('error'))
        total += 1
        continue
    if b['names'] != c['names']:
        bad += 1
        print(m, 'names differ')
        print('  generated only:', [n for n in b['names'] if n not in c['names']])
        print('  typed only:    ', [n for n in c['names'] if n not in b['names']])
        common = [n for n in b['names'] if n in c['names']]
        if [n for n in c['names'] if n in common] != common:
            print('  order differs')
    for n in b['names']:
        if n in c['values'] and json.dumps(b['values'][n], sort_keys=True, default=repr) != json.dumps(c['values'][n], sort_keys=True, default=repr):
            bad += 1
            print(m, n, 'generated', json.dumps(b['values'][n], default=repr)[:300])
            print(' ' * len(m), n, 'typed    ', json.dumps(c['values'][n], default=repr)[:300])
    print(m, len(b['names']), 'names', 'match' if not bad else 'DIFFER')
    total += bad
sys.exit(1 if total else 0)
