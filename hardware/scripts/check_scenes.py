#!/usr/bin/env python3
"""check_scenes.py — whether each unit card's picture is still the one its sources draw.

A scene PNG is a rendering of a subset of the machine, and every scene is drawn from the code
that builds that machine, the tables that say which part holds which body, and the camera in
`hardware/assembly/scenes/_scenes.py`. Between two renders any of those moves and the card goes
on printing whatever the last one drew.

    tools/cad-venv/bin/python hardware/scripts/check_scenes.py     (0 = current, 1 = stale)

WHAT THIS COSTS IS READING THE FILES THE RENDER WROTE DOWN. Beside each PNG the render leaves
`<png>.scene.json`: the scene's own tuple, hashed, and every repo file whose text could decide
the picture, each with the hash of its bytes. This hashes those files again and compares. No
module is imported, no geometry is built — which is the whole bargain, because a picture is
expensive to draw and cheap to doubt, and the doubting is what runs on every commit.

THE RECORDED LIST IS THE READING and not a list to take again here. Resolving the build's import
graph means asking `find_spec` for each name, which imports the package a dotted name hangs off;
from a cold process that loads OCP, costs seconds, and still comes back short, because the paths
the build runs under are not set up. The render walks it from inside, where the answer is free
and complete.

A scene whose PNG has never been drawn is reported as missing, not as current.
"""

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_HW = next(p for p in _HERE.parents if p.name == "hardware")
_ROOT = _HW.parent
if str(_HW / "assembly" / "scenes") not in sys.path:
    sys.path.insert(0, str(_HW / "assembly" / "scenes"))

import _scenes                                          # noqa: E402

IMG_DIR = _HW / "assembly" / "cards" / "img"


def png_for(scene) -> Path:
    return IMG_DIR / f"scene-{scene.id}.png"


def state(scene) -> tuple:
    """`(verdict, detail)` for one scene — "current", "stale" or "missing"."""
    png = png_for(scene)
    if not png.is_file():
        return "missing", "no picture has been drawn"
    sidecar = _scenes.sidecar_path(png)
    if not sidecar.is_file():
        return "stale", "the picture carries no record of what drew it"
    try:
        held = json.loads(sidecar.read_text())
    except ValueError:
        return "stale", "the record beside it will not parse"

    if held.get("scene") != _scenes.scene_digest(scene):
        return "stale", "the scene's own roots or camera have changed"

    sources = held.get("sources") or {}
    if not sources:
        return "stale", "the record names no sources"
    moved = [rel for rel, was in sorted(sources.items()) if _scenes.hash_of(rel) != was]
    if moved:
        head = ", ".join(moved[:3]) + (f" and {len(moved) - 3} more" if len(moved) > 3 else "")
        return "stale", f"{len(moved)} of {len(sources)} sources moved: {head}"
    return "current", f"current against {len(sources)} sources"


def main() -> int:
    rows = [(s, *state(s)) for s in _scenes.SCENES]
    bad = [r for r in rows if r[1] != "current"]
    for scene, verdict, detail in rows:
        print(f"  {scene.id:16} {verdict:8} {detail}")
        if verdict != "current":
            print("      run tools/cad-venv/bin/python "
                  f"hardware/assembly/scenes/render_scenes.py {scene.id}")
    print(f"\n{len(rows) - len(bad)}/{len(rows)} scenes carry the picture their sources draw")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
