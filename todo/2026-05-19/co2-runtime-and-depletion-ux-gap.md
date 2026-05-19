# CO2 runtime & depletion-UX gap — what the appliance knows about the customer's CO2 cylinder

*Hourly-agent recommendation, 2026-05-19. Distinct from yesterday's `co2-supply-ownership-gap.md` (commercial: who owns the cylinder fleet) and from `pie-in-the-sky/co2-service.md` (logistics: hazmat shipping of refills). This doc is about the **appliance side**: what the unit measures, what it tells the customer, and how it behaves when the cylinder runs out.*

---

## TL;DR

The integrated appliance currently has **zero instrumentation on the CO2 supply side**. It does not measure cylinder mass, supply-line pressure, or per-pour CO2 dose. The only customer-visible signal that the cylinder is empty is the same one every commercial draft system has had since 1950: the soda goes flat, mid-pour, with no warning. That is a "He hates these cans" failure — the *exact* recurring household annoyance the product promises to eliminate ("run out of soda" → "run out of the thing that makes the soda" is the same emotion in a different costume).

The fix is two cheap parts ($15–30 BOM total), two firmware behaviors, and one app screen. The hardest part is **deciding** what we want; the engineering after that is a few hundred lines of firmware and an HX711 or analog ADC channel.

Below: (1) what we know about CO2 budgets from the physics, (2) the four ways an appliance can know its own cylinder state, (3) the recommended combo and why, (4) the customer-facing UX (faucet display, iOS app, lockouts), (5) what to write down in `hardware/future.md`, and (6) what to commission with each Founder Edition unit so this isn't bench-only.

---

## Part 1 — How much CO2 does one pour actually use?

`future.md` doesn't say. `acceptance-and-burn-in.md` says "test rig uses a 5 lb or 10 lb cylinder" without a depletion estimate. The math matters because the answer drives every downstream decision (cylinder sizing recommendation, refill cadence promise, app warning thresholds, whether 5 lb is even the right SKU).

### CO2 dissolved in the dispensed water

Henry's-Law equilibrium for CO2 in water at our operating point (2 °C, 90 PSI headspace pressure with pure CO2):

- Henry's constant for CO2 at 2 °C: ~1.86 g/(L·atm) of dissolved CO2 per atm of partial pressure
- 90 PSI = ~6.12 atm, all CO2 partial pressure (pure CO2 sparge into closed headspace)
- Equilibrium dissolved CO2 ≈ 1.86 × 6.12 = **~11.4 g/L**

That's higher than commercial canned soda (typically 3.5–4 volumes of CO2 = ~7–8 g/L). The vessel can over-saturate compared to a can, which is consistent with the marketing claim "equal or better carbonation."

In practice we will not run the dispensed product at the full equilibrium value because:
- The faucet flash drops pressure from 90 PSI to atmospheric; some dissolved CO2 nucleates as foam at the spout (the visible "head" on the pour)
- The dispensed glass typically holds 7–8 g/L of *retained* CO2 after the flash and sit-time
- Headspace CO2 above the water column also has to be backfilled with each refill cycle

Working estimate: **~3 g CO2 enters the glass per 12 oz (355 mL) serving** as dissolved-and-retained gas.

### CO2 lost to the system per pour (the dominant cost)

The dissolved-in-the-glass number is a lower bound. The appliance loses gas to several non-product sinks every cycle. Order-of-magnitude estimates:

| Sink | Per-pour mass | Reasoning |
|---|---|---|
| Dissolved CO2 in dispensed water | ~3.0 g | from above |
| Flash at faucet (foam head, not retained in glass) | ~0.5 g | typical 10–15 % of dissolved CO2 lost to ambient on the pour |
| Headspace re-pressurization after refill | ~1.0 g | a 12 oz dispense lowers water level → headspace volume grows by ~355 mL at 90 PSI; 355 mL of 90 PSI CO2 ≈ 1.0 g |
| Sparge-stone over-injection (not fully dissolved) | ~1.0 g | sparge produces some headspace CO2 the headspace can't absorb at equilibrium; ends up in the next refill's vent or the next flash |
| Vessel/joint passive leakage between pours | ~0.1 g/hr | small, but real over a multi-month cylinder cycle |
| Clean-cycle CO2 use (if any) | TBD | depends on whether clean cycle uses CO2 for line-purge — see `reservoir-microbio-and-clean-policy-gap.md` from today |
| **Working budget per 12 oz pour** | **~5.5 g** | sum of dispense-coupled sinks |

For commercial-soda benchmarking: post-mix soda fountains in QSR operation budget about **6–8 g CO2 per 12 oz drink** end-to-end (BIB-syrup + carbonated water, with similar carbonator losses). Our number should land in the same envelope. **Use 6 g/serving as the working planning constant** — it has margin over the dispense-coupled estimate and matches industry numbers.

### Cylinder runtime

Standard CGA-320 aluminum CO2 cylinders, by net CO2 mass:

| Cylinder size | Net CO2 (g) | Servings at 6 g each | Typical household runtime |
|---|---|---|---|
| 2.5 lb | 1,134 | ~189 | ~6 weeks for 2 sodas/day household |
| 5 lb | 2,268 | ~378 | ~3 months for 2/day, ~2 months for 3/day, ~6 weeks for 4/day |
| 10 lb | 4,536 | ~756 | ~6 months for 2/day, ~4 months for 3/day, ~3 months for 4/day |
| 20 lb | 9,072 | ~1,512 | ~1 year for 2/day household |

This matters for the marketing claim. The target-market doc and `co2-service.md` casually say "CO2 lasts months" without specifying which cylinder size. At 5 lb and a typical 2.5/day combined household (1.25 servings × 2 drinkers), that's about **10 weeks** — call it "two to three months." That is honest and matches the implicit 5 lb / CGA-320 ecosystem the rest of the system targets.

**Recommendation: standardize on 5 lb cylinder as the default specified size**, with a note that 10 lb is supported by the same regulator and fits in most under-sink cabinet side gaps. The 5 lb form factor is also what the `co2-service.md` refill loop is built around, what the `cga320-kit.md` budget product uses, and what virtually all kegerator owners already have. Cylinder homogeneity across product lines is its own benefit.

### What's *not* in this estimate

Two things that should be measured on an actual unit before committing the 6 g number to firmware:

1. **Sparge-stone CO2 yield**: how much of the injected CO2 dissolves vs. bubbles straight to headspace. The 0.5 µm FERRODAY stone is sized for fast dissolution, but the actual residence time in the ~6"-tall vessel water column is short (a few seconds). If yield is lower than assumed, headspace re-pressurization costs go up and per-serving CO2 use rises.
2. **Refill-cycle CO2 reabsorption**: when the SeaFlo refill pump runs, fresh water enters the headspace and immediately starts absorbing CO2 to equilibrium. The headspace pressure drops, the WR1110 secondary regulator opens, and CO2 flows in. Some of this is "useful" CO2 (it ends up dissolved). Some is overhead. The split matters.

Both numbers can be measured gravimetrically during burn-in with a kitchen-scale on the test-rig CO2 cylinder — see Part 6.

---

## Part 2 — Four ways an appliance can know its cylinder state

The appliance currently knows nothing. The customer's first warning that the cylinder is empty is a flat pour. We need a better mechanism. There are four candidates, ordered by directness:

### Option A — Gravimetric: load cell under the cylinder

Put the cylinder on a 50 kg-capacity load cell wired to an HX711 24-bit ADC, ESP32 GPIO. Read the cylinder's mass directly. Subtract a tare value captured at "cylinder installed" time.

- **Pros**: ground-truth measurement. Resolves to a few grams. Linear from full to empty. Self-calibrating across cylinder swaps (the tare captures the cylinder's own tare weight, which varies cylinder-to-cylinder).
- **Cons**: requires the cylinder-placement affordance (per `front-panel/README.md` Open items, on the side-face exterior surface that doesn't have a doc yet) to integrate a load cell pocket. The customer has to actually seat the cylinder on the load cell, not next to it. If the cylinder leans against the cabinet wall or the customer's CGA-320 regulator + flex hose lifts part of the cylinder weight, the reading is wrong. Requires solving a mechanical bracket / cradle problem that hasn't been started.
- **BOM**: HX711 module + 50 kg load cell ~$8 on Amazon. Cradle / pocket: an enclosure-exterior printed part addition.
- **Calibration burden**: tare on swap (one-button "cylinder installed" in the iOS app), one factory zero per unit.

### Option B — Supply-line pressure transducer (upstream of WR1110)

Tap a 1/4" NPT pressure transducer (0–1500 PSI range) into the CO2 line between the customer's CGA-320 primary regulator and the WR1110 fixed-90 PSI secondary. Read with an analog GPIO via the ESP32's onboard ADC.

The physics: a CGA-320 5 lb cylinder is *liquid* CO2 in the cylinder, with the vapor at the cylinder's saturation pressure (~830 PSI at room temperature). As the customer draws gas, the liquid evaporates to replace it, so the pressure stays at ~830 PSI for almost the entire life of the cylinder. Only when the last of the liquid is gone does the pressure drop — and then it drops fast, from 830 PSI to 90 PSI (the WR1110 setpoint, below which the appliance can no longer pull 90 PSI carbonation) in a matter of pours. The customer-side primary regulator is set somewhere in 70–100 PSI per spec, so what we actually see at the transducer is whatever the primary regulator passes through, which is the primary's setpoint — until upstream pressure drops below the primary setpoint, at which point the primary regulator stops regulating and the transducer reads the cylinder's actual head pressure.

- **Pros**: cliff-detection is reliable. The transducer reads a steady value for the entire cylinder life, then a steep drop in the last few percent. Hard to false-alarm. Cheap. No mechanical integration with the cylinder.
- **Cons**: not linear — gives the customer a sudden "you have a day left" warning instead of a smooth gauge. Can't differentiate "half full" from "85% full". Has to be installed in the appliance's CO2 line, not on the cylinder, which means we're sensing the customer's regulator output rather than the cylinder directly.
- **BOM**: any 1/4" NPT 0–1500 PSI transducer with 0.5–4.5 V output (typical Amazon Prime: ~$15). Plus a 1/4" NPT tee in the line.
- **Calibration burden**: factory zero one time; no per-cylinder action.

### Option C — Per-pour dispense counter + assumed dose

Firmware counts every pour event (already needed for diagnostics, app history, dispense-count maintenance triggers per `reservoir-microbio-and-clean-policy-gap.md`). Multiply by a stored "grams per pour" constant (the 6 g number above, or a per-unit-calibrated value). Subtract from a known starting mass that the customer enters on cylinder swap ("I just installed a fresh 5 lb cylinder" → tank = 2,268 g).

- **Pros**: no new hardware. Pure firmware + UX. Gives a continuous "% remaining" or "days remaining" estimate based on rolling usage rate.
- **Cons**: drifts. Sparge inefficiency varies with water temperature, headspace pressure, refill timing. Passive leakage isn't counted. Vessel back-pressure changes mean the dose isn't actually constant. Most importantly: the customer has to remember to tell the appliance which cylinder size they just installed, and reset the counter on each swap. Forgetting the reset corrupts the estimate forever.
- **BOM**: none.
- **Calibration burden**: per-pour-dose calibration at factory burn-in (Part 6); per-swap reset by customer.

### Option D — Combination: dispense counter + supply-line cliff

Run C in normal operation as the day-to-day "% remaining" estimate. Run B as a backstop that catches the actual end-of-cylinder cliff regardless of whether the counter drifted or the customer forgot to reset.

- **Pros**: best of both. The dispense counter gives a continuous gauge with no extra hardware to fail. The pressure transducer guarantees the customer gets a hard "stop dispensing, your cylinder is empty" warning even if the counter is wrong, and acts as an auto-correct: if the cliff fires while the counter still says 40% remaining, the counter recalibrates to "empty" and the firmware logs the discrepancy for inspection on the next unit-health diagnostic.
- **Cons**: $15 BOM + one tee + one ADC channel.
- **Calibration burden**: same as B + C combined.

### Recommendation: Option D

The $15 transducer is the right call. The whole product premise is "no recurring household annoyance." An end-of-cylinder false-confidence event — customer pours a glass of flat water for their guest because the app said the cylinder was still half-full — is exactly the kind of moment that turns a $7,500 buyer into a refund request and a one-star review. The hardware backstop is cheap insurance.

The load cell (Option A) is correct in principle and gives the most beautiful UX (smooth gauge, no customer action on swap). But it requires solving the cylinder cradle / placement geometry that the front-panel and side-face docs both flag as "not yet written." Defer until that surface is committed. Add it as a future enhancement.

---

## Part 3 — Customer-facing UX

### Faucet display (RP2040 round display)

Already shows active flavor logo per `future.md`. Add a small CO2-state icon in a corner:

- **Normal** (>20 % remaining estimated, supply pressure healthy): no icon
- **Low** (5–20 % remaining): small yellow CO2 cylinder icon, persistent
- **Critical** (<5 % remaining OR supply-pressure transducer reads <120 PSI for >5 seconds during steady state): red icon, blink
- **Empty** (supply-pressure transducer reads <100 PSI under steady draw — the WR1110 can no longer hold 90 PSI carbonation): red icon, solid, and **dispense lockout** (see below)

This is glanceable at the faucet. Doesn't require the customer to open an app.

### iOS app (`ios/SodaMachine/`)

Three things in the app:

1. **CO2 cylinder card** on the main screen: cylinder graphic with a fill level, "~X servings remaining" estimate, "~Y days at your current rate" estimate. Tap to see the dispense-counter history and the supply-pressure trend.
2. **Push notification** at 20 % estimated remaining: "Your CO2 cylinder is getting low. Order a refill or schedule a swap so you don't run out." With a one-tap "Order from [our service / your local supplier]" button — this is the natural hook into the `co2-service.md` refill subscription if/when that exists, or a "find local supplier" map for the meantime.
3. **Push notification** at supply-pressure cliff: "Your CO2 cylinder is empty. The faucet is locked until you swap it. Here's how." Linked to a swap instructions page.

The notification cadence is asymmetric on purpose: the 20 % warning is the "this is your week to handle it" nudge that respects the customer's life; the cliff alert is the "this is now" interruption that only fires when there's nothing they can do but act.

### Cylinder-swap workflow

When the customer swaps the cylinder, they need to tell the appliance. Two equivalent paths:

- **App**: "I just installed a new [5 lb / 10 lb] cylinder" → counter resets to that capacity. One tap.
- **Faucet**: long-press the KRAUS air switch (or whatever the dual-purpose gesture turns out to be) when the dispense is locked out → counter resets to 5 lb default.

The faucet path is the "I can't find my phone" backup. The app path is the primary because it lets us record the cylinder size correctly and offer the "want to schedule the next refill automatically?" upsell.

### Dispense lockout — the most important UX call

When the appliance detects the supply-pressure cliff, **lock dispense**. Do not pour. Do not pour flavor either.

The product's identity is "real Pepsi-made concentrate injected into cold carbonated water from a faucet, indistinguishable from canned." Flat water + flavor is not that product. It is a worse experience than no soda at all, because it sets a frustration-anchor ("the machine is broken / the concentrate is wrong / something is off") that the customer carries forward for weeks even after the cylinder is replaced. The product never tasting flat is more important to the brand than the customer being able to extract one more serving from an empty tank.

The lockout should be:
- **Loud**: display + iOS notification + faucet rejection sound
- **Informative**: tells the customer exactly what's wrong and exactly what to do
- **Recoverable**: as soon as the supply-pressure transducer reads back above ~700 PSI (new cylinder installed and valve opened), the lockout clears automatically — no factory-reset required

This is the same "fail safe by refusing to ship a bad product" pattern as the freeze-protect cutout on the evaporator and the backflow drip-pan moisture alarm. The pattern is already in the firmware mental model.

### CO2-out grace mode (optional, requires explicit customer consent)

A possible accommodation: a "still water for now" mode the customer can enable in the app that, when the cylinder is empty, lets the faucet dispense flavored *non-carbonated* water (water + concentrate, no CO2) with a big display warning ("STILL — CO2 OUT") until the cylinder is replaced. Disabled by default. The option exists for the customer who wants to use up the open syrup with their kid's lunch rather than be totally locked out.

Not committing to this; flagging it as a design conversation that should happen before the first Founder Edition ships, because the answer affects how the lockout state machine is structured in firmware. **Default = no grace mode, hard lockout.**

---

## Part 4 — Firmware behaviors

Concrete additions to the ESP32 firmware:

1. **Per-pour dose counter**: every faucet-open event, log `(timestamp, duration, estimated water volume, estimated CO2 grams)` to flash. Decrement the cylinder-mass-remaining estimate.
2. **Supply-pressure ADC poll**: read the transducer on a 1 Hz schedule under steady state, 10 Hz during active dispense. Track a 30-second rolling average to ignore noise.
3. **Cliff detector**: if the 30-second average drops below 700 PSI (cylinder transitioning from liquid to vapor depletion), flag "imminent depletion" — push notification, faucet icon to red.
4. **Lockout trigger**: if the rolling average drops below 100 PSI under draw (WR1110 starved), assert the lockout state. Refuse to open the faucet solenoid. Refuse to dispense flavor.
5. **Recovery detector**: if pressure recovers above 700 PSI (new cylinder installed and valve opened), exit lockout. Optionally request cylinder-swap confirmation via app for counter reset; if not received within 24 hours, assume same-size cylinder and reset to the most recently entered capacity.
6. **Counter-correction event**: when the cliff fires, compare estimated remaining grams against zero. Log delta. This data, accumulated across the Founder Edition fleet, becomes our per-pour-dose calibration ground truth — we can refine the 6 g constant per unit based on actual cylinder lifetimes.
7. **Daily CO2 telemetry**: estimated grams used today, estimated days remaining, supply pressure baseline. Surfaced in the app's history view; also useful for the per-unit health diagnostic in the `per-unit-portal-gap.md` (yesterday) for the Founder Edition portal.

None of this changes the existing GPIO budget materially — one additional ADC channel for the transducer (the ESP32 has plenty). The flash-tracked log volume is small. The MCP23017 expansion isn't affected.

---

## Part 5 — What to add to the canonical docs

### `hardware/future.md` — Carbonation subsystem section

Add to the "CO2 supply" subsection (currently near line 31):

> CO2 consumption is budgeted at **~6 g per 12 oz dispense** (combined dissolved-in-product, flash, headspace re-pressurization, and sparge-injection losses), validated against commercial post-mix benchmarks. At this rate a 5 lb cylinder (2,268 g net CO2) delivers ~380 servings, which is **2–3 months for a 2–3 serving/day household**. The 5 lb cylinder is the standard supported size; 10 lb fits the same regulator and most under-sink cabinet side gaps.
>
> **Supply-side instrumentation:** a 0–1500 PSI transducer (1/4" NPT, 0.5–4.5 V output) on a tee between the customer's CGA-320 primary regulator and the in-appliance WR1110 secondary, read on an ESP32 ADC channel. The cylinder head pressure is steady (~830 PSI saturation) for the cylinder's full operational life and drops sharply (~830 → 100 PSI in a few pours) at end-of-life as the last liquid CO2 evaporates. The transducer is the appliance's ground-truth depletion signal.
>
> **Firmware tracks cylinder state** via a dispense counter (decremented per-pour by the budgeted dose) for continuous "remaining capacity" estimation, with the supply-pressure cliff as a hard backstop. When the rolling supply-pressure average drops below 100 PSI under steady draw, the appliance enters **CO2 lockout**: faucet refuses to dispense (carbonated or flavored), display shows red CO2 icon, app emits a notification with swap instructions. Lockout clears automatically when the transducer reads >700 PSI (new cylinder installed). Counter reset to fresh-cylinder capacity is via the iOS app on swap; faucet-side fallback is a long-press on the KRAUS air switch defaulting to 5 lb capacity.

Add to the "Front-to-back internal layout" enumeration (currently around line 97) or as a new short subsection:

> **Supply-side pressure transducer**: an inline 1/4" NPT pressure transducer in the CO2 line between the front-panel DERPIPE inlet stack and the WR1110 secondary regulator. Lives alongside the GASHER check valve in the front-of-cold-core electronics shelf vicinity. Signal cable runs to the ESP32 electronics shelf.

### `hardware/bom.md` §4 (CO2 path)

Add line items:

- Pressure transducer, 0–1500 PSI, 1/4" NPT, 0.5–4.5 V output. Amazon Prime SKU TBD (~$15 representative).
- 1/4" NPT 316 SS tee for the CO2 line transducer tap. (Brass acceptable on the dry CO2 side; the cleanliness argument that drives SS on the wetted side does not apply.)
- Optional: HX711 24-bit ADC module + 50 kg load cell, for future Option A gravimetric upgrade. (Hold off until the cylinder-placement surface document commits a cradle geometry.)

### `hardware/wiring/esp32-pinout.mmd`

Add the transducer to the analog-input bus. Pick the next available ADC1 channel that survives the WiFi-radio analog noise constraint (ADC2 channels are unusable while WiFi is active on ESP32).

### `hardware/assembly/internal-plumbing.md` §1 (CO2 path)

Add the tee install step. Note the orientation (transducer body pointing up to keep moisture out of the diaphragm, even though the CO2 side is dry — convention only).

### `hardware/assembly/acceptance-and-burn-in.md`

Add to the test sequence:

- **Step N: Supply-pressure transducer verification.** Cylinder valve closed, primary regulator vented to atmosphere. Transducer reading must read ~0 PSI (within ±10 PSI offset). Open cylinder valve, set primary to 90 PSI. Transducer reads ~830 PSI (cylinder head pressure, upstream of primary). Set primary to 0 PSI (closed). Transducer reads ~0 PSI again. Pass criteria: monotonic response, no zero-offset drift outside ±10 PSI.
- **Step N+1: Per-pour CO2 dose measurement (calibration).** With a kitchen-scale on the test-rig cylinder, record cylinder mass before and after a run of 10 metered 12-oz dispenses (with flavor, full normal sequence including refill cycles). Compute (mass_before − mass_after) / 10 to get per-pour grams. Log to the unit's per-unit calibration file. This is the unit's stored `grams_per_pour` constant; firmware uses it instead of the 6 g default.
- **Step N+2: Lockout simulation.** Close the cylinder valve mid-test. Continue dispensing. Verify that within a few pours the supply-pressure rolling average drops below 100 PSI and the firmware enters lockout, faucet rejects the next dispense command, display shows red icon, app receives push notification. Re-open cylinder valve. Verify lockout clears within ~30 seconds of pressure recovery.

### iOS / Android app

- Add a "CO2 cylinder" card to the home screen (estimated remaining + days estimate + supply-pressure status).
- Add the cylinder-swap reset flow.
- Wire the two notification triggers (20% remaining + cliff).
- Add a "settings → CO2 grace mode" toggle if the design conversation in Part 3 settles on supporting it.

---

## Part 6 — What to measure on every Founder Edition unit

The 6 g/serving working constant is a benchmark, not a measurement. For each of units 001–050 we have the chance to record actual per-pour CO2 mass against actual cylinder runtime. That data is:

- The calibration source for the next batch
- The proof-point for the marketing claim ("a 5 lb cylinder lasts about three months for a typical household")
- The early-warning system for any unit whose carbonation efficiency is degrading (sparge stone partially clogged, vessel leak, refill cycle wasting CO2)

Per-unit data captured at burn-in:
1. `grams_per_pour` measured by scale + cylinder over 10 dispenses
2. Supply-pressure transducer offset and response curve
3. WR1110 setpoint actual (against the transducer reading downstream of the WR1110, if a second transducer is included — optional)

Per-unit data captured by the deployed firmware over time:
1. Daily CO2 consumption (grams)
2. Cylinder-swap events and the calibrated remaining-mass at cliff (drift signal)
3. Lockout events (count, duration, recovery time)

This data feeds back to the per-unit portal (yesterday's `per-unit-portal-gap.md`) and the unit-health diagnostic flow.

---

## Open items / decisions still owed

These are decisions that need a human, not more analysis.

1. **Cylinder size default in marketing copy.** The implicit assumption everywhere in the repo is 5 lb. Confirm and commit. Add a one-line spec to `marketing/target-market.md`'s CO2 paragraph (around line 273): "The appliance ships sized for a 5 lb CGA-320 cylinder; 10 lb is also supported."
2. **Grace mode (still water with flavor on cylinder-out).** Default no. Confirm.
3. **Notification copy and tone.** The 20 % warning tone is the most important; this is the "I respect your time, here's a heads-up" moment. Draft copy belongs in the iOS app PR alongside the cylinder card.
4. **Per-pour dose calibration vs. fleet-default.** Use the per-unit-measured `grams_per_pour` from burn-in, or use a fleet-wide default and update by OTA? Per-unit is more accurate but more operational surface area. Fleet-default is simpler. Recommend: store per-unit at burn-in but also push a fleet-default OTA-updatable fallback; firmware uses the per-unit value when available, fleet-default when not.
5. **Counter reset gesture on the faucet.** Long-press the KRAUS air switch is the placeholder. Whether the same switch can be overloaded for this purpose (vs. requiring the iOS app for the cylinder-swap event) is a UX call dependent on the broader faucet-side interaction inventory, which isn't fully written.
6. **Load-cell future path.** When the enclosure-exterior surface document commits the cylinder cradle, revisit Option A. The transducer + counter combination is good; load cell + transducer is *better* (it gives the smooth gauge without trusting the counter at all). But not on the critical path for the first 10 units.
7. **Whether to surface the cliff-event auto-correction to the customer.** When the cliff fires and the counter shows 40 % remaining, firmware corrects to 0. The customer doesn't see the discrepancy directly. Should the app show "the appliance noticed your cylinder ran out earlier than estimated — we've adjusted future estimates based on the actual lifetime"? Transparency is good; surfacing failures of our own estimates may also be off-brand. Pick one.

---

## Why this matters in target-market terms

From `target-market.md`: "Running out. The moment the fridge is empty and the store isn't convenient. The daily ritual interrupted. This is peak frustration."

A surprise empty CO2 cylinder is exactly that frustration in a different costume. The customer paid $7,500 to never have it again. If we ship without a depletion-warning UX, the very first empty-cylinder event is the moment the product breaks its core promise — and at the Founder Edition scale of person-to-person trust (the "rings of trust" model in the same doc), one such event in unit 003 is heard about in units 008, 012, and 017 before it gets fixed.

The instrumentation cost is $15 BOM and a few hundred lines of firmware. The promise it protects is the entire product. That's the gap, and it should be closed before the first Founder Edition ships.
