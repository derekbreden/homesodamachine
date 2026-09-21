"""The print mesh of a solid: an absolute-tolerance triangulation, checked the way a slicer
reads it before it is written.

`faucet_shell.piece_mesh` is where this was learned, and its numbers are the ones here: a
0.005 mm deflection and a 0.05 rad angle, on a copy without cached triangulation, so a round
edge prints as a round and not as a run of facets. The zero-area facets OCC leaves where
rounds meet at a vertex are dropped at single precision, the way the front-top fixture
reconciles its mesh. The file is read back merged by position and refused on a
non-manifold edge or an open one, which is what the bed refuses.
"""

from __future__ import annotations

import io
from pathlib import Path

import numpy as np
import trimesh

from flute_skin import non_manifold_edges

#: Absolute millimetre deflection and angular deflection of a printed surface.
print_mesh_tol = 0.005
print_mesh_angle = 0.05


def print_mesh(solid, tol: float = print_mesh_tol, angle: float = print_mesh_angle) -> trimesh.Trimesh:
    """Absolute-tolerance print mesh, on a copy without cached triangulation."""
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopAbs import TopAbs_REVERSED
    from OCP.TopLoc import TopLoc_Location

    solid = solid.val() if hasattr(solid, "val") else solid
    meshed = solid.copy(mesh=False)
    triangulator = BRepMesh_IncrementalMesh(meshed.wrapped, tol, False, angle, False)
    if not triangulator.IsDone():
        raise ValueError("the absolute-tolerance print triangulation did not finish")
    points, tris = [], []
    for face in meshed.Faces():
        location = TopLoc_Location()
        poly = BRep_Tool.Triangulation_s(face.wrapped, location)
        if poly is None or poly.NbTriangles() == 0:
            raise ValueError("a printable face has no triangulation")
        offset = len(points)
        transform = location.Transformation()
        for i in range(1, poly.NbNodes() + 1):
            point = poly.Node(i).Transformed(transform)
            points.append((point.X(), point.Y(), point.Z()))
        for i in range(1, poly.NbTriangles() + 1):
            a, b, c = poly.Triangle(i).Get()
            if face.wrapped.Orientation() == TopAbs_REVERSED:
                b, c = c, b
            tris.append((offset + a - 1, offset + b - 1, offset + c - 1))
    mesh = trimesh.Trimesh(vertices=points, faces=tris, process=True)
    # AN STL IS SINGLE PRECISION, and OCC can supply a zero-area facet where three rounds meet
    # at a vertex: quantise to what the file will hold, drop what has no area there, and
    # merge by position, which is the mesh the slicer will read.
    mesh.vertices = mesh.vertices.astype(np.float32).astype(np.float64)
    mesh.update_faces(mesh.nondegenerate_faces(height=1e-6))
    mesh.merge_vertices()
    mesh.remove_unreferenced_vertices()
    return mesh


def write_print_stl(solid, path, tol: float = print_mesh_tol, angle: float = print_mesh_angle) -> trimesh.Trimesh:
    """The printed surface at `path`, checked as serialized STL before it lands there."""
    path = Path(path)
    mesh = print_mesh(solid, tol, angle)
    data = mesh.export(file_type="stl")
    written = trimesh.load_mesh(io.BytesIO(data), file_type="stl")
    loose = non_manifold_edges(written)
    if loose or not written.is_watertight or not written.is_winding_consistent:
        raise ValueError(
            f"{path.name}: a slicer refuses this — {loose} non-manifold edge(s), "
            f"watertight={written.is_watertight}, over {len(written.faces)} facets")
    path.write_bytes(data)
    return written
