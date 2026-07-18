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
  A component's intended position is written as measurements against the enclosure interior
  datum — e.g. "foam Y+ within 1 mm of the back wall, Z- within 10 mm of the floor, X-/X+
  within 1 mm of the side walls" — and the scorecard measures whether they hold. "Against
  the back-bottom", pinned to numbers. A component counts when it has rules *and* they hold;
  rules defined but violated are a visible drift; no rules yet is not-started. Rules are
  re-definable as the design iterates — authoring one, and holding it, are the milestones.
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
  connection is a tracked `routed` gap (0/28, blocked on the unplaced valve-manifold
  trays); a removed path is simply not in the topology. Conflating the two is how the
  bib-gate tray lingered as a phantom — never let a set-aside thing and a deleted thing
  wear the same label.

## The work queue — the focus, then what waits behind it

The current focus is **placed + located + shaped to 100%**; `routed` and `held` are parked
(gray) until then. In the open, so coverage is never misread as done:

**Focus — placed + located + shaped:**

- **Author placement rules for the remaining components.** Four carry them today
  (foam-assembly, compressor-shroud, condenser+fan, source-select-tray); the other 14 are
  not-yet-placed. Each earns a set of face-to-datum measurements that pin its intended
  position, and those must measurably hold. Rules iterate as the design moves — a
  redefinition is expected, not a failure. The tray also exposes a vocabulary gap: its
  governing relations (seated on the compressor top, +X edge shared with the compressor's,
  V-B under the funnel drain) are part-to-part and port-to-port, which face-to-datum rules
  cannot express — they hold by construction in `_contents` until the rules language grows
  those forms.
- **Locate every connector (`located` 78%).** All 18 components carry full port sets — 59 ports
  (25 fluid, 6 refrigerant, 28 electrical), each with a position *and* a bore Ø — and 43 of them
  sit on their body's real surface. Positions are derived from the part's own record where one
  exists (foam penetrations, compressor holes, the CO2 fittings' flow-face centres), and Ø from
  the line or fitting the port carries.
  **16 ports read `off-surface` — a coordinate on the body's bounding box but not on the body:**
  all 10 of the PCBA's Ø-flagged edge connectors sit at the board's bbox top, ~10.5 mm above the
  plane the connectors stand on, so the `pcba.tsx` mapping needs its Z re-solved against the
  board's real top face; the 4 power-tray terminals, the display harness, and the compressor's
  AC gland are the provisional ones (device terminals not individually modelled, connector not
  in the STEP) that a viewer pick pins. A handful of electrical bores (glands, headers, looms)
  are noted estimates pending teardown. And the physical CO2 order (DERPIPE → check → regulator,
  which the ports follow) disagrees with the carbonator schematic (regulator → check) — a
  placement question, not a port one. The source-select tray's four boundary ports (V-A-I,
  V-B-I, V-C-O, V-D-O) are PROVISIONAL on the placeholder box — V-B-I directly under the funnel
  drain — and pin down with the tray design.
- **Make the placeholders real.** Two components are boxes with real dimensions but not real
  geometry: the condenser+fan (harvested donor block) and the source-select tray. Convert each
  to real STEP / engineered geometry.
- **source-select-tray** — the lone unsourced component (also fails `parts-sourced`): its four
  Beduan valves and two PP2308E dividers are purchased parts, but the printed carrier that
  holds them is undesigned — the box is seeded from the valve bodies, calipers pending. The
  tray design is what closes the gate.
- **Re-place the deferred front-column subsystems.** The water deck (SeaFlo pump, Multiplex
  BFP, drip pan + moisture plate, SeaFlo outlet check), the DIGITEN flow sensor, and both
  Kamoer pump assemblies are deferred from the pack while the source-select column settles —
  tracked here and in the topology, never dropped. Each returns with a placement that respects
  the tray's column and the funnel drop. The SeaFlo's true body is 80 × 72 × 187 (the banked
  reference geometry), larger than the placeholder it last packed as.

**Deferred — behind the focus:**

- **routed** spans the fluid segments, the sealed refrigerant loop, and the electrical runs
  (1/59 — the loop's discharge leg). Paths are authored in [`_lines.py`](_lines.py) with the kit
  in [`_routing.py`](_routing.py); see [`tube-routing.md`](tube-routing.md). The fluid path is
  blocked on the **three unplaced valve-manifold trays** (bag-circuit, pump-inlet tees,
  nozzle-gates) and the deferred pumps/water deck; segment 4 (funnel → V-B) waits only on the
  tray design giving V-B a real inlet. The electrical runs wait on the components being placed,
  located, and held first. Two of the loop's three legs are in `_lines.BLOCKED`, each with the
  measurement that blocks it: the liquid leg needs a 3.2 mm lateral jog against a 25.4 mm
  two-corner minimum (a condenser-pick move clears it), and the suction leg's corridor lanes
  miss by 3.4–8.5 mm — closable by a 45° offset pair at R 12.7, a corner the orthogonal kit
  cannot yet express.
- **held** — a printed holder for every internal component. Today only the through-wall
  bodies (wall + their own nut) and the display (shell facet) are held; every loose internal
  part floats. Each needs bosses, a cradle, or a tray that itself fastens.
- **assemblability + serviceability** — the enclosure's hardest constraint (assembly
  sequence, service withdrawal) has no executable check yet. It is a named requirement and a
  standing review question until the tooling to measure it exists — see *Assemblability and
  serviceability*.
