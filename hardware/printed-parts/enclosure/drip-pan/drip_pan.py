"""Drip pan — the printed catch basin under the Multiplex atmospheric-vent stub,
carried on rails above the cold core's foam-cap top. The Shutao moisture plate
lies flat in it; any vent drip, condensate, or overflow pools in the basin and
wets the plate, tripping the moisture alarm. Watertight (no drain) — the basin
is emptied on service.

Two printed parts:

  * the BASIN — an open-top rounded-corner box, [100](PAN_LEN) x [48](PAN_DEPTH)
    outer x [14](PAN_HEIGHT) tall, [2.5](PAN_WALL) mm walls on a [3](PAN_FLOOR)
    mm floor, floor-to-wall coved. The floor slab runs out past the walls on
    both ±X faces as a SLIDE FLANGE, so the basin is carried from underneath at
    its own floor plane and nothing stands proud inside it.
  * the RAILS — a mirrored pair of L-sections, taped to the foam-cap top with
    VHB, whose shelves are what the flanges ride. They hold the basin
    [13.6](PAN_LIFT) mm clear of the cap, and they run fore-and-aft, so the
    basin travels in +Y — out the back of the cabinet — rather than lifting.

The stub weeps from a fixed tip onto a fixed cap, and the basin stands in the
column between them: `VENT_GAP` of air under the tip, then the basin, then
`RAIL_LIFT` of open deck down to the cap.

Frame: +X long axis, +Y depth (the withdrawal direction), +Z up; origin at the
basin's lower-front-left outer corner of the WALLS — the flanges reach to −X of
it. `rail_offset()` carries that origin to the rail pair's. Open top (+Z).

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

# [100](PAN_LEN) long so the moisture plate lies flat down its length.
# [48](PAN_DEPTH) deep is the aft strip spent: the run between the SeaFlo's back
# face and the foam cap's rear edge, less a standoff off the pump — the pack's
# placement rules hold both of those clearances. [14](PAN_HEIGHT) tall is what
# `VENT_GAP` and `RAIL_LIFT` leave of the vent's column.
PAN_X, PAN_Y, PAN_Z = 100.0, 48.0, 14.0
WALL, FLOOR = 2.5, 3.0
CORNER_R = 6.0        # outer vertical-corner radius
FLOOR_COVE = 3.0      # inner floor-to-wall fillet (water sheeting + cleanability)
FLANGE_W = 5.0        # the floor slab's reach past each wall — the slide surface

# The clear air the basin's rim keeps under the vent stub's tip.
VENT_GAP = 4.0
# The rail shelf's height off the cap — the basin's floor plane.
# `_contents.drip_pan_seat()` re-derives it from the placed vent tip.
RAIL_LIFT = 13.6

RAIL_WEB = 3.0        # web thickness, standing outboard of the flange
RAIL_FIT = 0.3        # per side, flange tip to web inner face
RAIL_FOOT = 4.0       # outboard base flange — the VHB footprint the web alone lacks
RAIL_FOOT_T = 1.5
RAIL_SHELF_W = 4.0    # inboard reach under the flange
RAIL_SHELF_T = 2.5
RAIL_FENCE = 6.0      # web height above the shelf — fences the basin in X
RAIL_STOP_Y = 3.0     # the home stop at the rail's forward end
RAIL_TAPE = 1.1       # 3M VHB 4941 between the foot's underside and the foam cap


def _rounded_prism(x, y, z, r):
    return (
        cq.Workplane("XY")
        .box(x, y, z, centered=(False, False, False))
        .edges("|Z").fillet(r)
    )


def build():
    """Rounded-corner open basin on a flanged floor slab: outer shell minus a
    filleted inner cavity, unioned with the slab that overhangs it on ±X."""
    outer = _rounded_prism(PAN_X, PAN_Y, PAN_Z, CORNER_R)
    # Inner cavity: rounded vertical corners + a filleted bottom, so subtracting
    # it leaves a floor-to-wall cove. Sits on the FLOOR-thick base, open at top.
    cavity = (
        _rounded_prism(PAN_X - 2 * WALL, PAN_Y - 2 * WALL, PAN_Z, max(CORNER_R - WALL, 1.5))
        .edges("<Z").fillet(FLOOR_COVE)
        .translate((WALL, WALL, FLOOR))
    )
    # The slide flange: the floor slab run out past both walls, carrying the
    # basin at its own floor plane.
    flange = _rounded_prism(
        PAN_X + 2 * FLANGE_W, PAN_Y, FLOOR, 3.0
    ).translate((-FLANGE_W, 0.0, 0.0))
    return outer.cut(cavity).union(flange)


def rail_offset():
    """Basin origin to the rail pair's origin — out past the flange tip by the
    slip fit, the web and the foot, forward by the home stop, and down by the
    lift. The enclosure places the basin; the rails follow it."""
    return (-(FLANGE_W + RAIL_FIT + RAIL_WEB + RAIL_FOOT), -RAIL_STOP_Y, -RAIL_LIFT)


def rail_span():
    """Outer width across the pair — what the cap top has to offer them."""
    return 2 * (RAIL_FOOT + RAIL_WEB + RAIL_FIT) + 2 * FLANGE_W + PAN_X


def rail_length():
    """The rail runs the basin's depth plus the home stop standing forward of it."""
    return PAN_Y + RAIL_STOP_Y


def _rail():
    """One L-section rail in the pair's frame: foot, web, shelf, home stop. Its
    shelf's top face is the basin's floor plane."""
    length = rail_length()
    foot = cq.Workplane("XY").box(RAIL_FOOT + RAIL_WEB, length, RAIL_FOOT_T,
                                  centered=(False, False, False))
    web = (cq.Workplane("XY")
           .box(RAIL_WEB, length, RAIL_LIFT + RAIL_FENCE, centered=(False, False, False))
           .translate((RAIL_FOOT, 0.0, 0.0)))
    shelf = (cq.Workplane("XY")
             .box(RAIL_SHELF_W, length, RAIL_SHELF_T, centered=(False, False, False))
             .translate((RAIL_FOOT + RAIL_WEB, 0.0, RAIL_LIFT - RAIL_SHELF_T)))
    # The home stop stands at the forward end, ahead of where the flange lands —
    # the aft end is the mouth the basin leaves through. The flange's front edge
    # butts it.
    stop = (cq.Workplane("XY")
            .box(RAIL_SHELF_W, RAIL_STOP_Y, RAIL_FENCE, centered=(False, False, False))
            .translate((RAIL_FOOT + RAIL_WEB, 0.0, RAIL_LIFT)))
    return foot.union(web).union(shelf).union(stop)


def build_rails():
    """The mirrored pair, as one body — they print together and install as a set.
    The basin drops between the two webs and rides the two shelves."""
    left = _rail()
    right = _rail().mirror("YZ").translate((rail_span(), 0.0, 0.0))
    return left.union(right)


def capacity_ml():
    """The basin holds this before it overflows the rim — no drain, emptied on
    service, so it is the interval the vent's weep buys."""
    return (PAN_X - 2 * WALL) * (PAN_Y - 2 * WALL) * (PAN_Z - FLOOR) / 1000.0


def main():
    pan = build()
    rails = build_rails()
    bb = pan.val().BoundingBox()
    rb = rails.val().BoundingBox()
    print("Drip pan — printed catch basin + slide rails")
    print(f"  Basin bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  {PAN_X:g}x{PAN_Y:g}x{PAN_Z:g} outer, {WALL:g} wall, {FLOOR:g} floor, "
          f"r{CORNER_R:g} corners, r{FLOOR_COVE:g} floor cove, {capacity_ml():.1f} mL to the rim")
    print(f"  Slide flange {FLANGE_W:g} per side at the floor plane — "
          f"{PAN_X + 2 * FLANGE_W:g} across the flanges")
    ox, oy, oz = rail_offset()
    print(f"  Rails bounding box: X [{rb.xmin:.2f}, {rb.xmax:.2f}]  "
          f"Y [{rb.ymin:.2f}, {rb.ymax:.2f}]  Z [{rb.zmin:.2f}, {rb.zmax:.2f}]  "
          f"at ({ox:+.1f}, {oy:+.1f}, {oz:+.1f}) off the basin origin")
    print(f"  Lift {RAIL_LIFT:g} to the floor plane on {RAIL_TAPE:g} VHB, "
          f"{RAIL_FIT:g} slip per side, {rail_span():g} across the pair")
    print(f"  Withdraws +Y: {PAN_Y:g} mm of travel clears the rails entirely")
    for shape, name in ((pan, "drip-pan.step"), (rails, "drip-pan-rails.step")):
        out = _here.parent / name
        export_step(shape, str(out))
        print(f"-> {out.name}")

    variables = {
        "PAN_LEN": f"{PAN_X:g}",
        "PAN_DEPTH": f"{PAN_Y:g}",
        "PAN_HEIGHT": f"{PAN_Z:g}",
        "PAN_WALL": f"{WALL:g}",
        "PAN_FLOOR": f"{FLOOR:g}",
        "PAN_FLANGE": f"{FLANGE_W:g}",
        "PAN_ACROSS": f"{PAN_X + 2 * FLANGE_W:g}",
        "PAN_LIFT": f"{RAIL_LIFT:g}",
        "PAN_VENT_GAP": f"{VENT_GAP:g}",
        "PAN_CAPACITY": f"{capacity_ml():.1f}",
        "PAN_CORNER_R": f"{CORNER_R:g}",
        "PAN_COVE_R": f"{FLOOR_COVE:g}",
        "RAIL_SPAN": f"{rail_span():g}",
        "RAIL_SLIP": f"{RAIL_FIT:g}",
        "RAIL_RAIL_T": f"{RAIL_WEB:g}",
        "RAIL_VHB": f"{RAIL_TAPE:g}",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "PAN_LEN": 2, "PAN_DEPTH": 2, "PAN_HEIGHT": 2,
            "PAN_WALL": 1, "PAN_FLOOR": 1, "PAN_LIFT": 1,
        },
    )
    substitute_md(
        _here.parent / "README.md",
        variables=variables,
        expected_counts={
            "PAN_LEN": 1, "PAN_DEPTH": 1, "PAN_HEIGHT": 1, "PAN_WALL": 1,
            "PAN_FLOOR": 1, "PAN_FLANGE": 1, "PAN_ACROSS": 1, "PAN_LIFT": 1,
            "PAN_VENT_GAP": 1, "PAN_CAPACITY": 1, "PAN_CORNER_R": 1,
            "PAN_COVE_R": 1, "RAIL_SPAN": 1, "RAIL_SLIP": 1,
            "RAIL_RAIL_T": 1, "RAIL_VHB": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
