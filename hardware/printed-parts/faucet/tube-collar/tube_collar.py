"""Tube collar — the bulkhead ring's word and colour, carried on the tube.

`../../enclosure/bulkhead-ring/` marks the wall: a chip lying in a pocket of the back face, under a through-wall
fitting's flange, in the colour of the tube that goes into it. This is that chip bored for the tube
instead of for the fitting's barrel, run along it, and turned a quarter so the word reads down the
run. Same four colours, same five words, same two-filament print.

    THE OUTLINE IS THE CHIP'S — a half circle below the bore's axis and a rectangle above it,
    `RISE` tall over an OD twice that. It is not a shape that turns: the flat lies one way up and
    the word stands level on it without anything holding it there.

THE BORE IS CLOSED AND SLIPS OVER THE TUBE, and the collar threads on end-first, over a tail that
is still bare. `assembly/faucet-and-umbilical.md` §1 cuts the umbilical's three tubes and §3 sleeves
them; the collars go on at §4, up to the braid's own end. The tap run and the CO2 tether ship
made up in the install kit, and their collars go on at `assembly/finish-pack-ship.md` §6.

THE LENGTH IS THE BORE'S. `rock()` is the angle a collar can cock on its loosest tube — a bore of
length L with diametral play c binds at two diagonal corners, leaving atan(c/L) — and `flag_sway()`
carries that angle out to the word's face, the furthest anything on the collar stands from the line
it would turn about. `selftest` reads both against `bulkhead_ring.THICK`, which is the same
identification carried on a chip.

Coordinate frame — THE TUBE'S, the same one `bulkhead_ring` gives the fitting:
  Y = the tube's axis. +Y = outboard, toward the free end and the customer.
  Origin = the collar's INBOARD end face; it spans y = 0 to y = LENGTH.
  +Z = up, the way the flag stands. X completes the right-handed frame.

It prints flat-face down, many to a bed, two colours to a plate.

Run:
    tools/cad-venv/bin/python hardware/printed-parts/faucet/tube-collar/tube_collar.py
    tools/cad-venv/bin/python hardware/printed-parts/faucet/tube-collar/tube_collar.py selftest
"""

import collections
import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts",
           _hw / "printed-parts" / "enclosure" / "y-wall-of-back-top",
           _hw / "printed-parts" / "enclosure" / "bulkhead-ring"):
    sys.path.insert(0, str(_p))
sys.path.insert(0, str(next(p for p in _here.parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_assembly, import_step  # noqa: E402
from _materials import step_safe  # noqa: E402
from _measuring import bores  # noqa: E402
import _y_wall_dimensions as _rear  # noqa: E402
import bulkhead_ring as _ring  # noqa: E402
from docgen import substitute_md  # noqa: E402

# THE ONE TUBE SIZE ON THIS MACHINE. Every line the customer meets is 1/4" OD LLDPE, off one of the
# four neoFlo spools in `ledger/bom.md` §3. It is the nominal and not a bench figure: the tube on
# the bench calipers Ø6.5, which is the top of the band below.
TUBE_OD = 6.35
# What 1/4" OD LLDPE holds its diameter to on the spool. THE BORE IS SIZED OFF THE TOP OF THAT BAND
# and not off the nominal — a spool running high is the tube a collar still has to go onto, and one
# running low only leaves play. `clearance()` and `rock()` are the answers about the low end.
LLDPE_TOL = 0.13
# WHAT THE PRINTER TAKES OFF THE BORE'S DIAMETER, calipered on a finished collar. It lies flat face
# down with the bore's axis along the bed, so the hole's crown is unsupported and sags into it.
# `BORE` is the figure the slicer is handed; `bore_printed()` is the one the tube meets.
BORE_SHRINK = 0.10
# AND WHAT IS LEFT OVER THE BIGGEST TUBE once the sag has had it. `LENGTH` of bore turns any
# interference at all into a collar that goes on with a mallet or not at all, and this one goes on
# by hand over a bare tail. What holds it where it is put is the bend the tube came off the spool
# with: 1/4" LLDPE is never straight through `LENGTH` of bore and stands against the wall at both
# ends of one.
SLIP = 0.15
# THE BORE, AS THE SLICER IS HANDED IT: the top of the tube's band, the sag, and the slip.
BORE = TUBE_OD + LLDPE_TOL + BORE_SHRINK + SLIP
# The collar's width, and the diameter of the half circle below the axis. It leaves a `wall()` of
# colour between the bore and each of the three flats.
OD = 12.0
# HOW FAR THE RECTANGLE STANDS ABOVE THE AXIS, and so how tall the two side flats are. It is
# `bulkhead_ring.RING_W` — the band a chip letters its own word in, between the flange's edge and the
# top of the chip — so a word stands in one band whether it is read off the wall or off the tube.
RISE = _ring.RING_W
# THE RUN ALONG THE TUBE. It is the longest of the five words plus its margins, set at
# `bulkhead_ring.WORD_SIZE` — the wall's lettering and the tube's are one size, and `selftest` holds
# this to it.
LENGTH = 30.0
# How deep the word's recess is cut into the flat, and what the flat keeps clear of it. Both are
# `bulkhead_ring`'s.
WORD_DEPTH = _ring.WORD_DEPTH
WORD_MARGIN = _ring.WORD_MARGIN

# ONE COLLAR PER CHIP. The five keys are `bulkhead_ring.STATIONS`' own, and each takes its word and its
# spool from the chip at that station — a word changed on the wall is changed on the tube by the
# same edit.
#
# WHICH TUBE EACH ONE RIDES, and the bench that threads it on.
Collar = collections.namedtuple("Collar", "word fluid tube fitted")
STATIONS = {
    which: Collar(_ring.STATIONS[which].word, _ring.FLUIDS[which], tube, fitted)
    for which, tube, fitted in (
        ("water", "the customer's tap-water run, up to their angle stop", "pack bench"),
        ("carb", "the umbilical's blue carbonated-water tail", "faucet bench"),
        ("co2", "the customer's red tether, +Y wall of back-top to regulator", "pack bench"),
        ("flavor-a", "the umbilical's first black flavour tail", "faucet bench"),
        ("flavor-b", "the umbilical's second black flavour tail", "faucet bench"),
    )
}
# ONE FILE PER STATION, AND IT HOLDS BOTH BODIES — `bulkhead_ring.STEPS`' construction. The part is one
# print in two filaments, a collar and the word lying in its recess, and the file is that pair.
STEPS = {name: _here.parent / f"tube-collar-{name}.step" for name in STATIONS}


def bore_printed() -> float:
    """The bore a caliper reads on a finished collar, and the one the tube is threaded into —
    `BORE` less what the crown's sag takes back out of it."""
    return BORE - BORE_SHRINK


def wall() -> float:
    """The colour standing between the bore and a side flat, which is the thinnest the collar gets —
    the round below the axis stands the same off it and the top flat stands `RISE` off, further."""
    return (OD - BORE) / 2.0


def backing() -> float:
    """The colour left under the word's recess, between its floor and the bore's crown. `selftest`
    reads it against `WORD_DEPTH`."""
    return wall() - WORD_DEPTH


def reach() -> float:
    """The furthest a collar stands from its own tube's axis — the top flat's corners, and whichever
    way the flag is turned they are what sweeps. Two collars on neighbouring tubes clear when the
    axes are further apart than the two of them reach."""
    return math.hypot(OD / 2.0, RISE)


def clearance() -> float:
    """The diametral play a collar has on the loosest tube its spool runs — the printed bore over
    an extrusion at the low end of `LLDPE_TOL`.

    On one at the high end it is `SLIP`, which is the figure the bore is sized to leave and the
    tightest a collar comes out. Everything below is a tube that ran under nominal."""
    return bore_printed() - (TUBE_OD - LLDPE_TOL)


def rock() -> float:
    """The angle a collar can cock on that tube, in degrees. A bore of length L with diametral play
    c binds at two diagonal corners, leaving atan(c/L)."""
    return math.degrees(math.atan2(clearance(), LENGTH))


def flag_sway() -> float:
    """That angle carried out to the flag's face, at `RISE` off the axis — the furthest anything on
    the collar stands from the line it turns about."""
    return RISE * math.tan(math.radians(rock()))


# THE THREE FLATS THE OUTLINE LEAVES, and every one of them carries the word. A collar on a tube
# takes whatever roll the bundle gives it, so a word on one face is a word that is behind the tube
# half the time — and what shows then is a coloured ring, which says nothing the tube's own colour
# has not already said. Lettered at 0° and ±90° the collar cannot present a blank face to a reader
# without presenting a lettered one to the same reader edge-on. The round below the axis takes no
# lettering; it is what the hand meets and it stays round.
FACES = ("top", "+x", "-x")


def word_band(face: str = "top") -> tuple:
    """The flat a face letters in, as `(along the tube, across it)` — the face less its margins.

    The advance runs along the tube on all three. The cap stands ACROSS the tube on the top flat,
    which is `OD` wide, and UP the collar on the two sides, which are `RISE` tall."""
    across = OD if face == "top" else RISE
    return (LENGTH - 2.0 * WORD_MARGIN, across - 2.0 * WORD_MARGIN)


def _face_word(which: str, face: str):
    """One station's word on one of its flats, standing in the recess it fills.

    THE LETTERS ARE LOOSE, one solid each — `bulkhead_ring.build_word`'s construction. The part opens as
    one file carrying both bodies and the lettering is assigned the second filament.

    `text` sets flat in XY with its advance on +X, its cap on +Y and its extrusion on +Z, and each
    face is that block turned onto its own outward normal:

        top   a quarter about Z              advance +Y, cap −X, out +Z
        +x    a quarter about X, then one Z  advance +Y, cap +Z, out +X
        −x    THE +x FACE, HALF-TURNED ABOUT Z          advance −Y, cap +Z, out −X

    THE TWO SIDES ARE ONE TURN APART and the second is struck off the first, not composed on its
    own. A half turn about Z reverses the advance and the outward normal together and leaves the cap
    standing, which is the whole of what the far side of a collar is; two independent compositions
    that each look right on paper can differ in a sign nothing but a render shows.
    """
    letters = cq.Workplane("XY").text(STATIONS[which].word, _ring.WORD_SIZE, WORD_DEPTH,
                                      font=_ring.WORD_FONT, kind=_ring.WORD_KIND,
                                      halign="center", valign="center")
    if face == "top":
        letters = letters.rotate((0, 0, 0), (0, 0, 1), 90.0)
    else:
        letters = (letters.rotate((0, 0, 0), (1, 0, 0), 90.0)
                          .rotate((0, 0, 0), (0, 0, 1), 90.0))
        if face == "-x":
            letters = letters.rotate((0, 0, 0), (0, 0, 1), 180.0)
    solid = letters.val()
    # `valign` centres on the font's own metrics rather than on the cap box, so the cap is squared up
    # on the flat here, off the solid that was actually built.
    bb = solid.BoundingBox()
    along = LENGTH / 2.0 - (bb.ymin + bb.ymax) / 2.0
    if face == "top":
        return solid.translate(cq.Vector(-(bb.xmin + bb.xmax) / 2.0, along,
                                         RISE - WORD_DEPTH - bb.zmin))
    # EACH SIDE BY THE FACE ITS OWN LETTERS STAND OUT OF — `xmax` on the +x side and `xmin` on the
    # −x, since the half turn carried the extrusion over with the advance. The side flats stand from
    # the axis up to `RISE`, so the cap is centred on half of that.
    out = (OD / 2.0 - bb.xmax) if face == "+x" else (-OD / 2.0 - bb.xmin)
    return solid.translate(cq.Vector(out, along, RISE / 2.0 - (bb.zmin + bb.zmax) / 2.0))


def build_word(which: str):
    """One station's word on all three flats, as one compound — what the second filament lays."""
    return cq.Compound.makeCompound(
        [letter for face in FACES for letter in _face_word(which, face).Solids()])


def build_blank():
    """The outline run along the tube and its bore, with no lettering taken out of it — what a
    station's own word is cut from, and what `letters_lie_in_it` weighs the cut against.

    Struck from primitives the way `bulkhead_ring.build_outline` strikes the chip's — a cylinder with
    everything above the axis taken off it, and a box standing on that same axis — so no plane's own
    chirality reaches the shape."""
    r = OD / 2.0
    barrel = cq.Solid.makeCylinder(r, LENGTH, cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 1.0, 0.0))
    below = cq.Solid.makeBox(OD, LENGTH, r, cq.Vector(-r, 0.0, -r))
    above = cq.Solid.makeBox(OD, LENGTH, RISE, cq.Vector(-r, 0.0, 0.0))
    return (barrel.intersect(below).fuse(above)
            .cut(cq.Solid.makeCylinder(BORE / 2.0, LENGTH,
                                       cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 1.0, 0.0))))


def build_collar(which: str):
    """One station's collar: the blank, with the word's recess taken out of each of its flats."""
    return build_blank().cut(build_word(which))


def _filament(rgb) -> "cq.Color":
    return step_safe(cq.Color(*(c / 255.0 for c in rgb)))


def build_part(which: str) -> cq.Assembly:
    """One station as it prints: the collar, and the word lying in its recess, each in the filament
    it comes off — `_y_wall_dimensions`' table, the one the chip on the wall reads."""
    fluid = STATIONS[which].fluid
    a = cq.Assembly()
    a.add(build_collar(which), name=f"tube-collar-{which}",
          color=_filament(_rear.chip_color(fluid)))
    a.add(build_word(which), name=f"tube-collar-{which}-word",
          color=_filament(_rear.word_color(fluid)))
    return a


def seat() -> tuple:
    """The face a tube run takes it by: `(position, outward axis)` on the collar's INBOARD end, the
    one that faces the fitting the tube goes into."""
    return ((0.0, 0.0, 0.0), (0.0, -1.0, 0.0))


def split(shape) -> tuple:
    """A station's STEP back apart, as `(collar, word)`.

    The collar reaches both end faces; the lettering stands in a recess in the flat and touches
    neither. So the body spanning the whole of `LENGTH` is the collar and every other body is a
    letter — read off the solid rather than by counting letters, which would tie this to the word a
    station happens to carry."""
    solids = shape.Solids() if hasattr(shape, "Solids") else shape
    full = [s for s in solids if abs(s.BoundingBox().ylen - LENGTH) < 1e-6]
    if len(full) != 1 or len(solids) < 2:
        raise ValueError(
            f"a station's STEP is a collar and the letters lying in it, and this one carries "
            f"{len(solids)} {'body' if len(solids) == 1 else 'bodies'}, {len(full)} of them "
            f"running the whole {LENGTH:g} mm")
    return (full[0], cq.Compound.makeCompound([s for s in solids if s is not full[0]]))


def stations_hold():
    """Hold the figures a tube run reads to each collar's own STEP.

    The width and height are extents of that solid, the length its run along the axis, and the bore
    a turned face inside it."""
    for which, step in STEPS.items():
        solid, _word = split(import_step(str(step)).val())
        bb = solid.BoundingBox()
        for what, claimed, actual in (("collar width", OD, bb.xlen),
                                      ("collar height", OD / 2.0 + RISE, bb.zlen),
                                      ("collar length", LENGTH, bb.ylen)):
            if abs(claimed - actual) > 1e-6:
                raise ValueError(
                    f"tube-collar {which} {what} is {claimed:g} and {step.name} carries "
                    f"{actual:.4f} — a run drawn to the declared figure does not take the collar "
                    f"that is there.")
        radii = sorted({r for _axis, r in bores(solid)})
        if not any(abs(2.0 * r - BORE) <= 1e-6 for r in radii):
            raise ValueError(
                f"the {which} collar's bore is declared Ø{BORE:g} and {step.name} turns no face at "
                f"that diameter — it carries Ø{[round(2 * r, 3) for r in radii]}. A collar bored "
                f"under its own figure does not thread onto the tube it is for.")


def words_hold():
    """Hold the lettering to `bulkhead_ring`'s figures, off the built solids.

    THE FACE IS THE SYSTEM'S. `bulkhead_ring.WORD_FONT` names one this repo does not ship, so a machine
    that resolves it elsewhere letters a collar with a different word on it — same colour, same
    outline — and nothing about that shows up in a bore or an extent. The word is set at
    `bulkhead_ring`'s own em, so the widths it carries are the widths these come out at."""
    for which, step in STEPS.items():
        word = STATIONS[which].word
        _collar, solid = split(import_step(str(step)).val())
        bb = solid.BoundingBox()
        if len(solid.Solids()) != len(FACES) * len(word):
            raise ValueError(
                f"'{word}' is {len(solid.Solids())} solids in {step.name} and {len(FACES)} flats "
                f"of a {len(word)}-letter word is {len(FACES) * len(word)} — the lettering is not "
                f"the word it is declared to be, on every face it is declared to be on.")
        if abs(bb.ylen - _ring.WORD_WIDTHS[word]) > 1e-3:
            raise ValueError(
                f"'{word}' is declared {_ring.WORD_WIDTHS[word]:.3f} mm along the tube and "
                f"{step.name} carries {bb.ylen:.3f} — `{_ring.WORD_FONT}` did not resolve to the "
                f"face the wall's own chips were struck on, and the collar is lettered in "
                f"something else.")
        # AND EVERY FLAT ONE RECESS DEEP. Read off the built face rather than off the compound,
        # which spans the collar and would hide a face lettered proud of its own flat.
        for face in FACES:
            fbb = _face_word(which, face).BoundingBox()
            depth = fbb.zlen if face == "top" else fbb.xlen
            if abs(depth - WORD_DEPTH) > 1e-6:
                raise ValueError(
                    f"'{word}' stands {depth:.4f} mm out of the {face} flat's recess, which is cut "
                    f"{WORD_DEPTH:g} deep — the word and the flat do not come out one plane.")


def letters_lie_in_it():
    """Hold every face's lettering INSIDE the collar it is cut from.

    A word is placed by turning a block onto a face's own outward normal, and a face whose normal
    came out reversed puts its letters just off the flat instead of just inside it. Nothing about
    that shows in a width, a depth or a count — the solids are all there and all the right size —
    and the collar it is cut from comes back whole.

    So it is weighed. What the cut takes off the blank is the volume of the lettering when every
    letter is inside it, and less by exactly the strays when any are not.

    The margin is a thousandth of the word. What this is here to catch is a whole face standing off
    the collar, which is a THIRD of it, or one letter, which is a twelfth of the shortest of these
    words — both of them three orders above the noise two booleans leave in a volume."""
    for which in STATIONS:
        blank, word = build_blank(), build_word(which)
        took = blank.Volume() - blank.cut(word).Volume()
        if abs(took - word.Volume()) > word.Volume() / 1000.0:
            outside = word.Volume() - took
            raise ValueError(
                f"the {which} collar's lettering runs to {word.Volume():.3f} mm³ and cutting it "
                f"off the blank takes {took:.3f} — {outside:.3f} mm³ of it stands outside the "
                f"collar rather than in a recess in one of its flats.")


def selftest() -> int:
    """Each collar against the tube it threads onto, the word it carries, and the chip on the wall."""
    fails = []
    # THE TUBE THE BORE IS ANSWERED AGAINST IS THE BIGGEST ONE A SPOOL RUNS, not the nominal. A
    # bore sized on the nominal meets a tube `LLDPE_TOL` over it and does not go on, and the sag
    # takes `BORE_SHRINK` more off before it ever meets one.
    if bore_printed() < TUBE_OD + LLDPE_TOL:
        fails.append(
            f"a collar prints Ø{bore_printed():g} and a spool running high hands the bench "
            f"Ø{TUBE_OD + LLDPE_TOL:g} of tube — {LENGTH:g} mm of bore on that is a part that goes "
            f"on with a mallet or not at all")
    if backing() < WORD_DEPTH - 1e-9:
        fails.append(
            f"the word's recess is {WORD_DEPTH:g} deep and leaves {backing():.3f} mm of colour "
            f"between its floor and the bore's crown")
    for which, collar in STATIONS.items():
        width = _ring.WORD_WIDTHS[collar.word]
        for face in FACES:
            along, across = word_band(face)
            if width > along + 1e-9:
                fails.append(
                    f"'{collar.word}' runs {width:.3f} mm along a collar {LENGTH:g} mm long that "
                    f"leaves {along:.3f} mm between its own margins")
            if _ring.WORD_CAP > across + 1e-9:
                fails.append(
                    f"the {which} collar letters a {_ring.WORD_CAP:g} mm cap across its {face} "
                    f"flat, which leaves {across:.3f} mm between its margins")
        if collar.word != _ring.STATIONS[which].word:
            fails.append(
                f"the {which} collar says '{collar.word}' and the chip on the wall at that same "
                f"station says '{_ring.STATIONS[which].word}' — a tube and the ring it goes "
                f"through are read by one word or by neither")
    needed = max(_ring.WORD_WIDTHS[c.word] for c in STATIONS.values()) + 2.0 * WORD_MARGIN
    if LENGTH < needed - 1e-9:
        fails.append(
            f"the longest of these words asks {needed:.3f} mm along the tube and `LENGTH` is "
            f"{LENGTH:g}")
    # `bulkhead_ring.THICK` is the same identification carried on a chip, on the same tube's play.
    chip_rock = math.degrees(math.atan2(clearance(), _ring.THICK))
    if rock() >= chip_rock:
        fails.append(
            f"a collar {LENGTH:g} mm long cocks {rock():.3f}° on its loosest tube and a chip's own "
            f"{_ring.THICK:g} mm cocks {chip_rock:.3f}°")
    if wall() <= 0.0:
        fails.append(f"a Ø{OD:g} collar bored Ø{BORE:g} leaves no wall around the tube")
    # THE FACES ARE WHAT A ROLL CANNOT HIDE. Two of them leave a collar that can turn a blank flat
    # square to a reader; three cannot.
    if len(FACES) < 3:
        fails.append(
            f"{len(FACES)} lettered flat(s) leave a roll that shows a reader colour and no word")
    for what, fn in (("stations_hold", stations_hold), ("words_hold", words_hold),
                     ("letters_lie_in_it", letters_lie_in_it)):
        try:
            fn()
        except Exception as exc:                                 # noqa: BLE001
            fails.append(str(exc))
    for line in fails:
        print(f"FAIL {line}")
    if not fails:
        print("ok  tube-collar  " + ", ".join(
            f"{w} {STATIONS[w].word}" for w in STATIONS)
            + f" — Ø{OD:g} × {LENGTH:g} on Ø{TUBE_OD:g} tube, bore Ø{BORE:g} modelled and "
              f"Ø{bore_printed():g} printed, cocks {rock():.3f}° "
              f"({flag_sway() * 1000:.0f} µm at the flag)")
    return 1 if fails else 0


def main():
    volumes, word_volumes = {}, {}
    for which in STATIONS:
        collar, word = build_collar(which), build_word(which)
        volumes[which] = collar.Volume() / 1000.0
        word_volumes[which] = word.Volume() / 1000.0
        bb = collar.BoundingBox()
        print(f"Tube collar — {which} station, '{STATIONS[which].word}'")
        print(f"  Ø{OD:g} wide × {OD / 2.0 + RISE:g} tall × {LENGTH:g} along the tube / "
              f"bore Ø{BORE:g} modelled, Ø{bore_printed():g} printed, on Ø{TUBE_OD:g} LLDPE")
        print(f"  Wall {wall():g} mm, {backing():g} mm of colour behind the lettering")
        print(f"  Canonical-frame bounding box: "
              f"X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
              f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
              f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
        print(f"  Solid valid: {collar.isValid()}")
        export_assembly(build_part(which), str(STEPS[which]))
        print(f"-> {STEPS[which].name}")

    chip_rock = math.degrees(math.atan2(clearance(), _ring.THICK))
    print(f"  Slips {SLIP:g} mm on the biggest tube a spool runs (Ø{TUBE_OD + LLDPE_TOL:g})")
    print(f"  Cocks {rock():.4f}° on its loosest tube "
          f"({clearance():.3f} mm of play over {LENGTH:g} mm of bore), "
          f"{flag_sway() * 1000:.0f} µm at the flag's face")
    print(f"  A {_ring.THICK:g} mm chip on the same tube: {chip_rock:.3f}°")

    substitute_md(_here.parent / "README.md", variables={
        "COLLAR_TUBE_OD": f"{TUBE_OD:g}",
        "COLLAR_TUBE_HIGH": f"{TUBE_OD + LLDPE_TOL:g}",
        "COLLAR_BORE": f"{BORE:g}",
        "COLLAR_BORE_PRINTED": f"{bore_printed():g}",
        "COLLAR_SHRINK": f"{BORE_SHRINK:g}",
        "COLLAR_SLIP": f"{SLIP:g}",
        "COLLAR_OD": f"{OD:g}",
        "COLLAR_RISE": f"{RISE:g}",
        "COLLAR_TALL": f"{OD / 2.0 + RISE:g}",
        "COLLAR_LENGTH": f"{LENGTH:g} mm",
        "COLLAR_WALL": f"{wall():g}",
        "COLLAR_BACKING": f"{backing():g}",
        "COLLAR_VOL": f"{volumes['flavor-a']:.2f}",
        "COLLAR_WORD_VOL": f"{word_volumes['flavor-a']:.2f}",
        "COLLAR_CLEARANCE": f"{clearance():.2f}",
        "COLLAR_LLDPE_TOL": f"{LLDPE_TOL:g}",
        "COLLAR_ROCK": f"{rock():.2f}",
        "COLLAR_CHIP_THICK": f"{_ring.THICK:g}",
        "COLLAR_CHIP_ROCK": f"{chip_rock:.2f}",
        "COLLAR_SWAY": f"{flag_sway() * 1000:.0f}",
        "COLLAR_WORD_DEPTH": f"{WORD_DEPTH:g}",
        "COLLAR_WORD_MARGIN": f"{WORD_MARGIN:g}",
        "COLLAR_WORD_SIZE": f"{_ring.WORD_SIZE:g}",
        "COLLAR_WORD_CAP": f"{_ring.WORD_CAP:g}",
        "COLLAR_BAND_ALONG": f"{word_band()[0]:g}",
        "COLLAR_BAND_ACROSS": f"{word_band()[1]:g}",
    })
    print("-> README.md")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main()
