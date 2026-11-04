"""What a figure about a stored thing is allowed to decide.

A holder is printed before the thing it holds is ever measured, so every figure it
is cut from carries where that figure came from, and the geometry asks the figure
for the reading it needs rather than for a number.

Two readings, and they are not interchangeable:

- **exact** — a standard, or the maker's own drawing of the item. An M3 screw is
  M3, a T18 barrel is 6.5 mm, a 6P4C jack is 6P4C. Read it either way: the thing is
  no bigger than this *and* no smaller.
- **most** — a listing's package. The thing came out of that box, so it is no bigger
  than the box. It says nothing at all about how small it is.

The reading is per axis, because that is how the world publishes. Klein gives the
11063W's overall length to a thousandth of an inch and neither of its other two figures;
RIDGID gives the 150 an overall length and nothing else. One exact axis and two parcels
is the ordinary case, not the exception, and it is the reason a holder that has to be
told a cross-section is a holder that will not fit.

Geometry that must be at least as large as its content — a bin, a well, a slot mouth,
a footprint — reads either. Geometry that must be no larger than its content — a
shoulder the content spans, a pad its rim lands on, a bore its shank fills — reads
only *exact*, and `Env.least` refuses a *most* figure to its face.

`Env.least` is the whole rule. Everything else here is bookkeeping for it.
"""

from dataclasses import dataclass



import pathlib as _reference_pathlib
_reference_hardware = next(p for p in _reference_pathlib.Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('_bound')
globals().update({name: _reference_values[name] for name in ('EXACT', 'MOST', 'NEST_INTERLOCKS', 'NEST_COMPACT', 'NEST_TANGLES')})



class PackageAsFit(ValueError):
    """A parcel's size was asked to say how small the thing inside it is."""


@dataclass(frozen=True)
class Env:
    """One stored thing's envelope, and where its three figures came from.

    `x`, `y` and `z` are the thing lying in its own natural pose — the pose the
    holder's own docstring names. `source` is the standard, the maker's page or the
    ASIN whose parcel this is, written so a reader can go and check it.
    """

    name: str
    x: float
    y: float
    z: float
    bound: object
    source: str

    def __post_init__(self):
        result = _reference_data('_bound', type(self).__name__,
            (self.name, self.x, self.y, self.z, self.bound, self.source), {})
        object.__setattr__(self, 'bound', result.bound)

    def reading(self, axis):
        return _reference_data('_bound', 'method', (self, 'reading', (axis,)), {})

    # -- the two readings -------------------------------------------------

    def most(self, axis):
        return _reference_data('_bound', 'method', (self, 'most', (axis,)), {})

    def least(self, axis):
        try:
            return _reference_data('_bound', 'method', (self, 'least', (axis,)), {})
        except ValueError as error:
            raise PackageAsFit(str(error)) from error

    def size(self, axis):
        try:
            return _reference_data('_bound', 'method', (self, 'size', (axis,)), {})
        except ValueError as error:
            raise PackageAsFit(str(error)) from error

    # -- convenience ------------------------------------------------------

    @property
    def thinnest(self):
        return _reference_data('_bound', 'attribute', (self, 'thinnest'), {})

    @property
    def exact_everywhere(self):
        return _reference_data('_bound', 'attribute', (self, 'exact_everywhere'), {})

    @property
    def longest(self):
        return _reference_data('_bound', 'attribute', (self, 'longest'), {})

    @property
    def volume(self):
        return _reference_data('_bound', 'attribute', (self, 'volume'), {})

    def footprint(self):
        return _reference_data('_bound', 'method', (self, 'footprint', ()), {})

    def rotated(self):
        return _reference_data('_bound', 'method', (self, 'rotated', ()), {})

    def __str__(self):
        return _reference_data('_bound', 'display', (self,), {})


def exact(name, x, y, z, source):
    "A standard's figure, or the maker's own drawing of the item."
    return _reference_data('_bound', 'exact', (name, x, y, z, source), {})


def parcel(name, x, y, z, source):
    "A listing's package: the thing is somewhere inside this and nothing more."
    return _reference_data('_bound', 'parcel', (name, x, y, z, source), {})


def mixed(name, x, y, z, source, bounds):
    'One thing, one axis at a time: `bounds` is a triple of EXACT and MOST.\n\n    The maker publishes an overall length and stops; the rest is the box it shipped in.\n    '
    return _reference_data('_bound', 'mixed', (name, x, y, z, source, bounds), {})


def bore(name, diameter, length, source):
    'A round thing whose diameter is a standard: a drill, a tip barrel, a dowel.'
    return _reference_data('_bound', 'bore', (name, diameter, length, source), {})


@dataclass(frozen=True)
class Heap(Env):
    """A pack of loose pieces, with no shape of its own.

    A heap is read for its volume and never for a direction: tipped into a compartment
    it takes the compartment's floor and stands as deep as it must. `Env.x`, `y` and `z`
    are the cube of that volume, so a heap prints the same figures as anything else and
    a reader can see the size of it.
    """

from _reference_data import register_types
register_types(Env=Env, Heap=Heap)


#: How a heap of tipped-in pieces stands against the sum of the boxes the pieces sweep.
#: Below one the boxes interlock and the heap is smaller than their sum — a box drawn
#: round a tee or a spade terminal is mostly air, and the neighbours fall into it. At one
#: the piece is about as solid as its box, which is what a cap screw is. Above one the
#: pieces spring and tangle and hold each other apart.


def heap(name, count, piece_envelope, source, nest=NEST_COMPACT):
    "`count` pieces of `piece_envelope` each, tipped in loose.\n\n    `piece_envelope` is the cylinder or box one piece sweeps — a DIN 912 head over its\n    own length, a DIN 46228 collar over a ferrule, a John Guest drawing's three figures —\n    and never the piece's metal volume. The box already holds the air around the piece,\n    so `nest` says how the boxes stand against each other and not how much of one is\n    metal: counting the metal and then inflating it counts the same air twice, and it is\n    how a compartment of thirty tube tees comes out a litre deep.\n    "
    return _reference_data('_bound', 'heap', (name, count, piece_envelope, source, nest), {})
