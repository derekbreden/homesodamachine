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

**Done** is mechanical, not a matter of opinion: *every gate green, and all four goal
axes at 100%*. Green gates alone are permission to build, not done — the same distinction
the board draws between "fab-ready" and "a tight, hand-routed board." The four goal axes
are worked in two waves: **placed + shaped are the current focus** (driven to 100% first);
**routed + held wait behind them**, rendered gray until the focus is met.

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

## Goals — the four axes

The board had one goal: take every connection off the autorouter onto deliberate hand
copper. The enclosure has four, one per thing every component owes. The first two are the
current **focus** (rendered live, green/yellow); the last two are **deferred** (rendered
gray) until the focus is met:

- **placed** *(focus)* — placement criteria are DEFINED in code and currently HELD.
  A component's intended position is written as measurements against the enclosure interior
  datum — e.g. "foam Y+ within 1 mm of the back wall, Z- within 10 mm of the floor, X-/X+
  within 1 mm of the side walls" — and the scorecard measures whether they hold. "Against
  the back-bottom", pinned to numbers. A component counts when it has rules *and* they hold;
  rules defined but violated are a visible drift; no rules yet is not-started. Rules are
  re-definable as the design iterates — authoring one, and holding it, are the milestones.
- **shaped** *(focus)* — real geometry, not a placeholder box or cylinder. A placeholder
  with the right *dimensions* is still a box; the real silhouette is what other parts must
  be packed against.
- **routed** *(deferred)* — every connection modeled as a real 3D path (bend radius, length,
  clearance), not two endpoints and an external graph. The denominator is both topologies —
  the fluid tube segments *and* the electrical runs (AC / DC / signal / low-voltage); a
  connection counts only once a real path exists.
- **held** *(deferred)* — a printed holder that fastens the component to the enclosure: a few
  bosses and screws, a tray-with-bosses that itself fastens, a wall capture, a shell facet.
  Not a free solid resting in a collision-checked void.

**Score by authorship, never by "it doesn't collide."** A bounding box that happens not to
overlap is the enclosure's version of the autorouter's accidentally-clean net — crediting
it would count the box-thinking this effort exists to remove as progress. So `shaped` and
`held` are read from what has actually been modeled and engineered (the registry), `placed`
from authored face-to-datum rules that must measurably hold, and `routed` from whether a
real path exists — never inferred from the mere absence of a clash.

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

The current focus is **placed + shaped to 100%**; `routed` and `held` are parked (gray)
until then. In the open, so coverage is never misread as done:

**Focus — placed + shaped:**

- **Author placement rules for the remaining components.** Three carry them today
  (foam-assembly, compressor-shroud, condenser+fan); the other 22 are not-yet-placed. Each
  earns a set of face-to-datum measurements that pin its intended position, and those must
  measurably hold. Rules iterate as the design moves — a redefinition is expected, not a
  failure.
- **Make the placeholders real.** Ten components are boxes/cylinders with real dimensions
  but not real geometry (every recently-sized connector, plus the condenser, MQ-6, drip-pan,
  moisture plate). Convert each to real STEP / engineered geometry.
- **SeaFlo real dimensions + a steeper funnel** — the live repack. The SeaFlo's true body
  is 80 × 72 × 187 (up from the modeled 75 × 60 × 175); it grows the pump-1 tower and, until
  the CO2 chain is lifted clear, clashes the regulator. The shape-aware version necks the
  funnel to the pump's real silhouette (not its bbox) to plunge it and pull the box back
  down — the canonical shapes-not-boxes exercise, now measured by the scorecard.
- **drip-pan** — the lone unsourced part (also fails `parts-sourced`): a printed pan with
  no CAD yet, dimensions estimated.

**Deferred — behind the focus:**

- **routed** is blocked on the **three unplaced valve-manifold trays** (source-select,
  bag-circuit, nozzle-gate). All 28 fluid segments live in them; the 28 electrical runs
  wait on the components being placed and held first.
- **held** — a printed holder for every internal component. Today only the through-wall
  bodies (wall + their own nut) and the display (shell facet) are held; every loose internal
  part floats. Each needs bosses, a cradle, or a tray that itself fastens.
- **assemblability + serviceability** — the enclosure's hardest constraint (assembly
  sequence, service withdrawal) has no executable check yet. It is a named requirement and a
  standing review question until the tooling to measure it exists — see *Assemblability and
  serviceability*.
