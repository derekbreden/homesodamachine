# Wiring

The production procedure for executing every electrical run in the appliance — chassis ground bonds, AC mains, the [12 V](DC_BUS_V) trunk, and signal lines — once the enclosure is plumbed and the electronics shelf is installed. The schedule of runs is [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md); this doc is the build-order procedure for executing that schedule, with AC, DC, and signal runs interleaved by physical zone because that is how the wires actually pass through the cabinet (the compressor shroud's grommet alone carries [18 AWG](SHROUD_SJOOW_AWG) switched mains alongside its own chassis bond).

The AC + DC + signal sides are kept in one document, not three, because the runs are interleaved physically: a single zip-tied bundle exiting the electronics shelf carries [16 AWG](AWG_AC_MAIN) mains, [18 AWG](AWG_AC_BRANCH) [12 V](DC_BUS_V), and [22 AWG](AWG_DC_BRANCH) signal in close proximity. Splitting the procedure across documents would lose that adjacency. Topology lives in [`../wiring/power.mmd`](../wiring/power.mmd), [`../wiring/esp32-pinout.mmd`](../wiring/esp32-pinout.mmd), and [`../wiring/valve-control.mmd`](../wiring/valve-control.mmd). This doc references those by run number rather than restating per-wire specs.

## Scope

In: a chassis that exits [`internal-plumbing.md`](internal-plumbing.md) — cold core dropped into the enclosure, valve manifold mounted, all water + CO2 + flavor lines plumbed but unwired; electronics shelf installed per [`electronics-shelf.md`](electronics-shelf.md) + [`enclosure-mechanical.md`](enclosure-mechanical.md), populated with C14 inlet, AC distribution block, Mean Well IRM-90-12ST PSU, both Teyleten relays, ESP32-DevKitC-32E, both MCP23017s, both ULN2803A modules, L298N board, [5 V](LOGIC_V) + [3.3 V](MCU_V) regulators, and ground bus — all mounted but unpowered, no field-side wires landed; compressor + condenser fan installed in their middle-bottom and side-wall positions, compressor shroud installed with its grommet open and its chassis-ground stud unbonded. Plus the bagged faucet-and-umbilical sub-assembly (output of [`faucet-and-umbilical.md`](faucet-and-umbilical.md)) brought to the wiring bench with its rear-panel-end Cat6 conductors broken out and accessible — the bag itself stays loose (the umbilical's tube tails do NOT push into the PP1208E bulkheads at the factory; that's the customer's install step), only the rear-panel-end Cat6 gets terminated at the electronics shelf during this procedure.

Wire stock and small parts: [16 AWG](AWG_AC_MAIN) silicone hookup wire for AC + ground (green for ground, plus the appliance-wire colors used in [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) §AC mains); [18 AWG](AWG_AC_BRANCH) silicone for the 18 AWG runs in the AC schedule; [18 AWG](SHROUD_SJOOW_AWG) SJOOW 3-conductor jacketed cable for the shroud pass-through; [16 AWG](AWG_AC_MAIN) hookup for the [12 V](DC_BUS_V) trunk, [22 AWG](AWG_DC_BRANCH) for branch DC and signal; JST XH [2.54 mm](JST_PITCH) housings + pre-crimped pigtails (CQRobot B0F6C7X5CR + Keszoox B0F8HMQRRN, per [`../bom.md`](../bom.md) §11); some JST XH pigtails pre-built at the electronics-shelf step and ready to pop into housings; ferrules sized for [16/18/22 AWG](AWG_TRIPLE); ring terminals for the ground bus + shroud stud; female-disconnect (Faston) terminals for the compressor terminal block, diaphragm pump, and condenser fan; spiral wrap + zip ties for bundling; Wago 221 lever-nut blocks (or screw terminal block, per the open item in [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) "What's not yet decided") for the AC distribution block and the [12 V](DC_BUS_V) distribution block; cable for the front-face display run (SIG-7 to the detachable ESP32-S3) — internal to the appliance from the electronics shelf to the front face, with the display-end cord pay-out per [`../printed-parts/enclosure/front-panel/README.md`](../printed-parts/enclosure/front-panel/README.md) "S3 detach mechanism".

Out: every run in [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) executed and continuity-tested. AC runs AC-1 through AC-6 landed, with the C14 ground pin bonded to the central chassis-ground point and onward to the four discrete chassis-ground targets (pressure vessel, compressor body, compressor shroud, faucet under-counter SS plate). Low-voltage logic runs LV-1, LV-2, LV-3 landing the [3.3 V](MCU_V) control side of the relays. DC runs DC-1 through DC-9, with DC-9 wired as the low-side switched [12 V](DC_BUS_V) condenser fan through ULN2803A #2 channel 5 (same pattern as the solenoid coils). Signal runs SIG-1 through SIG-4 + SIG-7 + SIG-8 + SIG-9 landed at both ends, with the I2C trunk on the electronics shelf using JST XH pigtails. SIG-7 (ESP32-S3 detachable) is a [~1 m](SIG_DISPLAY_LEN) internal run from the shelf to the front face; SIG-4 (DIGITEN flow meter) rides the umbilical up to the above-counter faucet head. A dielectric / continuity check passes on the AC side. The chassis is safe to apply [120 VAC](AC_LINE_V) but no power is applied — that step is [`firmware-and-commissioning.md`](firmware-and-commissioning.md).

Not in scope: applying [120 VAC](AC_LINE_V); flashing firmware; bringing up the [12 V](DC_BUS_V) rail; any sensor probe-into-water service. Those happen in [`firmware-and-commissioning.md`](firmware-and-commissioning.md). The compressor terminal block's clip-on PTC start relay / overload module is already mated to the compressor body — that's a donor-side subassembly preserved during teardown and ridden through unchanged ([`../harvested/ice-maker/README.md`](../harvested/ice-maker/README.md) "Powering and control") — so terminal-block wiring here is the appliance-side leads landing on already-populated spade terminals, not the start-relay/overload install itself.

## Inputs per appliance

Wire stock, connectors, and termination consumables are in [`../bom.md`](../bom.md) §11 (low-voltage wiring + connectors), §14 (AC stock + ground bonding), and §13 (mechanical attach for shroud + chassis bonding). Status in [`../purchases.md`](../purchases.md). The runs themselves are in [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) §"Run table"; gauges, run lengths, terminations, and per-run notes are in that table. This procedure does not restate them.

Tooling: ratcheting crimper for insulated and uninsulated terminals + ferrules + Faston disconnects + JST XH (one tool covers all four with the appropriate die per terminal family); wire strippers sized for [16/18/22 AWG](AWG_TRIPLE); small flat screwdriver for Wago 221 levers and the relay screw terminals; PEX-style sidecutters for trimming; a hot-glue gun for strain relief at intermediate tie points where the run crosses a printed-part edge; cable-tie tensioner (optional); multimeter for the continuity + dielectric checks at step 4.

## Procedure

The execution order is chassis-ground bonding first, then AC, then the DC trunk, then signal, with a static dielectric / continuity check on the AC side gated between AC completion and DC energization (no power is applied during the check — it is a multimeter cold check). Within each phase, runs are executed in the run-number order from [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md).

### 1. Chassis-ground bonds (single-point ground at the electronics shelf)

Before any current-carrying conductor lands, establish the single-point chassis ground. The appliance has no metal chassis backbone, so chassis grounding is via discrete green wires from the four exposed metal parts back to a central ground bus on the electronics shelf. Per [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) "Grounding strategy" all bonds are [16 AWG](AWG_AC_MAIN) green-insulated, ring terminal at the bus end, ring or fork at the target end.

Bond, from each target to the ground bus on the electronics shelf:

- **Pressure vessel** — ring terminal under the M3 SHCS that already secures one of the foam-shell top-cap screws to a heat-set insert at the cold-core ([`cold-core.md`](cold-core.md)) top face. Pick a top-cap screw position that sits closest to the electronics shelf so the green wire run is short. Route up through the cold-core / electronics-shelf boundary in the existing wire path used by signal run SIG-1.
- **Compressor body** — ring terminal at one of the compressor's M5 mounting feet (the same foot already secures one of the compressor-shroud mounting tabs through its M5→M3 step-down adapter washer per [`../cut-parts/compressor-shroud/README.md`](../cut-parts/compressor-shroud/README.md) "Penetrations" item 2). Route outside the shroud — this bond does not enter the shroud cavity, only the compressor body.
- **Compressor shroud** — ring terminal at the Ø ~[6 mm](GND_STUD_HOLE) PEM chassis-ground stud on the shroud's side wall ([`../cut-parts/compressor-shroud/README.md`](../cut-parts/compressor-shroud/README.md) "Penetrations" item 3). This is run AC-6 in [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md).
- **Faucet under-counter SS plate** — ring terminal under one of the bolts that already retains the under-counter plate ([`../cut-parts/faucet/touch-flo-under-counter-plate/`](../cut-parts/faucet/touch-flo-under-counter-plate/)) against the underside of the countertop. Run rides the umbilical alongside the Cat6 conductors back into the cabinet. Length is whatever the umbilical length plus [200 mm](CABINET_SLACK) of cabinet-side slack.

At the electronics-shelf end, all four bonds terminate on a single ring-terminal stack at the ground bus. The bus itself is bonded to the C14 inlet's earth pin by run AC-1's green conductor (executed in step 2).

Continuity check after this step: ohms-low between every bonded metal surface and the bus, before any other wire lands.

### 2. AC mains (C14 → distribution → relay #1 → compressor + PSU)

Execute the AC runs in the order they appear in [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) "AC mains (120 V)": AC-1, AC-2, AC-3, AC-4, AC-5, AC-6. AC-6 is the shroud chassis-ground done in step 1; it is the third conductor of the 3-conductor bundle through the shroud's Heyco SB-500-6 grommet, so the bundle gets built whole in this step even though the green conductor was landed at the bus end in step 1.

Specific to the shroud pass-through (AC-4 + AC-5 + AC-6): pre-build a single [18 AWG](AWG_AC_BRANCH) SJOOW 3-conductor jacketed lead, [~400 mm](SHROUD_LEAD_LEN) long, with the H_switched (from Teyleten relay #1 NO contact), N (from AC distribution block), and G (from electronics-shelf ground bus) conductors. Pull the bundle through the Heyco snap bushing in the shroud side wall as one cable — the snap bushing's [5.6](BUSHING_LOW)–[6.4 mm](BUSHING_HIGH) cable-OD range is sized for [18 AWG](SHROUD_SJOOW_AWG) SJOOW per [`../cut-parts/compressor-shroud/README.md`](../cut-parts/compressor-shroud/README.md) "Penetrations" item 1. Inside the shroud, fan the three conductors out the last [~50 mm](SHROUD_FAN_OUT): H_switched and N each take a female disconnect onto the appropriate compressor terminal-block spade (the donor's terminal block + clip-on PTC start relay/overload module is already populated and live as-is from harvest, see [`../harvested/ice-maker/README.md`](../harvested/ice-maker/README.md) "Powering and control"); G takes a ring terminal at the compressor body's mounting-foot bond from step 1.

At the shelf end of the bundle: H_switched lands on the Teyleten relay #1 NO terminal; N lands at the AC distribution block N pole; G lands on the ground bus. All AC distribution-block landings use ferrules into the Wago 221 lever-nut block (or screw terminal block — open item in [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) "What's not yet decided"). All relay screw-terminal landings use fork terminals.

AC-1 (C14 → distribution block) is short — [~50 mm](AC1_LEN) — and is built with ferrules at both ends. AC-2 (distribution block → PSU primary) is [~100 mm](AC2_LEN), ferrule at the block, ring or fork at the PSU; the PSU's chassis ground is bonded by AC-2's green conductor onto the PSU's earth lug. AC-3 is the short hot-pickup leg from the distribution block into relay #1's contact common.

Color discipline: [16 AWG](AWG_AC_MAIN) silicone, black for hot, white for neutral, green for ground (the schedule does not specify a switched-hot vs unswitched-hot color distinction — open item below).

### 3. Static dielectric / continuity check on the AC side

After step 2 and before any DC conductor lands, cold-check the AC wiring with the C14 inlet **disconnected from line**. No [120 VAC](AC_LINE_V) is applied — this is a multimeter check, not a hipot.

- **Continuity (ohms-low):** C14 earth pin to every metal-part chassis-ground target from step 1. C14 hot pin to AC distribution block H pole. C14 neutral pin to AC distribution block N pole. AC distribution block H pole to Teyleten relay #1 common. With relay #1 manually held closed (firmware not yet present — use a jumper across the input opto), distribution-block H to compressor terminal-block hot spade.
- **Open (ohms-high):** Hot to neutral across the AC primary loop, both with relay #1 open and with relay #1 closed (with the compressor's motor windings in circuit, this last reads the winding resistance, not open — confirm it matches the donor compressor's nameplate winding resistance, ~[10](WINDING_R_LOW)–[30 Ω](WINDING_R_HIGH) for a [100 W-class](COMP_CLASS_W) hermetic, rather than a short).
- **Open (ohms-high):** Every AC current-carrying conductor (H, N, switched H) to every chassis-ground target. No leakage path. This is the check that catches a hot leg landed on a ground terminal or a wire pinched into the shroud's grommet edge.

The goal is to catch wrong-leg landings before the PSU's [12 V](DC_BUS_V) rail brings up the controllers — diagnosing a backwards landing with the firmware end of the system also live is a much messier failure. If any check fails, find and fix it before step 4.

### 4. [12 V](DC_BUS_V) trunk + branch DC (DC-1 through DC-9)

Execute the DC runs in the order they appear in [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) "12 V distribution": DC-1 (PSU output → [12 V](DC_BUS_V) distribution block on the shelf) first, then DC-2 through DC-9 from the block outward. The block itself is the same Wago 221 (or screw terminal block, per the open item) form factor used for AC distribution; the [12 V](DC_BUS_V) block has its own lever-nut stack distinct from the AC stack to avoid the topology mistake of co-mingling.

DC-3 (relay #2 → SeaFlo diaphragm pump) and DC-5 (L298N → Kamoer pumps) both leave the shelf and route through the cabinet. DC-5's cabinet-side run lands at the pump-cartridge magnetic pogo interface ([`../bom.md`](../bom.md) §8 — the field-replaceable pump cartridge's tool-free disconnect), not at the pump itself, so terminate the DC-5 wires on the manifold-side pogo pad rather than on a wire-to-wire splice.

DC-7 (ULN2803A outputs → 12 solenoid coils on the manifold) ships as a single ~24-conductor bundle from the electronics shelf to the manifold. The bundle is either zip-tied loose wires (12× of the Keszoox B0F8HMQRRN pre-crimped [50 cm](KESZOOX_LEN) pigtails, one per valve) or a small ribbon — the open item in [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) "What's not yet decided" — and fans out to a female disconnect per valve at the manifold.

DC-9 (condenser fan) is wired identically in pattern to the solenoid coils: [12 V](DC_BUS_V) + side ties to the [12 V](DC_BUS_V) distribution block, ULN2803A #2 channel 5 sinks the − return when MCP23017 0x21 PA4 commands it, flyback path through the ULN2803A's integrated diode to COM (already at [12 V](DC_BUS_V) via DC-6 — no separate flyback diode added at the fan). See [`../wiring/power.mmd`](../wiring/power.mmd) and [`../wiring/valve-control.mmd`](../wiring/valve-control.mmd). The fan disconnects use female Fastons so the side-wall fan can be unplugged for service without unsoldering.

DC-6 ([12 V](DC_BUS_V) trunk → both ULN2803A COM pins) lands at each ULN module's COM pin header. Both ULNs share the same trunk feed via a JST XH pigtail tee on the shelf rather than two separate runs from the distribution block.

DC-8 ([12 V](DC_BUS_V) → [5 V](LOGIC_V) regulator input) is the only path into the regulator stack; the [3.3 V](MCU_V) regulator chains from the [5 V](LOGIC_V) output per [`../wiring/power.mmd`](../wiring/power.mmd) ("regulated logic-level supplies") and does not get a separate [12 V](DC_BUS_V) feed.

### 5. Low-voltage logic + signal (LV-1 through LV-3, SIG-1 through SIG-9)

Execute the LV and SIG runs from [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) "Low-voltage logic" and "Sensors and signal" tables. Many of these stay entirely on the electronics shelf and are short JST XH pigtail hops between modules; others leave the shelf to the cold core, the manifold, or the umbilical.

On-shelf hops, JST XH [2.54 mm](JST_PITCH) via the pre-crimped CQRobot bonded ribbons (B0F6C7X5CR):

- **LV-1, LV-2** — ESP32 GPIO 14 / GPIO 4 + GND, Dupont female on the ESP32 side, JST XH on the relay-module side (the Teyleten module's IN pin is a pin header). Two short runs, [~150 mm](LV_SHORT_LEN).
- **LV-3** — [5 V](LOGIC_V) regulator output → both Teyleten relay modules' VCC pins via a tee. Single 4-pin XH housing on the regulator side, fans out to two 2-pin connectors at the relay modules.
- **SIG-8** — ESP32 GPIO 21 / 22 (I2C) + [3.3 V](MCU_V) + GND to DS3231 RTC + both MCP23017s on a shared bus. A 4-pin XH housing on the ESP32, daisy-chained to the RTC's 6-pin XH header (VCC / GND / SDA / SCL / SQW / 32K, only the first four used) and then onward to each MCP23017's 4-pin I2C header. Keep stub lengths short — this is the bus that carries the valve + reservoir-level traffic.

Cabinet-side runs leaving the shelf:

- **SIG-1** — DS18B20 1-wire bus, [22 AWG](AWG_DC_BRANCH), [~600 mm](SIG_COLD_CORE_LEN) to the back of the cold core. Two DS18B20 probes are bussed in parallel: tank-wall probe + evap-suction probe ([`../wiring/esp32-pinout.mmd`](../wiring/esp32-pinout.mmd) "Refrigeration"). [4.7 kΩ](PULLUP_R) pull-up between data and [3.3 V](MCU_V) at the ESP32 end. Probes land at the cold core's exit per [`cold-core.md`](cold-core.md) — the tank-wall probe is already clamped to the vessel OD and the evap-suction probe is already bonded to the suction line during refrigerant-loop integration ([`refrigerant-loop.md`](refrigerant-loop.md)).
- **SIG-2, SIG-3** — carbonator reed switches (low + high), INPUT_PULLUP at the ESP32. Two [24 AWG](AWG_SIGNAL) twisted pairs (switch + GND) routed alongside SIG-1 in the same cold-core-exit cable channel.
- **SIG-4** — DIGITEN flow meter, [24 AWG](AWG_SIGNAL), [~1 m](SIG_UMBILICAL_LEN). Pulse interrupt at the ESP32. Flow meter sits in the post-faucet line on the under-counter side; cable routes through the cabinet up the umbilical (the only signal in the umbilical now that SIG-5/SIG-6/SIG-7 have moved out).
- **SIG-7** — UART trunk to the front-face ESP32-S3 rotary display. Runs from the ESP32 (GPIO 15 TX / 34 RX + [5 V](LOGIC_V) + GND) to the detachable S3 on the front face — the display-end cord pays out behind the panel as the customer pulls the display per [`../printed-parts/enclosure/front-panel/README.md`](../printed-parts/enclosure/front-panel/README.md) "S3 detach mechanism". The run is internal to the appliance (not through the umbilical); shelf end terminates via a short JST XH pigtail into the ESP32, display end terminates at the display's pin header.
- **SIG-9** — backflow vent moisture sensor, [24 AWG](AWG_SIGNAL), [~600 mm](SIG_COLD_CORE_LEN) to the drip pan inside the cabinet. Per [`../future.md`](../future.md) "Backflow vent monitoring" and [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) SIG-9: ESP32 pin assignment is not yet committed in [`../wiring/esp32-pinout.mmd`](../wiring/esp32-pinout.mmd). Lay the wire and leave the shelf end un-landed until the pin is assigned, or land it on an unassigned spare GPIO with a labeled flying lead that firmware-and-commissioning can re-land — open item below.

Continuity-test each signal run end-to-end before zip-tying down — sensor leads inside zip-tied bundles are painful to re-do.

### 6. Bundle, route, and strain-relieve

Bundle by zone, not by signal type, so that each cable management point handles one cluster of runs rather than separated by class:

- **Shelf-to-cold-core bundle** — SIG-1 (DS18B20 bus), SIG-2 + SIG-3 (carbonator reeds), the pressure-vessel chassis-ground bond, and any of the reservoir-reed harnesses ([`../printed-parts/cold-core/reservoir/level-sensing.md`](../printed-parts/cold-core/reservoir/level-sensing.md)) into a single spiral-wrapped bundle exiting the back of the shelf and routing along the back wall of the enclosure to the cold core's penetrations.
- **Shelf-to-manifold bundle** — DC-7 (24 conductors to the solenoid manifold), DC-3 (diaphragm pump), DC-5 (peristaltic pump pogo pad), and DC-4 (L298N feed). Spiral-wrap and zip-tie; fan-out happens at the manifold.
- **Shelf-to-shroud bundle** — the [18 AWG](SHROUD_SJOOW_AWG) SJOOW jacketed lead from step 2 is its own bundle (a single jacketed cable); no spiral wrap, just zip-tie tie-down points to keep the cable from migrating against the shroud's grommet edge.
- **Shelf-to-front-face bundle** — SIG-7 (ESP32-S3 detach cord) routed forward through the enclosure interior to the front face. The cable's display-end pays out behind the panel when the customer detaches the S3; cord-retention scheme per [`../printed-parts/enclosure/front-panel/README.md`](../printed-parts/enclosure/front-panel/README.md) "S3 detach mechanism".
- **Shelf-to-umbilical bundle** — SIG-4 (flow meter) and the under-counter SS plate chassis-ground bond. Both ride the umbilical together up to the under-counter zone; spiral-wrap on the shelf side, separator at the umbilical's bulkhead.
- **Shelf-to-condenser-fan bundle** — DC-9 alone; short [~400 mm](DC9_LEN) run along the side wall. Female Fastons at the fan.

Strain relief at every cable transition: shelf exit edge, cold-core penetration, manifold entry, shroud grommet (the Heyco SB-500-6 itself is the strain relief on that one), umbilical bulkhead. Use the existing printed-part features where they exist; cable-tie anchors are placed below the cable rather than above, so a downward pull on the cable is resisted by the anchor in compression. Open item below on the systemic strain-relief approach.

## Output condition

A wired but unenergized chassis:

- All four chassis-ground bonds (pressure vessel, compressor body, compressor shroud, faucet under-counter SS plate) land at the single ground bus on the electronics shelf; the bus is bonded to the C14 inlet's earth pin
- All AC runs (AC-1 through AC-6) executed and continuity-tested; the AC dielectric / continuity check (step 3) passes — no hot-to-ground leakage path, no swapped legs
- All DC runs (DC-1 through DC-9) executed; the [12 V](DC_BUS_V) trunk is contiguous from PSU output to every load; DC-9 wired as low-side ULN2803A switching for the condenser fan
- All LV runs (LV-1 through LV-3) executed; the [3.3 V](MCU_V) control side of both Teyleten relays is wired to the ESP32 GPIOs and powered from the [5 V](LOGIC_V) regulator
- All SIG runs (SIG-1 through SIG-9) landed at both ends, except SIG-9 if its ESP32 pin is still un-assigned (then landed on a labeled spare GPIO pending the assignment)
- SIG-7 (ESP32-S3 detach cord) seated at the shelf and landed at the front face display
- Wire bundles are spiral-wrapped or zip-tied by zone, with strain relief at every transition
- The chassis is safe to apply [120 VAC](AC_LINE_V) but no power has been applied

The chassis is the input to [`firmware-and-commissioning.md`](firmware-and-commissioning.md): plug in the C14 cord, flash the ESP32 and the ESP32-S3, bring up the rails, walk through each subsystem under firmware control.

## Open items

Procedure-level gaps that need answers before unit 1 ships:

1. **Switched-hot vs unswitched-hot color convention.** [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) does not specify how to color-code the switched-hot leg downstream of Teyleten relay #1 (AC-4) vs the unswitched-hot leg upstream of the relay (AC-3) when both run in the same bundle leaving the AC distribution block. Black-on-black is functional but unreviewable. Working option: red for switched-hot, black for unswitched-hot, white for neutral, green for ground — pick a convention and roll it back into the AC schedule.
2. **Umbilical cable selection.** With the display runs (SIG-6, SIG-7) and the KRAUS air switch (SIG-5) all gone, the umbilical now carries only SIG-4 (flow meter, 3 conductors) plus the under-counter SS plate ground bond. The Cat6 oversize that made sense when carrying two display trunks is no longer needed — pick a thinner cable family for the umbilical, or keep Cat6 and accept the spare capacity.
3. **Strain relief for bundles crossing the cold-core boundary.** The shelf-to-cold-core bundle enters the foam-shell at a printed pass-through; the bundle wants a defined strain-relief approach (a printed cable clamp on the foam-shell? a glue blob? a P-clip mounted to the back of the electronics shelf?) rather than relying on zip-tie friction alone. Pick a method and roll it into the foam-shell or the electronics-shelf printed parts.
4. **SIG-9 pin assignment.** Per [`../wiring/esp32-pinout.mmd`](../wiring/esp32-pinout.mmd) the backflow-vent moisture sensor's ESP32 GPIO is not yet committed. Either land the assignment in the pinout diagram before unit 1 wiring, or carry SIG-9 as a flying lead on a known spare GPIO and re-land it during commissioning.
5. **AC distribution-block hardware.** Open per [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) "What's not yet decided": Wago 221 vs. screw terminal block vs. PCB-mounted block. Same question applies to the [12 V](DC_BUS_V) distribution block. This procedure assumes Wago 221 because it is the fastest hand-build; pick the production form before unit 1.
