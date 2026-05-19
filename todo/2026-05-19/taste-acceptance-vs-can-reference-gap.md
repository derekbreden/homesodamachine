# Taste acceptance vs. a canned reference — the product's central marketing claim has no acceptance test

**Author:** hourly agent, 2026-05-19 (eighteenth of the day)
**Status:** recommendation only — not for direct execution
**Audience:** Derek, future agents

## Distinct from every sibling today and yesterday

| Sibling | What it covers | Why this is different |
| --- | --- | --- |
| 2026-05-19 [`flavor-metering-fidelity-gap.md`](flavor-metering-fidelity-gap.md) | The 1:20 ratio is a UI integer with no derivation from physical units. | That doc stops at *ratio in the glass*. This doc asks the next question: even with ratio held perfectly at 1:20, does the assembled output match a can? Carbonation level (CO2 volumes), serve temperature against a can, and any sensory comparison to canned reference are out-of-scope there and missing here. |
| 2026-05-19 [`tap-water-quality-spec-gap.md`](tap-water-quality-spec-gap.md) | No inlet water spec, no filter, no chloride/hardness limit. | That doc is about **inputs** to the carbonator. This doc is about **outputs** at the glass — the test that should catch any input drift that survives upstream controls. |
| 2026-05-19 [`above-counter-ux-gap.md`](above-counter-ux-gap.md) / [`integrated-firmware-gap.md`](integrated-firmware-gap.md) | What the customer sees / what firmware does. | Neither touches what comes out of the faucet sensorily. |
| 2026-05-19 [`reservoir-microbio-and-clean-policy-gap.md`](reservoir-microbio-and-clean-policy-gap.md) | Microbio risk inside the flavor reservoirs over storage. | That is "is the syrup spoiled?" — a safety/shelf-life question. This is "given fresh syrup, does the *appliance* produce a drink that matches the can?" — a fidelity question. The two failure modes are independent: a unit can pass microbio and fail can-match, or vice versa. |
| 2026-05-19 [`trademark-and-brand-name-usage-gap.md`](trademark-and-brand-name-usage-gap.md) | Legal exposure of saying "Diet Mountain Dew." | This is the matched **technical** exposure: if we say "Diet Mountain Dew" and the dispensed product doesn't actually match canned Diet Mountain Dew under a paired-comparison test, the marketing claim is false-in-fact, not just legally risky. |
| 2026-05-18 [`warranty-and-rma-gap.md`](../2026-05-18/warranty-and-rma-gap.md) | What happens when something physically breaks. | Off-spec taste is the silent failure mode that does *not* trip warranty — the unit "works," the soda "comes out," the customer just slowly stops believing the central claim. |
| `hardware/assembly/acceptance-and-burn-in.md` step 5–7 | Volume ±5 %, ≤6 °C, "visible and behaving normally" carbonation, refractometer optional. | The existing acceptance test checks the appliance is *internally consistent* (ratio against itself, channel A vs channel B). It never compares the dispensed product against a canned reference, and Open item §6 ("refractometer required or optional?") is still open. |

## TL;DR

`hardware/future.md:1` and `marketing/target-market.md:11` both make the same factual claim: the dispensed product is **"indistinguishable from the canned product, with equal or better carbonation and temperature."** The full marketing thesis depends on that claim being literally true under blind comparison, not poetically true.

Today the repo has:

- **No CO2-volumes measurement** anywhere. The carbonation acceptance test is "foam head, bubble train, no sputter" — pure operator gestalt. Commercial soft drinks dissolve roughly 3.5–4.2 volumes of CO2; the sparge architecture in `hardware/future.md:21` is targeted at "fast Henry's-law equilibration" at 90 PSI head pressure and ~2 °C water, but no acceptance number is committed and no instrument is in the bench kit.
- **No serve-temperature acceptance against a can**. Acceptance step 5 says ≤6 °C in the glass; a refrigerated can comes out at 3–5 °C in a kitchen. The two might overlap or might not — the test is bounded loosely enough that a unit can pass without matching can temperature.
- **No sensory-comparison protocol against a canned reference.** `acceptance-and-burn-in.md:84`: *"Tasting is allowed but not the pass criterion; the volume and the refractometer reading are."* This is correct *as far as it goes* for end-of-line factory acceptance (one operator, no statistical power, palate fatigue across 12 units/year), but it leaves the product-level claim untested at any cadence anywhere in the repo.
- **No design-change re-test trigger.** The integrated build changes substantively from the prototype on every axis that affects sensory outcome: sparge replaces the Beduan atomizer, the chiller targets 2 °C instead of relying on a Lillium upstream, the peristaltic flavor pumps are mounted differently and run at slightly different geometry, and the 1:20 ratio is held by a hand-tuned duty-cycle curve. Each change is justified on its own engineering merits, and none has a paired-comparison test that re-verifies the central claim survived the change.

The closest thing in the repo is `business/regulatory.md` and the existing acceptance-and-burn-in procedure. Neither addresses **"does the output match a can in a blind test?"**

For a $7,500 hand-built unit whose first-time-buyer purchase question #1 in [`target-market.md:266`](../../marketing/target-market.md) is literally **"Does it taste right? Pass/fail. Same formulation, colder, fizzier than a can. It does."** — and where the answer "It does" is currently a personal belief of one person, not a measurement — this is a load-bearing gap.

## Why the existing checks are not enough

Three reasons the volumetric-ratio + visible-carbonation + ≤6 °C battery does not stand in for can-match acceptance:

1. **Ratio fidelity ≠ taste fidelity.** Even at a perfect 1:20 ratio, the *vehicle* (water) is now different from the can's water in CO2-saturation level, temperature, hardness, and chloride. Pepsi's bottling plants hold tight specs on each of these because they each move the perceived product. A unit can hit 1:20 and produce a drink that no Diet Mountain Dew drinker would call Diet Mountain Dew.
2. **"Bubble train" is not a carbonation measurement.** Two glasses of carbonated water with the same surface bubble behavior can hold meaningfully different dissolved-CO2 levels — visible bubbles are a function of nucleation sites and surface tension, not dissolved gas content. A can of Diet Mountain Dew holds ~3.7–4.0 volumes of CO2. A 90 PSI / 2 °C sparge equilibrated for full residence time *should* land in that band — but "should" is a Henry's-law prediction, not a measurement. The sparge stone could foul, the headspace pressure could drift below regulator setpoint, the inlet water could be warm-charged after a refill, and the operator's "bubble train looked fine" would not catch any of it.
3. **One-operator end-of-line taste is below the noise floor.** At ~12 units/year solo build, the operator tastes one assembled unit per month. Palate calibration drifts across that interval. Without a paired canned reference tasted under the same conditions, the operator's "tastes about right" carries roughly the statistical weight of a single anecdote. The factory-acceptance failure mode this catches: drift large enough to be obvious. The failure mode it does not catch: drift inside the obvious band that nonetheless makes the customer stop drinking from the faucet by month 4.

## What the gap actually is — five specific sub-gaps

### S1. No CO2-volumes acceptance number, and no instrument in the kit

The hardware is built around "90 PSI, ~2 °C, sparge stone, fast equilibration." The *implicit* target is "matches a can," which for North American cola/dew commercial product is in the 3.5–4.2 volumes-of-CO2 band. That implicit target has never been written down as a number, and the bench has no way to read it.

Three realistic instrument options to evaluate:

- **Aluminum-can–style volumes-of-CO2 measurement by zahm-nagel-style piercer + pressure-and-temperature read.** Industry standard for canners but requires a Zahm-Nagel piercer (~$1.5k–$2.5k new) and a sealed pressure-temperature read. Overkill for solo-build cadence but the format the canners use; included for completeness.
- **Carbo-cap (Anton Paar style or hobbyist clones)** measures dissolved CO2 in an open glass via Henry's-law headspace equilibration. ~$300–800 hobbyist range, ~$3k+ instrument-grade. Suitable for end-of-line acceptance with one calibration step per session.
- **DIY pressure-temperature method.** Pour into a known-volume bottle, seal with a gauge cap, agitate, read equilibrium pressure and temperature, convert via the standard volumes-of-CO2 table. ~$50 in parts (capper + pressure gauge + thermometer). Coarse but real — and *vastly* better than "bubble train looked fine."

Open: which method is acceptable. The DIY pressure-temperature method is the right starting point — it gets the bench from "no measurement" to "a number," which is the first-order improvement worth taking. The Carbo-cap class instrument is the right next step if the DIY method's repeatability proves too coarse to discriminate good units from drifting ones.

### S2. No glass-temperature acceptance against a can

Acceptance step 5 sets ≤6 °C as a pass band. A refrigerated can opened from a household fridge is 3–5 °C at the lip. The acceptance band overlaps but does not require the appliance to actually match a can.

The fix is one line: serve temperature is acceptable when it falls inside (can-reference − 1 °C, can-reference + 1 °C). Take the canned reference temperature at the same time and on the same thermometer the unit is measured with. This eliminates ambient-temperature confounds and locks the acceptance to the actual claim ("ice cold" relative to the substitute experience the customer is replacing).

The instrument is already in the bench kit (`acceptance-and-burn-in.md:9` — thermocouple gun or food thermometer). The change is procedural, not capital.

### S3. No paired-comparison sensory protocol against canned reference

The repo has no protocol for *comparing* the dispensed product to its canned equivalent. The literature is well-established here; the appropriate test for "is the product matched or not?" is one of:

- **Paired-comparison (2-AFC, "which is which?")** — simplest; tells you the operator can or cannot tell them apart. Statistically weakest but the right starting point because it directly answers the marketing claim ("indistinguishable").
- **Triangle test (3-AFC, "two are the same, one is different — find the different one")** — the canonical sensory-science test for "is there a perceived difference?" Conducted across 8–15 tasters, gives a p-value against the null "no difference." This is the right test once Ring 1 customers exist and the Ring 1 install consults (`2026-05-18/install-consult-playbook-gap.md`) become an obvious recurring opportunity to put 10 trained palates on one unit.
- **Duo-trio test** — middle ground, useful for trained panel calibration.

Recommendation: lock the **paired-comparison test** as the per-unit factory acceptance ("operator must fail to discriminate dispensed-vs-can at α = 0.05 over n = 8 paired tastings, served blind, two glasses at the same temperature"), and the **triangle test** as the annual-cadence design-validation test (once-per-design-change, n = 12 tasters drawn from Ring 1 customers + founder + spouses + friends-of-friends, served blind in randomized labeled order). Both protocols are off-the-shelf in the sensory-science literature; the work is committing the n, the α, and the data-archival path.

### S4. No re-test trigger on design change

Today, a design change anywhere in the carbonation chain — sparge stone PN swap, 90 PSI setpoint change, evaporator coil re-wind, peristaltic tube material change, target-temperature change — proceeds through the engineering review without a paired re-test against the canned reference. The implicit assumption is "if the volumetric ratio is preserved and the temperature band is preserved, the taste is preserved." That assumption is exactly what this gap challenges.

A short list of "any of the following changes requires a paired-comparison re-test before the change is allowed to leave bench" lives naturally in `hardware/future.md` or a sibling. Candidate triggers:

- Any change to the sparge architecture (stone PN, stone porosity, headspace geometry, CO2 setpoint).
- Any change to carbonator wall temperature target or hysteresis.
- Any change to the peristaltic pump tubing material or geometry, OR to the duty-cycle curve in firmware.
- Any change to the dispense nozzle or air-switch / faucet geometry that alters the in-glass mixing.
- Concentrate SKU change (handled at concentrate-supply-resilience-gap level but the sensory leg of that decision lives here).

### S5. No data home for sensory results

Acceptance-and-burn-in §12 archives per-serial volume, temperature, refractometer (optional), compressor cycle data. There is no field for "operator paired-comparison result against canned reference" or "operator-measured CO2 volumes." Adding these is a schema change to whatever `logs/<serial>/acceptance.json` ends up being (per-unit-portal-gap from 2026-05-18 also touches this path), plus a row in the bench-acceptance UI for the operator to enter the result.

The Ring-1 customer data path is the more interesting one. The internal plan in `target-market.md:170` names "units in homes generating real-world use data" as the deliverable of phase one. A paired-comparison test conducted at the customer's home during the Ring-1 install consult, with the customer's own can and the customer's own glass, is the single highest-quality data point any version of this program will ever generate. There is no doc anywhere for capturing it.

## Suggested next actions, in dependency order

1. **Commit a number for target dissolved CO2 in the dispensed product.** The literature gives a window (3.5–4.2 volumes for North American cola/dew); the appliance should claim a target inside that window with a tolerance band. This is a one-line edit to `hardware/future.md` plus a corresponding pass band in `acceptance-and-burn-in.md`. ~15 minutes of writing, after a decision call on what number to pick.
2. **Add the DIY pressure-temperature measurement to the bench kit.** $50 in parts (capper + carbonator-cap with gauge + thermometer). Document the method as one step inserted into `acceptance-and-burn-in.md` between current steps 5 and 6.
3. **Lock the paired-comparison sensory protocol for per-unit acceptance.** n = 8 paired tastings, α = 0.05, served blind by a second operator (founder's spouse, friend, neighbor — any non-builder), result logged. The decision rule: if the operator distinguishes correctly on > 6 of 8 trials (p ≈ 0.04 under the null), the unit fails sensory acceptance and an investigation step is triggered. The investigation order: re-measure CO2 volumes, re-measure ratio, re-measure temperature, re-taste with a different reference can, escalate.
4. **Lock the triangle-test design-validation protocol.** n = 12 tasters, run annually OR on any S4 design-change trigger, whichever is sooner. Customers in Ring 1 are the natural panel; a recruited Ring-1 panel of 6–10 customers tasting each Ring-2 design-change candidate is the highest-leverage form this can take.
5. **Add a `taste` block to `logs/<serial>/acceptance.json`** with fields for CO2 volumes, can-reference temperature delta, paired-comparison n / correct-count / p-value, operator identity, reference-can lot code, and date. Same archive path as the existing acceptance log.
6. **Add a step to the Ring-1 install-consult playbook** (`2026-05-18/install-consult-playbook-gap.md`) that runs a single paired comparison with the customer's own can in their own kitchen, captures the result, and adds it to `logs/<serial>/field-taste.json`. This is the single richest data point the Ring-1 program produces and right now nothing in the repo asks for it.

## What this is NOT

- Not a request to delay unit 001. The pressure-temperature CO2 measurement and the paired-comparison protocol are both low-capital, sub-day procedural additions. Unit 001 can ship through them. The cost of *not* doing them is that unit 001's central claim is unverified at handoff and remains so for the life of the unit.
- Not a request for FDA / commercial-soft-drink-grade sensory facilities. The home-soda-machine sensory chain is naturally small-n at this stage; the protocols above are the small-n versions of the right tests, not laboratory-grade panels.
- Not a duplicate of flavor-metering-fidelity-gap. That doc fixes the *upstream* unverified term (1:20 ratio in physical units). This doc fixes the *downstream* unverified claim (the assembled output matches the can). Both are required; neither stands in for the other.

## One sentence of why this matters at $7,500

The Founder Edition buyer is paying $7,500 because they believe — on faith in the founder — that the dispensed product is the canned product. That belief carries the sale. If a customer four months in starts to suspect their machine doesn't quite match the can anymore and the appliance has no way to tell them whether they're right or wrong, the founder loses both the customer and the Ring-2 referral the customer was supposed to generate. The cost of catching that drift on the bench is two cheap instruments and one short blind tasting. The cost of not catching it is the marketing claim that funds the entire enterprise.
