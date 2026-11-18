# Refrigerant Loop

Integrate the Antarctic Star HZB-12/Q refrigeration circuit with the wrapped evaporator, then establish the charge under a repeatable water load.

Design intent and component rationale live in [`/hardware/README.md`](/hardware/README.md) "Refrigeration". Donor-component teardown notes (compressor, condenser, capillary tube, drier, hot-gas bypass) live in [`/hardware/reference/ice-maker/README.md`](/hardware/reference/ice-maker/README.md). Assembly-time argon-purge safety is documented at [`/business/regulatory.md`](/business/regulatory.md) "Assembly-time safety — argon purge during brazing". This document is the procedure that ties them together. The illustrated sequence is [`refrigeration-guide.pdf`](/hardware/refrigeration-guide/refrigeration-guide.pdf).

## Scope

This is a single-session integration procedure: bring a finished cold core and a donor ice maker together at one workspace, open the donor's refrigerant loop, braze the cold core's coil stubs into the donor's loop, vacuum, charge, run up. All multi-day prep work (coil winding, foam pour) happens upstream in [`cold-core.md`](/hardware/assembly/cold-core.md) before this session begins.

Bring the [donor ice maker](/hardware/reference/ice-maker/README.md), the [finished cold core](cold-core.md) with its cured foam and accessible coil stubs, R-600a refrigerant, and the dry inert gas specified by the A3 service setup.

Out: a leak-tested and evacuated refrigeration loop with a weighed first trial charge. The loaded commissioning run establishes the operating charge.

Not in scope: cold-core assembly — coil winding, foam pour — all in [`cold-core.md`](/hardware/assembly/cold-core.md); electronics-bay control wiring, AC distribution, and bolting the compressor down to the enclosure floor ([`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) §3).

## Safety

R-600a (isobutane) is flammable. Sealed-system work requires training in
flammable-refrigerant service and a ventilated workspace with ignition sources
controlled. Confirm the R-600a service equipment and its pressure ratings before
opening the donor. Use recovery for the donor and the rebuilt loop. The
end-use scope of the venting exemption is recorded in
[business/regulatory.md](/business/regulatory.md).
[Secop hermetic service guide](https://www.secop.com/fileadmin/user_upload/technical-literature/guidelines/repair_of_hermetic_refrigeration_systems_05-2018_desg620a202.pdf)

**Hazard A — Refrigerant removal.** Recover the charge before cold-opening
the circuit. The A3 service procedure establishes when the circuit can be
opened or heated. Use a calibrated hydrocarbon detector. Gauge pressure at
atmosphere and odor give no clearance for hot work.

**Hazard B — Residual hydrocarbon at the braze.** R-600a can remain dissolved
in compressor oil after recovery. Clear residual refrigerant before hot work,
then maintain and verify dry inert flow through every tube segment being
heated. Protect the retained drier from moisture during open work.

**Hazard C — Braze heat conducted back into the printed shell.** Both loop joints are brazed on a copper stub that passes through the **PET-GF shell**, with foil exit seals and cured pour foam behind it. The installed tube routing sets the distance from the joint to the shell. Protect the shell, exit collars and foam from conducted heat before each braze.



The in-service hazard — a refrigerant leak post-build into a sealed compartment that contains an ignition source — is owned elsewhere. The compressor's terminal block and clip-on PTC module remain under the R-600a donor's own moulded power-box cover. The cover stays installed while the appliance connects only at the donor assembly's factory-external electrical interface; a missing, cracked, modified, loose, or incorrectly retained cover fails the build. The appliance adds no second sheet-metal shroud, and [`/business/regulatory.md`](/business/regulatory.md) carries the qualification still owed on the retained donor cover against the applicable 60335 enclosure provisions.

The AC switching relay lives on the electronics bay, away from the compartment, so its switching arc is not co-located with the leak. A hardware-only backstop is a BOJACK SF76E SEFUSE thermal fuse (, in series with the AC primary feeding the compressor) — a one-shot cutoff that opens on the temperature of its own case, so what makes it a cutoff is contact: its case is pinched against the outside flank of the donor cover by the printed [`fuse-clamp`](/hardware/printed-parts/refrigeration/fuse-clamp/), whose two leaves press into the air gap the power box hangs over its own mounting plate, so the clamp rides the compressor rather than the cabinet — plus an ACEIRMC MQ-6 LPG/iso-butane sensor lying along the floor of the refrigeration bay's open −X strip beside the compressor, card on edge parallel to the flank and mesh horizontal in the well the flank opens for it. The bay's floor is one connected pool — every dominant brazed-joint leak site (cap-tube pinch-swage at the evap inlet, slip coupling at the evap outlet, service connection and compressor process tube) drains into it, and dense R-600a spreads over the slab as one layer — so what the sensor answers to is height, not aim: its mesh comes out below the power box's floor, so the layer reaches the module before it reaches the covered terminal assembly. It drops from above into two grooved posts standing on the bay's own floor (`enclosure._west_cradle`), the module having no mounting hole of its own — both ON-ORDER per [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md) §6. Thermal fuse + gas sensor backstop the soft (firmware) cutoffs so a controller failure can't keep the compressor energized through a thermal or leak event.

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

- **A3 service and recovery setup:** confirm process-tube access, recovery equipment and cylinder, hose and fittings for R-600a and the service pressures. Plan the final sealed closure before opening the donor.
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
- **Dry gas rig:** match the regulator to its specified gas. Uniweld lists the RHP400 for nitrogen. Record the actual dry inert inlet, open outlet and regulator in the A3 service plan. [Uniweld specifications](https://www.uniweld.com/product/nitrogen-regulators/)
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

### 2. Recover the factory charge

Isolate power. Use qualified process-tube access and recover the factory
R-600a into a suitable recovery cylinder. Confirm recovery and residual
refrigerant clearance by the A3 service method before opening any tube.
Record recovered mass as a service observation. Refrigerant can remain in
oil and the recovery set, so use the certification rating for the first
trial rather than the cylinder gain.

### 3. Separate the finger plate and verify each purge path

Trace and tag the sealed donor. Identify the two evaporator separations and
follow the hot-gas branch back to its discharge tee. Confirm the retained
compressor-to-condenser route and record the actual junction, materials and
approved rejoin in the A3 service plan. Use the guide's branch diagram to
identify what stays.

After recovery and clearance, cold-cut the suction and capillary at the old
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

Weigh the R-600a transfer after recovery and evacuation. Use an approved,
low-volume delivery assembly. Determine net grams past the circuit valve,
including the change in refrigerant inventory of hoses, valves and
instruments. Support the hose independently and check scale repeatability in that position. The display resolution alone gives no measure of
transfer accuracy.

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
clearance procedure. Recover through the qualified service connection before
opening a leaking joint. Restore the inert flow and heat protection,
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

### Model the installed inventory

Use the [EVAP-01 drawing](/hardware/cold-core-layout/evaporator-coil-drawing.pdf)
for the finished tube, subtract the actual tail trim and use bore area
times centreline length. In each boiling segment, multiply its internal
volume by `(1 - alpha) × liquid_density + alpha × vapor_density`, where
`alpha` is the fraction of the volume occupied by vapor. Estimate the
capillary discharge vapor mass fraction from the high-side liquid
enthalpy after the bonded heat exchanger and the saturation enthalpies at
evaporating pressure. Integrate from that inlet quality to dryout. Add
the dry outlet with vapor density. The worked guide example uses the
homogeneous case with slip ratio `S = 1`
and the Zivi case with `S = (liquid_density / vapor_density)^(1/3)`.
For local vapor mass fraction `x`, use
`alpha = 1 / (1 + ((1 - x) / x) × (vapor_density / liquid_density) × S)`.
The inlet tail is at inlet quality, the winding rises to dryout and the
outlet tail contains vapor. The estimates illustrate sensitivity to phase
distribution. Bottom feed, vertical rise,
oil and cycling can change the distribution.
[NIST R-600a properties](https://webbook.nist.gov/cgi/fluid.cgi?ID=C75285&Action=Page) · [ORNL void-fraction models](https://info.ornl.gov/sites/publications/Files/Pub57653.pdf)

The inventory change is the new coil and tails less the removed finger
plate and hot-gas branch, plus the change in liquid and vapor stored in
the retained condenser, drier and lines and in compressor oil. Small
changes in condenser liquid volume can dominate the calculation. Record
actual tube and condenser geometry at harvest. A volume measurement of the
isolated, recovered and discarded evaporator tightens the removed-volume
term. Keep that measurement off the retained refrigerant path. A full
cycle model also needs a compressor map, capillary flow with the bonded
heat exchanger, air and water heat transfer, and measured pressures and
temperatures. Use a charged trial to obtain those operating anchors.
[R-600a capillary inlet experiments](https://doi.org/10.1016/j.ijrefrig.2019.02.006)

### Repeat the water load and instrument the loop

Use the same high-reed fill, similar initial wall and supply-water
temperatures, and the same condenser airflow configuration and measurement
fixture. Keep the ordinary temperature, gas and compressor protections
active. Time the wall probe through the window in the guide. Record the
guard that ended a short run. Measure water immediately after a repeatable
pour in a glass using the immersion probe. Wall pull-down and dispensed
water temperature describe different parts of the cooling performance.
Repeat at the cold end and after a normal restart.
[Bench guide](/hardware/refrigeration-guide/refrigeration-guide.pdf)

Clamp and insulate a tube probe right after the evaporator and before the
bonded capillary/suction heat exchanger. Put a second one by the compressor
inlet after that exchanger. At each point use local running pressure to read
the R-600a saturation temperature and subtract it from the contact temperature
to obtain superheat. Use absolute pressure, or add the actual local barometric
pressure to gauge pressure. The process-tube pressure can represent compressor
suction if verified. Used at the evaporator outlet it gives apparent superheat,
biased high by suction-line pressure drop. Record pressure accuracy and
probe contact error with the readings. The installed coil probe measures
tube temperature for the freeze guard. A cold inlet and a warm outlet
with high superheat can indicate early dryout. Frost advancing along
the return calls for checking compressor-inlet superheat promptly. Frost
itself shows surface temperature and humidity. Read the probes with the
foam in its installed state.

On a qualified instrumented bench, read high-side pressure and temperature
at the condenser outlet upstream of the drier and bonded heat exchanger.
Saturation temperature less tube temperature is subcooling. Also compare
tube temperature across the drier. A suction connection alone gives no
subcooling measurement. If the evidence is ambiguous, add instrumentation
during a depressurized service cycle and repeat the same load.
[NIST pressure-temperature data](https://webbook.nist.gov/cgi/cbook.cgi?ID=C75285&Mask=225#Thermo-Phase) · [ASHRAE capillary systems](https://handbook.ashrae.org/Handbooks/R26/SI/r26_ch11/r26_ch11_si.aspx)

### Choose the next measured charge

- **Coil dries out early under load.** High outlet superheat, slow wall pull-down
  and poor delivered-water cooling and little or no condenser-outlet subcooling support an underfeed
  caused by low inventory. After leak, airflow and restriction checks, try
  the guide's single weighed increment within the compressor and test limits.
  Compare the same water window. Keep the change only if cooling improves
  and compressor-inlet vapor margin holds near the cold end.
- **Coil starves with liquid still on the high side.** Preserved or rising
  subcooling, an abnormal temperature drop at the drier or intermittent
  feed suggest a capillary, crushed joint, drier or moisture fault. Diagnose
  these before changing charge. If the clean factory capillary cannot meet
  both load and inlet-superheat limits at any tested charge, characterize its
  flow before changing its geometry. Restart the charge trials after any change.
- **Cooling reaches the coil but little reaches the water.** Check water fill,
  stratification or ice, contact probes and the coil-to-vessel bond. Investigate
  fan and condenser airflow when head conditions rise or capacity drops.
- **Return approaches saturation or the compressor alarms.** Stop for near-zero
  compressor-inlet superheat within uncertainty, liquid return, abnormal
  current or sound, lost airflow, a leak indication or repeated protection
  trips. Resolve the cause before restarting. If the evidence establishes
  excess charge, recover with A3 equipment and weigh back the lower mass.
  Keep recovery and evacuation conditions repeatable, including oil
  equilibration. Never trim the mass by cracking a valve.

Use the lowest measured mass that repeats the required water pull-down,
cold-water delivery and refill recovery with compressor-inlet superheat above
instrument uncertainty and within the verified compressor limits. Check
normal restart, cold end of cycle and intended hot and light-load conditions.
If the first trial meets those criteria, keep it. Finalize and leak-test the
process-tube closure, then record the charge and trace with the unit.
[Capillary and charge optimization study](https://www.sciencedirect.com/science/article/abs/pii/S014070072030205X)

## Open items

- Establish the first loaded charge and permitted trial envelope from the installed
  donor hardware and the charge log. Publish the final mass after the repeat tests.
- Confirm the A3 bench access and equipment and the final sealed process-tube closure.
