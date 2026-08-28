#!/usr/bin/env python3
"""publish_now.py — cut and pin from this machine, so the site does not wait on a runner.

    tools/cad-venv/bin/python tools/publish_now.py           publish if this tree owes a cut
    tools/cad-venv/bin/python tools/publish_now.py --check    say what it would do, touch nothing

THE LAPTOP IS THE PATH AND THE RUNNER IS THE RECONCILER. `pack.py --write` builds what is owed,
uploads the bundle and pins the lock. A CAD change that waits for CI to do that instead is
measured at 5.7 minutes from commit to visible, 4.2 of them spent between the commit and the
runner's lock push.

PINNING THE LOCK DEPLOYS NOTHING. It is not among `render.yaml`'s buildFilter paths: the
running container adopts a lock that moved and pushes the changed members to open pages.
`tell_the_site()` below is what makes that immediate rather than a poll away.

OWED IS READ BEFORE ANYTHING IS BUILT, AND IT IS TWO QUESTIONS. `affected.py --artifacts` from
the commit the lock names to HEAD reads SOURCE, and is the only one that sees a change whose
target has not been built yet. `pack.py --check` reads BYTES, and is the only one that sees a
solid whose bytes moved with no commit behind them. Neither owing anything means `--write` would
re-hash 314 MB to arrive at the bundle already published.

ONE AT A TIME, AND THE LAST REQUEST WINS. Several sessions commit at once and a publish takes
around a minute, so a second invocation while one is running does not queue behind it — it
marks the running one to look again when it finishes. Whatever is owed at that point is what
gets cut, which is the newest state rather than the one that asked.

IT REPORTS AND HOLDS NOTHING. The geometry's own commits are already on main by the time this
runs; the one commit this makes is the lock, and it goes to main through `push.py` before the
site is told anything. A publish that fails leaves the runner to do what it was always going to
do.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
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


def repair_flutes() -> None:
    """Recut and carry the enclosure payloads when they no longer draw their print.

    `check_flutes` reads the distance from each payload to the mesh its piece prints, and a
    payload standing a flute's depth away draws a part that does not exist. The flute cut is one
    bazel target and a carry, and then the site gets the part.

    WHAT DOES NOT SETTLE IS PUBLISHED ANYWAY, and said. CLAUDE.md, "Nothing withholds".
    """
    if run([str(PY), "hardware/scripts/check_flutes.py"], quiet=True).returncode == 0:
        return
    print("  payloads have drifted from the print they draw — recutting before the pack")
    run(["bazel", "build", "//:flute-payload", "//:enclosure-assembly", "//:enclosure"],
        quiet=True)
    run([str(PY), "tools/bazel/sync_tree.py", "--write", "--targets",
         "//:flute-payload,//:enclosure-assembly,//:enclosure"], quiet=True)
    settled = run([str(PY), "hardware/scripts/check_flutes.py"], quiet=True).returncode == 0
    print("  flutes recut and carried" if settled else
          "  recut did not settle them; publishing what the tree holds")


def tell_the_site() -> None:
    """Ask the running site to look at the lock now, rather than at its next poll.

    THE LOCK IS NOT IN `render.yaml`'s buildFilter, so pinning it deploys nothing — the container
    adopts it in place and pushes the changed members to open pages. It finds out on a two-minute
    poll on its own; this is what makes the usual case seconds instead.

    IT CARRIES NOTHING AND IS TRUSTED WITH NOTHING. The site reads the lock from GitHub either
    way, so this says only "look now" — and it is why the lock is on main before this is called,
    since a container sent to look at a commit that is not there reads the previous cut and then
    waits out a poll. A post that does not arrive costs a poll, which is why nothing here is
    retried and nothing here fails a publish.
    """
    try:
        urllib.request.urlopen(
            urllib.request.Request("https://homesodamachine.com/api/artifacts/refresh",
                                   data=b"", method="POST"),
            timeout=10).read()
        print("  the site is looking")
    except Exception as e:  # noqa: BLE001 — a site that did not answer still polls
        print(f"  could not reach the site ({e}); it polls every 2 min")


def publish() -> int:
    started = time.time()
    repair_flutes()
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
    # THE SITE READS THE LOCK FROM MAIN, so a commit that has not landed there is a cut nobody
    # can see and a `tell_the_site()` that sends the container to look at bytes that are not
    # up yet. `push.py` is the reconcile: it fetches, settles a lost race in a detached
    # worktree that shares no index with this one, and exits 0 only when the work is on the
    # remote. Anything short of that leaves the cut to the runner, which is where it was.
    if run([str(PY), "tools/push.py"]).returncode != 0:
        print(f"  the lock is committed and not on main; the runner reconciles this "
              f"({time.time() - started:.0f}s)", file=sys.stderr)
        return 1
    print(f"  lock pinned and pushed ({time.time() - started:.0f}s)")
    tell_the_site()
    return 0


def holder() -> int:
    """The pid the marker names, or 0 where there is none to read."""
    try:
        return int(LOCK.read_text().strip())
    except (OSError, ValueError):
        return 0


def alive(pid: int) -> bool:
    """Whether that process is still on this machine.

    THE MARKER OUTLIVES A PUBLISH THAT IS KILLED. `finally` drops it when the process gets to
    run its own unwinding, and a SIGKILL, a panic or a machine that sleeps hard is where it does
    not — after which every publish reads a marker whose pid is gone and stands down for it.
    That is a tree that stops reaching the site and says only that someone else is going."""
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    LOCK.parent.mkdir(parents=True, exist_ok=True)
    if args.check:
        reason, _ = owed()
        print(f"  --check: {reason}" if reason else "  --check: nothing owed")
        return 0

    fd = None
    for _ in range(2):
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            held = holder()
            if alive(held):
                AGAIN.touch()
                print("  a publish is already running — it will read the tree "
                      "again when it finishes")
                return 0
            print(f"  a publish left its marker behind (pid {held or '?'} is gone) — taking it")
            LOCK.unlink(missing_ok=True)
    if fd is None:
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
