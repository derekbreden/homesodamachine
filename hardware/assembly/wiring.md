# Wiring

The production procedure for executing every electrical run in the appliance — chassis ground bonds, AC mains, the [12 V](DC_BUS_V) trunk, and signal lines — once the enclosure is plumbed and the electronics shelf is installed. The schedule of runs is [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md); this doc is the build-order procedure for executing that schedule, with AC, DC, and signal runs interleaved by physical zone.

A single zip-tied bundle exiting the electronics shelf carries [16 AWG](AWG_AC_MAIN) mains, [18 AWG](AWG_AC_BRANCH_U) [12 V](DC_BUS_V), and [22 AWG](AWG_DC_BRANCH) signal in close proximity. Topology lives in [`/hardware/wiring/power.mmd`](/hardware/wiring/power.mmd), [`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd), and [`/hardware/wiring/valve-control.mmd`](/hardware/wiring/valve-control.mmd).

The field harnesses are **not** wired in place conductor-by-conductor — they are **pre-fabricated as cable assemblies** on the bench (cut-to-length all-black silicone, ferruled/crimped, black-braided-sleeved, continuity-tested), then landed here. The fabrication procedure is [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md); a failed harness is swapped as a whole assembly, never repaired conductor-by-conductor. Wire is all-black throughout **except the AC mains** (black hot / white neutral / green ground — a safety convention, not a service aid).

## Scope

In: a chassis that exits [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) — cold core dropped into the enclosure, valve manifold mounted, all water + CO2 + flavor lines plumbed but unwired; electronics shelf installed per [`electronics-shelf.md`](/hardware/assembly/electronics-shelf.md) + [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md), populated with C14 inlet, AC distribution block, Mean Well IRM-90-12ST PSU, both Teyleten relays, ESP32-DevKitC-32E, both MCP23017s, both ULN2803A modules, L298N board, the on-board [5 V](LOGIC_V) + [3.3 V](MCU_V) logic rails, and ground bus — all mounted but unpowered, no field-side wires landed; compressor + condenser fan installed in their middle-bottom and side-wall positions, compressor shroud installed with its AC gland open and its bond point unbonded. Plus the bagged faucet-and-umbilical sub-assembly (output of [`faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md)) brought to the wiring bench with its rear-panel-end signal-cable conductors broken out and accessible; only the rear-panel-end signal cable gets terminated at the electronics shelf during this procedure.

Wire stock and small parts: [16 AWG](AWG_AC_MAIN) silicone hookup wire for AC + ground (green for ground, plus the appliance-wire colors used in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) §AC mains); [18 AWG](AWG_AC_BRANCH_U) silicone for the 18 AWG runs in the AC schedule; [18 AWG](SHROUD_SJOOW_AWG) SJOOW 3-conductor jacketed cable for the shroud pass-through; [16 AWG](AWG_AC_MAIN) hookup for the [12 V](DC_BUS_V) trunk, [22 AWG](AWG_DC_BRANCH) for branch DC and signal; JST XH [2.54 mm](JST_PITCH) housings + pre-crimped pigtails (CQRobot B0F6C7X5CR + Keszoox B0F8HMQRRN, per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11); ferrules sized for [16/18/22 AWG](AWG_TRIPLE); ring terminals for the ground bus + shroud stud; female-disconnect (Faston) terminals for the compressor terminal block, diaphragm pump, and condenser fan; black PET braided sleeve + zip ties for bundling; Wago 221 lever-nut blocks for the AC distribution block and the [12 V](DC_BUS_V) distribution block; cable for the front-face display run (SIG-7, RS485 link + power to the fixed ESP32-S3-Touch-LCD-4.3B) — internal to the appliance from the electronics shelf to the front face per [`/hardware/printed-parts/enclosure/front-panel/README.md`](/hardware/printed-parts/enclosure/front-panel/README.md).

Out: every run in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) executed and continuity-tested. AC runs AC-1 through AC-6 landed, with the C14 ground pin bonded to the central chassis-ground point and onward to the four discrete chassis-ground targets (pressure vessel, compressor body, compressor shroud, faucet under-counter SS plate). Low-voltage logic runs LV-1, LV-2, LV-3 landing the [3.3 V](MCU_V) control side of the relays. DC runs DC-1 through DC-9, with DC-9 wired as the low-side switched [12 V](DC_BUS_V) condenser fan through ULN2803A #2 channel 5. Signal runs SIG-1 through SIG-4 + SIG-6 + SIG-7 + SIG-8 + SIG-9 landed at both ends, with the I2C trunk on the electronics shelf using JST XH pigtails. SIG-7 (4.3B config display) is a [~1 m](SIG_DISPLAY_LEN) internal run from the shelf to the front face; SIG-6 (1.47" faucet display, direct TTL UART) rides the umbilical up to the above-counter faucet head, while SIG-4 (flow meter) is a short internal run in the electronics-shelf zone. A dielectric / continuity check passes on the AC side.

Not in scope: applying [120 VAC](AC_LINE_V); flashing firmware; bringing up the [12 V](DC_BUS_V) rail; any sensor probe-into-water service — see [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md). The compressor terminal block's clip-on PTC start relay / overload module is already mated to the compressor body — a donor-side subassembly preserved during teardown ([`/hardware/reference/ice-maker/README.md`](/hardware/reference/ice-maker/README.md) "Powering and control"); terminal-block wiring here is the appliance-side leads landing on already-populated spade terminals.

## Inputs per appliance

Wire stock, connectors, and termination consumables are in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 (low-voltage wiring + connectors), §14 (AC stock + ground bonding), and §13 (mechanical attach for shroud + chassis bonding). Status in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md). The runs themselves are in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) §"Run table".

Tooling: ratcheting crimper for insulated and uninsulated terminals + ferrules + Faston disconnects + JST XH (one tool covers all four with the appropriate die per terminal family); wire strippers sized for [16/18/22 AWG](AWG_TRIPLE); small flat screwdriver for Wago 221 levers and the relay screw terminals; PEX-style sidecutters for trimming; a hot-glue gun for strain relief at intermediate tie points where the run crosses a printed-part edge; cable-tie tensioner (optional); multimeter for the continuity + dielectric checks at step 4.

## Procedure

Execution order: chassis-ground bonding, then AC, then the DC trunk, then signal, with a static dielectric / continuity check on the AC side gated between AC completion and DC energization. Within each phase, runs are executed in the run-number order from [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md).

### 1. Chassis-ground bonds (single-point ground at the electronics shelf)

Establish the single-point chassis ground first. Chassis grounding is via discrete green wires from the four exposed metal parts back to a central ground bus on the electronics shelf. Per [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Grounding strategy" all bonds are [16 AWG](AWG_AC_MAIN) green-insulated, ring terminal at the bus end, ring or fork at the target end.

Bond, from each target to the ground bus on the electronics shelf:

- **Pressure vessel** — ring terminal under the M3 SHCS that already secures one of the foam-shell top-cap screws to a heat-set insert at the cold-core ([`cold-core.md`](/hardware/assembly/cold-core.md)) top face. Pick the top-cap screw position closest to the electronics shelf. Route up through the cold-core / electronics-shelf boundary in the existing wire path used by signal run SIG-1.
- **Compressor body** — ring terminal at one of the compressor's M5 mounting feet. Route outside the shroud to the compressor body.
- **Compressor shroud** — ring terminal at the Ø ~[6 mm](GND_STUD_HOLE) earth-bond hole on the back face, beside the AC pass-through ([`/hardware/cut-parts/compressor-shroud/README.md`](/hardware/cut-parts/compressor-shroud/README.md) "Grounding & mounting"). This is run AC-6 in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md).
- **Faucet under-counter SS plate** — ring terminal under one of the bolts that already retains the under-counter plate ([`/hardware/cut-parts/faucet/touch-flo-under-counter-plate/`](/hardware/cut-parts/faucet/touch-flo-under-counter-plate/)) against the underside of the countertop. Run rides the umbilical alongside the signal cable back into the cabinet. Length is the umbilical length plus [200 mm](CABINET_SLACK) of cabinet-side slack.

At the electronics-shelf end, all four bonds terminate on a single ring-terminal stack at the ground bus. The bus is bonded to the C14 inlet's earth pin via run AC-1's green conductor (C14 earth → AC distribution block → ground bus), executed in step 2.

Continuity check after this step: ohms-low between every bonded metal surface and the bus.

### 2. AC mains (C14 → distribution → relay #1 → compressor + PSU)

Execute the AC runs in the order they appear in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "AC mains (120 V)": AC-1, AC-2, AC-3, AC-4, AC-5, AC-6. AC-1 lands the rear C14 inlet directly on the AC distribution block; there is no device in series — ground-fault protection is deferred, see [/pie-in-the-sky/gfci.md](/pie-in-the-sky/gfci.md). AC-6 is the shroud chassis-ground done in step 1; it is the third conductor of the 3-conductor bundle through the shroud's cable gland. Build the bundle whole here; the green conductor was landed at the bus end in step 1.

Shroud pass-through (AC-4 + AC-5 + AC-6): pre-build a single [18 AWG](AWG_AC_BRANCH_U) SJOOW 3-conductor jacketed lead, [~400 mm](SHROUD_LEAD_LEN) long, with the H_switched (from Teyleten relay #1 NO contact), N (from AC distribution block), and G (from electronics-shelf ground bus) conductors. Fit the SS cable gland into the shroud side wall, pass the [18 AWG](SHROUD_SJOOW_AWG) SJOOW lead through, and tighten the gland nut to clamp the jacket — the gland's [6](GLAND_LOW)–[12 mm](GLAND_HIGH) clamping range takes it, per [`/hardware/cut-parts/compressor-shroud/README.md`](/hardware/cut-parts/compressor-shroud/README.md) "Penetrations" item 1. Inside the shroud, fan the three conductors out the last [~50 mm](SHROUD_FAN_OUT): H_switched and N each take a female disconnect onto the appropriate compressor terminal-block spade (the donor's terminal block + clip-on PTC start relay/overload module is already populated from harvest, see [`/hardware/reference/ice-maker/README.md`](/hardware/reference/ice-maker/README.md) "Powering and control"); G takes a ring terminal at the compressor body's mounting-foot bond from step 1.

At the shelf end of the bundle: H_switched lands on the Teyleten relay #1 NO terminal; N lands at the AC distribution block N pole; G lands on the ground bus. AC distribution-block landings use ferrules into the Wago 221 lever-nut block. Relay screw-terminal landings use fork terminals.

AC-1 (C14 inlet → AC distribution block) is [~150 mm](AC1_LEN), ferrules at the C14 end and into the Wago block at the distribution end; H, N, and G land directly on the block. AC-2 (distribution block → PSU primary) is [~100 mm](AC2_LEN), ferrule at the block, ring or fork at the PSU; the PSU's chassis ground is bonded by AC-2's green conductor onto the PSU's earth lug. AC-3 is the hot-pickup leg from the distribution block into relay #1's contact common.

Color discipline (AC only): [16 AWG](AWG_AC_MAIN) silicone, black for hot, white for neutral, green for ground. DC and signal wire is all-black (cut-to-length, per [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md)) — color is reserved for the mains as a safety convention.

### 3. Static dielectric / continuity check on the AC side

After step 2 and before any DC conductor lands, cold-check the AC wiring with the C14 inlet **disconnected from line**, multimeter only. The AC path runs C14 inlet → AC distribution block directly (AC-1), so H and N continuity from the inlet to the distribution block reads end-to-end. Ground-fault protection is deferred — see [/pie-in-the-sky/gfci.md](/pie-in-the-sky/gfci.md).

- **Continuity (ohms-low) — earth, end-to-end:** C14 earth pin to every metal-part chassis-ground target from step 1.
- **Continuity (ohms-low) — H/N, C14 → distribution block:** C14 hot pin to AC distribution block H pole. C14 neutral pin to AC distribution block N pole.
- **Continuity (ohms-low) — H/N, distribution block → downstream loads:** AC distribution block H pole to Teyleten relay #1 common. With relay #1 manually held closed (jumper across the input opto), distribution-block H to compressor terminal-block hot spade.
- **Open (ohms-high) — H to N downstream of the distribution block:** distribution block H to distribution block N, both with relay #1 open and with relay #1 closed (with the compressor's motor windings in circuit, this last reads the winding resistance; confirm ~[10](WINDING_R_LOW)–[30 Ω](WINDING_R_HIGH) for a [100 W](COMP_CLASS_W) hermetic, matching the donor compressor's nameplate). With relay #1 open, C14 hot to C14 neutral reads open.
- **Open (ohms-high) — leakage:** Every AC current-carrying conductor to every chassis-ground target. C14 hot pin to chassis-ground, C14 neutral pin to chassis-ground, AC distribution block H pole, AC distribution block N pole, relay #1 NO terminal, compressor terminal-block hot spade — each to chassis-ground. No leakage path.

If any check fails, find and fix it before step 4.

### 4. [12 V](DC_BUS_V) trunk + branch DC (DC-1 through DC-9)

Execute the DC runs in the order they appear in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "12 V distribution": DC-1 (PSU output → [12 V](DC_BUS_V) distribution block on the shelf) first, then DC-2 through DC-9 from the block outward. The [12 V](DC_BUS_V) block has its own lever-nut stack distinct from the AC stack.

DC-3 (relay #2 → SeaFlo diaphragm pump) and DC-5 (L298N → Kamoer pumps) both leave the shelf and route through the cabinet. DC-5's cabinet-side run lands on the pump-motor spade tabs via crimped female faston receptacles ([`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11). Terminate on the pump-motor tabs.

DC-7 (ULN2803A outputs → solenoid manifold) is a **black jacketed trunk** from the electronics shelf to the manifold — the KWANGIL 22 AWG UL2464 cable populated to the conductors each manifold needs (MANIFOLD A = 8 OUT + COM = 9; MANIFOLD B = 4 OUT + FAN + COM = 6), cut-to-length per [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md). It breaks out at the manifold: each OUT lands on a female disconnect at its valve; the COM lands in the manifold's 221-420 lever nut, which fans the 12 V to every valve's other tab.

DC-9 (condenser fan): [12 V](DC_BUS_V) + side ties to the [12 V](DC_BUS_V) distribution block, ULN2803A #2 channel 5 sinks the − return when MCP23017 0x21 PA4 commands it, flyback path through the ULN2803A's integrated diode to COM (already at [12 V](DC_BUS_V) via DC-6). See [`/hardware/wiring/power.mmd`](/hardware/wiring/power.mmd) and [`/hardware/wiring/valve-control.mmd`](/hardware/wiring/valve-control.mmd). The fan disconnects use female Fastons.

DC-6 ([12 V](DC_BUS_V) trunk → both ULN2803A COM pins) lands at each ULN module's COM pin header. Both ULNs share the same trunk feed via a JST XH pigtail tee on the shelf.

DC-8 (the L298N's onboard [5 V](LOGIC_V) output → ESP32 5 V/VIN) carries the logic-rail 5 V to the MCUs; the ESP32's onboard AMS1117 makes [3.3 V](MCU_V) on its 3V3 pin per [`/hardware/wiring/power.mmd`](/hardware/wiring/power.mmd).

### 5. Low-voltage logic + signal (LV-1 through LV-3, SIG-1 through SIG-9)

Execute the LV and SIG runs from [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Low-voltage logic" and "Sensors and signal" tables.

On-shelf logic hops — JST XH [2.54 mm](JST_PITCH) where a module presents pin headers (CQRobot bonded ribbons B0F6C7X5CR feed the housings), screw terminals where it presents terminals:

- **LV-1, LV-2** — ESP32 GPIO 17 / GPIO 16 + GND to the Teyleten relay IN terminals. **Screw terminals both ends, no connector**: the ESP32 end lands on the DIN-breakout screw terminals, the relay end on the module's 3-position input screw terminal (VCC / GND / IN). [~150 mm](LV_SHORT_LEN) each.
- **LV-3** — [5 V](LOGIC_V) from the L298N Board A onboard regulator (7805/78M05) → both Teyleten relay modules' VCC screw terminals via a tee. **Screw terminals**, no JST.
- **SIG-8** — ESP32 GPIO 21 / 22 (I2C) + [3.3 V](MCU_V) + GND to the DS3231 RTC + both MCP23017s on a shared bus. The ESP32 end lands on the DIN-breakout **screw terminals**; the DS3231 takes a **4-pin XH** (VCC / GND / SDA / SCL — the RTC's other pins unused); each MCP23017 joins on its native **PH2.0** connector, not XH.

Cabinet-side runs leaving the shelf:

- **SIG-1** — DS18B20 1-wire bus, [22 AWG](AWG_DC_BRANCH), [~600 mm](SIG_COLD_CORE_LEN) to the back of the cold core. Two DS18B20 probes are bussed in parallel: tank-wall probe + evap-suction probe ([`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd) "Refrigeration"). [4.7 kΩ](PULLUP_R) pull-up between data and [3.3 V](MCU_V) at the ESP32 end. Probes land at the cold core's exit per [`cold-core.md`](/hardware/assembly/cold-core.md).
- **SIG-2, SIG-3** — carbonator reed switches (low + high), read through the 0x21 MCP23017 expander on its internal pull-ups (INPUT_PULLUP, magnet pulls LOW). Two [24 AWG](AWG_SIGNAL) twisted pairs (switch + GND) routed alongside SIG-1 in the same cold-core-exit cable channel.
- **SIG-4** — DIGITEN flow meter, [24 AWG](AWG_SIGNAL), short internal run. Pulse interrupt at the ESP32. The flow meter sits in Zone B on the carbonated-water line where it exits the cold core near the electronics shelf — flow detection is internal, so SIG-4 stays in the enclosure and never enters the umbilical.
- **SIG-6** — direct TTL UART to the gooseneck-mounted ESP32-S3-Touch-LCD-1.47 faucet display, on the BNTECHGO 28 AWG 4-conductor ribbon (TX / RX / [5 V](LOGIC_V) / GND). From the ESP32 (GPIO 33 TX / 35 RX), [~1 m](SIG_UMBILICAL_LEN) up the umbilical to the display, which breaks out TTL UART (no transceiver).
- **SIG-7** — RS485 config-display link to the front-face ESP32-S3-Touch-LCD-4.3B. Runs from the ESP32 (GPIO 32 TX / 34 RX) through the TTL-to-RS485 transceiver, then the RS485 A/B pair + [12 V](DC_BUS_V) + GND to the fixed 4.3B on the front face. The run is internal to the appliance; shelf end terminates via a JST XH pigtail into the ESP32, display end lands on the 4.3B's RS485 + power screw terminals.
- **SIG-9** — backflow vent moisture sensor, [24 AWG](AWG_SIGNAL), [~600 mm](SIG_COLD_CORE_LEN) to the drip pan inside the cabinet. the ESP32 end lands on GPIO 13 per [`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd).

Continuity-test each signal run end-to-end before zip-tying down.

### 6. Bundle, route, and strain-relieve

Bundle by zone:

- **Shelf-to-cold-core bundle** — SIG-1 (DS18B20 bus), SIG-2 + SIG-3 (carbonator reeds), the pressure-vessel chassis-ground bond, and any of the reservoir-reed harnesses ([`/hardware/printed-parts/cold-core/reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md)) into a single braided-sleeved bundle exiting the back of the shelf and routing along the back wall of the enclosure to the cold core's penetrations.
- **Shelf-to-manifold bundle** — DC-7 (24 conductors to the solenoid manifold), DC-3 (diaphragm pump), DC-5 (peristaltic pump spade leads), and DC-4 (L298N feed). Braided-sleeve and zip-tie; fan-out happens at the manifold.
- **Shelf-to-shroud bundle** — the [18 AWG](SHROUD_SJOOW_AWG) SJOOW jacketed lead from step 2 is its own bundle; zip-tie tie-down points only.
- **Shelf-to-front-face bundle** — SIG-7 (4.3B config-display RS485 + power run) routed forward through the enclosure interior to the front face. Display end lands on the 4.3B's screw terminals.
- **Shelf-to-umbilical bundle** — SIG-6 (faucet-display TTL UART on the BNTECHGO ribbon) and the under-counter SS plate chassis-ground bond. Both ride the umbilical together up to the under-counter zone; braided sleeve on the shelf side, separator at the umbilical's bulkhead.
- **Shelf-to-condenser-fan bundle** — DC-9 alone; [~400 mm](DC9_LEN) run along the side wall. Female Fastons at the fan.

Strain relief at every cable transition: shelf exit edge, cold-core penetration, manifold entry, shroud gland (the cable gland itself is the strain relief on that one), umbilical bulkhead. Use existing printed-part features. Cable-tie anchors are placed below the cable.

## Output condition

A wired but unenergized chassis:

- All four chassis-ground bonds (pressure vessel, compressor body, compressor shroud, faucet under-counter SS plate) land at the single ground bus on the electronics shelf; the bus is bonded to the C14 inlet's earth pin
- All AC runs (AC-1 through AC-6) executed and continuity-tested; the AC dielectric / continuity check (step 3) passes
- All DC runs (DC-1 through DC-9) executed; the [12 V](DC_BUS_V) trunk is contiguous from PSU output to every load; DC-9 wired as low-side ULN2803A switching for the condenser fan
- All LV runs (LV-1 through LV-3) executed; the [3.3 V](MCU_V) control side of both Teyleten relays is wired to the ESP32 GPIOs and powered from the [5 V](LOGIC_V) logic rail (L298N onboard)
- All SIG runs (SIG-1 through SIG-9) landed at both ends, except SIG-9 if its ESP32 pin is still un-assigned
- SIG-7 (4.3B config-display run) seated at the shelf and landed at the front-face display
- SIG-6 (1.47" faucet-display UART run) seated at the shelf and landed up the umbilical at the faucet head
- Wire bundles are black-braided-sleeved or zip-tied by zone, with strain relief at every transition
- The chassis is safe to apply [120 VAC](AC_LINE_V) but no power has been applied

The chassis is the input to [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md).

## Open items

1. **Switched-hot vs unswitched-hot color convention.** [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) does not specify color-coding for switched-hot (AC-4) vs unswitched-hot (AC-3). Pick a convention and roll it into the AC schedule.
2. **Strain relief for bundles crossing the cold-core boundary.** The shelf-to-cold-core bundle enters the foam-shell at a printed pass-through. Pick a strain-relief method and roll it into the foam-shell or the electronics-shelf printed parts.
3. **SIG-9 pin assignment.** Per [`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd) the backflow-vent moisture sensor's ESP32 GPIO is not yet committed. Land the assignment before unit 1 wiring.
4. **AC distribution-block hardware.** Open per [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "What's not yet decided": Wago 221 vs. screw terminal block vs. PCB-mounted block. Same question applies to the [12 V](DC_BUS_V) distribution block. This procedure assumes Wago 221; pick the production form before unit 1.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_wiring_sync.py`
