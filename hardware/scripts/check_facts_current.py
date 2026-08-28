#!/usr/bin/env python3
"""check_facts_current.py — the facts name the card, the solid and the tree they came off.

`enclosure_assembly.main()` writes three artifacts from one run: the assembly STEP, then the
scorecard, then `enclosure-assembly.facts.json`. The facts carry a digest of each of the two
written before them, so the three either name each other or they came off different runs.

THAT THEY CAME OFF ONE RUN IS NOT THAT THE RUN WAS THIS TREE. Three artifacts written together
agree with each other for as long as they exist, whatever the sources have done since, so a
check on those two digests alone cannot fail on the one fault it is here for: a reading that
still describes a machine the tree has moved off. `_facts.sources` is the third digest — what
`tools/bazel/graph.json` traced the generator opening, less everything some generator writes —
and it is what makes staleness visible rather than self-consistent.

This reads all three against the files in the tree. The STEP is fetched rather than committed,
and a checkout without it answers on the card alone; an artifact written before the source
digest existed carries none, and is reported as silent rather than failed.

    python3 hardware/scripts/check_facts_current.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _facts                                                           # noqa: E402


def main() -> int:
    try:
        facts = _facts.read()
    except FileNotFoundError as e:
        print(f"  {e}", file=sys.stderr)
        return 1

    stale = facts.stale()
    if not stale:
        held = ["card"] + (["solid"] if facts.agrees_with_step() is not None else [])
        print(f"the enclosure's facts name the {' and '.join(held)} they were taken beside")
        if facts.agrees_with_sources() is None:
            print("  and carry no digest for the tree they were taken from — the next run of "
                  "the generator writes one")
        else:
            print(f"  and the {len(_facts.sources())} sources behind them stand where they "
                  f"stood when it was written")
        return 0

    for line in stale:
        print(f"  {line}", file=sys.stderr)
    print("  the three come off one run:\n"
          "    tools/cad-venv/bin/python hardware/manifold-layout/enclosure_assembly.py",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
