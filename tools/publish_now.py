#!/usr/bin/env python3
"""publish_now.py — cut and pin from this machine, so the site does not wait on a runner.

    tools/cad-venv/bin/python tools/publish_now.py           publish if this tree owes a cut
    tools/cad-venv/bin/python tools/publish_now.py --check    say what it would do, touch nothing
    tools/cad-venv/bin/python tools/publish_now.py --selftest # exercise the held-cut decision

THE LAPTOP IS THE VISUAL PATH AND THE RUNNER IS THE RECONCILER. This process grafts an accepted
piece payload into the enclosure and appliance payloads, then `pack.py --write --publish-held`
uploads the bytes already standing on this machine. It never asks Bazel to stand the appliance
or run its motion scorecard. Plain `pack.py --write` remains the reconciler: it cuts the deferred
producer rules, carries their evidence through the normal derive, and advances the source pin.

PINNING THE LOCK DEPLOYS NOTHING. It is not among `render.yaml`'s buildFilter paths: the
running container adopts a lock that moved and pushes the changed members to open pages.
`tell_the_site()` below is what makes that immediate rather than a poll away.

OWED IS READ BEFORE ANYTHING IS PUBLISHED, AND IT IS TWO QUESTIONS. `affected.py --artifacts` from
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
import hashlib
import json
import os
import subprocess
import sys
import tempfile
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


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def enclosure_drift(root: Path = None) -> tuple:
    """`(changed enclosure members, changed piece payloads)` against the current lock.

    SOURCE IS NOT A CUT. A source-only checkpoint leaves mutually stamped old STEP/STL/payload
    bytes on disk, and `surfaces()` correctly says those old siblings agree with each other. The
    visual path needs a stronger entrance: at least one piece payload must differ from the lock
    before that surface can stand in for the source change.
    """
    root = root or ROOT
    try:
        held = json.loads((root / "hardware/cad-artifacts.lock.json").read_text()).get(
            "solids", {})
    except (OSError, ValueError):
        held = {}
    directory = root / "hardware/printed-parts/enclosure/enclosure"
    current = {
        path.relative_to(root).as_posix(): path
        for path in directory.iterdir()
        if path.is_file() and path.name.endswith((".step", ".stl", ".step.mesh"))
    } if directory.is_dir() else {}
    locked = {
        rel for rel in held
        if rel.startswith("hardware/printed-parts/enclosure/enclosure/")
        and rel.endswith((".step", ".stl", ".step.mesh"))
    }
    changed = sorted(
        rel for rel in set(current) | locked
        if rel not in current or held.get(rel) != _sha256(current[rel])
    )
    payloads = [
        rel for rel in changed
        if Path(rel).name.startswith("enclosure-") and rel.endswith(".step.mesh")
    ]
    return changed, payloads


def enclosure_source_owed(targets: list) -> bool:
    """Whether the source range reaches a producer of enclosure piece bytes."""
    return bool({"//:everything", "//:enclosure", "//:flute-payload-enclosure"} & set(targets))


def enclosure_release_plan(targets: list, root: Path = None) -> tuple:
    """`(action, changed piece payloads)`, where action is unrelated, defer, or graft."""
    moved, payloads = enclosure_drift(root)
    if not enclosure_source_owed(targets) and not moved:
        return "unrelated", []
    return ("graft", payloads) if payloads else ("defer", [])


def refresh_enclosure_viewer() -> None:
    """Graft current enclosure piece payloads into both viewer hosts, without building.

    `surfaces` admits a piece only when its payload names the exact STEP beside it. `graft`
    carries that surface onto the body the host names and refuses one it cannot place. Those are
    properties of constructing the payload, not a second geometry scorecard; the operation reads
    no CAD source and acquires no Bazel lock.
    """
    scripts = ROOT / "hardware" / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    import flute_payload

    pieces = flute_payload.pieces(flute_payload.ENCLOSURE_DIRS)
    fluted = flute_payload.surfaces(flute_payload.ENCLOSURE_DIRS)
    if not pieces or len(fluted) != len(pieces):
        raise RuntimeError(
            f"only {len(fluted)} of {len(pieces)} enclosure piece payload(s) are source-current")

    hosts = (
        ROOT / "hardware/printed-parts/enclosure/enclosure/enclosure.step.mesh",
        ROOT / "hardware/manifold-layout/enclosure-assembly.step.mesh",
    )
    for host in hosts:
        if not host.is_file():
            raise RuntimeError(f"the viewer host is absent: {host.relative_to(ROOT)}")
        landed = flute_payload.graft(host, fluted)
        if landed != len(fluted):
            raise RuntimeError(
                f"{host.relative_to(ROOT)} accepted {landed} of {len(fluted)} piece surface(s)")
    print(f"  {len(fluted)} current enclosure surface(s) grafted into both viewer payloads")


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
    reason, targets = owed()
    if reason:
        enclosure_action, _piece_payloads = enclosure_release_plan(targets)
        if enclosure_action == "defer":
            try:
                base = json.loads(
                    (ROOT / "hardware/cad-artifacts.lock.json").read_text()
                ).get("source", {}).get("commit", "")
            except (OSError, ValueError):
                base = ""
            print("  enclosure source is owed, but no changed piece payload is held; "
                  "publishing nothing")
            print(f"  source debt remains against {base[:12] or 'the existing lock'}")
            return 0
        if enclosure_action == "graft":
            try:
                refresh_enclosure_viewer()
            except Exception as exc:  # noqa: BLE001 — the runner remains the fallback
                print(f"  the held viewer payload could not be refreshed: {exc}", file=sys.stderr)
                print("  the runner still reconciles this", file=sys.stderr)
                return 1
        print(f"  {reason}; publishing the bytes held here")
        if run([str(PY), "tools/cad-artifacts/pack.py", "--write",
                "--publish-held"]).returncode != 0:
            print("  held publication did not finish; the runner still reconciles this",
                  file=sys.stderr)
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


def selftest() -> int:
    holds = 0

    def hold(name, got, want):
        nonlocal holds
        if got != want:
            raise AssertionError(f"{name}:\n  got  {got!r}\n  want {want!r}")
        holds += 1
        print(f"  \N{CHECK MARK} {name}")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        directory = root / "hardware/printed-parts/enclosure/enclosure"
        directory.mkdir(parents=True)
        piece = directory / "enclosure-front-top"
        paths = {
            "step": piece.with_suffix(".step"),
            "stl": piece.with_suffix(".stl"),
            "payload": Path(f"{piece}.step.mesh"),
            "host": directory / "enclosure.step.mesh",
        }
        for name, path in paths.items():
            path.write_bytes(name.encode())
        solids = {
            path.relative_to(root).as_posix(): _sha256(path)
            for path in paths.values()
        }
        lock = root / "hardware/cad-artifacts.lock.json"
        lock.write_text(json.dumps({"solids": solids}))

        hold("a source-only enclosure checkpoint waits for fresh piece bytes",
             enclosure_release_plan(["//:enclosure"], root), ("defer", []))
        hold("the nonexistent broad flute label grants no held publication",
             enclosure_release_plan(["//:flute-payload"], root), ("unrelated", []))

        paths["step"].write_bytes(b"new step")
        hold("changed STEP without a changed piece payload still waits",
             enclosure_release_plan([], root), ("defer", []))
        paths["step"].write_bytes(b"step")

        paths["host"].write_bytes(b"new grafted host")
        hold("a grafted host alone cannot vouch for current piece geometry",
             enclosure_release_plan([], root), ("defer", []))
        paths["host"].write_bytes(b"host")

        paths["payload"].write_bytes(b"new payload")
        payload_rel = paths["payload"].relative_to(root).as_posix()
        hold("a changed carried piece payload admits the graft-only refresh",
             enclosure_release_plan([], root), ("graft", [payload_rel]))

    print(f"publish-now selftest {holds}/5")
    return 0 if holds == 5 else 1


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
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
