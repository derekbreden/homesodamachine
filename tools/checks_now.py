#!/usr/bin/env python3
"""checks_now.py — run every check after a commit and put the answer where it is looked at.

    tools/cad-venv/bin/python tools/checks_now.py           read this tree, commit what changed
    tools/cad-venv/bin/python tools/checks_now.py --check    say what it would do, touch nothing

A CHECK NOBODY RUNS IS A CHECK THAT DOES NOT EXIST. `tools/checks.py` was written so a red
would be visible without someone deciding to look, and wired into `derive.yml`, which is
`workflow_dispatch` — so it ran nowhere, and two checks stood red for a day and a half with
nothing anywhere saying so. This is the caller that makes it true: the commit that changes the
tree is what asks the tree how it is doing.

THE ANSWER GOES TO THE SITE, BECAUSE THAT IS THE SURFACE THAT IS READ. `web/public/checks.json`
is under `render.yaml`'s buildFilter, so committing it deploys, and `web/lib/shell.js` draws a
red band on every page while any check is red and nothing at all while none is. A terminal line
in a detached log is a place a red can sit unread, which is the failure this replaces.

IT REPORTS AND HOLDS NOTHING. The commit is already made and pushed by the time this runs; a
red is a reading that rides to the site, never a reason to keep the tree from reaching it.
CLAUDE.md, "Nothing withholds".

ONE AT A TIME, AND THE LAST REQUEST WINS — `publish_now.py`'s arrangement, for its reason.
Several sessions commit at once, so a second invocation marks the running one to read again
rather than queueing behind it, and what gets reported is the newest tree.

THE TREE IS BEING WRITTEN WHILE IT IS READ, AND THE READING SAYS SO BY BEING TAKEN AGAIN. Six
sessions edit this checkout and `publish_now.py` runs from the same hook, recutting payloads
while this reads them — so a verdict can name a red that a repair already fixed, or miss one
that landed a second later. Every commit takes another reading, which is the only thing that
could be true of a tree nobody is holding still. Coupling this to the publish would buy a
tidier answer for a wait of up to four minutes, and a reading that is late is a reading nobody
acts on.

THE RECURSION ENDS ON THE MESSAGE, NOT ON THE BYTES. This commits, and a commit runs
`post-commit`, which runs this. An unchanged verdict writes identical bytes and stops there —
but a check whose output carries anything volatile would not, and would push a commit for every
commit forever. So a tree whose HEAD is already one of these is left alone: the reading it
carries was taken from the same content, and taking it again answers nothing.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True).stdout.strip() or ".")
PY = ROOT / "tools" / "cad-venv" / "bin" / "python"
OUT = ROOT / "web" / "public" / "checks.json"
REL = "web/public/checks.json"
LOCK = ROOT / ".cache" / "checks-now.lock"
AGAIN = ROOT / ".cache" / "checks-now.again"
MSG = "checks: the reading this commit's tree gives"


def run(args: list, quiet: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(ROOT), text=True, capture_output=quiet)


def head_is_ours() -> bool:
    """Whether HEAD is already one of these commits — see the docstring's last paragraph."""
    got = run(["git", "log", "-1", "--format=%s"], quiet=True)
    return got.stdout.strip() == MSG


def read() -> bool:
    """Run every check into the served file. True when a check is red."""
    return run([str(PY), "tools/checks.py", "--json", str(OUT)], quiet=True).returncode != 0


def changed() -> bool:
    """Whether the verdict differs from the one this commit already carries.

    `--quiet` exits 1 on a difference, and an untracked file is not a difference to `git diff`
    at all — so the first run, which creates the file, is asked separately.
    """
    if run(["git", "ls-files", "--error-unmatch", REL], quiet=True).returncode != 0:
        return True
    return run(["git", "diff", "--quiet", "HEAD", "--", REL], quiet=True).returncode != 0


def land() -> int:
    """Commit the verdict. `--only` keeps it to this file whatever else the tree holds, and
    `--no-verify` skips the pre-commit re-derive, which has nothing to say about a reading.

    THE INDEX IS SHARED AND SO IS THE RACE. `publish_now.py` runs detached from the same hook
    and commits the lock, so both can reach `index.lock` at once. A loss here is not a failure
    worth reporting as one: the next commit in this tree runs this again, off content that has
    not changed, and lands the same reading.
    """
    for attempt in range(3):
        run(["git", "add", REL], quiet=True)
        if run(["git", "commit", "--no-verify", "--only", REL, "-m", MSG],
               quiet=True).returncode == 0:
            return 0
        time.sleep(1.5 * (attempt + 1))
    print("  the reading did not commit; the next commit takes it", file=sys.stderr)
    return 1


def once() -> int:
    started = time.time()
    if head_is_ours():
        print("  HEAD is already a reading of this content — nothing to ask")
        return 0
    red = read()
    took = time.time() - started
    if not changed():
        print(f"  {'red' if red else 'green'}, and unchanged from what this commit carries "
              f"({took:.0f}s)")
        return 0
    print(f"  {'RED — the site says so on every page' if red else 'green again'}, "
          f"pinning the reading ({took:.0f}s)")
    return land()


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    LOCK.parent.mkdir(parents=True, exist_ok=True)
    if args.check:
        if head_is_ours():
            print("  --check: HEAD is already a reading of this content")
            return 0
        red = read()
        print(f"  --check: {'red' if red else 'green'}, "
              f"{'would pin it' if changed() else 'unchanged from this commit'}")
        return 0

    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        AGAIN.touch()
        print("  a read is already running — it will read the tree again when it finishes")
        return 0
    os.write(fd, str(os.getpid()).encode())
    os.close(fd)
    try:
        code = once()
        while AGAIN.exists():
            AGAIN.unlink(missing_ok=True)
            print("  a commit landed while that ran — reading the tree again")
            code = once()
        return code
    finally:
        LOCK.unlink(missing_ok=True)
        AGAIN.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
