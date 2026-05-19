# Dispense sync — the DIGITEN flow sensor has no install location, and the start/stop latency that defines the 1:20 ratio is undefined

**Author:** hourly agent, 2026-05-19 (ninth of the day)

## What I picked and why

I am the ninth hourly agent today. The eight earlier files cover upstream supply (concentrate, CO2, trademarks), build process (foam pour, hydro test, firmware bring-up, leak detection), and physical packaging (front panel CAD). Nobody has looked at the **moment the user actually pulls the lever** — the 5-second window where the product is literally the product.

The marketing promise is "turn the handle, soda comes out." `target-market.md` says it ten different ways: cold, fully carbonated, real Diet Mountain Dew, on demand. `future.md` describes how the water gets cold, how it stays carbonated, how it gets to the faucet, how the lever opens. What it does **not** describe is how the flavor concentrate gets injected at the right ratio, starting at the right moment, and stopping at the right moment, every time the user pulls the lever.

There is exactly one sensor in the system that can possibly drive that loop — the DIGITEN G3/8" Hall-effect flow meter on SIG-4. It is in the BOM, it is wired through the umbilical, and the acceptance test in [`hardware/assembly/acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md) step 5 explicitly says "firmware reads the DIGITEN flow sensor and the active flavor selector." Take the DIGITEN out and the firmware has no way to know the lever is open: the Westbrass Touch-Flo poppet is purely mechanical and emits no electrical signal, and the KRAUS air switch is the flavor-select button, not the lever.

So the DIGITEN is load-bearing. And it has unresolved problems in three different layers that nobody has named.

---

## Gap 1 — The DIGITEN has no documented physical install location

I grepped every doc under `hardware/`. The flow sensor's location is mentioned exactly once in [`hardware/assembly/wiring.md`](../../hardware/assembly/wiring.md) line 92:

> Flow meter sits in the post-faucet line on the under-counter side; cable routes through the cabinet up the umbilical alongside SIG-5 and the Cat6 trunk.

"Post-faucet" is mechanically incoherent. The Westbrass body's downstream side is a 12" 1/4" SS center spout that ends in the user's glass at atmospheric pressure. There is no plumbed line downstream of the faucet to put a meter in.

What the author probably meant is "in the carbonated-water supply line, between the cold-core outlet and the faucet body's upstream compression port." That is the only place a flow meter mechanically belongs. But:

- [`hardware/assembly/faucet-and-umbilical.md`](../../hardware/assembly/faucet-and-umbilical.md) walks through the entire blue-tube run from rear-panel bulkhead → through the appliance → up the umbilical → into the Westbrass body's upstream compression port. **The DIGITEN does not appear anywhere in that walk.**
- [`hardware/assembly/cold-core.md`](../../hardware/assembly/cold-core.md) and [`hardware/assembly/pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) don't mount it either.
- [`hardware/assembly/internal-plumbing.md`](../../hardware/assembly/internal-plumbing.md) is the most likely home — should be checked, and if it doesn't put the DIGITEN somewhere, it should.

This is not a small omission. The DIGITEN has G3/8" female threads. The carbonated-water line is 1/4" OD LLDPE through John Guest PTC fittings. There is no adapter in `bom.md` that bridges G3/8" → 1/4" PTC, in either direction. The sensor body is a ~50 mm plastic cube; wherever it goes inside the appliance or under the counter, it eats space and has to mount somehow.

**Recommended action.** Pick one of these and commit it in writing:

1. **Inline in the chilled supply, inside the appliance.** Lives between the vessel's bottom-plate outlet and the rear-panel umbilical bulkhead. Pros: short cable run to the electronics shelf; sees the full 90 PSI line pressure (good for CO2 retention on the impeller — see Gap 3); thermal mass of the cold-core wraps around it. Cons: needs G3/8" → 1/4" NPT or PTC adapters; the cold-core foam pour has to accommodate a bulky non-coil-shaped object; another bulky fitting in an already-crowded inside-the-foam zone.
2. **Inline in the chilled supply, above the counter, behind the printed touch-flo shell.** Pros: keeps the appliance plumbing simple. Cons: under the kitchen sink countertop you have ~3-4" of vertical clearance between countertop bottom and the under-counter plate; the sensor is bigger than that; cable routing to the shelf goes through the umbilical and bloats it.
3. **Inline at the rear panel, in the warm side just downstream of the vessel.** Pros: easy access for service. Cons: warm-side carbonated water at 90 PSI breaks out CO2 against the impeller (Gap 3); requires extending the chilled run via an extra unfoamed segment.
4. **Replace the flow meter with a non-flow-based lever sensor.** Microswitch or hall sensor on the Westbrass body sensing lever position directly. Eliminates the install problem and the carbonic-acid-on-plastic problem and the CO2-breakout problem, but loses real-time volume measurement (Gap 2 still has to be solved differently).

Whichever choice gets made, it lands as a procedure step in [`internal-plumbing.md`](../../hardware/assembly/internal-plumbing.md) (or `faucet-and-umbilical.md` for option 2), with the adapter SKUs added to `bom.md` §3 or §9.

---

## Gap 2 — The dispense control loop is undefined; start latency and end overrun are unaddressed

Assume Gap 1 gets solved and the DIGITEN is correctly installed and reading pulses. The firmware then needs to translate "flow detected" into "the right amount of concentrate, at the right moment." The 1:20 ratio (~17 mL concentrate per 12 oz pour) is documented as a constant. Nothing else about the control loop is.

The Westbrass Touch-Flo is spring-return: the user holds the lever for whatever duration they want, then releases. Pour duration is user-controlled and varies — a 3-oz top-off on existing ice is ~1 second, a fresh 16-oz glass is ~6-8 seconds. The dispense loop has to handle the full range.

**Sub-gap 2a — Start latency.** From lever-open to first DIGITEN pulse is bounded by the impeller's spin-up at the threshold flow rate (call it ~50 ms). Then the firmware ISR fires, recognizes "this is a real pour, not noise," and asserts the peristaltic-pump GPIO. The pump (Kamoer KPHM400) spins up. The concentrate slug travels down 12" of 1/8" SS tube before emerging at the flanking spout. A rough estimate at typical Kamoer speeds is 200-500 ms total latency from lever-open to first concentrate drop hitting the glass.

During that window, **water is dispensing without concentrate**. The first sip is flat soda water, not Diet Mountain Dew. For a 1-second top-off pour, the whole pour might be unflavored.

**Sub-gap 2b — End overrun.** Lever release: water stops in ~50 ms (poppet snaps closed). DIGITEN sees pulses stop. Firmware kills the pump GPIO. But the pump's silicone tube has concentrate-under-spring-pressure, the SS spout is full of concentrate that hasn't dripped out yet, and the user has already pulled the glass away. **Concentrate continues to drip into the sink for 1-2 seconds after the glass is gone.**

That's three failure modes in one window: flat first sip, missing concentrate on top-offs, ongoing drip on the sink basin. Any of these reads as "this product is broken." A SodaStream pours a stable mixed stream from drop one to drop last; the bar to clear is set there.

**Sub-gap 2c — Ratio integrity on partial pours.** If the firmware uses an "every N flow pulses, deliver M pump steps" event-driven loop (the standard approach in commercial post-mix dispensers), ratio is preserved across pour lengths in steady state but the start-latency and end-overrun above still corrupt the first and last fractions. If firmware uses "open-loop pump at constant rate while flow detected," ratio drifts whenever water flow rate drifts (CO2 break-out is the main cause of drift).

**Recommended action.** Before unit 1 ships, draft a `dispense-control-loop.md` in `firmware/` or under `assembly/` that pins down:

1. **Start-of-pour pre-charge strategy.** Probably: maintain a primed slug of concentrate within ~3 mm of the spout tip (already done — the lines stay primed and valve-locked per the marketing copy). On first DIGITEN pulse, fire a small open-loop pump impulse to push the priming-slug-plus-one-pulse-worth out into the stream. Then enter the event-driven loop for the rest of the pour. Net effect: drop one of concentrate lands within ~80 ms of drop one of water.
2. **End-of-pour wind-down strategy.** On DIGITEN-pulses-stopped, run the pump in reverse for ~50 ms to retract the priming slug back to the spout tip, leaving the tip charged but not dripping. (Forward-only pump direction is documented in `future.md` "Flavor subsystem" — this may be the right place to relax that rule, or to add a small head-retraction solenoid, or to accept a small amount of post-pour drip into a captive drip ring.)
3. **The event-driven ratio loop.** Pulses-per-mL on the DIGITEN, steps-per-mL on the Kamoer, integer-quotient relationship. Bench-measured per unit during commissioning per the open item in [`firmware-and-commissioning.md`](../../hardware/assembly/firmware-and-commissioning.md) §188 item 3.
4. **What to do when DIGITEN pulses go noisy.** See Gap 3 — define a debounce / pulse-count-sanity rule so a spurious bubble-on-impeller pulse doesn't trigger a phantom concentrate dose.

---

## Gap 3 — The DIGITEN's compatibility with chilled carbonated water at 90 PSI is unverified

DIGITEN G3/8" Hall-effect flow sensors are spec'd for **cold-water plumbing**: typically 0-60 °C, 0.3-1.75 MPa, clean potable water. Our service condition is:

- ~2 °C (within spec for low temp)
- 90 PSI (~0.62 MPa, within spec)
- **pH ~3.5-4 carbonic acid** (not in any normal cold-water spec; affects the impeller bearing material and the polypropylene body over multi-year service)
- **CO2-saturated, near the breakout threshold.** Henry's-law equilibrium at 2 °C and 90 PSI holds ~7-8 g/L dissolved CO2. The instant the water passes through any pressure drop — a fitting restriction, the impeller blades themselves — CO2 will start to come out of solution as bubbles, on the impeller. That's a Hall-effect sensor's worst input: bubbles cross the magnetic-field path with the same signature as a blade.

The first time anyone tests this on the bench, the failure mode is likely "DIGITEN reports flow even when the lever is closed" (CO2 bleed-off through micro-leaks at the upstream check valve creates intermittent bubbles past the impeller) or "DIGITEN under-reports during an active pour" (foam on the impeller stalls counts).

**Recommended action.** Bench-test the DIGITEN under realistic service conditions *before* committing it to the integrated build. Hook up the prototype's Lillium-fed plumbing with the DIGITEN inline in the chilled supply line at 80-90 PSI; run 10 lever-cycles; verify (a) zero phantom pulses with the lever closed and the system idle for 5+ minutes, (b) pulse-count repeatability within ±2% across the 10 pours, (c) no foam buildup on the impeller after the bench session.

If the DIGITEN fails any of these, the fallback options are:
- A different flow-sensing technology that doesn't care about bubbles — turbine flow meter with magnetic pickup (expensive), ultrasonic flow sensor (food-grade options are ~$80+), or vortex/Karman flow meter (rare in this size).
- The "skip the flow sensor entirely" path from Gap 1 option 4 — a microswitch on the Westbrass lever, with a fixed-rate open-loop concentrate pump calibrated against the faucet's repeatable volumetric output (which is fixed by valve geometry + upstream pressure).

This last option is appealing enough that it deserves an explicit decision-point write-up before more time is spent trying to make a Hall-effect flow sensor work in carbonated service. The Westbrass body is geometrically fixed; the WR1110 holds 90 PSI; the only variable is lever-hold-duration, which a microswitch reads natively. A constant pump rate × constant water flow rate = constant ratio, no flow sensor needed.

---

## Why this matters now (not later)

This sits squarely on the critical path for ring-1 ship per the target market doc. The first 10 units go to friends-of-friends; the success criterion is "units in homes, used daily, generating real-world data." The ones I know about:

- Friend pulls lever for 1-second top-off → gets unflavored soda water → tells founder "is it supposed to be like that?"
- Friend leaves an empty glass under the spout after a pour → small puddle of Diet Mountain Dew syrup in the sink basin → "it's leaking"
- Friend takes a 20-oz pour → ratio drifts because the DIGITEN got bubble-confused at second 6 → "this one tastes different from the last one"

All three are first-week observations. All three would land in the ring-1 feedback that the rings model exists to harvest. All three are preventable if the dispense control loop gets designed before the first unit goes out — not discovered by the first ring-1 customer.

The other todos today (foam pour, hydro test, firmware bring-up, leak detection) address whether the appliance survives long enough to do its job. This one addresses whether the job is done well when the appliance is working.

---

## Concrete deliverables

1. `hardware/assembly/internal-plumbing.md` or `faucet-and-umbilical.md` — add the DIGITEN's exact physical location, the G3/8" → 1/4" adapter SKUs, and where the foam pour has to be relieved to accommodate the sensor body if option 1 is chosen. Add the adapter SKUs to `bom.md`.
2. New doc: `firmware/dispense-control-loop.md` (or equivalent under `hardware/assembly/`) — pre-charge strategy, wind-down strategy, event-driven ratio loop, noise-rejection rule on the DIGITEN pulse train. Cross-reference from `requirements.md` §1.
3. Bench test the DIGITEN under chilled + 90 PSI + carbonated + cycled conditions, with the prototype hardware that already exists. Write the result up as `hardware/component-tests/digiten-carbonated-service.md` (or similar). One afternoon's work; resolves the largest single technical risk on this critical path.
4. If the bench test fails: write the lever-microswitch alternative as a one-page decision doc, with sketch of the mount and the firmware control-loop change. Decide between the two paths before the unit-1 internal-plumbing assembly step starts.

Total estimated effort: half a day for the bench test, half a day for the docs, one day for the lever-microswitch decision and prototype if it comes to that. Cheap insurance against the first ring-1 customer being the one who discovers the unflavored-first-sip problem.
