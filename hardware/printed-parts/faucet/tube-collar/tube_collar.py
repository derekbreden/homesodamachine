"""Tube collar — the port ring's word and colour, carried on the tube.

`../../enclosure/port-ring/` marks the wall: a chip lying in a pocket of the back face, under a through-wall
fitting's flange, in the colour of the tube that goes into it. This is that chip bored for the tube
instead of for the fitting's barrel, run along it, and turned a quarter so the word reads down the
run. Same four colours, same five words, same two-filament print.

    THE OUTLINE IS THE CHIP'S — a half circle below the bore's axis and a rectangle above it,
    `RISE` tall over an OD twice that. It is not a shape that turns: the flat lies one way up and
    the word stands level on it without anything holding it there.

THE BORE IS CLOSED AND CUT UNDER THE TUBE, and the collar threads on end-first, over a tail that is
still bare. `assembly/faucet-and-umbilical.md` §1 cuts the umbilical's three tubes and §4 sleeves
them; the collars go on between. The tap run and the CO2 tether are the customer's own cuts, and
their collars ride in the install kit.

THE LENGTH IS THE BORE'S. `rock()` is the angle a collar can cock on its loosest tube — a bore of
length L with diametral play c binds at two diagonal corners, leaving atan(c/L) — and `flag_sway()`
carries that angle out to the word's face, the furthest anything on the collar stands from the line
it would turn about. `selftest` reads both against `port_ring.THICK`, which is the same
identification carried on a chip.

Coordinate frame — THE TUBE'S, the same one `port_ring` gives the fitting:
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
           _hw / "printed-parts" / "enclosure" / "back-panel",
           _hw / "printed-parts" / "enclosure" / "port-ring"):
    sys.path.insert(0, str(_p))
sys.path.insert(0, str(next(p for p in _here.parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_assembly, import_step  # noqa: E402
from _materials import step_safe  # noqa: E402
from _measuring import bores  # noqa: E402
import _back_panel_dimensions as _rear  # noqa: E402
import port_ring as _ring  # noqa: E402
from docgen import substitute_md  # noqa: E402

# THE ONE TUBE SIZE ON THIS MACHINE. Every line the customer meets is 1/4" OD LLDPE, off one of the
# four neoFlo spools in `ledger/bom.md` §3.
TUBE_OD = 6.35
# The bore, cut under it. LLDPE is the soft half of the pair and takes the five hundredths; the grip
# runs the whole of `LENGTH`.
BORE = 6.30
# The collar's width, and the diameter of the half circle below the axis. It leaves a `wall()` of
# colour all round the tube — this part's answer to `port_ring.RING_W`, the band of colour a chip
# shows past its flange.
OD = 12.0
# HOW FAR THE RECTANGLE STANDS ABOVE THE AXIS. Half the OD, which is `port_ring.RISE` over its own
# OD to within a part in two hundred, so the outline comes out square the way a chip's does. The
# flat it puts on top is the face the word is lettered in.
RISE = OD / 2.0
# THE RUN ALONG THE TUBE. It is the longest of the five words plus its margins, set at
# `port_ring.WORD_SIZE` — the wall's lettering and the tube's are one size, and `selftest` holds
# this to it.
LENGTH = 30.0
# How deep the word's recess is cut into the flat, and what the flat keeps clear of it. Both are
# `port_ring`'s.
WORD_DEPTH = _ring.WORD_DEPTH
WORD_MARGIN = _ring.WORD_MARGIN
# What 1/4" OD LLDPE holds its diameter to on the spool. `clearance()` and `rock()` are answers
# about a tube at the low end of it.
LLDPE_TOL = 0.13

# ONE COLLAR PER CHIP. The five keys are `port_ring.STATIONS`' own, and each takes its word and its
# spool from the chip at that station — a word changed on the wall is changed on the tube by the
# same edit.
#
# WHICH TUBE EACH ONE RIDES, and the bench or the bag it goes in.
Collar = collections.namedtuple("Collar", "word fluid tube fitted")
STATIONS = {
    which: Collar(_ring.STATIONS[which].word, _ring.FLUIDS[which], tube, fitted)
    for which, tube, fitted in (
        ("water", "the customer's tap-water run, up to their angle stop", "install kit"),
        ("carb", "the umbilical's blue carbonated-water tail", "faucet bench"),
        ("co2", "the customer's red tether, rear wall to regulator", "install kit"),
        ("flavor-a", "the umbilical's first black flavour tail", "faucet bench"),
        ("flavor-b", "the umbilical's second black flavour tail", "faucet bench"),
    )
}
# ONE FILE PER STATION, AND IT HOLDS BOTH BODIES — `port_ring.STEPS`' construction. The part is one
# print in two filaments, a collar and the word lying in its recess, and the file is that pair.
STEPS = {name: _here.parent / f"tube-collar-{name}.step" for name in STATIONS}


def wall() -> float:
    """The colour standing between the bore and the outside — all round the tube below the axis, and
    between the bore's crown and the flat above it. One figure because `RISE` is half the OD: the
    rectangle stands as far over the axis as the half circle falls under it."""
    return (OD - BORE) / 2.0


def backing() -> float:
    """The colour left under the word's recess, between its floor and the bore's crown. `selftest`
    reads it against `WORD_DEPTH`."""
    return wall() - WORD_DEPTH


def clearance() -> float:
    """The diametral play a collar has on the loosest tube its spool runs.

    The bore is cut under the tube, so at nominal there is none and the fit is an interference. The
    tube is an extrusion held to `LLDPE_TOL`, and one at the low end of that is the case with any
    play in it at all."""
    return LLDPE_TOL - (TUBE_OD - BORE)


def rock() -> float:
    """The angle a collar can cock on that tube, in degrees. A bore of length L with diametral play
    c binds at two diagonal corners, leaving atan(c/L)."""
    return math.degrees(math.atan2(clearance(), LENGTH))


def flag_sway() -> float:
    """That angle carried out to the flag's face, at `RISE` off the axis — the furthest anything on
    the collar stands from the line it turns about."""
    return RISE * math.tan(math.radians(rock()))


def word_band() -> tuple:
    """The flat the word is lettered in, as `(along the tube, across it)` — the face less its
    margins. The advance runs along the tube and the cap stands across it."""
    return (LENGTH - 2.0 * WORD_MARGIN, OD - 2.0 * WORD_MARGIN)


def build_word(which: str):
    """One station's word, standing in the recess it fills, its face flush with the flat's own.

    THE LETTERS ARE LOOSE, one solid each — `port_ring.build_word`'s construction. The part opens as
    one file carrying both bodies and the lettering is assigned the second filament.

    TURNED TO READ ALONG THE TUBE. `text` sets flat in XY with its advance on +X and its cap on +Y;
    a quarter turn about Z lays the advance on +Y, outboard, and stands the cap across the tube on
    −X. The extrusion stays on +Z and the word drops until its face is level with the flat."""
    flat = cq.Workplane("XY").text(STATIONS[which].word, _ring.WORD_SIZE, WORD_DEPTH,
                                   font=_ring.WORD_FONT, kind=_ring.WORD_KIND,
                                   halign="center", valign="center")
    letters = flat.rotate((0, 0, 0), (0, 0, 1), 90.0).val()
    # `valign` centres on the font's own metrics rather than on the cap box, so the cap is squared up
    # on the flat here, off the solid that was actually built.
    bb = letters.BoundingBox()
    return letters.translate(cq.Vector(
        -(bb.xmin + bb.xmax) / 2.0,
        LENGTH / 2.0 - (bb.ymin + bb.ymax) / 2.0,
        RISE - WORD_DEPTH - bb.zmin))


def build_collar(which: str):
    """One station's collar: the outline run along the tube, its bore, and the word's recess taken
    out of the flat.

    Struck from primitives the way `port_ring.build_outline` strikes the chip's — a cylinder with
    everything above the axis taken off it, and a box standing on that same axis — so no plane's own
    chirality reaches the shape."""
    r = OD / 2.0
    barrel = cq.Solid.makeCylinder(r, LENGTH, cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 1.0, 0.0))
    below = cq.Solid.makeBox(OD, LENGTH, r, cq.Vector(-r, 0.0, -r))
    above = cq.Solid.makeBox(OD, LENGTH, RISE, cq.Vector(-r, 0.0, 0.0))
    body = barrel.intersect(below).fuse(above)
    body = body.cut(cq.Solid.makeCylinder(BORE / 2.0, LENGTH,
                                          cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 1.0, 0.0)))
    return body.cut(build_word(which))


def _filament(rgb) -> "cq.Color":
    return step_safe(cq.Color(*(c / 255.0 for c in rgb)))


def build_part(which: str) -> cq.Assembly:
    """One station as it prints: the collar, and the word lying in its recess, each in the filament
    it comes off — `_back_panel_dimensions`' table, the one the chip on the wall reads."""
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
    """Hold the lettering to `port_ring`'s figures, off the built solids.

    THE FACE IS THE SYSTEM'S. `port_ring.WORD_FONT` names one this repo does not ship, so a machine
    that resolves it elsewhere letters a collar with a different word on it — same colour, same
    outline — and nothing about that shows up in a bore or an extent. The word is set at
    `port_ring`'s own em, so the widths it carries are the widths these come out at."""
    for which, step in STEPS.items():
        word = STATIONS[which].word
        _collar, solid = split(import_step(str(step)).val())
        bb = solid.BoundingBox()
        if len(solid.Solids()) != len(word):
            raise ValueError(
                f"'{word}' is {len(solid.Solids())} solids in {step.name} and the word is "
                f"{len(word)} letters — the lettering is not the word it is declared to be.")
        if abs(bb.ylen - _ring.WORD_WIDTHS[word]) > 1e-3:
            raise ValueError(
                f"'{word}' is declared {_ring.WORD_WIDTHS[word]:.3f} mm along the tube and "
                f"{step.name} carries {bb.ylen:.3f} — `{_ring.WORD_FONT}` did not resolve to the "
                f"face the wall's own chips were struck on, and the collar is lettered in "
                f"something else.")
        if abs(bb.zlen - WORD_DEPTH) > 1e-6:
            raise ValueError(
                f"'{word}' stands {bb.zlen:.4f} mm out of a recess cut {WORD_DEPTH:g} deep — the "
                f"word and the flat do not come out one plane.")


def selftest() -> int:
    """Each collar against the tube it threads onto, the word it carries, and the chip on the wall."""
    fails = []
    if BORE >= TUBE_OD:
        fails.append(
            f"a bore of Ø{BORE:g} on a Ø{TUBE_OD:g} tube is clearance at nominal, and the collar "
            f"is held by nothing but the tube's own tolerance")
    if backing() < WORD_DEPTH - 1e-9:
        fails.append(
            f"the word's recess is {WORD_DEPTH:g} deep and leaves {backing():.3f} mm of colour "
            f"between its floor and the bore's crown")
    along, across = word_band()
    for which, collar in STATIONS.items():
        width = _ring.WORD_WIDTHS[collar.word]
        if width > along + 1e-9:
            fails.append(
                f"'{collar.word}' runs {width:.3f} mm along a collar {LENGTH:g} mm long that "
                f"leaves {along:.3f} mm between its own margins")
        if _ring.WORD_CAP > across + 1e-9:
            fails.append(
                f"the {which} collar letters a {_ring.WORD_CAP:g} mm cap across a flat that "
                f"leaves {across:.3f} mm between its margins")
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
    # `port_ring.THICK` is the same identification carried on a chip, on the same tube's play.
    chip_rock = math.degrees(math.atan2(clearance(), _ring.THICK))
    if rock() >= chip_rock:
        fails.append(
            f"a collar {LENGTH:g} mm long cocks {rock():.3f}° on its loosest tube and a chip's own "
            f"{_ring.THICK:g} mm cocks {chip_rock:.3f}°")
    if wall() <= 0.0:
        fails.append(f"a Ø{OD:g} collar bored Ø{BORE:g} leaves no wall around the tube")
    if abs(RISE - OD / 2.0) > 1e-9:
        fails.append(
            f"the rectangle stands {RISE:g} over an axis its own half circle reaches {OD / 2.0:g} "
            f"below — the outline is not the chip's proportion")
    for what, fn in (("stations_hold", stations_hold), ("words_hold", words_hold)):
        try:
            fn()
        except Exception as exc:                                 # noqa: BLE001
            fails.append(str(exc))
    for line in fails:
        print(f"FAIL {line}")
    if not fails:
        print("ok  tube-collar  " + ", ".join(
            f"{w} {STATIONS[w].word}" for w in STATIONS)
            + f" — Ø{OD:g} × {LENGTH:g} on Ø{TUBE_OD:g} tube, bore Ø{BORE:g}, "
              f"cocks {rock():.3f}° ({flag_sway() * 1000:.0f} µm at the flag)")
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
              f"bore Ø{BORE:g} on Ø{TUBE_OD:g} LLDPE")
        print(f"  Wall {wall():g} mm, {backing():g} mm of colour behind the lettering")
        print(f"  Canonical-frame bounding box: "
              f"X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
              f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
              f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
        print(f"  Solid valid: {collar.isValid()}")
        export_assembly(build_part(which), str(STEPS[which]))
        print(f"-> {STEPS[which].name}")

    chip_rock = math.degrees(math.atan2(clearance(), _ring.THICK))
    print(f"  Cocks {rock():.4f}° on its loosest tube "
          f"({clearance():.3f} mm of play over {LENGTH:g} mm of bore), "
          f"{flag_sway() * 1000:.0f} µm at the flag's face")
    print(f"  A {_ring.THICK:g} mm chip on the same tube: {chip_rock:.3f}°")

    substitute_md(_here.parent / "README.md", variables={
        "COLLAR_TUBE_OD": f"{TUBE_OD:g}",
        "COLLAR_BORE": f"{BORE:g}",
        "COLLAR_OD": f"{OD:g}",
        "COLLAR_RISE": f"{RISE:g}",
        "COLLAR_TALL": f"{OD / 2.0 + RISE:g}",
        "COLLAR_LENGTH": f"{LENGTH:g}",
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
