"""Port-ring test coupons — the chip itself, cut five times over with one figure moved.

A COUPON IS A PORT RING. Same D outline, same bore, same thickness, same word standing in the
same band, off the same two spools — `port_ring`'s own builders cut it. What a coupon changes is
one figure of the lettering, and nothing else, so a chip that comes out badly names what did it.
It drops into the wall's pocket like any other and can be read against the machine rather than
against a drawing.

Four figures strike that lettering, and each is one coupon of five chips:

    cap     the em the word is set at
    relief  how far the word stands past the chip's face
    depth   how deep its recess is cut
    fit     the air the recess leaves round it

    THE RIM IS THE TIGHT ONE. The band a word stands in — `port_ring.word_band`, between the
    fitting's flange edge and the chip's top edge — is fixed at both ends, so a cap grows out of
    the rim of chip above it. `cap` sweeps the em and the rim comes down with it.

THE BEAD IS 0.22 AND NOT 0.2. `port_ring.WORD_NOZZLE` is the orifice; `port_ring.WORD_BEAD` is
what the slicer plans to lay through it, squashed to `WORD_LAYER` against the layer below. The
bead is also the divisor: a feature's width over it is how many perimeters fit, and the remainder
is gap fill or nothing. `cap`'s ems are struck on whole and half multiples of it.

WHICH CHIP IS WHICH IS ON ITS BACK. Two rows of dimples in the face that lands on the pocket
floor — the coupon above, the chip below — so the face a customer reads carries nothing a real
chip does not.

Coordinate frame — `port_ring`'s, one chip per station along +X:
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

# THE STATION A COUPON IS A CHIP OF. `flavor-a` is the demanding one: FLAVOR is the longest of
# the five words, the one that can run out of chip, and it carries two counters that close (O, R),
# one that comes to a point (A), and two diagonals meeting in a stroke narrower than either (V).
# Its pair is white lettering on black, which is the direction the second colour stands OVER the
# first rather than beside it. Two of the five chips are this one.
STATION = "flavor-a"
WORD = _ring.STATIONS[STATION].word
FLUID = _ring.FLUIDS[STATION]

# THE PLATE THESE ARE READ ON, and the part states it — `port_ring.WORD_BEAD` and `WORD_LAYER`
# are read off `../port-ring-water.3mf` and gate the chip's own strokes and bridges. A coupon
# struck on one profile and printed on another measures the profile.
LINE_W = _ring.WORD_BEAD
LAYER_H = _ring.WORD_LAYER
# How many perimeters the profile lays before it falls back to infill.
WALLS = 4
# WHAT A LAYER CARRYING BOTH COLOURS COSTS. `filament_maps` on that plate stands both spools on
# ONE nozzle, so a colour change on a layer is a filament change, and `flush_volumes_matrix`
# charges it 900 mm³ black-to-white and 90 back. Every layer from the recess floor up to the
# chip's face carries both colours; the layers below the floor, and the layers above the face
# where a relief stands alone, carry one.
FLUSH = 900.0 + 90.0

# The specimen's narrowest stroke at `port_ring.WORD_SIZE`, off the built letterforms. Every em on
# the `cap` coupon is solved back from this figure. `port_ring.WORD_MIN_STROKE` is a different
# measurement — the narrowest across all five words, which is CO2's, 4% finer than this at the
# same em. `specimen_holds` reads this one back off the solid.
SPECIMEN_STROKE = 0.802588
# THE NARROWEST THING ON A CHIP IS NOT A STROKE. It is the bridge of chip standing between two
# letters, and `port_ring.WORD_MIN_BRIDGE` is the narrowest of them across all five words: 1.57
# beads, where the narrowest stroke is 3.65. The strokes are the word's colour and the bridges
# are the chip's, both off the same nozzle at the same width, so the bridge runs out first.
#   THE WORD IT BELONGS TO IS THIS SPECIMEN — it is FLAVOR's, between the L and the A, which is
# what lets `fit` be bounded by it. `specimen_holds` measures the specimen's own bridge and reads
# it against this, so a face resolving elsewhere and moving the minimum onto another word is
# caught here. Every `fit` chip takes twice its own figure out of it.
SPECIMEN_GAP = _ring.WORD_MIN_BRIDGE

# The specimen's narrowest stroke on each chip of `cap`, in beads. A whole number is a stroke the
# slicer spends entirely on perimeters; a half is one it cannot. `port_ring.WORD_SIZE` lands at
# 3.65 and stands on the coupon beside them.
BEADS = (2.5, 3.0, 4.0, 4.5)
# How far the word stands PAST the chip's face, in mm — 0 is the part as it is, and each of the
# rest is 1 to 4 whole layers at `LAYER_H`. A raised word's visible edge is its own free edge; a
# flush one's is a seam against the chip's. A raised layer carries the word's colour alone.
RELIEFS = (0.0, 0.08, 0.16, 0.24, 0.32)
# How deep the recess is cut, in mm — 3, 6, 9, 12 and 18 whole layers. `port_ring.WORD_DEPTH` is
# 1.0, which at this layer height is 12½ and stands between the fourth and fifth of them. Each is
# both a count of layers of the second filament standing over the first AND the count of layers
# carrying two colours, which is what `FLUSH` is charged for.
DEPTHS = (0.24, 0.48, 0.72, 0.96, 1.44)
# The air the recess leaves round the word, all the way round, in mm. The part leaves none — it
# cuts its recess with the word itself. TWO NOZZLES HOLD ONE ORIGIN BETWEEN THEM, and what they
# are out by lands here: a seam that closes on one side of every stroke and opens on the other.
# The sweep runs up past `gap_ceiling` — the air that takes `SPECIMEN_GAP` down to one bead — so
# the chip where nothing bridges between two letters is in the set.
FITS = (0.0, 0.02, 0.04, 0.06, 0.08)
# How the recess is grown: the letterforms unioned with copies of themselves standing round a
# circle of the offset. Eight of them leave a corner short by 7.6% of the offset, which at the
# widest chip here is 6 µm.
KERNEL_SIDES = 8

Coupon = collections.namedtuple("Coupon", "figure unit values")
COUPONS = collections.OrderedDict((
    ("cap", Coupon("the em the word is set at", "mm em", None)),      # solved from BEADS below
    ("relief", Coupon("how far the word stands past the face", "mm", RELIEFS)),
    ("depth", Coupon("how deep the recess is cut", "mm", DEPTHS)),
    ("fit", Coupon("the air the recess leaves round the word", "mm", FITS)),
))
STEPS = {kind: _here.parent / f"port-ring-coupon-{kind}.step" for kind in COUPONS}

# WHICH COUPON AND WHICH CHIP, counted in dimples in the face that lands on the pocket floor:
# the coupon in the upper row — `cap` one, `fit` four — and the chip in the lower. They are cut
# into the BACK, so the face a customer reads carries nothing a chip in the wall does not, and
# they are read by turning a coupon over. Five layers deep, which is a dimple the first layer
# cannot bridge over.
MARK_D = 1.5
MARK_DEPTH = 5.0 * LAYER_H
MARK_PITCH = 2.0 * MARK_D
# Where the two rows stand: under the bore, in the half circle, clear of the word's own band.
MARK_ROWS = (-12.0, -15.5)
# The air between two chips on a plate. Four wall loops on each facing edge, and a bead of
# nothing between them.
CHIP_GAP = 2.0 * WALLS * LINE_W + LINE_W


def band() -> float:
    """The strip of chip a customer reads the lettering in, top to bottom — the fitting's flange
    edge at its bottom and the box's top face at its top."""
    lo, hi = _ring.word_band(STATION)
    return hi - lo


def band_middle() -> float:
    """Where a cap box stands in it. `port_ring.build_word` centres on this and so does a
    coupon."""
    lo, hi = _ring.word_band(STATION)
    return (lo + hi) / 2.0


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
    """The most air a recess takes before that bridge falls to one bead. A `fit` chip takes twice
    its own figure out of the bridge, one side of it per letter."""
    return (gap_of(_ring.WORD_SIZE) - LINE_W) / 2.0


def em_for_beads(beads: float) -> float:
    """The em whose narrowest stroke is `beads` of `LINE_W` — `stroke_of` solved the other way,
    which is how `cap`'s chips are struck."""
    return beads * LINE_W * _ring.WORD_SIZE / SPECIMEN_STROKE


def rim(em: float) -> float:
    """The chip standing over the cap with the word centred in the band.
    `port_ring.WORD_MARGIN` is the least the part allows."""
    return (band() - cap_of(em)) / 2.0


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


EMS = tuple(sorted([em_for_beads(b) for b in BEADS] + [_ring.WORD_SIZE]))
COUPONS["cap"] = COUPONS["cap"]._replace(values=EMS)


def spec(kind: str, value: float) -> tuple:
    """One chip as `(em, depth, relief, fit)`. The three this coupon does not sweep stand at the
    part's own figures."""
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


def pitch() -> float:
    """Chip to chip along a coupon's row."""
    return _ring.od(_ring.family(STATION)) + CHIP_GAP


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


def build_word(em: float, depth: float, relief: float, grow: float = 0.0):
    """One chip's word where the chip carries it: `depth` of it in the recess, `relief` of it
    standing past the face, and `port_ring.WORD_TIE` of bar behind tying the letters into one
    solid the way the part's does.

    Turned to face the customer by the part's own two rotations, then squared on the cap box the
    solid came out with — `valign` centres on the font's metrics, which are not it — and stood in
    the middle of the band, where `port_ring.build_word` stands its own."""
    solid = (cq.Workplane(obj=_letters(em, depth + relief, grow))
             .rotate((0, 0, 0), (1, 0, 0), 90.0)
             .rotate((0, 0, 0), (0, 0, 1), 180.0).val())
    bb = solid.BoundingBox()
    solid = solid.translate(cq.Vector(-(bb.xmin + bb.xmax) / 2.0,
                                      _ring.THICK - depth - bb.ymin,
                                      band_middle() - (bb.zmin + bb.zmax) / 2.0))
    b = solid.BoundingBox()
    tie = cq.Solid.makeBox(
        b.xlen, _ring.WORD_TIE, _ring.WORD_TIE_H + 2.0 * grow,
        cq.Vector(b.xmin, _ring.THICK - depth - _ring.WORD_TIE, b.zmin))
    return solid.fuse(tie).clean()


def _marks(coupon: int, chip: int):
    """The two rows of dimples that say which coupon and which chip, cut into the face that lands
    on the pocket floor. Each row is centred on the bore's axis, so a row reads the same way up
    whichever end of it you start from."""
    out = []
    for row, count in zip(MARK_ROWS, (coupon, chip)):
        span = (count - 1) * MARK_PITCH
        for i in range(count):
            out.append(cq.Solid.makeCylinder(
                MARK_D / 2.0, MARK_DEPTH,
                cq.Vector(-span / 2.0 + i * MARK_PITCH, 0.0, row),
                cq.Vector(0.0, 1.0, 0.0)))
    return out


def build_ring(em: float, depth: float, relief: float, fit: float, coupon: int, chip: int):
    """One coupon chip: `port_ring`'s own outline and bore, the word's recess taken out of its
    face, and its two rows of marks taken out of its back."""
    diameter, top = _ring.outline(STATION)
    solid = _ring.build_outline(diameter, top, _ring.THICK)
    solid = solid.cut(cq.Solid.makeCylinder(
        _ring.bore_d(_ring.family(STATION)) / 2.0, _ring.THICK,
        cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 1.0, 0.0)))
    solid = solid.cut(build_word(em, depth, relief, grow=fit))
    for mark in _marks(coupon, chip):
        solid = solid.cut(mark)
    return solid


def build_coupon(kind: str) -> tuple:
    """One coupon as `(chips, words)` — five port rings in a row, and the word standing in each.

    Every chip is the same part but one figure, so the row is read straight across; the marks on
    their backs are what tells them apart once they are off the plate and in a hand."""
    values = COUPONS[kind].values
    chips, words = [], []
    for n, value in enumerate(values, 1):
        em, depth, relief, fit = spec(kind, value)
        at = cq.Vector(n * pitch(), 0.0, 0.0)
        chips.append(build_ring(em, depth, relief, fit,
                                _index(kind), n).translate(at))
        words.append(build_word(em, depth, relief).translate(at))
    return (cq.Compound.makeCompound(chips), cq.Compound.makeCompound(words))


def _index(kind: str) -> int:
    """Which coupon this is, counted in the upper row of marks."""
    return list(COUPONS).index(kind) + 1


def _filament(rgb) -> "cq.Color":
    return cq.Color(*(c / 255.0 for c in rgb))


def build_part(kind: str) -> cq.Assembly:
    """One coupon as it prints: five chips off one spool, five words off the other."""
    chips, words = build_coupon(kind)
    a = cq.Assembly()
    a.add(chips, name=f"port-ring-coupon-{kind}", color=_filament(_rear.chip_color(FLUID)))
    a.add(words, name=f"port-ring-coupon-{kind}-word", color=_filament(_rear.word_color(FLUID)))
    return a


def specimen_holds():
    """Hold `SPECIMEN_STROKE` and `SPECIMEN_GAP` to the letterforms this machine builds.

    `port_ring.WORD_FONT` names a face this repo does not ship, and every em on `cap` is solved
    back from the first figure while `fit`'s ceiling is struck on the second. A machine that
    resolves the face to something else sweeps a bead count the stroke never had."""
    got = _ring.min_stroke(build_word(_ring.WORD_SIZE, _ring.WORD_DEPTH, 0.0))
    if abs(got - SPECIMEN_STROKE) > 1e-3:
        raise ValueError(
            f"'{WORD}' carries a {got:.4f} mm narrowest stroke at em {_ring.WORD_SIZE:g} and "
            f"`SPECIMEN_STROKE` claims {SPECIMEN_STROKE:.4f} — `{_ring.WORD_FONT}` did not "
            f"resolve to the face these ems were solved from.")
    gap = measured_gap(_ring.WORD_SIZE)
    if abs(gap - SPECIMEN_GAP) > 1e-3:
        raise ValueError(
            f"'{WORD}' leaves a {gap:.4f} mm bridge between its closest two letters at em "
            f"{_ring.WORD_SIZE:g} and `port_ring.WORD_MIN_BRIDGE` is {SPECIMEN_GAP:.4f} — the "
            f"narrowest bridge on the wall is not this word's, and `fit`'s ceiling is struck on "
            f"a bridge that is not on the coupon.")


def recess_holds():
    """Hold every recess to the word it is cut for.

    `fit` offsets the letterforms outward to cut the recess and lays the word in unoffset. A
    counter offset the wrong way comes back as a recess that closes on the word — the O filled
    in — and no extent carries that, so what is read is the word standing wholly inside its
    hole."""
    for kind in COUPONS:
        for value in COUPONS[kind].values:
            em, depth, relief, fit = spec(kind, value)
            proud = build_word(em, depth, relief).cut(
                build_word(em, depth, relief, grow=fit)).Volume()
            if proud > 1e-6:
                raise ValueError(
                    f"the {kind} coupon's {value:g} chip leaves {proud:.4f} mm³ of word standing "
                    f"outside the recess cut for it — the {fit:g} mm offset did not carry every "
                    f"counter the way its outline went.")


def chips_hold():
    """Hold every coupon chip to the port ring it is one of, off its own STEP.

    A COUPON IS THE PART OR IT IS NOT A COUPON. The outline, the height and the thickness are
    extents of the chip solid and the bore is a turned face inside it, so a chip that would not
    drop into the wall's own pocket is caught here rather than at the wall. What is allowed to
    differ is the lettering, and that is read against the figure the coupon says it swept."""
    from _measuring import bores
    diameter, top = _ring.outline(STATION)
    for kind, step in STEPS.items():
        values = COUPONS[kind].values
        solids = import_step(str(step)).val().Solids()
        if len(solids) != 2 * len(values):
            raise ValueError(
                f"the {kind} coupon is {len(values)} chips and their words and {step.name} "
                f"carries {len(solids)} solids — a chip has lost its word.")
        chips = sorted((s for s in solids if s.BoundingBox().zlen > top),
                       key=lambda s: s.BoundingBox().xmin)
        words = sorted((s for s in solids if s.BoundingBox().zlen <= top),
                       key=lambda s: s.BoundingBox().xmin)
        for n, (value, cs, ws) in enumerate(zip(values, chips, words), 1):
            em, depth, relief, _fit = spec(kind, value)
            cb, wb = cs.BoundingBox(), ws.BoundingBox()
            for what, want, got in (
                    ("is", diameter, cb.xlen),
                    ("stands", diameter / 2.0 + top, cb.zlen),
                    ("runs", _ring.THICK, cb.ylen)):
                if abs(want - got) > 1e-3:
                    raise ValueError(
                        f"the {kind} coupon's chip {n} {what} {got:.4f} mm where a port ring "
                        f"{what} {want:.4f} — it is not the part it is a coupon of.")
            want_bore = _ring.bore_d(_ring.family(STATION))
            if not any(abs(2.0 * r - want_bore) <= 1e-3 for _axis, r in bores(cs)):
                raise ValueError(
                    f"the {kind} coupon's chip {n} turns no face at the wall's own "
                    f"Ø{want_bore:g} — it does not pass the barrel a port ring passes.")
            for what, want, got in (
                    ("tops its cap at", band_middle() + cap_of(em) / 2.0, wb.zmax),
                    ("runs the word", depth + _ring.WORD_TIE + relief, wb.ylen),
                    ("faces the word out at", _ring.THICK + relief, wb.ymax)):
                if abs(want - got) > 1e-3:
                    raise ValueError(
                        f"the {kind} coupon's chip {n} {what} {got:.4f} and its {value:g} "
                        f"{COUPONS[kind].unit} puts it at {want:.4f} — the chip is not the "
                        f"figure the coupon is read as sweeping.")


def selftest() -> int:
    """Each coupon chip against the port ring it is one of, the band it letters in, and the
    plate."""
    fails = []
    room = _ring.od(_ring.family(STATION)) - 2.0 * _ring.WORD_MARGIN
    for kind, coupon in COUPONS.items():
        for value in coupon.values:
            em, depth, relief, fit = spec(kind, value)
            if word_width(em) > room + 1e-9:
                fails.append(
                    f"the {kind} coupon's {value:g} chip letters '{WORD}' {word_width(em):.3f} "
                    f"mm across a chip that leaves {room:.3f} between its own margins")
            if cap_of(em) >= band() - 1e-9:
                fails.append(
                    f"the {kind} coupon's {value:g} chip stands a {cap_of(em):.3f} mm cap in a "
                    f"band {band():.3f} mm tall and leaves no rim at all")
            if depth + _ring.WORD_TIE >= _ring.THICK:
                fails.append(
                    f"the {kind} coupon's {value:g} chip cuts {depth + _ring.WORD_TIE:g} mm of "
                    f"recess into a {_ring.THICK:g} mm chip, and what stands behind the "
                    f"lettering is the pocket floor")
            if gap_of(em) - 2.0 * fit <= 0.0:
                fails.append(
                    f"the {kind} coupon's {value:g} chip opens the recess {fit:g} mm all round a "
                    f"{gap_of(em):.3f} mm bridge between two letters — the air meets in the "
                    f"middle and the two recesses come out as one hole")
            if kind == "cap" and gap_of(em) < LINE_W - 1e-9:
                fails.append(
                    f"the cap coupon's {value:g} em leaves a {gap_of(em):.3f} mm bridge between "
                    f"two of its letters and the bead is {LINE_W:g} — the chip does not reach "
                    f"between them")
            if kind in ("relief", "depth") and abs(value / LAYER_H
                                                   - round(value / LAYER_H)) > 1e-9:
                fails.append(
                    f"the {kind} coupon steps to {value:g} mm on a plate laying {LAYER_H:g} mm "
                    f"layers — the slicer lands that step on {value / LAYER_H:.2f} layers and "
                    f"rounds it, and the chip is not the figure it is read as")
    if MARK_DEPTH >= _ring.THICK - _ring.WORD_DEPTH - _ring.WORD_TIE:
        fails.append(
            f"a {MARK_DEPTH:g} mm mark in the back of a chip meets a recess cut "
            f"{_ring.WORD_DEPTH + _ring.WORD_TIE:g} into a {_ring.THICK:g} mm face, and the two "
            f"break through to each other")
    for row in MARK_ROWS:
        if abs(row) + MARK_D / 2.0 > _ring.od(_ring.family(STATION)) / 2.0:
            fails.append(
                f"a row of marks at z {row:g} stands off the bottom of a chip whose half circle "
                f"reaches {_ring.od(_ring.family(STATION)) / 2.0:.3f}")
        if abs(row) - MARK_D / 2.0 < _ring.bore_d(_ring.family(STATION)) / 2.0:
            fails.append(
                f"a row of marks at z {row:g} stands in the chip's own "
                f"Ø{_ring.bore_d(_ring.family(STATION)):g} bore")
    if not min(FITS) < gap_ceiling() < max(FITS):
        fails.append(
            f"the fit coupon sweeps {min(FITS):g} to {max(FITS):g} mm and the bridge between two "
            f"letters falls to one bead at {gap_ceiling():.3f} — the row stands wholly on one "
            f"side of the figure it is printed to find")
    if len({_index(k) for k in COUPONS}) != len(COUPONS):
        fails.append("two coupons are counted in the same number of marks")
    for _what, fn in (("specimen_holds", specimen_holds),
                      ("recess_holds", recess_holds),
                      ("chips_hold", chips_hold)):
        try:
            fn()
        except Exception as exc:                                     # noqa: BLE001
            fails.append(str(exc))
    for line in fails:
        print(f"FAIL {line}")
    if not fails:
        print("ok  port-ring-coupons  " + ", ".join(
            f"{kind} {len(c.values)} chips" for kind, c in COUPONS.items())
            + f" — '{WORD}' on a {LINE_W:g} mm bead, {band():.3f} mm band")
    return 1 if fails else 0


def main():
    volumes, sizes = {}, {}
    for kind, coupon in COUPONS.items():
        chips, words = build_coupon(kind)
        bb = chips.BoundingBox()
        volumes[kind] = (chips.Volume() / 1000.0, words.Volume() / 1000.0)
        sizes[kind] = f"{bb.xlen:.1f} × {bb.zlen:.1f}"
        print(f"Port-ring coupon — {kind}: {coupon.figure}")
        print(f"  {len(coupon.values)} chips: "
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
        "CPN_STATION": STATION,
        "CPN_STROKE": f"{SPECIMEN_STROKE:.3f}",
        "CPN_BAND": f"{band():.3f}",
        "CPN_CHIPS": f"{sum(len(c.values) for c in COUPONS.values())}",
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
        "CPN_THICK": f"{_ring.THICK:g}",
        "CPN_OD": f"{_ring.od(_ring.family(STATION)):g}",
        "CPN_CO2_BEADS": f"{_ring.WORD_MIN_STROKE / LINE_W:.2f}",
        "CPN_GAP": f"{SPECIMEN_GAP:.3f}",
        "CPN_GAP_BEADS": f"{SPECIMEN_GAP / LINE_W:.2f}",
        "CPN_GAP_CEIL": f"{gap_ceiling():.3f}",
        "CPN_KERNEL": f"{KERNEL_SIDES:g}",
        "CPN_MARK_D": f"{MARK_D:g}",
        "CPN_MARK_DEPTH": f"{MARK_DEPTH:g}",
    }
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
    for kind, (chip_v, word_v) in volumes.items():
        variables[f"CPN_VOL_{kind.upper()}"] = f"{chip_v + word_v:.2f}"
        variables[f"CPN_SIZE_{kind.upper()}"] = sizes[kind]
    substitute_md(_here.parent / "README.md", variables=variables)
    print("-> README.md")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main()
