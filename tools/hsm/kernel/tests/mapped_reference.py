"""A block with a hole down through it and a boss across its top, sheared as the Industrial display
cover's wings are leaned (x moves with z), by CadQuery's `transformGeometry`, and written to
`mapped_reference.json` beside this file: the shear, the sheared solid's volume, area and bounds,
and points sampled across every one of its faces. Plain CadQuery: it imports no generator.

    tools/run --cad -- tools/cad-venv/bin/python tools/hsm/kernel/tests/mapped_reference.py
"""

import json
from pathlib import Path

import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepClass import BRepClass_FaceClassifier
from OCP.BRepTools import BRepTools
from OCP.TopAbs import TopAbs_OUT
from OCP.gp import gp_Pnt2d

HERE = Path(__file__).resolve().parent
LEAN, PIVOT = 0.3, 4.0


def block():
    body = cq.Solid.makeBox(20.0, 12.0, 8.0, cq.Vector(-10.0, -6.0, 0.0))
    hole = cq.Solid.makeCylinder(3.0, 10.0, cq.Vector(4.0, 0.0, -1.0))
    boss = cq.Solid.makeCylinder(2.5, 12.0, cq.Vector(-4.0, -6.0, 8.0), cq.Vector(0.0, 1.0, 0.0))
    return body.cut(hole).fuse(boss).clean()


def face_samples(solid, n=7):
    pts = []
    for f in solid.Faces():
        s = BRepAdaptor_Surface(f.wrapped)
        u0, u1, v0, v1 = BRepTools.UVBounds_s(f.wrapped)
        for i in range(n):
            for j in range(n):
                u, v = u0 + (u1 - u0) * i / (n - 1), v0 + (v1 - v0) * j / (n - 1)
                if BRepClass_FaceClassifier(f.wrapped, gp_Pnt2d(u, v), 1e-7).State() != TopAbs_OUT:
                    p = s.Value(u, v)
                    pts.append([p.X(), p.Y(), p.Z()])
    return pts


def main():
    shear = [[1.0, 0.0, LEAN, -LEAN * PIVOT], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]]
    sheared = block().transformGeometry(cq.Matrix(shear + [[0.0, 0.0, 0.0, 1.0]]))
    bb = sheared.BoundingBox()
    out = {
        "shear": shear,
        "volume": sheared.Volume(),
        "area": sheared.Area(),
        "bbox": [bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax],
        "samples": face_samples(sheared),
    }
    path = HERE / "mapped_reference.json"
    path.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"volume {out['volume']:.6f}, {len(out['samples'])} samples; wrote {path}")


if __name__ == "__main__":
    main()
