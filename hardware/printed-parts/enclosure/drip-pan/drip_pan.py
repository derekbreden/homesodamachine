"""Drip pan — the printed catch basin under the Multiplex atmospheric-vent stub.
The Shutao moisture plate lies flat in it; any vent drip, condensate, or overflow
pools in the basin and wets the plate, tripping the moisture alarm. Watertight
(no drain) — the basin is emptied on service.

One printed part: the BASIN — an open-top rounded-corner box, [52](PAN_LEN) x
[76](PAN_DEPTH) outer x [10](PAN_HEIGHT) tall, [2.5](PAN_WALL) mm walls on a
[3](PAN_FLOOR) mm floor, floor-to-wall coved, with a [10](PAN_FLANGE) mm RIM
FLANGE turned out all four ways at the top — a baking tray, at tray scale.

ONE SILHOUETTE, ONE RADIUS. The plan outline is a single rounded rectangle at
[6](PAN_CORNER_R) mm and everything else is that outline offset: the floor slab and
the walls are the outline itself, the flange is the outline plus `FLANGE_W`, and
the cavity is the outline less `WALL`. A corner is the same corner at every height,
so a hand runs down one arris from the rim to the floor.

The column reads UP from the pump: the basin's own floor takes its air over the
SeaFlo's BRACKET — the feet's top face, the widest section the casting has and the
one the tray rides over — then the basin, then `VENT_GAP` of air under the chain's
underside. `front_half.pan_floor` is the plane the basin's own floor reaches, and
`front_half.build_asse` hangs the chain off that plane rather than the other way
round.

NOTHING STANDS UNDER THE FLOOR. The basin lies over the casting, so section
beneath it is height the basin pays for twice — once to clear the pump and again
to carry the load. So the carry takes hold of the RIM instead: the flange's flat
underside is the bearing face, `front_half.pan_rails` stands a rail pair under
it off the west wall, and the floor is left free at its own clearance over the
bracket. Nothing under the floor, so nothing under the floor to pay for.

Frame: +X long axis (the withdrawal direction — the tray draws WEST through
`front_half.west_wall_ports`'s slot), +Y depth, +Z up; origin at the basin's
lower-front-left outer corner of the WALLS, so the flange reaches −`FLANGE_W` of
it on both plan axes. Open top (+Z).

Run:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/drip-pan/drip_pan.py
"""

import sys
from collections import namedtuple
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_hw / "reference" / "shutao-moisture-plate"))
sys.path.insert(0, str(next(p for p in _here.parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_step
from docgen import substitute_md, substitute_py_comments
import shutao_moisture_plate as plate

# The basin is narrow across the strip and deep down it. X is the loft's
# contested axis — east of the basin the west column's crossing ladder climbs
# rung over rung (`manifold-layout/_lines`), and the basin's east rim is that
# ladder's lid: every millimetre the basin gives back in X is
# ceiling a rung buys radius from. Y is the axis with room to spare: the run
# between the SeaFlo's back face and the foam cap's rear edge is deeper than
# the basin needs. So the width is the LANE, and the floor the moisture plate needs is
# what the lane has to leave: the plate turned down the depth wants
# `PLATE_Y + 2·(PLATE_SLIP + WALL + FLOOR_COVE)` = [51](PAN_PLATE_MIN) of outer width, and
# `check_plate()` reports a basin that gives back more than that.
#
# THE LANE IS THE MACHINE'S, so this figure is stated here and gated there: the tray hangs
# off the pump's own casting at one clearance (`front_half.pan_east_x`) and its west lip has
# to land inside the −X wall (`front_half.check_pan_lane`), which is what fixes the rim at
# [72](PAN_RIM_LEN) over the [52](PAN_LEN) of basin. [76](PAN_DEPTH) down, the basin hung on
# the atmospheric vent's own tip in both plan axes. [10](PAN_HEIGHT) tall is what `VENT_GAP`
# leaves of the vent's column once the basin's floor has taken its own air over the casting.
PAN_X, PAN_Y, PAN_Z = 52.0, 76.0, 10.0
WALL, FLOOR = 2.5, 3.0
# The PLAN OUTLINE's radius, and the only one this part has. Floor slab, walls, cavity
# and flange are all the one outline at their own offset, so the corner a hand runs down
# is one corner from the floor to the rim.
CORNER_R = 6.0
# Floor-to-wall fillet — water sheeting + cleanability. It eats the flat floor from
# both ±Y walls, and the moisture plate's long edge has to land inside what is left.
FLOOR_COVE = 2.0

# The rim flange's reach past each wall, ALL FOUR WAYS, at the rim plane rather than at
# the floor — the basin lies over the casting, so a carry under the floor is height
# charged twice and this is the face that spares it.
#   ONE NUMBER FOR TWO GRIPS, and the HAND sets it: the west lip is hooked with a
# fingertip to draw the tray out through the wall, and a lip a finger pulls on wants ten.
# The MACHINE takes what that lip leaves — the flat band of underside a rail bears on,
# which is the reach less the haunch's `FLANGE_HAUNCH` and the fit's `PAN_SLIP`,
# [6.70](PAN_BEARING) mm of it, `bearing_w()`. One rim runs all four sides at the one
# figure.
FLANGE_W = 10.0
# The flange's own section — the wall turned out, so the rim is the gauge the tray is.
FLANGE_T = WALL
# The 45° haunch filling the corner between the wall's outer face and the flange's
# underside. The tray prints floor-down, so that underside is an overhang: the haunch is
# what the first courses of it grow out of, and it cuts the unsupported reach to
# `FLANGE_W - FLANGE_HAUNCH`. It also takes the rail's inboard arris, which is what
# centres the tray across the pair.
FLANGE_HAUNCH = 3.0
# A hair of vertical face left under the haunch so the 45° is a chamfer and not a
# degenerate one — at the full height OCC declines the cut.
FLANGE_HAUNCH_SKIRT = 0.5
# Per side, tray to whatever holds it: flange underside to rail flank, and tray
# silhouette to the wall slot it draws through.
PAN_SLIP = 0.3

# The Shutao LM393 module's conductivity plate (bom.md §sensors, B0B2W76MB1), lying
# flat on the basin floor with its long edge down the basin's Y — the withdrawal
# axis, the one the strip has depth to spare on. The floor's flat area inside the
# coves is what it lands on; `check_plate()` is that check.
#   READ OFF THE PLATE'S OWN MODEL, not copied from it. The body that lands in this
# basin in the assemblies is `reference/shutao-moisture-plate`, so the figure the
# floor is sized against and the figure the solid is built from are one figure —
# a basin cannot be gated on a plate a millimetre off the one it receives.
PLATE_X, PLATE_Y = plate.PLATE_X, plate.PLATE_Y
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


def flange_z():
    """The flange's UNDERSIDE, in the part's own frame — the bearing plane, and the plane a
    rail's top face reaches. The flange's top is the rim, so this is one section down from it."""
    return PAN_Z - FLANGE_T


def bearing_w():
    """The flat band of flange underside a rail may stand under, per side.

    Not the whole flange: the haunch takes the inboard `FLANGE_HAUNCH` of it at 45°, and the
    fit takes a `PAN_SLIP` off the outboard end so the rail's flank never becomes the thing
    that stops the tray. What is left is flat, and it is what carries the tray."""
    return FLANGE_W - FLANGE_HAUNCH - PAN_SLIP


# --- the bound this basin states --------------------------------------------
#
# The floor taking the moisture plate is a BOUND the basin states about itself, measured at
# every build off the plate's own model.
#
# A VIOLATED BOUND IS A THING TO LOOK AT, and what a reader looks at is the STEP, the three
# elevations and the scorecard a run writes. So it does not stop the build: `check_plate` hands
# back a `Bound` whether it holds or not, THE BASIN COMES OUT AT ITS STATED SIZE — too small for
# the plate that overran it — and `front_half.build_pan` enters the reading in that module's own
# ledger, where `_scorecard` renders it as the `plate-lies-flat` gate row carrying the message
# written here. A raise would have destroyed every artifact a reader could see the fault in.
Bound = namedtuple("Bound", "id label ok value target detail")


def check_plate() -> Bound:
    """Whether the flat floor takes the plate with its slip on every side. The
    plate lies turned — its long edge down the basin's Y — so the width it asks of the
    basin comes out of the axis the strip has to give. A plate wider than the flat
    rides up on the coves instead of lying down, and the water has to stand that much
    deeper before it reads."""
    fx, fy = flat_floor()
    need_x, need_y = PLATE_Y + 2 * PLATE_SLIP, PLATE_X + 2 * PLATE_SLIP
    ok = fx >= need_x and fy >= need_y
    return Bound(
        "plate-lies-flat", "The moisture plate lies flat on the basin's floor", ok,
        f"flat floor {fx:.2f} x {fy:.2f}", f"{need_x:.2f} x {need_y:.2f}",
        ([] if ok else [
            f"drip-pan floor {fx:.2f} x {fy:.2f} flat inside the r{FLOOR_COVE:g} coves; "
            f"the {PLATE_X:g} x {PLATE_Y:g} plate turned down the depth, with "
            f"{PLATE_SLIP:g} slip a side, needs {need_x:.2f} x {need_y:.2f}. Grow PAN_Y, "
            f"shrink FLOOR_COVE, or move the SeaFlo forward — the strip behind it is "
            f"what PAN_Y comes out of."]))


def build():
    """The one plan outline at four offsets: shell, rim flange and haunch fused, then the
    cavity cut back out of the lot — cut LAST, so the flange that laps the rim does not
    roof the basin it belongs to."""
    # Floor slab and walls together, on the outline itself. One prism, so the base cannot
    # take a radius of its own.
    outer = _rounded_prism(PAN_X, PAN_Y, PAN_Z, CORNER_R)
    # Inner cavity: rounded vertical corners + a filleted bottom, so subtracting
    # it leaves a floor-to-wall cove. Sits on the FLOOR-thick base, open at top.
    cavity = (
        _rounded_prism(PAN_X - 2 * WALL, PAN_Y - 2 * WALL, PAN_Z, max(CORNER_R - WALL, 1.5))
        .edges("<Z").fillet(FLOOR_COVE)
        .translate((WALL, WALL, FLOOR))
    )
    # The RIM FLANGE — the outline plus `FLANGE_W`, one section thick, its top face flush
    # with the rim so the flange costs the column nothing above the basin.
    flange = _rounded_prism(
        PAN_X + 2 * FLANGE_W, PAN_Y + 2 * FLANGE_W, FLANGE_T, CORNER_R + FLANGE_W
    ).translate((-FLANGE_W, -FLANGE_W, flange_z()))
    # The haunch under it: a prism on the outline plus `FLANGE_HAUNCH`, its lower edge
    # chamfered the full haunch back to the outline itself — so its underside leaves the
    # wall at 45° and the flange's overhang starts from something.
    haunch = (
        _rounded_prism(PAN_X + 2 * FLANGE_HAUNCH, PAN_Y + 2 * FLANGE_HAUNCH,
                       FLANGE_HAUNCH + FLANGE_HAUNCH_SKIRT, CORNER_R + FLANGE_HAUNCH)
        .edges("<Z").chamfer(FLANGE_HAUNCH)
        .translate((-FLANGE_HAUNCH, -FLANGE_HAUNCH,
                    flange_z() - FLANGE_HAUNCH - FLANGE_HAUNCH_SKIRT))
    )
    return outer.union(flange).union(haunch).cut(cavity)


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
    plate_bound = check_plate()
    print(f"  {'✓' if plate_bound.ok else '✗'} {plate_bound.label}: "
          f"{plate_bound.value}, wants {plate_bound.target}")
    for line in plate_bound.detail:
        print(f"      {line}")
    print(f"  Rim flange {FLANGE_W:g} all four ways at z {flange_z():g} — "
          f"{PAN_X + 2 * FLANGE_W:g} x {PAN_Y + 2 * FLANGE_W:g} over the rim, "
          f"r{CORNER_R + FLANGE_W:g}, {bearing_w():.2f} of flat bearing a side")
    print(f"  Withdraws −X: {PAN_X + 2 * FLANGE_W:g} mm long on that axis, so it draws its own "
          f"length plus the wall's section to come clear")
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
        "PAN_PLATE_MIN": f"{PLATE_Y + 2 * (PLATE_SLIP + WALL + FLOOR_COVE):g}",
        "PAN_VENT_GAP": f"{VENT_GAP:g}",
        "PAN_CAPACITY": f"{capacity_ml():.1f}",
        "PAN_CORNER_R": f"{CORNER_R:g}",
        "PAN_COVE_R": f"{FLOOR_COVE:g}",
        "PAN_FLANGE": f"{FLANGE_W:g}",
        "PAN_BEARING": f"{bearing_w():.2f}",
        "PAN_RIM_LEN": f"{PAN_X + 2 * FLANGE_W:g}",
        "PAN_RIM_DEPTH": f"{PAN_Y + 2 * FLANGE_W:g}",
        "PAN_RIM_CORNER_R": f"{CORNER_R + FLANGE_W:g}",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "PAN_LEN": 2, "PAN_DEPTH": 2, "PAN_HEIGHT": 2,
            "PAN_WALL": 1, "PAN_FLOOR": 1, "PAN_PLATE_MIN": 1,
            "PAN_FLANGE": 1, "PAN_CORNER_R": 1, "PAN_BEARING": 1,
            "PAN_RIM_LEN": 1,
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
            "PAN_FLANGE": 2, "PAN_BEARING": 1,
            "PAN_RIM_LEN": 1, "PAN_RIM_DEPTH": 1, "PAN_RIM_CORNER_R": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
