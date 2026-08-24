#!/usr/bin/env python3
"""Whether every bazel target a workflow names is one BUILD.bazel declares.

BUILD.bazel IS GENERATED AND THE WORKFLOWS ARE NOT. `gen_build.py` writes a target per step
and names it after the step's own path, so a source that moves takes its target's name with
it — and `.github/workflows/` keeps whatever it was told. The graph regenerates, every gate
stays green, and the run dies naming a target bazel has never heard of.

IT DIES LATE. A publish builds the CAD first and reaches the steps that name targets by hand
at the end, so the run cuts everything and then stops on the label.

AND A WORKFLOW MATCHES ON THESE LABELS AS WELL AS BUILDING THEM: scoping greps one out of the
requested list, debt greps one out of a provenance range. A `grep` for a name nothing emits
returns nothing, and the branch behind it stops being taken.

So this reads the labels out of the workflows and holds them against the names in
BUILD.bazel. Text and a set: no venv, no bazel, no network.
"""
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
WORKFLOWS = _ROOT / ".github" / "workflows"
BUILD = _ROOT / "BUILD.bazel"

#: `//:name`, and the alternation a `grep -E` writes it in — `^//:(quickstart-build|cad-art)$`
#: names two targets and neither is spelled on its own.
_LABEL = re.compile(r"//:\(?([A-Za-z0-9_|-]+)\)?")
_DECLARED = re.compile(r'^\s*name = "([^"]+)",\s*$', re.M)


def declared(text: str) -> set:
    """Every target name BUILD.bazel declares."""
    return set(_DECLARED.findall(text))


def named(text: str) -> tuple:
    """`(run, prose)` — the target names a workflow's steps name, and the ones only its
    comments do, alternations split out of both.

    A label a step names stops the run; a label only a comment names does not. They are
    counted apart, and `main` holds the commit for the first and prints the second."""
    run, prose = set(), set()
    for line in text.splitlines():
        stripped = line.lstrip()
        side = prose if stripped.startswith("#") else run
        for hit in _LABEL.findall(line):
            side |= {part for part in hit.split("|") if part}
    return run, prose - run


def selftest() -> int:
    holds = 0

    def hold(label, got, want):
        nonlocal holds
        ok = got == want
        holds += ok
        print(f"  {'✓' if ok else '✗'} {label}" + ("" if ok else f" — {got!r} != {want!r}"))

    hold("a plain label is named", named("bazel build //:cad-art"), ({"cad-art"}, set()))
    hold("an alternation names both",
         named("grep -E '^//:(quickstart-build|cad-art)$'"),
         ({"quickstart-build", "cad-art"}, set()))
    hold("a label in a longer line is found",
         named("  --targets //:enclosure-assembly\n"), ({"enclosure-assembly"}, set()))
    hold("text with no label names nothing", named("bazel build\n"), (set(), set()))
    hold("a label only a comment names is prose",
         named("  # //:render-scenes boots a viewer\n"), (set(), {"render-scenes"}))
    hold("a label a step names too is not prose",
         named("# see //:cad-art\nbazel build //:cad-art\n"), ({"cad-art"}, set()))
    hold("a declared name is read", declared('    name = "cad-art",\n'), {"cad-art"})
    # A NAME IN PROSE IS NOT A DECLARATION — the pattern is anchored to the whole line.
    hold("a name inside a comment is not a declaration",
         declared('# name = "not-a-target",\n'), set())
    print(f"check_ci_targets selftest {holds}/8")
    return 0 if holds == 8 else 1


def main(argv) -> int:
    if argv and argv[0] == "selftest":
        return selftest()
    if not BUILD.is_file():
        print("check_ci_targets: no BUILD.bazel")
        return 0
    have = declared(BUILD.read_text())
    missing, stale = {}, {}
    for workflow in sorted(WORKFLOWS.glob("*.yml")) if WORKFLOWS.is_dir() else ():
        run, prose = named(workflow.read_text())
        for want in sorted(run - have):
            missing.setdefault(workflow.name, []).append(want)
        for want in sorted(prose - have):
            stale.setdefault(workflow.name, []).append(want)
    for workflow, names in stale.items():
        for want in names:
            print(f"  a comment in .github/workflows/{workflow} names //:{want}, "
                  f"which nothing declares")
    if not missing:
        print("check_ci_targets: every target a workflow step names is declared")
        return 0
    total = sum(len(v) for v in missing.values())
    print(f"{total} target(s) a workflow STEP names are not declared in BUILD.bazel:")
    for workflow, names in missing.items():
        for want in names:
            print(f"    .github/workflows/{workflow} names //:{want}")
    print("  BUILD.bazel is written from the graph, so a target is renamed by the source")
    print("  moving. The workflow keeps what it was told:")
    print("    grep -n '//:' .github/workflows/*.yml")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
