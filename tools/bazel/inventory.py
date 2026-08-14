#!/usr/bin/env python3
"""Every generator in the tree and what it makes, read off what a run of it was watched doing.

    tools/cad-venv/bin/python tools/bazel/inventory.py        # print it

`trace_inputs.py` watches each generator run and writes down every tracked file it opened, by
the side it opened it on. `graph.json` is that record. This sorts each generator's writes into
the solids it cuts and the docs it rewrites, and carries its reads through to `gen_build.py`.
"""

import json
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[2]
GRAPH = _HERE.parent / "graph.json"

#: What a run reads and writes back over: a doc and its figures, a mermaid chart's `%%` lines,
#: and the generator's own comments and docstrings. Everything else a run writes it only cuts.
REWRITTEN_SUFFIXES = (".md", ".figures.json", ".mmd", ".py")


def tracked() -> list:
    return subprocess.run(["git", "-C", str(_ROOT), "ls-files"],
                          capture_output=True, text=True, check=True).stdout.split()


def _together(writes: dict) -> list:
    """Generators grouped so that every file has exactly one group writing it.

    `docgen` lets several scripts keep one doc's figures, each managing its own names:
    `touch_flo_shell.py` and `touch_flo_under_counter_plate.py` both write `ASSEMBLY.md`, and
    a run of either alone leaves the other's names standing at what they last were. So they
    are one step."""
    parent = {g: g for g in writes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    home = {}
    for gen in sorted(writes):
        for f in sorted(writes[gen]):
            first = home.setdefault(f, gen)
            a, b = find(first), find(gen)
            if a != b:
                parent[max(a, b)] = min(a, b)

    out = {}
    for gen in sorted(writes):
        out.setdefault(find(gen), []).append(gen)
    return [sorted(v) for _k, v in sorted(out.items())]


def inventory(files=None) -> dict:
    """`{(generator, …): {"solids": [...], "docs": [...], "reads": [...]}}` per build step."""
    files = set(files or tracked())
    try:
        graph = json.loads(GRAPH.read_text())
    except (OSError, ValueError):
        return {}

    writes = {gen: {f for f in seen["writes"] if f in files}
              for gen, seen in graph.items() if gen in files}
    writes = {gen: w for gen, w in writes.items() if w}

    out = {}
    for gens in _together(writes):
        entry = {"solids": [], "docs": [], "reads": sorted(
            {f for g in gens for f in graph[g]["reads"] if f in files})}
        for f in sorted(set().union(*(writes[g] for g in gens))):
            (entry["docs"] if f.endswith(REWRITTEN_SUFFIXES)
             else entry["solids"]).append(f)
        out[tuple(gens)] = entry
    return out


def main() -> int:
    inv = inventory()
    solids = sum(len(v["solids"]) for v in inv.values())
    docs = sum(len(v["docs"]) for v in inv.values())
    gens = sum(len(k) for k in inv)
    print(f"  {len(inv)} steps over {gens} generators, {solids} solids, {docs} doc files")
    for k in sorted(inv):
        if len(k) > 1:
            print("  one step: " + ", ".join(Path(g).name for g in k))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
