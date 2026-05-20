# First-pour commissioning gap — the unit ships dry, but no document defines what the appliance does between "plug in" and "first cold soda"

*Recommendation for follow-up — written 2026-05-20, hourly-todo-filler agent (second of the day).*

Distinct from sibling files: this gap is **not** the founder build-hour audit ([`founder-build-hour-audit-gap.md`](founder-build-hour-audit-gap.md), today's first file, which audits production-side labor). It is also distinct from:

- [`2026-05-19/integrated-firmware-gap.md`](../2026-05-19/integrated-firmware-gap.md) — that gap is about the **factory** integrated-build firmware that does not yet exist, oriented at [`hardware/assembly/firmware-and-commissioning.md`](../../hardware/assembly/firmware-and-commissioning.md) and [`acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md), both of which are bench procedures Derek runs before shipping. The present gap is what the **customer** experiences after the box arrives.
- [`2026-05-18/install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) — that gap is the human/conversational structure of the Zoom call. The present gap is what the **appliance itself** does and shows during the call.
- [`2026-05-19/above-counter-ux-gap.md`](../2026-05-19/above-counter-ux-gap.md) — that gap is the general UX of the visible above-counter surfaces over the product's lifetime. The present gap is the narrow first-power-on state machine, which has very different requirements than steady-state UX.
- [`2026-05-19/countertop-faucet-penetration-gap.md`](../2026-05-19/countertop-faucet-penetration-gap.md), [`2026-05-19/co2-cylinder-restraint-gap.md`](../2026-05-19/co2-cylinder-restraint-gap.md), [`2026-05-19/co2-runtime-and-depletion-ux-gap.md`](../2026-05-19/co2-runtime-and-depletion-ux-gap.md), [`2026-05-19/electrical-safety-acceptance-gap.md`](../2026-05-19/electrical-safety-acceptance-gap.md), [`2026-05-19/tap-water-quality-spec-gap.md`](../2026-05-19/tap-water-quality-spec-gap.md) — these cover the **physical** install steps (cut the counter, hang the faucet, restrain the cylinder, ground the chassis, plumb the water). The present gap starts the moment those steps are done and the customer flips the breaker on.

---

## What the gap actually is

[`hardware/assembly/finish-pack-ship.md:53-65`](../../hardware/assembly/finish-pack-ship.md) commits the appliance to ship **dry**: no water in the carbonator, no concentrate in either reservoir, no CO2 in any line, system at atmospheric pressure. The reasons are good — sub-freezing transit, lighter shipping weight, no customer-visible benefit to a wet ship. The Bill of Materials [`hardware/bom.md:254-258`](../../hardware/bom.md) reinforces this: CO2 tank and flavor concentrate are explicitly user-supplied, not included in the box.

That decision is correct, and it is also the source of the gap. The dry-ship decision moves the entire "from cold and empty to first soda" sequence out of the factory bench (where [`acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md) defines it carefully with a bench rig, a stopwatch, a thermocouple, and Derek standing next to it) and into the customer's kitchen — where:

- The appliance is at room temperature (sometimes warmer if it sat in a hot delivery truck, sometimes colder if it sat on a winter porch).
- The carbonator vessel is empty of water.
- Both flavor reservoirs are empty.
- The customer has never seen this appliance before.
- Derek may or may not be on a Zoom call watching ([`install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) Phase B).
- The customer paid $7,500 and expects, at some point soon, to turn the handle and have soda come out.

**There is no document in the repo that defines the state machine the appliance runs through between "plug into wall outlet" and "lever permits a dispense that produces a cold, fully-carbonated drink."** Specifically, none of the following are written down anywhere:

1. **The thermal-pulldown timeline.** How long does the appliance need, from a 22 °C cold start, to bring the carbonator water to dispense temperature (~2 °C target per [`future.md:55`](../../hardware/future.md)) under the harvested ice-maker compressor's nominal cooling capacity? A first-pass thermal calculation (back-of-envelope below) lands at **~50–80 minutes for the water alone**, plus additional time for the surrounding foam and reservoir mass to equilibrate. This number must exist as a calculated and a measured value, with the calculation in one of the assembly docs and the measurement collected at first unit. The number drives every other element of the first-pour story — what the display says, when the dispense interlock releases, how long the install Zoom needs to be, and what the customer is told to expect.

2. **The first-fill sequence for the carbonator vessel.** The SeaFlo pump can push water into an empty vessel quickly (1.3 GPM rated, ~1-2 minutes to fill 1.8 L through the back-pressure of an empty CO2 headspace). But: does the firmware trigger this automatically on first power-on when both reeds read empty? Or does it wait for a customer-initiated "begin commissioning" command? Or does it wait for some safety-interlock condition to be met (CO2 cylinder valve open, water line pressure detected, no leak sensor active)? The integrated firmware does not exist ([`integrated-firmware-gap.md`](../2026-05-19/integrated-firmware-gap.md)), so this is not a code-vs-spec gap — it is a spec gap. **The spec is silent on whether first fill is automatic, manual, or guarded.**

3. **The first-fill sequence for each flavor reservoir.** [`fluid-topology.md`](../../hardware/topology/fluid-topology.md) defines the valve states for hopper-fill (V-A/V-B in the manifold, "Same path as hopper fill"). But what does the customer do — pour the SodaStream concentrate bottle into the funnel and the appliance routes it via gravity through the open hopper-side solenoid into the reservoir? Or is there a pump-assist (Kamoer peristaltic in reverse? No — pumps are forward-only per [`future.md:87`](../../hardware/future.md))? Forward-pump-pull from the open hopper-side valve, into the reservoir? How does the customer know which flavor goes where? How does the appliance know which flavor is being poured (it can't, unless the customer first selects)? What does the user-facing display say at this step? **The procedure exists at the valve-truth-table level but does not exist as a customer-facing sequence.**

4. **The CO2 prime sequence.** With the customer's CGA-320 regulator now connected to the front-panel inlet and the cylinder valve open, CO2 will flow through the WR1110 secondary regulator and into the (empty) vessel headspace as soon as the back-pressure permits. At what point in the sequence does the customer open the cylinder valve? Before water fill? After? Does the firmware require the moisture sensor on the backflow vent to read dry before permitting CO2 admission? Does it require the MQ-6 to clear (no R-600a leak in the compressor compartment)? **None of these interlocks are spec'd as customer-facing sequence events; they only exist as steady-state safety conditions.**

5. **The carbonation equilibration dwell.** Even once water is in the vessel and the CO2 supply is connected, Henry's-law equilibrium between dissolved CO2 and the headspace gas takes time, especially as the water cools from 22 °C → 2 °C through the same window. A pour during equilibration tastes flat. A pour after equilibration is fully carbonated. **There is no defined dwell time at which the appliance considers itself "ready" — no number, no measurement, no interlock condition.**

6. **The first-pour interlock.** When does the appliance permit the customer to turn the faucet lever and get an actually-cold, actually-carbonated drink? The integrated firmware (per the partial spec in [`firmware-and-commissioning.md`](../../hardware/assembly/firmware-and-commissioning.md) and [`acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md)) has no "commissioning lockout" state described — only steady-state dispense behavior and steady-state refill-when-empty hysteresis. **What happens if the customer pulls the lever at minute 5 of a 75-minute pulldown? Does the lever do nothing? Does it pour warm/flat water? Does the display say "wait"? None of this is spec'd.**

7. **The display content during commissioning.** [`future.md:125`](../../hardware/future.md) describes the RP2040 round display as showing "the active flavor's logo" — i.e., steady-state behavior. The Meshnology ESP32-S3 rotary display ([`bom.md:16`](../../hardware/bom.md)) is presumably the config display, but its commissioning-mode UX is not defined. What does the customer see during the 60-90 minute pulldown? A countdown timer? A progress bar? The flavor logo (which would be wrong)? A "PLEASE WAIT" screen? The above-counter-ux-gap touches this but only in a general way; the commissioning-specific UX has its own requirements (e.g., "explain what we're doing and why" — the customer needs reassurance, not just a wait state).

8. **What the install Zoom call covers, in time.** The install-consult-playbook-gap committed Phase B to "the install itself," with a vague Phase C "first-pour debrief." But if the pulldown is 75 minutes, **the install Zoom cannot cover the first pour in a 60-minute slot.** Either the Zoom is two sessions (install at minute 0, debrief at minute 90), or the Zoom ends at install-complete and the customer is left to experience first pour alone with a printed guide, or the consultation is restructured to start the appliance, hand off to the customer for the dishwasher-load equivalent of waiting, and reconnect for debrief. **The install-consult-playbook does not yet address the timing constraint imposed by the cold pulldown.**

---

## Back-of-envelope thermal math (verify with actual measurement on unit 001)

Inputs from the BOM and future.md:
- Carbonator vessel: 5" OD × 0.065" wall × ~6" tall 316 SS round tube + 1/4" plates. Internal diameter ≈ 4.87". Internal length ≈ 5.5" (after end-plate thickness). Volume ≈ π × (4.87/2)² × 5.5 = ~102 in³ = **~1.67 L water at fill**.
- Vessel mass (316 SS, ρ = 8 g/cm³): tube ≈ 0.30 kg, two 1/4" plates × 4.86" dia ≈ 0.30 kg, total ≈ **0.6 kg SS**.
- Foam shells + bonded foil + evaporator coil: minimal during pulldown (foam is the insulator and barely warms; copper coil mass is small).
- Compressor cooling capacity: harvested ice-maker compressor (Frigidaire EFIC117-SS or generic, [`bom.md:77`](../../hardware/bom.md)). These are nominally ~70-100 W cooling capacity at typical evaporator temperatures.

Energy to pull water from 22 °C → 2 °C (ΔT = 20 K):
- Water: 1.67 kg × 4186 J/(kg·K) × 20 K = **140,000 J**.
- SS vessel: 0.6 kg × 500 J/(kg·K) × 20 K = **6,000 J**.
- Total to pull water + vessel: **~146,000 J**.

Time at 80 W net cooling capacity: 146,000 J / 80 W = **1,825 s = ~30 minutes**.

But: the compressor's nominal cooling capacity is measured at a specific evaporator temperature differential, and a custom-coil retrofit around a 5" OD vessel will not reach factory-spec efficiency. Realistic net cooling at vessel-wall temperatures is **probably 50-70 W**. Recompute: 146,000 / 60 = **~40 minutes**.

Add the surrounding insulated mass that pulls down before the vessel can sustain its setpoint: ~0.88 L of concentrate per reservoir × 2 = 1.76 kg, plus reservoir printed walls, plus inner-foam-shell envelope. The reservoirs only need to reach 8-15 °C ([`future.md:73`](../../hardware/future.md)), not 2 °C — but the pulldown from 22 °C → 12 °C still demands ~75,000 J. They are passively chilled by the gradient (not directly evaporator-coupled), so they pull down on a longer time constant than the vessel. **A conservative estimate is ~60-90 minutes from cold start before the first sub-5 °C, fully-carbonated pour is achievable.**

These numbers are wrong in detail. Unit 001 will measure them. But the order of magnitude is the point: **the customer cannot get a cold soda from this appliance in the first hour after plugging it in, and that fact is currently undocumented anywhere a customer or installer would see it.**

---

## Why this matters now

The dry-ship + cold-pulldown timeline collides hard with three commitments the product has already made:

1. **The $7,500 price tag and "turn the handle, soda comes out" promise.** The marketing copy in [`target-market.md:11`](../../marketing/target-market.md) explicitly sells the immediate-dispense experience. A customer who plugs in a $7,500 appliance and gets warm, flat water for the first hour will form a first impression that no later cold-and-fizzy pour fully erases. The first 50 buyers are Ring-1 friends and Ring-2 friends-of-friends per [`target-market.md:162-186`](../../marketing/target-market.md); their first-pour experience is also the founder's social network's first impression of the product.

2. **The Founder Edition install Zoom commitment ([`install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md)).** The Zoom call promises a guided install and a celebratory first pour. If the pulldown is 75 minutes and the Zoom is 60 minutes, the Zoom cannot deliver on the celebratory first pour. The playbook needs to plan around the thermal constraint — either restructure the call into two sessions, or design the first-pour interlock to tolerate a "pour for the camera at minute 60 even though it's only at 6 °C" path with explicit messaging that the next pour will be colder.

3. **The trust gap at Founder Edition pricing ([`target-market.md:256-270`](../../marketing/target-market.md)).** The customer is buying from Derek's face, not a brand. The single most fragile moment in that relationship is the first-pour experience. A bad first pour erodes the personal trust Derek has spent months building, in a way that a brand could absorb but a one-person operation cannot.

The integrated-firmware-gap correctly notes that the factory commissioning firmware does not yet exist. The deeper observation is: **even if Derek writes that firmware exactly to spec, the spec itself does not include a customer-commissioning state machine.** The repo currently treats commissioning as something that ends at the factory burn-in bench. The customer-side commissioning is implicit, undocumented, and load-bearing on every D2C touchpoint between Derek and the buyer.

---

## What "closing the gap" would look like

This is a documentation-and-spec gap, not a hardware gap. Nothing needs to be designed or fabricated. What needs to exist:

### 1. `hardware/assembly/customer-commissioning.md` — the customer-side counterpart to firmware-and-commissioning.md + acceptance-and-burn-in.md

A new document, parallel in structure to the existing factory-side commissioning docs, that defines:

- **Pre-conditions.** What the customer has done before this procedure starts: faucet hung in countertop, water line connected to rear panel, CO2 cylinder connected and tethered, AC plugged in, breaker on. Per the existing per-step install gaps (countertop-faucet-penetration, co2-cylinder-restraint, electrical-safety-acceptance), each of those install steps is the input to this procedure.
- **State machine.** A named-state diagram for the firmware's commissioning behavior. Working enumeration: `POWERED_DRY` (everything connected, nothing yet primed) → `WATER_FILL` (SeaFlo refilling the empty vessel against rising CO2 back-pressure) → `CO2_PRIME` (vessel at low-reed-just-trip, CO2 admitted, headspace pressurizing) → `COLD_PULLDOWN` (compressor on, water below carbonation-useful temperature still falling) → `CARBONATION_DWELL` (water at setpoint, holding for Henry's-law equilibration) → `READY` (dispense interlock released, first pour permitted) → `STEADY_STATE`. Each state has a defined trigger from the previous state, a defined display message, a defined audible cue (if any), and a defined customer-visible cue if the state is stuck.
- **Timeline expectation.** The honest 60-90 minute number, named upfront in the document and on the customer-facing display, with a measured-on-unit-001 update once that measurement exists.
- **First-fill sequence for reservoirs.** Step-by-step what the customer does at the hopper, with the firmware's valve-state response from [`fluid-topology.md`](../../hardware/topology/fluid-topology.md). Either: customer presses a "FILL FLAVOR A" button on the config display, the appliance opens V-A and the hopper-side route, customer pours the SodaStream bottle into the funnel, gravity drains into reservoir, the 4-reed level sensor reports increasing fullness, the customer hears a chime when the reservoir is at "first-fill complete" (say, the second reed), the appliance closes V-A and prompts for flavor B; or some equivalent sequence. The point is to **make the sequence customer-visible, not implicit in the valve truth table**.
- **First-pour interlock policy.** When does the lever permit a dispense, and when does it refuse? A "soft refuse" path (lever moves, no pour, display says "still cooling, ~38 min remaining") is the strong default. A "hard refuse" path (lever physically blocked) requires hardware not in the BOM. A "permit-but-warn" path (pour happens, display says "this first pour will be warmer than spec — your next pour will be colder") is the most permissive and may be the right behavior for the install-Zoom-celebratory-first-pour case at minute 60 even if the spec target is minute 75.
- **Failure paths.** What if the CO2 cylinder is empty (low-pressure read on no-yet-implemented inlet sensor — see [`co2-runtime-and-depletion-ux-gap.md`](../2026-05-19/co2-runtime-and-depletion-ux-gap.md))? What if the water line has zero pressure? What if the MQ-6 flags an R-600a leak during pulldown? What if the moisture sensor on the backflow vent flags wetness within the first 10 minutes? Each of these wants a defined commissioning-time behavior that is **different** from steady-state behavior — for example, an R-600a leak at minute 5 of pulldown is a hard stop and customer-call-Derek event, not a routine "shut down compressor and notify user" event because the customer is unfamiliar with the appliance and is more likely to ignore subtle warnings.

### 2. Add a "first-pour timeline" disclosure to the customer documentation packet

Per [`finish-pack-ship.md:26-109`](../../hardware/assembly/finish-pack-ship.md), the install kit includes a "printed quick-start install guide." That guide currently does not exist as a written artifact in the repo. Whenever it is drafted, it must include — prominently, on the first or second page — an honest statement of the form:

> **Your appliance needs approximately 60 to 90 minutes after first power-on before it can pour a fully cold, fully carbonated drink.** This is the time required to fill the carbonator with water, dissolve CO2 to its working pressure, and chill the water to dispense temperature. The display will show progress. The first pour will be slightly less cold than later pours; this is normal and resolves within the first hour of operation.

This single sentence in the printed guide does more for trust-gap closure than any other commissioning-related artifact. It converts a potential "this is broken" moment into an expected "this is what they told me would happen" moment.

### 3. Integrate the timeline constraint into install-consult-playbook-gap

The install-consult-playbook-gap defined a Phase A / B / C structure that should now be revised to acknowledge the thermal timeline. Either:

- **Option A (two sessions).** Phase A and Phase B happen on the install-day call (~30-45 minutes, focused on plumbing/cylinder/power). Phase C ("first-pour debrief") happens as a separate scheduled call 60-90 minutes later, or the next day, with the appliance fully commissioned by then.
- **Option B (one long session with a break).** A single 90-minute Zoom slot with an explicit "we're going to step away for 45 minutes while the appliance gets cold; here's what you'll see on the display in the meantime; reconnect at the bottom of the hour."
- **Option C (permit-but-warn first pour at minute 60).** Use the soft "permit-but-warn" first-pour interlock so that the celebratory pour happens on the install call even if the appliance is a few degrees warm of spec. Derek explicitly tells the customer this is the case, frames the next-day pour as "now it's really right." This is the most one-call-friendly path but commits the appliance firmware to a "permit-but-warn" mode that needs to be designed deliberately.

The call is Derek's. The constraint that motivates the call is **the appliance's thermal physics, not an engineering preference**, and the install-consult-playbook needs to acknowledge that as a constraint rather than as a soft design choice.

### 4. Measure the actual pulldown time on unit 001 and update the docs

The 60-90 minute estimate is back-of-envelope. Unit 001's acceptance-and-burn-in bench is the cheapest place to measure it accurately: when Derek runs the first chill cycle on unit 001, log the cabinet ambient temperature at the start, log the vessel-wall DS18B20 every 30 seconds, and plot the temperature curve from ambient to setpoint. That single measurement converts the back-of-envelope number into a measured spec, which the printed customer guide and the commissioning state machine display can both reference. The same measurement can be used to validate that the harvested compressor's effective cooling capacity matches the assumption above; a significant deviation in either direction would justify a different first-fill / first-pour architecture (for example, if pulldown is actually 30 minutes, the install-Zoom Option C above becomes trivially easy; if it is 120 minutes, none of the one-call options work and Option A becomes mandatory).

---

## Why this is worth surfacing now, not later

Three reasons it is high-leverage to write the customer-commissioning spec before unit 001 ships, rather than after:

1. **It changes what firmware the integrated-firmware-gap needs to deliver.** The firmware that satisfies factory acceptance is a subset of the firmware that satisfies customer commissioning — the customer-side adds the commissioning state machine, the lockout, the display content, the audible cues, and the timeline-aware interlocks. If the integrated firmware is written to the factory spec only, then a second pass adds the customer-commissioning behaviors after — fine, but the architecture choices made for the factory spec may not accommodate the customer-side cleanly. Writing the customer spec first lets the firmware author design one state machine that handles both.

2. **It changes what the printed quick-start guide needs to say.** Without the 60-90 minute disclosure, the guide promises faster behavior than the appliance can deliver. The dishonest disclosure compounds the trust-gap problem the Founder Edition was specifically designed to solve.

3. **It changes the structure of the install Zoom.** A 60-minute Zoom that ends at install-complete is a different conversation than a 90-minute Zoom that ends at first-pour. The install-consult-playbook can be written either way — but it has to know which timeline applies before it can be a finished playbook rather than a sketch.

The full closure of this gap is one new document (`hardware/assembly/customer-commissioning.md`), one update to the install-consult-playbook spec, one disclosure block in the printed quick-start guide, and one bench measurement on unit 001. None of those are large. All of them are upstream of "customer plugs in their $7,500 appliance and waits an hour wondering if it's broken," and that is the moment the entire Founder Edition story is most likely to fail in a way that cannot be recovered.

---

## What I am *not* recommending

- Not changing the dry-ship decision in [`finish-pack-ship.md`](../../hardware/assembly/finish-pack-ship.md). That decision is correct.
- Not adding a hardware interlock (relay-blocked faucet, electromechanical lever lock) at the dispense path — a firmware soft-refuse is sufficient and avoids new BOM. The above-counter-ux-gap is where any lever-related hardware would land if it is ever justified.
- Not committing to one of the three install-Zoom restructuring options above. That call is Derek's, contingent on the actual measured pulldown number from unit 001 and on the social-energy budget Derek wants to spend per Founder Edition delivery.
- Not designing the printed quick-start guide here — its existence is presupposed by [`finish-pack-ship.md:109`](../../hardware/assembly/finish-pack-ship.md) but its content has its own (un-filed) gap. This recommendation only specifies one sentence the guide must contain.
- Not asking unit 001 to ship until the customer-commissioning spec exists. Unit 001 is a bench unit ([`hardware/handwork.md`](../../hardware/handwork.md) treats it that way); the customer-commissioning spec is needed before unit 002 or 003 lands in a friend's kitchen, not before unit 001 runs on Derek's bench. The measurement on unit 001 is in fact one of the inputs to writing the spec.

---

## File map for whoever picks this up

To close this gap, the agent or human would touch (or create):

- **Create:** `hardware/assembly/customer-commissioning.md` — the new document described above. Sibling to [`firmware-and-commissioning.md`](../../hardware/assembly/firmware-and-commissioning.md) and [`acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md), referenced by [`finish-pack-ship.md`](../../hardware/assembly/finish-pack-ship.md) as the procedure the printed quick-start guide is anchored to.
- **Update:** [`finish-pack-ship.md`](../../hardware/assembly/finish-pack-ship.md) — add a reference to the new doc; mention the quick-start guide's pulldown-time disclosure as a required content item.
- **Update:** [`integrated-firmware-gap.md`](../2026-05-19/integrated-firmware-gap.md) (when that gap is being closed, not now) — expand the firmware spec to include the commissioning state machine and the soft-refuse dispense interlock.
- **Update:** [`install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) (when that playbook is being drafted) — adopt one of Options A / B / C above and design the call structure around the measured pulldown time.
- **Update:** `hardware/handwork.md` and the unit-001 acceptance log — add the "log vessel-wall temperature every 30 seconds during first pulldown" measurement task.
- **Update:** [`above-counter-ux-gap.md`](../2026-05-19/above-counter-ux-gap.md) (when the above-counter UX doc is drafted) — define the commissioning-mode display content for both the RP2040 round display and the ESP32-S3 config display, distinct from the steady-state flavor-logo content.

No code changes. No hardware changes. No BOM additions. The cost of closing this gap is the time to write one document, measure one curve on unit 001, and weave the result into the four sibling gap-files when they are drafted.
