"""Experimental elbow with its exterior filled vertically down to the bed.

Each upward-facing exterior triangle is extended straight down to Z0. Their
union follows the original roof; no global convex hull bridges the bend.
The unchanged functional bores are cut once afterward. There are no exterior
clamp channels. Circular clamp access is not part of this print specimen.
"""
from dataclasses import dataclass
import math

import cadquery as cq
import manifold3d as md
import numpy as np
import trimesh

from tpu_elbow import Elbow


_PRISM_FACES = np.array([[0, 1, 2], [5, 4, 3], [0, 3, 4], [0, 4, 1],
                         [1, 4, 5], [1, 5, 2], [2, 5, 3], [2, 3, 0]],
                        dtype=np.uint64)


def shape_mesh(shape):
    """Tessellate the native surface at 0.01 mm chord tolerance."""
    vertices, faces = shape.tessellate(.01, .10)
    mesh = trimesh.Trimesh([v.toTuple() for v in vertices], faces, process=True)
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    return mesh


def manifold(mesh):
    raw = md.Mesh64(np.asarray(mesh.vertices, dtype=np.float64),
                    np.asarray(mesh.faces, dtype=np.uint64))
    raw.merge()
    result = md.Manifold(raw)
    if result.status() != md.Error.NoError:
        raise ValueError(f"Invalid mesh for downward fill: {result.status()}")
    return result


def joined(body):
    # Reset prism provenance so coincident vertical faces simplify together.
    # Only numerical debris below 0.001 mm3 may be discarded.
    pieces = sorted(body.decompose(), key=lambda part: part.volume(), reverse=True)
    if not pieces or sum(abs(p.volume()) for p in pieces[1:]) > .001:
        raise ValueError("Downward stock did not join into one body")
    result = pieces[0].as_original().set_tolerance(.001).simplify(.001)
    pieces = sorted(result.decompose(), key=lambda part: part.volume(), reverse=True)
    if sum(abs(p.volume()) for p in pieces[1:]) > .001:
        raise ValueError("Downward stock has disconnected material")
    return pieces[0]


def print_mesh(body):
    raw = body.to_mesh64()
    mesh = trimesh.Trimesh(np.asarray(raw.vert_properties)[:, :3],
                           np.asarray(raw.tri_verts), process=True)
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    return mesh


@dataclass(frozen=True)
class BedSupportedElbow(Elbow):
    def _pose(self, shape):
        s = 1 / math.sqrt(2)
        posed = shape.moved(cq.Location(cq.Plane(
            origin=(0, 0, 0), xDir=(s, 0, -s), normal=(0, -1, 0))))
        xmin = (-self.barb_depth-self.barb_od/2) / math.sqrt(2)
        xmax = (self.axis+self.tube_od/2+self.mouth) / math.sqrt(2)
        foot = self.axis/math.sqrt(2) + self.passage/2 + self.wall
        return posed.translate((-(xmin+xmax)/2, 0, foot))

    def cavity(self):
        """Exact functional lumen, with each socket open beyond its mouth."""
        x = lambda r, a, b: cq.Solid.makeCylinder(
            r, b-a, cq.Vector(a, 0, 0), cq.Vector(1, 0, 0))
        y = lambda r, a, b: cq.Solid.makeCylinder(
            r, b-a, cq.Vector(self.axis, a, 0), cq.Vector(0, 1, 0))
        lead = self.entry * math.tan(math.radians(60))
        cavity = x(self.barb_bore/2, -100, 0).fuse(
            cq.Solid.makeCone(self.barb_bore/2+self.entry,
                             self.barb_bore/2, lead,
                             cq.Vector(-self.barb_depth, 0, 0), cq.Vector(1, 0, 0)),
            x(self.passage/2, 0, self.axis),
            y(self.passage/2, 0, self.tube_stop),
            y(self.tube_bore/2, self.tube_stop, 100),
            cq.Solid.makeCone(self.tube_bore/2, self.tube_bore/2+self.entry,
                             lead, cq.Vector(self.axis, self.mouth-lead, 0),
                             cq.Vector(0, 1, 0)))
        return self._pose(cavity)

    def support_envelope(self):
        """Downward closure of the original unbored exterior, as a manifold.

        The roof of each local triangular prism is an original surface facet.
        Its other end is directly below at Z0. Unioning these individual
        prisms fills below the roof without adding a convex bridge above it.
        """
        exterior = shape_mesh(super().print_shape(exterior=True))
        roofs = exterior.triangles[exterior.face_normals[:, 2] > 1e-7]
        prisms = []
        for triangle in roofs:
            floor = triangle.copy()
            floor[:, 2] = 0
            raw = md.Mesh64(np.asarray(np.vstack((triangle, floor)), dtype=np.float64),
                            _PRISM_FACES)
            raw.merge()
            prism = md.Manifold(raw)
            if prism.status() != md.Error.NoError:
                raise ValueError(f"Invalid vertical prism: {prism.status()}")
            prisms.append(prism)
        return joined(md.Manifold.batch_boolean(prisms, md.OpType.Add))

    def print_mesh(self):
        envelope = self.support_envelope()
        lumen = manifold(shape_mesh(self.cavity()))
        return print_mesh(joined(envelope - lumen))


def build():
    """One downward-filled elbow mesh in its bed-flat print orientation."""
    return BedSupportedElbow().print_mesh()
