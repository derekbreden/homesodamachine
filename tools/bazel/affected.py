#!/usr/bin/env python3
"""The targets a working tree's changes reach, for a build that holds only them.

    tools/cad-venv/bin/python tools/bazel/affected.py          # the targets, one per line
    tools/cad-venv/bin/python tools/bazel/affected.py --why    # each target, and what reaches it
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
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]


def _git(*args) -> list:
    out = subprocess.run(["git", "-C", str(_ROOT), *args],
                         capture_output=True, text=True).stdout
    return [l for l in out.splitlines() if l.strip()]


def changed() -> list:
    """Every path git reports as moved — staged, unstaged, and untracked alike.

    A build reads the worktree, so what is staged and what is merely saved reach it the same."""
    out = set()
    for line in _git("status", "--porcelain"):
        out.update(paths_in(line))
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
    q = subprocess.run(["bazel", "query", " + ".join(labels), "--keep_going"],
                       cwd=str(_ROOT), capture_output=True, text=True)
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
    # BAZEL IS THE ONE THING THIS CANNOT ASK FOR ITSELF. `known` and `targets` shell out to
    # `bazel query`, and a test bazel is running holds the server lock this workspace shares —
    # a query under it waits for the build that started it. The holds above stand on their own;
    # the three below are taken where a shell can reach bazel.
    if os.environ.get("TEST_SRCDIR"):
        print("  --   bazel query holds skipped: a query under `bazel test` waits on its own "
              "server. Run `affected.py selftest` from a shell for them.")
        print(f"affected selftest {holds}/{holds} (of the holds this run can take)")
        return 0 if holds == 3 else 1

    src = ["hardware/printed-parts/cold-core/foam-cap/foam_cap.py"]
    hit, miss = known(src)
    hold("a tracked source is a label bazel knows", hit == src, f"{hit!r} {miss!r}")
    t = targets(src)
    hold("a leaf part reaches its own target", "//:foam-cap" in t, str(t))
    hold("and not the whole graph", len(t) < 10, f"{len(t)} targets")
    hold("a path bazel does not name is reported, not dropped",
         known(["no/such/file.py"]) == ([], ["no/such/file.py"]))
    hold("nothing changed is no targets", targets([]) == [] and changed() is not None)
    print(f"affected selftest {holds}/8")
    return 0 if holds == 8 else 1


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
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()

    say_if_unshimmed()

    moved = changed()
    if not moved:
        print("nothing has moved — a build of this tree holds nothing to do", file=sys.stderr)
        return 0
    hit, miss = known(moved)
    if miss:
        print(f"{len(miss)} changed path(s) no target names — the list below is smaller than "
              f"this tree owes:", file=sys.stderr)
        for p in miss:
            print(f"    {p}", file=sys.stderr)
    found = targets(hit)
    if args.why:
        for t in found:
            reach = [p for p in hit if t in targets([p])]
            print(f"{t}\n    " + "\n    ".join(reach))
    else:
        print("\n".join(found))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
