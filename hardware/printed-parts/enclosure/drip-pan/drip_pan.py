"""Drip pan — the printed catch basin on the cold core's foam-cap top, under the
Multiplex atmospheric-vent stub. The Shutao moisture plate lies flat in it; any
vent drip, condensate, or overflow pools in the basin and wets the plate,
tripping the moisture alarm. Watertight (no drain) — the basin is emptied on
service.

Two printed parts:

  * the BASIN — an open-top rounded-corner box, 100 x 30 outer x 22 tall,
    2.5 mm walls on a 3 mm floor, floor-to-wall coved. It is 100 long so the
    moisture plate lies flat down its length, and only 30 deep because the
    service bay's aft strip is 55 mm wide between the SeaFlo's back face and
    the rear wall and the basin has to keep a clearance to each.
  * the CRADLE — a floorless fence, one closed rounded loop of 3 mm rail
    standing 7 mm off the deck, taped to the foam-cap top with VHB. The basin
    drops through it onto the cap, so the pan still lands on the cap the way
    the assembly says it does, and the fence takes it in X and Y. Lift the
    basin 7 mm clear of the rail and it draws west along the deck, out from
    under the ASSE chain.

Frame: +X long axis, +Y depth, +Z up; origin at the basin's lower-front-left
outer corner, and `cradle_offset()` carries that origin to the cradle's. Open
top (+Z).

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

PAN_X, PAN_Y, PAN_Z = 100.0, 30.0, 22.0
WALL, FLOOR = 2.5, 3.0
CORNER_R = 6.0        # outer vertical-corner radius
FLOOR_COVE = 3.0      # inner floor-to-wall fillet (water sheeting + cleanability)

# The fence around the basin's foot. The rail stands clear of the basin by a slip
# fit on every side, so the basin drops in and lifts out by hand; the rail is
# shorter than the free lift the ASSE overhead leaves, which is what lets the
# basin come up off it and draw west.
CRADLE_FIT = 0.2      # per side, basin-to-rail
CRADLE_RAIL = 3.0     # rail wall thickness
CRADLE_H = 7.0        # rail height off the deck
CRADLE_TAPE = 1.1     # 3M VHB 4941 between the rail's underside and the foam cap


def _rounded_prism(x, y, z, r):
    return (
        cq.Workplane("XY")
        .box(x, y, z, centered=(False, False, False))
        .edges("|Z").fillet(r)
    )


def build():
    """Rounded-corner open basin: outer shell minus a filleted inner cavity."""
    outer = _rounded_prism(PAN_X, PAN_Y, PAN_Z, CORNER_R)
    # Inner cavity: rounded vertical corners + a filleted bottom, so subtracting
    # it leaves a floor-to-wall cove. Sits on the FLOOR-thick base, open at top.
    cavity = (
        _rounded_prism(PAN_X - 2 * WALL, PAN_Y - 2 * WALL, PAN_Z, max(CORNER_R - WALL, 1.5))
        .edges("<Z").fillet(FLOOR_COVE)
        .translate((WALL, WALL, FLOOR))
    )
    return outer.cut(cavity)


def cradle_offset():
    """Basin origin to cradle origin — the rail's own thickness plus its slip fit,
    out on −X and −Y. The enclosure places the basin; the cradle follows it."""
    return (-(CRADLE_FIT + CRADLE_RAIL), -(CRADLE_FIT + CRADLE_RAIL), 0.0)


def build_cradle():
    """The fence: a closed rail loop with no floor, so the basin seats on the cap
    through it. Bonded to the foam-cap top; the basin is not bonded to anything."""
    opening_x = PAN_X + 2 * CRADLE_FIT
    opening_y = PAN_Y + 2 * CRADLE_FIT
    outer = _rounded_prism(
        opening_x + 2 * CRADLE_RAIL, opening_y + 2 * CRADLE_RAIL, CRADLE_H,
        CORNER_R + CRADLE_FIT + CRADLE_RAIL)
    opening = _rounded_prism(
        opening_x, opening_y, CRADLE_H, CORNER_R + CRADLE_FIT
    ).translate((CRADLE_RAIL, CRADLE_RAIL, 0.0))
    return outer.cut(opening)


def capacity_ml():
    """The basin holds this before it overflows the rim — no drain, emptied on
    service, so it is the interval the vent's weep buys."""
    return (PAN_X - 2 * WALL) * (PAN_Y - 2 * WALL) * (PAN_Z - FLOOR) / 1000.0


def main():
    pan = build()
    cradle = build_cradle()
    bb = pan.val().BoundingBox()
    cb = cradle.val().BoundingBox()
    print("Drip pan — printed catch basin + cradle")
    print(f"  Basin bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  {PAN_X}x{PAN_Y}x{PAN_Z} outer, {WALL} wall, {FLOOR} floor, "
          f"r{CORNER_R} corners, r{FLOOR_COVE} floor cove, {capacity_ml():.1f} mL to the rim")
    ox, oy, _ = cradle_offset()
    print(f"  Cradle bounding box: X [{cb.xmin:.2f}, {cb.xmax:.2f}]  "
          f"Y [{cb.ymin:.2f}, {cb.ymax:.2f}]  Z [{cb.zmin:.2f}, {cb.zmax:.2f}]  "
          f"at ({ox:+.1f}, {oy:+.1f}) off the basin origin")
    print(f"  {CRADLE_RAIL} rail x {CRADLE_H} tall on {CRADLE_TAPE} VHB, "
          f"{CRADLE_FIT} slip per side")
    for shape, name in ((pan, "drip-pan.step"), (cradle, "drip-pan-cradle.step")):
        out = _here.parent / name
        export_step(shape, str(out))
        print(f"-> {out.name}")


if __name__ == "__main__":
    main()
