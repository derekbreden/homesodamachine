"""ASSE 1022 assembly: the Multiplex 19-0897 backflow preventer with everything
that threads or clamps directly onto it.

The water path's one non-negotiable component and the fittings that make it
reachable from 1/4" tube on both sides — the chain
[`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) step 2 builds,
in the order it builds them:

    1/4" LLDPE → PP010822E → GAGIRA coupling → [ASSE 1022] → flare38-14ptc → 1/4" LLDPE
                                                     └ TPU sleeve ↓ 4 mm OVER → faucet bowl

The outlet leaves at 1/4" OD — the flare38-14ptc turns the ASSE's 3/8" male flare
straight onto 1/4" LLDPE, so no 3/8" tubing runs on toward the pump; the 1/4" line
carries the split (V-K + V-A) and only steps back up to 3/8" at the SeaFlo barbs.

Every station is read off the part upstream of it: each fitting's own module says
how deep its threads go, and this file stacks those reaches along the flow axis.
Move a length in any reference module and the chain closes on the new one.

A station is its module, its seat and its hue. The seat carries the fitting's metal and
the ports that fitting's module declares ([`_seating.py`](/hardware/scripts/_seating.py)).
This assembly's own terminals are its stations' ports, named.

The TPU sleeve covers the barb and connects directly to the 4 mm OVER return,
bulkhead and the separate faucet outlet over the bowl
([`asse-drain.md`](/hardware/assembly/asse-drain.md)).

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
sys.path.insert(0, str(next(p for p in _here.parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_assembly
from _seating import Seat
from docgen import substitute_md
import flare38_14ptc as oadapt
import gagira_reducing_coupling as coupling
import jg_pp010822e as ptc
import multiplex_asse1022 as bfp

# EACH FITTING IS THE COLOUR OF ITS OWN STOCK, off `_materials` — the same constant its own
# generator next door bakes into its own STEP, so a body in this chain and the picture of that
# body alone are one colour. Two of the five are the same metal and are drawn the same metal:
# what tells the GAGIRA coupling from the barrel it swallows is the step between their hexes,
# which is what tells them apart on the bench.
from _materials import (M_BRASS, M_JG_BLACK_PP, M_JG_GREY_ACETAL,  # noqa: E402
                        M_STAINLESS)

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


def _along(x) -> Seat:
    """The seat a fitting takes on the flow axis: its own X origin at `x`, its axis onto
    the ASSE 1022's (y = 0, z = the body-centre height)."""
    return Seat.shift((x, 0.0, bfp.BODY_CENTER_Z))


def flow_axis() -> tuple:
    """The line every station on this chain stands on, in the assembly's own frame:
    `(position, axis)` — the ASSE 1022's inlet plane on it, and the direction the water
    runs. `_along` seats each fitting onto this line, and the cabinet that holds the chain
    over a drain seats the whole assembly by it."""
    return (0.0, 0.0, bfp.BODY_CENTER_Z), (1.0, 0.0, 0.0)


# The chain, in the order the water meets it: what draws each station, the seat it takes,
# and its hue. The ASSE 1022 is the frame the other four are seated in.
STATIONS = {
    "jg-pp010822e":       (ptc,      _along(PTC_X),      M_JG_BLACK_PP),
    "gagira-coupling":    (coupling, _along(COUPLING_X), M_STAINLESS),
    "multiplex-asse1022": (bfp,      Seat(),             M_BRASS),
    "flare38-14ptc":      (oadapt,   _along(OUTLET_X),   M_JG_GREY_ACETAL),
}

# This assembly's boundary: the two mouths the cabinet plumbs to, and the one it catches
# under. Each names the station port it is.
TERMINALS = {
    "tube-in":  ("jg-pp010822e", "tube_port"),
    "tube-out": ("flare38-14ptc", "tube_port"),
    "vent-tip": ("multiplex-asse1022", "vent"),
}


def build():
    """The chain, each station at its seat."""
    assy = cq.Assembly(name="asse1022-assembly")
    for name, (part, seat, color) in STATIONS.items():
        assy.add(seat.solid(part.build()), name=name, color=color)
    return assy


def port(name: str) -> tuple:
    """One terminal in this assembly's own frame: `(position, outward axis)`.

    The station's module owns the station; the station's seat carries it here."""
    if name not in TERMINALS:
        raise KeyError(f"no terminal {name!r} (have: {', '.join(TERMINALS)})")
    station, local = TERMINALS[name]
    part, seat, _color = STATIONS[station]
    return seat.port(getattr(part, local)())


def ports() -> dict:
    """Every terminal, in the order the water meets them."""
    return {name: port(name) for name in TERMINALS}


def main():
    assy = build()
    bb = assy.toCompound().BoundingBox()
    stations = ports()
    print("ASSE 1022 assembly (Multiplex 19-0897 + upstream/downstream fittings)")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    for label, (pos, axis) in stations.items():
        print(f"  {label:8}: ({pos[0]:7.2f}, {pos[1]:6.2f}, {pos[2]:7.2f})  out {axis}")

    marks = {f"ASSE_{n.replace('-', '_').upper()}":
             "({:.2f}, {:.2f}, {:.2f})".format(*stations[n][0]) for n in TERMINALS}
    marks["ASSE_ENVELOPE"] = f"{bb.xlen:.1f} × {bb.ylen:.1f} × {bb.zlen:.1f} mm"
    substitute_md(_here.parent / "README.md", variables=marks,
)

    out = _here.parent / "asse1022-assembly.step"
    export_assembly(assy, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
