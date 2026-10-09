"""Bulkhead ring — the colour and the word one of the +Y wall of back-top's connections is
read by.

A flat chip lying in a pocket of that wall's outer face, with a through-wall fitting's own
flange landing on it. Nothing fastens it: the fitting's nut makes up on the inboard side and draws
flange, chip and wall together, so the chip is in the clamped stack the way the wall is. The pocket
is the chip's own thickness deep, so the two faces come out one plane and only the word stands out
of it.

    RING_W    how far a chip stands past the fitting's own flange, and so the width of colour that
              shows once the flange is on. The wall strikes its pockets from it, the iso line-art
              paints its marks from it, and it is the band the word is lettered in
    THICK     the chip's thickness, the depth the pocket is cut to, and — because the wall keeps
              its own full stock under every chip — the height of the boss the wall stands inboard

THE OUTLINE IS 32 MM WIDE AT EVERY STATION, with R2 lower corners. Its bottom edge meets
the flange envelope; above the flange, a dedicated band carries the lettering.
It is not a shape that turns — a pocket takes it one way up and no other, which is what puts the
word level without anything holding it there.

At the rear face the customer meets identical black fittings in a black wall, one of which takes
the blue tube — `../y-wall-of-back-top/README.md` §"Umbilical port — tube identification". A chip's colour
is its tube's colour and there are six of them; what a colour means is stated once, in
`../y-wall-of-back-top/_y_wall_dimensions.py`.

THE WORD IS A SECOND SOLID. It fills a recess `WORD_DEPTH` into the chip's outboard face and
stands `WORD_RAISE` proud of it, printed in the second colour that reads against the chip's own —
`_y_wall_dimensions.word_color` is where light-on-dark or dark-on-light is decided. It stands in
the band above the flange, so the flange lands on the chip and never on a letter.

The push a 1/4" push-to-connect takes to seat — past the collet's grabbers and an EPDM O-ring —
lands on this chip, and the chip carries it to the pocket floor across its whole face.

Coordinate frame — THE FITTING'S, so `enclosure_assembly` seats one on a union's own station with
no turn of its own:
  Y = the fitting's flow axis. +Y = outboard, toward the customer's tube.
  Origin = the chip's INBOARD face, the one that lands on the pocket floor. The chip spans
      y = 0 to y = THICK, the flange lands on that far face, and the word stands to
      y = THICK + WORD_RAISE.
  +Z = up. X completes the right-handed frame, so from outside the machine — looking down −Y —
      +X runs to the LEFT and a word reads along −X.

It prints face up, two colours to a plate: the inboard face on the bed, the outboard face closing on
a layer boundary, and the letters standing in whole layers above it.

Run:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/bulkhead-ring/bulkhead_ring.py
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/bulkhead-ring/bulkhead_ring.py selftest
"""

import collections
import math
import sys
from pathlib import Path

import cadquery as cq
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts",
           _hw / "printed-parts" / "cadlib",
           _hw / "printed-parts" / "enclosure" / "enclosure",
           _hw / "printed-parts" / "enclosure" / "y-wall-of-back-top",
           _hw / "reference" / "jg-bulkhead-union",
           _hw / "reference" / "neofit-bulkhead",
           _hw / "reference" / "neofit-drain-bulkhead"):
    sys.path.insert(0, str(_p))
sys.path.insert(0, str(next(p for p in _here.parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_assembly, import_step  # noqa: E402
from _materials import step_safe
import _y_wall_dimensions as _rear  # noqa: E402
import jg_bulkhead_union as _jg  # noqa: E402
import neofit_drain_bulkhead as _drain
import neofit_bulkhead as _neo  # noqa: E402
import fits  # noqa: E402
import port_chip  # noqa: E402
import _enclosure_interface as _enc_interface  # noqa: E402
from docgen import substitute_md  # noqa: E402

# THREE FAMILIES OF FITTING CROSS THIS WALL, and a chip is struck on the flange it hides under and
# the barrel it passes — `union` for the PP1208E the water and umbilical ports use, `neofit` for
# the ABU44 the CO2 inlet takes, and the metric DRAIN fitting. All labels share one width.
FAMILIES = {"union": _jg, "neofit": _neo, "drain": _drain}

# How far the chip stands past the fitting's own panel footprint — the width of colour that shows
# once the flange is on. `enclosure_assembly.y_wall_field` strikes its pockets from it and
# `drawings/line-art/_appliance_model` paints its marks from it. A pocket is this chip plus its
# slip, and what one `enclosure_assembly.PORT_PITCH` leaves between two pockets is the web of wall
# the field keeps between them. It is also the band the word is lettered in, top and bottom.
RING_W = 7.05
# The chip's thickness. A fitting's flange bears this far outboard of the pocket floor, which is
# what `enclosure_assembly.bulkhead_seat_y` reads. The pocket is cut to this same depth, so the
# chip's face and the wall's come out one plane.
THICK = 2.0
# The slip a chip takes around the fitting's threading — the wall's own
# `enclosure_assembly.PORT_HOLE_SLIP`. The two modules cannot import each other, so
# `bulkhead-ring-bore` is what holds them equal.
SLIP = 2.0 * fits.slip
# Rectangle height above the water and flavour axes. `rise` adds the CO2 axis's drop so all
# three upper chips finish on the enclosure's top face, open above their pockets.
RISE = 18.789

# One chip per station: the family whose fitting it rings, the word it carries, and whether it
# stands on the top row and so runs out on the box's top face.
Chip = collections.namedtuple("Chip", "family word top_row")
STATIONS = {
    "water": Chip("union", "TAP", True),
    "carb": Chip("union", "SODA", True),
    "co2": Chip("neofit", "CO2", True),
    "flavor-a": Chip("union", "FLAVOR", False),
    "flavor-b": Chip("union", "FLAVOR", False),
    "drain": Chip("drain", "OVER", False),
}
# ONE FILE PER STATION, AND IT HOLDS BOTH BODIES. The part is one print in two filaments — a chip
# and the word standing in its recess — so the file is that pair, each body carrying the colour of
# the spool it comes off. A reader opening a station sees the part a customer meets; a slicer
# opening it gets the two bodies to assign. `split` is how the pair comes back apart.
STEPS = {name: _here.parent / f"bulkhead-ring-{name}.step" for name in STATIONS}

# The key each station reads its two filaments under in `_y_wall_dimensions` — both flavour
# chips print off one spool and letter in one colour, so both answer to `flavor`.
FLUIDS = {"water": "water", "carb": "carb", "co2": "co2",
          "flavor-a": "flavor", "flavor-b": "flavor", "drain": "drain"}

# Physical port labels use the typeface below. The cap-height and stroke-width
# checks establish its printed fit on the identification ring.
#   Bold is what the nozzle asks for. Every stroke is an extrusion of the word's own colour, laid
# at `WORD_BEAD`. `WORD_MIN_STROKE` is what this weight turns out to be worth at `WORD_CAP`,
# measured off the built letterforms rather than claimed, and `selftest` reads it against the bead.
WORD_FONT = "Helvetica"
WORD_KIND = "bold"
# The em the word is set at. `WORD_CAP` is what that turns out to be worth in cap height, which is
# the figure the band is actually spent on.
WORD_SIZE = 6.5
# How deep the word's recess is cut into the chip's outboard face — half the chip, so the colour
# behind the lettering is as thick as the lettering itself and neither side of the print is a skin.
WORD_DEPTH = 1.0
# HOW FAR THE WORD STANDS PROUD OF THAT FACE. Each letter fills its recess and runs on past the
# face as one solid, the last `WORD_RAISE` of the print in the word's colour alone — the
# nameplate's rise. A whole number of `WORD_LAYER`s, standing in the band above the flange.
WORD_RAISE = 0.48
# The PROFILE these slice under — `0.24mm PET-GF faucet`, the nameplate's, saved in its plate at
# `../nameplate/nameplate-001-petgf.3mf` — and the bead it asks for. Face up, the first layer is
# `WORD_FIRST_LAYER` and every layer after it `WORD_LAYER`, but for the one `closing_layer` that
# lands the outboard face on `THICK`, so the letters start on a layer boundary. The ORIFICE is
# `WORD_NOZZLE`; `WORD_BEAD` is the outer wall the profile lays, and it is what a slicer divides a
# feature by to decide how many perimeters fit in it. So it, and not the tip, is what a stroke is
# counted in.
WORD_FIRST_LAYER = 0.2
WORD_LAYER = 0.24
WORD_BEAD = 0.42
# What the built words measure across, and the tallest cap among them. The face is the SYSTEM'S and
# not this repo's, so a machine that resolves `WORD_FONT` to something else letters a different chip
# — and the only thing that catches it is a figure carried here and read back off the solid.
# `words_hold` is where that is read.
WORD_CAP = 4.951
WORD_WIDTHS = {"TAP": 12.657, "SODA": 18.411, "CO2": 12.813, "FLAVOR": 25.952, "OVER": 17.827}
# The narrowest stroke any of these words carries, taken off the built letterforms as twice a
# glyph face's area over its perimeter.
WORD_MIN_STROKE = 0.771
# AND THE NARROWEST BRIDGE — the chip standing between two letters in the recess, and the gap
# between their raised tops above it. This is FLAVOR's, between the L and the A: under one
# `WORD_BEAD`, laid as a single outer wall of chip up to the face, with the tops apart above it.
# It scales with `WORD_SIZE`.
WORD_MIN_BRIDGE = 0.346
# The tip these print through — one per filament, the hardened pair the nameplate's two colours
# come off.
WORD_NOZZLE = 0.4
# What the word keeps off the flange below it and the chip's own top edge above. The band is
# `RING_W` tall and the cap stands in the middle of it, so this is what is left either side.
WORD_MARGIN = 1.0


def ring_od(across: float) -> float:
    """The OD a chip takes on a fitting whose own panel footprint is `across`."""
    return across + 2.0 * RING_W


def family(which: str) -> str:
    """Which fitting family one station's chip is struck on."""
    return STATIONS[which].family


def od(fam: str) -> float:
    """The common width of all six labels, including the longest FLAVOR word."""
    return port_chip.WIDTH


def bottom(fam: str) -> float:
    """The bottom edge, at the flange envelope with no extra band below it."""
    return FAMILIES[fam].flange_footprint() / 2.0


def bore_d(fam: str) -> float:
    """Its bore — the hole the wall passes that family's own barrel through."""
    return FAMILIES[fam].panel_hole_d(SLIP)


def tall(which: str) -> float:
    """One station's rectangular chip height."""
    return bottom(family(which)) + rise(which)


def rise(which: str) -> float:
    """The chip's top datum relative to its own fitting axis."""
    return RISE + (_enc_interface.co2_axis_drop if which == "co2" else 0.0)


def outline(which: str) -> tuple:
    """One station's chip as `(od, rise)` — the pair that strikes both the chip and the pocket it
    drops into. `enclosure_assembly.y_wall_field` cuts its pockets from this."""
    return (od(family(which)), rise(which))


def seat() -> tuple:
    """The face a pocket takes it by: `(position, outward axis)` on the chip's INBOARD face,
    pointing at the wall. That face lands on the pocket's floor, one `THICK` inside the wall's own
    outer face — so the wall keeps its whole thickness under every chip, made back on the inboard
    side by the boss the field stands there."""
    return ((0.0, 0.0, 0.0), (0.0, -1.0, 0.0))


def build_outline(diameter: float, top: float, thick: float, y0: float = 0.0,
                  lower: float = None):
    """Common-width chip with R2 lower corners and a text band above the flange."""
    lower = diameter / 2.0 if lower is None else lower
    return port_chip.outline(diameter, top, lower, thick, y0)


def word_band(which: str) -> tuple:
    """The band a station's word is lettered in, as `(z_lo, z_hi)`: between the flange's own edge
    and the top of the chip. Everything inside the flange is hidden once the fitting is on, so this
    is the whole of what a customer can be shown."""
    chip = STATIONS[which]
    return (FAMILIES[chip.family].flange_footprint() / 2.0, rise(which))


def closing_layer() -> float:
    """The layer that lands the outboard face on `THICK`, face up: what is left of the chip over the
    first layer and every whole `WORD_LAYER` under the face. Zero when the face lands on a layer
    boundary of its own."""
    whole = math.floor((THICK - WORD_FIRST_LAYER) / WORD_LAYER + 1e-9)
    return round(THICK - WORD_FIRST_LAYER - whole * WORD_LAYER, 6)


def build_word(which: str):
    """One station's word — its letters, each filling its recess `WORD_DEPTH` deep and standing
    `WORD_RAISE` proud of the chip's outboard face, one solid from the recess floor to its own top.

    THE LETTERS ARE LOOSE, one solid each, and nothing joins them. They are placed by the print
    rather than by hand: the chip is opened as one part carrying both bodies and the lettering is
    assigned the second filament, so there is nothing to lay on a bed and nothing to lose off one.
    `_cadq_export._per_solid_color` writes each of them as its own component, so all six carry the
    colour into the viewer.

    TURNED TO FACE THE CUSTOMER. The text is set flat in XY and carried onto the wall's plane by
    two turns — a quarter about X to stand it up, then a half about Z — which leaves it extruding
    OUTBOARD with its cap up and its advance along −X, the way a word reads to someone standing
    behind the machine."""
    flat = cq.Workplane("XY").text(STATIONS[which].word, WORD_SIZE, WORD_DEPTH + WORD_RAISE,
                                   font=WORD_FONT, kind=WORD_KIND,
                                   halign="center", valign="center")
    letters = (flat.rotate((0, 0, 0), (1, 0, 0), 90.0)
                   .rotate((0, 0, 0), (0, 0, 1), 180.0).val())
    # `valign` centres on the font's own metrics and not on the cap box, so the cap is squared up
    # on the band here — off the solid that was actually built, which is also what a font that
    # resolved to something else would be caught by.
    bb = letters.BoundingBox()
    lo, hi = word_band(which)
    return letters.translate(cq.Vector(
        -(bb.xmin + bb.xmax) / 2.0,
        THICK - WORD_DEPTH - bb.ymin,
        (lo + hi) / 2.0 - (bb.zmin + bb.zmax) / 2.0))


def build_ring(which: str):
    """One station's chip: the outline, its bore, and the word's recess taken out of its face."""
    diameter, top = outline(which)
    chip = build_outline(diameter, top, THICK, lower=bottom(family(which)))
    chip = chip.cut(cq.Solid.makeCylinder(bore_d(family(which)) / 2.0, THICK,
                                          cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 1.0, 0.0)))
    return chip.cut(build_word(which))


def _filament(rgb) -> "cq.Color":
    return step_safe(cq.Color(*(c / 255.0 for c in rgb)))


def flange_clearance(which: str) -> float:
    """The nearest one station's word comes to its fitting's flange: the letters against the
    flange's own footprint, standing outboard of the chip's face alongside them."""
    flange = cq.Solid.makeCylinder(FAMILIES[family(which)].flange_footprint() / 2.0,
                                   WORD_RAISE + WORD_DEPTH, cq.Vector(0.0, THICK, 0.0),
                                   cq.Vector(0.0, 1.0, 0.0))
    word = build_word(which)
    if word.intersect(flange).Volume() > 1e-9:
        return 0.0
    probe = BRepExtrema_DistShapeShape(word.wrapped, flange.wrapped)
    probe.Perform()
    return probe.Value()


def build_part(which: str) -> cq.Assembly:
    """One station as it prints: the chip, and the word standing in its recess and proud of its
    face, each in the filament it comes off. Two bodies of one part, in the frame `seat` places them
    by."""
    a = cq.Assembly()
    a.add(build_ring(which), name=f"bulkhead-ring-{which}",
          color=_filament(_rear.chip_color(FLUIDS[which])))
    a.add(build_word(which), name=f"bulkhead-ring-{which}-word",
          color=_filament(_rear.word_color(FLUIDS[which])))
    return a


def split(shape) -> tuple:
    """A station's STEP back apart, as `(chip, word)`.

    The chip spans the whole of `THICK` and lands on the pocket's floor; the lettering stands in
    the recess and reaches nowhere near it. So the ONE body touching the seating face is the chip —
    the same face `seat` hands the wall — and every other body is a letter. Counting letters would
    tie this to the word each station happens to carry; reading the face does not."""
    solids = shape.Solids() if hasattr(shape, "Solids") else shape
    floor = [s for s in solids if abs(s.BoundingBox().ymin) < 1e-6]
    if len(floor) != 1 or len(solids) < 2:
        raise ValueError(
            f"a station's STEP is a chip and the letters lying in it, and this one carries "
            f"{len(solids)} {'body' if len(solids) == 1 else 'bodies'}, {len(floor)} of them on "
            f"the seating face")
    return (floor[0], cq.Compound.makeCompound([s for s in solids if s is not floor[0]]))


def min_stroke(word_solid) -> float:
    """The narrowest stroke a built word carries, off its own outboard faces.

    Twice a face's area over its perimeter: for a stroke of width w and run L that is 2wL/2L, so
    a letterform's thinnest limb is what the smallest of them reports."""
    out = []
    for f in word_solid.Faces():
        if abs(f.Center().y - (THICK + WORD_RAISE)) > 1e-6:
            continue
        perimeter = sum(e.Length() for e in f.Edges())
        if perimeter > 0:
            out.append(2.0 * f.Area() / perimeter)
    return min(out) if out else 0.0


def words_hold():
    """Hold the lettering to the figures carried here, off the built solids.

    THE FONT IS THE SYSTEM'S. `WORD_FONT` names a face this repo does not ship, so a machine that
    resolves it to something else letters a chip that is a different part — same colour, same
    outline, different word entirely. Nothing about that shows up in a bore or an extent, which is
    why every word's width is carried in `WORD_WIDTHS` and read back off the solid here."""
    for which, step in STEPS.items():
        word = STATIONS[which].word
        _chip, solid = split(import_step(str(step)).val())
        bb = solid.BoundingBox()
        if abs(bb.xlen - WORD_WIDTHS[word]) > 1e-3:
            raise ValueError(
                f"'{word}' is declared {WORD_WIDTHS[word]:.3f} mm across and {step.name} carries "
                f"{bb.xlen:.3f} — `{WORD_FONT}` did not resolve to the face these figures were "
                f"struck on, and the chip is lettered in something else.")


def selftest() -> int:
    """Each chip against the fitting it rings, the wall that pockets it, and the word it carries."""
    fails = []
    for which, chip in STATIONS.items():
        fitting = FAMILIES[chip.family]
        flange = fitting.flange_footprint()
        if od(chip.family) <= flange:
            fails.append(f"a {which} chip of Ø{od(chip.family):g} shows nothing past a "
                         f"Ø{flange:g} flange")
        if bore_d(chip.family) <= fitting.THREAD_D:
            fails.append(
                f"the {which} chip's bore Ø{bore_d(chip.family):g} does not pass the fitting's "
                f"own Ø{fitting.THREAD_D:g} barrel")
        lo, hi = word_band(which)
        if hi - lo < WORD_CAP + 2.0 * WORD_MARGIN - 1e-9:
            fails.append(
                f"the {which} chip letters a {WORD_CAP:g} mm cap in a band {hi - lo:.3f} mm tall "
                f"and owes {WORD_MARGIN:g} mm either side of it")
        room = od(chip.family) - 2.0 * WORD_MARGIN
        if WORD_WIDTHS[chip.word] > room + 1e-9:
            fails.append(
                f"'{chip.word}' runs {WORD_WIDTHS[chip.word]:.3f} mm across a {which} chip that "
                f"leaves {room:.3f} mm between its own margins")
    if THICK >= _jg.THREAD_LEN:
        fails.append(
            f"a chip {THICK:g} thick stands in the {_jg.THREAD_LEN:g} mm of thread the union "
            f"has, and leaves none of it for the nut")
    if THICK >= _neo.PANEL_THREAD:
        fails.append(
            f"a chip {THICK:g} thick stands in the {_neo.PANEL_THREAD:.2f} mm of barrel the "
            f"ABU44 offers outboard of its flange, and leaves none of it for the wall")
    if WORD_DEPTH >= THICK:
        fails.append(
            f"a word {WORD_DEPTH:g} deep is cut through a chip {THICK:g} thick, and what is "
            f"behind the lettering is the pocket floor rather than the colour")
    if WORD_MIN_STROKE < WORD_BEAD + 1e-9:
        fails.append(
            f"the narrowest stroke these words carry is {WORD_MIN_STROKE:.3f} mm and the profile "
            f"lays a {WORD_BEAD:g} bead — a stroke under one bead wide is not one the slicer can lay")
    layers = WORD_RAISE / WORD_LAYER
    if abs(layers - round(layers)) > 1e-9 or round(layers) < 1:
        fails.append(
            f"a word {WORD_RAISE:g} proud stands in {layers:.3f} layers of {WORD_LAYER:g} — its "
            f"top is not a layer the profile lays")
    if not 0.0 <= closing_layer() < WORD_LAYER:
        fails.append(
            f"the face closes on a {closing_layer():g} mm layer, outside one {WORD_LAYER:g} layer")
    for which in STATIONS:
        clear = flange_clearance(which)
        if clear < WORD_MARGIN - 1e-6:
            fails.append(
                f"'{STATIONS[which].word}' stands {clear:.3f} mm off the {family(which)} flange "
                f"and owes it {WORD_MARGIN:g} mm")
    for which in STATIONS:
        got = min_stroke(build_word(which))
        if abs(got - WORD_MIN_STROKE) > 1e-3 and got < WORD_MIN_STROKE:
            fails.append(
                f"'{STATIONS[which].word}' carries a {got:.3f} mm stroke and `WORD_MIN_STROKE` "
                f"claims {WORD_MIN_STROKE:.3f} is the narrowest of them")
    try:
        words_hold()
    except Exception as exc:                                     # noqa: BLE001
        fails.append(str(exc))
    for line in fails:
        print(f"FAIL {line}")
    if not fails:
        print("ok  bulkhead-ring  " + ", ".join(
            f"{w} {STATIONS[w].word} Ø{od(family(w)):g}×{tall(w):.3f}"
            for w in STATIONS)
            + f" × {THICK:g}, {RING_W:g} mm of colour past each flange")
    return 1 if fails else 0


def main():
    volumes, word_volumes, clears = {}, {}, {}
    for which in STATIONS:
        chip, word = build_ring(which), build_word(which)
        diameter, top = outline(which)
        volumes[which] = chip.Volume() / 1000.0
        word_volumes[which] = word.Volume() / 1000.0
        bb = chip.BoundingBox()
        print(f"Bulkhead ring — {which} station, '{STATIONS[which].word}'")
        print(f"  Ø{diameter:g} wide × {tall(which):.3f} tall / "
              f"bore Ø{bore_d(family(which)):g} / thickness {THICK:g}")
        print(f"  Colour showing past the flange: {RING_W:g} mm")
        print(f"  Canonical-frame bounding box: "
              f"X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
              f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
              f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
        print(f"  Solid valid: {chip.isValid()}")
        clears[which] = flange_clearance(which)
        print(f"  Word: {WORD_DEPTH:g} deep, {WORD_RAISE:g} proud, top at y = "
              f"{THICK + WORD_RAISE:g}; {clears[which]:.3f} mm off the flange")
        export_assembly(build_part(which), str(STEPS[which]))
        print(f"-> {STEPS[which].name}")

    variables = {
        "RING_W": f"{RING_W:g}",
        "RING_THICK": f"{THICK:g}",
        "RING_OD": f"{od('union'):g}",
        "RING_LOWER_RADIUS": f"{port_chip.LOWER_CORNER_RADIUS:g}",
        "RING_BORE": f"{bore_d('union'):g}",
        "RING_VOL": f"{volumes['flavor-a']:.2f}",
        "RING_TALL": f"{tall('flavor-a'):.2f}",
        "RING_RISE": f"{RISE:g}",
        "CO2_RING_RISE": f"{rise('co2'):g}",
        "CO2_AXIS_DROP": f"{_enc_interface.co2_axis_drop:g}",
        "CO2_RING_OD": f"{od('neofit'):.2f}",
        "CO2_RING_BORE": f"{bore_d('neofit'):g}",
        "CO2_RING_TALL": f"{tall('co2'):.2f}",
        "CO2_RING_VOL": f"{volumes['co2']:.2f}",
        "WORD_FONT": WORD_FONT,
        "WORD_KIND": WORD_KIND,
        "WORD_CAP": f"{WORD_CAP:g}",
        "WORD_DEPTH": f"{WORD_DEPTH:g}",
        "WORD_RAISE": f"{WORD_RAISE:g}",
        "WORD_TOP": f"{THICK + WORD_RAISE:g}",
        "WORD_RAISE_LAYERS": f"{round(WORD_RAISE / WORD_LAYER):d}",
        "WORD_FIRST_LAYER": f"{WORD_FIRST_LAYER:g}",
        "WORD_CLOSING_LAYER": f"{closing_layer():g}",
        "WORD_FLANGE_CLEAR": f"{min(c for w, c in clears.items() if family(w) == 'union'):.2f}",
        "CO2_WORD_FLANGE_CLEAR": f"{clears['co2']:.2f}",
        "WORD_LAYER": f"{WORD_LAYER:g}",
        "WORD_BEAD": f"{WORD_BEAD:g}",
        "WORD_MIN_STROKE": f"{WORD_MIN_STROKE:g}",
        "WORD_MIN_BRIDGE": f"{WORD_MIN_BRIDGE:g}",
        "WORD_NOZZLE": f"{WORD_NOZZLE:g}",
        "WORD_VOL": f"{word_volumes['flavor-a']:.2f}",
    }
    substitute_md(_here.parent / "README.md", variables=variables,
)
    print("-> README.md")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main()
