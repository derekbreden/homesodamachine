"""Side engineering drawing of the cold core.

projectionDir (-1, 0, 0) places the camera at -X looking toward
+X — the -X side wall (carrying the -X reservoir-bulkhead port)
fills the frame; the +X side wall and everything between appear
as hidden dashed lines. +Y runs up.

CadQuery's HLR default: visible edges as solid strokes, hidden
edges as dashed strokes — engineering-drawing aesthetic.

Run from the repo root:

    tools/cad-venv/bin/python hardware/printed-parts/cold-core/drawings/engineering-drawings/cold-core-side.py
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import cadquery as cq

import _cold_core_model as model


def main() -> None:
    cold_core = model.build_cold_core()
    output_path = _HERE / "cold-core-side.svg"
    cq.exporters.export(
        cold_core,
        str(output_path),
        opt={
            "projectionDir": (-1, 0, 0),  # camera at +x, looking at +X face
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
