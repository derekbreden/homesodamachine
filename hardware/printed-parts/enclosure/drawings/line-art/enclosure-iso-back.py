"""
Isometric line-art view of the home-soda-machine enclosure — BACK.

Iso-back camera: positioned at world (+X, +Y, +Z) and aimed at the
geometric center with world +Z as up, so the back face (+Y), right
face (+X), and top face (+Z) are all visible.

Companion drawing: enclosure-iso-front.py — same geometry, front view.

Run from the repo root:

    tools/cad-venv/bin/python hardware/printed-parts/enclosure/drawings/line-art/enclosure-iso-back.py
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import _appliance_model as model
import _blender_render as blender


def main() -> None:
    appliance = model.build_appliance()
    markings = model.markings("back")
    output_path = _HERE / "enclosure-iso-back.svg"
    blender.render_iso(appliance, markings, view="back", out_svg=output_path)
    print(f"Wrote {output_path}")

    # [value](NAME)
    model.refresh_comments()
    print(f"-> updated comments in _appliance_model.py")


if __name__ == "__main__":
    main()
