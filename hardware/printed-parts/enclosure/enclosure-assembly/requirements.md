# Enclosure requirements

The appliance's printable-and-assembleable requirements, in prose. The executable form
is [`scorecard.py`](scorecard.py) — computed from the placed geometry and printed at the
tail of every `enclosure_assembly.py` run, so the agent and a human read one verdict from
the same shapes. This file is the *why* behind each rule, the method that drives the box
to done, and the lessons already paid for. Modeled on the board's
[`requirements.md`](/hardware/pcb/pcba/requirements.md) + [`scorecard.ts`](/hardware/pcb/pcba/scorecard.ts).

## The verdict: gates + goals

Two kinds of requirement, split the way the board splits them:

- **GATE** — a manufacturability requirement that must hold to print and assemble the box
  as it stands. Binary. A failing gate is a design not cleared to build.
- **GOAL** — the realization work this whole effort exists to drive, reported as a
  `score` (0–100), not a gate — the box still models while it converts.

**Done** is mechanical, not a matter of opinion: *every gate green, and all six goal
axes at 100%* — and the numbers serve a standard past mechanical, stated in the next
section. Green gates alone are permission to build, not done — the same distinction
the board draws between "fab-ready" and "a tight, hand-routed board." The **focus** is
`bend-radius` and `mounted`, in that order — one gate, one goal, printed together at the
card's head — and every other goal axis (**placed, located, shaped, routed, held**)
renders gray behind them until the focus is met.

## The standard — the machine reads as meant

Gates prove the pack is legal. The standard is higher: **someone who opens this machine
believes a person meant it**. That is what the board's weeks of hand placement and routing
bought — the autorouter's traces all cleared, and none read as chosen — and it is the whole
reason this assembly is worked by hand. Legal is the floor; the distance from legal to
meant is the distance from packed to composed. The expectation of record: the two focus
figures at their targets carry roughly nine tenths of it.

- **bend-radius** carries the arrangement. It is the one number on the card that cannot be
  improved by appending anything: most corners are bound by where their run's two ends
  stand, so the grade is a measurement of the pack wearing a tube's units, and it rises
  only when bodies move somewhere better.
- **mounted** carries the commitment. An unfastened body is a position nobody decided; a
  component whose fastening feature is printed into another placed part is a decision made
  and kept.

Three rules of engagement follow from the standard rather than from any gate:

- **The envelope is fixed.** A box that can grow always has a legal answer, so the good
  answer never has to be found — reaching for depth is the autorouter's move in three
  dimensions. The pack is not full; it is finely subdivided. Room is made by spending the
  same volume unevenly — bodies nested close where nothing needs to turn, closer together
  and not further apart, with the freed millimetres pooled where a line has to bend.
- **Everything moves.** The arrangement is a draft until the focus says otherwise. A pose
  derived from a neighbour is legibility, not law: the derivation is a line in
  [`_contents.py`](_contents.py), and changing what it derives from is ordinary work.
  "X cannot move" is never a finding — it is the name of the next thing to move. A claim
  about room is made over a render of the region, never over a table
  ([`calibration/Fences.md`](/calibration/Fences.md) carries both disciplines).
- **Prefer a move to an instrument.** The tools to look already exist — the three
  elevations written beside the STEP, `tools/render/render-view.js` for any subset from
  any side, `tools/around.sh` to turn the whole pack on one axis and click a body by pixel,
  `fit.py`, this card. A session that builds another describer instead of moving a body has
  chosen the comfortable failure.

**The last tenth is unexplained variance.** Wherever function leaves a choice free — which
collet a line takes, which way a fitting clocks, which lane a run dresses to — the machine
reads meant when that freedom is spent to a rule the eye can find (parallel, mirrored,
flush, a shared pitch, shortest), and unconsidered when it is spent at random. The
recurring forms: two lines crossing where re-clocking a valve or swapping an assignment
would uncross them; a run stepping twice where once would do; parallel runs at three
different pitches; one fitting clocked off the angle its row shares; twin channels that do
not read as twins; 3 mm of margin against one wall and 40 against the other with nothing
using the 40. None of these costs room — the only input they need is noticing, which is
exactly why their absence reads as *missing any consideration*. The closing sweep on any
stretch of placement work: open the elevations, list every variance you cannot explain,
fix the ones no rule contests, and bring Derek the ties — the crossing whose uncrossing
would break a symmetry, the flush that fights a pitch. Judging a tie is Derek's; seeing it
is ours.

## Gates — permission to build

- **coverage** — every placed solid is declared in the `scorecard.py` registry. The
  registry carries each component's per-axis state; if a part can be added to the pack
  without declaring what it still owes, the goal scores are measured against the wrong
  universe. This gate makes the registry and the pack the same set.
- **pack-closes** — no two solids overlap. Two parts cannot occupy the same space. This
  is the one gate that also blocks the export today (see *Gating*).
- **lines-clear** — no routed tube drives through a part it does not terminate on, through a
  printed piece, or through another tube. The routed analogue of pack-closes: the tubes are
  `_lines` runs rather than registry components, so pack-closes never sees them. Blocks the
  export alongside it.
- **bend-radius** — every routed tube turns at or above the minimum radius of the STOCK it is
  drawn in. `lines-clear` says a tube's path is free of everything else; this says the path
  can be made out of that tube at all. A turn tighter than the stock takes buckles the inside
  wall, ovals the bore and then shuts it, and a collet a kink runs into stops sealing — as
  unbuildable as two solids overlapping, and invisible to every other check on this card,
  which read a swept solid and never ask what it took to sweep it. Each run carries two
  grades: `drawn`, the authored radius over the stock's minimum, and `reach`, the largest
  radius the run's own INTERIOR legs could seat (`_routing.leg_caps`). Both failing is a
  placement — the lane is too short to turn in at any legal radius and something either side
  of it has to move. A good `reach` is not a promise the run can be raised, though: every run
  is drawn at the most its own legs seat, and what caps most of them is a LEAD — the standoff
  between the fitting and the lane its run turns onto, which the approach stub cannot outrun
  without the close folding. That standoff is a routing number while the band the lane stands
  in still has depth, and a placement once the band is full; `tube-routing.md` carries the
  trade. The stock minimums live in `STOCKS`; two are sourced from datasheets and the LLDPE one
  is seeded, like the clearance floor.
- **clearance-floor** — every part-to-part gap is at least the floor, unless the pair is a
  declared intentional contact (a part resting on another's top, a vent reaching into a
  pan). Part-to-wall is *not* here — parts seat against walls by design; overlap there is
  pack-closes' job. This is the enclosure's IPC-courtyard analog: a real spacing standard,
  measured, not a raw overlap test.
- **port-leads** — every tube port has the straight a run off it needs. Body-to-body
  clearance says two parts do not touch; it never says a connector between them can be
  used, and a port is a hole with a direction. So each port's own bore is cast along its own
  axis for the stub a run leaves a fitting on plus the tangent its first corner is seated on
  — the two reaches `route` itself emits — and the cast has to reach. What it may end on is
  the body the port's own runs join it to, read off those runs' anchors rather than from
  prose, because a divider's outlet stands one leg-lead off the collet it feeds by design.
  Two trays a clean millimetre apart with their collets facing each other pass every other
  gate on this card and pass nothing a tube can be built through; this is the one that says
  so. Wires are not in it — a loom turns against its own insulation and asks no straight —
  and neither are stations PICKED on a placeholder box, which are claims about the box; both
  are still measured and still printed.
- **pieces-fit-bed** — each printed piece fits the H2C build envelope (325 × 320 × 320).
  A piece that overflows the bed cannot be printed; it is why the box splits into four.
- **seams-mate** — the printed pieces mate to a slide fit (piece∩piece under the slip
  tolerance). A seam that interferes will not assemble.
- **parts-sourced** — every component is a selected real part or a finished printed-part
  design. You cannot build what is not yet specified.

## Goals — the six axes

The board had one goal: take every connection off the autorouter onto deliberate hand
copper. The enclosure has six, one per thing every component owes. **mounted** is the live
one (green/yellow); the other five render gray behind it until the focus — it and the
`bend-radius` gate together — is met:

- **mounted** *(focus)* — the feature that fastens the component is printed INTO another
  placed part. The board is the case the rest is read against: four boss columns stand in
  the cold core's top cap, so the cap holds the board, and the board is mounted whether or
  not the cap itself is — the test is local, what fastens *this* one. Resting on a part is
  not mounted, however closely: the valve trays carry boss holders, but the holders are in
  the tray and the tray sits on the cap loose — print those holders into the cap the way
  the board's columns are and the trays are mounted, not before. Adhesive is not a fastener.
  What the printed feature IS does not matter, only that it PINS: a screw into a boss column,
  a nut bearing on a bored land, a taper thread made up in a bore, a rail pair taking a tray's
  haunches — and a joint may leave one axis free on purpose, as the drip pan withdraws along
  its rails. A feature that only LOCATES is not a joint (the foam in its floor pocket, the
  display let into its facet — nothing in either resists lifting the body out).
  `MOUNTED_BY` in `scorecard.py` names each component's carrier and `mount_features` states
  the printed feature the joint stands on, which `mount_audit` measures every build. A
  component absent from `MOUNTED_BY` is a joint still to design; one present whose measurement
  fails, or which has no measurement, reads ADRIFT and does not count.
- **placed** *(deferred)* — placement criteria are DEFINED in code and currently HELD.
  A component's intended position is written as measurements the scorecard checks, in three
  forms: **face-to-datum** — a body face within max_mm of the enclosure interior's same
  face (the foam's Y+ at the back wall, its Z− on the floor) —
  **part-to-part** (`near`) — the exact solid-to-solid gap to a named neighbor at most
  max_mm, measured on the real shapes, not their boxes (the condenser block riding one seam
  band over the shroud's roof) — and **part-to-part keep-out** (`clear`) — that
  gap at least min_mm, a working space held open on purpose. "Against the back-bottom",
  "stands on the shroud", and "leaves the machine corridor", pinned to numbers. A component counts
  when it has rules *and* they hold; rules defined but violated are a visible drift; no
  rules yet is not-started. Rules are re-definable as the design iterates — authoring one,
  and holding it, are the milestones.
- **located** *(deferred)* — every connector (tube *and* wire) has a POSITION **and a bore Ø** on
  the component: a point the scorecard confirms sits on the placed body's real surface — within
  a bore radius of an actual face, so an opening counts wherever the body has one (the free
  collet of an elbow, a connector on a populated board) and a point in the open air over a
  bounding box does not — with the body face it exits, the nominal bore of the line it carries,
  and what it mates to. A
  coordinate says *where* a line lands; the Ø says *what* fits there — the PCBA had both per
  pad (a position and a copper/drill size), and routing needs both here (a tube's bend and
  clearance depend on its diameter). A connection has no path until *both* its ends are
  located, so this is the precondition to `routed`. Positions are derived where the part
  documents its penetrations (a foam-shell penetration table, a sheet-metal generator's hole
  centers) and picked off the model where it doesn't; the Ø comes from the line or fitting the
  port carries (1/4" ACR copper = 6.35 mm, a 3/8" hose barb = 9.525 mm, a cable gland). A
  connector with no position yet is a visible `needs a position`, one still unsized a `needs a
  bore Ø` — never a silent gap. A component counts when it has ports *and* every one is
  positioned, on-surface, *and* sized. This is the `placed` discipline applied to the
  connections instead of the body — "against the wall" becomes "the suction stub is *here*,
  and it is 1/4" copper." The full inventory — every port's coordinate + bore — is emitted as
  a structured `ports[]` block in the scorecard sidecar, so the audit reads it directly. A part
  that carries no tube or wire at all (a passive body) is declared connector-free in
  `PASSIVE_NO_PORTS` and counts once; declaring the absence is the honest analogue of declaring
  a position, and it lets the axis reach 100% without inventing a port.
- **shaped** *(deferred)* — real geometry, not a placeholder box or cylinder. A placeholder
  with the right *dimensions* is still a box; the real silhouette is what other parts must
  be packed against.
- **routed** *(deferred)* — every connection modeled as a real 3D path (bend radius, length,
  clearance), not two endpoints and an external graph. The denominator is every topology the
  machine carries — the flavor manifold's fluid segments, the tap-water path, the carb-water
  riser, the CO2 path, the **sealed refrigerant loop** (compressor → condenser →
  drier/cap-tube → evaporator → compressor), *and* the electrical runs (AC / DC / signal /
  low-voltage). The four declared in `scorecard.py` rather than parsed from a table are there
  because no table owns them: `fluid-topology.md` is the beverage manifold downstream of the
  carbonator, and the water, CO2, riser and refrigerant paths all sit outside it. A
  connection counts only once a real path exists.
- **held** *(deferred)* — a printed holder that fastens the component to the enclosure: a few
  bosses and screws, a tray-with-bosses that itself fastens, a wall capture, a shell facet.
  Not a free solid resting in a collision-checked void. Looser than `mounted`: a tray whose
  own holders are not printed into what it sits on counts here and not there.

**Score by authorship, never by "it doesn't collide."** A bounding box that happens not to
overlap is the enclosure's version of the autorouter's accidentally-clean net — crediting
it would count the box-thinking this effort exists to remove as progress. So `shaped` and
`held` are read from what has actually been modeled and engineered (the registry), `placed`
from authored face-to-datum rules that must measurably hold, `located` from declared port
positions checked on-surface against the real body *plus* a declared bore for each,
`routed` from whether a real path exists, and `mounted` from `MOUNTED_BY` — the named part
whose printed geometry does the fastening — never inferred from the mere absence of a clash.

## Standards — provisional, awaiting ratification

The clearance floor and the intentional-contact set (`CLEARANCE_FLOOR`, `TOUCHING_OK` in
`scorecard.py`) are **seeded, not ratified**. The floor is a placeholder for FDM print
tolerance plus a hand's assembly margin. `TOUCHING_OK` is empty: no pair in this pack is
declared free to touch, and none needs to be — the tightest pair the clearance gate reports
stands well clear of the floor. Ratifying both — a defensible floor, and the set of pairs
allowed to touch once the pack carries a stack that wants one — is the first directed step.
Context-specific keep-outs grow from there as their own gates, the way the board grew its
gate-set. **Tube bend radius** is the first of them and it is now two: `port-leads`, which
asks whether a run can leave its fitting at all and found four collets in the loft with a
tray parked a millimetre in front of them and the water split's supply collet looking down
the lane at the PSU's back face; and `bend-radius`, which asks whether the turns it takes
after that can be made in the tube. The `STOCKS` minimums that second one grades against are
in the same state as the floor — the copper and the braided PVC are sourced, the 1/4" LLDPE
figure is seeded from what polyethylene tube of that size is commonly published at, and the
tube actually bought ratifies it. Still to come: **tool/wrench access** at each fastener,
**condenser airflow**.

## Assemblability — named, not yet measured

The board's traces are *fabricated*; no hand ever installs one. The enclosure's tubes,
pumps, and carbonator go in **by a hand, in an order**. A pack that is collision-free in
CAD can still be **physically unassemblable** — no order threads every part past the others
into place. This is the enclosure's antenna keepout: a real defect that a geometry-only
scorecard passes in silence, because the guard does not exist.

The requirement runs one way: parts go in. A unit that fails in the field is replaced with
another unit, and the failed one comes apart on the bench that built it, where teardown is
the method — so no in-place service envelope is held open anywhere in this pack, and reach
to a fitting on an assembled machine is not a constraint on placement.

It is named here as a first-class requirement while it is cheap to name — the
*deferred-is-not-removed* discipline (below) applied to a requirement, not just a connection:
an unwritten check that is *named and tracked* is a known gap; one that is simply absent is a
trap. Today it has **no executable check** — measuring it needs tooling the project does not
have yet (assembly-order reasoning, tool/hand swept-volume) — and the `held` axis is only its
nearest neighbor: `held` asks whether a holder exists, not whether a hand can seat that part
*in a valid order*. Until that tooling exists the requirement rides as a standing review
question on every placement and holder decision (*what installs before this*), and as the
first candidate to become a scored axis or gate once a check can compute it. Absent from the
number, present in the design.

## Gating

The scorecard **reports** every gate; today only **pack-closes** blocks the export — a
physically invalid pack must never be written. The rest report until the design reaches
them, then their gating turns on, one at a time (the board's stance: "every gate passes
today; a failing gate is a broken board, once gating is turned on"). A gate goes hard only
once the design can hold it green.

## Method — how the box reaches done

Carried over from how the board reached manufacturable (its two audit sessions and 400-commit
arc), the transferable discipline:

- **Build the checker before the thing.** The verdict is the hero. Every claim about the
  box is computed from the box's geometry, shown identically to agent and human.
- **One thing at a time, and defer without losing it.** Work one component or one
  connection; to clear a region, set aside (defer) what is in the way and add it to the
  end of the queue — tracked, counted, never silently dropped.
- **Correctness before tightness; grow to stay correct.** Let the box grow freely to
  satisfy real geometry — sufficient clearance beats any box size. Tighten only once the
  design is correct, and re-prove every gate on each tightening step.
- **Prove every check fires.** A guard that never triggers is worthless. When a new gate
  is added, inject the defect and watch it flag; add a control that must not. This is
  executable: [`scorecard_selftest.py`](scorecard_selftest.py) feeds each geometry gate a
  hand-built defect and a passing control, and the enclosure pre-commit runs it whenever the
  checker (`scorecard.py`) changes — so a refactor cannot quietly blind a gate.
- **The gate-set is living.** Every time something passes while broken, a new proven gate
  is added so it never can again.
- **Difficulty is a tripwire, not a grind.** When a step demands absurd contortions
  ("this tube needs five bends and a service hatch"), change the upstream free variable —
  move a component — rather than routing harder. For the enclosure, placement is the free
  variable and usually the real move.

## Lessons — already paid for

- **Model shapes, not bounding boxes.** A component's footprint is its real silhouette,
  not its axis-aligned box. The `shaped` axis credits real geometry precisely so
  box-thinking scores zero, and the clearance gate reads real solid distance, not box gap.
  What a short `shaped` axis costs is visible in this pack: the condenser block is the one
  placeholder, so the lane beside it and its gap to the foam assembly are both measured
  against a box, and both are provisional until the block is real.
- **Deferred is not removed.** A deferred item is set aside with its intent preserved and
  counted; a removed item is absent. The scorecard makes the line concrete: `routed` counts
  every connection the machine owes, placed or not, so each unrouted leg is a tracked gap
  rather than an absence, and `_lines.BLOCKED` — where a leg the pack itself
  prevents is named, with the measurement that prevents it — is empty. Never let a
  set-aside thing and a deleted thing wear the same label.
- **A clearance no gate holds is one that can be lost.** All ten of the cold core's
  penetrations open on one x, and both bodies of the refrigeration stratum span it; what
  keeps them clear is height, not lane — the corridor the ports open into is described and
  measured in [`../README.md`](/hardware/printed-parts/enclosure/README.md). Two things bound
  it now: the shroud's `clear foam-assembly` rule, and fluid-15, which crosses the machine
  along that corridor at the bag port's own height and brings `lines-clear` with it. Above the
  bag line and below the shroud's roof there is still nothing — `lines-clear` fires only on
  tubes that exist, and the refrigerant loop's three legs are unauthored, so a body placed into
  that upper band would pass every gate.

## The work queue — the focus, then what waits behind it

The current focus is **`bend-radius` green and `mounted` to 100%**; the other axes are
parked (gray), their inventories below maintained while they wait. In the open, so
coverage is never misread as done:

**What the axes are measured over.** The `coverage` gate makes the registry and the pack the
same set, and every axis below is a fraction of that set — so a focus driven to 100% says
that what is in the pack is placed, connected and real, not that the machine is packed. What
is outside it: the manifold's four pump-row tees — Y-C and Y-D in the front column, Y-F and
Y-G in the loft — and the CO2 chain that lands on the front panel. Each arrives owing every
axis at once. The manifold owes one more: its tray is a cradle and nothing else — it carries
no wall, so what stands one tray above another is the enclosure's to provide, and three of
them are stacked with nothing between them while two more stand side by side on a loft floor
that does not exist yet. [`_contents.py`](_contents.py)'s docstring carries the front column's
budget and the scans behind it; [`../README.md`](/hardware/printed-parts/enclosure/README.md)
is where the pack itself, and what is open about it, is described.

**placed + located + shaped:**

- **Placement rules — every component that carries rules holds them.** The foam assembly into
  the back-bottom corner by face-to-datum, seating on the seams rather
  than the walls; the compressor shroud on the floor at the front, centred across the machine,
  with a `clear` keep-out holding the machine corridor open at the cold core's port face; the
  condenser block by `near` the shroud it stands on plus a `clear` off the core; the display
  centred on the facet by two matched x rules and the letting-in of y− and z+; the funnel by
  z+ on the top wall; Zone B's deck and shelf each by `near foam-assembly`, the cap being the
  mount, plus the neighbours that bound its strip; Zone C's head column — three trays, three junctions, both
  pumps and the two pump-row tees — each by `near` the thing above, ahead of or beside it, the
  funnel's real underside, the tray's own coil crown, the strip a junction stands across, the
  barb a tee's run stands off, plus a `clear` on the condenser's
  intake lane they all stand in and a `clear` on the shroud's roof for the bodies at the
  column's bottom; and Zone C's LOFT — two trays and one divider — each by
  `near` the body it packs against and a `clear` on whatever of the water deck stands under it,
  because the deck beneath the loft is not level and a floor up there is a body and not a plane. A full `placed` axis is a property of this registry, not of the machine: each
  component that joins the pack earns its own measurements, and rules iterate as the design
  moves. A redefinition is expected, not a failure.
- **Locate every connector — one port short.** Every port carries a position *and* a bore Ø,
  and all but one sit on their body's real surface. The exception is the compressor shroud's
  mains gland: a coordinate on the body's bounding box that does not land on the body, reported
  **off-surface**, and the only thing standing between `located` and 100%. Positions are
  derived from the part's own record where one exists — the foam ports from the shell's own
  station names, carried into world through the pack's yaw so they follow both the shell's port
  layout and the pose, and the shroud's from its generator's hole centres carried through the
  same turn and seat. Where no record exists they are picks: the condenser's three are picks on
  a placed *box* and move when the block becomes real, and the display harness is provisional on
  the interior back face pending a viewer pick. Three bores are declared estimates pending
  teardown — the shroud's mains gland and earth stud, and the condenser's fan pigtail.
  `PASSIVE_NO_PORTS` is empty: every body in this pack carries at least one connector, so
  nothing reaches the axis by declaring an absence.
- **Make the last placeholder real.** The condenser+fan — a harvested donor block with its
  factory filter-drier — is the one component still packed as a box, and the only thing standing
  between `shaped` and 100%. Everything around it is packed against that box, so converting it
  to real geometry is what makes its neighbors' clearances mean what they say. Its shelf, ear
  pads and the two side grilles its crossing airflow needs are open.

**mounted + routed + held:**

- **mounted** — the queue is the complement of `MOUNTED_BY`: every component it does not
  name. Named: the five cap-column modules the deck mounts carry, the aft stand's two trays on
  the cap columns their own ears reach, the C14 on its two panel bosses, and the WALL
  SEQUENCE — the ASSE chain, the water split and the flow regulator — each held by a clamp
  collar cut into the top wall directly over it and drawn shut on one of the fitting's own
  round barrels by a single M3 across the collar's mouth. That joint is the pattern for every
  smooth-bodied fitting still loose: the barrel is the fastening surface a fitting already has,
  and the collar is printed into whatever placed part stands over it. Two things the pattern
  needs before it travels — a station whose band lies wholly inside one printed piece
  (`enclosure._dims().y_joint` cut the regulator's own feed collet in two, which is why its
  collar sits on the end it feeds), and a neighbour that will give the collar its section
  (the hopper's closed corner gave 5 mm of one basin edge for this one).
- **routed** spans the flavor manifold's fluid segments, the tap-water path, the carb-water
  riser, the CO2 path, the sealed refrigerant loop and the electrical runs. **Every fluid
  segment the topology names is authored**: the flavor tap from the water split to V-A, the
  whole shared section (source to channel split), BOTH bag circuits — each pair's two legs to
  its own junction and the one line that carries that reservoir's fill and draw across the
  machine to the core's own face — BOTH pump rows, and the two nozzle gates' runs out to the rear
  panel, which are the only lines the manifold sends out of the machine.
  `_lines.BLOCKED` is empty, so no connection is blocked by the pack as it stands. A run needs
  two ports to stand between, and most of what is left has one end on a body the pack has not
  placed — those wait on the body and come back with it. **The refrigerant loop's three legs
  are the exception**: compressor discharge → condenser, condenser outlet → evaporator inlet,
  evaporator outlet → compressor suction, every end located and on-surface. They wait only on
  their author. Paths are authored in [`_lines.py`](_lines.py) with the kit in
  [`_routing.py`](_routing.py); see [`tube-routing.md`](tube-routing.md).
- **held** — a printed holder for every component. Held: the foam assembly by the floor, which
  carries it while the seam posts fence it (unfastened by design); the display by the shell
  facet it is let into; the drip basin by its own rim on rails printed into the −X wall; the
  five shelf modules by the cap's own deck-mount columns; the rear-panel bodies by the wall
  their nuts clamp; and the wall sequence's three fittings by the top wall's own clamp collars.
  Loose: the compressor shroud, whose seat, plan register and capture bosses
  are open; the condenser block, whose shelf and ear pads are open; the funnel, whose attach
  mode is open; the discharge chain and the CO2 chain's two bodies, whose brackets are open;
  V-K, which rides the wide plate and so is held by it; and
  the whole of Zone C — five trays with nothing standing one off another, eight tube-hung
  junctions and both flavor pumps.
- **assemblability** — the enclosure's hardest constraint, the order a hand seats every part
  in, has no executable check yet. It is a named requirement and a standing review question
  until the tooling to measure it exists — see *Assemblability*.
