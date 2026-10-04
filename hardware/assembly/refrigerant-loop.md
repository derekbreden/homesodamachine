# Refrigerant Loop

The integration procedure for converting an R-600a donor countertop ice maker into the appliance's refrigeration loop. Coil winding and foam work are upstream in `cold-core.md`. Opening, brazing, evacuation and charging require a technician trained for flammable refrigerants and a written service setup appropriate to this donor and the completed machine.

Design intent and component rationale live in [`/hardware/README.md`](/hardware/README.md) "Refrigeration". Donor-component teardown notes live in [`/hardware/reference/ice-maker/README.md`](/hardware/reference/ice-maker/README.md). The illustrated sequence is [`refrigeration-guide.pdf`](/hardware/refrigeration-guide/refrigeration-guide.pdf). The service hold points below apply before the loop is opened; the guide does not qualify an unresolved joint or charge recipe.

## Scope

Bring a finished cold core and a donor ice maker together at one workspace, remove the donor charge, open the loop, replace the drier, connect the coil, leak-test, evacuate, charge and run up. All multi-day prep work (coil winding, foam pour) happens upstream in [`cold-core.md`](/hardware/assembly/cold-core.md).

In: a donor verified against its label and actual circuit; a finished cold core with [200 mm](PROT_INLET) inlet and [175 mm](PROT_OUTLET) outlet protruding from its copper-plug faces; refrigerant-grade R-600a; a compatible sealed replacement drier; dry nitrogen; and approved hydrocarbon service equipment. The named stock in the ledger is an inventory, not evidence that every tool is suitable for this work.

Out: a closed and brazed refrigerant loop, vacuum-tight, charged within [±1 g](RECHARGE_TOL) of target mass, with the cold core's evaporator coil now brazed into the donor's refrigeration cycle. The compressor runs on its first run-up and the suction line drops cold.

Not in scope: cold-core assembly — coil winding, foam pour — all in [`cold-core.md`](/hardware/assembly/cold-core.md); electronics-bay control wiring, AC distribution, and bolting the compressor down to the enclosure floor ([`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) §3).

## Safety

R-600a (isobutane) is flammable, LFL ~1.8 % in air. The Section 608 exemption is
end-use-specific. The residential household design basis and its scope are recorded in
[`/business/regulatory.md`](/business/regulatory.md); the classification is the project's
reasoned basis rather than an individual EPA determination. Every service route still
addresses flammability and the actual appliance end-use. Three hazards apply to this
procedure — two to the technician, one to the part:

**Hazard A — Remove the charge before opening or heating.** Use the technician's controlled hydrocarbon-handling route. Its equipment, discharge location and end-use basis must be recorded. A zero-pressure gauge or lack of smell does not establish that the oil and tubing are free of residual fuel. No cut or heat is authorized solely by those observations.

**Hazard B — Residual hydrocarbon at the braze.** Residual R-600a can leave compressor oil after charge removal. Use dry-nitrogen clearing and braze protection with an unobstructed outlet and measured flow, under the technician's service procedure. A cylinder-pressure setting does not prove flow through each branch. Secop's hermetic-system service guidance specifies dry nitrogen and drier replacement after opening; an inert blanket does not establish that a used drier is fit for reuse. The current argon arrangement has no recorded donor-specific qualification.

**Hazard C — Braze heat conducted back into the printed copper-plug stack.** Both loop joints are brazed on a stub whose other end is a printed **PETG** copper plug ([`printed-parts/cold-core/copper-plugs/`](/hardware/printed-parts/cold-core/copper-plugs/), [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §7) with cured pour foam behind it. PETG's glass transition is [~80 °C](PETG_TG), and the joint is [~92 mm](JOINT_STANDOFF) from the plug face at most — the routed leg `_lines` refrig-3 is the whole of the reach, and it cannot be opened up: the suction leaves the compressor's shell on a tangent line, not a face, so where that leg goes is settled by which tangent the stub stands on and not by how much copper is cut. Copper is the conductor between the two.

Heat protection is unqualified at this standoff. A wet rag can reduce conducted heat, but water near its boiling point is above the plug's nominal glass transition and does not establish a safe plug temperature. Before an installed-core braze, qualify the joint sequence on the same copper reach, printed plug and foam stack, with temperature measured at the plug interface and an acceptance limit justified for the printed material and sealing function. An unmarked face alone is insufficient evidence. Keep flame and hot gas directed away from the core.

The in-service hazard — a refrigerant leak post-build into a sealed compartment that contains an ignition source — is owned elsewhere. The compressor's terminal block and clip-on PTC module remain under the R-600a donor's own moulded power-box cover. The cover stays installed while the appliance connects only at the donor assembly's factory-external electrical interface; a missing, cracked, modified, loose, or incorrectly retained cover fails the build. The appliance adds no second sheet-metal shroud, and [`/business/regulatory.md`](/business/regulatory.md) carries the qualification still owed on the retained donor cover against the applicable 60335 enclosure provisions.

The AC switching relay lives on the electronics bay, away from the compartment, so its switching arc is not co-located with the leak. A hardware-only backstop is a BOJACK SF76E SEFUSE thermal fuse ([77 °C](SF76E_TEMP), in series with the AC primary feeding the compressor) — a one-shot cutoff that opens on the temperature of its own case, so what makes it a cutoff is contact: its case is pinched against the outside flank of the donor cover by the printed [`fuse-clamp`](/hardware/printed-parts/refrigeration/fuse-clamp/), whose two leaves press into the air gap the power box hangs over its own mounting plate, so the clamp rides the compressor rather than the cabinet — plus an ACEIRMC MQ-6 LPG/iso-butane sensor lying along the floor of the refrigeration bay's open −X strip beside the compressor, card on edge parallel to the flank and mesh horizontal in the well the flank opens for it. The bay's floor is one connected pool — every dominant brazed-joint leak site (cap-tube pinch-swage at the evap inlet, slip coupling at the evap outlet, BPV31 saddle clamp + flare cap, compressor process tube) drains into it, and dense R-600a spreads over the slab as one layer — so what the sensor answers to is height, not aim: its mesh comes out below the power box's floor, so the layer reaches the module before it reaches the covered terminal assembly. It drops from above into two grooved posts standing on the bay's own floor (`enclosure._west_cradle`), the module having no mounting hole of its own — both ON-ORDER per [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md) §6. Thermal fuse and gas interlock complement the firmware cutoffs. Their installed fit, module polarity, gas threshold and shutdown behavior still require the commissioning evidence listed in `hardware/concerns.md`; they do not establish protection against every controller or relay failure.

## Inputs per appliance

Per-unit BOM lives in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §5 (refrigeration). The table below is the procedure-level summary; bom.md is the source of truth for per-unit allocation and cost. Status (ACQUIRED / ON-ORDER) for every item lives in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md) §6.

| Item | Source / spec | Notes |
|---|---|---|
| Donor ice maker | Generic B0F42MT8JX or Frigidaire EFIC117-SS B07PCZKG94 | Unit A topology recorded; verify Unit B at teardown |
| Finished cold core | Output of [`cold-core.md`](/hardware/assembly/cold-core.md) | Wound coil bonded to carbonator, foam-poured, coil stubs protruding through the foam-shell's copper-plug exits — [200 mm](PROT_INLET) inlet, [175 mm](PROT_OUTLET) outlet |
| Replacement drier | Supco D111 and SUD8358 are stocked candidates | The technician specifies R-600a/oil compatibility, connection arrangement and metering preservation; keep the selected drier sealed until assembly. Do not assume a dye-bearing drier is suitable without that review. |
| R-600a refrigerant | Enviro-Safe B0CGG1WH1N is stocked | Verify refrigerant grade/composition and the charging connection. Finished-machine charge mass is open; the approximate ledger allocation is not a charging recipe. |
| Supco BPV31 bullet-piercing valve | B00DM8J3MI | Temporary process-tube access, subject to tubing fit and manufacturer instructions. Supco's FAQ says solderless piercing valves should be removed after repair. Specify and qualify the final hermetic closure or permanent service connection before opening the donor. |
| BCuP-5 silver brazing alloy, 15 % Ag, 1/16" × 1 troy oz | B0DQ3ZMHK7 | Phosphorus self-fluxing filler. Every loop joint is copper-to-copper, so all are brazed **dry — no flux**; the phosphorus is the fluxing agent. ~10 g per build, ~3 builds per rod |
| 3M Scotch-Brite Maroon hand pads | B07CGPCTHT | Abrasive prep on 1/4" ACR copper OD + fitting sockets before braze; ~2 of 20 pads per build |
| Dry nitrogen | Technician's qualified clearing/purge rig | Nitrogen clearing and controlled braze flow. Uniweld lists the RHP400 as a nitrogen regulator with 20–400 PSIG delivery; the regulator alone does not establish a suitable low-flow braze setup. |
| BOJACK SF76E [77 °C](SF76E_TEMP) SEFUSE thermal fuse + ACEIRMC MQ-6 LPG sensor module | B07Y61YTTK + B0978JSCZ8 | Hardware-only fire-safety backstops — SF76E in series with the AC primary feeding the compressor, MQ-6 module on edge along the floor of the refrigeration bay's −X strip (see Safety section above) |

Tooling — all committed in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md) §6 (refrigeration) and §1 (argon side), ACQUIRED unless noted:

- **Temporary process access:** Supco BPV31 bullet-piercing valve, under its installation instructions; final closure is specified separately.
- **Cap-tube cutter** at the process-tube junction: Mastercool 70025
- **Tubing cutter, flaring tool:** RIDGID 31622 Model 150 + RIDGID 23332 Model 345
- **Tube bender + straightener** for the 1/4" ACR evaporator coil: Klein Tools 51006 3-in-1 bender + Wisscool 1/4" handheld straightener
- **Coil-to-cap-tube join:** Knipex 86 01 180 smooth parallel-jaw pliers are the proposed pinch-swage tool. Qualify insertion, bore preservation and braze integrity on a representative joint before the installed-core joint.
- **Coil-to-suction-line join:** HVAC 1/4" OD copper slip coupling (ACR-grade, sweat × sweat) joins coil outlet to factory suction line, both 1/4" OD.
- **Vacuum equipment:** use equipment explicitly suitable for R-600a plus an absolute micron gauge at the system. The owned Orion pump and manifold have no recorded exact-model hydrocarbon approval. Orion's current VPH-BN0A-O1/O2 manual excludes refrigerants beyond its named R134a/R12/R22/R502 uses; a compound manifold dial cannot measure the [500 microns](VACUUM_TARGET) target.
- **Mass scale:** Smart Weigh Pro digital pocket scale, 2000 g × 0.1 g (well under the [±1 g](RECHARGE_TOL) recharge target).
- **Brazing heat:** Bernzomatic TS8000 high-intensity torch head + MAP-Pro 3-can kit.
- **Braze heat protection:** a heat sink and flame shield chosen and qualified for the actual plug/foam stack, with interface temperature monitoring. A wet rag may be part of that setup; it is not its acceptance criterion.
- **Filler:** BCuP-5 15 % silver brazing alloy — phosphorus self-fluxes on copper, so every (copper-to-copper) loop joint is brazed **dry, no flux**. Brazing flux is only needed for a dissimilar-metal joint (copper-to-brass/steel), of which the loop has none; flux residue left inside a sealed refrigeration loop is corrosive and can plug the cap tube or drier screen, so it is deliberately omitted.
- **Copper prep:** 3M Scotch-Brite Maroon General Purpose Hand Pads (cut into strips for ACR copper OD prior to braze).
- **Nitrogen rig:** a compatible regulator, relief/pressure controls, hoses and flow control selected by the technician for the circuit's weakest rated component. Keep its outlet open during clearing and brazing; close-circuit pressure testing is a separate setup.
- **Leak detection:** a suitable calibrated hydrocarbon detector and leak-test solution. The Toptes PT520A is a combustible-gas detector; its available specifications do not establish a production leak-rate acceptance threshold.

## Procedure

### 1. Verify factory refrigerant + charge mass

Read the donor appliance back-panel rating label — refrigerant type (must be R-600a) and charge mass. The two donors tracked in [`/hardware/reference/ice-maker/README.md`](/hardware/reference/ice-maker/README.md) are both R-600a. Factory charge mass: **[15 g](UNIT_A_CHARGE)** for Unit A (Antarctic Star HZB-12/Q, per manufacturer manual); **[23 g](UNIT_B_CHARGE)** for Unit B (Frigidaire EFIC117-SS, per manufacturer manual). See harvested README per-unit for sources. Compressor body cast-stampings ("48.5-2" on Unit A's HD48Y11A; "45" on Unit B's BLC48AD) are *not* charge masses.

If the donor is anything other than R-600a (R-134a, R-410a, any HFC), this procedure
does not apply: the applicable recovery practices and technician qualifications need
review, and the cold-core architecture changes. Technician certification does not
authorize intentional venting of non-exempt refrigerants.

### 2. Remove the donor charge

Before opening the donor, the technician records the refrigerant, donor end-use, approved handling method, ventilation/exhaust arrangement, ignition control and service equipment. EPA's exemption is end-use-specific. This procedure does not direct an uncontrolled release at the bench, and the donor's status does not authorize venting of the rebuilt dispenser.

The compressor process tube is the factory closed charging stub. A BPV31 may provide temporary access if its adapter and installation instructions match the actual copper tube. Connect the controlled handling rig before piercing or opening it. Remove the charge under that rig's procedure, depressurize, and verify the required residual-hydrocarbon clearing condition before cutting. Keep the compressor upright and retain its oil.

### 3. Open the evaporator connections, clear the branches and replace the drier

Stage all joints and replacement components before opening. Mark the factory capillary's route, bonded suction heat exchanger, helix and total length. Protect these from kinks and unnecessary shortening; a changed restriction needs a technician's metering specification.

Use a tubing cutter at the suction side near the factory evaporator and a dedicated capillary cutter at the evaporator inlet. Keep swarf and abrasive grit out. Remove the finger-plate evaporator and the hot-gas bypass branch under the traced circuit plan, leaving no discharge-to-suction bypass path or open tee. The exact discharge-side closure is a donor-teardown hold point.

Clear both high and low branches separately with dry nitrogen, under the technician's approved flow/pressure sequence. Continue protective flow through each joint during brazing with an open outlet. No flame, oxygen or compressed-air clearing. The Uniweld RHP400's published 20–400 PSIG range is not a low-flow braze recipe; specify flow control and pressure protection appropriate to the component limits.

Replace the filter-drier whenever the loop is opened. Cut the used drier out without heating it. The technician selects a sealed, compatible replacement and its connection to the retained capillary, preserving the documented metering length or specifying a recalculation. The stocked D111/SUD8358 names alone do not qualify that arrangement. Keep the replacement capped until it can be installed and close interrupted work against moisture entry.

### 4. Qualify plug heat protection before either installed-core braze

The copper runs into PETG plugs with cured foam behind them. Qualify a representative joint at the actual [~92 mm](JOINT_STANDOFF) maximum reach before using flame near a finished core. Measure the plug-interface temperature throughout the planned braze sequence and cooling period. Set the acceptance limit from the printed material and sealing function; the nominal [~80 °C](PETG_TG) glass transition is not a permissible operating limit.

Use the qualified heat sink and flame shield at both coil joints, direct flame and exhaust away from the core, and monitor the interface. Recondition the protection between joints. Stop at the qualified temperature/time limit or if the protection loses contact. A wet rag can assist the heat sink, but a boiling-water temperature does not protect a material whose transition is below it.

After cooling, inspect both plugs and the foam boundary for distortion, gloss, dimpling, looseness or scorching. A damaged sealing/foam boundary requires replacement; neither appearance alone nor the schematic proves an undamaged internal stack.

### 5. Tie in the suction line

Position the cold core's coil-outlet stub (top of the wound coil — refrigerant exits as low-pressure gas heading to the compressor) next to the factory suction line cut. Join the two with the HVAC 1/4" OD ACR-grade slip coupling, sweat × sweat. Both lines are 1/4" OD, so the coupling is a direct sweat join. Braze dry — no flux (BCuP-5 self-fluxes on copper; see Inputs) — under the protective nitrogen flow established in step 3.

### 6. Tie in the capillary tube via pinch-swage

Position the cold core's coil-inlet stub (bottom of the wound coil) next to the capillary-tube end coming from the factory drier (cut to length at the evap-inlet end in step 3). The size mismatch — a 1/4" OD coil stub against a cap tube of ~0.031" bore ([`reference/ice-maker/`](/hardware/reference/ice-maker/README.md)) — uses a proposed **pinch-swage with the Knipex 86 01 180 Pliers Wrench**, rotating progressively around the 1/4" stub. Qualify insertion depth, capillary bore preservation, filler penetration and leak integrity on a representative joint before using it on the core. The 60° rotation suggestion is a forming trial, not an accepted metering-joint specification. Braze an accepted fit under protective nitrogen flow.

If total cap-tube length changes substantially relative to the donor's factory length (e.g., the new coil is significantly longer or shorter than the donor evaporator), a refrigeration tech recalculates cap length for the new load.

### 7. Leak-test and evacuate

Complete and cool all joints, then use the technician's dry-nitrogen leak test at a pressure and hold time justified by the circuit's weakest rated component. Record pressure, duration, temperature compensation and inspection of every new connection. These test limits are open; a pressure-vessel water-side hydro-test is not a refrigerant-circuit test specification. Depressurize the test gas before evacuation.

Use hydrocarbon-suitable evacuation equipment with its exhaust led to the technician's safe discharge location. Connect an absolute micron gauge at the system, where isolation leaves it reading the circuit rather than the pump. The manifold's compound dial does not measure deep vacuum. The owned Orion pump's 150-micron ultimate rating is not an R-600a suitability declaration or the vacuum achieved in this assembly.

The project's evacuation target is ≤[500 microns](VACUUM_TARGET), held for ≥[15 minutes](VACUUM_HOLD_FULL) while pumping, followed by a [15 minutes](VACUUM_HOLD_FULL) isolated record. Record the starting, intermediate and final absolute pressure. Some pressure rebound can occur in a tight system from oil and surface desorption; a literal zero-rise rule is not the acceptance criterion. The technician must commit the allowable isolated pressure/decay limit before charging. A rapid rise requires diagnosis of the setup or circuit; additional pumping alone does not repair a leak.

### 8. Mass-metered charge and final process closure

Hold until the finished-machine target charge and the qualified charging setup are documented. The donor label gives a baseline ([15 g](UNIT_A_CHARGE) Unit A / [23 g](UNIT_B_CHARGE) Unit B), not the redesigned loop's final charge. Evaporator volume alone does not establish charge or authorize an automatic overage.

Charge refrigerant-grade R-600a by mass under the technician's specified state/orientation and metering procedure. The Smart Weigh scale has 0.1 g resolution; verify its response with a check mass and keep hose forces off it. Account for refrigerant retained in hoses and connections: loss from the can is not automatically mass delivered to the circuit. Record starting mass, final mass, retained/returned mass and net delivered charge; the project's metering tolerance is [±1 g](RECHARGE_TOL) around the qualified target.

Use the specified final hermetic process closure or approved permanent access connection. The BPV31 is temporary: remove it as required by Supco's FAQ, then establish the final closure under the technician's qualified sequence. Do not apply a torch to a charged circuit. Leak-test the final closure and every threaded service connection after disconnection.

### 9. Initial run-up + leak check

Energize the compressor briefly. (Firmware enforces a [3-minute](OFF_TIME) minimum off-time per [`/hardware/reference/ice-maker/README.md`](/hardware/reference/ice-maker/README.md) "Powering and control"; boot also starts the timer.) Respect any longer donor/manufacturer restart requirement. Record current against the actual nameplate and the suction-probe trend; [~1 A](RUN_CURRENT) is an estimate, not the acceptance limit. Stop for a stalled/humming compressor, overload operation or leak indication.

Inspect every new joint, replacement drier connection, bypass closure and final process/service closure using the qualified leak-test method. An electronic detector must be suitable for R-600a and its sensitivity/proof check recorded. No bubbling or detector indication is required; the production leak-rate acceptance limit remains open.

A leak at any joint requires removal of the charge through the specified service access using the
handling route applicable to the completed dispenser. Its household design basis is recorded in
[`/business/regulatory.md`](/business/regulatory.md); the actual handling route must be
confirmed for the completed unit and service conditions. Recovery equipment must be suitable
for flammable refrigerants. After charge removal, the joint is re-cut, the protective
nitrogen flow from step 3 restored, the joint re-brazed, the loop re-vacuumed (step 7),
and re-charged (step 8). Field-repair-in-place with the charge still in is not the path.

## Output condition

A finished integrated refrigerant loop:

- Cold core's coil stubs brazed into the donor's loop (suction-line tie-in + cap-tube pinch-swage tie-in)
- Plug-interface thermal record meets the qualified limit, with plugs and foam boundaries undamaged
- Evacuation and [15 min](VACUUM_HOLD) isolated absolute-pressure record meet the qualified criterion, after reaching ≤[500 microns](VACUUM_TARGET)
- Charged to within [±1 g](RECHARGE_TOL) of target mass
- No detectable leaks at any joint
- Compressor runs and pulls the suction line cold on first run-up
- Hot-gas bypass solenoid, line, and tee discarded with the factory finger-plate evaporator
- Compatible replacement drier installed; final process closure/access connection leak-tested; temporary piercing valve removed

The integrated assembly — cold core + plumbed compressor + condenser — is now ready for enclosure install and final wiring.

## Open items

Procedure-level gaps that need answers before unit 1 ships:

1. **Finished-machine charge and metering.** A qualified technician must establish the charge for the assembled circuit under its specified load and ambient conditions, including hose inventory, frost distribution, suction condition and compressor current. The donor mass and approximate ledger allowance are not final targets.
2. **Service setup and circuit limits.** Record HC equipment approval, charge-removal route, nitrogen flow/pressure control, leak-test limits and the micron-gauge isolation/decay criterion.
3. **Metering and closure joints.** Qualify the capillary-to-coil joint, compatible replacement drier connection, bypass-branch deletion and final permanent process closure. Unit B's actual teardown topology and external compressor leads remain unrecorded.
4. **Plug heat protection.** Representative braze temperature data and a justified printed-stack limit are required before heating the installed core.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_refrigerant_loop_sync.py`

Manufacturer/service guidance consulted for this procedure:

- [Secop, Repair of Hermetic Refrigeration Systems](https://www.secop.com/fileadmin/user_upload/technical-literature/guidelines/repair_of_hermetic_refrigeration_systems_05-2018_desg620a202.pdf), §§2.1–2.4, 2.9 and 3.1. This is general hermetic-service guidance, not a manual for the harvested compressor.
- [Secop, Compressor Service for R600a/R290](https://www.secop.com/sustainability/natural-refrigerants/compressor-service), trained personnel, separate nitrogen clearing, protective flow and service-equipment requirements.
- [Supco BPV31](https://supco.com/web/supco_live/products/BPV31.html), installation instructions and FAQ on removal after repair.
- [Uniweld RHP regulators](https://www.uniweld.com/product/rhp-special-purpose-series/), RHP400 nitrogen listing and delivery range.
- [Orion VPH-BN0A-O1/O2 manual](https://orionmotortech.com/cdn/shop/files/new_VPH-BN0A-O1_VPH-BN0A-O2.pdf?v=10939169087783086859), compatible refrigerants; exact owned-model suitability remains to be documented.
- [EPA Section 608 venting rules](https://www.epa.gov/section608/stationary-refrigeration-prohibition-venting-refrigerants), end-use-specific exemptions.
