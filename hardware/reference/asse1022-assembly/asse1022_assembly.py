"""ASSE 1022 assembly: the Multiplex 19-0897 backflow preventer with everything
that threads or clamps directly onto it.

The water path's one non-negotiable component and the fittings that make it
reachable from 1/4" tube on both sides — the chain
[`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) step 2 builds,
in the order it builds them:

    1/4" LLDPE → PP010822E → GAGIRA coupling → [ASSE 1022] → flare38-14ptc → 1/4" LLDPE
                                                     └ vent stub ↓ drip pan

The outlet leaves at 1/4" OD — the flare38-14ptc turns the ASSE's 3/8" male flare
straight onto 1/4" LLDPE, so no 3/8" tubing runs on toward the pump; the 1/4" line
carries the split (V-K + V-A) and only steps back up to 3/8" at the SeaFlo barbs.

Every station is read off the part upstream of it: each fitting's own module says
how deep its threads go, and this file stacks those reaches along the flow axis.
Move a length in any reference module and the chain closes on the new one.

The vent is the assembly's reason for a pose rather than a bare envelope: it weeps
to atmosphere, and that drip is the mechanical telltale for a cross-contamination
event ([`future.md`](/hardware/future.md) "Backflow vent monitoring"). The drip
leaves the stub's tip and falls from there — the tip is the datum the drip pan and
its moisture plate sit under.

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
    _hw / "reference" / "flare38-14ptc",
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly
import flare38_14ptc as oadapt
import gagira_reducing_coupling as coupling
import jg_pp010822e as ptc
import multiplex_asse1022 as bfp

# The viewer draws thumbnails in x-ray: a body is carried by its edges, in its own
# color, against a #1a1a2e ground. Each fitting holds 3:1 or better on that ground and
# a hue the chain uses once, so it reads as its own body beside the one it butts onto.
BRASS = cq.Color(0.72, 0.58, 0.28)        # the Multiplex body — 5.98:1
STAINLESS = cq.Color(0.72, 0.74, 0.78)    # 304 SS — the barb stem, 9.05:1
COUPLING_SS = cq.Color(0.25, 0.78, 0.72)  # the 316L coupling, flat to the body's — 8.19:1
BLACK_PP = cq.Color(0.42, 0.44, 0.48)     # John Guest polypropylene — 3.43:1
CLEAR_PVC = cq.Color(0.85, 0.90, 0.92, 0.45)

# The vent stub: Sealproof 1/4" ID × 3/8" OD clear PVC, bored to the barb it slips
# over so the barb occupies the hose rather than its wall. It covers the barb to the
# body's underside and overhangs the barb tip by the reach — the length the bench
# cuts (~12" of stock, trimmed). The enclosure lays this body along −Y across the
# service bay's aft strip, so the overhang is the room the strip leaves between the
# electronics shelf's back edge and the chain, and the drip falls off the tip onto
# the foam-cap top, which is the pan's ground.
VENT_STUB_OD = 9.53
VENT_STUB_REACH = 2.0           # past the barb tip, along the vent axis

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
OUTLET_X = BARREL_DOWNSTREAM


def vent_stub():
    """The clear-PVC telltale stub, slipped over the vent barb and running down
    past its tip. Bored at the barb Ø, so the two share a surface and no metal."""
    top = bfp.BODY_UNDERSIDE_Z              # the body's underside, where the hose stops
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
    assy.add(_along(coupling.build(), COUPLING_X), name="gagira-coupling", color=COUPLING_SS)
    assy.add(bfp.build(), name="multiplex-asse1022", color=BRASS)
    assy.add(_along(oadapt.build(), OUTLET_X), name="flare38-14ptc", color=STAINLESS)
    assy.add(vent_stub(), name="vent-stub", color=CLEAR_PVC)
    return assy


def tube_in():
    """The 1/4" PTC mouth the cabinet's water run pushes into: (position, outward
    axis) — the assembly's upstream terminal, off the PP010822E's own port."""
    pos, axis = ptc.tube_port()
    return (pos[0] + PTC_X, pos[1], pos[2] + bfp.BODY_CENTER_Z), axis


def tube_out():
    """The 1/4" PTC mouth the LLDPE run to the split pushes into: (position,
    outward axis) — the assembly's downstream terminal, off the flare38-14ptc."""
    pos, axis = oadapt.tube_port()
    return (pos[0] + OUTLET_X, pos[1], pos[2] + bfp.BODY_CENTER_Z), axis


def vent_tip():
    """The vent stub's open end: (position, outward axis). It weeps to atmosphere —
    the drip falls from here into the pan, and nothing plumbs into it."""
    return (bfp.VENT_X, 0.0, -VENT_STUB_REACH), (0.0, 0.0, -1.0)


def main():
    assy = build()
    bb = assy.toCompound().BoundingBox()
    print("ASSE 1022 assembly (Multiplex 19-0897 + upstream/downstream fittings)")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    for label, (pos, axis) in (("tube-in ", tube_in()), ("tube-out", tube_out()),
                               ("vent-tip", vent_tip())):
        print(f"  {label}: ({pos[0]:7.2f}, {pos[1]:6.2f}, {pos[2]:7.2f})  out {axis}")
    out = _here.parent / "asse1022-assembly.step"
    export_assembly(assy, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
