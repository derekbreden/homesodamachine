"""Port-ring test coupons — six chips, each one a decision, on one plate.

A COUPON IS A PORT RING. Same D outline, same bore, same thickness, same word standing in the
same band, off the same two spools — `port_ring`'s own builders cut it, so a coupon drops into
the wall's pocket and is read against the machine rather than against a drawing.

EACH CHIP IS A RECOMMENDATION AND NOT A STEP IN A SWEEP. `matched`, `raised` and `recommended`
are what the part should become; `smaller` and `larger` stand either side of the em so the
recommendation has something to be read against; `co2` carries the same recommendation on the
word that cannot take it.

    THE BEAD IS 0.22 AND NOT 0.2. `port_ring.WORD_NOZZLE` is the orifice; `port_ring.WORD_BEAD`
    is what the slicer plans to lay through it. The bead is also the divisor: a feature's width
    over it is how many perimeters fit, and the remainder is gap fill or nothing. `matched` is
    the em whose narrowest stroke is `WALLS` whole beads — the exact perimeter count the profile
    lays, so every stroke is all wall and no fill.

    THE RIM IS WHAT PAYS FOR IT. The band a word stands in — `port_ring.word_band`, between the
    fitting's flange edge and the chip's top edge — is fixed at both ends, so a cap grows out of
    the rim of chip above it. `matched` spends the rim down to 4.4 beads. `larger` spends it to
    2.9, which is under the wall stack, and is on the plate to show what that costs.

Coordinate frame — `port_ring`'s, chips laid out in a grid on +X and −Z:
  Y = the thickness. y = 0 is the face that lands on the pocket floor, y = `port_ring.THICK` the
      face the word comes out of. A relief stands past it.
  +Z = up. X runs along the word, which reads along −X.

Run:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/port-ring/coupons/port_ring_coupons.py
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/port-ring/coupons/port_ring_coupons.py selftest
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
import _back_panel_dimensions as _rear  # noqa: E402
import port_ring as _ring  # noqa: E402
from docgen import substitute_md  # noqa: E402

STEP = _here.parent / "port-ring-coupons.step"

# THE PLATE THESE ARE READ ON, and the part states it — `port_ring.WORD_BEAD` and `WORD_LAYER`
# are read off `../port-ring-water.3mf` and gate the chip's own strokes and bridges. A coupon
# struck on one profile and printed on another measures the profile.
LINE_W = _ring.WORD_BEAD
LAYER_H = _ring.WORD_LAYER
# How many perimeters the profile lays before it falls back to infill, and so how many whole
# beads a stroke can be spent entirely on wall.
WALLS = 4
# WHAT A LAYER CARRYING BOTH COLOURS COSTS. `filament_maps` on that plate stands both spools on
# ONE nozzle, so a colour change on a layer is a filament change, and `flush_volumes_matrix`
# charges it 900 mm³ black-to-white and 90 back. Every layer from the recess floor up to the
# chip's face carries both colours; the layers below the floor, and the layers above the face
# where a relief stands alone, carry one.
FLUSH = 900.0 + 90.0

# WHAT EACH STATION'S LETTERING MEASURES AT `port_ring.WORD_SIZE`, off the built letterforms: its
# narrowest stroke and the narrowest bridge of chip between two of its letters. Every em here is
# solved back from the first, and the second is what puts a floor under how small one can go.
# `specimens_hold` reads both back off the solids.
STROKE = {"flavor-a": 0.802588, "co2": 0.771439}
BRIDGE = {"flavor-a": 0.345947, "co2": 0.548480}
# The station every em is struck on. FLAVOR is the longest of the five words, the one that can
# run out of chip, and the one carrying two counters that close, one that comes to a point, and
# two diagonals meeting in a stroke narrower than either. Two of the five chips wear it, and its
# pair is white on black — the direction the second colour stands OVER the first.
HOME = "flavor-a"
# How the recess is grown when a chip leaves air round its word: the letterforms unioned with
# copies of themselves standing round a circle of the offset. Eight of them leave a corner short
# by 7.6% of the offset.
KERNEL_SIDES = 8


def cap_of(em: float) -> float:
    """The cap height one em is worth, off the part's own pair."""
    return em * _ring.WORD_CAP / _ring.WORD_SIZE


def stroke_of(station: str, em: float) -> float:
    """One station's narrowest stroke at one em. A letterform is a scale of itself, so one
    measured figure carries up and down."""
    return em * STROKE[station] / _ring.WORD_SIZE


def gap_of(station: str, em: float) -> float:
    """Its narrowest bridge of chip between two letters, at one em."""
    return em * BRIDGE[station] / _ring.WORD_SIZE


def em_for_beads(beads: float, station: str = HOME) -> float:
    """The em whose narrowest stroke is `beads` of `LINE_W` — `stroke_of` solved the other way."""
    return beads * LINE_W * _ring.WORD_SIZE / STROKE[station]


def band(station: str) -> float:
    """The strip of chip a customer reads the lettering in — the fitting's flange edge at its
    bottom and the box's top face at its top."""
    lo, hi = _ring.word_band(station)
    return hi - lo


def band_middle(station: str) -> float:
    """Where a cap box stands in it. `port_ring.build_word` centres on this and so does a
    coupon."""
    lo, hi = _ring.word_band(station)
    return (lo + hi) / 2.0


def rim(station: str, em: float) -> float:
    """The chip standing over the cap with the word centred in the band.
    `port_ring.WORD_MARGIN` is the least the part allows."""
    return (band(station) - cap_of(em)) / 2.0


# THE EM THE PART SHOULD TAKE. Its narrowest stroke is `WALLS` whole beads — 0.88 mm against a
# profile that lays four 0.22 perimeters — so every stroke is spent entirely on wall, with no gap
# fill down the middle of it and no infill inside it. The part's own 6.5 lands at 3.65 beads,
# which is two whole perimeters and a ribbon of gap fill in every limb.
#   IT IS ALSO AS LARGE AS THE BAND TAKES. Five beads wants a 6.79 mm cap in a 7.36 mm band and
# leaves 0.29 of rim, which is one bead; four beads leaves 0.97, which is the four wall loops the
# rim needs and a tenth of a bead over. There is no larger whole-bead em on this part.
EM_MATCHED = em_for_beads(4.0)
# One whole bead down, for a chip to read the recommendation against. Three beads is the last
# whole count that still stands its bridges over one.
EM_SMALLER = em_for_beads(3.0)
# Half a bead up, which is past what the band carries: it leaves 0.63 mm of rim where the wall
# stack alone is 0.88. It is here because a recommendation with nothing past it is a claim rather
# than a reading.
EM_LARGER = em_for_beads(4.5)
# HOW FAR THE WORD SHOULD STAND PROUD. Two layers. One is inside the variation of a top surface
# and is the single course most easily dragged by a nozzle crossing it; two gives an edge that
# catches light and a step a fingertip finds. Past two it is a lip on the back of a kitchen
# appliance that collects what the room has and reads no better.
#   IT ALSO TAKES THE COLOUR SEAM OFF THE VISIBLE FACE. A flush word meets the chip in the same
# layer, so what the two nozzles disagree about lands on the edge a customer looks at. A raised
# word's visible edge is its own, with the seam two layers below it.
RELIEF = 2.0 * LAYER_H
# HOW DEEP THE RECESS SHOULD BE CUT. Six layers, where the part cuts twelve and a half. Every
# layer from the recess floor to the face carries both colours and is charged `FLUSH`, so the
# recess is the single largest cost on the plate and half of it is buying nothing but depth
# behind lettering nobody can see the back of. Six layers of white over black is what
# `recommended` is on the plate to confirm.
DEPTH = 6.0 * LAYER_H

Chip = collections.namedtuple("Chip", "name station em depth relief fit reads")
#: Six chips, laid out three across and two down. Read left to right, top row then bottom: the
#: em against its neighbours either side, then what the recommendation adds to it.
CHIPS = (
    Chip("smaller", HOME, EM_SMALLER, _ring.WORD_DEPTH, 0.0, 0.0,
         "three whole beads to a stroke"),
    Chip("matched", HOME, EM_MATCHED, _ring.WORD_DEPTH, 0.0, 0.0,
         "four whole beads to a stroke — the em to take"),
    Chip("larger", HOME, EM_LARGER, _ring.WORD_DEPTH, 0.0, 0.0,
         "four and a half, and the rim under its wall stack"),
    Chip("raised", HOME, EM_MATCHED, _ring.WORD_DEPTH, RELIEF, 0.0,
         "the em to take, standing two layers proud"),
    Chip("recommended", HOME, EM_MATCHED, DEPTH, RELIEF, 0.0,
         "all three at once, on six layers of second colour"),
    Chip("co2", "co2", EM_MATCHED, DEPTH, RELIEF, 0.0,
         "the same, on the word no em can stand on a whole bead"),
)

# WHICH CHIP IS WHICH, counted in dimples in the face that lands on the pocket floor. They are
# cut into the BACK, so the face a customer reads carries nothing a chip in the wall does not;
# turn one over to find out what it is. Five layers deep, which the first layer cannot bridge.
MARK_D = 1.5
MARK_DEPTH = 5.0 * LAYER_H
MARK_PITCH = 2.0 * MARK_D
# The row stands under the bore, in the half circle, clear of the word's own band.
MARK_ROW = -13.5
# The air between two chips on a plate: four wall loops on each facing edge, and a bead of
# nothing between them.
CHIP_GAP = 2.0 * WALLS * LINE_W + LINE_W
# Three across and two down, which stands the six on 114 × 77 mm of a 256 mm bed.
COLUMNS = 3


def word_of(station: str) -> str:
    """The word one station's chip carries."""
    return _ring.STATIONS[station].word


def word_width(station: str, em: float) -> float:
    """What it measures across at one em, off the part's own figure for it."""
    return _ring.WORD_WIDTHS[word_of(station)] * em / _ring.WORD_SIZE


def slot(n: int) -> "cq.Vector":
    """Where chip `n` stands on the plate, counting from 1 across the top row first."""
    widest = max(_ring.od(_ring.family(c.station)) for c in CHIPS)
    tallest = max(_ring.tall(c.station) for c in CHIPS)
    col, row = (n - 1) % COLUMNS, (n - 1) // COLUMNS
    return cq.Vector(col * (widest + CHIP_GAP), 0.0, -row * (tallest + CHIP_GAP))


def _letters(station: str, em: float, thickness: float, grow: float = 0.0):
    """One station's word flat in XY, extruded `thickness` along +Z, standing `grow` wider all
    round.

    The offset is a union: the letterforms and `KERNEL_SIDES` copies of themselves at `grow`
    round a circle. Every face it comes out with is one the letterform already carried or a plane
    where two copies meet. A counter closes in by the figure its outline stands out."""
    flat = cq.Workplane("XY").text(word_of(station), em, thickness, font=_ring.WORD_FONT,
                                   kind=_ring.WORD_KIND, halign="center", valign="center").val()
    if grow <= 0.0:
        return flat
    out = flat
    for i in range(KERNEL_SIDES):
        a = 2.0 * math.pi * i / KERNEL_SIDES
        out = out.fuse(flat.translate(cq.Vector(grow * math.cos(a), grow * math.sin(a), 0.0)))
    return out.clean()


def build_word(chip: Chip, grow: float = 0.0):
    """One chip's word where the chip carries it: the letterforms, `depth` of them in the recess
    and `relief` of them standing past the face, and nothing behind them.

    THE LETTERS ARE LOOSE, one solid each, the way the part's are. A bar across their feet would
    put second colour behind the recess floor, which on a chip cut to a stated depth is the one
    place that depth would not hold.

    Turned to face the customer by the part's own two rotations, then squared on the cap box the
    solid came out with — `valign` centres on the font's metrics, which are not it — and stood in
    the middle of the band, where `port_ring.build_word` stands its own."""
    solid = (cq.Workplane(obj=_letters(chip.station, chip.em, chip.depth + chip.relief, grow))
             .rotate((0, 0, 0), (1, 0, 0), 90.0)
             .rotate((0, 0, 0), (0, 0, 1), 180.0).val())
    bb = solid.BoundingBox()
    return solid.translate(cq.Vector(-(bb.xmin + bb.xmax) / 2.0,
                                     _ring.THICK - chip.depth - bb.ymin,
                                     band_middle(chip.station) - (bb.zmin + bb.zmax) / 2.0))


def _marks(n: int):
    """The row of dimples that says which chip this is, cut into the face that lands on the
    pocket floor and centred on the bore's axis."""
    span = (n - 1) * MARK_PITCH
    return [cq.Solid.makeCylinder(
        MARK_D / 2.0, MARK_DEPTH,
        cq.Vector(-span / 2.0 + i * MARK_PITCH, 0.0, MARK_ROW),
        cq.Vector(0.0, 1.0, 0.0)) for i in range(n)]


def build_ring(chip: Chip, n: int):
    """One coupon chip: `port_ring`'s own outline and bore, the word's recess taken out of its
    face, and its marks taken out of its back."""
    diameter, top = _ring.outline(chip.station)
    solid = _ring.build_outline(diameter, top, _ring.THICK)
    solid = solid.cut(cq.Solid.makeCylinder(
        _ring.bore_d(_ring.family(chip.station)) / 2.0, _ring.THICK,
        cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 1.0, 0.0)))
    solid = solid.cut(build_word(chip, grow=chip.fit))
    for mark in _marks(n):
        solid = solid.cut(mark)
    return solid


def build_plate() -> tuple:
    """The six as `(chips, words)`, standing where `slot` puts them."""
    chips, words = [], []
    for n, chip in enumerate(CHIPS, 1):
        at = slot(n)
        chips.append(build_ring(chip, n).translate(at))
        words.extend(build_word(chip).translate(at).Solids())
    return (cq.Compound.makeCompound(chips), cq.Compound.makeCompound(words))


def _filament(rgb) -> "cq.Color":
    return cq.Color(*(c / 255.0 for c in rgb))


def build_part() -> cq.Assembly:
    """The plate as it prints: six chips off one spool, every letter off the other.

    ONE PAIR OF SPOOLS FOR ALL SIX. The `co2` chip is drawn in the flavour pair rather than its
    own red so the plate runs on two filaments — what it is on the plate for is its word, and a
    red chip would be a third spool for a letterform question."""
    chips, words = build_plate()
    a = cq.Assembly()
    a.add(chips, name="port-ring-coupons", color=_filament(_rear.chip_color(_ring.FLUIDS[HOME])))
    a.add(words, name="port-ring-coupons-word",
          color=_filament(_rear.word_color(_ring.FLUIDS[HOME])))
    return a


def specimens_hold():
    """Hold `STROKE` and `BRIDGE` to the letterforms this machine builds.

    `port_ring.WORD_FONT` names a face this repo does not ship, and every em here is solved back
    from a stroke while every floor is struck on a bridge. A machine that resolves the face to
    something else stands the whole plate on a bead count the letterforms never had."""
    for station in sorted(STROKE):
        at_part = Chip("ref", station, _ring.WORD_SIZE, _ring.WORD_DEPTH, 0.0, 0.0, "")
        got = _ring.min_stroke(build_word(at_part))
        if abs(got - STROKE[station]) > 1e-3:
            raise ValueError(
                f"'{word_of(station)}' carries a {got:.4f} mm narrowest stroke at em "
                f"{_ring.WORD_SIZE:g} and `STROKE` claims {STROKE[station]:.4f} — "
                f"`{_ring.WORD_FONT}` did not resolve to the face these ems were solved from.")
        got = _ring.min_bridge(station)
        if abs(got - BRIDGE[station]) > 1e-3:
            raise ValueError(
                f"'{word_of(station)}' leaves a {got:.4f} mm bridge between its closest two "
                f"letters and `BRIDGE` claims {BRIDGE[station]:.4f} — the face that resolved "
                f"sets its letters at another fit.")


def recess_holds():
    """Hold every recess to the word it is cut for.

    A chip that leaves air round its word offsets the letterforms outward to cut the recess and
    lays the word in unoffset. A counter offset the wrong way comes back as a recess that closes
    on the word — the O filled in — and no extent carries that, so what is read is the word
    standing wholly inside its hole."""
    for chip in CHIPS:
        proud = build_word(chip).cut(build_word(chip, grow=chip.fit)).Volume()
        if proud > 1e-6:
            raise ValueError(
                f"the {chip.name} chip leaves {proud:.4f} mm³ of word standing outside the "
                f"recess cut for it — the {chip.fit:g} mm offset did not carry every counter "
                f"the way its outline went.")


def chips_hold():
    """Hold every chip on the plate to the port ring it is one of, off the STEP.

    A COUPON IS THE PART OR IT IS NOT A COUPON. The outline, the height and the thickness are
    extents of the chip solid and the bore is a turned face inside it, so a chip that would not
    drop into the wall's own pocket is caught here rather than at the wall. What is allowed to
    differ is the lettering, and that is read against the decision the chip carries."""
    from _measuring import bores
    solids = import_step(str(STEP)).val().Solids()
    want = sum(1 + len(word_of(c.station)) for c in CHIPS)
    if len(solids) != want:
        raise ValueError(
            f"the plate is {len(CHIPS)} chips and their letters, which is {want} solids, and "
            f"{STEP.name} carries {len(solids)} — a chip has lost a letter.")
    # EVERY SOLID BELONGS TO THE SLOT IT STANDS NEAREST. The chips are a grid and the letters
    # stand inside their own chip, so nearest-slot sorts them with nothing left over — which is
    # what `want` above has already counted.
    seats = {n: slot(n) for n in range(1, len(CHIPS) + 1)}
    home = collections.defaultdict(list)
    for s in solids:
        c = s.BoundingBox().center
        home[min(seats, key=lambda n: (c.x - seats[n].x) ** 2
                 + (c.z - seats[n].z) ** 2)].append(s)
    for n, chip in enumerate(CHIPS, 1):
        diameter, top = _ring.outline(chip.station)
        at = slot(n)
        # ONLY A CHIP REACHES THE FULL HEIGHT of its outline; every letter stands in the band.
        body = [s for s in home[n] if s.BoundingBox().zlen > top]
        letters = [s for s in home[n] if s.BoundingBox().zlen <= top]
        if len(body) != 1 or len(letters) != len(word_of(chip.station)):
            raise ValueError(
                f"the {chip.name} chip's slot holds {len(body)} chip(s) and {len(letters)} "
                f"letters where '{word_of(chip.station)}' is {len(word_of(chip.station))} — a "
                f"letter has merged with its neighbour or left its chip.")
        cb = body[0].BoundingBox()
        for what, wanted, got in (("is", diameter, cb.xlen),
                                  ("stands", _ring.tall(chip.station), cb.zlen),
                                  ("runs", _ring.THICK, cb.ylen)):
            if abs(wanted - got) > 1e-3:
                raise ValueError(
                    f"the {chip.name} chip {what} {got:.4f} mm where a port ring {what} "
                    f"{wanted:.4f} — it is not the part it is a coupon of.")
        want_bore = _ring.bore_d(_ring.family(chip.station))
        if not any(abs(2.0 * r - want_bore) <= 1e-3 for _axis, r in bores(body[0])):
            raise ValueError(
                f"the {chip.name} chip turns no face at the wall's own Ø{want_bore:g} — it does "
                f"not pass the barrel a port ring passes.")
        wb = cq.Compound.makeCompound(letters).BoundingBox()
        for what, wanted, got in (
                ("tops its cap at", at.z + band_middle(chip.station) + cap_of(chip.em) / 2.0,
                 wb.zmax),
                ("runs its word", chip.depth + chip.relief, wb.ylen),
                ("faces its word out at", _ring.THICK + chip.relief, wb.ymax)):
            if abs(wanted - got) > 1e-3:
                raise ValueError(
                    f"the {chip.name} chip {what} {got:.4f} and the decision it carries puts it "
                    f"at {wanted:.4f} — the chip is not what the plate is read as saying.")


def selftest() -> int:
    """Each chip against the port ring it is one of, the band it letters in, and the plate."""
    fails = []
    for chip in CHIPS:
        room = _ring.od(_ring.family(chip.station)) - 2.0 * _ring.WORD_MARGIN
        if word_width(chip.station, chip.em) > room + 1e-9:
            fails.append(
                f"the {chip.name} chip letters '{word_of(chip.station)}' "
                f"{word_width(chip.station, chip.em):.3f} mm across a chip that leaves "
                f"{room:.3f} between its own margins")
        if rim(chip.station, chip.em) <= 0.0:
            fails.append(
                f"the {chip.name} chip stands a {cap_of(chip.em):.3f} mm cap in a "
                f"{band(chip.station):.3f} mm band and leaves no rim at all")
        if chip.depth >= _ring.THICK:
            fails.append(
                f"the {chip.name} chip cuts {chip.depth:g} mm of recess into a "
                f"{_ring.THICK:g} mm chip, and what stands behind the lettering is the pocket "
                f"floor")
        if gap_of(chip.station, chip.em) - 2.0 * chip.fit < LINE_W - 1e-9:
            fails.append(
                f"the {chip.name} chip leaves {gap_of(chip.station, chip.em) - 2.0 * chip.fit:.3f}"
                f" mm of chip between two of its letters and the bead is {LINE_W:g} — nothing "
                f"reaches between them")
    # THE FIGURES THIS FILE RECOMMENDS LAND ON WHOLE LAYERS. A recommendation the slicer has to
    # round is one the plate cannot be read as confirming. `port_ring.WORD_DEPTH`, which the
    # chips carrying the part's own recess use, is 12½ layers and is not checked here — that it
    # does not land is a fact about the part and one of the things `recommended` moves.
    for what, value in (("relief", RELIEF), ("recess", DEPTH)):
        if abs(value / LAYER_H - round(value / LAYER_H)) > 1e-9:
            fails.append(
                f"the recommended {what} is {value:g} mm on a plate laying {LAYER_H:g} mm "
                f"layers — that is {value / LAYER_H:.2f} layers and the slicer rounds it")
    if abs(stroke_of(HOME, EM_MATCHED) - WALLS * LINE_W) > 1e-9:
        fails.append(
            f"`matched` stands its stroke on {stroke_of(HOME, EM_MATCHED):.4f} mm where "
            f"{WALLS} whole beads is {WALLS * LINE_W:.4f} — the em is not matched to anything")
    if rim(HOME, EM_MATCHED) < WALLS * LINE_W:
        fails.append(
            f"`matched` leaves {rim(HOME, EM_MATCHED):.3f} mm of rim over its cap and the "
            f"profile lays {WALLS * LINE_W:.2f} of wall — the recommendation asks for a rim the "
            f"plate cannot stand")
    if MARK_DEPTH >= _ring.THICK - max(c.depth for c in CHIPS):
        fails.append(
            f"a {MARK_DEPTH:g} mm mark in the back of a chip meets a recess cut "
            f"{max(c.depth for c in CHIPS):g} into a {_ring.THICK:g} mm face, and the two break "
            f"through to each other")
    for station in {c.station for c in CHIPS}:
        reach = math.hypot((len(CHIPS) - 1) * MARK_PITCH / 2.0, MARK_ROW) + MARK_D / 2.0
        if reach > _ring.od(_ring.family(station)) / 2.0:
            fails.append(
                f"a row of {len(CHIPS)} marks reaches {reach:.3f} mm from the bore's axis and a "
                f"{station} chip's half circle reaches "
                f"{_ring.od(_ring.family(station)) / 2.0:.3f}")
        if abs(MARK_ROW) - MARK_D / 2.0 < _ring.bore_d(_ring.family(station)) / 2.0:
            fails.append(f"a row of marks at z {MARK_ROW:g} stands in a {station} chip's bore")
    if len({c.name for c in CHIPS}) != len(CHIPS):
        fails.append("two chips on the plate answer to the same name")
    for _what, fn in (("specimens_hold", specimens_hold),
                      ("recess_holds", recess_holds),
                      ("chips_hold", chips_hold)):
        try:
            fn()
        except Exception as exc:                                     # noqa: BLE001
            fails.append(str(exc))
    for line in fails:
        print(f"FAIL {line}")
    if not fails:
        print("ok  port-ring-coupons  " + ", ".join(c.name for c in CHIPS)
              + f" — {WALLS} whole beads of {LINE_W:g} at em {EM_MATCHED:.3f}")
    return 1 if fails else 0


def main():
    chips, words = build_plate()
    bb = chips.BoundingBox()
    print(f"Port-ring coupons — {len(CHIPS)} chips, {bb.xlen:.1f} × {bb.zlen:.1f} mm, "
          f"{chips.Volume() / 1000.0:.2f} + {words.Volume() / 1000.0:.2f} cm³")
    for n, chip in enumerate(CHIPS, 1):
        print(f"  {n} {chip.name:<12s} {word_of(chip.station):<7s} em {chip.em:.3f}  "
              f"cap {cap_of(chip.em):.3f}  "
              f"stroke {stroke_of(chip.station, chip.em) / LINE_W:.2f} beads  "
              f"rim {rim(chip.station, chip.em):.3f} = "
              f"{rim(chip.station, chip.em) / LINE_W:.2f}  "
              f"bridge {gap_of(chip.station, chip.em) / LINE_W:.2f}  "
              f"recess {chip.depth / LAYER_H:.0f} layers  "
              f"relief {chip.relief / LAYER_H:.0f}  — {chip.reads}")
    export_assembly(build_part(), str(STEP))
    print(f"-> {STEP.name}")

    variables = {
        "CPN_LINE_W": f"{LINE_W:g}",
        "CPN_LAYER_H": f"{LAYER_H:g}",
        "CPN_WALLS": f"{WALLS:g}",
        "CPN_N": f"{len(CHIPS)}",
        "CPN_PLATE": f"{bb.xlen:.0f} × {bb.zlen:.0f}",
        "CPN_VOL": f"{(chips.Volume() + words.Volume()) / 1000.0:.2f}",
        "CPN_FLUSH": f"{FLUSH:g}",
        "CPN_THICK": f"{_ring.THICK:g}",
        "CPN_OD": f"{_ring.od(_ring.family(HOME)):g}",
        "CPN_BAND": f"{band(HOME):.3f}",
        "CPN_MARGIN": f"{_ring.WORD_MARGIN:g}",
        "CPN_CHIP_FILAMENT": _rear.chip_filaments[_ring.FLUIDS[HOME]][0],
        "CPN_MARK_D": f"{MARK_D:g}",
        "CPN_MARK_DEPTH": f"{MARK_DEPTH:g}",
        "CPN_PART_EM": f"{_ring.WORD_SIZE:g}",
        "CPN_PART_CAP": f"{_ring.WORD_CAP:g}",
        "CPN_PART_BEADS": f"{stroke_of(HOME, _ring.WORD_SIZE) / LINE_W:.2f}",
        "CPN_PART_RIM": f"{rim(HOME, _ring.WORD_SIZE):.3f}",
        "CPN_PART_DEPTH": f"{_ring.WORD_DEPTH:g}",
        "CPN_PART_LAYERS": f"{_ring.WORD_DEPTH / LAYER_H:.1f}",
        "CPN_EM": f"{EM_MATCHED:.3f}",
        "CPN_CAP": f"{cap_of(EM_MATCHED):.3f}",
        "CPN_STROKE": f"{stroke_of(HOME, EM_MATCHED):.2f}",
        "CPN_RIM": f"{rim(HOME, EM_MATCHED):.3f}",
        "CPN_RIMB": f"{rim(HOME, EM_MATCHED) / LINE_W:.2f}",
        "CPN_RELIEF": f"{RELIEF:g}",
        "CPN_RELIEF_L": f"{RELIEF / LAYER_H:.0f}",
        "CPN_DEPTH": f"{DEPTH:g}",
        "CPN_DEPTH_L": f"{DEPTH / LAYER_H:.0f}",
        "CPN_FIVE_CAP": f"{cap_of(em_for_beads(5.0)):.3f}",
        "CPN_FIVE_RIM": f"{rim(HOME, em_for_beads(5.0)):.3f}",
        "CPN_CO2_BEADS": f"{stroke_of('co2', EM_MATCHED) / LINE_W:.2f}",
        "CPN_CO2_RIM": f"{rim('co2', EM_MATCHED):.3f}",
        "CPN_WALLSTACK": f"{WALLS * LINE_W:.2f}",
        "CPN_RIM_SHORT": f"{_ring.WORD_MARGIN - rim(HOME, EM_MATCHED):.3f}",
    }
    for n, chip in enumerate(CHIPS, 1):
        variables.update({
            f"CPN_NAME{n}": chip.name,
            f"CPN_EM{n}": f"{chip.em:.3f}",
            f"CPN_CAP{n}": f"{cap_of(chip.em):.3f}",
            f"CPN_BEADS{n}": f"{stroke_of(chip.station, chip.em) / LINE_W:.2f}",
            f"CPN_RIM{n}": f"{rim(chip.station, chip.em):.3f}",
            f"CPN_RIMB{n}": f"{rim(chip.station, chip.em) / LINE_W:.2f}",
            f"CPN_DEPTH{n}": f"{chip.depth / LAYER_H:.0f}",
            f"CPN_RELIEF{n}": f"{chip.relief / LAYER_H:.0f}",
        })
    substitute_md(_here.parent / "README.md", variables=variables)
    print("-> README.md")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main()
