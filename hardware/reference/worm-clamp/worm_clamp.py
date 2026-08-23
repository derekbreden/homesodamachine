"""Line-art reference solid of the LOKMAN 304 SS worm-gear clamp, 10–16 mm
([`ledger/bom.md`](/hardware/ledger/bom.md) §3).

A steel band wrapped to a circle, a housing straddling it carrying the worm
screw, and the band's free tail run out through that housing. Turning the screw
draws the tail through and closes the band; the housing stands well off the
circle and stays where it is.

One closes the funnel's silicone spout onto its drain stub — see
`hardware/reference/funnel-drain-stub/`.

Coordinate convention:
  Z = the clamped axis, the tube running through the band. The band is centred
      on Z = 0, so it spans ±`BAND_W / 2`.
  +X = the way the housing stands off the band, and the way the screw head
      faces. Origin = the clamped circle's own centre.

Run:
    tools/cad-venv/bin/python hardware/reference/worm-clamp/worm_clamp.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_assembly
from _materials import M_STAINLESS, one_body

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


# --- the solid --------------------------------------------------------------

def _band(clamp_d):
    """The wrapped steel band: an annulus `BAND_T` thick, closed on `clamp_d`."""
    r = clamp_d / 2.0
    return (cq.Workplane("XY", origin=(0, 0, -BAND_W / 2.0))
            .circle(r + BAND_T).circle(r)
            .extrude(BAND_W).val())


def _housing(clamp_d):
    """The screw housing, straddling the band on +X: it sits on the band's outer face and
    reaches `HOUSING_H` beyond it, its length along the band's arc."""
    r0 = clamp_d / 2.0 + BAND_T
    return (cq.Workplane("XY", origin=(r0 + HOUSING_H / 2.0, 0, 0))
            .box(HOUSING_H, HOUSING_L, HOUSING_W).val())


def _screw(clamp_d):
    """The worm screw's head, on the housing's −Y end face, turned about the band's own
    tangent — the axis a driver comes in on."""
    r0 = clamp_d / 2.0 + BAND_T
    y = -HOUSING_L / 2.0
    return cq.Solid.makeCylinder(
        SCREW_D / 2.0, SCREW_PROUD,
        cq.Vector(r0 + HOUSING_H / 2.0, y - SCREW_PROUD, 0), cq.Vector(0, 1, 0))


def _tail(clamp_d):
    """The band's free end, out through the housing and standing off it along −Y."""
    r0 = clamp_d / 2.0
    return (cq.Workplane("XY", origin=(r0, HOUSING_L / 2.0 - TAIL_LEN, -BAND_W / 2.0))
            .box(BAND_T, TAIL_LEN, BAND_W, centered=(False, False, False)).val())


def build_worm_clamp(clamp_d: float):
    """The clamp closed on `clamp_d`, as a single solid wrapped in a `cq.Workplane`."""
    holds(clamp_d)
    return cq.Workplane(obj=_band(clamp_d).fuse(_housing(clamp_d), _screw(clamp_d),
                                                _tail(clamp_d)))


def main():
    # The STEP stands at the middle of the band. A placement builds its own at the diameter
    # it closes on.
    nominal = sum(RANGE) / 2.0
    part = build_worm_clamp(nominal)
    bb = part.val().BoundingBox()
    print(f"LOKMAN worm-gear clamp, {RANGE[0]:g}–{RANGE[1]:g} mm, {MATERIAL} — simplified")
    print(f"  Drawn closed on Ø{nominal:g}")
    print(f"  Canonical-frame bounding box: "
          f"X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
          f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Band {BAND_W:g} wide × {BAND_T:g} thick; housing crown "
          f"{stand_off(nominal):.2f} mm off the axis")
    print(f"  Solid valid: {part.val().isValid()}")

    export_assembly(one_body(part, "worm-clamp", M_STAINLESS), str(STEP))
    print(f"-> {STEP.name}")


if __name__ == "__main__":
    main()
