"""OCCT's splines for the cases `spline.rs` fits, written to `spline_reference.json` beside this
file: each case's points and end tangents, the curve `Edge.makeSpline` fits through them, sampled
at parameters across its range (the point and the unit tangent at each), and a circle swept along
a path holding one of them, by its volume, area and points sampled on its side faces. Plain
CadQuery: it imports no generator.

    tools/run --cad -- tools/cad-venv/bin/python tools/hsm/kernel/tests/spline_reference.py
"""

import json
import math
from pathlib import Path

import cadquery as cq
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepTools import BRepTools
from OCP.GeomAbs import GeomAbs_Plane
from OCP.gp import gp_Pnt, gp_Vec

HERE = Path(__file__).resolve().parent


def xyz(p):
    return [p.X(), p.Y(), p.Z()]


def ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * u * (10 + u * (-15 + 6 * u))


def eased(z):
    """A quintic run across 27.5 mm of rise, as the faucet's lower tube transitions are."""
    u = ease((z - 40.0) / 27.5)
    return (5.45 - 3.2 * u + 0.4 * u * (1 - u), 10.05 - 2.4 * u, z)


def bent(s):
    """A bend of radius 66 whose offset eases out across it, as the faucet's converging runs are."""
    a = math.radians(70.0) + s / 66.0
    u = ease(s / 24.0)
    r = 66.0 + 4.0 + 1.2 * u
    return (2.0 - 1.6 * u, -57.0 + r * math.cos(a), 120.0 + r * math.sin(a))


def sampled(fn, a, b):
    count = max(16, math.ceil((b - a) / 0.4))
    return [fn(a + (b - a) * i / count) for i in range(count + 1)]


CASES = {
    "eased": {"points": sampled(eased, 40.0, 67.5)},
    "bent": {"points": sampled(bent, 0.0, 24.0)},
    "four": {"points": [(0.0, 0.0, 0.0), (3.0, 1.0, 0.5), (4.0, 5.0, 1.0), (9.0, 6.0, -2.0)]},
    "three": {"points": [(0.0, 0.0, 0.0), (2.0, 3.0, 1.0), (6.0, 4.0, 0.0)]},
    "two": {"points": [(1.0, 2.0, 3.0), (4.0, -2.0, 8.0)]},
    "hermite": {"points": [(6.6, 21.5, -37.5), (0.0, 26.0, -76.0)], "tangents": [(0, 0, -1), (0, 0, -1)]},
}


def curve(case):
    points = [cq.Vector(*p) for p in case["points"]]
    tangents = case.get("tangents")
    if tangents:
        return cq.Edge.makeSpline(points, tangents=[cq.Vector(*t) for t in tangents])
    return cq.Edge.makeSpline(points, tol=1e-7)


def samples(edge, n=97):
    c = BRep_Tool.Curve_s(edge.wrapped, 0.0, 0.0)
    t0, t1 = c.FirstParameter(), c.LastParameter()
    out = []
    for i in range(n):
        t = t0 + (t1 - t0) * i / (n - 1)
        p, d = gp_Pnt(), gp_Vec()
        c.D1(t, p, d)
        out.append({"t": t, "p": xyz(p), "d": xyz(d.Normalized())})
    return {"range": [t0, t1], "samples": out}


def face_samples(solid, n=9):
    pts = []
    for f in solid.Faces():
        s = BRepAdaptor_Surface(f.wrapped)
        if s.GetType() == GeomAbs_Plane:
            continue
        u0, u1, v0, v1 = BRepTools.UVBounds_s(f.wrapped)
        for i in range(n):
            for j in range(n):
                pts.append(xyz(s.Value(u0 + (u1 - u0) * i / (n - 1), v0 + (v1 - v0) * j / (n - 1))))
    return pts


def swept():
    """A Ø4 tube up 40 mm, through `eased` and on up 22.5 mm, as `faucet_paths.path_wire` lays it."""
    pts = [cq.Vector(*eased(z)) for z in [p[2] for p in CASES["eased"]["points"]]]
    start, end = pts[0], pts[-1]
    path = cq.Wire.assembleEdges([
        cq.Edge.makeLine(cq.Vector(start.x, start.y, 0.0), start),
        cq.Edge.makeSpline(pts, tol=1e-7),
        cq.Edge.makeLine(end, cq.Vector(end.x, end.y, 90.0)),
    ])
    profile = cq.Workplane("XY").center(start.x, start.y).circle(2.0)
    tube = profile.sweep(cq.Workplane(obj=path), transition="round").val()
    bb = tube.BoundingBox()
    return {
        "volume": tube.Volume(),
        "area": tube.Area(),
        "bbox": [bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax],
        "samples": face_samples(tube),
    }


def main():
    out = {}
    for name, case in CASES.items():
        out[name] = {"points": [list(p) for p in case["points"]], **samples(curve(case))}
        if "tangents" in case:
            out[name]["tangents"] = [list(t) for t in case["tangents"]]
        print(f"{name:8} {len(case['points']):3} points  range {out[name]['range'][1]:.6f}")
    out["swept"] = swept()
    print(f"swept    volume {out['swept']['volume']:.6f}")
    path = HERE / "spline_reference.json"
    path.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
