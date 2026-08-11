"""The solid two bodies share.

`common(a, b)` hands back `(shape, mm³)`, where the shape is a `manifold3d.Manifold` and the
volume is what the two enclose between them. A body whose mesh does not close raises out of
`_meshes` rather than arriving here to be measured as a clean pair.

    import _overlap
    shape, vol = _overlap.common(a, b)
    vol = _overlap.volume(a, b)

The reading stands within the bound `_meshes` states. Two tubes of one Ø crossing axis-on-axis
share a Steinmetz solid of 16r³/3, and `_meshes.selftest` holds that crossing — a port row fixes
both runs to one z, so it is an arrangement the pack builds.
"""

import _meshes


def common(a, b) -> tuple:
    """The solid two bodies share and its volume, as `(shape, mm³)`. Empty is `(shape, 0.0)`."""
    shape = _meshes.meshed(a) ^ _meshes.meshed(b)
    return shape, shape.volume()


def volume(a, b) -> float:
    """Just the mm³ of `common`, for the checks that only threshold on it."""
    return common(a, b)[1]


# --- the guard ---------------------------------------------------------------
#
# WHAT COMES BACK IS NOT THE POINT — the point is that every gate ASKS HERE. `Shape.intersect`
# is the exact boolean, and it answers EMPTY for two bodies whose surfaces are exactly tangent
# along the crossing: two tubes of one Ø meeting on one stratum come back 0.00 mm³ with no error
# raised, which is the arrangement a port row builds on purpose. The regression to guard is a
# gate written with that bare pattern, which reads as a measurement and is an ask.
GATED = (
    "cold-core-layout/cold_core_assembly.py",
    "printed-parts/cold-core/_internal_routes.py",
    "manifold-layout/manifold_layout.py",
    "manifold-layout/_scorecard.py",
)
# `scripts/fit.py` is deliberately not on that list. Every occupancy it GRADES asks here, and
# its one remaining `intersect` clips a body to a scan band — a construction that decides what
# a cell costs and never what a cell answers. The flat rule above is right for a module with no
# use for the bare call, and wrong for one that has.


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
