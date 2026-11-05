"""Draft Rust signatures for one module's functions from the observed types, one table per part.

usage: sig_drafts.py <module> <functions.json> <out.md>
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict

R = '/Users/derekbredensteiner/Developer/homesodamachine/.cache/runs/typed-enclosure-202611041700'
module, fpath, out = sys.argv[1], sys.argv[2], sys.argv[3]
meta = json.load(open(fpath))
sigs = json.load(open(f'{R}/sigs/all.json')).get(module, [])
by_name = defaultdict(list)
for r in sigs:
    by_name[r['name']].append(r)


def split(s):
    """Top-level comma split of a type list."""
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch in '([{':
            depth += 1
        elif ch in ')]}':
            depth -= 1
        if ch == ',' and depth == 0:
            out.append(cur)
            cur = ''
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out


def rust(t, ret=False):
    t = t.strip()
    simple = {'F': 'f64', 'I': 'i64', 'B': 'bool', 'S': 'String' if ret else '&str', 'N': '()'}
    if t in simple:
        return simple[t]
    if t.startswith('R:'):
        k = t[2:]
        if k in ('_Shape', '_ReadingShape'):
            return 'Solid'
        if k in ('dict', 'list', 'set'):
            return 'Val'
        return k
    m = re.fullmatch(r'T(\d+)\[(.*)\]', t)
    if m:
        return f'[{rust(m.group(2), ret)}; {m.group(1)}]'
    if t.startswith('T(') and t.endswith(')'):
        items = split(t[2:-1])
        rs = [rust(x, ret) for x in items]
        if len(set(rs)) == 1 and len(rs) >= 3:
            return f'[{rs[0]}; {len(rs)}]'
        return '(' + ', '.join(rs) + (',)' if len(rs) == 1 else ')')
    if t == 'T()':
        return 'Tup<_>'
    if t.startswith('L[') and t.endswith(']'):
        inner = t[2:-1]
        return f'Vec<{rust(inner, ret) if inner else "_"}>'
    if t.startswith('D{'):
        return 'struct? ' + t[:80]
    return '? ' + t[:60]


def union(ts, ret=False):
    ts = sorted(set(ts))
    if not ts:
        return '?'
    if set(ts) <= {'F', 'I'} and len(ts) == 2:
        return 'Num'
    if 'N' in ts and len(ts) == 2:
        other = [t for t in ts if t != 'N'][0]
        return f'Option<{rust(other, ret)}>'
    rs = sorted({rust(t, ret) for t in ts})
    return rs[0] if len(rs) == 1 else ' | '.join(rs)


external = defaultdict(set)
for path in glob.glob(f'{R}/py/*.py'):
    other = os.path.basename(path)[:-3]
    if other == module:
        continue
    for name in re.findall(r'\b(?:shell|enclosure|_shell)\.([A-Za-z_][A-Za-z0-9_]*)', open(path).read()):
        external[name].add(other)
lines = [f'# {module}: draft signatures', '',
         'From the observed types (`$R/sigs/all.json`) over every traced step. `?` marks a parameter no step',
         'exercised; `Solid` is the graph API\'s solid; `Num` an int-or-float; a struct name is a namedtuple.',
         'A draft: read the Python before taking one.', '']
parts = sorted({f['part'] for f in meta['functions']})
for p in parts:
    lines += [f'## p{p}', '']
    for f in sorted((f for f in meta['functions'] if f['part'] == p), key=lambda f: f['py'][0]):
        rs = by_name.get(f['name'], [])
        params = defaultdict(list)
        returns, steps = [], set()
        for r in rs:
            for k, v in r['params'].items():
                params[k] += v
            returns += r['returns']
            steps |= set(r['steps'])
        args = []
        for a in f['params'] + f['kwonly']:
            d = f['defaults'].get(a, f['kwdefaults'].get(a))
            args.append(f'{a}: {union(params.get(a, []))}' + (f' = {d}' if d is not None else ''))
        if f['vararg']:
            args.append(f'*{f["vararg"]}')
        if f['kwarg']:
            args.append(f'**{f["kwarg"]}')
        ret = union(returns, True)
        callers = sorted({g['part'] for g in meta['functions'] if f['name'] in g['calls']})
        tail = f'steps: {", ".join(sorted(steps))}' if steps else 'NOT EXERCISED'
        ext = f'; read by {", ".join(sorted(external[f["name"]]))}' if external.get(f['name']) else ''
        slots = f'; slots: {", ".join(f["slots"])}' if f['slots'] else ''
        lines.append(f'- `{f["name"]}({", ".join(args)}) -> {ret}` (py {f["py"][0]}; called from parts {callers}{ext}{slots}; {tail})')
    lines.append('')
open(out, 'w').write('\n'.join(lines))
print('wrote', out)
