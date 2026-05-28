"""
Isometric line-art view of the home-soda-machine enclosure — BACK.

The appliance and its red ring marking are built as 3D CadQuery solids
in _appliance_model, exported as STL, and rendered to a vector SVG via
Blender's Freestyle line renderer (with the Freestyle SVG Exporter
add-on).

Iso-back camera: positioned at world (+X, +Y, +Z) and aimed at the
geometric center with world +Z as up, so the back face (+Y), right
face (+X), and top face (+Z) are all visible.

Companion drawing: enclosure-iso-front.py. The geometry is the same;
only the view direction differs.

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
    disc_params = model.red_disc_render_params()
    coupler = model.build_coupler()
    output_path = _HERE / "enclosure-iso-back.svg"
    blender.render_iso(appliance, disc_params, coupler, view="back", out_svg=output_path)
    print(f"Wrote {output_path}")

    # Keep _appliance_model.py's [value](NAME) comments in sync.
    model.refresh_comments()
    print(f"-> updated comments in _appliance_model.py")


if __name__ == "__main__":
    main()
