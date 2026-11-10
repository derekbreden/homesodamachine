"""OCCT's rounds and chamfers for the cases `rounds.rs` builds, written to `round_reference.json`
beside this file: each result's volume, area and bounds, and points on its faces, the nodes of
OCCT's own mesh of each face at the kernel's rule. Plain CadQuery: it imports no generator.

    tools/run --cad -- tools/cad-venv/bin/python tools/hsm/kernel/tests/round_reference.py
"""

import json
import re
from pathlib import Path

import cadquery as cq
from OCP.BRep import BRep_Tool
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopLoc import TopLoc_Location

HERE = Path(__file__).resolve().parent
LINEAR, ANGULAR = 0.005, 0.05
NEAR = cq.selectors.NearestToPointSelector


def wall_slot_fin():
    base = cq.Workplane().box(8.3, 10, 2).translate((4.15, 0, -1))
    wall = cq.Workplane().box(6, 10, 10).translate((3, 0, 5))
    fin = cq.Workplane().box(2, 10, 10).translate((7.3, 0, 5))
    return base.union(wall).union(fin)


def thin_l():
    pts = [(-1, -1), (20, -1), (20, 0), (0, 0), (0, 20), (-1, 20)]
    return cq.Workplane("YZ").polyline(pts).close().extrude(10)


def plate_boss():
    return cq.Workplane().box(30, 30, 0.8).faces(">Z").workplane().circle(5).extrude(6)


def slant():
    return cq.Workplane("XZ").polyline([(0, 0), (20, 0), (14, 10), (0, 10)]).close().extrude(-10)


def quarter_ring():
    return (cq.Workplane("XZ").moveTo(10, 0).rect(4, 3, centered=False)
            .revolve(90, (0, 0, 0), (0, 1, 0)))


CASES = {
    "box_vertical": lambda: cq.Workplane().box(20, 20, 10).edges("|Z").fillet(3),
    "vert_then_top": lambda: cq.Workplane().box(20, 20, 10).edges("|Z").fillet(3).edges(">Z").fillet(1),
    "vert_then_top_chamfer": lambda: cq.Workplane().box(20, 20, 10).edges("|Z").fillet(3).faces(">Z").chamfer(1),
    "slot_beside_round": lambda: wall_slot_fin().edges("|Y").edges(NEAR((6, 0, 10))).fillet(4),
    "thin_l_inside": lambda: thin_l().edges("|X").edges(NEAR((5, 0, 0))).fillet(5),
    "thin_plate_boss_root": lambda: plate_boss().edges(NEAR((0, 0, 0.4))).fillet(4),
    "cylinder_top_round": lambda: cq.Workplane().circle(5).extrude(10).faces(">Z").edges().fillet(1),
    "cylinder_top_chamfer": lambda: cq.Workplane().circle(10).extrude(5).edges(">Z").chamfer(1),
    "hole_top_round": lambda: (cq.Workplane().box(20, 20, 10).faces(">Z").workplane().hole(6)
                               .faces(">Z").edges("%CIRCLE").fillet(1)),
    "top_edges_round": lambda: cq.Workplane().box(20, 20, 10).edges(">Z").fillet(2),
    "top_edges_chamfer": lambda: cq.Workplane().box(20, 20, 10).edges(">Z").chamfer(2),
    "corner_then_top": lambda: (cq.Workplane().box(20, 20, 10).edges("|Z and >X and >Y").fillet(5)
                                .edges(">Z").fillet(1)),
    "slanted_round": lambda: slant().edges("|Y").edges(">Z").edges(">X").fillet(2),
    "rotated_box": lambda: (cq.Workplane().box(20, 10, 8).rotate((0, 0, 0), (0, 0, 1), 30)
                            .edges("|Z").fillet(2)),
    "z_and_max_y": lambda: cq.Workplane().box(30, 20, 10).edges("|Z and >Y").fillet(4),
    "slot_top_round": lambda: (cq.Workplane().box(30, 20, 8).faces(">Z").workplane().slot2D(16, 6)
                               .cutBlind(-4).faces(">Z").edges("not(<X or >X or <Y or >Y)").fillet(1)),
    "quarter_ring_round": lambda: quarter_ring().edges("%CIRCLE and >Z").edges(NEAR((10, 10, 3))).fillet(1),
}


def nodes(shape):
    """The nodes of OCCT's mesh of every face at the kernel's rule: points on the exact surfaces."""
    BRepMesh_IncrementalMesh(shape.wrapped, LINEAR, False, ANGULAR, True)
    out = set()
    for f in shape.Faces():
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(f.wrapped, loc)
        if tri is None:
            continue
        trsf = loc.Transformation()
        for i in range(1, tri.NbNodes() + 1):
            p = tri.Node(i).Transformed(trsf)
            out.add((round(p.X(), 6), round(p.Y(), 6), round(p.Z(), 6)))
    pts = sorted(out)
    step = -(-len(pts) // 200)
    return [list(p) for p in pts[::step]]


def main():
    out = {}
    for name, build in CASES.items():
        s = build().val()
        bb = s.BoundingBox()
        out[name] = {
            "volume": s.Volume(),
            "area": s.Area(),
            "bbox": [bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax],
            "samples": nodes(s),
        }
        print(f"{name:22} {len(s.Faces()):3} faces  volume {s.Volume():.6f}  area {s.Area():.6f}")
    path = HERE / "round_reference.json"
    text = json.dumps(out, indent=1, sort_keys=True)
    text = re.sub(r"\[\s+([-0-9.e]+),\s+([-0-9.e]+),\s+([-0-9.e]+)\s+\]", r"[\1, \2, \3]", text)
    path.write_text(text + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
