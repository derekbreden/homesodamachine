"""Front engineering drawing of the appliance enclosure with the
cold-core foam shell nested inside.

CadQuery HLR (hidden-line removal) with hidden edges DASHED.

projectionDir (0, 0, -1) places the camera on the +Z axis looking
toward -Z — i.e. looking AT the front face. The front face fills the
image; the cold core sits BEHIND the front face (toward the back of
the appliance) and reads entirely through dashed hidden lines.

Run from the repo root:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/drawings/engineering-drawings/enclosure-assembly-front.py
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import cadquery as cq

import _enclosure_assembly_model as model


def main() -> None:
    assembly = model.build_enclosure_assembly()
    output_path = _HERE / "enclosure-assembly-front.svg"
    cq.exporters.export(
        assembly,
        str(output_path),
        opt={
            "projectionDir": (0, 0, -1),  # camera on +Z looking -Z
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
