"""Lofts and sweeps as rings of corresponding points joined band by band.

A loft rules the sections OCCT's ThruSections would, edge pair by edge pair, each section on
the rule's own points (`loft`). A sweep carries the profile along the path in a
rotation-minimizing frame (the double-reflection method), one copy of the profile per path
point; a tube bend is cut into points by the rule at the bend's outer radius.
"""

import math

import numpy as np

from . import build
from .build import Part, _oriented, cap_triangles, orient_loops, plane_frame, record
from .rule import ANGULAR, LINEAR, canonical_axis, ring_count


def _edges(wire):
    from OCP.BRepTools import BRepTools_WireExplorer
    from cadquery.occ_impl import shapes as occ
    if isinstance(wire, occ.Edge):
        return [wire]
    exp = BRepTools_WireExplorer(wire.wrapped)
    out = []
    while exp.More():
        out.append(occ.Edge(exp.Current()))
        exp.Next()
    return out


def _kind(edge):
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.GeomAbs import GeomAbs_Circle, GeomAbs_Line
    k = BRepAdaptor_Curve(edge.wrapped).GetType()
    return "LINE" if k == GeomAbs_Line else "CIRCLE" if k == GeomAbs_Circle else "OTHER"


def _compatible(wires):
    """The sections as OCCT's ThruSections lofts them (BRepFill_CompatibleWires): the same
    count of edges in every one, a section split where another's vertex projects about its
    center (the polar method), origins and directions lined up."""
    from OCP.BRepFill import BRepFill_CompatibleWires
    from OCP.TopTools import TopTools_SequenceOfShape
    from OCP.TopoDS import TopoDS
    from cadquery.occ_impl import shapes as occ
    seq = TopTools_SequenceOfShape()
    for w in wires:
        seq.Append((occ.Wire.assembleEdges([w]) if isinstance(w, occ.Edge) else w).wrapped)
    work = BRepFill_CompatibleWires(seq)
    work.Perform(True)
    if not work.IsDone():
        raise ValueError("meshcad: loft sections OCCT cannot make compatible")
    out = work.Shape()
    return [occ.Wire(TopoDS.Wire_s(out.Value(i))) for i in range(1, out.Length() + 1)]


def _anchors(edge):
    """(t, points): the rule's points along `edge` in its direction (`solids._edge_points`),
    each at its share t of the edge's own parameter — length on a line, angle on a circle —
    from 0 at the edge's start to 1 at its end. A closed circle starts at its seam; where the
    seam falls between two of the rule's points, it lies on the chord joining them."""
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.GeomAbs import GeomAbs_Circle, GeomAbs_Line
    from OCP.GCPnts import GCPnts_TangentialDeflection
    from OCP.TopAbs import TopAbs_REVERSED
    from .solids import _edge_points
    ad = BRepAdaptor_Curve(edge.wrapped)
    u0, u1 = ad.FirstParameter(), ad.LastParameter()
    rev = edge.wrapped.Orientation() == TopAbs_REVERSED
    kind = ad.GetType()
    if kind == GeomAbs_Line:
        u = np.array([u0, u1])
        p = np.array([ad.Value(u0).Coord(), ad.Value(u1).Coord()])
    elif kind == GeomAbs_Circle:
        p, _, closed = _edge_points(edge)
        p = p[::-1] if rev else p
        ax = ad.Circle().Position()
        v = p - np.array(ax.Location().Coord())
        ang = np.arctan2(v @ np.array(ax.YDirection().Coord()), v @ np.array(ax.XDirection().Coord()))
        u = u0 + np.mod(ang - u0, 2 * math.pi)
        if closed:
            order = np.argsort(u, kind="stable")
            u, p = u[order], p[order]
            if u[0] - u0 > 1e-9 and u0 + 2 * math.pi - u[-1] > 1e-9:
                s = (u0 + 2 * math.pi - u[-1]) / (u[0] + 2 * math.pi - u[-1])
                seam = p[-1] + s * (p[0] - p[-1])
                u, p = np.r_[u0, u], np.vstack([seam, p])
            elif u0 + 2 * math.pi - u[-1] <= 1e-9:
                u, p = np.r_[u0, u[:-1]], np.vstack([p[-1:], p[:-1]])
            u, p = np.r_[u, u1], np.vstack([p, p[:1]])
        u[0], u[-1] = u0, u1
    else:
        d = GCPnts_TangentialDeflection(ad, u0, u1, ANGULAR, LINEAR)
        u = np.array([d.Parameter(i) for i in range(1, d.NbPoints() + 1)])
        p = np.array([d.Value(i).Coord() for i in range(1, d.NbPoints() + 1)])
    t = (u - u0) / (u1 - u0)
    t[0], t[-1] = 0.0, 1.0
    return (1.0 - t[::-1], p[::-1]) if rev else (t, p)


def _at(u, t, p):
    """The points at shares `u` along the polyline through `p` at shares `t`, each of its own
    points exactly where its share falls."""
    out = np.stack([np.interp(u, t, p[:, k]) for k in range(3)], 1)
    out[np.searchsorted(u, t, "right") - 1] = p
    return out


def _union(*shares):
    every = np.sort(np.concatenate(shares))
    u = every[np.r_[True, np.diff(every) > 1e-9]]
    u[0], u[-1] = 0.0, 1.0
    return u


def _ring(marks, shares):
    """(points, place): a section at `shares` along each of its edges, in ring order; a
    point's place is its edge's index plus its share along it."""
    pts = np.concatenate([_at(f, t, p)[:-1] for (t, p), f in zip(marks, shares)])
    place = np.concatenate([j + f[:-1] for j, f in enumerate(shares)])
    return pts, place


def _twist_split(ma, mb, shares, V):
    """`shares` with as many more between neighbours as keep every quad of the band between
    sections `ma` and `mb`, cut along its rulings at `V`, within LINEAR / 2 of the ruled
    surface: a bilinear patch's center sits a quarter of its twist off the two triangles that
    stand for it, and a quad's twist shrinks with its width."""
    for _ in range(8):
        A, B = _ring(ma, shares)[0], _ring(mb, shares)[0]
        An, Bn = np.roll(A, -1, axis=0), np.roll(B, -1, axis=0)
        twist = (An - A) - (Bn - B)
        worst = np.zeros(len(A))
        for v0, v1 in zip(V, V[1:]):
            n = np.cross(An + v1 * (Bn - An) - A - v0 * (B - A), A + v1 * (B - A) - An - v0 * (Bn - An))
            size = np.linalg.norm(n, axis=1)
            off = np.abs(np.einsum("ij,ij->i", twist, n)) / np.where(size > 0, size, 1.0)
            worst = np.maximum(worst, (v1 - v0) * off / 4)
        need = np.minimum(np.ceil(worst / (LINEAR / 2) - 1e-9), 64).astype(int)
        if (need <= 1).all():
            return shares
        out, k = [], 0
        for f in shares:
            parts = [f[:1]]
            for q in range(len(f) - 1):
                if need[k + q] > 1:
                    parts.append(f[q] + (f[q + 1] - f[q]) * np.arange(1, need[k + q]) / need[k + q])
                parts.append(f[q + 1:q + 2])
            k += len(f) - 1
            out.append(np.concatenate(parts))
        shares = out
    return shares


def _ruling_cuts(p0, p1):
    """Shares along the rulings between rings `p0` and `p1`, from 0 to 1, to cut the band at:
    halved until no quad's normal turns more than ANGULAR from one cut to the next, and no
    finer than a 64th. A quad's normal turns with the mix of its two chords, so it turns
    fastest where the longer chord stops outweighing the shorter, and the cuts gather there. A
    quad whose ends' normals are a quarter turn or more apart is folded: its normal swings
    round through nearly nothing somewhere along the ruling, no count of cuts brings that swing
    under ANGULAR, and it is left out."""
    R = p1 - p0
    da = np.roll(p0, -1, axis=0) - p0
    db = np.roll(p1, -1, axis=0) - p1
    keep = np.einsum("ij,ij->i", np.cross(da, R), np.cross(db, R)) > 0
    R, da, db = R[keep], da[keep], db[keep]

    def turn(v0, v1):
        n0 = np.cross((1 - v0) * da + v0 * db, R)
        n1 = np.cross((1 - v1) * da + v1 * db, R)
        s0, s1 = np.linalg.norm(n0, axis=1), np.linalg.norm(n1, axis=1)
        ok = (s0 > 1e-12) & (s1 > 1e-12)
        if not ok.any():
            return 0.0
        c = np.einsum("ij,ij->i", n0[ok], n1[ok]) / (s0[ok] * s1[ok])
        return float(np.arccos(np.clip(c, -1.0, 1.0)).max())

    cuts, todo = [0.0], [(0.0, 1.0)]
    while todo:
        v0, v1 = todo.pop()
        if v1 - v0 > 1.0 / 64 and turn(v0, v1) > ANGULAR:
            todo += [((v0 + v1) / 2, v1), (v0, (v0 + v1) / 2)]
        else:
            cuts.append(v1)
    return np.array(cuts)


def _zip(ia, ga, ib, gb, period):
    """Triangles joining ring a to ring b, both closed and ordered by place from 0 to
    `period`, each wound from a's chord toward b; and the place each one's chord starts at.
    Where the two rings share their places it is the quads' own split."""
    ia, ga = np.r_[ia, ia[:1]], np.r_[ga, period]
    ib, gb = np.r_[ib, ib[:1]], np.r_[gb, period]
    tris, start = [], []
    i = j = 0
    while i < len(ga) - 1 or j < len(gb) - 1:
        if i < len(ga) - 1 and (j == len(gb) - 1 or ga[i + 1] < gb[j + 1] - 1e-9):
            tris.append((ia[i], ia[i + 1], ib[j]))
            start.append(ga[i])
            i += 1
        else:
            tris.append((ia[i], ib[j + 1], ib[j]))
            start.append(gb[j])
            j += 1
    return np.array(tris, np.int64), np.array(start)


def loft(wires, ruled, src):
    """Bands between consecutive section wires, capped at both ends.

    The sections are the compatible wires ThruSections makes (`_compatible`), and each edge
    pair is ruled as ThruSections rules it: the point a share t along one edge's own
    parameter meets the point the same share along the other's. Each band is cut along its
    rulings where its normal turns (`_ruling_cuts`) and across them where it twists
    (`_twist_split`), on its own. A section holds the points of the bands on both its sides,
    the rule's points on its own edges and the rest on the chords joining them, so its cap
    meets a face cut from the same wire point for point."""
    edge_lists = [_edges(w) for w in _compatible(wires)]
    marks = [[_anchors(e) for e in el] for el in edge_lists]
    kinds = [[_kind(e) for e in el] for el in edge_lists]
    ns, ne = len(marks), len(marks[0])
    op = "loft" if ruled or len(wires) == 2 else "loft (smooth taken ruled)"
    bands = []
    for b in range(ns - 1):
        shares = [_union(ta, tb) for (ta, _), (tb, _) in zip(marks[b], marks[b + 1])]
        V = _ruling_cuts(_ring(marks[b], shares)[0], _ring(marks[b + 1], shares)[0])
        bands.append((_twist_split(marks[b], marks[b + 1], shares, V), V))
    verts, count = [], 0

    def add(points):
        nonlocal count
        verts.append(points)
        count += len(points)
        return np.arange(count - len(points), count)

    rings = []
    for i in range(ns):
        side = [bands[k][0] for k in (i - 1, i) if 0 <= k < ns - 1]
        pts, place = _ring(marks[i], [_union(*fs) for fs in zip(*side)])
        rings.append((add(pts), place, pts))
    axis = rings[-1][2].mean(0) - rings[0][2].mean(0)
    outward = np.dot(_normal(rings[0][2]), axis) >= 0   # a chord crossed with its ruling points out
    tris, fids, records = [], [], []
    for b, (shares, V) in enumerate(bands):
        first = len(records)
        for j in range(ne):
            (ta, pa), (tb, pb) = marks[b][j], marks[b + 1][j]
            nrm = np.cross(pa[-1] - pa[0], pb[0] - pa[0])
            size = np.linalg.norm(nrm)
            if (kinds[b][j] == kinds[b + 1][j] == "LINE" and size > 0
                    and abs(np.dot(pb[-1] - pa[0], nrm / size)) < 1e-7):
                records.append(record("PLANE", src, op, p=pa[0], n=nrm / size if outward else -nrm / size))
            else:
                records.append(record("BSPLINE", src, op))
        A, place = _ring(marks[b], shares)
        B = _ring(marks[b + 1], shares)[0]
        lower = rings[b][:2]
        for v in V[1:-1]:
            upper = (add(A + v * (B - A)), place)
            if lower[1] is place:
                k = np.arange(len(place))
                k1 = np.roll(k, -1)
                ia, ib = lower[0], upper[0]
                band = np.stack([np.stack([ia[k], ib[k1], ib[k]], 1),
                                 np.stack([ia[k], ia[k1], ib[k1]], 1)], 1).reshape(-1, 3)
                start = np.repeat(place, 2)
            else:
                band, start = _zip(lower[0], lower[1], upper[0], upper[1], ne)
            tris.append(band)
            fids.append(first + np.floor(start).astype(np.int64))
            lower = upper
        band, start = _zip(lower[0], lower[1], rings[b + 1][0], rings[b + 1][1], ne)
        tris.append(band)
        fids.append(first + np.floor(start).astype(np.int64))
    tris = np.concatenate(tris)
    if not outward:
        tris = tris[:, ::-1]
    for (ids, _, pts), sense in ((rings[0], -1.0), (rings[-1], 1.0)):
        nrm = _normal(pts)
        _, x, y = plane_frame(nrm)
        cap = cap_triangles([np.stack([pts @ x, pts @ y], 1)])
        if np.dot(nrm, axis) * sense < 0:
            cap, nrm = cap[:, ::-1], -nrm
        records.append(record("PLANE", src, op, p=pts[0], n=nrm))
        tris = np.vstack([tris, ids[cap]])
        fids.append(np.full(len(cap), len(records) - 1))
    verts = np.concatenate(verts)
    return Part(verts, _oriented(verts, tris), np.concatenate(fids).astype(np.int64), records)


def _normal(p):
    c = p.mean(0)
    n = np.zeros(3)
    for i in range(len(p)):
        n += np.cross(p[i] - c, p[(i + 1) % len(p)] - c)
    return n / np.linalg.norm(n)


def _bands(sections, seg_edge, closed_path, src, op):
    """Quads between consecutive sections, one face per band and edge."""
    m = len(sections[0])
    ns = len(sections)
    verts = np.concatenate(sections)
    nb = ns if closed_path is True else ns - 1
    i = np.repeat(np.arange(nb), m)
    k = np.tile(np.arange(m), nb)
    k1 = (k + 1) % m
    a0, b0 = i * m, ((i + 1) % ns) * m
    tris = np.stack([np.stack([a0 + k, a0 + k1, b0 + k1], 1),
                     np.stack([a0 + k, b0 + k1, b0 + k], 1)], 1).reshape(-1, 3)
    seg_edge = np.asarray(seg_edge, np.int64)
    key = i * (int(seg_edge.max()) + 1) + seg_edge[k]
    _, first, inv = np.unique(key, return_index=True, return_inverse=True)
    rank = np.empty(len(first), np.int64)
    rank[np.argsort(first, kind="stable")] = np.arange(len(first))
    fids = np.repeat(rank[inv], 2)
    records = [record("BSPLINE", src, op) for _ in range(len(first))]
    if closed_path == "open":                  # walls only; the caller caps them
        return Part(verts, tris, fids, records)
    if not closed_path:
        caps, cap_fids = [tris], [fids]
        for idx, sec, flip in ((0, sections[0], True), (ns - 1, sections[-1], False)):
            nrm = _normal(sec)
            _, x, y = plane_frame(nrm)
            cap = cap_triangles([np.stack([sec @ x, sec @ y], 1)])
            records.append(record("PLANE", src, op, p=sec[0], n=-nrm if flip else nrm))
            caps.append((cap[:, ::-1] if flip else cap) + idx * m)
            cap_fids.append(np.full(len(cap), len(records) - 1))
        tris, fids = np.concatenate(caps), np.concatenate(cap_fids)
    return Part(verts, _oriented(verts, tris), fids, records)


def _fiber_params(ad, u0, u1, reach):
    """Parameters along a curve that hold the rule on a sweep's outermost fiber, `reach` off
    the curve, spaced as `ring_count` spaces a circle: over a short span that turns by theta
    the fiber's radius is the curve's, chord / theta, plus `reach`, and the rule allows that
    radius a step of its own; the points fall evenly in turn over allowed step."""
    from OCP.GCPnts import GCPnts_TangentialDeflection
    from OCP.gp import gp_Pnt, gp_Vec
    d = GCPnts_TangentialDeflection(ad, u0, u1, ANGULAR / 4, LINEAR / 4)
    u = np.array([d.Parameter(i) for i in range(1, d.NbPoints() + 1)])
    P, T = [], []
    for x in u:
        p, v = gp_Pnt(), gp_Vec()
        ad.D1(x, p, v)
        P.append(p.Coord())
        T.append(v.Coord())
    P, T = np.array(P), np.array(T)
    T /= np.linalg.norm(T, axis=1)[:, None]
    theta = np.arccos(np.clip(np.einsum("ij,ij->i", T[:-1], T[1:]), -1.0, 1.0))
    chord = np.linalg.norm(np.diff(P, axis=0), axis=1)
    R = chord / np.maximum(theta, 1e-12) + reach
    step = np.minimum(ANGULAR, 2 * np.arccos(np.clip(1 - LINEAR / np.maximum(R, LINEAR), -1.0, 1.0)))
    cum = np.r_[0.0, np.cumsum(theta / step)]
    out = np.interp(np.linspace(0.0, cum[-1], max(1, math.ceil(cum[-1] - 1e-9)) + 1), cum, u)
    out[0], out[-1] = u0, u1
    return out


def _path(path, reach):
    """(points, tangents, edge index of each band) along the path; bends cut at radius+reach."""
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.GeomAbs import GeomAbs_Circle, GeomAbs_Line
    from OCP.TopAbs import TopAbs_REVERSED
    pts, tans, band = [], [], []
    for ei, e in enumerate(_edges(path)):
        ad = BRepAdaptor_Curve(e.wrapped)
        u0, u1 = ad.FirstParameter(), ad.LastParameter()
        k = ad.GetType()
        if k == GeomAbs_Line:
            u = np.array([u0, u1])
        elif k == GeomAbs_Circle:
            n = max(1, math.ceil(ring_count(ad.Circle().Radius() + reach) * (u1 - u0) / (2 * math.pi) - 1e-9))
            u = np.linspace(u0, u1, n + 1)
        else:
            u = _fiber_params(ad, u0, u1, reach)
        p = np.array([ad.Value(x).Coord() for x in u])
        t = []
        for x in u:
            from OCP.gp import gp_Pnt, gp_Vec
            P, V = gp_Pnt(), gp_Vec()
            ad.D1(x, P, V)
            t.append(np.array(V.Coord()))
        t = np.array(t)
        if e.wrapped.Orientation() == TopAbs_REVERSED:
            p, t = p[::-1], -t[::-1]
        t /= np.linalg.norm(t, axis=1)[:, None]
        if pts and np.linalg.norm(pts[-1][-1] - p[0]) < 1e-7:
            joint = tans[-1][-1] + t[0]
            tans[-1][-1] = joint / np.linalg.norm(joint)
            p, t = p[1:], t[1:]
        pts.append(p)
        tans.append(t)
        band += [ei] * len(p)
    P, T = np.concatenate(pts), np.concatenate(tans)
    return P, T, np.array(band[1:] if len(band) > 1 else band)


def sweep(loops, normal, path, isFrenet, mode, src):
    loops, _ = orient_loops([build.clean_loop(lp) for lp in loops], normal)
    prof = loops[0].pts
    P, T, band = _path(path, 0.0)
    reach = float(np.linalg.norm(prof - P[0], axis=1).max())
    P, T, band = _path(path, reach)
    if np.dot(T[0], normal) < 0:
        loops, _ = orient_loops(loops, -np.asarray(normal))
        prof = loops[0].pts
    closed = np.linalg.norm(P[0] - P[-1]) < 1e-7 and len(P) > 2
    if closed:
        P, T = P[:-1], T[:-1]
    t0 = T[0]
    r0 = np.cross(t0, [0, 0, 1.0]) if abs(t0[2]) < 0.9 else np.cross(t0, [1.0, 0, 0])
    r0 /= np.linalg.norm(r0)
    frames = [r0]
    if mode is not None and not isinstance(mode, str) and hasattr(mode, "toTuple"):
        b = np.array(mode.toTuple(), float)
        frames = [np.cross(b, t) / np.linalg.norm(np.cross(b, t)) for t in T]
        frames = [np.cross(t, f) for t, f in zip(T, frames)]
    else:
        for i in range(len(P) - 1):
            v1 = P[i + 1] - P[i]
            c1 = v1 @ v1
            rL = frames[i] - (2 / c1) * (v1 @ frames[i]) * v1
            tL = T[i] - (2 / c1) * (v1 @ T[i]) * v1
            v2 = T[i + 1] - tL
            c2 = v2 @ v2
            frames.append(rL - (2 / c2) * (v2 @ rL) * v2 if c2 > 1e-30 else rL)
    s0 = np.cross(t0, frames[0])
    per_loop = []
    for lp in loops:
        rel = lp.pts - P[0]
        local = np.stack([rel @ t0, rel @ frames[0], rel @ s0], 1)
        sections = []
        for p, t, r in zip(P, T, frames):
            s = np.cross(t, r)
            sections.append(p + local[:, :1] * t + local[:, 1:2] * r + local[:, 2:3] * s)
        per_loop.append((sections, np.asarray(lp.seg)))
    if len(per_loop) == 1:
        part = _bands(per_loop[0][0], per_loop[0][1], closed, src, "sweep")
    else:
        part = _holed(per_loop, closed, src, "sweep")
    # The walls' records come first, loop after loop, one per band and profile curve. A loop that
    # is one circle has one face per band, in band order, each on the surface its path edge
    # carries the circle through: a tube's outside and its bore alike.
    nb = len(P) if closed else len(P) - 1
    base = 0
    for lp in loops:
        rode = _rode(lp, path, P, T, src)
        if rode is not None:
            for i, e in enumerate(band[:nb]):
                if rode[e] is not None:
                    part.records[base + i] = rode[e]
        base += nb * len({int(s) for s in lp.seg})
    return part


def _rode(loop, path, P, T, src):
    """Per path edge, the surface one loop of a profile riding the path sweeps — a line's
    cylinder, an arc's torus, as OCCT makes them, or None for another curve — or None when the
    loop is not one circle centred on the path's start, square to it."""
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.GeomAbs import GeomAbs_Circle, GeomAbs_Line
    curves = {int(s) for s in loop.seg}
    if len(curves) != 1:
        return None
    circle = loop.curves[curves.pop()]
    if (circle.kind != "CIRCLE" or np.linalg.norm(np.asarray(circle.center) - P[0]) > 1e-6
            or np.linalg.norm(np.cross(np.asarray(circle.axis, float), T[0])) > 1e-6):
        return None
    out = []
    for e in _edges(path):
        ad = BRepAdaptor_Curve(e.wrapped)
        k = ad.GetType()
        if k == GeomAbs_Line:
            line = ad.Line()
            out.append(record("CYLINDER", src, "sweep", p=np.array(line.Location().Coord()),
                              d=canonical_axis(line.Direction().Coord()), r=circle.r))
        elif k == GeomAbs_Circle:
            arc = ad.Circle()
            out.append(record("TORUS", src, "sweep", c=np.array(arc.Location().Coord()),
                              d=np.array(arc.Axis().Direction().Coord()), R=arc.Radius(),
                              r=circle.r))
        else:
            out.append(None)
    return out


def _holed(per_loop, closed_path, src, op):
    """`_bands` for a profile with holes: each loop's walls, and both ends capped across all
    of them at once."""
    walls = [_bands(sections, seg, True if closed_path else "open", src, op)
             for sections, seg in per_loop]
    verts, tris, fids, records, base = [], [], [], [], 0
    bases = []
    for part in walls:
        bases.append(base)
        verts.append(part.verts)
        tris.append(part.tris + base)
        fids.append(part.fids + len(records))
        records += part.records
        base += len(part.verts)
    if not closed_path:
        ns = len(per_loop[0][0])
        for idx, flip in ((0, True), (ns - 1, False)):
            secs = [sections[idx] for sections, _ in per_loop]
            nrm = _normal(secs[0])
            _, x, y = plane_frame(nrm)
            cap = cap_triangles([np.stack([sec @ x, sec @ y], 1) for sec in secs])
            starts = np.concatenate([[0], np.cumsum([len(sec) for sec in secs])])
            glob = np.concatenate([b + idx * len(sec) + np.arange(len(sec))
                                   for b, sec in zip(bases, secs)])
            records.append(record("PLANE", src, op, p=secs[0][0], n=-nrm if flip else nrm))
            cap = glob[cap[:, ::-1] if flip else cap]
            tris.append(cap)
            fids.append(np.full(len(cap), len(records) - 1))
    verts = np.concatenate(verts)
    return Part(verts, _oriented(verts, np.concatenate(tris)), np.concatenate(fids), records)


def prism(faces, vector):
    """The solid mesh `faces` sweep along `vector`: each triangle's own prism, the hull of its
    corners at both ends, all unioned. Two triangles that share an edge share the face that
    edge sweeps, so the union closes between them; a triangle that sweeps no volume, `vector`
    in its plane, is left out."""
    import manifold3d as m3d
    from .rule import caller, snap
    from .solids import MeshCompound, MeshSolid
    src = caller()
    v = np.asarray(vector, float)
    parts = []
    for f in faces:
        t = f.topo.t
        for tri in t.V[t.T[f.tris]]:
            corners = snap(np.vstack([tri, tri + v]))     # on the grid before the hull, not after
            if m3d.Manifold.hull_points(corners).volume() > 1e-12:
                parts.append(build.solid(build.hull_part(corners, src, "prism")))
    if not parts:
        return MeshCompound([])
    joined = build.boolean(parts, m3d.OpType.Add)
    return MeshCompound([MeshSolid(p) for p in joined.decompose()])
