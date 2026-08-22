#!/usr/bin/env python3
"""The solids this machine just cut, against the ones the lock names.

    tools/cad-venv/bin/python tools/cad-artifacts/cut_vs_lock.py
    tools/cad-venv/bin/python tools/cad-artifacts/cut_vs_lock.py --annotate   # in a workflow

WHAT IT IS FOR. `pack.py --check` walks the TREE, and on a runner the tree's solids came from
`web/scripts/fetch-cad-artifacts.mjs`, which downloaded the bundle the lock names — so it hashes
the lock's own bundle against the lock and reports agreement. That is a tautology, and it is why
every green on a runner has meant nothing. This walks `bazel-bin` instead: the bytes THIS
machine's OpenCASCADE cut, which nothing else in the pipeline ever hashes.

Two kernels on two operating systems either write the same STEP for the same model or they do
not. `_cadq_export` canonicalizes each one so that they can; whether they do is measurable and
has never been measured. That is the first thing this answers.

THE SECOND IS WHETHER THE TREE HOLDS WHAT THIS MACHINE CUTS, and it is free once the bytes are
in hand. The workflow runs this immediately after Bazel and before `sync_tree` carries declared
outputs, so the comparison measures the fetched/hand-cut tree against this build's exact bytes.

IT NEEDS NO CARRY, WHICH IS WHY IT EXISTS SEPARATELY. The bytes are on disk in `bazel-bin` the
moment the build goes green; reading them there preserves the pre-carry measurement and lets an
incomplete build fail before any tree file moves.

A DIFFERENCE HAS THREE CAUSES AND ONLY ONE OF THEM IS THE ANSWER. The bytes cannot say which:

  1. the kernels disagree — the question, and the only reading worth the words
  2. the lock is behind the tree's current source, so it names an older shape
  3. `bazel-bin` holds a STALE cut — bazel keeps whatever a target wrote the last time it ran,
     and a target not requested since is still sitting there under its old bytes

Three is not hypothetical: the first local run of this script reported six differences, and all
six were outputs two days old for targets that had not re-run. So the up-to-date check below is
not ceremony. It is the thing that separates a finding from an artifact of a warm output tree,
and without it this script would produce exactly the confident-and-wrong line the rest of the
pipeline kept producing.

NOTHING COMPARED IS NOT AGREEMENT. A run whose solid-cutting targets were all cache hits still
has bytes to read — a disk-cache hit is this configuration's own output — but a run that cut and
restored nothing has nothing, and the one thing this must never do is print a calm line then.
`compared == 0` is its own verdict, worded as the absence it is.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_LOCK = _ROOT / "hardware" / "cad-artifacts.lock.json"

#: An output is `…/bin/out/<target>/<the path the tree keeps it under>`, the same shape
#: `sync_tree` reads. The suffix is the lock's key.
_DECLARED = re.compile(r"/bin/out/([^/]+)/(.+)$")


def _bazel(*args: str, timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run(["bazel", *args], cwd=_ROOT, capture_output=True,
                          text=True, timeout=timeout)


def _bazel_bin() -> Path:
    """Where bazel cut, asked of bazel rather than guessed at."""
    try:
        q = _bazel("info", "bazel-bin", timeout=120)
        if q.returncode == 0 and q.stdout.strip():
            return Path(q.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    return _ROOT / "bazel-bin"


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _labels(raw: str) -> list:
    out = []
    for item in re.split(r"[\s,]+", raw.strip()):
        if item:
            out.append(item if item.startswith("//") else f"//:{item.lstrip(':')}")
    return sorted(set(out))


def _expected(labels: list, failed: set) -> set:
    """Publish outputs declared by a target slice, excluding failed writers."""
    query = f"deps(set({' '.join(labels)}))" if labels else "deps(//:everything)"
    q = _bazel("cquery", query, "--output=files", timeout=300)
    if q.returncode != 0:
        detail = next((line for line in q.stderr.splitlines() if line.startswith("ERROR")),
                      f"exit {q.returncode}")
        raise SystemExit(f"  the build graph could not name the expected cut: {detail}")
    out = set()
    for line in q.stdout.split():
        m = _DECLARED.search(line)
        if (m and m.group(1) not in failed
                and m.group(2).endswith((".step", ".stl", ".glb", ".step.mesh"))):
            out.add(m.group(2))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--annotate", action="store_true",
                    help="also emit GitHub workflow annotations")
    ap.add_argument("--failed", default="",
                    help="comma-separated targets that failed this build; their outputs are "
                         "whatever they wrote last time and are excluded")
    ap.add_argument("--assume-fresh", action="store_true",
                    help="skip the up-to-date check and trust bazel-bin. Only honest straight "
                         "after a full build in a container that starts empty.")
    ap.add_argument("--targets", default="",
                    help="compare this built slice and its dependencies; default: //:everything")
    args = ap.parse_args()

    def note(kind: str, title: str, text: str) -> None:
        if args.annotate:
            print(f"::{kind} title={title}::{text}")

    if not _LOCK.exists():
        print(f"  no lock at {_LOCK.relative_to(_ROOT)}, so there is nothing to compare against")
        return 2
    lock = json.loads(_LOCK.read_text()).get("solids", {})
    if not lock:
        print("  the lock names no solids, so there is nothing to compare against")
        return 2

    labels = _labels(args.targets)
    failed = {t.strip().lstrip("/").lstrip(":")
              for t in args.failed.split(",") if t.strip()}
    expected = _expected(labels, failed)
    if not expected:
        print("  NOTHING DECLARED: the requested target slice has no publishable outputs")
        note("warning", "cut-vs-lock", "nothing compared: target slice has no CAD outputs")
        return 3

    out = _bazel_bin() / "out"
    if not out.is_dir():
        print(f"  NOTHING CUT: {out} does not exist, so this build cut no solids to compare.")
        note("warning", "cut-vs-lock", "nothing compared: bazel-bin holds no outputs")
        return 3

    # IS WHAT IS SITTING THERE THIS TREE'S? Cause 3 above, and the only one askable of bazel.
    # `--check_up_to_date` builds nothing and returns 0 only if every output already matches its
    # inputs. It does NOT detect a target that failed this run — Manager established that, which
    # is what `--failed` is for — but it does detect the stale cut, which is what sank the first
    # run of this script.
    fresh = args.assume_fresh
    if not fresh:
        chk = _bazel("build", "--check_up_to_date", *(labels or ["//:everything"]))
        fresh = chk.returncode == 0
        if not fresh:
            print("  BAZEL-BIN IS NOT UP TO DATE with this tree, so some of what is sitting")
            print("  there was cut for an older source and a difference would say nothing")
            print("  about the kernels. Build the requested target slice first, or pass")
            print("  --assume-fresh if")
            print("  you know this output tree was written by the build that just ran.")
            for line in (chk.stderr or "").splitlines():
                if "not up to date" in line.lower():
                    print(f"      {line.strip()}")
            note("warning", "cut-vs-lock",
                 "bazel-bin is not up to date — nothing compared")
            return 3

    cut: dict[str, list[Path]] = {}
    skipped_failed = 0
    for p in out.rglob("*"):
        if not p.is_file():
            continue
        m = _DECLARED.search(p.as_posix())
        if not m or m.group(2) not in expected:
            continue
        if m.group(1) in failed:
            skipped_failed += 1
            continue
        cut.setdefault(m.group(2), []).append(p)

    absent = sorted(expected - set(cut))
    if absent:
        print(f"  INCOMPLETE CUT: {len(absent)} of {len(expected)} expected solid(s) are absent")
        for path in absent[:20]:
            print(f"      {path}")
        note("error", "cut-vs-lock", "the build did not materialize every expected solid")
        return 3

    # AND WHAT THE TREE HOLDS, which is a different question from the lock's and free to ask
    # here. Before the carry, the tree holds the fetched bundle or a hand cut while bazel-bin
    # holds this action's output. `stale` measures that gap directly.
    same, differ, fresh, twice, stale = [], [], [], [], []
    for tree_path, paths in sorted(cut.items()):
        digests = {_sha256(p) for p in paths}
        if len(digests) > 1:
            twice.append(tree_path)
            continue
        here = digests.pop()
        in_tree = _ROOT / tree_path
        if in_tree.exists() and _sha256(in_tree) != here:
            stale.append(tree_path)
        if tree_path not in lock:
            fresh.append(tree_path)
        else:
            (same if here == lock[tree_path] else differ).append(tree_path)

    compared = len(same) + len(differ)
    materialized = compared + len(fresh)
    steps = sum(1 for k in same + differ + fresh if k.endswith(".step"))

    # THE ABSENCE CASE COMES FIRST AND HAS ITS OWN WORDS, because the failure this pipeline
    # keeps producing is a reassuring line printed over a measurement that never happened.
    if materialized == 0:
        print(f"  NOTHING COMPARED — none of the {len(expected)} expected solids was found")
        print("  in bazel-bin. This is the absence of a measurement, not agreement.")
        if skipped_failed:
            print(f"  ({skipped_failed} held back as outputs of failed targets: "
                  f"{', '.join(sorted(failed))})")
        note("warning", "cut-vs-lock", "nothing compared: no solid of the lock's was cut")
        return 3

    print(f"  {materialized} of {len(expected)} expected solids were cut here and hashed "
          f"({steps} of them .step)")
    if skipped_failed:
        print(f"  {skipped_failed} held back as outputs of failed targets: "
              f"{', '.join(sorted(failed))}")
    if twice:
        print(f"  {len(twice)} cut by two targets that disagree with each other:")
        for k in twice[:10]:
            print(f"      {k}")
        note("error", "cut-vs-lock", "two actions produced disagreeing bytes for one output")
        return 3

    if materialized != len(expected):
        print(f"  INCOMPLETE COMPARISON: {len(expected) - materialized} expected solid(s) were not hashed")
        note("error", "cut-vs-lock", "not every expected solid was compared")
        return 3

    if fresh:
        print(f"  {len(fresh)} are new outputs with no historical lock member:")
        for k in fresh[:20]:
            print(f"      {k}")

    if differ:
        print(f"  {len(differ)} DIFFER from the lock:")
        for k in differ[:20]:
            print(f"      {k}")
            print(f"        lock {lock[k][:16]}   cut here {_sha256(cut[k][0])[:16]}")
        if len(differ) > 20:
            print(f"      …and {len(differ) - 20} more")
        print()
        print("  THE BYTES DO NOT SAY WHY THEY DIFFER. Either this machine's OpenCASCADE")
        print("  writes different bytes than the one that packed the lock, or the lock is")
        print("  simply behind the tree's current source for these parts.")
        if args.assume_fresh:
            # THE THIRD CAUSE IS NOT EXCLUDED HERE AND MUST NOT BE CLAIMED AS SUCH. The check
            # that rules out a stale cut was skipped by --assume-fresh, so this is three
            # readings, not two, and the caller asserted away the one it is cheapest to be
            # wrong about.
            print("  And a THIRD: --assume-fresh skipped the up-to-date check, so an output")
            print("  bazel kept from an older run has not been ruled out. On this evidence")
            print("  that is the likeliest of the three, not the least.")
        else:
            print("  bazel-bin is up to date, so a stale cut is excluded — but a lock older")
            print("  than the geometry is not.")
        print("  What separates the readings: run this on BOTH machines at the")
        print("  same commit. Same `cut here` hashes on both means the lock is behind and the")
        print("  kernels agree; different ones means the kernels disagree, and then the lock")
        print("  belongs to whichever machine packs it — a repin here pins these bytes and the")
        print("  next repin there pins them back, every lap.")
        note("warning", "cut-vs-lock",
             f"{len(differ)} of {compared} solids differ from the lock "
             f"— compare against the other machine's cut hashes to read it")
        _tree_verdict(stale, compared, note)
        return 1

    if fresh:
        print()
        if same:
            print(f"  THE {len(same)} EXISTING SOLIDS MATCH THE LOCK; the {len(fresh)} new "
                  "output(s) are ready to be pinned.")
        else:
            print("  EVERY OUTPUT IS NEW; there are no historical lock bytes to compare.")
        _tree_verdict(stale, materialized, note)
        return 1

    print()
    print("  EVERY SOLID CUT HERE MATCHES THE LOCK, byte for byte. This machine's OpenCASCADE")
    print("  and the one that packed the lock agree, so a lock is a fact about the geometry")
    print("  rather than about the machine that packed it.")
    note("notice", "cut-vs-lock",
         f"{compared} solids cut here match the lock byte for byte ({steps} .step)")
    return _tree_verdict(stale, materialized, note)


def _tree_verdict(stale, compared, note) -> int:
    """What the tree holds against what this machine cuts, said after the lock's verdict.

    A SOLID IN THE TREE IS NOT EVIDENCE OF THE SOURCE THAT NAMES IT. Every scorecard, mass and
    picture is read off the tree's copy, so one cut for an older source is a whole card's worth
    of confident readings about a shape the generator no longer makes — and mtime answers
    neither direction: older than the commit naming its source and still right, newer and still
    wrong."""
    if not stale:
        print()
        print(f"  THE TREE HOLDS WHAT THIS BUILD CUT for all {compared}, so every card, mass")
        print("  and picture read off it describes the shape the generators now make.")
        return 0
    print()
    print(f"  BUT {len(stale)} OF THEM ARE NOT WHAT THE TREE HOLDS:")
    for k in stale[:20]:
        print(f"      {k}")
    if len(stale) > 20:
        print(f"      …and {len(stale) - 20} more")
    print()
    print("  Every check that reads a solid reads the tree's copy, and these two disagree.")
    print("  WHICH SIDE IS BEHIND IS NOT IN THE BYTES. Before sync_tree runs, the tree holds")
    print("  the fetched bundle or the last hand cut, while bazel-bin holds this build's cut.")
    print("  The latter is only as good as the source that action read:")
    print("  a generator or a module dirty in the worktree cuts bytes no commit reproduces.")
    print("  `git status` over what the cutting run imports is what separates them.")
    note("warning", "cut-vs-lock",
         f"{len(stale)} solids in the tree differ from what this build cut")
    return 1


if __name__ == "__main__":
    sys.exit(main())
