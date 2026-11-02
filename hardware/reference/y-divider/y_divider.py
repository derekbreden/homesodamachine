"""Y-divider — the three-port trident the manifold joins a valve pair with.

`y-divider.step` is a harvested solid: there is no builder here, and every number below was
measured off that file. `native-measurements.json` binds the native readings to that STEP by
SHA-256.
`stations_hold` compares the interface figures with those recorded readings.

Coordinate frame
----------------
- The long axis on Z. The STEM is the single port at +Z; the two OUTLETS are at −Z, offset
  ±`OUTLET_Y` either side of the axis. All three take 1/4" OD tube.
- Origin at the body centre, so the stem and the outlet faces are ±`HALF`.

The topology names its three legs (`../../topology/fluid-topology.md`); which outlet reaches
which valve is the seating's business, and the enclosure's.
"""

import json
import sys
from pathlib import Path

_here = Path(__file__).resolve()

STEP = _here.parent / "y-divider.step"
MEASUREMENTS = _here.parent / "native-measurements.json"

# --- Measured off the STEP ------------------------------------------------
HALF = 19.25          # stem and outlet collet faces from the body centre
OUTLET_Y = 7.35       # each outlet's offset from the divider axis
HALF_W = 8.1          # the body's own radius about the stem axis
TUBE_D = 6.35         # the 1/4" OD LLDPE all three ports accept
MEASURE_TOL = 0.01    # what the figures above are rounded to


def stem():
    """The single port at +Z: `(position, outward axis)`."""
    return ((0.0, 0.0, +HALF), (0.0, 0.0, 1.0))


def outlet(sign):
    """One of the two ports at −Z, `sign` picking the +Y or −Y side."""
    return ((0.0, sign * OUTLET_Y, -HALF), (0.0, 0.0, -1.0))


def stations() -> dict:
    """All three, under the sides they stand on."""
    return {"stem": stem(), "-y": outlet(-1.0), "+y": outlet(+1.0)}


def _collet_offsets(readings, axis, bore_r, tol=1e-4):
    for bore in readings["bores"]:
        if bore["axis"] == axis and abs(bore["radius_mm"] - bore_r) <= tol:
            return sorted(tuple(centre) for centre in bore["centres_mm"])
    raise ValueError(
        f"no bore of r={bore_r:g} running along {axis} — the solid carries "
        f"{sorted({(b['axis'], b['radius_mm']) for b in readings['bores']})}")


def stations_hold():
    """Compare the interface figures with the recorded native STEP readings.

    The reaches and the radius are extents of the solid's own box. The outlet offset is not —
    it is a bore centre inside the envelope, and it is read off the tube bores themselves."""
    readings = json.loads(MEASUREMENTS.read_text())
    bounds = readings["bounds_mm"]
    for name, claimed, actual in (
            ("HALF", HALF, bounds["zmax"]), ("HALF_W", HALF_W, bounds["xmax"])):
        if abs(actual - claimed) > MEASURE_TOL:
            raise ValueError(
                f"y-divider {name} is {claimed:g} and the STEP's own is {actual:.4f} — "
                f"{abs(actual - claimed):.4f} mm apart, over the {MEASURE_TOL:g} mm this file "
                f"rounds to. Every leg placed off {name} closes on tube that is not there.")
    ys = [y for _x, y in _collet_offsets(readings, "z", TUBE_D / 2.0)]
    want = sorted({-OUTLET_Y, 0.0, +OUTLET_Y})
    if len(ys) != 3 or max(abs(a - b) for a, b in zip(ys, want)) > MEASURE_TOL:
        raise ValueError(
            f"y-divider OUTLET_Y is {OUTLET_Y:g}, so its three 1/4\" bores should run at "
            f"y = {want}; the STEP's run at {ys}. The outlets are not where the legs are "
            f"aimed.")


# --- controls -------------------------------------------------------------

def selftest():
    stations_hold()
    return ["  the three declared stations stand on the solid they were measured off"]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(line)
        print("y_divider selftest OK")
    else:
        print(__doc__)
