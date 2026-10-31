"""Fillets and chamfers on mesh solids, built as tools and cut or filled.

Rounding an edge is a 2D problem in its cross-section. A straight edge between faces that run
along it — planes, or cylinders whose axis is parallel to it — is cut across into two lines or
arcs meeting at a corner; the fillet circle tangent to both, and the sliver between it and the
corner, are extruded over the edge. A circle edge where a plane meets a coaxial cylinder or
cone is the same problem in the half-plane through the axis, turned about it.

A convex edge loses its sliver and a concave one gains it. The tool reaches a little past the
faces on the side that is empty, so the boolean never meets the solid exactly on its surface.
Where two rounded edges meet at a corner, each tool runs its own edge's full length and the
corner is what the two cuts leave, not OCCT's blend.
"""

import math

import manifold3d as m3d
import numpy as np

from . import build
from .build import Curve, Loop
from .rule import ANGULAR, LINEAR, axis_frame, caller, circle_points, ring_count


def fillet(solid, radius, edges):
    return _round(solid, edges, lambda corner: _fillet_profile(corner, radius), "fillet", radius)


def chamfer(solid, length, length2, edges):
    d2 = length if length2 is None else length2
    return _round(solid, edges, lambda corner: _chamfer_profile(corner, length, d2), "chamfer")


def _round(solid, edges, profile, op, radius=None):
    from .solids import MeshSolid
    src = caller()
    base, fill, cut = solid.rounds()
    fill, cut = list(fill), list(cut)
    for e in edges:
        try:
            tool, convex = _tool(e, profile, src, op)
        except NotImplementedError:
            if radius is None:
                raise
            tool, convex = _rolled(e, radius, src, op)
        if tool is not None:
            (cut if convex else fill).append(tool)
    return MeshSolid(None, (base, fill, cut))


class _Corner:
    """The cross-section at an edge: two curves through the origin, each with its outward
    normal and the direction into its face, in 2D coordinates (x, y)."""

    def __init__(self, curves, normals, intos):
        self.curves, self.n, self.u = curves, normals, intos
        self.convex = float(np.dot(intos[0], normals[1])) < 0


def _face_side(face, edge, at, axis):
    """(outward normal, direction into the face) where `edge` runs past `at`, both
    perpendicular to `axis`, read off the face's own triangle on that stretch of the edge."""
    t = face.topo.t
    v = np.asarray(edge.vids)
    mids = (t.V[v[1:]] + t.V[v[:-1]]) / 2
    i = int(np.argmin(np.linalg.norm(mids - at, axis=1)))
    a, b = v[i], v[i + 1]
    tri = t.T[face.tris]
    k = face.tris[np.flatnonzero((tri == a).any(1) & (tri == b).any(1))[0]]
    third = next(x for x in t.T[k] if x != a and x != b)
    # Into the face across the segment itself, where the triangle says which side is which;
    # then both directions laid into the cross-section.
    into = np.cross(t.tri_n[k], t.V[b] - t.V[a])
    if np.dot(t.V[third] - t.V[a], into) < 0:
        into = -into
    n = t.tri_n[k] - np.dot(t.tri_n[k], axis) * axis
    into = into - np.dot(into, axis) * axis
    return n / np.linalg.norm(n), into / np.linalg.norm(into)


def _tool(edge, profile, src, op):
    faces = edge.faces_of()
    if edge.kind == "LINE":
        a, b = edge.pts[0], edge.pts[-1]
        t = (b - a) / np.linalg.norm(b - a)
        _, e1, e2 = axis_frame(t)
        to2 = lambda p: np.array([np.dot(p - a, e1), np.dot(p - a, e2)])  # noqa: E731
        curves, normals, intos = [], [], []
        mid = (a + b) / 2
        for f in faces:
            rec = f.rec
            n3, u3 = _face_side(f, edge, mid, t)
            if rec["kind"] == "PLANE":
                curves.append(("LINE", None))
            elif rec["kind"] == "CYLINDER" and np.linalg.norm(np.cross(rec["d"], t)) < 1e-6:
                c = to2(np.asarray(rec["p"], float))
                curves.append(("CIRCLE", (c, rec["r"])))
            else:
                raise NotImplementedError(f"meshcad: {op} of a straight edge on a {rec['kind']} face")
            normals.append(np.array([np.dot(n3, e1), np.dot(n3, e2)]))
            intos.append(np.array([np.dot(u3, e1), np.dot(u3, e2)]))
        corner = _Corner(curves, normals, intos)
        poly, arc_mask, center2 = profile(corner)
        pts = np.array([a + x * e1 + y * e2 for x, y in poly])
        center3 = a + center2[0] * e1 + center2[1] * e2 if center2 is not None else None
        loop = _loop(pts, arc_mask, center3, t, profile_radius(corner, center2, poly))
        part = build.prism([loop], t, b - a, src, op)
        return build.solid(part), corner.convex
    if edge.kind == "CIRCLE":
        c, d, r = edge.circle
        p, turn = _arc_start(edge, c, d)
        radial = p - c - np.dot(p - c, d) * d
        e1 = radial / np.linalg.norm(radial)
        curves, normals, intos = [], [], []
        for f in faces:
            rec = f.rec
            n3, u3 = _face_side(f, edge, p, np.cross(d, e1))
            if rec["kind"] not in ("PLANE", "CYLINDER", "CONE"):
                raise NotImplementedError(f"meshcad: {op} of a circle edge on a {rec['kind']} face")
            curves.append(("LINE", None))
            normals.append(np.array([np.dot(n3, e1), np.dot(n3, d)]))
            intos.append(np.array([np.dot(u3, e1), np.dot(u3, d)]))
        corner = _Corner(curves, normals, intos)
        poly, arc_mask, center2 = profile(corner)
        pts = np.array([p + x * e1 + y * d for x, y in poly])
        center3 = p + center2[0] * e1 + center2[1] * d if center2 is not None else None
        normal = np.cross(e1, d)
        loop = _loop(pts, arc_mask, center3, normal, profile_radius(corner, center2, poly))
        axis_p = c
        part = build.revolve([loop], axis_p, d, turn, src, op)
        return build.solid(part), corner.convex
    raise NotImplementedError(f"meshcad: {op} of a {edge.kind} edge")


def _arc_start(edge, c, d):
    """(point the arc starts at, degrees it turns about `d` from there): the whole turn for a
    closed circle, else whichever end the arc leaves counterclockwise."""
    if edge.closed:
        return edge.pts[0], 360.0
    a, b = edge.pts[0] - c, edge.pts[-1] - c
    mid = edge.pts[len(edge.pts) // 2] - c

    def ang(u, v):
        return math.atan2(np.dot(np.cross(u, v), d), np.dot(u, v)) % (2 * math.pi)
    ab = ang(a, b)
    if ang(a, mid) <= ab:
        return edge.pts[0], math.degrees(ab)
    return edge.pts[-1], math.degrees(2 * math.pi - ab)


def profile_radius(corner, center2, poly):
    return getattr(corner, "radius", None)


def _loop(pts, arc_mask, center3, axis, radius):
    curves = [Curve("LINE"), Curve("CIRCLE", center3, axis, radius or 0.0)]
    seg = np.where(arc_mask, 1, 0)
    return build.clean_loop(Loop(pts, seg, curves))


def _offset_hits(curve, n, s, R):
    """The curve moved R along s·n: ('LINE', normal, offset) or ('CIRCLE', center, radius)."""
    kind, geo = curve
    if kind == "LINE":
        return ("LINE", n, s * R)
    c, r = geo
    sigma = 1.0 if np.dot(-c, n) > 0 else -1.0       # outward normal points away from the axis?
    return ("CIRCLE", c, r + s * sigma * R)


def _intersect(p, q):
    if p[0] == "LINE" and q[0] == "LINE":
        A = np.array([p[1], q[1]])
        return [np.linalg.solve(A, [p[2], q[2]])]
    if p[0] == "CIRCLE" and q[0] == "LINE":
        p, q = q, p
    if p[0] == "LINE" and q[0] == "CIRCLE":
        n, off = p[1], p[2]
        c, r = q[1], q[2]
        foot = c + (off - np.dot(n, c)) * n
        h2 = r * r - np.sum((foot - c) ** 2)
        if h2 < 0:
            return []
        tdir = np.array([-n[1], n[0]])
        h = math.sqrt(h2)
        return [foot + h * tdir, foot - h * tdir]
    c1, r1, c2, r2 = p[1], p[2], q[1], q[2]
    dvec = c2 - c1
    dist = np.linalg.norm(dvec)
    a = (r1 * r1 - r2 * r2 + dist * dist) / (2 * dist)
    h2 = r1 * r1 - a * a
    if h2 < 0:
        return []
    base = c1 + a * dvec / dist
    perp = np.array([-dvec[1], dvec[0]]) / dist
    return [base + math.sqrt(h2) * perp, base - math.sqrt(h2) * perp]


def _foot(curve, n, x):
    kind, geo = curve
    if kind == "LINE":
        return x - np.dot(x, n) * n
    c, r = geo
    v = x - c
    return c + r * v / np.linalg.norm(v)


def _fillet_profile(corner, R):
    s = -1.0 if corner.convex else 1.0
    off = [_offset_hits(corner.curves[i], corner.n[i], s, R) for i in (0, 1)]
    # Of the offset curves' crossings, the fillet's center is the one whose tangent points
    # both lie on their own faces, going away from the corner.
    cands = [c for c in _intersect(off[0], off[1])
             if np.dot(_foot(corner.curves[0], corner.n[0], c), corner.u[0]) > 0
             and np.dot(_foot(corner.curves[1], corner.n[1], c), corner.u[1]) > 0]
    if not cands:
        raise ValueError(f"meshcad: no fillet of radius {R} fits this corner")
    center = min(cands, key=lambda x: np.linalg.norm(x))
    t1, t2 = _foot(corner.curves[0], corner.n[0], center), _foot(corner.curves[1], corner.n[1], center)
    corner.radius = R
    arc = _arc2(center, R, t1, t2)
    reach = max(0.25 * R, 0.02)
    for i in (0, 1):
        if corner.curves[i][0] == "CIRCLE":
            chord = np.linalg.norm((t1, t2)[i])
            reach = max(reach, 2 * chord * chord / (8 * corner.curves[i][1][1]) + 0.02)
    m = corner.n[0] + corner.n[1]
    m = m / max(np.linalg.norm(m), 1e-9)
    side = 1.0 if corner.convex else -1.0         # outside the solid for a cut, inside for a fill
    o = side * m * reach * 2.0 / max(np.linalg.norm(corner.n[0] + corner.n[1]), 0.2)
    pts = [t1 + side * reach * corner.n[0], *arc, t2 + side * reach * corner.n[1], o]
    is_arc = [False] + [True] * (len(arc) - 1) + [False, False, False]
    return np.array(pts), np.array(is_arc), center


def _arc2(center, R, a, b):
    """Points from a to b on the circle (center, R), the short way, on the rule's angles."""
    a3, b3, c3 = (np.array([p[0], p[1], 0.0]) for p in (a, b, center))
    turn = np.cross(a3 - c3, b3 - c3)[2]
    pts = circle_points(c3, (0, 0, 1), R, a3, b3, ccw_about=(0, 0, 1 if turn > 0 else -1))
    return pts[:, :2]


def _chamfer_profile(corner, d1, d2):
    t1 = d1 * corner.u[0]
    t2 = d2 * corner.u[1]
    corner.radius = None
    side = 1.0 if corner.convex else -1.0
    reach = 0.25 * max(d1, d2)
    m = corner.n[0] + corner.n[1]
    m = m / max(np.linalg.norm(m), 1e-9)
    o = side * m * reach * 2.0 / max(np.linalg.norm(corner.n[0] + corner.n[1]), 0.2)
    pts = [t1 + side * reach * corner.n[0], t1, t2, t2 + side * reach * corner.n[1], o]
    return np.array(pts), np.zeros(len(pts), bool), None


# --- Any other edge: the rolling ball, station by station -----------------------------------

class _Surface:
    """A face's surface as a signed distance, positive outside the solid, with the gradient of
    that distance (the outward normal of the level set through a point)."""

    KINDS = ("PLANE", "CYLINDER", "CONE", "SPHERE", "TORUS")

    def __init__(self, face, near):
        rec = face.rec
        kind = rec["kind"] if rec else None
        if kind not in self.KINDS:
            raise NotImplementedError(f"meshcad: fillet against a {kind} face")
        self.face, self.rec, self.kind, self.sign = face, rec, kind, 1.0
        t = face.topo.t
        k = face.tris[np.argmin(np.linalg.norm(t.tri_c[face.tris] - near, axis=1))]
        self.sign = 1.0 if np.dot(self.normal(t.tri_c[k]), t.tri_n[k]) > 0 else -1.0
        self.tri = t.V[t.T[face.tris]]

    def _parts(self, x):
        r = self.rec
        if self.kind == "PLANE":
            n = np.asarray(r["n"], float)
            n = n / np.linalg.norm(n)
            return np.dot(x - r["p"], n), n
        if self.kind == "SPHERE":
            v = x - r["c"]
            return np.linalg.norm(v) - r["r"], v / np.linalg.norm(v)
        d = np.asarray(r["d"], float)
        v = x - np.asarray(r.get("p", r.get("c")), float)
        h = np.dot(v, d)
        radial = v - h * d
        rho = np.linalg.norm(radial)
        out = radial / rho
        if self.kind == "CYLINDER":
            return rho - r["r"], out
        if self.kind == "CONE":
            k = math.hypot(1.0, r["slope"])
            return (rho - r["r"] - r["slope"] * h) / k, (out - r["slope"] * d) / k
        w = (rho - r["R"]) * out + h * d
        return np.linalg.norm(w) - r["r"], w / np.linalg.norm(w)

    def dist(self, x):
        return self.sign * self._parts(x)[0]

    def normal(self, x):
        return self.sign * self._parts(x)[1]

    def foot(self, x):
        s, n = self._parts(x)
        return x - s * n

    def holds(self, x, tol):
        """Whether `x` lies on this face's own patch, not on its surface past the patch."""
        return float(_tri_dist(x, self.tri).min()) <= tol


def _tri_dist(p, tri):
    """Distance from the point `p` to each triangle of `tri` (n, 3, 3)."""
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    ab, ac, ap = b - a, c - a, p - a
    d1, d2 = (ab * ap).sum(1), (ac * ap).sum(1)
    bp = p - b
    d3, d4 = (ab * bp).sum(1), (ac * bp).sum(1)
    cp = p - c
    d5, d6 = (ab * cp).sum(1), (ac * cp).sum(1)
    va, vb, vc = d3 * d6 - d5 * d4, d5 * d2 - d1 * d6, d1 * d4 - d3 * d2
    den = va + vb + vc
    den = np.where(np.abs(den) < 1e-30, 1e-30, den)
    q = a + ab * (vb / den)[:, None] + ac * (vc / den)[:, None]
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.clip(d1 / (d1 - d3), 0, 1)
        q = np.where(((vc <= 0) & (d1 >= 0) & (d3 <= 0))[:, None], a + ab * t[:, None], q)
        t = np.clip(d2 / (d2 - d6), 0, 1)
        q = np.where(((vb <= 0) & (d2 >= 0) & (d6 <= 0))[:, None], a + ac * t[:, None], q)
        t = np.clip((d4 - d3) / ((d4 - d3) + (d5 - d6)), 0, 1)
        q = np.where(((va <= 0) & (d4 - d3 >= 0) & (d5 - d6 >= 0))[:, None], b + (c - b) * t[:, None], q)
    q = np.where(((d1 <= 0) & (d2 <= 0))[:, None], a, q)
    q = np.where(((d3 >= 0) & (d4 <= d3))[:, None], b, q)
    q = np.where(((d6 >= 0) & (d5 <= d6))[:, None], c, q)
    return np.linalg.norm(p - q, axis=1)


def _ball(sa, sb, e, t, target):
    """The center whose distance to both surfaces is `target`, in the plane through `e`
    across `t`, or None where the two surfaces give it no single place."""
    na, nb = sa.normal(e), sb.normal(e)
    if 1.0 + np.dot(na, nb) < 1e-9:
        return None
    c = e + target * (na + nb) / (1.0 + np.dot(na, nb))
    for _ in range(40):
        F = np.array([sa.dist(c) - target, sb.dist(c) - target, np.dot(c - e, t)])
        if np.abs(F).max() < 1e-11:
            return c
        J = np.array([sa.normal(c), sb.normal(c), t])
        try:
            c = c - np.linalg.solve(J, F)
        except np.linalg.LinAlgError:
            return None
    return None


def _neighbours(face):
    t, topo = face.topo.t, face.topo
    out = []
    for i in t.face_edges[face.index]:
        for f in t.edges[i]["faces"]:
            if f != face.index and f not in out:
                out.append(f)
    return [topo.faces[f] for f in out]


def _rolled(edge, R, src, op):
    """The fillet of radius `R` along an edge the prism and revolve tools do not cover.

    At stations along the edge, the ball of radius R that touches both faces is solved on their
    exact surfaces (Newton on the two distances, its center held in the plane across the edge).
    Where a contact runs off its face onto the next one, as it does wherever the face boundary
    meets the edge at a slant, the ball is solved again against the face that holds it. Each
    station gives the arc between the two contacts about the ball's center; the sections are
    ruled into one tool, cut where the corner is convex and filled where it is concave."""
    if edge.closed:
        raise NotImplementedError("meshcad: fillet of a closed curved edge")
    tol = 2 * LINEAR + 1e-6
    pts = edge.pts
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    L = cum[-1]
    h0 = min(0.2, math.sqrt(8 * LINEAR * R) / 2)
    n = max(3, math.ceil(L / h0) + 1)
    s = np.linspace(0.0, L, n)
    st = np.stack([np.interp(s, cum, pts[:, k]) for k in range(3)], 1)
    tan = np.gradient(st, axis=0)
    tan /= np.linalg.norm(tan, axis=1)[:, None]

    fa0, fb0 = edge.faces_of()
    mid = st[n // 2]
    na, ua = _face_side(fa0, edge, mid, tan[n // 2])
    nb, _ = _face_side(fb0, edge, mid, tan[n // 2])
    convex = float(np.dot(ua, nb)) < 0
    target = -R if convex else R
    surfaces = {}

    def surface(face, near):
        if face.index not in surfaces:
            try:
                surfaces[face.index] = _Surface(face, near)
            except NotImplementedError:
                surfaces[face.index] = None
        return surfaces[face.index]

    A, B = surface(fa0, mid), surface(fb0, mid)
    if A is None or B is None:
        raise NotImplementedError(f"meshcad: fillet of a {edge.kind} edge between "
                                  f"{fa0.rec and fa0.rec['kind']} and {fb0.rec and fb0.rec['kind']} faces")
    # Below this angle between the faces the fillet is shallower than the rule's tolerance.
    least = math.sqrt(8 * 0.25 * LINEAR / R)

    def solve(sa, sb, e, t):
        """The ball against `sa` and `sb` at this station, if it sits by the edge and both
        contacts land on their own faces."""
        c = _ball(sa, sb, e, t, target)
        if c is None or np.linalg.norm(c - e) > 3 * R:
            return None
        ca, cb = sa.foot(c), sb.foot(c)
        if not (sa.holds(ca, tol) and sb.holds(cb, tol)):
            return None
        return c, ca, cb

    stations = []
    cur, last = (A, B), None
    for e, t in zip(st, tan):
        if math.acos(np.clip(np.dot(A.normal(e), B.normal(e)), -1, 1)) < least:
            continue
        got = solve(*cur, e, t)
        if got is None:
            # A contact ran off its face: of the neighbouring faces that hold one, the pair
            # whose ball stays nearest the last station's.
            pa = dict.fromkeys([cur[0], A] + [x for x in map(lambda f: surface(f, e), _neighbours(cur[0].face)) if x])
            pb = dict.fromkeys([cur[1], B] + [x for x in map(lambda f: surface(f, e), _neighbours(cur[1].face)) if x])
            near = e if last is None else last
            best = None
            for sa in pa:
                for sb in pb:
                    g = None if sa is sb else solve(sa, sb, e, t)
                    if g is not None and (best is None or np.linalg.norm(g[0] - near)
                                          < np.linalg.norm(best[1][0] - near)):
                        best = (sa, sb), g
            if best is None:
                continue
            cur, got = best
        c, ca, cb = got
        last = c
        u1, u2 = (ca - c) / R, (cb - c) / R
        phi = math.acos(np.clip(np.dot(u1, u2), -1, 1))
        if phi < least:
            continue
        stations.append((c, u1, u2, phi, t))
    if len(stations) < 2:
        return None, convex

    step = 2 * math.pi / ring_count(R)
    m = max(2, math.ceil(max(x[3] for x in stations) / step))
    reach = max(0.25 * R, 0.02) + 0.02
    sections, normals = [], []
    for c, u1, u2, phi, t in stations:
        w = u2 - np.dot(u1, u2) * u1
        w /= np.linalg.norm(w)
        th = np.linspace(0.0, phi, m + 1)
        arc = c + R * (np.cos(th)[:, None] * u1 + np.sin(th)[:, None] * w)
        bis = (u1 + u2) / np.linalg.norm(u1 + u2)
        far = c + bis * (R + reach) / math.cos(phi / 2)
        sec = np.vstack([arc[0] + reach * u1, arc, arc[-1] + reach * u2, far])
        # Where a contact moves onto the next face the ball can set its section down behind
        # the last one, or wound the other way round the edge. Ruled to it, the band turns
        # inside out through the tool, and the cut leaves that fold as surface touching itself.
        if sections and (((sec - sections[-1]) @ t).min() <= 0
                         or np.dot(build._poly_normal(sec), t) * np.dot(build._poly_normal(sections[-1]), t) <= 0):
            continue
        sections.append(sec)
        normals.append((u1, u2))
    if len(sections) < 2:
        return None, convex
    sections = _thinned(sections, normals)
    # A hair past both ends, so the tool overlaps whatever rounds the next edge on.
    ends = []
    for sec, nxt in ((sections[0], sections[1]), (sections[-1], sections[-2])):
        d = sec[1:-3].mean(0) - nxt[1:-3].mean(0)
        ends.append(sec + 0.002 * d / np.linalg.norm(d))
    sections = [ends[0], *sections, ends[1]]
    k = len(sections[0])
    kinds = [["arc" if 1 <= j <= m else "tool" for j in range(k)] for _ in sections[:-1]]
    part = build.ruled(sections, True, src, op, kinds)
    return build.solid(part), convex


def _thinned(sections, normals):
    """Sections dropped wherever the ruled band between their neighbours stays within the
    rule: no point of a dropped section farther than LINEAR from it, no normal turning more
    than ANGULAR across it."""
    keep = [0]
    i = 0
    while i < len(sections) - 1:
        j = i + 1
        while j + 1 < len(sections):
            cand = j + 1
            ok = True
            a, b = sections[i], sections[cand]
            ab = b - a
            for q in range(i + 1, cand):
                ap = sections[q] - a
                t = np.clip((ap * ab).sum(1) / np.maximum((ab * ab).sum(1), 1e-30), 0, 1)
                if np.linalg.norm(ap - ab * t[:, None], axis=1).max() > LINEAR:
                    ok = False
                    break
            if ok:
                for u, v in zip(normals[i], normals[cand]):
                    if math.acos(np.clip(np.dot(u, v), -1, 1)) > ANGULAR:
                        ok = False
            if not ok:
                break
            j = cand
        keep.append(j)
        i = j
    return [sections[k] for k in keep]
