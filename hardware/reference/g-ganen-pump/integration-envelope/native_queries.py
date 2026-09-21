"""Native occupied-region queries for separate, possibly overlapping envelopes.

Intersection distributes over a union. Cutting each native solid separately
preserves occupied space without constructing partitions between overlapping
components. The returned compound retains overlaps; its summed volume is not a
material volume or a union-volume measurement.
"""
import cadquery as cq


def intersect_components(shape, cutter):
    fragments = []
    for component in shape.Solids():
        fragments.extend(component.intersect(cutter).Solids())
    return cq.Compound.makeCompound(fragments)


def occupied_bounds(shape):
    """XYZ min/max of occupied solids, or None for an empty intersection."""
    if not shape.Solids():
        return None
    box = shape.BoundingBox()
    return [[box.xmin, box.ymin, box.zmin], [box.xmax, box.ymax, box.zmax]]
