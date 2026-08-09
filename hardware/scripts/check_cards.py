#!/usr/bin/env python3
"""check_cards.py — whether a committed scorecard still describes the tree.

A card is what the machine measured, and it is written by a build. Between two builds an agent
edits a source and the card on disk goes on reading whatever the last build found — the numbers
look like measurements and are a memory of one. That is the state this answers.

Each card carries `sources`: the digest of the whole text of every file of this repo its build
could reach, walked off the import statements by `_realized.source_files`. This imports the same
builder, takes the digest again, and compares two hex strings. What it costs is the import; what
running the build costs is the build.

    tools/cad-venv/bin/python hardware/scripts/check_cards.py    (0 = current, 1 = stale)

WHAT THE DIGEST COVERS IS PYTHON. A card also reads STEP files — the cold core's, the funnel's —
and those are drawn by a builder of this repo, so an edit that moves one moves a source this
walk already holds. A vendor STEP replaced by hand is the case it does not see, and `git` does.
"""

import importlib
import json
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


def _digest(builder: Path) -> str:
    """The digest of everything `builder` imports, with the module imported so the walk can
    resolve each name it reads to a file."""
    sys.path.insert(0, str(builder.parent))
    importlib.import_module(builder.stem)
    return _realized.digest(_realized.source_files(builder))


def main() -> int:
    stale = []
    for card, builder in CARDS:
        rel = card.relative_to(_hw.parent)
        if not card.is_file():
            print(f"  {rel}\n      no card on disk")
            stale.append(rel)
            continue
        held = json.loads(card.read_text()).get("sources")
        now = _digest(builder)
        if held is None:
            print(f"  {rel}\n      carries no `sources` — rebuild it once to give it one")
            stale.append(rel)
        elif held != now:
            print(f"  {rel}\n      card {held}  tree {now}\n"
                  f"      a source moved since this card was written; "
                  f"run {builder.relative_to(_hw.parent)}")
            stale.append(rel)
        else:
            print(f"  {rel}\n      current at {held}")
    print(f"\n{len(CARDS) - len(stale)}/{len(CARDS)} cards describe the tree")
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
