"""Elbow connector — the two-port union that turns a 1/4" line through a right angle.

`elbow-connector.step` is a harvested solid standing in for the John Guest PP0308E
(`README.md`): there is no builder here, and every number below was measured off that file.
`native-measurements.json` binds the native readings to that STEP by SHA-256.
`stations_hold` compares the interface figures with those recorded readings. The machine
places the scanned PP0308E (`reference/jg-pp0308e-elbow`), not this stand-in.

Coordinate frame
----------------
- The two leg AXES meet at the origin — the bend corner — and the body has no other datum:
  one leg runs out along +Y, the other along +Z, each to a collet face `LEG` from that corner.
- `HALF_W` is the body's own radius about either axis, and `BACK` how far the outer corner
  stands behind the pair of them. So the fitting's whole envelope is `2·HALF_W` across the
  free axis by `BACK + LEG` on each of the two the legs lie on.

WHAT AN ELBOW BUYS OVER A UNION IS THE CORNER. A straight union hands the line back on its own
axis and the run turns after it, in the room past the fitting; this turns inside its own
envelope, so the line leaves on an axis the run never had to spend a bend radius reaching. The
funnel's drain turns this way: its PP0308E stands in a cradle under the funnel frame, the drain
stub in its +Z collet and `fluid-4` leaving aft off its +Y one.
"""

import json
import sys
from pathlib import Path

_here = Path(__file__).resolve()

STEP = _here.parent / "elbow-connector.step"
MEASUREMENTS = _here.parent / "native-measurements.json"

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


def _collet_offsets(readings, axis, bore_r, tol=1e-4):
    for bore in readings["bores"]:
        if bore["axis"] == axis and abs(bore["radius_mm"] - bore_r) <= tol:
            return sorted(tuple(centre) for centre in bore["centres_mm"])
    raise ValueError(
        f"no bore of r={bore_r:g} running along {axis} — the solid carries "
        f"{sorted({(b['axis'], b['radius_mm']) for b in readings['bores']})}")


def stations_hold():
    """Compare the interface figures with the recorded native STEP readings.

    Four of them are extents of the solid's own box, and each leg is also a 1/4" bore standing
    on the body's own centreline — which is what says the two axes cross at this origin and not
    merely near it. `INSERTION` is the fifth and is not an extent at all: it is where a tube
    pushed into a leg meets the stop, bisected off the metal. The funnel's drain stub is cut to
    John Guest's data-sheet stop instead (`reference/funnel-drain-stub`)."""
    readings = json.loads(MEASUREMENTS.read_text())
    bounds = readings["bounds_mm"]
    for leg in LEGS:
        got = readings["socket_depths_mm"][leg]
        if abs(got - INSERTION) > MEASURE_TOL:
            raise ValueError(
                f"elbow-connector INSERTION is {INSERTION:g} and the +{leg.upper()} leg's socket "
                f"bottoms a 1/4\" tube at {got:.4f} — {abs(got - INSERTION):.4f} mm apart, over "
                f"the {MEASURE_TOL:g} mm this file rounds to. Every stub cut to this figure is "
                f"cut to a socket that is not there.")
    for name, claimed, actual in (
            ("LEG on +Y", LEG, bounds["ymax"]), ("LEG on +Z", LEG, bounds["zmax"]),
            ("HALF_W", HALF_W, bounds["xmax"]), ("BACK off +Y", -BACK, bounds["ymin"]),
            ("BACK off +Z", -BACK, bounds["zmin"])):
        if abs(actual - claimed) > MEASURE_TOL:
            raise ValueError(
                f"elbow-connector {name} is {claimed:g} and the STEP's own is {actual:.4f} — "
                f"{abs(actual - claimed):.4f} mm apart, over the {MEASURE_TOL:g} mm this file "
                f"rounds to. Every leg placed off {name} closes on tube that is not there.")
    for axis, what in (("y", "+Y leg"), ("z", "+Z leg")):
        seen = _collet_offsets(readings, axis, TUBE_D / 2.0)
        if seen != [(0.0, 0.0)]:
            raise ValueError(
                f"the elbow's {what} bore runs at {seen} and not on the body's own centreline — "
                f"the stations here both stand on the corner, so a port is off its own axis.")


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
