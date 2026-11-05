"""Compare two names probes: names, order and values per module.

usage: compare_names.py <before.json> <after.json> [module ...]
"""
import json, sys
a = json.load(open(sys.argv[1]))
b = json.load(open(sys.argv[2]))
mods = sys.argv[3:] or sorted(set(a) & set(b))
bad = 0
for m in mods:
    x, y = a.get(m), b.get(m)
    if x is None or y is None:
        print(f'{m}: missing in', 'before' if x is None else 'after'); bad += 1; continue
    if 'error' in y or 'error' in x:
        print(f'{m}: error', (x.get('error') or '')[:300], '|', (y.get('error') or '')[:600]); bad += 1; continue
    if x['names'] != y['names']:
        bad += 1
        sx, sy = set(x['names']), set(y['names'])
        print(f'{m}: names differ; only before {sorted(sx - sy)[:20]}; only after {sorted(sy - sx)[:20]}')
        if sx == sy:
            for i, (p, q) in enumerate(zip(x['names'], y['names'])):
                if p != q:
                    print(f'   first order difference at {i}: before {p} after {q}'); break
    for n in x['names']:
        if n not in y['values']:
            continue
        u, v = x['values'][n], y['values'][n]
        if n == '__file__' or (isinstance(u, dict) and isinstance(v, dict) and 'value' in u and 'value' in v
                and isinstance(u['value'], dict) and '$ref' in u['value'] and isinstance(v['value'], dict) and '$ref' in v['value']):
            continue
        if isinstance(u, dict) and isinstance(v, dict) and 'value' in u and 'value' in v and isinstance(u['value'], dict) and '$set' in u['value'] and isinstance(v['value'], dict) and '$set' in v['value']:
            if sorted(map(json.dumps, u['value']['$set'])) == sorted(map(json.dumps, v['value']['$set'])):
                continue
        if u != v:
            bad += 1
            print(f'{m}.{n}: before {json.dumps(u)[:300]}\n{" " * len(m + n)}   after  {json.dumps(v)[:300]}')
print('modules', len(mods), 'differences', bad)
