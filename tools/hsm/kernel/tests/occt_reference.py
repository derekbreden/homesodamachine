"""OCCT's volume, area and bounds for every case the kernel's tests build, written to
`occt_reference.json` beside this file. Plain CadQuery, but for one generator: the fuse clamp's
module, whose `build()` is recorded under `fuse_clamp_module` as the B-rep the part the kernel
cuts from its numbers is held to. Importing it takes the CAD lock.

    tools/cad-venv/bin/python tools/hsm/kernel/tests/occt_reference.py
"""

import json
import math
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def props(shape):
    s = shape.val() if isinstance(shape, cq.Workplane) else shape
    bb = s.BoundingBox()
    return {
        "volume": s.Volume(),
        "area": s.Area(),
        "bbox": [bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax],
    }


def holes_60():
    block = cq.Solid.makeBox(100, 60, 10)
    pins = [cq.Solid.makeCylinder(2.5, 12, cq.Vector(5 + 10 * i, 5 + 10 * j, -1))
            for i in range(10) for j in range(6)]
    return block.cut(*pins)


def sweep_bend():
    path = cq.Wire.assembleEdges([
        cq.Edge.makeLine(cq.Vector(0, 0, 0), cq.Vector(0, 0, 20)),
        cq.Edge.makeThreePointArc(cq.Vector(0, 0, 20),
                                  cq.Vector(10 - 10 * math.cos(math.pi / 4), 0, 20 + 10 * math.sin(math.pi / 4)),
                                  cq.Vector(10, 0, 30)),
    ])
    return cq.Workplane("XY").circle(2).sweep(cq.Workplane().add(path))


def sweep_tube():
    path = cq.Wire.assembleEdges([
        cq.Edge.makeLine(cq.Vector(0, 0, 0), cq.Vector(0, 0, 20)),
        cq.Edge.makeThreePointArc(cq.Vector(0, 0, 20),
                                  cq.Vector(10 - 10 * math.cos(math.pi / 4), 0, 20 + 10 * math.sin(math.pi / 4)),
                                  cq.Vector(10, 0, 30)),
        cq.Edge.makeLine(cq.Vector(10, 0, 30), cq.Vector(25, 0, 30)),
    ])
    return cq.Workplane("XY").circle(3).circle(2).sweep(cq.Workplane().add(path))


CASES = {
    "box": lambda: cq.Solid.makeBox(10, 20, 30),
    "cylinder": lambda: cq.Solid.makeCylinder(5, 12),
    "cylinder_tilted": lambda: cq.Solid.makeCylinder(3.2, 7, cq.Vector(1, 2, 3), cq.Vector(1, 1, 0.5)),
    "cylinder_sector": lambda: cq.Solid.makeCylinder(5, 10, angleDegrees=120),
    "cone": lambda: cq.Solid.makeCone(6, 2, 9),
    "cone_point": lambda: cq.Solid.makeCone(4, 0, 5),
    "sphere": lambda: cq.Workplane().sphere(7),
    "torus": lambda: cq.Solid.makeTorus(10, 3),
    "wedge": lambda: cq.Solid.makeWedge(10, 8, 6, 2, 1, 7, 4),
    "extrude_holed": lambda: cq.Workplane("XY").rect(20, 10).circle(3).extrude(5),
    "extrude_slot": lambda: cq.Workplane("XY").slot2D(30, 8, 20).extrude(4),
    "extrude_rounded": lambda: cq.Workplane("XY").rect(20, 12).extrude(3).edges("|Z").fillet(3),
    "extrude_offset": lambda: cq.Workplane("XY").rect(20, 12).offset2D(2).extrude(3),
    "extrude_yz": lambda: cq.Workplane("YZ", origin=(-2, 0, 0))
        .polyline([(0, 0), (6, 0), (6, 3), (2, 5), (0, 5)]).close().extrude(4),
    "revolve_partial": lambda: cq.Workplane("XZ").polyline([(5, 0), (9, 0), (9, 6), (5, 6)]).close()
        .revolve(270, (0, 0, 0), (0, 1, 0)),
    "revolve_arc": lambda: cq.Workplane("XZ").moveTo(3, 0).lineTo(8, 0).threePointArc((10, 2), (8, 4))
        .lineTo(3, 4).close().revolve(360, (0, 0, 0), (0, 1, 0)),
    "drafted_rect": lambda: cq.Workplane("XY").rect(20, 10).extrude(8, taper=5),
    "drafted_circle": lambda: cq.Workplane("XY").circle(6).extrude(5, taper=10),
    "union_boxes": lambda: cq.Workplane().box(10, 10, 10).union(cq.Workplane().box(10, 10, 10).translate((5, 5, 5))),
    "cut_bore": lambda: cq.Workplane().box(20, 20, 10).cut(cq.Workplane().cylinder(12, 4)),
    "intersect_ball": lambda: cq.Workplane().box(10, 10, 10).intersect(cq.Workplane().sphere(6.5)),
    "holes_60": holes_60,
    "split_top": lambda: cq.Workplane().box(10, 10, 10, centered=False).faces(">Z").workplane(-7)
        .split(keepTop=True),
    "split_bottom": lambda: cq.Workplane().box(10, 10, 10, centered=False).faces(">Z").workplane(-7)
        .split(keepBottom=True),
    "sweep_bend": sweep_bend,
    "sweep_tube": sweep_tube,
    "loft_rects": lambda: cq.Workplane("XY").rect(10, 10).workplane(offset=8).rect(6, 6).loft(ruled=True),
    "loft_circles": lambda: cq.Workplane("XY").circle(5).workplane(offset=10).circle(3).loft(ruled=True),
    "text": lambda: cq.Workplane("XY").text("HSM", 10, 2),
    "text_left": lambda: cq.Workplane("XY").text("go", 8, 1.5, halign="left", valign="bottom"),
    "text_right_top": lambda: cq.Workplane("XY").text("HSM", 6, 1, halign="right", valign="top"),
    "text_arial_bold": lambda: cq.Workplane("XY").text("AV Ta", 4, 0.6, font="Arial", kind="bold"),
    "text_helvetica_bold": lambda: cq.Workplane("XY").text("Ab8", 5.0, 0.48, font="Helvetica", kind="bold"),
}


def fuse_clamp_module():
    """The fuse clamp's own `build()`, the body `enclosure_assembly` seats."""
    sys.path.insert(0, str(ROOT / "hardware/printed-parts/refrigeration/fuse-clamp"))
    import fuse_clamp as module
    return module.build()


def main():
    out = {name: props(make()) for name, make in CASES.items()}
    out["fuse_clamp_module"] = props(fuse_clamp_module())
    path = HERE / "occt_reference.json"
    path.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"-> {path.name}: {len(out)} cases")


if __name__ == "__main__":
    main()
