"""
Build the appliance line-art scene as a glTF assembly.

The line-art drawings are split into two pipelines:
  - SVG line-art (drawings/line-art/) — monochrome HLR via cq.exporters,
    used for views that don't need color or per-part occlusion control.
  - Scene line-art (this directory) — multi-part glTF rendered by the
    /scene viewer in three.js, used for views that need colored markings
    occluded by surrounding 3D geometry (e.g. the red ring around the
    CO2 port, hidden where the coupling body sits in front of it).

This module builds the second pipeline's input. Each part of the scene
is a separate Workplane added to a cq.Assembly with its own color; the
glTF export tessellates each part as its own mesh. The three.js scene
viewer then loads the glTF and renders with z-buffer occlusion, so
front parts naturally hide what's behind them.

Run from the repo root:

    tools/cad-venv/bin/python hardware/printed-parts/enclosure/scene/build_scene.py
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
# Pull build_appliance + dimension constants from the line-art module.
sys.path.insert(0, str(_HERE.parent / "drawings" / "line-art"))

import cadquery as cq

import _appliance_model as model


# Ring sits on the wall's outer face. Extruded outward in +x by RING_THICKNESS
# so it has a distinct depth from the wall surface (prevents z-fighting in
# the GL renderer) and reads as a printed/decal layer.
RING_THICKNESS = 0.3


def _build_co2_red_ring() -> cq.Workplane:
    """Annular plate on the right side wall (x=W) around the CO2 port.

    Inner / outer radius come from the ring annulus definition in
    _appliance_model: CO2_PORT_RING_INNER_R and CO2_PORT_RING_OUTER_R.
    """
    inner_r = model.CO2_PORT_RING_INNER_R
    outer_r = model.CO2_PORT_RING_OUTER_R
    world_y, world_z = model.CO2_PORT_WALL_AT
    return (
        cq.Workplane(cq.Plane(
            origin=(model.W, world_y, world_z),
            xDir=(0, 1, 0),
            normal=(1, 0, 0),
        ))
        .circle(outer_r)
        .circle(inner_r)
        .extrude(RING_THICKNESS)
    )


def build_scene_assembly() -> cq.Assembly:
    """Assemble all scene parts with their colors."""
    appliance = model.build_appliance()
    co2_red_ring = _build_co2_red_ring()

    asm = cq.Assembly()
    asm.add(appliance, name="appliance", color=cq.Color("white"))
    asm.add(co2_red_ring, name="co2_red_ring", color=cq.Color("red"))
    return asm


def main() -> None:
    output_path = _HERE / "scene.glb"
    asm = build_scene_assembly()
    # Binary glTF (.glb) — single file, smaller than ASCII glTF + .bin.
    # Tolerances control mesh tessellation; defaults of 0.1 mm linear and
    # 0.1 rad angular keep file sizes small while staying tight enough
    # for an appliance-scale model where smallest features (button
    # protrusions, knob bevels) are ≥ 1 mm.
    asm.export(str(output_path), tolerance=0.1, angularTolerance=0.1)
    print(f"Wrote {output_path} ({output_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
