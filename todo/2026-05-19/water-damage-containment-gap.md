# Whole-appliance water/syrup containment gap

*Recommendation for follow-up — written 2026-05-19, hourly-todo-filler agent.*

This is a liability gap, not a build-blocker. Unit 001 can run on the bench without it. But the moment Unit 001 sits under a friend's kitchen sink, the appliance has no answer for the failure mode that costs more in real households than any other appliance failure: a slow water leak into the cabinet that nobody notices for hours or days.

The hydrocarbon-leak gap covered earlier today ([leak-detection-coverage-gap](leak-detection-coverage-gap.md)) is the parallel safety story for R-600a. This one is the *liquid* story — water at house pressure on the suction side, water at ~90 PSI on the discharge side, sugary syrup in the reservoirs, and condensate generated wherever the cold core's foam shells fall short. None of it has a catch path. None of it has a firmware response. None of it has a positive shut-off upstream of the leakable joint inventory.

## What I think is wrong

The only liquid-sensing component in the current architecture is the moisture sensor under the Multiplex 19-0897 backflow-preventer vent ([`hardware/future.md:121`](../../hardware/future.md), [`hardware/assembly/enclosure-mechanical.md:58`](../../hardware/assembly/enclosure-mechanical.md)). It is a small printed drip pan sized for the vent termination only, and it observes exactly one failure mode: the backflow preventer's primary check beginning to weep. That sensor's job is described correctly and I am not proposing to change it.

What's missing is everything that pan does **not** catch:

- A loose hose clamp on the JoyTube 3/8" ID silicone suction line (between the FFL38BARB38 swivel and the SeaFlo pump inlet) → leaks at house pressure (60-80 PSI typical, up to 80+ PSI in homes without a PRV) at the pump's natural intake, continuously, until the home's main shutoff is closed.
- A failed NPT joint on the discharge side (MAACFLOW barb-adapter, GASHER check, first PP010822E PTC-to-NPT) → leaks at the SeaFlo's discharge head (up to 100 PSI shutoff) when the pump is active, then drops to vessel pressure (≤ 90 PSI from the WR1110 secondary) for as long as the vessel holds charge.
- A failed PTC ring on any of the four JG PP010822E warm-side/cold-side adapters in the water or CO2 paths → carbonated water + CO2 escape together, foaming, until vessel pressure drops to atmospheric.
- A failed laser weld at the carbonator vessel end-plate-to-tube seam → the PRV handles the pressure side (relief at 125 PSI, which is the safety story covered by the [hydro-test-acceptance-criteria-gap](hydro-test-acceptance-criteria-gap.md) today), but a sub-PRV-trip seep at a weld pinhole still bleeds carbonated water + CO2 into the cabinet for hours before the vessel drains itself.
- Aged peristaltic-pump silicone tubing past its service interval → drips of syrup at the pump head. Sugary, sticky, attracts pests, ferments. Doesn't damage cabinetry in small volumes the way water does, but it is not benign on a six-month cleaning cadence.
- A failed printed flavor reservoir (PETG/PET-CF print, ~1.18 L geometric volume, vented to atmosphere through a filter, not pressurized) → 0.88 L of syrup into the cabinet on whatever cracking-mode failure the print exhibits. The reservoir is layer-line-anisotropic by definition; a single dropped or thermally-shocked print can split along a layer line.
- A condensation event at any uninsulated cold surface — the SS 1/4" NPT bottom-plate outlet stub before its insulation begins, the TAISHER 90° elbow at that stub, the carbonated-water PP1208E bulkhead at the back panel (cold tube enters there, bulkhead body is in cabinet ambient), the CARGEN nitrile foam pipe insulation if a segment is misaligned or undersized at a joint. The dew point in a typical kitchen at 22 °C / 50% RH is **11 °C**; the cold side of these components runs near 2 °C in steady state. Anything cold and bare sweats, persistently, every hour the compressor cycles.

The leak rate ceiling matters because it sets the cabinet-damage timeline. A worst-case open suction-side joint with the customer's tap full-on: ~10 GPM (38 L/min) until the home shutoff is closed. A SeaFlo discharge-side leak with the pump active: 1.3 GPM (4.9 L/min) per the pump nameplate. A vessel-side weep at fitting failure with the pump idle and the vessel at 90 PSI: empirically ~0.1-0.5 GPM until the vessel drains to atmospheric, then 0 until the next refill cycle pumps it back up — which firmware would happily do, repeatedly, because the refill trigger is "tank empty, faucet closed," not "tank empty, faucet closed, and no leak alarm."

Under-sink cabinet floors are typically melamine-laminated particleboard or MDF. Particleboard absorbs water, swells permanently, and delaminates at the seam where the cabinet floor meets the side panels. A 1-2 liter leak puddled overnight on a particleboard floor is a $500-1,500 cabinet-replacement job; a leak that wicks past the cabinet floor onto subfloor or wall framing is a $5,000-50,000 insurance event. The reason home dishwashers and refrigerators have moved toward integrated drain pans + float switches + inlet shut-off solenoids over the past two decades is that this exact failure has dominated whitegoods warranty claims.

The appliance described in `hardware/future.md` has none of those three.

## What an answer looks like, in three layers

These three layers stack. Layer 1 catches the leak; Layer 2 bounds it; Layer 3 escalates it. Each layer is independently useful, but the architecture works best when all three are present. I'll cost each one against a $7,500 Founder Edition price.

### Layer 1: catch pan with leak sensor across the entire appliance floor

A printed pan that forms the bottom face of the enclosure, with a continuous lip ~20-25 mm tall around the inside perimeter. Watertight to the cabinet — any liquid leaving any internal component lands in the pan and stays there. One conductive or capacitive water sensor at the pan's lowest point, wired to an MCP23017 input on the electronics shelf.

Sizing: the pan needs to hold the largest credible single-event volume without overflow. Candidates:

- Full carbonator vessel (~2 L) — released as a slow seep through a failed weld or fitting after PRV verification has confirmed the pressure-relief path. ~2 L.
- Both flavor reservoirs combined (~1.76 L) — printed-shell failure mode.
- "House water on, suction joint open, ten minutes to customer noticing" — at 10 GPM that's 380 L. Out of scope for a passive pan; this is Layer 2's job.

Design pan capacity: **~3 L usable** (slightly more than full vessel + leeway), sized to overflow only in the Layer-2 failure case. At 25 mm lip × the appliance footprint, this is achievable without adding meaningful height. PET-CF prints with a 0.4 mm nozzle and 4-5 perimeter walls are functionally watertight; for belt-and-suspenders, a thin food-safe epoxy or silicone-conformal coating along the seam where the pan meets the side walls eliminates the layer-line porosity question entirely.

The catch pan also subsumes the existing backflow-vent drip pan — one moisture sensor, one structure, the backflow-vent stub just terminates over the same pan. (The current pan-under-vent geometry stays useful as a *location* — the vent should still terminate near the sensor, not at a random part of the pan, so that a slow backflow-preventer weep produces the earliest possible alarm.)

Cost adder: zero hardware BOM increase (print cost only — a printed pan replaces what would otherwise be a flat printed floor). Sensor cost is already in the BOM for the backflow vent. **Net unit cost: ~$0.**

### Layer 2: inlet shut-off solenoid + firmware leak response

A normally-closed 12V solenoid valve on the tap-water inlet, upstream of everything. The valve only opens during an active dispense or refill cycle. When the appliance is idle (which is most of every day), there is no water pressure inside the appliance. A failed joint can't leak what isn't there.

This is the architecture every modern dishwasher and ice-maker-equipped refrigerator uses for the same reason: house water pressure plus a leak path equals an unbounded leak. Removing the pressure when no flow is needed removes the failure mode for the majority of clock-time.

Candidate part: a standard 3/8" or 1/2" appliance inlet solenoid valve (BWUM/Frigidaire-pattern, the same family used on dishwashers/ice makers, $15-25 on Amazon Prime, lead-free brass body, 120V or 12V variants). 12V variant pairs naturally with the existing Mean Well IRM-90-12ST bus and an MCP23017 GPIO → ULN2803A driver pattern that the solenoid manifold already uses (`hardware/future.md` "Power"). 120V variant runs through a third Teyleten relay if the 12V variant isn't sourceable; the 12V path is preferable because it keeps mains off the inlet hardware.

Firmware behavior:

- **Open inlet valve** before issuing a SeaFlo refill cycle. Wait 250-500 ms for line pressure to stabilize at the pump's suction side. Run refill cycle. **Close inlet valve** immediately at refill completion.
- **Refuse to open inlet valve** if the Layer-1 catch-pan sensor is wet, the backflow-preventer vent has weeped within the last N minutes, or the vessel high-level reed never made before low-level cleared (sensor-disagreement fault).
- **Force inlet valve closed** if pan sensor reads wet at any point — independent of which subsystem requested the open.
- **Annunciate the closure.** The customer can dispense whatever is still in the vessel (drains via the cold-side outlet, which has its own check valve and is unaffected), but the next refill won't happen, so the next attempt to pour past the empty point returns nothing. Display + iOS app: "Leak detected — appliance is in safe mode. Open the cabinet, check for water." Sticking with the same "critical alert" iOS entitlement that [leak-detection-coverage-gap](leak-detection-coverage-gap.md) recommended for hydrocarbon leaks; single entitlement covers both alarm classes.

Cost adder: inlet solenoid ($20 retail single-quantity, less at quantity-of-50), one MCP23017 channel (free, plenty of unused pins), one ULN2803A channel (free, both modules have headroom per `hardware/wiring/ac-wiring-schedule.md`), ~6" of 18 AWG wire, a 3/8" MPT × 1/2" NPT or matching adapter between the solenoid outlet and the existing Multiplex 19-0897 inlet (~$3). **Net unit cost: ~$25-30.**

The Multiplex 19-0897 backflow preventer stays where it is, immediately downstream of the inlet solenoid. ASSE 1022 protects the home plumbing from CO2-acidified water backflow — that's its statutory job per `hardware/future.md` §"Carbonation subsystem". The inlet solenoid protects the cabinet from leaks at the Multiplex itself and everything downstream. Different layers, different jobs, both required.

### Layer 3: customer alarm + telemetry

Same shape as the hydrocarbon-leak response from the parallel gap, with two differences:

- **Severity is lower.** Water in the pan is bad but not life-safety. The display message is "Leak detected — safe mode" not "REFRIGERANT LEAK — SHUT OFF CO2 + UNPLUG." Buzzer is present but at a lower volume / less aggressive cadence.
- **Recovery is customer-serviceable** in most cases. Mop the pan, identify the source, tighten or replace the offending joint, dry the sensor, clear the alarm in the app. No SF76E thermal fuse to replace; no service call required for the routine cases. Founder Edition customers get a phone call from Derek to walk them through it, which is exactly the install-consult relationship they paid $7,500 for.

This means the firmware state machine has *two* leak-alarm severities (hydrocarbon = hard-fail, liquid = safe-mode-with-customer-recovery) rather than one. Worth making the distinction explicit in firmware now, before the integrated-firmware work referenced by [integrated-firmware-gap](integrated-firmware-gap.md) lays a single-severity rail.

Cost adder: zero hardware, ~50 lines of firmware on top of whatever the integrated firmware brings in.

## Condensation, separately

The leak-detection layers above also catch condensation, but condensation is a steady-state phenomenon that the customer is going to live with for ten years, not a once-in-a-decade event. Treating it via the catch pan is a backstop, not the solution. The actual solution is:

- **Insulate every cold component that breaks out of the foam shells.** The TAISHER 90° elbow at the cold-side outlet, the short 1/4" NPT stub between the vessel bottom plate and that elbow, the LLDPE riser up through the foam shell exit, and the back-panel PP1208E carbonated-water bulkhead. The CARGEN nitrile pipe insulation BOM line (`bom.md §9`) is sized for the umbilical run but doesn't currently cover these in-cabinet cold-side components. Spec the additional segments.
- **Air-seal the foam-shell exit point for the cold-side riser.** The current shell design routes the cold-side outlet tube through a slot in the inner foam shell; if that slot has any open area to ambient cabinet air, warm humid air convects into the cold core and condenses on the inner shell's outside surface — invisible to the customer, but it slowly waterlogs the foam-pour insulation and degrades R-value over years.
- **Consider a slow-cycle fan or convective vent in the appliance interior.** The condenser fan already pulls cabinet air across the hot side; a few CFM of cross-flow at the cold side end of the enclosure dries any incidental condensate before it accumulates. Cost: ~$3 for a small 12V fan, one more ULN2803A channel.

This is a separate enough body of work that it deserves its own analysis cycle, but I'm flagging it here because the catch-pan + inlet-solenoid architecture above is what *also* catches the condensation case if the insulation work is incomplete or fails in the field.

## Failure modes the catch pan still doesn't address

A few cases the architecture above does not handle, called out so the project owner can decide whether to add layers or accept the risk:

- **Catastrophic above-counter failure** — the faucet body, the under-counter mounting plate, or the umbilical leaking *above* the appliance. Liquid lands on the inside of the cabinet door, the countertop, or runs down the outside of the appliance enclosure without entering the catch pan. The TPU shank gasket (`hardware/printed-parts/faucet/touch-flo-mounting-gasket/`) and the keyhole-plate compression at the countertop are the seals here; their long-term performance is not characterized. Mitigation candidate: a second moisture sensor inside the cabinet near the countertop pass-through, observing the typical drip path. Low cost, separate sensor location.
- **Slow leak that evaporates before reaching the pan** — a fitting weep that evaporates between cycles and never accumulates enough liquid to puddle. The customer sees mineral scaling or corrosion at a fitting six months later; the pan never alarmed. Mitigation candidate: opportunistic visual-inspection checklist in the founder's first-year-anniversary phone call (which doesn't exist yet as a documented practice — separate from but related to [install-consult-playbook-gap](../2026-05-18/install-consult-playbook-gap.md)).
- **Catch-pan sensor failure.** A failed-open ADC reads dry forever; a shorted sensor reads wet constantly. Same failure-mode analysis as the MQ-6 work in [leak-detection-coverage-gap](leak-detection-coverage-gap.md); the right answer is the same self-test-at-boot + baseline-drift architecture used there. One firmware pattern, two sensor channels.
- **Refrigerant-loop coolant pan.** Not relevant — R-600a is a gas and a piercing-valve leak alarms via the MQ-6, not as liquid in a pan. Called out only because someone reading both gaps in sequence might expect symmetry, and the asymmetry is intentional.

## What I'd ask the project owner to decide

In order of decreasing urgency:

1. **Catch pan or no catch pan.** This is the architectural decision. Doesn't block unit-1 build, but does block "unit goes into a kitchen." If yes, the printed enclosure floor needs a redesign — the lip integrates with the side-wall geometry, so this is best done before the next enclosure print cycle (which the [front-panel-cad-gap](front-panel-cad-gap.md) from today says is imminent).
2. **Inlet solenoid yes/no.** Independent decision from #1. Either layer alone is meaningfully better than nothing; together is the architecture I'd recommend. Marginal cost is ~$30 against $7,500.
3. **Firmware alarm-severity model.** Two severities (hydrocarbon hard-fail vs. liquid safe-mode), or one (all-leaks-are-hard-fail). Two is more nuanced and respects the actual hazard distinction; one is simpler. I'd recommend two, but the integrated-firmware track owns this choice and should not be blocked by it.
4. **Customer-facing copy + iOS critical-alert entitlement.** Shared with the hydrocarbon-leak track. Already on the critical-path for one alarm class; adding a second alarm class to the same entitlement adds zero Apple-side review time but does require both copy strings to land before submission.
5. **Condensation insulation work.** Spec the additional CARGEN segments at the cold-side elbow + riser + back-panel bulkhead. Adjacent to the foam-pour gap from today but lower-risk: this is an additive change to an existing BOM line, not a new procedure.

## Files this recommendation should propagate into when actioned

- `hardware/future.md` — add a "Liquid containment + leak response" section near the existing "Backflow vent monitoring" section, framing the catch pan as the architecture-level answer and the existing drip pan as a subset of it.
- `hardware/bom.md` §3 (Water inlet) — add the inlet solenoid line item if Layer 2 is accepted; add the additional CARGEN insulation segments for the cold-side elbow + riser + bulkhead if the condensation work is accepted.
- `hardware/assembly/enclosure-mechanical.md` step 2 — replace "Install the internal drip pan" with "Install the integrated catch pan" or expand it, depending on whether the catch pan is a separate part or integral to the enclosure floor print.
- `hardware/assembly/internal-plumbing.md` step on water inlet — insert inlet-solenoid wiring between the water-inlet bulkhead and the Multiplex 19-0897 if Layer 2 is accepted.
- `hardware/assembly/acceptance-and-burn-in.md` — add a "wet the pan, verify the inlet solenoid closes within N seconds" bench-acceptance step.
- `hardware/wiring/ac-wiring-schedule.md` and DC schedule — add the inlet-solenoid drive run (12V to solenoid coil), reusing the SIG-9 conventions already established for the moisture sensor.
- `hardware/printed-parts/enclosure/` — the pan geometry is a printed-parts deliverable, almost certainly integrated with whatever the next enclosure-floor design becomes.
- `firmware/src/main.cpp` (or its successor in the integrated-firmware work) — implement the two-tier leak-alarm severity model and the inlet-solenoid open-only-when-needed pattern.
- `business/regulatory.md` — append a brief "liquid-leak architecture" note. Not required by any specific standard for an unlisted appliance, but documenting the design intent is useful when the appliance eventually pursues UL/ETL listing (currently deferred per `business/regulatory.md`).
- `business/warranty-and-rma-gap.md` (yesterday) — note that customer-serviceable leak events are the common case, and that the warranty policy should distinguish them from service-required events.

---

*This recommendation is the work of an hourly background agent. The leak-rate numbers cited above (10 GPM house, 1.3 GPM pump, 0.1-0.5 GPM vessel weep) are nameplate or rule-of-thumb figures and should be verified against bench data before they become customer-facing claims. The dew-point calculation (22 °C, 50% RH → 11 °C) is from standard psychrometric tables. The architectural argument — that the appliance currently has no answer for a slow liquid leak, that home appliances in this category have converged on catch-pan-plus-inlet-solenoid for good reason, and that this is the dominant warranty/liability failure mode for under-sink whitegoods — is grounded in the existing repo and in industry practice and should hold up under verification.*
