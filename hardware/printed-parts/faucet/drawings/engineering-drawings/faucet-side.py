"""Side engineering drawing of the touch-flo faucet assembly.

CadQuery HLR (hidden-line removal) with hidden edges DASHED.

projectionDir (0, 1, 0) places the camera on the -Y axis looking
toward +Y — i.e. looking along the symmetric axis from the -Y side.
The valve body is symmetric about the XZ plane (flavor tubes mirror
+Y/-Y), so this view shows the gooseneck's swing in true profile:
the dispense tip extends to the +X side, the gooseneck arcs up and
forward from the valve body, and the shell/mounting plate/gasket
stack reads top to bottom on the +Z side.

This is the "elevation" most useful for reading bend angles and
gooseneck reach; the two flavor tubes superimpose on the water
tube along the page-normal, with their inner-vs-outer arc
separation visible at each bend.

Run from the repo root:
    tools/cad-venv/bin/python hardware/printed-parts/faucet/drawings/engineering-drawings/faucet-side.py
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import cadquery as cq

import _faucet_model as model


def main() -> None:
    faucet = model.build_faucet()
    output_path = _HERE / "faucet-side.svg"
    cq.exporters.export(
        faucet,
        str(output_path),
        opt={
            "projectionDir": (0, 1, 0),  # camera on -Y axis looking +Y
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
