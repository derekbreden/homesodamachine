# Compressor acoustic budget gap

**Date:** 2026-05-19
**Status:** Recommendation. Not yet acted on.
**Distinct from siblings:** No file in 2026-05-18 or 2026-05-19 addresses noise, vibration, or compressor sound. The closest reference in `hardware/future.md` is one paragraph that rejects a metal floor pan "for acoustic reasons" — a passing aside, not an analysis.

---

## The gap, in one sentence

The appliance has no defined noise budget, no documented vibration-isolation strategy beyond the donor compressor's factory rubber grommet feet, and no acceptance criterion for "is this quiet enough to live with under a kitchen sink in the house's loudest room." We are about to ship Founder Edition units to people who will pay $7,500 and then live with whatever this thing sounds like for the next decade.

## Why this matters now, specifically

The product lives under the kitchen sink. The kitchen is the household's most-used room. The compressor cycles ON and OFF on temperature hysteresis several times an hour during active use, indefinitely. The Founder Edition buyer is paying premium money on a thin trust runway — their first 30 days of ownership are dominated by one question, "did I just make a $7,500 mistake?", and the answer is being whispered to them every time the compressor kicks on while they are reading on the couch ten feet away.

`marketing/target-market.md` "The coworker model" is built on the buyer wanting to *show off* the appliance — opening the cabinet door so a friend can see. If the cabinet door is the only thing standing between a buzzing, droning compressor and the dinner conversation, the showing-off moment becomes apologizing for the noise.

`marketing/target-market.md` "Not gadget collectors" warns that we want daily users. A noisy appliance is exactly the appliance that ends up "running only when we need to refill — turn it off otherwise." That kills the temperature setpoint, kills the carbonation, kills the product.

And `hardware/future.md` "Refrigeration subsystem" already lists a 3-minute minimum off-time and a 2 °C hysteresis band — so the compressor stops and starts in audible chunks, with a click of the relay each time. This is not a continuous, fade-into-background HVAC drone. It is a series of discrete acoustic events the customer will register every time.

## What's actually said today

A complete inventory of what the repo currently says about sound, vibration, or acoustic transmission. It is short.

1. **`hardware/future.md` "Other metal candidates considered"** rejects a steel floor pan: "the compressor vibrates at ~60 Hz mechanical plus refrigerant pulsation, and a steel pan amplifies those frequencies at the surface the compressor sits on (mass damping or ribbing can mitigate but adds cost and weight). Printed floor handles drips with attention to first-layer adhesion at the lip-floor joint."
   - This is one paragraph and stops at "printed floor is fine." There is no analysis of whether the *printed* floor transmits to the cabinet bottom, no analysis of resonance in the printed wall panels, no analysis of structure-borne path up through the cold-core support ring → cold core → faucet umbilical → countertop.

2. **`hardware/assembly/enclosure-mechanical.md` step 3** says "don't crush the compressor's M5 grommet feet" when torquing the shroud-to-compressor adapter.
   - This is the *only* mechanical-isolation feature in the build. The compressor's own factory rubber grommet feet are doing 100% of the vibration-isolation work between the compressor and the rest of the appliance.

3. **`hardware/harvested/ice-maker/README.md`** has no dBA rating recorded for either donor compressor and no measurement plan to capture one.

4. **`hardware/assembly/acceptance-and-burn-in.md`** has acceptance criteria for first-fill, CO2 hold, PRV behavior, first dispense temperature, ratio, clean cycle, and burn-in stability. It has nothing about a sound-pressure-level measurement, no microphone reference distance, no cabinet-door-shut-vs-open A/B, no "does the customer hear it from across the kitchen island" check.

5. **`hardware/assembly/finish-pack-ship.md`** has nothing on noise. Once a unit passes burn-in, nobody listens to it again before it leaves the shop.

That is the entire repo's treatment of noise. It is incomplete enough that I have to flag it before more donor variants are folded into the design, because the cost of fixing this scales with how many donor-variant-shaped assumptions get baked in.

## Why the factory grommet feet are not enough

The donor compressor's factory rubber grommet feet are tuned for a *countertop ice maker sitting on a Formica kitchen counter*. That product spec accepts a noise profile because (a) the unit is on top of a counter, not enclosed in a cabinet that resonates, (b) the user can walk away from it, and (c) it cycles less frequently because ice production is bursty not continuous-hold. Our use case differs on all three counts.

Specifically, the factory grommets are likely sized to isolate against a stamped sheet-metal enclosure floor with mass damping. We are bolting the same compressor to a printed PET-CF floor of unknown stiffness and unknown modal response, then asking that printed floor to sit on whatever's at the bottom of someone's under-sink cabinet (3/4" particle board, MDF with a vinyl liner, occasionally a metal pan from a prior leak). The transfer function from compressor → factory grommets → printed enclosure floor → cabinet bottom → cabinet walls → cabinet door has zero datapoints in this repo. It could be excellent. It could be terrible. We literally do not know.

Refrigerant pulsation at the suction line is a separate path — the compressor is connected to the cold core via brazed copper. That copper run terminates at the evaporator coil, wrapped around the carbonator vessel, which is rigidly captured by the inner foam shell. Foam is a poor structural transmitter at low frequency. The carbonated-water outlet line then runs up through the countertop in an insulated tube — that tube is structural-borne path #2 into the customer's countertop. Again no analysis.

And the condenser fan — 12 V DC, harvested from the donor ice maker, running continuously alongside the compressor — is a small whine on top of the compressor drone. Side-to-side airflow geometry per `hardware/future.md` "Enclosure layout" is great thermally but the intake and exhaust grilles are printed slats facing the cabinet side walls 2-4" away. The fan is loud at the grille, which is loud at the cabinet wall, which is loud back into the room.

## Recommended work, in priority order

The deliverable goal is a documented, measurable noise budget the appliance has to meet before it ships, and a design path that hits it.

### 1. Measure the donor ice makers as-shipped, before any teardown decisions get baked

Both donor units (Antarctic Star HZB-12/Q and Frigidaire EFIC117-SS) are already in hand. Before teardown, plug each donor in on a hard kitchen surface and measure:

- Sound pressure level (dBA) at 1 m, A-weighted, slow integration. A phone app (e.g. NIOSH Sound Level Meter on iOS, no calibration claim — used relative only) is sufficient to establish a *relative* baseline between the two donors and against any later prototype. A calibrated meter is nice-to-have, not required, because the budget below is relative to ambient kitchen baseline, not to an ISO spec.
- Sound pressure level at 30 cm directly above the compressor, with the donor cover off — this isolates the compressor itself from the donor's own enclosure resonance.
- Quick frequency-domain look (any phone FFT app, NoiseScore, decent enough) to identify the dominant tone — 60 Hz mechanical, 120 Hz electromagnetic, any high-frequency content from the fan, refrigerant gurgle on startup.

Outcome: two numbers per donor (1 m enclosed, 30 cm bare-compressor) and a one-paragraph description of what each sounds like. **Add these as a "Donor acoustic baseline" section to `hardware/harvested/ice-maker/README.md`.** This is the floor we work up from — the appliance cannot be quieter than the bare donor compressor, only louder.

### 2. Establish a noise budget in `hardware/requirements.md`

Concrete target proposal, to be argued with not adopted blindly:

- **At-counter, cabinet door shut, compressor running, refrigerator-quiet kitchen: ≤ 45 dBA at 1 m.** This is "noticeable if you listen for it, gone if you're talking." A typical residential refrigerator sits at 38-45 dBA. We are competing against that benchmark because the customer's frame of reference is the appliance they already live next to.
- **At-counter, cabinet door shut, compressor cycling ON event: ≤ 5 dBA spike above steady-state.** No "thunk" or relay-snap loud enough to startle someone in the next room.
- **Operating frequency content:** no narrow-band tone more than 10 dB above broadband background — this is the "it has a *whine*" test. A whining tone at 8 kHz is more annoying at 38 dBA than broadband noise at 45 dBA. Targeting peak-to-broadband ratio catches this even when the overall SPL number looks fine.

These are starting points, not gospel. Pick numbers, write them down, then measure against them. Numbers we can argue with are infinitely more useful than no numbers at all.

### 3. Design a vibration-isolation interface at the compressor mounting bosses

The printed enclosure floor today has "compressor-mounting bosses" (per `enclosure-mechanical.md` step 3) that bolt directly to the compressor's M5 grommet feet. Two problems:

- The factory grommets are tuned for the donor enclosure, not ours. We don't know what their compliance is, what their stiffness is, or what frequency they roll off at.
- Even if the grommets are great, the path from grommet-bottom to printed-floor is rigid — bolts pass straight through with no second isolation stage.

Two design moves, cheap:

- **Add a second isolation stage between the compressor's grommet feet and the printed floor:** a Sorbothane or EPDM washer pair stacked on each M5 bolt (one above the floor, one below) so the compressor sits on a two-stage isolation system. Sorbothane is ~$8 for enough material for 50 units. The literature on this is unambiguous for compressors in this size class. The grommet feet handle low-frequency mechanical, the Sorbothane handles high-frequency structure-borne.
- **Decouple the printed floor from the rest of the printed enclosure with a damping gasket at the floor-to-wall seam:** today the floor is a printed integral part of the shell. If the compressor drives the floor at 60 Hz and the floor is rigidly fused to the side walls, the side walls become a speaker. A printed "floor tile" sitting on EPDM strips inside the shell costs us print orientation and a few grams of EPDM — buys us a broken structural path. Not pursued because we don't know we need it yet, but **decide based on measurement #1 above**.

### 4. Address the cold-core → faucet-umbilical structure-borne path

The carbonated-water outlet leaves the cold core at the bottom of the carbonator vessel and runs up through a "short insulated tube" through the countertop to the faucet (`hardware/future.md`, "Enclosure layout" final paragraph). That tube is a structural-borne acoustic path from the compressor zone *into the customer's countertop*. The countertop is a large flat surface that radiates sound efficiently. The faucet sits on the kitchen counter where the user is mixing a drink and the noise reaches their ears at zero attenuation.

The umbilical is currently 3 LLDPE tubes inside a braided sleeve (`hardware/assembly/faucet-and-umbilical.md`). LLDPE is a poor structural transmitter at low frequency — that helps. But the tubes terminate at PP1208E PTC bulkheads at the back panel and at compression fittings at the faucet body, both rigid, both stiff. A small amount of foam strain-relief or a bend-loop in the umbilical between cold core and counterop penetration would break up the structural path.

Test: with the prototype running, place a contact microphone (phone with one of the various contact-mic apps, or an actual piezo disc taped to the input) at the faucet body and at the under-counter-plate gasket. Compare to ambient air pickup. If the contact reading is significantly above the air reading, we have a structural path and the umbilical strain-relief move is justified.

### 5. Tune the firmware cycle algorithm for acoustic, not just thermal, acceptability

`hardware/harvested/ice-maker/README.md` "Firmware obligations" already requires a 3-minute minimum off-time and a hysteresis band. That algorithm currently optimizes for compressor longevity (avoiding short-cycle damage). It doesn't optimize for acoustic comfort.

Two firmware moves worth exploring once the rest is measured:

- **Slow-start the compressor where possible.** Most hermetic compressors at this size have a hard start — no soft-start option. But the condenser fan can ramp from rest to running RPM over 1-2 seconds via PWM. A fan that doesn't snap-start is a fan that doesn't announce the cycle ON event. Cheap firmware change, no hardware cost.
- **Cluster cycles around predictable times.** A compressor that runs in a 10-minute block every 40 minutes is less perceptually annoying than the same compressor switching every 8 minutes for 2 minutes at a time, because the human ear notices the *transition*, not the steady state. Once thermal mass is measured, the cycle band can be widened (e.g. ±3 °C instead of ±2 °C) to lengthen the period at no quality cost — the water temperature is still well within acceptable limits, and acoustic events drop in frequency.

### 6. Add a noise acceptance step to `hardware/assembly/acceptance-and-burn-in.md`

Even without calibrated equipment, the bench should have:

- A phone-app SPL reading at 1 m, cabinet door shut, during burn-in. Logged per-unit. Catches the donor-variant outlier — the one compressor in the batch of 10 that came in 5 dBA hotter than its siblings because of grommet wear, fan bearing, or seasonal manufacturing drift.
- A subjective listen-test: bench operator stands at the would-be cabinet door, eyes closed, for 60 seconds during a compressor cycle ON event. Pass/fail on "is this what I'd accept in my own kitchen?" From the founder, until production ramps and a noise-baseline reference recording exists for comparison.

### 7. Document the customer-side expectation honestly

Whatever the measured noise actually is, write it down in the customer-facing install guide and on the website. "Operating noise: ~42 dBA at 1 m. Quieter than your refrigerator." Or, if it turns out we land at 50 dBA, "Operating noise: ~50 dBA at 1 m. Comparable to a quiet dishwasher. Cycles on and off; not continuous." A buyer who is told the truth and chooses to buy anyway is happy. A buyer who finds out from their kitchen is angry, posts a review, and the brand pays for it forever.

This connects to `marketing/target-market.md` "The purchase decision, once they trust the person" item 4 ("What's the ongoing hassle?") — noise is a hassle attribute the founder is currently not naming. He should name it.

## Why this is worth the founder's time *now*, not later

Two reasons.

**First, the cost of measurement is hours, not days.** Items 1, 2, and 6 above are all phone-app-level work. Item 3 is a $20 Sorbothane order from Amazon Prime. Item 7 is a paragraph on the website. These are not weeks of work. They are an afternoon.

**Second, the cost of *not* measuring scales.** Every donor unit teardown that happens between now and discovery is a teardown that locked in mounting geometry, shroud anchor points, and refrigerant-line routing under the assumption that noise was fine. If at unit 003 it turns out noise is not fine, every prior unit either ships with the problem or comes back for retrofit. Retrofit at Founder Edition pricing destroys margin in a hurry.

The right time to set the noise budget is *before* the first production unit's compressor is bolted down. The donors are in hand. The prototype is on the counter. This is a discoverable answer this week.

## Out of scope for this file

- Recommending a specific dBA target without measuring first. The numbers in §2 are a starting proposal; pick numbers after §1 produces data.
- Recommending a different donor compressor. Both donors are committed and the harvest path is built around them. Acoustic outcome is what we accept from these donors, not a sourcing reopen.
- Recommending UL/ETL noise certification. Not pursuing UL (per `business/regulatory.md`); the relevant standard here is "will the customer keep using it?", not a marked compliance number.
- Soundproofing materials inside the enclosure (mass-loaded vinyl, acoustic foam linings). These add cost and weight and are a third-line move; the first-line moves (isolation interface, structural decoupling, firmware) are higher-leverage and should be tried first.

## Suggested next concrete action

Before any further teardown work on Unit 001, plug both donor ice makers in for 30 minutes each, on a hard kitchen surface, and capture a phone-app SPL reading at 1 m and a 30-second voice-memo recording for each. Append the numbers and the recordings (or links) to `hardware/harvested/ice-maker/README.md` as a new "Acoustic baseline" subsection per unit. That single afternoon establishes the floor everything else gets measured against, and costs nothing.
