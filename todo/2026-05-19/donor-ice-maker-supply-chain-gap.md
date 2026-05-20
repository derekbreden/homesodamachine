# Donor ice maker supply chain: two pinned Amazon ASINs carry the refrigeration subsystem for 50 hand-built units over four years

**Author:** hourly agent, 2026-05-19 (late)
**Status:** recommendation only — not for direct execution
**Audience:** future agents, Derek
**Distinct from siblings:**
- 2026-05-19 sibling [`concentrate-supply-resilience-gap.md`](concentrate-supply-resilience-gap.md) covers Pepsi/SodaStream syrup SKU stockouts on the *consumables* path. This doc is the same risk pattern on the *durable BOM* path: the refrigeration subsystem is sourced by harvesting a countertop ice maker, and the ice-maker SKU is at least as volatile on Amazon as a CPG concentrate bottle — but the consequences are different. Concentrate stockouts inconvenience the customer; donor stockouts stop production.
- 2026-05-18 sibling [`appliance-freight-bench-gap.md`](../2026-05-18/appliance-freight-bench-gap.md) covers *outbound* shipping of the finished unit. This doc is *inbound* component sourcing.
- Existing [`hardware/harvested/ice-maker/README.md`](../../hardware/harvested/ice-maker/README.md) is a *teardown* document — what the parts are, how to identify them. It is not a *sourcing* document — what to do when one of the two named SKUs is gone.

The two are adjacent, but the actions are different. The teardown doc tells you what to expect inside a B0F42MT8JX. This doc is about what happens when B0F42MT8JX no longer exists on Amazon, or still exists but ships with different internals.

---

## TL;DR

The refrigeration subsystem of every Founder Edition unit is sourced by harvesting a countertop ice maker. Per [`hardware/future.md`](../../hardware/future.md) line 49, two specific Amazon SKUs are named:

- **Unit A** — generic Antarctic Star HZB-12/Q, [B0F42MT8JX](https://www.amazon.com/dp/B0F42MT8JX), $63.80
- **Unit B** — Frigidaire EFIC117-SS, [B07PCZKG94](https://www.amazon.com/dp/B07PCZKG94), $78.70

A documented fallback exists — [`hardware/future.md`](../../hardware/future.md) line 60 names the **RIGID DV1910E** (~$580 from Lanxi Lizhide Refrigeration Equipment Co., Ltd via ChinaPost, per [`hardware/purchases.md`](../../hardware/purchases.md)) as a factory-sealed pre-charged module that can replace the harvest path. But the fallback is **not a second source** in the conventional supply-chain sense — it is a different architecture. Switching to it changes:

- Per-unit BOM cost (+$500/unit, ~9× the donor price)
- Lead time (Amazon Prime 2-day → ChinaPost ~26 days observed)
- Procedure: [`hardware/assembly/refrigerant-loop.md`](../../hardware/assembly/refrigerant-loop.md) is written entirely around vent-cut-braze-recharge of a donor. The RIGID path skips all of that — different procedure document needed.
- Enclosure layout: the side-mount condenser-and-fan in [`hardware/future.md`](../../hardware/future.md) lines 96-101 is harvested as a unit *with* the donor. RIGID is a 12 V chiller without a matching condenser/fan in the same package.

The 50-unit Founder Edition run means 50 donor harvests over ~4 years at 12 units/year. The probability that either named ASIN ships the same internal topology for four straight years on Amazon is low. The probability that *both* survive is lower.

What is not in the repo:

- No buy-ahead policy at ring 1, when supply is verified and prices are low.
- No incoming-inspection acceptance test against the documented topology. The teardown README is rich on what a *known-good* unit contains, but there is no procedural test that says "before you cut the box open and start brazing, verify these N attributes."
- No third-source SKU pre-characterized. If both named ASINs go dark on the same week, the production line stops.
- No per-unit serial-number → donor-ASIN-and-batch traceability requirement. If a refrigerant-loop failure surfaces in field unit #008 two years post-install, "which donor batch did this come from" is a question the repo cannot answer.
- No business-side accounting for the cost-bump scenario. At Founder Edition $7,500, a $500 BOM jump on the donor is absorbable. At ring-1 friend-pricing $2,000-3,000 (per [`marketing/target-market.md`](../../marketing/target-market.md) line 174), a $500 BOM jump is a meaningful margin event.

---

## Why this is worth a focused doc, not a line in the teardown README

The existing teardown README is correctly framed as a reference manual: *what is inside this specific unit, how to identify it, how to harvest it*. It serves the build procedure perfectly. It does not serve the question that comes earlier in the supply chain: *will the unit on my doorstep next month match the document?*

The answer to that question has nothing to do with the technical content of the teardown. It has to do with how Amazon ASINs behave for low-end appliances:

1. **No-name ASINs cycle off Amazon routinely.** The "generic" Antarctic Star HZB-12/Q listing (B0F42MT8JX) is the cheaper of the two, the more obscure of the two, and the one with the cleaner topology (8-cube cycle, simpler controls). It is also the one most likely to be a transient listing — these branded-by-the-listing-not-the-factory products are typically rebadged by the importer-of-record on each container, with ASIN continuity not guaranteed past a single shipping cycle.
2. **ASIN reuse with internal swaps.** The listing stays alive, the product photo stays the same, but the unit inside the box changes manufacturer, compressor model, refrigerant charge mass, drier outlet bore, capillary length, or hot-gas bypass topology. The teardown README locks in topology details that were *verified by disassembly on 2026-04-17* (line 24); none of those are guaranteed by the ASIN.
3. **Voltage-variant collisions.** [`harvested/ice-maker/README.md`](../../hardware/harvested/ice-maker/README.md) line 27 already calls out that the HZB-12/Q ships in two voltage variants — 110-120 V US and 220-240 V UK — and that only the compressor electrical spec differs. The risk is that Amazon US starts cross-shipping the UK variant under the same ASIN during a US-side stockout, which has happened with other small appliances. A 220 V compressor on a 120 V build is not a survivable error — it's a smoke event.
4. **Frigidaire SKU lifecycle.** The EFIC117-SS is a branded SKU (B07PCZKG94) which is more stable than the generic, but small-appliance branded SKUs have lifecycles of 2-5 years, after which a successor model takes the same shelf space. Frigidaire's EFIC189-family manual (cited at [`harvested/ice-maker/README.md`](../../hardware/harvested/ice-maker/README.md) line 153) already shows the model is part of a family that has been refreshed before. The successor model will not necessarily share the BLC48AD compressor, the 23 g R-600a charge, or the fan/condenser geometry that the side-mount enclosure layout depends on.

None of these failure modes is hostile or strategic — they are the normal background noise of sourcing low-cost durable goods from Amazon. They will happen at some point during the 4-year Founder Edition window. The only question is whether they happen before or after a buy-ahead policy is in place.

---

## The four failure modes in detail

### Failure mode 1 — Generic SKU goes dark (likely within 12 months)

The Antarctic Star HZB-12/Q listing (B0F42MT8JX) is the more vulnerable of the two. Generic-rebadge ASINs for $60 appliances routinely show 30-90 day Amazon stockouts and full delistings within 1-2 years. The product itself continues to exist — the same factory in China continues to ship the same HZB-12/Q — but under a different US importer's ASIN with a different brand sticker.

**Impact on the build:** the teardown topology that the production refrigerant-loop procedure is written against — R-600a charge of 15 g, Compressor HD48Y11A from NingBo Anuodan, "60-130-05" drier label — is specific to this ASIN's *current* fulfillment chain. A new ASIN selling the apparently-same HZB-12/Q model from a different importer is not guaranteed to ship the same internals.

**What is missing:** a documented procedure to qualify a new generic-class donor before committing the build session to it. Specifically: a pre-vent inspection step that records the back-panel rating label, compressor model, drier label, and refrigerant charge mass — and compares them to the recorded topology in [`harvested/ice-maker/README.md`](../../hardware/harvested/ice-maker/README.md). If the topology differs in any load-bearing way (different compressor model, different cap-tube routing, different refrigerant), the unit is not a drop-in donor and the procedure has to be re-validated against it.

**Mitigation cost:** low. The fix is a one-page incoming-inspection checklist appended to [`hardware/assembly/refrigerant-loop.md`](../../hardware/assembly/refrigerant-loop.md) before step 1, plus a per-unit build record that captures the inspection result. The teardown README already documents *what* to look for; this just makes inspection a procedural gate rather than implicit knowledge.

### Failure mode 2 — Branded SKU successor replaces EFIC117-SS

Frigidaire (or whichever importer holds the Frigidaire-branded countertop ice maker line) refreshes the product. The EFIC117-SS is replaced by an EFIC120-SS or similar successor, sold under the same product family, possibly using a different compressor manufacturer, refrigerant charge, or internal topology.

**Impact on the build:** the production refrigerant-loop procedure currently uses two distinct factory charge targets — 15 g for Unit A and 23 g for Unit B (per [`refrigerant-loop.md`](../../hardware/assembly/refrigerant-loop.md) step 1). A successor SKU adds a third factory charge mass and possibly a third evaporator geometry, both of which feed into the open item §1 calibration. The empirical first-run-up iteration on charge mass would need to be re-run against the new donor.

**Mitigation cost:** medium. Each new donor SKU is a small build-time-engineering effort: verify topology, re-derive recharge target, update the teardown README with a Unit-C section.

### Failure mode 3 — Both named SKUs unavailable simultaneously

A worst-case stockout where neither Amazon listing is fulfillable in a build-cycle-relevant window. The next build is scheduled, the cold core is finished, the customer is on the build schedule — and there is no donor.

**Impact on the build:** the documented fallback is the RIGID DV1910E. But that path is not a drop-in replacement; it is an architecture change:

- RIGID is a factory-sealed module — no vent, no braze, no recharge. [`assembly/refrigerant-loop.md`](../../hardware/assembly/refrigerant-loop.md) does not apply.
- RIGID has its own evaporator geometry (a flexible copper coil per [`future.md`](../../hardware/future.md) line 60) that wraps around the carbonator. [`assembly/cold-core.md`](../../hardware/assembly/cold-core.md) coil-winding procedure would need a fork.
- RIGID lacks the harvested ice-maker's condenser + fan as a co-packaged unit. The enclosure layout's side-mount condenser/fan story breaks; a separate condenser sourcing decision is needed.
- RIGID lead time on the one observed order was Apr 1 → Apr 27 = ~26 days from ChinaPost. That is incompatible with any kind of just-in-time build schedule. A unit booked for build in 3 weeks cannot wait for RIGID to arrive.

**Mitigation cost:** medium-high. Either keep a buffer stock of RIGID modules on the shelf (capital tied up, but a real second-source), or pre-characterize a *third* Amazon donor SKU (a Frigidaire-EFIC189 sibling, a GE Profile countertop, a Newair) so that "both named SKUs unavailable" doesn't immediately fall through to the China-imported $580 fallback.

### Failure mode 4 — ASIN-reuse internal swap (silent, dangerous)

The ASIN B0F42MT8JX continues to be live on Amazon. The product photo doesn't change. The price doesn't change meaningfully. But the unit inside the box is different: different compressor manufacturer, different refrigerant (R-134a instead of R-600a — possible if the importer is sourcing from a factory line that runs both), different cap-tube length.

**Impact on the build:** this is the failure mode that *can hurt people*. R-134a in place of R-600a means:

- EPA 608 venting prohibition applies — venting to atmosphere is illegal, requires recovery equipment we do not own.
- The cold-core safety architecture (compressor shroud, SF76E thermal fuse, MQ-6 hydrocarbon sensor) is designed around the failure modes of a flammable hydrocarbon. R-134a has a different (much smaller) ignition risk but a different (asphyxiation) leak risk that the current architecture doesn't address.
- The recharge target mass would be different (R-134a has different operating density).

**What is missing:** the [`refrigerant-loop.md`](../../hardware/assembly/refrigerant-loop.md) procedure step 1 currently says *"If the donor is anything other than R-600a (R-134a, R-410a, any HFC), this procedure does not apply"*. Good — that catches the case at vent time. But that's mid-procedure, after the unit has been shipped, unboxed, partially disassembled, and the build session is already underway. The check belongs *before* the build session begins, at receiving inspection, when there is still time to refuse the donor and source a different one.

**Mitigation cost:** trivial. Move the refrigerant-type check from procedure step 1 to a pre-procedure receiving inspection step. Photograph the back-panel rating label on every unit received and archive it under the build record.

---

## What a buy-ahead policy looks like at Founder Edition scale

The Founder Edition commits to 50 units over ~4 years. The donor harvest is one ice maker per build. At ring-1 / ring-2 pricing (per [`target-market.md`](../../marketing/target-market.md) line 174), the founder is absorbing the cost; at full Founder Edition price, the buyer is.

A modest buy-ahead policy looks like:

1. **Today** — while both ASINs are verified and Prime-eligible, buy 4-6 of each ($63.80 × 5 + $78.70 × 5 = ~$712), enough to cover the next 8-10 builds. Storage footprint is modest (small countertop appliances stack in a closet; ~2 ft³ each). Capital exposure is ~$700.
2. **Per-build trigger** — when the on-hand donor count drops below 4 of either type, reorder. This is the simplest possible reorder policy: a constant reorder point, not a forecast.
3. **Quarterly verification** — once per quarter, place an order for one *new* unit at each ASIN to confirm the ASIN is still live and the topology hasn't changed. Use the receiving inspection to detect ASIN-reuse swaps (failure mode 4 above) before they show up in a production build.
4. **Third-source pre-qualification** — over the first year, evaluate one additional R-600a small-appliance SKU as Unit C. The pre-qualification effort is a single teardown plus a single test build. The output is a Unit C section in [`harvested/ice-maker/README.md`](../../hardware/harvested/ice-maker/README.md). At the end of year one, the production line has three qualified donor SKUs, not two.

The cost of the policy is the standing inventory (~$700 at any time) and the quarterly verification spend (~$60-80/quarter = ~$280/year). The cost of *not* having the policy is a production stoppage at some point during the 4-year run, with the only available recovery being either a 26-day wait for ChinaPost or a re-engineering effort against a new donor under deadline pressure.

---

## Per-unit traceability — connecting donor batch to field unit

Separate from the supply-chain resilience question above is the traceability question: when a refrigerant-loop failure surfaces in a customer's unit 18 months post-install, which donor went into which build?

The repo currently has the donor → build relationship documented only in narrative form (the teardown README references "this unit", "the donor we bought"). For 50 hand-built units over 4 years, the operationally useful artifact is a per-unit build record that captures:

- Serial number (already implied by Founder Edition plaque, but the plaque is what the customer sees — the build record is what the founder consults at service time)
- Donor ASIN purchased for this build
- Donor's manufacturer rating label (refrigerant type, charge mass, model number, manufacture date code)
- Recharge target used (the empirical first-run-up number from refrigerant-loop §7)
- Compressor cast-stamp and PTC-relay/overload module sticker (failure correlation if a batch of compressors turns out to be defective)

This is a build-time form that takes ~5 minutes per unit to complete and lives alongside the per-unit portal data flagged in the [`per-unit-portal-gap.md`](../2026-05-18/per-unit-portal-gap.md) sibling. The traceability data is internal-only; the customer-facing per-unit page is a separate concern.

---

## Recommendation priorities

1. **(Same-day, costs nothing)** — Add a "Receiving inspection" section to [`hardware/assembly/refrigerant-loop.md`](../../hardware/assembly/refrigerant-loop.md) before step 1. Refrigerant type, charge mass, compressor model, drier label — recorded and compared to [`harvested/ice-maker/README.md`](../../hardware/harvested/ice-maker/README.md) before any cut is made. This pre-empts failure modes 1 and 4.
2. **(This week, ~$700 capital)** — Buy 4-6 of each named donor SKU now, while both are verified Prime-available. Stockpile in storage. Adopt a constant reorder-point inventory policy.
3. **(This quarter)** — Pre-qualify a third donor SKU (the Newair NIM026 or a Frigidaire EFIC189 sibling are candidates; both are R-600a-class small appliances in the same retail tier). One teardown + one test build = one additional qualified source. Adds a Unit C section to the harvested README.
4. **(This quarter)** — Stand up a per-unit build record sheet that captures donor traceability data, separate from the customer-facing per-unit portal.
5. **(Defer to ring 2)** — Decide whether to buffer-stock the RIGID DV1910E as a true emergency third source, or whether the third-Amazon-donor approach (above) is sufficient. The decision depends on whether the third Amazon donor's qualification holds up after a few production builds.

None of these recommendations changes the appliance. All of them harden the *path* by which 50 appliances actually get built without a production stoppage caused by a $64 Amazon listing going dark on a Tuesday in 2027.

---

## Pointers to existing docs

- [`hardware/future.md`](../../hardware/future.md) lines 49-60 — names the two donor ASINs and the RIGID fallback
- [`hardware/harvested/ice-maker/README.md`](../../hardware/harvested/ice-maker/README.md) — full teardown of Unit A, pre-teardown notes on Unit B
- [`hardware/assembly/refrigerant-loop.md`](../../hardware/assembly/refrigerant-loop.md) — the production procedure that assumes a known-good donor
- [`hardware/purchases.md`](../../hardware/purchases.md) §6 — ledger entries for both donors plus the RIGID order to Lanxi Lizhide
- [`hardware/bom.md`](../../hardware/bom.md) §5 — per-unit BOM allocation
- [`marketing/target-market.md`](../../marketing/target-market.md) lines 174-180 — ring-1 friend pricing, which is where a BOM cost bump bites hardest
- Today's sibling [`concentrate-supply-resilience-gap.md`](concentrate-supply-resilience-gap.md) — same risk pattern on the syrup side, useful as a structural reference for how to write up the BiB-equivalent secondary-source plan
- Today's sibling [`fielded-unit-firmware-update-gap.md`](fielded-unit-firmware-update-gap.md) — adjacent failure-handling concern (what happens when a field unit needs intervention), motivates the per-unit build record above
