"""Export the appliance + red ring as a glb assembly with per-part colors.

The assembly is the smoke-test input for the three.js line-art renderer
(scene.html). Each part is a separate mesh in the glb with its own
material color, so the renderer can color each independently.

Run:
    tools/cad-venv/bin/python tools/render/iso-line-art/export_pieces.py
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[2]
sys.path.insert(0, str(_REPO_ROOT / "hardware" / "printed-parts" / "enclosure" / "drawings" / "line-art"))

import cadquery as cq

import _appliance_model as model


def main() -> None:
    appliance = model.build_appliance()
    ring = model.build_red_ring()

    assy = cq.Assembly(name="iso_line_art")
    assy.add(appliance, name="appliance", color=cq.Color(1.0, 1.0, 1.0))
    assy.add(ring, name="ring", color=cq.Color(0.85, 0.10, 0.10))

    out_path = _HERE / "appliance.glb"
    assy.save(str(out_path), exportType="GLB")
    print(f"-> {out_path.relative_to(_REPO_ROOT)}")


if __name__ == "__main__":
    main()
