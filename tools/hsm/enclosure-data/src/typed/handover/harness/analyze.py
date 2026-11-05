"""Summarize the trace: live compiled functions per module, the Python-facing surface,
module sets, external modules and callback members.

usage: analyze.py TRACE_DIR OUT_JSON
"""
import ast
import collections
import glob
import json
import os
import re
import sys

REPO = '/Users/derekbredensteiner/Developer/homesodamachine'
RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPILED = f'{REPO}/tools/hsm/enclosure-data/src/compiled'
trace_dir, out_path = sys.argv[1], sys.argv[2]

# compiled line -> function name
site_name = {}
for path in glob.glob(f'{COMPILED}/*.rs'):
    module = os.path.basename(path)[:-3]
    for n, line in enumerate(open(path), 1):
        k = line.find('bind(&outer')
        if k < 0:
            continue
        head = line[:k]
        names = re.findall(r'e\.set\("([^"]+)"', head)
        site_name[(module, n)] = names[-1] if names else '<lambda>'

live = collections.defaultdict(lambda: collections.defaultdict(set))   # module -> name -> steps
reqs = collections.defaultdict(lambda: collections.defaultdict(set))   # (action module path) -> origin -> steps
members = collections.defaultdict(set)
exts = collections.defaultdict(set)
cbs = collections.Counter()
ops = collections.defaultdict(set)
natives = collections.defaultdict(set)
cad = {}
steps = set()
for path in glob.glob(f'{trace_dir}/*.log'):
    base = os.path.basename(path)
    step = re.sub(r'-\d+\.(py\.log|cb\.log|log)$', '', base)
    steps.add(step)
    for line in open(path, errors='replace'):
        parts = line.rstrip('\n').split('\t')
        kind = parts[0]
        if base.endswith('.py.log'):
            if kind == 'send':
                _, origin, action, module, p, result = parts
                reqs[(action, module, p)][origin].add(step)
            elif kind == 'op':
                ops[parts[2]].add((parts[1], step))
            elif kind == 'native':
                natives[(parts[2], parts[3], parts[4])].add((parts[1], step))
            elif kind == 'cadquery':
                cad[step] = parts[1:]
        elif base.endswith('.cb.log'):
            cbs[(parts[1], parts[2], parts[3])] += 1
        else:
            if kind == 'fn':
                f, n = parts[1].rsplit(':', 1)
                module = os.path.basename(f)[:-3]
                name = site_name.get((module, int(n)), f'?{n}')
                live[module][name].add(step)
            elif kind == 'ext':
                exts[parts[1]].add(step)
            elif kind == 'member':
                members[parts[1]].add(step)
            elif kind == 'req':
                pass

total_sites = collections.Counter(m for (m, _n) in site_name)
summary = {
    'steps': sorted(steps),
    'cadquery': cad,
    'live': {m: {n: sorted(s) for n, s in sorted(v.items())} for m, v in sorted(live.items())},
    'live_counts': {m: [len(v), total_sites[m]] for m, v in sorted(live.items())},
    'dead_modules': sorted(set(total_sites) - set(live)),
    'requests': [
        {'action': a, 'module': m, 'path': p,
         'origins': {o: sorted(s) for o, s in sorted(v.items())}}
        for (a, m, p), v in sorted(reqs.items())
    ],
    'ops': {k: sorted(v) for k, v in sorted(ops.items())},
    'natives': [{'op': k[0], 'label': k[1], 'name': k[2], 'origins': sorted(v)} for k, v in sorted(natives.items())],
    'ext': {k: sorted(v) for k, v in sorted(exts.items())},
    'members': {k: sorted(v) for k, v in sorted(members.items())},
    'callbacks': [list(k) + [n] for k, n in cbs.most_common()],
}
json.dump(summary, open(out_path, 'w'), indent=1)
print('steps', len(steps))
for m, (a, b) in summary['live_counts'].items():
    print(f'{m:32s} {a:4d}/{b:4d} live')
print('dead modules:', summary['dead_modules'])
print('cadquery states:', collections.Counter(tuple(v) for v in cad.values()))
