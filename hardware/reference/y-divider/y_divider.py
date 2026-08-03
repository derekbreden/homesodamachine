"""Y-divider — the three-port trident the manifold joins a valve pair with.

`y-divider.step` is a harvested solid: there is no builder here, and every number below was
measured off that file. `stations_hold` reads them back off it at import of the pack that
places it, so a measurement and the metal it was taken from cannot part.

Coordinate frame
----------------
- The long axis on Z. The STEM is the single port at +Z; the two OUTLETS are at −Z, offset
  ±`OUTLET_Y` either side of the axis. All three take 1/4" OD tube.
- Origin at the body centre, so the stem and the outlet faces are ±`HALF`.

The topology names its three legs (`../../topology/fluid-topology.md`); which outlet reaches
which valve is the seating's business, and the enclosure's.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _measuring import collet_offsets

STEP = _here.parent / "y-divider.step"

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


def stations_hold():
    """Hold the figures above to `y-divider.step`.

    The reaches and the radius are extents of the solid's own box. The outlet offset is not —
    it is a bore centre inside the envelope, and it is read off the tube bores themselves."""
    solid = cq.importers.importStep(str(STEP)).val()
    bb = solid.BoundingBox()
    for name, claimed, actual in (("HALF", HALF, bb.zmax), ("HALF_W", HALF_W, bb.xmax)):
        if abs(actual - claimed) > MEASURE_TOL:
            raise ValueError(
                f"y-divider {name} is {claimed:g} and the STEP's own is {actual:.4f} — "
                f"{abs(actual - claimed):.4f} mm apart, over the {MEASURE_TOL:g} mm this file "
                f"rounds to. Every leg placed off {name} closes on tube that is not there.")
    ys = [y for _x, y in collet_offsets(solid, "z", TUBE_D / 2.0)]
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
