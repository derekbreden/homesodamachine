"""OCCT's lofts for the cases `thru.rs` builds, written to `thru_reference.json` beside this
file: each case's sections as OCCT walks them (every edge's curve, in wire order), and the loft's
volume, area, bounds and points sampled on each of its side faces. Plain CadQuery: it imports no
generator and takes no CAD lock.

    tools/cad-venv/bin/python tools/hsm/kernel/tests/thru_reference.py
"""

import json
import math
from pathlib import Path

import cadquery as cq
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepTools import BRepTools, BRepTools_WireExplorer
from OCP.GeomAbs import GeomAbs_Circle, GeomAbs_Ellipse, GeomAbs_Line, GeomAbs_Plane
from OCP.GeomAdaptor import GeomAdaptor_Curve
from OCP.TopAbs import TopAbs_REVERSED

HERE = Path(__file__).resolve().parent


def xyz(p):
    return [p.X(), p.Y(), p.Z()]


def edge_record(edge):
    """The edge as `LoftEdge` takes it: walked the way the wire walks it."""
    curve = BRep_Tool.Curve_s(edge, 0.0, 0.0)
    first, last = cq.Edge(edge)._bounds()
    a = GeomAdaptor_Curve(curve)
    reversed_ = edge.Orientation() == TopAbs_REVERSED
    kind = a.GetType()
    if kind == GeomAbs_Line:
        p, q = xyz(curve.Value(first)), xyz(curve.Value(last))
        if reversed_:
            p, q = q, p
        return {"line": [p, q]}
    if kind in (GeomAbs_Circle, GeomAbs_Ellipse):
        if kind == GeomAbs_Circle:
            c = a.Circle()
            pos, rx, ry = c.Position(), c.Radius(), c.Radius()
        else:
            e = a.Ellipse()
            pos, rx, ry = e.Position(), e.MajorRadius(), e.MinorRadius()
        x = [v * rx for v in xyz(pos.XDirection())]
        y = [v * ry for v in xyz(pos.YDirection())]
        t0, t1 = (last, first) if reversed_ else (first, last)
        return {"conic": {"c": xyz(pos.Location()), "x": x, "y": y, "t0": t0, "t1": t1}}
    raise ValueError(f"an edge of curve type {kind}")


def section_record(wire):
    out = []
    ex = BRepTools_WireExplorer(wire.wrapped)
    while ex.More():
        out.append(edge_record(ex.Current()))
        ex.Next()
    return out


def face_samples(solid, n=7):
    """Points on every side face of the loft, an n × n grid over each face's parameters."""
    pts = []
    for f in solid.Faces():
        s = BRepAdaptor_Surface(f.wrapped)
        if s.GetType() == GeomAbs_Plane:
            continue
        u0, u1, v0, v1 = BRepTools.UVBounds_s(f.wrapped)
        for i in range(n):
            for j in range(n):
                u = u0 + (u1 - u0) * i / (n - 1)
                v = v0 + (v1 - v0) * j / (n - 1)
                pts.append(xyz(s.Value(u, v)))
    return pts


def ellipse(cx, cy, z, w, d):
    return cq.Workplane("XY", origin=(0, 0, z)).center(cx, cy).ellipse(w / 2, d / 2).val()


def circle(cx, cy, z, r):
    return cq.Workplane("XY", origin=(0, 0, z)).center(cx, cy).circle(r).val()


def rounded(cx, cy, z, w, d, r):
    sk = cq.Sketch().rect(w, d).vertices().fillet(r)
    return sk._faces.Faces()[0].outerWire().translate(cq.Vector(cx, cy, z))


def rect(cx, cy, z, w, d):
    return cq.Workplane("XY", origin=(0, 0, z)).center(cx, cy).rect(w, d).val()


def slot(cx, cy, z, length, d):
    return cq.Workplane("XY", origin=(0, 0, z)).center(cx, cy).slot2D(length, d).val()


def tilted_circle(angle_deg, radius_path, r, w=None):
    """A circle on the plane normal to an arc of radius `radius_path` about the Y axis."""
    a = math.radians(angle_deg)
    centre = cq.Vector(radius_path * (1 - math.cos(a)), 0, radius_path * math.sin(a))
    normal = cq.Vector(math.sin(a), 0, math.cos(a))
    plane = cq.Plane(origin=centre, xDir=cq.Vector(math.cos(a), 0, -math.sin(a)), normal=normal)
    wp = cq.Workplane(plane)
    return (wp.ellipse(w / 2, r) if w else wp.circle(r)).val()


CASES = {
    "ellipses3": (
        [ellipse(0, 0, 0, 30, 20), ellipse(1.5, -1, 9, 24, 21), ellipse(0.5, 2, 21, 18, 12)],
        False,
    ),
    "shell_like": (
        [
            ellipse(0, 0, 0, 58, 59),
            ellipse(0, 0, 8.5, 58, 59),
            ellipse(0, 4.25, 20, 48, 53.5),
            ellipse(0, 5.25, 34, 44, 52.5),
            ellipse(0, 5.0, 43, 38, 50),
            ellipse(0, 11.5, 59, 30, 31),
            circle(0, 8.9, 65, 13.5),
        ],
        False,
    ),
    "rounded3": (
        [rounded(0, 0, 0, 40, 24, 3), rounded(0.5, 0.5, 6, 36, 22, 4), rounded(1, 1, 14, 30, 18, 2.5)],
        False,
    ),
    "ellipses12": (
        [
            ellipse(0.3 * math.sin(k), 0.2 * k, 1.5 * k, 20 - 0.6 * k + 0.4 * math.sin(k), 14 + 0.3 * k)
            for k in range(12)
        ],
        False,
    ),
    "rect_slot_ruled": ([rect(0, 0, 0, 30, 10), slot(0, 0, 12, 28, 8)], True),
    "counts_differ": (
        [rect(0, 0, 0, 20, 20), circle(0, 0, 10, 9), rect(0, 0, 20, 16, 16)],
        False,
    ),
    "tilted": (
        [tilted_circle(a, 40.0, 6.0, w) for a, w in [(0, None), (12, 14.0), (24, 16.0), (36, None)]],
        False,
    ),
}


def main():
    out = {}
    for name, (wires, ruled) in CASES.items():
        loft = cq.Solid.makeLoft(wires, ruled)
        bb = loft.BoundingBox()
        out[name] = {
            "ruled": ruled,
            "sections": [section_record(w) for w in wires],
            "volume": loft.Volume(),
            "area": loft.Area(),
            "bbox": [bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax],
            "samples": face_samples(loft),
        }
        print(f"{name:16} {len(loft.Faces()):3} faces  volume {loft.Volume():.6f}")
    path = HERE / "thru_reference.json"
    path.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
