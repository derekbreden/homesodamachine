"""Isometric engineering drawing of the cold core.

projectionDir (1, 1, -1) places the camera at +x, +y, -z — front
face (the +Z outer wall, the one carrying the copper / water /
PRV slot), top face, and +X side face all visible. Mirrors the
front-iso convention used in the existing line-art drawings.

CadQuery's HLR default: visible edges as solid strokes, hidden
edges as dashed strokes — engineering-drawing aesthetic. No
showHidden=False, no smooth-stroke postprocessor.

Run from the repo root:

    tools/cad-venv/bin/python hardware/printed-parts/cold-core/drawings/engineering-drawings/cold-core-iso.py
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import cadquery as cq

import _cold_core_model as model


def main() -> None:
    cold_core = model.build_cold_core()
    output_path = _HERE / "cold-core-iso.svg"
    cq.exporters.export(
        cold_core,
        str(output_path),
        opt={
            "projectionDir": (1, 1, -1),  # camera at +x, +y, -z
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
