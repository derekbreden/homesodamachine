"""Tee connector — the three-port union the manifold's junctions are built from.

`tee-connector.step` is a harvested solid standing in for the John Guest PP0208E
(`README.md`): there is no builder here, and every number in the first block below was
measured off that file. `stations_hold` reads them back off it at import of the pack that
places it, so a measurement and the metal it was taken from cannot part. The second block is
calipered on the PP0208E in hand, which the STEP does not carry.

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

# THE MOUTH COLLAR, AND THE COLLET STANDING PROUD OF IT. `BARREL_R` is the widest anything on
# an arm reaches over `BARREL_NEAR`..`BARREL_FAR`, which is what a rib laid across the arm must
# CLEAR. These are the band that IS that radius, which is what a bore can BEAR on: a journal
# closed on the collar holds the arm across its own axis and leaves it free along it.
# `BODY_FACE` is where the collar ends and the collet stands out of it, so `COLLET_PROUD` is
# the collet's whole exposed length — press it that far and the grip is fully open, which makes
# it the CEILING on any release stroke built around this fitting. The same three figures the
# calipered members of this family carry (`../jg-pp0408w/`, `../jg-pp061208w/`,
# `../jg-pp451223w/`), read off the solid here because this one is harvested.
CAP_NEAR = 12.815         # the collar's inboard end, off the body centre
CAP_FAR = 16.700          # the last station standing full `BARREL_R`; the collar breaks after
BODY_FACE = 16.95         # where the collar ends and the collet begins
COLLET_PROUD = RUN_HALF - BODY_FACE
ARM_ROOT = 8.2            # where the arm's own round section begins, off the body centre
ARM_R = 6.6415            # what the arm stands from that root out to the collar

# --- Measured on the PP0208E in hand ----------------------------------------
# Calipered on the production tee, not read off the stand-in STEP, so `stations_hold` does not
# hold them. The two spans are collet face to collet face along the run. The three depths are
# how far a 1/4" tube stands inside one collet from the sleeve's face, sleeve extended.
RUN_SPAN = 42.5            # sleeves extended
RUN_SPAN_PRESSED = 39.2    # both sleeves pressed home
COLLET_TRAVEL = (RUN_SPAN - RUN_SPAN_PRESSED) / 2.0   # one sleeve's stroke, 1.65
FIRST_RESISTANCE = 7.0     # the tube first meets the mechanism
GRIP_DEPTH = 8.5           # the teeth hold from here in; at 8.4 the tube still draws out
INSERTION = 10.0           # the tube bottoms


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


def branch_collar():
    """The mouth collar on the branch arm — `(station, radius, length)`, `station` its
    mid-point with the branch axis through it. What a printed bore journals on."""
    return (((0.0, (CAP_NEAR + CAP_FAR) / 2.0, 0.0), (0.0, 1.0, 0.0)),
            BARREL_R, CAP_FAR - CAP_NEAR)


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
    # THE BRANCH ARM CARRIES THE SAME PROFILE, and a journal is closed on it rather than a rib
    # laid across it, so it is held here in its own right. Two readings: the collar stands full
    # `BARREL_R` the whole way over `CAP_NEAR`..`CAP_FAR`, and nothing past `BODY_FACE` stands
    # that wide. The first is what a bore bears on; the second is what leaves the collet free to
    # be pressed inside that bore, which is the whole of the release.
    # READ THE NARROWEST STATION ACROSS THE BAND, not the widest in it. A journal bears along
    # its whole length, so what matters is where the collar is thinnest — and a band claimed
    # wider than the collar actually is still contains the collar's own full radius somewhere,
    # so a widest-in-band reading passes exactly the error worth catching.
    thin, wide = _branch_band(solid, CAP_NEAR, CAP_FAR)
    # AND THE ROUND ROOT BEHIND IT, on the same reading — the stretch a bore passes rather than
    # bears on, and what fixes how deep a wall can take the arm before the run body stops it.
    root_thin, _root_wide = _branch_band(solid, ARM_ROOT, CAP_NEAR)
    if abs(root_thin - ARM_R) > MEASURE_TOL:
        raise ValueError(
            f"tee-connector ARM_R is {ARM_R:g} and the narrowest station of the STEP's own "
            f"branch arm stands {root_thin:.4f} over {ARM_ROOT:g}..{CAP_NEAR:g} — "
            f"{abs(root_thin - ARM_R):.4f} mm apart, over the {MEASURE_TOL:g} mm this file "
            f"rounds to. A wall taken to `ARM_ROOT` closes on a body that is not that shape.")
    # BOTH ENDS OF THE COLLAR PINNED FROM OUTSIDE. The band reading alone cannot fix an edge
    # finer than one slice; these say the arm is already NARROWER one slice past each end, which
    # is what makes `CAP_NEAR` and `CAP_FAR` the collar's own stations rather than near them.
    for label, lo, hi in (("inboard of", CAP_NEAR - 0.1, CAP_NEAR - 0.05),
                          ("outboard of", CAP_FAR + 0.05, CAP_FAR + 0.1)):
        seen = _branch_radius(solid, lo, hi)
        if seen >= BARREL_R - MEASURE_TOL:
            raise ValueError(
                f"the tee's branch arm still stands {seen:.4f} at {lo:g}..{hi:g}, {label} the "
                f"collar this file declares — so the collar runs past the station claimed for "
                f"it and a journal struck on it bears on less than it thinks.")
    for label, seen in (("narrowest", thin), ("widest", wide)):
        if abs(seen - BARREL_R) > MEASURE_TOL:
            raise ValueError(
                f"tee-connector BARREL_R is {BARREL_R:g} and the {label} station of the STEP's "
                f"own branch collar stands {seen:.4f} over {CAP_NEAR:g}..{CAP_FAR:g} — "
                f"{abs(seen - BARREL_R):.4f} mm apart, over the {MEASURE_TOL:g} mm this file "
                f"rounds to. A bore journalled on the collar rides on a body that is not that "
                f"shape for the whole of its length.")
    collet = _branch_radius(solid, BODY_FACE, BRANCH_REACH)
    if collet >= BARREL_R - MEASURE_TOL:
        raise ValueError(
            f"the tee's branch collet stands {collet:.4f} about its axis and the collar stands "
            f"{BARREL_R:g} — a bore journalled on the collar would close on the collet too, and "
            f"a collet a bore grips cannot be pressed to release the tube it holds.")


def _branch_band(solid, lo: float, hi: float, step: float = 0.5):
    """The narrowest and widest the body stands about the branch axis ACROSS a band, read one
    slice at a time. `_branch_radius` over the whole band answers only the widest, which a band
    claimed longer than the feature still satisfies."""
    n = max(2, int(round((hi - lo) / step)))
    edges = [lo + (hi - lo) * i / n for i in range(n + 1)]
    seen = [_branch_radius(solid, a, b) for a, b in zip(edges, edges[1:])]
    return min(seen), max(seen)


def _branch_radius(solid, lo: float, hi: float) -> float:
    """The widest the body stands about the BRANCH axis between two stations on the +Y arm."""
    bb = solid.BoundingBox()
    band = cq.Solid.makeBox(
        2 * bb.xlen, hi - lo, 2 * bb.zlen, cq.Vector(-bb.xlen, lo, -bb.zlen))
    cut = solid.intersect(band).BoundingBox()
    return max(cut.xmax, -cut.xmin, cut.zmax, -cut.zmin)


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
