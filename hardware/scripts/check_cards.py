#!/usr/bin/env python3
"""check_cards.py — whether a committed scorecard still describes the tree.

A card is what the machine measured, and it is written by a build. Between two builds an agent
edits a source and the card on disk goes on reading whatever the last build found — the numbers
look like measurements and are a memory of one. That is the state this answers.

The card is what the build measured. Under `.cache/stamps/cards/`, the same run leaves the
digest of the whole text of every file of this repo it could reach, walked off the import
statements by `_realized.source_files`. This walks the same builder — each in a process of its
own, so no builder's `sys.path` reaches another's graph — and compares two hex strings. What
it costs is the import; what running the build costs is the build. A card no run here has
watched is named, and the build that would watch it with it.

    tools/cad-venv/bin/python hardware/scripts/check_cards.py    (0 = current, 1 = stale)

WHAT THE DIGEST COVERS IS PYTHON. A card also reads STEP files — the cold core's, the funnel's —
and those are drawn by a builder of this repo, so an edit that moves one moves a source this
walk already holds. A vendor STEP replaced by hand is the case it does not see, and `git` does.
"""

import subprocess
import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
import _realized                                        # noqa: E402

# Each card, and the file whose build wrote it. The builder is imported rather than run.
CARDS = [
    (_hw / "manifold-layout" / "enclosure-assembly.scorecard.json",
     _hw / "manifold-layout" / "enclosure_assembly.py"),
    (_hw / "cold-core-layout" / "cold-core-assembly.scorecard.json",
     _hw / "cold-core-layout" / "cold_core_assembly.py"),
    (_hw / "printed-parts" / "cold-core" / "foam-assembly" / "foam-assembly.scorecard.json",
     _hw / "cold-core-layout" / "cold_core_assembly.py"),
]


_WALK = """
import sys
from pathlib import Path
builder = Path(sys.argv[1])
sys.path.insert(0, str(Path(sys.argv[2])))
sys.path.insert(0, str(builder.parent))
import importlib, _realized
importlib.import_module(builder.stem)
print(_realized.digest(_realized.source_files(builder)))
"""


def _digest(builder: Path, _cache={}) -> str:
    """The digest of everything `builder` imports, taken in a PROCESS OF ITS OWN.

    ONE CARD'S WALK MAY NOT SEE ANOTHER'S IMPORTS. A builder puts its own directories on
    `sys.path` as it is imported and they stay there, so walked one after another in a single
    process the second builder resolves names the first one's path made reachable, and its
    graph grows by whatever that other machine imports. `cold_core_assembly` walks 40 files
    alone and 86 behind `enclosure_assembly` — and no run of the generator can write the
    second, because the generator only ever runs alone. The card then reads stale at every
    pass and `owed.py` never reaches its fixpoint.

    A subprocess is the same answer from every caller, which is what `_realized._repo_file`
    promises and cannot keep for walks that share an interpreter. Memoized on the builder,
    since two cards here are written by one build."""
    key = str(builder)
    if key not in _cache:
        out = subprocess.run([sys.executable, "-c", _WALK, key, str(_hw / "scripts")],
                             capture_output=True, text=True)
        if out.returncode != 0:
            raise SystemExit(f"walking {builder.name} failed:\n{out.stderr.strip()}")
        _cache[key] = out.stdout.strip()
    return _cache[key]


def main() -> int:
    stale = []
    for card, builder in CARDS:
        rel = card.relative_to(_hw.parent)
        if not card.is_file():
            print(f"  {rel}\n      no card on disk")
            stale.append(rel)
            continue
        held = _realized.stamp_read("cards", rel.as_posix()).get("sources")
        now = _digest(builder)
        if held is None:
            print(f"  {rel}\n      nothing here has watched this card being made; "
                  f"run {builder.relative_to(_hw.parent)}")
            stale.append(rel)
        elif held != now:
            print(f"  {rel}\n      card {held}  tree {now}\n"
                  f"      a source moved since this card was written; "
                  f"run {builder.relative_to(_hw.parent)}")
            stale.append(rel)
        else:
            print(f"  {rel}\n      current at {held}")
    if stale:
        # WHAT RUNS THEM. A reader who has this list in front of it writes a loop
        # around it — the same loop, by hand, every time — so the list says what
        # takes it. `owed` asks all three of us, runs exactly what is named, and
        # loops to a fixpoint, which a hand-rolled pass over one check's answer
        # cannot: a sync that rewrites a figure stales the doc watching it.
        print("\n  all of them, to a fixpoint: python3 hardware/scripts/owed.py --run")
    print(f"\n{len(CARDS) - len(stale)}/{len(CARDS)} cards describe the tree")
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
