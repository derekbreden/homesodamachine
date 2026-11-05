"""Join the type trace with the Python sources: one observed signature per compiled function.

usage: analyze_types.py TRACE_DIR OUT_DIR
Writes OUT_DIR/<module>.sigs.md (and all.json): each live function with its Python line,
the parameter types seen on every call, the return types seen, and the steps that ran it.
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
trace_dir, out_dir = sys.argv[1], sys.argv[2]
os.makedirs(out_dir, exist_ok=True)

# compiled bind site -> (module, function name, ordinal among same-named sites)
site_name = {}
for path in glob.glob(f'{COMPILED}/*.rs'):
    module = os.path.basename(path)[:-3]
    pending, current = None, '<lambda>'
    for n, line in enumerate(open(path), 1):
        opened = re.search(r'e\.set\("([^"]+)",\s*\{\s*$', line)
        if opened:
            pending = opened.group(1)
            continue
        if 'Val::function(move |' in line and 'bind(&outer' not in line:
            current, pending = (pending or '<lambda>'), None
        k = line.find('bind(&outer')
        if k < 0:
            continue
        names = re.findall(r'e\.set\("([^"]+)"', line[:k])
        site_name[(module, n)] = names[-1] if names else current
        current = '<lambda>'

# Python definitions per module: name -> [(qualname, line)]
pydefs = collections.defaultdict(lambda: collections.defaultdict(list))
for path in open(f'{RUN}/modules.txt').read().split():
    module = os.path.basename(path)[:-3]
    tree = ast.parse(open(f'{RUN}/py/{module}.py').read())

    def walk(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                q = f'{prefix}{child.name}'
                pydefs[module][child.name].append((q, child.lineno))
                if prefix and not prefix.endswith('.<locals>.'):
                    pydefs[module][prefix.rstrip('.') + '.' + child.name].append((q, child.lineno))
                walk(child, q + '.<locals>.')
            elif isinstance(child, ast.ClassDef):
                walk(child, f'{prefix}{child.name}.')
            else:
                walk(child, prefix)
    walk(tree, '')

sigs = collections.defaultdict(lambda: collections.defaultdict(set))   # site -> param -> types
rets = collections.defaultdict(set)
steps = collections.defaultdict(set)
for path in glob.glob(f'{trace_dir}/*.types.log'):
    step = re.sub(r'-\d+\.types\.log$', '', os.path.basename(path))
    for line in open(path, errors='replace'):
        parts = line.rstrip('\n').split('\t')
        if parts[0] == 'sig' and len(parts) >= 2:
            site = parts[1]
            steps[site].add(step)
            for item in (parts[2].split(' ') if len(parts) > 2 and parts[2] else []):
                name, _, t = item.partition('=')
                sigs[site][name].add(t)
        elif parts[0] == 'ret' and len(parts) == 3:
            rets[parts[1]].add(parts[2])

by_module = collections.defaultdict(list)
for site in sorted(set(sigs) | set(rets) | set(steps)):
    f, n = site.rsplit(':', 1)
    module = os.path.basename(f)[:-3]
    name = site_name.get((module, int(n)), f'?{n}')
    defs = pydefs[module].get(name, [])
    by_module[module].append({
        'site': site, 'name': name,
        'python': [f'{q}:{l}' for q, l in defs],
        'params': {p: sorted(t) for p, t in sigs[site].items()},
        'returns': sorted(rets[site]),
        'steps': sorted(steps[site]),
    })

json.dump(by_module, open(f'{out_dir}/all.json', 'w'), indent=1)
for module, rows in sorted(by_module.items()):
    with open(f'{out_dir}/{module}.sigs.md', 'w') as out:
        out.write(f'# {module}: observed signatures ({len(rows)} live compiled functions)\n\n')
        for r in sorted(rows, key=lambda r: int(r['site'].rsplit(':', 1)[1])):
            where = ', '.join(r['python']) or '?'
            out.write(f"## {r['name']}  (python {where}; compiled line {r['site'].rsplit(':', 1)[1]})\n")
            for p, t in r['params'].items():
                out.write(f"- `{p}`: {' | '.join(t)}\n")
            out.write(f"- returns: {' | '.join(r['returns']) or '?'}\n")
            out.write(f"- steps: {', '.join(r['steps'][:8])}{' …' if len(r['steps']) > 8 else ''}\n\n")
    print(module, len(rows))
