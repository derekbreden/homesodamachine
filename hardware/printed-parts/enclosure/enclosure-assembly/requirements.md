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

**Done** is mechanical, not a matter of opinion: *every gate green, and all five goal
axes at 100%*. Green gates alone are permission to build, not done — the same distinction
the board draws between "fab-ready" and "a tight, hand-routed board." The five goal axes
are worked in two waves: **placed + located + shaped are the current focus** (driven to
100% first); **routed + held wait behind them**, rendered gray until the focus is met.

## Gates — permission to build

- **coverage** — every placed solid is declared in the `scorecard.py` registry. The
  registry carries each component's per-axis state; if a part can be added to the pack
  without declaring what it still owes, the goal scores are measured against the wrong
  universe. This gate makes the registry and the pack the same set.
- **pack-closes** — no two solids overlap. Two parts cannot occupy the same space. This
  is the one gate that also blocks the export today (see *Gating*).
- **clearance-floor** — every part-to-part gap is at least the floor, unless the pair is a
  declared intentional contact (a part resting on another's top, a vent reaching into a
  pan). Part-to-wall is *not* here — parts seat against walls by design; overlap there is
  pack-closes' job. This is the enclosure's IPC-courtyard analog: a real spacing standard,
  measured, not a raw overlap test.
- **pieces-fit-bed** — each printed piece fits the H2C build envelope (325 × 320 × 320).
  A piece that overflows the bed cannot be printed; it is why the box splits into four.
- **seams-mate** — the printed pieces mate to a slide fit (piece∩piece under the slip
  tolerance). A seam that interferes will not assemble.
- **parts-sourced** — every component is a selected real part or a finished printed-part
  design. You cannot build what is not yet specified.

## Goals — the five axes

The board had one goal: take every connection off the autorouter onto deliberate hand
copper. The enclosure has five, one per thing every component owes. The first three are the
current **focus** (rendered live, green/yellow); the last two are **deferred** (rendered
gray) until the focus is met:

- **placed** *(focus)* — placement criteria are DEFINED in code and currently HELD.
  A component's intended position is written as measurements the scorecard checks, in three
  forms: **face-to-datum** — a body face within max_mm of the enclosure interior's same
  face ("foam Y+ within 1 mm of the back wall, Z- within 10 mm of the floor") —
  **part-to-part** (`near`) — the exact solid-to-solid gap to a named neighbor at most
  max_mm, measured on the real shapes, not their boxes ("the assembly's wall tops ride
  one clearance under the display body") — and **part-to-part keep-out** (`clear`) — that
  gap at least min_mm, a working space held open on purpose. "Against the back-bottom",
  "pressed to the display", and "leaves the channel", pinned to numbers. A component counts
  when it has rules *and* they hold; rules defined but violated are a visible drift; no
  rules yet is not-started. Rules are re-definable as the design iterates — authoring one,
  and holding it, are the milestones.
- **located** *(focus)* — every connector (tube *and* wire) has a POSITION **and a bore Ø** on
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
- **shaped** *(focus)* — real geometry, not a placeholder box or cylinder. A placeholder
  with the right *dimensions* is still a box; the real silhouette is what other parts must
  be packed against.
- **routed** *(deferred)* — every connection modeled as a real 3D path (bend radius, length,
  clearance), not two endpoints and an external graph. The denominator is all three
  topologies — the fluid tube segments, the **sealed refrigerant loop** (compressor →
  condenser → drier/cap-tube → evaporator → compressor), *and* the electrical runs (AC / DC /
  signal / low-voltage); a connection counts only once a real path exists.
- **held** *(deferred)* — a printed holder that fastens the component to the enclosure: a few
  bosses and screws, a tray-with-bosses that itself fastens, a wall capture, a shell facet.
  Not a free solid resting in a collision-checked void.

**Score by authorship, never by "it doesn't collide."** A bounding box that happens not to
overlap is the enclosure's version of the autorouter's accidentally-clean net — crediting
it would count the box-thinking this effort exists to remove as progress. So `shaped` and
`held` are read from what has actually been modeled and engineered (the registry), `placed`
from authored face-to-datum rules that must measurably hold, `located` from declared port
positions checked on-surface against the real body *plus* a declared bore for each, and
`routed` from whether a real path exists — never inferred from the mere absence of a clash.

## Standards — provisional, awaiting ratification

The clearance floor and the intentional-contact set (`CLEARANCE_FLOOR`, `TOUCHING_OK` in
`scorecard.py`) are **seeded, not ratified**. The floor is a placeholder for FDM print
tolerance plus a hand's assembly margin; the contact set is read off the pack's deliberate
stacks. Ratifying both — a defensible floor, the exact set of pairs allowed to touch — is
the first directed step. Context-specific keep-outs grow from there as their own gates, the
way the board grew its gate-set: **tube bend radius** at each port, **tool/wrench access**
at each fastener, **condenser airflow**, service-withdrawal envelopes.

## Assemblability and serviceability — named, not yet measured

The board's traces are *fabricated*; no hand ever installs one. The enclosure's tubes,
pumps, and carbonator go in **by a hand, in an order**, and come back out for service. A
pack that is collision-free in CAD can still be **physically unassemblable** — no order
threads every part past the others into place — or serviceable only by tearing down half the
machine to reach one fitting. This is the enclosure's antenna keepout: a real defect that a
geometry-only scorecard passes in silence, because the guard does not exist.

It is named here as a first-class requirement while it is cheap to name — the
*deferred-is-not-removed* discipline (below) applied to a requirement, not just a connection:
an unwritten check that is *named and tracked* is a known gap; one that is simply absent is a
trap. Today it has **no executable check** — measuring it needs tooling the project does not
have yet (assembly-order reasoning, tool/hand swept-volume, service-withdrawal envelopes),
and the `held` axis is only its nearest neighbor: `held` asks whether a holder exists, not
whether a hand can seat that part *in a valid order* or free it for service without a
teardown. Until that tooling exists the requirement rides two ways — as a standing review
question on every placement and holder decision (*what installs before this; what must come
out to service it*), and as the first candidate to become a scored axis or gate once a check
can compute it. Absent from the number, present in the design.

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
  not its axis-aligned box. The funnel that necks at a pump's bounding box — topped by two
  thin outlet elbows — abandons the clear column beside them and goes shallow; measured
  against the real shape it plunges. The `shaped` axis credits real geometry precisely so
  box-thinking scores zero, and the clearance gate reads real solid distance, not box gap.
- **Deferred is not removed.** A deferred item is set aside with its intent preserved and
  counted; a removed item is absent. The scorecard makes the line concrete: a deferred
  connection is a tracked `routed` gap, each waiting or blocked entry counted against the
  axis; a removed path is simply not in the topology. Conflating the two is how the
  bib-gate tray lingered as a phantom — never let a set-aside thing and a deleted thing
  wear the same label.

## The work queue — the focus, then what waits behind it

The current focus is **placed + located + shaped to 100%**; `routed` and `held` are parked
(gray) until then. In the open, so coverage is never misread as done:

**Focus — placed + located + shaped:**

- **Author placement rules for the remaining components.** Twelve carry them today
  (foam-assembly, compressor-shroud, condenser+fan by face-to-datum; the source-select
  assembly stood a bag-line fall corridor ahead of the cold core's front face by `clear`; the
  hopper funnel by z+; the bag-circuit assembly by `near` the source-select tray its
  stacking walls carry — another declared contact — plus `clear` keep-outs holding the
  floor stratum open under its own floor; the nozzle-gate assembly by `near` the same tray
  plus the inset off the +X wall; pump-a by `near` the bag tray's front columns
  plus a `clear` keep-out holding the funnel drain's fall corridor open over its head;
  pump-b by `near` its row neighbor plus a `clear` keep-out ahead of the source-select
  east bank its elbows thread past; both pump-inlet tees by `near` the source bank they
  hang off; the ASSE 1022 assembly by `near` the rear bulkhead it protects, a drip BAND on
  the cold core (`near` says the vent still reaches down toward the pan's ground, `clear`
  says it stops a pan's depth above it), a keep-out off the shelf row, and the axial room
  its barb keeps for the stiff 3/8" hose;
  all measured on the real solids); the other 19 are
  not-yet-placed. Each
  earns a set of measurements that pin its intended position, and those must
  measurably hold. Rules iterate as the design moves — a redefinition is expected,
  not a failure.
- **Locate every connector (`located` 84%).** All 31 components carry full port sets — 90 ports
  (56 fluid, 6 refrigerant, 28 electrical), each with a position *and* a bore Ø — and 69 of them
  sit on their body's real surface. Positions are derived from the part's own record where one
  exists (foam penetrations, compressor holes, both trays' elbow collet centres measured off
  their built assemblies, the pumps' outlet-elbow collets carried through their lying pose,
  the funnel drain in the funnel's own frame, the ASSE 1022 chain's three terminals stacked
  along its flow axis), and Ø from the line or fitting the port carries.
  **21 ports read `off-surface` — a coordinate on the body's bounding box but not on the body:**
  13 on the PCBA, whose Ø-flagged edge connectors sit at the board's bbox top, ~10.5 mm above the
  plane the connectors stand on, so the `pcba.tsx` mapping needs its Z re-solved against the
  board's real top face; the 3 power-tray terminals, the 3 DC-distribution terminals, the
  foam's CO2 top entry and the compressor's
  AC gland are the provisional ones (device terminals not individually modelled, connector not
  in the STEP) that a viewer pick pins. A handful of electrical bores (glands, headers, looms)
  are noted estimates pending teardown.
- **Make the last placeholder real.** The condenser+fan (harvested donor block) is the one
  component still packed as a box. Convert it to real STEP geometry.
- **Re-place the deferred front-column subsystems.** The rest of the water deck (SeaFlo pump,
  its outlet check, drip pan + moisture plate), the DIGITEN flow sensor, and the
  CO2 chain's GASHER check + WR1110 regulator (the physical CO2 order also disagrees with
  the carbonator schematic — DERPIPE → check → regulator vs regulator → check) are
  deferred from the pack while the front column settles — tracked here and in the
  topology, never dropped. Each returns with a placement that respects the tray stack at
  the cold core, the pump row ahead of it, and the funnel drop. What stays open: the band
  under the pump row down to the floor-stratum tops (~34 mm tall), the slab ahead of the
  row's front faces, and the ±X columns beside it. The SeaFlo's true body is 80 × 72 × 187
  (the banked reference geometry), larger than the placeholder it last packed as, and
  none of those three volumes takes it — it needs a lane of its own found for it.
  The ASSE 1022 assembly is placed, provisionally: it lies along X in the **service bay's
  aft strip**, between the electronics shelf's back edge and the rear-panel bodies reaching
  in from the wall, yawed so its 1/4" PTC inlet stands 50.8 mm off the water bulkhead's
  inboard mouth and its 3/8" barb faces the strip's open west end. Its vent hangs over the
  foam-cap top, which is the pan's ground in this bay: the drip pan + moisture plate sit on
  the cap under the stub's tip in a 70 × 50 footprint measured clear, and the stub is cut to
  that drop. Its discharge hose leaves the strip's west end for the SeaFlo and V-A's tap
  point, both still unplaced. Placement and envelope both move again: the pack is sparse, and
  the chain's 123.5 × 33 × 41.3 is the reference model's spec-sheet arithmetic rather than
  the four acquired parts measured.

**Deferred — behind the focus:**

- **routed** spans the fluid segments, the sealed refrigerant loop, and the electrical runs
  (19/59 — the loop's discharge and liquid legs in copper, the junction column's four
  straight collet-to-tee legs, the six pump-discharge divider legs and stems, the two
  nozzle-outlet runs to the rear bulkheads, the hopper drain, and both bag reservoir lines).
  Paths are
  authored in [`_lines.py`](_lines.py) with the kit in [`_routing.py`](_routing.py); see
  [`tube-routing.md`](tube-routing.md). All three valve-manifold trays and both pump-discharge
  dividers stand placed with every boundary port located — the fluid path waits on the SeaFlo
  the ASSE 1022's discharge hose lands on, and on the manifold's remaining legs. The hopper
  funnel places in
  [`_contents.py`](_contents.py) alongside the panel bodies, so segment 4 anchors on its own
  drain. The on-tray seats (3/5–8, 14/16, 24/26) are interior to their assemblies and still
  count against the axis until modeled. The electrical runs wait on the components being
  placed, located, and held first. `_lines.BLOCKED` is empty: no connection is blocked by the
  pack as it stands, so every unrouted one waits on its author or on a body not yet placed.
  refrig-3 is simply unauthored: its corridor
  stands open (the source tray's central span stops short of the cold-core face at the evap
  ports, and the band under the ASSE 1022's body carries it the rest of the way — a cast from
  the compressor's suction port runs its full length unobstructed), so it waits only on its
  author.
- **held** — a printed holder for every internal component. Today only the through-wall
  bodies (wall + their own nut) and the display (shell facet) are held; every loose internal
  part floats. Each needs bosses, a cradle, or a tray that itself fastens.
- **assemblability + serviceability** — the enclosure's hardest constraint (assembly
  sequence, service withdrawal) has no executable check yet. It is a named requirement and a
  standing review question until the tooling to measure it exists — see *Assemblability and
  serviceability*.
