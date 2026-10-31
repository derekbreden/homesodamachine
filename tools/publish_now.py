#!/usr/bin/env python3
"""publish_now.py — move the pointer file from this machine when this tree owes it.

    tools/cad-venv/bin/python tools/publish_now.py           publish if this tree owes it
    tools/cad-venv/bin/python tools/publish_now.py --check    say what it would do, touch nothing
    tools/cad-venv/bin/python tools/publish_now.py --selftest # exercise the owed decision

THIS IS THE VISUAL PATH AND PLAIN `pack.py --write` IS THE RECONCILER. This process grafts an
accepted piece payload into the enclosure and appliance payloads, then `pack.py --write
--publish-held` uploads the bytes already standing on this machine and moves each member's `made`
line. It never asks Bazel to stand the appliance or run its motion scorecard. Plain `pack.py
--write` cuts the producer rules whose members no line proves, and records what they were cut
from.

MOVING THE POINTER FILE DEPLOYS NOTHING. It is not among `render.yaml`'s buildFilter paths: the
running container adopts a pointer file that moved and pushes the changed members to open pages.
`tell_the_site()` below is what makes that immediate rather than a poll away.

OWED IS READ BEFORE ANYTHING IS PUBLISHED, AND IT IS TWO QUESTIONS OF THE MEMBERS. BYTES: a member
or scorecard on this disk whose sha256 is not its line, with digests reused while device, inode,
size, mtime and ctime are unchanged. INPUTS: a member whose `made` line the tree moves — one with
no line, one whose inputs the tree has moved off, and an unproven one the tree has come back to
(`tools/_artifact_inputs.py` reads those inputs' blob ids off the index). A tree that moved
neither starts no other process.

ONE AT A TIME, AND THE LAST REQUEST WINS. Several sessions commit at once and a publish takes
around a minute, so a second invocation while one is running does not queue behind it — it
marks the running one to look again when it finishes. Whatever is owed at that point is what
gets cut, which is the newest state rather than the one that asked.

IT REPORTS AND HOLDS NOTHING. The geometry's own commits are already on main by the time this
runs; the one commit this makes is the pointer file, and the site is told to look only once main holds
it. A publish that fails says so, and what it owed is still owed to the next one.
"""

from __future__ import annotations

import time

STARTED = time.monotonic()

import argparse  # noqa: E402
import hashlib  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import NamedTuple  # noqa: E402

import _single_flight  # noqa: E402
from _artifact_inputs import blob_id, staged  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PY = ROOT / "tools" / "cad-venv" / "bin" / "python"
LOCK = ROOT / ".cache" / "publish-now.lock"
AGAIN = ROOT / ".cache" / "publish-now.again"
POINTERS = "hardware/cad-artifacts.json"

#: The enclosure's piece payloads, by the prefix of their paths.
PIECE_PAYLOADS = "hardware/printed-parts/enclosure/enclosure/enclosure-"
#: What the graft writes the piece payloads into.
VIEWER_HOSTS = (
    "hardware/printed-parts/enclosure/enclosure/enclosure.step.mesh",
    "hardware/manifold-layout/enclosure-assembly.step.mesh",
)
#: The STEPs beside the viewer hosts, which take the stock colours again after a graft.
RECOLORED = (
    "hardware/printed-parts/enclosure/enclosure/enclosure.step",
    "hardware/manifold-layout/enclosure-assembly.step",
)


def run(args: list, quiet: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(ROOT), text=True,
                          capture_output=quiet)


def _pack():
    spec = importlib.util.spec_from_file_location("_publish_pack", ROOT / "tools/cad-artifacts/pack.py")
    pack = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pack)
    return pack


def bytes_drifted(pack=None, held: dict = None, graph=None) -> list:
    """The members and scorecards on this disk whose bytes are not the pointer file's lines,
    hashing only files whose stat changed. A member the pointer file names and this disk does
    not hold keeps its line."""
    pack = pack or _pack()
    if held is None:
        held = json.loads((ROOT / POINTERS).read_text())
    was, side_was = held.get("solids", {}), held.get("sidecars", {})
    moved = [rel for rel, digest in pack.hashes(ROOT, pack.solids(ROOT)).items()
             if was.get(rel) != digest]
    moved += [rel for rel, digest in pack.sidecar_lines(ROOT, held, graph).items()
              if side_was.get(rel) != digest]
    return sorted(moved)


class Owed(NamedTuple):
    """Why this tree owes a publish, and what moved."""

    reason: str
    #: Members and scorecards whose bytes are not their lines.
    moved: list
    #: Members whose `made` line moves though no bytes do.
    inputs: list
    #: The pointer file and scorecards whose bytes on disk the index does not hold.
    heal: list


def owed() -> Owed:
    """What this tree owes the pointer file.

    TWO QUESTIONS, AND NEITHER ANSWERS THE OTHER. The inputs question is the only one that sees
    a source change whose member has not been cut yet. The bytes question is the only one that
    sees a solid whose bytes moved with no commit behind them — a rebuild, a carry, or a payload
    recut. Asking only about sources is how a tree that had lost the enclosure's flutes read as
    owing nothing while the site drew a smooth box."""
    try:
        text = (ROOT / POINTERS).read_text()
    except OSError:
        return Owed("there is no pointer file yet", [], [], [])
    held = json.loads(text)
    pack = _pack()
    graph = pack.Graph.load(ROOT)
    moved = bytes_drifted(pack, held, graph)
    index = staged(ROOT)
    lines = {**held.get("solids", {}), **held.get("sidecars", {})}
    inputs = pack.made_moves(held.get("made") or {},
                             pack.tree_digests(ROOT, graph, lines, index))
    heal = [rel for rel in (POINTERS, *sidecar_paths(held))
            if blob_id(ROOT / rel) != index.get(rel)]
    reason = "; ".join(part for part in (
        f"{len(moved)} member(s) on this disk are not the bytes the pointer file names"
        if moved else "",
        f"the tree moves the `made` line of {len(inputs)} member(s)" if inputs else "",
    ) if part)
    return Owed(reason, moved, inputs, heal)


def sidecar_paths(held: dict) -> list:
    """The scorecards the pointer file names, as paths this tree holds.

    A path it names that is not a file here is one this commit has nothing to say about — the
    pack is what settles which scorecards exist."""
    return [rel for rel in sorted(held.get("sidecars", {})) if (ROOT / rel).is_file()]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def piece_payloads(moved: list) -> list:
    """The enclosure piece payloads among `moved`, which are what the graft carries.

    SOURCE IS NOT A CUT. A source-only checkpoint leaves mutually stamped old STEP/STL/payload
    bytes on disk, and `surfaces()` correctly says those old siblings agree with each other. The
    visual path needs a stronger entrance: at least one piece payload must differ from the pointer file
    before that surface can stand in for the source change. The viewer hosts are outputs of the
    graft and are not piece payloads: counting one would make a completed graft ask for itself
    again."""
    return [rel for rel in moved if rel.startswith(PIECE_PAYLOADS) and rel.endswith(".step.mesh")]


def refresh_enclosure_viewer() -> None:
    """Graft current enclosure piece payloads into both viewer hosts, without building.

    `surfaces` admits a piece only when its payload names the exact STEP beside it.
    The rigid pieces share the host frame; the pump retainer keeps its native seated pose.
    The operation reads no CAD source and acquires no Bazel lock.
    """
    scripts = ROOT / "hardware" / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    import flute_payload

    pieces = [(step, stl) for step, stl in flute_payload.pieces(flute_payload.ENCLOSURE_DIRS)
              if step.stem != "enclosure-pump-retainer"]
    fluted = flute_payload.surfaces(flute_payload.ENCLOSURE_DIRS)
    if len(fluted) != len(pieces):
        print(f"  {len(fluted)} of {len(pieces)} enclosure piece payload(s) are source-current; "
              f"the hosts take those")
    if not fluted:
        return

    for host in (ROOT / rel for rel in VIEWER_HOSTS):
        if not host.is_file():
            print(f"  the viewer host is absent: {host.relative_to(ROOT)}")
            continue
        # Each host receives the piece surfaces it holds, in the frame it holds them in.
        expected = {flute_payload.fluted_key(name, fluted)
                    for name in flute_payload.payload_names(host)} - {None}
        landed = flute_payload.graft(host, {name: fluted[name] for name in expected},
                                     same_frame=True) if expected else 0
        print(f"  {host.relative_to(ROOT)}: {landed} of {len(expected)} piece surface(s) landed")


def tell_the_site() -> None:
    """Ask the running site to look at the pointer file now, rather than at its next poll.

    THE POINTER FILE IS NOT IN `render.yaml`'s buildFilter, so pointing at it deploys nothing — the container
    adopts it in place and pushes the changed members to open pages. It finds out on a two-minute
    poll on its own; this is what makes the usual case seconds instead.

    IT CARRIES NOTHING AND IS TRUSTED WITH NOTHING. The site reads the pointer file from GitHub either
    way, so this says only "look now" — and it is why the pointer file is on main before this is called,
    since a container sent to look at a commit that is not there reads the previous cut and then
    waits out a poll. A post that does not arrive costs a poll, which is why nothing here is
    retried and nothing here fails a publish.
    """
    import urllib.request

    try:
        urllib.request.urlopen(
            urllib.request.Request("https://homesodamachine.com/api/artifacts/refresh",
                                   data=b"", method="POST"),
            timeout=10).read()
        print("  the site is looking")
    except Exception as e:  # noqa: BLE001 — a site that did not answer still polls
        print(f"  could not reach the site ({e}); it polls every 2 min")


#: The keys of the pointer file a reader fetches by; a commit that moves none of them moves records.
SERVED = ("release", "bundle", "solids", "sidecars")


def publish(started: float) -> int:
    debt = owed()
    if not debt.reason and not debt.heal:
        print(f"  {time.strftime('%H:%M:%S')} nothing owed: no member's bytes or inputs moved "
              f"({time.monotonic() - started:.2f}s)")
        return 0
    if debt.reason:
        grafted = []
        if piece_payloads(debt.moved):
            # WHAT IS HELD IS PUBLISHED, refreshed as far as the refresh got. A host the refresh
            # could not touch goes up as it stands and says so; the next cut replaces it.
            try:
                if sys.flags.no_site:
                    import site
                    site.main()
                refresh_enclosure_viewer()
            except Exception as exc:  # noqa: BLE001 — printed, and the publish goes on
                print(f"  the viewer refresh stopped short: {exc}", file=sys.stderr)
                print("  publishing the bytes held here anyway", file=sys.stderr)
            # The graft writes the two viewer hosts, so those two take the stock colours again.
            if run([str(PY), "hardware/scripts/materialize_material_colors.py", "--write",
                    *RECOLORED]).returncode != 0:
                return 1
            grafted = [*VIEWER_HOSTS, *RECOLORED]
        print(f"  {debt.reason}; publishing the bytes held here")
        if run([str(PY), "tools/cad-artifacts/pack.py", "--write", "--publish-held",
                *(arg for rel in grafted for arg in ("--grafted", rel))]).returncode != 0:
            print("  held publication did not finish; the next publish still owes it",
                  file=sys.stderr)
            return 1
    # THE SCORECARDS COMMIT WITH THE POINTER FILE, BECAUSE THE POINTER FILE IS NOT WHERE THEIR BYTES LIVE.
    # `pack.py` keeps them outside the geometry tar and off the release: the pointer file names each
    # one's sha256 and the committed tree is what anyone reads them from. Pointing at a hash whose
    # bytes never landed leaves the pointer file naming a file main does not hold, and the site — which
    # carries them from main in `web/lib/artifacts-live.js` — draws the older verdict against
    # the newer geometry. They are one cut, so they are one commit.
    held = json.loads((ROOT / POINTERS).read_text())
    index = staged(ROOT)
    paths = [rel for rel in (POINTERS, *sidecar_paths(held))
             if blob_id(ROOT / rel) != index.get(rel)]
    if not paths:
        print(f"  the cut is the one already published ({time.monotonic() - started:.0f}s)")
        return 0
    fresh = [rel for rel in paths if rel not in index]
    if fresh:
        run(["git", "add", "--", *fresh], quiet=True)
    shown = run(["git", "show", f"HEAD:{POINTERS}"], quiet=True)
    try:
        before = json.loads(shown.stdout) if shown.returncode == 0 else {}
    except ValueError:
        before = {}
    served = any(before.get(key) != held.get(key) for key in SERVED)
    msg = ("cad-artifacts: cut here, and the pointer file moved" if served
           else "cad-artifacts: record which members' inputs moved")
    # `--no-verify`: the pre-commit hook re-derives and stages, and this commit is these files by
    # name. `--only` keeps it that way whatever else the tree is holding.
    made = run(["git", "commit", "--no-verify", "--only", "-m", msg, "--", *paths], quiet=True)
    if made.returncode != 0:
        print(f"  the pointer file did not commit: {(made.stderr or made.stdout).strip()}",
              file=sys.stderr)
        return 1
    # THE SITE READS THE POINTER FILE FROM MAIN, so a cut that did not land there is one nobody can see
    # and a `tell_the_site()` that sends the container to fetch the bytes it already has. The
    # `.githooks/post-commit` hook runs `push.py` inside the commit above and, by its own
    # contract, reports a push that did not land and leaves the work committed — so the commit
    # returning says the commit was made and not that main has it. This reads the tracking ref
    # `push.py` moves, which costs no network and no second reconcile: the post goes out on the
    # strength of the pointer file being on main.
    if run(["git", "merge-base", "--is-ancestor", "HEAD", "origin/main"],
           quiet=True).returncode != 0:
        print(f"  the pointer file is committed and not on main; the next push carries it "
              f"({time.monotonic() - started:.0f}s)", file=sys.stderr)
        return 1
    print(f"  pointer file moved and pushed ({time.monotonic() - started:.0f}s)")
    if served:
        tell_the_site()
    return 0


def selftest() -> int:
    import shutil
    import tempfile

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
        rels = {name: path.relative_to(root).as_posix() for name, path in paths.items()}
        hold("only a piece payload asks for the graft: not its STEP, its STL or a host",
             piece_payloads([rels["step"], rels["stl"], rels["host"], VIEWER_HOSTS[1],
                             rels["payload"]]), [rels["payload"]])

        # Mock only the payload API: exercise the real refresh dispatch and
        # both hosts without importing CAD or publishing any files.
        from contextlib import redirect_stdout
        from io import StringIO
        from types import SimpleNamespace
        from unittest.mock import patch

        fixed = {f"enclosure-{name}" for name in (
            "front-top", "front-bottom", "back-top", "back-bottom")}
        appliance = root / "hardware/manifold-layout/enclosure-assembly.step.mesh"
        appliance.parent.mkdir(parents=True)
        appliance.write_bytes(b"appliance host")
        calls = []

        def graft(host, surfaces, *, same_frame):
            calls.append((host.relative_to(root).as_posix(), set(surfaces), same_frame))
            return len(surfaces)

        fake = SimpleNamespace(
            ENCLOSURE_DIRS=(), pieces=lambda _: [
                (Path(name+".step"), Path(name+".stl"))
                for name in sorted(fixed | {"enclosure-pump-retainer"})],
            surfaces=lambda _: {name: object() for name in fixed},
            payload_names=lambda host: sorted(fixed) + ["unrelated-component"],
            fluted_key=lambda name, surfaces: name if name in surfaces else None,
            graft=graft,
        )
        with patch.dict(sys.modules, {"flute_payload": fake}), \
                patch.object(sys.modules[__name__], "ROOT", root), \
                redirect_stdout(StringIO()):
            refresh_enclosure_viewer()
        hold("both hosts graft surfaces in their exact assembly frame",
             [(host, names) for host, names, same in calls if same],
             [(paths["host"].relative_to(root).as_posix(), fixed),
              (appliance.relative_to(root).as_posix(), fixed)])
        hold("refresh never passes an unrelated host entry to the graft",
             set().union(*(names for _host, names, _same in calls)), fixed)

    # WHAT IS OWED, read off a tree whose one rule writes the piece, its payload and the host.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "tools/cad-artifacts").mkdir(parents=True)
        (root / "tools/docgen").mkdir()
        (root / "tools/bazel").mkdir()
        shutil.copyfile(ROOT / "tools/cad-artifacts/pack.py", root / "tools/cad-artifacts/pack.py")
        source = "hardware/printed-parts/enclosure/enclosure.py"
        (root / source).parent.mkdir(parents=True)
        (root / source).write_text("pieces")
        written = {rel: root / rel for rel in (PIECE_PAYLOADS + "front-top.step",
                                               PIECE_PAYLOADS + "front-top.step.mesh",
                                               VIEWER_HOSTS[0])}
        for rel, path in written.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(rel)
        payload = PIECE_PAYLOADS + "front-top.step.mesh"
        (root / "tools/bazel/graph.json").write_text(json.dumps(
            {source: {"reads": [source], "writes": sorted(written)}}))

        def git(*args):
            subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=True)

        git("init", "-q")
        git("add", "--", source)
        with patch.object(sys.modules[__name__], "ROOT", root):
            pack = _pack()
            lines = {rel: _sha256(path) for rel, path in written.items()}
            tree = pack.tree_digests(root, pack.Graph.load(root), lines)
            pointer = json.dumps({"solids": lines, "made": {
                rel: {"inputs": digest, "commit": "c"} for rel, digest in tree.items()}})
            (root / POINTERS).write_text(pointer)
            git("add", "--", POINTERS)

            hold("a tree that moved neither bytes nor inputs owes nothing",
                 owed(), Owed("", [], [], []))
            calls = []
            with patch.object(sys.modules[__name__], "run",
                              lambda args, quiet=False: calls.append(args)), \
                    redirect_stdout(StringIO()):
                publish(time.monotonic())
            hold("…and publishing it starts no process", calls, [])

            written[payload].write_text("recut")
            hold("a payload recut with no commit behind it is owed, and asks for the graft",
                 piece_payloads(owed().moved), [payload])
            written[payload].write_text(payload)

            (root / source).write_text("pieces, moved")
            git("add", "--", source)
            hold("an input the tree moved owes the lines of the members its rule writes",
                 owed().inputs, sorted(written))
            (root / source).write_text("pieces")
            git("add", "--", source)

            (root / POINTERS).write_text(pointer + "\n")
            hold("a pointer file the index does not hold is owed as it stands",
                 owed().heal, [POINTERS])

    print(f"publish-now selftest {holds}/8")
    return 0 if holds == 8 else 1


def main(argv) -> int:
    sys.stdout.reconfigure(line_buffering=True)
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    if args.check:
        debt = owed()
        print(f"  --check: {debt.reason}" if debt.reason else "  --check: nothing owed")
        if debt.heal:
            print(f"  --check: the index does not hold {', '.join(debt.heal)} as it is on disk")
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
        code = publish(STARTED)
        while AGAIN.exists():
            AGAIN.unlink(missing_ok=True)
            print("  a commit landed while that ran — reading the tree again")
            code = publish(time.monotonic())
        return code
    finally:
        LOCK.unlink(missing_ok=True)
        AGAIN.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
