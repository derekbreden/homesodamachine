#!/usr/bin/env python3
"""check_step_colours.py — whether each solid's own STEP carries the colour of what it is made of.

    python3 hardware/scripts/check_step_colours.py     (0 = every STEP coloured, 1 = some are not)

A BODY IS COLOURED TWICE AND THE TWO ARE DIFFERENT QUESTIONS. The assembly that places a body
paints it as it adds it, and `enclosure_assembly`'s `bodies-colored` row reads that: every placed
solid carries a colour. A body's OWN STEP is the other half, and it is what the part's own card
and `/3d` draw — `web/public/js/viewer/step.js` paints a body whose STEP carries no colour at
`DEFAULT_FRONT`, a blue-grey that is no material on this machine. So a part can be black in the
picture of the appliance and blue-grey in the picture of itself, with the assembly's own gate
green over it.

`cq.exporters.export` writes geometry and no colour. `hardware/scripts/_materials.one_body` is
what a generator wraps a solid in so `export_assembly` bakes the material in beside the geometry.

`git ls-files` IS THE READING, and not the directory: a STEP the index does not hold is a STEP a
fresh clone does not have, and a directory listing that finds it there is reading leftovers.
"""

import subprocess
import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_root = _hw.parent

# The STEP entity a colour arrives as. AP214 writes one per distinct colour, referenced by a
# `STYLED_ITEM` per shape; a file with none names no colour for anything in it.
COLOUR_ENTITY = b"COLOUR_RGB"
_CHUNK = 1 << 20


def _tracked_steps() -> list:
    """Every `.step` the index holds under `hardware/`, repo-relative."""
    out = subprocess.run(["git", "-C", str(_root), "ls-files", "hardware"],
                         capture_output=True, text=True, check=True).stdout
    return sorted(p for p in out.splitlines() if p.endswith(".step"))


def carries_colour(path) -> bool:
    """Whether `path` names a colour anywhere in it.

    Read in chunks and overlapped by the token's length: the entity sits past the geometry in
    every file OCCT writes, and the largest STEP in this tree is tens of megabytes."""
    keep = len(COLOUR_ENTITY) - 1
    try:
        with open(path, "rb") as fh:
            tail = b""
            while True:
                chunk = fh.read(_CHUNK)
                if not chunk:
                    return False
                if COLOUR_ENTITY in tail + chunk:
                    return True
                tail = chunk[-keep:] if keep else b""
    except OSError:
        return False


def main() -> int:
    steps = _tracked_steps()
    bare = [rel for rel in steps if not carries_colour(_root / rel)]
    print(f"step colours: {len(steps) - len(bare)}/{len(steps)} carry the colour of what they are "
          f"made of")
    if not bare:
        return 0
    print(f"  {len(bare)} STEP(s) name no colour, so /3d and their own cards draw them at the "
          f"viewer's blue-grey:")
    for rel in bare:
        print(f"    {rel}")
    print("  A generator hands its solid to `_materials.one_body` and exports the assembly.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
