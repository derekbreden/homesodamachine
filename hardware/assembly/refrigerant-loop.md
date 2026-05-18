# Refrigerant Loop

The production procedure for converting a donor countertop ice maker into the appliance's refrigeration loop — from vent of the factory R-600a charge, through coil wind around the carbonator vessel, to final mass-metered recharge. The most safety-critical procedure in the build: the loop is open to a flammable hydrocarbon for several steps, and the argon purge during brazing is load-bearing.

Design intent and component rationale live in [`../future.md`](../future.md) "Refrigeration subsystem". Donor-component teardown notes (compressor, condenser, capillary tube, drier, hot-gas bypass) live in [`../harvested/ice-maker/README.md`](../harvested/ice-maker/README.md). Assembly-time argon-purge safety is documented at [`../../business/regulatory.md`](../../business/regulatory.md) "Assembly-time safety — argon purge during brazing". This document is the repeatable production procedure that ties them together.

## Scope

This is a single-session integration procedure: bring a finished cold core and a donor ice maker together at one workspace, open the donor's refrigerant loop, braze the cold core's coil stubs into the donor's loop, vacuum, charge, run up. Half a day of work end-to-end. All multi-day prep work (coil winding, foam pour) happens upstream in [`cold-core.md`](cold-core.md) before this session begins.

In: donor ice maker (verified topology in [`../harvested/ice-maker/README.md`](../harvested/ice-maker/README.md)); a finished cold core (output of [`cold-core.md`](cold-core.md) — wound evaporator coil bonded around the vessel, coil inlet/outlet stubs ~2 ft each protruding through the foam-shell's copper-plug exits, foam pour fully cured); R-600a refrigerant; argon from the welder cylinder.

Out: a closed and brazed refrigerant loop, vacuum-tight, charged within ±1 g of target mass, with the cold core's evaporator coil now brazed into the donor's refrigeration cycle. The compressor runs on its first run-up and the suction line drops cold.

Not in scope: cold-core assembly — coil winding, foam pour — all in [`cold-core.md`](cold-core.md); electronics-shelf control wiring, AC distribution, compressor shroud install (its own spec at [`../cut-parts/compressor-shroud/README.md`](../cut-parts/compressor-shroud/README.md)).

## Safety

R-600a (isobutane) is flammable, LFL ~1.8 % in air. EPA Section 608 carves natural refrigerants out of the venting prohibition, so no technician certification is legally required ([`../../business/regulatory.md`](../../business/regulatory.md)). The gas doesn't care about the regulatory carveout. Two distinct hazards apply to this procedure:

**Hazard A — Vent the factory charge before applying any flame.** Heating a pressurized R-600a circuit with a torch is the textbook flash-fire scenario. The charge must be vented and the loop allowed to decompress to atmospheric before any cut, braze, or torch step.

**Hazard B — Residual hydrocarbon at the braze.** After venting, residual R-600a remains dissolved in the compressor oil and pooled in low points of the tubing. When a torch is applied to copper near an oil-soaked compressor pocket, the flame front pulls residual hydrocarbon into itself. Mitigation, load-bearing for this procedure: flow low-pressure argon (a few psi, *flowing*, not static) through the open loop during the entire loop-open period, sweeping residual fuel out ahead of the heat. The same continuous flow also serves as the dry inert blanket that preserves the factory drier's desiccant during the loop-open period (see step 3) — one regimen satisfies both requirements. The existing welder-side argon cylinder is the source.

The in-service hazard — a refrigerant leak post-build into a sealed compartment that contains an ignition source — is owned elsewhere: the compressor shroud isolates the highest-temperature surface in the system, and the AC switching relay is deliberately placed *outside* the shroud so its switching arc isn't co-located with the protected zone. See [`../cut-parts/compressor-shroud/README.md`](../cut-parts/compressor-shroud/README.md). The shroud also carries a hardware-only backstop: a BOJACK SF76E SEFUSE thermal fuse (77 °C, in series with the AC primary feeding the compressor) plus an ACEIRMC MQ-6 LPG/iso-butane sensor inside the shroud — both ON-ORDER per [`../purchases.md`](../purchases.md) §6. Thermal fuse + gas sensor backstop the soft (firmware) cutoffs so a controller failure can't keep the compressor energized through a thermal or leak event.

## Inputs per appliance

Per-unit BOM lives in [`../bom.md`](../bom.md) §5 (refrigeration). The table below is the procedure-level summary; bom.md is the source of truth for per-unit allocation and cost. Status (ACQUIRED / ON-ORDER) for every item lives in [`../purchases.md`](../purchases.md) §6.

| Item | Source / spec | Notes |
|---|---|---|
| Donor ice maker | Generic B0F42MT8JX or Frigidaire EFIC117-SS B07PCZKG94 | Both verified topology |
| Finished cold core | Output of [`cold-core.md`](cold-core.md) | Wound coil bonded to vessel, foam-poured, coil stubs protruding ~2 ft through foam-shell copper-plug exits |
| Drier (spare / contingency only) | Supco SUD8358 + Supco D111 | The factory drier stays in service (see step 3 + harvested README "Filter-drier"); SUD8358 and D111 kept on the shelf as spares for any future loop-open service that requires replacement. Not consumed in the production procedure. |
| R-600a refrigerant | Enviro-Safe B0CGG1WH1N (3-pack + brass charging gauge) | ~40 g per system, mass-metered; one 3-can pack covers ~12 recharges |
| Supco BPV31 bullet-piercing valve | B00DM8J3MI | Single permanent service-access point for the life of the appliance — taps the compressor process tube to vent factory R-600a (step 2), feeds argon during the entire loop-open period (step 3 onward), and serves as the manifold connection for vacuum (step 6) + recharge (step 7). Clamped permanently. |
| BCuP-5 silver brazing alloy, 15 % Ag, 1/16" × 1 troy oz | B0DQ3ZMHK7 | Phosphorus-bearing self-fluxing filler for copper-to-copper joints; ~10 g per build, ~3 builds per rod |
| 3M Scotch-Brite Maroon hand pads | B07CGPCTHT | Abrasive prep on 1/4" ACR copper OD + fitting sockets before flux + braze; ~2 of 20 pads per build |
| Argon | Welder cylinder + Uniweld RHP400 brazing-purge regulator | Continuous low-pressure flow through the loop during the entire loop-open period (step 3 through step 6); no new cylinder needed |
| BOJACK SF76E 77 °C SEFUSE thermal fuse + ACEIRMC MQ-6 LPG sensor module | B07Y61YTTK + B0978JSCZ8 | Hardware-only fire-safety backstops installed inside the compressor shroud (see Safety section above) |

Tooling — all committed in [`../purchases.md`](../purchases.md) §6 (refrigeration) and §1 (argon side), ACQUIRED unless noted:

- **Piercing valve** for venting the factory charge: Supco BPV31 bullet-piercing valve
- **Cap-tube cutter** at the process-tube junction: Mastercool 70025
- **Tubing cutter, flaring tool:** RIDGID 31622 Model 150 + RIDGID 23332 Model 345
- **Tube bender + straightener** for the 1/4" ACR evaporator coil: Klein Tools 51006 3-in-1 bender + Wisscool 1/4" handheld straightener
- **Coil-to-cap-tube join:** Knipex 86 01 180 Pliers Wrench (7.25", smooth parallel-jaw) — pinch-swages 1/4" ACR copper inlet down onto 0.031" capillary tube via progressive 60° rotation collapse. No reducer fitting required.
- **Coil-to-suction-line join:** HVAC 1/4" OD copper slip coupling (ACR-grade, sweat × sweat) joins coil outlet to factory suction line, both 1/4" OD.
- **Vacuum pump + gauges:** Orion Motor Tech 4 CFM 1/3 HP single-stage vacuum pump (150 µ ultimate) + Orion Motor Tech HVAC A/C manifold gauge set, 1/4" SAE.
- **Mass scale:** Smart Weigh Pro digital pocket scale, 2000 g × 0.1 g (well under the ±1 g recharge target).
- **Brazing heat:** Bernzomatic TS8000 high-intensity torch head + MAP-Pro 3-can kit.
- **Filler + flux:** BCuP-5 15 % silver brazing alloy + Harris SSWF7 Stay Silv white brazing flux.
- **Copper prep:** 3M Scotch-Brite Maroon General Purpose Hand Pads (cut into strips for ACR copper OD prior to flux + braze).
- **Argon purge rig:** Uniweld RHP400 CGA-580 regulator (swaps onto the existing argon cylinder already feeding the laser welder) + Joywayus brass 1/4" SAE 45° flare nut (clamps flared 1/4" ACR stub onto RHP400 outlet + HVAC charging hose). No nitrogen cylinder needed.
- **Leak detector:** Toptes PT520A refrigerant/hydrocarbon gas leak detector.

## Procedure

### 1. Verify factory refrigerant + charge mass

Read the donor appliance back-panel rating label — refrigerant type (must be R-600a) and charge mass. The two donors tracked in [`../harvested/ice-maker/README.md`](../harvested/ice-maker/README.md) are both R-600a. Factory charge mass: **15 g** for Unit A (Antarctic Star HZB-12/Q, per manufacturer manual); **23 g** for Unit B (Frigidaire EFIC117-SS, per manufacturer manual). See harvested README per-unit for sources. Compressor body cast-stampings ("48.5-2" on Unit A's HD48Y11A; "45" on Unit B's BLC48AD) are *not* charge masses.

If the donor is anything other than R-600a (R-134a, R-410a, any HFC), this procedure does not apply: Section 608 certification is required to vent, and the cold-core architecture changes.

### 2. Vent factory R-600a

Install a piercing valve (saddle clamp + valve core) onto the compressor process tube — the short copper stub pinched-and-brazed shut at the factory ([`../harvested/ice-maker/README.md`](../harvested/ice-maker/README.md) "Process tube"). Open the valve and vent to atmosphere in a well-ventilated area — outdoors or under a vent hood is preferred — with no ignition sources within 3 m.

Confirm fully vented before proceeding: gauge reads atmospheric, no further hiss, no propane-like smell at the valve.

### 3. Cut the loop and start continuous argon flow

The factory drier stays in service (see [`../harvested/ice-maker/README.md`](../harvested/ice-maker/README.md) "Filter-drier" for rationale: the cap-tube outlet on any commodity replacement drier doesn't match the donor's hair-bore capillary, and the surgery to bridge that mismatch is rework risk for no functional gain). The drier, its brazed-on capillary tube, the cap-tube helix at the evap end, and the bonded suction-line heat-exchanger pair all stay together as one preserved upstream subassembly.

**Before cutting anything, start continuous argon flow into the loop:** hook the argon-purge rig (Uniweld RHP400 + flared 1/4" ACR stub + Joywayus flare nut + HVAC charging hose) to the BPV31 flare port on the compressor process tube, open the BPV31, and start low-pressure argon (a few PSI). This flow continues without interruption from the first cut in this step until vacuum begins in step 6. The flow does two jobs simultaneously: (a) the per-braze hydrocarbon sweep from Hazard B, and (b) the dry inert blanket that preserves the factory drier's desiccant during the loop-open period. One continuous regimen satisfies both.

With argon flowing through the loop, cut the refrigerant tubing at two points:

- **Suction side**, between the evaporator outlet and the compressor inlet — close to the evaporator. Argon exits here as one of the loop's open ends.
- **Capillary-tube side**, at the evaporator-inlet end of the cap tube (just upstream of the factory evap) — leaving the entire factory drier + cap tube + cap-tube helix intact, with cap tube length unchanged from factory. Argon exits here as the other open end.

The factory finger-plate evaporator (cold plate) and the hot-gas bypass solenoid + bypass line + tee come out — the bypass path has no purpose in the production refrigerant loop (the loop wants steady cold, not harvest cycles). The bonded capillary-tube + suction-line heat-exchanger pair (where they run alongside each other for most of the suction line's length) stays intact on the compressor side. Per [`../harvested/ice-maker/README.md`](../harvested/ice-maker/README.md) "Capillary tube + suction-line heat exchanger": keep the bonded pair together, don't separate them.

### 4. Tie in the suction line

Position the cold core's coil-outlet stub (top of the wound coil — refrigerant exits as low-pressure gas heading to the compressor) next to the factory suction line cut. Join the two with the HVAC 1/4" OD ACR-grade slip coupling, sweat × sweat. Both lines are 1/4" OD, so the coupling is a direct sweat join. Braze under the continuous argon flow established in step 3.

### 5. Tie in the capillary tube via pinch-swage

Position the cold core's coil-inlet stub (bottom of the wound coil) next to the capillary-tube end coming from the factory drier (cut to length at the evap-inlet end in step 3). The OD mismatch (1/4" ACR coil vs 0.031" cap tube) is handled by **pinch-swaging the coil-inlet stub down onto the cap tube using the Knipex 86 01 180 Pliers Wrench** — progressive 60° rotation collapse technique, no reducer fitting required. Once swaged, braze the joint under the continuous argon flow established in step 3.

If total cap-tube length changes substantially relative to the donor's factory length (e.g., the new coil is significantly longer or shorter than the donor evaporator), a refrigeration tech should recalculate cap length for the new load rather than guessing — per [`../harvested/ice-maker/README.md`](../harvested/ice-maker/README.md) "Capillary tube + suction-line heat exchanger".

### 6. Pull vacuum

All brazes complete. Stop the argon flow at the RHP400 regulator and close the BPV31. Disconnect the argon hose from the BPV31 flare port; connect the gauge manifold's 1/4" SAE flare in its place. Reopen the BPV31. Pull vacuum to 500 microns or below. Hold for ≥15 minutes. Valve off the pump and verify vacuum holds (no rise) for another 15 minutes. A rise during isolation indicates either residual moisture (run pump longer) or a leak (find and fix).

### 7. Mass-metered recharge

Place the vacuum-tight loop on a mass scale. Tare. Connect the Enviro-Safe R-600a can to the gauge manifold and the manifold to the BPV31 flare port. Open the can valve; refrigerant enters the loop under its own vapor pressure. Watch the scale; close the can valve and the manifold when mass reaches target. Target is *not* simply the factory charge mass from step 1 — the new evaporator coil has greater internal volume than the discarded factory finger-plate, so the recharge runs higher than factory. First-unit calibration starts from factory mass (15 g for Unit A / 23 g for Unit B, per step 1) plus a small overage and iterates against frost-pattern and suction-line superheat on first run-up — see Open items §1.

Disconnect the manifold; close the BPV31 and cap its flare port. The BPV31 stays clamped on the compressor process tube as the single permanent service-access point for the life of the appliance.

### 8. Initial run-up + leak check

Energize the compressor briefly. (Firmware enforces a 3-minute minimum off-time per [`../harvested/ice-maker/README.md`](../harvested/ice-maker/README.md) "Powering and control"; the first run-up starts that timer with no prior on-state.) Verify the compressor draws expected running current (~1 A) and the suction line drops cold within a minute or two.

Apply electronic leak detector or soap solution at all braze joints + the BPV31 saddle clamp + the BPV31 flare port cap + any threaded connection. No bubbles, no detector hits.

A leak at any joint requires the loop be re-vented through the BPV31 (open the valve, vent to atmosphere as in step 2), the joint re-cut, the continuous argon flow from step 3 restored, the joint re-brazed, the loop re-vacuumed (step 6), and re-charged (step 7). Field-repair-in-place with the charge still in is not the path.

## Output condition

A finished integrated refrigerant loop:

- Cold core's coil stubs brazed into the donor's loop (suction-line tie-in + cap-tube pinch-swage tie-in)
- Vacuum-tight (≤500 microns, no rise over 15 min isolated)
- Charged to within ±1 g of target mass
- No detectable leaks at any joint
- Compressor runs and pulls the suction line cold on first run-up
- Hot-gas bypass solenoid, line, and tee discarded with the factory finger-plate evaporator
- Factory drier preserved in service; the BPV31 flare port (closed and capped, BPV31 clamped on the compressor process tube) is the single permanent service-access point

The integrated assembly — cold core + plumbed compressor + condenser — is now ready for enclosure install and final wiring.

## Open items

Procedure-level gaps that need answers before unit 1 ships:

1. **Recharge target mass for the new larger evap coil.** Factory charge masses are known (Unit A 15 g, Unit B 23 g per their manufacturer manuals — see harvested README per-unit), but the recharge target for this build is *not* the factory mass because the new evaporator coil has greater internal volume than the discarded factory finger-plate. The volume-corrected target needs empirical validation on first run-up against frost-pattern + suction-line superheat. Bound: factory mass + the evap-volume-times-operating-density correction (order-of-magnitude +5-15 g for the ~80-110 mL volume delta vs. a finger-plate evap at typical R-600a operating density). Iterate in 1-2 g increments rather than committing to a calculated final number.
2. **Failure handling beyond "redo the sequence."** Decision tree for hard-to-find leaks, charge loss between vacuum check and run-up.
3. **No dedicated donor-teardown procedure.** Which steps remove which components, in what order, what gets discarded vs. salvaged — currently scattered across this doc and [`../harvested/ice-maker/README.md`](../harvested/ice-maker/README.md). Worth a standalone teardown doc when production teardown begins for unit 1.
