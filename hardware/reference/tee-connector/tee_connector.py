"""Tee connector — the three-port union the manifold's junctions are built from.

`tee-connector.step` is a harvested solid standing in for the John Guest PP0208E
(`README.md`): there is no builder here, and every number below was measured off that file.
`stations_hold` reads them back off it at import of the pack that places it, so a measurement
and the metal it was taken from cannot part.

Coordinate frame
----------------
- The RUN on Z, its two collet faces at ±`RUN_HALF`. The BRANCH on +Y, its face at
  `BRANCH_REACH`. All three ports are coaxial with the body centre and take 1/4" OD tube.
- Origin at the body centre, so `HALF_W` is the body's own radius about the run.

The topology names the three legs of each junction (`../../topology/fluid-topology.md`); which
name lands on the branch is the numbering's business, and the enclosure's.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _measuring import collet_offsets

STEP = _here.parent / "tee-connector.step"

# --- Measured off the STEP ------------------------------------------------
RUN_HALF = 20.07          # run collet face from the body centre
BRANCH_REACH = 20.07      # branch collet face from the same centre
HALF_W = 6.86             # the body's own radius about the run axis
TUBE_D = 6.35             # the 1/4" OD LLDPE all three ports accept
MEASURE_TOL = 0.01        # what the figures above are rounded to


def run(sign):
    """One of the run's two collinear ports, `sign` picking the +Z or −Z end."""
    return ((0.0, 0.0, sign * RUN_HALF), (0.0, 0.0, sign))


def branch():
    """The third port, perpendicular to the run, out +Y."""
    return ((0.0, +BRANCH_REACH, 0.0), (0.0, 1.0, 0.0))


def stations() -> dict:
    """All three, under the ends they stand on."""
    return {"+z": run(+1.0), "-z": run(-1.0), "branch": branch()}


def stations_hold():
    """Hold the figures above to `tee-connector.step`.

    All three are extents of the solid's own box, and the run and the branch are each also a
    1/4" bore standing on the body's own centreline."""
    solid = cq.importers.importStep(str(STEP)).val()
    bb = solid.BoundingBox()
    for name, claimed, actual in (("RUN_HALF", RUN_HALF, bb.zmax),
                                  ("BRANCH_REACH", BRANCH_REACH, bb.ymax),
                                  ("HALF_W", HALF_W, bb.xmax)):
        if abs(actual - claimed) > MEASURE_TOL:
            raise ValueError(
                f"tee-connector {name} is {claimed:g} and the STEP's own is {actual:.4f} — "
                f"{abs(actual - claimed):.4f} mm apart, over the {MEASURE_TOL:g} mm this file "
                f"rounds to. Every leg placed off {name} closes on tube that is not there.")
    for axis, what in (("z", "run"), ("y", "branch")):
        seen = collet_offsets(solid, axis, TUBE_D / 2.0)
        if seen != [(0.0, 0.0)]:
            raise ValueError(
                f"the tee's {what} bore runs at {seen} and not on the body's own centreline — "
                f"the stations here all stand at the centre, so a port is off its own axis.")


# --- controls -------------------------------------------------------------

def selftest():
    stations_hold()
    return ["  the three declared stations stand on the solid they were measured off"]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(line)
        print("tee_connector selftest OK")
    else:
        print(__doc__)
