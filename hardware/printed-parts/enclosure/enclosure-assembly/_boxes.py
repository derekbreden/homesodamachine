"""Bounding boxes for the placed world's immutable solids, computed once.

`cq.Shape.BoundingBox()` runs `BRepBndLib.AddOptimal` — an exact, mesh-based box
that costs ~0.2 s on a pack solid, and CadQuery's own source calls "expensive".
The placed solids are memoized (`_contents.build`, `panel_bodies`,
`placed_funnel`) and never mutate, so their optimal boxes are fixed too. The
consumers that scan the pack — the port frame and front-wall inset
(`_contents`), the enclosure sizing (`enclosure._dims`), each routing `Frame`
(`_routing.frame`) — read the box through `boxed()`, which computes it once per
solid and hands back the same `BoundBox` on every later ask.

Keyed by `id(solid.wrapped)`, which is a stable attribute (not a regenerating
property). The solid is pinned in the cache alongside its box, so its id cannot
be recycled onto a different shape while the entry lives.
"""

_CACHE: dict = {}


def boxed(solid):
    """The solid's optimal bounding box, memoized by identity."""
    key = id(solid.wrapped)
    hit = _CACHE.get(key)
    if hit is not None:
        return hit[1]
    box = solid.BoundingBox()
    _CACHE[key] = (solid, box)          # pin the solid so its id stays its own
    return box
