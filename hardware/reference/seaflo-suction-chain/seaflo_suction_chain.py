"""The SeaFlo's suction chain — the two fittings that carry the pump's inlet from
the 1/4" LLDPE that reaches it off V-K down onto its 3/8" hose barb
([`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §2), made up
as one piece and hung off the suction barb on a stub.

The pump's barbs are molded into the head casting — there is no port thread and
no elbow fits them, so the only connection the pump offers is a hose over the
barb with a clamp. A stub of 3/8" braided PVC carries the water off the barb to
this chain, where the 3/8" ends:

  * **MAACFLOW** 3/8" hose barb × 1/4" NPT M — the stub clamps over this barb.
  * **PP450822E** 1/4" NPT F × 1/4" PTC — its socket takes the MAACFLOW's thread
    and its collet takes the 1/4" LLDPE.

It is the discharge chain less the GASHER check: nothing holds pressure off the
pump on the inlet side, so the two fittings thread straight together. Flow runs
COLLET TO BARB here, the opposite of its twin, which is why the check is absent
and not merely omitted.

External envelopes only, each fitting a plain body at its nominal size; the one
NPT joint is drawn made up to its engagement, so the length is what the chain
actually stands, not the sum of the parts.

Frame: the barb tip at Z = 0 and the 1/4" PTC collet mouth at −Z — the same
frame its twin is drawn in, so one turn reads the same against either.

Run:
    tools/cad-venv/bin/python hardware/reference/seaflo-suction-chain/seaflo_suction_chain.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_hw / "reference" / "seaflo-discharge-chain"))
from _cadq_export import export_step
import seaflo_discharge_chain as disch   # the same two fittings, off the same BOM lines

# Both fittings are the parts the discharge chain already draws — the same MAACFLOW off the
# same 4-pack and the same PP450822E out of the same bag — so their sections come off that
# module rather than being restated here.
NPT_ENGAGE = disch.NPT_ENGAGE
TUBE_D = disch.TUBE_D               # the 1/4" OD LLDPE the collet accepts
HOSE_ID = disch.HOSE_ID             # the 3/8" ID reinforced PVC the barb takes
HOSE_OD = disch.HOSE_OD             # the same hose over the barb — what a neighbour clears

# Made up: the MAACFLOW's male buries NPT_ENGAGE in the PP450822E's female. One joint, so
# one engagement — the check the discharge chain carries between them is not here.
LENGTH = (disch.BARB_L + disch.MAAC_HEX_L + disch.MAAC_NPT_L
          + disch.JG_SOCKET_L + disch.JG_HEX_L + disch.JG_COLLET_L
          - NPT_ENGAGE)


def barb_tip():
    """The MAACFLOW's barb tip — the open end the 3/8" hose stub slips over:
    (position, outward axis). This is where the chain meets the hose onto the
    pump, and the last 3/8" on the suction side."""
    return (0.0, 0.0, 0.0), (0.0, 0.0, 1.0)


def tube_port():
    """The PP450822E's 1/4" PTC mouth the LLDPE pushes into: (position, axis)."""
    return (0.0, 0.0, -LENGTH), (0.0, 0.0, -1.0)


def build():
    """The two fittings stacked along −Z, barb tip at Z = 0, made up at the one NPT
    joint so the stack stands its real length."""
    part, z = None, 0.0
    for dia, length in ((disch.BARB_D, disch.BARB_L),
                        (disch.MAAC_HEX, disch.MAAC_HEX_L),
                        (disch.MAAC_NPT_D, disch.MAAC_NPT_L - NPT_ENGAGE),
                        (disch.JG_SOCKET_D, disch.JG_SOCKET_L),
                        (disch.JG_HEX, disch.JG_HEX_L),
                        (disch.JG_COLLET_D, disch.JG_COLLET_L)):
        z -= length
        seg = cq.Solid.makeCylinder(
            dia / 2.0, length, cq.Vector(0, 0, z), cq.Vector(0, 0, 1))
        part = seg if part is None else part.fuse(seg)
    return part


def main():
    part = build()
    bb = part.BoundingBox()
    print("SeaFlo suction chain — MAACFLOW barb + PP450822E")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  made up {LENGTH:.1f} mm barb tip to collet mouth "
          f"({disch.LENGTH - LENGTH:.1f} mm shorter than the discharge chain, the check's share)")
    for label, (pos, axis) in (("barb-tip ", barb_tip()), ("tube-port", tube_port())):
        print(f"  {label}: ({pos[0]:7.2f}, {pos[1]:6.2f}, {pos[2]:7.2f})  out {axis}")
    out = _here.parent / "seaflo-suction-chain.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
