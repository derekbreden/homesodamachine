"""Bounding boxes for the placed world's immutable solids, computed once.

`cq.Shape.BoundingBox()` runs `BRepBndLib.AddOptimal` — an exact, mesh-based box
that costs ~0.2 s on a pack solid, and CadQuery's own source calls "expensive".
The placed solids come out of one `enclosure_assembly.build_enclosure_assembly()` and never
mutate, so their optimal boxes are fixed too. The consumers that scan the pack —
the enclosure's sizing and its Z joints (`enclosure._dims`, `_z_joints`), the
scorecard's clearance and clash scans (`_scorecard`), each routing `Frame`
(`_routing.frame`) — read the box through `boxed()`, which computes it once per
solid and hands back the same `BoundBox` on every later ask.

Keyed by `hash(solid.wrapped)` — OCCT's own hash over the underlying TShape, the
location and the orientation, which together are what decide the box. Two wrappers
of one body hash alike, and a moved copy of it does not. `id()` cannot stand in:
`Solids()`, `moved()` and `.val()` each hand back a fresh Python wrapper around the
same body, so an identity key reads a first ask every time and the memo never fires.

A hit is confirmed with `IsSame` before it is served — a hash collision would
otherwise hand back a wrong box, silently, in the reading that decides where a
body stands.
"""

_CACHE: dict = {}
_SOLIDS_CACHE: dict = {}


def boxed(solid):
    """The solid's optimal bounding box, memoized by identity."""
    key = hash(solid.wrapped)
    hit = _CACHE.get(key)
    if hit is not None and hit[0].wrapped.IsSame(solid.wrapped):
        return hit[1]
    box = solid.BoundingBox()
    _CACHE[key] = (solid, box)          # pin the solid so the entry keeps its shape alive
    return box


def boxed_solids(shape) -> list:
    """One box per solid the shape is built from, memoized against the shape.

    The list is memoized against its parent, and each box in it through `boxed`, so a body that
    two shapes are both built from is boxed once between them. Read-only: callers share the list,
    as they share the pack `build()` hands back."""
    key = id(shape.wrapped)
    hit = _SOLIDS_CACHE.get(key)
    if hit is not None:
        return hit[1]
    boxes = [boxed(s) for s in shape.Solids()]
    _SOLIDS_CACHE[key] = (shape, boxes)
    return boxes
