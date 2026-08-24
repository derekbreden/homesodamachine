"""Bulkhead ring — the colour and the word one of the +Y wall of back-top's connections is
read by.

A flat chip lying in a pocket of that wall's outer face, with a through-wall fitting's own
flange landing on it. Nothing fastens it: the fitting's nut makes up on the inboard side and draws
flange, chip and wall together, so the chip is in the clamped stack the way the wall is. The pocket
is the chip's own thickness deep, so the two faces come out one plane.

    RING_W    how far a chip stands past the fitting's own flange, and so the width of colour that
              shows once the flange is on. The wall strikes its pockets from it, the iso line-art
              paints its marks from it, and it is the band the word is lettered in
    THICK     the chip's thickness, the depth the pocket is cut to, and — because the wall keeps
              its own full stock under every chip — the height of the boss the wall stands inboard

THE OUTLINE IS A D ON ITS BACK. Below the bore's axis it is a half circle, the shape the port
itself is; above it a rectangle, and the corners that adds are the room the lettering stands in.
It is not a shape that turns — a pocket takes it one way up and no other, which is what puts the
word level without anything holding it there.

At the rear face the customer meets identical black fittings in a black wall, one of which takes
the blue tube — `../y-wall-of-back-top/README.md` §"Umbilical port — tube identification". A chip's colour
is its tube's colour and there are four of them; what a colour means is stated once, in
`../y-wall-of-back-top/_y_wall_dimensions.py`.

THE WORD IS A SECOND SOLID. It lies in a recess `WORD_DEPTH` into the chip's outboard face and
fills it flush, printed in the second colour that reads against the chip's own —
`_y_wall_dimensions.word_color` is where light-on-dark or dark-on-light is decided.

The push a 1/4" push-to-connect takes to seat — past the collet's grabbers and an EPDM O-ring —
lands on this chip, and the chip carries it to the pocket floor across its whole face.

Coordinate frame — THE FITTING'S, so `enclosure_assembly` seats one on a union's own station with
no turn of its own:
  Y = the fitting's flow axis. +Y = outboard, toward the customer's tube.
  Origin = the chip's INBOARD face, the one that lands on the pocket floor. The chip spans
      y = 0 to y = THICK, and the flange lands on that far face.
  +Z = up. X completes the right-handed frame, so from outside the machine — looking down −Y —
      +X runs to the LEFT and a word reads along −X.

It prints flat, many to a bed, two colours to a plate.

Run:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/bulkhead-ring/bulkhead_ring.py
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/bulkhead-ring/bulkhead_ring.py selftest
"""

import collections
import sys
from pathlib import Path

import cadquery as cq
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts",
           _hw / "printed-parts" / "cadlib",
           _hw / "printed-parts" / "enclosure" / "y-wall-of-back-top",
           _hw / "reference" / "jg-bulkhead-union",
           _hw / "reference" / "neofit-bulkhead"):
    sys.path.insert(0, str(_p))
sys.path.insert(0, str(next(p for p in _here.parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_assembly, import_step  # noqa: E402
from _materials import step_safe
from _measuring import bores  # noqa: E402
import _y_wall_dimensions as _rear  # noqa: E402
import jg_bulkhead_union as _jg  # noqa: E402
import neofit_bulkhead as _neo  # noqa: E402
from docgen import substitute_md  # noqa: E402

# TWO FAMILIES OF FITTING CROSS THIS WALL, and a chip is struck on the flange it hides under and
# the barrel it passes — `union` for the PP1208E the water and umbilical ports use, `neofit` for
# the ABU44 the CO2 inlet takes. `RING_W` and `THICK` are the same for both.
FAMILIES = {"union": _jg, "neofit": _neo}

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
SLIP = 0.86
# HOW FAR THE RECTANGLE STANDS ABOVE THE AXIS, on every chip. The figure is the top row's own
# storey read to the box's top face, so those three run out FLUSH with it — fenced left, right and
# below, open above. The bottom row rises the same, which is what makes a chip on one family one
# height wherever it stands and puts every word in the same band over its own bore.
# `bulkhead-ring-top-row` reads it back against the box, because the two modules cannot import each
# other.
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
}
# ONE FILE PER STATION, AND IT HOLDS BOTH BODIES. The part is one print in two filaments — a chip
# and the word lying in its recess — so the file is that pair, each body carrying the colour of the
# spool it comes off. A reader opening a station sees the part a customer meets; a slicer opening
# it gets the two bodies to assign. `split` is how the pair comes back apart.
STEPS = {name: _here.parent / f"bulkhead-ring-{name}.step" for name in STATIONS}

# The key each station reads its two filaments under in `_y_wall_dimensions` — both flavour
# chips print off one spool and letter in one colour, so both answer to `flavor`.
FLUIDS = {"water": "water", "carb": "carb", "co2": "co2",
          "flavor-a": "flavor", "flavor-b": "flavor"}

# THE FACE THE REST OF THE MACHINE'S PAPER IS SET IN. `assembly/cards/style.css` sets the build
# deck's `--sans` to it and `quickstart/style.css` sets the customer's sheets in it — and those
# sheets point at these very ports. A customer holding one beside the machine reads one typeface,
# not two. (The web surface's Montserrat is a
# webfont, not installed, and nothing physical is set in it.)
#   Bold is what the nozzle asks for. Every stroke is an extrusion of the word's own colour and
# every counter and gap is an extrusion of the chip's, so both are held over the nozzle's width.
# `WORD_MIN_STROKE` is what this weight turns out to be worth at `WORD_CAP`, measured off the built
# letterforms rather than claimed, and `word-stroke` reads it against the tip.
WORD_FONT = "Helvetica"
WORD_KIND = "bold"
# The em the word is set at. `WORD_CAP` is what that turns out to be worth in cap height, which is
# the figure the band is actually spent on.
WORD_SIZE = 6.5
# How deep the word's recess is cut into the chip's outboard face — half the chip, so the colour
# behind the lettering is as thick as the lettering itself and neither side of the print is a skin.
WORD_DEPTH = 1.0
# The PROFILE these slice under — `0.08mm High Quality @BBL H2C 0.2 nozzle`, saved in the plate at
# `bulkhead-ring-water.3mf` — and the bead it asks for. The ORIFICE is `WORD_NOZZLE`; this is the width
# the profile lays at, and it is what a slicer divides a feature by to decide how many perimeters
# fit in it. So it, and not the tip, is what a stroke and a bridge are counted in.
WORD_LAYER = 0.08
WORD_BEAD = 0.22
# What the built words measure across, and the tallest cap among them. The face is the SYSTEM'S and
# not this repo's, so a machine that resolves `WORD_FONT` to something else letters a different chip
# — and the only thing that catches it is a figure carried here and read back off the solid.
# `words_hold` is where that is read.
WORD_CAP = 4.951
WORD_WIDTHS = {"TAP": 12.657, "SODA": 18.411, "CO2": 12.813, "FLAVOR": 25.952}
# The narrowest stroke any of these words carries, taken off the built letterforms as twice a
# glyph face's area over its perimeter.
WORD_MIN_STROKE = 0.771
# AND THE NARROWEST BRIDGE — the chip standing between two letters, which is the finer of the two
# features by more than a factor of two. A stroke is the word's spool and a bridge is the chip's,
# but both are laid at `WORD_BEAD` through the same tip, so the bridge is what runs out first. This
# is FLAVOR's, between the L and the A. It scales with `WORD_SIZE`, so it is also the floor under
# how small this lettering can be set.
WORD_MIN_BRIDGE = 0.346
# The tip these print through. The chips are the machine's first two-colour print and its finest
# work; everything else in the box runs 0.4 and up (`ledger/machine-time.md`).
WORD_NOZZLE = 0.2
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
    """One family's chip OD — its width, and the diameter of the half circle below the axis."""
    return ring_od(FAMILIES[fam].flange_footprint())


def bore_d(fam: str) -> float:
    """Its bore — the hole the wall passes that family's own barrel through."""
    return FAMILIES[fam].panel_hole_d(SLIP)


def tall(which: str) -> float:
    """One station's chip top to bottom: its own half circle below the axis, `RISE` above."""
    return od(family(which)) / 2.0 + RISE


def outline(which: str) -> tuple:
    """One station's chip as `(od, rise)` — the pair that strikes both the chip and the pocket it
    drops into. `enclosure_assembly.y_wall_field` cuts its pockets from this."""
    return (od(family(which)), RISE)


def seat() -> tuple:
    """The face a pocket takes it by: `(position, outward axis)` on the chip's INBOARD face,
    pointing at the wall. That face lands on the pocket's floor, one `THICK` inside the wall's own
    outer face — so the wall keeps its whole thickness under every chip, made back on the inboard
    side by the boss the field stands there."""
    return ((0.0, 0.0, 0.0), (0.0, -1.0, 0.0))


def build_outline(diameter: float, top: float, thick: float, y0: float = 0.0):
    """The D on its back, as a solid spanning `y0` to `y0 + thick`: a half circle of `diameter`
    below the axis and a rectangle that wide standing `top` above it.

    Struck from primitives rather than sketched, so no plane's own chirality reaches the shape —
    the half circle is a cylinder with everything above the axis taken off it, and the rectangle is
    a box standing on that same axis."""
    r = diameter / 2.0
    barrel = cq.Solid.makeCylinder(r, thick, cq.Vector(0.0, y0, 0.0), cq.Vector(0.0, 1.0, 0.0))
    below = cq.Solid.makeBox(diameter, thick, r, cq.Vector(-r, y0, -r))
    above = cq.Solid.makeBox(diameter, thick, top, cq.Vector(-r, y0, 0.0))
    return barrel.intersect(below).fuse(above)


def word_band(which: str) -> tuple:
    """The band a station's word is lettered in, as `(z_lo, z_hi)`: between the flange's own edge
    and the top of the chip. Everything inside the flange is hidden once the fitting is on, so this
    is the whole of what a customer can be shown."""
    chip = STATIONS[which]
    return (FAMILIES[chip.family].flange_footprint() / 2.0, RISE)


def build_word(which: str):
    """One station's word — its letters, standing in the recess they fill, `WORD_DEPTH` deep with
    their outboard faces flush with the chip's own.

    THE LETTERS ARE LOOSE, one solid each, and nothing joins them. They are placed by the print
    rather than by hand: the chip is opened as one part carrying both bodies and the lettering is
    assigned the second filament, so there is nothing to lay on a bed and nothing to lose off one.
    `_cadq_export._per_solid_color` writes each of them as its own component, so all six carry the
    colour into the viewer.

    TURNED TO FACE THE CUSTOMER. The text is set flat in XY and carried onto the wall's plane by
    two turns — a quarter about X to stand it up, then a half about Z — which leaves it extruding
    OUTBOARD with its cap up and its advance along −X, the way a word reads to someone standing
    behind the machine."""
    flat = cq.Workplane("XY").text(STATIONS[which].word, WORD_SIZE, WORD_DEPTH,
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
    chip = build_outline(diameter, top, THICK)
    chip = chip.cut(cq.Solid.makeCylinder(bore_d(family(which)) / 2.0, THICK,
                                          cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 1.0, 0.0)))
    return chip.cut(build_word(which))


def _filament(rgb) -> "cq.Color":
    return step_safe(cq.Color(*(c / 255.0 for c in rgb)))


def build_part(which: str) -> cq.Assembly:
    """One station as it prints: the chip, and the word lying in its recess, each in the filament
    it comes off. Two bodies of one part, in the frame `seat` places them by."""
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


def stations_hold():
    """Hold the figures the wall and the drawings read to each chip's own STEP.

    The width and the height are extents of that solid, the thickness its run along the axis, and
    the bore a turned face inside it — so a chip exported from different numbers is caught here
    rather than by a pocket it will not drop into."""
    for which, step in STEPS.items():
        solid, _word = split(import_step(str(step)).val())
        bb = solid.BoundingBox()
        diameter, top = outline(which)
        for what, claimed, actual in (("chip width", diameter, bb.xlen),
                                      ("chip height", diameter / 2.0 + top, bb.zlen),
                                      ("chip thickness", THICK, bb.ylen)):
            if abs(claimed - actual) > 1e-6:
                raise ValueError(
                    f"bulkhead-ring {which} {what} is {claimed:g} and {step.name} carries "
                    f"{actual:.4f} — a wall pocketed to the declared figure does not take the "
                    f"chip that is there.")
        radii = sorted({r for _axis, r in bores(solid)})
        want = bore_d(family(which))
        if not any(abs(2.0 * r - want) <= 1e-6 for r in radii):
            raise ValueError(
                f"the {which} chip's bore is declared Ø{want:g} and {step.name} turns no face at "
                f"that diameter — it carries Ø{[round(2 * r, 3) for r in radii]}. A chip bored "
                f"under the wall's own figure closes on the barrel the wall passes.")


def min_stroke(word_solid) -> float:
    """The narrowest stroke a built word carries, off its own outboard faces.

    Twice a face's area over its perimeter: for a stroke of width w and run L that is 2wL/2L, so
    a letterform's thinnest limb is what the smallest of them reports."""
    out = []
    for f in word_solid.Faces():
        if abs(f.Center().y - THICK) > 1e-6:
            continue
        perimeter = sum(e.Length() for e in f.Edges())
        if perimeter > 0:
            out.append(2.0 * f.Area() / perimeter)
    return min(out) if out else 0.0


def min_bridge(which: str) -> float:
    """The narrowest bridge of CHIP one station's word leaves standing between two letters.

    Measured between the letterforms before the tie fuses them, which is where the gap is a gap:
    the pair nearest each other across the word's advance. `build_word` sets the same text at the
    same size, so a font that resolves elsewhere is read here too."""
    flat = cq.Workplane("XY").text(STATIONS[which].word, WORD_SIZE, WORD_DEPTH,
                                   font=WORD_FONT, kind=WORD_KIND,
                                   halign="center", valign="center").val()
    letters = sorted(flat.Solids(), key=lambda s: s.BoundingBox().xmin)
    gaps = []
    for a, b in zip(letters, letters[1:]):
        probe = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
        probe.Perform()
        gaps.append(probe.Value())
    return min(gaps) if gaps else 0.0


def words_hold():
    """Hold the lettering to the figures carried here, off the built solids.

    THE FONT IS THE SYSTEM'S. `WORD_FONT` names a face this repo does not ship, so a machine that
    resolves it to something else letters a chip that is a different part — same colour, same
    outline, different word entirely. Nothing about that shows up in a bore or an extent, which is
    why every word's width is carried in `WORD_WIDTHS` and read back off the solid here.

    AND EVERY LETTER IS ITS OWN SOLID. Nothing joins them and nothing needs to: the chip is opened
    as one part carrying both bodies and the lettering takes the second filament, so a word is a
    count of letters rather than a thing to keep together.

    AND THE CHIP BETWEEN THE LETTERS is read the same way. A face that resolves elsewhere moves the
    bridges as surely as it moves the widths, and the bridge is the finer feature of the two."""
    for which, step in STEPS.items():
        word = STATIONS[which].word
        _chip, solid = split(import_step(str(step)).val())
        bb = solid.BoundingBox()
        if len(solid.Solids()) != len(word):
            raise ValueError(
                f"'{word}' is {len(solid.Solids())} solids in {step.name} and the word is "
                f"{len(word)} letters — the lettering is not the word it is declared to be.")
        got = min_bridge(which)
        if abs(got - WORD_MIN_BRIDGE) > 1e-3 and got < WORD_MIN_BRIDGE:
            raise ValueError(
                f"'{word}' leaves a {got:.3f} mm bridge of chip between two of its letters and "
                f"`WORD_MIN_BRIDGE` claims {WORD_MIN_BRIDGE:.3f} is the narrowest — the lettering "
                f"is set finer than these figures were measured at.")
        if abs(bb.xlen - WORD_WIDTHS[word]) > 1e-3:
            raise ValueError(
                f"'{word}' is declared {WORD_WIDTHS[word]:.3f} mm across and {step.name} carries "
                f"{bb.xlen:.3f} — `{WORD_FONT}` did not resolve to the face these figures were "
                f"struck on, and the chip is lettered in something else.")
        if abs(bb.ylen - WORD_DEPTH) > 1e-6:
            raise ValueError(
                f"'{word}' runs {bb.ylen:.4f} mm deep and the recess cut for it is "
                f"{WORD_DEPTH:g} — the word and the chip do not come out one plane.")


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
        if RISE < od(chip.family) / 2.0 - 1e-9:
            fails.append(
                f"the {which} chip rises {RISE:.3f} mm over an axis its own half circle reaches "
                f"{od(chip.family) / 2.0:.3f} mm below — the rectangle does not close on the "
                f"circle and the outline is not one shape")
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
    # BOTH FEATURES ARE COUNTED IN BEADS, and the bridge is the one that runs out first — a stroke
    # is the word's spool and a bridge is the chip's, but the same tip lays both at `WORD_BEAD`.
    for what, got in (("stroke these words carry", WORD_MIN_STROKE),
                      ("bridge of chip they leave standing", WORD_MIN_BRIDGE)):
        if got < WORD_BEAD + 1e-9:
            fails.append(
                f"the narrowest {what} is {got:.3f} mm and the profile lays a {WORD_BEAD:g} bead — "
                f"a feature under one bead wide is not a feature the slicer can fill")
    for which in STATIONS:
        got = min_stroke(build_word(which))
        if abs(got - WORD_MIN_STROKE) > 1e-3 and got < WORD_MIN_STROKE:
            fails.append(
                f"'{STATIONS[which].word}' carries a {got:.3f} mm stroke and `WORD_MIN_STROKE` "
                f"claims {WORD_MIN_STROKE:.3f} is the narrowest of them")
    for what, fn in (("stations_hold", stations_hold), ("words_hold", words_hold)):
        try:
            fn()
        except Exception as exc:                                 # noqa: BLE001
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
    volumes, word_volumes = {}, {}
    for which in STATIONS:
        chip, word = build_ring(which), build_word(which)
        diameter, top = outline(which)
        volumes[which] = chip.Volume() / 1000.0
        word_volumes[which] = word.Volume() / 1000.0
        bb = chip.BoundingBox()
        print(f"Bulkhead ring — {which} station, '{STATIONS[which].word}'")
        print(f"  Ø{diameter:g} wide × {diameter / 2.0 + top:.3f} tall / "
              f"bore Ø{bore_d(family(which)):g} / thickness {THICK:g}")
        print(f"  Colour showing past the flange: {RING_W:g} mm")
        print(f"  Canonical-frame bounding box: "
              f"X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
              f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
              f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
        print(f"  Solid valid: {chip.isValid()}")
        export_assembly(build_part(which), str(STEPS[which]))
        print(f"-> {STEPS[which].name}")

    variables = {
        "RING_W": f"{RING_W:g}",
        "RING_THICK": f"{THICK:g}",
        "RING_OD": f"{od('union'):g}",
        "RING_BORE": f"{bore_d('union'):g}",
        "RING_VOL": f"{volumes['flavor-a']:.2f}",
        "RING_TALL": f"{tall('flavor-a'):.2f}",
        "RING_RISE": f"{RISE:g}",
        "CO2_RING_OD": f"{od('neofit'):.2f}",
        "CO2_RING_BORE": f"{bore_d('neofit'):g}",
        "CO2_RING_TALL": f"{tall('co2'):.2f}",
        "CO2_RING_VOL": f"{volumes['co2']:.2f}",
        "WORD_FONT": WORD_FONT,
        "WORD_KIND": WORD_KIND,
        "WORD_CAP": f"{WORD_CAP:g}",
        "WORD_DEPTH": f"{WORD_DEPTH:g}",
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
