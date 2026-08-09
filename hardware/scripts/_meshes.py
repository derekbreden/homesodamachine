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

import numpy as np

from OCP.BRep import BRep_Tool
from OCP.BRepBuilderAPI import BRepBuilderAPI_Copy
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS

from manifold3d import Error, Manifold, Mesh

# The chord a mesh may sit off the surface it stands for, and the turn it may take in one step.
# Every reading taken through this module is bounded by the first of them; `selftest` holds the
# bound, so moving it moves what the audit can resolve.
DEFLECTION = 0.05
ANGULAR = 0.2

# Two nodes nearer than this are one vertex. A seam duplicate is the SAME point reached through
# two face parametrizations, so what separates them is arithmetic noise; the smallest real
# feature in the pack is three orders over this.
WELD = 1e-7

_CACHE: dict = {}


def meshed(solid, deflection: float = DEFLECTION):
    """The solid as a `Manifold`, memoized by identity. Keyed like `_boxes.boxed`."""
    key = (hash(solid.wrapped), deflection)
    hit = _CACHE.get(key)
    if hit is not None and hit[0].wrapped.IsSame(solid.wrapped):
        return hit[1]
    man = _manifold(solid, deflection)
    _CACHE[key] = (solid, man)          # pin the solid so the entry keeps its shape alive
    return man


def _manifold(solid, deflection: float):
    verts, tris = _tessellate(solid, deflection)
    if verts is None:
        raise RuntimeError(
            "a solid tessellated to no triangles — it cannot be measured against anything, and "
            "an unmeasured body is not an absent one")
    verts, tris = _weld(verts, tris)
    man = Manifold(Mesh(verts.astype(np.float32), tris))
    if man.status() != Error.NoError:
        raise RuntimeError(
            f"a solid's mesh came back {man.status()} — manifold3d hands such a mesh on EMPTY, so "
            f"every overlap against it reads 0.00 and every gap reads clear. The body is "
            f"unmeasured, not clean")
    return man


def _tessellate(solid, deflection: float):
    """Flat vertex and triangle arrays for one solid, in world coordinates, wound outward.

    THE SHAPE MESHED IS A COPY — see trap 1."""
    copy = BRepBuilderAPI_Copy(solid.wrapped).Shape()
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


def selftest():
    """Each reading held against the answer arithmetic gives, and against the exact kernel."""
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

    # An open sheet is not a body. manifold3d hands one back empty at volume 0.0, which reads
    # exactly like two bodies that share nothing — trap 3, held on the status the guard reads.
    sheet = Manifold(Mesh(np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], dtype=np.float32),
                          np.array([[0, 1, 2], [0, 2, 3]], dtype=np.uint32)))
    if sheet.status() == Error.NoError or not sheet.is_empty():
        raise AssertionError("an open sheet was accepted as a body — the guard in `_manifold` "
                             "reads a status that no longer means what it did")
    yield "an unclosed mesh is rejected rather than measured as empty"


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(" ", line)
        print("_meshes selftest OK")
