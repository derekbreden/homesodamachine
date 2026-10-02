"""The funnel's drain stub, and the joint it closes — a length of 1/4" LLDPE standing in the drain
elbow's upper collet, up through the funnel frame's drain hole into the silicone plug's land.

The funnel lifts out of the machine for the dishwasher and the stub stays. The PP0308E elbow under
the frame grips its lower end; the plug's sealing land closes on its upper end when the funnel goes
back in. Lifting the funnel slides the land off it, and a thumb on the collet frees the stub.

THIS FILE WRITES NO SOLID. The stub is a cut length of the same 1/4" LLDPE every water-side run is
drawn from, so it is stock and not a part: `build_stub()` hands it to the assembly that seats it,
the way any other run is drawn. What is a part here is the JOINT — the figures it stands on and
the checks `joint_holds()` reads them against.

Frame:
  Origin = the elbow's +Z release face, on its axis. +Z = up, through the frame's hole into the
      plug. The stub runs from `-UNION_INSERTION` to `FACE_GAP + FUNNEL_ENGAGEMENT`.

Run:
    tools/cad-venv/bin/python hardware/reference/funnel-drain-stub/funnel_drain_stub.py selftest
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts",
           _hw / "reference" / "jg-pp0308e-elbow",
           _hw / "printed-parts" / "zone-c" / "funnel"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import elbow as _union
import elbow_cradle as _cradle
import funnel as _funnel

STUB_OD = 6.35          # 1/4" LLDPE, the same stock every water-side run is cut from
STUB_ID = 4.32          # its bore
# The elbow's nose bears on the frame's underside and the plug sits on the web's top, so the
# web less the elbow's collet projection stands between the release face and the plug.
FACE_GAP = _cradle.WEB - (_cradle.ELBOW_Z + _union.COLLET_FACE)
# The plug's bore from its bottom face to the top of its sealing land.
FUNNEL_ENGAGEMENT = _funnel.spout_tube
# Collet face to tube stop for John Guest's 1/4" PP range, data sheet Pp4608_01/23 row D
# (`jg_pp0208e_tee.INSERTION`). The scan leaves the elbow's own stop unmeasured
# (`elbow.INSERTION`); a shallower stop only carries the stub further up the plug's bore.
UNION_INSERTION = 15.7
LENGTH = UNION_INSERTION + FACE_GAP + FUNNEL_ENGAGEMENT
# The land the plug seals on, measured down from the stub's top.
LAND = _funnel.sealing_land


def joint_holds() -> None:
    """The stub reaches through the elbow's collet to its stop and up through the whole land."""
    if FACE_GAP < 0.0:
        raise ValueError(
            f"the elbow's release face stands {-FACE_GAP:.2f} mm above the plug's bottom face — "
            f"its collet would bear on the silicone.")
    if FUNNEL_ENGAGEMENT < LAND:
        raise ValueError(
            f"the plug's bore reaches {FUNNEL_ENGAGEMENT:.2f} mm up to its land's top and the "
            f"land is {LAND:g} mm: the stub would stop short of sealing.")
    if STUB_OD <= _funnel.sealing_id:
        raise ValueError(
            f"the {STUB_OD:g} mm stub does not fill the plug's {_funnel.sealing_id:g} mm land.")


def build_stub():
    """The stub alone: `LENGTH` of 1/4" LLDPE, bored, standing on the elbow's release face."""
    return (cq.Workplane("XY", origin=(0, 0, -UNION_INSERTION))
            .circle(STUB_OD / 2.0).circle(STUB_ID / 2.0)
            .extrude(LENGTH))


def selftest():
    joint_holds()
    return [f"  the stub is {LENGTH:.2f} mm: {UNION_INSERTION:g} in the elbow, {FACE_GAP:.3f} "
            f"through the web, and {FUNNEL_ENGAGEMENT:.3f} up the plug to its land's top"]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(line)
        print("funnel_drain_stub selftest OK")
    else:
        print(__doc__)
