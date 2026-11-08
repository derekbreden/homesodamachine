#!/usr/bin/env python3
"""Publish completed geometry and shared scene references from this checkout.

Changed mesh objects and manufacturing files are uploaded before the committed pointer advances.
Each completed producer can advance its own references while other producers continue.
Concurrent requests coalesce onto the latest held output.
"""

from __future__ import annotations

import time

STARTED = time.monotonic()

import argparse  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import NamedTuple  # noqa: E402

import _single_flight  # noqa: E402
from _artifact_inputs import staged  # noqa: E402

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


def run(args: list, quiet: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(ROOT), text=True,
                          capture_output=quiet)


def timing(phase, started, **fields):
    """Requested publication measurements record elapsed phases outside the normal path."""
    name = os.environ.get("HSM_PUBLISH_TIMING")
    if name:
        row = {"phase": phase, "pid": os.getpid(), "wall_time_ns": time.time_ns(),
               "seconds": time.monotonic() - started, **fields}
        with open(name, "a") as log:
            log.write(json.dumps(row) + "\n")


def _pack():
    spec = importlib.util.spec_from_file_location("_publish_pack", ROOT / "tools/cad-artifacts/pack.py")
    pack = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pack)
    return pack


def _native(op, **fields):
    sys.path.insert(0, str(ROOT / "hardware/scripts"))
    from _build_data import request
    return request("publication-" + op, **{key: str(value.absolute()) if isinstance(value, Path) else value
                                           for key, value in fields.items()})


def bytes_drifted(pack=None, held: dict = None, graph=None) -> list:
    """The members and scorecards on this disk whose bytes are not the pointer file's lines,
    hashing only files whose stat changed. A member the pointer file names and this disk does
    not hold keeps its line."""
    pack = pack or _pack()
    if held is None:
        held = json.loads((ROOT / POINTERS).read_text())
    return _native("bytes-drifted", held=held, hashes=pack.hashes(ROOT, pack.solids(ROOT)),
                   sidecar_hashes=pack.sidecar_lines(ROOT, held, graph))


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

    The inputs question is the only one that sees
    a source change whose member has not been cut yet. The bytes question is the only one that
    sees a solid whose bytes moved with no commit behind them — a rebuild, a carry, or a payload
    recut. Asking only about sources is how a tree that had lost the enclosure's flutes read as
    owing nothing while the site drew a smooth box. Catalog membership also moves the website
    projection when all the stored member bytes and producer inputs remain unchanged."""
    state = _native("pointer-state-ordered", root=ROOT, pointers=POINTERS)
    if state["missing"]:
        return Owed("there is no pointer file yet", [], [], [])
    pack = _pack()
    held = pack._unorder(state["ordered"])
    graph = pack.Graph.load(ROOT)
    moved = bytes_drifted(pack, held, graph)
    index = staged(ROOT)
    lines = _native("merge-lines", maps=[held.get("solids", {}), held.get("sidecars", {})])
    inputs = pack.made_moves(held.get("made") or {}, pack.tree_digests(ROOT, graph, lines, index))
    catalog_moved = pack._native("catalog-moved", root=ROOT, held=held)
    return Owed(*_native("owed", root=ROOT, held=held, index=index, pointers=POINTERS,
                         moved=moved, inputs=inputs, catalog_moved=catalog_moved))


def sidecar_paths(held: dict) -> list:
    """The scorecards the pointer file names, as paths this tree holds.

    A path it names that is not a file here is one this commit has nothing to say about — the
    pack is what settles which scorecards exist."""
    return _native("sidecar-paths", root=ROOT, held=held)


def _sha256(path: Path) -> str:
    return _native("sha256", path=path)


def piece_payloads(moved: list) -> list:
    """Changed mesh outputs can advance existing scene references without a whole-machine build."""
    return [rel for rel in moved if rel.endswith(".step.mesh") and rel not in VIEWER_HOSTS]


def refresh_enclosure_viewer(changed=None) -> None:
    """Completed source payloads replace their references in the existing published scenes."""
    from _build_data import request
    pack = _pack()
    candidates = pack.solids(ROOT)
    hosts = [ROOT / rel for rel in candidates if rel.endswith((".step.mesh", ".glb.mesh"))]
    sources = changed or []
    for relative in sources:
        source = ROOT / relative
        selected = [str(path) for path in hosts if path != source and
                    path.is_file() and (str(path.relative_to(ROOT)) in VIEWER_HOSTS or
                     (request("header", path=str(path)).get("v") == 4))]
        rows = request("scene-replace", source=str(source), relative=relative, hosts=selected)
        for row in rows:
            if row["replaced"]:
                print(f"  {Path(row['path']).relative_to(ROOT)}: {row['replaced']} part reference(s) updated")


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
SERVED = ("release", "bundle", "solids", "sidecars", "website", "mesh_assets")


def publish(started: float) -> int:
    phase_started = time.monotonic()
    debt = owed()
    timing("identify", phase_started, moved=debt.moved)
    if not debt.reason and not debt.heal:
        print(f"  {time.strftime('%H:%M:%S')} nothing owed: member bytes, inputs and website selection agree "
              f"({time.monotonic() - started:.2f}s)")
        return 0
    if debt.reason:
        phase_started = time.monotonic()
        grafted = []
        if piece_payloads(debt.moved):
            # WHAT IS HELD IS PUBLISHED, refreshed as far as the refresh got. A host the refresh
            # could not touch goes up as it stands and says so; the next cut replaces it.
            try:
                if sys.flags.no_site:
                    import site
                    site.main()
                refresh_enclosure_viewer(piece_payloads(debt.moved))
            except Exception as exc:  # noqa: BLE001 — printed, and the publish goes on
                print(f"  the viewer refresh stopped short: {exc}", file=sys.stderr)
                print("  publishing the bytes held here anyway", file=sys.stderr)
            grafted = [*VIEWER_HOSTS, *[str(p.relative_to(ROOT)) for p in (ROOT / "hardware/assembly/scenes/glb").glob("*.glb.mesh")]]
        timing("references", phase_started)
        phase_started = time.monotonic()
        print(f"  {debt.reason}; publishing the bytes held here")
        if run([str(PY), "tools/cad-artifacts/pack.py", "--write", "--publish-held",
                *(arg for rel in grafted for arg in ("--grafted", rel))]).returncode != 0:
            print("  held publication did not finish; the next publish still owes it",
                  file=sys.stderr)
            return 1
    timing("objects", phase_started)
    phase_started = time.monotonic()
    # THE SCORECARDS COMMIT WITH THE POINTER FILE, BECAUSE THE POINTER FILE IS NOT WHERE THEIR BYTES LIVE.
    # `pack.py` keeps them outside the geometry tar and off the release: the pointer file names each
    # one's sha256 and the committed tree is what anyone reads them from. Pointing at a hash whose
    # bytes never landed leaves the pointer file naming a file main does not hold, and the site — which
    # carries them from main in `web/lib/artifacts-live.js` — draws the older verdict against
    # the newer geometry. They are one cut, so they are one commit.
    held = json.loads((ROOT / POINTERS).read_text())
    index = staged(ROOT)
    paths = _native("heal", root=ROOT, pointers=POINTERS, held=held, index=index)
    if not paths:
        print(f"  the cut is the one already published ({time.monotonic() - started:.0f}s)")
        return 0
    fresh = _native("untracked-paths", paths=paths, index=index)
    if fresh:
        run(["git", "add", "--", *fresh], quiet=True)
    shown = run(["git", "show", f"HEAD:{POINTERS}"], quiet=True)
    try:
        before = json.loads(shown.stdout) if shown.returncode == 0 else {}
    except ValueError:
        before = {}
    plan = _native("commit-plan", root=ROOT, pointers=POINTERS, held=held, index=index,
                   before=before, served=SERVED)
    served, msg = plan["served"], plan["message"]
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
    timing("commit-and-push", phase_started)
    phase_started = time.monotonic()
    print(f"  pointer file moved and pushed ({time.monotonic() - started:.0f}s)")
    if served:
        tell_the_site()
    timing("notify", phase_started)
    timing("publication", started)
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

        # Exercise reference dispatch without publishing or importing a CAD builder.
        from contextlib import redirect_stdout
        from io import StringIO
        from types import SimpleNamespace
        from unittest.mock import patch

        appliance = root / "hardware/manifold-layout/enclosure-assembly.step.mesh"
        appliance.parent.mkdir(parents=True)
        appliance.write_bytes(b"appliance host")
        candidates = [rels["payload"], rels["host"], VIEWER_HOSTS[1]]
        calls = []

        def request(operation, **fields):
            if operation == "scene-replace":
                calls.append(fields)
                return [{"path": host, "replaced": 1} for host in fields["hosts"]]
            raise AssertionError(operation)

        with patch.dict(sys.modules, {"_build_data": SimpleNamespace(request=request)}), \
                patch.object(sys.modules[__name__], "ROOT", root), \
                patch.object(sys.modules[__name__], "_pack", lambda: SimpleNamespace(solids=lambda _: candidates)), \
                redirect_stdout(StringIO()):
            refresh_enclosure_viewer([rels["payload"]])
        hold("both hosts receive the completed source reference",
             calls[0]["hosts"], [str(paths["host"]), str(appliance)])
        hold("refresh identifies the authoritative producer payload",
             (calls[0]["source"], calls[0]["relative"]), (str(paths["payload"]), rels["payload"]))

    # WHAT IS OWED, read off a tree whose one rule writes the piece, its payload and the host.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "tools/cad-artifacts").mkdir(parents=True)
        (root / "tools/docgen").mkdir()
        (root / "tools/bazel").mkdir()
        shutil.copyfile(ROOT / "tools/cad-artifacts/pack.py", root / "tools/cad-artifacts/pack.py")
        shutil.copyfile(ROOT / "tools/bazel/inventory.py", root / "tools/bazel/inventory.py")
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
