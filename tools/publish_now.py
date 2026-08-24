#!/usr/bin/env python3
"""publish_now.py — cut and pin from this machine, so the site does not wait on a runner.

    tools/cad-venv/bin/python tools/publish_now.py           publish if this tree owes a cut
    tools/cad-venv/bin/python tools/publish_now.py --check    say what it would do, touch nothing

THE LAPTOP IS THE PATH AND THE RUNNER IS THE RECONCILER. `pack.py --write` builds what is owed,
uploads the bundle and pins the lock, and moving the lock is what Render deploys on. A CAD
change that waits for CI to do that instead is measured at 5.7 minutes from commit to visible,
4.2 of them spent between the commit and the runner's lock push; the same publish from here
reaches the site in about two.

OWED IS READ BEFORE ANYTHING IS BUILT, AND IT IS TWO QUESTIONS. `affected.py --artifacts` from
the commit the lock names to HEAD reads SOURCE, and is the only one that sees a change whose
target has not been built yet. `pack.py --check` reads BYTES, and is the only one that sees a
solid whose bytes moved with no commit behind them. Neither owing anything means `--write` would
re-hash 314 MB to arrive at the bundle already published.

ONE AT A TIME, AND THE LAST REQUEST WINS. Several sessions commit at once and a publish takes
around a minute, so a second invocation while one is running does not queue behind it — it
marks the running one to look again when it finishes. Whatever is owed at that point is what
gets cut, which is the newest state rather than the one that asked.

IT REPORTS AND HOLDS NOTHING. Nothing here is in front of a commit or a push; the work is
already on main by the time this runs, and a publish that fails leaves the runner to do what it
was always going to do.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True).stdout.strip() or ".")
PY = ROOT / "tools" / "cad-venv" / "bin" / "python"
LOCK = ROOT / ".cache" / "publish-now.lock"
AGAIN = ROOT / ".cache" / "publish-now.again"


def run(args: list, quiet: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(ROOT), text=True,
                          capture_output=quiet)


def source_owes() -> list:
    """Artifact rules whose sources moved since the commit the lock names."""
    lock = ROOT / "hardware" / "cad-artifacts.lock.json"
    if not lock.exists():
        return ["//:everything"]
    base = json.loads(lock.read_text()).get("source", {}).get("commit", "")
    if not base or run(["git", "cat-file", "-t", base], quiet=True).returncode != 0:
        return ["//:everything"]
    got = run([str(PY), "tools/bazel/affected.py", "--artifacts",
               "--base", base, "--head", "HEAD"], quiet=True)
    return [ln for ln in got.stdout.split() if ln.startswith("//")]


def bytes_drifted() -> bool:
    """Whether the solids on this disk are the ones the lock names. `--check` exits 1 when not."""
    return run([str(PY), "tools/cad-artifacts/pack.py", "--check"],
               quiet=True).returncode == 1


def owed() -> tuple:
    """`(reason, targets)` — why this tree owes a publish, and what moved.

    TWO QUESTIONS, AND NEITHER ANSWERS THE OTHER. `affected` reads SOURCE: it names what a
    commit changed, and it is the only one that sees a change whose target has not been built
    yet. `pack.py --check` reads BYTES: it hashes the tree against the lock, and it is the only
    one that sees a solid whose bytes moved with no commit behind them — a rebuild, a carry, or
    a payload recut. Asking only the first is how a tree that had lost the enclosure's flutes
    read as owing nothing while the site drew a smooth box."""
    targets = source_owes()
    if targets:
        return (f"{len(targets)} artifact target(s) owed since the lock's source", targets)
    if bytes_drifted():
        return ("the solids on this disk are not the ones the lock names", [])
    return ("", [])


def publish() -> int:
    started = time.time()
    reason, targets = owed()
    if not reason:
        print("  nothing owed — this tree's solids are the ones the lock names")
        return 0
    print(f"  {reason}; cutting here")
    if run([str(PY), "tools/cad-artifacts/pack.py", "--write"]).returncode != 0:
        print("  --write did not finish; the runner still reconciles this", file=sys.stderr)
        return 1
    if run(["git", "diff", "--quiet", "--", "hardware/cad-artifacts.lock.json"],
           quiet=True).returncode == 0:
        print(f"  the cut is the one already published ({time.time() - started:.0f}s)")
        return 0
    run(["git", "add", "hardware/cad-artifacts.lock.json"], quiet=True)
    # `--no-verify`: the pre-commit hook re-derives and stages, and this commit is one file by
    # name. `--only` keeps it that way whatever else the tree is holding.
    msg = "cad-artifacts: cut and pinned from the machine that changed it"
    if run(["git", "commit", "--no-verify", "--only",
            "hardware/cad-artifacts.lock.json", "-m", msg], quiet=True).returncode != 0:
        print("  the lock did not commit", file=sys.stderr)
        return 1
    print(f"  lock pinned and pushed ({time.time() - started:.0f}s)")
    return 0


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    LOCK.parent.mkdir(parents=True, exist_ok=True)
    if args.check:
        reason, _ = owed()
        print(f"  --check: {reason}" if reason else "  --check: nothing owed")
        return 0

    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        AGAIN.touch()
        print("  a publish is already running — it will read the tree again when it finishes")
        return 0
    os.write(fd, str(os.getpid()).encode())
    os.close(fd)
    try:
        code = publish()
        while AGAIN.exists():
            AGAIN.unlink(missing_ok=True)
            print("  a commit landed while that ran — reading the tree again")
            code = publish()
        return code
    finally:
        LOCK.unlink(missing_ok=True)
        AGAIN.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
