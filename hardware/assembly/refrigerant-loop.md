# Refrigerant Loop

The production procedure for converting a donor countertop ice maker into the appliance's refrigeration loop — from vent of the factory R-600a charge, through coil wind around the carbonator vessel, to final mass-metered recharge. The most safety-critical procedure in the build: the loop is open to a flammable hydrocarbon for several steps, and the argon purge during brazing is load-bearing.

Design intent and component rationale live in [`../future.md`](../future.md) "Refrigeration subsystem". Donor-component teardown notes (compressor, condenser, capillary tube, drier, hot-gas bypass) live in [`../harvested/ice-maker/README.md`](../harvested/ice-maker/README.md). Assembly-time argon-purge safety is documented at [`../../business/regulatory.md`](../../business/regulatory.md) "Assembly-time safety — argon purge during brazing". This document is the repeatable production procedure that ties them together.

## Scope

In: donor ice maker (verified topology in [`../harvested/ice-maker/README.md`](../harvested/ice-maker/README.md)), one hydro-tested + passivated carbonator vessel (per [`pressure-vessel.md`](pressure-vessel.md)), replacement filter-drier, R-600a refrigerant, argon from the welder cylinder.

Out: a closed and brazed refrigerant loop, vacuum-tight, charged within ±1 g of target mass, with the new evaporator coil bonded around the carbonator vessel. The compressor runs on its first run-up and the suction line drops cold.

Not in scope: cold-core foam pour ([`cold-core.md`](cold-core.md)), electronics-shelf control wiring, AC distribution, compressor shroud install (its own spec at [`../cut-parts/compressor-shroud/README.md`](../cut-parts/compressor-shroud/README.md)).

## Safety

R-600a (isobutane) is flammable, LFL ~1.8 % in air. EPA Section 608 carves natural refrigerants out of the venting prohibition, so no technician certification is legally required ([`../../business/regulatory.md`](../../business/regulatory.md)). The gas doesn't care about the regulatory carveout. Two distinct hazards apply to this procedure:

**Hazard A — Vent the factory charge before applying any flame.** Heating a pressurized R-600a circuit with a torch is the textbook flash-fire scenario. The charge must be vented and the loop allowed to decompress to atmospheric before any cut, braze, or torch step.

**Hazard B — Residual hydrocarbon at the braze.** After venting, residual R-600a remains dissolved in the compressor oil and pooled in low points of the tubing. When a torch is applied to copper near an oil-soaked compressor pocket, the flame front pulls residual hydrocarbon into itself. Mitigation, load-bearing for this procedure: flow low-pressure argon (a few psi, *flowing*, not static) through the open loop during and through each braze, sweeping residual fuel out ahead of the heat. The existing welder-side argon cylinder is the source.

The in-service hazard — a refrigerant leak post-build into a sealed compartment that contains an ignition source — is owned elsewhere: the compressor shroud isolates the highest-temperature surface in the system, and the AC switching relay is deliberately placed *outside* the shroud so its switching arc isn't co-located with the protected zone. See [`../cut-parts/compressor-shroud/README.md`](../cut-parts/compressor-shroud/README.md). The shroud also carries a hardware-only backstop: a BOJACK SF76E SEFUSE thermal fuse (77 °C, in series with the AC primary feeding the compressor) plus an ACEIRMC MQ-6 LPG/iso-butane sensor inside the shroud — both ON-ORDER per [`../purchases.md`](../purchases.md) §6. Thermal fuse + gas sensor backstop the soft (firmware) cutoffs so a controller failure can't keep the compressor energized through a thermal or leak event.

## Inputs per appliance

Per-unit BOM lives in [`../bom.md`](../bom.md) §5 (refrigeration); 3M 425 foil tape is categorized in §6 (cold-core insulation) because it's a thermal-interface part, even though it gets applied during step 4 below. The table below is the procedure-level summary; bom.md is the source of truth for per-unit allocation and cost. Status (ACQUIRED / ON-ORDER) for every item lives in [`../purchases.md`](../purchases.md) §6.

| Item | Source / spec | Notes |
|---|---|---|
| Donor ice maker | Generic B0F42MT8JX or Frigidaire EFIC117-SS B07PCZKG94 | Both verified topology |
| Replacement filter-drier | Supco SUD8358 UV-dye filter-drier, 1/4" sweat × cap-tube outlet | XH-9 hydrocarbon-compatible desiccant + integrated Schrader; the cap-tube outlet accepts the factory capillary tube directly. The Supco D111 in purchases.md is the wrong-part legacy, retained as spare |
| R-600a refrigerant | Enviro-Safe B0CGG1WH1N (3-pack + brass charging gauge) | ~40 g per system, mass-metered; one 3-can pack covers ~12 recharges |
| GOORY 1/4" OD × 0.031" wall ACR copper tubing | B0DKSW5VL9 | ~24 ft per vessel for coil + tie-ins (1/2 of 50 ft roll per build) |
| 3M 425 aluminum foil tape | B07BTW7C2N | Coil-to-vessel thermal interface; applied as continuous skin under the coil; one 180 ft roll covers ~12 builds (bom.md §6, not §5 — categorized as a cold-core insulation part) |
| Supco BPV31 bullet-piercing valve | B00DM8J3MI | Taps compressor process tube to vent factory R-600a; single-use per build, left clamped on the cut stub |
| BCuP-5 silver brazing alloy, 15 % Ag, 1/16" × 1 troy oz | B0DQ3ZMHK7 | Phosphorus-bearing self-fluxing filler for copper-to-copper joints; ~10 g per build, ~3 builds per rod |
| 3M Scotch-Brite Maroon hand pads | B07CGPCTHT | Abrasive prep on 1/4" ACR copper OD + fitting sockets before flux + braze; ~2 of 20 pads per build |
| Argon | Welder cylinder + Uniweld RHP400 brazing-purge regulator | Purge flow during every braze; no new cylinder needed |
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

Read the donor appliance back-panel rating label — refrigerant type (must be R-600a) and charge mass. The two donors tracked in [`../harvested/ice-maker/README.md`](../harvested/ice-maker/README.md) are both R-600a. Factory charge mass: **23 g** for Unit B (Frigidaire EFIC117-SS, per manufacturer manual — see harvested README "Unit B"); Unit A (generic B0F42MT8JX) still open until the appliance back-panel label is read (no published manufacturer documentation found). Compressor body cast-stampings ("48.5-2" on Unit A's HD48Y11A; "45" on Unit B's BLC48AD) are *not* charge masses.

If the donor is anything other than R-600a (R-134a, R-410a, any HFC), this procedure does not apply: Section 608 certification is required to vent, and the cold-core architecture changes.

### 2. Vent factory R-600a

Install a piercing valve (saddle clamp + valve core) onto the compressor process tube — the short copper stub pinched-and-brazed shut at the factory ([`../harvested/ice-maker/README.md`](../harvested/ice-maker/README.md) "Process tube"). Open the valve and vent to atmosphere in a well-ventilated area — outdoors or under a vent hood is preferred — with no ignition sources within 3 m.

Confirm fully vented before proceeding: gauge reads atmospheric, no further hiss, no propane-like smell at the valve.

### 3. Cut the loop

With the loop fully vented, cut the refrigerant tubing at two points:

- **Suction side**, between the evaporator outlet and the compressor inlet
- **Capillary-tube side**, between the filter-drier outlet and the evaporator inlet

The factory evaporator (cold plate) and filter-drier come out as a discarded subassembly — the capillary tube stays brazed to the drier outlet at one end and is discarded with the drier.

The bonded capillary-tube + suction-line heat-exchanger pair (where they run alongside each other for most of the suction line's length) stays intact on the compressor side. The cut is downstream of that pair, at the evaporator end. Per [`../harvested/ice-maker/README.md`](../harvested/ice-maker/README.md) "Capillary tube + suction-line heat exchanger": keep the bonded pair together, don't separate them.

### 4. Wind the evaporator coil around the vessel

A hydro-tested + passivated carbonator vessel (per [`pressure-vessel.md`](pressure-vessel.md)) is the substrate. Wind the GOORY 1/4" OD × 0.031" wall ACR copper tubing as a single-layer helical coil at ~1/8" pitch around the vessel OD — ~22 ft of wrap per vessel + ~2 ft each end for the compressor + suction tie-ins. The 0.031" wall was specifically chosen to resist kinking at the bend radius around the 5" OD vessel; thinner wall kinks, this wall holds.

Bond the coil to the vessel OD with 3M 425 aluminum foil tape applied as a continuous skin between vessel and coil. The tape spans the tank-to-coil thermal interface.

Wind around the printed [coil-mandrel](../printed-parts/cold-core/coil-mandrel/generate_step_cadquery.py) — hollow PETG cylinder with a shallow 1 mm helical guide groove, mandrel OD 123 mm vs. tank OD 127 mm so the as-wound coil inner radius is 3 mm under the tank radius and tightens onto the vessel after slip-off. Wind length 120.4 mm and 9.687 wraps (pitch 12.43 mm) are set to align the coil's inlet/outlet ends with the foam-shell copper plugs at Y=46 and Y=166.4, so the exit bends are purely radial with no vertical jog. Pull the wound coil off the mandrel and slip it onto the foil-taped vessel; coil springback (1–3 mm radial) leaves a net interference fit.

[`../handwork.md`](../handwork.md) "Bend copper around the pressure vessel" is the summary-level dev-phase entry for this step.

### 5. Braze in the new filter-drier

Braze the new Supco SUD8358 filter-drier into the cut between the condenser outlet and (in step 7) the capillary tube that feeds the new evaporator coil. The SUD8358 has an integrated Schrader port that becomes the post-build vacuum + recharge access point. The factory drier was discarded in step 3 because the desiccant is spent once the loop is open — reusing a saturated drier gives a short service life and eventual capillary icing. (The earlier Supco D111 buy — kept as a spare per [`../purchases.md`](../purchases.md) §6 — is the wrong-part legacy.)

**Argon purge during every braze:** flow low-pressure argon (a few psi) through the open loop using the Uniweld RHP400 regulator on the existing argon cylinder, with a flared 1/4" ACR stub + Joywayus flare nut + HVAC charging hose as the rig. Argon enters at the compressor process tube and exits at the cut being brazed; flow continues through joint cool-down. The purge sweeps residual hydrocarbon from the compressor oil out ahead of the torch. This is the load-bearing safety step for every braze in steps 5–7.

### 6. Tie in the suction line

Join the new evaporator coil's outlet end (top of the wound coil — refrigerant exits as low-pressure gas heading to the compressor) to the factory suction line using the HVAC 1/4" OD ACR-grade slip coupling, sweat × sweat. Both lines are 1/4" OD, so the coupling is a direct sweat join. Braze with argon purge as in step 5.

### 7. Tie in the capillary tube via pinch-swage

Join the new evaporator coil's inlet end (bottom of the wound coil) to the capillary-tube end coming from the new drier. The OD mismatch (1/4" ACR coil vs 0.031" cap tube) is handled by **pinch-swaging the coil inlet down onto the cap tube using the Knipex 86 01 180 Pliers Wrench** — progressive 60° rotation collapse technique, no reducer fitting required. Once swaged, braze the joint with argon purge as in step 5.

If total cap-tube length changes substantially relative to the donor's factory length (e.g., the new coil is significantly longer or shorter than the donor evaporator), a refrigeration tech should recalculate cap length for the new load rather than guessing — per [`../harvested/ice-maker/README.md`](../harvested/ice-maker/README.md) "Capillary tube + suction-line heat exchanger".

### 8. ~~Hot-gas bypass solenoid disposition~~

Resolved by dropping the solenoid entirely during donor teardown — once the factory evaporator is cut out (step 3) and replaced by the coil wound around the carbonator vessel (step 4), the bypass path has no purpose in the production refrigerant loop. The solenoid, its bypass line, and the tee come off with the discarded evaporator subassembly. Documented obliquely here only because there's no dedicated donor-teardown doc yet (see "Open items").

### 9. Pull vacuum

Connect the gauge manifold to the new drier's Schrader port. Pull vacuum to 500 microns or below. Hold for ≥15 minutes. Valve off the pump and verify vacuum holds (no rise) for another 15 minutes. A rise during isolation indicates either residual moisture (run pump longer) or a leak (find and fix).

### 10. Mass-metered recharge

Place the vacuum-tight loop on a mass scale. Tare. Connect the Enviro-Safe R-600a can to the gauge manifold and to the Schrader. Open the can valve; refrigerant enters the loop under its own vapor pressure. Watch the scale; close the can valve and the manifold when mass reaches target. Target is *not* simply the factory charge mass from step 1 — the new evaporator coil has greater internal volume than the discarded factory finger-plate, so the recharge runs higher than factory. First-unit calibration starts from factory mass (23 g for Unit B; Unit A still open) plus a small overage and iterates against frost-pattern and suction-line superheat on first run-up — see Open items §2.

Disconnect the manifold; cap the Schrader.

### 11. Initial run-up + leak check

Energize the compressor briefly. (Firmware enforces a 3-minute minimum off-time per [`../harvested/ice-maker/README.md`](../harvested/ice-maker/README.md) "Powering and control"; the first run-up starts that timer with no prior on-state.) Verify the compressor draws expected running current (~1 A) and the suction line drops cold within a minute or two.

Apply electronic leak detector or soap solution at all braze joints + the Schrader + any threaded connection. No bubbles, no detector hits.

A leak at any joint requires the loop be re-vented (per step 2 procedure), the joint re-cut, re-brazed with argon purge, re-vacuumed (step 9), re-charged (step 10). Field-repair-in-place with the charge still in is not the path.

## Output condition

A finished refrigerant loop:

- Vessel wrapped in coil, coil bonded to vessel with 3M 425 foil tape
- Vacuum-tight (≤500 microns, no rise over 15 min isolated)
- Charged to within ±1 g of target mass
- No detectable leaks at any joint
- Compressor runs and pulls the suction line cold on first run-up
- Hot-gas bypass solenoid, line, and tee discarded with the factory evaporator subassembly
- Filter-drier carries a fresh, sealed Schrader

The wrapped vessel + plumbed compressor + condenser assembly is the input to [`cold-core.md`](cold-core.md) for the foam-pour install.

## Open items

Procedure-level gaps that need answers before unit 1 ships:

1. ~~**Coil winding technique for unit 1.**~~ Resolved by the printed [coil-mandrel](../printed-parts/cold-core/coil-mandrel/generate_step_cadquery.py): hollow PETG cylinder with a shallow helical guide groove, sized 3 mm undersize vs. the tank so the coil clamps after slip-off, with wind length and wrap count aligned to the foam-shell plug positions. Working well by hand.
2. **Donor factory charge mass — partial.** Unit B (Frigidaire EFIC117-SS): **23 g** per manufacturer manual (see harvested README "Unit B"). Unit A (generic B0F42MT8JX): still open — no published manufacturer documentation; read from the appliance back-panel label during teardown. Separately and more loadbearing: the recharge target for this build is not the factory mass, because the new evaporator coil has greater internal volume than the discarded factory finger-plate evaporator. The volume-corrected target needs to be empirically validated on first run-up against frost-pattern + suction-line superheat. Bound: factory mass + the evap-volume-times-operating-density correction (order-of-magnitude +5-15 g for the ~80-110 mL volume delta vs. a finger-plate evap at typical R-600a operating density). Iterate in 1-2 g increments rather than committing to a calculated final number.
3. **Failure handling beyond "redo the sequence."** Decision tree for hard-to-find leaks, charge loss between vacuum check and run-up.
4. **No dedicated donor-teardown procedure.** Which steps remove which components, in what order, what gets discarded vs. salvaged — currently scattered across this doc and [`../harvested/ice-maker/README.md`](../harvested/ice-maker/README.md). Worth a standalone teardown doc when production teardown begins for unit 1; for now, ad-hoc dispositions like the hot-gas bypass solenoid (step 8 above) are folded into per-component notes here rather than captured in one place.
