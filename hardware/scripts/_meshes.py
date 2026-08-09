"""Triangle meshes for the placed world's solids, tessellated once.

`_overlap` and `_clearing` ask what two bodies share and how far apart they stand. Both are
asked here, on meshes, and both readings carry a bound rather than a last representable digit.

    import _meshes
    m = _meshes.meshed(solid)                    # a manifold3d Manifold, memoized
    (m_a ^ m_b).volume()                         # what two bodies share, mm³
    m_a.min_gap(m_b, within)                     # how far apart, up to `within`

A tessellation of a convex surface is INSCRIBED — every mesh point lies on or inside the true
surface — so a mesh gap over-reports and a mesh overlap under-reports; on a concave surface the
sign flips. Neither runs past the chord the mesh may sit off the surface, so a reading stands
within ~2 × `DEFLECTION` of the exact one, in a direction the shape decides. `selftest` holds
that against the exact kernel on the curvature where the chord is widest.

`min_gap` COSTS WHAT IT SEARCHES. Told to look further than the bodies are apart, it sweeps the
volume between them; told to stop at `within`, it returns `within` and stops. The bound is what
makes the reading cheap, and `within` is a floor under an answer rather than the answer.

THREE TRAPS, EACH OF WHICH LOSES A MEASUREMENT SILENTLY:

1. BRepMesh WRITES ITS TRIANGLES ONTO THE FACES IT IS HANDED, and an OCCT bounding box prefers a
   triangulation to the analytic surface when one is there. Meshing a live solid would widen
   every later `_boxes.boxed()` on it by the deflection — and `placed` grades seats at
   `enclosure_assembly.SEAT_TOL`, so the pack would fail on a tolerance it never left. Every
   shape meshed here is a COPY.

2. OCCT TRIANGULATES FACE BY FACE, so a shared edge arrives twice and the mesh is a pile of
   loose sheets rather than a closed body. Unwelded, manifold3d rejects it. The weld is by
   rounded coordinate at `WELD`, far under any feature and far over the noise between two
   parametrizations of one edge.

3. A MESH manifold3d REJECTS COMES BACK EMPTY, VOLUME 0.0 — no exception, no flag. Every overlap
   against it would read 0.00 and every gap would read clear, which is the same silent zero the
   exact boolean is guarded against. The status is read on construction and a rejected mesh
   raises here rather than being handed on to be measured as a clean pair.
"""

import collections
import hashlib
import io
import os

import numpy as np
import manifold3d

import _realized

from OCP.BRep import BRep_Tool
from OCP.BRepBuilderAPI import BRepBuilderAPI_Copy
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepTools import BRepTools
from OCP.gp import gp_TrsfForm
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.TopExp import TopExp_Explorer
from OCP.TopTools import TopTools_FormatVersion
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS

from manifold3d import Error, Manifold, Mesh

# The chord a mesh may sit off the surface it stands for, and the turn it may take in one step.
#
# WHAT SETS THE TURN IS THE TIGHTEST CLASH FLOOR IN THE REPO, which is
# `_cold_scorecard.TOUCH_VOLUME` at a tenth of a mm³ — not the millimetre `_clearing.HIT_VOL`
# calls a hit at. Two curved bodies that TOUCH — a boss seated in its bore, a tube laid along a
# coil — carry two rings of facets struck independently, and wherever the rings do not phase
# together a vertex of one reaches past a facet of the other. The pair then shares a sliver no
# pair of true surfaces shares, and a seat the machine is built around reads as a clash.
#
# The sliver does not fall smoothly as the facets shrink — how the two rings land against each
# other is worth as much as how fine they are — so the turn is set an order of magnitude under
# the floor rather than at the first value that clears it. `selftest` holds a seat against it.
#
# The chord binds on flats and on wide radii, where the turn does not reach. The gap readings
# ride on it: they stand within ~2 × the chord of the exact ones, against a millimetre floor.
DEFLECTION = 0.02
ANGULAR = 0.10

# Two nodes nearer than this are one vertex. A seam duplicate is the SAME point reached through
# two face parametrizations, so what separates them is arithmetic noise; the smallest real
# feature in the pack is three orders over this.
WELD = 1e-7

_CACHE: dict = {}

# The extents of a mesh, named as `_boxes.boxed` names a solid's, so a caller reading `.ymax`
# off one reads it off the other. A shared solid is built for one reading and thrown away, so
# it has no place in `_boxes`, whose entries are the placed world's and outlive the ask.
Box = collections.namedtuple("Box", "xmin ymin zmin xmax ymax zmax")


def box(manifold) -> Box:
    """A manifold's own extents."""
    return Box(*manifold.bounding_box())


def meshed(solid, deflection: float = DEFLECTION):
    """The solid as a `Manifold`, memoized by identity. Keyed like `_boxes.boxed`.

    A `Manifold` passes through: `common` hands one back, and what it shares with a third body
    is a fair question to ask of it."""
    if isinstance(solid, Manifold):
        return solid
    key = (hash(solid.wrapped), deflection)
    hit = _CACHE.get(key)
    if hit is not None and hit[0].wrapped.IsSame(solid.wrapped):
        return hit[1]
    man = _manifold(solid, deflection)
    _CACHE[key] = (solid, man)          # pin the solid so the entry keeps its shape alive
    return man


_DIR = _realized._ROOT / ".cache" / "meshes"

# One pack's triangles are tens of megabytes and every edit to a part's shape names a new set,
# so what is kept here grows with the work rather than with the machine. The oldest entries go
# once the pile passes this; a build that wanted one of them tessellates it as it always did.
KEEP_BYTES = 1 << 30
_pruned = False


def _prune():
    """The pile brought back under `KEEP_BYTES`, oldest first. Once per process, on the first
    entry written — a build that reads and writes nothing has nothing to tidy after it."""
    global _pruned
    _pruned = True
    entries = []
    for f in _DIR.glob("*.npz"):
        try:
            entries.append((f.stat().st_mtime, f.stat().st_size, f))
        except OSError:
            continue
    over = sum(e[1] for e in entries) - KEEP_BYTES
    for _t, size, f in sorted(entries):
        if over <= 0:
            return
        try:
            f.unlink()
            over -= size
        except OSError:
            continue


def _unplaced(solid):
    """The shape in its OWN frame, and the rigid move that stands it where it stands.

    A body is placed by hanging a location on the shape, so the shape under it is the one the
    part module drew and is the same shape wherever the body goes. Meshing THAT is what lets a
    move cost a matrix multiply rather than a tessellation."""
    shape = solid.wrapped
    loc = shape.Location()
    return shape.Located(TopLoc_Location()), loc.Transformation()


def _named(shape, deflection: float) -> str:
    """A name for the mesh `shape` tessellates to. The shape's own BREP text, WITHOUT its
    triangulation — a body already meshed once carries one, and a name that moved when it
    appeared would name the same geometry two ways — beside every number that decides how
    finely it is cut."""
    stream = io.BytesIO()
    BRepTools.Write_s(shape, stream, False, False, TopTools_FormatVersion.TopTools_FormatVersion_VERSION_1)
    h = hashlib.blake2b(stream.getbuffer(), digest_size=16)
    h.update(repr((deflection, ANGULAR, WELD)).encode())
    return h.hexdigest()


def _local_mesh(shape, deflection: float):
    """The welded, closed triangles of `shape` in its own frame — drawn once and kept.

    Sibling of [`_realized`](_realized.py), which keeps solids; this keeps what one tessellates
    to, and `_realized.DISABLED` defeats both so one run can prove the kept work honest."""
    if _realized.DISABLED:
        return _drawn(shape, deflection)
    path = _DIR / f"{_named(shape, deflection)}.npz"
    if path.is_file():
        try:
            with np.load(path) as kept:
                return kept["verts"], kept["tris"]
        except Exception:
            pass                                 # an entry that cannot be read is a miss
    verts, tris = _drawn(shape, deflection)
    try:
        _DIR.mkdir(parents=True, exist_ok=True)
        if not _pruned:
            _prune()
        tmp = path.with_suffix(f".{os.getpid()}.tmp")
        with open(tmp, "wb") as f:               # np.savez appends .npz to a PATH, not a handle
            np.savez(f, verts=verts, tris=tris)
        os.replace(tmp, path)                    # a reader never sees a half-written entry
    except Exception:
        pass                                     # a cache that cannot be written is not an error
    return verts, tris


def _drawn(shape, deflection: float):
    verts, tris = _tessellate(shape, deflection)
    if verts is None:
        raise RuntimeError(
            "a solid tessellated to no triangles — it cannot be measured against anything, and "
            "an unmeasured body is not an absent one")
    verts, tris = _weld(verts, tris)
    return verts, _close(verts, tris)


def _standing(verts, trsf):
    """`verts`, moved out of the body's own frame onto where the body stands."""
    if trsf.Form() == gp_TrsfForm.gp_Identity:
        return verts
    m = np.array([[trsf.Value(r, c) for c in range(1, 5)] for r in range(1, 4)])
    return verts @ m[:, :3].T + m[:, 3]


def _manifold(solid, deflection: float):
    shape, trsf = _unplaced(solid)
    verts, tris = _local_mesh(shape, deflection)
    verts = _standing(verts, trsf)
    man = Manifold(Mesh(verts.astype(np.float32), tris))
    if man.status() != Error.NoError:
        raise RuntimeError(
            f"a solid's mesh came back {man.status()} — manifold3d hands such a mesh on EMPTY, so "
            f"every overlap against it reads 0.00 and every gap reads clear. The body is "
            f"unmeasured, not clean")
    return man


def _tessellate(shape, deflection: float):
    """Flat vertex and triangle arrays for one shape, in the frame it is handed in, wound
    outward.

    THE SHAPE MESHED IS A COPY — see trap 1."""
    copy = BRepBuilderAPI_Copy(shape).Shape()
    BRepMesh_IncrementalMesh(copy, deflection, False, ANGULAR, True)
    pos, idx = [], []
    exp = TopExp_Explorer(copy, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face_s(exp.Current())
        exp.Next()
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is None:                 # a face BRepMesh could not mesh contributes nothing
            continue
        trsf = loc.Transformation()
        flip = face.Orientation() == TopAbs_REVERSED
        base = len(pos)
        for i in range(1, tri.NbNodes() + 1):
            p = tri.Node(i).Transformed(trsf)
            pos.append((p.X(), p.Y(), p.Z()))
        for i in range(1, tri.NbTriangles() + 1):
            a, b, c = tri.Triangle(i).Get()
            if flip:
                a, c = c, a
            idx.append((base + a - 1, base + b - 1, base + c - 1))
    if not idx:
        return None, None
    return np.array(pos), np.array(idx, dtype=np.int64)


def _weld(verts, tris):
    """One vertex per distinct point, and the triangles rewritten onto it."""
    key = np.round(verts / WELD).astype(np.int64)
    _, first, inverse = np.unique(key, axis=0, return_index=True, return_inverse=True)
    return verts[first], inverse.ravel()[tris].astype(np.uint32)


def _close(verts, tris):
    """The same triangles, plus a patch over every hole the mesher left.

    BRepMesh returns no triangulation at all for the occasional face and reports it the same way
    it reports a face with nothing to draw, so a solid arrives here with a face-shaped hole in it
    and every reading against it would be taken on an open sheet.

    The patch is stitched onto the mesh's OWN BOUNDARY rather than onto the face's wires. An
    edge sampled off the surface a second time lands its points between the neighbour's, and the
    two rings meet at T-junctions that leave the hole exactly as open as it was; a ring taken
    from the boundary is made of vertices the neighbours already share."""
    # A closed body carries every edge twice, once each way round. An edge whose reverse is
    # missing is a rim.
    directed = set()
    for a, b, c in tris:
        directed.update(((a, b), (b, c), (c, a)))
    open_edges = {u: v for u, v in directed if (v, u) not in directed}
    if not open_edges:
        return tris

    rings = []
    while open_edges:
        start = next(iter(open_edges))
        ring, at = [start], start
        while (nxt := open_edges.pop(at, None)) is not None and nxt != start:
            ring.append(nxt)
            at = nxt
        if len(ring) >= 3:
            rings.append(ring)

    # Rings sharing a plane bound one hole together — an outer ring and whatever stands inside
    # it — so they are triangulated in one ask and the inner ones come out as holes.
    patches, by_plane = [], {}
    for ring in rings:
        pts = verts[ring]
        normal = _ring_normal(pts)
        key = tuple(np.round(np.append(normal, normal @ pts[0]), 3))
        by_plane.setdefault(key, []).append(ring)
    for key, group in by_plane.items():
        normal = np.array(key[:3])
        ux = np.array([1.0, 0.0, 0.0]) if abs(normal[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
        ux = np.cross(ux, normal)
        ux /= np.linalg.norm(ux)
        uy = np.cross(normal, ux)
        flat = [np.column_stack([verts[r] @ ux, verts[r] @ uy]) for r in group]
        offs, run = [], 0
        for f in flat:
            offs.append(run)
            run += len(f)
        index = np.concatenate([np.array(r) for r in group])
        # The surrounding surface carries each of these edges one way round, so the patch has to
        # carry it the other for the pair to close.
        for a, b, c in np.asarray(manifold3d.triangulate([f.astype(np.float64) for f in flat])):
            patches.append((index[a], index[c], index[b]))
    return np.vstack([tris, np.array(patches, dtype=np.uint32)]) if patches else tris


def _ring_normal(pts):
    """The unit normal of a closed ring, by Newell's method."""
    nxt = np.roll(pts, -1, axis=0)
    n = np.array([
        ((pts[:, 1] - nxt[:, 1]) * (pts[:, 2] + nxt[:, 2])).sum(),
        ((pts[:, 2] - nxt[:, 2]) * (pts[:, 0] + nxt[:, 0])).sum(),
        ((pts[:, 0] - nxt[:, 0]) * (pts[:, 1] + nxt[:, 1])).sum()])
    mag = np.linalg.norm(n)
    if mag < 1e-12:
        raise RuntimeError("a hole in a solid's mesh has no plane to be patched in — the "
                           "boundary it left is not a ring")
    return n / mag


def selftest():
    """Each reading held against the answer arithmetic gives, and against the exact kernel."""
    import pathlib
    import sys

    import cadquery as cq

    from OCP.BRepExtrema import BRepExtrema_DistShapeShape

    r = 3.175
    cyl = cq.Solid.makeCylinder(r, 100.0)
    got, want = meshed(cyl).volume(), cyl.Volume()
    off = abs(got - want) / want
    if off > 0.01:
        raise AssertionError(f"a Ø{2*r:g} tube meshes {off:.2%} off its own volume, past what a "
                             f"{DEFLECTION} mm chord accounts for")
    yield f"a tube meshes within {off:.3%} of its exact volume"

    box = cq.Workplane("XY").box(10, 10, 10)
    if meshed(box.val().Solids()[0]) is not meshed(box.val().Solids()[0]):
        raise AssertionError("two wrappers of one solid meshed twice — the memo is keyed on the "
                             "wrapper, so every ask is a first ask")
    yield "two wrappers of one solid share a mesh"

    # A gap across two curved faces, where the chord is widest. Both the arithmetic answer and
    # the kernel's own are held, so neither backend can drift alone.
    d = 12.0
    a = cq.Solid.makeCylinder(r, 60.0, cq.Vector(0, 0, 0), cq.Vector(0, 0, 1))
    b = cq.Solid.makeCylinder(r, 60.0, cq.Vector(d, 0, 0), cq.Vector(0, 0, 1))
    arith = d - 2 * r
    exact = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped).Value()
    mesh = meshed(a).min_gap(meshed(b), 3.0 * arith)
    for label, ref in (("arithmetic", arith), ("the exact kernel", exact)):
        if abs(mesh - ref) > 2.0 * DEFLECTION:
            raise AssertionError(
                f"two Ø{2*r:g} tubes {d:g} apart read {mesh:.4f} mm against {label}'s {ref:.4f} — "
                f"past the 2 × {DEFLECTION} mm a chord accounts for")
    yield f"a curved gap reads {mesh:.4f} mm against an exact {exact:.4f}"

    # Two tubes of one Ø crossing axis-on-axis share a Steinmetz solid of 16r³/3. A port row
    # fixes both runs to one z, so this is an arrangement the pack builds.
    L = 300.0
    x = cq.Solid.makeCylinder(r, L, cq.Vector(461 - L / 2, 358, 188), cq.Vector(1, 0, 0))
    y = cq.Solid.makeCylinder(r, L, cq.Vector(461, 358 - L / 2, 188), cq.Vector(0, 1, 0))
    want = 16.0 / 3.0 * r ** 3
    got = (meshed(x) ^ meshed(y)).volume()
    if abs(got - want) / want > 0.02:
        raise AssertionError(f"two crossed Ø{2*r:g} tubes share {got:.1f} mm³ against a Steinmetz "
                             f"{want:.1f} — the crossing is being missed")
    yield f"two crossed tubes share {got:.1f} mm³ against a Steinmetz {want:.1f}"

    # TWO BODIES THAT TOUCH SHARE NOTHING, and their meshes have to agree. A boss seated in its
    # own bore is the case the pack is full of, and the two surfaces are faceted independently:
    # the shaft's ring of facets stands where its own body was turned to, the bore's where the
    # body it was cut from was, and a shaft vertex reaches past a bore facet wherever the two
    # rings do not phase together. What they share has to stay under the volume a clash is
    # called at, or a seat the machine is built around reads as interpenetration.
    #
    # TURNED OFF PHASE ON PURPOSE. Cut a bore with the same cylinder and the two carry the same
    # facets, share nothing, and hold this whatever the chord is — which is not the case a pack
    # presents and not a reading worth taking.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "cold-core-layout"))
    import _cold_scorecard
    floor = _cold_scorecard.TOUCH_VOLUME
    seat = 20.0
    shaft = cq.Solid.makeCylinder(r, seat, cq.Vector(0, 0, 0), cq.Vector(0, 0, 1))
    bore = (cq.Workplane("XY").box(4 * r, 4 * r, seat, centered=(True, True, False))
            .cut(cq.Workplane(obj=shaft)).val())
    shared = (meshed(shaft.rotate((0, 0, 0), (0, 0, 1), 3.0)) ^ meshed(bore)).volume()
    if shared >= floor:
        raise AssertionError(
            f"a Ø{2*r:g} shaft seated {seat:g} mm into its own bore shares {shared:.4f} mm³ "
            f"where the two only touch, at or over the {floor:g} mm³ the tightest gate in the "
            f"repo calls a clash at — a designed seat reads as interpenetration at this facet "
            f"size")
    yield f"{seat:g} mm of shaft-in-bore seat shares {shared:.4f} mm³, under a {floor:g} floor"

    # An open sheet is not a body. manifold3d hands one back empty at volume 0.0, which reads
    # exactly like two bodies that share nothing — trap 3, held on the status the guard reads.
    sheet = Manifold(Mesh(np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], dtype=np.float32),
                          np.array([[0, 1, 2], [0, 2, 3]], dtype=np.uint32)))
    if sheet.status() == Error.NoError or not sheet.is_empty():
        raise AssertionError("an open sheet was accepted as a body — the guard in `_manifold` "
                             "reads a status that no longer means what it did")
    yield "an unclosed mesh is rejected rather than measured as empty"

    # THE WHOLE OF THE KEPT MESH RESTS ON THIS: a body meshed in its own frame and then moved is
    # the body meshed where it stands. The seat is a turn and a shift together, so neither is
    # answered for by the other.
    seat = cq.Location(cq.Vector(137.0, -46.5, 88.25), cq.Vector(0.3, 1.0, -0.7), 37.0)
    part = cq.Workplane("XY").box(18.0, 11.0, 7.0).faces(">Z").workplane().hole(4.0).val()
    seated = part.moved(seat)
    kept = meshed(seated)                                  # its own frame, then moved
    verts, tris = _drawn(seated.wrapped, DEFLECTION)       # meshed where it stands
    in_place = Manifold(Mesh(verts.astype(np.float32), tris))
    off = abs(kept.volume() - in_place.volume())
    if off > 1e-3:
        raise AssertionError(
            f"a seated body measures {kept.volume():.6f} mm³ off its own mesh moved and "
            f"{in_place.volume():.6f} meshed where it stands — {off:.2e} apart. The kept mesh "
            f"is not the body")
    apart = kept.min_gap(in_place, 1.0)
    if apart > 1e-4:
        raise AssertionError(
            f"a body's kept mesh stands {apart:.2e} mm off the one meshed in place — the seat "
            f"is not reaching the triangles it was kept without")
    yield (f"a body meshed in its own frame and moved is the one meshed in place, to "
           f"{off:.1e} mm³ and {apart:.1e} mm")

    # A name is what stands between a shape and last build's triangles.
    thicker = cq.Workplane("XY").box(18.0, 11.0, 7.1).val()
    mine = _named(_unplaced(part)[0], DEFLECTION)
    if mine == _named(_unplaced(thicker)[0], DEFLECTION):
        raise AssertionError("two shapes share a mesh name — one would be measured on the "
                             "other's triangles")
    if mine == _named(_unplaced(part)[0], DEFLECTION * 2):
        raise AssertionError("one shape names one mesh at two chords — a finer ask would be "
                             "served the coarser answer")
    if mine != _named(_unplaced(seated)[0], DEFLECTION):
        raise AssertionError("a body names a different mesh once seated — the name is reading "
                             "the placement, so nothing is read back after a move, which is the "
                             "one edit the keeping is for")
    yield "a name follows the shape and the chord, and not where the body stands"


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(" ", line)
        print("_meshes selftest OK")
