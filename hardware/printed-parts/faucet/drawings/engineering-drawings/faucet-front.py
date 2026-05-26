"""Front engineering drawing of the touch-flo faucet assembly.

CadQuery HLR (hidden-line removal) with hidden edges DASHED.

projectionDir (-1, 0, 0) places the camera on the +X axis looking
toward -X — i.e. looking AT the dispense tip, head-on with the
gooseneck swing. The valve body and shell appear as a column rising
on the right; the gooseneck arcs out toward the viewer and reads
mostly foreshortened. The two flavor tubes (mirrored across the XZ
plane) overlap each other at this projection, and the water-tube
gooseneck profile shows in elevation.

Note: looking along -X means features behind the shell (lever, body)
become hidden lines, which appear dashed.

Run from the repo root:
    tools/cad-venv/bin/python hardware/printed-parts/faucet/drawings/engineering-drawings/faucet-front.py
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import cadquery as cq

import _faucet_model as model


def main() -> None:
    faucet = model.build_faucet()
    output_path = _HERE / "faucet-front.svg"
    cq.exporters.export(
        faucet,
        str(output_path),
        opt={
            "projectionDir": (-1, 0, 0),  # camera on +X axis looking -X
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
