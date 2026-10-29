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


def rounded_segments(points, radius=4.0, *, keep_collinear=False,
                     endpoint_tangent_fraction=.44):
    """Lines and tangent arcs, with a locally limited radius at short approaches.

    The actual minimum is returned in the manifest. This is geometric shaping,
    not a manufacturer bend-radius qualification. Endpoints never move.
    A saved endpoint tangent fraction can use more of an isolated terminal
    approach; interior corners retain their usual shared-segment allowance.
    """
    pts = []
    for p in points:
        p = tuple(map(float, p))
        if not pts or math.dist(pts[-1], p) > 1e-6:
            pts.append(p)
        if not keep_collinear:
            while len(pts)>2:
                a,b=sub(pts[-2],pts[-3]),sub(pts[-1],pts[-2])
                if dot(unit(a),unit(b))<1.-1e-10:
                    break
                pts.pop(-2)
    corners = {}
    for i in range(1, len(pts) - 1):
        before, after = sub(pts[i-1], pts[i]), sub(pts[i+1], pts[i])
        la, lb = norm(before), norm(after)
        u, v = unit(before), unit(after)
        included = math.acos(max(-1.0, min(1.0, dot(u, v))))
        if included < 1e-5 or abs(math.pi - included) < 1e-5:
            continue
        before_fraction = endpoint_tangent_fraction if i == 1 else .44
        after_fraction = endpoint_tangent_fraction if i == len(pts)-2 else .44
        tangent = min(radius / math.tan(included/2), before_fraction*la,
                      after_fraction*lb)
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


def spline_segment(points, tangents):
    """Record a smooth native span and its arc-length samples for pure readers."""
    count=len(points)-1
    derivatives=[]
    for direction,a,b,c in [(tangents[0],*points[:3]),(tangents[1],*reversed(points[-3:]))]:
        derivative=mul(sub(sub(mul(b,4),c),mul(a,3)),count/2)
        derivatives.append(mul(unit(direction),abs(dot(derivative,unit(direction)))))
    segment={'kind':'spline','start_mm':points[0],'end_mm':points[-1],
             'interpolation_points_mm':points,'endpoint_tangents':tangents,
             'endpoint_derivatives':derivatives,'parameters':[i/count for i in range(count+1)]}
    edge=segment_edge(segment);length=edge.Length();count=max(2,math.ceil(length/.25))
    segment.update(length_mm=length,
                   sampled_points_mm=[edge.positionAt(i/count).toTuple()for i in range(count+1)],
                   maximum_sample_step_mm=length/count,
                   minimum_bend_mm=min((1/k for k in edge.curvatures([i/200 for i in range(201)])if k>1e-12),default=None))
    return segment


def sampled_segments(segments, step=1.):
    """Sample recorded lines, circular arcs and smooth spans without importing CAD.

    Smooth spans retain native arc-length samples at no more than 0.25 mm;
    intermediate display/search points interpolate those recorded samples.
    """
    points=[]
    def append_line(a,b):
        count=max(1,math.ceil(norm(sub(b,a))/step))
        points.extend(add(a,mul(sub(b,a),i/count))for i in range(count))
    for s in segments:
        a,b=s['start_mm'],s['end_mm']
        if s['kind']=='line':append_line(a,b)
        elif s['kind']=='spline':
            for p,q in zip(s['sampled_points_mm'],s['sampled_points_mm'][1:]):append_line(p,q)
        elif s['kind']=='arc':
            u,v=sub(s['midpoint_mm'],a),sub(b,a)
            cross=lambda x,y:(x[1]*y[2]-x[2]*y[1],x[2]*y[0]-x[0]*y[2],x[0]*y[1]-x[1]*y[0])
            n=cross(u,v)
            centre=add(a,mul(add(mul(cross(n,u),dot(v,v)),mul(cross(v,n),dot(u,u))),1/(2*dot(n,n))))
            x=mul(sub(a,centre),1/s['radius_mm']);y=cross(unit(n),x)
            count=max(2,math.ceil(s['length_mm']/step))
            points.extend(add(centre,mul(add(mul(x,math.cos(s['angle_radians']*i/count)),mul(y,math.sin(s['angle_radians']*i/count))),s['radius_mm']))for i in range(count))
        else:raise ValueError(('Unknown wire segment',s['kind']))
    if segments:points.append(tuple(segments[-1]['end_mm']))
    return points


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


def finish(connection, points, note="", radius=None, *, endpoint_tangent_fraction=.44):
    route = Route(connection, points, note=note)
    route.segments = rounded_segments(points, radius if radius is not None else
                                      5.0 if STOCK[connection.stock]["awg"] < 22 else 4.0,
                                      endpoint_tangent_fraction=endpoint_tangent_fraction)
    route.length_mm = sum(s["length_mm"] for s in route.segments)
    radii = [s["radius_mm"] for s in route.segments if s["kind"] == "arc"]
    route.minimum_bend_mm = round(min(radii), 4) if radii else None
    return route
