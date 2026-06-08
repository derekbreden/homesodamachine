"""Isometric engineering drawing of the Kitchen Edition enclosure assembly:
HLR (hidden-line removal) with hidden edges dashed.

The assembly is +Z-up natively. Rotating -90 about +X lands the height axis
on +Y, the direction OCCT's HLR projector reads as image-up.

In the rotated frame, projectionDir (1, 1, 1) matches the 3D STEP viewer's
default front-iso camera: lid up, contents reading through the translucent
shell.
"""

from pathlib import Path

import cadquery as cq

_HERE = Path(__file__).resolve().parent
_repo = next(p for p in _HERE.parents if (p / "hardware" / "_cadq_export.py").is_file())
ASSEMBLY_STEP = _repo / "hardware" / "enclosure-assembly" / "enclosure-assembly.step"


def main() -> None:
    shape = cq.importers.importStep(str(ASSEMBLY_STEP))
    drawing = shape.rotate((0, 0, 0), (1, 0, 0), -90)
    output_path = _HERE / "enclosure-assembly-iso.svg"
    cq.exporters.export(
        drawing,
        str(output_path),
        opt={
            "projectionDir": (1, 1, 1),
            "width": None,
            "height": 800,
            "marginLeft": 30,
            "marginTop": 30,
            "strokeWidth": 1.5,
            "showAxes": False,
        },
    )
    print(f"-> {output_path.name}")


if __name__ == "__main__":
    main()
