"""Drip pan — the printed catch basin under the Multiplex atmospheric-vent stub.
The Shutao moisture plate lies flat in it; any vent drip, condensate, or overflow
pools in the basin and wets the plate, tripping the moisture alarm. Watertight
(no drain) — the basin is emptied on service.

One printed part: the BASIN — an open-top rounded-corner box, [53](PAN_LEN) x
[76](PAN_DEPTH) outer x [10](PAN_HEIGHT) tall, [2.5](PAN_WALL) mm walls on a
[3](PAN_FLOOR) mm floor, floor-to-wall coved.

The column reads down from the chain: `VENT_GAP` of air under its underside, then
the basin, and under the basin nothing but the air it needs over the SeaFlo's
crown. `_contents.drip_pan_seat` is the plane the basin's own floor reaches.

WHAT CARRIES IT IS OPEN, AND THE OPEN QUESTION HAS A SHAPE. The basin stands over
the casting, so anything under its floor is height the basin pays for twice —
once to clear the pump and again to carry the load. So the carry belongs on the
basin's OWN FLANGE, the way a baking tray's rim is what its oven rack holds:
`FLANGE_W` grows off the wall at a plane up the basin's height, rails stand
outboard of the basin at that plane, and the basin hangs between them with its
floor free to sit at its own clearance over the crown. Nothing under the floor,
so nothing under the floor to pay for.

Frame: +X long axis, +Y depth (the withdrawal direction), +Z up; origin at the
basin's lower-front-left outer corner of the WALLS. Open top (+Z).

Run:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/drip-pan/drip_pan.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(next(p for p in _here.parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_step
from docgen import substitute_md, substitute_py_comments

# The basin is narrow across the strip and deep down it. X is the loft's
# contested axis — east of the basin the west column's crossing ladder climbs
# rung over rung (`enclosure-assembly/_lines`), and the basin's east rim is that
# ladder's lid: every millimetre the basin gives back in X is
# ceiling a rung buys radius from. Y is the axis with room to spare: the run
# between the SeaFlo's back face and the foam cap's rear edge is deeper than
# the basin needs. So the width is the FLOOR the moisture plate sets and one
# millimetre of grace — the plate turned down the depth wants
# `PLATE_Y + 2·(PLATE_SLIP + WALL + FLOOR_COVE)` = 52 of outer width —
# [53](PAN_LEN) across and [76](PAN_DEPTH) down, the basin hung on the atmospheric vent's own
# tip in both plan axes (`_contents._pan_room` is the reading, and it refuses a tip that stands
# outside the inner floor). [10](PAN_HEIGHT) tall is what `VENT_GAP` leaves of the vent's
# column once the basin's floor has taken its own air over the casting.
PAN_X, PAN_Y, PAN_Z = 53.0, 76.0, 10.0
WALL, FLOOR = 2.5, 3.0
CORNER_R = 6.0        # outer vertical-corner radius
# Floor-to-wall fillet — water sheeting + cleanability. It eats the flat floor from
# both ±Y walls, and the moisture plate's long edge has to land inside what is left.
FLOOR_COVE = 2.0
# The slab's reach past each wall. Zero — the basin carries no flange yet, and
# nothing is under it: it stands free at the plane `_contents.drip_pan_seat`
# gives it, one `LINE_HUG` over the SeaFlo's crown.
#   This is the number the CARRY is waiting on. A flange grown here, at a plane
# up the wall rather than at the floor, is what rails outboard of the basin hold
# — the aft strip's east end belongs to V-K and the umbilical cluster and its
# west end to the board, so what the pair may spend in X is the wall's own
# footprint and the slip, and what it may not spend is anything under the floor.
FLANGE_W = 0.0

# The Shutao LM393 module's conductivity plate (bom.md §sensors, B0B2W76MB1), lying
# flat on the basin floor with its long edge down the basin's Y — the withdrawal
# axis, the one the strip has depth to spare on. The floor's flat area inside the
# coves is what it lands on; `check_plate()` is that check.
PLATE_X, PLATE_Y = 55.25, 41.0
PLATE_SLIP = 1.0      # per side, plate edge to where the cove starts rising

# The least clear air the basin's rim keeps under the ASSE chain's underside —
# which is the vent stub's tip when the chain hangs unrolled, and a body corner
# when it does not, the stub then standing above it.
VENT_GAP = 4.0
# How much more than that a carry may leave, so it can be a round printed number
# under a chain whose underside is a rolled hex corner and irrational.
VENT_GAP_SLACK = 1.0


def _rounded_prism(x, y, z, r):
    return (
        cq.Workplane("XY")
        .box(x, y, z, centered=(False, False, False))
        .edges("|Z").fillet(r)
    )


def flat_floor():
    """The floor's flat area, inside the coves — what the moisture plate lies on."""
    return (PAN_X - 2 * WALL - 2 * FLOOR_COVE, PAN_Y - 2 * WALL - 2 * FLOOR_COVE)


def check_plate():
    """Raises unless the flat floor takes the plate with its slip on every side. The
    plate lies turned — its long edge down the basin's Y — so the width it asks of the
    basin comes out of the axis the strip has to give. A plate wider than the flat
    rides up on the coves instead of lying down, and the water has to stand that much
    deeper before it reads."""
    fx, fy = flat_floor()
    need_x, need_y = PLATE_Y + 2 * PLATE_SLIP, PLATE_X + 2 * PLATE_SLIP
    if fx < need_x or fy < need_y:
        raise ValueError(
            f"drip-pan floor {fx:.2f} x {fy:.2f} flat inside the r{FLOOR_COVE:g} coves; "
            f"the {PLATE_X:g} x {PLATE_Y:g} plate turned down the depth, with "
            f"{PLATE_SLIP:g} slip a side, needs {need_x:.2f} x {need_y:.2f}. Grow PAN_Y, "
            f"shrink FLOOR_COVE, or move the SeaFlo forward — the strip behind it is "
            f"what PAN_Y comes out of.")


def build():
    """Rounded-corner open basin on a flanged floor slab: outer shell minus a
    filleted inner cavity, unioned with the slab that overhangs it on ±X."""
    check_plate()
    outer = _rounded_prism(PAN_X, PAN_Y, PAN_Z, CORNER_R)
    # Inner cavity: rounded vertical corners + a filleted bottom, so subtracting
    # it leaves a floor-to-wall cove. Sits on the FLOOR-thick base, open at top.
    cavity = (
        _rounded_prism(PAN_X - 2 * WALL, PAN_Y - 2 * WALL, PAN_Z, max(CORNER_R - WALL, 1.5))
        .edges("<Z").fillet(FLOOR_COVE)
        .translate((WALL, WALL, FLOOR))
    )
    # The flange the carry is waiting on, at the floor plane where the slab already
    # is. At `FLANGE_W` 0 it reaches nowhere and the basin is the shell alone.
    flange = _rounded_prism(
        PAN_X + 2 * FLANGE_W, PAN_Y, FLOOR, 3.0
    ).translate((-FLANGE_W, 0.0, 0.0))
    return outer.cut(cavity).union(flange)


def capacity_ml():
    """The basin holds this before it overflows the rim — no drain, emptied on
    service, so it is the interval the vent's weep buys."""
    return (PAN_X - 2 * WALL) * (PAN_Y - 2 * WALL) * (PAN_Z - FLOOR) / 1000.0


def main():
    pan = build()
    bb = pan.val().BoundingBox()
    print("Drip pan — printed catch basin")
    print(f"  Basin bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  {PAN_X:g}x{PAN_Y:g}x{PAN_Z:g} outer, {WALL:g} wall, {FLOOR:g} floor, "
          f"r{CORNER_R:g} corners, r{FLOOR_COVE:g} floor cove, {capacity_ml():.1f} mL to the rim")
    fx, fy = flat_floor()
    print(f"  Flat floor {fx:g} x {fy:g} inside the coves — "
          f"plate {PLATE_X:g} x {PLATE_Y:g} with {PLATE_SLIP:g} slip a side")
    print(f"  Flange {FLANGE_W:g} per side — the carry stands on it, and on nothing under "
          f"the floor")
    print(f"  Withdraws +Y: {PAN_Y:g} mm of travel takes it clear")
    for shape, name in ((pan, "drip-pan.step"),):
        out = _here.parent / name
        export_step(shape, str(out))
        print(f"-> {out.name}")

    variables = {
        "PAN_LEN": f"{PAN_X:g}",
        "PAN_DEPTH": f"{PAN_Y:g}",
        "PAN_HEIGHT": f"{PAN_Z:g}",
        "PAN_WALL": f"{WALL:g}",
        "PAN_FLOOR": f"{FLOOR:g}",
        "PLATE_LEN": f"{PLATE_X:g}",
        "PLATE_DEPTH": f"{PLATE_Y:g}",
        "PLATE_SLIP_MM": f"{PLATE_SLIP:g}",
        "PAN_VENT_GAP": f"{VENT_GAP:g}",
        "PAN_CAPACITY": f"{capacity_ml():.1f}",
        "PAN_CORNER_R": f"{CORNER_R:g}",
        "PAN_COVE_R": f"{FLOOR_COVE:g}",
        "PAN_FLANGE": f"{FLANGE_W:g}",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "PAN_LEN": 2, "PAN_DEPTH": 2, "PAN_HEIGHT": 2,
            "PAN_WALL": 1, "PAN_FLOOR": 1,
        },
    )
    substitute_md(
        _here.parent / "README.md",
        variables=variables,
        expected_counts={
            "PAN_LEN": 1, "PAN_DEPTH": 1, "PAN_HEIGHT": 1, "PAN_WALL": 1,
            "PAN_FLOOR": 1, "PAN_VENT_GAP": 1,
            "PAN_CAPACITY": 1, "PAN_CORNER_R": 1, "PAN_COVE_R": 1,
            "PLATE_LEN": 1, "PLATE_DEPTH": 1, "PLATE_SLIP_MM": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
