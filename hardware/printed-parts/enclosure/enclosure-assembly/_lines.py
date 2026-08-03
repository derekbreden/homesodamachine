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
  * the LOFT's own port plane at [333.3](LOFT_PORT_Z), where the whole of channel B stands.
    Both of the loft's trays present their eight collets on it, so fluid-24 and fluid-26 are
    the bag-A pair's two legs read again a storey up, and fluid-18 and fluid-28 leave it on
    the level before they climb.
  * the loft's JUNCTION BAY (`_contents.AFT_TRAY_BAY`) — [37.33](LOFT_BAY) mm between the
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
    [-28.4](LOFT_GAP) mm, and the one stratum at this height that runs clear across the machine
    with the electronics shelf under it and the basin's rails over it. Nothing crosses IN it
    today: water-3 crosses east a storey over it, on the west column's fifth rung, forward of
    every tray and rail — its stratum is ranked against fluid-19's fall on the column a pitch
    short of its own (the west-column table below) — and holds V-K's column down to the third
    `LINE_PITCH` ahead of the bay's own turn lane, whose lead seats its foot corner at stock.
  * the loft's OUTLET LANE (`_contents.aft_outlet_lane`), [32.2](OUTLET_LANE) mm of spare
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
# The reach the branch run to V-K is given at each end: the climb off the split's upward collet,
# the lane ahead of the valve's mouth, and twice it for the height that lane stands at, which is
# what carries the run over the PSU's aft corner. The lane is the binding one — the mouth stands
# this far behind the PSU's back face, and a closing corner seats on the straight it has.
VK_TURN = 7.0
# How far off a collet's own axis a soft-LLDPE run may leave or enter as one straight length,
# past the rigid-copper `COLLET_SKEW`. The legs at the divider lean by construction
# (`_contents.DIVIDER_LEAN`), fluid-16 leans out of Y-E's run the same way, and a
# push-to-connect collet grips all round.
FLAVOR_SKEW = 22.0
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

    # fluid-24 / fluid-26 — the bag-B pair to its divider. A divider's outlets are
    # [14.7](DIVIDER_SPAN) apart and the two collets they join a seat pitch
    # ([34.25](SEAT_PITCH)) apart, so each leg leans [9.775](LEG_LEAN) mm across on its
    # way through — and that cross is now ALL either leg carries. Y-H used to be the one
    # divider not standing in its pair's port plane: the PSU's brick was what the aft stand
    # had ahead of it, so the fitting stood over that crown and each leg's lean carried a
    # climb as well as the cross. The stand packs forward now, the brick is aft behind the
    # whole deck, and Y-H lies where every other divider lies — `_contents.y_h_pos` is
    # `_divider_pos`, and `DIVIDER_LEG_LEAD` is the straight each leg leaves its collet on.
    yh_lead = contents.DIVIDER_LEG_LEAD
    for cid, frm, to, who in (
        ("fluid-24", "bag-b-tray-assembly.V-I-O", "divider-y-h.Y-H-1", "pump return → Y-H"),
        ("fluid-26", "divider-y-h.Y-H-3", "bag-b-tray-assembly.V-H-I", "Y-H → bag B draw"),
    ):
        runs.append(R.bent(
            cid, frm, to, kind="fluid", skew=FLAVOR_SKEW,
            lead=yh_lead,
            note=f"{who}: one leaning leg carrying the cross and the climb, straight off "
                 f"each collet"))

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

    runs.append(R.bent(
        "fluid-16", "tee-y-e.Y-E-3", "bag-a-tray-assembly.V-E-I",
        kind="fluid", skew=FLAVOR_SKEW, lead=WBEND,
        note="Y-E run → bag A draw: one leaning leg, straight off each collet, carrying the fall "
             "to the port plane and the cross onto the draw's line in one move"))

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
    # hangs in the LOFT, so what this connection owes is a STOREY OF Z and [0.125](BAG_B_CROSS)
    # mm of plan. It does not cross the machine and it takes no lane in the corridor: the cold
    # core's own +Y BAND (`_cold_core_interface.west_lane_mid_y`) stands directly under the
    # fitting, runs the shell's whole height with nothing else in it, and carries the climb
    # potted — from the pocket-wall bore on the bulkhead's own axis, up the band, out through
    # the cap's `reservoir-b` conduit onto the deck. None of that is drawn here; it is shell,
    # and `assembly/cold-core.md` lays the tube in the band before the pour.
    #
    # What IS drawn is the last of it, off the conduit's mouth on the lid's outer face at
    # [253.4](BAG_B_DECK_Z), and it is two legs: up the PSU's WEST FLANK to the stem's own
    # plane, and one leaning leg north-east over the brick's crown into the collet. The brick
    # prices both — it roofs the lid everywhere reservoir B lies, which is
    # why the climb stands beside it rather than over it, and its crown is only
    # [27.9](Y_H_CROWN_BAND) mm under the stem's plane: a stock arc turning off this climb is still
    # [0.725](STOCK_RISE) mm short of clearing that crown when it has already drifted
    # [0.0103](STOCK_DRIFT) mm east into it. So the turn seats what the band leaves it, and what
    # buys it back is the brick moving further east — `probe travel psu +x` prices that, and the
    # bill is the water-5 lane and the ground stud's second move. Lifting the fitting instead
    # buys nothing: the stem's plane is a slot of its own, [41](STEM_SHELF) mm over the selects
    # crown with a tube and its floor and nothing spare, and fluid-19's shelf crossing rides
    # Y-F's own column [-12](LOFT_CROSS_CLEAR) mm above it.
    y_h = f["divider-y-h"]
    riser = f["foam-assembly"].at("reservoir-B")
    runs.append(R.bent(
        "fluid-25", "foam-assembly.reservoir-B",
        (riser[0], riser[1], y_h.at("Y-H-2")[2]),      # straight up the conduit's own column, west of the brick
        "divider-y-h.Y-H-2",                           # and one lean, north-east over the crown into the stem
        kind="fluid", skew=FLAVOR_SKEW, lead=(0.0, STEM_FALL_REACH),
        note="reservoir B → Y-H stem: up the conduit's own column past the PSU's west flank, "
             "and one leaning leg over its crown into the stem"))

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
    y_f, y_g = f["tee-y-f"], f["divider-y-g"]
    sea, vk = f["seaflo-pump"], f["vk-tray-assembly"]

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

    def aft_row_approach(stock: float) -> float:
        """The Y a run FALLS on to reach the aft row's forward-facing collets — the mirror of
        `aft_turn_lane`, struck off the row it is going into rather than the row it left.

        Held AFT of the SUCTION BARB'S OWN LANE. The barb faces west out of the casting and
        water-4 crosses the whole band on its axis to reach it; a fall struck for the closing
        corner alone lands within a tube of that crossing, so the corner gives up the last
        millimetres rather than the crossing giving up its plane."""
        return max(nz.bb.ymin - contents.JUNCTION_LEG_LEAD - stock,
                   sea.at("suction")[1] + LINE_PITCH + 6.35 / 2.0)
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
    for cid, frm, to, who in (
        ("fluid-23", "bag-b-tray-assembly.V-I-I", "divider-y-g.Y-G-2", "bag B fill ← Y-G"),
        ("fluid-27", "vk-tray-assembly.V-J-I", "divider-y-g.Y-G-3", "nozzle B gate ← Y-G"),
    ):
        runs.append(R.bent(cid, frm, to, kind="fluid", skew=FLAVOR_SKEW,
                           lead=(bay_lead, contents.Y_G_CLIMB - y_g_rise),
                           note=f"{who}: out of the collet along the bay, about, and up into "
                                f"the outlet standing over it"))

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
    # ends [11.6](F21_GRAZE_CLEAR) mm west of that column, so this run never comes near the
    # corner a lean would be dodging — and struck as a 45° about that corner the two waypoints
    # land AFT of each other while the run is travelling forward, which is a doubling-back and
    # two 135° turns on a six millimetre leg. What the run owes between the collet and the
    # band is [4.17](F21_BAND_STEP) mm of X, and the fall already carries more than that.
    runs.append(R.bent(
        "fluid-21", "tee-y-f.Y-F-3",
        (yf3[0], yf3[1] - yf3_lead, west_col[2]),    # forward, then down onto the deck crossing
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
        # THE STEM'S OWN COLUMN IS THE LANE. Y-G stands in the strip between the lanes and the
        # band over its crown is [31](YG_COLUMN) mm clear to the hopper's floor, so this run
        # takes the stem's x at the FIRST crossing and never leaves it: the climb, the length
        # of the machine and the fall are all one column, and the fall is taken ON the stem.
        # Struck off the tray-east lane instead, the run arrives a stem's offset east of the
        # port and spends two corners on a jog no body asks for.
        y_g.x("Y-G-1"),                      # east over it onto the stem's own column
        # AND STRAIGHT UP FROM THERE. The aft leg this run used to take at the crossing's own
        # height put it in the front column's east lane at the very depth fluid-21's fall
        # crosses that lane, and the run has the same Y to spend whichever storey it spends it
        # on — so it spends it aloft, where the column is the funnel's floor and nothing else's.
        {"z": loft_cross_z},                 # up the front column, to the funnel floor's hug
        y_g.y("Y-G-1"),                      # aft the machine's length onto the stem's own lane
        "divider-y-g.Y-G-1",                 # and straight down into the stem
        # The strip off P-A-O carries fluid-16's lean out of Y-E's run, a `WBEND` off the barb.
        kind="fluid", stub=WBEND, skew=FLAVOR_SKEW,
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
    yf1_col = yf1[0] - contents.JUNCTION_LEG_LEAD - R.stock_min("fluid", y_f.diam("Y-F-1"))
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

    # fluid-17 — channel A's discharge tee to the nozzle-A gate, and the longest run in the
    # machine: a storey, from the front column's own west rim to the aft stand's wide plate.
    # Y-D's branch faces UP, so the run leaves on that axis; what it has to cross is the whole
    # service bay, and the aft stand is what shapes it. It climbs the front column's west lane
    # onto the stratum over the electronics shelf, crosses east in the band aft of the trays,
    # comes aft up the SLOT between the bag-B pair's east face and the SeaFlo's flank, drops
    # onto the stand's own port plane in the junction bay, and turns west onto the gate's
    # column.
    #
    # The band it crosses in is floored by the shelf's tallest module and roofed by the source
    # pair's own port underside, and it carries TWO crossings: reservoir B's fill holds the Y-H
    # port plane through it on its way to the loft, so this one takes the band's ROOF — a tube's
    # radius and a clearance floor under that underside.
    #   It comes aft on THE GATE'S OWN COLUMN. The stand is three rows of one plate now and the
    # gate takes its plate's east seat, so that column runs the length of the stand with the
    # middle row's bare west seat and the bag pair's bay under it — the run reaches its own
    # collet without ever leaving the column it lands on, and the turn into the bay is the fall
    # itself rather than a lane across it.
    vg_stock = R.stock_min("fluid", nz.diam("V-G-I"))
    runs.append(route(
        "fluid-17", "tee-y-d.Y-D-3",
        {"x": f["tee-y-c"].bb.xmin - contents.PUMP_ROW_TURN},
                                             # EAST OUT OF THE BAND FIRST. Y-D stands in the
                                             # front column's west lane, which is inside the −X
                                             # boss chain, and that chain runs the piece's whole
                                             # height — so a climb taken where the tee stands
                                             # rises into the wall's own furniture.
                                             #   THE STEP IS A LEG AND TWO CORNERS SHARE IT, so it
                                             # runs to the far wall of the strip rather than just
                                             # off the near one: the strip is bounded east by Y-C,
                                             # whose own centre column carries fluid-9's fall, and
                                             # the tray stack stands behind that. Struck one tube's
                                             # floor off `CORE_WEST_FACE` the step is seven
                                             # millimetres and both corners turn on three
        {"z": nz.bb.zmax + contents.PUMP_ROW_TURN},
                                             # up out of the front column and OVER THE STAND'S
                                             # CROWN — the stand is three rows of one plate on one
                                             # lane, so a run reaching the last row crosses the
                                             # other two, and the band over the crown is where it
                                             # crosses them
        {"y": y_g.bb.ymin - CLIMB_HUG - 6.35},
                                             # CROSS IN THE ONE BAND BETWEEN THE TWO TRIDENTS.
                                             # This run ends on the far side of the machine AND
                                             # well aft, so every millimetre it crosses forward of
                                             # its own destination it pays for twice. Forward of
                                             # this plane stands Y-H on the pair's west flank with
                                             # its two legs and the bag's own fill, and the draw's
                                             # climb beside Y-F; aft of it Y-G's crown reaches into
                                             # this very stratum — and a fitting is round where
                                             # its box is square, so the clearance is struck as
                                             # a whole tube off that box and not one floor
        nz.x("V-G-I"),                       # east onto the gate's own COLUMN, still aloft
        {"y": aft_row_approach(vg_stock)},   # aft ALONG THE CROWN onto the plane its own
                                             # lane. The fall is taken IN the bay and not ahead
                                             # of it: V-K's plate stands on this column between
                                             # here and there, and a run dropping to the port
                                             # plane before it has cleared that plate crosses it
        {"z": nz.at("V-G-I")[2]},            # down the bay onto the stand's port plane
        "nozzle-tray-assembly.V-G-I",        # and aft into the collet, down the lane it faces
        kind="fluid", skew=FLAVOR_SKEW, stub=(7.45, 1.0),
        bend=vg_stock,
        note="Y-D branch → nozzle A gate: up the front column's west lane, east over the "
             "stand's crown onto the gate's own column, and down it into the collet"))

    # fluid-18 / fluid-28 — the nozzle gates to the rear panel, and the only two lines the
    # manifold sends OUT of the machine. Both end on the rear panel's own port row, one
    # bulkhead each, and the nozzle tray stands in the loft's west lane
    # ahead of them — which is what puts that pair up here rather than in the front column.
    #
    # Both leave AFT into the OUTLET LANE behind the plate (`_contents.aft_outlet_lane`), and
    # the band they turn in is the panel field's own footing: the water bulkhead's body stands
    # on V-J's column from the port row down, and the C14's on V-G's.
    #   So each climbs only as far as the SHELF — the band between the AFT STAND'S OWN CROWN
    # and the lowest body in that field (the header's shelf bullet: the plate's coil row is
    # what runs under these crossings, not the SeaFlo, whose tall half ends forward of them).
    # Each crosses it in ONE LEAN, east and forward together, onto its bulkhead's own column
    # ahead of the body, and climbs the last storey there.
    #   The pair are TWINS and are built as twins: one lane, one shelf level, one approach
    # rule, and the only thing that differs between them is which bulkhead each is aimed at.
    # What holds them apart is the aim itself — the two turns behind the plate stand a whole
    # seat pitch apart in X ([6.7](GATE_SEAT_PITCH) mm) and the two leans diverge from
    # there, never closing nearer than [0](GATE_PAIR_GAP) mm of tube — so neither owes the
    # other a Y lane or a level. Both come about on the outlet lane's one rung, the deepest
    # the band holds, and water-4's turn is the third station on it.
    #   That lane is struck off the STATED WALL, not the plate's face: the band behind the
    # plate runs one `aft_outlet_lane()` deeper than one lane's own minimum — spare the
    # PLATE cannot pack into (V-J's rim on the corner column, `_contents.bag_b_tray_y`) —
    # and a lane is air, so the rung stands where its tube holds the pack's floor off
    # `REAR_PLANE_Y` and the whole spare rides the three leads that turn on it.
    out_lane = contents.REAR_PLANE_Y - contents.LINE_HUG - 6.35 / 2.0
    for cid, port, panel, who, plate, body in (
        ("fluid-18", "V-G-O", "bulkhead-flavor-a", "nozzle A", nz, "nozzle-tray-assembly"),
        ("fluid-28", "V-J-O", "bulkhead-flavor-b", "nozzle B", vk, "vk-tray-assembly"),
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

        #   The come-about stands where its OWN CORNER wants it and not at the band's midpoint:
        # a square turn at stock spends its radius on the tangent, and the collet's lead is the
        # straight that has to survive in front of that. `_contents.nozzle_tray_y` cuts the band
        # to exactly this sum, so the midpoint of it is half a corner.
        climb_y = (aft_turn_lane(gate_stock) if plate is vk
                   else min(gate[1] + contents.JUNCTION_LEG_LEAD + gate_stock,
                            field_front(gate[0], plate.bb.ymax) - contents.PUMP_ROW_TURN))
        # The climb stands on the gate's own column unless the METER stands in it — the run
        # crosses the meter's band at the panel's stratum and the meter's crown reaches into it,
        # so the column steps west of that body before it rises.
        meter_w = f["digiten-flow"].bb.xmin - contents.PUMP_ROW_TURN
        lane_x = min(gate[0], meter_w) if gate[0] + 6.35 / 2.0 > meter_w else gate[0]
        # The west leg runs at the panel's stratum, and the ASSE CHAIN stands in that stratum
        # across the west end of the field. A leg reaching a bulkhead behind the chain crosses
        # its column, so on that column the approach stands AFT of the chain rather than ahead
        # of the bulkhead — which is the shorter closing straight of the two, and the collet's.
        chain_bb = f["asse1022-assembly"].bb
        appr_y = tin[1] - gate_stock - contents.JUNCTION_LEG_LEAD
        if tin[0] - 6.35 / 2.0 < chain_bb.xmax:
            appr_y = max(appr_y, chain_bb.ymax + contents.PUMP_ROW_TURN)
        # THE TWO GATES DO NOT SHARE A STRATUM. Their columns stand one seat pitch apart
        # ([6.71](GATE_SEAT_PITCH) mm — closer than a tube), their bulkheads stand a station
        # apart the other way, and the westmost of the two has to cross the whole field AFT of
        # the ASSE chain: so each one's long leg runs through the other's column, and no lane in
        # X parts them. What parts them is height. The AFT ROW'S gate keeps the panel's own row
        # — its bulkhead is east of the chain and its approach is the shorter of the two — and
        # the MIDDLE ROW'S crosses a tube and its floor under that row, climbing the last step
        # on its own bulkhead's column where nothing else stands.
        #   That stratum is the AFT ROW'S OWN CROWN, one tube and its floor over it: the middle
        # row's gate is the only one of the two with a plate standing between it and the panel,
        # so the row it climbs over is what its crossing height is for, and everything else in
        # that field — the basin, the backflow chain, the meter's outlet lean — stands clear
        # above or west of the two legs it spends there.
        cross_z = (panel_z if plate is nz
                   else nz.bb.zmax + 2.0 * contents.PUMP_ROW_TURN)
        legs = [(lane_x, climb_y, gate[2]),  # aft off the gate into its own climb band
                (lane_x, climb_y, cross_z),  # and up the storey, clear of the field
                (lane_x, appr_y, cross_z),   # aft over it on this run's own stratum
                (tin[0], appr_y, cross_z)]   # west onto the bulkhead's column
        if cross_z != panel_z:
            legs.append((tin[0], appr_y, panel_z))   # the last step, on that column alone
        runs.append(R.bent(
            cid, f"{body}.{port}", *legs,
            f"{panel}.tube-in",              # and aft into the collet
            kind="fluid", skew=FLAVOR_SKEW, bend=gate_stock,
            note=f"{who}: nozzle gate → rear panel, up its whole storey in the band behind "
                 f"the gate, aft over the electronics field on its own stratum, and west onto "
                 f"the bulkhead's column"))

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
    #   The branch stands the line down where it leaves, and the first fall stops on the west
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
    vk_stock = R.stock_min("water", vk.diam("V-K-I"))
    runs.append(route(
        "water-3", "water-split.to-vk",
        {"z": nz.bb.zmax + contents.PUMP_ROW_TURN + 6.35},
                                             # down out of the fittings loft onto the rung over
                                             # fluid-17's, one tube clear of the run it shares
                                             # the east column with
        vk.x("V-K-I"),                       # east across it onto the valve's own column
        vk.y("V-K-I", -(vk_stock + contents.JUNCTION_LEG_LEAD)),
                                             # aft down that column onto the plane its own CLOSING
                                             # CORNER wants. V-K's east seat stands at the far end
                                             # of the stand and the band ahead of that column is
                                             # open to the condenser — Y-G's strip is thirty
                                             # millimetres west of it — so the fall lands where a
                                             # square turn seats its tangent with the collet's
                                             # lead surviving in front, not on a bay lead struck
                                             # for a bay that no longer stands here
        vk.z("V-K-I"),                       # down into the bay onto the stand's port plane
        "vk-tray-assembly.V-K-I",            # and aft into the mouth
        kind="water", skew=FLAVOR_SKEW, stub=(VK_TURN, 1.0),
        note="tap water: split branch → V-K inlet, down onto the west column's crown rung, east "
             "across the machine onto the valve's column and down the far side of the trays"))

    # water-4 — V-K's outlet to the SeaFlo's suction barb, a hop across the lane between the
    # east stand and the pump. Its two ends stand [65.9](W4_SPAN) mm apart and BOTH FACE INTO
    # THE BAY: the valve discharges aft at y [333.4](W4_BARB_Y), the barb opens EAST on that
    # same plane, and the bay behind the valve's plate is the one band on this deck with no
    # plate in it. So the run never leaves the valves' own port stratum to cross — it comes
    # aft one bay-half, runs west down the bay, and leans forward and up into the barb.
    #   THE BAY IS THE LANE. `VK_TRAY_BAY` is struck for one tube: the plate's aft face and
    # the aft row's forward face stand [24](W4_BAY) mm apart and a ⌀6.35 line hugs each by
    # 0.83, which is why the crossing rides the bay's midpoint and nothing else turns in it
    # west of the gate's own climb.
    #   The descent column stands in the LANE BETWEEN THE BARB TIP AND THE PLATE'S WEST
    # FACE — `R.channel` puts it on that gap's midpoint, and the gap is the whole of what
    # the pump leaves the east lane at this depth, since the casting's own reach here is the
    # barb and not the foot pad ([10](W4_LANE) mm). What the lean buys is the barb's
    # [17.7](W4_RISE) mm of Z and the half-bay of Y together, one leg carrying both, and its
    # two corners are the run's roundest: the crossing and the closing lead are what they
    # seat on.
    #   The come-about off the mouth turns on the plane its own arc wants
    # ([33.4](W4_STUB) mm off the plate's face, `aft_turn_lane`) — a stock tangent with the
    # collet's lead surviving in front of it.
    suction = sea.at("suction")
    # THREE RUNS TURN IN THIS BAND and each stands on its own column: this one off V-K-O at the
    # stand's east end, the nozzle-B gate off V-J-O, and the nozzle-A feed descending on V-G's.
    # None is within a tube of another in X, so each takes the whole band's depth for its turn.
    w4_lane = aft_turn_lane(R.stock_min("water", vk.diam("V-K-O")))
    # The descent column stands ONE STOCK ARC EAST OF THE BARB, which is what its closing corner
    # turns on. Nothing closes that lane: at the barb's own depth the pump's reach IS the barb,
    # the east stand is forward of it and the aft row is behind it, so the band from the tip to
    # the core's east face is empty and the lead the corner wants is the only thing asking for
    # any of it. Clamped to that face, which is the one edge the band does have.
    #   The band's one tenant is the NOZZLE-A FEED, which falls on its gate's own column on its
    # way into the row behind; the descent stands a lane clear of that and takes the stock arc
    # anyway, since east of the fall the band is wider than the arc asks for.
    w4_stock = R.stock_min("water", vk.diam("V-K-O"))
    #   A `LINE_PITCH` off that fall is centre-to-centre spacing, which leaves the two tubes one
    # clearance floor apart on the straights and nothing at all once each turns — and both DO
    # turn here, this one west off its lane and the fall onto its own closing leg. So the
    # descent stands a pitch AND a tube's radius clear, which is what the two arcs want.
    w4_x = min(max(suction[0] + w4_stock,
                   nz.at("V-G-I")[0] + LINE_PITCH + 6.35 / 2.0),
               contents.CORE_EAST_FACE - 6.35 / 2.0)
    runs.append(R.bent(
        "water-4", "vk-tray-assembly.V-K-O",
        (w4_x, w4_lane, vk.at("V-K-O")[2]),
                                         # west down the bay's first lane, holding the valves'
                                         # own port stratum onto the descent column
        "seaflo-pump.suction",
        kind="water", skew=FLAVOR_SKEW,
        lead=(w4_lane - vk.at("V-K-O")[1], w4_x - suction[0]),
        note="tap water: V-K outlet → SeaFlo suction, aft into the bay's first lane, west "
             "down it on the valves' own stratum, and one lean aft and up the lane between "
             "the casting and the aft row into the barb"))

    # water-6 — the 3/8" braided stub off the molded discharge barb. The barb points east
    # at the wall; the hose comes about in the pocket between them on its own radius and
    # runs forward leaning gently back onto the chain's barb, which stands east of the
    # discharge's own column for exactly this leg.
    #   The pocket is what sets the exit stub. The wall's inner face stands at x 195 and the
    # barb tip at x 177, so the hose's own half-section and one clearance floor leave 9.45 mm
    # for the stub to reach into before the sweep's corner touches the piece — and the corner
    # IS the reach, a quarter turn putting its far tangent on the waypoint itself. 9.0 takes
    # that room and keeps the 8.00 the port wants to leave on axis; the quarter turn then
    # rounds under its stock minimum, which is the pocket's depth and not a number to raise.
    runs.append(R.bent(
        "water-6", "seaflo-pump.discharge", "discharge-chain.barb-tip",
        # The approach is the COLLET'S OWN LEAD and no more. The basin stands aft of this barb
        # at exactly that reach (`_contents` hangs its front wall off this station), so a
        # closing straight longer than the lead is a straight drawn inside the basin.
        kind="water", bend=HOSE_BEND, skew=14.0,
        lead=(9.0, contents.JUNCTION_LEG_LEAD),
        note="carb water: SeaFlo discharge barb → discharge chain, one leaning sweep in "
             "the wall pocket (3/8\" braided PVC, two clamps)"))

    # water-5 — the chain's forward collet to the core's water inlet, and the tap-water path's
    # one fall. THE INLET IS UNDER THE PUMP. The conduit opens +Z out of the top cap at
    # x [71.5](W5_INLET_X), and the casting's head block stands over that column from
    # [13](W5_SLOT) mm above the lid to its crown — so nothing reaches this port from above,
    # and the run arrives along the SLOT the casting leaves between its head and the lid it
    # stands on. `contents.seaflo_lid_slot` measures that slot off the solid, because the
    # pump's box is one brick from foot to crown and says the port is buried.
    #   The collet faces FORWARD, so the run leaves forward whatever it is going to do, and
    # the turn it makes there is bounded by Y-H's aft face — the trident stands on this same
    # column a storey down. One come-about there, east along the loft over the bag pair's own
    # crown, aft clear of that pair, and one fall down the open column in the band between the
    # pair and the casting's front face. Then the slot: aft under the head at the lead the
    # port itself asks for, and down into the conduit.
    #   The fall's column is the one place on this deck where a line may go from the loft to
    # the lid without crossing a body — the bag pair closes it forward, the casting closes it
    # aft, and the [23.5](W5_WINDOW) mm between them is what this run spends.
    w5_slot = contents.seaflo_lid_slot(*foam.at("water-in")[:2])
    # The band under the head: the port's own lead off the lid, which is what a ⌀6.35 line
    # clears the casting's underside on. `port-leads` states the lead; the slot states the roof.
    w5_under = foam.at("water-in")[2] + contents.JUNCTION_LEG_LEAD
    # The come-about stands clear of the trident's aft face; the fall's column stands clear of
    # the bag pair's, in the window between that pair and the casting's front face. ONE LEAN
    # joins them — the whole eastward crossing and the step onto the fall's column in one leg,
    # which is what the fall's head corner seats on. The lean holds the loft's height for its
    # whole length: the pair's crown is under it and the drop is on the far side of the pair.
    chain = f["discharge-chain"]
    # The come-about stands the collet's own lead ahead of it. The band forward of this chain
    # is the pair's, and the trident that used to hold this column stands ahead of the pair
    # now (`_contents.y_h_pos`), so what bounds the turn is the port and not a body.
    w5_turn = chain.at("tube-port")[1] - contents.JUNCTION_LEG_LEAD
    w5_drop = f["bag-b-tray-assembly"].bb.ymax + contents.PUMP_ROW_TURN
    runs.append(R.bent(
        "water-5", "discharge-chain.tube-port",
        (foam.at("water-in")[0], w5_drop, chain.at("tube-port")[2]),
                                             # the lean: east along the loft over the pair's
                                             # crown and onto the conduit's column together
        (foam.at("water-in")[0], w5_drop, w5_under),
                                             # down the window onto the slot under the head
        (foam.at("water-in")[0], foam.at("water-in")[1], w5_under),
                                             # aft along the slot onto the conduit's station
        "foam-assembly.water-in",            # and down into it
        kind="water", skew=FLAVOR_SKEW,
        lead=(chain.at("tube-port")[1] - w5_turn, contents.JUNCTION_LEG_LEAD),
        note="carb water: discharge chain → cold-core water inlet, one lean east along the "
             "loft, down the window ahead of the pump and aft along the slot under its head"))
    if w5_under + 6.35 / 2.0 > foam.at("water-in")[2] + w5_slot - contents.LINE_HUG:
        R._blocked("water-5",
                   f"the slot the casting leaves over the conduit is {w5_slot:.2f} mm and the "
                   f"line wants "
                   f"{contents.JUNCTION_LEG_LEAD + 6.35 / 2.0 + contents.LINE_HUG:.2f} of it — "
                   f"the pump's head stands over this port's own column")

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
    runs.append(R.bent(
        "carb-2", "digiten-flow.outlet",
        "bulkhead-carb.tube-in",
        kind="water", skew=FLAVOR_SKEW, lead=(12.9, 12.9),
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
    # The band the PSU's crown leaves under Y-H's stem plane, and what a stock arc turning off a
    # vertical spends of a climb before it has drifted out of that band: the arc reaches one tube
    # radius over the crown after `rise` of climb, by which point it stands `drift` to the side.
    yh_band = runs["fluid-25"].pts[-1][2] - _boxes.boxed(solids["psu"]).zmax
    stock_rise = contents.LLDPE_STOCK_BEND - yh_band + 6.35 / 2.0
    stock_drift = contents.LLDPE_STOCK_BEND * (
        1.0 - math.sqrt(max(0.0, 1.0 - (stock_rise / contents.LLDPE_STOCK_BEND) ** 2)))
    return {
        "SRC_PORT_Z":       f"{f4.pts[-1][2]:.4g}",
        "HOPPER_FALL":      f"{f4.pts[0][2] - f4.pts[1][2]:.4g}",
        # The geometry the loft divider's two legs share.
        "DIVIDER_SPAN":     f"{span:.4g}",
        "SEAT_PITCH":       f"{contents._tray.pitch:.4g}",
        "LEG_LEAN":         f"{(contents._tray.pitch - span) / 2.0:.4g}",
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
        "Y_H_CROWN_BAND":   f"{yh_band:.3g}",
        "STOCK_RISE":       f"{stock_rise:.3g}",
        "STOCK_DRIFT":      f"{stock_drift:.3g}",
        "LOFT_BAY":         f"{runs['fluid-27'].pts[0][1] - runs['fluid-23'].pts[0][1]:.4g}",
        "PORT_ROW_Z":       f"{runs['fluid-18'].pts[-1][2]:.4g}",
        # The outlet lane: what the band has spare once its one rung is struck, the pitch the
        # three turns on it stand apart, and the closest the twin gates' tubes ever come.
        "OUTLET_LANE":      f"{contents.aft_outlet_lane():.3g}",
        "GATE_SEAT_PITCH":  f"{abs(runs['fluid-18'].pts[1][0] - runs['fluid-28'].pts[1][0]):.4g}",
        "GATE_PAIR_GAP":    f"{scorecard._solid_gap(R.tube(runs['fluid-18']), R.tube(runs['fluid-28'])):.3g}",
        # The shelf, off the two bodies that actually bound it: the aft stand's coil crown
        # under it and the lowest body of the port field over it. The SeaFlo does not bound
        # it — its tall half ends forward of every crossing up here — and `seaflo_aft_step`
        # reads where that ends off the placed casting rather than off a typed station.
        "PANEL_SHELF":      f"{_boxes.boxed(solids['c14-inlet']).zmin - _boxes.boxed(solids['nozzle-tray-assembly']).zmax:.4g}",
        "STAND_CROWN":      f"{_boxes.boxed(solids['nozzle-tray-assembly']).zmax:.4g}",
        "SHELF_OVERSHOOT":  f"{_boxes.boxed(solids['seaflo-pump']).zmax - _boxes.boxed(solids['nozzle-tray-assembly']).zmax:.3g}",
        "SEAFLO_STEP_Y":    f"{contents.seaflo_aft_step()[0]:.4g}",
        "SEAFLO_AFT_CROWN": f"{contents.seaflo_aft_step()[1]:.4g}",
        # water-4's own need and the four stations that answer it: the span its two ends
        # actually ask for, the plane they share, the bay it crosses in and the lane its
        # descent column stands in, and the rise its one lean carries.
        "W4_SPAN":          f"{math.dist(runs['water-4'].pts[0], runs['water-4'].pts[-1]):.3g}",
        "W4_BARB_Y":        f"{runs['water-4'].pts[-1][1]:.4g}",
        "W4_BAY":           f"{contents.VK_TRAY_BAY:.3g}",
        "W4_LANE":          f"{_boxes.boxed(solids['vk-tray-assembly']).xmin - runs['water-4'].pts[-1][0]:.3g}",
        "W4_RISE":          f"{runs['water-4'].pts[-1][2] - runs['water-4'].pts[0][2]:.3g}",
        "W4_STUB":          f"{runs['water-4'].pts[1][1] - runs['water-4'].pts[0][1]:.3g}",
        # The band over Y-G's crown that fluid-22's fall is taken in, off the two bodies that
        # bound it: the trident's own crown and the hopper's floor.
        "YG_COLUMN":        f"{_boxes.boxed(contents.placed_funnel()).zmin - _boxes.boxed(solids['divider-y-g']).zmax:.3g}",
        # water-5's fall, and the two figures the casting sets it: the slot its head leaves
        # over the conduit's own column, and the window between the bag pair and its front face.
        "W5_INLET_X":       f"{runs['water-5'].pts[-1][0]:.3g}",
        "W5_SLOT":          f"{contents.seaflo_lid_slot(*runs['water-5'].pts[-1][:2]):.3g}",
        "W5_WINDOW":        f"{_boxes.boxed(solids['seaflo-pump']).ymin - _boxes.boxed(solids['bag-b-tray-assembly']).ymax:.3g}",
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
        "STEM_SHELF":       f"{runs['fluid-25'].pts[-1][2] - _boxes.boxed(solids['selects-tray-assembly']).zmax:.2g}",
        "LOFT_CROSS_CLEAR": f"{runs['fluid-19'].pts[2][2] - runs['fluid-25'].pts[-1][2]:.2g}",
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
