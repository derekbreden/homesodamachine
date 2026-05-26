"""Top engineering drawing of the cold core.

projectionDir (0, -1, 0) places the camera below the foam shell
looking up along the +Y axis — the foam-shell floor (the y = 0
plane) fills the frame, with the support ring, reservoir-pocket
walls, tank cavity, copper-plug stack and coil mandrel above it
appearing as hidden dashed lines.

CadQuery's HLR default: visible edges as solid strokes, hidden
edges as dashed strokes — engineering-drawing aesthetic.

Run from the repo root:

    tools/cad-venv/bin/python hardware/printed-parts/cold-core/drawings/engineering-drawings/cold-core-top.py
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import cadquery as cq

import _cold_core_model as model


def main() -> None:
    cold_core = model.build_cold_core()
    output_path = _HERE / "cold-core-top.svg"
    cq.exporters.export(
        cold_core,
        str(output_path),
        opt={
            "projectionDir": (0, -1, 0),  # camera at +y, looking down
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
