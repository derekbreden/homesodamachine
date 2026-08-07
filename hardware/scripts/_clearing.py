"""How far apart two bodies stand, and how far a line leaving a port gets.

`_overlap` measures the solid two bodies SHARE. These are the two questions on the other side of
zero — the gap between bodies that do not share anything, and the free straight ahead of a mouth
— and both are answered exactly or not at all.

    import _clearing
    _clearing.box_gap(bb_a, bb_b)                 # a lower bound, for prefiltering
    _clearing.gap(a, b)                           # the exact distance, 0 when they touch
    who, free = _clearing.cast(pos, axis, dia, reach, solids, skip=("self",))

A BOUNDING BOX PROVES CLEARANCE AND NEVER PROVES OBSTRUCTION, which is what splits `box_gap`
from `gap`: two boxes that miss are two solids that miss, so a caller may skip that pair; two
boxes that overlap say nothing at all, and the exact query is the only answer. `cast` follows
the same rule from the other end — every body it reports is one the exact boolean found the
column inside, and the distance it reports is the shape's own minimum along the axis rather than
a corner of its box.
"""

import math

import cadquery as cq
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

import _boxes
import _overlap

# mm³ of column inside a body before the cast calls it a contact. The same floor `_overlap`'s
# readers use: under it the pair is a graze on a tangent surface, not something in the way.
HIT_VOL = 1.0


def box_gap(a, b) -> float:
    """The least distance between two axis-aligned boxes, 0 when they overlap — a lower bound on
    the solids' own gap, and sound to prefilter on for exactly that reason."""
    dx = max(0.0, a.xmin - b.xmax, b.xmin - a.xmax)
    dy = max(0.0, a.ymin - b.ymax, b.ymin - a.ymax)
    dz = max(0.0, a.zmin - b.zmax, b.zmin - a.zmax)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def gap(a, b) -> float:
    """The exact least distance between two solids, 0 when they touch or overlap.

    Raises rather than falling back to a box: a gap that cannot be taken is unknown, not large,
    and a card printing this as a measurement may not print a guess."""
    dss = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    if not dss.IsDone():
        raise RuntimeError(
            "exact distance did not resolve between two solids — the gap is unknown, not large")
    return dss.Value()


def cast(pos, axis, dia: float, reach: float, solids: dict, skip=()) -> tuple:
    """What a line of `dia` leaving `pos` along `axis` runs into, as `(name, how far it got)`.

    `(None, reach)` is the column reaching its full length untouched — the probe's own length,
    and not a clearance beyond it.

    A boolean that will not resolve raises: an unmeasured body is not an absent one, and the
    difference decides whether a fitting can be plugged in."""
    col = cq.Solid.makeCylinder(dia / 2.0, reach, cq.Vector(*pos), cq.Vector(*axis))
    cb = _boxes.boxed(col)
    best, who = reach, None
    for name, solid in solids.items():
        if name in skip:
            continue
        if box_gap(cb, _boxes.boxed(solid)) > 0:
            continue
        try:
            inter, vol = _overlap.common(col, solid)
        except Exception as exc:
            raise RuntimeError(
                f"the lead out of {tuple(round(c, 2) for c in pos)} against {name} could not be "
                f"taken ({exc}) — whether the port can be used is unknown, not clear") from exc
        if vol <= HIT_VOL:
            continue
        got = axis_min(inter, pos, axis)
        if got < best:
            best, who = max(0.0, got), name
    return who, best


def axis_min(shape, origin, axis) -> float:
    """How far along `axis` from `origin` the nearest point of `shape` lies.

    The shape is moved to the origin and turned until the axis lies on +Z, where its box's `zmin`
    IS that distance. Taken this way rather than off the corners of an axis-aligned box, which
    for a column running diagonally reads short and would invent an obstruction nearer than the
    one that is there."""
    d = _unit(axis)
    loc = shape.translate((-origin[0], -origin[1], -origin[2]))
    dot = d[2]
    if dot < 1.0 - 1e-12:
        if dot <= -1.0 + 1e-12:
            loc = loc.rotate((0, 0, 0), (1, 0, 0), 180.0)
        else:
            loc = loc.rotate((0, 0, 0), (d[1], -d[0], 0.0),           # d × ẑ
                             math.degrees(math.acos(max(-1.0, min(1.0, dot)))))
    return loc.BoundingBox().zmin


def _unit(v) -> tuple:
    n = math.sqrt(sum(float(c) * float(c) for c in v))
    if n < 1e-12:
        raise ValueError(f"direction {tuple(v)} has no length")
    return tuple(float(c) / n for c in v)
