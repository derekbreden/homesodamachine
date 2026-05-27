"""Isometric engineering drawing of the cold core.

The model is +Z-up natively; for the SVG export we rotate +90° about
+X to land the body axis on +Y. That's the direction OCCT's HLR
projector reads as image-up for an iso projectionDir — without the
rotation, +Y (world depth) gets image-up instead of +Z (world height)
and the body leans diagonally in the rendered SVG. The rotation is
local to this script's export step; the model passed downstream
elsewhere stays +Z-up.

In the rotated drawing frame, projectionDir (1, 1, -1) places the
camera at +x, +y, -z — the viewer's front-iso angle. Top face,
front face, and right face all visible.

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
    # Rotate the Z-up model into a drawing frame where the body axis
    # lands on +Y, so OCCT's HLR projector treats world height as
    # image-up (see docstring).
    cold_core_drawing = cold_core.rotate((0, 0, 0), (1, 0, 0), 90)
    output_path = _HERE / "cold-core-iso.svg"
    cq.exporters.export(
        cold_core_drawing,
        str(output_path),
        opt={
            "projectionDir": (1, 1, -1),  # camera at +x, +y, -z (in the rotated drawing frame)
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
