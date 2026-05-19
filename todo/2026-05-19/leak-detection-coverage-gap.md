# Hydrocarbon leak-detection coverage gap

*Recommendation for follow-up — written 2026-05-19, hourly-todo-filler agent.*

This is a safety-architecture gap, not a build-blocker. The unit-1 build path doesn't need it resolved before first run-up. But it does need to be resolved before any unit lives in a customer's kitchen, and it touches several existing docs that currently assume the architecture is settled when it isn't.

## What I think is wrong

The MQ-6 hydrocarbon sensor is documented in three places — `hardware/cut-parts/compressor-shroud/README.md`, `hardware/assembly/refrigerant-loop.md` "Safety", and `hardware/assembly/acceptance-and-burn-in.md` step 11 — as living **inside the compressor shroud**, with the explanation that this is where the ignition source is, so this is where leak detection belongs.

That reasoning is half right. The shroud's *job* is to contain a flame event around the terminal block + PTC module if one occurs; the sensor inside the shroud is what would tell us a fuel-air mixture had reached the ignition-source zone. Fine.

But that placement assumes the leak originates inside the shroud, or that gas migrates uphill against its density gradient to get there. Neither is the dominant in-service case.

**R-600a is ~2× denser than air** (isobutane MW 58 vs air MW 29; gas density ~2.5 kg/m³ vs 1.2 kg/m³ at room conditions). A slow leak from any joint released into still air sinks, not rises. It pools at the lowest point of the enclosure interior, and (over time, through whatever gaps exist in the enclosure floor and walls) further down into the kitchen cabinet itself.

The actual high-probability leak sites are not in the shroud:

- **Pinch-swage joint at the evap inlet** (`refrigerant-loop.md` step 5) — a hand-formed, copper-on-capillary-tube braze. Highest workmanship variance of any joint in the build.
- **Slip coupling at the evap outlet** (`refrigerant-loop.md` step 4) — sweat × sweat braze, more forgiving than the pinch-swage, but still a hand braze.
- **BPV31 saddle clamp on the compressor process tube** — a permanent service-access tap mentioned in `cold-core` + `refrigerant-loop.md` as the single permanent service-access point. Mechanical seal under a saddle clamp, not a braze. Documented leak-check point in acceptance step 8.
- **BPV31 flare-port cap** — same. Mechanical seal at every service event over the appliance's 10-year design life.
- **Compressor process tube itself** — flexes with mounting-foot vibration over 10 years; the original factory pinch-shut closure does not get re-brazed after the BPV31 is installed.

Three of those five sites — the suction-line coupling, the cap-tube pinch-swage, and the bulk of the evap coil itself — sit at the **back** of the enclosure, against the cold core, on the order of a hand's-width away from the compressor shroud (everything lives inside one ~400–500 mm-wide appliance, so distances are inches, not feet). The two BPV31-related sites sit on top of the compressor body, *outside* the shroud (the BPV31 hangs off the process tube where the tube exits the compressor can, not from inside the shroud's protected zone).

The leak from any of those settles to the bottom of the enclosure interior and pools there. The shroud is open-bottom and sits on the same enclosure floor, so pooled gas can enter the shroud from below — but only after the pool depth reaches whatever standoff exists between the shroud's bottom edge and the floor, and then only as fast as it diffuses up to the MQ-6's mounting height inside the shroud (the sensor isn't flush with the bottom edge; it sits at middle-height where the trimmer + LED + connector all need access). A floor-level sensor catches the same leak at a lower pool depth, which is earlier in real time on a slow leak.

There's a corner case where the in-shroud sensor wins: a leak that originates *inside* the shroud — process tube weep at the can, terminal-seal failure on the hermetic. Those are real but lower-probability than the brazed joints, and the gas would still settle within the shroud volume before escaping out the open bottom, so a sensor at the bottom of the shroud (not at middle-height) would still catch them faster than the current placement.

This is a **coverage gap** (and arguably also a sensor-height gap *within* the shroud), not a sensor-selection gap. The MQ-6 is a fine choice. There is one of it, at the wrong height inside a small box, instead of at the bottom of the enclosure where a dense gas would actually pool.

## Three options for fixing the coverage gap

I'm not recommending one over the others without more thought from the project owner. All three are buildable inside the current parts envelope.

**Option A: Move the single MQ-6 to the cabinet floor / enclosure floor.** Cheapest. Catches the dominant pooling case. Loses the inside-shroud coverage. The argument for keeping the inside-shroud coverage is that an ignition event needs *both* fuel and source co-located, and the sensor's job is to catch the fuel reaching the source — which the open-bottom shroud only sees if gas has filled past the shroud's bottom edge. If you accept that the floor sensor catches the leak event well before that point, the shroud sensor is redundant.

**Option B: Two MQ-6 sensors.** One on the cabinet/enclosure floor (covers the pooling case), one inside the shroud (covers the inside-shroud leak case). Two analog channels on the ESP32 (the chip has plenty). Adds ~$8 in parts and one more wire run. This is the conservative answer if the budget tolerates it.

**Option C: Keep one MQ-6 inside the shroud, add a cheaper supplementary sensor on the floor.** The MiCS-5524 or a generic LPG breakout at the floor handles the bulk gas detection; the MQ-6 stays in the shroud as the ignition-zone sentinel. Mixed-sensor architectures get complicated — different warm-up times, different baseline drift behaviors, different alarm thresholds. Probably not worth the complexity vs. Option B.

My weak preference is **Option B**. Two of the same sensor is the cleanest firmware story (single calibration routine, single threshold, single alarm-handling code path used twice). The marginal cost is trivial against a $7,500 hand-built appliance.

## Five other things that are also undefined

The placement question is the headline gap. While I was reading, I noticed five adjacent things that are also unresolved in the existing docs. They become more urgent once the placement question is settled, because they're all downstream of "we have a working sensor reading; what do we do with it?"

### 1. Alarm threshold — what PPM, expressed in what units?

`refrigerant-loop.md` and `acceptance-and-burn-in.md` both say "any MQ-6 trip is hard-fail." Neither defines what a trip is. The ACEIRMC MQ-6 module (B0978JSCZ8) has a digital output with an onboard trimmer-set threshold *and* an analog output. The threshold the trimmer is set to from the factory is unknown without bench measurement.

R-600a LFL is **1.8 % by volume = 18,000 ppm**. Industry practice for hydrocarbon leak detectors in domestic appliances (UL 60335-2-89 informative annex; mirrored in UL 60335-2-40 for heat pumps) targets alarm at **~10 % of LFL = ~1,800 ppm** — well below the explosive concentration, with margin for sensor drift and air mixing.

Concrete recommendation: spec the alarm threshold as **1,500 ppm equivalent (≈ 8 % LFL)** with a 30-second persistence requirement to ride out transients (cooking-gas ingress from a nearby stove cycle, cleaning-product solvent burst). Calibrate against a known-concentration source at the bench during commissioning. Read the analog output for proportional warning; reserve the digital output as a hardware-redundant trip.

### 2. Sensor-failure behavior — open, short, drift

MQ-6 cells age (heater wears, baseline drifts upward). At end-of-life the sensor can also fail open (no reading) or short (rail reading). Firmware behavior on each:

- **Open input (floating ADC):** treat as failed sensor → degraded-mode alarm to app + buzzer, *do not* shut compressor (a stuck-open sensor isn't a leak; killing refrigeration on a sensor fault creates a different failure mode — the food in the same cabinet doesn't care, but the customer cares a lot when their cold soda goes warm and they don't know why).
- **Rail-high reading (sensor short or saturated):** treat as leak alarm → shut compressor + shut Teyleten relay #2 (whatever drives the diaphragm pump — kills the pour path so the customer doesn't keep using the appliance while it's flagged unsafe) + app + buzzer.
- **Slow baseline drift:** track a 7-day rolling baseline. If the baseline drifts above a sanity ceiling (say, 500 ppm equivalent in clean kitchen air, which would itself indicate a real problem if true), surface a "sensor needs replacement" advisory in the app.

None of this is in the firmware today — `firmware/src/main.cpp` and `firmware/src_config/main.cpp` have no MQ-6 read path at all. Acceptance-test step 11 references the MQ-6, but the integrated firmware referenced by [`integrated-firmware-gap`](integrated-firmware-gap.md) is precisely the place this lives.

### 3. Customer-facing alarm UX

`acceptance-and-burn-in.md` says "any MQ-6 trip is hard-fail" for the factory bench, where the operator is present and the chassis is on a bench. The in-home equivalent is undefined. Proposal:

- **Local appliance:** loud (≥85 dBA at 1 m) intermittent buzzer at the unit, both displays show a full-screen RED "REFRIGERANT LEAK — SHUT OFF CO2 + UNPLUG + OPEN CABINET DOOR" message. Don't try to be polite about it.
- **iOS app:** critical-alert push notification (the iOS "critical alert" entitlement bypasses Do Not Disturb / Silent — requires Apple approval for the entitlement, worth applying for given this is the only critical-alert use case in the app). Same message text.
- **Hardware action:** firmware drops compressor relay, drops pump relay, drops fan relay (the fan is the only ignition source still on if you don't drop it). Solenoid valves all close. Display stays lit on standby power until the customer unplugs.
- **The "you must turn off the CO2 cylinder" instruction is important** — CO2 leaking from the regulator into the cabinet doesn't combust, but it does displace air, which raises the apparent PPM/LFL fraction in a confined cabinet and could push a marginal leak past the threshold. Also it's the only thing the customer can manually do to reduce the appliance's pressurized-gas inventory while they wait for service.

Customer-facing copy is in the marketing/docs side, not the firmware side, but the firmware needs to render *some* text in this state and that text should be reviewed by whoever owns customer comms (probably the founder personally, given target-market.md's "rings of trust" framing).

### 4. Post-event recovery — the SF76E is one-shot

The BOJACK SF76E SEFUSE thermal fuse is a non-resettable, one-shot device. It opens at 77 °C and stays open forever. Once it trips, the appliance is bricked until a service visit replaces the fuse — which lives inside the compressor shroud and requires the shroud to come off, which means access to the refrigerant compartment.

Three things to spell out:

- Customer-facing: "this appliance has a one-shot thermal fuse — if your appliance won't power its compressor after a leak event, do not attempt to power-cycle, contact us for a service swap." That sentence lives in the install doc and the warranty doc and the per-serial portal page.
- Service: what's the swap procedure? Open the shroud, replace the SF76E, close the shroud, restart. Does it require purging the loop? (No — the SF76E is on the AC side, not in the refrigerant path. But it does require physical access through the compressor compartment.) This is a procedure doc that doesn't exist yet — adjacent to `warranty-and-rma-gap.md` from 2026-05-18 but more specific.
- MQ-6 vs SF76E ordering: the MQ-6 trip should fire well before the SF76E thermal trip (1,500 ppm is far below the concentration that would cause a flame event hot enough to reach 77 °C on the fuse). If the SF76E ever trips, it implies the MQ-6 missed — that's a defect investigation, not a routine service event. Worth saying out loud in the SF76E swap procedure.

### 5. Periodic verification — MQ-6 baseline drift over 10 years

MQ-series sensors have a documented 24-hour burn-in for a fresh cell to stabilize, and a multi-year drift profile after that (typical figure: ±20 % over 3 years, depending on environment). The 10-year design life of this appliance is well past any honest "no recalibration needed" claim from the sensor vendor.

Two practical paths:

- **Self-test at boot.** Every cold start, the firmware compares the MQ-6 reading to the expected baseline (saved in NVS from commissioning). If the baseline has drifted more than ±X %, log an advisory but don't block boot. The customer sees a "sensor health: needs attention at next service" indicator in the app. This costs ~30 lines of firmware and zero hardware.
- **Annual replacement.** Treat the MQ-6 as a consumable, replaced at the same service interval as the peristaltic pump silicone tubing. Adds a line to the service kit. Adds a labor step to the annual visit (if there is one — the annual-visit model is itself not yet committed; the install-consult playbook from 2026-05-18 is a different thing).

I lean toward the self-test, with the annual-replacement option held in reserve for unit 1 field data. If the baseline genuinely doesn't drift in normal kitchen ambient over the first year, the annual replacement is overkill.

## What this gap is *not*

A few adjacent things this recommendation deliberately doesn't cover, to keep its scope clean:

- **The argon-purge procedure during brazing.** That's the assembly-time hazard, fully covered by `refrigerant-loop.md` "Safety" and `business/regulatory.md`. Not the same hazard as in-service leak detection.
- **Cabinet ventilation specification.** A real worst-case calculation — "if entire 23 g charge releases into a sealed 0.5 m³ cabinet, what's the PPM?" — needs a separate analysis. (Back-of-envelope: 23 g of isobutane = ~9.5 L of gas at room conditions = ~1.9 % concentration in 0.5 m³, which is just above LFL. That's a real number worth a real document, with the cabinet-volume assumption sourced from the under-sink size distribution in the target market.) Adjacent to this gap but separate work.
- **MQ-6 false positives from other household sources.** Natural gas (methane) — different sensor, but the MQ-6 has some cross-sensitivity. Cleaning products (alcohol, ammonia, propellants). Aerosol cans. The 30-second persistence requirement above handles the burst sources. A steady cooking-gas leak from a stove regulator under a poorly-vented sink is a real false-positive risk; an MQ-6 in the cabinet would alarm on a gas-stove problem, which is a different bug (or arguably a feature). Worth flagging in customer comms.
- **CO2 leak detection.** A separate concern entirely. CO2 isn't flammable; it's an asphyxiation hazard at high concentration in poorly-ventilated spaces. The cylinder lives in the cabinet on a tether. A regulator failure would dump the cylinder's contents — meaningful, but a different sensor (NDIR CO2) and a different alarm calculus. Not in scope for this hydrocarbon-leak gap.

## What I'd ask the project owner to decide

In order of decreasing urgency:

1. **Placement: one sensor or two; floor or shroud.** This is the architectural decision. Options A / B / C above. Doesn't block unit-1 bench work but does block "unit goes into a kitchen."
2. **Alarm threshold + persistence + sensor-failure behavior.** Decide once; codify in firmware. Cheap to do; expensive to retrofit across units in the field.
3. **Customer-facing alarm UX text + critical-alert iOS entitlement.** Founder review required. iOS critical-alert is an Apple-approval process with a multi-week lead time — start that paperwork early.
4. **SF76E service-swap procedure** as part of the existing `warranty-and-rma-gap.md` track. Single page; references this doc.
5. **Periodic verification plan.** Self-test now, annual replacement as a fallback. Defer to unit-1 field data.

## Files this recommendation should propagate into when actioned

- `hardware/cut-parts/compressor-shroud/README.md` — if Option A or B chosen, update the "What's inside vs outside the shroud" table and clarify that the in-shroud MQ-6 is one of two (B) or is being moved out (A).
- `hardware/assembly/refrigerant-loop.md` "Safety" — update the MQ-6 placement description; add the alarm threshold + persistence.
- `hardware/assembly/acceptance-and-burn-in.md` step 11 — update "the MQ-6 sits inside the compressor shroud and reads only the protected zone" to whatever the answer becomes; add bench-calibration to a known concentration to step 7 ("commissioning") or step 11 ("burn-in watch items").
- `hardware/assembly/firmware-and-commissioning.md` step about MQ-6 warm-up — extend with read-path spec, threshold, fail-mode behavior.
- `firmware/src/main.cpp` — actually implement the read path (currently absent).
- `business/regulatory.md` — append a "leak-detection architecture" sub-section under "UL 60335-2-89" reflecting whatever architecture is chosen.
- A new `hardware/assembly/safety-events.md` (or similar) covering: what the customer experiences during a leak alarm, what the appliance does, what service does on the recovery side. Adjacent to `warranty-and-rma-gap.md` from 2026-05-18 but more specific.

---

*This recommendation is the work of an hourly background agent and may be wrong about specific numbers (gas density, LFL margins, drift percentages); the project owner should verify any number cited here against a primary source before committing it to a customer-facing doc or to firmware. The architectural argument — that R-600a settles to the cabinet floor, and that the dominant leak sites are outside the shroud — is grounded in basic physics and the existing repo docs and should hold up under verification.*
