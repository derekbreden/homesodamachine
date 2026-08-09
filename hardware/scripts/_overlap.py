"""The solid two bodies share, measured exactly.

`intersect` is one ask, and one ask is not a measurement — the case it is quiet on is the
case a pack is most likely to have built on purpose. `common(a, b)` asks twice and hands
back `(shape, mm³)`; a boolean that does not resolve raises rather than reporting zero.

    import _overlap
    shape, vol = _overlap.common(a, b)
    vol = _overlap.volume(a, b)
"""

try:
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
    from OCP.TopTools import TopTools_ListOfShape
    from OCP.GProp import GProp_GProps
    from OCP.BRepGProp import BRepGProp
    _HAVE_EXACT = True
except ImportError:                                  # pragma: no cover — OCP is the CAD kernel
    _HAVE_EXACT = False


# An exact Common hands back an EMPTY result — IsDone, no error, no solid — for two bodies
# whose surfaces are exactly TANGENT along the crossing. Two tubes of one Ø meeting on one
# stratum are that case, and a pack builds it deliberately: a port row fixes both runs to a
# single z, so their axes meet inside a plane, the two surfaces touch at the poles of the
# crossing and the section curve is singular at those two points. On sweeps this long, this
# far from the origin, the section step cannot resolve that node inside Precision::Confusion
# and returns nothing at all — a whole Steinmetz solid of interpenetration reported as zero,
# so the one arrangement most likely to be wrong is the one a single ask cannot see.
#
# So an empty exact result is asked again with a fuzz, and only then. The retry is bounded on
# both sides. Under 1e-5 the tangency is still unresolved (1e-6 returns the same nothing); far
# over it a fuzz SWALLOWS a real overlap shallower than itself, and a 1 mm³ floor is reached by
# a thin wide overlap (1e-5 mm over 100,000 mm²) as readily as by a deep narrow one. What it
# cannot do is invent an overlap: a fuzz raises the tolerance for merging coincident geometry,
# it does not grow the solids, so two bodies that merely touch — a tray on its lid, a foot on
# the floor slab — still measure zero however large it is.
FUZZ = 1e-5


def common(a, b) -> tuple:
    """The solid two bodies share and its volume, as `(shape, mm³)`. Empty is `(shape, 0.0)`."""
    if not _HAVE_EXACT:
        raise RuntimeError(
            "the exact boolean is unavailable — OCP.BRepAlgoAPI did not import, so no overlap "
            "here is a measurement")
    shape, vol = _at(a, b, 0.0)
    return (shape, vol) if vol > 0.0 else _at(a, b, FUZZ)


def _at(a, b, fuzz: float) -> tuple:
    """One Common at one fuzz, as `(cq shape, volume)`. Raises rather than reporting an
    unresolved boolean as a clean pair."""
    import cadquery as cq

    args, tools = TopTools_ListOfShape(), TopTools_ListOfShape()
    args.Append(a.wrapped)
    tools.Append(b.wrapped)
    op = BRepAlgoAPI_Common()
    op.SetArguments(args)
    op.SetTools(tools)
    if fuzz:
        op.SetFuzzyValue(fuzz)
    op.Build()
    if not op.IsDone():
        raise RuntimeError(
            f"an intersection did not resolve between two solids (fuzz {fuzz:g}) — the overlap "
            f"is unknown, not absent")
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(op.Shape(), props)
    return cq.Shape.cast(op.Shape()), props.Mass()


def volume(a, b) -> float:
    """Just the mm³ of `common`, for the checks that only threshold on it."""
    return common(a, b)[1]


# --- the guard ---------------------------------------------------------------
#
# WHAT COMES BACK IS NOT THE POINT — the point is that every gate ASKS HERE. The tangency
# above cannot be reproduced from primitives: two perpendicular cylinders of one Ø answer
# correctly to a bare `intersect`, and it takes a long sweep far from the origin to put the
# section step past what `Precision::Confusion` can resolve. So there is no small numeric
# test to leave behind, and the regression to guard is the one that actually happens — a
# gate written with the bare pattern, which reads as a measurement and is an ask.
GATED = (
    "cold-core-layout/cold_core_assembly.py",
    "printed-parts/cold-core/_internal_routes.py",
    "manifold-layout/manifold_layout.py",
    "manifold-layout/_scorecard.py",
)


def selftest():
    """Every module that grades an overlap measures it through here."""
    import pathlib
    hw = pathlib.Path(__file__).resolve().parents[1]
    for rel in GATED:
        path = hw / rel
        if not path.is_file():
            raise AssertionError(f"{rel} is gone — this list names the modules that grade "
                                 f"overlaps, so a rename has to come through here too")
        # ANY `.intersect(` at all, not the one-line `.intersect(...).Volume()` shape. The
        # pattern this replaced was written over two lines — `inter = si.intersect(sj)` and
        # `v = inter.Volume()` — so a shape-matching rule read it as clean. None of these
        # modules has a use for the bare call, so the flat rule is the honest one.
        hits = [f"{rel}:{n}" for n, line in enumerate(path.read_text().splitlines(), 1)
                if ".intersect(" in line]
        if hits:
            raise AssertionError(
                "a clash gate measures an overlap with a bare `.intersect(...).Volume()`, "
                "which reports 0.00 on two swept tubes whose axes cross — the case a pack is "
                "most likely to have built on purpose. Ask `_overlap.volume` instead: "
                + ", ".join(hits))
        yield f"{rel}: no bare intersect"


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(" ", line)
        print("_overlap selftest OK")
