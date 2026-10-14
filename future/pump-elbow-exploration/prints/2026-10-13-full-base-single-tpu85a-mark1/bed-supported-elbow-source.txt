"""Experimental TPU elbow with a full footprint of stock down to the bed.

The support envelope contains the elbow and its XY projection onto Z0. Two
mouth-open annular channels retain circular clamp access around the cuffs.
The socket bores, stops, insertion lengths and V orientation are Elbow's.
"""
from dataclasses import dataclass
import math

import cadquery as cq
import numpy as np
from scipy.spatial import ConvexHull

from tpu_elbow import Elbow


def _convex_solid(points):
    """Closed native polygonal solid; combine coplanar hull triangles."""
    points = np.asarray(points, dtype=float)
    hull = ConvexHull(points)
    groups = {}
    for triangle, equation in zip(hull.simplices, hull.equations):
        key = tuple(np.round(equation, 8))
        group = groups.setdefault(key, [equation[:3], set()])
        group[1].update(int(i) for i in triangle)
    faces = []
    for normal, indices in groups.values():
        vertices = points[list(indices)]
        centre = vertices.mean(axis=0)
        u = vertices[0] - centre
        u /= np.linalg.norm(u)
        v = np.cross(normal, u)
        order = np.argsort(np.arctan2((vertices-centre) @ v,
                                     (vertices-centre) @ u))
        ring = vertices[order]
        wire = cq.Wire.makePolygon([cq.Vector(*p) for p in ring], close=True)
        faces.append(cq.Face.makeFromWires(wire))
    return cq.Solid.makeSolid(cq.Shell.makeShell(faces))


@dataclass(frozen=True)
class BedSupportedElbow(Elbow):
    channel_width: float = 1.2
    footprint_scale: float = 1.015

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

    def channels(self):
        """1.2 mm radial channels, covering the full 9 mm clamp seats.

        The cutting tools extend outward through each mouth. A 0.001 mm
        inward overlap is removed from the stock only; the original exact
        cuff is subsequently united back into the part.
        """
        out = {}
        for name, radius, origin, direction, length in (
            ("barb", self.barb_od/2, (-100, 0, 0), (1, 0, 0),
             100-self.barb_depth+self.band_width),
            ("tube", self.tube_od/2, (self.axis, self.mouth-self.band_width, 0),
             (0, 1, 0), 100-self.mouth+self.band_width),
        ):
            outer = cq.Solid.makeCylinder(radius+self.channel_width, length,
                                           cq.Vector(*origin), cq.Vector(*direction))
            inner = cq.Solid.makeCylinder(radius-.001, length,
                                           cq.Vector(*origin), cq.Vector(*direction))
            out[name] = self._pose(outer.cut(inner))
        return out

    def support_envelope(self):
        """Convex stock under the complete silhouette, with a broad flat bed.

        Projected vertices are enlarged 1.5% about the centred XY frame,
        covering the 0.01 mm tessellation chord allowance. The native cuff
        surfaces are supplied by the original elbow, not by the hull facets.
        """
        original = super().print_shape()
        vertices, _ = original.tessellate(.01, .08)
        points = np.array([p.toTuple() for p in vertices])
        floor = points.copy()
        floor[:, :2] *= self.footprint_scale
        floor[:, 2] = 0
        return _convex_solid(np.vstack((points, floor)))

    def print_shape(self):
        original = super().print_shape()
        stock = self.support_envelope().cut(self.cavity())
        for channel in self.channels().values():
            stock = stock.cut(channel)
        # Merge the coplanar mouth annuli created by the stock union. This
        # relaxed print body has no expanded installed-envelope tangencies.
        return stock.fuse(original).clean()


def build():
    """One grounded, full-base elbow for the experimental print."""
    return BedSupportedElbow().print_shape()
