"""Isometric engineering drawing of the touch-flo faucet assembly: HLR
(hidden-line removal) with hidden edges dashed.

The assembly is +Z-up natively (body height along +Z, gooseneck
dispensing toward -Y). Rotating -90° about +X lands the body's height
axis on +Y, the direction OCCT's HLR projector reads as image-up.

In the rotated frame, projectionDir (1, 1, 1) matches the 3D STEP
viewer's default front-iso camera (web/public/js/viewer/scene.js
resetCamera: world camera at +x, -y, +z, up +Z): body upright,
gooseneck dispensing toward the lower-left (the user's side), lever
toward the viewer.

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
    faucet_drawing = faucet.rotate((0, 0, 0), (1, 0, 0), -90)
    output_path = _HERE / "faucet-iso.svg"
    cq.exporters.export(
        faucet_drawing,
        str(output_path),
        opt={
            "projectionDir": (1, 1, 1),  # rotated frame = 3D viewer's world (1,-1,1), up +Z
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
