"""Swap one crate's source files in tools/bazel/graph.json for the ones its program now reads.

usage: graph_swap.py <crate dir, e.g. tools/hsm/cold-core-data> <program dep-info .d file> [<out>]
Every graph entry that reads a file under the crate gets the crate files the dep-info names
instead (sources under the crate plus its Cargo.toml); nothing else in the graph changes.
Written the way trace_inputs.py writes it: indent 2, sorted keys, trailing newline.
"""
import json
import sys
from pathlib import Path

REPO = Path('/Users/derekbredensteiner/Developer/homesodamachine')
GRAPH = REPO / 'tools/bazel/graph.json'
crate = sys.argv[1].rstrip('/') + '/'
depinfo = Path(sys.argv[2]).read_text()

# The dep-info's first rule lists every source rustc read, separated by spaces (escaped "\ ").
first = depinfo.split('\n', 1)[0]
_, deps = first.split(': ', 1)
files = set()
for token in deps.replace('\\ ', '\0').split():
    path = Path(token.replace('\0', ' '))
    try:
        rel = path.resolve().relative_to(REPO).as_posix()
    except ValueError:
        continue
    if rel.startswith(crate):
        files.add(rel)
files.add(crate + 'Cargo.toml')
missing = [f for f in files if not (REPO / f).exists()]
if missing:
    raise SystemExit(f'dep-info names files that do not exist: {missing[:5]}')

graph = json.loads(GRAPH.read_text())
changed = 0
for name, entry in graph.items():
    reads = entry.get('reads', [])
    if not any(r.startswith(crate) for r in reads):
        continue
    new = sorted({r for r in reads if not r.startswith(crate)} | files)
    if new != reads:
        entry['reads'] = new
        changed += 1
Path(sys.argv[3] if len(sys.argv) > 3 else GRAPH).write_text(json.dumps(graph, indent=2, sort_keys=True) + '\n')
print(json.dumps({'crate': crate, 'crate_files': len(files), 'entries_changed': changed}))
