# Routing lines in the enclosure (`route`)

Every line the box carries is a `route(...)` in [`_lines.py`](_lines.py), built with the kit in
[`_routing.py`](_routing.py). Precedent: the board's
[`hand-routing.md`](/hardware/pcb/pcba/hand-routing.md).

## Writing a run

```python
route("refrig-1", "compressor-shroud.refrig-discharge",
      {"x": slot},                    # across into the condenser channel
      cond.y("refrig-inlet"),         # forward to the inlet's station
      cond.z("refrig-inlet"),         # up the channel to its height
      "condenser+fan.refrig-inlet")
```

A port anchor at each end, one-dimensional constraints between. Each constraint supplies one
coordinate; the other two carry over from the point before, so a waypoint moves along one axis
and every corner is square.

`F.x/y/z(port, d)` is the plane `d` along a world axis from that port. `F.out(port, d)` steps `d`
along the port's own face normal. `F.face("x+", gap)` sits `gap` clear of the component's +X body
face. `channel(a, b, bias)` positions a run between two faces — centred at bias 0, hugging one at
±1. A frame's box comes off the placed solid and its ports off `scorecard.PORTS`.

## Ports off the axes

A port's `face` is one of the six body faces by name, or — where a fitting is clocked off the
world axes — its axis given straight as a vector. The junction column's rolled elbows and the
tees hanging between them carry vectors. `out` needs a single axis and raises on one of these;
give the plane as `x`/`y`/`z`, or let the run close straight into the port.

`COLLET_SKEW` is how far off its own axis a straight tube may enter a collet and still run
unbent — a push-to-connect collet grips all round and soft LLDPE takes up the rest. A leg
arriving inside that angle needs no corner, so it needs no constraint to place one, and a run
between two nearly-facing collets is authored `route(cid, frm, to, stub=0.0)` with nothing
between. The column's four legs are written that way, ~1.8° at each end.

The exit stub off the source port and the approach stub into the destination are emitted by
`route`, along each port's face normal, one bend radius by default. `stub=(exit, approach)` sets
them separately.

## Bends

Each interior corner is a tangent arc of `bend` radius (`BEND_RATIO × Ø`, seeded at 2×OD =
12.7 mm for 1/4"), backed off `r·tan(θ/2)` down each leg. `Run.length` is the developed
centreline — the length of stock the run cuts.

A leg between two 90° corners is 2R = 25.4 mm. A corridor carries a turn one bend radius after
the face its port leaves.

`route` raises on a leg shorter than the tangents its two ends demand, on a close leaving more
than one coordinate differing from the approach point, and on a close nearer the port than its
own approach stub. Each guard has a defect and a control in
[`scorecard_selftest.py`](scorecard_selftest.py).

## How gentle a bend can be

`leg ≥ r·(tan(θa/2) + tan(θb/2))` is the guard above. Solved for `r` it is a ceiling the
waypoints put on the radius, and `leg_caps(run)` returns it per leg — so the smallest is the
most radius a centreline holds without a point moving. `scorecard.bend-radius` grades against
the minimum radius of the stock the run is drawn in (`scorecard.STOCKS`).

**The population is CORNERS, not runs.** Each corner turns at its own radius — the largest its
own two legs seat, up to the cap `bend=` sets (`_routing.seat_radii`). A leg between two corners
is shared, so the two rise together and whichever runs out first stops while the other keeps
rising into what is left; a corner an author caps deliberately hands the rest of its legs to its
neighbour. One radius for a whole run is that same solve with every corner roped to the tightest
one in it, so a run's gentlest turns read as its worst — fluid-22 holds four corners its legs
would seat at the full R25.4. A run's `radius` in the sidecar is its tightest corner and its
`grade` follows that; `corners` carries each one, and `atSpec` counts them.

Each run gets two grades. **drawn** is the authored radius over that minimum — the buildable
question, and what the gate reads. **reach** is the cap over the run's INTERIOR legs alone. The
leads are held out because the exit and approach stubs are reaches this file picks: counting
them would blame the pack for a number `_lines.py` owns, and every run whose stub is one bend
radius would report a ceiling exactly where it already sits.

So the pair narrows where to look, but **`reach` alone does not say a run can be raised.** It
bounds the interior legs; what usually binds first is a LEAD, and a lead is only free until it
meets a guard. The approach stub cannot exceed the distance the lane already stands off the port
— past that the close folds — so a square corner is capped at that standoff no matter how much
room the interior legs report. Runs whose `reach` is unbounded sit here: one bend, no interior
leg to measure, and a ceiling set entirely by how far their fitting stands off the lane.

Growing a lead is not free in the other direction either. On a leaning run the stub eats the
straight the lean is carried on, so every millimetre of stub steepens the angle the leg meets
the collet at — and `COLLET_SKEW`/`skew` is waiting. fluid-12 is the whole trade in one run: it
reaches its stock's full radius on a stub of 4.9, where 4.87 is too little tangent to seat the
arc and 4.97 arrives past the skew.

**A lead's DIRECTION is the other half of it, and it is free.** What a corner spends out of its
lead is `r·tan(θ/2)`, so the lead's length is only half the question — the turn angle is the
other half, and a lead that leaves dead on its collet's axis hands the run a square corner,
where `tan(45°) = 1` and the corner can never seat more radius than the lead is long. That is
the worst exchange rate on the curve. Tilt the lead toward the leg it hands off to and the turn
opens: the same lead buys `1/tan((90° − tilt)/2)` times as much radius, and the tilt costs only
what the collet's own `skew` allows, which soft LLDPE in a push-to-connect gives freely
(`FLAVOR_SKEW`). `lean_leads` is that solve, for the shape it pays best on — two mouths FACING
THE SAME WAY with a crossing between them, where the two leads have nothing but the mouths' own
separation to divide. It returns the SHALLOWEST tilt that seats a stock arc with
`DIVIDER_LEG_STRAIGHT` of tube still running straight into each collet, so the run spends what
the corner needs and no more of the collet. fluid-2 is the case, and its four figures are in
`_lines.py` beside the run: a forward budget too short for two stock arcs on axis at any lead
length, both corners at stock on a tilt well inside the skew, and the millimetres of that budget
still spare before the skew is the binding one.

Which leaves the division. A run's own numbers — `bend=`, `stub=`, `lead=` — buy the largest
radius its legs seat as drawn, and every run on the machine is authored at that number. But a
LEG is the distance from a port to the LANE its run comes about on, and a lane is a coordinate
this file picks inside a BAND: the aft band between the tray column and the core's front face,
the machine corridor between the shroud's roof and that same face, the strip between two bodies,
the bay between a tee and the tray behind it. Where a band has depth left, standing the lane
further off the port it turns from carries the whole corner up with it, and that is one number
in this file. Where the band is full — a line already on every `LINE_PITCH` of it, or a body
closing its far end — the lane is fixed and the run is a placement: the measurement to move is
the depth of the band. The binding leg's two endpoints print with the grade, which is where to
look.

Two runs a storey apart may hold the same lane. A lane is a Y, not a tube, and what forbids
sharing one is overlapping in the other two coordinates — so the aft band's far lane carries
fluid-13 at the barb plane and fluid-9 a stack pitch above it, while fluid-19 takes it in the
front column where neither of those two reaches.

`reach` bounds the centreline and nothing else. A run redrawn at it sweeps a wider tube through
different air; `lines-clear` and the routed clearances are what answer that, after the edit.
fluid-16 and fluid-22 pass each other across the bag strip, and both are drawn under what their
own legs seat because that gap is what the strip has.

## Port leads

A run has to be able to LEAVE its port. `scorecard.port_leads` gates that, at each tube port's
own bore along its own axis, for the stub `route` emits plus the tangent its first corner is
seated on — the same two reaches this kit uses to build the run. The body a port's own runs join
it to is held out, because a divider's outlet stands one `divider_reach()` off the collet it
feeds and a tee's run collet one `TEE_RUN_LEAD` off its, both by construction. A port with no run
yet is held to the full lead against everything, which is the useful direction: that is the state
a collet is in before anyone tries to route it, and the state four of them were in when a tray
was parked a millimetre in front of them.

## `BLOCKED`

Connections the pack does not carry, each recorded with the measurement that blocks it. They stay
counted against the `routed` axis and print on every run. Empty today: every fluid segment the
topology names is built, and what is left owes a body rather than a route.

## `CARRIES`

One run can answer for more than one connection. A union tee's two RUN ports face each other down
a single straight path, so the segments butted into them can be one piece of authored geometry —
the run takes an id of its own and `CARRIES` names the connections it satisfies. Empty today,
even though Y-G's run IS such a path: the two collets it joins stand `TEE_RUN_LEAD` off its own
two, so the fitting's body lies between them and there are two pieces of tube, not one. `CARRIES`
is for a tee a single length passes THROUGH.

## Running it

```
tools/cad-venv/bin/python enclosure_assembly.py
```

Per routed line: Ø, developed length, bend count and radius, and the tightest gap to a part it
does not terminate on. Per blocked line: the measurement. `routed` on the scorecard counts the
paths `_lines.py` builds. The runs render into `enclosure-assembly.step` — copper for the
refrigerant loop, white for the LLDPE the fluid and tap-water lines are drawn in.

Line clearance is reported, not gated. Port leads are gated.
