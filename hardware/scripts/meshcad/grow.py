"""A solid grown by a distance along its normals, with round joins: every point within `d`.

OCCT offsets a B-rep face by face and trims the offset faces against each other. On a mesh
the same set is a union of pieces that each lie within `d` of the solid and together reach
everywhere that is: the solid itself; each face's slab, the face moved out along its own
normals to its offset surface; along each edge the wedge of roll between its two faces'
normals; and at each corner the cap of ball over the normals of the faces that meet there.
A face on a plane, cylinder, cone, sphere or torus moves along its surface's exact normal, so
its slab ends on the exact offset surface; any other face moves along its triangles' normals.
Faces that meet tangent all along their edges — a loft's ruled faces, a rounded box's sides —
share their normals there and move out as one slab, with no wall between them.

NO TWO PIECES MEET ON A FACE. A union cancels two faces only when they coincide exactly, and
two pieces built apart never quite do: the slit left between them is a cut through whatever
the grown solid is subtracted from. So each wedge turns a little past both faces' normals and
runs a little past both of its ends, and its sides lie inside the slabs and the next wedge
rather than on them. Every point a wedge adds lies within `d` of its own edge point, so the
overlap never reaches past the grown surface by more than `REACH`² / 2`d`.
"""

import math

import manifold3d as m3d
import numpy as np

from . import build
from .rule import ANGULAR, ring_count

#: Faces whose normals meet within this angle are taken as tangent: they share their mean
#: normal along the edge, so their slabs meet without a step and a thin wedge covers the seam.
SMOOTH = 0.05
#: How far each wedge runs past the ends of its edge, mm.
REACH = 0.02


def offset(shape, d):
    from .solids import MeshCompound, MeshSolid, lift
    solids = [MeshSolid(s.m) for s in lift(shape)._solids()]
    out = [MeshSolid(_grown(s, d)) for s in solids]
    return out[0] if len(out) == 1 else MeshCompound(out)


def _grown(solid, d):
    from .solids import _MeshTopology
    topo = _MeshTopology(solid)
    t = topo.t
    step = 2 * math.pi / ring_count(d)
    normal = _normal_table(topo)

    def normals(face, vids):
        return np.array([normal[face.index, v] for v in vids])

    region = _smooth_regions(topo, normal)
    pieces = [solid.m]
    for faces in region.values():
        pieces.extend(_slab(faces, d, normals))
    within = {f.index: r for r, faces in region.items() for f in faces}
    for edge in topo.edge_objs:
        fa, fb = edge.face_ids
        if within[fa] == within[fb]:
            continue
        w = _wedge(edge, d, step, normals)
        if w is not None:
            pieces.append(w)
    meet = {}
    for e in t.edges:
        for v in (e["verts"][0], e["verts"][-1]):
            meet.setdefault(v, set()).update(e["faces"])
    ball = np.asarray(m3d.Manifold.sphere(1.0, ring_count(d)).to_mesh().vert_properties)[:, :3]
    for v in t.corners:
        c = _cap(topo, v, meet.get(v, ()), d, step, ball, normals)
        if c is not None:
            pieces.append(c)
    return build.boolean(pieces, m3d.OpType.Add)


def _normal_table(topo):
    """{(face index, vertex): outward unit normal}. A face on a plane, cylinder, cone, sphere
    or torus takes its surface's exact normal; any other its triangles' normals, area-weighted.
    Faces that meet within SMOOTH of tangent share the mean of their normals there, as the one
    array: `is` tells a seam's shared normal from two that merely agree."""
    from .fillet import _Surface
    t = topo.t
    raw = {}
    for face in topo.faces:
        vids = np.unique(t.T[face.tris])
        try:
            s = _Surface(face, t.tri_c[face.tris].mean(0))
            n = np.array([s.normal(t.V[v]) for v in vids])
        except NotImplementedError:
            n = _vertex_normals(t, face.tris)[vids]
        for v, nv in zip(vids.tolist(), n):
            raw[face.index, v] = nv
    parent = {k: k for k in raw}

    def root(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    cos_smooth = math.cos(SMOOTH)
    for edge in topo.edge_objs:
        fa, fb = edge.face_ids
        for v in edge.vids:
            if np.dot(raw[fa, v], raw[fb, v]) > cos_smooth:
                a, b = root((fa, v)), root((fb, v))
                if a != b:
                    parent[max(a, b)] = min(a, b)
    groups = {}
    for k in raw:
        groups.setdefault(root(k), []).append(k)
    table = {}
    for members in groups.values():
        n = np.sum([raw[k] for k in members], axis=0)
        n = n / np.linalg.norm(n)
        for k in members:
            table[k] = n
    return table


def _vertex_normals(t, tris):
    """Unit normals at the vertices of `tris`, each triangle's corner weighted by Max's rule —
    the cross product of its two edges over both their squared lengths — so a vertex's short
    edges set its normal. A loft's triangles run the length of a ruling, and an area-weighted
    sum would give the normal halfway along it."""
    T = t.T[tris]
    acc = np.zeros((len(t.V), 3))
    for k in range(3):
        e1 = t.V[T[:, (k + 1) % 3]] - t.V[T[:, k]]
        e2 = t.V[T[:, (k + 2) % 3]] - t.V[T[:, k]]
        w = np.cross(e1, e2) / np.maximum((e1 * e1).sum(1) * (e2 * e2).sum(1), 1e-12)[:, None]
        np.add.at(acc, T[:, k], w)
    size = np.linalg.norm(acc, axis=1)
    return acc / np.where(size > 0, size, 1.0)[:, None]


def _smooth_regions(topo, normal):
    """{region: [faces]}: faces joined across every edge along which they share their normals
    at every vertex. A region whose faces still disagree at some vertex goes face by face."""
    parent = list(range(len(topo.faces)))

    def root(f):
        while parent[f] != f:
            parent[f] = parent[parent[f]]
            f = parent[f]
        return f

    for edge in topo.edge_objs:
        fa, fb = edge.face_ids
        if all(normal[fa, v] is normal[fb, v] for v in edge.vids):
            a, b = root(fa), root(fb)
            if a != b:
                parent[max(a, b)] = min(a, b)
    region = {}
    for face in topo.faces:
        region.setdefault(root(face.index), []).append(face)
    out = {}
    t = topo.t
    for r, faces in region.items():
        seen = {}
        whole = True
        for face in faces:
            for v in np.unique(t.T[face.tris]).tolist():
                n = normal[face.index, v]
                if seen.setdefault(v, n) is not n:
                    whole = False
        if whole:
            out[r] = faces
        else:
            out.update({(r, face.index): [face] for face in faces})
    return out


def _solid_or_none(verts, tris, op="offset"):
    tris = build._fix_winding(verts, np.asarray(tris, np.int64))
    part = build.Part(verts, tris, np.zeros(len(tris), np.int64), [build.record("BSPLINE", None, op)])
    try:
        return build.solid(part)
    except ValueError:
        return None


def _slab(faces, d, normals):
    """The faces swept out to their offset: their triangles, their offsets, and the walls
    between their boundaries. A region whose offset folds over itself goes face by face, and a
    face that folds goes triangle by triangle."""
    t = faces[0].topo.t
    tri = np.concatenate([t.T[f.tris] for f in faces])
    vids, local = np.unique(tri, return_inverse=True)
    local = local.reshape(-1, 3)
    n = len(vids)
    V = t.V[vids]
    owner = {}
    for f in faces:
        for v in np.unique(t.T[f.tris]).tolist():
            owner.setdefault(v, f)
    top = V + d * np.array([normals(owner[v], [v])[0] for v in vids.tolist()])
    e = np.concatenate([local[:, [0, 1]], local[:, [1, 2]], local[:, [2, 0]]])
    key = np.sort(e, 1)
    _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    rim = e[cnt[inv.reshape(-1)] == 1]
    walls = [(a, b, b + n) for a, b in rim] + [(a, b + n, a + n) for a, b in rim]
    m = _solid_or_none(np.vstack([V, top]), np.vstack([local[:, ::-1], local + n,
                                                      np.array(walls, np.int64).reshape(-1, 3)]))
    if m is not None and m.volume() > 0:
        return [m]
    if len(faces) > 1:
        return [x for f in faces for x in _slab([f], d, normals)]
    # Folded: each triangle with its own prism along its own normal, which the edges' wedges
    # and the corners' caps then join.
    out = []
    face = faces[0]
    for k, (a, b, c) in enumerate(t.T[face.tris]):
        p = t.V[[a, b, c]]
        q = p + d * t.tri_n[face.tris[k]]
        prism = _solid_or_none(np.vstack([p, q]),
                               [(2, 1, 0), (3, 4, 5), (0, 1, 4), (0, 4, 3), (1, 2, 5), (1, 5, 4),
                                (2, 0, 3), (2, 3, 5)])
        if prism is not None:
            out.append(prism)
    return out


def _wedge(edge, d, step, normals):
    """The roll between the two faces' offsets along a convex or tangent edge, as sector
    sections lofted along the edge; a closed edge goes round in two halves that overlap."""
    fa, fb = edge.faces_of()
    vids = list(edge.vids)
    if edge.closed:
        h = len(vids) // 2
        a = _wedge_run(vids[:h + 1], fa, fb, d, step, normals)
        b = _wedge_run(vids[h:], fa, fb, d, step, normals)
        parts = [x for x in (a, b) if x is not None]
        return build.boolean(parts, m3d.OpType.Add) if parts else None
    return _wedge_run(vids, fa, fb, d, step, normals)


def _wedge_run(vids, fa, fb, d, step, normals):
    t = fa.topo.t
    P = t.V[vids]
    na, nb = normals(fa, vids), normals(fb, vids)
    ang = np.arccos(np.clip((na * nb).sum(1), -1, 1))
    # Convex where the faces turn away from each other across the edge: the far face's normal
    # points against the way into the near face. A concave edge needs no wedge unless its
    # faces are near tangent, where their slabs' walls would all but coincide.
    # Asked where the normals part most: where they agree, the answer is noise.
    i = int(ang.argmax())
    j = min(i, len(vids) - 2)
    tri = t.T[fa.tris]
    k = fa.tris[np.flatnonzero((tri == vids[j]).any(1) & (tri == vids[j + 1]).any(1))[0]]
    third = next(x for x in t.T[k] if x not in (vids[j], vids[j + 1]))
    along = P[j + 1] - P[j]
    into = t.V[third] - P[i]
    into -= np.dot(into, along) * along / max(np.dot(along, along), 1e-30)
    if np.dot(into, nb[i]) >= 0 and ang.max() >= SMOOTH:
        return None
    seg = np.diff(P, axis=0)
    tan = np.vstack([seg[:1], seg[:-1] + seg[1:], seg[-1:]])
    tan /= np.linalg.norm(tan, axis=1)[:, None]
    side = np.cross(tan, na)
    side /= np.maximum(np.linalg.norm(side, axis=1), 1e-30)[:, None]
    toward = nb - (na * nb).sum(1)[:, None] * na
    size = np.linalg.norm(toward, axis=1)
    turned = ang >= 1e-7
    sense = 1.0 if (np.einsum("ij,ij->i", toward[turned], side[turned]).sum() >= 0) else -1.0
    w = np.where(turned[:, None], toward / np.maximum(size, 1e-30)[:, None], sense * side)
    # Past both normals by at least half a step, and by half the largest turn of either face's
    # normal between two stations: the most the two diagonals of a wall's quad can part.
    turn = max(np.linalg.norm(np.diff(na, axis=0), axis=1).max(initial=0.0),
               np.linalg.norm(np.diff(nb, axis=0), axis=1).max(initial=0.0))
    past = max(step, ANGULAR, turn) / 2
    m = max(1, math.ceil((ang.max() + 2 * past) / step))
    sections = []
    for p, u, v, a in zip(P, na, w, ang):
        th = np.linspace(-past, a + past, m + 1)
        arc = p + d * (np.cos(th)[:, None] * u + np.sin(th)[:, None] * v)
        sections.append(np.vstack([p, arc]))
    sections.insert(0, sections[0] - REACH * tan[0])
    sections.append(sections[-1] + REACH * tan[-1])
    part = build.ruled(sections, True, None, "offset")
    try:
        return build.solid(part)
    except ValueError:
        return None


def _cap(topo, v, faces, d, step, ball, normals):
    """The ball over a corner: every direction within the widest angle between the mean of
    its faces' normals and any one of them, hulled with the corner itself."""
    t = topo.t
    if len(faces) < 2:
        return None
    ns = np.array([normals(topo.faces[f], [v])[0] for f in faces])
    mean = ns.mean(0)
    if np.linalg.norm(mean) < 1e-9:
        dirs = ball
    else:
        mean /= np.linalg.norm(mean)
        half = np.arccos(np.clip(ns @ mean, -1, 1)).max()
        if half < 1e-7:
            return None
        dirs = ball[ball @ mean >= math.cos(min(half + step, math.pi))]
    pts = np.vstack([t.V[v][None], t.V[v] + d * dirs, t.V[v] + d * ns])
    hull = m3d.Manifold.hull_points(pts)
    return hull if hull.volume() > 0 else None
