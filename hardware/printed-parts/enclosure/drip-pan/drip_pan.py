"""Drip pan — the printed catch basin under the Multiplex atmospheric-vent stub,
carried on rails above the cold core's foam-cap top. The Shutao moisture plate
lies flat in it; any vent drip, condensate, or overflow pools in the basin and
wets the plate, tripping the moisture alarm. Watertight (no drain) — the basin
is emptied on service.

Two printed parts:

  * the BASIN — an open-top rounded-corner box, [64](PAN_LEN) x [76](PAN_DEPTH)
    outer x [15](PAN_HEIGHT) tall, [2.5](PAN_WALL) mm walls on a [3](PAN_FLOOR)
    mm floor, floor-to-wall coved. The floor slab runs out past the walls on
    both ±X faces as a SLIDE FLANGE, so the basin is carried from underneath at
    its own floor plane and nothing stands proud inside it.
  * the RAILS — a mirrored pair of L-sections, taped to the foam-cap top with
    VHB, whose shelves are what the flanges ride. They hold the basin
    [17.7](PAN_LIFT) mm clear of the cap, and they run fore-and-aft, so the
    basin travels in +Y — out the back of the cabinet — rather than lifting.

The chain hangs at a fixed height over a fixed cap, and the basin stands in the
column between them: `VENT_GAP` of air under the chain's underside, then the
basin, then `RAIL_LIFT` of open deck down to the cap.

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

# The basin is narrow across the strip and deep down it. X is the aft strip's
# contested axis — the controller board stands in the same strip, west of the
# basin, and every millimetre the basin gives back in X is a millimetre of the
# board's connector lanes. Y is the axis with room to spare: the run between the
# SeaFlo's back face and the foam cap's rear edge is deeper than the basin needs.
# So [64](PAN_LEN) across and [76](PAN_DEPTH) down, and the moisture plate lies
# with its long edge down the depth. [15](PAN_HEIGHT) tall is what `VENT_GAP` and
# `RAIL_LIFT` leave of the vent's column.
PAN_X, PAN_Y, PAN_Z = 64.0, 76.0, 15.0
WALL, FLOOR = 2.5, 3.0
CORNER_R = 6.0        # outer vertical-corner radius
# Floor-to-wall fillet — water sheeting + cleanability. It eats the flat floor from
# both ±Y walls, and the moisture plate's long edge has to land inside what is left.
FLOOR_COVE = 2.0
# The floor slab's reach past each wall. Zero: the basin is carried on its own
# floor edge, and the rails keep to the basin's own width — the aft strip's east
# end belongs to V-K and the umbilical cluster, and a rail reaching out into it
# buys nothing the wall's own footprint does not already give.
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
# How much more than that the rail may leave, so the rail can be a round printed
# number under a chain whose underside is a rolled hex corner and irrational.
VENT_GAP_SLACK = 1.0
# The rail shelf's height off the cap — the basin's floor plane. What is left of the
# vent's column below the rim is split between this open deck, which carries the SIG-9
# leads and the C14 cordage, and the basin standing on it.
# `_contents.drip_pan_seat()` measures the gap this leaves and raises outside the band.
RAIL_LIFT = 17.7

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
    # The slide flange: the floor slab run out past both walls, carrying the
    # basin at its own floor plane.
    flange = _rounded_prism(
        PAN_X + 2 * FLANGE_W, PAN_Y, FLOOR, 3.0
    ).translate((-FLANGE_W, 0.0, 0.0))
    return outer.cut(cavity).union(flange)


def rail_offset():
    """Basin origin to the rail pair's origin — out past the basin's floor edge by
    the slip fit and the web, forward by the home stop, and down by the lift. The
    enclosure places the basin; the rails follow it."""
    return (-(FLANGE_W + RAIL_FIT + RAIL_WEB), -RAIL_STOP_Y, -RAIL_LIFT)


def rail_span():
    """Outer width across the pair — what the cap top has to offer them. The feet
    turn inboard, under the basin, so this is the basin plus two webs."""
    return 2 * (RAIL_WEB + RAIL_FIT) + 2 * FLANGE_W + PAN_X


def rail_length():
    """The rail runs the basin's depth plus the home stop standing forward of it."""
    return PAN_Y + RAIL_STOP_Y


def _rail():
    """One L-section rail in the pair's frame: foot, web, shelf, home stop. Its
    shelf's top face is the basin's floor plane."""
    length = rail_length()
    # Foot and shelf both turn INBOARD off the web, at opposite ends of its height:
    # the foot lies on the cap under the basin, the shelf carries the basin's floor
    # edge. Nothing reaches outboard, so the pair is no wider than the basin plus
    # its two webs.
    foot = cq.Workplane("XY").box(RAIL_WEB + RAIL_FOOT, length, RAIL_FOOT_T,
                                  centered=(False, False, False))
    web = cq.Workplane("XY").box(RAIL_WEB, length, RAIL_LIFT + RAIL_FENCE,
                                 centered=(False, False, False))
    shelf = (cq.Workplane("XY")
             .box(RAIL_SHELF_W, length, RAIL_SHELF_T, centered=(False, False, False))
             .translate((RAIL_WEB, 0.0, RAIL_LIFT - RAIL_SHELF_T)))
    # The home stop stands at the forward end, ahead of where the basin lands —
    # the aft end is the mouth it leaves through. The basin's front wall butts it.
    stop = (cq.Workplane("XY")
            .box(RAIL_SHELF_W, RAIL_STOP_Y, RAIL_FENCE, centered=(False, False, False))
            .translate((RAIL_WEB, 0.0, RAIL_LIFT)))
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
    fx, fy = flat_floor()
    print(f"  Flat floor {fx:g} x {fy:g} inside the coves — "
          f"plate {PLATE_X:g} x {PLATE_Y:g} with {PLATE_SLIP:g} slip a side")
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
        "PLATE_LEN": f"{PLATE_X:g}",
        "PLATE_DEPTH": f"{PLATE_Y:g}",
        "PLATE_SLIP_MM": f"{PLATE_SLIP:g}",
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
            "PAN_FLOOR": 1, "PAN_LIFT": 1, "PAN_VENT_GAP": 1,
            "PAN_CAPACITY": 1, "PAN_CORNER_R": 1, "PAN_COVE_R": 1,
            "PLATE_LEN": 1, "PLATE_DEPTH": 1, "PLATE_SLIP_MM": 1,
            "RAIL_SPAN": 2, "RAIL_SLIP": 1, "RAIL_RAIL_T": 1, "RAIL_VHB": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
