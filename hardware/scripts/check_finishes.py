#!/usr/bin/env python3
"""check_finishes.py — whether `web/public/finishes.json` is the finish table this tree states.

    tools/cad-venv/bin/python hardware/scripts/check_finishes.py            (0 = current, 1 = stale)
    tools/cad-venv/bin/python hardware/scripts/check_finishes.py --write    rewrite it

A COLOUR IS HALF OF WHAT A MATERIAL LOOKS LIKE and the viewer only ever had that half. A STEP
carries `COLOUR_RGB` and nothing else — no roughness, no name — so a body arrives at
`web/public/js/viewer/step.js` already reduced to three numbers, and every one of them was drawn
at one hardcoded `roughness: 0.6`. This file is the other half, carried alongside rather than
inside: the table the viewer looks a finish up in, written from the same constants that wrote the
colour.

The table itself is `_finishes.rows()`; this writes it where the browser can reach it and
fails when what is on disk is not what the tree states.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import _finishes                                                 # noqa: E402

OUT = HERE.parents[1] / "web" / "public" / "finishes.json"
REL = "web/public/finishes.json"

def body():
    """The file's exact bytes — ONE MATERIAL PER LINE, so a diff of this file reads as a list of
    the substances that changed. Stable for an unchanged tree, so `--write` is a no-op then."""
    lines = ",\n".join("  " + json.dumps(r, separators=(", ", ": ")) for r in _finishes.rows())
    return '{\n "finishes": [\n' + lines + "\n ]\n}\n"


def main():
    want = body()
    if "--write" in sys.argv:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(want, encoding="utf-8")
        print(f"-> {REL}  ({len(json.loads(want)['finishes'])} materials)")
        return 0
    got = OUT.read_text(encoding="utf-8") if OUT.exists() else None
    if got != want:
        print(f"{REL} is not the table this tree states"
              f"{' — the file is missing' if got is None else ''}.")
        print("  fix: tools/cad-venv/bin/python hardware/scripts/check_finishes.py --write")
        return 1
    print(f"finishes: {len(json.loads(want)['finishes'])} materials, "
          f"and every colour this tree draws has one")
    return 0


if __name__ == "__main__":
    sys.exit(main())
