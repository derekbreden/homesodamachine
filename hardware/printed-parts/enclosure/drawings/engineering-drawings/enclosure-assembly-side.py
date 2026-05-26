"""Side engineering drawing of the appliance enclosure with the
cold-core foam shell nested inside.

CadQuery HLR (hidden-line removal) with hidden edges DASHED.

projectionDir (-1, 0, 0) places the camera on the +X axis looking
toward -X — i.e. looking AT the +X (right) side face. The side face
fills the image; the cold core sits INSIDE the appliance and reads
entirely through dashed hidden lines, showing the foam shell's
position in depth (Z) and height (Y).

Run from the repo root:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/drawings/engineering-drawings/enclosure-assembly-side.py
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import cadquery as cq

import _enclosure_assembly_model as model


def main() -> None:
    assembly = model.build_enclosure_assembly()
    output_path = _HERE / "enclosure-assembly-side.svg"
    cq.exporters.export(
        assembly,
        str(output_path),
        opt={
            "projectionDir": (-1, 0, 0),  # camera on +X looking -X
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
