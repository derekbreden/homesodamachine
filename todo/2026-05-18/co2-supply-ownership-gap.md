# CO2 supply: closing the named rough edge of ownership

**Author:** hourly agent, 2026-05-18 (with extensive Derek collaboration in chat)
**Status:** recommendation only — not for direct execution
**Audience:** future agents, Derek
**Sibling today:** [firmware-manifold-gap.md](firmware-manifold-gap.md) — distinct focus area; that one is hardware/firmware build-readiness, this one is the customer-ownership experience after delivery.

## Reading order

This doc has three parts. Read them in order or skip:

1. **Part 1 — The appliance CO2 ownership problem.** Why the gap matters, what the customer experiences today, seven sized recommendations (C1–C7) for closing it. Most of this is pre-first-sale work that's cheap or free.
2. **Part 2 — The hazmat shipping picture, in detail.** What we learned from research into whether/how someone could ship filled 5 lb CO2 cylinders to customers' homes. Includes the actual carrier contract reads, the 49 CFR 173.29 return-leg exemption, and the carrier-side requirements that apply if and when the project ever ships a cylinder.
3. **Part 3 — The standalone CO2 exchange service idea.** A separate business that the same supply-chain work would unlock — bigger TAM than home soda, would also serve as the moat for the appliance product. Captured for the future, not for now.

## Project-stance alignment

Before any of the below, the relevant frame: this project is **pre-revenue**, treats compliance work as **safety-driven and voluntary** (per [`business/regulatory.md`](../../business/regulatory.md): "D2C sale does not require this listing. The design follows the standard anyway because the standard codifies what safe handling … actually requires"), and explicitly does not pursue regulatory posture for its own sake. The appliance business currently carries no insurance and has no plans to before the first sale; the CO2 service work should follow the same pattern. Everything in this doc that costs money or compliance overhead is **future-state reference material**, not a pre-sale to-do list. The doc-only recommendations (C1, C4 cheap version, C7) are the only things worth doing now.

---

## Part 1 — The appliance CO2 ownership problem

### TL;DR

[marketing/target-market.md:272–274](../../marketing/target-market.md) is the only place in the repo that calls out an explicit gap in the product story:

> CO2 refills currently require a trip to a welding gas supplier during business hours. We message this honestly: "CO2 lasts months. When it runs out, a local gas supplier refills it." In the medium term, we explore delivery options, partnerships, or alternative sources. **This is the one piece of the ownership experience that doesn't yet meet the standard of the rest of the product.**

The technical inlet side is done — [bom.md §4](../../hardware/bom.md) has a two-stage regulator (customer's CGA-320 primary → in-appliance WR1110 fixed 90 PSI) feeding the sparge stone, locked at a working pressure with a 35 PSI margin to the SV-125 PRV. Derek's running prototype has been on a Feb-13 5 lb food-grade Airgas cylinder for three months ([purchases.md:75](../../hardware/purchases.md)). The plumbing is real.

What is missing, end-to-end:

1. **No customer-facing CO2 doc.** The only mention of customer CO2 in shipping-doc form is one line in [bom.md:262](../../hardware/bom.md) ("5 lb CO2 tank + refills (~$25/refill at welding/homebrew shops)") under "External / user-supplied (not shipped)." There is no `docs/co2-supply.md`, no install-kit doc, and no messaging in any web/marketing artifact.
2. **No monitoring.** The appliance has no idea how much CO2 is in the customer's cylinder. The carbonator has reed-based level sensing for the water side (low-/high-level reeds, [future.md:37](../../hardware/future.md)) but nothing on the CO2 side — no pressure transducer, no flow meter, no consumption accounting. The customer discovers the empty tank when soda stops being soda.
3. **No supply-side playbook.** No supplier-finder, no list of national chains that fill CGA-320 5 lb food-grade, no fallback when the local Airgas isn't open. Derek's own supplier (Airgas Lincoln NE) is hardcoded in the purchases ledger only because he's the customer.
4. **No Ring 1 measurement plan.** The "CO2 lasts months" claim is not based on instrumented data from this product. SodaStream's 60 L cartridge is calibrated for chilled-bottle dispense, not a 6"-tall headspace sparged into 1.6 L of water at 90 PSI. Our actual cylinder life per dispense is unknown.

This is a **Ring-1-and-Ring-2 readiness gap**, not a hardware blocker. Unit #1 can ship without it. The first 10 customers will hit it within 2–8 weeks of install (estimate; see C5), and the recovery experience is what will or won't validate the $7,500 Founder Edition story.

### Why this matters more at Founder Edition than at Standard

The trust-gap argument in [target-market.md:256–262](../../marketing/target-market.md) — "at Founder Edition scale, the brand is a person" — cuts both ways. A clean recovery from an empty cylinder is a story Derek will be told back ("the app pinged me, the local place was on the list, twenty minutes done"). A bad one ("first time it ran out, I drove to three places, no one had it") is the *only* daily-life touchpoint where the customer goes back to behaving like a SodaStream owner. The whole product is positioned against the can-haul; the CO2 refill, today, is a can-haul.

This is also the one moment a Ring 1 customer would call Derek personally. A documented playbook lets him answer the call in 30 seconds instead of debugging it live.

### What the customer actually has to do today (best reconstruction)

Assembling the picture from [bom.md](../../hardware/bom.md), [future.md](../../hardware/future.md), and [purchases.md §2](../../hardware/purchases.md):

1. **Acquire a 5 lb aluminum food-grade CGA-320 cylinder.** Not shipped with the appliance. Airgas line item "CD FG5" — $124.10 cylinder + $32.59 fill + $12.10 hazmat = $168.79 at customer pickup. Not Prime, not Amazon, not next-day. Customer must drive to a welding-gas branch during business hours, sign for a hazmat receipt, and lift a ~12 lb cylinder into a car.
2. **Connect to the appliance's CGA-320 inlet** on the rear panel. (The inlet is one of the rear-panel connections in the umbilical-port inventory in [`printed-parts/enclosure/back-panel/README.md`](../../hardware/printed-parts/enclosure/back-panel/README.md).)
3. **Open the cylinder valve. Done — until empty.**
4. **Discover empty by dispense failure.** Symptoms: flat soda, then no soda. No advance warning.
5. **Drive empty cylinder back to a fill location.** Repeat step 1.

Steps 1 and 5 are the rough edge. Step 4 — *the lack of warning* — is what turns step 5 into a "next free morning" problem instead of a "schedule it" problem.

### C1 — Add a customer-facing `docs/co2-supply.md` (cheapest, do first)

A single canonical doc that answers:

- What cylinder do I need? (5 lb aluminum food-grade, CGA-320, ~12" tall, fits in the under-sink cabinet next to the appliance — confirm physical fit against [enclosure layout](../../hardware/future.md))
- Where do I get it? (Airgas, Praxair/Linde, AirWeld, local homebrew supplier, paintball shop — by category, not specific chains, with a note on the food-grade requirement vs. industrial-grade)
- What does a refill cost and how often? (placeholder pending C5)
- What does "food-grade" mean for CO2 and why does it matter? (Open question — Airgas charges differently for the two grades; the BOM should eventually know why we're paying for the food-grade SKU)
- Service-life and replacement guidance (DOT hydrostatic re-test every 5 years on aluminum 3AL cylinders)

Single source of truth, linked from `marketing/target-market.md`, the future web checkout, and the per-unit `homesodamachine.com/u/NNN` page referenced in [future.md:143](../../hardware/future.md).

Estimated effort: ~2 hours of writing, no hardware change, no spending.

### C2 — Founder Edition includes a filled cylinder; document the decision

This is a $169 line item on a $7,500 unit (2.3% of price) that closes the most acute friction — "day-one onboarding" — completely. The customer plugs the appliance in, opens the included cylinder, makes their first soda. They are never the person who got it home and then realized they had to drive somewhere.

**Practical implementation:** the Founder Edition unit ships LTL anyway (heavy appliance). Add a filled cylinder to the same pallet, sourced from a welding-supply distributor delivered on the same LTL freight leg to the customer. Welding suppliers do LTL-to-commercial as their normal business; in this case Derek ships to a residential address, but pallet-via-LTL is standard. No parcel-hazmat infrastructure is needed for this case — the cylinder rides with the appliance, hazmat-handled by the existing LTL carrier.

This needs a documented decision (probably a one-line addition to [target-market.md](../../marketing/target-market.md)'s Founder Edition section and a per-unit BOM line in [bom.md §14 "Install kit"](../../hardware/bom.md)), not a vague intent. At Standard ($5,500) the question is open — the BOM tradeoff is different. The decision should be a separate, deliberate one.

The harder version — shipping a *replacement* cylinder to a customer post-install via parcel — is the Part 2 / standalone-service problem, not this one.

### C3 — Add CO2 pressure monitoring to the BOM and firmware

The appliance currently has:

- DS18B20 ×2 (tank wall + suction line) on the 1-wire bus
- 8 reservoir reeds + 2 carbonator reeds for water-side level
- Sparge stone on the inside-vessel face of Port 1

It does **not** have a pressure transducer or pressure switch anywhere on the CO2 line. Reads from the customer-side regulator's gauge are visual-only and the regulator is under the sink — the customer cannot see it.

Minimum-viable add: one low-cost 0–1500 PSI pressure transducer (0.5–4.5 V ratiometric, e.g. CNBTR-class ~$15) tee'd into the high-pressure side of the CGA-320 regulator inlet, ADC channel on the ESP32 (one of the unused ADC1 pins — pinout in [esp32-pinout.mmd](../../hardware/wiring/esp32-pinout.mmd) should be checked for a free one). Tank-side pressure is a direct read on "is there CO2 left": a full 5 lb cylinder at room temp reads ~830 PSI and stays roughly flat (saturated liquid + vapor) until the liquid is gone, then drops fast to atmospheric over the last ~20% of mass. The cliff is the warning.

Firmware behavior:

- Read pressure every N seconds (slow signal).
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

### C6 — Cylinder-swap loaner pool: future-state, captured in Part 2

For Ring 2+ with 20+ units in the field, the natural answer to "ongoing hassle" is a swap-cylinder pool — customer app says "low CO2," they click "send a refill," a pre-filled cylinder arrives, they ship the empty back. This is the "ongoing hassle" answer in [target-market.md:269](../../marketing/target-market.md) — and the one place where the Founder Edition story can extend past day 1.

Whether this is viable, what it costs, and how it integrates with the appliance product is the substance of Part 2 and Part 3 of this doc. Out of scope for unit #1. Not pre-validated; don't spend on it yet.

### C7 — Hardware-side optionality: SodaStream Quick-Connect adapter

SodaStream's QCC (Quick Connect) cylinders are the friction-free option in the existing consumer-CO2 market — Costco, Bed Bath, Target all swap them for $17 each. They're 60 L cartridges (~133 g of CO2) vs. our 5 lb (2,270 g of CO2) — *17× less* capacity per swap. Bad as a primary supply (a heavy user would do 6–10 swaps per month). Possibly viable as an **emergency bridge** when the customer's main cylinder is empty and the welding supplier is closed.

A small CGA-320 ↔ SodaStream-QCC adapter is a $15–25 commodity. Buying one and including it in the install kit is a near-zero-cost insurance policy. The customer's "what do I do tonight" answer becomes "stop at Costco." No hardware change to the appliance — just an adapter and a documented note in `docs/co2-supply.md`.

This is small and easily reversed; worth piloting on unit #1.

### Migration plan / order of operations for Part 1

Pre-revenue stance: do only the work that's cheap and doesn't commit money or compliance overhead.

1. **C1 + C4 cheap-version (today, free).** A markdown doc that lists what cylinder, where to refill, and how to read the gauge. ~1 day of writing.
2. **C2 decision (this week, free).** Make the call on whether the Founder Edition includes a filled cylinder. Document it in [bom.md §14](../../hardware/bom.md) and [target-market.md §"Founder Edition"](../../marketing/target-market.md). The hard part of C2 (parcel-shipping a replacement cylinder later) is the Part 2/3 problem, not this one.
3. **C3 minimum-viable (before unit #1 firmware freeze, ~$30 of parts).** Add the pressure transducer + ADC pin + simple two-threshold alert. Couple it to the iOS app notification path.
4. **C5 (Ring 1 ship — passive).** With C3 done, data logs on its own. Make sure the log makes it back to a queryable place.
5. **C7 (low priority, opportunistic, ~$20).** Order the adapter, add a line to the install kit.
6. **C4 best-version + C6 (post first 10 sales).** Don't build the supplier web tool or the swap pool until there are real customers being served.

### Out of scope for Part 1

- The broader telemetry architecture (what comes back from in-home units, where it's stored, who can query it). CO2 pressure is one signal; the system needs the rest (refrigeration duty cycle, dispense counts, fault events, water-side reed transitions). Worth a future hourly-agent focus.
- The food-grade vs. industrial-grade CO2 question. Worth its own focused dive — Airgas charges differently for the two grades and the BOM should know why we're paying for the food-grade SKU.
- The CO2 sensor for the *room* (hydrocarbon leak detection from R-600a is already covered by the MQ-6 in [future.md:107](../../hardware/future.md); a CO2 leak from our supply line is a separate concern — low risk because we leak food-grade gas, not flammable, but a customer "I smell gas" call still gets one).

---

## Part 2 — The hazmat shipping picture, in detail

This part captures everything learned through research into whether and how cylinders could be shipped parcel-to-residential — relevant for C6 (Ring 2+ swap-cylinder pool) and Part 3 (standalone CO2 exchange service). All of this is **reference material**, not a pre-revenue to-do.

### The question that started this: why doesn't anyone ship filled 5 lb CO2 cylinders to homes?

Derek asked: "Is there any such outfit? I'd be thrilled to pay $400 for a shipped 5 lb bottle — no one offers it that I can tell."

Answer, after research: correct — functionally no one offers it, and the reason is structural rather than regulatory-impossible. The market is bifurcated into two halves with a structural hole in the middle:

- **Small consumer cylinders (60 L / ~133 g)** ship to homes under DOT Special Permits. SodaStream's 60 L cylinder is covered by [DOT-SP 20796](https://www.phmsa.dot.gov/hazmat/documents/offer/SP20796.pdf/offerserver/SP20796); their 130 L is covered by DOT-SP 15634. These permits waive the shipper-certification signature and authorize alternative hazard communication, enabling the "exchange your empty by mail" UX. [Drinkmate](https://idrinkproducts.com/pages/co2-exchange-shipping-instructions) operates a similar program.
- **Large industrial / commercial cylinders (5+ lb and up)** ship via fleet-truck routes from welding-supply distributors (Airgas, Praxair, NuCO2). The customer is a bar, restaurant, brewery, or industrial site with a commercial delivery address.
- **The 5 lb consumer cylinder is in the gap.** Too big for the consumer-mail DOT-SPs (which are scoped to specific small form factors, not extensible by grade). Too small for fleet-truck route economics. No DOT-SP exists for the 5 lb CGA-320 form factor because no operator with enough volume to justify it has chosen to apply.

The application work to obtain a DOT Special Permit for a 5 lb form factor is substantial — $40–145k of consultant + packaging design + accredited-lab testing, plus 12–24 months calendar (PHMSA review is 120 days minimum after submission, and SodaStream-style permits go through multiple revisions over years). The reason no welding-supply distributor has done this work is the same reason no one offers shipped 5 lb refills: their existing business doesn't require it, and the volume to amortize it isn't in their segment.

**Concrete proof that the market gap is real:** searches surface no white-label "filled CO2 cylinder drop-ship to your customer" service, and a direct probe of American Brewmaster's "2.5# CO2 Tank Full" listing turned out to be in-store-fill only ("YES - WE FILL CO2 TANKS! BRING IT IN, AND WE'LL FILL IT UP!"). The pattern of "online order, ships to home, filled cylinder" doesn't exist at the 5 lb form factor.

### The 49 CFR 173.29 return-leg exemption (the key research finding)

Initially this addendum framed cylinder swap as symmetric hazmat — outbound and return both regulated. **That's wrong on the return leg.** Per [49 CFR 173.29 — Empty packagings](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-C/part-173/subpart-B/section-173.29), an empty Division 2.2 non-flammable gas cylinder (CO2 qualifies) is **exempt from the Hazardous Materials Regulations entirely** when:

- residue is a Division 2.2 gas, not ammonia, no subsidiary hazards
- gauge pressure **< 29.0 psig at 20°C (68°F)** — the load-bearing number
- not a hazardous substance / waste / marine pollutant
- loaded by shipper, unloaded by shipper or consignee

Industry shorthand: **"valve open = empty."** Open the valve, equalize to atmospheric in seconds, ships as standard parcel — no label, no shipping paper, no surcharge, no Chemtrec. UPS Ground, FedEx Ground, or USPS. This is exactly how SodaStream and Drinkmate empties come back to them ([SodaStream support page](https://support-us.sodastream.com/hc/en-us/articles/14243394657179-How-do-I-return-my-empty-cylinders) confirms USPS for the return).

Verification by the consumer is trivial — turn the valve until it stops, listen for absence of hiss. A photo of the open valve next to the shipping label or tamper-evident tape across the open valve is optional belt-and-suspenders.

**This makes any future swap-cylinder service asymmetric:** outbound = regulated hazmat parcel, return = plain parcel. Cost per round trip is dominated by the outbound leg.

### Carrier picture — UPS Ground and FedEx Ground handle this routinely

To be unambiguous: **the carrier infrastructure for residential hazmat delivery already exists, is mature, and is used at consumer scale every day.** No delivery network needs to be built.

- **UPS Ground** accepts Class 2.2 compressed gases in the lower 48. The package routes and delivers to a residential address like any other UPS Ground parcel. Geographic exclusions: no Alaska, no Hawaii, no Puerto Rico, plus a handful of specific island communities (Catalina, Bass Islands, San Juan Islands, etc.) per the [UPS Hazardous Materials Service Definition](https://www.ups.com/us/en/support/shipping-special-care-regulated-items/hazardous-materials-guide/hazardous-material-service-definition). UN1013 (carbon dioxide) is on the accepted-via-Ground list per the [UPS Dangerous Goods Ground Accepted Table](https://www.ups.com/assets/resources/media/UPS_TDG_Ground_Accepted_Table.pdf).
- **FedEx Ground** is the same. Class 2.1 and 2.2 accepted, lower 48 only, no AK/HI. See the [FedEx Ground Hazmat Service Guide](https://www.fedex.com/content/dam/fedex/us-united-states/services/HazMat-FXG-shipping-guide.pdf).
- **USPS** prohibits compressed gas as a general rule — *except* under specific DOT Special Permits. Without a permit, USPS is off the table; with one, it becomes the cheapest channel.

All carrier "restrictions" are **shipper-side, not destination-side.** The carriers refuse hazmat at *origin* if you try to drop it at a UPS Store, FedEx Office, FedEx drop box, or any other consumer-facing pickup point. Once shipper-side compliance is in place, the carrier picks up, routes through their normal hazmat-compliant ground network, and drops it on the doorstep of any lower-48 residential address.

**Concrete proof points at consumer scale:** SodaStream and Drinkmate ship millions of consumer-direct CO2 cylinders per year to residential addresses across the lower 48 — almost all via USPS (under DOT-SP) and UPS Ground (for orders of 3+ cylinders). Specialty-gas suppliers ship hazmat to grad students at home every day. The infrastructure is real, mature, and routinely used by small operations.

### Insurance is not a legal requirement, and neither carrier requires it

The strongest finding from the research: **no federal law, no state law, and neither UPS nor FedEx requires a hazmat shipper / offeror to carry insurance.**

- **Federal law (PHMSA, 49 CFR):** Hazmat Registration requires a fee, employee training, and shipping paper / packaging compliance — no insurance. FMCSA's $1M/$5M liability minimums apply to motor carriers (operators of commercial trucks), not to parcel shippers. UPS and FedEx are the motor carrier; the shipper is not.
- **UPS Dangerous Goods Agreement (Form 2008)** — the actual 2-page shipper contract was retrieved and reviewed in entirety (via Wayback Machine; UPS's live URL blocks direct fetch). Source: [UPS hazmat_contract.pdf](https://www.ups.com/assets/resources/media/hazmat_contract.pdf). The contract contains zero mentions of insurance, indemnification, additional-insured status, certificate of insurance, or minimum financial responsibility. The shipper's obligations are limited to: comply with 49 CFR + IATA DGR, classify/package/mark/label correctly, train employees per 49 CFR, ship to approved destinations. One-year term, auto-renewing, 30-day termination by either party. That's the whole list.
- **FedEx Ground Hazmat Shipping Guide (99 pages)** — full document downloaded and grepped for "insur", "indemn", "liabil". Zero hits in the shipper-requirements context. The entire qualification process per the guide is: review and agree to form OP-910 + provide proof of 49 CFR 172.704 training. Nothing else. Source: [FedEx Ground Hazmat Shipping Guide PDF](https://www.fedex.com/content/dam/fedex/us-united-states/services/HazMat-FXG-shipping-guide.pdf).

Two unverified caveats remain:

1. **The OP-910 form text itself isn't publicly posted** — it's distributed through FedEx account executives. The form *might* impose terms not in the public guide. Worth asking the account exec directly when/if making that call.
2. **The UPS Tariff that Form 2008 references is a larger document** whose hazmat sections might add insurance language not in Form 2008 itself. The publicly searchable parts don't appear to, but UPS's Hazmat Support Center (1-800-554-9964) can confirm definitively.

**The "you need hazmat insurance" claim that pervades search results traces consistently to three sources, none of which are the carrier or the regulator:**

1. **3PL fulfillment providers** require it of their customers because they're holding your inventory and want protection. Contract term, not law. Not applicable if you don't use a 3PL.
2. **Hazmat-trucking insurance brokers** are selling commercial-vehicle policies to fleet operators ($15–45k/yr range you see online). Wrong product for a parcel shipper. They quote this because it's what they sell.
3. **Compliance-vendor marketing pages** bundle insurance into "complete hazmat compliance solutions." Selling insurance is part of their revenue mix; that doesn't make it a mandate.

**Why a hazmat shipper might still buy insurance (when revenue justifies it):** catastrophic-tail liability protection, not compliance. Two real scenarios:

- **Cylinder valve failure in transit.** A defective valve fails; a cylinder vents violently and becomes a projectile inside a UPS facility or in a customer's hallway. Industry-wide this happens a few times a year across consumer CO2 shipping. If your cylinder is the one that hits a UPS handler or a customer's child, you're on the hook for medical, legal, and settlement costs that easily reach six or seven figures.
- **Customer handling injury.** Customer drops a 12 lb cylinder on their foot, over-tightens a regulator, or asphyxiates in a small room with the valve open. Most are not-your-fault outcomes, but defending the claim still costs $30–100k of legal fees before "not your fault" is established. Product liability insurance pays for the defense, not just the settlement.

**For this project specifically:** this is a future-state concern, not a current one. The project is pre-revenue and the appliance side already operates uninsured ([`business/regulatory.md`](../../business/regulatory.md) treats compliance as voluntary safety work, not regulatory posture; insurance is in the same bucket). When and if the first sale closes and a CO2 service starts taking customer money, the question reopens — and the cheapest path is then to add a Class 2.2 endorsement to whatever product-liability policy the appliance business carries at that point, not to procure a standalone hazmat shipper policy.

### What it would cost to become a hazmat shipper, if/when the time comes

Captured here as **reference material for future planning**, not as a current-period budget item.

**Carrier shipper-side compliance — the five-step apparatus:**

1. Open a UPS or FedEx shipper account with the hazmat addendum (one-time phone call + paperwork, no fee)
2. Get yourself or one employee 49 CFR 172.704 trained (one-day online course, $49 per person, valid 3 years per [PHMSA training requirements](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-C/part-172/subpart-H/section-172.704))
3. Sign up for Chemtrec or equivalent 24-hour emergency response contact (~$1,000–1,500/yr per [Hazmat Line breakdown](https://www.hazmatline.com/pages/chemtrec-cost), depending on configuration)
4. Buy UN-rated 4G/4GV overpacks for cylinders (~$9.50/ea at 600-unit bulk per [Air Sea Containers](https://airseacontainers.com/blog/wholesale-corrugated-hazmat-and-dangerous-goods-boxes/))
5. Schedule a daily pickup at the fulfillment address (no drop-off at counters)

**Plus the federal registration:** PHMSA Hazmat Registration is $275/year for small businesses (rising to $400/year in the proposed rule) per the [PHMSA 2025-2026 brochure](https://www.phmsa.dot.gov/sites/phmsa.dot.gov/files/2025-04/Hazmat-Registration-Brochure-2025-2026.pdf).

**Plus the cylinder fleet and fills:** recertified 5 lb aluminum cylinders run ~$50–80 each per [Gas Cylinder Source](https://gascylindersource.com/shop/co2-carbon-dioxide-cylinders/5-lb-aluminum-co2-cylinder-recertified/) (new run $100–140); fills run ~$25 each at customer-pickup rates (less at commercial wholesale).

**Reference startup cost (50 cylinder fleet, no insurance, no recordkeeping software, no legal review):**

| Item | Cost |
|---|---|
| Hazmat training (1 person) | $49 |
| 100 UN 4G overpacks | ~$1,000 |
| 50 recertified cylinders | ~$3,000 |
| Initial fills (50 × $25) | ~$1,250 |
| **Total one-time** | **~$5,300** |

**Reference annual recurring (no insurance):**

| Item | Cost |
|---|---|
| PHMSA Hazmat Registration | $275 |
| Chemtrec subscription | ~$1,000 |
| Training renewals (amortized) | ~$16/yr |
| **Total recurring** | **~$1,300/yr** |

The ~$45/shipment hazmat surcharge is what UPS/FedEx charges on top of normal ground freight, once the shipper apparatus is in place. That's the marginal carrier cost of using the network — paid per shipment, not annually.

**Insurance, if eventually purchased:** ~$500–2,000/yr incremental as a Class 2.2 endorsement on the existing appliance product-liability policy (when one exists). Right framing for the broker call is "Class 2.2 endorsement on my product-liability policy," not "hazmat shipper insurance." The latter framing gets quoted hazmat-trucking products at $15–45k/yr that don't apply.

### Outbound options if/when a swap service eventually exists

Three options for the outbound parcel-hazmat leg, in honest order:

- **Option A — Hazmat 3PL fulfillment.** Real, available, but onerous at low volume. Providers like [Shiphype](https://shiphype.com/hazmat-fulfillment/), [ShipDudes](https://shipdudes.com/blog/dangerous-goods-fulfillment-hazmat-shipping-rules-and-3pl-requirements), and others ([fulfill.com hazmat 3PL index](https://www.fulfill.com/3pl/specialty/hazmat)) will store and ship Class 2.2 inventory under their own hazmat account. The model: stock their warehouse with filled cylinders (typically delivered as a pallet via LTL freight from a welding-supply distributor — that part welding suppliers do as normal business), they pick-pack-ship per customer order. Adds a per-shipment 3PL fee (~$30) and monthly storage rent (~$200–400) on top of the carrier surcharge. **Doesn't make sense at low volume** — fixed costs stack, per-shipment fee never goes away. Only earns its keep above ~200 shipments/year when the labor of Option B becomes the binding constraint.
- **Option B — Stand up your own hazmat shipper account.** The 5-step apparatus above. Derek (or a designated person) becomes the hazmat shipper of record. At any volume below ~200 shipments/year, this is the cheaper path on every dimension — the fixed costs amortize fine at even 10 shipments/year, and there's no per-shipment 3PL fee.
- **Option C — Don't ship; drive locally.** No shipping infrastructure. Tests willingness-to-pay but not the parcel-shipping product. Fine for validation phase.

There is no fourth option. The "drop-ship via partner gas supplier" path that earlier-drafts of this addendum referenced does not exist as a turnkey service — welding-supply distributors run fleet-truck routes to commercial accounts; they do not maintain a parcel-fulfillment side for single residential drop-ships. Verified across multiple search angles.

**Per-swap direct cost at Option B (the realistic destination if/when this ever happens):**

| Line | Cost |
|---|---|
| Cylinder fill, amortized | ~$20 |
| UPS Ground hazmat surcharge | ~$45 |
| Freight | ~$18 |
| Return label (173.29 plain parcel) | ~$15 |
| Box / packaging amortized | ~$3 |
| Payment processing | ~$8 |
| **Direct cost per exchange** | **~$109** |

Plus Derek's per-shipment labor at low volume.

### Why we're explicitly not pursuing a DOT Special Permit

A DOT Special Permit would let us ship cheaper (and use USPS as SodaStream does), but the math does not pay back at this project's scale. The permit costs $40–145k all-in and 12–24 months calendar to obtain (consultant + packaging design + accredited-lab testing — no PHMSA filing fee but real preparation cost); the per-shipment savings (~$45 carrier surcharge eliminated) only amortize meaningfully above roughly 1,000 shipments per year sustained for many years. The rings-model plan in [target-market.md:170](../../marketing/target-market.md) tops out around 20–30 units per year of the appliance product, and even a successful standalone exchange service in the same craft-practice mold would not generate the shipment volume to justify the permit work.

**Option B (own hazmat shipper account, per-shipment surcharge, no permit) is the destination if/when the service exists, not a stepping stone toward a permit.** Don't budget for, plan for, or research the DOT-SP further unless project ambitions change fundamentally.

---

## Part 3 — The standalone CO2 exchange service idea

Captured here because the supply-chain work to close the appliance's CO2 gap is also the work to launch a standalone consumer CO2 exchange service available to anyone with a 5 lb CGA-320 cylinder — not just homesodamachine customers. Belongs in a separate document (`business/co2-exchange-service.md`) when/if it advances past validation. For now it's a follow-on insight that should not be lost.

### The pricing model

Derek's sketch:

- **$50** — the existing alternative: drive to your local welding supplier during business hours, swap an empty for a full one.
- **$250 exchange tier** — you have an empty, we ship a full to your door, you ship the empty back in the same box (valve open, ships as non-hazmat parcel under 49 CFR 173.29).
- **$500 non-exchange tier** — you don't have an empty to send back; you keep the cylinder. The customer-acquisition product for anyone whose first interaction is "I need CO2 but I don't have a tank yet."

The $200 markup over self-serve is the price of "never drive to a welding supplier again." For a 3-can/day household with 60-day cylinder life, that's ~$1,200/year of service — comparable to a high-tier streaming bundle, framed against the recovered weekend mornings.

### Quick unit-economics sanity check

Rough numbers, pre-overhead:

| Line | Exchange ($250) | Non-exchange ($500) |
|---|---|---|
| Cylinder COGS | $0 (fleet cycles) | ~$95 at quantity |
| Fill (food-grade) | ~$33 | ~$33 |
| Outbound hazmat parcel + freight | ~$65 | ~$65 |
| Return label (173.29, plain parcel) | ~$15 | — |
| Box + foam insert (reusable, amortized) | ~$3 | ~$3 |
| Payment processing (~3%) | ~$8 | ~$15 |
| **Direct margin** | **~$126/swap** | **~$289/swap** |

Doesn't include the ops org, the customer-service call, the fulfillment labor per shipment, the cylinder-fleet financing cost (each cylinder in rotation is ~$95 of working capital tied up), or the hydro-test cadence (every 5 years on a 3AL aluminum). But the gross margins are real and the structure works.

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

The non-exchange tier ($500) is the customer-acquisition product: anyone with a SodaStream, a Drinkmate, a friend's kegerator, a new homebrew setup gets an immediate full cylinder, no welding-supply trip ever. After their first cylinder is empty, they're on the $250 exchange tier forever.

### Why this is the strategic moat the appliance product needs

[target-market.md:272–274](../../marketing/target-market.md) flags CO2 refill as the **one** ownership-experience gap in the appliance product. A standalone service solves it for every appliance customer automatically — bundled as included-for-N-years with the Founder Edition, included-with-subscription at Standard, available to non-customers at retail price. **The appliance becomes the only home-soda product on the market that solves its own CO2 problem at the system level.** That is a genuinely defensible product claim, not a marketing one.

### Sequencing — validate before building anything

The pre-revenue stance from the project-stance alignment up top applies here too. Don't spend on Phase 1 infrastructure before there's a paying customer for the service. Suggested order:

1. **Validate willingness-to-pay locally before building any shipping infrastructure.** Drive cylinders to 5–10 local customers who pay $250 in cash, with a Stripe Payment Link and a one-page landing site. Test the demand signal before testing the shipping product. ~$1–2k experiment that runs alongside appliance work. No PHMSA Registration, no Chemtrec, no UN overpacks, no insurance — none of it is needed for hand-delivered local cylinders.
2. **If validated, decide whether to build Option B.** The startup cost reference in Part 2 (~$5,300 one-time + ~$1,300/yr recurring + ~$109/shipment variable) is what it actually takes. The decision: is the demand signal enough to justify that spend, and does Derek want to be a hazmat shipper of record? Both real questions, both deferrable.
3. **Service launch.** Web product, subscription tier, the full pricing model. Independent of any appliance Ring schedule.
4. **Appliance integration.** Founder Edition includes N free swaps; Standard ships with a subscription credit. Out of scope until both products are real on their own.

### Open questions worth their own thinking later

- **Brand and positioning.** A standalone service needs a name that works for a paintball owner and a kegerator owner and a homesodamachine customer. "CO2Direct," "TankSwap," something more imaginative. Not a homesodamachine sub-brand.
- **Fill operations: in-house or partner?** Buying a fill station (~$15–25k) + bulk-CO2 contract is a real capex decision but unlocks much better unit economics at scale. Partnering keeps capex zero but caps margin.
- **Cylinder ownership and DOT compliance at scale.** A fleet of ~1,000 cylinders is ~$95k of working capital. Each cylinder needs visual inspection at every fill and hydro-test every 5 years (~$15 per test). Real operations.
- **Geography and shipping hub strategy.** One hub in Lincoln NE works for the validation phase. National coverage eventually wants 2–3 regional hubs to keep ground-shipping zones reasonable.
- **B2B vs B2C.** Brewery taprooms and craft soda makers are higher LTV, lower CAC, lower margin per swap. Worth a separate analysis once B2C validates.

---

## Source list

### Regulations / federal documents

- [49 CFR 173.29 — Empty packagings (eCFR)](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-C/part-173/subpart-B/section-173.29) — the rule that makes the return leg ship as non-hazmat at <29 psig
- [49 CFR Part 173 Subpart G — Gases (eCFR)](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-C/part-173/subpart-G) — the rules for the filled outbound leg
- [49 CFR 172.704 — Training requirements (eCFR)](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-C/part-172/subpart-H/section-172.704) — hazmat employee training spec
- [Daniels Training — Shipment of Empty Division 2.2 Compressed Gas Cylinders](https://danielstraining.com/shipment-of-empty-division-2-2-compressed-gas-cylinders/) — plain-language read of the 29 psig threshold
- [DOT-SP 20796 (SodaStream 60 L permit, sixth revision, PHMSA)](https://www.phmsa.dot.gov/hazmat/documents/offer/SP20796.pdf/offerserver/SP20796) — canonical reference for what a Special Permit looks like
- [PHMSA 2025-2026 Hazmat Registration Brochure (PDF)](https://www.phmsa.dot.gov/sites/phmsa.dot.gov/files/2025-04/Hazmat-Registration-Brochure-2025-2026.pdf) — annual registration fee schedule ($275 small biz)
- [PHMSA Fee Adjustment Proposed Rule (Federal Register, May 2024)](https://www.federalregister.gov/documents/2024/05/24/2024-11391/hazardous-materials-adjusting-registration-and-fee-assessment-program) — proposed fee increase to $400/yr small biz
- [PHMSA Special Permits Application Procedures (PDF)](https://www.phmsa.dot.gov/sites/phmsa.dot.gov/files/docs/news/55431/sp-brochure-procedures-compliance.pdf) — confirms no PHMSA filing fee for SP applications; preparation cost is all consultant + packaging design + testing

### Carrier contracts and policies

- [UPS Dangerous Goods Agreement (Form 2008) PDF](https://www.ups.com/assets/resources/media/hazmat_contract.pdf) — full 2-page shipper contract text; verified to contain zero insurance requirements
- [UPS Hazardous Materials Service Definition](https://www.ups.com/us/en/support/shipping-special-care-regulated-items/hazardous-materials-guide/hazardous-material-service-definition) — confirms residential-destination is allowed; lists the lower-48-only geographic exclusions
- [UPS Hazardous Materials Guide](https://www.ups.com/us/en/support/shipping-special-care-regulated-items/hazardous-materials-guide) — UPS-side requirements for shipping under 49 CFR
- [UPS Dangerous Goods Ground Accepted Table (PDF)](https://www.ups.com/assets/resources/media/UPS_TDG_Ground_Accepted_Table.pdf) — UN1013 (carbon dioxide) on the accepted-via-Ground list
- [FedEx Ground Hazardous Materials Shipping Guide (full 99-page PDF)](https://www.fedex.com/content/dam/fedex/us-united-states/services/HazMat-FXG-shipping-guide.pdf) — full document grepped; zero hits for insurance/liability/indemnification in shipper-requirements context
- [FedEx Dangerous Goods & Hazardous Materials Service Guide](https://www.fedex.com/en-us/service-guide/dangerous-goods-hazardous-materials.html) — FedEx Ground hazmat acceptance overview

### Cost references

- [Hazmat Line — CHEMTREC Cost Breakdown](https://www.hazmatline.com/pages/chemtrec-cost) — $1,000/yr base, $1,500/yr with one affiliate + contact
- [Air Sea Containers — Wholesale Corrugated Hazmat Boxes](https://airseacontainers.com/blog/wholesale-corrugated-hazmat-and-dangerous-goods-boxes/) — UN 4G/4GV overpack bulk pricing (~$9.50/ea at 600 units)
- [Gas Cylinder Source — Recertified 5 lb Aluminum CO2 Cylinder](https://gascylindersource.com/shop/co2-carbon-dioxide-cylinders/5-lb-aluminum-co2-cylinder-recertified/) — cylinder fleet cost reference
- [MoneyGeek — Ecommerce Business Insurance Cost](https://www.moneygeek.com/insurance/business/retail/ecommerce/cost/) — general-liability baseline (~$810–1,000/yr) for context on the insurance line
- [ICC Compliance Center — case study on shipping CO2 cartridges for a consumer product](https://www.thecompliancecenter.com/case-study-shipping-carbon-dioxide-cartridges-for-a-consumer-product/) — outlines the special-permit + custom-packaging-kit pattern; informed the DOT-SP cost range

### Industry / competitor proof points

- [SodaStream CO2 Cylinder Support](https://sodastream.com/pages/sodastream-co2-cylinder-support) — how a permit holder explains the program to customers
- [SodaStream — How do I return my empty cylinders?](https://support-us.sodastream.com/hc/en-us/articles/14243394657179-How-do-I-return-my-empty-cylinders) — direct evidence that consumer-direct residential hazmat shipping works at scale, via USPS (under DOT-SP) and UPS Ground
- [Drinkmate CO2 Exchange Shipping Instructions](https://idrinkproducts.com/pages/co2-exchange-shipping-instructions) — confirms the return-leg-only-non-hazmat workflow as standard industry practice
- [Catalina Cylinders — Transporting/Shipping CO2 Cylinders](https://www.catalinacylinders.com/ufaq/transporting-shipping-of-co2-cylinders/) — cylinder-manufacturer plain-language read

### Hazmat 3PL providers (reference for Option A if it ever matters)

- [Shiphype — Hazmat Fulfillment](https://shiphype.com/hazmat-fulfillment/)
- [ShipDudes — Dangerous Goods Fulfillment](https://shipdudes.com/blog/dangerous-goods-fulfillment-hazmat-shipping-rules-and-3pl-requirements)
- [fulfill.com — Hazmat 3PL provider index](https://www.fulfill.com/3pl/specialty/hazmat)

### Repo cross-references

- [`marketing/target-market.md`](../../marketing/target-market.md) — the original CO2 rough-edge flag; rings-of-trust model; trust-gap argument
- [`business/regulatory.md`](../../business/regulatory.md) — project stance on compliance as voluntary safety work, not regulatory posture
- [`hardware/future.md`](../../hardware/future.md) — appliance CO2 inlet architecture
- [`hardware/bom.md`](../../hardware/bom.md) — §4 CO2 subsystem, §14 install kit
- [`hardware/purchases.md`](../../hardware/purchases.md) — Airgas cylinder pricing reference, Feb-13 prototype cylinder
- [`hardware/wiring/esp32-pinout.mmd`](../../hardware/wiring/esp32-pinout.mmd) — ADC channels for C3 pressure transducer
- [`hardware/printed-parts/enclosure/back-panel/README.md`](../../hardware/printed-parts/enclosure/back-panel/README.md) — rear-panel CO2 inlet placement
- Sibling todo: [firmware-manifold-gap.md](firmware-manifold-gap.md)
