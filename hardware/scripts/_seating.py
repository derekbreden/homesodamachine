"""_seating — the seat a body takes, and its ports with it.

A `Seat` is one `cq.Location`: the turns a part takes and where it lands. The body reads
through it, and so does every port the part declares.

`(position, outward axis)` is the pair a reference module hands back for a station, in the
part's own frame. Seating carries the pair. Nesting carries it again — a fitting seated in
an assembly and that assembly seated in the machine is `fitting.then(assembly)`, the
fitting's own frame to world in one hop.

    seat = _seating.Seat.turn((0, 0, 1), -90.0).then(_seating.Seat.shift((17.5, 427.0, 289.6)))
    body = seat.solid(part.build())
    mouth = seat.port(part.tube_port())

[`fit.py`](fit.py) poses a part that is not placed on this same transform, to ask whether it
would fit. Sibling: `seat_body` in
[`enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py), where the
machine's bodies take theirs.
"""

import cadquery as cq
from OCP.gp import gp_Pnt, gp_Vec


class Seat:
    """One rigid move — a rotation about the frame's origin, then a translation."""

    def __init__(self, loc: cq.Location | None = None):
        self.loc = cq.Location() if loc is None else loc

    @staticmethod
    def turn(axis, deg) -> "Seat":
        """A turn of `deg` about `axis` through the frame's origin."""
        return Seat(cq.Location(cq.Vector(0, 0, 0),
                                cq.Vector(*(float(c) for c in axis)), float(deg)))

    @staticmethod
    def shift(v) -> "Seat":
        """A translation, no turn."""
        return Seat(cq.Location(cq.Vector(*(float(c) for c in v))))

    def then(self, outer: "Seat") -> "Seat":
        """This seat, and then `outer`'s — the move a body makes when the frame it is
        seated in is itself seated. Composes as deep as the frames nest."""
        return Seat(outer.loc * self.loc)

    def solid(self, shape):
        """The body at this seat: the shape `.rotate()` and `.translate()` hand back, with
        the coordinates carried into the frame rather than left under a location. A body
        whose frame is already this one is the body as drawn."""
        if self.loc.wrapped.IsIdentity():
            return shape
        return shape._apply_transform(self.loc.wrapped.Transformation())

    def point(self, p) -> tuple:
        """A bare coordinate at this seat — a mount hole, a centroid, a station with no
        facing. A port is this plus a direction."""
        return _carry_point(self.loc, p)

    def port(self, station) -> tuple:
        """A `(position, outward axis)` pair at this seat. The position takes the turn and
        the translation; the axis is a direction and takes only the turn."""
        pos, axis = station
        return _carry_point(self.loc, pos), _carry_axis(self.loc, axis)

    def ports(self, stations: dict) -> dict:
        """A whole declaration at this seat: `{name: (position, axis)}`."""
        return {n: self.port(s) for n, s in stations.items()}

    def __repr__(self) -> str:
        t = self.loc.wrapped.Transformation()
        d = t.TranslationPart()
        return f"<Seat at ({d.X():.3f}, {d.Y():.3f}, {d.Z():.3f})>"


def _carry_point(loc: cq.Location, p) -> tuple:
    q = gp_Pnt(float(p[0]), float(p[1]), float(p[2]))
    q.Transform(loc.wrapped.Transformation())
    return (q.X(), q.Y(), q.Z())


def _carry_axis(loc: cq.Location, a) -> tuple:
    """A direction takes the rotation and not the translation — `gp_Vec` is the direction
    half of the same transform that moved the body."""
    v = gp_Vec(float(a[0]), float(a[1]), float(a[2]))
    v.Transform(loc.wrapped.Transformation())
    return (v.X(), v.Y(), v.Z())


# --- controls -------------------------------------------------------------

def selftest():
    """Known answers: what a seat does to a point, to a direction, and to the metal."""
    out = []

    def near(a, b, what):
        assert all(abs(x - y) < 1e-9 for x, y in zip(a, b)), f"{what}: {a} != {b}"

    # A shift carries a position and leaves a direction alone.
    pos, axis = Seat.shift((1.0, 2.0, 3.0)).port(((10.0, 0.0, 0.0), (1.0, 0.0, 0.0)))
    near(pos, (11.0, 2.0, 3.0), "shifted position")
    near(axis, (1.0, 0.0, 0.0), "shifted axis")
    out.append("  a shift carries the position and leaves the direction")

    # A bare point is a port's position without its facing.
    near(Seat.turn((0, 0, 1), 90.0).then(Seat.shift((1.0, 2.0, 3.0))).point((10.0, 0.0, 0.0)),
         (1.0, 12.0, 3.0), "carried point")
    out.append("  a bare coordinate rides the seat a port's position does")

    # A turn carries both, about the origin.
    pos, axis = Seat.turn((0, 0, 1), 90.0).port(((10.0, 0.0, 0.0), (1.0, 0.0, 0.0)))
    near(pos, (0.0, 10.0, 0.0), "turned position")
    near(axis, (0.0, 1.0, 0.0), "turned axis")
    out.append("  a turn carries the position and the direction alike")

    # About Y, the same as about X or Z.
    pos, axis = Seat.turn((0, 1, 0), 90.0).port(((1.0, 0.0, 0.0), (1.0, 0.0, 0.0)))
    near(pos, (0.0, 0.0, -1.0), "pitched position")
    near(axis, (0.0, 0.0, -1.0), "pitched axis")
    out.append("  a turn about Y carries what one about X or Z does")

    # Turn then shift, in that order.
    pos, _ = Seat.turn((0, 0, 1), 90.0).then(Seat.shift((1.0, 2.0, 3.0))).port(
        ((10.0, 0.0, 0.0), (1.0, 0.0, 0.0)))
    near(pos, (1.0, 12.0, 3.0), "turned then shifted")
    out.append("  turn, then shift — the order a body is seated in")

    # Nesting: a station in an assembly, the assembly in the machine, one hop.
    station = Seat.shift((5.0, 0.0, 0.0))
    frame = Seat.turn((0, 0, 1), 90.0).then(Seat.shift((0.0, 0.0, 7.0)))
    pos, axis = station.then(frame).port(((1.0, 0.0, 0.0), (1.0, 0.0, 0.0)))
    near(pos, (0.0, 6.0, 7.0), "nested position")
    near(axis, (0.0, 1.0, 0.0), "nested axis")
    out.append("  nesting composes: a station's own frame reaches world in one hop")

    # A bar drawn 0..10 along X with its mouth at the +X end, pitched onto −Z: the mouth
    # lands on the seated body's lowest face.
    bar = cq.Workplane("XY").box(10, 2, 2, centered=(False, True, True)).val()
    mouth = ((10.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    seat = Seat.turn((0, 1, 0), 90.0).then(Seat.shift((3.0, 4.0, 5.0)))
    bb = seat.solid(bar).BoundingBox()
    pos, axis = seat.port(mouth)
    assert abs(pos[2] - bb.zmin) < 1e-9, (pos, bb.zmin)
    near(axis, (0.0, 0.0, -1.0), "mouth axis")
    out.append("  the mouth lands on the seated body's own face")

    return out


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(line)
        print("_seating selftest OK")
    else:
        print(__doc__)
