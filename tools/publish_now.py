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
runs; the one commit this makes is the lock, and the site is told to look only once main holds
it. A publish that fails leaves the runner to do what it was always going to do.
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

import _single_flight

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


def sidecar_paths() -> list:
    """The scorecards the lock names, as paths this tree holds.

    A lock predating the map names none, and a path it names that is not a file here is one
    this commit has nothing to say about — the pack is what settles which scorecards exist."""
    lock = ROOT / "hardware" / "cad-artifacts.lock.json"
    try:
        named = json.loads(lock.read_text()).get("sidecars", {})
    except (OSError, ValueError):
        return []
    return [rel for rel in sorted(named) if (ROOT / rel).is_file()]


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
    if reason:
        print(f"  {reason}; cutting here")
        if run([str(PY), "tools/cad-artifacts/pack.py", "--write"]).returncode != 0:
            print("  --write did not finish; the runner still reconciles this", file=sys.stderr)
            return 1
    else:
        # A CUT IS NOT THE ONLY THING A TREE CAN OWE. `--write` pins the scorecards off the
        # working tree, so a verdict recomputed after the last publish leaves the lock naming
        # bytes no commit carries — solids that match the lock exactly, and a scorecard the site
        # cannot read. Nothing is cut for that, and the commit below still is.
        print("  nothing owed — this tree's solids are the ones the lock names")
    # THE SCORECARDS COMMIT WITH THE LOCK, BECAUSE THE LOCK IS NOT WHERE THEIR BYTES LIVE.
    # `pack.py` keeps them outside the geometry tar and off the release: the lock names each
    # one's sha256 and the committed tree is what anyone reads them from. Pinning a hash whose
    # bytes never landed leaves the lock naming a file main does not hold, and the site — which
    # carries them from main in `web/lib/artifacts-live.js` — draws the older verdict against
    # the newer geometry. They are one cut, so they are one commit.
    paths = ["hardware/cad-artifacts.lock.json", *sidecar_paths()]
    if run(["git", "diff", "--quiet", "--", *paths], quiet=True).returncode == 0:
        if reason:
            print(f"  the cut is the one already published ({time.time() - started:.0f}s)")
        return 0
    run(["git", "add", "--", *paths], quiet=True)
    # `--no-verify`: the pre-commit hook re-derives and stages, and this commit is these files by
    # name. `--only` keeps it that way whatever else the tree is holding.
    msg = "cad-artifacts: cut and pinned from the machine that changed it"
    if run(["git", "commit", "--no-verify", "--only", *paths, "-m", msg],
           quiet=True).returncode != 0:
        print("  the lock did not commit", file=sys.stderr)
        return 1
    # THE SITE READS THE LOCK FROM MAIN, so a cut that did not land there is one nobody can see
    # and a `tell_the_site()` that sends the container to fetch the bytes it already has. The
    # `.githooks/post-commit` hook runs `push.py` inside the commit above and, by its own
    # contract, reports a push that did not land and leaves the work committed — so the commit
    # returning says the commit was made and not that main has it. This reads the tracking ref
    # `push.py` moves, which costs no network and no second reconcile: the post goes out on the
    # strength of the lock being on main.
    if run(["git", "merge-base", "--is-ancestor", "HEAD", "origin/main"],
           quiet=True).returncode != 0:
        print(f"  the lock is committed and not on main; the runner reconciles this "
              f"({time.time() - started:.0f}s)", file=sys.stderr)
        return 1
    print(f"  lock pinned and pushed ({time.time() - started:.0f}s)")
    tell_the_site()
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

    fd, cleared = _single_flight.take(LOCK)
    if cleared:
        print(f"  a publish left its marker behind (pid {cleared} is gone) — taking it")
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
