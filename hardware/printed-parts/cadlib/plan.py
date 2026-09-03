"""Plans — figures in the XY plane, and the prisms that stand on them.

A CAVITY IS ONE FIGURE. A pocket cut for each body in a set is a list of cutters, and what
stands between two of them — a web thinner than a wall, a corner round running on past the
edge it was drawn against — is in no cutter. Held as one figure the set has an inside and an
outside and nothing else: a gap narrower than a wall is filled (`closed`), the stock's own
plan is where the figure stops (`prism`'s `within`), and a mouth is rounded because the
figure turns there, whatever cutters it was assembled from.

THE TOPOLOGY IS HELD IN SHAPELY AND THE SOLID IS CUT IN OCCT. Union, mitred offset and
intersection of planar figures are exact there, and a mitred offset of an axis-aligned figure
comes back axis-aligned on the same coordinates. The prism is then built from that figure's
own vertices, every arc a true arc, so the STEP reads planes and cylinders.

A FIGURE'S INTERIOR STANDS ON THE LEFT of every ring that bounds it — the exterior run
counter-clockwise, each hole clockwise. A corner where a ring turns LEFT is a convex corner
of the figure: a pocket's mouth, seen from the stock it is cut out of, and the only corner
`prism` rounds. A right turn is a pillar's own corner and stays sharp.
"""

import math

import cadquery as cq
from shapely.geometry import box as _box
from shapely.geometry.polygon import orient as _orient
from shapely.ops import unary_union

#: A corner whose round would come out shorter than this is left sharp.
round_min = 0.1
#: Two vertices within this are one vertex; a straight shorter than this is not drawn.
_MERGE = 1e-7
#: A ring vertex whose turn is flatter than this is a point on a straight, not a corner.
_STRAIGHT = 1e-9


def rect(x0, x1, y0, y1):
    """The axis-aligned figure between these bounds."""
    return _box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))


def union(figures):
    """One figure covering every figure given."""
    return unary_union(list(figures))


def closed(figure, web):
    """`figure` with every gap narrower than `web` between its parts filled in.

    The morphological closing: grown by half of `web` and shrunk back by the same, both with
    mitred corners. Two parts standing closer than `web` are one part afterwards; a part's own
    outline is untouched."""
    return (figure.buffer(web / 2.0, join_style="mitre")
            .buffer(-web / 2.0, join_style="mitre"))


def prism(figure, z0, z1, round_r=0.0, within=None):
    """The solids standing on `figure` from `z0` to `z1`, one per island.

    `within` is `(x0, x1, y0, y1)`, the plan of the stock the prism is cut from: the figure is
    cut to it, and a corner standing on it is where the figure leaves the stock and stays
    square. Every other convex corner is rounded to `round_r` — or to what half of the shorter
    edge it stands on allows, so the two rounds one edge carries always fit — and a round
    under `round_min` is left sharp."""
    if within is not None:
        figure = figure.intersection(rect(*within))
    solids = []
    for island in _islands(figure):
        island = _orient(island, 1.0)
        outer = _ring(island.exterior.coords, z0, round_r, within)
        holes = [_ring(hole.coords, z0, round_r, within) for hole in island.interiors]
        face = cq.Face.makeFromWires(outer, holes)
        solids.append(cq.Solid.extrudeLinear(face, cq.Vector(0.0, 0.0, z1 - z0)))
    return tuple(solids)


def _islands(figure):
    """The polygons in a figure, whatever shapely wrapped them in."""
    if figure.is_empty:
        return
    if figure.geom_type == "Polygon":
        if figure.area > _MERGE:
            yield figure
    elif hasattr(figure, "geoms"):
        for part in figure.geoms:
            yield from _islands(part)


def _corners(coords):
    """A ring's vertices with the repeated closing point, doubled points and points that lie
    on a straight all dropped, in the ring's own order."""
    pts = []
    for x, y in coords:
        p = (float(x), float(y))
        if not pts or abs(p[0] - pts[-1][0]) > _MERGE or abs(p[1] - pts[-1][1]) > _MERGE:
            pts.append(p)
    while len(pts) > 1 and (abs(pts[0][0] - pts[-1][0]) <= _MERGE
                            and abs(pts[0][1] - pts[-1][1]) <= _MERGE):
        pts.pop()
    n = len(pts)
    corners = []
    for i, p in enumerate(pts):
        a, b = pts[i - 1], pts[(i + 1) % n]
        d1 = (p[0] - a[0], p[1] - a[1])
        d2 = (b[0] - p[0], b[1] - p[1])
        cross = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(cross) > _STRAIGHT * math.hypot(*d1) * math.hypot(*d2):
            corners.append(p)
    return corners


def _on(p, within):
    """Whether a vertex stands on the stock's plan boundary."""
    if within is None:
        return False
    x0, x1, y0, y1 = within
    return (abs(p[0] - x0) <= _MERGE or abs(p[0] - x1) <= _MERGE
            or abs(p[1] - y0) <= _MERGE or abs(p[1] - y1) <= _MERGE)


def _ring(coords, z, round_r, within):
    """One closed wire on the ring, drawn in the ring's order with its closing edge explicit:
    a straight to each corner and, where the corner is rounded, the arc through it."""
    pts = _corners(coords)
    n = len(pts)
    stations = []
    for i, p in enumerate(pts):
        a, b = pts[i - 1], pts[(i + 1) % n]
        l_in = math.hypot(p[0] - a[0], p[1] - a[1])
        l_out = math.hypot(b[0] - p[0], b[1] - p[1])
        d_in = ((p[0] - a[0]) / l_in, (p[1] - a[1]) / l_in)
        d_out = ((b[0] - p[0]) / l_out, (b[1] - p[1]) / l_out)
        cross = d_in[0] * d_out[1] - d_in[1] * d_out[0]
        dot = d_in[0] * d_out[0] + d_in[1] * d_out[1]
        turn = math.atan2(cross, dot)
        r = round_r if cross > 0.0 and not _on(p, within) else 0.0
        if r > 0.0:
            tangent = min(r * math.tan(turn / 2.0), l_in / 2.0, l_out / 2.0)
            r = tangent / math.tan(turn / 2.0)
        if r < round_min:
            stations.append((p, p, p, False))
            continue
        start = (p[0] - d_in[0] * tangent, p[1] - d_in[1] * tangent)
        end = (p[0] + d_out[0] * tangent, p[1] + d_out[1] * tangent)
        bis = (d_out[0] - d_in[0], d_out[1] - d_in[1])
        bl = math.hypot(*bis)
        bis = (bis[0] / bl, bis[1] / bl)
        reach = r / math.cos(turn / 2.0)
        centre = (p[0] + bis[0] * reach, p[1] + bis[1] * reach)
        mid = (centre[0] - bis[0] * r, centre[1] - bis[1] * r)
        stations.append((start, mid, end, True))

    def v(q):
        return cq.Vector(q[0], q[1], z)

    edges = []
    for i, (start, mid, end, rounded) in enumerate(stations):
        prev_end = stations[i - 1][2]
        if math.hypot(start[0] - prev_end[0], start[1] - prev_end[1]) > _MERGE:
            edges.append(cq.Edge.makeLine(v(prev_end), v(start)))
        elif rounded:
            start = prev_end
        if rounded:
            edges.append(cq.Edge.makeThreePointArc(v(start), v(mid), v(end)))
    return cq.Wire.assembleEdges(edges)
