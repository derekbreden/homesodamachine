# Founder build-hour audit gap — does "~12 units/year" hold up?

*Recommendation for follow-up — written 2026-05-20, hourly-todo-filler agent.*

This is a strategic gap, not a hardware gap. Every other gap on the [`2026-05-19/`](../2026-05-19/) and [`2026-05-18/`](../2026-05-18/) lists asks "is the appliance ready?" This one asks a different question: **is the production plan ready?** The phrase "~12 units/year at solo build capacity" appears six times in [`marketing/target-market.md`](../../marketing/target-market.md) and is the structural anchor of every downstream business decision — the Founder Edition price, the four-year runway, the rings-of-trust ramp, the timing of Standard Edition opening, the revenue projection. The number is asserted; it has never been audited against the documented assembly procedures. If it is materially wrong in either direction, the entire plan downstream of it shifts.

## Why this matters now

Four claims in [`marketing/target-market.md`](../../marketing/target-market.md) rest on the 12-units-per-year throughput:

- **Pricing.** "$7,500, hand-built by the founder one at a time" — the price is justified by the founder's time and by the scarcity that "is real because the constraint is real" (target-market.md line 94). If the constraint isn't real — if the founder can ship meaningfully more or fewer than 12 units/year solo — the price reasoning wobbles in different directions.
- **Cadence.** "Roughly four years at solo build capacity" — this divides 50 by 12. A different throughput stretches or compresses the four-year run by the same ratio, and the Standard Edition open date moves with it.
- **Revenue projection.** "Founder Edition, 12 units/year ≈ $90,000 revenue" (target-market.md line 122). The number drives the founder's personal financial model — when to take a sabbatical (the "wowzers outcome", line 195), when to step away from the day job, what to expect in year one vs. year three.
- **Ring 1 plan.** "Ring 1 — the first 10 units go to people the founder knows directly... Pricing is whatever moves the unit. Probably $2,000–3,000" (target-market.md line 173). The ramp from ring 1 → ring 2 → ring 3 paces against the same throughput; if throughput drifts, every ring's calendar drifts.

The plan can survive a wrong estimate; it cannot survive a wrong estimate that nobody knows is wrong. The cost of validating this *before* publishing Founder Edition pricing to a stranger is keeping a build-hour log on unit 001; the cost of validating it *after* and discovering capacity is half of plan is a public refund cycle.

## What the assembly docs actually contain

The eleven documents in [`hardware/assembly/`](../../hardware/assembly/) total roughly 1,650 lines of repeatable procedure. The five top-of-funnel docs ([`pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md), [`cold-core.md`](../../hardware/assembly/cold-core.md), [`refrigerant-loop.md`](../../hardware/assembly/refrigerant-loop.md), [`internal-plumbing.md`](../../hardware/assembly/internal-plumbing.md), [`electronics-shelf.md`](../../hardware/assembly/electronics-shelf.md)) were read in full for this audit; the remaining six were sampled at the Scope + Procedure-summary level for step count and complexity.

What's there is qualitatively heavy. To sketch the shape without inventing numbers:

- **Pressure vessel.** Four hand-tapped 1/4" NPT ports per vessel, two laser welds plus a tack-weld for the internal float rod, a hydro test with hold-time, a citric-acid passivation soak, then post-passivation install of four elbows + sparge stone + PRV. [`pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) has five named "Open items" before unit 1 ships, including the hydro pass/fail criterion, the failure-handling decision tree, and end-to-end recipe validation on 316L production stock (the most recent recipe was practiced on 304L).
- **Cold core.** Single-layer copper coil wound around a printed mandrel and transferred to the vessel, two foam-cap pours, twelve heat-set inserts pressed into the outer shell, body-side install of vessel + two reservoirs + three copper plugs + every routed penetration, the main body foam pour, post-cure trim, and final 12-screw cap assembly over a TPU gasket. Cure time is wall-clock; the trim cannot happen until cure completes. Four named open items including foam pour parameters and trim method.
- **Refrigerant loop.** Described in its own doc as "half a day of work end-to-end" and "the most safety-critical procedure in the build" — venting factory R-600a, two brazes under continuous argon, a vacuum hold, mass-metered recharge, first run-up + leak walk. Recharge mass for the new larger evap coil is explicitly undetermined and will iterate on the first units.
- **Electronics shelf.** Pure bench, but dense — heat-sets, soldered JST headers on each of ~10 modules, AC distribution staged with three Wagos and labeled pigtails, DC distribution staged, eight modules mounted, six inter-module JST harnesses crimped + plugged, nine SIG pigtails staged for sensor termination, pre-power continuity + isolation check. Four named open items including the shelf-frame CAD itself.
- **Enclosure mechanical, internal plumbing, wiring, faucet + umbilical, firmware + commissioning, acceptance + 8-hour burn-in, finish/pack/ship.** Each is detailed and procedural; [`internal-plumbing.md`](../../hardware/assembly/internal-plumbing.md) names its own 12-valve / 10-Y-divider / 2-pump flavor manifold as "the bulk of the bench labor."

Plus per-unit work that isn't in those eleven docs:

- **Parts kitting + receiving QC.** The per-build BOM crosses many ASINs from Amazon plus OnlineMetals (MTRs required), SendCutSend laser cuts, and harvested ice maker teardown. Each batch needs a receive-and-stage pass.
- **Printed-part production.** Foam shell, foam caps, cap lids, copper plugs, two reservoirs, pump cartridge, electronics shelf frame, back panel, enclosure walls, faucet shell, nameplate plaque, TPU gaskets. Mostly passive print farm but slicing, plate swap, supervision, and reprints aren't free.
- **First-of-kind rework headroom.** No yield assumption is declared anywhere in the docs. The hydro pass/fail and failure-handling questions in [`pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) are open; brazing rework is explicitly "redo the sequence."
- **Per-build documentation.** Per-serial test log required by [`acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md), nameplate sign-off + customer docs by [`finish-pack-ship.md`](../../hardware/assembly/finish-pack-ship.md), install-consult prep notes per unit.

And the founder is doing things beyond per-unit assembly:

- **Marketing video capture + posting.** [`marketing/target-market.md`](../../marketing/target-market.md) line 240–260 makes this explicit: "the founder isn't a stopgap while the brand gets built; he *is* the product for the first 50." Video is "the discovery mechanism." If the founder doesn't ship video, the rings don't fill.
- **Pre-sale + ring-1/ring-2 sales conversations.** "At 10 units/year, every sale is a conversation."
- **Post-sale customer support.** Founder Edition includes "personal install consultation" and implicitly the relationship downstream of that. Every fielded unit adds a long tail of follow-up.
- **Bookkeeping, taxes, supplier management, shipping logistics, returns.** Solo-proprietor overhead.
- **Design iteration.** There is no separate engineering team. Every open item in every assembly doc is future founder labor.

The shape of the work is heavy, multi-day per unit, with several wall-clock-bounded steps (foam cure, burn-in, refrigerant-loop single-session sequencing) that cannot be parallelized away. The shape supports a craft-pace operation. Whether that pace matches 12/year, 8/year, or 18/year is the question the docs cannot answer on their own.

## What the answer to "is 12/year right" actually looks like

It looks like measurement, not a counter-estimate. A bottom-up estimate from documentation is exactly the kind of pattern-matched number that should not stand in for data. The correction is to instrument the real builds.

### Layer 1: instrument unit 001 (and 002 and 003)

Start a build-hour log on unit 001 — a single text file at [`hardware/build-hour-log.md`](../../hardware/) or per-serial under [`logs/<serial>/`](../../logs/) (the per-serial directory is already called for by [`finish-pack-ship.md`](../../hardware/assembly/finish-pack-ship.md)). Each build session adds one entry; the log is append-only.

What to capture per entry:

- Date / weekend range and which assembly-doc step was worked.
- Operator-estimated active hours for the session, recorded coarsely.
- Anything that was rework or first-of-kind learning, separately from steady-state activity, so the steady-state number can be recovered from the total.
- Anything that *blocked* — parts not arrived, foam not cured, partner needed the kitchen, day-job spillover.

Three units' worth of data is enough to ground the 12/year claim or correct it. Per-session journaling is the smallest practical instrumentation that produces real numbers; the log entry itself takes a fraction of the build session.

### Layer 2: identify the bottlenecks before scaling

A real number from Layer 1 lets the founder see which step actually dominates and where leverage is. The candidates are already visible qualitatively from the docs:

- **Vessel-batch tap fixturing.** [`hardware/tapping-plan-2026-05-03.md`](../../hardware/tapping-plan-2026-05-03.md) is a single-use Baltic-birch fixture. A reusable batch fixture for the 10-vessel stock is called out as a downstream design step in [`pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) "Open items §1" but not yet built. Forty hand-tapped NPT holes per batch of ten vessels is the single most repetitive operation in the production procedure.
- **Pour-foam jig with pre-measured kit components.** Three separate pours per unit with shared consumables. A dedicated foam-bench with pre-staged kit components removes some setup/teardown per pour.
- **Pre-built electronics shelves on hand.** Pure bench work, shelf-stable, parallel to in-chassis work. The shelf moves out of the build-day critical path if the founder batches four at a time on a separate weekend.
- **Pre-bagged faucet-and-umbilicals.** Same logic — bagged sub-assembly, small, shelf-stable.

None of these block unit 1. They are the answer to "how do we grow throughput without burning the founder out," which is a different question from "is current throughput what was claimed."

### Layer 3: tier the public-facing plan against the real number

Once Layer 1 produces a measured throughput after the first few units:

- If the measurement is roughly consistent with 12/year, [`marketing/target-market.md`](../../marketing/target-market.md) is approximately right and the 12 number should be footnoted as validated rather than estimated.
- If the measurement is meaningfully below 12/year, the four-year run, the revenue projection, and the Standard Edition open date all stretch by the same ratio. The Founder Edition price arguably goes *up*, not down, since the scarcity is then more real. The internal-plan ring-1/ring-2 friend-and-family pricing of $2,000–3,000 doesn't change — those numbers are time-budget-independent.
- If the measurement is meaningfully above 12/year, Standard Edition opens sooner than four years. The scarcity story in target-market.md needs revision. The bus-factor risk concentrates because more units are in the field per unit of time.
- If the measurement is well below 12/year, the Founder Edition becomes a multi-decade craft practice rather than a four-year run. That is exactly the "yay outcome" from target-market.md line 192–194 ("twenty units a year, supplier relationships stable, design maturing"). It is not failure; it is a different plan. But the 50-units-in-four-years claim should not stand against a smaller real number.

### Layer 4: name the bus factor explicitly

The plan's single-builder design is a feature for ring 1 and ring 2 — the founder is the brand. It is a hazard for ring 3 and beyond, and for any in-field unit that needs warranty service. [`business/incorporation.md`](../../business/incorporation.md) and [`marketing/target-market.md`](../../marketing/target-market.md) both describe the founder-as-builder model but neither names the bus factor explicitly or commits to a continuity stance. Founder illness, day-job pressure, family events, single-vessel scrap, supplier failure, and in-field warranty events on delivered units all compress throughput in ways the plan does not currently absorb. The right answer probably isn't "hire help" — that breaks the Founder Edition story. The right answer is closer to a written-down successor stance: who finishes the current half-built unit if the founder is unavailable, where do customers reach someone during that window, where do the build instructions and supplier contacts live such that a friend with hands could step in. Not staffing; documentation against the bus.

Adjacent gap, worth its own file: [`workshop-as-factory-gap`](../2026-05-19/workshop-as-factory-gap.md) flags the residential-structure-as-factory liability surface; this gap flags the founder-as-factory continuity surface. Both are the same shape of problem — a hidden dependency on a thing that wasn't named as load-bearing.

## What I'd ask the project owner to decide

In order of decreasing urgency:

1. **Start the build-hour log on unit 001.** Single text file, append-only, coarse entries. Captures the data that will validate or correct the 12/year claim. Every downstream business decision that rests on that number depends on this log existing.
2. **Footnote 12/year in [`marketing/target-market.md`](../../marketing/target-market.md) as estimated, not committed.** A one-line addition: *"This estimate is the founder's working assumption; it will be validated against actual build hours on units 001–003 and revised if needed."* The footnote costs nothing to the buyer narrative and protects against a public-revision embarrassment later.
3. **Identify which steps to batch first.** Electronics shelf and faucet-and-umbilical are the obvious candidates — pure bench, shelf-stable, parallel to in-chassis work. The next time the founder is staging an order, doubling up lets two of each be built in one bench session.
4. **Build the vessel-tap batch fixture before scale.** [`pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) "Open items §1" is already on the list; this gap promotes it from production-procedure cleanup to throughput-gating fixture.
5. **Budget the marketing-video work separately from the per-unit build.** Whether that means a fixed cadence (one short per week, one per month) or a sprint model is a founder call, but treating video time as "found time around the build" is the failure mode this gap is warning about. Same for ring-1/ring-2 sales conversation time and post-sale support time. None of these are free.
6. **Name the bus factor explicitly somewhere.** A short paragraph in [`business/incorporation.md`](../../business/incorporation.md) or [`marketing/target-market.md`](../../marketing/target-market.md) acknowledging that the founder-as-factory model has a single point of failure, and pointing to whatever continuity stance exists (or naming the lack of one).

## Files this recommendation should propagate into when actioned

- New file [`hardware/build-hour-log.md`](../../hardware/) — append-only per-build-session journal, populated unit by unit starting with unit 001.
- [`marketing/target-market.md`](../../marketing/target-market.md) — footnote the 12/year claim as a working estimate; once units 001–003 are logged, revise the number and the four-year-run language to reflect what was measured. Update the revenue projection consistently.
- [`hardware/assembly/pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) "Open items §1" — promote the batch tap-fixture from "downstream design step" to a named throughput-gating deliverable.
- [`hardware/assembly/electronics-shelf.md`](../../hardware/assembly/electronics-shelf.md) and [`hardware/assembly/faucet-and-umbilical.md`](../../hardware/assembly/faucet-and-umbilical.md) — add a note that these sub-assemblies are batch candidates, intended to be pre-staged rather than built one-per-build-day.
- [`business/incorporation.md`](../../business/incorporation.md) — bus-factor paragraph + pointer to whatever continuity stance exists.
- [`marketing/target-market.md`](../../marketing/target-market.md) "Open questions" — add a sixth open question: *"6. Real per-unit build hours, validated against units 001–003. Until measured, all throughput and revenue claims are estimates."*

---

*This recommendation is the work of an hourly background agent. The argument is structural: "~12 units/year" is the load-bearing throughput claim under Founder Edition pricing, the four-year run, the rings-of-trust pacing, and the revenue projection; it has never been audited; the right correction is measurement, not a counter-estimate; the smallest practical instrumentation is a build-hour log starting on unit 001. The qualitative read of the eleven assembly docs (heavy, multi-day per unit, several wall-clock-bounded steps, multiple still-open procedural questions before unit 1 ships) supports the urgency of measuring rather than supplying any specific counter-number.*
