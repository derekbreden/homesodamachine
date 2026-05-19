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

**The shipping picture is asymmetric, and the outbound path is harder than first written — see the addendum below.** Return leg is plain UPS Ground under 49 CFR 173.29 (valve open, <29 psig, ships as non-hazmat). Outbound is genuinely regulated hazmat with no turnkey partner-drop-ship workaround — Derek either onboards with a hazmat 3PL or stands up his own hazmat shipper account. Per-swap direct cost works out to ~$109–139 depending on path, not the ~$60–80 a naive "non-hazmat return + cheap drop-ship outbound" calculation would suggest.

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

Return leg is materially cheaper than the original C6 figure implied (plain parcel rate, not a hazmat round-trip). Outbound is still hazmat, and the per-swap economics work out to ~$109–139 of direct cost depending on whether Derek uses a hazmat 3PL or stands up his own shipper account — see the corrected economics table further down.

### The carrier picture — UPS Ground and FedEx Ground handle this routinely

To be unambiguous: **the carrier infrastructure for residential hazmat delivery already exists, is mature, and is used at consumer scale every day.** No delivery network needs to be built.

- **UPS Ground:** accepts Class 2.2 compressed gases in the lower 48. No "residential restriction" — the package routes and delivers to a residential address like any other UPS Ground parcel. Geographic exclusions: no Alaska, no Hawaii, no Puerto Rico, plus a handful of specific island communities (Catalina, Bass Islands, San Juan Islands, etc.) per [UPS's hazmat service definition](https://www.ups.com/us/en/support/shipping-special-care-regulated-items/hazardous-materials-guide/hazardous-material-service-definition).
- **FedEx Ground:** same. Class 2.1 and 2.2 accepted, lower 48 only, no AK/HI. See the [FedEx Ground Hazmat Service Guide](https://www.fedex.com/content/dam/fedex/us-united-states/services/HazMat-FXG-shipping-guide.pdf).
- **USPS:** prohibits compressed gas as a general rule — *except* under specific DOT Special Permits. SodaStream uses USPS as their primary carrier under DOT-SP 20796 ([their support page confirms it](https://support-us.sodastream.com/hc/en-us/articles/14243394657179-How-do-I-return-my-empty-cylinders)). Without a permit, USPS is off the table; with one, USPS becomes the cheapest channel.

All carrier "restrictions" cited earlier are **shipper-side, not destination-side.** The carriers refuse hazmat at *origin* if you try to drop it at a UPS Store, FedEx Office, FedEx drop box, or any other consumer-facing pickup point. Once the shipper-side compliance is in place, the carrier picks up, routes through their normal hazmat-compliant ground network, and drops it on the doorstep of any lower-48 residential address.

**Concrete proof points that this works at consumer scale:** SodaStream and Drinkmate ship millions of consumer-direct CO2 cylinders per year to residential addresses across the lower 48 — almost all via USPS (under DOT-SP) and UPS Ground (for orders of 3+ cylinders). Specialty-gas suppliers ship hazmat to grad students at home every day. The infrastructure is real, mature, and routinely used by small operations.

**Shipper-side compliance — what you actually have to do:**

1. Open a UPS or FedEx shipper account with the hazmat addendum (one-time phone call + paperwork)
2. Get yourself or one employee 49 CFR 172.700 trained (one-day online course, ~$200, recertify every 3 years)
3. Sign up for Chemtrec or equivalent 24-hour emergency response contact (~$1k/year for the small-shipper tier, or pay per shipment)
4. Buy UN-rated overpacks for your cylinders (off-the-shelf — cylinder manufacturers and packaging vendors sell them; not custom)
5. Schedule a daily pickup at your fulfillment address (no drop-off at counters)

That's the whole apparatus. The ~$45/shipment hazmat surcharge is what UPS/FedEx charges on top of normal ground freight, once those five things are in place. That's the marginal cost of using the network you didn't build.

### The outbound options — none of them are "turnkey partner drop-ship"

An earlier draft of this section claimed a "partner gas supplier drop-ship" path existed as the cheap interim — call up a welding supplier, ask them to ship one filled cylinder to your customer's address, pay a fee. **That path does not appear to exist as a turnkey service.** Welding-supply distributors run fleet-truck routes to commercial accounts; they do not maintain a parcel-fulfillment side for single residential drop-ships. Searches turn up no white-label "filled CO2 cylinder drop-ship to your customer" service for the 5 lb CGA-320 form factor. The pattern I assumed exists, doesn't.

What actually exists, honestly sorted:

**Option A — Hazmat 3PL fulfillment.** Real, available, but not a "partner" in the colloquial sense. Companies like [Shiphype](https://shiphype.com/hazmat-fulfillment/), [ShipDudes](https://shipdudes.com/blog/dangerous-goods-fulfillment-hazmat-shipping-rules-and-3pl-requirements), and the [hazmat-3PL providers indexed at fulfill.com](https://www.fulfill.com/3pl/specialty/hazmat) will store and ship Class 2.2 inventory under their own hazmat account. The model is: you stock their warehouse with filled cylinders, they pick-pack-ship per customer order. You still have to source the filled cylinders yourself — typically by ordering a pallet from a welding-supply distributor delivered LTL freight to the 3PL's commercial dock. Welding suppliers do LTL-to-commercial as their normal business; they just don't do the residential parcel leg. The 3PL bridges that gap, for a per-shipment fee.

**Option B — Stand up your own hazmat shipper account from shipment #1.** The 5-step apparatus listed in the carrier-picture subsection above. Derek (or a designated person) becomes the hazmat shipper of record. Realistic from validation onward — the fixed costs are bounded (~$1k/year Chemtrec, ~$200 one-time training, addendum paperwork). Variable costs are the per-shipment hazmat surcharge (~$45) and freight (~$15–20). Carries the liability and compliance burden of being a hazmat shipper on record.

**Option C — Don't ship; drive locally.** Tests the willingness-to-pay but not the parcel-shipping product. Fine for a pre-validation hand-test with five neighbors; not informative about the actual standalone-service hypothesis.

**Option D (years out) — Get the DOT-SP.** Enables USPS at much lower cost and reduces carrier surcharges. Real moat, but the up-front work doesn't pay back at validation scale.

### Per-swap unit economics, corrected

The earlier table omitted the 3PL pick-pack-hazmat-handling fee under Option A. Honest version:

| Line | Exchange ($250), Option A (3PL) | Exchange ($250), Option B (own shipper) |
|---|---|---|
| Cylinder fill, amortized over pallet | ~$20 | ~$20 |
| 3PL pick-pack + hazmat handling | ~$30 | $0 (Derek's labor) |
| UPS Ground hazmat surcharge | ~$45 | ~$45 |
| Freight | ~$18 | ~$18 |
| Return label (173.29 plain parcel) | ~$15 | ~$15 |
| Box / packaging amortized | ~$3 | ~$3 |
| Payment processing | ~$8 | ~$8 |
| **Direct cost per exchange** | **~$139** | **~$109 + Derek's labor** |
| Direct margin at $250 retail | ~$111 | ~$141 minus labor |

Plus fixed costs that don't show on a per-swap line:

- Option A: 3PL monthly storage fee (variable, but small for a pallet of cylinders)
- Option B: Chemtrec retainer (~$1k/year), one-time hazmat training (~$200/3yr), UN-rated overpack inventory

At low volume (10–50 shipments/year), Option A's per-shipment 3PL fee makes more sense than amortizing the Option B fixed costs over very few shipments. Crossover is somewhere in the 50–200 shipments/year range, depending on what the 3PL charges and how much of Derek's time Option B consumes.

### Implication for the standalone-service validation phase

There's no "easy interim" path. The 10–20 shipment validation phase requires either onboarding with a hazmat 3PL (Option A — real contracting work, but no permanent compliance burden on Derek) or Derek personally becoming a hazmat shipper (Option B — moderate one-time cost, compounding compliance discipline). Both are real steps forward, not turnkey arrangements.

This shifts the recommended sequencing: **don't validate by shipping at all.** Instead, validate willingness-to-pay first with a much smaller-scale local hand-test (Option C — drive cylinders to five neighbors who pay $250), and only commit to Option A or B once the demand signal is real enough to justify the contracting or compliance load.

### Strategic implication: the DOT-SP is a real moat for Ring 3+

Applying for a homesodamachine-specific DOT Special Permit at the 5 lb CGA-320 form factor is a genuine competitive moat. SodaStream's permit is the asset that lets them ship cylinders; it's also what no competitor can use. A homesodamachine permit at the 5 lb size would let the swap-cylinder service exist on terms no welding supplier wants to build, and it would not be available to any future home-soda competitor.

This is not Ring 1. It is potentially the defining product feature of the eventual business at Ring 3+ if the rings model in [target-market.md:170](../../marketing/target-market.md) plays out, because it directly closes the one ownership-experience rough edge target-market.md names. Worth a phone call with a hazmat consultancy (Labelmaster, [ICC Compliance Center](https://www.thecompliancecenter.com/case-study-shipping-carbon-dioxide-cartridges-for-a-consumer-product/), J. J. Keller) sometime in the next 1–2 years to scope cost and timeline accurately rather than relying on the rough-order-of-magnitude estimate above.

### Net effect on the recommendations above

- **C2 (Founder Edition includes a filled cylinder)** is still a real decision but the cost is higher than first implied because no turnkey partner-drop-ship exists. The Founder Edition unit ships LTL anyway (heavy appliance), so adding a filled cylinder to the same pallet — sourced from a welding-supply distributor on the same LTL leg — sidesteps the parcel-hazmat problem entirely. That keeps the all-in CO2 cylinder cost near the $169 retail figure. The harder version is shipping a replacement cylinder to a customer post-install, which lands in the C6 picture (~$109–139 direct cost per shipment).
- **C6 (cylinder-swap loaner pool)** has a cheaper return leg than first written (plain parcel under 173.29) but the outbound leg is harder than first written — no turnkey partner-drop-ship service exists for filled 5 lb CGA-320 cylinders. Realistic outbound is either Option A (hazmat 3PL fulfillment, ~$30/shipment 3PL fee on top of the carrier surcharge) or Option B (Derek stands up his own hazmat shipper account, ~$1k/year fixed + per-shipment surcharge). Per-swap direct cost lands at ~$109–139 depending on path. Worth revisiting before Ring 2 with an actual 3PL quote.
- **New work item: scope a DOT-SP application** as a Ring 3+ strategic option. Phone call with a hazmat consultancy to get a real cost + timeline. Not urgent; should not be forgotten.

### The standalone CO2 exchange service — a business on its own

Derek's reframe after reading the hazmat picture: the supply-chain work to solve the home-soda CO2 gap is *also* the work to launch a standalone consumer CO2 exchange service, available to anyone with a 5 lb CGA-320 cylinder — not just homesodamachine customers. The pricing he sketched:

- **$50** — the existing alternative: drive to your local welding supplier during business hours, swap an empty for a full one.
- **$250 exchange tier** — you have an empty, we ship a full to your door, you ship the empty back in the same box (valve open, ships as non-hazmat parcel under 173.29).
- **$500 non-exchange tier** — you don't have an empty to send back; you keep the cylinder. The customer-acquisition product for anyone whose first interaction is "I need CO2 but I don't have a tank yet."

The $200 markup over self-serve is the price of "never drive to a welding supplier again." For a 3-can/day household with 60-day cylinder life, that's ~$1,200/year of service — comparable to a high-tier streaming bundle, framed against the recovered weekend mornings.

**Quick unit-economics sanity check** (all numbers rough, single-cylinder costs; volume changes most of these):

| Line | Exchange ($250) | Non-exchange ($500) |
|---|---|---|
| Cylinder COGS | $0 (fleet cycles) | ~$95 at quantity |
| Fill (food-grade) | ~$33 | ~$33 |
| Outbound hazmat parcel + freight | ~$65 | ~$65 |
| Return label (173.29, plain parcel) | ~$15 | — |
| Box + foam insert (reusable, amortized) | ~$3 | ~$3 |
| Payment processing (~3%) | ~$8 | ~$15 |
| **Direct margin** | **~$126/swap** | **~$289/swap** |

Pre-overhead. Doesn't include the ops org, the customer-service call, the fulfillment labor per shipment, the cylinder-fleet financing cost (each cylinder in rotation is ~$95 of working capital tied up), the hydro-test cadence (every 5 years on a 3AL aluminum), or the DOT-SP application amortization. But the gross margins are real and the structure works.

### Why this is a real business independent of the appliance

**TAM is much larger than home-soda machine buyers.** The 5 lb CGA-320 cylinder is the standard size across:

- Homebrew kegerators (millions of cylinders in service in the US)
- Paintball / airsoft (5–20 lb cylinders)
- Aquarium planted-tank CO2 injection (hobbyist niche but cylinder-density customers)
- Draft beer at home / kegerator culture
- MIG welders (CO2 or Ar/CO2 mix, different valve but same form factor in many cases)
- Mushroom cultivation, calibration-gas users, craft-soda hobbyists
- Small B2B: brewery taprooms, restaurants below the NuCO2 commercial threshold, coffee shops with cold brew on nitro

Each segment has the same problem: welding suppliers are commercial-feeling, business-hours-only, located in industrial parks, require a counter interaction. The convenience tax of ~$200 over self-serve is paid by everyone with an opinion about their time.

### Why this is the strategic moat the appliance product needs

[target-market.md:272–274](../../marketing/target-market.md) flags CO2 refill as the **one** ownership-experience gap in the appliance product. A standalone service solves it for every appliance customer automatically — bundled as included-for-N-years with the Founder Edition, included-with-subscription at Standard, available to non-customers at retail price. **The appliance becomes the only home-soda product on the market that solves its own CO2 problem at the system level.** That is a genuinely defensible product claim, not a marketing one.

It also reframes the DOT-SP application from "Ring-3 nice-to-have for the appliance moat" to "first major capex of the service business." The same permit, amortized over the much larger service TAM, becomes much cheaper per shipment. The legal/regulatory work pays for itself out of service revenue, not appliance margin.

### Sequencing this honestly

This is a separate business with separate operational profile (fulfillment, customer service, fleet management, supplier ops) from the appliance build. It should not be conflated with appliance work or pulled into the Founder Edition build path.

Suggested order:

1. **Validate willingness-to-pay locally before building any shipping infrastructure.** There is no turnkey "drop-ship partner" for filled 5 lb cylinders — see the "outbound options" subsection in the addendum below. The two real shipping paths (hazmat 3PL onboarding or standing up Derek's own hazmat shipper account) both have real setup cost that should not be committed pre-validation. Instead, drive cylinders to 5–10 local customers who pay $250 in cash, with a Stripe Payment Link and a one-page landing site. Test the demand signal before testing the shipping product. ~$1–2k experiment, runs alongside appliance work.
2. **If validated, build a real ops backbone.** Cylinder fleet inventory, fulfillment hub (Derek's garage at first; 3PL later), DOT-SP application kickoff, supplier contracts for bulk CO2 fill at wholesale cost.
3. **Service launch.** Web product, subscription tier, the full pricing model. Independent of any appliance Ring schedule.
4. **Appliance integration.** Founder Edition includes N free swaps; Standard ships with a subscription credit. Out of scope until both products are real on their own.

This belongs in a separate document — probably `business/co2-exchange-service.md` — once Derek decides to take it past the validation stage. For now, captured here as the follow-on insight from the hazmat-shipping research.

### Open questions worth their own thinking later

- **Brand and positioning.** A standalone service needs a name that works for a paintball owner and a kegerator owner and a homesodamachine customer. "CO2Direct," "TankSwap," something more imaginative. Not a homesodamachine sub-brand.
- **Fill operations: in-house or partner?** Buying a fill station (~$15–25k) + bulk-CO2 contract is a real capex decision but unlocks much better unit economics at scale. Partnering keeps capex zero but caps margin.
- **Cylinder ownership and DOT compliance.** A fleet of ~1,000 cylinders is ~$95k of working capital. Each cylinder needs visual inspection at every fill and hydro-test every 5 years (~$15 per test). Real operations.
- **Geography and shipping hub strategy.** One hub in Lincoln NE works for the validation phase. National coverage eventually wants 2–3 regional hubs to keep ground-shipping zones reasonable.
- **B2B vs B2C.** Brewery taprooms and craft soda makers are higher LTV, lower CAC, lower margin per swap. Worth a separate analysis once B2C validates.

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
- [UPS Hazardous Materials Service Definition](https://www.ups.com/us/en/support/shipping-special-care-regulated-items/hazardous-materials-guide/hazardous-material-service-definition) — confirms residential-destination is allowed; lists the lower-48-only geographic exclusions
- [UPS Dangerous Goods Ground Accepted Table (PDF)](https://www.ups.com/assets/resources/media/UPS_TDG_Ground_Accepted_Table.pdf) — Class 2.2 (UN1013 carbon dioxide) on the accepted-via-Ground list
- [FedEx Dangerous Goods & Hazardous Materials Service Guide](https://www.fedex.com/en-us/service-guide/dangerous-goods-hazardous-materials.html) — FedEx Ground hazmat acceptance overview
- [FedEx Ground Hazardous Materials Shipping Guide (PDF)](https://www.fedex.com/content/dam/fedex/us-united-states/services/HazMat-FXG-shipping-guide.pdf) — origin-side restrictions (no counter dropoff), Class 2.2 acceptance, AK/HI exclusions
- [SodaStream — How do I return my empty cylinders?](https://support-us.sodastream.com/hc/en-us/articles/14243394657179-How-do-I-return-my-empty-cylinders) — direct evidence that consumer-direct residential hazmat shipping works at scale, via USPS (under DOT-SP) and UPS Ground
