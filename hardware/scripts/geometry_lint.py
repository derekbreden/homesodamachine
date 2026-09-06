"""Geometry lint — ranked anomalies read off the printed mesh, after the publish.

Derek finds geometry defects by rotating the /3d view and clicking the edge that
looks wrong. This is the agent's version of that eye: it reads the piece's STL —
the tessellated geometry the slicer reads, the same authority `pick_read.py`
answers from — and prints the places that look wrong, ranked, each as pick text
that pastes straight into the /3d Find box (or back into `pick_read.py`).

Order of operations is part of the contract: publish first, lint second. The
first shape that builds goes to the site so Derek sees it immediately; the lint
is the agent's follow-through while Derek is already looking — never a gate
between an edit and the first look, never wired into the build path. Justify or
fix what it flags; a finding with a reason is a finding answered.

    tools/cad-venv/bin/python hardware/scripts/geometry_lint.py \
        hardware/printed-parts/enclosure/enclosure/enclosure-pump-cartridge.stl

    geometry_lint.py <piece>.stl [<piece2>.stl …] [--top N] [--all] [--classes a,b]

A finding that is intentional gets its reason recorded in
`<piece>.lint-answers` beside the STL — one entry per feature family: a
`[class] reason` line, then pick lines whose points anchor it (one `click:`
per instance). A finding of the same class within `--answer-radius` (default
3 mm) of an anchor point reports as answered and is hidden unless `--all`
shows it with its reason. Geometry that moves away from its anchors
resurfaces as an open finding.

    [sliver] Wago cluster-well ceiling tab — retention ledge; prints as a
    one-sided bridge on the H2C with our settings and filament.
    file: hardware/printed-parts/enclosure/enclosure/enclosure-back-top.step
    click: x=94.200 y=357.088 z=334.300

What it looks for — each class is intent-free, the same epistemic standing as
"watertight"; the design's reasons live with the designer, so the lint only
points, it does not gate:

  step     two parallel same-facing planes, offset by less than a millimeter,
           whose footprints overlap — an edge that could be flush and is not,
           or a feature emerging by a smear (0.25 mm of boss out of a wall).
  sliver   an axis-aligned face that is a strip — long, and thinner than a
           ligament (a 0.1 mm land, a 1.5 mm ledge carrying a plate).
  ceiling  a horizontal down-facing face above air — needs support the corbel
           policy exists to avoid, or is a designed support roof (say which).
  slope    a 45° underside that slopes along its adjacent wall instead of
           rising off it — a Y slope on an X wall.

A `.step` argument is answered from the `.stl` beside it."""

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pick_read import points as pick_points  # noqa: E402
from pick_text import click, file_line, plane_face, straight, _vec  # noqa: E402

#: Facet normals rounded this many decimals share a plane direction.
_NORMAL_DECIMALS = 3
#: Offsets along a shared normal within this many mm are one plane.
_OFFSET_MM = 0.02
#: `step` flags parallel-plane gaps up to this.
_STEP_MAX_MM = 1.0
#: `step` needs this much footprint overlap to call two planes one edge.
_STEP_OVERLAP_MINOR = 0.2
_STEP_OVERLAP_MAJOR = 2.0
#: `sliver` is a strip thinner than this and at least this long.
_SLIVER_MINOR = 1.6
_SLIVER_MAJOR = 4.0
#: `ceiling` ignores faces smaller than this (mm²) or lower than this off the bed.
_CEILING_AREA = 20.0
_CEILING_OFF_BED = 0.5
#: `slope` considers 45-ish undersides at least this big (mm²).
_SLOPE_AREA = 15.0

_CLASSES = ("step", "sliver", "ceiling", "slope")
#: Which way each piece builds along the box's Z. Every coordinate the lint reads and emits
#: stays in the box's own frame; the sign only says which faces look print-down and where the
#: bed is: +1 for a piece bedded on its Z- face, -1 for one bedded on its Z+ face.
PRINT_UP = {"enclosure-back-top": -1.0}


def print_up_of(stl):
    """The build sign for the piece an STL names, +1 unless `PRINT_UP` says otherwise."""
    return PRINT_UP.get(Path(stl).stem, 1.0)


def _basis(n):
    """Two in-plane axes for normal `n`."""
    a = np.array([0.0, 0.0, 1.0]) if abs(n[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    u = np.cross(n, a)
    u /= np.linalg.norm(u)
    return u, np.cross(n, u)


class Plane:
    """One coplanar facet group: normal, offset, member facets, extents."""

    __slots__ = ("n", "o", "f", "mesh", "vids", "bands", "gid", "verts", "area",
                 "uv_lo", "uv_hi", "lo", "hi", "u", "v")

    def __init__(self, n, o, f, mesh, vids, bands=None):
        self.n, self.o, self.f, self.mesh = n, o, f, mesh
        self.vids = vids
        self.bands = bands
        self.gid = -1
        tri = mesh.triangles[f]
        self.verts = tri.reshape(-1, 3)
        self.area = float(mesh.area_faces[f].sum())
        self.lo, self.hi = self.verts.min(axis=0), self.verts.max(axis=0)
        self.u, self.v = _basis(n)
        uv = np.column_stack([self.verts @ self.u, self.verts @ self.v])
        self.uv_lo, self.uv_hi = uv.min(axis=0), uv.max(axis=0)

    def center(self):
        return (self.lo + self.hi) / 2.0

    def thru(self):
        """A point actually on the plane, near the footprint centre."""
        c = self.center()
        return c + self.n * (self.o - float(c @ self.n))

    def soft_frac(self):
        """How much of this plane's boundary folds gently into other groups.

        Chords of a curved or warped surface are bounded almost entirely by
        gentle folds; an authored face is bounded by sharp edges. Fractions
        near 1.0 mean tessellation artefact, not geometry.
        """
        if self.bands is None:
            return 0.0
        soft = float(self.bands[0][self.f].sum())
        sharp = float(self.bands[1][self.f].sum())
        return soft / (soft + sharp) if soft + sharp else 0.0

    def components(self):
        """This plane split into vertex-connected islands, largest first.

        Coplanar faces merge into one group whether or not they touch; a strip
        pinched beside a large face is only visible island by island.
        """
        my = self.vids[self.f]  # (k, 3) global vertex ids
        if len(my) == 1:
            return [self]
        cols, cinv = np.unique(my.ravel(), return_inverse=True)
        k = len(my)
        rows = np.repeat(np.arange(k), 3)
        graph = sp.coo_matrix((np.ones(k * 3), (rows, k + cinv)),
                              shape=(k + len(cols), k + len(cols)))
        n, labels = sp.csgraph.connected_components(graph, directed=False)
        if n == 1:
            return [self]
        parts = [self.f[labels[:k] == lab] for lab in np.unique(labels[:k])]
        planes = [Plane(self.n, self.o, part, self.mesh, self.vids, self.bands)
                  for part in parts if len(part)]
        planes.sort(key=lambda p: -p.area)
        return planes


def band_degrees(mesh, vids, gid, pos):
    """Boundary folds between plane groups, two readings of the same edges.

    Per facet: how much edge length folds gently / sharply into other groups —
    an edge two facets share is a boundary when the facets sit in different
    plane groups; the fold across it is gentle below 20° and sharp above.
    Millimetres of edge, not edge counts — a two-triangle strip has one gentle
    pair per long side, but a hundred times the length of its sharp ends.
    Edges inside one group say nothing and count as neither.

    Per group pair: the total shared boundary length, any fold angle — which
    neighbour a face is mounted on is the one it shares the most edge with.
    """
    f = np.arange(len(mesh.faces))
    edges = np.stack([np.sort(np.stack([vids[:, i], vids[:, (i + 1) % 3]], 1), 1)
                      for i in range(3)]).reshape(-1, 2)
    owner = np.tile(f, 3)
    uniq, inverse, counts = np.unique(edges, axis=0, return_inverse=True,
                                      return_counts=True)
    shared = counts[inverse] == 2
    order = np.argsort(inverse[shared], kind="stable")
    pair = owner[shared][order].reshape(-1, 2)
    ab = pos[uniq[counts == 2]]
    length = np.linalg.norm(ab[:, 0] - ab[:, 1], axis=1)
    level_edge = (np.abs(ab[:, 0, 2] - ab[:, 1, 2])
                  / np.maximum(length, 1e-9)) < 0.3
    cross = gid[pair[:, 0]] != gid[pair[:, 1]]
    pair, length, level_edge = pair[cross], length[cross], level_edge[cross]
    cos = np.einsum("ij,ij->i", mesh.face_normals[pair[:, 0]],
                    mesh.face_normals[pair[:, 1]])
    gentle = cos > np.cos(np.radians(20.0))
    soft = np.zeros(len(f))
    sharp = np.zeros(len(f))
    for col in (0, 1):
        np.add.at(soft, pair[gentle, col], length[gentle])
        np.add.at(sharp, pair[~gentle, col], length[~gentle])

    ga, gb = gid[pair[:, 0]], gid[pair[:, 1]]
    base = int(gid.max() + 1)
    key = np.minimum(ga, gb) * base + np.maximum(ga, gb)
    uniq_key, inv = np.unique(key, return_inverse=True)
    sums = np.bincount(inv, weights=length)
    boundary = {(int(k // base), int(k % base)): float(s)
                for k, s in zip(uniq_key, sums)}

    # The same boundaries, level edges only (|Δz| under 30% of length): the
    # foot a corbel stands on is level; the edges running up its rise are not.
    lvl_sums = np.bincount(inv, weights=length * level_edge,
                           minlength=len(uniq_key))
    level = {(int(k // base), int(k % base)): float(s)
             for k, s in zip(uniq_key, lvl_sums) if s > 0}
    return (soft, sharp), boundary, level


def group_planes(mesh, vids):
    """Every coplanar facet group in `mesh`, keyed by rounded normal.

    Returns ({rounded-normal bytes: [Plane, …]}, per-facet group id) with each
    normal's planes sorted by offset. Curved surfaces tessellate into many
    small single-strip groups; the classes filter by relation, not here.
    """
    nrm = mesh.face_normals
    off = np.einsum("ij,ij->i", nrm, mesh.triangles[:, 0, :])
    key = np.round(nrm, _NORMAL_DECIMALS)
    key[key == 0.0] = 0.0  # -0.0 and 0.0 are one direction
    _, inverse = np.unique(key, axis=0, return_inverse=True)

    order = np.argsort(inverse, kind="stable")
    bounds = np.flatnonzero(np.diff(inverse[order])) + 1
    out = {}
    gid = np.empty(len(nrm), np.int64)
    next_gid = 0
    for run in np.split(order, bounds):
        n = nrm[run[0]]
        o = off[run]
        by_o = run[np.argsort(o, kind="stable")]
        o_sorted = off[by_o]
        splits = np.flatnonzero(np.diff(o_sorted) > _OFFSET_MM) + 1
        planes = []
        for part in np.split(by_o, splits):
            p = Plane(n, float(off[part].mean()), part, mesh, vids)
            gid[part] = p.gid = next_gid
            next_gid += 1
            planes.append(p)
        out[key[run[0]].tobytes()] = planes
    return out, gid


def plane_map(mesh):
    """The mesh's plane groups with boundary-fold degrees attached, and the
    group-to-group shared boundary lengths (all edges, and level edges only)."""
    vids, pos = vertex_ids(mesh)
    planes, gid = group_planes(mesh, vids)
    bands, boundary, level = band_degrees(mesh, vids, gid, pos)
    for group in planes.values():
        for p in group:
            p.bands = bands
    return planes, boundary, level


def vertex_ids(mesh):
    """One id per distinct rounded vertex position: (facets, 3) ids and the
    positions the ids name."""
    flat = np.round(mesh.triangles.reshape(-1, 3), 2)
    pos, inverse = np.unique(flat, axis=0, return_inverse=True)
    return inverse.reshape(-1, 3), pos


def _overlap(a, b):
    """In-plane footprint overlap of two same-normal planes, as (minor, major)."""
    lo = np.maximum(a.uv_lo, b.uv_lo)
    hi = np.minimum(a.uv_hi, b.uv_hi)
    w = hi - lo
    if (w <= 0).any():
        return 0.0, 0.0, None
    centre_uv = (lo + hi) / 2.0
    return float(w.min()), float(w.max()), centre_uv


def find_steps(planes):
    """Parallel same-facing plane pairs a sub-millimetre apart, footprints met.

    Evaluated island by island: coplanar faces merge into one group whether
    or not they touch, and a group's box spans the air between its islands.
    Two groups whose boxes meet are tried island against island, the widest
    met footprint is the finding, and the click is a point of the smaller
    island's own facets nearest the centre of what met — a facet holds the
    click, never the air between two faces.
    """
    neighbours = _neighbour_arrays(planes)
    islands = {}

    def parts(p):
        if p.gid not in islands:
            islands[p.gid] = p.components()
        return islands[p.gid]

    found = []
    for group in planes.values():
        for a, b in zip(group, group[1:]):
            dlt = b.o - a.o
            if not (_OFFSET_MM < dlt <= _STEP_MAX_MM):
                continue
            if min(a.area, b.area) < 0.5:
                continue
            minor, major, _ = _overlap(a, b)
            if minor < _STEP_OVERLAP_MINOR or major < _STEP_OVERLAP_MAJOR:
                continue  # no island pair meets more than its groups do
            for ia, ib, lo, hi in _met_islands(parts(a), parts(b)):
                if min(ia.area, ib.area) < 0.5:
                    continue
                if ia.soft_frac() > 0.75 or ib.soft_frac() > 0.75:
                    continue  # chords of a curved surface, not authored planes
                small = ia if ia.area <= ib.area else ib
                if _banded(small, small, neighbours, allowed=2):
                    continue  # patch of a warped surface — the pair itself is 2
                at = _on_facets(small, lo, hi)
                if at is None:
                    continue  # the boxes met; the facets did not
                w = hi - lo
                minor, major = float(w.min()), float(w.max())
                p = small.u * at[0] + small.v * at[1] + small.n * small.o
                found.append({
                    "class": "step", "score": major / dlt,
                    "line": (f"Δ{dlt:.3f} mm between parallel planes"
                             f" · footprint met {major:.1f} × {minor:.1f} mm"),
                    "pick": [plane_face(_vec(*ia.n), _vec(*ia.thru()), "faceA"),
                             plane_face(_vec(*ib.n), _vec(*ib.thru()), "faceB"),
                             click(_vec(*p))],
                })
                break
    return found


def _met_islands(aa, bb):
    """Island pairs across two same-normal groups whose footprints meet by the
    `_STEP_OVERLAP_*` floors, widest met footprint first, each as
    (island of `aa`, island of `bb`, met uv lo, met uv hi)."""
    a_lo, a_hi = np.array([p.uv_lo for p in aa]), np.array([p.uv_hi for p in aa])
    b_lo, b_hi = np.array([p.uv_lo for p in bb]), np.array([p.uv_hi for p in bb])
    lo = np.maximum(a_lo[:, None, :], b_lo[None, :, :])
    hi = np.minimum(a_hi[:, None, :], b_hi[None, :, :])
    w = hi - lo
    met = ((w.min(axis=2) >= _STEP_OVERLAP_MINOR)
           & (w.max(axis=2) >= _STEP_OVERLAP_MAJOR))
    pairs = np.argwhere(met)
    order = np.argsort(-w.max(axis=2)[met], kind="stable")
    return [(aa[i], bb[j], lo[i, j], hi[i, j]) for i, j in pairs[order]]


def _on_facets(p, lo, hi):
    """A uv point of island `p`'s own facets inside the met footprint (lo, hi):
    the footprint's centre when a facet holds it, else the centroid nearest
    that centre among facets whose centroids the footprint holds. None when
    the footprint holds no facet of `p`."""
    tri = p.mesh.triangles[p.f]
    uv = np.stack([tri @ p.u, tri @ p.v], axis=-1)  # (k, 3, 2)
    c = (lo + hi) / 2.0
    if _holds(uv, c):
        return c
    cen = uv.mean(axis=1)
    inside = (cen >= lo - 1e-6).all(axis=1) & (cen <= hi + 1e-6).all(axis=1)
    if not inside.any():
        return None
    cen = cen[inside]
    return cen[np.argmin(np.linalg.norm(cen - c, axis=1))]


def _holds(uv, c):
    """Whether any 2-D triangle of `uv` (k, 3, 2) holds the point `c`, its
    edges included."""
    def side(p, q):
        return ((q[:, 0] - p[:, 0]) * (c[1] - p[:, 1])
                - (q[:, 1] - p[:, 1]) * (c[0] - p[:, 0]))
    s = np.stack([side(uv[:, 0], uv[:, 1]), side(uv[:, 1], uv[:, 2]),
                  side(uv[:, 2], uv[:, 0])], axis=1)
    return bool(((s >= -1e-9).all(axis=1) | (s <= 1e-9).all(axis=1)).any())


def _banded(c, group, neighbours, allowed=1):
    """True when same-facing planes passing close by `c`'s centre touch its
    box — the signature of a chord band (tessellation of a curve), whether or
    not its edges pair up (T-junction tessellation hides them from
    `band_degrees`). Same-facing means within 25°: a small round's chords fold
    8° or more, while no authored neighbour runs that close to parallel.
    `allowed` is how many matches are legitimate — the plane itself, plus its
    step partner when testing a pair.
    """
    ns, os_, lo, hi = neighbours
    centre = c.thru()
    near = (ns @ group.n > 0.9063) & (np.abs(ns @ centre - os_) < 0.6)
    near &= (lo <= c.hi + 0.05).all(axis=1) & (hi >= c.lo - 0.05).all(axis=1)
    return int(near.sum()) > allowed


def _neighbour_arrays(planes):
    every = [p for group in planes.values() for p in group]
    return (np.array([p.n for p in every]), np.array([p.o for p in every]),
            np.array([p.lo for p in every]), np.array([p.hi for p in every]))


def find_slivers(planes, q_min, s=1.0):
    """Axis-aligned faces that are strips — long and thinner than a ligament.

    Evaluated island by island, so a strip that happens to share a plane with a
    healthy face is still seen on its own.
    """
    neighbours = _neighbour_arrays(planes)
    found = []
    for group in planes.values():
        n = group[0].n
        axis_aligned = abs(abs(n[2]) - 1.0) < 0.01 or abs(n[2]) < 0.01
        if not axis_aligned:
            continue
        for whole in group:
            if s * n[2] < -0.99 and abs(s * whole.o / n[2] - q_min) < 0.05:  # the bed face
                continue
            if whole.soft_frac() > 0.75:
                continue  # chords of a curved surface, not authored planes
            for p in whole.components():
                if _banded(p, whole, neighbours):
                    continue
                w = p.uv_hi - p.uv_lo
                minor, major = float(w.min()), float(w.max())
                if minor > _SLIVER_MINOR or major < _SLIVER_MAJOR or major < 4 * minor:
                    continue
                if p.area < 0.8 * minor * major:  # holes/annuli: bbox is not the strip
                    continue
                axis = p.u if w[0] >= w[1] else p.v
                c = p.thru()
                a, b = c - axis * major / 2.0, c + axis * major / 2.0
                found.append({
                    "class": "sliver", "score": major,
                    "line": f"{minor:.3f} mm strip, {major:.1f} mm long",
                    "pick": [plane_face(_vec(*p.n), _vec(*c)),
                             straight(_vec(*a), _vec(*b)),
                             click(_vec(*c))],
                })
    return found


def find_ceilings(planes, mesh, q_min, s=1.0):
    """Horizontal print-down faces above air, with the drop measured below them in the print.

    `s` is the piece's build sign along the box's Z: a face looks print-down when `s * n[2]`
    is -1, its print height is `s * z`, and the bed is `q_min`, the least print height in
    the piece. Every coordinate reported stays in the box's frame.

    Evaluated island by island: every ceiling in a part shares one or two z
    planes, and only the islands are individual roofs.
    """
    down = [c for group in planes.values() if s * group[0].n[2] < -0.99
            for p in group
            if p.area >= _CEILING_AREA and s * p.o / p.n[2] > q_min + _CEILING_OFF_BED
            and p.soft_frac() <= 0.75
            for c in p.components() if c.area >= _CEILING_AREA]
    if not down:
        return []
    up = s * mesh.face_normals[:, 2] > 0.1
    up_tri = mesh.triangles[up]
    up_lo2, up_hi2 = up_tri[:, :, :2].min(axis=1), up_tri[:, :, :2].max(axis=1)
    up_qhi = (s * up_tri[:, :, 2]).max(axis=1)

    found = []
    for p in down:
        z0 = p.o / p.n[2]                      # the plane's own z, whichever way it looks
        q0 = s * z0
        centers = mesh.triangles_center[p.f]
        samples = centers[:: max(1, len(centers) // 12)][:12]
        gaps = []
        for sample in samples:
            near = ((up_lo2 <= sample[:2]).all(axis=1) & (up_hi2 >= sample[:2]).all(axis=1)
                    & (up_qhi < q0 - 1e-6))
            best = None
            for t in up_tri[near]:
                z = _z_in_triangle(t, sample[:2])
                if z is not None and (best is None or s * z > best):
                    best = s * z
            gaps.append(None if best is None else q0 - best)
        real = [g for g in gaps if g is not None]
        drop = (f"drop {min(real):.1f}–{max(real):.1f} mm to material below"
                if real else f"open to the bed ({q0 - q_min:.1f} mm up)")
        w = p.uv_hi - p.uv_lo
        c = p.thru()
        found.append({
            "class": "ceiling",
            "score": p.area ** 0.5 * (max(real) if real else q0 - q_min),
            "line": (f"{p.area:.0f} mm² flat print-down face at z={z0:.3f}"
                     f" · {w.max():.1f} × {w.min():.1f} mm · {drop}"),
            "pick": [plane_face(_vec(*p.n), _vec(*c)), click(_vec(*c))],
        })
    return found


def _z_in_triangle(t, xy):
    """z of triangle `t`'s plane at `xy`, or None when `xy` is outside it."""
    a, b, c = t[:, :2]
    d = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
    if abs(d) < 1e-12:
        return None
    w1 = ((b[1] - c[1]) * (xy[0] - c[0]) + (c[0] - b[0]) * (xy[1] - c[1])) / d
    w2 = ((c[1] - a[1]) * (xy[0] - c[0]) + (a[0] - c[0]) * (xy[1] - c[1])) / d
    w3 = 1.0 - w1 - w2
    if min(w1, w2, w3) < -1e-6:
        return None
    return float(w1 * t[0, 2] + w2 * t[1, 2] + w3 * t[2, 2])


def find_slopes(planes, boundary, level, s=1.0):
    """45° undersides that run along a wall with no level foot on any wall.

    A corbel that stands on a level foot — a horizontal boundary shared with
    some wall — is not flagged. A slope with no such foot, whose boundary with
    a wall is its own rising edges, hangs sideways along that wall: a slope in
    the wrong axis. The PRV chase's Y hip stood on level jamb feet while its
    corrected X-rise roof stands on a level root; in this class's reading of
    the local mesh the two are mirror images, and both read as grounded.
    """
    slopes, wall_by_gid = [], {}
    for group in planes.values():
        n = group[0].n
        if -0.80 <= s * n[2] <= -0.60:
            slopes.extend(p for p in group if p.area >= _SLOPE_AREA)
        elif abs(n[2]) <= 0.05:
            for p in group:
                wall_by_gid[p.gid] = p
    contact = {}
    for (ga, gb), length in boundary.items():
        for s_gid, w_gid in ((ga, gb), (gb, ga)):
            if w_gid in wall_by_gid:
                lvl = level.get((min(ga, gb), max(ga, gb)), 0.0)
                contact.setdefault(s_gid, []).append((length, lvl, w_gid))
    found = []
    for s in slopes:
        if s.soft_frac() > 0.75:
            continue
        touches = [t for t in contact.get(s.gid, ()) if t[0] >= 0.5]
        if not touches:
            continue
        if any(lvl >= 0.5 for _, lvl, _ in touches):
            continue  # grounded
        length, lvl, w_gid = max(touches)
        w = wall_by_gid[w_gid]
        h = s.n[:2] / (np.linalg.norm(s.n[:2]) or 1.0)
        wh = w.n[:2] / (np.linalg.norm(w.n[:2]) or 1.0)
        if abs(float(h @ wh)) > 0.35:
            continue  # rises across that wall, not along it
        c = s.thru()
        found.append({
            "class": "slope", "score": s.area,
            "line": (f"45° underside runs along a wall with no level foot"
                     f" · slope dir {h[0]:+.2f},{h[1]:+.2f}"
                     f" vs wall n {wh[0]:+.2f},{wh[1]:+.2f}"
                     f" · along {length:.1f} mm · {s.area:.0f} mm²"),
            "pick": [plane_face(_vec(*s.n), _vec(*c), "faceA"),
                     plane_face(_vec(*w.n), _vec(*w.thru()), "faceB"),
                     click(_vec(*c))],
        })
    return found


def parse_answers(text):
    """Entries from answers text: (class, reason, anchor points).

    An entry is a `[class] reason` line — the reason may wrap onto following
    lines — then pick lines whose positions anchor it. Blank lines separate
    entries.
    """
    entries = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [ln.strip() for ln in block.strip().splitlines() if ln.strip()]
        if not lines or not lines[0].startswith("["):
            continue
        cls, _, rest = lines[0].lstrip("[").partition("]")
        reason, picks = [rest.strip()], []
        for line in lines[1:]:
            if line.startswith(("file:", "solid:")) or "x=" in line:
                picks.append(line)
            elif not picks:
                reason.append(line)
        pts = [p for _, p in pick_points("\n".join(picks))]
        if cls.strip() in _CLASSES and pts:
            entries.append((cls.strip(), " ".join(reason).strip(), pts))
    return entries


def split_answered(found, entries, radius):
    """Findings partitioned into (open, [(finding, reason), …]) by anchors."""
    if not entries:
        return list(found), []
    open_, answered = [], []
    for r in found:
        pts = [p for _, p in pick_points("\n".join(r["pick"]))]
        hit = None
        for cls, why, anchors in entries:
            if cls != r["class"]:
                continue
            if any(np.linalg.norm(fp - ap) <= radius
                   for fp in pts for ap in anchors):
                hit = why
                break
        if hit is None:
            open_.append(r)
        else:
            answered.append((r, hit))
    return open_, answered


def lint(stl, classes=_CLASSES):
    """Every finding for the piece at `stl`, most severe first within each class."""
    mesh = trimesh.load(stl, process=False)
    s = print_up_of(stl)
    q_min = float((s * mesh.vertices[:, 2]).min())     # the bed, in print height
    planes, boundary, level = plane_map(mesh)
    finders = {"step": lambda: find_steps(planes),
               "sliver": lambda: find_slivers(planes, q_min, s),
               "ceiling": lambda: find_ceilings(planes, mesh, q_min, s),
               "slope": lambda: find_slopes(planes, boundary, level, s)}
    found = {}
    for name in classes:
        try:
            found[name] = sorted(finders[name](), key=lambda r: -r["score"])
        except Exception as e:  # one class's edge case never hides the others
            found[name] = []
            print(f"  [{name}] lint pass failed: {e}", file=sys.stderr)
    return mesh, found


def report(stl, top, show_all, classes, answer_radius=3.0):
    step = stl.with_suffix("") if stl.suffix == ".stl" else stl
    step = step if step.suffix == ".step" else step.with_suffix(".step")
    mesh, found = lint(stl, classes)
    answers_path = stl.with_suffix(".lint-answers")
    entries = (parse_answers(answers_path.read_text())
               if answers_path.exists() else [])
    opens, answered = {}, []
    for name in classes:
        opens[name], hit = split_answered(found[name], entries, answer_radius)
        answered += hit
    total = sum(len(v) for v in opens.values())
    print(f"{stl.name} · {len(mesh.faces)} printed facets · {total} findings"
          + (f" · {len(answered)} answered" if answered else "")
          + ("" if show_all or total <= top else f" · top {top} (--all for every one)"))
    shown = 0
    for name in classes:
        rows = opens[name] if show_all else opens[name][: max(3, top // len(classes))]
        for r in rows:
            if not show_all and shown >= top:
                break
            shown += 1
            print(f"\n  [{r['class']}] {r['line']}")
            print(f"    {file_line(step)}")
            for line in r["pick"]:
                print(f"    {line}")
    if show_all:
        for r, why in answered:
            print(f"\n  [{r['class']} · answered] {why}")
            print(f"    {r['line']}")
            for line in r["pick"]:
                print(f"    {line}")
    return total


def _selftest():
    """Synthetic sheets, one defect per class, each found and none invented."""
    def sheet(polys):
        v, f = [], []
        for poly in polys:
            i = len(v)
            v += list(poly)
            f += [[i, i + 1 + j, i + 2 + j] for j in range(len(poly) - 2)]
        return trimesh.Trimesh(vertices=np.array(v, float), faces=np.array(f),
                               process=False)

    def planes_of(m):
        return plane_map(m)[0]

    # step: two up-facing squares, 0.25 mm apart, footprints met
    m = sheet([[(0, 0, 10), (20, 0, 10), (20, 20, 10), (0, 20, 10)],
               [(5, 5, 10.25), (15, 5, 10.25), (15, 15, 10.25), (5, 15, 10.25)]])
    got = find_steps(planes_of(m))
    assert len(got) == 1 and "Δ0.250" in got[0]["line"], got

    # step, island by island: two squares 30 mm apart on one plane and a
    # square 0.5 mm above the gap between them — the groups' boxes meet over
    # the gap, no faces do
    low = [[(0, 0, 10), (10, 0, 10), (10, 10, 10), (0, 10, 10)],
           [(40, 0, 10), (50, 0, 10), (50, 10, 10), (40, 10, 10)]]
    over_gap = [(15, -5, 10.5), (35, -5, 10.5), (35, 15, 10.5), (15, 15, 10.5)]
    assert find_steps(planes_of(sheet(low + [over_gap]))) == [], "step over a gap"

    # the same square over one of the two: one step, its click on both faces
    over_one = [(-5, -5, 10.5), (15, -5, 10.5), (15, 15, 10.5), (-5, 15, 10.5)]
    got = find_steps(planes_of(sheet(low + [over_one])))
    assert len(got) == 1 and "Δ0.500" in got[0]["line"], got
    at = dict(pick_points("\n".join(got[0]["pick"])))["click"]
    assert 0 < at[0] < 10 and 0 < at[1] < 10 and abs(at[2] - 10) < 1e-9, at

    # sliver: a 0.5 × 30 strip sharing its plane with a healthy 10 × 30 face —
    # only the island is the strip
    m = sheet([[(0, 0, 5), (30, 0, 5), (30, 0.5, 5), (0, 0.5, 5)],
               [(0, 10, 5), (30, 10, 5), (30, 20, 5), (0, 20, 5)]])
    got = find_slivers(planes_of(m), 0.0)
    assert len(got) == 1 and "0.500 mm strip" in got[0]["line"], got

    # answers: an anchor within radius answers the strip; a wrong class or a
    # far anchor leaves it open
    entries = parse_answers("[sliver] retention tab — prints as a one-sided"
                            " bridge\nclick: x=15.000 y=0.250 z=5.000\n")
    opened, answered = split_answered(got, entries, 3.0)
    assert not opened and len(answered) == 1, (opened, answered)
    assert "one-sided bridge" in answered[0][1], answered
    for miss in ("[step] wrong class\nclick: x=15.000 y=0.250 z=5.000\n",
                 "[sliver] far away\nclick: x=15.000 y=0.250 z=95.000\n"):
        opened, answered = split_answered(got, parse_answers(miss), 3.0)
        assert len(opened) == 1 and not answered, miss

    # ceiling: a down-facing square 15 mm above an up-facing floor
    m = sheet([[(0, 0, 20), (0, 20, 20), (20, 20, 20), (20, 0, 20)],
               [(0, 0, 5), (20, 0, 5), (20, 20, 5), (0, 20, 5)]])
    got = find_ceilings(planes_of(m), m, 0.0)
    assert len(got) == 1 and "drop 15.0" in got[0]["line"], got

    # slope: the bad underside's only wall boundary is its own rising edge in
    # an X wall — no level foot anywhere. The good one stands on a level foot
    # on a Y wall. Only the bad one is flagged.
    wall_x = [(0, 0, 0), (0, 0, 20), (0, 10, 30), (0, 40, 40), (0, 40, 0)]
    bad = [(0, 0, 20), (0, 10, 30), (10, 10, 30), (10, 0, 20)]  # n (0,+.7,-.7)
    wall_y = [(0, 50, 0), (30, 50, 0), (30, 50, 20), (0, 50, 20)]
    good = [(30, 50, 20), (0, 50, 20), (0, 60, 30), (30, 60, 30)]  # n (0,+.7,-.7)
    m = sheet([wall_x, bad, wall_y, good])
    planes, boundary, level = plane_map(m)
    got = find_slopes(planes, boundary, level)
    assert len(got) == 1 and "no level foot" in got[0]["line"], got

    # the corrected PRV roof's shape: a rise standing on a level root in an X
    # wall, with its rising edge in a Y end cap — grounded, no finding
    wall_root = [(0, 0, 0), (0, 20, 0), (0, 20, 20), (0, 0, 20)]
    roof = [(0, 0, 20), (0, 20, 20), (10, 20, 30), (10, 0, 30)]  # n (+.7,0,-.7)
    end_cap = [(0, 0, 0), (0, 0, 20), (10, 0, 30), (10, 0, 0)]
    m2 = sheet([wall_root, roof, end_cap])
    planes2, boundary2, level2 = plane_map(m2)
    assert find_slopes(planes2, boundary2, level2) == [], "grounded roof flagged"

    # THE SAME THREE CLASSES ON A PIECE THAT BUILDS DOWN THE BOX'S Z. Mirror the ceiling sheet
    # in z: the roof looks up in the box and down in the print, and it is found; run right way
    # up under s = -1 the same sheet is a floor over air and is not.
    m = sheet([[(0, 0, -20), (20, 0, -20), (20, 20, -20), (0, 20, -20)],
               [(0, 0, -5), (0, 20, -5), (20, 20, -5), (20, 0, -5)]])
    got = find_ceilings(planes_of(m), m, 5.0, s=-1.0)
    assert len(got) == 1 and "drop 15.0" in got[0]["line"], got
    at = dict(pick_points("\n".join(got[0]["pick"])))["click"]
    assert abs(at[2] + 20.0) < 1e-6, at                       # reported in the box's frame
    # and the right-way-up sheet read under s = -1 trades roles: its floor is the print-down
    # face and the roof is the material below it, so the finding moves to z = 5
    m_up = sheet([[(0, 0, 20), (0, 20, 20), (20, 20, 20), (20, 0, 20)],
                  [(0, 0, 5), (20, 0, 5), (20, 20, 5), (0, 20, 5)]])
    got = find_ceilings(planes_of(m_up), m_up, -20.0, s=-1.0)
    assert len(got) == 1 and "z=5.000" in got[0]["line"] and "drop 15.0" in got[0]["line"], got
    # sliver: the bed face is the strip at the piece's greatest z when s = -1
    m = sheet([[(0, 0, 5), (30, 0, 5), (30, 0.5, 5), (0, 0.5, 5)],
               [(0, 10, 5), (30, 10, 5), (30, 20, 5), (0, 20, 5)]])
    assert find_slivers(planes_of(m), -5.0, s=-1.0) == [], "the bed strip flagged under s=-1"
    # slope: the bad underside mirrored is a bad print-down slope under s = -1
    wall_x = [(0, 0, 0), (0, 0, -20), (0, 10, -30), (0, 40, -40), (0, 40, 0)]
    bad = [(10, 0, -20), (10, 10, -30), (0, 10, -30), (0, 0, -20)]      # n (0,+.7,+.7)
    wall_y = [(0, 50, 0), (30, 50, 0), (30, 50, -20), (0, 50, -20)]
    good = [(30, 60, -30), (0, 60, -30), (0, 50, -20), (30, 50, -20)]   # n (0,+.7,+.7)
    m = sheet([wall_x, bad, wall_y, good])
    planes, boundary, level = plane_map(m)
    got = find_slopes(planes, boundary, level, s=-1.0)
    assert len(got) == 1 and "no level foot" in got[0]["line"], got

    print("selftest: all four classes find their defect and only theirs, both ways up")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pieces", nargs="*", help=".stl (or .step with .stl beside it)")
    ap.add_argument("--top", type=int, default=12, help="findings to show (default 12)")
    ap.add_argument("--all", action="store_true",
                    help="show every finding, answered ones included")
    ap.add_argument("--classes", default=",".join(_CLASSES),
                    help="comma list of: " + ",".join(_CLASSES))
    ap.add_argument("--answer-radius", type=float, default=3.0,
                    help="mm from a .lint-answers anchor that answers a finding")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        _selftest()
        return 0
    if not args.pieces:
        ap.error("name at least one piece (or --selftest)")
    classes = tuple(c for c in args.classes.split(",") if c in _CLASSES)
    for i, piece in enumerate(args.pieces):
        p = Path(piece)
        stl = p if p.suffix == ".stl" else p.with_suffix(".stl")
        if p.suffix == ".step" and not stl.exists():
            stl = Path(str(p)[: -len(".step")] + ".stl")
        if not stl.exists():
            raise SystemExit(f"no STL for {piece}")
        if i:
            print()
        report(stl, args.top, args.all, classes, args.answer_radius)
    return 0


if __name__ == "__main__":
    sys.exit(main())
