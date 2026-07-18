"""Drip pan — the printed catch basin on the compressor top, under the Multiplex
atmospheric-vent barb. The Shutao moisture probe lies flat in it; any vent drip,
condensate, or overflow pools in the basin and wets the probe, tripping the
moisture alarm. Watertight (no drain) — the basin is emptied on service.

Open-top rounded-corner basin: 130 × 66 outer × 22 tall, 2.5 mm walls on a 3 mm
floor, with the inner corners and the floor-to-wall junction filleted. No mount
features; the pan rests on the compressor top.

Frame: +X long axis, +Y depth, +Z up; origin at the lower-front-left outer
corner. Open top (+Z).

Run:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/drip-pan/drip_pan.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

PAN_X, PAN_Y, PAN_Z = 130.0, 66.0, 22.0
WALL, FLOOR = 2.5, 3.0
CORNER_R = 6.0        # outer vertical-corner radius
FLOOR_COVE = 3.0      # inner floor-to-wall fillet (water sheeting + cleanability)


def build():
    """Rounded-corner open basin: outer shell minus a filleted inner cavity."""
    outer = (
        cq.Workplane("XY")
        .box(PAN_X, PAN_Y, PAN_Z, centered=(False, False, False))
        .edges("|Z").fillet(CORNER_R)
    )
    # Inner cavity: rounded vertical corners + a filleted bottom, so subtracting
    # it leaves a floor-to-wall cove. Sits on the FLOOR-thick base, open at top.
    cavity = (
        cq.Workplane("XY")
        .box(PAN_X - 2 * WALL, PAN_Y - 2 * WALL, PAN_Z, centered=(False, False, False))
        .edges("|Z").fillet(max(CORNER_R - WALL, 1.5))
        .edges("<Z").fillet(FLOOR_COVE)
        .translate((WALL, WALL, FLOOR))
    )
    return outer.cut(cavity)


def main():
    pan = build()
    bb = pan.val().BoundingBox()
    print("Drip pan — printed catch basin")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  {PAN_X}×{PAN_Y}×{PAN_Z} outer, {WALL} wall, {FLOOR} floor, "
          f"r{CORNER_R} corners, r{FLOOR_COVE} floor cove")
    out = _here.parent / "drip-pan.step"
    export_step(pan, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
