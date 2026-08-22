#!/usr/bin/env python3
"""The targets a working tree's changes reach, for a build that holds only them.

    tools/cad-venv/bin/python tools/bazel/affected.py          # the targets, one per line
    tools/cad-venv/bin/python tools/bazel/affected.py --why    # each target, and what reaches it
    tools/cad-venv/bin/python tools/bazel/affected.py --base HEAD^ --artifacts
    tools/cad-venv/bin/python tools/bazel/affected.py selftest

    bazel build $(tools/cad-venv/bin/python tools/bazel/affected.py)

A NO-OP BUILD OF THIS TREE IS UNDER A SECOND AND A FULL ONE IS FOURTEEN MINUTES, so what an
edit costs is decided by how much of the graph it reaches. `bazel query rdeps` answers that
against the same BUILD.bazel a build reads, and this hands it the files git says have moved.

A CHANGED FILE NO TARGET NAMES IS THE ONE THAT MATTERS, and it is named on stderr rather than
passed over: the target list below it is then a smaller set than the tree owes, and a build of
that list is not a build of what changed. A file bazel does not know is either outside every
target's inputs or newly added to a graph that has not been regenerated.
"""

import argparse
import io
import importlib.util
import json
import os
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "tools" / "bazel"))

from gen_build import target_name  # noqa: E402
from inventory import inventory, tracked  # noqa: E402


def _git(*args) -> list:
    run = subprocess.run(["git", "-C", str(_ROOT), *args],
                         capture_output=True, text=True)
    if run.returncode != 0:
        detail = next((line for line in run.stderr.splitlines() if line.strip()),
                      f"exit {run.returncode}")
        raise SystemExit(f"git {' '.join(args)} did not answer: {detail}")
    return [line for line in run.stdout.splitlines() if line.strip()]


def changed() -> list:
    """Every path git reports as moved — staged, unstaged, and untracked alike.

    A build reads the worktree, so what is staged and what is merely saved reach it the same."""
    out = set()
    for line in _git("status", "--porcelain"):
        out.update(paths_in(line))
    return sorted(p for p in out if p and not p.endswith("/"))


def changed_between(base: str, head: str = "HEAD") -> list:
    """Every old and new path changed between two commits."""
    return _diff_paths(_git("diff", "--name-status", "--find-renames", base, head))


def _diff_paths(lines: list[str]) -> list:
    """Parse `git diff --name-status`, retaining both sides of a rename or copy."""
    out = set()
    for line in lines:
        fields = line.split("\t")
        if not fields:
            continue
        if fields[0].startswith(("R", "C")) and len(fields) >= 3:
            out.update(fields[1:3])
        elif len(fields) >= 2:
            out.add(fields[1])
    return sorted(p for p in out if p and not p.endswith("/"))


def paths_in(line: str) -> tuple:
    """The path or paths one porcelain line names.

    A RENAME NAMES BOTH SIDES. The old path is gone from the worktree and the new one carries
    its bytes, and a target reading either is a target this edit reaches."""
    path = line[3:].strip()
    if " -> " in path:
        old, new = path.split(" -> ", 1)
        return (old.strip('"'), new.strip('"'))
    return (path.strip('"'),)


def known(paths: list) -> tuple:
    """The paths bazel names as source labels, and the ones it does not."""
    if not paths:
        return [], []
    labels = [f"//:{p}" for p in paths]
    # Asking for the package's source-file universe keeps a genuinely unknown path from
    # turning the query itself red. Every generated rule lives in this root package.
    q = subprocess.run(["bazel", "query", 'kind("source file", //:*)'],
                       cwd=str(_ROOT), capture_output=True, text=True)
    if q.returncode != 0:
        detail = next((line for line in q.stderr.splitlines() if line.startswith("ERROR")),
                      f"exit {q.returncode}")
        raise SystemExit(f"bazel could not enumerate source inputs: {detail}")
    seen = {l.strip() for l in q.stdout.splitlines() if l.startswith("//:")}
    hit = [p for p, l in zip(paths, labels) if l in seen]
    return hit, [p for p in paths if p not in set(hit)]


def targets(paths: list) -> list:
    """Every target `paths` reach, source labels dropped."""
    if not paths:
        return []
    q = subprocess.run(
        ["bazel", "query", f"rdeps(//..., set({' '.join(f'//:{p}' for p in paths)}))"],
        cwd=str(_ROOT), capture_output=True, text=True)
    if q.returncode != 0:
        detail = next((line for line in q.stderr.splitlines() if line.startswith("ERROR")),
                      f"exit {q.returncode}")
        raise SystemExit(f"bazel could not compute the affected graph: {detail}")
    out = []
    for line in q.stdout.splitlines():
        line = line.strip()
        # A source file is its own rdep. What a build takes is the rules.
        if line.startswith("//:") and not any(line.endswith(s) for s in
                                              (".py", ".js", ".json", ".md", ".step", ".mmd",
                                               ".html", ".css", ".svg", ".png", ".dxf", ".glb",
                                               ".pdf", ".3mf", ".stl", ".ts", ".tsx", ".sh")):
            out.append(line)
    return sorted(set(out))


def artifact_targets() -> set:
    """Generator rules that publish at least one member of the CAD bundle."""
    inv = inventory(tracked())
    seen, shared = set(), set()
    for gens in inv:
        for gen in gens:
            stem = Path(gen).stem.strip("_").replace("_", "-")
            (shared if stem in seen else seen).add(stem)
    return {
        f"//:{target_name(gens[0], shared)}"
        for gens, made in inv.items()
        if any(p.endswith((".step", ".stl", ".glb", ".step.mesh"))
               for p in made["solids"])
    }


def declared_outputs() -> set:
    try:
        graph = json.loads((_ROOT / "tools" / "bazel" / "graph.json").read_text())
    except (OSError, ValueError):
        return set()
    return {path for node in graph.values() for path in node.get("writes", ())}


def artifact_global(path: str) -> bool:
    """Whether an edit changes how every artifact action is described or executed."""
    if path in {".bazelrc", ".bazelversion", ".dockerignore", "BUILD.bazel", "MODULE.bazel",
                "MODULE.bazel.lock", "tools/cad-requirements.txt"}:
        return True
    return path.startswith(("tools/bazel/", "tools/cad-artifacts/",
                            "tools/cad-venv-site/", "tools/ci-image/"))


def unscoped_changes(paths: list, known_paths: list, artifacts_only: bool) -> list:
    """Changes whose effect cannot be bounded by Bazel reverse dependencies."""
    known_set = set(known_paths)
    return sorted(
        path for path in paths
        if artifact_global(path)
        or (path not in known_set and artifact_unknown(path, artifacts_only))
    )


def write_targets(found: list, stream=None) -> None:
    """Write labels one per line, and exactly zero bytes for an empty slice."""
    if stream is None:
        stream = sys.stdout
    if found:
        stream.write("\n".join(found) + "\n")


@lru_cache(maxsize=1)
def _artifact_presentation_context() -> tuple:
    try:
        graph = json.loads((_ROOT / "tools" / "bazel" / "graph.json").read_text())
    except (OSError, ValueError):
        return {}, set()
    inv = inventory(tracked())
    artifact_gens = {
        gen for gens, made in inv.items()
        if any(p.endswith((".step", ".stl", ".glb", ".step.mesh"))
               for p in made["solids"])
        for gen in gens
    }
    return graph, artifact_gens


def artifact_presentation_only(path: str) -> bool:
    """Whether `path` can change presentation but not a published solid.

    Rewritten docs and media are source inputs to their combined generator action only so the
    action can preserve authored text while updating figures. Their bytes do not define its
    geometry. A path stops being presentation-only if another artifact generator reads it as a
    normal input; that keeps real data-bearing documents such as the BOM and fluid topology in
    the CAD slice while letting ordinary README/card edits advance the deployment lock without
    recutting solids.
    """
    if not path.startswith("hardware/"):
        return False
    if not (path.endswith((".md", ".mmd", ".html", ".png", ".svg", ".pdf", ".css",
                           ".figures.json", ".scene.json"))):
        return False
    graph, artifact_gens = _artifact_presentation_context()
    if not graph:
        return False

    writers = {gen for gen, seen in graph.items()
               if path in seen.get("rewritten", ())}
    readers = {gen for gen, seen in graph.items()
               if gen in artifact_gens and path in seen.get("reads", ())}
    return readers <= writers


def artifact_unknown(path: str, artifacts_only: bool = False) -> bool:
    """Whether an unlabelled path could define or feed a new CAD action."""
    if path == "hardware/cad-artifacts.lock.json":
        return False
    if path in declared_outputs():
        return False
    if path.startswith("hardware/"):
        # Presentation outputs cannot alter a STEP/STL/GLB action. They still widen the full
        # derive lane, where cards and docs are outputs in their own right.
        if artifacts_only and artifact_presentation_only(path):
            return False
        return True
    if artifact_global(path):
        return True
    return path.startswith(("tools/bazel/", "tools/cad-artifacts/",
                            "tools/cad-venv-site/", "tools/ci-image/",
                            "tools/docgen/", "tools/render/", "web/"))


def selftest() -> int:
    holds = 0

    def hold(label, ok, got=""):
        nonlocal holds
        holds += ok
        print(f"  {'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f" — {got}"))

    hold("a rename names both sides",
         paths_in('R  old/a.py -> new/b.py') == ("old/a.py", "new/b.py"),
         str(paths_in('R  old/a.py -> new/b.py')))
    hold("a quoted path loses its quotes",
         paths_in('?? "has space.py"') == ("has space.py",),
         str(paths_in('?? "has space.py"')))
    hold("an ordinary line is one path",
         paths_in(' M hardware/scripts/lanes.py') == ("hardware/scripts/lanes.py",))
    hold("a diff rename names both sides",
         _diff_paths(["R100\told/a.py\tnew/b.py"]) == ["new/b.py", "old/a.py"])
    hold("firmware outside the graph does not widen the CAD slice",
         not artifact_unknown("firmware/src/main.cpp")
         and artifact_unknown("hardware/new_part.py")
         and not artifact_unknown("hardware/cad-artifacts.lock.json")
         and artifact_unknown(".dockerignore")
         and artifact_unknown("hardware/new-image.png")
         and not artifact_unknown("hardware/new-image.png", artifacts_only=True))
    hold("rewritten presentation is outside the artifact slice",
         artifact_presentation_only(
             "hardware/printed-parts/enclosure/ceiling-panel/README.md"))
    hold("a data-bearing document stays in the artifact slice",
         not artifact_presentation_only("hardware/ledger/bom.md"))
    hold("a known global build input still widens the artifact slice",
         unscoped_changes(["BUILD.bazel"], ["BUILD.bazel"], True) == ["BUILD.bazel"]
         and unscoped_changes(["hardware/part.py"], ["hardware/part.py"], True) == [])
    empty = io.StringIO()
    write_targets([], empty)
    hold("zero targets write zero bytes", empty.getvalue() == "", repr(empty.getvalue()))
    # BAZEL IS THE ONE THING THIS CANNOT ASK FOR ITSELF. `known` and `targets` shell out to
    # `bazel query`, and a test bazel is running holds the server lock this workspace shares —
    # a query under it waits for the build that started it. The holds above stand on their own;
    # the three below are taken where a shell can reach bazel.
    if os.environ.get("TEST_SRCDIR"):
        print("  --   bazel query holds skipped: a query under `bazel test` waits on its own "
              "server. Run `affected.py selftest` from a shell for them.")
        print(f"affected selftest {holds}/{holds} (of the holds this run can take)")
        return 0 if holds == 9 else 1

    src = ["hardware/printed-parts/cold-core/foam-cap/foam_cap.py"]
    hit, miss = known(src)
    hold("a tracked source is a label bazel knows", hit == src, f"{hit!r} {miss!r}")
    t = targets(src)
    hold("a leaf part reaches its own target", "//:foam-cap" in t, str(t))
    hold("and not an unrelated artifact branch", "//:texture-coupons" not in t,
         f"{len(t)} targets")
    hold("a path bazel does not name is reported, not dropped",
         known(["no/such/file.py"]) == ([], ["no/such/file.py"]))
    hold("nothing changed is no targets", targets([]) == [] and changed() is not None)
    hold("artifact rules are a strict build slice",
         "//:ceiling-panel" in artifact_targets() and "//:everything" not in artifact_targets())
    print(f"affected selftest {holds}/15")
    return 0 if holds == 15 else 1


def say_if_unshimmed() -> None:
    """Name it on stderr when this interpreter has no import shim.

    THE COST OF NOT HAVING IT LANDS ON A BUILD AND NOTHING ELSE SAYS SO. Every CAD action
    reaches `tools/cad-venv/bin/python` by absolute path, outside the sandbox, so the
    interpreter is not a declared input to any of them — bazel cannot see the shim, and a
    checkout that never installed it builds the same solids while paying VTK's 12 s and
    145 MB in each of 85 processes. Green, correct, and slow, with nothing to read.

    An advisory and not a gate: the solids are byte-identical either way, so a tree without
    the shim is slow and not wrong, and a red step would be claiming otherwise.

    Only asked when this IS the CAD venv's python — `install.py` answers for whatever
    interpreter imports it, so any other one would be answering about itself.

    BY `sys.prefix` AND NOT BY `sys.executable`. The venv's `bin/python` is a symlink to the
    interpreter it was built from, so resolving it lands in homebrew's cellar and no venv is
    ever recognised — a guard that reads as careful and returns early every time, leaving the
    advisory silent on exactly the tree that needs it. `sys.prefix` is the venv itself."""
    venv = _ROOT / "tools" / "cad-venv"
    try:
        if Path(sys.prefix).resolve() != venv.resolve():
            return
        spec = importlib.util.spec_from_file_location(
            "_hsm_shim_install", venv.parent / "cad-venv-site" / "install.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        gone = mod.missing()
    except Exception:
        return
    if gone:
        print("this interpreter has no import shim — every CAD action will load VTK, which "
              "nothing here draws with, for 12 s and 145 MB apiece:", file=sys.stderr)
        print(f"    {sys.executable} tools/cad-venv-site/install.py", file=sys.stderr)


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", help="selftest")
    ap.add_argument("--why", action="store_true", help="name what reaches each target")
    ap.add_argument("--base", help="read committed changes from BASE instead of the worktree")
    ap.add_argument("--head", default="HEAD", help="range endpoint used with --base")
    ap.add_argument("--artifacts", action="store_true",
                    help="print only rules that publish members of the CAD bundle")
    ap.add_argument("--all-artifacts", action="store_true",
                    help="print every rule that publishes a CAD bundle member")
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.all_artifacts:
        write_targets(sorted(artifact_targets()))
        return 0

    say_if_unshimmed()

    moved = changed_between(args.base, args.head) if args.base else changed()
    if args.artifacts:
        moved = [path for path in moved if not artifact_presentation_only(path)]
    if not moved:
        print("nothing has moved — a build of this tree holds nothing to do", file=sys.stderr)
        return 0
    hit, miss = known(moved)
    risky = unscoped_changes(moved, hit, args.artifacts)
    if risky:
        print(f"{len(risky)} changed CAD path(s) cannot be safely scoped — this slice widens "
              f"to every artifact rule:", file=sys.stderr)
        for p in risky:
            print(f"    {p}", file=sys.stderr)
    found = targets(hit)
    if risky:
        # Unknown changes cannot be scoped honestly. The artifact lane can still stay narrower
        # than the docs/tests graph; an ordinary affected build takes the aggregate target.
        found = sorted(artifact_targets()) if args.artifacts else ["//:everything"]
    elif args.artifacts:
        found = sorted(set(found) & artifact_targets())
    if args.why:
        for t in found:
            reach = [p for p in hit if t in targets([p])]
            print(f"{t}\n    " + "\n    ".join(reach))
    else:
        write_targets(found)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
