"""Line-art reference solid of the LOKMAN 304 SS worm-gear clamp, 10–16 mm
([`ledger/bom.md`](/hardware/ledger/bom.md) §3).

A steel band wrapped to a circle, a housing straddling it carrying the worm
screw, and the band's free tail run out through that housing. Turning the screw
draws the tail through and closes the band; the housing stands well off the
circle and stays where it is.

One closes the backflow-vent telltale's clear PVC stub onto the ASSE 1022's vent barb — see
`hardware/assembly/internal-plumbing.md`.

Coordinate convention:
  Z = the clamped axis, the tube running through the band. The band is centred
      on Z = 0, so it spans ±`BAND_W / 2`.
  +X = the way the housing stands off the band, and the way the screw head
      faces. Origin = the clamped circle's own centre.

Geometry is in the frozen STEP and display payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from pathlib import Path

_here = Path(__file__).resolve()
STEP_PATH = _here.parent / "worm-clamp.step"
PAYLOAD_PATH = _here.parent / "worm-clamp.step.mesh"
ASSET_MANIFEST_PATH = _here.parent / "frozen-asset.json"

STEP = _here.parent / "worm-clamp.step"

# --- what the listing states ------------------------------------------------

RANGE = (10.0, 16.0)    # the diameters this clamp closes between
MATERIAL = "304 stainless steel"

# --- the envelope -----------------------------------------------------------
#
# The DIN 3017-W1 8 mm-band micro family's nominal envelope. SEEDED, NOT RATIFIED — measure the
# clamp in hand before anything is spaced to these five figures.
BAND_W = 8.0            # band width, along the clamped axis
BAND_T = 0.6            # band thickness
HOUSING_L = 14.0        # housing length, ALONG the band (the arc it straddles)
HOUSING_W = 9.5         # housing width, across the band
HOUSING_H = 7.0         # how far the housing rises off the band's own outer face
SCREW_D = 7.0           # worm screw head Ø
SCREW_PROUD = 4.0       # how far that head stands off the housing's end face
TAIL_LEN = 12.0         # the band's free end, out past the housing


def stand_off(clamp_d: float) -> float:
    """How far the clamp reaches from the clamped AXIS at its tallest — the housing's crown."""
    return clamp_d / 2.0 + BAND_T + HOUSING_H


def envelope(clamp_d: float) -> tuple:
    """`(across, along)` the clamp takes: twice its tallest reach from the axis, and its
    length on the clamped axis. The band alone is `clamp_d + 2 × BAND_T` across; the housing
    is on one side of it."""
    return (2.0 * stand_off(clamp_d), max(BAND_W, HOUSING_W))


def holds(clamp_d: float) -> None:
    """The clamp closes on this diameter, or it does not.

    Below `RANGE`'s floor the band bottoms on itself with the joint still loose; above its
    ceiling the tail runs out of the housing."""
    lo, hi = RANGE
    if not lo <= clamp_d <= hi:
        raise ValueError(
            f"a {lo:g}–{hi:g} mm worm clamp is asked to close on Ø{clamp_d:.2f} — outside its "
            f"band, so the joint is either not closed or not reached. Bill the size that "
            f"carries this diameter, or state the joint at one this clamp holds.")


def main():
    print("worm-clamp")
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
