"""The SeaFlo's discharge chain — the three fittings that carry the pump's outlet
from its 3/8" hose barb onto the 1/4" LLDPE that reaches the cold core's water
inlet ([`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §2), made
up as one piece and hung in the bag-fall corridor.

The pump's barbs are molded into the head casting — there is no port thread and
no elbow fits them, so the only connection the pump offers is a hose over the
barb with a clamp. A stub of 3/8" braided PVC carries the water off the barb and
turns it down into this chain, which stands in the corridor:

  * **MAACFLOW** 3/8" hose barb × 1/4" NPT M — the stub clamps over this barb, so
    the 3/8" ends here.
  * **GASHER** 1/4" NPT check, female in / male out — its socket takes the
    MAACFLOW's thread. The arrow points away from the pump; this is what holds
    the carbonator's pressure off the pump when it is idle.
  * **PP450822E** 1/4" NPT F × 1/4" PTC — its socket takes the check's male stub
    and its collet starts the 1/4" LLDPE.

External envelopes only, each fitting a plain body at its nominal size; every
NPT joint is drawn made up to its engagement, so the length is what the chain
actually stands, not the sum of the parts.

Frame: +Z = flow (the chain hangs vertically, water running DOWN it), the barb
tip at Z = 0 and the 1/4" PTC collet mouth at −Z. Centered on X and Y.

Run:
    tools/cad-venv/bin/python hardware/reference/seaflo-discharge-chain/seaflo_discharge_chain.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_hw / "reference" / "gasher-check-valve"))
from _cadq_export import export_step
import gasher_check_valve as check   # the middle fitting's own three sections

NPT_ENGAGE = 11.0           # how deep a 1/4" NPT male runs into its female

# MAACFLOW 3/8" hose barb x 1/4" NPT M — 39.4 mm overall (listing item dimensions).
BARB_D, BARB_L = 11.5, 22.0     # the ridged 3/8" barb the hose stub clamps over
MAAC_HEX, MAAC_HEX_L = 17.0, 6.0
MAAC_NPT_D, MAAC_NPT_L = 13.7, 11.4

# John Guest PP450822E 1/4" NPT F x 1/4" PTC.
JG_SOCKET_D, JG_SOCKET_L = 15.0, 8.0
JG_HEX, JG_HEX_L = 16.5, 5.0
JG_COLLET_D, JG_COLLET_L = 14.0, 13.0

TUBE_D = 6.35               # the 1/4" OD LLDPE the collet accepts
HOSE_ID = 9.525             # the 3/8" ID braided PVC the barb takes
HOSE_OD = 15.10             # the same hose over the barb — what a neighbouring body clears

# Made up: each male buries NPT_ENGAGE in the female below it. The check contributes its
# own overall length, off the module that draws it.
LENGTH = (BARB_L + MAAC_HEX_L + MAAC_NPT_L
          + check.TOTAL_LENGTH
          + JG_SOCKET_L + JG_HEX_L + JG_COLLET_L
          - 2 * NPT_ENGAGE)


def barb_tip():
    """The MAACFLOW's barb tip — the open end the 3/8" hose stub slips over:
    (position, outward axis). This is where the chain meets the hose off the
    pump, and the last 3/8" on the discharge side."""
    return (0.0, 0.0, 0.0), (0.0, 0.0, 1.0)


def tube_port():
    """The PP450822E's 1/4" PTC mouth the LLDPE pushes into: (position, axis)."""
    return (0.0, 0.0, -LENGTH), (0.0, 0.0, -1.0)


def build():
    """The three fittings stacked along −Z, barb tip at Z = 0, made up at each
    NPT joint so the stack stands its real length. The check's three sections come off
    its own module — socket boss, hex barrel, male stub, at the sizes it draws them."""
    part, z = None, 0.0
    for dia, length in ((BARB_D, BARB_L),
                        (MAAC_HEX, MAAC_HEX_L),
                        (MAAC_NPT_D, MAAC_NPT_L - NPT_ENGAGE),
                        (check.SOCKET_D, check.SOCKET_LENGTH),
                        (check.HEX_ACROSS_CORNERS, check.HEX_LENGTH),
                        (check.THREAD_D, check.STUB_LENGTH - NPT_ENGAGE),
                        (JG_SOCKET_D, JG_SOCKET_L),
                        (JG_HEX, JG_HEX_L),
                        (JG_COLLET_D, JG_COLLET_L)):
        z -= length
        seg = cq.Solid.makeCylinder(
            dia / 2.0, length, cq.Vector(0, 0, z), cq.Vector(0, 0, 1))
        part = seg if part is None else part.fuse(seg)
    return part


def main():
    part = build()
    bb = part.BoundingBox()
    print("SeaFlo discharge chain — MAACFLOW barb + GASHER check + PP450822E")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  made up {LENGTH:.1f} mm barb tip to collet mouth")
    for label, (pos, axis) in (("barb-tip ", barb_tip()), ("tube-port", tube_port())):
        print(f"  {label}: ({pos[0]:7.2f}, {pos[1]:6.2f}, {pos[2]:7.2f})  out {axis}")
    out = _here.parent / "seaflo-discharge-chain.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
