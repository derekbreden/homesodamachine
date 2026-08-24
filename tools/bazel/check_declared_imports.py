#!/usr/bin/env python3
"""Whether a staged module's imports are declared by the steps that read it.

An action holds the files its step declared and nothing else, so a generator that imports a
module no step names finds no module — `ModuleNotFoundError` on a file sitting in the tree,
tracked and committed. `trace_inputs.py` is what records a read, and it records what a run was
watched doing; an import added since that run is not in the graph until the run happens again.

This reads a staged file's own `import` statements, resolves each to a tracked `.py` by module
name, and holds the result against every step that reaches that file by importing it. Ast and a
graph lookup: no venv, no cadquery, no bazel.

A STEP READS A `.py` IT NEVER RUNS. Digesting a source is a read of it, and so is globbing the
directory it sits in — `flute_payload.py` reads `enclosure.py` and imports `_mesh_payload`,
numpy, trimesh and scipy. Nothing of `enclosure.py` executes in that run, so no module behind
it is owed, and the walk in `reaches` is what tells the two apart.

A name two tracked files share is left alone. Which of them an action reaches is what
`trace_inputs.py` answers by watching, and a guess here would be the name rule this graph
exists to stop making.
"""
import ast
import functools
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


@functools.lru_cache(maxsize=None)
def imports_of(text: str) -> set:
    """The module names a source imports AT IMPORT TIME.

    HELD BY TEXT, BECAUSE THE WALK ASKS THE SAME FILE THOUSANDS OF TIMES. `reaches` runs once
    per step per source and re-walks the imports under it each time; parsing them fresh made a
    whole-tree pass minutes rather than seconds. A source's imports are a function of its bytes,
    and the bytes are read once into `texts`, so the answer is the same every time it is asked.

    A FUNCTION-LOCAL IMPORT IS NOT AN IMPORT-TIME FACT, and this check's whole subject is the
    module that is missing when an action opens the file. `_facts.py` reaches five modules from
    inside functions and `_scorecard.py` reaches `enclosure_assembly` from inside three; a step
    that touches none of those paths loads none of them, so no such file is owed and the action
    runs. Whether a run gets there is precisely what `trace_inputs.py` answers by watching, and
    a guess here is the name rule this graph exists to stop making.

    So the walk does not enter a function. A CLASS BODY RUNS AT IMPORT and is walked; so is an
    import a module-level `if` or `try` guards, which runs at import like any other statement."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set()
    names = set()

    def visit(node):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                continue
            if isinstance(child, ast.Import):
                names.update(a.name.split(".")[0] for a in child.names)
            elif isinstance(child, ast.ImportFrom) and child.level == 0 and child.module:
                names.add(child.module.split(".")[0])
            visit(child)

    visit(tree)
    return names


def reaches(gen: str, src: str, by_name: dict, texts: dict) -> bool:
    """Whether `gen` gets to `src` by importing, at any depth.

    A STEP READS A `.py` IT NEVER RUNS. Digesting a source is a read of it, and so is globbing
    the directory it sits in, and neither executes a line — `flute_payload.py` reads
    `enclosure.py` and imports `_mesh_payload`, numpy, trimesh and scipy. What a file imports is
    owed by whoever imports it, so the walk to `src` is what decides, not the read."""
    seen, stack = set(), [gen]
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        if cur == src:
            return True
        for name in imports_of(texts.get(cur, "")):
            stack += [f for f in by_name.get(name, ()) if f not in seen]
    return False


def owed(graph: dict, tracked: set, sources: dict, texts: dict | None = None) -> list:
    """Every (step, source, imported file) where a step imports a source and holds no module the
    source imports.

    THE SOURCE IS THE HALF THAT ANSWERS "WHY THIS STEP". Most steps named here import nothing
    of the module directly — they import a file that does, so the module is theirs to hold and
    `from ... import` appears nowhere in them. Reporting the pair is what makes that a fact
    rather than a hunt.

    `sources` is the staged text by path and `texts` is every tracked source the walk reads, so
    this is a pure reading of four records and can be held against known answers."""
    by_name = {}
    for f in tracked:
        if f.endswith(".py"):
            by_name.setdefault(Path(f).stem, []).append(f)
    if texts is None:
        texts = {}
        for f in tracked:
            if f.endswith(".py"):
                try:
                    texts[f] = (_ROOT / f).read_text()
                except OSError:
                    pass
    texts = {**texts, **sources}

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
            if src in reads and reaches(gen, src, by_name, texts):
                out += [(gen, src, w) for w in sorted(wants - reads)]
    return sorted(set(out))


def selftest() -> int:
    graph = {"gen.py": {"reads": ["gen.py", "src.py", "seen.py"]}}
    tracked = {"gen.py", "src.py", "seen.py", "unseen.py", "a/dup.py", "b/dup.py"}
    # `gen.py` imports `src`, so what `src` imports is `gen`'s to hold.
    texts = {"gen.py": "import src"}

    holds = 0

    def hold(label, got, want):
        nonlocal holds
        ok = got == want
        holds += ok
        print(f"  {'✓' if ok else '✗'} {label}" + ("" if ok else f" — {got!r} != {want!r}"))

    def named(text):
        return [w for _g, _s, w in owed(graph, tracked, {"src.py": text}, texts)]

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
                                  {"loose.py": "import unseen"}, texts)], [])
    hold("a source that is not tracked is silent",
         [w for _g, _s, w in owed(graph, tracked, {"untracked.py": "import unseen"}, texts)], [])
    # THE STEP NAMED HERE IMPORTS THE MODULE THROUGH ANOTHER FILE. It imports `src.py`, which is
    # what imports the module, so the pair is what a reader needs and the step alone would send
    # them hunting.
    hold("the step is named with the file that imports",
         owed(graph, tracked, {"src.py": "import unseen"}, texts),
         [("gen.py", "src.py", "unseen.py")])
    # A `.py` A STEP READS WITHOUT IMPORTING IS NOT A MODULE IT LOADS. Digesting a source, or
    # globbing the directory it sits in, reads it and runs none of it, so what it imports is
    # nobody's to hold on its account.
    hold("a source a step reads but never imports is silent",
         owed(graph, tracked, {"src.py": "import unseen"}, {"gen.py": "import json"}), [])
    hold("a step reaching the source at depth is named",
         owed({"gen.py": {"reads": ["gen.py", "src.py", "seen.py"]}}, tracked | {"mid.py"},
              {"src.py": "import unseen"},
              {"gen.py": "import mid", "mid.py": "import src"}),
         [("gen.py", "src.py", "unseen.py")])
    # AN IMPORT A FUNCTION MAKES IS A RUN'S FACT, and the run is watched. A step that never
    # calls the function never loads the module, so the action owes no such file.
    hold("an import inside a function is the trace's to answer",
         named("def draw():\n    import unseen\n"), [])
    hold("an import inside a method reads the same",
         named("class A:\n    def draw(self):\n        import unseen\n"), [])
    # WHAT RUNS AT IMPORT IS OWED HOWEVER IT IS SPELLED. A class body executes, and a guard
    # around an import does not defer it.
    hold("an import a class body makes runs at import",
         named("class A:\n    import unseen\n"), ["unseen.py"])
    hold("an import a module-level try guards runs at import",
         named("try:\n    import unseen\nexcept ImportError:\n    unseen = None\n"), ["unseen.py"])

    print(f"check_declared_imports selftest {holds}/15")
    return 0 if holds == 15 else 1


def repair(graph: dict, missing: list) -> int:
    """Write the owed reads into `graph`, and answer how many were new.

    ONLY EVER ADDITIVE, AND THAT IS WHY IT IS SAFE TO WRITE WITHOUT WATCHING A RUN. The general
    job of the tracer is to answer what a run opened, which no reading of the source can do —
    a path built at runtime is invisible here. This answers a far narrower question: a module
    named in an `import` at module scope IS opened, by the interpreter, before the first line
    of the step runs. A re-trace would record exactly these edges and some others.

    So the failure mode is a step carrying a file it turns out not to need, which costs it one
    input and rebuilds it once more than it must. A re-trace is still what settles the whole
    entry — this settles the import, which is the edge that fails an action outright."""
    new = 0
    for gen, _src, want in missing:
        reads = graph[gen].setdefault("reads", [])
        if want not in reads:
            reads.append(want)
            new += 1
    for entry in graph.values():
        if "reads" in entry:
            entry["reads"] = sorted(set(entry["reads"]))
    return new


def main(argv) -> int:
    if argv and argv[0] == "selftest":
        return selftest()
    fix = "--fix" in argv
    # WHAT IS STAGED IS THE COMMIT'S OWN QUESTION, and the hook asks it there. A repair is asked
    # of a tree that is already committed and already failing, so it reads every tracked source.
    every = "--all" in argv or fix
    try:
        graph = json.loads(GRAPH.read_text())
    except (OSError, ValueError):
        print("check_declared_imports: no graph.json")
        return 0
    tracked = set(_git("ls-files"))
    # A SOURCE NO STEP READS OWES NOTHING, and `owed` says so by looking — so the whole-tree
    # pass asks only about the sources the graph already names, which is hundreds rather than
    # thousands and is the same answer.
    named = (f for f in sorted({r for e in graph.values() for r in e.get("reads", ())})
             if f.endswith(".py")) if every else (
        f for f in _git("diff", "--cached", "--name-only", "--diff-filter=ACM")
        if f.endswith(".py"))
    sources = {}
    for f in named:
        try:
            sources[f] = (_ROOT / f).read_text()
        except OSError:
            pass
    missing = owed(graph, tracked, sources)
    if not missing:
        print("check_declared_imports: every step holds what it imports")
        return 0
    print(f"{len(missing)} step(s) read a file importing a module the step does not hold:")
    for gen, src, want in missing:
        print(f"    {gen}\n      reads {src}, which imports {want}")
    if fix:
        new = repair(graph, missing)
        # THE SHAPE `trace_inputs` WRITES, so a repair is the lines it moved and not the file.
        # Several sessions hold this tree and read each other's diffs; a reformat here is 13,000
        # lines of noise over ten facts, and it collides with every re-trace in flight.
        GRAPH.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n")
        print(f"  wrote {new} read(s) into {GRAPH.name}. The graph states them; the file that")
        print("  carries them to bazel is written by:")
        print("    tools/cad-venv/bin/python tools/bazel/gen_build.py")
        return 0
    gens = sorted({g for g, _s, _w in missing})
    print("  a read is recorded by watching a run:")
    print(f"    tools/cad-venv/bin/python tools/bazel/trace_inputs.py {' '.join(gens)}")
    print("    tools/cad-venv/bin/python tools/bazel/gen_build.py")
    print("  or write just the import edges, which are read off the source:")
    print("    tools/cad-venv/bin/python tools/bazel/check_declared_imports.py --fix")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
