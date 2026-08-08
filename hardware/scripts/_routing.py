"""_routing — the geometry kit the enclosure's lines are built with.

A run is a `route(...)`: a port anchor at each end, one-dimensional constraints between. Each
constraint supplies one coordinate and the other two carry over, so a waypoint moves along one
axis and every corner is square. Every `F.*` constraint reads off a port or a body face of the
component that owns it — `F.x(port, d)` is the plane `d` along world X from that port,
`F.out(port, d)` steps `d` along the port's own face normal, `F.face("x+", gap)` sits `gap` clear
of the component's +X body face. A frame's box comes off the placed solid and its ports off
`scorecard.PORTS`, so a run rides a move of its parts.

A line leaves and enters along its port's face normal; `route` emits the exit and approach stubs,
one bend radius by default. Each interior corner is a tangent arc backed off `r·tan(θ/2)` down
each leg, so `Run.length` is the length of stock the run cuts.

Every corner turns at its OWN radius (`seat_radii`, `Run.radii`) — the largest its two legs
seat. `bend=` is the ceiling, not the radius: one number caps every corner, a
`{corner index: number}` caps them one at a time, and a turn meant tighter than its legs allow
is said there. A leg between two corners is shared, so the two rise together and whichever runs
out first stops; the other keeps rising into what is left.

An unknown port, a destination that is not an anchor, a bore the port never declared, a `bend=`
cap on a waypoint that does not turn: these RAISE.

A close leaving two coordinates to one turn, a close nearer its port than its own approach stub,
a leg leaving or entering a collet past its skew, a corner with no tangent left to seat an arc
in: the run is DRAWN at what it has — the diagonal leg, the stub clamped to the room, the skew,
the square corner — and its shortfall recorded in `BLOCKED` with the measurement. `tube` sweeps
the port's bore Ø along that centreline like any other.

Coordinates are the assembly's world frame. Authorship:
[`manifold-layout/_lines.py`](/hardware/manifold-layout/_lines.py). Precedent:
[`routing.ts`](/hardware/pcb/pcba/routing.ts).
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

# Runs the pack does not carry as drawn, each with the measurement that falls short — run id →
# reason, read out under `_lines.BLOCKED`, the same dict. A blocked run is still swept and still
# graded: `_scorecard.routed` counts its connection unmade, `enclosure_assembly.main` prints the
# reason, `lines-clear` and `bend-radius` read the centreline as drawn.
#
# One run holds every shortfall it has — a lead running out along its port and a corner downstream
# seating nothing are two readings on one line.
BLOCKED: dict = {}


def _blocked(cid: str, why: str) -> None:
    """Record a run falling short of what it needs."""
    BLOCKED[cid] = f"{BLOCKED[cid]}; {why}" if cid in BLOCKED else why


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
    """Register a component's frame. `route`'s "compressor.refrig-discharge" anchors
    resolve through the registry; an unknown component or port raises with the offending name."""
    import _boxes                                       # placed solids are memoized; box each once

    f = Frame(name, ports, _boxes.boxed(solid))
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
    bend: float                     # the cap the author asked every corner to hold under
    note: str = ""
    bends: list = field(default_factory=list)   # (index, turn°, leg-in, leg-out) per corner
    radii: dict = field(default_factory=dict)   # corner index → the radius it turns at

    @property
    def length(self) -> float:
        """Developed centreline length, arcs included — the length of stock the run cuts."""
        total = 0.0
        for a, b in zip(self.pts, self.pts[1:]):
            total += math.dist(a, b)
        for i, turn, _li, _lo in self.bends:       # square corner → arc: shorter by 2t − rθ
            r = self.radii[i]
            t = r * math.tan(math.radians(turn) / 2.0)
            total -= 2.0 * t - r * math.radians(turn)
        return total

    @property
    def tightest(self) -> float:
        """The smallest radius the run turns at — what a reader means by "this run's radius"
        when the run turns at more than one."""
        return min(self.radii.values(), default=self.bend)


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
    # A stub the author left open reaches one bend radius. That is the AUTHORED cap where there
    # is one, and one `BEND_RATIO` where there is not — the stock's minimum is a ceiling a corner
    # may rise to, not a reach to stand a fitting off by, and letting it set the stub would walk
    # every unnamed run's standoff out with it.
    reach = BEND_RATIO * d if bend is None or isinstance(bend, dict) else float(bend)
    stub_out, stub_in = stub if isinstance(stub, (tuple, list)) else (stub, stub)
    stub_out = reach if stub_out is None else stub_out
    stub_in = reach if stub_in is None else stub_in
    # Unnamed, the cap is the stock's own minimum: every corner rises to what its legs seat and
    # stops where the tube stops caring.
    bend = bend if bend is not None else stock_min(kind, d)
    nominal = reach if isinstance(bend, dict) else float(bend)

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

    # The close runs inward to the port: a path already nearer the fitting than its approach
    # stub would back out along the normal and come straight back, so the stub is drawn at
    # whatever room the path leaves it.
    outward = sum((cur[i] - end[i]) * n_to[i] for i in range(3))
    if outward < stub_in - 1e-9:
        _blocked(cid,
                 f"the close into {to} folds — the path is {outward:.2f} mm off the port face but "
                 f"its approach stub is {stub_in:.2f} mm, so the last turn would back out and come "
                 f"straight back. Drawn with the stub at {max(outward, 0.0):.2f}; give the lane "
                 f"{stub_in - outward:.2f} mm more standoff, or shorten the stub to fit it.")
        stub_in = max(outward, 0.0)
    approach = tuple(end[i] + n_to[i] * stub_in for i in range(3))   # approach stub
    differ = [AXES[i] for i in range(3) if abs(cur[i] - approach[i]) > 1e-9]
    # A leg that arrives already pointing into the collet, within `sk` of its axis, is
    # one straight piece of tube — it needs no corner and so no constraint to place one.
    straight_in = leg_skew(cur, approach, tuple(-c for c in n_to)) <= sk
    if len(differ) > 1 and not straight_in:
        _blocked(cid,
                 f"the path needs another constraint — {', '.join(differ)} all still differ from "
                 f"the approach to {to} (at {tuple(round(v, 2) for v in cur)}, approach "
                 f"{tuple(round(v, 2) for v in approach)}), and the leg runs "
                 f"{leg_skew(cur, approach, tuple(-c for c in n_to)):.1f}° off the port's axis, "
                 f"past the {sk:.1f}° a collet takes straight. Drawn as one leg across all of "
                 f"them; say which turns first.")
    if math.dist(cur, approach) > 1e-9:
        pts.append(approach)
    pts.append(tuple(end))

    pts = _straighten(_dedupe(pts))
    lead = leg_skew(pts[0], pts[1], n_from)
    if lead > sk:
        _blocked(cid,
                 f"the run leaves {frm} {lead:.1f}° off the collet's axis, past the {sk:.1f}° one "
                 f"takes straight — the first leg runs out along the port. Drawn at the {lead:.1f}°; "
                 f"stand the lane off the port, or turn the collet onto the run.")
    corners = _bends(pts, cid)
    radii = seat_radii(pts, corners, _caps(corners, bend, cid, d), cid, d)
    return Run(cid, kind, frm, to, pts, d, nominal, note, corners, radii)


def bent(cid: str, frm: str, *rest, kind: str = "refrigerant", bend: float | None = None,
         skew: float | None = None, lead=None, note: str = "") -> Run:
    """Author a run as a HAND-PLACED centreline: the source port, explicit interior 3-D waypoints,
    the destination port — joined by straight legs and rounded at each interior corner with a tangent
    arc of `bend` radius, at whatever angle the corner turns (not just square). This is the free-form
    companion to `route`: where `route`'s axis-aligned constraints can only step one world coordinate
    at a time — so a diagonal move becomes a stack of square corners — `bent` follows the points given,
    so a run can lean and climb in one gentle move. Waypoints are `(x, y, z)` tuples in world.

    `bent("…", A, (x, y, z), (x, y, z), B)` — first arg after the source and last arg are the port
    anchors; everything between is a waypoint. The leg leaving `frm` and the leg entering `to` are
    checked against each port's own axis (`skew`, default `COLLET_SKEW`). `skew=(exit, approach)`
    holds the two ends to their own figures, for a run whose mouths are different features — a
    collet grips a tube and a countersunk bore lays its lip along one, and the two open by
    different angles (`manifold_layout.FLAVOR_SKEW`, `_lines.CAP_BORE_SKEW`).

    `lead` is `bent`'s exit/approach stub — the analogue of `route`'s `stub`. Given, it plants a
    waypoint one `lead` mm along the source normal off `frm`, and one along the destination normal off
    `to`, so the run leaves and enters exactly on-axis (leave/enter skew ~0 by construction) and the
    interior waypoints are free to dodge obstacles without fighting the collet check. `lead=d` reaches
    both ends by `d`; `lead=(out, in)` sets them apart, and 0 or None skips that end. Without it the
    first and last waypoints must themselves sit on the collet axes.
    """
    sk_out, sk_in = ((COLLET_SKEW, COLLET_SKEW) if skew is None
                     else skew if isinstance(skew, (tuple, list)) else (skew, skew))
    to = rest[-1]
    if not isinstance(to, str):
        raise TypeError(f"{cid}: the last argument must be the destination anchor, got {to!r}")
    f_from, p_from = _anchor(frm)
    f_to, p_to = _anchor(to)
    d = f_from.diam(p_from)
    if d is None:
        raise ValueError(f"{cid}: {frm} has no bore Ø — a line cannot be routed through an unsized port")
    bend = bend if bend is not None else stock_min(kind, d)
    nominal = BEND_RATIO * d if isinstance(bend, dict) else float(bend)

    n_from, n_to = f_from.normal(p_from), f_to.normal(p_to)
    src, dst = tuple(f_from.at(p_from)), tuple(f_to.at(p_to))
    mids = [tuple(w) for w in rest[:-1]]
    if lead is not None:
        lead_out, lead_in = lead if isinstance(lead, (tuple, list)) else (lead, lead)
        if lead_out:
            mids.insert(0, tuple(src[i] + n_from[i] * lead_out for i in range(3)))
        if lead_in:
            mids.append(tuple(dst[i] + n_to[i] * lead_in for i in range(3)))
    pts = _straighten(_dedupe([src] + mids + [dst]))
    if len(pts) < 2:
        raise ValueError(f"{cid}: a run needs at least a source and a destination")
    lead_off = leg_skew(pts[0], pts[1], n_from)
    if lead_off > sk_out:
        _blocked(cid, f"leaves {frm} {lead_off:.1f}° off the port's axis (> {sk_out:.1f}°), and is "
                      f"drawn at it — move the first waypoint onto the port's normal, or pass "
                      f"`lead=` to plant one.")
    tail_off = leg_skew(pts[-2], pts[-1], tuple(-c for c in n_to))
    if tail_off > sk_in:
        _blocked(cid, f"enters {to} {tail_off:.1f}° off the port's axis (> {sk_in:.1f}°), and is "
                      f"drawn at it — move the last waypoint onto the port's normal, or pass "
                      f"`lead=` to plant one.")
    corners = _bends(pts, cid)
    radii = seat_radii(pts, corners, _caps(corners, bend, cid, d), cid, d)
    return Run(cid, kind, frm, to, pts, d, nominal, note, corners, radii)


def meet(p, u, q, v, bias):
    """The corner where two facing collets' axes (`p` along `u`, `q` along `v`) come nearest, blended
    `bias` toward q's line so the tail enters q straight — one interior waypoint for `bent`, joining the
    two with a single bend there. For collets that nearly face down one line; where they do not, lead a
    stub off each end and let the interior carry the turn (`bent(..., lead=…)`)."""
    dot = lambda a, b: a[0] * b[0] + a[1] * b[1] + a[2] * b[2]      # noqa: E731
    w0 = tuple(p[i] - q[i] for i in range(3))
    a, b, c = dot(u, u), dot(u, v), dot(v, v)
    d, e = dot(u, w0), dot(v, w0)
    s = (b * e - c * d) / (a * c - b * b)
    t = (a * e - b * d) / (a * c - b * b)
    c1 = tuple(p[i] + s * u[i] for i in range(3))
    c2 = tuple(q[i] + t * v[i] for i in range(3))
    return tuple(c1[i] * (1.0 - bias) + c2[i] * bias for i in range(3))


def _dedupe(pts: list) -> list:
    out = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, out[-1]) > 1e-9:
            out.append(p)
    return out


_STRAIGHT_TOL = math.cos(math.radians(2.0))    # a turn below 2° is treated as straight


def _straighten(pts: list) -> list:
    """Drop a waypoint that continues the run in nearly the same direction (turn < 2°). Below that
    a rounded corner is pointless and its arc is degenerate — the centre sits `r/sin(θ/2)` away, so a
    sub-degree turn throws the arc (and the swept tube) wildly off — so such a kink is dropped and the
    run passes straight through."""
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        din, dout = _unit(out[-1], pts[i]), _unit(pts[i], pts[i + 1])
        if sum(din[j] * dout[j] for j in range(3)) < _STRAIGHT_TOL:
            out.append(pts[i])
    out.append(pts[-1])
    return out


def _unit(a, b):
    v = [b[i] - a[i] for i in range(3)]
    n = math.dist(a, b)
    return [c / n for c in v]


def _bends(pts: list, cid: str) -> list:
    """Every interior corner, with its turn angle and the two legs it seats its arc in."""
    out = []
    for i in range(1, len(pts) - 1):
        din, dout = _unit(pts[i - 1], pts[i]), _unit(pts[i], pts[i + 1])
        dot = max(-1.0, min(1.0, sum(din[j] * dout[j] for j in range(3))))
        turn = math.degrees(math.acos(dot))
        if turn < 1e-6:
            continue                                                # collinear — no corner
        out.append((i, turn, math.dist(pts[i - 1], pts[i]), math.dist(pts[i], pts[i + 1])))
    return out


# The tube on the machine, and the floor each one's corners answer to. A tube bent tighter
# than its stock takes kinks or thins its outer wall; the floor is a property of the STOCK — its
# material, its wall, its diameter — so it is stated per stock and every run drawn in it is
# measured against the same number. Conventionally quoted as a multiple of OD, which is how
# these read. `min_bend` is the tightest CENTRELINE radius; `source` is where the figure is from.
@dataclass
class Stock:
    name: str
    od: float            # the tube's outside Ø — the run's own `diam`
    min_bend: float      # tightest centreline radius, mm
    kinds: tuple         # the run kinds drawn in it
    source: str


STOCKS = (
    Stock("1/4\" LLDPE", 6.35, 14.0, ("fluid", "water", "co2"),
          "2.2×OD — bench test on the spool: \"flow with no kinks at 14.0 mm comfortably\""),
    Stock("1/4\" soft ACR copper", 6.35, 12.7, ("refrigerant",),
          "2×OD — a lever bender's smallest common former (BEND_RATIO)"),
    Stock("3/8\" braided PVC", 15.10, 15.9, ("water",),
          "neoPure PVCR-0610 datasheet minimum"),
)


def stock_of(kind: str, od: float) -> Stock:
    """The stock a run is drawn in, from its kind and bore Ø. Raises on a pair no stock claims —
    a new tube on the machine states its own bend floor before its runs can be graded."""
    for s in STOCKS:
        if kind in s.kinds and abs(s.od - od) < 0.05:
            return s
    have = "; ".join(f"{s.name} Ø{s.od:g} for " + "/".join(s.kinds) for s in STOCKS)
    raise KeyError(
        f"no stock declared for a {kind} run at Ø{od:g} — add it to STOCKS with the minimum "
        f"bend radius its datasheet gives (have: {have})")


def stock_min(kind: str, diam: float) -> float:
    """The roundest a corner in this stock is ever asked to be — its published minimum radius,
    and the ceiling a run carries when its author names none."""
    return stock_of(kind, diam).min_bend


def _caps(bends: list, bend, cid: str, diam: float) -> dict:
    """Each corner's ceiling, from what the author asked for. `bend` is a number capping every
    corner, or `{corner index: number}` capping them one at a time — a turn the author wants
    tighter than its legs would allow is said here and nowhere else. A corner the dict does not
    name is left UNCAPPED, held only by its own legs, so naming one turn says nothing about the
    rest. An index that names no corner raises, because a cap that lands on a straight is a cap
    on nothing."""
    idx = {i for i, _t, _a, _b in bends}
    if not isinstance(bend, dict):
        return {i: float(bend) for i in idx}
    stray = set(bend) - idx
    if stray:
        raise ValueError(
            f"{cid}: bend={{...}} caps corner{'s' if len(stray) > 1 else ''} "
            f"{', '.join(str(s) for s in sorted(stray))}, which {'are' if len(stray) > 1 else 'is'} "
            f"not a corner — this run turns at {sorted(idx) if idx else 'no waypoint at all'}.")
    return {i: float(bend.get(i, math.inf)) for i in idx}


def seat_radii(pts: list, bends: list, caps: dict, cid: str, diam: float) -> dict:
    """The radius each corner actually turns at: the largest its own two legs seat, up to its cap.

    A corner backs its arc `r·tan(θ/2)` down each leg, and a leg between two corners pays that
    at both ends — so the two share it, and the share is what this solves. Every corner rises
    together from zero and stops at whichever comes first, its own cap or a leg running out of
    tangent; a corner that stops early leaves the rest of its legs to the neighbour still rising.
    One radius for a whole run is that solve with every corner tied to the tightest one in it,
    which is why a run's gentlest turns used to read as its worst.

    A corner with no room at all is drawn SQUARE, and its run recorded in `BLOCKED`. Anything
    above that is drawn at what it seats and GRADED — `scorecard.bend_radii` is where a radius
    is called too tight for its stock, so a part that moves re-seats its corners instead of
    failing the build, and the reading of how tight they now are arrives in the scorecard rather
    than in a traceback.
    """
    floor = 1e-6
    tan = {i: math.tan(math.radians(t) / 2.0) for i, t, _a, _b in bends}
    legs = [(j, math.dist(pts[j], pts[j + 1])) for j in range(len(pts) - 1)]
    r = {i: 0.0 for i in tan}
    free = set(tan)
    while free:
        step = min(caps[i] - r[i] for i in free)
        for j, leg in legs:
            on = [k for k in (j, j + 1) if k in tan]
            rising = [k for k in on if k in free]
            if not rising:
                continue
            spent = sum(r[k] * tan[k] for k in on)
            step = min(step, max(0.0, leg - spent) / sum(tan[k] for k in rising))
        for i in free:
            r[i] += step
        done = {i for i in free if caps[i] - r[i] <= 1e-9}
        for j, leg in legs:
            on = [k for k in (j, j + 1) if k in tan]
            if on and leg - sum(r[k] * tan[k] for k in on) <= 1e-9:
                done |= {k for k in on if k in free}
        if not done:
            break
        free -= done
    # Under the floor there is no arc to draw — `centreline` skips a corner at exactly zero and
    # runs the two legs into each other, where a sub-micron radius would sweep a degenerate one.
    tight = [i for i, v in sorted(r.items()) if v < floor - 1e-9]
    for i in tight:
        r[i] = 0.0
    if tight:
        i = tight[0]
        turn = next(t for k, t, _a, _b in bends if k == i)
        legs_here = " and ".join(f"{math.dist(pts[k], pts[k + 1]):.2f} mm" for k in (i - 1, i))
        _blocked(cid,
                 f"corner {i} turns {turn:.0f}° between legs of {legs_here} and seats no radius at "
                 f"all — its legs are wholly spent on the corners either side of them. Drawn "
                 f"square. Lengthen a leg, or move what the legs run between.")
    return r


def leg_caps(run: Run) -> list:
    """Per leg, the largest bend radius this run's centreline as drawn could seat there.

    `_bends` raises when a leg is shorter than the tangents its two corners demand —
    `leg ≥ r·(tan(θa/2) + tan(θb/2))`. Solved for `r`, that same inequality is a ceiling the
    waypoints put on the radius, and the smallest ceiling along a run is the most radius the run
    holds without a point moving. A leg with a corner at neither end bounds nothing and is left
    out; a run with no corner at all returns nothing and is bounded by its stock alone.

    Each row is `(cap, i, leg, demand, where)`. `where` is "lead" for the first and last legs —
    the exit and approach reaches the author picks (`stub`, `lead`) — and "interior" for the
    rest, whose two ends are both waypoints something else put there. The split is by who can
    widen it: a lead is a number in [`_lines.py`](_lines.py), an interior leg is a part that has
    to move. `scorecard.bend_radii` grades a run against both.
    """
    tang = {i: math.tan(math.radians(turn) / 2.0) for i, turn, _li, _lo in run.bends}
    last = len(run.pts) - 2
    out = []
    for i in range(len(run.pts) - 1):
        demand = tang.get(i, 0.0) + tang.get(i + 1, 0.0)
        if demand <= 1e-12:
            continue
        leg = math.dist(run.pts[i], run.pts[i + 1])
        out.append((leg / demand, i, leg, demand, "lead" if i in (0, last) else "interior"))
    return out


def centreline(run: Run) -> cq.Wire:
    """The run's centreline as a wire: straights joined by a tangent arc at each corner, every
    one at the radius that corner seats (`run.radii`)."""
    pts = run.pts
    need = [0.0] * len(pts)
    for i, turn, _li, _lo in run.bends:
        need[i] = run.radii[i] * math.tan(math.radians(turn) / 2.0)

    edges, cur = [], cq.Vector(*pts[0])
    for i in range(1, len(pts) - 1):
        if need[i] == 0.0:
            continue
        r = run.radii[i]
        din, dout = _unit(pts[i - 1], pts[i]), _unit(pts[i], pts[i + 1])
        t = need[i]
        p1 = cq.Vector(*[pts[i][j] - din[j] * t for j in range(3)])
        p2 = cq.Vector(*[pts[i][j] + dout[j] * t for j in range(3)])
        turn = next(b[1] for b in run.bends if b[0] == i)
        # Arc centre on the inward bisector, r/cos(θ/2) from the corner (θ the turn/deflection); the
        # midpoint is r from that centre. (r/sin reads the same only at 90°, where the copper loop
        # lives — off the square it throws the centre out and balloons the arc.)
        bis = [dout[j] - din[j] for j in range(3)]
        bl = math.sqrt(sum(c * c for c in bis))
        bis = [c / bl for c in bis]
        dist = r / math.cos(math.radians(turn) / 2.0)
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
