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


#: The generated solids, which are on this disk and in no index. A sandbox is filled from `srcs`,
#: so a solid one generator cuts and the next loads has to be named there whichever side of the
#: index it sits.
#:
#: TWO READINGS SAY WHICH SOLIDS THOSE ARE AND `tracked` TAKES BOTH, because each holds one the
#: other does not. `pack.py`'s walk reads this disk, so a solid cut since the last release is in
#: it — and a solid a trace is filtered against the lock alone cannot enter the graph until a
#: bundle is pinned, which is a part the sandbox is never filled with and an action that dies
#: on a file sitting in the tree. `hardware/cad-artifacts.lock.json` names the solids the pinned
#: bundle carries, which is the reading a checkout that has cut nothing of its own still has.
LOCK = _ROOT / "hardware" / "cad-artifacts.lock.json"

#: Outputs whose writer deliberately avoids touching them when the bytes beside its STEP are
#: already current. A syscall trace therefore sees the read that proves they are current, not a
#: write, even though a clean action must produce them. The enclosure payload is shared by its
#: smooth writer and the fluting pass; declaring it for both groups those generators into one
#: action, so the fluting pass never seeds itself from the fetched prior bundle.
IMPLICIT_SOLIDS = {
    "hardware/cold-core-layout/cold_core_assembly.py": (
        "hardware/cold-core-layout/cold-core-assembly.step.mesh",
    ),
    "hardware/printed-parts/enclosure/enclosure/enclosure.py": (
        "hardware/printed-parts/enclosure/enclosure/enclosure.step.mesh",
    ),
    "hardware/manifold-layout/enclosure_assembly.py": (
        "hardware/manifold-layout/enclosure-assembly.step.mesh",
    ),
    "hardware/manifold-layout/manifold_layout.py": (
        "hardware/manifold-layout/manifold-layout.step.mesh",
    ),
    "hardware/faucet-layout/faucet_assembly.py": (
        "hardware/faucet-layout/faucet-assembly.step.mesh",
    ),
}

# Outputs whose bytes cross from one Bazel action to another and stop there. The cold-core mesh
# saves the enclosure-assembly action from standing and tessellating the core a second time; the
# public artifact remains the cold-core STEP, so neither sync_tree nor the release pack may carry
# this ignored handoff into the source tree or the artifact lock.
ACTION_INTERMEDIATE = frozenset({
    "hardware/cold-core-layout/cold-core-assembly.step.mesh",
})

# A direct scene-render run can produce both media. The enclosure-assembly producer owns the
# public GLBs now, cutting them from the named machine it already has in memory. This synthetic
# card wrapper retains only the browser-driven PNG/JSON outputs from the shared trace.
SPLIT_GENERATORS = {
    "hardware/assembly/scenes/render_scenes.py": (
        "hardware/assembly/scenes/render_scene_cards.py",
    ),
}


def _split_generators(graph: dict) -> dict:
    graph = dict(graph)
    for source, (cards,) in SPLIT_GENERATORS.items():
        if source not in graph:
            continue
        seen = graph.pop(source)
        rewritten = set(seen.get("rewritten", ()))
        graph[cards] = {
            "reads": list(seen.get("reads", ())),
            "writes": [p for p in seen.get("writes", ()) if not p.endswith(".glb")],
            "rewritten": list(seen.get("rewritten", ())),
        }
    return graph

#: ONE WALK ANSWERS WHICH `.step` ON THIS DISK IS A GENERATED SOLID, and `pack.py` is where it
#: lives — `pack.py --check` holds that same walk against the outputs `graph.json` declares, so
#: the solids a bundle ships and the solids an action is filled from are one reading. Its
#: directory's hyphen keeps it out of a dotted import, so the path goes on `sys.path` and
#: `tracked` imports it by name.
sys.path.append(str(_ROOT / "tools" / "cad-artifacts"))


def tracked() -> list:
    """Every file this tree stands behind: git's, and the generated solids — the ones this disk
    holds and the ones the lock names."""
    files = subprocess.run(["git", "-C", str(_ROOT), "ls-files"],
                           capture_output=True, text=True, check=True).stdout.split()
    # Imported here and not above: `trace_inputs`'s own selftest runs in an action holding the
    # two modules it was watched reading, and nothing there asks this question.
    import pack
    files += pack.solids(_ROOT)
    try:
        files += json.loads(LOCK.read_text()).get("solids", {})
    except (OSError, ValueError):
        pass
    # The first trace happens before an ignored handoff can appear in graph.json or a release
    # lock. Its producer write and consumer read still need to survive the trace filter so that
    # this inventory can create the edge on that very first pass.
    files += [path for paths in IMPLICIT_SOLIDS.values() for path in paths]
    return sorted(set(files))


def _together(writes: dict) -> list:
    """Generators grouped so that every file has exactly one group writing it.

    `docgen` lets several scripts keep one doc's figures, each managing its own names:
    `faucet_shell.py` and `under_counter_plate.py` both write `ASSEMBLY.md`, and
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

    orphaned = sorted(set(graph) - files)
    if orphaned:
        raise SystemExit(
            f"  {len(orphaned)} build-graph generator(s) are absent from the tree — "
            f"{orphaned[0]} among them. Re-trace the renamed generator or remove its stale "
            f"graph entry.")

    graph = _split_generators(graph)
    files |= {path for paths in SPLIT_GENERATORS.values() for path in paths}

    # A NEW OUTPUT IS NOT IN GIT OR THE OLD BUNDLE YET. Filtering the trace through only the
    # files already present made that output disappear from BUILD.bazel, so no clean action
    # could ever create it and no publisher could ever add it. Writers declare their outputs;
    # their paths therefore join the inventory before writes and downstream reads are sorted.
    graph_writes = {f for seen in graph.values() for f in seen.get("writes", ())}
    files |= graph_writes
    files |= {f for paths in IMPLICIT_SOLIDS.values() for f in paths}

    # A READ OF A FILE NOTHING HAS AND NOTHING WRITES IS A READ OF A GHOST. The sort below
    # drops it — `if f in files` — so a generator can go on declaring it forever, and the
    # declaration says the build depends on something it cannot depend on. That is how a
    # deleted output leaves its readers behind: the pictures stop being drawn, the reads that
    # named them stay, and nothing says so. Named here, where the drop happens.
    ghosts = {g: sorted(f for f in seen.get("reads", ()) if f not in files)
              for g, seen in graph.items()}
    ghosts = {g: bad for g, bad in ghosts.items() if bad}
    if ghosts:
        gen, bad = sorted(ghosts.items())[0]
        raise SystemExit(
            f"  {sum(len(b) for b in ghosts.values())} declared read(s) across {len(ghosts)} "
            f"generator(s) name a file\n  the tree does not hold and no rule writes — "
            f"{bad[0]}, read by {Path(gen).name},\n  among them. Drop the read if what wrote it "
            f"is gone, or declare the writer.")

    # A READING TAKEN BEFORE THE WRITERS SAID WHICH KIND OF WRITE IT WAS cannot be sorted, and
    # sorting it wrong makes every doc an output its own action is not given. Named here rather
    # than built into a graph that fails one action at a time.
    stale = sorted(g for g, seen in graph.items() if "rewritten" not in seen)
    if stale:
        raise SystemExit(
            f"  {len(stale)} generator(s) were traced before a run said which of its writes it\n"
            f"  read back — {Path(stale[0]).name} among them. Re-trace them:\n"
            f"    tools/cad-venv/bin/python tools/bazel/trace_inputs.py")

    writes = {gen: (set(seen["writes"]) | set(IMPLICIT_SOLIDS.get(gen, ())))
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
