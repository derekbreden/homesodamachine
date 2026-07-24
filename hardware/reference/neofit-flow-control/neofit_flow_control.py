"""neoFit ABCVU44 flow-control bulkhead, 1/4" tube — the flow regulator on the
flavor tap. It sits between the water split's flavor run and V-A, throttling the
clean-water feed down to the flavor manifold's low (<10 PSI) working pressure
([`fluid-topology.md`](/hardware/topology/fluid-topology.md) tube segments 1 + 2).

A tee in form: two 1/4" PTC collets in line carrying the water, and a needle
stem standing perpendicular off the body — a brass bulkhead nut, a threaded
barrel and a knurled slotted head. The needle throttles the run; the barrel is
what a panel would clamp. Acetal body, EPDM O-rings, NSF 51 + 61.

External envelope only — the needle, the seat and the O-rings are not modeled.

  PROVISIONAL: the neoFit catalogue lists the flow-control valves by part number
and pack quantity without a dimensioned drawing, so this envelope is scaled off
the manufacturer's product photograph against the one dimension it shares with
the rest of the pack — the 1/4" PTC collet OD. Reconcile against a measured
ABCVU44 as parts come in hand (same note as reference/water-split).

Frame: +X = flow (inlet at −X, outlet at +X), the needle stem standing along +Z
so a hand reaches it from above. Body centre at the origin, both collet faces on
the Z = 0 plane — placed by a pure translation in the enclosure.

Run:
    tools/cad-venv/bin/python hardware/reference/neofit-flow-control/neofit_flow_control.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

COLLET_D = 13.7      # 1/4" PTC collet OD — the pack's shared 1/4" PTC dimension
REACH = 23.0         # collet face from the body centre; run length is twice this
TUBE_D = 6.35        # 1/4" OD LLDPE both ports accept
HUB = 14.0           # central body

NUT_ACROSS_CORNERS = 17.0   # brass bulkhead nut on the stem
NUT_LENGTH = 6.0
BARREL_D, BARREL_LENGTH = 12.0, 9.0     # threaded barrel the panel clamps
KNURL_D, KNURL_LENGTH = 10.0, 12.0      # knurled slotted adjuster head
STEM_REACH = HUB / 2.0 + NUT_LENGTH + BARREL_LENGTH + KNURL_LENGTH


def inlet():
    """The PTC collet the tap-water line from the split's flavor run pushes into:
    (position, outward axis)."""
    return (-REACH, 0.0, 0.0), (-1.0, 0.0, 0.0)


def outlet():
    """The PTC collet feeding V-A's inlet: (position, outward axis)."""
    return (REACH, 0.0, 0.0), (1.0, 0.0, 0.0)


def adjuster():
    """The tip of the knurled adjuster head — the face a screwdriver reaches:
    (position, outward axis). Not a port; the service reach the pack holds open."""
    return (0.0, 0.0, STEM_REACH), (0.0, 0.0, 1.0)


def build():
    """Run collets along ±X meeting at a central hub, the needle stem standing
    off it along +Z: bulkhead nut, threaded barrel, knurled adjuster head."""
    run = cq.Solid.makeCylinder(
        COLLET_D / 2.0, 2 * REACH, cq.Vector(-REACH, 0, 0), cq.Vector(1, 0, 0))
    hub = cq.Workplane("XY").box(HUB, HUB, HUB).val()
    part = run.fuse(hub)
    z = HUB / 2.0
    nut = (
        cq.Workplane("XY")
        .workplane(offset=z)
        .polygon(6, NUT_ACROSS_CORNERS)
        .extrude(NUT_LENGTH)
        .val()
    )
    z += NUT_LENGTH
    barrel = cq.Solid.makeCylinder(
        BARREL_D / 2.0, BARREL_LENGTH, cq.Vector(0, 0, z), cq.Vector(0, 0, 1))
    z += BARREL_LENGTH
    knurl = cq.Solid.makeCylinder(
        KNURL_D / 2.0, KNURL_LENGTH, cq.Vector(0, 0, z), cq.Vector(0, 0, 1))
    return part.fuse(nut).fuse(barrel).fuse(knurl)


def main():
    part = build()
    bb = part.BoundingBox()
    print("neoFit ABCVU44 flow-control bulkhead, 1/4\" tube — the flavor tap's regulator")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  run {2 * REACH:g} mm collet face to collet face; stem reach {STEM_REACH:g} mm")
    for label, (pos, axis) in (("inlet   ", inlet()), ("outlet  ", outlet()),
                               ("adjuster", adjuster())):
        print(f"  {label}: ({pos[0]:7.2f}, {pos[1]:6.2f}, {pos[2]:7.2f})  out {axis}")
    out = _here.parent / "neofit-flow-control.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
