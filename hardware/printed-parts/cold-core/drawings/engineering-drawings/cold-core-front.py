"""Front engineering drawing of the cold core.

projectionDir (0, 0, -1) places the camera at -Z looking toward
+Z — the -Z outer wall fills the frame, with everything behind it
(reservoir pockets, support ring, coil mandrel windings, copper
plug stack on the far +Z wall) appearing as hidden dashed lines.
+X runs left/right, +Y runs up.

CadQuery's HLR default: visible edges as solid strokes, hidden
edges as dashed strokes — engineering-drawing aesthetic.

Run from the repo root:

    tools/cad-venv/bin/python hardware/printed-parts/cold-core/drawings/engineering-drawings/cold-core-front.py
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import cadquery as cq

import _cold_core_model as model


def main() -> None:
    cold_core = model.build_cold_core()
    output_path = _HERE / "cold-core-front.svg"
    cq.exporters.export(
        cold_core,
        str(output_path),
        opt={
            "projectionDir": (0, 0, -1),  # camera at +z, looking at +Z face
            "width": None,
            "height": 800,
            "marginLeft": 30,
            "marginTop": 30,
            "strokeWidth": 1.5,
            "showAxes": False,
        },
    )
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
