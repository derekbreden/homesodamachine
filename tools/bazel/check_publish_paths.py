#!/usr/bin/env python3
"""Whether every source a step reads is one a push of which starts a publish.

`publish.yml`'s `paths:` is a CLAIM ABOUT WHICH CHANGES MATTER, and nothing holds it against
the graph. A file some step reads that sits under no pattern in that list is a file whose
change publishes nothing: the push lands, no run is created, no target is cut, and the tracked
output it feeds keeps yesterday's bytes.

THE SYMPTOM IS SILENCE, WHICH IS WHY IT NEEDS A GATE. Every other fault in this pipeline ends
in a red run somebody reads. This one ends in "I pushed it and nothing happened" — no run, no
log, no failure, and a doc or a picture that quietly stopped tracking its source.

A PATTERN THAT EXCLUDES ON PURPOSE IS NOT THIS FAULT. The list negates its own outputs —
scorecards, the Quick Start artwork — because a generated file that is also a source would
have each publish start the next one. So a source the list REACHES and then excludes is a
decision, and passes; only a source no pattern names at all is reported.

Text and two sets: no venv, no bazel, no network.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
GRAPH = _HERE / "graph.json"
WORKFLOW = _ROOT / ".github" / "workflows" / "publish.yml"


def _git(*args) -> list:
    return subprocess.run(["git", *args], cwd=_ROOT,
                          capture_output=True, text=True).stdout.split()


def as_regex(pattern: str):
    """A GitHub path filter as a regex.

    `**` crosses directories and `*` does not, which is the whole of the difference and the
    reason `fnmatch` cannot answer this: it lets a single star swallow a slash, so
    `tools/*.py` would match `tools/bazel/affected.py` and a real gap would read as covered."""
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**", i):
            out += ".*"
            i += 2
        elif pattern[i] == "*":
            out += "[^/]*"
            i += 1
        else:
            out += re.escape(pattern[i])
            i += 1
    return re.compile("^" + out + "$")


def filters(text: str) -> tuple:
    """`(positive, negative)` patterns from the `paths:` list of a workflow's push trigger."""
    start = text.index("    paths:")
    end = text.index("  workflow_dispatch:", start)
    named = [line.strip()[2:].strip().strip("'\"")
             for line in text[start:end].splitlines() if line.strip().startswith("- ")]
    return ([p for p in named if not p.startswith("!")],
            [p[1:] for p in named if p.startswith("!")])


def unnamed(graph: dict, tracked: set, positive: list) -> list:
    """Every tracked source the graph reads that no positive pattern names."""
    srcs = {r for entry in graph.values() for r in entry.get("reads", ())} | set(graph)
    hit = [as_regex(p) for p in positive]
    return sorted(s for s in srcs & tracked if not any(r.match(s) for r in hit))


def selftest() -> int:
    holds = 0

    def hold(label, got, want):
        nonlocal holds
        ok = got == want
        holds += ok
        print(f"  {'✓' if ok else '✗'} {label}" + ("" if ok else f" — {got!r} != {want!r}"))

    hold("a double star crosses directories",
         bool(as_regex("hardware/**").match("hardware/a/b/c.py")), True)
    # THE STAR THAT DOES NOT CROSS IS WHY `fnmatch` CANNOT ANSWER THIS.
    hold("a single star stays in its segment",
         bool(as_regex("tools/*.py").match("tools/bazel/affected.py")), False)
    hold("an exact name matches itself", bool(as_regex("BUILD.bazel").match("BUILD.bazel")), True)
    hold("a dot is a dot, not any character",
         bool(as_regex("BUILD.bazel").match("BUILDxbazel")), False)
    text = "    paths:\n      - hardware/**\n      - '!hardware/**/*.json'\n  workflow_dispatch:"
    hold("the list splits into kept and excluded",
         filters(text), (["hardware/**"], ["hardware/**/*.json"]))
    graph = {"a/gen.py": {"reads": ["a/gen.py", "far/away.py"]}}
    hold("a source no pattern names is reported",
         unnamed(graph, {"a/gen.py", "far/away.py"}, ["a/**"]), ["far/away.py"])
    hold("a source a pattern names is silent",
         unnamed(graph, {"a/gen.py"}, ["a/**"]), [])
    print(f"check_publish_paths selftest {holds}/7")
    return 0 if holds == 7 else 1


def main(argv) -> int:
    if argv and argv[0] == "selftest":
        return selftest()
    if not (GRAPH.is_file() and WORKFLOW.is_file()):
        print("check_publish_paths: no graph.json or no publish.yml")
        return 0
    positive, _negative = filters(WORKFLOW.read_text())
    missing = unnamed(json.loads(GRAPH.read_text()), set(_git("ls-files")), positive)
    if not missing:
        print("check_publish_paths: every source a step reads can start a publish")
        return 0
    print(f"{len(missing)} source(s) a step reads that no `paths:` pattern names — "
          f"a push of one starts no run at all:")
    for src in missing:
        print(f"    {src}")
    print("  the list is in .github/workflows/publish.yml, under `on: push: paths:`.")
    print("  A source that must NOT start a publish belongs there as a `!` rule, which says so.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
