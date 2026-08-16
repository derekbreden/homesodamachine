"""Port-ring test coupons — the chip's lettering, swept, on a comb that prints instead of a chip.

A port ring is the machine's first two-colour print and its finest work: a `WORD_CAP` cap in
`WORD_DEPTH` of second filament, off a 0.2 nozzle. Four figures strike that lettering — the em,
how deep the recess goes, how far the word stands past the face, and how much air the recess
leaves round it. Each of the four is one coupon, swept across a comb of teeth.

ONE COUPON MOVES ONE FIGURE. The other three stand at the part's own numbers, read out of
`port_ring`, so a tooth that comes out badly names what did it.

A TOOTH IS THE BAND, at full size. The lettering a customer sees is the strip between the
fitting's flange edge and the chip's own top edge — `port_ring.word_band` — and three numbers
say how it prints: the cap, the rim of chip standing over it, and the strokes' width against the
bead. A tooth carries all three. Below the flange the chip is hidden under it, and a tooth
carries `BELOW` of that instead of all of it.

    THE RIM IS THE TIGHT ONE. The band is fixed — the flange sets its bottom, the box's top face
    sets `port_ring.RISE` over it — so a cap grows out of the rim of chip above it. `cap` sweeps
    the em and the rim comes down with it.

THE BEAD IS 0.22 AND NOT 0.2. `port_ring.WORD_NOZZLE` is the orifice; `LINE_W` is what the
slicer plans to lay through it, squashed to `LAYER_H` against the layer below. `LINE_W` is also
the divisor: a feature's width over the bead is how many perimeters fit in it, and the remainder
is gap fill or nothing. `cap`'s ems are struck on whole and half multiples of it.

Coordinate frame — the chip's, so a tooth prints the way a chip does:
  Y = the thickness. y = 0 is the face that lands on the plate, y = `port_ring.THICK` the face
      the word comes out of. A relief stands past it.
  +Z = up the band. X runs along the word, which reads along −X.

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

# THE PLATE THESE ARE READ ON, and the part states it — `port_ring.WORD_BEAD` and `WORD_LAYER`
# are read off `../port-ring-water.3mf` and gate the chip's own strokes and bridges. A coupon
# struck on one profile and printed on another measures the profile, and a coupon carrying its
# own copy of the profile measures whichever copy was updated last.
#   The bead is not the nozzle. The orifice meters; the bead is laid at the width the profile
# asks for and squashed to `LAYER_H` against the layer below. The slicer's own arithmetic runs on
# it: a feature's width over the bead is how many perimeters fit, and what the division leaves is
# gap fill or nothing.
LINE_W = _ring.WORD_BEAD
LAYER_H = _ring.WORD_LAYER
# How many perimeters the profile lays before it falls back to infill. A strip narrower than
# `WALLS * LINE_W` comes out all wall and no middle.
WALLS = 4
# WHAT A LAYER CARRYING BOTH COLOURS COSTS. `filament_maps` on that plate stands both spools on
# ONE nozzle, so a colour change on a layer is a filament change, and `flush_volumes_matrix`
# charges it 900 mm³ black-to-white and 90 back. Every layer from the recess floor up to the
# chip's face carries both colours; a layer above the face, where a relief stands alone, and a
# layer below the floor carry one.
FLUSH = 900.0 + 90.0

# THE SPECIMEN. `FLAVOR` is the longest of the five words — the one that can run out of chip —
# and carries two counters that close (O, R), one that comes to a point (A), and two diagonals
# meeting in a stroke narrower than either (V). Two of the five chips wear it.
WORD = "FLAVOR"
# Its narrowest stroke at `port_ring.WORD_SIZE`, off the built letterforms. Every em on the `cap`
# coupon is solved back from this figure. `port_ring.WORD_MIN_STROKE` is a different measurement
# — the narrowest across all five words, which is CO2's, 4% finer than this at the same em.
# `specimen_holds` reads this one back off the solid.
SPECIMEN_STROKE = 0.802588
# THE NARROWEST THING ON A CHIP IS NOT A STROKE. It is the bridge of chip standing between two
# letters, and `port_ring.WORD_MIN_BRIDGE` is the narrowest of them across all five words: 1.57
# beads, where the narrowest stroke is 3.65. The strokes are the word's colour and the bridges
# are the chip's, both off the same nozzle at the same width, so the bridge runs out first.
#   THE WORD IT BELONGS TO IS THE SPECIMEN — it is FLAVOR's, between the L and the A, which is
# why the sweep can be bounded by it. `specimen_holds` measures the specimen's own bridge and
# reads it against this, so a face that resolves elsewhere and moves the minimum onto another
# word is caught here. Every `fit` tooth takes twice its own figure out of it.
SPECIMEN_GAP = _ring.WORD_MIN_BRIDGE
# The specimen's narrowest stroke on each tooth of `cap`, in beads. A whole number is a stroke
# the slicer spends entirely on perimeters; a half is one it cannot. `port_ring.WORD_SIZE` lands
# at 3.65 and stands on the coupon beside them.
BEADS = (2.5, 3.0, 4.0, 4.5)
# How far the word stands PAST the chip's face, in mm — 0 is the part as it is, and each of the
# rest is 1 to 4 whole layers at `LAYER_H`. A raised word's visible edge is its own free edge; a
# flush one's is a seam against the chip's. A raised layer carries the word's colour alone.
RELIEFS = (0.0, 0.08, 0.16, 0.24, 0.32)
# How deep the recess is cut, in mm — 3, 6, 9, 12 and 18 whole layers. `port_ring.WORD_DEPTH` is
# 1.0, which at this layer height is 12½ and stands between the fourth and fifth of them. Each
# is both a count of layers of the second filament standing over the first AND the count of
# layers that carry two colours, which is what `FLUSH` is charged for.
DEPTHS = (0.24, 0.48, 0.72, 0.96, 1.44)
# The air the recess leaves round the word, all the way round, in mm. The part leaves none — it
# cuts its recess with the word itself. TWO NOZZLES HOLD ONE ORIGIN BETWEEN THEM, and what they
# are out by lands here: a seam that closes on one side of every stroke and opens on the other.
# The sweep runs up past `gap_ceiling` — the air that takes `SPECIMEN_GAP` down to one bead —
# so the tooth where the chip stops bridging between two letters is on the comb.
FITS = (0.0, 0.02, 0.04, 0.06, 0.08)
# How the recess is grown: the letterforms unioned with copies of themselves standing round a
# circle of the offset. Eight of them leave a corner short by 7.6% of the offset, which at the
# widest tooth here is 6 µm.
KERNEL_SIDES = 8

# THE FILAMENT PAIR. Two of the five chips are `flavor` — white lettering on black — which is
# the direction the second colour stands over the first rather than beside it. The other three
# letter black on a colour.
FLUID = "flavor"

Coupon = collections.namedtuple("Coupon", "figure unit values")
COUPONS = collections.OrderedDict((
    ("cap", Coupon("the em the word is set at", "mm em", None)),      # solved from BEADS below
    ("relief", Coupon("how far the word stands past the face", "mm", RELIEFS)),
    ("depth", Coupon("how deep the recess is cut", "mm", DEPTHS)),
    ("fit", Coupon("the air the recess leaves round the word", "mm", FITS)),
))
STEPS = {kind: _here.parent / f"port-ring-coupon-{kind}.step" for kind in COUPONS}

# What stands under a tooth's word: twice the least the part allows over a cap, so of a tooth's
# two rims the top one is the tight one — as it is on the chip, where 30 mm of chip stands below
# the word and the flange hides it.
BELOW = 2.0 * _ring.WORD_MARGIN
# The air between two teeth: four wall loops on each facing edge and a bead of nothing between
# them. Under this the two edges come out as one wall.
TOOTH_GAP = 2.0 * WALLS * LINE_W + LINE_W
# The spine that holds a coupon together: its two edges' wall stacks, and the identifying hole
# between them.
ID_HOLE_D = 2.0
SPINE_W = 2.0 * WALLS * LINE_W + ID_HOLE_D
ID_PITCH = 2.0 * ID_HOLE_D
# WHICH COUPON THIS IS, counted in holes down the spine — `cap` one, `fit` four. The four combs
# are otherwise one shape, and three of the four sweep something invisible.
ID_ORDER = {kind: n for n, kind in enumerate(COUPONS, 1)}
# WHICH TOOTH THIS IS, counted in steps down the free end: tooth 1 is the shortest and each one
# below it is a step longer, so a coupon's right edge is a staircase. Nothing on a tooth is
# marked in the second colour, which two of these coupons sweep. One step is the tooth end's own
# wall stack and a bead past it.
TOOTH_STEP = WALLS * LINE_W + LINE_W


def band() -> float:
    """The strip of chip a customer reads the lettering in, top to bottom. The flange's edge
    stands at its bottom and the box's top face at its top."""
    lo, hi = _ring.word_band("flavor-a")
    return hi - lo


def cap_of(em: float) -> float:
    """The cap height one em is worth, off the part's own pair."""
    return em * _ring.WORD_CAP / _ring.WORD_SIZE


def stroke_of(em: float) -> float:
    """The specimen's narrowest stroke at one em. A letterform is a scale of itself, so one
    measured figure carries up and down."""
    return em * SPECIMEN_STROKE / _ring.WORD_SIZE


def gap_of(em: float) -> float:
    """The chip's narrowest bridge between two of the specimen's letters, at one em."""
    return em * SPECIMEN_GAP / _ring.WORD_SIZE


def gap_ceiling() -> float:
    """The most air a recess takes before that bridge falls to one bead. A `fit` tooth takes
    twice its own figure out of the bridge, one side of it per letter."""
    return (gap_of(_ring.WORD_SIZE) - LINE_W) / 2.0


def measured_gap(em: float) -> float:
    """That bridge off the letterforms this machine builds — the least distance between two
    solids of the built word, taken between neighbours in the order they set."""
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    letters = sorted(_letters(em, _ring.WORD_DEPTH).Solids(),
                     key=lambda s: s.BoundingBox().xmin)
    out = []
    for a, b in zip(letters, letters[1:]):
        d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
        d.Perform()
        out.append(d.Value())
    return min(out) if out else 0.0


def em_for_beads(beads: float) -> float:
    """The em whose narrowest stroke is `beads` of `LINE_W` — `stroke_of` solved the other way,
    which is how `cap`'s teeth are struck."""
    return beads * LINE_W * _ring.WORD_SIZE / SPECIMEN_STROKE


def rim(em: float) -> float:
    """The chip standing over the cap with the word centred in the band.
    `port_ring.WORD_MARGIN` is the least the part allows."""
    return (band() - cap_of(em)) / 2.0


EMS = tuple(sorted([em_for_beads(b) for b in BEADS] + [_ring.WORD_SIZE]))
COUPONS["cap"] = COUPONS["cap"]._replace(values=EMS)


def spec(kind: str, value: float) -> tuple:
    """One tooth as `(em, depth, relief, fit)`. The three this coupon does not sweep stand at
    the part's own figures."""
    em, depth, relief, fit = _ring.WORD_SIZE, _ring.WORD_DEPTH, 0.0, 0.0
    if kind == "cap":
        em = value
    elif kind == "relief":
        relief = value
    elif kind == "depth":
        depth = value
    elif kind == "fit":
        fit = value
    else:
        raise ValueError(f"no coupon sweeps {kind!r}")
    return (em, depth, relief, fit)


def word_width(em: float) -> float:
    """What the specimen measures across at one em, off the part's own figure for it."""
    return _ring.WORD_WIDTHS[WORD] * em / _ring.WORD_SIZE


def _letters(em: float, thickness: float, grow: float = 0.0):
    """The specimen flat in XY, extruded `thickness` along +Z, standing `grow` wider all round.

    The offset is a union: the letterforms and `KERNEL_SIDES` copies of themselves at `grow`
    round a circle. Every face it comes out with is one the letterform already carried or a plane
    where two copies meet. A counter closes in by the figure its outline stands out."""
    flat = cq.Workplane("XY").text(WORD, em, thickness, font=_ring.WORD_FONT,
                                   kind=_ring.WORD_KIND, halign="center", valign="center").val()
    if grow <= 0.0:
        return flat
    out = flat
    for i in range(KERNEL_SIDES):
        a = 2.0 * math.pi * i / KERNEL_SIDES
        out = out.fuse(flat.translate(cq.Vector(grow * math.cos(a), grow * math.sin(a), 0.0)))
    return out.clean()


def build_word(em: float, depth: float, relief: float, cx: float, cz: float, grow: float = 0.0):
    """One tooth's word where the tooth carries it: `depth` of it in the recess, `relief` of it
    standing past the face, and `port_ring.WORD_TIE` of bar behind tying the letters into one
    solid the way the part's does.

    Turned to face the customer by the part's own two rotations, then squared on the cap box the
    solid came out with — `valign` centres on the font's metrics, which are not it."""
    solid = (cq.Workplane(obj=_letters(em, depth + relief, grow))
             .rotate((0, 0, 0), (1, 0, 0), 90.0)
             .rotate((0, 0, 0), (0, 0, 1), 180.0).val())
    bb = solid.BoundingBox()
    solid = solid.translate(cq.Vector(cx - (bb.xmin + bb.xmax) / 2.0,
                                      _ring.THICK - depth - bb.ymin,
                                      cz - (bb.zmin + bb.zmax) / 2.0))
    b = solid.BoundingBox()
    tie = cq.Solid.makeBox(
        b.xlen, _ring.WORD_TIE, _ring.WORD_TIE_H + 2.0 * grow,
        cq.Vector(b.xmin, _ring.THICK - depth - _ring.WORD_TIE, b.zmin))
    return solid.fuse(tie).clean()


def _tooth_length(kind: str, n: int) -> float:
    """Tooth `n`'s run out from the spine: the widest word this coupon carries with the chip's
    own margin either side, and `n` steps of tail. Every tooth on a coupon holds its word in the
    same place; the tail stands behind it."""
    widest = max(word_width(spec(kind, v)[0]) for v in COUPONS[kind].values)
    return widest + 2.0 * _ring.WORD_MARGIN + n * TOOTH_STEP


def build_coupon(kind: str) -> tuple:
    """One coupon as `(comb, words)` — the chip-coloured comb, and every word standing on it.

    Teeth run top to bottom in the order the values sweep, tooth 1 at the top. A tooth stands as
    tall as its own rim, cap and `BELOW`, so on `cap` the teeth are different heights."""
    values = COUPONS[kind].values
    ems = [spec(kind, v)[0] for v in values]
    heights = [rim(em) + cap_of(em) + BELOW for em in ems]
    total = sum(heights) + (len(values) - 1) * TOOTH_GAP

    word_cx = _ring.WORD_MARGIN + max(word_width(em) for em in ems) / 2.0
    bars, words, z = [], [], total
    for n, (value, em, height) in enumerate(zip(values, ems, heights), 1):
        _em, depth, relief, fit = spec(kind, value)
        z -= height
        bar = cq.Solid.makeBox(_tooth_length(kind, n), _ring.THICK, height,
                               cq.Vector(0.0, 0.0, z))
        cz = z + height - rim(em) - cap_of(em) / 2.0
        bar = bar.cut(build_word(em, depth, relief, word_cx, cz, grow=fit))
        bars.append(bar)
        words.append(build_word(em, depth, relief, word_cx, cz))
        z -= TOOTH_GAP

    spine = cq.Solid.makeBox(SPINE_W, _ring.THICK, total, cq.Vector(-SPINE_W, 0.0, 0.0))
    for i in range(ID_ORDER[kind]):
        spine = spine.cut(cq.Solid.makeCylinder(
            ID_HOLE_D / 2.0, _ring.THICK, cq.Vector(-SPINE_W / 2.0, 0.0, ID_PITCH * (i + 1)),
            cq.Vector(0.0, 1.0, 0.0)))
    comb = spine
    for bar in bars:
        comb = comb.fuse(bar)
    return (comb.clean(), cq.Compound.makeCompound(words))


def _filament(rgb) -> "cq.Color":
    return cq.Color(*(c / 255.0 for c in rgb))


def build_part(kind: str) -> cq.Assembly:
    """One coupon as it prints: the comb off the chip's spool, every word off the other."""
    comb, words = build_coupon(kind)
    a = cq.Assembly()
    a.add(comb, name=f"port-ring-coupon-{kind}", color=_filament(_rear.chip_color(FLUID)))
    a.add(words, name=f"port-ring-coupon-{kind}-word",
          color=_filament(_rear.word_color(FLUID)))
    return a


def specimen_holds():
    """Hold `SPECIMEN_STROKE` to the letterforms this machine builds.

    `port_ring.WORD_FONT` names a face this repo does not ship, and every em on `cap` is solved
    back from this one figure. A machine that resolves the face to something else strikes the
    whole sweep on a bead count the stroke never had."""
    got = _ring.min_stroke(build_word(_ring.WORD_SIZE, _ring.WORD_DEPTH, 0.0, 0.0, 0.0))
    if abs(got - SPECIMEN_STROKE) > 1e-3:
        raise ValueError(
            f"'{WORD}' carries a {got:.4f} mm narrowest stroke at em {_ring.WORD_SIZE:g} and "
            f"`SPECIMEN_STROKE` claims {SPECIMEN_STROKE:.4f} — `{_ring.WORD_FONT}` did not "
            f"resolve to the face these ems were solved from.")
    gap = measured_gap(_ring.WORD_SIZE)
    if abs(gap - SPECIMEN_GAP) > 1e-3:
        raise ValueError(
            f"'{WORD}' leaves a {gap:.4f} mm bridge between its closest two letters at em "
            f"{_ring.WORD_SIZE:g} and `SPECIMEN_GAP` claims {SPECIMEN_GAP:.4f} — the face that "
            f"resolved sets its letters at another fit, and `fit`'s ceiling is struck on a "
            f"bridge that is not there.")


def recess_holds():
    """Hold every recess to the word it is cut for.

    `fit` offsets the letterforms outward to cut the recess and lays the word in unoffset. A
    counter offset the wrong way comes back as a recess that closes on the word — the O filled
    in — and no extent carries that, so what is read is the word standing wholly inside its
    hole."""
    for kind in COUPONS:
        for value in COUPONS[kind].values:
            em, depth, relief, fit = spec(kind, value)
            word = build_word(em, depth, relief, 0.0, 0.0)
            recess = build_word(em, depth, relief, 0.0, 0.0, grow=fit)
            proud = word.cut(recess).Volume()
            if proud > 1e-6:
                raise ValueError(
                    f"the {kind} coupon's {value:g} tooth leaves {proud:.4f} mm³ of word "
                    f"standing outside the recess cut for it — the {fit:g} mm offset did not "
                    f"carry every counter the way its outline went.")


def band_holds():
    """Hold every word on every comb to the rim it is supposed to stand under.

    A tooth is the band only if the chip over its cap measures what the chip's own does. The
    words come back off the STEP sorted down the comb, which is the order the teeth are cut in,
    and each one's cap top is read against its own tooth's top edge less that tooth's rim."""
    for kind, step in STEPS.items():
        values = COUPONS[kind].values
        ems = [spec(kind, v)[0] for v in values]
        heights = [rim(em) + cap_of(em) + BELOW for em in ems]
        top = sum(heights) + (len(values) - 1) * TOOTH_GAP

        words = sorted((s for s in import_step(str(step)).val().Solids()
                        if s.BoundingBox().zlen < max(heights)),
                       key=lambda s: -s.BoundingBox().zmax)
        if len(words) != len(values):
            raise ValueError(
                f"{step.name} sorts to {len(words)} words down the comb and the {kind} coupon "
                f"cuts {len(values)} teeth — a word stands as tall as the tooth holding it.")
        for n, (value, em, height, word) in enumerate(zip(values, ems, heights, words), 1):
            _em, depth, relief, _fit = spec(kind, value)
            bb = word.BoundingBox()
            # A micron, which is what a STEP round trip holds a letterform's extent to and is
            # a two-hundredth of the bead that lays it.
            for what, want, got in (
                    ("tops its cap at", top - rim(em), bb.zmax),
                    ("runs the word", depth + _ring.WORD_TIE + relief, bb.ylen),
                    ("faces the word out at", _ring.THICK + relief, bb.ymax)):
                if abs(got - want) > 1e-3:
                    raise ValueError(
                        f"the {kind} coupon's tooth {n} {what} {got:.4f} and its "
                        f"{value:g} {COUPONS[kind].unit} puts it at {want:.4f} — the tooth is "
                        f"not the figure the comb is read as sweeping.")
            top -= height + TOOTH_GAP


def coupons_hold():
    """Hold each coupon's own STEP to the comb it is: one solid to pick up, one word per tooth,
    and the chip's thickness plus whatever relief that coupon stands its words at."""
    for kind, step in STEPS.items():
        shape = import_step(str(step)).val()
        solids = shape.Solids()
        want = len(COUPONS[kind].values) + 1
        if len(solids) != want:
            raise ValueError(
                f"the {kind} coupon is a comb and {len(COUPONS[kind].values)} words and "
                f"{step.name} carries {len(solids)} solids — a tooth has lost its word or the "
                f"comb has come apart into teeth.")
        thick = _ring.THICK + max(spec(kind, v)[2] for v in COUPONS[kind].values)
        got = shape.BoundingBox().ylen
        if abs(got - thick) > 1e-6:
            raise ValueError(
                f"the {kind} coupon stands {got:.4f} mm off the plate and the chip plus the "
                f"relief it carries is {thick:.4f} — a coupon printed at another thickness lays "
                f"a different number of layers over the word.")


def selftest() -> int:
    """Each coupon against the band it is read in, the chip it stands for, and the plate."""
    fails = []
    for kind, coupon in COUPONS.items():
        for value in coupon.values:
            em, depth, relief, fit = spec(kind, value)
            room = _ring.od("union") - 2.0 * _ring.WORD_MARGIN
            if word_width(em) > room + 1e-9:
                fails.append(
                    f"the {kind} coupon's {value:g} tooth letters '{WORD}' "
                    f"{word_width(em):.3f} mm across a chip that leaves {room:.3f} — the coupon "
                    f"sweeps a word no chip can carry")
            if cap_of(em) >= band() - 1e-9:
                fails.append(
                    f"the {kind} coupon's {value:g} tooth stands a {cap_of(em):.3f} mm cap in a "
                    f"band {band():.3f} mm tall and leaves no rim at all")
            if depth + _ring.WORD_TIE >= _ring.THICK:
                fails.append(
                    f"the {kind} coupon's {value:g} tooth cuts {depth + _ring.WORD_TIE:g} mm of "
                    f"recess into a {_ring.THICK:g} mm chip, and what stands behind the "
                    f"lettering is the plate")
            if gap_of(em) - 2.0 * fit <= 0.0:
                fails.append(
                    f"the {kind} coupon's {value:g} tooth opens the recess {fit:g} mm all round "
                    f"a {gap_of(em):.3f} mm bridge between two letters — the air meets in the "
                    f"middle and the two recesses come out as one hole")
            if kind == "cap" and gap_of(em) < LINE_W - 1e-9:
                fails.append(
                    f"the cap coupon's {value:g} em leaves a {gap_of(em):.3f} mm bridge between "
                    f"two of its letters and the bead is {LINE_W:g} — the chip does not reach "
                    f"between them, and the tooth reads a word no chip carries")
            if kind in ("relief", "depth") and abs(value / LAYER_H
                                                   - round(value / LAYER_H)) > 1e-9:
                fails.append(
                    f"the {kind} coupon steps to {value:g} mm on a plate laying {LAYER_H:g} mm "
                    f"layers — the slicer lands that step on {value / LAYER_H:.2f} layers and "
                    f"rounds it, and the tooth is not the figure it is read as")
    if TOOTH_GAP <= 2.0 * WALLS * LINE_W:
        fails.append(
            f"a {TOOTH_GAP:g} mm gap between teeth does not stand {WALLS} wall loops on each "
            f"facing edge, and the two teeth come out one")
    if SPINE_W - ID_HOLE_D < 2.0 * WALLS * LINE_W - 1e-9:
        fails.append(
            f"a Ø{ID_HOLE_D:g} hole in a {SPINE_W:g} mm spine leaves "
            f"{(SPINE_W - ID_HOLE_D) / 2.0:.3f} mm of wall either side and the profile lays "
            f"{WALLS * LINE_W:.2f}")
    if len(COUPONS) != len(set(ID_ORDER.values())):
        fails.append("two coupons are counted in the same number of spine holes")
    if not min(FITS) < gap_ceiling() < max(FITS):
        fails.append(
            f"the fit coupon sweeps {min(FITS):g} to {max(FITS):g} mm and the bridge between "
            f"two letters falls to one bead at {gap_ceiling():.3f} — the comb stands wholly on "
            f"one side of the figure it is printed to find")
    for _what, fn in (("specimen_holds", specimen_holds),
                      ("recess_holds", recess_holds),
                      ("band_holds", band_holds),
                      ("coupons_hold", coupons_hold)):
        try:
            fn()
        except Exception as exc:                                     # noqa: BLE001
            fails.append(str(exc))
    for line in fails:
        print(f"FAIL {line}")
    if not fails:
        print("ok  port-ring-coupons  " + ", ".join(
            f"{kind} {len(c.values)} teeth" for kind, c in COUPONS.items())
            + f" — '{WORD}' on a {LINE_W:g} mm bead, {band():.3f} mm band")
    return 1 if fails else 0


def main():
    volumes, sizes = {}, {}
    for kind, coupon in COUPONS.items():
        comb, words = build_coupon(kind)
        bb = comb.BoundingBox()
        volumes[kind] = (comb.Volume() / 1000.0, words.Volume() / 1000.0)
        sizes[kind] = f"{bb.xlen:.1f} × {bb.zlen:.1f}"
        print(f"Port-ring coupon — {kind}: {coupon.figure}")
        print(f"  {len(coupon.values)} teeth: "
              + ", ".join(f"{v:g}" for v in coupon.values) + f" {coupon.unit}")
        print(f"  {bb.xlen:.2f} × {bb.zlen:.2f} × {_ring.THICK:g} mm, "
              f"{volumes[kind][0]:.2f} + {volumes[kind][1]:.2f} cm³")
        for n, value in enumerate(coupon.values, 1):
            em, depth, relief, fit = spec(kind, value)
            print(f"    {n}  em {em:.3f}  cap {cap_of(em):.3f}  "
                  f"stroke {stroke_of(em):.3f} = {stroke_of(em) / LINE_W:.2f} beads  "
                  f"rim {rim(em):.3f} = {rim(em) / LINE_W:.2f}  "
                  f"bridge {gap_of(em) - 2.0 * fit:.3f} = "
                  f"{(gap_of(em) - 2.0 * fit) / LINE_W:.2f}  "
                  f"depth {depth:g} = {depth / LAYER_H:.1f} two-colour layers  "
                  f"relief {relief:g}  fit {fit:g}")
        export_assembly(build_part(kind), str(STEPS[kind]))
        print(f"-> {STEPS[kind].name}")

    total = sum(c + w for c, w in volumes.values())
    variables = {
        "CPN_LINE_W": f"{LINE_W:g}",
        "CPN_LAYER_H": f"{LAYER_H:g}",
        "CPN_WALLS": f"{WALLS:g}",
        "CPN_WORD": WORD,
        "CPN_STROKE": f"{SPECIMEN_STROKE:.3f}",
        "CPN_BAND": f"{band():.3f}",
        "CPN_BELOW": f"{BELOW:g}",
        "CPN_TOOTH_GAP": f"{TOOTH_GAP:g}",
        "CPN_SPINE": f"{SPINE_W:g}",
        "CPN_STEP": f"{TOOTH_STEP:g}",
        "CPN_HOLE": f"{ID_HOLE_D:g}",
        "CPN_TEETH": f"{sum(len(c.values) for c in COUPONS.values())}",
        "CPN_VOL": f"{total:.2f}",
        "CPN_FLUID": FLUID,
        "CPN_CHIP_FILAMENT": _rear.chip_filaments[FLUID][0],
        "CPN_PART_EM": f"{_ring.WORD_SIZE:g}",
        "CPN_PART_BEADS": f"{stroke_of(_ring.WORD_SIZE) / LINE_W:.2f}",
        "CPN_PART_RIM": f"{rim(_ring.WORD_SIZE):.3f}",
        "CPN_FOUR_EM": f"{em_for_beads(4.0):.3f}",
        "CPN_FOUR_CAP": f"{cap_of(em_for_beads(4.0)):.3f}",
        "CPN_FOUR_RIM": f"{rim(em_for_beads(4.0)):.3f}",
        "CPN_MARGIN": f"{_ring.WORD_MARGIN:g}",
        "CPN_PART_DEPTH": f"{_ring.WORD_DEPTH:g}",
        "CPN_PART_LAYERS": f"{_ring.WORD_DEPTH / LAYER_H:.1f}",
        "CPN_FLUSH": f"{FLUSH:g}",
        "CPN_TIE": f"{_ring.WORD_TIE:g}",
        "CPN_THICK": f"{_ring.THICK:g}",
        "CPN_CO2_BEADS": f"{_ring.WORD_MIN_STROKE / LINE_W:.2f}",
        "CPN_GAP": f"{SPECIMEN_GAP:.3f}",
        "CPN_GAP_BEADS": f"{SPECIMEN_GAP / LINE_W:.2f}",
        "CPN_GAP_CEIL": f"{gap_ceiling():.3f}",
        "CPN_KERNEL": f"{KERNEL_SIDES:g}",
    }
    # The `cap` teeth, each one solved rather than chosen — what the README's table reads.
    for n, em in enumerate(EMS, 1):
        variables.update({
            f"CPN_EM{n}": f"{em:.3f}",
            f"CPN_CAP{n}": f"{cap_of(em):.3f}",
            f"CPN_BEADS{n}": f"{stroke_of(em) / LINE_W:.2f}",
            f"CPN_RIM{n}": f"{rim(em):.3f}",
            f"CPN_RIMB{n}": f"{rim(em) / LINE_W:.2f}",
            f"CPN_WIDE{n}": f"{word_width(em):.2f}",
            f"CPN_GAPB{n}": f"{gap_of(em) / LINE_W:.2f}",
        })
    for kind, (comb_v, word_v) in volumes.items():
        variables[f"CPN_VOL_{kind.upper()}"] = f"{comb_v + word_v:.2f}"
        variables[f"CPN_SIZE_{kind.upper()}"] = sizes[kind]
    substitute_md(_here.parent / "README.md", variables=variables)
    print("-> README.md")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main()
