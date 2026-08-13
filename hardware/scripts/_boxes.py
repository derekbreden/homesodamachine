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

Under the memo, `_kept` holds the same six numbers on disk against the shape's
own BREP text, so a body already read optimally by any run is not read again.
"""

import hashlib
import io
import json
import os

from OCP.Bnd import Bnd_Box
from OCP.BRepTools import BRepTools
from OCP.TopTools import TopTools_FormatVersion
from cadquery.occ_impl.geom import BoundBox

import _realized

_CACHE: dict = {}
_LOOSE_CACHE: dict = {}
_SOLIDS_CACHE: dict = {}

_DIR = _realized._ROOT / ".cache" / "boxes"

# Six numbers apiece, so what is kept here is the count of distinct placed bodies this tree has
# ever drawn rather than anything that grows with the machine. The least recently read go once
# the pile passes this, as `_meshes` does it.
KEEP_BYTES = 1 << 24
_pruned = False


def _named(shape) -> str:
    """A name for the box `shape` reads. The shape's own BREP text, WHICH CARRIES ITS LOCATION —
    the optimal box of a turned body is not the turned optimal box, so a name that held still
    under a move would hand back the wrong six numbers."""
    stream = io.BytesIO()
    BRepTools.Write_s(shape, stream, False, False,
                      TopTools_FormatVersion.TopTools_FormatVersion_VERSION_1)
    return hashlib.blake2b(stream.getbuffer(), digest_size=16).hexdigest()


def _prune():
    """The pile brought back under `KEEP_BYTES`, least recently read first."""
    global _pruned
    _pruned = True
    entries = []
    for f in _DIR.glob("*.json"):
        try:
            entries.append((f.stat().st_mtime, f.stat().st_size, f))
        except OSError:
            continue
    over = sum(e[1] for e in entries) - KEEP_BYTES
    for _t, size, f in sorted(entries):
        if over <= 0:
            return
        try:
            f.unlink()
            over -= size
        except OSError:
            continue


def _kept(solid):
    """`AddOptimal` for this exact placed shape, drawn once across every process.

    Sibling of [`_meshes`](_meshes.py), which keeps what a shape tessellates to; this keeps the
    six numbers that reading it optimally comes to, and `_realized.DISABLED` defeats both so one
    run can prove the kept work honest."""
    if _realized.DISABLED:
        return solid.BoundingBox()
    path = _DIR / f"{_named(solid.wrapped)}.json"
    if path.is_file():
        try:
            v = json.loads(path.read_text())
        except Exception:
            v = None                             # an entry that cannot be read is a miss
        if v is not None and len(v) == 6:
            try:
                os.utime(path, None)             # a hit is what `_prune` reads as the entry's age
            except OSError:
                pass
            bb = Bnd_Box()
            bb.Update(*v)
            return BoundBox(bb)

    box = solid.BoundingBox()
    try:
        _DIR.mkdir(parents=True, exist_ok=True)
        if not _pruned:
            _prune()
        tmp = path.with_suffix(f".{os.getpid()}.tmp")
        tmp.write_text(json.dumps([box.xmin, box.ymin, box.zmin,
                                   box.xmax, box.ymax, box.zmax]))
        os.replace(tmp, path)                    # a reader never sees a half-written entry
    except Exception:
        pass                                     # a cache that cannot be written is not an error
    return box


def boxed(solid):
    """The solid's optimal bounding box, memoized by identity and kept on disk."""
    key = hash(solid.wrapped)
    hit = _CACHE.get(key)
    if hit is not None and hit[0].wrapped.IsSame(solid.wrapped):
        return hit[1]
    box = _kept(solid)
    _CACHE[key] = (solid, box)          # pin the solid so the entry keeps its shape alive
    return box


def loose(solid):
    """A box that CONTAINS the solid, taken off its control points rather than its surface.

    A Bézier or B-spline lies inside its own control hull, so this box is the optimal one or
    larger, never smaller — and it is taken without meshing, at a small fraction of what
    `boxed` costs.

    LARGE IS THE SAFE DIRECTION FOR A PREFILTER AND THE WRONG ONE FOR A READING. Two boxes that
    miss are two solids that miss whether the boxes are tight or slack, so a caller skipping a
    pair on this is sound; a slack box only lets a pair through to the query that would have
    answered anyway. A caller that reads a FACE off the box — where a body stands, how tall the
    machine is — wants `boxed`, because slack there is a body in the wrong place."""
    key = hash(solid.wrapped)
    hit = _LOOSE_CACHE.get(key)
    if hit is not None and hit[0].wrapped.IsSame(solid.wrapped):
        return hit[1]
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib
    from cadquery.occ_impl.geom import BoundBox
    bb = Bnd_Box()
    BRepBndLib.Add_s(solid.wrapped, bb, True)
    box = BoundBox(bb)
    _LOOSE_CACHE[key] = (solid, box)
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
