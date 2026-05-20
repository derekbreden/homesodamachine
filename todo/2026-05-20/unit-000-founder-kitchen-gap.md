# Unit 000 — the founder's-own-kitchen install — is the prerequisite the repo does not name

**Author:** hourly agent, 2026-05-20 (mid-day)
**Status:** recommendation only — not for direct execution
**Audience:** future agents, Derek

**Distinct from siblings:**
- Today's [`first-pour-commissioning-gap.md`](first-pour-commissioning-gap.md) is the *customer-side* state machine between "appliance shows up on the doorstep" and "first cold soda." This doc is upstream of that: the *founder's own* install of an integrated appliance, in his own kitchen, replacing his existing countertop prototype, *before* unit 001 ships to anybody.
- Today's [`founder-build-hour-audit-gap.md`](founder-build-hour-audit-gap.md) audits the 12/year sustainable build pace claim. This doc audits a different load-bearing claim — that the marketing strategy ("his kitchen, his pour, his face") is grounded in a kitchen that contains the product being sold. It does not.
- 2026-05-19 [`workshop-as-factory-gap.md`](../2026-05-19/workshop-as-factory-gap.md) is about the founder's **workshop** — where units get built. This doc is about the founder's **kitchen** — where the unit gets *lived with*, and where every Tier 1 marketing video must be filmed per [`marketing/video/concepts.md`](../../marketing/video/concepts.md).
- 2026-05-19 [`above-counter-ux-gap.md`](../2026-05-19/above-counter-ux-gap.md) covers the missing above-counter (faucet/display/air-switch) design layer. This doc presumes that work is done — and asks the next-level question: where does the *first instance* of the finished above-counter + under-counter system get installed, and why is that location not the founder's own kitchen by mandate?
- 2026-05-18 [`install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) is about the **customer's** install consult (the phone/Zoom call promised at Founder Edition pricing). This doc is the founder's *first* install — the one that gives him standing to do that consult at all.

---

## TL;DR

The marketing strategy in [`marketing/target-market.md`](../../marketing/target-market.md) — Founder Edition at $7,500, "the brand is Derek, his face, his kitchen, his story" (line 260), Tier 1 video #1 is "The Pour" filmed in his kitchen ([`marketing/video/concepts.md`](../../marketing/video/concepts.md) line 31), the buyer's "is this real?" question answered by "his kitchen, his pour" (target-market.md line 267) — rests on a premise the hardware repo does not satisfy: **the founder has a finished integrated appliance installed in his own kitchen.**

Today he does not. The kitchen contains the *prototype* photographed in [`README.md`](../../README.md) lines 28–40 — a countertop dispenser faucet, an under-cabinet **Lilium** carbonator, Platypus concentrate bags, a control panel. That is the right machine to ship Tier-2 build-process content from. It is the *wrong* machine to film Tier-1 "30 second pour, ends with 'He hates these cans'" content from, because:

1. The Lilium goes away in the product being sold ([`future.md`](../../hardware/future.md) line 1). The Tier-1 pour video must show the *product*, not its predecessor.
2. The countertop reservoirs go away. The Platypus bags visible at [`README.md`](../../README.md) line 40 are not in the appliance.
3. The carbonator chiller is integrated in the product being sold (target-market.md line 11 — "refrigerates and carbonates its own water internally"). The prototype's external carbonator is the most visible architectural delta.
4. Tier-1 video #3 — "The Install (2-3 minutes)" — explicitly requires a finished unit to install on camera ([`marketing/video/concepts.md`](../../marketing/video/concepts.md) lines 50–56). That install has to happen somewhere, on a real kitchen with real plumbing. The first one is the founder's.

The repo has a complete production-side chain that ends at a sealed carton sitting on the loading-out shelf ([`hardware/assembly/finish-pack-ship.md`](../../hardware/assembly/finish-pack-ship.md)). It has an explicit handoff: "the customer-side countertop install at the kitchen — that's the customer's (or their installer's) job, supported by the printed install guide that lives in the install kit" (finish-pack-ship.md, scope section). Every other assembly doc in [`hardware/assembly/`](../../hardware/assembly/) is a per-unit *factory* procedure. None of them describe the founder's *own* install in his *own* kitchen. There is no `hardware/assembly/founder-install.md`, no `marketing/video/unit-000.md`, no entry in [`marketing/target-market.md`](../../marketing/target-market.md) "Finding the first 10 buyers" that names the unit that proves they could be found.

This is unit **000**, not unit 001. Numbering matters: the customer-facing Founder Edition begins at 001 ([`marketing/target-market.md`](../../marketing/target-market.md) line 13). Unit 000 is internal — the founder's home install, the dogfood, the film set, the install-procedure shakedown, the source-of-trust for every Tier-1 video the marketing strategy depends on. The repo treats unit 001 as the first thing built; it should treat unit 000 as the *zeroth* thing built, and the only one not for sale.

---

## Why this is a gap, not just an obvious next step

It would be reasonable to read this and think: "of course the founder installs one in his own kitchen first — that's just what happens; we don't need to write it down."

That reasoning is the same shape as the founder-build-hour-audit-gap raised in [`founder-build-hour-audit-gap.md`](founder-build-hour-audit-gap.md): the 12/year claim is "obvious" enough that nobody has questioned it, and the work to make it real has never been planned. Same here. The "obvious" install in the founder's kitchen has not been planned because nobody has named it as a project. As a result:

- **No place in the build order.** The build order at the moment is *pressure vessel → cold core → electronics shelf → enclosure → faucet + umbilical → acceptance → finish-pack-ship → carrier handoff*. There is no "and now I install one in my own kitchen, before any customer-bound unit leaves the workshop" step. The structural risk is that the founder finishes unit 001 and ships it to a paying ring-1 customer without ever having lived with an integrated unit, because no procedure says "stop here, install in your own kitchen, drink soda from it for at least N weeks before any unit ships."
- **No filming plan.** Marketing/video/concepts.md describes the videos that need to exist (The Pour, The Full Story, The Install) but does not describe *which physical unit* gets filmed from. The implicit answer is "the founder's." The explicit answer should be "unit 000 in his kitchen, on a date that's blocked out in advance, with a shot list."
- **No install-procedure shakedown.** Customer install is supported only by "the printed install guide in the install kit" (finish-pack-ship.md, scope). The install guide does not yet exist as a callable artifact. Its first real test is the founder's own install — running the guide as a customer would, in a real cabinet, with real plumbing, and finding everything that doesn't work. If unit 001 ships first and the customer is the first to use the install guide, every failure mode of the guide surfaces in front of a paying customer at $7,500 — the worst possible audience.
- **No dogfood signal.** A founder who does not personally use the product he is selling has no honest answer to "what is daily life with this thing like?" The prototype on the counter answers that question for the prototype; it does not answer it for the appliance. Concrete examples of what the founder cannot yet answer from prototype experience: (a) Does the compressor cycling sound bother you at the kitchen sink? (b) What does it sound like at 11 PM when somebody is watching TV in the adjoining room? (c) How often does the cabinet door get opened to glance at the CO2 cylinder gauge — daily? weekly? never? (d) Does the front-panel CO2 inlet location actually feel right when you're swapping a cylinder in a real cabinet under a real sink? (e) Does the harvested-ice-maker condenser fan whine at a frequency that drives a household crazy after a month? None of these are answerable from the countertop prototype. All of them are answerable from unit 000 after 30 days of daily use. All of them affect the answer to "is this a real product?" — the question target-market.md line 267 says the founder's presence answers. He cannot honestly answer it from the prototype he's living with.

- **No graceful migration off the existing prototype.** The countertop dispenser faucet in [`README.md`](../../README.md) is the founder's daily soda. When unit 000 gets installed, the prototype gets uninstalled. That is a domestic operation — removing the Lilium, removing the Platypus-bag control panel, possibly patching the existing faucet penetration in the countertop or repurposing it for the new appliance's faucet. None of that has been scoped. If the unit 000 install fails halfway through (a leak, a wiring miss, a refrigerant short-charge that needs to come back to the bench), the founder has no soda at home that week. That's a non-trivial domestic cost for a founder who drinks 3/day per his own profile in target-market.md line 64.

The combined picture: the unit-000 install is simultaneously a marketing milestone, an install-procedure validation, a domestic upgrade, and a dogfood data source — and it has been scoped under none of those headings.

---

## What unit 000 has to be

Unit 000 is **not** a "test build" in the sense of a bench prototype that lives in the workshop. The workshop already has the bench prototype (the countertop unit photographed in README.md). Unit 000 is a *production-fidelity* unit assembled per the full [`hardware/assembly/`](../../hardware/assembly/) chain — same pressure vessel procedure, same cold-core foam pour, same acceptance-and-burn-in pass, same finish-pack-ship pack-out — that is **then taken to the founder's own kitchen and installed** rather than packed into a carton.

Functionally it must be indistinguishable from unit 001. The only differences are:

1. **Plaque.** Unit 000 plaque says 000, with whatever signing convention separates it from the customer-bound series. ("000 — kept by the founder. Not for sale.") The plaque exists for the same reason every other plaque exists — per-unit traceability and identity. Detail deferred to [`hardware/printed-parts/enclosure/nameplate/README.md`](../../hardware/printed-parts/enclosure/nameplate/README.md), but called out here so the plaque generator is aware that 000 is a valid serial.
2. **Destination.** Carton → loading-out shelf → carrier handoff is replaced by carton → trunk of the founder's car → his kitchen. The finish-pack-ship procedure runs to completion as if it were a customer carton (the install kit goes in, the line cord goes in, the documentation packet goes in, the transit caps go on) — because the install procedure being validated is *the customer's*, not a special-case founder one. The founder unboxes his own carton in his kitchen as a customer would, and uses the same documentation packet he expects a customer to use.
3. **Dogfood window.** Unit 000 lives in the founder's kitchen for at least N weeks (suggested N: 6) of daily use before unit 001 ships. Define what the dogfood is *for* — see "Acceptance criteria" below — so the founder isn't tempted to short-circuit it.

Unit 000 is **not** a free unit for the founder in any honest accounting sense. It absorbs:
- One full set of BOM ($1,486.55 per [`hardware/bom.md`](../../hardware/bom.md), confirmable from the latest BOM total in [`purchases.md`](../../hardware/purchases.md))
- One full set of build hours (the very thing being audited in [`founder-build-hour-audit-gap.md`](founder-build-hour-audit-gap.md) — so this is the *first* real data point for that audit)
- The slot that would otherwise have been unit 001 in time-to-first-customer

It is a real cost. It pays back across three lines simultaneously — marketing video, install-procedure validation, dogfood — that no other build cycle pays back across.

---

## Where unit 000 sits in the build order

The build order today (implicit, never written as a sequence document) appears to be:

1. Pressure vessel — in progress per shipped welding videos
2. Cold core — design exists, pour procedure exists
3. Electronics shelf — design exists
4. Enclosure mechanical — printed parts exist in design
5. Faucet + umbilical — design exists
6. Internal plumbing — design exists
7. Acceptance + burn-in — procedure exists
8. Finish, pack, ship — procedure exists

A defensible insertion point for unit 000 is **between step 7 (acceptance + burn-in passes for the first time) and step 8 (the first carton ships).** Specifically:

- The first integrated unit to pass acceptance-and-burn-in becomes unit 000 by default. It does not get a customer order number attached. It does not enter the ship queue.
- Founder takes possession; install in his own kitchen begins that day or the next.
- Dogfood window of 6 weeks runs.
- During the dogfood window, the very next acceptance-passed unit becomes unit 001. Unit 001 sits in inventory on the loading-out shelf — built, validated, plaque-applied — but **does not ship** until unit 000's dogfood window closes successfully.
- If unit 000 dogfood surfaces a defect that requires a design change, unit 001 is reworked (or scrapped, depending on the defect) before shipping. The cost of a paying customer receiving a known-defective design is much higher than the cost of building a second pre-ship unit.

The 6-week window is a choice, not a derivation. Rationale: it is long enough to cover (a) the first compressor-cycling-in-real-life experience, (b) a CO2 cylinder run-out, (c) a flavor-reservoir refill cycle, (d) at least one clean cycle, (e) a weekend with guests over. Shorter risks missing systemic issues that take a few use cycles to appear; longer punishes time-to-first-customer for marginal additional signal. Worth revisiting after the first run.

This insertion adds *one* unit to the BOM cost of the Founder Edition pre-ramp and *one* build cycle of calendar time before unit 001 ships. At the audited build pace ([`founder-build-hour-audit-gap.md`](founder-build-hour-audit-gap.md)) those are real but not large costs.

---

## What the founder's kitchen needs before unit 000 can land

This is the part that nobody has scoped. The kitchen install presumes:

1. **Plumbing.** A 3/8" or 1/4" cold-water tee under the sink for the appliance's rear-panel water inlet. Per [`marketing/target-market.md`](../../marketing/target-market.md) line 76, "same prerequisite as a dishwasher or under-counter water filter, present in virtually all owned homes." That is the assumed condition. **Is it actually present in the founder's kitchen?** If yes, document the tap location and any fittings already in place; if no, scope the plumbing work as a prerequisite (likely under $50 in parts, possibly a plumber visit) and put it on the calendar before unit 000 is built.
2. **AC outlet.** A 120 V outlet inside the cabinet, sized for the appliance's continuous load. Existing under-cabinet outlets often exist for disposals or dishwashers. Verify presence and condition; add if missing.
3. **CO2 cylinder location.** Front-panel inlet with cylinder beside the appliance in the cabinet on the cabinet floor (per [`future.md`](../../hardware/future.md) line 95). The cabinet has to accommodate a 5 lb or 10 lb cylinder beside the appliance. Measure cabinet interior dimensions; confirm cylinder fits in the side gap; identify which side gap (left or right) the cylinder will live in — this is the side-face exterior surface decision that [`future.md`](../../hardware/future.md) line 131 defers to an as-yet-unwritten document.
4. **Faucet penetration.** A hole in the countertop for the under-cabinet faucet's gooseneck. The existing prototype already has a faucet penetration ([`README.md`](../../README.md) line 174 references the Milwaukee 1-1/4" hole dozer). The integrated appliance's faucet may or may not match the existing penetration diameter and location. Scope: measure existing penetration, compare to faucet-and-umbilical spec, decide whether to reuse, enlarge, fill-and-redrill, or relocate. This is the highest-friction physical change in the install and is the same surface gap covered in 2026-05-19 [`countertop-faucet-penetration-gap.md`](../2026-05-19/countertop-faucet-penetration-gap.md), but with the founder's own counter as the test case.
5. **Cabinet height / footprint.** Under-counter cabinets vary widely. The integrated appliance's height + footprint has to fit in the founder's specific cabinet, leaving the cabinet door operable, room for the CO2 cylinder in the side gap, and at least 2–4" of working gap at the back per [`future.md`](../../hardware/future.md) line 95. Measure cabinet interior. If the appliance does not fit, that is information the marketing strategy needs *before* it ships to customer cabinets — because the founder's cabinet is statistically a normal one for the target buyer.
6. **Prototype removal plan.** The existing prototype is plumbed, wired, and connected to a Lilium and a CO2 cylinder. Removing it without losing soda continuity through the install week needs a sequence: stop using the prototype, drain it, remove the Lilium and bags, cap the existing water connection if it's not the same one the new appliance uses, store the prototype components (they are still useful as a bench reference). This is a half-day operation at most but it is a *household* operation, and it costs the founder his daily soda for the install week — worth scheduling around social calendar, work load, and any visiting family.

None of items 1–5 are blocking — they are just the prerequisite scope that nobody has written down. Item 6 is sequencing.

---

## Filming plan

The same week unit 000 is installed is the week the Tier-1 video work begins. Concrete plan:

- **Day of install.** Set up a fixed camera position covering the under-cabinet space. Film the entire install, real-time. This becomes raw material for "The Install (2-3 minutes)" per [`marketing/video/concepts.md`](../../marketing/video/concepts.md) lines 50–56. The footage exists or doesn't — there is no second chance to film the founder's first install. Even if the cut never ships, the raw footage is irreplaceable.
- **Within 7 days.** Shoot "The Pour (30 seconds)" per concepts.md lines 31–38. Repeat variants: morning, afternoon, late night, different glass, different flavor. Build a library of 8–12 takes from which the strongest one becomes the launch video.
- **Within 30 days.** Shoot "The Full Story (3–5 minutes)" per concepts.md lines 40–48. By this point the founder has lived with the unit long enough to be honest about what daily life is like with it. The honesty is the value.

The shipped Tier-2 videos (welding, tapping, the laser-welder antagonist arc) continue in parallel, sourced from the workshop. The founder's kitchen is a separate film set from his workshop. Unit 000 establishes that set.

---

## Acceptance criteria — what unit 000 has to produce before unit 001 ships

A list of *what dogfood is supposed to surface* — so that the dogfood window is not a vibes exercise.

1. **Daily-use compressor cycling profile.** How many compressor on/off cycles per day at the founder's actual consumption (~3/day)? Does the duty cycle exceed the donor compressor's spec? This is the first real validation of the freeze-protection hysteresis chosen at [`future.md`](../../hardware/future.md) line 56.
2. **Acoustic experience at the sink.** Subjective: is the compressor audible at the sink? At adjacent rooms? At night? This feeds into the same concern raised in 2026-05-19 [`compressor-acoustic-budget-gap.md`](../2026-05-19/compressor-acoustic-budget-gap.md), but tested in a real domestic acoustic environment rather than a workshop.
3. **CO2 runtime measurement.** How long does the founder's first cylinder actually last at his consumption? This is the first real data point for [`marketing/target-market.md`](../../marketing/target-market.md) line 269 "CO2 every few months" and for 2026-05-19 [`co2-runtime-and-depletion-ux-gap.md`](../2026-05-19/co2-runtime-and-depletion-ux-gap.md).
4. **Cabinet thermal experience.** Is the cabinet warm to the touch after a day of use? Does the exhaust grille direction make sense given the founder's actual cabinet geometry? This is the field test for the assumptions in 2026-05-19 [`cabinet-heat-rejection-gap.md`](../2026-05-19/cabinet-heat-rejection-gap.md).
5. **Install guide friction.** Every step in the printed install guide that the founder had to deviate from is a defect in the install guide. Every tool he reached for that wasn't in the install kit is a defect in the install kit. Every question he had that the guide didn't answer is a defect in the guide. Capture these in real time — a notepad on the counter during install.
6. **Refill / clean-cycle UX.** First time the flavor reservoir runs low, document what the user-visible signal is and whether the printed-guide refill procedure matches reality. Same for the first clean cycle initiated from the iOS app.
7. **Domestic acceptability.** Does anyone else in the household have an opinion (founder is single per the implicit signals in target-market.md but if that's wrong, this matters)? Does it look like a kitchen appliance or like a science project? This is the question the marketing strategy is most exposed to and the one that *cannot* be answered from the workshop.
8. **Three guest reactions.** Have at least three people see it pour soda in the founder's kitchen during the dogfood window. Capture their unprompted first sentence. This is rehearsal for "The coworker model" in [`marketing/target-market.md`](../../marketing/target-market.md) lines 219–225 — the marketing strategy says "you know, they have a machine for that now" is the most powerful sentence in the entire go-to-market plan. If three guests in six weeks never say it, that is a signal that the appliance is not visible/conversation-starting enough in its current physical form, and the marketing strategy needs adjustment before shipping unit 001.

Each of these is a finite, recordable observation. None requires special instrumentation beyond what the unit already has. All of them are unavailable from the prototype.

---

## Recommendation priorities

1. **(Now, zero hardware cost.)** Add unit 000 to the build-order narrative — either as a section in [`hardware/future.md`](../../hardware/future.md) (after "Rear-panel nameplate") or as a new top-level doc at `hardware/assembly/unit-000-founder-install.md`. Name it as the deliberate, scoped first install. Stop relying on the implicit assumption that it'll just happen.
2. **(This week, zero hardware cost.)** Measure the founder's kitchen against the prerequisites in "What the founder's kitchen needs" above. Document findings under unit 000's procedure doc. If anything blocks the install (no water tap under sink, no AC outlet, cabinet too small), call that out as a project to land before unit 000 build starts.
3. **(Before first integrated build.)** Add unit 000 to the plaque-generator's valid-serial list. Add unit 000 to the per-unit-portal scaffolding (see 2026-05-18 [`per-unit-portal-gap.md`](../2026-05-18/per-unit-portal-gap.md)) — the founder's own unit gets a `homesodamachine.com/u/000` page just like every customer unit, and is the first page the founder publishes against the per-unit-portal contract.
4. **(Concurrent with unit 000 install.)** Stand up the filming plan in "Filming plan" above. Block the calendar week. Make sure cameras, lights, and shot-list exist before the install begins. This is irreversible work.
5. **(During dogfood window.)** Capture the acceptance criteria in "Acceptance criteria" above as a written log. The log is the first entry in whatever build-hour and field-data instrumentation the founder ends up keeping (per [`founder-build-hour-audit-gap.md`](founder-build-hour-audit-gap.md)).
6. **(End of dogfood window.)** Write a published-or-internal "Unit 000 dogfood report" — what worked, what surfaced, what changed before unit 001 shipped. This is also a marketing artifact: a credible buyer arriving at homesodamachine.com from the Tier-1 pour video can read it and conclude "this person is operating in good faith with their own kitchen."

None of these recommendations changes the appliance. All of them harden the *path* by which the marketing strategy ("his face, his kitchen, his story") becomes a thing that has happened, rather than a thing that is assumed will happen.

---

## Pointers to existing docs

- [`marketing/target-market.md`](../../marketing/target-market.md) — lines 219–268, the "his face, his kitchen, his story" load-bearing claim that this gap is about
- [`marketing/video/concepts.md`](../../marketing/video/concepts.md) — Tier 1 video plan, which presumes a unit-in-founder's-kitchen exists
- [`hardware/future.md`](../../hardware/future.md) — the integrated appliance spec; the unit 000 install procedure should be a sibling of the existing assembly docs
- [`hardware/assembly/finish-pack-ship.md`](../../hardware/assembly/finish-pack-ship.md) — the procedure unit 000 still runs to completion, ending at unboxing in the founder's kitchen instead of carrier handoff
- [`README.md`](../../README.md) lines 28–47 — the existing countertop prototype, which is the *thing that gets removed* when unit 000 lands
- [`pie-in-the-sky/lite.md`](../../pie-in-the-sky/lite.md) line 80 — confirms the existing prototype is the founder's own counter, not a separate bench piece
- Today's sibling [`first-pour-commissioning-gap.md`](first-pour-commissioning-gap.md) — customer-side commissioning, which unit 000 is the rehearsal for
- Today's sibling [`founder-build-hour-audit-gap.md`](founder-build-hour-audit-gap.md) — unit 000 is the first real data point for that audit
- 2026-05-19 sibling [`countertop-faucet-penetration-gap.md`](../2026-05-19/countertop-faucet-penetration-gap.md) — the founder's countertop is the first test case
- 2026-05-19 sibling [`cabinet-heat-rejection-gap.md`](../2026-05-19/cabinet-heat-rejection-gap.md) — the founder's cabinet is the first thermal test
- 2026-05-19 sibling [`compressor-acoustic-budget-gap.md`](../2026-05-19/compressor-acoustic-budget-gap.md) — the founder's kitchen is the first acoustic test
- 2026-05-18 sibling [`per-unit-portal-gap.md`](../2026-05-18/per-unit-portal-gap.md) — unit 000 is the first page to publish against that contract
- 2026-05-18 sibling [`install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) — the founder cannot honestly run a customer install consult without first having run his own
