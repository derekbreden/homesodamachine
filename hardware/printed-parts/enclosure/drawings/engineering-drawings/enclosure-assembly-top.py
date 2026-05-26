"""Top engineering drawing of the appliance enclosure with the
cold-core foam shell nested inside.

CadQuery HLR (hidden-line removal) with hidden edges DASHED.

projectionDir (0, -1, 0) places the camera on the +Y axis looking
toward -Y — i.e. looking DOWN at the top face. The top face fills the
image; the cold core sits BELOW the top face and reads through dashed
hidden lines, showing its footprint inside the appliance's plan view.

Run from the repo root:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/drawings/engineering-drawings/enclosure-assembly-top.py
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import cadquery as cq

import _enclosure_assembly_model as model


def main() -> None:
    assembly = model.build_enclosure_assembly()
    output_path = _HERE / "enclosure-assembly-top.svg"
    cq.exporters.export(
        assembly,
        str(output_path),
        opt={
            "projectionDir": (0, -1, 0),  # camera on +Y looking -Y
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
