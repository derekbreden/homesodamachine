"""How far apart two bodies stand.

`_overlap` measures the solid two bodies SHARE. This is the question on the other side of zero —
the gap between bodies that do not share anything.

    import _clearing
    _clearing.box_gap(bb_a, bb_b)                 # a lower bound, for prefiltering
    _clearing.shadows(a, b)                       # whether a fall can reach it at all
    _clearing.gap(a, b, within)                   # the distance up to `within`, 0 when touching

A BOUNDING BOX PROVES CLEARANCE AND NEVER PROVES OBSTRUCTION, which is what splits `box_gap`
from `gap`: two boxes that miss are two solids that miss, so a caller may skip that pair; two
boxes that overlap say nothing at all, and the mesh query is the only answer.

`within` IS A HORIZON AND EVERY CALLER STATES ITS OWN. Under it, what comes back is the
distance. At it, what comes back is a floor: the bodies are at least that far apart, and how
much further was not asked. The horizon is also what the reading costs — a query told to look
past the bodies sweeps the volume between them, and one told to stop returns at the bound. A
caller that prints a gap as a measurement passes a horizon it expects to stay under.
"""

import math

import numpy as np

import _meshes

# mm³ two solids share before the pair counts as a contact. The same floor `_overlap`'s readers
# use: under it the pair is a graze on a tangent surface, not something in the way.
HIT_VOL = 1.0


def box_gap(a, b) -> float:
    """The least distance between two axis-aligned boxes, 0 when they overlap — a lower bound on
    the solids' own gap, and sound to prefilter on for exactly that reason."""
    dx = max(0.0, a.xmin - b.xmax, b.xmin - a.xmax)
    dy = max(0.0, a.ymin - b.ymax, b.ymin - a.ymax)
    dz = max(0.0, a.zmin - b.zmax, b.zmin - a.zmax)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def shadows(a, b) -> bool:
    """Whether `a` coming straight down can ever reach `b` — do their plan outlines overlap.

    EXACT FOR A FALL, where the other two readings are bounds. A body carried along -Z keeps
    its outline at every station, so outlines that miss are bodies that miss at every height —
    a hundredth of a millimetre apart in plan is as far apart as a metre."""
    return not (_meshes.meshed(a).project() ^ _meshes.meshed(b).project()).is_empty()


def gap(a, b, within: float, offset=(0.0, 0.0, 0.0)) -> float:
    """The least distance between two solids, measured as far as `within`. 0 when they touch.

    `offset` moves `a` before the reading is taken. A body walked along an axis is the same body
    at every station, so the mesh is taken once off the unmoved solid and carried — re-asking
    `_meshes` for each step would tessellate the same shape over and over."""
    ma = _meshes.meshed(a)
    if any(offset):
        ma = ma.translate(tuple(float(c) for c in offset))
    return ma.min_gap(_meshes.meshed(b), within)


def axis_min(shape, origin, axis) -> float:
    """How far along `axis` from `origin` the nearest point of `shape` lies.

    The shape is carried to the origin and turned until the axis lies on +Z, where its box's
    `zmin` IS that distance. Taken this way rather than off the corners of an axis-aligned box,
    which for a column running diagonally reads short and would invent an obstruction nearer
    than the one that is there."""
    d = np.array(_unit(axis))
    # An orthonormal frame with the axis as its third row sends the axis to +Z: R·d = (0, 0, 1).
    other = np.array((1.0, 0.0, 0.0)) if abs(d[0]) < 0.9 else np.array((0.0, 1.0, 0.0))
    u = np.cross(other, d)
    u /= np.linalg.norm(u)
    rot = np.array([u, np.cross(d, u), d])
    o = np.array([float(c) for c in origin])
    return shape.transform(np.hstack([rot, (-rot @ o).reshape(3, 1)])).bounding_box()[2]


def _unit(v) -> tuple:
    n = math.sqrt(sum(float(c) * float(c) for c in v))
    if n < 1e-12:
        raise ValueError(f"direction {tuple(v)} has no length")
    return tuple(float(c) / n for c in v)


def selftest():
    """The horizon, the offset, and the turn `axis_min` takes — each against arithmetic."""
    import cadquery as cq

    r, d = 3.175, 12.0
    a = cq.Solid.makeCylinder(r, 60.0, cq.Vector(0, 0, 0), cq.Vector(0, 0, 1))
    b = cq.Solid.makeCylinder(r, 60.0, cq.Vector(d, 0, 0), cq.Vector(0, 0, 1))
    true = d - 2 * r

    floored = gap(a, b, true / 2.0)
    if floored != true / 2.0:
        raise AssertionError(f"a gap past its horizon read {floored:.4f} rather than the "
                             f"{true/2.0:.4f} floor — the bound is being reported as a distance")
    yield f"a gap past its horizon reads its own {true/2.0:.4f} floor"

    # Carrying `a` the whole way onto `b` closes the gap; the same solid is meshed once.
    if gap(a, b, 3.0 * true, offset=(d, 0.0, 0.0)) > 1e-9:
        raise AssertionError("a body carried onto another still reads a gap — `offset` is not "
                             "reaching the mesh")
    yield "a body carried onto another reads 0"

    # A column running diagonally: the nearest point of a body sitting `s` along the axis is at
    # `s`, and an axis-aligned box would read the corner instead.
    s = 20.0
    ax = _unit((1.0, 1.0, 1.0))
    ball = cq.Solid.makeSphere(2.0, cq.Vector(*[s * c for c in ax]), angleDegrees1=-90)
    got = axis_min(_meshes.meshed(ball), (0.0, 0.0, 0.0), ax)
    if abs(got - (s - 2.0)) > 0.1:
        raise AssertionError(f"a ball {s:g} along a diagonal reads {got:.3f} rather than "
                             f"{s-2.0:.3f} — the turn onto +Z is wrong")
    yield f"a ball {s:g} along a diagonal reads {got:.3f}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(" ", line)
        print("_clearing selftest OK")
