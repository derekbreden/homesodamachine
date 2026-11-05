import json, sys
from pathlib import Path
A, B, rel = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
limit = int(sys.argv[4]) if len(sys.argv) > 4 else 40
def load(root):
    text = (root / rel).read_bytes().replace(str(root.resolve()).encode(), b'<WORK>').decode()
    return json.loads(text)
a, b = load(A), load(B)
out = []
def walk(x, y, path):
    if len(out) >= limit: return
    if type(x) != type(y):
        out.append((path, repr(x)[:160], repr(y)[:160])); return
    if isinstance(x, dict):
        for k in list(dict.fromkeys([*x, *y])):
            if k not in x or k not in y: out.append((path + '/' + str(k), 'in a' if k in x else '', 'in b' if k in y else '')); continue
            walk(x[k], y[k], path + '/' + str(k))
    elif isinstance(x, list):
        if len(x) != len(y): out.append((path, 'len', len(x), len(y)))
        for i, (p, q) in enumerate(zip(x, y)): walk(p, q, f'{path}[{i}]')
    elif x != y:
        out.append((path, repr(x)[:160], repr(y)[:160]))
walk(a, b, '')
for o in out: print(o)
print('diffs shown', len(out))
