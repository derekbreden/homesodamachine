#!/usr/bin/env python3
"""Whether an uncommitted path no generator reads can record the whole bundle unproven.

`pack.py` writes `unproven` for the members `source.commit` does not describe, and it has one
blanket: where an uncommitted path is neither a label bazel can walk nor a path the graph
explains, nothing says which members it reaches, so every member goes in. That blanket is right
for a mid-edit generator and wrong for a photograph. An export dropped under `hardware/` opens
no action, and the lock that answers "where did this solid come from" then says "nowhere" about
all of them — for a file the machine is not made of.

WHAT MAKES A KIND BOUNDING IS THE GRAPH. `tools/bazel/graph.json` records the files each
generator was traced opening, so a suffix absent from every `reads` is a kind no generator has
code to open — not by a path it spells, not by a glob over a directory. One more file of it
moves no action's inputs. `affected.read_kind` asks exactly that, and this holds the answer
against the tree: every uncommitted path under `hardware/` of a kind nothing reads, and whether
it widens the artifact slice. None may.

IT ASKS BAZEL NOTHING. `_dirty_artifact_reach` runs `known()` first and tests only what bazel
could not name. A path of a kind no generator reads is a source label of no rule — `srcs` are
written from the same `reads` — so testing it without that split can over-report and cannot
under-report, and a red here is a real one.

THE OTHER HALF IS THE READ ITSELF. `status` answers the worktree half from stat data, so a
cancelled edit reads as dirt, and dirt that bounds nothing blankets everything. `changed()`
asks HEAD for content instead, and asks with `--no-optional-locks`, so a peer session holding
`.git/index.lock` is survived and not fatal. `selftest` holds both against a scratch repo it
builds, where an index lock can be taken without waiting for anyone.

    tools/cad-venv/bin/python tools/bazel/check_unbounded_reach.py
    tools/cad-venv/bin/python tools/bazel/check_unbounded_reach.py selftest
"""

import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
sys.path.insert(0, str(_ROOT / "tools" / "bazel"))

import affected  # noqa: E402

_PACK = _ROOT / "tools" / "cad-artifacts" / "pack.py"


def pack():
    """`pack.py` as a module — the same file the publisher runs, on no import path of its own."""
    spec = importlib.util.spec_from_file_location("cad_artifacts_pack", _PACK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def unread(paths) -> list:
    """The `hardware/` paths whose kind no generator reads."""
    return sorted(p for p in paths if p.startswith("hardware/") and not affected.read_kind(p))


def widens(path: str) -> bool:
    """Whether an uncommitted `path` bazel cannot name puts every member in `unproven`.

    The union `_dirty_artifact_reach` calls `unbounded`, asked of one path."""
    return affected.artifact_global(path) or affected.artifact_unknown(path, artifacts_only=True)


def _scratch_repo(where: Path) -> None:
    """A repo holding one committed file, for holds about reading a working tree."""
    def git(*args):
        subprocess.run(["git", "-C", str(where), *args], check=True,
                       capture_output=True, text=True)

    git("init", "-q", "-b", "main")
    git("config", "user.email", "check@example.invalid")
    git("config", "user.name", "check")
    (where / "f.txt").write_text("a\n")
    git("add", "f.txt")
    git("commit", "-qm", "one")


def selftest() -> int:
    holds = 0

    def hold(label, ok, got=""):
        nonlocal holds
        holds += bool(ok)
        print(f"  {'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f" — {got}"))

    photo = "hardware/off-the-shelf-parts/C14 - 1.jpeg"
    hold("a photograph is a kind no generator reads", not affected.read_kind(photo))
    hold("and it widens nothing", not widens(photo))
    hold("a generator and a solid are kinds that do read, and still widen",
         affected.read_kind("hardware/new_part.py")
         and affected.read_kind("hardware/off-the-shelf-parts/new.step")
         and widens("hardware/new_part.py")
         and widens("hardware/off-the-shelf-parts/new.step"))

    # END TO END, THROUGH THE FUNCTION THAT ARMS THE BLANKET, over a stated tree.
    #
    # `known()` shells out to `bazel query`, which under a running build waits on that build;
    # what it answers for an untracked path is that bazel does not name it, and that is the
    # premise here rather than a result. `artifact_targets()` walks the whole tracked inventory
    # to name the rules the FIRST return value holds, which is 1199 files of declared test data
    # for a set no hold below reads. `unbounded` is the answer these ask for, and nothing
    # stated here feeds it.
    def reach(moved):
        was = (affected.changed, affected.known, affected.artifact_targets)
        affected.changed = lambda root=None: sorted(moved)
        affected.known = lambda paths: ([], list(paths))
        affected.artifact_targets = set
        try:
            return pack()._dirty_artifact_reach(_ROOT)
        finally:
            affected.changed, affected.known, affected.artifact_targets = was

    _, unbounded, dirty = reach([photo])
    hold("a tree dirty with photographs alone bounds nothing",
         unbounded == [] and dirty == [photo], f"{unbounded!r} {dirty!r}")
    _, unbounded, _ = reach([photo, "hardware/new_part.py"])
    hold("and one unlabelled generator beside them still bounds everything",
         unbounded == ["hardware/new_part.py"], repr(unbounded))

    with tempfile.TemporaryDirectory() as d:
        empty = Path(d)
        was_root = affected._ROOT
        affected._read_kinds.cache_clear()
        try:
            affected._ROOT = empty
            no_graph = affected.read_kind(photo)
        finally:
            affected._ROOT = was_root
            affected._read_kinds.cache_clear()
        hold("no graph to read, and every kind bounds again", no_graph)

    with tempfile.TemporaryDirectory() as d:
        repo = Path(d)
        _scratch_repo(repo)
        # A staged edit and an unstaged one that cancel: the index stands off HEAD, the worktree
        # does not. `status` calls that path modified twice over; a build sees nothing to do.
        (repo / "f.txt").write_text("b\n")
        subprocess.run(["git", "-C", str(repo), "add", "f.txt"], check=True,
                       capture_output=True, text=True)
        (repo / "f.txt").write_text("a\n")
        porcelain = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"],
                                   capture_output=True, text=True).stdout.split()
        hold("a cancelled edit is dirt to status and nothing to this read",
             "f.txt" in porcelain and affected.changed(repo) == [],
             f"{porcelain!r} {affected.changed(repo)!r}")

        (repo / "C14 - 1.jpeg").write_bytes(b"\xff\xd8\xff")
        (repo / ".git" / "index.lock").write_text("")
        try:
            named = affected.changed(repo)
        except SystemExit as exc:
            named = f"died: {exc}"
        hold("a peer holding the index lock is survived, not fatal",
             named == ["C14 - 1.jpeg"], repr(named))

    print(f"check_unbounded_reach selftest {holds}/8")
    return 0 if holds == 8 else 1


def main(argv) -> int:
    if argv and argv[0] == "selftest":
        return selftest()
    moved = affected.changed(_ROOT)
    quiet = unread(moved)
    loud = [path for path in quiet if widens(path)]
    members = len(pack().solids(_ROOT))
    if not loud:
        print(f"check_unbounded_reach: {len(quiet)} of {len(moved)} uncommitted path(s) are a "
              f"kind no generator reads, and none widens the artifact slice — "
              f"{members} member(s) keep their provenance")
        return 0
    print(f"{len(loud)} uncommitted path(s) of a kind no generator reads would put all "
          f"{members} bundle member(s) in `unproven`:")
    for path in loud:
        print(f"    {path}")
    print("  A kind absent from every `reads` in tools/bazel/graph.json is a kind no generator")
    print("  opens, and a file of it reaches no action. `affected.read_kind` says which:")
    print("    tools/cad-venv/bin/python tools/bazel/affected.py selftest")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
