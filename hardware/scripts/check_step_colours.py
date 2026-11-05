#!/usr/bin/env python3
"""check_step_colours.py — whether each model the site lists draws in the colour of what it is made of.

    python3 hardware/scripts/check_step_colours.py     (0 = every model coloured, 1 = some are not)

A BODY IS COLOURED TWICE AND THE TWO ARE DIFFERENT QUESTIONS. The assembly that places a body
paints it as it adds it, and `enclosure_assembly`'s `bodies-colored` row reads that: every placed
solid carries a colour. A model's OWN picture is the other half — its card and `/3d` — and
`web/public/js/viewer/step.js` paints a body that names no colour at `DEFAULT_FRONT`, a blue-grey
that is no material on this machine. So a part can be black in the picture of the appliance and
blue-grey in the picture of itself, with the assembly's own gate green over it.

THE SITE'S MODELS ARE THE READING: the `.step` files `hardware/cad-artifacts.json` selects for the
website, which are the models `/api/steps` lists. The viewer draws a model from its `.step.mesh`
payload when it has one, so each mesh colour the payload names is what a reader sees; a model with
no payload is drawn from its STEP, and a STEP names its colours as `COLOUR_RGB` entities.

`cq.exporters.export` writes geometry and no colour. `hardware/scripts/_materials.one_body` is
what a generator wraps a solid in so `export_assembly` bakes the material in beside the geometry.
"""

import json
import struct
import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_root = _hw.parent
POINTERS = _hw / "cad-artifacts.json"

# The STEP entity a colour arrives as. AP214 writes one per distinct colour, referenced by a
# `STYLED_ITEM` per shape; a file with none names no colour for anything in it.
COLOUR_ENTITY = b"COLOUR_RGB"
_CHUNK = 1 << 20


def site_models() -> list:
    """The STEPs the website selection carries, repo-relative: the models `/api/steps` lists."""
    selection = json.loads(POINTERS.read_text())["website"]["solids"]
    return sorted(p for p in selection if p.startswith("hardware/") and p.endswith(".step"))


def payload_colours(path):
    """The colour each mesh of a `.step.mesh` payload names, or None when there is no payload."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    (size,) = struct.unpack_from("<I", data)
    return [mesh.get("color") for mesh in json.loads(data[4:4 + size])["meshes"]]


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


def draws_coloured(rel: str) -> bool:
    """Whether the viewer draws every body of this model in a colour it names."""
    colours = payload_colours(_root / f"{rel}.mesh")
    if colours is None:
        return carries_colour(_root / rel)
    return all(colours)


def main() -> int:
    models = site_models()
    absent = [rel for rel in models if not (_root / rel).is_file()]
    grey = [rel for rel in models if rel not in absent and not draws_coloured(rel)]
    for rel in absent:
        print(f"  not on this disk: {rel}")
    if grey:
        print(f"  {len(grey)} model(s) the site lists name no colour, so /3d and their own cards "
              f"draw them at the viewer's blue-grey:")
        for rel in grey:
            print(f"    {rel}")
        print("  A generator hands its solid to `_materials.one_body` and exports the assembly.")
    if absent:
        print(f"step colours: {len(absent)} of {len(models)} site models are not on this disk; "
              f"`node web/scripts/fetch-cad-artifacts.mjs` fetches them.")
        return 1
    print(f"step colours: {len(models) - len(grey)}/{len(models)} site models draw in the colour "
          f"of what they are made of")
    return 1 if grey else 0


if __name__ == "__main__":
    sys.exit(main())
