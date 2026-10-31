"""Solids built as triangles: prisms, revolutions, boxes, lofts, sweeps and hulls.

Each builder returns a `Part`: vertices, triangles, a face index per triangle, and one record
per face naming the surface it lies on and the generator line that asked for it. `solid()`
hands the part to Manifold under an id of its own, and `REGISTRY` keeps the records under that
id, so every triangle a later boolean keeps can still say which face it belongs to.

Profiles arrive as `Loop`s: closed polygons whose segments each name the curve they came from,
so a profile's arc becomes one cylinder face when extruded and one torus or sphere when
revolved, whatever number of segments the rule cut it into.
"""

import math
from dataclasses import dataclass, field

import manifold3d as m3d
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

from .rule import LINEAR, axis_frame, canonical_axis, ring_angles, ring_count, snap

#: Manifold original id → the face records of the mesh it was built from.
REGISTRY = {}


@dataclass
class Curve:
    """What a profile segment lies on: LINE, CIRCLE (center, axis, r) or another kind."""
    kind: str
    center: np.ndarray = None
    axis: np.ndarray = None
    r: float = 0.0


@dataclass
class Loop:
    pts: np.ndarray                       # (m, 3), closed, first point not repeated
    seg: np.ndarray                       # (m,) index into `curves` of segment i → i+1
    curves: list = field(default_factory=list)


@dataclass
class Part:
    verts: np.ndarray
    tris: np.ndarray
    fids: np.ndarray
    records: list


def record(kind, src, op, **params):
    return {"kind": kind, "src": src, "op": op, **params}


def solid(part):
    """The part as a Manifold, its records kept under the id Manifold tracks it by."""
    oid = m3d.Manifold.reserve_ids(1)
    REGISTRY[oid] = part.records
    tris = np.ascontiguousarray(part.tris, dtype=np.uint64)
    mesh = m3d.Mesh64(vert_properties=np.ascontiguousarray(snap(part.verts)),
                      tri_verts=tris,
                      face_id=np.ascontiguousarray(part.fids, dtype=np.uint64),
                      run_original_id=np.array([oid], dtype=np.uint32),
                      run_index=np.array([0, tris.size], dtype=np.uint64))
    m = m3d.Manifold(mesh)
    if m.status() != m3d.Error.NoError:
        raise ValueError(f"meshcad: {part.records[0].get('op') if part.records else '?'} "
                         f"built an invalid solid ({m.status()}) at "
                         f"{part.records[0].get('src') if part.records else '?'}")
    if m.volume() < 0:
        raise ValueError("meshcad: built an inside-out solid")
    return m


#: mm. Two operands' coordinates closer than this are one coordinate to a boolean (`boolean`).
FUZZ = 1e-8


def boolean(ms, op):
    """Manifold's batch boolean of `ms` under `op`, the operands first made to agree on every
    coordinate they share, and the result without the components that hold nothing.

    ONE COORDINATE, HOWEVER IT WAS COMPUTED. A bracket drawn against a wall at y = face and the
    wall's own face at that y arrive by two float paths — the wall a box built at the origin and
    moved, the bracket drawn where it stands — and differ in their last bits. OCCT takes the two
    as one face, within its tolerance, and fuses the bracket on; Manifold is exact and leaves it
    a nanometre off the wall, a solid of its own. So, axis by axis, an operand's coordinate
    within FUZZ of an earlier operand's is moved onto it before Manifold sees either.

    NOTHING IS KEPT THAT HOLDS NOTHING (`held`)."""
    ms = _agreed(list(ms))
    return held(ms[0] if len(ms) == 1 else m3d.Manifold.batch_boolean(ms, op))


def held(m):
    """`m` without the components thinner on average — twice their volume over their area —
    than the rule resolves. Where faces coincide, Manifold's symbolic perturbation can leave a
    sheet, a needle or a sliver standing apart from the solid; OCCT, working to a tolerance,
    leaves none. A void is a component too, inside out, and one as thick as the rule resolves is
    kept with the solid around it.

    The components are counted off the triangles rather than by Manifold's `decompose`, which
    builds a solid for every one of them: a cut that leaves a thousand crumbs would take
    gigabytes to be told so."""
    mesh = m.to_mesh64()
    T = np.asarray(mesh.tri_verts, np.int64).reshape(-1, 3)
    _last[0] = (m, mesh)
    if not len(T):
        return m
    n, label = connected_components(coo_matrix(
        (np.ones(2 * len(T)), (np.concatenate([T[:, 0], T[:, 1]]), np.concatenate([T[:, 1], T[:, 2]]))),
        shape=(len(mesh.vert_properties),) * 2), directed=False)
    if n == 1:
        return m
    V = np.asarray(mesh.vert_properties)[:, :3]
    a, b, c = (V[T[:, k]] - V.mean(0) for k in range(3))
    cr = np.cross(b - a, c - a)
    part = label[T[:, 0]]
    volume = np.bincount(part, np.einsum("ij,ij->i", a, cr) / 6.0, n)
    area = np.bincount(part, np.linalg.norm(cr, axis=1) / 2.0, n)
    keep = 2.0 * np.abs(volume) >= LINEAR * area
    if keep.all():
        return m
    if not keep.any():
        return m3d.Manifold()
    return _subset(m, mesh, keep[part])


#: The last solid `held` read, and its mesh: the next boolean's first operand, as a rule.
_last = [(None, None)]


def _mesh_of(m):
    return _last[0][1] if _last[0][0] is m else m.to_mesh64()


def _copied(x, dtype):
    return np.array(np.asarray(x), dtype=dtype, copy=True)


def _subset(m, mesh, keep):
    """`m` with only the triangles `keep` marks, its runs and faces as they were."""
    runs = np.asarray(mesh.run_index, np.int64) // 3
    kept = np.concatenate([[0], np.cumsum(keep)])[runs]
    out = m3d.Manifold(m3d.Mesh64(
        vert_properties=_copied(mesh.vert_properties, np.float64),
        tri_verts=_copied(np.asarray(mesh.tri_verts).reshape(-1, 3)[keep], np.uint64),
        run_index=_copied(3 * kept, np.uint64),
        run_original_id=_copied(mesh.run_original_id, np.uint32),
        run_transform=_copied(mesh.run_transform, np.float64).reshape(-1, 4, 3),
        run_flags=_copied(mesh.run_flags, np.uint8),
        face_id=_copied(np.asarray(mesh.face_id)[keep], np.uint64)))
    if out.status() != m3d.Error.NoError:
        raise ValueError(f"meshcad: the solid left after dropping what holds nothing is invalid "
                         f"({out.status()})")
    return out


def _agreed(ms):
    """`ms` with each operand's coordinates, axis by axis, moved onto any earlier operand's
    within FUZZ. An operand nothing moves is handed back as it came."""
    out, seen = [], []
    for m in ms:
        mesh = _mesh_of(m)
        V = np.asarray(mesh.vert_properties)[:, :3]
        if seen and len(V):
            W = _onto(V, seen[0] if len(seen) == 1 else np.concatenate(seen))
            if W is not None:
                m, V = _moved(m, mesh, W), W
        seen.append(V)
        out.append(m)
    return out


def _onto(V, prior):
    """`V` with each coordinate within FUZZ of one in `prior` moved onto the nearest such, axis
    by axis; None when nothing moves. An operand has few distinct coordinates on an axis and the
    solid before it many, so each earlier coordinate is placed among this operand's own."""
    W = None
    for k in range(3):
        own = np.unique(V[:, k])
        x = prior[:, k]
        x = x[(x >= own[0] - FUZZ) & (x <= own[-1] + FUZZ)]
        if not len(x):
            continue
        j = np.searchsorted(own, x)
        i = np.concatenate([np.minimum(j, len(own) - 1), np.maximum(j - 1, 0)])
        x = np.concatenate([x, x])
        d = np.abs(x - own[i])
        near = d <= FUZZ
        if not near.any():
            continue
        i, d, x = i[near], d[near], x[near]
        order = np.lexsort((d, i))                       # nearest first within each own value
        first = order[np.r_[True, np.diff(i[order]) != 0]]
        onto = own.copy()
        onto[i[first]] = x[first]
        if np.array_equal(onto, own):
            continue
        if W is None:
            W = np.array(V, dtype=np.float64)
        W[:, k] = onto[np.searchsorted(own, V[:, k])]
    return W


def _moved(m, mesh, V):
    """`m` with its vertices at `V`, its runs and faces as they were; `m` itself if Manifold will
    not take the moved mesh."""
    copy = _copied
    props = copy(mesh.vert_properties, np.float64)
    props[:, :3] = V
    moved = m3d.Manifold(m3d.Mesh64(
        vert_properties=props, tri_verts=copy(mesh.tri_verts, np.uint64),
        run_index=copy(mesh.run_index, np.uint64),
        run_original_id=copy(mesh.run_original_id, np.uint32),
        run_transform=copy(mesh.run_transform, np.float64).reshape(-1, 4, 3),
        run_flags=copy(mesh.run_flags, np.uint8), face_id=copy(mesh.face_id, np.uint64)))
    return moved if moved.status() == m3d.Error.NoError else m


def _oriented(verts, tris):
    """`tris` wound so the solid's volume is positive."""
    a, b, c = verts[tris[:, 0]], verts[tris[:, 1]], verts[tris[:, 2]]
    vol = np.einsum("ij,ij->i", a, np.cross(b, c)).sum()
    return tris[:, ::-1].copy() if vol < 0 else tris


def plane_frame(normal):
    d, x, y = axis_frame(normal)
    if np.dot(d, normal) < 0:          # the frame's own sense, so CCW means CCW about `normal`
        y = -y
        d = -d
    return d, x, y


def _signed_area(p2):
    x, y = p2[:, 0], p2[:, 1]
    return 0.5 * (np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def _reverse(loop):
    m = len(loop.pts)
    idx = (m - 2 - np.arange(m)) % m
    return Loop(loop.pts[::-1].copy(), loop.seg[idx].copy(), loop.curves)


def cap_triangles(loops2d):
    """Triangles over polygons-with-holes, indices into the loops' concatenated points."""
    tris = m3d.triangulate([np.ascontiguousarray(p, dtype=np.float64) for p in loops2d])
    return np.asarray(tris, dtype=np.int64).reshape(-1, 3)


def orient_loops(loops, normal):
    """Outer loop counterclockwise about `normal`, holes clockwise, all in one frame.
    Returns the loops and their 2D coordinates."""
    _, x, y = plane_frame(normal)
    out, flat = [], []
    for i, lp in enumerate(loops):
        p2 = np.stack([lp.pts @ x, lp.pts @ y], axis=1)
        a = _signed_area(p2)
        if (i == 0) != (a > 0):
            lp = _reverse(lp)
            p2 = p2[::-1].copy()
        out.append(lp)
        flat.append(p2)
    return out, flat


def clean_loop(loop, tol=1e-9):
    """`loop` without zero-length segments."""
    pts, seg = loop.pts, loop.seg
    keep = np.linalg.norm(np.roll(pts, -1, axis=0) - pts, axis=1) > tol
    if keep.all():
        return loop
    return Loop(pts[keep], seg[keep], loop.curves)


def prism(loops, normal, vec, src, op="extrude"):
    """The profile `loops` (outer first, on a plane of `normal`) swept straight along `vec`."""
    vec = np.asarray(vec, float)
    up = normal if np.dot(vec, normal) > 0 else -np.asarray(normal)
    loops, flat = orient_loops([clean_loop(lp) for lp in loops], up)
    base = np.concatenate([lp.pts for lp in loops])
    n = len(base)
    verts = np.concatenate([base, base + vec])
    cap = cap_triangles(flat)
    tris = [cap[:, ::-1], cap + n]
    fids = [np.zeros(len(cap), np.int64), np.ones(len(cap), np.int64)]
    records = [record("PLANE", src, op, p=base[0], n=-up), record("PLANE", src, op, p=base[0] + vec, n=up)]
    curve_face = {}
    off = 0
    for lp in loops:
        m = len(lp.pts)
        i = np.arange(m) + off
        j = (np.arange(m) + 1) % m + off
        quad = np.concatenate([np.stack([i, j, j + n], 1), np.stack([i, j + n, i + n], 1)])
        face = np.empty(m, np.int64)
        for k in range(m):
            key = (id(lp.curves), int(lp.seg[k]))
            if key not in curve_face:
                curve_face[key] = len(records)
                records.append(_side_record(lp.curves[lp.seg[k]], lp.pts[k], lp.pts[(k + 1) % m],
                                            vec, src, op))
            face[k] = curve_face[key]
        tris.append(quad)
        fids.append(np.concatenate([face, face]))
        off += m
    tris = _oriented(verts, np.concatenate(tris))
    return Part(verts, tris, np.concatenate(fids), records)


def _side_record(curve, a, b, vec, src, op):
    if curve.kind == "LINE":
        nrm = np.cross(b - a, vec)
        nn = np.linalg.norm(nrm)
        return record("PLANE", src, op, p=a, n=nrm / nn if nn > 0 else nrm)
    if curve.kind == "CIRCLE" and np.linalg.norm(np.cross(canonical_axis(curve.axis),
                                                           vec / np.linalg.norm(vec))) < 1e-9:
        return record("CYLINDER", src, op, p=curve.center, d=canonical_axis(curve.axis), r=curve.r)
    return record("EXTRUSION", src, op)


def _zipper(a_idx, a_ang, b_idx, b_ang, closed):
    """Triangles joining ring A to ring B, walking both in angle order."""
    out = []
    na, nb = len(a_idx), len(b_idx)
    if na == 1 and nb == 1:
        return out
    end = 2 * math.pi if closed else None
    i = j = 0
    last_i = na if closed else na - 1
    last_j = nb if closed else nb - 1
    if na == 1:
        rng = range(nb) if closed else range(nb - 1)
        return [(a_idx[0], b_idx[(k + 1) % nb], b_idx[k]) for k in rng]
    if nb == 1:
        rng = range(na) if closed else range(na - 1)
        return [(a_idx[k], a_idx[(k + 1) % na], b_idx[0]) for k in rng]
    while i < last_i or j < last_j:
        na_ang = (a_ang[i + 1] if i + 1 < na else end) if i < last_i else math.inf
        nb_ang = (b_ang[j + 1] if j + 1 < nb else end) if j < last_j else math.inf
        if na_ang <= nb_ang:
            out.append((a_idx[i], a_idx[(i + 1) % na], b_idx[j % nb]))
            i += 1
        else:
            out.append((a_idx[i % na], b_idx[(j + 1) % nb], b_idx[j]))
            j += 1
    return out


def revolve(loops, axis_p, axis_d, angle_deg, src, op="revolve"):
    """The profile `loops` (on a plane holding the axis) turned `angle_deg` about the axis
    through `axis_p` along `axis_d`. A full turn puts every ring on the rule's angles."""
    axis_p = np.asarray(axis_p, float)
    turn = math.radians(angle_deg)
    full = abs(abs(angle_deg) - 360.0) < 1e-9
    d, x, y = axis_frame(axis_d)
    sense = 1.0 if np.dot(axis_d, d) > 0 else -1.0
    loops = [clean_loop(lp) for lp in loops]
    rel = np.concatenate([lp.pts for lp in loops]) - axis_p
    t_all = rel @ d
    radial = rel - np.outer(t_all, d)
    far = radial[np.argmax(np.linalg.norm(radial, axis=1))]
    u = far / np.linalg.norm(far)
    phi = math.atan2(np.dot(u, y), np.dot(u, x))
    # The profile in its half-plane, as (radius, height); outer loop CCW there.
    loops2 = []
    for lp in loops:
        r2 = lp.pts - axis_p
        t = r2 @ d
        rad = r2 - np.outer(t, d)
        r = np.where(np.einsum("ij,j->i", rad, u) >= -1e-9, np.linalg.norm(rad, axis=1), -np.linalg.norm(rad, axis=1))
        if (r < -1e-9).any():
            raise ValueError(f"meshcad: revolve profile crosses its axis at {src}")
        loops2.append((lp, np.stack([np.maximum(r, 0.0), t], 1)))
    oriented = []
    for i, (lp, p2) in enumerate(loops2):
        if (i == 0) != (_signed_area(p2) > 0):
            lp = _reverse(lp)
            p2 = p2[::-1].copy()
        oriented.append((lp, p2))
    if full:
        a0, a1 = 0.0, None
    elif sense * turn > 0:
        a0, a1 = phi, phi + abs(turn)
    else:
        a0, a1 = phi - abs(turn), phi
    verts, rings = [], []
    for lp, p2 in oriented:
        lr = []
        for r, t in p2:
            if r <= 1e-9:
                ang = np.array([a0])
            else:
                ang = ring_angles(r, a0, a1) if a1 is not None else ring_angles(r)
            base = len(verts)
            pts = axis_p + t * d + r * (np.cos(ang)[:, None] * x + np.sin(ang)[:, None] * y)
            verts.extend(pts)
            lr.append((np.arange(base, base + len(ang)), ang))
        rings.append(lr)
    verts = np.asarray(verts)
    tris, fids, records = [], [], []
    curve_face = {}
    for (lp, p2), lr in zip(oriented, rings):
        m = len(p2)
        for k in range(m):
            (ia, aa), (ib, ab) = lr[k], lr[(k + 1) % m]
            if len(ia) == 1 and len(ib) == 1:
                continue
            key = (id(lp.curves), int(lp.seg[k]))
            if key not in curve_face:
                curve_face[key] = len(records)
                records.append(_revolve_record(lp.curves[lp.seg[k]], p2[k], p2[(k + 1) % m],
                                               axis_p, d, src, op))
            band = _zipper(ia, aa, ib, ab, full)
            tris.extend(band)
            fids.extend([curve_face[key]] * len(band))
    if not full:
        flat = [p2 for _, p2 in oriented]
        cap = cap_triangles(flat)
        first = np.concatenate([[ring[0][0] for ring in lr] for lr in rings])
        last = np.concatenate([[ring[0][-1] for ring in lr] for lr in rings])
        start_face, end_face = len(records), len(records) + 1
        w0 = np.cross(d, np.cos(a0) * x + np.sin(a0) * y)
        w1 = np.cross(d, np.cos(a1) * x + np.sin(a1) * y)
        records.append(record("PLANE", src, op, p=verts[first[0]], n=-w0))
        records.append(record("PLANE", src, op, p=verts[last[0]], n=w1))
        tris.extend(first[cap])
        fids.extend([start_face] * len(cap))
        tris.extend(last[cap[:, ::-1]])
        fids.extend([end_face] * len(cap))
    tris = np.asarray(tris, np.int64)
    used = np.unique(tris)
    if len(used) != len(verts):            # rings on the axis that no band reached
        remap = -np.ones(len(verts), np.int64)
        remap[used] = np.arange(len(used))
        verts, tris = verts[used], remap[tris]
    tris = _oriented(verts, tris)
    return Part(verts, tris, np.asarray(fids, np.int64), records)


def _revolve_record(curve, a, b, axis_p, d, src, op):
    (r0, t0), (r1, t1) = a, b
    if curve.kind == "LINE":
        if abs(r1 - r0) < 1e-9:
            return record("CYLINDER", src, op, p=axis_p, d=d, r=r0)
        if abs(t1 - t0) < 1e-9:
            return record("PLANE", src, op, p=axis_p + t0 * d, n=d)
        slope = (r1 - r0) / (t1 - t0)
        return record("CONE", src, op, p=axis_p + t0 * d, d=d, r=r0, slope=slope)
    if curve.kind == "CIRCLE":
        rel = curve.center - axis_p
        tc = float(np.dot(rel, d))
        rc = float(np.linalg.norm(rel - tc * d))
        c = axis_p + tc * d
        if rc < 1e-9:
            return record("SPHERE", src, op, c=c, r=curve.r)
        return record("TORUS", src, op, c=c, d=d, R=rc, r=curve.r)
    return record("REVOLUTION", src, op)


def box(origin, xdir, ydir, zdir, lx, ly, lz, src, op="box"):
    o = np.asarray(origin, float)
    ex, ey, ez = (np.asarray(v, float) for v in (xdir, ydir, zdir))
    corners = [o + i * lx * ex + j * ly * ey + k * lz * ez
               for k in (0, 1) for j in (0, 1) for i in (0, 1)]
    verts = np.asarray(corners)
    quads = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
    normals = [-ez, ez, -ey, ey, -ex, ex]
    tris, fids, records = [], [], []
    for f, (a, b, c, e) in enumerate(quads):
        tris += [(a, b, c), (a, c, e)]
        fids += [f, f]
        records.append(record("PLANE", src, op, p=verts[a], n=normals[f]))
    tris = _oriented(verts, np.asarray(tris, np.int64))
    return Part(verts, tris, np.asarray(fids, np.int64), records)


def hull_part(points, src, op="hull"):
    """The convex hull of `points`, one plane face per facet plane."""
    m = m3d.Manifold.hull_points(np.asarray(points, float))
    mesh = m.to_mesh64()
    verts = np.asarray(mesh.vert_properties)[:, :3]
    tris = np.asarray(mesh.tri_verts, np.int64)
    return planar_faces(verts, tris, src, op)


def planar_faces(verts, tris, src, op):
    a, b, c = verts[tris[:, 0]], verts[tris[:, 1]], verts[tris[:, 2]]
    n = np.cross(b - a, c - a)
    norm = np.linalg.norm(n, axis=1)
    flat = norm > 0
    n[flat] /= norm[flat, None]
    off = np.einsum("ij,ij->i", n, a)
    key = np.round(np.concatenate([n, off[:, None]], 1), 6)
    fids = np.full(len(tris), -1, np.int64)
    fids[flat] = np.unique(key[flat], axis=0, return_inverse=True)[1].reshape(-1)
    # A triangle the hull left with no area lies along the edge between the facets beside it,
    # and joins one of them.
    if not flat.all():
        half = np.sort(np.stack([tris, np.roll(tris, -1, 1)], 2).reshape(-1, 2), 1)
        edge = np.unique(half, axis=0, return_inverse=True)[1].reshape(-1)
        pair = (np.argsort(edge, kind="stable") // 3).reshape(-1, 2)
        while (fids < 0).any():
            for x, y in (pair.T, pair.T[::-1]):
                take = (fids[x] < 0) & (fids[y] >= 0)
                fids[x[take]] = fids[y[take]]
    records = [None] * (fids.max() + 1)
    for t in np.flatnonzero(flat):
        if records[fids[t]] is None:
            records[fids[t]] = record("PLANE", src, op, p=a[t], n=n[t])
    return Part(verts, tris, fids, records)


def ruled(sections, closed_ends, src, op="loft", kinds=None):
    """Quads between consecutive sections of equal point count, capped at both ends.

    `sections` are (m, 3) arrays whose points correspond index for index; `kinds[i][k]` names
    the surface of band i, segment k (bands of one kind and index share a face)."""
    m = len(sections[0])
    verts = np.concatenate(sections)
    tris, fids, records = [], [], []
    face_of = {}
    for i in range(len(sections) - 1):
        a0, b0 = i * m, (i + 1) * m
        for k in range(m):
            k1 = (k + 1) % m
            key = kinds[i][k] if kinds else (i, k)
            if key not in face_of:
                face_of[key] = len(records)
                records.append(record("BSPLINE" if not isinstance(key, tuple) or len(key) != 3
                                      else key[0], src, op))
            f = face_of[key]
            tris += [(a0 + k, a0 + k1, b0 + k1), (a0 + k, b0 + k1, b0 + k)]
            fids += [f, f]
    if closed_ends:
        for idx, sec in ((0, sections[0]), (len(sections) - 1, sections[-1])):
            nrm = _poly_normal(sec)
            _, x, y = plane_frame(nrm)
            p2 = np.stack([sec @ x, sec @ y], 1)
            cap = cap_triangles([p2 if _signed_area(p2) > 0 else p2[::-1]])
            if _signed_area(p2) <= 0:
                cap = (m - 1) - cap
            f = len(records)
            records.append(record("PLANE", src, op, p=sec[0], n=nrm))
            tris.extend((cap + idx * m).tolist())
            fids += [f] * len(cap)
    verts = np.asarray(verts)
    tris = np.asarray(tris, np.int64)
    tris = _fix_winding(verts, tris)
    return Part(verts, tris, np.asarray(fids, np.int64), records)


def _poly_normal(p):
    c = p.mean(0)
    n = np.zeros(3)
    for i in range(len(p)):
        n += np.cross(p[i] - c, p[(i + 1) % len(p)] - c)
    return n / np.linalg.norm(n)


def _fix_winding(verts, tris):
    """Triangles wound consistently with their neighbours, then outward."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import breadth_first_order
    e = np.stack([tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]], 1).reshape(-1, 2)
    key = np.sort(e, 1)
    order = np.lexsort((key[:, 1], key[:, 0]))
    ks = key[order]
    same = (ks[1:] == ks[:-1]).all(1)
    a, b = order[:-1][same], order[1:][same]
    ta, tb = a // 3, b // 3
    # two neighbours agree when they walk their shared edge in opposite directions
    agree = (e[a] != e[b]).any(1)
    n = len(tris)
    g = coo_matrix((np.where(agree, 1, 2), (ta, tb)), shape=(n, n)).tocsr()
    g = g + g.T
    flip = np.zeros(n, bool)
    seen = np.zeros(n, bool)
    for start in range(n):
        if seen[start]:
            continue
        order_, pred = breadth_first_order(g, start, directed=False, return_predecessors=True)
        for t in order_:
            seen[t] = True
            p = pred[t]
            if p >= 0:
                flip[t] = flip[p] ^ (g[p, t] == 2)
    tris = np.where(flip[:, None], tris[:, ::-1], tris)
    return _oriented(verts, tris)
