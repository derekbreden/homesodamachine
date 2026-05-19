# Concentrate supply resilience: what happens to a $7,500 faucet when a single Amazon SKU stocks out

**Author:** hourly agent, 2026-05-19 (second of the day)
**Status:** recommendation only — not for direct execution
**Audience:** future agents, Derek
**Distinct from siblings:**
- 2026-05-18 covered post-sale logistics (freight/bench, CO2 supply, install consult, order+payment, per-unit portal, warranty/RMA). None of them touch the concentrate (flavor syrup) supply.
- 2026-05-19 morning sibling [`trademark-and-brand-name-usage-gap.md`](trademark-and-brand-name-usage-gap.md) covers the *legal* exposure of using "Diet Mountain Dew" in marketing. This doc is about the *operational* exposure: what happens to the customer's daily ritual when the Diet Mountain Dew SKU itself becomes hard to buy.

The two are adjacent but the actions are completely different. Trademark gap fixes the marketing copy and the firmware bitmaps. This gap fixes inventory, supplier diversity, and customer communication.

---

## TL;DR

The repo treats concentrate supply as a low-priority background risk. [`marketing/competitors/pepsi.md`](../../marketing/competitors/pepsi.md) §"Supply Chain Risk" frames it at the platform level: *PepsiCo could discontinue the SodaStream syrup line.* That framing understates the near-term, high-probability failure mode and overstates the catastrophic one.

**The real risk surface is per-SKU, per-channel, per-month — not platform-level.** Five concrete failure modes that can occur this calendar year, with no warning, against any of the eleven SKUs we depend on:

1. A single SKU goes "Currently unavailable" on Amazon for 2-8 weeks (routine for SodaStream-Pepsi concentrate bottles — Mountain Dew Code Red Zero Sugar in particular sits on Amazon-only distribution per [`pepsi.md`](../../marketing/competitors/pepsi.md) line 176).
2. The bottle goes Prime-ineligible (third-party fulfilled, multi-week ship times, +30-50% markup, often counterfeit).
3. The SKU is delisted from Amazon entirely while remaining on sodastream.com (PepsiCo channel-steering — they prefer their owned channel; the AGENTS.md note "I only care about Amazon Prime listings" reflects how the founder shops, not how PepsiCo distributes).
4. The bottle format / cap changes. Today's 14.9 fl oz / 440 mL bottle is a SodaStream packaging decision, not an ingredient-supply decision. PepsiCo can change the format unilaterally; the hopper / pour UX in [`hardware/future.md`](../../hardware/future.md) lines 127-128 is calibrated to today's bottle.
5. The customer's *preferred* flavor goes off-sale while *some* flavors remain. This is the worst case for retention: the customer still has a working appliance, but the product loop they paid $7,500 for is broken until the SKU returns.

None of these failures involve PepsiCo "noticing" us or making a strategic decision against the product. They are noise inherent to retail packaged-goods distribution. They will happen — the only question is what happens to the customer's faucet that day.

**What is in the repo today:**

- [`pepsi.md`](../../marketing/competitors/pepsi.md) lines 188-201: a 14-line supply-chain risk section naming three platform-level risks and four mitigations. Frames the problem as low-probability tail risk.
- [`hardware/future.md`](../../hardware/future.md) line 89: the BiB rear-panel adapter is "present but not prominently marketed; it serves customers who source their own commercial syrup." Hardware path exists; business-side support for it is absent.
- [`target-market.md`](../../marketing/target-market.md) line 269: "Syrup every few weeks (Amazon)." Stated as the answer to the buyer's "what's the ongoing hassle?" question — implicitly promising Amazon-Prime availability as the steady state.
- AGENTS.md "Amazon Prime" memory: founder treats non-Prime Amazon listings as nonexistent. **The customer almost certainly will too.**

**What is not in the repo:**

- No per-SKU shelf-life / expiration-date characterization. Concentrate bottles ship with date codes; we have no documented data on what the typical date code reads when received, or whether opened/unopened bottles behave differently in our chilled-reservoir application (8-15 °C reservoir per `future.md` line 81 vs. shelf-stable ambient on the packaging).
- No buffer-stock policy. With ~12 units/year in the Founder Edition window and 11 candidate SKUs, even a "ship two bottles of each launch flavor with the appliance" policy is unspecified.
- No multi-source supplier list. The repo names SodaStream/PepsiCo only. Alternative concentrate suppliers (BiB from a commercial route, off-brand SodaStream-compatible) are mentioned in `pepsi.md` line 201 in passing without specifics.
- No customer communication template for "your preferred flavor is unavailable for six weeks."
- No BiB-path business operationalization despite the rear-panel adapter being on the hardware roadmap. What wholesale account? What MOQ? What pricing? Who is the BiB supplier of record?
- No tracking of which SKUs are launch-day-supported. The firmware ships bitmaps for Diet Wild Cherry Pepsi, Diet Mountain Dew, and Diet Coke (per [`trademark-and-brand-name-usage-gap.md`](trademark-and-brand-name-usage-gap.md) finding #2), but the marketing in `target-market.md` line 11 names "Diet Mountain Dew, Diet Pepsi, Pepsi Zero Sugar." These are different lists. There is no single source of truth for which flavors a Founder Edition unit is sold against.

---

## Why this is worth a focused doc, not a line in `pepsi.md`

The existing supply-chain risk section in `pepsi.md` is a *competitive-analysis* document. It catalogs the risk from PepsiCo's perspective: *will PepsiCo do something hostile.* The framing is correct for that purpose.

But the customer doesn't experience PepsiCo's strategic posture. The customer experiences:

> "I went to reorder my Diet Mountain Dew last Tuesday and it's been 'Currently unavailable' for three weeks. I paid $7,500 for this thing. What do I do?"

This is an *operations* question, and it has nothing to do with whether PepsiCo is friendly or hostile. SodaStream-Pepsi SKUs go in and out of stock on Amazon on a multi-week cadence under normal conditions, the same way any specialty-CPG SKU does. The question is what the appliance maker does about it.

The reason this gap matters specifically *now*, not later:

- Ring 1 buyers (per `target-market.md` lines 170-180) are friends and family. The first time a ring-1 buyer's flavor stocks out, the founder gets a personal text — and an opportunity to model the response that will scale.
- At ring 1, the founder can absorb a stockout by literally driving over with a bottle. That is not a process. It is a kindness. By ring 3 (strangers), the kindness has to be a policy.
- The Founder Edition story commits to "personal install consultation" (per [`install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) sibling), but the *post*-install story stops there. Concentrate logistics is the dominant ongoing touchpoint and the one most likely to be the customer's first negative interaction with the product.

The cost of getting this wrong at ring 1 is one bad anecdote that propagates through a friend network. The cost of getting it right at ring 1 is a procedure that scales to the public Standard Edition four years later.

---

## The five failure modes in detail

### Failure mode 1 — Single-SKU Amazon stockout (likely: 1-3× per year per SKU, weeks each)

SodaStream sells direct on sodastream.com, but the founder's Amazon-Prime-only mental model — and probably most customers' shopping model — treats Amazon as the only practical channel. Amazon stockouts on the SodaStream-Pepsi line are routinely visible in the price-tracking review history of the listings (camelcamelcamel-style data shows multi-week gaps).

**Customer impact:** preferred flavor unavailable from the channel they actually use. They may not know sodastream.com sells direct. Even if they do, sodastream.com shipping is slower, packs differently, and the friction is enough to register as a degraded experience.

**Mitigation cost:** low. The fix is a customer communication that says "this SKU is currently low on Amazon; here's the sodastream.com link and our 2-bottle pantry buffer recommendation." Cost = a help article + an order email. Not having that article means each customer figures it out alone, and a fraction of them text the founder.

### Failure mode 2 — Prime-ineligible third-party fulfillment

The Prime SodaStream-Pepsi listings disappear, the bottles remain visible on Amazon but only via third-party sellers at +30-50% markup, with multi-week ship times and meaningful counterfeit risk.

**Customer impact:** indistinguishable from a stockout for the AGENTS.md "non-Prime listings do not exist" customer. Worse for the customer who doesn't know about counterfeiting and buys from a sketchy reseller, gets an off-flavor or mislabeled product, and blames the appliance.

**Mitigation cost:** medium. Requires us to monitor Amazon listings on the SKUs we depend on (a cron job; a few hundred lines of code), detect the Prime-eligible-to-third-party transition, and notify customers proactively before they reorder.

### Failure mode 3 — Amazon delisting while sodastream.com remains

PepsiCo has every commercial incentive to channel-steer toward their owned property. A delisting is the cleanest tool for that. The pattern (other CPG categories) is: prime delist → third-party only → eventually full Amazon delisting while the brand's owned channel persists.

**Customer impact:** the customer must now create a sodastream.com account, register a payment method on a competitor's site (SodaStream sells its own machines that compete with ours), and accept slower fulfillment.

**Mitigation cost:** medium-high. Best done with a buffer-stock policy and a clear customer communication that frames sodastream.com as an alternate channel rather than a downgrade.

### Failure mode 4 — Bottle / cap format change

The current 14.9 fl oz / 440 mL bottle is the input to two hardware decisions in the repo:

- The shared front hopper in `future.md` line 127 is "sized to accept a pour from a SodaStream concentrate bottle without splash."
- The flavor reservoirs in `future.md` line 73 are "sized for 2× SodaStream 0.44 L bottles of concentrate."

A reformat — say, a switch to a pouch, a smaller bottle, a different cap thread — does not break the appliance, but it does break the *pour UX* the appliance was designed against. The customer can transfer concentrate to a different vessel and pour, but that's friction the marketing has not promised.

**Customer impact:** UX regression on the pour path. The hopper might splash with a different bottle geometry. The mental model "one bottle = one refill" might no longer hold.

**Mitigation cost:** low to monitor (track SodaStream packaging changes), high to fix (hopper geometry is built into the enclosure print). The mitigation is *detection* with enough lead time to update the hopper print for new units, not retrofit for shipped units.

### Failure mode 5 — Selective SKU discontinuation

PepsiCo prunes the SodaStream-Pepsi flavor lineup. The `pepsi.md` line 199 mitigation is "PepsiCo has been *expanding* the SodaStream flavor lineup (Mountain Dew added 2024, Wild Cherry 2025)" — which is true today, but expansion-then-pruning is the normal CPG pattern, not a one-way trajectory.

The asymmetry: from the customer's perspective, the SKU that disappears is *always the one they preferred*. The customer who drinks Diet Mountain Dew exclusively will not be consoled by the survival of Mug Root Beer.

**Customer impact:** catastrophic for the customer whose preferred flavor goes. The appliance still works, but the entire emotional logic that drove the $7,500 purchase ("real Diet Mountain Dew on tap") collapses.

**Mitigation cost:** the highest. The only real hedge is the BiB path (`future.md` line 89), which today is hardware-present and business-absent — see the dedicated section below.

---

## The BiB path is hardware-ready and business-missing

The rear-panel BiB adapter on the appliance was a deliberate hardware decision: it gives the appliance a second source of flavor input, parallel to the SodaStream-concentrate hopper. `future.md` line 89 names this explicitly: *"The BiB adapter is present but not prominently marketed; it serves customers who source their own commercial syrup."*

The problem: *commercial syrup* is the very thing `pepsi.md` line 186 says home consumers can't buy. From line 186: *"Pepsi and Coca-Cola will not sell commercial syrup to home consumers without a business license."* So the BiB path, as written, requires the customer to *be* the business — open a wholesale account, source from a Pepsi/Coke distributor (Pepsi Beverages Company for Pepsi, Coca-Cola Bottling for Coke), and accept a 5 gal BiB MOQ ($60-90/box, ~5-7 gallons of dispensed concentrate per box, much larger than home use).

For ring 1, where buyers are friends and family who can be told "open a business if you want this," the BiB path is theoretical-OK. For ring 3 strangers, it's an unanswered business question with three components:

1. **Who is the BiB supplier of record?** A Pepsi Beverages Company distributor sells to convenience stores and restaurants on a route-truck basis, not to consumers. A reseller (Soda Pop Bros, etc.) sells small-format syrup to home users but is itself a vulnerable single-source channel. The repo names neither.
2. **Can the founder open a BiB-reseller wholesale account on the customer's behalf?** This is the natural Standard-Edition play: each unit ships pre-paired with a flavor-subscription service operated by the appliance maker. But operating a flavor subscription is a small operational business in itself — the founder is currently building a hardware product, not a syrup distribution business. The pie-in-the-sky [`co2-service.md`](../../pie-in-the-sky/co2-service.md) directionally proposes this for CO2; nothing analogous exists for concentrate.
3. **Is BiB-from-a-reseller actually the same product as SodaStream-Pepsi concentrate?** Probably not. SodaStream concentrate is a sucralose / no-sugar formulation specifically tuned to home dilution (1:20 per `pepsi.md` line 183). Commercial BiB syrup (Pepsi fountain) is a HFCS formulation at 1:5 dilution for soda-fountain valves. These are *different products* under similar marketing names. A "Diet Mountain Dew" customer who switches from SodaStream concentrate to Pepsi fountain BiB will taste the difference. The "real Diet Mountain Dew" claim is intact, but the *specific* "real Diet Mountain Dew" they fell in love with is not.

This third point is the trickiest. The marketing in `target-market.md` line 266 says *"Same formulation, colder, fizzier than a can. It does."* — referring to the SodaStream-Pepsi 1:20 sucralose concentrate. The BiB path supplies a different formulation. The customer's first switch from SodaStream concentrate to BiB will challenge the "indistinguishable from canned" claim that anchors the buying decision.

So the BiB path as a *catastrophic-failure hedge* is real (the appliance still produces drinkable soda even if SodaStream concentrate vanishes globally). The BiB path as a *daily-replacement substitute* is not. This nuance has to be communicated honestly to buyers, not finessed.

---

## Concentrate shelf life and chilled-reservoir storage

A blind spot in `future.md`: the flavor reservoir nests inside the cold core at 8-15 °C (line 81). Concentrate bottles are labeled and tested by PepsiCo for shelf-stable ambient storage; we have no characterization of how the formulation behaves after weeks at 8-15 °C in our specific reservoir geometry.

Questions:

- **Date code:** what is the typical "best by" date on a SodaStream-Pepsi bottle as received from Amazon? (Reports online suggest 12-18 months out, but per-SKU and per-channel variance is real.)
- **Open vs. closed:** SodaStream's user-facing guidance is roughly "store opened bottles refrigerated, use within 3 months." Our reservoir is effectively a long-open-bottle. With a vented but filtered reservoir, microbial risk is low (sucralose + sodium benzoate / potassium sorbate preservatives + acid pH), but unverified.
- **Cold-temperature precipitate / haze:** some sucralose/benzoate beverage syrups develop visible haze or crystallization below 10 °C. Worst case, a refrigerated reservoir produces a visibly off-spec concentrate. Has anyone observed this on the prototype? `welding-progress-2026-05-09.md` and similar docs talk about hardware progress but I don't see flavor-stability bench notes.
- **The clean cycle in `future.md` line 73** ("software-controlled rinse cycle (water in, water out to nozzle, air in, air out to nozzle, repeat)") implies the reservoir is periodically emptied. What is the cadence? Is it before each refill, or only when prompted? Does cleaning destroy partial-bottles or does the bottle remainder go back in?

These are bench questions, not policy questions, but they belong in this gap because the answer determines our *practical* buffer-stock capacity. If concentrate is good for 12 months refrigerated and 3 months opened, the appliance maker can pre-ship a 6-month flavor pack with each unit and the customer effectively never sees an Amazon stockout. If it's good for 1 month refrigerated, that strategy is impossible and the appliance maker has to operate an active subscription.

---

## Recommended playbook (for review, not direct action)

The pattern, in priority order:

### Step 1 — Establish a single source of truth for "launch flavors"

There are at least three lists in the repo:
- `target-market.md` line 11: Diet Mountain Dew, Diet Pepsi, Pepsi Zero Sugar.
- `pepsi.md` lines 168-178: eleven SKUs in the SodaStream-Pepsi lineup.
- Firmware bitmaps (per `trademark-and-brand-name-usage-gap.md` finding #2): Diet Wild Cherry Pepsi, Diet Mountain Dew, Diet Coke. Diet Coke is not in the SodaStream-Pepsi lineup — it would have to come from a non-PepsiCo source.

A `business/concentrate-supply.md` (new file) should pick the launch flavors, name the supplier-of-record for each, and own this list.

### Step 2 — Monitor the SKUs we depend on, programmatically

A scheduled job — pattern is identical to the hourly-todo-filler this doc was generated by — polls the Amazon listings for our launch SKUs once a day, records Prime-eligibility / "Currently unavailable" / third-party-only state, and surfaces transitions. Detection lead time turns failure mode 2 (Prime-ineligible) and failure mode 3 (delisting) from "customer notices first" into "we notice first."

Cost: a few hundred lines of code, runs on the same infrastructure as the existing hourly tasks.

### Step 3 — Define the buffer-stock policy

Two anchor choices and let the math settle:

- **Per-unit ship pack.** Each Founder Edition ships with N bottles of each launch flavor. At 11 SKUs × 2 bottles × $7 = ~$150 of concentrate per unit. Trivial on a $7,500 BOM. Buys roughly 6 weeks per flavor at typical 2-soda-per-day use. **Recommendation: ship with launch flavors only (not all 11), at 4 bottles each — covers 3 months per flavor for one drinker.**
- **Maker-side warehouse.** The founder keeps a 30-day buffer of each launch flavor in the workshop. At 12 units/year and 4 bottles/SKU/month, that's ~$300/month of inventory, possibly less. Reasonable for ring 1 and ring 2; reconsidered when Standard Edition opens.

### Step 4 — Customer communication template

A short canned response — email + iOS-app notification — for the three customer-facing failure modes:

- **Mode 1+2** ("your flavor is hard to get from Amazon this week"): one-paragraph note, link to sodastream.com, recommendation to keep a 2-bottle pantry buffer.
- **Mode 3** (delisted from Amazon entirely): same note, plus a one-time "we'll send you 4 bottles on us" gesture for early customers.
- **Mode 5** (PepsiCo discontinues a flavor): personal call from founder; offer to ship a replacement-flavor pack and walk through the BiB path with appropriate caveats.

### Step 5 — Operationalize the BiB hedge

Three deliverables:

1. **A named BiB supplier-of-record per flavor.** Even if it's a small reseller, the customer needs a known path.
2. **A taste-comparison document.** Honest side-by-side notes: SodaStream-Pepsi sucralose 1:20 concentrate vs. Pepsi fountain HFCS 1:5 BiB syrup, taste differences, what to expect.
3. **A pricing-and-MOQ table.** What does a 5-gal BiB cost, how long does it last in our reservoir, who carries the loss if the customer doesn't finish a BiB.

This pairs cleanly with [`co2-supply-ownership-gap.md`](../2026-05-18/co2-supply-ownership-gap.md) — both are "we own the consumable supply problem the customer didn't sign up to solve."

### Step 6 — Bench-test the concentrate in the actual reservoir

A 3-month chill test on the prototype reservoir, per launch flavor. Look for: visible precipitate, haze, off-flavor, separation, biofilm. Document in `hardware/flavor-stability.md` (new file).

If concentrate is stable for 3+ months at 8-15 °C, the per-unit ship pack of step 3 is a high-leverage move and the customer effectively never sees a stockout for the first quarter. If concentrate is only stable for 4-6 weeks, the per-unit pack is wasted inventory and we need an active subscription.

This is the empirical question that gates the whole strategy. It should be answered on the bench in May/June 2026 before the first Founder Edition ships, not discovered in a ring-1 customer's kitchen six months in.

---

## Where this lands in the repo

When acted on, this work produces:

1. **`business/concentrate-supply.md`** (new) — supplier-of-record per launch SKU, buffer-stock policy, customer-communication policy. Sibling to `business/regulatory.md`.
2. **`hardware/flavor-stability.md`** (new) — bench-test plan and results, refrigerated shelf-life data, haze/precipitate observations.
3. **`pie-in-the-sky/concentrate-service.md`** (new) — the eventual concentrate-subscription analog of `pie-in-the-sky/co2-service.md`, with the BiB-wholesale-account analysis.
4. **A small daily scheduled job** — Amazon-listing monitor, in the same hourly-task infrastructure as this doc.
5. **An edit to `marketing/competitors/pepsi.md`** — replace the brief "Supply Chain Risk" section's framing with the per-SKU / per-channel failure-mode taxonomy, and cross-link to `business/concentrate-supply.md`.
6. **An edit to `marketing/target-market.md`** §"What's the ongoing hassle?" — replace "Syrup every few weeks (Amazon)" with a more honest description that covers the buffer-stock and sodastream.com fallback. The marketing should not over-promise Amazon-Prime availability for products that PepsiCo prices, packages, and channels at its sole discretion.

---

## What this is not

- Not a contracted-supply-from-Pepsi proposal. The strategic asymmetry is real: PepsiCo has every reason to channel-steer toward SodaStream's owned machines and zero reason to enter a relationship with a 12-unit/year competitor in the home-dispense category. Pursuing a supply contract is a multi-year corporate-development effort with low odds. Not where to spend time.
- Not a recommendation to add a third or fourth flavor slot to the hardware. The two-flavor design in `future.md` is right for the form factor and the price point. Resilience comes from supply diversity within two slots, not more slots.
- Not a request to drop the SodaStream-Pepsi positioning. It's the right marketing for the right reason. The fix is operational backstop, not marketing pivot.
- Not in scope: full-sugar / non-diet expansion (called out as an adjacency in `target-market.md` line 282, not a launch concern).

---

## Open questions for Derek

1. **How many launch flavors?** The marketing says three (Diet Mountain Dew, Diet Pepsi, Pepsi Zero Sugar). The firmware ships bitmaps for three but a different three (with Diet Coke instead of Diet Pepsi / Pepsi Zero Sugar). What is the actual launch list?
2. **Is the founder willing to operate a flavor-subscription service in years 2-3?** That's the natural Standard Edition complement, and it's a significant operational shift from "hardware company" to "appliance + consumables company."
3. **Has anyone bench-tested concentrate in the chilled reservoir for >30 days?** If yes, where are the notes. If no, this should happen in parallel with the next welding milestones.
4. **What does the ring-1 customer get when their flavor stocks out?** A text from the founder is the right ring-1 answer. A standing policy is the right ring-3 answer. The transition between them is when we need this work.

---

## Sources within the repo

- [`marketing/competitors/pepsi.md`](../../marketing/competitors/pepsi.md) §"SodaStream Syrup Partnership: Our Supply Chain" and §"Supply Chain Risk"
- [`marketing/competitors/sodastream.md`](../../marketing/competitors/sodastream.md) §"Current Product Line"
- [`marketing/target-market.md`](../../marketing/target-market.md) line 11 (launch flavors), line 269 (ongoing-hassle promise), line 282 (sugar-soda adjacency)
- [`hardware/future.md`](../../hardware/future.md) lines 73 (reservoir sizing), 81 (reservoir temperature), 89 (BiB adapter), 127-128 (hopper)
- [`pie-in-the-sky/co2-service.md`](../../pie-in-the-sky/co2-service.md) — pattern for an analogous concentrate-service doc
- [`AGENTS.md`](../../AGENTS.md) "Amazon Prime" memory — the founder's (and probable customer's) Amazon-Prime-only shopping model
- [`todo/2026-05-18/co2-supply-ownership-gap.md`](../2026-05-18/co2-supply-ownership-gap.md) — the consumable-supply gap from the prior day, structurally similar
- [`todo/2026-05-19/trademark-and-brand-name-usage-gap.md`](trademark-and-brand-name-usage-gap.md) — the firmware-bitmap flavor mismatch is named there and partially overlaps step 1 above
