"""
Isometric line-art view of the home-soda-machine enclosure — FRONT.

Canonical iso layout: top of enclosure at top of image, front face (y=0) at
lower-right, right side face (x=W) at lower-left.

Companion drawing: enclosure-iso-back.py (back face + left side + top).
Shared top-face features (GFCI band, pump door, hopper lid) and the
enclosure outer dimensions live in _common.py; both view scripts use them.

Run from the repo root:

    tools/cad-venv/bin/python hardware/printed-parts/enclosure/drawings/enclosure-iso-front.py

Source for the feature inventory:
hardware/printed-parts/enclosure/README.md
"""

import sys
from pathlib import Path

# tools/line-art/ for the drawing library; _HERE for the local _common
# module that carries the enclosure dimensions + shared top-face features.
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[3]
sys.path.insert(0, str(_REPO_ROOT / "tools" / "line-art"))
sys.path.insert(0, str(_HERE))

from line_art import Scene, Box
import _common as common


def main() -> None:
    scene = Scene(view="front")
    appliance = scene.add(Box(W=common.APPLIANCE_W, D=common.APPLIANCE_D, H=common.APPLIANCE_H))

    # Front face: ESP32-S3 rotary display (~32 mm OD), protruding 19 mm
    # so its sides can be gripped to turn it. Placed high on the front
    # face — in front of the Zone C funnel/hopper, which leaves only a
    # small amount of interior depth at that height; the knob's depth
    # lives outside the enclosure where the gripping happens.
    appliance.front.add_knob(at=(135, 235), d=32, protrusion=19, label="ESP32-S3")

    # Top face: shared features (GFCI band, pump door, hopper lid).
    common.add_top_face_features(appliance)

    output_path = _HERE / "enclosure-iso-front.svg"
    scene.render(str(output_path))
    print(f"Wrote {output_path}")

    # Keep _common.py's [value](NAME) link comments in sync with current values.
    common.refresh_comments()
    print(f"-> updated comments in _common.py")


if __name__ == "__main__":
    main()
