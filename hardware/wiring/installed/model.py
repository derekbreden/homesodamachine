"""Typed wiring records backed by the Rust route composer."""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from ._wiring_data import read as _read

@dataclass(frozen=True)
class Terminal:
    id: str
    part: str
    point: tuple[float, float, float]
    outward: tuple[float, float, float]
    kind: str
    basis: str
    status: str = "modeled"
    pin: str = ""

@dataclass(frozen=True)
class Connection:
    id: str
    harness: str
    net: str
    start: str
    end: str
    stock: str = "ribbon22"
    schedule: str = ""
    service: str = "fixed"
    note: str = ""

@dataclass
class Route:
    connection: Connection
    points: list[tuple[float, float, float]]
    segments: list[dict] = field(default_factory=list)
    length_mm: float = 0.0
    minimum_bend_mm: float | None = None
    status: str = "selected_layout"
    note: str = ""

    def record(self):
        return _read("route_record", asdict(self))


def route_from_data(data):
    data = dict(data)
    data["connection"] = Connection(**data["connection"])
    data["points"] = [tuple(point) for point in data["points"]]
    return Route(**data)


STOCK = _read("stock")


def add(a, b): return tuple(_read("add", {"a": a, "b": b}))
def sub(a, b): return tuple(_read("sub", {"a": a, "b": b}))
def mul(a, t): return tuple(_read("mul", {"a": a, "t": t}))
def dot(a, b): return _read("dot", {"a": a, "b": b})
def norm(a): return _read("norm", {"a": a})
def unit(a): return tuple(_read("unit", {"a": a}))


def rounded_segments(points, radius=4.0, *, keep_collinear=False, endpoint_tangent_fraction=.44):
    return _read("round_segments", {"points": points, "radius": radius,
                                    "keep_collinear": keep_collinear,
                                    "endpoint_tangent_fraction": endpoint_tangent_fraction})


def spline_segment(points, tangents, *, chord_length=False):
    return _read("spline_segment", {"points": points, "tangents": tangents, "chord_length": chord_length})


def sampled_segments(segments, step=1.):
    return [tuple(point) for point in _read("sampled_segments", {"segments": segments, "step": step})]


def finish(connection, points, note="", radius=None, *, endpoint_tangent_fraction=.44):
    return route_from_data(_read("finish", {"connection": connection, "points": points,
                                           "note": note, "radius": radius,
                                           "endpoint_tangent_fraction": endpoint_tangent_fraction}))


def segment_edge(segment):
    """Reconstruct one recorded native centreline edge."""
    import cadquery as cq
    a,b=(cq.Vector(*segment[k])for k in ('start_mm','end_mm'))
    if segment['kind']=='line':return cq.Edge.makeLine(a,b)
    if segment['kind']=='arc':return cq.Edge.makeThreePointArc(a,cq.Vector(*segment['midpoint_mm']),b)
    if segment['kind']=='spline':
        return cq.Edge.makeSpline([cq.Vector(*p)for p in segment['interpolation_points_mm']],
                                  tangents=[cq.Vector(*p)for p in segment['endpoint_derivatives']],
                                  parameters=segment['parameters'],scale=False)
    raise ValueError(('Unknown wire segment',segment['kind']))

def shape(route, diameter, inner_diameter=None):
    import cadquery as cq
    edges=[segment_edge(s)for s in route.segments]
    path = cq.Wire.assembleEdges(edges)
    start = cq.Vector(*route.segments[0]["start_mm"])
    tangent = edges[0].tangentAt(0)
    profile = cq.Wire.makeCircle(diameter/2, start, tangent)
    holes = [] if inner_diameter is None else [cq.Wire.makeCircle(inner_diameter/2, start, tangent)]
    body=cq.Solid.sweep(profile, holes, path, makeSolid=True, isFrenet=False)
    return body.fix() if any(s['kind']=='spline'for s in route.segments) else body
