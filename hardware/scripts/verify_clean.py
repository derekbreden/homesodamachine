#!/usr/bin/env python3
"""verify_clean.py — every figure in a commit, re-derived from nothing.

    python3 hardware/scripts/verify_clean.py           # HEAD
    python3 hardware/scripts/verify_clean.py <rev>     # any commit
    python3 hardware/scripts/verify_clean.py --keep    # leave the worktree to look at

A commit is checked out into a worktree of its own, `owed.py --run` is run there, and what
that leaves is compared against what was checked out. The verdict is `git status`: a commit
whose docs, cards and pictures are the ones its sources make comes back with nothing to say.

WHAT MAKES IT A DIFFERENT READING FROM THE ONE THE HOOK TAKES is the empty `.cache/`. A
stamp is one machine's note that it watched a generator run; a fresh tree has none, so every
generator runs and every figure is measured again rather than compared to a hash of what
measured it last. The working tree here is also the commit's own — a file that never reached
the index is absent, whatever sits beside it on the disk this ran from.

The venv is linked in rather than built: it is one interpreter and the packages under it,
and nothing this checks lives there.
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

_HERE = Path(__file__).resolve()
_HW = next(p for p in _HERE.parents if p.name == "hardware")
_ROOT = _HW.parent
_VENV = _ROOT / "tools" / "cad-venv"


def _git(*args, cwd=None, check=True):
    return subprocess.run(["git", "-C", str(cwd or _ROOT), *args],
                          capture_output=True, text=True, check=check).stdout


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rev", nargs="?", default="HEAD", help="the commit to verify")
    ap.add_argument("--keep", action="store_true", help="leave the worktree in place")
    args = ap.parse_args()

    sha = _git("rev-parse", "--short", args.rev).strip()
    subject = _git("log", "-1", "--format=%s", sha).strip()
    print(f"verifying {sha}  {subject}")

    wt = Path(tempfile.mkdtemp(prefix=f"hsm-verify-{sha}-"))
    shutil.rmtree(wt)                                   # git wants to make it itself
    _git("worktree", "add", "-q", "--detach", str(wt), sha)
    try:
        (wt / "tools" / "cad-venv").symlink_to(_VENV)

        t0 = time.time()
        run = subprocess.run([sys.executable, "hardware/scripts/owed.py", "--run"],
                             cwd=str(wt), capture_output=True, text=True)
        took = time.time() - t0
        tail = [ln for ln in run.stdout.splitlines() if ln.strip()][-1:]
        print(f"  {int(took)}s  " + (tail[0].strip() if tail else "owed.py said nothing"))
        if run.returncode != 0:
            print(run.stdout[-2000:] or run.stderr[-2000:])

        # WHAT IT LEFT, against what it was handed. `--porcelain` names a tracked file that
        # moved and an untracked one that arrived; `.gitignore` holds the caches and the
        # rendering intermediates, so what is left is the tree's own answer.
        moved = _git("status", "--porcelain", cwd=wt).splitlines()
        if moved:
            print(f"\n  {len(moved)} file(s) are not what {sha} says they are:")
            for line in moved[:20]:
                print(f"    {line}")
            if len(moved) > 20:
                print(f"    …and {len(moved) - 20} more")
            print(f"\n  the diff: git -C {wt} diff")
        else:
            print(f"  every figure, card and picture in {sha} is the one its sources make")
        return 1 if (moved or run.returncode != 0) else 0
    finally:
        if args.keep:
            print(f"  worktree kept at {wt}")
        else:
            (wt / "tools" / "cad-venv").unlink(missing_ok=True)
            _git("worktree", "remove", "--force", str(wt), check=False)


if __name__ == "__main__":
    raise SystemExit(main())
