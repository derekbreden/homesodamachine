"""CadQuery's hulls for the sets `sketch_hull.rs` wraps, written to `sketch_hull_reference.json`
beside this file: each set's circles and points and the hull's edges as OCCT walks the outer wire
of `Sketch.hull()`, lines by their ends and arcs by centre, radius and parameters. Plain
CadQuery: it imports no generator and takes no CAD lock.

    tools/cad-venv/bin/python tools/hsm/kernel/tests/sketch_hull_reference.py
"""

import json
import math
import random
from pathlib import Path

import cadquery as cq
from OCP.BRep import BRep_Tool
from OCP.BRepTools import BRepTools_WireExplorer
from OCP.GeomAbs import GeomAbs_Circle, GeomAbs_Line
from OCP.GeomAdaptor import GeomAdaptor_Curve
from OCP.TopAbs import TopAbs_REVERSED

HERE = Path(__file__).resolve().parent


def edges(wire):
    out = []
    ex = BRepTools_WireExplorer(wire.wrapped)
    while ex.More():
        edge = ex.Current()
        curve = BRep_Tool.Curve_s(edge, 0.0, 0.0)
        first, last = cq.Edge(edge)._bounds()
        a = GeomAdaptor_Curve(curve)
        assert edge.Orientation() != TopAbs_REVERSED
        if a.GetType() == GeomAbs_Line:
            p, q = curve.Value(first), curve.Value(last)
            out.append({"line": [[p.X(), p.Y()], [q.X(), q.Y()]]})
        else:
            assert a.GetType() == GeomAbs_Circle
            c = a.Circle()
            assert c.Axis().Direction().Z() > 0 and c.XAxis().Direction().X() > 0.999999999
            out.append({"arc": {"c": [c.Location().X(), c.Location().Y()], "r": c.Radius(),
                                "t0": first, "t1": last}})
        ex.Next()
    return out


def hull(circles, points):
    sk = cq.Sketch()
    for (x, y), r in circles:
        sk = sk.arc((x, y), r, 0.0, 360.0)
    for i in range(len(points)):
        a, b = points[i], points[(i + 1) % len(points)]
        if len(points) > 1:
            sk = sk.segment(a, b)
    return edges(sk.hull().clean()._faces.Faces()[0].outerWire())


def sets():
    soda = 5.1125
    yield "shell_inner", [((0, 0), soda), ((-2.7811, 5.5795), 1.25), ((2.7811, 5.5795), 1.25),
                          ((-1.6, 9.75), 0.9), ((1.6, 9.75), 0.9)], []
    yield "lower_lane", [((0, 8.875), soda), ((-5.45, 18.925), 1.25), ((5.45, 18.925), 1.25),
                         ((0, 18.525), 1.25), ((-1.6, 21.4875), 0.9), ((1.6, 21.4875), 0.9)], []
    yield "two_equal", [((0, 0), 2.0), ((5, 1), 2.0)], []
    yield "with_points", [((0, 0), 2.0), ((6, 0.5), 1.0)], [(3, 5), (-4, 3), (2, -4)]
    # CadQuery's march needs every circle clear of every other's inside.
    rng = random.Random(7)
    k = 0
    while k < 24:
        circles = []
        for _ in range(rng.randint(2, 7)):
            circles.append(((rng.uniform(-10, 10), rng.uniform(-10, 10)), rng.uniform(0.3, 6.0)))
        if all(math.dist(a, b) > abs(ra - rb) + 1e-3
               for i, (a, ra) in enumerate(circles) for b, rb in circles[i + 1:]):
            yield f"random{k}", circles, []
            k += 1


def main():
    out = {}
    for name, circles, points in sets():
        out[name] = {"circles": [[x, y, r] for (x, y), r in circles],
                     "points": [list(p) for p in points], "edges": hull(circles, points)}
        print(f"{name:12} {len(out[name]['edges'])} edges")
    path = HERE / "sketch_hull_reference.json"
    path.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
