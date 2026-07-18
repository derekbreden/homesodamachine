"""Multiplex 19-0897 ASSE 1022 dual-check backflow preventer (= Anderson Brass
ABF-1) — the appliance's `multiplex` in the enclosure pack, inline on the water
path over the drip pan, its atmospheric-vent barb pointing down into the pan.

External envelope only. A brass hex barrel along the flow axis with a radial
atmospheric-vent barb; the internal dual-check + vent mechanism and the threaded
ends are not modeled. Dimensions off the Welbilt spec sheet 5030A: 2.55" long,
Ø33 across the hex corners (1.12" across flats).

Frame: +X = flow axis; the vent barb runs down to Z = 0 (its tip, the bbox
floor, seats toward the pan); body centered on Y. +Z up.

Run:
    tools/cad-venv/bin/python hardware/reference/multiplex-asse1022/multiplex_asse1022.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

HEX_ACROSS_CORNERS = 33.0   # hex circumdiameter (28.6 across flats)
BODY_LENGTH = 65.0          # along the flow axis (2.55")
VENT_D = 8.0                # atmospheric-vent barb Ø
VENT_DROP = 10.5            # barb reach below the body bottom, to the pan
VENT_INTO_BODY = 5.0        # extra barb length fused up into the body


def build():
    """Hex body along +X, raised on a downward atmospheric-vent barb whose tip
    sits at Z = 0 (the bbox floor)."""
    body_center_z = VENT_DROP + HEX_ACROSS_CORNERS / 2.0
    # Hex prism along +X (YZ plane, normal +X); a flat faces down so the vent
    # exits a face, not a corner.
    body = (
        cq.Workplane("YZ")
        .polygon(6, HEX_ACROSS_CORNERS)
        .extrude(BODY_LENGTH)
        .val()
        .translate((0, 0, body_center_z))            # flats face ±Z (vent exits the bottom flat)
    )
    vent = cq.Solid.makeCylinder(
        VENT_D / 2.0, VENT_DROP + VENT_INTO_BODY,
        cq.Vector(BODY_LENGTH / 2.0, 0, 0), cq.Vector(0, 0, 1),
    )
    return body.fuse(vent)


def main():
    part = build()
    bb = part.BoundingBox()
    print("Multiplex 19-0897 ASSE 1022 backflow preventer")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Hex: {HEX_ACROSS_CORNERS} across corners × {BODY_LENGTH:g} mm; "
          f"vent Ø{VENT_D} dropping {VENT_DROP:g} mm to the pan")
    out = _here.parent / "multiplex-asse1022.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
