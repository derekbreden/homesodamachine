"""Isometric engineering drawing of the appliance enclosure with the
cold-core foam shell nested inside.

CadQuery HLR (hidden-line removal) with hidden edges DASHED — the
engineering-drawing aesthetic. No showHidden override, no smooth-stroke
postprocessor; the dashed hidden lines reveal the cold core's outline
through the enclosure walls.

The model is +Z-up natively; for the SVG export we rotate +90° about
+X so the body's height axis lands on +Y at projection time (see
`../line-art/enclosure-iso-front.py`'s docstring for the OCCT-HLR
rationale). In the rotated drawing frame, projectionDir (1, 1, -1)
places the camera at +x, +y, -z — front face, right side, and top
all visible (standard engineering iso layout).

Run from the repo root:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/drawings/engineering-drawings/enclosure-assembly-iso.py
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import cadquery as cq

import _enclosure_assembly_model as model


def main() -> None:
    assembly = model.build_enclosure_assembly()
    # Rotate the Z-up assembly into a drawing frame where the body
    # height axis lands on +Y (see docstring).
    assembly_drawing = assembly.rotate((0, 0, 0), (1, 0, 0), 90)
    output_path = _HERE / "enclosure-assembly-iso.svg"
    cq.exporters.export(
        assembly_drawing,
        str(output_path),
        opt={
            "projectionDir": (1, 1, -1),  # camera at +x, +y, -z (rotated drawing frame)
            "width": None,                  # auto-fit projected width
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
