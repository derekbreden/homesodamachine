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


def inventory(files=None) -> dict:
    """`{generator: {"solids": [...], "docs": [...], "reads": [...]}}` for every generator."""
    files = set(files or tracked())
    try:
        graph = json.loads(GRAPH.read_text())
    except (OSError, ValueError):
        return {}

    out = {}
    for gen, seen in sorted(graph.items()):
        if gen not in files:
            continue
        wrote = [f for f in seen["writes"] if f in files]
        entry = {"solids": [], "docs": [],
                 "reads": [f for f in seen["reads"] if f in files]}
        for f in sorted(wrote):
            (entry["docs"] if f.endswith(REWRITTEN_SUFFIXES)
             else entry["solids"]).append(f)
        if entry["solids"] or entry["docs"]:
            out[gen] = entry
    return out


def main() -> int:
    inv = inventory()
    solids = sum(len(v["solids"]) for v in inv.values())
    docs = sum(len(v["docs"]) for v in inv.values())
    print(f"  {len(inv)} generators, {solids} solids, {docs} doc files")
    multi = [g for g, v in inv.items() if v["solids"] and v["docs"]]
    print(f"  {len(multi)} cut a solid AND write a doc")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
