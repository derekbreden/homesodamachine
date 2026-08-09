"""A solid drawn once and kept, keyed on everything that decides its shape.

    import _realized
    shape = _realized.realized(_realized.key(__file__, description), lambda: draw(description))

A part is redrawn on every build, and most builds change nothing about it — an agent moving one
body rebuilds the four printed pieces, whose shape is decided by the box description and the
code that cuts it, neither of which moved. `realized` reads such a part back off disk instead.

WHAT THE KEY MUST COVER IS EVERYTHING THAT DECIDES THE SHAPE, and a key that misses one is a
build that ships last run's geometry. So it takes the SOURCE of the module that draws the part
— the whole file, so an edit anywhere in it misses — beside a repr of the description handed
in. A description that is not fully repr'd is a key that cannot see part of its own input:
`enclosure.Box` is a namedtuple of numbers and station tuples and repr's completely, which is
what makes it usable here.

The entries are not committed and carry no meaning between machines: `.gitignore` holds
`.cache/`, a miss costs exactly what the build always cost, and deleting the directory is
always safe.
"""

import hashlib
import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_DIR = _ROOT / ".cache" / "realized"

# A build that must not read a kept solid — the one that proves the cache is honest — sets this.
DISABLED = bool(os.environ.get("HSM_NO_REALIZED_CACHE"))


def key(source_file, *inputs) -> str:
    """A name for the shape `source_file` draws from `inputs`."""
    h = hashlib.blake2b(digest_size=16)
    h.update(Path(source_file).resolve().read_bytes())
    for i in inputs:
        h.update(repr(i).encode())
    return h.hexdigest()


def realized(name: str, build):
    """The shape `build()` draws, read back from disk when `name` already stands for one."""
    from OCP.BRep import BRep_Builder
    from OCP.BRepTools import BRepTools
    from OCP.TopoDS import TopoDS_Shape
    import cadquery as cq

    if DISABLED:
        return build()
    path = _DIR / f"{name}.brep"
    if path.is_file():
        shape, builder = TopoDS_Shape(), BRep_Builder()
        if BRepTools.Read_s(shape, str(path), builder) and not shape.IsNull():
            return cq.Workplane(obj=cq.Shape.cast(shape))
    made = build()
    solid = made.val() if hasattr(made, "val") else made
    try:
        _DIR.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(f".{os.getpid()}.tmp")
        BRepTools.Write_s(solid.wrapped, str(tmp))
        os.replace(tmp, path)                    # a reader never sees a half-written entry
    except Exception:
        pass                                     # a cache that cannot be written is not an error
    return made


def selftest():
    """A kept solid is the drawn one, and a key that cannot see its input is caught."""
    import cadquery as cq

    drawn = [0]

    def draw(r):
        drawn[0] += 1
        return cq.Workplane(obj=cq.Solid.makeCylinder(r, 10.0))

    import tempfile
    global _DIR
    held, _DIR = _DIR, Path(tempfile.mkdtemp(prefix="hsm-realized-"))
    try:
        k = key(__file__, ("selftest", 3.0))
        first = realized(k, lambda: draw(3.0))
        second = realized(k, lambda: draw(3.0))
        if drawn[0] != 1:
            raise AssertionError(f"one shape was drawn {drawn[0]} times — the key does not stand "
                                 f"for it, so nothing is ever read back")
        a, b = first.val().Volume(), second.val().Volume()
        if abs(a - b) > 1e-9:
            raise AssertionError(f"a kept solid measures {b:.6f} where the drawn one measures "
                                 f"{a:.6f} — the round trip is not the shape")
        yield f"a kept solid is the drawn one, to {abs(a-b):.1e} mm³"

        if key(__file__, ("selftest", 3.0)) == key(__file__, ("selftest", 4.0)):
            raise AssertionError("two descriptions share a key — a change to one would be "
                                 "served the other's geometry")
        yield "two descriptions do not share a key"
    finally:
        _DIR = held


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(" ", line)
        print("_realized selftest OK")
