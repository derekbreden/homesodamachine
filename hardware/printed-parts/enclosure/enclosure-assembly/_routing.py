"""_routing — the geometry kit the enclosure's lines are built with.

A run is a `route(...)`: a port anchor at each end, one-dimensional constraints between. Each
constraint supplies one coordinate and the other two carry over, so a waypoint moves along one
axis and every corner is square. Every `F.*` constraint reads off a port or a body face of the
component that owns it — `F.x(port, d)` is the plane `d` along world X from that port,
`F.out(port, d)` steps `d` along the port's own face normal, `F.face("x+", gap)` sits `gap` clear
of the component's +X body face. A frame's box comes off the placed solid and its ports off
`scorecard.PORTS`, so a run rides a move of its parts.

A line leaves and enters along its port's face normal; `route` emits the exit and approach stubs,
one bend radius by default. Each interior corner is a tangent arc of `bend` radius, backed off
`r·tan(θ/2)` down each leg, so `Run.length` is the length of stock the run cuts.

`route` raises on a leg shorter than the tangents its two ends demand, on a close leaving more
than one coordinate differing from the approach point, and on a close nearer the port than its
own approach stub. `tube` sweeps the port's bore Ø along the centreline.

Coordinates are the assembly's world frame (+X right, +Y back, +Z up, origin lower-front-left).
Authorship: [`_lines.py`](_lines.py). Precedent: [`routing.ts`](/hardware/pcb/pcba/routing.ts).
"""

import math
from dataclasses import dataclass, field

import cadquery as cq

# A port's declared face → the outward normal the line must leave along.
FACE_NORMAL = {
    "x-": (-1.0, 0.0, 0.0), "x+": (1.0, 0.0, 0.0),
    "y-": (0.0, -1.0, 0.0), "y+": (0.0, 1.0, 0.0),
    "z-": (0.0, 0.0, -1.0), "z+": (0.0, 0.0, 1.0),
}
AXES = ("x", "y", "z")


def normal_of(face) -> tuple:
    """The outward normal a line leaves a port along. A port's `face` is either
    one of the six body faces by name, or — where a fitting is clocked off the
    world axes, as the junction column's rolled elbows and the tees hung
    between them are — its axis given directly as a vector."""
    if isinstance(face, str):
        return FACE_NORMAL[face]
    m = math.sqrt(sum(c * c for c in face))
    return tuple(c / m for c in face)


def face_name(face) -> str:
    """A port's face for display: the body-face name, or the axis rounded."""
    return face if isinstance(face, str) else "(" + ", ".join(
        f"{c:+.3f}" for c in normal_of(face)) + ")"


def leg_skew(a, b, d) -> float:
    """How far the leg a→b runs off the direction `d`, in degrees."""
    v = [b[i] - a[i] for i in range(3)]
    m = math.sqrt(sum(c * c for c in v))
    if m < 1e-9:
        return 0.0
    dot = sum(v[i] * d[i] for i in range(3)) / m
    return math.degrees(math.acos(max(-1.0, min(1.0, dot))))

# Centreline bend radius as a multiple of the line's Ø. 2×OD is 12.7 mm on 1/4" soft ACR copper,
# a lever bender's smallest common former. Seeded, not ratified — like `CLEARANCE_FLOOR`; the
# number is the shoe radius of the bender this build uses. It sets how close to a fitting a line
# turns, and so how deep a corridor carries one.
BEND_RATIO = 2.0
# The exit/approach stub: the straight a line runs off its fitting before it turns. None = one
# bend radius. A longer reach drops a run onto a lane.
STUB = None
# How far off a collet's own axis a straight tube may enter it and still run unbent. A
# push-to-connect collet grips the tube all round and soft LLDPE takes up the rest. Seeded,
# not ratified, like `BEND_RATIO`.
COLLET_SKEW = 3.0


# A constraint supplies one coordinate; the other two carry over from the point before.
def _c(axis: str, value: float) -> dict:
    return {axis: float(value)}


@dataclass
class Frame:
    """A component's placed pose: its body box from the placed solid, its ports from the port
    table."""

    name: str
    ports: dict           # port name → (pos, face, diam)
    bb: object            # the placed solid's bounding box (for body-face constraints)

    def _port(self, p: str):
        if p not in self.ports:
            raise KeyError(f"{self.name}: no port {p} (have: {', '.join(sorted(self.ports))})")
        return self.ports[p]

    def at(self, p: str) -> tuple:
        """The port's world position."""
        return self._port(p)[0]

    def normal(self, p: str) -> tuple:
        """The outward unit normal of the face the port exits."""
        return normal_of(self._port(p)[1])

    def diam(self, p: str) -> float:
        return self._port(p)[2]

    # Plane `d` along a world axis from the port. The port rides its component's placement, so
    # these ride with it.
    def x(self, p: str, d: float = 0.0) -> dict:
        return _c("x", self.at(p)[0] + d)

    def y(self, p: str, d: float = 0.0) -> dict:
        return _c("y", self.at(p)[1] + d)

    def z(self, p: str, d: float = 0.0) -> dict:
        return _c("z", self.at(p)[2] + d)

    def out(self, p: str, d: float) -> dict:
        """Plane `d` along the port's own face normal."""
        n = self.normal(p)
        off = [i for i in range(3) if abs(n[i]) > 1e-9]
        if len(off) > 1:
            raise ValueError(
                f"{self.name}.{p} exits along {tuple(round(c, 4) for c in n)}, off the world "
                f"axes — `out` supplies one coordinate and cannot name that step. Give the "
                f"plane as x/y/z, or let the run close straight into the port.")
        i = off[0]
        return _c(AXES[i], self.at(p)[i] + d * n[i])

    def face(self, f: str, gap: float = 0.0) -> dict:
        """Plane `gap` clear of the component's body face, off the placed solid's box."""
        axis, sign = f[0], f[1]
        b = self.bb
        val = {("x", "-"): b.xmin, ("x", "+"): b.xmax,
               ("y", "-"): b.ymin, ("y", "+"): b.ymax,
               ("z", "-"): b.zmin, ("z", "+"): b.zmax}[(axis, sign)]
        return _c(axis, val + (gap if sign == "+" else -gap))


_frames: dict = {}


def frame(name: str, solid, ports: dict) -> Frame:
    """Register a component's frame. `route`'s "compressor-shroud.refrig-discharge" anchors
    resolve through the registry; an unknown component or port raises with the offending name."""
    f = Frame(name, ports, solid.BoundingBox())
    _frames[name] = f
    return f


def channel(a: float, b: float, bias: float = 0.0) -> float:
    """Position a run in the corridor between two faces `a` and `b`: centred at bias 0, hugging
    `a` at −1 or `b` at +1 to leave the other side open."""
    return (a + b) / 2.0 + bias * (abs(b - a) / 2.0 - 0.6)


def _anchor(a: str) -> tuple:
    comp, _, port = a.partition(".")
    if comp not in _frames:
        raise KeyError(f"no frame {comp} (have: {', '.join(sorted(_frames))})")
    return _frames[comp], port


@dataclass
class Run:
    """One authored line: its connection id, the centreline it follows, and the bore it carries."""

    id: str
    kind: str
    frm: str
    to: str
    pts: list                       # centreline waypoints, corners still square
    diam: float
    bend: float
    note: str = ""
    bends: list = field(default_factory=list)   # (index, turn°, leg-in, leg-out) per corner

    @property
    def length(self) -> float:
        """Developed centreline length, arcs included — the length of stock the run cuts."""
        total = 0.0
        for a, b in zip(self.pts, self.pts[1:]):
            total += math.dist(a, b)
        for _i, turn, _li, _lo in self.bends:      # square corner → arc: shorter by 2t − rθ
            t = self.bend * math.tan(math.radians(turn) / 2.0)
            total -= 2.0 * t - self.bend * math.radians(turn)
        return total


def route(cid: str, frm: str, *rest, kind: str = "refrigerant", stub=STUB,
          bend: float | None = None, skew: float | None = None, note: str = "") -> Run:
    """An orthogonal path from port to port through the given one-dimensional constraints.

    `route("refrig-1", "A.out", F.z("out", 40), ..., "B.in")` — the trailing argument is the
    destination anchor, everything between it and the source is a constraint. Each constraint
    supplies the one coordinate it is responsible for; the other two carry over from the point
    before. The exit stub off the source port and the approach stub into the destination are
    emitted here, along each port's own face normal. `stub` is one reach for both ends, or
    `(exit, approach)`.

    The closing turn comes from the destination: after the last constraint at most one
    coordinate may still differ from the approach point. Two raises, naming the coordinates.

    `skew` overrides `COLLET_SKEW` for this run — how far off a collet's own axis a straight
    tube may leave or enter it. The default suits rigid ACR copper; a flexible-tube run (soft
    LLDPE in a push-to-connect collet) takes more, so two nearly-facing fittings joined by one
    straight length of LLDPE author with a larger `skew` and no bend between them.
    """
    sk = COLLET_SKEW if skew is None else skew
    to = rest[-1]
    if not isinstance(to, str):
        raise TypeError(f"{cid}: the last argument must be the destination anchor, got {to!r}")
    constraints = list(rest[:-1])

    f_from, p_from = _anchor(frm)
    f_to, p_to = _anchor(to)
    d = f_from.diam(p_from)
    if d is None:
        raise ValueError(f"{cid}: {frm} has no bore Ø — a line cannot be routed through an unsized port")
    bend = bend if bend is not None else BEND_RATIO * d
    stub_out, stub_in = stub if isinstance(stub, (tuple, list)) else (stub, stub)
    stub_out = bend if stub_out is None else stub_out
    stub_in = bend if stub_in is None else stub_in

    start = f_from.at(p_from)
    n_from = f_from.normal(p_from)
    end = f_to.at(p_to)
    n_to = f_to.normal(p_to)

    pts = [tuple(start)]
    cur = tuple(start[i] + n_from[i] * stub_out for i in range(3))   # exit stub
    pts.append(cur)

    for c in constraints:
        (axis, value), = c.items()
        i = AXES.index(axis)
        if abs(cur[i] - value) < 1e-9:
            continue                                                # no-op constraint
        cur = tuple(value if j == i else cur[j] for j in range(3))
        pts.append(cur)

    approach = tuple(end[i] + n_to[i] * stub_in for i in range(3))   # approach stub
    differ = [AXES[i] for i in range(3) if abs(cur[i] - approach[i]) > 1e-9]
    # A leg that arrives already pointing into the collet, within `sk` of its axis, is
    # one straight piece of tube — it needs no corner and so no constraint to place one.
    straight_in = leg_skew(cur, approach, tuple(-c for c in n_to)) <= sk
    if len(differ) > 1 and not straight_in:
        raise ValueError(
            f"{cid}: the path needs another constraint — {', '.join(differ)} all still differ from "
            f"the approach to {to} (at {tuple(round(v, 2) for v in cur)}, approach "
            f"{tuple(round(v, 2) for v in approach)}), and the leg runs "
            f"{leg_skew(cur, approach, tuple(-c for c in n_to)):.1f}° off the port's axis, past the "
            f"{sk:.1f}° a collet takes straight. One inferred turn only; say which leg first.")
    # The close runs inward to the port: a path already nearer the fitting than its approach
    # stub would back out along the normal and come straight back.
    outward = sum((cur[i] - end[i]) * n_to[i] for i in range(3))
    if outward < stub_in - 1e-9:
        raise ValueError(
            f"{cid}: the close into {to} folds — the path is {outward:.2f} mm off the port face but "
            f"its approach stub is {stub_in:.2f} mm, so the last turn would back out and come "
            f"straight back. Shorten the approach stub to {outward:.2f} or move the lane out.")
    if math.dist(cur, approach) > 1e-9:
        pts.append(approach)
    pts.append(tuple(end))

    pts = _straighten(_dedupe(pts))
    lead = leg_skew(pts[0], pts[1], n_from)
    if lead > sk:
        raise ValueError(
            f"{cid}: the run leaves {frm} {lead:.1f}° off the collet's axis, past the "
            f"{sk:.1f}° one takes straight — the first leg runs out along the port.")
    return Run(cid, kind, frm, to, pts, d, bend, note, _bends(pts, bend, cid))


def _dedupe(pts: list) -> list:
    out = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, out[-1]) > 1e-9:
            out.append(p)
    return out


def _straighten(pts: list) -> list:
    """Drop a waypoint that continues the run in the same direction."""
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        din, dout = _unit(out[-1], pts[i]), _unit(pts[i], pts[i + 1])
        if sum(din[j] * dout[j] for j in range(3)) < 1.0 - 1e-9:
            out.append(pts[i])
    out.append(pts[-1])
    return out


def _unit(a, b):
    v = [b[i] - a[i] for i in range(3)]
    n = math.dist(a, b)
    return [c / n for c in v]


def _bends(pts: list, r: float, cid: str) -> list:
    """Every interior corner, with its turn angle and the two legs it seats its arc in. A bend
    takes `t = r·tan(θ/2)` off each leg; a leg shorter than the tangents its two ends demand
    raises."""
    out = []
    for i in range(1, len(pts) - 1):
        din, dout = _unit(pts[i - 1], pts[i]), _unit(pts[i], pts[i + 1])
        dot = max(-1.0, min(1.0, sum(din[j] * dout[j] for j in range(3))))
        turn = math.degrees(math.acos(dot))
        if turn < 1e-6:
            continue                                                # collinear — no corner
        out.append((i, turn, math.dist(pts[i - 1], pts[i]), math.dist(pts[i], pts[i + 1])))
    # A leg between two bends pays a tangent at each end.
    need = [0.0] * len(pts)
    for i, turn, _li, _lo in out:
        need[i] = r * math.tan(math.radians(turn) / 2.0)
    for i in range(len(pts) - 1):
        leg = math.dist(pts[i], pts[i + 1])
        if leg + 1e-9 < need[i] + need[i + 1]:
            raise ValueError(
                f"{cid}: leg {i}→{i + 1} is {leg:.2f} mm but its bends need "
                f"{need[i] + need[i + 1]:.2f} mm of tangent (R{r:.1f}) — the run needs a longer "
                f"leg, a tighter radius, or a part moved")
    return out


def centreline(run: Run) -> cq.Wire:
    """The run's centreline as a wire: straights joined by tangent arcs of `run.bend` radius."""
    pts, r = run.pts, run.bend
    need = [0.0] * len(pts)
    for i, turn, _li, _lo in run.bends:
        need[i] = r * math.tan(math.radians(turn) / 2.0)

    edges, cur = [], cq.Vector(*pts[0])
    for i in range(1, len(pts) - 1):
        if need[i] == 0.0:
            continue
        din, dout = _unit(pts[i - 1], pts[i]), _unit(pts[i], pts[i + 1])
        t = need[i]
        p1 = cq.Vector(*[pts[i][j] - din[j] * t for j in range(3)])
        p2 = cq.Vector(*[pts[i][j] + dout[j] * t for j in range(3)])
        turn = next(b[1] for b in run.bends if b[0] == i)
        # Arc centre on the inward bisector, r/sin(θ/2) from the corner; the midpoint is r from
        # that centre.
        bis = [dout[j] - din[j] for j in range(3)]
        bl = math.sqrt(sum(c * c for c in bis))
        bis = [c / bl for c in bis]
        dist = r / math.sin(math.radians(turn) / 2.0)
        ctr = [pts[i][j] + bis[j] * dist for j in range(3)]
        mv = [pts[i][j] - ctr[j] for j in range(3)]
        ml = math.sqrt(sum(c * c for c in mv))
        mid = cq.Vector(*[ctr[j] + mv[j] / ml * r for j in range(3)])
        if (p1 - cur).Length > 1e-9:
            edges.append(cq.Edge.makeLine(cur, p1))
        edges.append(cq.Edge.makeThreePointArc(p1, mid, p2))
        cur = p2
    tail = cq.Vector(*pts[-1])
    if (tail - cur).Length > 1e-9:
        edges.append(cq.Edge.makeLine(cur, tail))
    return cq.Wire.assembleEdges(edges)


def tube(run: Run) -> cq.Solid:
    """Sweep the run's bore Ø along its centreline."""
    path = centreline(run)
    d0 = _unit(run.pts[0], run.pts[1])
    prof = cq.Wire.makeCircle(run.diam / 2.0, cq.Vector(*run.pts[0]), cq.Vector(*d0))
    return cq.Solid.sweep(prof, [], path, makeSolid=True, isFrenet=True)
