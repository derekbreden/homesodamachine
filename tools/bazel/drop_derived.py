#!/usr/bin/env python3
"""Restore the dirty files a rebuild would write anyway, so a rebase has room.

    python3 tools/bazel/drop_derived.py            # name them
    python3 tools/bazel/drop_derived.py --write    # and `git checkout --` them

A rebase refuses against a dirty worktree — not only for the files it touches, for ANY
unstaged change. Several sessions building at once keep this tree permanently dirty in the
artifacts they all rewrite, so `git pull --rebase` is never available and the divergence
grows all night. What clears it is not waiting: it is dropping the changes that carry no
information, because the build writes them again from the same sources.

WHAT IS SAFE TO DROP IS WHAT A REBUILD REPRODUCES, and `graph.json` names most of it — every
path a traced generator `writes` or is `rewritten` in. Those files are a function of the
sources beside them, so a copy differing from HEAD only says a build ran here since.

ONE CLASS THE GRAPH CANNOT NAME. The printed deck's pictures are drawn by a browser the graph
does not model, so they are listed here by path rather than read out of it — and they matter,
because they are binary and every session's build rewrites them, which is the shape that
collides.

WHAT IS NEVER DROPPED IS ANYTHING AUTHORED, and the test is not the extension. `_KEEP` holds
three cases that read as derived and are not. A `.py` under `hardware/` is somebody's geometry
mid-edit whatever else writes figures into it. `graph.json` is where a trace lands, so a
session partway through `trace_inputs.py` has its whole result sitting in a file this would
otherwise call regenerable. And a `.step.png` is half of a pair whose other half is an ignored
`.step` on the disk that nothing here restores — drop the picture alone and the solid it is
held against by `check_thumbnails.py` is still the new one, so a clean tree becomes a red gate.

Anything this cannot place stays too — a file it does not recognise is a file it does not
touch. WHAT IS LEFT IS FOR `--autostash` TO CARRY, and that is the division: this drops what
nobody would miss, so the stash holds only work worth a conflict.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]

#: Drawn by the deck's browser, declared as an output by nothing.
_UNDECLARED = ("hardware/assembly/cards/out/*.png",)

#: Authored, or holding a result no rebuild reproduces, whatever else writes into it.
_KEEP = ("hardware/**/*.py", "tools/bazel/graph.json", "hardware/**/*.step.png")


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(_ROOT), *args], capture_output=True, text=True, check=True
    ).stdout


def _made_by_the_build() -> set[str]:
    graph = json.loads((_ROOT / "tools/bazel/graph.json").read_text())
    made: set[str] = set()
    for step in graph.values():
        made |= set(step.get("writes", ())) | set(step.get("rewritten", ()))
    return made


def _split(dirty: list[str]) -> tuple[list[str], list[str]]:
    made = _made_by_the_build()
    drop, keep = [], []
    for path in dirty:
        p = Path(path)
        if any(p.full_match(k) for k in _KEEP):
            keep.append(path)
        elif path in made or any(p.full_match(u) for u in _UNDECLARED):
            drop.append(path)
        else:
            keep.append(path)
    return drop, keep


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--write", action="store_true", help="restore them, rather than naming them"
    )
    args = ap.parse_args()

    dirty = [p for p in _git("diff", "--name-only").split("\n") if p]
    if not dirty:
        print("the worktree carries no unstaged change — a rebase has room already")
        return 0

    drop, keep = _split(dirty)

    if keep:
        print(f"{len(keep)} left alone, because a rebuild does not write them:")
        for path in keep:
            print(f"    {path}")
    if not drop:
        print("nothing here is the build's — a rebase still has no room")
        return 0

    verb = "restored" if args.write else "would be restored"
    print(f"\n{len(drop)} {verb}, because the build writes them from the sources beside them:")
    for path in drop:
        print(f"    {path}")

    if not args.write:
        print("\n--write to restore them")
        return 0

    # One call: a path that has since been staged or removed fails the whole checkout rather
    # than leaving half the set restored and the rebase still refusing.
    _git("checkout", "--", *drop)
    print(f"\n{len(drop)} restored. `git pull --rebase --autostash` now has room.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
