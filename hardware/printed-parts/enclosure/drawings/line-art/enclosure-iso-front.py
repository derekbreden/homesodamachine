"""
Isometric line-art view of the home-soda-machine enclosure — FRONT.

Iso-front camera: positioned at world (+X, -Y, +Z) and aimed at the
geometric center with world +Z as up, so the front face (-Y), right
face (+X), and top face (+Z) are all visible. The top face sits at the
top of the image, with the front and right faces in the lower half.

What this view carries: the 45° display facet across the top-front arris, the
hopper throat through the top wall — and a FRONT FACE WITH NOTHING ON IT, which
is the whole of what the front of this machine has.

Companion drawing: enclosure-iso-back.py — same geometry, view from (+Y).

Run from the repo root:

    tools/cad-venv/bin/python hardware/printed-parts/enclosure/drawings/line-art/enclosure-iso-front.py
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import _appliance_model as model
import _blender_render as blender


def main() -> None:
    appliance = model.build_appliance()
    output_path = _HERE / "enclosure-iso-front.svg"
    blender.render_iso(appliance, model.markings("front"), view="front",
                       out_svg=output_path, anchors=model.anchors("front"))
    print(f"Wrote {output_path}")

    model.refresh_comments()
    print(f"-> updated comments in _appliance_model.py")


if __name__ == "__main__":
    main()
