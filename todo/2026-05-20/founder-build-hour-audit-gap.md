# Founder build-hour audit gap — does "~12 units/year" hold up?

*Recommendation for follow-up — written 2026-05-20, hourly-todo-filler agent.*

This is a strategic gap, not a hardware gap. Every other gap on the [`2026-05-19/`](../2026-05-19/) and [`2026-05-18/`](../2026-05-18/) lists asks "is the appliance ready?" This one asks a different question: **is the production plan ready?** The phrase "~12 units/year at solo build capacity" appears six times in [`marketing/target-market.md`](../../marketing/target-market.md) and is the structural anchor of every downstream business decision — the Founder Edition price, the four-year runway, the rings-of-trust ramp, the timing of Standard Edition opening, the revenue projections. The number is asserted; it has never been audited against the documented assembly procedures. If it is materially wrong in either direction, the entire plan downstream of it shifts.

## Why this matters now

Four claims in [`marketing/target-market.md`](../../marketing/target-market.md) rest on the 12-units-per-year throughput:

- **Pricing.** "$7,500, hand-built by the founder one at a time" — the price is justified by the founder's time and by the scarcity that "is real because the constraint is real" (target-market.md line 94). If the constraint isn't real — if the founder can ship 25 units/year solo, or 8 units/year — the price reasoning wobbles in different directions.
- **Cadence.** "Roughly four years at solo build capacity" — 50 units ÷ 12/year = 4.17 years. At 8/year it's 6.25 years; at 6/year it's 8.3 years and Founder Edition becomes a lifetime project. At 18/year it's 2.8 years and Standard Edition opens sooner than the brand can absorb.
- **Revenue projection.** "Founder Edition, 12 units/year ≈ $90,000 revenue" (target-market.md line 122). The number drives the founder's personal financial model — when to take a sabbatical (the "wowzers outcome", line 195), when to step away from the day job, what to expect in year one vs. year three.
- **Ring 1 plan.** "Ring 1 — the first 10 units go to people the founder knows directly... Pricing is whatever moves the unit. Probably $2,000–3,000" (target-market.md line 173). Ring 1 takes ~10 months at 12/year, ~15 months at 8/year, ~20 months at 6/year. The ramp to ring 2 and beyond stretches accordingly.

The plan can survive a wrong estimate; it cannot survive a wrong estimate that nobody knows is wrong. The cost of doing this audit *before* publishing Founder Edition pricing to a stranger is one weekend of bottom-up estimation; the cost of doing it *after* and discovering capacity is half of plan is a public refund cycle.

## What I did: bottom-up labor estimate from the assembly docs

The 11 documents in [`hardware/assembly/`](../../hardware/assembly/) total ~1,650 lines of repeatable procedure. The five top-of-funnel docs ([`pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md), [`cold-core.md`](../../hardware/assembly/cold-core.md), [`refrigerant-loop.md`](../../hardware/assembly/refrigerant-loop.md), [`internal-plumbing.md`](../../hardware/assembly/internal-plumbing.md), [`electronics-shelf.md`](../../hardware/assembly/electronics-shelf.md)) were read in full; the remaining six were sampled at the Scope + Procedure-summary level for step count and complexity.

The estimate below is steady-state per-unit *active* labor, not wall-clock and not first-unit. Steady-state means: fixturing exists, the founder has run each step at least three times, no first-of-kind weld-recipe debugging, no foam-cure surprises, no parts that arrived wrong. Active means: the hours of hands-on work — the citric-acid soak's 30 min and the foam pour's hours of cure time are not active hours, but the operator's other-step parallelism during those waits is also not free in a solo shop.

Numbers are deliberately rounded to the nearest 30 min — the underlying procedure docs aren't tight enough yet to defend 15-min precision, and rounding hides the false certainty.

| Step | Doc | Active hours/unit (steady-state) | Wall-clock notes |
|---|---|---|---|
| Pressure vessel (4 NPT taps + 2 plate welds + tack-weld float rod + hydro test 30-min hold + citric passivation + post-soak elbow/sparge/PRV install) | [`pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) | ~4.0 | 30-min hydro hold + 30-60 min passivation soak are wall-clock; weld bench session is contiguous |
| Cold core (coil wind on mandrel + insert press + body-side install + 3 foam pours + trim + final 12-screw cap assembly) | [`cold-core.md`](../../hardware/assembly/cold-core.md) | ~5.0 | Foam cure runs hours of wall-clock per pour; trim must wait for cure |
| Refrigerant loop (vent factory R-600a + cut + braze suction tie-in + pinch-swage cap-tube braze + vacuum 30 min + mass-meter recharge + first run-up) | [`refrigerant-loop.md`](../../hardware/assembly/refrigerant-loop.md) | ~4.0 | Doc explicitly says "half a day of work end-to-end" — single contiguous session, no parallelism possible |
| Electronics shelf (heat-sets + JST header solder × ~10 modules + AC distribution + DC distribution + 8 module mounts + 6 inter-module harnesses + 9 SIG pigtails + isolation check) | [`electronics-shelf.md`](../../hardware/assembly/electronics-shelf.md) | ~7.0 | Pure bench, fully parallel with refrigerant-loop and faucet-and-umbilical days |
| Enclosure mechanical (drop cold core + mount compressor + shroud + condenser/fan on side wall + back panel + 5 bulkheads + hopper + seat shelf unpowered) | [`enclosure-mechanical.md`](../../hardware/assembly/enclosure-mechanical.md) | ~4.0 | |
| Internal plumbing (CO2 path + water path with silicone hose + clamps + 12-valve / 10-Y / 2-pump flavor manifold + 3 risers to umbilical bulkheads) | [`internal-plumbing.md`](../../hardware/assembly/internal-plumbing.md) | ~5.5 | Doc itself calls the flavor manifold "the bulk of the bench labor"; ~22 PTC terminations + 12 valves to land |
| Wiring (ground bonds + AC mains + 12V trunk + sensor pigtails routed to all 9 SIG locations + compressor-shroud grommet pass) | [`wiring.md`](../../hardware/assembly/wiring.md) | ~5.0 | Interleaved with internal-plumbing in some zones |
| Faucet + umbilical (Touch-Flo body + printed shell/gasket/plate + 3 LLDPE tubes + brass stiffener + CARGEN insulation + cable sleeve + RP2040 display + KRAUS air switch + Cat6, all into one bagged sub-assembly) | [`faucet-and-umbilical.md`](../../hardware/assembly/faucet-and-umbilical.md) | ~3.0 | Pure bench, fully parallel; ships in the install bag |
| Firmware + commissioning (flash 3 MCUs + first power-on + sensor health walk + 12-valve self-test + relay-driven compressor cycle) | [`firmware-and-commissioning.md`](../../hardware/assembly/firmware-and-commissioning.md) | ~2.0 | |
| Acceptance + 8-hour burn-in (first water fill + first CO2 + 6 metered dispenses + leak walk every 4 hours + per-serial log archive) | [`acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md) | ~3.0 active | 8-hour wall-clock — burn-in eats one full workday of the chassis but only ~3 hrs of operator |
| Finish, pack, ship (cosmetic walk + sign nameplate + fluid drain + install-kit pack + customer docs + label + carrier handoff) | [`finish-pack-ship.md`](../../hardware/assembly/finish-pack-ship.md) | ~2.0 | |
| Install consult (Founder Edition explicit deliverable per [`target-market.md`](../../marketing/target-market.md) line 92 — phone/Zoom call walking customer through countertop drill + faucet drop + keyhole-plate slide + nut + 3 PP1208E pushes + customer-side water + customer-side CO2 first connect) | not yet a standalone doc — see [`install-consult-playbook-gap`](../2026-05-18/install-consult-playbook-gap.md) | ~2.5 | Includes ~30 min prep + 1-2 hr call + ~30 min follow-up |

**Per-unit assembly + ship subtotal: ~47 hours active labor.**

That is the optimistic lower bound. It does not include:

- **Per-unit parts kitting + receiving QC.** Per-unit BOM crosses 10+ ASINs from Amazon + OnlineMetals MTRs + SendCutSend laser-cut plates + harvested ice maker teardown. Receiving each batch, inspecting, staging on the per-build shelf is real labor — call it **~3 hrs/unit** amortized.
- **Per-unit printed-part production.** [`hardware/printed-parts/`](../../hardware/printed-parts/) covers foam shell + 2 foam caps + 2 cap lids + 3 copper plugs + 2 reservoirs + pump cartridge + electronics shelf frame (still pending CAD — see [`electronics-shelf.md`](../../hardware/assembly/electronics-shelf.md) open item §1) + back panel + enclosure walls + faucet shell + nameplate plaque + TPU gaskets. The print farm is mostly passive but slicing, plate swap, supervision, failed prints, post-process: **~3 hrs/unit** is a reasonable amortization.
- **First-of-kind rework headroom.** Vessels that don't pass hydro (no failure-handling decision tree yet — [`pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) open item §2), foam pours that don't cure right ([`cold-core.md`](../../hardware/assembly/cold-core.md) open items still list pour parameters not yet locked), brazes that leak ([`refrigerant-loop.md`](../../hardware/assembly/refrigerant-loop.md) explicitly says re-vent + redo). Yield assumption is undeclared anywhere in the docs. At a placeholder 80 % first-pass yield on the three critical operations (vessel weld + cold core + refrigerant loop), 20 % rework × the affected steps' ~13 hrs ≈ **~3 hrs/unit** of expected rework time.
- **Per-build documentation.** [`acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md) calls for "per-serial test log archived"; [`finish-pack-ship.md`](../../hardware/assembly/finish-pack-ship.md) calls for customer docs and nameplate sign-off. Plus the install-consult prep notes per unit. **~1 hr/unit.**

**Realistic per-unit total: ~57 hours active labor.**

And the founder is doing things beyond per-unit work:

- **Marketing video capture + posting.** [`marketing/target-market.md`](../../marketing/target-market.md) line 240–260 makes this explicit: "the founder isn't a stopgap while the brand gets built; he *is* the product for the first 50." Video is "the discovery mechanism." If the founder doesn't ship video, the rings don't fill. Plausible time budget: ~2-3 hrs/week of capture + edit + post, sustained.
- **Pre-sale + ring-1/ring-2 sales conversations.** "At 10 units/year, every sale is a conversation." A single warm-intro sale from ring-1 trust networks plausibly takes 2-3 hours of conversation, demo, and follow-up across multiple sessions. At 12/year, that's another ~30-40 hrs/year of customer-facing time that isn't in the per-unit number.
- **Post-sale customer support.** No first-year unit will be silent. Founder Edition includes "personal install consultation" and implicitly the relationship downstream of that. Realistic budget: ~2 hrs/unit of follow-up support across the first year of each unit's life. At year three, with 36 fielded units, that's ~72 hrs/year on follow-up support alone.
- **Bookkeeping, taxes, supplier management, shipping logistics, returns.** Solo proprietor overhead. Plausible ~2-4 hrs/week amortized.
- **Design iteration.** The Founder Edition is explicitly described as "shipping looks like while the founder is the factory" — there is no separate engineering team. Every open item in every assembly doc is a future evening of founder labor.

## What the math says

| Scenario | Per-unit active hrs | Marketing + sales + support + overhead | Total annual hrs at 12 units/year | Sustainable weekly hours with a day job |
|---|---|---|---|---|
| Optimistic floor | 47 | ~5 hr/week × 52 = 260 | 12 × 47 + 260 = **824** | 824 / 52 = **15.8 hr/week** |
| Realistic mid | 57 | ~7 hr/week × 52 = 364 | 12 × 57 + 364 = **1,048** | 1,048 / 52 = **20.2 hr/week** |
| Conservative high | 65 | ~10 hr/week × 52 = 520 | 12 × 65 + 520 = **1,300** | 1,300 / 52 = **25 hr/week** |

For reference: a person with a 40 hr/week day job, a partner, a household, and ordinary social and physical-life commitments can probably sustain **15–20 hours/week of focused side-project effort indefinitely**. The upper end (25 hr/week) is achievable for short sprints but not sustainable for four years without burning out or absorbing damage in another part of life.

**Reading off the table:** at the optimistic floor, 12/year is comfortably achievable. At the realistic mid, 12/year is at the upper edge of sustainable spare time. At the conservative high, 12/year is unsustainable and the actual capacity is closer to 8–10/year.

The single biggest unknown is whether the steady-state estimate (47–65 hrs/unit) is right at all. The five assembly docs read in full are detailed and procedural, but they have not been validated against a built unit. Unit 1 has not been built end-to-end. The first unit will plausibly take **~1.5–2× steady-state** because of fixturing-design time, first-of-kind weld debugging (the [`hardware/welding-progress-2026-05-09.md`](../../hardware/welding-progress-2026-05-09.md) recipe was on 304L practice fixture, not 316L production stock — [`pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) open item §4), first foam pour against a real cold-core geometry, first refrigerant-loop tie-in against a brand-new evap coil that needs charge-mass calibration ([`refrigerant-loop.md`](../../hardware/assembly/refrigerant-loop.md) open item §1), and the integration discovery from running every doc end-to-end for the first time. That first-unit overhead is one-time, not annual — but it's also two-to-three full weekends of work that has to happen before unit 1 ships, and the founder shouldn't book that overhead against the 12-unit/year annual target.

## Risks that compress the timeline further (single points of failure)

The plan's bus factor is 1. Several discrete events are catastrophic to the 12/year claim:

- **Founder illness, injury, or family event.** A six-week absence at any point in a given year drops capacity by ~12 % even if everything else is perfect. The plan has no surge capacity, no second builder, no contracted help. This isn't pessimism — it's the actuarial expectation across a four-year run.
- **Day-job pressure.** The plan's spare-time budget assumes the day job stays at ~40 hrs/week. A promotion, a project crunch, a manager change, or an industry shift in the day job can compress side-project hours by 30-50 % for months at a time.
- **Supplier failure.** [`donor-ice-maker-supply-chain-gap`](../2026-05-19/donor-ice-maker-supply-chain-gap.md) already flags the refrigeration-subsystem single-source risk; an Amazon de-list of either ASIN forces a re-source that eats build weeks.
- **Single-vessel scrap.** [`pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) open item §2 has no committed scrap-vs-rework decision tree. One vessel scrapped without rework restores 0 hours of labor but consumes the next 4 hours of bench time on its replacement. At 10-vessel stock that's recoverable; at 1-vessel-of-stock-in-hand that's a build delay.
- **In-field warranty event on a delivered unit.** Founder Edition is built on relationships. A single bad-pour foam shell or a leaking weld on unit #003 sitting in a friend's kitchen consumes founder time at the bench (RMA fix), founder relational equity (with that friend, and with their network), and founder confidence — all of which compound. [`warranty-and-rma-gap`](../2026-05-18/warranty-and-rma-gap.md) flagged this generically; the founder-hour cost is what concerns this gap.

## What an answer looks like

The right answer is **measure, don't argue.** A bottom-up estimate from documentation is what this analysis is, and it has the failure mode of any paper estimate: it doesn't know the real number, only a defensible range. The correction is to run a few units and time them.

### Layer 1: instrument the first three units

For unit 001, 002, 003 — whether they go to friends, family, or stay on the bench — capture the actual hours. Not stopwatch-tracked to the minute, but coarse-grained: which calendar weekend did each major step happen, how many evenings, and rough hours per step. A single text file at [`hardware/build-hour-log.md`](../../hardware/) or per-serial under [`logs/<serial>/`](../../logs/) — that already exists per [`finish-pack-ship.md`](../../hardware/assembly/finish-pack-ship.md). Entries are noisy individually but converge to a real steady-state estimate by unit #3.

What to capture per unit:

- Date / weekend the step was started and the date it was finished.
- Cumulative active hours (operator estimate to the nearest 30 min).
- Anything that was rework or first-of-kind learning (so steady-state can be backed out of total).
- Anything that *blocked* on another step (parts not arrived, foam not cured, partner needed kitchen).

Three units' data is enough to validate or correct the 47–65 hr range and the 12/year claim. Cost: ~5 min per build session of journaling.

### Layer 2: identify the bottleneck step before building 50 of them

The table above identifies the largest single steps — electronics shelf at ~7 hrs, internal plumbing at ~5.5 hrs, cold core at ~5 hrs, wiring at ~5 hrs. Two of those (electronics shelf, faucet-and-umbilical) are pure bench work that can be batched: the founder can do five electronics shelves in one weekend if every module is in hand, then five faucet-and-umbilicals the next weekend. The other steps are coupled to a specific in-progress chassis and cannot be batched across units in the same way.

If steady-state capacity needs to grow from ~12/year to ~18/year without adding a second builder, the leverage is in:

- **Vessel-batch tap fixturing.** [`hardware/tapping-plan-2026-05-03.md`](../../hardware/tapping-plan-2026-05-03.md) is a single-use Baltic-birch fixture. A reusable fixture for the 10-vessel batch is called out as a downstream design step in [`pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) "Open items" but not yet built. The 4 NPT taps per vessel × 10 vessels × ~10 min/tap = ~6.6 hrs per batch; a good fixture cuts that to ~3.
- **Pour-foam jig with timed kit pre-measurement.** Currently 3 separate pours per unit with shared consumables. A dedicated foam-bench setup with pre-measured kit components could shave ~30 min/unit.
- **Pre-built electronics shelves on hand.** If the founder builds 4 shelves in a weekend twice a year, every per-unit build day starts with a shelf already done. ~7 hrs/unit moves out of the build-day critical path and into batched weekend work.
- **Pre-bagged faucet-and-umbilicals.** Same logic — the bagged sub-assembly is small and shelf-stable.

None of these block unit 1. They are the answer to "how do we get from 12/year to 18/year without burning the founder out," which is a different question from "is 12/year achievable." Worth pre-staging the analysis so the founder isn't reinventing it in year 2.

### Layer 3: tier the public-facing plan against the real number

Once Layer 1 gives a real number after three units:

- **If real capacity is 10–14/year:** [`marketing/target-market.md`](../../marketing/target-market.md) is approximately right. Maybe footnote the 12/year claim as "current best estimate, validated against units 001–003," not a commitment.
- **If real capacity is 7–9/year:** the four-year run becomes a six-year run. Re-examine whether Standard Edition opens at unit 51 or whether the threshold moves; re-examine whether $7,500 is the right price for a now-7-year-backlog scarce product (arguably it goes up, not down). Update revenue projections; the "12 × $7,500 = $90,000/year" line in target-market.md becomes "8–9 × $7,500 ≈ $65–70K/year." The internal-plan ring-1/ring-2 pricing of $2,000–3,000 doesn't change — those are friend-and-family numbers, time-budget-independent.
- **If real capacity is 15+/year:** Standard Edition opens sooner than four years. The scarcity story in target-market.md needs revision. The founder's sabbatical math accelerates. The bus-factor risk concentrates because more units are in the field per unit of time.
- **If real capacity is below 6/year:** the Founder Edition stops being a four-year run and becomes a multi-decade craft practice with maybe 20–30 units total ever shipped. That is the "yay outcome" from target-market.md line 192–194 ("twenty units a year, supplier relationships stable, design maturing"). It is not a failure; it is a different plan. But target-market.md should not claim 50 units in four years if six per year is the real number.

### Layer 4: separately, name the bus-factor explicitly in business docs

The plan's single-builder design is a feature for ring 1 and ring 2 — the founder is the brand. It is a hazard for ring 3 and beyond, and for any in-field unit that needs warranty service. [`business/incorporation.md`](../../business/incorporation.md) and [`marketing/target-market.md`](../../marketing/target-market.md) both describe the founder-as-builder model but neither names the bus factor explicitly or commits to a continuity plan. The right answer probably isn't "hire help" — that breaks the Founder Edition story. The right answer is closer to a written-down successor plan: who finishes the current half-built unit if the founder is in the hospital for six weeks, how do customers reach someone who knows the appliance during that window, where do the build instructions and supplier contacts live such that a friend with hands could step in. Not staffing; documentation against the bus.

Adjacent gap, worth its own file: [`workshop-as-factory-gap`](../2026-05-19/workshop-as-factory-gap.md) flags the residential-structure-as-factory liability surface; this gap flags the founder-as-factory continuity surface. Both are the same shape of problem — a hidden dependency on a thing that wasn't named as load-bearing.

## What I'd ask the project owner to decide

In order of decreasing urgency:

1. **Start the build-hour log now, on unit 001.** Single text file, coarse entries, takes 5 min per build session. Captures the data that will validate or correct the 12/year claim. Cost: zero. Value: every downstream business decision that rests on the 12 number depends on this data existing within a year.
2. **Footnote 12/year in [`marketing/target-market.md`](../../marketing/target-market.md) as estimated, not committed.** A one-line addition: *"This estimate is the founder's working assumption; it will be validated against actual build hours on units 001–003 and revised if needed."* The footnote costs nothing to the buyer narrative and protects against a public-revision embarrassment later.
3. **Identify which steps to batch first.** Electronics shelf and faucet-and-umbilical are the obvious candidates — both are pure bench, shelf-stable, and parallel to the coupled in-chassis work. The next time the founder is staging an order, double up so two of each can be built in one bench session.
4. **Build the vessel-tap batch fixture before unit 002.** [`pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) open item §1 is already on the list; this gap promotes it from "production-procedure cleanup" to "throughput-gating fixture, build before scale."
5. **Decide the year-1 marketing-video time budget separately from the per-unit build budget.** Target is "consistent video presence." Translate to hours: ~2-3 hr/week is the lower bound for a single 30-second short per week. Either commit or scale back the claim. Both are defensible; the worst answer is to assume it's free time.
6. **Name the bus factor explicitly somewhere.** A short paragraph in [`business/incorporation.md`](../../business/incorporation.md) or [`marketing/target-market.md`](../../marketing/target-market.md) acknowledging that the founder-as-factory model has a single point of failure, and pointing to whatever continuity plan exists (or naming the lack of one).

## Files this recommendation should propagate into when actioned

- New file [`hardware/build-hour-log.md`](../../hardware/) — append-only per-build-session journal, ~5 min/session, populated unit by unit starting with unit 001.
- [`marketing/target-market.md`](../../marketing/target-market.md) — footnote the 12/year claim as a working estimate; once units 001–003 are logged, revise both the number and the four-year-run language to reflect what was measured. Update the "$90,000 annual revenue" line accordingly.
- [`hardware/assembly/pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) "Open items" — promote the batch tap-fixture from item §1's downstream design step to a named throughput-gating deliverable with a target-before date (before unit 002 or before unit 005, founder's choice).
- [`hardware/assembly/electronics-shelf.md`](../../hardware/assembly/electronics-shelf.md) and [`hardware/assembly/faucet-and-umbilical.md`](../../hardware/assembly/faucet-and-umbilical.md) — add a note that these sub-assemblies are batch candidates, and that the build cadence is intended to pre-stage them in 2- or 4-unit batches rather than one-per-build-day.
- [`business/incorporation.md`](../../business/incorporation.md) — bus-factor paragraph + pointer to whatever continuity plan exists.
- [`marketing/target-market.md`](../../marketing/target-market.md) "Open questions" — add a sixth open question: *"6. Real per-unit build hours, validated against units 001–003. Until measured, all throughput and revenue claims are estimates."*

---

*This recommendation is the work of an hourly background agent. The per-step hour estimates above are bottom-up reads of the assembly docs, not measurements of a real build — they should be considered upper-bound-of-confident-range estimates and replaced with actual log entries as soon as unit 001 begins. The 15–25 hr/week sustainable-spare-time band is a working assumption from general knowledge about side-project capacity for working professionals with families; it is not specific to this founder, and the founder's real sustainable budget may be higher or lower. The strategic argument — that "~12 units/year" is the structural anchor of Founder Edition pricing and the rings-of-trust plan, that the number has never been audited, that the cost of auditing is one build-hour log starting on unit 001, and that the cost of not auditing compounds into every downstream business decision — is grounded in the existing repo and should hold up under verification.*
