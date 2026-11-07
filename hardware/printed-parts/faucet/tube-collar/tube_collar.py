"""Tube collar — the bulkhead ring's word and colour, carried on the tube.

`../../enclosure/bulkhead-ring/` marks the wall: a chip lying in a pocket of the back face, under a through-wall
fitting's flange, in the colour of the tube that goes into it. This is that chip bored for the tube
instead of for the fitting's barrel, run along it, and turned a quarter so the word reads down the
run. Same four colours, six stations and two-filament print.

    THE COLLAR OUTLINE has a half circle below the bore's axis and a rectangle above it,
    `RISE` tall over an OD twice that. It is not a shape that turns: the flat lies one way up and
    the word stands level on it without anything holding it there.

THE BORE IS CLOSED AND SLIPS OVER THE TUBE, and the collar threads on end-first, over a tail that
is still bare. `assembly/faucet-and-umbilical.md` §1 cuts the umbilical's four tubes and §3 sleeves
them; the collars go on at §4, up to the braid's own end. The tap run and the CO2 tether ship
made up in the install kit, and their collars go on at `assembly/finish-pack-ship.md` §6.

THE LENGTH IS THE BORE'S. `rock()` is the angle a collar can cock on its loosest tube — a bore of
length L with diametral play c binds at two diagonal corners, leaving atan(c/L) — and `flag_sway()`
carries that angle out to the word's face, the furthest anything on the collar stands from the line
it would turn about.

Coordinate frame — THE TUBE'S, the same one the bulkhead ring gives the fitting:
  Y = the tube's axis. +Y = outboard, toward the free end and the customer.
  Origin = the collar's INBOARD end face; it spans y = 0 to y = LENGTH.
  +Z = up, the way the flag stands. X completes the right-handed frame.

It prints flat-face down, many to a bed, two colours to a plate.

`tube_collar.rs` cuts the six collars from their numbers (`numbers.rs`). This module is for the
readers that still take them from Python: `build_collar` and `build_word` draw them in CadQuery.
"""

from __future__ import annotations

import collections
import json
import math
import sys
import types
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(next(p for p in _here.parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))
import cadquery as cq

from _cadq_export import export_assembly, import_step  # noqa: E402
from _materials import chip_color, step_safe, word_color  # noqa: E402

# THE BEVERAGE, TAP AND CO2 TUBE SIZE. Those lines are 1/4" OD LLDPE, off the
# four colour-coded spools in `ledger/bom.md` §3. It is the nominal and not a bench figure: the tube on
# the bench calipers Ø6.5, which is the top of the band below.
from _rust_data import request as _data_request


def _collar_data(fn="datums", **values):
    return _data_request("faucet-data", "faucet-data", {"op": "collar", "fn": fn, **values})


_collar_values = _collar_data()
globals().update(_collar_values["datums"])
# The bulkhead ring's lettering and stations, which the collar op reads from the ring's numbers.
_ring = types.SimpleNamespace(**_collar_values["ring"])
Collar = collections.namedtuple("Collar", "word fluid tube fitted")
STATIONS = {row["name"]: Collar(*(row[k] for k in ("word", "fluid", "tube", "fitted")))
            for row in _collar_values["stations"]}
FACES = tuple(FACES)


# What 1/4" OD LLDPE holds its diameter to on the spool. THE BORE IS SIZED OFF THE TOP OF THAT BAND
# and not off the nominal — a spool running high is the tube a collar still has to go onto, and one
# running low only leaves play. `clearance()` and `rock()` are the answers about the low end.

# WHAT THE PRINTER TAKES OFF THE BORE'S DIAMETER, calipered on a finished collar. It lies flat face
# down with the bore's axis along the bed, so the hole's crown is unsupported and sags into it.
# `BORE` is the figure the slicer is handed; `bore_printed()` is the one the tube meets.

# AND WHAT IS LEFT OVER THE BIGGEST TUBE once the sag has had it. `LENGTH` of bore turns any
# interference at all into a collar that goes on with a mallet or not at all, and this one goes on
# by hand over a bare tail. What holds it where it is put is the bend the tube came off the spool
# with: 1/4" LLDPE is never straight through `LENGTH` of bore and stands against the wall at both
# ends of one.
#   ITS SLIP IS THE TIGHTEST ON THE MACHINE and does not follow `port_hole_radius`. This figure
# and `BORE_SHRINK` are a PETG collar's, calipered off the 0.2 mm nozzle, where a hole holds its
# figure far better than the PET-GF bores do. The collar ships in PET-GF (`ledger/bom.md` §7),
# and no PET-GF collar has been calipered against either.

# THE BORE, AS THE SLICER IS HANDED IT: the top of the tube's band, the sag, and the slip.

# The collar's width, and the diameter of the half circle below the axis. It leaves a `wall()` of
# colour between the bore and each of the three flats.

# HOW FAR THE RECTANGLE STANDS ABOVE THE AXIS, and so how tall the two side flats are. It is
# the bulkhead ring's `RING_W`, the band a port's identification is lettered in.

# THE RUN ALONG THE TUBE. It is the longest station word plus its margins, set at
# the bulkhead ring's `WORD_SIZE`.

# How deep the word's recess is cut into the flat, and what the flat keeps clear of it. Both are
# the bulkhead ring's.


# ONE COLLAR PER CHIP. The six keys are the bulkhead ring's `STATIONS`, and each takes its word and its
# spool from the chip at that station — a word changed on the wall is changed on the tube by the
# same edit.
#
# WHICH TUBE EACH ONE RIDES, and the bench that threads it on.
Collar = collections.namedtuple("Collar", "word fluid tube fitted")

# ONE FILE PER STATION, AND IT HOLDS BOTH BODIES, as a rear tile's does. The part is one
# print in two filaments, a collar and the word lying in its recess, and the file is that pair.
STEPS = {name: _here.parent / f"tube-collar-{name}.step" for name in STATIONS}


def bore_printed():
    return _collar_data('bore_printed')


def wall():
    return _collar_data('wall')


def backing():
    return _collar_data('backing')


def reach():
    return _collar_data('reach')


def clearance():
    return _collar_data('clearance')


def rock():
    return _collar_data('rock')


def flag_sway():
    return _collar_data('flag_sway')


# THE THREE FLATS THE OUTLINE LEAVES, and every one of them carries the word. A collar on a tube
# takes whatever roll the bundle gives it, so a word on one face is a word that is behind the tube
# half the time — and what shows then is a coloured ring, which says nothing the tube's own colour
# has not already said. Lettered at 0° and ±90° the collar cannot present a blank face to a reader
# without presenting a lettered one to the same reader edge-on. The round below the axis takes no
# lettering; it is what the hand meets and it stays round.


def word_band(face="top"):
    return tuple(_collar_data("word_band", face=face))


def _face_word(which: str, face: str):
    """One station's word on one of its flats, standing in the recess it fills.

    THE LETTERS ARE LOOSE, one solid each, as `rear_identification.word` sets them. The part opens as
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


def bore_d(which):
    return _collar_data("bore_d", which=which)


def build_blank(which="water"):
    """The outline run along the tube and its bore, with no lettering taken out of it — what a
    station's own word is cut from, and what `letters_lie_in_it` weighs the cut against.

    Struck from primitives the way `rear_identification.chip` strikes a rear tile — a cylinder with
    everything above the axis taken off it, and a box standing on that same axis — so no plane's own
    chirality reaches the shape."""
    r = OD / 2.0
    barrel = cq.Solid.makeCylinder(r, LENGTH, cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 1.0, 0.0))
    below = cq.Solid.makeBox(OD, LENGTH, r, cq.Vector(-r, 0.0, -r))
    above = cq.Solid.makeBox(OD, LENGTH, RISE, cq.Vector(-r, 0.0, 0.0))
    return (barrel.intersect(below).fuse(above)
            .cut(cq.Solid.makeCylinder(bore_d(which) / 2.0, LENGTH,
                                       cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 1.0, 0.0))))


def build_collar(which: str):
    """One station's collar: the blank, with the word's recess taken out of each of its flats."""
    return build_blank(which).cut(build_word(which))


def _filament(rgb) -> "cq.Color":
    return step_safe(cq.Color(*(c / 255.0 for c in rgb)))


def build_part(which: str) -> cq.Assembly:
    """One station as it prints: the collar, and the word lying in its recess, each in the filament
    it comes off — shared-data's `color.chips`, the table the chip on the wall reads."""
    fluid = STATIONS[which].fluid
    a = cq.Assembly()
    a.add(build_collar(which), name=f"tube-collar-{which}",
          color=_filament(chip_color(fluid)))
    a.add(build_word(which), name=f"tube-collar-{which}-word",
          color=_filament(word_color(fluid)))
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
