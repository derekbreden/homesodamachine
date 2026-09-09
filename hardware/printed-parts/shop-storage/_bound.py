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


EXACT = "exact"
MOST = "most"


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
        bounds = self.bound if isinstance(self.bound, tuple) else (self.bound,) * 3
        if len(bounds) != 3 or any(b not in (EXACT, MOST) for b in bounds):
            raise ValueError(f"{self.name}: bound {self.bound!r} is not exact or most")
        object.__setattr__(self, "bound", bounds)
        for axis in ("x", "y", "z"):
            if getattr(self, axis) <= 0.0:
                raise ValueError(f"{self.name}: {axis} is {getattr(self, axis)}")

    def reading(self, axis):
        """How this axis was come by: exact, or a parcel."""
        return self.bound["xyz".index(axis)]

    # -- the two readings -------------------------------------------------

    def most(self, axis):
        """No more than this. Every figure reads this way."""
        return getattr(self, axis)

    def least(self, axis):
        """No less than this — and a parcel cannot say it.

        A shoulder the content has to span, a pad its rim has to land on, a jaw that
        grips it: all of them need to know the content is *at least* some size, and a
        box the thing was shipped in never knew that. The four ramps under a wire spool
        are the shape of this mistake — spaced for the parcel's 89 mm, and the spool
        passes between them.
        """
        if self.reading(axis) != EXACT:
            raise PackageAsFit(
                f"{self.name}: {self.source} is a parcel, so it says the thing is no "
                f"bigger than {getattr(self, axis):.1f} mm in {axis} and nothing about "
                f"how small it is. Geometry that needs a floor under {axis} wants an "
                f"exact figure — a standard, or the maker's own drawing — or a holder "
                f"that does not ask."
            )
        return getattr(self, axis)

    def size(self, axis):
        """The thing's own figure, cut to.

        A bore fails loose as surely as it fails tight: bored to a parcel it is the
        size of the box, and a 3.6 mm drill stands in a 90 mm hole. Anything cut *to* a
        content rather than merely around it reads this, and it takes exact figures
        only, for the same reason `least` does.
        """
        return self.least(axis)

    # -- convenience ------------------------------------------------------

    @property
    def thinnest(self):
        """The least of the three: an upper bound on how thick the thing is anywhere.

        A parcel gives this honestly. Whatever pose the thing was packed in, it is no
        thicker than the smallest side of the box it came out of, so a slot this wide
        takes it.
        """
        return min(self.x, self.y, self.z)

    @property
    def exact_everywhere(self):
        return all(b == EXACT for b in self.bound)

    @property
    def longest(self):
        return max(self.x, self.y, self.z)

    @property
    def volume(self):
        return self.x * self.y * self.z

    def footprint(self):
        return self.x, self.y

    def rotated(self):
        """The same thing turned a quarter turn about Z."""
        return Env(self.name, self.y, self.x, self.z, self.bound, self.source)

    def __str__(self):
        parts = [
            f"{value:.1f}" + ("" if reading == EXACT else "-")
            for value, reading in zip((self.x, self.y, self.z), self.bound)
        ]
        tail = "" if self.exact_everywhere else "  (- is a parcel: no more than that)"
        return " x ".join(parts) + " mm" + tail


def exact(name, x, y, z, source):
    """A standard's figure, or the maker's own drawing of the item."""
    return Env(name, x, y, z, EXACT, source)


def parcel(name, x, y, z, source):
    """A listing's package: the thing is somewhere inside this and nothing more."""
    return Env(name, x, y, z, MOST, source)


def mixed(name, x, y, z, source, bounds):
    """One thing, one axis at a time: `bounds` is a triple of EXACT and MOST.

    The maker publishes an overall length and stops; the rest is the box it shipped in.
    """
    return Env(name, x, y, z, tuple(bounds), source)


def bore(name, diameter, length, source):
    """A round thing whose diameter is a standard: a drill, a tip barrel, a dowel."""
    return Env(name, diameter, diameter, length, EXACT, source)


@dataclass(frozen=True)
class Heap(Env):
    """A pack of loose pieces, with no shape of its own.

    A heap is read for its volume and never for a direction: tipped into a compartment
    it takes the compartment's floor and stands as deep as it must. `Env.x`, `y` and `z`
    are the cube of that volume, so a heap prints the same figures as anything else and
    a reader can see the size of it.
    """


#: How a heap of tipped-in pieces stands against the sum of the boxes the pieces sweep.
#: Below one the boxes interlock and the heap is smaller than their sum — a box drawn
#: round a tee or a spade terminal is mostly air, and the neighbours fall into it. At one
#: the piece is about as solid as its box, which is what a cap screw is. Above one the
#: pieces spring and tangle and hold each other apart.
NEST_INTERLOCKS = 0.75
NEST_COMPACT = 1.0
NEST_TANGLES = 1.4


def heap(name, count, piece_envelope, source, nest=NEST_COMPACT):
    """`count` pieces of `piece_envelope` each, tipped in loose.

    `piece_envelope` is the cylinder or box one piece sweeps — a DIN 912 head over its
    own length, a DIN 46228 collar over a ferrule, a John Guest drawing's three figures —
    and never the piece's metal volume. The box already holds the air around the piece,
    so `nest` says how the boxes stand against each other and not how much of one is
    metal: counting the metal and then inflating it counts the same air twice, and it is
    how a compartment of thirty tube tees comes out a litre deep.
    """
    side = (count * piece_envelope * nest) ** (1.0 / 3.0)
    return Heap(name, side, side, side, EXACT, source)


# ============================================================
# SELFTEST
# ============================================================

def _refuses(call):
    try:
        call()
    except PackageAsFit:
        return True
    return False


def selftest():
    """The rule, against the case that made it necessary.

    The wire reel is the whole argument. Its listing publishes the wire's outside
    diameter, its length and its strand count, and no figure at all for the reel; the
    only three numbers anyone has are the box it shipped in. A shelf that spaced four
    ramps at that box's width read those numbers as if they said how *wide the reel is*,
    and the reel fell between them.
    """
    reel = parcel(
        "BNTECHGO 22 AWG, 250 ft",
        99.1, 99.1, 88.9,
        "B06Y2PNW41 package",
    )
    screw = exact("M3 x 8 cap screw", 5.5, 5.5, 11.0, "DIN 912")
    klein = mixed(
        "Klein 11063W", 167.5, 90.0, 25.0, "Klein's length, then B00CXKOEQ6",
        (EXACT, MOST, MOST),
    )

    assert reel.most("x") == 99.1, "a parcel gives an upper bound"
    assert screw.least("x") == 5.5, "a standard gives both bounds"
    assert screw.size("z") == 11.0, "and a size to cut to"
    print(f"   a parcel reads {reel.most('x'):.1f} mm as an upper bound")
    print(f"   a standard reads {screw.least('x'):.1f} mm as both bounds")

    assert _refuses(lambda: reel.least("x")), "a parcel must refuse a lower bound"
    assert _refuses(lambda: reel.size("x")), "and refuse being cut to"
    print("   a parcel refuses to say how small the thing inside it is")

    assert klein.least("x") == 167.5, "the maker's own axis reads both ways"
    assert _refuses(lambda: klein.least("z")), "the parcel's axes do not"
    print("   one exact axis and two parcels: each axis answers for itself")

    assert reel.thinnest == 88.9, "the least side bounds the thickness"
    assert reel.longest == 99.1
    print(f"   whatever pose it was packed in, it is no thicker than {reel.thinnest:.1f} mm")

    pile = heap("a hundred of them", 100, screw.volume, "DIN 912")
    assert abs(pile.volume - 100 * screw.volume * NEST_COMPACT) < 1e-6
    print(f"   a hundred of those heap to {pile.volume / 1000.0:.0f} cm3")

    ramps = 2.0 * (88.9 / 2.0 - 3.0)
    print(
        f"   the shelf that started this spaced its ramps {ramps:.1f} mm apart, from a "
        f"figure that never said the reel was that wide"
    )
    print("_bound selftest OK")


if __name__ == "__main__":
    selftest()
