"""CadQuery's Solid and Compound held as Manifold meshes.

`activate` installs these under CadQuery's own classes before its Workplane is imported, so a
generator's `cq.Workplane(...).rect(...).extrude(...).cut(...)` runs CadQuery's own Workplane
and selector code over meshes. Sketches, wires and planar faces stay OCCT's: they are cheap
and exact, and the rule cuts them into points only where a solid is built from them.

`MeshSolid` is a subclass of CadQuery's Solid, and `MeshFace`/`MeshEdge` of its Face/Edge,
so every isinstance test in CadQuery holds. None of them has a `wrapped` B-rep: code that
reaches for OCCT on one fails at that line and says so.
"""

import math

import manifold3d as m3d
import numpy as np

from cadquery.occ_impl import shapes as occ
from cadquery.occ_impl.geom import BoundBox, Location, Matrix, Plane, Vector

from . import build
from .build import Curve, Loop, record
from .rule import ANGULAR, LINEAR, axis_frame, caller, circle_points, ring_count
from .topo import GEOM, Topology, classify


class NoBrep(AttributeError):
    pass


def _no_brep(self):
    raise NoBrep(f"meshcad: a {type(self).__name__} is a mesh and has no OCCT B-rep; "
                 "this line needs a mesh-kernel equivalent")


def vec3(v):
    if isinstance(v, Vector):
        return np.array(v.toTuple(), float)
    if hasattr(v, "X") and callable(getattr(v, "X")):
        return np.array([v.X(), v.Y(), v.Z()], float)
    return np.array(tuple(v) + (0.0,) * (3 - len(tuple(v))), float)


def _bbox(lo, hi):
    from OCP.Bnd import Bnd_Box
    bb = Bnd_Box()
    bb.Update(*lo, *hi)
    return BoundBox(bb)


def _matrix_of(loc):
    """3x4 of a Location, Matrix or gp_Trsf."""
    if isinstance(loc, Location):
        t = loc.wrapped.Transformation()
        return np.array([[t.Value(i, j) for j in range(1, 5)] for i in range(1, 4)])
    if isinstance(loc, Matrix):
        return np.array([[loc[i, j] for j in range(4)] for i in range(3)])
    return np.array([[loc.Value(i, j) for j in range(1, 5)] for i in range(1, 4)])


# --- OCCT profiles cut into points by the rule --------------------------------------

def _edge_points(edge):
    """(points in the edge's direction, Curve, closed) for an OCCT edge."""
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.GCPnts import GCPnts_TangentialDeflection
    from OCP.GeomAbs import GeomAbs_Circle, GeomAbs_Line
    from OCP.TopAbs import TopAbs_REVERSED
    ad = BRepAdaptor_Curve(edge.wrapped)
    kind = ad.GetType()
    u0, u1 = ad.FirstParameter(), ad.LastParameter()
    rev = edge.wrapped.Orientation() == TopAbs_REVERSED

    def at(u):
        return np.array(ad.Value(u).Coord())

    closed = False
    if kind == GeomAbs_Line:
        pts, curve = np.array([at(u0), at(u1)]), Curve("LINE")
    elif kind == GeomAbs_Circle:
        circ = ad.Circle()
        ax = circ.Position()
        c = np.array(ax.Location().Coord())
        a = np.array(ax.Direction().Coord())
        r = circ.Radius()
        curve = Curve("CIRCLE", c, a, r)
        if abs(u1 - u0 - 2 * math.pi) < 1e-9:
            closed = True
            pts = circle_points(c, a, r)
            if np.dot(a, axis_frame(a)[0]) < 0:
                pts = pts[::-1]
        else:
            pts = circle_points(c, a, r, at(u0), at(u1), ccw_about=a)
    else:
        d = GCPnts_TangentialDeflection(ad, u0, u1, ANGULAR, LINEAR)
        pts = np.array([d.Value(i).Coord() for i in range(1, d.NbPoints() + 1)])
        curve = Curve(str(kind).split("_")[-1].upper())
        closed = np.linalg.norm(pts[0] - pts[-1]) < 1e-9 and len(pts) > 2
        if closed:
            pts = pts[:-1]
    if rev:
        pts = pts[::-1]
    return pts, curve, closed


def wire_loop(wire, curves=None):
    """A closed OCCT wire as a Loop, each segment naming the edge it came from."""
    from OCP.BRepTools import BRepTools_WireExplorer
    curves = [] if curves is None else curves
    exp = BRepTools_WireExplorer(wire.wrapped)
    pts, seg = [], []
    while exp.More():
        p, curve, closed = _edge_points(occ.Edge(exp.Current()))
        ci = len(curves)
        curves.append(curve)
        if not closed:
            p = p[:-1]
        pts.append(p)
        seg.append(np.full(len(p), ci))
        exp.Next()
    return Loop(np.concatenate(pts), np.concatenate(seg), curves)


def face_loops(face):
    curves = []
    loops = [wire_loop(face.outerWire(), curves)]
    loops += [wire_loop(w, curves) for w in face.innerWires()]
    return loops


def _profile(args):
    """(loops, plane normal, remaining args) from (face, ...) or (outer, inners, ...)."""
    if isinstance(args[0], occ.Face):
        face = args[0]
        if face.geomType() != "PLANE":
            raise ValueError("meshcad: only planar faces are swept into solids")
        return face_loops(face), vec3(face.normalAt()), args[1:]
    outer, inners = args[0], args[1]
    face = occ.Face.makeFromWires(outer, list(inners))
    return face_loops(face), vec3(face.normalAt()), args[2:]


# --- The solid ------------------------------------------------------------------------

class MeshShape:
    """What MeshSolid and MeshCompound share."""

    wrapped = property(_no_brep)
    forConstruction = False
    label = ""

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other

    def isSame(self, other):
        """One shape twice: the same object, the same Manifold, or the same solid's face or
        edge by its index."""
        if self is other:
            return True
        if isinstance(self, MeshSolid) and isinstance(other, MeshSolid):
            return self.m is other.m
        return (type(self) is type(other) and getattr(self, "owner", None) is not None
                and self.owner is getattr(other, "owner", None) and self.index == other.index)

    def isNull(self):
        return False

    def isValid(self):
        return all(s.m.status() == m3d.Error.NoError for s in self._solids())

    def clean(self):
        return self

    def fix(self):
        return self

    def copy(self, mesh=False):
        return self

    def location(self):
        return Location()

    def Volume(self, tol=None):
        return float(sum(s.m.volume() for s in self._solids()))

    def Area(self):
        return float(sum(s.m.surface_area() for s in self._solids()))

    def Center(self):
        tot, acc = 0.0, np.zeros(3)
        for s in self._solids():
            v, c = s._mass()
            tot += v
            acc += v * c
        return Vector(*(acc / tot)) if tot else self.CenterOfBoundBox()

    def CenterOfBoundBox(self, tolerance=None):
        return self.BoundingBox().center

    def BoundingBox(self, tolerance=None, optimal=False):
        boxes = [s.m.bounding_box() for s in self._solids() if not s.m.is_empty()]
        if not boxes:
            return _bbox((0, 0, 0), (0, 0, 0))
        b = np.array(boxes)
        return _bbox(b[:, :3].min(0), b[:, 3:].max(0))

    def Faces(self):
        return [f for s in self._solids() for f in s._topology().faces]

    def Edges(self):
        return [e for s in self._solids() for e in s._topology().edge_objs]

    def Vertices(self):
        return [v for s in self._solids() for v in s._topology().vertex_objs]

    def Wires(self):
        return [w for f in self.Faces() for w in f.Wires()]

    def Shells(self):
        return []

    def Compounds(self):
        return [self]

    def _entities(self, topo_type):
        return {"Solid": self.Solids, "Face": self.Faces, "Edge": self.Edges,
                "Vertex": self.Vertices, "Compound": self.Compounds}[topo_type]()

    def faces(self, selector=None):
        return _filtered(self.Faces(), selector)

    def edges(self, selector=None):
        return _filtered(self.Edges(), selector)

    def vertices(self, selector=None):
        return _filtered(self.Vertices(), selector)

    def solids(self, selector=None):
        return _filtered(self.Solids(), selector)

    # Booleans: every operand is a mesh; the union of the tools goes in one batch.
    def fuse(self, *others, glue=False, tol=None):
        ms = [s.m for s in self._solids()] + [m for o in others for m in _meshes(o)]
        return MeshSolid(build.boolean(ms, m3d.OpType.Add))

    def cut(self, *others, tol=None):
        tools = [m for o in others for m in _meshes(o)]
        return _each(self, lambda m: build.boolean([m] + tools, m3d.OpType.Subtract)
                     if tools else m)

    def intersect(self, *others, tol=None):
        tools = [m for o in others for m in _meshes(o)]
        if not tools:
            return self
        tool = _union(tools)
        return _each(self, lambda m: build.boolean([m, tool], m3d.OpType.Intersect))

    def __add__(self, other):
        return self.fuse(other)

    def __sub__(self, other):
        return self.cut(other)

    def __mul__(self, other):
        return self.intersect(other)

    def split(self, *splitters):
        pieces = []
        for s in self._solids():
            parts = [s.m]
            for sp in splitters:
                nxt = []
                for m in parts:
                    if isinstance(sp, (occ.Face, occ.Shell)) and not isinstance(sp, MeshShape):
                        n, off = _splitting_plane(sp)
                        nxt += [build.held(x) for x in m.split_by_plane(tuple(n), off)]
                    else:
                        m, tool = build._agreed([m, _union(_meshes(sp))])
                        nxt += [build.held(x) for x in m.split(tool)]
                parts = nxt
            pieces += [p for m in parts if not m.is_empty() for p in m.decompose()]
        return MeshCompound([MeshSolid(p) for p in pieces])

    def distance(self, other):
        a, b = _union([s.m for s in self._solids()]), _union(_meshes(other))
        bb = np.array([a.bounding_box(), b.bounding_box()])
        span = np.linalg.norm(bb[:, 3:].max(0) - bb[:, :3].min(0)) + 1.0
        return float(a.min_gap(b, span))

    def distances(self, *others):
        return (self.distance(o) for o in others)

    def isInside(self, point, tolerance=1e-6):
        p = vec3(point)
        probe = m3d.Manifold.cube((2 * tolerance,) * 3, True).translate(tuple(p))
        return any((s.m ^ probe).volume() > 0 for s in self._solids())

    # Placement.
    def _mapped(self, fn):
        raise NotImplementedError

    def transformShape(self, tMatrix):
        mat = _matrix_of(tMatrix)
        return self._mapped(lambda m: m.transform(mat))

    def transformGeometry(self, tMatrix):
        return self.transformShape(tMatrix)

    def translate(self, vector):
        v = tuple(vec3(vector))
        return self._mapped(lambda m: m.translate(v))

    def rotate(self, startVector, endVector, angleDegrees):
        a, b = vec3(startVector), vec3(endVector)
        from OCP.gp import gp_Ax1, gp_Dir, gp_Pnt, gp_Trsf
        t = gp_Trsf()
        t.SetRotation(gp_Ax1(gp_Pnt(*a), gp_Dir(*(b - a))), math.radians(angleDegrees))
        mat = _matrix_of(t)
        return self._mapped(lambda m: m.transform(mat))

    def scale(self, factor):
        return self._mapped(lambda m: m.scale((factor,) * 3))

    def mirror(self, mirrorPlane="XY", basePointVector=(0, 0, 0)):
        if isinstance(mirrorPlane, str):
            n = {"XY": (0, 0, 1), "YX": (0, 0, 1), "XZ": (0, 1, 0), "ZX": (0, 1, 0),
                 "YZ": (1, 0, 0), "ZY": (1, 0, 0)}[mirrorPlane.upper()]
        else:
            n = tuple(vec3(mirrorPlane))
        p = vec3(basePointVector)
        return self._mapped(lambda m: m.translate(tuple(-p)).mirror(n).translate(tuple(p)))

    def located(self, loc):
        return self.moved(loc)

    def locate(self, loc):
        return self.moved(loc)

    def move(self, *args, **kwargs):
        return self.moved(*args, **kwargs)

    def moved(self, *args, **kwargs):
        if kwargs or (args and isinstance(args[0], (int, float))):
            loc = Location(*args, **kwargs) if not kwargs else Location(
                Vector(kwargs.get("x", 0), kwargs.get("y", 0), kwargs.get("z", 0)))
            if kwargs and any(kwargs.get(k) for k in ("rx", "ry", "rz")):
                raise NotImplementedError("meshcad: moved(rx=...)")
            return self.transformShape(loc)
        if len(args) == 1 and isinstance(args[0], (Location,)):
            return self.transformShape(args[0])
        if len(args) == 1 and isinstance(args[0], (Vector, tuple)) and not (
                isinstance(args[0], tuple) and args[0] and isinstance(args[0][0], (Location, Vector, tuple))):
            return self.translate(args[0])
        locs = args[0] if len(args) == 1 else args
        out = []
        for loc in locs:
            out.append(self.transformShape(loc) if isinstance(loc, Location) else self.translate(loc))
        return MeshCompound(out)

    # Output.
    def tessellate(self, tolerance=None, angularTolerance=None):
        mesh = _union([s.m for s in self._solids()]).to_mesh64()
        V = np.asarray(mesh.vert_properties)[:, :3]
        T = np.asarray(mesh.tri_verts, np.int64).reshape(-1, 3)
        return [Vector(*p) for p in V], [tuple(map(int, t)) for t in T]

    def exportStl(self, fileName, tolerance=None, angularTolerance=None, ascii=False,
                  relative=True, parallel=True):
        from .write import write_stl
        write_stl(self, fileName)
        return True

    def exportStep(self, fileName, **kwargs):
        raise NoBrep("meshcad: a mesh solid writes .stl/.step.mesh/.glb, not STEP")

    def export(self, fname, tolerance=0.1, angularTolerance=0.1, opt=None):
        from cadquery.occ_impl.exporters import export
        export(self, fname, tolerance=tolerance, angularTolerance=angularTolerance, opt=opt)

    def fillet(self, radius, edgeList):
        from .fillet import fillet
        return fillet(self, radius, list(edgeList))

    def chamfer(self, length, length2, edgeList):
        from .fillet import chamfer
        return chamfer(self, length, length2, list(edgeList))

    def shell(self, faceList, thickness, tolerance=0.0001, kind="arc"):
        raise NotImplementedError("meshcad: shell")

    def __iter__(self):
        return iter(self.Solids())

    def __repr__(self):
        return f"<{type(self).__name__} {len(self._solids())} solid(s)>"


class MeshSolid(MeshShape, occ.Solid):
    """One Manifold: a solid, or several disjoint ones a cut left apart."""

    def __init__(self, m, rounds=None):
        if m is self:                     # Solid(mesh_solid), as CadQuery unpacks a compound
            return
        self._m = m
        self._rounds = rounds
        self._topo = None
        self._parts = None

    # A RUN OF FILLETS IS ONE EDIT. OCCT rounds an edge by editing the faces beside it, so a
    # round that reaches through to another feature leaves that feature's edges standing for
    # the next fillet to select, and the run as a whole comes out right. A boolean would cut
    # them away. So fillets after fillets select on the solid before the first of them, and
    # their fills and cuts are applied together when the solid is next used.
    @property
    def m(self):
        if self._m is None:
            base, fills, cuts = self._rounds
            m = base.m
            if fills:
                m = build.boolean([m] + fills, m3d.OpType.Add)
            if cuts:
                m = build.boolean([m] + cuts, m3d.OpType.Subtract)
            self._m = m
        return self._m

    def rounds(self):
        """(solid the run of fillets selects on, fills, cuts)."""
        return self._rounds if self._rounds is not None else (self, [], [])

    def _solids(self):
        return [self]

    def Solids(self):
        """The solids apart, each with the voids inside it: OCCT's solid holds a void as a
        second shell, and Manifold's as a component of its own, inside out."""
        if self._parts is None:
            parts = self.m.decompose()
            solids = [p for p in parts if p.volume() > 0]
            if len(solids) <= 1:
                self._parts = [self]
            else:
                held = [[s] for s in solids]
                boxes = np.array([s.bounding_box() for s in solids])
                sizes = np.prod(boxes[:, 3:] - boxes[:, :3], axis=1)
                for void in (p for p in parts if p.volume() <= 0):
                    b = np.array(void.bounding_box())
                    around = np.nonzero(np.all(boxes[:, :3] <= b[:3], axis=1)
                                        & np.all(boxes[:, 3:] >= b[3:], axis=1))[0]
                    if len(around):
                        held[around[np.argmin(sizes[around])]].append(void)
                self._parts = [MeshSolid(g[0] if len(g) == 1 else m3d.Manifold.compose(g))
                               for g in held]
        return list(self._parts)

    def ShapeType(self):
        return "Solid" if len(self.Solids()) <= 1 else "Compound"

    def geomType(self):
        return "SOLID"

    def _mapped(self, fn):
        return MeshSolid(fn(self.m))

    def _mass(self):
        mesh = self.m.to_mesh64()
        V = np.asarray(mesh.vert_properties)[:, :3]
        T = np.asarray(mesh.tri_verts, np.int64).reshape(-1, 3)
        a, b, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
        vol = np.einsum("ij,ij->i", a, np.cross(b, c)) / 6.0
        tot = vol.sum()
        cen = ((a + b + c) / 4.0 * vol[:, None]).sum(0) / tot if tot else np.zeros(3)
        return float(tot), cen

    def _topology(self):
        if self._rounds is not None:
            return self._rounds[0]._topology()
        if self._topo is None:
            self._topo = _MeshTopology(self)
        return self._topo


class MeshCompound(MeshShape, occ.Compound):
    """Several mesh shapes held together without fusing them, as an OCCT compound would."""

    def __init__(self, parts):
        if parts is self:
            return
        flat = []
        for p in parts:
            flat += p.parts if isinstance(p, MeshCompound) else [p]
        self.parts = flat

    def _solids(self):
        return [s for p in self.parts for s in p._solids()]

    def Solids(self):
        return [s for p in self.parts for s in p.Solids()]

    def ShapeType(self):
        return "Compound"

    def geomType(self):
        return "COMPOUND"

    def __bool__(self):
        return bool(self.parts)

    def __iter__(self):
        return iter(self.parts)

    def _mapped(self, fn):
        return MeshCompound([p._mapped(fn) for p in self.parts])

    def fuse(self, *others, glue=False, tol=None):
        ms = [s.m for s in self._solids()] + [m for o in others for m in _meshes(o)]
        if not ms:
            return self
        return MeshSolid(build.boolean(ms, m3d.OpType.Add))

    def fillet(self, radius, edgeList):
        edges = list(edgeList)
        out = []
        for s in self._solids():
            mine = [e for e in edges if e.owner is s.rounds()[0]]
            out.append(s.fillet(radius, mine) if mine else s)
        return out[0] if len(out) == 1 else MeshCompound(out)

    def chamfer(self, length, length2, edgeList):
        edges = list(edgeList)
        out = []
        for s in self._solids():
            mine = [e for e in edges if e.owner is s.rounds()[0]]
            out.append(s.chamfer(length, length2, mine) if mine else s)
        return out[0] if len(out) == 1 else MeshCompound(out)


def _meshes(shape):
    if isinstance(shape, MeshShape):
        return [s.m for s in shape._solids()]
    if hasattr(shape, "vals"):
        return [m for v in shape.vals() for m in _meshes(v)]
    if isinstance(shape, occ.Compound) and not isinstance(shape, MeshShape):
        kids = list(shape)
        if all(isinstance(k, MeshShape) for k in kids):
            return [m for k in kids for m in _meshes(k)]
    return [s.m for s in lift(shape)._solids()]


def lift(shape):
    """An OCCT shape as a mesh: what a builder the kernel does not patch hands back (a solid
    sewn from faces, a prism made through OCP directly), the moment it meets a mesh. Each
    solid is tessellated under the rule, on a copy, and its faces recorded off OCCT's own
    surfaces."""
    from .imports import occ_solid_mesh
    if isinstance(shape, MeshShape):
        return shape
    if not isinstance(shape, occ.Shape):
        raise TypeError(f"meshcad: {type(shape).__name__} is not a shape")
    src = caller()
    solids = [occ_solid_mesh(s.copy().wrapped, src) for s in occ.Shape.Solids(shape)]
    if not solids:
        raise TypeError(f"meshcad: a {type(shape).__name__} with no solid in it is not a mesh solid")
    return solids[0] if len(solids) == 1 else MeshCompound(solids)


_occ_bool_op = occ.Shape._bool_op


def _bool_op(self, args, tools, op, parallel=True):
    """OCCT's boolean, unless a mesh is among its operands: then every operand is lifted and
    the boolean is the kernel's."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
    args, tools = list(args), list(tools)
    if not any(isinstance(x, MeshShape) for x in args + tools):
        return _occ_bool_op(self, args, tools, op, parallel)
    base = lift(args[0]) if len(args) == 1 else MeshCompound([lift(a) for a in args])
    if isinstance(op, BRepAlgoAPI_Cut):
        return base.cut(*tools)
    if isinstance(op, BRepAlgoAPI_Fuse):
        return base.fuse(*tools)
    if isinstance(op, BRepAlgoAPI_Common):
        return base.intersect(*tools)
    raise NoBrep(f"meshcad: an OCCT {type(op).__name__} on a mesh has no kernel equivalent")


def _free_boolean(name, orig):
    """CadQuery's free `fuse`/`cut`/`intersect`, which build OCCT's BOPAlgo_BOP themselves
    rather than through `_bool_op`: the kernel's boolean when a mesh is among the operands."""
    def op(s1, s2, *rest, **kw):
        shapes = [s1, s2, *(x for x in rest if isinstance(x, occ.Shape))]
        if not any(isinstance(x, MeshShape) for x in shapes):
            return orig(s1, s2, *rest, **kw)
        base = lift(s1)
        return getattr(base, name)(*shapes[1:])
    op.__name__ = name
    return op


def _union(ms):
    return ms[0] if len(ms) == 1 else build.boolean(ms, m3d.OpType.Add)


def _each(shape, fn):
    if isinstance(shape, MeshCompound):
        return MeshCompound([MeshSolid(fn(s.m)) for s in shape._solids()])
    return MeshSolid(fn(shape.m))


def _splitting_plane(face):
    n = vec3(face.normalAt())
    c = vec3(face.Center())
    return n, float(np.dot(n, c))


def _filtered(objs, selector):
    if selector is not None:
        from cadquery.selectors import StringSyntaxSelector, Selector
        sel = StringSyntaxSelector(selector) if isinstance(selector, str) else selector
        objs = sel.filter(objs)
    return occ.Compound.makeCompound(objs)


# --- Faces, edges, vertices ---------------------------------------------------------

class _MeshTopology:
    def __init__(self, solid):
        t = Topology(solid.m)
        self.t = t
        self.faces = [MeshFace(solid, self, i) for i in range(len(t.face_surface))]
        self._vertex = {}
        self.edge_objs = [MeshEdge(solid, self, i) for i in range(len(t.edges))]
        self.vertex_objs = [self.vertex(v) for v in t.corners]

    def vertex(self, vid):
        if vid not in self._vertex:
            self._vertex[vid] = occ.Vertex.makeVertex(*self.t.V[vid])
        return self._vertex[vid]


class MeshFace(MeshShape, occ.Face):
    def __init__(self, owner, topo=None, index=None):
        if owner is self:
            return
        self.owner, self.topo, self.index = owner, topo, index
        self.tris = topo.t.face_tris[index]
        self.rec = topo.t.face_record(index)

    def _solids(self):
        return []

    def ShapeType(self):
        return "Face"

    def geomType(self):
        return GEOM.get(self.rec["kind"], "BSPLINE") if self.rec else "OTHER"

    def Faces(self):
        return [self]

    def Area(self):
        return float(self.topo.t.tri_area[self.tris].sum())

    def Center(self):
        w = self.topo.t.tri_area[self.tris]
        return Vector(*((self.topo.t.tri_c[self.tris] * w[:, None]).sum(0) / w.sum()))

    def BoundingBox(self, tolerance=None, optimal=False):
        p = self.topo.t.V[np.unique(self.topo.t.T[self.tris])]
        return _bbox(p.min(0), p.max(0))

    def normalAt(self, locationVector=None):
        t = self.topo.t
        if self.rec is not None and self.rec["kind"] == "PLANE":
            n = (t.tri_n[self.tris] * t.tri_area[self.tris, None]).sum(0)
            return Vector(*(n / np.linalg.norm(n)))
        p = vec3(locationVector) if locationVector is not None else vec3(self.Center())
        k = self.tris[np.argmin(np.linalg.norm(t.tri_c[self.tris] - p, axis=1))]
        return Vector(*t.tri_n[k])

    def Edges(self):
        return [self.topo.edge_objs[i] for i in self.topo.t.face_edges[self.index]]

    def Vertices(self):
        seen = {}
        for e in self.Edges():
            for v in e.Vertices():
                seen[id(v)] = v
        return list(seen.values())

    def Wires(self):
        return _face_wires(self)

    def outerWire(self):
        return self.Wires()[0]

    def innerWires(self):
        return self.Wires()[1:]

    def toPln(self):
        from OCP.gp import gp_Dir, gp_Pln, gp_Pnt
        return gp_Pln(gp_Pnt(*vec3(self.Center())), gp_Dir(*vec3(self.normalAt())))

    def Volume(self, tol=None):
        return 0.0

    def radius(self):
        if self.rec and "r" in self.rec:
            return self.rec["r"]
        raise ValueError("meshcad: this face has no radius")

    def source(self):
        return self.rec.get("src") if self.rec else None

    def to_occ(self):
        """This face as an OCCT face, built on its own boundary: exact for a plane."""
        if self.geomType() != "PLANE":
            raise NoBrep(f"meshcad: a {self.geomType()} mesh face has no OCCT equivalent")
        wires = self.Wires()
        return occ.Face.makeFromWires(wires[0], wires[1:])


class MeshEdge(MeshShape, occ.Edge):
    def __init__(self, owner, topo=None, index=None):
        if owner is self:
            return
        self.owner, self.topo, self.index = owner, topo, index
        ch = topo.t.edges[index]
        self.vids = ch["verts"]
        self.pts = topo.t.V[self.vids]
        self.closed = ch["closed"]
        self.face_ids = ch["faces"]
        recs = [topo.t.face_record(f) for f in self.face_ids]
        self.kind, self.circle = classify(self.pts, self.closed, recs)

    def _solids(self):
        return []

    def ShapeType(self):
        return "Edge"

    def geomType(self):
        return self.kind

    def Edges(self):
        return [self]

    def faces_of(self):
        return [self.topo.faces[f] for f in self.face_ids]

    def Vertices(self):
        if self.closed:
            return [self.topo.vertex(self.vids[0])]
        return [self.topo.vertex(self.vids[0]), self.topo.vertex(self.vids[-1])]

    def IsClosed(self):
        return self.closed

    def _lengths(self):
        seg = np.linalg.norm(np.diff(self.pts, axis=0), axis=1)
        return seg, np.concatenate([[0], np.cumsum(seg)])

    def Length(self):
        if self.kind == "CIRCLE" and self.closed:
            return 2 * math.pi * self.circle[2]
        if self.kind == "CIRCLE":
            c, d, r = self.circle
            a, b = self.pts[0] - c, self.pts[-1] - c
            mid = self.pts[len(self.pts) // 2] - c
            ang = _arc_angle(a, mid, b, d)
            return r * ang
        return float(self._lengths()[0].sum())

    def Center(self):
        seg, _ = self._lengths()
        mids = (self.pts[1:] + self.pts[:-1]) / 2
        return Vector(*((mids * seg[:, None]).sum(0) / seg.sum()))

    def BoundingBox(self, tolerance=None, optimal=False):
        return _bbox(self.pts.min(0), self.pts.max(0))

    def startPoint(self):
        return Vector(*self.pts[0])

    def endPoint(self):
        return Vector(*self.pts[-1])

    def positionAt(self, d, mode="length"):
        seg, cum = self._lengths()
        s = d * cum[-1]
        i = min(np.searchsorted(cum, s, side="right") - 1, len(seg) - 1)
        f = (s - cum[i]) / seg[i] if seg[i] else 0.0
        return Vector(*(self.pts[i] + f * (self.pts[i + 1] - self.pts[i])))

    def tangentAt(self, locationParam=0.5, mode="length"):
        if self.kind == "LINE":
            t = self.pts[-1] - self.pts[0]
            return Vector(*(t / np.linalg.norm(t)))
        seg, cum = self._lengths()
        s = locationParam * cum[-1]
        i = min(np.searchsorted(cum, s, side="right") - 1, len(seg) - 1)
        t = self.pts[i + 1] - self.pts[i]
        return Vector(*(t / np.linalg.norm(t)))

    def radius(self):
        if self.kind != "CIRCLE":
            raise ValueError("Shape could not be reduced to a circle")
        return self.circle[2]

    def arcCenter(self):
        if self.kind != "CIRCLE":
            raise ValueError("meshcad: not a circle")
        return Vector(*self.circle[0])

    def normal(self):
        if self.kind == "CIRCLE":
            return Vector(*self.circle[1])
        raise ValueError("meshcad: an edge that is not a circle has no normal")

    def Volume(self, tol=None):
        return 0.0

    def to_occ(self):
        """This edge as an OCCT edge: exact when it is a line or a circle."""
        if self.kind == "LINE":
            return occ.Edge.makeLine(Vector(*self.pts[0]), Vector(*self.pts[-1]))
        if self.kind == "CIRCLE" and self.closed:
            c, d, r = self.circle
            return occ.Edge.makeCircle(r, Vector(*c), Vector(*d))
        if self.kind == "CIRCLE":
            return occ.Edge.makeThreePointArc(Vector(*self.pts[0]), Vector(*self.pts[len(self.pts) // 2]),
                                              Vector(*self.pts[-1]))
        return occ.Edge.makeSpline([Vector(*p) for p in self.pts])


def _arc_angle(a, mid, b, axis):
    def ang(u, v):
        return math.atan2(np.dot(np.cross(u, v), axis), np.dot(u, v))
    t1 = ang(a, mid) % (2 * math.pi)
    t2 = ang(a, b) % (2 * math.pi)
    return t2 if t1 <= t2 else 2 * math.pi - t2


def _face_wires(face):
    """The face's boundary loops as OCCT wires, the outer (largest) first."""
    edges = face.Edges()
    loops, left = [], list(edges)
    while left:
        e = left.pop(0)
        if e.closed:
            loops.append([e])
            continue
        loop = [e]
        start, end = e.vids[0], e.vids[-1]
        while end != start:
            nxt = next((x for x in left if end in (x.vids[0], x.vids[-1])), None)
            if nxt is None:
                break
            left.remove(nxt)
            loop.append(nxt)
            end = nxt.vids[-1] if nxt.vids[0] == end else nxt.vids[0]
        loops.append(loop)
    n = vec3(face.normalAt())
    _, x, y = axis_frame(n)

    def area(loop):
        p = np.concatenate([e.pts for e in loop])
        p2 = np.stack([p @ x, p @ y], 1)
        return abs(0.5 * (np.dot(p2[:, 0], np.roll(p2[:, 1], -1)) - np.dot(p2[:, 1], np.roll(p2[:, 0], -1))))

    loops.sort(key=area, reverse=True)
    return [occ.Wire.assembleEdges([e.to_occ() for e in loop]) for loop in loops]


# --- Builders under CadQuery's names ------------------------------------------------

def _ax2(pnt, dir_):
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
    ax = gp_Ax2(gp_Pnt(*vec3(pnt)), gp_Dir(*vec3(dir_)))
    return (np.array(ax.XDirection().Coord()), np.array(ax.YDirection().Coord()),
            np.array(ax.Direction().Coord()))


def make_box(cls, length, width, height, pnt=Vector(0, 0, 0), dir=Vector(0, 0, 1)):
    x, y, z = _ax2(pnt, dir)
    return MeshSolid(build.solid(build.box(vec3(pnt), x, y, z, length, width, height, caller())))


def _circle_loop(center, axis, r):
    pts = circle_points(center, axis, r)
    return Loop(pts, np.zeros(len(pts), np.int64), [Curve("CIRCLE", np.asarray(center, float),
                                                           np.asarray(axis, float), r)])


def _poly_loop(pts, curves=None):
    pts = np.asarray(pts, float)
    return Loop(pts, np.arange(len(pts)), curves or [Curve("LINE") for _ in pts])


def make_cylinder(cls, radius, height, pnt=Vector(0, 0, 0), dir=Vector(0, 0, 1), angleDegrees=360):
    p, d = vec3(pnt), vec3(dir)
    d = d / np.linalg.norm(d)
    src = caller()
    if abs(angleDegrees - 360) < 1e-9:
        part = build.prism([_circle_loop(p, d, radius)], d, d * height, src, "cylinder")
    else:
        x = axis_frame(d)[1]
        prof = _poly_loop([p, p + radius * x, p + radius * x + height * d, p + height * d])
        part = build.revolve([prof], p, d, angleDegrees, src, "cylinder")
    return MeshSolid(build.solid(part))


def make_cone(cls, radius1, radius2, height, pnt=Vector(0, 0, 0), dir=Vector(0, 0, 1), angleDegrees=360):
    p, d = vec3(pnt), vec3(dir)
    d = d / np.linalg.norm(d)
    x = axis_frame(d)[1]
    prof = _poly_loop([p, p + radius1 * x, p + radius2 * x + height * d, p + height * d])
    return MeshSolid(build.solid(build.revolve([prof], p, d, angleDegrees, caller(), "cone")))


def make_sphere(cls, radius, pnt=Vector(0, 0, 0), dir=Vector(0, 0, 1), angleDegrees1=0,
                angleDegrees2=90, angleDegrees3=360):
    c, d = vec3(pnt), vec3(dir)
    d = d / np.linalg.norm(d)
    x = axis_frame(d)[1]
    a1, a2 = math.radians(angleDegrees1), math.radians(angleDegrees2)
    s, e = c + radius * (math.cos(a1) * x + math.sin(a1) * d), c + radius * (math.cos(a2) * x + math.sin(a2) * d)
    arc = circle_points(c, np.cross(x, d), radius, s, e, ccw_about=np.cross(x, d))
    top, bot = c + radius * math.sin(a2) * d, c + radius * math.sin(a1) * d
    pts = np.concatenate([[bot], arc, [top]])
    curves = [Curve("LINE"), Curve("CIRCLE", c, np.cross(x, d), radius), Curve("LINE"), Curve("LINE")]
    seg = np.concatenate([[0], np.full(len(arc) - 1, 1), [2], [3]])
    loop = build.clean_loop(Loop(pts, seg, curves))
    return MeshSolid(build.solid(build.revolve([loop], c, d, angleDegrees3, caller(), "sphere")))


def make_torus(cls, radius1, radius2, pnt=Vector(0, 0, 0), dir=Vector(0, 0, 1), angleDegrees1=0,
               angleDegrees2=360):
    c, d = vec3(pnt), vec3(dir)
    d = d / np.linalg.norm(d)
    x = axis_frame(d)[1]
    loop = _circle_loop(c + radius1 * x, np.cross(x, d), radius2)
    return MeshSolid(build.solid(build.revolve([loop], c, d, 360, caller(), "torus")))


def make_wedge(cls, dx, dy, dz, xmin, zmin, xmax, zmax, pnt=Vector(0, 0, 0), dir=Vector(0, 0, 1)):
    X, Y, Z = _ax2(pnt, dir)
    o = vec3(pnt)
    loc = [(0, 0, 0), (dx, 0, 0), (dx, 0, dz), (0, 0, dz),
           (xmin, dy, zmin), (xmax, dy, zmin), (xmax, dy, zmax), (xmin, dy, zmax)]
    pts = np.array([o + a * X + b * Y + cc * Z for a, b, cc in loc])
    return MeshSolid(build.solid(build.hull_part(pts, caller(), "wedge")))


def extrude_linear(cls, *args, taper=0, **kwargs):
    loops, normal, rest = _profile(args)
    vec = vec3(rest[0] if rest else kwargs["vecNormal"])
    if len(rest) > 1:
        taper = rest[1]
    if taper:
        raise NotImplementedError("meshcad: extrude with taper")
    return MeshSolid(build.solid(build.prism(loops, normal, vec, caller())))


def extrude_with_rotation(cls, *args, **kwargs):
    raise NotImplementedError("meshcad: extrudeLinearWithRotation")


def revolve_(cls, *args, **kwargs):
    loops, normal, rest = _profile(args)
    angle, a, b = rest[0], vec3(rest[1]), vec3(rest[2])
    return MeshSolid(build.solid(build.revolve(loops, a, b - a, angle, caller())))


def sweep_(cls, *args, makeSolid=True, isFrenet=False, mode=None, transitionMode="transformed", **kw):
    loops, normal, rest = _profile(args)
    path = rest[0]
    if len(rest) > 1:
        makeSolid = rest[1]
    if len(rest) > 2:
        isFrenet = rest[2]
    if len(rest) > 3:
        mode = rest[3]
    from .sweep import sweep
    return MeshSolid(build.solid(sweep(loops, normal, path, isFrenet, mode, caller())))


def sweep_multi(cls, profiles, path, makeSolid=True, isFrenet=False, mode=None):
    raise NotImplementedError("meshcad: sweep_multi")


def make_loft(cls, listOfWire, ruled=False):
    from .sweep import loft
    return MeshSolid(build.solid(loft(list(listOfWire), ruled, caller())))


def loft_(*s, cap=False, ruled=False, **kwargs):
    shapes = list(s[0]) if len(s) == 1 and isinstance(s[0], (list, tuple)) else list(s)
    wires = [x.outerWire() if isinstance(x, occ.Face) else x for x in shapes]
    from .sweep import loft
    return MeshSolid(build.solid(loft(wires, ruled, caller())))


def make_compound(cls, listOfShapes):
    shapes = list(listOfShapes)
    if shapes and any(isinstance(s, MeshShape) for s in shapes):
        if not all(isinstance(s, MeshShape) for s in shapes):
            mesh = [s for s in shapes if isinstance(s, MeshShape)]
            if all(isinstance(s, (MeshFace, MeshEdge)) or isinstance(s, occ.Vertex) for s in shapes):
                return _Selection(shapes)
            return MeshCompound([lift(s) for s in shapes])
        if all(isinstance(s, (MeshFace, MeshEdge)) for s in shapes):
            return _Selection(shapes)
        return MeshCompound(shapes)
    return _ORIG["makeCompound"].__func__(cls, shapes)


class _Selection(list):
    """Faces or edges picked off a mesh solid, standing where CadQuery expects a compound."""

    def Faces(self):
        return [s for s in self if isinstance(s, MeshFace)]

    def Edges(self):
        return [e for s in self for e in (s.Edges() if isinstance(s, MeshFace) else [s] if isinstance(s, MeshEdge) else [])]

    def Vertices(self):
        return [v for s in self for v in s.Vertices()]

    def Center(self):
        return occ.Shape.CombinedCenter(list(self))

    @property
    def wrapped(self):
        """The picked faces and edges as one OCCT compound, for code that hands them to OCP."""
        return _ORIG["makeCompound"].__func__(
            occ.Compound, [s.to_occ() if isinstance(s, (MeshFace, MeshEdge)) else s for s in self]).wrapped


def make_text(cls, text, size, height, font="Arial", fontPath=None, kind="regular",
              halign="center", valign="center", position=Plane.XY()):
    flat = _ORIG["makeText"].__func__(cls, text, size, 0, font, fontPath, kind, halign, valign, position)
    if height == 0:
        return flat
    vec = vec3(position.zDir) * height
    src = caller()
    ms = [build.solid(build.prism(face_loops(f), vec3(f.normalAt()), vec, src, "text"))
          for f in flat.Faces()]
    return MeshSolid(_union(ms))


def compute_mass(obj, tol=None):
    if isinstance(obj, MeshFace):
        return obj.Area()
    if isinstance(obj, MeshEdge):
        return obj.Length()
    if isinstance(obj, MeshShape):
        return obj.Volume()
    return _ORIG["computeMass"](obj, tol)


def center_of_mass(obj):
    if isinstance(obj, MeshShape):
        return obj.Center()
    return _ORIG["centerOfMass"](obj)


def combined_center_bb(objects):
    lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
    for o in objects:
        bb = o.BoundingBox()
        lo = np.minimum(lo, (bb.xmin, bb.ymin, bb.zmin))
        hi = np.maximum(hi, (bb.xmax, bb.ymax, bb.zmax))
    return Vector(*((lo + hi) / 2))


_ORIG = {}


def _shape_new(cls, *args, **kwargs):
    """`Face(mesh_face)`, `Solid(mesh_solid)`: CadQuery re-wrapping a shape it already has
    gets the same mesh shape back."""
    if args and isinstance(args[0], MeshShape) and isinstance(args[0], cls):
        return args[0]
    return object.__new__(cls)


def install():
    """Put the mesh builders under CadQuery's class names. Call before cadquery.cq imports."""
    S, C, Sh = occ.Solid, occ.Compound, occ.Shape
    Sh.__new__ = _shape_new
    _ORIG.update(makeCompound=C.__dict__["makeCompound"], makeText=C.__dict__["makeText"],
                 computeMass=Sh.computeMass, centerOfMass=Sh.centerOfMass)
    for name, fn in (("makeBox", make_box), ("makeCylinder", make_cylinder), ("makeCone", make_cone),
                     ("makeSphere", make_sphere), ("makeTorus", make_torus), ("makeWedge", make_wedge),
                     ("extrudeLinear", extrude_linear),
                     ("extrudeLinearWithRotation", extrude_with_rotation), ("revolve", revolve_),
                     ("sweep", sweep_), ("sweep_multi", sweep_multi), ("makeLoft", make_loft)):
        setattr(S, name, classmethod(fn))
    C.makeCompound = classmethod(make_compound)
    C.makeText = classmethod(make_text)
    Sh.computeMass = staticmethod(compute_mass)
    Sh.centerOfMass = staticmethod(center_of_mass)
    Sh.CombinedCenterOfBoundBox = staticmethod(combined_center_bb)
    Sh._bool_op = _bool_op
    occ.loft = loft_
    import cadquery.func as func
    for name in ("fuse", "cut", "intersect"):
        free = _free_boolean(name, getattr(occ, name))
        setattr(occ, name, free)
        setattr(func, name, free)
