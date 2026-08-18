#!/usr/bin/env python3
"""check_facts_current.py — the facts name the card and the solid they were taken beside.

`enclosure_assembly.main()` writes three artifacts from one run: the assembly STEP, then the
scorecard, then `enclosure-assembly.facts.json`. The facts carry a digest of each of the two
written before them, so the three either name each other or they came off different runs.

This reads those digests against the files in the tree — one JSON read and one digest apiece.
The STEP is fetched rather than committed, and a checkout without it answers on the card alone.

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
        held = "card and solid" if facts.agrees_with_step() is not None else "card"
        print(f"the enclosure's facts name the {held} they were taken beside")
        return 0

    for line in stale:
        print(f"  {line}", file=sys.stderr)
    print("  the three come off one run:\n"
          "    tools/cad-venv/bin/python hardware/manifold-layout/enclosure_assembly.py",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
