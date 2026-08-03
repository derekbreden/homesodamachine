"""_measuring — what a harvested solid says about itself.

A part with a builder answers where its stations are by construction. A part that arrived as
a STEP and nothing else answers by being measured, and this is the measuring: the axes of its
cylindrical faces, grouped by the direction they run and the radius they turn at.

    for (axis, radius), centres in bores(shape).items():
        ...

`axis` is "x", "y" or "z" — the frame axis the cylinder's own axis lies on, for the
axis-aligned bodies the pack seats. `centres` is the set of that cylinder's positions on the
other two axes, in the part's own frame, so a collet standing off the body's centreline names
its own offset. Fittings whose collets are neither on nor off an axis do not appear.

Used by the two harvested fittings ([`tee_connector.py`](/hardware/reference/tee-connector/tee_connector.py),
[`y_divider.py`](/hardware/reference/y-divider/y_divider.py)) to hold the reaches they declare
to the solid they were read off.
"""

import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
from OCP.TopAbs import TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS

_AXES = "xyz"


def bores(shape, tol: float = 1e-6) -> dict:
    """`{(axis, radius): {(a, b), ...}}` — every axis-aligned cylindrical face in the solid.

    The centre pair is the cylinder's position on the two axes it is NOT running along, in the
    order those axes appear in `xyz`. Radii and centres are rounded to 4 decimals, which is
    finer than any reach a fitting is declared to."""
    solid = shape.val() if isinstance(shape, cq.Workplane) else shape
    out: dict = {}
    walk = TopExp_Explorer(solid.wrapped, TopAbs_FACE)
    while walk.More():
        surf = BRepAdaptor_Surface(TopoDS.Face_s(walk.Current()))
        if surf.GetType() == GeomAbs_Cylinder:
            cyl = surf.Cylinder()
            direction, at = cyl.Axis().Direction(), cyl.Location()
            comp = {a: getattr(direction, a.upper())() for a in _AXES}
            along = max(_AXES, key=lambda a: abs(comp[a]))
            if abs(abs(comp[along]) - 1.0) <= tol:
                key = (along, round(cyl.Radius(), 4))
                out.setdefault(key, set()).add(
                    tuple(round(getattr(at, a.upper())(), 4) for a in _AXES if a != along))
        walk.Next()
    return out


def collet_offsets(shape, axis: str, bore_r: float, tol: float = 1e-4) -> list:
    """The centres of every bore of radius `bore_r` running along `axis`, sorted.

    A push-to-connect fitting's tube bore is the one feature every one of its ports has, and
    its centre is where that port's line runs — so the bore radius picks the ports out of the
    body's other turned faces."""
    for (along, r), centres in bores(shape).items():
        if along == axis and abs(r - bore_r) <= tol:
            return sorted(centres)
    raise ValueError(
        f"no bore of r={bore_r:g} running along {axis} — the solid carries "
        f"{sorted({(a, r) for a, r in bores(shape)})}")
