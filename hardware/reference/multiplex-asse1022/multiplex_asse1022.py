"""Multiplex 19-0897 ASSE 1022 dual-check backflow preventer (= Anderson Brass
ABF-1) — the appliance's `multiplex` in the enclosure pack, inline on the water
path above the drip pan, its atmospheric-vent barb weeping into it.

External envelope only. A brass hex barrel along the flow axis with a radial
atmospheric-vent barb, a 3/8" NPT male inlet at one end and a 3/8" SAE 45° male
flare outlet at the other; the internal dual-check + vent mechanism is not
modeled and the threads are plain cylinders at their nominal majors, no helix.
Overall length off the Welbilt spec sheet 5030A: 2.55", Ø33 across the hex
corners (1.12" across flats). The ends divide that length — the barrel is what
is left between them.

Flow runs inlet → outlet: the arrow points away from the customer side, so the
GAGIRA reducing coupling lands on the NPT inlet and the FFL38BARB38 swivel nut
on the flare outlet ([`asse1022-assembly`](../asse1022-assembly/)).

Frame: +X = flow axis, inlet at X = 0; the vent barb runs down to Z = 0, its tip
on the bbox floor; body centered on Y. +Z up.

Run:
    tools/cad-venv/bin/python hardware/reference/multiplex-asse1022/multiplex_asse1022.py
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

HEX_ACROSS_CORNERS = 33.0   # hex circumdiameter (28.6 across flats)
TOTAL_LENGTH = 65.0         # along the flow axis, end to end (2.55")
INLET_THREAD_D = 17.15      # 3/8" NPT major Ø (0.675", simplified, no helix)
INLET_LENGTH = 13.0         # 3/8" NPT male engagement
FLARE_THREAD_D = 15.88      # 3/8" SAE 45° flare thread major Ø (5/8"-18 UNF)
FLARE_LENGTH = 14.0         # male flare nose + thread
BARREL_LENGTH = TOTAL_LENGTH - INLET_LENGTH - FLARE_LENGTH
VENT_D = 8.0                # atmospheric-vent barb Ø
VENT_DROP = 10.5            # the two together are the barb's length from its tip, split
VENT_INTO_BODY = 5.0        # at the hex's circumradius rather than at its underside

BODY_CENTER_Z = VENT_DROP + HEX_ACROSS_CORNERS / 2.0    # flow axis height off the bbox floor
# The hex is clocked flats-down (`build()`), so its half-height off the flow axis is the
# apothem, not the circumradius. The underside is where the vent barb leaves the body —
# the datum a stub slipped over that barb stops against, and the top of its exposed reach.
HEX_ACROSS_FLATS = HEX_ACROSS_CORNERS * math.sqrt(3) / 2.0
BODY_UNDERSIDE_Z = BODY_CENTER_Z - HEX_ACROSS_FLATS / 2.0
VENT_X = INLET_LENGTH + BARREL_LENGTH / 2.0             # vent barb on the barrel's midpoint


def inlet():
    """The 3/8" NPT male inlet face: (position, outward axis). What the GAGIRA
    reducing coupling threads onto."""
    return (0.0, 0.0, BODY_CENTER_Z), (-1.0, 0.0, 0.0)


def outlet():
    """The 3/8" SAE 45° male flare outlet face: (position, outward axis). What the
    FFL38BARB38 swivel nut seats against."""
    return (TOTAL_LENGTH, 0.0, BODY_CENTER_Z), (1.0, 0.0, 0.0)


def vent():
    """The atmospheric-vent barb tip: (position, outward axis). The vent stub
    slips on here, and the drip leaves its far end."""
    return (VENT_X, 0.0, 0.0), (0.0, 0.0, -1.0)


def build():
    """NPT inlet stub → hex barrel → male flare outlet along +X, the barrel
    raised on a downward atmospheric-vent barb whose tip sits at Z = 0."""
    # Hex prism along +X (YZ plane, normal +X); a flat faces down so the vent
    # exits a face, not a corner.
    body = (
        cq.Workplane("YZ")
        .polygon(6, HEX_ACROSS_CORNERS)
        .extrude(BARREL_LENGTH)
        .val()
        .translate((INLET_LENGTH, 0, BODY_CENTER_Z))   # flats face ±Z (vent exits the bottom flat)
    )
    inlet_stub = cq.Solid.makeCylinder(
        INLET_THREAD_D / 2.0, INLET_LENGTH,
        cq.Vector(0, 0, BODY_CENTER_Z), cq.Vector(1, 0, 0),
    )
    outlet_stub = cq.Solid.makeCylinder(
        FLARE_THREAD_D / 2.0, FLARE_LENGTH,
        cq.Vector(INLET_LENGTH + BARREL_LENGTH, 0, BODY_CENTER_Z), cq.Vector(1, 0, 0),
    )
    vent_barb = cq.Solid.makeCylinder(
        VENT_D / 2.0, VENT_DROP + VENT_INTO_BODY,
        cq.Vector(VENT_X, 0, 0), cq.Vector(0, 0, 1),
    )
    return body.fuse(inlet_stub).fuse(outlet_stub).fuse(vent_barb)


def main():
    part = build()
    bb = part.BoundingBox()
    print("Multiplex 19-0897 ASSE 1022 backflow preventer")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Hex: {HEX_ACROSS_CORNERS} across corners × {BARREL_LENGTH:g} mm barrel; "
          f"3/8\" NPT Ø{INLET_THREAD_D} × {INLET_LENGTH:g} in, "
          f"3/8\" flare Ø{FLARE_THREAD_D} × {FLARE_LENGTH:g} out")
    print(f"  Vent Ø{VENT_D} at x={VENT_X:g}, reaching {BODY_UNDERSIDE_Z:.2f} mm below "
          f"the body's underside to the pan")
    out = _here.parent / "multiplex-asse1022.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
