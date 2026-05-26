"""Top engineering drawing of the touch-flo faucet assembly.

CadQuery HLR (hidden-line removal) with hidden edges DASHED.

projectionDir (0, 0, -1) places the camera on the +Z axis looking
toward -Z — i.e. looking straight DOWN onto the faucet (Z is the
vertical axis through the valve body). The shell base reads as a
circle/rectangle at the bottom of the stackup, the gooseneck sweeps
toward +X across the page (the dispense tip ends to the upper edge
of the image), and the shank/body/tubes-below are hidden lines
beneath the visible top profile.

This projection points the gooseneck toward the top of the image
(viewer looks down +Z, +X is "up" on the page in screen
coordinates). For a layout where the gooseneck points toward the
bottom of the image, swap to (0, 0, 1).

Run from the repo root:
    tools/cad-venv/bin/python hardware/printed-parts/faucet/drawings/engineering-drawings/faucet-top.py
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import cadquery as cq

import _faucet_model as model


def main() -> None:
    faucet = model.build_faucet()
    output_path = _HERE / "faucet-top.svg"
    cq.exporters.export(
        faucet,
        str(output_path),
        opt={
            "projectionDir": (0, 0, -1),  # camera on +Z axis looking -Z
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
