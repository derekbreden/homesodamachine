"""Elbow connector — the two-port union that turns a 1/4" line through a right angle.

`elbow-connector.step` is a harvested solid standing in for the John Guest PP0308E
(`README.md`): there is no builder here, and every number below was measured off that file.
`stations_hold` reads them back off it at import of the machine that places it, so a
measurement and the metal it was taken from cannot part.

Coordinate frame
----------------
- The two leg AXES meet at the origin — the bend corner — and the body has no other datum:
  one leg runs out along +Y, the other along +Z, each to a collet face `LEG` from that corner.
- `HALF_W` is the body's own radius about either axis, and `BACK` how far the outer corner
  stands behind the pair of them. So the fitting's whole envelope is `2·HALF_W` across the
  free axis by `BACK + LEG` on each of the two the legs lie on.

WHAT AN ELBOW BUYS OVER A UNION IS THE CORNER. A straight union hands the line back on its own
axis and the run turns after it, in the room past the fitting; this turns inside its own
envelope, so the line leaves on an axis the run never had to spend a bend radius reaching. One
hangs under the hopper basin's spout, taking the fall out of `hopper_funnel`'s drain on its +Z
leg and handing `fluid-4` aft off its +Y one.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _measuring import collet_offsets
from _cadq_export import import_step

STEP = _here.parent / "elbow-connector.step"

# --- Measured off the STEP ------------------------------------------------
LEG = 19.558           # bend corner to a collet face, the same on both legs
HALF_W = 7.366         # the body's own radius about either leg's axis
BACK = 7.366           # the outer corner, behind both legs' axes
TUBE_D = 6.35          # the 1/4" OD LLDPE both ports accept
INSERTION = 15.75      # how far a tube runs into either leg before it bottoms on the stop
MEASURE_TOL = 0.01     # what the figures above are rounded to

#: The two legs, named by the axis each runs out along in this frame.
LEGS = {"y": (0.0, 1.0, 0.0), "z": (0.0, 0.0, 1.0)}


def port(leg: str) -> tuple:
    """One of the two 1/4" tube ports: `(position, outward axis)`, `leg` naming the axis it
    opens along. The station is the collet face — the plane a tube crosses to enter."""
    axis = LEGS[leg]
    return (tuple(a * LEG for a in axis), axis)


def stations() -> dict:
    """Both, under the legs they stand on."""
    return {k: port(k) for k in LEGS}


def envelope() -> tuple:
    """`(dx, dy, dz)` the fitting takes in its own frame — what crowds a neighbour. The two
    legs' axes are on Y and Z, so those two spans each carry `BACK` behind the corner as well
    as the leg in front of it, and X is the body alone."""
    return (2.0 * HALF_W, BACK + LEG, BACK + LEG)


def reach() -> float:
    """Corner to collet face — how far the fitting hangs past a body seated on one of its
    ports, measured along the other leg's axis."""
    return LEG


def _bottoms_at(solid, leg: str) -> float:
    """How far a 1/4" tube runs into one leg before it meets metal — the socket's own depth,
    bisected off the solid rather than stated twice."""
    axis = LEGS[leg]
    lo, hi = 0.0, LEG
    for _ in range(48):
        mid = (lo + hi) / 2.0
        base = tuple(a * (LEG - mid) for a in axis)
        rod = cq.Solid.makeCylinder(TUBE_D / 2.0, mid + 1.0, cq.Vector(*base),
                                    cq.Vector(*axis))
        if rod.intersect(solid).Volume() > 1e-9:
            hi = mid
        else:
            lo = mid
    return lo


def stations_hold():
    """Hold the figures above to `elbow-connector.step`.

    Four of them are extents of the solid's own box, and each leg is also a 1/4" bore standing
    on the body's own centreline — which is what says the two axes cross at this origin and not
    merely near it. `INSERTION` is the fifth and is not an extent at all: it is where a tube
    pushed into a leg meets the stop, bisected off the metal, and it is what the basin's drain
    stub is cut to (`reference/hopper-drain-stub`). A stub cut to a deeper socket than the
    fitting has is a stub the collet never closes on."""
    solid = import_step(str(STEP)).val()
    bb = solid.BoundingBox()
    for leg in LEGS:
        got = _bottoms_at(solid, leg)
        if abs(got - INSERTION) > MEASURE_TOL:
            raise ValueError(
                f"elbow-connector INSERTION is {INSERTION:g} and the +{leg.upper()} leg's socket "
                f"bottoms a 1/4\" tube at {got:.4f} — {abs(got - INSERTION):.4f} mm apart, over "
                f"the {MEASURE_TOL:g} mm this file rounds to. Every stub cut to this figure is "
                f"cut to a socket that is not there.")
    for name, claimed, actual in (("LEG on +Y", LEG, bb.ymax), ("LEG on +Z", LEG, bb.zmax),
                                  ("HALF_W", HALF_W, bb.xmax), ("BACK off +Y", -BACK, bb.ymin),
                                  ("BACK off +Z", -BACK, bb.zmin)):
        if abs(actual - claimed) > MEASURE_TOL:
            raise ValueError(
                f"elbow-connector {name} is {claimed:g} and the STEP's own is {actual:.4f} — "
                f"{abs(actual - claimed):.4f} mm apart, over the {MEASURE_TOL:g} mm this file "
                f"rounds to. Every leg placed off {name} closes on tube that is not there.")
    for axis, what in (("y", "+Y leg"), ("z", "+Z leg")):
        seen = collet_offsets(solid, axis, TUBE_D / 2.0)
        if seen != [(0.0, 0.0)]:
            raise ValueError(
                f"the elbow's {what} bore runs at {seen} and not on the body's own centreline — "
                f"the stations here both stand on the corner, so a port is off its own axis.")


def build_elbow_connector():
    """The harvested solid, wrapped in a `cq.Workplane` the way every builder here hands one
    back. Nothing is drawn: the file IS the part, and `stations_hold` is what says the figures
    above describe it."""
    return cq.Workplane(obj=import_step(str(STEP)).val())


# --- controls -------------------------------------------------------------

def selftest():
    stations_hold()
    return ["  both declared stations stand on the solid they were measured off"]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(line)
        print("elbow_connector selftest OK")
    else:
        print(__doc__)
