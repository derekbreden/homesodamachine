#!/usr/bin/env python3
"""Every generator in the tree and what it makes, read off what the tree already records.

    tools/cad-venv/bin/python tools/bazel/inventory.py        # print it

Three readings, in the order they are trusted:

  - A SOLID SAYS WHO CUT IT. `.cache/stamps/parts/<solid>.json` carries `by`, written by the
    run that cut it. Six directories hold artifacts and more than one `.py` — `manifold-layout`
    holds the assembly and the manifold — and this is what tells them apart.
  - A DOC SAYS WHO WROTE ITS FIGURES. `<doc>.figures.json` is keyed by driver, written by
    `docgen.substitute_md`. A doc sync cuts no solid and is invisible to any rule about
    artifacts, and this finds every one of them.
  - Failing both, the one `.py` beside the artifact. A first build has no stamp, and the
    convention holds for 101 of the 102 committed solids.
"""

import json
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[2]
sys.path.insert(0, str(_ROOT / "hardware" / "scripts"))

import _realized                                        # noqa: E402

SOLID_SUFFIXES = (".step", ".dxf", ".stl", ".step.png", ".dxf.png",
                  ".scorecard.json", ".facts.json")

#: What one run draws that lands nowhere near its own directory. `render_scenes` cuts a scene
#: out of a machine somebody else stood, so the picture, its record and the mesh a browser
#: opens are three trees away from the script.
ELSEWHERE = {
    "hardware/assembly/scenes/render_scenes.py": (
        "hardware/assembly/cards/img/scene-", "hardware/assembly/scenes/glb/"),
}
FIGURES_SUFFIX = ".figures.json"


def tracked() -> list:
    return subprocess.run(["git", "-C", str(_ROOT), "ls-files"],
                          capture_output=True, text=True, check=True).stdout.split()


def _one_py_beside(art: str, by_dir: dict):
    pys = [f for f in by_dir.get(str(Path(art).parent), [])
           if f.endswith(".py") and not Path(f).name.startswith("_")]
    return pys[0] if len(pys) == 1 else None


def inventory(files=None) -> dict:
    """`{generator: {"solids": [...], "docs": [...]}}` for every generator this tree has."""
    files = files or tracked()
    by_dir = {}
    for f in files:
        by_dir.setdefault(str(Path(f).parent), []).append(f)

    out = {}
    for art in sorted(f for f in files if f.endswith(SOLID_SUFFIXES)):
        gen = (_realized.stamp_read("parts", _ROOT / art).get("by")
               or _one_py_beside(art, by_dir))
        if gen and gen in files:
            out.setdefault(gen, {"solids": [], "docs": []})["solids"].append(art)

    # A card in `manifold-layout` holds the assembly's readings and one beside it holds the
    # manifold's; the name is what tells them apart where the directory cannot.
    for gen in list(out):
        stem = Path(gen).stem.replace("_", "-")
        for f in files:
            if (f.endswith((".scorecard.json", ".facts.json"))
                    and Path(f).name.startswith(stem) and f not in out[gen]["solids"]):
                out[gen]["solids"].append(f)

    for gen, prefixes in ELSEWHERE.items():
        if gen not in files:
            continue
        entry = out.setdefault(gen, {"solids": [], "docs": []})
        for f in files:
            if f.startswith(prefixes) and f not in entry["solids"]:
                entry["solids"].append(f)
            side = f + ".scene.json"
            if f.startswith(prefixes[0]) and side in files and side not in entry["solids"]:
                entry["solids"].append(side)

    for side in sorted(f for f in files if f.endswith(FIGURES_SUFFIX)):
        doc = side[:-len(FIGURES_SUFFIX)] + ".md"
        try:
            drivers = json.loads((_ROOT / side).read_text())
        except (OSError, ValueError):
            continue
        for driver in drivers:
            gen = driver.lstrip("/")
            if gen not in files:
                continue
            entry = out.setdefault(gen, {"solids": [], "docs": []})
            for f in (doc, side):
                if f in files and f not in entry["docs"]:
                    entry["docs"].append(f)
    return out


def main() -> int:
    inv = inventory()
    solids = sum(len(v["solids"]) for v in inv.values())
    docs = sum(len(v["docs"]) for v in inv.values())
    print(f"  {len(inv)} generators, {solids} solids, {docs} doc files")
    multi = [g for g, v in inv.items() if v["solids"] and v["docs"]]
    print(f"  {len(multi)} cut a solid AND write a doc")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
