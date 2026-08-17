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

#: WHICH KIND OF WRITE IT WAS IS THE WRITER'S TO SAY, and `graph.json` carries the answer:
#: `rewritten` is what `docgen` and `_cardgen` read and wrote back, and the rest of `writes`
#: is what `_cadq_export` cut whole. A name cannot tell them apart — `.figures.json` carries
#: no marker and is rewritten, a `.step` is read to be compared against and is not — and a
#: suffix list forgot a medium four times before this: a driver's own docstring, a mermaid
#: chart's `%%` lines, a doc's figures sidecar, and a card's `data-gen` elements.


#: The generated solids, which are on this disk and in no index — `hardware/cad-artifacts.lock.json`
#: names them and the release asset they arrive in. A sandbox is filled from `srcs`, so a solid one
#: generator cuts and the next loads has to be named there whichever side of the index it sits.
LOCK = _ROOT / "hardware" / "cad-artifacts.lock.json"


def tracked() -> list:
    """Every file this tree stands behind: git's, and the solids the lock names."""
    files = subprocess.run(["git", "-C", str(_ROOT), "ls-files"],
                           capture_output=True, text=True, check=True).stdout.split()
    try:
        files += json.loads(LOCK.read_text()).get("solids", {})
    except (OSError, ValueError):
        pass
    return sorted(set(files))


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

    # A READING TAKEN BEFORE THE WRITERS SAID WHICH KIND OF WRITE IT WAS cannot be sorted, and
    # sorting it wrong makes every doc an output its own action is not given. Named here rather
    # than built into a graph that fails one action at a time.
    stale = sorted(g for g, seen in graph.items() if "rewritten" not in seen)
    if stale:
        raise SystemExit(
            f"  {len(stale)} generator(s) were traced before a run said which of its writes it\n"
            f"  read back — {Path(stale[0]).name} among them. Re-trace them:\n"
            f"    tools/cad-venv/bin/python tools/bazel/trace_inputs.py")

    writes = {gen: {f for f in seen["writes"] if f in files}
              for gen, seen in graph.items() if gen in files}
    writes = {gen: w for gen, w in writes.items() if w}

    out = {}
    for gens in _together(writes):
        entry = {"solids": [], "docs": [], "reads": sorted(
            {f for g in gens for f in graph[g]["reads"] if f in files})}
        back = {f for g in gens for f in graph[g].get("rewritten", ()) if f in files}
        for f in sorted(set().union(*(writes[g] for g in gens))):
            (entry["docs"] if f in back else entry["solids"]).append(f)
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
