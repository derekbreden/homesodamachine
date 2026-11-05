"""CPU, wall and peak RSS of staged genrules, per machine-data binary: one warm-up run, then
`ROUNDS` measured runs, the variants interleaved round by round. Each run is a fresh clone of
the pristine work directory; its files are checked against the hashes saved in base-trees/.

usage: measure.py <out.jsonl> <target>[,<target>...] <label=program> [<label=program> ...]
   env: ROUNDS (default 3)
Appends one JSON line per run, then one summary line per target with each variant's medians.
"""
import json, os, statistics, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.argv = [sys.argv[0], *sys.argv[1:]]
out, targets, variants = Path(sys.argv[1]), sys.argv[2].split(','), [a.split('=', 1) for a in sys.argv[3:]]
rounds = int(os.environ.get('ROUNDS', '3'))

import importlib.util
spec = importlib.util.spec_from_file_location('cmp', HERE / 'compare.py')


def load(target):
    # compare.py runs on import; give it a harmless argv and keep its helpers.
    saved = sys.argv
    sys.argv = ['compare.py', str(HERE / 'steps'), target]
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.argv = saved
    return module


for target in targets:
    module = load(target)
    saved = json.loads((HERE / 'base-trees' / f'{target}.json').read_text())['tree']
    rows = {label: [] for label, _ in variants}
    for round_ in range(rounds + 1):
        for label, program in variants:
            files, run = module.run(f'measure-{label}', program)
            differ = sorted(k for k in set(saved) | set(files) if saved.get(k) != files.get(k))
            row = {'target': target, 'label': label, 'round': round_, **run, 'differ_count': len(differ),
                   'differ': differ[:10]}
            with out.open('a') as f:
                f.write(json.dumps(row) + '\n')
            if round_:
                rows[label].append(run)
    summary = {'target': target, 'summary': {
        label: {'cpu_median': statistics.median(r['cpu'] for r in runs),
                'wall_median': statistics.median(r['wall'] for r in runs),
                'maxrss_mb_max': max(r['maxrss_mb'] for r in runs),
                'cpu': [r['cpu'] for r in runs], 'wall': [r['wall'] for r in runs]}
        for label, runs in rows.items()}}
    with out.open('a') as f:
        f.write(json.dumps(summary) + '\n')
