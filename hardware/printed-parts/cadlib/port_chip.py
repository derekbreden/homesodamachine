"""Shared rear-panel label and pocket outline in the fitting's X/Z frame."""

import cadquery as cq


WIDTH = 28.0
LOWER_CORNER_RADIUS = 2.0


def outline(width, top, bottom, thickness, y0=0.0, radius=LOWER_CORNER_RADIUS):
    """A rectangular label with square upper and rounded lower corners."""
    solid = cq.Solid.makeBox(width, thickness, top + bottom,
                            cq.Vector(-width / 2, y0, -bottom))
    lower_edges = [edge for edge in solid.Edges()
                   if abs(edge.Center().z + bottom) < 1e-7
                   and abs(abs(edge.Center().x) - width / 2) < 1e-7
                   and edge.BoundingBox().ylen > thickness - 1e-7]
    assert len(lower_edges) == 2
    return solid.fillet(radius, lower_edges)
