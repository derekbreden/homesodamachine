"""Python compatibility for Rust faucet dimensions and numeric centrelines.

The scalar construction and path sampling live in `tools/hsm/faucet-data`.
CadQuery edge/wire adapters remain available to manual native readers.
"""

import sys
from pathlib import Path

_HARDWARE = next(p for p in Path(__file__).resolve().parents if p.name == "hardware")
sys.path.insert(0, str(_HARDWARE / "scripts"))
from _rust_data import request


def _call(op, *args, **kwargs):
    return request("faucet-data", "faucet-data", {"op": op, "args": args, "kwargs": kwargs})


globals().update(_call("constants"))


def ease(t):
    return _call("ease", t)


def lower_positions(z):
    return tuple(_call("lower_positions", z))


def lower_bundle_x(z):
    return _call("lower_bundle_x", z)


def lower_ribbon_y(z):
    return _call("lower_ribbon_y", z)


def lower_point(z, kind, sign=1):
    return tuple(_call("lower_point", z, kind, sign))


def positions(s):
    return tuple(_call("positions", s))


def arc_point(angle, x=0.0, n=0.0):
    return tuple(_call("arc_point", angle, x, n))


def station_point(s, x=0.0, n=0.0):
    return tuple(_call("station_point", s, x, n))


def station_plane(s, *, center_n=0.0):
    return tuple(tuple(row) for row in _call("station_plane", s, center_n=center_n))


def tube_arc_point(s, kind, sign=1):
    return tuple(_call("tube_arc_point", s, kind, sign))


def port_half_width(s):
    return _call("port_half_width", s)


def path_legs(kind, bottom_z=-6.2, sign=1, *, end_s=None):
    legs = _call("path_legs", kind, bottom_z, sign, end_s=end_s)
    return [(row[0], [tuple(p) for p in row[1]]) if row[0] == "spline"
            else (row[0], *(tuple(p) for p in row[1:])) for row in legs]


def leg_edge(leg):
    """One of `path_legs`' legs as a CadQuery edge, or `("hermite", a, b, ta, tb)`: the spline
    from `a` to `b` leaving along `ta` and arriving along `tb`."""
    import cadquery as cq
    if leg[0] == "line":
        return cq.Edge.makeLine(cq.Vector(*leg[1]), cq.Vector(*leg[2]))
    if leg[0] == "arc":
        return cq.Edge.makeThreePointArc(*(cq.Vector(*p) for p in leg[1:]))
    if leg[0] == "hermite":
        return cq.Edge.makeSpline([cq.Vector(*p) for p in leg[1:3]],
                                  tangents=[cq.Vector(*t) for t in leg[3:]])
    return cq.Edge.makeSpline([cq.Vector(*p) for p in leg[1]], tol=1e-7)


def path_wire(kind, bottom_z=-6.2, sign=1, *, end_s=None):
    """Circular/spline CAD path with analytic straight and constant arc runs."""
    import cadquery as cq
    return cq.Wire.assembleEdges([leg_edge(leg) for leg in path_legs(kind, bottom_z, sign, end_s=end_s)])
