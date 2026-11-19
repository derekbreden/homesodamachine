# Refrigerant Loop

Integrate the Antarctic Star HZB-12/Q refrigeration circuit with the wrapped evaporator, then establish the charge under a repeatable water load.

Design intent and component rationale live in [`/hardware/README.md`](/hardware/README.md) "Refrigeration". Donor-component teardown notes (compressor, condenser, capillary tube, drier, hot-gas bypass) live in [`/hardware/reference/ice-maker/README.md`](/hardware/reference/ice-maker/README.md). Assembly-time argon-purge safety is documented at [`/business/regulatory.md`](/business/regulatory.md) "Assembly-time safety — argon purge during brazing". This document is the procedure that ties them together. The illustrated sequence is [`refrigeration-guide.pdf`](/hardware/refrigeration-guide/refrigeration-guide.pdf).

## Scope

This is a single-session integration procedure: bring a finished cold core and a donor ice maker together at one workspace, open the donor's refrigerant loop, braze the cold core's coil stubs into the donor's loop, vacuum, charge, run up. All multi-day prep work (coil winding, foam pour) happens upstream in [`cold-core.md`](/hardware/assembly/cold-core.md) before this session begins.

Bring the [donor ice maker](/hardware/reference/ice-maker/README.md), the [finished cold core](cold-core.md) with its cured foam and accessible coil stubs, R-600a refrigerant, and the dry inert gas specified by the A3 service setup.

Out: a leak-tested and evacuated refrigeration loop with a weighed first trial charge. The loaded commissioning run establishes the operating charge.

Not in scope: cold-core assembly — coil winding, foam pour — all in [`cold-core.md`](/hardware/assembly/cold-core.md); electronics-bay control wiring, AC distribution, and bolting the compressor down to the enclosure floor ([`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) §3).

## Safety

R-600a (isobutane) is flammable. Confirm the R-600a service equipment, its
pressure ratings and the work-area controls before opening the donor. The
verified household R-600a donor uses controlled outdoor charge removal under the
project's [household end-use basis](/business/regulatory.md#epa-section-608--refrigerant-handling).
The procedure for removing charge from the rebuilt loop depends on that loop's
own end-use and the service location.
[Secop hermetic service guide](https://www.secop.com/fileadmin/user_upload/technical-literature/guidelines/repair_of_hermetic_refrigeration_systems_05-2018_desg620a202.pdf)

**Hazard A — Refrigerant removal.** Remove the charge before cold-opening
the circuit. Establish residual clearance by the R-600a service method with
suitable detection. A reading at atmospheric pressure alone leaves residual
refrigerant in the oil and tubing unaccounted for.

**Hazard B — Residual hydrocarbon at the braze.** R-600a can remain dissolved
in compressor oil after charge removal. Clear residual refrigerant before hot work,
then maintain and verify dry inert flow through every tube segment being
heated. Protect the retained drier from moisture during open work.

**Hazard C — Braze heat conducted back into the printed shell.** Both loop joints are brazed on a copper stub that passes through the **PET-GF shell**, with foil exit seals and cured pour foam behind it. The installed tube routing sets the distance from the joint to the shell. Protect the shell, exit collars and foam from conducted heat before each braze.



The in-service hazard — a refrigerant leak post-build into a sealed compartment that contains an ignition source — is owned elsewhere. The compressor's terminal block and clip-on PTC module remain under the R-600a donor's own moulded power-box cover. The cover stays installed while the appliance connects only at the donor assembly's factory-external electrical interface; a missing, cracked, modified, loose, or incorrectly retained cover fails the build. The appliance adds no second sheet-metal shroud, and [`/business/regulatory.md`](/business/regulatory.md) carries the qualification still owed on the retained donor cover against the applicable 60335 enclosure provisions.

The AC switching relay lives on the electronics bay, away from the compartment, so its switching arc is not co-located with the leak. A hardware-only backstop is a BOJACK SF76E SEFUSE thermal fuse in series with the AC primary feeding the compressor — a one-shot cutoff that opens on the temperature of its own case, so what makes it a cutoff is contact: its case is pinched against the outside flank of the donor cover by the printed [`fuse-clamp`](/hardware/printed-parts/refrigeration/fuse-clamp/), whose two leaves press into the air gap the power box hangs over its own mounting plate, so the clamp rides the compressor rather than the cabinet — plus an ACEIRMC MQ-6 LPG/iso-butane sensor lying along the floor of the refrigeration bay's open −X strip beside the compressor, card on edge parallel to the flank and mesh horizontal in the well the flank opens for it. The bay's floor is one connected pool — every dominant brazed-joint leak site (cap-tube pinch-swage at the evap inlet, slip coupling at the evap outlet, service connection and compressor process tube) drains into it, and dense R-600a spreads over the slab as one layer — so what the sensor answers to is height, not aim: its mesh comes out below the power box's floor, so the layer reaches the module before it reaches the covered terminal assembly. It drops from above into two grooved posts standing on the bay's own floor (`enclosure._west_cradle`), the module having no mounting hole of its own — both acquired per the [refrigeration purchases](/hardware/ledger/purchases.md#6-refrigeration). Thermal fuse + gas sensor backstop the soft (firmware) cutoffs so a controller failure can't keep the compressor energized through a thermal or leak event.

## Inputs per appliance

Per-unit BOM lives in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §5 (refrigeration). The table below is the procedure-level summary; bom.md is the source of truth for per-unit allocation and cost. Status (ACQUIRED / ON-ORDER) for every item lives in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md) §6.

| Item | Source / spec | Notes |
|---|---|---|
| Donor ice maker | [Antarctic Star HZB-12/Q, B0F8NKJD6X](https://www.amazon.com/dp/B0F8NKJD6X) | Verify the harvested components against the [reference teardown](/hardware/reference/ice-maker/README.md). |
| Finished cold core | Output of [`cold-core.md`](/hardware/assembly/cold-core.md) | Wound coil bonded to carbonator, foam-poured, coil stubs protruding through the foam-shell's copper exits — inlet, outlet |
| Factory drier | Retained from the donor | Keep its capillary connection and protect its desiccant from moisture throughout open work. |
| R-600a refrigerant | Enviro-Safe B0CGG1WH1N | Weigh net mass delivered for each trial. |
| Process tube access | Qualified for R-600a and the bench pressures | The BPV31 in the model needs confirmation for A3 bench use. Supco directs removal of solderless taps after service. [Supco BPV31 FAQ](https://supco.com/web/supco_live/products/BPV31.html) |
| BCuP-5 silver brazing alloy, 15 % Ag, 1/16" × 1 troy oz | B0DQ3ZMHK7 | Phosphorus self-fluxing filler. Every loop joint is copper-to-copper, so all are brazed **dry — no flux**; the phosphorus is the fluxing agent. ~10 g per build, ~3 builds per rod |
| 3M Scotch-Brite Maroon hand pads | B07CGPCTHT | Abrasive prep on 1/4" ACR copper OD + fitting sockets before braze; ~2 of 20 pads per build |
| Dry purge and test gas | Gas, regulator and fixture qualified for their use | Prove an open sweep path for each heated segment. Use a regulated dry-inert test with a circuit-side gauge. |
| BOJACK SF76E SEFUSE thermal fuse + ACEIRMC MQ-6 LPG sensor module | B07Y61YTTK + B0978JSCZ8 | Hardware-only fire-safety backstops — SF76E in series with the AC primary feeding the compressor, MQ-6 module on edge along the floor of the refrigeration bay's −X strip (see Safety section above) |

Confirm the complete R-600a bench kit before starting. The refrigeration section of the [purchase ledger](/hardware/ledger/purchases.md) records which tools are on hand.

- **Temporary access and outdoor discharge:** check the actual process tube OD and usable straight length. Confirm the R-600a access fitting, hose, outlet site and final sealed closure before opening.
- **Cap-tube cutter** at the process-tube junction: Mastercool 70025
- **Tubing cutter, flaring tool:** RIDGID 31622 Model 150 + RIDGID 23332 Model 345
- **Tube bender + straightener** for the 1/4" ACR evaporator coil: Klein Tools 51006 3-in-1 bender + Wisscool 1/4" handheld straightener
- **Coil-to-cap-tube join:** Knipex 86 01 180 Pliers Wrench (7.25", smooth parallel-jaw) — pinch-swages 1/4" ACR copper inlet down onto the capillary tube (~0.031" bore) via progressive 60° rotation collapse. No reducer fitting required.
- **Coil-to-suction-line join:** HVAC 1/4" OD copper slip coupling (ACR-grade, sweat × sweat) joins coil outlet to factory suction line, both 1/4" OD.
- **Vacuum and gauges:** A3-suitable vacuum pump and manifold with a circuit-side micron gauge. Orion lists the ledger pump for other refrigerants. Use a low-volume absolute pressure sensor for running suction, or a compound gauge and local station barometer. [Orion pump specifications](https://orionmotortech.com/products/4cfm-vacuum-pump-1-stage-hvac-vacuum-pump-for-r12-r22-r134a-r410a-systems-small-1-3hp-38-micron-vacuum-pump-for-air-conditioner-servicing-resin-degassing-and-more-oil-included)
- **Mass scale and transfer volume:** verify the Smart Weigh Pro under the actual hose load. Use the repeatability and transfer method in the [bench guide](/hardware/refrigeration-guide/refrigeration-guide.pdf).
- **Brazing heat:** Bernzomatic TS8000 high-intensity torch head + MAP-Pro 3-can kit.
- **Braze heat protection** for the printed shell exits (Hazard C): two cotton shop rags and a cup of water, off the bench. Nothing is bought for this and nothing appears in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) — a soaked rag is a boiling-water clamp on the tube, which draws heat from the tube while it remains wet. Heat-blocking paste (~$25/tub) is the alternative and is rejected here: it has to be smeared onto and then cleaned off a tube that is about to be brazed dry, and residue on the OD near a phosphorus-fluxing joint is a contamination risk the rag does not carry.
- **Filler:** BCuP-5 15 % silver brazing alloy — phosphorus self-fluxes on copper, so every (copper-to-copper) loop joint is brazed **dry, no flux**. Brazing flux is only needed for a dissimilar-metal joint (copper-to-brass/steel), of which the loop has none; flux residue left inside a sealed refrigeration loop is corrosive and can plug the cap tube or drier screen, so it is deliberately omitted.
- **Copper prep:** 3M Scotch-Brite Maroon General Purpose Hand Pads (cut into strips for ACR copper OD prior to braze).
- **Dry gas rig:** use the shop's argon cylinder and RX Weld flowmeter for the open purge once the refrigerant-side connection and flow are verified. The owned RHP400 is specified for nitrogen. Confirm a compatible regulator, gauge, isolation and pressure limit for the static test. [Owned argon hardware](/hardware/ledger/tools.md#welding) · [Uniweld specifications](https://www.uniweld.com/product/nitrogen-regulators/)
- **Leak detection:** use a qualified R-600a wand, a known reference leak
  and a calibrated ambient monitor. The acquired TopTes PT520A can localize a
  response on the cool, de-energized appliance after the work area is cleared.
  Its methane concentration scale gives no installed R-600a leak rate.
  [TopTes PT520A manual](https://cdn.shopify.com/s/files/1/0651/5952/8680/files/PT520A.pdf?v=1768791404) · [Secop hermetic service guide](https://www.secop.com/fileadmin/user_upload/technical-literature/guidelines/repair_of_hermetic_refrigeration_systems_05-2018_desg620a202.pdf)

## Procedure

### 1. Identify the donor and first trial mass

Photograph the Antarctic Star HZB-12/Q appliance label and compressor sticker.
Record the model, electrical ratings and component identities. Use the U.S.
HZB-12/Q rating from the Intertek constructional report for the first trial mass
in the [bench guide](/hardware/refrigeration-guide/refrigeration-guide.pdf).
The inspected plate provides no charge mass. Read any markings the actual unit
carries and resolve a conflicting refrigerant or model identity before opening.
[Donor evidence](/hardware/reference/ice-maker/README.md#refrigerant)

### 2. Remove the factory charge outdoors

Isolate power and verify the household donor and R-600a identity. Check work-area
air and stage the qualified access and discharge hose before opening the service
connection. Secure the hose outlet outdoors in freely dispersing air, away from
ignition sources, people, openings and low places. Keep that location under
observation for the discharge. The donor stays de-energized.

After bulk discharge, use the R-600a service method to clear retained gas from
the circuit and oil. Record the outlet conditions and clearance checks before
cutting or heating. Confirm charge removal throughout the connected circuit.
If a suitable outdoor discharge is unavailable, establish compatible capture
before opening. Use the Intertek rating as the first fill.
[Whirlpool R-600a service manual, pp. 19–22](https://www.whirlpool.com/content/dam/global/documents/202409/technical-manual-w11105483-revb.pdf#page=19)

### 3. Separate the finger plate and verify each purge path

Trace and tag the sealed donor. Identify the two evaporator separations and
follow the hot-gas branch back to its discharge tee. Confirm the retained
compressor-to-condenser route and record the actual junction, materials and
approved rejoin in the A3 service plan. Use the guide's branch diagram to
identify what stays.

After charge removal and clearance, cold-cut the suction and capillary at the old
evaporator. Protect the factory drier, capillary, terminal helix and bonded
capillary/suction section. Complete separation of the bypass with the planned
discharge join. Support the remaining tubing and log each new joint.

Keep the factory drier dry during open work. Before heating, verify that dry
inert gas flows from the specified inlet, through the heated segment and out
a safe open outlet. Verify the two sides independently. A connection at the
compressor process tube does not establish flow through the discharge and
capillary path. Recheck the outlet as each join changes the route.
[Secop hermetic service guide](https://www.secop.com/fileadmin/user_upload/technical-literature/guidelines/repair_of_hermetic_refrigeration_systems_05-2018_desg620a202.pdf#page=9)

### 4. Heat-protect the copper exits before each braze

Both joints below are brazed on a stub that runs back into a PET-GF shell with cured foam behind it (Hazard C). Measure the actual clearance at the staged joint. Do this immediately before lighting the torch, and do it again for the second joint — a rag that has already been through one braze is dry.

- Soak a cotton shop rag and wring it so it is heavy with water but not running.
- Wrap it around the stub **hard against the shell exit**, on the core side of the joint, covering as much of the remaining stub as it will reach. The rag is the heat sink; the gap between it and the joint is what the torch has to overcome, so wrap it toward the shell exit, not toward the joint.
- Keep it wet for the whole braze. A rag that steams dry has stopped working and the shell exit starts climbing immediately; re-wet it between passes rather than pushing on.
- Aim the torch **away from the core** — flame and hot gas off toward the compressor side, never played along the stub toward the shell exit. The rag answers for what the copper conducts; it does nothing about a flame laid straight onto the shell exit.

After each braze, before moving on: look at the shell exit. Any gloss, sag, dimpling, or smell of scorched foam means the shell exit is compromised — it is a sealing surface and a foam boundary, and it is not repairable in place.

### 5. Tie in the suction line

Position the cold core's coil-outlet stub (top of the wound coil — refrigerant exits as low-pressure gas heading to the compressor) next to the factory suction line cut. Join the two with the HVAC 1/4" OD ACR-grade slip coupling, sweat × sweat. Both lines are 1/4" OD, so the coupling is a direct sweat join. Braze dry — no flux (BCuP-5 self-fluxes on copper; see Inputs) — under the verified inert sweep established in step 3.

### 6. Tie in the capillary tube via pinch-swage

Position the cold core's coil-inlet stub (bottom of the wound coil) next to the capillary-tube end coming from the factory drier (cut to length at the evap-inlet end in step 3). The size mismatch — a 1/4" OD coil stub against a cap tube of ~0.031" bore ([`reference/ice-maker/`](/hardware/reference/ice-maker/README.md)) — is handled by **pinch-swaging the coil-inlet stub down onto the cap tube using the Knipex 86 01 180 Pliers Wrench** — progressive 60° rotation collapse technique, no reducer fitting required. Once swaged, braze the joint under the verified inert sweep established in step 3.

Keep the capillary bore, length and bonded section fixed for the charge trials. Check for a kink or plugged braze before assigning a feed fault to the capillary design.

### 7. Pressure-test, then pull vacuum

The service plan establishes pressure and duration for the whole modified
circuit and fixture, constrained by the donor low-side rating and every
lower limit. With power isolated, pressure-test with regulated dry inert gas.
Let both sides and temperature stabilize. Isolate the supply and log actual
pressure and temperature at the circuit at both ends of the hold. Check
accessible seams and fixture seals with approved leak-detection solution.
Remove the solution and dry the surfaces after inspection.

Release inert test gas before connecting the A3 vacuum equipment. Keep the
micron gauge on the circuit side of the isolation valve and allow the high
side time to evacuate. Use the pumping and isolation times on the vacuum
page. Resolve a sustained rise before charging.
[Bench guide](/hardware/refrigeration-guide/refrigeration-guide.pdf)

### 8. Meter the first trial

Weigh the R-600a transfer after charge removal and evacuation. Use the approved
low-volume kit with a sealed split at the circuit boundary. Weigh the can, tap,
transfer hose, valve and end fitting together before and after so refrigerant
retained in the kit stays in both readings. Account for any transfer loss before
calling the difference net to the circuit. The [gram-scale page](/hardware/refrigeration-guide/refrigeration-guide.pdf#page=24)
gives the loaded check and the display targets.

Start at the U.S. HZB-12/Q rating printed on the metering page of the
[bench guide](/hardware/refrigeration-guide/refrigeration-guide.pdf).
The first mass is a commissioning point. Close and leak-check the service
access between runs. Log the delivered mass and the transfer setup. Weigh
each subsequent change and use the matched water-load trial below.

### 9. Initial run-up and leak check

Assemble the mounts, condenser airflow path, earth bonds, fuse and covered
compressor interface. Establish gas clearance, the installed interlock and
the protected bench power disconnect. Use the warm-wall demand from the
actual probes after the firmware off guard. Read running RMS amps and watts
on the P4400 with the feed and other loads recorded. Record standby readings,
first-run current and the falling coil temperature. The first repeatable
normal trace supplies a comparison for later runs. Stop for a stalled hum,
overload, lost airflow, protection trip or gas indication.

In the cleared area, prove the R-600a wand response to the reference source
before and after work. Use the guide's actual joint map. Include the new
discharge joint, condenser and drier while running on the high side. Sweep
both low-side tie-ins, the compressor return and the process connection
with the loop stopped, equalized, and measured positive relative to ambient.
Use the documented inert test for a location whose pressure or access cannot
support the charged check. Recheck the final process-tube seal.

For an ambient alarm, withdraw and use the established safe isolation and
clearance procedure. Remove the charge through the qualified service connection
using the route established for the rebuilt loop before opening a leaking joint.
Restore the inert flow and heat protection,
pressure-test, evacuate and weigh the next fill.
[Bench guide](/hardware/refrigeration-guide/refrigeration-guide.pdf)

## Output condition

A finished integrated refrigerant loop:

- Cold core's coil stubs brazed into the donor's loop (suction-line tie-in + cap-tube pinch-swage tie-in)
- Both printed shell exits unmarked — no gloss, sag or dimpling — and no scorch smell off the foam behind them (Hazard C)
- Pressure-tested and evacuated to the guide targets
- Weighed first trial with the transfer uncertainty and setup recorded
- No detectable leaks at any joint
- Compressor runs and pulls the suction line cold on first run-up
- Hot-gas bypass solenoid, line, and tee discarded with the factory finger-plate evaporator
- Factory drier preserved and temporary service access closed between trials

The integrated assembly — cold core + plumbed compressor + condenser — is now ready for enclosure install and final wiring.

## Charge commissioning

Follow pages 25 and 38–47 of the [bench guide](/hardware/refrigeration-guide/refrigeration-guide.pdf).
Use 16.0 g net for the first weighed fill. The [charge estimate](/hardware/refrigeration-guide/README.md#why-the-first-fill-is-160-g)
records the completed coil calculation. The measured bench comparison supplies
the commissioning result.

### Compare two runs at the first fill

With a completed high-reed refill, normal controls and unchanged airflow, time
the wall probe from the first running reading at or below 12 °C to the first
one at or below 8 °C. Sample at the same interval and compare matched loads.
Read the paired compressor-inlet pressure and contact temperature at the warm
crossing, just before normal cutoff, and after the normal restart. Page 39
gives the temperature floor directly from the pressure band. A run with a
refill, fault or freeze trip during the timed window is an interrupted lap.

After normal wall cutoff and a completed fill, use the faucet before loading
concentrate. Collect four 250 mL samples starting a minute apart. Measure at
mid-depth immediately after each pour. The cold-water target is 6 °C or colder
in every glass, with normal refill, recovery and restart. Record the repeated
lap times and temperatures separately from the refrigerant readings.
[Water targets](/hardware/assembly/calibration_inputs.rs) · [Cold policy](/firmware/lib/machine_policy/cold_policy.h)

### Observe the exposed return

Photograph the same visible suction route at the 8 °C crossing and the last
running sample. Mark whether the copper is dry, sweating or frosted and the
furthest point reached. The winding stays foamed. Frost depends on surface
temperature and the surrounding air. When it spreads toward the compressor,
check the paired B readings. A B reading below the chart floor, frost reaching
the compressor can or abnormal knock calls for a safe stop. Use operating
measurements and the glass test to decide the charge.
[Secop capillary diagnostics](https://www.secop.com/fileadmin/user_upload/technical-literature/danfoss-lectures/operational_defects_in_hermetic_compressors_and_refrigerating_systems.pdf#page=52)

### Choose the next measured charge

- **Keep 16.0 g** when both matched runs pass the four-glass test, B clears
  the cold-end and restart checks, and the controls run normally.
- **Try 17.0 g once** when both runs miss the glass target, the local A and C
  readings meet the WARM A and LOW C lookups, and airflow, leak and drier
  checks clear. Use the weighed one-gram step and repeat both runs.
- **Hold the charge** when measurements conflict or are too coarse, when
  the high side shows liquid held upstream of a possible restriction, or when
  a refill or freeze trip invalidates the lap. Correct the indicated condition
  before repeating.
- **Stop** for a below-floor B reading, frost onto the compressor, abnormal
  operation, lost airflow, overload or a gas indication. Follow the
  established safe isolation procedure and diagnose before restarting.

Keep the lowest demonstrated passing fill. If the trial at 17.0 g fails, end the
charge increase. To restore the prior measured fill after a failed addition,
remove the full charge by the applicable handling method, evacuate and weigh
in 16.0 g again. Close and leak-check the final service access and save the
matched runs and finished charge with the unit.
[Worked examples](/hardware/refrigeration-guide/refrigeration-guide.pdf#page=47)
