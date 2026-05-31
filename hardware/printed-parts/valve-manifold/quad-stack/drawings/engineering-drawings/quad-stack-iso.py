"""Isometric engineering drawing of the quad-stack assembly.

CadQuery HLR projection (visible edges solid, hidden edges dashed gray) of
`../../quad-stack-assembly.step`. Run from the repo root:

    tools/cad-venv/bin/python \
      hardware/printed-parts/valve-manifold/quad-stack/drawings/engineering-drawings/quad-stack-iso.py
"""

from pathlib import Path

import cadquery as cq

_HERE = Path(__file__).resolve().parent
# .../quad-stack/drawings/engineering-drawings/  ->  .../quad-stack/<step>
_STEP = _HERE.parents[1] / "quad-stack-assembly.step"


def main():
    model = cq.importers.importStep(str(_STEP))
    # Rotate -90 about +X so +Z (height) lands on image-up (+Y); project
    # front-iso with (1,1,1).
    drawing = model.rotate((0, 0, 0), (1, 0, 0), -90)
    out = _HERE / "quad-stack-iso.svg"
    cq.exporters.export(
        drawing,
        str(out),
        opt={
            "projectionDir": (1, 1, 1),
            "width": None,
            "height": 900,
            "marginLeft": 30,
            "marginTop": 30,
            "strokeWidth": 1.5,
            "showAxes": False,
        },
    )
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
