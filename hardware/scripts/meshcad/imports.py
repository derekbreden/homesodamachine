"""STEP files read as meshes.

A STEP the mesh kernel wrote beside itself (`<name>.step.npz`, `write.write_model`) is read
back as it was built, face records and all. Any other STEP — a vendor's part, or one an OCCT
generator still cuts — is tessellated once by OCCT under the rule's tolerances, its faces
recorded with the surfaces OCCT names, and kept in `.cache/meshcad/` under the digest of its
bytes, so the next read is a file load.
"""

import hashlib
import json
from pathlib import Path

import manifold3d as m3d
import numpy as np

from . import build
from .rule import ANGULAR, LINEAR, snap

_ROOT = Path(__file__).resolve().parents[3]
CACHE = _ROOT / ".cache" / "meshcad" / "import"
#: Moves when the tessellation of a STEP would come out differently.
IMPORT_VERSION = 2


def load_model(path):
    """[MeshSolid] from a model file written by `write.write_model`, or its bytes."""
    import io
    from .solids import MeshSolid
    if isinstance(path, (bytes, bytearray, memoryview)):
        path = io.BytesIO(path)
    with np.load(path, allow_pickle=False) as z:
        records = json.loads(bytes(z["records"]).decode())
        solids = []
        for i, name in enumerate(json.loads(bytes(z["names"]).decode())):
            V, T, F = z[f"V{i}"], z[f"T{i}"].astype(np.int64), z[f"F{i}"].astype(np.int64)
            recs = [_unjson(r) for r in records[i]]
            part = build.Part(V, T, F, recs)
            solids.append(MeshSolid(build.solid(part)))
    return solids


def _unjson(r):
    return {k: (np.asarray(v, float) if isinstance(v, list) else v) for k, v in r.items()}


def step_solids(path):
    """[MeshSolid] for the STEP at `path`, through the model beside it or the import cache."""
    path = Path(path)
    model = path.with_name(path.name + ".npz")
    if model.is_file() and (not path.is_file() or model.stat().st_mtime >= path.stat().st_mtime):
        return load_model(model)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    cached = CACHE / f"{digest}-{IMPORT_VERSION}.npz"
    if cached.is_file():
        return load_model(cached)
    solids = tessellate_step(path)
    from .write import write_model
    CACHE.mkdir(parents=True, exist_ok=True)
    write_model(solids, cached, names=[""] * len(solids))
    return load_model(cached)


def tessellate_step(path):
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader
    from OCP.TopAbs import TopAbs_SOLID
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS
    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone:
        raise ValueError(f"STEP File could not be loaded: {path}")
    reader.TransferRoots()
    shape = reader.OneShape()
    out = []
    exp = TopExp_Explorer(shape, TopAbs_SOLID)
    while exp.More():
        out.append(occ_solid_mesh(TopoDS.Solid_s(exp.Current()), _named(path)))
        exp.Next()
    return out


def _named(path):
    """`path` as a face record names it: from the repo's root when it lies in this tree, as a
    generator's line is, so one STEP is one record in every checkout."""
    try:
        return Path(path).resolve().relative_to(_ROOT).as_posix()
    except ValueError:
        return str(path)


def occ_solid_mesh(solid, src=None):
    """An OCCT solid as a MeshSolid, one face record per B-rep face."""
    from OCP.BRep import BRep_Tool
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.GeomAbs import (GeomAbs_Cone, GeomAbs_Cylinder, GeomAbs_Plane, GeomAbs_Sphere,
                             GeomAbs_Torus)
    from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS
    from .solids import MeshSolid
    BRepMesh_IncrementalMesh(solid, LINEAR, False, ANGULAR, True)
    V, T, F, recs, bare = [], [], [], [], []
    exp = TopExp_Explorer(solid, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face_s(exp.Current())
        exp.Next()
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is None:
            bare.append(face)
            continue
        trsf = loc.Transformation()
        flip = face.Orientation() == TopAbs_REVERSED
        base = len(V)
        for i in range(1, tri.NbNodes() + 1):
            V.append(tri.Node(i).Transformed(trsf).Coord())
        fi = len(recs)
        for i in range(1, tri.NbTriangles() + 1):
            a, b, c = tri.Triangle(i).Get()
            T.append((base + a - 1, base + c - 1, base + b - 1) if flip else (base + a - 1, base + b - 1, base + c - 1))
            F.append(fi)
        s = BRepAdaptor_Surface(face)
        k = s.GetType()
        if k == GeomAbs_Plane:
            pl = s.Plane()
            n = np.array(pl.Axis().Direction().Coord()) * (-1 if flip else 1)
            rec = build.record("PLANE", src, "step", p=np.array(pl.Location().Coord()), n=n)
        elif k == GeomAbs_Cylinder:
            cy = s.Cylinder()
            rec = build.record("CYLINDER", src, "step", p=np.array(cy.Location().Coord()),
                               d=np.array(cy.Axis().Direction().Coord()), r=cy.Radius())
        elif k == GeomAbs_Cone:
            co = s.Cone()
            rec = build.record("CONE", src, "step", p=np.array(co.Location().Coord()),
                               d=np.array(co.Axis().Direction().Coord()), r=co.RefRadius(),
                               slope=float(np.tan(co.SemiAngle())))
        elif k == GeomAbs_Sphere:
            sp = s.Sphere()
            rec = build.record("SPHERE", src, "step", c=np.array(sp.Location().Coord()), r=sp.Radius())
        elif k == GeomAbs_Torus:
            to = s.Torus()
            rec = build.record("TORUS", src, "step", c=np.array(to.Location().Coord()),
                               d=np.array(to.Axis().Direction().Coord()), R=to.MajorRadius(),
                               r=to.MinorRadius())
        else:
            rec = build.record("BSPLINE", src, "step")
        recs.append(rec)
    V = np.asarray(V, float)
    T = np.asarray(T, np.int64)
    # Faces meshed apart share their edges' points exactly; weld them.
    uniq, inv = np.unique(V, axis=0, return_inverse=True)
    T = inv.reshape(-1)[T]
    keep = (T[:, 0] != T[:, 1]) & (T[:, 1] != T[:, 2]) & (T[:, 0] != T[:, 2])
    part = build.Part(uniq, T[keep], np.asarray(F, np.int64)[keep], recs)
    try:
        return MeshSolid(build.solid(part))
    except ValueError:
        if bare:
            return occ_solid_mesh(_sewn_without(solid, bare, src), src)
        oid = m3d.Manifold.reserve_ids(1)
        build.REGISTRY[oid] = recs
        mesh = m3d.Mesh64(vert_properties=snap(part.verts), tri_verts=part.tris.astype(np.uint64),
                          face_id=part.fids.astype(np.uint64),
                          run_original_id=np.array([oid], np.uint32),
                          run_index=np.array([0, part.tris.size], np.uint64))
        mesh.merge()
        m = m3d.Manifold(mesh)
        if m.status() != m3d.Error.NoError:
            raise ValueError(f"meshcad: {src} does not mesh to a closed solid ({m.status()})")
        return MeshSolid(m)


def _sewn_without(solid, bare, src):
    """`solid` sewn again from its faces less `bare`, the ones OCCT's mesher left empty, which
    must have no area. A shell sewn from ruled faces holds one where two outlines collapse at
    the same vertex: it stands between two faces along one line, and the mesher discretizes the
    edges on its two sides apart. Sewn without it, those two faces share one edge."""
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing
    from OCP.BRepGProp import BRepGProp
    from OCP.BRepTools import BRepTools
    from OCP.GProp import GProp_GProps
    from OCP.ShapeFix import ShapeFix_Solid
    from OCP.TopAbs import TopAbs_FACE, TopAbs_SHELL
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS
    for face in bare:
        props = GProp_GProps()
        BRepGProp.SurfaceProperties_s(face, props)
        if props.Mass() > 1e-9:
            raise ValueError(f"meshcad: {src}: OCCT meshes nothing on a face of {props.Mass():.3g} mm²")
    sew = BRepBuilderAPI_Sewing(1e-6)
    exp = TopExp_Explorer(solid, TopAbs_FACE)
    while exp.More():
        if not any(exp.Current().IsSame(face) for face in bare):
            sew.Add(exp.Current())
        exp.Next()
    sew.Perform()
    sewn = sew.SewedShape()
    BRepTools.Clean_s(sewn)
    exp = TopExp_Explorer(sewn, TopAbs_SHELL)
    return ShapeFix_Solid().SolidFromShell(TopoDS.Shell_s(exp.Current()))


def install(cq):
    """`cq.importers.importStep` answering with meshes."""
    def importStep(fileName, *args, **kwargs):
        from .solids import MeshCompound
        solids = step_solids(fileName)
        shape = solids[0] if len(solids) == 1 else MeshCompound(solids)
        return cq.Workplane("XY").newObject([shape])
    cq.importers.importStep = importStep
    cq.occ_impl.importers.importStep = importStep
