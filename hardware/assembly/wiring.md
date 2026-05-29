# Wiring

The production procedure for executing every electrical run in the appliance — chassis ground bonds, AC mains, the [12 V](DC_BUS_V) trunk, and signal lines — once the enclosure is plumbed and the electronics shelf is installed. The schedule of runs is [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md); this doc is the build-order procedure for executing that schedule, with AC, DC, and signal runs interleaved by physical zone.

A single zip-tied bundle exiting the electronics shelf carries [16 AWG](AWG_AC_MAIN) mains, [18 AWG](AWG_AC_BRANCH) [12 V](DC_BUS_V), and [22 AWG](AWG_DC_BRANCH) signal in close proximity. Topology lives in [`/hardware/wiring/power.mmd`](/hardware/wiring/power.mmd), [`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd), and [`/hardware/wiring/valve-control.mmd`](/hardware/wiring/valve-control.mmd).

## Scope

In: a chassis that exits [`internal-plumbing.md`](internal-plumbing.md) — cold core dropped into the enclosure, valve manifold mounted, all water + CO2 + flavor lines plumbed but unwired; electronics shelf installed per [`electronics-shelf.md`](electronics-shelf.md) + [`enclosure-mechanical.md`](enclosure-mechanical.md), populated with C14 inlet, AC distribution block, Mean Well IRM-90-12ST PSU, both Teyleten relays, ESP32-DevKitC-32E, both MCP23017s, both ULN2803A modules, L298N board, [5 V](LOGIC_V) + [3.3 V](MCU_V) regulators, and ground bus — all mounted but unpowered, no field-side wires landed; compressor + condenser fan installed in their middle-bottom and side-wall positions, compressor shroud installed with its grommet open and its chassis-ground stud unbonded. Plus the bagged faucet-and-umbilical sub-assembly (output of [`faucet-and-umbilical.md`](faucet-and-umbilical.md)) brought to the wiring bench with its rear-panel-end Cat6 conductors broken out and accessible; only the rear-panel-end Cat6 gets terminated at the electronics shelf during this procedure.

Wire stock and small parts: [16 AWG](AWG_AC_MAIN) silicone hookup wire for AC + ground (green for ground, plus the appliance-wire colors used in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) §AC mains); [18 AWG](AWG_AC_BRANCH) silicone for the 18 AWG runs in the AC schedule; [18 AWG](SHROUD_SJOOW_AWG) SJOOW 3-conductor jacketed cable for the shroud pass-through; [16 AWG](AWG_AC_MAIN) hookup for the [12 V](DC_BUS_V) trunk, [22 AWG](AWG_DC_BRANCH) for branch DC and signal; JST XH [2.54 mm](JST_PITCH) housings + pre-crimped pigtails (CQRobot B0F6C7X5CR + Keszoox B0F8HMQRRN, per [`/hardware/bom.md`](/hardware/bom.md) §11); ferrules sized for [16/18/22 AWG](AWG_TRIPLE); ring terminals for the ground bus + shroud stud; female-disconnect (Faston) terminals for the compressor terminal block, diaphragm pump, and condenser fan; spiral wrap + zip ties for bundling; Wago 221 lever-nut blocks for the AC distribution block and the [12 V](DC_BUS_V) distribution block; cable for the front-face display run (SIG-7 to the detachable ESP32-S3) — internal to the appliance from the electronics shelf to the front face per [`/hardware/printed-parts/enclosure/front-panel/README.md`](/hardware/printed-parts/enclosure/front-panel/README.md) "S3 detach mechanism".

Out: every run in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) executed and continuity-tested. AC runs AC-1a through AC-6 landed, with the C14 ground pin bonded to the central chassis-ground point and onward to the four discrete chassis-ground targets (pressure vessel, compressor body, compressor shroud, faucet under-counter SS plate). Low-voltage logic runs LV-1, LV-2, LV-3 landing the [3.3 V](MCU_V) control side of the relays. DC runs DC-1 through DC-9, with DC-9 wired as the low-side switched [12 V](DC_BUS_V) condenser fan through ULN2803A #2 channel 5. Signal runs SIG-1 through SIG-4 + SIG-7 + SIG-8 + SIG-9 landed at both ends, with the I2C trunk on the electronics shelf using JST XH pigtails. SIG-7 (ESP32-S3 detachable) is a [~1 m](SIG_DISPLAY_LEN) internal run from the shelf to the front face; SIG-4 (DIGITEN flow meter) rides the umbilical up to the above-counter faucet head. A dielectric / continuity check passes on the AC side.

Not in scope: applying [120 VAC](AC_LINE_V); flashing firmware; bringing up the [12 V](DC_BUS_V) rail; any sensor probe-into-water service — see [`firmware-and-commissioning.md`](firmware-and-commissioning.md). The compressor terminal block's clip-on PTC start relay / overload module is already mated to the compressor body — a donor-side subassembly preserved during teardown ([`/hardware/harvested/ice-maker/README.md`](/hardware/harvested/ice-maker/README.md) "Powering and control"); terminal-block wiring here is the appliance-side leads landing on already-populated spade terminals.

## Inputs per appliance

Wire stock, connectors, and termination consumables are in [`/hardware/bom.md`](/hardware/bom.md) §11 (low-voltage wiring + connectors), §14 (AC stock + ground bonding), and §13 (mechanical attach for shroud + chassis bonding). Status in [`/hardware/purchases.md`](/hardware/purchases.md). The runs themselves are in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) §"Run table".

Tooling: ratcheting crimper for insulated and uninsulated terminals + ferrules + Faston disconnects + JST XH (one tool covers all four with the appropriate die per terminal family); wire strippers sized for [16/18/22 AWG](AWG_TRIPLE); small flat screwdriver for Wago 221 levers and the relay screw terminals; PEX-style sidecutters for trimming; a hot-glue gun for strain relief at intermediate tie points where the run crosses a printed-part edge; cable-tie tensioner (optional); multimeter for the continuity + dielectric checks at step 4.

## Procedure

Execution order: chassis-ground bonding, then AC, then the DC trunk, then signal, with a static dielectric / continuity check on the AC side gated between AC completion and DC energization. Within each phase, runs are executed in the run-number order from [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md).

### 1. Chassis-ground bonds (single-point ground at the electronics shelf)

Establish the single-point chassis ground first. Chassis grounding is via discrete green wires from the four exposed metal parts back to a central ground bus on the electronics shelf. Per [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Grounding strategy" all bonds are [16 AWG](AWG_AC_MAIN) green-insulated, ring terminal at the bus end, ring or fork at the target end.

Bond, from each target to the ground bus on the electronics shelf:

- **Pressure vessel** — ring terminal under the M3 SHCS that already secures one of the foam-shell top-cap screws to a heat-set insert at the cold-core ([`cold-core.md`](cold-core.md)) top face. Pick the top-cap screw position closest to the electronics shelf. Route up through the cold-core / electronics-shelf boundary in the existing wire path used by signal run SIG-1.
- **Compressor body** — ring terminal at one of the compressor's M5 mounting feet (the same foot already secures one of the compressor-shroud mounting tabs through its M5→M3 step-down adapter washer per [`/hardware/cut-parts/compressor-shroud/README.md`](/hardware/cut-parts/compressor-shroud/README.md) "Penetrations" item 2). Route outside the shroud to the compressor body.
- **Compressor shroud** — ring terminal at the Ø ~[6 mm](GND_STUD_HOLE) PEM chassis-ground stud on the shroud's side wall ([`/hardware/cut-parts/compressor-shroud/README.md`](/hardware/cut-parts/compressor-shroud/README.md) "Penetrations" item 3). This is run AC-6 in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md).
- **Faucet under-counter SS plate** — ring terminal under one of the bolts that already retains the under-counter plate ([`/hardware/cut-parts/faucet/touch-flo-under-counter-plate/`](/hardware/cut-parts/faucet/touch-flo-under-counter-plate/)) against the underside of the countertop. Run rides the umbilical alongside the Cat6 conductors back into the cabinet. Length is the umbilical length plus [200 mm](CABINET_SLACK) of cabinet-side slack.

At the electronics-shelf end, all four bonds terminate on a single ring-terminal stack at the ground bus. The bus is bonded to the C14 inlet's earth pin via run AC-1b's green conductor (G Wago → ground bus) and run AC-1a's green conductor (C14 → GFCI LINE earth; earth is a pass-through on the GFCI), both executed in step 2.

Continuity check after this step: ohms-low between every bonded metal surface and the bus.

### 2. AC mains (C14 → distribution → relay #1 → compressor + PSU)

Execute the AC runs in the order they appear in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "AC mains (120 V)": AC-1a, AC-1b, AC-2, AC-3, AC-4, AC-5, AC-6. AC-1b lands fully on the shelf during [`electronics-shelf.md`](electronics-shelf.md) and needs no work here. AC-6 is the shroud chassis-ground done in step 1; it is the third conductor of the 3-conductor bundle through the shroud's Heyco SB-500-6 grommet. Build the bundle whole here; the green conductor was landed at the bus end in step 1.

Shroud pass-through (AC-4 + AC-5 + AC-6): pre-build a single [18 AWG](AWG_AC_BRANCH) SJOOW 3-conductor jacketed lead, [~400 mm](SHROUD_LEAD_LEN) long, with the H_switched (from Teyleten relay #1 NO contact), N (from AC distribution block), and G (from electronics-shelf ground bus) conductors. Pull the bundle through the Heyco snap bushing in the shroud side wall as one cable — [18 AWG](SHROUD_SJOOW_AWG) SJOOW fits the snap bushing's [5.6](BUSHING_LOW)–[6.4 mm](BUSHING_HIGH) cable-OD range per [`/hardware/cut-parts/compressor-shroud/README.md`](/hardware/cut-parts/compressor-shroud/README.md) "Penetrations" item 1. Inside the shroud, fan the three conductors out the last [~50 mm](SHROUD_FAN_OUT): H_switched and N each take a female disconnect onto the appropriate compressor terminal-block spade (the donor's terminal block + clip-on PTC start relay/overload module is already populated from harvest, see [`/hardware/harvested/ice-maker/README.md`](/hardware/harvested/ice-maker/README.md) "Powering and control"); G takes a ring terminal at the compressor body's mounting-foot bond from step 1.

At the shelf end of the bundle: H_switched lands on the Teyleten relay #1 NO terminal; N lands at the AC distribution block N pole; G lands on the ground bus. AC distribution-block landings use ferrules into the Wago 221 lever-nut block. Relay screw-terminal landings use fork terminals.

AC-1a (C14 inlet → GFCI **LINE** terminals) is [~150 mm](AC1A_LEN), ferrules at the C14 end and backstab/screw at the GFCI. AC-1b (GFCI **LOAD** terminals → distribution block) is [~150 mm](AC1B_LEN), backstab/screw at the GFCI end and ferrules at the Wago block — landed in [`electronics-shelf.md`](electronics-shelf.md) at the bench, not here. AC-2 (distribution block → PSU primary) is [~100 mm](AC2_LEN), ferrule at the block, ring or fork at the PSU; the PSU's chassis ground is bonded by AC-2's green conductor onto the PSU's earth lug. AC-3 is the hot-pickup leg from the distribution block into relay #1's contact common.

Color discipline: [16 AWG](AWG_AC_MAIN) silicone, black for hot, white for neutral, green for ground.

### 3. Static dielectric / continuity check on the AC side

After step 2 and before any DC conductor lands, cold-check the AC wiring with the C14 inlet **disconnected from line**, multimeter only. The Legrand GFCI's internal relay is open in the unpowered / un-RESET state, so H and N continuity is verified separately on each side of the device: **AC-1a** (C14 inlet → GFCI LINE terminals) and **AC-1b** (GFCI LOAD terminals → AC distribution block → downstream loads). End-to-end through-GFCI continuity on H and N is exercised at first power-on per [`firmware-and-commissioning.md`](firmware-and-commissioning.md) step 2, when the GFCI's self-test closes the relay. Earth is a pass-through on the GFCI (not switched, not sensed by the CT), so the earth checks below run end-to-end as written.

- **Continuity (ohms-low) — earth, end-to-end:** C14 earth pin to every metal-part chassis-ground target from step 1.
- **Continuity (ohms-low) — H/N, AC-1a side (C14 → GFCI LINE):** C14 hot pin to the GFCI's LINE H terminal. C14 neutral pin to the GFCI's LINE N terminal.
- **Continuity (ohms-low) — H/N, AC-1b side and downstream of the GFCI:** GFCI LOAD H terminal to AC distribution block H pole. GFCI LOAD N terminal to AC distribution block N pole. AC distribution block H pole to Teyleten relay #1 common. With relay #1 manually held closed (jumper across the input opto), distribution-block H to compressor terminal-block hot spade.
- **Open (ohms-high) — H to N downstream of the GFCI:** GFCI LOAD H to GFCI LOAD N, both with relay #1 open and with relay #1 closed (with the compressor's motor windings in circuit, this last reads the winding resistance; confirm ~[10](WINDING_R_LOW)–[30 Ω](WINDING_R_HIGH) for a [100 W-class](COMP_CLASS_W) hermetic, matching the donor compressor's nameplate). The same check from C14 hot to C14 neutral reads open regardless of relay #1's state — that is the GFCI's open relay, an expected pre-power-on condition, not a wiring fault.
- **Open (ohms-high) — leakage:** Every AC current-carrying conductor to every chassis-ground target, checked on both sides of the GFCI. Upstream of the device: C14 hot pin to chassis-ground, C14 neutral pin to chassis-ground. Downstream: GFCI LOAD H, GFCI LOAD N, relay #1 NO terminal, compressor terminal-block hot spade — each to chassis-ground. No leakage path on either side.

If any check fails, find and fix it before step 4.

### 4. [12 V](DC_BUS_V) trunk + branch DC (DC-1 through DC-9)

Execute the DC runs in the order they appear in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "12 V distribution": DC-1 (PSU output → [12 V](DC_BUS_V) distribution block on the shelf) first, then DC-2 through DC-9 from the block outward. The [12 V](DC_BUS_V) block has its own lever-nut stack distinct from the AC stack.

DC-3 (relay #2 → SeaFlo diaphragm pump) and DC-5 (L298N → Kamoer pumps) both leave the shelf and route through the cabinet. DC-5's cabinet-side run lands at the pump-cartridge magnetic pogo interface ([`/hardware/bom.md`](/hardware/bom.md) §8). Terminate on the manifold-side pogo pad.

DC-7 (ULN2803A outputs → 12 solenoid coils on the manifold) ships as a single ~24-conductor bundle from the electronics shelf to the manifold. The bundle ships as 12× Keszoox B0F8HMQRRN pre-crimped [50 cm](KESZOOX_LEN) pigtails (one per valve) and fans out to a female disconnect per valve at the manifold.

DC-9 (condenser fan): [12 V](DC_BUS_V) + side ties to the [12 V](DC_BUS_V) distribution block, ULN2803A #2 channel 5 sinks the − return when MCP23017 0x21 PA4 commands it, flyback path through the ULN2803A's integrated diode to COM (already at [12 V](DC_BUS_V) via DC-6). See [`/hardware/wiring/power.mmd`](/hardware/wiring/power.mmd) and [`/hardware/wiring/valve-control.mmd`](/hardware/wiring/valve-control.mmd). The fan disconnects use female Fastons.

DC-6 ([12 V](DC_BUS_V) trunk → both ULN2803A COM pins) lands at each ULN module's COM pin header. Both ULNs share the same trunk feed via a JST XH pigtail tee on the shelf.

DC-8 ([12 V](DC_BUS_V) → [5 V](LOGIC_V) regulator input) feeds the regulator stack; the [3.3 V](MCU_V) regulator chains from the [5 V](LOGIC_V) output per [`/hardware/wiring/power.mmd`](/hardware/wiring/power.mmd).

### 5. Low-voltage logic + signal (LV-1 through LV-3, SIG-1 through SIG-9)

Execute the LV and SIG runs from [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Low-voltage logic" and "Sensors and signal" tables.

On-shelf hops, JST XH [2.54 mm](JST_PITCH) via the pre-crimped CQRobot bonded ribbons (B0F6C7X5CR):

- **LV-1, LV-2** — ESP32 GPIO 14 / GPIO 4 + GND, Dupont female on the ESP32 side, JST XH on the relay-module side (the Teyleten module's IN pin is a pin header). [~150 mm](LV_SHORT_LEN) each.
- **LV-3** — [5 V](LOGIC_V) regulator output → both Teyleten relay modules' VCC pins via a tee. Single 4-pin XH housing on the regulator side, fans out to two 2-pin connectors at the relay modules.
- **SIG-8** — ESP32 GPIO 21 / 22 (I2C) + [3.3 V](MCU_V) + GND to DS3231 RTC + both MCP23017s on a shared bus. A 4-pin XH housing on the ESP32, daisy-chained to the RTC's 6-pin XH header (VCC / GND / SDA / SCL / SQW / 32K, only the first four used) and then onward to each MCP23017's 4-pin I2C header.

Cabinet-side runs leaving the shelf:

- **SIG-1** — DS18B20 1-wire bus, [22 AWG](AWG_DC_BRANCH), [~600 mm](SIG_COLD_CORE_LEN) to the back of the cold core. Two DS18B20 probes are bussed in parallel: tank-wall probe + evap-suction probe ([`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd) "Refrigeration"). [4.7 kΩ](PULLUP_R) pull-up between data and [3.3 V](MCU_V) at the ESP32 end. Probes land at the cold core's exit per [`cold-core.md`](cold-core.md).
- **SIG-2, SIG-3** — carbonator reed switches (low + high), INPUT_PULLUP at the ESP32. Two [24 AWG](AWG_SIGNAL) twisted pairs (switch + GND) routed alongside SIG-1 in the same cold-core-exit cable channel.
- **SIG-4** — DIGITEN flow meter, [24 AWG](AWG_SIGNAL), [~1 m](SIG_UMBILICAL_LEN). Pulse interrupt at the ESP32. Flow meter sits in the post-faucet line on the under-counter side; cable routes through the cabinet up the umbilical.
- **SIG-7** — UART trunk to the front-face ESP32-S3 rotary display. Runs from the ESP32 (GPIO 15 TX / 34 RX + [5 V](LOGIC_V) + GND) to the detachable S3 on the front face. Display-end retention per [`/hardware/printed-parts/enclosure/front-panel/README.md`](/hardware/printed-parts/enclosure/front-panel/README.md) "S3 detach mechanism". The run is internal to the appliance; shelf end terminates via a JST XH pigtail into the ESP32, display end terminates at the display's pin header.
- **SIG-9** — backflow vent moisture sensor, [24 AWG](AWG_SIGNAL), [~600 mm](SIG_COLD_CORE_LEN) to the drip pan inside the cabinet. ESP32 pin assignment is not yet committed in [`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd). Lay the wire and leave the shelf end un-landed, or land it on a labeled spare GPIO.

Continuity-test each signal run end-to-end before zip-tying down.

### 6. Bundle, route, and strain-relieve

Bundle by zone:

- **Shelf-to-cold-core bundle** — SIG-1 (DS18B20 bus), SIG-2 + SIG-3 (carbonator reeds), the pressure-vessel chassis-ground bond, and any of the reservoir-reed harnesses ([`/hardware/printed-parts/cold-core/reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md)) into a single spiral-wrapped bundle exiting the back of the shelf and routing along the back wall of the enclosure to the cold core's penetrations.
- **Shelf-to-manifold bundle** — DC-7 (24 conductors to the solenoid manifold), DC-3 (diaphragm pump), DC-5 (peristaltic pump pogo pad), and DC-4 (L298N feed). Spiral-wrap and zip-tie; fan-out happens at the manifold.
- **Shelf-to-shroud bundle** — the [18 AWG](SHROUD_SJOOW_AWG) SJOOW jacketed lead from step 2 is its own bundle; zip-tie tie-down points only.
- **Shelf-to-front-face bundle** — SIG-7 (ESP32-S3 detach cord) routed forward through the enclosure interior to the front face. Display-end retention per [`/hardware/printed-parts/enclosure/front-panel/README.md`](/hardware/printed-parts/enclosure/front-panel/README.md) "S3 detach mechanism".
- **Shelf-to-umbilical bundle** — SIG-4 (flow meter) and the under-counter SS plate chassis-ground bond. Both ride the umbilical together up to the under-counter zone; spiral-wrap on the shelf side, separator at the umbilical's bulkhead.
- **Shelf-to-condenser-fan bundle** — DC-9 alone; [~400 mm](DC9_LEN) run along the side wall. Female Fastons at the fan.

Strain relief at every cable transition: shelf exit edge, cold-core penetration, manifold entry, shroud grommet (the Heyco SB-500-6 itself is the strain relief on that one), umbilical bulkhead. Use existing printed-part features. Cable-tie anchors are placed below the cable.

## Output condition

A wired but unenergized chassis:

- All four chassis-ground bonds (pressure vessel, compressor body, compressor shroud, faucet under-counter SS plate) land at the single ground bus on the electronics shelf; the bus is bonded to the C14 inlet's earth pin
- All AC runs (AC-1a through AC-6) executed and continuity-tested; the AC dielectric / continuity check (step 3) passes
- All DC runs (DC-1 through DC-9) executed; the [12 V](DC_BUS_V) trunk is contiguous from PSU output to every load; DC-9 wired as low-side ULN2803A switching for the condenser fan
- All LV runs (LV-1 through LV-3) executed; the [3.3 V](MCU_V) control side of both Teyleten relays is wired to the ESP32 GPIOs and powered from the [5 V](LOGIC_V) regulator
- All SIG runs (SIG-1 through SIG-9) landed at both ends, except SIG-9 if its ESP32 pin is still un-assigned
- SIG-7 (ESP32-S3 detach cord) seated at the shelf and landed at the front face display
- Wire bundles are spiral-wrapped or zip-tied by zone, with strain relief at every transition
- The chassis is safe to apply [120 VAC](AC_LINE_V) but no power has been applied

The chassis is the input to [`firmware-and-commissioning.md`](firmware-and-commissioning.md).

## Open items

1. **Switched-hot vs unswitched-hot color convention.** [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) does not specify color-coding for switched-hot (AC-4) vs unswitched-hot (AC-3). Pick a convention and roll it into the AC schedule.
2. **Umbilical cable selection.** The umbilical carries SIG-4 (flow meter, 3 conductors) plus the under-counter SS plate ground bond. Pick the cable family.
3. **Strain relief for bundles crossing the cold-core boundary.** The shelf-to-cold-core bundle enters the foam-shell at a printed pass-through. Pick a strain-relief method and roll it into the foam-shell or the electronics-shelf printed parts.
4. **SIG-9 pin assignment.** Per [`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd) the backflow-vent moisture sensor's ESP32 GPIO is not yet committed. Land the assignment before unit 1 wiring.
5. **AC distribution-block hardware.** Open per [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "What's not yet decided": Wago 221 vs. screw terminal block vs. PCB-mounted block. Same question applies to the [12 V](DC_BUS_V) distribution block. This procedure assumes Wago 221; pick the production form before unit 1.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_wiring_sync.py`
