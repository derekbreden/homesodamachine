"""Faces, edges and vertices read off a Manifold mesh, for CadQuery's selectors.

A face is a connected run of triangles on one surface. Triangles from different cuts that lie
on the same plane or cylinder and touch are one face, as OCCT's `clean()` would leave them.
An edge is a chain of mesh edges between two faces, broken where three or more faces meet,
and it says LINE or CIRCLE when its points are one, with the exact radius and axis the face
records carry.
"""

from collections import defaultdict

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

from .build import REGISTRY
from .rule import LINEAR, canonical_axis

#: CadQuery's names for the surface kinds the builders record.
GEOM = {"PLANE": "PLANE", "CYLINDER": "CYLINDER", "CONE": "CONE", "SPHERE": "SPHERE",
        "TORUS": "TORUS", "EXTRUSION": "EXTRUSION", "REVOLUTION": "REVOLUTION"}


def placed(rec, rt):
    """A face record moved by a Manifold run transform ((4, 3), Manifold's layout)."""
    if rec is None:
        return None
    lin, t = rt[:3].T, rt[3]
    scale = abs(np.linalg.det(lin)) ** (1 / 3)
    out = dict(rec)
    for k in ("p", "c"):
        if k in rec:
            out[k] = lin @ np.asarray(rec[k], float) + t
    if "d" in rec:
        d = lin @ np.asarray(rec["d"], float)
        out["d"] = d / np.linalg.norm(d)
        if "slope" in rec and np.dot(out["d"], lin @ np.asarray(rec["d"], float)) < 0:
            out["slope"] = -rec["slope"]
    if "n" in rec:
        n = np.linalg.inv(lin).T @ np.asarray(rec["n"], float)
        out["n"] = n / np.linalg.norm(n)
    for k in ("r", "R"):
        if k in rec:
            out[k] = rec[k] * scale
    return out


def surface_key(rec, fallback):
    """What two faces must share to be one face: the surface, never where it came from."""
    if rec is None:
        return fallback
    k = rec["kind"]
    if k == "PLANE":
        n = canonical_axis(rec["n"])
        return ("P", *np.round(n, 6), round(float(np.dot(n, rec["p"])), 5))
    if k == "CYLINDER":
        d = canonical_axis(rec["d"])
        p = np.asarray(rec["p"], float)
        foot = p - np.dot(p, d) * d
        return ("C", *np.round(d, 6), *np.round(foot, 4), round(rec["r"], 5))
    if k == "CONE":
        d = np.asarray(rec["d"], float)
        slope = rec["slope"]
        apex = np.asarray(rec["p"], float) - (rec["r"] / slope) * d
        dc = canonical_axis(d)
        return ("K", *np.round(dc, 6), *np.round(apex, 4), round(abs(float(np.arctan(slope))), 6))
    if k == "SPHERE":
        return ("S", *np.round(rec["c"], 4), round(rec["r"], 5))
    if k == "TORUS":
        return ("T", *np.round(canonical_axis(rec["d"]), 6), *np.round(rec["c"], 4),
                round(rec["R"], 5), round(rec["r"], 5))
    return fallback


class Topology:
    """Everything the selectors ask of one Manifold, computed once."""

    def __init__(self, m):
        mesh = m.to_mesh64()
        V = np.asarray(mesh.vert_properties, float)[:, :3]
        T = np.asarray(mesh.tri_verts, np.int64).reshape(-1, 3)
        fid = np.asarray(mesh.face_id, np.int64)
        runs = np.asarray(mesh.run_index, np.int64) // 3
        rids = np.asarray(mesh.run_original_id, np.int64)
        rtf = np.asarray(mesh.run_transform, float).reshape(-1, 4, 3)
        run_of = np.repeat(np.arange(len(rids)), np.diff(runs))
        self.V, self.T = V, T
        a, b, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
        cr = np.cross(b - a, c - a)
        self.tri_area = 0.5 * np.linalg.norm(cr, axis=1)
        with np.errstate(invalid="ignore", divide="ignore"):
            self.tri_n = cr / (2 * self.tri_area[:, None])
        self.tri_n = np.nan_to_num(self.tri_n)
        self.tri_c = (a + b + c) / 3

        # One label per surface; triangles of an unknown source get a plane of their own.
        src_key = run_of * (1 << 32) + fid
        uniq, inv = np.unique(src_key, return_inverse=True)
        labels, recs = {}, []
        src_label = np.empty(len(uniq), np.int64)
        for i, key in enumerate(uniq):
            r, f = int(key >> 32), int(key & 0xFFFFFFFF)
            table = REGISTRY.get(int(rids[r]))
            rec = placed(table[f], rtf[r]) if table is not None and f < len(table) else None
            sk = surface_key(rec, ("X", int(rids[r]), f, r))
            if sk not in labels:
                labels[sk] = len(recs)
                recs.append(rec)
            src_label[i] = labels[sk]
        tri_label = src_label[inv.reshape(-1)]
        unknown = np.array([recs[l] is None for l in tri_label]) if len(tri_label) else np.zeros(0, bool)
        if unknown.any():
            n = self.tri_n[unknown]
            nc = np.where((n[:, :1] < -1e-6) | ((np.abs(n[:, :1]) <= 1e-6) & (n[:, 1:2] < -1e-6))
                          | ((np.abs(n[:, :1]) <= 1e-6) & (np.abs(n[:, 1:2]) <= 1e-6) & (n[:, 2:3] < 0)),
                          -n, n)
            off = np.einsum("ij,ij->i", nc, self.tri_c[unknown])
            pk = np.round(np.concatenate([nc, off[:, None]], 1), 5)
            pu, pinv = np.unique(pk, axis=0, return_inverse=True)
            base = len(recs)
            for row in pu:
                recs.append({"kind": "PLANE", "p": row[3] * row[:3], "n": row[:3], "src": None,
                             "op": "manifold"})
            tri_label = tri_label.copy()
            tri_label[unknown] = base + pinv.reshape(-1)
        self.surface = recs

        # Adjacency across every mesh edge.
        e = T[:, [0, 1, 1, 2, 2, 0]].reshape(-1, 2)
        ks = np.sort(e, 1)
        order = np.lexsort((ks[:, 1], ks[:, 0]))
        kso = ks[order]
        same = (kso[1:] == kso[:-1]).all(1)
        h0, h1 = order[:-1][same], order[1:][same]
        ta, tb = h0 // 3, h1 // 3
        n = len(T)
        ev = kso[1:][same]
        elen = np.linalg.norm(V[ev[:, 0]] - V[ev[:, 1]], axis=1)

        def faces_of(labels):
            join = labels[ta] == labels[tb]
            g = coo_matrix((np.ones(join.sum()), (ta[join], tb[join])), shape=(n, n))
            return connected_components(g, directed=False)[1]

        comp = faces_of(tri_label)
        # A face narrower than the rule's tolerance is no face: a boolean leaves one wherever two
        # surfaces meet at a tangent the rule cut into different points. It joins the neighbour
        # it shares the most boundary with, as OCCT's exact boolean leaves no face there at all.
        if n:
            nf = comp.max() + 1
            ca, cb = comp[ta], comp[tb]
            cut = ca != cb
            area = np.bincount(comp, self.tri_area, nf)
            perim = (np.bincount(ca[cut], elen[cut], nf) + np.bincount(cb[cut], elen[cut], nf))
            thin = np.nonzero((perim > 0) & (2 * area < LINEAR * perim))[0]
            if len(thin):
                is_thin = np.zeros(nf, bool)
                is_thin[thin] = True
                f_, g_ = np.concatenate([ca[cut], cb[cut]]), np.concatenate([cb[cut], ca[cut]])
                w = np.concatenate([elen[cut], elen[cut]])
                mine = is_thin[f_]
                f_, g_, w = f_[mine], g_[mine], w[mine] * np.where(is_thin[g_[mine]], 1e-6, 1.0)
                key, inv = np.unique(f_ * nf + g_, return_inverse=True)
                tot = np.bincount(inv.reshape(-1), w)
                kf, kg = key // nf, key % nf
                order = np.lexsort((-tot, kf))              # each thin face's longest border first
                first = np.r_[True, kf[order][1:] != kf[order][:-1]]
                into = dict(zip(kf[order][first].tolist(), kg[order][first].tolist()))
                face_label = np.zeros(nf, np.int64)
                face_label[comp] = tri_label
                for f, g in into.items():
                    seen = {f}
                    while g in into and g not in seen:     # a thin face beside only thin faces
                        seen.add(g)
                        g = into[g]
                    face_label[f] = face_label[g]
                tri_label = face_label[comp]
                comp = faces_of(tri_label)
        self.tri_face = comp
        self.face_surface = np.zeros(comp.max() + 1 if n else 0, np.int64)
        self.face_surface[comp] = tri_label
        self.face_tris = [None] * len(self.face_surface)
        order_f = np.argsort(comp, kind="stable")
        bounds = np.searchsorted(comp[order_f], np.arange(len(self.face_surface) + 1))
        for f in range(len(self.face_surface)):
            self.face_tris[f] = order_f[bounds[f]:bounds[f + 1]]

        # Edges: chains of mesh edges between two faces.
        cut = comp[ta] != comp[tb]
        bu, bv = kso[1:][same][cut][:, 0], kso[1:][same][cut][:, 1]
        fa, fb = np.minimum(comp[ta][cut], comp[tb][cut]), np.maximum(comp[ta][cut], comp[tb][cut])
        self.edges = _chains(bu, bv, fa, fb, len(V))
        self.face_edges = defaultdict(list)
        for i, ch in enumerate(self.edges):
            self.face_edges[ch["faces"][0]].append(i)
            self.face_edges[ch["faces"][1]].append(i)
        corner = set()
        for ch in self.edges:
            if not ch["closed"]:
                corner.update((ch["verts"][0], ch["verts"][-1]))
        self.corners = sorted(corner)

    def face_record(self, f):
        return self.surface[self.face_surface[f]]


def _chains(bu, bv, fa, fb, nv):
    deg = np.bincount(np.concatenate([bu, bv]), minlength=nv)
    inc = defaultdict(list)
    for i, (u, v) in enumerate(zip(bu.tolist(), bv.tolist())):
        inc[u].append(i)
        inc[v].append(i)
    fa, fb, bu, bv = fa.tolist(), fb.tolist(), bu.tolist(), bv.tolist()
    used = [False] * len(bu)
    chains = []

    def walk(v, e):
        pair = (fa[e], fb[e])
        verts = [v]
        while True:
            used[e] = True
            v = bv[e] if bu[e] == v else bu[e]
            verts.append(v)
            if deg[v] != 2:
                break
            nxt = [x for x in inc[v] if not used[x] and (fa[x], fb[x]) == pair]
            if not nxt:
                break
            e = nxt[0]
        return {"verts": verts, "faces": pair, "closed": verts[0] == verts[-1] and len(verts) > 2}

    for v in sorted(k for k in inc if deg[k] != 2):
        for e in inc[v]:
            if not used[e]:
                chains.append(walk(v, e))
    for e in range(len(bu)):
        if not used[e]:
            chains.append(walk(min(bu[e], bv[e]), e))
    return chains


def classify(pts, closed, recs):
    """('LINE', None) | ('CIRCLE', (center, axis, r)) | ('BSPLINE', None) for a chain."""
    if not closed and len(pts) >= 2:
        a, b = pts[0], pts[-1]
        d = b - a
        L = np.linalg.norm(d)
        if L > 0:
            u = d / L
            rel = pts - a
            dev = np.linalg.norm(rel - np.outer(rel @ u, u), axis=1).max()
            if dev < 1e-6 + 1e-9 * L:
                return "LINE", None
    if len(pts) < 3:
        return "LINE", None
    for rec in recs:
        if rec is None or rec["kind"] not in ("CYLINDER", "CONE", "SPHERE", "TORUS"):
            continue
        d = canonical_axis(rec.get("d", (0, 0, 1)))
        c0 = np.asarray(rec.get("p", rec.get("c")), float)
        rel = pts - c0
        h = rel @ d
        rad = np.linalg.norm(rel - np.outer(h, d), axis=1)
        if np.ptp(h) < 1e-6 and np.ptp(rad) < 1e-5:
            return "CIRCLE", (c0 + h.mean() * d, d, float(rad.mean()))
    # A circle no record names: points on one plane and one radius.
    c = pts.mean(0)
    _, s, vt = np.linalg.svd(pts - c)
    if s[-1] < 1e-6 * max(1.0, s[0]):
        n = vt[2]
        x, y = vt[0], vt[1]
        p2 = np.stack([(pts - c) @ x, (pts - c) @ y], 1)
        A = np.column_stack([2 * p2, np.ones(len(p2))])
        sol, *_ = np.linalg.lstsq(A, (p2 ** 2).sum(1), rcond=None)
        cc = sol[:2]
        r = np.sqrt(sol[2] + cc @ cc)
        if np.abs(np.linalg.norm(p2 - cc, axis=1) - r).max() < 1e-5:
            return "CIRCLE", (c + cc[0] * x + cc[1] * y, canonical_axis(n), float(r))
    return "BSPLINE", None
