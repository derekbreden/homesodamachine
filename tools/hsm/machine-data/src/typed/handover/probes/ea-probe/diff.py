"""usage: diff.py <a.jsonl> <b.jsonl> [width]  — the probe entries whose results differ."""
import json, sys
a = [json.loads(l) for l in open(sys.argv[1])]
b = [json.loads(l) for l in open(sys.argv[2])]
w = int(sys.argv[3]) if len(sys.argv) > 3 else 600
ka, kb = [d['k'] for d in a], [d['k'] for d in b]
if ka != kb:
    print('KEYS DIFFER', len(ka), len(kb))
    for i, (x, y) in enumerate(zip(ka, kb)):
        if x != y:
            print(' first at', i, x, '|', y)
            break
db = {}
for d in b:
    db.setdefault(d['k'], []).append(d['r'])
n = 0
seen = {}
for d in a:
    k = d['k']
    i = seen.get(k, 0)
    seen[k] = i + 1
    rb = db.get(k, [None] * (i + 1))
    other = rb[i] if i < len(rb) else None
    if d['r'] != other:
        n += 1
        print('==', k)
        print('  A', json.dumps(d['r'])[:w])
        print('  B', json.dumps(other)[:w])
print(n, 'differ of', len(a))
