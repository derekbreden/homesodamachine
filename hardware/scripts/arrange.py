"""Arrangements — the same bodies put together every way they legally can be, ranked.

`probe` asks about the world as it stands. `fit` asks about a body that is not in it yet.
Both hold everything else frozen, so both answer one pose at a time, and a question about
how a SET of parts goes together comes back as a column of clearances that never adds up to
a design. This is the third instrument: it varies the whole front column at once — every
tray's turn and every tray's clocking — and scores the arrangements against each other.

Two fittings may stand at a junction, and `Divider` and `Tee` are both here because the
COST of a junction is what this scores. A TRIDENT presents two parallel outlets at the pair
and its stem the other way. A TEE lays its run broadside across the pair's spread and its
branch the other way. Both take the same three port names, and where a pair has the room
ahead of it for either, which one stands there is a choice a ranking can make.

What it scores is the TUBE. A joint between two collets is not free and not equal: two
collets facing each other down one line take a straight length, two facing the same way take
a leg out and a leg back, and two square to each other take a corner. So an arrangement's
cost is the run it obliges — the tube, and the corners — and that is what "fits together"
means here. It is measurable without authoring a single waypoint, which is the whole point:
the reason a rotation has never been costed is that costing one meant re-authoring fifteen
routes first.

    import arrange

    sp = arrange.front_column()                 # the space: every choice and its values
    print(sp.report())                          # what it varies, what it holds, how many
    best = arrange.rank(sp, top=10)
    print(best[0].report())                     # one arrangement, joint by joint

A joint's cost is exact on a stated lattice: both collets get their lead of straight tube,
and the run between the lead ends turns only on the coordinates those ends and their own
leads define. `leg()` carries the lattice it solved on. Nothing here estimates — a geometry
it cannot route raises rather than scoring high.

The bodies are checked by BOUNDING BOX, against each other and against the cavity. That is
the fast pass and it is named as one: a box-clear arrangement is a CANDIDATE, not a fit.
`verify` carries one into `fit.py`'s exact world — printed walls, seam lips and all — and
that is the answer. A rank read without a verify is a claim about tube, not about whether
the machine closes.

From the shell:

    tools/cad-venv/bin/python hardware/scripts/arrange.py space
    tools/cad-venv/bin/python hardware/scripts/arrange.py rank --top 12
    tools/cad-venv/bin/python hardware/scripts/arrange.py show current
    tools/cad-venv/bin/python hardware/scripts/arrange.py rank --top 1 --full
    tools/cad-venv/bin/python hardware/scripts/arrange.py verify --rank 1
    tools/cad-venv/bin/python hardware/scripts/arrange.py selftest

`selftest` runs the leg solver against known-answer geometry — two collets facing down one
line, two facing the same way, two square to each other, a pair that has to turn back on
itself — then the tee against its own: a run that is one line, a branch that leaves square
to it, a swap that exchanges the run ends and nothing else, the turn `verify` poses the
solid with against the ports derived from the same two faces, and that turn refusing two
faces not square to each other. Then it checks that the arrangement the tree builds today is
IN the space and that every port this module derives lands where `_contents` places it. Run
it before trusting a ranking.

`front_column` SEARCHES no junction. All three of the head column's are poses to reach
rather than choices to score, and each for its own reason: the source pair stands in the
selects pair's own seats, so Y-A and Y-B each take a port from each tray down one column
(`_contents.junction_tee_pos`); and Y-E stands ACROSS the strip between the pump row's aft
faces and the head column's forward one (`_contents.y_e_pos`), which is a band one fitting's
own diameter deep — nothing there is free to face another way. What the space varies is every
tray's turn and clocking above the pack's own three seats, and the ranking prices reaching all
three junctions. The one trident in the machine is Y-H, in the loft.
"""

import argparse
import heapq
import itertools
import math
import os
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

_HW = next(p for p in Path(__file__).resolve().parents if p.name == "hardware")
_ENCLOSURE = _HW / "printed-parts" / "enclosure" / "enclosure-assembly"
sys.path.insert(0, str(_ENCLOSURE))
sys.path.insert(0, str(_HW / "printed-parts" / "enclosure" / "enclosure"))
sys.path.insert(0, str(_HW / "scripts"))

# The env a read-only run wants, set the way `probe._ensure_paths` sets it — but BEFORE the
# enclosure modules are imported rather than after. This scan writes no STEP and exports
# nothing, so it must not take the global build lock: holding it makes every later build
# follow this process instead of running, and a scan that can take an hour would hold it for
# one. `_contents` is imported below, and importing it is what would claim the lock.
os.environ.setdefault("HSM_SKIP_THUMBNAILS", "1")
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

import _contents as _c                                          # noqa: E402


# --- the run a joint obliges ----------------------------------------------

FACES = {"x+": (1.0, 0.0, 0.0), "x-": (-1.0, 0.0, 0.0),
         "y+": (0.0, 1.0, 0.0), "y-": (0.0, -1.0, 0.0),
         "z+": (0.0, 0.0, 1.0), "z-": (0.0, 0.0, -1.0)}

# The straight a collet needs before the tube may turn — the lead every leg in this machine
# is already drawn with. A corner nearer a collet face than this is a corner the tube cannot
# be bent to, so it is the lattice's own step as well as its offset.
LEAD = _c.DIVIDER_LEG_LEAD

# What a corner is worth against a millimetre of tube. A bend is not free — it is a fixture,
# a spring-back and a place the bore necks — and this is the exchange rate the ranking uses.
# It is a WEIGHT, not a measurement: change it and the ranking re-orders, which is why every
# arrangement reports its tube and its bends separately as well as its cost.
BEND_MM = 25.0


def _vec(a, b):
    return tuple(q - p for p, q in zip(a, b))


def _face(axis):
    """The face name of a unit axis, or a raise. Every collet in this machine is axis
    aligned; one that is not is one this instrument cannot cost."""
    for name, v in FACES.items():
        if all(abs(x - y) < 1e-6 for x, y in zip(axis, v)):
            return name
    raise ValueError(f"{axis} is not an axis-aligned face — arrange costs axis-aligned "
                     f"collets only, and this one is off-axis by more than 1e-6")


@dataclass(frozen=True)
class Leg:
    """One joint's run: the corners it turns, the tube it takes, and the lattice it was
    solved on. The lattice travels with the answer because an end of a search is a fact
    about the search."""
    bends: int
    length: float
    lattice: tuple

    @property
    def cost(self) -> float:
        return self.length + BEND_MM * self.bends

    def __str__(self):
        return f"{self.length:7.1f} mm  {self.bends} bend{' ' if self.bends == 1 else 's'}"


_LEG_CACHE: dict = {}


def leg(p1, f1, p2, f2, lead: float = LEAD) -> Leg:
    """The cheapest axis-aligned run from collet `p1` facing `f1` to collet `p2` facing `f2`.

    A tube leaves a collet along its own face and arrives at one against it, and neither may
    turn inside `lead` of the face. So the run is solved between the two LEAD ENDS, leaving
    the first heading out and reaching the second heading in.

    Exact on a stated lattice: the turning coordinates are the two lead ends' own, plus one
    `lead` either side of each on every axis, which is what a run that has to come about
    needs to turn on. A tube never turns back through itself, so a reversal is not a corner —
    it is not a move. Corners rank before tube, and `BEND_MM` is the rate.

    What this does NOT do is check the run against a body. It is the cost of the tube two
    collets oblige, not a route: a leg this prices at two corners may still have to be
    authored around something. That is what makes it cheap enough to run over a whole space,
    and it is why a ranking is a shortlist rather than a verdict.

    RAISES when no run exists on the lattice, which for two axis-aligned collets cannot
    happen, and so means the ends were not the collets they claimed."""
    a1, a2 = FACES[f1], FACES[f2]
    q1 = tuple(p + lead * d for p, d in zip(p1, a1))
    q2 = tuple(p + lead * d for p, d in zip(p2, a2))
    key = (tuple(round(v, 4) for v in _vec(q1, q2)), f1, f2, round(lead, 4))
    hit = _LEG_CACHE.get(key)
    if hit is not None:
        return hit

    coords, index = [], []
    for i in range(3):
        c = tuple(sorted({round(q1[i], 6), round(q2[i], 6),
                          round(q1[i] + lead, 6), round(q1[i] - lead, 6),
                          round(q2[i] + lead, 6), round(q2[i] - lead, 6)}))
        coords.append(c)
        index.append({v: n for n, v in enumerate(c)})
    start = tuple(index[i][round(q1[i], 6)] for i in range(3))
    goal = tuple(index[i][round(q2[i], 6)] for i in range(3))
    enter = _face(tuple(-x for x in a2))            # the heading the far collet is entered on

    seen = set()
    heap = [(0.0, 0, start, f1)]
    while heap:
        cost, bends, cell, head = heapq.heappop(heap)
        if (cell, head) in seen:
            continue
        seen.add((cell, head))
        if cell == goal and head == enter:
            out = Leg(bends, cost - BEND_MM * bends, tuple(coords))
            _LEG_CACHE[key] = out
            return out
        for name, d in FACES.items():
            if name[0] == head[0] and name[1] != head[1]:
                continue                # a tube does not turn back through itself
            axis = 0 if d[0] else (1 if d[1] else 2)
            nxt = list(cell)
            nxt[axis] += 1 if d[axis] > 0 else -1
            if not 0 <= nxt[axis] < len(coords[axis]):
                continue
            run = abs(coords[axis][nxt[axis]] - coords[axis][cell[axis]])
            turn = 0 if name == head else 1
            heapq.heappush(heap, (cost + run + BEND_MM * turn, bends + turn,
                                  tuple(nxt), name))
    raise ValueError(f"no axis-aligned run from {p1} {f1} to {p2} {f2} on the lattice "
                     f"{coords} — the ends are not the axis-aligned collets they claim")


# --- the bodies, and where a turn puts them -------------------------------

TRAY_HALF = (_c._tray.half_x, _c._tray.half_y)
TRAY_Z = (_c._tray.bot_z, _c._tray.top_z)
PORT_HALF = _c._tray.port_half
PORT_Z = _c._tray.port_collets()["xn-yn"][0][2]
SEAT_X = _c._tray.seats["xp"][0]
DIV_HALF = _c.DIVIDER_HALF
DIV_OFF = _c.DIVIDER_OUTLET_X
TEE_RUN_HALF = _c.TEE_RUN_HALF
TEE_BRANCH_REACH = _c.TEE_BRANCH_REACH
TEE_HALF_W = _c.TEE_HALF_W


@lru_cache(maxsize=1)
def _divider_half_widths() -> tuple:
    """The trident's own half-extents square to its axis, off the reference part's solid —
    across the outlet spread, and across the other way. Read from the body rather than
    written down, so a fitting swapped in `reference/y-divider` moves the box that filters
    the scan."""
    import fit
    bb = fit.part("y-divider").pose(at=(0.0, 0.0, 0.0)).bb
    return (bb.xlen / 2.0, bb.ylen / 2.0)


@lru_cache(maxsize=None)
def obstacles(held: tuple) -> tuple:
    """The placed world as BOXES — every body the column has to miss, with the column's own
    six held out by name, and with the routed tubes of the joints being re-arranged held out
    too. Those tubes are the arrangement's own output; leaving them in would measure a
    candidate against the routes of the one it replaces, which is the reason a scan like this
    has never been runnable against the real machine.

    Boxes, not solids: this is the fast pass. A body that is mostly air reads as full here,
    which can only ever REMOVE arrangements, never admit one — so a rank filtered this way
    is a shortlist, and `verify` is what settles it.

    Two whole categories are NOT in it, and cannot be, because their boxes are not proxies
    for their solids at all:

      * the printed PIECES — a piece's box is the whole machine, so a box pass holding one
        would report every arrangement clashing and rank nothing. `cavity()` is what stands
        in for them here, the interior they leave.
      * the ROUTED RUNS — a tube that crosses the machine and climbs has a box that is almost
        entirely air. Boxing `fluid-25` alone puts a 137 × 60 × 318 mm slab through the front
        column, and the arrangements it deletes are real ones.

    So the fast pass sees the COMPONENTS, and only those. What it cannot see, `verify`
    measures exactly — which is why a rank is a shortlist and a verify is the answer."""
    import probe
    w = probe.world()
    fair = [n for n in w.tagged("component", "panel", "display", "funnel") if n not in held]
    return tuple((n, {"x": (b.xmin, b.xmax), "y": (b.ymin, b.ymax), "z": (b.zmin, b.zmax)})
                 for n, b in ((n, w.bb(n)) for n in fair))


@lru_cache(maxsize=None)
def _world_clear(box_key: tuple, held: tuple) -> tuple:
    """Which placed bodies a body's box actually runs into.

    Two tiers, the same two `fit.slab` uses. The obstacles' BOXES narrow the field, and then
    every survivor is measured as the SOLID it is — because a box is a fair proxy for some
    bodies and not others, and the ones it is unfair to are exactly the crowded ones. The
    display's box reaches 0.74 mm into Y-A's and its solid does not come near it; a scan that
    stopped at the first tier would delete the arrangement this machine is built to.

    Memoized on the box, which is what makes the second tier affordable: two million
    arrangements put the same six bodies in a few hundred distinct places."""
    box = {k: (box_key[2 * i], box_key[2 * i + 1]) for i, k in enumerate("xyz")}
    near = {n for n, b in obstacles(held) if _overlap(box, b)}
    if not near:
        return ()
    import probe
    w = probe.world()
    vol = probe.box(box["x"], box["y"], box["z"])
    return tuple(h.name for h in w.hits(vol, skip=tuple(n for n in w.names if n not in near)))


@lru_cache(maxsize=1)
def cavity() -> dict:
    """The box the front column stands in, off the enclosure's own interior and the pack's
    own lane limits: the interior's front wall, the west lip rim the pump lane already reads,
    the cold core's front face at the back of the aft band, and in Z the band the head column
    itself occupies — the refrigeration stratum's roof it stands on up to the crown of its top
    seat. Everything standing on that roof is a body the search already sees, so the floor here
    is the plane and not a clearance off it."""
    import enclosure
    inner = enclosure._dims().inner
    return {"x": (_c.FRONT_COLUMN_WEST, inner[1] - _c.SIDE_RIB_INSET),
            "y": (inner[2], _c.source_tray_pos()[1] + PORT_HALF + _c.SOURCE_TRAY_AFT_BAND),
            "z": (_c.shroud_roof_z(), _c.source_tray_crown_z())}


def _yaw(v, deg):
    r = math.radians(deg)
    return (v[0] * math.cos(r) - v[1] * math.sin(r),
            v[0] * math.sin(r) + v[1] * math.cos(r), v[2])


# The reach is a function of the lean alone, and the lean is a constant of the pack. Held
# here so a scan over two million arrangements does not re-derive one number two million
# times — `divider_reach` still raises where it always did, on the first call.
REACH = _c.divider_reach()


@lru_cache(maxsize=None)
def _tray_collets(origin, yaw, valves, clock):
    out = {}
    swap, f1, f2 = clock
    order = (valves[1], valves[0]) if swap else valves
    for seat, (sx, letter) in enumerate(zip((-SEAT_X, SEAT_X), order)):
        flip = (f1, f2)[seat]
        for end, tag in ((-1.0, "I" if flip == 0 else "O"),
                         (1.0, "O" if flip == 0 else "I")):
            pos = _yaw((sx, end * PORT_HALF, PORT_Z), yaw)
            axis = _yaw((0.0, end, 0.0), yaw)
            out[f"V-{letter}-{tag}"] = (tuple(p + o for p, o in zip(pos, origin)),
                                        _face(axis))
    return out


@lru_cache(maxsize=None)
def _tray_box(origin, yaw):
    hx, hy = TRAY_HALF if yaw % 180 == 0 else TRAY_HALF[::-1]
    return {"x": (origin[0] - hx, origin[0] + hx),
            "y": (origin[1] - hy, origin[1] + hy),
            "z": (origin[2] + TRAY_Z[0], origin[2] + TRAY_Z[1])}


@lru_cache(maxsize=None)
def _divider_centre(faces, joins):
    a = FACES[faces]
    mid = tuple((p + q) / 2.0 for p, q in zip(*joins))
    return tuple(m - d * (REACH + DIV_HALF) for m, d in zip(mid, a))


@dataclass(frozen=True)
class Tray:
    """One valve tray: where it stands, the quarter turn it takes, and which of its four
    collets carries which port name.

    Every tray lies FLAT — plate down, valves up — so a yaw is its only turn, and the yaw is
    what decides whether its four collets face the machine's front and back or its two sides.
    The clocking is the seating: which seat carries which valve, and which end of each valve
    is its inlet. Both are free, both are recorded, and neither makes it a different part."""
    name: str
    origin: tuple
    yaw: int
    valves: tuple
    clock: tuple            # (seat swap, valve-1 inlet end, valve-2 inlet end), each 0 or 1

    def collets(self) -> dict:
        return _tray_collets(self.origin, self.yaw, self.valves, self.clock)

    def box(self) -> dict:
        return _tray_box(self.origin, self.yaw)


@dataclass(frozen=True)
class Divider:
    """One JG PP2308E trident: stem and two parallel outlets, all three coaxial.

    Its whole pose is WHERE THE OUTLETS LOOK, because the stem is the other end of the same
    axis and looks the opposite way — there is no third choice in a coaxial fitting. So a
    divider is placed by naming the face its outlets present at the pair it joins, and which
    of the two collets the first outlet takes. The body then stands one `divider_reach()` and
    one half-length back along that face, which is what leaves each leg the straight it
    leans through."""
    kind = "divider"
    name: str
    faces: str              # the face the two OUTLETS look along
    swap: int               # which of the pair the first-named outlet takes
    joins: tuple            # the two collet positions it hangs off, in the order named
    stem: str
    outs: tuple

    @property
    def axis(self) -> tuple:
        return FACES[self.faces]

    @property
    def spread(self) -> int:
        """The axis the pair it joins is spread on — the axis its outlet offsets lie along."""
        span = _vec(self.joins[0], self.joins[1])
        return max(range(3), key=lambda i: abs(span[i]))

    def centre(self) -> tuple:
        return _divider_centre(self.faces, self.joins)

    def ports(self) -> dict:
        c, a, n = self.centre(), self.axis, self.spread
        sign = 1.0 if _vec(self.joins[0], self.joins[1])[n] > 0 else -1.0
        off = [0.0, 0.0, 0.0]
        off[n] = DIV_OFF * sign
        first, second = (self.outs[::-1] if self.swap else self.outs)
        back = _face(tuple(-x for x in a))
        return {
            first: (tuple(p - o + d * DIV_HALF for p, o, d in zip(c, off, a)), self.faces),
            second: (tuple(p + o + d * DIV_HALF for p, o, d in zip(c, off, a)), self.faces),
            self.stem: (tuple(p - d * DIV_HALF for p, d in zip(c, a)), back),
        }

    def box(self) -> dict:
        c, a, n = self.centre(), self.axis, self.spread
        wide, narrow = _divider_half_widths()
        out = {}
        for i, k in enumerate("xyz"):
            half = DIV_HALF if a[i] else (wide if i == n else narrow)
            out[k] = (c[i] - half, c[i] + half)
        return out


@dataclass(frozen=True)
class Tee:
    """One tee-connector at a junction: a RUN of two collinear collets facing opposite ways,
    and a BRANCH square to it at the body's centre.

    It stands where a `Divider` stands and takes the same three port names: the two run ends
    take the `outs`, the branch takes the `stem`. `faces` is the face it presents at the pair,
    which for a tee is the run laid broadside across the pair's own spread; the branch leaves
    the opposite way.

    A trident's outlets look AT the collets they join. A tee's run ends look along the
    spread, square to them."""
    kind = "tee"
    name: str
    faces: str              # the face the RUN presents at the pair, as a trident's outlets do
    swap: int               # which of the pair the first-named run end takes
    joins: tuple
    stem: str               # the BRANCH takes it — the leg that leaves the junction
    outs: tuple             # the two RUN ends

    @property
    def axis(self) -> tuple:
        return FACES[self.faces]

    @property
    def spread(self) -> int:
        """The axis the pair it joins is spread on — the axis its own run lies along."""
        span = _vec(self.joins[0], self.joins[1])
        return max(range(3), key=lambda i: abs(span[i]))

    def centre(self) -> tuple:
        """Back from the pair's midpoint along the face it presents, by the body's own radius
        about the run and the `divider_reach()` its legs lean through."""
        mid = tuple((p + q) / 2.0 for p, q in zip(*self.joins))
        return tuple(m - d * (REACH + TEE_HALF_W) for m, d in zip(mid, self.axis))

    def ports(self) -> dict:
        c, a, n = self.centre(), self.axis, self.spread
        sign = 1.0 if _vec(self.joins[0], self.joins[1])[n] > 0 else -1.0
        run = [0.0, 0.0, 0.0]
        run[n] = sign
        first, second = (self.outs[::-1] if self.swap else self.outs)
        return {
            first: (tuple(p - d * TEE_RUN_HALF for p, d in zip(c, run)),
                    _face(tuple(-x for x in run))),
            second: (tuple(p + d * TEE_RUN_HALF for p, d in zip(c, run)),
                     _face(run)),
            self.stem: (tuple(p - d * TEE_BRANCH_REACH for p, d in zip(c, a)),
                        _face(tuple(-x for x in a))),
        }

    def box(self) -> dict:
        """Tight, and asymmetric on the branch axis: the run reaches `TEE_RUN_HALF` either
        way, the branch reaches only one way, and the body is `TEE_HALF_W` about the run
        everywhere else."""
        c, a, n = self.centre(), self.axis, self.spread
        out = {}
        for i, k in enumerate("xyz"):
            if i == n:
                lo = hi = TEE_RUN_HALF
            elif a[i]:
                lo, hi = ((TEE_BRANCH_REACH, TEE_HALF_W) if a[i] > 0
                          else (TEE_HALF_W, TEE_BRANCH_REACH))
            else:
                lo = hi = TEE_HALF_W
            out[k] = (c[i] - lo, c[i] + hi)
        return out


# --- the space ------------------------------------------------------------

@dataclass(frozen=True)
class Choice:
    """One axis of the space: a body, what about it is free, and every value it may take."""
    body: str
    what: str
    values: tuple


TRAY_YAWS = (0, 90)             # collets along the machine's depth, or across its width
CLOCKS = tuple(itertools.product((0, 1), repeat=3))
SWAPS = (0, 1)
KINDS = {"divider": Divider, "tee": Tee}     # what may stand at a junction


@dataclass
class Space:
    """The arrangements, and the joints they are scored on.

    A space states itself before it states an answer: every choice, every value, the joints
    each arrangement owes, and the bodies held fixed while the rest vary. A ranking read
    without its space is a ranking of a search."""
    choices: tuple
    joints: tuple
    fixed: dict
    label: str

    @property
    def size(self) -> int:
        """How many arrangements that is. A divider's faces are counted PER TRAY TURN — the
        four a fitting may present are a fact about the pair it joins, and turning the tray
        makes them a different four, not more of them."""
        n = 1
        for c in self.choices:
            n *= len(c.values) if c.values else len(_OUT_FACES[0])
        return n

    def report(self) -> str:
        cav = cavity()
        out = [f"{self.label} — {self.size:,} arrangements over {len(self.choices)} choices"]
        for c in self.choices:
            vals = list(c.values) if c.values else [
                f"{len(_OUT_FACES[0])} faces square to the pair's own spread"]
            out.append(f"  {c.body:<9} {c.what:<6} "
                       f"{len(c.values) if c.values else len(_OUT_FACES[0]):>2}  {vals}")
        out.append(f"  joints  {len(self.joints)}: "
                   f"{', '.join(j[0] for j in self.joints)}")
        out.append(f"  fixed   {', '.join(sorted(self.fixed))}")
        out.append(f"  cavity  x {cav['x'][0]:.1f}..{cav['x'][1]:.1f}   "
                   f"y {cav['y'][0]:.1f}..{cav['y'][1]:.1f}   "
                   f"z {cav['z'][0]:.1f}..{cav['z'][1]:.1f}")
        out.append(f"  weights bend {BEND_MM:.0f} mm of tube, lead {LEAD:.0f} mm")
        return "\n".join(out)


# Where a fitting may look at a pair spread across the machine, and at one spread along it.
# Both fittings are barred from the same two faces for the same reason: a trident's outlet
# offsets lie on the pair's own spread axis and a tee's run lies along it, so neither can
# present itself down the line it is already spread on. The four square to it are what is
# left.
_OUT_FACES = {0: ("y+", "y-", "z+", "z-"), 1: ("x+", "x-", "z+", "z-")}

_TRAY_SPEC = {"source": ("A", "B"), "selects": ("C", "D"), "bag-a": ("E", "F")}
# A junction free to face another way at the pair it joins would live here, keyed by the tray,
# the two collets it takes in the order it names them, its third port and its other two. The head
# column has none: Y-A and Y-B stand on the columns their four ports already make, and Y-E stands
# across the strip ahead of the bag pair, so `front_column` holds all three fixed and prices the
# reach — the way it holds the pump row's.
_JUNCTION_SPEC: dict = {}


def _tray_origin(name):
    return {"source": _c.source_tray_pos(), "selects": _c.selects_tray_pos(),
            "bag-a": _c.bag_a_tray_pos()}[name]


def front_column() -> Space:
    """The head column as a space: three trays, and the one junction still free to move.

    The source and selects pairs are joined by two tees standing on the columns their four
    ports already make (`_contents.junction_tee_pos`), so that junction has no face to present
    and no pair to swap — it is a fixed joint here, not a choice.

    The trays keep their SEATS — the column's three Z planes are the pack's, and the source
    pair's east seat hangs on the hopper's own fall column, which is the one line in this
    machine that cannot be routed around anything. What varies is every turn and every
    clocking above those seats, and at each junction which FITTING stands there and which
    face it presents.

    The PUMP ROW's two tees are held fixed, and so are BOTH of the column's own junctions and
    the three lines that arrive from outside it. The pump row's stand on the barbs of a pump whose
    seat the front column's corner already decided; Y-A and Y-B stand on the two columns the
    source and selects pairs already make; Y-E stands across the strip ahead of the bag pair,
    where a fitting has one way to stand. None is free while the trays turn — all of them are
    joints the column has to reach, and the ranking prices reaching them."""
    choices = []
    for name in _TRAY_SPEC:
        choices.append(Choice(name, "yaw", TRAY_YAWS))
        choices.append(Choice(name, "clock", CLOCKS))
    for name in _JUNCTION_SPEC:
        choices.append(Choice(name, "kind", tuple(KINDS)))
        choices.append(Choice(name, "faces", ()))       # filled per arrangement, see `build`
        choices.append(Choice(name, "swap", SWAPS))
    fixed = {
        "hopper-funnel.drain": (_c.funnel_drain(), "z-"),
        "flow-regulator.outlet": _c.flowreg_terminal("outlet"),
        "foam-assembly.reservoir-A": _c.foam_shell_port("reservoir-a"),
        "tee-y-c.Y-C-1": _c.y_c_port("Y-C-1"),
        "tee-y-c.Y-C-2": _c.y_c_port("Y-C-2"),
        "tee-y-d.Y-D-2": _c.y_d_port("Y-D-2"),
        "tee-y-a.Y-A-1": _c.y_a_port("Y-A-1"),
        "tee-y-a.Y-A-2": _c.y_a_port("Y-A-2"),
        "tee-y-b.Y-B-1": _c.y_b_port("Y-B-1"),
        "tee-y-b.Y-B-2": _c.y_b_port("Y-B-2"),
        "tee-y-e.Y-E-1": _c.y_e_port("Y-E-1"),
        "tee-y-e.Y-E-2": _c.y_e_port("Y-E-2"),
        "tee-y-e.Y-E-3": _c.y_e_port("Y-E-3"),
    }
    joints = (
        ("fluid-2", "flow-regulator.outlet", "V-A-I"),
        ("fluid-4", "hopper-funnel.drain", "V-B-I"),
        ("fluid-3", "V-A-O", "tee-y-a.Y-A-1"),
        ("fluid-5", "V-B-O", "tee-y-b.Y-B-1"),
        ("fluid-7", "tee-y-a.Y-A-2", "V-C-I"),
        ("fluid-8", "tee-y-b.Y-B-2", "V-D-I"),
        ("fluid-9", "V-C-O", "tee-y-c.Y-C-1"),
        ("fluid-10", "V-E-O", "tee-y-c.Y-C-2"),
        ("fluid-13", "tee-y-d.Y-D-2", "V-F-I"),
        ("fluid-14", "V-F-O", "tee-y-e.Y-E-1"),
        ("fluid-16", "tee-y-e.Y-E-3", "V-E-I"),
        ("fluid-15", "foam-assembly.reservoir-A", "tee-y-e.Y-E-2"),
    )
    return Space(tuple(choices), joints, fixed, "front column")


def junction_faces(tray_yaw: int) -> tuple:
    """The faces a fitting may present at a pair on a tray turned this way."""
    return _OUT_FACES[0 if tray_yaw % 180 == 0 else 1]


# --- one arrangement ------------------------------------------------------

@dataclass
class Arrangement:
    """One value for every choice, and what it costs.

    `legs` is the whole of it: joint by joint, the tube and the corners that arrangement
    obliges. The totals are sums of those; `clash` is the box-level pass, bodies against
    each other and against the cavity, which is a filter and not a fit."""
    space: Space
    values: dict
    trays: dict
    fittings: dict
    legs: dict
    clash: tuple

    @property
    def tube(self) -> float:
        return sum(l.length for l in self.legs.values())

    @property
    def bends(self) -> int:
        return sum(l.bends for l in self.legs.values())

    @property
    def cost(self) -> float:
        return sum(l.cost for l in self.legs.values())

    @property
    def face(self) -> float:
        """The forward-most face any body in the column presents — what the whole column
        costs the machine's depth, and the back wall of the front pocket."""
        return min(b.box()["y"][0] for b in
                   list(self.trays.values()) + list(self.fittings.values()))

    def vector(self) -> str:
        bits = []
        for name, t in self.trays.items():
            bits.append(f"{name}:{t.yaw}/{''.join(str(c) for c in t.clock)}")
        for name, d in self.fittings.items():
            bits.append(f"{name}:{d.kind[0]}{d.faces}{d.swap}")
        return " ".join(bits)

    def report(self) -> str:
        out = [("CLASH: " + "; ".join(self.clash)) if self.clash else "box-clear",
               f"  tube {self.tube:.0f} mm   bends {self.bends}   "
               f"cost {self.cost:.0f}   front face y {self.face:.1f}", ""]
        for name, a, b in self.space.joints:
            out.append(f"  {name:<9} {self.legs[name]}   {a} → {b}")
        out.append("")
        for t in self.trays.values():
            seats = "  ".join(f"{n} {v[1]}" for n, v in sorted(t.collets().items()))
            out.append(f"  {t.name:<8} yaw {t.yaw:<4} clock {t.clock}   {seats}")
        for d in self.fittings.values():
            c = d.centre()
            out.append(f"  {d.name:<8} {d.kind:<7} presents {d.faces:<3} swap {d.swap}   "
                       f"centre ({c[0]:.1f}, {c[1]:.1f}, {c[2]:.1f})")
        return "\n".join(out)


def _overlap(a, b, slack=1e-6):
    return all(a[k][0] < b[k][1] - slack and b[k][0] < a[k][1] - slack for k in "xyz")


def held_out(space: Space) -> tuple:
    """The bodies a candidate is NOT measured against: the column's own, and the routed tubes
    of every joint the space re-arranges. Both are the arrangement's own output. The junction's
    two tees stay IN, because the space holds them fixed — a candidate that stands in one is a
    candidate that cannot reach its own joints."""
    return tuple(sorted({"source-tray-assembly", "selects-tray-assembly", "bag-a-tray-assembly",
                         "tee-y-e"}
                        | {j[0] for j in space.joints}))


def build(space: Space, values: dict, world: bool = False) -> Arrangement:
    """One arrangement from one value per choice: the bodies placed, the joints costed.

    With `world`, each body's box is checked against the placed machine as well as against
    the column and the cavity — which is what keeps a scan from ranking arrangements that
    stand in the condenser."""
    trays = {}
    for name, valves in _TRAY_SPEC.items():
        trays[name] = Tray(name, _tray_origin(name), values[(name, "yaw")], valves,
                           values[(name, "clock")])
    ports = dict(space.fixed)
    for t in trays.values():
        ports.update(t.collets())

    fittings = {}
    for name, (_tray, joins, stem, outs) in _JUNCTION_SPEC.items():
        pair = tuple(ports[j][0] for j in joins)
        d = KINDS[values[(name, "kind")]](
            name, values[(name, "faces")], values[(name, "swap")], pair, stem, outs)
        fittings[name] = d
        ports.update(d.ports())

    legs = {n: leg(*ports[a], *ports[b]) for n, a, b in space.joints}

    bodies = [(t.name, t.box()) for t in trays.values()]
    bodies += [(d.name, d.box()) for d in fittings.values()]
    clash = []
    for (na, ba), (nb, bb) in itertools.combinations(bodies, 2):
        if _overlap(ba, bb):
            clash.append(f"{na}/{nb}")
    cav = cavity()
    for n, b in bodies:
        for k in "xyz":
            if b[k][0] < cav[k][0] - 1e-6 or b[k][1] > cav[k][1] + 1e-6:
                clash.append(f"{n} out of cavity on {k}")
    if world:
        held = held_out(space)
        for n, b in bodies:
            key = tuple(v for k in "xyz" for v in b[k])
            for hit in _world_clear(key, held):
                clash.append(f"{n}/{hit}")
    return Arrangement(space, values, trays, fittings, legs, tuple(clash))


def current() -> dict:
    """The arrangement the tree builds today, read off `_contents` rather than restated — so
    a value changed there moves this, and the selftest that scores it stays honest."""
    def clock_of(collets, valves):
        swap = 0 if collets[f"V-{valves[0]}-I"].startswith("xn") else 1
        order = valves[::-1] if swap else valves
        return (swap,) + tuple(0 if collets[f"V-{v}-I"].endswith("yn") else 1 for v in order)

    vals = {}
    for name, collets in (("source", _c.SOURCE_TRAY_COLLETS),
                          ("selects", _c.SELECTS_TRAY_COLLETS),
                          ("bag-a", _c.BAG_A_TRAY_COLLETS)):
        vals[(name, "yaw")] = int(_c.TRAY_YAW)
        vals[(name, "clock")] = clock_of(collets, _TRAY_SPEC[name])
    return vals


# --- the scan -------------------------------------------------------------

def rank(space: Space, top: int = 10, keep_clashing: bool = False,
         world: bool = True) -> list:
    """Every arrangement in the space, scored, best first.

    Cost is the tube and the corners the joints oblige. Box-clashing arrangements are
    dropped unless asked for — a body standing in another body is not a worse arrangement,
    it is not an arrangement.

    The divider faces are enumerated PER TRAY TURN, because which faces a fitting may present
    is a fact about the pair it joins: turn the tray and the fitting's four become a different
    four. So the space's size is the sum over the tray turns, which `Space.size` reports."""
    trays = [(n, "yaw", TRAY_YAWS) for n in _TRAY_SPEC]
    clocks = [(n, "clock", CLOCKS) for n in _TRAY_SPEC]
    out = []
    for yaws in itertools.product(*(v for _n, _w, v in trays)):
        yaw_of = {n: y for (n, _w, _v), y in zip(trays, yaws)}
        faces = [(d, "faces", junction_faces(yaw_of[_JUNCTION_SPEC[d][0]])) for d in _JUNCTION_SPEC]
        swaps = [(d, "swap", SWAPS) for d in _JUNCTION_SPEC]
        kinds = [(d, "kind", tuple(KINDS)) for d in _JUNCTION_SPEC]
        axes = clocks + kinds + faces + swaps
        for combo in itertools.product(*(v for _n, _w, v in axes)):
            values = {(n, w): v for (n, w, _vals), v in zip(axes, combo)}
            values.update({(n, "yaw"): y for n, y in yaw_of.items()})
            a = build(space, values, world=world)
            if a.clash and not keep_clashing:
                continue
            out.append(a)
    out.sort(key=lambda a: (round(a.cost, 3), round(a.face, 3)))
    return out[:top]


# The yaw and roll that carry the STEP's native pose — stem +Z, outlets −Z — onto each face
# its outlets can present. The solid and the ports take the same pair, so a body can never
# be turned one way and its collets another.
POSE_OF = {"y+": (-90.0, 90.0), "y-": (-90.0, -90.0), "z-": (-90.0, 0.0), "z+": (-90.0, 180.0),
           "x+": (0.0, 90.0), "x-": (0.0, -90.0)}


def _turn(v, yaw, pitch, roll):
    """A vector through `fit.Part.pose`'s own composition — roll (X), pitch (Y), yaw (Z)."""
    r, p, y = (math.radians(a) for a in (roll, pitch, yaw))
    v = (v[0], v[1] * math.cos(r) - v[2] * math.sin(r), v[1] * math.sin(r) + v[2] * math.cos(r))
    v = (v[0] * math.cos(p) + v[2] * math.sin(p), v[1], -v[0] * math.sin(p) + v[2] * math.cos(p))
    v = (v[0] * math.cos(y) - v[1] * math.sin(y), v[0] * math.sin(y) + v[1] * math.cos(y), v[2])
    return tuple(round(c, 9) + 0.0 for c in v)


@lru_cache(maxsize=None)
def _tee_turns(run_face: str, branch_face: str) -> tuple:
    """The yaw, pitch and roll that lay the tee-connector's native run (+Z) on `run_face` and
    its native branch (+Y) on `branch_face`.

    Searched over the quarter turns rather than written down, because a tee at a junction
    takes a different one for every pair of axes it can present, and a table of them written
    by hand is a table with a wrong row in it. RAISES if no quarter turn does it, which means
    the two faces were not square to each other."""
    for yaw, pitch, roll in itertools.product((0.0, 90.0, 180.0, 270.0), repeat=3):
        if (_face(_turn((0, 0, 1), yaw, pitch, roll)) == run_face
                and _face(_turn((0, 1, 0), yaw, pitch, roll)) == branch_face):
            return (yaw, pitch, roll)
    raise ValueError(f"no quarter turn lays a tee's run on {run_face} with its branch on "
                     f"{branch_face} — the two are not square to each other")


def verify(arrangement: Arrangement, clearance: float = 0.0) -> str:
    """A ranked arrangement in the exact world: every body of it measured as a solid against
    `probe.world()`, printed pieces included, with the column's own six bodies held out so
    each is measured against the machine rather than against the pose it is replacing.

    The rank is a claim about tube, on boxes. This is the claim about the machine, and they
    are not the same answer — a box-clear arrangement standing in a seam lip clashes here,
    and this is the one that counts. Every tray is carried through the same turn-then-
    translate the pack itself uses, so a body checked here is the body that would be built.

    It holds out exactly what the scan holds out (`held_out`), and for the same reason: the
    routed runs of the joints being re-arranged are the arrangement's own output. Measuring a
    turned tray against the tubes drawn to the unturned one reports a clash at every joint the
    turn was meant to change, which is a tautology and not a finding."""
    import fit
    import probe
    w = probe.world()
    held = tuple(n for n in held_out(arrangement.space) if n in w.names)
    out = [f"exact world: {len(w.parts)} bodies, {len(w.pieces)} printed pieces",
           f"held out: {', '.join(sorted(held))}", ""]
    for t in arrangement.trays.values():
        solid = _c._rot(_c._load(_c.TRAY_ASSEMBLY), (0, 0, 1), float(t.yaw)).translate(t.origin)
        out.append(f"  {t.name + '-tray':<10} yaw {t.yaw:<4} "
                   f"{fit.check(solid, skip=held, clearance=clearance, world=w)}")
    for d in arrangement.fittings.values():
        if isinstance(d, Tee):
            run = _face(tuple(1.0 if i == d.spread else 0.0 for i in range(3)))
            branch = _face(tuple(-x for x in d.axis))
            yaw, pitch, roll = _tee_turns(run, branch)
            pose = fit.part("tee-connector").pose(at=d.centre(), yaw=yaw, pitch=pitch, roll=roll)
            what = f"tee   run {run} branch {branch}"
        else:
            yaw, roll = POSE_OF[d.faces]
            pose = fit.part("y-divider").pose(at=d.centre(), yaw=yaw, roll=roll)
            what = f"trident outlets {d.faces}"
        out.append(f"  {d.name:<10} {what:<26} "
                   f"{fit.check(pose, skip=held, clearance=clearance, world=w)}")
    return "\n".join(out)


# --- selftest -------------------------------------------------------------

def selftest() -> int:
    """Known-answer controls on the leg solver, then the real column through the space."""
    fails = []

    def check(name, got, want, tol=1e-6):
        ok = abs(got - want) <= tol if isinstance(want, float) else got == want
        print(f"  {'ok  ' if ok else 'FAIL'} {name}: {got} (want {want})")
        if not ok:
            fails.append(name)

    print("leg — known answers")
    l = leg((0, 0, 0), "y-", (0, -50, 0), "y+")
    check("facing down one line: bends", l.bends, 0)
    check("facing down one line: tube", l.length, 50.0 - 2 * LEAD)
    l = leg((0, 0, 0), "y-", (20, -50, 0), "y+")
    check("facing, offset square: bends", l.bends, 2)
    check("facing, offset square: tube", l.length, (50.0 - 2 * LEAD) + 20.0)
    l = leg((0, 0, 0), "y-", (30, -30, 0), "x-")
    check("square to each other: bends", l.bends, 1)
    # The shape a divider makes with a pair it is turned the wrong way at: both collets
    # present the same face, so the tube leaves one, crosses, and comes back — a U.
    l = leg((0, 0, 0), "y+", (20, 0, 0), "y+")
    check("same face, offset square: bends", l.bends, 2)
    check("same face, offset square: tube", l.length, 2 * LEAD + 20.0)
    # A reversal is not a corner, it is impossible: two collets on one line facing the same
    # way cost the detour out and back, not a turn in place.
    l = leg((0, 0, 0), "y+", (0, -50, 0), "y+")
    check("same face, in line: bends", l.bends, 4)

    print("space — the tree's own arrangement is in it")
    sp = front_column()
    vals = current()
    for name in _TRAY_SPEC:
        for what, values in (("yaw", TRAY_YAWS), ("clock", CLOCKS)):
            if vals[(name, what)] not in values:
                fails.append(f"{name}.{what} not in space")
                print(f"  FAIL {name}.{what} = {vals[(name, what)]} is not a value")
    for name in _JUNCTION_SPEC:
        allowed = junction_faces(vals[(_JUNCTION_SPEC[name][0], "yaw")])
        if vals[(name, "faces")] not in allowed:
            fails.append(f"{name}.faces not in space")
            print(f"  FAIL {name}.faces = {vals[(name, 'faces')]} not in {allowed}")
        if vals[(name, "kind")] not in KINDS:
            fails.append(f"{name}.kind not in space")
            print(f"  FAIL {name}.kind = {vals[(name, 'kind')]} not in {tuple(KINDS)}")

    print("tee — the fitting a junction may take instead")
    t = Tee("probe-tee", "y-", 0, ((-30.0, 0.0, 0.0), (30.0, 0.0, 0.0)), "S", ("P", "Q"))
    tp = t.ports()
    # The run is one straight line through the body: two collets on the spread axis, one
    # `TEE_RUN_HALF` either side of centre, each looking out of the end it is.
    check("run ends face out", (tp["P"][1], tp["Q"][1]), ("x-", "x+"))
    check("run is one line", max(abs(tp["P"][0][i] - tp["Q"][0][i]) for i in (1, 2)), 0.0)
    check("run length", tp["Q"][0][0] - tp["P"][0][0], 2 * TEE_RUN_HALF)
    # The branch leaves the way a trident's stem does — opposite the face presented at the
    # pair — and the body stands off by the same reach a trident leans through.
    check("branch faces away", tp["S"][1], "y+")
    check("branch reach", tp["S"][0][1] - t.centre()[1], TEE_BRANCH_REACH)
    check("stands off the pair", t.centre()[1] - 0.0, REACH + TEE_HALF_W)
    # A swap exchanges which collet each run end serves and moves nothing else.
    sw = Tee("probe-tee", "y-", 1, ((-30.0, 0.0, 0.0), (30.0, 0.0, 0.0)), "S", ("P", "Q")).ports()
    check("swap exchanges the run ends", (sw["P"][0], sw["Q"][0]), (tp["Q"][0], tp["P"][0]))
    check("swap moves the branch nowhere", sw["S"], tp["S"])
    # The turn `verify` poses the solid with, against the ports this module derives from the
    # same two faces. A solid turned one way and its collets another is the one failure a
    # verify cannot catch, because it measures the solid and reports the collets.
    yaw, pitch, roll = _tee_turns("x+", "y+")
    check("solved turn lays the run", _face(_turn((0, 0, 1), yaw, pitch, roll)), "x+")
    check("solved turn lays the branch", _face(_turn((0, 1, 0), yaw, pitch, roll)), "y+")
    try:
        _tee_turns("x+", "x-")
        fails.append("tee turn refuses faces not square")
        print("  FAIL tee turn refuses faces not square: returned a turn for x+ / x-")
    except ValueError:
        print("  ok   tee turn refuses faces not square: raised")
    # A box the fast pass filters on is a box the solid fills. Tight on the run, and short
    # of the branch by the body's own radius on the other side.
    box = t.box()
    check("box spans the run", box["x"], (-TEE_RUN_HALF, TEE_RUN_HALF))
    check("box is short behind the branch",
          box["y"], (t.centre()[1] - TEE_HALF_W, t.centre()[1] + TEE_BRANCH_REACH))

    print("space — every port lands where _contents places it")
    a = build(sp, vals)
    # The junctions the space holds FIXED are read straight off `_contents`, so what there is to
    # check about them is that every anchor the JOINTS name is a port the arrangement actually
    # has — a fitting renamed or a port dropped upstream fails here rather than costing nothing.
    named = {a for _id, frm, to in sp.joints for a in (frm, to)}
    have = set(sp.fixed) | {c for t in a.trays.values() for c in t.collets()}
    check("every joint's anchors are ports", sorted(named - have), [])
    for name, fn in (("source", _c.source_tray_port), ("selects", _c.selects_tray_port),
                     ("bag-a", _c.bag_a_tray_port)):
        for port, (pos, face) in a.trays[name].collets().items():
            want, wface = fn(port)
            d = max(abs(p - q) for p, q in zip(want, pos))
            check(f"{port}", d, 0.0)
            check(f"{port} face", face, wface)

    print("current — what the tree builds today costs")
    print(f"  ok   tube {a.tube:.0f} mm, bends {a.bends}, cost {a.cost:.0f}, "
          f"face y {a.face:.1f}, {'; '.join(a.clash) if a.clash else 'box-clear'}")

    # The control the whole filter stands on. This machine is built, and its gates pass, so
    # an arrangement scan that rejects it is rejecting reality — which is what a box pass
    # holding a printed piece, a routed run or the display's own compound does.
    print("filter — the machine that exists survives it")
    w = build(sp, vals, world=True)
    check("current against the placed world", w.clash, ())

    print(f"\n{'PASS' if not fails else 'FAIL: ' + ', '.join(sorted(set(fails)))}")
    return 1 if fails else 0


# --- CLI ------------------------------------------------------------------

def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("space", help="the choices, the joints, the cavity and the weights")
    p = sub.add_parser("rank", help="every arrangement, scored, best first")
    p.add_argument("--top", type=int, default=10)
    p.add_argument("--full", action="store_true", help="the winner joint by joint")
    p.add_argument("--no-world", action="store_true",
                   help="tube cost alone — do not filter against the placed machine")
    p = sub.add_parser("show", help="one arrangement, joint by joint")
    p.add_argument("which", help="'current', or a rank index")
    p = sub.add_parser("verify", help="a ranked arrangement in the exact world")
    p.add_argument("--rank", type=int, default=1)
    p.add_argument("--clearance", type=float, default=0.0)
    sub.add_parser("selftest", help="known-answer controls, then the real column")
    args = ap.parse_args(argv)

    sp = front_column()
    if args.cmd == "space":
        print(sp.report())
        return 0
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "show":
        if args.which == "current":
            print(build(sp, current()).report())
        else:
            n = int(args.which)
            print(rank(sp, top=n)[n - 1].report())
        return 0
    if args.cmd == "rank":
        print(sp.report())
        print()
        best = rank(sp, top=args.top, world=not args.no_world)
        cur = build(sp, current(), world=not args.no_world)
        print(f"measured against: "
              f"{'the column and the cavity alone' if args.no_world else 'the placed machine'}"
              f", holding out {', '.join(held_out(sp))}")
        print()
        print(f"{'#':>3}  {'cost':>6}  {'tube':>6}  {'bend':>4}  {'face y':>6}   arrangement")
        for n, a in enumerate(best, 1):
            print(f"{n:>3}  {a.cost:6.0f}  {a.tube:6.0f}  {a.bends:4d}  {a.face:6.1f}   "
                  f"{a.vector()}")
        print(f"{'now':>3}  {cur.cost:6.0f}  {cur.tube:6.0f}  {cur.bends:4d}  "
              f"{cur.face:6.1f}   {cur.vector()}")
        if args.full and best:
            print()
            print(best[0].report())
        return 0
    if args.cmd == "verify":
        print(verify(rank(sp, top=args.rank)[args.rank - 1], clearance=args.clearance))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
