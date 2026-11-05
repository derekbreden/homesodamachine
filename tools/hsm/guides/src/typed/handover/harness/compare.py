"""Compare two labels' file hashes, step by step.

usage: compare.py <labelA> <labelB> [<genrule> ...]
"""
import json, sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
a, b = sys.argv[1], sys.argv[2]
names = sys.argv[3:] or sorted(p.stem for p in (RUN / 'results' / a).glob('*.json')
                               if not p.name.endswith('.trace.jsonl'))
total = differ_total = 0
for name in names:
    pa, pb = RUN / 'results' / a / f'{name}.json', RUN / 'results' / b / f'{name}.json'
    if not pa.exists() or not pb.exists():
        print(json.dumps({'step': name, 'missing': [str(p.name) for p in (pa, pb) if not p.exists()]}))
        continue
    fa, fb = json.loads(pa.read_text())['files'], json.loads(pb.read_text())['files']
    differ = sorted(k for k in set(fa) | set(fb) if fa.get(k) != fb.get(k))
    total += len(fa)
    differ_total += len(differ)
    print(json.dumps({'step': name, 'files': len(fa), 'differ': len(differ), 'first': differ[:8]}))
print(json.dumps({'files': total, 'differ': differ_total}))
