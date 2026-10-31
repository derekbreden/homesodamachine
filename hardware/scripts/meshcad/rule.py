"""The one triangulation rule, and where each face came from.

EVERY CURVE IN THE TREE IS CUT INTO SEGMENTS BY ONE RULE. A circle of radius r gets
`ring_count(r)` points at fixed angles about its axis, measured from a frame that depends on
the axis and nothing else. A boss and the bore it sits in, a cutter and the wall it trims, two
parts that touch on a cylinder: wherever two surfaces coincide they were cut into the same
points, so a boolean between them leaves no sliver to find later.

The step is print_mesh's: no chord strays more than LINEAR from the true curve and no segment
turns more than ANGULAR. Counts round up to a multiple of 8, so every ring has its points on
the axes of its own frame and its bounding box is exact.

Every vertex the kernel builds lands on one grid, GRID apart (`snap`). Two computations of
one point that differ in their last bits — a fillet2D arc's center an ulp off the plane its
lines lie on — come out as the same point, so faces that coincide in the model coincide
exactly in the mesh and a boolean between them cancels them. The grid sits far under the
1e-7 mm a generator compares coordinates to, so a selector finds a vertex where it was put.

A file gets the solid simplified to TOLERANCE (`write._triangles`). Where three coincident
faces meet, Manifold's symbolic perturbation can leave the surface touching itself across a
sliver a rounding error wide. Manifold keeps the two sides apart; a file's float32 merges them
into one edge that four faces share, and a slicer refuses it. Simplifying collapses the
sliver and leaves every vertex it keeps where the rule put it. The solid itself stays exact,
so the next boolean still meets its faces on the rule's points.

`caller()` names the generator line that asked for a face. Every face the kernel builds keeps
it, with the surface it lies on, so "which cut made this face" is a lookup.
"""

import math
import sys
from pathlib import Path

import numpy as np

LINEAR = 0.005     # mm, the chord's largest distance from the curve
ANGULAR = 0.05     # rad, the largest turn between two segments
GRID = 2.0 ** -30  # mm, about a picometre: the spacing every vertex is snapped to
TOLERANCE = 1e-5   # mm, the shortest edge and thinnest sliver a file's triangles keep

_ROOT = Path(__file__).resolve().parents[3]


def snap(points):
    """`points` on the grid: scaling by a power of two and rounding are exact."""
    return np.round(np.asarray(points, np.float64) / GRID) * GRID


def ring_count(r):
    """Segments in a full circle of radius `r`."""
    if r <= 1e-9:
        return 1
    step = ANGULAR if r <= LINEAR else min(ANGULAR, 2 * math.acos(1 - LINEAR / r))
    return 8 * math.ceil(2 * math.pi / step / 8 - 1e-9)


def canonical_axis(d):
    """`d` or `-d`, whichever points into the positive half: both directions of one axis
    share a frame, so a bore drilled down meets a boss extruded up on the same points."""
    d = np.asarray(d, float)
    d = d / np.linalg.norm(d)
    for c in d:
        if abs(c) > 1e-6:
            return d if c > 0 else -d
    return d


def axis_frame(d):
    """(axis, x, y): the canonical axis of `d` and the frame its rings are measured in."""
    d = canonical_axis(d)
    w = np.array([0.0, 0.0, 1.0]) if abs(d[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    x = w - np.dot(w, d) * d
    x /= np.linalg.norm(x)
    return d, x, np.cross(d, x)


def ring_angles(r, a0=0.0, a1=None):
    """Angles of a ring of radius `r` about its canonical frame: the whole ring when `a1` is
    None, else the ends `a0` < `a1` with the rule's angles strictly between them."""
    n = ring_count(r)
    step = 2 * math.pi / n
    if a1 is None:
        return np.arange(n) * step
    k0 = math.floor(a0 / step) + 1
    k1 = math.ceil(a1 / step) - 1
    inner = [k * step for k in range(k0, k1 + 1)
             if k * step - a0 > 0.25 * step and a1 - k * step > 0.25 * step]
    return np.array([a0, *inner, a1])


def circle_points(center, axis, r, start=None, end=None, ccw_about=None):
    """Points of a circle (or of the arc from `start` to `end`) on the rule's angles.

    `ccw_about` is the direction the arc turns counterclockwise about; the arc's own points
    come back in that order, beginning at `start` and ending at `end` exactly."""
    center = np.asarray(center, float)
    d, x, y = axis_frame(axis)
    if start is None:
        a = ring_angles(r)
        return center + r * (np.cos(a)[:, None] * x + np.sin(a)[:, None] * y)
    start = np.asarray(start, float)
    end = np.asarray(end, float)
    sense = 1.0 if ccw_about is None or np.dot(ccw_about, d) > 0 else -1.0
    v0, v1 = start - center, end - center
    t0 = math.atan2(np.dot(v0, y), np.dot(v0, x))
    t1 = math.atan2(np.dot(v1, y), np.dot(v1, x))
    if sense < 0:
        t0, t1 = t1, t0
    if t1 <= t0 + 1e-12:
        t1 += 2 * math.pi
    a = ring_angles(r, t0, t1)
    pts = center + r * (np.cos(a)[:, None] * x + np.sin(a)[:, None] * y)
    if sense < 0:
        pts = pts[::-1]
    pts[0], pts[-1] = start, end
    return pts


# --- Where a face came from -----------------------------------------------------------

_KERNEL_DIRS = None


def _kernel_dirs():
    global _KERNEL_DIRS
    if _KERNEL_DIRS is None:
        import importlib.util
        spec = importlib.util.find_spec("OCP")
        dirs = [str(Path(__file__).resolve().parent)]
        site = Path(spec.origin).resolve().parent.parent if spec and spec.origin else None
        if site is not None:
            dirs.append(str(site / "cadquery"))
            dirs.append(str(site / "multimethod"))
        dirs.append(str(_ROOT / "hardware/printed-parts/cadlib/world_workplane.py"))
        _KERNEL_DIRS = tuple(dirs)
    return _KERNEL_DIRS


def caller():
    """`path:line` of the first frame outside the kernel and CadQuery: the generator's line
    that asked for this face."""
    skip = _kernel_dirs()
    f = sys._getframe(1)
    while f is not None:
        fn = f.f_code.co_filename
        if not fn.startswith(skip) and not fn.startswith("<"):
            try:
                fn = Path(fn).resolve().relative_to(_ROOT).as_posix()
            except ValueError:
                pass
            return f"{fn}:{f.f_lineno}"
        f = f.f_back
    return None
