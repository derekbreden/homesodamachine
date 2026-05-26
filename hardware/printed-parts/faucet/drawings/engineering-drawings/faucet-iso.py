"""Isometric engineering drawing of the touch-flo faucet assembly.

CadQuery HLR (hidden-line removal) with hidden edges DASHED — the
engineering-drawing aesthetic, as opposed to the line-art renders in
`../line-art/`. The faucet is drawn in the repo's +Y-up frame (the
upstream Z-up assembly is rebased in `_faucet_model.build_faucet`).

projectionDir (1, 1, -1) places the camera at +x, +y, -z — looking at
the dispense side, with the valve body upright and the gooseneck
arching forward toward the viewer's lower-left. Matches the iso
convention used by the enclosure-iso-front and engineering-drawing
counterparts for the cold core and enclosure assembly.

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
    faucet = model.build_faucet()
    output_path = _HERE / "faucet-iso.svg"
    cq.exporters.export(
        faucet,
        str(output_path),
        opt={
            "projectionDir": (1, 1, -1),  # camera at +x, +y, -z
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
