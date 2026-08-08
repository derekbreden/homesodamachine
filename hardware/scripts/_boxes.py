"""Bounding boxes for the placed world's immutable solids, computed once.

`cq.Shape.BoundingBox()` runs `BRepBndLib.AddOptimal` — an exact, mesh-based box
that costs ~0.2 s on a pack solid, and CadQuery's own source calls "expensive".
The placed solids come out of one `enclosure_assembly.build_enclosure_assembly()` and never
mutate, so their optimal boxes are fixed too. The consumers that scan the pack —
the enclosure's sizing and its Z joints (`enclosure._dims`, `_z_joints`), the
scorecard's clearance and clash scans (`_scorecard`), each routing `Frame`
(`_routing.frame`) — read the box through `boxed()`, which computes it once per
solid and hands back the same `BoundBox` on every later ask.

Keyed by `id(solid.wrapped)`, which is a stable attribute (not a regenerating
property). The solid is pinned in the cache alongside its box, so its id cannot
be recycled onto a different shape while the entry lives.
"""

_CACHE: dict = {}
_SOLIDS_CACHE: dict = {}


def boxed(solid):
    """The solid's optimal bounding box, memoized by identity."""
    key = id(solid.wrapped)
    hit = _CACHE.get(key)
    if hit is not None:
        return hit[1]
    box = solid.BoundingBox()
    _CACHE[key] = (solid, box)          # pin the solid so its id stays its own
    return box


def boxed_solids(shape) -> list:
    """One box per solid the shape is built from, memoized against the shape.

    `shape.Solids()` hands back freshly wrapped sub-shapes on every call, so `boxed()` can never
    see the same body twice and the whole list is memoized against its parent instead. Read-only:
    callers share the list, as they share the pack `build()` hands back."""
    key = id(shape.wrapped)
    hit = _SOLIDS_CACHE.get(key)
    if hit is not None:
        return hit[1]
    boxes = [s.BoundingBox() for s in shape.Solids()]
    _SOLIDS_CACHE[key] = (shape, boxes)
    return boxes
