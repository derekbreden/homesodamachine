"""Whether a card still describes the tree.

A build writes the .step, the three elevations, and `enclosure-assembly.scorecard.json`. The
card carries every component's real boxes and fill, every port's coordinate and bore, every
run's corners, grades and detour, and the verdict on every gate. Reading it costs nothing.
This says whether what it carries is still true of the source on disk.

The build stamps the card under `source` with a fingerprint of every file that ran to produce
it. A reader re-fingerprints those same paths. Nothing here imports cadquery or touches
geometry.

    tools/cad-venv/bin/python .../fresh.py                  # the card beside the assembly
    tools/cad-venv/bin/python .../fresh.py <card.json>      # any card carrying a stamp
    tools/cad-venv/bin/python .../fresh.py selftest

The input set is read out of `sys.modules` at the end of the build: every module of this repo's
own source that ran. It reaches well outside this directory — `scorecard.py` imports `need.py`,
and the ports table reaches the cold core's own interface module and two fitting modules in
other part trees.

What a stamp does not cover: a change with no file behind it. A different cadquery, a different
OCC, an env var that gates a check (`HSM_SKIP_CLEARANCES`, `HSM_SKIP_VIEWS`). Those move the
numbers and leave every fingerprint intact, so a fresh verdict says the sources agree.

`moved()` splits what changed. `_lines.py` and `_routing.py` reach only the run rows — `bends`,
`routed`, `lines-clear`, `bend-radius`. Everything else, from a component's boxes to the
pack-closes clash list, is a function of the placed bodies. It is the same line
`enclosure_assembly._source_digest` draws for the scorecard cache, read here rather than
written: with only the routing files moved, the boxes and ports on the card still stand.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_here = Path(__file__).resolve()

# The repo root, by the marker that is always there. Paths in a stamp are stored relative to
# it, so a card reads the same in any clone and any worktree.
REPO = next(p for p in _here.parents if (p / ".git").exists())

# The two files whose only reach into the card is the runs. Matched by name; each edition
# carries its own copy of the tree.
RUN_SOURCES = frozenset({"_lines.py", "_routing.py"})

# The card key this module owns.
STAMP_KEY = "source"

# The interpreter's own trees. `tools/cad-venv` lives inside the repo, so cadquery, OCP and
# every other installed package carry repo-relative paths. A stamp covers the source written
# here; the library underneath it is the case `What a stamp does not cover` names above.
_INTERPRETER = tuple({Path(p).resolve() for p in (sys.prefix, sys.base_prefix)})


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return "sha256:" + h.hexdigest()[:16]


def _stat(path: Path) -> str:
    st = path.stat()
    return f"stat:{st.st_size}:{st.st_mtime_ns}"


def fingerprint(path: Path) -> str:
    """One input's identity.

    A `.py` is hashed: its mtime moves for reasons that are not edits — a checkout, a
    formatter, a touch — and the whole Python input set is well under a megabyte. A `.step`
    is stat'd: it runs to tens of megabytes, and its mtime moves when a build rewrites it.
    """
    return _stat(path) if path.suffix.lower() == ".step" else _sha(path)


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO))
    except ValueError:
        return str(path.resolve())


def _loaded() -> list[Path]:
    """Every module of this repo's own source that has been imported. Excludes the interpreter's
    trees, and excludes this one — the stamper runs after the verdict it stamps."""
    out = []
    for mod in list(sys.modules.values()):
        f = getattr(mod, "__file__", None)
        if not f or not f.endswith(".py"):
            continue
        p = Path(f).resolve()
        if p == _here or any(p.is_relative_to(root) for root in _INTERPRETER):
            continue
        try:
            p.relative_to(REPO)
        except ValueError:
            continue
        if p.is_file():
            out.append(p)
    return sorted(set(out))


def inputs(extra=()) -> dict:
    """`{repo-relative path: fingerprint}` for everything that produced the card — the imported
    Python, plus the non-module inputs the caller declares: the STEPs the pack imports, the
    editor's placement overrides."""
    seen = {}
    for p in list(_loaded()) + [Path(e) for e in extra]:
        p = Path(p).resolve()
        if p.is_file():
            seen[_rel(p)] = fingerprint(p)
    return dict(sorted(seen.items()))


def _commit() -> str | None:
    """HEAD when the build ran, for orientation. A stamp is keyed on file content, not on the
    commit."""
    try:
        out = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or None if out.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def stamp(extra=()) -> dict:
    """The block the build embeds under `source`. Called after the build, with `sys.modules`
    holding everything that ran."""
    return {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "commit": _commit(),
        "inputs": inputs(extra),
    }


def moved(card: dict) -> dict:
    """What has changed under a card since it was written.

    `runs` are the paths that reach only the run rows; `pack` is everything else, which reaches
    the whole card. `gone` is an input that no longer exists. A card with all three empty
    describes the sources on disk exactly.
    """
    src = card.get(STAMP_KEY) or {}
    rec = src.get("inputs") or {}
    runs, pack, gone = [], [], []
    for rel, was in rec.items():
        p = REPO / rel
        if not p.is_file():
            gone.append(rel)
        elif fingerprint(p) != was:
            (runs if Path(rel).name in RUN_SOURCES else pack).append(rel)
    return {"runs": sorted(runs), "pack": sorted(pack), "gone": sorted(gone)}


def is_fresh(card: dict) -> bool:
    """True when every recorded input is exactly as it was. An unstamped card carries no claim
    and is not fresh."""
    if not (card.get(STAMP_KEY) or {}).get("inputs"):
        return False
    m = moved(card)
    return not (m["runs"] or m["pack"] or m["gone"])


def verdict(card: dict) -> str:
    """The one-line answer, and what moved under it."""
    src = card.get(STAMP_KEY) or {}
    if not src.get("inputs"):
        return ("UNSTAMPED — this card carries no record of what built it. Build once to "
                "stamp it.")
    m = moved(card)
    when = src.get("generated", "?")
    head = (src.get("commit") or "")[:8]
    at = f"{when}" + (f" at {head}" if head else "")
    n = len(src["inputs"])

    if not (m["runs"] or m["pack"] or m["gone"]):
        return f"FRESH — {n} inputs unchanged since {at}. A build reproduces it."

    lines = []
    if m["pack"] or m["gone"]:
        lines.append("STALE — the whole card. The bodies moved under it:")
    else:
        lines.append("STALE IN THE RUNS ONLY — boxes, ports and the pack verdict still stand; "
                     "bends, routed, lines-clear and bend-radius do not:")
    for rel in m["pack"]:
        lines.append(f"    changed  {rel}")
    for rel in m["runs"]:
        lines.append(f"    changed  {rel}")
    for rel in m["gone"]:
        lines.append(f"    missing  {rel}")
    lines.append(f"  built {at}, {n} inputs")
    return "\n".join(lines)


def read(card_path) -> dict:
    return json.loads(Path(card_path).read_text())


DEFAULT_CARD = _here.parent / "enclosure-assembly.scorecard.json"


def _selftest() -> int:
    """Controls in both directions."""
    fails = []

    def ok(cond, what):
        print(f"  {'ok  ' if cond else 'FAIL'}  {what}")
        if not cond:
            fails.append(what)

    # Under the repo, so the paths in a stamp resolve the way a card's do.
    probe_dir = REPO / ".fresh-selftest"
    probe_dir.mkdir(exist_ok=True)
    try:
        f = probe_dir / "sample.py"
        f.write_text("x = 1\n")
        step = probe_dir / "sample.step"
        step.write_text("ISO-10303-21;\n")

        card = {STAMP_KEY: stamp([f, step])}
        ok(_rel(f) in card[STAMP_KEY]["inputs"], "a declared input is recorded")
        ok(is_fresh(card), "a card stamped from the tree reads fresh")

        f.write_text("x = 2\n")
        ok(not is_fresh(card), "a changed input reads stale")
        ok(_rel(f) in moved(card)["pack"], "the changed input is named")

        f.write_text("x = 1\n")
        ok(is_fresh(card), "restoring the content restores fresh — content, not mtime")

        os.utime(step, ns=(1, 1))
        ok(not is_fresh(card), "a STEP rewritten reads stale")
        ok(_rel(step) in moved(card)["pack"], "the STEP is named")

        # The split: a routing file alone leaves the pack's half of the card standing.
        lines = probe_dir / "_lines.py"
        lines.write_text("runs = 1\n")
        card2 = {STAMP_KEY: stamp([lines])}
        lines.write_text("runs = 2\n")
        m = moved(card2)
        ok(_rel(lines) in m["runs"], "_lines.py lands in runs")
        ok(not m["pack"], "_lines.py alone leaves pack clean")

        gone = probe_dir / "vanishes.py"
        gone.write_text("y = 1\n")
        card3 = {STAMP_KEY: stamp([gone])}
        gone.unlink()
        ok(_rel(gone) in moved(card3)["gone"], "a deleted input is reported missing")

        ok(not is_fresh({}), "an unstamped card is not fresh")
        ok("UNSTAMPED" in verdict({}), "an unstamped card says so")
        ok(_rel(_here) not in inputs(), "the stamper does not stamp itself")
        # tools/cad-venv is inside the repo: without this, cadquery and OCP stamp as source.
        ok(not [k for k in inputs()
                if any((REPO / k).is_relative_to(r) for r in _INTERPRETER)],
           "no interpreter tree in the input set")
    finally:
        for p in sorted(probe_dir.glob("*")):
            p.unlink()
        probe_dir.rmdir()

    print()
    if fails:
        print(f"{len(fails)} failed")
        return 1
    print("every control holds: a stamp names its inputs, a change is caught in the half of "
          "the card it can reach, and an unstamped card claims nothing")
    return 0


def main(argv) -> int:
    arg = argv[1] if len(argv) > 1 else None
    if arg == "selftest":
        return _selftest()
    path = Path(arg) if arg else DEFAULT_CARD
    if not path.is_file():
        print(f"fresh: no card at {path}", file=sys.stderr)
        return 2
    card = read(path)
    print(f"{_rel(path)}")
    print(verdict(card))
    return 0 if is_fresh(card) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
