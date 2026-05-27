"""Isometric engineering drawing of the touch-flo faucet assembly.

CadQuery HLR (hidden-line removal) with hidden edges DASHED — the
engineering-drawing aesthetic, as opposed to the line-art renders in
`../line-art/`.

The faucet's native frame is Z-up (body axis along +Z, gooseneck
dispense direction along -X). For the SVG export we re-orient the
loaded assembly into a frame where +Y is body-up: this is what
OCCT's HLR projector treats as image-up under the iso projectionDir
below, so the body draws vertical in the rendered image. The
projection then has the gooseneck arching up and toward the viewer
with the lever pointing toward the viewer — the user's view standing
at the sink.

Run from the repo root:
    tools/cad-venv/bin/python hardware/printed-parts/faucet/drawings/engineering-drawings/faucet-iso.py
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import cadquery as cq

import _faucet_model as model


def main() -> None:
    # Re-orient native (Z-up) -> drawing-frame (Y-up). Composed, the
    # two rotations map original (X, Y, Z) -> (-Y, Z, -X):
    #   +Z body-up          ->  +Y  (image-up under projectionDir below)
    #   -X gooseneck tip    ->  +Z  (toward the viewer)
    #   +Y lateral          ->  -X
    faucet = (
        model.build_faucet()
        .rotate((0, 0, 0), (0, 0, 1), 90)    # spin 90° about body axis
        .rotate((0, 0, 0), (1, 0, 0), -90)   # tip 90° onto its side
    )
    output_path = _HERE / "faucet-iso.svg"
    cq.exporters.export(
        faucet,
        str(output_path),
        opt={
            "projectionDir": (-1, 1, 1),  # camera at -x, +y, +z (user iso)
            "width": None,                  # auto-fit to projected width
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
