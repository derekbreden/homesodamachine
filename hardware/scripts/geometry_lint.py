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
fix what it flags. A justification is a reason AND the alternatives: the
thicker or larger constructions that would do the same job, and why each is
worse. Thinness is a spectrum — larger is preferred and every thin feature is
a compromise — so `thin` and `ledge` are a ranking of where the piece is
thinnest and smallest, and an answer never takes a place off it.

    tools/cad-venv/bin/python hardware/scripts/geometry_lint.py \
        hardware/printed-parts/enclosure/enclosure/enclosure-pump-cartridge.stl

    geometry_lint.py <piece>.stl [<piece2>.stl …] [--top N] [--all] [--classes a,b]

A finding's answer is recorded in `<piece>.lint-answers` beside the STL — one
entry per feature family: a `[class] reason` line, an `alternatives:` line,
then pick lines whose points anchor it (one `click:` per instance). AN ANSWER
EXPLAINS THE FACE IT NAMES AND NOTHING ELSE: a finding reports as answered
when its own pick point IS an anchor point of an entry of its class, to the
three decimals the pick text carries. A face-class finding is hidden then
unless `--all` shows it with its answer; a `thin` or `ledge` finding keeps
its place in the ranking with the answer printed beside it, and an entry that
names no alternatives prints `alternatives: none recorded`. Nothing near an
anchor inherits that anchor's prose, so a face that moves, or a new face
beside an explained one, comes back open — which is the whole use of the
file. Answering a moved feature means re-anchoring its entry on the face it
now has.

    [sliver] <why this face has to be what it is>
    alternatives: <each thicker or larger construction considered, and why it is worse>
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
  ceiling  a horizontal down-facing face above air — carried by a corbel, by a
           column, or by support that leaves through a stated lane (say which).
  slope    a 45° underside that slopes along its adjacent wall instead of
           rising off it — a Y slope on an X wall.
  thin     material between opposite-facing surfaces at any orientation — a
           fin between touching bores, a skin beside a cut, a knife edge or a
           ridge — ranked thinnest first out to 3 mm across, with no line
           inside that reach where thin becomes fine.
  ledge    a flat face within 30° of facing the bed in the print's pose,
           bounded by edges sharper than 25° and smaller than a ceiling —
           ranked smallest first.

A `.step` argument is answered from the `.stl` beside it."""

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp
import trimesh
from scipy.spatial import cKDTree
from trimesh.triangles import closest_point

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
#: `thin` looks this far across the material. It is how far the lint reads, not a pass line:
#: everything inside it is ranked.
_THIN_REACH = 3.0
#: `thin` samples the surface about this far apart.
_THIN_SPACING = 0.7
#: Facets whose normals are at least 120° apart face each other across material, so a knife
#: edge sharper than 60° reads as thin toward its tip.
_THIN_OPPOSITE = -0.5
#: `thin` bins sample normals over this many directions to search each cone apart.
_THIN_DIRECTIONS = 32
#: `thin` samples this close, in one thickness band, are one place.
_THIN_LINK = 1.5
#: `thin` places a band or less apart whose cores come this close are pieces of one place.
_THIN_GATHER = 2.5
#: `thin` reads thickness in bands that double from here: under 0.05, 0.05–0.1, 0.1–0.2 … mm.
_THIN_BAND0 = 0.05
#: `ledge` reads faces within 30° of facing the bed — the support threshold angle the print
#: profiles carry.
_LEDGE_FACING = float(np.cos(np.radians(30.0)))
#: An anchor answers the point it names. `pick_text.fnum` writes three decimals, so a point
#: written out and read back moves by at most half a thousandth on each axis; this is that
#: round trip and nothing else. It is not a radius, and there is no flag to widen it.
_ANSWER_TOL = 0.002

_CLASSES = ("step", "sliver", "ceiling", "slope", "thin", "ledge")
#: The classes that rank: an answer is printed beside the finding and never hides it.
_RANKED = ("thin", "ledge")
#: Which way each piece builds along the box's Z. Every coordinate the lint reads and emits
#: stays in the box's own frame; the sign only says which faces look print-down and where the
#: bed is: +1 for a piece bedded on its Z- face, -1 for one bedded on its Z+ face.
PRINT_UP = {"enclosure-back-top": -1.0, "enclosure-pump-cap": -1.0, "funnel-mold/core": -1.0,
            "display-cover": -1.0,
            "display-cover-reach-05": -1.0,
            "display-cover-reach-10": -1.0,
            "display-cover-retention-v2": -1.0,
            "display-cover-retention-reach-060": -1.0,
            "display-cover-retention-reach-075": -1.0}


#: Degrees about the box's X a piece leans on the bed, after `PRINT_UP`'s flip. The faucet bases
#: bed on their foot with the -Y edge lifted by `faucet_shell.print_base_build_rot`, which
#: refresh_print_project.py and prepare_vent_prints.py apply as a negative turn about X; these
#: entries mirror it. `ledge` reads it.
PRINT_TILT_X = {"faucet-shell-base": -15.0, "industrial-shell-base": -15.0}


def print_up_of(stl):
    """The build sign for the piece an STL names, +1 unless `PRINT_UP` says otherwise."""
    path = Path(stl)
    return PRINT_UP.get(f"{path.parent.name}/{path.stem}", PRINT_UP.get(path.stem, 1.0))


def print_pose_of(stl):
    """The rotation from the box's frame into the print's: `PRINT_UP`'s flip, then the lean
    `PRINT_TILT_X` gives. Findings still report in the box's frame."""
    path = Path(stl)
    lean = np.radians(PRINT_TILT_X.get(f"{path.parent.name}/{path.stem}",
                                       PRINT_TILT_X.get(path.stem, 0.0)))
    s = print_up_of(stl)
    c, sn = np.cos(lean), np.sin(lean)
    return np.array([[1.0, 0.0, 0.0], [0.0, c, -sn], [0.0, sn, c]]) @ np.diag([1.0, s, s])


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


class _Boxes:
    """The planes' boxes, asked which could touch a given box without reading every plane.

    Boxes are kept in tiers by size, each with a tree of its centres searched out to the
    tier's own largest box, so a chord a tenth of a millimetre long is looked for a tenth of a
    millimetre away; the few boxes past the last tier are read directly.
    """

    TIERS = (0.5, 2.0, 8.0, 32.0)

    def __init__(self, neighbours):
        _, _, lo, hi = neighbours
        self.mid, self.half = (lo + hi) / 2.0, np.linalg.norm(hi - lo, axis=1) / 2.0
        self.tiers, low = [], 0.0
        for top in self.TIERS:
            members = np.flatnonzero((self.half > low) & (self.half <= top)
                                     if low else self.half <= top)
            if len(members):
                self.tiers.append((top, members, cKDTree(self.mid[members])))
            low = top
        self.big = np.flatnonzero(self.half > low)

    def near(self, lo, hi, pad):
        """Planes whose boxes could reach within `pad` of the box (`lo`, `hi`)."""
        mid, half = (lo + hi) / 2.0, float(np.linalg.norm(hi - lo)) / 2.0
        found = [members[tree.query_ball_point(mid, half + top + pad)]
                 for top, members, tree in self.tiers]
        far = np.linalg.norm(self.mid[self.big] - mid, axis=1) <= half + self.half[self.big] + pad
        return np.concatenate(found + [self.big[far]]).astype(np.int64)


def _banded(c, group, neighbours, allowed=1, split_ok=False, among=None):
    """True when same-facing planes passing close by `c`'s centre touch its
    box — the signature of a chord band (tessellation of a curve), whether or
    not its edges pair up (T-junction tessellation hides them from
    `band_degrees`). Same-facing means within 25°: a small round's chords fold
    8° or more, while no authored neighbour runs that close to parallel.
    `allowed` is how many matches are legitimate — the plane itself, plus its
    step partner when testing a pair. `split_ok` stops counting the planes
    coplanar with `c` — one flat face whose facets rounded to neighbouring
    normals — so only a fold of 2° or more makes a band. `among` limits the
    reading to those planes (`_Boxes.near`), when every other could not touch.
    """
    ns, os_, lo, hi = neighbours
    if among is not None:
        ns, os_, lo, hi = ns[among], os_[among], lo[among], hi[among]
    centre = c.thru()
    near = (ns @ group.n > 0.9063) & (np.abs(ns @ centre - os_) < 0.6)
    near &= (lo <= c.hi + 0.05).all(axis=1) & (hi >= c.lo - 0.05).all(axis=1)
    if split_ok:
        same = ((ns @ group.n > np.cos(np.radians(2.0)))
                & (np.abs(ns @ centre - os_) < 2 * _OFFSET_MM))
        return int((near & ~same).sum()) > allowed - 1
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
                w = p.uv_hi - p.uv_lo
                minor, major = float(w.min()), float(w.max())
                if minor > _SLIVER_MINOR or major < _SLIVER_MAJOR or major < 4 * minor:
                    continue
                if p.area < 0.8 * minor * major:  # holes/annuli: bbox is not the strip
                    continue
                if _banded(p, whole, neighbours):
                    continue  # only a plausible strip needs the all-plane comparison
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


def surface_samples(mesh, spacing=_THIN_SPACING):
    """Points covering every facet about `spacing` apart: (points, facet of each, the area each
    stands for).

    Laid in columns along each facet's longest edge, then up each column, so a long chord of a
    curved surface is covered end to end and not only where it is wide. A sliver gets columns
    for its area, as long as that leaves one every three spacings of its length: its neighbours
    in the same fan cover the strip it runs along, and the search reaches past its gaps. A
    needle under a micron high gets no samples: the STL's single-precision corners leave its
    normal pointing anywhere.
    """
    tri = mesh.triangles
    edge = np.linalg.norm(tri - np.roll(tri, -1, axis=1), axis=2)  # edge i runs vertex i → i+1
    first = edge.argmax(axis=1)
    rows = np.flatnonzero(2.0 * mesh.area_faces > 1e-3 * edge.max(axis=1))
    first = first[rows]
    a = tri[rows, first]
    b = tri[rows, (first + 1) % 3]
    c = tri[rows, (first + 2) % 3]
    base = edge[rows, first]
    along = (b - a) / np.maximum(base, 1e-12)[:, None]
    foot = np.einsum("ij,ij->i", c - a, along)       # where the apex stands over the base
    rise = c - a - foot[:, None] * along
    height = np.linalg.norm(rise, axis=1)
    up = rise / np.maximum(height, 1e-12)[:, None]

    area = mesh.area_faces[rows]
    cols = np.maximum(1, np.rint(np.maximum(np.minimum(base / spacing, area / spacing ** 2),
                                            base / (3.0 * spacing)))).astype(np.int64)
    col_of = np.repeat(np.arange(len(rows)), cols)  # each column's facet, by position in `rows`
    k = np.arange(len(col_of)) - np.repeat(np.cumsum(cols) - cols, cols)
    u = (k + 0.5) * base[col_of] / cols[col_of]
    ft, bs = foot[col_of], base[col_of]
    frac = np.where(u <= ft, u / np.maximum(ft, 1e-12), (bs - u) / np.maximum(bs - ft, 1e-12))
    h = np.clip(frac, 0.0, 1.0) * height[col_of]     # the facet's height at u
    per = np.maximum(1, np.rint(h / spacing)).astype(np.int64)
    col = np.repeat(np.arange(len(col_of)), per)
    j = np.arange(len(col)) - np.repeat(np.cumsum(per) - per, per)
    v = (j + 0.5) * h[col] / per[col]
    at = col_of[col]
    pts = a[at] + u[col, None] * along[at] + v[:, None] * up[at]
    share = area / np.bincount(at, minlength=len(rows))
    return pts, rows[at], share[at]


def material_thickness(mesh, pts, facet, reach=_THIN_REACH):
    """Per sample, how far across the material its surface is from an opposite-facing facet,
    and the point on that facet it measures to — inf and nan past `reach`.

    Closest approach, not a ray: a ray must land on the one facet straight across, and on a
    finely tessellated far wall the samples nearest a point are seldom that facet's. A candidate
    counts when its facet faces back at least 120° from the sample's and each surface lies
    behind the other — material between them, not air, which is what tells a 0.3 mm wall from a
    0.3 mm slot. The distance is to the facet itself, so a large facet sampled `_THIN_SPACING`
    apart still measures to the point straight across.

    Candidates are searched per direction: the samples are binned by normal over
    `_THIN_DIRECTIONS` directions, and a sample looks only among samples whose normals lie in the
    cone that can face back 120° from its bin — so its own surface and the walls square to it
    never crowd the nearest few, and every facet inside the cone competes on distance alone. A
    sample whose nearest few are all air — the far side of a slot in front of it — searches
    again from half the reach inside the material, where any wall behind it sits closer than the
    slot. Only candidates that can still beat the nearest sample-to-sample reading are measured
    to their facets.

    The readings are surest at the thin end. A knife edge reads as thin as the sample nearest its
    edge, and a far wall all of whose samples stand past the search is missed, which happens
    toward the thick end of the reach.
    """
    n = mesh.face_normals[facet]
    thick = np.full(len(pts), np.inf)
    meet = np.full((len(pts), 3), np.nan)
    dirs = _directions(_THIN_DIRECTIONS)
    home = np.argmax(n @ dirs.T, axis=1)
    # the widest a bin runs from its direction, so its cone holds every candidate of every member
    spread = float(np.arccos(np.clip((n * dirs[home]).sum(axis=1), -1.0, 1.0)).max())
    cone = np.cos(min(np.pi, np.arccos(-_THIN_OPPOSITE) + spread))
    for d in range(len(dirs)):
        mine = np.flatnonzero(home == d)
        cand = np.flatnonzero(n @ dirs[d] < -cone)
        if not len(mine) or not len(cand):
            continue
        tree = cKDTree(pts[cand], balanced_tree=False, compact_nodes=False)
        _thickness_from(tree, cand, mine, mesh, pts, facet, n, reach, thick, meet)
    far = thick > reach
    thick[far], meet[far] = np.inf, np.nan
    return thick, meet


def _directions(count):
    """`count` directions spread evenly over the sphere."""
    i = np.arange(count) + 0.5
    polar = np.arccos(1.0 - 2.0 * i / count)
    turn = np.pi * (1.0 + 5.0 ** 0.5) * i
    return np.column_stack([np.cos(turn) * np.sin(polar), np.sin(turn) * np.sin(polar),
                            np.cos(polar)])


def _thickness_from(tree, cand, mine, mesh, pts, facet, n, reach, thick, meet):
    """`material_thickness` for the samples `mine`, against the candidates `tree` holds: from
    the sample itself, then from half the reach inside for those whose nearest were all air."""
    todo = mine
    for inset, k in ((0.0, 16), (reach / 2.0, 64)):
        k = min(k, len(cand))
        # past the reach by the most a sliver's samples stand off its nearest point
        bound = float(np.hypot(reach, inset)) + 1.5 * _THIN_SPACING
        step = max(1, 400000 // k)
        again = []
        for lo in range(0, len(todo), step):
            sel = todo[lo:lo + step]
            # every core: the lint holds the build lock, so nothing else is running
            dist, nb = tree.query(pts[sel] - inset * n[sel], k=k, distance_upper_bound=bound,
                                  workers=-1)
            dist, nb = dist.reshape(len(sel), k), nb.reshape(len(sel), k)
            row, col = np.nonzero(np.isfinite(dist))
            other = cand[nb[row, col]]
            ni, nj = n[sel[row]], n[other]
            p = pts[sel[row]]
            v = p - pts[other]
            coarse = ((np.einsum("ij,ij->i", ni, nj) < _THIN_OPPOSITE)
                      & (np.einsum("ij,ij->i", v, ni) >= -_THIN_SPACING)
                      & (np.einsum("ij,ij->i", v, nj) <= _THIN_SPACING))
            apart = np.linalg.norm(v, axis=1)
            nearest = np.full(len(sel), np.inf)
            np.minimum.at(nearest, row[coarse], apart[coarse])
            keep = coarse & (apart <= nearest[row] + _THIN_SPACING)
            row, other, p, ni = row[keep], other[keep], p[keep], ni[keep]
            q = closest_point(mesh.triangles[facet[other]], p)
            gap = p - q
            across = ((np.einsum("ij,ij->i", gap, ni) >= -1e-9)
                      & (np.einsum("ij,ij->i", gap, n[other]) <= 1e-9))
            row, q = row[across], q[across]
            length = np.linalg.norm(gap[across], axis=1)
            if len(row):
                order = np.lexsort((length, row))
                first = order[np.r_[True, row[order][1:] != row[order][:-1]]]
                thick[sel[row[first]]] = length[first]
                meet[sel[row[first]]] = q[first]
            # nothing across yet, and the k nearest ran out inside the bound
            full = np.isfinite(dist[:, -1])
            again.append(sel[~np.isfinite(thick[sel]) & full])
        todo = np.concatenate(again)
        if not len(todo):
            break


def thin_places(pts, thick, link=_THIN_LINK, gather=_THIN_GATHER):
    """Where the material is thin, one entry per place, thinnest first: (the sample where it is
    thinnest, the samples of the place, the band edge the place reaches up to, its pieces).

    Thickness is read in bands that double from `_THIN_BAND0`. Samples within `link` of each
    other in one band are one region. A region that touches no thinner band is a place, and the
    regions one band thicker that touch it are its surroundings, counted with it. A fin between
    touching bores is one place along the line where they meet, not the whole wall it thickens
    into, and a wall's own thinnest stretch is a place of its own.
    """
    thin = np.flatnonzero(np.isfinite(thick))
    if not len(thin):
        return []
    t = thick[thin]
    band = np.where(t < _THIN_BAND0, 0,
                    np.floor(np.log2(np.maximum(t, _THIN_BAND0) / _THIN_BAND0)).astype(np.int64)
                    + 1)
    pairs = cKDTree(pts[thin]).query_pairs(link, output_type="ndarray")
    a, b = pairs[:, 0], pairs[:, 1]
    same = band[a] == band[b]
    graph = sp.coo_matrix((np.ones(int(same.sum())), (a[same], b[same])),
                          shape=(len(thin), len(thin)))
    count, region = sp.csgraph.connected_components(graph, directed=False)
    level = np.zeros(count, np.int64)
    level[region] = band
    ra, rb = region[a[~same]], region[b[~same]]
    thicker = np.where(level[ra] > level[rb], ra, rb)
    thinner = np.where(level[ra] > level[rb], rb, ra)
    surrounded = np.zeros(count, bool)
    surrounded[thicker] = True                        # touches a thinner band
    least = np.full(count, np.inf)
    np.minimum.at(least, region, t)
    # each surrounding region joins the thinnest place one band below it that it touches
    step = (level[thicker] == level[thinner] + 1) & ~surrounded[thinner]
    out, into = thicker[step], thinner[step]
    joins = {}
    if len(out):
        order = np.lexsort((least[into], out))
        first = order[np.r_[True, out[order][1:] != out[order][:-1]]]
        joins = dict(zip(out[first].tolist(), into[first].tolist()))
    by_place = {}
    for out, into in joins.items():
        by_place.setdefault(into, []).append(out)
    order = np.argsort(region, kind="stable")
    starts = np.searchsorted(region[order], np.arange(count + 1))
    roots = np.flatnonzero(~surrounded)
    owns = [order[starts[r]:starts[r + 1]] for r in roots]

    # one feature in pieces — a fin broken where its bores cut through each other — is one
    # place: roots a band or less apart whose own samples come within `gather` are gathered
    lo = np.array([pts[thin[o]].min(axis=0) for o in owns])
    hi = np.array([pts[thin[o]].max(axis=0) for o in owns])
    lv = level[roots]
    near = []
    for i in range(0, len(roots), 512):              # boxes within reach, a block of rows at a time
        gap = np.maximum(lo[i:i + 512, None, :] - hi[None, :, :],
                         lo[None, :, :] - hi[i:i + 512, None, :]).max(axis=2)
        a_, b_ = np.nonzero((gap <= gather) & (np.abs(lv[i:i + 512, None] - lv[None, :]) <= 1))
        near.extend((int(x + i), int(y)) for x, y in zip(a_, b_) if x + i < y)
    parent = np.arange(len(roots))

    def top(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for i, j in near:
        if top(i) == top(j):
            continue
        d, _ = cKDTree(pts[thin[owns[i]]]).query(pts[thin[owns[j]]], k=1,
                                                distance_upper_bound=gather)
        if np.isfinite(d).any():
            parent[top(j)] = top(i)
    families = {}
    for i in range(len(roots)):
        families.setdefault(top(i), []).append(i)

    places = []
    for group in families.values():
        own = np.concatenate([owns[i] for i in group])
        rims = [o for i in group for o in by_place.get(roots[i], [])]
        members = np.concatenate([own] + [order[starts[o]:starts[o + 1]] for o in rims])
        at = own[np.argmin(t[own])]
        upto = min(_THIN_REACH, _THIN_BAND0 * 2.0 ** (max(level[roots[i]] for i in group)
                                                      + (1 if rims else 0)))
        places.append((int(thin[at]), thin[members], upto, len(group)))
    places.sort(key=lambda place: thick[place[0]])
    return places


def find_thin(mesh):
    """Material between opposite-facing surfaces, thinnest place first."""
    pts, facet, share = surface_samples(mesh)
    thick, meet = material_thickness(mesh, pts, facet)
    found = []
    for at, members, upto, pieces in thin_places(pts, thick):
        span = pts[members].max(axis=0) - pts[members].min(axis=0)
        pick = [click(_vec(*pts[at]))]
        if thick[at] >= 0.0005:                       # the far side, unless it prints as this one
            pick.append(click(_vec(*meet[at])))
        found.append({
            "class": "thin", "score": -float(thick[at]),
            "line": (f"{thick[at]:.3f} mm of material at its thinnest"
                     f" · {share[members].sum():.1f} mm² of surface under {upto:g} mm"
                     f" · spans {span[0]:.1f} × {span[1]:.1f} × {span[2]:.1f} mm"
                     + (f" · in {pieces} pieces" if pieces > 1 else "")),
            "pick": pick,
        })
    return found


def _facets_touching(vids):
    """Which facets share a vertex, as a sparse facet × facet matrix."""
    count = len(vids)
    rows = np.repeat(np.arange(count), 3)
    incidence = sp.csr_matrix((np.ones(count * 3), (rows, vids.ravel())),
                              shape=(count, int(vids.max()) + 1))
    return (incidence @ incidence.T).tocsr()


def _gently_folded(mesh, touching):
    """Per facet: whether a facet sharing one of its vertices folds 2–25° from it — a chord of a
    curved surface, the way `_banded` reads one, found for every facet at once."""
    pairs = touching.tocoo()
    a, b = pairs.row, pairs.col
    cos = np.einsum("ij,ij->i", mesh.face_normals[a], mesh.face_normals[b])
    gentle = (cos > 0.9063) & (cos < np.cos(np.radians(2.0)))
    out = np.zeros(touching.shape[0], bool)
    out[a[gentle]] = True
    return out


def _whole_face(p, every, neighbours):
    """Island `p` with the coplanar islands it touches — one flat face whose facets rounded to
    neighbouring normals or offsets, so `group_planes` split it — grown until nothing more
    joins."""
    ns, os_, lo, hi = neighbours
    near = np.flatnonzero((ns @ p.n > np.cos(np.radians(2.0)))
                          & (np.abs(ns @ p.thru() - os_) < 2 * _OFFSET_MM))
    face = p
    while True:
        touch = near[(lo[near] <= face.hi + 0.05).all(axis=1)
                     & (hi[near] >= face.lo - 0.05).all(axis=1)]
        facets = np.unique(np.concatenate([face.f] + [every[k].f for k in touch]))
        if len(facets) == len(face.f):
            return face                               # nothing more touches it
        grown = Plane(p.n, p.o, facets, p.mesh, p.vids, p.bands)
        joined = next(i for i in grown.components() if np.isin(p.f[0], i.f))
        if len(joined.f) == len(face.f):
            return face                               # what touched its box is not joined to it
        face = joined


def find_ledges(planes, mesh, pose):
    """Flat faces within 30° of facing the bed, bounded by edges sharper than 25° and smaller
    than a ceiling, smallest first.

    `pose` turns the box's frame into the print's (`print_pose_of`); the bed is the lowest point
    of the piece in that pose. Every coordinate reported stays in the box's frame.
    """
    q_min = float((mesh.vertices @ pose.T)[:, 2].min())
    centers = mesh.triangles_center
    neighbours = _neighbour_arrays(planes)
    boxes = _Boxes(neighbours)
    every = [p for group in planes.values() for p in group]
    touching = _facets_touching(every[0].vids) if every else None
    chord = _gently_folded(mesh, touching) if every else None
    islands = []
    for group in planes.values():
        facing = float((pose @ group[0].n)[2])
        if facing > -_LEDGE_FACING:
            continue
        for whole in group:
            if whole.soft_frac() > 0.75:
                continue  # chords of a curved surface, not authored planes
            islands += [(p, whole, facing) for p in whole.components()
                        if p.soft_frac() <= 0.75 and not chord[p.f].any()]
    seen = set()
    found = []
    for p, whole, facing in islands:
        if _banded(p, whole, neighbours, split_ok=True, among=boxes.near(p.lo, p.hi, 0.05)):
            continue  # a patch of a curved or warped surface
        p = _whole_face(p, every, neighbours)
        if int(p.f.min()) in seen:
            continue  # a face already read through another of its islands
        seen.add(int(p.f.min()))
        if p.area >= _CEILING_AREA:
            continue  # a ceiling's to read
        up = float((p.verts @ pose.T)[:, 2].min()) - q_min
        if up < _CEILING_OFF_BED:
            continue  # on the bed
        w = p.uv_hi - p.uv_lo
        if p.area / max(float(w.max()), 1e-9) < 0.01:
            continue  # narrower than the 0.01 mm `vertex_ids` rounds to — a facet sliver
        outside = np.setdiff1d(touching[p.f].indices, p.f)
        if (mesh.face_normals[outside] @ p.n > 0.9063).any():
            continue  # it runs on into a curve: a ledge is bounded by edges sharper than 25°
        c = centers[p.f]
        at = c[np.argmin(np.linalg.norm(c - p.center(), axis=1))]
        found.append({
            "class": "ledge", "score": -p.area,
            "line": (f"{p.area:.2f} mm² flat face"
                     f" {np.degrees(np.arccos(min(1.0, -facing))):.0f}° off facing"
                     f" the bed · {w.max():.1f} × {w.min():.1f} mm · {up:.1f} mm up"),
            "pick": [plane_face(_vec(*p.n), _vec(*at)), click(_vec(*at))],
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
            if line.lower().startswith("alternatives:"):
                reason.append(line)
            elif line.startswith(("file:", "solid:")) or "x=" in line:
                picks.append(line)
            elif not picks:
                reason.append(line)
        pts = [p for _, p in pick_points("\n".join(picks))]
        if cls.strip() in _CLASSES and pts:
            entries.append((cls.strip(), " ".join(reason).strip(), pts))
    return entries


def split_answered(found, entries):
    """Findings partitioned into (open, [(finding, reason), …]) by anchors.

    An entry answers a finding of its class whose own pick point is one of the entry's anchor
    points. Proximity is not a relationship: a face beside an explained face is a face nobody
    has explained, and it belongs in the open list where it can be looked at."""
    if not entries:
        return list(found), []
    open_, answered = [], []
    for r in found:
        pts = [p for _, p in pick_points("\n".join(r["pick"]))]
        hit = None
        for cls, why, anchors in entries:
            if cls != r["class"]:
                continue
            if any(np.linalg.norm(fp - ap) <= _ANSWER_TOL
                   for fp in pts for ap in anchors):
                hit = why
                break
        if hit is None:
            open_.append(r)
        else:
            answered.append((r, hit))
    return open_, answered


def answered_in_place(found, entries):
    """`split_answered` for a ranked class: every finding stays, in rank order, and an answered
    one carries its answer under "answer"."""
    open_, answered = split_answered(found, entries)
    for r, why in answered:
        r["answer"] = why
    return sorted(open_ + [r for r, _ in answered], key=lambda r: -r["score"])


def split_alternatives(why):
    """An answer's reason, and the alternatives it records ("" when it names none)."""
    parts = re.split(r"(?i)\balternatives:\s*", why, maxsplit=1)
    return parts[0].strip(), (parts[1].strip() if len(parts) > 1 else "")


def _print_answer(why, lead):
    reason, alternatives = split_alternatives(why)
    print(f"{lead}{reason}")
    print(f"    alternatives: {alternatives or 'none recorded'}")


def lint(stl, classes=_CLASSES):
    """Every finding for the piece at `stl`, most severe first within each class."""
    mesh = trimesh.load(stl, process=False)
    s = print_up_of(stl)
    q_min = float((s * mesh.vertices[:, 2]).min())     # the bed, in print height
    planes = boundary = level = None
    if any(name != "thin" for name in classes):        # `thin` reads facets, not planes
        planes, boundary, level = plane_map(mesh)
    finders = {"step": lambda: find_steps(planes),
               "sliver": lambda: find_slivers(planes, q_min, s),
               "ceiling": lambda: find_ceilings(planes, mesh, q_min, s),
               "slope": lambda: find_slopes(planes, boundary, level, s),
               "thin": lambda: find_thin(mesh),
               "ledge": lambda: find_ledges(planes, mesh, print_pose_of(stl))}
    found = {}
    for name in classes:
        try:
            found[name] = sorted(finders[name](), key=lambda r: -r["score"])
        except Exception as e:  # one class's edge case never hides the others
            found[name] = []
            print(f"  [{name}] lint pass failed: {e}", file=sys.stderr)
    return mesh, found


def report(stl, top, show_all, classes):
    step = stl.with_suffix("") if stl.suffix == ".stl" else stl
    step = step if step.suffix == ".step" else step.with_suffix(".step")
    mesh, found = lint(stl, classes)
    answers_path = stl.with_suffix(".lint-answers")
    entries = (parse_answers(answers_path.read_text())
               if answers_path.exists() else [])
    opens, answered = {}, []
    for name in classes:
        if name in _RANKED:
            opens[name] = answered_in_place(found[name], entries)
            continue
        opens[name], hit = split_answered(found[name], entries)
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
            if "answer" in r:
                _print_answer(r["answer"], "    answered: ")
    if show_all:
        for r, why in answered:
            _print_answer(why, f"\n  [{r['class']} · answered] ")
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

    # answers: an anchor ON the strip answers it; a wrong class, a far anchor, and an anchor
    # a fifth of a millimetre off the face all leave it open — nothing inherits by proximity
    entries = parse_answers("[sliver] retention tab — prints as a one-sided"
                            " bridge\nclick: x=15.000 y=0.250 z=5.000\n")
    opened, answered = split_answered(got, entries)
    assert not opened and len(answered) == 1, (opened, answered)
    assert "one-sided bridge" in answered[0][1], answered
    for miss in ("[step] wrong class\nclick: x=15.000 y=0.250 z=5.000\n",
                 "[sliver] far away\nclick: x=15.000 y=0.250 z=95.000\n",
                 "[sliver] beside it\nclick: x=15.000 y=0.450 z=5.000\n"):
        opened, answered = split_answered(got, parse_answers(miss))
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

    # thin: a 0.3 mm plate — two faces looking away from each other across material — is found
    # at its thickness; the same faces looking at each other are a 0.3 mm slot of air and are
    # not; a 5 mm slab is past the reach
    def plate(z0, z1, x0=0.0):
        return [[(x0, 0, z1), (x0 + 10, 0, z1), (x0 + 10, 10, z1), (x0, 10, z1)],   # up
                [(x0, 0, z0), (x0, 10, z0), (x0 + 10, 10, z0), (x0 + 10, 0, z0)]]   # down
    got = find_thin(sheet(plate(0.0, 0.3)))
    assert len(got) == 1 and got[0]["line"].startswith("0.300 mm"), got
    slot = [[(0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0)],
            [(0, 0, 0.3), (0, 10, 0.3), (10, 10, 0.3), (10, 0, 0.3)]]
    assert find_thin(sheet(slot)) == [], "a slot of air read as material"
    assert find_thin(sheet(plate(0.0, 5.0))) == [], "a 5 mm slab read as thin"
    # ranked thinnest first, and an answer keeps the place on the ranking beside its reason
    got = sorted(find_thin(sheet(plate(0.0, 1.0) + plate(0.0, 0.05, x0=20.0))),
                 key=lambda r: -r["score"])
    assert [r["line"][:9] for r in got] == ["0.050 mm ", "1.000 mm "], got
    # the same plate broken by a 2 mm gap is one place in two pieces
    two = find_thin(sheet(plate(0.0, 0.05) + plate(0.0, 0.05, x0=12.0)))
    assert len(two) == 1 and two[0]["line"].endswith("in 2 pieces"), two
    at = dict(pick_points("\n".join(got[0]["pick"])))["click"]
    ranked = answered_in_place(got, parse_answers(
        f"[thin] a reason\nclick: x={at[0]:.3f} y={at[1]:.3f} z={at[2]:.3f}\n"))
    assert len(ranked) == 2 and ranked[0]["answer"] == "a reason", ranked
    assert split_alternatives(ranked[0]["answer"]) == ("a reason", ""), ranked
    assert split_alternatives("why\nalternatives: thicker, but it hits the plate") == (
        "why", "thicker, but it hits the plate")

    # ledge: a 1 mm² print-down square 10 mm up is found; a 25 mm² one on the same plane is a
    # ceiling's, and a 1 mm² one on the bed is not a ledge
    tiny = [(5, 5, 10), (5, 6, 10), (6, 6, 10), (6, 5, 10)]
    big = [(20, 20, 10), (20, 25, 10), (25, 25, 10), (25, 20, 10)]
    bed = [(30, 30, 0), (30, 31, 0), (31, 31, 0), (31, 30, 0)]
    m = sheet([tiny, big, bed])
    got = find_ledges(planes_of(m), m, np.eye(3))
    assert len(got) == 1 and got[0]["line"].startswith("1.00 mm² flat face 0° off"), got
    # a faucet base leans 15° on the bed: the flat square reads 15° off; a square sloped 40°
    # toward +Y in the box comes round to 25° and is a ledge; one sloped 40° toward -Y goes on
    # to 55°, past the 30° the profiles support from
    rise = float(np.tan(np.radians(40)))
    toward = [(5, 15, 10), (5, 16, 10 + rise), (6, 16, 10 + rise), (6, 15, 10)]
    away = [(5, 25, 10 + rise), (5, 26, 10), (6, 26, 10), (6, 25, 10 + rise)]
    m = sheet([tiny, toward, away, bed])
    got = find_ledges(planes_of(m), m, print_pose_of(Path("industrial-shell-base.stl")))
    assert sorted(r["line"].split("flat face ")[1][:3] for r in got) == ["15°", "25°"], got

    print("selftest: every class finds its defect and only its own; the face classes both ways up")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pieces", nargs="*", help=".stl (or .step with .stl beside it)")
    ap.add_argument("--top", type=int, default=12, help="findings to show (default 12)")
    ap.add_argument("--all", action="store_true",
                    help="show every finding, answered ones included")
    ap.add_argument("--classes", default=",".join(_CLASSES),
                    help="comma list of: " + ",".join(_CLASSES))
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
        report(stl, args.top, args.all, classes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
