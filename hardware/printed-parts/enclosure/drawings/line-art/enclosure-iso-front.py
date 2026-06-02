"""
Isometric line-art view of the home-soda-machine enclosure — FRONT.

Iso-front camera: positioned at world (+X, -Y, +Z) and aimed at the
geometric center with world +Z as up, so the front face (-Y), right
face (+X), and top face (+Z) are all visible. The top face sits at the
top of the image, with the front and right faces in the lower half.

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
    markings = model.markings("front")
    anchors = [{
        "id": "hopper-door-center",
        "point": [model.hopper_door_a, model.hopper_door_b, model.H],
    }]
    output_path = _HERE / "enclosure-iso-front.svg"
    blender.render_iso(appliance, markings, view="front", out_svg=output_path, anchors=anchors)
    print(f"Wrote {output_path}")

    model.refresh_comments()
    print(f"-> updated comments in _appliance_model.py")


if __name__ == "__main__":
    main()
