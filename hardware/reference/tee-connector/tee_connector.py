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
from _cadq_export import import_step

STEP = _here.parent / "tee-connector.step"

# --- Measured off the STEP ------------------------------------------------
RUN_HALF = 20.07          # run collet face from the body centre
BRANCH_REACH = 20.07      # branch collet face from the same centre
HALF_W = 6.86             # the body's own radius about the run axis
TUBE_D = 6.35             # the 1/4" OD LLDPE all three ports accept
MEASURE_TOL = 0.01        # what the figures above are rounded to

# THE ROUND BARREL ON EACH ARM — the stretch a printed seat closes on. Every arm carries the same
# three sections outward from the centre: a waist the branch's own arm crosses, then the barrel
# and the collet cap standing `BARREL_R` about the axis, then the release nose stepping back in
# so a thumb reaches it. `BARREL_NEAR` is where the waist ends and `BARREL_FAR` where the nose
# begins, so a rib laid between them bears on the cap and clears the release.
BARREL_NEAR = 7.0
BARREL_FAR = 17.0
BARREL_R = 6.858


def run(sign):
    """One of the run's two collinear ports, `sign` picking the +Z or −Z end."""
    return ((0.0, 0.0, sign * RUN_HALF), (0.0, 0.0, sign))


def run_barrel(sign):
    """The barrel on one of the run's two arms — `(station, radius, length)`, `station` its
    mid-point and the run axis through it."""
    return (((0.0, 0.0, sign * (BARREL_NEAR + BARREL_FAR) / 2.0), (0.0, 0.0, sign)),
            BARREL_R, BARREL_FAR - BARREL_NEAR)


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
    solid = import_step(str(STEP)).val()
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
    for label, lo, hi, claimed in (("barrel", BARREL_NEAR, BARREL_FAR, BARREL_R),
                                   ("release nose", BARREL_FAR, RUN_HALF, None)):
        actual = _arm_radius(solid, lo, hi)
        if claimed is None:
            if actual >= BARREL_R - MEASURE_TOL:
                raise ValueError(
                    f"the tee's {label} stands {actual:.4f} about the run and the barrel stands "
                    f"{BARREL_R:g} — a seat bored for the barrel would close on the release "
                    f"instead of leaving it for a thumb.")
        elif abs(actual - claimed) > MEASURE_TOL:
            raise ValueError(
                f"tee-connector BARREL_R is {claimed:g} and the STEP's own {label} stands "
                f"{actual:.4f} about the run over {lo:g}..{hi:g} — {abs(actual - claimed):.4f} mm "
                f"apart, over the {MEASURE_TOL:g} mm this file rounds to. A seat bored for it "
                f"closes on a body that is not that shape.")


def _arm_radius(solid, lo: float, hi: float) -> float:
    """The widest the body stands about the run axis between two stations on the +Z arm."""
    bb = solid.BoundingBox()
    band = cq.Solid.makeBox(
        2 * bb.xlen, 2 * bb.ylen, hi - lo, cq.Vector(-bb.xlen, -bb.ylen, lo))
    cut = solid.intersect(band).BoundingBox()
    return max(cut.xmax, -cut.xmin)


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
