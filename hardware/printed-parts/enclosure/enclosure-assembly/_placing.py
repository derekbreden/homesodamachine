"""_placing — the pose kit the enclosure's bodies are packed with.

A placement is a `place(...)`: the turns the body takes, and one constraint per axis. Each
constraint names a face OF THIS BODY and the plane that face sits on — `west=off("pump-b",
"east", GAP)` puts this body's −X face that far clear of pump B's +X face, `front=flush("pump-b",
"front")` makes the two −Y faces coplanar, `foot=off("compressor-shroud", "crown", CLEAR)` stands
this body that far over the other's top. The face a plane is read from is the PLACED body's, through
the pack, so a body seated on another rides every move of it.

`centre_x/y/z` seats the box's midpoint instead of a face, and `org_x/y/z` seats the body's own
origin — the anchor a part whose STEP is drawn about its mount takes. `station=` names one of the
body's OWN declared stations and `port_x/y/z` lands it, so a fitting made up on another stands on
the mouth its module draws rather than on whichever face its envelope happens to end at. One and
only one of the four per axis.

The turns come first and the box is measured after them, so a constraint is always about the
body as it stands. `yaw`/`pitch`/`roll` turn about Z/Y/X and are applied roll, pitch, yaw — the
order [`fit.py`](/hardware/scripts/fit.py) composes a pose in. `turn=` gives an axis and an angle
directly, for a body clocked off the world axes.

`off` and `flush` carry the axis of the face they read, so a plane taken across the machine
cannot seat a body up it: `foot=off(x, "east")` raises rather than standing the body at an X
coordinate. `at` and `between` are bare planes and carry no axis.

Every failure names what is missing: an unplaced referent lists the pack, an unknown face lists
the six, an axis left free or given twice is raised before anything is turned.

The pack keeps the move each body made. `pack.port(name, station)` takes a station in that
body's own frame — the `(position, outward axis)` pair the body's module declares — and hands
back where it stands in world, on the seat the body took
([`_seating.py`](/hardware/scripts/_seating.py)). `pack.point` is the same for a bare
coordinate, one with no facing: a bore, a mount, a centroid.

Coordinates are the assembly's world frame (+X right/east, +Y back/aft, +Z up, origin
lower-front-left). Authorship: [`_contents.py`](_contents.py). Sibling: [`_routing.py`](_routing.py),
which does this for the lines between the bodies placed here.
"""

import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents
                            if p.name == "hardware") / "scripts"))

import _boxes
from _seating import Seat

# A body face by the name the pack calls it, and by its axis code: the axis it lies on, and
# which end of that axis it is.
FACES = {
    "west": ("x", -1), "east": ("x", 1),
    "front": ("y", -1), "aft": ("y", 1),
    "foot": ("z", -1), "crown": ("z", 1),
    "x-": ("x", -1), "x+": ("x", 1),
    "y-": ("y", -1), "y+": ("y", 1),
    "z-": ("z", -1), "z+": ("z", 1),
}
AXES = ("x", "y", "z")

# The seat keyword a constraint arrives under → the axis it fixes, and what of the body lands
# on the plane: a face at that end of the axis, the box's midpoint, the body's own origin, or
# the station `station=` names.
SEATS = {**{n: (a, ("face", s)) for n, (a, s) in FACES.items() if len(n) > 2},
         **{f"centre_{a}": (a, ("centre", 0)) for a in AXES},
         **{f"org_{a}": (a, ("origin", 0)) for a in AXES},
         **{f"port_{a}": (a, ("port", 0)) for a in AXES}}


def _face(f: str) -> tuple:
    if f not in FACES:
        raise KeyError(f"no face {f!r} (have: {', '.join(sorted(FACES))})")
    return FACES[f]


@dataclass
class Plane:
    """One world coordinate a seat lands on: a constant, plus a weight on each body face it
    reads. `between` and `+` combine two planes, so a band's own two faces make the plane
    midway between them.

    `axis` is None for a plane given as a number — it fits any seat. A plane that reads a face
    carries that face's axis, so it can only ever seat a body along that axis."""

    axis: str | None
    const: float
    terms: tuple = ()          # ((ref, face, weight), ...) — ref is a pack name or a box

    def value(self, pack=None) -> float:
        v = self.const
        for ref, face, weight in self.terms:
            b = ref if not isinstance(ref, str) else _resolve(pack, ref)
            axis, sign = _face(face)
            v += weight * getattr(b, axis + ("max" if sign > 0 else "min"))
        return v

    def __add__(self, d: float) -> "Plane":
        return Plane(self.axis, self.const + float(d), self.terms)

    def __sub__(self, d: float) -> "Plane":
        return self + (-float(d))


def _resolve(pack, name: str):
    if pack is None:
        raise TypeError(
            f"{name} is a name and there is no pack to read it from — seat on a box directly, "
            f"or place through a Pack")
    return pack.box(name)


def _plane(p) -> Plane:
    return p if isinstance(p, Plane) else at(p)


def at(v: float) -> Plane:
    """The world coordinate `v`, on whichever axis its seat is."""
    return Plane(None, float(v))


def off(ref, face: str, gap: float = 0.0) -> Plane:
    """The plane `gap` clear of a body's face, outboard of it. `ref` is a name in the pack, or
    a box already in hand — which is what a pose derived before the pack exists reads."""
    axis, sign = _face(face)
    return Plane(axis, sign * float(gap), ((ref, face, 1.0),))


def flush(ref, face: str) -> Plane:
    """The plane of a body's face itself."""
    return off(ref, face, 0.0)


def between(a, b) -> Plane:
    """Midway between two planes — the seat a body centred in a band takes."""
    pa, pb = _plane(a), _plane(b)
    if pa.axis and pb.axis and pa.axis != pb.axis:
        raise TypeError(f"a band cannot run from a {pa.axis} plane to a {pb.axis} one")
    return Plane(pa.axis or pb.axis, (pa.const + pb.const) / 2.0,
                 tuple((r, f, w / 2.0) for r, f, w in pa.terms + pb.terms))


def _fixed(who: str, seats: dict) -> dict:
    """One constraint per axis, checked before anything is turned."""
    out: dict = {}
    for key, plane in seats.items():
        if key not in SEATS:
            raise TypeError(f"{who}: no seat {key!r} (have: {', '.join(sorted(SEATS))})")
        axis, how = SEATS[key]
        if axis in out:
            raise TypeError(
                f"{who}: {axis} is seated twice, by {out[axis][0]} and by {key} — "
                f"one constraint holds one axis")
        plane = _plane(plane)
        if plane.axis is not None and plane.axis != axis:
            raise TypeError(
                f"{who}: {key} seats the body along {axis}, and the plane it is given "
                f"is a {plane.axis} one")
        out[axis] = (key, how, plane)
    free = [a for a in AXES if a not in out]
    if free:
        raise TypeError(
            f"{who}: {', '.join(free)} unseated — every axis takes one constraint "
            f"(have: {', '.join(seats) or 'none'})")
    return out


def _turns(who: str, yaw: float, pitch: float, roll: float, turn) -> Seat:
    """The seat a body's turns make, before it is moved onto its planes. One of
    `yaw`/`pitch`/`roll` composes with nothing, so the order two turns go on in can never be
    a convention this kit chose: a body clocked about more than one axis states its own
    sequence in `turn`."""
    named = [n for n, d in (("yaw", yaw), ("pitch", pitch), ("roll", roll)) if d]
    if len(named) > 1:
        raise TypeError(
            f"{who}: {' and '.join(named)} together — the order they compose in is the body's, "
            f"not this kit's. Give the sequence as turn=[(axis, deg), ...]")
    seat = Seat()
    for axis, deg in (((1, 0, 0), roll), ((0, 1, 0), pitch), ((0, 0, 1), yaw)):
        if deg:
            seat = seat.then(Seat.turn(axis, deg))
    for axis, deg in turn:
        seat = seat.then(Seat.turn(axis, deg))
    return seat


def _landed(who: str, fixed: dict, station, turns: Seat) -> tuple | None:
    """Where the station a `port_*` seat lands stands after the body's turns.

    `station=` and a `port_*` seat are one declaration in two halves: the station says what
    of the body lands, the seat says where. Neither stands alone."""
    asks = sorted(key for key, (kind, _sign), _plane in fixed.values() if kind == "port")
    if station is None:
        if asks:
            raise TypeError(
                f"{who}: {', '.join(asks)} lands the body's own station and none is given — "
                f"pass station=(position, outward axis), the pair the body's module declares")
        return None
    if not asks:
        raise TypeError(
            f"{who}: a station is given and nothing lands it — seat an axis with "
            f"port_x/port_y/port_z, or drop the station")
    if len(station) != 2 or len(station[0]) != 3:
        raise TypeError(
            f"{who}: a station is the (position, outward axis) pair a module declares, and "
            f"this one is {station!r}")
    return turns.port(station)[0]


def _deltas(bb, fixed: dict, pack, landed=None) -> tuple:
    """How far the turned body moves to put each seat on its plane."""
    out = []
    for axis in AXES:
        _key, (kind, sign), plane = fixed[axis]
        lo, hi = getattr(bb, axis + "min"), getattr(bb, axis + "max")
        here = {"face": hi if sign > 0 else lo,
                "centre": (lo + hi) / 2.0,
                "origin": 0.0,
                "port": landed[AXES.index(axis)] if landed else None}[kind]
        out.append(plane.value(pack) - here)
    return tuple(out)


def corner(solid, *, yaw: float = 0.0, pitch: float = 0.0, roll: float = 0.0, turn=(),
           station=None, port=None, who: str = "this body", **seats) -> tuple:
    """The low corner a turned body's seats put it on, with no pack in hand.

    The seat vocabulary and every check are `place`'s; the planes read boxes directly rather
    than names. A pose derived before the pack exists — one another pose stands on, which the
    pack would recur through — is stated here and stays a pure function of the boxes it reads."""
    if port is not None:
        seats = {**{f"port_{a}": at(v) for a, v in zip(AXES, port)}, **seats}
    fixed = _fixed(who, seats)
    turns = _turns(who, yaw, pitch, roll, turn)
    bb = turns.solid(solid).BoundingBox()
    d = _deltas(bb, fixed, None, _landed(who, fixed, station, turns))
    return (bb.xmin + d[0], bb.ymin + d[1], bb.zmin + d[2])


class Pack:
    """The bodies placed so far, the seat each took, and the faces a later placement reads
    off them.

    `moves` is the editor's open hand on this pack: name → the steps the 3D viewer's component
    editor has dragged that body through. A step is a turn about the body's own centre and a
    shift, and it lands ON the seat rather than on the finished solid — so the body's stations
    ride it, and a body seated on a moved one is seated on where it now stands. A name with no
    move is placed exactly as authored."""

    def __init__(self, moves=None):
        self.solids: dict = {}
        self.seats: dict = {}
        self.moves: dict = dict(moves or {})

    def _placed(self, name: str):
        if name not in self.solids:
            raise KeyError(
                f"{name} is not placed (have: {', '.join(sorted(self.solids)) or 'nothing'}) — "
                f"a body is seated on one already in the pack")
        return name

    def box(self, name: str):
        return _boxes.boxed(self.solids[self._placed(name)])

    def seat(self, name: str) -> Seat:
        """The move a placed body made — its turns and its translation, as one."""
        return self.seats[self._placed(name)]

    def port(self, name: str, station) -> tuple:
        """A placed body's own station, in world: `(position, outward axis)`.

        `station` is the pair the body's module declares, in the body's own frame. It reads
        through the seat the body took."""
        return self.seat(name).port(station)

    def point(self, name: str, p) -> tuple:
        """A bare coordinate in a placed body's own frame, in world — a bore, a mount, a
        centroid. A port is this and a facing."""
        return self.seat(name).point(p)

    def place(self, name: str, solid, *, yaw: float = 0.0, pitch: float = 0.0,
              roll: float = 0.0, turn=(), org=None, station=None, port=None, **seats):
        """Turn a body and seat it, one constraint per axis. Returns the placed solid.

        `org=(x, y, z)` seats all three on the body's own origin, which is the whole of a pose
        a part's own builder hands back. It holds all three axes, so a body seated on its
        origin in one and on a face in another names each of the three itself. `port=(x, y, z)`
        is the same three for the station `station=` names — the whole of a fitting's pose,
        given as the one mouth the chain around it stands on."""
        if name in self.solids:
            raise KeyError(f"{name} is already placed")
        if org is not None:
            seats = {**{f"org_{a}": at(v) for a, v in zip(AXES, org)}, **seats}
        if port is not None:
            seats = {**{f"port_{a}": at(v) for a, v in zip(AXES, port)}, **seats}

        fixed = _fixed(name, seats)
        turns = _turns(name, yaw, pitch, roll, turn)
        turned = turns.solid(solid)
        onto = Seat.shift(_deltas(turned.BoundingBox(), fixed, self,
                                  _landed(name, fixed, station, turns)))
        seat, body = turns.then(onto), onto.solid(turned)

        # The editor's move, if this body has one, composes onto the seat here — inside the
        # placement, so everything downstream reads the moved body: its own stations through
        # `port`, its faces through `box`, and any body later seated on this one.
        moved = _moved(body, self.moves.get(name))
        if moved is not None:
            seat, body = seat.then(moved), moved.solid(body)

        self.seats[name] = seat
        self.solids[name] = body
        return self.solids[name]


def _moved(solid, steps) -> Seat | None:
    """The one world move a body's dragged steps come to, or None for a body with none.

    Each step turns about the body's centre AS THAT STEP FINDS IT and then shifts, which is
    what the viewer's gizmo does — so the centre is re-read between steps and the chain
    composes in order. A step with neither a turn nor a shift contributes nothing."""
    if not steps:
        return None
    out = Seat()
    for step in ([steps] if isinstance(steps, dict) else steps):
        turn, shift = step.get("rotate"), step.get("translate")
        move = Seat()
        if turn and turn.get("deg"):
            bb = solid.BoundingBox()
            c = ((bb.xmin + bb.xmax) / 2.0, (bb.ymin + bb.ymax) / 2.0,
                 (bb.zmin + bb.zmax) / 2.0)
            move = (Seat.shift((-c[0], -c[1], -c[2]))
                    .then(Seat.turn(turn.get("axis") or (0.0, 0.0, 1.0), float(turn["deg"])))
                    .then(Seat.shift(c)))
        if shift and any(shift):
            move = move.then(Seat.shift(tuple(float(v) for v in shift)))
        out, solid = out.then(move), move.solid(solid)
    return out


# --- controls -------------------------------------------------------------

def _box(dx, dy, dz, at_=(0.0, 0.0, 0.0)):
    return (cq.Workplane("XY").box(dx, dy, dz, centered=(False, False, False))
            .val().translate(at_))


def _raises(what, fn):
    try:
        fn()
    except Exception as exc:
        return f"  {what}: raised {type(exc).__name__}: {str(exc).splitlines()[0][:78]}"
    raise AssertionError(f"{what} did not raise")


def selftest():
    """Known answers for every seat, every plane, and every refusal."""
    out = []

    # A face lands exactly on the plane it is given, on all three axes and both ends.
    p = Pack()
    p.place("a", _box(10, 20, 30), west=at(100.0), front=at(200.0), foot=at(300.0))
    b = p.box("a")
    assert (b.xmin, b.ymin, b.zmin) == (100.0, 200.0, 300.0), b
    p.place("b", _box(10, 20, 30), east=at(100.0), aft=at(200.0), crown=at(300.0))
    b = p.box("b")
    assert (b.xmax, b.ymax, b.zmax) == (100.0, 200.0, 300.0), b
    out.append("  face seats: six faces land on their own plane")

    # `off` leaves exactly the gap, measured between the two boxes; `flush` leaves none.
    p = Pack()
    p.place("host", _box(10, 10, 10), west=at(0.0), front=at(0.0), foot=at(0.0))
    p.place("guest", _box(4, 4, 4), west=off("host", "east", 1.5),
            aft=flush("host", "aft"), foot=off("host", "crown", 2.0))
    h, g = p.box("host"), p.box("guest")
    assert abs((g.xmin - h.xmax) - 1.5) < 1e-9, (g.xmin, h.xmax)
    assert abs(g.ymax - h.ymax) < 1e-9, (g.ymax, h.ymax)
    assert abs((g.zmin - h.zmax) - 2.0) < 1e-9, (g.zmin, h.zmax)
    out.append("  off/flush: the gap between the placed boxes is the gap asked for")

    # A gap off a −ve face runs outboard, away from the body it is read from.
    p = Pack()
    p.place("host", _box(10, 10, 10), west=at(0.0), front=at(0.0), foot=at(0.0))
    p.place("guest", _box(4, 4, 4), east=off("host", "west", 1.5),
            front=at(0.0), foot=at(0.0))
    assert abs(p.box("host").xmin - p.box("guest").xmax - 1.5) < 1e-9
    out.append("  off a low face: the gap runs outboard of the body it reads")

    # Centre and origin seats.
    p = Pack()
    p.place("a", _box(10, 20, 30), centre_x=at(0.0), centre_y=at(0.0), centre_z=at(0.0))
    b = p.box("a")
    assert (abs(b.xmin + b.xmax) < 1e-9 and abs(b.ymin + b.ymax) < 1e-9
            and abs(b.zmin + b.zmax) < 1e-9), b
    p.place("o", _box(4, 4, 4, (7.0, 0.0, 0.0)), org_x=at(10.0), org_y=at(20.0), org_z=at(30.0))
    b = p.box("o")
    assert (b.xmin, b.ymin, b.zmin) == (17.0, 20.0, 30.0), b
    out.append("  centre seats the midpoint; origin seats the body's own zero")

    # `org=` seats all three on the body's own origin, and a seat given beside it still holds.
    p = Pack()
    p.place("v", _box(4, 4, 4, (7.0, 0.0, 0.0)), org=(10.0, 20.0, 30.0))
    assert tuple(round(v, 9) for v in (p.box("v").xmin, p.box("v").ymin,
                                       p.box("v").zmin)) == (17.0, 20.0, 30.0)
    out.append("  org seats all three on the body's own zero")

    # A station seat lands the body's own mouth, wherever the envelope around it ends. The
    # bar's mouth is 1 mm inboard of its own +X face, so the two seats stand 1 mm apart.
    mouth = ((9.0, 1.0, 1.0), (1.0, 0.0, 0.0))
    p = Pack()
    p.place("m", _box(10, 2, 2), station=mouth, port=(50.0, 60.0, 70.0))
    assert p.port("m", mouth)[0] == (50.0, 60.0, 70.0), p.port("m", mouth)
    assert round(p.box("m").xmax, 9) == 51.0, p.box("m")
    p.place("e", _box(10, 2, 2), east=at(50.0), front=at(59.0), foot=at(69.0))
    assert round(p.box("e").xmax - p.box("m").xmax, 9) == -1.0
    out.append("  a station seat lands the mouth a module draws, not the face it ends at")

    # It lands through the turns, the same as any other seat: the mouth is measured on the
    # body as it stands, and the port reads back exactly where it was asked for.
    p = Pack()
    p.place("t", _box(10, 2, 2), yaw=90.0, station=mouth, port=(5.0, 6.0, 7.0))
    pos, axis = p.port("t", mouth)
    assert tuple(round(c, 9) for c in pos) == (5.0, 6.0, 7.0), pos
    assert tuple(round(c, 9) for c in axis) == (0.0, 1.0, 0.0), axis
    out.append("  a turned body's station lands where it is asked for, facing where it turned")

    # A chain: each fitting's mouth seated a gap off the one before it, read as a station and
    # not as a box. Move the head and the whole chain follows.
    for head in (0.0, 12.5):
        p = Pack()
        p.place("a", _box(10, 2, 2), station=mouth, port=(head, 0.0, 0.0))
        p.place("b", _box(10, 2, 2), station=mouth,
                port=(p.port("a", mouth)[0][0] + 4.0, 0.0, 0.0))
        assert round(p.port("b", mouth)[0][0] - p.port("a", mouth)[0][0], 9) == 4.0
    out.append("  a chain seated mouth to mouth holds its hop wherever its head stands")

    # An editor's move lands ON the seat: the body's own mouth rides it, and so does a body
    # seated on the moved one. A shift of 3 along X carries both by exactly 3.
    plain = Pack()
    plain.place("a", _box(10, 2, 2), station=mouth, port=(0.0, 0.0, 0.0))
    plain.place("b", _box(4, 4, 4), west=off("a", "east", 1.0), front=at(0.0), foot=at(0.0))
    p = Pack({"a": [{"translate": [3.0, 0.0, 0.0]}]})
    p.place("a", _box(10, 2, 2), station=mouth, port=(0.0, 0.0, 0.0))
    p.place("b", _box(4, 4, 4), west=off("a", "east", 1.0), front=at(0.0), foot=at(0.0))
    assert round(p.port("a", mouth)[0][0] - plain.port("a", mouth)[0][0], 9) == 3.0
    assert round(p.box("a").xmin - plain.box("a").xmin, 9) == 3.0
    assert round(p.box("b").xmin - plain.box("b").xmin, 9) == 3.0
    out.append("  a dragged body carries its own station, and the body seated on it")

    # A dragged turn is about the body's OWN centre, so the mouth swings with the metal and
    # keeps its place on it. The bar's mouth is 1 mm in from its +X end; a quarter turn about
    # Z faces it +Y, still 1 mm in from the end — now the +Y one.
    p = Pack({"a": [{"rotate": {"axis": [0, 0, 1], "deg": 90.0}}]})
    p.place("a", _box(10, 2, 2), station=mouth, port=(0.0, 0.0, 0.0))
    pos, axis = p.port("a", mouth)
    assert tuple(round(c, 9) for c in axis) == (0.0, 1.0, 0.0), axis
    assert abs(pos[1] - (p.box("a").ymax - 1.0)) < 1e-9, (pos, p.box("a").ymax)
    out.append("  a dragged turn takes the station round with the metal it is drawn on")

    # Steps compose in the order they were dragged, each turning about the centre it finds.
    # Seated, the bar spans x −9..1 with its mouth at the origin. The shift takes it to x −4..6,
    # centre x=1; the quarter turn about THAT centre swings the mouth to (1, 4, 0); the second
    # step's own shift then lifts it to y=6.
    p = Pack({"a": [{"translate": [5.0, 0.0, 0.0]},
                    {"rotate": {"axis": [0, 0, 1], "deg": 90.0}, "translate": [0.0, 2.0, 0.0]}]})
    p.place("a", _box(10, 2, 2), station=mouth, port=(0.0, 0.0, 0.0))
    pos, _axis = p.port("a", mouth)
    assert tuple(round(c, 9) for c in pos) == (1.0, 6.0, 0.0), pos
    out.append("  dragged steps compose in order, each about the centre it finds")

    # A body with no move is placed exactly as authored.
    p = Pack({"other": [{"translate": [9.0, 9.0, 9.0]}]})
    p.place("a", _box(10, 2, 2), station=mouth, port=(0.0, 0.0, 0.0))
    assert p.port("a", mouth)[0] == (0.0, 0.0, 0.0), p.port("a", mouth)
    out.append("  a name with no move of its own is placed as authored")

    # `port_x` alone seats one axis and leaves the other two to any other seat.
    p = Pack()
    p.place("s", _box(10, 2, 2), station=mouth, port_x=at(50.0), org_y=at(0.0), foot=at(0.0))
    assert round(p.port("s", mouth)[0][0], 9) == 50.0
    assert round(p.box("s").zmin, 9) == 0.0
    out.append("  port_x seats one axis; the other two take any seat")

    # `between` centres a body in a band, given as numbers or as another body's own two faces.
    p = Pack()
    p.place("a", _box(10, 4, 4), centre_x=between(0.0, 100.0), front=at(0.0), foot=at(0.0))
    assert (p.box("a").xmin, p.box("a").xmax) == (45.0, 55.0), p.box("a")
    p.place("band", _box(80, 4, 4), west=at(10.0), front=at(50.0), foot=at(0.0))
    p.place("c", _box(10, 4, 4), centre_x=between(flush("band", "west"), flush("band", "east")),
            front=at(0.0), foot=at(0.0))
    assert (p.box("c").xmin, p.box("c").xmax) == (45.0, 55.0), p.box("c")
    out.append("  between: a band's own two faces centre a body the same as its numbers")

    # A plane shifts by a signed distance, for an offset that is not a clearance.
    p = Pack()
    p.place("host", _box(10, 10, 10), west=at(0.0), front=at(0.0), foot=at(0.0))
    p.place("g", _box(2, 2, 2), west=flush("host", "west") + 3.0,
            front=flush("host", "front") - 1.0, foot=at(0.0))
    assert (p.box("g").xmin, p.box("g").ymin) == (3.0, -1.0), p.box("g")
    out.append("  a plane shifts by a signed distance, either way")

    # `corner` is `place`'s answer with no pack: the same seats off boxes already in hand.
    p = Pack()
    p.place("host", _box(10, 10, 10), west=at(5.0), front=at(0.0), foot=at(0.0))
    host_box = p.box("host")
    guest = _box(4, 4, 4)
    p.place("guest", guest, west=off("host", "east", 1.5), aft=flush("host", "aft"),
            foot=off("host", "crown", 2.0))
    pure = corner(_box(4, 4, 4), west=off(host_box, "east", 1.5),
                  aft=flush(host_box, "aft"), foot=off(host_box, "crown", 2.0))
    g = p.box("guest")
    assert tuple(round(v, 9) for v in pure) == tuple(
        round(v, 9) for v in (g.xmin, g.ymin, g.zmin)), (pure, g)
    out.append("  corner: the pure answer and the packed one are the same coordinate")

    # The turns are taken before the box is measured, so a seat is about the body as it stands.
    p = Pack()
    p.place("t", _box(10, 20, 30), yaw=90.0, west=at(0.0), front=at(0.0), foot=at(0.0))
    b = p.box("t")
    assert (round(b.xlen, 9), round(b.ylen, 9)) == (20.0, 10.0), (b.xlen, b.ylen)
    assert (round(b.xmin, 9), round(b.ymin, 9)) == (0.0, 0.0), b
    out.append("  a yawed body is seated by its turned box, not its drawn one")

    # A body's own station reaches world on the seat the body took. The bar is drawn 0..10
    # along X with its mouth at the +X end; turned about Y, that end is the low Z face.
    p = Pack()
    bar = _box(10, 2, 2)
    mouth = ((10.0, 0.0, 1.0), (1.0, 0.0, 0.0))
    p.place("bar", bar, turn=(((0, 1, 0), 90.0),), west=at(20.0), front=at(30.0), foot=at(40.0))
    pos, axis = p.port("bar", mouth)
    b = p.box("bar")
    assert abs(pos[2] - b.zmin) < 1e-9, (pos, b.zmin)
    assert tuple(round(c, 9) for c in axis) == (0.0, 0.0, -1.0), axis
    out.append("  a port reaches world on the seat its body took, about any axis")

    # The same body seated somewhere else takes its port along.
    q = Pack()
    q.place("bar", _box(10, 2, 2), turn=(((0, 1, 0), 90.0),),
            west=at(20.0), front=at(30.0), foot=at(55.0))
    assert abs(q.port("bar", mouth)[0][2] - (pos[2] + 15.0)) < 1e-9
    out.append("  re-seat the body and the port is already there")

    # A body seated on another rides it: move the host, the guest follows by construction.
    for host_x in (0.0, 37.5):
        p = Pack()
        p.place("host", _box(10, 10, 10), west=at(host_x), front=at(0.0), foot=at(0.0))
        p.place("guest", _box(4, 4, 4), west=off("host", "east", 1.5),
                front=at(0.0), foot=at(0.0))
        assert abs(p.box("guest").xmin - (host_x + 11.5)) < 1e-9
    out.append("  a seated body rides its host: the gap holds wherever the host stands")

    # Every refusal, each naming what is wrong.
    p = Pack()
    p.place("host", _box(10, 10, 10), west=at(0.0), front=at(0.0), foot=at(0.0))
    out.append(_raises("an axis given twice",
                       lambda: p.place("x", _box(1, 1, 1), west=at(0), east=at(5),
                                       front=at(0), foot=at(0))))
    out.append(_raises("an axis left free",
                       lambda: p.place("x", _box(1, 1, 1), west=at(0), front=at(0))))
    out.append(_raises("a plane taken across the machine seating a body up it",
                       lambda: p.place("x", _box(1, 1, 1), west=at(0), front=at(0),
                                       foot=off("host", "east", 1.0))))
    out.append(_raises("a referent that is not placed",
                       lambda: p.place("x", _box(1, 1, 1), west=off("ghost", "east"),
                                       front=at(0), foot=at(0))))
    out.append(_raises("a face that does not exist", lambda: off("host", "starboard")))
    out.append(_raises("two shorthand turns, whose order is the body's",
                       lambda: p.place("x", _box(1, 1, 1), yaw=90, roll=90,
                                       west=at(0), front=at(0), foot=at(0))))
    out.append(_raises("a band running across two axes",
                       lambda: between(flush("host", "west"), flush("host", "crown"))))
    out.append(_raises("a name where there is no pack to read it from",
                       lambda: corner(_box(1, 1, 1), west=off("host", "east"),
                                      front=at(0), foot=at(0))))
    out.append(_raises("org beside a seat on one of its own three axes",
                       lambda: p.place("x", _box(1, 1, 1), org=(0, 0, 0), foot=at(0))))
    out.append(_raises("a station landed and none given",
                       lambda: p.place("x", _box(1, 1, 1), port=(0, 0, 0))))
    out.append(_raises("a station given and nothing landing it",
                       lambda: p.place("x", _box(1, 1, 1), station=((0, 0, 0), (1, 0, 0)),
                                       west=at(0), front=at(0), foot=at(0))))
    out.append(_raises("a bare coordinate where a station's own pair belongs",
                       lambda: p.place("x", _box(1, 1, 1), station=(0, 0, 0),
                                       port=(0, 0, 0))))
    out.append(_raises("a seat that does not exist",
                       lambda: p.place("x", _box(1, 1, 1), abaft=at(0))))
    out.append(_raises("a body placed twice",
                       lambda: p.place("host", _box(1, 1, 1), west=at(0), front=at(0),
                                       foot=at(0))))
    return out


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(line)
        print("_placing selftest OK")
    else:
        print(__doc__)
