"""
Isometric line-art view of the home-soda-machine enclosure — BACK.

CadQuery-based: the appliance geometry is built in _appliance_model and
exported via cq.exporters with HLR (hidden-line removal). In the repo's
+Y-up convention, projectionDir (1, 1, 1) places the camera at +x, +y,
+z — back face, right side, and top visible.

Companion drawing: enclosure-iso-front.py. The geometry is the same;
only the projection direction differs.

Run from the repo root:

    tools/cad-venv/bin/python hardware/printed-parts/enclosure/drawings/line-art/enclosure-iso-back.py
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import cadquery as cq

import _appliance_model as model


def main() -> None:
    appliance = model.build_appliance()
    ring = model.build_red_ring()
    output_path = _HERE / "enclosure-iso-back.svg"
    cq.exporters.export(
        appliance,
        str(output_path),
        opt={
            "projectionDir": (1, 1, 1),  # camera at +x, +y, +z
            "showHidden": False,          # visible outlines only
            "width": None,                 # auto-fit to projected geometry width
            "height": 800,
            "marginLeft": 30,
            "marginTop": 30,
            "strokeWidth": 1.5,
            "showAxes": False,
        },
    )
    model.smooth_stroke(output_path)
    model.add_co2_red_ring(output_path, (1, 1, 1), appliance, ring)
    print(f"Wrote {output_path}")

    # Keep _appliance_model.py's [value](NAME) comments in sync.
    model.refresh_comments()
    print(f"-> updated comments in _appliance_model.py")


if __name__ == "__main__":
    main()
