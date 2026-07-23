"""ASSE 1022 assembly: the Multiplex 19-0897 backflow preventer with everything
that threads or clamps directly onto it.

The water path's one non-negotiable component and the four fittings that make it
reachable from 1/4" tube — the chain [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md)
step 2 builds, in the order it builds them:

    1/4" LLDPE → PP010822E → GAGIRA coupling → [ASSE 1022] → FFL38BARB38 → 3/8" hose
                                                     └ vent stub ↓ drip pan

Every station is read off the part upstream of it: each fitting's own module says
how deep its threads go, and this file stacks those reaches along the flow axis.
Move a length in any reference module and the chain closes on the new one.

The vent is the assembly's reason for a pose rather than a bare envelope: it must
point DOWN, into the drip pan over the moisture sensor, because it is the
mechanical telltale for a cross-contamination event
([`future.md`](/hardware/future.md) "Backflow vent monitoring"). Anything that
places this assembly inherits that constraint — the vent stub's tip is the datum
the pan has to catch.

Frame: the ASSE 1022's own — +X = flow, inlet upstream at its X = 0, the vent
running −Z. The upstream fittings therefore sit at negative X.

Run:
    tools/cad-venv/bin/python hardware/reference/asse1022-assembly/asse1022_assembly.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hw / "scripts",
    _hw / "reference" / "multiplex-asse1022",
    _hw / "reference" / "gagira-reducing-coupling",
    _hw / "reference" / "jg-pp010822e",
    _hw / "reference" / "ffl38barb38",
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly
import ffl38barb38 as barb
import gagira_reducing_coupling as coupling
import jg_pp010822e as ptc
import multiplex_asse1022 as bfp

BRASS = cq.Color(0.72, 0.58, 0.28)      # the Multiplex body
STAINLESS = cq.Color(0.72, 0.74, 0.78)  # 316L / 304 SS — the coupling, the barb stem
BLACK_PP = cq.Color(0.16, 0.16, 0.18)   # John Guest black polypropylene
CLEAR_PVC = cq.Color(0.85, 0.90, 0.92, 0.45)

# The vent stub: Sealproof 1/4" ID × 3/8" OD clear PVC, bored to the barb it slips
# over so the barb occupies the hose rather than its wall. It runs past the barb
# tip toward the pan; the reach is what clears the parts below it, set where this
# assembly is placed, and this is the length the bench cuts (~12" of stock, trimmed).
VENT_STUB_OD = 9.53
VENT_STUB_REACH = 50.0          # below the barb tip, toward the drip pan

# Where each fitting lands on the flow axis, each read off the part it threads into.
# The barrel's two shoulders are what the female fittings butt against.
BARREL_UPSTREAM = bfp.INLET_LENGTH                        # the inlet thread's root
BARREL_DOWNSTREAM = BARREL_UPSTREAM + bfp.BARREL_LENGTH   # the flare thread's root
# The coupling swallows the ASSE inlet to its full socket depth, so its large-end
# face lands on that shoulder and its body reaches upstream by its own length.
COUPLING_X = BARREL_UPSTREAM - coupling.LENGTH
# The PTC's shank threads into the coupling's small socket, so the shank tip lands
# that far inside the coupling's upstream face.
PTC_X = COUPLING_X + coupling.SMALL_SOCKET_DEPTH - ptc.LENGTH
# The swivel nut is drawn up over the flare, its face on the downstream shoulder.
BARB_X = BARREL_DOWNSTREAM


def vent_stub():
    """The clear-PVC telltale stub, slipped over the vent barb and running down
    past its tip. Bored at the barb Ø, so the two share a surface and no metal."""
    _tip, _axis = bfp.vent()
    top = bfp.VENT_DROP                     # the body's underside, where the hose stops
    length = top + VENT_STUB_REACH
    stub = cq.Solid.makeCylinder(
        VENT_STUB_OD / 2.0, length,
        cq.Vector(bfp.VENT_X, 0.0, top), cq.Vector(0, 0, -1))
    bore = cq.Solid.makeCylinder(
        bfp.VENT_D / 2.0, length,
        cq.Vector(bfp.VENT_X, 0.0, top), cq.Vector(0, 0, -1))
    return stub.cut(bore)


def _along(part, x):
    """Seat a fitting on the flow axis: its own X origin to `x`, its axis onto the
    ASSE 1022's (y = 0, z = the body-centre height)."""
    return part.translate((x, 0.0, bfp.BODY_CENTER_Z))


def build():
    assy = cq.Assembly(name="asse1022-assembly")
    assy.add(_along(ptc.build(), PTC_X), name="jg-pp010822e", color=BLACK_PP)
    assy.add(_along(coupling.build(), COUPLING_X), name="gagira-coupling", color=STAINLESS)
    assy.add(bfp.build(), name="multiplex-asse1022", color=BRASS)
    assy.add(_along(barb.build(), BARB_X), name="ffl38barb38", color=STAINLESS)
    assy.add(vent_stub(), name="vent-stub", color=CLEAR_PVC)
    return assy


def tube_in():
    """The 1/4" PTC mouth the cabinet's water run pushes into: (position, outward
    axis) — the assembly's upstream terminal, off the PP010822E's own port."""
    pos, axis = ptc.tube_port()
    return (pos[0] + PTC_X, pos[1], pos[2] + bfp.BODY_CENTER_Z), axis


def hose_out():
    """The 3/8" barb tip the silicone hose to the SeaFlo suction slips over:
    (position, outward axis) — the assembly's downstream terminal."""
    pos, axis = barb.barb_tip()
    return (pos[0] + BARB_X, pos[1], pos[2] + bfp.BODY_CENTER_Z), axis


def vent_tip():
    """The vent stub's open end: (position, outward axis). It weeps to atmosphere
    and must hang over the drip pan — not be plumbed into anything."""
    return (bfp.VENT_X, 0.0, -VENT_STUB_REACH), (0.0, 0.0, -1.0)


def main():
    assy = build()
    bb = assy.toCompound().BoundingBox()
    print("ASSE 1022 assembly (Multiplex 19-0897 + upstream/downstream fittings)")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    for label, (pos, axis) in (("tube-in ", tube_in()), ("hose-out", hose_out()),
                               ("vent-tip", vent_tip())):
        print(f"  {label}: ({pos[0]:7.2f}, {pos[1]:6.2f}, {pos[2]:7.2f})  out {axis}")
    out = _here.parent / "asse1022-assembly.step"
    export_assembly(assy, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
