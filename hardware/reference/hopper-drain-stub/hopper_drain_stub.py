"""The hopper basin's drain stub, and the joint it is closed in — a length of
1/4" LLDPE run up inside the silicone spout and closed there under a worm clamp.

The basin comes out of the machine and goes into the dishwasher. The stub goes
with it: it is worm-clamped to the spout at the factory and stays. What parts is
the stub's free end and the John Guest union under the top wall — thumb on the
collet, basin lifts out; stub back into the collet, basin back in.

The stub is hidden at both ends. `FUNNEL_ENGAGEMENT` of it stands inside the
silicone and `UNION_INSERTION` inside the union, and the union's collet face
meets the spout's own exit face, so nothing of it is in the room between them.

THIS FILE WRITES NO SOLID. The stub is a cut length of the same 1/4" LLDPE every
water-side run is drawn from, so it is stock and not a part: `build_stub()` hands
it to the assembly that seats it, the way any other run is drawn. What is a part
here is the JOINT — the three figures it stands on and the checks `joint_holds()`
reads them against.

Frame:
  Origin = the spout's exit face, on the spout's axis — the plane the funnel's
      silicone ends and the union's collet begins.
  +Z = up, into the funnel. The stub runs from `-UNION_INSERTION` to
      `+FUNNEL_ENGAGEMENT`; the union hangs at z ≤ 0.

Run:
    tools/cad-venv/bin/python hardware/reference/hopper-drain-stub/hopper_drain_stub.py selftest
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts",
           _hw / "reference" / "worm-clamp",
           _hw / "reference" / "jg-pp0408w",
           _hw / "printed-parts" / "zone-c" / "hopper-funnel"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import worm_clamp as _clamp
import jg_pp0408w as _union
import hopper_funnel as _funnel

# --- the stub ---------------------------------------------------------------

STUB_OD = 6.35          # 1/4" LLDPE, the same stock every water-side run is cut from
STUB_ID = 4.32          # its bore
# Up the spout's straight land as far as the ramp tip, which is where the bore stops being
# round and starts opening into the basin's floor.
FUNNEL_ENGAGEMENT = _funnel.spout_tube
UNION_INSERTION = _union.INSERTION
LENGTH = FUNNEL_ENGAGEMENT + UNION_INSERTION

# --- the clamped joint ------------------------------------------------------

SPOUT_OD = 2.0 * (_funnel.spout_id / 2.0 + _funnel.spout_wall)
# The band lands on the spout as moulded, and the silicone gives under it from there. What is
# left between the spout and the clamp's floor is the travel the screw still has — the whole of
# the bite this joint can be closed to, on a wall of `_funnel.spout_wall`.
CLAMP_D = SPOUT_OD
CLAMP_RESERVE = SPOUT_OD - _clamp.RANGE[0]
# The band sits centred on the land, `_clamp.BAND_W` of it between two shoulders of silicone.
CLAMP_Z = FUNNEL_ENGAGEMENT / 2.0
CLAMP_SHOULDER = (FUNNEL_ENGAGEMENT - _clamp.BAND_W) / 2.0

# --- the union under it -----------------------------------------------------

# The union's upper collet face lies on the spout's exit face, so its far port — where
# `fluid-4` starts — hangs this far below the drain.
UNION_DROP = _union.OVERALL


def union_port() -> tuple:
    """Where `fluid-4` leaves the joint: `(position, outward axis)` in this frame, the union's
    lower collet face looking down."""
    return ((0.0, 0.0, -UNION_DROP), (0.0, 0.0, -1.0))


def joint_holds() -> None:
    """The three figures the joint stands on, against the parts that carry them.

    The band has to land on round silicone with a shoulder either side of it; the clamp has to
    reach the diameter that silicone presents; and the stub has to be long enough to be inside
    both the spout and the union at once."""
    if CLAMP_SHOULDER < 0.0:
        raise ValueError(
            f"the spout's straight land is {FUNNEL_ENGAGEMENT:.2f} mm and the clamp's band is "
            f"{_clamp.BAND_W:g} mm wide — the band runs off the land and onto the ramp cone, "
            f"where the spout is no longer round. Set `hopper_funnel.spout_tube` to at least "
            f"{_clamp.BAND_W:g} mm, or bill a narrower band.")
    _clamp.holds(CLAMP_D)
    lo, hi = _clamp.RANGE
    if not lo <= SPOUT_OD <= hi:
        raise ValueError(
            f"the spout is Ø{SPOUT_OD:.2f} and the clamp closes between Ø{lo:g} and Ø{hi:g} — "
            f"it does not reach the silicone. Bill the size that carries this spout.")
    if LENGTH <= UNION_INSERTION:
        raise ValueError(
            f"the stub is {LENGTH:.2f} mm and {UNION_INSERTION:g} of it is inside the union — "
            f"nothing is left for the spout to be clamped onto.")


# --- the solids -------------------------------------------------------------

def build_stub():
    """The stub alone: `LENGTH` of 1/4" LLDPE, bored, standing on the joint face."""
    return (cq.Workplane("XY", origin=(0, 0, -UNION_INSERTION))
            .circle(STUB_OD / 2.0).circle(STUB_ID / 2.0)
            .extrude(LENGTH))


def build_clamp():
    """The worm clamp, closed on the spout at `CLAMP_Z`. The housing faces +X."""
    return _clamp.build_worm_clamp(CLAMP_D).translate((0, 0, CLAMP_Z))


def build_union():
    """The union hanging off the joint face, its upper collet on z = 0."""
    return _union.build_jg_pp0408w().translate((0, 0, -_union.reach()))


# --- controls -------------------------------------------------------------

def selftest():
    joint_holds()
    return ["  the band lands on round silicone, the clamp reaches it, and the stub is "
            "inside the spout and the union at once"]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(line)
        print("hopper_drain_stub selftest OK")
    else:
        print(__doc__)
