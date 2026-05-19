# Flavor metering fidelity — the 1:20 ratio is a UI label, not a measured volumetric chain

**Author:** hourly agent, 2026-05-19 (fifteenth of the day)
**Status:** recommendation only — not for direct execution
**Audience:** Derek, future agents

**Distinct from siblings today:**
- [integrated-firmware-gap.md](integrated-firmware-gap.md) — *firmware target doesn't exist*. This doc accepts that prototype firmware is what works today and asks: even if a clean integrated rewrite lands, what does it have to compute, and against what calibration data? The two docs touch the same source file but ask different questions.
- [concentrate-supply-resilience-gap.md](concentrate-supply-resilience-gap.md) — *what happens when the SKU is unavailable*. This doc is upstream of that: assume the SKU is on hand; will what comes out of the faucet actually taste like it?
- [trademark-and-brand-name-usage-gap.md](trademark-and-brand-name-usage-gap.md) — *legal exposure of saying "Diet Mountain Dew"*. This doc is the matched physical-fidelity exposure: if we say "Diet Mountain Dew" and the unit drifts noticeably off-recipe in month four, the legal exposure is the smaller of the two problems.
- Yesterday's [warranty-and-rma-gap.md](../2026-05-18/warranty-and-rma-gap.md) — *what happens when something physically breaks*. Metering drift is the opposite failure mode: nothing is broken, the customer just slowly stops trusting the taste.

---

## TL;DR

The product's central marketing premise — [`marketing/target-market.md:11`](../../marketing/target-market.md): *"real brand-name diet soda ... ice cold, fully carbonated, on demand"*; and from [`README.md` / `hardware/future.md`](../../hardware/future.md):1 *"indistinguishable from the canned product"* — rides on one number: **1:20**. SodaStream-Pepsi concentrate is formulated to be diluted 1:20 (volumetric) into carbonated water, and the taste premise *only* holds if the appliance delivers that ratio, on every pour, in every unit, for the appliance's design life.

Today the **1:20 ratio** appears in the firmware as a UI integer that drives a hand-tuned duty-cycle curve:

```cpp
// firmware/src/main.cpp:435–448
//   S = 2.5 at FLAVOR_RATIO=6  (constant on at full flow)
//   S = 1.0 at FLAVOR_RATIO=20 (baseline recipe)
float S = 2.5f - 1.5f * (ratio - 6) / 14.0f;
```

The curve was empirically tuned on the prototype. There is **no documented derivation** anywhere in the repo from "Kamoer KPHM400 with this silicone tubing delivers N mL per second" + "DIGITEN flow meter reads M pulses per mL of carbonated water at our line pressure" → "therefore to produce 1:20 volumetric in the glass, on-time should be X ms per pulse-interval." The curve is `SHAPE_ON_BASE = 20`, `SHAPE_ON_SLOPE = 30`, etc. — magic numbers that produced a glass of soda that tasted right to *one person* on *one prototype* at *one moment in time*.

The on-bench acceptance step at [`hardware/assembly/acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md):82 measures *total dispensed volume* against ±5% of 262.5 mL and an *optional refractometer reading* with "no absolute number locked here" (Open item §5 in the same doc). That test is a reasonable end-of-line sanity check but it is not a calibration — it does not feed any per-unit number back into firmware, and it does not characterize anything that drifts with age.

This is the actual taste-fidelity chain, end to end:

```
"Diet Mountain Dew tastes like Diet Mountain Dew"
   ↑ requires
1:20 ± perceptual-tolerance volumetric ratio in glass
   ↑ requires
Kamoer KPHM400 mL/sec  ×  pump on-time  ==  1/20  ×  DIGITEN-mL/pulse × pulse-count
   ↑ requires that every term on both sides is *known*, *measured*, and *stable*
```

**Of the four terms required to be known: zero are.**

1. Kamoer KPHM400 mL/sec with the BOM-spec tubing — never measured in this repo.
2. Pump on-time as a function of "ratio" — derived from a magic-number curve, not from term 1.
3. DIGITEN B07QQW4C7R pulses-per-mL **on carbonated water at 90 PSI line pressure** (not on the plain water in DIGITEN's datasheet) — never characterized.
4. Pulse-count over a pour — read in real time but only ever compared against itself.

Compound this with three drift mechanisms — peristaltic tube wear, concentrate-viscosity variation with reservoir temperature, and the first-pour-after-ship / first-pour-after-idle effects — and the picture is: **every Founder Edition unit ships with hand-tuned taste fidelity, drifts from there at unknown rate in unknown direction, and has no in-service feedback path back to "still 1:20"**.

For a product whose entire premise is *not* the off-brand approximation, this is the gap that most directly threatens the premise. It is not a build-blocker (units will work, soda will come out) but it is a *promise-blocker* — the marketing line breaks before the warranty runs out.

---

## Five specific gaps within this area

### G1. The "ratio" → duty-cycle curve has no derivation from physical units

[`firmware/src/main.cpp:354–364`](../../firmware/src/main.cpp):

```cpp
// ── Recipe shape (empirically tuned baseline, not user-adjustable) ──
// These define how duty cycle scales with flow rate.
// At FLAVOR_RATIO=20 (baseline) they produce:
//   1 pulse →  50 on / 600 off  (7.7% duty)
//   6 pulse → 200 on / 300 off  (40% duty)
#define SHAPE_ON_BASE    20
#define SHAPE_ON_SLOPE   30
#define SHAPE_OFF_BASE  660
#define SHAPE_OFF_SLOPE  60
```

The comment says "empirically tuned baseline" — i.e. someone watched soda come out of the prototype and adjusted these four constants until it tasted right. That is a perfectly legitimate way to *start*, and it is exactly the wrong way to *commit*.

What's missing is the one-page derivation:

> Kamoer KPHM400 with 1/8" ID × 1/4" OD silicone tube delivers `q_pump` mL/sec at PWM=255 (measured: TBD). DIGITEN B07QQW4C7R on the carbonated-water dispense line at 90 PSI inlet delivers `k_flow` pulses/mL on 2-phase carbonated flow (measured: TBD). To produce volumetric ratio 1:R in the glass, the integral of `q_pump × duty(t)` over the pour must equal `(1/R) × (pulse_count / k_flow)`. Solving for steady-state duty cycle: `duty = (q_water / q_pump) / R = ...`. The four shape constants are then chosen to track this target across the FLOW_MIN_PULSES → FLOW_FULL_PULSES range.

That paragraph does not exist in the repo. It needs to.

Once it exists, the magic numbers either (a) match what the math predicts within the noise floor of the empirical tune, in which case great, we have a derivation and we can defend the curve; (b) disagree, in which case one of `q_pump`, `k_flow`, or the prototype's hand-tune is wrong and we want to know that *now*, on the bench, not 18 months in when a customer says "this tastes flat."

### G2. The DIGITEN flow meter has never been characterized on carbonated water at line pressure

The DIGITEN B07QQW4C7R is a hall-effect impeller flow meter. The manufacturer's datasheet calibration is for **plain water**. In service it sees **carbonated water at the cold-core outlet under CO2 head pressure**, depressurizing across the faucet seat. Three differences vs. the datasheet:

1. **Two-phase flow.** Dissolved CO2 comes out of solution as the pressure drops at the faucet seat (and to some extent earlier, in the flow meter itself). The impeller's pulse rate on a two-phase fluid is not the same as on a single-phase fluid — bubbles slip past the vanes; the impeller can over-spin in slug flow.
2. **Pressure-dependent flow rate.** At 90 PSI vessel head and a fully-open faucet, the volumetric flow rate is much higher than the datasheet calibration condition (typically ~1 PSI head on a water test fixture). The DIGITEN is rated up to a flow ceiling; near that ceiling its pulses-per-mL drifts.
3. **Cold viscosity.** At 2 °C, water is ~70% more viscous than at 25 °C. Hall-effect flow meters with low-friction impellers are mostly insensitive to viscosity, but "mostly" is not "characterized."

The acceptance test at [`acceptance-and-burn-in.md:76`](../../hardware/assembly/acceptance-and-burn-in.md) treats the flow meter as the gold-standard volume sensor for the "dispense volume approximately 12 oz" pass criterion. If `k_flow` is wrong by 15% on carbonated water, the acceptance test passes a unit that's actually pouring 14 oz, the customer's first pour fills their glass strangely, and the pump duty cycle is computed against a flow signal that's lying.

This gap is fixable on the bench with a kitchen scale and a stopwatch. Pour known volumes of carbonated water into a tared container, count pulses, plot. Do this once, commit the curve to firmware-and-commissioning notes, and the flow meter becomes a trustworthy sensor.

### G3. Peristaltic tube wear is the largest drift mechanism and there is no service interval

Peristaltic pumps wear their silicone tube as a known function of run-time. Kamoer's own application notes for the KPHM400 family (silicone tubing) describe a ~30–50% reduction in delivered volume-per-revolution between fresh tube and end-of-life, occurring over hundreds of hours of run-time depending on duty cycle, viscosity, and inlet pressure.

In service at this product, the pumps run at a duty cycle that varies with flow rate (G1) and roughly tracks the active dispense window. For a household at 4 sodas/day with ~3 seconds of pump-active per pour, that's ~12 seconds/day × 365 days = ~4,400 seconds/year ≈ 1.2 hours/year — well under the wear horizon for any single year. But:

1. The wear curve is **monotonic and one-way**. Even slow wear eventually shifts taste.
2. The customer probably swaps the cartridge for *cleanability* (and because it's been designed to be swappable per [`future.md`](../../hardware/future.md):85, palm-squeeze release plate, John Guest quick-connects) before they swap it for *wear*. After they swap it, the curve resets to fresh — but with a step-change in delivered volume that the firmware doesn't account for.
3. The two pumps wear independently. Cross-channel drift accumulates.

What's missing:

- A characterization curve: mL/revolution vs. cumulative run-seconds, plotted to end-of-life on at least one tube + pump. Once. With the result committed to `printed-parts/cold-core/reservoir/level-sensing.md` or a sibling characterization doc.
- A firmware-side cumulative run-time counter per pump, persistent across reboots.
- A service-interval threshold based on the characterization (something like "swap the cartridge at 1,000 cumulative seconds of pump-on" — number TBD), surfaced in the iOS app as a maintenance notification.
- A post-swap recalibration. Even a one-shot "after you swap the cartridge, the app runs a 30-second timed test pour, you measure the volume, you tell the app the number" loop would close this. Better: a per-pump small EEPROM constant in the firmware that the app updates after a calibration pour.

Without G3 closed, the appliance silently drifts off-recipe in proportion to how heavily it's used. The heaviest users are the customers who hate the cans the most — the bullseye target market — and they're the ones for whom drift will be most noticeable.

### G4. Concentrate viscosity varies with reservoir temperature, in the range the cold core operates in

[`hardware/future.md`](../../hardware/future.md):81: *"The flavor reservoirs passively pre-chill to roughly 8–15 °C by sitting in the thermal gradient ..."*. This is a 7 °C range, not a fixed point. SodaStream concentrate is roughly 1.05 g/mL syrup with a viscosity that doubles or triples across that range (dilute sucralose/citric acid syrups are not as bad as full-sugar HFCS, but they are not water either — for reference, Coke-style HFCS concentrate at 4 °C is ~5× more viscous than at 20 °C).

The Kamoer KPHM400 is a positive-displacement pump and is relatively insensitive to outlet viscosity. But:

- **Inlet suction at low temperature** matters. The reservoir is gravity-fed to the pump inlet (per the manifold in [`topology/fluid-topology.md`](../../hardware/topology/fluid-topology.md)); the cold concentrate column has to flow into the pump head fast enough for the squeeze tubing to fill between revolutions. At the cold end of the range, the inlet might starve and the delivered volume drops.
- **Tube relaxation after the roller passes** is what re-fills the squeeze tubing between strokes. Cold silicone is stiffer and relaxes more slowly. This is exactly the regime where peristaltic dispense volume drops.

What's missing: a 2-point viscosity check on the dispense curve. Run a dispense at 8 °C reservoir temp and again at 15 °C, measure the volume out, and confirm the spread is within the perceptual tolerance the product will commit to (G5). If it isn't, the firmware needs to either (a) compensate via the existing flavor-reservoir DS18B20 hookup (which isn't in the integrated wiring per [`firmware-and-commissioning.md:111`](../../hardware/assembly/firmware-and-commissioning.md) — only the carbonator wall and evap suction DS18B20s are listed), or (b) the reservoir temperature range needs to be narrowed by active control.

### G5. There is no committed perceptual-tolerance threshold for ratio drift

[`acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md) Open item §5: *"the 1:20 ratio is documented as the design target. The ±5% volume band and the ~10% channel-to-channel agreement band in this doc are starting points; the production-final ratio tolerance ... needs a committed number that ties back to the perceived-taste impact of small ratio drifts on the SodaStream concentrate formulation."*

That open item is correct as far as it goes. It frames the question as a within-unit acceptance threshold. But the *threshold* number can't be set without a *psychophysical* characterization: at what ratio delta does a typical drinker notice? At what delta do they reject?

This is a doable experiment. Pour three glasses: 1:18, 1:20, 1:22. Taste blind. Either you can tell or you can't. If you can tell easily, the appliance tolerance has to be much tighter than ±10%; if 1:18 vs 1:22 is within noise, the spec can be loose. Repeat for the actual SodaStream Diet Mountain Dew, Diet Pepsi, Pepsi Zero formulations because their sweetener+acid balances are not identical.

This is also one of the easier things in this whole list to do — it doesn't require any of the integrated build to exist. A SodaStream bottle, a graduated cylinder, a 2L CO2 bottle of plain seltzer, and 30 minutes. Output: a real number that all of G1–G4 then have to design to.

### G6. The first-pour-after-ship and first-pour-after-idle behaviors are unspecified

Two related failure modes that hit the customer's *first impression*:

**G6a. First pour after dry-ship.** [`finish-pack-ship.md:11`](../../hardware/assembly/finish-pack-ship.md): *"the system fluid-drained and air-purged dry"*. The peristaltic pump tubes are emptied. When the customer fills the reservoirs at install, the pump has to prime: silicone tubing wets, air pockets clear, the rotor pushes liquid uphill to the nozzle. The first dispense after install is volumetrically unreliable until the pump is primed.

Three open questions: (a) Does the install procedure include a "prime each pump" step? (b) If yes, what is the pump duty cycle during prime, and how does the customer or firmware know the prime is complete? (c) If the customer's first pour is volumetrically wrong because the prime wasn't complete, what is their reaction? This pour is the single most marketed moment in the product — "turn the handle, soda comes out" — and it is the most likely to be off-recipe.

**G6b. First pour after a 12-hour idle.** Between pours, concentrate sits in the nozzle-side tubing downstream of the pump. After overnight idle, that resting concentrate has had time to (a) settle (gravitational fractionation in a vertical riser is small at this viscosity but real), (b) lose CO2 sparge from the nozzle merge point, and (c) for the very tip of the nozzle, partially evaporate / concentrate by evaporation through the open faucet outlet. The first pour pushes this resting slug into the glass — at a different concentration than the steady-state pour. The user notices. They drink half a glass of stronger-than-usual soda followed by normal soda.

Mitigation candidates: (i) a small purge-to-drain at idle wake-up (wastes ~5 mL of concentrate per wake), (ii) a redesigned nozzle geometry that minimizes resting concentrate volume, (iii) accept the effect and document it (telling the user "first pour of the morning is a little stronger" is honest and possibly even charming, but only if the founder has decided that and not stumbled into it).

Both of these effects are larger than the steady-state ratio drift of G1–G4. Neither is addressed in any doc I could find.

---

## What a path forward might look like

Listed in rough dependency order. None of these are large pieces of work; the gap is that none of them have been done.

1. **G5 first.** Settle the perceptual tolerance. One blind taste test, one number committed in the repo. Without this, G1–G4 have no design target.
2. **G2.** Characterize the DIGITEN flow meter on carbonated water. Kitchen scale + stopwatch. Commit a `k_flow` constant.
3. **G1.** Write the one-page derivation. Compare the math's predicted duty-cycle curve against the prototype's empirical curve. Resolve any disagreement.
4. **G3.** Characterize one Kamoer KPHM400 to end-of-life on the BOM silicone tubing. Commit a wear curve, a cumulative-run-time service interval, and a firmware-side run-counter.
5. **G6a.** Define a prime procedure. Bench-validate it. Add it to install documentation.
6. **G4.** Bracket-test concentrate viscosity at 8 °C vs 15 °C. If the spread fits inside G5's tolerance, document it and move on. If it doesn't, add a flavor-reservoir DS18B20 to the wiring and compensate in firmware, or tighten the reservoir temperature range.
7. **G6b.** Decide between mitigation, redesign, or honest documentation. Commit the decision.

The integrated-firmware rewrite ([integrated-firmware-gap.md](integrated-firmware-gap.md) today) is a natural moment to fold the result of (1)–(4) into a clean dispense module — replacing the four magic numbers with named constants whose provenance is the work in (1)–(4).

---

## What I'm not claiming

- **I'm not claiming the prototype tastes wrong.** It evidently tastes right enough to the founder, on at least one bottle of Diet Mountain Dew, on at least one day, to have produced [`marketing/target-market.md:11`](../../marketing/target-market.md). The gap is between "tastes right today, here" and "is provably going to taste right in 50 kitchens for a decade."
- **I'm not claiming this is a launch-blocker for unit 001.** Founder Edition is a Ring 1 unit going to a friend at $2,000–3,000 with a personal install consult per [`target-market.md` "The actual goal of phase one is 10 units in homes"](../../marketing/target-market.md). Drift over month one of in-home use is exactly the kind of thing that ring is designed to surface. The gap matters *before Ring 3*, when buyers stop being friends and start being strangers paying the full anchor price.
- **I'm not recommending closed-loop concentration sensing.** An in-line refractometer or conductivity sensor in the dispense path could in principle correct ratio drift in real time, but the part cost, the calibration complexity, and the wetted-materials food-contact qualification would all be substantial. Open-loop calibration plus a periodic check is almost certainly the right architecture at this scale.

---

## Cross-references

- [`marketing/target-market.md`](../../marketing/target-market.md) — the "not the off-brand approximation" promise this gap threatens.
- [`hardware/future.md`](../../hardware/future.md) "Flavor subsystem" — physical hardware described, taste-fidelity chain not.
- [`hardware/assembly/acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md) Open items §5–§6 — same area; this doc deepens it.
- [`hardware/assembly/firmware-and-commissioning.md:5`](../../hardware/assembly/firmware-and-commissioning.md) — "per-customer ratio tuning" is punted to the iOS app, with no spec of how the customer knows what to tune to.
- [`firmware/src/main.cpp:354–448`](../../firmware/src/main.cpp) — the empirically-tuned curve.
- [`hardware/printed-parts/cold-core/reservoir/level-sensing.md`](../../hardware/printed-parts/cold-core/reservoir/level-sensing.md) — natural neighbor for the per-pump wear-curve characterization doc that doesn't yet exist.
