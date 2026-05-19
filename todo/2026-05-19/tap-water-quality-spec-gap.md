# Inlet water spec is missing: the repo says "filtered tap water" but ships no filter and names no water-quality limits

**Author:** hourly agent, 2026-05-19 (twelfth of the day)
**Status:** recommendation only — not for direct execution
**Audience:** Derek, future agents

**Siblings today, and why this is distinct:**

- `cabinet-heat-rejection-gap.md` — air on the hot side. This one is water on the cold side.
- `compressor-acoustic-budget-gap.md` — noise. Unrelated.
- `concentrate-supply-resilience-gap.md` — what goes *into* the hopper. This is what comes in through the back-panel water inlet.
- `enclosure-exterior-doc-gap.md`, `routine-is-optimizing-the-wrong-thing-gap.md`, `trademark-and-brand-name-usage-gap.md` — exterior aesthetic / process / legal. None overlap.
- `foam-pour-procedure-gap.md`, `hydro-test-acceptance-criteria-gap.md`, `integrated-firmware-gap.md` — build process. This is product spec.
- `leak-detection-coverage-gap.md`, `water-damage-containment-gap.md` — what happens when water *escapes*. This is what happens when water *enters*.
- 2026-05-18: shipping, CO2, install-consult, payment, portal, warranty. None addresses inlet water quality.

The closest the repo comes to this topic is one phrase — "filtered tap water" — in [`hardware/future.md`](../../hardware/future.md) Port 2, and one external-supplied line item in [`hardware/bom.md`](../../hardware/bom.md): *"Water filter — user's choice of inline filter upstream of the appliance."* That's the entire spec. No filter SKU, no recommended micron rating, no inlet TDS / chloride / hardness / pH / temperature / pressure spec, no failure mode if the customer ignores it. The Ring 1 buyer doesn't know what they're supposed to install upstream of the appliance, and the founder doesn't have a paragraph to give them when they ask.

## Why this matters more than it looks

### 1. The 316L vessel longevity claim hinges on chloride control

[`hardware/future.md`](../../hardware/future.md) §"Carbonation subsystem" makes the 316L material decision with a specific argument:

> 316L was chosen over 304 for the wetted pressure boundary because the molybdenum addition gives meaningfully better pitting and crevice-corrosion resistance in the chloride + carbonic-acid environment of long-life carbonated water service.

And separately:

> Carbonated water at ~2 °C and pH ~3.5–4 naturally suppresses biofilm and scale formation in the vessel — no scheduled clean cycle is required for the carbonator.

Both claims assume the chloride concentration entering the vessel is in the range where 316L's PREN (~25) is sufficient. Municipal tap water in the U.S. typically runs 5–50 mg/L Cl⁻. Coastal and brackish-groundwater regions (parts of Florida, Texas Gulf Coast, Long Island, southern California well systems) can run 100–250 mg/L. Households on water softeners that fail in the regenerate-stuck position can briefly deliver >500 mg/L Cl⁻ at the kitchen tap. At pH ~3.5, 4 °C, and 100+ mg/L chloride, 316L is at the edge of its pitting-corrosion envelope; the molybdenum margin is consumed. A pitting failure in the welded vessel is a 90 PSI carbonated-water leak inside the cabinet — exactly the failure mode `water-damage-containment-gap.md` is trying to prevent on a different axis.

The decade-of-service argument for the vessel is not unconditional. It is conditional on inlet water staying inside a chloride budget that the repo has not declared.

### 2. The carbonator vessel can scale, even at pH 3.5–4

The "pH suppresses scale" line is true at the water surface where dissolved CO2 has equilibrated. But the inlet path on the cold side — TAISHER 316L 90° street elbow → 1/4" NPT top-plate port → free-fall onto the water surface — sees the *upstream* water, not yet acidified, which can carry calcium and magnesium hardness. In hard-water households (>180 mg/L as CaCO3, common in the U.S. Southwest, Midwest, and parts of Texas), the inlet path can scale at the cold-side LLDPE-to-NPT transition where the wall is coldest and the velocity is lowest. The evaporator coil sees the carbonator wall, not the inlet path, so the coil itself is not directly exposed — but the inlet-path scaling will eventually:

- Bias the high-level reed reading low (water column not reaching the magnet's flux range because the inlet path restricts fill rate)
- Create a pressure-drop signature the firmware doesn't expect, possibly tripping a refill-time-out the firmware doesn't yet know about (`integrated-firmware-gap.md` flagged the absence)
- Concentrate corrosion at the scale crevices on the SS 316L elbow — crevice corrosion, the failure mode 316L was chosen *to avoid*

This is not catastrophic in a 6-month bench test, but the Founder Edition is implicitly a multi-year service commitment.

### 3. Taste

The product's emotional pitch is taste fidelity. [`marketing/target-market.md`](../../marketing/target-market.md) line 11–17:

> dispenses real brand-name diet soda — Diet Mountain Dew, Diet Pepsi, Pepsi Zero Sugar — from a kitchen faucet, ice cold, fully carbonated, on demand. … *indistinguishable from the canned product*.

The canned product is bottled with water that PepsiCo de-chlorinates and treats to a specified TDS range. The home machine bottles with the customer's tap water. Tap water at:

- 1.0 mg/L free chlorine (legal U.S. residual at the tap, common in chloraminated systems): immediately detectable in carbonated water, especially in clear/colorless products. Diet Mountain Dew's flavor profile is built on top of citrus + brominated vegetable oil substitutes; chlorine breaks through the masking and the drink tastes "pool-like."
- Sulfate >250 mg/L (common in groundwater systems): metallic bitterness that compounds with the sucralose aftertaste already cited by Ninja Thirsti reviewers in [`marketing/competitors/ninja.md`](../../marketing/competitors/ninja.md) — the same complaint we're trying not to inherit.
- TDS >500 mg/L (legal U.S. potable but high): the drink will taste flat-mineral even at full carbonation, because the dissolved-solids load is what gives mineral water its "heavy" mouthfeel and what *cans* of soda specifically do not have.

A customer in Phoenix on city water (~600 mg/L TDS, ~1 mg/L Cl₂, ~120 mg/L hardness) will get a different dispense than a customer in Seattle (~50 mg/L TDS, chloramine, ~25 mg/L hardness) — from the same machine with the same SodaStream concentrate. That gap shows up in the customer's first taste. They will not say "the water in my house is the variable" — they will say "this machine doesn't taste like a can."

### 4. The internal plumbing's elastomers are downstream

The SeaFlo 22-Series diaphragm pump uses a Santoprene-class diaphragm. The Multiplex 19-0897 backflow preventer has internal elastomer checks. The peristaltic pump heads are food-grade silicone. Free chlorine at 1+ mg/L attacks Santoprene and many silicones over months; ozone (present in some treated systems) attacks them faster. Without a pre-pump activated-carbon polish, every wear-part in the water path has its service interval determined by the customer's municipal disinfection regime, not by the BOM spec sheet.

## The actual customer-facing question

Two paths are both defensible. The gap is that the repo has not chosen one.

### Path A — Ship a filter inside the appliance

A small inline carbon-block + sediment filter on the warm side, between the rear-panel water inlet and the Multiplex 19-0897 backflow preventer, makes the appliance unconditional on the customer's water. Trade-off: one more replaceable consumable for the customer to remember, one more cartridge in the under-cabinet space (the airflow plenum), and a cartridge that has its own NSF certification path the repo doesn't currently track. The 3M AP Easy Cyst FF (or equivalent — ~$45 cartridge, ~$20 head, ~1,000 gal service life at typical flows) is the off-the-shelf reference. At our duty cycle (24 oz/day × 365 days ≈ 70 gal/year), one cartridge would carry ~14 years of service before flow-rate failure, but the carbon binder degrades by ~5 years even at low throughput, so the customer's actual replacement interval would be a calendar-bound 5-year swap rather than a flow-bound one.

### Path B — Specify and require the customer's filter

A documented inlet-water spec — say, *"≤50 mg/L Cl⁻, ≤0.1 mg/L free chlorine, ≤150 mg/L hardness as CaCO3, 30–80 PSI, 4–35 °C, NSF-certified pre-filter required"* — punted onto the customer. Trade-off: ~30–40% of U.S. households at the Founder Edition income bracket already have a Reverse Osmosis or whole-house carbon filter installed (it is common in the $200K+ household income bracket the target-market doc names), and the spec just confirms their existing setup is adequate. The other ~60% need to be told what to install, and the install consult ([2026-05-18 install-consult-playbook-gap.md](../2026-05-18/install-consult-playbook-gap.md)) becomes the moment that recommendation lands.

The argument for **Path A** is reliability of the founder's product promise — every machine pours the same drink regardless of zip code. The argument for **Path B** is that under-counter space is at a premium (every cubic inch of the cabinet is contested per [`cabinet-heat-rejection-gap.md`](cabinet-heat-rejection-gap.md)) and the founder doesn't need another wear-part on the warranty hook (`warranty-and-rma-gap.md`). My read: Path A wins for the Founder Edition because the founder cannot risk a "this machine doesn't taste like a can" review on units 001–050. The 5-year cartridge swap is a customer-facing consumable that aligns with the CO2 cylinder cadence (`co2-supply-ownership-gap.md`) — both are "things you change every few years, included in the ownership model."

But that's a recommendation, not a decision. The decision belongs to Derek.

## Concrete follow-up tickets

Not for the hourly agent to execute. For a human or for a future, more-empowered agent to pick up.

### W1 — Declare the inlet water spec

A short document at `hardware/inlet-water-spec.md` (or a section in `hardware/requirements.md`) that names, with units:

- **Pressure range** at the rear-panel water inlet. Plausible target: 30–80 PSI dynamic. The SeaFlo 22-Series spec sheet sets the floor; the Multiplex 19-0897 ASSE 1022 backflow preventer sets the ceiling at 200 PSI. The actual narrower band depends on the diaphragm-pump intake characteristic.
- **Temperature range.** Plausible target: 4–35 °C. The 35 °C ceiling matters in the U.S. Sunbelt where summer mains temperature can hit 30 °C and the appliance's chiller has to do meaningfully more work to pull to 2 °C.
- **Maximum chloride concentration** for 316L vessel-life guarantee. Plausible target: 50 mg/L Cl⁻. This is the number that determines whether the molybdenum margin in 316L is consumed or preserved.
- **Maximum free chlorine + chloramine** for taste. Plausible target: 0.1 mg/L combined. Below the customer-detectable threshold in carbonated water.
- **Hardness ceiling** for inlet-path scaling. Plausible target: 150 mg/L as CaCO3. Above this, the inlet-path Cu/SS/PP transitions begin to scale on a multi-year timeline.
- **Total Dissolved Solids ceiling** for taste fidelity. Plausible target: 300 mg/L. Above this, the dispense reads as mineral water with sweetener, not as a can.
- **Particle / sediment** ceiling. Plausible target: ≤5 µm nominal at the inlet. The diaphragm pump's check valves and the Beduan solenoids in the manifold have small flow passages that silt above this.

The numbers above are *plausible starting points based on industry-standard practice for chilled beverage systems and the 316L material limits*, not commitments. The exercise is for Derek to walk through them with the BOM elastomers + the vessel material + the taste argument and confirm or revise each.

### W2 — Decide Path A vs Path B

A short memo, in `hardware/requirements.md` or a new `hardware/inlet-water-spec.md`, that says either:

> *"The appliance ships with an integrated carbon + sediment filter on the warm side of the inlet path. The filter cartridge is a customer-replaceable consumable on a 5-year cadence, included in the per-unit BOM."*

or:

> *"The appliance does not include integrated filtration. The install consultation specifies a customer-supplied filter meeting [spec from W1] upstream of the rear-panel water inlet. The install kit includes [a recommended cartridge SKU OR a measurement-and-recommendation card]."*

Either decision unblocks downstream work. The current "filtered tap water" phrase in [`future.md`](../../hardware/future.md) sits in a place where a reader can plausibly assume there's a filter in the BOM (there isn't) or that the customer's existing filter is presumed adequate (no specification of what "adequate" means).

### W3 — If Path A, source and integrate the filter

Engineering work, downstream of W2:

- Cartridge SKU + head SKU committed in `bom.md`. Reference candidates: 3M AP Easy Cyst FF (carbon block + sediment, NSF 42/53), Pentair Everpure 2FC-S (carbon block, NSF 42), Watts WCBSC-975-PR (sediment-then-carbon). All are warm-side, 3/8" inlet/outlet, designed for under-counter point-of-use service.
- Physical placement in the enclosure interior. Plausible location: against the inner face of the back panel, beside the AC inlet and water-inlet stub, where the warm-side plumbing is already routed. The cartridge needs ~3" of axial clearance for swap, which the back-of-enclosure layout in [`future.md`](../../hardware/future.md) §"Enclosure layout" has not yet committed to.
- A user-accessible cartridge-swap procedure. The customer should not need to open the appliance to swap the filter; the head + cartridge should hang off the back panel where the customer reaches in from the cabinet's open face. This is a back-panel CAD update against [`hardware/printed-parts/enclosure/back-panel/README.md`](../../hardware/printed-parts/enclosure/back-panel/README.md), which is already the densest panel on the appliance.
- A firmware "filter remaining life" tracker. Counted in dispense-events (i.e., flow-sensor pulses) and surfaced in the iOS app at the same place the CO2-remaining and concentrate-remaining indicators live. The hardware is the same flow sensor already in the dispense path; the firmware adds an integrator and an EEPROM-persisted counter.

### W4 — If Path B, ship a measurement card

Engineering-light work, but customer-facing:

- A short printed insert in the install kit ([`finish-pack-ship.md:109`](../../hardware/assembly/finish-pack-ship.md)) that lists the inlet spec from W1 in customer language ("your water needs to be below X chlorine, below Y hardness, etc.")
- A recommendation that the customer order a "$25 mail-in water test kit" (multiple SKUs exist on Amazon Prime — none cited here because the recommendation should be evaluated against the spec) before install. The install consult then reviews the result and either approves the install or recommends a filter.
- A short list of filter SKUs that meet the spec, ranked by under-counter footprint. This list goes on the per-unit portal (`per-unit-portal-gap.md` from 2026-05-18) where it can be updated without re-printing the install kit insert.
- A explicit, in-writing carve-out in the warranty (`warranty-and-rma-gap.md` from 2026-05-18) that names "vessel pitting or evaporator-coil scaling attributable to inlet water outside the published spec" as a non-warranty failure mode. This is the legal half of the path-B decision and the half most likely to surprise the customer if it's not stated up-front.

### W5 — Lab measure the actual vessel chloride tolerance

Independent of W1–W4. The 50 mg/L number in W1 is a textbook number for 316L in chloride + chlorinated environments at low temperature and mildly acidic pH. The actual chloride tolerance of *this* welded vessel — laser-welded with the X1 Pro, citric-acid passivated per the procedure in [`hardware/assembly/pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md), with the weld zone HAZ that the laser process creates — is not the textbook 316L number. The weld zone is the failure-onset location.

A bench test that runs three vessels through accelerated chloride exposure (carbonated synthetic tap water at 100, 250, and 500 mg/L Cl⁻ at 2 °C, pH 3.5, 90 PSI, 6 months) would harden the 50 mg/L number into either "the textbook is conservative for this geometry" or "the textbook overstates our margin, drop the customer spec to 25 mg/L." The test costs three vessels, six months of bench time, and a $50 chloride test strip kit. It does not need to gate Ring 1 — it gates Ring 2's confidence about Ring 1 units in the field.

This is the test that, when done, lets the founder say in the install consult: "Your water is fine — I tested vessels at 5× your chloride level for 6 months and the welds were clean." That sentence, in a 30-second clip on the install consult, is worth more than any spec sheet.

## What I did not write

- An actual filter SKU recommendation. The bench-test data (W5) and the cabinet-layout decision (W3 placement) should drive that, not a doc agent's read of Amazon.
- A revision to [`hardware/future.md`](../../hardware/future.md) Port 2's "filtered tap water" phrase. That phrase is correct as written *if* Path A is chosen (filtered by the integrated filter) and *incorrect* as written if Path B is chosen (filtered by a presumed-existing customer filter). The phrase change is downstream of the W2 decision.
- An update to the BOM. No BOM line should be added until Path A is committed.

## One-line summary

The appliance promises "filtered tap water" inside the carbonator pressure boundary but neither ships a filter nor specifies what the customer's filter must do — and the 316L vessel longevity, the diaphragm and peristaltic elastomer lives, and the *"indistinguishable from a can"* taste promise all rest on whatever the customer's water happens to be. Decide Path A (integrated filter) or Path B (specified customer filter), publish the inlet water spec, and lab-test the vessel's actual chloride tolerance so the install consult can stop guessing.
