"""_lines — the runs the box carries, authored port to port.

[`_routing.py`](_routing.py) is the kit; this file is the authorship: one `route(...)` per
connection, its waypoints written against the ports and body faces that shape them.

Today: the flavor tap and EVERY FLUID SEGMENT the manifold owes —
[fluid-topology](/hardware/topology/fluid-topology.md)'s whole shared section (fluid-1
through fluid-8), both bag circuits (fluid-14 / 15 / 16 in the front column, fluid-24 / 25 /
26 in the loft), both PUMP ROWS (fluid-9 through fluid-13 in the front column, fluid-19
through fluid-23 and fluid-27 in the loft), and the two nozzle gates' runs out of the
machine, fluid-17 / 18 / 28. Fifteen corridors carry them, each measured off the faces that
bound it:

  * the WALL SEQUENCE, the west wall's own column: the ASSE chain on the bulkhead's line, the
    split and the regulator inline ahead of it, all three on the chain's own axis, so one
    line carries every mouth. water-1, water-2 and fluid-1 are the straights between them,
    and the family reads — and later mounts — as one spine. The basin and its rails hang
    under the chain's vent, and the deck under all of it is the loft trays' ground and holds
    no station for any of them (`fit.py slab`).
  * the sequence's forward throw: the regulator's outlet fires down the wall's open strip and
    fluid-2 is one leaning leg from it onto V-A's inlet at the manifold's port plane
    ([312.1](SRC_PORT_Z)) — the whole fall and the whole cross in one move, straight off each
    mouth. The slot between V-K's east face and the pump's west one, which this line once
    climbed and crossed the machine in, now carries only fluid-17, in the band over the
    shelf's tallest module on its way aft to the pump's flank.
  * the band ahead of the cold core's front face (`_contents.SOURCE_TRAY_AFT_BAND`), which
    is where every aft-facing collet in the column turns. It is [24](AFT_BAND) mm deep
    because at the pump row's two planes it carries THREE lines abreast, and its depth is
    what three 1/4" tubes at the clearance floor come to. How far into it a lane stands is
    the straight the turn onto that lane is seated on, so the lanes are struck once at the
    top of `_authored_runs` and taken by name: the climb on the core's own face, the row's
    near lane one turn off the tray's, the far lane a `LINE_PITCH` in from the climb, and the
    middle between the two for a run crossing a storey up. fluid-4 turns forward in it onto
    V-B's own X; fluid-15 holds its plane across the machine floor. Nothing stands in the
    band, and nothing may: it runs the column's whole height.
  * the PUMP LANE, the strip west of the tray column and aft of channel A's pump, and the
    one corridor in the front column that reaches the trays' aft collets without meeting
    them. Both of pump B's lines run down it and both of channel A's tees stand in it, each
    on the column of the barb its run butts and each pushed off the rim it would otherwise
    overrun (`_contents.pump_row_tee_pos`) — the suction tee east against the tray column,
    the discharge tee west against the front column's own lip rim, [32.41](PUMP_LANE_W) mm
    apart. Every run on this lane holds one level, the bag-A pair's own port plane, because
    `_contents._build` stood the barbs on it: fluid-11 and fluid-12 lean the
    [4.05](PUMP_DISCH_LEAN) mm the fittings gave way by, and fluid-10 and fluid-13 come about
    in the band on their own lanes, [7.35](PUMP_ROW_PITCH) mm apart, the suction leg turning
    west off the tray's west seat and the discharge leg east under it to its east one. The
    only legs that change level are the two BRANCHES, which stand up out of the lane: fluid-9
    falls a stack pitch into Y-C's from the selects pair, and Y-D's is the storey-high climb
    to the nozzle gate.
  * the SHELF CROSSING, the stratum over the electronics shelf — a lane standing [7.86](SHELF_STEP)
    mm over the tallest lid standing under it. On the cap itself the modules stand shoulder to
    shoulder, the widest lane between them [0](SHELF_GAP) mm against a 1/4" line's own
    [6.35](TUBE_OD): the shelf is a FLOOR at this end of the machine and not a field of lanes, so
    what crosses it crosses over. fluid-19 does, from the front column to the strip aft of the
    ground stack, where the cap carries nothing and the fall to the loft's plane is clear.
  * the MACHINE CORRIDOR under all of it (`_contents.MACHINE_CORRIDOR`) —
    [47.5](CORRIDOR_DEPTH) mm between the shroud's aft face and the core's front one, empty
    from the floor slab to the shroud's roof. It carries ONE lane: fluid-15, which crosses in
    the aft band as far as the TRAY-EAST LANE and goes straight up out of it there. Only one
    of the two bag lines is in here at all — reservoir B's climbs inside the cold core, in the
    core's own +Y pour band, which stands under the fitting it feeds — so nothing has to pass
    fluid-15's climb and the corridor needs no second lane to get past it. The two evaporator
    stubs turn in the same corridor a stratum above.
  * the hopper's fall column, from the spout straight down to the port plane —
    [34.62](HOPPER_FALL) mm with nothing in it. The tray's east seat hangs on that column
    (`_contents.source_tray_pos`), so fluid-4 arrives already on V-B-I's line and closes on
    the one coordinate left; two would raise, which is what keeps the seat under the spout.
  * the JUNCTION's own two columns, ahead of the source and selects pairs and
    [4.945](COLUMN_SPREAD) mm outboard of their seats (`_contents.junction_column_x`). Each
    carries one tee and the two legs off it, fluid-3 falling [65.6](STACK_PITCH) mm from the
    source collet to the selects one through the fitting's run, and the two branches meet
    across the gap on fluid-6. Nothing places the columns but the four collets and the
    fitting's own reach.
  * the TRAY-EAST LANE, between the manifold column's east plate edge and the condenser's west
    face — [15.38](TRAY_EAST_LANE) mm, and the one corridor at the manifold's own height that
    runs the machine's FULL DEPTH with nothing standing in it. fluid-15 climbs in it and comes
    forward down it, passing the column on the outside, and fluid-22 crosses into it and runs
    aft down it. Both stand on the SAME side, hugging the condenser's intake face at the
    clearance floor, because the lane is one tube wide and they never share a height: the climb
    stops at the fitting's run plane and the crossing enters above it. What holds them to one
    side is that nothing else descends here — the line that used to is fluid-21, and it goes
    down the COLLET BAND instead. The lane is bounded by two bodies neither of which is placed
    against it: the trays' east face is the column's, and the condenser's west face is the
    block's intake side.
  * the COLLET BAND, the head column's own aft margin — the [9.5](COLLET_PROUD) mm between the
    trays' plate edge and the plane their aft collets stand on. It is a corridor by accident of
    the part: `two_valve_tray` sizes the plate to the valve's saddle and the ports reach past it,
    so all three storeys leave the same empty margin over the plate and it runs the whole height
    of the column. Nothing crosses it, because everything that turns off an aft collet does so
    in the AFT BAND behind it. fluid-21 comes forward down it on the east plate edge's own
    column, clear of the east seat's valve, and crosses onto the barb's column in it — ahead of
    the aft band, where the tray-east lane's own climb stands.
  * the STRIP ahead of the bag-A pair — [20.59](BAG_STRIP) mm between the pump row's aft faces
    and that pair's forward collets, and the shallowest corridor in the machine. Y-E stands
    ACROSS it (`_contents.y_e_pos`) and fluid-14, fluid-15 and fluid-16 all reach it here, along
    with the four legs that land on the two pumps' own barbs. Nothing stands in the strip but
    that fitting, and what bounds it is placed at both ends: the pump row's Y is its twin's and
    the pair's is the head column's.
  * the selects pair's own port plane at [246.5](SEL_PORT_Z), where fluid-7 and fluid-8 arrive
    down their columns at the two channel gates, and the bag pair's a stack pitch below it,
    where fluid-14 and fluid-16 leave forward and both pumps' four barbs stand. Those two legs
    CLIMB out of this plane, because the fitting they reach stands over it.
  * the LOFT's own port plane at [267.7](LOFT_PORT_Z), where the whole of channel B stands.
    Both of the loft's trays present their eight collets on it, so fluid-24 and fluid-26 are
    the bag-A pair's two legs read again a storey up, and fluid-18 and fluid-28 leave it on
    the level before they climb.
  * the loft's JUNCTION BAY (`_contents.AFT_TRAY_BAY`) — [141.6](LOFT_BAY) mm between the
    two trays, and the loft's answer to the front column's aft band, except that here the two
    pairs face each OTHER collet for collet. So its depth is a FITTING's: Y-G stands in it on
    the one column V-I-I and V-J-I share, and fluid-23 and fluid-27 are the two straight
    lengths of tube its run passes through, one `TEE_RUN_LEAD` apiece. It is two
    `JUNCTION_LEG_LEAD`s and nothing over, so a run that comes about in it turns one
    `PUMP_ROW_TURN` off the face it left rather than out at the end of its lead: the bay's two
    other columns each carry a facing pair that way — fluid-20 turning UP off V-H's draw
    against fluid-17 falling into V-G's gate. water-3 is the one fall the lane cannot seat:
    fluid-17's crossing leg TRAVELS that lane straight over V-K's column on its way to its own
    fall, and the arc it comes about on reaches a pitch ahead of the lane at this column — so
    the fall to V-K's mouth stands the second pitch ahead and comes aft into the mouth on the
    lead that buys.
  * the LOFT'S PUMP LANE — V-H's OWN COLUMN, in the band [1.002](LOFT_TEE_STANDOFF) mm over the
    aft stand's crown, where Y-F stands on the front column's own tee construction — RUN along
    the lane, BRANCH UP. The strip between the stand's east face and the SeaFlo's flank is a
    `LINE_HUG` and not a lane: a fitting two `TEE_HALF_W` across does not stand beside this
    stand at the port plane, at any x. What is open is the band OVER the plates, so the tee
    stands on the very collet it serves and the draw falls down one column instead of crossing
    a corridor to reach it. fluid-19 falls into that branch off the
    shelf crossing and fluid-20 comes about into the run's aft port out of the bay. The run's
    fore port leaves the loft altogether: channel B's PUMP stands in the front column, so
    fluid-21 and fluid-22 are the two runs that cross a storey and a half. They cross the deck
    on OPPOSITE strata and pass the head column on OPPOSITE sides — the inlet over the
    electronics shelf and down the COLLET BAND, the outlet over the water deck and up the
    TRAY-EAST LANE — so neither owes the other any separation, and each corridor carries the
    one line it was already the shape for.
  * the LOFT GAP, between the Y-H divider's crown and the aft stand's trays' —
    [37.2](LOFT_GAP) mm, and the one stratum at this height that runs clear across the machine
    with the electronics shelf under it and the basin's rails over it. Nothing crosses IN it
    today: water-3 crosses east a storey over it, on the west column's fifth rung, forward of
    every tray and rail — its stratum is ranked against fluid-19's fall on the column a pitch
    short of its own (the west-column table below) — and holds V-K's column down to the third
    `LINE_PITCH` ahead of the bay's own turn lane, whose lead seats its foot corner at stock.
  * the loft's OUTLET LANE (`_contents.aft_outlet_lane`), [188](OUTLET_LANE) mm of spare
    between the nozzle plate's aft face and the stated wall beyond its one lane's own minimum
    — spare the plate's own pin (V-J's aft collet rim on the rear corner column,
    `_contents.bag_b_tray_y`) leaves to the lane, which is struck off the wall and carries it
    as lead. ONE rung serves all three of the plate's aft outlets: the two gates and V-K
    stand a seat pitch apart across it, so their turns never meet and none needs a plane of
    its own. It is also the panel field's own footing: the water bulkhead stands over V-J's
    column and the C14 over V-G's, from the port row at [358.2](PORT_ROW_Z) down.
  * the SHELF under that field — [30.62](PANEL_SHELF) mm between the aft stand's own coil
    crown ([313](STAND_CROWN)) and the lowest body in the row, the one stratum at this end of
    the machine that runs clear across it. The STAND and not the pump: the SeaFlo reaches its
    box's crown only forward of y [348.4](SEAFLO_STEP_Y), stands [322.4](SEAFLO_AFT_CROWN)
    from there to its back face, and every crossing up here is behind that step — so a shelf
    hung off the pump's global crown stands [12.4](SHELF_OVERSHOOT) mm over the body it is
    actually clearing, which any run that comes back DOWN off it pays twice. The two outlet
    runs climb out of the outlet lane onto ONE level of it and cross in one lean each, east
    and forward together, onto their bulkheads' own columns ahead of the bodies before they
    climb the last storey; water-4 crosses it the other way, aft to fore, on the level its own
    fall needs. What holds the gates apart is the aim: a bulkhead column each, the climb on
    it, and the whole seat pitch their two turns start from.

Each junction lies in one line with the ports it joins. A divider stands off the two collets
at their own height, so no leg of fluid-14 or fluid-16 climbs; Y-H stands over the PSU's
crown instead, and its two legs carry that climb inside their leans. A tee lies
on the lane its run shares with two of its three, so the same holds for fluid-10 through
fluid-13 and for fluid-23 and fluid-27, and the third leg's is the branch's alone. The
manifold's junction is that lane stood on end: fluid-3, fluid-5, fluid-7 and fluid-8 fall down
their columns through a run, and fluid-6 crosses level on the two branches. Channel B's row is
the exception, and the STOREY is why: its pump stands in the front column and both its junctions
in the loft, so fluid-21 and fluid-22 change level whatever they leave by — the inlet forward
off Y-F's run, the outlet down into Y-G's stem.

Every port here has the straight a line off it needs — `scorecard.port_leads` gates it, at each
port's own bore along its own axis, and a collet with a body parked in front of it fails the
build the way two overlapping solids do.

Every other connection the machine owes is carried in the scorecard's connection table
against the `routed` axis, so an unauthored leg is counted, not lost — it comes back with
the second body it lands on.

Precedent: `pcba.tsx`'s `route(...)` call sites.
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(0, str(_here.parent))

import _boxes
import _contents as contents
import _routing as R
from _routing import route

# 1/4" ACR copper, drawn as the metal it is.
COPPER = cq.Color(0.72, 0.45, 0.20)
# 1/4" LLDPE, drawn as the soft tube it is.
LLDPE = cq.Color(0.90, 0.90, 0.94)

# Connections the pack does not carry as it stands, each with the measurement that blocks it —
# `_routing.BLOCKED` itself, filled as the runs below are drawn. They stay counted against the
# `routed` axis. A leg with no second body is not blocked by a measurement — it is unpacked — so
# it belongs to the connection table, not here.
BLOCKED = R.BLOCKED


def _frames():
    """A frame per placed component, per through-wall panel body, and the hopper funnel: its body
    box from the pack, its ports from the scorecard's port table. The panel bodies and the funnel
    are not interior components, but a run terminates on a bulkhead's inward collet and one falls
    from the funnel's drain, so they carry frames too."""
    import scorecard                                   # deferred: scorecard reads this module back

    placed = {**contents.build(), **contents.panel_bodies(),
              "hopper-funnel": (contents.placed_funnel(), None)}
    by_comp: dict = {}
    for p in scorecard.PORTS:
        if p.pos is not None and p.face and p.component in placed:
            by_comp.setdefault(p.component, {})[p.name] = (p.pos, p.face, p.diam)
    return {n: R.frame(n, placed[n][0], by_comp.get(n, {})) for n in placed}


_RUNS: list | None = None


def build_runs() -> list:
    """The authored runs. Each waypoint is a port offset, a body face, or a bend-radius reach.

    Memoized for the life of the process. The export, the routed axis, the lines-clear gate and
    the lane stations each ask for the runs; a rebuild is always a fresh process. `_routing`'s
    frame registry is filled by the first call and reads the same afterwards."""
    global _RUNS
    if _RUNS is None:
        _RUNS = _authored_runs()
    return _RUNS


# 1/4" LLDPE bends far tighter than the copper loop's former does; this is the radius the
# flavor tap and the hopper's fall are drawn at. It is DEFINED in `_contents` because a
# POSE depends on it and not only a path: a divider stands off the pair it joins by what
# its two legs' corners cost at this radius, so the pack would have to read the routing
# module back to place a fitting.
WBEND = contents.LLDPE_BEND
# `WBEND` is the radius a run turns at when nothing else is said, and taken as a default it is
# SELF-LIMITING: where the author gives no `stub`, `route` derives the collet stub FROM the bend
# radius, and a corner needs `R·tan(θ/2)` of tangent in each of the two legs it sits in — so a
# square corner on a run drawn at R4 leaves its fitting on a 4 mm straight, and 4 mm of straight
# seats nothing rounder than R4. The radius holds itself down.
#
# So the runs that turn tighter than that carry a MEASURED radius instead of the default: the
# largest their own legs seat, backed off from where the tangent check refuses. What a leg is,
# on most of them, is the standoff between a fitting and the LANE its run comes about on — and a
# lane stands in a band with two ends, so the lane is written here at the far end of whatever
# depth the band has left. The runs still under the R25.4 that 1/4" LLDPE wants
# (`scorecard.STOCKS`) are the ones whose band is spent: a line already on every `LINE_PITCH` of
# it, or a body closing it. `scorecard.bend_radius` names each with its binding leg's endpoints.
# The tap-water and CO2 pigtails' radius — hand-formed 1/4" LLDPE.
PWBEND = 3.0
CBEND = 3.0
# The 3/8" braided-PVC discharge stub's minimum bend radius (neoPure PVCR-0610 spec).
HOSE_BEND = 15.9
# How far off a collet's own axis a soft-LLDPE run may leave or enter as one straight length,
# past the rigid-copper `COLLET_SKEW`. Y-H's two legs are a straight at exactly this lean and
# the reach that stands the fitting off its pair is struck on it (`_contents.divider_reach`),
# so the number is the PACK's and this name is bound to it.
FLAVOR_SKEW = contents.FLAVOR_SKEW
# The straight the fall into Y-H's stem is seated on: the run comes about this far ahead of the
# collet, in the plane the stem faces. Y-G's fall comes about at one `WBEND` instead — its stem
# faces UP into the basin's own column, so the lane it turns on is under the rails and the
# straight it has to spend is the `JUNCTION_LEG_LEAD` the collet itself takes.
STEM_FALL_REACH = 2.0 * WBEND
# The climb out of the regulator's pocket runs UP ITS OWN FITTING'S FACE, one clearance
# floor off it. The outlet faces east into the SeaFlo's flank with barely a tube between
# them, so the run cannot turn where it leaves — and what crowds it as it climbs is the
# pump's forward FOOT, which stands off the regulator's east face in Y rather than in X. So
# every millimetre the climb steps east is a millimetre off the foot, and the run hugs the
# body it belongs to instead: the fitting it is leaving. `clearances()` reports what the
# foot is left, which is the gap that means anything here.
CLIMB_HUG = contents.LINE_HUG
# Centre to centre between two 1/4" lines sharing a corridor, and the same separation taken as
# a LEG with a corner at each end. Both live on the PACK's side, for `WBEND`'s reason: the
# water split's pose is one `LINE_STEP` off the column that feeds it, so the pack would have to
# read this module back to place a fitting.
LINE_PITCH = contents.LINE_PITCH
LINE_STEP = contents.LINE_STEP


def lean_leads(f_from, p_from, f_to, p_to, radius=contents.LLDPE_STOCK_BEND,
               straight=contents.DIVIDER_LEG_STRAIGHT, skew=FLAVOR_SKEW):
    """Two waypoints joining a pair of mouths that FACE THE SAME WAY, and the lean they stand
    on: `((W1, W2), lean°, lead, tangent)`.

    The shape is `bent`'s two-lead lean — a straight off each mouth, one leg between them — and
    what this solves is the direction of those two leads. A lead that runs dead on its collet's
    axis makes the corner it hands the lean a SQUARE one, and a square corner backs its arc
    `r·tan(45°)` = `r` down each leg: on-axis, a lead can never seat a radius bigger than its
    own length, and the two leads have only the mouths' own separation to divide between them.

    Leaning each lead into the crossing by `θ` opens both corners to `90° − θ`, and the tangent
    an arc of the same radius costs falls with `tan((90° − θ)/2)` — so the same budget seats a
    rounder corner the further off-axis the leads leave. The lean returned is the SHALLOWEST
    that seats `radius` at both corners with `straight` mm of tube still running straight into
    each collet — what the corner needs and no more of the collet's own `skew` than that.

    The two leads carry the whole separation between them, so the leg between them is the
    crossing alone: level in the mouths' shared axis, shortened by what the leads lean out.

    RAISES when the budget cannot buy the arc at any lean the collet takes — the mouths are too
    close along their own axis, and the answer is at whichever end of the sequence has room."""
    a, b = f_from.at(p_from), f_to.at(p_to)
    n = f_from.normal(p_from)                     # the direction both mouths point the run
    if R.leg_skew(a, b, n) < 1e-9:
        raise ValueError("lean_leads: the two mouths stand on one line — nothing to lean into")
    budget = sum((b[i] - a[i]) * n[i] for i in range(3))     # their separation along that axis
    cross = [(b[i] - a[i]) - budget * n[i] for i in range(3)]  # and the rest of the way there
    q = math.sqrt(sum(c * c for c in cross))
    u = [c / q for c in cross]

    def lead_at(deg):
        return budget / (2.0 * math.cos(math.radians(deg)))

    def spare(deg):
        """Straight left over on each lead once an arc of `radius` seats in it."""
        return lead_at(deg) - radius * math.tan(math.radians(90.0 - deg) / 2.0)

    if spare(skew) < straight:
        raise ValueError(
            f"lean_leads: {budget:.2f} mm between the two mouths leaves {spare(skew):.2f} mm of "
            f"straight at the collet's own {skew:g}° of lean, under the {straight:g} an R"
            f"{radius:g} arc has to leave — the two ends need "
            f"{2.0 * (radius * math.tan(math.radians(90.0 - skew) / 2.0) + straight) * math.cos(math.radians(skew)) - budget:.2f} mm more between them.")
    lo, hi = 0.0, skew                            # spare() rises with the lean: bisect for its floor
    for _ in range(80):
        mid = (lo + hi) / 2.0
        lo, hi = (lo, mid) if spare(mid) >= straight else (mid, hi)
    lean = hi
    lead, rad = lead_at(lean), math.radians(lean)
    step = [math.cos(rad) * n[i] + math.sin(rad) * u[i] for i in range(3)]
    w1 = tuple(a[i] + lead * step[i] for i in range(3))
    w2 = tuple(b[i] - lead * step[i] for i in range(3))
    return (w1, w2), lean, lead, radius * math.tan(math.radians(90.0 - lean) / 2.0)


def _tilt(n, toward, deg):
    """`n` turned `deg` toward `toward`, in the plane those two span. `toward` parallel to `n`
    spans no plane and there is nothing to lean into, so the direction comes back unchanged."""
    t = [toward[i] - n[i] * sum(toward[j] * n[j] for j in range(3)) for i in range(3)]
    m = math.sqrt(sum(c * c for c in t))
    if m < 1e-12:
        return tuple(n)
    rad = math.radians(deg)
    return tuple(math.cos(rad) * n[i] + math.sin(rad) * (t[i] / m) for i in range(3))


def _seat_lean(a, u, b, v, la, lb, pa, pb, straight, cap):
    """One trial of the lean pair: the two waypoints, the turn each corner makes, and the
    radius each seats once `straight` is taken off its lead."""
    da, db = _tilt(u, [b[i] - a[i] for i in range(3)], pa), _tilt(v, [a[i] - b[i] for i in range(3)], pb)
    w1 = tuple(a[i] + la * da[i] for i in range(3))
    w2 = tuple(b[i] + lb * db[i] for i in range(3))
    span = math.dist(w1, w2)
    if span < 1e-9:
        return w1, w2, 0.0, 0.0, 0.0, 0.0
    d = [(w2[i] - w1[i]) / span for i in range(3)]
    ang = lambda p, q: math.degrees(math.acos(max(-1.0, min(1.0,      # noqa: E731
        sum(p[i] * q[i] for i in range(3))))))
    t1, t2 = ang(da, d), ang(d, [-c for c in db])
    k1, k2 = math.tan(math.radians(t1) / 2.0), math.tan(math.radians(t2) / 2.0)
    r1 = min(cap, max(0.0, la - straight) / k1) if k1 > 1e-9 else cap
    r2 = min(cap, max(0.0, lb - straight) / k2) if k2 > 1e-9 else cap
    spent = r1 * k1 + r2 * k2                      # the leg between them is shared
    if spent > span:
        r1, r2 = r1 * span / spent, r2 * span / spent
    return w1, w2, t1, t2, r1, r2


def _mouth(f, anchor: str):
    """A `route`/`bent` anchor — `"component.port"` — split into the frame and port name
    `lean_into` reads, so a run states its two ends once and both the solve and the run itself
    are struck from the same string."""
    comp, _, port = anchor.partition(".")
    return f[comp], port


def lean_into(f_from, p_from, f_to, p_to, lead, radius=contents.LLDPE_STOCK_BEND,
              straight=contents.DIVIDER_LEG_STRAIGHT, skew=FLAVOR_SKEW):
    """Two waypoints joining a pair of mouths in ANY relative orientation, each lead leaned
    into the single leg between them: `((W1, W2), (lean1°, lean2°), radius, (turn1°, turn2°))`.

    `lean_leads` is the case where both mouths FACE THE SAME WAY: their normals are one
    direction, the separation along it is one budget, and the two leads divide it. This is the
    general one — two normals pointing wherever the fittings put them, and each lead paying
    `r·tan(θ/2)` at its own corner on a leg both share. It is the shape most of the pack's tight
    corners are: a mouth whose run has to go somewhere its own axis does not point.

    Where the lean pays is the corner PAST SQUARE. A lead dead on its collet's axis, handing off
    to a leg that comes back the way the lead came, turns more than 90°, and `tan(θ/2)` is above
    1 there — so the corner spends more tangent than the lead is long and the radius lands under
    it. Every degree of lean is a degree off that turn.

    `straight` comes off the lead FIRST and the corner seats in what is left: a collet grips the
    tube, and an arc starting at the collet face leaves the fitting nothing to hold. The radius
    returned is the caller's to hand back as `bent(..., bend=r)` — `seat_radii` reads the leg
    alone and otherwise spends the lead whole.

    `lead` is one reach for both ends or `(out, in)`, and it is the caller's to name: how far a
    run may stand off its own mouth is a fact about the air the pack leaves beside it. What the
    reach buys runs out — past where the two leads overshoot each other the leg between them
    shortens faster than the turns open, and the radius comes back DOWN.

    This sweeps: the answer is a maximum, not a threshold. Ties go to the shallower pair, so no
    more of the collet is spent than the corner needs."""
    a, u = f_from.at(p_from), f_from.normal(p_from)
    b, v = f_to.at(p_to), f_to.normal(p_to)
    la, lb = lead if isinstance(lead, (tuple, list)) else (lead, lead)
    if min(la, lb) <= straight:
        raise ValueError(
            f"lean_into: a lead of {min(la, lb):g} mm has no corner in it — {straight:g} of it is "
            f"the straight the collet grips on. Give the run more standoff, or say a shorter "
            f"`straight`.")

    # Each lead's window narrows around ITS OWN best, not the pair's — the two optima part
    # company whenever the mouths do (fluid-23 wants the whole skew at one end and none at the
    # other), and a window struck on one lean would refine the other out of reach.
    # The sweep stops a hair inside the skew. `bent` blocks a leg leaving more than `skew` off
    # its collet's axis, and a lean solved exactly ON that bound rounds to either side of it
    # through the tilt and the arc-cosine that measure it back.
    skew = max(0.0, skew - 1e-6)
    best = None
    (alo, ahi), (blo, bhi), step = (0.0, skew), (0.0, skew), skew / 24.0
    for _ in range(4):                             # coarse sweep, then three refinements
        pa = alo
        while pa <= ahi + 1e-9:
            pb = blo
            while pb <= bhi + 1e-9:
                w1, w2, t1, t2, r1, r2 = _seat_lean(a, u, b, v, la, lb, pa, pb, straight, radius)
                got = min(r1, r2)
                if best is None or got > best[0] + 1e-9:
                    best = (got, pa, pb, w1, w2, t1, t2)
                pb += step
            pa += step
        alo, ahi = max(0.0, best[1] - step), min(skew, best[1] + step)
        blo, bhi = max(0.0, best[2] - step), min(skew, best[2] + step)
        step /= 6.0
    got, pa, pb, w1, w2, t1, t2 = best
    return (w1, w2), (pa, pb), got, (t1, t2)


def _authored_runs() -> list:
    f = _frames()
    runs: list = []
    sp, reg, src = f["water-split"], f["flow-regulator"], f["source-tray-assembly"]

    # The AFT BAND — the strip between the tray column's aft collets and the cold core's front
    # face, `_contents.SOURCE_TRAY_AFT_BAND` deep. Every run that leaves the column aft, and
    # every run that crosses the machine at this depth, comes about in it. How far into the band
    # a lane stands IS the straight the turn onto it is seated on, so the lanes are named here
    # once and taken by name below — one ladder hung off the core's own face at a hug and a
    # `LINE_PITCH` per rung: the climb on the face, the row's far lane a pitch in, the near
    # lane a pitch again, and the middle left for the runs that cross a storey up, which share
    # the band's Y with the row without ever sharing its plane. What the ladder leaves at the
    # tray face — [5.125](PUMP_ROW_LEAD) mm — is the near lane's whole turn radius, and the
    # band has one rung to sell it and no depth to give it:
    #   * the RUNG IS FREE. Nothing crosses the band on the climb lane: fluid-15 rides it only
    #     as far as the tray-east lane and goes up out of it there, and reservoir B's line is
    #     not in this corridor at all — it climbs inside the cold core, up the +Y pour band
    #     standing under its own fitting. So no crossing has to get past fluid-15's climb, and
    #     the whole ladder may step one `LINE_PITCH` toward the core's face: the near lane's
    #     lead goes to 12.475 mm, which is what fluid-10's and fluid-13's corners are short of.
    #     It carries the row's two approach legs and both of channel A's tees with it, which is
    #     what makes it a rung to climb rather than a constant to raise.
    #   * the band cannot grow: its forward chain stands priced in
    #     `_contents.SOURCE_TRAY_AFT_BAND`'s own note — every link at its floor, so a
    #     millimetre on the band is a millimetre off the junction legs' own standoff.
    bag = f["bag-a-tray-assembly"]
    climb_lane = contents.FRONT_DEPTH - CLIMB_HUG - 6.35 / 2.0
    lane_2 = climb_lane - LINE_PITCH
    lane_1 = lane_2 - LINE_PITCH
    lane_mid = (lane_1 + lane_2) / 2.0

    # fluid-1 — the flavor tap off the water split, into the regulator that throttles it. The
    # two fittings stand inline on the wall sequence's own axis (`contents.flowreg_lane`), the
    # flavor collet firing forward at the inlet that faces it, so the run is the straight
    # between the two mouths and nothing about it turns.
    runs.append(route(
        "fluid-1", "water-split.to-flavor",
        "flow-regulator.inlet",
        kind="fluid", skew=FLAVOR_SKEW, stub=(2.0, 2.0),
        note="flavor tap: split run → flow regulator, straight in on the sequence's own axis"))

    # fluid-2 — the regulator's outlet to V-A, off the wall sequence's forward end. The outlet
    # fires forward down the west wall's open strip and the collet it feeds stands a storey
    # down and east of it, so the run is the divider legs' shape: a lead off each mouth and ONE
    # lean between them, carrying the whole fall and the whole cross in one move. The two
    # mouths face the same way a storey apart, so their two leads split the whole forward
    # budget between them and the lean runs level in y.
    #   What the leads do with that budget is `lean_leads`: a lead dead on its collet's axis
    # squares the corner it hands the lean, and a square corner spends its whole radius as
    # tangent in each leg — so an on-axis lead can never seat more than its own length, and the
    # budget here is [37.75](F2_BUDGET) mm for two arcs of the stock's own
    # [25.4](F2_STOCK) each. Leaning both leads into the crossing opens both corners
    # instead, and at [21.51](F2_LEAN)° the tangent falls to [17.29](F2_TANGENT) mm of the
    # [20.29](F2_LEAD) mm lead — a stock arc at each end with `DIVIDER_LEG_STRAIGHT` of tube
    # still running straight into each collet, and [0.422](F2_SLACK) mm of the budget still
    # spare before the collet's own skew is what binds instead of the corner.
    runs.append(R.bent(
        "fluid-2", "flow-regulator.outlet",
        *lean_leads(reg, "outlet", src, "V-A-I")[0],
        "source-tray-assembly.V-A-I",
        kind="fluid", skew=FLAVOR_SKEW,
        note="flavor tap: flow regulator → V-A inlet, one leaning leg off the wall's axis "
             "down onto the collet's own line, on two leads that lean into it"))

    # fluid-4 — the hopper's gravity drain into V-B. It carries head, not pressure, so no leg
    # may rise: it falls down the spout's OWN column to the pair's port plane, crosses LEVEL to
    # the collet's line, and turns forward into the aft-facing collet. The fall and the cross
    # are stated separately because the two columns are struck from different datums —
    # `_contents._tray_column_plan` hangs V-B's seat on the CORE's centreline carrying the
    # spout's offset, while the drain stands on the FUNNEL's own collar centre — and the day
    # those two part, a route that closes on one coordinate has two still differing. The cross
    # is level, so no leg rises whatever the gap between them is.
    runs.append(route(
        "fluid-4", "hopper-funnel.drain",
        src.z("V-B-I"),                      # straight down the spout's column to the port plane
        src.x("V-B-I"),                      # level across to the collet's own line
        "source-tray-assembly.V-B-I",        # and forward into the collet
        kind="fluid", skew=FLAVOR_SKEW, stub=(WBEND, WBEND),
        note="hopper drain → V-B inlet: down the spout's own column, one corner, and in — "
             "every leg falls or is level"))

    # fluid-24 / fluid-26 — the bag-B pair to its divider, and each is ONE STRAIGHT LENGTH OF
    # TUBE. The outlets are [14.7](DIVIDER_SPAN) apart and the two collets they join a seat
    # pitch ([34.25](SEAT_PITCH)) apart, so each leg closes [9.775](LEG_LEAN) mm of cross on
    # its way through; `_contents.y_h_pos` stands the trident on the pair's own port plane a
    # `divider_reach()` off their faces, which is that offset over the tangent of the lean a
    # collet takes. So the straight between each pair of mouths leaves both of them
    # [28](YH_LEG_LEAN)° off axis, and there is no corner on either run to seat an arc in.
    for cid, frm, to, who in (
        ("fluid-24", "bag-b-tray-assembly.V-I-O", "divider-y-h.Y-H-1", "pump return → Y-H"),
        ("fluid-26", "divider-y-h.Y-H-3", "bag-b-tray-assembly.V-H-I", "Y-H → bag B draw"),
    ):
        runs.append(R.bent(
            cid, frm, to, kind="fluid", skew=FLAVOR_SKEW,
            note=f"{who}: one straight length across the reach, leaving each collet at the "
                 f"lean the fitting's own standoff is struck on"))

    # fluid-14 / fluid-16 — the bag-A pair to Y-E, which stands ACROSS the strip ahead of them
    # rather than along the plane they share (`_contents.y_e_pos`). So neither of these is the
    # divider's leaning leg: both leave their collet forward into the strip and CLIMB out of the
    # port plane into a fitting standing over it, and the two climbs are different shapes because
    # the collets they enter are.
    #   fluid-14 takes the BRANCH, which faces down on V-F's own column. It runs forward to the
    # fitting's own Y and turns once, straight up the column into the collet — the whole leg is
    # in one plane and never leaves the seat's line.
    #   fluid-16 leaves the run's WEST collet, which faces along the strip, and it is authored as
    # ONE LEANING LEG the way the divider's are — straight off each collet for a `lead`, and a
    # single gentle move between them carrying the whole fall and the whole cross. So it stands on
    # the draw's own line only AT the collet: the strip ahead of the pump's own west barb, which
    # lands within a tube's width of that line, is the leg that leaves the barb's.
    y_e = f["tee-y-e"]
    runs.append(route(
        "fluid-14", "bag-a-tray-assembly.V-F-O",
        y_e.y("Y-E-1"),                      # forward into the strip, onto the fitting's own lane
        "tee-y-e.Y-E-1",                     # and up the seat's column into the branch
        kind="fluid", stub=7.95, skew=FLAVOR_SKEW,
        note="pump return → Y-E branch: forward into the strip and straight up V-F's own column"))

    # fluid-16's two mouths do not face one way either — Y-E's run collet fires WEST along the
    # strip and V-E's draw opens −Y out of the port plane — so the leg between them carries a
    # fall and a cross that neither axis points down, and both corners come in under square on
    # an on-axis lead.
    #
    # NEITHER OF ITS TWO REACHES IS ITS OWN TO SPEND. V-E-I and pump A's outlet barb stand
    # HEAD-ON down one y at one z, [0.905](STRIP_OFFSET) mm apart in x — closer than a tube, so
    # no lane in x parts them — and fluid-22 leaves that barb up a column this run's own descent
    # falls through. Both of these reaches move it in that pocket: the EXIT walks the top of the
    # descent WEST onto fluid-22's climb, and the APPROACH walks its foot AFT onto fluid-22's
    # stub. So the pocket carries one reach and both runs take it.
    #   `BAG_STRIP_REACH` is the largest the three take together with a `LINE_PITCH` still
    # between the two centrelines. What binds is the crossing — the top of this descent against
    # that climb — where the two tubes close to [1.02](STRIP_SEP) mm of each other over a
    # `LINE_HUG` floor. Split unequally the pocket buys about half a millimetre more on the
    # tighter of the two corners and stands that crossing exactly ON the floor; this is the
    # reach with room left in it.
    BAG_STRIP_REACH = 6.25
    f22_stub = BAG_STRIP_REACH
    (w1, w2), f16_lean, f16_r, _f16_turns = lean_into(
        *_mouth(f, "tee-y-e.Y-E-3"), *_mouth(f, "bag-a-tray-assembly.V-E-I"),
        (BAG_STRIP_REACH, BAG_STRIP_REACH))
    runs.append(R.bent(
        "fluid-16", "tee-y-e.Y-E-3", w1, w2, "bag-a-tray-assembly.V-E-I",
        kind="fluid", skew=FLAVOR_SKEW, bend=f16_r,
        note=f"Y-E run → bag A draw: one leaning leg carrying the fall to the port plane and the "
             f"cross onto the draw's line in one move, on leads leaning "
             f"{f16_lean[0]:.1f}°/{f16_lean[1]:.1f}° into it"))

    # fluid-3 / fluid-5 / fluid-7 / fluid-8 — the junction's four COLUMN LEGS. The source pair
    # stands in the selects pair's own seats a stack pitch up, so each of these joins two
    # collets already on one X, and the tee between them stands on the FRONT CHAIN'S OWN PLANE
    # (`_contents.junction_tee_pos` — the pumps, the pack's floor, the fitting's radius) and
    # `_contents.junction_column_x` outboard of the seat. A leg leaves its collet on axis for a
    # lead and enters the run collet on axis for another, and the single diagonal between them
    # carries the drop, the spread, and the standoff's remainder in one gentle move. Four legs,
    # one geometry, four times. Every term is a wall: the drop is what the fitting's run
    # leaves of the stack pitch (12.73), the forward is the chain — the pumps at the
    # front-corner pod's own floor put the standoff level with the drop — and the spread is
    # the branch reach (the priced fence on `junction_column_x`). The DROP is the ceiling
    # now: with the standoff at 12.73 the family seats R ≈ 11.9, a deeper standoff saturates
    # at ≈ 12.7 (the drop spent whole as one square corner's lead), and the 2.3 mm the
    # front-wall pod re-cut could still buy is worth ≈ +0.2 R — so the next real rung is the
    # fitting (18.5 branch reach published, `junction_column_x`) or the stack pitch itself.
    # The straight each leg leaves its collet on, solved against the diagonal it feeds: at
    # standoff = drop = D with spread x, the lead cap a/tan(θ/2) meets the diagonal's own
    # L/(tan(θa/2)+tan(θb/2)) at a = −D + √(2D² + x²/2) = 5.61 — under it the lead binds
    # first, over it the diagonal does, and either way both corners lose.
    JUNCTION_LEG_REACH = 5.6
    for cid, frm, to, who in (
        ("fluid-3", "source-tray-assembly.V-A-O", "tee-y-a.Y-A-1", "tap water source → Y-A"),
        ("fluid-5", "source-tray-assembly.V-B-O", "tee-y-b.Y-B-1", "hopper source → Y-B"),
        ("fluid-7", "tee-y-a.Y-A-2", "selects-tray-assembly.V-C-I", "Y-A → channel A select"),
        ("fluid-8", "tee-y-b.Y-B-2", "selects-tray-assembly.V-D-I", "Y-B → channel B select"),
    ):
        runs.append(R.bent(
            cid, frm, to, kind="fluid", skew=FLAVOR_SKEW,
            lead=JUNCTION_LEG_REACH,
            note=f"{who}: down the column, straight off each collet"))

    # fluid-6 — the H's CROSSBAR, Y-A's branch to Y-B's. The two tees stand on one line in Y and
    # in Z with their branches facing each other, so the run leaves and enters on axis with
    # nothing to turn: one straight length, [4](CROSSBAR) mm of exposed tube between the collet
    # faces, which is what a butted joint takes.
    runs.append(route(
        "fluid-6", "tee-y-a.Y-A-3", "tee-y-b.Y-B-3",
        kind="fluid", skew=FLAVOR_SKEW, stub=0.0,
        note="Y-A → Y-B: the H's bar, branch to branch, one straight length"))

    # fluid-15 — reservoir A to Y-E's RUN, and the longest run in the machine. Both ends of the
    # bag circuit ride it: the pump fills through it and V-E draws back through it.
    #
    # The bag port is LOW on the cold core's front face ([26.75](BAG_PORT_Z)) and at the EAST end
    # of its column (x [168](BAG_PORT_X)). Over that x the condenser stands from
    # [160.5](CONDENSER_FLOOR) up and leaves the core's face `_contents.CORE_FACE_CLEAR`. So the
    # run crosses the machine at the port's own height, down the MACHINE CORRIDOR, holding the
    # AFT BAND's own plane. The two evaporator stubs leave the same face a stratum above this one
    # and turn in the same corridor.
    #
    # It stops crossing at the TRAY-EAST LANE — the strip between the trays' own plate edge and
    # the condenser's west face, east of the whole manifold column, and the one corridor in this
    # machine that runs the FULL DEPTH at the manifold's height with nothing in it. The climb
    # stands in that lane and goes up it as far as the fitting's own RUN, which is the plane this
    # line arrives on; the forward leg holds that plane into the strip ahead of the pair, and the
    # only turn left is west into the run's east collet, which faces back down the lane at it.
    # Every leg is level or climbing: the bag takes pump pressure one way and pump suction the
    # other. This is also the leg that puts the fitting above the port plane, which is what lets
    # the pair's own two legs reach it from below.
    # The tray-east lane's own CLIMB COLUMN, hugging the condenser's intake face: the lane is one
    # tube wide at the clearance floor, so a line climbing it stands on one side and what shares
    # it takes its own Y lane rather than the other side. Both of the machine's long climbs use
    # it — this one and fluid-22 — and the refrigerant line falls down the lane's WEST side.
    shroud, cond = f["compressor-shroud"], f["condenser+fan"]
    lane_e = cond.bb.xmin - CLIMB_HUG - 6.35 / 2.0
    # The crossing lane holds mid-band, and the CLIMB is what pins it there: the corridor's
    # two east-bound legs cross the climb's column low — refrig-2 comes east at y 161 on the
    # evaporator stratum and co2-2 a stratum under at 159.65 — and a climb standing any
    # closer to the tray face than one pitch off refrig-2's leg (168.35) passes through
    # them. The turn off the bag port seats what is left of the band aft of that floor.
    lane_aft = R.channel(contents.FRONT_DEPTH - contents.SOURCE_TRAY_AFT_BAND, contents.FRONT_DEPTH)
    runs.append(route(
        "fluid-15", "foam-assembly.reservoir-A",
        {"y": lane_aft},                                  # forward into the aft band's own plane
        {"x": lane_e},                                    # west down the corridor into the tray-east lane
        y_e.z("Y-E-2"),                                   # up the lane to the fitting's own run plane
        y_e.y("Y-E-2"),                                   # forward down the lane into the strip
        "tee-y-e.Y-E-2",                                  # and west into the run's east collet
        # The turn off the climb is the one corner here the lane does not own: the REFRIGERANT
        # line crosses the tray-east lane directly under it, and an arc backs its tangent down
        # the leg it is leaving — so the radius this corner takes is how far down the climb it
        # may reach before it meets that crossing. The other three ride their legs.
        kind="fluid", bend={3: 10.2}, skew=FLAVOR_SKEW, stub=(WBEND, WBEND),
        note="reservoir A → Y-E run: west down the machine corridor at the port's own height, up "
             "the tray-east lane to the fitting's run plane, forward into the strip and west in"))

    # fluid-25 — reservoir B to Y-H's stem, and the run whose two ends stand one nearly over
    # the other. The reservoir drains from a ramped outlet at the bottom of its pocket and Y-H
    # hangs in the LOFT, so what this connection owes is a STOREY OF Z and [10.12](BAG_B_CROSS)
    # mm of plan. It does not cross the machine and it takes no lane in the corridor: the cold
    # core's own +Y BAND (`_cold_core_interface.west_lane_mid_y`) stands directly under the
    # fitting, runs the shell's whole height with nothing else in it, and carries the climb
    # potted — from the pocket-wall bore on the bulkhead's own axis, up the band, out through
    # the cap's `reservoir-b` conduit onto the deck. None of that is drawn here; it is shell,
    # and `assembly/cold-core.md` lays the tube in the band before the pour.
    #
    # What IS drawn is the last of it, off the conduit's mouth on the lid's outer face at
    # [253.4](BAG_B_DECK_Z): a rise off the deck and a reach east into the stem, and ONE CORNER
    # between them. THE CONDUIT OPENS +Z and THE STEM FACES WEST on the pair's own port plane,
    # so the two mouths are square to each other and the whole run stands in one section — the
    # stem's own plane at y [216.75](F25_PLANE_Y), which `_cold_core_interface.cap_conduits`
    # puts the bore on.
    #   EACH MOUTH HAS THE SAME ROOM, `_contents.stem_standoff` — the rise is the port plane's
    # height over the lid and the reach is struck to match it — and what the two leads spend of
    # that room is solved, not picked: past where they overshoot each other the leg between them
    # shortens faster than the turns open. The pair that seats the roundest corner leaves
    # [9](F25_RISE_LEAD) mm on the rise and [4.75](F25_REACH_LEAD) on the reach, both leaning
    # [22](F25_LEAN)° in, and the turns come to [49.6](F25_TURN)° and [10.6](F25_TURN_IN)°
    # against the square the two axes stand at.
    #   Nothing crowds it on this deck: the conduits' own column is what it rises on, and the
    # whole run stands east of that column.
    f25_room = contents.stem_standoff()

    def _f25_trials():
        """Every lead pair on the room, less the ones whose two arcs eat the whole leg between
        them: at the very top of the sweep the corners meet and the straight they share is
        gone, and a leg with no straight left in it is a pair of arcs and not a route."""
        for a in range(7, int(2.0 * f25_room) + 1):
            for b in range(7, int(2.0 * f25_room) + 1):
                got = lean_into(*_mouth(f, "foam-assembly.reservoir-B"),
                                *_mouth(f, "divider-y-h.Y-H-2"), (0.5 * a, 0.5 * b))
                (p, q), _lean, r, (t1, t2) = got
                spent = r * (math.tan(math.radians(t1) / 2.0) + math.tan(math.radians(t2) / 2.0))
                if spent <= math.dist(p, q) - contents.LINE_HUG:
                    yield got

    (w1, w2), f25_lean, f25_r, f25_turns = max(_f25_trials(), key=lambda got: got[2])
    runs.append(R.bent(
        "fluid-25", "foam-assembly.reservoir-B", w1, w2, "divider-y-h.Y-H-2",
        kind="fluid", skew=FLAVOR_SKEW, bend=f25_r,
        note=f"reservoir B → Y-H stem: up off the conduit and east into the stem in the stem's "
             f"own plane, each leg leaning {f25_lean[0]:.1f}°/{f25_lean[1]:.1f}° into the "
             f"corner between them"))

    # fluid-9 … fluid-13 — CHANNEL A's PUMP ROW, in the pump lane west of the tray column.
    # Five runs and two tees, and every one of them is a lane and a turn: the lane is the
    # strip the pump's own two lines run down (`_contents.pump_row_tee_pos`), and the turn is
    # the aft band, where each tray leg leaves its collet and comes about onto that lane.
    #
    # The band carries THREE tubes abreast at this height — the suction leg going west, the
    # discharge leg coming east, and reservoir B's climb crossing on its way to the loft — so
    # it is sized for three (`_contents.SOURCE_TRAY_AFT_BAND`), and the lanes it is cut into are
    # struck at the top of this function. Which lane a run takes is decided by what shares its
    # PLANE, not by what shares the band: at the barb plane fluid-10 and fluid-13 overlap in x
    # and so take one lane each, and a stack pitch up fluid-9 has the far lane to itself.
    #
    # Each tee's RUN lies along the lane and its BRANCH stands up, so the only leg that
    # climbs at a junction is the one that leaves the lane: fluid-9 falls a stack pitch into
    # Y-C's branch from the selects pair, and Y-D's branch is the storey-high climb to the
    # nozzle gate. Nothing else changes level — pump B's barbs stand on the bag-A pair's own
    # port plane, so the whole row is flat.
    y_c, y_d, pb = f["tee-y-c"], f["tee-y-d"], f["pump-b"]

    # fluid-9 — the selects pair's channel-A gate down to Y-C's branch. It leaves aft with
    # the rest of the row, comes west onto the tee's own column, runs forward down the lane
    # a storey above the tee, and falls in — the one leg of this junction that changes level,
    # and it is the branch's by construction.
    runs.append(route(
        "fluid-9", "selects-tray-assembly.V-C-O",
        {"y": lane_2},                       # aft the depth of the band, onto its far lane
        y_c.x("Y-C-1"),                      # west onto the tee's own column
        y_c.y("Y-C-1"),                      # forward down the pump lane, over the tee
        "tee-y-c.Y-C-1",                     # and down into the branch
        kind="fluid", stub=12.4, skew=FLAVOR_SKEW,
        note="channel A select → Y-C branch: west onto the tee's column, forward down the "
             "pump lane and a stack pitch down into the branch"))

    # fluid-10 — the bag-A draw into Y-C's aft run port. Same turn, same lane, one storey
    # lower and straight into the run: this leg and fluid-11 are the two halves of the one
    # line the tee sits in, so neither of them leaves the lane or the plane.
    runs.append(route(
        "fluid-10", "bag-a-tray-assembly.V-E-O",
        {"y": lane_1},                       # aft into the band, onto the ladder's near rung
        y_c.x("Y-C-2"),                      # west onto the tee's column
        "tee-y-c.Y-C-2",                     # and forward into the run's aft port
        # THE EXIT IS THE WHOLE STANDOFF THIS GATE HAS. The first rung of the ladder stands
        # this far aft of the collet, so the reach cannot grow without the exit running past
        # the rung it is aiming at and folding the corner back on itself. The corner it seats
        # is the tray's to give, not this number's.
        kind="fluid", stub=5.1, skew=FLAVOR_SKEW,
        note="bag A draw → Y-C run: aft, west onto the pump lane and straight down it"))

    # fluid-11 — Y-C's forward run port to pump B's inlet barb. The suction tee stands on
    # that barb's own column where the lane allows, but the barb sits inboard of the tray
    # column's west face, so the tee is the one that gives way and this leg comes about in
    # the strip between the pump's aft face and that column — the only band at this height
    # where a line may cross the lane without meeting the trays.
    runs.append(route(
        "fluid-11", "tee-y-c.Y-C-3",
        {"y": R.channel(pb.at("P-B-I")[1], y_c.at("Y-C-3")[1])},   # forward into the strip, midway
        pb.x("P-B-I"),                       # east onto the barb's own column
        "pump-b.P-B-I",                      # and forward into it
        kind="fluid", stub=9.9, skew=FLAVOR_SKEW,
        note="Y-C run → pump B inlet: down the lane, about in the strip behind the pump and "
             "onto the barb's own column"))

    # fluid-12 — pump B's outlet barb to Y-D's forward run port, and the shortest run in the
    # machine. The discharge tee stands on ITS barb's column too; here the barb sits outboard
    # of the front column's own lip rim, so the tee gives way by the millimetres the body's
    # radius needs and this leg leans that far back onto it — one straight length of LLDPE,
    # no corner. The docstring above carries the lean.
    #
    # It is also the ONE run on the machine that turns at the full [25.4](LLDPE_MIN_BEND) its
    # stock wants, and it gets there on a shallow lean rather than on room: the tangent an arc
    # costs goes as `R·tan(θ/2)`, so this run's [18.7](PUMP_DISCH_TURN)° corner asks only
    # [4.17](PUMP_DISCH_TANGENT) mm of straight where a square one would ask the whole radius.
    # The stub is stated rather than derived because the two numbers pull opposite ways here:
    # every millimetre of stub is a millimetre off the straight the lean is carried on, so too
    # short a stub cannot seat the arc, and too long a one steepens the lean into the collet —
    # at 4.9 it arrives 0.2° inside `FLAVOR_SKEW`, which is the whole window.
    runs.append(route(
        "fluid-12", "pump-b.P-B-O", "tee-y-d.Y-D-1",
        kind="fluid", skew=FLAVOR_SKEW, stub=(4.9, 4.9),
        note="pump B outlet → Y-D run: one leaning straight up the lane the tee stands on"))

    # fluid-13 — Y-D's aft run port to V-F, the valve that fills bag A. It comes up the lane,
    # turns into the band on the row's SECOND lane — the first is the suction leg's and the
    # third is reservoir B's climb — and runs east to the collet's own column.
    runs.append(route(
        "fluid-13", "tee-y-d.Y-D-2",
        {"y": lane_2},                       # aft into the band, onto the row's second lane
        bag.x("V-F-I"),                      # east onto the collet's own column
        "bag-a-tray-assembly.V-F-I",         # and forward into it
        # THE APPROACH IS SPENT, and not on air. The lane ahead of this collet is open — the
        # foam block's west face is the next thing in it — but the path stands only
        # [12.5](F13_APPROACH) mm off the port face to begin with, and a stub longer than that
        # would have the closing turn back out and come straight back in. So the closing
        # corner is held by where the LANE stands, not by this number: what buys it a rounder
        # turn is the tray's own standoff, not a reach.
        kind="fluid", stub=12.4, skew=FLAVOR_SKEW,
        note="Y-D run → V-F: up the pump lane, east across the band on its own lane and "
             "forward into the bag's fill gate"))

    # fluid-19 … fluid-23, fluid-27 — CHANNEL B's PUMP ROW. Its two junctions stand in the LOFT
    # and its pump a storey and a half below in the FRONT COLUMN, so two of these five runs
    # cross the machine and the row is not flat the way channel A's is.
    #
    #   Y-G stands IN THE BAY on the one column its run already has: V-I-I and V-J-I face each
    # other down a single line across it, so fluid-23 and fluid-27 are one `TEE_RUN_LEAD` of
    # straight tube apiece and neither turns — the bay is that fitting's own section.
    #   Y-F stands in the LOFT'S PUMP LANE, the strip between the trays' east face and the
    # SeaFlo's west flank, with its run along the lane and its branch standing UP — the front
    # column's own construction, read a storey and a half higher.
    pa, bb, nz = f["pump-a"], f["bag-b-tray-assembly"], f["nozzle-tray-assembly"]
    y_f, y_g = f["tee-y-f"], f["tee-y-g"]
    sea, vk = f["seaflo-pump"], f["vk-tray-assembly"]
    nzb = f["nozzle-b-tray-assembly"]

    def aft_turn_lane(stock: float) -> float:
        """The Y a run leaving the middle row's AFT face turns on — the plane its own closing
        corner wants, not a rung on a ladder.

        Three runs turn in this band and they are parted BY THEIR OWN COLUMNS: water-4 off
        V-K-O at the stand's east end, the nozzle-B gate off V-J-O a seat pitch west of it,
        and the nozzle-A feed on V-G's column between them. None of the three is within a
        tube of another in X, so none owes the others a lane, and stacking them a
        `LINE_PITCH` apart in Y spends on separation what their corners need for tangent.
        Each turns where a square arc at its own stock seats with the collet's
        `JUNCTION_LEG_LEAD` surviving in front of it. The band is the whole deck between the
        two rows, and what it holds is one turn's worth wherever the turn stands in X."""
        return vk.bb.ymax + contents.JUNCTION_LEG_LEAD + stock

    # The stratum a run crosses the WATER DECK on: the FUNNEL'S FLOOR, at the hug — the one
    # ceiling this end of the box has, and the funnel spans the crossing's whole forward
    # reach. The pump's crown sets the stratum's floor a storey down; everything between
    # crown and funnel is height the crossing banks, because the fall off this stratum into
    # the junction bay is a leg two corners split, and the bay's own shelf is pinned under
    # the basin's rails — every millimetre of ceiling is a millimetre of radius in that fall.
    funnel = f["hopper-funnel"]
    loft_cross_z = funnel.bb.zmin - CLIMB_HUG - 6.35 / 2.0

    # fluid-23 / fluid-27 — Y-G's two OUTLET legs. The fitting stands across the bay with both
    # outlets facing DOWN, so neither of these is a straight line: each leaves its valve's
    # collet along the bay on axis, comes about, and CLIMBS into the outlet standing over it.
    # The lean is `_contents.DIVIDER_OUTLET_X`, the offset the trident's own outlets carry.
    #   The two collets face each OTHER down one column an `AFT_TRAY_BAY` apart, and the bay
    # is `2·AFT_BAY_LEAD + LINE_PITCH` deep by construction — so each leg turns at the end of
    # its own lead and the two turns stand a line's width apart on the column they share,
    # before either of them leans off it.
    #   Both corners turn on the DIAGONAL between them, and what that diagonal spans is the
    # climb: `_contents.y_g_pos` stands the fitting's outlets `Y_G_CLIMB` over the stand's
    # own port plane, on the bay's midpoint — half a `LINE_PITCH` past where each lead
    # ends. Neither corner is capped: each turns at the roundest its own two legs carry.
    #   The climb rides the APPROACH lead, not the diagonal: the diagonal holds the rise
    # that leaves the bay-lead corner its whole cap, and everything the climb has over that
    # rise lengthens the lead into the outlet — whose corner stops at the diagonal's
    # remainder once the low corner has taken its share. So the low corner is the bay
    # lead's and the high corner is the diagonal's, and the family's next rung is the bay
    # (`_contents.AFT_TRAY_BAY`), not more climb.
    bay_lead = contents.AFT_BAY_LEAD
    y_g_rise = 5.0                       # the diagonal's own vertical share of the climb
    # HOW FAR DOWN AN OUTLET LEG MAY REACH. Y-G's outlets face down and stand over the BAY —
    # the band between the two plates, and east of the bag pair's own face — so what is under
    # them is the stand's seat and not a plate's crown. The leg reaches to one `LINE_HUG` over
    # that seat, which is the whole of the climb plus the port plane's own height on it.
    y_g_drop = y_g.at("Y-G-2")[2] - contents.aft_tray_z() - contents.LINE_HUG
    # WHICH SIDE OF V-K'S PLATE THE GATE'S FEED PASSES. The gate stands aft of that plate and
    # the outlet it is fed from stands forward of it, so the plate is between them: a straight
    # between the two mouths goes through it. West of the plate is the SeaFlo's flank, one
    # `LINE_HUG` of it, so the run takes the EAST lane — the deck between the stand's own east
    # face and the electrical flank, which is open the plate's whole depth. It leaves forward
    # off the collet, steps east onto that lane a `PUMP_ROW_TURN` clear of the plate, runs
    # forward down it past the plate, and comes west under the trident onto the column its
    # outlet stands on, where the last leg climbs into a mouth that faces down.
    #   Where the plate does NOT stand between them the straight is the run, and the two legs
    # off the mouths are a lead each — the bay's own and the outlet's drop.
    gate, outlet = nzb.at("V-J-I"), y_g.at("Y-G-2")
    f27_between = (min(gate[1], outlet[1]) < vk.bb.ymax and vk.bb.ymin < max(gate[1], outlet[1])
                   and min(gate[0], outlet[0]) - 6.35 / 2.0 < vk.bb.xmax
                   and vk.bb.xmin < max(gate[0], outlet[0]) + 6.35 / 2.0)
    if f27_between:
        # The lane clears the whole of what stands in the strip it runs down — V-K's plate for
        # the aft half of it and the TRIDENT for the forward half, whose own east face is the
        # far side of the column fluid-23's exit lead turns on.
        f27_lane = y_g.at('Y-G-2')[0]
        # WHERE IT TURNS EAST, AND IT IS NOT THE PLATE THAT SAYS. This run only has to get PAST
        # V-K's plate; turning off that plate's own face would lay the whole column between the
        # gate and the plate down as straight, in the one band the plate and `water-4` have to
        # move through, and would pin the run to the plate so it followed instead of leaving
        # room. The turn belongs as far AFT as it will go — its business is the lane, and every
        # millimetre it turns sooner is a millimetre of this column given back.
        #   THE COLLET IS WHAT STOPS IT, AND WHAT IT ASKS IS THE TANGENT AND A LITTLE MORE. The
        # arc cannot start before its own tangent point — that is geometry — and after it the
        # tube owes the fitting `DIVIDER_LEG_STRAIGHT`, the run of straight a collet still has
        # to grip once the arc seats. It does NOT owe a whole `JUNCTION_LEG_LEAD` on top: that
        # reach is 2 bend radii, which is a stub AND a tangent at the default radius, and this
        # corner's tangent is already [15](F27_TANGENT) mm on its own. The step's two corners
        # share the step and each turn on half of it, so that tangent is known before the turn
        # is placed and the leg is struck at what the pair actually costs: [18](F27_LEG) mm.
        #   NOTHING EAST OF IT BINDS. The step reaches toward the PSU's brick, but a square
        # corner is not where the tube is: the arc rounds it away, so the run does not stand on
        # the step's own east end until a whole tangent FORWARD of the turn, and measured
        # against the casting rather than its box the tube keeps [6.37](F27_PSU_CLEAR) mm of it.
        f27_step = (f27_lane - gate[0]) / 2.0
        f27_aft = gate[1] - f27_step - contents.DIVIDER_LEG_STRAIGHT
        runs.append(R.bent(
            "fluid-27", "nozzle-b-tray-assembly.V-J-I",
            (gate[0], f27_aft, gate[2]),      # forward off the collet, only as far as the turn
            (f27_lane, f27_aft, gate[2]),     # east onto the lane, which is the junction's own
                                              # column — the fitting stands ON this run's corridor
            "tee-y-g.Y-G-2",                  # and straight forward down it into the mouth that
                                              # faces back up it
            kind="fluid", skew=FLAVOR_SKEW,
            note="nozzle B gate ← Y-G: forward off the collet, east onto the lane, and straight "
                 "down it into the junction standing in that lane"))
    else:
        runs.append(R.bent("fluid-27", "nozzle-b-tray-assembly.V-J-I", "tee-y-g.Y-G-3",
                           kind="fluid", skew=FLAVOR_SKEW,
                           lead=(bay_lead, y_g_drop - y_g_rise),
                           note="nozzle B gate ← Y-G: out of the collet along the bay, about, and "
                                "up into the outlet standing over it"))

    # fluid-23 takes the same climb from the other side of the bay, and its collet does not
    # face the fitting: V-I-I opens EAST off the turned plate while Y-G-2 stands
    # [-18.1](F23_BACKTRACK) mm WEST of it, so the lead leaves east and the leg it hands off to
    # comes straight back — the corner past square again. WHAT BOUNDS THE EXIT is water-3's own
    # fall, which holds the column [-8.9](F23_EAST_AIR) mm east of this collet on its way to V-K:
    # the lead stops a `LINE_PITCH` short of it, which is the whole of the deck this run has.
    F23_LEAD = max(contents.DIVIDER_LEG_STRAIGHT + contents.LINE_HUG,
                   vk.at("V-K-I")[0] - LINE_PITCH - bb.at("V-I-I")[0])
    # The junction's own reach is now ALONG THE LANE and not down a stem: Y-G-3 faces FORWARD
    # off the tee's near end, so what this lead may spend is the band between that collet and
    # the bag pair's aft face — [29](F23_IN_REACH) mm of it, a `PUMP_ROW_TURN` off the plate.
    f23_in = y_g.at("Y-G-3")[1] - (bb.bb.ymax + contents.PUMP_ROW_TURN)
    (w1, w2), f23_lean, f23_r, _f23_turns = lean_into(
        *_mouth(f, "bag-b-tray-assembly.V-I-I"), *_mouth(f, "tee-y-g.Y-G-3"),
        (F23_LEAD, f23_in))
    runs.append(R.bent(
        "fluid-23", "bag-b-tray-assembly.V-I-I", w1, w2, "tee-y-g.Y-G-3",
        kind="fluid", skew=FLAVOR_SKEW, bend=f23_r,
        note=f"bag B fill ← Y-G: out of the collet along the bay and up into the outlet "
             f"standing over it, on leads leaning {f23_lean[0]:.1f}°/{f23_lean[1]:.1f}° into "
             f"the leg between them"))

    # fluid-20 — the bag-B draw into Y-F's aft run port. The tee stands over the collet's own
    # column (`_contents.aft_lane_x`), but the pair is turned (`_contents.BAG_B_TRAY_YAW`) and
    # this collet opens EAST at the plate's forward end while the run port opens AFT on the
    # plate's aft face, a plate's depth behind it. So the two are parted in Y as well as in
    # height, and the U that joins them lies in the LANE EAST OF THE TEE: the tee's own body
    # fills the column between the collet and the port at the run's plane, so the climb stands
    # a tube and its floor off that body's east face and comes back west onto the column only
    # once it is aft of the port.
    #   The come-forward leg is the tee's own approach, so it turns on the lead a collet leaves
    # plus the bend that follows it, and the west jog is what the tee's half-width leaves.
    yf_lane = f["tee-y-f"].bb.xmax + contents.PUMP_ROW_TURN
    runs.append(route(
        "fluid-20", "bag-b-tray-assembly.V-H-O",
        {"x": yf_lane},                          # east off the collet into the lane beside the tee
        y_f.z("Y-F-2"),                          # up that lane to the run's own plane
        y_f.y("Y-F-2", contents.JUNCTION_LEG_LEAD + contents.LLDPE_BEND),
                                                 # aft past the port, over the bay's mouth
        y_f.x("Y-F-2"),                          # west onto the port's own column
        "tee-y-f.Y-F-2",                         # and forward into the run's aft port
        kind="fluid", stub=WBEND, skew=FLAVOR_SKEW,
        note="bag B draw → Y-F run: east off the collet into the lane beside the tee, up it to "
             "the run's plane, aft past the port and forward into it from behind"))

    # fluid-21 / fluid-22 — the two legs between channel B's junctions in the LOFT and its pump
    # in the FRONT COLUMN, and the only two runs in the machine that cross a storey and a half
    # twice. They cross the deck on OPPOSITE strata and descend on OPPOSITE sides of the head
    # column, which is why the tray-east lane is left holding one line.
    #   fluid-21 leaves Y-F's run FORWARD along the loft's pump lane and never turns back: it
    # climbs onto the DECK CROSSING at the west column's second rung — its climb stands on
    # fluid-19's own plan line, so it holds a full rung under that run's crossing, and the
    # longer climb is what its top corner turns on — and LEANS east past the SeaFlo's
    # forward-west corner onto the head column's aft margin, at 45° through the corner's own
    # clearance point: the slot's x, the lane's y — the two margins the pump keeps everywhere else. It
    # holds that column the length of the machine into the front column's aft band, and falls
    # the whole storey and a half behind the tray column — the COLLET BAND, whose forward wall
    # is the east seat's valve body standing out past its own plate edge — leaning east as it
    # falls, so it lands on the barb's own column with only the forward run left.
    #   fluid-22 climbs BEFORE it crosses. Its barb is on the port plane too, and the height it
    # would otherwise cross east on is the height the refrigerant line leaves the condenser across
    # this lane on, so it goes up the strip first — clear over the junction standing across it —
    # and crosses at that height instead. Then aft down the lane on its own Y lane and up the rest
    # of the front column.
    band_x = bag.bb.xmax - CLIMB_HUG - 6.35 / 2.0
    band_y = bag.bb.ymax - CLIMB_HUG - 6.35 / 2.0
    sea_front = sea.bb.ymin

    # THE WEST COLUMN'S STRATA. Four lines cross the strip at x≈67–75 between the pump's own
    # discharge plane and the regulator's floor. The ladder stands on that plane: it is the
    # molded barb's height on the casting, so it holds wherever the stand carries the pump to
    # and whatever level the chain the barb feeds is mounted at.
    #   The column is pitched, not stacked: one `LINE_PITCH` a storey off that floor, so a run
    # moved between rungs lengthens a leg that is there rather than gaining one.
    #   The ladder's lid is the drip pan and its rails, and the pan is sized to the ladder:
    # its width is the moisture plate's own floor plus a millimetre (`drip_pan.PAN_X`), so
    # the rails end at x 59.8 and no rung over Y-F's (67.36) or V-K's (74.62) column meets
    # them. What ranks the rungs instead is the pairs themselves: Y-F's column stands 7.26
    # off V-K's, a pitch short by 0.09. The order, floor to crown: water-5 on the pinned rung,
    # fluid-21 on rung 2 (its lean passes fluid-17's slot leg at (84, 267) one pitch down),
    # fluid-17 on rung 3 (its bay fall is capped by the turn-lane leg, not the rung — moving
    # it buys nothing and shortens that fall), water-3 on rung 5 (its own first fall off the
    # split seats stock at 31). Rungs 1 and 4 stand empty — the ladder's slack.
    #   Fluid-19 crosses clear of the ladder, on Y-F's branch plane over the aft stand's
    # crown, and fluid-21 reaches rung 2 by a FALL out of that same tee's fore run port.
    west_col = [contents.seaflo_terminal("discharge")[0][2] + i * LINE_PITCH for i in range(6)]

    yf3, pai = y_f.at("Y-F-3"), pa.at("P-A-I")
    graze_x = sea.bb.xmin - CLIMB_HUG - 6.35 / 2.0   # the slot's x — the SeaFlo's west margin
    cross_y = sea_front - contents.PUMP_ROW_TURN     # the lane's y — its forward margin
    # Y-F stands over the aft stand's crown and the deck crossing runs UNDER it, so this leg
    # FALLS out of the collet instead of climbing into the lane. The fall is a leg with a
    # corner at each end and it holds both their tangents, so what it seats is HALF its own
    # height — and the lead off the collet is that same half, which is what makes neither
    # corner the tighter one. The lane forward of the collet is clear to the lean's own turn.
    yf3_drop = yf3[2] - west_col[2]
    yf3_lead = yf3_drop / 2.0
    # THE COLLET IS ALREADY EAST OF THE CASTING. Y-F stands over V-H-O and the SeaFlo's flank
    # ends [39](F21_GRAZE_CLEAR) mm west of that column, so this run never comes near the
    # corner a lean would be dodging — and struck as a 45° about that corner the two waypoints
    # land AFT of each other while the run is travelling forward, which is a doubling-back and
    # two 135° turns on a six millimetre leg. What the run owes between the collet and the
    # band is [31.6](F21_BAND_STEP) mm of X, and the fall already carries more than that.
    runs.append(R.bent(
        "fluid-21", "tee-y-f.Y-F-3",
        # THE RUN REACHES THE BLOCK'S LANE BEFORE IT DROPS PAST THE CROWN. Y-F stands over V-H-O
        # and that collet's column is east of the condenser's west flank, so a fall struck on
        # the tee's own x stands inside the block for every millimetre it crosses. The port
        # itself is clear over the crown, so the west move is taken THERE, on the plane the
        # collet already presents on, and the fall that follows is the same single leg it was.
        (lane_e, yf3[1] - yf3_lead, yf3[2]),         # west onto the block's own lane, over its crown
        (lane_e, yf3[1] - yf3_lead, west_col[2]),    # and down onto the deck crossing
        (band_x, band_y, west_col[2]),               # forward the machine's length into the collet band
        (pai[0], band_y, pai[2]),                    # the fall, leaning onto the barb's own column
        "pump-a.P-A-I",                              # and forward into it
        kind="fluid", lead=(yf3_lead, WBEND), skew=FLAVOR_SKEW,
        note="Y-F run → pump B-channel inlet: forward out of the loft's pump lane onto the deck "
             "crossing, the machine's length into the collet band, and down the front column "
             "leaning onto the barb's own column"))

    runs.append(route(
        "fluid-22", "pump-a.P-A-O",
        {"z": y_e.bb.zmax + LINE_STEP},      # up the strip, clear over the junction across it
        # THE STEM'S OWN COLUMN IS THE LANE, ONCE THE RUN IS ALOFT AND AFT OF THE RISER. Y-G
        # stands in the strip between the lanes and the band over its crown is [58.9](YG_COLUMN)
        # mm clear to the hopper's floor, so the length of the machine and the fall want one
        # column and the fall is taken ON the stem. THE CLIMB CANNOT HAVE IT: the stem stands
        # east of `lane_e`, the lane the condenser's west flank leaves, and carb-1's riser holds
        # that lane for the whole storey — so this run climbs a `LINE_PITCH` west of the riser,
        # in the strip neither the block nor the riser is in.
        {"x": min(y_g.at("Y-G-1")[0], lane_e - LINE_PITCH)},
        # AND STRAIGHT UP FROM THERE. The aft leg this run used to take at the crossing's own
        # height put it in the front column's east lane at the very depth fluid-21's fall
        # crosses that lane, and the run has the same Y to spend whichever storey it spends it
        # on — so it spends it aloft, where the column is the funnel's floor and nothing else's.
        # THE BAND IS UNDER CARB-1'S, NOT AT THE FUNNEL'S FLOOR. The riser leaves `lane_e` for
        # the meter along the loft and holds its own column aft of that, a `LINE_PITCH` off the
        # stem's; the band this run has is the one between Y-F's crown and that lane, and it
        # stands on the crown because the lane above it is spoken for.
        {"z": y_f.bb.zmax + CLIMB_HUG + 6.35 / 2.0},
        # The step east waits until the run is AFT OF THE RISER'S OWN REACH EAST. carb-1 leaves
        # `lane_e` for the meter on the band ahead of the core, so the two cross wherever this
        # run takes the stem's column forward of it; aft of that band the loft is this run's.
        {"y": f["foam-assembly"].bb.ymin - contents.PUMP_ROW_TURN + LINE_PITCH
              + contents.LLDPE_STOCK_BEND},
        y_g.x("Y-G-1"),                      # east over the aft stand onto the stem's own column
        y_g.y("Y-G-1"),                      # aft the machine's length onto the stem's own lane
        "tee-y-g.Y-G-1",                 # and straight down into the stem
        # THE STRIP OFF P-A-O IS BOUNDED BY THE RUN THAT CROSSES IT, not by a bend radius.
        # fluid-16 falls through the column this stub climbs and closes on the collet at its far
        # end, so the reach here is the bag strip's `BAG_STRIP_REACH` — [6.25](F22_STUB) mm. The
        # climb it hands off to is [42.9](F22_CLIMB) mm and would carry [17.5](F22_STUB_CAP) mm
        # here on its own; the strip is what binds, not the leg.
        kind="fluid", stub=f22_stub, skew=FLAVOR_SKEW,
        note="pump B-channel outlet → Y-G stem: east into the tray-east lane, aft down it "
             "under the inlet's turn, up the front column over the water deck, aft over the "
             "pump and west along the funnel's floor onto the stem's own column"))

    # fluid-19 — the channel-B select to Y-F's BRANCH, which faces WEST out over the aft
    # stand's plates, and one of the two runs that cross between the manifold's two stands. It
    # leaves V-D-O into the front column's aft band on the lane between the row's, comes west
    # onto THE BRANCH'S OWN COLUMN — which stands inside the strip this band has left, between
    # the leg that turns west off V-C-O and the flavor lane — and climbs the front column onto
    # the branch's own plane, which carries it the length of the machine straight into the
    # collet. One column from the band to the branch: the lean and the climb both hold it —
    # the west move rides the climb, one leg carrying both.
    #   A west-facing collet is entered by a leg running east along it, so the crossing rides
    # the branch's own height and the approach owes no corner. That plane stands over the aft
    # stand's crown and under the regulator's floor. Fluid-21 leaves the same tee's fore run
    # port and falls to the deck crossing, so the two hold this column at two heights and
    # never the point.
    yf1, vdo = y_f.at("Y-F-1"), f["selects-tray-assembly"].at("V-D-O")
    #   THE APPROACH COLUMN STANDS BACK BY WHAT ITS OWN CORNER WANTS, not by the stub. This
    # collet is entered along its axis, so the leg that closes on it is the same leg the last
    # turn seats its tangent in — a stock arc's worth with the collet's `JUNCTION_LEG_LEAD`
    # surviving in front. Struck at the stub the run turns four millimetres off the fitting's
    # face and both corners clamp to it. The band west of here is the pair's crown and the
    # trident's two legs are a lane further west again, so this column is free to stand back.
    #   AND IT CLEARS THE HOPPER DRAIN. Fluid-4 falls the spout's own column through this same
    # band, so the column stands back by whichever is further west: what its own corner wants,
    # or a `LINE_PITCH` off that fall.
    yf1_col = min(yf1[0] - contents.JUNCTION_LEG_LEAD - R.stock_min("fluid", y_f.diam("Y-F-1")),
                  f["hopper-funnel"].at("drain")[0] - LINE_PITCH)
    runs.append(R.bent(
        "fluid-19", "selects-tray-assembly.V-D-O",
        (vdo[0], lane_mid, vdo[2]),          # aft into the band, onto the lane between the row's
        (yf1_col, lane_mid, yf1[2]),         # west and up in one lean, onto the branch's plane
        (yf1_col, yf1[1], yf1[2]),           # aft on that plane, over the shelf to the collet's lane
        "tee-y-f.Y-F-1",                     # and east along the collet's own axis into it
        kind="fluid", skew=FLAVOR_SKEW,
        note="channel B select → Y-F branch: leaning west and up out of the aft band onto the "
             "branch's own plane, aft along it over the shelf, and east into the collet "
             "standing out over the aft stand's plates"))

    # fluid-17 — channel A's discharge tee to the nozzle-A gate. Both ends stand in the FRONT
    # COLUMN'S WEST LANE: Y-D's branch faces UP off the lane's own floor, and the gate's inlet
    # faces WEST down the lane from the far end of it. So the run never leaves the lane — it
    # steps east off the tee, climbs the storey, comes aft the length of the lane on the gate's
    # own port plane, and turns east into the collet.
    #
    # THE GATE'S OWN PORT PLANE CARRIES NO LANE THROUGH THE Y-H BAND. Between the tee and the
    # gate the run has to cross the band the bag pair's west flank stands in, and at that height
    # the band is full across the whole corridor: the −X boss chain, then the cap conduit's
    # column falling on `water-in`, then reservoir B's own fill climbing to Y-H, then the
    # trident itself. The conduit's column wants the lane a `LINE_PITCH` EAST of it and Y-H's
    # west flank wants it a turn's clearance WEST — two fences that cross, and a corridor with
    # no width left between them.
    #   SO THE RUN CROSSES OVER Y-H'S CROWN. One tube and its floor over the trident is a
    # stratum nothing else in the band reaches, and the conduit's column is the only body still
    # standing in it — which sets the lane's X on its own, a line's pitch clear of that column.
    # The run comes aft on that stratum and takes its fall in the bay the gate's plate opens on,
    # where the plate itself is the only thing standing.
    vg_stock = R.stock_min("fluid", nz.diam("V-G-I"))
    vg_stub = 7.45                           # the straight Y-D's branch collet takes before it turns
    gate_in = nz.at("V-G-I")
    lane_x = f["foam-assembly"].at("water-in")[0] + LINE_PITCH
    crown_z = f["divider-y-h"].bb.zmax + CLIMB_HUG + 6.35 / 2.0
    runs.append(route(
        "fluid-17", "tee-y-d.Y-D-3",
        {"x": lane_x},                       # east out of the −X boss chain the tee stands
                                             # inside, and onto the one column the conduit's own
                                             # fall leaves open in this corridor
        {"z": crown_z},                      # up the storey and over Y-H's crown, the stratum
                                             # the band's own bodies stop under
        {"y": gate_in[1]},                   # aft along it to the gate's plane
        {"z": gate_in[2]},                   # down into the bay the gate's plate opens on
        "nozzle-tray-assembly.V-G-I",        # and east into the collet, on the collet's own axis
        kind="fluid", skew=FLAVOR_SKEW, stub=(vg_stub, 1.0),
        bend=vg_stock,
        note="Y-D branch → nozzle A gate: east onto the lane the conduit's column leaves, up "
             "and over Y-H's crown, aft to the gate's plane and down into its own bay"))

    # fluid-18 — the nozzle-A gate to its rear bulkhead. V-G-O faces EAST off the turned plate,
    # standing forward of the pump and one lane west of its bulkhead's column, and those three
    # facts are the whole run: east onto that column, up the storey in the open band forward of
    # the pump, and AFT ALONG THE COLUMN INTO THE COLLET.
    #   THE CLOSING LEG IS THE COLLET'S OWN AXIS, so there is no closing corner: the column the
    # run climbs is the bulkhead's own X and the stratum it turns onto is the bulkhead's own Z,
    # and what is left between them is one straight length of tube. The climb's corner has that
    # whole leg to turn on and rises to stock; the corner off the collet turns on the Δx between
    # the gate and the bulkhead, which is the only plan this run owes.
    gate18, tin18 = nz.at("V-G-O"), f["bulkhead-flavor-a"].at("tube-in")
    stock18 = R.stock_min("fluid", nz.diam("V-G-O"))
    runs.append(R.bent(
        "fluid-18", "nozzle-tray-assembly.V-G-O",
        (tin18[0], gate18[1], gate18[2]),    # east onto the bulkhead's own column, on the
                                             # collet's axis, clear of the pump's flank
        (tin18[0], gate18[1], tin18[2]),     # up the storey in the band forward of the pump,
                                             # onto the panel's own stratum
        "bulkhead-flavor-a.tube-in",         # and straight aft into the collet
        kind="fluid", skew=FLAVOR_SKEW, bend=stock18,
        note="nozzle A: gate → rear panel, east onto the bulkhead's column, up the storey "
             "forward of the pump, and one straight run aft into the collet"))

    # fluid-28 — the nozzle-B gate to its rear bulkhead, the line the manifold sends OUT of the
    # machine from the aft stand. It ends on the rear panel's own port row and the vk plate
    # stands in the loft's west lane ahead of it.
    #
    # It leaves AFT into the OUTLET LANE behind the plate (`_contents.aft_outlet_lane`), and
    # the band they turn in is the panel field's own footing: the water bulkhead's body stands
    # on V-J's column from the port row down, and the C14's on V-G's.
    #   So each climbs only as far as the SHELF — the band between the AFT STAND'S OWN CROWN
    # and the lowest body in that field (the header's shelf bullet: the plate's coil row is
    # what runs under these crossings, not the SeaFlo, whose tall half ends forward of them).
    # Each crosses it in ONE LEAN, east and forward together, onto its bulkhead's own column
    # ahead of the body, and climbs the last storey there.
    #   The pair are TWINS and are built as twins: one lane, one shelf level, one approach
    # rule, and the only thing that differs between them is which bulkhead each is aimed at.
    # The two turns behind the plate stand a whole seat pitch apart in X
    # ([19.96](GATE_SEAT_PITCH) mm) and the two leans diverge from there — but the panel's
    # port row is ONE z, so both runs finish on that one stratum and fluid-28's west leg
    # drives clean through fluid-18's aft leg where their columns cross:
    # [175.3](GATE_PAIR_OVERLAP) mm³ of one tube inside the other.
    #   THAT CLASH IS HELD, NOT MISSED. `lines-clear` names it every build and the pack reads
    # NOT BUILD-READY on it. Parting them wants a second level under one of the two, and the
    # routes that buys read worse here than the overlap does; the gate carries the debt until
    # the pair is redrawn. Both come about on the outlet lane's one rung, the deepest
    # the band holds, and water-4's turn is the third station on it.
    #   That lane is struck off the STATED WALL, not the plate's face: the band behind the
    # plate runs one `aft_outlet_lane()` deeper than one lane's own minimum — spare the
    # PLATE cannot pack into (V-J's rim on the corner column, `_contents.bag_b_tray_y`) —
    # and a lane is air, so the rung stands where its tube holds the pack's floor off
    # `REAR_PLANE_Y` and the whole spare rides the three leads that turn on it.
    out_lane = contents.REAR_PLANE_Y - contents.LINE_HUG - 6.35 / 2.0
    # The nozzle-B gate's own climb plane, read back out of the loop: `water-4` crosses the
    # same deck and holds off the band between that collet and this plane.
    nzb_climb_y = None
    for cid, port, panel, who, plate, body in (
        ("fluid-28", "V-J-O", "bulkhead-flavor-b", "nozzle B", nzb, "nozzle-b-tray-assembly"),
    ):
        bh = f[panel]
        # The climb stands as far ahead of the collet as the CLOSING CORNER wants — a stock
        # arc's tangent and the `JUNCTION_LEG_LEAD` the collet itself takes — and comes no
        # further forward than the shelf's own floor allows, which is where the SeaFlo's crown
        # steps back up (`_contents.seaflo_aft_step`, one `PUMP_ROW_TURN` clear of it). The
        # step is the binding one on both columns, and what it leaves is still more than the
        # two leads the approach used to be given.
        #   With the shelf on the stand's own crown the last storey holds two stock arcs on
        # both columns, so nothing here has to be capped under stock any more: the run carries
        # ONE ceiling, its stock's, and every corner but the first rises to it — which leaves
        # the closing arc tangent short of the bulkhead's face rather than on it, and the
        # collet keeps a straight to be pressed onto.
        gate, tin = plate.at(port), bh.at("tube-in")
        gate_stock = R.stock_min("fluid", plate.diam(port))
        # THE PANEL'S OWN STRATUM IS THE CROSSING. Both bulkheads open at one z and every body
        # in the aft-east field stands under it — the boards, the hub, the relay and the stud
        # all crown below the port row — so a run that climbs its whole storey BEFORE it turns
        # aft crosses that field in open air and owes it nothing. The climb is taken in the
        # band each gate already has behind it, and what the run spends after that is its own
        # Δy and Δx and nothing else.
        panel_z = tin[2]
        # A gate with a ROW BEHIND IT climbs in its own bay: the band aft of that row is the far
        # side of it, and a run held at collet height to reach it goes through the plate. A gate
        # with open deck behind it climbs in that deck, between its own plate and the first body
        # of the field.
        def field_front(x0, behind):
            """The forwardmost body of the aft field standing on one column, off placed boxes."""
            ahead = [fr.bb.ymin for fr in f.values()
                     if fr.bb.xmax > x0 - 6.35 / 2.0 and fr.bb.xmin < x0 + 6.35 / 2.0
                     and fr.bb.ymin > behind]
            return min(ahead) if ahead else out_lane

        # The west leg runs at the panel's stratum, and the ASSE CHAIN stands in that stratum
        # across the west end of the field. A leg reaching a bulkhead behind the chain crosses
        # its column, so what that column has to clear is whatever of the chain STANDS ON IT.
        def chain_reach_on(x0):
            """The aftmost ASSE-chain material standing on the column at `x0`, or None.

            Read off the chain's OWN PARTS. The chain is a run of six fittings and its
            bounding box is the one rectangle around all of them: that box's aft face belongs
            to the vent elbow at x[7.04, 23.54], a body clear of every bulkhead column here,
            while what actually stands on this column ends [36](CHAIN_COLUMN_SLACK) mm
            forward of it. A box read here is a reach measured on one fitting and spent on
            another."""
            lo, hi = x0 - 6.35 / 2.0, x0 + 6.35 / 2.0
            on = [b.ymax for b in
                  (s.BoundingBox() for s in
                   contents.packed().solids["asse1022-assembly"].Solids())
                  if b.xmax > lo and b.xmin < hi]
            return max(on) if on else None

        appr_y = tin[1] - gate_stock - contents.JUNCTION_LEG_LEAD
        _chain = chain_reach_on(tin[0])
        if _chain is not None:
            appr_y = max(appr_y, _chain + contents.PUMP_ROW_TURN)
        #   The come-about stands where its OWN CORNER wants it: a square turn at stock spends
        # its radius on the tangent, and the collet's lead is the straight that has to survive
        # in front of that. `_contents.nozzle_tray_y` cuts the band to exactly this sum.
        #   IT STANDS AFT OF THE COLLET AND THE APPROACH STANDS FORWARD OF THE MOUTH, and the
        # two are not the same lane. The collet faces aft and the mouth is entered from ahead,
        # so both the come-about and the closing turn want their tangent in Y — and the band
        # between the two fittings is [15.78](GATE_MOUTH_BAND) mm, which is not two arcs. What
        # the run does instead is take each turn on the side of its own fitting that HAS the
        # room: aft of the collet, in the band the rear plane leaves behind the stand, and
        # forward of the mouth on the chain's own honest lane. The leg between them is the
        # crossing, and it carries the Y move at the field's stratum where nothing stands.
        climb_y = min(aft_turn_lane(gate_stock) if plate is vk
                      else gate[1] + contents.JUNCTION_LEG_LEAD + gate_stock,
                      out_lane)
        # The climb stands on the gate's own column unless the METER stands in it — the run
        # crosses the meter's band at the panel's stratum and the meter's crown reaches into it,
        # so the column steps west of that body before it rises.
        meter_w = f["digiten-flow"].bb.xmin - contents.PUMP_ROW_TURN
        lane_x = min(gate[0], meter_w) if gate[0] + 6.35 / 2.0 > meter_w else gate[0]
        # THE TWO GATES SHARE A STRATUM, AND ON IT THEIR LONG LEGS CROSS. Their columns stand
        # one seat pitch apart ([19.96](GATE_COLUMN_PITCH) mm — closer than a tube), their
        # bulkheads stand a station apart the other way, and the westmost of the two has to
        # cross the whole field AFT of the ASSE chain: so each one's long leg runs through the
        # other's column, and no lane in X parts them. Only height can, and only `crosses_row`
        # buys it — a gate held UNDER the aft row crosses over that row's own crown, one tube
        # and its floor above it, and climbs its last step on its own bulkhead's column where
        # nothing else stands. Neither gate is held under that row, so neither takes the step,
        # both finish on `panel_z`, and the crossing is a real interpenetration the header
        # above states and `lines-clear` fails the pack on every build.
        #   Were the step taken, that stratum would be the AFT ROW'S OWN CROWN: the middle
        # row's gate is the only one of the two with a plate standing between it and the panel,
        # so the row it climbs over is what its crossing height would be for, and everything
        # else in that field — the basin, the backflow chain, the meter's outlet lean — stands
        # clear above or west of the two legs it spends there.
        #   THE CROSSING ANSWERS TO WHAT STANDS IN ITS OWN LANE. A gate held under that row
        # crossed AFT over it; this one crosses FORWARD on the approach lane, and the row's own
        # band stands [141.3](CROSS_ROW_SLACK) mm away from it — so there is nothing to climb
        # under and the crossing takes the panel's stratum whole, on one climb rather than two.
        crosses_row = (nz.bb.ymin - contents.PUMP_ROW_TURN <= appr_y
                       <= nz.bb.ymax + contents.PUMP_ROW_TURN)
        cross_z = (panel_z if plate is nz or not crosses_row
                   else nz.bb.zmax + 2.0 * contents.PUMP_ROW_TURN)
        nzb_climb_y = climb_y
        legs = [(lane_x, climb_y, gate[2]),  # aft off the gate into the outlet lane
                (lane_x, climb_y, cross_z),  # and up the storey there, clear of the field
                (lane_x, appr_y, cross_z)]   # forward onto the approach lane
        if abs(climb_y - appr_y) < 1e-6:     # one lane serves both where the band allows it
            legs = legs[:2]
        legs.append((tin[0], appr_y, cross_z))       # west onto the bulkhead's column
        if cross_z != panel_z:
            legs.append((tin[0], appr_y, panel_z))   # the last step, on that column alone
        runs.append(R.bent(
            cid, f"{body}.{port}", *legs,
            f"{panel}.tube-in",              # and aft into the collet
            kind="fluid", skew=FLAVOR_SKEW, bend=gate_stock,
            note=f"{who}: nozzle gate → rear panel, aft off the collet into the outlet lane, "
                 f"up its whole storey there, forward onto the approach lane and west across "
                 f"the electronics field to the bulkhead's own column"))

    # --- The TAP-WATER PATH: rear bulkhead → ASSE 1022 → split → V-K → SeaFlo → the core's
    # water inlet. Six runs on the water deck and down the front column, at the pigtails'
    # own radius.
    bfp, foam = f["asse1022-assembly"], f["foam-assembly"]

    # water-1 — the rear bulkhead's pigtail to the ASSE inlet. The chain hangs on this
    # station (`_contents.asse_axis`): the bulkhead's collet faces FORWARD and the chain's
    # inlet faces AFT on the same column at the same height, so the two mouths look straight
    # at each other and the pigtail is the tube between them.
    runs.append(route(
        "water-1", "bulkhead-water.tube-in", "asse1022-assembly.tube-in",
        kind="water", stub=0.0,
        note="tap water: rear bulkhead → ASSE 1022 inlet, one straight hop on the "
             "bulkhead's own axis"))

    # water-2 — the ASSE outlet to the split's aft-facing run: two mouths on the sequence's
    # one axis, and the straight between them.
    runs.append(route(
        "water-2", "asse1022-assembly.tube-out",
        "water-split.supply",
        kind="water", skew=FLAVOR_SKEW, stub=(2.0, 2.0),
        note="tap water: ASSE 1022 outlet → split run, straight in on the sequence's own axis"))

    # water-3 — the split's DOWNWARD branch to V-K's forward-facing inlet on the aft stand, and
    # the one run that has to get from the fittings loft to the loft's own port plane. What
    # stands between the two is the whole electronics shelf and the bag-B pair behind it, so the
    # fall is in two parts on either side of them.
    #   The branch runs EAST [25.4](W3_EXIT) mm — one stock radius — before it turns down. A
    # square corner turns on `R` of tangent in each of its two legs, so the exit reach is a
    # CEILING on the exit corner and a reach under stock caps that corner under stock. Here the
    # reach is free: the loft's east lane is open well past this standoff, and the run crosses
    # east anyway, so the millimetres come out of a leg it was already going to travel and only
    # move WHERE the fall happens. Past its own tangent the reach stops binding and the FALL is
    # what bounds the corner — the exit corner and the one at the bottom of the fall share that
    # leg, so each seats [17.34](W3_EXIT_R) mm of it — and the first fall stops on the west
    # column's FIFTH rung — over the loft gap, at the crossing's own y forward of every tray
    # and rail — because this run and fluid-19's fall may not share a stratum: V-K's column
    # stands 7.26 off Y-F's, a pitch short by 0.09, so the rung under fluid-19's crossing
    # belongs to that run's fall and this one crosses ABOVE it, on what its own first fall
    # still seats a stock arc off the split at (31). The run crosses east on that rung onto
    # V-K's own column, holds it the length of the trays, and falls the rest on the far side
    # of them. That column is V-G's as well — both valves take their own row's east seat — and
    # fluid-17 holds it the same length on its way to the gate, so the two runs are parallel
    # over the trays rather than crossing. What parts them is height: fluid-17 rides the band
    # one `PUMP_ROW_TURN` over the stand's crown, and this one stands a whole tube above that,
    # forward of the basin's rails the whole way.
    y_h = f["divider-y-h"]
    y_g = f["tee-y-g"]
    vk_stock = R.stock_min("water", vk.diam("V-K-I"))
    # How far forward of its own collet this fall comes down. THREE floors want that plane and
    # the longest takes it, and a CEILING holds all three. The CLOSING CORNER wants a stock arc
    # with the collet's own lead still standing in front of it. Y-G stands in this bay, and
    # where the fall's column meets the trident in X the fall may not come down inside its band
    # at all: it stops a tube and a floor FORWARD of it, and the aft leg that leaves runs under
    # the trident's floor on the port plane. Where the column stands clear of the trident in X
    # the fitting is beside the fall rather than under it and asks for nothing. And the leg
    # between the crossing and the fall carries a corner at each end, so it seats a stock arc
    # for both only at twice the stock radius; the run holds the split's own Y the whole way
    # across, so that leg is exactly what this backoff leaves of it.
    #   THE CEILING IS THE BAG PAIR'S OWN AFT FACE. This fall comes down in the bay between that
    # plate and V-K's, and a backoff longer than the bay walks it onto the plate's crown. What
    # the bay leaves is what the floors get; where it leaves less than the closing corner wants,
    # the corner takes the bay.
    w3_column_meets_y_g = (y_g.bb.xmin - 6.35 / 2.0 <= vk.at("V-K-I")[0]
                           <= y_g.bb.xmax + 6.35 / 2.0)
    w3_floor = max(vk_stock + contents.JUNCTION_LEG_LEAD,
                   (vk.at("V-K-I")[1] - (y_g.bb.ymin - CLIMB_HUG - 6.35 / 2.0)
                    if w3_column_meets_y_g else 0.0),
                   vk.at("V-K-I")[1] - (sp.at("to-vk")[1] - 2.0 * vk_stock))
    w3_back = min(w3_floor,
                  vk.at("V-K-I")[1] - (bb.bb.ymax + contents.PUMP_ROW_TURN))
    runs.append(route(
        "water-3", "water-split.to-vk",
        {"z": nz.bb.zmax + contents.PUMP_ROW_TURN + 6.35},
                                             # down out of the fittings loft onto the rung over
                                             # fluid-17's, one tube clear of the run it shares
                                             # the east column with
        vk.x("V-K-I"),                       # east across it onto the valve's own column
        vk.y("V-K-I", -w3_back),             # aft down that column onto the plane `w3_back`
                                             # strikes — a square turn's own tangent with the
                                             # collet's lead in front of it, or clear forward of
                                             # Y-G's band, whichever stands further out
        vk.z("V-K-I"),                       # down into the bay onto the stand's port plane
        "vk-tray-assembly.V-K-I",            # and aft into the mouth
        kind="water", skew=FLAVOR_SKEW, stub=(contents.LLDPE_STOCK_BEND, 1.0),
        note="tap water: split branch → V-K inlet, down onto the west column's crown rung, east "
             "across the machine onto the valve's column and down the far side of the trays"))

    # water-4 — V-K's outlet to the suction chain's collet, and TWO GENTLE LEANS is the whole of
    # it. BOTH MOUTHS FACE ALONG Y: the valve discharges AFT, and the chain lying in the slot
    # beside the casting opens FORWARD at it. So the run leaves and enters on ONE AXIS, and
    # everything it has to do in between is an OFFSET — [30.1](W4_DX) mm west onto the slot's
    # column and [44.3](W4_DZ) mm up onto its plane, taken across [32.6](W4_DY) mm of Y.
    #   AN OFFSET IS NOT A CORNER, and that is the whole economy of it. A square turn spends its
    # entire radius as tangent in each of the two legs it sits in; a [70](W4_TURN1)° and a
    # [70](W4_TURN2)° lean spend `R·tan(θ/2)`, under HALF of it — so both corners seat a
    # WHOLE [25.4](W4_R) mm ARC on a run only [67.4](W4_LEN) mm long, [1.08](W4_SPRAWL)× the
    # [62.7](W4_SPAN) mm span it crosses.
    #   THE MOUTH IS WHAT MOVED. Run onto `seaflo-pump.suction` — the 3/8" barb moulded into
    # the head casting — the two ends stood 34.2 mm apart and NINETY DEGREES apart, and no
    # all-stock path across that span is anything but a coil: an R25.4 corner spends its whole
    # radius as tangent in each leg it touches, and four of them want more straight than 34 mm
    # holds anywhere in it. The chain is what takes the 3/8" off that barb, and how its collet
    # lies is ours to choose; laid along Y it faces this run square on.
    W4_LEAN = ((124.40, 362.08, 273.41),    # off the collet, barely leaning out of its own axis
               (102.37, 360.88, 306.74))    # onto the slot's column and plane, square on the
                                            # mouth it closes on
    runs.append(R.bent(
        "water-4", "vk-tray-assembly.V-K-O", *W4_LEAN, "suction-chain.tube-port",
        kind="water", skew=FLAVOR_SKEW, bend=R.stock_min("water", vk.diam("V-K-O")),
        note="tap water: V-K outlet → suction chain's collet, one leaning offset west and up "
             "into the slot beside the casting, both corners at R25.4"))

    # water-6 — the 3/8" braided stub off the molded discharge barb. The barb points WEST
    # at the wall; the hose comes about in the pocket between them on its own radius and
    # climbs the pump's west flank, closing forward and up onto the chain's barb, which
    # stands over the discharge's own column for exactly this leg.
    #   THE APPROACH IS FENCED AND THE EXIT IS NOT. The pocket the exit turns in runs from the
    # −X wall's inner face at x [-14](W6_WALL_X) out to the barb tip at x [9](W6_BARB_X), and
    # the hose's own half-section and one clearance floor leave [14.45](W6_POCKET_FREE) mm of
    # it before a sweep touches the piece — more than this reach spends, so the sweep stands
    # [8.16](W6_WALL_CLEAR) mm off that wall built. The approach is the COLLET'S OWN LEAD and
    # no more — the basin stands aft of this barb at exactly that reach (`_contents` hangs its
    # front wall off this station), so a closing straight longer than the lead is a straight
    # drawn inside the basin.
    #   What is left is the DIRECTION of each. This hose is CLAMPED ONTO A BARB, so the straight
    # a joint needs is the barb itself and lies upstream of this run's first point — the route
    # owes none of its own, and every millimetre of both reaches goes to the corner. `lean_into`
    # spends the [14](W6_SKEW)° a braided stub takes at each end: [9.09](W6_LEAN_OUT)° off the
    # discharge and [14](W6_LEAN_IN)° off the chain's barb, bringing both turns back from past
    # square to [92.4](W6_TURN_OUT)° and [85.6](W6_TURN_IN)°.
    w6_lead = (9.0, contents.JUNCTION_LEG_LEAD)
    (w1, w2), w6_lean, w6_r, _w6_turns = lean_into(
        *_mouth(f, "seaflo-pump.discharge"), *_mouth(f, "discharge-chain.barb-tip"),
        w6_lead, radius=HOSE_BEND, straight=0.0, skew=14.0)
    runs.append(R.bent(
        "water-6", "seaflo-pump.discharge", w1, w2, "discharge-chain.barb-tip",
        kind="water", bend=w6_r, skew=14.0,
        note=f"carb water: SeaFlo discharge barb → discharge chain, one leaning sweep in the "
             f"wall pocket on reaches leaning {w6_lean[0]:.1f}°/{w6_lean[1]:.1f}° into it "
             f"(3/8\" braided PVC, two clamps)"))

    # water-7 — the 3/8" braided stub off the molded suction barb, the discharge stub's opposite
    # number and the last 3/8" on this side. BOTH OF ITS ENDS FACE THE SAME WAY DOWN THE MACHINE
    # and the chain is the one ahead: the barb opens EAST at y [333.4](W7_PUMP_Y) and the chain's
    # own barb, [98.8](W7_REACH) mm aft of it, opens AFT too. A barb facing aft is fed from
    # BEHIND, so the hose has to get past the fitting it closes on and come back forward onto it.
    #   SO THE RUN GOES UNDER THE CHAIN AND LOOPS UP BEHIND IT. It turns aft off the pump's barb
    # and runs the length of the slot on the barb's own storey, one turnover BELOW the chain
    # lying above it, and takes its loop in the [39.8](W7_REAR_ROOM) mm the rear plane leaves
    # behind the chain's mouth — which is where the room is, because the slot itself is
    # [17](W7_SLOT) mm wide and holds the chain and nothing beside it.
    #   These three points hold R[15.9](W7_R) — the reinforced PVC's own minimum, which its twin
    # on the discharge side does not reach — at every corner, leave the barb and enter the
    # chain's inside [14](W7_SKEW)°, and clear every placed body and every other run. They are
    # solved against those conditions, so a body moving near them moves what they should be.
    W7_LOOP = ((104.13, 336.57, 283.64),    # east off the barb and turning aft onto its storey
               (87.41, 414.80, 264.70),     # aft the length of the slot, under the chain above
               (100.42, 464.45, 304.96))    # up in the room behind the chain's mouth, and back
                                            # forward onto it
    runs.append(R.bent(
        "water-7", "seaflo-pump.suction", *W7_LOOP, "suction-chain.barb-tip",
        kind="water", bend=HOSE_BEND, skew=14.0,
        note="carb water: SeaFlo suction barb → suction chain, aft under the chain on the "
             "barb's own storey and up behind it, every corner at R15.9 (3/8\" braided PVC, "
             "two clamps)"))

    # water-5 — the chain's forward collet to the core's water inlet, and the tap-water path's
    # one fall. TWO LEGS AND ONE CORNER. The chain hands the water over on the deck's own west
    # end, facing FORWARD, and `_cold_core_interface.cap_conduits` stands the inlet's bore
    # ahead of it on very nearly that column — so the run is one horizontal leg out to the
    # bore's own station and one fall straight down it, and the corner between them has a
    # [30](W5_LEG) mm leg on one side and the whole [81.5](W5_FALL) mm of the fall on the
    # other. Both hold a stock arc, which is what this line turns at.
    #   The horizontal leg carries the whole plan move, so it leaves the collet
    # [0.955](W5_LEAN)° off its axis — inside the `FLAVOR_SKEW` a push-to-connect takes — and
    # the fall enters the bore dead on the vertical it is drilled at. Nothing stands under the
    # leg: the deck's west end carries reservoir B's own riser [7.42](W5_RISER_GAP) mm off this
    # bore, and the bag pair closes the band east of both.
    chain = f["discharge-chain"]
    runs.append(R.bent(
        "water-5", "discharge-chain.tube-port",
        (foam.at("water-in")[0], foam.at("water-in")[1], chain.at("tube-port")[2]),
                                             # out to the bore's own station, holding the deck's
                                             # height the whole way
        "foam-assembly.water-in",            # and one fall straight down the bore
        kind="water", skew=FLAVOR_SKEW, lead=(0.0, 0.0),
        note="carb water: discharge chain → cold-core water inlet, one leg out to the conduit's "
             "own station and one fall down it"))

    # --- The CO2 path: the front-wall chain to the core's CO2 bore. The check is made up
    # on the DERPIPE's stub and carries no line, so the path is one short hop and one long
    # run past the regulator.
    reg110 = f["wr1110"]

    # co2-1 — the check's stub to the regulator's inlet: the two mouths face each other
    # down the chain's own axis, one straight hop of tube between the adapters.
    runs.append(route(
        "co2-1", "gasher-co2.outlet", "wr1110.inlet",
        kind="co2", bend=CBEND, stub=0.0,
        note="CO2: check outlet → WR1110 inlet, one straight hop on the chain's axis"))

    # co2-2 — the regulator's outlet to the core's CO2 bore, all inside the corridor. Out
    # west off the chain's axis, then one lean — the climb to the bore's level and the aft
    # step onto the corridor lane share a leg — and east along the corridor over the chain
    # to close aft into the bore. The lane stands one stock radius ahead of the bore's face,
    # so the aft lead IS that radius and the corner into the close turns at stock. The lean
    # is the only leg its own two corners have, and the chain's Z is what sizes it
    # (`_contents.CO2_INLET_Z`): the axis stands far enough under the bore that
    # √(Δy² + Δz²) seats a stock tangent at each end, so all three corners turn at stock.
    # The out-lead is the west tangent's own length with straight left over; the corridor
    # west of the body is empty to the wall.
    co2_stock = R.stock_min("co2", reg110.diam("outlet"))
    co2_lead = co2_stock + 2.6                       # the west tangent, and straight past it
    runs.append(R.bent(
        "co2-2", "wr1110.outlet",
        (reg110.at("outlet")[0] - co2_lead,
         foam.at("co2-in")[1] - co2_stock,
         foam.at("co2-in")[2]),
                                             # the lean's far end: on the lane, at the bore's level,
                                             # on the out-lead's own column so the turn stays square
        "foam-assembly.co2-in",              # east over the chain, and aft into the bore
        kind="co2", skew=FLAVOR_SKEW, lead=(co2_lead, co2_stock),
        note="CO2: WR1110 outlet → cold-core CO2 bore, one stock lean up-and-aft then east "
             "along the corridor over its own chain"))

    # --- The carb-water riser: the core's bottom-plate outlet to the blue-ringed rear
    # bulkhead, with the DIGITEN meter inline where the riser crosses the loft.
    meter, b_carb = f["digiten-flow"], f["bulkhead-carb"]

    # carb-1 — the core's outlet up to the meter, and the one run that crosses the machine
    # in X twice. Forward into the aft band, west onto the riser column, up the machine,
    # east over the condenser's crown, and up again into the meter's forward collet. Both
    # crossings are the block's: the condenser fills the whole front column east of the
    # riser between its own stratum and its crown, so the climb cannot start under the
    # meter, and the loft's east pocket the meter stands in cannot be reached until the
    # climb is over that crown. The eastward leg lies in the window between the crown and
    # pump A's two loft lines, the only band at this depth carrying nothing.
    #   That leg is [19.17](CARB_WINDOW_LEG) mm — one corner short of two stock arcs — so the
    # corner it hands the meter's column is capped at what the leg leaves a stock turn at
    # the riser's crown ([9.59](CARB_JOG_CAP)), and the last climb splits its own storey
    # with it: the crown corner turns at stock, and the jog's remainder rides the two
    # corners the window holds under it either way.
    # THE RISER STANDS ON THE CONDENSER'S OWN FLANK. What sends this run west is the block, so
    # the block's west face is how far west it has to go — and every millimetre past that is
    # spent twice, once each way, through the one column the loft's own lines all cross. Struck
    # there, the riser is EAST of Y-F's column and of the stem lane fluid-22 holds, so it climbs
    # the whole storey in a band it shares with nothing and arrives at the meter's own plane
    # with only the reach east of it left.
    riser_x = lane_e
    band_y_carb = foam.bb.ymin - contents.PUMP_ROW_TURN
    stock = R.stock_min("water", foam.diam("carb-water-out"))
    runs.append(route(
        "carb-1", "foam-assembly.carb-water-out",
        {"y": band_y_carb},                  # forward into the aft band, behind the tray-east climb
        {"x": riser_x},                      # west onto the riser column, clear of the block
        meter.z("inlet"),                    # up the whole storey onto the meter's own plane
        meter.x("inlet"),                    # east over the block's crown into the loft's pocket
        "digiten-flow.inlet",                # and aft into the meter
        kind="water", skew=FLAVOR_SKEW, stub=(1.0, 4.0), bend=stock,
        note="carb riser: cold-core outlet → DIGITEN inlet, up the riser column on the "
             "condenser's flank and east over its crown onto the meter's own plane"))

    # carb-2 — the meter's outlet to the rear bulkhead, one straight lean. Squared, the jog
    # west onto the bulkhead's column and the climb to the row each take a corner pair, and
    # the jog is the shortest leg in the run — so every corner seats the jog and nothing
    # more. Leaned, the jog and the climb share one leg between the two on-axis leads, and
    # the two corners seat what the aft budget between the ports holds.
    #   THE LEADS PAY FOR THEMSELVES ONLY SO FAR. Both are one stock radius, which is every
    # millimetre this run can spend on them: the aft budget is fixed, so each millimetre of
    # lead comes out of the lean's own y and STEEPENS it, and a steeper lean turns through a
    # wider angle at each end — which asks `R·tan(θ/2)` back faster than the lead grows. The
    # two corners climb to [23.4](CARB2_R) mm against a stock R25.4 and stop there; past this
    # reach the angle takes more than the lead gives and the corners come back down.
    runs.append(R.bent(
        "carb-2", "digiten-flow.outlet",
        "bulkhead-carb.tube-in",
        kind="water", skew=FLAVOR_SKEW,
        lead=(contents.LLDPE_STOCK_BEND, contents.LLDPE_STOCK_BEND),
        note="carb riser: DIGITEN outlet → rear bulkhead, one lean west and up between "
             "the on-axis leads"))

    # --- The REFRIGERANT LOOP: three legs of 1/4" ACR copper at the bender's radius.
    # The corridor's floor and the tray-east lane carry all three; every leg is 25.4 mm
    # or longer between corners.

    # refrig-1 — hot gas, the shroud's east stub to the condenser's crown, up the EAST WALL
    # LANE: the strip between the block's east face and the side wall, the one column in
    # this machine that runs floor to loft carrying nothing else. Aft off the stub into the
    # corridor, east along it over the CO2 chain, up the lane the block's whole height,
    # then west over its crown and down into the inlet.
    #   The lane matters because the copper is rigid and the alternatives are not lanes at
    # all: west of the block the front column is the flavor manifold's, and the trays, the
    # tees and their runs leave nothing straight through it for a 1/4" leg at this radius.
    runs.append(route(
        "refrig-1", "compressor-shroud.refrig-discharge",
        {"y": 146.0},                        # aft into the corridor's own band
        {"x": 186.5},                        # east along it, over the CO2 chain
        {"z": 330.0},                        # up the east wall lane, past the block
        cond.x("refrig-inlet"),              # west over the block's crown
        "condenser+fan.refrig-inlet",        # and down into the inlet
        kind="refrigerant", stub=(0.0, 5.0),
        note="hot gas: compressor → condenser crown, up the east wall lane"))

    # refrig-2 — the liquid line (the drier + cap tube ride this leg). Off the intake face
    # into the tray-east lane, down it between the pack's own climbs, and east along the
    # corridor at the evaporator inlet's stratum to close aft into the core.
    runs.append(route(
        "refrig-2", "condenser+fan.refrig-outlet",
        {"x": 110.0},                        # west into the tray-east lane
        foam.z("evap-inlet"),                # down it to the inlet's stratum
        foam.x("evap-inlet"),                # east along the corridor
        "foam-assembly.evap-inlet",          # and aft into the port
        kind="refrigerant", stub=(0.0, 6.5),
        note="liquid: condenser (drier + cap tube) → evaporator, down the tray-east lane"))

    # refrig-3 — the suction leg home. Forward into the corridor's band, up over the floor
    # traffic, west under the condenser's floor the width of the machine, and down onto
    # the shroud's west stub to close forward into it.
    runs.append(route(
        "refrig-3", "foam-assembly.evap-outlet",
        {"y": 153.6},                        # forward into the corridor's band
        {"z": 113.5},                        # up, over the corridor's floor traffic
        shroud.x("refrig-suction"),          # west under the condenser's floor
        shroud.z("refrig-suction"),          # down onto the stub's plane
        "compressor-shroud.refrig-suction",  # and forward into it
        kind="refrigerant", stub=(6.0, 6.0),
        note="suction: evaporator → compressor, the corridor's own width at one level"))

    return runs


def build() -> dict:
    """The runs as placed solids: {name: (solid, color)} — copper for the refrigerant loop,
    white LLDPE for the fluid (flavor) and tap-water runs."""
    return {r.id: (R.tube(r), COPPER if r.kind == "refrigerant" else LLDPE) for r in build_runs()}


def _shelf(solids: dict) -> list:
    """The bodies standing on the foam cap, named by what holds them there."""
    import scorecard

    return [c.name for c in scorecard.COMPONENTS if c.held == "cap" and c.name in solids]


def _shelf_top_under(solids: dict, run) -> float:
    """The tallest lid the shelf crossing passes OVER — the cap's modules whose footprint the
    crossing leg's own column crosses, and not the ones standing beside it. The psu is taller
    than anything the crossing meets and stands a lane west of it, so a figure read off the whole
    shelf would report a standoff this run does not have.

    The shelf stands AFT of this crossing now, so the leg may pass over no module at all — then
    what it stands over is the cap's own lid face, and that is what the standoff is measured
    against."""
    z0 = max(p[2] for p in run.pts)
    legs = [(a, b) for a, b in zip(run.pts, run.pts[1:])
            if abs(a[2] - z0) < 1e-6 and abs(b[2] - z0) < 1e-6]
    r = run.diam / 2.0
    tops = []
    for n in _shelf(solids):
        bb = _boxes.boxed(solids[n])
        for a, b in legs:
            xlo, xhi = sorted((a[0], b[0]))
            ylo, yhi = sorted((a[1], b[1]))
            if (xlo - r <= bb.xmax and xhi + r >= bb.xmin
                    and ylo - r <= bb.ymax and yhi + r >= bb.ymin):
                tops.append(bb.zmax)
                break
    return max(tops, default=contents.foam_cap_top())


def _shelf_gap(solids: dict) -> float:
    """The widest lane the cap's own modules leave between them: their X footprints merged, and
    the widest space between two neighbouring runs of that merge."""
    spans = sorted((_boxes.boxed(solids[n]).xmin, _boxes.boxed(solids[n]).xmax)
                   for n in _shelf(solids))
    widest, reach = 0.0, spans[0][1]
    for lo, hi in spans[1:]:
        widest = max(widest, lo - reach)
        reach = max(reach, hi)
    return widest


def lane_stations() -> dict:
    """The stations the authored runs actually swept, for the [value](NAME) markers in the prose
    above — so a number a corridor is described by is the number a tube was built along, not a
    second hand-kept copy of it. `enclosure_assembly` feeds these to docgen."""
    import scorecard

    runs = {r.id: r for r in build_runs()}
    f4, f15 = runs["fluid-4"], runs["fluid-15"]
    solids = {n: s for n, (s, _c) in {**contents.build(), **contents.panel_bodies()}.items()}
    span = 2.0 * contents.DIVIDER_OUTLET_X
    # The two straight legs, off the runs themselves: how far off its collet's own axis each
    # leaves. `leg_skew` against the port's own normal is the lean by definition, so the figure
    # in the prose is the one the reach was struck on and not a second copy of it.
    f24, f16 = runs["fluid-24"], runs["fluid-16"]
    fr = _frames()
    yh_lean = R.leg_skew(f24.pts[0], f24.pts[1],
                         fr["bag-b-tray-assembly"].normal("V-I-O"))
    return {
        "SRC_PORT_Z":       f"{f4.pts[-1][2]:.4g}",
        "HOPPER_FALL":      f"{f4.pts[0][2] - f4.pts[1][2]:.4g}",
        # The geometry the loft divider's two legs share.
        "DIVIDER_SPAN":     f"{span:.4g}",
        "SEAT_PITCH":       f"{contents._tray.pitch:.4g}",
        "LEG_LEAN":         f"{(contents._tray.pitch - span) / 2.0:.4g}",
        # Y-H's two legs: the lean the straight between each pair of mouths leaves them at.
        "YH_LEG_LEAN":      f"{yh_lean:.3g}",
        # The bag strip: how far apart in x the two mouths that face down it stand, and the
        # closest the two runs that cross it ever come — off the swept tubes, not the
        # centrelines, which is the reading `lines-clear` answers.
        "STRIP_OFFSET":     f"{abs(f16.pts[-1][0] - runs['fluid-22'].pts[0][0]):.3g}",
        "STRIP_SEP":        f"{scorecard._solid_gap(R.tube(f16), R.tube(runs['fluid-22'])):.3g}",
        # fluid-22's stub off the barb, the climb it hands off to, and what that climb has left
        # for this corner once its far one has taken a stock arc.
        "F22_STUB":         f"{math.dist(runs['fluid-22'].pts[0], runs['fluid-22'].pts[1]):.3g}",
        "F22_CLIMB":        f"{math.dist(runs['fluid-22'].pts[1], runs['fluid-22'].pts[2]):.3g}",
        "F22_STUB_CAP":     f"{math.dist(runs['fluid-22'].pts[1], runs['fluid-22'].pts[2]) - contents.LLDPE_STOCK_BEND:.3g}",
        # fluid-23's exit lead, the deck east of its collet that water-3's fall leaves it, and
        # how far west of that collet the outlet it feeds stands.
        "F23_EAST_AIR":     f"{_frames()['vk-tray-assembly'].at('V-K-I')[0] - runs['fluid-23'].pts[0][0]:.3g}",
        "F23_BACKTRACK":    f"{runs['fluid-23'].pts[0][0] - runs['fluid-23'].pts[-1][0]:.3g}",
        # The strip the bag-A junction stands across: the pump row's aft face to that pair's own
        # forward collets, off the placed pump rather than off the number its seat was built from.
        "BAG_STRIP":        f"{contents.bag_a_tray_port('V-F-O')[0][1] - _boxes.boxed(solids['pump-a']).ymax:.4g}",
        # The manifold's junction: the storey its four column legs cross, the plane they land
        # on, and what the two tees cost — how far each column stands off its own seat, and the
        # tube the crossbar is left with. Both off the built runs: the legs' own two ends, and
        # the crossbar's own length.
        "STACK_PITCH":      f"{runs['fluid-3'].pts[0][2] - runs['fluid-7'].pts[-1][2]:.4g}",
        "SEL_PORT_Z":       f"{runs['fluid-7'].pts[-1][2]:.4g}",
        "COLUMN_SPREAD":    f"{abs(runs['fluid-3'].pts[-1][0] - runs['fluid-3'].pts[0][0]):.4g}",
        "CROSSBAR":         f"{runs['fluid-6'].length:.4g}",
        # The bag line's ends and the two bands it crosses in.
        "BAG_PORT_Z":       f"{f15.pts[0][2]:.4g}",
        "BAG_PORT_X":       f"{f15.pts[0][0]:.4g}",
        "CONDENSER_FLOOR":  f"{_boxes.boxed(solids['condenser+fan']).zmin:.4g}",
        "CORRIDOR_DEPTH":   f"{contents.MACHINE_CORRIDOR:.4g}",
        "TRAY_EAST_LANE":   f"{_boxes.boxed(solids['condenser+fan']).xmin - _boxes.boxed(solids['bag-a-tray-assembly']).xmax:.4g}",
        # The head column's aft margin, off the same two faces the prose names it by: the plate's
        # own aft edge, and the plane the placed body's collets end on.
        "COLLET_PROUD":     f"{_boxes.boxed(solids['bag-a-tray-assembly']).ymax - (contents.bag_a_tray_pos()[1] + contents._tray.half_y):.4g}",
        # What the loft tee stands off the plates it sits over: its own body underside to the
        # aft stand's crown, off the placed fitting rather than off the term that positioned it.
        "LOFT_TEE_STANDOFF": f"{_boxes.boxed(solids['tee-y-f']).zmin - contents.aft_stand_crown():.4g}",
        # And what closes the column over it — the hopper's floor to that same body's crown.
        # It is the reading that lays Y-F's branch west instead of up (`_contents.TEE_TURNS`).
        "LOFT_TEE_HEADROOM": f"{_boxes.boxed(contents.placed_funnel()).zmin - _boxes.boxed(solids['tee-y-f']).zmax:.2g}",
        # The loft's own two ends: the deck reservoir B's riser reaches it on, and the plane the
        # loft's trays present every one of their eight collets on. The bay between them is
        # read off the two run legs Y-G's own fitting passes through.
        "BAG_B_DECK_Z":     f"{runs['fluid-25'].pts[0][2]:.4g}",
        "LOFT_PORT_Z":      f"{runs['fluid-25'].pts[-1][2]:.4g}",
        # Reservoir B's last two legs, and what prices the corner between them: the plan the
        # lean carries, the band the PSU's crown leaves under the stem's plane, and what a stock
        # arc has drifted sideways by the time it has climbed clear of that band.
        "BAG_B_CROSS":      f"{abs(runs['fluid-25'].pts[-1][0] - runs['fluid-25'].pts[0][0]):.4g}",
        # fluid-25's two mouths, the shell plane its approach reaches west to, and what the two
        # bodies nearest that plane leave it. The lean and the turn are off the built run.
        # The approach runs OUTWARD from the collet to its waypoint, so the lean is measured
        # against the port's own outward normal — negated, it reads the supplement.
        "F25_LEAN":         f"{R.leg_skew(runs['fluid-25'].pts[-1], runs['fluid-25'].pts[-2], _frames()['divider-y-h'].normal('Y-H-2')):.3g}",
        "F25_TURN":         f"{runs['fluid-25'].bends[-1][1]:.3g}",
        # water-6's two leans and the turns they leave, off the built run. A braided stub takes
        # more off its barb's axis than a rigid line does off a collet's.
        "W6_SKEW":          "14",
        "W6_LEAN_OUT":      f"{R.leg_skew(runs['water-6'].pts[0], runs['water-6'].pts[1], _frames()['seaflo-pump'].normal('discharge')):.3g}",
        "W6_LEAN_IN":       f"{R.leg_skew(runs['water-6'].pts[-1], runs['water-6'].pts[-2], _frames()['discharge-chain'].normal('barb-tip')):.3g}",
        "W6_TURN_OUT":      f"{runs['water-6'].bends[0][1]:.3g}",
        "W6_TURN_IN":       f"{runs['water-6'].bends[-1][1]:.3g}",
        # The pocket that reach turns in, off the two faces that bound it — the −X wall stands
        # one rib inset outboard of the core's west face — and what it leaves once the hose's
        # own half-section and one clearance floor are off it, against what the built sweep
        # actually keeps to that wall.
        "W6_BARB_X":        f"{runs['water-6'].pts[0][0]:.3g}",
        "W6_WALL_X":        f"{contents.CORE_WEST_FACE - contents.SIDE_RIB_INSET:.3g}",
        "W6_POCKET_FREE":   f"{runs['water-6'].pts[0][0] - (contents.CORE_WEST_FACE - contents.SIDE_RIB_INSET) - runs['water-6'].diam / 2.0 - contents.LINE_HUG:.4g}",
        "W6_WALL_CLEAR":    f"{_boxes.boxed(R.tube(runs['water-6'])).xmin - (contents.CORE_WEST_FACE - contents.SIDE_RIB_INSET):.3g}",
        "LOFT_BAY":         f"{runs['fluid-27'].pts[0][1] - runs['fluid-23'].pts[0][1]:.4g}",
        "PORT_ROW_Z":       f"{runs['fluid-18'].pts[-1][2]:.4g}",
        # The outlet lane: what the band has spare once its one rung is struck, the pitch the
        # three turns on it stand apart, and how much of one twin gate's tube is inside the
        # other's. OVERLAP, not gap: `_solid_gap` reads 0 for a graze and 0 for a run driving
        # clean through, so on this pair the gap is the one number that cannot tell the
        # difference — and this pair drives through. Zero here means parted.
        "OUTLET_LANE":      f"{contents.aft_outlet_lane():.3g}",
        "GATE_SEAT_PITCH":  f"{abs(runs['fluid-18'].pts[1][0] - runs['fluid-28'].pts[1][0]):.4g}",
        # The two gates' own columns, at that same pitch.
        "GATE_COLUMN_PITCH": f"{abs(runs['fluid-18'].pts[1][0] - runs['fluid-28'].pts[1][0]):.4g}",
        "GATE_PAIR_OVERLAP": f"{scorecard._common_volume(R.tube(runs['fluid-18']), R.tube(runs['fluid-28'])):.4g}",
        # The shelf, off the two bodies that actually bound it: the aft stand's coil crown
        # under it and the lowest body of the port field over it. The SeaFlo does not bound
        # it — its tall half ends forward of every crossing up here — and `seaflo_aft_step`
        # reads where that ends off the placed casting rather than off a typed station.
        "PANEL_SHELF":      f"{_boxes.boxed(solids['c14-inlet']).zmin - _boxes.boxed(solids['nozzle-tray-assembly']).zmax:.4g}",
        "STAND_CROWN":      f"{_boxes.boxed(solids['nozzle-tray-assembly']).zmax:.4g}",
        "SHELF_OVERSHOOT":  f"{_boxes.boxed(solids['seaflo-pump']).zmax - _boxes.boxed(solids['nozzle-tray-assembly']).zmax:.3g}",
        "SEAFLO_STEP_Y":    f"{contents.seaflo_aft_step()[0]:.4g}",
        "SEAFLO_AFT_CROWN": f"{contents.seaflo_aft_step()[1]:.4g}",
        # water-4's span and centreline, the OFFSET it is really made of — both its mouths face
        # along Y, so what the run does is move sideways, not turn — and the two leans that
        # offset costs. Neither is near square, which is why both seat a whole stock arc.
        "W4_SPAN":          f"{math.dist(runs['water-4'].pts[0], runs['water-4'].pts[-1]):.3g}",
        "W4_LEN":           f"{runs['water-4'].length:.3g}",
        "W4_R":             f"{runs['water-4'].tightest:.4g}",
        "W4_DX":            f"{abs(runs['water-4'].pts[-1][0] - runs['water-4'].pts[0][0]):.3g}",
        "W4_DY":            f"{runs['water-4'].pts[-1][1] - runs['water-4'].pts[0][1]:.3g}",
        "W4_DZ":            f"{runs['water-4'].pts[-1][2] - runs['water-4'].pts[0][2]:.3g}",
        "W4_TURN1":         f"{runs['water-4'].bends[0][1]:.2g}",
        "W4_TURN2":         f"{runs['water-4'].bends[1][1]:.2g}",
        "W4_SPRAWL":        f"{runs['water-4'].length / math.dist(runs['water-4'].pts[0], runs['water-4'].pts[-1]):.3g}",
        # The suction stub: the plane its barb opens on, how far aft the chain's own barb stands
        # from it, the room the rear plane leaves behind that mouth for the loop, and the slot
        # the run passes under — which holds the chain and has nothing beside it.
        "W7_SKEW":          "14",
        "W7_R":             f"{runs['water-7'].tightest:.3g}",
        "W7_PUMP_Y":        f"{runs['water-7'].pts[0][1]:.4g}",
        "W7_REACH":         f"{runs['water-7'].pts[-1][1] - runs['water-7'].pts[0][1]:.3g}",
        "W7_REAR_ROOM":     f"{contents.REAR_PLANE_Y - runs['water-7'].pts[-1][1]:.3g}",
        "W7_SLOT":          f"{_boxes.boxed(solids['suction-chain']).xmax - _boxes.boxed(solids['suction-chain']).xmin:.3g}",
        # The suction chain's own three clearances, for the pose that states them: what it
        # leaves the casting and the aft row MEASURED AGAINST SOLIDS — both of those columns
        # read closed off the bounding boxes and both boxes are wrong about it — and the room
        # its barb leaves the rear plane, which is what the stub's loop is taken in.
        "SUCT_PUMP_GAP":    f"{scorecard._solid_gap(solids['suction-chain'], solids['seaflo-pump']):.3g}",
        "SUCT_ROW_GAP":     f"{scorecard._solid_gap(solids['suction-chain'], solids['nozzle-b-tray-assembly']):.3g}",
        "SUCT_REAR_ROOM":   f"{contents.REAR_PLANE_Y - _boxes.boxed(solids['suction-chain']).ymax:.4g}",
        # fluid-27's turn: the leg its own corner and the collet's lead cost off the gate, which
        # is what places it, and what the tube keeps off the PSU's casting there — measured
        # against the SWEPT SOLID and the casting itself, because the square corner the run is
        # authored on is not where the tube stands and the brick's box is not where its metal is.
        "F27_LEG":          f"{_frames()['nozzle-b-tray-assembly'].at('V-J-I')[1] - runs['fluid-27'].pts[1][1]:.3g}",
        "F27_TANGENT":      f"{runs['fluid-27'].radii[1]:.3g}",
        "F23_IN_REACH":     f"{_frames()['tee-y-g'].at('Y-G-3')[1] - (_boxes.boxed(solids['bag-b-tray-assembly']).ymax + contents.PUMP_ROW_TURN):.3g}",
        "F27_PSU_CLEAR":    f"{scorecard._solid_gap(R.tube(runs['fluid-27']), solids['psu']):.3g}",
        # The nozzle-B gate's own three fences, each one a figure a BOUNDING BOX got wrong.
        # The band its collet and its mouth leave between them, which is not two stock arcs;
        # how far forward of the chain's box the chain's own material on that column stops;
        # and how far the crossing now runs from the row its height was once held under.
        "GATE_MOUTH_BAND":  f"{runs['fluid-28'].pts[-1][1] - runs['fluid-28'].pts[0][1]:.4g}",
        "CHAIN_COLUMN_SLACK": f"{_boxes.boxed(solids['asse1022-assembly']).ymax - max(b.ymax for b in (s.BoundingBox() for s in solids['asse1022-assembly'].Solids()) if b.xmax > runs['fluid-28'].pts[-1][0] - 6.35 / 2.0 and b.xmin < runs['fluid-28'].pts[-1][0] + 6.35 / 2.0):.3g}",
        "CROSS_ROW_SLACK":  f"{runs['fluid-28'].pts[-2][1] - _boxes.boxed(solids['nozzle-tray-assembly']).ymax:.4g}",
        # water-3's exit reach off the split, and what its exit corner seats on it. The corner
        # is the FALL's to bound once the reach clears its own tangent, so the two figures part
        # company at the point the standoff stops being the binding one.
        "W3_EXIT":          f"{math.dist(runs['water-3'].pts[0], runs['water-3'].pts[1]):.3g}",
        "W3_EXIT_R":        f"{runs['water-3'].radii[1]:.4g}",
        # carb-2's corners against the lean they are struck on, and fluid-13's approach — the
        # two other reaches on this pack that a corner, not a body, is what spends.
        "CARB2_R":          f"{runs['carb-2'].tightest:.3g}",
        "F13_APPROACH":     f"{math.dist(runs['fluid-13'].pts[-1], runs['fluid-13'].pts[-2]):.3g}",
        # The band over Y-G's crown that fluid-22's fall is taken in, off the two bodies that
        # bound it: the trident's own crown and the hopper's floor.
        "YG_COLUMN":        f"{_boxes.boxed(contents.placed_funnel()).zmin - _boxes.boxed(solids['tee-y-g']).zmax:.3g}",
        # water-5's fall, and the two figures the casting sets it: the slot its head leaves
        # over the conduit's own column, and the window between the bag pair and its front face.
        # water-5's two legs, the lean the horizontal one leaves its collet on, and what the
        # deck's own west end leaves between this bore and reservoir B's riser.
        "W5_LEG":           f"{math.dist(runs['water-5'].pts[0], runs['water-5'].pts[1]):.3g}",
        "W5_FALL":          f"{math.dist(runs['water-5'].pts[1], runs['water-5'].pts[2]):.3g}",
        "W5_LEAN":          f"{R.leg_skew(runs['water-5'].pts[0], runs['water-5'].pts[1], _frames()['discharge-chain'].normal('tube-port')):.3g}",
        "W5_RISER_GAP":     f"{math.dist(runs['water-5'].pts[-1][:2], runs['fluid-25'].pts[0][:2]):.3g}",
        # The shelf crossing, off the shelf itself: how far over the tallest lid on the cap the
        # crossing's own lane stands, and the widest lane those modules leave between them.
        "SHELF_STEP":       f"{max(p[2] for p in runs['fluid-19'].pts) - _shelf_top_under(solids, runs['fluid-19']):.4g}",
        "SHELF_GAP":        f"{_shelf_gap(solids):.3g}",
        # The stratum over the divider and under the trays, off the two crowns that bound it.
        "LOFT_GAP":         f"{_boxes.boxed(solids['bag-b-tray-assembly']).zmax - _boxes.boxed(solids['divider-y-h']).zmax:.3g}",
        "TUBE_OD":          f"{runs['fluid-19'].diam:.4g}",
        # The pump lane, and what the row's own legs measure off it.
        "AFT_BAND":         f"{contents.SOURCE_TRAY_AFT_BAND:.4g}",
        "PUMP_LANE_W":      f"{contents.pump_row_tee_pos('tee-y-c')[0] - contents.pump_row_tee_pos('tee-y-d')[0]:.4g}",
        "PUMP_DISCH_LEAN":  f"{abs(runs['fluid-12'].pts[0][0] - runs['fluid-12'].pts[-1][0]):.3g}",
        # The discharge leg's own corner, and what an arc of the stock's full radius costs there.
        # A shallow turn is what lets the shortest run on the machine carry the widest radius: the
        # tangent goes as tan(θ/2), so this corner asks a fifth of what a square one would.
        "PUMP_DISCH_TURN":  f"{max(t for _i, t, _a, _b in runs['fluid-12'].bends):.3g}",
        "PUMP_DISCH_TANGENT": f"{max((runs['fluid-12'].radii[i] * math.tan(math.radians(t) / 2.0) for i, t, _a, _b in runs['fluid-12'].bends), default=0.0):.3g}",
        "LLDPE_MIN_BEND":   f"{scorecard.stock_of('fluid', 6.35).min_bend:.4g}",
        "PUMP_ROW_PITCH":   f"{runs['fluid-13'].pts[1][1] - runs['fluid-10'].pts[1][1]:.4g}",
        # The aft band's ladder, read off the built runs: what its near rung leaves at the tray
        # face, and the two figures that pin reservoir B's riser to Y-H's column — the shelf the
        # stem's plane keeps over the selects crown, and what fluid-19's crossing leaves over
        # that plane at Y-F's column.
        "PUMP_ROW_LEAD":    f"{runs['fluid-10'].pts[1][1] - runs['fluid-10'].pts[0][1]:.4g}",
        # The front chain's own link, off the placed bodies: what Y-E's hang keeps to the
        # pumps' aft faces. The column keeps the same figure to Y-E.
        "FRONT_CHAIN_GAP":  f"{_boxes.boxed(solids['tee-y-e']).ymin - _boxes.boxed(solids['pump-a']).ymax:.2g}",
        # The two legs one corner short of two stock arcs, and the cap each hands its second
        # corner so the first turns at stock: carb-1's window under the meter, and fluid-17's
        # turn lane over the junction bay.
        # Y-F's own column against the two bodies fluid-21 was drawn around: the casting whose
        # corner the dropped lean was struck on, and the tray stack's east margin it lands in.
        "F21_GRAZE_CLEAR":  f"{contents.y_f_port('Y-F-3')[0][0] - _boxes.boxed(solids['seaflo-pump']).xmax:.3g}",
        "F21_BAND_STEP":    f"{contents.y_f_port('Y-F-3')[0][0] - (_boxes.boxed(solids['bag-a-tray-assembly']).xmax - CLIMB_HUG - 6.35 / 2.0):.3g}",
        "CARB_WINDOW_LEG":  f"{runs['carb-1'].pts[4][0] - runs['carb-1'].pts[3][0]:.4g}",
        "CARB_JOG_CAP":     f"{runs['carb-1'].radii[4]:.3g}",
        # The wall sequence's forward end: what the panel leaves fluid-2 between the regulator's
        # outlet and V-A's inlet, and what `lean_leads` spends it on — the lean each lead takes
        # off its collet's axis, the lead that buys, and the tangent a stock arc costs at that
        # lean. The difference between the last two is the straight still running into each
        # collet (`DIVIDER_LEG_STRAIGHT`).
        "F2_BUDGET":        f"{_f2_leads()[0]:.4g}",
        "F2_LEAN":          f"{_f2_leads()[1]:.4g}",
        "F2_LEAD":          f"{_f2_leads()[2]:.4g}",
        "F2_TANGENT":       f"{_f2_leads()[3]:.4g}",
        "F2_STOCK":         f"{contents.LLDPE_STOCK_BEND:.4g}",
        "F2_SLACK":         f"{_f2_slack():.3g}",
    }


def _f2_leads():
    """fluid-2's forward budget and the three figures `lean_leads` turns it into."""
    f = _frames()
    reg, src = f["flow-regulator"], f["source-tray-assembly"]
    _pts, lean, lead, tangent = lean_leads(reg, "outlet", src, "V-A-I")
    return reg.at("outlet")[1] - src.at("V-A-I")[1], lean, lead, tangent


def _f2_slack():
    """How much of fluid-2's forward budget could be taken back before the collet's own skew
    is the binding one — the run's headroom against a body drifting toward it, in millimetres
    of the sequence's standoff off the rear panel."""
    have = _f2_leads()[0]
    r, s = contents.LLDPE_STOCK_BEND, contents.DIVIDER_LEG_STRAIGHT
    need = 2.0 * math.cos(math.radians(FLAVOR_SKEW)) * (
        r * math.tan(math.radians(90.0 - FLAVOR_SKEW) / 2.0) + s)
    return have - need


# A run whose id is not itself a connection, because an in-line fitting splits it: a union
# tee's RUN ports face each other down one straight path, so two segments butted into them
# can be one piece of authored geometry answering for both on the routed axis.
CARRIES: dict = {}


def routed_ids() -> set:
    """The connection ids with a built path — what the scorecard's `routed` axis counts. A run
    that fell short of what it needs is drawn but not carried, so its connections are counted
    by `blocked_ids` instead."""
    return {c for r in build_runs() if r.id not in BLOCKED
            for c in CARRIES.get(r.id, (r.id,))}


def blocked_ids() -> dict:
    """Connection id → the measurement that blocks it. A run answering for several connections
    blocks all of them, so the reasons follow `CARRIES` the way the routed ids do."""
    return {c: why for r in build_runs() if (why := BLOCKED.get(r.id))
            for c in CARRIES.get(r.id, (r.id,))}


def clearances(solids: dict) -> list:
    """Each run's tightest gap to a part it does not terminate on, or to another run. The two
    components a run joins are skipped. Reported, not gated; `HSM_SKIP_CLEARANCES` drops it.

    The nearest is found by a box-sorted branch-and-bound. A box gap is a lower bound on the exact
    solid gap — a box encloses its solid, so two boxes are at least as close as the solids inside
    them — so candidates are ordered by box gap and, once one's box gap exceeds the tightest exact
    gap found, every farther candidate is skipped: its exact gap cannot be smaller. The reported
    number is still the exact BRepExtrema distance to the true nearest; only the queries that
    provably cannot win are dropped, several hundred of them per build. The cached boxes make the
    ordering nearly free. PRUNE_SLOP guards the bound against floating-point on a near-flush pair."""
    import scorecard

    PRUNE_SLOP = 1e-6                                   # mm; a box gap this much past best still queries
    runs = build_runs()
    tubes = {r.id: R.tube(r) for r in runs}
    boxes = {n: _boxes.boxed(s) for n, s in solids.items()}
    tube_boxes = {rid: _boxes.boxed(t) for rid, t in tubes.items()}

    out = []
    for r in runs:
        t, tb = tubes[r.id], tube_boxes[r.id]
        ends = {r.frm.split(".")[0], r.to.split(".")[0]}
        cand = [(scorecard._bbox_gap(tb, boxes[n]), n, solids[n]) for n in solids if n not in ends]
        cand += [(scorecard._bbox_gap(tb, tube_boxes[o]), o, tubes[o]) for o in tubes if o != r.id]
        cand.sort(key=lambda c: c[0])
        best = None                                    # (exact gap, name) of the nearest so far
        for bgap, n, s in cand:
            if best is not None and bgap > best[0] + PRUNE_SLOP:
                break                                  # lower bound past best: no farther body can win
            g = scorecard._solid_gap(t, s)
            if best is None or (g, n) < best:
                best = (g, n)
        out.append((r, best))
    return out
