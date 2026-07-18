"""Interstate Pneumatics WR1110 fixed 90 PSI secondary regulator — the
appliance's `wr1110` on the CO2 inlet chain (DERPIPE → GASHER → WR1110, running
+Y). A "Mini Body Series" fixed preset: no adjustment knob, just two wrench
hexes and a flush vent hole.

External envelope only — a round regulator body between two hex wrench
sections, flow axis along +Y. The internal diaphragm + spring is not modeled;
the flush vent hole doesn't break the envelope, so it isn't cut. Ø21 across the
hex corners × 57 mm off the small-body item (the old 1.31"/3.19" figures were
the package; ~45 g confirms the mini body). The hex sections inscribe the old
Ø21 placeholder cylinder, so the real shape is no larger than the box it
replaces.

Frame: +Y = flow axis (matches the enclosure placement, _cyl(..., (0, 1, 0)));
centered on X/Z. +Z up.

Run:
    tools/cad-venv/bin/python hardware/reference/wr1110-regulator/wr1110_regulator.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

HEX_ACROSS_CORNERS = 21.0   # inscribes the old Ø21 placeholder cylinder
TOTAL_LENGTH = 57.0         # along the flow axis
BODY_D = 19.0               # round regulator body between the hexes
HEX_LENGTH = 15.0           # each wrench hex section
BODY_LENGTH = TOTAL_LENGTH - 2 * HEX_LENGTH   # 27 mm round body


def build():
    """Two hex wrench sections with a round body between, flow axis along +Y."""
    # Build along +Z, then reorient +Z -> +Y.
    inlet_hex = cq.Workplane("XY").polygon(6, HEX_ACROSS_CORNERS).extrude(HEX_LENGTH)
    body = (
        cq.Workplane("XY")
        .workplane(offset=HEX_LENGTH)
        .circle(BODY_D / 2.0)
        .extrude(BODY_LENGTH)
    )
    outlet_hex = (
        cq.Workplane("XY")
        .workplane(offset=HEX_LENGTH + BODY_LENGTH)
        .polygon(6, HEX_ACROSS_CORNERS)
        .extrude(HEX_LENGTH)
    )
    part = inlet_hex.union(body).union(outlet_hex)
    return part.rotate((0, 0, 0), (1, 0, 0), -90.0)


def main():
    part = build()
    bb = part.val().BoundingBox()
    print("Interstate Pneumatics WR1110 secondary regulator")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Hex: {HEX_ACROSS_CORNERS} across corners × {HEX_LENGTH:g} mm each; "
          f"body Ø{BODY_D} × {BODY_LENGTH:g} mm; total {TOTAL_LENGTH:g} mm")
    out = _here.parent / "wr1110-regulator.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
