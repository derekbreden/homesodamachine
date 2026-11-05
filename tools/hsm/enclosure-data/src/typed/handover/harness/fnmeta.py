"""Per-function map of one enclosure module for the agents converting it in parts.

usage: fnmeta.py <module> <out.json> [<bound> ...]   (bounds: first Python line of each part)
Each function: its Python lines, parameters and defaults, the module functions it calls (with their
part), the module constants it reads, the replaceable names it calls (leaf slots and patched names),
the other modules' attributes it reads, and its generated line range.
"""
import ast
import json
import re
import sys

R = '/Users/derekbredensteiner/Developer/homesodamachine/.cache/runs/typed-enclosure-202611041700'
GEN = '/Users/derekbredensteiner/Developer/homesodamachine/tools/hsm/enclosure-data/src/compiled'
module, out = sys.argv[1], sys.argv[2]
bounds = [int(b) for b in sys.argv[3:]] or [1]
src = open(f'{R}/py/{module}.py').read()
tree = ast.parse(src)
funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
imports = {}
for n in tree.body:
    if isinstance(n, ast.Import):
        for a in n.names:
            imports[a.asname or a.name] = a.name
    elif isinstance(n, ast.ImportFrom):
        for a in n.names:
            imports[a.asname or a.name] = f'{n.module}.{a.name}'
consts = {}
for n in tree.body:
    if isinstance(n, (ast.Assign, ast.AnnAssign)):
        targets = n.targets if isinstance(n, ast.Assign) else [n.target]
        for tg in targets:
            for x in ast.walk(tg):
                if isinstance(x, ast.Name):
                    consts.setdefault(x.id, n.lineno)
# Slots: module names assigned None at top level (recorders replace them).
slots = []
for n in tree.body:
    if isinstance(n, ast.Assign) and isinstance(n.value, ast.BinOp) and isinstance(n.targets[0], ast.Tuple) \
            and ast.unparse(n.value.left) == '(None,)':
        slots += [x.id for x in n.targets[0].elts]


def part(line):
    k = 0
    for i, b in enumerate(bounds):
        if line >= b:
            k = i + 1
    return k


gen = open(f'{GEN}/{module}.rs').read().split('\n')
starts = {}
for i, line in enumerate(gen, 1):
    m = re.fullmatch(r'    // ([A-Za-z_][A-Za-z0-9_]*)', line)
    if m and m.group(1) in funcs and m.group(1) not in starts:
        starts[m.group(1)] = i
order = sorted(starts, key=starts.get)
ends = {n: (starts[order[i + 1]] - 1 if i + 1 < len(order) else len(gen)) for i, n in enumerate(order)}
rows = []
for name, f in funcs.items():
    a = f.args
    pos = [x.arg for x in a.posonlyargs + a.args]
    defaults = dict(zip(pos[len(pos) - len(a.defaults):], [ast.unparse(d) for d in a.defaults]))
    kwonly = [x.arg for x in a.kwonlyargs]
    kwdefaults = {x.arg: ast.unparse(d) for x, d in zip(a.kwonlyargs, a.kw_defaults) if d is not None}
    calls, reads, slot_calls, ext = {}, set(), set(), set()
    local = {x.arg for x in ast.walk(f) if isinstance(x, ast.arg)}
    for x in ast.walk(f):
        if isinstance(x, (ast.Name)) and isinstance(x.ctx, ast.Store):
            local.add(x.id)
    for x in ast.walk(f):
        if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load):
            if x.id in slots:
                slot_calls.add(x.id)
            elif x.id in funcs and x.id != name:
                calls[x.id] = part(funcs[x.id].lineno)
            elif x.id in consts and x.id not in local:
                reads.add(x.id)
        if isinstance(x, ast.Attribute) and isinstance(x.value, ast.Name) and x.value.id in imports:
            ext.add(f'{x.value.id}.{x.attr}')
    nested = [y.name for y in ast.walk(f) if isinstance(y, (ast.FunctionDef, ast.Lambda)) and y is not f and isinstance(y, ast.FunctionDef)]
    rows.append(dict(name=name, part=part(f.lineno), py=[f.lineno, f.end_lineno], gen=[starts.get(name), ends.get(name)],
                     params=pos, defaults=defaults, vararg=a.vararg.arg if a.vararg else None,
                     kwonly=kwonly, kwdefaults=kwdefaults, kwarg=a.kwarg.arg if a.kwarg else None,
                     doc=bool(ast.get_docstring(f)), nested=nested,
                     calls=dict(sorted(calls.items())), consts=sorted(reads), slots=sorted(slot_calls), ext=sorted(ext)))
json.dump(dict(module=module, bounds=bounds, slots=slots, imports=imports,
               consts={k: v for k, v in sorted(consts.items(), key=lambda kv: kv[1])}, functions=rows),
          open(out, 'w'), indent=1)
print(module, len(rows), 'functions', len(consts), 'constants', len(slots), 'slots:', ' '.join(slots))
