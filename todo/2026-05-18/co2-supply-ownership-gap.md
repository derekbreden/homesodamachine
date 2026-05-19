# CO2 supply: closing the named rough edge of ownership

**Author:** hourly agent, 2026-05-18
**Status:** recommendation only — not for direct execution
**Audience:** future agents, Derek
**Sibling today:** [firmware-manifold-gap.md](firmware-manifold-gap.md) — distinct focus area; that one is hardware/firmware build-readiness, this one is the customer-ownership experience after delivery.

## TL;DR

[marketing/target-market.md:272–274](../../marketing/target-market.md) is the only place in the repo that calls out an explicit gap in the product story:

> CO2 refills currently require a trip to a welding gas supplier during business hours. We message this honestly: "CO2 lasts months. When it runs out, a local gas supplier refills it." In the medium term, we explore delivery options, partnerships, or alternative sources. **This is the one piece of the ownership experience that doesn't yet meet the standard of the rest of the product.**

The technical inlet side is done — [bom.md §4](../../hardware/bom.md) has a two-stage regulator (customer's CGA-320 primary → in-appliance WR1110 fixed 90 PSI) feeding the sparge stone, locked at a working pressure with a 35 PSI margin to the SV-125 PRV. Derek's running prototype has been on a Feb-13 5 lb food-grade Airgas cylinder for three months ([purchases.md:75](../../hardware/purchases.md)). The plumbing is real.

What is missing, end-to-end:

1. **No customer-facing CO2 doc.** The only mention of customer CO2 in shipping-doc form is one line in [bom.md:262](../../hardware/bom.md) ("5 lb CO2 tank + refills (~$25/refill at welding/homebrew shops)") under "External / user-supplied (not shipped)." There is no `docs/co2-supply.md`, no install-kit doc, and no messaging in any web/marketing artifact.
2. **No monitoring.** The appliance has no idea how much CO2 is in the customer's cylinder. The carbonator has reed-based level sensing for the water side (low-/high-level reeds, [future.md:37](../../hardware/future.md)) but nothing on the CO2 side — no pressure transducer, no flow meter, no consumption accounting. The customer discovers the empty tank when soda stops being soda.
3. **No supply-side playbook.** No supplier-finder, no list of national chains that fill CGA-320 5 lb food-grade, no fallback when the local Airgas isn't open. Derek's own supplier (Airgas Lincoln NE) is hardcoded in the purchases ledger only because he's the customer.
4. **No Ring 1 measurement plan.** The "CO2 lasts months" claim is not based on instrumented data from this product. SodaStream's 60 L cartridge is calibrated for chilled-bottle dispense, not a 6"-tall headspace sparged into 1.6 L of water at 90 PSI. Our actual cylinder life per dispense is unknown.

This is a **Ring-1-and-Ring-2 readiness gap**, not a hardware blocker. Unit #1 can ship without it. The first 10 customers will hit it within 2–8 weeks of install (estimate; see §5), and the recovery experience is what will or won't validate the $7,500 Founder Edition story.

## Why this matters more at Founder Edition than at Standard

The trust-gap argument in [target-market.md:256–262](../../marketing/target-market.md) — "at Founder Edition scale, the brand is a person" — cuts both ways. A clean recovery from an empty cylinder is a story Derek will be told back ("the app pinged me, the local place was on the list, twenty minutes done"). A bad one ("first time it ran out, I drove to three places, no one had it") is the *only* daily-life touchpoint where the customer goes back to behaving like a SodaStream owner. The whole product is positioned against the can-haul; the CO2 refill, today, is a can-haul.

This is also the one moment a Ring 1 customer would call Derek personally. A documented playbook lets him answer the call in 30 seconds instead of debugging it live.

## What the customer actually has to do today (best reconstruction)

Assembling the picture from [bom.md](../../hardware/bom.md), [future.md](../../hardware/future.md), and [purchases.md §2](../../hardware/purchases.md):

1. **Acquire a 5 lb aluminum food-grade CGA-320 cylinder.** Not shipped with the appliance. Airgas line item "CD FG5" — $124.10 cylinder + $32.59 fill + $12.10 hazmat = $168.79 at customer pickup. Not Prime, not Amazon, not next-day. Customer must drive to a welding-gas branch during business hours, sign for a hazmat receipt, and lift a ~12 lb cylinder into a car.
2. **Connect to the appliance's CGA-320 inlet** on the rear panel. (Documented in [printed-parts/enclosure/back-panel/README.md](../../hardware/printed-parts/enclosure/back-panel/README.md) — not separately re-read here, but the inlet is one of the rear-panel connections in the "umbilical port" inventory.)
3. **Open the cylinder valve. Done — until empty.**
4. **Discover empty by dispense failure.** Symptoms: flat soda, then no soda. No advance warning.
5. **Drive empty cylinder back to a fill location.** Repeat step 1.

Steps 1 and 5 are the rough edge. Step 4 — *the lack of warning* — is what turns step 5 into a "next free morning" problem instead of a "schedule it" problem.

## Specific gaps, sized for follow-up tickets

### C1 — Add a customer-facing `docs/co2-supply.md` (cheapest, do first)

A single canonical doc that answers:

- What cylinder do I need? (5 lb aluminum food-grade, CGA-320, ~12" tall, fits in the under-sink cabinet next to the appliance — confirm physical fit against [enclosure layout](../../hardware/future.md))
- Where do I get it? (Airgas, Praxair/Linde, AirWeld, local homebrew supplier, paintball shop — by category, not specific chains, with a note on the food-grade requirement vs. industrial-grade)
- What does a refill cost and how often? (placeholder pending C5)
- What does "food-grade" mean for CO2 and why does it matter?
- Service-life and replacement guidance (DOT hydrostatic re-test every 5 years on aluminum 3AL cylinders)

Single source of truth, linked from `marketing/target-market.md`, the future web checkout, and the per-unit `homesodamachine.com/u/NNN` page referenced in [future.md:143](../../hardware/future.md).

Estimated effort: ~2 hours of writing, no hardware change.

### C2 — Founder Edition includes a filled cylinder; document the decision

This is a $169 line item on a $7,500 unit (2.3% of price) that closes the most acute friction — "day-one onboarding" — completely. The customer plugs the appliance in, opens the included cylinder, makes their first soda. They are never the person who got it home and then realized they had to drive somewhere.

This needs a documented decision (probably a one-line addition to [target-market.md](../../marketing/target-market.md)'s Founder Edition section and a per-unit BOM line in [bom.md §14 "Install kit"](../../hardware/bom.md)), not a vague intent. At Standard ($5,500) the question is open — the BOM tradeoff is different.

Hidden assumption to validate: can a 5 lb pre-filled cylinder be **shipped** legally and economically to a customer, or does it have to be customer-pickup? Hazmat shipping rules for compressed CO2 are not trivial. Worth a focused legal/logistics check before locking this in. If shipping is prohibitive, the alternative is: ship the appliance with a *certified-empty cylinder* + a $40 voucher / pre-purchased fill at one of N partner suppliers near the customer's ZIP. That's a worse experience but a legal-and-finite shipping problem.

### C3 — Add CO2 pressure monitoring to the BOM and firmware

The appliance currently has:

- DS18B20 ×2 (tank wall + suction line) on the 1-wire bus
- 8 reservoir reeds + 2 carbonator reeds for water-side level
- Sparge stone on the inside-vessel face of Port 1

It does **not** have a pressure transducer or pressure switch anywhere on the CO2 line. Reads from the customer-side regulator's gauge are visual-only and the regulator is under the sink — the customer cannot see it.

Minimum-viable add: one low-cost 0–1500 PSI pressure transducer (0.5–4.5 V ratiometric, e.g. CNBTR-class ~$15) tee'd into the high-pressure side of the CGA-320 regulator inlet, ADC channel on the ESP32 (one of the unused ADC1 pins — pinout in [esp32-pinout.mmd](../../hardware/wiring/esp32-pinout.mmd) should be checked for a free one). Tank-side pressure is a direct read on "is there CO2 left": a full 5 lb cylinder at room temp reads ~830 PSI and stays roughly flat (saturated liquid + vapor) until the liquid is gone, then drops fast to atmospheric over the last ~20% of mass. The cliff is the warning.

Firmware behavior:

- Read pressure every N seconds (slow — this is a slow signal).
- Trigger "order a refill" notification at the first sustained reading below ~700 PSI (cliff onset).
- Trigger "swap now or no soda" notification at ~200 PSI.
- Log the curve to telemetry for the consumption baseline (C5).

This unblocks the iOS app having anything to say about CO2 at all, which today it cannot.

Lower-cost alternative for Ring 1 only: a Gems-style pressure switch (single set-point microswitch, ~$30) that fires once at the low-pressure threshold. No analog readout, no app curve, just "now you need a refill." Cheaper, less informative, sufficient for "did we close the rough edge."

### C4 — Build the supplier-finder before the first ship

The customer needs to be able to answer "where do I refill?" with one click. Today they Google "CO2 refill near me" and get welding suppliers, paintball stores, and homebrew shops in some random order with no info on which fill food-grade.

Cheap version: a markdown table in `docs/co2-supply.md` of national chains that fill food-grade CGA-320, with a link to each chain's branch-finder. Airgas, AirWeld, Praxair / Linde, NuCO2 (commercial only — note this), and the homebrew chain MoreBeer + LD Carlson dealers.

Better version: per-customer manual lookup at unit shipment. The Founder Edition includes a personal install consultation ([target-market.md:91](../../marketing/target-market.md)); Derek can spend 10 minutes finding the customer's three closest food-grade-CGA-320 fill points before the call, and hand it to them in writing. This is a real product of the Founder Edition tier — the customer who paid $7,500 for one of 50 is not Google-searching for CO2 at 7am.

Best version (later): a small web tool at `homesodamachine.com/refill?zip=NNNNN` that returns the same three places. Out of scope for Ring 1.

### C5 — Ring 1 measurement: instrument consumption per pour

The "lasts months" claim should be measured before it's marketed. The math:

- A 5 lb (2.27 kg) CO2 cylinder = ~620 L of CO2 gas at STP
- A 12 oz pour of carbonated water at ~3.5 volumes CO2 (above-can carbonation) contains ~1.24 L of dissolved CO2
- Sparge efficiency is < 100% — some CO2 vents past saturation on the way through
- Headspace replenishment between pours uses CO2 too (vessel headspace ~0.5–1 L compresses back to 90 PSI on every refill cycle)

Naive estimate: 620 L / 1.24 L per pour = ~500 pours per cylinder if sparge efficiency is 100% and no headspace loss. Realistic guess: 150–300 pours per cylinder. At a 3-can/day household = 50–100 days per cylinder. **"Months" is plausible but the floor matters.** Customer expectations live at the floor, not the ceiling.

Ring 1 unit telemetry should log: dispense count, dispense volume, CO2 pressure curve over time, ambient temp, days-between-fills. After 3–6 months of real data across 10 units, the marketing copy can move from "lasts months" to "lasts X–Y weeks at your usage rate, and the app will tell you 1–2 weeks before it runs out." That's a fundamentally stronger product story than the current vague one.

This dovetails into the broader "telemetry from in-home units" question that the rings model in [target-market.md:170](../../marketing/target-market.md) implies but doesn't specify the architecture for. Worth a separate focused todo on its own (out of scope here).

### C6 — Consider the cylinder-swap loaner pool as a Ring 2 product

For Ring 2+, when there are 20+ units in 20+ households, a hub-and-spoke swap-cylinder pool starts to make sense: a customer's app says "low CO2," they click "send a refill," a pre-filled cylinder arrives in 2–3 days, they ship the empty back in the same box. This is the "ongoing hassle" answer in [target-market.md:269](../../marketing/target-market.md) — and the one place where the Founder Edition story ("we built this whole thing for you, including the supply chain") can extend past day 1.

**The shipping picture is asymmetric — see the addendum below.** Return leg is plain UPS Ground under 49 CFR 173.29 (valve open, <29 psig, ships as non-hazmat); only the outbound filled leg is regulated hazmat. That changes the unit economics significantly from a naive "round-trip hazmat" assumption.

Out of scope for unit #1. Worth naming so it doesn't get lost.

### C7 — Hardware-side optionality: SodaStream Quick-Connect adapter

SodaStream's QCC (Quick Connect) cylinders are the friction-free option in the existing consumer-CO2 market — Costco, Bed Bath, Target all swap them for $17 each. They're 60 L cartridges (~133 g of CO2) vs. our 5 lb (2,270 g of CO2) — *17× less* capacity per swap. Bad as a primary supply (a heavy user would do 6–10 swaps per month). Possibly viable as an **emergency bridge** when the customer's main cylinder is empty and the welding supplier is closed.

A small CGA-320 ↔ SodaStream-QCC adapter is a $15–25 commodity. Buying one and including it in the install kit is a near-zero-cost insurance policy. The customer's "what do I do tonight" answer becomes "stop at Costco." No hardware change to the appliance — just an adapter and a documented note in `docs/co2-supply.md`.

This is small and easily reversed; worth piloting on unit #1.

## Migration plan / order of operations

Don't try to land all of these at once. Order matters:

1. **C1 + C4 cheap-version (today).** A markdown doc that lists what cylinder, where to refill, and how to read the gauge. Costs nothing, ships nothing, but the doc is needed by every subsequent step. ~1 day.
2. **C2 decision (this week).** Make the call on whether the Founder Edition includes a filled cylinder, then update [bom.md §14](../../hardware/bom.md) + [target-market.md §"Founder Edition"](../../marketing/target-market.md). Validate the legal/logistics question on shipping a filled cylinder. ~1–2 days of research, ~30 minutes of doc edit.
3. **C3 minimum-viable (before unit #1 firmware freeze).** Add the pressure transducer + ADC pin + a simple two-threshold alert. Couple it to the iOS app notification path. Don't try to ship full curve telemetry yet. ~1 weekend.
4. **C5 (Ring 1 ship — passive).** With C3 done, the data starts logging on its own. Nothing to do at ship time beyond making sure the log makes it back to a queryable place.
5. **C7 (low priority, opportunistic).** Order the adapter, add a line to the install kit. ~10 minutes.
6. **C4 best-version + C6 (Ring 2 era).** Don't build the swap pool or the supplier web tool until there's a customer base it's actually serving.

## Out of scope for this todo

- The broader telemetry architecture (what comes back from in-home units, where is it stored, who can query it). The CO2 curve is one signal; the system needs the rest (refrigeration duty cycle, dispense counts, fault events, water-side reed transitions). Worth a future hourly-agent focus.
- The legal/hazmat detail on shipping a filled CO2 cylinder C2C and the empty return shipping for the C6 swap pool. Real research; out of scope for one agent-hour.
- The food-grade vs. industrial-grade CO2 question (is the difference real for our use case, or marketing?). Worth a focused dive — Airgas charges differently for the two grades and the BOM should know why we're paying for the food-grade SKU.
- The CO2 sensor for the *room* (hydrocarbon leak detection from R-600a is already covered by the MQ-6 in [future.md:107](../../hardware/future.md); a CO2 leak from our supply line is a separate concern — low risk because we leak food-grade gas, not flammable, but a customer "I smell gas" call still gets one).

## Suggested next concrete step

Write `docs/co2-supply.md` (C1) and a 2–3 sentence decision note on C2. Both are doc-only, both unblock messaging work that the rest of the launch sequence depends on. Everything below those two depends on the decisions captured there.

---

## Addendum (added later same day) — the hazmat-shipping picture, in detail

Derek's read of the original recommendation prompted a closer look at consumer CO2 shipping. The picture is sharper than the original recommendation captured, and it changes the C2 / C6 economics meaningfully.

### Why no one ships filled 5 lb CGA-320 cylinders to homes

Derek asked: "Is there any such outfit? I'd be thrilled to pay $400 for a shipped 5 lb bottle — no one offers it that I can tell." Correct — functionally no one offers this, and the reason is structural, not regulatory-impossible.

**The DOT Special Permit (DOT-SP) regime is the mechanism that makes consumer-mail cylinder shipping practical.** SodaStream's 60 L cylinder ships to consumers under [DOT-SP 20796](https://www.phmsa.dot.gov/hazmat/documents/offer/SP20796.pdf/offerserver/SP20796); their 130 L ships under DOT-SP 15634. These permits waive the shipper-certification signature and authorize alternative hazard communication (no Class 2 diamond), enabling the entire "exchange your empty by mail" UX. Drinkmate uses the same permit family ([CO2 Exchange instructions](https://idrinkproducts.com/pages/co2-exchange-shipping-instructions)).

**No DOT-SP exists for a 5 lb CGA-320 / DOT-3AL form factor.** The permits are issued per-applicant, per-form-factor; SodaStream's permit is scoped to their 60 L cylinder and doesn't extend up. No welding-supply distributor has applied for one at the 5 lb size because consumer-parcel isn't their business model — their business is fleet-truck routes to bars, restaurants, and beverage accounts.

Three converging reasons no one's in the middle:

1. **Permit-application work is non-trivial** (rough order-of-magnitude $20–50k + 6–12 months with a hazmat consultancy — to be confirmed; numbers from the [ICC Compliance Center case study](https://www.thecompliancecenter.com/case-study-shipping-carbon-dioxide-cartridges-for-a-consumer-product/) and conversational estimates, not a real quote). SodaStream did it because cylinder exchange *is* their business.
2. **The fully-regulated path works but kills small-volume unit economics.** Per-shipment hazmat surcharge (~$45 ground per UPS's [hazmat guide](https://www.ups.com/us/en/support/shipping-special-care-regulated-items/hazardous-materials-guide)) + UN-rated overpack + trained hazmat employee + Chemtrec retainer + shipping papers. Real, doable, expensive at low volume.
3. **The market is bifurcated.** Small cylinders → permit-enabled consumer mail (SodaStream, Drinkmate). Large cylinders → fleet-truck routes (Airgas, Praxair, NuCO2). The 5 lb form factor is too big for the consumer-mail permits, too small for fleet-truck economics. No one's there because no one's there.

### Correction to the return-leg story — it's not symmetric

The original C6 text said round-trip hazmat shipping ran ~$120–140 per swap. **That's wrong on the return leg.** Per [49 CFR 173.29](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-C/part-173/subpart-B/section-173.29), an empty Division 2.2 non-flammable gas cylinder (CO2 qualifies) is **exempt from the Hazardous Materials Regulations entirely** when:

- residue is a Division 2.2 gas, not ammonia, no subsidiary hazards
- gauge pressure **< 29.0 psig at 20°C (68°F)** — this is the load-bearing number
- not a hazardous substance / waste / marine pollutant
- loaded by shipper, unloaded by shipper or consignee

The industry shorthand is "valve open = empty." Open the valve, equalize to atmospheric in seconds, ships as standard parcel — no label, no shipping paper, no surcharge, no Chemtrec. UPS Ground or USPS. This is exactly how SodaStream and Drinkmate empties come back. Verification by the consumer is trivial — turn the valve until it stops, no hiss. Tamper-evident tape across the valve in the open position is the optional belt-and-suspenders.

So the swap-pool economics actually look like:

| Leg | Status | Cost (rough) |
|---|---|---|
| Outbound filled cylinder → customer | Hazmat. Needs DOT-SP OR per-shipment fully-regulated hazmat treatment | ~$45 surcharge + freight + apparatus, OR permit amortization |
| Customer empty → swap depot | **Non-hazmat under 173.29.** Plain UPS Ground or USPS | Normal parcel rate, ~$15–20 |

Round-trip in the ~$60–80 range plus the cylinder + fill cost, not $120–140. Materially better than the original C6 figure.

### The interim outbound path (before a DOT-SP)

Before doing the permit work, the cheaper outbound model is **drop-shipping the filled cylinder from a partner gas supplier** that's already a hazmat shipper. Their truck, their hazmat account, their shipping papers, their UN-rated packaging — paid as a per-cylinder service fee on top of the cylinder + fill cost. They run hazmat shipments daily; the marginal one is cheap to them. This sidesteps Derek owning the hazmat shipper apparatus (Chemtrec retainer, 49 CFR 172.700 employee training, packaging design, recordkeeping) at Ring 1 / Ring 2 scale.

Who actually does this is the open question. Welding-supply branches (Airgas, Praxair) deliver to commercial addresses with fleet accounts but typically don't drop-ship single residential parcels. A focused phone call to a regional Airgas branch + one or two homebrew-supply distributors (MoreBeer, LD Carlson, KegWorks, BrewHardware) would settle whether any of them will accept a "drop-ship one filled 5 lb cylinder to my customer's address, here's their info, bill me" arrangement.

If none will, the third option is using a parcel-hazmat fulfillment house (Labelmaster, ShipHazmat, etc.) — they specialize in exactly this, but pricing typically only makes sense above a few hundred shipments a year.

### Strategic implication: the DOT-SP is a real moat for Ring 3+

Applying for a homesodamachine-specific DOT Special Permit at the 5 lb CGA-320 form factor is a genuine competitive moat. SodaStream's permit is the asset that lets them ship cylinders; it's also what no competitor can use. A homesodamachine permit at the 5 lb size would let the swap-cylinder service exist on terms no welding supplier wants to build, and it would not be available to any future home-soda competitor.

This is not Ring 1. It is potentially the defining product feature of the eventual business at Ring 3+ if the rings model in [target-market.md:170](../../marketing/target-market.md) plays out, because it directly closes the one ownership-experience rough edge target-market.md names. Worth a phone call with a hazmat consultancy (Labelmaster, [ICC Compliance Center](https://www.thecompliancecenter.com/case-study-shipping-carbon-dioxide-cartridges-for-a-consumer-product/), J. J. Keller) sometime in the next 1–2 years to scope cost and timeline accurately rather than relying on the rough-order-of-magnitude estimate above.

### Net effect on the recommendations above

- **C2 (Founder Edition includes a filled cylinder)** is more practical than I implied. The shipped-from-a-partner path likely exists for an extra ~$45–60 over the cylinder + fill cost, putting the all-in around $215–230 on a $7,500 unit. The legal work is partner-side, not homesodamachine-side. Decision is still real but the cost-per-unit shouldn't be the blocker.
- **C6 (cylinder-swap loaner pool)** is meaningfully cheaper than first written. Return-leg is standard parcel under 173.29. Outbound-leg via partner is the only hazmat piece. Worth revisiting before Ring 2 with an actual cost from a partner gas supplier, not the rough estimate.
- **New work item: scope a DOT-SP application** as a Ring 3+ strategic option. Phone call with a hazmat consultancy to get a real cost + timeline. Not urgent; should not be forgotten.

### Source list for the hazmat picture

- [49 CFR 173.29 — Empty packagings (eCFR)](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-C/part-173/subpart-B/section-173.29) — the rule that makes return-leg ship as non-hazmat
- [49 CFR Part 173 Subpart G — Gases (eCFR)](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-C/part-173/subpart-G) — the rules for the filled outbound leg
- [Daniels Training — Shipment of Empty Division 2.2 Compressed Gas Cylinders](https://danielstraining.com/shipment-of-empty-division-2-2-compressed-gas-cylinders/) — plain-language read of the 29 psig threshold
- [DOT-SP 20796 (SodaStream 60 L permit, sixth revision, PHMSA)](https://www.phmsa.dot.gov/hazmat/documents/offer/SP20796.pdf/offerserver/SP20796) — the canonical reference for what a permit looks like
- [SodaStream CO2 Cylinder Support](https://sodastream.com/pages/sodastream-co2-cylinder-support) — how a permit holder explains the program to customers
- [Drinkmate CO2 Exchange Shipping Instructions](https://idrinkproducts.com/pages/co2-exchange-shipping-instructions) — confirms the return-leg-only-non-hazmat workflow as standard industry practice
- [ICC Compliance Center — case study on shipping CO2 cartridges for a consumer product](https://www.thecompliancecenter.com/case-study-shipping-carbon-dioxide-cartridges-for-a-consumer-product/) — outlines the special-permit + custom-packaging-kit pattern
- [UPS Hazardous Materials Guide](https://www.ups.com/us/en/support/shipping-special-care-regulated-items/hazardous-materials-guide) — UPS-side requirements for shipping under 49 CFR
- [Catalina Cylinders — Transporting/Shipping CO2 Cylinders](https://www.catalinacylinders.com/ufaq/transporting-shipping-of-co2-cylinders/) — cylinder-manufacturer plain-language read
