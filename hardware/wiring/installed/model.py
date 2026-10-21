"""Shared millimetre-based wiring records and tangent circular route construction."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import math


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
    status: str = "proposed"
    note: str = ""

    def record(self):
        return {**asdict(self.connection), "points_mm": self.points,
                "segments": self.segments, "length_mm": round(self.length_mm, 3),
                "minimum_bend_mm": self.minimum_bend_mm,
                "route_status": self.status, "routing_note": self.note}


# Insulation is included. Only ribbon22's diameter is bound to the current
# purchased-ribbon schedule; the other ODs are explicit layout allowances.
STOCK = {
    "ribbon22": {"awg": 22, "od_mm": 1.7, "color": [0.065, 0.075, 0.095],
                 "basis": "22 AWG silicone ribbon, 1.7 mm conductor section in cable-assemblies.md",
                 "construction": "stranded silicone; web retained along shared ribbon lanes"},
    "bulk22": {"awg": 22, "od_mm": 1.7, "color": [0.065, 0.075, 0.095],
               "basis": "Layout uses the ribbon conductor OD; bulk insulation OD remains unmeasured",
               "construction": "stranded silicone"},
    "power16": {"awg": 16, "od_mm": 3.0, "color": [0.045, 0.045, 0.055],
                "basis": "3.0 mm nominal layout allowance; purchased insulation OD unmeasured",
                "construction": "solid PVC at fixed cages; stranded at removable device leads"},
    "neutral16": {"awg": 16, "od_mm": 3.0, "color": [0.9, 0.9, 0.87],
                  "basis": "3.0 mm nominal layout allowance; purchased insulation OD unmeasured",
                  "construction": "solid PVC"},
    "earth16": {"awg": 16, "od_mm": 3.0, "color": [0.06, 0.42, 0.12],
                "basis": "3.0 mm nominal layout allowance; purchased insulation OD unmeasured",
                "construction": "stranded green silicone"},
    "cord18": {"awg": 18, "od_mm": 2.6, "color": [0.045, 0.045, 0.055],
               "basis": "Individual conductor layout allowance inside the SJOOW lead",
               "construction": "three stranded conductors in one continuous jacket"},
}
STOCK['neutral18']={**STOCK['cord18'],'color':[.9,.9,.87]}
STOCK['earth18']={**STOCK['cord18'],'color':[.06,.42,.12]}


def add(a, b): return tuple(x + y for x, y in zip(a, b))
def sub(a, b): return tuple(x - y for x, y in zip(a, b))
def mul(a, t): return tuple(x * t for x in a)
def dot(a, b): return sum(x * y for x, y in zip(a, b))
def norm(a): return math.sqrt(dot(a, a))
def unit(a): return mul(a, 1.0 / norm(a))


def rounded_segments(points, radius=4.0):
    """Lines and tangent arcs, with a locally limited radius at short approaches.

    The actual minimum is returned in the manifest. This is geometric shaping,
    not a manufacturer bend-radius qualification. Endpoints never move.
    """
    pts = []
    for p in points:
        p = tuple(map(float, p))
        if not pts or math.dist(pts[-1], p) > 1e-6:
            pts.append(p)
    corners = {}
    for i in range(1, len(pts) - 1):
        before, after = sub(pts[i-1], pts[i]), sub(pts[i+1], pts[i])
        la, lb = norm(before), norm(after)
        u, v = unit(before), unit(after)
        included = math.acos(max(-1.0, min(1.0, dot(u, v))))
        if included < 1e-5 or abs(math.pi - included) < 1e-5:
            continue
        tangent = min(radius / math.tan(included/2), .44*la, .44*lb)
        r = tangent * math.tan(included/2)
        a, b = add(pts[i], mul(u, tangent)), add(pts[i], mul(v, tangent))
        bisector = unit(add(u, v))
        centre = add(pts[i], mul(bisector, r/math.sin(included/2)))
        midpoint = add(centre, mul(bisector, -r))
        corners[i] = a, midpoint, b, r, math.pi-included
    out, current = [], pts[0]
    def line(end):
        nonlocal current
        length = math.dist(current, end)
        if length > 1e-6:
            out.append({"kind": "line", "start_mm": current, "end_mm": end,
                        "length_mm": length})
        current = end
    for i in range(1, len(pts)-1):
        if i not in corners:
            line(pts[i]); continue
        a, mid, b, r, angle = corners[i]
        line(a)
        out.append({"kind": "arc", "start_mm": a, "midpoint_mm": mid,
                    "end_mm": b, "radius_mm": r, "angle_radians": angle,
                    "length_mm": r*angle})
        current = b
    line(pts[-1])
    return out


def shape(route, diameter):
    import cadquery as cq
    edges = []
    for s in route.segments:
        a, b = cq.Vector(*s["start_mm"]), cq.Vector(*s["end_mm"])
        edges.append(cq.Edge.makeLine(a, b) if s["kind"] == "line" else
                     cq.Edge.makeThreePointArc(a, cq.Vector(*s["midpoint_mm"]), b))
    path = cq.Wire.assembleEdges(edges)
    start = cq.Vector(*route.segments[0]["start_mm"])
    tangent = edges[0].tangentAt(0)
    profile = cq.Wire.makeCircle(diameter/2, start, tangent)
    return cq.Solid.sweep(profile, [], path, makeSolid=True, isFrenet=False)


def finish(connection, points, note="", radius=None):
    route = Route(connection, points, note=note)
    route.segments = rounded_segments(points, radius if radius is not None else
                                      5.0 if STOCK[connection.stock]["awg"] < 22 else 4.0)
    route.length_mm = sum(s["length_mm"] for s in route.segments)
    radii = [s["radius_mm"] for s in route.segments if s["kind"] == "arc"]
    route.minimum_bend_mm = round(min(radii), 4) if radii else None
    return route
