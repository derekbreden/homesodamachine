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

A station is its module, its seat and its hue. The seat carries the fitting's metal and
the ports that fitting's module declares ([`_seating.py`](/hardware/scripts/_seating.py)).
This assembly's own terminals are its stations' ports, named.

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
from types import SimpleNamespace

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


def _stub_tip():
    """The stub's open end: (position, outward axis). It weeps to atmosphere — the drip
    falls from here into the pan, and nothing plumbs into it."""
    return (bfp.VENT_X, 0.0, -VENT_STUB_REACH), (0.0, 0.0, -1.0)


# The stub is drawn here rather than imported, in the chain's own frame, bored onto the
# ASSE's vent barb. It answers `build` and a port the way the reference modules do.
_stub = SimpleNamespace(build=vent_stub, tip=_stub_tip)


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
    "jg-pp010822e":       (ptc,      _along(PTC_X),      BLACK_PP),
    "gagira-coupling":    (coupling, _along(COUPLING_X), COUPLING_SS),
    "multiplex-asse1022": (bfp,      Seat(),             BRASS),
    "flare38-14ptc":      (oadapt,   _along(OUTLET_X),   STAINLESS),
    "vent-stub":          (_stub,    Seat(),             CLEAR_PVC),
}

# This assembly's boundary: the two mouths the cabinet plumbs to, and the one it catches
# under. Each names the station port it is.
TERMINALS = {
    "tube-in":  ("jg-pp010822e", "tube_port"),
    "tube-out": ("flare38-14ptc", "tube_port"),
    "vent-tip": ("vent-stub", "tip"),
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
                  expected_counts={k: 1 for k in marks})

    out = _here.parent / "asse1022-assembly.step"
    export_assembly(assy, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
