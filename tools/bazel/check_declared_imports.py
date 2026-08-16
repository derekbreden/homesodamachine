#!/usr/bin/env python3
"""Whether a staged module's imports are declared by the steps that read it.

An action holds the files its step declared and nothing else, so a generator that imports a
module no step names finds no module — `ModuleNotFoundError` on a file sitting in the tree,
tracked and committed. `trace_inputs.py` is what records a read, and it records what a run was
watched doing; an import added since that run is not in the graph until the run happens again.

This reads a staged file's own `import` statements, resolves each to a tracked `.py` by module
name, and holds the result against every step whose reads already include that file. Ast and a
graph lookup: no venv, no cadquery, no bazel.

A name two tracked files share is left alone. Which of them an action reaches is what
`trace_inputs.py` answers by watching, and a guess here would be the name rule this graph
exists to stop making.
"""
import ast
import json
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
GRAPH = _HERE / "graph.json"


def _git(*args) -> list:
    return subprocess.run(["git", *args], cwd=_ROOT,
                          capture_output=True, text=True).stdout.split()


def imports_of(text: str) -> set:
    """The top-level module names a source imports."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set()
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return names


def owed(graph: dict, tracked: set, sources: dict) -> list:
    """Every (step, source, imported file) where a step reads a source and holds no module the
    source imports.

    THE SOURCE IS THE HALF THAT ANSWERS "WHY THIS STEP". Most steps named here import nothing
    themselves — they read a file that does, so the module is theirs to hold and `from ... import`
    appears nowhere in them. Reporting the pair is what makes that a fact rather than a hunt.

    `sources` is the staged text by path, so this is a pure reading of three records and can be
    held against known answers."""
    by_name = {}
    for f in tracked:
        if f.endswith(".py"):
            by_name.setdefault(Path(f).stem, []).append(f)

    out = []
    for src, text in sorted(sources.items()):
        if src not in tracked:
            continue
        wants = set()
        for name in imports_of(text):
            same = by_name.get(name, [])
            if len(same) == 1:
                wants.add(same[0])
        wants.discard(src)
        for gen, entry in sorted(graph.items()):
            reads = set(entry.get("reads", ()))
            if src in reads:
                out += [(gen, src, w) for w in sorted(wants - reads)]
    return sorted(set(out))


def selftest() -> int:
    graph = {"gen.py": {"reads": ["gen.py", "src.py", "seen.py"]}}
    tracked = {"gen.py", "src.py", "seen.py", "unseen.py", "a/dup.py", "b/dup.py"}

    holds = 0

    def hold(label, got, want):
        nonlocal holds
        ok = got == want
        holds += ok
        print(f"  {'✓' if ok else '✗'} {label}" + ("" if ok else f" — {got!r} != {want!r}"))

    def named(text):
        return [w for _g, _s, w in owed(graph, tracked, {"src.py": text})]

    hold("an import the step does not declare is named", named("import unseen"), ["unseen.py"])
    hold("an import the step declares is silent", named("import seen"), [])
    hold("a stdlib name is no file of this tree", named("import json"), [])
    hold("a from-import reads the same", named("from unseen import x"), ["unseen.py"])
    hold("a dotted import names its root", named("import unseen.deep"), ["unseen.py"])
    # WHICH OF TWO FILES SHARING A NAME AN ACTION REACHES IS A WATCHED FACT, not a guess.
    hold("a name two tracked files share is left alone", named("import dup"), [])
    # A SOURCE NO STEP READS IS NOT THIS CHECK'S BUSINESS — nothing stages it either way.
    hold("a source no step reads is silent",
         [w for _g, _s, w in owed(graph, tracked | {"loose.py"},
                                  {"loose.py": "import unseen"})], [])
    hold("a source that is not tracked is silent",
         [w for _g, _s, w in owed(graph, tracked, {"untracked.py": "import unseen"})], [])
    # THE STEP NAMED HERE IMPORTS NOTHING. It reads `src.py`, which is what imports the module,
    # so the pair is what a reader needs and the step alone would send them hunting.
    hold("the step is named with the file that imports",
         owed(graph, tracked, {"src.py": "import unseen"}),
         [("gen.py", "src.py", "unseen.py")])

    print(f"check_declared_imports selftest {holds}/9")
    return 0 if holds == 9 else 1


def main(argv) -> int:
    if argv and argv[0] == "selftest":
        return selftest()
    try:
        graph = json.loads(GRAPH.read_text())
    except (OSError, ValueError):
        print("check_declared_imports: no graph.json")
        return 0
    tracked = set(_git("ls-files"))
    sources = {}
    for f in _git("diff", "--cached", "--name-only", "--diff-filter=ACM"):
        if f.endswith(".py"):
            try:
                sources[f] = (_ROOT / f).read_text()
            except OSError:
                pass
    missing = owed(graph, tracked, sources)
    if not missing:
        return 0
    print(f"{len(missing)} step(s) read a file importing a module the step does not hold:")
    for gen, src, want in missing:
        print(f"    {gen}\n      reads {src}, which imports {want}")
    gens = sorted({g for g, _s, _w in missing})
    print("  a read is recorded by watching a run:")
    print(f"    tools/cad-venv/bin/python tools/bazel/trace_inputs.py {' '.join(gens)}")
    print("    tools/cad-venv/bin/python tools/bazel/gen_build.py")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
