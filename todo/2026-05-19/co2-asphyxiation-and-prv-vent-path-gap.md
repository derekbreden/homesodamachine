# CO2 asphyxiation hazard + PRV vent path gap

*Recommendation for follow-up — written 2026-05-19, hourly-todo-filler agent.*

This is a safety-architecture gap that is **distinct from** the hydrocarbon (R-600a) leak gap covered in [leak-detection-coverage-gap.md](leak-detection-coverage-gap.md), which explicitly carved out CO2 as out of scope. CO2 is not flammable; it is an asphyxiant. The hazard physics, the sensor chemistry, and the mitigation architecture are unrelated to the R-600a story and need their own treatment.

Like the hydrocarbon gap, this doesn't block unit-1 bench work, but it does need to be resolved before any unit lives in a customer's kitchen.

## What I think is wrong

Two things are undefined that should be defined, and one assumption is unverified that should be examined:

1. **The PRV (Control Devices SV-125, 125 PSI / 49 SCFM) has no documented discharge path to atmosphere.** The PRV body is installed laterally on top of the carbonator vessel, inside the cold-core foam shell ([`assembly/pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) step 8: "PRV body extends horizontally, fitting within the cylindrical shell's headroom"). The foam shell encloses the cold core. The cold core sits inside the appliance enclosure. The appliance enclosure sits inside the under-sink cabinet. The PRV discharges into the **innermost** of those three nested volumes. No tube, fitting, or routed path takes the discharge from the PRV outlet to outside the appliance, and from outside the appliance to outside the cabinet. If the PRV ever opens, 49 SCFM of CO2 floods into the foam-shell cavity, then leaks out through whatever gaps exist around the PRV pocket and the cold-core penetrations, into the appliance interior, then out of the appliance into the cabinet — entirely passively, and entirely without measurement.
2. **There is no CO2 sensor in the BOM.** The MQ-6 detects hydrocarbons (LPG, isobutane, propane) — that's what it's there for, and per the hydrocarbon gap doc, even that one sensor's placement is wrong. The MQ-6 does **not** detect CO2. CO2 detection requires an NDIR (non-dispersive infrared) sensor; the common hobby-grade options are the SCD30, SCD40/41 (Sensirion), or the MH-Z19B/MH-Z14A. None of those appear anywhere in the repo (`grep -ril "scd30\|scd40\|mh-z19\|ndir" .` returns nothing in `hardware/` or `firmware/`).
3. **The CO2 cylinder lives in the cabinet on a short tether.** The cylinder is the largest pressurized-gas inventory in the system by 2–3 orders of magnitude. A 5 lb CO2 cylinder holds ~2,270 g of CO2 — ~1,230 L of gas at room conditions. A 20 lb cylinder holds ~9,070 g = ~4,900 L. The 90 PSI carbonator headspace, by contrast, holds maybe ~5 L of free gas inventory. The carbonator vessel is the small inventory; the cylinder is the big one. Every safety-architecture document so far has focused on the carbonator. The cylinder is the dominant scenario, sitting in the confined volume of the cabinet, on a hose that the customer connects at install and disconnects at refill.

## Why this matters physically

**CO2 is denser than air.** Molecular weight 44.0 vs air ~29.0. Gas density ~1.84 kg/m³ vs 1.20 kg/m³ at 20 °C. A CO2 leak in still air sinks, displaces the air below it, and pools at the cabinet floor — which is exactly where the customer leans in to retrieve the cylinder, reach a shutoff valve, or service the appliance. (R-600a is similarly heavy and the [hydrocarbon-leak-coverage-gap.md] argument about pooling at the cabinet floor applies here too, with arguably *more* force because the CO2 inventory is so much larger.)

**Asphyxiation thresholds (NIOSH / OSHA):**

- **Normal atmospheric CO2:** ~420 ppm (0.042 %).
- **OSHA PEL (8-hr TWA):** 5,000 ppm (0.5 %).
- **ACGIH STEL (15-min):** 30,000 ppm (3 %).
- **NIOSH IDLH:** 40,000 ppm (4 %). At this level, ~30 minutes of exposure can cause unconsciousness; immediate evacuation is required.
- **70,000 ppm (7 %):** unconsciousness in a few minutes.
- **>100,000 ppm (10 %):** unconsciousness in under a minute, death in minutes.

CO2 is more dangerous than its reputation suggests because the body's CO2 receptors trigger panicked hyperventilation **before** oxygen depletion is felt. Customers in a CO2-rich pocket don't faint quietly — they breathe harder, which accelerates the dose, and *then* they faint.

**Back-of-envelope volume math.** A typical 36"-base under-sink cabinet is roughly 36" W × 24" D × 30" H interior = ~430 L gross. With the appliance footprint (assume ~300 W × 500 D × 600 H mm ≈ 90 L) and the plumbing stack, drain, garbage disposal, and stored cleaning products, the free air volume around the appliance is generously 100–200 L. Call it 150 L for a base case.

The actual leak scenarios:

- **PRV opens fully and continuously.** This only happens if the WR1110 secondary regulator fails open and lets the customer's primary regulator output (typically 70–100 PSI) into the vessel at full flow. The PRV vents at 49 SCFM = 23.1 L/s. That's the *capacity* of the valve; the actual rate is whatever the upstream supply can deliver. A failed-open WR1110 passes whatever the customer's primary regulator setpoint allows — assume 90 PSI of source, and the cylinder is the bottleneck. The flow through a 1/4" NPT regulator orifice at 90 PSI is on the order of 5–15 SCFM, well below the PRV's 49 SCFM relief capacity, which means the PRV opens, throttles, and vents continuously at the supply rate. At 10 SCFM = 4.7 L/s into a 150 L cabinet, the cabinet reaches 4 % CO2 (IDLH) in roughly **6 seconds** of pure displacement, or **5–15 minutes** if you assume realistic mixing with kitchen air through the cabinet door gap. Either way it's a real-time event, not a creeping one.
- **Cylinder valve failure or hose rupture.** A full-bore CO2 cylinder discharge (no regulator throttling) empties a 5 lb cylinder in seconds to a minute depending on the orifice. The cabinet hits and exceeds IDLH essentially instantly. The customer crouched into the cabinet to investigate "what's that sound" is at lethal exposure in under a minute.
- **Slow leak from the CGA-320 primary regulator seal, the WR1110, or any push-to-connect joint in the cabinet-resident gas path.** The customer's nose smells nothing — CO2 is odorless. The cylinder weight changes slowly (replacement happens months apart, so a customer doesn't have a recent baseline). Over a weekend a slow leak can fill a cabinet to STEL or PEL without any sensory warning, and the customer opens the cabinet door Monday morning to put recycling away.

The cabinet-door gap and the appliance's own condenser-fan airflow provide some ventilation. The fan is the more important of the two: it pulls cabinet air through the appliance enclosure for heat rejection, which churns the cabinet volume on a useful timescale. But the fan is only on when the compressor is on, which (after the cabinet reaches setpoint) is a 30–50 % duty cycle. During the fan's *off* phases, the cabinet is effectively still air, and CO2 pools.

(Per [`assembly/refrigerant-loop.md`](../../hardware/assembly/refrigerant-loop.md) §"Safety" and the hydrocarbon-leak gap doc, the appliance interior is non-sealed by design — the condenser fan creates negative pressure that pulls makeup air through every gap, giving slow circulation throughout. That same not-sealed property means cabinet air freely enters the appliance interior. The cabinet *is* the appliance's ventilation plenum, which is fine for thermal management and bad for asphyxiant management.)

## What's covered already that overlaps

To avoid recapitulating what's already addressed elsewhere:

- **Hydrocarbon leak detection (MQ-6 placement, threshold, fail-mode behavior, alarm UX).** Covered in [`leak-detection-coverage-gap.md`](leak-detection-coverage-gap.md). The recommendations there should be **mirrored** for CO2 wherever the same architectural decision applies (sensor placement low because both gases are heavy; persistence requirement to ride out transients; sensor self-test at boot; iOS critical-alert entitlement for alarms; SF76E-equivalent recovery procedure). I won't restate those mechanics. The thresholds, sensors, and chemistry are different; the architecture pattern is the same.
- **CO2 supply ownership / refill UX.** Covered in [`co2-supply-ownership-gap.md`](../2026-05-18/co2-supply-ownership-gap.md) and [`co2-runtime-and-depletion-ux-gap.md`](co2-runtime-and-depletion-ux-gap.md). Those address the operational side of CO2 (refill cadence, supplier relationships, depletion notification). They do not address what happens when the cylinder leaks.
- **Backflow vent monitoring (Multiplex 19-0897 atmospheric vent → drip pan → moisture sensor).** That telltale is specifically for the *water-side* check-valve failure — it detects backfed liquid water or CO2-saturated water exiting via the vent. It is not a CO2-in-cabinet sensor; it is a vent-weep witness. Independent system.
- **Cylinder placement (in the cabinet, beside the appliance, on a tether to the front-panel inlet).** Covered in [`future.md`](../../hardware/future.md) §"Enclosure layout" — but the placement rationale there is ergonomic (customer's line of sight at install / service) and footprint-driven (cabinet door not blocked). The placement has not been evaluated against the in-cabinet asphyxiation scenario, which is a different optimization than ergonomics.

## What this recommendation adds

Three distinct decisions:

### 1. PRV discharge path

The PRV must vent **outside the appliance enclosure**, ideally outside the cabinet, into a place a person isn't standing. The current architecture vents into the foam-shell cavity and lets the gas find its own way out. That's adequate for the carbonator's small free-gas inventory (~5 L) in the case of a one-shot trip, but it's catastrophically wrong in the failed-open-WR1110 case where the PRV vents continuously at the supply rate.

Three options:

**Option A: PRV-outlet tube routed out the back panel.** A 1/4" hose barb threaded into the PRV's outlet port, a length of high-temperature silicone or PTFE tubing routed up through the foam-shell top, across the appliance interior to the back panel, and terminated at a small printed cowl on the back panel that discharges *downward* into the under-cabinet air gap. The cabinet still receives the gas, but the discharge happens at a known location away from where a person would be reaching in.

Pros: simplest, no new penetrations through the kitchen cabinet, no plumbing into a drain. Bad failure case (asphyxiant in cabinet) is somewhat mitigated by directing the discharge below the cabinet door's seal gap, where the heaviest CO2 column can spill out under the cabinet's toe-kick rather than rising into the under-sink working area.

Cons: cabinet still receives the gas. Mitigation depends on cabinet geometry that varies across kitchens.

**Option B: PRV-outlet tube routed through the floor of the cabinet to atmosphere.** A 1/4" tube terminating in a small grommet through the cabinet floor, exiting under the cabinet base (toe-kick area) into the kitchen floor's air space. Adds one penetration to the customer's cabinet, but discharges fully outside the cabinet volume.

Pros: clean separation between the appliance's failure modes and the cabinet's breathing space.

Cons: requires drilling the customer's cabinet floor at install (or pre-supplying a grommeted kit). One more thing the install-consult playbook owns. The discharge still ends up at the floor of the customer's kitchen — which is fine for the small one-shot trip but is itself an asphyxiation risk at the failed-open-WR1110 case if the kitchen is small / poorly ventilated (a galley kitchen with the door closed).

**Option C: PRV-outlet tube routed up the umbilical to atmosphere above the counter.** Adds a fourth tube to the 3-tube umbilical port already documented in [`back-panel/README.md`](../../hardware/printed-parts/enclosure/back-panel/README.md). The discharge would surface at the faucet base or at a small printed vent on the countertop near the faucet — visible, above the counter where airflow is good, and located right where the customer can hear and see the event.

Pros: best safety outcome (CO2 vents above counter into a well-ventilated room volume); customer-visible telltale; same penetration as the existing tube umbilical, no new holes.

Cons: requires extending the umbilical from 3 tubes to 4. Touches the umbilical-port spec, the faucet base spec, and the under-counter routing. Most invasive change.

My weak preference is **Option C** for the worst-case scenario coverage and the visible-telltale property, with **Option A** as the realistic minimum if Option C touches too many surfaces this late in the design. Option B I'd avoid — drilling the customer's cabinet is a per-install variable that the install-consult playbook would rather not own.

### 2. CO2 sensor in the cabinet (or in the appliance interior — see below)

Adding an NDIR CO2 sensor closes the cylinder-leak detection gap. The cylinder is the dominant CO2 inventory and the only way to detect a slow leak is direct measurement.

**Sensor selection.** The three reasonable choices:

- **Sensirion SCD30 / SCD40 / SCD41** — laboratory-grade NDIR + (SCD30) photoacoustic; 400–10,000 ppm range (SCD40), 400–40,000 ppm (SCD41); I²C; ~$25–55 in single quantities. Auto-baseline-calibration mode requires the sensor to see ambient CO2 (~420 ppm) for at least one period per week, which is satisfied any time the cabinet door is open. The SCD41 has the range to detect the IDLH-threshold event (40,000 ppm) directly; the SCD40 saturates at the STEL level (10,000 ppm), which is still a useful alarm point.
- **Sensirion STC31** — thermal-conductivity CO2 sensor, 0–100 % range; intended for industrial / agricultural use; ~$30; better for high-concentration scenarios (the cabinet near a leaking cylinder will pin an NDIR above its scale, while a TC sensor reads cleanly through the saturation event).
- **Winsen MH-Z19C / MH-Z14A** — hobby-grade NDIR; UART or PWM out; 0–10,000 ppm (MH-Z19C), 0–50,000 ppm (MH-Z14A); ~$15–25. Lower precision, longer warm-up, but adequate for the alarm-threshold detection at the IDLH-fraction level.

Concrete recommendation: **SCD41** for the standard scenario (warning at PEL, alarm at STEL), or **MH-Z14A** if the budget for an under-cabinet asphyxiation sensor needs to come in under $20. The 40,000 ppm = IDLH coverage matters; an SCD40 / MH-Z19C saturates below that. If both budgets allow, the cleanest architecture is *two* sensors: a high-precision SCD41 at the cabinet floor for the slow-leak case (sub-PEL detection) and a wide-range MH-Z14A at the same location as a wide-band backup that doesn't saturate during a catastrophic cylinder discharge. That's the same two-sensor philosophy as Option B in the hydrocarbon-leak gap. Cost: ~$55–75 in parts at single quantities.

**Sensor placement.** CO2 is dense and pools at low points. Place the sensor at the **cabinet floor**, not inside the appliance enclosure. The hydrocarbon-leak gap's argument about pooling applies here with even more force because (a) the CO2 inventory is much larger, and (b) the dominant leak source (cylinder) is *also* at the cabinet floor. If the choice is between one sensor on the cabinet floor (next to the cylinder) and one sensor on the appliance floor (inside the enclosure), the cabinet floor is the right answer.

**Alarm thresholds.**

- **2,000 ppm: advisory** (app notification only — "CO2 elevated; check cylinder for slow leak; not an emergency"). This is well below PEL but well above ambient (420 ppm), so it catches the slow-leak case before it becomes a hazard.
- **5,000 ppm = PEL: warning** (local buzzer + app notification — "open cabinet door, check cylinder valve").
- **10,000 ppm = STEL: alarm** (local loud buzzer + iOS critical alert — "leave kitchen; close the cylinder valve only if you can do so quickly").
- **40,000 ppm = IDLH: hard fail** (firmware shuts everything down — compressor relay, pump relay, fan relay, solenoid valves all closed; loud continuous alarm; iOS critical alert).

Persistence requirements as in the hydrocarbon gap: 30 seconds to ride out cooking-CO2 transients (a gas stove cycling next to an undersink intake can briefly push CO2 above ambient).

### 3. Cylinder location, briefly reconsidered

Out of scope for full re-litigation, but: the cylinder-in-cabinet decision was made on ergonomic and footprint grounds in `future.md`. It is the right answer for those criteria. It is the wrong answer for the asphyxiation criterion. The competitive-product equivalent (commercial bar dispensers, soda fountains in restaurants) keeps the CO2 cylinder in a separate ventilated space — often a basement, often a dedicated closet. We can't do that in a home install; the cabinet is the only available space.

The trade-off the customer is implicitly accepting is: "the CO2 cylinder lives in your under-sink cabinet, and the appliance monitors that cabinet for CO2 leaks." That is acceptable if and only if (a) the sensor exists, (b) the alarm path works, and (c) the customer has been told this is the deal. None of those three things is true today. The recommendation is to make all three true rather than to relocate the cylinder.

(A future Shop / Standard / next-generation tier could relocate the cylinder to an attached outdoor enclosure — see [`pie-in-the-sky/shop-edition.md`](../../pie-in-the-sky/shop-edition.md) for the broader "this is bar equipment, not kitchen equipment" architectural alternative. Out of scope for Founder Edition.)

## What this gap is *not*

- **CO2 vs. R-600a sensor cross-talk.** They're different chemistries and different sensors; the NDIR doesn't see hydrocarbons, the MQ-6 doesn't see CO2. Two independent systems. No false-positive interference.
- **CO2 contamination of the water (carbonic acid pH, lead-leaching, ASSE 1022 backflow).** Already covered in [`future.md`](../../hardware/future.md) §"Carbonation subsystem" and [`assembly/internal-plumbing.md`](../../hardware/assembly/internal-plumbing.md). Different concern.
- **The cylinder hydrostatic test interval.** Customer-cylinder regulatory item; the supplier owns it. Not a product-design concern.
- **Compliance / UL 60335 specifically.** The hydrocarbon-leak gap covers UL 60335-2-89 framing. There is no comparable harmonized standard for in-appliance CO2 sensing in a residential dispenser, because most commercial soda dispensers either live in a commercial kitchen with separate gas-room ventilation, or rely on the building's HVAC. The home-soda case is unusual. Worth a half-day on whether the European EN 16129 or similar gas-appliance ventilation requirement bears on a U.S. retail product — out of scope for this recommendation, into scope for [`business/regulatory.md`](../../business/regulatory.md).

## What I'd ask the project owner to decide

In order of decreasing urgency:

1. **PRV discharge path.** Options A / B / C above. The "current" answer (no path) is wrong, and the failed-open-WR1110 scenario is the one that bites if it ever happens. Decide once; codify in the foam-shell and back-panel specs.
2. **CO2 sensor architecture.** Single SCD41 vs. dual SCD41 + MH-Z14A at the cabinet floor. Cheap parts; firmware work mirrors the hydrocarbon-sensor read path (same I²C / UART bus pattern). Doesn't block unit-1 bench, but blocks "unit goes into a kitchen."
3. **Alarm thresholds + persistence + UX text.** Mirrored from the hydrocarbon-leak gap framework; the four-level ladder (advisory / warning / alarm / hard fail) is new and worth founder review.
4. **iOS critical-alert entitlement** — same Apple-approval paperwork as the hydrocarbon-leak gap; ideally the same entitlement covers both alarm types. Worth bundling and starting the entitlement application early.
5. **Customer documentation: "you have a CO2 cylinder in your cabinet, and here's what the appliance does about it."** This is install-doc + per-serial portal + warranty-doc content. Should be honest about the risk, the mitigations, and the customer's role (notice the alarm; open the cabinet door; close the cylinder valve; ventilate the kitchen).

## Files this recommendation should propagate into when actioned

- `hardware/future.md` §"Carbonation subsystem" Port 4 — extend the PRV description with the chosen discharge path. The current "Not ASME UV-stamped; not required because this project is not pursuing UL/ETL listing" remark sets aside the regulatory-stamp question but does not address the architectural question of where the discharged gas goes.
- `hardware/future.md` §"Enclosure layout" / cylinder-placement paragraph — add a sentence acknowledging the CO2-in-cabinet trade-off and pointing at the in-cabinet sensor as the mitigation.
- `hardware/assembly/pressure-vessel.md` step 8 — update the PRV-installation step to install the chosen discharge fitting at the same time the PRV body is installed, so it can't be forgotten on a future build.
- `hardware/printed-parts/cold-core/foam-shell/README.md` — add the PRV-outlet-tube routing as a documented foam-shell penetration with its own slot, alongside the existing slot inventory.
- `hardware/printed-parts/enclosure/back-panel/README.md` (Option A) **or** `hardware/printed-parts/enclosure/back-panel/README.md` + faucet-base spec (Option C) — terminate the PRV vent tube.
- `hardware/bom.md` §10 sensors (or wherever CO2 sensors land) — add the SCD41 (or chosen NDIR), with the wiring to the electronics shelf.
- `hardware/wiring/ac-wiring-schedule.md` — add SIG-X for the CO2 sensor(s); allocate ESP32 pins.
- `hardware/wiring/esp32-pinout.mmd` — claim the I²C bus addresses (SCD41 default 0x62) or the UART pins (MH-Z14A).
- `firmware/src/main.cpp` — implement the read path. Most of the architecture from [the hydrocarbon-leak gap doc's §2 sensor-failure behavior](leak-detection-coverage-gap.md) applies verbatim, with CO2 thresholds instead of hydrocarbon thresholds.
- `hardware/assembly/acceptance-and-burn-in.md` — add a CO2-sensor check to step 11 alongside the MQ-6 check. The bench calibration step is straightforward: SCD41 reads ~420 ppm in clean room air; if the bench reads >700 ppm, the bench itself has a CO2 problem (person breathing close to the sensor) and the bench operator should move and re-test.
- `business/regulatory.md` — append a "CO2 leak architecture" sub-section. Note that this is a self-imposed safety architecture, not a code requirement; UL 60335 in the U.S. residential appliance space does not mandate it for CO2.
- A new `hardware/assembly/safety-events.md` (or update the one proposed in the hydrocarbon-leak gap) — both alarm types should share the same event-handling framework so a future agent doesn't have to read two separate docs to understand what happens when something is leaking.

---

*This recommendation is the work of an hourly background agent. The architectural argument — that CO2 is denser than air, pools at the cabinet floor, and is asphyxiant at concentrations well below visible/audible/olfactory detection — is grounded in basic gas-density physics and NIOSH/OSHA published thresholds. The specific PPM thresholds cited are standard published values but should be verified against the current NIOSH IDLH and OSHA PEL documents before being committed to firmware or customer-facing copy. The sensor part numbers and prices reflect a single-quantity hobbyist-grade survey and should be validated at Founder Edition production quantity before BOM commitment.*
