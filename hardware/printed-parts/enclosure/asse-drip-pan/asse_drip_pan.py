"""ASSE drip pan — the printed catch pan under the Multiplex atmospheric-vent stub.
The Shutao moisture plate lies flat in it; any vent drip, condensate, or overflow
pools in the pan and wets the plate, tripping the moisture alarm. Watertight
(no drain) — the pan is emptied on service.

One printed part: the PAN — an open-top rounded-corner box, [51](PAN_LEN) x
[76](PAN_DEPTH) outer x [15](PAN_HEIGHT) tall, [2.5](PAN_WALL) mm walls on a
[3](PAN_FLOOR) mm floor, floor-to-wall coved, with a [4](PAN_FLANGE) mm RIM
FLANGE turned out all four ways at the top — a baking tray, at that scale.

ONE SILHOUETTE, ONE RADIUS. The plan outline is a single rounded rectangle at
[6](PAN_CORNER_R) mm and everything else is that outline offset: the floor slab and
the walls are the outline itself, the flange is the outline plus `FLANGE_W`, and
the cavity is the outline less `WALL`. A corner is the same corner at every height,
so a hand runs down one arris from the rim to the floor. At the withdrawal end, one
full-height chamfered pull face closes that raw section and stands over the wall slot.

AND ONE FACE FROM THE FLOOR TO THE FLANGE. The wall's outside is a single vertical face
for the whole of `PAN_Z` under the flange's own section, so the pan's section across the
withdrawal axis is two rectangles: the body, and the rim standing out either side of it.

THE SLEEVE CARRIES IT, THE RIM KEEPS IT DOWN. `enclosure_assembly.pan_sleeve` stands a
solid block off the −X wall's inner face and cuts those same two rectangles out of it, one
`PAN_SLIP` larger all round. The pan lies on that block's floor the way a drawer lies in
its carcase, and the lid over the berth laps the flange, [3.70](PAN_LAP) mm of it a side
(`lap_w()`). West through the wall's slot is the one way the berth opens.

Frame: +X long axis (the withdrawal direction — the pan draws WEST through
`enclosure_assembly.west_wall_ports`'s slot), +Y depth, +Z up; origin at the pan's
lower-front-left outer corner of the WALLS, so the flange reaches −`FLANGE_W` of
it on both plan axes. Open top (+Z).

Run:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/asse-drip-pan/asse_drip_pan.py
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
from _cadq_export import export_assembly
from _materials import M_PETG_BLACK, one_body
from docgen import substitute_md, substitute_py_comments
import shutao_moisture_plate as plate

# The pan is narrow across the strip and deep down it. X is the loft's
# contested axis — east of the pan the west column's crossing ladder climbs
# rung over rung (`manifold-layout/_lines`), and the pan's east rim is that
# ladder's lid: every millimetre the pan gives back in X is
# ceiling a rung buys radius from. Y is the axis with room to spare: the run
# between the SeaFlo's back face and the foam cap's rear edge is deeper than
# the pan needs. So the width is the LANE, and the floor the moisture plate needs is
# what the lane has to leave: the plate turned down the depth wants
# `PLATE_Y + 2·(PLATE_SLIP + WALL + FLOOR_COVE)` = [51](PAN_PLATE_MIN) of outer width, and
# `check_plate()` reports a pan that gives back more than that.
#
# THE LANE IS THE MACHINE'S, so this figure is stated here and gated there: the pan hangs off
# the −X wall's own outer face (`enclosure_assembly.pan_west_x`) and the sleeve behind it has
# to stop short of the pump's casting (`enclosure_assembly.check_pan_lane`), which is what
# fixes the rim at [59](PAN_RIM_LEN) over the [51](PAN_LEN) of pan. [76](PAN_DEPTH) down, the
# pan hung on the atmospheric vent's own tip in both plan axes.
#
# [15](PAN_HEIGHT) TALL STANDS [12](PAN_WATER_DEPTH) mm OF WALL OVER THE WATER, and THE PAN
# COMES OUT FULL: drawn west down its slot, clear of the wall, then carried at arm's length to
# be poured out. The plate reads a pool a millimetre deep, so the alarm has been out since the
# first few mL and what these millimetres hold is the pool on that trip. They are dug DOWN —
# `enclosure_assembly.pan_floor` hangs the floor under a rim the chain fixes — into the strip
# of air over the SeaFlo's casting.
PAN_X, PAN_Y, PAN_Z = 51.0, 76.0, 15.0
WALL, FLOOR = 2.5, 3.0
# The PLAN OUTLINE's radius, and the only one this part has. Floor slab, walls, cavity
# and flange are all the one outline at their own offset, so the corner a hand runs down
# is one corner from the floor to the rim.
CORNER_R = 6.0
# Floor-to-wall fillet — water sheeting + cleanability. It eats the flat floor from
# both ±Y walls, and the moisture plate's long edge has to land inside what is left.
FLOOR_COVE = 2.0

# The rim flange's reach past each wall, ALL FOUR WAYS, at the rim plane. THE LAP IS WHAT
# CLOSES ON IT: the sleeve's floor takes the pan's weight and the sleeve's lid comes back over
# this band, `lap_w()` of it once the fit's `PAN_SLIP` is off. The pan's west end, which stands
# `enclosure_assembly.PAN_PROUD` outside the machine's skin, is where a hand goes.
#   IT IS ON THE WITHDRAWAL AXIS TWICE, so the rim runs [59](PAN_RIM_LEN) down a lane the pan
# takes [51](PAN_LEN) of — and that 51 is the plate's own minimum. One rim runs all four sides
# at the one figure.
FLANGE_W = 4.0
# The flange's own section — the wall turned out, so the rim is the gauge the pan is.
FLANGE_T = WALL
# Per side, pan to whatever holds it: the berth's flanks and its rebate's ceiling, and the
# pan's silhouette to the wall slot it draws through.
PAN_SLIP = 0.3

# THE PART THE HAND SEES IS A FACE, not the open pan's raw end section. From the flange's
# outermost west plane, this face runs back through the west wall and stops one `PAN_SLIP`
# short of the enclosure skin when `enclosure_assembly` stands it in the machine. It therefore
# masks the two-level wall slot without becoming an insertion stop, and the existing six
# millimetres of exposed pan become one deliberate pull rather than a rim shelf over a
# recessed wall. Its YZ outline uses printable 45 degree corners: it starts on the bed, grows
# no unsupported ledge, and preserves both the top thumb surface and the floor edge a finger
# hooks under.
PULL_FACE_DEPTH = 5.7
PULL_FACE_CHAMFER = WALL

# The Shutao LM393 module's conductivity plate (bom.md §sensors, B0B2W76MB1), lying
# flat on the pan floor with its long edge down the pan's Y — the withdrawal
# axis, the one the strip has depth to spare on. The floor's flat area inside the
# coves is what it lands on; `check_plate()` is that check.
#   READ OFF THE PLATE'S OWN MODEL, not copied from it. The body that lands in this
# pan in the assemblies is `reference/shutao-moisture-plate`, so the figure the
# floor is sized against and the figure the solid is built from are one figure —
# a pan cannot be gated on a plate a millimetre off the one it receives.
PLATE_X, PLATE_Y = plate.PLATE_X, plate.PLATE_Y
PLATE_SLIP = 1.0      # per side, plate edge to where the cove starts rising

# The least clear air the SLEEVE'S LID keeps under the ASSE chain's underside — which is the
# vent stub's tip when the chain hangs unrolled, and a body corner when it does not, the stub
# then standing above it. The lid is the topmost thing the pan's column carries, so it is
# what this gap is struck on, and the rim takes station one lid and one `PAN_SLIP` below it
# (`enclosure_assembly.pan_rim_z`).
VENT_GAP = 4.0


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
    """The flange's UNDERSIDE, in the part's own frame — the plane the wall's one vertical face
    runs up to, and the floor of the rebate the rim runs in. The flange's top is the rim, so
    this is one section down from it."""
    return PAN_Z - FLANGE_T


def lap_w():
    """The band of flange the sleeve's lid closes over, per side.

    The whole reach less a `PAN_SLIP`, so the lid's own flank never becomes the thing that
    stops the pan. The pan lies on the sleeve's floor, so what closes here holds it down and
    carries nothing."""
    return FLANGE_W - PAN_SLIP


# --- the bound this pan states --------------------------------------------
#
# The floor taking the moisture plate is a BOUND the pan states about itself, measured at
# every build off the plate's own model.
#
# A VIOLATED BOUND IS A THING TO LOOK AT, and what a reader looks at is the STEP, the three
# elevations and the scorecard a run writes. So it does not stop the build: `check_plate` hands
# back a `Bound` whether it holds or not, THE PAN COMES OUT AT ITS STATED SIZE — too small for
# the plate that overran it — and `enclosure_assembly.build_pan` enters the reading in that
# module's own ledger, where `_scorecard` renders it as the `plate-lies-flat` gate row carrying the
# message written here. A raise would have destroyed every artifact a reader could see the fault
# in.
Bound = namedtuple("Bound", "id label ok value target detail")


def check_plate() -> Bound:
    """Whether the flat floor takes the plate with its slip on every side. The
    plate lies turned — its long edge down the pan's Y — so the width it asks of the
    pan comes out of the axis the strip has to give. A plate wider than the flat
    rides up on the coves instead of lying down, and the water has to stand that much
    deeper before it reads."""
    fx, fy = flat_floor()
    need_x, need_y = PLATE_Y + 2 * PLATE_SLIP, PLATE_X + 2 * PLATE_SLIP
    ok = fx >= need_x and fy >= need_y
    return Bound(
        "plate-lies-flat", "The moisture plate lies flat on the pan's floor", ok,
        f"flat floor {fx:.2f} x {fy:.2f}", f"{need_x:.2f} x {need_y:.2f}",
        ([] if ok else [
            f"ASSE drip pan floor {fx:.2f} x {fy:.2f} flat inside the r{FLOOR_COVE:g} coves; "
            f"the {PLATE_X:g} x {PLATE_Y:g} plate turned down the depth, with "
            f"{PLATE_SLIP:g} slip a side, needs {need_x:.2f} x {need_y:.2f}. Grow PAN_Y, "
            f"shrink FLOOR_COVE, or move the SeaFlo forward — the strip behind it is "
            f"what PAN_Y comes out of."]))


def build():
    """The one plan outline at three offsets, with one face closing the withdrawal end.

    Shell, rim and pull face are fused before the cavity is cut. The pull stops inside the
    west wall's own thickness, so the cavity remains the same watertight volume and the face
    adds no obstruction to the moisture plate or its open-top lead route.
    """
    # Floor slab and walls together, on the outline itself. One prism, so the base cannot
    # take a radius of its own, and its flank is one face the whole way up.
    outer = _rounded_prism(PAN_X, PAN_Y, PAN_Z, CORNER_R)
    # Inner cavity: rounded vertical corners + a filleted bottom, so subtracting
    # it leaves a floor-to-wall cove. Sits on the FLOOR-thick base, open at top.
    cavity = (
        _rounded_prism(PAN_X - 2 * WALL, PAN_Y - 2 * WALL, PAN_Z, max(CORNER_R - WALL, 1.5))
        .edges("<Z").fillet(FLOOR_COVE)
        .translate((WALL, WALL, FLOOR))
    )
    # The RIM FLANGE — the outline plus `FLANGE_W`, one section thick, its top face flush
    # with the rim so the flange costs the column nothing above the pan. Its underside is
    # the only overhang on the part, and it reaches `FLANGE_W` off a face the printer has
    # been laying down since the first layer.
    flange = _rounded_prism(
        PAN_X + 2 * FLANGE_W, PAN_Y + 2 * FLANGE_W, FLANGE_T, CORNER_R + FLANGE_W
    ).translate((-FLANGE_W, -FLANGE_W, flange_z()))
    y0, y1 = -FLANGE_W, PAN_Y + FLANGE_W
    c = PULL_FACE_CHAMFER
    pull_section = (
        (y0 + c, 0.0), (y1 - c, 0.0),
        (y1, c), (y1, PAN_Z - c),
        (y1 - c, PAN_Z), (y0 + c, PAN_Z),
        (y0, PAN_Z - c), (y0, c),
    )
    pull = (
        cq.Workplane("YZ", origin=(-FLANGE_W, 0.0, 0.0))
        .polyline(pull_section).close()
        .extrude(PULL_FACE_DEPTH)
    )
    return outer.union(flange).union(pull).cut(cavity)


def capacity_ml():
    """The pan holds this before it overflows the rim — no drain, emptied on
    service, so it is the interval the vent's weep buys."""
    return (PAN_X - 2 * WALL) * (PAN_Y - 2 * WALL) * (PAN_Z - FLOOR) / 1000.0


def main():
    pan = build()
    bb = pan.val().BoundingBox()
    print("ASSE drip pan — printed catch pan")
    print(f"  Pan bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
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
          f"r{CORNER_R + FLANGE_W:g}, {lap_w():.2f} of lap a side")
    print(f"  Pull face {PAN_Y + 2 * FLANGE_W:g} x {PAN_Z:g}, "
          f"{PULL_FACE_DEPTH:g} deep with {PULL_FACE_CHAMFER:g} mm 45 degree corners")
    print(f"  Withdraws −X: {PAN_X + 2 * FLANGE_W:g} mm long on that axis, so it draws its own "
          f"length plus the wall's section to come clear")
    for shape, name in ((pan, "asse-drip-pan.step"),):
        out = _here.parent / name
        export_assembly(one_body(shape, out.stem, M_PETG_BLACK), str(out))
        print(f"-> {out.name}")

    variables = {
        "PAN_LEN": f"{PAN_X:g}",
        "PAN_DEPTH": f"{PAN_Y:g}",
        "PAN_HEIGHT": f"{PAN_Z:g}",
        "PAN_WATER_DEPTH": f"{PAN_Z - FLOOR:g}",
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
        "PAN_LAP": f"{lap_w():.2f}",
        "PAN_RIM_LEN": f"{PAN_X + 2 * FLANGE_W:g}",
        "PAN_RIM_DEPTH": f"{PAN_Y + 2 * FLANGE_W:g}",
        "PAN_RIM_CORNER_R": f"{CORNER_R + FLANGE_W:g}",
        "PULL_FACE_DEPTH": f"{PULL_FACE_DEPTH:g}",
        "PULL_FACE_CHAMFER": f"{PULL_FACE_CHAMFER:g}",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
    )
    substitute_md(
        _here.parent / "README.md",
        variables=variables,
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
